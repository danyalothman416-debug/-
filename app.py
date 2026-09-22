from flask import Flask, render_template, request, jsonify
import base64
import os
import time

# دروستکردنی فۆڵدەرێک بۆ هەڵگرتنی سناپەکان ئەگەر بوونی نەبێت
if not os.path.exists('snaps'):
    os.makedirs('snaps')

app = Flask(__name__, template_folder='.')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/send_snap', methods=['POST'])
def send_snap():
    data = request.get_json()
    if 'image' in data:
        # جیاکردنەوەی کۆدی وێنەکە
        image_data = data['image'].split(',')[1]
        
        # دروستکردنی ناوێکی ناوازە بۆ وێنەکە بەپێی کات
        filename = f"snaps/snap_{int(time.time())}.jpg"
        
        # پاشەکەوتکردنی وێنەکە
        with open(filename, "wb") as fh:
            fh.write(base64.b64decode(image_data))
            
        return jsonify({'status': 'success', 'message': 'سناپەکە بە سەرکەوتوویی نێردرا! 👻'})
    return jsonify({'status': 'error', 'message': 'هیچ وێنەیەک نەدۆزرایەوە'})

if __name__ == '__main__':
    print("🚀 سێرڤەرەکە ئامادەیە لەسەر لینکی: http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
