(function () {
  if (window.__sditLayoutReady) {
    return;
  }
  window.__sditLayoutReady = true;

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
    const path = window.location.pathname || "/";
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
      previousPath: previousPath,
      nextPath: nextPath,
      chapterPath: chapterPath,
      volumePath: basePath + "index.html"
    };
  }

  function buildLessonTopbar(meta, links) {
    const topbar = createElement("section", "lesson-topbar");
    const chipRow = createElement("div", "lesson-chip-row");

    [
      meta.volume.year + " / " + meta.volume.term,
      meta.volume.label + " - " + meta.volume.title,
      "Chapter " + meta.chapterNumber,
      "Day " + meta.dayNumber + " of " + meta.volume.daysPerChapter
    ].forEach(function (item) {
      chipRow.appendChild(createElement("span", "lesson-chip", item));
    });

    const nav = createElement("div", "lesson-nav");

    [
      { href: links.previousPath, label: "Previous" },
      { href: links.chapterPath, label: "Chapter" },
      { href: links.nextPath, label: "Next" }
    ].forEach(function (item) {
      const link = createElement("a", "", item.label);
      link.href = item.href;
      nav.appendChild(link);
    });

    topbar.appendChild(chipRow);
    topbar.appendChild(nav);
    return topbar;
  }

  function buildLessonSummary(meta, lessonTitle, courseName) {
    const summary = createElement("section", "lesson-card");
    summary.appendChild(createElement("p", "eyebrow", "Daily lesson"));
    summary.appendChild(createElement("h3", "", lessonTitle));

    const detail = createElement(
      "p",
      "meta",
      meta.volume.label +
        " / " +
        meta.volume.year +
        " / Chapter " +
        meta.chapterNumber +
        " / Day " +
        meta.dayNumber +
        " of " +
        meta.volume.daysPerChapter
    );
    summary.appendChild(detail);

    if (courseName) {
      summary.appendChild(createElement("p", "meta", courseName));
    }

    return summary;
  }

  function buildDayRail(meta, links) {
    const rail = createElement("section", "day-rail");
    rail.appendChild(createElement("h3", "", "Chapter flow"));

    const body = createElement(
      "p",
      "meta",
      "Move through this chapter one day at a time or jump back to the full semester map."
    );
    rail.appendChild(body);

    const grid = createElement("div", "day-rail-grid");
    for (let index = 1; index <= meta.volume.daysPerChapter; index += 1) {
      const link = createElement("a", index === meta.dayNumber ? "is-current" : "", String(index));
      link.href =
        "/programs/Bachelor-Liberal-Arts/" +
        meta.volumeSlug +
        "/schedule/chapter-" +
        pad(meta.chapterNumber) +
        "/section-" +
        pad(index) +
        ".html";
      link.setAttribute("aria-label", "Open day " + index);
      grid.appendChild(link);
    }
    rail.appendChild(grid);

    const shortcutRow = createElement("div", "lesson-nav");
    [
      { href: links.chapterPath, label: "Chapter overview" },
      { href: links.volumePath, label: "Semester map" }
    ].forEach(function (item) {
      const link = createElement("a", "", item.label);
      link.href = item.href;
      shortcutRow.appendChild(link);
    });
    rail.appendChild(shortcutRow);

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
      sidebar.appendChild(buildLessonSummary(meta, firstHeading ? firstHeading.textContent.trim() : "Daily lesson", courseName));
      sidebar.appendChild(buildDayRail(meta, links));
      const outline = buildLessonOutline(article);
      if (outline) {
        sidebar.appendChild(outline);
      }
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
    updateActiveNav();
    enhanceCardGrids();
    enhanceSectionCards();
    appendChapterToolbar();
    enhanceLessonPage();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
