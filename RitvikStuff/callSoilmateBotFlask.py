from flask import Flask, request, jsonify
from openai import OpenAI

# Initialize the Flask app
app = Flask(__name__)

client = OpenAI()

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
