# Project Report — Vaccination Data Analysis and Visualization

## 1. Objective

Analyze global WHO/UNICEF vaccination data (1980–2023, 245 countries/territories) to
understand vaccination coverage trends, disease incidence, and program effectiveness,
and package the pipeline (cleaning → SQL database → EDA → Power BI) as requested in the
project brief.

## 2. Data cleaning — approach and decisions

| Step | Decision | Why |
|---|---|---|
| Footer rows | Dropped rows with >50% null columns | WHO exports end with a blank summary row |
| Data types | `YEAR` coerced to integer, numeric fields (`COVERAGE`, `DOSES`, `TARGET_NUMBER`, `CASES`, `INCIDENCE_RATE`) coerced to float | Excel exports sometimes carry these as text |
| Coverage range | Clipped to [0, 100] | A handful of extreme/erroneous outliers existed outside a valid percentage range |
| Text fields | Whitespace-stripped, standardised casing | Prevents duplicate "Yes"/"yes " style categories |
| Country dimension | Built by combining country code/name/region across all 5 source tables, de-duplicated on ISO-3 code | No single source table has a complete, clean country list |
| Referential integrity | Verified — 0 orphan foreign keys across all 5 fact tables | Confirms the database is safe to join on `code` everywhere |

**Note on regional aggregate codes:** a small number of rows use WHO's aggregate
grouping codes (e.g. `WB_LONG_NA`, `WB_SHORT_NA` — World Bank income-group aggregates)
rather than individual countries. These were kept in the dataset (they're valid WHO
rows) but should be **excluded via the `GROUP` column when building country-level Power
BI visuals** — filter `GROUP = 'COUNTRIES'` for individual-country analysis.

## 3. Database

Normalized SQLite database (`vaccination.db`): 1 dimension table + 5 fact tables,
~717,000 rows total. See `sql/schema.sql` for the full DDL and
`sql/analysis_queries.sql` for 11 ready-to-run queries answering the brief's questions.

## 4. Key findings (real figures from this dataset)

**Lowest-coverage countries (2023, average across BCG/DTP1/DTP3/Polio3/Measles1/HepB3/PCV3, WUENIC):**

| Country | Avg. coverage |
|---|---|
| Democratic People's Republic of Korea | 27.3% |
| Papua New Guinea | 40.7% |
| Somalia | 44.3% |
| Central African Republic | 46.6% |
| Yemen | 48.4% |
| Sudan | 52.0% |
| Guinea | 54.0% |

→ **Directly answers the "which regions have low coverage" easy-level question** and
the resource-allocation scenario question. These are the clearest candidates for
targeted intervention.

**Largest DTP1 → DTP3 drop-off (2023):**

| Country | DTP1 | DTP3 | Drop-off |
|---|---|---|---|
| Dominica | 99% | 56% | 43 pp |
| DPR Korea | 41% | 16% | 25 pp |
| Haiti | 75% | 51% | 24 pp |
| Lebanon | 78% | 55% | 23 pp |
| Saint Lucia | 96% | 74% | 22 pp |

→ **Directly answers the "drop-off between 1st dose and subsequent doses" question.**
These countries reach families for dose 1 — the fix is retention/follow-up, not initial
access.

**Global measles (MCV1) coverage, 2015–2023:** coverage held near 87% through 2019,
fell to **83.2% in 2021** (a ~4-point drop), and has only partially recovered to **85.0%
by 2023** — still below the pre-pandemic level and well short of the WHO 2030 target
of 95%.

→ Answers both the "seasonal/temporal pattern" question (in the sense the annual data
allows) and the "progress toward 95% by 2030" scenario question: **progress has
stalled, not advanced**, since 2019.

**Highest disease burden by total reported cases (1980–2023):**

| Disease | Total reported cases |
|---|---|
| Measles | 144,065,673 |
| Pertussis | 53,089,864 |
| Mumps | 36,326,936 |
| Typhoid | 31,153,098 |
| Rubella | 16,655,663 |

→ Answers the "which diseases have the most significant reduction potential /
high-priority disease" questions — measles and pertussis dominate by volume and should
anchor booster and catch-up-campaign policy.

## 5. Answers to selected scenario questions

1. **"Identify regions with low vaccination coverage to allocate resources effectively"**
   — see the lowest-coverage table above; query in `sql/analysis_queries.sql` (Scenario 1).
2. **"Evaluate effectiveness of a measles campaign launched five years ago"** — use
   `sql/analysis_queries.sql` Q5 (before/after `vaccine_introduction` join), adjusting
   the country filter; the notebook's Chart 8 shows the global before/after pattern.
3. **"Track progress toward 95% measles coverage by 2030"** — see the MCV1 trend above
   and `sql/analysis_queries.sql` Scenario 6; at the current trajectory (85.0% in 2023,
   flat since 2021) the 95% target is not on track without accelerated catch-up efforts.
4. **"Detect disparities across socioeconomic groups"** — the dataset's `GROUP` column
   includes World Bank income-group aggregates (`WB_LONG_NA` etc.) that can be used for
   this directly; filter `GROUP != 'COUNTRIES'` in `fact_coverage` to isolate them.

## 6. Deliverables checklist (per the brief)

- [x] Python scripts for data extraction and cleaning — `scripts/01_clean_data.py`
- [x] SQL queries for creating and populating tables — `sql/schema.sql`, `scripts/02_build_database.py`
- [x] Structured, normalized SQL database — `vaccination.db`
- [x] EDA with 20+ charts, UBM structure, insight + business-impact write-up per chart — `notebook/`
- [x] Power BI-ready data + build guide — `data/powerbi/`, `docs/PowerBI_Dashboard_Guide.md`
- [x] Documentation — this report + `README.md`
