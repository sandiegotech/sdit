#!/usr/bin/env python3
"""scaffold_day.py — create a new lesson day from the canonical template.

    python3 scripts/scaffold_day.py HUM-101 2

Writes courses/<DIR>/day-NN.md in the standard lesson shape (front matter, H1,
intro line, prose sections). Never overwrites an existing file. After editing,
run scripts/build_site.py to publish.
"""
from __future__ import annotations

import sys
from pathlib import Path

from catalog import load_catalog

ROOT = Path(__file__).resolve().parents[1]

TEMPLATE = '''---
id: {id}
title: "Day {nn} — Title goes here"
day: {n}
course: {course}
---

# Day {nn} — Title goes here

Ten minutes. One idea, one thing to experience, one question.

## Look

Set the scene — an image, a passage, a short clip — then say plainly why it
matters to the reader today.

## Carry the question

For the rest of today, carry this one:

**The question goes here.**

No right answer, no writing required.

That's it. **Day {n} is done.**

## If you're still curious

One or two optional doors — a reading, a film, a person to ask.
'''


def course_label(course_dir: str) -> str:
    for c in load_catalog().get("courses", []):
        if c.get("dir") == course_dir:
            return f"{c.get('code', course_dir)} — {c.get('name', '')}".strip(" —")
    return course_dir


def main(argv) -> int:
    if len(argv) != 2:
        print("usage: scaffold_day.py <COURSE-DIR> <DAY-NUMBER>")
        return 2
    course_dir, day_s = argv
    try:
        n = int(day_s)
    except ValueError:
        print(f"day number must be an integer, got {day_s!r}")
        return 2

    path = ROOT / "courses" / course_dir / f"day-{n:02d}.md"
    if not path.parent.exists():
        print(f"no such course directory: courses/{course_dir}")
        return 1
    if path.exists():
        print(f"refusing to overwrite existing {path.relative_to(ROOT)}")
        return 1

    path.write_text(
        TEMPLATE.format(
            id=f"{course_dir.lower().replace('-', '')}-day-{n:02d}",
            nn=f"{n:02d}",
            n=n,
            course=course_label(course_dir),
        ),
        encoding="utf-8",
    )
    print(f"created {path.relative_to(ROOT)} — edit the title/content, then run build_site.py.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
