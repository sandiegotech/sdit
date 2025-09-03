# SDIT Knowledge Base

Authoritative, versioned source for San Diego Institute of Technology (SDIT) identity, strategy, programs, and public-facing content. The goal is to keep information organized, human-readable, and easy to validate.

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

- `courses/`: Core volumes and electives organized simply as:
  - For core: `core/vol-XX/` with `syllabus.md`, `courses/` (one file per course), and `schedule/` (daily summary and one file per week). No module subfolders.
  - For electives: one file per field book.

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

## Courses (`courses/`)

Keep course content simple: one page per course; schedules use daily or weekly pages. Avoid nested module folders.

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
