SELECT
    customer_segment,
    priority_flag,
    COUNT(*)                                    AS total_customers,
    SUM(actual_churn)                           AS churned_customers,
    ROUND(AVG(actual_churn) * 100, 2)           AS churn_rate_pct,
    ROUND(SUM(revenue_at_risk), 2)              AS total_revenue_at_risk,
    ROUND(AVG(churn_probability) * 100, 2)      AS avg_churn_prob_pct,
    ROUND(AVG(total_spend), 2)                  AS avg_spend_eur,
    ROUND(AVG(complaint_rate), 4)               AS avg_complaint_rate
FROM {{ ref('fct_churn') }}
GROUP BY customer_segment, priority_flag
ORDER BY total_revenue_at_risk DESC