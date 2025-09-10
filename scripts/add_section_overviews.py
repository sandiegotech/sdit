#!/usr/bin/env python3
"""Add description field and Overview section to all section Markdown files."""
from __future__ import annotations

import re
from pathlib import Path

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None

ROOT = Path(__file__).resolve().parents[1]
SECTIONS = sorted(ROOT.glob("programs/Bachelor-Liberal-Arts/vol-01-foundations/schedule/chapter-*/section-*.md"))

def desc_from_title(title: str) -> str:
    parts = re.split(r"\s[—–-]\s", title, maxsplit=1)
    desc = parts[1] if len(parts) > 1 else title
    desc = re.sub(r"\s*\([^)]*\)\s*", "", desc).strip()
    return desc

def load_yaml(block: str) -> dict:
    if yaml is not None:
        try:
            data = yaml.safe_load(block) or {}
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}
    data: dict[str, str] = {}
    for line in block.splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        data[k.strip()] = v.strip().strip('"')
    return data

def dump_yaml(data: dict) -> str:
    if yaml is not None:
        return yaml.safe_dump(data, sort_keys=False).strip()
    return "\n".join(f"{k}: {v}" for k, v in data.items())

for path in SECTIONS:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        continue
    fm_end = text.find("\n---", 3)
    if fm_end == -1:
        continue
    fm_block = text[3:fm_end].strip()
    body = text[fm_end + 4:]
    data = load_yaml(fm_block)
    title = data.get("title", "")
    desc = data.get("description") or desc_from_title(title)
    data.setdefault("description", desc)
    # ensure Overview section exists
    if "## Overview" not in body:
        lines = body.splitlines()
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.strip().startswith("Course"):
                insert_idx = i + 1
                break
        overview_block = ["", "## Overview", desc, ""]
        lines[insert_idx:insert_idx] = overview_block
        body = "\n".join(lines)
    new_fm = "---\n" + dump_yaml(data) + "\n---\n"
    path.write_text(new_fm + body, encoding="utf-8")
