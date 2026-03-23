import pandas as pd
import numpy as np
import os

np.random.seed(42)
N = 5000  # number of customers
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

customer_ids = [f"CUST_{str(i).zfill(5)}" for i in range(1, N + 1)]

age                  = np.random.randint(18, 70, N)
gender               = np.random.choice(["Male", "Female"], N)
country              = np.random.choice(["Germany", "France", "Netherlands",
                                          "Austria", "Switzerland"], N,
                                         p=[0.45, 0.20, 0.15, 0.10, 0.10])
tenure_months        = np.random.randint(1, 60, N)
num_orders           = np.random.poisson(lam=8, size=N)
avg_order_value      = np.round(np.random.uniform(20, 500, N), 2)
total_spend          = np.round(num_orders * avg_order_value, 2)
days_since_last_order= np.random.randint(1, 365, N)
num_returns          = np.random.poisson(lam=1.5, size=N)
num_complaints       = np.random.poisson(lam=0.8, size=N)
discount_used        = np.random.choice([0, 1], N, p=[0.4, 0.6])
newsletter_subscribed= np.random.choice([0, 1], N, p=[0.35, 0.65])
preferred_category   = np.random.choice(
    ["Electronics", "Fashion", "Home & Garden",
     "Sports", "Beauty", "Books"], N)
payment_method       = np.random.choice(
    ["Credit Card", "PayPal", "SEPA", "Klarna"], N,
    p=[0.30, 0.25, 0.25, 0.20])
device_type          = np.random.choice(
    ["Mobile", "Desktop", "Tablet"], N, p=[0.55, 0.35, 0.10])



churn_score = (
      0.03 * days_since_last_order
    + 0.15 * num_returns
    + 0.20 * num_complaints
    - 0.01 * tenure_months
    - 0.002 * total_spend
    + np.random.normal(0, 2, N)   # noise
)


churn_prob = 1 / (1 + np.exp(-0.15 * (churn_score - 5)))
churn      = (churn_prob > 0.5).astype(int)


df = pd.DataFrame({
    "customer_id"           : customer_ids,
    "age"                   : age,
    "gender"                : gender,
    "country"               : country,
    "tenure_months"         : tenure_months,
    "num_orders"            : num_orders,
    "avg_order_value"       : avg_order_value,
    "total_spend"           : total_spend,
    "days_since_last_order" : days_since_last_order,
    "num_returns"           : num_returns,
    "num_complaints"        : num_complaints,
    "discount_used"         : discount_used,
    "newsletter_subscribed" : newsletter_subscribed,
    "preferred_category"    : preferred_category,
    "payment_method"        : payment_method,
    "device_type"           : device_type,
    "churn"                 : churn
})


df.to_csv(os.path.join(DATA_DIR, "ecommerce_customers.csv"), index=False)

print(f" Dataset saved: {len(df)} rows, {df.shape[1]} columns")
print(f"   Churn rate: {df['churn'].mean():.1%}")
print(df.head())
