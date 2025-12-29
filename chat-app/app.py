from flask import Flask, render_template, request, jsonify, session
import requests
import os
from dotenv import load_dotenv
import uuid

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Changed to localhost since all services run in same container
BACKEND_API_URL = os.getenv('BACKEND_API_URL', 'http://localhost:8000')

@app.route('/')
def index():
    # Initialize session for conversation history
    if 'conversation_id' not in session:
        session['conversation_id'] = str(uuid.uuid4())
    if 'messages' not in session:
        session['messages'] = []
    
    return render_template('chat.html')

@app.route('/api/send', methods=['POST'])
def send_message():
    try:
        data = request.json
        user_message = data.get('message', '')
        use_mcp = data.get('use_mcp', False)
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Get or initialize conversation history
        if 'messages' not in session:
            session['messages'] = []
        
        # Add user message to history
        session['messages'].append({
            'role': 'user',
            'content': user_message
        })
        
        # Call backend API
        response = requests.post(
            f'{BACKEND_API_URL}/api/chat',
            json={
                'messages': session['messages'],
                'use_mcp': use_mcp
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Add assistant response to history
            session['messages'].append({
                'role': 'assistant',
                'content': result['content']
            })
            
            session.modified = True
            
            return jsonify({
                'response': result['content'],
                'model': result['model'],
                'finish_reason': result['finish_reason']
            })
        else:
            return jsonify({'error': 'Backend API error'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear', methods=['POST'])
def clear_conversation():
    """Clear conversation history"""
    session['messages'] = []
    session.modified = True
    return jsonify({'status': 'cleared'})

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get conversation history"""
    return jsonify({'messages': session.get('messages', [])})

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)