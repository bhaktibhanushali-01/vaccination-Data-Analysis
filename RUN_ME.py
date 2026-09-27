"""
RUN_ME.py
----------
Single entry point for the whole project. Run this one file and it will:
  1. Check the raw Excel files are present
  2. Clean the data
  3. Build the SQL database
  4. Export the Power BI-ready CSVs

Works no matter which folder you run it from (it finds its own location
automatically), so you can double-click it or run `python RUN_ME.py` from
anywhere inside the project.

Usage:
    python RUN_ME.py
"""

import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data" / "raw"
SCRIPTS = ROOT / "scripts"

REQUIRED_FILES = [
    "coverage-data.xlsx",
    "incidence-rate-data.xlsx",
    "reported-cases-data.xlsx",
    "vaccine-introduction-data.xlsx",
    "vaccine-schedule-data.xlsx",
]


def check_raw_files():
    print("Step 0: checking raw data files...")
    missing = [f for f in REQUIRED_FILES if not (RAW / f).exists()]
    if missing:
        print("\n *** STOP: the following files are missing from data/raw/ ***")
        for f in missing:
            print(f"   - {f}")
        print(f"\nExpected folder: {RAW}")
        print("Make sure the project was extracted fully (not just some files),")
        print("and that these 5 Excel files are sitting directly inside data/raw/.")
        sys.exit(1)
    print("  All 5 raw files found. Good to go.\n")


def run_step(script_name, description):
    print(f"--- {description} ---")
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / script_name)],
        cwd=str(SCRIPTS),
    )
    if result.returncode != 0:
        print(f"\n *** STOP: {script_name} failed (see error above) ***")
        sys.exit(1)
    print()


if __name__ == "__main__":
    print("=" * 60)
    print("Vaccination Data Analysis -- full pipeline")
    print("=" * 60)
    print(f"Project root: {ROOT}\n")

    check_raw_files()
    run_step("01_clean_data.py", "Step 1: Cleaning raw data")
    run_step("02_build_database.py", "Step 2: Building SQL database")
    run_step("04_export_powerbi.py", "Step 3: Exporting Power BI-ready CSVs")

    print("=" * 60)
    print("ALL DONE. Nothing failed.")
    print("=" * 60)
    print(f"""
What to open next:
  - Notebook (charts):      notebook/Vaccination_Data_Analysis_EDA.ipynb
  - Dashboard (interactive): dashboard/vaccination_dashboard.html  (double-click it)
  - Database:                vaccination.db
  - Report:                  docs/Project_Report.md
  - Power BI guide:          docs/PowerBI_Dashboard_Guide.md
""")
