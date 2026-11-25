
import streamlit as st
import pandas as pd
import plotly.express as px
from database import get_connection

st.set_page_config(
    page_title="OHT Tyre Quality Analytics",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ OHT Tyre Quality Incident Analytics")
st.caption("Manufacturing Quality | Rejection Cost | Root Cause | CAPA")

# Load PostgreSQL data
@st.cache_data(ttl=60)
def load_data():
    conn = get_connection()
    try:
        df = pd.read_sql_query(
            "SELECT * FROM public.oht_tyre_quality_staging",
            conn
        )
    finally:
        conn.close()

    df["incident_date"] = pd.to_datetime(
        df["incident_date"], errors="coerce", dayfirst=True
    )

    for col in [
        "affected_qty", "rejection_cost_inr", "resolution_days"
    ]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df

df = load_data()

# Sidebar filters
st.sidebar.header("Dashboard Filters")

defects = st.sidebar.multiselect(
    "Select Defect Type",
    sorted(df["defect_type"].dropna().unique()),
    default=sorted(df["defect_type"].dropna().unique())
)

lines = st.sidebar.multiselect(
    "Select Production Line",
    sorted(df["line_no"].dropna().unique()),
    default=sorted(df["line_no"].dropna().unique())
)

statuses = st.sidebar.multiselect(
    "Select CAPA Status",
    sorted(df["status"].dropna().unique()),
    default=sorted(df["status"].dropna().unique())
)

filtered = df[
    df["defect_type"].isin(defects)
    & df["line_no"].isin(lines)
    & df["status"].isin(statuses)
].copy()

# KPI Cards
total_incidents = len(filtered)
affected_qty = filtered["affected_qty"].sum()
rejection_cost = filtered["rejection_cost_inr"].sum()
avg_resolution = filtered["resolution_days"].mean()

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Incidents", f"{total_incidents:,}")
c2.metric("Affected Quantity", f"{affected_qty:,.0f}")
c3.metric("Rejection Cost", f"₹{rejection_cost:,.0f}")
c4.metric(
    "Avg Resolution Days",
    f"{avg_resolution:.1f}" if pd.notna(avg_resolution) else "N/A"
)

st.divider()

# Defect analysis
left, right = st.columns(2)

with left:
    defect_data = (
        filtered.groupby("defect_type", as_index=False)
        ["rejection_cost_inr"].sum()
        .sort_values("rejection_cost_inr", ascending=False)
    )

    fig = px.bar(
        defect_data,
        x="defect_type",
        y="rejection_cost_inr",
        title="Defect-wise Rejection Cost"
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    line_data = (
        filtered.groupby("line_no", as_index=False)
        .agg(total_incidents=("incident_id", "count"))
    )

    fig = px.bar(
        line_data,
        x="line_no",
        y="total_incidents",
        title="Production Line-wise Incidents"
    )
    st.plotly_chart(fig, use_container_width=True)

# Root cause and CAPA
left, right = st.columns(2)

with left:
    root_data = filtered["root_cause_category"].value_counts().reset_index()
    root_data.columns = ["root_cause_category", "incidents"]

    fig = px.pie(
        root_data,
        names="root_cause_category",
        values="incidents",
        title="Root Cause Distribution",
        hole=0.4
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    capa_data = filtered["status"].value_counts().reset_index()
    capa_data.columns = ["status", "incidents"]

    fig = px.pie(
        capa_data,
        names="status",
        values="incidents",
        title="CAPA Status Distribution",
        hole=0.4
    )
    st.plotly_chart(fig, use_container_width=True)

# Monthly rejection cost trend
monthly = (
    filtered.dropna(subset=["incident_date"])
    .set_index("incident_date")
    .resample("ME")["rejection_cost_inr"]
    .sum()
    .reset_index()
)

fig = px.line(
    monthly,
    x="incident_date",
    y="rejection_cost_inr",
    markers=True,
    title="Monthly Rejection Cost Trend"
)
st.plotly_chart(fig, use_container_width=True)

# Data table
st.subheader("Quality Incident Details")
st.dataframe(filtered, use_container_width=True)

# Download filtered data
st.download_button(
    "Download Analysis Data",
    filtered.to_csv(index=False).encode("utf-8"),
    file_name="OHT_Tyre_Quality_Analysis.csv",
    mime="text/csv"
)


# ==========================================
# BUSINESS INSIGHTS & RECOMMENDATIONS
# ==========================================

st.divider()
st.header("Business Insights & Recommendations")

if not filtered.empty:

    # 1. Highest cost defect
    defect_cost = (
        filtered.groupby("defect_type")["rejection_cost_inr"]
        .sum()
        .sort_values(ascending=False)
    )

    highest_defect = defect_cost.index[0]
    highest_defect_cost = defect_cost.iloc[0]

    total_cost = filtered["rejection_cost_inr"].sum()

    defect_contribution = (
        highest_defect_cost / total_cost * 100
        if total_cost > 0 else 0
    )

    st.subheader("1. Highest Financial Impact")

    st.write(
        f"**{highest_defect}** is the highest-cost defect, "
        f"contributing ₹{highest_defect_cost:,.0f} "
        f"({defect_contribution:.1f}% of total rejection cost)."
    )

    # 2. Production line
    line_incidents = filtered["line_no"].value_counts()

    highest_line = line_incidents.index[0]
    highest_line_count = line_incidents.iloc[0]

    st.subheader("2. Production Line Performance")

    st.write(
        f"Production line **{highest_line}** has the highest "
        f"number of recorded incidents: {highest_line_count}."
    )

    # 3. Root cause
    root_causes = filtered["root_cause_category"].value_counts()

    if not root_causes.empty:
        major_cause = root_causes.index[0]
        major_cause_count = root_causes.iloc[0]

        st.subheader("3. Major Root Cause")

        st.write(
            f"**{major_cause}** is the most frequently recorded "
            f"root cause category, with {major_cause_count} incidents."
        )

    # 4. CAPA status
    capa_status = filtered["status"].astype(str).str.strip().str.lower()

    closed_count = capa_status.isin(
        ["closed", "completed"]
    ).sum()

    open_count = capa_status.isin(
        ["open", "pending", "in progress"]
    ).sum()

    st.subheader("4. Corrective Action Status")

    st.write(f"Closed/completed incidents: **{closed_count}**")
    st.write(f"Open/pending/in-progress incidents: **{open_count}**")

    # 5. Resolution time
    avg_days = filtered["resolution_days"].mean()

    st.subheader("5. Resolution Performance")

    if pd.notna(avg_days):
        st.write(
            f"Average incident resolution time: **{avg_days:.1f} days**."
        )

    # 6. Management recommendations
    st.subheader("6. Management Recommendations")

    st.markdown("""
    - Prioritize investigation of the highest-cost defect.
    - Conduct process audits on the production line with the most incidents.
    - Validate major root causes using process data and 5 Why analysis.
    - Review pending CAPA actions and assign clear responsibility.
    - Monitor monthly rejection cost to measure improvement.
    - Verify CAPA effectiveness by tracking repeat defects after closure.
    """)

else:
    st.warning("No records available for the selected filters.")
