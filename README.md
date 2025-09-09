# SDIT Knowledge Base

A single repository for the San Diego Institute of Technology's curriculum and institutional knowledge.

- **Website:** https://sandiegotech.github.io/sdit/
- **Repository:** https://github.com/sandiegotech/sdit

## Repository structure

- `knowledge/` – YAML files describing identity, philosophies, programs, and more.
- `courses/` – one Markdown file per course plus a generated index.
- `programs/` – semester syllabi and schedules.
- `docs/` – generated static site served by GitHub Pages.
- `scripts/` – helper tools for validation and site generation.

## Working locally

```bash
# Install dependencies
pip install pyyaml markdown

# Validate YAML content
python scripts/validate.py

# Build the static site into docs/
python scripts/build_site.py --out docs
```

Any push to `main` builds the site and publishes the latest content to the GitHub Pages site.
