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
