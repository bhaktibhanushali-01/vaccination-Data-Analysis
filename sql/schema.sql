-- =====================================================================
-- schema.sql
-- Normalized schema for the WHO Vaccination Data Analysis project.
-- Compatible with SQLite (used to build vaccination.db) and portable
-- to MySQL / PostgreSQL / SQL Server with minor type tweaks.
-- =====================================================================

DROP TABLE IF EXISTS fact_coverage;
DROP TABLE IF EXISTS fact_incidence_rate;
DROP TABLE IF EXISTS fact_reported_cases;
DROP TABLE IF EXISTS fact_vaccine_introduction;
DROP TABLE IF EXISTS fact_vaccine_schedule;
DROP TABLE IF EXISTS dim_country;

-- ---------------------------------------------------------------------
-- DIMENSION: Country
-- ---------------------------------------------------------------------
CREATE TABLE dim_country (
    code        TEXT PRIMARY KEY,      -- ISO-3 country code
    name        TEXT NOT NULL,
    who_region  TEXT                   -- WHO region (AFRO, AMRO, EMRO, EURO, SEARO, WPRO)
);

-- ---------------------------------------------------------------------
-- FACT: Vaccination coverage (Table 1)
-- ---------------------------------------------------------------------
CREATE TABLE fact_coverage (
    id                              INTEGER PRIMARY KEY AUTOINCREMENT,
    code                            TEXT NOT NULL REFERENCES dim_country(code),
    year                            INTEGER NOT NULL,
    antigen                         TEXT NOT NULL,
    antigen_description             TEXT,
    coverage_category               TEXT,
    coverage_category_description   TEXT,
    target_number                   REAL,
    doses                           REAL,
    coverage                        REAL          -- % of target population vaccinated
);

CREATE INDEX idx_coverage_code_year ON fact_coverage(code, year);
CREATE INDEX idx_coverage_antigen   ON fact_coverage(antigen);

-- ---------------------------------------------------------------------
-- FACT: Disease incidence rate (Table 2)
-- ---------------------------------------------------------------------
CREATE TABLE fact_incidence_rate (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    code                  TEXT NOT NULL REFERENCES dim_country(code),
    year                  INTEGER NOT NULL,
    disease               TEXT NOT NULL,
    disease_description   TEXT,
    denominator            TEXT,
    incidence_rate         REAL
);

CREATE INDEX idx_incidence_code_year ON fact_incidence_rate(code, year);
CREATE INDEX idx_incidence_disease   ON fact_incidence_rate(disease);

-- ---------------------------------------------------------------------
-- FACT: Reported cases (Table 3)
-- ---------------------------------------------------------------------
CREATE TABLE fact_reported_cases (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    code                  TEXT NOT NULL REFERENCES dim_country(code),
    year                  INTEGER NOT NULL,
    disease               TEXT NOT NULL,
    disease_description   TEXT,
    cases                 REAL
);

CREATE INDEX idx_cases_code_year ON fact_reported_cases(code, year);
CREATE INDEX idx_cases_disease   ON fact_reported_cases(disease);

-- ---------------------------------------------------------------------
-- FACT: Vaccine introduction (Table 4)
-- ---------------------------------------------------------------------
CREATE TABLE fact_vaccine_introduction (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    code          TEXT NOT NULL REFERENCES dim_country(code),
    who_region    TEXT,
    year          INTEGER NOT NULL,
    description   TEXT NOT NULL,     -- vaccine name
    intro         TEXT               -- Yes / No
);

CREATE INDEX idx_intro_code_year ON fact_vaccine_introduction(code, year);

-- ---------------------------------------------------------------------
-- FACT: Vaccine schedule (Table 5)
-- ---------------------------------------------------------------------
CREATE TABLE fact_vaccine_schedule (
    id                        INTEGER PRIMARY KEY AUTOINCREMENT,
    code                      TEXT NOT NULL REFERENCES dim_country(code),
    who_region                TEXT,
    year                      INTEGER NOT NULL,
    vaccine_code              TEXT,
    vaccine_description       TEXT,
    schedule_rounds           REAL,
    target_pop                TEXT,
    target_pop_description    TEXT,
    geoarea                   TEXT,
    age_administered          TEXT,
    source_comment            TEXT
);

CREATE INDEX idx_schedule_code_year ON fact_vaccine_schedule(code, year);
