/* Site public : choix de confidentialité, accessibilité et validation. */
(function () {
  'use strict';
  if (window.exitSite) return;
  var consentKey = 'exit-consent-v1';
  var optOutKey = 'exit-annuaire-mesure-desactivee';
  var lifetime = 180 * 86400000;
  var memory = null;
  function blocked() { return navigator.doNotTrack === '1' || navigator.globalPrivacyControl === true; }
  function read() {
    try {
      var value = memory || JSON.parse(localStorage.getItem(consentKey) || 'null');
      return value && value.version === 1 && typeof value.analytics === 'boolean' && value.at > Date.now() - lifetime && value.at <= Date.now() ? value : null;
    } catch (_) { return memory; }
  }
  function allows() { var value = read(); return !!value && value.analytics && !blocked(); }
  function choose(analytics) {
    memory = { version: 1, analytics: !!analytics && !blocked(), at: Date.now() };
    try { localStorage.setItem(consentKey, JSON.stringify(memory)); } catch (_) { /* Choix valable pour la page courante. */ }
    banner.hidden = true;
    document.dispatchEvent(new CustomEvent('exit:consent', { detail: { analytics: allows() } }));
  }
  window.exitSite = { allowsAnalytics: allows, openPreferences: function () { banner.hidden = false; banner.querySelector('button').focus(); } };
  var banner = document.createElement('section');
  banner.className = 'ec-consent'; banner.hidden = true;
  banner.setAttribute('aria-label', 'Préférences de confidentialité');
  banner.innerHTML = '<div><strong>Votre confidentialité</strong><p>Avec votre accord, nous mesurons la fréquentation du site avec Vercel Analytics, sans cookie publicitaire. Vous pouvez refuser et continuer à consulter le site.</p><a href="/confidentialite">Politique de confidentialité</a></div><div class="ec-consent-actions"><button type="button" data-choice="no">Refuser</button><button type="button" data-choice="yes">Accepter la mesure d’audience</button></div>';
  document.body.appendChild(banner);
  banner.querySelector('[data-choice=no]').addEventListener('click', function () { choose(false); });
  banner.querySelector('[data-choice=yes]').addEventListener('click', function () { choose(true); });
  document.querySelectorAll('[data-cookie-preferences]').forEach(function (button) {
    button.addEventListener('click', window.exitSite.openPreferences);
  });
  try {
    if (!read() && localStorage.getItem(optOutKey) === '1') choose(false);
  } catch (_) { /* Pas de stockage accessible. */ }
  if (blocked() && !read()) choose(false);
  banner.hidden = !!read();
  window.addEventListener('storage', function (e) {
    if (e.key !== consentKey) return;
    memory = null; banner.hidden = !!read();
    document.dispatchEvent(new CustomEvent('exit:consent', { detail: { analytics: allows() } }));
  });
  document.addEventListener('error', function (e) { var img=e.target; if(img && img.tagName==='IMG' && /\/assets\/logos\//.test(img.src)) { img.src='/assets/site/logo-placeholder.svg'; } }, true);
  // Ne jamais laisser un formulaire invalide atteindre son gestionnaire d’envoi.
  document.querySelectorAll('form').forEach(function (form) {
    if (form.getAttribute('role') === 'search') return;
    var status = document.createElement('p');
    status.className = 'ec-form-status'; status.setAttribute('role', 'alert'); status.hidden = true;
    form.prepend(status);
    form.querySelectorAll('#msg,#err').forEach(function(el){ el.setAttribute('role','alert'); el.setAttribute('aria-live','polite'); });
    var note = document.createElement('p'); note.className = 'ec-form-privacy';
    note.innerHTML = 'Vos données servent à traiter cette demande. <a href="/confidentialite#formulaires">En savoir plus</a>.';
    form.appendChild(note);
    form.querySelectorAll('input,textarea,select').forEach(function (field, index) {
      if (field.name === 'site') { field.setAttribute('aria-hidden','true'); field.tabIndex = -1; return; }
      if (!field.id) field.id = 'ec-field-' + (form.id || 'form') + '-' + index;
      var label = field.closest('label') || field.previousElementSibling;
      if (label && label.tagName === 'LABEL') label.htmlFor = field.id;
      if (field.tagName === 'TEXTAREA' && field.maxLength <= 0) field.maxLength = ['presentation','equipe','opportunite','actualite'].includes(field.name) ? 1900 : 4000;
      if (field.tagName === 'INPUT' && ['text','email','url','tel'].includes(field.type) && !field.hasAttribute('maxlength')) field.maxLength = field.type === 'url' ? 400 : field.type === 'tel' ? 40 : field.name === 'agrements' ? 500 : ['institution','nom','contact'].includes(field.name) ? 120 : 150;
      field.addEventListener('input', function () { field.setCustomValidity(''); field.removeAttribute('aria-invalid'); status.hidden = true; });
    });
    form.addEventListener('submit', function (e) {
      var problem = ''; var invalid = null; var totalBytes = 0;
      form.querySelectorAll('input,textarea,select').forEach(function (field) {
        if (field.name === 'site') { if (field.value) problem = 'La demande n’a pas pu être envoyée.'; return; }
        field.setCustomValidity('');
        if (field.required && ['text','email','url','tel','textarea'].includes(field.type) && !field.value.trim()) field.setCustomValidity('Merci de remplir ce champ.');
        if (field.type === 'url' && field.value && !/^https?:\/\//i.test(field.value)) field.setCustomValidity('Indiquez une adresse commençant par https:// ou http://.');
        if (field.files) Array.from(field.files).forEach(function (file) {
          totalBytes += file.size;
          var image = /\.(png|jpe?g|webp|avif)$/i.test(file.name);
          var pdf = /\.pdf$/i.test(file.name);
          if (!(field.name === 'deck' ? image || pdf : image)) field.setCustomValidity('Formats acceptés : PNG, JPG, WebP, AVIF ou PDF pour un document.');
        });
        if (!field.checkValidity() && !invalid) { invalid = field; field.setAttribute('aria-invalid','true'); }
      });
      if (totalBytes > 3 * 1024 * 1024) problem = 'Les fichiers doivent peser moins de 3 Mo au total. Réduisez leur taille ou transmettez-les par email.';
      if (problem || invalid) {
        e.preventDefault(); e.stopImmediatePropagation();
        status.textContent = problem || invalid.validationMessage; status.hidden = false;
        if (invalid) { invalid.focus(); invalid.reportValidity(); }
      }
    }, true);
  });
})();
