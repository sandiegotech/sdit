#!/usr/bin/env python3
"""
sync_courses.py — the schedule and course day lists pull from the course files.

Single source of truth: courses/<DIR>/day-NN.md (front-matter title + first
body line as the dek) and knowledge/catalog.yaml (course names, semesters,
planned lengths, statuses).

What it regenerates, in place, between markers:
  1. courses/<DIR>/index.md   — "The Daily Path" day sections
                                 (between <!-- sdit:days:begin/end -->)
                                 and the `status:` line of the front matter,
                                 which always mirrors the registry.
  2. curriculum/schedule.html — every semester: its weekday rhythm, then one
                                 Week section per published week
                                 (between <!-- sdit:weeks:begin/end -->)

Run directly, or let build_site.py call it before rendering. Never edits
anything outside the markers (or the one front-matter line).
"""
from __future__ import annotations

import re
from pathlib import Path

from catalog import DEFAULT_DAYS, planned_days, load_catalog, day_info

ROOT = Path(__file__).resolve().parents[1]
SCHEDULE = ROOT / "curriculum" / "schedule.html"

# The weekday rhythm of every semester. Monday is always the books and Friday
# is always the Workshop; the middle of the week changes with the semester.
# A prefix names the course that owns that weekday. STUDIO marks the days given
# to depth studios (a learner takes the ones their concentration prescribes, so
# studios are listed without a fixed weekday). A "~" entry is a requirement
# that is not a catalog course and links to the four-year map instead.
STUDIO = "*studio*"
WEEKDAY_ORDER = {
    1: ["HUM", "MATH", "PHYS", "CS", "WKSP"],
    2: ["HUM", "MATH", "PHYS", "CS", "WKSP", "SIG"],
    3: ["HUM", "MATH", "RHET", "CS", "WKSP"],
    4: ["HUM", "MATH", "RHET", "CS", "WKSP", "SIG"],
    5: ["HUM", STUDIO, STUDIO, STUDIO, "WKSP", "SIG"],
    6: ["HUM", "FLD", STUDIO, STUDIO, "WKSP"],
    7: ["HUM", "CS", STUDIO, "CAP", "WKSP"],
    8: ["HUM", "~crossing", "~open", "CAP", "WKSP", "SIG"],
}
WEEKDAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
REQUIREMENT_ROWS = {
    "~crossing": ("The Crossing", "one depth studio from outside your concentration — required"),
    "~open": ("Open Studio", "one course from the rotating practitioner-taught slate"),
}
SEMESTER_LABEL = {
    1: "Year 1 · Fall", 2: "Year 1 · Spring",
    3: "Year 2 · Fall", 4: "Year 2 · Spring",
    5: "Year 3 · Fall", 6: "Year 3 · Spring",
    7: "Year 4 · Fall", 8: "Year 4 · Spring",
}
SEMESTER_MILESTONE = {
    2: "Year 1 ends with your work in a public exhibition.",
    4: "Year 2 ends with the Declaration — you choose Media, Design, or Engineering from two years of made work.",
    6: "The Field Term: a full term embedded in a working organization.",
    8: "Capstone defense, the teaching requirement, graduation.",
}
FOUNDATION_NOTE = "One schedule serves everyone for the first two years — the Foundation is identical for every student."
FOCUS_NOTE = "The spine is shared. The studios are the four your concentration prescribes; the Crossing is one from outside it."


def _course_prefix(c: dict) -> str:
    return c["dir"].split("-")[0]


def _set_front_matter_status(src: str, status: str) -> str:
    """Mirror the registry's status into an index.md front-matter block."""
    if not src.startswith("---\n"):
        return src
    end = src.find("\n---\n", 4)
    if end == -1:
        return src
    fm = src[4:end]
    if not re.search(r"^status:\s*.*$", fm, flags=re.M):
        return src
    new_fm = re.sub(r"^status:\s*.*$", f"status: {status}", fm, count=1, flags=re.M)
    return "---\n" + new_fm + src[end:]


def sync_course_days(catalog) -> int:
    """Regenerate 'The Daily Path' sections in every course index.md with markers,
    and keep each index's front-matter status equal to the registry's."""
    by_dir = {c["dir"]: c for c in catalog.get("courses", []) if c.get("dir")}
    changed = 0
    for index_md in sorted((ROOT / "courses").glob("*/index.md")):
        src = index_md.read_text(encoding="utf-8")
        course_dir = index_md.parent
        course = by_dir.get(course_dir.name)
        new = src
        if course and course.get("status"):
            new = _set_front_matter_status(new, str(course["status"]))
        if "<!-- sdit:days:begin -->" in new:
            planned = planned_days(course) if course else DEFAULT_DAYS
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
                        f"Every course in the semester advances together, week by week.\n"
                    )
                blocks.append(block)
            generated = "<!-- sdit:days:begin -->\n" + "\n".join(blocks) + "<!-- sdit:days:end -->"
            new = re.sub(
                r"<!-- sdit:days:begin -->.*?<!-- sdit:days:end -->",
                generated.replace("\\", "\\\\"),
                new,
                flags=re.S,
            )
        if new != src:
            index_md.write_text(new, encoding="utf-8")
            changed += 1
    return changed


def semester_rows(catalog, semester: int) -> list[tuple[str, object]]:
    """The semester's week as (day label, course-or-requirement) rows, in rhythm order.

    Spine courses carry their weekday. Depth studios carry "Studio" and sit on
    the studio days. A requirement that is not a course carries its weekday and
    the REQUIREMENT_ROWS key. Anything in the catalog for this semester that the
    rhythm does not name is appended unlabelled rather than dropped.
    """
    courses = [
        c for c in catalog.get("courses", [])
        if c.get("semester") == semester and (ROOT / "courses" / c["dir"]).exists()
    ]
    order = WEEKDAY_ORDER.get(semester, [])
    studios = sorted((c for c in courses if c.get("thread") == "depth"), key=lambda c: c["dir"])
    rows: list[tuple[str, object]] = []
    used: set[str] = set()
    studios_placed = False
    for i, slot in enumerate(order):
        day = WEEKDAY_NAMES[i] if i < len(WEEKDAY_NAMES) else ""
        if slot == STUDIO:
            if not studios_placed:
                for c in studios:
                    rows.append(("Studio", c))
                    used.add(c["dir"])
                studios_placed = True
            continue
        if slot.startswith("~"):
            rows.append((day, slot))
            continue
        for c in courses:
            if c["dir"] in used or c.get("thread") == "depth":
                continue
            if _course_prefix(c) == slot:
                rows.append((day, c))
                used.add(c["dir"])
                break
    for c in courses:
        if c["dir"] not in used:
            rows.append(("", c))
    return rows


def semester_courses(catalog, semester: int):
    """Catalog courses for a semester, in rhythm order (requirements omitted)."""
    return [c for _label, c in semester_rows(catalog, semester) if isinstance(c, dict)]


def _display(c: dict) -> str:
    return c.get("display") or c.get("name") or c["code"]


def _rhythm_ledger(rows) -> str:
    out = []
    for label, item in rows:
        if isinstance(item, dict):
            lead = f"{label} · " if label else ""
            units = item.get("units")
            units_s = f"{units} unit{'s' if units != 1 else ''}" if isinstance(units, int) else ""
            meta = " · ".join(x for x in (item.get("code", ""), units_s) if x)
            out.append(
                f'            <a href="/courses/{item["dir"]}/index.html">'
                f'<span class="l-name">{lead}{_display(item)}</span>'
                f'<span class="l-meta">{meta} →</span></a>'
            )
        else:
            name, meta = REQUIREMENT_ROWS[item]
            out.append(
                f'            <a href="/curriculum/four-years.html">'
                f'<span class="l-name">{label} · {name}</span>'
                f'<span class="l-meta">{meta} →</span></a>'
            )
    return "\n".join(out)


def _week_ledger(rows, week: int) -> str:
    out = []
    for label, item in rows:
        if not isinstance(item, dict):
            continue
        info = day_info(ROOT / "courses" / item["dir"], week)
        if not info:
            continue
        title, _dek = info
        lead = f"{label} · " if label else ""
        out.append(
            f'            <a href="/courses/{item["dir"]}/day-{week:02d}.html">'
            f'<span class="l-name">{lead}{_display(item)}</span>'
            f'<span class="l-meta">{title} →</span></a>'
        )
    return "\n".join(out)


def _section(section_id: str, label: str, num: str, body: str) -> str:
    return f'''    <section class="article" id="{section_id}">
      <div class="frame article-grid">
        <div class="article-label">{label}<span class="num">{num}</span></div>
        <div class="article-body">
{body}
        </div>
      </div>
    </section>'''


def sync_schedule(catalog) -> int:
    """Regenerate the semester and Week sections of curriculum/schedule.html."""
    src = SCHEDULE.read_text(encoding="utf-8")
    if "<!-- sdit:weeks:begin -->" not in src:
        return 0

    sections = []
    for semester in range(1, 9):
        rows = semester_rows(catalog, semester)
        if not rows:
            continue
        courses = [c for _l, c in rows if isinstance(c, dict)]
        note = FOUNDATION_NOTE if semester <= 4 else FOCUS_NOTE
        milestone = SEMESTER_MILESTONE.get(semester)
        milestone_html = (
            f'\n          <p style="margin-top:0.6rem;font-size:0.88rem;color:var(--muted);">→ {milestone}</p>'
            if milestone else ""
        )
        sections.append(_section(
            f"semester-{semester}",
            f"Semester {semester}",
            SEMESTER_LABEL.get(semester, ""),
            f'          <nav class="ledger" aria-label="Semester {semester} week" style="margin-top:0.5rem;">\n'
            f"{_rhythm_ledger(rows)}\n"
            f"          </nav>\n"
            f'          <p style="margin-top:1rem;font-size:0.88rem;color:var(--muted);">{note}</p>'
            f"{milestone_html}",
        ))

        max_week = max((planned_days(c) for c in courses), default=DEFAULT_DAYS)
        published_weeks = 0
        for week in range(1, max_week + 1):
            ledger = _week_ledger(rows, week)
            if not ledger:
                continue
            published_weeks += 1
            num = "Start Here" if (semester == 1 and week == 1) else f"Semester {semester}"
            sections.append(_section(
                f"s{semester}-week-{week}",
                f"Week {week}",
                num,
                f'          <nav class="ledger" aria-label="Semester {semester}, Week {week}" style="margin-top:0.5rem;">\n'
                f"{ledger}\n"
                f"          </nav>",
            ))
        if not published_weeks:
            sections.append(
                f'    <p class="frame" style="font-size:0.88rem;color:var(--muted);margin:-0.5rem auto 2rem;">'
                f"Semester {semester}'s days publish week by week once the semester before it is complete.</p>"
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
