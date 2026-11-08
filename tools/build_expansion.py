"""Rebuild only the twelve 1.2 paths, preserving the original catalog."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    for filename in ("expansion_languages.py", "expansion_frameworks.py"):
        subprocess.run([sys.executable, str(ROOT / "tools" / filename)], cwd=ROOT, check=True)
    subprocess.run([sys.executable, str(ROOT / "tools/compile_catalog.py")], cwd=ROOT, check=True)
    subprocess.run([sys.executable, str(ROOT / "tools/audit_catalog.py")], cwd=ROOT, check=True)


if __name__ == "__main__":
    main()

