#!/usr/bin/env python3
"""publishing.py — when each week of the degree publishes.

    week_date(semester, week)  -> date, or None for the launch week
    long_date(d) / short_date(d)

Reads knowledge/calendar.yaml. Weeks are counted straight through the degree:
Semester 1 Week 1 is week 0 (already live, no date), Semester 1 Week 2 is
`first_release`, and each later week follows `cadence_days` after the one
before, pushed back by any `breaks`. Deterministic: nothing here reads today's
date, so the built site does not change from one day to the next.
"""
from __future__ import annotations

import datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CALENDAR = ROOT / "knowledge" / "calendar.yaml"

_CAL = None


def load_calendar(path: Path = CALENDAR) -> dict:
    global _CAL
    if _CAL is None or path != CALENDAR:
        import yaml

        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if path != CALENDAR:
            return data
        _CAL = data
    return _CAL


def weeks_per_semester(cal: dict | None = None) -> int:
    cal = cal or load_calendar()
    return int(cal["semesters"][0]["weeks"])


def semester_label(n: int, cal: dict | None = None) -> str:
    cal = cal or load_calendar()
    for s in cal["semesters"]:
        if s["n"] == n:
            return s["label"]
    return ""


def week_index(semester: int, week: int, cal: dict | None = None) -> int:
    return (semester - 1) * weeks_per_semester(cal) + (week - 1)


def week_date(semester: int, week: int, cal: dict | None = None) -> dt.date | None:
    """The Monday a week publishes; None for Semester 1 Week 1, already live."""
    cal = cal or load_calendar()
    idx = week_index(semester, week, cal)
    if idx == 0:
        return None
    pub = cal["publishing"]
    first = pub["first_release"]
    if isinstance(first, str):
        first = dt.date.fromisoformat(first)
    cadence = int(pub.get("cadence_days", 7))
    shift = 0
    for b in pub.get("breaks") or []:
        after = b["after"]
        if idx > week_index(after["semester"], after["week"], cal):
            shift += int(b["weeks"])
    return first + dt.timedelta(days=cadence * (idx - 1 + shift))


def long_date(d: dt.date) -> str:
    return f"{d:%A}, {d.day} {d:%B} {d.year}"


def plain_date(d: dt.date) -> str:
    return f"{d.day} {d:%B} {d.year}"


def short_date(d: dt.date) -> str:
    return f"{d.day} {d:%b}"


# ── The release gate ─────────────────────────────────────────────────────────

def released_through(cal: dict | None = None) -> tuple[int, int]:
    """(semester, week) of the last released week. Weeks after it are backlog."""
    cal = cal or load_calendar()
    rt = (cal.get("publishing") or {}).get("released_through") or {}
    return int(rt.get("semester", 1)), int(rt.get("week", 1))


def released(semester: int, week: int, cal: dict | None = None) -> bool:
    """Is this week out? Earlier semesters are; later ones are not; the current
    one up to and including released_through's week."""
    rs, rw = released_through(cal)
    return (semester, week) <= (rs, rw)


def unreleased_paths(root: Path | None = None) -> list[str]:
    """Site paths of day pages that exist but are not yet released, so the
    deploy can leave them out: courses/<DIR>/day-NN.html and .md."""
    import re as _re
    from catalog import load_catalog
    root = root or ROOT
    out = []
    for c in load_catalog()["courses"]:
        sem = c.get("semester")
        cdir = root / "courses" / c["dir"]
        for f in sorted(cdir.glob("day-*.md")):
            m = _re.match(r"day-(\d+)\.md$", f.name)
            if not m or not sem:
                continue
            n = int(m.group(1))
            if not released(int(sem), n):
                out.append(f"courses/{c['dir']}/day-{n:02d}.md")
                out.append(f"courses/{c['dir']}/day-{n:02d}.html")
    return out


if __name__ == "__main__":
    import sys as _sys
    if "--unreleased-paths" in _sys.argv:
        print("\n".join(unreleased_paths()))
    else:
        rs, rw = released_through()
        print(f"released through Semester {rs}, Week {rw}; {len(unreleased_paths()) // 2} written day(s) in the backlog")
