/* Small enhancement; the full category list is available if scripts are blocked. */
(() => {
  'use strict';
  const toolbar = document.querySelector('.toolbar');
  const menu = toolbar && toolbar.querySelector('.jump');
  if (!menu) return;
  menu.id = 'ecosysteme-categories';
  const toggle = document.createElement('button');
  toggle.type = 'button';
  toggle.className = 'ec-category-toggle';
  toggle.textContent = 'Explorer les ' + menu.querySelectorAll('a').length + ' catégories';
  toggle.setAttribute('aria-controls',menu.id);
  function setOpen(open) {
    menu.hidden = !open;
    toggle.setAttribute('aria-expanded',String(open));
  }
  setOpen(false);
  menu.before(toggle);
  toggle.addEventListener('click',() => setOpen(menu.hidden));
  menu.addEventListener('click',e => {
    const link = e.target.closest('a');
    if (!link) return;
    const target = document.getElementById(link.hash.slice(1));
    setOpen(false);
    if (target) {
      target.setAttribute('tabindex','-1');
      target.focus({preventScroll:true});
    }
  });
  toolbar.addEventListener('keydown',e => {
    if (e.key === 'Escape' && !menu.hidden) {
      e.preventDefault();setOpen(false);toggle.focus();
    }
  });
  const query = document.getElementById('q');
  if (query) {
    query.setAttribute('aria-label','Rechercher une institution');
    query.placeholder = 'Rechercher une institution…';
    query.addEventListener('input',() => {if(query.value.trim())setOpen(false);});
  }
  document.querySelectorAll('.wall__f a').forEach(link => {
    if (!link.textContent.includes('catégories')) return;
    link.href = '#' + menu.id;
    link.addEventListener('click',e => {e.preventDefault();setOpen(true);toggle.focus();toggle.scrollIntoView({block:'start'});});
  });
  // Each wide ranking scrolls horizontally on its own; its heading stays readable.
  document.querySelectorAll('.league table,.league-t table,#ligue-cgp table').forEach(table => {
    const wrap = document.createElement('div');
    wrap.className = 'table-scroll';
    wrap.setAttribute('role','region');wrap.setAttribute('tabindex','0');
    const heading = table.closest('.league-t')?.querySelector('h2') || table.closest('.league')?.querySelector('h2');
    wrap.setAttribute('aria-label',(heading?.textContent || 'Classement') + ' — tableau défilant');
    table.before(wrap);wrap.append(table);
  });
})();
