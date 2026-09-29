import os
import pandas as pd
import sweetviz as sv

print("==================================================")
print("1. LOADING RAW RAILWAY TRANSIT DATASET")
print("==================================================")

file_path = "data/raw/railway_transit_raw.csv"
df = pd.read_csv(file_path, low_memory=False)

print(f"Total Records: {df.shape[0]:,}")
print(f"Total Columns: {df.shape[1]}")
print("\nColumn Names and Data Types:")
print(df.dtypes)

print("\nMissing Values Count:")
missing = df.isnull().sum()
print(missing[missing > 0] if missing.sum() > 0 else "No missing values found.")

print("\n==================================================")
print("2. GENERATING SWEETVIZ PROFILING REPORT")
print("==================================================")
# Sample 25,000 records for fast, balanced automated visual profiling
sample_df = df.sample(min(25000, len(df)), random_state=42)

os.makedirs("reports", exist_ok=True)
report = sv.analyze(sample_df)

output_html = "reports/sweetviz_raw_data_profile.html"
report.show_html(filepath=output_html, open_browser=False)

print(f"\nAutomated profiling completed successfully!")
print(f"Report saved to: {output_html}")
