from flask import Flask, request, jsonify
from openai import OpenAI

# Initialize the Flask app
app = Flask(__name__)

client = OpenAI()

@app.route('/uploadFle', methods=['POST'])
def upload_file():
    data = request.json
    print("hello")
    fileName = data.get('fileName')
    folderName = data.get('folderName')

    if not fileName or not folderName:
        return jsonify({"error": "File is required"}), 400
    
    try:
        # Retrieve specific assistant
        DownloadedfileName = "SMBP.pdf"
        assistant = client.beta.assistants.retrieve("asst_MptmDGLUuHUQf9dEvfsFfWg3")

        # Ready the files for upload to OpenAI
        file_paths = ["./" + DownloadedfileName]
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
