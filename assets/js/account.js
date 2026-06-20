/**
 * account.js — the SDIT Card (Phase 1, web client)
 *
 * Passwordless sign-in (email + code) and cloud sync of student work.
 *   - When signed in, student-work.js loads/saves answers through the account
 *     API so they follow you across browsers and devices.
 *   - When signed out — or before the API is configured — nothing changes: the
 *     site works exactly as before, on localStorage alone.
 *
 * Configure by setting window.SDIT_ACCOUNT_API (the deployed ApiUrl) before
 * this script loads; see partials/header.html. With it unset, no UI appears.
 */

(function () {
  "use strict";

  var API = (window.SDIT_ACCOUNT_API || "").replace(/\/+$/, "");
  var TOKEN_KEY = "sdit:session";
  var PROFILE_KEY = "sdit:profile";

  // ── Session state (localStorage) ───────────────────────────────────────────

  function token() { return localStorage.getItem(TOKEN_KEY) || ""; }

  function setToken(t) {
    if (t) localStorage.setItem(TOKEN_KEY, t);
    else localStorage.removeItem(TOKEN_KEY);
  }

  function cachedProfile() {
    try { return JSON.parse(localStorage.getItem(PROFILE_KEY) || "null"); }
    catch (e) { return null; }
  }

  function setProfile(p) {
    if (p) localStorage.setItem(PROFILE_KEY, JSON.stringify(p));
    else localStorage.removeItem(PROFILE_KEY);
    // Keep the portal/marketing toggle in sync with auth state after load.
    document.documentElement.classList.toggle("sdit-authed", !!p);
    render();
  }

  // ── API ────────────────────────────────────────────────────────────────────

  function request(path, opts) {
    opts = opts || {};
    var headers = { "Content-Type": "application/json" };
    if (token()) headers["Authorization"] = "Bearer " + token();
    return fetch(API + path, {
      method: opts.method || "GET",
      headers: headers,
      body: opts.body ? JSON.stringify(opts.body) : undefined,
    }).then(function (r) {
      return r.json().catch(function () { return {}; }).then(function (data) {
        if (!r.ok) {
          var err = new Error(data.error || ("HTTP " + r.status));
          err.status = r.status;
          throw err;
        }
        return data;
      });
    });
  }

  var Account = {
    configured: function () { return !!API; },
    isSignedIn: function () { return !!token() && !!cachedProfile(); },
    profile: function () { return cachedProfile(); },

    requestCode: function (email) {
      return request("/auth/request", { method: "POST", body: { email: email } });
    },
    verify: function (email, code) {
      return request("/auth/verify", { method: "POST", body: { email: email, code: code } })
        .then(function (d) { setToken(d.token); setProfile(d.profile); return d.profile; });
    },
    subscribe: function (email) {
      return request("/subscribe", { method: "POST", body: { email: email } });
    },
    signOut: function () { setToken(null); setProfile(null); },
    openSignIn: function () { openDialog(); },

    progress: function () {
      if (!this.isSignedIn()) return Promise.resolve([]);
      return request("/progress")
        .then(function (d) { return d.lessons || []; })
        .catch(function () { return []; });
    },

    loadWork: function (lesson) {
      if (!this.isSignedIn()) return Promise.resolve({});
      return request("/work?lesson=" + encodeURIComponent(lesson))
        .then(function (d) { return d.responses || {}; })
        .catch(function () { return {}; });
    },
    saveWork: function (lesson, heading, content) {
      if (!this.isSignedIn()) return Promise.resolve(false);
      return request("/work", { method: "PUT", body: { lesson: lesson, heading: heading, content: content } })
        .then(function () { return true; })
        .catch(function () { return false; });
    },

    enrollments: function () {
      if (!this.isSignedIn()) return Promise.resolve([]);
      return request("/enrollments")
        .then(function (d) { return d.courses || []; })
        .catch(function () { return []; });
    },
    enroll: function (course) {
      return request("/enroll", { method: "POST", body: { course: course } })
        .then(function () { return true; }).catch(function () { return false; });
    },
    unenroll: function (course) {
      return request("/unenroll", { method: "POST", body: { course: course } })
        .then(function () { return true; }).catch(function () { return false; });
    },
  };

  // Re-check the session in the background. Only a definitive 401 (bad/expired
  // token) signs you out — network blips, cold starts and 5xx must NOT, or a
  // single hiccup on navigation would drop the session.
  function refreshProfile() {
    if (!API || !token()) return;
    request("/me")
      .then(function (d) { setProfile(d.profile); })
      .catch(function (err) { if (err && err.status === 401) Account.signOut(); });
  }

  // ── UI: header chip + sign-in dialog ───────────────────────────────────────

  var ROLE_LABEL = {
    subscriber: "Subscriber", visitor: "Visitor", student: "Student",
    fellow: "Fellow", professor: "Professor",
  };

  function el(tag, attrs, children) {
    var node = document.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(function (k) {
      if (k === "class") node.className = attrs[k];
      else if (k === "text") node.textContent = attrs[k];
      else node.setAttribute(k, attrs[k]);
    });
    (children || []).forEach(function (c) { node.appendChild(c); });
    return node;
  }

  function render(tries) {
    if (!API) return;
    var mount = document.getElementById("sdit-account");
    if (!mount) {
      // The header partial loads asynchronously — wait for the mount point.
      if ((tries || 0) < 40) setTimeout(function () { render((tries || 0) + 1); }, 100);
      return;
    }
    mount.innerHTML = "";

    if (Account.isSignedIn()) {
      var p = Account.profile();
      var chip = el("span", { class: "account-chip" });
      chip.appendChild(el("span", { class: "account-role", text: ROLE_LABEL[p.role] || "Member" }));
      var out = el("button", { class: "account-link", type: "button", text: "Sign out" });
      out.addEventListener("click", function () { Account.signOut(); location.reload(); });
      chip.appendChild(out);
      mount.appendChild(chip);
    } else {
      var btn = el("button", { class: "account-link account-signin", type: "button", text: "Sign in" });
      btn.addEventListener("click", openDialog);
      mount.appendChild(btn);
    }
  }

  var dialog = null;

  function buildDialog() {
    var email = el("input", { class: "account-input", type: "email", placeholder: "you@example.com", autocomplete: "email" });
    var code = el("input", { class: "account-input", type: "text", inputmode: "numeric", placeholder: "6-digit code", autocomplete: "one-time-code", maxlength: "6" });
    var msg = el("p", { class: "account-msg" });
    var submit = el("button", { class: "account-submit", type: "submit" });

    var stepEmail = el("div", { class: "account-step" }, [
      el("label", { class: "account-label", text: "Email" }), email,
    ]);
    var stepCode = el("div", { class: "account-step", hidden: "" }, [
      el("label", { class: "account-label", text: "Enter the code we emailed you" }), code,
    ]);

    var form = el("form", { class: "account-form" }, [
      el("h2", { class: "account-title", text: "Your SDIT Card" }),
      el("p", { class: "account-sub", text: "Sign in to save your work and pick up on any device." }),
      stepEmail, stepCode, msg, submit,
    ]);

    var state = "email";
    function show(step) {
      state = step;
      stepEmail.hidden = step !== "email";
      stepCode.hidden = step !== "code";
      submit.textContent = step === "email" ? "Email me a code" : "Sign in";
      msg.textContent = "";
      (step === "email" ? email : code).focus();
    }

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      submit.disabled = true;
      if (state === "email") {
        Account.requestCode(email.value.trim())
          .then(function () { submit.disabled = false; show("code"); })
          .catch(function (err) { submit.disabled = false; msg.textContent = err.message; });
      } else {
        Account.verify(email.value.trim(), code.value.trim())
          .then(function () { close(); location.reload(); })
          .catch(function (err) { submit.disabled = false; msg.textContent = err.message; });
      }
    });

    var panel = el("div", { class: "account-panel", role: "dialog", "aria-modal": "true" }, [form]);
    var closeBtn = el("button", { class: "account-close", type: "button", "aria-label": "Close", text: "×" });
    closeBtn.addEventListener("click", close);
    panel.appendChild(closeBtn);

    var overlay = el("div", { class: "account-overlay", hidden: "" }, [panel]);
    overlay.addEventListener("click", function (e) { if (e.target === overlay) close(); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") close(); });

    document.body.appendChild(overlay);
    return { overlay: overlay, show: show };
  }

  function openDialog() {
    if (!dialog) dialog = buildDialog();
    dialog.overlay.hidden = false;
    dialog.show("email");
  }

  function close() {
    if (dialog) dialog.overlay.hidden = true;
  }

  // ── Homepage engagement controls ───────────────────────────────────────────
  // [data-sdit-signin] → open the Visitor sign-in dialog.
  // [data-sdit-subscribe] (a <form> with an email input) → join The Daily.

  function wireEngagement() {
    Array.prototype.forEach.call(document.querySelectorAll("[data-sdit-signin]"), function (b) {
      if (b._sditWired) return;
      b._sditWired = true;
      b.addEventListener("click", function (e) { e.preventDefault(); openDialog(); });
    });
    Array.prototype.forEach.call(document.querySelectorAll("[data-sdit-subscribe]"), function (form) {
      if (form._sditWired) return;
      form._sditWired = true;
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        var input = form.querySelector('input[type="email"]');
        var msg = form.querySelector(".way-msg");
        var email = ((input && input.value) || "").trim();
        if (!email) return;
        if (msg) msg.textContent = "Adding you…";
        Account.subscribe(email).then(function () {
          if (msg) msg.textContent = "You're on the list. Watch your inbox.";
          if (input) input.value = "";
        }).catch(function () {
          if (msg) msg.textContent = "That didn't go through — try again.";
        });
      });
    });
  }

  // ── Init ─────────────────────────────────────────────────────────────────────

  function init() {
    render();
    refreshProfile();
    wireEngagement();
  }

  window.SDITAccount = Account;

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    setTimeout(init, 200); // allow header partial to settle
  }
})();
