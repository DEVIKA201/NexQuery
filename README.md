# Sales BD AI Agent - Smart Chat Bot

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Project Structure](#project-structure)

## Introduction
The Sales BD AI Agent is a smart chat-bot designed to assist in managing and analyzing sales data. It leverages machine learning and natural language processing to answer queries related to lead details, combined lead details, and lead counts. It integrates with MySQL to fetch data and uses OpenAI's API for enhanced query handling.

## Features
- Fetch and preprocess sales lead data from a MySQL database
- Assign weights based on conversion rates for locations, treatments, and sources
- Classify leads based on their importance into categories: Critical, Essential, Routine
- Handle and respond to various types of queries related to sales data
- Integrate with OpenAI for advanced natural language understanding

## Features
sales-bd-ai-agent/
├── README.md
├── weight_assign.py
├── queries.py
├── app.py
├── requirements.txt
