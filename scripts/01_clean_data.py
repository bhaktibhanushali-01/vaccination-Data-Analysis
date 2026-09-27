"""
01_clean_data.py
-----------------
Cleans the 5 raw WHO vaccination Excel tables and writes tidy CSVs to
data/clean/. Run this first, before building the SQL database or notebook.

Usage:
    python 01_clean_data.py
"""

import pandas as pd
import numpy as np
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"
CLEAN = Path(__file__).resolve().parent.parent / "data" / "clean"
CLEAN.mkdir(parents=True, exist_ok=True)


def drop_fully_blank_rows(df: pd.DataFrame) -> pd.DataFrame:
    """WHO exports carry a trailing footer row that is entirely NaN except
    for a stray key column. Drop rows where almost everything is null."""
    thresh = max(1, int(df.shape[1] * 0.5))
    return df.dropna(thresh=thresh).reset_index(drop=True)


def clean_common(df: pd.DataFrame) -> pd.DataFrame:
    df = drop_fully_blank_rows(df)
    # Standardise column names
    df.columns = [c.strip().upper() for c in df.columns]
    # Strip whitespace from all string/object columns
    for c in df.select_dtypes(include="object").columns:
        df[c] = df[c].astype(str).str.strip().replace({"nan": np.nan})
    return df


def clean_coverage():
    df = pd.read_excel(RAW / "coverage-data.xlsx", sheet_name="Data")
    df = clean_common(df)
    df["YEAR"] = pd.to_numeric(df["YEAR"], errors="coerce").astype("Int64")
    for col in ["TARGET_NUMBER", "DOSES", "COVERAGE"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    # Coverage is a percentage: clip implausible values, keep NaN for unknown
    df["COVERAGE"] = df["COVERAGE"].clip(lower=0, upper=100)
    # Drop rows with no country code or no year (can't be analysed)
    df = df.dropna(subset=["CODE", "YEAR"]).reset_index(drop=True)
    df.to_csv(CLEAN / "coverage_data.csv", index=False)
    print(f"coverage_data.csv        -> {df.shape}")
    return df


def clean_incidence():
    df = pd.read_excel(RAW / "incidence-rate-data.xlsx", sheet_name="Data")
    df = clean_common(df)
    df["YEAR"] = pd.to_numeric(df["YEAR"], errors="coerce").astype("Int64")
    df["INCIDENCE_RATE"] = pd.to_numeric(df["INCIDENCE_RATE"], errors="coerce")
    df = df.dropna(subset=["CODE", "YEAR", "DISEASE"]).reset_index(drop=True)
    df.to_csv(CLEAN / "incidence_rate_data.csv", index=False)
    print(f"incidence_rate_data.csv  -> {df.shape}")
    return df


def clean_reported_cases():
    df = pd.read_excel(RAW / "reported-cases-data.xlsx", sheet_name="Data")
    df = clean_common(df)
    df["YEAR"] = pd.to_numeric(df["YEAR"], errors="coerce").astype("Int64")
    df["CASES"] = pd.to_numeric(df["CASES"], errors="coerce")
    df = df.dropna(subset=["CODE", "YEAR", "DISEASE"]).reset_index(drop=True)
    df.to_csv(CLEAN / "reported_cases_data.csv", index=False)
    print(f"reported_cases_data.csv  -> {df.shape}")
    return df


def clean_vaccine_intro():
    df = pd.read_excel(RAW / "vaccine-introduction-data.xlsx", sheet_name="Data")
    df = clean_common(df)
    df["YEAR"] = pd.to_numeric(df["YEAR"], errors="coerce").astype("Int64")
    # Normalise Yes/No/NA style flags
    df["INTRO"] = df["INTRO"].str.title().replace(
        {"Yes": "Yes", "No": "No", "Nan": np.nan}
    )
    df = df.dropna(subset=["ISO_3_CODE", "YEAR"]).reset_index(drop=True)
    df.to_csv(CLEAN / "vaccine_introduction_data.csv", index=False)
    print(f"vaccine_introduction_data.csv -> {df.shape}")
    return df


def clean_vaccine_schedule():
    df = pd.read_excel(RAW / "vaccine-schedule-data.xlsx", sheet_name="Data")
    df = clean_common(df)
    df["YEAR"] = pd.to_numeric(df["YEAR"], errors="coerce").astype("Int64")
    df["SCHEDULEROUNDS"] = pd.to_numeric(df["SCHEDULEROUNDS"], errors="coerce")
    df = df.dropna(subset=["ISO_3_CODE", "YEAR"]).reset_index(drop=True)
    df.to_csv(CLEAN / "vaccine_schedule_data.csv", index=False)
    print(f"vaccine_schedule_data.csv -> {df.shape}")
    return df


def build_dim_country(coverage, incidence, cases, intro, schedule):
    """A single, de-duplicated country dimension table (code -> name)."""
    frames = [
        coverage[["CODE", "NAME"]].rename(columns={"CODE": "code", "NAME": "name"}),
        incidence[["CODE", "NAME"]].rename(columns={"CODE": "code", "NAME": "name"}),
        cases[["CODE", "NAME"]].rename(columns={"CODE": "code", "NAME": "name"}),
        intro[["ISO_3_CODE", "COUNTRYNAME", "WHO_REGION"]].rename(
            columns={"ISO_3_CODE": "code", "COUNTRYNAME": "name", "WHO_REGION": "who_region"}
        ),
        schedule[["ISO_3_CODE", "COUNTRYNAME", "WHO_REGION"]].rename(
            columns={"ISO_3_CODE": "code", "COUNTRYNAME": "name", "WHO_REGION": "who_region"}
        ),
    ]
    dim = pd.concat(frames, ignore_index=True)
    dim = dim.dropna(subset=["code"])
    # Prefer rows that actually have a name; fall back to the code itself
    dim["name"] = dim["name"].fillna(dim["code"])
    dim = dim.sort_values(["code", "name"]).drop_duplicates(subset=["code"], keep="last")
    dim = dim.sort_values("code").reset_index(drop=True)
    dim.to_csv(CLEAN / "dim_country.csv", index=False)
    print(f"dim_country.csv          -> {dim.shape}")
    return dim


if __name__ == "__main__":
    print("Cleaning WHO vaccination data files...\n")
    coverage = clean_coverage()
    incidence = clean_incidence()
    cases = clean_reported_cases()
    intro = clean_vaccine_intro()
    schedule = clean_vaccine_schedule()
    build_dim_country(coverage, incidence, cases, intro, schedule)
    print("\nDone. Cleaned CSVs are in data/clean/")
