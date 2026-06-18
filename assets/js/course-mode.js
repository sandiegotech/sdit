/**
 * course-mode.js — the signed-in learning environment.
 *
 * When you're signed in, a calm strip appears under the masthead: the course
 * you're working in, your progress through it, and one Continue button to the
 * next day. It's derived from your synced progress plus the course catalog —
 * there's no enrollment to manage; your current course is simply the one you're
 * in. Signed out, nothing renders and the site is unchanged.
 */
(function () {
  "use strict";

  var LESSON_RE = /\/courses\/([A-Z]+-\d+)\/day-(\d{2})(?:\.html)?$/;
  var catalogPromise = null;

  function resolveSitePath(p) {
    return typeof window.__sditResolvePath === "function" ? window.__sditResolvePath(p) : p;
  }

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  function loadCatalog() {
    if (!catalogPromise) {
      catalogPromise = fetch(resolveSitePath("/assets/catalog.json"))
        .then(function (r) { return r.ok ? r.json() : { courses: {} }; })
        .catch(function () { return { courses: {} }; });
    }
    return catalogPromise;
  }

  function courseOf(p) { var m = (p || "").match(/\/courses\/([A-Z]+-\d+)\//); return m ? m[1] : null; }
  function dayOf(p) { var m = (p || "").match(/\/day-(\d{2})(?:\.html)?$/); return m ? parseInt(m[1], 10) : null; }

  function localLastCourse() {
    try {
      var last = JSON.parse(localStorage.getItem("sdit:resume:last") || "null");
      return last && last.path ? courseOf(last.path) : null;
    } catch (e) { return null; }
  }

  // Pick the current course and which of its days are done.
  function resolveState(progressLessons) {
    var here = location.pathname.match(LESSON_RE);
    var onLessonCourse = here ? here[1] : null;

    var byCourse = {}; // courseId -> { dayNumber: updatedAt }
    progressLessons.forEach(function (row) {
      var c = courseOf(row.lesson), n = dayOf(row.lesson);
      if (!c || !n) return;
      if (!byCourse[c]) byCourse[c] = {};
      byCourse[c][n] = row.updatedAt || "1";
    });

    // most recently worked course
    var recentCourse = null, recentTs = "";
    Object.keys(byCourse).forEach(function (c) {
      Object.keys(byCourse[c]).forEach(function (n) {
        if (byCourse[c][n] > recentTs) { recentTs = byCourse[c][n]; recentCourse = c; }
      });
    });

    var courseId = onLessonCourse || recentCourse || localLastCourse();
    var completed = (courseId && byCourse[courseId])
      ? Object.keys(byCourse[courseId]).map(Number)
      : [];
    return { courseId: courseId, completedDays: completed };
  }

  function firstCourseWithDays(courses) {
    if (courses["HUM-101"] && courses["HUM-101"].days.length) return "HUM-101";
    var ids = Object.keys(courses);
    for (var i = 0; i < ids.length; i++) if (courses[ids[i]].days.length) return ids[i];
    return null;
  }

  function el(tag, cls) { var n = document.createElement(tag); if (cls) n.className = cls; return n; }

  function render(catalog, courseId, completedDays) {
    var prior = document.querySelector(".course-strip");
    if (prior) prior.parentNode.removeChild(prior);

    var header = document.querySelector("header.masthead");
    if (!header) return;

    var courses = catalog.courses || {};
    var isEmpty = false;
    if (!courseId || !courses[courseId] || !courses[courseId].days.length) {
      courseId = firstCourseWithDays(courses);
      completedDays = [];
      isEmpty = true;
      if (!courseId) return; // nothing published yet
    }

    var course = courses[courseId];
    var planned = course.plannedDays || 15;
    var done = {};
    completedDays.forEach(function (n) { done[n] = true; });
    var completedCount = completedDays.length;

    var nextDay = null;
    for (var i = 0; i < course.days.length; i++) {
      if (!done[course.days[i].n]) { nextDay = course.days[i]; break; }
    }
    var caughtUp = !nextDay && !isEmpty;
    var pct = Math.max(0, Math.min(100, Math.round((completedCount / planned) * 100)));

    var strip = el("div", "course-strip");
    var inner = el("div", "frame course-strip-inner");

    var name = el("a", "course-strip-name");
    name.href = resolveSitePath("/courses/" + courseId + "/");
    name.innerHTML =
      '<span class="course-strip-eyebrow">' + (isEmpty ? "Start here" : "Your course") + "</span>" +
      '<span class="course-strip-title">' + esc(course.name) + "</span>";

    var prog = el("div", "course-strip-progress");
    prog.innerHTML =
      '<div class="course-bar"><span style="width:' + pct + '%"></span></div>' +
      '<span class="course-strip-count">' + completedCount + " of " + planned + " days</span>";

    var cont = el("a", "course-continue");
    if (caughtUp) {
      cont.href = resolveSitePath("/courses/" + courseId + "/");
      cont.textContent = "Course overview →";
      cont.setAttribute("title", "You're up to date on published days");
    } else {
      cont.href = resolveSitePath(nextDay.path + ".html");
      cont.textContent = (isEmpty || completedCount === 0) ? "Begin →" : "Continue →";
      cont.setAttribute("title", "Day " + nextDay.n + " — " + nextDay.title);
    }

    inner.appendChild(name);
    inner.appendChild(prog);
    inner.appendChild(cont);
    strip.appendChild(inner);
    header.parentNode.insertBefore(strip, header.nextSibling);
    document.body.classList.add("has-course-strip");
  }

  // When signed in, the nav is about your work, not the whole catalog.
  function personalizeNav() {
    var nav = document.querySelector(".masthead .toc");
    if (!nav || nav.querySelector(".nav-mine")) return;
    Array.prototype.forEach.call(
      nav.querySelectorAll("a[data-nav='curriculum'], a[data-nav='courses']"),
      function (a) { a.style.display = "none"; }
    );
    var mine = el("a", "nav-mine");
    mine.href = resolveSitePath("/index.html");
    mine.textContent = "My Courses";
    nav.insertBefore(mine, nav.firstChild);
    var browse = el("a", "nav-browse");
    browse.href = resolveSitePath("/courses/index.html");
    browse.textContent = "Browse";
    nav.insertBefore(browse, mine.nextSibling);
  }

  // Replace the marketing homepage with a personal dashboard of your courses.
  function renderHomeDashboard(catalog, progressLessons) {
    var p = location.pathname;
    if (p !== "/" && p !== "/index.html") return;
    var main = document.querySelector("main");
    if (!main) return;

    var courses = catalog.courses || {};
    var byCourse = {};
    progressLessons.forEach(function (row) {
      var c = courseOf(row.lesson), n = dayOf(row.lesson);
      if (!c || !n) return;
      if (!byCourse[c]) byCourse[c] = {};
      byCourse[c][n] = true;
    });
    var started = Object.keys(byCourse).filter(function (c) { return courses[c]; });

    function card(courseId, completed) {
      var course = courses[courseId];
      if (!course) return null;
      var planned = course.plannedDays || 15;
      var nextDay = null;
      for (var i = 0; i < course.days.length; i++) {
        if (completed.indexOf(course.days[i].n) === -1) { nextDay = course.days[i]; break; }
      }
      var pct = Math.max(0, Math.min(100, Math.round((completed.length / planned) * 100)));
      var verb = nextDay ? ((completed.length ? "Continue" : "Begin") + " →") : "Course overview →";
      var a = el("a", "my-course");
      a.href = nextDay ? resolveSitePath(nextDay.path + ".html") : resolveSitePath("/courses/" + courseId + "/");
      a.innerHTML =
        '<span class="my-course-name">' + esc(course.name) + "</span>" +
        '<span class="my-course-code">' + esc(course.code) + "</span>" +
        '<span class="course-bar"><span style="width:' + pct + '%"></span></span>' +
        '<span class="my-course-meta">' + completed.length + " of " + planned + " days · " + verb + "</span>";
      return a;
    }

    var wrap = el("div", "frame my-home");
    var eyebrow = el("p", "my-eyebrow");
    eyebrow.textContent = started.length ? "Your coursework" : "Start here";
    var h1 = el("h1", "my-title");
    h1.textContent = started.length ? "Pick up where you left off" : "Begin the Foundation";
    wrap.appendChild(eyebrow);
    wrap.appendChild(h1);

    var grid = el("div", "my-courses");
    var cards = [];
    if (started.length) {
      started.forEach(function (cid) { cards.push(card(cid, Object.keys(byCourse[cid]).map(Number))); });
    } else {
      var firstId = firstCourseWithDays(courses);
      if (firstId) cards.push(card(firstId, []));
    }
    cards.filter(Boolean).forEach(function (c) { grid.appendChild(c); });
    if (!grid.childNodes.length) return; // nothing to show — leave the page alone
    wrap.appendChild(grid);

    var browse = el("p", "my-browse");
    browse.innerHTML = '<a href="' + resolveSitePath("/courses/index.html") + '">Browse all courses →</a>';
    wrap.appendChild(browse);

    main.innerHTML = "";
    main.appendChild(wrap);
  }

  function waitForMasthead(cb) {
    var tries = 0;
    (function check() {
      if (document.querySelector("header.masthead")) return cb();
      if (tries++ > 30) return;
      setTimeout(check, 100);
    })();
  }

  function start() {
    var A = window.SDITAccount;
    if (!A || !A.configured() || !A.isSignedIn()) return;
    waitForMasthead(function () {
      personalizeNav();
      Promise.all([loadCatalog(), A.progress()]).then(function (res) {
        try {
          var state = resolveState(res[1]);
          render(res[0], state.courseId, state.completedDays);
          renderHomeDashboard(res[0], res[1]);
        } catch (e) { /* never blank the page on a rendering error */ }
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () { setTimeout(start, 150); });
  } else {
    setTimeout(start, 150);
  }
})();
