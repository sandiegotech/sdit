#!/usr/bin/env python3
"""validate.py — fail the build on a registry that disagrees with the files.

Every knowledge/*.yaml must parse as a mapping. Then knowledge/catalog.yaml is
checked course by course:

  - required fields present; dirs and codes unique; thread ids real
  - semester 1-8; units a positive integer; days_planned an explicit integer
  - outcomes non-empty and drawn from the five institutional outcomes
  - depth studios name their concentrations
  - the course directory and its index.md exist
  - published days are contiguous from day 1 and never exceed days_planned
  - each day file's front-matter `day:` matches its filename
  - status agrees with the files on disk:
        planned / syllabus  -> no day files
        building            -> no day files (being written, none published)
        day1                -> at least one day file
        live                -> every planned day, and an index.md at catalog grade
  - the index.md front-matter status mirrors the registry (sync_courses keeps it so)

Nothing is called live until a learner knows exactly what to do each day.
"""
from __future__ import annotations

import re
import sys
from glob import glob
from pathlib import Path

import yaml

import catalog as catalog_mod
import frontmatter

ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE = ROOT / "knowledge"
COURSES = ROOT / "courses"

REQUIRED_COURSE_FIELDS = [
    "code", "dir", "name", "units", "thread", "semester", "status",
    "days_planned", "outcomes", "catalog_register", "teaching_frame", "artifact",
]
STATUSES = {"planned", "syllabus", "building", "day1", "live"}
OUTCOMES = {"judgment", "intelligence", "craft", "articulation", "breadth"}
CONCENTRATIONS = {"media", "design", "engineering"}
MAX_DAYS = 60

# What a course page must carry before its course can be called live.
LIVE_HEADINGS = [
    "## Overview",
    "## The Two Registers",
    "## Learning Outcomes",
    "## The Made Thing",
    "## How You're Assessed",
    "## The Daily Path",
]


def load(p):
    with open(p, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def validate_yaml_files(errors, knowledge: Path = KNOWLEDGE):
    for f in glob(str(knowledge / "*.yaml")):
        try:
            data = load(f)
            if not isinstance(data, dict):
                raise ValueError("top-level YAML must be a mapping")
        except Exception as e:
            errors.append(f"{Path(f).name}: {e}")


def _positive_int(v) -> bool:
    return isinstance(v, int) and not isinstance(v, bool) and v >= 1


def validate_course(c: dict, i: int, threads: set, courses_root: Path, errors: list) -> None:
    label = c.get("dir") or c.get("code") or f"#{i}"
    err = lambda msg: errors.append(f"catalog.yaml: {label} {msg}")

    for field in REQUIRED_COURSE_FIELDS:
        if c.get(field) in (None, "", []):
            err(f"missing required field `{field}`")

    sem = c.get("semester")
    if sem is not None and not (isinstance(sem, int) and 1 <= sem <= 8):
        err(f"has invalid semester {sem!r} (want int 1-8)")

    if "units" in c and not _positive_int(c.get("units")):
        err(f"has invalid units {c.get('units')!r} (want a positive integer; one course per semester)")

    planned = c.get("days_planned")
    if planned is not None and not (_positive_int(planned) and planned <= MAX_DAYS):
        err(f"has invalid days_planned {planned!r} (want int 1-{MAX_DAYS})")

    if threads and c.get("thread") and c["thread"] not in threads:
        err(f"names unknown thread `{c['thread']}`")

    status = c.get("status")
    if status is not None and status not in STATUSES:
        err(f"has unknown status `{status}` (want one of {', '.join(sorted(STATUSES))})")

    outcomes = c.get("outcomes")
    if outcomes is not None:
        if not isinstance(outcomes, list) or not outcomes:
            err("must list at least one outcome")
        else:
            for o in outcomes:
                if o not in OUTCOMES:
                    err(f"names unknown outcome `{o}` (want one of {', '.join(sorted(OUTCOMES))})")

    if c.get("thread") == "depth":
        concs = c.get("concentrations")
        if not isinstance(concs, list) or not concs:
            err("is a depth studio but names no concentrations")
        else:
            for k in concs:
                if k not in CONCENTRATIONS:
                    err(f"names unknown concentration `{k}`")

    d = c.get("dir")
    if not d:
        return
    cdir = courses_root / d
    if not cdir.is_dir():
        err(f"has no directory courses/{d} (run scripts/scaffold_catalog.py)")
        return
    index_md = cdir / "index.md"
    if not index_md.exists():
        err(f"has no courses/{d}/index.md (run scripts/scaffold_catalog.py)")

    days = catalog_mod.published_days(cdir)
    if days != list(range(1, len(days) + 1)):
        err(f"has a gap in its day files ({', '.join(f'day-{n:02d}' for n in days)}); days publish in order from day 1")
    if _positive_int(planned) and days and days[-1] > planned:
        err(f"has day-{days[-1]:02d}.md but plans only {planned} days")

    for n in days:
        f = cdir / f"day-{n:02d}.md"
        meta, _body = frontmatter.parse(f.read_text(encoding="utf-8"))
        fm_day = meta.get("day")
        try:
            fm_day = int(fm_day) if fm_day is not None else None
        except (TypeError, ValueError):
            pass
        if fm_day is not None and fm_day != n:
            err(f"day-{n:02d}.md says `day: {meta.get('day')}` in its front matter")
        if not meta.get("title"):
            err(f"day-{n:02d}.md has no `title` in its front matter")

    if status in ("planned", "syllabus", "building") and days:
        err(f"has status `{status}` but {len(days)} published day file(s); set `day1` (or `live`)")
    if status == "day1" and not days:
        err("has status `day1` but no day-NN.md file")
    if status == "live":
        if not _positive_int(planned):
            pass  # already reported
        elif len(days) < planned:
            err(f"has status `live` but only {len(days)} of {planned} days exist")
        if index_md.exists():
            text = index_md.read_text(encoding="utf-8")
            missing = [h for h in LIVE_HEADINGS if h not in text]
            if missing:
                err(f"has status `live` but index.md lacks {', '.join(missing)}")

    if index_md.exists() and status:
        meta, _ = frontmatter.parse(index_md.read_text(encoding="utf-8"))
        fm_status = meta.get("status")
        if fm_status is not None and str(fm_status) != str(status):
            err(f"index.md front matter says `status: {fm_status}` but the registry says `{status}` "
                f"(run scripts/sync_courses.py)")


def validate_catalog(errors, data: dict | None = None, courses_root: Path = COURSES):
    if data is None:
        path = KNOWLEDGE / "catalog.yaml"
        if not path.exists():
            return
        data = load(path) or {}
    courses = data.get("courses", [])
    if not isinstance(courses, list):
        errors.append("catalog.yaml: `courses` must be a list")
        return
    threads = {t.get("id") for t in data.get("threads", []) if isinstance(t, dict)}

    seen_dirs, seen_codes = set(), set()
    for i, c in enumerate(courses):
        if not isinstance(c, dict):
            errors.append(f"catalog.yaml: course #{i} is not a mapping")
            continue
        d = c.get("dir")
        if d:
            if d in seen_dirs:
                errors.append(f"catalog.yaml: duplicate dir `{d}`")
            seen_dirs.add(d)
        code = c.get("code")
        if code:
            if code in seen_codes:
                errors.append(f"catalog.yaml: duplicate code `{code}`")
            seen_codes.add(code)
        validate_course(c, i, threads, courses_root, errors)

    # Every course directory on disk should be a registered course, so nothing
    # unlisted gets built and published by accident.
    if courses_root.is_dir():
        for p in sorted(courses_root.iterdir()):
            if p.is_dir() and not p.name.startswith(".") and p.name not in seen_dirs:
                errors.append(f"courses/{p.name}/ exists but is not in catalog.yaml")


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
