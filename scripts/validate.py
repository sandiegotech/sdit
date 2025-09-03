#!/usr/bin/env python3
# Minimal placeholder validator; extend with JSON Schema as you grow.
import sys, pathlib, yaml
from glob import glob

def load(p):
    with open(p, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

base = pathlib.Path(__file__).resolve().parents[1] / "knowledge"
files = glob(str(base / "*.yaml"))

ok = True
for f in files:
    try:
        data = load(f)
        if not isinstance(data, dict):
            raise ValueError("Top-level YAML must be a mapping")
    except Exception as e:
        ok = False
        print(f"[ERROR] {f}: {e}")

print("Validation:", "OK" if ok else "FAILED")
sys.exit(0 if ok else 1)
