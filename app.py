<!DOCTYPE html>
<html lang="ku" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>چاتی دانیال - وەشانی پێشکەوتوو</title>
    <!-- فۆنتی جوان بۆ کوردی -->
    <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;700&display=swap" rel="stylesheet">
    <!-- ئایکۆنەکان -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    
    <style>
        /* ڕێکخستنی گشتی */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Vazirmatn', Tahoma, sans-serif;
        }

        body {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            padding: 20px;
        }

        /* چوارچێوەی چاتەکە */
        .chat-container {
            width: 100%;
            max-width: 500px;
            height: 90vh;
            background: #ffffff;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            position: relative;
        }

        /* سەرەوەی چاتەکە */
        .chat-header {
            background: #fffc00; /* ڕەنگی سناپچات */
            color: #1a1a1a;
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #e6e300;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            z-index: 10;
        }

        .header-info {
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .header-info i {
            font-size: 24px;
            background: #1a1a1a;
            color: #fffc00;
            padding: 8px;
            border-radius: 50%;
        }

        .header-info h2 {
            font-size: 18px;
            font-weight: 700;
        }

        .header-actions button {
            background: transparent;
            border: none;
            font-size: 18px;
            cursor: pointer;
            color: #1a1a1a;
            transition: 0.3s;
        }

        .header-actions button:hover {
            color: #d32f2f;
            transform: scale(1.1);
        }

        /* بەشی نامەکان */
        .chat-messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            background: #fafafa;
            display: flex;
            flex-direction: column;
            gap: 15px;
            scroll-behavior: smooth;
        }

        /* شێوازی بڵۆکی نامە */
        .message-bubble {
            max-width: 80%;
            padding: 12px 16px;
            border-radius: 15px;
            position: relative;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            animation: fadeIn 0.3s ease-in-out;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* نامەی خۆم (لای چەپ بە ڕەنگی زەرد) */
        .my-message {
            align-self: flex-start;
            background: #fffc00;
            color: #1a1a1a;
            border-bottom-right-radius: 2px;
        }

        /* نامەی کەسانی تر (لای ڕاست بە ڕەنگی سپی) */
        .other-message {
            align-self: flex-end;
            background: #ffffff;
            color: #333;
            border: 1px solid #eee;
            border-bottom-left-radius: 2px;
        }

        .message-info {
            display: flex;
            justify-content: space-between;
            font-size: 11px;
            margin-bottom: 5px;
            opacity: 0.7;
            gap: 15px;
        }

        .message-info .username {
            font-weight: 700;
        }

        .message-text {
            font-size: 14px;
            line-height: 1.5;
            word-wrap: break-word;
        }

        /* بەشی نووسین */
        .chat-input {
            display: flex;
            padding: 15px;
            background: #ffffff;
            border-top: 1px solid #eee;
            gap: 10px;
        }

        .chat-input input {
            flex: 1;
            padding: 12px 20px;
            border: 2px solid #eee;
            border-radius: 30px;
            outline: none;
            font-size: 14px;
            transition: 0.3s;
        }

        .chat-input input:focus {
            border-color: #fffc00;
            box-shadow: 0 0 10px rgba(255, 252, 0, 0.3);
        }

        .chat-input button {
            background: #fffc00;
            border: none;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 18px;
            color: #1a1a1a;
            transition: 0.3s;
            box-shadow: 0 4px 10px rgba(255, 252, 0, 0.5);
        }

        .chat-input button:hover {
            background: #e6e300;
            transform: scale(1.1);
        }

        /* سڕۆڵ بار */
        .chat-messages::-webkit-scrollbar {
            width: 6px;
        }
        .chat-messages::-webkit-scrollbar-thumb {
            background: #ccc;
            border-radius: 10px;
        }
    </style>
</head>
<body>

    <div class="chat-container">
        <!-- سەرەوە -->
        <div class="chat-header">
            <div class="header-info">
                <i class="fas fa-ghost"></i>
                <h2>چاتی دانیال</h2>
            </div>
            <div class="header-actions">
                <button id="clear-btn" title="سڕینەوەی چات"><i class="fas fa-trash-alt"></i></button>
            </div>
        </div>

        <!-- نامەکان -->
        <div class="chat-messages" id="messages-container">
            <!-- نامەکان لێرەدا دەردەکەون -->
        </div>

        <!-- نووسین -->
        <div class="chat-input">
            <input type="text" id="message-input" placeholder="نامەیەک بنووسە...">
            <button id="send-btn"><i class="fas fa-paper-plane"></i></button>
        </div>
    </div>

    <script>
        // ١. دۆزینەوەی بەشەکانی ڕووکارەکە
        const input = document.getElementById('message-input');
        const sendBtn = document.getElementById('send-btn');
        const clearBtn = document.getElementById('clear-btn');
        const messagesDiv = document.getElementById('messages-container');
        
        // ٢. پرسیارکردن لە بەکارهێنەر بۆ ناوی خۆی
        let username = prompt("تکایە ناوی خۆت بنووسە:");
        if (!username || username.trim() === "") {
            username = "نەناسراو";
        }

        // ٣. چالاککردنی دوگمەکان
        sendBtn.addEventListener('click', sendMessage);
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') sendMessage();
        });
        clearBtn.addEventListener('click', clearChat);

        // ٤. فەنکشنی ناردنی نامە
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
                input.value = '';
                loadMessages();
            });
        }

        // ٥. فەنکشنی وەرگرتنی نامەکان
        function loadMessages() {
            fetch('/get_messages')
            .then(response => response.json())
            .then(data => {
                messagesDiv.innerHTML = ''; 
                
                if (data.length === 0) {
                    messagesDiv.innerHTML = `
                        <div class="message-bubble other-message">
                            <div class="message-info">
                                <span class="username">سیستەم</span>
                            </div>
                            <div class="message-text">بەخێربێن بۆ چاتەکە! هیچ نامەیەک نییە.</div>
                        </div>`;
                }

                data.forEach(msg => {
                    const bubble = document.createElement('div');
                    const user = msg.username || "نەناسراو";
                    const time = msg.time || "";
                    const text = msg.message || msg;

                    // دیاریکردنی لای نامەکە (ئەگەر هی خۆم بێت، زەرد دەبێت)
                    if (user === username) {
                        bubble.className = 'message-bubble my-message';
                    } else {
                        bubble.className = 'message-bubble other-message';
                    }

                    bubble.innerHTML = `
                        <div class="message-info">
                            <span class="username">${user}</span>
                            <span class="time">${time}</span>
                        </div>
                        <div class="message-text">${text}</div>
                    `;
                    messagesDiv.appendChild(bubble);
                });
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            });
        }

        // ٦. فەنکشنی سڕینەوەی چات
        function clearChat() {
            if (confirm("دڵنیایت دەتەوێت هەموو نامەکان بسڕیتەوە؟")) {
                fetch('/clear_messages', { method: 'POST' })
                .then(response => response.json())
                .then(data => loadMessages());
            }
        }

        // ٧. نوێکردنەوەی خۆکارانە هەر ٢ چرکە جارێک
        setInterval(loadMessages, 2000);
        loadMessages(); 
    </script>
</body>
</html>
