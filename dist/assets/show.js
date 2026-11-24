/* Product showcase behaviour (styles in tools/odoo_site/show.css): stacked cards settle back,
   the statement fills in while scrolling, screenshots open in a lightbox. */
(() => {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* stacked cards: the one underneath shrinks a little as the next slides over it */
  const cards = [...document.querySelectorAll('.sh-stack > .sh-card')];
  const stacked = matchMedia('(min-width: 992px) and (min-height: 640px)');
  /* statement: words light up */
  const statements = reduce ? [] : [...document.querySelectorAll('.sh-statement')].map(el => {
    const words = el.textContent.trim().split(/\s+/);
    el.textContent = '';
    const spans = words.map((w, i) => {
      const s = document.createElement('span');
      s.className = 'sh-w';
      s.textContent = w;
      el.append(s, i < words.length - 1 ? ' ' : '');
      return s;
    });
    return { el, spans };
  });
  let queued = false;
  const update = () => {
    queued = false;
    if (!reduce && stacked.matches) {
      cards.forEach((c, i) => {
        const next = cards[i + 1];
        if (!next) return;
        const gap = next.getBoundingClientRect().top - c.getBoundingClientRect().top;
        const k = Math.max(0, Math.min(1, 1 - (gap - 12) / c.offsetHeight));
        c.style.transform = k > 0.001 ? `scale(${1 - k * 0.05})` : '';
      });
    } else cards.forEach(c => { c.style.transform = ''; });
    statements.forEach(({ el, spans }) => {
      const r = el.getBoundingClientRect();
      const p = (innerHeight * 0.85 - r.top) / (innerHeight * 0.45 + r.height);
      spans.forEach((s, i) => s.classList.toggle('is-on', i / spans.length < p));
    });
  };
  const queue = () => { if (!queued) { queued = true; requestAnimationFrame(update); } };
  if (cards.length || statements.length) {
    addEventListener('scroll', queue, { passive: true });
    addEventListener('resize', queue);
    update();
  }

  /* product video inside the laptop: plays only while visible */
  document.querySelectorAll('.sh-laptop video').forEach(v => {
    if (reduce) return;
    new IntersectionObserver(([e]) => { if (e.isIntersecting) v.play().catch(() => {}); else v.pause(); }, { threshold: 0.2 }).observe(v);
  });

  /* lightbox */
  const shots = [...document.querySelectorAll('a[data-lightbox]')];
  if (!shots.length || !window.HTMLDialogElement) return;
  const T = { ru: ['Закрыть', 'Назад', 'Вперёд'], uz: ['Yopish', 'Oldingi', 'Keyingi'], en: ['Close', 'Previous', 'Next'] }[document.documentElement.lang] || ['Close', 'Previous', 'Next'];
  const dialog = document.createElement('dialog');
  dialog.className = 'sh-light';
  const img = document.createElement('img'), cap = document.createElement('p');
  const btn = (cls, text, label, fn) => {
    const b = document.createElement('button');
    b.type = 'button'; b.className = cls; b.textContent = text; b.setAttribute('aria-label', label);
    b.addEventListener('click', fn);
    return b;
  };
  let at = 0, from = null;
  const show = i => {
    at = (i + shots.length) % shots.length;
    const alt = shots[at].querySelector('img').alt;
    img.src = shots[at].href; img.alt = alt; cap.textContent = alt;
  };
  dialog.append(img, cap, btn('sh-x', '×', T[0], () => dialog.close()));
  if (shots.length > 1) dialog.append(btn('sh-prev', '‹', T[1], () => show(at - 1)), btn('sh-nextb', '›', T[2], () => show(at + 1)));
  dialog.addEventListener('click', e => { if (e.target === dialog) dialog.close(); });
  dialog.addEventListener('keydown', e => { if (e.key === 'ArrowRight') show(at + 1); if (e.key === 'ArrowLeft') show(at - 1); });
  dialog.addEventListener('close', () => { if (from) from.focus(); });
  document.body.append(dialog);
  shots.forEach((a, i) => a.addEventListener('click', e => {
    if (e.metaKey || e.ctrlKey) return;
    e.preventDefault();
    from = a; show(i); dialog.showModal();
  }));
})();
