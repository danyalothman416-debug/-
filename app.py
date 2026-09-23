<!DOCTYPE html>
<html lang="ckb" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>سیستەمی قەرز و حسابات | پڕۆژەی دانیال</title>
    <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;600;700;800;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <!-- کتێبخانەی فەرمی Google Sign-In -->
    <script src="https://accounts.google.com/gsi/client" async defer></script>

    <style>
        :root {
            --bg-dark: #07090e;
            --surface: rgba(15, 20, 32, 0.82);
            --surface-glass: rgba(255, 255, 255, 0.05);
            --border-glass: rgba(255, 255, 255, 0.1);
            --accent-blue: #0070f3;
            --accent-purple: #7928ca;
            --accent-danger: #ef4444;
            --accent-success: #10b981;
            --text-main: #ffffff;
            --text-muted: #9ba1b0;
            --transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Vazirmatn', sans-serif;
            -webkit-font-smoothing: antialiased;
        }

        body {
            background-color: var(--bg-dark);
            color: var(--text-main);
            min-height: 100vh;
            overflow-x: hidden;
        }

        /* ١. پەڕەی دەستپێکی سینەمایی (Video Splash Intro) */
        #splashScreen {
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            background: #000;
            z-index: 9999;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            transition: opacity 0.8s ease, visibility 0.8s;
        }

        .splash-video {
            position: absolute;
            top: 50%; left: 50%;
            min-width: 100%; min-height: 100%;
            transform: translate(-50%, -50%);
            object-fit: cover;
            filter: brightness(0.4) contrast(1.2);
            z-index: 1;
        }

        .splash-content {
            position: relative;
            z-index: 2;
            text-align: center;
            animation: introPop 1.2s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }

        @keyframes introPop {
            0% { opacity: 0; transform: scale(0.7) translateY(40px); }
            100% { opacity: 1; transform: scale(1) translateY(0); }
        }

        .splash-logo {
            width: 110px;
            height: 110px;
            margin: 0 auto 24px;
            border-radius: 30px;
            background: linear-gradient(135deg, var(--accent-purple), var(--accent-blue));
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 50px;
            box-shadow: 0 0 50px rgba(0, 112, 243, 0.8);
            animation: floatLogo 3s infinite alternate ease-in-out;
        }

        @keyframes floatLogo {
            0% { transform: translateY(0) rotate(0deg); }
            100% { transform: translateY(-12px) rotate(4deg); }
        }

        .splash-title {
            font-size: 32px;
            font-weight: 900;
            letter-spacing: -0.5px;
            background: linear-gradient(180deg, #ffffff, #a5b4fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
        }

        .splash-subtitle {
            color: #d1d5db;
            font-size: 15px;
            letter-spacing: 0.5px;
        }

        /* دوگمەی تێپەڕاندن */
        .btn-skip-splash {
            margin-top: 30px;
            padding: 10px 24px;
            border-radius: 30px;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: #fff;
            cursor: pointer;
            backdrop-filter: blur(8px);
            transition: var(--transition);
        }

        .btn-skip-splash:hover {
            background: rgba(255, 255, 255, 0.25);
            transform: scale(1.05);
        }

        /* ٢. پەڕەی لۆگین لەگەڵ وێنەی باکگراوند */
        .login-wrapper {
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            background: url('https://images.unsplash.com/photo-1518770660439-4636190af475?w=1800') center/cover no-repeat;
        }

        .login-backdrop-overlay {
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background: radial-gradient(circle, rgba(11, 15, 25, 0.75) 0%, rgba(7, 9, 14, 0.95) 100%);
            backdrop-filter: blur(8px);
        }

        .login-card {
            position: relative;
            z-index: 2;
            width: 100%;
            max-width: 440px;
            padding: 44px 36px;
            background: var(--surface);
            backdrop-filter: blur(28px);
            border: 1px solid var(--border-glass);
            border-radius: 28px;
            box-shadow: 0 30px 60px rgba(0,0,0,0.6);
            animation: cardIn 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
            text-align: center;
        }

        @keyframes cardIn {
            from { opacity: 0; transform: translateY(20px) scale(0.96); }
            to { opacity: 1; transform: translateY(0) scale(1); }
        }

        /* دوگمەی فەرمی گۆگڵ */
        .google-btn-custom {
            width: 100%;
            padding: 13px;
            background: #ffffff;
            color: #1f2937;
            border-radius: 14px;
            border: none;
            font-size: 14px;
            font-weight: 700;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
            transition: var(--transition);
            margin-bottom: 22px;
        }

        .google-btn-custom:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(255, 255, 255, 0.2);
        }

        .google-icon-svg {
            width: 20px;
            height: 20px;
        }

        .divider-line {
            display: flex;
            align-items: center;
            text-align: center;
            color: var(--text-muted);
            font-size: 12px;
            margin-bottom: 22px;
        }

        .divider-line::before, .divider-line::after {
            content: '';
            flex: 1;
            border-bottom: 1px solid var(--border-glass);
        }

        .divider-line span { padding: 0 10px; }

        .input-group {
            margin-bottom: 16px;
            text-align: right;
        }

        .input-group label {
            display: block;
            margin-bottom: 6px;
            font-size: 12.5px;
            color: var(--text-muted);
        }

        .input-group input {
            width: 100%;
            padding: 11px 14px;
            background: rgba(0,0,0,0.35);
            border: 1px solid var(--border-glass);
            border-radius: 12px;
            color: #fff;
            outline: none;
            font-size: 13.5px;
        }

        .btn-login-admin {
            width: 100%;
            padding: 12px;
            border-radius: 12px;
            border: none;
            background: linear-gradient(135deg, var(--accent-purple), var(--accent-blue));
            color: #fff;
            font-weight: 700;
            font-size: 13.5px;
            cursor: pointer;
            transition: var(--transition);
        }

        .btn-login-admin:hover { filter: brightness(1.1); transform: translateY(-2px); }

        /* ٣. داشبۆرد و ناوەوەی سیستەم */
        .app-view {
            display: none;
            min-height: 100vh;
            flex-direction: column;
        }

        .navbar {
            background: rgba(11, 15, 25, 0.85);
            backdrop-filter: blur(20px);
            border-bottom: 1px solid var(--border-glass);
            padding: 14px 28px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: sticky;
            top: 0;
            z-index: 50;
        }

        .profile-pill {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 6px 14px;
            border-radius: 30px;
            background: var(--surface-glass);
            border: 1px solid var(--border-glass);
            cursor: pointer;
            transition: var(--transition);
        }

        .profile-pill:hover { background: rgba(255,255,255,0.08); }

        .profile-avatar-img {
            width: 38px;
            height: 38px;
            border-radius: 50%;
            object-fit: cover;
            border: 2px solid var(--accent-blue);
        }

        .main-container {
            max-width: 1240px;
            width: 100%;
            margin: 26px auto;
            padding: 0 20px;
            flex: 1;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 20px;
            margin-bottom: 26px;
        }

        .stat-card {
            background: var(--surface);
            border: 1px solid var(--border-glass);
            border-radius: 20px;
            padding: 22px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .stat-card h4 { font-size: 13px; color: var(--text-muted); margin-bottom: 6px; }
        .stat-card .val { font-size: 24px; font-weight: 800; }

        .controls-row {
            background: var(--surface);
            border: 1px solid var(--border-glass);
            border-radius: 20px;
            padding: 16px 20px;
            margin-bottom: 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 14px;
        }

        .search-box {
            position: relative;
            min-width: 280px;
        }

        .search-box input {
            width: 100%;
            padding: 10px 38px 10px 14px;
            background: rgba(0,0,0,0.3);
            border: 1px solid var(--border-glass);
            border-radius: 12px;
            color: #fff;
            outline: none;
            font-size: 13px;
        }

        .search-box i {
            position: absolute;
            right: 12px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-muted);
        }

        .btn-action {
            padding: 10px 18px;
            border-radius: 12px;
            border: none;
            font-size: 13px;
            font-weight: 700;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: var(--transition);
        }

        .table-panel {
            background: var(--surface);
            border: 1px solid var(--border-glass);
            border-radius: 20px;
            overflow: hidden;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            text-align: right;
            font-size: 13.5px;
        }

        th {
            background: rgba(0,0,0,0.3);
            padding: 16px 20px;
            color: var(--text-muted);
            border-bottom: 1px solid var(--border-glass);
        }

        td {
            padding: 16px 20px;
            border-bottom: 1px solid var(--border-glass);
        }

        .badge-status {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 11.5px;
            font-weight: 700;
        }

        .badge-paid { background: rgba(16, 185, 129, 0.15); color: var(--accent-success); }
        .badge-overdue { background: rgba(239, 68, 68, 0.15); color: var(--accent-danger); }
        .badge-pending { background: rgba(0, 112, 243, 0.15); color: var(--accent-blue); }

        /* مۆداڵەکان */
        .modal-screen {
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.7);
            backdrop-filter: blur(8px);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 2000;
            padding: 16px;
        }

        .modal-body {
            background: #101422;
            border: 1px solid var(--border-glass);
            border-radius: 24px;
            width: 100%;
            max-width: 460px;
            padding: 26px;
            animation: cardIn 0.35s ease;
        }
    </style>
</head>
<body>

    <!-- ١. پەڕەی دەستپێکی سینەمایی (Video Splash) -->
    <div id="splashScreen">
        <video class="splash-video" autoplay muted loop playsinline>
            <source src="https://assets.mixkit.co/videos/preview/mixkit-digital-animation-of-screens-with-graphs-and-data-31913-large.mp4" type="video/mp4">
        </video>
        <div class="splash-content">
            <div class="splash-logo">
                <i class="fa-solid fa-cube" style="color: #fff;"></i>
            </div>
            <h1 class="splash-title">سیستەمی دانیال</h1>
            <p class="splash-subtitle">بەڕێوەبردنی قەرز، وەسڵەکان و حسابی پێشکەوتوو</p>
            <button class="btn-skip-splash" onclick="finishSplash()">
                دەستپێکردن <i class="fa-solid fa-arrow-left" style="margin-right: 6px;"></i>
            </button>
        </div>
    </div>

    <!-- ٢. پەڕەی چوونەژوورەوە بە باکگراوندی دیمەنی سەرنجڕاکێش -->
    <div class="login-wrapper" id="loginWrapper">
        <div class="login-backdrop-overlay"></div>
        <div class="login-card">
            <div style="font-size: 32px; color: var(--accent-blue); margin-bottom: 12px;">
                <i class="fa-solid fa-file-invoice-dollar"></i>
            </div>
            <h2 style="font-size: 22px; font-weight: 800; margin-bottom: 6px;">بەخێربێیتەوە</h2>
            <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 24px;">تکایە هەژمارەکەت هەڵبژێرە بۆ چوونەژوورەوە</p>

            <!-- دوگمەی چوونەژوورەوە لە ڕێگەی Google -->
            <button class="google-btn-custom" onclick="triggerGoogleSignIn()">
                <svg class="google-icon-svg" viewBox="0 0 48 48">
                    <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
                    <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
                    <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.79l7.97-6.2z"/>
                    <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
                </svg>
                <span>چوونەژوورەوە لە ڕێگەی Google</span>
            </button>

            <!-- شوێنی Google One-Tap ی ئۆتۆماتیکی -->
            <div id="g_id_onload"
                 data-client_id="YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com"
                 data-callback="handleGoogleCredentialResponse"
                 data-auto_prompt="false">
            </div>

            <div class="divider-line">
                <span>یان بە هەژماری Admin</span>
            </div>

            <!-- چوونەژوورەوەی ئەدمین -->
            <form id="adminLoginForm">
                <div class="input-group">
                    <label>ناوی بەکارهێنەر</label>
                    <input type="text" id="adminUser" placeholder="admin" required>
                </div>
                <div class="input-group">
                    <label>وشەی نهێنی</label>
                    <input type="password" id="adminPass" placeholder="••••••••" required>
                </div>
                <button type="submit" class="btn-login-admin">چوونەژوورەوە</button>
            </form>
            <p id="loginErrMsg" style="color: var(--accent-danger); font-size: 13px; margin-top: 14px; display: none;"></p>
        </div>
    </div>

    <!-- ٣. داشبۆردی سەرەکی سیستەم -->
    <div class="app-view" id="appView">
        <header class="navbar">
            <div style="font-weight: 800; font-size: 18px; display: flex; align-items: center; gap: 10px;">
                <i class="fa-solid fa-cube" style="color: var(--accent-blue);"></i>
                سیستەمی قەرز و حسابات
            </div>

            <!-- پرۆفایلی بەکارهێنەر -->
            <div class="profile-pill" onclick="openProfileModal()">
                <img src="" id="navAvatar" class="profile-avatar-img" alt="avatar">
                <div style="text-align: right;">
                    <div id="navName" style="font-weight: 700; font-size: 13px;"></div>
                    <div id="navBio" style="font-size: 11px; color: var(--text-muted); max-width: 140px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;"></div>
                </div>
                <i class="fa-solid fa-angle-down" style="font-size: 12px; color: var(--text-muted);"></i>
            </div>
        </header>

        <main class="main-container">
            <!-- ئامارەکان -->
            <div class="stats-grid">
                <div class="stat-card">
                    <div>
                        <h4>کۆی قەرز</h4>
                        <div class="val" id="statDebt">0</div>
                    </div>
                    <i class="fa-solid fa-coins" style="font-size: 26px; color: var(--accent-blue);"></i>
                </div>
                <div class="stat-card">
                    <div>
                        <h4>کۆی پارەی دراو</h4>
                        <div class="val" style="color: var(--accent-success);" id="statPaid">0</div>
                    </div>
                    <i class="fa-solid fa-circle-check" style="font-size: 26px; color: var(--accent-success);"></i>
                </div>
                <div class="stat-card">
                    <div>
                        <h4>کۆی پارەی ماوە</h4>
                        <div class="val" style="color: var(--accent-danger);" id="statRem">0</div>
                    </div>
                    <i class="fa-solid fa-hand-holding-dollar" style="font-size: 26px; color: var(--accent-danger);"></i>
                </div>
            </div>

            <!-- کۆنترۆڵەکان -->
            <div class="controls-row">
                <div class="search-box">
                    <i class="fa-solid fa-magnifying-glass"></i>
                    <input type="text" id="searchInput" placeholder="گەڕان بەپێی ناوی کەسەکە..." oninput="loadDebts()">
                </div>
                <div style="display: flex; gap: 10px;">
                    <button class="btn-action" style="background: linear-gradient(135deg, var(--accent-purple), var(--accent-blue)); color: #fff;" onclick="openDebtModal()">
                        <i class="fa-solid fa-plus"></i> قەرزی نوێ
                    </button>
                    <button class="btn-action" style="background: var(--surface-glass); border: 1px solid var(--border-glass); color: #fff;" onclick="location.href='/api/reports/export-excel'">
                        <i class="fa-solid fa-file-excel"></i> ئێکسڵ
                    </button>
                    <button class="btn-action" style="background: var(--surface-glass); border: 1px solid var(--border-glass); color: var(--accent-danger);" onclick="logout()">
                        <i class="fa-solid fa-arrow-right-from-bracket"></i> دەرچوون
                    </button>
                </div>
            </div>

            <!-- خشتە -->
            <div class="table-panel">
                <table>
                    <thead>
                        <tr>
                            <th>کۆد</th>
                            <th>ناوی کەسی قەرزدار</th>
                            <th>مۆبایل</th>
                            <th>کۆی قەرز</th>
                            <th>دراو</th>
                            <th>ماوە</th>
                            <th>بەرواری دانەوە</th>
                            <th>دۆخ</th>
                            <th>کردارەکان</th>
                        </tr>
                    </thead>
                    <tbody id="debtsBody"></tbody>
                </table>
            </div>
        </main>
    </div>

    <!-- مۆداڵی قەرزی نوێ -->
    <div class="modal-screen" id="debtModal">
        <div class="modal-body">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px;">
                <h3 style="font-size: 16px;">تۆمارکردنی قەرزی نوێ</h3>
                <i class="fa-solid fa-xmark" style="cursor: pointer;" onclick="closeModal('debtModal')"></i>
            </div>
            <form id="debtForm">
                <div class="input-group">
                    <label>ناوی کەسی قەرزەکە *</label>
                    <input type="text" id="custName" list="custSuggestions" required placeholder="ناوی کڕیار بنووسە...">
                    <datalist id="custSuggestions"></datalist>
                </div>
                <div class="input-group">
                    <label>ژمارەی مۆبایل</label>
                    <input type="text" id="custPhone" placeholder="0750...">
                </div>
                <div class="input-group">
                    <label>بڕی قەرز (دینار) *</label>
                    <input type="number" id="custAmount" required placeholder="نموونە: 120000">
                </div>
                <div class="input-group">
                    <label>بەرواری دانەوە *</label>
                    <input type="date" id="custDueDate" required>
                </div>
                <button type="submit" class="btn-login-admin" style="margin-top: 10px;">تۆمارکردن</button>
            </form>
        </div>
    </div>

    <!-- مۆداڵی پرۆفایل و بایۆ -->
    <div class="modal-screen" id="profileModal">
        <div class="modal-body">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px;">
                <h3 style="font-size: 16px;">پرۆفایلی من</h3>
                <i class="fa-solid fa-xmark" style="cursor: pointer;" onclick="closeModal('profileModal')"></i>
            </div>
            <form id="profileForm">
                <div style="text-align: center; margin-bottom: 16px;">
                    <img src="" id="profileImgPreview" style="width: 80px; height: 80px; border-radius: 50%; object-fit: cover; border: 2px solid var(--accent-blue);">
                    <div style="margin-top: 8px;">
                        <input type="file" id="avatarInput" accept="image/*" style="display: none;">
                        <button type="button" class="btn-action" style="background: var(--surface-glass); border: 1px solid var(--border-glass); color: #fff; font-size: 11px; padding: 6px 12px;" onclick="document.getElementById('avatarInput').click()">
                            گۆڕینی وێنە
                        </button>
                    </div>
                </div>
                <div class="input-group">
                    <label>ناوی تەواو</label>
                    <input type="text" id="profileName" required>
                </div>
                <div class="input-group">
                    <label>بایۆ (Bio)</label>
                    <input type="text" id="profileBio">
                </div>
                <button type="submit" class="btn-login-admin" style="margin-top: 10px;">پاشەکەوتکردن</button>
            </form>
        </div>
    </div>

    <!-- مۆداڵی واسڵکردن -->
    <div class="modal-screen" id="payModal">
        <div class="modal-body">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px;">
                <h3 id="payTitle" style="font-size: 16px;">واڵسکردنی پارە</h3>
                <i class="fa-solid fa-xmark" style="cursor: pointer;" onclick="closeModal('payModal')"></i>
            </div>
            <form id="payForm">
                <input type="hidden" id="payDebtId">
                <div class="input-group">
                    <label>بڕی پارەی واسڵکراو (دینار) *</label>
                    <input type="number" id="payAmount" required>
                </div>
                <button type="submit" class="btn-action" style="width: 100%; justify-content: center; background: var(--accent-success); color: #fff; margin-top: 10px;">
                    تەواوکردن
                </button>
            </form>
        </div>
    </div>

    <script>
        let currentUser = null;
        let customerSuggestionsList = [];

        // پەڕەی دەستپێک (Splash Screen) پاش 3 چرکە دەڕوات یان بە کلیک
        let splashTimer = setTimeout(finishSplash, 3500);

        function finishSplash() {
            clearTimeout(splashTimer);
            const splash = document.getElementById('splashScreen');
            splash.style.opacity = '0';
            setTimeout(() => {
                splash.style.display = 'none';
                checkAuth();
            }, 800);
        }

        async function checkAuth() {
            const res = await fetch('/api/auth/me');
            const data = await res.json();
            if (data.logged_in) {
                currentUser = data.user;
                showApp();
            } else {
                showLogin();
            }
        }

        function showLogin() {
            document.getElementById('loginWrapper').style.display = 'flex';
            document.getElementById('appView').style.display = 'none';
        }

        function showApp() {
            document.getElementById('loginWrapper').style.display = 'none';
            document.getElementById('appView').style.display = 'flex';
            updateProfileUI();
            loadDashboard();
            loadCustomerSuggestions();
            loadDebts();
        }

        function updateProfileUI() {
            document.getElementById('navName').textContent = currentUser.full_name;
            document.getElementById('navBio').textContent = currentUser.bio || 'بێ بایۆ';
            document.getElementById('navAvatar').src = currentUser.avatar;
            document.getElementById('profileImgPreview').src = currentUser.avatar;
            document.getElementById('profileName').value = currentUser.full_name;
            document.getElementById('profileBio').value = currentUser.bio || '';
        }

        // وەڵامدانەوەی فەرمی گووگڵ (Callback)
        async function handleGoogleCredentialResponse(response) {
            const res = await fetch('/api/auth/google', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ credential: response.credential })
            });
            const data = await res.json();
            if (res.ok) {
                currentUser = data.user;
                showApp();
            } else {
                alert(data.message || 'هەڵە لە چوونەژوورەوەی گووگڵ');
            }
        }

        // بۆ تاقیکردنەوەی خێرای چوونەژوورەوەی گووگڵ
        function triggerGoogleSignIn() {
            // ئەگەر Google Client ID دابنرێت ڕاستەوخۆ دیالۆگ دەکاتەوە
            if (window.google && google.accounts && google.accounts.id) {
                google.accounts.id.prompt();
            } else {
                // شێوازی دەستپێکردنی تاقیکاری لە نەبوونی کلیل
                const mockPayload = btoa(JSON.stringify({
                    email: "danyal.google@gmail.com",
                    name: "Danyal Google User",
                    picture: "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150"
                }));
                handleGoogleCredentialResponse({ credential: `header.${mockPayload}.signature` });
            }
        }

        // لۆگینی ئەدمین
        document.getElementById('adminLoginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const err = document.getElementById('loginErrMsg');
            err.style.display = 'none';

            const res = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    username: document.getElementById('adminUser').value.trim(),
                    password: document.getElementById('adminPass').value.trim()
                })
            });
            const data = await res.json();
            if (res.ok) {
                currentUser = data.user;
                showApp();
            } else {
                err.textContent = data.message;
                err.style.display = 'block';
            }
        });

        async function logout() {
            await fetch('/api/auth/logout', { method: 'POST' });
            location.reload();
        }

        // ئامارەکان
        async function loadDashboard() {
            const res = await fetch('/api/dashboard/stats');
            const data = await res.json();
            document.getElementById('statDebt').textContent = Number(data.total_debt).toLocaleString() + " د.ع";
            document.getElementById('statPaid').textContent = Number(data.total_paid).toLocaleString() + " د.ع";
            document.getElementById('statRem').textContent = Number(data.total_remaining).toLocaleString() + " د.ع";
        }

        // پێشنیارەکانی ناوی کڕیار
        async function loadCustomerSuggestions() {
            const res = await fetch('/api/customers/suggestions');
            customerSuggestionsList = await res.json();
            const dl = document.getElementById('custSuggestions');
            dl.innerHTML = '';
            customerSuggestionsList.forEach(c => {
                const opt = document.createElement('option');
                opt.value = c.name;
                dl.appendChild(opt);
            });
        }

        document.getElementById('custName').addEventListener('input', (e) => {
            const match = customerSuggestionsList.find(c => c.name.toLowerCase() === e.target.value.toLowerCase());
            if (match && match.phone) {
                document.getElementById('custPhone').value = match.phone;
            }
        });

        // خشتەی قەرزەکان
        async function loadDebts() {
            const search = document.getElementById('searchInput').value;
            const res = await fetch(`/api/debts?search=${encodeURIComponent(search)}`);
            const debts = await res.json();

            const tbody = document.getElementById('debtsBody');
            tbody.innerHTML = '';

            const statusMap = {
                paid: { label: 'تەواوبوو', cls: 'badge-paid' },
                overdue: { label: 'دواکەوتوو', cls: 'badge-overdue' },
                pending: { label: 'نەدراوە', cls: 'badge-pending' },
                partial: { label: 'بەشەکی دراوە', cls: 'badge-pending' }
            };

            debts.forEach(d => {
                const s = statusMap[d.status] || { label: d.status, cls: 'badge-pending' };
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td style="color: var(--text-muted);">#${d.id}</td>
                    <td style="font-weight: 800;">${d.customer_name}</td>
                    <td>${d.phone || '-'}</td>
                    <td>${Number(d.total_amount).toLocaleString()}</td>
                    <td style="color: var(--accent-success);">${Number(d.paid_amount).toLocaleString()}</td>
                    <td style="color: var(--accent-danger); font-weight: 800;">${Number(d.remaining_amount).toLocaleString()}</td>
                    <td>${d.due_date}</td>
                    <td><span class="badge-status ${s.cls}">${s.label}</span></td>
                    <td>
                        <div style="display: flex; gap: 6px;">
                            ${d.remaining_amount > 0 ? `
                                <button class="btn-action" style="padding: 4px 8px; font-size: 11px; background: var(--accent-success); color: #fff;" onclick="openPayModal(${d.id}, '${d.customer_name}')">واسڵکردن</button>
                            ` : ''}
                            <button class="btn-action" style="padding: 4px 8px; font-size: 11px; background: var(--surface-glass); border: 1px solid var(--border-glass); color: var(--accent-danger);" onclick="deleteDebt(${d.id})">
                                <i class="fa-solid fa-trash"></i>
                            </button>
                        </div>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }

        // تۆمارکردنی قەرزی نوێ
        document.getElementById('debtForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const res = await fetch('/api/debts', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    customer_name: document.getElementById('custName').value.trim(),
                    phone: document.getElementById('custPhone').value.trim(),
                    total_amount: document.getElementById('custAmount').value,
                    due_date: document.getElementById('custDueDate').value
                })
            });
            if (res.ok) {
                closeModal('debtModal');
                document.getElementById('debtForm').reset();
                loadCustomerSuggestions();
                loadDashboard();
                loadDebts();
            }
        });

        // نوێکردنەوەی پرۆفایل
        document.getElementById('profileForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData();
            formData.append('full_name', document.getElementById('profileName').value);
            formData.append('bio', document.getElementById('profileBio').value);
            const file = document.getElementById('avatarInput').files[0];
            if (file) formData.append('avatar', file);

            const res = await fetch('/api/profile/update', { method: 'POST', body: formData });
            const data = await res.json();
            if (res.ok) {
                currentUser = data.user;
                updateProfileUI();
                closeModal('profileModal');
            }
        });

        document.getElementById('avatarInput').addEventListener('change', (e) => {
            if (e.target.files && e.target.files[0]) {
                const reader = new FileReader();
                reader.onload = (ev) => document.getElementById('profileImgPreview').src = ev.target.result;
                reader.readAsDataURL(e.target.files[0]);
            }
        });

        function openPayModal(id, name) {
            document.getElementById('payDebtId').value = id;
            document.getElementById('payTitle').textContent = `واڵسکردن بۆ: ${name}`;
            document.getElementById('payModal').style.display = 'flex';
        }

        document.getElementById('payForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const id = document.getElementById('payDebtId').value;
            const res = await fetch(`/api/debts/${id}/payments`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ amount: document.getElementById('payAmount').value })
            });
            if (res.ok) {
                closeModal('payModal');
                loadDashboard();
                loadDebts();
            }
        });

        async function deleteDebt(id) {
            if (confirm('سڕینەوەی ئەم قەرزە؟')) {
                await fetch(`/api/debts/${id}`, { method: 'DELETE' });
                loadDashboard();
                loadDebts();
            }
        }

        function openDebtModal() { document.getElementById('debtModal').style.display = 'flex'; }
        function openProfileModal() { document.getElementById('profileModal').style.display = 'flex'; }
        function closeModal(id) { document.getElementById(id).style.display = 'none'; }
    </script>
</body>
</html>
