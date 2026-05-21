import pandas as pd

df = pd.read_csv("data/jobs.csv")

print(f"Total jobs loaded: {len(df)}")
print(f"Columns: {list(df.columns)}")
print("\nFirst 3 rows:")
print(df.head(3))