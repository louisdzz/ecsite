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
  const peopleGrid = document.querySelector('#personnes .people-grid');
  const movementKinds = new Set(['Nomination', 'Recrutement', 'Mouvement', 'Promotion', 'Départ', "Création de cabinet", "Mouvement d’équipe"]);
  const knownMovements = new Map(peopleGrid ? [...peopleGrid.querySelectorAll('[data-home-story]')]
    .map(card => [card.dataset.homeStory, card.cloneNode(true)]) : []);
  function storyId(card) {
    const link = card.querySelector('h2 a[href]');
    return link ? new URL(link.getAttribute('href'), location.origin).pathname
      .replace(/\.html$/, '').replace(/\/$/, '').split('/').pop() : '';
  }
  function publicPath(href, prefix) {
    try {
      const url = new URL(href, location.origin);
      return url.origin === location.origin && url.pathname.startsWith(prefix) ? url.pathname : null;
    } catch (_) { return null; }
  }
  function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text) node.textContent = text;
    return node;
  }
  function movementCard(source) {
    const id = storyId(source);
    const href = publicPath(source.querySelector('h2 a')?.getAttribute('href'), '/actualites/');
    const title = source.querySelector('h2 a')?.textContent.trim();
    if (!id || !href || !title) return null;
    // Keep approved portraits for existing stories; new stories need no invented person metadata.
    if (knownMovements.has(id)) return knownMovements.get(id).cloneNode(true);
    const card = element('article', 'person-card');
    card.dataset.homeStory = id;
    const top = element('div', 'person-top');
    const mark = element('span', 'person-monogram', '↗');
    mark.setAttribute('aria-hidden', 'true');
    const meta = element('span', 'person-type', source.dataset.kind);
    const time = source.querySelector('time[datetime]');
    if (time) { meta.append(document.createElement('br'), time.cloneNode(true)); }
    top.append(mark, meta);
    const heading = element('h3');
    const link = element('a', '', title); link.href = href; heading.append(link);
    const house = source.querySelector('.news-house');
    const route = element('p', 'person-route', house?.querySelector('span')?.childNodes[0]?.textContent.trim() || '');
    const summary = element('p', '', source.querySelector('.news-summary')?.textContent.trim());
    const foot = element('div', 'person-foot');
    const read = element('a', '', 'Lire avec les sources ↗'); read.href = href; foot.append(read);
    const houseHref = publicPath(source.querySelector('.news-house a[href]')?.getAttribute('href'), '/f/');
    if (houseHref) { const houseLink = element('a', '', 'La maison'); houseLink.href = houseHref; foot.append(houseLink); }
    card.append(top, heading, route, summary, foot);
    return card;
  }
  function renderMovements(cards) {
    if (!peopleGrid) return;
    const seen = new Set();
    const records = cards.filter(card => {
      const id = storyId(card);
      if (!id || seen.has(id) || (!movementKinds.has(card.dataset.kind) && !knownMovements.has(id))) return false;
      const date = Date.parse(card.querySelector('time[datetime]')?.getAttribute('datetime') || '');
      if (!Number.isFinite(date) || date > Date.now()) return false;
      seen.add(id); return true;
    }).sort((a, b) => Date.parse(b.querySelector('time').getAttribute('datetime')) -
      Date.parse(a.querySelector('time').getAttribute('datetime')));
    const rendered = records.slice(0, 6).map(movementCard).filter(Boolean);
    // If the public feed has no eligible story or cannot be read, retain the existing edition.
    if (rendered.length) peopleGrid.replaceChildren(...rendered);
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
  fetch('/actualites.html',{credentials:'omit', cache:'no-cache'}).then(response => {
    if (!response.ok) throw new Error('Feed unavailable');
    return response.text();
  }).then(html => {
    const doc = new DOMParser().parseFromString(html,'text/html');
    const cards = [...doc.querySelectorAll('article.news-card[data-news]')];
    if (!cards.length) return;
    renderMovements(cards);
    grid.replaceChildren(...prepareCards(cards).map(card => document.importNode(card,true)));
    render();
  }).catch(() => {});
})();
