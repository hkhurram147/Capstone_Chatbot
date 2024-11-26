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

# Custom CSS to style the sidebar logo
st.markdown("""
    <style>
    .sidebar-logo {
        margin-bottom: 20px;
        text-align: left;
        padding: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)
# Sidebar logo placement
with st.sidebar:
    # Container for logo with custom CSS class
    st.markdown('<div class="sidebar-logo">', unsafe_allow_html=True)
    
    # Construct absolute path to image
    image_path = os.path.join(current_dir, "logo.png")
    
    # Check if file exists before trying to display
    if os.path.exists(image_path):
        st.image(image_path, width=200, use_container_width=False)  # Updated parameter
    else:
        st.error("Logo not found")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Other sidebar content
    st.success("Select a demo above.")

# Main content
st.write("# Welcome to GEI Bot 👋")