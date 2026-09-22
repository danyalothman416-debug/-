<!DOCTYPE html>
<html lang="ku" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>چاتی دانیال</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f0f2f5; display: flex; justify-content: center; padding: 20px; margin: 0; }
        .chat-container { width: 400px; background: white; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.2); overflow: hidden; display: flex; flex-direction: column; height: 80vh; }
        .header { background: #fffc00; color: black; padding: 15px; text-align: center; font-weight: bold; font-size: 18px; }
        .messages { flex: 1; padding: 15px; overflow-y: auto; background: #fafafa; display: flex; flex-direction: column; gap: 10px; }
        .message-box { display: flex; flex-direction: column; max-width: 80%; align-self: flex-start; background: #e4e6eb; padding: 10px; border-radius: 10px; }
        .message-info { display: flex; justify-content: space-between; font-size: 10px; color: #555; margin-bottom: 5px; gap: 10px; }
        .message-text { font-size: 14px; word-wrap: break-word; }
        .input-area { display: flex; padding: 10px; border-top: 1px solid #ddd; background: white; }
        input { flex: 1; padding: 12px; border: 1px solid #ccc; border-radius: 25px; outline: none; }
        button { background: #fffc00; border: none; padding: 12px 20px; border-radius: 25px; margin-right: 10px; cursor: pointer; font-weight: bold; }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="header">چاتی دانیال</div>
        <div class="messages" id="messages-container">
            <!-- نامەکان لێرەدا دەردەکەون -->
        </div>
        <div class="input-area">
            <input type="text" placeholder="نامەیەک بنووسە..." id="message-input">
            <button>ناردن</button>
        </div>
    </div>

    <script>
        // ١. دۆزینەوەی بەشەکانی ڕووکارەکە
        const input = document.getElementById('message-input');
        const button = document.querySelector('button');
        const messagesDiv = document.getElementById('messages-container');
        
        // ٢. پرسیارکردن لە بەکارهێنەر بۆ ناوی خۆی
        let username = prompt("تکایە ناوی خۆت بنووسە:");
        if (!username || username.trim() === "") {
            username = "نەناسراو";
        }

        // ٣. چالاککردنی دوگمە و دوگمەی Enter
        button.addEventListener('click', sendMessage);
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') sendMessage();
        });

        // ٤. فەنکشنی ناردنی نامە بۆ ڕاژەکارەکە
        function sendMessage() {
            const text = input.value.trim();
            if (!text) return;

            fetch('/send', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username: username, message: text})
            })
            .then(response => response.json())
            .then(data => {
                input.value = ''; // پاککردنەوەی خانەکە
                loadMessages(); // نوێکردنەوەی لیستەکە
            });
        }

        // ٥. فەنکشنی وەرگرتنی نامەکان لە ڕاژەکارەکە
        function loadMessages() {
            fetch('/get_messages')
            .then(response => response.json())
            .then(data => {
                messagesDiv.innerHTML = ''; // پاککردنەوەی لیستەکە
                
                if (data.length === 0) {
                    messagesDiv.innerHTML = '<div class="message-box"><div class="message-text">سیستەم: بەخێربێن بۆ چاتەکە!</div></div>';
                }

                data.forEach(msg => {
                    const bubble = document.createElement('div');
                    bubble.className = 'message-box';
                    
                    const user = msg.username || "نەناسراو";
                    const time = msg.time || "";
                    const text = msg.message || msg;

                    bubble.innerHTML = `
                        <div class="message-info">
                            <b>${user}</b>
                            <span>${time}</span>
                        </div>
                        <div class="message-text">${text}</div>
                    `;
                    messagesDiv.appendChild(bubble);
                });
                messagesDiv.scrollTop = messagesDiv.scrollHeight; // بڕۆ بۆ خوارەوە
            });
        }

        // ٦. هەر ٢ چرکە جارێک نامەکان نوێ دەکاتەوە
        setInterval(loadMessages, 2000);
        loadMessages(); // بانگکردنی یەکەم جار
    </script>
</body>
</html>
