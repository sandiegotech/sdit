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
  2. curriculum/schedule.html — every semester: its load and weekday rhythm (one
                                 Week section per published week
                                 (between <!-- sdit:weeks:begin/end -->)

Run directly, or let build_site.py call it before rendering. Never edits
anything outside the markers (or the one front-matter line).
"""
from __future__ import annotations

import re
from pathlib import Path

import arcs
import publishing
import review_grade
from catalog import DEFAULT_DAYS, planned_days, load_catalog, day_info

ROOT = Path(__file__).resolve().parents[1]
SCHEDULE = ROOT / "curriculum" / "schedule.html"

# The weekday rhythm of every semester. Monday is always the books and Friday
# is always the Workshop; the middle of the week changes with the semester.
# A prefix names the course that owns that weekday. STUDIO marks the days given
# to depth studios (a learner takes the ones their concentration prescribes, so
# studios are listed without a fixed weekday). A "~" entry is a requirement
# that is not a catalog course and links to the requirements instead.
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
FOUNDATION_NOTE = "The same courses for everyone: the first two years are the Foundation, and nothing in them is elective."
FOCUS_NOTE = "The spine (the books, the Workshop, the Field Term, the capstone) is shared. The studios listed are the ones offered that semester; your concentration prescribes four across Years 3 and 4, and the Crossing adds one from outside it."


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
                    arc = arcs.load_arc(course_dir)
                    arc_day = arc.day(n) if arc else None
                    when = publishing.week_date(course["semester"], n) if course and course.get("semester") else None
                    when_line = f"Publishes {publishing.long_date(when)}." if when else "Being written."
                    if arc_day:
                        block = f"### Day {n:02d} — {arc_day.title}\n\n{when_line}\n"
                    else:
                        block = f"### Day {n:02d} — *coming soon*\n\n{when_line}\n"
                blocks.append(block)
            lead = review_grade.DAYS_LEAD + "\n\n" if (course and _syllabus(new)) else ""
            generated = "<!-- sdit:days:begin -->\n" + lead + "\n".join(blocks) + "<!-- sdit:days:end -->"
            new = re.sub(
                r"<!-- sdit:days:begin -->.*?<!-- sdit:days:end -->",
                generated.replace("\\", "\\\\"),
                new,
                flags=re.S,
            )
        if course:
            new = review_grade.sync_course_sections(new, course, _syllabus(new))
        if new != src:
            index_md.write_text(new, encoding="utf-8")
            changed += 1
    return changed


def _syllabus(text: str) -> dict | None:
    import frontmatter
    meta, _ = frontmatter.parse(text)
    block = (meta or {}).get("syllabus") if isinstance(meta, dict) else None
    return block if isinstance(block, dict) else None


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
        # The load, honestly: one unit is three hours a week for fifteen weeks.
        spine = [c for c in courses if c.get("thread") != "depth"]
        spine_units = sum(int(c.get("units") or 0) for c in spine)
        # Years 3 and 4: the studios listed are the ones offered; a learner takes
        # four across the two years (2, 1, 1) and, in Semester 8, the Crossing
        # and the Open Studio. With the spine that is 13 + 12 + 14 + 15 = 54
        # units, which with the Foundation's 66 makes the degree's 120.
        STUDIO_LOAD = {5: (8, "two studios"), 6: (4, "one studio"), 7: (4, "one studio"),
                       8: (8, "the Crossing and the Open Studio")}
        if semester <= 4:
            load = f"{spine_units} units · about {spine_units * 3} hours of work a week"
        else:
            su, what = STUDIO_LOAD[semester]
            load = f"{spine_units} units on the spine + {su} in {what} · about {(spine_units + su) * 3} hours of work a week"
        first = publishing.week_date(semester, 1)
        if first:
            dates = f"from {publishing.long_date(first)}"
        else:
            second = publishing.week_date(semester, 2)
            dates = f"Week 1 is live · Weeks 2–15 from {publishing.long_date(second)}" if second else ""
        sections.append(_section(
            f"semester-{semester}",
            f"Semester {semester}",
            SEMESTER_LABEL.get(semester, ""),
            f'          <p class="sched-load">{load}{" · " + dates if dates else ""}</p>\n'
            f'          <nav class="ledger" aria-label="Semester {semester} week" style="margin-top:0.5rem;">\n'
            f"{_rhythm_ledger(rows)}\n"
            f"          </nav>\n"
            f'          <p style="margin-top:1rem;font-size:0.88rem;color:var(--muted);">{note}</p>'
            f"{milestone_html}"
            f'\n          <p style="margin-top:0.6rem;font-size:0.88rem;"><a href="/curriculum/day-by-day.html#semester-{semester}">Every day of Semester {semester}, dated, on the Path →</a></p>',
        ))

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


CATALOG_PAGE = ROOT / "courses" / "index.html"
CATALOG_MARKERS = ("<!-- sdit:catalog:begin -->", "<!-- sdit:catalog:end -->")


def _esc(s) -> str:
    import html
    return html.escape(str(s), quote=False)


def _status_tag(c: dict) -> str:
    from catalog import published_days
    n = len(published_days(ROOT / "courses" / c["dir"]))
    planned = planned_days(c)
    if n and n >= planned:
        return '<span class="tag tag--live">live</span>'
    if n:
        return f'<span class="tag tag--live">{"day 1" if n == 1 else f"{n} days"} live</span>'
    first = publishing.week_date(c["semester"], 1) if c.get("semester") else None
    when = f"from {publishing.short_date(first)} {first.year}" if first else "coming soon"
    return f'<span class="tag tag--planned">{when}</span>'


def sync_catalog_page(catalog) -> int:
    """The course list on courses/index.html, by thread, from the registry."""
    src = CATALOG_PAGE.read_text(encoding="utf-8")
    if CATALOG_MARKERS[0] not in src:
        return 0
    courses = catalog.get("courses", [])
    parts = []
    for t in catalog.get("threads", []):
        rows = [c for c in courses if c.get("thread") == t["id"]]
        if not rows:
            continue
        depth = t["id"] == "depth"
        items = []
        for c in rows:
            name = c.get("display") or c.get("name", "")
            formal = c.get("name", "") if c.get("display") and c.get("display") != c.get("name") else ""
            if c["dir"].startswith("WKSP-") or c["dir"].startswith("CAP-"):
                name = f"{name} · Semester {c.get('semester')}"
            frame = " · ".join(x.title() for x in c.get("concentrations", [])) if depth else ""
            why = " ".join(str(c.get("description", "")).split())
            ends = " ".join(str(c.get("artifact", "")).split())
            units = c.get("units")
            meta = " · ".join(x for x in (
                f'{units} unit{"s" if units != 1 else ""}' if isinstance(units, int) else "",
                f'Semester {c.get("semester")}' if c.get("semester") else "",
                frame) if x)
            items.append(
                f'            <li class="cat-course" id="{_esc(c["dir"])}">\n'
                f'              <a class="cat-head" href="/courses/{c["dir"]}/index.html"><span class="cat-code">{_esc(c["code"])}</span>'
                f'<strong>{_esc(name)}</strong>{f"<small>{_esc(formal)}</small>" if formal else ""}</a>\n'
                f'              <p class="cat-why">{_esc(why)}</p>\n'
                + (f'              <p class="cat-ends"><span>You make</span> {_esc(ends)}</p>\n' if ends else "")
                + f'              <p class="cat-meta">{_esc(meta)} · {_status_tag(c)}</p>\n'
                f'            </li>')
        parts.append(
            f'          <h3 id="{_esc(t["id"])}">{_esc(t["name"])}</h3>\n'
            f'          <p class="cat-thread-note">{_esc(t.get("note", ""))}</p>\n'
            f'          <ul class="cat-list">\n'
            + "\n".join(items) +
            '\n          </ul>\n')
    body = "\n".join(parts)
    new = re.sub(re.escape(CATALOG_MARKERS[0]) + r".*?" + re.escape(CATALOG_MARKERS[1]),
                 lambda _m: f"{CATALOG_MARKERS[0]}\n{body}          {CATALOG_MARKERS[1]}", src, flags=re.S)
    if new != src:
        CATALOG_PAGE.write_text(new, encoding="utf-8")
        return 1
    return 0


def main() -> int:
    catalog = load_catalog()
    n = sync_course_days(catalog)
    s = sync_schedule(catalog)
    sync_catalog_page(catalog)
    print(f"sync_courses: {n} course page(s) updated, schedule {'updated' if s else 'unchanged'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
