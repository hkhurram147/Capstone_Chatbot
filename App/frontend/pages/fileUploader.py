import streamlit as st
import requests
import os

# Flask server URL
UPLOAD_URL = 'http://127.0.0.1:5500/uploadFile'

st.title("PDF Upload Interface")

# File upload section
st.header("Upload a PDF File")

# File uploader component
uploaded_file = st.file_uploader("Choose a file", type=["pdf"])

# Function to upload file to backend server
def upload_file_to_backend(file_path):
    with open(file_path, "rb") as f:
        files = {'file': f}
        response = requests.post(UPLOAD_URL, files=files)
        if response.status_code == 200:
            st.success("File successfully uploaded!")
        else:
            st.error("Failed to upload file.")

if uploaded_file:
    # Check if the uploaded file is a PDF
    if uploaded_file.type == "application/pdf":
        # Save the uploaded file temporarily
        temp_file_path = os.path.join("temp", uploaded_file.name)
        
        # Ensure the 'temp' directory exists
        os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)
        
        # Write the file to the specified path
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Upload file to the backend
        upload_file_to_backend(temp_file_path)

        # Clean up temporary file after upload
        os.remove(temp_file_path)
    else:
        st.error("Only PDF files are allowed. Please upload a valid PDF.")
