import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

st.set_page_config(page_title="HR Analytics Dashboard", layout="wide")

CSV_PATH = "WA_Fn-UseC_-HR-Employee-Attrition.csv"

# Last updated
try:
    file_mtime = os.path.getmtime(CSV_PATH)
    last_updated_str = datetime.fromtimestamp(file_mtime).strftime('%Y-%m-%d %H:%M:%S')
except:
    file_mtime = 0
    last_updated_str = "Unknown"

# Header
col1, col2 = st.columns([0.85, 0.15])
with col1:
    st.title("HR Analytics Dashboard")
    st.markdown("Analyze employee attrition and performance metrics")

with col2:
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.caption(f"Last Updated: {last_updated_str}")

# Load data
@st.cache_data
def load_data(mtime):
    return pd.read_csv(CSV_PATH)

df = load_data(file_mtime)

# =========================
# FILTERS (FIXED)
# =========================
st.sidebar.header("Filters")

selected_dept = st.sidebar.multiselect(
    "Department",
    df["Department"].unique()
)

selected_role = st.sidebar.multiselect(
    "Job Role",
    df["JobRole"].unique()
)

filtered_df = df.copy()

if selected_dept:
    filtered_df = filtered_df[filtered_df["Department"].isin(selected_dept)]

if selected_role:
    filtered_df = filtered_df[filtered_df["JobRole"].isin(selected_role)]

if filtered_df.empty:
    st.warning("No data available")
    st.stop()

# =========================
# METRICS
# =========================
total = len(filtered_df)
attrition = len(filtered_df[filtered_df["Attrition"] == "Yes"])
rate = (attrition / total) * 100

avg_income = filtered_df["MonthlyIncome"].mean()
avg_age = filtered_df["Age"].mean()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Employees", total)
col2.metric("Attrition Rate", f"{rate:.2f}%")
col3.metric("Avg Income", f"${avg_income:,.0f}")
col4.metric("Avg Age", f"{avg_age:.1f}")

# =========================
# ATTRITION PIE
# =========================
attr_df = filtered_df["Attrition"].value_counts().reset_index()
attr_df.columns = ["Attrition", "Count"]

fig = px.pie(attr_df, values="Count", names="Attrition",
             color="Attrition",
             color_discrete_map={"Yes": "red", "No": "green"})
st.plotly_chart(fig, use_container_width=True)

# =========================
# DEPARTMENT
# =========================
dept = filtered_df.groupby(["Department", "Attrition"]).size().reset_index(name="Count")

fig = px.bar(dept, x="Department", y="Count", color="Attrition",
             barmode="group")
st.plotly_chart(fig, use_container_width=True)

# =========================
# AGE GROUP (FIXED)
# =========================
filtered_df = filtered_df.copy()

filtered_df["AgeGroup"] = pd.cut(
    filtered_df["Age"],
    bins=[18, 25, 35, 45, 55, 65],
    labels=["18-25", "26-35", "36-45", "46-55", "56-65"]
)

age_attr = filtered_df.groupby("AgeGroup")["Attrition"].apply(
    lambda x: (x == "Yes").mean() * 100
).reset_index(name="Rate")

fig = px.bar(age_attr, x="AgeGroup", y="Rate",
             color="Rate", color_continuous_scale="reds")
st.plotly_chart(fig, use_container_width=True)

# =========================
# JOB ROLE
# =========================
role_attr = filtered_df.groupby("JobRole")["Attrition"].apply(
    lambda x: (x == "Yes").mean() * 100
).reset_index(name="Rate")

fig = px.bar(role_attr, x="JobRole", y="Rate",
             color="Rate", color_continuous_scale="reds")
fig.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig, use_container_width=True)

# =========================
# SALARY RANGE (FIXED)
# =========================
filtered_df = filtered_df.copy()

filtered_df["SalaryRange"] = pd.cut(
    filtered_df["MonthlyIncome"],
    bins=[0, 2500, 5000, 7500, 10000, 15000, 30000],
    labels=["<2.5k", "2.5-5k", "5-7.5k", "7.5-10k", "10-15k", "15k+"]
)

sal = filtered_df.groupby("SalaryRange")["Attrition"].apply(
    lambda x: (x == "Yes").mean() * 100
).reset_index(name="Rate")

fig = px.bar(sal, x="SalaryRange", y="Rate",
             color="Rate", color_continuous_scale="reds")
st.plotly_chart(fig, use_container_width=True)

# =========================
# OVERTIME
# =========================
ot = filtered_df.groupby(["OverTime", "Attrition"]).size().reset_index(name="Count")

fig = px.bar(ot, x="OverTime", y="Count", color="Attrition",
             barmode="group")
st.plotly_chart(fig, use_container_width=True)

# =========================
# DEBUG (REMOVE LATER)
# =========================
st.write("Filtered rows:", filtered_df.shape)