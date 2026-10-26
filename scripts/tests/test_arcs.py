import arcs

ARC = """---
course: X 101 — Thing
semester: 1
days: 3
---

# Arc — X 101

## The made thing

A thing.

## The fifteen days

| Day | Title | Thing | Idea | Question | Doors |
|---|---|---|---|---|---|
| 1 | First Light | a photo \\| caption | one idea | What now? | read: a · watch: b · ask: c |
| 2 | Second | x | y | Why? | read · watch · ask |
| 3 | Third | x | y | How? | read · watch · ask |

## Outcome map

| Outcome | Days |
|---|---|
| Judgment | 1, 2 |
"""


def test_parse_rows_sections_and_escaped_pipe():
    a = arcs.parse_arc(ARC, "x/arc.md")
    assert sorted(a.days) == [1, 2, 3]
    assert a.day(1).title == "First Light"
    assert a.day(1).thing == "a photo | caption"
    assert a.day(3).question == "How?"
    assert a.sections["The made thing"] == "A thing."
    assert a.meta["semester"] == 1
    # The outcome-map table must not be read as day rows.
    assert a.day(4) is None


def _raises(text):
    try:
        arcs.parse_arc(text, "x/arc.md")
    except arcs.ArcError as e:
        return str(e)
    return None


def test_errors_name_the_problem():
    assert "no '## The fifteen days'" in _raises("---\na: 1\n---\n\n## Other\n")
    gap = ARC.replace("| 2 | Second | x | y | Why? | read · watch · ask |\n", "")
    assert "missing [2]" in _raises(gap)
    short = ARC.replace("| 3 | Third | x | y | How? | read · watch · ask |", "| 3 | Third | x |")
    assert "has 3 cells" in _raises(short)
    dup = ARC.replace("| 3 | Third", "| 2 | Third")
    assert "appears twice" in _raises(dup)


def test_every_real_arc_parses():
    from pathlib import Path
    for f in sorted((arcs.COURSES).glob("*/arc.md")):
        a = arcs.parse_arc(f.read_text(encoding="utf-8"), str(f))
        assert len(a.days) == 15, f


def test_normalize_title():
    assert arcs.normalize_title("Zoom In Until It’s Straight ") == "Zoom In Until It's Straight"
