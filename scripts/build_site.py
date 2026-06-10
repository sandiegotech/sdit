#!/usr/bin/env python3
"""
Build a minimal static site to browse repo content offline.

Outputs to: dist/site

Features:
- Converts Markdown under courses/ and programs/ to HTML
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
import re


ROOT = Path(__file__).resolve().parents[1]
# Defaults; may be overridden via --out
OUT = ROOT / "dist" / "site"
ASSETS = OUT / "assets"
MANUAL_ROOT_HTML = {
    Path("courses/index.html"),
    Path("programs/index.html"),
    Path("programs/Bachelor-Liberal-Arts/index.html"),
    Path("programs/Bachelor-Liberal-Arts/vol-01-foundations/schedule/index.html"),
    Path("programs/Bachelor-Liberal-Arts/vol-01-foundations/before-you-begin.html"),
    Path("guides/using-ai.html"),
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


def strip_front_matter(text: str) -> tuple[str, dict]:
    """Remove simple YAML front matter delimited by '---' lines."""
    if not text.startswith("---\n"):
        return text, {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return text, {}
    fm = text[4:end]
    body = text[end + 5 :]
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(fm) or {}
        if isinstance(data, dict):
            return body.lstrip(), data
    except Exception:
        pass

    meta: dict[str, str] = {}
    for line in fm.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, val = line.split(":", 1)
        meta[key.strip()] = val.strip().strip('"')
    return body.lstrip(), meta


def render_markdown_tree(src: Path, dest: Path) -> list[tuple[str, Path]]:
    """Convert all .md files under src into .html under dest, preserving structure.
    Returns: list of (title, output_path) for index building.
    """
    ensure_markdown()
    entries: list[tuple[str, Path]] = []
    for path in sorted(src.rglob("*.md")):
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

        # Wrap student work section if present
        is_lesson = re.search(r"(section-\d+|day-\d+)\.html$", str(out_path))
        if is_lesson:
            html = inject_student_work_class(html)

        # Course day pages: canonical lesson id + a "next in this course" card,
        # so responses unify across routes and every lesson ends with a pull forward.
        day_match = re.match(r"^courses/([^/]+)/day-(\d+)$", path.relative_to(ROOT).with_suffix("").as_posix())
        canonical = None
        if day_match:
            course_dir, day_num = day_match.group(1), int(day_match.group(2))
            canonical = f"/courses/{course_dir}/day-{day_num:02d}"
            next_md = ROOT / "courses" / course_dir / f"day-{day_num + 1:02d}.md"
            if next_md.exists():
                _, next_meta = strip_front_matter(next_md.read_text(encoding="utf-8"))
                next_title = (next_meta.get("title") or f"Day {day_num + 1:02d}") if isinstance(next_meta, dict) else f"Day {day_num + 1:02d}"
                html += journey_footer_html(
                    journey=f"Day {day_num} of 15 in this course",
                    eyebrow="Next in this course",
                    card_title=re.sub(r"^Day \d+\s*[—–-]\s*", "", str(next_title)),
                    card_sub=str(meta.get("course") or "") if isinstance(meta, dict) else "",
                    href=f"day-{day_num + 1:02d}.html",
                )

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


def journey_footer_html(journey: str, eyebrow: str, card_title: str, card_sub: str,
                        href: str, week_map: str = "", note: str = "") -> str:
    """The end-of-lesson journey chrome: where you are, and the pull to tomorrow."""
    import html as _html
    parts = ['<aside class="lesson-journey">']
    parts.append(f'<p class="lesson-journey-meta">{_html.escape(journey)}</p>')
    if week_map:
        parts.append(week_map)
    parts.append(
        f'<a class="lesson-tomorrow-card" href="{_html.escape(href)}">'
        f'<span class="lesson-tomorrow-eyebrow">{_html.escape(eyebrow)}</span>'
        f'<strong>{_html.escape(card_title)}</strong>'
        + (f'<span class="lesson-tomorrow-sub">{_html.escape(card_sub)}</span>' if card_sub else "")
        + '<span class="lesson-tomorrow-cta">Continue the practice →</span>'
        f'</a>'
    )
    parts.append(f'<p class="lesson-selfpace">{_html.escape(note or "Self-paced — tomorrow means whenever you come back.")}</p>')
    parts.append("</aside>")
    return "\n".join(parts)


def render_schedule_sections() -> list[tuple[str, Path]]:
    """Generate the daily-practice pages from the course library (single source of truth).

    programs/Bachelor-Liberal-Arts/schedule.yaml interleaves the five foundation
    courses into weeks: chapter-WW/section-DD is one course session. Each page is
    built from the canonical courses/<course>/day-NN.md, carries a canonical-lesson
    meta tag (responses unify across the course and schedule routes), and ends with
    the journey footer: day-of-volume context, a this-week map, and a Tomorrow card.
    """
    import html as _html
    import yaml

    ensure_markdown()
    entries: list[tuple[str, Path]] = []
    sched_path = ROOT / "programs" / "Bachelor-Liberal-Arts" / "schedule.yaml"
    if not sched_path.exists():
        return entries
    sched = yaml.safe_load(sched_path.read_text(encoding="utf-8")) or {}

    for vol in sched.get("volumes") or []:
        weeks = vol.get("weeks") or []
        if not weeks:
            continue
        vol_id = vol.get("id")
        vol_label = f"{vol.get('label', '')}: {vol.get('title', '')}".strip(": ")
        base = OUT / "programs" / "Bachelor-Liberal-Arts" / vol_id / "schedule"

        # Flatten to an ordered list of sessions with source metadata.
        flat = []  # (week_no, week_title, slot, course, day)
        for w in weeks:
            for slot, sess in enumerate(w.get("sessions") or [], start=1):
                flat.append((w["week"], w.get("title", ""), slot, sess["course"], int(sess["day"])))
        total = len(flat)

        # Pre-read titles/course labels from the canonical md front matter.
        info: dict[tuple[str, int], dict] = {}
        for _, _, _, course, day in flat:
            src = ROOT / "courses" / course / f"day-{day:02d}.md"
            if not src.exists():
                continue
            body, meta = strip_front_matter(src.read_text(encoding="utf-8"))
            raw_title = str((meta or {}).get("title") or f"Day {day:02d}")
            info[(course, day)] = {
                "body": body,
                "title": re.sub(r"^Day \d+\s*[—–-]\s*", "", raw_title),
                "course_label": str((meta or {}).get("course") or course),
            }

        for n, (week_no, week_title, slot, course, day) in enumerate(flat, start=1):
            rec = info.get((course, day))
            if rec is None:
                print(f"  schedule: missing courses/{course}/day-{day:02d}.md — section skipped")
                continue

            # Program-day framing: the journey strip carries day-of-volume context,
            # so strip the course-relative "Day NN —" prefix from the lesson heading.
            body = re.sub(r"^# Day \d+\s*[—–-]\s*", "# ", rec["body"], count=1, flags=re.M)
            html = inject_student_work_class(md_to_html(body))

            # This-week map: five pills, current one marked.
            pills = []
            for w2, _, s2, c2, d2 in flat:
                if w2 != week_no:
                    continue
                t2 = info.get((c2, d2), {}).get("title", "")
                if s2 == slot:
                    pills.append(f'<span class="lesson-week-pill is-current" title="{_html.escape(t2)}">Day {s2}</span>')
                else:
                    pills.append(f'<a class="lesson-week-pill" href="../chapter-{week_no:02d}/section-{s2:02d}.html" title="{_html.escape(t2)}">Day {s2}</a>')
            week_map = (
                f'<p class="lesson-week-label">Week {week_no} — {_html.escape(week_title)}</p>'
                f'<div class="lesson-week-map">{"".join(pills)}</div>'
            )

            journey = f"Day {n} of {total} · Week {week_no} of {len(weeks)} · {vol_label}"
            if n < total:
                nw, nwt, ns, nc, nd = flat[n]
                nxt = info.get((nc, nd), {})
                eyebrow = f"Tomorrow · Week {nw} begins" if nw != week_no else f"Tomorrow · Day {n + 1} of {total}"
                footer = journey_footer_html(
                    journey=journey, eyebrow=eyebrow,
                    card_title=nxt.get("title", "The next session"),
                    card_sub=nxt.get("course_label", nc),
                    href=f"../chapter-{nw:02d}/section-{ns:02d}.html",
                    week_map=week_map,
                )
            else:
                footer = journey_footer_html(
                    journey=journey, eyebrow="You finished Volume 1",
                    card_title="Foundations, complete. Volume 2: Ethics and Reasoning is next.",
                    card_sub="Four years. Eight volumes. This was the first.",
                    href="/programs/Bachelor-Liberal-Arts/index.html",
                    week_map=week_map,
                    note="Go back and reread your Day 1 manifesto before you move on.",
                )
            html += footer

            out_path = base / f"chapter-{week_no:02d}" / f"section-{slot:02d}.html"
            page = tmpl_page(rec["title"], html)
            page = page.replace("</head>", f'  <meta name="sdit-lesson" content="/courses/{course}/day-{day:02d}" />\n</head>', 1)
            page = page.replace("{ASSET_REL}", asset_rel(out_path))
            page = page.replace(
                "<!doctype html>",
                f"<!doctype html>\n<!-- Generated from courses/{course}/day-{day:02d}.md via schedule.yaml — edit those, not this file -->",
                1,
            )
            write_file(out_path, page)
            entries.append((rec["title"], out_path))
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

    knowledge_entries = render_knowledge(ROOT / "knowledge", OUT / "knowledge")
    institute_entries = render_markdown_tree(ROOT / "institute", OUT / "institute")
    courses_entries = render_markdown_tree(ROOT / "courses", OUT / "courses")
    programs_entries = render_markdown_tree(ROOT / "programs", OUT / "programs")
    # After the trees: section pages are derived from courses/ + schedule.yaml and
    # must win over any stale committed copies.
    schedule_entries = render_schedule_sections()

    # Add simple section index pages where no manual one is preserved.
    for (title, out_path), section_name in (
        (("Courses", OUT / "courses" / "index.html"), "courses"),
        (("Programs", OUT / "programs" / "index.html"), "programs"),
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
    for title, path in (knowledge_entries + institute_entries + courses_entries + programs_entries + schedule_entries):
        title_map[path.resolve()] = title
    # Only generate an index page if one does not already exist. This allows
    # callers to run the build into the repository root ("--out .") without
    # clobbering a manually maintained index.html that may contain markers used
    # by other scripts (e.g. generate_programs_tree.py).
    index_path = OUT / "index.html"
    if not index_path.exists():
        build_index(title_map)
    # When an existing index is present we assume it will be updated separately
    # and simply leave it untouched.
    print(f"Wrote static site to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
