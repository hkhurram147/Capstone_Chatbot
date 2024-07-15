import streamlit as st
import requests
import sys
import os
# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from modules.CloudUtils import gdrive

st.markdown( "#File Uploader")

st.sidebar.markdown("## Welcome to File Uploader")


import shutil
docuQueryFolderID='1J19XU6RdlnVlCd-4y_R7YRN1Uw6JzDgl'
def delete_folder(folder_path):
    # Check if the folder exists
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        shutil.rmtree(folder_path)
        return 1
    else:
        return 0

# Flask server URL
UPLOAD_URL = 'http://127.0.0.1:5500/uploadFile'

def upload_file(file,folderid):
    if not file:
        st.write(file)
        st.error("File is required")
        return

    try:
        response = gdrive.upload(file,folderid)
        response_data = response.json()
        if response.status_code == 200:
            st.success(response_data["response"])
            return 1
        else:
            st.error(response_data["error"])
            return 0
    except Exception as e:
        st.error(str(e))
        return 0

# Streamlit UI
st.title("File Upload Interface")

# File upload section
st.header("Upload a File")

uploadbtn = st.button("Upload File")
if "uploadbtn_state" not in st.session_state:
    st.session_state.uploadbtn_state = False
upload_success=None
if uploadbtn or st.session_state.uploadbtn_state:
    st.session_state.uploadbtn_state = True
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "txt", "docx"])
    if uploaded_file is not None:
        # Save the uploaded file to a temporary location
        temp_file_path = os.path.join("temp", uploaded_file.name)
        
        # Ensure the 'temp' directory exists
        os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)
        
        # Write the file to the specified path
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        
        # Upload the file to Google Drive
        upload_success=upload_file(temp_file_path,docuQueryFolderID)
