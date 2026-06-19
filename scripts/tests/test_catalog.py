import tempfile
from pathlib import Path

import catalog


def test_default_days():
    assert catalog.planned_days({}) == catalog.DEFAULT_DAYS == 15


def test_override_days():
    assert catalog.planned_days({"days_planned": 8}) == 8


def test_bad_days_falls_back():
    assert catalog.planned_days({"days_planned": "oops"}) == catalog.DEFAULT_DAYS


def test_published_days_discovers():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d)
        (p / "day-01.md").write_text("x")
        (p / "day-03.md").write_text("x")
        (p / "index.md").write_text("x")
        assert catalog.published_days(p) == [1, 3]


def test_day_info_title_and_dek():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d)
        (p / "day-02.md").write_text('---\ntitle: "Day 02 — The Title"\n---\n\nFirst line is the dek.\n')
        title, dek = catalog.day_info(p, 2)
        assert title == "The Title"
        assert dek == "First line is the dek."


def test_day_info_missing():
    with tempfile.TemporaryDirectory() as d:
        assert catalog.day_info(Path(d), 9) is None
