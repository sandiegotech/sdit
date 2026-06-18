#!/usr/bin/env python3
"""frontmatter.py — the one front-matter parser for the build.

    parse(text) -> (meta: dict, body: str)

YAML front matter is delimited by leading '---' lines. A real YAML parser is
used when available, with a simple `key: value` reader as a fallback. When
there is no front matter, returns ({}, text) unchanged.
"""
from __future__ import annotations


def parse(text: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    fm = text[4:end]
    body = text[end + 5:].lstrip()

    try:
        import yaml  # type: ignore

        data = yaml.safe_load(fm) or {}
        if isinstance(data, dict):
            return data, body
    except Exception:
        pass

    meta: dict[str, str] = {}
    for line in fm.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, val = line.split(":", 1)
        meta[key.strip()] = val.strip().strip('"')
    return meta, body
