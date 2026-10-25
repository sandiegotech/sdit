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


def _write_course(root: Path, course: dict, days: int, index_tpl=INDEX_SCAFFOLD, skip=()):
    d = root / course["dir"]
    d.mkdir(parents=True)
    (d / "index.md").write_text(index_tpl.format(status=course["status"]))
    for n in range(1, days + 1):
        if n in skip:
            continue
        (d / f"day-{n:02d}.md").write_text(f'---\nid: x\ntitle: "Day {n:02d} — T"\nday: {n}\n---\n\n# T\n\ndek\n')


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
