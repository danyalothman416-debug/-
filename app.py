<!DOCTYPE html>
<html lang="ku" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>سناپ چاتی دانیال</title>
    <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Vazirmatn', Tahoma, sans-serif; }
        body { background: #e5e5e5; display: flex; justify-content: center; align-items: center; height: 100vh; }
        .app-container { width: 100%; max-width: 420px; height: 90vh; background: white; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.15); overflow: hidden; display: flex; flex-direction: column; position: relative; }
        .hidden { display: none !important; }
        .btn { background: #fffc00; border: none; padding: 12px 20px; border-radius: 25px; font-weight: bold; cursor: pointer; font-size: 15px; transition: 0.3s; width: 100%; }
        .btn:hover { background: #e6e300; transform: scale(1.02); }
        .btn-secondary { background: #1a1a1a; color: white; }
        .btn-secondary:hover { background: #333; }
        #login-view { padding: 40px 25px; display: flex; flex-direction: column; justify-content: center; height: 100%; background: linear-gradient(135deg, #fff 0%, #fffc00 100%); }
        #login-view h1 { text-align: center; margin-bottom: 30px; font-size: 28px; color: #1a1a1a; }
        .input-group { margin-bottom: 15px; }
        .input-group input { width: 100%; padding: 15px; border: 2px solid #ddd; border-radius: 15px; outline: none; font-size: 16px; background: white; }
        .input-group input:focus { border-color: #1a1a1a; }
        .auth-buttons { display: flex; gap: 10px; margin-top: 10px; }
        .auth-buttons .btn { flex: 1; }
        #chat-view { display: flex; flex-direction: column; height: 100%; background: #f9f9f9; }
        .chat-header { background: #fffc00; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 5px rgba(0,0,0,0.05); z-index: 10; }
        .user-info { display: flex; align-items: center; gap: 10px; font-weight: bold; font-size: 16px; }
        .avatar-display { font-size: 22px; background: white; padding: 5px 10px; border-radius: 50%; }
        .header-actions button { background: transparent; border: none; font-size: 20px; cursor: pointer; margin-right: 15px; opacity: 0.7; transition: 0.2s; }
        .header-actions button:hover { opacity: 1; transform: scale(1.1); }
        .chat-messages { flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 15px; }
        .message-box { max-width: 75%; padding: 12px 15px; border-radius: 18px; display: flex; gap: 12px; align-items: flex-start; box-shadow: 0 2px 5px rgba(0,0,0,0.05); animation: fadeIn 0.3s ease; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .my-message { align-self: flex-start; background: #fffc00; border-bottom-right-radius: 4px; }
        .other-message { align-self: flex-end; background: #ffffff; border-bottom-left-radius: 4px; border: 1px solid #eee; }
        .msg-avatar { font-size: 20px; background: rgba(0,0,0,0.05); padding: 5px; border-radius: 50%; }
        .msg-content { display: flex; flex-direction: column; width: 100%; }
        .msg-header { display: flex; justify-content: space-between; font-size: 11px; opacity: 0.7; margin-bottom: 4px; width: 100%; gap: 15px; }
        .msg-username { font-weight: bold; }
        .msg-text { font-size: 14px; line-height: 1.4; word-wrap: break-word; }
        .chat-input { display: flex; padding: 15px; background: white; border-top: 1px solid #eee; gap: 10px; }
        .chat-input input { flex: 1; padding: 12px 20px; border: 2px solid #eee; border-radius: 25px; outline: none; font-size: 14px; transition: 0.3s; }
        .chat-input input:focus { border-color: #fffc00; }
        .chat-input button { width: 50px; height: 50px; border-radius: 50%; background: #fffc00; border: none; font-size: 20px; cursor: pointer; display: flex; justify-content: center; align-items: center; box-shadow: 0 4px 10px rgba(255,252,0,0.4); transition: 0.3s; }
        .chat-input button:hover { transform: scale(1.1); }
        #profile-view { padding: 30px 25px; display: flex; flex-direction: column; height: 100%; background: #fff; }
        #profile-view h2 { margin-bottom: 25px; text-align: center; font-size: 22px; }
        .profile-avatar-preview { font-size: 70px; text-align: center; margin-bottom: 20px; background: #fffc00; width: 120px; height: 120px; border-radius: 50%; display: flex; justify-content: center; align-items: center; margin-left: auto; margin-right: auto; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; font-size: 14px; font-weight: bold; }
        .profile-input { width: 100%; padding: 15px; border: 2px solid #eee; border-radius: 15px; font-size: 15px; outline: none; }
        .profile-input:focus { border-color: #fffc00; }
        .back-btn { background: #1a1a1a; color: white; margin-top: 15px; }
    </style>
</head>
<body>

<div class="app-container">
    <!-- ١. شاشەی لۆگین -->
    <div id="login-view">
        <h1>چاتی دانیال</h1>
        <div class="input-group"><input type="text" id="login-username" placeholder="ناوی بەکارهێنەر..."></div>
        <div class="input-group"><input type="password" id="login-password" placeholder="وشەی نهێنی..."></div>
        <div class="auth-buttons">
            <button class="btn" onclick="login()">چوونەژوورەوە</button>
            <button class="btn btn-secondary" onclick="register()">تۆمارکردن</button>
        </div>
    </div>

    <!-- ٢. شاشەی چات -->
    <div id="chat-view" class="hidden">
        <div class="chat-header">
            <div class="user-info">
                <span class="avatar-display" id="my-avatar">😎</span>
                <span id="my-username">ناو</span>
            </div>
            <div class="header-actions">
                <button onclick="openProfile()" title="پرۆفایل">⚙️</button>
                <button onclick="logout()" title="دەرچوون">🚪</button>
            </div>
        </div>
        <div class="chat-messages" id="messages-container"></div>
        <div class="chat-input">
            <input type="text" id="message-input" placeholder <div id="profile-view" class="hidden">
        <h2>ڕێکخستنی="نامەیەک بنووسە...">
            <button onclick="sendMessage()">➤</button>
        </div>
    </div>

    <!-- ٣. شاشەی پرۆفایل -->
    پرۆفایل</h2>
        <div class="profile-avatar-preview" id="profile-avatar-preview">😎</div>
        <div class="form-group">
            <label>ئایکۆن (Emoji):</label>
            <input type="text" id="profile-avatar" class="profile-input" placeholder="بۆ نموونە: 😎 یان 🐱">
        </div>
        <div class="form-group">
            <label>دەربارەی من:</label>
            <input type="text" id="profile-bio" class="profile-input" placeholder="دەربارەی خۆت بنووسە...">
        </div>
        <button class="btn" onclick="saveProfile()">پاشەکەوتکردن</button>
        <button class="btn back-btn" onclick="showView('chat-view')">گەڕانەوە بۆ چات</button>
    </div>
</div>

<!-- کتێبخانەی Socket.IO -->
<script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
<script>
    let currentUser = null;
    const socket = io(); // پەیوەندیکردن بە Socket.IO

    // --- لۆگین ---
    function login() {
        const username = document.getElementById('login-username').value.trim();
        const password = document.getElementById('login-password').value.trim();
        if (!username || !password) return alert("تکایە هەموو خانەکان پڕ بکەرەوە.");
        fetch('/api/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username, password})
        }).then(res => res.json()).then(data => {
            if (data.status === 'success') {
                currentUser = data.user;
                localStorage.setItem('chat_user', JSON.stringify(currentUser));
                startChat();
            } else { alert(data.message); }
        });
    }

    // --- تۆمارکردن ---
    function register() {
        const username = document.getElementById('login-username').value.trim();
        const password = document.getElementById('login-password').value.trim();
        if (!username || !password) return alert("تکایە هەموو خانەکان پڕ بکەرەوە.");
        fetch('/api/register', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username, password})
        }).then(res => res.json()).then(data => {
            if (data.status === 'success') {
                alert("بە سەرکەوتوویی تۆمارکرایت! ئێستا بچۆ ژوورەوە.");
            } else { alert(data.message); }
        });
    }

    // --- دەستپێکردنی چات ---
    function startChat() {
        document.getElementById('my-username').innerText = currentUser.username;
        document.getElementById('my-avatar').innerText = currentUser.avatar || '😎';
        showView('chat-view');
        loadMessages();
    }

    // --- ناردنی نامە بە Socket.IO ---
    function sendMessage() {
        const input = document.getElementById('message-input');
        const text = input.value.trim();
        if (!text) return;

        // ناردنی نامە بۆ ڕاژەکارەکە بە Socket.IO
        socket.emit('send_message', {
            username: currentUser.username,
            avatar: currentUser.avatar || '😎',
            message: text
        });
        input.value = '';
    }

    // --- وەرگرتنی نامەکان لە ڕاژەکارەکە ---
    function loadMessages() {
        fetch('/api/messages').then(res => res.json()).then(data => {
            const container = document.getElementById('messages-container');
            container.innerHTML = '';
            data.forEach(msg => appendMessage(msg, container));
            container.scrollTop = container.scrollHeight;
        });
    }

    // --- زیادکردنی نامەیەک بۆ لیستەکە ---
    function appendMessage(msg, container = null) {
        const containerRef = container || document.getElementById('messages-container');
        const isMe = msg.username === currentUser.username;
        const box = document.createElement('div');
        box.className = `message-box ${isMe ? 'my-message' : 'other-message'}`;
        box.innerHTML = `
            <div class="msg-avatar">${msg.avatar || '👤'}</div>
            <div class="msg-content">
                <div class="msg-header">
                    <span class="msg-username">${msg.username}</span>
                    <span>${msg.time || ''}</span>
                </div>
                <div class="msg-text">${msg.message}</div>
            </div>
        `;
        containerRef.appendChild(box);
        containerRef.scrollTop = containerRef.scrollHeight;
    }

    // --- گوێگرتن بۆ نامەی نوێ لە Socket.IO ---
    socket.on('new_message', function(msg) {
        appendMessage(msg);
    });

    // --- پرۆفایل ---
    function openProfile() {
        document.getElementById('profile-avatar-preview').innerText = currentUser.avatar || '😎';
        document.getElementById('profile-avatar').value = currentUser.avatar || '😎';
        document.getElementById('profile-bio').value = currentUser.bio || '';
        showView('profile-view');
    }

    function saveProfile() {
        const bio = document.getElementById('profile-bio').value;
        const avatar = document.getElementById('profile-avatar').value;
        fetch('/api/update_profile', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username: currentUser.username, bio, avatar})
        }).then(res => res.json()).then(data => {
            if (data.status === 'success') {
                currentUser = data.user;
                localStorage.setItem('chat_user', JSON.stringify(currentUser));
                document.getElementById('my-avatar').innerText = currentUser.avatar;
                alert("پرۆفایل نوێکرایەوە!");
                showView('chat-view');
            }
        });
    }

    // --- دەرچوون و گۆڕینی شاشەکان ---
    function logout() {
        localStorage.removeItem('chat_user');
        currentUser = null;
        showView('login-view');
    }

    function showView(viewId) {
        document.querySelectorAll('.app-container > div').forEach(div => div.classList.add('hidden'));
        document.getElementById(viewId).classList.remove('hidden');
    }

    // --- لە سەرەتادا بزانە ئایا بەکارهێنەر لۆگین کراوە یان نا ---
    window.onload = function() {
        const savedUser = localStorage.getItem('chat_user');
        if (savedUser) {
            currentUser = JSON.parse(savedUser);
            startChat();
        }
    };
</script>
</body>
</html>
