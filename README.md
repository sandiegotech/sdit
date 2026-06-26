# SDIT Open Curriculum

An open-source liberal arts curriculum you can take yourself, fork to your own GitHub, and build on.

- Website: https://sandiegotech.github.io/sdit/
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

5. **Push to GitHub** — the server saves and pushes in the background after each response. Or push manually:
   ```bash
   git push
   ```

6. **Enable GitHub Pages** in your repo settings (Settings → Pages → Deploy from branch → main) and your site will be live at `https://YOUR-USERNAME.github.io/sdit/`.

### How responses are saved

When you type in a My Work field:
- Your response saves to **localStorage** instantly (survives page refresh)
- On `localhost`, it also writes back to the source `.md` file and triggers a `git push`
- On GitHub Pages (published site), it saves to localStorage only — visible to you in the browser

### Where lesson files live

Every course has its own directory:

```
courses/LBS-101/day-01.md    ← Day 1 of The Mental Gym
courses/LBS-105/day-03.md    ← Day 3 of Writing & Communication
courses/LBS-110/day-07.md    ← Day 7 of Mathematics for Modern Thinkers
...
```

Each file has a `## My Work` section at the bottom where your responses go. The `serve.py` server writes your browser input directly into these files.

---

## What This Repo Contains

```
courses/           Course library — each course owns its day files (source of truth)
programs/          Degree programs assembled from the course library
knowledge/         Institutional YAML reference files
assets/            Styles (site.css) and JavaScript (layout.js, student-work.js)
partials/          Shared site header and footer (loaded dynamically)
scripts/           Build script (build_site.py)
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
