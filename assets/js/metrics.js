(function() {
  function run() {
    try {
      const nav = performance.getEntriesByType('navigation')[0];
      const loadMs = nav ? Math.round(nav.domComplete - nav.startTime) : Math.round(performance.now());
      const bytes = new TextEncoder().encode(document.documentElement.outerHTML).length;
      const kb = (bytes / 1024).toFixed(1);
      const links = document.querySelectorAll('a').length;
      const stamp = new Date().toLocaleString();
      const el = document.getElementById('metrics');
      if (el) el.textContent = `Load Time: ${loadMs} ms · Page Size: ${kb} KB · Links: ${links} · ${stamp}`;
    } catch (e) {}
  }
  if (document.readyState === 'complete') run();
  else window.addEventListener('load', run);
})();
