#!/usr/bin/env python3
"""status.py — at-a-glance course authoring status. Read-only.

    python3 scripts/status.py          # every course, published vs planned days
    python3 scripts/status.py --gaps   # only courses with days still to write
    python3 scripts/status.py --next   # the next week to write, day by day
"""
from __future__ import annotations

import sys
from pathlib import Path

from catalog import load_catalog, planned_days, published_days

ROOT = Path(__file__).resolve().parents[1]
COURSES = ROOT / "courses"


def next_week() -> int:
    """The first week on the Path with a spine day not yet written: every day
    of it in weekday order, with its arc title, question, and publish date.
    Weeks are written whole, all courses together, never one course ahead."""
    import arcs
    import degree_path
    import publishing

    pending = [s for s in degree_path.sequence() if s.kind == "day" and not s.studio and not s.written]
    if not pending:
        print("Every spine day is written.")
        return 0
    sem, week = pending[0].semester, pending[0].week
    when = publishing.week_date(sem, week)
    print(f"Next to write: Semester {sem}, Week {week}"
          + (f" (publishes {publishing.long_date(when)})" if when else ""))
    print()
    for s in degree_path.sequence():
        if s.kind != "day" or s.semester != sem or s.week != week:
            continue
        c = s.course or {}
        a = arcs.load_arc(COURSES / c["dir"])
        q = a.day(s.n).question if a and a.day(s.n) else ""
        state = "written" if s.written else "TO WRITE"
        print(f"  {s.label:<6} {c['dir']:<9} Day {s.n:02d}  {state:<8}  {s.title}")
        if not s.written:
            print(f"         {'':9} question: {q}")
            print(f"         {'':9} python3 scripts/scaffold_day.py {c['dir']} {s.n}")
    ahead = sum(1 for s in degree_path.sequence() if s.kind == "day" and s.written and not s.published)
    rs, rw = publishing.released_through()
    print()
    print(f"Released through Semester {rs}, Week {rw}. Written ahead of the release gate: {ahead} day(s).")
    print("Release the next week by moving released_through in knowledge/calendar.yaml, then build, commit, deploy.")
    return 0


def main(argv) -> int:
    if "--next" in argv:
        return next_week()
    gaps_only = "--gaps" in argv
    courses = sorted(
        load_catalog().get("courses", []),
        key=lambda c: (c.get("semester") or 99, c.get("dir") or ""),
    )

    rows, total_pub, total_planned = [], 0, 0
    for c in courses:
        d = c.get("dir")
        if not d:
            continue
        cdir = COURSES / d
        pub = len(published_days(cdir)) if cdir.exists() else 0
        planned = planned_days(c)
        total_pub += pub
        total_planned += planned
        if gaps_only and pub >= planned:
            continue
        bar = "#" * pub + "." * max(0, planned - pub)
        arc = "arc" if (cdir / "arc.md").exists() else "-"
        rows.append((str(c.get("semester") or "-"), d, f"{pub}/{planned}", bar, arc, c.get("status", "")))

    w = max((len(r[1]) for r in rows), default=6)
    print(f"{'sem':>3}  {'course':<{w}}  {'days':>6}  {'progress':<16} {'arc':<4} status")
    for sem, d, days, bar, arc, status in rows:
        print(f"{sem:>3}  {d:<{w}}  {days:>6}  {bar:<16} {arc:<4} {status}")
    arcs = sum(1 for r in rows if r[4] == "arc")
    print(f"\n{total_pub}/{total_planned} days published across {len(courses)} courses; {arcs} arc(s) written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
