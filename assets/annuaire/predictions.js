(() => {
  'use strict';
  const block = document.querySelector('#polymarket');
  if (!block) return;
  const status = block.querySelector('.pm-update');
  const cards = [...block.querySelectorAll('.pm-item')].map(card => ({
    slug: new URL(card.href).pathname.split('/').pop(),
    price: card.querySelector('.pm-price'),
    label: card.querySelector('.pm-copy small')
  }));
  const dateFormat = new Intl.DateTimeFormat('fr-FR', {
    timeZone: 'Europe/Paris', day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit'
  });
  let pending = false;
  let lastReading = '';

  async function refresh() {
    if (document.hidden || pending) return;
    pending = true;
    try {
      const response = await fetch('/api/predictions', {credentials: 'omit', signal: AbortSignal.timeout(10000)});
      if (!response.ok) throw new Error('Unavailable');
      const data = await response.json();
      const time = Date.parse(data.fetchedAt);
      if (data.source !== 'Polymarket CLOB' || !Number.isFinite(time) || Math.abs(Date.now() - time) > 120000 || !Array.isArray(data.items)) {
        throw new Error('Expired');
      }
      let count = 0;
      for (const {slug, price, label} of cards) {
        const item = data.items.find(item => item.slug === slug && Number.isFinite(item.probability) &&
          item.probability >= 0 && item.probability <= 100);
        if (!item) {
          delete price.dataset.probability;
          price.textContent = 'Indisponible';
          continue;
        }
        price.dataset.probability = 'true';
        price.textContent = item.probability.toLocaleString('fr-FR', {maximumFractionDigits: 1}) + ' %';
        if (slug === 'next-french-presidential-election' && typeof item.outcome === 'string') {
          label.textContent = item.outcome + ' · favori du marché';
        }
        count++;
      }
      if (!count) throw new Error('No quotes');
      lastReading = 'Dernier relevé le ' + dateFormat.format(time) + ' (Paris)';
      status.textContent = lastReading + ' · carnet d’ordres' +
        (count < cards.length ? ' · certains chiffres indisponibles' : '') + '.';
    } catch (_) {
      status.textContent = lastReading
        ? lastReading + ' · actualisation indisponible.'
        : 'Carnet d’ordres temporairement indisponible.';
    } finally {
      pending = false;
    }
  }

  document.addEventListener('visibilitychange', refresh);
  setInterval(refresh, 60000);
  refresh();
})();
