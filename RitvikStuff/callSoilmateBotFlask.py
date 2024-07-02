from flask import Flask, request, jsonify
from openai import OpenAI
import shutil
import glob
from Cloud import gdrive
import os
import yaml
import argparse

def read_yaml(file_path):
    if not os.path.exists(file_path):
        return 0
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def move_file_to_folder(file_path, destination_folder):
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    
    file_name = os.path.basename(file_path)
    destination_path = os.path.join(destination_folder, file_name)
    
    shutil.move(file_path, destination_path)
    print(f"Moved file: {file_path} to {destination_path}")

def delete_folder(folder_path):
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        shutil.rmtree(folder_path)
        return 1
    else:
        return 0

app = Flask(__name__)



@app.route('/uploadFile', methods=['POST'])
def upload_file():
    data = request.json
    filename = data.get('filename')
    filepath = r'OpenAiKnowledgeBase'
    downloadRes = gdrive.DownloadMostRecentFile(filepath)

    if downloadRes == "":
        return jsonify({"error": "File download error"}), 500

    try:
        files = glob.glob(downloadRes)
        if not files:
            return jsonify({"error": "File is required"}), 400
        
        most_recent_file = max(files, key=os.path.getmtime)
        got_file_name = os.path.basename(most_recent_file)
        print(got_file_name)

        if got_file_name != filename:
            return jsonify({"error": "Wrong File error"}), 500
        
        if most_recent_file:
            move_file_to_folder(most_recent_file, r'consumeFile')
        
        assistant = client.beta.assistants.retrieve("asst_MptmDGLUuHUQf9dEvfsFfWg3")

        file_paths = glob.glob(os.path.join('consumeFile', '*'))
        file_streams = [open(path, "rb") for path in file_paths]
        print(file_streams)

        file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id='vs_2JCZBWOGWZXPiiyb3zHhYJwf', files=file_streams
        )

        print(file_batch.status)
        print(file_batch.file_counts)

        for file_stream in file_streams:
            file_stream.close()

        res = delete_folder('consumeFile')
        if res == 0:
            return jsonify({"error": "File Cleanup error"}), 500
        
        return jsonify({"response": "File uploaded successfully"}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.json
    question = data.get('question')

    if not question:
        return jsonify({"error": "Question is required"}), 400

    try:
        assistant = client.beta.assistants.retrieve("asst_MptmDGLUuHUQf9dEvfsFfWg3")
        thread = client.beta.threads.create()
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=question
        )

        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant.id,
            instructions="Only use information from the files provided to you through file search tool"
        )

        messages = client.beta.threads.messages.list(thread_id=thread.id)
        messages_str = str(messages)
        return jsonify({"response": messages_str}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='insert openai-key.')
    parser.add_argument('--get-key', action='store_true', help='get openai API key from config')

    args = parser.parse_args()

    yaml_file_path = 'openai-key.yaml'
    config = read_yaml(yaml_file_path)
    

    if config!=0:
        key = None
        if args.get_key:
            key = config.get('API-key')
            print("API-key is set manually")
        else:
            print("API-key not set")
        client = OpenAI(api_key=key)
    else:
        client=OpenAI()

    app.run(host='0.0.0.0', port=5500)
