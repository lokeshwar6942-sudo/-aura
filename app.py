import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from google import genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Initialize client (will automatically use GEMINI_API_KEY from env)
client = genai.Client()

# Dictionary to store chat sessions
chat_sessions = {}

def get_chat_response(message, session_id):
    try:
        # Retrieve or create stateful chat session
        if session_id not in chat_sessions:
            chat_sessions[session_id] = client.chats.create(
                model="gemini-1.5-flash",
                config={"system_instruction": "You are Aura, an elite AI assistant. Be professional, helpful, and concise."}
            )
        
        chat = chat_sessions[session_id]
        response = chat.send_message(message)
        
        if response and response.text:
            return response.text, None
        else:
            return None, "Empty response from AI"
            
    except Exception as e:
        # If session fails, clear it to retry fresh next time
        if session_id in chat_sessions:
            del chat_sessions[session_id]
        return None, str(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message')
        session_id = data.get('session_id', 'default')

        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        reply, error = get_chat_response(user_message, session_id)
        
        if reply:
            return jsonify({"reply": reply})
        else:
            # Custom error message for better UX
            return jsonify({"reply": f"⚠️ Aura is resting. Error: {error}. Please try again."}), 500

    except Exception as e:
        return jsonify({"reply": f"Global Error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
