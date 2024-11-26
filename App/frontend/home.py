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

# Custom CSS for logo positioning
st.markdown("""
    <style>
    .header-container {
        display: flex;
        align-items: center;
        gap: 20px;
        padding: 10px 0;
    }
    .logo-img {
        width: 100px;
    }
    .title-text {
        margin: 0;
        font-size: 2.5em;
    }
    </style>
""", unsafe_allow_html=True)


# Move logo placement to top of sidebar
with st.sidebar:
    # Container for logo with custom CSS class
    st.markdown('<div class="sidebar-logo">', unsafe_allow_html=True)
    
    # Get current directory and construct absolute path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(current_dir, "logo.png")
    
    # Display logo
    if os.path.exists(image_path):
        st.image(image_path, width=100, use_container_width=True)
    else:
        st.error("Logo not found")
    
    st.markdown('</div>', unsafe_allow_html=True)


        
    # Other sidebar content
    st.success("Select a demo above.")

# Main content
st.write("# Welcome to GEI Bot 👋")