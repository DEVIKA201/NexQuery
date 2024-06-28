import mysql.connector
import pandas as pd

def fetch_data(config, query):
    try:
        link = mysql.connector.connect(**config)
        cursor = link.cursor(dictionary=True)
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        link.close()
        return data
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []

def assign_weights_from_table(config, table_name):
    data = fetch_data(config, f"SELECT id, conv_rate FROM {table_name}")
    total_weight = sum(float(row['conv_rate']) for row in data)
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
        l.id as location_id, l.name as location, uts.name as transaction_status, tm.name as bd
        FROM user_transaction ut
        LEFT JOIN users u ON ut.user_id = u.id
        LEFT JOIN source s ON s.id = ut.source_id
        LEFT JOIN treatment t ON t.id = u.treatment_id
        LEFT JOIN location l ON l.id = u.location_id
        LEFT JOIN user_trxn_status uts ON uts.id = ut.user_trxn_status_id
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

config = {
    'user': 'root',
    'password': 'root',
    'host': 'localhost',
    'port': 8889,
    'database': 'bd_data',
    'raise_on_warnings': True,
}

weights = assign_weights_from_database(config)
leads = get_lead_data(config)
leads = preprocess_data(leads, weights)

df = pd.DataFrame(leads)

# Display the DataFrame with all float values up to 4 decimal places
pd.options.display.float_format = '{:.4f}'.format

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

df = df[['enquiry_id', 'patient_name', 'bd', 'source', 'treatment', 'location', 'total_importance', 'priority']]
#print(df)
#print(df[['total_importance','priority']]) 