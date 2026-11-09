#!/usr/bin/env python3
"""Run repository installer tests and the skill regression suite without network."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
for folder in (ROOT / "tests", ROOT / "skills/shellferry/scripts/tests"):
    result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", str(folder), "-v"], cwd=ROOT)
    if result.returncode:
        raise SystemExit(result.returncode)
