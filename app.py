// ١. دۆزینەوەی بەشەکانی ڕووکار
        const input = document.getElementById('message-input');
        const sendBtn = document.getElementById('send-btn');
        const messagesDiv = document.getElementById('messages-container');
        
        // ٢. پرسیارکردن لە بەکارهێنەر بۆ ناوی خۆی
        let username = prompt("تکایە ناوی خۆت بنووسە:");
        if (!username || username.trim() === "") {
            username = "نەناسراو";
        }

        // ٣. چالاککردنی دوگمەکە بۆ ناردنی نامە
        sendBtn.addEventListener('click', function() {
            const text = input.value.trim();
            if (!text) return;

            fetch('/send', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username: username, message: text})
            })
            .then(res => res.json())
            .then(data => {
                input.value = '';
                loadMessages();
            });
        });

        // ٤. وەرگرتنی نامەکان لە ڕاژەکارەکە
        function loadMessages() {
            fetch('/get_messages')
            .then(res => res.json())
            .then(data => {
                messagesDiv.innerHTML = ''; 
                data.forEach(msg => {
                    const bubble = document.createElement('div');
                    bubble.className = 'message-bubble other-message';
                    bubble.innerHTML = `
                        <div class="message-info">
                            <span class="username">${msg.username}</span>
                            <span class="time">${msg.time}</span>
                        </div>
                        <div class="message-text">${msg.message}</div>
                    `;
                    messagesDiv.appendChild(bubble);
                });
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            });
        }

        // ٥. هەر ٢ چرکە جارێک نامەکان نوێ دەکاتەوە
        setInterval(loadMessages, 2000);
        loadMessages();
