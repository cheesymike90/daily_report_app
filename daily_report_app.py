import streamlit as st
import pandas as pd
import io
import os

st.set_page_config(page_title="Freight Report Generator", layout="wide")
st.title("📦 Freight Report Generator")
st.write("Upload a month-to-date CSV report to generate daily pivot summaries and update the master sheet by Ship Date (no duplicates).")

uploaded_file = st.file_uploader("Choose your MTD CSV report", type="csv")

MASTER_PATH = "master_data.csv"

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip().str.replace('\r', '', regex=True)

    # Include all profit values, including negative
    df = df.copy()

    # Calculate Gross Rate splits
    df["30% of Gross Rate"] = df["Gross Rate"] * 0.30
    df["70% of Gross Rate"] = df["Gross Rate"] * 0.70

    # Rename for consistency
    df.rename(columns={
        "Pro #": "PRO#",
        "Customer": "Customer",
        "Ship Date": "Ship Date",
        "Gross Rate": "Gross Rate",
        "Gross Profit": "Gross Profit",
        "Actual Dispatcher": "Actual Dispatch",
        "Salesrep": "Sales Rep",
        "30% Profit": "30% of Profit",
        "70% Profit": "70% of Profit"
    }, inplace=True)

    # Create lane identifier
    df["Lane"] = df["Customer"] + " (" + df["Ship Date"] + ")"

    pivot_df = df[[
        "PRO#", "Customer", "Ship Date", "Gross Rate",
        "30% of Gross Rate", "70% of Gross Rate", "Gross Profit",
        "Actual Dispatch", "Sales Rep", "30% of Profit", "70% of Profit", "Lane"
    ]].copy()

    # Load or create master sheet
    if os.path.exists(MASTER_PATH):
        master_df = pd.read_csv(MASTER_PATH)
    else:
        master_df = pd.DataFrame()

    # Merge without duplicates (based on PRO#)
    combined_df = pd.concat([master_df, pivot_df]).drop_duplicates(subset="PRO#", keep="last")
    combined_df.to_csv(MASTER_PATH, index=False)

    # Convert Ship Date to datetime
    combined_df["Ship Date"] = pd.to_datetime(combined_df["Ship Date"])

    # Sidebar filters
    st.sidebar.header("Filter by Profit")
    include_negatives = st.sidebar.checkbox("Include negative profits", value=True)

    if not include_negatives:
        combined_df = combined_df[combined_df["Gross Profit"] >= 0]
    st.sidebar.header("Filter by Time Period")
    period = st.sidebar.selectbox("Select Period", ["All", "Weekly", "Monthly", "Yearly"])

    st.sidebar.header("Filter by Customer or Rep")
    selected_customer = st.sidebar.selectbox("Customer", ["All"] + sorted(combined_df["Customer"].dropna().unique().tolist()))
    selected_rep = st.sidebar.selectbox("Sales Rep", ["All"] + sorted(combined_df["Sales Rep"].dropna().unique().tolist()))
    selected_dispatcher = st.sidebar.selectbox("Dispatcher", ["All"] + sorted(combined_df["Actual Dispatch"].dropna().unique().tolist()))

    # Apply filters
    filtered_df = combined_df.copy()
    if selected_customer != "All":
        filtered_df = filtered_df[filtered_df["Customer"] == selected_customer]
    if selected_rep != "All":
        filtered_df = filtered_df[filtered_df["Sales Rep"] == selected_rep]
    if selected_dispatcher != "All":
        filtered_df = filtered_df[filtered_df["Actual Dispatch"] == selected_dispatcher]

    if period == "Weekly":
        summary_df = filtered_df.groupby(filtered_df["Ship Date"].dt.to_period("W")).agg({"Gross Profit": "sum"}).reset_index()
    elif period == "Monthly":
        summary_df = filtered_df.groupby(filtered_df["Ship Date"].dt.to_period("M")).agg({"Gross Profit": "sum"}).reset_index()
    elif period == "Yearly":
        summary_df = filtered_df.groupby(filtered_df["Ship Date"].dt.to_period("Y")).agg({"Gross Profit": "sum"}).reset_index()
    else:
        summary_df = filtered_df.copy()

    # Create summaries
    dispatcher_summary = filtered_df.groupby("Actual Dispatch", as_index=False)["30% of Profit"].sum()
    salesrep_summary = filtered_df.groupby("Sales Rep", as_index=False)["70% of Profit"].sum()
    customer_summary = filtered_df.groupby("Customer", as_index=False)["Gross Profit"].sum()
    lane_summary = filtered_df.groupby("Lane", as_index=False).agg({"Gross Profit": "sum", "PRO#": "count"}).rename(columns={"PRO#": "Shipment Count"})

    # Show data
    negative_profits_df = pivot_df[pivot_df["Gross Profit"] < 0]
    st.subheader("🚩 Negative Profit Entries")
    st.dataframe(negative_profits_df)
    st.subheader("Today's Pivot Table by PRO#")
    st.dataframe(pivot_df)

    st.subheader("Updated Dispatcher Profit Summary (30%)")
    st.dataframe(dispatcher_summary)

    st.subheader("Updated Sales Rep Profit Summary (70%)")
    st.dataframe(salesrep_summary)

    st.subheader("Gross Profit by Customer")
    st.dataframe(customer_summary)

    st.subheader("Gross Profit and Shipment Count by Lane")
    st.dataframe(lane_summary)

    st.subheader(f"Gross Profit by {period} Period")
    st.dataframe(summary_df)

    # Excel download
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        # Always write the full pivot_df (including negatives) to Excel
        pivot_df.to_excel(writer, sheet_name="Pivot by PRO#", index=False)
        # Use filtered summaries based on sidebar filters
        dispatcher_summary.to_excel(writer, sheet_name="Profit Summaries", startrow=0, index=False)
        salesrep_summary.to_excel(writer, sheet_name="Profit Summaries", startrow=len(dispatcher_summary) + 2, index=False)
        customer_summary.to_excel(writer, sheet_name="Profit Summaries", startrow=len(dispatcher_summary) + len(salesrep_summary) + 4, index=False)
        lane_summary.to_excel(writer, sheet_name="Profit Summaries", startrow=len(dispatcher_summary) + len(salesrep_summary) + len(customer_summary) + 6, index=False)
        negative_profits_df.to_excel(writer, sheet_name="Negative Profits", index=False)
        if period != "All":
            summary_df.to_excel(writer, sheet_name=f"{period} Summary", index=False)

    st.download_button((
        label="📥 Download Excel Report",
        data=output.getvalue(),
        file_name="freight_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
