/* Static replacement for the few Odoo website behaviours the exported pages use:
   reveal animations, scrolled header, mobile offcanvas menu and the showreel player. */
(() => {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Odoo animations (.o_animate start hidden; .o_animate_on_scroll waits for the viewport).
  const show = el => {
    el.classList.add('o_nv_visible');
    if (reduce) return;
    el.classList.add('o_animating');
    el.addEventListener('animationend', () => {
      el.classList.remove('o_animating');
      el.classList.add('o_animated');
    }, { once: true });
  };
  const animated = document.querySelectorAll('.o_animate');
  const onScroll = [...animated].filter(el => el.classList.contains('o_animate_on_scroll'));
  animated.forEach(el => { if (!onScroll.includes(el)) show(el); });
  if (onScroll.length) {
    if (!('IntersectionObserver' in window)) onScroll.forEach(show);
    else {
      const io = new IntersectionObserver(entries => entries.forEach(e => {
        if (e.isIntersecting) { show(e.target); io.unobserve(e.target); }
      }), { rootMargin: '0px 0px -10% 0px' });
      onScroll.forEach(el => io.observe(el));
    }
  }

  // Header shadow once the page scrolls.
  const header = document.getElementById('top');
  if (header) {
    const update = () => header.classList.toggle('o_header_is_scrolled', scrollY > 8);
    update();
    addEventListener('scroll', update, { passive: true });
  }

  // Mobile menu (Bootstrap offcanvas markup, without Bootstrap's JS).
  document.querySelectorAll('[data-bs-toggle="offcanvas"]').forEach(button => {
    const panel = document.querySelector(button.dataset.bsTarget);
    if (!panel) return;
    let backdrop = null;
    const close = () => {
      panel.classList.remove('show');
      button.setAttribute('aria-expanded', 'false');
      backdrop?.remove();
      backdrop = null;
      document.removeEventListener('keydown', onKey);
      button.focus();
    };
    const onKey = e => { if (e.key === 'Escape') close(); };
    button.addEventListener('click', () => {
      panel.classList.add('show');
      panel.setAttribute('role', 'dialog');
      panel.setAttribute('aria-modal', 'true');
      button.setAttribute('aria-expanded', 'true');
      backdrop = document.createElement('div');
      backdrop.className = 'offcanvas-backdrop';
      backdrop.addEventListener('click', close);
      panel.before(backdrop);  // same stacking context as the panel
      document.addEventListener('keydown', onKey);
      panel.querySelector('a, button')?.focus();
    });
    panel.querySelectorAll('[data-bs-dismiss="offcanvas"], a[href^="#"], a[href^="/#"]')
      .forEach(el => el.addEventListener('click', close));
  });

  // FAQ on <details>: keep Bootstrap's accordion state class in sync.
  document.querySelectorAll('details.s_nv_faq').forEach(d => {
    d.addEventListener('toggle', () => d.querySelector('summary').classList.toggle('collapsed', !d.open));
  });

  // Hero loop video: respect reduced motion.
  document.querySelectorAll('.s_nv_reel video').forEach(v => {
    if (reduce) { v.removeAttribute('autoplay'); v.pause(); }
  });

  // Showreel: the full film with sound opens only on request.
  document.querySelectorAll('[data-reel-src]').forEach(button => {
    button.addEventListener('click', () => {
      const dialog = document.createElement('dialog');
      dialog.className = 'reel-player';
      dialog.setAttribute('aria-label', button.textContent.trim());
      const close = document.createElement('button');
      close.type = 'button';
      close.className = 'btn-close btn-close-white reel-player__close';
      close.setAttribute('aria-label', document.documentElement.lang === 'ru' ? 'Закрыть' : 'Close');
      const video = document.createElement('video');
      video.src = button.dataset.reelSrc;
      video.controls = true;
      video.autoplay = true;
      video.playsInline = true;
      dialog.append(close, video);
      document.body.append(dialog);
      close.addEventListener('click', () => dialog.close());
      dialog.addEventListener('click', e => { if (e.target === dialog) dialog.close(); });
      dialog.addEventListener('close', () => { video.pause(); dialog.remove(); button.focus(); });
      dialog.showModal();
    });
  });
})();
