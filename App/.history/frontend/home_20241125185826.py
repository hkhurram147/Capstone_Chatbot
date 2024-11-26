import streamlit as st
import os

# Get the directory containing the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Set page configuration
st.set_page_config(
    page_title="Welcome to GEI Bot!",
    page_icon="👋",
    layout="wide"
)


    
# Other sidebar content
st.success("Select a demo above.")

# Main content
st.write("# Welcome to GEI Bot 👋")