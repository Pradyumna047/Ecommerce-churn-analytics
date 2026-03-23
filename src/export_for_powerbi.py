import duckdb
import os


BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DBT_DB     = os.path.join(BASE_DIR, "ecommerce_dbt", "ecommerce.duckdb")
EXPORT_DIR = os.path.join(BASE_DIR, "data", "powerbi_exports")
os.makedirs(EXPORT_DIR, exist_ok=True)


print(f"Connecting to: {DBT_DB}")
con = duckdb.connect(DBT_DB)


print("\nAvailable tables:")
tables = con.execute("SHOW TABLES").fetchall()
for t in tables:
    print(f"  {t[0]}")


exports = [
    ("fct_churn",              "fct_churn.csv"),
    ("dim_customers",          "dim_customers.csv"),
    ("agg_churn_by_country",   "agg_churn_by_country.csv"),
    ("agg_churn_by_category",  "agg_churn_by_category.csv"),
    ("agg_churn_by_segment",   "agg_churn_by_segment.csv"),
]

print("\nExporting tables...")
for table_name, file_name in exports:
    try:
        df = con.execute(f"SELECT * FROM {table_name}").df()
        output_path = os.path.join(EXPORT_DIR, file_name)
        df.to_csv(output_path, index=False)
        print(f"  Saved: {file_name} ({len(df):,} rows)")
    except Exception as e:
        print(f"  ERROR on {table_name}: {e}")

con.close()
print(f"\nAll exports saved to: {EXPORT_DIR}")
print("Ready to connect Power BI.")
