/* Une offre commerciale, sans certification de fiabilité ni effet sur le rang. */
(() => {
  const badges = [...document.querySelectorAll('.ec-verifie-status')];
  const positionTooltip = wrapper => {
    const tooltip = wrapper.querySelector('.ec-verifie-tooltip');
    const bounds = wrapper.getBoundingClientRect();
    const width = tooltip.getBoundingClientRect().width;
    const left = Math.max(16, Math.min(bounds.right - width, innerWidth - width - 16));
    tooltip.style.right = 'auto';
    tooltip.style.left = (left - bounds.left) + 'px';
  };
  const setOpen = (wrapper, open) => {
    wrapper.classList.toggle('is-open', open);
    wrapper.querySelector('button').setAttribute('aria-expanded', String(open));
    if (open) positionTooltip(wrapper);
  };
  badges.forEach(wrapper => {
    const button = wrapper.querySelector('button');
    wrapper.addEventListener('mouseenter', () => setOpen(wrapper, true));
    wrapper.addEventListener('mouseleave', () => {
      if (!wrapper.contains(document.activeElement)) setOpen(wrapper, false);
    });
    wrapper.addEventListener('focusin', () => setOpen(wrapper, true));
    wrapper.addEventListener('focusout', event => {
      if (!wrapper.contains(event.relatedTarget)) setOpen(wrapper, false);
    });
    button.addEventListener('click', () => setOpen(wrapper, true));
    button.addEventListener('keydown', event => {
      if (event.key === 'Escape') { setOpen(wrapper, false); event.stopPropagation(); }
    });
  });
  document.addEventListener('click', event => badges.forEach(wrapper => {
    if (!wrapper.contains(event.target)) setOpen(wrapper, false);
  }));
  window.addEventListener('resize', () => badges.forEach(wrapper => {
    if (wrapper.classList.contains('is-open')) positionTooltip(wrapper);
  }));
})();
