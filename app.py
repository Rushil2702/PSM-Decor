from pathlib import Path
import re

from flask import Flask, abort, render_template, send_from_directory

app = Flask(__name__)

PROJECT_IMAGES_DIR = Path(app.root_path) / "Images"
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
TITLE_EXTENSION_ORDER = {".webp": 0, ".jpg": 1, ".jpeg": 2, ".png": 3}
FEATURED_PROJECT_FOLDERS = [
    "Shree palace",
    "Quistaniya",
    "Shahi Family",
    "CountrySide",
]


def slugify_folder_name(folder_name):
    slug = re.sub(r"[^a-z0-9]+", "-", folder_name.casefold()).strip("-")
    return slug or "project"


def discover_projects():
    """Use each Images/<project folder> as the portfolio source of truth."""
    if not PROJECT_IMAGES_DIR.is_dir():
        return []

    discovered = []
    used_slugs = set()
    folders = sorted(
        (path for path in PROJECT_IMAGES_DIR.iterdir() if path.is_dir()),
        key=lambda path: path.name.casefold(),
    )

    for project_id, folder in enumerate(folders, start=1):
        slug_base = slugify_folder_name(folder.name)
        slug = slug_base
        suffix = 2
        while slug in used_slugs:
            slug = f"{slug_base}-{suffix}"
            suffix += 1
        used_slugs.add(slug)

        image_files = sorted(
            (
                path
                for path in folder.iterdir()
                if path.is_file() and path.suffix.casefold() in IMAGE_EXTENSIONS
            ),
            key=lambda path: path.name.casefold(),
        )
        title_files = [path for path in image_files if path.stem.casefold() == "title"]
        title_files.sort(
            key=lambda path: (
                TITLE_EXTENSION_ORDER.get(path.suffix.casefold(), 99),
                path.name.casefold(),
            )
        )
        cover_image = title_files[0].name if title_files else None
        gallery_images = [
            path.name
            for path in image_files
            if path.stem.casefold() != "title"
        ]

        discovered.append(
            {
                "id": project_id,
                "slug": slug,
                "folder_name": folder.name,
                "title": folder.name,
                "category": "Interior Project",
                "location": "",
                "description": "Project description placeholder. Replace with approved project details.",
                "description_is_placeholder": True,
                "image_dir": folder,
                "cover_image": cover_image,
                "gallery_images": gallery_images,
            }
        )

    return discovered


projects = discover_projects()
projects_by_slug = {project["slug"]: project for project in projects}


@app.route("/")
def home():
    projects_by_folder = {project["folder_name"]: project for project in projects}
    featured_projects = [
        projects_by_folder[name]
        for name in FEATURED_PROJECT_FOLDERS
        if name in projects_by_folder
    ]
    return render_template(
        "index.html",
        projects=projects,
        featured_projects=featured_projects,
    )


@app.route("/services")
def services():
    return render_template("services.html", project_count=len(projects))


@app.route("/projects")
def projects_page():
    return render_template("projects.html", projects=projects)


@app.route("/projects/<project_id>")
def project_details(project_id):
    # Slug URLs are canonical; numeric aliases keep older links resolvable.
    if project_id.isdecimal():
        project = next(
            (item for item in projects if item["id"] == int(project_id)),
            None,
        )
    else:
        project = projects_by_slug.get(project_id)

    if project is None:
        abort(404)

    return render_template("project_details.html", project=project)


@app.route("/project-images/<project_slug>/<path:filename>")
def project_image(project_slug, filename):
    project = projects_by_slug.get(project_slug)
    if project is None:
        abort(404)

    allowed_images = set(project["gallery_images"])
    if project["cover_image"]:
        allowed_images.add(project["cover_image"])
    if filename not in allowed_images:
        abort(404)
    return send_from_directory(project["image_dir"], filename)

if __name__ == "__main__":
    app.run(debug=True)
