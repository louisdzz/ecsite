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
      const outcomes = array(m.outcomes);
      const tokens = array(m.clobTokenIds);
      const yes = outcomes.findIndex(outcome => /^yes$/i.test(outcome));
      const token = tokens[yes];
      if (outcomes.length !== 2 || tokens.length !== 2 || !/^\d+$/.test(token) || typeof token !== 'string') return [];
      return [{token, condition: m.conditionId, name: m.groupItemTitle || 'Oui'}];
    } catch (_) {
      return [];
    }
  });
  if (!markets.length || (!config.leader && markets.length !== 1)) throw new Error('Ambiguous market');
  return markets;
}

function quote(book, market) {
  if (!book || book.market !== market.condition || !Array.isArray(book.bids) || !Array.isArray(book.asks)) return null;
  const validPrices = levels => levels.map(level => Number(level.price)).filter(price => price > 0 && price < 1);
  const bid = Math.max(...validPrices(book.bids));
  const ask = Math.min(...validPrices(book.asks));
  if (!Number.isFinite(bid) || !Number.isFinite(ask) || bid > ask) return null;
  return {bid, ask, probability: (bid + ask) * 50, outcome: market.name};
}
async function handler(req,res) {
  res.setHeader('X-Content-Type-Options','nosniff');
  if(req.method!=='GET'){res.setHeader('Allow','GET');return res.status(405).json({error:'Method not allowed'});}
  const signal = AbortSignal.timeout(8500);
  const results = await Promise.allSettled(SELECTION.map(async config => {
    const response = await fetch('https://gamma-api.polymarket.com/events/slug/' + config.slug, {signal});
    if (!response.ok) throw new Error('Upstream unavailable');
    return {config, markets: parseEvent(await response.json(), config)};
  }));
  const selections = results.filter(result => result.status === 'fulfilled').map(result => result.value);
  let items = [];
  try {
    const tokens = [...new Set(selections.flatMap(({markets}) => markets.map(market => market.token)))];
    if (!tokens.length) throw new Error('No active markets');
    const response = await fetch('https://clob.polymarket.com/books', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(tokens.map(token_id => ({token_id}))),
      signal
    });
    if (!response.ok) throw new Error('Order books unavailable');
    const books = new Map((await response.json()).map(book => [book.asset_id, book]));
    items = selections.flatMap(({config, markets}) => {
      const quotes = markets.map(market => quote(books.get(market.token), market)).filter(Boolean);
      const best = quotes.sort((a, b) => b.probability - a.probability)[0];
      return best ? [{...best, slug: config.slug, title: config.title, label: config.label,
        url: 'https://polymarket.com/event/' + config.slug}] : [];
    });
  } catch (_) {
    // Missing order books leave the affected prices unavailable.
  }
  res.setHeader('Cache-Control', items.length ? 'public, max-age=0, s-maxage=30' : 'no-store');
  return res.status(items.length ? 200 : 503).json({source: 'Polymarket CLOB', fetchedAt: new Date().toISOString(), items});
}
module.exports = handler;
