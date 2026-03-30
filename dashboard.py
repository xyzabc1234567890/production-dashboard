import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Production Dashboard", layout="wide")

st.title("🚗 Production Dashboard")
st.markdown("### Plan vs Actual | Dropping | Rollout")

# -----------------------------
# GOOGLE SHEET LINK
# -----------------------------
sheet_url = "https://docs.google.com/spreadsheets/d/191zGMKGDlODL-DTkmSyLIJj8CNQh7S7iUBHe1kDTZK4/export?format=csv"

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(sheet_url, skiprows=1)

    # Clean column names
    df.columns = df.columns.str.strip()

    # Convert dates
    df["Dropping Date"] = pd.to_datetime(df["Dropping Date"], errors='coerce')
    df["Rollout Date"] = pd.to_datetime(df["Rollout Date"], errors='coerce')

    return df

df = load_data()

# -----------------------------
# SIDEBAR FILTER
# -----------------------------
st.sidebar.header("Filters")

models = st.sidebar.multiselect(
    "Select Model",
    df["Model :"].dropna().unique(),
    default=df["Model :"].dropna().unique()
)

df = df[df["Model :"].isin(models)]

# -----------------------------
# KPI SECTION
# -----------------------------
st.subheader("📊 Production Summary")

total_plan = len(df)
dropping_done = df["Dropping Date"].notna().sum()
rollout_done = df["Rollout Date"].notna().sum()

col1, col2, col3 = st.columns(3)

col1.metric("📦 Total Plan", total_plan)
col2.metric("⬇ Dropping Done", dropping_done)
col3.metric("🚚 Rolled Out", rollout_done)

# -----------------------------
# DAILY TREND
# -----------------------------
st.subheader("📈 Daily Trend")

drop = df.groupby("Dropping Date").size().reset_index(name="Dropping")
roll = df.groupby("Rollout Date").size().reset_index(name="Rollout")

trend = pd.merge(drop, roll,
                 left_on="Dropping Date",
                 right_on="Rollout Date",
                 how="outer").fillna(0)

trend["Date"] = trend["Dropping Date"].combine_first(trend["Rollout Date"])

fig = px.line(trend, x="Date", y=["Dropping", "Rollout"],
              markers=True)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# MODEL-WISE ANALYSIS
# -----------------------------
st.subheader("📊 Model-wise Plan vs Actual")

model_summary = df.groupby("Model :").agg({
    "Chassis No:": "count",
    "Dropping Date": lambda x: x.notna().sum(),
    "Rollout Date": lambda x: x.notna().sum()
}).reset_index()

model_summary.columns = ["Model", "Plan", "Dropping", "Rollout"]

fig2 = px.bar(model_summary,
              x="Model",
              y=["Plan", "Dropping", "Rollout"],
              barmode="group",
              text_auto=True)

st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# STATUS COLUMN (ADVANCED)
# -----------------------------
st.subheader("📌 Status Overview")

df["Status"] = df.apply(
    lambda x: "Rolled Out" if pd.notna(x["Rollout Date"])
    else ("Dropped" if pd.notna(x["Dropping Date"]) else "Pending"),
    axis=1
)

status_count = df["Status"].value_counts().reset_index()
status_count.columns = ["Status", "Count"]

fig3 = px.pie(status_count, names="Status", values="Count")

st.plotly_chart(fig3, use_container_width=True)

# -----------------------------
# DATA TABLE
# -----------------------------
st.subheader("📋 Data Table")
st.dataframe(df, use_container_width=True)
