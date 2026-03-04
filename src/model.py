import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (classification_report, roc_auc_score,
                              roc_curve, ConfusionMatrixDisplay)
import os

# ── Always resolve paths relative to project root ────────────────────────────
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR    = os.path.join(BASE_DIR, "data")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)

# ── Load ──────────────────────────────────────────────────────────────────────
df = pd.read_csv(os.path.join(DATA_DIR, "ecommerce_customers.csv"))
print(f"Loaded: {df.shape[0]} rows, {df.shape[1]} columns")

# ── Feature Engineering ───────────────────────────────────────────────────────
df["return_rate"]     = df["num_returns"]    / (df["num_orders"]             + 1)
df["complaint_rate"]  = df["num_complaints"] / (df["tenure_months"]          + 1)
df["spend_per_order"] = df["total_spend"]    / (df["num_orders"]             + 1)
df["recency_score"]   = 1                    / (df["days_since_last_order"]  + 1)

# ── Encode Categoricals ───────────────────────────────────────────────────────
cat_cols = ["gender", "country", "preferred_category",
            "payment_method", "device_type"]
le = LabelEncoder()
for col in cat_cols:
    df[col] = le.fit_transform(df[col])

# ── Features & Target ─────────────────────────────────────────────────────────
feature_cols = [
    "age", "gender", "country", "tenure_months", "num_orders",
    "avg_order_value", "total_spend", "days_since_last_order",
    "num_returns", "num_complaints", "discount_used",
    "newsletter_subscribed", "preferred_category", "payment_method",
    "device_type", "return_rate", "complaint_rate",
    "spend_per_order", "recency_score"
]
X = df[feature_cols]
y = df["churn"]

# ── Split & Scale ─────────────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)
scaler     = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc  = scaler.transform(X_test)

print(f"Train: {X_train.shape[0]} | Test: {X_test.shape[0]}")

# ── Train 3 Models ────────────────────────────────────────────────────────────
models = {
    "Logistic Regression" : LogisticRegression(max_iter=1000, random_state=42),
    "Random Forest"       : RandomForestClassifier(n_estimators=100,
                                                    random_state=42,
                                                    class_weight="balanced"),
    "Gradient Boosting"   : GradientBoostingClassifier(n_estimators=100,
                                                        learning_rate=0.1,
                                                        random_state=42)
}

results = {}
print("\n" + "=" * 60)
for name, model in models.items():
    print(f"\n--- {name} ---")
    model.fit(X_train_sc, y_train)
    y_pred  = model.predict(X_test_sc)
    y_proba = model.predict_proba(X_test_sc)[:, 1]
    auc     = roc_auc_score(y_test, y_proba)
    cv_auc  = cross_val_score(model, X_train_sc, y_train,
                               cv=5, scoring="roc_auc").mean()
    results[name] = {"model": model, "y_pred": y_pred,
                     "y_proba": y_proba, "auc": auc, "cv_auc": cv_auc}
    print(f"  AUC: {auc:.4f}  |  CV AUC: {cv_auc:.4f}")
    print(classification_report(y_test, y_pred,
                                 target_names=["Retained", "Churned"], digits=3))

best_name = max(results, key=lambda k: results[k]["auc"])
best      = results[best_name]
print(f"\nBest model: {best_name}  (AUC = {best['auc']:.4f})")

# ── Plot 1: ROC Curves ────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 6))
colors = ["#2E75B6", "#E05C5C", "#2CA02C"]
for (name, res), color in zip(results.items(), colors):
    fpr, tpr, _ = roc_curve(y_test, res["y_proba"])
    ax.plot(fpr, tpr, label=f"{name}  (AUC={res['auc']:.3f})",
            color=color, lw=2)
ax.plot([0, 1], [0, 1], "k--", lw=1)
ax.set_xlabel("False Positive Rate")
ax.set_ylabel("True Positive Rate")
ax.set_title("ROC Curves — Model Comparison", fontsize=14, fontweight="bold")
ax.legend(loc="lower right")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUTS_DIR, "09_roc_curves.png"), dpi=150)
plt.close()
print("Saved: 09_roc_curves.png")

# ── Plot 2: Confusion Matrix ──────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(6, 5))
ConfusionMatrixDisplay.from_predictions(
    y_test, best["y_pred"],
    display_labels=["Retained", "Churned"],
    cmap="Blues", ax=ax, colorbar=False)
ax.set_title(f"Confusion Matrix — {best_name}", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUTS_DIR, "10_confusion_matrix.png"), dpi=150)
plt.close()
print("Saved: 10_confusion_matrix.png")

# ── Plot 3: Feature Importance ────────────────────────────────────────────────
rf_model    = results["Random Forest"]["model"]
importances = pd.Series(rf_model.feature_importances_,
                         index=feature_cols).sort_values(ascending=True)
fig, ax = plt.subplots(figsize=(9, 7))
importances.tail(15).plot(kind="barh", color="#2E75B6",
                           edgecolor="white", ax=ax)
ax.set_title("Top 15 Feature Importances — Random Forest",
             fontsize=14, fontweight="bold")
ax.set_xlabel("Importance Score")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUTS_DIR, "11_feature_importance.png"), dpi=150)
plt.close()
print("Saved: 11_feature_importance.png")

# ── Plot 4: Model Comparison ──────────────────────────────────────────────────
model_names = list(results.keys())
auc_scores  = [results[n]["auc"]    for n in model_names]
cv_scores   = [results[n]["cv_auc"] for n in model_names]
x = np.arange(len(model_names))
w = 0.35
fig, ax = plt.subplots(figsize=(9, 5))
b1 = ax.bar(x - w/2, auc_scores, w, label="Test AUC",
            color="#2E75B6", edgecolor="white")
b2 = ax.bar(x + w/2, cv_scores,  w, label="CV AUC",
            color="#E05C5C", edgecolor="white")
for bar in list(b1) + list(b2):
    ax.text(bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.003,
            f"{bar.get_height():.3f}",
            ha="center", va="bottom", fontsize=10, fontweight="bold")
ax.set_xticks(x)
ax.set_xticklabels(model_names, fontsize=11)
ax.set_ylim(0, 1.1)
ax.set_ylabel("AUC-ROC Score")
ax.set_title("Model Comparison — Test vs CV AUC",
             fontsize=14, fontweight="bold")
ax.legend()
ax.axhline(y=0.8, color="green", linestyle="--", lw=1)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUTS_DIR, "12_model_comparison.png"), dpi=150)
plt.close()
print("Saved: 12_model_comparison.png")

# ── Save Predictions (for Databricks + Power BI) ─────────────────────────────
X_test_copy = X_test.copy()
X_test_copy["customer_id"]        = df.loc[X_test.index, "customer_id"].values
X_test_copy["actual_churn"]       = y_test.values
X_test_copy["predicted_churn"]    = best["y_pred"]
X_test_copy["churn_probability"]  = np.round(best["y_proba"], 4)
X_test_copy["churn_risk_segment"] = pd.cut(
    best["y_proba"],
    bins=[0, 0.3, 0.6, 1.0],
    labels=["Low Risk", "Medium Risk", "High Risk"]
)
X_test_copy.to_csv(os.path.join(DATA_DIR, "model_predictions.csv"), index=False)

# ── Save full decoded dataset for Power BI ────────────────────────────────────
cat_mapping = {
    "gender"            : {0: "Female",       1: "Male"},
    "country"           : {0: "Austria",      1: "France",       2: "Germany",
                           3: "Netherlands",  4: "Switzerland"},
    "preferred_category": {0: "Beauty",       1: "Books",        2: "Electronics",
                           3: "Fashion",      4: "Home & Garden",5: "Sports"},
    "payment_method"    : {0: "Credit Card",  1: "Klarna",
                           2: "PayPal",       3: "SEPA"},
    "device_type"       : {0: "Desktop",      1: "Mobile",       2: "Tablet"}
}
df_full = df.copy()
for col, mapping in cat_mapping.items():
    df_full[col] = df_full[col].map(mapping)

pred_slim  = X_test_copy[["customer_id", "predicted_churn",
                            "churn_probability", "churn_risk_segment"]]
df_powerbi = df_full.merge(pred_slim, on="customer_id", how="left")
df_powerbi.to_csv(os.path.join(DATA_DIR, "ecommerce_powerbi.csv"), index=False)

print(f"\nmodel_predictions.csv : {os.path.join(DATA_DIR, 'model_predictions.csv')}")
print(f"ecommerce_powerbi.csv : {os.path.join(DATA_DIR, 'ecommerce_powerbi.csv')}")
print(f"\nRisk segment breakdown:")
print(df_powerbi["churn_risk_segment"].value_counts())
print("\nPhase 1 complete. Ready for Phase 2 (Databricks).")