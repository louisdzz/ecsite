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
  'conseil-ma': 'Conseil M&A', 'banques-affaires': 'Banques d’affaires', 'boutiques-ma': 'Boutiques M&A', mfo: 'Multi-family offices',
  'banques-privees': 'Banques privées', avocats: 'Avocats & fiscalistes', 'experts-comptables': 'Experts-comptables',
  notaires: 'Notaires patrimoniaux', cgp: 'Gestion de patrimoine', 'assurance-vie-lux': 'Assurance-vie luxembourgeoise',
  treso: 'Trésorerie & monétaire', 'actifs-numeriques': 'Actifs numériques', 'fonds-pe': 'Private equity & LBO',
  'fonds-dette': 'Fonds de dette', 'fonds-vc': 'Venture capital', secondaire: 'Secondaire & pré-IPO', 'secondaire-fonds': 'Secondaire de fonds & private equity', jets: 'Aviation d’affaires',
  expatriation: 'Expatriation & installation à l’étranger',
  biographies: 'Biographies & mémoire familiale',
  'formations-transitions': 'Formations & nouvelles perspectives',
  'conseil-rh': 'Conseil RH et intégration',
  intermediaires: 'Intermédiaires & distribution de fonds',
  hotels: 'Hôtels', montres: 'Montres', voyages: 'Voyages sur mesure', yachting: 'Yachting'
};
let houses = [], categories = [], active = '', maType = '', secondaryRole = '', limit = pageSize;
// Public identity export, controlled 1 November 2026. No CRM/private data.
const publicProfiles = [{"id":"degryck","name":"Michel Degryck","house":"Investec Advisory France","houseSlug":null,"role":"Associé","specialty":"Services & industrie","category":"conseil-ma","photo":"https://annuaire-exit-classement-maquette.louisdeb.chatgpt.site/assets/portraits/degryck.jpg"},{"id":"vonbulow","name":"Nicolas von Bülow","house":"Clipperton","houseSlug":"clipperton","role":"Managing Partner","specialty":"Tech & logiciels","category":"conseil-ma","photo":"https://annuaire-exit-classement-maquette.louisdeb.chatgpt.site/assets/portraits/vonbulow.jpg"},{"id":"salabi","name":"David Salabi","house":"Cambon Partners","houseSlug":"cambon-partners","role":"Associé fondateur","specialty":"Entreprises de croissance","category":"conseil-ma","photo":"https://annuaire-exit-classement-maquette.louisdeb.chatgpt.site/assets/portraits/salabi.jpg"},{"id":"benin","name":"David Benin","house":"Houlihan Lokey","houseSlug":"houlihan-lokey","role":"Managing Director","specialty":"Industrie & aéronautique","category":"conseil-ma","photo":null},{"id":"scheer","name":"Fabrice Scheer","house":"Alantra","houseSlug":"alantra","role":"Managing Partner","specialty":"Services & industrie","category":"conseil-ma","photo":"https://annuaire-exit-classement-maquette.louisdeb.chatgpt.site/assets/portraits/scheer.jpg"},{"id":"noat","name":"Franck Noat","house":"Alantra","houseSlug":"alantra","role":"Managing Partner","specialty":"Santé","category":"conseil-ma","photo":"https://annuaire-exit-classement-maquette.louisdeb.chatgpt.site/assets/portraits/noat.jpg"},{"id":"bertier","name":"Thomas Bertier","house":"Cambon Partners","houseSlug":"cambon-partners","role":"Managing Director","specialty":"Venture & growth","category":"conseil-ma","photo":"https://annuaire-exit-classement-maquette.louisdeb.chatgpt.site/assets/portraits/bertier.jpg"},{"id":"larreur","name":"Charles-Henri Larreur","house":"Virellian Partners","houseSlug":null,"role":"Managing Partner","specialty":"Infrastructure","category":"conseil-ma","photo":"https://annuaire-exit-classement-maquette.louisdeb.chatgpt.site/assets/portraits/larreur.jpg"},{"id":"alter","name":"Arik Alter","house":"Rothschild & Co · Transaction R&Co","houseSlug":"rothschild-co","role":"Conseil M&A · Transaction R&Co","specialty":"PME & ETI","category":"conseil-ma","photo":null},{"id":"deltoso","name":"Christophe Del Toso","house":"In Extenso Finance","houseSlug":"in-extenso-finance","role":"Directeur général","specialty":"PME & ETI","category":"conseil-ma","photo":"https://annuaire-exit-classement-maquette.louisdeb.chatgpt.site/assets/portraits/deltoso.jpg"},{"id":"montille","name":"Thomas de Montille","house":"Clipperton","houseSlug":"clipperton","role":"Managing Partner","specialty":"Travel tech & services B2B","category":"conseil-ma","photo":"https://annuaire-exit-classement-maquette.louisdeb.chatgpt.site/assets/portraits/montille.jpg"},{"id":"dardel","name":"Olivier Dardel","house":"Natixis Partners","houseSlug":"natixis-partners","role":"Conseil M&A","specialty":"Acquisitions & private equity","category":"conseil-ma","photo":null},{"id":"tenhave","name":"Guillaume ten Have","house":"Investec Advisory France","houseSlug":null,"role":"Associé","specialty":"Industrie & services","category":"conseil-ma","photo":"https://annuaire-exit-classement-maquette.louisdeb.chatgpt.site/assets/portraits/tenhave.jpg"},{"id":"alle","name":"Augustin Alle","house":"Investec Advisory France","houseSlug":null,"role":"Directeur","specialty":"Services & transmissions","category":"conseil-ma","photo":"https://annuaire-exit-classement-maquette.louisdeb.chatgpt.site/assets/portraits/alle.jpg"},{"id":"dattee","name":"Jean-Arthur Dattée","house":"Investec Advisory France","houseSlug":null,"role":"Associé","specialty":"TMT & services professionnels","category":"conseil-ma","photo":"https://annuaire-exit-classement-maquette.louisdeb.chatgpt.site/assets/portraits/dattee.jpg"},{"id":"feydeau","name":"Ghislain de Feydeau","house":"Oaklins France","houseSlug":"oaklins-arjil","role":"Director","specialty":"Industrie & packaging","category":"conseil-ma","photo":"https://annuaire-exit-classement-maquette.louisdeb.chatgpt.site/assets/portraits/feydeau.jpg"},{"id":"senlis","name":"Nicolas Senlis","house":"Alantra","houseSlug":"alantra","role":"Managing Partner","specialty":"Santé & services","category":"conseil-ma","photo":null},{"id":"bursztyn","name":"Jonathan Bursztyn","house":"Financière de Courcelles","houseSlug":"financiere-de-courcelles","role":"Managing Partner","specialty":"Industrie & services","category":"conseil-ma","photo":"https://annuaire-exit-classement-maquette.louisdeb.chatgpt.site/assets/portraits/bursztyn.jpg"},{"id":"felixfaure","name":"Eric Félix-Faure","house":"Oaklins France","houseSlug":"oaklins-arjil","role":"Managing Partner","specialty":"Industrie & services","category":"conseil-ma","photo":null},{"id":"vielle","name":"Martin Vielle","house":"Clipperton","houseSlug":"clipperton","role":"Partner","specialty":"Logiciels & deep tech","category":"conseil-ma","photo":"https://annuaire-exit-classement-maquette.louisdeb.chatgpt.site/assets/portraits/vielle.jpg"},{"id":"revel","name":"Thibaut Revel","house":"Clipperton","houseSlug":"clipperton","role":"Managing Partner","specialty":"Logiciels & services B2B","category":"conseil-ma","photo":"https://annuaire-exit-classement-maquette.louisdeb.chatgpt.site/assets/portraits/revel.jpg"},{"id":"schafer","name":"Marc Schäfer","house":"Clipperton","houseSlug":"clipperton","role":"Executive Director","specialty":"Logiciels B2B","category":"conseil-ma","photo":"https://annuaire-exit-classement-maquette.louisdeb.chatgpt.site/assets/portraits/schafer.jpg"},{"id":"rodriguez","name":"Stéphane Rodriguez","house":"Lamartine Conseil","houseSlug":"lamartine-conseil","role":"Avocat associé","specialty":"LBO & transmission","category":"avocats","photo":"https://annuaire-exit-classement-maquette.louisdeb.chatgpt.site/assets/portraits/rodriguez.jpg"},{"id":"ricome","name":"Thibault Ricome","house":"Lexicube","houseSlug":null,"role":"Avocat associé","specialty":"LBO & capital-investissement","category":"avocats","photo":"https://annuaire-exit-classement-maquette.louisdeb.chatgpt.site/assets/portraits/ricome.avif"},{"id":"laubert","name":"Déborah Laubert","house":"Lexicube","houseSlug":null,"role":"Avocate","specialty":"Corporate & croissance externe","category":"avocats","photo":"https://annuaire-exit-classement-maquette.louisdeb.chatgpt.site/assets/portraits/laubert.avif"},{"id":"segonds","name":"Tristan Segonds","house":"Mermoz Avocats","houseSlug":null,"role":"Avocat associé","specialty":"Private equity & M&A","category":"avocats","photo":"https://annuaire-exit-classement-maquette.louisdeb.chatgpt.site/assets/portraits/segonds.jpg"},{"id":"roux","name":"Gilles Roux","house":"Mermoz Avocats","houseSlug":null,"role":"Avocat associé","specialty":"Private equity & M&A","category":"avocats","photo":"https://annuaire-exit-classement-maquette.louisdeb.chatgpt.site/assets/portraits/roux.jpg"},{"id":"crepy","name":"Sébastien Crepy","house":"Gide","houseSlug":"gide-loyrette-nouel","role":"Avocat associé","specialty":"LBO & private equity","category":"avocats","photo":"https://annuaire-exit-classement-maquette.louisdeb.chatgpt.site/assets/portraits/crepy.jpg"},{"id":"nacinovic","name":"Vincent Nacinovic","house":"Gide","houseSlug":"gide-loyrette-nouel","role":"Avocat associé","specialty":"LBO & private equity","category":"avocats","photo":"https://annuaire-exit-classement-maquette.louisdeb.chatgpt.site/assets/portraits/nacinovic.jpg"},{"id":"thebault","name":"Olivier Thébault","house":"A&O Shearman","houseSlug":"a-o-shearman","role":"Avocat associé","specialty":"Corporate & marchés de capitaux","category":"avocats","photo":"https://annuaire-exit-classement-maquette.louisdeb.chatgpt.site/assets/portraits/thebault.jpg"},{"id":"romain","name":"Kate Romain","house":"Bredin Prat","houseSlug":"bredin-prat","role":"Avocate associée","specialty":"Fusions-acquisitions","category":"avocats","photo":"https://annuaire-exit-classement-maquette.louisdeb.chatgpt.site/assets/portraits/romain.jpg"},{"id":"angel","name":"Karine Angel","house":"Bredin Prat","houseSlug":"bredin-prat","role":"Avocate associée","specialty":"Fusions-acquisitions","category":"avocats","photo":"https://annuaire-exit-classement-maquette.louisdeb.chatgpt.site/assets/portraits/angel.jpg"},{"id":"soumagne","name":"Adrien Soumagne","house":"Bredin Prat","houseSlug":"bredin-prat","role":"Avocat associé","specialty":"Fiscalité transactionnelle","category":"avocats","photo":"https://annuaire-exit-classement-maquette.louisdeb.chatgpt.site/assets/portraits/soumagne.jpg"},{"id":"mandelbaum","name":"Jean-Florent Mandelbaum","house":"Bredin Prat","houseSlug":"bredin-prat","role":"Avocat associé","specialty":"Fiscalité transactionnelle","category":"avocats","photo":"https://annuaire-exit-classement-maquette.louisdeb.chatgpt.site/assets/portraits/mandelbaum.jpg"},{"id":"robert","name":"Anne Robert","house":"Bredin Prat","houseSlug":"bredin-prat","role":"Avocate associée","specialty":"Fiscalité transactionnelle","category":"avocats","photo":"https://annuaire-exit-classement-maquette.louisdeb.chatgpt.site/assets/portraits/robert.jpg"},{"id":"bosc","name":"Frédéric Bosc","house":"Moncey Avocats","houseSlug":null,"role":"Avocat associé","specialty":"Fiscalité des LBO et de la cession","category":"avocats","photo":"https://annuaire-exit-classement-maquette.louisdeb.chatgpt.site/assets/portraits/bosc.jpg"},{"id":"bruneel","name":"Marie-Laure Bruneel","house":"Goodwin","houseSlug":"goodwin-procter-france","role":"Avocate associée","specialty":"Fiscalité transactionnelle","category":"avocats","photo":null},{"id":"fourniere","name":"Paul Fournière","house":"Goodwin","houseSlug":"goodwin-procter-france","role":"Avocat collaborateur","specialty":"Fiscalité transactionnelle","category":"avocats","photo":null},{"id":"filleux","name":"Charles Filleux-Pommerol","house":"Paul Hastings","houseSlug":"paul-hastings","role":"Avocat associé","specialty":"Fiscalité transactionnelle","category":"avocats","photo":null},{"id":"loup","name":"André Loup","house":"Ydès","houseSlug":"ydes","role":"Avocat associé","specialty":"Fiscalité de la cession","category":"avocats","photo":"https://annuaire-exit-classement-maquette.louisdeb.chatgpt.site/assets/portraits/loup.png"},{"id":"gour","name":"Pascal Gour","house":"Jeausserand Audouard","houseSlug":"jeausserand-audouard","role":"Avocat associé","specialty":"Fiscalité des dirigeants et de la cession","category":"avocats","photo":"https://annuaire-exit-classement-maquette.louisdeb.chatgpt.site/assets/portraits/gour.jpg"},{"id":"rauch","name":"Olivia Rauch-Ravisé","house":"Latham & Watkins","houseSlug":"latham-watkins","role":"Avocate associée","specialty":"Fiscalité transactionnelle","category":"avocats","photo":"https://annuaire-exit-classement-maquette.louisdeb.chatgpt.site/assets/portraits/rauch.jpg"},{"id":"xerri","name":"Emmanuel Xerri","house":"Financière de Courcelles","houseSlug":"financiere-de-courcelles","role":"Managing Partner","specialty":"Dette & financement","category":"conseil-ma","photo":"https://annuaire-exit-classement-maquette.louisdeb.chatgpt.site/assets/portraits/xerri.png"},{"id":"avosse","name":"Kodjo Avosse","house":"Financière de Courcelles","houseSlug":"financiere-de-courcelles","role":"Analyst","specialty":"Dette & financement","category":"conseil-ma","photo":"https://annuaire-exit-classement-maquette.louisdeb.chatgpt.site/assets/portraits/avosse.png"},{"id":"nahon","name":"Pierre-Louis Nahon","house":"Alantra","houseSlug":"alantra","role":"Managing Partner · Head of Debt Advisory France","specialty":"Dette & refinancement","category":"conseil-ma","photo":"https://annuaire-exit-classement-maquette.louisdeb.chatgpt.site/assets/portraits/nahon.png"},{"id":"berta","name":"Simon Berta","house":"Alantra","houseSlug":"alantra","role":"Director · Debt Advisory","specialty":"Dette & refinancement","category":"conseil-ma","photo":"https://annuaire-exit-classement-maquette.louisdeb.chatgpt.site/assets/portraits/berta.png"},{"id":"vlach","name":"Jérémy Vlach","house":"Grant Thornton France","houseSlug":"grant-thornton-france","role":"Associé · Modeling & Debt Advisory","specialty":"Financement de projets","category":"conseil-ma","photo":"https://annuaire-exit-classement-maquette.louisdeb.chatgpt.site/assets/portraits/vlach.jpg"},{"id":"ranaivosoa","name":"Dinan Ranaivosoa","house":"Grant Thornton France","houseSlug":"grant-thornton-france","role":"Manager · Modeling & Debt Advisory","specialty":"Financement de projets","category":"conseil-ma","photo":null},{"id":"nguyen","name":"Stéphane Nguyen","house":"Grant Thornton France","houseSlug":"grant-thornton-france","role":"Analyste · Modeling & Debt Advisory","specialty":"Financement de projets","category":"conseil-ma","photo":null},{"id":"palleau","name":"Serge Palleau","house":"Lincoln International","houseSlug":"lincoln-international","role":"Managing Director","specialty":"Dette & financement","category":"conseil-ma","photo":"https://annuaire-exit-classement-maquette.louisdeb.chatgpt.site/assets/portraits/palleau.jpg"},{"id":"assael","name":"Paul Assaël","house":"Edmond de Rothschild Corporate Finance","houseSlug":"edmond-de-rothschild-cf","role":"Managing Director · Conseil en financement","specialty":"Dette & financement","category":"conseil-ma","photo":"https://annuaire-exit-classement-maquette.louisdeb.chatgpt.site/assets/portraits/assael.jpg"},{"id":"martinez","name":"Carlos Martinez Oliva","house":"Edmond de Rothschild Corporate Finance","houseSlug":"edmond-de-rothschild-cf","role":"Conseil en financement","specialty":"Dette & financement","category":"conseil-ma","photo":null}];
const profileDirectoryOrigin = '/annuaire';


function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}
function showHouseName(mark, name) {
  mark.classList.remove('logo-dark', 'logo-wide');
  mark.classList.add('logo-unavailable');
  mark.classList.toggle('logo-name-long', name.length > 24);
  mark.replaceChildren(el('span', 'house-nameplate', name));
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
  if (active === 'secondaire' && secondaryRole) params.set('role', secondaryRole);
  if (active === 'conseil-ma' && maType) params.set('type', maType);
  const query = params.toString();
  history.replaceState(null, '', location.pathname + (query ? '?' + query : '') + location.hash);
}
function renderCategories() {
  categoryList.replaceChildren();
  const choices = [{ id: '', name: 'Toutes les sociétés' }, ...categories];
  choices.forEach((category) => {
    const button = el('button', 'category-button');
    button.type = 'button';
    button.dataset.category = category.id;
    button.setAttribute('aria-pressed', String(active === category.id));
    const count = category.id ? houses.filter(h => h.categories.includes(category.id)).length : houses.length;
    button.append(el('span', '', labels[category.id] || category.name), el('span', '', number.format(count)));
    button.addEventListener('click', () => {
      active = category.id; maType = ''; secondaryRole = ''; limit = pageSize; closeCategories(); render();
      if (matchMedia('(max-width:800px)').matches) $('#results-title').focus({ preventScroll: true });
    });
    categoryList.append(button);
  });
}
function render() {
  const words = normalize(input.value).split(' ').filter(Boolean);
  const matchedProfiles = words.length ? publicProfiles.filter(p => (!active || p.category === active) && (!maType || (p.houseSlug && houses.some(h => h.slug === p.houseSlug && h.maTypes.includes(maType)))) && words.every(w => normalize(p.name + ' ' + p.house + ' ' + p.specialty).includes(w))) : [];
  const matchedHouseSlugs = new Set(matchedProfiles.map(p => p.houseSlug).filter(Boolean));
  const filtered = houses.filter(h => (!active || h.categories.includes(active)) && (active !== 'conseil-ma' || !maType || h.maTypes.includes(maType)) && (active !== 'secondaire' || !secondaryRole || h.secondaryRole === secondaryRole) && (words.every(w => h.search.includes(w)) || matchedHouseSlugs.has(h.slug)));
  renderProfileResults(matchedProfiles);

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
      img.addEventListener('error', () => showHouseName(mark, h.name), { once: true });
      mark.append(img);
    } else { showHouseName(mark, h.name); }
    const arrow = el('span', 'house-arrow', '↗'); arrow.setAttribute('aria-hidden', 'true');
    top.append(mark, arrow);
    a.append(top, el('h3', '', h.name), el('p', '', h.categories.map(c => labels[c] || c).join(' · ')));
    if (h.note) a.append(el('p', 'house-note', h.note));
    if (h.logoAttribution) a.append(el('p', 'house-note logo-attribution', h.logoAttribution));
    item.append(a); results.append(item);
  });
  $('#results-title').textContent = active ? labels[active] : ($('#results-title').dataset.defaultTitle || 'Toutes les sociétés');
  $('#results-count').textContent = `${number.format(filtered.length)} société${filtered.length > 1 ? 's' : ''}${words.length ? ' trouvée' + (filtered.length > 1 ? 's' : '') : ' référencée' + (filtered.length > 1 ? 's' : '')}` + (matchedProfiles.length ? ` · ${number.format(matchedProfiles.length)} professionnel${matchedProfiles.length > 1 ? 's' : ''}` : '');
  $('#results-context').textContent = input.value.trim() ? `Recherche : « ${input.value.trim()} »` : 'Par ordre alphabétique';
  $('#reset-results').hidden = !active && !input.value.trim();
  $('#shown-count').textContent = filtered.length ? `${number.format(visible.length)} sur ${number.format(filtered.length)} sociétés` : '';
  $('#load-more').hidden = limit >= filtered.length && limit >= matchedProfiles.length;
  $('#empty-state').hidden = filtered.length !== 0 || matchedProfiles.length !== 0;
  categoryList.querySelectorAll('button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.category === active)));
  renderMaFilters();
  const hotelEditorial = $('#hotels-editorial');
  if (hotelEditorial) hotelEditorial.hidden = active !== 'hotels';
  updateURL();
  document.dispatchEvent(new CustomEvent('annuaire:results', { detail: { category: active, query: input.value.trim(), slugs: filtered.map(h => h.slug) } }));
  return { previousSize, visible };
}
function renderProfileResults(profiles) {
  let section = $('#person-results');
  if (!section) {
    section = el('section', 'person-results'); section.id = 'person-results';
    section.setAttribute('aria-label', 'Professionnels correspondant à votre recherche');
    section.style.cssText = 'margin:0 0 32px';
    results.before(section);
  }
  section.hidden = profiles.length === 0; section.replaceChildren();
  if (!profiles.length) return;
  section.append(el('h3', '', 'Les professionnels'));
  const grid = el('div', 'results-grid'); grid.style.marginTop = '20px';
  profiles.slice(0, limit).forEach(p => {
    const item = el('article', 'house person-result'); const a = el('a');
    a.href = profileDirectoryOrigin + '?person=' + encodeURIComponent(p.id);
    const top = el('div', 'house-top'); const portrait = el('span', 'house-mark');
    if (p.photo) {
      const img = document.createElement('img'); img.src = p.photo; img.alt = p.name; img.loading = 'lazy';
      img.style.cssText = 'width:64px;height:64px;border-radius:50%;object-fit:cover'; portrait.append(img);
      img.addEventListener('error', () => { portrait.replaceChildren(el('span', '', p.name.split(' ').map(n=>n[0]).slice(0,2).join(''))); }, { once:true });
    } else portrait.append(el('span', '', p.name.split(' ').map(n=>n[0]).slice(0,2).join('')));
    top.append(portrait, el('span', 'house-arrow', '↗'));
    a.append(top, el('h3', '', p.name), el('p', '', p.house), el('p', 'house-note', p.role), el('p', 'house-note', p.specialty), el('p', 'text-link', 'Voir le profil et les opérations ↗'));
    item.append(a); grid.append(item);
  });
  section.append(grid, el('p', 'ma-help', 'Profils individuels documentés. Leurs opérations et sources sont accessibles sur chaque profil. La sélection reste partielle.'));
}
function reset(event) {
  event.preventDefault(); input.value = ''; active = ''; maType = ''; secondaryRole = ''; limit = pageSize; closeCategories(); render(); input.focus({ preventScroll: true });
}
document.querySelectorAll('.reset-all').forEach(b => b.addEventListener('click', reset));
input.addEventListener('input', () => { limit = pageSize; render(); });
$('.search-form').addEventListener('submit', e => {
  e.preventDefault(); limit = pageSize; render(); $('#results-title').focus({ preventScroll: true }); $('#annuaire').scrollIntoView({ block: 'start' });
});
document.querySelectorAll('.example').forEach(b => b.addEventListener('click', () => {
  input.value = b.dataset.query; active = ''; maType = ''; secondaryRole = ''; limit = pageSize; closeCategories(); render(); $('#results-title').focus({ preventScroll: true }); $('#annuaire').scrollIntoView({ block: 'start' });
}));
$('#load-more').addEventListener('click', () => {
  const old = results.children.length; limit += pageSize; render(); (results.children[old]?.querySelector('a') || $('#person-results a'))?.focus({ preventScroll: true });
});
toggle.addEventListener('click', () => {
  const open = toggle.getAttribute('aria-expanded') !== 'true';
  toggle.setAttribute('aria-expanded', String(open)); categoryList.classList.toggle('open', open); toggle.lastElementChild.textContent = open ? '−' : '+';
});
document.addEventListener('keydown', e => {
  if (e.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') { closeCategories(); toggle.focus(); }
  if (e.key === '/' && !['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName) && !document.activeElement.isContentEditable) { e.preventDefault(); input.focus(); }
});
function selectCategory(key, type = '') {
  const legacy = { 'boutiques-ma': 'boutiques', 'banques-affaires': 'banques' };
  active = legacy[key] ? 'conseil-ma' : categories.some(c => c.id === key) ? key : '';
  maType = active === 'conseil-ma' ? (legacy[key] || (['boutiques', 'banques'].includes(type) ? type : '')) : '';
}
function renderMaFilters() {
  const box = $('#ma-filters');
  box.hidden = !['conseil-ma', 'secondaire'].includes(active);
  box.replaceChildren();
  if (box.hidden) return;
  if (active === 'secondaire') {
    const controls = el('div', 'ma-types');
    controls.setAttribute('role', 'group'); controls.setAttribute('aria-label', 'Rôle sur le marché secondaire');
    [['', 'Tous'], ['acces', 'Accès et structuration'], ['investisseurs', 'Fonds et investisseurs'], ['plateformes', 'Revente et données']].forEach(([key, label]) => {
      const count = houses.filter(h => h.categories.includes('secondaire') && (!key || h.secondaryRole === key)).length;
      const button = el('button', 'ma-type', `${label} · ${number.format(count)}`);
      button.type = 'button'; button.setAttribute('aria-pressed', String(secondaryRole === key));
      button.addEventListener('click', () => { secondaryRole = key; limit = pageSize; render(); });
      controls.append(button);
    });
    const link = el('a', '', 'Secondaire de fonds et private equity');
    link.href = '/annuaire?metier=secondaire-fonds#annuaire';
    box.append(controls, link, el('p', 'ma-help', 'Late stage ne signifie pas IPO programmée. Les conditions d’accès et de revente dépendent de chaque offre.'));
    return;
  }
  const group = houses.filter(h => h.categories.includes('conseil-ma'));
  const choices = [['', 'Tous'], ['boutiques', 'Boutiques'], ['banques', 'Banques d’affaires']];
  const controls = el('div', 'ma-types');
  controls.setAttribute('role', 'group'); controls.setAttribute('aria-label', 'Type de conseil M&A');
  choices.forEach(([key, label]) => {
    const count = group.filter(h => !key || h.maTypes.includes(key)).length;
    const button = el('button', 'ma-type', `${label} · ${number.format(count)}`);
    button.type = 'button'; button.dataset.maType = key;
    button.setAttribute('aria-pressed', String(maType === key));
    button.addEventListener('click', () => {
      maType = key; limit = pageSize; render();
      Array.from(box.querySelectorAll('button')).find(b => b.dataset.maType === key)?.focus({preventScroll:true});
    });
    controls.append(button);
  });
  box.append(controls, el('p', 'ma-help', 'Certaines sociétés figurent dans les deux catégories. Chaque société apparaît une seule fois dans « Tous ».'));
}
async function init() {
  try {
    const response = await fetch('/assets/ecosysteme/maison/data.json?v=20261024-fundora');
    if (!response.ok) throw new Error('Data unavailable');
    const data = await response.json();
    const group = data.categoryGroups.find(c => c.id === 'conseil-ma');
    categories = [group, ...data.categories.filter(c => !group.categoryIds.includes(c.id))];
    const categoryNames = Object.fromEntries([...data.categories, ...categories].map(c => [c.id, c.name]));
    houses = data.houses.sort((a,b) => a.name.localeCompare(b.name, 'fr', { sensitivity: 'base', ignorePunctuation: true })).map(h => ({ ...h, maTypes: [h.categories.includes('boutiques-ma') ? 'boutiques' : '', h.categories.includes('banques-affaires') ? 'banques' : ''].filter(Boolean), categories: [...h.categories.filter(c => !group.categoryIds.includes(c)), ...(h.categories.some(c => group.categoryIds.includes(c)) ? ['conseil-ma'] : [])], search: normalize(h.name + ' ' + h.categories.map(c => categoryNames[c] + ' ' + labels[c]).join(' ') + ' ' + (h.keywords || []).join(' ') + ' ' + (h.logoAttribution || '')) }));
    const params = new URLSearchParams(location.search);
    input.value = params.get('q') || '';
    secondaryRole = ['acces', 'investisseurs', 'plateformes'].includes(params.get('role')) ? params.get('role') : '';
    const requested = params.get('metier') || location.hash.slice(1);
    selectCategory(requested, params.get('type'));
    if (['ligues','ligue-cgp','actualites','argent','vie'].includes(location.hash.slice(1))) { location.replace('/ecosysteme-ligues' + location.hash); return; }
    const totalCount = $('#total-count');
    if (totalCount) totalCount.textContent = number.format(houses.length);
    renderCategories(); render();
  } catch (error) {
    $('#results-count').textContent = 'Chargement indisponible';
    const p = el('p', '', 'L’annuaire n’a pas pu être chargé. ');
    const a = el('a', 'text-link', 'Consulter l’annuaire public ↗'); a.href = 'https://www.exit.club/annuaire';
    p.append(a); results.replaceChildren(p); $('#load-more').hidden = true;
  }
}
init();

window.addEventListener('hashchange', () => { const key = location.hash.slice(1); if (categories.some(c => c.id === key) || ['banques-affaires', 'boutiques-ma'].includes(key)) { selectCategory(key); limit = pageSize; render(); document.querySelector('#annuaire').scrollIntoView({block:'start'}); } else if (['ligues','ligue-cgp','actualites','argent','vie'].includes(key)) { location.assign('/ecosysteme-ligues' + location.hash); } });

window.addEventListener('popstate', () => {
  const params = new URLSearchParams(location.search);
  secondaryRole = ['acces', 'investisseurs', 'plateformes'].includes(params.get('role')) ? params.get('role') : '';
  input.value = params.get('q') || '';
  selectCategory(params.get('metier') || location.hash.slice(1), params.get('type'));
  limit = pageSize; render();
});

