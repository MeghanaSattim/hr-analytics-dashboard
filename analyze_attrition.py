import pandas as pd
import warnings
warnings.filterwarnings('ignore')

df = pd.read_csv('WA_Fn-UseC_-HR-Employee-Attrition.csv')

print("=== 1. Why employees are leaving (Attrition) ===")
num_cols = ['MonthlyIncome', 'Age', 'DistanceFromHome', 'TotalWorkingYears', 'JobSatisfaction', 'EnvironmentSatisfaction']
print("Mean values for numerical factors:")
print(df.groupby('Attrition')[num_cols].mean().round(2))

print("\nAttrition % by OverTime:")
print((pd.crosstab(df['OverTime'], df['Attrition'], normalize='index') * 100).round(2))

print("\nAttrition % by BusinessTravel:")
print((pd.crosstab(df['BusinessTravel'], df['Attrition'], normalize='index') * 100).round(2))

print("\n=== 2. Which employees perform better ===")
print("Distribution of PerformanceRating:")
print(df['PerformanceRating'].value_counts())

perf_cols = ['PercentSalaryHike', 'YearsAtCompany', 'MonthlyIncome', 'Age']
print("\nMean values by PerformanceRating:")
print(df.groupby('PerformanceRating')[perf_cols].mean().round(2))

print("\nPerformance Ratings by JobRole (Percentage of Rating 4):")
perf_role = pd.crosstab(df['JobRole'], df['PerformanceRating'], normalize='index') * 100
print(perf_role.round(2))

print("\n=== 3. Relationship between Salary, Age, Job Role, and Attrition ===")
print("Attrition % by Job Role:")
role_attr = pd.crosstab(df['JobRole'], df['Attrition'], normalize='index') * 100
print(role_attr.sort_values(by='Yes', ascending=False).round(2))

print("\nAverage Salary (MonthlyIncome) by Attrition & Job Role:")
print(df.groupby(['JobRole', 'Attrition'])['MonthlyIncome'].mean().unstack().round(2))

print("\nAttrition % by Age Groups:")
df['AgeGroup'] = pd.cut(df['Age'], bins=[17, 25, 35, 45, 55, 65])
age_attr = pd.crosstab(df['AgeGroup'], df['Attrition'], normalize='index') * 100
print(age_attr.round(2))
