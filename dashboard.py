import streamlit as st
import pandas as pd

st.title("🚗 Production Dashboard")

# Your Google Sheet ID
sheet_id = "1IKPz6spdA00Cd_KN9y2cn67z1k54wKgJe7IgrxItzQ8"

# IMPORTANT: add sheet name (gid=0 means first sheet)
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&gid=0"

# Load data
try:
    df = pd.read_csv(url)
    st.write("✅ Data Loaded Successfully")
    st.dataframe(df)

except Exception as e:
    st.error(f"Error loading data: {e}")
