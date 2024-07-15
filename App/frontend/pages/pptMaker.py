import streamlit as st
import requests
import sys
import os
from io import BytesIO

# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from modules.CloudUtils import gdrive

st.markdown("# PPT Maker")

st.sidebar.markdown("## Welcome to PPT Maker")

# Flask server URL
MAKE_PPT_URL = 'http://127.0.0.1:5500/make-ppt'

def make_ppt(topic):
    if not topic:
        st.error("Presentation topic is required")
        return

    payload = {"topic": topic}
    try:
        with st.spinner("Creating your presentation..."):
            response = requests.post(MAKE_PPT_URL, json=payload)
            print('frontend response received')

            if response.status_code == 200:
                ppt_file_bytes = response.content
                ppt_file = BytesIO(ppt_file_bytes)
                ppt_file.name = "RequiredPresentation.pptx"

                st.success("Presentation created successfully")
                st.download_button(
                    label="Download the presentation",
                    data=ppt_file,
                    file_name=f"{topic}.pptx",
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                )
            else:
                response_data = response.json()
                st.error(response_data["error"])
    except Exception as e:
        st.error(str(e))

# Make PPT section
st.header("Create a PowerPoint Presentation")
topic = st.text_input("Presentation Topic")
if st.button("Generate PPT"):
    make_ppt(topic)
