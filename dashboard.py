import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("🚗 Production Dashboard")

# Google Sheet ID
sheet_id = "1IKPz6spdA00Cd_KN9y2cn67z1k54wKgJe7IgrxItzQ8"

# Load data
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&gid=0"
df = pd.read_csv(url)

# Clean column names (VERY IMPORTANT)
df.columns = df.columns.str.strip()

# Rename for easy use
df.rename(columns={
    "Dropping Date": "Dropping",
    "Roll Out Date": "Rollout",
    "Offered to QA": "PDI",
    "Model": "Model_Name"
}, inplace=True)

# Convert to datetime
df["Dropping"] = pd.to_datetime(df["Dropping"], errors='coerce')
df["Rollout"] = pd.to_datetime(df["Rollout"], errors='coerce')
df["PDI"] = pd.to_datetime(df["PDI"], errors='coerce')

# Create count flags
df["Drop_Count"] = df["Dropping"].notna().astype(int)
df["Rollout_Count"] = df["Rollout"].notna().astype(int)
df["PDI_Count"] = df["PDI"].notna().astype(int)

# ================= KPI =================
st.subheader("📊 Overall KPIs")

col1, col2, col3 = st.columns(3)
col1.metric("Total Dropping", df["Drop_Count"].sum())
col2.metric("Total Rollout", df["Rollout_Count"].sum())
col3.metric("Total PDI Offered", df["PDI_Count"].sum())

# ================= MODEL SUMMARY =================
st.subheader("📌 Model-wise Production Summary")

model_summary = df.groupby("Model_Name").agg({
    "Drop_Count": "sum",
    "Rollout_Count": "sum",
    "PDI_Count": "sum"
}).reset_index()

model_summary.columns = ["Model", "Dropping", "Rollout", "PDI"]

st.dataframe(model_summary, use_container_width=True)

# ================= DAILY TREND =================
st.subheader("📈 Daily Production Trend")

drop_trend = df.groupby("Dropping")["Drop_Count"].sum()
rollout_trend = df.groupby("Rollout")["Rollout_Count"].sum()
pdi_trend = df.groupby("PDI")["PDI_Count"].sum()

trend_df = pd.concat([drop_trend, rollout_trend, pdi_trend], axis=1)
trend_df.columns = ["Dropping", "Rollout", "PDI"]
trend_df = trend_df.fillna(0)

st.line_chart(trend_df)

# ================= RAW DATA (OPTIONAL) =================
with st.expander("🔍 View Raw Data"):
    st.dataframe(df)
