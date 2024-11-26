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

# Create two columns: left for title, right for logo
col1, col2 = st.columns([3, 1])

with col1:
    st.write("# Welcome to GEI Bot 👋")

with col2:
    # Construct absolute path to image
    image_path = os.path.join(current_dir, "logo.png")
    
    # Add debug print to verify path
    print(f"Looking for image at: {image_path}")
    
    # Check if file exists before trying to display
    if os.path.exists(image_path):
        st.image(image_path, width=100, use_container_width=False)
    else:
        st.error(f"Logo file not found at {image_path}")

# Sidebar content
st.sidebar.success("Select a demo above.")