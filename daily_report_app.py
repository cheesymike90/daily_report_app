{\rtf1\ansi\ansicpg1252\cocoartf2820
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import pandas as pd\
import streamlit as st\
import io\
\
def generate_daily_report(file):\
    df = pd.read_csv(file)\
    df.columns = df.columns.str.strip().str.replace('\\r', '')\
\
    df['30% of Gross Rate'] = df['Gross Rate'] * 0.30\
    df['70% of Gross Rate'] = df['Gross Rate'] * 0.70\
    df['30% of Profit'] = df['Gross Profit'] * 0.30\
    df['70% of Profit'] = df['Gross Profit'] * 0.70\
\
    report_df = df[[\
        'Pro #', 'Customer', 'Ship Date', 'Gross Rate',\
        '30% of Gross Rate', '70% of Gross Rate', 'Gross Profit',\
        'Actual Dispatcher', 'Salesrep', '30% of Profit', '70% of Profit'\
    ]].rename(columns=\{'Actual Dispatcher': 'Actual Dispatch'\})\
\
    return report_df\
\
# Streamlit Interface\
st.title("Daily Profitability Report Generator")\
\
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])\
\
if uploaded_file is not None:\
    report = generate_daily_report(uploaded_file)\
    st.dataframe(report)\
\
    csv = report.to_csv(index=False).encode('utf-8')\
    st.download_button(\
        label="Download Report as CSV",\
        data=csv,\
        file_name='daily_report_output.csv',\
        mime='text/csv'\
    )\
}