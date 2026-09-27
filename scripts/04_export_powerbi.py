"""
04_export_powerbi.py
---------------------
Exports a Power BI-ready star schema: one fact table per dataset plus the
country dimension, all as flat CSVs with a WHO region column already
joined on, ready to load straight into Power BI (Get Data > Text/CSV) or
via the SQL Server/SQLite connector against vaccination.db.
"""

import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLEAN = ROOT / "data" / "clean"
PBI = ROOT / "data" / "powerbi"
PBI.mkdir(parents=True, exist_ok=True)

dim_country = pd.read_csv(CLEAN / "dim_country.csv")
coverage = pd.read_csv(CLEAN / "coverage_data.csv")
incidence = pd.read_csv(CLEAN / "incidence_rate_data.csv")
cases = pd.read_csv(CLEAN / "reported_cases_data.csv")
intro = pd.read_csv(CLEAN / "vaccine_introduction_data.csv")
schedule = pd.read_csv(CLEAN / "vaccine_schedule_data.csv")

# who_region lives in the intro/schedule tables; build one lookup and reuse it
region_lookup = pd.concat([
    intro[["ISO_3_CODE", "WHO_REGION"]].rename(columns={"ISO_3_CODE": "CODE", "WHO_REGION": "WHO_REGION"}),
    schedule[["ISO_3_CODE", "WHO_REGION"]].rename(columns={"ISO_3_CODE": "CODE", "WHO_REGION": "WHO_REGION"}),
]).dropna().drop_duplicates(subset=["CODE"])

dim_country_pbi = dim_country.rename(columns={"code": "CODE", "name": "COUNTRY_NAME"})
dim_country_pbi = dim_country_pbi.merge(region_lookup, on="CODE", how="left")
dim_country_pbi = dim_country_pbi[["CODE", "COUNTRY_NAME", "WHO_REGION"]].drop_duplicates(subset=["CODE"])
dim_country_pbi.to_csv(PBI / "Dim_Country.csv", index=False)

coverage.to_csv(PBI / "Fact_Coverage.csv", index=False)
incidence.to_csv(PBI / "Fact_IncidenceRate.csv", index=False)
cases.to_csv(PBI / "Fact_ReportedCases.csv", index=False)
intro.to_csv(PBI / "Fact_VaccineIntroduction.csv", index=False)
schedule.to_csv(PBI / "Fact_VaccineSchedule.csv", index=False)

print("Power BI-ready CSVs written to data/powerbi/:")
for f in sorted(PBI.glob("*.csv")):
    df = pd.read_csv(f, nrows=0)
    n = sum(1 for _ in open(f, encoding="utf-8")) - 1
    print(f"  {f.name:30s} {n:>8,} rows   cols: {list(df.columns)}")
