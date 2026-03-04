-- Dimension table: enriched customer profile
-- Joins staging data with engineered features
-- Materialized as TABLE for Power BI performance

WITH customers AS (
    SELECT * FROM {{ ref('stg_customers') }}
),

enriched AS (
    SELECT
        -- Core identity
        customer_id,
        gender,
        country,
        age,
        tenure_months,

        -- Spend metrics
        num_orders,
        avg_order_value,
        total_spend,
        days_since_last_order,

        -- Behaviour
        num_returns,
        num_complaints,
        discount_used,
        newsletter_subscribed,
        preferred_category,
        payment_method,
        device_type,

        -- Engineered features
        ROUND(num_returns::DOUBLE
              / NULLIF(num_orders + 1, 0), 4)          AS return_rate,

        ROUND(num_complaints::DOUBLE
              / NULLIF(tenure_months + 1, 0), 4)       AS complaint_rate,

        ROUND(total_spend
              / NULLIF(num_orders + 1, 0), 2)          AS spend_per_order,

        ROUND(1.0
              / NULLIF(days_since_last_order + 1, 0), 6) AS recency_score,

        -- Business segments
        CASE
            WHEN total_spend >= 2000 THEN 'High Value'
            WHEN total_spend >= 800  THEN 'Mid Value'
            ELSE 'Low Value'
        END                                             AS customer_segment,

        -- Engagement score
        newsletter_subscribed + discount_used           AS engagement_score,

        -- Age group
        CASE
            WHEN age < 25 THEN '18-24'
            WHEN age < 35 THEN '25-34'
            WHEN age < 45 THEN '35-44'
            WHEN age < 55 THEN '45-54'
            ELSE '55+'
        END                                             AS age_group,

        -- Target
        churn

    FROM customers
)

SELECT * FROM enriched