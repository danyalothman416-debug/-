from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

USERS_FILE = 'users.json'
MESSAGES_FILE = 'messages.json'

# --- فەنکشنەکانی یاریدەدەر بۆ خوێندنەوە و پاشەکەوتکردن ---
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

# ١. سیستەمی لۆگین
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    users = load_data(USERS_FILE)
    
    if username in users and users[username]['password'] == password:
        return jsonify({'status': 'success', 'user': users[username]})
    return jsonify({'status': 'error', 'message': 'ناوی بەکارهێنەر یان وشەی نهێنی هەڵەیە.'})

# ٢. سیستەمی تۆمارکردن (خۆ تۆمارکردن)
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

# ٣. نوێکردنەوەی پرۆفایل
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

# ٤. ناردنی نامە
@app.route('/api/send', methods=['POST'])
def send_message():
    data = request.get_json()
    username = data.get('username')
    avatar = data.get('avatar')
    message = data.get('message')
    
    if message:
        messages = load_data(MESSAGES_FILE)
        if not isinstance(messages, list): messages = []
        
        messages.append({
            'username': username,
            'avatar': avatar,
            'message': message
        })
        save_data(MESSAGES_FILE, messages)
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error'})

# ٥. وەرگرتنی نامەکان
@app.route('/api/messages')
def get_messages():
    messages = load_data(MESSAGES_FILE)
    if not isinstance(messages, list): messages = []
    return jsonify(messages)

if __name__ == '__main__':
    app.run(debug=True)
