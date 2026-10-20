/* Les ancres historiques ouvrent le dossier avant de le rejoindre. */
(() => {
  const reveal = (hash, scroll) => {
    if (!hash || hash === '#') return;
    let target;
    try { target = document.getElementById(decodeURIComponent(hash.slice(1))); } catch { return; }
    if (!target) return;
    if (target.tagName === 'DETAILS') target.open = true;
    let parent = target.parentElement;
    while (parent) {
      if (parent.tagName === 'DETAILS') parent.open = true;
      parent = parent.parentElement;
    }
    if (scroll) requestAnimationFrame(() => target.scrollIntoView({block:'start'}));
  };
  document.addEventListener('click', event => {
    const anchor = event.target.closest('a[href^="#"]');
    if (anchor) reveal(anchor.hash, false);
  });
  window.addEventListener('hashchange', () => reveal(location.hash, true));
  reveal(location.hash, Boolean(location.hash));
})();

/* Renforcer la comparaison depuis la destination de catégorie déjà publiée. */
(() => {
  const profile = document.querySelector('.profile-visual-v2 .pv-main');
  const actions = profile?.querySelector('.pv-actions');
  if (!actions) return;
  const categoryURL = anchor => {
    if (!anchor) return null;
    try {
      const url = new URL(anchor.getAttribute('href'), location.href);
      if (url.origin !== location.origin || url.pathname !== '/annuaire' ||
          !url.searchParams.get('metier')) return null;
      url.hash = 'annuaire';
      return url.pathname + url.search + url.hash;
    } catch { return null; }
  };
  const links = [...actions.querySelectorAll('a[href]')];
  let comparison = links.find(anchor => categoryURL(anchor));
  const destination = categoryURL(comparison) || categoryURL(profile.querySelector('a.pv-category[href]'));
  if (!destination) return;
  if (!comparison) {
    comparison = document.createElement('a');
    comparison.className = 'pv-secondary';
    const secondary = actions.querySelector('.pv-secondary');
    if (secondary) secondary.before(comparison);
    else actions.append(comparison);
  }
  comparison.href = destination;
  comparison.classList.add('pv-comparison-cta');
  const arrow = comparison.querySelector('svg') || actions.querySelector('.pv-secondary svg')?.cloneNode(true);
  comparison.replaceChildren(document.createTextNode('Comparer avec les autres acteurs'));
  if (arrow) comparison.append(arrow);

  // Le tableau de produits Spiko reste accessible, avec un libellé distinct.
  for (const anchor of links) {
    try {
      const url = new URL(anchor.getAttribute('href'), location.href);
      if (url.origin !== location.origin || url.pathname !== '/tresorerie') continue;
      const icon = anchor.querySelector('svg');
      anchor.replaceChildren(document.createTextNode('Voir le tableau détaillé'));
      if (icon) anchor.append(icon);
    } catch { /* Laisser les autres liens et les ancres historiques inchangés. */ }
  }
})();
