// Lightweight client-side includes for header/footer partials
(function() {
  function resolveSitePath(path) {
    if (typeof window.__sditResolvePath === 'function') {
      return window.__sditResolvePath(path);
    }
    return path;
  }

  function rewritePaths(root) {
    if (typeof window.__sditRewritePaths === 'function') {
      window.__sditRewritePaths(root);
    }
  }

  async function include(el) {
    const src = resolveSitePath(el.getAttribute('data-include'));
    if (!src) return;
    try {
      const res = await fetch(src, { credentials: 'same-origin' });
      if (!res.ok) throw new Error('Failed to fetch ' + src);
      const html = await res.text();
      el.innerHTML = html;
      rewritePaths(el);
      // Execute any scripts inside the included HTML
      const scripts = el.querySelectorAll('script');
      scripts.forEach(old => {
        const s = document.createElement('script');
        // Copy attributes (e.g., src, type, defer)
        for (const a of old.attributes) {
          const value = a.name === 'src' ? resolveSitePath(a.value) : a.value;
          s.setAttribute(a.name, value);
        }
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
    rewritePaths(document);
    await Promise.all(Array.from(nodes).map(include));
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', run);
  } else {
    run();
  }
})();
