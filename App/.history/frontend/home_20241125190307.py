import streamlit as st
import os

# Set page config
st.set_page_config(page_title="Welcome to GEI Bot!", page_icon="👋", layout="wide")

# Create two columns for logo and title
col1, col2 = st.columns([1, 4])

# Get logo path
current_dir = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(current_dir, "logo.png")

# Display logo in first column
with col1:
    if os.path.exists(image_path):
        st.image(image_path, width=100)
    else:
        st.error("Logo not found")

# Display title in second column
with col2:
    st.title("Welcome to GEI Bot 👋")

# Sidebar content
with st.sidebar:
    st.success("Select a demo above.")