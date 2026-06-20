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

  var SDIT = window.SDIT;
  var resolveSitePath = SDIT.resolvePath;
  var esc = SDIT.esc;
  var courseOf = SDIT.courseOf;
  var dayOf = SDIT.dayOf;
  var LESSON_RE = SDIT.LESSON_RE;
  var loadCatalog = SDIT.getCatalog;

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

    var courseId = onLessonCourse || recentCourse;
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

  // Fill the logged-in portal with a personal dashboard of your courses.
  // The portal container is already in the page and shown before paint, so
  // this never flashes the marketing home.
  function renderHomeDashboard(catalog, progressLessons, enrolled) {
    var p = location.pathname;
    if (p !== "/" && p !== "/index.html") return;
    var portal = document.getElementById("sdit-portal");
    if (!portal) return;

    var courses = catalog.courses || {};
    var byCourse = {};
    progressLessons.forEach(function (row) {
      var c = courseOf(row.lesson), n = dayOf(row.lesson);
      if (!c || !n) return;
      if (!byCourse[c]) byCourse[c] = {};
      byCourse[c][n] = true;
    });
    function doneFor(cid) { return byCourse[cid] ? Object.keys(byCourse[cid]).map(Number) : []; }

    function card(courseId, completed) {
      var course = courses[courseId];
      if (!course) return null;
      var planned = course.plannedDays || 15;
      var days = course.days || [];
      var nextDay = null;
      for (var i = 0; i < days.length; i++) {
        if (completed.indexOf(days[i].n) === -1) { nextDay = days[i]; break; }
      }
      var pct = Math.max(0, Math.min(100, Math.round((completed.length / planned) * 100)));
      var verb = nextDay ? ((completed.length ? "Continue" : "Begin") + " →")
        : (days.length ? "Course overview →" : "Coming soon");
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
    var h1 = el("h1", "my-title");
    var mine = (enrolled || []).filter(function (c) { return courses[c]; });

    if (mine.length) {
      eyebrow.textContent = "Your coursework";
      h1.textContent = "My Courses";
      wrap.appendChild(eyebrow);
      wrap.appendChild(h1);
      var grid = el("div", "my-courses");
      mine.forEach(function (cid) { var c = card(cid, doneFor(cid)); if (c) grid.appendChild(c); });
      if (grid.childNodes.length) wrap.appendChild(grid);
    } else {
      eyebrow.textContent = "My Courses";
      h1.textContent = "Add your first course";
      wrap.appendChild(eyebrow);
      wrap.appendChild(h1);
      var empty = el("p", "my-empty");
      empty.textContent = "Browse the curriculum and add courses to build your own track. Your progress then shows up here.";
      wrap.appendChild(empty);
    }

    var browse = el("p", "my-browse");
    browse.innerHTML = '<a href="' + resolveSitePath("/courses/index.html") + '">Browse all courses →</a>';
    wrap.appendChild(browse);

    portal.innerHTML = "";
    portal.appendChild(wrap);
  }

  // On the courses catalog page, let signed-in users add/remove courses.
  function enhanceCoursesPage(catalog, enrolled) {
    if (!/\/courses\/?(index\.html)?$/.test(location.pathname)) return;
    var courses = catalog.courses || {};
    var set = {};
    (enrolled || []).forEach(function (c) { set[c] = true; });

    function paint(btn, courseId) {
      var on = !!set[courseId];
      btn.textContent = on ? "✓ Added" : "+ Add";
      btn.className = "enroll-btn" + (on ? " is-enrolled" : "");
      btn.setAttribute("aria-pressed", on ? "true" : "false");
    }

    Array.prototype.forEach.call(document.querySelectorAll('a[href*="/courses/"]'), function (a) {
      var m = (a.getAttribute("href") || "").match(/\/courses\/([A-Z]+-\d+)\//);
      if (!m || !courses[m[1]]) return;
      var courseId = m[1];
      var row = a.closest("tr");
      if (!row || row.querySelector(".enroll-btn")) return;
      var btn = el("button", "enroll-btn");
      btn.type = "button";
      paint(btn, courseId);
      btn.addEventListener("click", function (e) {
        e.preventDefault();
        var A = window.SDITAccount;
        var next = !set[courseId];
        btn.disabled = true;
        (next ? A.enroll(courseId) : A.unenroll(courseId)).then(function (okk) {
          btn.disabled = false;
          if (okk) { set[courseId] = next; paint(btn, courseId); }
        });
      });
      (row.lastElementChild || row).appendChild(btn);
    });
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
      // On a lesson day page the lesson topbar already shows course + progress,
      // so the strip would be redundant — skip it there.
      var onLessonPage = /\/courses\/[A-Z]+-\d+\/day-\d{2}/.test(location.pathname);
      Promise.all([loadCatalog(), A.progress(), A.enrollments()]).then(function (res) {
        try {
          var catalog = res[0], progress = res[1], enrolled = res[2];
          if (!onLessonPage) {
            var state = resolveState(progress);
            render(catalog, state.courseId, state.completedDays);
          }
          renderHomeDashboard(catalog, progress, enrolled);
          enhanceCoursesPage(catalog, enrolled);
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
