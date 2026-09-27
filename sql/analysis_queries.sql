-- =====================================================================
-- analysis_queries.sql
-- Answers to the business questions in the project brief.
-- Run against vaccination.db (SQLite syntax; portable with minor edits).
-- =====================================================================

-- ---------------------------------------------------------------------
-- Q1 (Easy). Vaccination rate vs disease incidence, by country/year
--     (join coverage for DTP-containing antigen against incidence of
--      Diphtheria as an example pair)
-- ---------------------------------------------------------------------
SELECT
    c.code,
    d.name AS country,
    c.year,
    AVG(c.coverage)              AS avg_dtp_coverage,
    i.incidence_rate             AS diphtheria_incidence
FROM fact_coverage c
JOIN dim_country d          ON d.code = c.code
JOIN fact_incidence_rate i  ON i.code = c.code AND i.year = c.year AND i.disease = 'DIPHTHERIA'
WHERE c.antigen = 'DTPCV3'
GROUP BY c.code, c.year
ORDER BY c.year DESC;

-- ---------------------------------------------------------------------
-- Q2 (Easy). Drop-off rate between 1st dose and later doses (DTP1 -> DTP3)
-- ---------------------------------------------------------------------
WITH dose1 AS (
    SELECT code, year, coverage AS dtp1_coverage
    FROM fact_coverage WHERE antigen = 'DTPCV1'
),
dose3 AS (
    SELECT code, year, coverage AS dtp3_coverage
    FROM fact_coverage WHERE antigen = 'DTPCV3'
)
SELECT
    d1.code, dc.name AS country, d1.year,
    d1.dtp1_coverage, d3.dtp3_coverage,
    ROUND(d1.dtp1_coverage - d3.dtp3_coverage, 2) AS dropoff_pp
FROM dose1 d1
JOIN dose3 d3 ON d1.code = d3.code AND d1.year = d3.year
JOIN dim_country dc ON dc.code = d1.code
WHERE d1.dtp1_coverage IS NOT NULL AND d3.dtp3_coverage IS NOT NULL
ORDER BY dropoff_pp DESC;

-- ---------------------------------------------------------------------
-- Q3 (Easy). Booster dose uptake trend over time (e.g. DTP booster / DTPCV4)
-- ---------------------------------------------------------------------
SELECT year, ROUND(AVG(coverage), 2) AS avg_booster_coverage
FROM fact_coverage
WHERE antigen LIKE 'DTPCV4%' OR antigen LIKE '%BOOSTER%'
GROUP BY year
ORDER BY year;

-- ---------------------------------------------------------------------
-- Q4 (Easy). Regions with high disease incidence despite high vaccination
-- ---------------------------------------------------------------------
SELECT
    c.code, d.name AS country, c.year,
    ROUND(AVG(c.coverage), 2) AS avg_coverage,
    ROUND(AVG(i.incidence_rate), 4) AS avg_incidence
FROM fact_coverage c
JOIN dim_country d ON d.code = c.code
JOIN fact_incidence_rate i ON i.code = c.code AND i.year = c.year
WHERE c.coverage >= 90
GROUP BY c.code, c.year
HAVING avg_incidence > 0
ORDER BY avg_incidence DESC
LIMIT 25;

-- ---------------------------------------------------------------------
-- Q5 (Medium). Trend in disease cases before/after a vaccine's introduction
--     (parameterised for Measles as an example -- swap DISEASE/VACCINE)
-- ---------------------------------------------------------------------
WITH intro_year AS (
    SELECT code, MIN(year) AS year_introduced
    FROM fact_vaccine_introduction
    WHERE description LIKE '%Measles%' AND intro = 'Yes'
    GROUP BY code
)
SELECT
    r.code, dc.name AS country, r.year,
    iy.year_introduced,
    (r.year - iy.year_introduced) AS years_since_intro,
    r.cases
FROM fact_reported_cases r
JOIN intro_year iy ON iy.code = r.code
JOIN dim_country dc ON dc.code = r.code
WHERE r.disease = 'MEASLES'
ORDER BY r.code, r.year;

-- ---------------------------------------------------------------------
-- Q6 (Medium). % of target population covered, per vaccine (antigen)
-- ---------------------------------------------------------------------
SELECT
    antigen, antigen_description,
    ROUND(SUM(doses) * 100.0 / NULLIF(SUM(target_number), 0), 2) AS pct_target_covered
FROM fact_coverage
WHERE target_number IS NOT NULL AND doses IS NOT NULL
GROUP BY antigen, antigen_description
ORDER BY pct_target_covered DESC;

-- ---------------------------------------------------------------------
-- Q7 (Medium). Disparities in vaccine introduction timelines across WHO regions
-- ---------------------------------------------------------------------
SELECT
    who_region,
    description AS vaccine,
    MIN(CASE WHEN intro = 'Yes' THEN year END) AS earliest_intro_year,
    MAX(CASE WHEN intro = 'Yes' THEN year END) AS latest_intro_year,
    COUNT(DISTINCT CASE WHEN intro = 'Yes' THEN code END) AS countries_introduced
FROM fact_vaccine_introduction
GROUP BY who_region, description
ORDER BY vaccine, who_region;

-- ---------------------------------------------------------------------
-- Q8 (Medium). Countries with low coverage despite vaccine being introduced
-- ---------------------------------------------------------------------
SELECT
    vi.code, dc.name AS country, vi.description AS vaccine, vi.year,
    ROUND(AVG(c.coverage), 2) AS avg_coverage
FROM fact_vaccine_introduction vi
JOIN dim_country dc ON dc.code = vi.code
LEFT JOIN fact_coverage c ON c.code = vi.code AND c.year = vi.year
WHERE vi.intro = 'Yes'
GROUP BY vi.code, vi.description, vi.year
HAVING avg_coverage < 50
ORDER BY avg_coverage ASC
LIMIT 30;

-- ---------------------------------------------------------------------
-- Q9 (Medium). Most prevalent diseases by geographic region (WHO region)
-- ---------------------------------------------------------------------
SELECT
    vi.who_region,
    rc.disease,
    ROUND(SUM(rc.cases), 0) AS total_cases
FROM fact_reported_cases rc
JOIN (SELECT DISTINCT code, who_region FROM fact_vaccine_introduction) vi
      ON vi.code = rc.code
GROUP BY vi.who_region, rc.disease
ORDER BY vi.who_region, total_cases DESC;

-- ---------------------------------------------------------------------
-- Scenario 1. Regions with low vaccination coverage (for resource allocation)
--     Latest year, national-level coverage, below 80% threshold
-- ---------------------------------------------------------------------
SELECT d.name AS country, c.antigen, c.year, c.coverage
FROM fact_coverage c
JOIN dim_country d ON d.code = c.code
WHERE c.year = (SELECT MAX(year) FROM fact_coverage)
  AND c.coverage_category = 'ADMIN'
  AND c.coverage < 80
ORDER BY c.coverage ASC
LIMIT 50;

-- ---------------------------------------------------------------------
-- Scenario 6. Global progress toward 95% measles coverage target by 2030
-- ---------------------------------------------------------------------
SELECT
    year,
    ROUND(AVG(coverage), 2) AS avg_measles_coverage,
    ROUND(100.0 * SUM(CASE WHEN coverage >= 95 THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_countries_at_target
FROM fact_coverage
WHERE antigen LIKE 'MCV1%'
GROUP BY year
ORDER BY year;
