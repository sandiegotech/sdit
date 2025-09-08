# Knowledge Data

The `knowledge/` folder contains small, canonical YAML maps that define SDIT’s identity, principles, programs, and research. These files are meant to be stable “single sources of truth” that copy can reference and future tooling can read.

Each file now includes a top-level `__meta__` block with a short description and intended use. Keep records concise and public‑safe; avoid sensitive details.

## What’s Essential vs. Optional

- Essential: `identity.yaml`, `anchors.yaml`, `philosophies.yaml`, `programs.yaml`, `courses.yaml`, `research.yaml`
- Optional/Contextual: `projects.yaml` (index view), `community.yaml` (when fellowships/events go live), `priorities.yaml` (internal planning), `infrastructure.yaml` (ops reference)

## Files

- `knowledge/identity.yaml`: Canonical org identity (name, mission, tagline, positioning). Powers About/landing copy and sets tone.
- `knowledge/anchors.yaml`: Strategic anchors (enduring pillars for decisions/messaging). Use for consistent framing across docs and projects.
- `knowledge/philosophies.yaml`: Educational and cultural principles. Guides curriculum design, editorial voice, and tradeoffs.
- `knowledge/programs.yaml`: Official programs, tracks, and labs with stable IDs. Cross‑link to courses/modules.
- `knowledge/courses.yaml`: Master list of all courses (core and electives) with canonical paths and grouping; powers course indexes.
- `knowledge/research.yaml`: Research divisions and detailed project records with status. Use for research pages and roadmaps.
- `knowledge/projects.yaml`: Cross‑cutting, high‑level project index (education, research, culture). Keep brief; detail lives in `research.yaml`.
- `knowledge/community.yaml`: Fellowships, training rhythms, and local/affinity groups. Drives community pages and planning.
- `knowledge/priorities.yaml`: Near‑term execution list. Use for quarterly planning/status; keep short and current.
- `knowledge/infrastructure.yaml`: Operational footprint (digital, legal/financial, physical). Internal reference only.

## Conventions

- Top-level structure is always a mapping; stable IDs for anything referenced elsewhere.
- Prefer short, declarative phrases; this is structured data, not narrative.
- Keep `__meta__` up-to-date with a one‑line purpose and how the file is used.
- Public repo: only include sanitized, non‑sensitive information.

## Validation

Run `python scripts/validate.py` to sanity‑check that each YAML file is a mapping. Extend this script with schema checks as the data model matures.
