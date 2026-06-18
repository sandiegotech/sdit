/**
 * utils.js — shared helpers for the curriculum frontend, exposed as window.SDIT.
 *
 * Loaded first among the header scripts (includes.js forces ordered execution),
 * so layout.js / course-mode.js / account.js can build on it. The catalog
 * loader is cached here, so a page fetches /assets/catalog.json at most once
 * no matter how many modules need it.
 */
(function () {
  "use strict";

  function resolvePath(path) {
    return typeof window.__sditResolvePath === "function" ? window.__sditResolvePath(path) : path;
  }

  function pad(n) { return String(n).padStart(2, "0"); }

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  // The one place the course/day URL shape is defined.
  var LESSON_RE = /\/courses\/([A-Z]+-\d+)\/day-(\d{2})(?:\.html)?$/;
  function courseOf(path) { var m = (path || "").match(/\/courses\/([A-Z]+-\d+)\//); return m ? m[1] : null; }
  function dayOf(path) { var m = (path || "").match(/\/day-(\d{2})(?:\.html)?$/); return m ? parseInt(m[1], 10) : null; }

  var _catalog = null;
  function getCatalog() {
    if (!_catalog) {
      _catalog = fetch(resolvePath("/assets/catalog.json"))
        .then(function (r) { return r.ok ? r.json() : { courses: {} }; })
        .catch(function () { return { courses: {} }; });
    }
    return _catalog;
  }

  window.SDIT = {
    resolvePath: resolvePath,
    pad: pad,
    esc: esc,
    LESSON_RE: LESSON_RE,
    courseOf: courseOf,
    dayOf: dayOf,
    getCatalog: getCatalog
  };
})();
