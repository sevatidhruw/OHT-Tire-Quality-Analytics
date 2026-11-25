import pandas as pd
from database import get_connection

# Connect to PostgreSQL
conn = get_connection()

# Load data into Pandas
query = """
SELECT *
FROM public.oht_tyre_quality_staging;
"""

df = pd.read_sql_query(query, conn)

conn.close()

# Display data
print("\nDATA PREVIEW:")
print(df.head())

print("\nDATA INFORMATION:")
print(df.info())

print("\nTOTAL RECORDS:", len(df))

# Defect-wise rejection cost
print("\nDEFECT-WISE REJECTION COST:")

defect_analysis = (
    df.groupby("defect_type")["rejection_cost_inr"]
    .sum()
    .sort_values(ascending=False)
)

print(defect_analysis)


import pandas as pd
from database import get_connection

# ==================================
# 1. CONNECT TO POSTGRESQL
# ==================================

conn = get_connection()
cursor = conn.cursor()

query = """
SELECT *
FROM public.oht_tyre_quality_staging;
"""

cursor.execute(query)

rows = cursor.fetchall()
columns = [desc[0] for desc in cursor.description]

df = pd.DataFrame(rows, columns=columns)

cursor.close()
conn.close()

print("Original Data Shape:", df.shape)


# ==================================
# 2. CREATE A BACKUP
# ==================================

df_raw = df.copy()


# ==================================
# 3. REMOVE EXTRA SPACES
# ==================================

for col in df.select_dtypes(include="object").columns:
    df[col] = df[col].apply(
        lambda x: x.strip() if isinstance(x, str) else x
    )

# Convert empty strings into missing values
df = df.replace(r"^\s*$", pd.NA, regex=True)


# ==================================
# 4. CONVERT DATE COLUMN
# ==================================

df["incident_date"] = pd.to_datetime(
    df["incident_date"],
    format="%d-%m-%Y",
    errors="coerce"
)


# ==================================
# 5. CONVERT NUMERIC COLUMNS
# ==================================

numeric_columns = [
    "affected_qty",
    "unit_cost_inr",
    "rejection_cost_inr",
    "resolution_days"
]

for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")


# ==================================
# 6. CHECK MISSING VALUES
# ==================================

print("\nMISSING VALUES:")
print(df.isnull().sum())


# ==================================
# 7. CHECK DUPLICATES
# ==================================

print("\nDUPLICATE ROWS:", df.duplicated().sum())

print(
    "DUPLICATE INCIDENT IDs:",
    df["incident_id"].duplicated().sum()
)


# ==================================
# 8. CHECK INVALID VALUES
# ==================================

print("\nINVALID DATA CHECK:")

print("Invalid quantities:",
      (df["affected_qty"] < 0).sum())

print("Invalid unit costs:",
      (df["unit_cost_inr"] < 0).sum())

print("Invalid rejection costs:",
      (df["rejection_cost_inr"] < 0).sum())

print("Invalid resolution days:",
      (df["resolution_days"] < 0).sum())


# ==================================
# 9. STANDARDIZE TEXT COLUMNS
# ==================================

category_columns = [
    "plant_location",
    "product_category",
    "defect_type",
    "root_cause_category",
    "status"
]

for col in category_columns:
    df[col] = df[col].str.strip().str.title()


# ==================================
# 10. FINAL DATA QUALITY REPORT
# ==================================

print("\nCLEANED DATA SHAPE:", df.shape)

print("\nCLEANED DATA PREVIEW:")
print(df.head())

print("\nFINAL DATA TYPES:")
print(df.dtypes)


# ==================================
# 11. EXPORT CLEANED DATA
# ==================================

df.to_csv(
    "oht_tyre_quality_cleaned.csv",
    index=False
)

print("\nCleaned CSV file saved successfully!")



import plotly.express as px
import plotly.graph_objects as go

# Convert numeric columns
df["rejection_cost_inr"] = pd.to_numeric(
    df["rejection_cost_inr"], errors="coerce"
)
df["affected_qty"] = pd.to_numeric(
    df["affected_qty"], errors="coerce"
)
df["resolution_days"] = pd.to_numeric(
    df["resolution_days"], errors="coerce"
)

# 1. Defect-wise Rejection Cost
defect_cost = (
    df.groupby("defect_type", as_index=False)
      ["rejection_cost_inr"].sum()
      .sort_values("rejection_cost_inr", ascending=False)
)

fig1 = px.bar(
    defect_cost,
    x="defect_type",
    y="rejection_cost_inr",
    title="Defect-wise Rejection Cost",
    text_auto=".2s",
    labels={
        "defect_type": "Defect Type",
        "rejection_cost_inr": "Rejection Cost (INR)"
    }
)
fig1.show()

# 2. Production Line-wise Incidents
line_data = (
    df.groupby("line_no", as_index=False)
      .agg(total_incidents=("incident_id", "count"))
      .sort_values("total_incidents", ascending=False)
)

fig2 = px.bar(
    line_data,
    x="line_no",
    y="total_incidents",
    title="Production Line-wise Quality Incidents",
    text_auto=True
)
fig2.show()

# 3. Root Cause Analysis
root_cause = (
    df.groupby("root_cause_category", as_index=False)
      .agg(total_incidents=("incident_id", "count"))
      .sort_values("total_incidents", ascending=False)
)

fig3 = px.pie(
    root_cause,
    names="root_cause_category",
    values="total_incidents",
    title="Quality Incidents by Root Cause",
    hole=0.4
)
fig3.show()

# 4. CAPA Status
capa = df["status"].value_counts().reset_index()
capa.columns = ["status", "total_incidents"]

fig4 = px.pie(
    capa,
    names="status",
    values="total_incidents",
    title="CAPA Status Distribution",
    hole=0.4
)
fig4.show()

# 5. Monthly Rejection Cost Trend
df["incident_date"] = pd.to_datetime(
    df["incident_date"], errors="coerce", dayfirst=True
)

monthly = (
    df.dropna(subset=["incident_date"])
      .set_index("incident_date")
      .resample("ME")["rejection_cost_inr"]
      .sum()
      .reset_index()
)

fig5 = px.line(
    monthly,
    x="incident_date",
    y="rejection_cost_inr",
    markers=True,
    title="Monthly Rejection Cost Trend"
)
fig5.show()

# 6. Affected Quantity by Defect
quantity = (
    df.groupby("defect_type", as_index=False)
      ["affected_qty"].sum()
      .sort_values("affected_qty", ascending=False)
)

fig6 = px.bar(
    quantity,
    x="defect_type",
    y="affected_qty",
    title="Affected Quantity by Defect",
    text_auto=True
)
fig6.show()

print("All Plotly visualizations generated successfully!")
