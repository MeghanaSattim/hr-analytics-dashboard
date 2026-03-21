import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# Set page configuration
st.set_page_config(page_title="HR Analytics Dashboard", layout="wide")

# Dataset Path
CSV_PATH = "WA_Fn-UseC_-HR-Employee-Attrition.csv"

# Get last modified time
try:
    file_mtime = os.path.getmtime(CSV_PATH)
    last_updated_str = datetime.fromtimestamp(file_mtime).strftime('%Y-%m-%d %H:%M:%S')
except Exception:
    file_mtime = 0
    last_updated_str = "Unknown"

# Title and Header
col1, col2 = st.columns([0.85, 0.15])
with col1:
    st.title("HR Analytics Dashboard")
    st.markdown("Analyze employee attrition and performance metrics based on the HR dataset.")

with col2:
    st.write("") # Padding
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.caption(f"**Last Updated:**  \n{last_updated_str}")

# Load data
@st.cache_data
def load_data(mtime):
    df = pd.read_csv(CSV_PATH)
    return df

try:
    df = load_data(file_mtime)
except Exception as e:
    st.error(f"Error loading dataset: {e}")
    st.stop()

# Sidebar filters
st.sidebar.header("Filter Results")
selected_dept = st.sidebar.multiselect("Department", options=df["Department"].unique(), default=df["Department"].unique())
selected_role = st.sidebar.multiselect("Job Role", options=df["JobRole"].unique(), default=df["JobRole"].unique())

filtered_df = df[(df["Department"].isin(selected_dept)) & (df["JobRole"].isin(selected_role))]

if filtered_df.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

# ==========================================
# 1. PROBLEM: ATTRITION OVERVIEW
# ==========================================
st.header("1. 📉 Problem: Attrition Overview")
st.markdown("**What is our current attrition rate, and where are we fundamentally losing people?**")

total_employees = len(filtered_df)
attrition_count = len(filtered_df[filtered_df["Attrition"] == "Yes"])
attrition_rate = (attrition_count / total_employees) * 100 if total_employees > 0 else 0
avg_monthly_income = filtered_df["MonthlyIncome"].mean()
avg_age = filtered_df["Age"].mean()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Employees", total_employees)
col2.metric("Attrition Rate", f"{attrition_rate:.2f}%")
col3.metric("Avg Monthly Income", f"${avg_monthly_income:,.2f}")
col4.metric("Avg Age", f"{avg_age:.1f} years")

col_a, col_b = st.columns(2)
with col_a:
    attr_summary = filtered_df["Attrition"].value_counts().reset_index()
    attr_summary.columns = ["Attrition", "Count"]
    fig_overview = px.pie(attr_summary, values="Count", names="Attrition", hole=0.5,
                           title="Global Attrition Overview", color="Attrition",
                           color_discrete_map={"Yes": "#EF553B", "No": "#00CC96"})
    st.plotly_chart(fig_overview, use_container_width=True)
    st.caption("📝 **Insight:** The baseline company-wide attrition rate sits at ~16%, representing a massive compounding expense.")

with col_b:
    dept_attr = filtered_df.groupby(["Department", "Attrition"]).size().reset_index(name="Count")
    fig_dept = px.bar(dept_attr, x="Department", y="Count", color="Attrition",
                      title="Total Attrition by Department", barmode="group",
                      color_discrete_map={"Yes": "#EF553B", "No": "#00CC96"})
    st.plotly_chart(fig_dept, use_container_width=True)
    st.caption("📝 **Insight:** R&D experiences the highest sheer volume of departures, threatening core product knowledge.")

st.divider()

# ==========================================
# 2. CAUSE: DEMOGRAPHICS & DRIVERS
# ==========================================
st.header("2. 🔍 Cause: Key Attrition Drivers")
st.markdown("**Which employee groups and demographic factors correlate with the highest flight risk?**")

col_c, col_d = st.columns(2)
with col_c:
    age_bins = [17, 25, 35, 45, 55, 65]
    age_labels = ["18-25", "26-35", "36-45", "46-55", "56-65"]
    if not filtered_df.empty:
        filtered_df["AgeGroup"] = pd.cut(filtered_df["Age"], bins=age_bins, labels=age_labels)
        age_attr = filtered_df.groupby("AgeGroup", observed=False)["Attrition"].apply(lambda x: (x == "Yes").mean() * 100).reset_index(name="Attrition Rate (%)")
        fig_age = px.bar(age_attr, x="AgeGroup", y="Attrition Rate (%)", title="Attrition Rate by Age Group",
                         color="Attrition Rate (%)", color_continuous_scale="Reds")
        st.plotly_chart(fig_age, use_container_width=True)
        st.caption("📝 **Insight:** Flight risk is critically high (~35%+) for employees under 26 and drops dramatically as age increases.")

with col_d:
    role_attr_pct = filtered_df.groupby("JobRole")["Attrition"].apply(lambda x: (x == "Yes").mean() * 100).reset_index(name="Attrition Rate (%)")
    role_attr_pct = role_attr_pct.sort_values(by="Attrition Rate (%)", ascending=False)
    fig_role_attr = px.bar(role_attr_pct, x="JobRole", y="Attrition Rate (%)", title="Attrition Rate by Job Role",
                           color="Attrition Rate (%)", color_continuous_scale="Reds")
    fig_role_attr.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_role_attr, use_container_width=True)
    st.caption("📝 **Insight:** Sales Representatives and Lab Technicians face significantly higher proportional attrition than Management roles.")

st.markdown("### ⚠️ Top 3 High-Risk Roles")
top_3_roles = role_attr_pct.head(3)
if not top_3_roles.empty:
    cols = st.columns(3)
    for i, (idx, row) in enumerate(top_3_roles.iterrows()):
        if i < 3:
            cols[i].error(f"**{row['JobRole']}**  \n{row['Attrition Rate (%)']:.1f}% Attrition")

st.divider()

# ==========================================
# 3. IMPACT: COMPENSATION & BURNOUT
# ==========================================
st.header("3. ⚠️ Impact: Compensation & Burnout")
st.markdown("**How pay discrepancies and overtime expectations directly impact our retention.**")

col_e, col_f = st.columns(2)
with col_e:
    sal_bins = [0, 2500, 5000, 7500, 10000, 15000, 25000]
    sal_labels = ["< $2.5k", "$2.5k-$5k", "$5k-$7.5k", "$7.5k-$10k", "$10k-$15k", "> $15k"]
    if not filtered_df.empty:
        filtered_df["SalaryRange"] = pd.cut(filtered_df["MonthlyIncome"], bins=sal_bins, labels=sal_labels)
        sal_attr = filtered_df.groupby("SalaryRange", observed=False)["Attrition"].apply(lambda x: (x == "Yes").mean() * 100).reset_index(name="Attrition Rate (%)")
        fig_sal_range = px.bar(sal_attr, x="SalaryRange", y="Attrition Rate (%)", title="Attrition by Salary Bracket", 
                               color="Attrition Rate (%)", color_continuous_scale="Reds")
        st.plotly_chart(fig_sal_range, use_container_width=True)
        st.caption("📝 **Insight:** Employees earning strictly under $2,500/month are vastly more likely to leave the organization.")

with col_f:
    overtime_attr = filtered_df.groupby(["OverTime", "Attrition"]).size().reset_index(name="Count")
    fig_overtime = px.bar(overtime_attr, x="OverTime", y="Count", color="Attrition",
                          title="Overtime Impact on Attrition", barmode="group",
                          color_discrete_map={"Yes": "#EF553B", "No": "#00CC96"})
    st.plotly_chart(fig_overtime, use_container_width=True)
    st.caption("📝 **Insight:** Employees burdened with mandatory overtime have nearly triple the normal attrition rate.")

st.markdown("<br>", unsafe_allow_html=True)
col_g, col_h = st.columns([0.65, 0.35])
with col_g:
    fig_sal_attr = px.box(filtered_df, x="Attrition", y="MonthlyIncome", color="Attrition",
                          title="Monthly Income Spread by Attrition", 
                          color_discrete_map={"Yes": "#EF553B", "No": "#00CC96"},
                          labels={"MonthlyIncome": "Monthly Income ($)"})
    st.plotly_chart(fig_sal_attr, use_container_width=True)
    st.caption("📝 **Insight:** Those who leave universally earn lower aggregate salaries than peers in the same demographic who stay.")

with col_h:
    st.info("💡 **Unnecessary Visual Removed: Performance Analytics**\n\nWe intentionally removed the Performance Rating chart because 100% of employees heavily cluster at a 3 or 4 rating. This metric acts as statistical noise without contributing towards flight risk analysis and dilutes the core narrative of the dashboard.")

st.divider()

# ==========================================
# 4. RECOMMENDATION: ACTION PLAN
# ==========================================
st.header("4. 🎯 Recommendation: Action Plan")
st.markdown("**What steps should HR take immediately to improve retention and business outcomes?**")
st.success("""
- **📉 Re-evaluate Junior Salary Bands**: Low pay brackets (< $2.5k) have heavily disproportionate turnover. Immediate market adjustment is required.
- **🕒 Cap Overtime Hours**: Employees consistently working overtime leave at triple the standard rate. Enforce strict limits or mandate compensation.
- **👶 Target the < 30 Demographic**: Massive flight risk exists for youth; institute formal career mapping and mentorship networks upon onboarding.
- **💼 Intervene with Sales & Lab Teams**: Sales Representatives and Laboratory Technicians are the highest risk cohorts; conduct stay-interviews immediately.
""")
