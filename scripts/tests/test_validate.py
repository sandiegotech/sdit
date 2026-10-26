import tempfile
from pathlib import Path

import validate


def test_real_catalog_passes():
    # The committed catalog must always satisfy the validator (regression guard).
    assert validate.main() == 0


# ── Fixtures for the per-course rules ────────────────────────────────────────

INDEX_LIVE = """---
id: x-101
title: "X 101 — Thing"
status: {status}
---

# X 101 — Thing

## Overview
## The Two Registers
## Learning Outcomes
## The Made Thing
## How You're Assessed
## The Daily Path
"""

INDEX_SCAFFOLD = """---
id: x-101
title: "X 101 — Thing"
status: {status}
---

# X 101 — Thing

## The Two Registers
## The Daily Path
"""


def _course(**over):
    c = {
        "code": "X 101", "dir": "X-101", "name": "Thing", "units": 4,
        "thread": "canon", "semester": 1, "status": "syllabus", "days_planned": 3,
        "outcomes": ["judgment"], "catalog_register": "r", "teaching_frame": "t",
        "artifact": "a",
    }
    c.update(over)
    return c


def _data(course):
    return {"threads": [{"id": "canon"}, {"id": "depth"}], "courses": [course]}


def _day(n: int, question: str = "Why?", marker: bool = True, bold: bool = True) -> str:
    asked = f"**{question}**" if bold else question
    return (f'---\nid: x\ntitle: "Day {n:02d} — T"\nday: {n}\nquestion: "{question}"\n---\n\n# T\n\ndek\n\n'
            f"## Carry the question\n\n{asked}\n\n" + ("<!-- sdit:answer -->\n" if marker else ""))


def _arc(n_days: int) -> str:
    rows = "\n".join(f"| {n} | T | thing | idea | question? | read · watch · ask |" for n in range(1, n_days + 1))
    return ("---\ncourse: X 101 — Thing\nsemester: 1\ndays: %d\n---\n\n# Arc\n\n"
            "## The fifteen days\n\n| Day | Title | Thing | Idea | Question | Doors |\n|---|---|---|---|---|---|\n%s\n" % (n_days, rows))


def _write_course(root: Path, course: dict, days: int, index_tpl=INDEX_SCAFFOLD, skip=()):
    d = root / course["dir"]
    d.mkdir(parents=True)
    (d / "index.md").write_text(index_tpl.format(status=course["status"]))
    (d / "arc.md").write_text(_arc(course.get("days_planned") or 3))
    for n in range(1, days + 1):
        if n in skip:
            continue
        (d / f"day-{n:02d}.md").write_text(_day(n))


def _run(course, days=0, index_tpl=INDEX_SCAFFOLD, skip=()):
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write_course(root, course, days, index_tpl, skip)
        errors = []
        validate.validate_catalog(errors, _data(course), root)
        return errors


def test_minimal_valid_course_passes():
    assert _run(_course()) == []


def test_days_planned_is_required():
    c = _course(); del c["days_planned"]
    assert any("days_planned" in e for e in _run(c))


def test_unknown_outcome_and_status_fail():
    errs = _run(_course(outcomes=["vibes"], status="shipped"))
    assert any("unknown outcome" in e for e in errs)
    assert any("unknown status" in e for e in errs)


def test_syllabus_with_day_files_fails():
    errs = _run(_course(status="syllabus"), days=1)
    assert any("published day file" in e for e in errs)


def test_day1_needs_a_day():
    assert any("no day-NN.md" in e for e in _run(_course(status="day1")))
    assert _run(_course(status="day1"), days=1) == []


def test_gap_in_days_fails():
    errs = _run(_course(status="day1"), days=3, skip=(2,))
    assert any("gap" in e for e in errs)


def test_more_days_than_planned_fails():
    errs = _run(_course(status="day1", days_planned=2), days=3)
    assert any("plans only 2 days" in e for e in errs)


def test_live_requires_every_day_and_catalog_grade_index():
    short = _run(_course(status="live"), days=2, index_tpl=INDEX_LIVE)
    assert any("only 2 of 3 days" in e for e in short)
    scaffold = _run(_course(status="live"), days=3, index_tpl=INDEX_SCAFFOLD)
    assert any("lacks ## Overview" in e for e in scaffold)
    assert _run(_course(status="live"), days=3, index_tpl=INDEX_LIVE) == []


def test_front_matter_status_must_mirror_registry():
    c = _course(status="day1")
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write_course(root, _course(status="syllabus"), 1)  # index says syllabus
        errors = []
        validate.validate_catalog(errors, _data(c), root)
    assert any("front matter says `status: syllabus`" in e for e in errors)


def test_depth_studio_needs_concentrations():
    errs = _run(_course(thread="depth"))
    assert any("names no concentrations" in e for e in errs)


def test_unregistered_course_directory_fails():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        c = _course()
        _write_course(root, c, 0)
        (root / "STRAY-999").mkdir()
        errors = []
        validate.validate_catalog(errors, _data(c), root)
    assert any("STRAY-999" in e for e in errors)


def test_arc_is_required_and_must_match_days_planned():
    c = _course()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write_course(root, c, 0)
        (root / c["dir"] / "arc.md").unlink()
        errors = []
        validate.validate_catalog(errors, _data(c), root)
    assert any("has no arc.md" in e for e in errors)
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write_course(root, c, 0)
        (root / c["dir"] / "arc.md").write_text(_arc(2))
        errors = []
        validate.validate_catalog(errors, _data(c), root)
    assert any("plans 2 days" in e for e in errors)


def test_published_title_must_match_arc():
    c = _course(status="day1")
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write_course(root, c, 1)
        (root / c["dir"] / "day-01.md").write_text(_day(1).replace("Day 01 — T", "Day 01 — Other"))
        errors = []
        validate.validate_catalog(errors, _data(c), root)
    assert any("but the arc calls it" in e for e in errors)


def test_calendar_rules():
    errors = []
    validate.validate_calendar(errors, {"publishing": {"first_release": "2027-01-05"},
                                        "semesters": [{"n": i, "weeks": 15} for i in range(1, 9)]})
    assert any("not a Monday" in e for e in errors)
    errors = []
    validate.validate_calendar(errors, {"publishing": {"first_release": "2027-01-04"},
                                        "semesters": [{"n": i, "weeks": 15} for i in range(1, 8)]})
    assert any("1 to 8" in e for e in errors)


def test_day_must_ask_its_question_and_keep_the_answer():
    c = _course(status="day1")
    for text, expect in ((_day(1, marker=False), "has no answer field"),
                         (_day(1, bold=False), "does not ask its front-matter question"),
                         (_day(1).replace('question: "Why?"\n', ""), "has no `question`")):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_course(root, c, 1)
            (root / c["dir"] / "day-01.md").write_text(text)
            errors = []
            validate.validate_catalog(errors, _data(c), root)
        assert any(expect in e for e in errors), (expect, errors)
