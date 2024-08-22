from flask import Flask, render_template, request, jsonify, session
from langchain_google_genai import GoogleGenerativeAI
import secrets
import os
from dotenv import load_dotenv

load_dotenv()

secret_key = secrets.token_hex(16)
app = Flask(__name__)
app.secret_key = secret_key  # Necessary for session management

api_key = os.getenv('GOOGLE_API_KEY')

# Initialize conversation history
conversation_history = {}

def chatbot(user_input, session_id):
    if session_id not in conversation_history:
        conversation_history[session_id] = []

    # Append the new user input to the conversation history
    conversation_history[session_id].append(f"User: {user_input}")

    # Build the prompt with the conversation history
    prompt = "\n".join(conversation_history[session_id])

    # Call the Google GenAI API
    llm = GoogleGenerativeAI(model="gemini-pro", google_api_key=api_key)
    ai_response = llm.invoke(prompt)

    # Append the AI's response to the conversation history
    conversation_history[session_id].append(f"Bot: {ai_response}")

    return ai_response

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new_conversation', methods=['POST'])
def new_conversation():
    conversation_id = secrets.token_hex(16)
    session['conversation_id'] = conversation_id
    return jsonify({'conversation_id': conversation_id})

@app.route('/ask', methods=['POST'])
def ask_ai():
    user_input = request.json.get('message')
    conversation_id = request.json.get('conversation_id')
    
    if not conversation_id:
        return jsonify({'error': 'No conversation ID provided'}), 400

    ai_response = chatbot(user_input, conversation_id)
    return jsonify({'response': ai_response})

@app.route('/reset', methods=['POST'])
def reset():
    conversation_id = session.get('conversation_id')
    if conversation_id in conversation_history:
        del conversation_history[conversation_id]

    return jsonify({'response': 'Conversation history cleared.'})

if __name__ == '__main__':
    app.run(debug=True)
