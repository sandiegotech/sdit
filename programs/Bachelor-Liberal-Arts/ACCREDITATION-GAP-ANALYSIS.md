# Bachelor of Liberal Arts — Accreditation Gap Analysis

> **Superseded (June 2026).** The institution's degree is now the **Bachelor of
> Science in Technology** — see [The Degree](../../institute/the-degree.html) and
> [The Plan](../../institute/sdit-bible.html). The BLA remains published as the
> open curriculum archive. This analysis is retained for the record; its Track B
> (institutional) findings still apply and are folded into the Plan's
> accreditation pathway (§VII).

**Model:** Competency-Based Education (CBE / direct assessment)
**Target:** WSCUC institutional accreditation + CA BPPE degree authority
**Source of truth:** [`knowledge/degree.yaml`](../../knowledge/degree.yaml)
**Status:** architecture draft — not yet a sanctioned degree

---

## 1. The one-sentence verdict

You have a **strong Year 1 of a curriculum** and **none of the institution** — and accreditation
grades the institution. The repo can carry the academic 10–15% of an accreditation file; the
other 85% (faculty of record, registrar, finances, governance, multi-year assessment evidence)
is an organization-building project that no amount of curriculum work substitutes for.

This document scores the **academic** layer against the CBE degree contract and is brutally
specific about what's missing. The institutional layer is tracked separately in §5.

---

## 2. Scorecard — degree contract vs. current repo

| Degree component (from `degree.yaml`) | Required | Current state | Gap | Priority |
|---|---|---|---|---|
| **Credit/competency accounting** | 120 CU, each course carries CU + workload hrs | No CU or hours anywhere | **Total** | P0 |
| **General-education breadth** | 8 distribution areas, 60 CU | ~6 of 8 areas have courses | **Partial** | P1 |
| **Oral communication** | Dedicated competency | None (only film/design touch it) | **Missing area** | P1 |
| **Upper division (300/400)** | ≥40 CU of depth | **Zero** — entire catalog is 100–200 | **Total** | P0 |
| **A declared major / concentration** | 1 concentration, 36 CU | Breadth only; no major exists | **Total** | P0 |
| **Years 2–4 built out** | Vols 2–8 with sessions | Only **vol-01** has lessons | **~7/8 missing** | P1 |
| **Program Learning Outcomes** | PLOs laddering to ILOs | Volume-level outcomes only (good seed) | **Partial** | P1 |
| **Curriculum map (course→outcome)** | Matrix: Introduce/Develop/Master | Does not exist | **Total** | P1 |
| **Rubrics per competency** | Every competency rubric-scored | None | **Total** | P0 |
| **Capstone structure** | Defended portfolio, 9 CU | Saving mechanism exists; no structure | **Partial** | P2 |
| **Transcript / records system** | Legal record of completion | localStorage + git push | **Not credible as record** | P2 |

P0 = blocks the degree from being coherent at all · P1 = blocks completeness · P2 = blocks legitimacy

---

## 3. The five gaps that actually matter

### Gap 1 — There is no upper division (P0)
A four-year degree is *defined* by Years 3–4: 300/400-level depth, a major, and research/capstone.
**Every course you have is 100–200 level.** Right now you have, in accreditation terms, roughly an
Associate's worth of *breadth* and zero *depth*. This is the single biggest gap. `degree.yaml` reserves
Volumes 5–8 for upper division, but the courses to fill them don't exist yet.

### Gap 2 — There is no major (P0)
Liberal Arts still requires a concentration. Your anchors hand you three natural ones
(Technology/DEUS, Media-Arts/MIRA, Enterprise) and `degree.yaml` defines them — but each is seeded
with 200-level courses and needs a genuine upper-division sequence built on top.

### Gap 3 — Nothing is measured (P0)
CBE's entire credibility rests on **rubrics**: "how do you *know* the competency was demonstrated?"
You have rich lessons and a portfolio-saving mechanism, but **zero rubrics**. To an accreditor a
program with no assessment instruments is not a program. This is also the cheapest gap to close —
it's writing, not engineering.

### Gap 4 — The degree isn't counted (P0)
No course carries a competency-unit value or workload-hours estimate, so the 120-CU contract can't
be audited. Until courses carry CU + hours, you cannot prove the degree adds up to a degree. This is
a metadata backfill across the ~45 existing courses.

### Gap 5 — The institution doesn't exist yet (P2 here, but P0 for the *real* goal)
No faculty of record, no registrar, no audited finances, no independent board, no state authority.
**In California you legally cannot confer or advertise a "degree" without CA BPPE approval first** —
before WSCUC even becomes relevant. Until then, this is honestly an *open curriculum + certificate of
completion*, and the public copy must say so to avoid misrepresentation.

---

## 4. What's already strong (don't rebuild these)

- **The 8-volume spine is genuinely good architecture.** 8 volumes = 8 terms = 4 years ≈ 120 CU maps
  almost perfectly onto a degree. You designed the skeleton right without knowing it.
- **Volume-level `outcomes:` + `assessment:` blocks** already exist in syllabi — a real seed for PLOs.
- **The portfolio/student-work mechanism** is, in CBE terms, an *evidence engine*. Most programs have
  to build this; you have it.
- **The philosophy fits CBE.** "Project-based validation in lieu of grades" is a liability in a
  traditional degree and an *asset* in CBE. You picked the one model where your DNA is a feature.
- **Vol-01 lesson quality is high** — the Year-1 content bar is set; the work is to extend it, not redo it.

---

## 5. Two tracks, run in parallel

These are different kinds of work. Don't let the slow one block the fast one.

**Track A — Curriculum (this repo, you can do now, weeks–months)**
1. Backfill CU + workload-hours onto all existing courses *(closes Gap 4)*
2. Write rubrics for existing competencies *(closes Gap 3)*
3. Define PLOs + build the curriculum map *(P1)*
4. Design 300/400-level courses + one full concentration *(closes Gaps 1–2)*
5. Build out Volumes 2–8 lessons *(P1, largest content effort)*
6. Formalize the capstone rubric + defense *(P2)*

**Track B — Institution (not a coding project, months–years, capital-intensive)**
1. Legal entity + nonprofit confirmation, conflict-separated governing board
2. **CA BPPE application** for degree-granting authority *(gates everything public)*
3. Faculty-of-record model (even part-time/affiliate to start)
4. Registrar/transcript system of record (not localStorage)
5. Audited financials / multi-year runway
6. WSCUC Eligibility → Candidacy → Initial Accreditation (5–7+ yrs)

**The honest sequencing:** Track A makes the curriculum *accreditation-shaped* and is worth doing on
its own merits (it's a great open credential even if accreditation never happens). Track B is the
real gate to the word "degree," and step B2 (BPPE) must land before any public degree language.

---

## 6. Immediate next actions (Track A, in order)

1. **`knowledge/outcomes.yaml`** — PLOs + curriculum map matrix. *(highest evidence-per-hour artifact)*
2. **Per-course metadata schema** — add `cu`, `workload_hours`, `clos`, `rubric` to `courses.yaml`
   / course frontmatter, then backfill the ~45 courses.
3. **One reference rubric** — write a single competency rubric end-to-end as the template all others copy.
4. **One concentration, fully designed** — pick Technology/DEUS or Media/MIRA and build its 300/400 sequence
   as the proof-of-concept for upper division.

---

*Generated as a strategic planning artifact. Pair with [`knowledge/degree.yaml`](../../knowledge/degree.yaml),
the machine-readable contract this analysis scores against.*
