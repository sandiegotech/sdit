#!/usr/bin/env python3
"""site_polish.py — the last pass over every page the site publishes.

Some things must be true of every page, whichever script or hand made it:

  - favicon, touch icon, manifest, and theme color in <head>
  - a meta description (from the page's first paragraph when it has none)
  - <main id="main">, the target of the masthead's skip link
  - the entrance-animation guard: animation runs only when the page is visible
  - every <img> loads lazily and sends no referrer to the image host
  - video embeds use YouTube's cookieless domain

Then robots.txt (the Institute's crawler policy) and sitemap.xml.

Idempotent and deterministic: a second run changes nothing, and nothing here
reads the clock or git, so CI's drift check rebuilds the same bytes.
"""
from __future__ import annotations

import html as _html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://learn.sandiegotech.org"
SKIP_DIRS = {".git", "dist", "account", "infra", "node_modules", "partials", "scripts", ".github", ".vscode", "my-work"}

HEAD_MARK = "<!-- sdit:head -->"
HEAD = (HEAD_MARK + "\n"
        '  <link rel="icon" href="/favicon.ico" sizes="any" />\n'
        '  <link rel="apple-touch-icon" href="/apple-touch-icon.png" />\n'
        '  <link rel="manifest" href="/site.webmanifest" />\n'
        '  <meta name="theme-color" content="#101C2C" />\n'
        "  <script>try{var d=document.documentElement;if(document.visibilityState===\"visible\"){d.classList.add(\"sdit-animate\");setTimeout(function(){d.classList.add(\"sdit-settled\")},1200)}}catch(e){}</script>\n")


def pages(root: Path = ROOT) -> list[Path]:
    out = []
    for p in sorted(root.rglob("*.html")):
        rel = p.relative_to(root)
        if rel.parts and rel.parts[0] in SKIP_DIRS:
            continue
        out.append(p)
    return out


def is_redirect(text: str) -> bool:
    return 'http-equiv="refresh"' in text


def _first_paragraph(text: str) -> str:
    main = text.split("<main", 1)[1] if "<main" in text else text
    for m in re.finditer(r"<p[^>]*>(.*?)</p>", main, flags=re.S):
        t = re.sub(r"<[^>]+>", "", m.group(1))
        t = _html.unescape(" ".join(t.split()))
        if len(t) > 40:
            if len(t) > 158:
                cut = t[:158].rsplit(" ", 1)[0].rstrip(",;:—-")
                t = cut + "…"
            return t
    return ""


def polish(text: str) -> str:
    if is_redirect(text) or "<head>" not in text:
        return text
    if HEAD_MARK in text and HEAD not in text:
        text = re.sub(re.escape(HEAD_MARK) + r"\n.*?</script>\n", lambda _m: HEAD, text, count=1, flags=re.S)
    if HEAD_MARK not in text:
        text = re.sub(r'(<meta name="viewport"[^>]*>\n)', lambda m: m.group(1) + "  " + HEAD, text, count=1)
    if 'name="description"' not in text:
        desc = _first_paragraph(text)
        if desc:
            tag = f'  <meta name="description" content="{_html.escape(desc, quote=True)}">\n'
            text = text.replace("  " + HEAD_MARK, tag + "  " + HEAD_MARK, 1)
    text = re.sub(r"<main(?![^>]*\bid=)(\s|>)", r'<main id="main"\1', text, count=1)

    def img(m):
        tag = m.group(0)
        if "loading=" not in tag:
            tag = tag.replace("<img ", '<img loading="lazy" ', 1)
        if "referrerpolicy=" not in tag:
            tag = tag.replace("<img ", '<img referrerpolicy="no-referrer" ', 1)
        return tag
    text = re.sub(r"<img\b[^>]*>", img, text)
    text = text.replace("https://www.youtube.com/embed/", "https://www.youtube-nocookie.com/embed/")
    return text


ROBOTS = """# San Diego Institute of Technology — the Curriculum. Crawler policy.
#
# The same position as sandiegotech.org: the curriculum is open to read, and
# open to find. Search engines and readers are welcome. Bulk collection for
# model training is a separate act from reading, and it is the one the
# Institute reserves. Robots.txt is a request, not an enforcement mechanism.

User-agent: *
Content-Signal: search=yes, ai-train=no, use=reference
Allow: /
Disallow: /api/

User-agent: Amazonbot
Disallow: /

User-agent: Applebot-Extended
Disallow: /

User-agent: Bytespider
Disallow: /

User-agent: CCBot
Disallow: /

User-agent: ClaudeBot
Disallow: /

User-agent: Google-Extended
Disallow: /

User-agent: GPTBot
Disallow: /

User-agent: meta-externalagent
Disallow: /

Sitemap: https://learn.sandiegotech.org/sitemap.xml
"""

MANIFEST = """{
  "name": "San Diego Institute of Technology — The Curriculum",
  "short_name": "SDIT",
  "start_url": "/",
  "icons": [
    {"src": "/assets/icon-192.png", "sizes": "192x192", "type": "image/png"},
    {"src": "/assets/icon-512.png", "sizes": "512x512", "type": "image/png"}
  ],
  "theme_color": "#101C2C",
  "background_color": "#FCFBF8",
  "display": "browser"
}
"""


def url_for(p: Path, root: Path) -> str:
    rel = p.relative_to(root).as_posix()
    if rel == "index.html":
        return SITE + "/"
    if rel.endswith("/index.html"):
        return SITE + "/" + rel[: -len("index.html")]
    return SITE + "/" + rel


def sitemap(root: Path) -> str:
    urls = []
    for p in pages(root):
        rel = p.relative_to(root).as_posix()
        if rel == "404.html":
            continue
        if is_redirect(p.read_text(encoding="utf-8")):
            continue
        urls.append(url_for(p, root))
    body = "\n".join(f"  <url><loc>{_html.escape(u)}</loc></url>" for u in sorted(urls))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + "\n</urlset>\n")


def run(write, out: Path = ROOT) -> int:
    changed = 0
    for p in pages(out):
        text = p.read_text(encoding="utf-8")
        new = polish(text)
        if new != text:
            write(p, new)
            changed += 1
    write(out / "robots.txt", ROBOTS)
    write(out / "site.webmanifest", MANIFEST)
    write(out / "sitemap.xml", sitemap(out))
    return changed
