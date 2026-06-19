import sys
from pathlib import Path

# Make the scripts/ modules importable as top-level (frontmatter, catalog, validate).
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
