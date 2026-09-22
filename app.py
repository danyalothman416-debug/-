<!DOCTYPE html>
<html lang="ku" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>چاتی دانیال</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f0f2f5; display: flex; justify-content: center; padding: 20px; margin: 0; }
        .chat-container { width: 400px; background: white; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.2); overflow: hidden; display: flex; flex-direction: column; height: 80vh; }
        .header { background: #fffc00; color: black; padding: 15px; text-align: center; font-weight: bold; font-size: 18px; }
        .messages { flex: 1; padding: 15px; overflow-y: auto; background: #fafafa; }
        .message { margin-bottom: 10px; padding: 10px; border-radius: 10px; background: #e4e6eb; display: inline-block; }
        .input-area { display: flex; padding: 10px; border-top: 1px solid #ddd; background: white; }
        input { flex: 1; padding: 12px; border: 1px solid #ccc; border-radius: 25px; outline: none; }
        button { background: #fffc00; border: none; padding: 12px 20px; border-radius: 25px; margin-right: 10px; cursor: pointer; font-weight: bold; }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="header">چاتی دانیال</div>
        <div class="messages" id="messages-container">
            <div class="message">سیستەم: بەخێربێن بۆ چاتەکە!</div>
        </div>
        <div class="input-area">
            <input type="text" placeholder="نامەیەک بنووسە..." id="message-input">
            <button>ناردن</button>
        </div>
    </div>

    <script>
        const input = document.getElementById('message-input');
        const button = document.querySelector('button');
        const messagesDiv = document.getElementById('messages-container');

        button.addEventListener('click', sendMessage);
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') sendMessage();
        });

        function sendMessage() {
            const text = input.value.trim();
            if (!text) return;

            fetch('/send', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: text})
            })
            .then(response => response.json())
            .then(data => {
                input.value = '';
                loadMessages();
            });
        }

        function loadMessages() {
            fetch('/get_messages')
            .then(response => response.json())
            .then(data => {
                messagesDiv.innerHTML = '<div class="message">سیستەم: بەخێربێن بۆ چاتەکە!</div>';
                data.forEach(msg => {
                    messagesDiv.innerHTML += '<div class="message">' + msg + '</div>';
                });
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            });
        }

        setInterval(loadMessages, 2000);
    </script>
</body>
</html>
