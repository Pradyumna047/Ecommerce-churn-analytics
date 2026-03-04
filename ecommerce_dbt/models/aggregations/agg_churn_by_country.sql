SELECT
    country,
    COUNT(*)                                    AS total_customers,
    SUM(actual_churn)                           AS churned_customers,
    ROUND(AVG(actual_churn) * 100, 2)           AS churn_rate_pct,
    ROUND(AVG(total_spend), 2)                  AS avg_spend_eur,
    ROUND(SUM(revenue_at_risk), 2)              AS total_revenue_at_risk,
    ROUND(AVG(days_since_last_order), 1)        AS avg_days_inactive,
    ROUND(AVG(tenure_months), 1)                AS avg_tenure_months
FROM {{ ref('fct_churn') }}
GROUP BY country
ORDER BY churn_rate_pct DESC