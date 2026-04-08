import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Explicitly set template and static folders for Vercel
app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Configure Gemini API
API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

# Initialize the model
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    print(f"Error: {e}")
    model = None

chat_sessions = {}

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

        if not API_KEY:
             return jsonify({"error": "API Key is missing."}), 500

        if session_id not in chat_sessions:
            chat_sessions[session_id] = model.start_chat(history=[
                 {"role": "user", "parts": ["You are Aura, a futuristic AI assistant. Be helpful and professional."]},
                 {"role": "model", "parts": ["Understood. I am Aura."]}
            ])
        
        chat_session = chat_sessions[session_id]
        response = chat_session.send_message(user_message)
        
        return jsonify({"reply": response.text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Required for Vercel
app.debug = False
if __name__ == '__main__':
    app.run()
