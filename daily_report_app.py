import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Freight Report Generator", layout="wide")
st.title("📦 Freight Report Generator")
st.write("Upload a CSV file to generate a pivot report and profit summaries for dispatchers and sales reps.")

uploaded_file = st.file_uploader("Choose your CSV file", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip().str.replace('\r', '', regex=True)

    # Filter positive gross profit only
    df = df[df["Gross Profit"] >= 0].copy()

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

    pivot_df = df[[
        "PRO#", "Customer", "Ship Date", "Gross Rate",
        "30% of Gross Rate", "70% of Gross Rate", "Gross Profit",
        "Actual Dispatch", "Sales Rep", "30% of Profit", "70% of Profit"
    ]]

    dispatcher_summary = pivot_df.groupby("Actual Dispatch", as_index=False)["30% of Profit"].sum()
    salesrep_summary = pivot_df.groupby("Sales Rep", as_index=False)["70% of Profit"].sum()

    # Show data previews
    st.subheader("Pivot Table by PRO#")
    st.dataframe(pivot_df)

    st.subheader("Dispatcher Profit Summary (30%)")
    st.dataframe(dispatcher_summary)

    st.subheader("Sales Rep Profit Summary (70%)")
    st.dataframe(salesrep_summary)

    # Excel download
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        pivot_df.to_excel(writer, sheet_name="Pivot by PRO#", index=False)
        dispatcher_summary.to_excel(writer, sheet_name="Profit Summaries", startrow=0, index=False)
        salesrep_summary.to_excel(writer, sheet_name="Profit Summaries", startrow=len(dispatcher_summary) + 2, index=False)
    
    st.download_button(
        label="📥 Download Excel Report",
        data=output.getvalue(),
        file_name="freight_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
