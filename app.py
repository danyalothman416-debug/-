<!DOCTYPE html>
<html lang="ku" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>سناپ چاتی دانیال</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', Tahoma, sans-serif; }
        body { background: #f0f2f5; display: flex; justify-content: center; align-items: center; height: 100vh; }
        
        .app-container { width: 100%; max-width: 450px; height: 90vh; background: white; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); overflow: hidden; display: flex; flex-direction: column; position: relative; }
        
        /* --- شێوازی گشتی --- */
        .hidden { display: none !important; }
        .btn { background: #fffc00; border: none; padding: 12px 20px; border-radius: 25px; font-weight: bold; cursor: pointer; font-size: 16px; transition: 0.3s; }
        .btn:hover { background: #e6e300; transform: scale(1.02); }
        
        /* --- شاشەی لۆگین --- */
        #login-view { padding: 40px 20px; display: flex; flex-direction: column; justify-content: center; height: 100%; background: linear-gradient(135deg, #fff 0%, #fffc00 100%); }
        #login-view h1 { text-align: center; margin-bottom: 30px; font-size: 28px; color: #1a1a1a; }
        .input-group { margin-bottom: 15px; }
        .input-group input { width: 100%; padding: 15px; border: 2px solid #ddd; border-radius: 15px; outline: none; font-size: 16px; }
        .input-group input:focus { border-color: #1a1a1a; }
        .auth-buttons { display: flex; gap: 10px; margin-top: 10px; }
        .auth-buttons .btn { flex: 1; }
        .btn-secondary { background: #1a1a1a; color: white; }
        .btn-secondary:hover { background: #333; }
        
        /* --- شاشەی چات --- */
        #chat-view { display: flex; flex-direction: column; height: 100%; }
        .chat-header { background: #fffc00; padding: 15px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .user-info { display: flex; align-items: center; gap: 10px; font-weight: bold; }
        .avatar-display { font-size: 24px; }
        .header-actions button { background: transparent; border: none; font-size: 20px; cursor: pointer; margin-left: 10px; }
        
        .chat-messages { flex: 1; padding: 20px; overflow-y: auto; background: #fafafa; display: flex; flex-direction: column; gap: 15px; }
        .message-box { max-width: 80%; padding: 12px; border-radius: 15px; display: flex; gap: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
        .my-message { align-self: flex-start; background: #fffc00; border-bottom-right-radius: 2px; }
        .other-message { align-self: flex-end; background: #fff; border: 1px solid #eee; border-bottom-left-radius: 2px; }
        .msg-avatar { font-size: 20px; }
        .msg-content { display: flex; flex-direction: column; }
        .msg-username { font-size: 11px; font-weight: bold; opacity: 0.7; margin-bottom: 3px; }
        .msg-text { font-size: 14px; word-wrap: break-word; }
        
        .chat-input { display: flex; padding: 15px; background: white; border-top: 1px solid #eee; gap: 10px; }
        .chat-input input { flex: 1; padding: 12px 15px; border: 2px solid #eee; border-radius: 25px; outline: none; }
        .chat-input button { width: 50px; height: 50px; border-radius: 50%; background: #fffc00; border: none; font-size: 20px; cursor: pointer; }
        
        /* --- شاشەی پرۆفایل --- */
        #profile-view { padding: 30px 20px; display: flex; flex-direction: column; height: 100%; background: #fff; }
        #profile-view h2 { margin-bottom: 20px; text-align: center; }
        .profile-avatar { font-size: 60px; text-align: center; margin-bottom: 20px; }
        .profile-input { width: 100%; padding: 15px; border: 2px solid #ddd; border-radius: 15px; margin-bottom: 15px; font-size: 16px; }
        .back-btn { background: #1a1a1a; color: white; margin-top: 20px; }
    </style>
</head>
<body>

<div class="app-container">
    
    <!-- ١. شاشەی لۆگین -->
    <div id="login-view">
        <h1>چاتی دانیال</h1>
        <div class="input-group">
            <input type="text" id="login-username" placeholder="ناوی بەکارهێنەر...">
        </div>
        <div class="input-group">
            <input type="password" id="login-password" placeholder="وشەی نهێنی...">
        </div>
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
            <input type="text" id="message-input" placeholder="نامەیەک بنووسە...">
            <button onclick="sendMessage()">➤</button>
        </div>
    </div>

    <!-- ٣. شاشەی پرۆفایل -->
    <div id="profile-view" class="hidden">
        <h2>ڕێکخستنی پرۆفایل</h2>
        <div class="profile-avatar" id="profile-avatar-preview">😎</div>
        
        <label>ئایکۆن (Emoji):</label>
        <input type="text" id="profile-avatar" class="profile-input" placeholder="بۆ نموونە: 😎 یان 🐱">
        
        <label>دەربارەی من:</label>
        <input type="text" id="profile-bio" class="profile-input" placeholder="دەربارەی خۆت بنووسە...">
        
        <button class="btn" onclick="saveProfile()">پاشەکەوتکردن</button>
        <button class="btn back-btn" onclick="showView('chat-view')">گەڕانەوە بۆ چات</button>
    </div>

</div>

<script>
    let currentUser = null;

    // --- ١. لۆگین ---
    function login() {
        const username = document.getElementById('login-username').value.trim();
        const password = document.getElementById('login-password').value.trim();
        
        if (!username || !password) return alert("تکایە هەموو خانەکان پڕ بکەرەوە.");

        fetch('/api/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username, password})
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') {
                currentUser = data.user;
                localStorage.setItem('chat_user', JSON.stringify(currentUser));
                startChat();
            } else {
                alert(data.message);
            }
        });
    }

    // --- ٢. تۆمارکردن ---
    function register() {
        const username = document.getElementById('login-username').value.trim();
        const password = document.getElementById('login-password').value.trim();
        
        if (!username || !password) return alert("تکایە هەموو خانەکان پڕ بکەرەوە.");

        fetch('/api/register', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username, password})
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') {
                alert("بە سەرکەوتوویی تۆمارکرایت! ئێستا بچۆ ژوورەوە.");
            } else {
                alert(data.message);
            }
        });
    }

    // --- ٣. دەستپێکردنی چات ---
    function startChat() {
        document.getElementById('my-username').innerText = currentUser.username;
        document.getElementById('my-avatar').innerText = currentUser.avatar || '😎';
        showView('chat-view');
        loadMessages();
        setInterval(loadMessages, 2000); // هەر ٢ چرکە جارێک نوێکردنەوە
    }

    // --- ٤. ناردنی نامە ---
    function sendMessage() {
        const input = document.getElementById('message-input');
        const text = input.value.trim();
        if (!text) return;

        fetch('/api/send', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                username: currentUser.username,
                avatar: currentUser.avatar || '😎',
                message: text
            })
        })
        .then(res => res.json())
        .then(data => {
            input.value = '';
            loadMessages();
        });
    }

    // --- ٥. وەرگرتنی نامەکان ---
    function loadMessages() {
        fetch('/api/messages')
        .then(res => res.json())
        .then(data => {
            const container = document.getElementById('messages-container');
            container.innerHTML = '';
            
            data.forEach(msg => {
                const isMe = msg.username === currentUser.username;
                const box = document.createElement('div');
                box.className = `message-box ${isMe ? 'my-message' : 'other-message'}`;
                box.innerHTML = `
                    <div class="msg-avatar">${msg.avatar || '👤'}</div>
                    <div class="msg-content">
                        <div class="msg-username">${msg.username}</div>
                        <div class="msg-text">${msg.message}</div>
                    </div>
                `;
                container.appendChild(box);
            });
            container.scrollTop = container.scrollHeight;
        });
    }

    // --- ٦. پرۆفایل ---
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
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') {
                currentUser = data.user;
                localStorage.setItem('chat_user', JSON.stringify(currentUser));
                document.getElementById('my-avatar').innerText = currentUser.avatar;
                alert("پرۆفایل نوێکرایەوە!");
                showView('chat-view');
            }
        });
    }

    // --- ٧. دەرچوون و گۆڕینی شاشەکان ---
    function logout() {
        localStorage.removeItem('chat_user');
        currentUser = null;
        showView('login-view');
    }

    function showView(viewId) {
        document.querySelectorAll('.app-container > div').forEach(div => div.classList.add('hidden'));
        document.getElementById(viewId).classList.remove('hidden');
    }

    // --- ٨. لە سەرەتادا بزانە ئایا بەکارهێنەر لۆگین کراوە یان نا ---
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
