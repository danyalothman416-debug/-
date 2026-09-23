<!DOCTYPE html>
<html lang="ckb" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>سیستەمی فرۆشتن و کۆگای دانیال | Mobile POS</title>
    
    <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <style>
        :root {
            --bg: #090b10;
            --surface: rgba(18, 22, 34, 0.85);
            --border: rgba(255, 255, 255, 0.1);
            --primary: #0A84FF;
            --success: #30D158;
            --danger: #FF453A;
            --warning: #FF9F0A;
            --purple: #BF5AF2;
            --text: #FFFFFF;
            --muted: #8E8E93;
            --card-radius: 18px;
            --transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
        }

        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Vazirmatn', sans-serif; -webkit-tap-highlight-color: transparent; }
        body { background: var(--bg); color: var(--text); min-height: 100vh; display: flex; overflow-x: hidden; }

        /* سایدبار لە کۆمپیوتەر و شریتی خوارەوە لە مۆبایل */
        .sidebar {
            width: 250px; background: rgba(14, 17, 27, 0.95);
            border-left: 1px solid var(--border);
            display: flex; flex-direction: column; padding: 20px 14px;
            z-index: 100;
        }

        .brand-header {
            display: flex; align-items: center; gap: 12px;
            margin-bottom: 26px; padding: 0 8px;
        }
        .brand-icon {
            width: 44px; height: 44px; border-radius: 14px;
            background: linear-gradient(135deg, var(--purple), var(--primary));
            display: flex; align-items: center; justify-content: center;
            font-size: 22px; color: #fff; box-shadow: 0 0 20px rgba(10, 132, 255, 0.5);
        }

        .nav-link {
            display: flex; align-items: center; gap: 12px;
            padding: 12px 14px; border-radius: 14px; color: var(--muted);
            text-decoration: none; font-size: 13.5px; font-weight: 700;
            cursor: pointer; transition: var(--transition); margin-bottom: 6px;
        }
        .nav-link:hover, .nav-link.active {
            background: rgba(10, 132, 255, 0.15); color: var(--primary);
        }

        .content-area {
            flex: 1; height: 100vh; overflow-y: auto;
            padding: 20px 24px; display: flex; flex-direction: column;
        }

        /* بەشی سەرووی پەڕە (Top Bar) */
        .topbar {
            display: flex; justify-content: space-between; align-items: center;
            background: var(--surface); border: 1px solid var(--border);
            border-radius: 18px; padding: 12px 20px; margin-bottom: 22px;
            backdrop-filter: blur(20px);
        }

        .lang-switch {
            display: flex; background: rgba(255,255,255,0.06);
            border-radius: 10px; padding: 2px;
        }
        .lang-btn {
            border: none; background: transparent; color: var(--muted);
            padding: 5px 10px; font-size: 12px; font-weight: 700;
            border-radius: 8px; cursor: pointer;
        }
        .lang-btn.active { background: var(--primary); color: #fff; }

        /* شاشەی POS */
        .pos-grid {
            display: grid; grid-template-columns: 1fr 390px;
            gap: 20px; flex: 1;
        }

        .products-grid {
            display: grid; grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
            gap: 14px; max-height: calc(100vh - 180px); overflow-y: auto; padding-left: 4px;
        }

        .product-card {
            background: var(--surface); border: 1px solid var(--border);
            border-radius: 16px; padding: 14px; cursor: pointer;
            transition: var(--transition); display: flex; flex-direction: column;
            justify-content: space-between; position: relative;
        }
        .product-card:hover { transform: translateY(-3px); border-color: var(--primary); }
        .product-card:active { transform: scale(0.97); }

        .prod-category-badge {
            align-self: flex-start; font-size: 10px; font-weight: 700;
            padding: 2px 8px; border-radius: 6px; background: rgba(255,255,255,0.06);
            color: var(--muted); margin-bottom: 6px;
        }

        /* سەبەتەی کڕین (Cart Panel) */
        .cart-panel {
            background: var(--surface); border: 1px solid var(--border);
            border-radius: 22px; padding: 18px; display: flex;
            flex-direction: column; justify-content: space-between;
            max-height: calc(100vh - 180px);
        }

        .cart-items-list {
            flex: 1; overflow-y: auto; margin: 12px 0; padding-left: 4px;
        }

        .cart-row {
            display: flex; align-items: center; justify-content: space-between;
            background: rgba(0,0,0,0.3); border: 1px solid var(--border);
            padding: 10px 12px; border-radius: 12px; margin-bottom: 8px;
        }

        .qty-controls {
            display: flex; align-items: center; gap: 8px;
        }
        .qty-btn {
            width: 26px; height: 26px; border-radius: 8px; border: none;
            background: rgba(255,255,255,0.1); color: #fff; cursor: pointer;
            font-weight: 800;
        }

        /* دوگمەکانی شێوازی پارەدان */
        .pay-method-grid {
            display: grid; grid-template-columns: 1fr 1fr 1fr;
            gap: 8px; margin: 10px 0;
        }
        .pay-pill {
            padding: 10px; border-radius: 12px; border: 1px solid var(--border);
            background: rgba(255,255,255,0.04); color: #fff; font-size: 12px;
            font-weight: 700; text-align: center; cursor: pointer;
        }
        .pay-pill.active {
            background: var(--primary); border-color: var(--primary);
        }

        .btn-checkout {
            width: 100%; padding: 14px; border-radius: 14px; border: none;
            background: var(--success); color: #000; font-size: 15px;
            font-weight: 900; cursor: pointer; box-shadow: 0 4px 15px rgba(48, 209, 88, 0.4);
        }

        /* کارتەکانی داشبۆرد */
        .stats-grid {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px; margin-bottom: 22px;
        }
        .stat-card {
            background: var(--surface); border: 1px solid var(--border);
            border-radius: var(--card-radius); padding: 18px; position: relative;
        }
        .stat-card h4 { font-size: 12px; color: var(--muted); margin-bottom: 6px; }
        .stat-card .val { font-size: 22px; font-weight: 900; }

        /* خشتەکان */
        .table-box {
            background: var(--surface); border: 1px solid var(--border);
            border-radius: var(--card-radius); overflow-x: auto;
        }
        table { width: 100%; border-collapse: collapse; text-align: right; font-size: 13px; }
        th, td { padding: 13px 16px; border-bottom: 1px solid var(--border); }
        th { background: rgba(0,0,0,0.3); color: var(--muted); font-weight: 700; }

        /* مۆداڵ */
        .modal {
            position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
            background: rgba(0,0,0,0.7); backdrop-filter: blur(8px);
            z-index: 10000; display: none; align-items: center; justify-content: center; padding: 16px;
        }
        .modal-body {
            background: #141824; border: 1px solid var(--border);
            border-radius: 24px; width: 100%; max-width: 460px; padding: 24px;
        }

        .form-group { margin-bottom: 12px; text-align: right; }
        .form-group label { display: block; margin-bottom: 5px; font-size: 12px; color: var(--muted); }
        .form-group input, .form-group select {
            width: 100%; padding: 10px 14px; background: rgba(0,0,0,0.35);
            border: 1px solid var(--border); border-radius: 12px; color: #fff; outline: none; font-size: 13.5px;
        }

        /* 80mm پسوڵەی چاپی گەرمیی */
        #thermalInvoice {
            display: none; width: 80mm; padding: 14px; background: #fff;
            color: #000; font-size: 12px; font-family: monospace, 'Vazirmatn';
        }
        @media print {
            body * { visibility: hidden; }
            #thermalInvoice, #thermalInvoice * { visibility: visible; }
            #thermalInvoice { display: block !important; position: absolute; left: 0; top: 0; width: 80mm; }
        }

        /* مۆبایل و شاشەی بچووک */
        @media (max-width: 900px) {
            body { flex-direction: column; padding-bottom: 80px; }
            .sidebar {
                position: fixed; bottom: 0; left: 0; width: 100vw; height: 68px;
                flex-direction: row; justify-content: space-around; padding: 6px;
                border-top: 1px solid var(--border); border-left: none;
            }
            .brand-header { display: none; }
            .nav-link { flex-direction: column; gap: 3px; font-size: 10px; padding: 6px; }
            .nav-link i { font-size: 18px; }
            .pos-grid { grid-template-columns: 1fr; }
            .content-area { height: auto; padding: 14px; }
        }
    </style>
</head>
<body>

    <!-- سایدبار / مینیۆ -->
    <aside class="sidebar">
        <div class="brand-header">
            <div class="brand-icon"><i class="fa-solid fa-mobile-screen-button"></i></div>
            <div>
                <h3 style="font-size: 15px; font-weight: 800;">دانیال مۆبایل</h3>
                <p style="font-size: 11px; color: var(--muted);">POS & Management</p>
            </div>
        </div>

        <nav style="flex:1;">
            <div class="nav-link active" onclick="showTab('tabPos')"><i class="fa-solid fa-cash-register"></i> <span data-i18n="pos">فرۆشتن (POS)</span></div>
            <div class="nav-link" onclick="showTab('tabDashboard')"><i class="fa-solid fa-chart-pie"></i> <span data-i18n="dashboard">داشبۆرد</span></div>
            <div class="nav-link" onclick="showTab('tabProducts')"><i class="fa-solid fa-boxes-stacked"></i> <span data-i18n="stock">کۆگا و کاڵاکان</span></div>
            <div class="nav-link" onclick="showTab('tabDebts')"><i class="fa-solid fa-hand-holding-dollar"></i> <span data-i18n="debts">قەرزەکان</span></div>
            <div class="nav-link" onclick="showTab('tabCustomers')"><i class="fa-solid fa-users"></i> <span data-i18n="customers">کڕیارەکان</span></div>
            <div class="nav-link" onclick="showTab('tabExpenses')"><i class="fa-solid fa-money-bill-transfer"></i> <span data-i18n="expenses">مەسرەف</span></div>
        </nav>

        <div style="border-top: 1px solid var(--border); padding-top: 12px;">
            <div class="nav-link" style="color: var(--danger);" onclick="logout()"><i class="fa-solid fa-arrow-right-from-bracket"></i> <span data-i18n="logout">دەرچوون</span></div>
        </div>
    </aside>

    <!-- ناوەڕۆک -->
    <main class="content-area">
        <header class="topbar">
            <!-- سکانەری بارکۆد -->
            <div style="display: flex; align-items: center; gap: 10px; flex: 1; max-width: 400px;">
                <i class="fa-solid fa-barcode" style="font-size: 20px; color: var(--primary);"></i>
                <input type="text" id="barcodeScanInput" placeholder="بارکۆد سکان بکە یان بنووسە..." 
                       style="width: 100%; padding: 8px 14px; background: rgba(0,0,0,0.3); border: 1px solid var(--border); border-radius: 12px; color: #fff; font-size: 13px;">
            </div>

            <!-- زمانی سێیانە -->
            <div class="lang-switch">
                <button class="lang-btn active" onclick="setLanguage('ckb')">کوردی</button>
                <button class="lang-btn" onclick="setLanguage('ar')">عربي</button>
                <button class="lang-btn" onclick="setLanguage('en')">English</button>
            </div>
        </header>

        <!-- ١. شاشەی فرۆشتن (POS Screen) -->
        <section id="tabPos" class="tab-content">
            <div class="pos-grid">
                <!-- بەشی کاڵاکان -->
                <div>
                    <!-- فلتەری جۆرەکان -->
                    <div style="display: flex; gap: 8px; margin-bottom: 14px; overflow-x: auto; padding-bottom: 4px;">
                        <button class="lang-btn active" onclick="filterCategory('all', this)">هەمووی</button>
                        <button class="lang-btn" onclick="filterCategory('موبایل', this)">مۆبایل</button>
                        <button class="lang-btn" onclick="filterCategory('کاڤەر', this)">کاڤەر</button>
                        <button class="lang-btn" onclick="filterCategory('شەحنکەر', this)">شەحنکەر</button>
                        <button class="lang-btn" onclick="filterCategory('سیمکارت', this)">سیمکارت</button>
                        <button class="lang-btn" onclick="filterCategory('ئەکسسوار', this)">ئەکسسوار</button>
                    </div>

                    <div class="products-grid" id="posProductsContainer"></div>
                </div>

                <!-- بەشی پسوڵە و سەبەتە (Cart Panel) -->
                <div class="cart-panel">
                    <div>
                        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 10px;">
                            <h3 style="font-size: 16px;"><i class="fa-solid fa-receipt" style="color: var(--primary);"></i> سەبەتەی کڕین</h3>
                            <button onclick="clearCart()" style="background: none; border: none; color: var(--danger); font-size: 12px; cursor: pointer;">سڕینەوەی هەمووی</button>
                        </div>

                        <!-- کڕیار -->
                        <div style="margin-top: 12px;">
                            <input type="text" id="posCustName" placeholder="ناوی کڕیار (ئارەزوومەندانە)" style="width: 100%; padding: 8px 12px; background: rgba(0,0,0,0.3); border: 1px solid var(--border); border-radius: 10px; color: #fff; font-size: 12px; margin-bottom: 6px;">
                            <input type="tel" id="posCustPhone" placeholder="ژمارەی مۆبایل (بۆ قەرز پێویستە)" style="width: 100%; padding: 8px 12px; background: rgba(0,0,0,0.3); border: 1px solid var(--border); border-radius: 10px; color: #fff; font-size: 12px;">
                        </div>

                        <div class="cart-items-list" id="cartItemsList"></div>
                    </div>

                    <!-- حیساباتی کۆتایی پسوڵە -->
                    <div style="border-top: 1px solid var(--border); padding-top: 12px;">
                        <div style="display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 4px;">
                            <span style="color: var(--muted);">کۆی گشتی:</span>
                            <strong id="cartSubtotal">$0.00</strong>
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <span style="color: var(--muted); font-size: 13px;">داشکاندن ($):</span>
                            <input type="number" id="cartDiscount" value="0" min="0" oninput="calculateCartTotals()" style="width: 80px; padding: 4px 8px; background: rgba(0,0,0,0.3); border: 1px solid var(--border); border-radius: 8px; color: #fff; text-align: center;">
                        </div>
                        <div style="display: flex; justify-content: space-between; font-size: 16px; font-weight: 900; margin-bottom: 10px;">
                            <span>کۆی پارە:</span>
                            <strong style="color: var(--primary);" id="cartGrandTotal">$0.00</strong>
                        </div>

                        <!-- شێوازی پارەدان: Cash / FIB / FastPay -->
                        <div class="pay-method-grid">
                            <div class="pay-pill active" onclick="setPaymentMethod('Cash', this)"><i class="fa-solid fa-money-bill"></i> Cash</div>
                            <div class="pay-pill" onclick="setPaymentMethod('FIB', this)"><i class="fa-solid fa-building-columns"></i> FIB</div>
                            <div class="pay-pill" onclick="setPaymentMethod('FastPay', this)"><i class="fa-solid fa-bolt"></i> FastPay</div>
                        </div>

                        <div style="display: flex; gap: 8px; margin-bottom: 12px;">
                            <input type="number" id="cartPaidAmount" placeholder="بڕی پارەی دراو" oninput="calculateCartTotals()" style="flex: 1; padding: 10px; background: rgba(0,0,0,0.4); border: 1px solid var(--border); border-radius: 12px; color: #fff; font-size: 13px;">
                            <div style="padding: 10px; background: rgba(255,255,255,0.05); border-radius: 12px; font-size: 12px; text-align: center;">
                                <span style="color: var(--muted); display: block; font-size: 10px;">ماوە (قەرز)</span>
                                <strong id="cartRemainingText" style="color: var(--danger);">$0.00</strong>
                            </div>
                        </div>

                        <button class="btn-checkout" onclick="checkout()"><i class="fa-solid fa-print"></i> تەواوکردن و چاپکردنی پسوڵە</button>
                    </div>
                </div>
            </div>
        </section>

        <!-- ٢. داشبۆرد (Dashboard) -->
        <section id="tabDashboard" class="tab-content" style="display: none;">
            <div class="stats-grid">
                <div class="stat-card">
                    <h4>فرۆشتنی ئەمڕۆ</h4>
                    <div class="val" id="dashTodaySales" style="color: var(--primary);">$0.00</div>
                </div>
                <div class="stat-card">
                    <h4>قازانجی خاوێنی ئەمڕۆ</h4>
                    <div class="val" id="dashTodayProfit" style="color: var(--success);">$0.00</div>
                </div>
                <div class="stat-card">
                    <h4>کۆی قەرز لای خەڵک</h4>
                    <div class="val" id="dashTotalDebt" style="color: var(--danger);">$0.00</div>
                </div>
                <div class="stat-card">
                    <h4>کۆی کاڵاکان</h4>
                    <div class="val" id="dashTotalProducts">0</div>
                </div>
            </div>

            <!-- هێڵکاری فرۆشتن و هۆشداریی کۆگا -->
            <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 20px; margin-bottom: 22px;">
                <div class="table-box" style="padding: 18px;">
                    <h4 style="font-size: 14px; margin-bottom: 12px; color: var(--muted);"><i class="fa-solid fa-chart-line"></i> فرۆشتنی هەفتەی ڕابردوو</h4>
                    <div style="height: 220px;"><canvas id="salesChart"></canvas></div>
                </div>
                <div class="table-box" style="padding: 18px;">
                    <h4 style="font-size: 14px; margin-bottom: 12px; color: var(--warning);"><i class="fa-solid fa-triangle-exclamation"></i> کاڵای بەرەو تەواوبوون</h4>
                    <div id="lowStockList" style="max-height: 220px; overflow-y: auto;"></div>
                </div>
            </div>
        </section>

        <!-- ٣. کۆگا و کاڵاکان (Stock) -->
        <section id="tabProducts" class="tab-content" style="display: none;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <input type="text" id="prodSearchInput" placeholder="گەڕان بەپێی ناو یان بارکۆد..." oninput="loadStockTable()" style="width: 300px; padding: 10px 14px; background: var(--surface); border: 1px solid var(--border); border-radius: 12px; color: #fff;">
                <button onclick="openModal('addProductModal')" style="padding: 10px 18px; border-radius: 12px; border: none; background: var(--primary); color: #fff; font-weight: 700; cursor: pointer;">
                    <i class="fa-solid fa-plus"></i> زیادکردنی کاڵای نوێ
                </button>
            </div>
            <div class="table-box">
                <table>
                    <thead>
                        <tr>
                            <th>بارکۆد</th>
                            <th>ناوی کاڵا</th>
                            <th>جۆر</th>
                            <th>نرخی کڕین</th>
                            <th>نرخی فرۆشتن</th>
                            <th>ژمارەی ماوە</th>
                            <th>دۆخی کۆگا</th>
                            <th>کردار</th>
                        </tr>
                    </thead>
                    <tbody id="stockTableBody"></tbody>
                </table>
            </div>
        </section>

        <!-- ٤. قەرزەکان (Debts) -->
        <section id="tabDebts" class="tab-content" style="display: none;">
            <div class="table-box">
                <table>
                    <thead>
                        <tr>
                            <th>ناوی کڕیار</th>
                            <th>مۆبایل</th>
                            <th>ژ. پسوڵە</th>
                            <th>کۆی قەرز</th>
                            <th>دراو</th>
                            <th>ماوە</th>
                            <th>بەروار</th>
                            <th>کردار</th>
                        </tr>
                    </thead>
                    <tbody id="debtsTableBody"></tbody>
                </table>
            </div>
        </section>

        <!-- ٥. کڕیارەکان (Customers) -->
        <section id="tabCustomers" class="tab-content" style="display: none;">
            <div class="table-box">
                <table>
                    <thead>
                        <tr>
                            <th>کۆد</th>
                            <th>ناوی کڕیار</th>
                            <th>مۆبایل</th>
                            <th>کۆی کڕینەکان</th>
                            <th>قەرزی ماوە</th>
                        </tr>
                    </thead>
                    <tbody id="customersTableBody"></tbody>
                </table>
            </div>
        </section>

        <!-- ٦. مەسرەف (Expenses) -->
        <section id="tabExpenses" class="tab-content" style="display: none;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <h3 style="font-size: 16px;">تۆمارکردنی خەرجی و مەسرەفی دوکان</h3>
                <button onclick="openModal('addExpenseModal')" style="padding: 10px 18px; border-radius: 12px; border: none; background: var(--danger); color: #fff; font-weight: 700; cursor: pointer;">
                    <i class="fa-solid fa-plus"></i> خەرجی نوێ
                </button>
            </div>
            <div class="table-box">
                <table>
                    <thead>
                        <tr>
                            <th>بابەت</th>
                            <th>بڕی پارە</th>
                            <th>جۆر</th>
                            <th>تێبینی</th>
                            <th>بەروار</th>
                        </tr>
                    </thead>
                    <tbody id="expensesTableBody"></tbody>
                </table>
            </div>
        </section>
    </main>

    <!-- مۆداڵی زیادکردنی کاڵا -->
    <div class="modal" id="addProductModal">
        <div class="modal-body">
            <h3 style="margin-bottom: 16px; font-size: 16px;">زیادکردنی کاڵای نوێ بۆ کۆگا</h3>
            <form id="newProductForm" onsubmit="event.preventDefault(); saveProduct();">
                <div class="form-group">
                    <label>بارکۆد (Barcode)</label>
                    <input type="text" id="newProdBarcode" placeholder="سکان بکە یان بەتاڵی جێبێڵە">
                </div>
                <div class="form-group">
                    <label>ناوی کاڵا *</label>
                    <input type="text" id="newProdName" required placeholder="iPhone 15 Case...">
                </div>
                <div class="form-group">
                    <label>جۆری کاڵا</label>
                    <select id="newProdCategory">
                        <option value="موبایل">مۆبایل</option>
                        <option value="کاڤەر">کاڤەر</option>
                        <option value="شەحنکەر">شەحنکەر</option>
                        <option value="سیمکارت">سیمکارت</option>
                        <option value="ئەکسسوار">ئەکسسوار</option>
                    </select>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                    <div class="form-group">
                        <label>نرخی کڕین ($)</label>
                        <input type="number" step="any" id="newProdBuyPrice" required value="0">
                    </div>
                    <div class="form-group">
                        <label>نرخی فرۆشتن ($) *</label>
                        <input type="number" step="any" id="newProdSellPrice" required placeholder="10">
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                    <div class="form-group">
                        <label>ژمارەی کاڵا (Stock)</label>
                        <input type="number" id="newProdStock" value="10" required>
                    </div>
                    <div class="form-group">
                        <label>ئاگاداری کەمبوونەوە</label>
                        <input type="number" id="newProdMinStock" value="3" required>
                    </div>
                </div>
                <div style="display: flex; gap: 8px; margin-top: 10px;">
                    <button type="submit" style="flex:1; padding: 12px; border-radius: 12px; border:none; background: var(--primary); color: #fff; font-weight: 700; cursor: pointer;">پاشەکەوتکردن</button>
                    <button type="button" onclick="closeModal('addProductModal')" style="padding: 12px; border-radius: 12px; border:1px solid var(--border); background: transparent; color: #fff; cursor: pointer;">داخستن</button>
                </div>
            </form>
        </div>
    </div>

    <!-- مۆداڵی واسڵکردنی قەرز -->
    <div class="modal" id="payDebtModal">
        <div class="modal-body">
            <h3 style="margin-bottom: 12px; font-size: 16px;">تۆمارکردنی پارەدانەوەی قەرز</h3>
            <p id="payDebtRemaining" style="color: var(--danger); font-weight: 800; font-size: 15px; margin-bottom: 14px;"></p>
            <form id="payDebtForm" onsubmit="event.preventDefault(); submitDebtPayment();">
                <input type="hidden" id="payDebtId">
                <div class="form-group">
                    <label>بڕی پارەی دراو ($) *</label>
                    <input type="number" step="any" id="payDebtAmount" required>
                </div>
                <div class="form-group">
                    <label>تێبینی</label>
                    <input type="text" id="payDebtNote" placeholder="وەسڵی کاش، هتد...">
                </div>
                <div style="display: flex; gap: 8px; margin-top: 10px;">
                    <button type="submit" style="flex:1; padding: 12px; border-radius: 12px; border:none; background: var(--success); color: #000; font-weight: 700; cursor: pointer;">وەرگرتنی پارە</button>
                    <button type="button" onclick="closeModal('payDebtModal')" style="padding: 12px; border-radius: 12px; border:1px solid var(--border); background: transparent; color: #fff; cursor: pointer;">داخستن</button>
                </div>
            </form>
        </div>
    </div>

    <!-- وەسڵی چاپی گەرمیی 80mm بۆ فرۆشتن -->
    <div id="thermalInvoice">
        <div style="text-align: center; border-bottom: 1px dashed #000; padding-bottom: 8px; margin-bottom: 8px;">
            <h2 style="font-size: 16px; margin: 0;">دانیال مۆبایل</h2>
            <p style="font-size: 11px; margin: 2px 0;">فرۆشتنی مۆبایل و ئەکسسوارات</p>
            <p id="recInvNo" style="font-size: 10px; margin: 0;"></p>
            <p id="recDate" style="font-size: 10px; margin: 0;"></p>
            <p id="recCashier" style="font-size: 10px; margin: 0;"></p>
        </div>
        <div style="font-size: 11px; margin-bottom: 8px;">
            <p><strong>کڕیار:</strong> <span id="recCustomer"></span></p>
        </div>
        <table style="width: 100%; font-size: 11px; border-collapse: collapse; margin-bottom: 8px;">
            <thead>
                <tr style="border-bottom: 1px solid #000;">
                    <th style="text-align: right;">کاڵا</th>
                    <th style="text-align: center;">دانە</th>
                    <th style="text-align: left;">کۆ</th>
                </tr>
            </thead>
            <tbody id="recItemsBody"></tbody>
        </table>
        <div style="border-top: 1px dashed #000; padding-top: 6px; font-size: 11px;">
            <div style="display: flex; justify-content: space-between;"><span>کۆی گشتی:</span><span id="recSubtotal"></span></div>
            <div style="display: flex; justify-content: space-between;"><span>داشکاندن:</span><span id="recDiscount"></span></div>
            <div style="display: flex; justify-content: space-between; font-weight: bold; font-size: 13px; margin: 4px 0;"><span>کۆی کۆتایی:</span><span id="recGrandTotal"></span></div>
            <div style="display: flex; justify-content: space-between;"><span>دراو:</span><span id="recPaid"></span></div>
            <div style="display: flex; justify-content: space-between; color: red;"><span>ماوە (قەرز):</span><span id="recRemaining"></span></div>
            <div style="display: flex; justify-content: space-between; margin-top: 4px;"><span>شێوازی پارەدان:</span><span id="recMethod"></span></div>
        </div>
        <div style="text-align: center; font-size: 10px; margin-top: 12px; border-top: 1px dashed #000; padding-top: 6px;">
            <p>سوپاس بۆ کڕینەکەتان - دانەی فرۆشراو ناگەڕێندرێتەوە</p>
        </div>
    </div>

    <script>
        let allProducts = [];
        let cart = [];
        let currentCategory = 'all';
        let currentPaymentMethod = 'Cash';
        let salesChartInstance = null;

        // فەرهەنگی سێ زمانە
        const i18n = {
            ckb: { pos: "فرۆشتن (POS)", dashboard: "داشبۆرد", stock: "کۆگا و کاڵاکان", debts: "قەرزەکان", customers: "کڕیارەکان", expenses: "مەسرەف", logout: "دەرچوون" },
            ar: { pos: "نقطة البيع (POS)", dashboard: "لوحة التحكم", stock: "المخزن والمنتجات", debts: "الديون", customers: "الزبائن", expenses: "المصاريف", logout: "تسجيل خروج" },
            en: { pos: "Point of Sale", dashboard: "Dashboard", stock: "Inventory", debts: "Debts", customers: "Customers", expenses: "Expenses", logout: "Logout" }
        };

        window.addEventListener('DOMContentLoaded', () => {
            loadPosProducts();
            initBarcodeScannerListener();
        });

        // ناسینەوەی خۆکاری بارکۆد سکانەر
        function initBarcodeScannerListener() {
            let barcodeBuffer = '';
            let lastKeyTime = Date.now();

            window.addEventListener('keydown', (e) => {
                const currentTime = Date.now();
                // ئەگەر نووسینەکە زۆر خێرا بوو (وەک سکانەر)
                if (currentTime - lastKeyTime > 50) {
                    barcodeBuffer = '';
                }
                lastKeyTime = currentTime;

                if (e.key === 'Enter') {
                    if (barcodeBuffer.length >= 3) {
                        e.preventDefault();
                        scanProductByBarcode(barcodeBuffer.trim());
                        barcodeBuffer = '';
                    }
                } else if (e.key.length === 1) {
                    barcodeBuffer += e.key;
                }
            });

            // گەڕانی دەستی لە خانەی سەرەوە
            document.getElementById('barcodeScanInput').addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    scanProductByBarcode(e.target.value.trim());
                    e.target.value = '';
                }
            });
        }

        async function scanProductByBarcode(barcode) {
            try {
                const res = await fetch(`/api/products/scan/${encodeURIComponent(barcode)}`);
                const data = await res.json();
                if (res.ok) {
                    addToCart(data.product);
                } else {
                    alert("کاڵا بەم بارکۆدە نەدۆزرایەوە!");
                }
            } catch(e) {}
        }

        async function loadPosProducts() {
            const res = await fetch('/api/products');
            allProducts = await res.json();
            renderPosProducts();
        }

        function filterCategory(cat, el) {
            currentCategory = cat;
            document.querySelectorAll('#tabPos .lang-btn').forEach(b => b.classList.remove('active'));
            el.classList.add('active');
            renderPosProducts();
        }

        function renderPosProducts() {
            const container = document.getElementById('posProductsContainer');
            container.innerHTML = '';

            let list = allProducts;
            if (currentCategory !== 'all') {
                list = allProducts.filter(p => p.category === currentCategory);
            }

            list.forEach(p => {
                container.innerHTML += `
                    <div class="product-card" onclick='addToCart(${JSON.stringify(p)})'>
                        <div>
                            <span class="prod-category-badge">${p.category}</span>
                            <h4 style="font-size: 13.5px; font-weight: 800; margin-bottom: 6px;">${p.name}</h4>
                            <span style="font-size: 11px; color: var(--muted);">${p.barcode || 'بێ بارکۆد'}</span>
                        </div>
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-top: 10px;">
                            <strong style="color: var(--primary); font-size: 15px;">$${Number(p.sell_price).toLocaleString()}</strong>
                            <span style="font-size: 11px; color: ${p.stock_qty <= p.min_stock_alert ? 'var(--danger)' : 'var(--muted)'};">
                                ماوە: ${p.stock_qty}
                            </span>
                        </div>
                    </div>
                `;
            });
        }

        // کردارەکانی سەبەتەی کڕین
        function addToCart(product) {
            const existing = cart.find(item => item.id === product.id);
            if (existing) {
                if (existing.qty + 1 > product.stock_qty) {
                    alert("ژمارەی ماوە لە کۆگا بەشی ئەم داواکارییە ناکات!");
                    return;
                }
                existing.qty++;
            } else {
                if (product.stock_qty < 1) {
                    alert("ئەم کاڵایە لە کۆگا تەواو بووە!");
                    return;
                }
                cart.push({ ...product, qty: 1 });
            }
            renderCart();
        }

        function updateCartQty(id, delta) {
            const item = cart.find(i => i.id === id);
            if (!item) return;
            item.qty += delta;
            if (item.qty <= 0) {
                cart = cart.filter(i => i.id !== id);
            }
            renderCart();
        }

        function clearCart() {
            cart = [];
            renderCart();
        }

        function renderCart() {
            const list = document.getElementById('cartItemsList');
            list.innerHTML = '';

            cart.forEach(item => {
                list.innerHTML += `
                    <div class="cart-row">
                        <div style="flex:1;">
                            <strong style="font-size: 12.5px;">${item.name}</strong>
                            <span style="display:block; font-size: 11px; color: var(--muted);">$${item.sell_price} × ${item.qty}</span>
                        </div>
                        <div class="qty-controls">
                            <button class="qty-btn" onclick="updateCartQty(${item.id}, -1)">-</button>
                            <span style="font-weight: 800; font-size: 13px;">${item.qty}</span>
                            <button class="qty-btn" onclick="updateCartQty(${item.id}, 1)">+</button>
                        </div>
                        <strong style="margin-right: 12px; font-size: 13px; color: var(--primary);">$${item.sell_price * item.qty}</strong>
                    </div>
                `;
            });

            calculateCartTotals();
        }

        function calculateCartTotals() {
            const subtotal = cart.reduce((sum, i) => sum + (i.sell_price * i.qty), 0);
            const discount = parseFloat(document.getElementById('cartDiscount').value) || 0;
            const grandTotal = Math.max(0, subtotal - discount);

            document.getElementById('cartSubtotal').textContent = `$${subtotal.toLocaleString()}`;
            document.getElementById('cartGrandTotal').textContent = `$${grandTotal.toLocaleString()}`;

            let paid = parseFloat(document.getElementById('cartPaidAmount').value);
            if (isNaN(paid)) paid = grandTotal; // بنەڕەتی پارەی تەواو دەدات

            const remaining = Math.max(0, grandTotal - paid);
            document.getElementById('cartRemainingText').textContent = `$${remaining.toLocaleString()}`;
        }

        function setPaymentMethod(method, el) {
            currentPaymentMethod = method;
            document.querySelectorAll('.pay-pill').forEach(p => p.classList.remove('active'));
            el.classList.add('active');
        }

        // فرۆشتنی کۆتایی و دەرکردنی پسوڵە
        async function checkout() {
            if (cart.length === 0) {
                alert("سەبەتەی کڕین بەتاڵە!");
                return;
            }

            const subtotal = cart.reduce((sum, i) => sum + (i.sell_price * i.qty), 0);
            const discount = parseFloat(document.getElementById('cartDiscount').value) || 0;
            const grandTotal = Math.max(0, subtotal - discount);
            let paid = parseFloat(document.getElementById('cartPaidAmount').value);
            if (isNaN(paid)) paid = grandTotal;

            const custName = document.getElementById('posCustName').value.trim();
            const custPhone = document.getElementById('posCustPhone').value.trim();

            if (paid < grandTotal && !custPhone) {
                alert("ئەگەر پارەکە بە قەرز دەمێنێتەوە، دەبێت ژمارەی مۆبایلی کڕیار بنووسیت!");
                return;
            }

            const res = await fetch('/api/pos/checkout', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    cart: cart,
                    customer_name: custName,
                    customer_phone: custPhone,
                    discount: discount,
                    paid: paid,
                    payment_method: currentPaymentMethod
                })
            });

            const data = await res.json();
            if (res.ok) {
                printThermalInvoice(data.invoice);
                clearCart();
                document.getElementById('posCustName').value = '';
                document.getElementById('posCustPhone').value = '';
                document.getElementById('cartDiscount').value = '0';
                document.getElementById('cartPaidAmount').value = '';
                loadPosProducts();
            } else {
                alert(data.message);
            }
        }

        function printThermalInvoice(inv) {
            document.getElementById('recInvNo').textContent = `Invoice: ${inv.invoice_no}`;
            document.getElementById('recDate').textContent = `Date: ${inv.date}`;
            document.getElementById('recCashier').textContent = `Cashier: ${inv.cashier}`;
            document.getElementById('recCustomer').textContent = inv.customer_name;

            const tbody = document.getElementById('recItemsBody');
            tbody.innerHTML = '';
            inv.items.forEach(i => {
                tbody.innerHTML += `
                    <tr>
                        <td>${i.name}</td>
                        <td style="text-align:center;">${i.qty}</td>
                        <td style="text-align:left;">$${i.sell_price * i.qty}</td>
                    </tr>
                `;
            });

            document.getElementById('recSubtotal').textContent = `$${inv.subtotal}`;
            document.getElementById('recDiscount').textContent = `$${inv.discount}`;
            document.getElementById('recGrandTotal').textContent = `$${inv.grand_total}`;
            document.getElementById('recPaid').textContent = `$${inv.paid}`;
            document.getElementById('recRemaining').textContent = `$${inv.remaining}`;
            document.getElementById('recMethod').textContent = inv.payment_method;

            window.print();
        }

        // گۆڕینی تابەکان
        function showTab(tabId) {
            document.querySelectorAll('.tab-content').forEach(t => t.style.display = 'none');
            document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
            document.getElementById(tabId).style.display = 'block';

            if (tabId === 'tabDashboard') loadDashboard();
            if (tabId === 'tabProducts') loadStockTable();
            if (tabId === 'tabDebts') loadDebtsTable();
            if (tabId === 'tabCustomers') loadCustomersTable();
            if (tabId === 'tabExpenses') loadExpensesTable();
        }

        async function loadDashboard() {
            const res = await fetch('/api/dashboard/stats');
            const data = await res.json();

            document.getElementById('dashTodaySales').textContent = `$${Number(data.today_sales).toLocaleString()}`;
            document.getElementById('dashTodayProfit').textContent = `$${Number(data.today_profit).toLocaleString()}`;
            document.getElementById('dashTotalDebt').textContent = `$${Number(data.total_debt).toLocaleString()}`;
            document.getElementById('dashTotalProducts').textContent = data.total_products;

            // لیستی کاڵای کەمبووەوە
            const lowList = document.getElementById('lowStockList');
            lowList.innerHTML = '';
            data.low_stock_items.forEach(i => {
                lowList.innerHTML += `
                    <div style="display:flex; justify-content:space-between; align-items:center; background:rgba(255,255,255,0.03); padding:8px 12px; border-radius:10px; margin-bottom:6px; font-size:12px;">
                        <span>${i.name}</span>
                        <strong style="color:var(--danger);">ماوە: ${i.stock_qty}</strong>
                    </div>
                `;
            });

            // هێڵکاری
            const ctx = document.getElementById('salesChart').getContext('2d');
            if (salesChartInstance) salesChartInstance.destroy();
            salesChartInstance = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.chart_data.map(d => d.sale_date),
                    datasets: [{
                        label: 'فرۆشتن ($)',
                        data: data.chart_data.map(d => d.daily_total),
                        borderColor: '#0A84FF',
                        backgroundColor: 'rgba(10, 132, 255, 0.1)',
                        fill: true,
                        tension: 0.3
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });
        }

        async function loadStockTable() {
            const q = document.getElementById('prodSearchInput').value;
            const res = await fetch(`/api/products?search=${encodeURIComponent(q)}`);
            const prods = await res.json();
            const tbody = document.getElementById('stockTableBody');
            tbody.innerHTML = '';

            prods.forEach(p => {
                tbody.innerHTML += `
                    <tr>
                        <td><code>${p.barcode || '-'}</code></td>
                        <td><strong>${p.name}</strong></td>
                        <td>${p.category}</td>
                        <td>$${p.buy_price}</td>
                        <td style="color:var(--primary); font-weight:700;">$${p.sell_price}</td>
                        <td style="font-weight:800;">${p.stock_qty}</td>
                        <td>
                            <span style="padding: 3px 8px; border-radius: 6px; font-size: 11px; font-weight:700; background: ${p.stock_qty <= p.min_stock_alert ? 'rgba(255,69,58,0.15)' : 'rgba(48,209,88,0.15)'}; color: ${p.stock_qty <= p.min_stock_alert ? 'var(--danger)' : 'var(--success)'};">
                                ${p.stock_qty <= p.min_stock_alert ? 'کەمبووەتەوە' : 'باشە'}
                            </span>
                        </td>
                        <td>
                            <button onclick="deleteProduct(${p.id})" style="border:none; background:rgba(255,69,58,0.15); color:var(--danger); padding:4px 8px; border-radius:6px; cursor:pointer;"><i class="fa-solid fa-trash"></i></button>
                        </td>
                    </tr>
                `;
            });
        }

        async function saveProduct() {
            const res = await fetch('/api/products', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    barcode: document.getElementById('newProdBarcode').value.trim(),
                    name: document.getElementById('newProdName').value.trim(),
                    category: document.getElementById('newProdCategory').value,
                    buy_price: document.getElementById('newProdBuyPrice').value,
                    sell_price: document.getElementById('newProdSellPrice').value,
                    stock_qty: document.getElementById('newProdStock').value,
                    min_stock_alert: document.getElementById('newProdMinStock').value
                })
            });
            const data = await res.json();
            if (res.ok) {
                closeModal('addProductModal');
                document.getElementById('newProductForm').reset();
                loadStockTable();
                loadPosProducts();
            } else {
                alert(data.message);
            }
        }

        async function deleteProduct(id) {
            if (confirm("دڵنیایت لە سڕینەوەی ئەم کاڵایە لە کۆگا؟")) {
                await fetch(`/api/products/${id}`, { method: 'DELETE' });
                loadStockTable();
                loadPosProducts();
            }
        }

        async function loadDebtsTable() {
            const res = await fetch('/api/debts');
            const debts = await res.json();
            const tbody = document.getElementById('debtsTableBody');
            tbody.innerHTML = '';

            debts.forEach(d => {
                tbody.innerHTML += `
                    <tr>
                        <td><strong>${d.customer_name}</strong></td>
                        <td>${d.customer_phone || '-'}</td>
                        <td><code>${d.invoice_no || '-'}</code></td>
                        <td>$${d.total_amount}</td>
                        <td style="color:var(--success);">$${d.paid_amount}</td>
                        <td style="color:var(--danger); font-weight:800;">$${d.remaining_amount}</td>
                        <td>${d.created_at.split(' ')[0]}</td>
                        <td>
                            <button onclick="openPayDebtModal(${d.id}, '${d.customer_name}', ${d.remaining_amount})" style="border:none; background:var(--success); color:#000; font-weight:700; padding:4px 10px; border-radius:8px; cursor:pointer;">پارەدانەوە</button>
                        </td>
                    </tr>
                `;
            });
        }

        function openPayDebtModal(id, name, remaining) {
            document.getElementById('payDebtId').value = id;
            document.getElementById('payDebtRemaining').textContent = `ماوەی قەرز بۆ (${name}): $${remaining}`;
            document.getElementById('payDebtAmount').max = remaining;
            document.getElementById('payDebtAmount').value = remaining;
            openModal('payDebtModal');
        }

        async function submitDebtPayment() {
            const id = document.getElementById('payDebtId').value;
            const res = await fetch(`/api/debts/${id}/pay`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    amount: document.getElementById('payDebtAmount').value,
                    note: document.getElementById('payDebtNote').value
                })
            });
            if (res.ok) {
                closeModal('payDebtModal');
                loadDebtsTable();
            }
        }

        async function loadCustomersTable() {
            const res = await fetch('/api/customers');
            const custs = await res.json();
            const tbody = document.getElementById('customersTableBody');
            tbody.innerHTML = '';
            custs.forEach(c => {
                tbody.innerHTML += `
                    <tr>
                        <td>#${c.id}</td>
                        <td><strong>${c.name}</strong></td>
                        <td>${c.phone || '-'}</td>
                        <td style="color:var(--primary); font-weight:700;">$${c.total_purchases}</td>
                        <td style="color:var(--danger); font-weight:800;">$${c.total_debt}</td>
                    </tr>
                `;
            });
        }

        async function loadExpensesTable() {
            const res = await fetch('/api/expenses');
            const exps = await res.json();
            const tbody = document.getElementById('expensesTableBody');
            tbody.innerHTML = '';
            exps.forEach(e => {
                tbody.innerHTML += `
                    <tr>
                        <td><strong>${e.title}</strong></td>
                        <td style="color:var(--danger); font-weight:700;">$${e.amount}</td>
                        <td>${e.category}</td>
                        <td>${e.note || '-'}</td>
                        <td>${e.created_at}</td>
                    </tr>
                `;
            });
        }

        function setLanguage(lang) {
            document.querySelectorAll('.lang-switch .lang-btn').forEach(b => b.classList.remove('active'));
            event.target.classList.add('active');

            if (lang === 'en') {
                document.documentElement.dir = 'ltr';
            } else {
                document.documentElement.dir = 'rtl';
            }

            document.querySelectorAll('[data-i18n]').forEach(el => {
                const key = el.getAttribute('data-i18n');
                if (i18n[lang] && i18n[lang][key]) {
                    el.textContent = i18n[lang][key];
                }
            });
        }

        function openModal(id) { document.getElementById(id).style.display = 'flex'; }
        function closeModal(id) { document.getElementById(id).style.display = 'none'; }

        async function logout() {
            await fetch('/api/auth/logout', { method: 'POST' });
            location.reload();
        }
    </script>
</body>
</html>
