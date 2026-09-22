from flask import Flask, render_template, request, jsonify
import datetime
import json
import os

app = Flask(__name__)

# ناوی فایلی پاشەکەوتکردنی نامەکان
MESSAGES_FILE = 'messages.json'

# فەنکشن بۆ خوێندنەوەی نامەکان لە فایلەکە
def load_messages():
    if os.path.exists(MESSAGES_FILE):
        try:
            with open(MESSAGES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

# فەنکشن بۆ پاشەکەوتکردنی نامەکان لە فایلەکە
def save_messages(messages):
    with open(MESSAGES_FILE, 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False, indent=4)

# ڕێگەی سەرەکی (ماڵپەڕەکە)
@app.route('/')
def home():
    return render_template('index.html')

# ڕێگە بۆ وەرگرتنی نامە نوێیەکان
@app.route('/send', methods=['POST'])
def send():
    data = request.get_json()
    username = data.get('username', 'نەناسراو')
    message = data.get('message')
    
    if message:
        # وەرگرتنی کاتی ئێستا
        time_now = datetime.datetime.now().strftime("%H:%M")
        
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

# ڕێگە بۆ ناردنی نامەکان بۆ وێبگەڕەکە
@app.route('/get_messages')
def get_messages():
    return jsonify(load_messages())

# ڕێگە بۆ سڕینەوەی نامەکان
@app.route('/clear_messages', methods=['POST'])
def clear_messages():
    save_messages([]) # پاشەکەوتکردنی لیستێکی بەتاڵ
    return jsonify({'status': 'cleared'})

if __name__ == '__main__':
    app.run(debug=True)
