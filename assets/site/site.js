/* Site public : choix de confidentialité, accessibilité et validation. */
(function () {
  'use strict';
  if (window.exitSite) return;
  var consentKey = 'exit-consent-v2';
  var optOutKey = 'exit-annuaire-mesure-desactivee';
  var lifetime = 180 * 86400000;
  var memory = null;
  function blocked() { return navigator.doNotTrack === '1' || navigator.globalPrivacyControl === true; }
  function read() {
    try {
      var match=document.cookie.split('; ').find(function(c){return c.startsWith(consentKey+'=');});
      var value = match ? JSON.parse(decodeURIComponent(match.slice(consentKey.length+1))) : memory || JSON.parse(localStorage.getItem(consentKey) || localStorage.getItem('exit-consent-v1') || 'null');
      if(value && value.version===1)value={version:2,analytics:value.analytics,affiliation:false,at:value.at};
      return value && value.version === 2 && typeof value.analytics === 'boolean' && value.at > Date.now() - lifetime && value.at <= Date.now() ? value : null;
    } catch (_) { return null; }
  }
  function allows() { var value = read(); return !!value && value.analytics && !blocked(); }
  function allowsAffiliation() { var value=read();return !!value && value.affiliation===true && !blocked(); }
  function clearReferral() { ['', '; Domain=exit.club','; Domain=.exit.club'].forEach(function(domain){document.cookie='promotekit_referral=; Max-Age=0; Path=/; SameSite=Lax'+domain;}); }
  function choose(analytics, affiliation) {
    var reload=(!affiliation || blocked()) && !!document.querySelector('script[data-promotekit]');
    memory = { version: 2, analytics: !!analytics && !blocked(), affiliation: !!affiliation && !blocked(), at: Date.now() };
    try { localStorage.setItem(consentKey, JSON.stringify(memory)); } catch (_) { /* Choix valable pour la page courante. */ }
    var domain=['www.exit.club','exit.club','app.exit.club'].includes(location.hostname)?'; Domain=exit.club':'';
    document.cookie=consentKey+'='+encodeURIComponent(JSON.stringify(memory))+'; Max-Age=15552000; Path=/; SameSite=Lax'+(location.protocol==='https:'?'; Secure':'')+domain;
    if(!memory.affiliation)clearReferral();
    banner.hidden = true;
    document.dispatchEvent(new CustomEvent('exit:consent', { detail: { analytics: allows(), affiliation: allowsAffiliation() } }));
    if(reload)location.reload();
  }
  window.exitSite = { allowsAnalytics: allows, allowsAffiliation:allowsAffiliation, openPreferences: function () { var c=read();banner.querySelector('[data-purpose=analytics]').checked=!!c&&c.analytics;banner.querySelector('[data-purpose=affiliation]').checked=!!c&&c.affiliation===true;banner.hidden = false; banner.querySelector('button').focus(); } };
  var banner = document.createElement('section');
  banner.className = 'ec-consent'; banner.hidden = true;
  banner.setAttribute('aria-label', 'Préférences de confidentialité');
  banner.innerHTML = '<div><strong>Votre confidentialité</strong><p>Deux services facultatifs : la mesure d’audience avec Vercel et le suivi des parrainages avec PromoteKit. Vous pouvez refuser ou choisir les services autorisés.</p><a href="/confidentialite">Politique de confidentialité</a><details class="ec-consent-options"><summary>Personnaliser</summary><label><input type="checkbox" data-purpose="analytics"> Mesure d’audience (Vercel)</label><label><input type="checkbox" data-purpose="affiliation"> Suivi des parrainages (PromoteKit)</label><button type="button" data-choice="save">Enregistrer mes choix</button></details></div><div class="ec-consent-actions"><button type="button" data-choice="no">Tout refuser</button><button type="button" data-choice="yes">Tout accepter</button></div>';
  document.body.appendChild(banner);
  banner.querySelector('[data-choice=no]').addEventListener('click', function () { choose(false,false); });
  banner.querySelector('[data-choice=yes]').addEventListener('click', function () { choose(true,true); });
  banner.querySelector('[data-choice=save]').addEventListener('click',function(){choose(banner.querySelector('[data-purpose=analytics]').checked,banner.querySelector('[data-purpose=affiliation]').checked);});
  var existing=read();if(existing){banner.querySelector('[data-purpose=analytics]').checked=existing.analytics;banner.querySelector('[data-purpose=affiliation]').checked=existing.affiliation===true;}
  document.querySelectorAll('[data-cookie-preferences]').forEach(function (button) {
    button.addEventListener('click', window.exitSite.openPreferences);
  });
  try {
    if (!read() && localStorage.getItem(optOutKey) === '1') choose(false);
  } catch (_) { /* Pas de stockage accessible. */ }
  if (blocked() && !read()) choose(false);
  if(!allowsAffiliation())clearReferral();
  banner.hidden = !!read();
  window.addEventListener('focus',function(){if(!allowsAffiliation()){clearReferral();if(document.querySelector('script[data-promotekit]'))location.reload();}});
  window.addEventListener('storage', function (e) {
    if (e.key !== consentKey) return;
    memory = null; banner.hidden = !!read();
    if(!allowsAffiliation()){clearReferral();if(document.querySelector('script[data-promotekit]'))location.reload();}
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
