#!/usr/bin/env python3
"""catalog.py — the course/day data layer.

    load_catalog()           -> dict from knowledge/catalog.yaml
    day_info(course_dir, n)  -> (title, dek) for a published day, or None
    published_days(dir)      -> [day numbers that actually have a file]
    planned_days(course)     -> course length (catalog `days_planned`, else DEFAULT_DAYS)

Shared by sync_courses.py (schedule + course index generation) and
build_catalog.py (the browser catalog.json) so both read days the same way.
"""
from __future__ import annotations

import re
from pathlib import Path

import frontmatter

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "knowledge" / "catalog.yaml"
DEFAULT_DAYS = 15  # planned length of a Foundation course unless it overrides it


def load_catalog() -> dict:
    import yaml

    return yaml.safe_load(CATALOG.read_text(encoding="utf-8"))


def planned_days(course: dict) -> int:
    """A course's planned length — catalog `days_planned`, else DEFAULT_DAYS."""
    try:
        return int(course.get("days_planned", DEFAULT_DAYS))
    except (TypeError, ValueError):
        return DEFAULT_DAYS


def published_days(course_dir: Path) -> list[int]:
    """The day numbers that actually have a day-NN.md file, sorted."""
    days = []
    for f in course_dir.glob("day-*.md"):
        m = re.match(r"day-(\d+)\.md$", f.name)
        if m:
            days.append(int(m.group(1)))
    return sorted(days)


def day_info(course_dir: Path, n: int):
    """Return (title, dek) for day n, or None if the file doesn't exist."""
    f = course_dir / f"day-{n:02d}.md"
    if not f.exists():
        return None
    meta, body = frontmatter.parse(f.read_text(encoding="utf-8"))
    title = str(meta.get("title", f"Day {n:02d}"))
    title = re.sub(r"^Day\s+\d+\s*[—–-]\s*", "", title).strip()
    # Dek = first non-empty body line after the H1.
    dek = ""
    for line in body.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("---"):
            continue
        dek = line
        break
    return title, dek
