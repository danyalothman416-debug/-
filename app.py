<!DOCTYPE html>
<html lang="ckb" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>سیستەمی قەرز | پڕۆژەی دانیال</title>
    <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;600;700;800;900&family=Plus+Jakarta+Sans:wght@700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

    <style>
        :root {
            --bg-dark: #07090e;
            --surface: rgba(18, 24, 38, 0.85);
            --surface-glass: rgba(255, 255, 255, 0.04);
            --border-glass: rgba(255, 255, 255, 0.08);
            --accent-blue: #0070f3;
            --accent-purple: #7928ca;
            --accent-danger: #ef4444;
            --accent-success: #10b981;
            --accent-warning: #f59e0b;
            --text-main: #ffffff;
            --text-muted: #8e95a5;
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
            position: relative;
        }

        /* ١. بەشی چوونەژوورەوە لەگەڵ ڤیدیۆ و ئەنیمەیشن */
        .auth-wrapper {
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            z-index: 1000;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            background: #000;
        }

        .video-bg {
            position: absolute;
            top: 50%; left: 50%;
            min-width: 100%; min-height: 100%;
            width: auto; height: auto;
            transform: translate(-50%, -50%);
            object-fit: cover;
            filter: brightness(0.35) contrast(1.15) saturate(1.2);
            z-index: 0;
        }

        .auth-overlay {
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background: radial-gradient(circle, rgba(0,0,0,0.2) 0%, rgba(7,9,14,0.85) 100%);
            z-index: 1;
        }

        .auth-box {
            position: relative;
            z-index: 2;
            width: 100%;
            max-width: 440px;
            padding: 44px 36px;
            background: rgba(14, 18, 28, 0.65);
            backdrop-filter: blur(28px);
            -webkit-backdrop-filter: blur(28px);
            border: 1px solid var(--border-glass);
            border-radius: 28px;
            box-shadow: 0 30px 60px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.1);
            animation: zoomFade 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }

        @keyframes zoomFade {
            from { opacity: 0; transform: scale(0.92) translateY(20px); }
            to { opacity: 1; transform: scale(1) translateY(0); }
        }

        .brand-icon-anim {
            width: 72px;
            height: 72px;
            margin: 0 auto 16px;
            border-radius: 22px;
            background: linear-gradient(135deg, var(--accent-purple), var(--accent-blue));
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 32px;
            color: #fff;
            box-shadow: 0 12px 28px rgba(121, 40, 202, 0.4);
            animation: pulseGlow 4s infinite alternate ease-in-out;
        }

        @keyframes pulseGlow {
            0% { transform: scale(1); box-shadow: 0 0 20px rgba(121, 40, 202, 0.4); }
            100% { transform: scale(1.06); box-shadow: 0 0 35px rgba(0, 112, 243, 0.7); }
        }

        /* بەشی ناوەوەی سیستەم */
        .app-container {
            display: none;
            min-height: 100vh;
            flex-direction: column;
            animation: fadeIn 0.6s ease forwards;
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        .navbar {
            position: sticky;
            top: 0;
            z-index: 100;
            background: rgba(11, 15, 25, 0.8);
            backdrop-filter: blur(20px);
            border-bottom: 1px solid var(--border-glass);
            padding: 14px 28px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .user-profile-badge {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 6px 14px;
            border-radius: 40px;
            background: var(--surface-glass);
            border: 1px solid var(--border-glass);
            cursor: pointer;
            transition: var(--transition);
        }

        .user-profile-badge:hover {
            background: rgba(255,255,255,0.08);
            transform: translateY(-2px);
        }

        .user-avatar-mini {
            width: 38px;
            height: 38px;
            border-radius: 50%;
            object-fit: cover;
            border: 2px solid var(--accent-blue);
        }

        .main-layout {
            max-width: 1240px;
            width: 100%;
            margin: 28px auto;
            padding: 0 20px;
            flex: 1;
        }

        /* کارتەکانی داشبۆرد */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 20px;
            margin-bottom: 28px;
        }

        .stat-card {
            background: var(--surface);
            border: 1px solid var(--border-glass);
            border-radius: 20px;
            padding: 22px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: relative;
            overflow: hidden;
            transition: var(--transition);
        }

        .stat-card:hover {
            transform: translateY(-4px);
            border-color: rgba(255,255,255,0.18);
        }

        .stat-card::after {
            content: '';
            position: absolute;
            top: 0; right: 0; width: 4px; height: 100%;
        }

        .card-blue::after { background: var(--accent-blue); }
        .card-green::after { background: var(--accent-success); }
        .card-red::after { background: var(--accent-danger); }
        .card-yellow::after { background: var(--accent-warning); }

        .stat-card h4 { font-size: 13px; color: var(--text-muted); margin-bottom: 6px; }
        .stat-card .val { font-size: 24px; font-weight: 800; }

        /* کۆنترۆڵەکان و دوگمەکان */
        .controls-bar {
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

        .search-field {
            position: relative;
            min-width: 280px;
        }

        .search-field input {
            width: 100%;
            padding: 11px 40px 11px 16px;
            background: rgba(0,0,0,0.3);
            border: 1px solid var(--border-glass);
            border-radius: 12px;
            color: #fff;
            outline: none;
            font-size: 13px;
        }

        .search-field i {
            position: absolute;
            right: 14px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-muted);
        }

        .btn-modern {
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

        .btn-gradient {
            background: linear-gradient(135deg, var(--accent-purple), var(--accent-blue));
            color: #fff;
            box-shadow: 0 4px 14px rgba(0,112,243,0.3);
        }

        .btn-gradient:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0,112,243,0.5);
        }

        .btn-glass {
            background: var(--surface-glass);
            border: 1px solid var(--border-glass);
            color: var(--text-main);
        }

        .btn-glass:hover {
            background: rgba(255,255,255,0.1);
        }

        /* خشتە و تاگەکان */
        .table-panel {
            background: var(--surface);
            border: 1px solid var(--border-glass);
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
        }

        table {
            width: 100%;
            border-collapse: collapse;
            text-align: right;
            font-size: 13.5px;
        }

        th {
            background: rgba(0,0,0,0.25);
            padding: 16px 20px;
            color: var(--text-muted);
            font-weight: 600;
            border-bottom: 1px solid var(--border-glass);
        }

        td {
            padding: 16px 20px;
            border-bottom: 1px solid var(--border-glass);
        }

        tr:hover td {
            background: rgba(255,255,255,0.02);
        }

        .status-pill {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 11.5px;
            font-weight: 700;
        }

        .pill-paid { background: rgba(16, 185, 129, 0.15); color: var(--accent-success); }
        .pill-overdue { background: rgba(239, 68, 68, 0.15); color: var(--accent-danger); }
        .pill-pending { background: rgba(0, 112, 243, 0.15); color: var(--accent-blue); }
        .pill-partial { background: rgba(245, 158, 11, 0.15); color: var(--accent-warning); }

        /* مۆداڵەکان */
        .modal-screen {
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.7);
            backdrop-filter: blur(10px);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            padding: 16px;
        }

        .modal-body {
            background: #111624;
            border: 1px solid var(--border-glass);
            border-radius: 24px;
            width: 100%;
            max-width: 480px;
            padding: 28px;
            animation: modalSlide 0.35s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }

        @keyframes modalSlide {
            from { opacity: 0; transform: scale(0.95) translateY(15px); }
            to { opacity: 1; transform: scale(1) translateY(0); }
        }

        .input-box {
            margin-bottom: 16px;
        }

        .input-box label {
            display: block;
            margin-bottom: 7px;
            font-size: 12.5px;
            color: var(--text-muted);
            font-weight: 600;
        }

        .input-box input, .input-box select, .input-box textarea {
            width: 100%;
            padding: 11px 14px;
            background: rgba(0,0,0,0.3);
            border: 1px solid var(--border-glass);
            border-radius: 12px;
            color: #fff;
            outline: none;
            font-size: 13.5px;
            transition: var(--transition);
        }

        .input-box input:focus, .input-box textarea:focus {
            border-color: var(--accent-blue);
            box-shadow: 0 0 0 3px rgba(0,112,243,0.2);
        }
    </style>
</head>
<body>

    <!-- ١. بەشی چوونەژوورەوە بە دیزاینی ڤیدیۆی ئەڵقەیی -->
    <div class="auth-wrapper" id="authSection">
        <video class="video-bg" autoplay muted loop playsinline>
            <source src="https://assets.mixkit.co/videos/preview/mixkit-digital-animation-of-screens-with-graphs-and-data-31913-large.mp4" type="video/mp4">
        </video>
        <div class="auth-overlay"></div>

        <div class="auth-box">
            <div class="brand-icon-anim">
                <i class="fa-solid fa-cube"></i>
            </div>
            <h2 style="font-size: 24px; font-weight: 800; text-align: center; margin-bottom: 6px;">سیستەمی دانیال</h2>
            <p style="font-size: 13px; color: var(--text-muted); text-align: center; margin-bottom: 26px;">بەڕێوەبردنی قەرز و حسابی دارایی</p>

            <form id="loginForm">
                <div class="input-box">
                    <label>ناوی بەکارهێنەر</label>
                    <input type="text" id="loginUser" required placeholder="admin">
                </div>
                <div class="input-box">
                    <label>وشەی نهێنی</label>
                    <input type="password" id="loginPass" required placeholder="••••••••">
                </div>
                <button type="submit" class="btn-modern btn-gradient" style="width: 100%; justify-content: center; padding: 13px; margin-top: 10px;">
                    چوونەژوورەوە
                </button>
            </form>
            <p id="loginError" style="color: var(--accent-danger); font-size: 13px; text-align: center; margin-top: 14px; display: none;"></p>
        </div>
    </div>

    <!-- ٢. ناوەڕۆکی سەرەکی بەرنامە -->
    <div class="app-container" id="appContainer">
        <!-- ناڤبار -->
        <header class="navbar">
            <div style="display: flex; align-items: center; gap: 10px; font-weight: 800; font-size: 18px;">
                <i class="fa-solid fa-wallet" style="color: var(--accent-blue);"></i>
                سیستەمی قەرز و حسابات
            </div>

            <!-- پرۆفایلی بەکارهێنەر لەگەڵ بایۆ -->
            <div class="user-profile-badge" onclick="openProfileModal()">
                <img src="" id="userNavAvatar" class="user-avatar-mini" alt="avatar">
                <div style="text-align: right;">
                    <div id="userNavName" style="font-weight: 700; font-size: 13px;"></div>
                    <div id="userNavBio" style="font-size: 11px; color: var(--text-muted); max-width: 140px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;"></div>
                </div>
                <i class="fa-solid fa-angle-down" style="font-size: 12px; color: var(--text-muted);"></i>
            </div>
        </header>

        <main class="main-layout">
            <!-- ئامارەکان -->
            <div class="stats-grid">
                <div class="stat-card card-blue">
                    <div>
                        <h4>کۆی گشتی قەرز</h4>
                        <div class="val" id="statTotalDebt">0</div>
                    </div>
                    <i class="fa-solid fa-sack-dollar" style="font-size: 28px; color: var(--accent-blue);"></i>
                </div>

                <div class="stat-card card-green">
                    <div>
                        <h4>کۆی پارەی واسڵکراو</h4>
                        <div class="val" style="color: var(--accent-success);" id="statTotalPaid">0</div>
                    </div>
                    <i class="fa-solid fa-circle-check" style="font-size: 28px; color: var(--accent-success);"></i>
                </div>

                <div class="stat-card card-red">
                    <div>
                        <h4>کۆی پارەی ماوە</h4>
                        <div class="val" style="color: var(--accent-danger);" id="statTotalRemaining">0</div>
                    </div>
                    <i class="fa-solid fa-hand-holding-dollar" style="font-size: 28px; color: var(--accent-danger);"></i>
                </div>

                <div class="stat-card card-yellow">
                    <div>
                        <h4>قەرزی دواکەوتوو</h4>
                        <div class="val" style="color: var(--accent-warning);" id="statOverdue">0</div>
                    </div>
                    <i class="fa-solid fa-clock-rotate-left" style="font-size: 28px; color: var(--accent-warning);"></i>
                </div>
            </div>

            <!-- کۆنترۆڵەکان -->
            <div class="controls-bar">
                <div class="search-field">
                    <i class="fa-solid fa-magnifying-glass"></i>
                    <input type="text" id="searchInput" placeholder="گەڕان بەپێی ناوی کەسەکە یان مۆبایل..." oninput="loadDebts()">
                </div>

                <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                    <button class="btn-modern btn-gradient" onclick="openAddDebtModal()">
                        <i class="fa-solid fa-plus"></i> قەرزی نوێ
                    </button>
                    <button class="btn-modern btn-glass" onclick="location.href='/api/reports/export-excel'">
                        <i class="fa-solid fa-file-excel"></i> هەناردەکردن بۆ Excel
                    </button>
                    <button class="btn-modern btn-glass" onclick="logout()">
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
                            <th>ژمارەی مۆبایل</th>
                            <th>کۆی قەرز</th>
                            <th>بڕی دراو</th>
                            <th>بڕی ماوە</th>
                            <th>بەرواری دانەوە</th>
                            <th>دۆخ</th>
                            <th>کردارەکان</th>
                        </tr>
                    </thead>
                    <tbody id="debtsTableBody"></tbody>
                </table>
            </div>
        </main>
    </div>

    <!-- مۆداڵی زیادکردنی قەرزی نوێ (ناوی کەسەکە بە هەڵبژاردن و دەستکرد) -->
    <div class="modal-screen" id="debtModal">
        <div class="modal-body">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h3 style="font-size: 17px;">تۆمارکردنی قەرزی نوێ</h3>
                <i class="fa-solid fa-xmark" style="cursor: pointer;" onclick="closeModal('debtModal')"></i>
            </div>
            <form id="addDebtForm">
                <div class="input-box">
                    <label>ناوی کەسی قەرزەکە * (دەتوانیت هەڵیبژێریت یان ناوی نوێ بنووسیت)</label>
                    <input type="text" id="custNameInput" list="customerSuggestions" required placeholder="ناوی کڕیار بنووسە..." autocomplete="off">
                    <datalist id="customerSuggestions"></datalist>
                </div>
                <div class="input-box">
                    <label>ژمارەی مۆبایل</label>
                    <input type="text" id="custPhoneInput" placeholder="0750...">
                </div>
                <div class="input-box">
                    <label>بڕی قەرز (دینار) *</label>
                    <input type="number" id="custAmountInput" required placeholder="نموونە: 150000">
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                    <div class="input-box">
                        <label>بەرواری قەرز</label>
                        <input type="date" id="custDebtDate">
                    </div>
                    <div class="input-box">
                        <label>بەرواری دانەوە *</label>
                        <input type="date" id="custDueDate" required>
                    </div>
                </div>
                <div class="input-box">
                    <label>تێبینی</label>
                    <textarea id="custNoteInput" rows="2" placeholder="کەلوپەل، هۆکار..."></textarea>
                </div>
                <button type="submit" class="btn-modern btn-gradient" style="width: 100%; justify-content: center; padding: 12px; margin-top: 10px;">
                    پاشەکەوتکردنی قەرز
                </button>
            </form>
        </div>
    </div>

    <!-- مۆداڵی پرۆفایل و بایۆ و گۆڕینی وێنە -->
    <div class="modal-screen" id="profileModal">
        <div class="modal-body">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h3 style="font-size: 17px;">دەستکاریکردنی پرۆفایل</h3>
                <i class="fa-solid fa-xmark" style="cursor: pointer;" onclick="closeModal('profileModal')"></i>
            </div>
            <form id="profileForm">
                <div style="text-align: center; margin-bottom: 18px;">
                    <img src="" id="profilePreviewImg" style="width: 80px; height: 80px; border-radius: 50%; object-fit: cover; border: 2px solid var(--accent-blue); margin-bottom: 8px;">
                    <div>
                        <button type="button" class="btn-modern btn-glass" style="font-size: 11px; padding: 6px 12px;" onclick="document.getElementById('avatarFileInput').click()">
                            <i class="fa-solid fa-camera"></i> گۆڕینی وێنە
                        </button>
                        <input type="file" id="avatarFileInput" accept="image/*" style="display: none;">
                    </div>
                </div>

                <div class="input-box">
                    <label>ناوی تەواو</label>
                    <input type="text" id="profileFullName" required>
                </div>

                <div class="input-box">
                    <label>بایۆ (دەربارەی من)</label>
                    <textarea id="profileBio" rows="3" placeholder="ڕوونکردنەوەیەک دەربارەی بەرپرسیارێتیت..."></textarea>
                </div>

                <button type="submit" class="btn-modern btn-gradient" style="width: 100%; justify-content: center; padding: 12px;">
                    نوێکردنەوەی زانیارییەکان
                </button>
            </form>
        </div>
    </div>

    <!-- مۆداڵی واسڵکردنی پارە -->
    <div class="modal-screen" id="payModal">
        <div class="modal-body">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <h3 id="payModalTitle" style="font-size: 16px;">واڵسکردنی پارە</h3>
                <i class="fa-solid fa-xmark" style="cursor: pointer;" onclick="closeModal('payModal')"></i>
            </div>
            <p id="payModalRemainingLabel" style="font-size: 13px; color: var(--accent-danger); margin-bottom: 14px; font-weight: 700;"></p>
            <form id="paymentForm">
                <input type="hidden" id="payDebtId">
                <div class="input-box">
                    <label>بڕی پارەی دراو (دینار) *</label>
                    <input type="number" id="payAmountInput" required placeholder="بڕی پارە بنووسە...">
                </div>
                <div class="input-box">
                    <label>تێبینی وەسڵ</label>
                    <input type="text" id="payNoteInput" placeholder="وەسڵی ژمارە، هتد...">
                </div>
                <button type="submit" class="btn-modern" style="width: 100%; justify-content: center; background: var(--accent-success); color: #fff; padding: 12px;">
                    تەواوکردنی وەرگرتن
                </button>
            </form>
        </div>
    </div>

    <script>
        let currentUser = null;
        let customerDataList = [];

        window.addEventListener('DOMContentLoaded', () => {
            document.getElementById('custDebtDate').value = new Date().toISOString().split('T')[0];
            checkAuth();
        });

        async function checkAuth() {
            try {
                const res = await fetch('/api/auth/me');
                const data = await res.json();
                if (data.logged_in) {
                    currentUser = data.user;
                    initApp();
                } else {
                    document.getElementById('authSection').style.display = 'flex';
                    document.getElementById('appContainer').style.display = 'none';
                }
            } catch (e) {
                console.error(e);
            }
        }

        function initApp() {
            document.getElementById('authSection').style.display = 'none';
            document.getElementById('appContainer').style.display = 'flex';
            updateProfileUI();
            loadDashboard();
            loadCustomerSuggestions();
            loadDebts();
        }

        function updateProfileUI() {
            document.getElementById('userNavName').textContent = currentUser.full_name;
            document.getElementById('userNavBio').textContent = currentUser.bio || 'بێ بایۆ';
            document.getElementById('userNavAvatar').src = currentUser.avatar;
            document.getElementById('profilePreviewImg').src = currentUser.avatar;
            document.getElementById('profileFullName').value = currentUser.full_name;
            document.getElementById('profileBio').value = currentUser.bio || '';
        }

        // هێنانی ناوی کڕیارەکان بۆ ئاسان هەڵبژاردن و خۆکار پڕکردنەوەی ژمارە
        async function loadCustomerSuggestions() {
            const res = await fetch('/api/customers/suggestions');
            customerDataList = await res.json();
            const dl = document.getElementById('customerSuggestions');
            dl.innerHTML = '';
            customerDataList.forEach(c => {
                const opt = document.createElement('option');
                opt.value = c.name;
                dl.appendChild(opt);
            });
        }

        // کاتێک ناوەکەی هەڵبژارد، مۆبایلەکەی خۆی بنووسێت
        document.getElementById('custNameInput').addEventListener('input', (e) => {
            const match = customerDataList.find(c => c.name.toLowerCase() === e.target.value.toLowerCase());
            if (match && match.phone) {
                document.getElementById('custPhoneInput').value = match.phone;
            }
        });

        // لۆگین
        document.getElementById('loginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const err = document.getElementById('loginError');
            err.style.display = 'none';

            const res = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    username: document.getElementById('loginUser').value.trim(),
                    password: document.getElementById('loginPass').value.trim()
                })
            });
            const data = await res.json();
            if (res.ok) {
                currentUser = data.user;
                initApp();
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
            document.getElementById('statTotalDebt').textContent = Number(data.total_debt).toLocaleString() + " د.ع";
            document.getElementById('statTotalPaid').textContent = Number(data.total_paid).toLocaleString() + " د.ع";
            document.getElementById('statTotalRemaining').textContent = Number(data.total_remaining).toLocaleString() + " د.ع";
            document.getElementById('statOverdue').textContent = data.overdue_count;
        }

        // خشتەی قەرزەکان
        async function loadDebts() {
            const search = document.getElementById('searchInput').value;
            const res = await fetch(`/api/debts?search=${encodeURIComponent(search)}`);
            const debts = await res.json();

            const tbody = document.getElementById('debtsTableBody');
            tbody.innerHTML = '';

            const statusMap = {
                paid: { label: 'تەواوبوو', cls: 'pill-paid' },
                overdue: { label: 'دواکەوتوو', cls: 'pill-overdue' },
                partial: { label: 'بەشەکی دراوە', cls: 'pill-partial' },
                pending: { label: 'نەدراوە', cls: 'pill-pending' }
            };

            debts.forEach(d => {
                const s = statusMap[d.status] || { label: d.status, cls: 'pill-pending' };
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td style="font-weight: 700; color: var(--text-muted);">#${d.id}</td>
                    <td style="font-weight: 800;">${d.customer_name}</td>
                    <td>${d.phone || '-'}</td>
                    <td>${Number(d.total_amount).toLocaleString()}</td>
                    <td style="color: var(--accent-success); font-weight: 700;">${Number(d.paid_amount).toLocaleString()}</td>
                    <td style="color: var(--accent-danger); font-weight: 800;">${Number(d.remaining_amount).toLocaleString()}</td>
                    <td>${d.due_date}</td>
                    <td><span class="status-pill ${s.cls}">${s.label}</span></td>
                    <td>
                        <div style="display: flex; gap: 8px;">
                            ${d.remaining_amount > 0 ? `
                                <button class="btn-modern" style="padding: 5px 10px; font-size: 11px; background: var(--accent-success); color: #fff;" onclick="openPayModal(${d.id}, '${d.customer_name}',${d.remaining_amount})">
                                    واسڵکردن
                                </button>
                            ` : ''}
                            <button class="btn-modern btn-glass" style="padding: 5px 10px; font-size: 11px; color: var(--accent-danger);" onclick="deleteDebt(${d.id})">
                                <i class="fa-solid fa-trash"></i>
                            </button>
                        </div>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }

        // پاشەکەوتکردنی قەرزی نوێ
        document.getElementById('addDebtForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const payload = {
                customer_name: document.getElementById('custNameInput').value.trim(),
                phone: document.getElementById('custPhoneInput').value.trim(),
                total_amount: document.getElementById('custAmountInput').value,
                debt_date: document.getElementById('custDebtDate').value,
                due_date: document.getElementById('custDueDate').value,
                note: document.getElementById('custNoteInput').value.trim()
            };

            const res = await fetch('/api/debts', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if (res.ok) {
                closeModal('debtModal');
                document.getElementById('addDebtForm').reset();
                loadCustomerSuggestions();
                loadDashboard();
                loadDebts();
            } else {
                alert(data.message || 'هەڵەیەک هەیە');
            }
        });

        // واسڵکردنی پارە
        function openPayModal(id, name, remaining) {
            document.getElementById('payDebtId').value = id;
            document.getElementById('payModalTitle').textContent = `واسڵکردن بۆ: ${name}`;
            document.getElementById('payModalRemainingLabel').textContent = `بڕی پارەی ماوە: ${Number(remaining).toLocaleString()} دینار`;
            document.getElementById('payAmountInput').max = remaining;
            document.getElementById('payModal').style.display = 'flex';
        }

        document.getElementById('paymentForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const debtId = document.getElementById('payDebtId').value;
            const res = await fetch(`/api/debts/${debtId}/payments`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    amount: document.getElementById('payAmountInput').value,
                    note: document.getElementById('payNoteInput').value.trim()
                })
            });
            if (res.ok) {
                closeModal('payModal');
                document.getElementById('paymentForm').reset();
                loadDashboard();
                loadDebts();
            }
        });

        // نوێکردنەوەی پرۆفایل و وێنە
        document.getElementById('profileForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData();
            formData.append('full_name', document.getElementById('profileFullName').value);
            formData.append('bio', document.getElementById('profileBio').value);

            const file = document.getElementById('avatarFileInput').files[0];
            if (file) formData.append('avatar', file);

            const res = await fetch('/api/profile/update', {
                method: 'POST',
                body: formData
            });
            const data = await res.json();
            if (res.ok) {
                currentUser = data.user;
                updateProfileUI();
                closeModal('profileModal');
            }
        });

        document.getElementById('avatarFileInput').addEventListener('change', (e) => {
            if (e.target.files && e.target.files[0]) {
                const reader = new FileReader();
                reader.onload = (ev) => document.getElementById('profilePreviewImg').src = ev.target.result;
                reader.readAsDataURL(e.target.files[0]);
            }
        });

        async function deleteDebt(id) {
            if (confirm('ئایا دڵنیایت لە سڕینەوەی ئەم قەرزە؟')) {
                await fetch(`/api/debts/${id}`, { method: 'DELETE' });
                loadDashboard();
                loadDebts();
            }
        }

        function openAddDebtModal() { document.getElementById('debtModal').style.display = 'flex'; }
        function openProfileModal() { document.getElementById('profileModal').style.display = 'flex'; }
        function closeModal(id) { document.getElementById(id).style.display = 'none'; }
    </script>
</body>
</html>
