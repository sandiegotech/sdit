#!/usr/bin/env python3
"""catalog.py — the course/day data layer.

    load_catalog()           -> dict from knowledge/catalog.yaml
    day_info(course_dir, n)  -> (title, dek) for a published day, or None
    TOTAL_DAYS               -> planned length of a Foundation course

Shared by sync_courses.py (schedule + course index generation) and
build_catalog.py (the browser catalog.json) so both read days the same way.
"""
from __future__ import annotations

import re
from pathlib import Path

import frontmatter

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "knowledge" / "catalog.yaml"
TOTAL_DAYS = 15


def load_catalog() -> dict:
    import yaml

    return yaml.safe_load(CATALOG.read_text(encoding="utf-8"))


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
