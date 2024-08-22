from flask import Flask, render_template, request, jsonify, session
from langchain_google_genai import GoogleGenerativeAI
import secrets
import os

secret_key = secrets.token_hex(16)
app = Flask(__name__)
app.secret_key = secret_key  # Necessary for session management

api_key = os.getenv('GOOGLE_API_KEY')

def chatbot(user_input):
    # Call the Google GenAI API
    llm = GoogleGenerativeAI(model="gemini-pro", google_api_key=api_key)
    ai_response = llm.invoke(user_input)  # Directly use user input as prompt
    return ai_response

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask_ai():
    user_input = request.json.get('message')
    
    if not user_input:
        return jsonify({'error': 'No message provided'}), 400

    ai_response = chatbot(user_input)
    return jsonify({'response': ai_response})

if __name__ == '__main__':
    app.run(debug=True)
