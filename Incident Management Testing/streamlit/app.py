import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Function to convert SLA to timedelta
def convert_sla_to_timedelta(sla):
    parts = sla.split(':')
    days = int(parts[0])
    hours = int(parts[1])  
    minutes = int(parts[2])  
    seconds = int(parts[3])  
    return pd.Timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)

# Streamlit App
st.title('Incident Management Dashboard')

# Sidebar for file upload
st.sidebar.title('File Upload')
IM_file = st.sidebar.file_uploader('Upload IM Data Excel File', type='xlsx')
sla_file = st.sidebar.file_uploader('Upload SLA Data Excel File', type='xlsx')

if IM_file is not None and sla_file is not None:
    # Load data
    im_df = pd.read_excel(IM_file)
    sla_df = pd.read_excel(sla_file)
    
    im_df = pd.merge(im_df, sla_df, on='Priority', how="left")
    im_df['Time taken for resolution (days)'] = (im_df['Resolution Date'] - im_df['Creation Date']).dt.days
    im_df['SLA'] = im_df['SLA'].apply(convert_sla_to_timedelta)
    im_df['SLA Breached By (days)'] = im_df['Time taken for resolution (days)'] - im_df['SLA'].dt.days
    im_df['Creation Month'] = im_df['Creation Date'].dt.to_period('M')
    im_df['Resolution Month'] = im_df['Resolution Date'].dt.to_period('M')
    im_df['SLA Breached(T/F)'] = im_df['SLA Breached By (days)'].apply(lambda x: True if x >= 1 else False)

    # Number of Incidents Created Each Month
    st.header('Number of Incidents Created Each Month')
    creation_monthly_counts = im_df['Creation Month'].value_counts().sort_index()

    plt.figure(figsize=(10, 6))
    plt.plot(creation_monthly_counts.index.astype(str), creation_monthly_counts.values, marker='o', linestyle='-', color="green")
    for i, count in enumerate(creation_monthly_counts.values):
        plt.text(i, count, str(count), ha='center', va='bottom', fontsize=10)
    plt.title('Number of Incidents Created Each Month')
    plt.xlabel('Month')
    plt.ylabel('Number of Incidents')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    st.pyplot(plt)
    plt.clf()  # Clear the current figure

    # Number of Incidents Resolved Each Month
    st.header('Number of Incidents Resolved Each Month')
    resolution_monthly_counts = im_df['Resolution Month'].value_counts().sort_index()

    plt.figure(figsize=(10, 6))
    plt.plot(resolution_monthly_counts.index.astype(str), resolution_monthly_counts.values, marker='.', linestyle='-', color="green")
    for i, count in enumerate(resolution_monthly_counts.values):
        plt.text(i, count, str(count), ha='center', va='top', fontsize=10)
    plt.title('Number of Incidents Resolved Each Month')
    plt.xlabel('Month')
    plt.ylabel('Number of Incidents')
    plt.xticks(rotation=45)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    st.pyplot(plt)
    plt.clf()  # Clear the current figure

    # Distribution of Incidents by Application
    st.header('Distribution of Incidents by Application')
    application_counts = im_df['Application'].value_counts()

    plt.figure(figsize=(16, 8))
    bars = plt.bar(application_counts.index, application_counts.values, color='lightgreen', width=0.9, edgecolor='black')
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval + 0.2, round(yval, 1), ha='center', va='bottom')
    plt.title('Distribution of Incidents by Application')
    plt.xlabel('Application')
    plt.ylabel('Number of Incidents')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(plt)
    plt.clf()  # Clear the current figure

    # Distribution of Priorities
    st.header('Distribution of Priorities')
    custom_order = ['Critical', 'High', 'Medium', 'Low']
    priority_counts = im_df['Priority'].value_counts().reindex(custom_order, fill_value=0)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    ax1.pie(priority_counts, labels=priority_counts.index, autopct='%1.1f%%', startangle=60)
    ax1.set_title('Distribution of Priorities')
    ax1.axis('equal')

    bars = ax2.bar(priority_counts.index, priority_counts.values, color='lightgreen', width=0.5, edgecolor='black')
    ax2.set_title('Histogram of Priorities')
    ax2.set_xlabel('Priority')
    ax2.set_ylabel('Frequency')
    for bar in bars:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2, yval + 0.1, int(yval), ha='center', va='bottom', fontsize=12)
    plt.tight_layout()
    st.pyplot(fig)
    plt.clf()  # Clear the current figure

    # SLA Breached (T/F)
    st.header('SLA Breached (T/F)')
    sla_breached_counts = im_df['SLA Breached(T/F)'].value_counts()
    colors = ['gray', 'green']

    plt.figure(figsize=(4, 3))
    plt.pie(sla_breached_counts, labels=sla_breached_counts.index, colors=colors, autopct='%1.1f%%', startangle=0)
    plt.title('SLA Breached (T/F)')
    plt.axis('equal')
    st.pyplot(plt)
    plt.clf()  # Clear the current figure

    # Count of SLA Breaches by Priority
    st.header('Count of SLA Breaches by Priority')
    sla_breaches = im_df[im_df['SLA Breached(T/F)'] == True]
    sla_breaches_count = sla_breaches.groupby('Priority').size().reindex(custom_order, fill_value=0)

    plt.figure(figsize=(12, 5))
    bars = plt.bar(sla_breaches_count.index, sla_breaches_count.values, color='lightgreen', width=0.5, edgecolor='black')
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval + 0.1, int(yval), ha='center', va='bottom', fontsize=12)
    plt.title('Count of SLA Breaches by Priority')
    plt.xlabel('Priority')
    plt.ylabel('Count')
    plt.xticks(rotation=0)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    st.pyplot(plt)
    plt.clf()  # Clear the current figure

    # Percentage of SLA Breaches by Priority
    st.header('Percentage of SLA Breaches by Priority')
    sla_breached_percentage = im_df.groupby('Priority').agg(
        total_incidents=('Incident ID', 'count'),
        breached_incidents=('SLA Breached(T/F)', 'sum')
    ).reset_index()
    sla_breached_percentage['breached_percentage'] = (
        sla_breached_percentage['breached_incidents'] / sla_breached_percentage['total_incidents'] * 100
    )
    sla_breached_percentage = sla_breached_percentage.set_index('Priority').reindex(custom_order).reset_index()

    plt.figure(figsize=(12, 5))
    bars = plt.bar(sla_breached_percentage['Priority'], sla_breached_percentage['breached_percentage'], color='lightgreen', width=0.5, edgecolor='black')
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval + 0.1, f'{yval:.2f}%', ha='center', va='bottom', fontsize=12)
    plt.title('Percentage of SLA Breaches by Priority')
    plt.xlabel('Priority')
    plt.ylabel('Percentage of SLA Breaches')
    plt.xticks(rotation=0)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.ylim(0, 100)
    st.pyplot(plt)
    plt.clf()  # Clear the current figure

    # Save final DataFrame with SLA Breaches to Excel
    final_df = im_df[im_df['SLA Breached(T/F)'] == True]
    excel_file = "SLA_Breached_Final_Output.xlsx"
    final_df.to_excel(excel_file, index=False)
    st.success(f"DataFrame with SLA Breached(T/F) = True has been written to {excel_file}")

else:
    st.warning("Please upload both the IM Data and SLA Data Excel files to proceed.")
