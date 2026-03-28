import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("🚗 Production Dashboard")

# Google Sheet ID
sheet_id = "1IKPz6spdA00Cd_KN9y2cn67z1k54wKgJe7IgrxItzQ8"

# Load Data
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&gid=0"
df = pd.read_csv(url)

# Clean column names
df.columns = df.columns.str.strip()

# Rename columns (based on your explanation)
df.rename(columns={
    "MODEL": "Loadbody_Type",
    "MODEL DATE WISE": "Fitment_Date",
    "Date": "Dropping_Date",
    "Roll Out": "Rollout_Date",
    "Offered to QA": "PDI_Date",
    "REMARKS 2": "Model_Name"
}, inplace=True)

# Convert to datetime
df["Dropping_Date"] = pd.to_datetime(df["Dropping_Date"], errors='coerce')
df["Rollout_Date"] = pd.to_datetime(df["Rollout_Date"], errors='coerce')
df["PDI_Date"] = pd.to_datetime(df["PDI_Date"], errors='coerce')

# Create count flags
df["Drop"] = df["Dropping_Date"].notna().astype(int)
df["Rollout"] = df["Rollout_Date"].notna().astype(int)
df["PDI"] = df["PDI_Date"].notna().astype(int)

# ================= KPI SECTION =================
st.subheader("📊 Overall KPIs")
col1, col2, col3 = st.columns(3)

col1.metric("Total Dropping", df["Drop"].sum())
col2.metric("Total Rollout", df["Rollout"].sum())
col3.metric("Total PDI Offered", df["PDI"].sum())

# ================= MODEL WISE =================
st.subheader("📌 Model-wise Summary")

model_summary = df.groupby("Model_Name").agg({
    "Drop": "sum",
    "Rollout": "sum",
    "PDI": "sum"
}).reset_index()

st.dataframe(model_summary)

# ================= DAILY TREND =================
st.subheader("📈 Daily Production Trend")

# Group by date
drop_trend = df.groupby("Dropping_Date")["Drop"].sum()
rollout_trend = df.groupby("Rollout_Date")["Rollout"].sum()
pdi_trend = df.groupby("PDI_Date")["PDI"].sum()

# Combine into one dataframe
trend_df = pd.concat([drop_trend, rollout_trend, pdi_trend], axis=1)
trend_df.columns = ["Dropping", "Rollout", "PDI"]

trend_df = trend_df.fillna(0)

# Show line chart
st.line_chart(trend_df)
