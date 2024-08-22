from flask import Flask, render_template, request, jsonify, session
from langchain_google_genai import GoogleGenerativeAI
import sqlite3
import secrets
secret_key = secrets.token_hex(16)
app = Flask(__name__)
app.secret_key = secret_key  # Necessary for session management
import os
from dotenv import load_dotenv

api_key = os.getenv('GOOGLE_API_KEY')

load_dotenv()


# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('chatbot.db')
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS conversation_history (
        session_id TEXT,
        message TEXT
    )
    ''')
    conn.commit()
    conn.close()

init_db()

def chatbot(user_input, session_id):
    conn = sqlite3.connect('chatbot.db')
    c = conn.cursor()

    # Retrieve conversation history from the database
    c.execute("SELECT message FROM conversation_history WHERE session_id = ?", (session_id,))
    rows = c.fetchall()
    conversation_history = [row[0] for row in rows]

    # Append the new user input to the conversation history
    conversation_history.append(f"User: {user_input}")

    # Build the prompt with the conversation history
    prompt = "\n".join(conversation_history)

    # Call the Google GenAI API
    llm = GoogleGenerativeAI(model="gemini-pro", google_api_key=api_key)
    ai_response = llm.invoke(prompt)

    # Append the AI's response to the conversation history
    conversation_history.append(f"Bot: {ai_response}")

    # Save the updated conversation history back to the database
    for message in conversation_history[-2:]:
        c.execute("INSERT INTO conversation_history (session_id, message) VALUES (?, ?)", (session_id, message))
    conn.commit()
    conn.close()

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
    session_id = session.sid
    conn = sqlite3.connect('chatbot.db')
    c = conn.cursor()
    c.execute("DELETE FROM conversation_history WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()

    return jsonify({'response': 'Conversation history cleared.'})

if __name__ == '__main__':
    app.run(debug=True)
