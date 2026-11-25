
import pandas as pd
from database import get_connection

# Connect to PostgreSQL
conn = get_connection()

query = """
SELECT *
FROM public.oht_tyre_quality_staging;
"""

df = pd.read_sql_query(query, conn)
conn.close()

# Convert date
df["incident_date"] = pd.to_datetime(
    df["incident_date"],
    format="%d-%m-%Y",
    errors="coerce"
)

# 1. Basic information
print("\n--- BASIC DATA INFORMATION ---")
print("Total Incidents:", len(df))
print("Total Columns:", len(df.columns))

# 2. Defect-wise incidents
print("\n--- DEFECT-WISE INCIDENTS ---")
print(df["defect_type"].value_counts())

# 3. Plant-wise incidents
print("\n--- PLANT-WISE INCIDENTS ---")
print(df["plant_location"].value_counts())

# 4. Production line-wise incidents
print("\n--- LINE-WISE INCIDENTS ---")
print(df["line_no"].value_counts())

# 5. Root cause analysis
print("\n--- ROOT CAUSE CATEGORY ---")
print(df["root_cause_category"].value_counts())

# 6. Total rejection cost
print("\n--- TOTAL REJECTION COST ---")
print(df["rejection_cost_inr"].sum())

# 7. Average rejection cost
print("\n--- AVERAGE REJECTION COST ---")
print(df["rejection_cost_inr"].mean())

# 8. Status analysis
print("\n--- CAPA STATUS ---")
print(df["status"].value_counts())

# 9. Monthly incidents
print("\n--- MONTHLY INCIDENTS ---")
monthly = (
    df.groupby(df["incident_date"].dt.to_period("M"))
    .size()
)
print(monthly)
