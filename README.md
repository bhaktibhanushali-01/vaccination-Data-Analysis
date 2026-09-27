# Vaccination Data Analysis and Visualization

End-to-end project: raw WHO vaccination data → cleaned data → normalized SQL database →
exploratory data analysis (Jupyter notebook, 20+ charts) → Power BI-ready dashboard data.

## Fastest way to run everything

**Windows:** double-click `RUN_ME.bat`
**Mac/Linux/any terminal:** `python RUN_ME.py`

This single command checks the raw files are present, cleans the data, builds the
SQL database, and exports the Power BI CSVs — in the right order, automatically.
Nothing else to run manually unless you want to look under the hood.

## Folder structure

```
.
├── README.md                          <- you are here
├── vaccination.db                     <- SQLite database (built from the raw data)
├── data/
│   ├── raw/                           <- original WHO Excel files, untouched
│   ├── clean/                         <- cleaned CSVs (output of step 1)
│   └── powerbi/                       <- flat star-schema CSVs, ready for Power BI
├── sql/
│   ├── schema.sql                     <- table definitions (dimension + 5 fact tables)
│   └── analysis_queries.sql           <- SQL answers to the brief's business questions
├── notebook/
│   └── Vaccination_Data_Analysis_EDA.ipynb   <- full EDA notebook, pre-executed
├── dashboard/
│   └── vaccination_dashboard.html     <- interactive web dashboard, open in any browser
├── scripts/
│   ├── 01_clean_data.py               <- step 1: clean raw Excel -> data/clean/
│   ├── 02_build_database.py           <- step 2: build vaccination.db from clean CSVs
│   ├── 03_build_notebook.py           <- (re)generates the notebook programmatically
│   └── 04_export_powerbi.py           <- step 4: build data/powerbi/ CSVs
└── docs/
    ├── Project_Report.md              <- write-up: approach, findings, Q&A from the brief
    └── PowerBI_Dashboard_Guide.md     <- step-by-step Power BI build guide + DAX measures
```

## How to reproduce everything from scratch

```bash
pip install pandas openpyxl nbformat nbclient matplotlib seaborn jupyter

cd scripts
python 01_clean_data.py        # raw Excel -> data/clean/*.csv
python 02_build_database.py    # data/clean/*.csv -> ../vaccination.db
python 04_export_powerbi.py    # data/clean/*.csv -> data/powerbi/*.csv (Power BI ready)

# (Optional) rebuild + re-execute the notebook
python 03_build_notebook.py
cd ../notebook
jupyter nbconvert --to notebook --execute --inplace Vaccination_Data_Analysis_EDA.ipynb
```

## Data source

Five tables, provided as Excel exports (WHO/UNICEF immunization data format):
coverage, incidence rate, reported cases, vaccine introduction, vaccine schedule.
Data spans **1980–2023** across **245** countries/territories.

## What's in the database

`vaccination.db` (SQLite) — a normalized star schema:

- `dim_country` — 245 rows: ISO-3 code, name, WHO region
- `fact_coverage` — ~400K rows: coverage % by country/year/antigen
- `fact_incidence_rate` — ~85K rows: disease incidence rate by country/year/disease
- `fact_reported_cases` — ~85K rows: raw case counts by country/year/disease
- `fact_vaccine_introduction` — ~138K rows: Yes/No vaccine introduction by country/year
- `fact_vaccine_schedule` — ~8K rows: dosing schedule detail by country/vaccine

Zero orphan foreign keys — every fact row's country code resolves to `dim_country`.

## Notebook

`notebook/Vaccination_Data_Analysis_EDA.ipynb` follows the standard EDA capstone
structure (Know Your Data → Data Wrangling → Univariate/Bivariate/Multivariate
visualization → Solution to Business Objective → Conclusion), with **21 charts**, each
answering: why this chart, what insight it shows, and its business impact. The notebook
is pre-executed — all outputs/charts are already rendered — and re-runs cleanly end to
end with no errors.

## Interactive dashboard (no install needed)

`dashboard/vaccination_dashboard.html` — double-click to open in any browser. Filter by
WHO region, switch the antigen shown in the trend chart, sort the country table, and
explore coverage trends, disease burden, coverage-vs-incidence, dose drop-off, and
vaccine rollout pace — all interactive, no Power BI or server required.

## Power BI

See `docs/PowerBI_Dashboard_Guide.md` for the full walkthrough: which CSVs to load, the
relationships to build, recommended DAX measures, and suggested dashboard pages.
`data/powerbi/` has the CSVs ready to import.

## Report

See `docs/Project_Report.md` for the write-up: approach, data-cleaning decisions, and
answers to the brief's easy/medium/scenario-based questions.
