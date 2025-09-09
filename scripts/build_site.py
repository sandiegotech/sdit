#!/usr/bin/env python3
"""
Build a minimal static site to browse repo content offline.

Outputs to: dist/site

Features:
- Converts Markdown under docs/, courses/, and programs/ to HTML
- Renders knowledge/*.yaml into simple HTML pages
- Generates a top-level index with organized navigation

Dependencies: pyyaml (already used) and markdown (auto-installed if missing)
"""
from __future__ import annotations

import os
import sys
import shutil
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dist" / "site"
ASSETS = OUT / "assets"


def ensure_markdown():
    try:
        import markdown  # noqa: F401
    except Exception:
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "markdown"], check=True)


def md_to_html(md_text: str) -> str:
    import markdown  # type: ignore
    return markdown.markdown(md_text, extensions=[
        "extra",
        "toc",
        "sane_lists",
        "tables",
        "fenced_code",
        "codehilite",
        "smarty",
    ])


def tmpl_page(title: str, body_html: str, breadcrumb: str = "") -> str:
    page_header = f"<header><h1>{title}</h1>{breadcrumb}</header>"
    return f"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title} — SDIT</title>
  <link rel="stylesheet" href="{{ASSET_REL}}assets/styles.css" />
</head>
<body>
  {page_header}
  <main>
  {body_html}
  </main>
  <footer>
    <p>Built locally from repo content.</p>
  </footer>
</body>
</html>
"""


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def asset_rel(from_path: Path) -> str:
    # Compute relative path from a page to OUT/ so we can link /assets
    # e.g., from OUT/docs/foo/bar.html to OUT/ -> ../../
    rel = os.path.relpath(OUT, start=from_path.parent)
    if rel == ".":
        rel = ""
    else:
        rel = rel.rstrip("/") + "/"
    # But from file:// context, relative path from OUT to OUT is ""; we want "" prefix
    return rel.replace("\\", "/")


def render_markdown_tree(src: Path, dest: Path) -> list[tuple[str, Path]]:
    """Convert all .md files under src into .html under dest, preserving structure.
    Returns: list of (title, output_path) for index building.
    """
    ensure_markdown()
    entries: list[tuple[str, Path]] = []
    for path in sorted(src.rglob("*.md")):
        md = path.read_text(encoding="utf-8")
        html = md_to_html(md)
        # Extract title from first H1 if present
        title = None
        for line in md.splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break
        if not title:
            title = path.stem.replace("-", " ").title()

        out_path = dest / path.relative_to(src)
        out_path = out_path.with_suffix(".html")

        # Prepare template and asset path
        page = tmpl_page(title, html)
        # Inject the correct asset relative prefix
        rel = asset_rel(out_path)
        page = page.replace("{ASSET_REL}", rel)
        write_file(out_path, page)
        entries.append((title, out_path))
    return entries


def render_knowledge(src: Path, dest: Path) -> list[tuple[str, Path]]:
    import yaml

    entries: list[tuple[str, Path]] = []

    # Index page for knowledge
    sections: list[str] = []

    for yml in sorted(src.glob("*.yaml")):
        data = yaml.safe_load(yml.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            continue
        meta = data.get("__meta__", {}) if isinstance(data.get("__meta__", {}), dict) else {}
        title = meta.get("title") or yml.stem.replace("-", " ").title()
        desc = meta.get("description") or ""

        # Build a simple HTML representation of the YAML mapping
        body_parts: list[str] = []
        if desc:
            body_parts.append(f"<p class=desc>{desc}</p>")

        # Render top-level keys except __meta__
        for k, v in data.items():
            if k == "__meta__":
                continue
            body_parts.append(f"<h2>{k}</h2>")
            body_parts.append(yaml_to_html(v))

        body_html = "\n".join(body_parts)
        out_path = dest / (yml.stem + ".html")
        page = tmpl_page(title, body_html)
        page = page.replace("{ASSET_REL}", asset_rel(out_path))
        write_file(out_path, page)

        entries.append((title, out_path))
        sections.append(f"<li><a href='{yml.stem}.html'><strong>{title}</strong></a> — {desc}</li>")

    # knowledge index page
    index_body = """
    <h2>Knowledge Base</h2>
    <p>Canonical YAML maps for identity, principles, programs, research, and more.</p>
    <ul>
    {items}
    </ul>
    """.format(items="\n".join(sections))
    out_index = dest / "index.html"
    page = tmpl_page("Knowledge", index_body)
    page = page.replace("{ASSET_REL}", asset_rel(out_index))
    write_file(out_index, page)

    return entries


def yaml_to_html(value) -> str:
    import html
    import yaml
    # Render dicts and lists recursively into definition lists and lists.
    if isinstance(value, dict):
        items = []
        for k, v in value.items():
            items.append(f"<dt>{html.escape(str(k))}</dt><dd>{yaml_to_html(v)}</dd>")
        return f"<dl>\n{''.join(items)}\n</dl>"
    if isinstance(value, list):
        items = []
        for v in value:
            items.append(f"<li>{yaml_to_html(v)}</li>")
        return f"<ul>\n{''.join(items)}\n</ul>"
    # Scalars
    if value is None:
        return "<em>null</em>"
    if isinstance(value, (int, float)):
        return str(value)
    s = str(value)
    # Lightly detect URLs
    if s.startswith("http://") or s.startswith("https://"):
        return f"<a href='{html.escape(s)}'>{html.escape(s)}</a>"
    return html.escape(s)


def build_index(knowledge_entries: list[tuple[str, Path]], docs_entries: list[tuple[str, Path]], courses_entries: list[tuple[str, Path]]):
    def rel_from_root(p: Path) -> str:
        return p.resolve().relative_to(OUT).as_posix()

    def mk_list(title: str, entries: Iterable[tuple[str, Path]]) -> str:
        items = [f"<li><a href='{rel_from_root(p)}'>{t}</a></li>" for t, p in entries]
        if not items:
            items = ["<li><em>No items found.</em></li>"]
        return f"<section><h2>{title}</h2><ul>\n" + "\n".join(items) + "\n</ul></section>"

    body = [
        "<p>Browse SDIT content: Knowledge base, Docs, and Courses.</p>",
        mk_list("Knowledge", sorted(knowledge_entries, key=lambda x: x[0].lower())),
        mk_list("Docs", sorted(docs_entries, key=lambda x: x[0].lower())),
        mk_list("Courses", sorted(courses_entries, key=lambda x: x[0].lower())),
    ]
    html = tmpl_page("SDIT Content Index", "\n".join(body))
    html = html.replace("{ASSET_REL}", asset_rel(OUT / "index.html"))
    write_file(OUT / "index.html", html)


def write_assets():
    ASSETS.mkdir(parents=True, exist_ok=True)
    # Disable Jekyll processing on GitHub Pages so files are served as-is
    write_file(OUT / ".nojekyll", "")
    css = """
    :root { --bg: #0c0d10; --fg: #e8e8ea; --muted: #a7a7ad; --link: #7cc4ff; --card: #17181d; }
    * { box-sizing: border-box; }
    body { margin: 0; font-family: -apple-system, Segoe UI, Roboto, Inter, sans-serif; color: var(--fg); background: var(--bg); line-height: 1.6; }
    header { padding: 16px 20px; border-bottom: 1px solid #22242a; }
    header h1 { margin: 0 0 4px; font-size: 20px; }
    main { padding: 20px; max-width: 900px; margin: 0 auto; }
    section { background: var(--card); padding: 12px 16px; margin: 12px 0; border-radius: 8px; }
    ul { padding-left: 20px; }
    a { color: var(--link); text-decoration: none; }
    a:hover { text-decoration: underline; }
    h1, h2, h3 { color: #fff; }
    code, pre { background: #101217; border-radius: 6px; }
    pre { padding: 12px; overflow: auto; }
    dl { display: grid; grid-template-columns: max-content 1fr; gap: 6px 12px; }
    dt { color: #c9c9ce; }
    dd { margin: 0 0 6px 0; }
    .desc { color: var(--muted); }
    footer { padding: 16px 20px; color: var(--muted); border-top: 1px solid #22242a; margin-top: 24px; }
    """
    write_file(ASSETS / "styles.css", css)


def main(argv: list[str] | None = None) -> int:
    # Reset output dir
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True, exist_ok=True)
    write_assets()

    knowledge_entries = render_knowledge(ROOT / "knowledge", OUT / "knowledge")
    docs_entries = render_markdown_tree(ROOT / "docs", OUT / "docs")
    courses_entries = render_markdown_tree(ROOT / "courses", OUT / "courses")
    programs_entries = render_markdown_tree(ROOT / "programs", OUT / "programs")

    # Add simple section index pages for docs/ and courses/
    for (title, out_path), section_name in (
        (("Docs", OUT / "docs" / "index.html"), "docs"),
        (("Courses", OUT / "courses" / "index.html"), "courses"),
        (("Programs", OUT / "programs" / "index.html"), "programs"),
    ):
        # list all pages under the section
        entries = []
        for p in sorted((OUT / section_name).rglob("*.html")):
            if p.name == "index.html":
                continue
            rel = p.resolve().relative_to(OUT / section_name).as_posix()
            # Derive display from filename
            display = p.stem.replace("-", " ").title()
            entries.append(f"<li><a href='{rel}'>{display}</a></li>")
        body = f"<h2>{title}</h2><ul>\n" + "\n".join(entries) + "\n</ul>"
        page = tmpl_page(title, body)
        page = page.replace("{ASSET_REL}", asset_rel(out_path))
        write_file(out_path, page)

    build_index(knowledge_entries, docs_entries, courses_entries + programs_entries)
    print(f"Wrote static site to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
