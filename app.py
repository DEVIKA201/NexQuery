import streamlit as st
import spacy
import weight_assign
import queries

st.title("Sales BD AI Agent - Smart Chat Bot")

query = st.text_area("Enter your query: ","")

if st.button("Submit"):
    if query:
        query_handler = queries.QueryHandler()
        dataframe_context = weight_assign.df.to_string(index=False)
        response = queries.ask_openai(query, dataframe_context)
        st.write(response)
    else:
        st.warning("Please enter your query: ")
        




