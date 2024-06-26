import streamlit as st
import requests
import json
import base64

# Flask server URL
UPLOAD_URL = 'http://127.0.0.1:5500/uploadFile'
ASK_URL = 'http://127.0.0.1:5500/ask'

def upload_file(file):
    if not file:
        st.error("File is required")
        return

    try:
        # Read the file content
        file_content = file.getvalue()
        file_extension = file.name.split('.')[-1]
        
        # Encode file content to base64
        encoded_file_content = base64.b64encode(file_content).decode('utf-8')
        
        payload = {
            "fileContent": encoded_file_content,
            "fileExtension": file_extension
        }

        response = requests.post(UPLOAD_URL, json=payload)
        response_data = response.json()

        if response.status_code == 200:
            st.success(response_data["response"])
        else:
            st.error(response_data["error"])
    except Exception as e:
        st.error(str(e))

def ask_question(question):
    if not question:
        st.error("Question is required")
        return

    payload = {"question": question}
    try:
        response = requests.post(ASK_URL, json=payload)
        response_data = response.json()

        if response.status_code == 200:
            st.success("Answer: " + response_data["response"])
        else:
            st.error(response_data["error"])
    except Exception as e:
        st.error(str(e))

# Streamlit UI
st.title("File Upload and Question Interface")

# File upload section
st.header("Upload a File")
uploaded_file = st.file_uploader("Choose a file", type=["pdf", "txt", "docx"])
if st.button("Upload File"):
    upload_file(uploaded_file)

# Ask question section
st.header("Ask a Question")
question = st.text_input("Question")
if st.button("Send Question"):
    ask_question(question)
