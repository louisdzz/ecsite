/* Comparaison de produits, à partir des relevés publics déjà utilisés sur /tresorerie. */
(() => {
  'use strict';
  const root = document.getElementById('treso-comparison');
  if (!root) return;
  const state = { category: '', query: '', slugs: null, family: '', companies: false };
  let products = null;
  let request = null;
  let ui = null;
  const labels = { deposit: 'Dépôts bancaires', fund: 'Fonds monétaires', digital: 'Actifs numériques', mixed: 'Supports mixtes' };
  const fmt = new Intl.DateTimeFormat('fr-FR', { timeZone: 'Europe/Paris', day: '2-digit', month: '2-digit', year: 'numeric' });
  const normalize = s => String(s || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  function node(tag, cls, text) {
    const n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text !== undefined) n.textContent = text;
    return n;
  }
  function link(text, href, external = false) {
    const a = node('a', '', text);
    a.href = href;
    if (external) { a.target = '_blank'; a.rel = 'noopener noreferrer'; }
    return a;
  }
  function family(p) {
    if (['qonto', 'trade-republic'].includes(p.slug)) return 'mixed';
    if (/mon[eé]taire/i.test(p.nature)) return 'fund';
    if (/num[eé]rique|stablecoin/i.test(p.nature)) return 'digital';
    return 'deposit';
  }
  function date(value) {
    const t = Date.parse(value);
    return Number.isFinite(t) ? fmt.format(t) : 'Date non renseignée';
  }
  function old(value) {
    const t = Date.parse(value);
    return !Number.isFinite(t) || t > Date.now() || Date.now() - t > 7 * 86400000;
  }
  function rateKind(p) {
    const basis = normalize(p.taux_type);
    if (/objectif/.test(basis)) return 'Objectif';
    if (/apy/.test(basis)) return 'APY affiché';
    if (/compte a terme/.test(normalize(p.nature))) return 'Taux fixe';
    if (/30 jours|31 jours/.test(basis)) return 'Rendement observé';
    return 'Taux publié';
  }
  function source(p) {
    try { const u = new URL(p.source); return u.protocol === 'https:' ? u.href : null; } catch { return null; }
  }
  function mount() {
    root.replaceChildren();
    const heading = node('div', 'tc-heading');
    const intro = node('div');
    const h = node('h3', '', 'Comparer les solutions'); h.id = 'treso-compare-title';
    intro.append(h, node('p', 'tc-intro', 'Taux, frais, disponibilité : voyez ce qui change d’un produit à l’autre.'));
    const count = node('span', 'tc-total');
    heading.append(intro, count);
    const controls = node('div', 'tc-controls');
    const filters = node('div', 'tc-families'); filters.setAttribute('role', 'group'); filters.setAttribute('aria-label', 'Famille de solutions');
    const buttons = [];
    for (const [key, label] of [['', 'Toutes'], ...Object.entries(labels)]) {
      const b = node('button', 'tc-filter', label); b.type = 'button'; b.dataset.family = key;
      b.addEventListener('click', () => { state.family = key; paint(); });
      filters.append(b); buttons.push(b);
    }
    const companyLabel = node('label', 'tc-company');
    const companies = document.createElement('input'); companies.type = 'checkbox';
    companies.addEventListener('change', () => { state.companies = companies.checked; paint(); });
    companyLabel.append(companies, node('span', '', 'Accessibles aux sociétés'));
    controls.append(filters, companyLabel);
    const note = node('p', 'tc-note', 'Un taux fixe, un rendement observé et un objectif ne sont pas équivalents. Les protections et les délais de retrait diffèrent.');
    const status = node('p', 'tc-status'); status.setAttribute('role', 'status'); status.setAttribute('aria-live', 'polite');
    const scroll = node('div', 'tc-scroll'); scroll.tabIndex = 0; scroll.setAttribute('role', 'region'); scroll.setAttribute('aria-label', 'Tableau comparatif, défilement horizontal possible');
    const table = node('table', 'tc-table');
    const caption = node('caption', 'visually-hidden', 'Comparatif daté des produits de trésorerie, par ordre alphabétique de maison.');
    const head = node('thead'); const row = node('tr');
    for (const title of ['Solution et support', 'Taux et base du relevé', 'Disponibilité', 'Frais et accès', 'Capital et risques']) {
      const th = node('th', '', title); th.scope = 'col'; row.append(th);
    }
    head.append(row);
    const tbody = node('tbody'); table.append(caption, head, tbody); scroll.append(table);
    const empty = node('p', 'tc-empty', 'Aucun produit documenté ne correspond à ces filtres.'); empty.hidden = true;
    const foot = node('div', 'tc-footer');
    foot.append(node('p', '', 'Relevés datés, avant fiscalité. « À actualiser » signale un taux relevé il y a plus de sept jours. La date du taux ne revalide pas toutes les conditions.'), link('Voir le tableau détaillé', '/tresorerie'));
    root.append(heading, controls, note, status, scroll, empty, foot);
    ui = { count, buttons, companies, status, tbody, scroll, empty };
  }
  function cell(label, cls) {
    const td = node('td', cls); td.dataset.label = label; return td;
  }
  function productRow(p) {
    const tr = node('tr'); tr.dataset.product = p.key;
    const f = family(p);
    const main = cell('Solution', 'tc-product');
    const brand = node('div', 'tc-brand');
    if (p.logo && p.logo.startsWith('/assets/')) {
      const img = document.createElement('img'); img.src = p.logo; img.alt = ''; img.loading = 'lazy'; img.width = 58; img.height = 30;
      img.addEventListener('error', () => img.remove(), { once: true }); brand.append(img);
    }
    brand.append(link(p.maison, '/f/' + encodeURIComponent(p.slug)));
    main.append(brand, node('strong', 'tc-product-name', p.produit), node('span', 'tc-family tc-family-' + f, labels[f]));
    const rate = cell('Taux et base', 'tc-rate');
    rate.append(node('span', 'tc-rate-kind', rateKind(p)), node('strong', 'tc-rate-value', p.taux || 'Non renseigné'), node('p', 'tc-basis', p.taux_type || 'Base à préciser'));
    const dt = node('div', 'tc-date');
    const time = node('time', '', 'Relevé du ' + date(p.taux_date)); if (p.taux_date) time.dateTime = p.taux_date;
    dt.append(time); if (old(p.taux_date)) dt.append(node('span', 'tc-stale', 'À actualiser')); rate.append(dt);
    const src = source(p); if (src) rate.append(link('Source du relevé ↗', src, true));
    const availability = cell('Disponibilité', 'tc-availability');
    availability.append(node('span', 'tc-term', p.dispo_code === 'bloque' ? 'Durée de blocage' : 'Sans durée de blocage'), node('p', '', p.dispo || 'À préciser'));
    const access = cell('Frais et accès', 'tc-access');
    access.append(node('p', '', p.frais || 'Frais à préciser'), node('p', 'tc-ticket', p.ticket || 'Ticket à préciser'));
    if (p.plafond) access.append(node('p', 'tc-cap', p.plafond));
    access.append(node('span', 'tc-eligibility', p.personne_morale === 'oui' ? 'Sociétés : oui au relevé' : p.personne_morale === 'non' ? 'Particuliers uniquement au relevé' : 'Accès sociétés à confirmer'));
    const risk = cell('Capital et risques', 'tc-risk');
    risk.append(node('p', '', p.protection || 'Protection à préciser'));
    const details = node('details', 'tc-details'); details.append(node('summary', '', 'Comprendre le support'), node('p', '', p.nature_detail || p.nature || 'À préciser'));
    risk.append(details);
    tr.append(main, rate, availability, access, risk); return tr;
  }
  function paint() {
    root.hidden = state.category !== 'treso';
    if (root.hidden || !products) return;
    if (!ui) mount();
    // La recherche est celle de l’annuaire : ne pas réinterpréter ses résultats.
    const scoped = products.filter(p => !state.slugs || state.slugs.has(p.slug));
    const list = scoped.filter(p => (!state.family || family(p) === state.family) && (!state.companies || p.personne_morale === 'oui'));
    const houses = new Set(scoped.map(p => p.slug));
    ui.count.textContent = scoped.length + ' produit' + (scoped.length > 1 ? 's' : '') + ' · ' + houses.size + ' maison' + (houses.size > 1 ? 's' : '');
    ui.buttons.forEach(b => {
      b.setAttribute('aria-pressed', String(b.dataset.family === state.family));
      b.hidden = false;
    });
    ui.companies.checked = state.companies;
    ui.status.textContent = list.length + ' produit' + (list.length > 1 ? 's' : '') + ' affiché' + (list.length > 1 ? 's' : '') + ' · ordre alphabétique, sans classement de rendement';
    ui.tbody.replaceChildren(...list.map(productRow));
    ui.scroll.hidden = !list.length; ui.empty.hidden = Boolean(list.length);
  }
  function load() {
    if (!request) {
      root.replaceChildren(node('p', 'tc-loading', 'Chargement du comparatif…'));
      request = fetch('/tresorerie.json', { cache: 'no-cache', credentials: 'omit' })
        .then(r => { if (!r.ok) throw Error('unavailable'); return r.json(); })
        .then(data => {
          if (!Array.isArray(data.produits)) throw Error('invalid products');
          products = data.produits.filter(p => p && typeof p.slug === 'string' && typeof p.produit === 'string').map((p, i) => ({ ...p, key: p.slug + ':' + i + ':' + p.produit }));
          products.sort((a, b) => a.maison.localeCompare(b.maison, 'fr') || a.produit.localeCompare(b.produit, 'fr'));
          paint();
        }).catch(() => {
          root.replaceChildren(node('h3', '', 'Comparatif indisponible'), node('p', '', 'Les données n’ont pas pu être chargées.'), link('Consulter les relevés détaillés', '/tresorerie'));
          ui = null;
        });
    }
  }
  document.addEventListener('annuaire:results', event => {
    state.category = event.detail.category;
    state.query = event.detail.query || '';
    state.slugs = new Set(event.detail.slugs || []);
    root.hidden = state.category !== 'treso';
    if (!root.hidden) { load(); paint(); }
  });
  const initial = new URLSearchParams(location.search);
  state.category = initial.get('metier') || '';
  state.query = initial.get('q') || '';
  if (state.category === 'treso') { root.hidden = false; load(); }
})();
