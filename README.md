# Capstone Project: Chatbot Documentation

## Overview
This chatbot application for our Engineering Science Capstone Project is an AI-powered document management system that enables users to upload PDFs, query documents, and interact with content through a conversational interface. Leveraging OpenAI's capabilities, the system provides seamless integration between document storage, embedding generation, and conversational querying, enhancing productivity and information retrieval.

## Project Structure

```
App/
├── backend/
│   ├── api.py          # Flask server
│   ├── temp/           # Temporary PDF storage
│   └── temp2/          # Embeddings storage
└── frontend/
    ├── home.py         # Main Streamlit app
    ├── pages/
    │   ├── documentQuery.py
    │   └── fileUploader.py
    └── logo.png

```

## Setup Instructions

### Prerequisites
Before setting up the Chatbot, ensure you have the following installed on your Windows machine:

- **Python 3.8+**: [Download Python](https://www.python.org/downloads/)
- **Git**: [Download Git](https://git-scm.com/downloads)
- **VSCode**: [Download Visual Studio Code](https://code.visualstudio.com/download)
- **OpenAI API Key**: Sign up and obtain an API key from [OpenAI](https://platform.openai.com/account/api-keys)

### Installation

#### 1. Clone the Repository
1. Open **Visual Studio Code (VSCode)**.
2. Open the terminal in VSCode by navigating to **View > Terminal** or pressing ``Ctrl + ` ``.
3. Clone the Chatbot repository. Replace `[repository-url]` with the actual URL of your repository.

    ```bash
    git clone [repository-url]
    cd Capstone_Chatbot/App
    ```

    **Note:** Ensure you have access to the GitHub repository. If the repository is private, request access from the repository owner.

#### 2. Set Up the Virtual Environment
1. **Open a new terminal** in VSCode or use Git Bash.
2. Navigate to the project directory if not already there.

    ```bash
    cd Capstone_Chatbot/App
    ```

3. Create a virtual environment named `openai-env`:

    ```bash
    python -m venv openai-env
    ```

4. Activate the virtual environment:

    - **Using Git Bash:**

        ```bash
        source openai-env/Scripts/activate
        ```

    - **Using Command Prompt:**

        ```bash
        openai-env\Scripts\activate
        ```

    You should see `(openai-env)` prefixed in your terminal, indicating the virtual environment is active.


### Configuration

#### 1. Set Up the OpenAI API Key
1. Navigate to [OpenAI API Keys](https://platform.openai.com/account/api-keys).
2. Click on **"Create new secret key"** and copy the generated API key.
3. In the Git Bash terminal within VSCode, set the environment variable:

    ```bash
    export OPENAI_API_KEY="your-api-key"
    ```

    **Note:** Replace `"your-api-key"` with the actual API key you copied.

    **For Command Prompt Users:**

    ```cmd
    set OPENAI_API_KEY="your-api-key"
    ```

    To ensure the environment variable is set every time you open a new terminal, consider adding it to your system environment variables.

### Running the Application

#### 1. Start the Backend Server
1. Ensure the virtual environment is activated.
2. In the terminal, navigate to the `backend` directory:

    ```bash
    cd backend
    ```

3. Run the Flask backend:

    ```bash
    python api.py
    ```

4. **Expected Terminal Output:**

    ```
    2024-11-25 17:41:08,869 - DEBUG - load_ssl_context verify=True cert=None trust_env=True http2=False
    2024-11-25 17:41:08,871 - DEBUG - load_verify_locations cafile='C:\\Users\\hkhur\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\certifi\\cacert.pem'
     * Serving Flask app 'api'
     * Debug mode: on
    2024-11-25 17:41:09,272 - INFO - WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
     * Running on all addresses (0.0.0.0)
     * Running on http://127.0.0.1:5500
     * Running on http://100.66.5.6:5500
    2024-11-25 17:41:09,288 - INFO - Press CTRL+C to quit
    2024-11-25 17:41:09,304 - INFO -  * Restarting with watchdog (windowsapi)
    2024-11-25 17:41:14,456 - DEBUG - load_ssl_context verify=True cert=None trust_env=True http2=False
    2024-11-25 17:41:14,458 - DEBUG - load_verify_locations cafile='C:\\Users\\hkhur\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\certifi\\cacert.pem'
    2024-11-25 17:41:14,825 - WARNING -  * Debugger is active!
    2024-11-25 17:41:14,829 - INFO -  * Debugger PIN: 129-185-596
    ```

    This indicates that the backend server is running and accessible at `http://127.0.0.1:5500` and `http://100.66.5.6:5500`.

#### 2. Run the Frontend Application
1. **Open a new terminal** in VSCode or a new Git Bash window to keep the backend running.
2. Activate the virtual environment if not already active:

    ```bash
    source openai-env/Scripts/activate
    ```

    **Or for Command Prompt:**

    ```cmd
    openai-env\Scripts\activate
    ```

3. Navigate to the `frontend` directory:

    ```bash
    cd frontend
    ```

4. Run the Streamlit frontend:

    ```bash
    streamlit run home.py
    ```

5. **Expected Behavior:**
    - Streamlit will launch the frontend application.
    - A new browser window or tab should automatically open, displaying the home page of the Chatbot website.
    - If it doesn't open automatically, navigate to the URL provided in the terminal (usually `http://localhost:8501`).

### Using the Application

1. **Uploading a PDF:**
    - Navigate to the **File Uploader** page.
    - Select a PDF file from your local machine.
    - Optionally, specify a category for the document.
    - Click **Upload** to add the document to the system. The backend will process the PDF, extract text, generate embeddings, and store them for future queries.

2. **Querying Documents:**
    - Navigate to the **Document Query** page.
    - Enter your query or question related to the uploaded documents.
    - Select the desired thread or create a new one for the conversation.
    - Interact with the chatbot to retrieve information based on your query.

3. **Managing Threads:**
    - Use the **Threads** endpoint to create, list, or delete conversation threads.
    - Each thread maintains its own context, allowing for organized and context-aware interactions.

### Troubleshooting

- **Backend Server Not Starting:**
    - Ensure that all dependencies are installed correctly.
    - Verify that the `OPENAI_API_KEY` is set correctly in the environment variables.
    - Check for any port conflicts on `5500`.

- **Frontend Not Loading:**
    - Ensure the backend server is running.
    - Verify that the Streamlit app is running without errors.
    - Check your firewall settings to allow connections to the specified ports.

- **API Key Issues:**
    - Ensure that the OpenAI API key is correct and has the necessary permissions.
    - Verify that the API key is set in the environment variables correctly.

- **File Upload Errors:**
    - Ensure that the uploaded file is a valid PDF.
    - Check the backend logs (`app.log`) for detailed error messages.

### Additional Information

- **Logging:**
    - The backend Flask server logs detailed information to both the console and the `app.log` file located in the `backend` directory.
    - Logs include debug information, errors, and informational messages to help monitor the application's behavior.

- **Environment Variables:**
    - It's recommended to manage sensitive information like API keys using environment variables to enhance security.
    - Consider using tools like [dotenv](https://github.com/theskumar/python-dotenv) for managing environment variables in development.

- **Virtual Environment:**
    - Always activate the virtual environment before running backend or frontend services to ensure dependencies are correctly loaded.

### Contributing

Contributions are welcome! If you encounter issues or have suggestions for improvements, please open an issue or submit a pull request.


