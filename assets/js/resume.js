/**
 * resume.js — remembers where you are, with no account.
 *
 * - Visiting any lesson records it as your "last lesson" and adds it to the
 *   visited set (localStorage, this device only).
 * - On the homepage, the main CTA becomes "Resume — <lesson>" when a last
 *   lesson exists, with a count of responses saved on this device.
 * - Anywhere lessons are listed, links you have already visited get a ✓.
 */
(function () {
  "use strict";

  var LAST_KEY = "sdit:resume:last";
  var VISITED_KEY = "sdit:resume:visited";

  function resolveSitePath(path) {
    if (typeof window.__sditResolvePath === "function") {
      return window.__sditResolvePath(path);
    }
    return path;
  }

  function safeParse(raw, fallback) {
    try {
      var v = JSON.parse(raw);
      return v == null ? fallback : v;
    } catch (e) {
      return fallback;
    }
  }

  function isLessonPath(pathname) {
    return /\/courses\/[^/]+\/day-\d+(\.html)?$/.test(pathname);
  }

  function cleanTitle() {
    return (document.title || "")
      .replace(/\s+[—–-]\s+SDIT\s*$/, "")
      .trim();
  }

  // ── Record this visit ───────────────────────────────────────────────────────

  function recordVisit() {
    var path = location.pathname;
    if (!isLessonPath(path)) return;
    try {
      localStorage.setItem(
        LAST_KEY,
        JSON.stringify({ path: path, title: cleanTitle(), t: Date.now() })
      );
      var visited = safeParse(localStorage.getItem(VISITED_KEY), {});
      visited[path] = Date.now();
      localStorage.setItem(VISITED_KEY, JSON.stringify(visited));
    } catch (e) {
      /* storage unavailable — degrade silently */
    }
  }

  // ── Homepage: continue where you left off ───────────────────────────────────

  function countResponses() {
    var n = 0;
    try {
      for (var i = 0; i < localStorage.length; i++) {
        var k = localStorage.key(i);
        if (k && k.indexOf("sdit:") === 0 && k.indexOf("::") !== -1 && localStorage.getItem(k)) n++;
      }
    } catch (e) {}
    return n;
  }

  function enhanceHome() {
    var cta = document.getElementById("home-cta");
    if (!cta) return;
    var last = safeParse(localStorage.getItem(LAST_KEY), null);
    if (!last || !last.path) return;

    var label = document.getElementById("home-cta-label");
    if (label) label.textContent = "Resume — " + (last.title || "your last lesson");
    cta.setAttribute("href", last.path);

    var sub = document.createElement("p");
    sub.className = "home-cta-sub";
    var n = countResponses();
    var startHref = resolveSitePath("/curriculum/schedule.html");
    sub.innerHTML =
      (n ? n + " response" + (n === 1 ? "" : "s") + " saved on this device · " : "") +
      '<a href="' + startHref + '">or start from the beginning</a>';
    cta.parentNode.appendChild(sub);
  }

  // ── Masthead ribbon: resume from any page ──────────────────────────────────

  function enhanceMasthead() {
    var chip = document.getElementById("masthead-resume");
    if (!chip) return;
    var last = safeParse(localStorage.getItem(LAST_KEY), null);
    if (!last || !last.path) return;
    if (location.pathname === last.path) return; // already there
    var m = (last.title || "").match(/^Day\s+0?(\d+)/);
    chip.textContent = m ? "Resume · Day " + m[1] : "Resume lesson";
    if (last.title) chip.setAttribute("title", last.title);
    chip.setAttribute("href", last.path);
    chip.hidden = false;
  }

  // ── Mark visited lessons wherever they are linked ───────────────────────────

  function markVisitedLinks() {
    var visited = safeParse(localStorage.getItem(VISITED_KEY), {});
    var paths = Object.keys(visited);
    if (!paths.length) return;
    var links = document.querySelectorAll("main a[href]");
    Array.prototype.forEach.call(links, function (link) {
      try {
        var u = new URL(link.getAttribute("href"), location.href);
        if (u.origin === location.origin && visited[u.pathname]) {
          link.classList.add("is-visited");
        }
      } catch (e) {}
    });
  }

  // ── Init — after includes.js partials and layout.js chrome settle ───────────

  function init() {
    recordVisit();
    enhanceHome();
    enhanceMasthead();
    markVisitedLinks();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () { setTimeout(init, 250); });
  } else {
    setTimeout(init, 250);
  }
})();
