#!/usr/bin/env python3
"""scaffold_day.py — create a new lesson day from the canonical template.

    python3 scripts/scaffold_day.py HUM-101 2

Writes courses/<DIR>/day-NN.md in the standard lesson shape: front matter, the
H1, a one-line dek, one thing to experience ON the page, one idea, one question
to carry, the done line, and three optional doors. Refuses to write a day the
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
title: "Day {nn} — Title goes here"
day: {n}
course: {course}
---

# Day {nn} — Title goes here

Ten minutes. One thing to experience, one idea, one question.
<!-- The dek: one line, under fifteen words, naming what the day holds. It is
     reused on the course page and the schedule. -->

---

## Look
<!-- Or "## Watch" or "## Listen". The thing to experience goes ON the page:
     an image from Wikimedia Commons, a passage from Project Gutenberg or a
     Lectio edition, an embeddable clip or recording. Never "go watch this."
     Public domain, openly licensed, or embeddable by its publisher — nothing
     else. Then one short paragraph on why it matters to the reader today. -->

<figure class="day-figure">
  <img src="IMAGE-URL" alt="Describe the image for someone who cannot see it" loading="lazy" />
  <figcaption><strong>Title of the work.</strong> Maker, date. One or two sentences on what to look at.</figcaption>
</figure>

Why it matters today, in a paragraph.

---

## One idea
<!-- A few hundred words. One idea only; if a draft has two, it is two days or
     one day with a door. The whole main path, doors excluded, runs 400 to 600
     words. Physical before formal: no concept arrives as notation first.
     Short declarative sentences. No hype words. Name the course's catalog
     register once, somewhere, so a transcript reader can place the day. -->

The idea, plainly.

---

## Carry the question

For the rest of today, carry this one:

**The question goes here.**

No right answer, no writing required.

That's it. **Day {n} is done.**

---

## If you're still curious

Three doors. Open one, or none — they'll be here tomorrow too.
<!-- Always three: something to read, something to watch or hear, someone to
     ask. The "ask someone" door is the signature of these days. Keep it. -->

**Read the real thing.** [Title](URL) — what to read and how much.

**Watch (or listen to) the other half.** [Title](URL) — the film or album half of the pairing, and why.

**Ask someone.** Tonight, ask someone you trust: *"The question to ask them."* What to listen for.
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
