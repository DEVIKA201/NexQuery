import streamlit as st
from datetime import datetime
from queries import QueryHandler
from alert import check_new_leads, check_old_new_leads
from weight_assign import df  # Import the DataFrame from weight_assign.py
import time


st.set_page_config(page_title="NexQuery - Chatbot", layout="wide")

def load_css():
    with open("style.css", "r") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

load_css()

def chatbot_interface():
    st.markdown('<p class="title-text">Sales BD AI Agent - Chatbot</p>', unsafe_allow_html=True)
    
    query = st.text_input("Enter your query:")

    if query:
        st.markdown(f"""
            <div class="message-container">
                <div class="user-message">{query}</div>
            </div>
        """, unsafe_allow_html=True)

        with st.spinner("Processing..."):
            dataframe_context = df
            query_handler = QueryHandler(dataframe_context)

            try:
                response = query_handler.process_query(query)
                st.markdown(f"""
                    <div class="message-container">
                        <div class="bot-message">{response}</div>
                    </div>
                """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
        
    else:
        st.warning("Please enter your query.")

def display_alerts():
    st.markdown("<h2>Alerts</h2>", unsafe_allow_html=True)

    new_leads = check_new_leads(df)
    old_new_leads = check_old_new_leads(df)

    if 'alert_start_time' not in st.session_state:
        st.session_state.alert_start_time = datetime.now()

    if 'show_new_leads_expander' not in st.session_state:
        st.session_state.show_new_leads_expander = False

    if 'show_old_leads_expander' not in st.session_state:
        st.session_state.show_old_leads_expander = False

    current_time = datetime.now()
    elapsed_time = (current_time - st.session_state.alert_start_time).seconds

    # Reset expanders and clear alerts after 10 seconds
    if elapsed_time > 10:
        st.session_state.show_new_leads_expander = False
        st.session_state.show_old_leads_expander = False
        st.session_state.alert_start_time = datetime.now()  # Reset the timer

        # Clear alert content after 10 seconds
        st.session_state.alert_content = ""

    if not new_leads.empty and not st.session_state.show_new_leads_expander:
        display_toast(f"{len(new_leads)} recently added new lead(s) available!", icon='😍')
        st.session_state.alert_content = f"""
            <div class="message-container">
                <div class="bot-message">
                    <p>{len(new_leads)} recently added new lead(s) available!</p>
                    <div class="expander">
                        <details>
                            <summary>View details</summary>
                            <div class="scrollable">
                                {new_leads.sort_values(by='priority', ascending=False).to_html(index=False)}
                            </div>
                        </details>
                    </div>
                </div>
            </div>
        """
        
        st.session_state.show_new_leads_expander = True
        st.session_state.alert_start_time = datetime.now()  # Start timer

    if not old_new_leads.empty and not st.session_state.show_old_leads_expander:
        display_toast(f"{len(old_new_leads)} old lead(s) still marked as 'New Lead'!", icon='⚠️')
        st.session_state.alert_content = f"""
            <div class="message-container">
                <div class="bot-message">
                    <p>{len(old_new_leads)} old lead(s) still marked as 'New Lead'!</p>
                    <div class="expander">
                        <details>
                            <summary>View details</summary>
                            <div class="scrollable">
                                {old_new_leads.sort_values(by='priority', ascending=False).to_html(index=False)}
                            </div>
                        </details>
                    </div>
                </div>
            </div>
        """
        st.session_state.show_old_leads_expander = True
        st.session_state.alert_start_time = datetime.now()  # Start timer

    if 'alert_content' in st.session_state and st.session_state.alert_content:
        st.markdown(st.session_state.alert_content, unsafe_allow_html=True)

def display_toast(message, icon=None):
    st.toast(message, icon=icon)

if __name__ == "__main__":
    chatbot_interface()
    
    while True:
        display_alerts()
        time.sleep(60)  # Poll every 10 seconds for new leads
