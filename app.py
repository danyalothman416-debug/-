<!DOCTYPE html>
<html lang="ckb" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>سیستەمی بەڕێوەبردنی قەرز و حسابات</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;600;700;800;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

    <style>
        :root {
            --bg-body: #0b0f19;
            --surface: #111827;
            --surface-hover: #1f2937;
            --border: rgba(255, 255, 255, 0.08);
            --primary: #3b82f6;
            --primary-hover: #2563eb;
            --danger: #ef4444;
            --success: #10b981;
            --warning: #f59e0b;
            --text: #f9fafb;
            --text-muted: #9ca3af;
            --radius: 14px;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Vazirmatn', sans-serif;
        }

        body {
            background-color: var(--bg-body);
            color: var(--text);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }

        /* بەشی لۆگین */
        .auth-container {
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            padding: 20px;
        }

        .auth-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 24px;
            padding: 40px 32px;
            width: 100%;
            max-width: 420px;
            text-align: center;
            box-shadow: 0 20px 40px rgba(0,0,0,0.5);
        }

        /* ڕووکاری سەرەکی */
        .app-layout {
            display: none;
            flex-direction: column;
            min-height: 100vh;
        }

        /* ناڤبار */
        .navbar {
            background: rgba(17, 24, 39, 0.85);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--border);
            padding: 16px 28px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: sticky;
            top: 0;
            z-index: 50;
        }

        .nav-brand {
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 20px;
            font-weight: 800;
        }

        .nav-brand i { color: var(--primary); }

        .nav-user {
            display: flex;
            align-items: center;
            gap: 16px;
        }

        .user-tag {
            background: rgba(255,255,255,0.05);
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 13px;
            border: 1px solid var(--border);
        }

        /* بەشە سەرەکییەکان */
        .main-content {
            max-width: 1300px;
            width: 100%;
            margin: 24px auto;
            padding: 0 20px;
            flex: 1;
        }

        /* داشبۆرد: کارتەکانی ئامار */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 18px;
            margin-bottom: 24px;
        }

        .stat-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .stat-card h4 {
            font-size: 12px;
            color: var(--text-muted);
            margin-bottom: 8px;
        }

        .stat-card .val {
            font-size: 22px;
            font-weight: 800;
        }

        .stat-icon {
            width: 48px;
            height: 48px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
        }

        /* تابی ئاگادارییەکان */
        .alerts-banner {
            background: rgba(245, 158, 11, 0.1);
            border: 1px solid rgba(245, 158, 11, 0.3);
            border-radius: var(--radius);
            padding: 16px 20px;
            margin-bottom: 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        /* کۆنترۆڵەکان: گەڕان و دوگمەکان */
        .actions-bar {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            gap: 14px;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 16px 20px;
            margin-bottom: 24px;
        }

        .filters-group {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            align-items: center;
        }

        .search-box {
            position: relative;
            min-width: 260px;
        }

        .search-box input {
            width: 100%;
            padding: 9px 38px 9px 14px;
            background: var(--bg-body);
            border: 1px solid var(--border);
            border-radius: 10px;
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

        select, input[type="text"], input[type="password"], input[type="number"], input[type="date"], textarea {
            background: #1f2937;
            border: 1px solid var(--border);
            border-radius: 10px;
            color: #fff;
            padding: 9px 12px;
            outline: none;
            font-size: 13px;
        }

        /* دوگمەکان */
        .btn {
            padding: 9px 16px;
            border-radius: 10px;
            border: none;
            font-size: 13px;
            font-weight: 700;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: 0.2s;
        }

        .btn-primary { background: var(--primary); color: #fff; }
        .btn-primary:hover { background: var(--primary-hover); }

        .btn-success { background: var(--success); color: #fff; }
        .btn-danger { background: var(--danger); color: #fff; }
        .btn-secondary { background: #374151; color: #fff; }
        .btn-secondary:hover { background: #4b5563; }

        /* خشتەی داتاکان */
        .table-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            overflow: hidden;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            text-align: right;
            font-size: 13.5px;
        }

        th {
            background: #172033;
            padding: 14px 18px;
            color: var(--text-muted);
            font-weight: 600;
            border-bottom: 1px solid var(--border);
        }

        td {
            padding: 14px 18px;
            border-bottom: 1px solid var(--border);
            vertical-align: middle;
        }

        tr:hover td {
            background: rgba(255,255,255,0.015);
        }

        /* تاگەکان */
        .badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 700;
        }

        .badge-paid { background: rgba(16, 185, 129, 0.15); color: var(--success); }
        .badge-overdue { background: rgba(239, 68, 68, 0.15); color: var(--danger); }
        .badge-partial { background: rgba(245, 158, 11, 0.15); color: var(--warning); }
        .badge-pending { background: rgba(59, 130, 246, 0.15); color: var(--primary); }

        /* مۆداڵەکان */
        .modal-overlay {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0, 0, 0, 0.75);
            backdrop-filter: blur(4px);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 100;
            padding: 16px;
        }

        .modal-box {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 20px;
            width: 100%;
            max-width: 520px;
            padding: 26px;
            box-shadow: 0 25px 50px rgba(0,0,0,0.6);
        }

        .modal-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--border);
        }

        .form-row {
            margin-bottom: 16px;
        }

        .form-row label {
            display: block;
            margin-bottom: 6px;
            font-size: 12.5px;
            color: var(--text-muted);
            font-weight: 600;
        }

        .form-row input, .form-row select, .form-row textarea {
            width: 100%;
        }

        /* بەشی چاپ / ڕاپۆرت */
        @media print {
            .navbar, .actions-bar, .stats-grid, .alerts-banner, .btn, td:last-child, th:last-child {
                display: none !important;
            }
            body { background: #fff !important; color: #000 !important; }
            .table-card { border: none !important; }
            table { width: 100%; color: #000; }
            th, td { border: 1px solid #ccc !important; padding: 8px !important; }
        }
    </style>
</head>
<body>

    <!-- ١. بەشی چوونەژوورەوە (Login) -->
    <div class="auth-container" id="authSection">
        <div class="auth-card">
            <div style="font-size: 38px; color: var(--primary); margin-bottom: 16px;">
                <i class="fa-solid fa-vault"></i>
            </div>
            <h2 style="font-size: 22px; font-weight: 800; margin-bottom: 8px;">سیستەمی قەرز و حسابات</h2>
            <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 28px;">تکایە ناوی بەکارهێنەر و وشەی نهێنی بنووسە</p>

            <form id="loginForm">
                <div class="form-row" style="text-align: right;">
                    <label>ناوی بەکارهێنەر</label>
                    <input type="text" id="loginUser" required placeholder="admin">
                </div>
                <div class="form-row" style="text-align: right;">
                    <label>وشەی نهێنی</label>
                    <input type="password" id="loginPass" required placeholder="••••••••">
                </div>
                <button type="submit" class="btn btn-primary" style="width: 100%; justify-content: center; padding: 12px; margin-top: 10px;">
                    چوونەژوورەوە
                </button>
            </form>
            <p id="loginError" style="color: var(--danger); font-size: 13px; margin-top: 14px; display: none;"></p>
        </div>
    </div>

    <!-- ٢. ڕووکاری سەرەکیی سیستم -->
    <div class="app-layout" id="appLayout">
        <!-- ناڤبار -->
        <header class="navbar">
            <div class="nav-brand">
                <i class="fa-solid fa-file-invoice-dollar"></i>
                <span>سیستەمی دانیال بۆ بەڕێوەبردنی قەرز</span>
            </div>
            <div class="nav-user">
                <span class="user-tag" id="userRoleBadge"></span>
                <span id="userNameDisplay" style="font-weight: 700; font-size: 14px;"></span>
                <button class="btn btn-secondary" onclick="logout()" title="دەرچوون">
                    <i class="fa-solid fa-right-from-bracket"></i>
                </button>
            </div>
        </header>

        <main class="main-content">
            <!-- ئاگادارییەکانی قەرزی ئەمڕۆ و بەسەرچوو -->
            <div class="alerts-banner" id="alertsBanner" style="display: none;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <i class="fa-solid fa-triangle-exclamation" style="font-size: 24px; color: var(--warning);"></i>
                    <div>
                        <strong style="color: var(--warning);">ئاگاداری بەرواری دانەوە!</strong>
                        <p style="font-size: 13px; color: #d1d5db;" id="alertText"></p>
                    </div>
                </div>
                <button class="btn btn-secondary" style="font-size: 12px;" onclick="filterOverdue()">پیشاندانی دواکەوتووەکان</button>
            </div>

            <!-- کارتەکانی ئامار (Dashboard) -->
            <div class="stats-grid">
                <div class="stat-card">
                    <div>
                        <h4>کۆی گشتی قەرزەکان</h4>
                        <div class="val" id="statTotalDebt">0</div>
                    </div>
                    <div class="stat-icon" style="background: rgba(59, 130, 246, 0.15); color: var(--primary);">
                        <i class="fa-solid fa-coins"></i>
                    </div>
                </div>

                <div class="stat-card">
                    <div>
                        <h4>کۆی پارەی وەرگیراو</h4>
                        <div class="val" style="color: var(--success);" id="statTotalPaid">0</div>
                    </div>
                    <div class="stat-icon" style="background: rgba(16, 185, 129, 0.15); color: var(--success);">
                        <i class="fa-solid fa-circle-check"></i>
                    </div>
                </div>

                <div class="stat-card">
                    <div>
                        <h4>کۆی پارەی ماوە</h4>
                        <div class="val" style="color: var(--danger);" id="statTotalRemaining">0</div>
                    </div>
                    <div class="stat-icon" style="background: rgba(239, 68, 68, 0.15); color: var(--danger);">
                        <i class="fa-solid fa-hand-holding-dollar"></i>
                    </div>
                </div>

                <div class="stat-card">
                    <div>
                        <h4>قەرزی دواکەوتوو</h4>
                        <div class="val" style="color: var(--warning);" id="statOverdueCount">0</div>
                    </div>
                    <div class="stat-icon" style="background: rgba(245, 158, 11, 0.15); color: var(--warning);">
                        <i class="fa-solid fa-clock"></i>
                    </div>
                </div>
            </div>

            <!-- کۆنترۆڵەکان: گەڕان و دوگمەی زیادکردن -->
            <div class="actions-bar">
                <div class="filters-group">
                    <div class="search-box">
                        <i class="fa-solid fa-magnifying-glass"></i>
                        <input type="text" id="searchInput" placeholder="گەڕان بەپێی ناوی کڕیار یان مۆبایل..." oninput="loadDebts()">
                    </div>

                    <select id="statusFilter" onchange="loadDebts()">
                        <option value="">هەموو دۆخەکان</option>
                        <option value="pending">تەواو نەدراوە (Pending)</option>
                        <option value="partial">بەشەکی دراوە (Partial)</option>
                        <option value="overdue">دواکەوتوو (Overdue)</option>
                        <option value="paid">تەواوبوو (Paid)</option>
                    </select>
                </div>

                <div class="filters-group">
                    <button class="btn btn-primary" onclick="openAddDebtModal()">
                        <i class="fa-solid fa-plus"></i> قەرزی نوێ
                    </button>
                    <button class="btn btn-secondary" onclick="exportExcel()">
                        <i class="fa-solid fa-file-excel"></i> ئێکسڵ
                    </button>
                    <button class="btn btn-secondary" onclick="window.print()">
                        <i class="fa-solid fa-print"></i> چاپ / PDF
                    </button>
                    <!-- بەشی تایبەت بە ئەدمین -->
                    <span id="adminControls" style="display: none; gap: 8px;">
                        <button class="btn btn-secondary" onclick="openUserModal()">
                            <i class="fa-solid fa-user-gear"></i> بەکارهێنەر
                        </button>
                        <a href="/api/admin/backup" class="btn btn-secondary" style="text-decoration: none;">
                            <i class="fa-solid fa-database"></i> باکئەپ
                        </a>
                    </span>
                </div>
            </div>

            <!-- خشتەی قەرزەکان -->
            <div class="table-card">
                <table>
                    <thead>
                        <tr>
                            <th>کۆد</th>
                            <th>ناوی کڕیار</th>
                            <th>مۆبایل</th>
                            <th>کۆی قەرز</th>
                            <th>بڕی دراو</th>
                            <th>ماوە</th>
                            <th>بەرواری دانەوە</th>
                            <th>دۆخ</th>
                            <th>کردارەکان</th>
                        </tr>
                    </thead>
                    <tbody id="debtsTableBody">
                        <!-- داتاکان بە شێوەی دینامیکی لێرە بار دەبن -->
                    </tbody>
                </table>
            </div>
        </main>
    </div>

    <!-- مۆداڵی زیادکردنی قەرزی نوێ -->
    <div class="modal-overlay" id="addDebtModal">
        <div class="modal-box">
            <div class="modal-header">
                <h3>تۆمارکردنی قەرزی نوێ</h3>
                <i class="fa-solid fa-xmark" style="cursor: pointer;" onclick="closeModal('addDebtModal')"></i>
            </div>
            <form id="addDebtForm">
                <div class="form-row">
                    <label>ناوی تەواوی کڕیار *</label>
                    <input type="text" id="custName" required placeholder="نموونە: ئارام ئەحمەد">
                </div>
                <div class="form-row">
                    <label>ژمارەی مۆبایل</label>
                    <input type="text" id="custPhone" placeholder="0750 000 0000">
                </div>
                <div class="form-row">
                    <label>بڕی قەرز (دینار) *</label>
                    <input type="number" id="custAmount" required placeholder="نموونە: 150000">
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                    <div class="form-row">
                        <label>بەرواری قەرز</label>
                        <input type="date" id="custDebtDate">
                    </div>
                    <div class="form-row">
                        <label>بەرواری دانەوە (Due Date) *</label>
                        <input type="date" id="custDueDate" required>
                    </div>
                </div>
                <div class="form-row">
                    <label>تێبینی</label>
                    <textarea id="custNote" rows="2" placeholder="هۆکاری قەرز، کاڵاکان..."></textarea>
                </div>
                <button type="submit" class="btn btn-primary" style="width: 100%; justify-content: center; padding: 12px; margin-top: 10px;">
                    تۆمارکردن
                </button>
            </form>
        </div>
    </div>

    <!-- مۆداڵی پارەدانەوە (واڵسکردن) -->
    <div class="modal-overlay" id="paymentModal">
        <div class="modal-box">
            <div class="modal-header">
                <h3 id="payModalTitle">واڵسکردنی پارە</h3>
                <i class="fa-solid fa-xmark" style="cursor: pointer;" onclick="closeModal('paymentModal')"></i>
            </div>
            <div style="background: rgba(255,255,255,0.04); padding: 12px; border-radius: 10px; margin-bottom: 16px;">
                <div style="display: flex; justify-content: space-between; font-size: 13px;">
                    <span>ماوەی پێشوو:</span>
                    <strong id="payModalRemaining" style="color: var(--danger);">0 دینار</strong>
                </div>
            </div>
            <form id="paymentForm">
                <input type="hidden" id="payDebtId">
                <div class="form-row">
                    <label>بڕی پارەی دراو (دینار) *</label>
                    <input type="number" id="payAmount" required placeholder="بڕی پارە...">
                </div>
                <div class="form-row">
                    <label>بەرواری وەرگرتن</label>
                    <input type="date" id="payDate">
                </div>
                <div class="form-row">
                    <label>تێبینی وەسڵ</label>
                    <input type="text" id="payNote" placeholder="وەسڵی ژمارە، شێوازی دان...">
                </div>
                <button type="submit" class="btn btn-success" style="width: 100%; justify-content: center; padding: 12px; margin-top: 10px;">
                    تەواوکردنی واسڵکردن
                </button>
            </form>
        </div>
    </div>

    <!-- مۆداڵی مێژووی هەموو پارەدانەکان -->
    <div class="modal-overlay" id="historyModal">
        <div class="modal-box" style="max-width: 600px;">
            <div class="modal-header">
                <h3 id="historyTitle">مێژووی پارەدانەکان</h3>
                <i class="fa-solid fa-xmark" style="cursor: pointer;" onclick="closeModal('historyModal')"></i>
            </div>
            <div id="historyList" style="max-height: 380px; overflow-y: auto;"></div>
        </div>
    </div>

    <!-- مۆداڵی زیادکردنی بەکارهێنەر (Admin Only) -->
    <div class="modal-overlay" id="userModal">
        <div class="modal-box">
            <div class="modal-header">
                <h3>زیادکردنی بەکارهێنەری نوێ بۆ سیستەم</h3>
                <i class="fa-solid fa-xmark" style="cursor: pointer;" onclick="closeModal('userModal')"></i>
            </div>
            <form id="addUserForm">
                <div class="form-row">
                    <label>ناوی تەواو</label>
                    <input type="text" id="newFullName" required placeholder="ئاراس کەریم">
                </div>
                <div class="form-row">
                    <label>ناوی بەکارهێنەر (Username)</label>
                    <input type="text" id="newUsername" required placeholder="aras">
                </div>
                <div class="form-row">
                    <label>وشەی نهێنی</label>
                    <input type="password" id="newPassword" required placeholder="••••••••">
                </div>
                <div class="form-row">
                    <label>ڕۆڵ / دەسەڵات</label>
                    <select id="newRole">
                        <option value="staff">کارمەند (Staff - تەنها تۆمارکردن و واسڵکردن)</option>
                        <option value="admin">بەڕێوەبەر (Admin - دەسەڵاتی تەواو، سڕینەوە، باکئەپ)</option>
                    </select>
                </div>
                <button type="submit" class="btn btn-primary" style="width: 100%; justify-content: center; padding: 12px; margin-top: 10px;">
                    دروستکردن
                </button>
            </form>
        </div>
    </div>

    <script>
        let currentUser = null;

        // دڵنیابوونەوە لە دۆخی لۆگین لە سەرەتادا
        window.addEventListener('DOMContentLoaded', async () => {
            document.getElementById('custDebtDate').value = new Date().toISOString().split('T')[0];
            document.getElementById('payDate').value = new Date().toISOString().split('T')[0];
            checkAuth();
        });

        async function checkAuth() {
            try {
                const res = await fetch('/api/auth/me');
                const data = await res.json();
                if (data.logged_in) {
                    currentUser = data.user;
                    setupAppLayout();
                } else {
                    showAuth();
                }
            } catch (err) {
                showAuth();
            }
        }

        function showAuth() {
            document.getElementById('authSection').style.display = 'flex';
            document.getElementById('appLayout').style.display = 'none';
        }

        function setupAppLayout() {
            document.getElementById('authSection').style.display = 'none';
            document.getElementById('appLayout').style.display = 'flex';
            document.getElementById('userNameDisplay').textContent = currentUser.full_name;
            
            const badge = document.getElementById('userRoleBadge');
            badge.textContent = currentUser.role === 'admin' ? 'بەڕێوەبەر (Admin)' : 'کارمەند (Staff)';
            badge.style.color = currentUser.role === 'admin' ? 'var(--primary)' : 'var(--text-muted)';

            if (currentUser.role === 'admin') {
                document.getElementById('adminControls').style.display = 'inline-flex';
            }

            loadDashboardStats();
            loadDebts();
        }

        // کرداری چوونەژوورەوە
        document.getElementById('loginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const errEl = document.getElementById('loginError');
            errEl.style.display = 'none';

            const payload = {
                username: document.getElementById('loginUser').value.trim(),
                password: document.getElementById('loginPass').value.trim()
            };

            const res = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            });
            const data = await res.json();

            if (res.ok) {
                currentUser = data.user;
                setupAppLayout();
            } else {
                errEl.textContent = data.message || 'هەڵەیەک ڕوویدا';
                errEl.style.display = 'block';
            }
        });

        async function logout() {
            await fetch('/api/auth/logout', { method: 'POST' });
            location.reload();
        }

        // هێنانی ئامارەکان و ئاگادارییەکان
        async function loadDashboardStats() {
            const res = await fetch('/api/dashboard/stats');
            if (!res.ok) return;
            const data = await res.json();

            document.getElementById('statTotalDebt').textContent = Number(data.total_debt).toLocaleString() + " دینار";
            document.getElementById('statTotalPaid').textContent = Number(data.total_paid).toLocaleString() + " دینار";
            document.getElementById('statTotalRemaining').textContent = Number(data.total_remaining).toLocaleString() + " دینار";
            document.getElementById('statOverdueCount').textContent = data.overdue_count;

            if (data.due_today > 0 || data.overdue_count > 0) {
                const banner = document.getElementById('alertsBanner');
                banner.style.display = 'flex';
                document.getElementById('alertText').textContent = 
                    `ئاگاداری: (${data.due_today}) قەرز بەرواری دانەوەیان ئەمڕۆیە، و (${data.overdue_count}) قەرز کاتیان بەسەرچووە!`;
            }
        }

        // هێنانی خشتەی قەرزەکان لەگەڵ گەڕان و فلتەر
        async function loadDebts() {
            const search = document.getElementById('searchInput').value;
            const status = document.getElementById('statusFilter').value;

            const res = await fetch(`/api/debts?search=${encodeURIComponent(search)}&status=${encodeURIComponent(status)}`);
            const debts = await res.json();

            const tbody = document.getElementById('debtsTableBody');
            tbody.innerHTML = '';

            if (debts.length === 0) {
                tbody.innerHTML = `<tr><td colspan="9" style="text-align: center; color: var(--text-muted); padding: 30px;">هیچ تۆمارێک نەدۆزرایەوە</td></tr>`;
                return;
            }

            const statusMap = {
                paid: { label: 'تەواوبوو', cls: 'badge-paid' },
                overdue: { label: 'دواکەوتوو', cls: 'badge-overdue' },
                partial: { label: 'بەشەکی دراوە', cls: 'badge-partial' },
                pending: { label: 'نەدراوە', cls: 'badge-pending' }
            };

            debts.forEach(d => {
                const badgeInfo = statusMap[d.status] || { label: d.status, cls: 'badge-pending' };
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td style="font-weight: 700; color: var(--text-muted);">#${d.id}</td>
                    <td style="font-weight: 700;">${d.customer_name}</td>
                    <td>${d.phone || '-'}</td>
                    <td>${Number(d.total_amount).toLocaleString()}</td>
                    <td style="color: var(--success); font-weight: 700;">${Number(d.paid_amount).toLocaleString()}</td>
                    <td style="color: var(--danger); font-weight: 800;">${Number(d.remaining_amount).toLocaleString()}</td>
                    <td>${d.due_date}</td>
                    <td><span class="badge ${badgeInfo.cls}">${badgeInfo.label}</span></td>
                    <td>
                        <div style="display: flex; gap: 6px;">
                            ${d.remaining_amount > 0 ? `
                                <button class="btn btn-success" style="padding: 5px 10px; font-size: 11px;" onclick="openPaymentModal(${d.id}, '${d.customer_name}',${d.remaining_amount})">
                                    <i class="fa-solid fa-hand-holding-dollar"></i> واسڵکردن
                                </button>
                            ` : ''}
                            <button class="btn btn-secondary" style="padding: 5px 10px; font-size: 11px;" onclick="viewHistory(${d.id})" title="مێژووی پارەدان">
                                <i class="fa-solid fa-clock-rotate-left"></i>
                            </button>
                            ${currentUser && currentUser.role === 'admin' ? `
                                <button class="btn btn-danger" style="padding: 5px 10px; font-size: 11px;" onclick="deleteDebt(${d.id})" title="سڕینەوە">
                                    <i class="fa-solid fa-trash"></i>
                                </button>
                            ` : ''}
                        </div>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }

        function filterOverdue() {
            document.getElementById('statusFilter').value = 'overdue';
            loadDebts();
        }

        // پاشەکەوتکردنی قەرزی نوێ
        document.getElementById('addDebtForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const payload = {
                customer_name: document.getElementById('custName').value.trim(),
                phone: document.getElementById('custPhone').value.trim(),
                total_amount: document.getElementById('custAmount').value,
                debt_date: document.getElementById('custDebtDate').value,
                due_date: document.getElementById('custDueDate').value,
                note: document.getElementById('custNote').value.trim()
            };

            const res = await fetch('/api/debts', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if (res.ok) {
                closeModal('addDebtModal');
                document.getElementById('addDebtForm').reset();
                document.getElementById('custDebtDate').value = new Date().toISOString().split('T')[0];
                loadDashboardStats();
                loadDebts();
            } else {
                alert(data.message || 'هەڵەیەک ڕوویدا');
            }
        });

        // واسڵکردنی پارە
        function openPaymentModal(debtId, name, remaining) {
            document.getElementById('payDebtId').value = debtId;
            document.getElementById('payModalTitle').textContent = `واڵسکردنی پارە بۆ: ${name}`;
            document.getElementById('payModalRemaining').textContent = `${Number(remaining).toLocaleString()} دینار`;
            document.getElementById('payAmount').max = remaining;
            document.getElementById('paymentModal').style.display = 'flex';
        }

        document.getElementById('paymentForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const debtId = document.getElementById('payDebtId').value;
            const payload = {
                amount: document.getElementById('payAmount').value,
                payment_date: document.getElementById('payDate').value,
                note: document.getElementById('payNote').value.trim()
            };

            const res = await fetch(`/api/debts/${debtId}/payments`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if (res.ok) {
                closeModal('paymentModal');
                document.getElementById('paymentForm').reset();
                document.getElementById('payDate').value = new Date().toISOString().split('T')[0];
                loadDashboardStats();
                loadDebts();
            } else {
                alert(data.message || 'هەڵەیەک ڕوویدا');
            }
        });

        // بینینی مێژووی واسڵکراوەکان
        async function viewHistory(debtId) {
            const res = await fetch(`/api/debts/${debtId}/payments`);
            const data = await res.json();
            if (!res.ok) return;

            document.getElementById('historyTitle').textContent = `مێژووی واسڵکردنی: ${data.debt.customer_name}`;
            const list = document.getElementById('historyList');
            list.innerHTML = '';

            if (data.payments.length === 0) {
                list.innerHTML = `<p style="text-align: center; color: var(--text-muted); padding: 20px;">تا ئێستا هیچ پارەیەک نەدراوەتەوە</p>`;
            } else {
                data.payments.forEach(p => {
                    list.innerHTML += `
                        <div style="background: rgba(255,255,255,0.03); border: 1px solid var(--border); padding: 12px 16px; border-radius: 12px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <strong style="color: var(--success); font-size: 15px;">+ ${Number(p.amount_paid).toLocaleString()} دینار</strong>
                                <p style="font-size: 12px; color: var(--text-muted); margin-top: 3px;">تێبینی: ${p.note || 'بێ تێبینی'}</p>
                                <span style="font-size: 11px; color: #6b7280;">بەروار: ${p.payment_date} | وەرگیراوە لەلایەن: ${p.received_by}</span>
                            </div>
                        </div>
                    `;
                });
            }
            document.getElementById('historyModal').style.display = 'flex';
        }

        // سڕینەوەی قەرز (تەنها Admin)
        async function deleteDebt(debtId) {
            if (!confirm('دڵنیایت لە سڕینەوەی ئەم قەرزە و تەواوی مێژووی واسڵکردنەکەی؟')) return;
            const res = await fetch(`/api/debts/${debtId}`, { method: 'DELETE' });
            if (res.ok) {
                loadDashboardStats();
                loadDebts();
            }
        }

        // زیادکردنی بەکارهێنەری نوێ (Admin)
        document.getElementById('addUserForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const payload = {
                full_name: document.getElementById('newFullName').value.trim(),
                username: document.getElementById('newUsername').value.trim(),
                password: document.getElementById('newPassword').value.trim(),
                role: document.getElementById('newRole').value
            };

            const res = await fetch('/api/admin/users', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if (res.ok) {
                alert('بەکارهێنەرەکە دروستکرا');
                closeModal('userModal');
                document.getElementById('addUserForm').reset();
            } else {
                alert(data.message || 'هەڵەیەک ڕوویدا');
            }
        });

        function exportExcel() {
            window.location.href = '/api/reports/export-excel';
        }

        function openAddDebtModal() { document.getElementById('addDebtModal').style.display = 'flex'; }
        function openUserModal() { document.getElementById('userModal').style.display = 'flex'; }
        function closeModal(id) { document.getElementById(id).style.display = 'none'; }
    </script>
</body>
</html>
