SELECT
    preferred_category,
    COUNT(*)                                    AS total_customers,
    SUM(actual_churn)                           AS churned_customers,
    ROUND(AVG(actual_churn) * 100, 2)           AS churn_rate_pct,
    ROUND(AVG(total_spend), 2)                  AS avg_spend_eur,
    ROUND(SUM(revenue_at_risk), 2)              AS total_revenue_at_risk,
    ROUND(AVG(num_orders), 1)                   AS avg_orders,
    ROUND(AVG(return_rate), 4)                  AS avg_return_rate
FROM {{ ref('fct_churn') }}
GROUP BY preferred_category
ORDER BY churn_rate_pct DESC