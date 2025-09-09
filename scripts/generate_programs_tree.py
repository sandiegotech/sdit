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


def build_tree() -> str:
    if not BASE.exists():
        return "<p><em>No programs found.</em></p>"

    out: list[str] = []
    out.append("<details class='root' open><summary>Programs</summary>")
    out.append("<ul>")
    out.append("<li><details><summary>Bachelor Liberal Arts</summary>")
    out.append("<ul>")

    vol_dirs = sorted([p for p in BASE.glob("vol-*") if p.is_dir()], key=vol_key)
    for vol in vol_dirs:
        vol_label = labelize(vol.name)
        vol_index = (vol / "syllabus.html").as_posix()
        out.append(f"<li><details><summary>{vol_label} <a class='view' href='{vol_index}'>View</a></summary>")
        # Chapters
        sched = vol / "schedule"
        if sched.exists():
            chaps = sorted([p for p in sched.glob("chapter-*") if p.is_dir()], key=chap_key)
            if chaps:
                out.append("<ul>")
                for chap in chaps:
                    chap_label = labelize(chap.name)
                    chap_index = (chap / "index.html").as_posix()
                    out.append(f"<li><details><summary>{chap_label} <a class='view' href='{chap_index}'>View</a></summary>")
                    # Sections
                    secs = sorted(chap.glob("section-*.html"), key=sect_key)
                    if secs:
                        out.append("<ul>")
                        for sec in secs:
                            sec_num = sect_key(sec)
                            sec_label = f"Section {sec_num:02d}"
                            out.append(f"<li><a href='{sec.as_posix()}'>{sec_label}</a></li>")
                        out.append("</ul>")
                    out.append("</details></li>")
                out.append("</ul>")
        out.append("</details></li>")

    out.append("</ul>")
    out.append("</details>")
    return "\n".join(out)


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

