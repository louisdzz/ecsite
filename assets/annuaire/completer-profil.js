/* Public fiche context only. No respondent identity, email or CRM data in URLs. */
(function () {
  'use strict';
  if (window.ExitProfileForm) return;
  const trades = {'conseil-ma':'M&A','banques-affaires':'M&A','boutiques-ma':'M&A',avocats:'Autre',cgp:'Banque privée, CGP et MFO',mfo:'Banque privée, CGP et MFO','banques-privees':'Banque privée, CGP et MFO','fonds-dette':'Dette et financement',secondaire:'Secondaire sur sociétés','secondaire-fonds':'Secondaire sur fonds','fonds-pe':'Private equity et venture capital','fonds-vc':'Private equity et venture capital','immobilier-patrimonial':'Immobilier et infrastructures',jets:'Aviation d’affaires'};
  const professions = {bankers:'M&A',banker:'M&A',lawyers:'Avocats M&A',lawyer:'Avocats M&A',tax:'Fiscalité de la cession',debt:'Dette et financement',wealth:'Banque privée, CGP et MFO'};
  const fields = ['company','site','trade','services','clients','situation','geography','approach','reference','profile','person','conditions'];
  const clean = value => String(value || '').replace(/\s+/g,' ').trim().slice(0,800);
  function urlFor(context, preview) {
    const c = Object.assign({}, context);
    c.trade = c.trade || professions[c.profession] || trades[c.category] || 'Autre';
    const url = new URL(preview ? '/completer-profil-apercu.html' : 'https://tally.so/r/ArzLOe', location.href);
    url.searchParams.set('ec_mode','Présenter ma société / mon expertise');
    for (const key of fields) {
      const value = clean(c[key]);
      if (value) url.searchParams.set('ec_' + key,value);
    }
    return url.href;
  }
  window.ExitProfileForm = {urlFor};
  function houseContext() {
    const profile = document.querySelector('.pv-main[data-category]');
    const main = document.querySelector('main');
    if (!main) return null;
    const name = (profile || main).querySelector('h1')?.textContent;
    if (!name) return null;
    const canonical = document.querySelector('link[rel="canonical"]')?.href;
    const source = Array.from(document.querySelectorAll('a[href]')).find(a => /site officiel|site de la maison/i.test(a.textContent) && /^https?:/.test(a.getAttribute('href')));
    if (!canonical || !/^\/f\//.test(new URL(canonical).pathname)) return null;
    const category = profile?.dataset.category || document.querySelector('script[data-profile-category]')?.dataset.profileCategory;
    const c = {company:name,category,profile:canonical,site:source?.href};
    const lead = profile?.querySelector('.pv-hero h2')?.textContent || main.querySelector('.lead')?.textContent || profile?.querySelector('.pv-lead')?.textContent || '';
    if (!/non renseign|à compléter|repères du métier/i.test(lead)) c.services=lead;
    if (canonical && new URL(canonical).pathname === '/f/ibc-aviation') Object.assign(c,{
      site:'https://www.ibc-aviation.com/',
      services:'Courtier en aviation privée : affrètement de jets, conseil en management et acquisition.',
      situation:'Vol ponctuel, déplacements réguliers ou projet d’acquisition d’un appareil.',
      reference:'https://www.ibc-aviation.com/la-societe.html',
      conditions:'Sur demande et devis. Décomposition du prix et rémunération du courtier à préciser.'
    });
    return c;
  }
  const context=houseContext();
  if (!context) return;
  const main=document.querySelector('main');
  let actions=document.querySelector('.pv-main .pv-actions');
  if (!actions) {actions=document.createElement('p');actions.className='profile-complete-actions';(main.querySelector('.lead') || main.querySelector('h1')).after(actions);}
  let link=main.querySelector('[data-complete-profile]') || Array.from(main.querySelectorAll('a[href]')).find(a=>a.href.startsWith('https://tally.so/') && /compléter mon profil/i.test(a.textContent));
  if (!link) {link=document.createElement('a');link.className='pv-secondary';link.dataset.completeProfile='';actions.append(link);}
  if (actions.classList.contains('profile-complete-actions')) link.style.cssText='display:inline-block;padding:12px 20px;border:1px solid #bbc9b8;border-radius:28px;color:#193c32;text-decoration:none';
  link.textContent='Compléter mon profil ↗';
  link.href=urlFor(context,location.hostname==='127.0.0.1'||location.hostname==='localhost');
  link.target='_blank';link.rel='noopener';
  if (actions.classList.contains('profile-complete-actions') && link.parentElement !== actions) actions.remove();
})();
