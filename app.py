<!DOCTYPE html>
<html lang="ckb" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>سیستەمی دارایی دانیال | SaaS Platform</title>
    
    <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">

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
            color: var(--ios-text);
            min-height: 100vh;
            padding-bottom: calc(var(--safe-bottom) + 85px);
            user-select: none;
        }

        /* بەشی لۆگین و تۆمارکردن */
        .auth-container {
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            background: #000;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 50000;
            padding: 20px;
        }

        .auth-card {
            width: 100%;
            max-width: 400px;
            background: var(--ios-card);
            border: 1px solid var(--ios-card-border);
            border-radius: 28px;
            padding: 32px 24px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.8);
        }

        .auth-tabs {
            display: flex;
            background: rgba(255,255,255,0.06);
            border-radius: 12px;
            padding: 4px;
            margin-bottom: 22px;
        }

        .auth-tab-btn {
            flex: 1; padding: 8px; border: none; background: transparent;
            color: var(--ios-muted); font-weight: 700; font-size: 13px;
            border-radius: 9px; cursor: pointer;
        }

        .auth-tab-btn.active { background: var(--ios-blue); color: #fff; }

        /* بانەری بەسەرچوونی بەشداریکردن */
        .trial-banner {
            background: rgba(255, 159, 10, 0.15);
            border: 1px solid rgba(255, 159, 10, 0.3);
            border-radius: 14px;
            padding: 10px 14px;
            margin-bottom: 14px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 12px;
            color: var(--ios-orange);
            font-weight: 700;
        }

        .trial-banner.expired {
            background: rgba(255, 69, 58, 0.15);
            border-color: rgba(255, 69, 58, 0.3);
            color: var(--ios-red);
        }

        /* سەرپەڕەی ئەپ */
        .ios-header {
            position: sticky; top: 0; z-index: 100;
            background: rgba(0, 0, 0, 0.75);
            backdrop-filter: blur(20px);
            padding: 14px 18px;
            display: flex; align-items: center; justify-content: space-between;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }

        .app-view {
            display: none;
            padding: 14px 16px;
            max-width: 600px;
            margin: 0 auto;
        }

        .tab-page { display: none; }
        .tab-page.active { display: block; }

        /* کارتەکانی باڵانس (Apple Wallet Style) */
        .wallet-card {
            background: linear-gradient(135deg, #182030, #0f1420);
            border: 1px solid var(--ios-card-border);
            border-radius: 24px;
            padding: 20px;
            margin-bottom: 16px;
            box-shadow: 0 10px 24px rgba(0,0,0,0.4);
        }

        .wallet-balance {
            font-size: 26px; font-weight: 900; color: var(--ios-red); margin: 6px 0 14px;
        }

        .wallet-grid {
            display: grid; grid-template-columns: 1fr 1fr; gap: 10px;
            padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.08);
        }

        .debt-card {
            background: var(--ios-card);
            border: 1px solid var(--ios-card-border);
            border-radius: 20px;
            padding: 16px;
            margin-bottom: 12px;
        }

        .debt-row {
            display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;
        }

        .action-pill {
            flex: 1; padding: 9px; border-radius: 12px; border: none;
            font-size: 12px; font-weight: 700; cursor: pointer;
            display: flex; align-items: center; justify-content: center; gap: 6px;
            text-decoration: none;
        }

        /* شریتی خوارەوەی مۆبایل */
        .ios-tab-bar {
            position: fixed; bottom: 0; left: 0; width: 100vw;
            background: rgba(18, 20, 28, 0.9);
            backdrop-filter: blur(24px);
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
            width: 46px; height: 46px; border-radius: 50%;
            background: linear-gradient(135deg, var(--ios-purple), var(--ios-blue));
            display: flex; align-items: center; justify-content: center;
            color: #fff; font-size: 20px; margin-top: -12px;
            box-shadow: 0 6px 16px rgba(10, 132, 255, 0.4);
        }

        .ios-modal {
            position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
            background: rgba(0,0,0,0.7); backdrop-filter: blur(8px);
            z-index: 20000; display: none; align-items: flex-end; justify-content: center;
        }

        .ios-sheet {
            width: 100%; max-width: 500px; background: #161822;
            border-radius: 28px 28px 0 0; padding: 20px 20px calc(var(--safe-bottom) + 20px);
            max-height: 85vh; overflow-y: auto;
        }

        .form-group { margin-bottom: 12px; text-align: right; }
        .form-group label { display: block; margin-bottom: 6px; font-size: 12px; color: var(--ios-muted); }
        .form-group input, .form-group select, .form-group textarea {
            width: 100%; padding: 12px 14px; background: rgba(255,255,255,0.06);
            border: 1px solid var(--ios-card-border); border-radius: 14px; color: #fff; outline: none; font-size: 14px;
        }

        .btn-ios-submit {
            width: 100%; padding: 14px; border-radius: 16px; border: none;
            background: var(--ios-blue); color: #fff; font-size: 15px; font-weight: 800; cursor: pointer; margin-top: 8px;
        }
    </style>
</head>
<body>

    <!-- ١. پەڕەی لۆگین و دروستکردنی دوکان (Multi-Tenancy Sign Up) -->
    <div class="auth-container" id="authSection">
        <div class="auth-card">
            <div style="text-align: center; margin-bottom: 18px;">
                <div style="width: 60px; height: 60px; background: linear-gradient(135deg, var(--ios-purple), var(--ios-blue)); border-radius: 18px; margin: 0 auto 10px; display: flex; align-items: center; justify-content: center; font-size: 26px;">
                    <i class="fa-solid fa-cube"></i>
                </div>
                <h2 style="font-size: 18px; font-weight: 800;">سیستەمی دارایی دانیال</h2>
                <p style="font-size: 11px; color: var(--ios-muted);">بەڕێوەبردنی تایبەتی قەرزی فرۆشگاکەت</p>
            </div>

            <div class="auth-tabs">
                <button class="auth-tab-btn active" id="btnTabLogin" onclick="switchAuthTab('login')">چوونەژوورەوە</button>
                <button class="auth-tab-btn" id="btnTabRegister" onclick="switchAuthTab('register')">تۆمارکردنی دوکانی نوێ</button>
            </div>

            <!-- فۆڕمی چوونەژوورەوە -->
            <form id="formLogin">
                <div class="form-group">
                    <label>ناوی بەکارهێنەر</label>
                    <input type="text" id="loginUser" required placeholder="admin">
                </div>
                <div class="form-group">
                    <label>وشەی نهێنی</label>
                    <input type="password" id="loginPass" required placeholder="••••••••">
                </div>
                <button type="submit" class="btn-ios-submit">چوونەژوورەوە</button>
            </form>

            <!-- فۆڕمی دوکانی نوێ (١٤ ڕۆژ تاقیکردنەوە) -->
            <form id="formRegister" style="display: none;">
                <div class="form-group">
                    <label>ناوی دوکان / مارکێت *</label>
                    <input type="text" id="regBizName" required placeholder="مارکێتی کوردستان">
                </div>
                <div class="form-group">
                    <label>ناوی خاوەن دوکان *</label>
                    <input type="text" id="regFullName" required placeholder="ئارام ئەحمەد">
                </div>
                <div class="form-group">
                    <label>ژمارەی مۆبایل</label>
                    <input type="tel" id="regPhone" required placeholder="0750 000 0000">
                </div>
                <div class="form-group">
                    <label>ناوی بەکارهێنەر (Username) *</label>
                    <input type="text" id="regUsername" required placeholder="aram_shop">
                </div>
                <div class="form-group">
                    <label>وشەی نهێنی *</label>
                    <input type="password" id="regPassword" required placeholder="••••••••">
                </div>
                <button type="submit" class="btn-ios-submit" style="background: var(--ios-green); color: #000;">
                    دەستپێکردنی ١٤ ڕۆژی بەخۆڕایی
                </button>
            </form>

            <p id="authMsg" style="color: var(--ios-red); font-size: 12px; text-align: center; margin-top: 12px; display: none;"></p>
        </div>
    </div>

    <!-- ٢. ئەپی سەرەکی -->
    <div class="app-view" id="appView">
        <header class="ios-header">
            <div>
                <h3 id="topBizName" style="font-size: 15px; font-weight: 800;">ناوی دوکان</h3>
                <span id="topOwnerName" style="font-size: 11px; color: var(--ios-muted);">خاوەن کار</span>
            </div>
            <button class="action-pill" style="background: rgba(255, 69, 58, 0.15); color: var(--ios-red); flex:0 0 38px; height:38px; border-radius:50%;" onclick="logout()">
                <i class="fa-solid fa-right-from-bracket"></i>
            </button>
        </header>

        <!-- ئاگاداری ماوەی تاقیکردنەوە -->
        <div id="trialBanner" class="trial-banner" style="display: none; margin-top: 14px;">
            <span id="trialText">١٤ ڕۆژ لە تاقیکردنەوەت ماوە</span>
            <a href="tel:07500000000" style="color: inherit; text-decoration: underline;">نوێکردنەوە</a>
        </div>

        <!-- تابی سەرەکی: باڵانس -->
        <div id="tabHome" class="tab-page active">
            <div class="wallet-card">
                <span style="font-size: 12px; color: var(--ios-muted);">کۆی قەرزی ماوە (دینار)</span>
                <div class="wallet-balance" id="iqdRemaining">0 د.ع</div>
                <div class="wallet-grid">
                    <div><span style="font-size: 11px; color: var(--ios-muted);">کۆی گشتی:</span><strong id="iqdTotalDebt">0</strong></div>
                    <div><span style="font-size: 11px; color: var(--ios-muted);">واسڵکراو:</span><strong id="iqdTotalPaid" style="color: var(--ios-green);">0</strong></div>
                </div>
            </div>

            <div class="wallet-card" style="background: linear-gradient(135deg, #13241b, #0d1712);">
                <span style="font-size: 12px; color: var(--ios-muted);">کۆی قەرزی ماوە (دۆلار)</span>
                <div class="wallet-balance" id="usdRemaining">$0</div>
                <div class="wallet-grid">
                    <div><span style="font-size: 11px; color: var(--ios-muted);">کۆی گشتی:</span><strong id="usdTotalDebt">$0</strong></div>
                    <div><span style="font-size: 11px; color: var(--ios-muted);">واسڵکراو:</span><strong id="usdTotalPaid" style="color: var(--ios-green);">$0</strong></div>
                </div>
            </div>

            <div style="background: var(--ios-card); border: 1px solid var(--ios-card-border); border-radius: 20px; padding: 16px;">
                <h4 style="font-size: 12px; margin-bottom: 12px; color: var(--ios-muted);">واڵسکردنی ٦ مانگی ڕابردوو</h4>
                <div style="height: 160px;"><canvas id="monthlyChart"></canvas></div>
            </div>
        </div>

        <!-- تابی قەرزەکان -->
        <div id="tabDebts" class="tab-page">
            <input type="text" id="searchInput" placeholder="گەڕان بەپێی ناوی کەسەکە..." oninput="loadDebts()"
                   style="width: 100%; padding: 12px 14px; background: var(--ios-card); border: 1px solid var(--ios-card-border); border-radius: 14px; color: #fff; font-size: 13px; margin: 10px 0 14px;">
            <div id="debtsCardsContainer"></div>
        </div>

        <!-- تابی ڕاپۆرت -->
        <div id="tabAnalytics" class="tab-page">
            <div style="background: var(--ios-card); border: 1px solid var(--ios-card-border); border-radius: 20px; padding: 16px; margin: 14px 0;">
                <h4 style="font-size: 12px; margin-bottom: 12px; color: var(--ios-muted);">گەورەترین قەرزدارەکان</h4>
                <div style="height: 180px;"><canvas id="debtorsChart"></canvas></div>
            </div>
            <button class="action-pill" style="background: var(--ios-card); border: 1px solid var(--ios-card-border); color: #fff; width: 100%; padding: 14px;" onclick="location.href='/api/reports/export-excel'">
                <i class="fa-solid fa-file-excel" style="color: var(--ios-green);"></i> دابەزاندنی ڕاپۆرتی ئێکسڵ (Excel)
            </button>
        </div>
    </div>

    <!-- شریتی خوارەوە (iOS Tab Bar) -->
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
    </nav>

    <!-- مۆداڵی قەرزی نوێ -->
    <div class="ios-modal" id="debtModal">
        <div class="ios-sheet">
            <h3 style="margin-bottom: 16px; font-size: 16px;">تۆمارکردنی قەرزی نوێ</h3>
            <form id="debtForm" onsubmit="event.preventDefault(); saveNewDebt();">
                <div class="form-group">
                    <label>ناوی کڕیار *</label>
                    <input type="text" id="custName" list="custSuggestions" required placeholder="ناوی کڕیار بنووسە...">
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
                <button type="submit" class="btn-ios-submit" id="btnSaveDebt">پاشەکەوتکردن</button>
                <button type="button" class="btn-ios-submit" style="background: transparent; color: var(--ios-muted);" onclick="closeModal('debtModal')">داخستن</button>
            </form>
        </div>
    </div>

    <!-- مۆداڵی واسڵکردن -->
    <div class="ios-modal" id="payModal">
        <div class="ios-sheet">
            <h3 id="payTitle" style="margin-bottom: 10px; font-size: 16px;">واسڵکردن</h3>
            <p id="payRemainingText" style="color: var(--ios-red); font-weight: 800; font-size: 14px; margin-bottom: 14px;"></p>
            <form id="payForm">
                <input type="hidden" id="payDebtId">
                <div class="form-group">
                    <label>بڕی دراو *</label>
                    <input type="number" step="any" id="payAmount" required>
                </div>
                <button type="submit" class="btn-ios-submit" style="background: var(--ios-green); color: #000;">تەواوکردنی وەرگرتن</button>
                <button type="button" class="btn-ios-submit" style="background: transparent; color: var(--ios-muted);" onclick="closeModal('payModal')">داخستن</button>
            </form>
        </div>
    </div>

    <script>
        let monthlyChartInstance = null;
        let debtorsChartInstance = null;

        window.addEventListener('DOMContentLoaded', checkAuth);

        function switchAuthTab(type) {
            document.getElementById('formLogin').style.display = type === 'login' ? 'block' : 'none';
            document.getElementById('formRegister').style.display = type === 'register' ? 'block' : 'none';
            document.getElementById('btnTabLogin').className = `auth-tab-btn ${type === 'login' ? 'active' : ''}`;
            document.getElementById('btnTabRegister').className = `auth-tab-btn ${type === 'register' ? 'active' : ''}`;
            document.getElementById('authMsg').style.display = 'none';
        }

        async function checkAuth() {
            try {
                const res = await fetch('/api/auth/me');
                const data = await res.json();
                if (data.logged_in) {
                    document.getElementById('authSection').style.display = 'none';
                    document.getElementById('appView').style.display = 'block';
                    document.getElementById('iosTabBar').style.display = 'flex';

                    document.getElementById('topBizName').textContent = data.business.name;
                    document.getElementById('topOwnerName').textContent = data.user.full_name;

                    // ڕێکخستنی بانەری تاقیکردنەوە
                    const banner = document.getElementById('trialBanner');
                    banner.style.display = 'flex';
                    if (data.is_expired) {
                        banner.className = 'trial-banner expired';
                        document.getElementById('trialText').textContent = 'ماوەی تاقیکردنەوەت بەسەرچووە!';
                    } else {
                        document.getElementById('trialText').textContent = `${data.days_left} ڕۆژ لە بەکارهێنانی بەخۆڕایی ماوە`;
                    }

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

        // لۆگین
        document.getElementById('formLogin').addEventListener('submit', async (e) => {
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
                location.reload();
            } else {
                showAuthError(data.message);
            }
        });

        // تۆمارکردنی دوکانی نوێ
        document.getElementById('formRegister').addEventListener('submit', async (e) => {
            e.preventDefault();
            const res = await fetch('/api/auth/register', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    business_name: document.getElementById('regBizName').value.trim(),
                    full_name: document.getElementById('regFullName').value.trim(),
                    phone: document.getElementById('regPhone').value.trim(),
                    username: document.getElementById('regUsername').value.trim(),
                    password: document.getElementById('regPassword').value.trim()
                })
            });
            const data = await res.json();
            if (res.ok) {
                location.reload();
            } else {
                showAuthError(data.message);
            }
        });

        function showAuthError(msg) {
            const el = document.getElementById('authMsg');
            el.textContent = msg;
            el.style.display = 'block';
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

        function closeModal(id) {
            document.getElementById(id).style.display = 'none';
        }

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
                const waLink = cleanPhone ? `https://wa.me/${cleanPhone}?text=${encodeURIComponent(`سڵاو کاک ${d.customer_name}، لە سیستەمی ${document.getElementById('topBizName').textContent} بڕی (${Number(d.remaining_amount).toLocaleString()}${d.currency}) قەرزت ماوە.`)}` : '#';

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
                    due_date: document.getElementById('custDueDate').value
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
                alert(data.message);
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
            } else {
                alert(data.message);
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
