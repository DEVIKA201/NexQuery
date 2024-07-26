import spacy
from transformers import pipeline, GPT2Tokenizer, GPT2LMHeadModel
import re

class QueryHandler:
    def __init__(self, dataframe):
        self.dataframe = dataframe
        self.available_columns = self.dataframe.columns.tolist()
        self.nlp = spacy.load("en_core_web_sm")
        self.gpt2_tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
        self.gpt2_tokenizer.pad_token_id = self.gpt2_tokenizer.eos_token_id  
        self.gpt2_model = GPT2LMHeadModel.from_pretrained("gpt2")
        self.gpt2 = pipeline("text-generation", model=self.gpt2_model, tokenizer=self.gpt2_tokenizer)

    def process_query(self, query):
        conditions, columns = self.extract_conditions_and_columns_from_query(query)
        response = self.handle_column_query(conditions, columns, query)
        if response:
            return response
        return "**No entries found matching the conditions.**"

    def extract_conditions_and_columns_from_query(self, query):
        conditions = {}
        columns = []

        # Use spaCy to process the query
        doc = self.nlp(query.lower())

        # Define patterns for matching conditions
        patterns = {
            'priority': 'priority',
            'location': 'location',
            'treatment': 'treatment',
            'bd': 'bd',
            'patient_name': 'patient name',
            'source': 'source',
        }

        # Extract conditions from the query
        for token in doc:
            for key, pattern in patterns.items():
                if pattern in token.text:
                    next_token_idx = token.i + 1
                    if next_token_idx < len(doc):
                        next_token = doc[next_token_idx]
                        conditions[key] = next_token.text.strip()

        # Extract columns to display
        for ent in doc.ents:
            if ent.label_ == "NOUN" and ent.text in self.available_columns:
                columns.append(ent.text)

        # Fallback to regex for extracting display only part
        display_match = re.search(r'display\s+only\s+(.+)', query)
        if display_match:
            display_cols = display_match.group(1).strip().split(',')
            columns.extend([col.strip() for col in display_cols if col.strip() in self.available_columns])

        return conditions, columns

    def handle_column_query(self, conditions, columns, query):
        if conditions:
            filtered_data = self.dataframe.copy()
            for col, val in conditions.items():
                if col in self.available_columns:
                    filtered_data = filtered_data[filtered_data[col].str.contains(val, case=False, na=False)]

            if not filtered_data.empty:
                # Handling specific column display requests
                if len(columns) > 0:
                    valid_columns = [col for col in columns if col in self.available_columns]
                    if valid_columns:
                        return f"Here are the requested details:\n\n{filtered_data[valid_columns].to_html(index=False, escape=False)}"

                # Prepare GPT-2 prompt
                prompt = f"Based on your query '{query}', I found {len(filtered_data)} entries.\n\n"

                # Combine elements for response
                response = f"Based on your query '{query}', I found {len(filtered_data)} entries.\n\n\n\nHere are the details of the retrieved leads:\n\n{filtered_data.to_html(index=False, escape=False)}"
                return response

            else:
                return f"**No entries found matching the conditions: {conditions}.**"

        return None

    def generate_gpt2_response(self, prompt):
        inputs = self.gpt2_tokenizer(prompt, return_tensors="pt", max_length=150, truncation=True, padding=True)
        outputs = self.gpt2_model.generate(inputs['input_ids'], max_new_tokens=50, pad_token_id=self.gpt2_tokenizer.eos_token_id)
        return self.gpt2_tokenizer.decode(outputs[0], skip_special_tokens=True)

    def count_entries_by_priority(self):
        return self.dataframe['priority'].value_counts().to_string()
