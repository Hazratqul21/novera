/* Novera v2 interactions (2026-10 redesign). Progressive enhancement only: content,
   links and the brief form work without this file. Motion respects
   prefers-reduced-motion. */
(() => {
  'use strict';
  const root = document.documentElement;
  const lang = (root.lang || 'uz').slice(0, 2);
  const L = {
    uz: { search: 'Qidirish', searchPh: 'Sahifa yoki xizmatni qidiring…', empty: 'Hech narsa topilmadi.', hint: 'Enter: ochish. Esc: yopish.',
          kinds: { service: 'Xizmat', work: 'Loyiha', page: 'Sahifa', contact: 'Aloqa', action: 'Amal' }, theme: 'Yorug‘/tungi rejim',
          sound: 'Ovoz effektlari', soundOn: 'Ovoz: yoqilgan', soundOff: 'Ovoz: o‘chiq', top: 'Sahifa boshiga', city: 'Toshkent',
          required: 'Bu maydonni to‘ldiring.', contact: 'Telefon raqami yoki email kiriting.' },
    en: { search: 'Search', searchPh: 'Search pages or services…', empty: 'Nothing found.', hint: 'Enter: open. Esc: close.',
          kinds: { service: 'Service', work: 'Project', page: 'Page', contact: 'Contact', action: 'Action' }, theme: 'Light/dark mode',
          sound: 'Sound effects', soundOn: 'Sound: on', soundOff: 'Sound: off', top: 'Back to top', city: 'Tashkent',
          required: 'Please fill in this field.', contact: 'Enter a phone number or email.' },
    ru: { search: 'Поиск', searchPh: 'Найдите страницу или услугу…', empty: 'Ничего не найдено.', hint: 'Enter: открыть. Esc: закрыть.',
          kinds: { service: 'Услуга', work: 'Проект', page: 'Страница', contact: 'Контакты', action: 'Действие' }, theme: 'Светлая/тёмная тема',
          sound: 'Звуковые эффекты', soundOn: 'Звук: вкл.', soundOff: 'Звук: выкл.', top: 'Наверх', city: 'Ташкент',
          required: 'Заполните это поле.', contact: 'Введите телефон или email.' },
  }[lang];
  if (!L) return;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const fine = matchMedia('(hover: hover) and (pointer: fine) and (min-width: 1001px)');
  const motionOK = () => !reduced.matches;
  const store = (k, v) => { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (_) {} return null; };
  const el = (tag, attrs = {}, ...kids) => {
    const n = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) { if (k === 'text') n.textContent = v; else if (v !== false && v != null) n.setAttribute(k, v === true ? '' : v); }
    n.append(...kids); return n;
  };

  /* ---------- Sound FX (off by default) ---------- */
  let soundOn = store('novera-sound') === '1'; let audio = null;
  function sound(type) {
    if (!soundOn) return;
    try {
      audio = audio || new (window.AudioContext || window.webkitAudioContext)();
      const o = audio.createOscillator(), g = audio.createGain(), t = audio.currentTime;
      o.type = 'sine'; o.frequency.value = { hover: 784, tap: 587, ok: 523, open: 440 }[type] || 600;
      g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(type === 'hover' ? 0.012 : 0.03, t + 0.012); g.gain.exponentialRampToValueAtTime(0.0001, t + 0.14);
      o.connect(g).connect(audio.destination); o.start(t); o.stop(t + 0.15);
    } catch (_) {}
  }
  document.addEventListener('click', e => { if (e.target.closest('a,button,[role="option"]')) sound('tap'); });
  if (fine.matches) document.querySelectorAll('.button').forEach(b => b.addEventListener('pointerenter', () => sound('hover')));

  /* ---------- Toasts (site.js calls window.siteToast after a lead is sent) ---------- */
  const toasts = el('div', { class: 'toasts', role: 'status', 'aria-live': 'polite' }); document.body.append(toasts);
  window.siteToast = (message, kind = 'info') => {
    const t = el('div', { class: `toast toast--${kind}`, text: message }); toasts.append(t);
    requestAnimationFrame(() => t.classList.add('is-in'));
    setTimeout(() => { t.classList.remove('is-in'); setTimeout(() => t.remove(), 400); }, 4600);
    sound(kind === 'error' ? 'open' : 'ok');
  };

  /* ---------- Header: real height for the hero overlap; dark tone over dark sections ---------- */
  const header = document.querySelector('.header');
  const darkZones = [...document.querySelectorAll('[data-tone="dark"], .site-footer')];
  const tone = () => {
    if (!header) return;
    root.style.setProperty('--header-h', `${header.offsetHeight}px`);
    const line = header.getBoundingClientRect().bottom / 2;
    header.classList.toggle('is-dark', darkZones.some(z => { const r = z.getBoundingClientRect(); return r.top <= line && r.bottom >= line; }));
  };
  addEventListener('scroll', tone, { passive: true }); addEventListener('resize', tone); tone();

  /* ---------- Footer extras + back to top ---------- */
  const bottom = document.querySelector('.site-footer .footer-bottom');
  if (bottom) {
    const clock = el('time', { class: 'footer-clock' });
    const fmt = new Intl.DateTimeFormat(lang === 'uz' ? 'uz-UZ' : lang, { hour: '2-digit', minute: '2-digit', timeZone: 'Asia/Tashkent' });
    const tick = () => { const now = new Date(); clock.textContent = `${L.city} ${fmt.format(now)}`; clock.dateTime = now.toISOString(); };
    tick(); setInterval(tick, 30000);
    const btn = el('button', { class: 'sound-toggle', type: 'button' });
    const paint = () => { btn.textContent = soundOn ? L.soundOn : L.soundOff; btn.setAttribute('aria-pressed', String(soundOn)); };
    paint(); btn.addEventListener('click', () => { soundOn = !soundOn; store('novera-sound', soundOn ? '1' : '0'); paint(); sound('ok'); });
    bottom.append(el('div', { class: 'footer-extras' }, clock, btn));
  }
  const top = el('button', { class: 'to-top', type: 'button', 'aria-label': L.top }, el('span', { 'aria-hidden': 'true', text: '↑' }));
  document.body.append(top);
  const showTop = () => top.classList.toggle('is-visible', scrollY > innerHeight * 1.2);
  addEventListener('scroll', showTop, { passive: true }); showTop();
  top.addEventListener('click', () => { scrollTo({ top: 0, behavior: motionOK() ? 'smooth' : 'auto' }); document.querySelector('.wordmark')?.focus({ preventScroll: true }); });

  /* ---------- Mega menu (desktop) ---------- */
  const megaLink = document.querySelector('[data-mega]');
  const mega = megaLink && document.getElementById(megaLink.dataset.mega);
  if (megaLink && mega) {
    let timer = 0;
    megaLink.setAttribute('aria-controls', mega.id); megaLink.setAttribute('aria-expanded', 'false');
    const open = () => { if (!fine.matches) return; clearTimeout(timer); mega.hidden = false; megaLink.setAttribute('aria-expanded', 'true'); requestAnimationFrame(() => mega.classList.add('is-open')); };
    const close = now => { clearTimeout(timer); timer = setTimeout(() => { mega.classList.remove('is-open'); megaLink.setAttribute('aria-expanded', 'false'); setTimeout(() => { if (!mega.classList.contains('is-open')) mega.hidden = true; }, 220); }, now ? 0 : 160); };
    megaLink.addEventListener('pointerenter', open); megaLink.addEventListener('focus', open);
    mega.addEventListener('pointerenter', () => clearTimeout(timer));
    megaLink.addEventListener('pointerleave', () => close()); mega.addEventListener('pointerleave', () => close());
    mega.addEventListener('focusout', e => { if (!mega.contains(e.relatedTarget) && e.relatedTarget !== megaLink) close(true); });
    megaLink.addEventListener('blur', e => { if (!mega.contains(e.relatedTarget)) close(); });
    document.addEventListener('keydown', e => { if (e.key === 'Escape' && !mega.hidden) { close(true); megaLink.focus(); } });
  }

  /* ---------- Command palette: Ctrl/Cmd+K or "/" ---------- */
  const palette = el('dialog', { class: 'cmdk', 'aria-label': L.search });
  const input = el('input', { class: 'cmdk__input', type: 'search', placeholder: L.searchPh, 'aria-label': L.search, autocomplete: 'off', role: 'combobox', 'aria-expanded': 'true', 'aria-controls': 'cmdk-list' });
  const list = el('ul', { class: 'cmdk__list', id: 'cmdk-list', role: 'listbox' });
  palette.append(el('div', { class: 'cmdk__box' }, input, list, el('p', { class: 'cmdk__hint', text: L.hint }))); document.body.append(palette);
  let rows = null, shown = [], active = 0;
  const norm = s => s.toLowerCase().normalize('NFD').replace(/[̀-ͯ‘’ʻʼ'`]/g, '');
  const actions = () => {
    const out = []; const theme = document.querySelector('.theme-toggle');
    if (theme && !theme.hidden) out.push({ t: L.theme, d: '', k: 'action', run: () => theme.click() });
    out.push({ t: L.sound, d: soundOn ? L.soundOn : L.soundOff, k: 'action', run: () => document.querySelector('.sound-toggle')?.click() });
    document.querySelectorAll('.header .languages a').forEach(a => { if (!a.hasAttribute('aria-current')) out.push({ t: a.textContent, d: a.hreflang, k: 'action', u: a.getAttribute('href') }); });
    return out;
  };
  const mark = i => { active = i; list.querySelectorAll('.cmdk__item').forEach((li, n) => li.setAttribute('aria-selected', String(n === i))); input.setAttribute('aria-activedescendant', `cmdk-${i}`); list.children[i]?.scrollIntoView({ block: 'nearest' }); };
  const choose = i => { const r = shown[i]; if (!r) return; palette.close(); if (r.run) r.run(); else location.href = r.u; };
  function render() {
    const q = norm(input.value.trim()); const pool = [...(rows || []), ...actions()];
    shown = (q ? pool.filter(r => norm(`${r.t} ${r.d}`).includes(q)) : pool).slice(0, 12); active = 0;
    list.replaceChildren(...(shown.length ? shown.map((r, i) => {
      const li = el('li', { class: 'cmdk__item', role: 'option', id: `cmdk-${i}`, 'aria-selected': String(i === 0) }, el('span', { class: 'cmdk__kind', text: L.kinds[r.k] || '' }), el('b', { text: r.t }), el('small', { text: r.d }));
      li.addEventListener('click', () => choose(i)); li.addEventListener('pointermove', () => mark(i)); return li;
    }) : [el('li', { class: 'cmdk__empty', text: L.empty })]));
    input.setAttribute('aria-activedescendant', shown.length ? 'cmdk-0' : '');
  }
  async function openPalette() {
    if (palette.open) return;
    if (!rows) { try { rows = (await (await fetch('/assets/search.json')).json())[lang] || []; } catch (_) { rows = []; } }
    input.value = ''; render(); palette.showModal(); input.focus(); sound('open');
  }
  input.addEventListener('input', render);
  input.addEventListener('keydown', e => {
    if (e.key === 'ArrowDown') { e.preventDefault(); if (shown.length) mark((active + 1) % shown.length); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); if (shown.length) mark((active - 1 + shown.length) % shown.length); }
    else if (e.key === 'Enter') { e.preventDefault(); choose(active); }
  });
  palette.addEventListener('click', e => { if (e.target === palette) palette.close(); });
  document.addEventListener('keydown', e => {
    const typing = /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement?.tagName);
    if ((e.key === 'k' || e.key === 'K') && (e.metaKey || e.ctrlKey)) { e.preventDefault(); openPalette(); }
    else if (e.key === '/' && !typing && !palette.open) { e.preventDefault(); openPalette(); }
  });
  const langs = document.querySelector('.header .languages');
  if (langs) {
    const mac = /Mac|iPhone|iPad/.test(navigator.platform);
    const trigger = el('button', { class: 'cmdk-trigger', type: 'button', 'aria-keyshortcuts': mac ? 'Meta+K' : 'Control+K' }, el('span', { text: L.search }), el('kbd', { text: mac ? '⌘K' : 'Ctrl K' }));
    trigger.addEventListener('click', openPalette); langs.before(trigger);
  }

  /* ---------- Brief form: live validation (site.js sends the lead) ---------- */
  const form = document.getElementById('brief-form');
  if (form) {
    const contactField = form.querySelector('[name="contact"]');
    const check = field => {
      let msg = '';
      if (field === contactField && field.value.trim() && !/^(\+?[\d\s()-]{7,}|[^\s@]+@[^\s@]+\.[^\s@]+)$/.test(field.value.trim())) msg = L.contact;
      if (field === contactField) field.setCustomValidity(msg);
      if (!msg && !field.value.trim()) msg = L.required;
      let note = document.getElementById(`${field.id}-error`);
      if (!note) { note = el('p', { class: 'field-error', id: `${field.id}-error` }); field.after(note); field.setAttribute('aria-describedby', [field.getAttribute('aria-describedby'), note.id].filter(Boolean).join(' ')); }
      note.textContent = field.dataset.touched ? msg : '';
      field.setAttribute('aria-invalid', String(Boolean(msg && field.dataset.touched)));
      field.classList.toggle('is-valid', !msg);
    };
    form.querySelectorAll('input[required],textarea[required]').forEach(f => {
      f.addEventListener('blur', () => { if (f.value) f.dataset.touched = '1'; check(f); });
      f.addEventListener('input', () => check(f));
    });
    form.addEventListener('submit', () => form.querySelectorAll('input[required],textarea[required]').forEach(f => { f.dataset.touched = '1'; check(f); }), true);
  }

  /* ---------- Capabilities marquee ---------- */
  const caps = document.querySelector('.capabilities');
  if (caps && !reduced.matches) {
    const items = [...caps.children];
    const track = el('div', { class: 'cap-track' }, ...items);
    // Second copy keeps the loop seamless; it is hidden from assistive tech.
    items.forEach(i => { const c = i.cloneNode(true); c.setAttribute('aria-hidden', 'true'); track.append(c); });
    caps.replaceChildren(track); caps.classList.add('is-marquee');
  }

  if (fine.matches && motionOK()) {
    /* ---------- Sculpture: turns toward the cursor across the hero ---------- */
    const hero = document.querySelector('.hero-v2'); const art = hero && hero.querySelector('.hero-art');
    if (art) {
      hero.addEventListener('pointermove', e => {
        const r = hero.getBoundingClientRect(); const x = (e.clientX - r.left) / r.width - 0.5; const y = (e.clientY - r.top) / r.height - 0.5;
        art.style.transform = `perspective(1100px) rotateY(${(x * 14).toFixed(2)}deg) rotateX(${(-y * 10).toFixed(2)}deg) translateZ(0)`;
        const a = art.getBoundingClientRect();
        art.style.setProperty('--mx', `${(((e.clientX - a.left) / a.width) * 100).toFixed(1)}%`); art.style.setProperty('--my', `${(((e.clientY - a.top) / a.height) * 100).toFixed(1)}%`);
      });
      hero.addEventListener('pointerleave', () => { art.style.transform = ''; });
    }
    /* ---------- One orchestrated moment: the hero headline rises word by word on load ---------- */
    const h1 = document.querySelector('.hero-v2 h1');
    if (h1) {
      let i = 0;
      const parts = [...h1.childNodes].flatMap(n => n.nodeType !== 3 ? [n.cloneNode(true)] : n.textContent.split(/(\s+)/).map(w => {
        if (!w.trim()) return document.createTextNode(w);
        const s = el('span', { class: 'split-w' }, el('span', { text: w })); s.style.setProperty('--i', i++); return s;
      }));
      h1.replaceChildren(...parts); h1.classList.add('is-split');
      requestAnimationFrame(() => requestAnimationFrame(() => h1.classList.add('is-split-in')));
    }
  }
})();
