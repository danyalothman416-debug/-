from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import json
import os
import datetime

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*") # چالاککردنی SocketIO

USERS_FILE = 'users.json'
MESSAGES_FILE = 'messages.json'

# --- فەنکشنەکانی یاریدەدەر ---
def load_data(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_data(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- ڕێگاکانی ماڵپەڕەکە ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    users = load_data(USERS_FILE)
    if username in users and users[username]['password'] == password:
        return jsonify({'status': 'success', 'user': users[username]})
    return jsonify({'status': 'error', 'message': 'ناوی بەکارهێنەر یان وشەی نهێنی هەڵەیە.'})

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    users = load_data(USERS_FILE)
    if username in users:
        return jsonify({'status': 'error', 'message': 'ئەم ناوە پێشتر بەکارهێنراوە.'})
    users[username] = {
        'username': username,
        'password': password,
        'bio': 'بەخێربێن بۆ پرۆفایلی من!',
        'avatar': '😎'
    }
    save_data(USERS_FILE, users)
    return jsonify({'status': 'success', 'user': users[username]})

@app.route('/api/update_profile', methods=['POST'])
def update_profile():
    data = request.get_json()
    username = data.get('username')
    bio = data.get('bio')
    avatar = data.get('avatar')
    users = load_data(USERS_FILE)
    if username in users:
        users[username]['bio'] = bio
        users[username]['avatar'] = avatar
        save_data(USERS_FILE, users)
        return jsonify({'status': 'success', 'user': users[username]})
    return jsonify({'status': 'error'})

# --- بەشی Socket.IO بۆ چاتی خێرا ---
@socketio.on('send_message')
def handle_send_message(data):
    username = data.get('username')
    avatar = data.get('avatar')
    message = data.get('message')
    
    if message:
        messages = load_data(MESSAGES_FILE)
        if not isinstance(messages, list): messages = []
        
        time_now = datetime.datetime.now().strftime("%H:%M")
        
        msg_data = {
            'username': username,
            'avatar': avatar,
            'message': message,
            'time': time_now
        }
        
        messages.append(msg_data)
        save_data(MESSAGES_FILE, messages)
        
        # ناردنی نامەکە بۆ هەموو ئەو کەسانەی کە پەیوەستن
        emit('new_message', msg_data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True) # بەکارهێنانی socketio لە جیاتی app
