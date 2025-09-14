// Enhance chapter and section lists into card grids
(function() {
  function wrapAsGrid(items) {
    if (!items.length) return;
    // Don't re-wrap if already inside a .cards-grid
    const first = items[0];
    const parent = first.parentElement;
    if (parent && parent.classList.contains('cards-grid')) return;

    const grid = document.createElement('div');
    grid.className = 'cards-grid';
    // Insert grid before the first item
    parent.insertBefore(grid, first);
    // Move all sibling items with the same class into the grid
    const list = Array.from(parent.querySelectorAll(`.${first.className.split(' ').join('.')}, .section-item, .chapter-item`));
    // Filter to only direct children of parent to avoid moving nested sections
    const direct = list.filter(el => el.parentElement === parent);
    direct.forEach(el => grid.appendChild(el));
  }

  function enhance() {
    // Chapter lists
    const chapters = document.querySelectorAll('.chapter-item');
    if (chapters.length) wrapAsGrid(Array.from(chapters));

    // Section lists
    const sections = document.querySelectorAll('.section-item');
    if (sections.length) wrapAsGrid(Array.from(sections));
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', enhance);
  } else {
    enhance();
  }
})();
