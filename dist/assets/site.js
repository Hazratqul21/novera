(() => {
  'use strict';
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  document.querySelector('#year').textContent = new Date().getFullYear();
  document.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener('click', event => {
      const target = document.querySelector(link.getAttribute('href') === '#' ? 'body' : link.getAttribute('href'));
      if (!target) return;
      event.preventDefault();
      if (link.dataset.service) {
        const radio = [...document.querySelectorAll('input[name="service"]')].find(input => input.value === link.dataset.service);
        if (radio) radio.checked = true;
      }
      target.scrollIntoView({behavior: reduced.matches || event.detail === 0 ? 'instant' : 'smooth', block:'start'});
      if (target !== document.body) {
        target.setAttribute('tabindex', '-1');
        target.focus({preventScroll:true});
        target.addEventListener('blur', () => target.removeAttribute('tabindex'), {once:true});
        history.replaceState(null, '', link.getAttribute('href'));
      }
    });
  });
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        if (!reduced.matches && !entry.target.contains(document.activeElement)) {
          entry.target.animate([{opacity:0,transform:'translateY(20px)'},{opacity:1,transform:'translateY(0)'}], {duration:600,easing:'cubic-bezier(.23,1,.32,1)'});
        }
        observer.unobserve(entry.target);
      });
    }, {threshold:.12});
    document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
    reduced.addEventListener('change', () => { if(reduced.matches) document.getAnimations().forEach(animation => animation.finish()); });
  }
  document.querySelector('#brief-form').addEventListener('submit', event => {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    const text = String(data.get('brief')).trim();
    const status = document.querySelector('#form-status');
    if (!text) {status.textContent = 'Iltimos, vazifangizni qisqacha yozing.'; document.querySelector('#brief').focus(); return;}
    const subject = encodeURIComponent(`Novera — ${data.get('service')}`);
    const body = encodeURIComponent(`Assalomu alaykum!\n\nYo‘nalish: ${data.get('service')}\n\n${text}`);
    window.location.href = `mailto:info@innovera.uz?subject=${subject}&body=${body}`;
    status.textContent = 'Email ilovasida xatni tekshirib, yuboring. Ilova ochilmasa: info@innovera.uz yoki +998 99 811 28 29.';
  });
})();
