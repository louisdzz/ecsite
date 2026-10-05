(() => {
  'use strict';
  const panels = [...document.querySelectorAll('[data-panel]')];
  const nav = [...document.querySelectorAll('[data-view]')];
  const ids = new Set(panels.map(p => p.dataset.panel));
  const journalAnchors = new Set(['polymarket', 'regards', 'fil-actualites', 'personnes']);
  const status = document.querySelector('#media-status');
  const yieldBlock = document.querySelector('[data-yield-observed-at]');
  if (yieldBlock) {
    const age = Date.now() - Date.parse(yieldBlock.dataset.yieldObservedAt);
    if (!Number.isFinite(age) || age < 0 || age > 86400000) yieldBlock.querySelector('.yield-stale').hidden = false;
  }
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
  document.addEventListener('submit', event => {
    if (event.target.matches('.search-form')) {show('annuaire');history.replaceState(null,'',location.pathname+location.search+'#annuaire');}
  }, true);
  document.addEventListener('click', event => {
    if (event.target.closest('.example')) show('annuaire',true);
  }, true);
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
