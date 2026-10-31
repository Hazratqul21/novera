/* Brief form -> /api/v1/lead and project estimate -> /api/v1/estimate (backend/). */
(() => {
  const lang = (document.documentElement.lang || 'uz').slice(0, 2);
  const messages = (window.noveraMessages || {})[lang] || (window.noveraMessages || {}).uz || {};
  const honeypot = form => (form.querySelector('[name="website"]') || {}).value || '';
  const post = (url, body) => fetch(url, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body)
  });

  const form = document.getElementById('brief-form');
  if (form && window.fetch) {
    const status = document.getElementById('form-status');
    const brief = document.getElementById('brief');
    brief.addEventListener('input', () => { brief.setCustomValidity(''); status.textContent = ''; });
    brief.addEventListener('invalid', () => { if (brief.validity.valueMissing) brief.setCustomValidity(messages.required || ''); });
    form.addEventListener('submit', async event => {
      event.preventDefault();
      if (!form.reportValidity()) return;
      const button = form.querySelector('button[type="submit"]');
      const label = button.textContent;
      button.disabled = true;
      button.textContent = '…';
      try {
        const response = await post('/api/v1/lead', {
          name: document.getElementById('brief-name').value.trim(),
          contact: document.getElementById('brief-contact').value.trim(),
          service: new FormData(form).get('service'),
          details: brief.value.trim(), lang, website: honeypot(form)
        });
        if (!response.ok) throw new Error(String(response.status));
        form.reset();
        status.className = 'mt-3 mb-0 text-o-color-1';
        status.textContent = messages.leadSuccess || '';
      } catch (_) {
        status.className = 'mt-3 mb-0 text-danger';
        status.textContent = messages.leadError || '';
      } finally {
        button.disabled = false;
        button.textContent = label;
      }
    });
  }

  const estimate = document.getElementById('ai-calc-form');
  const result = document.getElementById('ai-calc-result');
  if (estimate && result && window.fetch) {
    estimate.addEventListener('submit', async event => {
      event.preventDefault();
      if (!estimate.reportValidity()) return;
      const button = estimate.querySelector('button[type="submit"]');
      const label = button.textContent;
      button.disabled = true;
      button.textContent = messages.aiLoading || '…';
      result.hidden = true;
      // Model output is untrusted text: build nodes, never innerHTML.
      const row = (name, value) => {
        const p = document.createElement('p');
        if (name) {
          const b = document.createElement('strong');
          b.textContent = name + ' ';
          p.append(b);
        }
        p.append(document.createTextNode(String(value || '')));
        return p;
      };
      try {
        const response = await post('/api/v1/estimate', {
          description: document.getElementById('ai-description').value.trim(), lang, website: honeypot(estimate)
        });
        if (!response.ok) throw new Error(String(response.status));
        const data = await response.json();
        result.replaceChildren(
          row(messages.aiBudget, data.estimated_price),
          row(messages.aiTime, data.estimated_time),
          row(messages.aiStack, Array.isArray(data.tech_stack) ? data.tech_stack.join(', ') : ''),
          row('', data.recommendation));
      } catch (_) {
        result.replaceChildren(row('', messages.aiError));
      } finally {
        result.hidden = false;
        button.disabled = false;
        button.textContent = label;
      }
    });
  }
})();
