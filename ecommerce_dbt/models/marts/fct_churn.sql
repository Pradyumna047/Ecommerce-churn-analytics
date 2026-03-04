-- Fact table: one row per customer with full churn profile
-- Joins customer dimensions with ML predictions

WITH customers AS (
    SELECT * FROM {{ ref('dim_customers') }}
),

predictions AS (
    SELECT * FROM {{ ref('stg_predictions') }}
),

joined AS (
    SELECT
        -- Customer identity
        c.customer_id,
        c.country,
        c.customer_segment,
        c.age_group,
        c.preferred_category,
        c.payment_method,
        c.device_type,

        -- Spend & behaviour
        c.total_spend,
        c.num_orders,
        c.tenure_months,
        c.days_since_last_order,
        c.num_returns,
        c.num_complaints,
        c.engagement_score,
        c.return_rate,
        c.complaint_rate,
        c.spend_per_order,
        c.recency_score,

        -- Actual outcome
        c.churn                             AS actual_churn,

        -- Model predictions (may be null if customer not in test set)
        p.predicted_churn,
        p.churn_probability,
        p.churn_risk_segment,
        p.confidence_band,
        p.is_correct_prediction,

        -- Priority flag for CRM/retention campaigns
        CASE
            WHEN c.churn = 1
             AND c.num_complaints > 2      THEN 'URGENT'
            WHEN c.churn = 1              THEN 'AT RISK'
            ELSE 'STABLE'
        END                                 AS priority_flag,

        -- Revenue at risk (for Power BI KPI)
        CASE
            WHEN c.churn = 1
            THEN c.total_spend
            ELSE 0
        END                                 AS revenue_at_risk

    FROM customers c
    LEFT JOIN predictions p
        ON c.customer_id = p.customer_id
)

SELECT * FROM joined