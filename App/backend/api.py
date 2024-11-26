from flask import Flask, request, jsonify, send_file, after_this_request
from openai import OpenAI, OpenAIError

import shutil
import glob
import time
import os
import yaml
import argparse
import sys
from datetime import datetime  # Import datetime module

import os
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pdfplumber
from sentence_transformers import SentenceTransformer
import logging


logging.basicConfig(
    level=logging.DEBUG,  # Set to INFO or WARNING in production
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),       # Logs to console
        logging.FileHandler("app.log") # Logs to a file named app.log
    ]
)

app = Flask(__name__)

UPLOAD_FOLDER = 'temp'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

EMBEDDINGS_DIR = 'temp2'
EMBEDDINGS_FILE = os.path.join(EMBEDDINGS_DIR, 'embeddings.json')


def sanitize_filename(filename):
    """
    Sanitize the filename to prevent directory traversal and other security issues.
    """
    return os.path.basename(filename)


threads = {}  # Dictionary to store thread instances with their names

# Initialize OpenAI client at the global scope
client = OpenAI()
@app.route('/uploadFile', methods=['POST'])
def upload_file():
    # Check if the file is in the request
    if 'file' not in request.files:
        logging.error("No file part in the request")
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    # Check if a file was uploaded
    if file.filename == '':
        logging.error("No selected file")
        return jsonify({"error": "No selected file"}), 400

    # Check if the file is a PDF
    if not file.filename.lower().endswith('.pdf'):
        logging.error("Only PDF files are allowed")
        return jsonify({"error": "Only PDF files are allowed"}), 400

    # Sanitize filename
    sanitized_filename = sanitize_filename(file.filename)
    temp_path = os.path.join(UPLOAD_FOLDER, sanitized_filename)
    
    # Save the uploaded file temporarily
    file.save(temp_path)
    logging.debug(f"File saved temporarily at {temp_path}")

    try:
        # Initialize the OpenAI client (ensure correct initialization based on your SDK)
        client = OpenAI()  # Make sure this is the correct way to initialize

        # Upload the file to the assistant’s vector store
        assistant = client.beta.assistants.retrieve("asst_Wk1Ue0iDYkhbdiXXDPPJsvAV")

        with open(temp_path, "rb") as f:
            file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
                vector_store_id='vs_qUspcB7VllWXM4z7aAEdIK9L', files=[f]
            )

        # Check upload status
        if file_batch.status != "completed":
            logging.error("File upload to vector store failed")
            return jsonify({"error": "File upload to vector store failed"}), 500

        logging.debug("File successfully uploaded to vector store")

        # **Proceed with embedding extraction and storage**

        # Extract text from PDF using pdfplumber
        with pdfplumber.open(temp_path) as pdf:
            pages = pdf.pages
            text = '\n'.join([page.extract_text() for page in pages if page.extract_text()])

        if not text:
            logging.error("No extractable text found in the PDF.")
            return jsonify({"error": "No extractable text found in the PDF."}), 400

        model = SentenceTransformer('all-MiniLM-L6-v2')  # Choose an appropriate model

        # Generate embedding for the extracted text
        embedding = model.encode(text).tolist()  # Convert numpy array to list for JSON serialization

        # **Handle the 'category' field**
        # Example: Extract category from filename assuming format "Category_DocumentName.pdf"
        # Adjust the logic based on your actual filename structure or data source
        try:
            category = sanitized_filename.split('_')[0]  # Example extraction
        except IndexError:
            category = "Uncategorized"

        # Prepare metadata
        doc_id = sanitized_filename
        metadata = {
            "category": category,
            "doc_id": doc_id,
            "file_path": os.path.abspath(temp_path),
            "title": os.path.splitext(sanitized_filename)[0],
            "upload_time": datetime.utcnow().isoformat()
            # Add more metadata fields as needed
        }

        # Load existing embeddings.json or initialize an empty list
        if os.path.exists(EMBEDDINGS_FILE):
            with open(EMBEDDINGS_FILE, 'r') as f:
                embeddings_data = json.load(f)
        else:
            embeddings_data = []

        # Append the new document's embedding and metadata
        embeddings_data.append({
            "doc_id": metadata["doc_id"],
            "embedding": embedding,
            "metadata": metadata
        })

        # Save back to embeddings.json
        with open(EMBEDDINGS_FILE, 'w') as f:
            json.dump(embeddings_data, f, indent=4)
        logging.debug(f"Embeddings for {doc_id} appended to {EMBEDDINGS_FILE}")

        # Clean up the temporary file after processing
        os.remove(temp_path)
        logging.debug(f"Temporary file {temp_path} removed after processing.")

        # **Final Response after all processing is done**
        return jsonify({"response": "File uploaded and embeddings stored successfully."}), 200

    except OpenAIError as e:
        logging.exception("An OpenAI error occurred during file upload and processing.")
        return jsonify({"error": f"OpenAI Error: {str(e)}"}), 500
    except Exception as e:
        logging.exception("An unexpected error occurred during file upload and processing.")
        return jsonify({"error": str(e)}), 500


def ir_stuff(filename, K):
    """
    Find similar documents using pre-computed embeddings from embeddings.json

    Parameters:
    - filename: the file name of the query document in the format "Category\\DocumentName.pdf"
    - K: optional, the number of similar documents to return (default is 5)
    """
    try:
        logging.debug(f"ir_stuff invoked with filename='{filename}' and K={K}")

        # Define paths
        TEMP2_DIR = 'temp2'
        EMBEDDINGS_FILE = os.path.join(TEMP2_DIR, 'embeddings.json')
        logging.debug(f"Using embeddings file at '{EMBEDDINGS_FILE}'")

        # Load pre-computed embeddings
        if not os.path.exists(EMBEDDINGS_FILE):
            logging.error(f"Embeddings file not found at '{EMBEDDINGS_FILE}'")
            return jsonify({"error": "Embeddings file not found"}), 404

        with open(EMBEDDINGS_FILE, 'r') as f:
            all_embeddings = json.load(f)
            logging.debug(f"Loaded {len(all_embeddings)} embeddings from '{EMBEDDINGS_FILE}'")

        # Find the query document embedding from embeddings.json
        query_embedding = None
        for doc in all_embeddings:
            if doc['metadata']["title"] == filename:
                query_embedding = np.array(doc['embedding'])
                logging.debug(f"Found embedding for document '{filename}'")
                break

        if query_embedding is None:
            logging.error(f"Query document '{filename}' not found in embeddings")
            return jsonify({"error": "Query document not found in embeddings"}), 404

        # Calculate cosine similarities
        similarities = []
        for doc in all_embeddings:
            if doc['doc_id'] == filename:
                continue  # Skip the query document itself
            doc_embedding = np.array(doc['embedding'])
            similarity = cosine_similarity(
                query_embedding.reshape(1, -1),
                doc_embedding.reshape(1, -1)
            )[0][0]

            doc_metadata = doc.get('metadata', {})
            category = doc_metadata.get('category', 'Unknown')
            file_path = doc_metadata.get('file_path', 'N/A')
            title = doc_metadata.get('title', 'Untitled')

            similarities.append({
                'doc_id': doc['doc_id'],
                'similarity': float(similarity),
                'category': category,
                'file_path': file_path,
                'title': title
            })

        logging.debug(f"Calculated similarities for {len(similarities)} documents")

        # Sort by similarity in descending order
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        top_similar = similarities[:K]
        logging.info(f"Top {K} similar documents for '{filename}': {top_similar}")

        # Return top K most similar documents
        return jsonify(top_similar), 200

    except Exception as e:
        logging.exception("An error occurred in ir_stuff")
        return jsonify({"error": str(e)}), 500


@app.route('/threads', methods=['GET', 'POST'])
def manage_threads():
    if request.method == 'GET':
        # Return the list of threads with IDs and names
        thread_list = [{'id': thread_id, 'name': info['name']} for thread_id, info in threads.items()]
        return jsonify({"threads": thread_list}), 200
    elif request.method == 'POST':
        # Get thread name from request body
        data = request.get_json()
        thread_name = data.get('name')
        # Set default name to "Thread [DATETIME]" if name is not provided or empty
        if not thread_name or thread_name.strip() == '':
            thread_name = f"Thread {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        # Create a new thread using the OpenAI API
        thread = client.beta.threads.create()
        # Store the thread along with its name
        threads[thread.id] = {'thread': thread, 'name': thread_name}
        return jsonify({"thread_id": thread.id, "name": thread_name}), 201


@app.route('/threads/<thread_id>', methods=['DELETE'])
def delete_thread(thread_id):
    if thread_id in threads:
        del threads[thread_id]
        return jsonify({"message": "Thread deleted"}), 200
    else:
        return jsonify({"error": "Thread not found"}), 404


@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.json
    question = data.get('question')
    thread_id = data.get('thread_id')

    if not question or not thread_id:
        logging.error("Missing question or thread_id in the request.")
        return jsonify({"error": "Question and Thread ID are required."}), 400
    if thread_id not in threads:
        logging.error(f"Thread ID '{thread_id}' not found.")
        return jsonify({"error": "Thread not found."}), 404

    thread = threads[thread_id]['thread']

    try:
        assistant = client.beta.assistants.retrieve("asst_Wk1Ue0iDYkhbdiXXDPPJsvAV")
        logging.debug(f"Retrieved assistant with ID '{assistant.id}'")

        # Create a message in the existing thread
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=question
        )
        logging.debug(f"Created user message with ID '{message.id}' in thread '{thread.id}'")

        # Run the assistant
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id
        )
        logging.debug(f"Assistant run created with ID '{run.id}'")

        # Poll for the run to complete and handle tool calls
        while True:
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            logging.debug(f"Run '{run.id}' status: '{run.status}'")

            

            if run.status == 'completed':
                # Get the assistant's response
                messages = client.beta.threads.messages.list(thread_id=thread.id)
                assistant_reply = messages.data[0].content[0].text.value
                logging.info(f"Assistant reply: {assistant_reply}")
                return jsonify({"response": assistant_reply}), 200

            elif run.status == 'requires_action':
                # Handle tool calls
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                tool_outputs = []
                logging.debug(f"Handle {len(tool_calls)} tool calls")

                for tool_call in tool_calls:
                    if tool_call.function.name == "ir_stuff":
                        # Parse arguments
                        try:
                            args = json.loads(tool_call.function.arguments)
                        except json.JSONDecodeError as json_err:
                            logging.error(f"JSON decoding error: {json_err}")
                            tool_outputs.append({
                                "tool_call_id": tool_call.id,
                                "output": json.dumps({"error": "Invalid JSON arguments"})
                            })
                            continue

                        filename = args.get("filename")
                        k = args.get("k", 5)

                        # Ensure K is an integer
                        try:
                            k = int(k)
                            if k <= 0:
                                raise ValueError("K must be a positive integer.")
                        except (ValueError, TypeError) as ve:
                            logging.error(f"Invalid K value: {ve}")
                            tool_outputs.append({
                                "tool_call_id": tool_call.id,
                                "output": json.dumps({"error": "Invalid value for K. It must be a positive integer."})
                            })
                            continue

                        logging.debug(f"Calling ir_stuff with filename='{filename}' and K={k}")

                        # Call ir_stuff function
                        response, status_code = ir_stuff(filename, k)
                        if status_code == 200:
                            tool_outputs.append({
                                "tool_call_id": tool_call.id,
                                "output": json.dumps(response.json)
                            })
                            logging.debug(f"ir_stuff output: {response.json}")
                        else:
                            tool_outputs.append({
                                "tool_call_id": tool_call.id,
                                "output": json.dumps({"error": "Failed to find similar documents"})
                            })
                            logging.error(f"ir_stuff failed for filename='{filename}' with status_code={status_code}")

                # Submit tool outputs back to the assistant
                run = client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )
                logging.debug(f"Submitted tool outputs for run '{run.id}'")
                continue

            elif run.status == 'failed':
                logging.error(f"Assistant run '{run.id}' failed.")
                return jsonify({"error": "Assistant run failed"}), 500

            time.sleep(1)  # Wait before polling again

    except OpenAIError as e:
        logging.error(f"OpenAI Error: {str(e)}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logging.exception("An unexpected error occurred in ask_question")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5500, debug=True)  # Added debug=True for more detailed logs
