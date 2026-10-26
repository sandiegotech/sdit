/**
 * portfolio.js — the learner's Portfolio, assembled in the browser.
 *
 * Reads the degree map embedded in the page (#degree-map, built by
 * scripts/portfolio.py) and the learner's own answers: from this device
 * (localStorage "sdit:<lesson>::<heading>", with "…@t" timestamps) and, when
 * signed in, from the account (GET /work/all). Renders one of three editions:
 *
 *   Short      the judging document: who this is, then one page per course's
 *              highlight (the work itself, large), the capstone, the Question
 *              across the years, the outcomes
 *   Volumes    one book per semester: each course opens with its highlight and
 *              the day answers sit behind it; then the gate and the Question
 *              as it stood
 *   Expanded   every volume, in order
 *
 * The files behind a highlight (photos, a film, a deck, an essay) live in the
 * account's work bucket. A record keeps their keys; this page asks the API
 * for signed links to show them. A published snapshot carries site URLs
 * instead (/work/p/...), written by the server when the edition went public.
 *
 * Print uses the print stylesheet; downloads are built here as files.
 */
(function () {
  "use strict";

  var ROMAN = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII"];
  var MAP, ANSWERS = {}, SOURCE = "this device", PROFILE = null;
  var state = { edition: "short", volume: 1, name: "", about: "" };
  var FILE_URLS = {};      // key -> signed link (own mode)
  var TEXTS = {};          // url -> fetched text (essays)

  // ── Utilities ──────────────────────────────────────────────────────────────

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function paras(text) {
    return String(text || "").split(/\n{2,}/).map(function (p) {
      return "<p>" + esc(p).replace(/\n/g, "<br>") + "</p>";
    }).join("");
  }
  function dateOf(iso) {
    if (!iso) return "";
    var d = new Date(iso.length <= 10 ? iso + "T12:00:00" : iso);
    if (isNaN(d)) return "";
    return d.toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric" });
  }
  function k(lesson, heading) { return lesson + "::" + heading; }
  function get(lesson, heading) { return ANSWERS[k(lesson, heading)] || null; }
  function pad(n) { return String(n).padStart(2, "0"); }
  function dayLesson(dir, n) { return "/courses/" + dir + "/day-" + pad(n); }
  function fmtSize(n) {
    if (!n) return "";
    if (n < 1024 * 1024) return Math.max(1, Math.round(n / 1024)) + " KB";
    return (n / (1024 * 1024)).toFixed(n < 10 * 1024 * 1024 ? 1 : 0) + " MB";
  }

  function waitFor(test, ms) {
    return new Promise(function (resolve) {
      var t0 = Date.now();
      (function poll() {
        if (test() || Date.now() - t0 > ms) return resolve();
        setTimeout(poll, 50);
      })();
    });
  }

  // ── Gathering the answers ──────────────────────────────────────────────────

  function readLocal() {
    var out = {};
    try {
      for (var i = 0; i < localStorage.length; i++) {
        var key = localStorage.key(i);
        if (!key || key.indexOf("sdit:") !== 0 || /@t$/.test(key)) continue;
        var rest = key.slice(5), cut = rest.lastIndexOf("::");
        if (cut < 0) continue;
        var lesson = rest.slice(0, cut), heading = rest.slice(cut + 2);
        var content = localStorage.getItem(key);
        if (!content || !content.trim()) continue;
        out[k(lesson, heading)] = { lesson: lesson, heading: heading, content: content,
                                    at: localStorage.getItem(key + "@t") || null };
      }
    } catch (e) {}
    return out;
  }

  function gather() {
    ANSWERS = readLocal();
    var acct = window.SDITAccount && window.SDITAccount.isSignedIn() ? window.SDITAccount : null;
    if (!acct || !acct.allWork) return Promise.resolve();
    PROFILE = acct.profile();
    return acct.allWork().then(function (rows) {
      if (rows === null) { SOURCE = "this device (your account could not be reached)"; return; }
      SOURCE = "your account and this device";
      rows.forEach(function (r) {
        if (!r.content || !String(r.content).trim()) return;
        var key = k(r.lesson, r.heading), mine = ANSWERS[key];
        // The newer of the two wins; an undated local copy yields to the account.
        if (!mine || !mine.at || (r.updatedAt && r.updatedAt > mine.at)) {
          ANSWERS[key] = { lesson: r.lesson, heading: r.heading, content: r.content, at: r.updatedAt };
        }
      });
      var about = get("/portfolio", "about"), name = get("/portfolio", "name");
      if (about && !state.about) state.about = about.content;
      if (name && !state.name) state.name = name.content;
    });
  }

  // Signed links for the files behind the highlights (own mode only; public
  // snapshots already carry site URLs).
  function resolveFiles() {
    var acct = window.SDITAccount && window.SDITAccount.isSignedIn() ? window.SDITAccount : null;
    if (!acct || !acct.request) return Promise.resolve();
    var keys = [];
    madeThings().forEach(function (m) {
      (m.rec.files || []).forEach(function (f) { if (f.key && !f.url && !FILE_URLS[f.key]) keys.push(f.key); });
    });
    if (!keys.length) return Promise.resolve();
    return acct.request("/work/file-urls", { method: "POST", body: { keys: keys } }).then(function (d) {
      Object.keys(d.urls || {}).forEach(function (key) { FILE_URLS[key] = d.urls[key]; });
    }, function () {});
  }

  function fileUrl(f) { return f.url || FILE_URLS[f.key] || ""; }

  // ── Reading the store as the degree ────────────────────────────────────────

  function commitment() {
    var c = get("/begin", "commitment");
    return c ? c.content : null;
  }

  // Every answer to the Question, Day 0 through the gates, in order.
  function theQuestion(upTo) {
    var rows = [];
    var b = get(MAP.begin.lesson, "education");
    if (b) rows.push({ where: "Day 0", a: b });
    MAP.gates.forEach(function (g) {
      if (upTo && g.n > upTo) return;
      var x = get(g.lesson, "education");
      if (x) rows.push({ where: "Gate · Semester " + g.n, a: x });
    });
    return rows;
  }

  function madeOf(dir) {
    var r = get("/courses/" + dir + "/made", "made-thing");
    if (!r) return null;
    var rec;
    try { rec = JSON.parse(r.content); } catch (e) { return null; }
    if (!rec || !(rec.title || rec.words || rec.link || (rec.files && rec.files.length))) return null;
    rec.files = Array.isArray(rec.files) ? rec.files.filter(function (f) { return f && (f.url || f.key); }) : [];
    var c = MAP.courses[dir];
    return { dir: dir, course: c, rec: rec, at: r.at, days: semesterDays(c.semester, dir) };
  }

  function madeThings(semester) {
    var out = [];
    Object.keys(MAP.courses).forEach(function (dir) {
      var c = MAP.courses[dir];
      if (semester && c.semester !== semester) return;
      var m = madeOf(dir);
      if (m) out.push(m);
    });
    out.sort(function (a, b) {
      return (a.course.semester - b.course.semester) || (a.course.code < b.course.code ? -1 : 1);
    });
    return out;
  }

  function semesterDays(semester, dir) {
    return MAP.days.filter(function (d) { return d[0] === semester && (!dir || d[3] === dir); }).map(function (d) {
      return { s: d[0], w: d[1], label: d[2], dir: d[3], n: d[4], title: d[5], q: d[6],
               a: get(dayLesson(d[3], d[4]), "answer") };
    }).filter(function (d) { return d.a; });
  }

  // The semester's courses in the order the week meets them, each with its
  // highlight and its day answers; only courses with something in them.
  function semesterCourses(semester) {
    var order = [], seen = {};
    MAP.days.forEach(function (d) { if (d[0] === semester && !seen[d[3]]) { seen[d[3]] = true; order.push(d[3]); } });
    Object.keys(MAP.courses).forEach(function (dir) {
      if (MAP.courses[dir].semester === semester && !seen[dir]) { seen[dir] = true; order.push(dir); }
    });
    return order.map(function (dir) {
      return { dir: dir, course: MAP.courses[dir], made: madeOf(dir), days: semesterDays(semester, dir) };
    }).filter(function (c) { return c.made || c.days.length; });
  }

  function countAll() {
    return Object.keys(ANSWERS).filter(function (key) { return ANSWERS[key].lesson !== "/portfolio"; }).length;
  }

  // ── Rendering ──────────────────────────────────────────────────────────────

  function titlePage(subtitle) {
    var name = state.name || (PROFILE && PROFILE.email) || "";
    var dates = Object.keys(ANSWERS).map(function (key) { return ANSWERS[key].at; }).filter(Boolean).sort();
    var span = dates.length ? dateOf(dates[0]) + " — " + dateOf(dates[dates.length - 1]) : "";
    return '<section class="pf-page pf-title">' +
      '<p class="pf-eyebrow">San Diego Institute of Technology</p>' +
      "<h2>The Portfolio" + (name ? '<span class="pf-of">of ' + esc(name) + "</span>" : "") + "</h2>" +
      '<p class="pf-sub">' + esc(subtitle) + "</p>" +
      (span ? '<p class="pf-span">' + esc(span) + "</p>" : "") +
      "</section>";
  }

  // Who this is: the statement written on the Portfolio page, and the Commitment.
  function aboutPage(isPublic) {
    var c = commitment();
    var about = (state.about || "").trim();
    if (!about && !c) return "";
    var body = about ? '<div class="pf-about">' + paras(about) + "</div>" :
      (isPublic ? "" : '<p class="pf-empty">A few lines about who you are and what you want your work to say. Write them in "About you" above; they open the Portfolio.</p>');
    return '<section class="pf-page pf-who"><p class="pf-eyebrow">Who this is</p>' +
      (state.name ? "<h3>" + esc(state.name) + "</h3>" : "") + body +
      (c ? '<p class="pf-commit">Committed to the four years on ' + esc(dateOf(c)) + ".</p>" : "") +
      "</section>";
  }

  // The Question across the years. Compact: the first and latest answers in
  // full voice, the ones between in a quieter list, so the change reads at a
  // glance without taking the front of the book.
  function questionSection(upTo, title, compact) {
    var rows = theQuestion(upTo);
    var body;
    if (!rows.length) {
      body = '<p class="pf-empty">Not answered yet. It is the first question on <a href="/begin/">Day 0</a>.</p>';
    } else if (compact && rows.length > 2) {
      var first = rows[0], last = rows[rows.length - 1], mid = rows.slice(1, -1);
      body = qRow(first) +
        '<div class="pf-q-between"><p class="pf-q-when">Between</p>' +
        mid.map(function (r) {
          return '<p class="pf-q-mid"><span class="pf-q-where">' + esc(r.where) + (r.a.at ? " · " + esc(dateOf(r.a.at)) : "") + "</span> " + esc(r.a.content) + "</p>";
        }).join("") + "</div>" + qRow(last);
    } else {
      body = rows.map(qRow).join("");
    }
    return '<section class="pf-page pf-question"><p class="pf-eyebrow">' + esc(title || "The Question") + "</p>" +
      "<h3>" + esc(MAP.question) + "</h3>" + body + "</section>";
  }
  function qRow(r) {
    return '<div class="pf-q-row"><p class="pf-q-when">' + esc(r.where) +
      (r.a.at ? " · " + esc(dateOf(r.a.at)) : "") + "</p>" +
      '<blockquote class="pf-q-answer">' + paras(r.a.content) + "</blockquote></div>";
  }

  // ── The work itself ────────────────────────────────────────────────────────

  var KIND_WORD = { image: "photo", video: "film", audio: "recording", pdf: "pages", text: "text" };

  function mediaHtml(f, big) {
    var url = fileUrl(f), name = esc(f.name || "");
    if (!url) return '<div class="pf-media pf-media--pending">' + name + "</div>";
    var u = esc(url);
    if (f.kind === "image") {
      return '<figure class="pf-media pf-media--image' + (big ? " is-big" : "") + '"><img src="' + u + '" alt="' + name + '" loading="lazy"></figure>';
    }
    if (f.kind === "video") {
      return '<figure class="pf-media pf-media--video"><video controls preload="metadata" playsinline src="' + u + '"' +
        (f.poster ? ' poster="' + esc(f.poster) + '"' : "") + "></video></figure>";
    }
    if (f.kind === "audio") {
      return '<figure class="pf-media pf-media--audio"><audio controls preload="metadata" src="' + u + '"></audio><figcaption>' + name + "</figcaption></figure>";
    }
    if (f.kind === "pdf") {
      return '<figure class="pf-media pf-media--pdf">' +
        (big ? '<iframe src="' + u + '#toolbar=0&view=FitH" title="' + name + '" loading="lazy"></iframe>' : "") +
        '<figcaption><a href="' + u + '" target="_blank" rel="noopener">Open ' + name + "</a>" + (f.size ? " · " + fmtSize(f.size) : "") + "</figcaption></figure>";
    }
    if (f.kind === "text") {
      var t = TEXTS[url];
      return '<div class="pf-media pf-media--text" data-pf-text="' + u + '">' +
        (t == null ? '<p class="pf-empty">Reading ' + name + "…</p>" : textHtml(t)) +
        '<p class="pf-media-foot"><a href="' + u + '" target="_blank" rel="noopener">' + name + "</a></p></div>";
    }
    return '<p class="pf-link"><a href="' + u + '" target="_blank" rel="noopener">' + name + "</a></p>";
  }

  // Plain text or light markdown: headings, paragraphs, emphasis. Nothing else.
  function textHtml(t) {
    var out = [];
    String(t).replace(/\r/g, "").split(/\n{2,}/).forEach(function (block) {
      block = block.trim();
      if (!block) return;
      var h = block.match(/^(#{1,3})\s+(.*)$/);
      if (h) { out.push("<h" + (h[1].length + 3) + ">" + inline(h[2]) + "</h" + (h[1].length + 3) + ">"); return; }
      if (/^---+$/.test(block)) { out.push("<hr>"); return; }
      out.push("<p>" + inline(block).replace(/\n/g, "<br>") + "</p>");
    });
    return out.join("");
  }
  function inline(s) {
    return esc(s).replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>").replace(/(^|[^*])\*(?!\s)(.+?)\*(?!\*)/g, "$1<em>$2</em>");
  }

  function fillTexts() {
    Array.prototype.forEach.call(document.querySelectorAll("[data-pf-text]"), function (box) {
      var url = box.getAttribute("data-pf-text");
      if (TEXTS[url] != null) return;
      fetch(url).then(function (r) { return r.ok ? r.text() : ""; }).then(function (t) {
        TEXTS[url] = t;
        var foot = box.querySelector(".pf-media-foot");
        box.innerHTML = textHtml(t) + (foot ? foot.outerHTML : "");
      }).catch(function () { TEXTS[url] = ""; });
    });
  }

  // The course's highlight: the cover large, the rest smaller, then the words.
  function highlight(m, opts) {
    opts = opts || {};
    var r = m.rec, c = m.course;
    var files = r.files || [];
    var cover = files[0], rest = files.slice(1);
    var media = "";
    if (cover) media += mediaHtml(cover, true);
    if (rest.length) {
      media += '<div class="pf-gallery">' + rest.map(function (f) {
        return f.kind === "image" ? mediaHtml(f, false) :
          '<p class="pf-file"><a href="' + esc(fileUrl(f)) + '" target="_blank" rel="noopener">' + esc(f.name) + "</a>" +
          ' <span class="pf-file-kind">' + (KIND_WORD[f.kind] || "file") + (f.size ? " · " + fmtSize(f.size) : "") + "</span></p>";
      }).join("") + "</div>";
    }
    // The way deeper: this course's days, in its Volume. In a published Short
    // Edition the days are not in the snapshot, so the link stands only when
    // that Volume is published too.
    var more = "";
    if (opts.deeper) {
      var n = m.days ? m.days.length : 0;
      var vol = "volume-" + c.semester;
      if (n && !PUBLIC) more = n + " day" + (n === 1 ? "" : "s") + " of answers from this course, in Volume " + ROMAN[c.semester];
      else if (PUBLIC && PUBLIC.editions && PUBLIC.editions[vol]) more = "The days from this course, in Volume " + ROMAN[c.semester];
      if (more) more = '<p class="pf-deeper"><a href="#course-' + esc(m.dir) + '">' + more + " →</a></p>";
    }
    return '<section class="' + (opts.onePage ? "pf-page " : "") + 'pf-made pf-highlight"' + (opts.id ? ' id="' + esc(opts.id) + '"' : "") + ">" +
      '<p class="pf-eyebrow">' + esc(opts.eyebrow || (c.code + " · " + c.name + " · Semester " + c.semester)) + "</p>" +
      "<h3>" + esc(r.title || "Untitled") + "</h3>" +
      '<p class="pf-meta">' + esc(r.form || "") +
        (r.date ? " · defended or shown " + esc(dateOf(r.date)) : "") +
        (r.level ? " · " + esc(r.level) : "") + "</p>" +
      media +
      (r.words ? '<div class="pf-words">' + paras(r.words) + "</div>" : "") +
      (r.applied ? '<div class="pf-applied"><p class="pf-q-when">Where it went</p>' + paras(r.applied) + "</div>" : "") +
      (r.link ? '<p class="pf-link"><a href="' + esc(r.link) + '" rel="noopener">' + esc(r.link) + "</a></p>" : "") +
      '<p class="pf-evidence">Evidence of: ' + esc(c.outcomes.join(" · ")) + "</p>" +
      (c.fundamentals && c.fundamentals.length ? '<p class="pf-evidence pf-fundamentals">Fundamentals shown: ' + esc(c.fundamentals.join(" · ")) + "</p>" : "") + more +
      "</section>";
  }

  function daysHtml(days) {
    var parts = [], week = 0;
    days.forEach(function (d) {
      if (d.w !== week) { week = d.w; parts.push('<p class="pf-week">Week ' + week + "</p>"); }
      var c = MAP.courses[d.dir] || {};
      parts.push('<article class="pf-day"><p class="pf-day-head">' + esc(d.label ? d.label + " · " : "") +
        esc(c.code || d.dir) + " · Day " + d.n + (d.a.at ? " · " + esc(dateOf(d.a.at)) : "") + "</p>" +
        "<h4>" + esc(d.title) + "</h4>" +
        '<p class="pf-day-q">' + esc(d.q) + "</p>" +
        '<div class="pf-day-a">' + paras(d.a.content) + "</div></article>");
    });
    return parts.join("");
  }

  // One course inside a volume: the highlight first, the days behind it.
  function courseSection(cs) {
    var c = cs.course;
    var head = '<section class="pf-course" id="course-' + esc(cs.dir) + '">' +
      '<p class="pf-eyebrow">' + esc(c.code) + " · " + esc(c.name) + "</p>";
    var body = "";
    if (cs.made) body += highlight(cs.made, { eyebrow: "The highlight" });
    else body += '<p class="pf-empty pf-no-highlight">No highlight recorded for this course yet. Its course page has the place for one.</p>';
    if (cs.days.length) {
      body += '<details class="pf-days" open><summary>The days · ' + cs.days.length + " answer" + (cs.days.length === 1 ? "" : "s") + "</summary>" +
        daysHtml(cs.days) + "</details>";
    }
    return head + body + "</section>";
  }

  function gateBlock(n) {
    var g = MAP.gates[n - 1];
    var rows = g.questions.map(function (q) {
      var a = get(g.lesson, q.id);
      return a ? '<div class="pf-qa"><p class="pf-qa-q">' + esc(q.text) + "</p>" +
        '<div class="pf-qa-a">' + paras(a.content) + "</div></div>" : "";
    }).join("");
    return rows ? '<section class="pf-block pf-gate"><p class="pf-eyebrow">The Gate · end of Semester ' + n + '</p><h3>What stood at the end</h3>' + rows + "</section>" : "";
  }

  function dayZeroBlock() {
    var rows = MAP.begin.questions.map(function (q) {
      var a = get(MAP.begin.lesson, q.id);
      return a ? '<div class="pf-qa"><p class="pf-qa-q">' + esc(q.text) + "</p>" +
        '<div class="pf-qa-a">' + paras(a.content) + "</div></div>" : "";
    }).join("");
    return rows ? '<section class="pf-block"><h3>Day 0</h3>' + rows + "</section>" : "";
  }

  function commitmentBlock() {
    var c = commitment();
    if (!c) return "";
    return '<section class="pf-block"><h3>The Commitment</h3>' +
      "<p>Committed on " + esc(dateOf(c)) + ".</p></section>";
  }

  function volume(n) {
    var sem = MAP.semesters[n - 1];
    var courses = semesterCourses(n);
    var gate = gateBlock(n);
    var parts = [];
    parts.push('<section class="pf-page pf-volume-title"><p class="pf-eyebrow">Volume ' + ROMAN[n] + "</p>" +
               "<h2>" + esc(sem.label) + "</h2><p class=\"pf-sub\">Semester " + n + "</p></section>");
    if (n === 1) { parts.push(commitmentBlock()); parts.push(dayZeroBlock()); }
    courses.forEach(function (cs) { parts.push(courseSection(cs)); });
    parts.push(gate);
    if (theQuestion(n).length) parts.push(questionSection(n, "The Question, as it stood at the end of Semester " + n, true));
    if (!gate && !courses.length && n !== 1) {
      parts.push('<p class="pf-empty">Nothing written in this semester yet.</p>');
    }
    return '<div class="pf-volume">' + parts.join("") + "</div>";
  }

  function volumeHasContent(n) {
    return semesterCourses(n).length || gateBlock(n) || (n === 1 && (commitment() || dayZeroBlock()));
  }

  function shortEdition(isPublic) {
    var made = madeThings();
    var cap = made.filter(function (m) { return /^CAP-/.test(m.dir); });
    var rest = made.filter(function (m) { return !/^CAP-/.test(m.dir); });
    var out = [titlePage("The Short Edition"), aboutPage(isPublic)];
    if (rest.length) {
      out.push('<section class="pf-page pf-block pf-divider"><p class="pf-eyebrow">The work</p><h3>' +
               rest.length + " course" + (rest.length === 1 ? "" : "s") + ", one highlight each</h3>" +
               '<p class="pf-sub">The piece from each course that shows what it taught and where it went. The days behind each one are in the Volumes.</p></section>');
      rest.forEach(function (m) { out.push(highlight(m, { onePage: true, deeper: true })); });
    }
    if (cap.length) {
      cap.forEach(function (m) { out.push(highlight(m, { onePage: true, deeper: true, eyebrow: "The Capstone · " + m.course.code + " · defended" })); });
    }
    out.push(questionSection(0, "The Question, across the years", true));
    if (made.length) {
      var rows = MAP.outcomes.map(function (o) {
        var ev = made.filter(function (m) { return m.course.outcomes.indexOf(o) !== -1; });
        return "<tr><th>" + esc(o) + "</th><td>" +
          (ev.length ? ev.map(function (m) { return esc(m.rec.title || m.course.code); }).join(" · ") : "—") + "</td></tr>";
      }).join("");
      out.push('<section class="pf-page pf-block"><p class="pf-eyebrow">The five outcomes</p><h3>What the work evidences</h3>' +
               '<table class="pf-outcomes">' + rows + "</table></section>");
    } else {
      out.push('<p class="pf-empty">No highlights recorded yet. Each course page has a place for one, under "The Made Thing".</p>');
    }
    return out.join("");
  }

  function expandedEdition(isPublic) {
    var out = [titlePage("The Expanded Edition"), aboutPage(isPublic)];
    for (var n = 1; n <= 8; n++) if (volumeHasContent(n)) out.push(volume(n));
    out.push(questionSection(0, "The Question, across the years", false));
    return out.join("");
  }

  function render() {
    var root = document.getElementById("portfolio-root");
    if (!root) return;
    var isPublic = document.body.getAttribute("data-portfolio-mode") === "public";
    var html;
    if (!countAll()) {
      html = '<div class="pf-empty-start"><p>Nothing written yet.</p>' +
        '<p>Your Portfolio fills as you go: the Commitment and three questions on <a href="/begin/">Day 0</a>, ' +
        "an answer on each day, one highlight per course on its course page, and the gates at the end of each semester.</p>" +
        '<p><a href="/portfolio/demo/">See a sample portfolio →</a></p></div>';
    } else if (state.edition === "volumes") {
      html = titlePage("Volume " + ROMAN[state.volume]) + volume(state.volume);
    } else if (state.edition === "expanded") {
      html = expandedEdition(isPublic);
    } else {
      html = shortEdition(isPublic);
    }
    root.innerHTML = html;
    fillTexts();

    Array.prototype.forEach.call(document.querySelectorAll("[data-edition]"), function (b) {
      var on = b.getAttribute("data-edition") === state.edition;
      b.setAttribute("aria-selected", on ? "true" : "false");
      b.classList.toggle("is-on", on);
    });
    var pick = document.querySelector("[data-volume-pick]");
    if (pick) pick.hidden = state.edition !== "volumes";
    var src = document.querySelector("[data-pf-source]");
    if (src) src.textContent = countAll() + " entr" + (countAll() === 1 ? "y" : "ies") + ", read from " + SOURCE + ".";
  }

  // ── Publishing (opt-in, one edition at a time) ────────────────────────────

  function editionId() {
    return state.edition === "volumes" ? "volume-" + state.volume : state.edition;
  }

  // Exactly the answers the chosen edition shows, and nothing else.
  function editionAnswers(edition) {
    var all = Object.keys(ANSWERS).map(function (key) { return ANSWERS[key]; })
      .filter(function (a) { return a.lesson !== "/portfolio"; });
    var semOfLesson = function (lesson) {
      var m = lesson.match(/^\/courses\/([A-Z]+-\d+)\//);
      return m && MAP.courses[m[1]] ? MAP.courses[m[1]].semester : null;
    };
    var gateN = function (lesson) { var m = lesson.match(/^\/gates\/semester-(\d)$/); return m ? +m[1] : null; };
    if (edition === "expanded") return all;
    if (edition === "short") {
      return all.filter(function (a) {
        return (a.lesson === "/begin" && (a.heading === "commitment" || a.heading === "education")) ||
               (gateN(a.lesson) && a.heading === "education") || a.heading === "made-thing";
      });
    }
    var n = +edition.split("-")[1];
    return all.filter(function (a) {
      var g = gateN(a.lesson);
      if (a.lesson === "/begin") return n === 1 || a.heading === "education";
      if (g) return g === n || (g < n && a.heading === "education");
      return semOfLesson(a.lesson) === n;
    });
  }

  function publishStatus(text, link) {
    var el = document.querySelector("[data-pf-publish-status]");
    if (!el) return;
    el.innerHTML = esc(text) + (link ? ' <a href="' + esc(link) + '">' + esc(link) + "</a>" : "");
  }

  var MINE = { handle: null, published: [] };

  function publicLink(handle) { return location.origin + "/portfolio/" + handle + "/"; }

  function refreshPublishPanel() {
    var panel = document.querySelector("[data-pf-publish]");
    var acct = window.SDITAccount;
    if (!panel || !acct || !acct.isSignedIn() || !acct.request) return;
    panel.hidden = false;
    var ed = editionId();
    var on = MINE.published.filter(function (p) { return p.edition === ed; })[0];
    var un = panel.querySelector("[data-pf-unpublish-btn]");
    if (un) un.hidden = !on;
    var label = { short: "The Short Edition", expanded: "The Expanded Edition" }[ed] || ("Volume " + ROMAN[+ed.split("-")[1]]);
    if (on && MINE.handle) publishStatus(label + " is published, as of " + dateOf(on.publishedAt) + ":", publicLink(MINE.handle));
    else publishStatus(label + " is private.");
  }

  function wirePublishing() {
    var acct = window.SDITAccount;
    if (!acct || !acct.isSignedIn() || !acct.request) return;
    var input = document.querySelector("[data-pf-handle]");
    acct.request("/portfolio/mine").then(function (d) {
      MINE = { handle: d.handle, published: d.published || [] };
      if (input && d.handle) input.value = d.handle;
      refreshPublishPanel();
    }, function () { refreshPublishPanel(); });
    var pub = document.querySelector("[data-pf-publish-btn]");
    if (pub) pub.addEventListener("click", function () {
      var handle = (input && input.value || "").trim().toLowerCase();
      var ed = editionId();
      var answers = editionAnswers(ed).map(function (a) { return { lesson: a.lesson, heading: a.heading, content: a.content, at: a.at }; });
      if (!answers.length) { publishStatus("This edition is empty; there is nothing to publish yet."); return; }
      publishStatus("Publishing… (the files behind the highlights are copied; this can take a moment)");
      acct.request("/portfolio", { method: "PUT", body: { handle: handle, edition: ed, snapshot: { name: state.name, about: state.about, answers: answers } } })
        .then(function (d) {
          MINE.handle = d.handle;
          MINE.published = MINE.published.filter(function (p) { return p.edition !== ed; })
            .concat([{ edition: ed, publishedAt: new Date().toISOString() }]);
          refreshPublishPanel();
        }, function (err) {
          publishStatus(err && err.status === 404 ? "Publishing is not switched on yet." : (err && err.message) || "Not published.");
        });
    });
    var un = document.querySelector("[data-pf-unpublish-btn]");
    if (un) un.addEventListener("click", function () {
      var ed = editionId();
      acct.request("/portfolio/unpublish", { method: "POST", body: { edition: ed } }).then(function () {
        MINE.published = MINE.published.filter(function (p) { return p.edition !== ed; });
        refreshPublishPanel();
      }, function (err) { publishStatus((err && err.message) || "Could not unpublish."); });
    });
  }

  // ── The public view (/portfolio/<handle>/) ────────────────────────────────

  var PUBLIC = null;

  function publicHandle() {
    var m = location.pathname.match(/^\/portfolio\/([a-z0-9-]{3,30})\/?$/);
    if (m && m[1] !== "view") return m[1];
    return new URLSearchParams(location.search).get("h");
  }

  // The sample portfolio (a fictional learner, labelled as one) is a static
  // file, not an account: every edition is built from it with the same
  // filters a real publish uses.
  function loadDemo() {
    return fetch("/portfolio/demo.json").then(function (r) { return r.json(); }).then(function (d) {
      ANSWERS = {};
      d.answers.forEach(function (a) { ANSWERS[k(a.lesson, a.heading)] = a; });
      var editions = {};
      ["short", "expanded"].concat([1, 2, 3, 4, 5, 6, 7, 8].map(function (n) { return "volume-" + n; }))
        .forEach(function (e) {
          editions[e] = { publishedAt: d.answers[d.answers.length - 1].at,
                          snapshot: { name: d.name, about: d.about, answers: editionAnswers(e) } };
        });
      var note = document.querySelector("[data-demo-note]");
      if (note) { note.textContent = d.note; note.hidden = false; }
      showPublic({ handle: "demo", editions: editions });
    });
  }

  function loadPublic() {
    var h = publicHandle();
    var root = document.getElementById("portfolio-root");
    if (!h) { root.innerHTML = '<p class="pf-empty">No portfolio named.</p>'; return; }
    if (h === "demo") { loadDemo(); return; }
    var api = (window.SDIT_ACCOUNT_API || "/api").replace(/\/+$/, "");
    fetch(api + "/portfolio/" + encodeURIComponent(h)).then(function (r) {
      if (!r.ok) throw new Error(String(r.status));
      return r.json();
    }).then(showPublic).catch(function () {
      root.innerHTML = '<div class="pf-empty-start"><p>This portfolio is not published.</p></div>';
      var src = document.querySelector("[data-pf-source]"); if (src) src.textContent = "";
    });
  }

  function showPublic(d) {
      PUBLIC = d;
      var eds = Object.keys(d.editions || {});
      // Offer only what was published.
      Array.prototype.forEach.call(document.querySelectorAll("[data-edition]"), function (b) {
        var e = b.getAttribute("data-edition");
        var has = e === "volumes" ? eds.some(function (x) { return /^volume-/.test(x); }) : eds.indexOf(e) !== -1;
        b.hidden = !has;
      });
      var sel = document.querySelector("[data-volume]");
      if (sel) Array.prototype.forEach.call(sel.options, function (o) { o.hidden = eds.indexOf("volume-" + o.value) === -1; });
      var want = state.edition;
      if (want === "volumes" && eds.some(function (x) { return x === "volume-" + state.volume; })) { /* keep */ }
      else if (eds.indexOf(want) !== -1) { /* keep */ }
      else if (eds.indexOf("short") !== -1) state.edition = "short";
      else if (eds.indexOf("expanded") !== -1) state.edition = "expanded";
      else { state.edition = "volumes"; state.volume = +eds.filter(function (x) { return /^volume-/.test(x); })[0].split("-")[1]; if (sel) sel.value = state.volume; }
      usePublicEdition();
  }

  function usePublicEdition() {
    var ed = PUBLIC.editions[editionId()];
    ANSWERS = {};
    ((ed && ed.snapshot && ed.snapshot.answers) || []).forEach(function (a) {
      ANSWERS[k(a.lesson, a.heading)] = { lesson: a.lesson, heading: a.heading, content: a.content, at: a.at };
    });
    state.name = (ed && ed.snapshot && ed.snapshot.name) || "";
    state.about = (ed && ed.snapshot && ed.snapshot.about) || "";
    SOURCE = PUBLIC.handle === "demo" ? "the sample portfolio" : "a snapshot published " + (ed ? dateOf(ed.publishedAt) : "");
    render();
  }

  // ── Downloads ──────────────────────────────────────────────────────────────

  function markdown() {
    var md = [];
    var name = state.name || (PROFILE && PROFILE.email) || "";
    md.push("# The Portfolio" + (name ? " of " + name : ""), "");
    if (state.about) md.push("## Who this is", "", state.about, "");
    var c = commitment();
    if (c) md.push("Committed on " + dateOf(c) + ".", "");
    var made = madeThings();
    if (made.length) {
      md.push("## The work", "");
      made.forEach(function (m) {
        var r = m.rec;
        md.push("### " + (r.title || "Untitled") + " — " + m.course.code + " " + m.course.name, "");
        md.push([r.form, r.date ? "defended or shown " + dateOf(r.date) : "", r.level].filter(Boolean).join(" · "), "");
        if (r.words) md.push(r.words, "");
        if (r.applied) md.push("Where it went: " + r.applied, "");
        (r.files || []).forEach(function (f) { md.push("- " + f.name + (fileUrl(f) ? " <" + fileUrl(f) + ">" : "")); });
        if ((r.files || []).length) md.push("");
        if (r.link) md.push(r.link, "");
        md.push("Evidence of: " + m.course.outcomes.join(" · "), "");
      });
    }
    md.push("## " + MAP.question, "");
    theQuestion(0).forEach(function (r) {
      md.push("**" + r.where + (r.a.at ? " · " + dateOf(r.a.at) : "") + "**", "", r.a.content, "");
    });
    if (state.edition !== "short") {
      var vols = state.edition === "volumes" ? [state.volume] : [1, 2, 3, 4, 5, 6, 7, 8];
      vols.forEach(function (n) {
        if (state.edition === "expanded" && !volumeHasContent(n)) return;
        md.push("## Volume " + ROMAN[n] + " · " + MAP.semesters[n - 1].label, "");
        if (n === 1) MAP.begin.questions.forEach(function (q) {
          var a = get(MAP.begin.lesson, q.id); if (a) md.push("**Day 0 · " + q.text + "**", "", a.content, "");
        });
        semesterCourses(n).forEach(function (cs) {
          md.push("### " + cs.course.code + " · " + cs.course.name, "");
          cs.days.forEach(function (d) {
            md.push("#### Day " + d.n + " — " + d.title, "");
            md.push("*" + d.q + "*" + (d.a.at ? " · " + dateOf(d.a.at) : ""), "", d.a.content, "");
          });
        });
        var g = MAP.gates[n - 1];
        g.questions.forEach(function (q) {
          var a = get(g.lesson, q.id); if (a) md.push("**Gate · " + q.text + "**", "", a.content, "");
        });
      });
    }
    return md.join("\n");
  }

  function download(name, type, text) {
    var blob = new Blob([text], { type: type });
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = name;
    document.body.appendChild(a);
    a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 1000);
  }

  // ── Wiring ─────────────────────────────────────────────────────────────────

  function init() {
    var mapEl = document.getElementById("degree-map");
    if (!mapEl) return;
    MAP = JSON.parse(mapEl.textContent);
    var isPublic = document.body.getAttribute("data-portfolio-mode") === "public";

    var params = new URLSearchParams(location.search);
    var ed = params.get("edition");
    if (ed === "volumes" || ed === "expanded" || ed === "short") state.edition = ed;
    var v = parseInt(params.get("volume"), 10);
    if (v >= 1 && v <= 8) state.volume = v;

    var sel = document.querySelector("[data-volume]");
    if (sel) {
      MAP.semesters.forEach(function (s) {
        var o = document.createElement("option");
        o.value = s.n; o.textContent = ROMAN[s.n] + " · " + s.label;
        sel.appendChild(o);
      });
      sel.value = state.volume;
      sel.addEventListener("change", function () {
        state.volume = parseInt(sel.value, 10);
        if (PUBLIC) usePublicEdition(); else { render(); refreshPublishPanel(); }
      });
    }
    Array.prototype.forEach.call(document.querySelectorAll("[data-edition]"), function (b) {
      b.addEventListener("click", function () {
        state.edition = b.getAttribute("data-edition");
        if (PUBLIC) usePublicEdition(); else { render(); refreshPublishPanel(); }
      });
    });
    // A "days of answers" link under a Short Edition highlight opens the
    // Volumes at that course.
    document.addEventListener("click", function (e) {
      var a = e.target.closest && e.target.closest('a[href^="#course-"]');
      if (!a) return;
      var dir = a.getAttribute("href").slice("#course-".length);
      var c = MAP.courses[dir];
      if (!c || state.edition !== "short") return;
      e.preventDefault();
      state.edition = "volumes"; state.volume = c.semester;
      if (sel) sel.value = state.volume;
      if (PUBLIC) {
        if (!PUBLIC.editions["volume-" + c.semester]) { state.edition = "short"; return; }
        usePublicEdition();
      } else { render(); refreshPublishPanel(); }
      var target = document.getElementById("course-" + dir);
      if (target) target.scrollIntoView({ behavior: "smooth", block: "start" });
    });
    if (isPublic) {
      Array.prototype.forEach.call(document.querySelectorAll("[data-own-only]"), function (el) { el.hidden = true; });
      waitFor(function () { return window.SDIT_ACCOUNT_API; }, 3000).then(loadPublic);
      return;
    }

    var nameInput = document.querySelector("[data-pf-name]");
    if (nameInput) {
      try { state.name = localStorage.getItem("sdit:/portfolio::name") || ""; } catch (e) {}
      nameInput.value = state.name;
      nameInput.addEventListener("input", function () {
        state.name = nameInput.value.trim();
        if (window.SDITWork) window.SDITWork.save("/portfolio", "name", state.name);
        render();
      });
    }
    var aboutInput = document.querySelector("[data-pf-about]");
    if (aboutInput) {
      try { state.about = localStorage.getItem("sdit:/portfolio::about") || ""; } catch (e) {}
      aboutInput.value = state.about;
      var saveAbout;
      aboutInput.addEventListener("input", function () {
        state.about = aboutInput.value;
        clearTimeout(saveAbout);
        saveAbout = setTimeout(function () {
          if (window.SDITWork) window.SDITWork.save("/portfolio", "about", state.about.trim());
          render();
        }, 800);
      });
    }
    var p = document.querySelector("[data-pf-print]");
    if (p) p.addEventListener("click", function () { window.print(); });
    var m = document.querySelector("[data-pf-md]");
    if (m) m.addEventListener("click", function () { download("sdit-portfolio.md", "text/markdown", markdown()); });
    var j = document.querySelector("[data-pf-json]");
    if (j) j.addEventListener("click", function () {
      var rows = Object.keys(ANSWERS).sort().map(function (key) {
        var a = ANSWERS[key];
        return { lesson: a.lesson, heading: a.heading, content: a.content, updatedAt: a.at };
      });
      download("sdit-portfolio.json", "application/json",
               JSON.stringify({ exported: new Date().toISOString(), name: state.name, about: state.about, answers: rows }, null, 2));
    });

    ANSWERS = readLocal();
    render();
    // The account script arrives with the header partial; wait for it briefly.
    waitFor(function () { return window.SDITWork && (window.SDITAccount || !window.SDIT_ACCOUNT_API); }, 4000)
      .then(gather).then(function () {
        if (aboutInput && !aboutInput.value && state.about) aboutInput.value = state.about;
        if (nameInput && !nameInput.value && state.name) nameInput.value = state.name;
        render(); wirePublishing();
        return resolveFiles();
      }).then(render);
  }

  // For inspection and tests; the page itself uses the buttons.
  window.SDITPortfolio = { markdown: function () { return markdown(); }, render: render, state: state,
                           showPublic: function (d) { showPublic(d); }, editionAnswers: function (e) { return editionAnswers(e); } };

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
