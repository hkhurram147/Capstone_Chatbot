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

# Create header with logo and title
current_dir = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(current_dir, "logo.png")

header_html = f"""
<div class="header-container">
    <img src="data:image/png;base64,{open(image_path, "rb").read().hex()}" class="logo-img">
    <h1 class="title-text">Welcome to GEI Bot 👋</h1>
</div>
"""

with st.sidebar:
        
    # Other sidebar content
    st.success("Select a demo above.")

# Main content
st.write("# Welcome to GEI Bot 👋")