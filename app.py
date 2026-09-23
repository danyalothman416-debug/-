<!DOCTYPE html>
<html lang="ckb" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>سیستەمی دارایی دانیال | Danyal OS</title>
    
    <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">

    <style>
        :root {
            --ios-bg: #07090e;
            --ios-card: rgba(18, 20, 32, 0.82);
            --ios-card-border: rgba(255, 255, 255, 0.12);
            --ios-blue: #0A84FF;
            --ios-green: #30D158;
            --ios-red: #FF453A;
            --ios-orange: #FF9F0A;
            --ios-purple: #BF5AF2;
            --ios-text: #FFFFFF;
            --ios-muted: #9ba1b0;
            --safe-bottom: env(safe-area-inset-bottom, 20px);
            --transition: all 0.25s cubic-bezier(0.2, 0.8, 0.2, 1);
        }

        * {
            margin: 0; padding: 0; box-sizing: border-box;
            font-family: 'Vazirmatn', -apple-system, sans-serif;
            -webkit-tap-highlight-color: transparent;
        }

        body {
            background-color: var(--ios-bg);
            background-image: 
                radial-gradient(circle at 10% 10%, rgba(191, 90, 242, 0.16), transparent 35%),
                radial-gradient(circle at 90% 90%, rgba(10, 132, 255, 0.18), transparent 45%),
                linear-gradient(rgba(7, 9, 14, 0.88), rgba(7, 9, 14, 0.95)),
                url('https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=1600');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            color: var(--ios-text);
            min-height: 100vh;
            padding-bottom: calc(var(--safe-bottom) + 85px);
            user-select: none;
        }

        /* ١. دەستپێکی شاهانەی "دانیال" لەسەر شێوازی ئەپڵ */
        #splashScreen {
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            background-color: #06070a;
            background-image: 
                radial-gradient(circle at center, rgba(121, 40, 202, 0.35), transparent 70%),
                linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.85)),
                url('https://images.unsplash.com/photo-1550684848-fac1c5b4e853?w=1600');
            background-size: cover;
            background-position: center;
            z-index: 99999;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: opacity 0.6s cubic-bezier(0.16, 1, 0.3, 1), transform 0.6s cubic-bezier(0.16, 1, 0.3, 1);
        }

        .splash-card {
            text-align: center;
            padding: 30px;
        }

        .danyal-brand-logo {
            width: 90px; height: 90px;
            margin: 0 auto 20px;
            border-radius: 26px;
            background: linear-gradient(135deg, #7928ca, #0070f3);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 42px;
            color: #fff;
            box-shadow: 0 0 50px rgba(0, 112, 243, 0.7);
            animation: pulseSoft 2.5s infinite alternate ease-in-out;
        }

        @keyframes pulseSoft {
            0% { transform: scale(1); box-shadow: 0 0 35px rgba(121, 40, 202, 0.5); }
            100% { transform: scale(1.05); box-shadow: 0 0 65px rgba(0, 112, 243, 0.85); }
        }

        .danyal-title {
            font-size: 32px;
            font-weight: 900;
            background: linear-gradient(180deg, #ffffff, #c7d2fe);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 6px;
        }

        .danyal-sub {
            color: var(--ios-muted);
            font-size: 13px;
            margin-bottom: 26px;
        }

        /* لۆدەری نەرمی بازنەیی ئەپڵ */
        .apple-spinner {
            width: 26px;
            height: 26px;
            margin: 0 auto;
            border: 3px solid rgba(255, 255, 255, 0.15);
            border-top-color: var(--ios-blue);
            border-radius: 50%;
            animation: spinFast 0.8s linear infinite;
        }

        @keyframes spinFast {
            to { transform: rotate(360deg); }
        }

        /* ٢. پەڕەی چوونەژوورەوە */
        .auth-container {
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            background-image: 
                radial-gradient(circle, rgba(121, 40, 202, 0.25), transparent 70%),
                linear-gradient(rgba(7, 9, 14, 0.85), rgba(7, 9, 14, 0.95)),
                url('https://images.unsplash.com/photo-1518770660439-4636190af475?w=1600');
            background-size: cover;
            background-position: center;
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 50000;
            padding: 20px;
        }

        .auth-card {
            width: 100%;
            max-width: 400px;
            background: var(--ios-card);
            backdrop-filter: blur(28px);
            -webkit-backdrop-filter: blur(28px);
            border: 1px solid var(--ios-card-border);
            border-radius: 28px;
            padding: 34px 26px;
            box-shadow: 0 30px 60px rgba(0,0,0,0.8);
            text-align: center;
        }

        .btn-google {
            width: 100%;
            padding: 13px;
            background: #ffffff;
            color: #1f2937;
            border-radius: 14px;
            border: none;
            font-weight: 700;
            font-size: 13.5px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            transition: var(--transition);
            margin-bottom: 20px;
        }

        .btn-google:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(255,255,255,0.2); }

        /* ٣. ئەپی سەرەکی */
        .app-view {
            display: none;
            padding: 14px 16px;
            max-width: 620px;
            margin: 0 auto;
        }

        .ios-header {
            position: sticky; top: 0; z-index: 100;
            background: rgba(7, 9, 14, 0.82);
            backdrop-filter: blur(24px);
            -webkit-backdrop-filter: blur(24px);
            padding: 14px 18px;
            display: flex; align-items: center; justify-content: space-between;
            border-bottom: 1px solid rgba(255,255,255,0.06);
            border-radius: 0 0 20px 20px;
            margin-bottom: 14px;
        }

        .ios-profile {
            display: flex; align-items: center; gap: 12px; cursor: pointer;
        }

        .ios-avatar {
            width: 44px; height: 44px; border-radius: 50%; object-fit: cover; border: 2px solid var(--ios-blue);
        }

        .tab-page { display: none; }
        .tab-page.active { display: block; }

        .wallet-card {
            background: linear-gradient(135deg, rgba(24, 32, 48, 0.85), rgba(15, 20, 32, 0.85));
            backdrop-filter: blur(20px);
            border: 1px solid var(--ios-card-border);
            border-radius: 24px;
            padding: 22px;
            margin-bottom: 16px;
            box-shadow: 0 12px 28px rgba(0,0,0,0.45);
        }

        .wallet-balance {
            font-size: 28px; font-weight: 900; color: var(--ios-red); margin: 6px 0 16px;
        }

        .wallet-grid {
            display: grid; grid-template-columns: 1fr 1fr; gap: 12px;
            padding-top: 14px; border-top: 1px solid rgba(255,255,255,0.08);
        }

        .debt-card {
            background: var(--ios-card);
            backdrop-filter: blur(16px);
            border: 1px solid var(--ios-card-border);
            border-radius: 20px;
            padding: 16px;
            margin-bottom: 12px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.3);
        }

        .debt-row {
            display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;
        }

        .action-pill {
            flex: 1; padding: 10px; border-radius: 12px; border: none;
            font-size: 12px; font-weight: 700; cursor: pointer;
            display: flex; align-items: center; justify-content: center; gap: 6px;
            text-decoration: none;
        }

        .ios-tab-bar {
            position: fixed; bottom: 0; left: 0; width: 100vw;
            background: rgba(14, 16, 24, 0.88);
            backdrop-filter: blur(28px);
            -webkit-backdrop-filter: blur(28px);
            border-top: 1px solid var(--ios-card-border);
            display: flex; justify-content: space-around;
            padding: 8px 0 var(--safe-bottom);
            z-index: 1000;
        }

        .tab-item {
            display: flex; flex-direction: column; align-items: center; gap: 4px;
            color: var(--ios-muted); font-size: 10px; font-weight: 600; cursor: pointer; flex: 1;
        }
        .tab-item.active { color: var(--ios-blue); }

        .fab-tab .fab-button {
            width: 48px; height: 48px; border-radius: 50%;
            background: linear-gradient(135deg, var(--ios-purple), var(--ios-blue));
            display: flex; align-items: center; justify-content: center;
            color: #fff; font-size: 20px; margin-top: -14px;
            box-shadow: 0 8px 20px rgba(10, 132, 255, 0.45);
        }

        .ios-modal {
            position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
            background: rgba(0,0,0,0.75); backdrop-filter: blur(12px);
            z-index: 100000 !important; display: none; align-items: flex-end; justify-content: center;
        }

        .ios-sheet {
            width: 100%; max-width: 520px; background: #121520;
            border-top: 1px solid var(--ios-card-border);
            border-radius: 28px 28px 0 0; padding: 22px 22px calc(var(--safe-bottom) + 24px);
            max-height: 88vh; overflow-y: auto;
        }

        .form-group { margin-bottom: 14px; text-align: right; }
        .form-group label { display: block; margin-bottom: 6px; font-size: 12px; color: var(--ios-muted); font-weight: 600; }
        .form-group input, .form-group select, .form-group textarea {
            width: 100%; padding: 12px 14px; background: rgba(255,255,255,0.06);
            border: 1px solid var(--ios-card-border); border-radius: 14px; color: #fff; outline: none; font-size: 14px;
        }

        .btn-ios-submit {
            width: 100%; padding: 14px; border-radius: 16px; border: none;
            background: var(--ios-blue); color: #fff; font-size: 15px; font-weight: 800; cursor: pointer; margin-top: 10px;
        }

        #thermalReceipt { display: none; width: 80mm; padding: 15px; background: #fff; color: #000; font-size: 12px; }
        @media print {
            body * { visibility: hidden; }
            #thermalReceipt, #thermalReceipt * { visibility: visible; }
            #thermalReceipt { display: block !important; position: absolute; left: 0; top: 0; width: 80mm; }
        }
    </style>
</head>
<body>

    <!-- ١. پەڕەی دەستپێکی شاهانەی "دانیال" بە ستایلی مۆدێرنی ئەپڵ -->
    <div id="splashScreen">
        <div class="splash-card">
            <div class="danyal-brand-logo">
                <i class="fa-solid fa-cube"></i>
            </div>
            <h1 class="danyal-title">دانیال</h1>
            <p class="danyal-sub">سیستەمی دارایی و بەڕێوەبردنی قەرز</p>
            <div class="apple-spinner"></div>
        </div>
    </div>

    <!-- ٢. پەڕەی چوونەژوورەوە بە ئیمەیڵ -->
    <div class="auth-container" id="authSection">
        <div class="auth-card">
            <div style="text-align: center; margin-bottom: 22px;">
                <div style="width: 64px; height: 64px; background: linear-gradient(135deg, var(--ios-purple), var(--ios-blue)); border-radius: 20px; margin: 0 auto 12px; display: flex; align-items: center; justify-content: center; font-size: 28px; color: #fff;">
                    <i class="fa-solid fa-cube"></i>
                </div>
                <h2 style="font-size: 20px; font-weight: 800;">سیستەمی دانیال</h2>
                <p style="font-size: 12px; color: var(--ios-muted);">بە ئیمەیڵی تایبەتی خۆت بچۆ ژوورەوە</p>
            </div>

            <button class="btn-google" type="button" onclick="loginWithGooglePrompt()">
                <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" width="18" alt="Google">
                <span>چوونەژوورەوە لە ڕێگەی Google</span>
            </button>

            <div style="display: flex; align-items: center; margin-bottom: 18px; color: var(--ios-muted); font-size: 12px;">
                <span style="flex:1; border-bottom:1px solid rgba(255,255,255,0.1);"></span>
                <span style="padding: 0 10px;">یان بە ئیمەیڵ</span>
                <span style="flex:1; border-bottom:1px solid rgba(255,255,255,0.1);"></span>
            </div>

            <form id="emailLoginForm" onsubmit="event.preventDefault(); submitEmailAuth();">
                <div class="form-group">
                    <label>ئیمەیڵ (Email)</label>
                    <input type="email" id="userEmailInput" required placeholder="danyal@gmail.com">
                </div>
                <div class="form-group">
                    <label>وشەی نهێنی (Password)</label>
                    <input type="password" id="userPasswordInput" required placeholder="••••••••">
                </div>
                <button type="submit" class="btn-ios-submit" id="btnSubmitAuth">
                    چوونەژوورەوە / دروستکردنی ئەکاونت
                </button>
            </form>
            <p id="authErrorMsg" style="color: var(--ios-red); font-size: 12px; margin-top: 14px; display: none;"></p>
        </div>
    </div>

    <!-- ٣. ئەپی سەرەکی -->
    <div class="app-view" id="appView">
        <header class="ios-header">
            <div class="ios-profile" onclick="openProfileModal()">
                <img src="" id="userAvatar" class="ios-avatar" alt="Avatar">
                <div>
                    <h3 id="topBizName" style="font-size: 15px; font-weight: 800;">فرۆشگای دانیال</h3>
                    <span id="topOwnerName" style="font-size: 11px; color: var(--ios-muted);">بەڕێوەبەری سیستەم</span>
                </div>
            </div>
            <button class="action-pill" style="background: rgba(255, 69, 58, 0.15); color: var(--ios-red); flex:0 0 40px; height:40px; border-radius:50%;" onclick="logout()" title="دەرچوون">
                <i class="fa-solid fa-right-from-bracket"></i>
            </button>
        </header>

        <!-- تابی باڵانس -->
        <div id="tabHome" class="tab-page active">
            <div class="wallet-card">
                <span style="font-size: 12px; color: var(--ios-muted);">کۆی قەرزی ماوە لای خەڵک (IQD)</span>
                <div class="wallet-balance" id="iqdRemaining">0 د.ع</div>
                <div class="wallet-grid">
                    <div><span style="font-size: 11px; color: var(--ios-muted);">کۆی گشتی:</span><strong id="iqdTotalDebt">0 د.ع</strong></div>
                    <div><span style="font-size: 11px; color: var(--ios-muted);">واسڵکراو:</span><strong id="iqdTotalPaid" style="color: var(--ios-green);">0 د.ع</strong></div>
                </div>
            </div>

            <div class="wallet-card" style="background: linear-gradient(135deg, rgba(19, 36, 27, 0.85), rgba(13, 23, 18, 0.85));">
                <span style="font-size: 12px; color: var(--ios-muted);">کۆی قەرزی ماوە لای خەڵک (USD)</span>
                <div class="wallet-balance" id="usdRemaining" style="color: var(--ios-green);">$0</div>
                <div class="wallet-grid">
                    <div><span style="font-size: 11px; color: var(--ios-muted);">کۆی بە دۆلار:</span><strong id="usdTotalDebt">$0</strong></div>
                    <div><span style="font-size: 11px; color: var(--ios-muted);">واسڵکراو:</span><strong id="usdTotalPaid" style="color: var(--ios-green);">$0</strong></div>
                </div>
            </div>

            <div style="background: var(--ios-card); backdrop-filter: blur(16px); border: 1px solid var(--ios-card-border); border-radius: 20px; padding: 18px; margin-bottom: 20px;">
                <h4 style="font-size: 13px; margin-bottom: 12px; color: var(--ios-muted);">
                    <i class="fa-solid fa-chart-column"></i> واسڵکردنی ٦ مانگی ڕابردوو
                </h4>
                <div style="height: 180px;"><canvas id="monthlyChart"></canvas></div>
            </div>
        </div>

        <!-- تابی قەرزەکان -->
        <div id="tabDebts" class="tab-page">
            <input type="text" id="searchInput" placeholder="گەڕان بەپێی ناوی کەس یان مۆبایل..." oninput="loadDebts()"
                   style="width: 100%; padding: 14px 16px; background: var(--ios-card); border: 1px solid var(--ios-card-border); border-radius: 16px; color: #fff; font-size: 13px; margin-bottom: 14px;">
            <div id="debtsCardsContainer"></div>
        </div>

        <!-- تابی ڕاپۆرت -->
        <div id="tabAnalytics" class="tab-page">
            <div style="background: var(--ios-card); backdrop-filter: blur(16px); border: 1px solid var(--ios-card-border); border-radius: 20px; padding: 18px; margin-bottom: 16px;">
                <h4 style="font-size: 13px; margin-bottom: 12px; color: var(--ios-muted);">گەورەترین قەرزدارەکان</h4>
                <div style="height: 190px;"><canvas id="debtorsChart"></canvas></div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                <button class="action-pill" style="background: var(--ios-card); border: 1px solid var(--ios-card-border); color: #fff; padding: 14px;" onclick="location.href='/api/reports/export-excel'">
                    <i class="fa-solid fa-file-excel" style="color: var(--ios-green);"></i> ئێکسڵ (Excel)
                </button>
                <button class="action-pill" style="background: var(--ios-card); border: 1px solid var(--ios-card-border); color: #fff; padding: 14px;" onclick="location.href='/api/admin/backup'">
                    <i class="fa-solid fa-cloud-arrow-down" style="color: var(--ios-blue);"></i> باکئەپ (.db)
                </button>
            </div>
        </div>
    </div>

    <!-- ٤. شریتی خوارەوە (Tab Bar) -->
    <nav class="ios-tab-bar" id="iosTabBar" style="display: none;">
        <div class="tab-item active" onclick="switchTab('tabHome', this)">
            <i class="fa-solid fa-wallet"></i><span>باڵانس</span>
        </div>
        <div class="tab-item" onclick="switchTab('tabDebts', this)">
            <i class="fa-solid fa-list-check"></i><span>قەرزەکان</span>
        </div>
        <div class="tab-item fab-tab" onclick="openAddDebtModal()">
            <div class="fab-button"><i class="fa-solid fa-plus"></i></div>
            <span>نوێ</span>
        </div>
        <div class="tab-item" onclick="switchTab('tabAnalytics', this)">
            <i class="fa-solid fa-chart-pie"></i><span>ڕاپۆرت</span>
        </div>
        <div class="tab-item" onclick="openProfileModal()">
            <i class="fa-solid fa-circle-user"></i><span>پرۆفایل</span>
        </div>
    </nav>

    <!-- مۆداڵی قەرزی نوێ -->
    <div class="ios-modal" id="debtModal">
        <div class="ios-sheet">
            <h3 style="margin-bottom: 16px; font-size: 17px;">تۆمارکردنی قەرزی نوێ</h3>
            <form id="debtForm" onsubmit="event.preventDefault(); saveNewDebt();">
                <div class="form-group">
                    <label>ناوی کڕیار *</label>
                    <input type="text" id="custName" list="custSuggestions" required placeholder="ناوی کڕیار بنووسە..." autocomplete="off">
                    <datalist id="custSuggestions"></datalist>
                </div>
                <div class="form-group">
                    <label>مۆبایل (واتسئاپ)</label>
                    <input type="tel" id="custPhone" placeholder="0750 000 0000">
                </div>
                <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 8px;">
                    <div class="form-group">
                        <label>بڕی قەرز *</label>
                        <input type="number" step="any" id="custAmount" required placeholder="100000">
                    </div>
                    <div class="form-group">
                        <label>دراو</label>
                        <select id="custCurrency">
                            <option value="IQD">دینار</option>
                            <option value="USD">دۆلار ($)</option>
                        </select>
                    </div>
                </div>
                <div class="form-group">
                    <label>بەرواری دانەوە *</label>
                    <input type="date" id="custDueDate" required>
                </div>
                <div class="form-group">
                    <label>تێبینی</label>
                    <textarea id="custNote" rows="2" placeholder="کەلوپەل، هۆکار..."></textarea>
                </div>
                <button type="submit" class="btn-ios-submit" id="btnSaveDebt">پاشەکەوتکردن</button>
                <button type="button" class="btn-ios-submit" style="background: transparent; color: var(--ios-muted);" onclick="closeModal('debtModal')">داخستن</button>
            </form>
        </div>
    </div>

    <!-- مۆداڵی واسڵکردن -->
    <div class="ios-modal" id="payModal">
        <div class="ios-sheet">
            <h3 id="payTitle" style="margin-bottom: 8px; font-size: 16px;">واسڵکردن</h3>
            <p id="payRemainingText" style="color: var(--ios-red); font-weight: 800; font-size: 14px; margin-bottom: 14px;"></p>
            <form id="payForm">
                <input type="hidden" id="payDebtId">
                <div class="form-group">
                    <label>بڕی پارەی دراو *</label>
                    <input type="number" step="any" id="payAmount" required placeholder="بڕی دراو...">
                </div>
                <button type="submit" class="btn-ios-submit" style="background: var(--ios-green); color: #000;">تەواوکردنی وەرگرتن</button>
                <button type="button" class="btn-ios-submit" style="background: transparent; color: var(--ios-muted);" onclick="closeModal('payModal')">داخستن</button>
            </form>
        </div>
    </div>

    <!-- مۆداڵی پرۆفایل -->
    <div class="ios-modal" id="profileModal">
        <div class="ios-sheet">
            <h3 style="margin-bottom: 16px; font-size: 16px;">پرۆفایلی من</h3>
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
                <button type="submit" class="btn-ios-submit">پاشەکەوتکردن</button>
                <button type="button" class="btn-ios-submit" style="background: transparent; color: var(--ios-muted);" onclick="closeModal('profileModal')">داخستن</button>
            </form>
        </div>
    </div>

    <!-- وەسڵی چاپ -->
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
        </div>
        <div style="border-top: 1px dashed #000; border-bottom: 1px dashed #000; padding: 6px 0; margin-bottom: 8px;">
            <div style="display: flex; justify-content: space-between; font-weight: bold; font-size: 13px;">
                <span>بڕی دراو:</span><span id="recPaid"></span>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 12px; margin-top: 4px;">
                <span>ماوەی قەرز:</span><span id="recRem"></span>
            </div>
        </div>
    </div>

    <script>
        let currentUser = null;
        let monthlyChartInstance = null;
        let debtorsChartInstance = null;

        // ئەنیمەیشنی شاهانەی ئەپڵ بۆ ماوەی ١.٢ چرکە
        window.addEventListener('DOMContentLoaded', () => {
            setTimeout(() => {
                const splash = document.getElementById('splashScreen');
                splash.style.opacity = '0';
                splash.style.transform = 'scale(1.05)';
                splash.style.pointerEvents = 'none';
                setTimeout(() => {
                    splash.style.display = 'none';
                    checkAuth();
                }, 500);
            }, 1200);
        });

        async function checkAuth() {
            try {
                const res = await fetch('/api/auth/me');
                const data = await res.json();
                if (data.logged_in) {
                    document.getElementById('authSection').style.display = 'none';
                    document.getElementById('appView').style.display = 'block';
                    document.getElementById('iosTabBar').style.display = 'flex';

                    currentUser = data.user;
                    document.getElementById('topBizName').textContent = data.business.name;
                    document.getElementById('topOwnerName').textContent = data.user.email;
                    document.getElementById('userAvatar').src = data.user.avatar;
                    document.getElementById('profileImgPreview').src = data.user.avatar;
                    document.getElementById('profileFullName').value = data.user.full_name;
                    document.getElementById('profileBio').value = data.user.bio || '';

                    loadDashboard();
                    loadDebts();
                    loadSuggestions();
                } else {
                    document.getElementById('authSection').style.display = 'flex';
                    document.getElementById('appView').style.display = 'none';
                    document.getElementById('iosTabBar').style.display = 'none';
                }
            } catch (e) {
                console.error(e);
            }
        }

        // چوونەژوورەوە بە ئیمەیڵ
        async function submitEmailAuth() {
            const email = document.getElementById('userEmailInput').value.trim();
            const password = document.getElementById('userPasswordInput').value.trim();
            const errMsg = document.getElementById('authErrorMsg');
            const submitBtn = document.getElementById('btnSubmitAuth');

            errMsg.style.display = 'none';
            submitBtn.disabled = true;
            submitBtn.textContent = 'کەمێکی تر...';

            try {
                const res = await fetch('/api/auth/email-login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ email: email, password: password })
                });

                const data = await res.json();

                if (res.ok && data.status === 'success') {
                    location.reload();
                } else {
                    errMsg.textContent = data.message || "هەڵەیەک لە چوونەژوورەوەدا ڕوویدا";
                    errMsg.style.display = 'block';
                }
            } catch (err) {
                errMsg.textContent = "سێرڤەرەکە کارناکات یان ناونیشانەکە پچڕاوە";
                errMsg.style.display = 'block';
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = 'چوونەژوورەوە / دروستکردنی ئەکاونت';
            }
        }

        // چوونەژوورەوە لە ڕێگەی Google
        function loginWithGooglePrompt() {
            const email = prompt("ئیمەیڵی گووگڵت بنووسە بۆ چوونەژوورەوە:");
            if (!email || !email.includes("@")) return;

            fetch('/api/auth/google-one-click', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ email: email.trim(), full_name: email.split('@')[0] })
            }).then(r => r.json()).then(d => {
                if (d.status === 'success') location.reload();
                else alert(d.message);
            });
        }

        async function logout() {
            await fetch('/api/auth/logout', { method: 'POST' });
            location.reload();
        }

        function switchTab(tabId, el) {
            document.querySelectorAll('.tab-page').forEach(p => p.classList.remove('active'));
            document.querySelectorAll('.tab-item').forEach(i => i.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
            el.classList.add('active');
        }

        function openAddDebtModal() {
            const nextMonth = new Date();
            nextMonth.setDate(nextMonth.getDate() + 30);
            document.getElementById('custDueDate').value = nextMonth.toISOString().split('T')[0];
            document.getElementById('debtModal').style.display = 'flex';
        }

        function openProfileModal() { document.getElementById('profileModal').style.display = 'flex'; }
        function closeModal(id) { document.getElementById(id).style.display = 'none'; }

        async function loadDashboard() {
            const res = await fetch('/api/dashboard/analytics');
            const data = await res.json();

            document.getElementById('iqdTotalDebt').textContent = Number(data.iqd.debt).toLocaleString() + " د.ع";
            document.getElementById('iqdTotalPaid').textContent = Number(data.iqd.paid).toLocaleString() + " د.ع";
            document.getElementById('iqdRemaining').textContent = Number(data.iqd.remaining).toLocaleString() + " د.ع";

            document.getElementById('usdTotalDebt').textContent = "$" + Number(data.usd.debt).toLocaleString();
            document.getElementById('usdTotalPaid').textContent = "$" + Number(data.usd.paid).toLocaleString();
            document.getElementById('usdRemaining').textContent = "$" + Number(data.usd.remaining).toLocaleString();

            renderCharts(data.monthly_chart, data.top_debtors);
        }

        function renderCharts(monthlyData, topDebtors) {
            const ctx1 = document.getElementById('monthlyChart').getContext('2d');
            if (monthlyChartInstance) monthlyChartInstance.destroy();
            monthlyChartInstance = new Chart(ctx1, {
                type: 'bar',
                data: {
                    labels: monthlyData.map(m => m.month),
                    datasets: [{ data: monthlyData.map(m => m.total), backgroundColor: '#0A84FF', borderRadius: 8 }]
                },
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
            });

            const ctx2 = document.getElementById('debtorsChart').getContext('2d');
            if (debtorsChartInstance) debtorsChartInstance.destroy();
            debtorsChartInstance = new Chart(ctx2, {
                type: 'doughnut',
                data: {
                    labels: topDebtors.map(d => d.customer_name),
                    datasets: [{ data: topDebtors.map(d => d.remaining), backgroundColor: ['#FF453A', '#FF9F0A', '#BF5AF2', '#0A84FF', '#30D158'] }]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });
        }

        async function loadDebts() {
            const q = document.getElementById('searchInput').value;
            const res = await fetch(`/api/debts?search=${encodeURIComponent(q)}`);
            const debts = await res.json();
            const container = document.getElementById('debtsCardsContainer');
            container.innerHTML = '';

            if (debts.length === 0) {
                container.innerHTML = '<p style="text-align:center; color: var(--ios-muted); padding: 30px;">هیچ قەرزێک تۆمار نەکراوە</p>';
                return;
            }

            debts.forEach(d => {
                let cleanPhone = (d.phone || '').replace(/[^0-9]/g, '');
                if (cleanPhone.startsWith('07')) cleanPhone = '964' + cleanPhone.substring(1);
                const waLink = cleanPhone ? `https://wa.me/${cleanPhone}?text=${encodeURIComponent(`سڵاو کاک ${d.customer_name}، لە سیستەمی دانیال بڕی (${Number(d.remaining_amount).toLocaleString()} ${d.currency}) قەرزت ماوە کە بەرواری دانەوەی (${d.due_date})یە.`)}` : '#';

                container.innerHTML += `
                    <div class="debt-card">
                        <div class="debt-row">
                            <div>
                                <strong style="font-size: 15px;">${d.customer_name}</strong>
                                <p style="font-size: 11px; color: var(--ios-muted);">${d.due_date}</p>
                            </div>
                            <strong style="color: var(--ios-red); font-size: 17px;">${Number(d.remaining_amount).toLocaleString()} ${d.currency}</strong>
                        </div>
                        <div style="display: flex; gap: 8px; margin-top: 10px;">
                            ${d.remaining_amount > 0 ? `
                                <button class="action-pill" style="background: var(--ios-green); color: #000;" onclick="openPayModal(${d.id}, '${d.customer_name}', ${d.remaining_amount}, '${d.currency}')">
                                    واسڵکردن
                                </button>
                            ` : ''}
                            ${cleanPhone ? `
                                <a href="${waLink}" target="_blank" class="action-pill" style="background: rgba(37,211,102,0.15); color: var(--ios-green);">
                                    واتسئاپ
                                </a>
                            ` : ''}
                            <button class="action-pill" style="background: rgba(255,69,58,0.15); color: var(--ios-red); flex:0 0 38px;" onclick="deleteDebt(${d.id})">
                                <i class="fa-solid fa-trash"></i>
                            </button>
                        </div>
                    </div>
                `;
            });
        }

        async function saveNewDebt() {
            const btn = document.getElementById('btnSaveDebt');
            btn.disabled = true;
            btn.textContent = 'کەمێکی تر...';

            const res = await fetch('/api/debts', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    customer_name: document.getElementById('custName').value.trim(),
                    phone: document.getElementById('custPhone').value.trim(),
                    total_amount: document.getElementById('custAmount').value,
                    currency: document.getElementById('custCurrency').value,
                    due_date: document.getElementById('custDueDate').value,
                    note: document.getElementById('custNote').value.trim()
                })
            });
            const data = await res.json();
            btn.disabled = false;
            btn.textContent = 'پاشەکەوتکردن';

            if (res.ok) {
                closeModal('debtModal');
                document.getElementById('debtForm').reset();
                loadDashboard();
                loadDebts();
                loadSuggestions();
            } else {
                alert(data.message || 'هەڵەیەک ڕوویدا');
            }
        }

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
                body: JSON.stringify({ amount: document.getElementById('payAmount').value })
            });
            const data = await res.json();
            if (res.ok) {
                closeModal('payModal');
                loadDashboard();
                loadDebts();
                if (confirm('پارەکە واسڵکرا! ئایا وەسڵەکە چاپ دەکەیت؟')) window.print();
            } else {
                alert(data.message);
            }
        });

        async function saveProfile() {
            const formData = new FormData();
            formData.append('full_name', document.getElementById('profileFullName').value.trim());
            formData.append('bio', document.getElementById('profileBio').value.trim());
            const file = document.getElementById('avatarFileInput').files[0];
            if (file) formData.append('avatar', file);

            const res = await fetch('/api/profile/update', { method: 'POST', body: formData });
            if (res.ok) {
                closeModal('profileModal');
                checkAuth();
            }
        }

        document.getElementById('avatarFileInput').addEventListener('change', (e) => {
            if (e.target.files && e.target.files[0]) {
                const reader = new FileReader();
                reader.onload = (ev) => document.getElementById('profileImgPreview').src = ev.target.result;
                reader.readAsDataURL(e.target.files[0]);
            }
        });

        async function loadSuggestions() {
            const res = await fetch('/api/customers/suggestions');
            const list = await res.json();
            const dl = document.getElementById('custSuggestions');
            dl.innerHTML = '';
            list.forEach(c => {
                const opt = document.createElement('option');
                opt.value = c.name;
                dl.appendChild(opt);
            });
        }

        document.getElementById('custName').addEventListener('input', (e) => {
            const match = customerSuggestions.find(c => c.name.toLowerCase() === e.target.value.toLowerCase());
            if (match && match.phone) document.getElementById('custPhone').value = match.phone;
        });

        async function deleteDebt(id) {
            if (confirm('ئایا دڵنیایت لە سڕینەوە؟')) {
                await fetch(`/api/debts/${id}`, { method: 'DELETE' });
                loadDashboard();
                loadDebts();
            }
        }
    </script>
</body>
</html>
