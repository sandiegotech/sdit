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
syllabus:
  level: lower
  prerequisites: []
  corequisites: []
  method: [lecture]
  hours: {{instruction: 3, studio_or_lab: 0, independent: 9}}
  materials:
    - {{title: "A Book", author: "Someone", access: open, cost: 0}}
  assessment:
    - {{component: "Weekly answers", weight: 20}}
    - {{component: "Unassisted examination", weight: 20}}
    - {{component: "The made thing", weight: 60}}
  exam: "Week 13, tools closed."
  rubric: made-response
  core_competencies: {{critical-thinking: I}}
  outcome_levels: {{judgment: I}}
---

# X 101 — Thing

## Overview
## The Two Registers
## Learning Outcomes

1. Do the thing. → *Judgment* · *Critical thinking*
## The Made Thing
## How You're Assessed
## The Daily Path
"""

INDEX_SCAFFOLD = """---
id: x-101
title: "X 101 — Thing"
status: {status}
syllabus:
  level: lower
  prerequisites: []
  corequisites: []
  method: [lecture]
  hours: {{instruction: 3, studio_or_lab: 0, independent: 9}}
  materials:
    - {{title: "A Book", author: "Someone", access: open, cost: 0}}
  assessment:
    - {{component: "Weekly answers", weight: 20}}
    - {{component: "Unassisted examination", weight: 20}}
    - {{component: "The made thing", weight: 60}}
  exam: "Week 13, tools closed."
  rubric: made-response
  core_competencies: {{critical-thinking: I}}
  outcome_levels: {{judgment: I}}
---

# X 101 — Thing

## Learning Outcomes

1. Do the thing. → *Judgment* · *Critical thinking*
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
    """A minimal day held to the core rules only (standard: 1)."""
    asked = f"**{question}**" if bold else question
    return (f'---\nid: x\ntitle: "Day {n:02d} — T"\nday: {n}\ncourse: X 101 — Thing\nstandard: 1\nquestion: "{question}"\n---\n\n'
            f"# Day {n:02d} — T\n\ndek\n\n"
            f"## Carry the question\n\n{asked}\n\n" + ("<!-- sdit:answer -->\n\n" if marker else "")
            + f"That's it. **Day {n} is done.**\n")


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


def _run_with_syllabus(edit):
    """Run the validator on the minimal course after editing its index.md text."""
    c = _course()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write_course(root, c, 0)
        f = root / c["dir"] / "index.md"
        f.write_text(edit(f.read_text()))
        errors = []
        validate.validate_catalog(errors, _data(c), root)
    return errors


def test_syllabus_numbers_must_add_up():
    assert _run_with_syllabus(lambda t: t) == []
    e = _run_with_syllabus(lambda t: t.replace("independent: 9", "independent: 8"))
    assert any("weekly hours sum to 11" in x for x in e)
    e = _run_with_syllabus(lambda t: t.replace("weight: 60", "weight: 50"))
    assert any("sum to 90, not 100" in x for x in e)
    e = _run_with_syllabus(lambda t: t.replace("level: lower", "level: upper"))
    assert any("lower division" in x for x in e)


def test_syllabus_references_must_be_real():
    e = _run_with_syllabus(lambda t: t.replace("prerequisites: []", "prerequisites: [NOPE 999]"))
    assert any("not in the catalog" in x for x in e)
    e = _run_with_syllabus(lambda t: t.replace("rubric: made-response", "rubric: vibes"))
    assert any("not in knowledge/rubrics.yaml" in x for x in e)
    e = _run_with_syllabus(lambda t: t.replace("access: open, cost: 0", "access: open, cost: 40"))
    assert any("is open but costs 40" in x for x in e)


def test_syllabus_claims_must_be_on_the_page():
    e = _run_with_syllabus(lambda t: t.replace(" · *Critical thinking*", ""))
    assert any("no learning outcome names it" in x for x in e)
    e = _run_with_syllabus(lambda t: t.replace("Unassisted examination", "Quiz"))
    assert any("no unassisted examination component" in x for x in e)
    e = _run_with_syllabus(lambda t: t.replace("outcome_levels: {judgment: I}", "outcome_levels: {breadth: I}"))
    assert any("outcome_levels covers" in x for x in e)
    e = _run_with_syllabus(lambda t: t.replace("syllabus:", "notsyllabus:"))
    assert any("no `syllabus:` block" in x for x in e)


def test_day_media_must_not_track_the_reader():
    c = _course(status="day1")
    bad = [
        ('<iframe src="https://www.youtube.com/embed/x"></iframe>', "outside www.youtube-nocookie.com"),
        ('<img src="https://example.com/a.jpg" alt="a" loading="lazy" referrerpolicy="no-referrer" />', "outside upload.wikimedia.org"),
        ('<img src="https://upload.wikimedia.org/a.jpg" alt="a" loading="lazy" />', "without referrerpolicy"),
    ]
    for html_tag, expect in bad:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_course(root, c, 1)
            f = root / c["dir"] / "day-01.md"
            f.write_text(_day(1) + "\n" + html_tag + "\n")
            errors = []
            validate.validate_catalog(errors, _data(c), root)
        assert any(expect in e for e in errors), (expect, errors)


# ── Day standard v2 ──────────────────────────────────────────────────────────

FILLER = " ".join(["The wave stands up when it feels the bottom, and the face steepens."] * 22)

V2 = """---
id: x101-day-02
title: "Day 02 — T"
day: 2
course: X 101 — Thing
question: "Why?"
---

# Day 02 — T

Ten minutes. One picture, one idea, one question.

---

## Look

<figure class="day-figure">
  <img src="https://upload.wikimedia.org/a.jpg" alt="A wave" loading="lazy" referrerpolicy="no-referrer" />
  <figcaption><strong>A wave.</strong> Someone, 1900.</figcaption>
</figure>

Why it matters.

---

## One idea

""" + FILLER + """

---

## Carry the question

For the rest of today, carry this one:

**Why?**

Answer in a line or a page, or not at all. What you write is kept in your Notebook.

<!-- sdit:answer -->

That's it. **Day 2 is done.**

---

## If you're still curious

Three doors. Open one, or none.

**Read the real thing.** A book.

**Watch the other half.** A film.

**Ask someone.** Tonight, ask someone you trust a question.
"""


def _v2_errors(text):
    import frontmatter
    meta, body = frontmatter.parse(text)
    return validate.validate_day_text(meta, body, 2, "X-101")


def test_a_complete_v2_day_passes():
    assert _v2_errors(V2) == []


def test_v2_rules_each_catch_their_fault():
    cases = [
        (V2.replace("## One idea", "## Another idea"), "no '## One idea'"),
        (V2.replace("## One idea", "## Watch"), "2 experience sections"),
        (V2.replace("<figure", "<div").replace("</figure>", "</div>"), "does not put the thing on the page"),
        (V2.replace("**Ask someone.** Tonight", "Tonight"), "has 2 doors"),
        (V2.replace("**Ask someone.**", "**Ring someone.**"), "third door is not"),
        (V2.replace(FILLER, "Too short."), "main path is"),
        (V2.replace("The wave stands up", "The amazing wave stands up", 1), "words the voice does not"),
        (V2.replace("# Day 02 — T", "# Day 02 — Other"), "H1 does not equal"),
        (V2.replace("**Day 2 is done.**", "Done."), "no done line"),
        (V2.replace("## If you're still curious", "## More\n\n## If you're still curious"), "outside the standard"),
    ]
    for text, expect in cases:
        errs = _v2_errors(text)
        assert any(expect in e for e in errs), (expect, errs)


def test_a_fresh_scaffold_cannot_publish():
    import scaffold_day
    text = scaffold_day.TEMPLATE.format(id="x", nn="02", n=2, course="X 101", title="T",
                                        question="Why?", thing="", idea="", doors="")
    errs = _v2_errors(text)
    assert any("scaffold placeholder" in e for e in errs), errs
