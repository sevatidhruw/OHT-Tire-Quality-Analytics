CREATE TABLE public.oht_tyre_quality_staging (
    incident_id VARCHAR(50),
    incident_date VARCHAR(20),
    plant_location VARCHAR(100),
    line_no VARCHAR(50),
    product_category VARCHAR(100),
    defect_type VARCHAR(100),
    affected_qty INTEGER,
    unit_cost_inr NUMERIC(12,2),
    rejection_cost_inr NUMERIC(14,2),
    root_cause_category VARCHAR(100),
    root_cause_description TEXT,
    action_taken_capa TEXT,
    status VARCHAR(50),
    resolution_days INTEGER
);
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public'
AND table_name = 'oht_tyre_quality_staging'
ORDER BY ordinal_position;

SELECT COUNT(*)
FROM public.oht_tyre_quality_staging;
	
--Verify transferred records
SELECT COUNT(*) AS total_records
FROM public.oht_tyre_quality_staging;

--Preview the final table
SELECT *
FROM public.oht_tyre_quality_incident
LIMIT 10;
--Transfer data into the final table
SELECT
    incident_id,
    TO_DATE(incident_date, 'DD-MM-YYYY'),
    plant_location,
    line_no, 
    product_category,
    defect_type,
    affected_qty,
    unit_cost_inr,
    rejection_cost_inr,
    root_cause_category,
    root_cause_description,
    action_taken_capa,
    status,
    resolution_days
FROM oht_tyre_quality_staging;

--Verify your imported data
SELECT COUNT(*) AS total_incidents
FROM oht_tyre_quality_staging;

--Check missing values
SELECT
    COUNT(*) FILTER (WHERE incident_id IS NULL) AS missing_incident_id,
    COUNT(*) FILTER (WHERE defect_type IS NULL) AS missing_defect,
    COUNT(*) FILTER (WHERE rejection_cost_inr IS NULL) AS missing_cost,
    COUNT(*) FILTER (WHERE root_cause_category IS NULL) AS missing_root_cause
FROM oht_tyre_quality_staging;

--1.Which defect causes the highest rejection cost?
SELECT
    defect_type,
    SUM(affected_qty) AS total_affected_qty,
    SUM(rejection_cost_inr) AS total_rejection_cost
FROM public.oht_tyre_quality_staging
GROUP BY defect_type
ORDER BY total_rejection_cost DESC;

--2.Which production line has the most quality incidents?
SELECT
    line_no,
    COUNT(*) AS total_incidents,
    SUM(affected_qty) AS total_affected_qty,
    SUM(rejection_cost_inr) AS total_rejection_cost
FROM public.oht_tyre_quality_staging
GROUP BY line_no
ORDER BY total_incidents DESC;

-- 3.What are the major root causes?
SELECT
    root_cause_category,
    COUNT(*) AS total_incidents,
    SUM(affected_qty) AS total_affected_qty,
    SUM(rejection_cost_inr) AS total_rejection_cost
FROM public.oht_tyre_quality_staging
GROUP BY root_cause_category
ORDER BY total_incidents DESC;

--4. Which plant has the highest rejection cost?
SELECT
    plant_location,
    COUNT(*) AS total_incidents,
    SUM(rejection_cost_inr) AS total_rejection_cost
FROM public.oht_tyre_quality_staging
GROUP BY plant_location
ORDER BY total_rejection_cost DESC;

--5. Monthly rejection cost trend
SELECT
    DATE_TRUNC(
        'month',
        TO_DATE(incident_date::text, 'DD-MM-YYYY')
    ) AS incident_month,
    COUNT(*) AS total_incidents,
    SUM(rejection_cost_inr) AS monthly_rejection_cost
FROM public.oht_tyre_quality_staging
GROUP BY incident_month
ORDER BY incident_month;

--Which incidents took the longest to resolve?
SELECT
    incident_id,
    defect_type,
    root_cause_category,
    resolution_days,
    status,
    rejection_cost_inr
FROM public.oht_tyre_quality_staging
ORDER BY resolution_days DESC
LIMIT 10;

--Which defects have the highest financial impact?
SELECT
    defect_type,
    SUM(rejection_cost_inr) AS total_rejection_cost,
    ROUND(AVG(rejection_cost_inr), 2) AS avg_rejection_cost,
    SUM(affected_qty) AS total_affected_qty
FROM public.oht_tyre_quality_staging
GROUP BY defect_type
ORDER BY total_rejection_cost DESC
LIMIT 5;

--Calculate each defect's contribution to total rejection cost ?
SELECT
    defect_type,
    SUM(rejection_cost_inr) AS rejection_cost,
    ROUND(
        SUM(rejection_cost_inr) * 100.0 /
        NULLIF((SELECT SUM(rejection_cost_inr)
                FROM public.oht_tyre_quality_staging), 0),
        2
    ) AS cost_contribution_percent
FROM public.oht_tyre_quality_staging
GROUP BY defect_type
ORDER BY rejection_cost DESC;

--First analysis: Highest rejection cost defect
SELECT
    defect_type,
    SUM(affected_qty) AS total_affected_qty,
    SUM(rejection_cost_inr) AS total_rejection_cost
FROM public.oht_tyre_quality_staging
GROUP BY defect_type
ORDER BY total_rejection_cost DESC;
