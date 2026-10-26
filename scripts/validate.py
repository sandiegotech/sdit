#!/usr/bin/env python3
"""validate.py — fail the build on a registry that disagrees with the files.

Every knowledge/*.yaml must parse as a mapping. Then knowledge/catalog.yaml is
checked course by course:

  - required fields present; dirs and codes unique; thread ids real
  - semester 1-8; units a positive integer; days_planned an explicit integer
  - outcomes non-empty and drawn from the five institutional outcomes
  - depth studios name their concentrations
  - the course directory and its index.md exist
  - published days are contiguous from day 1 and never exceed days_planned
  - each day file's front-matter `day:` matches its filename
  - status agrees with the files on disk:
        planned / syllabus  -> no day files
        building            -> no day files (being written, none published)
        day1                -> at least one day file
        live                -> every planned day, and an index.md at catalog grade
  - the index.md front-matter status mirrors the registry (sync_courses keeps it so)

Nothing is called live until a learner knows exactly what to do each day.
"""
from __future__ import annotations

import re
import sys
from glob import glob
from pathlib import Path

import yaml

import arcs
import catalog as catalog_mod
import frontmatter

ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE = ROOT / "knowledge"
COURSES = ROOT / "courses"

REQUIRED_COURSE_FIELDS = [
    "code", "dir", "name", "units", "thread", "semester", "status",
    "days_planned", "outcomes", "catalog_register", "teaching_frame", "artifact",
]
STATUSES = {"planned", "syllabus", "building", "day1", "live"}
OUTCOMES = {"judgment", "intelligence", "craft", "articulation", "breadth"}
CONCENTRATIONS = {"media", "design", "engineering"}
MAX_DAYS = 60
ANSWER_MARKER = "<!-- sdit:answer -->"

# What a course page must carry before its course can be called live.
LIVE_HEADINGS = [
    "## Overview",
    "## The Two Registers",
    "## Learning Outcomes",
    "## The Made Thing",
    "## How You're Assessed",
    "## The Daily Path",
]


# ── Day standard v2 (PLAN.md 12.4): what a day must be before it publishes ──
EXPERIENCE = ("Look", "Watch", "Listen", "Read")
QUESTION_SECTIONS = ("Carry the question", "Now make something")   # the latter: Workshop days
CURIOUS = "If you're still curious"
MIN_WORDS, MAX_WORDS = 200, 550     # measured on the published days (273-315)
BANNED = re.compile(r"\b(revolutionary|disruptive|game-changing|incredible|amazing|unlock\w*|delve\w*|dive into|journey)\b", re.I)
PLACEHOLDERS = ("DEK:", "WRITE THE", "IMAGE-URL", "Title goes here", "The question goes here", "Why it matters today, in a paragraph", "The idea, plainly")


def _h2s(body: str) -> list[str]:
    return [m.group(1).strip().replace("\u2019", "'") for m in re.finditer(r"^## (.+)$", body, flags=re.M)]


def _section_text(body: str, heading: str) -> str:
    m = re.search(rf"^## {re.escape(heading)}\s*$(.*?)(?=^## |\Z)", body.replace("\u2019", "'"), flags=re.M | re.S)
    return m.group(1) if m else ""


def main_path_words(body: str) -> int:
    main = re.split(r"^## If you.re still curious", body, flags=re.M)[0]
    main = re.sub(r"<!--.*?-->", " ", main, flags=re.S)
    main = re.sub(r"<[^>]+>", " ", main)
    main = re.sub(r"^# .*$", " ", main, flags=re.M)
    return len(re.findall(r"[A-Za-z\u2019'-]+", main))


def validate_day_text(meta: dict, body: str, n: int, course_dir: str) -> list[str]:
    """Rules for one day file. Days marked `standard: 1` (the five first days,
    written before v2) get the core rules; every other day gets all of them."""
    out = []
    title = str(meta.get("title") or "")
    h1 = re.search(r"^# (.+)$", body, flags=re.M)
    if not h1 or h1.group(1).strip() != title:
        out.append("its H1 does not equal its front-matter title")
    for k in ("id", "course"):
        if not meta.get(k):
            out.append(f"has no `{k}` in its front matter")
    if not re.search(rf"\*\*Day {n} is done\.?\*\*", body):
        out.append(f"has no done line (\"That's it. **Day {n} is done.**\")")
    for ph in PLACEHOLDERS:
        if ph in body:
            out.append(f"still contains the scaffold placeholder {ph!r}")
    if str(meta.get("standard", "2")) == "1":
        return out

    h2 = _h2s(body)
    exp = [h for h in h2 if h in EXPERIENCE]
    if len(exp) != 1:
        out.append(f"has {len(exp)} experience sections; exactly one of {', '.join(EXPERIENCE)}")
    if "One idea" not in h2:
        out.append("has no '## One idea' section")
    q = [h for h in h2 if h in QUESTION_SECTIONS]
    if len(q) != 1:
        out.append("has no '## Carry the question' section")
    if not h2 or h2[-1] != CURIOUS:
        out.append(f"does not end with '## {CURIOUS}'")
    extra = [h for h in h2 if h not in EXPERIENCE + QUESTION_SECTIONS + ("One idea", CURIOUS)]
    if extra:
        out.append(f"has sections outside the standard: {', '.join(extra)}")
    if exp and q and "One idea" in h2:
        qi = h2.index(q[0])
        if not (h2.index(exp[0]) < qi and h2.index("One idea") < qi):
            out.append("asks its question before the thing to experience and the idea")
    if exp:
        sec = re.sub(r"<!--.*?-->", " ", _section_text(body, exp[0]), flags=re.S)
        if not re.search(r"<figure\b|<iframe\b|<blockquote\b|^> ", sec, flags=re.M):
            out.append(f"'## {exp[0]}' does not put the thing on the page (a figure, an embed, or a quotation)")
    doors = re.findall(r"^\*\*[^*]+\*\*", _section_text(body, CURIOUS), flags=re.M)
    if len(doors) != 3:
        out.append(f"has {len(doors)} doors under '{CURIOUS}'; it needs three")
    elif not doors[-1].startswith("**Ask someone"):
        out.append("its third door is not '**Ask someone.**'")
    words = main_path_words(body)
    if not MIN_WORDS <= words <= MAX_WORDS:
        out.append(f"main path is {words} words; a ten-minute day is {MIN_WORDS} to {MAX_WORDS}")
    prose = re.sub(r"<!--.*?-->", " ", body, flags=re.S)
    prose = re.sub(r"^>.*$", "", prose, flags=re.M)
    prose = re.sub(r"\[[^\]]*\]\([^)]*\)|<[^>]+>|https?://\S+", " ", prose)
    hits = sorted({m.group(1).lower() for m in BANNED.finditer(prose)})
    if hits:
        out.append(f"uses words the voice does not: {', '.join(hits)}")
    return out


def load(p):
    with open(p, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def validate_yaml_files(errors, knowledge: Path = KNOWLEDGE):
    for f in glob(str(knowledge / "*.yaml")):
        try:
            data = load(f)
            if not isinstance(data, dict):
                raise ValueError("top-level YAML must be a mapping")
        except Exception as e:
            errors.append(f"{Path(f).name}: {e}")


def _positive_int(v) -> bool:
    return isinstance(v, int) and not isinstance(v, bool) and v >= 1


def validate_course(c: dict, i: int, threads: set, courses_root: Path, errors: list) -> None:
    label = c.get("dir") or c.get("code") or f"#{i}"
    err = lambda msg: errors.append(f"catalog.yaml: {label} {msg}")

    for field in REQUIRED_COURSE_FIELDS:
        if c.get(field) in (None, "", []):
            err(f"missing required field `{field}`")

    sem = c.get("semester")
    if sem is not None and not (isinstance(sem, int) and 1 <= sem <= 8):
        err(f"has invalid semester {sem!r} (want int 1-8)")

    if "units" in c and not _positive_int(c.get("units")):
        err(f"has invalid units {c.get('units')!r} (want a positive integer; one course per semester)")

    planned = c.get("days_planned")
    if planned is not None and not (_positive_int(planned) and planned <= MAX_DAYS):
        err(f"has invalid days_planned {planned!r} (want int 1-{MAX_DAYS})")

    if threads and c.get("thread") and c["thread"] not in threads:
        err(f"names unknown thread `{c['thread']}`")

    status = c.get("status")
    if status is not None and status not in STATUSES:
        err(f"has unknown status `{status}` (want one of {', '.join(sorted(STATUSES))})")

    outcomes = c.get("outcomes")
    if outcomes is not None:
        if not isinstance(outcomes, list) or not outcomes:
            err("must list at least one outcome")
        else:
            for o in outcomes:
                if o not in OUTCOMES:
                    err(f"names unknown outcome `{o}` (want one of {', '.join(sorted(OUTCOMES))})")

    if c.get("thread") == "depth":
        concs = c.get("concentrations")
        if not isinstance(concs, list) or not concs:
            err("is a depth studio but names no concentrations")
        else:
            for k in concs:
                if k not in CONCENTRATIONS:
                    err(f"names unknown concentration `{k}`")

    d = c.get("dir")
    if not d:
        return
    cdir = courses_root / d
    if not cdir.is_dir():
        err(f"has no directory courses/{d} (run scripts/scaffold_catalog.py)")
        return
    index_md = cdir / "index.md"
    if not index_md.exists():
        err(f"has no courses/{d}/index.md (run scripts/scaffold_catalog.py)")

    days = catalog_mod.published_days(cdir)
    if days != list(range(1, len(days) + 1)):
        err(f"has a gap in its day files ({', '.join(f'day-{n:02d}' for n in days)}); days publish in order from day 1")
    if _positive_int(planned) and days and days[-1] > planned:
        err(f"has day-{days[-1]:02d}.md but plans only {planned} days")

    for n in days:
        f = cdir / f"day-{n:02d}.md"
        meta, _body = frontmatter.parse(f.read_text(encoding="utf-8"))
        fm_day = meta.get("day")
        try:
            fm_day = int(fm_day) if fm_day is not None else None
        except (TypeError, ValueError):
            pass
        if fm_day is not None and fm_day != n:
            err(f"day-{n:02d}.md says `day: {meta.get('day')}` in its front matter")
        if not meta.get("title"):
            err(f"day-{n:02d}.md has no `title` in its front matter")
        # Every day asks one question and keeps the answer (day standard v2).
        q = str(meta.get("question") or "").strip()
        if not q:
            err(f"day-{n:02d}.md has no `question` in its front matter")
        elif f"**{q}**" not in _body:
            err(f"day-{n:02d}.md does not ask its front-matter question in bold on the page")
        if ANSWER_MARKER not in _body:
            err(f"day-{n:02d}.md has no answer field ({ANSWER_MARKER}) under its question")
        for problem in validate_day_text(meta, _body, n, d):
            err(f"day-{n:02d}.md {problem}")
        # Nothing on a day page tracks the reader (PLAN.md 12.3, items 2 and 3).
        # Comments are the scaffold's instructions, not content; skip them.
        _live = re.sub(r"<!--.*?-->", " ", _body, flags=re.S)
        for tag in re.findall(r"<iframe\b[^>]*>", _live):
            src = re.search(r'src="([^"]+)"', tag)
            if not src or not src.group(1).startswith("https://www.youtube-nocookie.com/embed/"):
                err(f"day-{n:02d}.md embeds a frame from outside www.youtube-nocookie.com")
        for tag in re.findall(r"<img\b[^>]*>", _live):
            src = re.search(r'src="([^"]+)"', tag)
            if not src or not (src.group(1).startswith("https://upload.wikimedia.org/") or src.group(1).startswith("/")):
                err(f"day-{n:02d}.md shows an image from outside upload.wikimedia.org or this site")
            for attr, name in (('alt="', "alt"), ('loading="lazy"', "loading"), ('referrerpolicy="no-referrer"', "referrerpolicy")):
                if attr not in tag:
                    err(f"day-{n:02d}.md has an <img> without {name}")

    if status in ("planned", "syllabus", "building") and days:
        err(f"has status `{status}` but {len(days)} published day file(s); set `day1` (or `live`)")
    if status == "day1" and not days:
        err("has status `day1` but no day-NN.md file")
    if status == "live":
        if not _positive_int(planned):
            pass  # already reported
        elif len(days) < planned:
            err(f"has status `live` but only {len(days)} of {planned} days exist")
        if index_md.exists():
            text = index_md.read_text(encoding="utf-8")
            missing = [h for h in LIVE_HEADINGS if h not in text]
            if missing:
                err(f"has status `live` but index.md lacks {', '.join(missing)}")

    # The arc is the plan for every day, so it must parse, cover every planned
    # day, and agree with each published day's title.
    arc_file = cdir / "arc.md"
    if not arc_file.exists():
        err("has no arc.md (every course is planned day by day before it is written)")
    else:
        try:
            arc = arcs.parse_arc(arc_file.read_text(encoding="utf-8"), f"courses/{d}/arc.md")
        except arcs.ArcError as e:
            errors.append(f"{e}")
            arc = None
        if arc is not None and _positive_int(planned) and max(arc.days) != planned:
            err(f"arc.md plans {max(arc.days)} days but the registry says days_planned: {planned}")
        if arc is not None:
            for n in days:
                info = catalog_mod.day_info(cdir, n)
                a = arc.day(n)
                if info and a and arcs.normalize_title(info[0]) != arcs.normalize_title(a.title):
                    err(f"day-{n:02d}.md is titled '{info[0]}' but the arc calls it '{a.title}'; make them agree")

    if index_md.exists() and status:
        meta, _ = frontmatter.parse(index_md.read_text(encoding="utf-8"))
        fm_status = meta.get("status")
        if fm_status is not None and str(fm_status) != str(status):
            err(f"index.md front matter says `status: {fm_status}` but the registry says `{status}` "
                f"(run scripts/sync_courses.py)")


SYLLABUS_METHODS = {"seminar", "lecture", "laboratory", "studio", "placement", "independent"}
ACCESS = {"open", "library", "purchase", "provided"}
LEVELS = {"I", "D", "M"}
COMPETENCIES = {
    "written-communication": "Written communication",
    "oral-communication": "Oral communication",
    "quantitative-reasoning": "Quantitative reasoning",
    "information-literacy": "Information literacy",
    "critical-thinking": "Critical thinking",
}
INSTITUTIONAL = ["Judgment", "Command of Intelligence", "Workmanship", "Articulation", "Breadth of Mind"]


def _rubric_ids(knowledge: Path = KNOWLEDGE) -> set:
    f = knowledge / "rubrics.yaml"
    if not f.exists():
        return set()
    return {r["id"] for r in (load(f) or {}).get("rubrics", [])}


def _section(text: str, heading: str) -> str:
    m = re.search(rf"^## {re.escape(heading)}\s*$(.*?)(?=^## |\Z)", text, flags=re.M | re.S)
    return m.group(1) if m else ""


def validate_syllabi(courses: list, courses_root: Path, errors: list, rubric_ids: set | None = None) -> None:
    """Every course page carries a syllabus block a reviewer could check, and
    every number in it adds up (PLAN.md section 13)."""
    rubric_ids = _rubric_ids() if rubric_ids is None else rubric_ids
    by_code = {c.get("code"): c for c in courses if isinstance(c, dict)}
    served: dict[str, set] = {k: set() for k in COMPETENCIES}   # competency -> years assessed
    mastered: set = set()
    for c in courses:
        if not isinstance(c, dict) or not c.get("dir"):
            continue
        label = c["dir"]
        err = lambda msg: errors.append(f"courses/{label}/index.md: {msg}")
        f = courses_root / c["dir"] / "index.md"
        if not f.exists():
            continue
        text = f.read_text(encoding="utf-8")
        meta, body = frontmatter.parse(text)
        b = (meta or {}).get("syllabus") if isinstance(meta, dict) else None
        if not isinstance(b, dict):
            err("has no `syllabus:` block in its front matter")
            continue

        num = re.search(r"\d+", str(c.get("code", "")))
        want_level = "upper" if num and int(num.group()[0]) >= 3 else "lower"
        if b.get("level") != want_level:
            err(f"syllabus level is {b.get('level')!r}; a {c.get('code')} course is {want_level} division")

        units = c.get("units")
        h = b.get("hours") or {}
        try:
            total = sum(float(h.get(k, 0)) for k in ("instruction", "studio_or_lab", "independent"))
        except (TypeError, ValueError):
            total = -1
        if isinstance(units, int) and abs(total - units * 3) > 1e-9:
            err(f"weekly hours sum to {total:g}; {units} units need {units * 3}")

        methods = b.get("method") or []
        if not methods or any(m not in SYLLABUS_METHODS for m in methods):
            err(f"method must be a non-empty list from {sorted(SYLLABUS_METHODS)}")

        sem = c.get("semester")
        for key, rel in (("prerequisites", "earlier"), ("corequisites", "same")):
            for code in b.get(key) or []:
                other = by_code.get(code)
                if not other:
                    err(f"{key} names {code!r}, which is not in the catalog")
                elif rel == "earlier" and not (other.get("semester") or 9) < (sem or 0):
                    err(f"prerequisite {code} is not in an earlier semester")
                elif rel == "same" and other.get("semester") != sem:
                    err(f"corequisite {code} is not in the same semester")

        mats = b.get("materials") or []
        if not mats:
            err("lists no required materials")
        for m in mats:
            if not isinstance(m, dict) or not m.get("title"):
                err("has a material with no title")
                continue
            if m.get("access") not in ACCESS:
                err(f"material {m['title']!r} has access {m.get('access')!r}; want one of {sorted(ACCESS)}")
            cost = m.get("cost")
            if not isinstance(cost, (int, float)) or cost < 0:
                err(f"material {m['title']!r} needs a cost (0 when open, library, or provided)")
            elif m.get("access") in ("open", "library", "provided") and cost:
                err(f"material {m['title']!r} is {m.get('access')} but costs {cost}")

        rows = b.get("assessment") or []
        try:
            wsum = sum(int(r.get("weight")) for r in rows)
        except (TypeError, ValueError):
            wsum = -1
        if wsum != 100:
            err(f"assessment weights sum to {wsum}, not 100")
        if not any("unassisted" in str(r.get("component", "")).lower() for r in rows):
            err("assessment has no unassisted examination component")
        if not str(b.get("exam") or "").strip():
            err("syllabus names no unassisted examination (`exam`)")

        if b.get("rubric") not in rubric_ids:
            err(f"rubric {b.get('rubric')!r} is not in knowledge/rubrics.yaml")

        ol = b.get("outcome_levels") or {}
        reg = set(c.get("outcomes") or [])
        if set(ol) != reg:
            err(f"outcome_levels covers {sorted(ol)}; the registry lists {sorted(reg)}")
        if any(v not in LEVELS for v in ol.values()):
            err("outcome_levels values must be I, D, or M")

        outcomes_text = _section(body, "Learning Outcomes")
        for line in re.findall(r"^\d+\.\s.*$", outcomes_text, flags=re.M):
            tail = line.split("→", 1)[1] if "→" in line else ""
            if not any(name in tail for name in INSTITUTIONAL):
                err(f"learning outcome is not mapped to an institutional outcome: {line[:60]}…")
        cc = b.get("core_competencies") or {}
        for k, v in cc.items():
            if k not in COMPETENCIES:
                err(f"unknown core competency {k!r}")
                continue
            if v not in LEVELS:
                err(f"core competency {k} has level {v!r}; want I, D, or M")
            if COMPETENCIES[k] not in outcomes_text:
                err(f"core competency {COMPETENCIES[k]} is claimed but no learning outcome names it")
            if isinstance(sem, int):
                served[k].add((sem + 1) // 2)
            if v == "M":
                mastered.add(k)

    if courses and all(isinstance(c, dict) for c in courses) and len(courses) > 5:
        for k, name in COMPETENCIES.items():
            for year in (1, 2):
                if year not in served[k]:
                    errors.append(f"curriculum: {name} is assessed by no course in Year {year} of the Foundation")
            if k not in mastered:
                errors.append(f"curriculum: {name} is never assessed at graduation level (M)")


def validate_catalog(errors, data: dict | None = None, courses_root: Path = COURSES):
    if data is None:
        path = KNOWLEDGE / "catalog.yaml"
        if not path.exists():
            return
        data = load(path) or {}
    courses = data.get("courses", [])
    if not isinstance(courses, list):
        errors.append("catalog.yaml: `courses` must be a list")
        return
    threads = {t.get("id") for t in data.get("threads", []) if isinstance(t, dict)}

    seen_dirs, seen_codes = set(), set()
    for i, c in enumerate(courses):
        if not isinstance(c, dict):
            errors.append(f"catalog.yaml: course #{i} is not a mapping")
            continue
        d = c.get("dir")
        if d:
            if d in seen_dirs:
                errors.append(f"catalog.yaml: duplicate dir `{d}`")
            seen_dirs.add(d)
        code = c.get("code")
        if code:
            if code in seen_codes:
                errors.append(f"catalog.yaml: duplicate code `{code}`")
            seen_codes.add(code)
        validate_course(c, i, threads, courses_root, errors)

    validate_syllabi(courses, courses_root, errors)

    # Every course directory on disk should be a registered course, so nothing
    # unlisted gets built and published by accident.
    if courses_root.is_dir():
        for p in sorted(courses_root.iterdir()):
            if p.is_dir() and not p.name.startswith(".") and p.name not in seen_dirs:
                errors.append(f"courses/{p.name}/ exists but is not in catalog.yaml")


def validate_calendar(errors, data: dict | None = None):
    """The publishing calendar must describe eight fifteen-week semesters and a
    first release on a Monday, or every date on the site is wrong."""
    import datetime as dt
    path = KNOWLEDGE / "calendar.yaml"
    if data is None:
        if not path.exists():
            errors.append("knowledge/calendar.yaml is missing")
            return
        data = load(path) or {}
    pub = data.get("publishing") or {}
    first = pub.get("first_release")
    if isinstance(first, str):
        try:
            first = dt.date.fromisoformat(first)
        except ValueError:
            first = None
    if not isinstance(first, dt.date):
        errors.append("calendar.yaml: publishing.first_release must be a date")
    elif first.weekday() != 0:
        errors.append(f"calendar.yaml: first_release {first} is not a Monday")
    sems = data.get("semesters") or []
    if [s.get("n") for s in sems] != list(range(1, 9)):
        errors.append("calendar.yaml: semesters must be listed 1 to 8 in order")
    if any(s.get("weeks") != 15 for s in sems):
        errors.append("calendar.yaml: every semester has 15 weeks (days_planned is 15 everywhere)")


def main() -> int:
    errors: list[str] = []
    validate_yaml_files(errors)
    validate_calendar(errors)
    validate_catalog(errors)
    if errors:
        for e in errors:
            print(f"[ERROR] {e}")
        print(f"Validation: FAILED ({len(errors)} issue(s))")
        return 1
    print("Validation: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
