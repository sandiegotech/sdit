/**
 * student-work.js
 *
 * Converts _italic placeholder_ paragraphs into interactive response fields
 * throughout the lesson — wherever the author placed them, right in context.
 *
 * Save behaviour:
 *   - Saves to localStorage immediately (debounced 1.5 s after you stop typing)
 *   - On localhost: also POSTs to /api/save → written to my-work/ directory
 *     and pushed to GitHub automatically
 *   - On GitHub Pages: localStorage only — shows "Saved locally"
 *   - On page open: restores from localStorage; on localhost also loads from
 *     server so responses survive across browsers/devices
 */

(function () {
  "use strict";

  var SAVE_DELAY = 1500;

  // ── Utilities ──────────────────────────────────────────────────────────────

  function isLocalhost() {
    return location.hostname === "localhost" || location.hostname === "127.0.0.1";
  }

  function lessonPath() {
    // /courses/LBS-101/day-01.html  →  /courses/LBS-101/day-01
    return location.pathname.replace(/\.html$/, "");
  }

  function storageKey(heading) {
    return "sdit:" + lessonPath() + "::" + heading;
  }

  function debounce(fn, delay) {
    var t;
    return function () {
      var a = arguments;
      clearTimeout(t);
      t = setTimeout(function () { fn.apply(null, a); }, delay);
    };
  }

  // ── Status badge ───────────────────────────────────────────────────────────

  function makeStatus() {
    var el = document.createElement("span");
    el.className = "response-status";
    return el;
  }

  function setStatus(el, state) {
    var labels = { saving: "Saving…", saved: "Saved ✓", local: "Saved locally", error: "Error saving" };
    el.className = "response-status response-status--" + state;
    el.textContent = labels[state] || "";
    if (state === "saved" || state === "local") {
      clearTimeout(el._t);
      el._t = setTimeout(function () {
        el.textContent = "";
        el.className = "response-status";
      }, 3000);
    }
  }

  // ── Server load / save ─────────────────────────────────────────────────────

  function loadFromServer(onDone) {
    fetch("/api/load?file=" + encodeURIComponent(lessonPath()))
      .then(function (r) { return r.json(); })
      .then(function (d) { onDone(d || {}); })
      .catch(function () { onDone({}); });
  }

  function saveToServer(heading, content, statusEl) {
    setStatus(statusEl, "saving");
    fetch("/api/save", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ file: lessonPath(), heading: heading, content: content }),
    })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        setStatus(statusEl, d.ok ? "saved" : "error");
        if (!d.ok) console.warn("Save error:", d.error);
      })
      .catch(function () { setStatus(statusEl, "error"); });
  }

  // ── Placeholder detection ──────────────────────────────────────────────────

  /**
   * True if a <p> element's entire visible text is wrapped in <em>.
   * This matches _italic placeholder_ paragraphs after markdown rendering.
   */
  function isPlaceholderEm(p) {
    var text = p.textContent.trim();
    if (!text) return false;
    var emText = Array.prototype.map
      .call(p.querySelectorAll("em"), function (e) { return e.textContent; })
      .join("")
      .trim();
    return emText === text;
  }

  // ── Build one response field ───────────────────────────────────────────────

  function buildField(placeholder, heading, serverResponses) {
    var key       = storageKey(heading);
    var localVal  = localStorage.getItem(key) || "";
    var serverVal = (serverResponses && serverResponses[heading]) || "";
    var saved     = localVal || serverVal; // local wins (more recent)

    var wrap = document.createElement("div");
    wrap.className = "response-field";

    var ta = document.createElement("textarea");
    ta.className     = "response-textarea";
    ta.placeholder   = placeholder.textContent.trim();
    ta.rows          = 5;
    ta.value         = saved;
    ta.setAttribute("aria-label", heading);

    var status = makeStatus();
    wrap.appendChild(ta);
    wrap.appendChild(status);
    placeholder.replaceWith(wrap);

    // Auto-resize to content
    function resize() {
      ta.style.height = "auto";
      ta.style.height = (ta.scrollHeight + 2) + "px";
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

    ta.addEventListener("input", function () { resize(); debouncedSave(); });
  }

  // ── Scan the page ──────────────────────────────────────────────────────────

  function enhance(serverResponses) {
    var main = document.querySelector("main");
    if (!main) return;

    var currentHeading = null;

    // querySelectorAll returns elements in document order — perfect for this
    var nodes = main.querySelectorAll("h2, h3, p, blockquote");
    for (var i = 0; i < nodes.length; i++) {
      var node = nodes[i];
      var tag  = node.tagName;

      if (tag === "H2" || tag === "H3") {
        currentHeading = node.textContent.trim();

      } else if (currentHeading && tag === "P" && isPlaceholderEm(node)) {
        buildField(node, currentHeading, serverResponses);

      } else if (currentHeading && tag === "BLOCKQUOTE") {
        var inner = node.querySelector("p");
        if (inner && isPlaceholderEm(inner)) {
          buildField(node, currentHeading, serverResponses);
        }
      }
    }
  }

  // ── Init ───────────────────────────────────────────────────────────────────

  function init() {
    if (isLocalhost()) {
      loadFromServer(enhance);
    } else {
      enhance({});
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    setTimeout(init, 200); // allow data-include partials to settle
  }

})();
