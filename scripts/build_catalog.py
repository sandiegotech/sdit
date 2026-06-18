#!/usr/bin/env python3
"""build_catalog.py — emit assets/catalog.json for the signed-in course mode.

A compact, browser-fetchable index of courses and their published days, so the
signed-in learning environment can show a course title, progress, and the next
lesson without reading the site's markdown at runtime.

Source of truth is the same as the schedule: knowledge/catalog.yaml for course
names, and courses/<dir>/day-NN.md for published-day titles (via sync_courses).
"""
from __future__ import annotations

import json
from pathlib import Path

from catalog import TOTAL_DAYS, load_catalog, day_info

ROOT = Path(__file__).resolve().parents[1]


def build_catalog() -> dict:
    catalog = load_catalog()
    courses = {}
    for c in catalog.get("courses", []):
        dir_name = c.get("dir")
        if not dir_name:
            continue
        course_dir = ROOT / "courses" / dir_name
        if not course_dir.exists():
            continue
        days = []
        for n in range(1, TOTAL_DAYS + 1):
            info = day_info(course_dir, n)
            if not info:
                continue
            title, _dek = info
            days.append({
                "n": n,
                "path": f"/courses/{dir_name}/day-{n:02d}",
                "title": title,
            })
        courses[dir_name] = {
            "code": c.get("code", dir_name),
            "name": c.get("display") or c.get("name") or c.get("code", dir_name),
            "thread": c.get("thread", ""),
            "semester": c.get("semester"),
            "plannedDays": TOTAL_DAYS,
            "days": days,
        }
    return {"courses": courses}


def main(out_dir: Path | None = None) -> int:
    out_dir = out_dir or (ROOT / "assets")
    out_dir.mkdir(parents=True, exist_ok=True)
    data = build_catalog()
    (out_dir / "catalog.json").write_text(
        json.dumps(data, indent=2) + "\n", encoding="utf-8"
    )
    n_days = sum(len(c["days"]) for c in data["courses"].values())
    print(f"build_catalog: {len(data['courses'])} courses, {n_days} published days")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
