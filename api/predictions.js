'use strict';
// Editorial selection only. No caller-provided URL, no account, no trading.
const SELECTION = [
  {slug:'will-gamestop-acquire-ebay',title:'GameStop rachètera-t-il eBay ?',label:'M&A'},
  {slug:'ipos-before-2027',group:'Anthropic',title:'Anthropic entrera-t-il en Bourse avant 2027 ?',label:'IPO'},
  {slug:'next-french-presidential-election',title:'Qui gagnera la présidentielle française ?',label:'FR',leader:true}
];
function array(value) {return Array.isArray(value)?value:JSON.parse(value);}
function parseEvent(event, config, now=Date.now()) {
  if(event.slug!==config.slug || event.closed===true || event.active!==true || !Array.isArray(event.markets)) throw new Error('Unavailable event');
  const markets=event.markets.filter(m=>m.closed===false && m.active===true && m.acceptingOrders===true && (!m.endDate || Date.parse(m.endDate)>now) && (!config.group || m.groupItemTitle===config.group)).flatMap(m=>{
    try {
      const outcomes=array(m.outcomes),prices=array(m.outcomePrices).map(Number);
      const yes=outcomes.findIndex(x=>/^yes$/i.test(x));
      if(outcomes.length!==prices.length || yes<0 || prices.some(p=>!Number.isFinite(p)||p<0||p>1)) return [];
      return [{probability:prices[yes]*100,name:m.groupItemTitle||'Oui',question:m.question}];
    } catch(_){return [];}
  });
  if(!markets.length || (!config.leader && !config.group && markets.length!==1)) throw new Error('Ambiguous market');
  const market=config.leader?markets.sort((a,b)=>b.probability-a.probability)[0]:markets[0];
  return {slug:config.slug,title:config.title,label:config.label,probability:market.probability,outcome:market.name,url:'https://polymarket.com/event/'+config.slug};
}
async function handler(req,res) {
  res.setHeader('X-Content-Type-Options','nosniff');
  if(req.method!=='GET'){res.setHeader('Allow','GET');return res.status(405).json({error:'Method not allowed'});}
  const results=await Promise.allSettled(SELECTION.map(async config=>{
    const response=await fetch('https://gamma-api.polymarket.com/events/slug/'+config.slug,{signal:AbortSignal.timeout(8000)});
    if(!response.ok)throw new Error('Upstream unavailable');
    return parseEvent(await response.json(),config);
  }));
  const items=results.filter(r=>r.status==='fulfilled').map(r=>r.value);
  res.setHeader('Cache-Control',items.length?'public, max-age=60, s-maxage=3600':'no-store');
  return res.status(items.length?200:503).json({source:'Polymarket Gamma API',fetchedAt:new Date().toISOString(),items});
}
module.exports=handler;
module.exports.parseEvent=parseEvent;
