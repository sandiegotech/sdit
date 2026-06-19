#!/usr/bin/env python3
"""Run the scripts/ tests without pytest (CI uses pytest; this is for local use).

    python3 scripts/tests/run_tests.py
"""
import sys
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))  # scripts/
sys.path.insert(0, str(HERE))         # tests/

import test_frontmatter
import test_catalog
import test_validate

passed = failed = 0
for module in (test_frontmatter, test_catalog, test_validate):
    for name in sorted(dir(module)):
        if not name.startswith("test_"):
            continue
        fn = getattr(module, name)
        if not callable(fn):
            continue
        try:
            fn()
            passed += 1
            print(f"  PASS  {module.__name__}.{name}")
        except Exception:
            failed += 1
            print(f"  FAIL  {module.__name__}.{name}")
            traceback.print_exc()

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
