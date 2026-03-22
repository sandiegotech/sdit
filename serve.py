#!/usr/bin/env python3
"""
SDIT local development server.

Usage:
    python3 serve.py   (or  ./serve.py)

Opens the site at http://localhost:3001. Student responses are saved to the
my-work/ directory, rebuilt to HTML, and pushed to GitHub automatically.
"""

import http.server
import json
import re
import subprocess
import sys
import threading
import urllib.parse
import webbrowser
from pathlib import Path

PORT = 3001
ROOT = Path(__file__).parent.resolve()
MY_WORK = ROOT / "my-work"


# ── my-work/ helpers ──────────────────────────────────────────────────────────

def work_path(file_path: str) -> Path:
    """
    Derive the my-work/ save path from a URL path.
    /courses/LBS-101/day-01.html  →  my-work/courses/LBS-101/day-01.md
    """
    clean = file_path.lstrip("/")
    clean = re.sub(r"\.(html|md)$", "", clean)
    return MY_WORK / (clean + ".md")


def load_responses(file_path: str) -> dict:
    """Return {heading: content} for a lesson's saved responses."""
    path = work_path(file_path)
    if not path.exists():
        return {}

    text = path.read_text(encoding="utf-8")
    result = {}
    current_heading = None
    current_lines = []

    for line in text.splitlines():
        if line.startswith("### "):
            if current_heading is not None:
                result[current_heading] = "\n".join(current_lines).strip()
            current_heading = line[4:].strip()
            current_lines = []
        elif current_heading is not None and line != "---":
            current_lines.append(line)

    if current_heading is not None:
        result[current_heading] = "\n".join(current_lines).strip()

    return result


def save_response(file_path: str, heading: str, content: str) -> dict:
    """Write or update a response block in my-work/."""
    path = work_path(file_path)
    if not path.resolve().is_relative_to(ROOT):
        return {"ok": False, "error": "Invalid path"}

    path.parent.mkdir(parents=True, exist_ok=True)
    text = path.read_text(encoding="utf-8") if path.exists() else ""

    new_block = f"### {heading}\n\n{content.strip()}\n\n---\n\n"

    # Replace existing block if heading found, otherwise append
    pattern = re.compile(
        r"### " + re.escape(heading) + r"\n\n.*?(?=\n### |\Z)",
        re.DOTALL,
    )
    m = pattern.search(text)
    if m:
        new_text = text[: m.start()] + new_block.rstrip() + text[m.end() :]
    else:
        new_text = text + new_block

    path.write_text(new_text.strip() + "\n", encoding="utf-8")
    return {"ok": True}


# ── Build + push ──────────────────────────────────────────────────────────────

def rebuild():
    try:
        subprocess.run(
            [sys.executable, "scripts/build_site.py", "--out", "."],
            cwd=ROOT, capture_output=True,
        )
    except Exception as e:
        print(f"  rebuild error: {e}")


def git_push(message="Update student work"):
    try:
        subprocess.run(["git", "add", "."], cwd=ROOT, capture_output=True)
        r = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT)
        if r.returncode != 0:
            subprocess.run(["git", "commit", "-m", message], cwd=ROOT, capture_output=True)
            subprocess.run(["git", "push"], cwd=ROOT, capture_output=True)
            print(f"  pushed: {message}")
    except Exception as e:
        print(f"  git error: {e}")


# ── Request handler ───────────────────────────────────────────────────────────

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, fmt, *args):
        if self.command == "POST" or (
            self.command == "GET"
            and (args[1] not in ("200", "304") or args[0].endswith(".html"))
        ):
            super().log_message(fmt, *args)

    def send_json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        # Intercept /api/load — everything else is static files
        if self.path.startswith("/api/load"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            file_path = (params.get("file") or [""])[0]
            if not file_path:
                self.send_json({"error": "Missing file param"}, 400)
                return
            self.send_json(load_responses(file_path))
            return
        super().do_GET()

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

        file_path = data.get("file", "")
        heading   = data.get("heading", "")
        content   = data.get("content", "")

        if not file_path or not heading:
            self.send_error(400, "Missing file or heading")
            return

        result = save_response(file_path, heading, content)
        if result["ok"]:
            print(f"  saved  {file_path} → {heading}")
            threading.Thread(
                target=lambda: (rebuild(), git_push(f"Response: {heading}")),
                daemon=True,
            ).start()

        self.send_json(result)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def guess_type(self, path):
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
