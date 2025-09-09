#!/usr/bin/env python3
"""
Generate the nested Programs tree (Volumes → Chapters → Sections) for
Bachelor-Liberal-Arts and inject it into index.html between markers:
  <!-- PROGRAMS_TREE_START --> ... <!-- PROGRAMS_TREE_END -->

It links to the rendered HTML pages under programs/ so ensure you run:
  python scripts/build_site.py --out .
before this script to keep links valid.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "programs" / "Bachelor-Liberal-Arts"
INDEX_HTML = ROOT / "index.html"


def vol_key(p: Path) -> tuple[int, str]:
    m = re.search(r"vol-(\d+)", p.name)
    n = int(m.group(1)) if m else 0
    return (n, p.name)


def chap_key(p: Path) -> int:
    m = re.search(r"chapter-(\d+)$", p.name)
    return int(m.group(1)) if m else 0


def sect_key(p: Path) -> int:
    m = re.search(r"section-(\d+)$", p.stem)
    return int(m.group(1)) if m else 0


def labelize(name: str) -> str:
    name = name.replace("-", " ")
    parts = name.split()
    if len(parts) >= 2 and parts[0] == "vol" and parts[1].isdigit():
        parts[1] = f"{int(parts[1]):02d}"
    if len(parts) >= 2 and parts[0] == "chapter" and parts[1].isdigit():
        parts[1] = f"{int(parts[1]):02d}"
    return " ".join(w.capitalize() for w in parts)


def strip_tags(html: str) -> str:
    # Remove tags
    text = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.I)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_preview(section_html_path: Path, max_chars: int = 320) -> str:
    try:
        s = section_html_path.read_text(encoding="utf-8")
    except Exception:
        return ""
    m = re.search(r"<main>([\s\S]*?)</main>", s, flags=re.I)
    body = m.group(1) if m else s
    text = strip_tags(body)
    if len(text) > max_chars:
        text = text[:max_chars].rstrip() + "…"
    return text


def build_tree() -> str:
    if not BASE.exists():
        return "<p><em>No programs found.</em></p>"

    out: list[str] = []
    # Render only volumes as top-level dropdowns (no Programs/Bachelor wrappers)

    vol_dirs = sorted([p for p in BASE.glob("vol-*") if p.is_dir()], key=vol_key)
    blocks: list[str] = []
    for vol in vol_dirs:
        vol_label = labelize(vol.name)
        vol_index = (vol / "syllabus.html").relative_to(ROOT).as_posix()
        vol_block: list[str] = []
        vol_block.append(f"<details><summary>{vol_label} <a class='view' href='{vol_index}'>View</a></summary>")
        # Chapters
        sched = vol / "schedule"
        if sched.exists():
            chaps = sorted([p for p in sched.glob("chapter-*") if p.is_dir()], key=chap_key)
            if chaps:
                vol_block.append("<ul>")
                for chap in chaps:
                    chap_label = labelize(chap.name)
                    chap_index = (chap / "index.html").relative_to(ROOT).as_posix()
                    vol_block.append(f"<li><details><summary>{chap_label} <a class='view' href='{chap_index}'>View</a></summary>")
                    # Sections
                    secs = sorted(chap.glob("section-*.html"), key=sect_key)
                    if secs:
                        vol_block.append("<ul>")
                        for sec in secs:
                            sec_num = sect_key(sec)
                            sec_label = f"Section {sec_num:02d}"
                            preview = extract_preview(sec)
                            if preview:
                                vol_block.append(f"<li><a href='{sec.relative_to(ROOT).as_posix()}'>{sec_label}</a><div class='preview'>{preview}</div></li>")
                            else:
                                vol_block.append(f"<li><a href='{sec.relative_to(ROOT).as_posix()}'>{sec_label}</a></li>")
                        vol_block.append("</ul>")
                    vol_block.append("</details></li>")
                vol_block.append("</ul>")
        vol_block.append("</details>")
        blocks.append("\n".join(vol_block))

    return "\n".join(blocks)


def inject_into_index(html_block: str) -> None:
    content = INDEX_HTML.read_text(encoding="utf-8")
    start = "<!-- PROGRAMS_TREE_START"
    end = "PROGRAMS_TREE_END -->"
    sidx = content.find(start)
    eidx = content.find(end)
    if sidx == -1 or eidx == -1:
        raise SystemExit("Markers not found in index.html")
    eidx += len(end)
    new = content[:sidx] + f"<!-- PROGRAMS_TREE_START (auto-generated) -->\n" + html_block + "\n" + content[eidx:]
    INDEX_HTML.write_text(new, encoding="utf-8")


def main() -> int:
    html = build_tree()
    inject_into_index(html)
    print("Updated index.html with Programs tree")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
