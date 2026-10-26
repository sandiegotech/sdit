#!/usr/bin/env python3
"""degree_path.py — the Path: every day of the degree, in order.

    sequence()             -> [Step] for the whole degree, in walking order
    day_step(dir, n)       -> the Step for one course day
    next_on_path(dir, n)   -> the next spine Step after that day
    render_path_page()     -> writes curriculum/day-by-day.html

Order: Day 0 (Begin), then for each semester, each week, the week's days in
the semester's weekday rhythm (sync_courses.WEEKDAY_ORDER), then the
semester's gate. Day n of a course is in week n of its semester.

The spine is everything every learner takes. Depth studios (Years 3-4) are on
the Path too, labelled with their concentrations, but "Next on the Path" walks
the spine only: which studios a learner takes is their concentration's call,
and a stranger's studio is not their next day.

Titles come from the published day when it exists, else from the course arc.
Begin and the gates link only once their pages exist.
"""
from __future__ import annotations

import html
from dataclasses import dataclass
from pathlib import Path

import arcs
import publishing
from catalog import load_catalog, planned_days, day_info

ROOT = Path(__file__).resolve().parents[1]
COURSES = ROOT / "courses"
PATH_PAGE = ROOT / "curriculum" / "day-by-day.html"
BEGIN_PAGE = ROOT / "begin" / "index.html"


def gate_page(semester: int) -> Path:
    return ROOT / "gates" / f"semester-{semester}" / "index.html"


@dataclass
class Step:
    kind: str                 # "begin" | "day" | "gate"
    semester: int
    week: int
    label: str = ""           # Mon..Sat, or "Studio"
    course: dict | None = None
    n: int = 0
    title: str = ""
    published: bool = False
    href: str = ""
    publishes: object = None  # datetime.date or None
    studio: bool = False

    @property
    def key(self):
        return (self.course or {}).get("dir"), self.n


def _course_day_step(c: dict, semester: int, week: int, label: str) -> Step | None:
    n = week
    if n > planned_days(c):
        return None
    cdir = COURSES / c["dir"]
    info = day_info(cdir, n)
    arc = arcs.load_arc(cdir)
    arc_day = arc.day(n) if arc else None
    if info:
        title, published = info[0], True
    elif arc_day:
        title, published = arc_day.title, False
    else:
        title, published = f"Day {n:02d}", False
    studio = c.get("thread") == "depth"
    return Step(
        kind="day", semester=semester, week=week, label=label, course=c, n=n,
        title=title, published=published,
        href=f"/courses/{c['dir']}/day-{n:02d}.html",
        publishes=None if published else publishing.week_date(semester, week),
        studio=studio,
    )


_SEQ: list[Step] | None = None


def sequence(catalog: dict | None = None) -> list[Step]:
    global _SEQ
    use_cache = catalog is None
    if use_cache and _SEQ is not None:
        return _SEQ
    from sync_courses import semester_rows

    catalog = catalog or load_catalog()
    weeks = publishing.weeks_per_semester()
    steps: list[Step] = [Step(
        kind="begin", semester=1, week=0, title="Begin",
        published=BEGIN_PAGE.exists(), href="/begin/",
    )]
    for semester in range(1, 9):
        rows = semester_rows(catalog, semester)
        for week in range(1, weeks + 1):
            for label, item in rows:
                if not isinstance(item, dict):
                    continue
                step = _course_day_step(item, semester, week, label)
                if step:
                    steps.append(step)
        steps.append(Step(
            kind="gate", semester=semester, week=weeks, title=f"The Gate · Semester {semester}",
            published=gate_page(semester).exists(), href=f"/gates/semester-{semester}/",
            publishes=publishing.week_date(semester, weeks),
        ))
    if use_cache:
        _SEQ = steps
    return steps


def day_step(course_dir: str, n: int) -> Step | None:
    for s in sequence():
        if s.kind == "day" and s.key == (course_dir, n):
            return s
    return None


def next_on_path(course_dir: str, n: int) -> Step | None:
    """The next step every learner takes after this day: spine days and the
    gates (once the gate page exists); never another concentration's studio."""
    seq = sequence()
    for i, s in enumerate(seq):
        if s.kind == "day" and s.key == (course_dir, n):
            for t in seq[i + 1:]:
                if t.kind == "day" and not t.studio:
                    return t
                if t.kind == "gate" and t.published:
                    return t
            return None
    return None


# ── The Path page ────────────────────────────────────────────────────────────

MILESTONES = {
    2: "Year 1 ends with your work in a public exhibition.",
    4: "Year 2 ends with the Declaration: you choose Media, Design, or Engineering from two years of made work.",
    6: "The Field Term: a full term inside a working organization.",
    8: "The capstone, defended in public. You teach a first-year. Graduation.",
}


def _e(s) -> str:
    return html.escape(str(s), quote=True)


def _row(s: Step) -> str:
    c = s.course or {}
    code = c.get("code", "")
    if s.studio:
        concs = " · ".join(x.title() for x in c.get("concentrations", []))
        meta = f"Studio · {code}" + (f" · {concs}" if concs else "")
    else:
        meta = f"{s.label} · {code}" if s.label else code
    name = f'<span class="l-name">{_e(s.title)}</span><span class="l-meta">{_e(meta)}</span>'
    if s.published:
        return f'            <a href="{_e(s.href)}">{name}</a>'
    return f'            <span class="is-upcoming">{name}</span>'


def _special_row(s: Step, meta: str) -> str:
    name = f'<span class="l-name">{_e(s.title)}</span><span class="l-meta">{_e(meta)}</span>'
    if s.published:
        return f'            <a href="{_e(s.href)}">{name}</a>'
    return f'            <span class="is-upcoming">{name}</span>'


def render_path_page(catalog: dict | None = None) -> str:
    catalog = catalog or load_catalog()
    seq = sequence(catalog)
    weeks = publishing.weeks_per_semester()
    total_days = sum(1 for s in seq if s.kind == "day" and not s.studio)
    studio_days = sum(1 for s in seq if s.kind == "day" and s.studio)
    live_days = sum(1 for s in seq if s.kind == "day" and s.published)

    by_sem: dict[int, list[Step]] = {}
    for s in seq:
        by_sem.setdefault(s.semester, []).append(s)

    index_rows, sections = [], []
    for sem in range(1, 9):
        steps = by_sem.get(sem, [])
        days = [s for s in steps if s.kind == "day"]
        dates = [publishing.week_date(sem, w) for w in range(1, weeks + 1)]
        dated = [d for d in dates if d]
        label = publishing.semester_label(sem)
        if sem == 1:
            span = (f"Week 1 is live. Weeks 2–{weeks} publish on Mondays, "
                    f"{publishing.plain_date(dated[0])} to {publishing.plain_date(dated[-1])}")
        else:
            span = f"Publishes on Mondays, {publishing.plain_date(dated[0])} to {publishing.plain_date(dated[-1])}"
        index_rows.append(
            f'            <a href="#semester-{sem}"><span class="l-name">Semester {sem}</span>'
            f'<span class="l-meta">{_e(label)} · from {_e(publishing.short_date(dated[0]))} {dated[0].year}</span></a>'
        )

        parts = [f'          <p class="path-span">{_e(span)}.</p>']
        if sem >= 5:
            parts.append('          <p class="path-note">The spine is shared. Studios are listed every week; you take the ones your concentration prescribes, and one more for the Crossing.</p>')
        if sem == 8:
            parts.append('          <p class="path-note">The Crossing (one studio from outside your concentration) and the Open Studio elective run beside the spine this semester.</p>')
        if sem == 1:
            begin = steps[0]
            parts.append('          <nav class="ledger path-ledger" aria-label="Day 0">')
            parts.append(_special_row(begin, "Day 0 · before everything"))
            parts.append('          </nav>')
        for w in range(1, weeks + 1):
            wdays = [s for s in days if s.week == w]
            if not wdays:
                continue
            d = publishing.week_date(sem, w)
            when = "Live" if d is None else f"Publishes {publishing.long_date(d)}"
            parts.append(f'          <h3 class="path-week" id="s{sem}-w{w}">Week {w} <span>{_e(when)}</span></h3>')
            parts.append(f'          <nav class="ledger path-ledger" aria-label="Semester {sem}, Week {w}">')
            parts.extend(_row(s) for s in wdays)
            parts.append('          </nav>')
        gate = [s for s in steps if s.kind == "gate"][0]
        parts.append(f'          <h3 class="path-week">The Gate <span>End of Semester {sem}</span></h3>')
        parts.append(f'          <nav class="ledger path-ledger" aria-label="Gate, Semester {sem}">')
        parts.append(_special_row(gate, "Your answers again · what you made · what changed"))
        parts.append('          </nav>')
        if sem in MILESTONES:
            parts.append(f'          <p class="path-note">→ {_e(MILESTONES[sem])}</p>')

        n_spine = sum(1 for s in days if not s.studio)
        sections.append(f'''    <section class="article" id="semester-{sem}">
      <div class="frame article-grid">
        <div class="article-label">Semester {sem}<span class="num">{_e(label)}</span></div>
        <div class="article-body">
          <details class="path-weeks"{" open" if sem == 1 else ""}>
          <summary>{weeks} weeks · {n_spine} days{f" + studios" if any(s.studio for s in days) else ""}</summary>
{chr(10).join(parts)}
          </details>
        </div>
      </div>
    </section>''')

    first = publishing.week_date(1, 2)
    page = f'''<!doctype html>
<!-- Generated by scripts/degree_path.py from the registry, the arcs, and knowledge/calendar.yaml — do not edit by hand -->
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>The Path — SDIT</title>
  <meta name="description" content="Every day of the degree, in order, with the date each one publishes. You never have to decide what comes next.">
  <link rel="stylesheet" href="../assets/site.css" />
  <script src="../assets/js/site-paths.js" defer></script>
  <script src="../assets/js/includes.js" defer></script>
</head>
<body class="charter-page">
  <div data-include="/partials/header.html"></div>

  <main>

    <header class="page-header">
      <div class="frame">
        <span class="page-header__eyebrow">The Path</span>
        <h1 class="page-header__title">Every day of the degree, <em>in order.</em></h1>
        <p class="page-header__meta">8 semesters · {weeks * 8} weeks · {total_days} days on the shared spine · {studio_days} studio days · {live_days} live</p>
      </div>
    </header>

    <section class="article" id="how">
      <div class="frame article-grid">
        <div class="article-label">How It Works</div>
        <div class="article-body">
          <p>You do not have to decide what comes next. The Path is the whole degree laid out one day at a time: each week's days in the order you take them, Monday the books and Friday the Workshop, with the date each one publishes. Start at Day 0 and walk it. When a day is done, the end of the page points to the next one.</p>
          <p>One week of the Path publishes every Monday, starting {_e(publishing.long_date(first))}. Every course in a semester advances together, so nobody gets ahead of their week and nobody falls behind it. Each semester ends at a gate, where you answer the same questions again and see what changed.</p>
          <nav class="ledger" aria-label="Semesters" style="margin-top:1.25rem;">
{chr(10).join(index_rows)}
          </nav>
        </div>
      </div>
    </section>

{chr(10).join(sections)}

  </main>

  <div data-include="/partials/footer.html"></div>
  <script>
    // Opening a semester from the index should show its weeks.
    (function () {{
      function openTarget() {{
        var t = location.hash && document.getElementById(location.hash.slice(1));
        var d = t && t.querySelector ? t.querySelector("details.path-weeks") : null;
        if (!d && t && t.closest) d = t.closest("details.path-weeks");
        if (d) d.open = true;
      }}
      window.addEventListener("hashchange", openTarget);
      openTarget();
    }})();
  </script>
</body>
</html>
'''
    return page


def main() -> int:
    page = render_path_page()
    if not (PATH_PAGE.exists() and PATH_PAGE.read_text(encoding="utf-8") == page):
        PATH_PAGE.write_text(page, encoding="utf-8")
        print("degree_path: wrote curriculum/day-by-day.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
