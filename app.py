import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from google import genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Use the API key from environment variable explicitly
def get_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None
    return genai.Client(api_key=api_key)

# Dictionary to store chat sessions
chat_sessions = {}

def get_chat_response(message, session_id):
    try:
        client = get_client()
        if not client:
            return None, "GEMINI_API_KEY is missing in environment variables"

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
            return None, "AI returned an empty response"
            
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
        if not data:
            return jsonify({"reply": "Invalid request format"}), 400
            
        user_message = data.get('message')
        session_id = data.get('session_id', 'default')

        if not user_message:
            return jsonify({"reply": "Message is required"}), 400

        reply, error = get_chat_response(user_message, session_id)
        
        if reply:
            return jsonify({"reply": reply})
        else:
            # Send the specific error back to UI for debugging
            return jsonify({"reply": f"⚠️ Aura Error: {error}. Check Vercel Environment Variables."}), 500

    except Exception as e:
        return jsonify({"reply": f"Global Error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
