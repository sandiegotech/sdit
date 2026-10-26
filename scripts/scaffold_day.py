#!/usr/bin/env python3
"""scaffold_day.py — create a new lesson day from the canonical template.

    python3 scripts/scaffold_day.py HUM-101 2

Writes courses/<DIR>/day-NN.md in day standard v2: front matter with the
question, the H1, a one-line dek, one thing to experience ON the page, one
idea, the question to carry with its answer field, the done line, and three
optional doors. The title, the question, and the arc's notes for the thing,
the idea, and the doors are filled in from courses/<DIR>/arc.md; the author
writes the dek, the thing on the page, the idea, and the doors. Refuses to write a day the
course's planned length does not include, or to overwrite an existing file.
After editing, run scripts/build_site.py --out . to publish.

The template is the day standard (the Nine Laws, made mechanical). The HTML
comments in it are the rules; delete them as you write.
"""
from __future__ import annotations

import sys
from pathlib import Path

from catalog import load_catalog, planned_days

ROOT = Path(__file__).resolve().parents[1]

TEMPLATE = '''---
id: {id}
title: "Day {nn} — {title}"
day: {n}
course: {course}
question: "{question}"
---

# Day {nn} — {title}

DEK: one line, under fifteen words, naming what the day holds.

---

<!-- From the arc, the thing to experience: {thing} -->
## Look
<!-- Or "## Watch", "## Listen", "## Read": exactly one. The thing goes ON the
     page: a <figure> with an <img> from upload.wikimedia.org (alt,
     loading="lazy", referrerpolicy="no-referrer", and a figcaption), or an
     <iframe> from www.youtube-nocookie.com, or a <blockquote> from Project
     Gutenberg or a Lectio edition. Then one paragraph on why it matters
     today. -->

---

<!-- From the arc, the one idea: {idea} -->
## One idea
<!-- 300 to 450 words. One idea only. Short declarative sentences. Physical
     before formal: no concept arrives as notation first. Name the course's
     catalog register once. No hype words. -->

---

## Carry the question

For the rest of today, carry this one:

**{question}**

Answer in a line or a page, or not at all. What you write is kept in your Notebook.

<!-- sdit:answer -->

That's it. **Day {n} is done.**

---

## If you're still curious

Three doors. Open one, or none — they'll be here tomorrow too.

<!-- From the arc: {doors} -->

**Read the real thing.** WRITE THE READING DOOR.

**Watch (or listen to) the other half.** WRITE THE WATCH OR LISTEN DOOR.

**Ask someone.** Tonight, ask someone you trust: *"WRITE THE QUESTION TO ASK."* WRITE WHAT TO LISTEN FOR.
'''


def course_record(course_dir: str) -> dict | None:
    for c in load_catalog().get("courses", []):
        if c.get("dir") == course_dir:
            return c
    return None


def course_label(course_dir: str) -> str:
    c = course_record(course_dir)
    if not c:
        return course_dir
    return f"{c.get('code', course_dir)} — {c.get('name', '')}".strip(" —")


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
    course = course_record(course_dir)
    if course is not None:
        planned = planned_days(course)
        if not (1 <= n <= planned):
            print(f"{course_dir} plans {planned} days; day {n} is outside that. "
                  f"Change days_planned in knowledge/catalog.yaml first if that is the decision.")
            return 1
        if n > 1 and not (path.parent / f"day-{n - 1:02d}.md").exists():
            print(f"day-{n - 1:02d}.md does not exist yet; days publish in order, so write it first.")
            return 1

    import arcs
    arc = arcs.load_arc(course_dir)
    a = arc.day(n) if arc else None

    def clean(v: str) -> str:
        # Arc cells go into HTML comments and a YAML string: keep both valid.
        return (v or "").replace("-->", "—>").replace('"', "\u201d")

    path.write_text(
        TEMPLATE.format(
            id=f"{course_dir.lower().replace('-', '')}-day-{n:02d}",
            nn=f"{n:02d}",
            n=n,
            course=course_label(course_dir),
            title=a.title if a else "Title goes here",
            question=clean(a.question) if a else "The question goes here.",
            thing=clean(a.thing) if a else "",
            idea=clean(a.idea) if a else "",
            doors=clean(a.doors) if a else "",
        ),
        encoding="utf-8",
    )
    print(f"created {path.relative_to(ROOT)} — edit the title/content, then run build_site.py.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
