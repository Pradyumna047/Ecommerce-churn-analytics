-- Staging model: clean ML model predictions

WITH source AS (
    SELECT * FROM {{ ref('model_predictions') }}
),

cleaned AS (
    SELECT
        customer_id,
        CAST(actual_churn AS INTEGER)       AS actual_churn,
        CAST(predicted_churn AS INTEGER)    AS predicted_churn,
        CAST(churn_probability AS DOUBLE)   AS churn_probability,
        churn_risk_segment,

        -- Derived: was prediction correct?
        CASE
            WHEN actual_churn = predicted_churn THEN 1
            ELSE 0
        END                                 AS is_correct_prediction,

        -- Derived: prediction confidence band
        CASE
            WHEN churn_probability >= 0.8 THEN 'Very High Confidence'
            WHEN churn_probability >= 0.6 THEN 'High Confidence'
            WHEN churn_probability >= 0.4 THEN 'Medium Confidence'
            ELSE 'Low Confidence'
        END                                 AS confidence_band

    FROM source
    WHERE customer_id IS NOT NULL
)

SELECT * FROM cleaned