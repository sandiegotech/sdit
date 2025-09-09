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
import argparse
from typing import Iterable, Dict


ROOT = Path(__file__).resolve().parents[1]
# Defaults; may be overridden via --out
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


def build_index(title_map: Dict[Path, str]) -> None:
    def rel_from_root(p: Path) -> str:
        return p.resolve().relative_to(OUT).as_posix()

    def humanize(name: str) -> str:
        return name.replace("-", " ").replace("_", " ").title()

    def display_for_file(p: Path) -> str:
        return title_map.get(p.resolve(), p.stem.replace("-", " ").title())

    def tree_html(base: Path) -> str:
        if not base.exists():
            return "<p><em>None</em></p>"
        def walk(dir_path: Path) -> str:
            # list subdirs then files (html only)
            subs = sorted([d for d in dir_path.iterdir() if d.is_dir()])
            files = sorted([f for f in dir_path.iterdir() if f.is_file() and f.suffix == ".html"])
            items: list[str] = []
            # directories
            for d in subs:
                idx = d / "index.html"
                label = title_map.get(idx.resolve(), humanize(d.name)) if idx.exists() else humanize(d.name)
                inner = walk(d)
                if idx.exists():
                    items.append(
                        "<li><details><summary><a href='" + rel_from_root(idx) + "'>" + label + "</a></summary>" + inner + "</details></li>"
                    )
                else:
                    items.append(
                        "<li><details><summary>" + label + "</summary>" + inner + "</details></li>"
                    )
            # files
            for f in files:
                if f.name == "index.html":
                    continue
                items.append(f"<li><a href='{rel_from_root(f)}'>{display_for_file(f)}</a></li>")
            if not items:
                return ""
            return "<ul>" + "\n".join(items) + "</ul>"

        return walk(base) or "<p><em>None</em></p>"

    sections = []
    sections.append(f"<details class='root'><summary>Knowledge</summary>{tree_html(OUT / 'knowledge')}</details>")
    sections.append(f"<details class='root'><summary>Programs</summary>{tree_html(OUT / 'programs')}</details>")
    sections.append(f"<details class='root'><summary>Courses</summary>{tree_html(OUT / 'courses')}</details>")
    sections.append(f"<details class='root'><summary>Docs</summary>{tree_html(OUT / 'docs')}</details>")

    intro = "<p>Browse SDIT content organized by repository structure.</p>"
    html = tmpl_page("SDIT Content Index", intro + "\n" + "\n".join(sections))
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
    /* Collapsible tree (details/summary) */
    details { background: var(--card); border-radius: 8px; padding: 8px 12px; margin: 10px 0; }
    details[open] { padding-bottom: 10px; }
    details > summary { cursor: pointer; list-style: none; font-weight: 600; }
    details > summary::-webkit-details-marker { display: none; }
    details > summary::marker { content: ""; }
    details > summary::before { content: "▸"; display: inline-block; width: 1em; color: var(--muted); transition: transform .15s ease; }
    details[open] > summary::before { content: "▾"; }
    details ul { margin: 6px 0 0 18px; padding-left: 10px; }
    li { margin: 2px 0; }
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
    global OUT, ASSETS
    parser = argparse.ArgumentParser(description="Build static site")
    parser.add_argument("--out", type=str, default=None, help="Output directory (default: dist/site)")
    if argv is None:
        args = parser.parse_args()
    else:
        args = parser.parse_args(argv)
    if args.out:
        out_path = Path(args.out)
        if not out_path.is_absolute():
            OUT = ROOT / out_path
        else:
            OUT = out_path
        ASSETS = OUT / "assets"
    # Reset output dir
    # If building to repo root (OUT == ROOT), avoid deleting the repository.
    # In that case, just ensure directories and overwrite files in place.
    if OUT.resolve() != ROOT.resolve():
        if OUT.exists():
            shutil.rmtree(OUT)
        OUT.mkdir(parents=True, exist_ok=True)
    else:
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

    # Build title map for pretty labels in the tree
    title_map: Dict[Path, str] = {}
    for title, path in (knowledge_entries + docs_entries + courses_entries + programs_entries):
        title_map[path.resolve()] = title
    build_index(title_map)
    print(f"Wrote static site to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
