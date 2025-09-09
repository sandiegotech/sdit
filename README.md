# SDIT Curriculum & Knowledge Repository

Authoritative, versioned source for San Diego Institute of Technology (SDIT) curriculum, programs, and canonical knowledge. Plain‑text first, easy to validate, and auto‑published to GitHub Pages.

- Live site: https://sandiegotech.github.io/sdit/
- Repository: https://github.com/sandiegotech/sdit

---

## What’s Inside

- `knowledge/`: Canonical YAML describing SDIT.
  - `knowledge/identity.yaml`: Name, tagline, mission, values.
  - `knowledge/philosophies.yaml`: Core philosophies and principles.
  - `knowledge/anchors.yaml`: Strategic anchors.
  - `knowledge/programs.yaml`: Divisions and programs (e.g., DEUS, MIRA).
  - `knowledge/research.yaml`: Labs, streams, outputs.
  - `knowledge/community.yaml`: Fellowships, culture, admissions.
  - `knowledge/infrastructure.yaml`: Digital, legal, physical.
  - `knowledge/projects.yaml`: Initiatives and projects.
  - `knowledge/priorities.yaml`: Near-term goals.

- `docs/`: Generated static site (HTML). Do not edit by hand. The site is rebuilt and committed on each push to `main`.

- `courses/`: Flat list of all courses (one Markdown file per course). See `courses/INDEX.md` for the generated master list.

- `programs/`: Program curricula (syllabi + schedules). Example: `programs/Bachelor-Liberal-Arts/vol-01-foundations/` with `syllabus.md` and `schedule/` chapters/sections.

- `scripts/`: Generators and validation
  - `validate.py`: Minimal YAML shape check for `knowledge/`
  - `build_courses_yaml.py`: Scan `courses/` → write `knowledge/courses.yaml`
  - `generate_course_indexes.py`: Write `courses/INDEX.md` from the master list
  - `build_site.py`: Build static site; use `--out docs` for Pages
  - `clean_practice_times.py`: Remove times from Practice sections
  - `clean_learning_times.py`: Keep times for Read/Watch/Listen only

- `.github/workflows/validate.yml`: CI that runs the validator on every push and pull request.

---

## Getting Started

Prerequisites:
- Python 3.11+
- `pip` with access to install `pyyaml`

Setup and validate locally:
- `pip install pyyaml`
- `python scripts/validate.py`

Build the site locally (mirrors GitHub Pages output):
- `python scripts/build_site.py --out docs`

The validator checks that each file in `knowledge/` parses as YAML and uses a top-level mapping. It exits non-zero if any file fails to load or violates this shape.

---

## Authoring: Courses & Programs

General guidance:
- Use YAML with a top-level mapping (dictionary) per file.
- Prefer clear, descriptive keys; avoid unexplained abbreviations.
- Keep related concepts together; split into additional files when a topic grows.
- Commit small, focused changes; include context in commit messages.

Minimal example structure:

```yaml
# Example only — adapt keys to the file’s topic
name: San Diego Institute of Technology
mission: Education for the 21st century
values:
  - integrity
  - craft
  - service
notes: >
  Short, human-readable explanation that complements structured fields.
```

Schema: A formal schema is not enforced yet. If you add structure that others will reuse, document it briefly and keep key names consistent.

Add a course (flat file under `courses/`):
```yaml
---
id: lbs-101
title: "LBS 101 — The Mental Gym"
level: 100
tags: [liberal-education, foundations]
---

# LBS 101 — The Mental Gym
What this course is about...
```

Add a program section (chapter/section under a volume):
```yaml
---
id: vol01-chapter04-section02
title: "Section 02 — Structure & Flow (LBS 105)"
parent_volume: vol-01-foundations
chapter: 4
section: 2
course: LBS 105 – Writing & Communication I
---

# Section 02 — Structure & Flow

## Learning Session
Explore These Materials:
1. Read (45 min) — ...
2. Watch (45 min) — ...
3. Listen (30 min) — ...
4. Reflect While Engaging — ...

## Key Quote Box
“_______________________________________________________”

## Practice
1. Task — ...
2. Task — ...

## Hard Problem (Optional)
A stretch challenge...
```

---

## Building & Publishing

- GitHub Pages: Settings → Pages → Source = Deploy from a branch; Branch = `main`; Folder = `/docs`.
- Auto‑build: `.github/workflows/update-docs-index.yml` rebuilds the site into `docs/` and commits the update on every push to `main`.
- Local build: `python scripts/build_site.py --out docs` then open `docs/index.html`.

---

## Course Master List

Regenerate the canonical list and index after adding/updating courses:
- `python scripts/build_courses_yaml.py`
- `python scripts/generate_course_indexes.py`

---

## Continuous Integration

On each push and pull request, GitHub Actions runs `scripts/validate.py` to sanity-check the YAML in `knowledge/`:

- Workflow file: `.github/workflows/validate.yml`
- Python 3.11 and `pyyaml` are used to parse files.
- The job fails if any YAML is invalid or the top-level is not a mapping.

---

## Contributing

- Create a feature branch for each change.
- Run `python scripts/validate.py` before opening a PR.
- Keep changes minimal and well-scoped; prefer multiple small PRs over one large PR.
- In PR descriptions, summarize what changed and why.

---

## Future Improvements

- Add JSON Schema validation for `knowledge/`.
- Expand program schedules and link more courses.
- Add site search and sitemap.
