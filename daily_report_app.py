import pandas as pd
import streamlit as st

def generate_daily_report(file):
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip().str.replace('\r', '')

    df['30% of Gross Rate'] = df['Gross Rate'] * 0.30
    df['70% of Gross Rate'] = df['Gross Rate'] * 0.70
    df['30% of Profit'] = df['Gross Profit'] * 0.30
    df['70% of Profit'] = df['Gross Profit'] * 0.70

    df = df.rename(columns={'Actual Dispatcher': 'Actual Dispatch'})
    return df

def pivot_by_dispatch(df):
    return df.groupby('Actual Dispatch')[[
        '30% of Gross Rate', '30% of Profit'
    ]].sum().reset_index()

def pivot_by_salesrep(df):
    return df.groupby('Salesrep')[[
        '70% of Gross Rate', '70% of Profit'
    ]].sum().reset_index()

# Streamlit Interface
st.set_page_config(page_title="Daily Report Generator", layout="centered")
st.title("📦 Daily Profitability Report")
st.write("Upload your daily shipment CSV file by dragging and dropping it below:")

uploaded_file = st.file_uploader("Drop CSV here or click to browse", type=["csv"], label_visibility="collapsed")

if uploaded_file is not None:
    st.success("✅ File uploaded successfully.")
    df = generate_daily_report(uploaded_file)

    st.subheader("📋 Pivot Table by Actual Dispatch (30% Split)")
    dispatch_pivot = pivot_by_dispatch(df)
    st.dataframe(dispatch_pivot, use_container_width=True)

    st.subheader("📋 Pivot Table by Salesrep (70% Split)")
    salesrep_pivot = pivot_by_salesrep(df)
    st.dataframe(salesrep_pivot, use_container_width=True)

    # Excel export
    with pd.ExcelWriter("pivot_report.xlsx", engine="xlsxwriter") as writer:
        dispatch_pivot.to_excel(writer, sheet_name="By Dispatcher", index=False)
        salesrep_pivot.to_excel(writer, sheet_name="By Salesrep", index=False)
        writer.save()
        with open("pivot_report.xlsx", "rb") as f:
            st.download_button(
                label="⬇️ Download Excel Report",
                data=f,
                file_name="daily_pivot_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
else:
    st.info("Awaiting CSV file upload...")

