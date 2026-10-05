'use strict';
(() => {
  const form = document.querySelector('#news-filters');
  const normalize = s => s.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  if (form) {
    form.hidden = false;
    const cards = [...document.querySelectorAll('[data-news]')];
    const fields = ['q','theme','type','maison'];
    const aliases = { theme:'theme', type:'kind', maison:'house' };
    const count = document.querySelector('#news-count');
    const empty = document.querySelector('#news-empty');
    const clear = document.querySelector('#news-clear');
    function restore() {
      const params = new URLSearchParams(location.search);
      fields.forEach(name => { form.elements[name].value = params.get(name) || ''; });
    }
    function render(updateUrl) {
      const q = normalize(form.elements.q.value.trim());
      let shown = 0;
      for (const card of cards) {
        const match = (!q || normalize(card.dataset.search).includes(q)) && Object.entries(aliases).every(([key,attr]) => !form.elements[key].value || card.dataset[attr] === form.elements[key].value);
        card.hidden = !match;
        if (match) shown++;
      }
      count.textContent = `${shown} actualité${shown === 1 ? '' : 's'}`;
      empty.hidden = shown !== 0;
      clear.hidden = cards.length === 0;
      empty.querySelector('h2').textContent = cards.length ? 'Aucune actualité ne correspond.' : 'Aucune actualité pour le moment.';
      empty.querySelector('p').textContent = cards.length ? 'Essayez un autre nom ou élargissez les filtres.' : 'Les prochaines nouvelles apparaîtront ici après vérification.';
      if (updateUrl) {
        const params = new URLSearchParams();
        fields.forEach(name => { const value = form.elements[name].value.trim(); if (value) params.set(name,value); });
        history.replaceState(null,'',location.pathname+(params.size ? '?'+params : ''));
      }
    }
    restore(); render(false);
    form.addEventListener('input', () => render(true));
    form.addEventListener('change', () => render(true));
    form.addEventListener('submit', e => { e.preventDefault(); render(true); });
    form.addEventListener('reset', () => setTimeout(() => render(true),0));
    clear.addEventListener('click', () => { form.reset(); form.elements.q.focus(); });
    window.addEventListener('popstate', () => { restore(); render(false); });
  }
  const submit = document.querySelector('#news-submit');
  if (submit) {
    function embargo() {
      const needed = submit.elements.availability.value === 'embargo';
      document.querySelector('#embargo-field').hidden = !needed;
      submit.elements.embargo.required = needed;
      document.querySelector('#news-mail-ready').hidden = true;
    }
    submit.elements.availability.addEventListener('change',embargo);
    submit.addEventListener('input', () => { document.querySelector('#news-mail-ready').hidden = true; });
    embargo();
    submit.addEventListener('submit', e => {
      e.preventDefault();
      if (!submit.reportValidity()) return;
      const f = submit.elements;
      const timing = f.availability.value === 'public' ? 'Information déjà publique' : f.availability.value === 'embargo' ? `Sous embargo jusqu’au ${f.embargo.value.replace('T',' à ')}, heure de Paris. Ne pas publier avant confirmation écrite.` : 'À discuter avant toute publication';
      const text = `Bonjour Louis,\n\nMaison : ${f.house.value.trim()}\nAnnonce : ${f.title.value.trim()}\n\n${f.facts.value.trim()}\n\nSource : ${f.source.value.trim() || 'Document à joindre'}\nPublication : ${timing}\n\nPrécisions : ${f.notes.value.trim() || 'Aucune'}\n\nMerci de me recontacter pour convenir de la présentation.`;
      document.querySelector('#news-mail-text').value = text;
      document.querySelector('#news-mail-link').href = 'mailto:louis@exit.club?subject='+encodeURIComponent('Actualité Annuaire : '+f.house.value.trim())+'&body='+encodeURIComponent(text);
      const ready = document.querySelector('#news-mail-ready');
      ready.hidden = false;
      ready.scrollIntoView({block:'nearest',behavior:matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth'});
    });
  }
})();

// Les articles actuels et futurs utilisent la même mesure publique, avec refus du suivi.
(() => {
  if (!document.querySelector('script[src^="/assets/annuaire-mesure.js"]')) {
    const script = document.createElement('script');
    script.src = '/assets/annuaire-mesure.js?v=20261005';
    script.defer = true;
    document.head.appendChild(script);
  }
})();
