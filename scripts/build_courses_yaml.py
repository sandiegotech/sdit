#!/usr/bin/env python3
"""
Scan the repository for course Markdown files, extract frontmatter, and
write a canonical master list to knowledge/courses.yaml.

Conventions assumed (flat layout):
- All course files live directly under courses/*.md
- Filenames begin with a code prefix (e.g., LBS-101, TECH-201)
- Frontmatter is YAML between leading '---' and the next '---'

Fields captured:
- id, title, level, tags from frontmatter (if present)
- code derived from filename prefix (e.g., LBS-101, LAB-201, TECH-201)
- This script is idempotent and safe to re-run.
"""
from __future__ import annotations

import re
import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

import yaml

ROOT = Path(__file__).resolve().parents[1]
COURSES_DIR = ROOT / "courses"
KNOWLEDGE_DIR = ROOT / "knowledge"
OUTPUT = KNOWLEDGE_DIR / "courses.yaml"


def read_frontmatter(md_path: Path) -> Dict[str, Any]:
    text = md_path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    try:
        _, fm_text, _ = text.split("---\n", 2)
        data = yaml.safe_load(fm_text) or {}
        if not isinstance(data, dict):
            return {}
        return data
    except Exception:
        return {}


CODE_RE = re.compile(r"^([A-Z]+-[0-9]+)")


def derive_code(md_path: Path) -> Optional[str]:
    m = CODE_RE.match(md_path.name)
    if m:
        return m.group(1)
    # electives may include course_code in frontmatter
    fm = read_frontmatter(md_path)
    cc = fm.get("course_code") if isinstance(fm, dict) else None
    if isinstance(cc, str) and cc.strip():
        return cc.strip()
    return None


def course_entry(md_path: Path) -> Optional[Dict[str, Any]]:
    rel = md_path.relative_to(ROOT).as_posix()
    fm = read_frontmatter(md_path)
    code = derive_code(md_path)
    title = None
    if isinstance(fm, dict):
        t = fm.get("title")
        if isinstance(t, str):
            title = t
    # fallback: derive from H1 if present
    if not title:
        for line in md_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break

    level = None
    tags = []
    cid = None
    if isinstance(fm, dict):
        level = fm.get("level")
        tags = fm.get("tags") or []
        cid = fm.get("id")

    # derive id if missing
    if not cid:
        if code:
            cid = code.lower()
        else:
            cid = md_path.stem.lower()

    entry = {
        "id": cid,
        "code": code,
        "title": title,
        "path": rel,
    }
    if isinstance(level, int):
        entry["level"] = level
    if isinstance(tags, list):
        entry["tags"] = tags

    return entry


def scan_courses() -> List[Dict[str, Any]]:
    entries: List[Dict[str, Any]] = []
    # Flat layout: all course markdown files live directly under courses/
    for md in COURSES_DIR.glob("*.md"):
        if md.name.lower() in {"index.md", "readme.md"}:
            continue
        ce = course_entry(md)
        if ce:
            entries.append(ce)
    # Sort by code then title
    entries.sort(key=lambda e: (e.get("code") or "", e.get("title") or ""))
    return entries


def main() -> int:
    courses = scan_courses()
    data: Dict[str, Any] = {
        "__meta__": {
            "title": "Courses",
            "description": "Canonical master list of all courses with paths and grouping.",
            "intended_use": "Source for generating curriculum and electives indexes; single source of truth for course paths and labels.",
        },
        "courses": courses,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    print(f"Wrote {OUTPUT}")
    print(f"Total courses: {len(courses)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
