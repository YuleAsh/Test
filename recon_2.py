
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Sample data generation (50 records) with both disputed and undisputed data
def generate_sample_data():
    np.random.seed(42)
    months = pd.date_range(start="2024-01-01", periods=12, freq='M').strftime('%Y-%m').tolist()
    carriers = [f'Carrier {i}' for i in range(1, 11)]  # 10 unique carriers
    data = []

    for month in months:
        for carrier in carriers:
            invoice_amount = np.random.uniform(1000, 5000)
            is_disputed = np.random.rand() < 0.2
            disputed_amount = np.random.uniform(0, invoice_amount * 0.3) if is_disputed else 0
            billing_cycle = f'{2024}-{int(month[-2:]):02d}-{np.random.choice([1, 2])}'  # Format: Year-Month-Fortnight

            data.append({
                'Carrier Name': carrier,
                'Invoice Amount (USD)': invoice_amount,
                'Disputed Amount (USD)': disputed_amount,
                'Reconciliation Status': np.random.choice(['Pending', 'Completed', 'In Progress']),
                'Dispute Type': np.random.choice(['Rate Dispute', 'Volume Dispute']) if is_disputed else None,
                'Settlement Status': np.random.choice(['Settled', 'Unsettled']) if is_disputed else 'Settled',
                'Invoice Month': month,
                'Billing Cycle': billing_cycle,
                'Usage (Mins)': np.random.uniform(100, 500)  # Ensure 'Usage (Mins)' is included
            })

    return pd.DataFrame(data)

df = generate_sample_data()

# Set page layout to wide
st.set_page_config(layout="wide")

# Dashboard title
st.title("Telecom Billing Reconciliation Dashboard")

# Filters
carrier_filter = st.selectbox("Select Carrier (Optional)", options=["All"] + list(df['Carrier Name'].unique()))
month_filter = st.selectbox("Select Month (Optional)", options=["All"] + list(df['Invoice Month'].unique()))

# Applying filters (if selected) to data
filtered_df = df.copy()
if carrier_filter != "All":
    filtered_df = filtered_df[filtered_df['Carrier Name'] == carrier_filter]
if month_filter != "All":
    filtered_df = filtered_df[filtered_df['Invoice Month'] == month_filter]

# Function to create summary tables with specific fields and alignment
def create_summary_table(data, columns):
    table = data[columns].copy()
    # Format only the numeric fields to 2 decimal places
    for col in ['Invoice Amount (USD)', 'Disputed Amount (USD)', 'Usage (Mins)']:
        if col in table.columns:
            table[col] = table[col].round(2)
    return table.style.set_properties(**{'text-align': 'center'})

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Invoice Recon", "Reconciliation Summary", "Dispute Summary", "Settlement Summary"])

# Tab 1: Invoice Recon
with tab1:
    st.subheader("Invoice Reconciliation Overview")
    st.write("### Summary Table")
    table1_data = create_summary_table(filtered_df, [
        'Carrier Name', 'Reconciliation Status', 'Invoice Amount (USD)', 
        'Disputed Amount (USD)', 'Dispute Type', 'Settlement Status'
    ])
    st.dataframe(table1_data, use_container_width=True, height=250)

    # Chart: Disputed vs Processed Amounts by Carrier
    st.write("### Disputed vs Processed Amounts by Carrier")
    if not filtered_df.empty:
        processed_vs_disputed = px.bar(filtered_df, x='Carrier Name', y=['Invoice Amount (USD)', 'Disputed Amount (USD)'],
                                       title="Disputed vs Processed Amounts by Carrier", barmode="group")
        st.plotly_chart(processed_vs_disputed)

    # Chart: Invoice Disputes by Month
    st.write("### Invoice Disputes by Month")
    monthly_disputes = filtered_df.groupby('Invoice Month').agg({
        'Invoice Amount (USD)': 'sum', 'Disputed Amount (USD)': 'sum'}).reset_index()
    monthly_disputes_fig = px.line(monthly_disputes, x='Invoice Month', y=['Invoice Amount (USD)', 'Disputed Amount (USD)'],
                                   title="Invoice Disputes by Month")
    st.plotly_chart(monthly_disputes_fig)

# Tab 2: Reconciliation Summary
with tab2:
    st.subheader("Reconciliation Summary")
    st.write("### Summary Table")

    filtered_df['Receivables'] = filtered_df['Invoice Amount (USD)'] - filtered_df['Disputed Amount (USD)']
    filtered_df['Payables'] = filtered_df['Disputed Amount (USD)']  

    # Group by 'Carrier Name' and 'Billing Cycle'
    summary_table2 = filtered_df.groupby(['Carrier Name', 'Billing Cycle']).agg({
        'Invoice Amount (USD)': 'sum',
        'Disputed Amount (USD)': 'sum',
        }).reset_index()

    # Add some additional columns like Receivables, Payables, Netted Amount, and Settlement Status
    summary_table2['Receivables'] = np.random.uniform(1000, 3000, len(summary_table2))
    summary_table2['Payables'] = np.random.uniform(500, 2500, len(summary_table2))
    summary_table2['Netted Amount'] = summary_table2['Receivables'] - summary_table2['Payables']
    summary_table2['Settlement Status'] = np.random.choice(['Settled', 'Pending'], len(summary_table2))

    st.dataframe(summary_table2, use_container_width=True)

    # Chart: Pending Reconciliation by Carrier
    st.write("### Carriers with Pending Reconciliation")
    pending_reconciliation = filtered_df[filtered_df['Reconciliation Status'] == 'Pending']
    pending_summary = pending_reconciliation.groupby('Carrier Name')['Invoice Amount (USD)'].sum().reset_index()
    pending_reconciliation_fig = px.bar(pending_summary, x='Carrier Name', y='Invoice Amount (USD)',
                                        title="Invoices with Pending Reconciliation by Carrier")
    st.plotly_chart(pending_reconciliation_fig)



# Tab 3: Dispute Summary
with tab3:
    st.subheader("Dispute Summary")
    st.write("### Summary Table")
    
    # Generate disputed usage mins with random values between 0 and 5000
    filtered_df['Disputed Usage (Mins)'] = np.random.uniform(0, 500, size=len(filtered_df))

    # Set 'Disputed Usage (Mins)' to 0 if Dispute Type is 'Rate Dispute'
    filtered_df.loc[filtered_df['Dispute Type'] == 'Rate Dispute', 'Disputed Usage (Mins)'] = 0
    
    # Group by 'Carrier Name' and aggregate the required fields
    summary_table3 = filtered_df.groupby('Carrier Name').agg({
        'Invoice Amount (USD)': 'sum',
        'Dispute Type': 'first',  # Assuming Dispute Type is the same for each carrier
        'Disputed Amount (USD)': 'sum',
        'Disputed Usage (Mins)': 'sum',
        'Settlement Status': 'first'  # Assuming Settlement Status is the same for each carrier
    }).reset_index()

    # Ensure the 'Disputed Usage (Mins)' is still within the range 0-5000
    summary_table3['Disputed Usage (Mins)'] = summary_table3['Disputed Usage (Mins)'].clip(0, 5000)

    # Rename columns for clarity
    summary_table3.rename(columns={
        'Invoice Amount (USD)': 'Total Invoice Amount (USD)',
        'Disputed Amount (USD)': 'Total Disputed Amount (USD)',
        'Disputed Usage (Mins)': 'Total Disputed Usage (Mins)',
        'Dispute Type': 'Dispute Type',
        'Settlement Status': 'Settlement Status'
    }, inplace=True)

    # Display the summary table with the specified fields
    st.dataframe(summary_table3.style.set_properties(**{'text-align': 'center'}), use_container_width=True, height=250)

    # Create two columns for side-by-side charts
    col1, col2 = st.columns(2)

    # Chart 1: Total Disputed Amounts by Carrier
    with col1:
        st.write("### Disputed Amounts by Carrier")
        disputed_amounts = filtered_df.groupby('Carrier Name')['Disputed Amount (USD)'].sum().reset_index()
        disputed_amounts_fig = px.bar(disputed_amounts, x='Carrier Name', y='Disputed Amount (USD)', title="Disputed Amounts by Carrier")
        st.plotly_chart(disputed_amounts_fig, use_container_width=True)

    # Chart 2: Total Disputed Usage by Carrier
    with col2:
        st.write("### Disputed Usage (Mins) by Carrier")
        disputed_usage = filtered_df.groupby('Carrier Name')['Disputed Usage (Mins)'].sum().reset_index()
        disputed_usage_fig = px.bar(disputed_usage, x='Carrier Name', y='Disputed Usage (Mins)', title="Disputed Usage (Mins) by Carrier")
        st.plotly_chart(disputed_usage_fig, use_container_width=True)

# Tab 4: Settlement Summary
with tab4:
    st.subheader("Settlement Summary")
    st.write("### Summary Table")
    summary_table4 = filtered_df.groupby('Carrier Name').agg({
        'Invoice Amount (USD)': 'size',
        'Disputed Amount (USD)': 'sum'
    }).rename(columns={'Invoice Amount (USD)': 'Total Invoices'}).reset_index()
    summary_table4['Settled Invoices'] = np.random.randint(1, 5, size=len(summary_table4))
    summary_table4['Outstanding Amount'] = summary_table4['Disputed Amount (USD)'] * 0.8
    summary_table4['Settled Amount'] = summary_table4['Disputed Amount (USD)'] - summary_table4['Outstanding Amount']
    st.dataframe(summary_table4.style.set_properties(**{'text-align': 'center'}), use_container_width=True, height=250)

    # Chart: Settlement Status by Carrier
    st.write("### Settlement Status by Carrier")
    settlement_status = filtered_df.groupby(['Carrier Name', 'Settlement Status']).size().reset_index(name='Count')
    settlement_pie = px.pie(settlement_status, names='Settlement Status', values='Count', title="Settlement Status by Carrier")
    st.plotly_chart(settlement_pie)


