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
      predictionBlock.querySelector('#prediction-title').textContent = 'Polymarket · archive';
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
  const quoteIds = {gold:'GC=F',oil:'BZ=F',nasdaq:'^NDX',sp500:'^GSPC',eurusd:'EURUSD=X'};
  const quoteTime = new Intl.DateTimeFormat('fr-FR',{timeZone:'Europe/Paris',day:'2-digit',month:'2-digit',hour:'2-digit',minute:'2-digit'});
  function applyQuotes(payload) {
    if (!Array.isArray(payload.quotes)) throw new Error('Invalid quotes');
    let count = 0;
    for (const q of payload.quotes) {
      if (quoteIds[q.id] !== q.symbol || ![q.price,q.previousClose,q.changePercent].every(Number.isFinite) || q.price <= 0 || q.previousClose <= 0) continue;
      const time = Date.parse(q.quotedAt);
      if (!Number.isFinite(time) || time > Date.now()+300000 || Date.now()-time > 14*86400000) continue;
      const delta = (q.price / q.previousClose - 1)*100;
      if (Math.abs(delta-q.changePercent) > 0.01) continue;
      const digits = q.id === 'eurusd' ? 4 : 2;
      document.querySelectorAll('[data-market="'+q.id+'"]').forEach(card => {
        if (time < Date.parse(card.dataset.quotedAt)) return;
        card.dataset.quotedAt = q.quotedAt;
        card.querySelector('.mq-price').textContent = q.price.toLocaleString('fr-FR',{minimumFractionDigits:digits,maximumFractionDigits:digits});
        const change=card.querySelector('.mq-change');
        change.textContent=(delta>=0?'+':'')+delta.toLocaleString('fr-FR',{minimumFractionDigits:2,maximumFractionDigits:2})+' %';
        change.classList.toggle('up',delta>=0); change.classList.toggle('down',delta<0);
        const stamp=card.querySelector('.mq-time'); stamp.dateTime=q.quotedAt; stamp.textContent=quoteTime.format(new Date(time));
      });
      count++;
    }
    return count;
  }
  function flagOldQuotes() {
    document.querySelectorAll('[data-market]').forEach(card => {
      if(Date.now()-Date.parse(card.dataset.quotedAt)>4*86400000){
        const stamp=card.querySelector('.mq-time');
        if(!stamp.textContent.startsWith('Ancien')) stamp.textContent='Ancien relevé · '+stamp.textContent;
      }
    });
  }
  let refreshing=false;
  async function refreshQuotes() {
    if(document.hidden || refreshing) return;
    refreshing=true;
    const note=document.querySelector('#quotes-status');
    try {
      const response=await fetch('/api/marches',{signal:AbortSignal.timeout(10000)});
      if(!response.ok) throw new Error('Quotes unavailable');
      const count=applyQuotes(await response.json());
      note.textContent=count===5?'':'Certains cours restent au dernier relevé indiqué.';
    } catch (_) { note.textContent='Dernier relevé conservé. Horaires indiqués sur chaque cours.'; }
    finally { refreshing=false;flagOldQuotes(); }
  }
  flagOldQuotes(); refreshQuotes();
  setInterval(refreshQuotes,300000);
  document.addEventListener('visibilitychange',()=>{if(!document.hidden) refreshQuotes();});
})();
