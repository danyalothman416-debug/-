from flask import Flask, render_template, request, jsonify
import datetime
import json
import os

app = Flask(__name__)

# فایلی پاشەکەوتکردنی نامەکان
MESSAGES_FILE = 'messages.json'

def load_messages():
    if os.path.exists(MESSAGES_FILE):
        with open(MESSAGES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_messages(messages):
    with open(MESSAGES_FILE, 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False, indent=4)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/send', methods=['POST'])
def send():
    data = request.get_json()
    username = data.get('username')
    message = data.get('message')
    
    if message:
        time_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_message = {
            'username': username,
            'message': message,
            'time': time_now
        }
        messages = load_messages()
        messages.append(new_message)
        save_messages(messages)
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error'})

@app.route('/get_messages')
def get_messages():
    return jsonify(load_messages())

if __name__ == '__main__':
    app.run(debug=True)
