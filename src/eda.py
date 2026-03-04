import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ── Always resolve paths relative to project root ────────────────────────────
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR    = os.path.join(BASE_DIR, "data")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)

# ── Load data ─────────────────────────────────────────────────────────────────
csv_path = os.path.join(DATA_DIR, "ecommerce_customers.csv")
df = pd.read_csv(csv_path)

# FIX: Create a string label column for churn.
# Newer seaborn (0.13+) requires palette keys to match the ACTUAL values
# in the column — not integers. Using a string column avoids all palette errors.
df["churn_label"] = df["churn"].map({0: "Retained", 1: "Churned"})

sns.set_theme(style="whitegrid", palette="muted")

print("=" * 50)
print("DATASET OVERVIEW")
print("=" * 50)
print(f"Shape         : {df.shape}")
print(f"\nMissing values:\n{df.isnull().sum()}")
print(f"\nChurn distribution:\n{df['churn'].value_counts(normalize=True).round(3)}")
print(f"\nData types:\n{df.dtypes}")
print(f"\nNumerical summary:")
print(df.describe().round(2))

# ── Plot 1: Churn Distribution ────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(6, 4))
counts = df["churn"].value_counts().sort_index()
labels = ["Retained (0)", "Churned (1)"]
bars   = ax.bar(labels, counts.values,
                color=["#2E75B6", "#E05C5C"],
                edgecolor="white", width=0.5)
for bar, val in zip(bars, counts.values):
    ax.text(bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 30,
            f"{val}\n({val/len(df):.1%})",
            ha="center", va="bottom", fontsize=11, fontweight="bold")
ax.set_title("Churn Distribution", fontsize=14, fontweight="bold")
ax.set_ylabel("Number of Customers")
ax.set_ylim(0, counts.max() * 1.2)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUTS_DIR, "01_churn_distribution.png"), dpi=150)
plt.close()
print("Saved: 01_churn_distribution.png")

# ── Plot 2: Churn Rate by Country ─────────────────────────────────────────────
# FIX: use set_xticks() BEFORE set_xticklabels() to avoid FixedLocator warning
churn_by_country = (df.groupby("country")["churn"]
                      .mean()
                      .sort_values(ascending=False))
fig, ax = plt.subplots(figsize=(8, 4))
x_pos = list(range(len(churn_by_country)))
bars  = ax.bar(x_pos, churn_by_country.values,
               color="#2E75B6", edgecolor="white")
for bar, val in zip(bars, churn_by_country.values):
    ax.text(bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.005,
            f"{val:.1%}", ha="center", va="bottom", fontsize=10)
ax.set_title("Churn Rate by Country", fontsize=14, fontweight="bold")
ax.set_ylabel("Churn Rate")
ax.set_xticks(x_pos)
ax.set_xticklabels(list(churn_by_country.index), rotation=30, ha="right")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUTS_DIR, "02_churn_by_country.png"), dpi=150)
plt.close()
print("Saved: 02_churn_by_country.png")

# ── Plot 3: Days Since Last Order — Churned vs Retained ───────────────────────
# FIX: use hue="churn_label" with string palette keys
fig, ax = plt.subplots(figsize=(8, 4))
sns.histplot(data=df, x="days_since_last_order", hue="churn_label",
             bins=40,
             palette={"Retained": "#2E75B6", "Churned": "#E05C5C"},
             alpha=0.7, ax=ax)
ax.set_title("Days Since Last Order: Churned vs Retained",
             fontsize=14, fontweight="bold")
ax.set_xlabel("Days Since Last Order")
ax.set_ylabel("Count")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUTS_DIR, "03_days_since_order.png"), dpi=150)
plt.close()
print("Saved: 03_days_since_order.png")

# ── Plot 4: Correlation Heatmap ───────────────────────────────────────────────
numeric_cols = ["age", "tenure_months", "num_orders", "avg_order_value",
                "total_spend", "days_since_last_order",
                "num_returns", "num_complaints",
                "discount_used", "newsletter_subscribed", "churn"]
fig, ax = plt.subplots(figsize=(11, 8))
sns.heatmap(df[numeric_cols].corr(),
            annot=True, fmt=".2f",
            cmap="coolwarm", linewidths=0.5,
            vmin=-1, vmax=1, ax=ax)
ax.set_title("Correlation Heatmap — All Numeric Features",
             fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUTS_DIR, "04_correlation_heatmap.png"), dpi=150)
plt.close()
print("Saved: 04_correlation_heatmap.png")

# ── Plot 5: Total Spend by Churn ──────────────────────────────────────────────
# FIX: pass hue= explicitly and set legend=False to silence FutureWarning
fig, ax = plt.subplots(figsize=(8, 4))
sns.boxplot(data=df, x="churn_label", y="total_spend",
            hue="churn_label",
            palette={"Retained": "#2E75B6", "Churned": "#E05C5C"},
            width=0.4, legend=False, ax=ax)
ax.set_title("Total Spend by Churn Status", fontsize=14, fontweight="bold")
ax.set_xlabel("")
ax.set_ylabel("Total Spend (EUR)")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUTS_DIR, "05_spend_by_churn.png"), dpi=150)
plt.close()
print("Saved: 05_spend_by_churn.png")

# ── Plot 6: Churn Rate by Product Category ────────────────────────────────────
# FIX: same set_xticks() before set_xticklabels() pattern
churn_by_cat = (df.groupby("preferred_category")["churn"]
                  .mean()
                  .sort_values(ascending=False))
fig, ax = plt.subplots(figsize=(8, 4))
x_pos = list(range(len(churn_by_cat)))
bars  = ax.bar(x_pos, churn_by_cat.values,
               color="#2E75B6", edgecolor="white")
for bar, val in zip(bars, churn_by_cat.values):
    ax.text(bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.003,
            f"{val:.1%}", ha="center", va="bottom", fontsize=10)
ax.set_title("Churn Rate by Product Category", fontsize=14, fontweight="bold")
ax.set_ylabel("Churn Rate")
ax.set_xticks(x_pos)
ax.set_xticklabels(list(churn_by_cat.index), rotation=30, ha="right")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUTS_DIR, "06_churn_by_category.png"), dpi=150)
plt.close()
print("Saved: 06_churn_by_category.png")

# ── Plot 7: Churn Rate by Payment Method ──────────────────────────────────────
churn_by_pay = (df.groupby("payment_method")["churn"]
                  .mean()
                  .sort_values(ascending=False))
fig, ax = plt.subplots(figsize=(8, 4))
x_pos = list(range(len(churn_by_pay)))
bars  = ax.bar(x_pos, churn_by_pay.values,
               color="#E05C5C", edgecolor="white")
for bar, val in zip(bars, churn_by_pay.values):
    ax.text(bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.003,
            f"{val:.1%}", ha="center", va="bottom", fontsize=10)
ax.set_title("Churn Rate by Payment Method", fontsize=14, fontweight="bold")
ax.set_ylabel("Churn Rate")
ax.set_xticks(x_pos)
ax.set_xticklabels(list(churn_by_pay.index), rotation=20, ha="right")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUTS_DIR, "07_churn_by_payment.png"), dpi=150)
plt.close()
print("Saved: 07_churn_by_payment.png")

# ── Plot 8: Tenure by Churn — Violin Plot ─────────────────────────────────────
# FIX: hue= + legend=False pattern same as boxplot fix
fig, ax = plt.subplots(figsize=(8, 4))
sns.violinplot(data=df, x="churn_label", y="tenure_months",
               hue="churn_label",
               palette={"Retained": "#2E75B6", "Churned": "#E05C5C"},
               inner="quartile", legend=False, ax=ax)
ax.set_title("Customer Tenure by Churn Status", fontsize=14, fontweight="bold")
ax.set_xlabel("")
ax.set_ylabel("Tenure (Months)")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUTS_DIR, "08_tenure_by_churn.png"), dpi=150)
plt.close()
print("Saved: 08_tenure_by_churn.png")

print(f"\nAll 8 EDA charts saved to: {OUTPUTS_DIR}")