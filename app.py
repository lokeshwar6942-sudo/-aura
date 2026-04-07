import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure Gemini API
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY or API_KEY == "your_gemini_api_key_here":
    print("WARNING: Valid GEMINI_API_KEY not found in .env file.")
else:
    genai.configure(api_key=API_KEY)

# Initialize the model using the recommended 'gemini-1.5-flash'
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    print(f"Warning: Model initialization issue: {e}")
    model = None

# Store chat sessions in memory (for simplicity in this prototype)
# In production, use a database (like MongoDB/PostgreSQL)
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

        if not API_KEY or API_KEY == "your_gemini_api_key_here":
             return jsonify({"error": "API Key is missing. Please add your GEMINI_API_KEY in the .env file."}), 500

        # Retrieve or create a chat session with an initial prompt
        if session_id not in chat_sessions:
            chat_sessions[session_id] = model.start_chat(history=[
                 {"role": "user", "parts": ["You are Aura, an elite, professional, and friendly AI Customer Support Assistant for a premium website. Provide clear, concise, and highly helpful answers. Use formatting like bullet points or bold text if helpful. If you don't know the answer, politely admit it."]},
                 {"role": "model", "parts": ["Understood. I am Aura, your elite AI support assistant. I am ready to provide premium, helpful, and concise support."]}
            ])
        
        chat_session = chat_sessions[session_id]

        # Send message to Gemini
        response = chat_session.send_message(user_message)
        
        return jsonify({"reply": response.text})

    except Exception as e:
        print(f"Error handling request: {e}")
        return jsonify({"error": "Failed to get response from AI. Check terminal logs."}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
