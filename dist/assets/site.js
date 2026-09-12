(() => {
  'use strict';
  const lang = document.documentElement.lang;
  const messages = window.noveraMessages[lang] || window.noveraMessages.uz;
  const themeToggle = document.querySelector('.theme-toggle');
  const systemTheme = matchMedia('(prefers-color-scheme: dark)');
  function applyTheme(mode) {
    document.documentElement.dataset.theme = mode;
    document.querySelector('meta[name="theme-color"]').content = mode === 'dark' ? '#101b16' : '#f1f4f2';
    themeToggle.setAttribute('aria-pressed',String(mode === 'dark'));
    themeToggle.setAttribute('aria-label',mode === 'dark' ? messages.light : messages.dark);
  }
  applyTheme(document.documentElement.dataset.theme || 'light');
  themeToggle.hidden = false;
  themeToggle.addEventListener('click', () => {
    const mode = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    applyTheme(mode);
    try { localStorage.setItem('novera-theme',mode); } catch (_) {}
  });
  systemTheme.addEventListener('change', event => {
    let saved;
    try { saved = localStorage.getItem('novera-theme'); } catch (_) {}
    if (saved !== 'dark' && saved !== 'light') applyTheme(event.matches ? 'dark' : 'light');
  });
  document.querySelectorAll('.languages a').forEach(link => {
    link.addEventListener('click', () => {
      if (location.hash) link.href = link.pathname + location.hash;
    });
  });
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const form = document.querySelector('#brief-form');
  const textarea = document.querySelector('#brief');
  const status = document.querySelector('#form-status');
  const header = document.querySelector('.header');
  const progress = document.querySelector('.reading-progress');
  const navLinks = [...document.querySelectorAll('.main-nav a')];
  const sections = navLinks.map(link => document.querySelector(link.hash));
  const steps = [...document.querySelectorAll('.steps li')];
  const easeOut = getComputedStyle(document.documentElement).getPropertyValue('--ease-out').trim();
  let keyboard = false;
  let frame = 0;

  document.querySelector('#year').textContent = new Date().getFullYear();
  form.hidden = false;
  form.querySelectorAll('button').forEach(button => { button.hidden = false; });
  document.addEventListener('keydown', () => { keyboard = true; });
  document.addEventListener('pointerdown', () => { keyboard = false; }, {passive:true});
  document.addEventListener('wheel', () => { keyboard = false; }, {passive:true});

  document.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener('click', event => {
      if (event.metaKey || event.ctrlKey || event.altKey || event.shiftKey || event.button !== 0) return;
      const hash = link.getAttribute('href');
      const target = hash === '#' ? document.body : document.getElementById(hash.slice(1));
      if (!target) return;
      event.preventDefault();
      if (link.dataset.service) {
        const radio = [...form.querySelectorAll('input[name="service"]')].find(input => input.value === link.dataset.service);
        if (radio) radio.checked = true;
        status.textContent = '';
      }
      target.scrollIntoView({behavior: reduced.matches || event.detail === 0 ? 'instant' : 'smooth', block:'start'});
      if (target !== document.body) {
        const oldTabindex = target.getAttribute('tabindex');
        target.setAttribute('tabindex', '-1');
        target.focus({preventScroll:true});
        target.addEventListener('blur', () => {
          if (oldTabindex === null) target.removeAttribute('tabindex');
          else target.setAttribute('tabindex', oldTabindex);
        }, {once:true});
      }
      if (location.hash !== hash) history.pushState(null, '', hash === '#' ? location.pathname : hash);
    });
  });

  function updateScroll() {
    frame = 0;
    const max = document.documentElement.scrollHeight - innerHeight;
    progress.style.transform = 'scaleX(' + (max > 0 ? Math.min(1,Math.max(0,scrollY / max)) : 0) + ')';
    header.classList.toggle('is-scrolled', scrollY > 20);
    const guide = header.getBoundingClientRect().bottom + 80;
    let active = -1;
    sections.forEach((section, index) => {
      const rect = section.getBoundingClientRect();
      if (rect.top <= guide && rect.bottom > guide) active = index;
    });
    navLinks.forEach((link,index) => {
      if (index === active) link.setAttribute('aria-current','location');
      else link.removeAttribute('aria-current');
    });
    let current = 0;
    steps.forEach((step,index) => { if (step.getBoundingClientRect().top <= innerHeight * .55) current = index; });
    steps.forEach((step,index) => step.classList.toggle('is-current',index === current));
  }
  function scheduleScroll() { if (!frame) frame = requestAnimationFrame(updateScroll); }
  addEventListener('scroll',scheduleScroll,{passive:true});
  addEventListener('resize',scheduleScroll);
  addEventListener('pageshow',scheduleScroll);
  if ('ResizeObserver' in window) new ResizeObserver(scheduleScroll).observe(document.body);
  scheduleScroll();

  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        if (!reduced.matches && !keyboard && !entry.target.contains(document.activeElement)) {
          const animation = entry.target.animate([{opacity:0,transform:'translateY(20px)'},{opacity:1,transform:'translateY(0)'}], {duration:600,easing:easeOut});
          entry.target.addEventListener('focusin',()=>animation.finish(),{once:true});
        }
        observer.unobserve(entry.target);
      });
    }, {threshold:.12});
    document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
  }
  reduced.addEventListener('change', () => {
    if(reduced.matches) document.getAnimations().forEach(animation => animation.cancel());
  });

  function readBrief() {
    const text = textarea.value.trim();
    textarea.setCustomValidity(text ? '' : messages.required);
    if (!form.reportValidity()) return null;
    return {service:new FormData(form).get('service'),text};
  }
  textarea.addEventListener('input', () => {textarea.setCustomValidity('');status.textContent='';});
  textarea.addEventListener('invalid', () => {
    if (textarea.validity.valueMissing) textarea.setCustomValidity(messages.required);
  });
  form.addEventListener('submit', event => {
    event.preventDefault();
    const brief = readBrief();
    if (!brief) return;
    const subject = encodeURIComponent('Novera — ' + brief.service);
    const body = encodeURIComponent(messages.greeting + '\n\n' + messages.direction + ': ' + brief.service + '\n\n' + brief.text);
    window.location.href = 'mailto:info@innovera.uz?subject=' + subject + '&body=' + body;
    status.textContent = messages.draft;
  });
  form.querySelector('.download-brief').addEventListener('click', () => {
    const brief = readBrief();
    if (!brief) return;
    const content = 'NOVERA — ' + messages.brief + '\n\n' + messages.direction + ': ' + brief.service + '\n\n' + brief.text + '\n\ninfo@innovera.uz / +998 99 811 28 29\n' + messages.unsent + '\n';
    const url = URL.createObjectURL(new Blob([content],{type:'text/plain;charset=utf-8'}));
    const link = document.createElement('a');
    link.href=url; link.download='novera-loyiha-brifi.txt';
    document.body.append(link);link.click();link.remove();
    setTimeout(()=>URL.revokeObjectURL(url),1000);
    status.textContent=messages.saved;
  });
})();
