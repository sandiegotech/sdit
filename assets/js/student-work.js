/**
 * student-work.js — the learner's answers, kept.
 *
 * Every place a page asks for an answer is marked explicitly:
 *   <div class="answer-slot" data-sdit-answer="answer"></div>
 * Day pages get one under "Carry the question" (the build turns the day
 * file's <!-- sdit:answer --> into this). Day 0 and the gates get one per
 * question, keyed by the question id.
 *
 * An answer is stored under (lesson, heading): the page's canonical lesson id
 * (meta sdit-lesson, e.g. /courses/HUM-101/day-01 or /begin) and the slot's
 * key. The Notebook reads them back by the same pair.
 *
 * Save behaviour:
 *   - Always: localStorage, as "sdit:<lesson>::<heading>", debounced.
 *   - Signed in: also the account (SDITAccount.saveWork), so answers follow
 *     the learner to other devices.
 *   - On localhost: also the dev server (serve.py /api/save → my-work/).
 *
 * Also here, because they read and write the same store:
 *   - [data-sdit-commit]       the Commitment on Day 0 (heading "commitment",
 *                              value: the date committed, YYYY-MM-DD)
 *   - [data-after-commit]      shown once the learner has committed
 *   - [data-sdit-commitment-line]  the "You committed on…" line on a gate
 *   - [data-sdit-recall="<lesson>::<heading>"]  an earlier answer, read-only
 */

(function () {
  "use strict";

  var SAVE_DELAY = 1200;

  // ── Store ──────────────────────────────────────────────────────────────────

  function isLocalhost() {
    return location.hostname === "localhost" || location.hostname === "127.0.0.1";
  }

  function lessonPath() {
    var meta = document.querySelector('meta[name="sdit-lesson"]');
    if (meta && meta.content) return meta.content;
    return location.pathname.replace(/\.html$/, "").replace(/\/index$/, "").replace(/\/$/, "");
  }

  function key(lesson, heading) { return "sdit:" + lesson + "::" + heading; }

  function readLocal(lesson, heading) {
    try { return localStorage.getItem(key(lesson, heading)) || ""; } catch (e) { return ""; }
  }

  // Each answer keeps the time it was last written beside it ("…@t"), so the
  // Portfolio can date answers written on this device.
  function writeLocal(lesson, heading, value) {
    try {
      localStorage.setItem(key(lesson, heading), value);
      localStorage.setItem(key(lesson, heading) + "@t", new Date().toISOString());
      return true;
    } catch (e) { return false; }
  }

  function account() {
    return window.SDITAccount && window.SDITAccount.isSignedIn() ? window.SDITAccount : null;
  }

  var _remote = {};
  function loadRemote(lesson) {
    if (!_remote[lesson]) {
      var acct = account();
      if (acct) {
        _remote[lesson] = acct.loadWork(lesson);
      } else if (isLocalhost()) {
        _remote[lesson] = fetch("/api/load?file=" + encodeURIComponent(lesson))
          .then(function (r) { return r.ok ? r.json() : {}; })
          .catch(function () { return {}; });
      } else {
        _remote[lesson] = Promise.resolve({});
      }
    }
    return _remote[lesson];
  }

  // Local wins when both exist: it is the most recent thing typed on this device.
  function read(lesson, heading) {
    var local = readLocal(lesson, heading);
    if (local) return Promise.resolve(local);
    return loadRemote(lesson).then(function (r) { return (r && r[heading]) || ""; });
  }

  function save(lesson, heading, value) {
    writeLocal(lesson, heading, value);
    var acct = account();
    if (acct) return acct.saveWork(lesson, heading, value).then(function (ok) { return ok ? "saved" : "local"; });
    if (isLocalhost()) {
      return fetch("/api/save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ file: lesson, heading: heading, content: value }),
      }).then(function (r) { return r.json(); })
        .then(function (d) { return d && d.ok ? "saved" : "local"; })
        .catch(function () { return "local"; });
    }
    return Promise.resolve("local");
  }

  // ── Small helpers ──────────────────────────────────────────────────────────

  function debounce(fn, delay) {
    var t;
    return function () {
      var a = arguments;
      clearTimeout(t);
      t = setTimeout(function () { fn.apply(null, a); }, delay);
    };
  }

  function longDate(iso) {
    var d = new Date(iso + "T12:00:00");
    if (isNaN(d)) return iso;
    return d.toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric" });
  }

  function todayISO() {
    var d = new Date();
    return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
  }

  var LABELS = { saving: "Saving…", saved: "Saved", local: "Saved on this device", error: "Not saved" };

  function setStatus(el, state) {
    el.className = "response-status response-status--" + state;
    el.textContent = LABELS[state] || "";
    clearTimeout(el._t);
    if (state === "saved" || state === "local") {
      el._t = setTimeout(function () { el.textContent = ""; el.className = "response-status"; }, 3000);
    }
  }

  // ── Answer slots ───────────────────────────────────────────────────────────

  function buildSlot(slot, lesson) {
    if (slot._built) return;
    slot._built = true;
    var heading = slot.getAttribute("data-sdit-answer") || "answer";

    var ta = document.createElement("textarea");
    ta.className = "response-textarea";
    ta.rows = 3;
    ta.placeholder = slot.getAttribute("data-placeholder") || "Write here. A line is enough.";
    ta.setAttribute("aria-label", slot.getAttribute("data-question") || "Your answer");

    var foot = document.createElement("div");
    foot.className = "answer-foot";
    var hint = document.createElement("span");
    hint.className = "answer-hint";
    hint.innerHTML = account()
      ? 'Kept in your <a href="/portfolio/">Portfolio</a>, on every device you sign in on.'
      : 'Kept in your <a href="/portfolio/">Portfolio</a> on this device. Sign in to keep it everywhere.';
    var status = document.createElement("span");
    status.className = "response-status";
    foot.appendChild(hint);
    foot.appendChild(status);

    slot.appendChild(ta);
    slot.appendChild(foot);

    function resize() {
      ta.style.height = "auto";
      ta.style.height = (ta.scrollHeight + 2) + "px";
    }

    read(lesson, heading).then(function (v) { if (v && !ta.value) { ta.value = v; resize(); } });

    var debounced = debounce(function () {
      setStatus(status, "saving");
      save(lesson, heading, ta.value).then(function (state) { setStatus(status, state); },
                                           function () { setStatus(status, "error"); });
    }, SAVE_DELAY);
    ta.addEventListener("input", function () { resize(); debounced(); });
  }

  // ── The highlight (course pages) ───────────────────────────────────────────
  // One record per course: the piece that shows what the course taught and
  // where it went. Stored as JSON under (/courses/<DIR>/made, "made-thing"):
  //   title, form, link, words, applied, date, level,
  //   files: [{key, name, type, size, kind}]  — the photos, film, deck, essay
  // The words save like any answer. The files go to the account's work bucket
  // over links the API signs, so they need a sign-in; the record keeps only
  // their keys, and the Portfolio asks for links when it shows them.

  var FORMS = ["essay", "film", "recording", "object", "program", "build", "forecast", "report", "other"];
  var LEVELS = ["", "beginning", "developing", "proficient", "mastered"];
  var ACCEPT = "image/*,video/mp4,video/quicktime,video/webm,audio/*,application/pdf,text/plain,text/markdown,.md,.txt";
  var MAX_FILES = 12;

  function field(label, input, hint) {
    var wrap = document.createElement("label");
    wrap.className = "made-field";
    var span = document.createElement("span");
    span.textContent = label;
    wrap.appendChild(span);
    wrap.appendChild(input);
    if (hint) { var h = document.createElement("small"); h.textContent = hint; wrap.appendChild(h); }
    return wrap;
  }

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }

  function fmtSize(n) {
    if (!n) return "";
    if (n < 1024 * 1024) return Math.max(1, Math.round(n / 1024)) + " KB";
    return (n / (1024 * 1024)).toFixed(n < 10 * 1024 * 1024 ? 1 : 0) + " MB";
  }

  // Upload one file: ask for a signed link, put the bytes there, then have
  // the API check what landed. Progress comes from the put.
  function uploadFile(acct, course, file, onProgress) {
    var type = file.type || (/\.md$/i.test(file.name) ? "text/markdown" : /\.txt$/i.test(file.name) ? "text/plain" : "");
    return acct.request("/work/upload", { method: "POST", body: { course: course, name: file.name, type: type } })
      .then(function (link) {
        if (file.size > link.max) throw new Error("Too large: the limit for " + link.kind + " files is " + Math.round(link.max / 1048576) + " MB");
        return new Promise(function (resolve, reject) {
          var xhr = new XMLHttpRequest();
          xhr.open("PUT", link.url);
          xhr.setRequestHeader("Content-Type", type);
          xhr.upload.onprogress = function (e) { if (e.lengthComputable && onProgress) onProgress(e.loaded / e.total); };
          xhr.onload = function () { xhr.status >= 200 && xhr.status < 300 ? resolve() : reject(new Error("The upload failed (" + xhr.status + ")")); };
          xhr.onerror = function () { reject(new Error("The upload failed")); };
          xhr.send(file);
        }).then(function () { return acct.request("/work/upload/complete", { method: "POST", body: { key: link.key } }); })
          .then(function (d) { return d.file; });
      });
  }

  function buildMade(slot) {
    if (slot._built) return;
    slot._built = true;
    var lesson = slot.getAttribute("data-lesson");
    var heading = "made-thing";
    var course = (lesson.match(/^\/courses\/([^/]+)\//) || [])[1] || "";
    var record = { title: "", form: "essay", link: "", words: "", applied: "", date: "", level: "", files: [] };

    slot.appendChild(el("p", "made-head", "The highlight of this course, for your Portfolio"));
    slot.appendChild(el("p", "made-intro",
      "One piece that shows what the course taught you and where it went. Photos, a film, a deck, an essay, a recording: whatever the thing actually is. " +
      "Your Portfolio opens each course with it; everything else you wrote here sits behind it."));

    var title = document.createElement("input"); title.type = "text"; title.placeholder = "What it is called";
    var form = document.createElement("select");
    FORMS.forEach(function (f) { var o = document.createElement("option"); o.value = f; o.textContent = f; form.appendChild(o); });
    var link = document.createElement("input"); link.type = "url"; link.placeholder = "https://… if it lives somewhere online";
    var words = document.createElement("textarea"); words.rows = 3; words.className = "response-textarea";
    words.placeholder = "What you made, and what it taught you.";
    var applied = document.createElement("textarea"); applied.rows = 2; applied.className = "response-textarea";
    applied.placeholder = "Where it went afterwards: how you have used it outside the course, if you have.";
    var date = document.createElement("input"); date.type = "date";
    var level = document.createElement("select");
    LEVELS.forEach(function (l) { var o = document.createElement("option"); o.value = l; o.textContent = l || "not reviewed yet"; level.appendChild(o); });

    var status = el("span", "response-status");
    var grid = el("div", "made-grid");
    grid.appendChild(field("Title", title));
    grid.appendChild(field("Form", form));
    grid.appendChild(field("Defended or shown on", date));
    grid.appendChild(field("Rubric level, if reviewed", level));
    slot.appendChild(grid);
    slot.appendChild(field("In your words", words));
    slot.appendChild(field("Where it went", applied));

    // The files.
    var filesWrap = el("div", "made-files");
    filesWrap.appendChild(el("p", "made-files-head", "The work itself"));
    var list = el("ul", "made-file-list");
    var note = el("p", "made-files-note");
    var add = document.createElement("input"); add.type = "file"; add.multiple = true; add.accept = ACCEPT; add.id = "made-add-" + course;
    var addLabel = el("label", "learn-cta learn-cta--ghost made-add", "Add photos, video, a deck, an essay…");
    addLabel.setAttribute("for", add.id);
    add.hidden = true;
    filesWrap.appendChild(list);
    filesWrap.appendChild(note);
    filesWrap.appendChild(addLabel);
    filesWrap.appendChild(add);
    slot.appendChild(filesWrap);
    slot.appendChild(field("Link", link, "Optional. The Portfolio shows the files above; this is for a place it also lives."));
    slot.appendChild(status);

    var urls = {};
    function refreshUrls() {
      var acct = account();
      var keys = record.files.map(function (f) { return f.key; }).filter(function (k) { return k && !urls[k]; });
      if (!acct || !acct.request || !keys.length) return Promise.resolve();
      return acct.request("/work/file-urls", { method: "POST", body: { keys: keys } })
        .then(function (d) { Object.keys(d.urls || {}).forEach(function (k) { urls[k] = d.urls[k]; }); renderFiles(); }, function () {});
    }

    function renderFiles() {
      list.innerHTML = "";
      var acct = account();
      record.files.forEach(function (f, i) {
        var li = el("li", "made-file");
        var thumb = el("div", "made-file-thumb");
        if (f.kind === "image" && urls[f.key]) {
          var img = document.createElement("img"); img.src = urls[f.key]; img.alt = ""; img.loading = "lazy"; thumb.appendChild(img);
        } else {
          thumb.appendChild(el("span", "made-file-kind", { image: "photo", video: "film", audio: "sound", pdf: "pages", text: "text" }[f.kind] || "file"));
        }
        li.appendChild(thumb);
        var meta = el("div", "made-file-meta");
        var name = urls[f.key] ? document.createElement("a") : el("span");
        if (urls[f.key]) { name.href = urls[f.key]; name.target = "_blank"; name.rel = "noopener"; }
        name.textContent = f.name;
        name.className = "made-file-name";
        meta.appendChild(name);
        meta.appendChild(el("span", "made-file-size", (i === 0 ? "the cover · " : "") + fmtSize(f.size)));
        li.appendChild(meta);
        var actions = el("div", "made-file-actions");
        if (i > 0) {
          var cover = el("button", "made-file-btn", "Make it the cover"); cover.type = "button";
          cover.addEventListener("click", function () { record.files.splice(i, 1); record.files.unshift(f); renderFiles(); persist(); });
          actions.appendChild(cover);
        }
        var rm = el("button", "made-file-btn", "Remove"); rm.type = "button";
        rm.addEventListener("click", function () {
          if (!confirm("Remove " + f.name + " from this course? The file is deleted.")) return;
          record.files.splice(i, 1); renderFiles(); persist();
          if (acct && acct.request) acct.request("/work/file/delete", { method: "POST", body: { key: f.key } }).catch(function () {});
        });
        actions.appendChild(rm);
        li.appendChild(actions);
        list.appendChild(li);
      });
      if (!acct) {
        note.textContent = "Sign in to attach the work itself. The words save on this device either way.";
        addLabel.classList.add("is-off");
      } else {
        note.textContent = record.files.length ? "The first file is the cover: the one the Portfolio shows large." :
          "Photos, a film (MP4 or MOV), a recording, a PDF deck or paper, or a plain-text essay. Up to " + MAX_FILES + " files.";
        addLabel.classList.remove("is-off");
      }
    }

    function persist() {
      setStatus(status, "saving");
      save(lesson, heading, JSON.stringify(record)).then(function (st) { setStatus(status, st); },
                                                         function () { setStatus(status, "error"); });
    }
    var debounced = debounce(function () {
      record.title = title.value.trim(); record.form = form.value; record.link = link.value.trim();
      record.words = words.value.trim(); record.applied = applied.value.trim(); record.date = date.value; record.level = level.value;
      persist();
    }, SAVE_DELAY);

    add.addEventListener("change", function () {
      var acct = account();
      if (!acct || !acct.request) { note.textContent = "Sign in first to attach files."; return; }
      var picked = Array.prototype.slice.call(add.files || []);
      add.value = "";
      if (!picked.length) return;
      if (record.files.length + picked.length > MAX_FILES) { note.textContent = "Up to " + MAX_FILES + " files per course."; return; }
      var i = 0;
      (function next() {
        if (i >= picked.length) { note.textContent = "Added."; renderFiles(); persist(); refreshUrls(); return; }
        var f = picked[i++];
        note.textContent = "Uploading " + f.name + "…";
        uploadFile(acct, course, f, function (p) { note.textContent = "Uploading " + f.name + "… " + Math.round(p * 100) + "%"; })
          .then(function (file) { record.files.push(file); renderFiles(); next(); },
                function (err) { note.textContent = (err && err.message) || "The upload failed."; renderFiles(); });
      })();
    });

    read(lesson, heading).then(function (v) {
      if (v) {
        try {
          var r = JSON.parse(v);
          record.title = r.title || ""; record.form = r.form || "essay"; record.link = r.link || "";
          record.words = r.words || ""; record.applied = r.applied || ""; record.date = r.date || ""; record.level = r.level || "";
          record.files = Array.isArray(r.files) ? r.files.filter(function (f) { return f && f.key; }) : [];
        } catch (e) {}
      }
      title.value = record.title; form.value = record.form; link.value = record.link;
      words.value = record.words; applied.value = record.applied; date.value = record.date; level.value = record.level;
      renderFiles();
      refreshUrls();
    });
    [title, form, link, words, applied, date, level].forEach(function (x) {
      x.addEventListener("input", debounced);
      x.addEventListener("change", debounced);
    });
  }

  // ── The Commitment ─────────────────────────────────────────────────────────

  var COMMIT_LESSON = "/begin";
  var COMMIT_HEADING = "commitment";

  function showCommitted(block, iso) {
    var actions = block.querySelector("[data-commit-actions]");
    var done = block.querySelector("[data-commit-done]");
    if (actions) actions.hidden = true;
    if (done) {
      done.textContent = (done.getAttribute("data-template") || "You committed on {date}.").replace("{date}", longDate(iso));
      done.hidden = false;
    }
    Array.prototype.forEach.call(document.querySelectorAll("[data-after-commit]"), function (el) { el.hidden = false; });
  }

  function wireCommitment() {
    var block = document.querySelector("[data-sdit-commit]");
    if (!block) return;
    var after = document.querySelectorAll("[data-after-commit]");
    // Hidden only by script, so the questions are never lost without it.
    Array.prototype.forEach.call(after, function (el) { el.hidden = true; });
    read(COMMIT_LESSON, COMMIT_HEADING).then(function (iso) { if (iso) showCommitted(block, iso); });
    var btn = block.querySelector("[data-commit]");
    if (btn) btn.addEventListener("click", function () {
      var iso = todayISO();
      save(COMMIT_LESSON, COMMIT_HEADING, iso);
      showCommitted(block, iso);
      var q = document.getElementById("questions");
      if (q) q.scrollIntoView({ behavior: "smooth", block: "start" });
      var first = q && q.querySelector("textarea");
      if (first) setTimeout(function () { first.focus({ preventScroll: true }); }, 400);
    });
  }

  function fillCommitmentLines() {
    Array.prototype.forEach.call(document.querySelectorAll("[data-sdit-commitment-line]"), function (el) {
      var n = el.getAttribute("data-semester");
      read(COMMIT_LESSON, COMMIT_HEADING).then(function (iso) {
        el.textContent = iso
          ? "You committed on " + longDate(iso) + ". This is the end of Semester " + n + "."
          : "This is the end of Semester " + n + ".";
      });
    });
  }

  function fillRecalls() {
    Array.prototype.forEach.call(document.querySelectorAll("[data-sdit-recall]"), function (el) {
      var parts = el.getAttribute("data-sdit-recall").split("::");
      read(parts[0], parts[1]).then(function (v) {
        el.textContent = v || "You did not write an answer on Day 0. Write one now, and it will be the first.";
        if (!v) el.classList.add("is-empty");
      });
    });
  }

  // ── Init ───────────────────────────────────────────────────────────────────

  function init() {
    var lesson = lessonPath();
    wireCommitment();
    fillCommitmentLines();
    fillRecalls();
    Array.prototype.forEach.call(document.querySelectorAll("[data-sdit-answer]"), function (slot) {
      buildSlot(slot, lesson);
    });
    Array.prototype.forEach.call(document.querySelectorAll("[data-sdit-made]"), buildMade);
  }

  // Exposed for the Notebook, which reads the same store.
  window.SDITWork = { read: read, save: save, key: key, lessonPath: lessonPath, account: account };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () { setTimeout(init, 200); });
  } else {
    setTimeout(init, 200); // allow the header partial (and account.js) to settle
  }
})();
