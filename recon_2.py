#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Sample data generation for invoices, disputes, etc.
def generate_sample_data():
    np.random.seed(42)
    data = {
        'Carrier Name': [f'Carrier {i}' for i in range(1, 11)],
        'Invoice Amount (USD)': np.random.uniform(1000, 5000, 10).round(2),
        'Disputed Amount (USD)': np.random.uniform(0, 1000, 10).round(2),
        'Reconciliation Status': np.random.choice(['Pending', 'Completed', 'In Progress'], 10),
        'Dispute Type': np.random.choice(['Rate Dispute', 'Volume Dispute'], 10),
        'Settlement Status': np.random.choice(['Settled', 'Unsettled'], 10),
        'Invoice Month': pd.date_range(start="2024-01-01", periods=10, freq='M').strftime('%Y-%m')
    }
    return pd.DataFrame(data)

df = generate_sample_data()

# Set page layout to wide
st.set_page_config(layout="wide")

# Dashboard title
st.title("Telecom Billing Reconciliation Dashboard")

# Tabs for the dashboard
tab1, tab2, tab3, tab4 = st.tabs(["Invoice Recon", "Reconciliation Summary", "Dispute Summary", "Settlement Summary"])

# Tab 1: Invoice Recon
with tab1:
    st.subheader("Invoice Reconciliation")
    
    # Invoice Upload (example with CSV)
    uploaded_file = st.file_uploader("Upload Invoice File", type=["csv", "xlsx"])
    if uploaded_file is not None:
        df_uploaded = pd.read_csv(uploaded_file)
        st.write("Invoice Data", df_uploaded)
    
    # Example billing metrics (using generated data)
    total_bills_per_carrier = df.groupby('Carrier Name')['Invoice Amount (USD)'].sum().reset_index()
    st.write("Total Bills per Carrier", total_bills_per_carrier)
    
    # Processed vs Disputed Chart
    processed_vs_disputed = px.bar(df, x='Carrier Name', y=['Invoice Amount (USD)', 'Disputed Amount (USD)'], 
                                    title="Processed vs Disputed Amounts by Carrier", barmode="group")
    st.plotly_chart(processed_vs_disputed)

# Tab 2: Reconciliation Summary
with tab2:
    st.subheader("Reconciliation Summary")
    reconciliation_status = df['Reconciliation Status'].value_counts().reset_index()
    reconciliation_status.columns = ['Status', 'Count']
    
    # Pie chart for reconciliation status
    reconciliation_pie = px.pie(reconciliation_status, names='Status', values='Count', title="Reconciliation Status Distribution")
    st.plotly_chart(reconciliation_pie)
    
    # Reconciliation trend over time (e.g., monthly)
    reconciliation_trend = df.groupby(['Invoice Month', 'Reconciliation Status']).size().reset_index(name='Count')
    trend_fig = px.line(reconciliation_trend, x='Invoice Month', y='Count', color='Reconciliation Status', title="Reconciliation Trend Over Time")
    st.plotly_chart(trend_fig)

# Tab 3: Dispute Summary
with tab3:
    st.subheader("Dispute Summary")
    
    # Dispute overview (type distribution)
    dispute_type = df['Dispute Type'].value_counts().reset_index()
    dispute_type.columns = ['Dispute Type', 'Count']
    dispute_pie = px.pie(dispute_type, names='Dispute Type', values='Count', title="Dispute Type Distribution")
    st.plotly_chart(dispute_pie)
    
    # Disputed amounts by carrier
    dispute_by_carrier = df.groupby('Carrier Name')['Disputed Amount (USD)'].sum().reset_index()
    st.write("Disputed Amounts by Carrier", dispute_by_carrier)
    
    # Dispute analysis
    dispute_analysis_fig = px.bar(df, x='Carrier Name', y='Disputed Amount (USD)', color='Dispute Type', title="Disputed Amount by Carrier")
    st.plotly_chart(dispute_analysis_fig)

# Tab 4: Settlement Summary
with tab4:
    st.subheader("Settlement Summary")
    
    # Settlement status distribution
    settlement_status = df['Settlement Status'].value_counts().reset_index()
    settlement_status.columns = ['Settlement Status', 'Count']
    settlement_pie = px.pie(settlement_status, names='Settlement Status', values='Count', title="Settlement Status Distribution")
    st.plotly_chart(settlement_pie)
    
    # Outstanding settlements by carrier
    outstanding_settlements = df[df['Settlement Status'] == 'Unsettled']
    st.write("Outstanding Settlements", outstanding_settlements)


