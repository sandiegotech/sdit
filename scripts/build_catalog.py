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

import arcs
import publishing
from catalog import planned_days, published_days, load_catalog, day_info

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
        for n in published_days(course_dir):
            info = day_info(course_dir, n)
            if not info:
                continue
            title, _dek = info
            days.append({
                "n": n,
                "path": f"/courses/{dir_name}/day-{n:02d}",
                "title": title,
            })
        arc = arcs.load_arc(course_dir)
        planned = []
        for n in range(1, planned_days(c) + 1):
            info = day_info(course_dir, n)
            arc_day = arc.day(n) if arc else None
            when = publishing.week_date(c["semester"], n) if c.get("semester") else None
            question = ""
            if info:
                import frontmatter
                meta, _ = frontmatter.parse((course_dir / f"day-{n:02d}.md").read_text(encoding="utf-8"))
                question = str(meta.get("question") or "")
            if not question and arc_day:
                question = arc_day.question
            planned.append({
                "n": n,
                "title": info[0] if info else (arc_day.title if arc_day else ""),
                "question": question,
                "publishes": None if info or not when else when.isoformat(),
            })
        courses[dir_name] = {
            "code": c.get("code", dir_name),
            "name": c.get("display") or c.get("name") or c.get("code", dir_name),
            "thread": c.get("thread", ""),
            "semester": c.get("semester"),
            "status": c.get("status", ""),
            "plannedDays": planned_days(c),
            "days": days,
            "planned": planned,
        }
    return {"courses": courses}


def main(out_dir: Path | None = None) -> int:
    out_dir = out_dir or (ROOT / "assets")
    out_dir.mkdir(parents=True, exist_ok=True)
    data = build_catalog()
    out = out_dir / "catalog.json"
    text = json.dumps(data, indent=2) + "\n"
    if not (out.exists() and out.read_text(encoding="utf-8") == text):
        out.write_text(text, encoding="utf-8")  # unchanged files keep their mtime
    n_days = sum(len(c["days"]) for c in data["courses"].values())
    print(f"build_catalog: {len(data['courses'])} courses, {n_days} published days")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
