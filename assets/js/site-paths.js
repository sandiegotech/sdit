// Resolve site paths correctly for both custom-domain hosting and GitHub Pages project sites.
(function () {
  if (window.__sditPathsReady) {
    return;
  }
  window.__sditPathsReady = true;

  function detectBasePath() {
    const pathname = window.location.pathname || "/";
    const parts = pathname.split("/").filter(Boolean);

    if (!window.location.hostname.endsWith("github.io") || !parts.length) {
      return "";
    }

    const first = parts[0];
    if (!first || /\.[a-z0-9]+$/i.test(first)) {
      return "";
    }

    return "/" + first;
  }

  const basePath = detectBasePath();

  function stripBasePath(path) {
    if (!basePath) {
      return path;
    }

    if (path === basePath) {
      return "/";
    }

    if (path.indexOf(basePath + "/") === 0) {
      return path.slice(basePath.length) || "/";
    }

    return path;
  }

  function resolvePath(path) {
    if (
      !path ||
      path[0] === "#" ||
      /^[a-z][a-z0-9+.-]*:/i.test(path) ||
      path.indexOf("//") === 0
    ) {
      return path;
    }

    if (path[0] === "/") {
      return (basePath || "") + path;
    }

    return path;
  }

  function rewritePaths(root) {
    const scope = root || document;
    const attrs = ["href", "src", "data-include", "action", "poster"];

    attrs.forEach(function (attr) {
      scope.querySelectorAll("[" + attr + "]").forEach(function (node) {
        const value = node.getAttribute(attr);
        const resolved = resolvePath(value);
        if (resolved && resolved !== value) {
          node.setAttribute(attr, resolved);
        }
      });
    });
  }

  window.__sditBasePath = basePath;
  window.__sditResolvePath = resolvePath;
  window.__sditStripBasePath = stripBasePath;
  window.__sditRewritePaths = rewritePaths;

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      rewritePaths(document);
    });
  } else {
    rewritePaths(document);
  }
})();
