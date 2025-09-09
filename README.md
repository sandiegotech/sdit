# SDIT Curriculum & Knowledge Repository

Authoritative, versioned source for San Diego Institute of Technology (SDIT) identity, strategy, programs, and public-facing content. The goal is to keep information organized, human-readable, and easy to validate.

- **Website:** https://sandiegotech.github.io/sdit/
- **Repository:** https://github.com/sandiegotech/sdit
- **Main site:** https://sandiegotech.org
- **Learning portal:** https://learn.sandiegotech.org

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

- `docs/`: Public, human-readable Markdown content.
  - `docs/index.md`: High-level overview.
  - `docs/faq.md`: Frequently asked questions.

- `courses/`: Flat list of all courses (one Markdown file per course). No nested core/electives folders. See `courses/INDEX.md` for the generated master list.

- `programs/`: Volume syllabi and schedules by semester.
  - `programs/vol-XX-*` with `syllabus.md` (Year/Semester overview) and optional `schedule/` (daily/weekly pages).

- `scripts/`: Validation tooling.
  - `scripts/validate.py`: Minimal YAML shape check (ensures top-level mapping).

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

## Editing the Knowledge Base

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

Schema: A formal schema is not enforced yet. If you add structure that others will reuse, document it in the file with brief comments and keep key names consistent across files.

---

## Docs (`docs/`)

- Write public content in Markdown.
- Keep pages short and scannable; link to deeper details in `knowledge/` when appropriate.
- There is no static site generator configured yet in this repo. You can render directly on GitHub, or add a site tool (e.g., MkDocs) in a future change.

---

## Courses (`courses/`) and Programs (`programs/`)

- Courses: keep simple — one Markdown page per course at the top level of `courses/`.
- Programs: each volume lives under `programs/vol-XX-*/` with a `syllabus.md`. If you add schedules, place them under `programs/vol-XX-*/schedule/`.
- Master list: regenerate `courses/INDEX.md` and `knowledge/courses.yaml` with:
  - `python scripts/build_courses_yaml.py`
  - `python scripts/generate_course_indexes.py`

Publishing:
- This repository auto-updates the generated site under `docs/` on each push to `main` via GitHub Actions, and GitHub Pages is configured to serve from `main` / `docs`.

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

- Add JSON Schema-based validation for `knowledge/`.
- Define course content conventions and templates.
- Introduce a docs site (e.g., MkDocs) with a simple navigation and deploy workflow.
