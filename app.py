<!DOCTYPE html>
<html lang="ckb" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>سیستەمی دارایی دانیال</title>
    
    <!-- فۆنتی فەرمیی کوردی و لاتینی هاوشێوەی iOS -->
    <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <!-- ڕێکخستنی تایبەتی مۆبایل بۆ ئەوەی بە تەواوی وەک ئەپی ئایفۆن دەربکەوێت -->
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="Danyal App">

    <style>
        :root {
            --ios-bg: #000000;
            --ios-card: #12141c;
            --ios-card-border: rgba(255, 255, 255, 0.08);
            --ios-blue: #0A84FF;
            --ios-green: #30D158;
            --ios-red: #FF453A;
            --ios-orange: #FF9F0A;
            --ios-purple: #BF5AF2;
            --ios-text: #FFFFFF;
            --ios-muted: #8E8E93;
            --ios-sub: #1C1C1E;
            --safe-top: env(safe-area-inset-top, 20px);
            --safe-bottom: env(safe-area-inset-bottom, 20px);
            --transition: all 0.25s cubic-bezier(0.2, 0.8, 0.2, 1);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Vazirmatn', -apple-system, BlinkMacSystemFont, sans-serif;
            -webkit-tap-highlight-color: transparent;
        }

        body {
            background-color: var(--ios-bg);
            color: var(--ios-text);
            min-height: 100vh;
            padding-top: var(--safe-top);
            padding-bottom: calc(var(--safe-bottom) + 85px);
            overflow-x: hidden;
            user-select: none;
        }

        /* بەشی دەستپێکی سینەمایی */
        #splashScreen {
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            background: #000;
            z-index: 99999;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: opacity 0.5s ease;
        }

        .splash-video {
            position: absolute;
            top: 50%; left: 50%;
            min-width: 100%; min-height: 100%;
            transform: translate(-50%, -50%);
            object-fit: cover;
            filter: brightness(0.35);
        }

        .splash-content {
            position: relative;
            z-index: 2;
            text-align: center;
            padding: 24px;
        }

        .splash-logo {
            width: 88px; height: 88px;
            margin: 0 auto 16px;
            border-radius: 24px;
            background: linear-gradient(135deg, var(--ios-purple), var(--ios-blue));
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 38px;
            box-shadow: 0 10px 30px rgba(10, 132, 255, 0.5);
        }

        /* پەڕەی چوونەژوورەوەی iOS */
        .login-wrapper {
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 10000;
            background: #000;
            padding: 20px;
        }

        .login-card {
            width: 100%;
            max-width: 380px;
            background: var(--ios-card);
            border: 1px solid var(--ios-card-border);
            border-radius: 28px;
            padding: 32px 24px;
            text-align: center;
            box-shadow: 0 20px 40px rgba(0,0,0,0.8);
        }

        /* سەرپەڕەی مۆبایل (iOS Header) */
        .ios-header {
            position: sticky;
            top: 0;
            z-index: 100;
            background: rgba(0, 0, 0, 0.75);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            padding: 12px 18px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }

        .ios-profile {
            display: flex;
            align-items: center;
            gap: 12px;
            cursor: pointer;
        }

        .ios-avatar {
            width: 42px;
            height: 42px;
            border-radius: 50%;
            object-fit: cover;
            border: 2px solid var(--ios-blue);
        }

        .ios-greeting h2 {
            font-size: 15px;
            font-weight: 800;
        }

        .ios-greeting p {
            font-size: 11px;
            color: var(--ios-muted);
        }

        /* ناوەڕۆکی پەڕەکان */
        .app-view {
            display: none;
            padding: 0 16px;
            max-width: 600px;
            margin: 0 auto;
        }

        .tab-page {
            display: none;
            animation: fadeIn 0.3s ease;
        }

        .tab-page.active { display: block; }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(8px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* کارتەکانی باڵانس لەسەر ستایلی Apple Wallet */
        .wallet-card {
            background: linear-gradient(135deg, #182030, #0f1420);
            border: 1px solid var(--ios-card-border);
            border-radius: 24px;
            padding: 22px;
            margin-top: 14px;
            margin-bottom: 20px;
            box-shadow: 0 14px 28px rgba(0,0,0,0.4);
            position: relative;
            overflow: hidden;
        }

        .wallet-card::before {
            content: '';
            position: absolute;
            top: -40px; right: -40px;
            width: 140px; height: 140px;
            background: radial-gradient(circle, rgba(10, 132, 255, 0.25), transparent 70%);
            border-radius: 50%;
        }

        .wallet-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            font-size: 13px;
            color: var(--ios-muted);
        }

        .wallet-balance {
            font-size: 28px;
            font-weight: 900;
            color: #fff;
            margin-bottom: 16px;
            letter-spacing: -0.5px;
        }

        .wallet-sub-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            padding-top: 14px;
            border-top: 1px solid rgba(255,255,255,0.08);
        }

        .wallet-sub-item span { font-size: 11px; color: var(--ios-muted); display: block; }
        .wallet-sub-item strong { font-size: 14px; font-weight: 700; }

        /* شریتی فلتەری ستایلی iOS (Segmented Control) */
        .segmented-control {
            display: flex;
            background: var(--ios-card);
            padding: 4px;
            border-radius: 14px;
            margin-bottom: 18px;
            border: 1px solid var(--ios-card-border);
        }

        .segment-btn {
            flex: 1;
            padding: 8px 4px;
            border: none;
            background: transparent;
            color: var(--ios-muted);
            font-size: 12px;
            font-weight: 700;
            border-radius: 10px;
            cursor: pointer;
            transition: var(--transition);
        }

        .segment-btn.active {
            background: rgba(255,255,255,0.12);
            color: #fff;
        }

        /* کارتەکانی قەرز (iOS List Cards) لە جیاتی خشتە */
        .debt-card {
            background: var(--ios-card);
            border: 1px solid var(--ios-card-border);
            border-radius: 20px;
            padding: 16px;
            margin-bottom: 14px;
            transition: var(--transition);
            box-shadow: 0 4px 12px rgba(0,0,0,0.25);
        }

        .debt-card:active {
            transform: scale(0.98);
        }

        .debt-card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }

        .customer-info {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .customer-avatar {
            width: 40px; height: 40px;
            border-radius: 14px;
            background: linear-gradient(135deg, rgba(10, 132, 255, 0.2), rgba(191, 90, 242, 0.2));
            color: var(--ios-blue);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            font-size: 15px;
        }

        .customer-name {
            font-size: 14px;
            font-weight: 800;
        }

        .badge-status {
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 700;
        }

        .badge-paid { background: rgba(48, 209, 88, 0.15); color: var(--ios-green); }
        .badge-overdue { background: rgba(255, 69, 58, 0.15); color: var(--ios-red); }
        .badge-pending { background: rgba(10, 132, 255, 0.15); color: var(--ios-blue); }

        .debt-details-row {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            background: rgba(0,0,0,0.3);
            padding: 10px 14px;
            border-radius: 14px;
            margin-bottom: 12px;
        }

        .amount-remaining {
            font-size: 18px;
            font-weight: 900;
            color: var(--ios-red);
        }

        .debt-card-actions {
            display: flex;
            gap: 8px;
        }

        .action-pill {
            flex: 1;
            padding: 8px 12px;
            border-radius: 12px;
            border: none;
            font-size: 12px;
            font-weight: 700;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            text-decoration: none;
        }

        .action-pay { background: var(--ios-green); color: #000; }
        .action-wa { background: rgba(37, 211, 102, 0.15); color: var(--ios-green); }
        .action-del { background: rgba(255, 69, 58, 0.15); color: var(--ios-red); flex: 0 0 40px; }

        /* شریتی خوارەوەی مۆبایل (Bottom Tab Bar) */
        .ios-tab-bar {
            position: fixed;
            bottom: 0; left: 0; width: 100vw;
            background: rgba(18, 20, 28, 0.85);
            backdrop-filter: blur(24px);
            -webkit-backdrop-filter: blur(24px);
            border-top: 1px solid var(--ios-card-border);
            display: flex;
            align-items: center;
            justify-content: space-around;
            padding-bottom: var(--safe-bottom);
            padding-top: 8px;
            z-index: 1000;
        }

        .tab-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 4px;
            color: var(--ios-muted);
            text-decoration: none;
            font-size: 10px;
            font-weight: 600;
            cursor: pointer;
            transition: var(--transition);
            flex: 1;
        }

        .tab-item i { font-size: 19px; }
        .tab-item.active { color: var(--ios-blue); }

        /* دوگمەی دروستکردنی ناوەڕاست (+) */
        .tab-item.fab-tab {
            position: relative;
            top: -12px;
        }

        .fab-button {
            width: 48px; height: 48px;
            border-radius: 50%;
            background: linear-gradient(135deg, var(--ios-purple), var(--ios-blue));
            display: flex;
            align-items: center;
            justify-content: center;
            color: #fff;
            font-size: 20px;
            box-shadow: 0 8px 20px rgba(10, 132, 255, 0.45);
        }

        /* پەنجەرەی خلیسکاوەی خوارەوە (Bottom Sheet Modal) */
        .ios-modal {
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            background: rgba(0,0,0,0.7);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            z-index: 20000;
            display: none;
            align-items: flex-end;
            justify-content: center;
        }

        .ios-sheet {
            width: 100%;
            max-width: 500px;
            background: #161822;
            border-top: 1px solid var(--ios-card-border);
            border-radius: 28px 28px 0 0;
            padding: 20px 20px calc(var(--safe-bottom) + 20px);
            animation: slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
            max-height: 85vh;
            overflow-y: auto;
        }

        @keyframes slideUp {
            from { transform: translateY(100%); }
            to { transform: translateY(0); }
        }

        .sheet-drag {
            width: 40px; height: 5px;
            background: rgba(255,255,255,0.25);
            border-radius: 5px;
            margin: 0 auto 16px;
        }

        .sheet-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }

        .sheet-header h3 { font-size: 17px; font-weight: 800; }

        .form-group {
            margin-bottom: 14px;
        }

        .form-group label {
            display: block;
            margin-bottom: 6px;
            font-size: 12px;
            color: var(--ios-muted);
            font-weight: 600;
        }

        .form-group input, .form-group select, .form-group textarea {
            width: 100%;
            padding: 12px 14px;
            background: rgba(255,255,255,0.06);
            border: 1px solid var(--ios-card-border);
            border-radius: 14px;
            color: #fff;
            outline: none;
            font-size: 14px;
        }

        .btn-ios-submit {
            width: 100%;
            padding: 14px;
            border-radius: 16px;
            border: none;
            background: var(--ios-blue);
            color: #fff;
            font-size: 15px;
            font-weight: 800;
            cursor: pointer;
            margin-top: 10px;
            box-shadow: 0 4px 15px rgba(10, 132, 255, 0.3);
        }

        /* بەشی چاپ */
        #thermalReceipt {
            display: none;
            width: 80mm;
            padding: 15px;
            background: #fff;
            color: #000;
            font-size: 12px;
        }

        @media print {
            body * { visibility: hidden; }
            #thermalReceipt, #thermalReceipt * { visibility: visible; }
            #thermalReceipt { display: block !important; position: absolute; left: 0; top: 0; width: 80mm; }
        }
    </style>
</head>
<body>

    <!-- ١. پەڕەی دەستپێکی سینەمایی -->
    <div id="splashScreen">
        <video class="splash-video" autoplay muted loop playsinline>
            <source src="https://assets.mixkit.co/videos/preview/mixkit-digital-animation-of-screens-with-graphs-and-data-31913-large.mp4" type="video/mp4">
        </video>
        <div class="splash-content">
            <div class="splash-logo">
                <i class="fa-solid fa-cube" style="color: #fff;"></i>
            </div>
            <h1 style="font-size: 26px; font-weight: 900; margin-bottom: 6px;">سیستەمی دانیال</h1>
            <p style="color: #a1a1aa; font-size: 13px; margin-bottom: 24px;">بەڕێوەبردنی قەرز و حساباتی دارایی</p>
            <button class="btn-ios-submit" type="button" onclick="finishSplash()">
                دەستپێکردن <i class="fa-solid fa-arrow-left" style="margin-right: 6px;"></i>
            </button>
        </div>
    </div>

    <!-- ٢. پەڕەی چوونەژوورەوەی مۆبایل -->
    <div class="login-wrapper" id="loginWrapper">
        <div class="login-card">
            <div style="font-size: 36px; color: var(--ios-blue); margin-bottom: 12px;">
                <i class="fa-solid fa-vault"></i>
            </div>
            <h2 style="font-size: 20px; font-weight: 800; margin-bottom: 4px;">چوونەژوورەوە</h2>
            <p style="font-size: 12px; color: var(--ios-muted); margin-bottom: 24px;">تکایە ناوی بەکارهێنەر بنووسە</p>

            <form id="loginForm">
                <div class="form-group" style="text-align: right;">
                    <label>ناوی بەکارهێنەر</label>
                    <input type="text" id="loginUser" placeholder="admin" required>
                </div>
                <div class="form-group" style="text-align: right;">
                    <label>وشەی نهێنی</label>
                    <input type="password" id="loginPass" placeholder="••••••••" required>
                </div>
                <button type="submit" class="btn-ios-submit">چوونەژوورەوە</button>
            </form>
            <p id="loginErr" style="color: var(--ios-red); font-size: 12px; margin-top: 12px; display: none;"></p>
        </div>
    </div>

    <!-- ٣. ئەپی سەرەکیی iOS -->
    <div class="app-view" id="appView">
        <!-- سەرپەڕە -->
        <header class="ios-header">
            <div class="ios-profile" onclick="openProfileModal()">
                <img src="" id="userAvatar" class="ios-avatar" alt="Avatar">
                <div class="ios-greeting">
                    <h2 id="userName">دانیال ئیسماعیل</h2>
                    <p id="userBio">بەڕێوەبەری سیستەم</p>
                </div>
            </div>
            <div style="display: flex; gap: 8px;">
                <button class="action-pill" style="background: rgba(255,255,255,0.08); color: #fff; width: 38px; height: 38px; border-radius: 50%; padding:0;" onclick="openAuditModal()">
                    <i class="fa-solid fa-shield-halved"></i>
                </button>
                <button class="action-pill" style="background: rgba(255, 69, 58, 0.15); color: var(--ios-red); width: 38px; height: 38px; border-radius: 50%; padding:0;" onclick="logout()">
                    <i class="fa-solid fa-right-from-bracket"></i>
                </button>
            </div>
        </header>

        <!-- تابی ١: سەرەکی (Dashboard / Wallet) -->
        <div id="tabHome" class="tab-page active">
            <!-- کارتی باڵانسی دینار -->
            <div class="wallet-card">
                <div class="wallet-top">
                    <span>کۆی قەرزی ماوە لای خەڵک (IQD)</span>
                    <i class="fa-solid fa-wallet" style="color: var(--ios-blue);"></i>
                </div>
                <div class="wallet-balance" id="iqdRemaining" style="color: var(--ios-red);">0 د.ع</div>
                <div class="wallet-sub-grid">
                    <div class="wallet-sub-item">
                        <span>کۆی گشتی قەرز</span>
                        <strong id="iqdTotalDebt">0 د.ع</strong>
                    </div>
                    <div class="wallet-sub-item">
                        <span>کۆی پارەی واسڵکراو</span>
                        <strong id="iqdTotalPaid" style="color: var(--ios-green);">0 د.ع</strong>
                    </div>
                </div>
            </div>

            <!-- کارتی باڵانسی دۆلار -->
            <div class="wallet-card" style="background: linear-gradient(135deg, #13241b, #0d1712);">
                <div class="wallet-top">
                    <span>کۆی قەرزی ماوە لای خەڵک (USD)</span>
                    <i class="fa-solid fa-dollar-sign" style="color: var(--ios-green);"></i>
                </div>
                <div class="wallet-balance" id="usdRemaining" style="color: var(--ios-red);">$0</div>
                <div class="wallet-sub-grid">
                    <div class="wallet-sub-item">
                        <span>کۆی گشتی بە دۆلار</span>
                        <strong id="usdTotalDebt">$0</strong>
                    </div>
                    <div class="wallet-sub-item">
                        <span>واسڵکراو بە دۆلار</span>
                        <strong id="usdTotalPaid" style="color: var(--ios-green);">$0</strong>
                    </div>
                </div>
            </div>

            <!-- هێڵکاری سەرەکی -->
            <div style="background: var(--ios-card); border: 1px solid var(--ios-card-border); border-radius: 20px; padding: 18px; margin-bottom: 20px;">
                <h4 style="font-size: 13px; margin-bottom: 12px; color: var(--ios-muted);">
                    <i class="fa-solid fa-chart-column"></i> واسڵکردنی مانگانە
                </h4>
                <div style="height: 180px;"><canvas id="monthlyChart"></canvas></div>
            </div>
        </div>

        <!-- تابی ٢: قەرزەکان (Debts Cards List) -->
        <div id="tabDebts" class="tab-page">
            <!-- بەشی گەڕان -->
            <div style="margin-top: 14px; margin-bottom: 12px;">
                <input type="text" id="searchInput" placeholder="گەڕان بەپێی ناو یان مۆبایل..." oninput="loadDebts()"
                       style="width: 100%; padding: 12px 16px; background: var(--ios-card); border: 1px solid var(--ios-card-border); border-radius: 14px; color: #fff; font-size: 13px;">
            </div>

            <!-- شریتی فلتەر -->
            <div class="segmented-control">
                <button class="segment-btn active" onclick="filterStatus('all', this)">هەمووی</button>
                <button class="segment-btn" onclick="filterStatus('pending', this)">ماوە</button>
                <button class="segment-btn" onclick="filterStatus('overdue', this)">دواکەوتوو</button>
                <button class="segment-btn" onclick="filterStatus('paid', this)">دراوە</button>
            </div>

            <!-- لیستی کارتەکانی قەرز -->
            <div id="debtsCardsContainer"></div>
        </div>

        <!-- تابی ٣: ڕاپۆرت و گرافیک (Analytics) -->
        <div id="tabAnalytics" class="tab-page">
            <div style="margin-top: 16px;">
                <div style="background: var(--ios-card); border: 1px solid var(--ios-card-border); border-radius: 20px; padding: 18px; margin-bottom: 18px;">
                    <h4 style="font-size: 13px; margin-bottom: 12px; color: var(--ios-muted);">
                        <i class="fa-solid fa-chart-pie"></i> گەورەترین قەرزدارەکان
                    </h4>
                    <div style="height: 200px;"><canvas id="debtorsChart"></canvas></div>
                </div>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                    <button class="action-pill" style="background: var(--ios-card); border: 1px solid var(--ios-card-border); color: #fff; padding: 14px;" onclick="location.href='/api/reports/export-excel'">
                        <i class="fa-solid fa-file-excel" style="color: var(--ios-green);"></i> ئێکسڵ
                    </button>
                    <button class="action-pill" style="background: var(--ios-card); border: 1px solid var(--ios-card-border); color: #fff; padding: 14px;" onclick="location.href='/api/admin/backup'">
                        <i class="fa-solid fa-cloud-arrow-down" style="color: var(--ios-blue);"></i> باکئەپ
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- ٤. شریتی خوارەوەی مۆبایل (Bottom Tab Bar) -->
    <nav class="ios-tab-bar" id="iosTabBar" style="display: none;">
        <div class="tab-item active" onclick="switchTab('tabHome', this)">
            <i class="fa-solid fa-house"></i>
            <span>سەرەکی</span>
        </div>
        <div class="tab-item" onclick="switchTab('tabDebts', this)">
            <i class="fa-solid fa-list-check"></i>
            <span>قەرزەکان</span>
        </div>
        <div class="tab-item fab-tab" onclick="openAddDebtModal()">
            <div class="fab-button">
                <i class="fa-solid fa-plus"></i>
            </div>
            <span>نوێ</span>
        </div>
        <div class="tab-item" onclick="switchTab('tabAnalytics', this)">
            <i class="fa-solid fa-chart-pie"></i>
            <span>ڕاپۆرت</span>
        </div>
        <div class="tab-item" onclick="openProfileModal()">
            <i class="fa-solid fa-circle-user"></i>
            <span>پرۆفایل</span>
        </div>
    </nav>

    <!-- ٥. پەنجەرەی کشاوە: زیادکردنی قەرزی نوێ -->
    <div class="ios-modal" id="debtModal">
        <div class="ios-sheet">
            <div class="sheet-drag"></div>
            <div class="sheet-header">
                <h3>تۆمارکردنی قەرزی نوێ</h3>
                <i class="fa-solid fa-xmark" style="font-size: 18px; cursor: pointer;" onclick="closeModal('debtModal')"></i>
            </div>
            <form id="debtForm" onsubmit="event.preventDefault(); saveNewDebt();">
                <div class="form-group">
                    <label>ناوی کڕیار *</label>
                    <input type="text" id="custName" list="custSuggestions" placeholder="ناوی کڕیار بنووسە..." autocomplete="off">
                    <datalist id="custSuggestions"></datalist>
                </div>
                <div class="form-group">
                    <label>ژمارەی مۆبایل (واتسئاپ)</label>
                    <input type="tel" id="custPhone" placeholder="0750 000 0000">
                </div>
                <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 10px;">
                    <div class="form-group">
                        <label>بڕی قەرز *</label>
                        <input type="number" step="any" id="custAmount" placeholder="100000">
                    </div>
                    <div class="form-group">
                        <label>دراو</label>
                        <select id="custCurrency">
                            <option value="IQD">دینار</option>
                            <option value="USD">دۆلار ($)</option>
                        </select>
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                    <div class="form-group">
                        <label>بەرواری قەرز</label>
                        <input type="date" id="custDebtDate">
                    </div>
                    <div class="form-group">
                        <label>بەرواری دانەوە *</label>
                        <input type="date" id="custDueDate">
                    </div>
                </div>
                <div class="form-group">
                    <label>تێبینی</label>
                    <textarea id="custNote" rows="2" placeholder="کەلوپەل، هۆکار..."></textarea>
                </div>
                <button type="button" id="btnSaveDebt" class="btn-ios-submit" onclick="saveNewDebt()">پاشەکەوتکردن</button>
            </form>
        </div>
    </div>

    <!-- ٦. پەنجەرەی کشاوە: واسڵکردنی پارە -->
    <div class="ios-modal" id="payModal">
        <div class="ios-sheet">
            <div class="sheet-drag"></div>
            <div class="sheet-header">
                <h3 id="payTitle">واسڵکردنی پارە</h3>
                <i class="fa-solid fa-xmark" style="font-size: 18px; cursor: pointer;" onclick="closeModal('payModal')"></i>
            </div>
            <p id="payRemainingText" style="color: var(--ios-red); font-size: 15px; font-weight: 800; margin-bottom: 14px;"></p>
            <form id="payForm">
                <input type="hidden" id="payDebtId">
                <div class="form-group">
                    <label>بڕی پارەی دراو *</label>
                    <input type="number" step="any" id="payAmount" required>
                </div>
                <div class="form-group">
                    <label>تێبینی</label>
                    <input type="text" id="payNote" placeholder="وەسڵی کاش، هتد...">
                </div>
                <button type="submit" class="btn-ios-submit" style="background: var(--ios-green); color: #000;">وەرگرتنی پارە</button>
            </form>
        </div>
    </div>

    <!-- ٧. پەنجەرەی کشاوە: پرۆفایل -->
    <div class="ios-modal" id="profileModal">
        <div class="ios-sheet">
            <div class="sheet-drag"></div>
            <div class="sheet-header">
                <h3>پرۆفایلی بەکارهێنەر</h3>
                <i class="fa-solid fa-xmark" style="font-size: 18px; cursor: pointer;" onclick="closeModal('profileModal')"></i>
            </div>
            <form id="profileForm" onsubmit="event.preventDefault(); saveProfile();">
                <div style="text-align: center; margin-bottom: 16px;">
                    <img src="" id="profileImgPreview" style="width: 80px; height: 80px; border-radius: 50%; object-fit: cover; border: 2px solid var(--ios-blue); margin-bottom: 8px;">
                    <div>
                        <input type="file" id="avatarFileInput" accept="image/*" style="display: none;">
                        <button type="button" class="action-pill" style="margin: 0 auto; background: rgba(255,255,255,0.08); color: #fff; padding: 6px 14px; font-size: 11px;" onclick="document.getElementById('avatarFileInput').click()">
                            گۆڕینی وێنە
                        </button>
                    </div>
                </div>
                <div class="form-group">
                    <label>ناوی تەواو</label>
                    <input type="text" id="profileFullName" required>
                </div>
                <div class="form-group">
                    <label>بایۆ</label>
                    <textarea id="profileBio" rows="2"></textarea>
                </div>
                <button type="button" class="btn-ios-submit" onclick="saveProfile()">پاشەکەوتکردن</button>
            </form>
        </div>
    </div>

    <!-- ٨. پەنجەرەی لۆگی چاودێری -->
    <div class="ios-modal" id="auditModal">
        <div class="ios-sheet">
            <div class="sheet-drag"></div>
            <div class="sheet-header">
                <h3>لۆگی چاودێریی کارمەندان</h3>
                <i class="fa-solid fa-xmark" style="font-size: 18px; cursor: pointer;" onclick="closeModal('auditModal')"></i>
            </div>
            <div id="auditLogsContainer" style="max-height: 50vh; overflow-y: auto;"></div>
        </div>
    </div>

    <!-- وەسڵی گەرمیی -->
    <div id="thermalReceipt">
        <div style="text-align: center; border-bottom: 1px dashed #000; padding-bottom: 8px; margin-bottom: 8px;">
            <h2 style="font-size: 16px; margin: 0;">سیستەمی دانیال</h2>
            <p style="font-size: 11px; margin: 2px 0;">وەسڵی وەرگرتنی پارە</p>
            <p id="recNo" style="font-size: 10px; margin: 0;"></p>
            <p id="recDate" style="font-size: 10px; margin: 0;"></p>
        </div>
        <div style="font-size: 11px; margin-bottom: 8px;">
            <p><strong>کڕیار:</strong> <span id="recCustomer"></span></p>
            <p><strong>مۆبایل:</strong> <span id="recPhone"></span></p>
            <p><strong>وەرگیرا لەلایەن:</strong> <span id="recUser"></span></p>
        </div>
        <div style="border-top: 1px dashed #000; border-bottom: 1px dashed #000; padding: 6px 0; margin-bottom: 8px;">
            <div style="display: flex; justify-content: space-between; font-weight: bold; font-size: 13px;">
                <span>بڕی دراو:</span>
                <span id="recPaid"></span>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 12px; margin-top: 4px;">
                <span>ماوەی قەرز:</span>
                <span id="recRem"></span>
            </div>
        </div>
    </div>

    <script>
        let currentUser = null;
        let customerSuggestions = [];
        let allDebtsData = [];
        let currentFilter = 'all';
        let monthlyChartInstance = null;
        let debtorsChartInstance = null;

        // دەستپێک
        let splashTimer = setTimeout(finishSplash, 1800);

        function finishSplash() {
            clearTimeout(splashTimer);
            const splash = document.getElementById('splashScreen');
            if (splash) {
                splash.style.opacity = '0';
                setTimeout(() => {
                    splash.style.display = 'none';
                    checkAuth();
                }, 400);
            } else {
                checkAuth();
            }
        }

        async function checkAuth() {
            try {
                const res = await fetch('/api/auth/me');
                const data = await res.json();
                if (data.logged_in) {
                    currentUser = data.user;
                    initApp();
                } else {
                    document.getElementById('loginWrapper').style.display = 'flex';
                    document.getElementById('appView').style.display = 'none';
                    document.getElementById('iosTabBar').style.display = 'none';
                }
            } catch (e) {
                initApp();
            }
        }

        function initApp() {
            document.getElementById('loginWrapper').style.display = 'none';
            document.getElementById('appView').style.display = 'block';
            document.getElementById('iosTabBar').style.display = 'flex';

            updateProfileUI();
            loadDashboardAnalytics();
            loadDebts();
            loadCustomerSuggestions();
        }

        function updateProfileUI() {
            if (!currentUser) return;
            document.getElementById('userName').textContent = currentUser.full_name || 'دانیال ئیسماعیل';
            document.getElementById('userBio').textContent = currentUser.bio || 'بەڕێوەبەری سیستەم';
            document.getElementById('userAvatar').src = currentUser.avatar || 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150';
            document.getElementById('profileImgPreview').src = currentUser.avatar || 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150';
            document.getElementById('profileFullName').value = currentUser.full_name || '';
            document.getElementById('profileBio').value = currentUser.bio || '';
        }

        // گۆڕینی تابەکانی iOS
        function switchTab(tabId, el) {
            document.querySelectorAll('.tab-page').forEach(p => p.classList.remove('active'));
            document.querySelectorAll('.tab-item').forEach(i => i.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
            el.classList.add('active');
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }

        // مۆداڵەکان
        function openAddDebtModal() {
            const today = new Date();
            const nextMonth = new Date();
            nextMonth.setDate(today.getDate() + 30);
            document.getElementById('custDebtDate').value = today.toISOString().split('T')[0];
            document.getElementById('custDueDate').value = nextMonth.toISOString().split('T')[0];
            document.getElementById('debtModal').style.display = 'flex';
        }

        function openProfileModal() {
            updateProfileUI();
            document.getElementById('profileModal').style.display = 'flex';
        }

        function openAuditModal() {
            loadAuditLogs();
            document.getElementById('auditModal').style.display = 'flex';
        }

        function closeModal(id) {
            document.getElementById(id).style.display = 'none';
        }

        // داخستنی مۆداڵ بە کلیک لە دەرەوە
        window.onclick = function(e) {
            if (e.target.classList.contains('ios-modal')) {
                e.target.style.display = 'none';
            }
        };

        // ئامارەکان
        async function loadDashboardAnalytics() {
            try {
                const res = await fetch('/api/dashboard/analytics');
                const data = await res.json();

                document.getElementById('iqdTotalDebt').textContent = Number(data.iqd.debt).toLocaleString() + " د.ع";
                document.getElementById('iqdTotalPaid').textContent = Number(data.iqd.paid).toLocaleString() + " د.ع";
                document.getElementById('iqdRemaining').textContent = Number(data.iqd.remaining).toLocaleString() + " د.ع";

                document.getElementById('usdTotalDebt').textContent = "$" + Number(data.usd.debt).toLocaleString();
                document.getElementById('usdTotalPaid').textContent = "$" + Number(data.usd.paid).toLocaleString();
                document.getElementById('usdRemaining').textContent = "$" + Number(data.usd.remaining).toLocaleString();

                renderCharts(data.monthly_chart, data.top_debtors);
            } catch (e){}
        }

        function renderCharts(monthlyData, topDebtors) {
            try {
                const ctx1 = document.getElementById('monthlyChart').getContext('2d');
                if (monthlyChartInstance) monthlyChartInstance.destroy();
                monthlyChartInstance = new Chart(ctx1, {
                    type: 'bar',
                    data: {
                        labels: monthlyData.map(m => m.month),
                        datasets: [{
                            data: monthlyData.map(m => m.total),
                            backgroundColor: '#0A84FF',
                            borderRadius: 8
                        }]
                    },
                    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
                });

                const ctx2 = document.getElementById('debtorsChart').getContext('2d');
                if (debtorsChartInstance) debtorsChartInstance.destroy();
                debtorsChartInstance = new Chart(ctx2, {
                    type: 'doughnut',
                    data: {
                        labels: topDebtors.map(d => d.customer_name),
                        datasets: [{
                            data: topDebtors.map(d => d.remaining),
                            backgroundColor: ['#FF453A', '#FF9F0A', '#BF5AF2', '#0A84FF', '#30D158']
                        }]
                    },
                    options: { responsive: true, maintainAspectRatio: false }
                });
            } catch(e){}
        }

        // هێنانی قەرزەکان بە کارتی iOS
        async function loadDebts() {
            const search = document.getElementById('searchInput').value;
            const res = await fetch(`/api/debts?search=${encodeURIComponent(search)}`);
            allDebtsData = await res.json();
            renderDebtsList();
        }

        function filterStatus(status, el) {
            currentFilter = status;
            document.querySelectorAll('.segment-btn').forEach(b => b.classList.remove('active'));
            el.classList.add('active');
            renderDebtsList();
        }

        function renderDebtsList() {
            const container = document.getElementById('debtsCardsContainer');
            container.innerHTML = '';

            let filtered = allDebtsData;
            if (currentFilter !== 'all') {
                filtered = allDebtsData.filter(d => d.status === currentFilter);
            }

            if (filtered.length === 0) {
                container.innerHTML = `<p style="text-align: center; color: var(--ios-muted); padding: 30px; font-size: 13px;">هیچ قەرزێک بەردەست نییە</p>`;
                return;
            }

            filtered.forEach(d => {
                let cleanPhone = (d.phone || '').replace(/[^0-9]/g, '');
                if (cleanPhone.startsWith('07')) cleanPhone = '964' + cleanPhone.substring(1);
                const waMessage = encodeURIComponent(
                    `سڵاو بەڕێز ${d.customer_name}،\nلە سیستەمی دانیالەوە ئاگادارتان دەکەینەوە کە بڕی (${Number(d.remaining_amount).toLocaleString()} ${d.currency}) قەرزت ماوە کە بەرواری دانەوەی (${d.due_date})یە.\nسوپاس.`
                );
                const waLink = cleanPhone ? `https://wa.me/${cleanPhone}?text=${waMessage}` : '#';

                const statusLabel = d.status === 'paid' ? 'دراوە' : d.status === 'overdue' ? 'دواکەوتوو' : 'نەدراوە';
                const statusClass = d.status === 'paid' ? 'badge-paid' : d.status === 'overdue' ? 'badge-overdue' : 'badge-pending';

                container.innerHTML += `
                    <div class="debt-card">
                        <div class="debt-card-header">
                            <div class="customer-info">
                                <div class="customer-avatar">${d.customer_name.charAt(0)}</div>
                                <div>
                                    <div class="customer-name">${d.customer_name}</div>
                                    <div style="font-size: 11px; color: var(--ios-muted);">${d.due_date}</div>
                                </div>
                            </div>
                            <span class="badge-status ${statusClass}">${statusLabel}</span>
                        </div>

                        <div class="debt-details-row">
                            <span style="font-size: 12px; color: var(--ios-muted);">ماوەی قەرز:</span>
                            <span class="amount-remaining">${Number(d.remaining_amount).toLocaleString()} ${d.currency}</span>
                        </div>

                        <div class="debt-card-actions">
                            ${d.remaining_amount > 0 ? `
                                <button class="action-pill action-pay" onclick="openPayModal(${d.id}, '${d.customer_name}', ${d.remaining_amount}, '${d.currency}')">
                                    <i class="fa-solid fa-hand-holding-dollar"></i> واسڵکردن
                                </button>
                            ` : ''}
                            ${cleanPhone ? `
                                <a href="${waLink}" target="_blank" class="action-pill action-wa">
                                    <i class="fa-brands fa-whatsapp"></i> واتسئاپ
                                </a>
                            ` : ''}
                            <button class="action-pill action-del" onclick="deleteDebt(${d.id})">
                                <i class="fa-solid fa-trash"></i>
                            </button>
                        </div>
                    </div>
                `;
            });
        }

        // پاشەکەوتکردنی قەرزی نوێ
        async function saveNewDebt() {
            const name = document.getElementById('custName').value.trim();
            const amount = document.getElementById('custAmount').value.trim();
            const dueDate = document.getElementById('custDueDate').value;
            const debtDate = document.getElementById('custDebtDate').value || new Date().toISOString().split('T')[0];
            const phone = document.getElementById('custPhone').value.trim();
            const currency = document.getElementById('custCurrency').value;
            const note = document.getElementById('custNote').value.trim();

            if (!name || !amount || !dueDate) {
                alert("تکایە ناو، بڕی پارە و بەرواری دانەوە پڕبکەرەوە!");
                return;
            }

            const btn = document.getElementById('btnSaveDebt');
            btn.disabled = true;
            btn.textContent = "کەمێکی تر...";

            try {
                const res = await fetch('/api/debts', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        customer_name: name,
                        phone: phone,
                        total_amount: amount,
                        currency: currency,
                        debt_date: debtDate,
                        due_date: dueDate,
                        note: note
                    })
                });
                const data = await res.json();
                if (res.ok) {
                    closeModal('debtModal');
                    document.getElementById('debtForm').reset();
                    await loadDashboardAnalytics();
                    await loadDebts();
                    switchTab('tabDebts', document.querySelectorAll('.tab-item')[1]);
                } else {
                    alert(data.message || "هەڵەیەک ڕوویدا");
                }
            } catch(e) {
                alert("پەیوەندی بە سێرڤەرەوە پچڕا!");
            } finally {
                btn.disabled = false;
                btn.textContent = "پاشەکەوتکردن";
            }
        }

        // واسڵکردن
        function openPayModal(id, name, remaining, currency) {
            document.getElementById('payDebtId').value = id;
            document.getElementById('payTitle').textContent = `واسڵکردن: ${name}`;
            document.getElementById('payRemainingText').textContent = `ماوە: ${Number(remaining).toLocaleString()} ${currency}`;
            document.getElementById('payAmount').max = remaining;
            document.getElementById('payModal').style.display = 'flex';
        }

        document.getElementById('payForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const debtId = document.getElementById('payDebtId').value;
            const res = await fetch(`/api/debts/${debtId}/payments`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    amount: document.getElementById('payAmount').value,
                    note: document.getElementById('payNote').value.trim()
                })
            });
            const data = await res.json();
            if (res.ok) {
                closeModal('payModal');
                loadDashboardAnalytics();
                loadDebts();
                if (confirm('پارەکە واسڵکرا! ئایا وەسڵەکەی چاپ دەکەیت؟')) {
                    window.print();
                }
            }
        });

        // پرۆفایل
        async function saveProfile() {
            const formData = new FormData();
            formData.append('full_name', document.getElementById('profileFullName').value.trim());
            formData.append('bio', document.getElementById('profileBio').value.trim());
            const file = document.getElementById('avatarFileInput').files[0];
            if (file) formData.append('avatar', file);

            const res = await fetch('/api/profile/update', { method: 'POST', body: formData });
            const data = await res.json();
            if (res.ok) {
                currentUser = data.user;
                updateProfileUI();
                closeModal('profileModal');
            }
        }

        document.getElementById('avatarFileInput').addEventListener('change', (e) => {
            if (e.target.files && e.target.files[0]) {
                const reader = new FileReader();
                reader.onload = (ev) => document.getElementById('profileImgPreview').src = ev.target.result;
                reader.readAsDataURL(e.target.files[0]);
            }
        });

        async function deleteDebt(id) {
            if (confirm('دڵنیایت لە سڕینەوەی ئەم قەرزە؟')) {
                await fetch(`/api/debts/${id}`, { method: 'DELETE' });
                loadDashboardAnalytics();
                loadDebts();
            }
        }

        async function loadAuditLogs() {
            const res = await fetch('/api/audit-logs');
            const logs = await res.json();
            const cont = document.getElementById('auditLogsContainer');
            cont.innerHTML = '';
            logs.forEach(l => {
                cont.innerHTML += `
                    <div style="background: rgba(255,255,255,0.04); padding: 10px; border-radius: 12px; margin-bottom: 8px; font-size: 12px;">
                        <div style="display:flex; justify-content:space-between; font-weight:700; color: var(--ios-blue);">
                            <span>${l.username} (${l.action})</span>
                            <span style="color: var(--ios-muted); font-size:10px;">${l.created_at}</span>
                        </div>
                        <p style="margin-top:4px; color:#ddd;">${l.details}</p>
                    </div>
                `;
            });
        }

        async function loadCustomerSuggestions() {
            const res = await fetch('/api/customers/suggestions');
            customerSuggestions = await res.json();
            const dl = document.getElementById('custSuggestions');
            dl.innerHTML = '';
            customerSuggestions.forEach(c => {
                const opt = document.createElement('option');
                opt.value = c.name;
                dl.appendChild(opt);
            });
        }

        document.getElementById('custName').addEventListener('input', (e) => {
            const match = customerSuggestions.find(c => c.name.toLowerCase() === e.target.value.toLowerCase());
            if (match && match.phone) document.getElementById('custPhone').value = match.phone;
        });

        async function logout() {
            await fetch('/api/auth/logout', { method: 'POST' });
            location.reload();
        }
    </script>
</body>
</html>
