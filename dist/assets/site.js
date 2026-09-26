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
    link.addEventListener('click', () => { if (location.hash) link.href = link.pathname + location.hash; });
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
  let keyboard = false; let frame = 0;

  document.querySelector('#year').textContent = new Date().getFullYear();
  if(form) { form.hidden = false; form.querySelectorAll('button').forEach(b => b.hidden = false); }

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
      if (link.dataset.service && form) {
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
      if(!section) return;
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
  reduced.addEventListener('change', () => { if(reduced.matches) document.getAnimations().forEach(animation => animation.cancel()); });

  // 1. LEAD FORM INTEGRATION
  if (form) {
    textarea.addEventListener('input', () => {textarea.setCustomValidity('');status.textContent='';});
    textarea.addEventListener('invalid', () => { if (textarea.validity.valueMissing) textarea.setCustomValidity(messages.required); });

    form.addEventListener('submit', async event => {
      event.preventDefault();
      if (!form.reportValidity()) return;
      const submitBtn = form.querySelector('button[type="submit"]');
      const originalBtnHtml = submitBtn.innerHTML;
      const name = document.getElementById('brief-name').value.trim();
      const contact = document.getElementById('brief-contact').value.trim();
      const service = new FormData(form).get('service');
      const text = textarea.value.trim();

      submitBtn.textContent = '...'; submitBtn.disabled = true;
      try {
        const response = await fetch('http://127.0.0.1:8000/api/v1/lead', {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name, contact, details: `Сервис: ${service}\n\nОписание: ${text}` })
        });
        if (!response.ok) throw new Error();
        status.style.color = 'var(--brand)'; status.textContent = messages.leadSuccess; form.reset();
      } catch (err) { status.style.color = 'red'; status.textContent = messages.leadError;
      } finally { submitBtn.innerHTML = originalBtnHtml; submitBtn.disabled = false; }
    });
  }

  // 2. AI ESTIMATOR INTEGRATION
  const aiForm = document.getElementById('ai-calc-form');
  const aiResult = document.getElementById('ai-calc-result');
  if (aiForm) {
    aiForm.addEventListener('submit', async event => {
      event.preventDefault();
      const submitBtn = aiForm.querySelector('button[type="submit"]');
      const originalBtnHtml = submitBtn.innerHTML;
      submitBtn.textContent = messages.aiLoading; submitBtn.disabled = true;
      aiResult.hidden = true; aiResult.style.opacity = '0';

      try {
        const response = await fetch('http://127.0.0.1:8000/api/v1/estimate', {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ description: document.getElementById('ai-description').value.trim(), urgency: 'normal' })
        });
        if (!response.ok) throw new Error();
        const data = await response.json();

        // Здесь используется динамический перевод из messages.js
        aiResult.innerHTML = `
          <p><strong>${messages.aiBudget}</strong> ${data.estimated_price}</p>
          <p><strong>${messages.aiTime}</strong> ${data.estimated_time}</p>
          <p><strong>${messages.aiStack}</strong> ${data.tech_stack.join(', ')}</p>
          <p style="margin-top:16px; font-size:14px; color:var(--muted);">${data.recommendation}</p>
        `;
        aiResult.hidden = false;
        aiResult.animate([{ opacity: 0, transform: 'translateY(15px)' }, { opacity: 1, transform: 'translateY(0)' }], { duration: 500, easing: easeOut, fill: 'forwards' });
      } catch (err) {
        aiResult.innerHTML = `<p style="color: red;">${messages.aiError}</p>`;
        aiResult.hidden = false; aiResult.style.opacity = '1';
      } finally { submitBtn.innerHTML = originalBtnHtml; submitBtn.disabled = false; }
    });
  }
})();