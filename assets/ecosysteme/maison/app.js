'use strict';
const $ = (s) => document.querySelector(s);
const input = $('#recherche');
const results = $('#results');
const toggle = $('#category-toggle');
const categoryList = $('#category-list');
const pageSize = 12;
const number = new Intl.NumberFormat('fr-FR');
const normalize = (s) => s.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[’'&\-]/g, ' ').replace(/\s+/g, ' ').trim();
const labels = {
  'banques-affaires': 'Banques d’affaires', 'boutiques-ma': 'Boutiques M&A', mfo: 'Multi-family offices',
  'banques-privees': 'Banques privées', avocats: 'Avocats & fiscalistes', 'experts-comptables': 'Experts-comptables',
  notaires: 'Notaires patrimoniaux', cgp: 'Gestion de patrimoine', 'assurance-vie-lux': 'Assurance-vie luxembourgeoise',
  treso: 'Trésorerie & monétaire', 'actifs-numeriques': 'Actifs numériques', 'fonds-pe': 'Private equity & LBO',
  'fonds-dette': 'Fonds de dette', 'fonds-vc': 'Venture capital', secondaire: 'Secondaire & pré-IPO', jets: 'Aviation d’affaires',
  expatriation: 'Expatriation & installation à l’étranger'
};
let houses = [], categories = [], active = '', limit = pageSize;

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}
function closeCategories() {
  categoryList.classList.remove('open');
  toggle.setAttribute('aria-expanded', 'false');
  toggle.lastElementChild.textContent = '+';
}
function updateURL() {
  const params = new URLSearchParams();
  if (input.value.trim()) params.set('q', input.value.trim());
  if (active) params.set('metier', active);
  const query = params.toString();
  history.replaceState(null, '', location.pathname + (query ? '?' + query : '') + location.hash);
}
function renderCategories() {
  categoryList.replaceChildren();
  const choices = [{ id: '', name: 'Toutes les maisons' }, ...categories];
  choices.forEach((category) => {
    const button = el('button', 'category-button');
    button.type = 'button';
    button.dataset.category = category.id;
    button.setAttribute('aria-pressed', String(active === category.id));
    const count = category.id ? houses.filter(h => h.categories.includes(category.id)).length : houses.length;
    button.append(el('span', '', labels[category.id] || category.name), el('span', '', number.format(count)));
    button.addEventListener('click', () => {
      active = category.id; limit = pageSize; closeCategories(); render();
      if (matchMedia('(max-width:800px)').matches) $('#results-title').focus({ preventScroll: true });
    });
    categoryList.append(button);
  });
}
function render() {
  const words = normalize(input.value).split(' ').filter(Boolean);
  const filtered = houses.filter(h => (!active || h.categories.includes(active)) && words.every(w => h.search.includes(w)));
  const previousSize = results.children.length;
  const visible = filtered.slice(0, limit);
  results.replaceChildren();
  visible.forEach(h => {
    const item = el('article', 'house');
    const a = el('a');
    a.href = `/f/${encodeURIComponent(h.slug)}`;
    const top = el('div', 'house-top');
    const mark = el('span', 'house-mark');
    mark.setAttribute('aria-hidden', 'true');
    if (h.logo) {
      const img = document.createElement('img');
      img.src = h.logo.src || `assets/${h.slug}.webp`; img.alt = ''; img.loading = 'lazy'; img.decoding = 'async';
      if (h.logo.dark) mark.classList.add('logo-dark');
      if (h.logo.wide) mark.classList.add('logo-wide');
      img.addEventListener('error', () => { mark.classList.add('logo-unavailable'); mark.replaceChildren(); }, { once: true });
      mark.append(img);
    } else { mark.classList.add('logo-unavailable'); }
    const arrow = el('span', 'house-arrow', '↗'); arrow.setAttribute('aria-hidden', 'true');
    top.append(mark, arrow);
    a.append(top, el('h3', '', h.name), el('p', '', h.categories.map(c => labels[c] || c).join(' · ')));
    if (h.note) a.append(el('p', 'house-note', h.note));
    if (h.logoAttribution) a.append(el('p', 'house-note logo-attribution', h.logoAttribution));
    item.append(a); results.append(item);
  });
  $('#results-title').textContent = active ? labels[active] : 'Toutes les maisons';
  $('#results-count').textContent = `${number.format(filtered.length)} maison${filtered.length > 1 ? 's' : ''}${words.length ? ' trouvée' + (filtered.length > 1 ? 's' : '') : ' référencée' + (filtered.length > 1 ? 's' : '')}`;
  $('#results-context').textContent = input.value.trim() ? `Recherche : « ${input.value.trim()} »` : 'Par ordre alphabétique';
  $('#reset-results').hidden = !active && !input.value.trim();
  $('#shown-count').textContent = filtered.length ? `${number.format(visible.length)} sur ${number.format(filtered.length)} maisons` : '';
  $('#load-more').hidden = limit >= filtered.length;
  $('#empty-state').hidden = filtered.length !== 0;
  categoryList.querySelectorAll('button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.category === active)));
  updateURL();
  return { previousSize, visible };
}
function reset(event) {
  event.preventDefault(); input.value = ''; active = ''; limit = pageSize; closeCategories(); render(); input.focus({ preventScroll: true });
}
document.querySelectorAll('.reset-all').forEach(b => b.addEventListener('click', reset));
input.addEventListener('input', () => { limit = pageSize; render(); });
$('.search-form').addEventListener('submit', e => {
  e.preventDefault(); limit = pageSize; render(); $('#results-title').focus({ preventScroll: true }); $('#annuaire').scrollIntoView({ block: 'start' });
});
document.querySelectorAll('.example').forEach(b => b.addEventListener('click', () => {
  input.value = b.dataset.query; active = ''; limit = pageSize; closeCategories(); render(); $('#results-title').focus({ preventScroll: true }); $('#annuaire').scrollIntoView({ block: 'start' });
}));
$('#load-more').addEventListener('click', () => {
  const old = results.children.length; limit += pageSize; render(); results.children[old]?.querySelector('a').focus({ preventScroll: true });
});
toggle.addEventListener('click', () => {
  const open = toggle.getAttribute('aria-expanded') !== 'true';
  toggle.setAttribute('aria-expanded', String(open)); categoryList.classList.toggle('open', open); toggle.lastElementChild.textContent = open ? '−' : '+';
});
document.addEventListener('keydown', e => {
  if (e.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') { closeCategories(); toggle.focus(); }
  if (e.key === '/' && !['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName) && !document.activeElement.isContentEditable) { e.preventDefault(); input.focus(); }
});
async function init() {
  try {
    const response = await fetch('/assets/ecosysteme/maison/data.json?v=20260916-suite-v3');
    if (!response.ok) throw new Error('Data unavailable');
    const data = await response.json(); categories = data.categories;
    const categoryNames = Object.fromEntries(categories.map(c => [c.id, c.name]));
    houses = data.houses.sort((a,b) => a.name.localeCompare(b.name, 'fr', { sensitivity: 'base', ignorePunctuation: true })).map(h => ({ ...h, search: normalize(h.name + ' ' + h.categories.map(c => categoryNames[c] + ' ' + labels[c]).join(' ') + ' ' + (h.keywords || []).join(' ') + ' ' + (h.logoAttribution || '')) }));
    const params = new URLSearchParams(location.search);
    input.value = params.get('q') || '';
    const requested = params.get('metier') || location.hash.slice(1);
    active = categories.some(c => c.id === requested) ? requested : '';
    if (['ligues','ligue-cgp','actualites','argent','vie'].includes(location.hash.slice(1))) { location.replace('/ecosysteme-ligues' + location.hash); return; }
    $('#total-count').textContent = number.format(houses.length);
    renderCategories(); render();
  } catch (error) {
    $('#results-count').textContent = 'Chargement indisponible';
    const p = el('p', '', 'L’annuaire n’a pas pu être chargé. ');
    const a = el('a', 'text-link', 'Consulter l’annuaire public ↗'); a.href = 'https://www.exit.club/annuaire';
    p.append(a); results.replaceChildren(p); $('#load-more').hidden = true;
  }
}
init();

window.addEventListener('hashchange', () => { const key = location.hash.slice(1); if (categories.some(c => c.id === key)) { active = key; limit = pageSize; render(); document.querySelector('#annuaire').scrollIntoView({block:'start'}); } else if (['ligues','ligue-cgp','actualites','argent','vie'].includes(key)) { location.assign('/ecosysteme-ligues' + location.hash); } });
