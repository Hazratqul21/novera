/* One motion system for the whole site (styles in tools/odoo_site/motion.css):
   - smooth scrolling (Lenis, when window.Lenis is loaded);
   - magnetic pull on [data-magnetic] and the header call to action;
   - headings that rise line by line from behind a mask, images that unveil;
   Everything is desktop/fine-pointer only where it follows the mouse, and all of it
   is skipped with prefers-reduced-motion. Without this file the page is complete. */
(() => {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const fine = matchMedia('(hover: hover) and (pointer: fine)').matches;
  if (reduce) return;
  const root = document.documentElement;
  root.classList.add('mx-on');

  /* ---- smooth scroll ---- */
  let lenis = null;
  if (fine && window.Lenis) {
    lenis = new window.Lenis({
      lerp: 0.1, wheelMultiplier: 1, anchors: { offset: -72 },
      prevent: node => !!(node.closest && node.closest('dialog, .offcanvas, textarea, select')),
    });
    const raf = t => { lenis.raf(t); requestAnimationFrame(raf); };
    requestAnimationFrame(raf);
    // a modal showreel or the mobile menu owns the scroll while it is open
    new MutationObserver(() => (document.querySelector('dialog[open], .offcanvas.show') ? lenis.stop() : lenis.start()))
      .observe(document.body, { childList: true, subtree: true, attributes: true, attributeFilter: ['open', 'class'] });
  }

  if (fine) {
    /* ---- magnetic pull ---- */
    document.querySelectorAll('[data-magnetic], header .btn_cta').forEach(el => {
      const strength = parseFloat(el.dataset.magnetic) || 0.3;
      el.classList.add('mx-magnetic');
      el.addEventListener('pointermove', e => {
        const r = el.getBoundingClientRect();
        el.style.transform = `translate(${(e.clientX - r.left - r.width / 2) * strength}px, ${(e.clientY - r.top - r.height / 2) * strength}px)`;
      });
      el.addEventListener('pointerleave', () => { el.style.transform = ''; });
    });
  }

  /* ---- headings rise line by line; images unveil ---- */
  const splitLines = el => {
    const original = el.innerHTML, text = el.textContent.trim();
    // words -> spans, <br> kept as forced breaks
    const wrap = node => {
      [...node.childNodes].forEach(child => {
        if (child.nodeType === 3) {
          const frag = document.createDocumentFragment();
          child.textContent.split(/(\s+)/).forEach(part => {
            if (!part) return;
            if (/^\s+$/.test(part)) frag.append(' ');
            else { const w = document.createElement('span'); w.className = 'mx-word'; w.textContent = part; frag.append(w); }
          });
          child.replaceWith(frag);
        } else if (child.nodeType === 1 && child.tagName !== 'BR') wrap(child);
      });
    };
    wrap(el);
    const words = [...el.querySelectorAll('.mx-word')];
    if (!words.length) { el.innerHTML = original; return null; }
    let line = -1, top = null;
    words.forEach(w => {
      const t = Math.round(w.getBoundingClientRect().top);
      if (top === null || Math.abs(t - top) > 4) { line++; top = t; }
      const inner = document.createElement('span');
      inner.className = 'mx-word-inner';
      inner.style.transitionDelay = `${line * 90}ms`;
      inner.textContent = w.textContent;
      w.textContent = '';
      w.append(inner);
    });
    el.setAttribute('aria-label', text);
    words.forEach(w => w.setAttribute('aria-hidden', 'true'));
    return { original, lines: line + 1 };
  };

  const headings = [...document.querySelectorAll('main h1, main h2')].filter(h => !h.closest('.o_animate, .fx-aperture, .fx-preloader, dialog'));
  const images = [...document.querySelectorAll('[data-unveil]')];
  if ('IntersectionObserver' in window) {
    const prepared = new Map(), unveilOf = new Map();
    const io = new IntersectionObserver(entries => entries.forEach(e => {
      if (!e.isIntersecting) return;
      io.unobserve(e.target);
      const el = e.target;
      // a fully clipped image never intersects, so its parent is what we watch
      const img = unveilOf.get(el);
      if (img) { img.classList.add('mx-in'); return; }
      const info = prepared.get(el);
      if (!info) return;
      requestAnimationFrame(() => el.classList.add('mx-in'));
      // back to plain text once it has landed, so resizing re-wraps naturally
      setTimeout(() => { el.innerHTML = info.original; el.removeAttribute('aria-label'); el.classList.remove('mx-split', 'mx-in'); }, 1100 + info.lines * 90);
    }), { rootMargin: '0px 0px -12% 0px' });
    const start = () => {
      headings.forEach(h => {
        if (h.getBoundingClientRect().top < innerHeight * 0.88) return;  // already on screen: leave it alone
        const info = splitLines(h);
        if (!info) return;
        h.classList.add('mx-split');
        prepared.set(h, info);
        io.observe(h);
      });
      images.forEach(img => {
        if (img.getBoundingClientRect().top < innerHeight * 0.88) { img.removeAttribute('data-unveil'); return; }
        unveilOf.set(img.parentElement, img);
        io.observe(img.parentElement);
      });
    };
    (document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(start);
  }
})();
