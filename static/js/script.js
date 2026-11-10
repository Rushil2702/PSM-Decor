(() => {
    const toggle = document.querySelector('.menu-toggle');
    const navigation = document.querySelector('#primary-navigation');
    if (!toggle || !navigation) return;
    toggle.addEventListener('click', () => {
        const isOpen = toggle.getAttribute('aria-expanded') === 'true';
        toggle.setAttribute('aria-expanded', String(!isOpen));
        toggle.setAttribute('aria-label', isOpen ? 'Open navigation' : 'Close navigation');
        navigation.classList.toggle('is-open', !isOpen);
    });
    navigation.addEventListener('click', (event) => {
        if (event.target.closest('a')) {
            navigation.classList.remove('is-open');
            toggle.setAttribute('aria-expanded', 'false');
            toggle.setAttribute('aria-label', 'Open navigation');
        }
    });
})();
