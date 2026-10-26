/**
 * portfolio.js — the learner's Portfolio, assembled in the browser.
 *
 * Reads the degree map embedded in the page (#degree-map, built by
 * scripts/portfolio.py) and the learner's own answers: from this device
 * (localStorage "sdit:<lesson>::<heading>", with "…@t" timestamps) and, when
 * signed in, from the account (GET /work/all). Renders one of three editions:
 *
 *   Short      the judging document: the Commitment, the Question across the
 *              years, one page per made thing, the capstone, the outcomes
 *   Volumes    one book per semester: the gate, the Question so far, the
 *              semester's made things, then its daily answers in Path order
 *   Expanded   every volume, in order
 *
 * Print uses the print stylesheet; downloads are built here as files. Nothing
 * is sent anywhere: the learner's words stay in their browser and account.
 */
(function () {
  "use strict";

  var ROMAN = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII"];
  var MAP, ANSWERS = {}, SOURCE = "this device", PROFILE = null;
  var state = { edition: "short", volume: 1, name: "" };

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
    });
  }

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

  function madeThings(semester) {
    var out = [];
    Object.keys(MAP.courses).forEach(function (dir) {
      var c = MAP.courses[dir];
      if (semester && c.semester !== semester) return;
      var r = get("/courses/" + dir + "/made", "made-thing");
      if (!r) return;
      var rec;
      try { rec = JSON.parse(r.content); } catch (e) { return; }
      if (!rec || !(rec.title || rec.words || rec.link)) return;
      out.push({ dir: dir, course: c, rec: rec, at: r.at });
    });
    out.sort(function (a, b) {
      return (a.course.semester - b.course.semester) || (a.course.code < b.course.code ? -1 : 1);
    });
    return out;
  }

  function semesterDays(semester) {
    return MAP.days.filter(function (d) { return d[0] === semester; }).map(function (d) {
      return { s: d[0], w: d[1], label: d[2], dir: d[3], n: d[4], title: d[5], q: d[6],
               a: get(dayLesson(d[3], d[4]), "answer") };
    }).filter(function (d) { return d.a; });
  }

  function countAll() {
    return Object.keys(ANSWERS).length;
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

  function commitmentBlock() {
    var c = commitment();
    if (!c) return "";
    return '<section class="pf-block"><h3>The Commitment</h3>' +
      "<p>Committed on " + esc(dateOf(c)) + ".</p></section>";
  }

  function questionSpread(upTo, title) {
    var rows = theQuestion(upTo);
    var body = rows.length ? rows.map(function (r) {
      return '<div class="pf-q-row"><p class="pf-q-when">' + esc(r.where) +
        (r.a.at ? " · " + esc(dateOf(r.a.at)) : "") + "</p>" +
        '<blockquote class="pf-q-answer">' + paras(r.a.content) + "</blockquote></div>";
    }).join("") : '<p class="pf-empty">Not answered yet. It is the first question on <a href="/begin/">Day 0</a>.</p>';
    return '<section class="pf-page pf-question"><p class="pf-eyebrow">' + esc(title || "The Question") + "</p>" +
      "<h3>" + esc(MAP.question) + "</h3>" + body + "</section>";
  }

  function madeBlock(m, onePerPage) {
    var r = m.rec, c = m.course;
    return '<section class="' + (onePerPage ? "pf-page " : "") + 'pf-made">' +
      '<p class="pf-eyebrow">' + esc(c.code) + " · " + esc(c.name) + " · Semester " + esc(c.semester) + "</p>" +
      "<h3>" + esc(r.title || "Untitled") + "</h3>" +
      '<p class="pf-meta">' + esc(r.form || "") +
        (r.date ? " · defended or shown " + esc(dateOf(r.date)) : "") +
        (r.level ? " · " + esc(r.level) : "") + "</p>" +
      (r.words ? paras(r.words) : "") +
      (r.link ? '<p class="pf-link"><a href="' + esc(r.link) + '" rel="noopener">' + esc(r.link) + "</a></p>" : "") +
      '<p class="pf-evidence">Evidence of: ' + esc(c.outcomes.join(" · ")) + "</p>" +
      "</section>";
  }

  function gateBlock(n) {
    var g = MAP.gates[n - 1];
    var rows = g.questions.map(function (q) {
      var a = get(g.lesson, q.id);
      return a ? '<div class="pf-qa"><p class="pf-qa-q">' + esc(q.text) + "</p>" +
        '<div class="pf-qa-a">' + paras(a.content) + "</div></div>" : "";
    }).join("");
    return rows ? '<section class="pf-block"><h3>The Gate</h3>' + rows + "</section>" : "";
  }

  function dayZeroBlock() {
    var rows = MAP.begin.questions.map(function (q) {
      var a = get(MAP.begin.lesson, q.id);
      return a ? '<div class="pf-qa"><p class="pf-qa-q">' + esc(q.text) + "</p>" +
        '<div class="pf-qa-a">' + paras(a.content) + "</div></div>" : "";
    }).join("");
    return rows ? '<section class="pf-block"><h3>Day 0</h3>' + rows + "</section>" : "";
  }

  function volume(n) {
    var sem = MAP.semesters[n - 1];
    var days = semesterDays(n);
    var made = madeThings(n);
    var gate = gateBlock(n);
    var parts = [];
    parts.push('<section class="pf-page pf-volume-title"><p class="pf-eyebrow">Volume ' + ROMAN[n] + "</p>" +
               "<h2>" + esc(sem.label) + "</h2><p class=\"pf-sub\">Semester " + n + "</p></section>");
    if (n === 1) { parts.push(commitmentBlock()); parts.push(dayZeroBlock()); }
    parts.push(gate);
    parts.push(questionSpread(n, "The Question, as it stood at the end of Semester " + n));
    if (made.length) {
      parts.push('<section class="pf-block"><h3>What you made</h3></section>');
      made.forEach(function (m) { parts.push(madeBlock(m, false)); });
    }
    if (days.length) {
      parts.push('<section class="pf-block pf-days"><h3>The days</h3>');
      var week = 0;
      days.forEach(function (d) {
        if (d.w !== week) { week = d.w; parts.push('<p class="pf-week">Week ' + week + "</p>"); }
        var c = MAP.courses[d.dir] || {};
        parts.push('<article class="pf-day"><p class="pf-day-head">' + esc(d.label ? d.label + " · " : "") +
          esc(c.code || d.dir) + " · Day " + d.n + (d.a.at ? " · " + esc(dateOf(d.a.at)) : "") + "</p>" +
          "<h4>" + esc(d.title) + "</h4>" +
          '<p class="pf-day-q">' + esc(d.q) + "</p>" +
          '<div class="pf-day-a">' + paras(d.a.content) + "</div></article>");
      });
      parts.push("</section>");
    }
    if (!gate && !made.length && !days.length && n !== 1) {
      parts.push('<p class="pf-empty">Nothing written in this semester yet.</p>');
    }
    return '<div class="pf-volume">' + parts.join("") + "</div>";
  }

  function volumeHasContent(n) {
    return semesterDays(n).length || madeThings(n).length || gateBlock(n) || (n === 1 && (commitment() || dayZeroBlock()));
  }

  function shortEdition() {
    var made = madeThings();
    var cap = made.filter(function (m) { return /^CAP-/.test(m.dir); });
    var rest = made.filter(function (m) { return !/^CAP-/.test(m.dir); });
    var out = [titlePage("The Short Edition"), commitmentBlock(), questionSpread(0)];
    if (rest.length) {
      out.push('<section class="pf-page pf-block"><p class="pf-eyebrow">What was made</p><h3>' +
               rest.length + " made thing" + (rest.length === 1 ? "" : "s") + "</h3></section>");
      rest.forEach(function (m) { out.push(madeBlock(m, true)); });
    }
    if (cap.length) {
      out.push('<section class="pf-page pf-block"><p class="pf-eyebrow">The Capstone</p><h3>The defended work</h3></section>');
      cap.forEach(function (m) { out.push(madeBlock(m, true)); });
    }
    if (made.length) {
      var rows = MAP.outcomes.map(function (o) {
        var ev = made.filter(function (m) { return m.course.outcomes.indexOf(o) !== -1; });
        return "<tr><th>" + esc(o) + "</th><td>" +
          (ev.length ? ev.map(function (m) { return esc(m.rec.title || m.course.code); }).join(" · ") : "—") + "</td></tr>";
      }).join("");
      out.push('<section class="pf-page pf-block"><p class="pf-eyebrow">The five outcomes</p><h3>What the work evidences</h3>' +
               '<table class="pf-outcomes">' + rows + "</table></section>");
    } else {
      out.push('<p class="pf-empty">No made things recorded yet. Each course page has a place to record yours, under "The Made Thing".</p>');
    }
    return out.join("");
  }

  function expandedEdition() {
    var out = [titlePage("The Expanded Edition"), questionSpread(0)];
    for (var n = 1; n <= 8; n++) if (volumeHasContent(n)) out.push(volume(n));
    return out.join("");
  }

  function render() {
    var root = document.getElementById("portfolio-root");
    if (!root) return;
    var html;
    if (!countAll()) {
      html = '<div class="pf-empty-start"><p>Nothing written yet.</p>' +
        '<p>Your Portfolio fills as you go: the Commitment and three questions on <a href="/begin/">Day 0</a>, ' +
        "an answer on each day, a record of each made thing on its course page, and the gates at the end of each semester.</p>" +
        '<p><a href="/portfolio/demo/">See a sample portfolio →</a></p></div>';
    } else if (state.edition === "volumes") {
      html = titlePage("Volume " + ROMAN[state.volume]) + volume(state.volume);
    } else if (state.edition === "expanded") {
      html = expandedEdition();
    } else {
      html = shortEdition();
    }
    root.innerHTML = html;

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
      publishStatus("Publishing…");
      acct.request("/portfolio", { method: "PUT", body: { handle: handle, edition: ed, snapshot: { name: state.name, answers: answers } } })
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
                          snapshot: { name: d.name, answers: editionAnswers(e) } };
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
      if (eds.indexOf("short") !== -1) state.edition = "short";
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
    SOURCE = PUBLIC.handle === "demo" ? "the sample portfolio" : "a snapshot published " + (ed ? dateOf(ed.publishedAt) : "");
    render();
  }

  // ── Downloads ──────────────────────────────────────────────────────────────

  function markdown() {
    var md = [];
    var name = state.name || (PROFILE && PROFILE.email) || "";
    md.push("# The Portfolio" + (name ? " of " + name : ""), "");
    var c = commitment();
    if (c) md.push("Committed on " + dateOf(c) + ".", "");
    md.push("## " + MAP.question, "");
    theQuestion(0).forEach(function (r) {
      md.push("**" + r.where + (r.a.at ? " · " + dateOf(r.a.at) : "") + "**", "", r.a.content, "");
    });
    var made = madeThings();
    if (made.length) {
      md.push("## What was made", "");
      made.forEach(function (m) {
        var r = m.rec;
        md.push("### " + (r.title || "Untitled") + " — " + m.course.code + " " + m.course.name, "");
        md.push([r.form, r.date ? "defended or shown " + dateOf(r.date) : "", r.level].filter(Boolean).join(" · "), "");
        if (r.words) md.push(r.words, "");
        if (r.link) md.push(r.link, "");
        md.push("Evidence of: " + m.course.outcomes.join(" · "), "");
      });
    }
    if (state.edition !== "short") {
      var vols = state.edition === "volumes" ? [state.volume] : [1, 2, 3, 4, 5, 6, 7, 8];
      vols.forEach(function (n) {
        if (state.edition === "expanded" && !volumeHasContent(n)) return;
        md.push("## Volume " + ROMAN[n] + " · " + MAP.semesters[n - 1].label, "");
        if (n === 1) MAP.begin.questions.forEach(function (q) {
          var a = get(MAP.begin.lesson, q.id); if (a) md.push("**Day 0 · " + q.text + "**", "", a.content, "");
        });
        var g = MAP.gates[n - 1];
        g.questions.forEach(function (q) {
          var a = get(g.lesson, q.id); if (a) md.push("**Gate · " + q.text + "**", "", a.content, "");
        });
        semesterDays(n).forEach(function (d) {
          var cc = MAP.courses[d.dir] || {};
          md.push("### " + (cc.code || d.dir) + " · Day " + d.n + " — " + d.title, "");
          md.push("*" + d.q + "*" + (d.a.at ? " · " + dateOf(d.a.at) : ""), "", d.a.content, "");
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
    var print = document.querySelector("[data-pf-print]");
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
               JSON.stringify({ exported: new Date().toISOString(), name: state.name, answers: rows }, null, 2));
    });

    ANSWERS = readLocal();
    render();
    // The account script arrives with the header partial; wait for it briefly.
    waitFor(function () { return window.SDITWork && (window.SDITAccount || !window.SDIT_ACCOUNT_API); }, 4000)
      .then(gather).then(function () { render(); wirePublishing(); });
  }

  // For inspection and tests; the page itself uses the buttons.
  window.SDITPortfolio = { markdown: function () { return markdown(); }, render: render, state: state,
                           showPublic: function (d) { showPublic(d); }, editionAnswers: function (e) { return editionAnswers(e); } };

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
