// Mark JS before first paint so the phone header renders collapsed from the start (no shift).
document.documentElement.classList.add('nav-js');
(() => {
  let saved;
  try { saved = localStorage.getItem('novera-theme'); } catch (_) {}
  const mode = saved === 'dark' || saved === 'light' ? saved : (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  document.documentElement.dataset.theme = mode;
  document.querySelector('meta[name="theme-color"]').content = mode === 'dark' ? '#101b16' : '#f1f4f2';
})();
