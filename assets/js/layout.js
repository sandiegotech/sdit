(function () {
  if (window.__sditLayoutReady) {
    return;
  }
  window.__sditLayoutReady = true;

  function resolveSitePath(path) {
    if (typeof window.__sditResolvePath === "function") {
      return window.__sditResolvePath(path);
    }
    return path;
  }

  const volumeMeta = {
    "vol-01-foundations": {
      title: "Foundations",
      label: "Volume 1",
      year: "Year 1",
      term: "Term 1",
      chapters: 15,
      daysPerChapter: 5,
      schedulePath: "/programs/Bachelor-Liberal-Arts/vol-01-foundations/schedule/index.html",
      programPath: "/programs/Bachelor-Liberal-Arts/index.html"
    },
    "vol-02-ethics-and-reasoning": {
      title: "Ethics and Reasoning",
      label: "Volume 2",
      year: "Year 1",
      term: "Term 2",
      programPath: "/programs/Bachelor-Liberal-Arts/index.html"
    },
    "vol-03-communication-rhetoric": {
      title: "Communication and Rhetoric",
      label: "Volume 3",
      year: "Year 2",
      term: "Term 1",
      programPath: "/programs/Bachelor-Liberal-Arts/index.html"
    },
    "vol-04-science-systems": {
      title: "Science and Systems",
      label: "Volume 4",
      year: "Year 2",
      term: "Term 2",
      programPath: "/programs/Bachelor-Liberal-Arts/index.html"
    },
    "vol-05-design-creativity": {
      title: "Design and Creativity",
      label: "Volume 5",
      year: "Year 3",
      term: "Term 1",
      programPath: "/programs/Bachelor-Liberal-Arts/index.html"
    },
    "vol-06-economy-history": {
      title: "Economy and History",
      label: "Volume 6",
      year: "Year 3",
      term: "Term 2",
      programPath: "/programs/Bachelor-Liberal-Arts/index.html"
    },
    "vol-07-technology-society": {
      title: "Technology and Society",
      label: "Volume 7",
      year: "Year 4",
      term: "Term 1",
      programPath: "/programs/Bachelor-Liberal-Arts/index.html"
    },
    "vol-08-leadership-citizenship": {
      title: "Leadership and Citizenship",
      label: "Volume 8",
      year: "Year 4",
      term: "Term 2",
      programPath: "/programs/Bachelor-Liberal-Arts/index.html"
    }
  };

  function pad(value) {
    return String(value).padStart(2, "0");
  }

  function slugify(value) {
    return String(value)
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "");
  }

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

  function getVolumeSlug(pathname) {
    const match = pathname.match(/\/(vol-\d{2}-[^/]+)/);
    return match ? match[1] : null;
  }

  function getChapterNumber(pathname) {
    const match = pathname.match(/\/chapter-(\d{2})\//);
    return match ? Number(match[1]) : null;
  }

  function getDayNumber(pathname) {
    const match = pathname.match(/\/section-(\d{2})\.html$/);
    return match ? Number(match[1]) : null;
  }

  function getVolumeData(pathname) {
    const slug = getVolumeSlug(pathname);
    return slug ? volumeMeta[slug] || null : null;
  }

  function wrapAsGrid(items) {
    if (!items.length) {
      return;
    }

    const first = items[0];
    const parent = first.parentElement;
    if (!parent || parent.classList.contains("cards-grid")) {
      return;
    }

    const grid = document.createElement("div");
    grid.className = "cards-grid";
    parent.insertBefore(grid, first);

    const directChildren = Array.from(parent.children).filter(function (child) {
      return child.classList.contains("chapter-item") || child.classList.contains("section-item");
    });

    directChildren.forEach(function (child) {
      grid.appendChild(child);
    });
  }

  function enhanceCardGrids() {
    const chapterItems = Array.from(document.querySelectorAll(".chapter-item"));
    const sectionItems = Array.from(document.querySelectorAll(".section-item"));

    if (chapterItems.length) {
      wrapAsGrid(chapterItems);
    }

    if (sectionItems.length) {
      wrapAsGrid(sectionItems);
    }
  }

  function updateActiveNav() {
    const navLinks = document.querySelectorAll(".site-nav a[data-nav]");
    if (!navLinks.length) {
      return;
    }

    const path = currentPath();
    let current = "home";

    if (path.indexOf("/programs/Bachelor-Liberal-Arts/vol-01-foundations/schedule/") !== -1) {
      current = "daily";
    } else if (path.indexOf("/programs/") !== -1) {
      current = "degree";
    } else if (path.indexOf("/courses/") !== -1 || path.indexOf("/knowledge/") !== -1) {
      current = "library";
    } else if (path.indexOf("github.com/sandiegotech/sdit") !== -1) {
      current = "github";
    }

    navLinks.forEach(function (link) {
      if (link.getAttribute("data-nav") === current) {
        link.setAttribute("aria-current", "page");
      } else {
        link.removeAttribute("aria-current");
      }
    });
  }

  function bindMobileNav() {
    const header = document.querySelector(".site-header");
    const toggle = document.querySelector(".site-nav-toggle");
    const nav = document.querySelector(".site-nav");

    if (!header || !toggle || !nav || toggle.dataset.bound === "true") {
      return;
    }

    function closeNav() {
      header.classList.remove("is-nav-open");
      toggle.setAttribute("aria-expanded", "false");
    }

    function syncNavForViewport() {
      if (window.innerWidth > 760) {
        closeNav();
      }
    }

    toggle.addEventListener("click", function () {
      const isOpen = header.classList.toggle("is-nav-open");
      toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
    });

    nav.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        closeNav();
      });
    });

    window.addEventListener("resize", syncNavForViewport);
    syncNavForViewport();
    toggle.dataset.bound = "true";
  }

  function enhanceSectionCards() {
    document.querySelectorAll(".section-item").forEach(function (item, index) {
      const link = item.querySelector("a") || item;
      const strong = link.querySelector("strong");
      const sectionMeta = link.querySelector(".section-meta");
      const rawText = (strong ? strong.textContent : link.textContent || "").trim();
      const dayMatch = rawText.match(/Section\s+(\d+)/i);
      const dayValue = dayMatch ? pad(dayMatch[1]) : pad(index + 1);

      if (!link.querySelector(".day-badge")) {
        link.insertBefore(createElement("span", "day-badge", "Day " + dayValue), link.firstChild);
      }

      if (strong) {
        strong.classList.add("section-item__title");
        strong.textContent = strong.textContent.replace(/^Section/i, "Day");
      } else if (!link.querySelector(".section-item__title")) {
        const title = createElement("span", "section-item__title");
        title.textContent = rawText
          .replace(/\s+[-\u2014]\s+section-\d+\.md$/i, "")
          .replace(/^Section/i, "Day");
        link.textContent = "";
        link.appendChild(createElement("span", "day-badge", "Day " + dayValue));
        link.appendChild(title);
      }

      if (sectionMeta) {
        sectionMeta.classList.add("section-meta");
      }

      if (!link.querySelector(".section-arrow")) {
        link.appendChild(createElement("span", "section-arrow", "Open lesson"));
      }
    });
  }

  function appendChapterToolbar() {
    const path = currentPath();
    if (!/\/chapter-\d{2}\/index\.html$/.test(path)) {
      return;
    }

    document.body.classList.add("chapter-page");

    const hero = document.querySelector(".hero");
    const sectionItems = document.querySelectorAll(".section-item");
    if (!hero || !sectionItems.length || hero.querySelector(".chapter-toolbar")) {
      return;
    }

    const toolbar = createElement("div", "chapter-toolbar");
    const volumeData = getVolumeData(path);
    const chapterNumber = getChapterNumber(path);

    [
      { value: String(sectionItems.length), label: "daily lessons" },
      { value: "5", label: "course threads" },
      {
        value: volumeData ? volumeData.year : "Volume 1",
        label: volumeData ? volumeData.term : "schedule"
      }
    ].forEach(function (item) {
      const card = createElement("div", "mini-card");
      card.appendChild(createElement("strong", "", item.value));
      card.appendChild(createElement("span", "", item.label));
      toolbar.appendChild(card);
    });

    if (chapterNumber) {
      const crumb = document.querySelector(".breadcrumbs strong");
      if (crumb) {
        crumb.textContent = "Chapter " + chapterNumber;
      }
    }

    const searchInput = document.querySelector(".search-bar input");
    if (searchInput) {
      searchInput.setAttribute("placeholder", "Search days, courses, or topics");
    }

    hero.appendChild(toolbar);
  }

  function formatCourseLabel(label) {
    const text = label.textContent.trim();
    const courseText = text.replace(/^Course:\s*/i, "");
    label.textContent = "";
    label.classList.add("course-label");
    label.appendChild(createElement("strong", "", "Course"));
    label.appendChild(document.createTextNode(" " + courseText));
    return courseText;
  }

  function buildLessonLinks(volumeSlug, chapterNumber, dayNumber, chapterCount, daysPerChapter) {
    const basePath = "/programs/Bachelor-Liberal-Arts/" + volumeSlug + "/schedule/";
    const chapterPath = basePath + "chapter-" + pad(chapterNumber) + "/index.html";
    let previousPath = chapterPath;
    let nextPath = basePath + "index.html";

    if (dayNumber > 1) {
      previousPath = basePath + "chapter-" + pad(chapterNumber) + "/section-" + pad(dayNumber - 1) + ".html";
    } else if (chapterNumber > 1) {
      previousPath = basePath + "chapter-" + pad(chapterNumber - 1) + "/section-" + pad(daysPerChapter) + ".html";
    }

    if (dayNumber < daysPerChapter) {
      nextPath = basePath + "chapter-" + pad(chapterNumber) + "/section-" + pad(dayNumber + 1) + ".html";
    } else if (chapterNumber < chapterCount) {
      nextPath = basePath + "chapter-" + pad(chapterNumber + 1) + "/section-01.html";
    } else {
      nextPath = "/programs/Bachelor-Liberal-Arts/index.html";
    }

    return {
      previousPath: resolveSitePath(previousPath),
      nextPath: resolveSitePath(nextPath),
      chapterPath: resolveSitePath(chapterPath),
      volumePath: resolveSitePath(basePath + "index.html")
    };
  }

  var COURSE_URLS = {
    "LBS 101": "/courses/LBS-101-mental-gym.html",
    "LBS 105": "/courses/LBS-105-writing-communication.html",
    "LBS 110": "/courses/LBS-110-mathematics-for-modern-thinkers.html",
    "LBS 120": "/courses/LBS-120-physics-with-lab.html",
    "LAB 101": "/courses/LAB-101-creative-intelligence-lab.html"
  };

  function buildLessonTopbar(meta, links) {
    var topbar = createElement("div", "lesson-topbar");

    var pos = createElement("span", "lesson-pos",
      "Week " + meta.chapterNumber + " \u00b7 Day " + meta.dayNumber + " of " + meta.volume.daysPerChapter
    );

    var nav = createElement("div", "lesson-nav");
    var prev = createElement("a", "", "\u2190 Prev");
    prev.href = links.previousPath;
    var chap = createElement("a", "", "Week " + meta.chapterNumber);
    chap.href = links.chapterPath;
    var next = createElement("a", "", "Next \u2192");
    next.href = links.nextPath;
    nav.appendChild(prev);
    nav.appendChild(chap);
    nav.appendChild(next);

    topbar.appendChild(pos);
    topbar.appendChild(nav);
    return topbar;
  }

  function buildDayRail(meta, links) {
    var rail = createElement("section", "day-rail");

    var label = createElement("p", "day-rail-label", "Week " + meta.chapterNumber);
    rail.appendChild(label);

    var grid = createElement("div", "day-rail-grid");
    for (var i = 1; i <= meta.volume.daysPerChapter; i++) {
      var a = createElement("a", i === meta.dayNumber ? "is-current" : "", String(i));
      a.href = resolveSitePath(
        "/programs/Bachelor-Liberal-Arts/" + meta.volumeSlug +
        "/schedule/chapter-" + pad(meta.chapterNumber) +
        "/section-" + pad(i) + ".html"
      );
      a.setAttribute("aria-label", "Day " + i);
      grid.appendChild(a);
    }
    rail.appendChild(grid);

    var links2 = createElement("div", "lesson-nav");
    var ch = createElement("a", "", "Week overview");
    ch.href = links.chapterPath;
    var vol = createElement("a", "", "Full schedule");
    vol.href = links.volumePath;
    links2.appendChild(ch);
    links2.appendChild(vol);
    rail.appendChild(links2);

    return rail;
  }

  function buildLessonOutline(article) {
    const headings = Array.from(article.querySelectorAll("h2, h3")).filter(function (heading) {
      return !heading.closest(".lesson-topbar");
    });

    if (!headings.length) {
      return null;
    }

    const outline = createElement("section", "lesson-outline");
    outline.appendChild(createElement("h3", "", "On this page"));
    const list = createElement("ul", "");

    headings.forEach(function (heading) {
      if (!heading.id) {
        heading.id = slugify(heading.textContent || "section");
      }
      const item = createElement("li", "");
      const link = createElement("a", "", heading.textContent || "");
      link.href = "#" + heading.id;
      item.appendChild(link);
      list.appendChild(item);
    });

    outline.appendChild(list);
    return outline;
  }

  /* ── Lesson section map ─────────────────────────────────── */
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

  function enhanceLessonPage() {
    const path = currentPath();
    if (!/\/section-\d{2}\.html$/.test(path)) {
      return;
    }

    const volumeSlug = getVolumeSlug(path);
    const volume = getVolumeData(path);
    const chapterNumber = getChapterNumber(path);
    const dayNumber = getDayNumber(path);
    const main = document.querySelector("main");

    if (!volumeSlug || !volume || !chapterNumber || !dayNumber || !main) {
      return;
    }

    document.body.classList.add("lesson-page");

    const breadcrumbs = main.querySelector(".breadcrumbs");
    if (breadcrumbs) {
      const activeCrumb = breadcrumbs.querySelector("strong");
      if (activeCrumb) {
        activeCrumb.textContent = "Day " + dayNumber;
      }
    }

    const firstHeading = main.querySelector("h1");
    if (firstHeading && /^Section\s+/i.test(firstHeading.textContent || "")) {
      firstHeading.textContent = (firstHeading.textContent || "").replace(/^Section/i, "Day");
    }

    let courseName = "";
    const courseLabel = Array.from(main.querySelectorAll("p")).find(function (paragraph) {
      return /^Course:\s*/i.test(paragraph.textContent.trim());
    });
    if (courseLabel) {
      courseName = formatCourseLabel(courseLabel);
    }

    let shell = main.querySelector(".lesson-shell");
    let article;
    let sidebar;

    if (!shell) {
      const nodesToMove = Array.from(main.childNodes).filter(function (node) {
        return node !== breadcrumbs;
      });

      shell = createElement("div", "lesson-shell");
      article = createElement("article", "lesson-content");
      sidebar = createElement("aside", "lesson-sidebar");

      nodesToMove.forEach(function (node) {
        article.appendChild(node);
      });

      main.innerHTML = "";
      if (breadcrumbs) {
        main.appendChild(breadcrumbs);
      }
      shell.appendChild(article);
      shell.appendChild(sidebar);
      main.appendChild(shell);
    } else {
      article = shell.querySelector(".lesson-content");
      sidebar = shell.querySelector(".lesson-sidebar");
    }

    const meta = {
      volumeSlug: volumeSlug,
      volume: volume,
      chapterNumber: chapterNumber,
      dayNumber: dayNumber
    };
    const links = buildLessonLinks(
      meta.volumeSlug,
      meta.chapterNumber,
      meta.dayNumber,
      meta.volume.chapters,
      meta.volume.daysPerChapter
    );

    if (article && !article.querySelector(".lesson-topbar")) {
      article.insertBefore(buildLessonTopbar(meta, links), article.firstChild);
    }

    if (sidebar) {
      sidebar.innerHTML = "";
      sidebar.appendChild(buildDayRail(meta, links));
    }

    if (article) {
      // Inject course source link after the H1
      if (firstHeading && courseName) {
        var courseCode = courseName.split(/[\u2013\-]/)[0].trim();
        var courseUrl = COURSE_URLS[courseCode];
        var sourceEl = createElement("p", "lesson-course-source");
        var sourceText = document.createTextNode(courseName + " \u00b7 ");
        var sourceLink = createElement("a", "lesson-course-link", "View full course \u2192");
        if (courseUrl) sourceLink.href = resolveSitePath(courseUrl);
        sourceEl.appendChild(sourceText);
        sourceEl.appendChild(sourceLink);
        if (firstHeading.nextSibling) {
          article.insertBefore(sourceEl, firstHeading.nextSibling);
        } else {
          article.appendChild(sourceEl);
        }
      }
      wrapLessonSections(article);
      enhanceResourceLinks(article);
    }
  }

  function tagGenericPages() {
    const body = document.body;
    const path = currentPath();

    if (path === "/index.html") {
      body.classList.add("home-page");
    }

    if (path === "/programs/index.html") {
      body.classList.add("programs-page");
    }

    if (path === "/programs/Bachelor-Liberal-Arts/index.html") {
      body.classList.add("program-page");
    }
  }

  function boot() {
    tagGenericPages();
    bindMobileNav();
    updateActiveNav();
    enhanceCardGrids();
    enhanceSectionCards();
    appendChapterToolbar();
    enhanceLessonPage();
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
