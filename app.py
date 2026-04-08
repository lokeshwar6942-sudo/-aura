import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

# Explicitly set template and static folders for Vercel
app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Configure Gemini API from Environment Variables (Vercel settings)
API_KEY = os.environ.get("GEMINI_API_KEY")

if API_KEY:
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        model = None
        print(f"Gemini Init Error: {e}")
else:
    model = None
    print("API_KEY not found in environment variables")

chat_sessions = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    if not model:
        return jsonify({"reply": "⚠️ AI System Offline: API Key missing or invalid in Vercel settings."}), 500

    try:
        data = request.json
        user_message = data.get('message')
        session_id = data.get('session_id', 'default')

        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        if session_id not in chat_sessions:
            chat_sessions[session_id] = model.start_chat(history=[
                 {"role": "user", "parts": ["You are Aura, an elite, professional, and friendly AI Customer Support Assistant for a premium website. Provide clear, concise, and highly helpful answers."]},
                 {"role": "model", "parts": ["Understood. I am Aura, your elite AI support assistant."]}
            ])
        
        chat_session = chat_sessions[session_id]
        response = chat_session.send_message(user_message)
        
        return jsonify({"reply": response.text})

    except Exception as e:
        print(f"Chat Error: {e}")
        return jsonify({"reply": "I'm having trouble connecting to my brain right now. Please try again later."}), 500

# For local testing if needed
if __name__ == '__main__':
    app.run(debug=True)
