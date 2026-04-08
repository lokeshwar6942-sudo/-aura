import os
import sys
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from google import genai
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Multiple API Keys support (Failover logic)
API_KEYS = [
    os.environ.get("GEMINI_API_KEY"),
    os.environ.get("GEMINI_API_KEY_2")
]
# Clean None values
API_KEYS = [k.strip() for k in API_KEYS if k and k.strip()]

# Dictionary to store chat sessions
chat_sessions = {}

def get_chat_response(message, session_id):
    if not API_KEYS:
        return None, "No API keys configured in Vercel Settings"
    
    last_error = "Unknown error"
    
    # Try each API key until one works
    for idx, key in enumerate(API_KEYS):
        try:
            client = genai.Client(api_key=key)
            
            # Retrieve or create stateful chat session
            if session_id not in chat_sessions:
                # Start new chat with system instruction
                chat_sessions[session_id] = client.chats.create(
                    model="gemini-1.5-flash",
                    config={"system_instruction": "You are Aura, an elite AI assistant. Be professional, helpful, and concise."}
                )
            
            chat = chat_sessions[session_id]
            response = chat.send_message(message)
            
            if response and response.text:
                return response.text, None
            else:
                last_error = "Empty response from AI"
                
        except Exception as e:
            last_error = f"Key {idx+1} Error: {str(e)}"
            # If a session fails with one key, we might need to recreate it for the next key
            # Clear it so it retries from scratch next time
            if session_id in chat_sessions:
                del chat_sessions[session_id]
            continue
            
    return None, last_error

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
            return jsonify({"reply": f"⚠️ System Overload: {error}. Please try again in a moment."}), 500

    except Exception as e:
        return jsonify({"reply": f"Global Error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
