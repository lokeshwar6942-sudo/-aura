import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from genai import Client
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

# Dictionary to store chat sessions (Simplified for new SDK)
chat_histories = {}

def get_chat_response(message, session_id):
    if not API_KEYS:
        return None, "No API keys configured in .env or Vercel Settings"
    
    last_error = "Unknown error"
    
    # Try each API key until one works
    for key in API_KEYS:
        try:
            client = Client(api_key=key)
            
            # Initialize history if new session
            if session_id not in chat_histories:
                chat_histories[session_id] = [
                    {"role": "user", "content": "You are Aura, an elite AI assistant. Be professional, helpful, and concise."},
                    {"role": "model", "content": "Understood. I am Aura, your elite AI assistant. How can I help you today?"}
                ]
            
            # Add current message to history
            chat_histories[session_id].append({"role": "user", "content": message})
            
            # Get response using gemini-1.5-flash
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=chat_histories[session_id]
            )
            
            ai_reply = response.text
            # Save AI response to history
            chat_histories[session_id].append({"role": "model", "content": ai_reply})
            
            return ai_reply, None
            
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
