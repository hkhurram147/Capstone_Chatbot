import streamlit as st
import requests
import sys
import os
# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from modules.CloudUtils import gdrive

st.markdown( "# Document Query")

st.sidebar.markdown("## WELCOME TO DOCUMENT QUERY")


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
ASK_URL = 'http://127.0.0.1:5500/ask'

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


# Ask question section
st.header("Ask a Question")
question = st.text_input("Question")
if st.button("Send Question"):
    ask_question(question)