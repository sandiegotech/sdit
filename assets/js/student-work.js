/**
 * student-work.js
 *
 * Converts "My Work" placeholder paragraphs into interactive textareas.
 * - Saves to localStorage immediately on every keystroke (debounced)
 * - POSTs to /api/save when running on localhost
 * - Shows a small "Saved ✓" / "Saved locally" indicator per field
 */

(function () {
  "use strict";

  var SAVE_DELAY = 1500; // ms before autosave triggers

  // ── Utilities ──────────────────────────────────────────────────────────────

  function isLocalhost() {
    return (
      location.hostname === "localhost" ||
      location.hostname === "127.0.0.1"
    );
  }

  /** Derive a stable localStorage key from the page path + heading text. */
  function storageKey(heading) {
    return "sdit:" + location.pathname + "::" + heading;
  }

  /**
   * Find the .md source file path for the current page.
   * HTML pages live at /courses/LBS-101/day-01.html → courses/LBS-101/day-01.md
   */
  function mdPath() {
    return location.pathname.replace(/\.html$/, ".md");
  }

  function debounce(fn, delay) {
    var timer;
    return function () {
      var args = arguments;
      clearTimeout(timer);
      timer = setTimeout(function () { fn.apply(null, args); }, delay);
    };
  }

  // ── Status indicator ───────────────────────────────────────────────────────

  function makeStatus() {
    var el = document.createElement("span");
    el.className = "response-status";
    return el;
  }

  function setStatus(el, state) {
    el.className = "response-status response-status--" + state;
    var labels = { saving: "Saving…", saved: "Saved ✓", local: "Saved locally", error: "Error saving" };
    el.textContent = labels[state] || "";
    if (state === "saved" || state === "local") {
      clearTimeout(el._timer);
      el._timer = setTimeout(function () { el.textContent = ""; el.className = "response-status"; }, 3000);
    }
  }

  // ── Server save ────────────────────────────────────────────────────────────

  function saveToServer(heading, content, statusEl) {
    setStatus(statusEl, "saving");
    var body = JSON.stringify({ file: mdPath(), heading: heading, content: content });
    fetch("/api/save", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: body,
    })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        setStatus(statusEl, data.ok ? "saved" : "error");
        if (!data.ok) console.warn("Save error:", data.error);
      })
      .catch(function () { setStatus(statusEl, "error"); });
  }

  // ── Build a response field ─────────────────────────────────────────────────

  /**
   * Replace a placeholder paragraph with a textarea + status indicator.
   * @param {Element} placeholder  - the <p><em>…</em></p> element to replace
   * @param {string}  heading      - text of the parent ### heading
   */
  function buildField(placeholder, heading) {
    var key = storageKey(heading);
    var saved = localStorage.getItem(key) || "";

    // Wrapper
    var wrap = document.createElement("div");
    wrap.className = "response-field";

    // Textarea
    var ta = document.createElement("textarea");
    ta.className = "response-textarea";
    ta.placeholder = placeholder.textContent.trim();
    ta.rows = 6;
    ta.value = saved;
    ta.setAttribute("aria-label", heading);

    // Status
    var status = makeStatus();

    wrap.appendChild(ta);
    wrap.appendChild(status);
    placeholder.replaceWith(wrap);

    // Auto-resize
    function resize() {
      ta.style.height = "auto";
      ta.style.height = ta.scrollHeight + "px";
    }
    resize();

    var debouncedSave = debounce(function () {
      var val = ta.value;
      localStorage.setItem(key, val);
      if (isLocalhost()) {
        saveToServer(heading, val, status);
      } else {
        setStatus(status, "local");
      }
    }, SAVE_DELAY);

    ta.addEventListener("input", function () {
      resize();
      debouncedSave();
    });
  }

  // ── Helpers ────────────────────────────────────────────────────────────────

  /** True if a <p> element's sole meaningful content is an <em> (i.e. a placeholder). */
  function isPlaceholderEm(p) {
    var trimmed = p.textContent.trim();
    if (!trimmed) return false;
    // All visible text must be inside <em> tags
    var ems = p.querySelectorAll("em");
    if (!ems.length) return false;
    var emText = Array.prototype.map.call(ems, function (e) { return e.textContent; }).join("").trim();
    return emText === trimmed;
  }

  // ── Find and wire My Work section ──────────────────────────────────────────

  function enhance() {
    // Find ## My Work heading in the rendered HTML
    var headings = document.querySelectorAll("h2");
    var myWorkH2 = null;
    for (var i = 0; i < headings.length; i++) {
      if (/my work/i.test(headings[i].textContent)) {
        myWorkH2 = headings[i];
        break;
      }
    }
    if (!myWorkH2) return;

    // Collect all ### sub-headings and their following placeholder paragraph.
    // Placeholders are <p><em>text</em></p> or <blockquote><p><em>text</em></p></blockquote>
    // — markdown strips the _ markers, leaving only <em> content.
    var node = myWorkH2.nextElementSibling;
    var currentHeading = null;

    while (node) {
      if (node.tagName === "H2") break; // stop at next H2

      if (node.tagName === "H3") {
        currentHeading = node.textContent.trim();
      } else if (currentHeading) {
        // Plain paragraph placeholder: <p><em>...</em></p>
        if (node.tagName === "P" && isPlaceholderEm(node)) {
          buildField(node, currentHeading);
        }
        // Blockquote placeholder (e.g. Key Quote): <blockquote><p><em>...</em></p></blockquote>
        else if (node.tagName === "BLOCKQUOTE") {
          var inner = node.querySelector("p");
          if (inner && isPlaceholderEm(inner)) {
            buildField(node, currentHeading);
          }
        }
      }

      node = node.nextElementSibling;
    }
  }

  // Run after DOM + includes are ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", enhance);
  } else {
    // Delay slightly to allow data-include partials to load
    setTimeout(enhance, 200);
  }
})();
