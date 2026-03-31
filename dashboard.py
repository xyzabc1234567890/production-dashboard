import streamlit as st
import pandas as pd

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
    df.columns = df.columns.str.strip().str.replace(":", "")

    return df

df = load_data()

# -----------------------------
# AUTO DETECT COLUMNS
# -----------------------------
model_col = [c for c in df.columns if "Model" in c][0]
drop_col = [c for c in df.columns if "Dropping" in c][0]
roll_col = [c for c in df.columns if "Rollout" in c][0]

# Convert to datetime
df[drop_col] = pd.to_datetime(df[drop_col], errors='coerce')
df[roll_col] = pd.to_datetime(df[roll_col], errors='coerce')

# -----------------------------
# SIDEBAR FILTER
# -----------------------------
st.sidebar.header("🔍 Filters")

models = st.sidebar.multiselect(
    "Select Model",
    df[model_col].dropna().unique(),
    default=df[model_col].dropna().unique()
)

df = df[df[model_col].isin(models)]

# -----------------------------
# KPI SECTION
# -----------------------------
st.subheader("📊 Production Summary")

total = len(df)
dropping_done = df[drop_col].notna().sum()
rollout_done = df[roll_col].notna().sum()

col1, col2, col3 = st.columns(3)

col1.metric("📦 Total Plan", total)
col2.metric("⬇ Dropping Done", dropping_done)
col3.metric("🚚 Rolled Out", rollout_done)

# -----------------------------
# DAILY TREND (NO PLOTLY)
# -----------------------------
st.subheader("📈 Daily Trend")

drop = df.groupby(drop_col).size()
roll = df.groupby(roll_col).size()

trend = pd.concat([drop, roll], axis=1)
trend.columns = ["Dropping", "Rollout"]
trend = trend.fillna(0)

st.line_chart(trend)

# -----------------------------
# MODEL-WISE ANALYSIS
# -----------------------------
st.subheader("📊 Model-wise Plan vs Actual")

summary = df.groupby(model_col).agg({
    model_col: "count",
    drop_col: lambda x: x.notna().sum(),
    roll_col: lambda x: x.notna().sum()
}).rename(columns={
    model_col: "Plan",
    drop_col: "Dropping",
    roll_col: "Rollout"
})

st.bar_chart(summary)

# -----------------------------
# STATUS TRACKING
# -----------------------------
st.subheader("📌 Status Overview")

df["Status"] = df.apply(
    lambda x: "Rolled Out" if pd.notna(x[roll_col])
    else ("Dropped" if pd.notna(x[drop_col]) else "Pending"),
    axis=1
)

status = df["Status"].value_counts()

st.bar_chart(status)

# -----------------------------
# DATA TABLE
# -----------------------------
st.subheader("📋 Data Table")
st.dataframe(df, use_container_width=True)
