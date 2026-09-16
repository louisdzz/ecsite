/* Mesure des consultations uniquement. Aucun événement commercial personnalisé. */
(function () {
  'use strict';
  const key = 'exit-annuaire-mesure-desactivee';
  const privacyPath = '/statistiques-confidentialite';
  const isPrivacyPage = location.pathname.replace(/\.html$/, '') === privacyPath;
  const isDirectory = /^\/(annuaire|ecosysteme)(\.html)?\/?$/.test(location.pathname);
  const isProfile = /^\/f\/[a-z0-9-]+(?:\.html)?$/.test(location.pathname);
  function optedOut() {
    try { return localStorage.getItem(key) === '1'; } catch (_) { return false; }
  }
  function browserOptOut() {
    return navigator.doNotTrack === '1' || window.doNotTrack === '1' || navigator.globalPrivacyControl === true;
  }
  if (isPrivacyPage) {
    const status = document.getElementById('mesure-status');
    const stop = document.getElementById('mesure-stop');
    const allow = document.getElementById('mesure-allow');
    function render() {
      status.textContent = browserOptOut() ? 'La mesure est désactivée par le réglage de votre navigateur.' :
        optedOut() ? 'La mesure est désactivée sur ce navigateur.' : 'La mesure des consultations est activée sur ce navigateur.';
      stop.hidden = optedOut() || browserOptOut();
      allow.hidden = !optedOut() || browserOptOut();
    }
    function choose(disabled) {
      try {
        if (disabled) localStorage.setItem(key, '1'); else localStorage.removeItem(key);
        render();
      } catch (_) { status.textContent = 'Votre navigateur ne permet pas d’enregistrer ce choix. Vous pouvez activer son option de refus du suivi.'; }
    }
    stop.addEventListener('click', () => choose(true));
    allow.addEventListener('click', () => choose(false));
    render();
    return;
  }
  if (!isDirectory && !isProfile) return;
  if (!document.querySelector('[data-annuaire-privacy]')) {
    const footer = document.createElement('div');
    footer.setAttribute('data-annuaire-privacy', '');
    footer.style.cssText = 'padding:20px 16px;text-align:center;font:12px/1.5 system-ui,sans-serif;color:#666;';
    const link = document.createElement('a');
    link.href = privacyPath;
    link.textContent = 'Mesure d’audience et confidentialité';
    link.style.color = 'inherit';
    footer.appendChild(link);
    document.body.appendChild(footer);
  }
  // Ne pas mélanger les aperçus, les miroirs Vercel ou le développement avec l’audience publique.
  if (!['www.exit.club', 'exit.club'].includes(location.hostname) || optedOut() || browserOptOut()) return;
  if (window.exitAnnuaireAnalyticsLoaded) return;
  window.exitAnnuaireAnalyticsLoaded = true;
  window.va = window.va || function () { (window.vaq = window.vaq || []).push(arguments); };
  let recordedPath = '';
  window.va('beforeSend', function (event) {
    if (event.type !== 'pageview' || optedOut() || browserOptOut()) return null;
    try {
      const url = new URL(event.url, location.origin);
      if (!['www.exit.club', 'exit.club'].includes(url.hostname)) return null;
      let path = url.pathname.replace(/\.html$/, '').replace(/\/$/, '');
      if (path === '/ecosysteme') path = '/annuaire';
      if (path !== '/annuaire' && !/^\/f\/[a-z0-9-]+$/.test(path)) return null;
      if (recordedPath === path) return null;
      recordedPath = path;
      // Les mots saisis, paramètres d’URL et fragments ne sont jamais transmis.
      return { ...event, url: 'https://www.exit.club' + path };
    } catch (_) { return null; }
  });
  const script = document.createElement('script');
  script.defer = true;
  script.src = '/_vercel/insights/script.js';
  document.head.appendChild(script);
})();
