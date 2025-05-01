import streamlit as st
import pandas as pd
import os
from datetime import datetime

# File path for data storage
CSV_FILE = "daily_reports.csv"

# Load existing data or create empty DataFrame
def load_data():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE, parse_dates=['Ship Date'])
    else:
        return pd.DataFrame(columns=[
            "Date", "PRO#", "Customer", "Ship Date", "Gross Rate",
            "30% of Gross", "70% of Gross", "Gross Profit", "Actual Dispatch",
            "Sales Rep", "30% of Profit", "70% of Profit"
        ])

# Save a new report row
def save_report(data):
    df = load_data()
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

# App UI
st.title("📦 Daily Freight Report")
st.subheader("Enter Daily Report")

with st.form("report_form"):
    pro = st.text_input("PRO#")
    customer = st.text_input("Customer")
    ship_date = st.date_input("Ship Date")
    gross_rate = st.number_input("Gross Rate", min_value=0.0)
    gross_profit = st.number_input("Gross Profit", min_value=0.0)
    actual_dispatch = st.text_input("Actual Dispatch")
    sales_rep = st.text_input("Sales Rep")

    submitted = st.form_submit_button("Save Report")
    if submitted:
        report = {
            "Date": datetime.now().date(),
            "PRO#": pro,
            "Customer": customer,
            "Ship Date": pd.to_datetime(ship_date),
            "Gross Rate": gross_rate,
            "30% of Gross": 0.3 * gross_rate,
            "70% of Gross": 0.7 * gross_rate,
            "Gross Profit": gross_profit,
            "Actual Dispatch": actual_dispatch,
            "Sales Rep": sales_rep,
            "30% of Profit": 0.3 * gross_profit,
            "70% of Profit": 0.7 * gross_profit
        }
        save_report(report)
        st.success("Report saved successfully.")

# Load and display data
data = load_data()
st.subheader("📊 All Daily Reports")
st.dataframe(data)

# Summary filters
st.sidebar.header("Summary Filters")
summary_type = st.sidebar.selectbox("View Summary By", ["Week", "Month", "Year"])

if not data.empty:
    data["Ship Date"] = pd.to_datetime(data["Ship Date"])
    data["Week"] = data["Ship Date"].dt.strftime('%Y-W%U')
    data["Month"] = data["Ship Date"].dt.strftime('%Y-%m')
    data["Year"] = data["Ship Date"].dt.year

    group_field = summary_type
    summary = data.groupby(group_field)[["Gross Rate", "Gross Profit"]].sum().reset_index()
    st.subheader(f"📅 {summary_type}ly Summary")
    st.dataframe(summary)
else:
    st.warning("No data available to summarize.")
