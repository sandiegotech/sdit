#!/usr/bin/env python3
"""arcs.py — read a course's arc.md, the authoring plan for its days.

    load_arc(course_dir)  -> Arc, or None when the course has no arc.md
    parse_arc(text, src)  -> Arc

An arc has YAML front matter, `## ` sections, and one table under
"## The fifteen days" whose rows are

    | Day | Title | The thing to experience | The one idea | The question to carry | The three doors |

The arc is the source of truth for what each unwritten day will be called and
what it will ask, so the Path, the course pages, and the browser catalog can
show the whole degree before the days exist. A row that cannot be parsed is an
error naming the file and the row, never a silent gap.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import frontmatter

ROOT = Path(__file__).resolve().parents[1]
COURSES = ROOT / "courses"
DAY_TABLE = "## The fifteen days"
ROW_RE = re.compile(r"^\|\s*(\d+)\s*\|")
CELL_SPLIT = re.compile(r"(?<!\\)\|")


class ArcError(ValueError):
    """An arc.md that cannot be read as the standard says."""


@dataclass
class ArcDay:
    n: int
    title: str
    thing: str
    idea: str
    question: str
    doors: str


@dataclass
class Arc:
    source: str
    meta: dict
    days: dict[int, ArcDay] = field(default_factory=dict)
    sections: dict[str, str] = field(default_factory=dict)

    def day(self, n: int) -> ArcDay | None:
        return self.days.get(n)


def _cells(line: str) -> list[str]:
    parts = CELL_SPLIT.split(line.strip())
    # A row starts and ends with a pipe, so the first and last parts are empty.
    return [p.strip().replace("\\|", "|") for p in parts[1:-1]]


def parse_arc(text: str, source: str = "arc.md") -> Arc:
    meta, body = frontmatter.parse(text)
    arc = Arc(source=source, meta=meta if isinstance(meta, dict) else {})

    # Sections by `## ` heading, in order.
    current, buf = None, []
    for line in body.splitlines():
        if line.startswith("## "):
            if current is not None:
                arc.sections[current] = "\n".join(buf).strip()
            current, buf = line[3:].strip(), []
        elif current is not None:
            buf.append(line)
    if current is not None:
        arc.sections[current] = "\n".join(buf).strip()

    table = arc.sections.get(DAY_TABLE[3:])
    if table is None:
        raise ArcError(f"{source}: no '{DAY_TABLE}' section")

    for i, line in enumerate(table.splitlines(), 1):
        m = ROW_RE.match(line)
        if not m:
            continue
        cells = _cells(line)
        if len(cells) != 6:
            raise ArcError(f"{source}: day row {m.group(1)} has {len(cells)} cells, want 6: {line[:80]}")
        n = int(cells[0])
        if n in arc.days:
            raise ArcError(f"{source}: day {n} appears twice")
        if not cells[1]:
            raise ArcError(f"{source}: day {n} has no title")
        arc.days[n] = ArcDay(n, cells[1], cells[2], cells[3], cells[4], cells[5])

    if not arc.days:
        raise ArcError(f"{source}: the day table has no rows")
    expected = list(range(1, max(arc.days) + 1))
    if sorted(arc.days) != expected:
        missing = sorted(set(expected) - set(arc.days))
        raise ArcError(f"{source}: day rows are not contiguous from 1 (missing {missing})")
    return arc


_CACHE: dict[str, Arc | None] = {}


def load_arc(course_dir: str | Path) -> Arc | None:
    """The course's arc, parsed once per process; None when there is no arc.md."""
    d = Path(course_dir)
    if not d.is_absolute():
        d = COURSES / d
    key = str(d)
    if key not in _CACHE:
        f = d / "arc.md"
        _CACHE[key] = parse_arc(f.read_text(encoding="utf-8"), str(f.relative_to(ROOT))) if f.exists() else None
    return _CACHE[key]


def normalize_title(s: str) -> str:
    """Compare titles across files without tripping on typographic quotes."""
    return (s.replace("’", "'").replace("‘", "'")
             .replace("“", '"').replace("”", '"').strip())
