#!/usr/bin/env python3
"""review_grade.py — the course pages and degree pages an accreditation
reviewer reads (PLAN.md section 13).

Every number a reviewer could check is generated from data, never typed into
prose: the course's `syllabus:` front-matter block and knowledge/catalog.yaml.

    sync_course_sections(index_md_text, course, block) -> new text
        Ensures, between markers, on each course page:
          ## Course Information   (units and hours, level, prerequisites,
                                   method, materials, instructor standard,
                                   rubric, competencies, the unassisted exam)
          the weights table at the end of "How You're Assessed"
          ## Policies             (links to the academic policies)
          the Daily Path's opening sentence

    write_pages(write, out)
        curriculum/map.html, breadth.html, requirements.html,
        policies.html, assessment.html, rubrics.html
"""
from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

OUTCOMES = [
    ("judgment", "Judgment"),
    ("intelligence", "Command of Intelligence"),
    ("craft", "Workmanship"),
    ("articulation", "Articulation"),
    ("breadth", "Breadth of Mind"),
]
COMPETENCIES = [
    ("written-communication", "Written communication"),
    ("oral-communication", "Oral communication"),
    ("quantitative-reasoning", "Quantitative reasoning"),
    ("information-literacy", "Information literacy"),
    ("critical-thinking", "Critical thinking"),
]
LEVEL_WORD = {"I": "introduced", "D": "developed", "M": "mastered"}
METHOD_WORD = {"seminar": "Seminar", "lecture": "Lecture", "laboratory": "Laboratory",
               "studio": "Studio", "placement": "Field placement", "independent": "Independent work"}
ACCESS_WORD = {"open": "open, free", "library": "public library, free",
               "purchase": "purchase", "provided": "provided in the room"}
INSTRUCTOR = ("A practitioner-scholar with a body of work in the field: a terminal degree, or equivalent "
              "professional standing documented under the Institute's rubric (The Degree, section 9).")

INFO = ("<!-- sdit:info:begin -->", "<!-- sdit:info:end -->")
WEIGHTS = ("<!-- sdit:weights:begin -->", "<!-- sdit:weights:end -->")
POLICIES = ("<!-- sdit:policies:begin -->", "<!-- sdit:policies:end -->")
DAYS_LEAD = ("The fifteen days below are the open spine of the course, about ten minutes each. "
             "The hours in Course Information are the course.")


def _load_rubrics() -> dict:
    import yaml
    data = yaml.safe_load((ROOT / "knowledge" / "rubrics.yaml").read_text(encoding="utf-8"))
    return {r["id"]: r for r in data["rubrics"]}


def code_to_dir(code: str) -> str:
    return code.replace(" ", "-")


def _course_link(code: str) -> str:
    return f"[{code}](/courses/{code_to_dir(code)}/index.html)"


def _replace_between(text: str, markers: tuple[str, str], body: str) -> str:
    begin, end = markers
    block = f"{begin}\n{body.rstrip()}\n{end}"
    if begin in text and end in text:
        return re.sub(re.escape(begin) + r".*?" + re.escape(end), lambda _m: block, text, flags=re.S)
    return text


def _section_bounds(text: str, heading: str) -> tuple[int, int] | None:
    """Start and end offsets of a `## heading` section (end = next `## ` or closing rule)."""
    m = re.search(rf"^## {re.escape(heading)}\s*$", text, flags=re.M)
    if not m:
        return None
    nxt = re.search(r"^## |\n---\n\n\*Every course", text[m.end():], flags=re.M)
    end = m.end() + nxt.start() if nxt else len(text)
    return m.start(), end


def course_information(course: dict, block: dict) -> str:
    from publishing import semester_label

    rub = _load_rubrics().get(block.get("rubric", ""), {})
    h = block.get("hours", {})
    units = course.get("units")
    total = units * 3 * 15 if isinstance(units, int) else None
    level = {"lower": "Lower division", "upper": "Upper division"}.get(block.get("level"), "")
    prereq = ", ".join(_course_link(c) for c in block.get("prerequisites") or []) or "None"
    coreq = ", ".join(_course_link(c) for c in block.get("corequisites") or []) or "None"
    method = ", ".join(METHOD_WORD.get(m, m) for m in block.get("method") or [])
    cc = " · ".join(f"{name} ({LEVEL_WORD.get(block['core_competencies'][cid], '')})"
                    for cid, name in COMPETENCIES if cid in (block.get("core_competencies") or {}))
    rows = [
        ("Catalog number", f"{course['code']} — {course['name']}"),
        ("Units", f"{units} semester units · {total} hours of work over 15 weeks"),
        ("Each week", f"{h.get('instruction', 0)} h instruction · {h.get('studio_or_lab', 0)} h studio or laboratory · "
                      f"{h.get('independent', 0)} h independent work"),
        ("Level", level),
        ("Offered", f"Semester {course.get('semester')} · {semester_label(course.get('semester'))}"),
        ("Prerequisites", prereq),
        ("Corequisites", coreq),
        ("Instructional method", method),
        ("Instructor", INSTRUCTOR),
        ("Rubric", f"[{rub.get('name', block.get('rubric', ''))}](/curriculum/rubrics.html#{block.get('rubric', '')})"),
        ("Core competencies", cc or "None assessed in this course"),
        ("Unassisted examination", " ".join(str(block.get("exam", "")).split())),
    ]
    out = ["| | |", "|---|---|"]
    out += [f"| {k} | {str(v).replace('|', '/')} |" for k, v in rows]
    mats = block.get("materials") or []
    out += ["", "**Required materials**", ""]
    cost = 0
    for m in mats:
        bits = [f"*{m.get('title', '')}*"]
        if m.get("author"):
            bits.append(str(m["author"]))
        line = ", ".join(bits)
        if m.get("edition"):
            line += f" — {m['edition']}"
        access = ACCESS_WORD.get(m.get("access"), m.get("access", ""))
        price = m.get("cost") or 0
        cost += price if isinstance(price, (int, float)) else 0
        tail = access if not price else f"{access}, about ${price}"
        if m.get("note"):
            note = str(m["note"]).strip().rstrip(".")
            if len(note) > 1 and note[0].isupper() and note[1].islower():
                note = note[0].lower() + note[1:]
            tail += f"; {note}"
        out.append(f"- {line} · {tail}")
    out += ["", ("Required materials cost: nothing. Every item is open, borrowable from a public library, "
                 "or provided in the room." if cost == 0 else
                 f"Required materials cost: about ${int(cost)} if bought; everything else is open, "
                 f"borrowable from a public library, or provided in the room.")]
    return "\n".join(out)


def weights_table(block: dict) -> str:
    rows = block.get("assessment") or []
    out = ["", "| Component | Weight |", "|---|---|"]
    out += [f"| {r.get('component', '')} | {r.get('weight', 0)}% |" for r in rows]
    out.append(f"| **Total** | **{sum(int(r.get('weight', 0)) for r in rows)}%** |")
    out += ["", "Grades follow the scale in the [academic policies](/curriculum/policies.html#grading)."]
    return "\n".join(out)


POLICY_LINES = """- **Attendance and participation.** See [attendance](/curriculum/policies.html#attendance).
- **AI use.** Tools are open in every course, and the human is examined unaided. See [the AI policy](/curriculum/policies.html#ai).
- **Academic integrity.** See [academic integrity](/curriculum/policies.html#integrity).
- **Accommodations.** See [accommodations](/curriculum/policies.html#accommodations).
- **Late work.** See [late work](/curriculum/policies.html#late-work)."""


def sync_course_sections(text: str, course: dict, block: dict | None) -> str:
    """Insert or refresh the generated sections on one course page."""
    if not block:
        return text

    # Course Information, after The Two Registers.
    if INFO[0] not in text:
        b = _section_bounds(text, "The Two Registers")
        if b:
            insert = f"## Course Information\n\n{INFO[0]}\n{INFO[1]}\n\n"
            text = text[:b[1]].rstrip("\n") + "\n\n" + insert + text[b[1]:].lstrip("\n")
    text = _replace_between(text, INFO, course_information(course, block))

    # The weights table, at the end of How You're Assessed.
    if WEIGHTS[0] not in text:
        b = _section_bounds(text, "How You're Assessed")
        if b:
            insert = f"\n\n{WEIGHTS[0]}\n{WEIGHTS[1]}\n\n"
            text = text[:b[1]].rstrip("\n") + insert + text[b[1]:].lstrip("\n")
    text = _replace_between(text, WEIGHTS, weights_table(block))

    # Policies, before the closing rule.
    if POLICIES[0] not in text:
        closing = text.rfind("\n---\n")
        insert = f"\n## Policies\n\n{POLICIES[0]}\n{POLICIES[1]}\n"
        text = (text[:closing] + "\n" + insert + text[closing:]) if closing != -1 else text + insert
    text = _replace_between(text, POLICIES, POLICY_LINES)
    return text


# ── Degree-level pages ──────────────────────────────────────────────────────

def _e(s) -> str:
    return html.escape(str(s), quote=True)


def _shell(title: str, eyebrow: str, h1: str, meta: str, description: str, body: str) -> str:
    return f'''<!doctype html>
<!-- Generated by scripts/review_grade.py from the registry and the course syllabus blocks — do not edit by hand -->
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{_e(title)} — SDIT</title>
  <meta name="description" content="{_e(description)}">
  <link rel="stylesheet" href="../assets/site.css" />
  <script src="../assets/js/site-paths.js" defer></script>
  <script src="../assets/js/includes.js" defer></script>
</head>
<body class="charter-page evidence-page">
  <div data-include="/partials/header.html"></div>
  <main>
    <header class="page-header">
      <div class="frame">
        <span class="page-header__eyebrow">{_e(eyebrow)}</span>
        <h1 class="page-header__title">{h1}</h1>
        <p class="page-header__meta">{_e(meta)}</p>
      </div>
    </header>
{body}
    <section class="article">
      <div class="frame article-grid">
        <div class="article-label">Status</div>
        <div class="article-body">
          <p>A working framework, not an authorized degree. SDIT is in its founding phase and is not yet authorized to grant degrees; <a href="/accreditation.html">where authorization stands</a> is published in full. The curriculum is open and free to take.</p>
          <p><a href="/curriculum/map.html">Curriculum map</a> · <a href="/curriculum/breadth.html">General education</a> · <a href="/curriculum/requirements.html">Requirements</a> · <a href="/curriculum/policies.html">Academic policies</a> · <a href="/curriculum/assessment.html">Assessment plan</a> · <a href="/curriculum/rubrics.html">Rubrics</a> · <a href="/curriculum/fundamentals.html">Studio fundamentals</a></p>
        </div>
      </div>
    </section>
  </main>
  <div data-include="/partials/footer.html"></div>
</body>
</html>
'''


def _section(label: str, num: str, inner: str, sid: str = "") -> str:
    idattr = f' id="{_e(sid)}"' if sid else ""
    return f'''    <section class="article"{idattr}>
      <div class="frame article-grid">
        <div class="article-label">{_e(label)}<span class="num">{_e(num)}</span></div>
        <div class="article-body">
{inner}
        </div>
      </div>
    </section>
'''


def load_blocks() -> list[tuple[dict, dict]]:
    """(registry course, syllabus block or {}) for every course, in semester order."""
    import frontmatter
    from catalog import load_catalog
    rows = []
    for c in sorted(load_catalog()["courses"], key=lambda c: (c.get("semester", 9), c["code"])):
        f = ROOT / "courses" / c["dir"] / "index.md"
        meta, _ = frontmatter.parse(f.read_text(encoding="utf-8")) if f.exists() else ({}, "")
        rows.append((c, (meta or {}).get("syllabus") or {}))
    return rows


def unit_counts(rows) -> dict:
    spine = [c for c, _ in rows if c.get("thread") != "depth"]
    spine_units = sum(c["units"] for c in spine)
    depth_units = 4 * 4
    crossing = 4
    open_studio = 4
    upper_spine = sum(c["units"] for c in spine if int(c["code"].split()[1][0]) >= 3)
    return {
        "spine": spine_units, "depth": depth_units, "crossing": crossing, "open_studio": open_studio,
        "total": spine_units + depth_units + crossing + open_studio,
        "upper": upper_spine + depth_units + crossing + open_studio,
        "lower": spine_units - upper_spine,
    }


def page_map(rows) -> str:
    head = "".join(f"<th>{_e(n)}</th>" for _, n in OUTCOMES) + "".join(f"<th>{_e(n)}</th>" for _, n in COMPETENCIES)
    body = []
    for c, b in rows:
        ol, cc = b.get("outcome_levels") or {}, b.get("core_competencies") or {}
        cells = "".join(f"<td>{_e(ol.get(k, ''))}</td>" for k, _ in OUTCOMES)
        cells += "".join(f"<td>{_e(cc.get(k, ''))}</td>" for k, _ in COMPETENCIES)
        body.append(f'<tr><th><a href="/courses/{_e(c["dir"])}/index.html">{_e(c["code"])}</a> '
                    f'<span>{_e(c.get("display") or c["name"])}</span></th><td>{_e(c.get("semester"))}</td>{cells}</tr>')
    table = (f'<div class="evidence-table-wrap"><table class="evidence-table">'
             f'<thead><tr><th>Course</th><th>Sem.</th>{head}</tr></thead><tbody>{"".join(body)}</tbody></table></div>')
    inner = ('          <p>Each course against the five institutional outcomes and the five WSCUC Core Competencies. '
             '<strong>I</strong> introduced, <strong>D</strong> developed, <strong>M</strong> mastered. '
             'Generated from each course\'s syllabus block.</p>\n          ' + table)
    return _shell("Curriculum Map", "For Reviewers", "The curriculum <em>map</em>.",
                  "44 courses · 5 institutional outcomes · 5 core competencies",
                  "Every course against the five institutional outcomes and the five WSCUC Core Competencies, introduced, developed, or mastered.",
                  _section("The Map", "WSCUC Standard 2", inner))


BREADTH = [
    ("Written communication", ["RHET 110"], "Line-edited writing every week in RHET 110, and written answers and essays in every Canon course."),
    ("Oral communication", [], "No standalone course. Every made thing is defended out loud, in seminar or at exhibition, from the first semester; CAP 402's public defense is the graduation-level assessment."),
    ("Quantitative reasoning", ["MATH 110", "MATH 120", "MATH 210", "MATH 220"], "Calculus, linear algebra, and probability and statistics, each taught physical before formal."),
    ("Natural science with laboratory", ["PHYS 110", "PHYS 120"], "Mechanics and waves, with laboratory work on the sand, in the water, and at the bench."),
    ("Arts and humanities", ["HUM 101", "HUM 102", "HUM 201", "HUM 202", "HUM 301", "HUM 302", "HUM 401", "HUM 402"], "The Canon, every semester: text, film, and album as one conversation."),
    ("Social and behavioral sciences", ["HUM 201", "RHET 210", "SIG 301"], "Political and economic philosophy, epistemics and propaganda, and the sociology of scenes. Thin by conventional standards; stated here rather than stretched."),
    ("Computation", ["CS 110", "CS 120", "CS 210", "CS 220"], "Programming, machine organization, algorithms, and machine learning."),
]


def page_breadth(rows) -> str:
    units = {c["code"]: c["units"] for c, _ in rows}
    out, total = [], 0
    for area, codes, note in BREADTH:
        u = sum(units.get(c, 0) for c in codes)
        listed = ", ".join(f'<a href="/courses/{code_to_dir(c)}/index.html">{_e(c)}</a>' for c in codes) or "—"
        out.append(f"<tr><th>{_e(area)}</th><td>{listed}</td><td>{u}</td><td>{_e(note)}</td></tr>")
    inner = ('          <p>The Foundation set against the breadth areas general education is conventionally measured by. '
             'A course can serve more than one area; units are counted once per area, so the column does not sum to the degree.</p>\n'
             '          <div class="evidence-table-wrap"><table class="evidence-table"><thead><tr><th>Area</th><th>Courses</th><th>Units</th><th>How</th></tr></thead>'
             f'<tbody>{"".join(out)}</tbody></table></div>')
    return _shell("General Education", "For Reviewers", "General <em>education</em>.",
                  "the Foundation against the conventional breadth areas",
                  "How the shared Foundation covers the conventional general-education breadth areas, with units per area and where it is thin.",
                  _section("Breadth", "Units by area", inner))


def page_requirements(rows) -> str:
    u = unit_counts(rows)
    t = [("Shared spine (every student)", u["spine"]), ("Four depth studios in the concentration", u["depth"]),
         ("The Crossing: one studio outside the concentration", u["crossing"]),
         ("Open Studio elective", u["open_studio"]), ("Total", u["total"])]
    table = "".join(f"<tr><th>{_e(k)}</th><td>{v}</td></tr>" for k, v in t)
    facts = [
        f"Lower division: {u['lower']} units. Upper division: {u['upper']} units (the minimum is 40).",
        "Concentration declared at the end of Year 2 (the Declaration): Media, Design, or Engineering.",
        "Field Term (FLD 301), one placed term in Year 3, 4 units.",
        "Capstone (CAP 401–402), a defended original work in Year 4, 4 units across two semesters.",
        "Physical Culture: graduation-required, non-credit.",
        "Teaching requirement: every fourth-year leads first-years in the Workshop, a Canon section, or Physical Culture. Graduation-required, non-credit.",
        "Annual gates: a portfolio review and written and oral examination against the five outcomes at the end of each year.",
        "Residency and transfer: the Foundation is taken here; no transfer credit is accepted into it.",
    ]
    inner = ('          <p>Computed from the registry. If these numbers and the prose ever disagree, the numbers are right.</p>\n'
             f'          <div class="evidence-table-wrap"><table class="evidence-table"><tbody>{table}</tbody></table></div>\n'
             '          <ul>' + "".join(f"<li>{_e(f)}</li>" for f in facts) + "</ul>")
    return _shell("Requirements", "For Reviewers", "Degree <em>requirements</em>.",
                  f"Bachelor of Arts in Technology · {u['total']} semester units · 8 semesters",
                  "The 120 units of the BA in Technology, computed from the registry: spine, concentration, Crossing, elective, upper division, and graduation requirements.",
                  _section("The Units", f"{u['total']} total", inner))


POLICIES_HTML = [
    ("credit-hour", "The Credit Hour", """<p>One semester unit is about 45 hours of a student's work over a 15-week term: one hour of instruction and two of preparation each week, or the equivalent in laboratory, studio, or placement hours. Every course page states its hours by week. The fifteen ten-minute days published for each course are its open spine, not the course; the rest of the hours are the reading behind the doors, the seminar or laboratory, the making, and the writing.</p>"""),
    ("grading", "Grading", """<p>Letter grades A, B, C, D, and F, with plus and minus from A− to D−, on a 4.0 scale (A 4.0, A− 3.7, B+ 3.3, B 3.0, B− 2.7, C+ 2.3, C 2.0, C− 1.7, D+ 1.3, D 1.0, D− 0.7, F 0). Each course page lists its graded components and their weights. Transcripts require grades; the portfolio is the primary artifact, and it is what the annual gate reads.</p>"""),
    ("attendance", "Attendance and Participation", """<p>Seminars, laboratories, and studios meet in person; attendance is expected and counts where a course weights participation. A learner taking the open curriculum alone has no attendance requirement and earns no credit until the Institute is authorized to award it.</p>"""),
    ("ai", "AI Use", """<p>AI-native, not AI-dependent. Tools are open in every course and studied as a medium: what was delegated, how it was checked, and why the judgment calls were the student's. And every course examines the human unaided, in writing, mathematics, or code, because the Institute certifies the human and must observe the human without the tools.</p>"""),
    ("unassisted", "Unassisted Examinations", """<p>Every course names its unassisted examination on its page: when, how long, and what. They are sat with every tool closed and graded against the <a href="/curriculum/rubrics.html#unassisted-examination">unassisted examination rubric</a>.</p>"""),
    ("integrity", "Academic Integrity", """<p>Work submitted as a student's own is their own; sources are named, and machine assistance is disclosed in the account the course asks for. Presenting another's work, or a machine's, as unassisted work is a violation. A first violation is addressed by the instructor and recorded; a second goes to the academic standards committee.</p>"""),
    ("accommodations", "Accommodations", """<p>Students with a documented disability receive reasonable accommodations in every course, including the unassisted examinations, arranged before the term begins. The open curriculum is readable without an account, and its pages are built to work with assistive technology.</p>"""),
    ("late-work", "Late Work", """<p>Made things have defense and exhibition dates set at the start of the term; they move only by agreement before the date. Weekly written work may be submitted up to a week late for reduced credit, as the course states.</p>"""),
    ("gates", "The Annual Gate", """<p>At the end of each year, a portfolio review and a written and oral examination against the five outcomes. A student who does not pass a gate repeats the work the gate names before continuing.</p>"""),
    ("progress", "Satisfactory Academic Progress", """<p>Good standing requires a cumulative grade point average of 2.0, passing each annual gate, and completing the Foundation's courses in sequence. A student below the line is placed on notice for one term with a plan; a second term below it ends enrollment, with the right to appeal.</p>"""),
]


def page_policies() -> str:
    body = "".join(_section(t, "", f"          {p}", sid) for sid, t, p in POLICIES_HTML)
    return _shell("Academic Policies", "For Reviewers", "Academic <em>policies</em>.",
                  "written once, honest about being a working framework",
                  "The credit hour, grading, attendance, the AI policy, unassisted examinations, integrity, accommodations, late work, the annual gate, and academic progress.",
                  body)


def page_assessment(rows) -> str:
    rub = _load_rubrics()
    parts = []
    for key, name in OUTCOMES:
        where = [(c, b) for c, b in rows if (b.get("outcome_levels") or {}).get(key)]
        m = [c["code"] for c, b in where if b["outcome_levels"][key] == "M"]
        parts.append(f"<tr><th>{_e(name)}</th><td>{len(where)} courses</td><td>{_e(', '.join(m) or '—')}</td></tr>")
    oc = "".join(parts)
    parts = []
    for key, name in COMPETENCIES:
        where = [(c, b) for c, b in rows if (b.get("core_competencies") or {}).get(key)]
        m = [c["code"] for c, b in where if b["core_competencies"][key] == "M"]
        parts.append(f"<tr><th>{_e(name)}</th><td>{len(where)} courses</td><td>{_e(', '.join(m) or '—')}</td></tr>")
    cc = "".join(parts)
    rubs = "".join(f'<li><a href="/curriculum/rubrics.html#{_e(r["id"])}">{_e(r["name"])}</a></li>' for r in rub.values())
    inner1 = ('          <p>Each institutional outcome and each Core Competency, the number of courses that assess it, and where it is assessed at graduation level.</p>\n'
              '          <div class="evidence-table-wrap"><table class="evidence-table"><thead><tr><th>Institutional outcome</th><th>Assessed in</th><th>Mastery assessed in</th></tr></thead>'
              f'<tbody>{oc}</tbody></table></div>\n'
              '          <div class="evidence-table-wrap"><table class="evidence-table"><thead><tr><th>Core competency</th><th>Assessed in</th><th>Mastery assessed in</th></tr></thead>'
              f'<tbody>{cc}</tbody></table></div>')
    inner2 = ('          <p>Every made thing is judged against a published rubric, and every course sits an unassisted examination against its own. Levels run beginning, developing, proficient, mastered.</p>\n'
              f'          <ul>{rubs}</ul>')
    inner3 = ('          <p>The portfolio is the primary evidence. At each annual gate the faculty read every student\'s portfolio against the five outcomes and record a level for each. Each year the levels are aggregated by outcome and by course; a course whose students fall short on an outcome it claims is revised before the next year, and the revision is recorded with the reason. This is the program-review loop, and it is the same loop the gates run for each student.</p>')
    body = (_section("Where It Is Assessed", "Outcomes and competencies", inner1)
            + _section("How It Is Judged", "Rubrics", inner2)
            + _section("What Happens With It", "Program review", inner3))
    return _shell("Assessment Plan", "For Reviewers", "The assessment <em>plan</em>.",
                  "outcomes · competencies · rubrics · the gate",
                  "How each institutional outcome and WSCUC Core Competency is assessed, where, with what rubric, and how results feed program review.",
                  body)


def page_rubrics() -> str:
    rub = _load_rubrics()
    names = dict(OUTCOMES)
    body = []
    for r in rub.values():
        rows = []
        for cr in r["criteria"]:
            lv = "".join(f"<td>{_e(x)}</td>" for x in cr["levels"])
            ev = " · ".join(names.get(o, o) for o in cr["outcomes"])
            rows.append(f"<tr><th>{_e(cr['name'])}<span>{_e(ev)}</span></th>{lv}</tr>")
        inner = (f'          <p>{_e(r["applies_to"])}</p>\n'
                 '          <div class="evidence-table-wrap"><table class="evidence-table rubric-table"><thead><tr><th>Criterion</th>'
                 '<th>Beginning</th><th>Developing</th><th>Proficient</th><th>Mastered</th></tr></thead>'
                 f'<tbody>{"".join(rows)}</tbody></table></div>')
        body.append(_section(r["name"], r["id"], inner, r["id"]))
    return _shell("Rubrics", "For Reviewers", "The <em>rubrics</em>.",
                  f"{len(rub)} rubrics · four levels · every criterion mapped to the outcomes",
                  "How every kind of made thing, and every unassisted examination, is judged: criteria, four levels, and the outcomes each evidences.",
                  "".join(body))


def write_pages(write, out: Path = ROOT) -> None:
    rows = load_blocks()
    d = out / "curriculum"
    write(d / "map.html", page_map(rows))
    write(d / "breadth.html", page_breadth(rows))
    write(d / "requirements.html", page_requirements(rows))
    write(d / "policies.html", page_policies())
    write(d / "assessment.html", page_assessment(rows))
    write(d / "rubrics.html", page_rubrics())
    import fundamentals
    write(d / "fundamentals.html", fundamentals.page())
