<!DOCTYPE html>
<html lang="ckb" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>چوونەژوورەوە | سیستەمی دانیال</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&family=Vazirmatn:wght@300;400;600;700;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

    <style>
        :root {
            --bg-primary: #08070d;
            --accent-purple: #7928ca;
            --accent-blue: #0070f3;
            --accent-cyan: #00dfd8;
            --glass-bg: rgba(255, 255, 255, 0.03);
            --glass-border: rgba(255, 255, 255, 0.08);
            --text-main: #ffffff;
            --text-muted: #8a8f98;
            --error-color: #ff4757;
            --success-color: #2ed573;
            --transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Vazirmatn', 'Plus Jakarta Sans', sans-serif;
            -webkit-font-smoothing: antialiased;
        }

        body {
            background-color: var(--bg-primary);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            position: relative;
            color: var(--text-main);
        }

        /* باکگراوندی ڕەنگینی دینامیکی */
        .ambient-glow {
            position: absolute;
            width: 500px;
            height: 500px;
            filter: blur(140px);
            border-radius: 50%;
            z-index: 0;
            opacity: 0.45;
            pointer-events: none;
            animation: floatGlow 14s infinite alternate ease-in-out;
        }

        .glow-1 {
            background: radial-gradient(circle, var(--accent-purple), transparent 70%);
            top: -10%;
            right: -5%;
        }

        .glow-2 {
            background: radial-gradient(circle, var(--accent-blue), transparent 70%);
            bottom: -15%;
            left: -5%;
            animation-delay: -7s;
        }

        @keyframes floatGlow {
            0% { transform: translate(0, 0) scale(1); }
            100% { transform: translate(50px, 40px) scale(1.15); }
        }

        /* کارتەکەی ناوەند (Glassmorphism) */
        .login-card {
            position: relative;
            z-index: 1;
            width: 100%;
            max-width: 440px;
            padding: 48px 40px;
            background: var(--glass-bg);
            backdrop-filter: blur(24px);
            -webkit-backdrop-filter: blur(24px);
            border: 1px solid var(--glass-border);
            border-radius: 28px;
            box-shadow: 0 30px 60px rgba(0, 0, 0, 0.45),
                        inset 0 1px 0 rgba(255, 255, 255, 0.1);
            animation: cardAppear 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }

        @keyframes cardAppear {
            0% { opacity: 0; transform: translateY(30px) scale(0.97); }
            100% { opacity: 1; transform: translateY(0) scale(1); }
        }

        .brand-header {
            text-align: center;
            margin-bottom: 36px;
        }

        .brand-logo {
            width: 68px;
            height: 68px;
            margin: 0 auto 16px;
            border-radius: 20px;
            background: linear-gradient(135deg, var(--accent-purple), var(--accent-blue));
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 12px 24px rgba(121, 40, 202, 0.35);
            font-size: 28px;
            color: #fff;
            transform: rotate(-5deg);
            transition: var(--transition);
        }

        .login-card:hover .brand-logo {
            transform: rotate(0deg) scale(1.05);
        }

        .brand-header h1 {
            font-size: 26px;
            font-weight: 800;
            letter-spacing: -0.5px;
            margin-bottom: 6px;
            background: linear-gradient(180deg, #fff, #b8b8b8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .brand-header p {
            color: var(--text-muted);
            font-size: 14px;
        }

        /* فۆڕم و خانەکان */
        .input-group {
            margin-bottom: 22px;
            position: relative;
        }

        .input-label {
            display: block;
            margin-bottom: 8px;
            font-size: 13px;
            font-weight: 600;
            color: #d1d5db;
        }

        .input-wrapper {
            position: relative;
            display: flex;
            align-items: center;
        }

        .input-wrapper i.lead-icon {
            position: absolute;
            right: 18px;
            color: var(--text-muted);
            font-size: 17px;
            transition: var(--transition);
            pointer-events: none;
        }

        .input-wrapper input {
            width: 100%;
            padding: 16px 48px 16px 48px;
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid var(--glass-border);
            border-radius: 16px;
            color: #fff;
            font-size: 14px;
            outline: none;
            transition: var(--transition);
        }

        .input-wrapper input::placeholder {
            color: #555a64;
        }

        .input-wrapper input:focus {
            background: rgba(255, 255, 255, 0.07);
            border-color: rgba(0, 112, 243, 0.6);
            box-shadow: 0 0 0 4px rgba(0, 112, 243, 0.15);
        }

        .input-wrapper input:focus + i.lead-icon {
            color: var(--accent-cyan);
        }

        .toggle-password {
            position: absolute;
            left: 18px;
            cursor: pointer;
            color: var(--text-muted);
            font-size: 16px;
            transition: var(--transition);
        }

        .toggle-password:hover {
            color: #fff;
        }

        /* ڕێکخستنی هەڵبژاردن و لەبیرچوونەوە */
        .form-actions {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 28px;
            font-size: 13px;
        }

        .remember-wrap {
            display: flex;
            align-items: center;
            gap: 8px;
            cursor: pointer;
            user-select: none;
            color: var(--text-muted);
        }

        .remember-wrap input[type="checkbox"] {
            appearance: none;
            width: 18px;
            height: 18px;
            border-radius: 6px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--glass-border);
            cursor: pointer;
            position: relative;
            transition: var(--transition);
        }

        .remember-wrap input[type="checkbox"]:checked {
            background: var(--accent-blue);
            border-color: var(--accent-blue);
        }

        .remember-wrap input[type="checkbox"]:checked::after {
            content: "\f00c";
            font-family: "Font Awesome 6 Free";
            font-weight: 900;
            font-size: 10px;
            color: #fff;
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
        }

        .forgot-link {
            color: var(--accent-cyan);
            text-decoration: none;
            transition: var(--transition);
        }

        .forgot-link:hover {
            text-decoration: underline;
            color: #fff;
        }

        /* دوگمەی چوونەژوورەوە */
        .btn-submit {
            width: 100%;
            padding: 16px;
            border-radius: 16px;
            border: none;
            background: linear-gradient(135deg, var(--accent-purple), var(--accent-blue));
            color: #fff;
            font-size: 15px;
            font-weight: 700;
            cursor: pointer;
            box-shadow: 0 10px 24px rgba(0, 112, 243, 0.35);
            transition: var(--transition);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            position: relative;
            overflow: hidden;
        }

        .btn-submit:hover {
            transform: translateY(-2px);
            box-shadow: 0 14px 28px rgba(0, 112, 243, 0.45);
            filter: brightness(1.1);
        }

        .btn-submit:active {
            transform: translateY(0);
        }

        .btn-submit.loading .btn-text {
            visibility: hidden;
            opacity: 0;
        }

        .btn-submit.loading .spinner {
            display: block;
        }

        .spinner {
            display: none;
            position: absolute;
            width: 22px;
            height: 22px;
            border: 3px solid rgba(255, 255, 255, 0.3);
            border-top-color: #fff;
            border-radius: 50%;
            animation: spin 0.7s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        /* پەیامی ئاگاداری */
        .toast-banner {
            padding: 12px 16px;
            border-radius: 12px;
            font-size: 13px;
            margin-bottom: 20px;
            display: none;
            align-items: center;
            gap: 10px;
            animation: slideDown 0.3s ease;
        }

        @keyframes slideDown {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .toast-banner.error {
            background: rgba(255, 71, 87, 0.15);
            border: 1px solid rgba(255, 71, 87, 0.3);
            color: #ff6b81;
            display: flex;
        }

        .toast-banner.success {
            background: rgba(46, 213, 115, 0.15);
            border: 1px solid rgba(46, 213, 115, 0.3);
            color: #2ed573;
            display: flex;
        }

        /* ئەنیمەیشنی لەرزین لە کاتی هەڵە */
        .shake {
            animation: shake 0.4s ease-in-out;
        }

        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            20%, 60% { transform: translateX(-8px); }
            40%, 80% { transform: translateX(8px); }
        }
    </style>
</head>
<body>

    <div class="ambient-glow glow-1"></div>
    <div class="ambient-glow glow-2"></div>

    <div class="login-card" id="loginCard">
        <div class="brand-header">
            <div class="brand-logo">
                <i class="fa-solid fa-cube"></i>
            </div>
            <h1>سیستەمی دانیال</h1>
            <p>بەخێربێیتەوە! تکایە زانیارییەکانت بنووسە</p>
        </div>

        <div id="toast" class="toast-banner">
            <i class="fa-solid fa-circle-exclamation"></i>
            <span id="toastMsg"></span>
        </div>

        <form id="loginForm" autocomplete="off">
            <div class="input-group">
                <label class="input-label" for="identifier">ئیمەیڵ یان ناوی بەکارهێنەر</label>
                <div class="input-wrapper">
                    <input type="text" id="identifier" name="identifier" placeholder="danyal یان danyal@app.io" required>
                    <i class="fa-regular fa-user lead-icon"></i>
                </div>
            </div>

            <div class="input-group">
                <label class="input-label" for="password">وشەی نهێنی</label>
                <div class="input-wrapper">
                    <input type="password" id="password" name="password" placeholder="••••••••••••" required>
                    <i class="fa-solid fa-lock lead-icon"></i>
                    <i class="fa-regular fa-eye-slash toggle-password" id="togglePassword"></i>
                </div>
            </div>

            <div class="form-actions">
                <label class="remember-wrap">
                    <input type="checkbox" id="rememberMe">
                    <span>لەبیرم مەبە</span>
                </label>
                <a href="#" class="forgot-link">وشەی نهێنیت لەبیرچووە؟</a>
            </div>

            <button type="submit" class="btn-submit" id="submitBtn">
                <span class="btn-text">چوونەژوورەوە</span>
                <span class="spinner"></span>
            </button>
        </form>
    </div>

    <script>
        const form = document.getElementById('loginForm');
        const submitBtn = document.getElementById('submitBtn');
        const loginCard = document.getElementById('loginCard');
        const toast = document.getElementById('toast');
        const toastMsg = document.getElementById('toastMsg');
        const togglePassword = document.getElementById('togglePassword');
        const passwordInput = document.getElementById('password');

        // بینینی وشەی نهێنی
        togglePassword.addEventListener('click', () => {
            const isPassword = passwordInput.getAttribute('type') === 'password';
            passwordInput.setAttribute('type', isPassword ? 'text' : 'password');
            togglePassword.classList.toggle('fa-eye');
            togglePassword.classList.toggle('fa-eye-slash');
        });

        function showToast(message, type = 'error') {
            toast.className = `toast-banner ${type}`;
            toastMsg.textContent = message;
            toast.style.display = 'flex';
        }

        // ناردنی فۆڕم لەڕێگەی Fetch API
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            toast.style.display = 'none';

            const identifier = document.getElementById('identifier').value.trim();
            const password = passwordInput.value.trim();
            const rememberMe = document.getElementById('rememberMe').checked;

            submitBtn.classList.add('loading');
            submitBtn.disabled = true;

            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: JSON.stringify({
                        identifier: identifier,
                        password: password,
                        remember_me: rememberMe
                    })
                });

                const result = await response.json();

                if (response.ok) {
                    showToast(result.message, 'success');
                    setTimeout(() => {
                        window.location.href = result.redirect_url;
                    }, 1200);
                } else {
                    showToast(result.message || 'هەڵەیەک ڕوویدا', 'error');
                    loginCard.classList.add('shake');
                    setTimeout(() => loginCard.classList.remove('shake'), 400);
                }
            } catch (err) {
                showToast('نەتوانرا پەیوەندی بە سێرڤەرەوە بکرێت', 'error');
            } finally {
                submitBtn.classList.remove('loading');
                submitBtn.disabled = false;
            }
        });
    </script>
</body>
</html>
