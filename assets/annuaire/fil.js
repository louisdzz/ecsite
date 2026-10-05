(() => {
  'use strict';
  const feed = document.querySelector('.exit-feed');
  if (!feed) return;
  const grid = feed.querySelector('.exit-feed-grid');
  const status = feed.querySelector('.exit-feed-status');
  const buttons = [...feed.querySelectorAll('[data-feed-filter]')];
  let filter = 'all';
  const cession = new Set(['conseil-ma','avocats','notaires','experts-comptables']);
  const vivre = new Set(['jets','expatriation','biographies','formations-transitions','lifestyle','art-de-vivre','hotels','restaurants','vins','philanthropie']);
  function render() {
    const cards = [...grid.querySelectorAll('[data-news]')];
    let total = 0;
    const limit = filter === 'all' ? 5 : 6;
    for (const card of cards) {
      const theme = card.dataset.theme;
      const kind = card.dataset.kind;
      const movement = ['Nomination','Recrutement','Création','Ouverture','Mouvement'].includes(kind);
      const category = cession.has(theme) || kind === 'Opération' ? 'cession' : vivre.has(theme) ? 'vivre' : 'investir';
      const match = filter === 'all' || (filter === 'mouvements' ? movement : category === filter);
      card.hidden = !match || total >= limit;
      if (match) total++;
    }
    feed.querySelector('.exit-feed-empty').hidden = total !== 0;
    status.textContent = total ? `${Math.min(total,limit)} sur ${total} article${total > 1 ? 's' : ''} publié${total > 1 ? 's' : ''}.` : '';
    buttons.forEach(b => b.setAttribute('aria-pressed',String(b.dataset.feedFilter === filter)));
  }
  buttons.forEach(button => button.addEventListener('click',() => {filter = button.dataset.feedFilter;render();}));
  render();
  // Only use the published, same-origin feed. A failed or empty response keeps the existing edition.
  fetch('/actualites.html',{credentials:'omit'}).then(response => {
    if (!response.ok) throw new Error('Feed unavailable');
    return response.text();
  }).then(html => {
    const doc = new DOMParser().parseFromString(html,'text/html');
    const cards = [...doc.querySelectorAll('article.news-card[data-news]')];
    if (!cards.length) return;
    grid.replaceChildren(...cards.map(card => document.importNode(card,true)));
    render();
  }).catch(() => {});
})();
