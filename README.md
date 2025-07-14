# NexQuery: A Chatbot driven Database Discoverer
## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Project Structure](#project-structure)
- [Packages Needed](#packages-needed)
- [Sample Queries](#sample-queries)

## Introduction
The NexQuery is a smart chatbot designed to assist in managing and analyzing sales data. It leverages machine learning and natural language processing to answer queries related to lead details, combined lead details, and lead counts. It integrates with MySQL to fetch data and uses OpenAI's API for enhanced query handling.

## Features
- Fetch and preprocess sales lead data from a MySQL database
- Assign weights based on conversion rates for locations, treatments, and sources
- Classify leads based on their importance into categories: Critical, Essential, Routine
- Handle and respond to various types of queries related to sales data
- Integrate with OpenAI for advanced natural language understanding

## Project Structure
The project has the following structure:

sales-bd-ai-agent/
├── README.md
├── weight_assign.py
├── queries.py
├── app.py
├── requirements.txt
├── style.css


- **README.md**: This file, providing an overview of the project.
- **weight_assign.py**: Module for assigning weights based on conversion rates.
- **queries.py**: Contains the QueryHandler class for processing user queries.
- **app.py**: Main application file containing the Streamlit chatbot interface.
- **requirements.txt**: File listing the Python packages required for the project.
- **style.css**: CSS file for custom styling of the Streamlit interface.

## Packages Needed
To run the project, you need to install the following Python packages:

- Python3
- **mysql-connector-python**: pip3 install mysql-connector-python
- **pandas**: pip3 install pandas
- **streamlit**: pip3 install streamlit
- **spacy**: pip3 install spacy
- **transformers**: pip3 install transformers
pip install streamlit-toast


## Sample Queries
Here are some example queries that the Sales BD AI Agent can handle:

1. Count entries for priority Critical
2. Show me all entries for bd Riley
3. Show entries with source Patient Referral and treatment Varicose Vein
4. Show me all entries for bd Riley in location Vijayawada and treatment Piles.
5. Display only name, source, for treatment Lipoma in location Chennai
6. Show all entries for bd Riley with location Bengaluru display only enquiry_id, name, location
7. Show me all entries for bd Riley. Display only priority
8. Show me all entries for bd Riley in location Vijayawada and treatment Piles. Display only bd
