import streamlit as st
import os

# Get the directory containing the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Custom CSS at the beginning of the file
st.markdown("""
    <style>
    .sidebar-logo {
        position: relative;
        top: 0;
        left: 0;
        margin-top: -60px;  /* Adjust to move logo higher */
        margin-left: -30px; /* Adjust for left alignment */
        padding: 0;
        text-align: left;
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
        st.image(image_path, width=100, use_container_width=False)
    else:
        st.error("Logo not found")
    
    st.markdown('</div>', unsafe_allow_html=True)


    
# Other sidebar content
st.success("Select a demo above.")

# Main content
st.write("# Welcome to GEI Bot 👋")