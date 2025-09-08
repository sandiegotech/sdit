#!/usr/bin/env python3
"""
Assemble Volume 01 (Foundations) schedule sections into a single text/markdown file
in chronological order.

Usage:
  python scripts/build_vol01_book.py
  python scripts/build_vol01_book.py --output dist/vol-01-foundations.md

By default, writes to dist/vol-01-foundations-full-semester.md
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
SCHEDULE_DIR = ROOT / "programs" / "Bachelor-Liberal-Arts" / "vol-01-foundations" / "schedule"


def strip_front_matter(text: str) -> tuple[str, dict]:
    """Remove YAML front matter delimited by '---' at the start of the file.
    Returns (content_without_front_matter, meta_dict_like) where meta contains
    a few common keys parsed from simple `key: value` pairs if present.
    """
    if not text.startswith("---\n"):
        return text, {}

    # Find the end of front matter
    end = text.find("\n---\n", 4)
    if end == -1:
        # Malformed front matter; return original
        return text, {}

    fm = text[4:end]  # content between the leading and trailing --- lines
    body = text[end + 5 :]

    meta: dict[str, str | int] = {}
    # Simple key: value parser (no nested structures)
    for line in fm.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        key = key.strip()
        val = val.strip().strip('"')
        # try to coerce numbers
        if re.fullmatch(r"\d+", val):
            try:
                meta[key] = int(val)
                continue
            except Exception:
                pass
        meta[key] = val
    return body.lstrip(), meta


def find_chapter_dirs() -> list[Path]:
    if not SCHEDULE_DIR.exists():
        print(f"Error: schedule directory not found: {SCHEDULE_DIR}", file=sys.stderr)
        sys.exit(1)
    chapters = [p for p in SCHEDULE_DIR.iterdir() if p.is_dir() and p.name.startswith("chapter-")]
    # Sort by numeric suffix if present
    def chapter_key(p: Path):
        m = re.search(r"(\d+)$", p.name)
        return int(m.group(1)) if m else p.name

    return sorted(chapters, key=chapter_key)


def find_section_files(chapter_dir: Path) -> list[Path]:
    sections = [p for p in chapter_dir.iterdir() if p.is_file() and p.name.startswith("section-") and p.suffix == ".md"]

    def section_key(p: Path):
        m = re.search(r"(\d+)", p.stem)
        return int(m.group(1)) if m else p.name

    return sorted(sections, key=section_key)


def _assemble_markdown() -> str:
    """Return the compiled Markdown content for the full semester."""
    pieces: list[str] = []

    header = (
        "# Volume 01 — Foundations: Full Semester\n\n"
        "This file concatenates every section in chronological order from\n"
        "`programs/Bachelor-Liberal-Arts/vol-01-foundations/schedule`.\n\n"
    )
    pieces.append(header)

    for chapter_dir in find_chapter_dirs():
        # Extract chapter number for section header
        m = re.search(r"(\d+)$", chapter_dir.name)
        chapter_num = int(m.group(1)) if m else chapter_dir.name

        chapter_header = f"\n\n---\n\n## Chapter {int(chapter_num):02d}\n\n"
        pieces.append(chapter_header)

        for section_file in find_section_files(chapter_dir):
            raw = section_file.read_text(encoding="utf-8")
            body, _meta = strip_front_matter(raw)
            # Add a spacer between sections for readability; rely on the section's own H1
            pieces.append("\n")
            pieces.append(body.strip())
            pieces.append("\n")

    content = "".join(pieces).rstrip() + "\n"
    return content


def _has_pandoc() -> bool:
    return shutil.which("pandoc") is not None


def _inject_pagebreaks_for_docx(md_text: str) -> str:
    """Insert hard page breaks in Markdown so pandoc outputs pages in DOCX.

    Rules:
    - Before each new section heading (lines starting with `# Section`), except the first.
    - Before each `## Practice` section so Practice starts on a new page.

    Pandoc treats a form feed character (\f) on its own line as a page break
    in DOCX/ODT. We ensure it's on a dedicated line with surrounding newlines.
    """
    lines = md_text.splitlines()
    out: list[str] = []
    seen_first_section = False

    def prev_nonempty_is_break() -> bool:
        # Check if the last non-empty emitted line is a form feed
        for i in range(len(out) - 1, -1, -1):
            if out[i].strip() == "":
                continue
            return out[i].strip() == "\f"
        return False

    for raw in lines:
        line = raw.rstrip("\n")
        stripped = line.lstrip()

        # Insert a page break before subsequent Section headers
        if stripped.startswith("# Section "):
            if seen_first_section:
                if not prev_nonempty_is_break():
                    # Blank line, break, blank line
                    if len(out) and out[-1].strip() != "":
                        out.append("")
                    out.append("\f")
                    out.append("")
            seen_first_section = True
            out.append(line)
            continue

        # Insert a page break before Practice sections
        if stripped.startswith("## Practice"):
            if not prev_nonempty_is_break():
                if len(out) and out[-1].strip() != "":
                    out.append("")
                out.append("\f")
                out.append("")
            out.append(line)
            continue

        out.append(line)

    return "\n".join(out) + "\n"


def _convert_markdown_to_docx(md_text: str, output: Path) -> None:
    """Convert markdown to DOCX using pandoc. Attempts to use pypandoc and
    download pandoc if not available on the system.
    """
    output.parent.mkdir(parents=True, exist_ok=True)
    # Prefer system pandoc if available
    if _has_pandoc():
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as tmp:
            tmp.write(md_text)
            tmp_path = tmp.name
        try:
            subprocess.run([
                "pandoc",
                tmp_path,
                "-f","markdown",
                "-t","docx",
                "-o", str(output),
            ], check=True)
        finally:
            try:
                Path(tmp_path).unlink(missing_ok=True)
            except Exception:
                pass
        return

    # Fallback: use pypandoc and download pandoc binary if needed
    try:
        import pypandoc  # type: ignore
    except Exception:
        subprocess.run([sys.executable, "-m", "pip", "install", "pypandoc"], check=True)
        import pypandoc  # type: ignore

    try:
        # Ensure pandoc is available; this downloads if missing
        try:
            pypandoc.get_pandoc_path()
        except OSError:
            pypandoc.download_pandoc()
        pypandoc.convert_text(md_text, to="docx", format="md", outputfile=str(output))
    except Exception as e:
        raise RuntimeError(
            "Pandoc is required to export DOCX. Tried system pandoc and pypandoc; "
            f"conversion failed: {e}"
        )


def build(output: Path) -> None:
    md = _assemble_markdown()
    ext = output.suffix.lower()
    if ext in {".docx"}:
        md_docx = _inject_pagebreaks_for_docx(md)
        _convert_markdown_to_docx(md_docx, output)
        try:
            shown = output.resolve().relative_to(ROOT)
        except Exception:
            shown = output
        print(f"Wrote {shown} (DOCX)")
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(md, encoding="utf-8")
        try:
            shown = output.resolve().relative_to(ROOT)
        except Exception:
            shown = output
        print(f"Wrote {shown} (chars: {len(md):,})")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build Volume 01 (Foundations) full-semester content file")
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=ROOT / "dist" / "vol-01-foundations-full-semester.md",
        help="Output file path (default: dist/vol-01-foundations-full-semester.md)",
    )
    args = parser.parse_args(argv)

    build(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
