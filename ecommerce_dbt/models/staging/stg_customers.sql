-- Staging model: clean and standardise raw customers data
-- Materialized as VIEW (no storage cost, always fresh)

WITH source AS (
    SELECT * FROM {{ ref('ecommerce_customers') }}
),

cleaned AS (
    SELECT
        -- Identifiers
        customer_id,

        -- Demographics
        CAST(age AS INTEGER)                    AS age,
        gender,
        country,

        -- Behavioural
        CAST(tenure_months AS INTEGER)          AS tenure_months,
        CAST(num_orders AS INTEGER)             AS num_orders,
        CAST(avg_order_value AS DOUBLE)         AS avg_order_value,
        CAST(total_spend AS DOUBLE)             AS total_spend,
        CAST(days_since_last_order AS INTEGER)  AS days_since_last_order,
        CAST(num_returns AS INTEGER)            AS num_returns,
        CAST(num_complaints AS INTEGER)         AS num_complaints,

        -- Engagement flags
        CAST(discount_used AS INTEGER)          AS discount_used,
        CAST(newsletter_subscribed AS INTEGER)  AS newsletter_subscribed,

        -- Preferences
        preferred_category,
        payment_method,
        device_type,

        -- Target
        CAST(churn AS INTEGER)                  AS churn

    FROM source
    WHERE customer_id IS NOT NULL
)

SELECT * FROM cleaned