# SDIT Open Curriculum

Open-source curriculum and website for the San Diego Institute of Technology.

This repository publishes a structured academic program that people can read online, move through day by day, and improve in the open. The main program is a four-year Bachelor of Liberal Arts organized by year, volume, chapter, and daily lesson.

- Website: https://sandiegotech.github.io/sdit/
- Repository: https://github.com/sandiegotech/sdit
- Main site: https://sandiegotech.org

## What This Repo Contains

- `index.html`
  Main landing page for the curriculum site.

- `programs/`
  Degree pages, semester volumes, syllabi, schedules, chapters, and daily lessons.

- `courses/`
  The broader course library outside the day-by-day program flow.

- `knowledge/`
  Structured YAML files for institutional identity, programs, research, and related reference material.

- `assets/`
  Shared styles, JavaScript, and brand assets.

- `partials/`
  Shared site header and footer.

- `scripts/`
  Small utility scripts for validation and site generation.

## Current Focus

The main published path is the Bachelor of Liberal Arts.

- 4-year degree structure
- 8 semester volumes
- Volume 1 published as a complete day-by-day sequence
- Additional volumes, course pages, and supporting materials in progress

## Run The Site Locally

Because the site uses shared partials loaded in the browser, use a local server instead of opening files directly.

1. From the repo root, start a local server:

```bash
python3 -m http.server 8000
```

2. Open:

```text
http://localhost:8000/
```

3. If you change YAML files in `knowledge/`, run:

```bash
python3 scripts/validate.py
```

## How To Contribute

Contributions are welcome across curriculum, writing, structure, and UI.

You can help by:

- improving lesson pages
- fixing typos, broken links, or unclear wording
- expanding syllabi or course pages
- improving navigation and layout
- cleaning up styling and component consistency
- organizing knowledge base content

## Contribution Workflow

1. Create a branch for your change.
2. Make a focused update.
3. Preview the site locally.
4. Run `python3 scripts/validate.py` if you changed anything in `knowledge/`.
5. Open a pull request with a short summary of what changed and why.

## Curriculum Contribution Notes

When contributing to the curriculum, keep the work:

- clear
- academically serious
- easy to navigate
- consistent with the rest of the site

If you edit a lesson or course that has both Markdown and HTML versions checked into the repo, keep both aligned unless you are intentionally changing the source workflow.

When adding outside resources:

- prefer stable public links
- avoid dead or paywalled sources when possible
- make sure the resource clearly supports the lesson

## Good First Contributions

- fix broken links in lessons or course pages
- improve unclear lesson instructions
- tighten page layout on mobile
- improve the course library and program navigation
- add better descriptions to syllabus and course pages
- clean up inconsistent formatting between related pages

## Pull Request Expectations

Keep pull requests small and easy to review.

A good pull request usually includes:

- a short summary
- the files changed
- the reason for the change
- screenshots for UI edits when helpful

## Notes

- Do not commit secrets or private data.
- Keep institutional and curriculum content public-safe.
- Prefer small, clear edits over large unfocused rewrites.

## Questions

If you want to contribute but do not know where to start, open an issue or submit a small cleanup PR first. Curriculum clarity, navigation, and content quality are all useful contributions.
