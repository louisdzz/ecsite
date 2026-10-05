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
  // A topic featured in movements or decryptages must not appear again in the news feed.
  // Explicit story IDs handle alternate article URLs without matching unrelated stories by house.
  function prepareCards(cards) {
    const seen = new Set([...document.querySelectorAll('[data-home-story]')]
      .flatMap(card => card.dataset.homeStory.split(/\s+/)));
    const segmenter = typeof Intl.Segmenter === 'function'
      ? new Intl.Segmenter('fr', {granularity:'sentence'}) : null;
    return cards.filter(card => {
      const link = card.querySelector('h2 a[href]');
      if (!link) return false;
      const story = new URL(link.getAttribute('href'), location.origin).pathname
        .replace(/\.html$/, '').replace(/\/$/, '').split('/').pop();
      if (!story || seen.has(story)) return false;
      seen.add(story);
      const summary = card.querySelector('.news-summary');
      if (summary && segmenter) {
        summary.textContent = [...segmenter.segment(summary.textContent.trim())]
          .slice(0, 2).map(part => part.segment).join('').trim();
      }
      return true;
    });
  }
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
    status.textContent = total ? `${Math.min(total,limit)} actualité${Math.min(total,limit) > 1 ? 's' : ''} affichée${Math.min(total,limit) > 1 ? 's' : ''}.` : '';
    buttons.forEach(b => b.setAttribute('aria-pressed',String(b.dataset.feedFilter === filter)));
  }
  buttons.forEach(button => button.addEventListener('click',() => {filter = button.dataset.feedFilter;render();}));
  grid.replaceChildren(...prepareCards([...grid.querySelectorAll('[data-news]')]));
  render();
  // Only use the published, same-origin feed. A failed or empty response keeps the existing edition.
  fetch('/actualites.html',{credentials:'omit'}).then(response => {
    if (!response.ok) throw new Error('Feed unavailable');
    return response.text();
  }).then(html => {
    const doc = new DOMParser().parseFromString(html,'text/html');
    const cards = [...doc.querySelectorAll('article.news-card[data-news]')];
    if (!cards.length) return;
    grid.replaceChildren(...prepareCards(cards).map(card => document.importNode(card,true)));
    render();
  }).catch(() => {});
})();
