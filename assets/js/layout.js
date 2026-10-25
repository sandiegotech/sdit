/**
 * layout.js — page chrome for the SDIT curriculum site.
 *
 * - Highlights the active masthead nav item.
 * - Course day pages (/courses/CODE/day-NN.html): wraps content in the
 *   lesson shell (topbar, day rail, sectioned content, resource cards).
 * - Course overview pages (/courses/CODE/): code badge eyebrow and
 *   sectioned content cards.
 */
(function () {
  if (window.__sditLayoutReady) {
    return;
  }
  window.__sditLayoutReady = true;

  var SDIT = window.SDIT;
  var resolveSitePath = SDIT.resolvePath;
  var pad = SDIT.pad;

  function createElement(tagName, className, text) {
    const element = document.createElement(tagName);
    if (className) {
      element.className = className;
    }
    if (typeof text === "string") {
      element.textContent = text;
    }
    return element;
  }

  function currentPath() {
    const rawPath = window.location.pathname || "/";
    const path =
      typeof window.__sditStripBasePath === "function"
        ? window.__sditStripBasePath(rawPath)
        : rawPath;
    return path === "/" ? "/index.html" : path;
  }

  /* ── Masthead nav ─────────────────────────────────────────── */

  function updateActiveNav() {
    const navLinks = document.querySelectorAll(".masthead .toc a[data-nav]");
    if (!navLinks.length) {
      return;
    }

    const path = currentPath();
    let current = "home";

    if (path.indexOf("/curriculum/schedule") !== -1 || path.indexOf("/curriculum/day-by-day") !== -1) {
      current = "schedule";
    } else if (path.indexOf("/curriculum") !== -1) {
      current = "curriculum";
    } else if (
      path.indexOf("/courses") !== -1 ||
      path.indexOf("/knowledge") !== -1
    ) {
      current = "courses";
    }

    navLinks.forEach(function (link) {
      if (link.getAttribute("data-nav") === current) {
        link.setAttribute("aria-current", "page");
      } else {
        link.removeAttribute("aria-current");
      }
    });
  }

  /* ── Lesson section map ───────────────────────────────────── */

  var SECTION_CLASS_MAP = {
    "session-focus": "is-focus",
    "learning-objectives": "is-objectives",
    "session-flow": "is-flow",
    "practice-blocks": "is-practice",
    "key-quote-box": "is-quote",
    "hard-problem-optional": "is-challenge",
    "notes": "is-notes"
  };

  function getSectionClass(h2) {
    var id = (h2.id || "").toLowerCase();
    if (SECTION_CLASS_MAP[id]) return SECTION_CLASS_MAP[id];
    var text = (h2.textContent || "").toLowerCase();
    if (/focus|overview/.test(text)) return "is-focus";
    if (/objective/.test(text)) return "is-objectives";
    if (/flow|session/.test(text)) return "is-flow";
    if (/practice|exercise/.test(text)) return "is-practice";
    if (/quote/.test(text)) return "is-quote";
    if (/hard|optional/.test(text)) return "is-challenge";
    if (/note/.test(text)) return "is-notes";
    return "is-default";
  }

  function wrapLessonSections(article) {
    var children = Array.from(article.children);
    var currentSection = null;

    children.forEach(function (child) {
      if (child.classList.contains("lesson-topbar") || child.tagName === "H1") {
        currentSection = null;
        return;
      }
      if (child.tagName === "H2") {
        var sClass = getSectionClass(child);
        var section = createElement("div", "lesson-section " + sClass);
        article.insertBefore(section, child);
        section.appendChild(child);
        currentSection = section;
        return;
      }
      if (currentSection) currentSection.appendChild(child);
    });

    var flowSection = article.querySelector(".lesson-section.is-flow");
    if (flowSection) wrapFlowSteps(flowSection);

    var practiceSection = article.querySelector(".lesson-section.is-practice");
    if (practiceSection) wrapPromptCards(practiceSection);

    var objSection = article.querySelector(".lesson-section.is-objectives");
    if (objSection) {
      var ul = objSection.querySelector("ul");
      if (ul) makeChecklist(ul);
    }
  }

  function wrapFlowSteps(section) {
    var children = Array.from(section.children);
    var h2 = section.querySelector("h2");
    var currentStep = null;

    children.forEach(function (child) {
      if (child === h2) return;
      if (child.tagName === "H3") {
        var text = (child.textContent || "").toLowerCase();
        var stepClass = "flow-step";
        if (/read/.test(text)) stepClass += " flow-step--read";
        else if (/watch/.test(text)) stepClass += " flow-step--watch";
        else if (/listen/.test(text)) stepClass += " flow-step--listen";
        else if (/reflect/.test(text)) stepClass += " flow-step--reflect";
        else stepClass += " flow-step--intro";
        var step = createElement("div", stepClass);
        section.insertBefore(step, child);
        step.appendChild(child);
        currentStep = step;
        return;
      }
      if (currentStep) currentStep.appendChild(child);
    });
  }

  function wrapPromptCards(section) {
    var children = Array.from(section.children);
    var h2 = section.querySelector("h2");
    var currentCard = null;

    children.forEach(function (child) {
      if (child === h2) return;
      if (child.tagName === "H3") {
        var card = createElement("div", "prompt-card");
        section.insertBefore(card, child);
        card.appendChild(child);
        currentCard = card;
        return;
      }
      if (currentCard) currentCard.appendChild(child);
    });
  }

  function makeChecklist(ul) {
    ul.classList.add("lesson-checklist");
    Array.from(ul.querySelectorAll("li")).forEach(function (li) {
      var text = li.textContent.trim();
      li.innerHTML = "";
      var label = document.createElement("label");
      var checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      label.appendChild(checkbox);
      label.appendChild(document.createTextNode(" " + text));
      li.appendChild(label);
    });
  }

  /* ── Resource cards (Read / Watch / Listen links) ─────────── */

  function getYouTubeID(url) {
    var match = (url || "").match(/[?&]v=([^&]+)/) || (url || "").match(/youtu\.be\/([^?&]+)/);
    return match ? match[1] : null;
  }

  function buildResourceCard(title, linkText, href, parent, insertBeforeEl) {
    var ytId = getYouTubeID(href);
    var card = document.createElement("div");
    card.className = "resource-link-card" + (ytId ? " resource-link-card--video" : "");

    var icon = createElement("span", "resource-link-icon", ytId ? "▶" : "↗");
    var body = createElement("div", "resource-link-body");
    var titleEl = createElement("strong", "resource-link-title", title);
    var sub = document.createElement("a");
    sub.className = "resource-link-sub";
    sub.href = href;
    sub.target = "_blank";
    sub.rel = "noopener noreferrer";
    sub.textContent = linkText;
    body.appendChild(titleEl);
    body.appendChild(sub);
    card.appendChild(icon);
    card.appendChild(body);

    if (insertBeforeEl) {
      parent.insertBefore(card, insertBeforeEl);
    } else {
      parent.appendChild(card);
    }

    if (ytId) {
      var embedWrapper = document.createElement("div");
      embedWrapper.className = "lesson-embed";
      var iframe = document.createElement("iframe");
      iframe.src = "https://www.youtube.com/embed/" + ytId;
      iframe.setAttribute("frameborder", "0");
      iframe.setAttribute("allowfullscreen", "");
      iframe.setAttribute("allow", "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture");
      iframe.setAttribute("loading", "lazy");
      embedWrapper.appendChild(iframe);
      card.parentNode.insertBefore(embedWrapper, card.nextSibling);
    }
  }

  function enhanceResourceLinks(article) {
    var flowSection = article.querySelector(".lesson-section.is-flow");
    if (!flowSection) return;

    // Handle <p> elements with strong + a (Read / Listen sections)
    Array.from(flowSection.querySelectorAll(".flow-step p")).forEach(function (p) {
      var strong = p.querySelector("strong");
      var link = p.querySelector("a");
      if (!strong || !link) return;
      var parent = p.parentNode;
      buildResourceCard(strong.textContent.trim(), link.textContent.trim(), link.href, parent, p);
      parent.removeChild(p);
    });

    // Handle <li> elements with strong + a (Watch sections with ul lists)
    Array.from(flowSection.querySelectorAll(".flow-step li")).forEach(function (li) {
      var p = li.querySelector("p") || li;
      var strong = p.querySelector("strong");
      var link = p.querySelector("a");
      if (!strong || !link) return;
      var ul = li.closest("ul");
      var insertParent = ul ? ul.parentNode : li.parentNode;
      var insertBefore = ul ? ul.nextSibling : li.nextSibling;
      buildResourceCard(strong.textContent.trim(), link.textContent.trim(), link.href, insertParent, insertBefore);
      li.parentNode && li.parentNode.removeChild(li);
    });

    // Clean up empty uls
    Array.from(flowSection.querySelectorAll("ul")).forEach(function (ul) {
      if (!ul.querySelector("li")) ul.parentNode && ul.parentNode.removeChild(ul);
    });
  }

  /* ── Course day pages (/courses/CODE/day-NN.html) ─────────── */

  var fetchCatalog = SDIT.getCatalog;

  function enhanceCourseLessonPage(path) {
    var courseId  = SDIT.courseOf(path);
    var dayNumber = SDIT.dayOf(path) || 0;
    if (!courseId || !dayNumber) return;

    document.body.classList.add("lesson-page");

    var main = document.querySelector("main");
    if (!main) return;

    // Wrap content into the lesson shell
    var nodesToMove = Array.from(main.childNodes);
    var shell   = createElement("div", "lesson-shell");
    var article = createElement("article", "lesson-content");
    var sidebar = createElement("aside", "lesson-sidebar");
    nodesToMove.forEach(function (n) { article.appendChild(n); });
    main.innerHTML = "";
    shell.appendChild(article);
    shell.appendChild(sidebar);
    main.appendChild(shell);

    wrapLessonSections(article);
    enhanceResourceLinks(article);

    // The topbar and rail are driven by the catalog, so they only ever point
    // at days that actually exist — no broken links to unpublished days.
    fetchCatalog().then(function (catalog) {
      buildLessonChrome(article, sidebar, catalog, courseId, dayNumber);
    });
  }

  function buildLessonChrome(article, sidebar, catalog, courseId, dayNumber) {
    var course  = (catalog.courses || {})[courseId] || {};
    var days    = course.days || [];                 // published: [{n, path, title}]
    var planned = course.plannedDays || (days.length || 1);
    var pub = {};
    days.forEach(function (d) { pub[d.n] = d; });
    var lastN = Math.max(planned, days.length ? days[days.length - 1].n : 0);

    function dayHref(n) { return resolveSitePath("/courses/" + courseId + "/day-" + pad(n) + ".html"); }
    function overviewHref() { return resolveSitePath("/courses/" + courseId + "/"); }

    // Nearest published neighbours (skip any gaps)
    var prevN = null, nextN = null;
    for (var p = dayNumber - 1; p >= 1; p--) { if (pub[p]) { prevN = p; break; } }
    for (var x = dayNumber + 1; x <= lastN; x++) { if (pub[x]) { nextN = x; break; } }

    // ── Topbar ──
    var topbar = createElement("div", "lesson-topbar");
    topbar.appendChild(createElement("span", "lesson-pos",
      courseId + " · Day " + dayNumber + " of " + planned));
    var topNav = createElement("div", "lesson-nav");
    if (prevN) {
      var pa = createElement("a", "", "← Day " + prevN);
      pa.href = dayHref(prevN);
      topNav.appendChild(pa);
    }
    var cLink = createElement("a", "", "Overview");
    cLink.href = overviewHref();
    topNav.appendChild(cLink);
    if (nextN) {
      var na = createElement("a", "", "Day " + nextN + " →");
      na.href = dayHref(nextN);
      topNav.appendChild(na);
    }
    topbar.appendChild(topNav);
    article.insertBefore(topbar, article.firstChild);

    // ── Day rail: published days are links; planned-but-unpublished are locked ──
    var rail = createElement("section", "day-rail");
    rail.appendChild(createElement("p", "day-rail-label", courseId));
    var railGrid = createElement("div", "day-rail-grid");
    for (var i = 1; i <= lastN; i++) {
      if (pub[i]) {
        var a = createElement("a", i === dayNumber ? "is-current" : "", String(i));
        a.href = dayHref(i);
        a.setAttribute("aria-label", "Day " + i + (pub[i].title ? " — " + pub[i].title : ""));
        railGrid.appendChild(a);
      } else {
        var s = createElement("span", "is-locked", String(i));
        s.setAttribute("aria-label", "Day " + i + " — coming soon");
        railGrid.appendChild(s);
      }
    }
    rail.appendChild(railGrid);
    var railLinks = createElement("div", "lesson-nav");
    var overviewLink = createElement("a", "", "Course overview");
    overviewLink.href = overviewHref();
    railLinks.appendChild(overviewLink);
    rail.appendChild(railLinks);
    sidebar.appendChild(rail);
  }

  function enhanceLessonPage() {
    const path = currentPath();
    if (/\/courses\/[A-Z]+-\d+\/day-\d{2}(\.html)?$/.test(path)) {
      enhanceCourseLessonPage(path);
    }
  }

  /* ── Course overview pages (/courses/CODE/) ───────────────── */

  function getCourseCodeFromPath(pathname) {
    var m = pathname.match(/\/courses\/([A-Z]+-\d+)(\/|$)/);
    return m ? m[1] : null;
  }

  function getCourseCategory(code) {
    var prefix = (code || "").split("-")[0];
    var cats = {
      "HUM": "The Canon",
      "MATH": "Mathematics & Science",
      "PHYS": "Mathematics & Science",
      "CS": "Computation",
      "RHET": "Rhetoric & Epistemics",
      "SIG": "Culture & Signal",
      "WKSP": "The Workshop",
      "ART": "Depth Studio",
      "ENGR": "Depth Studio",
      "FLD": "Field Term",
      "CAP": "Capstone"
    };
    return cats[prefix] || "Course";
  }

  function enhanceCoursePage() {
    var path = currentPath();
    if (path.indexOf("/courses/") === -1) return;
    // Allow /courses/CODE/ but exclude the top-level catalog page
    if (/^\/courses\/(index(\.html)?)?$/.test(path)) return;
    // Exclude day pages — those are handled by enhanceCourseLessonPage
    if (/\/day-\d{2}(\.html)?$/.test(path)) return;

    document.body.classList.add("course-page");

    var code = getCourseCodeFromPath(path);
    var main = document.querySelector("main");
    var h1 = main && main.querySelector("h1");
    if (!h1 || !code) return;

    // Inject eyebrow with code badge + thread
    var eyebrow = createElement("div", "course-eyebrow");
    eyebrow.appendChild(createElement("span", "course-code-badge", code));
    eyebrow.appendChild(createElement("span", "course-category", getCourseCategory(code)));
    h1.parentNode.insertBefore(eyebrow, h1);

    // Strip course code prefix from H1 if present ("CS 110 — Title" → "Title")
    var h1Text = h1.textContent || "";
    var titleMatch = h1Text.match(/^[A-Z]+[\s-]\d+\s*[—\-]\s*(.+)$/);
    if (titleMatch) h1.textContent = titleMatch[1];

    // Wrap H2 sections into course-section cards
    var children = Array.from(main.children);
    var currentSection = null;
    children.forEach(function (child) {
      if (child === eyebrow || child.tagName === "H1") {
        currentSection = null;
        return;
      }
      if (child.tagName === "H2") {
        var section = createElement("div", "course-section");
        main.insertBefore(section, child);
        section.appendChild(child);
        currentSection = section;
        return;
      }
      if (currentSection) currentSection.appendChild(child);
    });
  }

  /* ── Boot ─────────────────────────────────────────────────── */

  function boot() {
    updateActiveNav();
    enhanceLessonPage();
    enhanceCoursePage();
    if (typeof window.__sditRewritePaths === "function") {
      window.__sditRewritePaths(document.body);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
