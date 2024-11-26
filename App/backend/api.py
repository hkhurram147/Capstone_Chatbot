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
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    # Check if a file was uploaded
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Check if the file is a PDF
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "Only PDF files are allowed"}), 400

    # Sanitize filename
    sanitized_filename = sanitize_filename(file.filename)
    temp_path = os.path.join(UPLOAD_FOLDER, sanitized_filename)
    


    try:

        # Save the uploaded file temporarily
        file.save(temp_path)

        with open(temp_path, "rb") as f:
            file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
                vector_store_id='vs_qUspcB7VllWXM4z7aAEdIK9L', files=[f]
            )

        # Check upload status
        if file_batch.status != "completed":
            return jsonify({"error": "File upload to vector store failed"}), 500


        # **Proceed with embedding extraction and storage**

        # Extract text from PDF using pdfplumber
        with pdfplumber.open(temp_path) as pdf:
            pages = pdf.pages
            text = '\n'.join([page.extract_text() for page in pages if page.extract_text()])

        if not text:
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

        # Clean up the temporary file after processing
        os.remove(temp_path)

        # **Final Response after all processing is done**
        return jsonify({"response": "File uploaded and embeddings stored successfully."}), 200

    except OpenAIError as e:
        return jsonify({"error": f"OpenAI Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def ir_stuff(filename, K):
    """
    Find similar documents using pre-computed embeddings from embeddings.json

    Parameters:
    - filename: the file name of the query document in the format "Category\\DocumentName.pdf"
    - K: optional, the number of similar documents to return (default is 5)
    """
    try:

        # Define paths
        TEMP2_DIR = 'temp2'
        EMBEDDINGS_FILE = os.path.join(TEMP2_DIR, 'embeddings.json')

        # Load pre-computed embeddings
        if not os.path.exists(EMBEDDINGS_FILE):
            return jsonify({"error": "Embeddings file not found"}), 404

        with open(EMBEDDINGS_FILE, 'r') as f:
            all_embeddings = json.load(f)

        # Find the query document embedding from embeddings.json
        query_embedding = None
        for doc in all_embeddings:
            if doc['metadata']["title"] == filename:
                query_embedding = np.array(doc['embedding'])
                break

        if query_embedding is None:
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


        # Sort by similarity in descending order
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        top_similar = similarities[:K]

        # Return top K most similar documents
        return jsonify(top_similar), 200

    except Exception as e:
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
        return jsonify({"error": "Question and Thread ID are required."}), 400
    if thread_id not in threads:
        return jsonify({"error": "Thread not found."}), 404

    thread = threads[thread_id]['thread']

    try:
        assistant = client.beta.assistants.retrieve("asst_Wk1Ue0iDYkhbdiXXDPPJsvAV")

        # Create a message in the existing thread
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=question
        )

        # Run the assistant
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id
        )

        # Poll for the run to complete and handle tool calls
        while True:
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )

            

            if run.status == 'completed':
                # Get the assistant's response
                messages = client.beta.threads.messages.list(thread_id=thread.id)
                assistant_reply = messages.data[0].content[0].text.value
                return jsonify({"response": assistant_reply}), 200

            elif run.status == 'requires_action':
                # Handle tool calls
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                tool_outputs = []

                for tool_call in tool_calls:
                    if tool_call.function.name == "ir_stuff":
                        # Parse arguments
                        try:
                            args = json.loads(tool_call.function.arguments)
                        except json.JSONDecodeError as json_err:
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
                            tool_outputs.append({
                                "tool_call_id": tool_call.id,
                                "output": json.dumps({"error": "Invalid value for K. It must be a positive integer."})
                            })
                            continue


                        # Call ir_stuff function
                        response, status_code = ir_stuff(filename, k)
                        if status_code == 200:
                            tool_outputs.append({
                                "tool_call_id": tool_call.id,
                                "output": json.dumps(response.json)
                            })
                        else:
                            tool_outputs.append({
                                "tool_call_id": tool_call.id,
                                "output": json.dumps({"error": "Failed to find similar documents"})
                            })

                # Submit tool outputs back to the assistant
                run = client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )
                continue

            elif run.status == 'failed':
                return jsonify({"error": "Assistant run failed"}), 500

            time.sleep(1)  # Wait before polling again

    except OpenAIError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5500, debug=True)  # Added debug=True for more detailed logs
