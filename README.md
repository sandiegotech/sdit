# SDIT Open Curriculum

An open-source liberal arts curriculum you can take yourself, fork to your own GitHub, and build on.

- Website: https://sandiegotech.github.io/sdit/
- Repository: https://github.com/sandiegotech/sdit

---

## For Students — Do the Work in Your Own Fork

The curriculum is designed to be taken, not just read. Fork this repo, write your answers directly in the lesson files, and your work lives on your GitHub — publicly or privately, as you choose.

### How it works

1. **Fork this repo** — click Fork in the top right on GitHub. This creates your own copy.

2. **Clone it to your computer**
   ```bash
   git clone https://github.com/YOUR-USERNAME/sdit.git
   cd sdit
   ```

3. **Open any lesson file and write your answers**

   Every lesson is a Markdown file at a path like:
   ```
   programs/Bachelor-Liberal-Arts/vol-01-foundations/schedule/chapter-01/section-01.md
   ```
   At the bottom of each lesson you'll find a `## My Work` section. Replace the placeholders with your actual responses.

4. **Push to your GitHub**
   ```bash
   git add .
   git commit -m "Day 1 complete"
   git push
   ```

5. **GitHub automatically rebuilds your site** — the HTML pages are regenerated from your updated markdown and pushed back to your repo within a minute or two.

6. **Enable GitHub Pages** in your repo settings (Settings → Pages → Deploy from branch → main) and your site will be live at `https://YOUR-USERNAME.github.io/sdit/`.

### What you edit

- **Lesson files** (`programs/.../section-NN.md`) — where you write your answers
- **Nothing else** — HTML files are generated automatically. Never edit them directly.

### What happens automatically

When you push to `main`, GitHub Actions runs the build script and commits the updated HTML. Your site reflects your latest work within about 60 seconds.

---

## What This Repo Contains

```
programs/          Degree pages, schedules, chapters, and daily lessons (.md = source)
courses/           Full course library with syllabi
knowledge/         Institutional YAML reference files
assets/            Styles (site.css) and JavaScript
partials/          Shared site header and footer (loaded dynamically)
scripts/           Build script (build_site.py) and validators
guides/            Student guides (AI setup, getting started)
```

### The source/generated split

| File type | Source of truth | Edit directly? |
|-----------|----------------|---------------|
| `*.md` in `programs/`, `courses/` | Yes — content source | Yes |
| `*.html` generated from `.md` | No — generated output | No |
| `index.html`, `programs/index.html`, manually maintained pages | Yes | Yes |
| `assets/site.css`, `assets/js/` | Yes | Yes |

The build script (`scripts/build_site.py`) converts markdown to HTML. Run it locally with:
```bash
python3 scripts/build_site.py --out .
```

---

## Run the Site Locally

The site uses shared partials loaded by the browser, so open it via a local server — not by opening files directly.

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000/`

---

## Contributing

Contributions are welcome across curriculum, writing, structure, and UI.

**Workflow:**
1. Fork and clone the repo
2. Make your change in a branch
3. Preview locally with `python3 -m http.server 8000`
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
