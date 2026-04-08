import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Configure Gemini API from Environment Variables
API_KEY = os.environ.get("GEMINI_API_KEY")

def init_gemini():
    if not API_KEY:
        return None, "API_KEY not found in Vercel settings"
    try:
        genai.configure(api_key=API_KEY.strip())
        return genai.GenerativeModel('gemini-1.5-flash'), None
    except Exception as e:
        return None, str(e)

chat_sessions = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    model, error_msg = init_gemini()
    if not model:
        return jsonify({"reply": f"⚠️ AI Offline: {error_msg}"}), 500

    try:
        data = request.json
        user_message = data.get('message')
        session_id = data.get('session_id', 'default')

        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        if session_id not in chat_sessions:
            chat_sessions[session_id] = model.start_chat(history=[
                 {"role": "user", "parts": ["You are Aura, an elite, professional, and friendly AI Customer Support Assistant. Provide helpful and concise answers."]},
                 {"role": "model", "parts": ["Understood. I am Aura, your AI assistant."]}
            ])
        
        chat_session = chat_sessions[session_id]
        response = chat_session.send_message(user_message)
        
        return jsonify({"reply": response.text})

    except Exception as e:
        return jsonify({"reply": f"Brain Error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
