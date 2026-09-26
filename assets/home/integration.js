(function () {
  'use strict';
  const menu = document.querySelector('.menu');
  const nav = document.querySelector('#nav');
  function closeMenu(restoreFocus) {
    if (!menu || !nav || !nav.classList.contains('open')) return;
    nav.classList.remove('open');
    menu.setAttribute('aria-expanded', 'false');
    menu.setAttribute('aria-label', 'Ouvrir le menu');
    menu.textContent = '☰';
    if (restoreFocus) menu.focus();
  }
  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') closeMenu(true);
  });
  document.addEventListener('click', function (event) {
    if (nav && menu && !nav.contains(event.target) && !menu.contains(event.target)) closeMenu(false);
  });
  window.matchMedia('(min-width: 681px)').addEventListener('change', function (event) {
    if (event.matches) closeMenu(false);
  });

  // L'ancien lien direct vers les valeurs reste utile après la refonte.
  function preserveValuesLink() {
    if (location.pathname === '/' && location.hash === '#valeurs') {
      location.replace('/manifeste' + location.search + '#valeurs');
    }
  }
  preserveValuesLink();
  window.addEventListener('hashchange', preserveValuesLink);

  // Conserver le suivi de parrainage existant, sans envoyer de visites de prévisualisation.
  if (['exit.club', 'www.exit.club'].includes(location.hostname)) {
    const tracking = document.createElement('script');
    tracking.async = true;
    tracking.src = 'https://cdn.promotekit.com/pk.js';
    tracking.dataset.promotekit = '28e58480-1d14-41dc-abdb-d778a9db9cff';
    document.head.appendChild(tracking);
  }
})();
