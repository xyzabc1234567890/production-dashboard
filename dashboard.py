import streamlit as st
import pandas as pd

st.set_page_config(page_title="Production Dashboard", layout="wide")

st.title("🚗 Vehicle Production Dashboard")

# 🔹 Paste your Google Sheet ID here
sheet_id = "https://docs.google.com/spreadsheets/d/1IKPz6spdA00Cd_KN9y2cn67z1k54wKgJe7IgrxItzQ8/edit?usp=sharing"

url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"

# 🔹 Load Data
try:
    df = pd.read_csv(url)
except:
    st.error("⚠️ Unable to load data. Check Google Sheet sharing settings.")
    st.stop()

# 🔹 Clean column names
df.columns = df.columns.str.strip()

# 🔹 Convert date columns
date_cols = ["Date", "Roll Out", "Offered to QA", "MODEL DATE WISE"]
for col in date_cols:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')

# 🔹 Create Status Columns
df["Dropped"] = df["Date"].notna().astype(int)
df["Rolled Out"] = df["Roll Out"].notna().astype(int)
df["Offered"] = df["Offered to QA"].notna().astype(int)

# 🔹 Pending Logic
df["Pending"] = ((df["Dropped"] == 1) & (df["Rolled Out"] == 0)).astype(int)

# 🔹 KPI CARDS
col1, col2, col3, col4 = st.columns(4)

col1.metric("🚘 Dropped", df["Dropped"].sum())
col2.metric("🏭 Rolled Out", df["Rolled Out"].sum())
col3.metric("📦 Offered", df["Offered"].sum())
col4.metric("⏳ Pending", df["Pending"].sum())

st.divider()

# 🔹 SIDEBAR FILTERS
st.sidebar.header("Filters")

# Model Name filter (Remarks 2)
model_name = st.sidebar.selectbox(
    "Select Model Name",
    ["All"] + list(df["REMARKS 2"].dropna().unique())
)

# Loadbody filter
loadbody = st.sidebar.selectbox(
    "Select Loadbody Type",
    ["All"] + list(df["MODEL"].dropna().unique())
)

# 🔹 Apply Filters
filtered_df = df.copy()

if model_name != "All":
    filtered_df = filtered_df[filtered_df["REMARKS 2"] == model_name]

if loadbody != "All":
    filtered_df = filtered_df[filtered_df["MODEL"] == loadbody]

# 🔹 MODEL-WISE SUMMARY (Top Table)
summary = filtered_df.groupby("REMARKS 2")[["Dropped", "Rolled Out", "Offered", "Pending"]].sum()

st.subheader("📊 Model-wise Summary")
st.dataframe(summary)

# 🔹 TREND CHART
st.subheader("📈 Daily Dropping Trend")
trend = filtered_df.groupby("Date")["Dropped"].sum()
st.line_chart(trend)

# 🔹 LOADBODY INSTALLATION TREND
st.subheader("🏗️ Loadbody Installation Trend")
if "MODEL DATE WISE" in filtered_df.columns:
    loadbody_trend = filtered_df.groupby("MODEL DATE WISE")["Dropped"].sum()
    st.line_chart(loadbody_trend)

# 🔹 FULL DATA TABLE
st.subheader("📋 Detailed Data")
st.dataframe(filtered_df, use_container_width=True)
