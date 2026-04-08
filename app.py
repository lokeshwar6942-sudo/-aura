import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Multiple API Keys support (Failover logic)
API_KEYS = [
    os.environ.get("GEMINI_API_KEY"),
    os.environ.get("GEMINI_API_KEY_2")
]
# Clean None values
API_KEYS = [k.strip() for k in API_KEYS if k]

def get_chat_response(message, session_id):
    last_error = "No API keys configured"
    
    for key in API_KEYS:
        try:
            genai.configure(api_key=key)
            # Using gemini-pro for maximum stability
            model = genai.GenerativeModel('gemini-pro')
            
            # Start or continue chat
            chat = model.start_chat(history=[
                 {"role": "user", "parts": ["You are Aura, an elite AI assistant. Be professional and helpful."]},
                 {"role": "model", "parts": ["Understood. I am Aura, your AI assistant."]}
            ])
            
            response = chat.send_message(message)
            return response.text, None
        except Exception as e:
            last_error = str(e)
            print(f"Key failed, trying next... Error: {e}")
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
