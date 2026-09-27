'use strict';
// Fixed public instruments only: no caller-provided upstream URL or symbol.
const INSTRUMENTS = [
  ['gold', 'GC=F'], ['oil', 'BZ=F'], ['nasdaq', '^NDX'],
  ['sp500', '^GSPC'], ['eurusd', 'EURUSD=X']
];
function parseQuote(id, symbol, payload, now = Date.now()) {
  const m = payload?.chart?.result?.[0]?.meta;
  if (!m || m.symbol !== symbol || m.currency !== 'USD') throw new Error('Unexpected instrument');
  const price = m.regularMarketPrice, previous = m.previousClose, at = m.regularMarketTime;
  if (![price, previous, at].every(Number.isFinite) || price <= 0 || previous <= 0 || at < 1e9 || at * 1000 > now + 300000 || now - at * 1000 > 14 * 86400000) throw new Error('Invalid or expired quote');
  return { id, symbol, price, previousClose: previous, changePercent: (price / previous - 1) * 100, quotedAt: new Date(at * 1000).toISOString(), currency: m.currency };
}
async function handler(req, res) {
  if (req.method !== 'GET' && req.method !== 'HEAD') {
    res.setHeader('Allow', 'GET, HEAD'); return res.status(405).json({ error: 'Method not allowed' });
  }
  const results = await Promise.allSettled(INSTRUMENTS.map(async ([id, symbol]) => {
    const url = 'https://query1.finance.yahoo.com/v8/finance/chart/' + encodeURIComponent(symbol) + '?interval=5m&range=1d';
    const response = await fetch(url, { signal: AbortSignal.timeout(8000), headers: { 'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json' } });
    if (!response.ok) throw new Error('Upstream unavailable');
    return parseQuote(id, symbol, await response.json());
  }));
  const quotes = results.filter(r => r.status === 'fulfilled').map(r => r.value);
  res.setHeader('Cache-Control', quotes.length ? 'public, max-age=60, s-maxage=300, stale-while-revalidate=60' : 'no-store');
  res.setHeader('X-Content-Type-Options', 'nosniff');
  return res.status(quotes.length ? 200 : 503).json({ source: 'Yahoo Finance', fetchedAt: new Date().toISOString(), quotes, unavailable: INSTRUMENTS.filter(([id]) => !quotes.some(q => q.id === id)).map(([id]) => id) });
}
module.exports = handler;
module.exports.parseQuote = parseQuote;
