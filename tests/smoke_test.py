from __future__ import annotations

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent.parent


def run_cmd(*args: str) -> None:
    cmd = [sys.executable, *args]
    subprocess.run(cmd, cwd=ROOT, check=True)


def main() -> int:
    run_cmd("build.py", "--data", "listings/451-heath.json", "--assets", "images", "--validate-only")
    run_cmd("tools/import_listing_csv.py", "--csv", "listings/sample-listing.csv", "--out", "listings/from-csv.json")
    run_cmd("build.py", "--data", "listings/from-csv.json", "--assets", "images", "--out", "tests/out")
    print("Smoke tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
