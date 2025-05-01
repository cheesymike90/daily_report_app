import pandas as pd
import streamlit as st
import io

def generate_daily_report(file):
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip().str.replace('\r', '')

    df['30% of Gross Rate'] = df['Gross Rate'] * 0.30
    df['70% of Gross Rate'] = df['Gross Rate'] * 0.70
    df['30% of Profit'] = df['Gross Profit'] * 0.30
    df['70% of Profit'] = df['Gross Profit'] * 0.70

    report_df = df[[
        'Pro #', 'Customer', 'Ship Date', 'Gross Rate',
        '30% of Gross Rate', '70% of Gross Rate', 'Gross Profit',
        'Actual Dispatcher', 'Salesrep', '30% of Profit', '70% of Profit'
    ]].rename(columns={'Actual Dispatcher': 'Actual Dispatch'})

    return report_df

# Streamlit Interface
st.set_page_config(page_title="Daily Report Generator", layout="centered")

st.title("📦 Daily Profitability Report")
st.write("Upload your daily shipment CSV file by dragging and dropping it below:")

uploaded_file = st.file_uploader("Drop CSV here or click to browse", type=["csv"], label_visibility="collapsed")

if uploaded_file is not None:
    st.success("✅ File uploaded successfully.")
    report = generate_daily_report(uploaded_file)
    
    st.subheader("📊 Generated Report")
    st.dataframe(report, use_container_width=True)

    csv = report.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Download CSV Report",
        data=csv,
        file_name='daily_report_output.csv',
        mime='text/csv'
    )
else:
    st.info("Awaiting CSV file upload...")

