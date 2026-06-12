#!/usr/bin/env python3
"""
Scaffold course pages from the catalog registry.

Reads knowledge/catalog.yaml and writes courses/<dir>/index.md for every
catalog course that does not already have one. Existing files are NEVER
overwritten — after scaffolding, the markdown is the live content source
and this script only fills gaps (e.g. when a new course is added to the
registry).

Run:  python3 scripts/scaffold_catalog.py
Then: python3 scripts/build_site.py --out .
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "knowledge" / "catalog.yaml"
COURSES = ROOT / "courses"

OUTCOME_NAMES = {
    "judgment": "Judgment",
    "intelligence": "Command of Intelligence",
    "craft": "Craft",
    "articulation": "Articulation",
    "breadth": "Breadth of Mind",
}

STATUS_LINES = {
    "day1": "Day 1 is live below; the rest of the daily path is being written.",
    "building": "The daily path for this course is being written now.",
    "syllabus": "This course is at syllabus stage — the daily path is not yet written, so it is not yet live.",
    "planned": "This course is planned and not yet written.",
}

TEMPLATE = """---
id: {cid}
title: "{code} — {name}"
course_code: {code}
units: {units}
thread: {thread_name}
status: {status}
---

# {code} — {name}

**{thread_name}** · {units} units · {degrees_label}

## The Two Registers

- **Catalog register:** {catalog_register}
- **Teaching frame:** {teaching_frame}

## Outcomes Served

{outcomes_list}

## What This Course Is About

{description}

## The Made Thing

{artifact}

## The Daily Path

One session per course day — each one designed to look easy and pull you in. {status_line}

{days_list}

---

*Every course here is built to one standard: it ends in a made thing you can show, and it ships day by day.*
"""


def degrees_label(c: dict) -> str:
    concs = c.get("concentrations")
    if concs:
        names = " & ".join(x.title() for x in concs)
        return f"Depth studio — {names} · the Crossing for others"
    return {
        "both": "Required core — everyone takes it",
    }.get(c.get("degrees", "both"), c.get("degrees", ""))


def main() -> int:
    data = yaml.safe_load(CATALOG.read_text(encoding="utf-8"))
    threads = {t["id"]: t["name"] for t in data.get("threads", [])}
    made, skipped = 0, 0

    for c in data["courses"]:
        cdir = COURSES / c["dir"]
        index_md = cdir / "index.md"
        if index_md.exists():
            skipped += 1
            continue

        outcomes = "\n".join(
            f"- **{OUTCOME_NAMES.get(o, o)}**" for o in c.get("outcomes", [])
        )

        day_lines = []
        for n in range(1, 16):
            day_md = cdir / f"day-{n:02d}.md"
            if day_md.exists():
                # Title from the day file's front matter if present
                title = None
                for line in day_md.read_text(encoding="utf-8").splitlines():
                    if line.startswith("title:"):
                        title = line.split(":", 1)[1].strip().strip('"')
                        break
                label = title or f"Day {n:02d}"
                day_lines.append(f"- [{label}](day-{n:02d}.html)")
            else:
                day_lines.append(f"- Day {n:02d} — *to be written*")

        body = TEMPLATE.format(
            cid=c["dir"].lower(),
            code=c["code"],
            name=c["name"],
            units=c["units"],
            thread_name=threads.get(c["thread"], c["thread"]),
            status=c["status"],
            degrees_label=degrees_label(c),
            catalog_register=c["catalog_register"],
            teaching_frame=c["teaching_frame"],
            outcomes_list=outcomes,
            description=" ".join(c["description"].split()),
            artifact=c["artifact"],
            status_line=STATUS_LINES.get(c["status"], ""),
            days_list="\n".join(day_lines),
        )

        cdir.mkdir(parents=True, exist_ok=True)
        index_md.write_text(body, encoding="utf-8")
        made += 1
        print(f"scaffolded {index_md.relative_to(ROOT)}")

    print(f"Done: {made} scaffolded, {skipped} already existed (left untouched).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
