#!/usr/bin/env python3
"""
SDIT local development server.

Usage:
    python3 serve.py

Opens the site at http://localhost:3001 and saves student responses to their
source .md files. Rebuilds HTML and pushes to GitHub after each save.
"""

import http.server
import json
import os
import re
import subprocess
import sys
import threading
import urllib.parse
import webbrowser
from pathlib import Path

PORT = 3001
ROOT = Path(__file__).parent.resolve()


# ── Helpers ───────────────────────────────────────────────────────────────────

def rebuild():
    """Run the build script in the background."""
    try:
        subprocess.run(
            [sys.executable, "scripts/build_site.py", "--out", "."],
            cwd=ROOT,
            capture_output=True,
        )
    except Exception as e:
        print(f"  rebuild error: {e}")


def git_push(message="Update student work"):
    """Stage, commit, and push all changes."""
    try:
        subprocess.run(["git", "add", "."], cwd=ROOT, capture_output=True)
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=ROOT,
        )
        if result.returncode != 0:  # there are staged changes
            subprocess.run(
                ["git", "commit", "-m", message],
                cwd=ROOT,
                capture_output=True,
            )
            subprocess.run(
                ["git", "push"],
                cwd=ROOT,
                capture_output=True,
            )
            print(f"  pushed: {message}")
    except Exception as e:
        print(f"  git error: {e}")


def save_response(md_file: str, heading: str, content: str) -> dict:
    """
    Write student response into the correct ### heading block in a .md file.

    The heading must exist under ## My Work. If the heading is not found,
    returns an error. Content replaces everything between the heading and
    the next heading (or end of file).
    """
    path = ROOT / md_file.lstrip("/")
    if not path.resolve().is_relative_to(ROOT):
        return {"ok": False, "error": "Invalid path"}
    if not path.exists():
        return {"ok": False, "error": f"File not found: {md_file}"}

    text = path.read_text(encoding="utf-8")

    # Locate the ### heading inside ## My Work
    # We look for "### {heading}" (case-insensitive match)
    pattern = re.compile(
        r"(### " + re.escape(heading) + r"\s*\n)"  # the heading line
        r"(.*?)"                                     # existing content
        r"(?=\n### |\n## |\Z)",                      # up to next heading or EOF
        re.DOTALL | re.IGNORECASE,
    )
    m = pattern.search(text)
    if not m:
        return {"ok": False, "error": f"Heading '### {heading}' not found in My Work"}

    replacement = m.group(1) + "\n" + content.strip() + "\n"
    new_text = text[: m.start()] + replacement + text[m.end() :]
    path.write_text(new_text, encoding="utf-8")
    return {"ok": True}


# ── Request handler ───────────────────────────────────────────────────────────

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, fmt, *args):
        # Only print GETs for HTML pages and errors; skip assets
        if self.command == "POST" or (
            self.command == "GET"
            and (args[1] not in ("200", "304") or args[0].endswith(".html"))
        ):
            super().log_message(fmt, *args)

    def do_POST(self):
        if self.path != "/api/save":
            self.send_error(404)
            return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            data = json.loads(body)
        except Exception:
            self.send_error(400, "Bad JSON")
            return

        md_file = data.get("file", "")
        heading = data.get("heading", "")
        content = data.get("content", "")

        if not md_file or not heading:
            self.send_error(400, "Missing file or heading")
            return

        result = save_response(md_file, heading, content)

        if result["ok"]:
            print(f"  saved  {md_file} → ### {heading}")
            # Rebuild + push in background so the response is instant
            threading.Thread(target=lambda: (rebuild(), git_push(f"Update: {heading}")), daemon=True).start()

        resp = json.dumps(result).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(resp)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.rfile  # flush
        self.wfile.write(resp)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def guess_type(self, path):
        # Ensure .md files are served as plain text if ever fetched directly
        if str(path).endswith(".md"):
            return "text/plain; charset=utf-8"
        return super().guess_type(path)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    server = http.server.HTTPServer(("", PORT), Handler)
    url = f"http://localhost:{PORT}/index.html"
    print(f"\n  SDIT local server")
    print(f"  {url}\n")
    threading.Timer(0.5, webbrowser.open, args=(url,)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  stopped.")
