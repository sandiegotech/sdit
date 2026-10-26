#!/usr/bin/env python3
"""
Build a minimal static site to browse repo content offline.

Outputs to: dist/site

Features:
- Converts Markdown under courses/ and programs/ to HTML
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
import re


ROOT = Path(__file__).resolve().parents[1]
# Defaults; may be overridden via --out
OUT = ROOT / "dist" / "site"
ASSETS = OUT / "assets"
MANUAL_ROOT_HTML = {
    Path("courses/index.html"),
}


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


ANSWER_MARKER = "<!-- sdit:answer -->"
ANSWER_SLOT = '<div class="answer-slot" data-sdit-answer="answer"></div>'


def inject_student_work_class(html: str) -> str:
    """Wrap the My Work H2 section and all following content in a .student-work div."""
    marker = '<h2 id="my-work">'
    idx = html.find(marker)
    if idx == -1:
        # Try alternate id pattern
        for alt in ['<h2 id="my-work-', '<h2>My Work</h2>']:
            idx = html.find(alt)
            if idx != -1:
                break
    if idx == -1:
        return html
    return html[:idx] + '<div class="student-work">\n' + html[idx:] + '\n</div>'


def tmpl_page(title: str, body_html: str, breadcrumb: str = "") -> str:
    return f"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title} — SDIT</title>
  <link rel="stylesheet" href="{{ASSET_REL}}assets/site.css" />
  <script src="{{ASSET_REL}}assets/js/site-paths.js" defer></script>
  <script src="{{ASSET_REL}}assets/js/includes.js" defer></script>
</head>
<body>
  <div data-include="/partials/header.html"></div>
  <main>
  {body_html}
  </main>
  <div data-include="/partials/footer.html"></div>
</body>
</html>
"""


def write_file(path: Path, content: str) -> None:
    """Write only when the content differs. An unchanged page keeps its
    modification time, so `aws s3 sync` (which compares size and mtime)
    does not re-upload the whole site after every build."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == ".html":
        import site_polish
        content = site_polish.polish(content)
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return
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


def strip_front_matter(text: str) -> tuple[str, dict]:
    """Remove YAML front matter; returns (body, meta). See scripts/frontmatter.py."""
    import frontmatter

    meta, body = frontmatter.parse(text)
    return body, meta


_PLANNED_BY_DIR = None


def course_planned_days(dir_name: str) -> int:
    """Planned day count for a course dir — catalog-driven, cached."""
    import catalog

    global _PLANNED_BY_DIR
    if _PLANNED_BY_DIR is None:
        _PLANNED_BY_DIR = {
            c["dir"]: catalog.planned_days(c)
            for c in catalog.load_catalog().get("courses", [])
            if c.get("dir")
        }
    return _PLANNED_BY_DIR.get(dir_name, catalog.DEFAULT_DAYS)


def render_markdown_tree(src: Path, dest: Path) -> list[tuple[str, Path]]:
    """Convert all .md files under src into .html under dest, preserving structure.
    Returns: list of (title, output_path) for index building.
    """
    ensure_markdown()
    entries: list[tuple[str, Path]] = []
    for path in sorted(src.rglob("*.md")):
        if path.name == "arc.md":
            # The course arc is the authoring plan for its days (see PLAN.md);
            # it is source, not site, and never renders.
            continue
        md = path.read_text(encoding="utf-8")
        body, meta = strip_front_matter(md)
        html = md_to_html(body)
        # Prefer title from front matter
        title = meta.get("title") if isinstance(meta, dict) else None
        if not title:
            for line in body.splitlines():
                if line.startswith("# "):
                    title = line[2:].strip()
                    break
        if not title:
            title = path.stem.replace("-", " ").title()

        out_path = dest / path.relative_to(src)
        out_path = out_path.with_suffix(".html")

        if should_preserve_root_html(out_path):
            entries.append((title, out_path))
            continue

        # Where the day asks for an answer, the source carries a marker; the
        # page carries a slot that student-work.js turns into the field.
        if ANSWER_MARKER in html:
            import html as _h
            q = str((meta or {}).get("question") or "") if isinstance(meta, dict) else ""
            slot = ANSWER_SLOT.replace('data-sdit-answer="answer"',
                                       f'data-sdit-answer="answer" data-question="{_h.escape(q, quote=True)}"')
            html = html.replace(ANSWER_MARKER, slot)

        # Course pages: the made-thing record sits right under "The Made Thing".
        idx_match = re.match(r"^courses/([^/]+)/index$", path.relative_to(ROOT).with_suffix("").as_posix())
        if idx_match and 'id="the-made-thing"' in html:
            d = idx_match.group(1)
            slot = (f'<div class="made-slot" data-sdit-made data-lesson="/courses/{d}/made"></div>\n')
            at = html.index('id="the-made-thing"')
            nxt = html.find("<h2", at)
            html = html[:nxt] + slot + html[nxt:] if nxt != -1 else html + slot

        # Course day pages: a canonical lesson id, and the end-of-day chrome that
        # pulls the learner forward: the next day in this course, and the next
        # day on the Path (which crosses courses in the weekly rhythm).
        day_match = re.match(r"^courses/([^/]+)/day-(\d+)$", path.relative_to(ROOT).with_suffix("").as_posix())
        canonical = None
        if day_match:
            course_dir, day_num = day_match.group(1), int(day_match.group(2))
            canonical = f"/courses/{course_dir}/day-{day_num:02d}"
            html += lesson_footer_html(course_dir, day_num, meta if isinstance(meta, dict) else {})

        # Prepare template and asset path
        page = tmpl_page(title, html)
        if canonical:
            page = page.replace("</head>", f'  <meta name="sdit-lesson" content="{canonical}" />\n</head>', 1)
        # Inject the correct asset relative prefix
        rel = asset_rel(out_path)
        page = page.replace("{ASSET_REL}", rel)
        # Mark generated files so contributors know not to edit HTML directly
        source_md = path.name
        page = page.replace("<!doctype html>", f"<!doctype html>\n<!-- Generated from {source_md} — edit the .md file, not this file -->", 1)
        write_file(out_path, page)
        entries.append((title, out_path))
    return entries


def _card(eyebrow: str, title: str, sub: str, href: str | None, cta: str) -> str:
    import html as _html
    inner = (
        f'<span class="lesson-tomorrow-eyebrow">{_html.escape(eyebrow)}</span>'
        f'<strong>{_html.escape(title)}</strong>'
        + (f'<span class="lesson-tomorrow-sub">{_html.escape(sub)}</span>' if sub else "")
        + f'<span class="lesson-tomorrow-cta">{_html.escape(cta)}</span>'
    )
    if href:
        return f'<a class="lesson-tomorrow-card" href="{_html.escape(href)}">{inner}</a>'
    return f'<div class="lesson-tomorrow-card is-upcoming">{inner}</div>'


def _step_card(eyebrow: str, step) -> str:
    import publishing
    if step.kind == "gate":
        return _card(eyebrow, step.title, "Your answers again, and what changed.",
                     step.href if step.published else None,
                     "Continue →" if step.published else "Opens at the end of the semester")
    c = step.course or {}
    sub = f"{step.label} · {c.get('code', '')} · {c.get('display') or c.get('name', '')}".strip(" ·")
    if step.published:
        return _card(eyebrow, step.title, sub, step.href, "Continue the practice →")
    when = f"Publishes {publishing.long_date(step.publishes)}" if step.publishes else "Being written"
    return _card(eyebrow, step.title, sub, None, when)


def lesson_footer_html(course_dir: str, n: int, meta: dict) -> str:
    """The end-of-day chrome: where you are on the Path, and what comes next."""
    import html as _html
    import degree_path

    here = degree_path.day_step(course_dir, n)
    planned = course_planned_days(course_dir)
    where = f"Day {n} of {planned} in this course"
    if here:
        where += f" · Semester {here.semester}, Week {here.week}"
    cards = []
    if n < planned:
        nxt = degree_path.day_step(course_dir, n + 1)
        if nxt:
            cards.append(_step_card("Next in this course", nxt))
    else:
        cards.append(_card("This course is complete", "Back to the course",
                           "The made thing is what remains.", "index.html", "Course overview →"))
    on_path = degree_path.next_on_path(course_dir, n)
    if on_path and on_path.key != (course_dir, n + 1):
        cards.append(_step_card("Next on the Path", on_path))
    parts = ['<aside class="lesson-journey">',
             f'<p class="lesson-journey-meta">{_html.escape(where)}</p>',
             '<div class="lesson-next">', *cards, '</div>',
             '<p class="lesson-selfpace">Self-paced: the next day is there whenever you come back. '
             '<a href="/curriculum/day-by-day.html">The whole Path →</a></p>',
             '</aside>']
    return "\n".join(parts)


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


def should_preserve_root_html(out_path: Path) -> bool:
    if OUT.resolve() != ROOT.resolve() or not out_path.exists():
        return False
    rel_out = Path(out_path.resolve().relative_to(ROOT.resolve()).as_posix())
    return rel_out in MANUAL_ROOT_HTML


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

    intro = "<p>Browse SDIT content organized by repository structure.</p>"
    html = tmpl_page("SDIT Content Index", intro + "\n" + "\n".join(sections))
    html = html.replace("{ASSET_REL}", asset_rel(OUT / "index.html"))
    write_file(OUT / "index.html", html)


def write_assets():
    """Prepare the output's static assets.

    Single source of truth for styling is assets/site.css. When building in
    place (OUT == ROOT) the source assets already live in assets/, so nothing
    needs copying. When building to a separate dir, copy the static source
    (CSS, JS, partials, brand) into the output so it is a complete site.
    """
    ASSETS.mkdir(parents=True, exist_ok=True)
    # Disable Jekyll processing on GitHub Pages so files are served as-is
    write_file(OUT / ".nojekyll", "")

    # When building to a separate output dir, copy JS files and partials so the
    # site header and footer work when serving the output locally.
    if OUT.resolve() != ROOT.resolve():
        js_src = ROOT / "assets" / "js"
        js_dest = ASSETS / "js"
        if js_src.exists():
            js_dest.mkdir(parents=True, exist_ok=True)
            for f in js_src.iterdir():
                if f.is_file():
                    shutil.copy2(f, js_dest / f.name)
        partials_src = ROOT / "partials"
        partials_dest = OUT / "partials"
        if partials_src.exists():
            partials_dest.mkdir(parents=True, exist_ok=True)
            for f in partials_src.iterdir():
                if f.is_file():
                    shutil.copy2(f, partials_dest / f.name)
        site_css = ROOT / "assets" / "site.css"
        if site_css.exists():
            shutil.copy2(site_css, ASSETS / "site.css")


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

    # The schedule and course day lists pull from the course day files.
    import sync_courses
    sync_courses.main()

    # Browser-fetchable course index for the signed-in course-mode header.
    import build_catalog
    build_catalog.main(ASSETS)

    # Day 0 (the Commitment and three questions) and the eight gates.
    import reflections
    reflections.write_all(write_file, OUT)

    # The pages a reviewer reads: map, breadth, requirements, policies,
    # assessment, rubrics.
    import review_grade
    review_grade.write_pages(write_file, OUT)

    # The Portfolio (and /notebook/, which points into it).
    import portfolio
    portfolio.write_all(write_file, OUT)
    # The sample portfolio of a fictional learner, at /portfolio/demo/.
    import demo_portfolio
    demo_portfolio.write_all(write_file, OUT)

    # The Path: every day of the degree, in order, with publish dates.
    import degree_path
    page = degree_path.render_path_page()
    write_file(OUT / "curriculum" / "day-by-day.html", page)

    # knowledge/ is the build's data, not pages: its YAML carries internal notes
    # and is no longer rendered or published (PLAN.md 12.3, item 8).
    knowledge_entries: list = []
    institute_entries = render_markdown_tree(ROOT / "institute", OUT / "institute")
    courses_entries = render_markdown_tree(ROOT / "courses", OUT / "courses")

    # Add simple section index pages where no manual one is preserved.
    for (title, out_path), section_name in (
        (("Courses", OUT / "courses" / "index.html"), "courses"),
    ):
        if should_preserve_root_html(out_path):
            continue
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
    for title, path in (knowledge_entries + institute_entries + courses_entries):
        title_map[path.resolve()] = title
    # The last pass: what every page must carry, robots.txt, the sitemap.
    import site_polish
    site_polish.run(write_file, OUT)

    # Only generate an index page if one does not already exist. This allows
    # callers to run the build into the repository root ("--out .") without
    # clobbering a manually maintained index.html that may contain markers used
    index_path = OUT / "index.html"
    if not index_path.exists():
        build_index(title_map)
    # When an existing index is present we assume it will be updated separately
    # and simply leave it untouched.
    print(f"Wrote static site to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
