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

/* Notes des exiters : encart flouté sur les fiches du secondaire et du pré-IPO.
   Les notes vivent dans l'espace membres (app.exit.club/notes). Rien de réel n'est
   affiché ici : le contenu flouté est décoratif. */
(function () {
  var ACTEURS = ['maresquier-partners','upscalers','clifton-partners','fish','hiive','forge-global','equityzen','caplight','nasdaq-private-market','zanbato','mvp-manhattan-venture-partners','g-squared','industry-ventures','isomer-capital','giano-capital','ltv-long-term-value-partners','rift-capital','tempocap'];
  var m = location.pathname.match(/^\/f\/([a-z0-9-]+?)(?:\.html)?\/?$/);
  if (!m || ACTEURS.indexOf(m[1]) < 0) return;
  var slug = m[1];
  function go() {
    if (document.getElementById('notes-exiters')) return;
    var h1 = document.querySelector('.pv-identity h1, h1');
    var nom = h1 ? h1.textContent.trim() : '';
    var css = document.createElement('style');
    css.textContent = '#notes-exiters{margin:28px 0;border-radius:18px;background:#17382f;color:#f7f3e4;padding:26px 26px 24px;display:grid;grid-template-columns:minmax(0,1.1fr) minmax(0,1fr);gap:26px;align-items:center;overflow:hidden}'
      + '#notes-exiters .ne-k{font-size:11.5px;letter-spacing:.22em;text-transform:uppercase;color:#d8b46a;font-weight:600;margin:0 0 10px}'
      + '#notes-exiters h2{font-family:Fraunces,Georgia,serif;font-weight:300;font-size:27px;line-height:1.12;margin:0 0 10px;color:#f7f3e4}'
      + '#notes-exiters p{font-size:14.5px;line-height:1.6;color:rgba(247,243,228,.82);margin:0}'
      + '#notes-exiters .ne-cta{display:flex;flex-wrap:wrap;gap:10px;margin-top:18px}'
      + '#notes-exiters .ne-cta a{display:inline-block;border-radius:999px;padding:10px 18px;font-size:13.5px;font-weight:600;text-decoration:none}'
      + '#notes-exiters .ne-1{background:#d8b46a;color:#17382f}#notes-exiters .ne-2{border:1px solid rgba(247,243,228,.4);color:#f7f3e4}'
      + '#notes-exiters .ne-flou{position:relative;background:rgba(247,243,228,.07);border:1px solid rgba(247,243,228,.15);border-radius:14px;padding:18px 20px}'
      + '#notes-exiters .ne-flou .ne-in{filter:blur(5px);user-select:none;pointer-events:none}'
      + '#notes-exiters .ne-big{font-family:Fraunces,Georgia,serif;font-size:38px;line-height:1}#notes-exiters .ne-big small{font-size:16px;opacity:.7}'
      + '#notes-exiters .ne-row{display:flex;align-items:center;gap:10px;margin-top:9px;font-size:12.5px}#notes-exiters .ne-row span:first-child{width:120px;flex:none}'
      + '#notes-exiters .ne-bar{height:7px;border-radius:9px;background:#d8b46a}'
      + '#notes-exiters .ne-lock{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:600;color:#f7f3e4;text-align:center;padding:12px}'
      + '#notes-exiters .ne-lock span{background:rgba(23,56,47,.88);border-radius:999px;padding:8px 14px}'
      + '@media (max-width:720px){#notes-exiters{grid-template-columns:1fr;padding:22px 18px}#notes-exiters h2{font-size:23px}}';
    document.head.appendChild(css);
    var rows = [['Frais d’entrée',62],['Carry',44],['Spread',78],['Délai',35]].map(function (r) {
      return '<div class="ne-row"><span>' + r[0] + '</span><span class="ne-bar" style="width:' + r[1] + '%"></span></div>';
    }).join('');
    var box = document.createElement('section');
    box.id = 'notes-exiters';
    box.setAttribute('aria-labelledby', 'notes-exiters-titre');
    var app = 'https://app.exit.club';
    box.innerHTML = '<div><p class="ne-k">Notes des exiters</p><h2 id="notes-exiters-titre">Ce que les membres ont vraiment payé chez ' + nom.replace(/</g, '&lt;') + '.</h2>'
      + '<p>Prix par action, frais réels, couches de SPV, délais, sorties. Notes anonymes des membres de l’Exit Club, réservées au club. Aucun acteur ne peut payer pour les modifier.</p>'
      + '<div class="ne-cta"><a class="ne-1" href="' + app + '/notes/noter?acteur=' + slug + '">J’ai investi avec eux : noter</a><a class="ne-2" href="' + app + '/notes">Lire les notes</a></div></div>'
      + '<div class="ne-flou" aria-hidden="true"><div class="ne-in"><div class="ne-big">4,1 <small>/ 5</small></div>' + rows + '</div><div class="ne-lock"><span>Réservé aux membres</span></div></div>';
    var hero = document.getElementById('pv-offre') || document.querySelector('main section');
    if (hero && hero.parentNode) hero.parentNode.insertBefore(box, hero.nextSibling);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', go); else go();
})();
