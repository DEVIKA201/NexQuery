#pip install langchain
#pip install faiss-cpu *
#pip install openai
#pip install llama_index

import weight_assign
import re
import spacy
import openai
import pandas as pd
import queries

nlp = spacy.load('en_core_web_sm')
df = weight_assign.df

class QueryHandler:
#parsing the query
    def parse_query(self, query):
        doc = nlp(query.lower())
        entities = {ent.label_: ent.text for ent in doc.ents}
        return entities

#basic lead deatils like location, treatment, priority, BD, source, high and low importance
    def lead_details(self, query):
        query=query.lower()

        if 'patient' in query:
            return df[['enquiry_id', 'patient_name']].to_string(index=False)   
        elif 'priority' in query:
            if 'critical' in query:
                return df[df['priority'] == 'Critical'][['enquiry_id', 'priority']].to_string(index=False)
            elif 'essential' in query:
                return df[df['priority'] == 'Essential'][['enquiry_id', 'priority']].to_string(index=False)
            return df[['enquriy_id', 'priority']].to_string(index = False)
        elif 'treatment' in query:
            treatment = re.findall(r'treatment (\w+)', query)
            if treatment:
                return df[df['treatment'].str.lower() == treatment[0].lower()][['enquiry_id', 'treatment']].to_string(index=False)  
            return df[['enquiry_id', 'treatment']].to_string(index = False)
        elif 'location' in query:
            location = re.findall(r'location (\w+)', query)
            if location:
                return df[df['location'].str.lower() == treatment[0].lower()][['enquiry_id', 'location']].to_string(index=False)  
            return df[['enquiry_id', 'location']].to_string(index= False)
        elif 'importance' in query:
            if 'high' in query:
                return df[df['total_importance'] >= 0.1][['enquiry_id', 'total_importance']].to_string(index=False)
            elif 'low' in query:
                return df[df['total_importance'] < 0.1][['enquiry_id', 'total_importance']].to_string(index=False)
            return df[['enquiry_id','total_importance']].to_string(index=False)          
        else:
            return "Query not accurate. Please provide a more detailed question."

#Combining multiple conditions
    def combined_lead_details(self, query):
        entities = self.parse_query(query)
        query = query.lower()
        if 'priority' in query and 'location' in query:
            location = re.findall(r'location (\w+)',query)
            priority = re.findall(r'priority (\w+)',query)
            if location and priority:
                return df[(df['location'].str.lower() == location[0].lower()) & (df['priority'].str.lower() == priority[0].lower())][['enquiry_id','priority','location']].to_string(index =False)
            elif 'priority' in query and 'source' in query:
                source = re.findall(r'source (\w+)',query)
                priority = re.findall(r'priority (\w+)',query)
                if source and priority:
                    return df[(df['source'].str.lower() == source[0].lower()) & (df['priority'].str.lower() == priority[0].lower())][['enquiry_id','priority','source']].to_string(index =False) 
            elif 'priority' in query and 'treatment' in query:
                treatment = re.findall(r'treatment (\w+)',query) 
                priority = re.findall(r'priority (\w+)',query)
                if treatment and priority:
                    return df[(df['treatment'].str.lower() == treatment[0].lower()) & (df['priority'].str.lower() == priority[0].lower())][['enquiry_id','priority','treatment']].to_string(index =False) 
            elif 'priority' in query and 'BD' in entities:
                bd = entities['BD']
                return df[df['bd'].str.lower() == bd][['enquiry_id','bd']].to_string(index=False)
            else:
                return "Query not accurate. Please provide a more detailed question."

#handle aggregate functions
    def lead_count(self, query):
        query = query.lower()

        if 'total count' in query:
            if 'patient' in query: 
                print(f"Total number of patients: {df['patient_name'].nunique()}")
                return f"Total number of patients: {df['patient_name'].nunique()}"
            
            elif 'treatment' in query:
                treatment = query.split('treatment ')[-1].strip()
                return f"Number of cases for treatment '{treatment}': {df[df['treatment'].str.lower() == treatment.lower()].shape[0]}"
            elif 'priority' in query:
                priority = query.split('priority ')[-1].strip()
                return f"Number of cases with priority '{priority}': {df[df['priority'].str.lower() == priority.lower()].shape[0]}"
            elif 'source' in query:
                source = query.split('source ')[-1].strip()
                return f"Number of cases in source '{source}': {df[df['source'].str.lower() == source.lower()].shape[0]}"            
            else:
                "Query not acceptable. Kindly enquire with respect to the context."
        elif 'average' in query:
            if 'importance' in query:
                return f"Average importance: df{['total_importance'].mean():.4f}"
        else:
            return "Query not accurate. Please provide a more detailed question."

    #handler function
    def handle_query(self, query):
        method_map = {
            'lead details' : 'lead_details',
            'combined lead details': 'combined_lead_details',
            'lead count': 'lead_count'
        }

        #determining the method to call
        for key in method_map:
            if key in query.lower():
                method_name = method_map[key]
                method = getattr(self, method_name)
                return method(query)
        return "Query not accurate. Please provide a more detailed question."

#OpenAI API
openai.api_key = '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'

#integrate openai
def ask_openai(query, dataframe_context):
    response = openai.completions.create(
        model = "gpt-3.5-turbo-instruct",
        prompt= f"The answer to your query:\n\n{dataframe_context}\n\nUser query: {query}\n\nAnswer:",
        max_tokens= 150 
    )
    return response.choices[0].text.strip()

while True:
    user_query = input("Enter your query: ")
    if user_query.lower() in ['exit','quit','Exit']:
        break
    dataframe_context = df.to_string(index = False)
    response = ask_openai(user_query, dataframe_context)
    print(response) 
