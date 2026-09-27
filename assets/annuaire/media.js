(() => {
  'use strict';
  const panels = [...document.querySelectorAll('[data-panel]')];
  const nav = [...document.querySelectorAll('[data-view]')];
  const ids = new Set(panels.map(p => p.dataset.panel));
  const journalAnchors = new Set(['polymarket', 'regards']);
  const status = document.querySelector('#media-status');
  // A cached edition never acquires a fresh timestamp just because it is opened.
  const predictionBlock = document.querySelector('[data-observed-at]');
  if (predictionBlock) {
    const age = Date.now() - Date.parse(predictionBlock.dataset.observedAt);
    if (!Number.isFinite(age) || age < 0 || age > 86400000) {
      predictionBlock.querySelector('.prediction-stale').hidden = false;
      predictionBlock.querySelector('#prediction-title').textContent = 'Les anticipations, dernier relevé.';
    }
  }
  const key = 'exit-media-edition-reading-v1';
  const yieldBlock = document.querySelector('[data-yield-observed-at]');
  if (yieldBlock) {
    const age = Date.now() - Date.parse(yieldBlock.dataset.yieldObservedAt);
    if (!Number.isFinite(age) || age < 0 || age > 86400000) yieldBlock.querySelector('.yield-stale').hidden = false;
  }
  let saved = new Set();
  let stories = [];
  try { const v = JSON.parse(localStorage.getItem(key) || '[]'); if (Array.isArray(v)) saved = new Set(v.filter(x => typeof x === 'string').slice(0,100)); } catch (_) {}
  function show(view, focus = false) {
    if (!ids.has(view)) view = 'journal';
    panels.forEach(p => p.hidden = p.dataset.panel !== view);
    document.querySelectorAll('[data-directory-part]').forEach(p => p.hidden = view !== 'annuaire');
    nav.forEach(a => { if (a.dataset.view === view) a.setAttribute('aria-current','page'); else a.removeAttribute('aria-current'); });
    if (focus) {
      const dest = view === 'annuaire' ? document.querySelector('.search-section') : document.getElementById(view);
      dest?.scrollIntoView({block:'start',behavior:'auto'});
    }
  }
  function fromUrl() {
    const hash = location.hash.slice(1);
    const params = new URLSearchParams(location.search);
    if (journalAnchors.has(hash)) { show('journal'); requestAnimationFrame(()=>document.getElementById(hash)?.scrollIntoView({block:'start'})); return; }
    show(ids.has(hash) ? hash : params.has('metier') || params.has('q') || (hash && hash!=='methode') ? 'annuaire' : 'journal');
  }
  document.addEventListener('click', event => {
    const a = event.target.closest('a[href^="#"]');
    if (a && a.hash==='#recherche') {
      event.preventDefault(); show('annuaire',true); document.querySelector('#recherche').focus(); return;
    }
    if (a && journalAnchors.has(a.hash.slice(1))) {
      event.preventDefault(); show('journal'); history.pushState(null,'',location.pathname+location.search+a.hash); document.getElementById(a.hash.slice(1))?.scrollIntoView({block:'start'}); return;
    }
    if (a && ids.has(a.hash.slice(1))) {
      event.preventDefault();
      const hash = a.hash;
      history.pushState(null,'',location.pathname + location.search + hash);
      show(hash.slice(1),true);
    }
  });
  window.addEventListener('popstate',fromUrl);
  window.addEventListener('hashchange',fromUrl);
  document.addEventListener('keydown', event => {
    if (event.key==='/' && !/INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName) && !document.activeElement.isContentEditable) {
      event.preventDefault(); show('annuaire',true); document.querySelector('#recherche').focus();
    }
  },true);
  fromUrl();
  document.querySelectorAll('[data-editorial-filter]').forEach(button => button.addEventListener('click', () => {
    const phase = button.dataset.editorialFilter;
    document.querySelectorAll('[data-editorial-filter]').forEach(b => b.setAttribute('aria-pressed', String(b === button)));
    let visible = 0;
    document.querySelectorAll('[data-editorial-phase]').forEach(card => {
      card.hidden = phase !== 'all' && card.dataset.editorialPhase !== phase;
      if (!card.hidden) visible++;
    });
    document.querySelector('#ec-status').textContent = visible + ' lecture' + (visible === 1 ? '' : 's') + ' affichée' + (visible === 1 ? '' : 's') + '.';
  }));
  function updateSaved() {
    document.querySelector('#saved-count').textContent = String(saved.size);
    document.querySelectorAll('[data-save]').forEach(b => {
      const yes = saved.has(b.dataset.save);
      b.setAttribute('aria-pressed',String(yes)); b.textContent = yes ? '✓ Enregistré' : '＋ À garder';
    });
    const list = document.querySelector('#reading-list'); list.replaceChildren();
    const matches = stories.filter(s => saved.has(s.id));
    document.querySelector('#reading-empty').hidden = matches.length>0;
    for (const s of matches) {
      const article = document.createElement('article'); article.className='media-card';
      const meta = document.createElement('p'); meta.className='media-tag'; meta.textContent=s.category+' · '+s.date;
      const title = document.createElement('h3'); const link = document.createElement('a'); link.href=s.url; link.textContent=s.title; title.append(link);
      const remove = document.createElement('button'); remove.type='button'; remove.className='save-story'; remove.dataset.remove=s.id; remove.textContent='Retirer de ma sélection';
      article.append(meta,title,remove); list.append(article);
    }
  }
  document.addEventListener('click', event => {
    const b = event.target.closest('[data-save],[data-remove]'); if(!b) return;
    const id = b.dataset.save || b.dataset.remove;
    if (saved.has(id)) saved.delete(id); else saved.add(id);
    try { localStorage.setItem(key,JSON.stringify([...saved])); status.textContent = saved.has(id) ? 'Article enregistré.' : 'Article retiré.'; }
    catch (_) { status.textContent='Sélection conservée pour cette visite uniquement.'; }
    updateSaved();
  });
  updateSaved();
  fetch('/assets/annuaire/reading.json').then(r => {if(!r.ok) throw new Error('reading');return r.json();}).then(rows => { stories = rows.filter(s => s.url.startsWith('/actualites/') || s.url.startsWith('https://x.com/')); const valid=new Set(stories.map(s=>s.id));saved=new Set([...saved].filter(id=>valid.has(id)));updateSaved(); }).catch(()=>{document.querySelector('#reading-empty').textContent='Les articles enregistrés ne peuvent pas être chargés. Réessayez en rechargeant la page.';});
  document.querySelector('#load-markets').addEventListener('click', () => {
    const box=document.querySelector('#tradingview'); box.hidden=false;
    document.querySelector('#market-placeholder').hidden=true;
    const s=document.createElement('script');
    s.src='https://s3.tradingview.com/external-embedding/embed-widget-tickers.js';s.async=true;
    s.textContent=JSON.stringify({symbols:[{proName:'COMEX:GC1!',title:'Or (futures)'},{proName:'ICEEUR:BRN1!',title:'Brent (futures)'},{proName:'NASDAQ:NDX',title:'Nasdaq 100'},{proName:'SP:SPX',title:'S&P 500'},{proName:'FX_IDC:EURUSD',title:'EUR / USD'}],isTransparent:true,colorTheme:'light',locale:'fr'});
    s.onerror=()=>{document.querySelector('#market-status').textContent='Le module ne se charge pas. Consultez les cours directement sur TradingView.';};
    document.querySelector('#market-status').textContent='Source : TradingView. Si un instrument est indisponible, consultez le site source.';
    box.querySelector('.tradingview-widget-container').append(s);
  },{once:true});
})();
