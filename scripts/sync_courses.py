#!/usr/bin/env python3
"""
sync_courses.py — the schedule and course day lists pull from the course files.

Single source of truth: courses/<DIR>/day-NN.md (front-matter title + first
body line as the dek) and knowledge/catalog.yaml (course names and semester).

What it regenerates, in place, between markers:
  1. courses/<DIR>/index.md   — "The Daily Path" day sections
                                 (between <!-- sdit:days:begin/end -->)
  2. curriculum/schedule.html — one Week section per published week
                                 (between <!-- sdit:weeks:begin/end -->)

Run directly, or let build_site.py call it before rendering. Never edits
anything outside the markers.
"""
from __future__ import annotations

import re
from pathlib import Path

from catalog import DEFAULT_DAYS, planned_days, load_catalog, day_info

ROOT = Path(__file__).resolve().parents[1]
SCHEDULE = ROOT / "curriculum" / "schedule.html"

# Monday-to-Friday rhythm for the shared Foundation semesters:
# books, mathematics, science, computation, the Workshop.
WEEKDAY_ORDER = {
    1: ["HUM", "MATH", "PHYS", "CS", "WKSP"],   # semester 1
    2: ["HUM", "MATH", "PHYS", "CS", "SIG", "WKSP"],
}
WEEKDAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]


def sync_course_days(catalog) -> int:
    """Regenerate 'The Daily Path' sections in every course index.md with markers."""
    planned_by_dir = {c["dir"]: planned_days(c) for c in catalog.get("courses", []) if c.get("dir")}
    changed = 0
    for index_md in sorted((ROOT / "courses").glob("*/index.md")):
        src = index_md.read_text(encoding="utf-8")
        if "<!-- sdit:days:begin -->" not in src:
            continue
        course_dir = index_md.parent
        planned = planned_by_dir.get(course_dir.name, DEFAULT_DAYS)
        blocks = []
        for n in range(1, planned + 1):
            info = day_info(course_dir, n)
            if info:
                title, dek = info
                block = f"### Day {n:02d} — {title}\n\n"
                if dek:
                    block += f"{dek}\n\n"
                block += f"[Begin Day {n:02d} →](day-{n:02d}.html)\n"
            else:
                block = (
                    f"### Day {n:02d} — *coming soon*\n\n"
                    f"Being written — publishes with Week {n}. "
                    f"All five courses advance together, week by week.\n"
                )
            blocks.append(block)
        generated = "<!-- sdit:days:begin -->\n" + "\n".join(blocks) + "<!-- sdit:days:end -->"
        new = re.sub(
            r"<!-- sdit:days:begin -->.*?<!-- sdit:days:end -->",
            generated.replace("\\", "\\\\"),
            src,
            flags=re.S,
        )
        if new != src:
            index_md.write_text(new, encoding="utf-8")
            changed += 1
    return changed


def semester_courses(catalog, semester: int):
    """Catalog courses for a semester, in Mon→Fri rhythm order."""
    rows = [
        c for c in catalog.get("courses", [])
        if c.get("semester") == semester and (ROOT / "courses" / c["dir"]).exists()
    ]
    order = WEEKDAY_ORDER.get(semester, [])

    def key(c):
        prefix = c["dir"].split("-")[0]
        return order.index(prefix) if prefix in order else len(order)

    return sorted(rows, key=key)


def sync_schedule(catalog) -> int:
    """Regenerate the Week sections of curriculum/schedule.html."""
    src = SCHEDULE.read_text(encoding="utf-8")
    if "<!-- sdit:weeks:begin -->" not in src:
        return 0
    courses = semester_courses(catalog, semester=1)
    max_week = max((planned_days(c) for c in courses), default=DEFAULT_DAYS)

    sections = []
    for week in range(1, max_week + 1):
        rows = []
        for i, c in enumerate(courses):
            info = day_info(ROOT / "courses" / c["dir"], week)
            if not info:
                continue
            title, _dek = info
            day_name = WEEKDAY_NAMES[i] if i < len(WEEKDAY_NAMES) else ""
            display = c.get("display") or c.get("name") or c["code"]
            rows.append(
                f'            <a href="/courses/{c["dir"]}/day-{week:02d}.html">'
                f'<span class="l-name">{day_name} · {display}</span>'
                f'<span class="l-meta">{title} →</span></a>'
            )
        if not rows:
            continue
        label_num = "Start Here" if week == 1 else f"Semester 1"
        sections.append(
            f'''    <section class="article" id="week-{week}">
      <div class="frame article-grid">
        <div class="article-label">Week {week}<span class="num">{label_num}</span></div>
        <div class="article-body">
          <nav class="ledger" aria-label="Week {week}" style="margin-top:0.5rem;">
{chr(10).join(rows)}
          </nav>
          <p style="margin-top:1rem;font-size:0.88rem;color:var(--muted);">One schedule serves everyone for the first two years — the Foundation is identical for every student.</p>
        </div>
      </div>
    </section>'''
        )

    generated = "<!-- sdit:weeks:begin -->\n" + "\n\n".join(sections) + "\n    <!-- sdit:weeks:end -->"
    new = re.sub(
        r"<!-- sdit:weeks:begin -->.*?<!-- sdit:weeks:end -->",
        generated.replace("\\", "\\\\"),
        src,
        flags=re.S,
    )
    if new != src:
        SCHEDULE.write_text(new, encoding="utf-8")
        return 1
    return 0


def main() -> int:
    catalog = load_catalog()
    n = sync_course_days(catalog)
    s = sync_schedule(catalog)
    print(f"sync_courses: {n} course page(s) updated, schedule {'updated' if s else 'unchanged'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
