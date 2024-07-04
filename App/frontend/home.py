import streamlit as st
from pages import dataIngestion,documentGenerator,documentQuery,pptMaker
import sys
import os
# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import modules.CloudUtils


# Function to navigate to a different page
def navigate_to(page):
    st.session_state.page = page
# Initialize session state for page navigation
if 'page' not in st.session_state:
    st.session_state.page = 'page'
    st.header("Welcome To Pheonix")
    st.write("Please select a tool on the left sidebar")
elif 'page' in st.session_state:
    st.session_state.page = 'page'
    st.header("Welcome To Pheonix")
    st.write("Please select a tool on the left sidebar")
# Render the appropriate page based on the session state
if st.session_state.page == 'documentQuery':
    documentQuery.show(navigate_to)
elif st.session_state.page == 'dataIngestion':
    dataIngestion.show(navigate_to)
elif st.session_state.page == 'documentGenerator':
    documentGenerator.show(navigate_to)
elif st.session_state.page == 'pptMaker':
    pptMaker.show(navigate_to)
