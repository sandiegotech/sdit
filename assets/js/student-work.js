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

  function writeLocal(lesson, heading, value) {
    try { localStorage.setItem(key(lesson, heading), value); return true; } catch (e) { return false; }
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
    hint.textContent = account()
      ? "Kept in your Notebook, on every device you sign in on."
      : "Kept in your Notebook on this device. Sign in to keep it everywhere.";
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
  }

  // Exposed for the Notebook, which reads the same store.
  window.SDITWork = { read: read, save: save, key: key, lessonPath: lessonPath };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () { setTimeout(init, 200); });
  } else {
    setTimeout(init, 200); // allow the header partial (and account.js) to settle
  }
})();
