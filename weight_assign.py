import mysql.connector
import pandas as pd

def fetch_data(config, query, retries=3, dealy=5):
    attempt = 0
    while attempt<retries:
        try:
            link = mysql.connector.connect(**config)
            cursor = link.cursor(dictionary=True)
            cursor.execute(query)
            data = cursor.fetchall()
            cursor.close()
            link.close()
            return data
        except mysql.connector.Error:
            attempt+=1
            if attempt>=retries:
                return []

def assign_weights_from_table(config, table_name):
    data = fetch_data(config, f"SELECT id, conv_rate FROM {table_name}")
    if not data:
        return{}
    total_weight = sum(float(row['conv_rate']) for row in data)
    if total_weight ==0:
        return {row['id']:0 for row in data}
    weights = {row['id']: float(row['conv_rate']) / total_weight for row in data}
    return weights

def assign_weights_from_database(config):
    weights = {}
    tables = ['conversion_rate_location', 'conversion_rate_treatment', 'conversion_rate_source']
    for table in tables:
        weights[table] = assign_weights_from_table(config, table)
    return weights

def get_lead_data(config):
    query = """
        SELECT ut.id as enquiry_id, u.patient_name, s.id as source_id, s.name as source, t.id as treatment_id, t.treatment_name as treatment, 
        l.id as location_id, l.name as location,ut.user_trxn_status_id, tm.name as bd,ut.created_date
        FROM user_transaction ut
        LEFT JOIN users u ON ut.user_id = u.id
        LEFT JOIN source s ON s.id = ut.source_id
        LEFT JOIN treatment t ON t.id = u.treatment_id
        LEFT JOIN location l ON l.id = u.location_id
        LEFT JOIN team_mapppings tm ON tm.code = ut.leads_assign_to
    """
    return fetch_data(config, query)

def preprocess_data(leads, weights):
    for lead in leads:
        lead['source_weight'] = weights['conversion_rate_source'].get(lead['source_id'], 0)
        lead['treatment_weight'] = weights['conversion_rate_treatment'].get(lead['treatment_id'], 0)
        lead['location_weight'] = weights['conversion_rate_location'].get(lead['location_id'], 0)
        lead['total_importance'] = (lead['source_weight'] + 
                                    lead['treatment_weight'] + 
                                    lead['location_weight'])
    return leads

def update_user_txn_status(leads, config):
    user_txn_status_map = fetch_data(config, "SELECT id, name FROM user_trxn_status")
    if user_txn_status_map:
        status_map = {status['id']:status['name'] for status in user_txn_status_map}
        for lead in leads:
            lead['transaction_status'] = status_map.get(lead['user_trxn_status_id'],'Unknown')
        return leads
    
config = {
    'user': 'username',
    'password': 'password',
    'host': 'hostname',
    'port': portnumber,
    'database': 'dbname',
}

weights = assign_weights_from_database(config)
leads = get_lead_data(config)

if leads:
    leads = preprocess_data(leads,weights)
    leads = update_user_txn_status(leads,config)
    
    df = pd.DataFrame(leads)
    pd.options.display.float_format = '{:.4f}'.format

    if 'total_importance' in df.columns:
        # define thresholds
        high_threshold = 0.25
        low_threshold = 0.095
        
        def categorize_importance(importance):
            if importance >= high_threshold:
                return 'Critical'
            elif low_threshold < importance < high_threshold:
                return 'Essential'
            else:
                return 'Routine'

        df['priority'] = df['total_importance'].apply(categorize_importance)
# Ordinal encoding in increasing order of Routine, Essential, Critical
        priority_mapping = {'Routine': 0, 'Essential': 1, 'Critical': 2}
        df['priority_encoded'] = df['priority'].map(priority_mapping)

        df = df[['enquiry_id', 'created_date', 'patient_name', 'transaction_status', 'bd', 'source', 'treatment', 'location', 'priority']]
else:
    pass

