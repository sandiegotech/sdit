#!/usr/bin/env python3
"""validate.py — fail the build on a malformed knowledge/ catalog.

Every knowledge/*.yaml must parse as a mapping. Then knowledge/catalog.yaml is
checked for required course fields, unique dirs, sane semesters, and that a
course claiming a live day actually has the day file (no silent broken links).
"""
from __future__ import annotations

import sys
from glob import glob
from pathlib import Path

import yaml

import catalog as catalog_mod

ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE = ROOT / "knowledge"
COURSES = ROOT / "courses"

REQUIRED_COURSE_FIELDS = ["code", "dir", "name", "thread", "semester"]


def load(p):
    with open(p, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def validate_yaml_files(errors):
    for f in glob(str(KNOWLEDGE / "*.yaml")):
        try:
            data = load(f)
            if not isinstance(data, dict):
                raise ValueError("top-level YAML must be a mapping")
        except Exception as e:
            errors.append(f"{Path(f).name}: {e}")


def validate_catalog(errors):
    path = KNOWLEDGE / "catalog.yaml"
    if not path.exists():
        return
    courses = (load(path) or {}).get("courses", [])
    if not isinstance(courses, list):
        errors.append("catalog.yaml: `courses` must be a list")
        return

    seen = set()
    for i, c in enumerate(courses):
        if not isinstance(c, dict):
            errors.append(f"catalog.yaml: course #{i} is not a mapping")
            continue
        label = c.get("dir") or c.get("code") or f"#{i}"

        for field in REQUIRED_COURSE_FIELDS:
            if not c.get(field):
                errors.append(f"catalog.yaml: {label} missing required field `{field}`")

        d = c.get("dir")
        if d:
            if d in seen:
                errors.append(f"catalog.yaml: duplicate dir `{d}`")
            seen.add(d)

        sem = c.get("semester")
        if sem is not None and not (isinstance(sem, int) and 1 <= sem <= 8):
            errors.append(f"catalog.yaml: {label} has invalid semester {sem!r} (want int 1-8)")

        # A course claiming a live first day must actually have one.
        if c.get("status") == "day1" and d:
            cdir = COURSES / d
            if not cdir.exists() or not catalog_mod.published_days(cdir):
                errors.append(f"catalog.yaml: {label} has status `day1` but no day-NN.md file")


def main() -> int:
    errors: list[str] = []
    validate_yaml_files(errors)
    validate_catalog(errors)
    if errors:
        for e in errors:
            print(f"[ERROR] {e}")
        print(f"Validation: FAILED ({len(errors)} issue(s))")
        return 1
    print("Validation: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
