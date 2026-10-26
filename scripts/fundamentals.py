#!/usr/bin/env python3
"""fundamentals.py — the Studio Fundamentals: where each is taught, where shown.

    load()            -> the knowledge/fundamentals.yaml data
    check()           -> list of error strings (empty when the map holds)
    for_course(dir)   -> fundamentals a course's highlight is expected to show
    taught_in(dir)    -> (day n, fundamental) pairs taught in a course
    page()            -> HTML for curriculum/fundamentals.html

The map is kept honest in three places: the validator refuses an arc whose
named day no longer carries its fundamental's mark; the course page says which
fundamentals its highlight should show; and the Portfolio prints the same list
under each highlight, so a reader can see the basics behind the flavor.
"""
from __future__ import annotations

import html
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "knowledge" / "fundamentals.yaml"
_DATA = None


def load() -> dict:
    global _DATA
    if _DATA is None:
        import yaml
        _DATA = yaml.safe_load(FILE.read_text(encoding="utf-8"))
    return _DATA


def _e(s) -> str:
    return html.escape(str(s), quote=True)


def _taught(f: dict) -> tuple[str, int]:
    course, n = str(f["taught"]).split("/")
    return course, int(n)


def check() -> list[str]:
    """Every fundamental names a real Year 1 or 2 day whose arc idea carries its
    mark, and every course it is shown in exists."""
    import arcs
    from catalog import load_catalog
    data = load()
    courses = {c["dir"]: c for c in load_catalog()["courses"]}
    groups = {g["id"] for g in data.get("groups", [])}
    errs, seen = [], set()
    for f in data.get("fundamentals", []):
        fid = f.get("id", "?")
        if fid in seen:
            errs.append(f"fundamental {fid!r} is listed twice")
        seen.add(fid)
        for key in ("group", "name", "statement", "taught", "mark", "shown_in"):
            if not f.get(key):
                errs.append(f"fundamental {fid!r} has no {key}")
        if f.get("group") not in groups:
            errs.append(f"fundamental {fid!r}: unknown group {f.get('group')!r}")
        try:
            course, n = _taught(f)
        except (ValueError, KeyError):
            errs.append(f"fundamental {fid!r}: taught must be COURSE/day, got {f.get('taught')!r}")
            continue
        c = courses.get(course)
        if not c:
            errs.append(f"fundamental {fid!r}: taught in unknown course {course}")
            continue
        if int(c.get("semester") or 9) > 4:
            errs.append(f"fundamental {fid!r}: taught in {course}, semester {c.get('semester')}; every fundamental is taught by the end of Year 2")
        arc = arcs.load_arc(ROOT / "courses" / course)
        day = arc.day(n) if arc else None
        if not day:
            errs.append(f"fundamental {fid!r}: {course} has no arc day {n}")
        elif str(f.get("mark", "")).lower() not in day.idea.lower():
            errs.append(f"fundamental {fid!r}: {course} day {n} ('{day.title}') no longer carries the mark {f.get('mark')!r}; teach it there or move it")
        for d in f.get("shown_in") or []:
            if d not in courses:
                errs.append(f"fundamental {fid!r}: shown_in names unknown course {d}")
        if course not in (f.get("shown_in") or []):
            errs.append(f"fundamental {fid!r}: the course that teaches it ({course}) must also show it")
    return errs


def for_course(dir: str) -> list[dict]:
    return [f for f in load().get("fundamentals", []) if dir in (f.get("shown_in") or [])]


def taught_in(dir: str) -> list[tuple[int, dict]]:
    out = []
    for f in load().get("fundamentals", []):
        course, n = _taught(f)
        if course == dir:
            out.append((n, f))
    return sorted(out, key=lambda x: x[0])


def course_note(dir: str) -> str:
    """The line under The Made Thing on a course page."""
    fs = for_course(dir)
    if not fs:
        return ""
    items = " · ".join(f'<a href="/curriculum/fundamentals.html#{_e(f["id"])}">{_e(f["name"])}</a>' for f in fs)
    return (f'<p class="made-fundamentals"><strong>Shows the fundamentals:</strong> {items}. '
            f'The basics every highlight here is expected to carry; what you make with them is yours.</p>\n')


def page() -> str:
    import review_grade
    from catalog import load_catalog
    data = load()
    courses = {c["dir"]: c for c in load_catalog()["courses"]}
    meta = data["__meta__"]
    by_group: dict[str, list[dict]] = {}
    for f in data["fundamentals"]:
        by_group.setdefault(f["group"], []).append(f)
    body = []
    intro = (f'          <p>{_e(meta["description"]).strip()}</p>\n'
             f'          <p>{_e(meta["rule"]).strip()}</p>\n'
             '          <p>Each course page lists the fundamentals its highlight is expected to show, and the Portfolio prints the same list under the highlight. '
             'The fundamentals are the shared floor; the work on top of them is each learner\'s own.</p>')
    body.append(review_grade._section("The rule", "12 fundamentals", intro, "rule"))
    for g in data["groups"]:
        rows = []
        for f in by_group.get(g["id"], []):
            course, n = _taught(f)
            c = courses[course]
            day = f'<a href="/courses/{_e(course)}/">{_e(c["code"])}</a> · Day {n}'
            shown = ", ".join(f'<a href="/courses/{_e(d)}/">{_e(courses[d]["code"])}</a>' for d in f["shown_in"] if d in courses)
            rows.append(f'<tr id="{_e(f["id"])}"><th>{_e(f["name"])}<span>{_e(f["statement"]).strip()}</span></th>'
                        f'<td>{day}<br><small>Semester {c.get("semester")}</small></td><td>{shown}</td></tr>')
        inner = ('          <div class="evidence-table-wrap"><table class="evidence-table rubric-table"><thead><tr>'
                 '<th>Fundamental</th><th>Taught, by name</th><th>Shown in the highlight of</th></tr></thead>'
                 f'<tbody>{"".join(rows)}</tbody></table></div>')
        body.append(review_grade._section(g["name"], f"{len(by_group.get(g['id'], []))} fundamentals", inner, g["id"]))
    return review_grade._shell("The Studio Fundamentals", "For Learners and Reviewers", "The studio <em>fundamentals</em>.",
                               f"{len(data['fundamentals'])} working skills · taught by name in Years 1 and 2 · shown in every highlight after",
                               "The twelve working skills every learner has by the end of Year 2: the image, sound and the moving image, the record, and showing. Where each is taught, and which highlights show it.",
                               "".join(body))
