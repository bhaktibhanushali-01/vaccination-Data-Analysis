# Power BI Dashboard Guide — Vaccination Data Analysis

This guide walks you through building the interactive Power BI dashboard on top of the
cleaned data produced by this project. Power BI Desktop itself can't be generated as a
file by an AI tool — you build it locally — but everything below (the data, the model,
the exact measures) is ready to paste in, so this should take **30–45 minutes**, not days.

## 1. Get the data into Power BI

You have two options:

**Option A — Flat CSVs (simplest):**
Open Power BI Desktop → **Get Data → Text/CSV** → load each file from `data/powerbi/`:
- `Dim_Country.csv`
- `Fact_Coverage.csv`
- `Fact_IncidenceRate.csv`
- `Fact_ReportedCases.csv`
- `Fact_VaccineIntroduction.csv`
- `Fact_VaccineSchedule.csv`

**Option B — Connect straight to the SQL database:**
Get Data → **More… → Database → SQLite database** (or ODBC if SQLite connector isn't
listed) → point it at `vaccination.db`. This pulls the same normalized tables and makes
future refreshes trivial if you re-run the cleaning/build scripts on newer WHO data.

## 2. Build the data model (relationships)

In **Model view**, create these relationships (all `Country Code` → `CODE`, one-to-many,
single direction from Dim_Country):

```
Dim_Country[CODE]  1 -----* Fact_Coverage[CODE]
Dim_Country[CODE]  1 -----* Fact_IncidenceRate[CODE]
Dim_Country[CODE]  1 -----* Fact_ReportedCases[CODE]
Dim_Country[CODE]  1 -----* Fact_VaccineIntroduction[ISO_3_CODE]
Dim_Country[CODE]  1 -----* Fact_VaccineSchedule[ISO_3_CODE]
```

This gives you a classic **star schema**: one dimension (country/region), five facts.

## 3. Recommended DAX measures

Paste these into a new measure on `Fact_Coverage` (or a dedicated Measures table):

```DAX
Avg Coverage = AVERAGE(Fact_Coverage[COVERAGE])

Coverage (WUENIC only) =
CALCULATE(
    AVERAGE(Fact_Coverage[COVERAGE]),
    Fact_Coverage[COVERAGE_CATEGORY] = "WUENIC"
)

DTP1 to DTP3 Dropoff (pp) =
VAR DTP1 = CALCULATE(AVERAGE(Fact_Coverage[COVERAGE]), Fact_Coverage[ANTIGEN] = "DTPCV1")
VAR DTP3 = CALCULATE(AVERAGE(Fact_Coverage[COVERAGE]), Fact_Coverage[ANTIGEN] = "DTPCV3")
RETURN DTP1 - DTP3

Total Reported Cases = SUM(Fact_ReportedCases[CASES])

Countries at 95%+ Target =
CALCULATE(
    DISTINCTCOUNT(Fact_Coverage[CODE]),
    Fact_Coverage[COVERAGE] >= 95,
    Fact_Coverage[ANTIGEN] = "MCV1"
)

% Vaccines Introduced =
DIVIDE(
    CALCULATE(COUNTROWS(Fact_VaccineIntroduction), Fact_VaccineIntroduction[INTRO] = "Yes"),
    COUNTROWS(Fact_VaccineIntroduction)
)
```

## 4. Suggested pages / visuals

| Page | Visual | Fields |
|---|---|---|
| **Overview** | KPI cards | Avg Coverage, Countries at 95%+ Target, Total Reported Cases |
| **Overview** | Geographic heatmap (Filled Map) | `Dim_Country[COUNTRY_NAME]` (or ISO code) on Location, `Avg Coverage` on color |
| **Coverage Trends** | Line chart | `YEAR` on X, `Avg Coverage` on Y, `ANTIGEN` as legend (filter to key antigens) |
| **Coverage Trends** | Slicer | `WHO_REGION`, `YEAR` range |
| **Disease Burden** | Bar chart | `DISEASE_DESCRIPTION` on Y, `Total Reported Cases` on X |
| **Disease Burden** | Scatter plot | `Avg Coverage` (X) vs `Avg Incidence Rate` (Y), one point per country |
| **Dose Retention** | Bar chart | `DTP1 to DTP3 Dropoff (pp)` by country, sorted descending |
| **Vaccine Introduction** | Line/area chart | Cumulative distinct vaccines introduced by year, split by `WHO_REGION` |
| **Vaccine Introduction** | Table | Country, vaccine, year introduced, current coverage |

## 5. Filters/slicers to add on every page

- `WHO_REGION` (from Dim_Country)
- `YEAR` (range slider)
- `ANTIGEN` / `DISEASE` (for the relevant pages)

## 6. Refreshing with new data

When new WHO data is released:
1. Replace the files in `data/raw/` with the new WHO exports (same filenames).
2. Re-run `scripts/01_clean_data.py`, `02_build_database.py`, `04_export_powerbi.py`.
3. In Power BI, click **Refresh** (if pointed at the CSVs/DB paths, no rebuild needed).
