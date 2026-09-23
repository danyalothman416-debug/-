<!DOCTYPE html>
<html lang="ckb" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>سیستەمی پێشکەوتووی قەرز و حسابات | دانیال</title>
    <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;600;700;800;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <!-- Chart.js بۆ گرافیکە داراییەکان -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <!-- کتێبخانەی Google Identity -->
    <script src="https://accounts.google.com/gsi/client" async defer></script>

    <style>
        :root {
            --bg-dark: #07090e;
            --surface: rgba(15, 20, 32, 0.85);
            --surface-glass: rgba(255, 255, 255, 0.05);
            --border-glass: rgba(255, 255, 255, 0.1);
            --accent-blue: #0070f3;
            --accent-purple: #7928ca;
            --accent-danger: #ef4444;
            --accent-success: #10b981;
            --accent-whatsapp: #25d366;
            --text-main: #ffffff;
            --text-muted: #9ba1b0;
            --transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
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

        /* ١. پەڕەی سینەمایی دەستپێک (Splash) */
        #splashScreen {
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            background: #000;
            z-index: 9999;
            display: flex;
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
            filter: brightness(0.35) contrast(1.2);
        }

        .splash-content {
            position: relative;
            z-index: 2;
            text-align: center;
            animation: popIn 1s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }

        @keyframes popIn {
            0% { opacity: 0; transform: scale(0.8) translateY(30px); }
            100% { opacity: 1; transform: scale(1) translateY(0); }
        }

        .splash-logo {
            width: 100px;
            height: 100px;
            margin: 0 auto 20px;
            border-radius: 28px;
            background: linear-gradient(135deg, var(--accent-purple), var(--accent-blue));
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 46px;
            box-shadow: 0 0 50px rgba(0, 112, 243, 0.8);
        }

        /* ٢. پەڕەی چوونەژوورەوە */
        .login-wrapper {
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            background: url('https://images.unsplash.com/photo-1518770660439-4636190af475?w=1800') center/cover no-repeat;
        }

        .login-overlay {
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
            padding: 40px 34px;
            background: var(--surface);
            border: 1px solid var(--border-glass);
            border-radius: 28px;
            box-shadow: 0 30px 60px rgba(0,0,0,0.6);
            text-align: center;
        }

        .btn-google {
            width: 100%;
            padding: 13px;
            background: #fff;
            color: #222;
            border-radius: 14px;
            border: none;
            font-weight: 700;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            cursor: pointer;
            transition: var(--transition);
            margin-bottom: 20px;
        }

        .btn-google:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(255,255,255,0.25); }

        /* ٣. داشبۆرد و ناوەوەی سیستم */
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

        .main-container {
            max-width: 1300px;
            width: 100%;
            margin: 26px auto;
            padding: 0 20px;
            flex: 1;
        }

        /* کارتەکانی ئامار بە دوو دراو */
        .currency-stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 26px;
        }

        .stat-card-currency {
            background: var(--surface);
            border: 1px solid var(--border-glass);
            border-radius: 20px;
            padding: 22px;
            position: relative;
            overflow: hidden;
        }

        .stat-card-currency::before {
            content: '';
            position: absolute;
            top: 0; right: 0; width: 6px; height: 100%;
        }

        .card-iqd::before { background: var(--accent-blue); }
        .card-usd::before { background: var(--accent-success); }

        .currency-title {
            font-size: 14px;
            color: var(--text-muted);
            margin-bottom: 14px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .currency-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 13.5px;
        }

        /* هێڵکارییەکان (Charts Panel) */
        .charts-row {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
            margin-bottom: 26px;
        }

        @media (max-width: 900px) {
            .charts-row { grid-template-columns: 1fr; }
        }

        .chart-box {
            background: var(--surface);
            border: 1px solid var(--border-glass);
            border-radius: 20px;
            padding: 20px;
        }

        .chart-box h3 {
            font-size: 15px;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        /* خشتە و دوگمەکان */
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
            gap: 12px;
        }

        .btn-action {
            padding: 10px 16px;
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
        }

        .btn-whatsapp {
            background: rgba(37, 211, 102, 0.15);
            color: var(--accent-whatsapp);
            border: 1px solid rgba(37, 211, 102, 0.3);
            padding: 5px 10px;
            border-radius: 8px;
            font-size: 12px;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 5px;
        }

        .btn-whatsapp:hover {
            background: var(--accent-whatsapp);
            color: #fff;
        }

        .table-panel {
            background: var(--surface);
            border: 1px solid var(--border-glass);
            border-radius: 20px;
            overflow-x: auto;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            text-align: right;
            font-size: 13px;
        }

        th, td {
            padding: 15px 18px;
            border-bottom: 1px solid var(--border-glass);
        }

        th { background: rgba(0,0,0,0.3); color: var(--text-muted); }

        /* مۆداڵەکان */
        .modal-screen {
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.75);
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
            max-width: 500px;
            padding: 26px;
            max-height: 90vh;
            overflow-y: auto;
        }

        .form-group {
            margin-bottom: 15px;
            text-align: right;
        }

        .form-group label {
            display: block;
            margin-bottom: 6px;
            font-size: 12px;
            color: var(--text-muted);
            font-weight: 600;
        }

        .form-group input, .form-group select, .form-group textarea {
            width: 100%;
            padding: 11px 14px;
            background: rgba(0,0,0,0.35);
            border: 1px solid var(--border-glass);
            border-radius: 12px;
            color: #fff;
            outline: none;
            font-size: 13px;
        }

        /* دیزاینی تایبەتی وەسڵی چاپی گەرمیی (Thermal Receipt 80mm) */
        #thermalReceipt {
            display: none;
            width: 80mm;
            padding: 15px;
            background: #fff;
            color: #000;
            font-family: monospace, 'Vazirmatn';
            font-size: 12px;
            line-height: 1.4;
        }

        @media print {
            body * { visibility: hidden; }
            #thermalReceipt, #thermalReceipt * { visibility: visible; }
            #thermalReceipt {
                display: block !important;
                position: absolute;
                left: 0; top: 0; width: 80mm; margin: 0; padding: 10px;
            }
        }
    </style>
</head>
<body>

    <!-- دەنگی ئاگادارکردنەوە لە ڕێگەی Web Audio API -->
    <script>
        function playChime() {
            try {
                const ctx = new (window.AudioContext || window.webkitAudioContext)();
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                osc.type = 'sine';
                osc.frequency.setValueAtTime(587.33, ctx.currentTime); // D5
                osc.frequency.exponentialRampToValueAtTime(880, ctx.currentTime + 0.15); // A5
                gain.gain.setValueAtTime(0.3, ctx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.4);
                osc.connect(gain);
                gain.connect(ctx.destination);
                osc.start();
                osc.stop(ctx.currentTime + 0.45);
            } catch(e){}
        }
    </script>

    <!-- ١. پەڕەی دەستپێکی سینەمایی (Video Splash) -->
    <div id="splashScreen">
        <video class="splash-video" autoplay muted loop playsinline>
            <source src="https://assets.mixkit.co/videos/preview/mixkit-digital-animation-of-screens-with-graphs-and-data-31913-large.mp4" type="video/mp4">
        </video>
        <div class="splash-content">
            <div class="splash-logo">
                <i class="fa-solid fa-cube" style="color: #fff;"></i>
            </div>
            <h1 style="font-size: 30px; font-weight: 900; margin-bottom: 8px;">سیستەمی دانیال</h1>
            <p style="color: #cbd5e1; font-size: 14px; margin-bottom: 24px;">بەڕێوەبردنی قەرز، قیستی مانگانە و حساباتی پێشکەوتوو</p>
            <button class="btn-action btn-gradient" onclick="finishSplash()">
                دەستپێکردن <i class="fa-solid fa-arrow-left"></i>
            </button>
        </div>
    </div>

    <!-- ٢. پەڕەی چوونەژوورەوە -->
    <div class="login-wrapper" id="loginWrapper">
        <div class="login-overlay"></div>
        <div class="login-card">
            <div style="font-size: 34px; color: var(--accent-blue); margin-bottom: 12px;">
                <i class="fa-solid fa-file-invoice-dollar"></i>
            </div>
            <h2 style="font-size: 22px; font-weight: 800; margin-bottom: 6px;">چوونەژوورەوە</h2>
            <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 22px;">تکایە هەژمارەکەت هەڵبژێرە</p>

            <button class="btn-google" onclick="triggerGoogleSignIn()">
                <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" width="18" alt="Google">
                <span>چوونەژوورەوە لە ڕێگەی Google</span>
            </button>

            <div style="display: flex; align-items: center; margin-bottom: 20px; color: var(--text-muted); font-size: 12px;">
                <span style="flex:1; border-bottom:1px solid var(--border-glass);"></span>
                <span style="padding: 0 10px;">یان بە بەکارهێنەر</span>
                <span style="flex:1; border-bottom:1px solid var(--border-glass);"></span>
            </div>

            <form id="loginForm">
                <div class="form-group">
                    <label>ناوی بەکارهێنەر</label>
                    <input type="text" id="loginUser" placeholder="admin" required>
                </div>
                <div class="form-group">
                    <label>وشەی نهێنی</label>
                    <input type="password" id="loginPass" placeholder="••••••••" required>
                </div>
                <button type="submit" class="btn-action btn-gradient" style="width: 100%; justify-content: center; padding: 12px;">
                    چوونەژوورەوە
                </button>
            </form>
            <p id="loginErr" style="color: var(--accent-danger); font-size: 13px; margin-top: 12px; display: none;"></p>
        </div>
    </div>

    <!-- ٣. داشبۆردی سەرەکی -->
    <div class="app-view" id="appView">
        <header class="navbar">
            <div style="display: flex; align-items: center; gap: 10px; font-weight: 800; font-size: 18px;">
                <i class="fa-solid fa-cube" style="color: var(--accent-blue);"></i>
                سیستەمی دارایی و قەرزی دانیال
            </div>
            <div style="display: flex; align-items: center; gap: 14px;">
                <button class="btn-action" style="background: rgba(255,255,255,0.06); color: #fff;" onclick="openAuditModal()">
                    <i class="fa-solid fa-shield-halved"></i> لۆگی چاودێری
                </button>
                <div style="display: flex; align-items: center; gap: 10px; padding: 6px 14px; background: var(--surface-glass); border-radius: 30px;">
                    <img src="" id="userAvatar" style="width: 34px; height: 34px; border-radius: 50%; object-fit: cover; border: 2px solid var(--accent-blue);">
                    <span id="userName" style="font-weight: 700; font-size: 13px;"></span>
                </div>
                <button class="btn-action" style="background: rgba(239,68,68,0.15); color: var(--accent-danger);" onclick="logout()">
                    <i class="fa-solid fa-right-from-bracket"></i>
                </button>
            </div>
        </header>

        <main class="main-container">
            <!-- ئاگاداری بەرواری دانەوە -->
            <div id="overdueAlertBanner" style="display: none; background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.3); padding: 14px 20px; border-radius: 16px; margin-bottom: 22px; justify-content: space-between; align-items: center;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <i class="fa-solid fa-triangle-exclamation" style="font-size: 22px; color: var(--accent-danger);"></i>
                    <span id="overdueText" style="font-weight: 600; font-size: 13.5px;"></span>
                </div>
                <button class="btn-action" style="background: var(--accent-danger); color: #fff; font-size: 12px; padding: 6px 14px;" onclick="playChime()">
                    بیستنی دەنگ
                </button>
            </div>

            <!-- کارتەکانی ئامار: دینار و دۆلار -->
            <div class="currency-stats-grid">
                <div class="stat-card-currency card-iqd">
                    <div class="currency-title">
                        <span><i class="fa-solid fa-money-bill-wave"></i> باڵانسی دینار (IQD)</span>
                        <strong style="color: var(--accent-blue);">عێراقی</strong>
                    </div>
                    <div class="currency-row"><span>کۆی قەرز:</span><strong id="iqdTotalDebt">0 د.ع</strong></div>
                    <div class="currency-row"><span>واسڵکراو:</span><strong style="color: var(--accent-success);" id="iqdTotalPaid">0 د.ع</strong></div>
                    <div class="currency-row" style="font-size: 15px; font-weight: 800; margin-top: 10px; border-top: 1px solid var(--border-glass); padding-top: 8px;">
                        <span>ماوەی گشتی:</span><strong style="color: var(--accent-danger);" id="iqdRemaining">0 د.ع</strong>
                    </div>
                </div>

                <div class="stat-card-currency card-usd">
                    <div class="currency-title">
                        <span><i class="fa-solid fa-dollar-sign"></i> باڵانسی دۆلار (USD)</span>
                        <strong style="color: var(--accent-success);">$ ئەمریکی</strong>
                    </div>
                    <div class="currency-row"><span>کۆی قەرز:</span><strong id="usdTotalDebt">$0</strong></div>
                    <div class="currency-row"><span>واسڵکراو:</span><strong style="color: var(--accent-success);" id="usdTotalPaid">$0</strong></div>
                    <div class="currency-row" style="font-size: 15px; font-weight: 800; margin-top: 10px; border-top: 1px solid var(--border-glass); padding-top: 8px;">
                        <span>ماوەی گشتی:</span><strong style="color: var(--accent-danger);" id="usdRemaining">$0</strong>
                    </div>
                </div>
            </div>

            <!-- هێڵکارییە داراییەکان (Charts) -->
            <div class="charts-row">
                <div class="chart-box">
                    <h3><i class="fa-solid fa-chart-column" style="color: var(--accent-blue);"></i> جوڵەی مانگانەی واسڵکراوەکان</h3>
                    <div style="height: 220px;"><canvas id="monthlyChart"></canvas></div>
                </div>
                <div class="chart-box">
                    <h3><i class="fa-solid fa-chart-pie" style="color: var(--accent-purple);"></i> قەرزدارترین کەسەکان</h3>
                    <div style="height: 220px;"><canvas id="debtorsChart"></canvas></div>
                </div>
            </div>

            <!-- کۆنترۆڵەکان -->
            <div class="controls-row">
                <div style="position: relative; min-width: 280px;">
                    <i class="fa-solid fa-magnifying-glass" style="position: absolute; right: 14px; top: 50%; transform: translateY(-50%); color: var(--text-muted);"></i>
                    <input type="text" id="searchInput" placeholder="گەڕان بەپێی ناوی کەس یان مۆبایل..." oninput="loadDebts()"
                           style="width: 100%; padding: 10px 40px 10px 14px; background: rgba(0,0,0,0.3); border: 1px solid var(--border-glass); border-radius: 12px; color: #fff;">
                </div>
                <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                    <button class="btn-action btn-gradient" onclick="openAddDebtModal()">
                        <i class="fa-solid fa-plus"></i> تۆمارکردنی قەرز / قیست
                    </button>
                    <button class="btn-action" style="background: var(--surface-glass); border: 1px solid var(--border-glass); color: #fff;" onclick="location.href='/api/reports/export-excel'">
                        <i class="fa-solid fa-file-excel"></i> هەناردە بۆ Excel
                    </button>
                    <button class="btn-action" style="background: var(--surface-glass); border: 1px solid var(--border-glass); color: #fff;" onclick="location.href='/api/admin/backup'">
                        <i class="fa-solid fa-cloud-arrow-down"></i> باکئەپ (.db)
                    </button>
                </div>
            </div>

            <!-- خشتەی داتاکان -->
            <div class="table-panel">
                <table>
                    <thead>
                        <tr>
                            <th>کۆد</th>
                            <th>ناوی کڕیار</th>
                            <th>واتسئاپ / مۆبایل</th>
                            <th>جۆری دراو</th>
                            <th>کۆی قەرز</th>
                            <th>دراو</th>
                            <th>ماوە</th>
                            <th>قیستە؟</th>
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

    <!-- مۆداڵی زیادکردنی قەرز و قیست -->
    <div class="modal-screen" id="debtModal">
        <div class="modal-body">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px;">
                <h3 style="font-size: 16px;">تۆمارکردنی قەرزی نوێ</h3>
                <i class="fa-solid fa-xmark" style="cursor: pointer;" onclick="closeModal('debtModal')"></i>
            </div>
            <form id="debtForm">
                <div class="form-group">
                    <label>ناوی کەسی قەرزدار *</label>
                    <input type="text" id="custName" list="custSuggestions" required placeholder="ناوی کڕیار بنووسە...">
                    <datalist id="custSuggestions"></datalist>
                </div>
                <div class="form-group">
                    <label>ژمارەی مۆبایل (واتسئاپ)</label>
                    <input type="text" id="custPhone" placeholder="0750 000 0000">
                </div>
                <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 10px;">
                    <div class="form-group">
                        <label>بڕی قەرز *</label>
                        <input type="number" step="any" id="custAmount" required placeholder="100000">
                    </div>
                    <div class="form-group">
                        <label>دراو</label>
                        <select id="custCurrency">
                            <option value="IQD">دینار (IQD)</option>
                            <option value="USD">دۆلار (USD $)</option>
                        </select>
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                    <div class="form-group">
                        <label>بەرواری قەرز</label>
                        <input type="date" id="custDebtDate">
                    </div>
                    <div class="form-group">
                        <label>بەرواری دانەوە (Due Date) *</label>
                        <input type="date" id="custDueDate" required>
                    </div>
                </div>

                <!-- سیستەمی قیستی مانگانە -->
                <div style="background: rgba(255,255,255,0.03); padding: 12px; border-radius: 12px; margin-bottom: 15px; border: 1px solid var(--border-glass);">
                    <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
                        <input type="checkbox" id="isInstallmentCheckbox" onchange="toggleInstallmentInput()">
                        <span style="font-weight: 700; font-size: 13px;">دابەشکردن بەسەر قیستی مانگانەدا</span>
                    </label>
                    <div id="installmentCountWrap" style="display: none; margin-top: 10px;">
                        <label style="font-size: 12px; color: var(--text-muted);">ژمارەی قیستەکان (مانگ):</label>
                        <input type="number" id="custInstallmentCount" value="3" min="2" max="60" style="padding: 8px; border-radius: 8px; background: rgba(0,0,0,0.4); border: 1px solid var(--border-glass); color: #fff; width: 100%;">
                    </div>
                </div>

                <div class="form-group">
                    <label>تێبینی</label>
                    <textarea id="custNote" rows="2" placeholder="کەلوپەل، هۆکار..."></textarea>
                </div>
                <button type="submit" class="btn-action btn-gradient" style="width: 100%; justify-content: center; padding: 12px;">تۆمارکردن</button>
            </form>
        </div>
    </div>

    <!-- مۆداڵی واسڵکردن -->
    <div class="modal-screen" id="payModal">
        <div class="modal-body">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <h3 id="payTitle" style="font-size: 16px;">واڵسکردنی پارە</h3>
                <i class="fa-solid fa-xmark" style="cursor: pointer;" onclick="closeModal('payModal')"></i>
            </div>
            <p id="payRemainingText" style="font-size: 14px; font-weight: 700; color: var(--accent-danger); margin-bottom: 14px;"></p>
            <form id="payForm">
                <input type="hidden" id="payDebtId">
                <div class="form-group">
                    <label>بڕی واسڵکراو *</label>
                    <input type="number" step="any" id="payAmount" required>
                </div>
                <div class="form-group">
                    <label>تێبینی وەسڵ</label>
                    <input type="text" id="payNote" placeholder="وەسڵی کاش، هتد...">
                </div>
                <button type="submit" class="btn-action" style="width: 100%; justify-content: center; background: var(--accent-success); color: #fff; padding: 12px;">
                    وەرگرتن و دەرکردنی وەسڵ
                </button>
            </form>
        </div>
    </div>

    <!-- مۆداڵی لۆگی چاودێری کارمەندان (Audit Logs) -->
    <div class="modal-screen" id="auditModal">
        <div class="modal-body" style="max-width: 650px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <h3 style="font-size: 16px;"><i class="fa-solid fa-shield-halved"></i> لۆگی چاودێریی کارمەندان</h3>
                <i class="fa-solid fa-xmark" style="cursor: pointer;" onclick="closeModal('auditModal')"></i>
            </div>
            <div id="auditLogsContainer" style="max-height: 400px; overflow-y: auto;"></div>
        </div>
    </div>

    <!-- پێکهاتەی وەسڵی گەرمیی بۆ چاپ (Thermal POS Receipt 80mm) -->
    <div id="thermalReceipt">
        <div style="text-align: center; border-bottom: 1px dashed #000; padding-bottom: 8px; margin-bottom: 8px;">
            <h2 style="font-size: 16px; margin: 0;">سیستەمی دانیال</h2>
            <p style="font-size: 11px; margin: 2px 0;">وەسڵی وەرگرتنی پارە (کاش)</p>
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
                <span>بڕی پارەی دراو:</span>
                <span id="recPaid"></span>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 12px; margin-top: 4px;">
                <span>ماوەی قەرز:</span>
                <span id="recRem"></span>
            </div>
        </div>
        <div style="text-align: center; font-size: 10px; margin-top: 10px;">
            <p>سوپاس بۆ مامەڵەکەتان</p>
            <p>نەرمەکاڵای دانیال بۆ حسابات</p>
        </div>
    </div>

    <script>
        let currentUser = null;
        let customerSuggestions = [];
        let monthlyChartInstance = null;
        let debtorsChartInstance = null;

        // ١. لۆجیکی دەستپێک و لۆگین
        let splashTimer = setTimeout(finishSplash, 3000);

        function finishSplash() {
            clearTimeout(splashTimer);
            const splash = document.getElementById('splashScreen');
            splash.style.opacity = '0';
            setTimeout(() => {
                splash.style.display = 'none';
                checkAuth();
            }, 700);
        }

        async function checkAuth() {
            const res = await fetch('/api/auth/me');
            const data = await res.json();
            if (data.logged_in) {
                currentUser = data.user;
                initApp();
            } else {
                document.getElementById('loginWrapper').style.display = 'flex';
                document.getElementById('appView').style.display = 'none';
            }
        }

        function initApp() {
            document.getElementById('loginWrapper').style.display = 'none';
            document.getElementById('appView').style.display = 'flex';
            document.getElementById('userName').textContent = currentUser.full_name;
            document.getElementById('userAvatar').src = currentUser.avatar;
            document.getElementById('custDebtDate').value = new Date().toISOString().split('T')[0];

            loadDashboardAnalytics();
            loadDebts();
            loadCustomerSuggestions();
        }

        // ٢. چوونەژوورەوە
        document.getElementById('loginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
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
                const err = document.getElementById('loginErr');
                err.textContent = data.message;
                err.style.display = 'block';
            }
        });

        function triggerGoogleSignIn() {
            const mock = btoa(JSON.stringify({
                email: "danyal@google.com",
                name: "Danyal User",
                picture: "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150"
            }));
            fetch('/api/auth/google', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ credential: `h.${mock}.s` })
            }).then(r => r.json()).then(d => {
                if (d.status === 'success') {
                    currentUser = d.user;
                    initApp();
                }
            });
        }

        async function logout() {
            await fetch('/api/auth/logout', { method: 'POST' });
            location.reload();
        }

        // ٣. ئامار و هێڵکارییەکان (Analytics & Chart.js)
        async function loadDashboardAnalytics() {
            const res = await fetch('/api/dashboard/analytics');
            const data = await res.json();

            // IQD
            document.getElementById('iqdTotalDebt').textContent = Number(data.iqd.debt).toLocaleString() + " د.ع";
            document.getElementById('iqdTotalPaid').textContent = Number(data.iqd.paid).toLocaleString() + " د.ع";
            document.getElementById('iqdRemaining').textContent = Number(data.iqd.remaining).toLocaleString() + " د.ع";

            // USD
            document.getElementById('usdTotalDebt').textContent = "$" + Number(data.usd.debt).toLocaleString();
            document.getElementById('usdTotalPaid').textContent = "$" + Number(data.usd.paid).toLocaleString();
            document.getElementById('usdRemaining').textContent = "$" + Number(data.usd.remaining).toLocaleString();

            // ئاگاداری قەرزی دواکەوتوو
            if (data.overdue_count > 0 || data.due_today_count > 0) {
                const banner = document.getElementById('overdueAlertBanner');
                banner.style.display = 'flex';
                document.getElementById('overdueText').textContent = 
                    `ئاگاداری: (${data.due_today_count}) قەرز ئەمڕۆ کاتی هاتووە، و (${data.overdue_count}) قەرزی دواکەوتوو هەیە!`;
                playChime();
            }

            renderCharts(data.monthly_chart, data.top_debtors);
        }

        function renderCharts(monthlyData, topDebtors) {
            // هێڵکاری مانگانە
            const ctx1 = document.getElementById('monthlyChart').getContext('2d');
            if (monthlyChartInstance) monthlyChartInstance.destroy();
            monthlyChartInstance = new Chart(ctx1, {
                type: 'bar',
                data: {
                    labels: monthlyData.map(m => m.month),
                    datasets: [{
                        label: 'پارەی وەرگیراو',
                        data: monthlyData.map(m => m.total),
                        backgroundColor: '#0070f3',
                        borderRadius: 6
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });

            // هێڵکاری ٥ گەورەترین قەرزدارەکان
            const ctx2 = document.getElementById('debtorsChart').getContext('2d');
            if (debtorsChartInstance) debtorsChartInstance.destroy();
            debtorsChartInstance = new Chart(ctx2, {
                type: 'doughnut',
                data: {
                    labels: topDebtors.map(d => d.customer_name),
                    datasets: [{
                        data: topDebtors.map(d => d.remaining),
                        backgroundColor: ['#ef4444', '#f59e0b', '#7928ca', '#0070f3', '#10b981']
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });
        }

        // ٤. خشتە و دروستکردنی نامەی واتسئاپ
        async function loadDebts() {
            const search = document.getElementById('searchInput').value;
            const res = await fetch(`/api/debts?search=${encodeURIComponent(search)}`);
            const debts = await res.json();
            const tbody = document.getElementById('debtsBody');
            tbody.innerHTML = '';

            debts.forEach(d => {
                // دروستکردنی لینکی نامەی فەرمی واتسئاپ
                let cleanPhone = (d.phone || '').replace(/[^0-9]/g, '');
                if (cleanPhone.startsWith('07')) cleanPhone = '964' + cleanPhone.substring(1);
                const waMessage = encodeURIComponent(
                    `سڵاو بەڕێز ${d.customer_name}،\nئاگادارتان دەکەینەوە لە سیستەمی دانیال کە بڕی (${Number(d.remaining_amount).toLocaleString()} ${d.currency}) قەرزت ماوە کە بەرواری دانەوەی (${d.due_date})یە.\nسوپاس بۆ مامەڵەکەت.`
                );
                const waLink = cleanPhone ? `https://wa.me/${cleanPhone}?text=${waMessage}` : '#';

                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td style="color: var(--text-muted);">#${d.id}</td>
                    <td style="font-weight: 800;">${d.customer_name}</td>
                    <td>
                        ${cleanPhone ? `
                            <a href="${waLink}" target="_blank" class="btn-whatsapp" title="ناردنی نامەی کوردی">
                                <i class="fa-brands fa-whatsapp"></i> ${d.phone}
                            </a>
                        ` : '-'}
                    </td>
                    <td><strong style="color: ${d.currency === 'USD' ? 'var(--accent-success)' : 'var(--accent-blue)'};">${d.currency}</strong></td>
                    <td>${Number(d.total_amount).toLocaleString()}</td>
                    <td style="color: var(--accent-success);">${Number(d.paid_amount).toLocaleString()}</td>
                    <td style="color: var(--accent-danger); font-weight: 800;">${Number(d.remaining_amount).toLocaleString()}</td>
                    <td>${d.is_installment ? `<span style="color: var(--accent-purple); font-weight: 700;">${d.installment_count} قیست</span>` : 'نەخێر'}</td>
                    <td>${d.due_date}</td>
                    <td>
                        <span style="padding: 3px 8px; border-radius: 6px; font-size: 11px; font-weight: 700; background: ${d.status==='paid'?'rgba(16,185,129,0.15)':d.status==='overdue'?'rgba(239,68,68,0.15)':'rgba(0,112,243,0.15)'}; color: ${d.status==='paid'?'#10b981':d.status==='overdue'?'#ef4444':'#0070f3'};">
                            ${d.status}
                        </span>
                    </td>
                    <td>
                        <div style="display: flex; gap: 6px;">
                            ${d.remaining_amount > 0 ? `
                                <button class="btn-action" style="padding: 4px 8px; font-size: 11px; background: var(--accent-success); color: #fff;" onclick="openPayModal(${d.id}, '${d.customer_name}', ${d.remaining_amount}, '${d.currency}')">
                                    واسڵکردن
                                </button>
                            ` : ''}
                            <button class="btn-action" style="padding: 4px 8px; font-size: 11px; background: rgba(239,68,68,0.15); color: var(--accent-danger);" onclick="deleteDebt(${d.id})">
                                <i class="fa-solid fa-trash"></i>
                            </button>
                        </div>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }

        // ٥. زیادکردنی قەرز
        document.getElementById('debtForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const res = await fetch('/api/debts', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    customer_name: document.getElementById('custName').value.trim(),
                    phone: document.getElementById('custPhone').value.trim(),
                    total_amount: document.getElementById('custAmount').value,
                    currency: document.getElementById('custCurrency').value,
                    debt_date: document.getElementById('custDebtDate').value,
                    due_date: document.getElementById('custDueDate').value,
                    note: document.getElementById('custNote').value.trim(),
                    is_installment: document.getElementById('isInstallmentCheckbox').checked,
                    installment_count: document.getElementById('custInstallmentCount').value
                })
            });
            if (res.ok) {
                closeModal('debtModal');
                document.getElementById('debtForm').reset();
                loadDashboardAnalytics();
                loadDebts();
                loadCustomerSuggestions();
            }
        });

        // ٦. واسڵکردن و چاپی وەسڵ (Thermal 80mm)
        function openPayModal(id, name, remaining, currency) {
            document.getElementById('payDebtId').value = id;
            document.getElementById('payTitle').textContent = `واسڵکردنی پارە بۆ: ${name}`;
            document.getElementById('payRemainingText').textContent = `ماوەی قەرز: ${Number(remaining).toLocaleString()} ${currency}`;
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

                // ڕێکخستنی وەسڵی گەرمیی و فەرمانی چاپ
                const rec = data.receipt;
                document.getElementById('recNo').textContent = `وەسڵ: ${rec.receipt_no}`;
                document.getElementById('recDate').textContent = `بەروار: ${rec.date}`;
                document.getElementById('recCustomer').textContent = rec.customer_name;
                document.getElementById('recPhone').textContent = rec.phone || '-';
                document.getElementById('recUser').textContent = rec.received_by;
                document.getElementById('recPaid').textContent = `${Number(rec.amount_paid).toLocaleString()} ${rec.currency}`;
                document.getElementById('recRem').textContent = `${Number(rec.remaining).toLocaleString()} ${rec.currency}`;

                if (confirm('پارەکە واسڵکرا! ئایا وەسڵی چاپی گەرمیی (Thermal Receipt) چاپ دەکەیت؟')) {
                    window.print();
                }
            } else {
                alert(data.message);
            }
        });

        // ٧. پێشنیاری ناوی کڕیاران
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

        // ٨. لۆگی چاودێری
        async function openAuditModal() {
            const res = await fetch('/api/audit-logs');
            const logs = await res.json();
            const cont = document.getElementById('auditLogsContainer');
            cont.innerHTML = '';
            logs.forEach(l => {
                cont.innerHTML += `
                    <div style="background: rgba(255,255,255,0.03); border: 1px solid var(--border-glass); padding: 10px 14px; border-radius: 10px; margin-bottom: 8px; font-size: 12.5px;">
                        <div style="display: flex; justify-content: space-between; font-weight: 700;">
                            <span style="color: var(--accent-blue);">${l.username} (${l.action})</span>
                            <span style="color: var(--text-muted); font-size: 11px;">${l.created_at}</span>
                        </div>
                        <p style="color: #cbd5e1; margin-top: 4px;">${l.details}</p>
                    </div>
                `;
            });
            document.getElementById('auditModal').style.display = 'flex';
        }

        function toggleInstallmentInput() {
            const chk = document.getElementById('isInstallmentCheckbox');
            document.getElementById('installmentCountWrap').style.display = chk.checked ? 'block' : 'none';
        }

        async function deleteDebt(id) {
            if (confirm('دڵنیایت لە سڕینەوەی ئەم قەرزە و سەرجەم مێژووەکەی؟')) {
                await fetch(`/api/debts/${id}`, { method: 'DELETE' });
                loadDashboardAnalytics();
                loadDebts();
            }
        }

        function openAddDebtModal() { document.getElementById('debtModal').style.display = 'flex'; }
        function closeModal(id) { document.getElementById(id).style.display = 'none'; }
    </script>
</body>
</html>
