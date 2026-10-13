/* Consultations publiques, après consentement. Pas d’événement commercial individuel. */
(function () {
  'use strict';
  var recordedPath = '';
  function permitted() { return !!window.exitSite && window.exitSite.allowsAnalytics(); }
  function load() {
    if (!['www.exit.club','exit.club'].includes(location.hostname) || !permitted() || window.exitAnnuaireAnalyticsLoaded) return;
    window.exitAnnuaireAnalyticsLoaded = true;
    window.va = window.va || function () { (window.vaq = window.vaq || []).push(arguments); };
    window.va('beforeSend', function (event) {
      if (event.type !== 'pageview' || !permitted()) return null;
      try {
        var url = new URL(event.url, location.origin);
        if (!['www.exit.club','exit.club'].includes(url.hostname)) return null;
        var path = url.pathname.replace(/\.html$/, '').replace(/\/$/, '');
        if (!path || path === '/index') path = '/';
        if (path === '/ecosysteme') path = '/annuaire';
        if (!['/','/annuaire','/actualites','/tresorerie'].includes(path) && !/^\/(f|actualites)\/[a-z0-9-]+$/.test(path)) return null;
        if (recordedPath === path) return null;
        recordedPath = path;
        // Ne pas transmettre paramètres, fragments, recherche, noms ou emails.
        return { ...event, url: 'https://www.exit.club' + path };
      } catch (_) { return null; }
    });
    var script = document.createElement('script');
    script.defer = true; script.src = '/_vercel/insights/script.js';
    document.head.appendChild(script);
  }
  document.addEventListener('exit:consent', load);
  document.addEventListener('DOMContentLoaded', load);
  load();
})();
