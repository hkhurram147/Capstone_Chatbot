import streamlit as st
import requests
import sys
import os


st.markdown( "# Document Query")

st.sidebar.markdown("## WELCOME TO DOCUMENT QUERY")

# Flask server URL
BASE_URL = 'http://127.0.0.1:5500'
ASK_URL = f'{BASE_URL}/ask'
THREADS_URL = f'{BASE_URL}/threads'

def get_threads():
    try:
        response = requests.get(THREADS_URL)
        if response.status_code == 200:
            return response.json().get('threads', [])
        else:
            st.error("Failed to fetch threads")
            return []
    except Exception as e:
        st.error(f"Error fetching threads: {str(e)}")
        return []

def create_thread(name):
    try:
        payload = {}
        if name.strip():
            payload['name'] = name.strip()
        response = requests.post(THREADS_URL, json=payload)
        if response.status_code == 201:
            data = response.json()
            thread_id = data.get('thread_id')
            thread_name = data.get('name')
            st.session_state.selected_thread = thread_id
            st.session_state.selected_thread_name = thread_name
            st.success(f"Thread '{thread_name}' created")
        else:
            st.error("Failed to create thread")
    except Exception as e:
        st.error(f"Error creating thread: {str(e)}")

def delete_thread(thread_id):
    try:
        response = requests.delete(f"{THREADS_URL}/{thread_id}")
        if response.status_code == 200:
            st.success(f"Thread {thread_id} deleted")
            if st.session_state.selected_thread == thread_id:
                st.session_state.selected_thread = None
                st.session_state.selected_thread_name = None
        else:
            st.error("Failed to delete thread")
    except Exception as e:
        st.error(f"Error deleting thread: {str(e)}")

def ask_question(question, thread_id):
    if not question:
        st.error("Question is required")
        return

    payload = {"question": question, "thread_id": thread_id}
    try:
        st.write(f"Sending request to {ASK_URL} with payload: {payload}")  # Debugging info
        response = requests.post(ASK_URL, json=payload)
        response_data = response.json()

        if response.status_code == 200:
            st.success("Answer: " + response_data.get("response", "No response received."))
        else:
            # Display the error from the backend
            st.error("Error: " + response_data.get("error", "An error occurred."))
    except Exception as e:
        st.error(f"Request failed: {str(e)}")

# Initialize session state
if 'selected_thread' not in st.session_state:
    st.session_state.selected_thread = None
if 'selected_thread_name' not in st.session_state:
    st.session_state.selected_thread_name = None

# Sidebar for thread management
st.sidebar.header("Threads")
thread_name_input = st.sidebar.text_input("New Thread Name (optional)")
threads = get_threads()  # Initialize threads before handling buttons

if st.sidebar.button("Create New Thread"):
    create_thread(thread_name_input)
    threads = get_threads()

if threads:
    thread_options = {thread['name']: thread['id'] for thread in threads}
    selected_thread_name = st.sidebar.selectbox("Select a thread", list(thread_options.keys()))
    selected_thread_id = thread_options[selected_thread_name]
    st.session_state.selected_thread = selected_thread_id
    st.session_state.selected_thread_name = selected_thread_name

    if st.sidebar.button("Delete Thread"):
        delete_thread(selected_thread_id)
        threads = get_threads()
else:
    st.sidebar.write("No threads available.")

if st.session_state.selected_thread:
    st.write(f"Using Thread: {st.session_state.selected_thread_name}")

    # Ask question section
    st.header("Ask a Question")
    question = st.text_input("Question")
    if st.button("Send Question"):
        ask_question(question, st.session_state.selected_thread)
else:
    st.write("Please select or create a thread to continue.")