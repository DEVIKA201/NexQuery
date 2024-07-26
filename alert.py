import pandas as pd
from datetime import datetime, timedelta
from threading import Timer
import time
from weight_assign import df

def check_new_leads(df):
    today = datetime.now().date()
    new_leads = df[(df['transaction_status'].str.lower() == 'new lead') & 
                   (pd.to_datetime(df['created_date']).dt.date == today)]
    return new_leads[['enquiry_id', 'source', 'priority']]

def check_old_new_leads(df, days_threshold=7):
    now = datetime.now()
    old_leads = df[(df['transaction_status'].str.lower() == 'new lead') & 
                   (pd.to_datetime(df['created_date']) < now - timedelta(days=days_threshold))]
    return old_leads[['enquiry_id', 'source', 'priority']]

# Function to poll for new leads continuously
def poll_for_new_leads():
    while True:
        try:
            from weight_assign import df  # Re-import `df` to ensure it retains the latest state
        except ImportError:
            break

        if df['priority'].isnull().any():
            break

        check_new_leads(df)
        time.sleep(10)  # Poll every 10 seconds

# Function to run the old leads check every 2 minutes
def schedule_old_leads_check():
    try:
        from weight_assign import df  # Re-import `df` to ensure it retains the latest state
    except ImportError:
        return

    if df['priority'].isnull().any():
        return

    check_old_new_leads(df)
    Timer(120, schedule_old_leads_check).start()
