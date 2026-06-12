# SDIT — The Curriculum

The open curriculum of the San Diego Institute of Technology — the learning site (learn.sandiegotech.org). The Institute itself, daily updates, and everything else live on the main site (sandiegotech.org); this repo is entirely for those who want to learn.

One degree framework — the **BA in Technology** (`curriculum/index.html`) — with a concentration declared at the end of Year 2 (`curriculum/four-years.html`):

- **Media** — things people watch, hear, and feel
- **Design** — things people use
- **Engineering** — things that work on their own

Years 1–2 are the Foundation, identical for everyone — the artist learns engineering, the engineer learns art — and the whole catalog is roughly forty courses; eight depth studios, shared across overlapping concentration lists, carry the focus. Every course is built to one standard: it ends in a made thing, and it ships day by day.

- Website: https://learn.sandiegotech.org
- Main site: https://www.sandiegotech.org
- Repository: https://github.com/sandiegotech/sdit

---

## For Students — Do the Work in Your Own Fork

The curriculum is designed to be taken, not just read. Fork this repo, run the local server, write your answers in the browser, and your work saves back to your files and syncs to your GitHub automatically.

### Quick Start

1. **Fork this repo** — click Fork in the top right on GitHub.

2. **Clone it to your computer**
   ```bash
   git clone https://github.com/YOUR-USERNAME/sdit.git
   cd sdit
   ```

3. **Start the local server**
   ```bash
   python3 serve.py
   ```
   Your browser will open at `http://localhost:3001`. That's all you need.

4. **Do the work** — navigate to any lesson, scroll to **My Work**, and type your responses directly in the page. They save automatically.

5. **Push to GitHub** — run the server with `python3 serve.py --push` to auto-commit and push each response, or push manually whenever you like:
   ```bash
   git push
   ```

6. **Enable GitHub Pages** in your repo settings (Settings → Pages → Deploy from branch → main) and your site will be live at `https://YOUR-USERNAME.github.io/sdit/`.

### How responses are saved

When you type in a response field:
- Your response saves to **localStorage** instantly (survives page refresh)
- On `localhost`, it also writes to a markdown file under `my-work/` (and auto-pushes if the server was started with `--push`)
- On GitHub Pages (published site), it saves to localStorage only — visible to you in the browser
- The site also remembers your **last lesson** on each device and offers to continue from it on the homepage

### Where lesson files live

Every course has its own directory:

```
courses/HUM-101/day-01.md    ← Day 1 of The Ancient World
courses/MATH-110/day-01.md   ← Day 1 of The Mathematics of Motion
courses/CS-110/day-01.md     ← Day 1 of Speaking to Machines
...
```

Each file has a `## My Work` section at the bottom where your responses go. The `serve.py` server writes your browser input directly into these files.

---

## What This Repo Contains

```
curriculum/        The Curriculum — degree requirements, the four-years map, the schedule
courses/           The catalog — each course owns its day files (source of truth)
institute/         Founding documents — The Plan, The Degree
knowledge/         Institutional YAML reference files (degree, catalog, outcomes, identity, programs)
accreditation.html Where authorization stands, stated plainly
downloads/         Generated PDFs (degree map, the Nine Laws)
assets/            Styles (site.css, charter design system) and JavaScript
partials/          Shared masthead header and colophon footer (loaded dynamically)
scripts/           Build & scaffold scripts (build_site.py, scaffold_catalog.py, validate.py)
serve.py           Local development server with student response saving
```

### The source/generated split

| File type | Source of truth | Edit directly? |
|-----------|----------------|---------------|
| `*.md` in `courses/` | Yes — content source | Yes |
| `*.html` generated from `.md` | No — generated output | No |
| `index.html`, manually maintained pages | Yes | Yes |
| `assets/site.css`, `assets/js/` | Yes | Yes |

The build script (`scripts/build_site.py`) converts Markdown to HTML. `serve.py` runs it automatically. To run it manually:
```bash
python3 scripts/build_site.py --out .
```

### The course registry

`knowledge/catalog.yaml` is the single source of truth for the catalog's structure — every course's code, registers, outcomes, and status. `scripts/scaffold_catalog.py` generates a templated `courses/<CODE>/index.md` for any registry course that doesn't have one yet (it never overwrites). After scaffolding, the markdown is the live content source: write lessons as `courses/<CODE>/day-NN.md`, link them from the course's `index.md`, and rebuild.

---

## Run the Site Locally

```bash
python3 serve.py
```

Opens at `http://localhost:3001`. The server handles:
- Serving the static site
- Saving student responses to `.md` files
- Rebuilding HTML after each save
- Pushing to GitHub

---

## Contributing

Contributions are welcome across curriculum, writing, structure, and UI.

**Workflow:**
1. Fork and clone the repo
2. Make your change in a branch
3. Preview locally with `python3 serve.py`
4. Run `python3 scripts/build_site.py --out .` if you changed markdown
5. Open a pull request

**Keep contributions:**
- Clear and focused (one thing per PR)
- Consistent with existing lesson style
- Using stable, public links for external resources

**Good first contributions:**
- Fix broken links in lessons
- Improve unclear lesson instructions
- Add better course descriptions
- Clean up mobile layout issues
- Improve accessibility

---

## Questions

Open an issue or start a discussion on GitHub.
