"""
02_build_database.py
---------------------
Builds vaccination.db (SQLite) from the cleaned CSVs using sql/schema.sql,
then loads each fact/dimension table. Run this after 01_clean_data.py.

Usage:
    python 02_build_database.py
"""

import sqlite3
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLEAN = ROOT / "data" / "clean"
SQL = ROOT / "sql"
DB_PATH = ROOT / "vaccination.db"

if DB_PATH.exists():
    DB_PATH.unlink()

conn = sqlite3.connect(DB_PATH)

# 1. Create schema
with open(SQL / "schema.sql", encoding="utf-8") as f:
    conn.executescript(f.read())

# 2. Load dim_country
dim_country = pd.read_csv(CLEAN / "dim_country.csv")
dim_country.to_sql("dim_country", conn, if_exists="append", index=False)

# 3. Load fact_coverage
coverage = pd.read_csv(CLEAN / "coverage_data.csv")
coverage = coverage.rename(columns={
    "CODE": "code", "YEAR": "year", "ANTIGEN": "antigen",
    "ANTIGEN_DESCRIPTION": "antigen_description",
    "COVERAGE_CATEGORY": "coverage_category",
    "COVERAGE_CATEGORY_DESCRIPTION": "coverage_category_description",
    "TARGET_NUMBER": "target_number", "DOSES": "doses", "COVERAGE": "coverage",
})[["code", "year", "antigen", "antigen_description", "coverage_category",
    "coverage_category_description", "target_number", "doses", "coverage"]]
coverage.to_sql("fact_coverage", conn, if_exists="append", index=False)

# 4. Load fact_incidence_rate
incidence = pd.read_csv(CLEAN / "incidence_rate_data.csv")
incidence = incidence.rename(columns={
    "CODE": "code", "YEAR": "year", "DISEASE": "disease",
    "DISEASE_DESCRIPTION": "disease_description",
    "DENOMINATOR": "denominator", "INCIDENCE_RATE": "incidence_rate",
})[["code", "year", "disease", "disease_description", "denominator", "incidence_rate"]]
incidence.to_sql("fact_incidence_rate", conn, if_exists="append", index=False)

# 5. Load fact_reported_cases
cases = pd.read_csv(CLEAN / "reported_cases_data.csv")
cases = cases.rename(columns={
    "CODE": "code", "YEAR": "year", "DISEASE": "disease",
    "DISEASE_DESCRIPTION": "disease_description", "CASES": "cases",
})[["code", "year", "disease", "disease_description", "cases"]]
cases.to_sql("fact_reported_cases", conn, if_exists="append", index=False)

# 6. Load fact_vaccine_introduction
intro = pd.read_csv(CLEAN / "vaccine_introduction_data.csv")
intro = intro.rename(columns={
    "ISO_3_CODE": "code", "WHO_REGION": "who_region", "YEAR": "year",
    "DESCRIPTION": "description", "INTRO": "intro",
})[["code", "who_region", "year", "description", "intro"]]
intro.to_sql("fact_vaccine_introduction", conn, if_exists="append", index=False)

# 7. Load fact_vaccine_schedule
schedule = pd.read_csv(CLEAN / "vaccine_schedule_data.csv")
schedule = schedule.rename(columns={
    "ISO_3_CODE": "code", "WHO_REGION": "who_region", "YEAR": "year",
    "VACCINECODE": "vaccine_code", "VACCINE_DESCRIPTION": "vaccine_description",
    "SCHEDULEROUNDS": "schedule_rounds", "TARGETPOP": "target_pop",
    "TARGETPOP_DESCRIPTION": "target_pop_description", "GEOAREA": "geoarea",
    "AGEADMINISTERED": "age_administered", "SOURCECOMMENT": "source_comment",
})[["code", "who_region", "year", "vaccine_code", "vaccine_description",
    "schedule_rounds", "target_pop", "target_pop_description", "geoarea",
    "age_administered", "source_comment"]]
schedule.to_sql("fact_vaccine_schedule", conn, if_exists="append", index=False)

conn.commit()

# Sanity check row counts
for tbl in ["dim_country", "fact_coverage", "fact_incidence_rate",
            "fact_reported_cases", "fact_vaccine_introduction", "fact_vaccine_schedule"]:
    n = conn.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
    print(f"{tbl:30s} {n:>10,} rows")

conn.close()
print(f"\nDatabase built at {DB_PATH}")
