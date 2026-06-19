#!/usr/bin/env python3
"""status.py — at-a-glance course authoring status. Read-only.

    python3 scripts/status.py          # every course, published vs planned days
    python3 scripts/status.py --gaps   # only courses with days still to write
"""
from __future__ import annotations

import sys
from pathlib import Path

from catalog import load_catalog, planned_days, published_days

ROOT = Path(__file__).resolve().parents[1]
COURSES = ROOT / "courses"


def main(argv) -> int:
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
        rows.append((str(c.get("semester") or "-"), d, f"{pub}/{planned}", bar, c.get("status", "")))

    w = max((len(r[1]) for r in rows), default=6)
    print(f"{'sem':>3}  {'course':<{w}}  {'days':>6}  progress")
    for sem, d, days, bar, status in rows:
        print(f"{sem:>3}  {d:<{w}}  {days:>6}  {bar}  {status}")
    print(f"\n{total_pub}/{total_planned} days published across {len(courses)} courses.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
