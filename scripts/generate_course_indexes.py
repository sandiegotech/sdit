#!/usr/bin/env python3
"""
Generate a single, flat course index from knowledge/courses.yaml:
- courses/INDEX.md (one list of all courses)

Run after scripts/build_courses_yaml.py.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, Any, List, DefaultDict
from collections import defaultdict

import yaml

ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE_COURSES = ROOT / "knowledge" / "courses.yaml"


def load_courses() -> List[Dict[str, Any]]:
    data = yaml.safe_load(KNOWLEDGE_COURSES.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "courses" not in data:
        raise SystemExit("Invalid courses.yaml format")
    courses = data["courses"]
    if not isinstance(courses, list):
        raise SystemExit("Invalid courses list in courses.yaml")
    return courses


def fmt_link(path: str, code: str | None, title: str | None) -> str:
    label = title or path
    if code:
        return f"- [{code}] {label} ({path})"
    return f"- {label} ({path})"


def gen_flat_index(courses: List[Dict[str, Any]]) -> None:
    items_sorted = sorted(courses, key=lambda c: (c.get("code") or "", c.get("title") or ""))
    lines: List[str] = []
    lines.append("<!-- GENERATED FILE: Do not edit directly. -->")
    lines.append("# Course List")
    lines.append("")
    for c in items_sorted:
        lines.append(fmt_link(c.get("path", ""), c.get("code"), c.get("title")))
    out_path = ROOT / "courses" / "INDEX.md"
    out_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")


def gen_core_indexes(courses: List[Dict[str, Any]]) -> None:
    # No per-volume indexes in flat mode
    return None


def main() -> int:
    courses = load_courses()
    gen_flat_index(courses)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
