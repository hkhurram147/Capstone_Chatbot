from flask import Flask, request, jsonify
from openai import OpenAI
from VidhanStuff import gdrive
import os
import glob
import shutil

def move_file_to_folder(file_path, destination_folder):
    # Check if the destination folder exists, if not, create it
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    
    # Get the file name from the file path
    file_name = os.path.basename(file_path)
    
    # Create the destination path
    destination_path = os.path.join(destination_folder, file_name)
    
    # Move the file to the destination folder
    shutil.move(file_path, destination_path)
    print(f"Moved file: {file_path} to {destination_path}")
def delete_folder(folder_path):
    # Check if the folder exists
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        shutil.rmtree(folder_path)
        return 1
    else:
        return 0

# Initialize the Flask app
app = Flask(__name__)

client = OpenAI()

@app.route('/uploadFile', methods=['POST'])
def upload_file():
    data=request.json
    filename=data.get('filename')
    filepath='RitvikStuff/OpenAiKnowledgeBase'
    downloadRes = gdrive.DownloadMostRecentFile(filepath)

    if downloadRes == 0:
        return jsonify({"error": "File download error"}), 500

    
    try:
        files=glob.glob(filepath)
        if not files:
            return jsonify({"error": "File is required"}), 400
        
        most_recent_file = max(files, key=os.path.getmtime)
        # Retrieve specific assistant
        
        got_file_name = os.path.basename(most_recent_file)

        if got_file_name != filename:
            return jsonify({"error": "Wrong File error"}), 500
        
        if most_recent_file:
            move_file_to_folder(most_recent_file, 'RitvikStuff/consumeFile')
        assistant = client.beta.assistants.retrieve("asst_MptmDGLUuHUQf9dEvfsFfWg3")

        # Ready the files for upload to OpenAI
        file_paths = ['RitvikStuff/consumeFile']
        file_streams = [open(path, "rb") for path in file_paths]
        print(file_streams)

        # Use the upload and poll SDK helper to upload the files, add them to the vector store,
        # and poll the status of the file batch for completion.
        file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id='vs_2JCZBWOGWZXPiiyb3zHhYJwf', files=file_streams
        )

        # You can print the status and the file counts of the batch to see the result of this operation.
        print(file_batch.status)
        print(file_batch.file_counts)

        res=delete_folder('RitvikStuff/consumeFile')
        if res==0:
            return jsonify({"error": "File Cleanup error"}), 500
        
        return jsonify({"response": "File uploaded successfully"}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    


    


    

@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.json
    print("hello")
    question = data.get('question')

    if not question:
        return jsonify({"error": "Question is required"}), 400

    try:
        
        # Retrieve specific assistant
        assistant = client.beta.assistants.retrieve("asst_MptmDGLUuHUQf9dEvfsFfWg3")

        # Create a thread
        thread = client.beta.threads.create()

        # Create a message
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=question
        )

        # Create and poll the run
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant.id,
            instructions="Only use information from the files provided to you through file search tool"
        )

        messages = client.beta.threads.messages.list(thread_id=thread.id)
        # make message obejct into string
        messages = str(messages)
        # Return the response
        return jsonify({"response": messages}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5500)
