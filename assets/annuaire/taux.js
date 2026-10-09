(() => {
  'use strict';
  const cards = [...document.querySelectorAll('[data-yield-provider]')];
  if (!cards.length) return;
  const dateFormat = new Intl.DateTimeFormat('fr-FR', {timeZone:'Europe/Paris'});
  const warning = document.querySelector('.yield-stale');
  const percent = n => new Intl.NumberFormat('fr-FR',{minimumFractionDigits:2,maximumFractionDigits:2}).format(n);
  function warn() {
    if (warning) warning.hidden = !cards.some(c => {const t=Date.parse(c.dataset.yieldDate); return !Number.isFinite(t) || t>Date.now() || Date.now()-t>7*86400000;});
  }
  function update(card, value, date) {
    const t=Date.parse(date);
    if (!Number.isFinite(value) || value<0 || value>100 || !Number.isFinite(t) || t>Date.now()+300000 || t<Date.parse(card.dataset.yieldDate)) return;
    const figure=card.querySelector('.yield-figure>strong');
    figure.replaceChildren(document.createTextNode(percent(value)));
    const suffix=document.createElement('span');suffix.textContent=' %';figure.append(suffix);
    card.dataset.yieldDate=date;
    card.querySelector('.yield-date').textContent='Relevé le '+dateFormat.format(t);
    warn();
  }
  async function refresh() {
    try {
      const res=await fetch('/tresorerie.json',{cache:'no-cache',credentials:'omit',signal:AbortSignal.timeout(8000)});
      if (!res.ok) throw Error('Source unavailable');
      const data=await res.json();
      for (const card of cards) {
        const key=card.dataset.yieldProvider;
        const product=data.produits?.find(p=>p.slug===key && (key!=='spiko'||p.produit==='Spiko Euro') && (key!=='cashbee'||p.produit.includes('Wormser')));
        // Fixed provider cards retain their stated basis; refresh only the documented Spiko observation here.
        if (key==='spiko' && product) update(card,Number(product.taux_num),product.taux_date);
      }
    } catch (_) { warn(); }
    try {
      const res=await fetch('https://public-api.spiko.io/v0/share-classes/eurSAFO/yield',{credentials:'omit',signal:AbortSignal.timeout(8000)});
      if (!res.ok) throw Error('Yield unavailable');
      const data=await res.json();
      if (typeof data.monthlyYield!=='string') return;
      update(cards.find(c=>c.dataset.yieldProvider==='spiko'),Number(data.monthlyYield)*100,data.updatedAt);
    } catch (_) { warn(); }
  }
  warn();refresh();
  setInterval(()=>{if(!document.hidden)refresh();},300000);
})();
