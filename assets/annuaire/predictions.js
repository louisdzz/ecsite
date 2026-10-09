(() => {
  'use strict';
  const block=document.querySelector('#polymarket');if(!block)return;
  const allowed=new Set(['will-gamestop-acquire-ebay','ipos-before-2027','next-french-presidential-election']);
  fetch('/api/predictions',{credentials:'omit',signal:AbortSignal.timeout(10000)}).then(r=>{if(!r.ok)throw new Error('Unavailable');return r.json();}).then(data=>{
    const time=Date.parse(data.fetchedAt);
    if(!Number.isFinite(time)||Date.now()-time>86400000||time>Date.now()+300000||!Array.isArray(data.items))throw new Error('Expired');
    let count=0;
    for(const item of data.items){
      if(!allowed.has(item.slug)||!Number.isFinite(item.probability)||item.probability<0||item.probability>100)continue;
      const card=[...block.querySelectorAll('.pm-item')].find(a=>new URL(a.href).pathname.endsWith('/'+item.slug));if(!card)continue;
      card.querySelector('.pm-price').dataset.probability='true';
      card.querySelector('.pm-price').textContent=item.probability.toLocaleString('fr-FR',{maximumFractionDigits:1})+' %';
      if(item.slug==='next-french-presidential-election' && typeof item.outcome==='string') card.querySelector('.pm-copy small').textContent=item.outcome+' · favori du marché';
      count++;
    }
    if(count)block.querySelector('.pm-update').textContent='Relevé du '+new Intl.DateTimeFormat('fr-FR',{timeZone:'Europe/Paris',day:'2-digit',month:'2-digit',hour:'2-digit',minute:'2-digit'}).format(new Date(time))+' · probabilités de marché'+(count<3?' · certains chiffres indisponibles':'')+'.';
  }).catch(()=>{});
})();
