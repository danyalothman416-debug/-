<!DOCTYPE html>
<html lang="ku" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>سناپ چات کلۆن 👻</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        body {
            background-color: #000;
            overflow: hidden;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }

        .camera-view {
            position: relative;
            width: 100%;
            height: 100%;
            max-width: 500px; /* بۆ شاشەی گەورەتر شێوەی مۆبایل وەردەگرێت */
            background-color: #111;
            overflow: hidden;
        }

        #videoElement {
            width: 100%;
            height: 100%;
            object-fit: cover;
            transform: scaleX(-1); /* بۆ ئەوەی وەک ئاوێنە دەربکەوێت */
        }

        /* باڕی سەرەوە */
        .top-bar {
            position: absolute;
            top: 20px;
            width: 100%;
            padding: 0 20px;
            display: flex;
            justify-content: space-between;
            z-index: 10;
        }

        .icon-btn {
            width: 45px;
            height: 45px;
            background: rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(10px);
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 20px;
            color: white;
            cursor: pointer;
            border: none;
        }

        /* دوگمەی وێنەگرتن */
        .capture-container {
            position: absolute;
            bottom: 40px;
            width: 100%;
            display: flex;
            justify-content: center;
            z-index: 10;
        }

        .capture-btn {
            width: 85px;
            height: 85px;
            border-radius: 50%;
            border: 6px solid #FFFC00; /* ڕەنگی زەردی سناپچات */
            background: transparent;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .capture-btn .inner-circle {
            width: 65px;
            height: 65px;
            background-color: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            transition: all 0.2s ease;
        }

        .capture-btn:active .inner-circle {
            background-color: #FFFC00;
            transform: scale(0.9);
        }

        /* ئیفێکتی فلاش لەکاتی وێنەگرتن */
        #flash {
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background-color: white;
            opacity: 0;
            pointer-events: none;
            z-index: 20;
            transition: opacity 0.1s ease-out;
        }
        
        .notification {
            position: absolute;
            top: 80px;
            left: 50%;
            transform: translateX(-50%);
            background: #FFFC00;
            color: black;
            padding: 10px 20px;
            border-radius: 20px;
            font-weight: bold;
            opacity: 0;
            transition: opacity 0.3s;
            z-index: 30;
        }
    </style>
</head>
<body>

    <div class="camera-view">
        <div id="flash"></div>
        <div class="notification" id="notify">سناپەکە نێردرا! 👻</div>

        <div class="top-bar">
            <button class="icon-btn">👤</button>
            <button class="icon-btn">🔍</button>
            <button class="icon-btn">⚙️</button>
        </div>

        <!-- پەخشی کامێرا -->
        <video id="videoElement" autoplay playsinline></video>
        <canvas id="canvas" style="display: none;"></canvas>

        <div class="capture-container">
            <div class="capture-btn" id="captureBtn">
                <div class="inner-circle"></div>
            </div>
        </div>
    </div>

    <script>
        const video = document.getElementById('videoElement');
        const canvas = document.getElementById('canvas');
        const captureBtn = document.getElementById('captureBtn');
        const flash = document.getElementById('flash');
        const notify = document.getElementById('notify');

        // پێکردنی کامێرا
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' } })
                .then(function(stream) {
                    video.srcObject = stream;
                })
                .catch(function(error) {
                    console.error("کێشەیەک هەیە لە کردنەوەی کامێرادا: ", error);
                    alert("تکایە ڕێگە بدە بە بەکارهێنانی کامێرا.");
                });
        }

        // کاتی کلیک کردن لەسەر دوگمەی وێنەگرتن
        captureBtn.addEventListener('click', function() {
            // ئیفێکتی فلاش
            flash.style.opacity = '1';
            setTimeout(() => { flash.style.opacity = '0'; }, 100);

            // وێنەگرتن
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            const context = canvas.getContext('2d');
            
            // وێنەکە پێچەوانە دەکەینەوە چونکە کامێرای پێشەوەیە
            context.translate(canvas.width, 0);
            context.scale(-1, 1);
            context.drawImage(video, 0, 0, canvas.width, canvas.height);

            // گۆڕینی وێنەکە بۆ کۆدی Base64
            const imageData = canvas.toDataURL('image/jpeg', 0.8);

            // ناردنی بۆ سێرڤەری پایتۆن
            fetch('/send_snap', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ image: imageData })
            })
            .then(response => response.json())
            .then(data => {
                if(data.status === 'success') {
                    // نیشاندانی نامەی سەرکەوتن
                    notify.style.opacity = '1';
                    setTimeout(() => { notify.style.opacity = '0'; }, 2000);
                }
            })
            .catch(error => console.error('هەڵە:', error));
        });
    </script>
</body>
</html>
