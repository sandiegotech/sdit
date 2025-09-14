// Lightweight client-side includes for header/footer partials
(function() {
  async function include(el) {
    const src = el.getAttribute('data-include');
    if (!src) return;
    try {
      const res = await fetch(src, { credentials: 'same-origin' });
      if (!res.ok) throw new Error('Failed to fetch ' + src);
      const html = await res.text();
      el.innerHTML = html;
      // Execute any scripts inside the included HTML
      const scripts = el.querySelectorAll('script');
      scripts.forEach(old => {
        const s = document.createElement('script');
        // Copy attributes (e.g., src, type, defer)
        for (const a of old.attributes) s.setAttribute(a.name, a.value);
        s.text = old.textContent;
        // Use head for external scripts, body for inline
        (s.src ? document.head : document.body).appendChild(s);
        old.remove();
      });
    } catch (e) {
      console.error('Include failed:', src, e);
    }
  }

  async function run() {
    const nodes = document.querySelectorAll('[data-include]');
    await Promise.all(Array.from(nodes).map(include));
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', run);
  } else {
    run();
  }
})();
