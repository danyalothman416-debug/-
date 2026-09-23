<!DOCTYPE html>
<html lang="ckb" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>دانیال مۆبایل | DANYAL LUXURY POS</title>
    
    <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800;900&family=Plus+Jakarta+Sans:wght@700;800;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">

    <style>
        :root {
            --bg-base: #06070a;
            --surface: rgba(18, 22, 34, 0.72);
            --surface-card: rgba(24, 29, 45, 0.78);
            --border-glass: rgba(255, 255, 255, 0.1);
            --border-highlight: rgba(10, 132, 255, 0.35);
            
            --ios-blue: #0A84FF;
            --ios-green: #30D158;
            --ios-red: #FF453A;
            --ios-purple: #BF5AF2;
            --ios-amber: #FF9F0A;
            --ios-cyan: #64D2FF;
            
            --fib-color: #00b4d8;
            --fastpay-color: #e6007e;
            
            --text-main: #FFFFFF;
            --text-muted: #8E8E93;
            --safe-bottom: env(safe-area-inset-bottom, 20px);
            --safe-top: env(safe-area-inset-top, 20px);
            --transition: all 0.24s cubic-bezier(0.16, 1, 0.3, 1);
        }

        * {
            margin: 0; padding: 0; box-sizing: border-box;
            font-family: 'Vazirmatn', -apple-system, BlinkMacSystemFont, sans-serif;
            -webkit-tap-highlight-color: transparent;
        }

        body {
            background-color: var(--bg-base);
            /* باکگراوندی کوالێتی بەرز و تاریک بۆ ئایفۆن لەگەڵ ڕووناکی Mesh */
            background-image: 
                radial-gradient(circle at 10% 10%, rgba(191, 90, 242, 0.18), transparent 35%),
                radial-gradient(circle at 90% 85%, rgba(10, 132, 255, 0.2), transparent 45%),
                linear-gradient(rgba(6, 7, 10, 0.88), rgba(6, 7, 10, 0.96)),
                url('https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=1600');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            color: var(--text-main);
            min-height: 100vh;
            padding-bottom: calc(var(--safe-bottom) + 85px);
            padding-top: var(--safe-top);
            user-select: none;
            overflow-x: hidden;
        }

        /* ١. دەستپێکی شاهانەی "دانیال مۆبایل" بە ستایلی مۆدێرنی ئەپڵ */
        #splashScreen {
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            background: #000;
            background-image: 
                radial-gradient(circle at center, rgba(121, 40, 202, 0.4), transparent 70%),
                linear-gradient(rgba(0,0,0,0.65), rgba(0,0,0,0.85)),
                url('https://images.unsplash.com/photo-1550684848-fac1c5b4e853?w=1600');
            background-size: cover;
            background-position: center;
            z-index: 99999;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: opacity 0.5s cubic-bezier(0.16, 1, 0.3, 1), transform 0.5s ease;
        }

        .splash-card {
            text-align: center;
            padding: 30px;
        }

        .danyal-brand-logo {
            width: 96px; height: 96px;
            margin: 0 auto 20px;
            border-radius: 28px;
            background: linear-gradient(135deg, var(--ios-purple), var(--ios-blue));
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 44px;
            color: #fff;
            box-shadow: 0 0 50px rgba(10, 132, 255, 0.8), inset 0 1px 1px rgba(255,255,255,0.4);
            animation: pulseGlow 2.5s infinite alternate ease-in-out;
        }

        @keyframes pulseGlow {
            0% { transform: scale(1); box-shadow: 0 0 35px rgba(191, 90, 242, 0.6); }
            100% { transform: scale(1.06); box-shadow: 0 0 65px rgba(10, 132, 255, 0.95); }
        }

        .danyal-title {
            font-size: 30px;
            font-weight: 900;
            background: linear-gradient(180deg, #ffffff, #c7d2fe);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 6px;
            letter-spacing: -0.5px;
        }

        .danyal-sub {
            color: var(--text-muted);
            font-size: 13px;
            margin-bottom: 24px;
        }

        .apple-spinner {
            width: 24px; height: 24px;
            margin: 0 auto;
            border: 3px solid rgba(255, 255, 255, 0.15);
            border-top-color: var(--ios-blue);
            border-radius: 50%;
            animation: spinFast 0.8s linear infinite;
        }

        @keyframes spinFast { to { transform: rotate(360deg); } }

        /* ٢. پەڕەی چوونەژوورەوە */
        .auth-container {
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            background: rgba(0,0,0,0.8);
            backdrop-filter: blur(25px);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 50000;
            padding: 20px;
        }

        .auth-card {
            width: 100%;
            max-width: 380px;
            background: var(--surface);
            border: 1px solid var(--border-glass);
            border-radius: 28px;
            padding: 34px 26px;
            box-shadow: 0 30px 60px rgba(0,0,0,0.8);
            text-align: center;
        }

        /* ٣. سەرپەڕەی مۆبایل (iOS Header) */
        .ios-topbar {
            position: sticky; top: 0; z-index: 100;
            background: rgba(6, 7, 10, 0.78);
            backdrop-filter: blur(25px);
            -webkit-backdrop-filter: blur(25px);
            padding: 12px 18px;
            display: flex; align-items: center; justify-content: space-between;
            border-bottom: 1px solid var(--border-glass);
            margin-bottom: 14px;
        }

        .shop-badge {
            display: flex; align-items: center; gap: 10px;
        }

        .shop-avatar {
            width: 38px; height: 38px; border-radius: 12px;
            background: linear-gradient(135deg, var(--ios-purple), var(--ios-blue));
            display: flex; align-items: center; justify-content: center;
            font-size: 18px; color: #fff;
        }

        /* بەشی گەڕانی خێرا و فلتەری بەشەکان (Horizontal Scroll) */
        .category-scroll {
            display: flex; gap: 8px; overflow-x: auto;
            padding: 0 16px 14px; scrollbar-width: none;
        }
        .category-scroll::-webkit-scrollbar { display: none; }

        .cat-pill {
            flex: 0 0 auto;
            padding: 8px 14px; border-radius: 16px;
            background: var(--surface); border: 1px solid var(--border-glass);
            color: var(--text-muted); font-size: 12.5px; font-weight: 700;
            cursor: pointer; display: flex; align-items: center; gap: 6px;
            transition: var(--transition);
        }
        .cat-pill.active {
            background: var(--ios-blue); color: #fff;
            border-color: var(--ios-blue);
            box-shadow: 0 4px 14px rgba(10, 132, 255, 0.4);
        }

        /* گرید و کارتەکانی کاڵا */
        .products-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
            gap: 12px; padding: 0 16px;
        }

        .item-card {
            background: var(--surface-card);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid var(--border-glass);
            border-radius: 20px;
            padding: 14px;
            cursor: pointer;
            transition: var(--transition);
            display: flex; flex-direction: column; justify-content: space-between;
            position: relative;
            box-shadow: 0 8px 20px rgba(0,0,0,0.3);
        }
        .item-card:active { transform: scale(0.96); }

        .item-badge-cat {
            align-self: flex-start;
            font-size: 10px; font-weight: 800; padding: 3px 8px; border-radius: 8px;
            background: rgba(255,255,255,0.06); color: var(--ios-cyan); margin-bottom: 8px;
        }

        .item-specs-sub {
            font-size: 11px; color: var(--text-muted); margin-bottom: 10px;
            white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
        }

        .item-price-tag {
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 16px; font-weight: 900; color: var(--ios-green);
        }

        /* ٤. شریتی خوارەوەی مۆبایل (Bottom Tab Bar) */
        .ios-tab-bar {
            position: fixed; bottom: 0; left: 0; width: 100vw;
            background: rgba(14, 17, 26, 0.88);
            backdrop-filter: blur(28px);
            -webkit-backdrop-filter: blur(28px);
            border-top: 1px solid var(--border-glass);
            display: flex; justify-content: space-around;
            padding: 8px 0 var(--safe-bottom);
            z-index: 1000;
        }

        .tab-item {
            display: flex; flex-direction: column; align-items: center; gap: 4px;
            color: var(--text-muted); font-size: 10px; font-weight: 700; cursor: pointer; flex: 1;
        }
        .tab-item.active { color: var(--ios-blue); }

        .fab-tab .fab-button {
            width: 48px; height: 48px; border-radius: 50%;
            background: linear-gradient(135deg, var(--ios-purple), var(--ios-blue));
            display: flex; align-items: center; justify-content: center;
            color: #fff; font-size: 20px; margin-top: -14px;
            box-shadow: 0 8px 24px rgba(10, 132, 255, 0.45);
        }

        /* شریتی هەڵکەوتووی سەبەتە (Floating Cart Bar) */
        .floating-cart-bar {
            position: fixed;
            bottom: calc(var(--safe-bottom) + 68px);
            left: 16px; right: 16px;
            background: linear-gradient(135deg, #101626, #161e36);
            border: 1px solid var(--border-highlight);
            border-radius: 20px;
            padding: 12px 18px;
            display: none;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.6);
            z-index: 900;
            cursor: pointer;
            animation: slideUpShort 0.3s ease;
        }
        @keyframes slideUpShort { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }

        /* ٥. مۆداڵەکانی شێوازی کشاوەی خوارەوەی Apple Sheet */
        .ios-modal {
            position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
            background: rgba(0,0,0,0.75); backdrop-filter: blur(14px);
            z-index: 100000; display: none; align-items: flex-end; justify-content: center;
        }

        .ios-sheet {
            width: 100%; max-width: 520px;
            background: #111420;
            border-top: 1px solid var(--border-glass);
            border-radius: 30px 30px 0 0;
            padding: 22px 22px calc(var(--safe-bottom) + 24px);
            max-height: 88vh; overflow-y: auto;
            animation: sheetUp 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        }
        @keyframes sheetUp { from { transform: translateY(100%); } to { transform: translateY(0); } }

        .sheet-drag {
            width: 38px; height: 4px; background: rgba(255,255,255,0.25);
            border-radius: 4px; margin: 0 auto 16px;
        }

        .form-group { margin-bottom: 13px; text-align: right; }
        .form-group label { display: block; margin-bottom: 6px; font-size: 12px; color: var(--text-muted); font-weight: 700; }
        .form-group input, .form-group select, .form-group textarea {
            width: 100%; padding: 12px 14px; background: rgba(255,255,255,0.06);
            border: 1px solid var(--border-glass); border-radius: 14px; color: #fff; outline: none; font-size: 14px;
        }

        .btn-ios-submit {
            width: 100%; padding: 14px; border-radius: 16px; border: none;
            background: var(--ios-blue); color: #fff; font-size: 15px; font-weight: 800; cursor: pointer; margin-top: 10px;
            box-shadow: 0 6px 20px rgba(10, 132, 255, 0.4);
        }

        /* دوگمەی پارەدان بە فاستپەی و FIB و کاش */
        .pay-pill-btn {
            flex: 1; padding: 10px; border-radius: 12px; border: 1px solid var(--border-glass);
            background: rgba(255,255,255,0.04); color: #fff; font-size: 12px; font-weight: 800;
            text-align: center; cursor: pointer;
        }
        .pay-pill-btn.active.pay-cash { background: var(--ios-green); color: #000; border-color: var(--ios-green); }
        .pay-pill-btn.active.pay-fib { background: var(--fib-color); color: #000; border-color: var(--fib-color); }
        .pay-pill-btn.active.pay-fastpay { background: var(--fastpay-color); color: #fff; border-color: var(--fastpay-color); }

        #thermalInvoice { display: none; width: 80mm; padding: 14px; background: #fff; color: #000; font-size: 12px; font-family: monospace; }
        @media print {
            body * { visibility: hidden; }
            #thermalInvoice, #thermalInvoice * { visibility: visible; }
            #thermalInvoice { display: block !important; position: absolute; left: 0; top: 0; width: 80mm; }
        }
    </style>
</head>
<body>

    <!-- ١. دەستپێکی درەوشاوەی "دانیال مۆبایل" بە ستایلی مۆدێرنی ئەپڵ -->
    <div id="splashScreen">
        <div class="splash-card">
            <div class="danyal-brand-logo">
                <i class="fa-solid fa-mobile-screen-button"></i>
            </div>
            <h1 class="danyal-title">دانیال مۆبایل</h1>
            <p class="danyal-sub">سیستەمی پێشکەوتووی فرۆشتن و کۆگا</p>
            <div class="apple-spinner"></div>
        </div>
    </div>

    <!-- ٢. پەڕەی چوونەژوورەوە -->
    <div class="auth-container" id="authSection">
        <div class="auth-card">
            <div style="width: 60px; height: 60px; background: linear-gradient(135deg, var(--ios-purple), var(--ios-blue)); border-radius: 18px; margin: 0 auto 12px; display: flex; align-items: center; justify-content: center; font-size: 26px; color: #fff;">
                <i class="fa-solid fa-store"></i>
            </div>
            <h2 style="font-size: 18px; font-weight: 800; margin-bottom: 4px;">دانیال مۆبایل</h2>
            <p style="font-size: 12px; color: var(--text-muted); margin-bottom: 20px;">تکایە ناوی بەکارهێنەر بنووسە</p>

            <form id="authForm" onsubmit="event.preventDefault(); submitAuth();">
                <div class="form-group">
                    <label>ناوی بەکارهێنەر</label>
                    <input type="text" id="userInput" required placeholder="admin">
                </div>
                <div class="form-group">
                    <label>وشەی نهێنی</label>
                    <input type="password" id="passInput" required placeholder="••••••••">
                </div>
                <button type="submit" class="btn-ios-submit" id="btnSubmitAuth">چوونەژوورەوە</button>
            </form>
            <p id="authErrorMsg" style="color: var(--ios-red); font-size: 12px; margin-top: 12px; display: none;"></p>
        </div>
    </div>

    <!-- ٣. ئەپی سەرەکیی مۆبایل -->
    <div id="appView" style="display: none;">
        <!-- سەرپەڕە -->
        <header class="ios-topbar">
            <div class="shop-badge">
                <div class="shop-avatar"><i class="fa-solid fa-mobile-retro"></i></div>
                <div>
                    <h3 id="topShopName" style="font-size: 15px; font-weight: 900;">دانیال مۆبایل</h3>
                    <p style="font-size: 11px; color: var(--ios-green); font-weight: 700;">● سیستەم ئۆنلاینە</p>
                </div>
            </div>
            <div style="display: flex; gap: 8px;">
                <button onclick="openModal('addItemModal')" style="width: 38px; height: 38px; border-radius: 50%; border:none; background: var(--ios-blue); color: #fff; font-size: 16px; cursor: pointer;">
                    <i class="fa-solid fa-plus"></i>
                </button>
                <button onclick="logout()" style="width: 38px; height: 38px; border-radius: 50%; border:none; background: rgba(255, 69, 58, 0.15); color: var(--ios-red); cursor: pointer;">
                    <i class="fa-solid fa-right-from-bracket"></i>
                </button>
            </div>
        </header>

        <!-- تابی سەرەکی: فرۆشتن (POS) -->
        <div id="tabPos" class="tab-content active">
            <!-- گەڕان -->
            <div style="padding: 0 16px 12px;">
                <input type="text" id="searchInput" placeholder="گەڕان بەپێی ناوی مۆبایل، سیمکارت، یان بارکۆد..." oninput="loadProducts()"
                       style="width: 100%; padding: 12px 16px; background: var(--surface); border: 1px solid var(--border-glass); border-radius: 16px; color: #fff; font-size: 13px;">
            </div>

            <!-- فلتەری خێرای بەشەکان -->
            <div class="category-scroll">
                <div class="cat-pill active" onclick="filterCategory('all', this)"><i class="fa-solid fa-grid-2"></i> هەمووی</div>
                <div class="cat-pill" onclick="filterCategory('موبایل', this)"><i class="fa-solid fa-mobile-screen"></i> مۆبایل</div>
                <div class="cat-pill" onclick="filterCategory('سیمکارت', this)"><i class="fa-solid fa-sim-card"></i> سیمکارت</div>
                <div class="cat-pill" onclick="filterCategory('شەحنکەر', this)"><i class="fa-solid fa-bolt"></i> شەحنکەر</div>
                <div class="cat-pill" onclick="filterCategory('کاڤەر', this)"><i class="fa-solid fa-shield"></i> کاڤەر و لەزگە</div>
                <div class="cat-pill" onclick="filterCategory('ئەکسسوار', this)"><i class="fa-solid fa-headphones"></i> ئەکسسوارات</div>
            </div>

            <!-- لیستی کاڵاکان لەسەر ستایلی کاتی ئایفۆن -->
            <div class="products-grid" id="productsGrid"></div>
        </div>

        <!-- تابی کۆگا و بەڕێوەبردن (Stock) -->
        <div id="tabStock" class="tab-content" style="display: none; padding: 0 16px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
                <h3 style="font-size: 16px; font-weight: 800;">کۆگای گشتی</h3>
                <button onclick="openModal('addItemModal')" style="padding: 8px 14px; border-radius: 12px; border:none; background: var(--ios-blue); color: #fff; font-weight: 700; font-size: 12px;">
                    + کاڵای نوێ
                </button>
            </div>
            <div id="stockListContainer"></div>
        </div>

        <!-- تابی داشبۆرد و ئامار -->
        <div id="tabDashboard" class="tab-content" style="display: none; padding: 0 16px;">
            <div style="background: linear-gradient(135deg, #182030, #0f1420); border: 1px solid var(--border-glass); border-radius: 22px; padding: 20px; margin-bottom: 14px;">
                <span style="font-size: 12px; color: var(--text-muted);">فرۆشتنی ئەمڕۆ</span>
                <div style="font-size: 28px; font-weight: 900; color: var(--ios-green); margin: 6px 0;" id="dashSales">$0.00</div>
                <div style="display: flex; justify-content: space-between; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.08); font-size: 12px;">
                    <span>قازانجی خاوێن: <strong id="dashProfit" style="color: var(--ios-cyan);">$0.00</strong></span>
                    <span>قەرزی ماوە: <strong id="dashDebt" style="color: var(--ios-red);">$0.00</strong></span>
                </div>
            </div>
        </div>

        <!-- تابی قەرزەکان -->
        <div id="tabDebts" class="tab-content" style="display: none; padding: 0 16px;">
            <h3 style="font-size: 16px; font-weight: 800; margin-bottom: 12px;">قەرزەکانی کڕیاران</h3>
            <div id="debtsContainer"></div>
        </div>

        <!-- شریتی سەرئاوکەوتووی سەبەتە (Floating Cart Pill) -->
        <div class="floating-cart-bar" id="floatingCart" onclick="openModal('cartModal')">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="background: var(--ios-blue); width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 13px;" id="cartCountBadge">0</div>
                <span style="font-size: 13px; font-weight: 700;">سەبەتەی کڕین</span>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <strong style="color: var(--ios-green); font-size: 16px;" id="cartFloatingTotal">$0</strong>
                <i class="fa-solid fa-chevron-left" style="font-size: 12px; color: var(--text-muted);"></i>
            </div>
        </div>
    </div>

    <!-- ٤. شریتی خوارەوەی مۆبایل (Bottom Tab Bar) -->
    <nav class="ios-tab-bar" id="iosTabBar" style="display: none;">
        <div class="tab-item active" onclick="switchTab('tabPos', this)">
            <i class="fa-solid fa-cash-register"></i><span>فرۆشتن</span>
        </div>
        <div class="tab-item" onclick="switchTab('tabStock', this)">
            <i class="fa-solid fa-boxes-stacked"></i><span>کۆگا</span>
        </div>
        <div class="tab-item fab-tab" onclick="openModal('addItemModal')">
            <div class="fab-button"><i class="fa-solid fa-plus"></i></div>
            <span>زیادکردن</span>
        </div>
        <div class="tab-item" onclick="switchTab('tabDebts', this)">
            <i class="fa-solid fa-hand-holding-dollar"></i><span>قەرزەکان</span>
        </div>
        <div class="tab-item" onclick="switchTab('tabDashboard', this)">
            <i class="fa-solid fa-chart-pie"></i><span>داشبۆرد</span>
        </div>
    </nav>

    <!-- ٥. پەنجەرەی مۆدێرنی زیادکردنی کاڵا بە جیاوازی بۆ مۆبایل، سیمکارت، شەحنکەر -->
    <div class="ios-modal" id="addItemModal">
        <div class="ios-sheet">
            <div class="sheet-drag"></div>
            <h3 style="margin-bottom: 14px; font-size: 17px; font-weight: 900;">زیادکردنی کاڵای نوێ بۆ کۆگا</h3>
            
            <!-- هەڵبژاردنی جۆری کاڵا -->
            <div style="display: flex; gap: 6px; overflow-x: auto; margin-bottom: 16px; padding-bottom: 4px;">
                <button type="button" class="cat-pill active" id="pillMob" onclick="switchAddCategory('موبایل')">📱 مۆبایل</button>
                <button type="button" class="cat-pill" id="pillSim" onclick="switchAddCategory('سیمکارت')">📶 سیمکارت</button>
                <button type="button" class="cat-pill" id="pillCharge" onclick="switchAddCategory('شەحنکەر')">🔌 شەحنکەر</button>
                <button type="button" class="cat-pill" id="pillCover" onclick="switchAddCategory('کاڤەر')">🛡️ کاڤەر و لەزگە</button>
                <button type="button" class="cat-pill" id="pillAcc" onclick="switchAddCategory('ئەکسسوار')">🎧 ئەکسسوار</button>
            </div>

            <form id="addItemForm" onsubmit="event.preventDefault(); submitAddProduct();">
                <input type="hidden" id="itemCatInput" value="موبایل">

                <div class="form-group">
                    <label id="itemNameLabel">ناوی مۆبایل *</label>
                    <input type="text" id="itemName" required placeholder="iPhone 15 Pro Max...">
                </div>

                <!-- خانەی تایبەت بە مۆبایل: بیرگە و ڕەنگ -->
                <div id="mobFields" style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                    <div class="form-group">
                        <label>بیرگە (Storage)</label>
                        <select id="mobStorage">
                            <option value="128GB">128 GB</option>
                            <option value="256GB" selected>256 GB</option>
                            <option value="512GB">512 GB</option>
                            <option value="1TB">1 TB</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>ڕەنگ</label>
                        <input type="text" id="mobColor" placeholder="تایتانیۆم، ڕەش...">
                    </div>
                </div>

                <!-- خانەی تایبەت بە سیمکارت: کۆمپانیا و ژمارە -->
                <div id="simFields" style="display: none; grid-template-columns: 1fr 1fr; gap: 8px;">
                    <div class="form-group">
                        <label>کۆمپانیا</label>
                        <select id="simOperator">
                            <option value="ئاسیاسێڵ">ئاسیاسێڵ (Asiacell)</option>
                            <option value="کۆڕەک">کۆڕەک (Korek)</option>
                            <option value="فاستلینک">فاستلینک (Fastlink)</option>
                            <option value="زین">زین (Zain)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>ژمارەی سیمکارت</label>
                        <input type="tel" id="simNumber" placeholder="0770 000 0000">
                    </div>
                </div>

                <!-- خانەی تایبەت بە شەحنکەر: هێز/وات -->
                <div id="chargeFields" style="display: none;">
                    <div class="form-group">
                        <label>هێزی شەحن (Watt / Type)</label>
                        <input type="text" id="chargeSpecs" placeholder="20W Type-C Original...">
                    </div>
                </div>

                <!-- نرخ و کۆگا -->
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                    <div class="form-group">
                        <label>نرخی کڕین ($)</label>
                        <input type="number" step="any" id="itemBuyPrice" required value="0">
                    </div>
                    <div class="form-group">
                        <label>نرخی فرۆشتن ($) *</label>
                        <input type="number" step="any" id="itemSellPrice" required placeholder="10">
                    </div>
                </div>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                    <div class="form-group">
                        <label>ژمارەی ماوە لە کۆگا</label>
                        <input type="number" id="itemStock" value="5" required>
                    </div>
                    <div class="form-group">
                        <label>بارکۆد (ئارەزوومەندانە)</label>
                        <input type="text" id="itemBarcode" placeholder="سکان یان کۆد">
                    </div>
                </div>

                <button type="submit" class="btn-ios-submit" id="btnAddSubmit">پاشەکەوتکردنی کاڵا</button>
                <button type="button" class="btn-ios-submit" style="background: transparent; color: var(--text-muted); box-shadow: none;" onclick="closeModal('addItemModal')">داخستن</button>
            </form>
        </div>
    </div>

    <!-- ٦. پەنجەرەی مۆدێرنی سەبەتەی کڕین (Cart Modal) -->
    <div class="ios-modal" id="cartModal">
        <div class="ios-sheet">
            <div class="sheet-drag"></div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
                <h3 style="font-size: 17px; font-weight: 900;">سەبەتەی کڕین و پسوڵە</h3>
                <span onclick="clearCart()" style="color: var(--ios-red); font-size: 12px; font-weight: 700; cursor: pointer;">سڕینەوەی هەمووی</span>
            </div>

            <!-- کڕیار -->
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 12px;">
                <input type="text" id="cartCustName" placeholder="ناوی کڕیار" style="padding: 10px 12px; background: rgba(255,255,255,0.06); border: 1px solid var(--border-glass); border-radius: 12px; color: #fff; font-size: 13px;">
                <input type="tel" id="cartCustPhone" placeholder="مۆبایل (بۆ قەرز)" style="padding: 10px 12px; background: rgba(255,255,255,0.06); border: 1px solid var(--border-glass); border-radius: 12px; color: #fff; font-size: 13px;">
            </div>

            <div id="cartItemsContainer" style="max-height: 200px; overflow-y: auto; margin-bottom: 14px;"></div>

            <!-- هەڵبژاردنی پارەدان بە فاستپەی، FIB یان کاش -->
            <div style="display: flex; gap: 6px; margin-bottom: 12px;">
                <div class="pay-pill-btn active pay-cash" onclick="setPaymentMethod('Cash', this)"><i class="fa-solid fa-money-bill"></i> Cash</div>
                <div class="pay-pill-btn pay-fib" onclick="setPaymentMethod('FIB', this)"><i class="fa-solid fa-building-columns"></i> FIB</div>
                <div class="pay-pill-btn pay-fastpay" onclick="setPaymentMethod('FastPay', this)"><i class="fa-solid fa-bolt"></i> FastPay</div>
            </div>

            <!-- حیسابات -->
            <div style="background: rgba(0,0,0,0.3); padding: 12px; border-radius: 14px; margin-bottom: 12px;">
                <div style="display:flex; justify-content:space-between; font-size: 13px; margin-bottom: 4px;">
                    <span style="color: var(--text-muted);">کۆی گشتی:</span>
                    <strong id="cartSubtotalText">$0.00</strong>
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 4px;">
                    <span style="color: var(--text-muted); font-size: 13px;">داشکاندن ($):</span>
                    <input type="number" id="cartDiscount" value="0" min="0" oninput="updateCartTotals()" style="width: 70px; padding: 4px; background: rgba(255,255,255,0.08); border: 1px solid var(--border-glass); border-radius: 8px; color: #fff; text-align: center;">
                </div>
                <div style="display:flex; justify-content:space-between; font-size: 16px; font-weight: 900; color: var(--ios-green);">
                    <span>کۆی کۆتایی:</span>
                    <span id="cartGrandTotalText">$0.00</span>
                </div>
            </div>

            <div style="display: flex; gap: 8px; margin-bottom: 12px;">
                <input type="number" id="cartPaidInput" placeholder="بڕی دراو" oninput="updateCartTotals()" style="flex:1; padding: 12px; background: rgba(255,255,255,0.06); border: 1px solid var(--border-glass); border-radius: 14px; color: #fff; font-size: 13px;">
                <div style="padding: 10px 14px; background: rgba(255,69,58,0.15); border-radius: 14px; text-align: center;">
                    <span style="font-size: 10px; color: var(--ios-red); display: block;">ماوە (قەرز)</span>
                    <strong id="cartRemainingText" style="color: var(--ios-red); font-size: 14px;">$0.00</strong>
                </div>
            </div>

            <button class="btn-ios-submit" style="background: var(--ios-green); color: #000;" onclick="submitCheckout()">
                <i class="fa-solid fa-print"></i> دەرکردنی پسوڵە و تەواوکردن
            </button>
            <button class="btn-ios-submit" style="background: transparent; color: var(--text-muted); box-shadow: none;" onclick="closeModal('cartModal')">داخستن</button>
        </div>
    </div>

    <!-- پسوڵەی چاپی گەرمیی -->
    <div id="thermalInvoice">
        <div style="text-align: center; border-bottom: 1px dashed #000; padding-bottom: 6px; margin-bottom: 6px;">
            <h2 style="font-size: 16px; margin: 0;">دانیال مۆبایل</h2>
            <p id="recInvNo" style="font-size: 10px; margin: 0;"></p>
            <p id="recDate" style="font-size: 10px; margin: 0;"></p>
        </div>
        <div style="font-size: 11px; margin-bottom: 6px;">
            <p>کڕیار: <span id="recCustomer"></span></p>
        </div>
        <table style="width: 100%; font-size: 11px; border-collapse: collapse; margin-bottom: 6px;">
            <thead><tr style="border-bottom: 1px solid #000;"><th style="text-align:right;">کاڵا</th><th>دانە</th><th style="text-align:left;">کۆ</th></tr></thead>
            <tbody id="recItemsBody"></tbody>
        </table>
        <div style="border-top: 1px dashed #000; padding-top: 4px; font-size: 11px;">
            <div style="display:flex; justify-content:space-between;"><span>کۆی گشتی:</span><span id="recSub"></span></div>
            <div style="display:flex; justify-content:space-between;"><span>داشکاندن:</span><span id="recDisc"></span></div>
            <div style="display:flex; justify-content:space-between; font-weight:bold;"><span>کۆی پارە:</span><span id="recTotal"></span></div>
            <div style="display:flex; justify-content:space-between;"><span>دراو:</span><span id="recPaid"></span></div>
            <div style="display:flex; justify-content:space-between; color:red;"><span>ماوە:</span><span id="recRem"></span></div>
            <div style="display:flex; justify-content:space-between; margin-top:2px;"><span>شێواز:</span><span id="recMethod"></span></div>
        </div>
        <p style="text-align: center; font-size: 10px; margin-top: 8px;">سوپاس بۆ کڕینەکەتان</p>
    </div>

    <script>
        let allProducts = [];
        let cart = [];
        let currentCatFilter = 'all';
        let currentPayMethod = 'Cash';

        // ئەنیمەیشنی شاهانەی ئەپڵ
        window.addEventListener('DOMContentLoaded', () => {
            setTimeout(() => {
                const splash = document.getElementById('splashScreen');
                splash.style.opacity = '0';
                splash.style.transform = 'scale(1.05)';
                setTimeout(() => {
                    splash.style.display = 'none';
                    checkAuth();
                }, 500);
            }, 1100);
        });

        async function checkAuth() {
            try {
                const res = await fetch('/api/auth/me');
                const data = await res.json();
                if (data.logged_in) {
                    document.getElementById('authSection').style.display = 'none';
                    document.getElementById('appView').style.display = 'block';
                    document.getElementById('iosTabBar').style.display = 'flex';
                    document.getElementById('topShopName').textContent = data.user.shop_name;
                    loadProducts();
                    loadDashboard();
                } else {
                    document.getElementById('authSection').style.display = 'flex';
                    document.getElementById('appView').style.display = 'none';
                    document.getElementById('iosTabBar').style.display = 'none';
                }
            } catch(e){}
        }

        async function submitAuth() {
            const res = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    username: document.getElementById('userInput').value.trim(),
                    password: document.getElementById('passInput').value.trim()
                })
            });
            const data = await res.json();
            if (res.ok) location.reload();
            else {
                const err = document.getElementById('authErrorMsg');
                err.textContent = data.message;
                err.style.display = 'block';
            }
        }

        async function logout() {
            await fetch('/api/auth/logout', { method: 'POST' });
            location.reload();
        }

        // فلتەری بەشەکان
        function filterCategory(cat, el) {
            currentCatFilter = cat;
            document.querySelectorAll('.cat-pill').forEach(p => p.classList.remove('active'));
            el.classList.add('active');
            renderProductsGrid();
        }

        async function loadProducts() {
            const search = document.getElementById('searchInput').value;
            const res = await fetch(`/api/products?search=${encodeURIComponent(search)}`);
            allProducts = await res.json();
            renderProductsGrid();
            renderStockList();
        }

        function renderProductsGrid() {
            const grid = document.getElementById('productsGrid');
            grid.innerHTML = '';

            let list = allProducts;
            if (currentCatFilter !== 'all') {
                list = allProducts.filter(p => p.category === currentCatFilter);
            }

            if (list.length === 0) {
                grid.innerHTML = '<p style="grid-column: 1/-1; text-align:center; color: var(--text-muted); padding: 40px;">هیچ کاڵایەک نەدۆزرایەوە</p>';
                return;
            }

            list.forEach(p => {
                let specObj = {};
                try { specObj = JSON.parse(p.specs || '{}'); } catch(e){}
                let specSummary = specObj.storage ? `${specObj.storage} - ${specObj.color || ''}` : specObj.operator ? `${specObj.operator}` : p.category;

                grid.innerHTML += `
                    <div class="item-card" onclick='addToCart(${JSON.stringify(p)})'>
                        <div>
                            <span class="item-badge-cat">${p.category}</span>
                            <h4 style="font-size: 14px; font-weight: 800; margin-bottom: 4px;">${p.name}</h4>
                            <p class="item-specs-sub">${specSummary}</p>
                        </div>
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span class="item-price-tag">$${Number(p.sell_price).toLocaleString()}</span>
                            <span style="font-size: 11px; color: ${p.stock_qty <= p.min_stock_alert ? 'var(--ios-red)' : 'var(--text-muted)'}; font-weight: 700;">
                                ماوە: ${p.stock_qty}
                            </span>
                        </div>
                    </div>
                `;
            });
        }

        // زیادکردن بۆ سەبەتە
        function addToCart(p) {
            const existing = cart.find(i => i.id === p.id);
            if (existing) {
                if (existing.qty + 1 > p.stock_qty) {
                    alert("ژمارەی کۆگا بەش ناکات!");
                    return;
                }
                existing.qty++;
            } else {
                if (p.stock_qty < 1) {
                    alert("ئەم کاڵایە لە کۆگا نەماوە!");
                    return;
                }
                cart.push({ ...p, qty: 1 });
            }
            updateCartUI();
        }

        function updateCartUI() {
            const bar = document.getElementById('floatingCart');
            if (cart.length > 0) {
                bar.style.display = 'flex';
                const totalCount = cart.reduce((s, i) => s + i.qty, 0);
                const totalPrice = cart.reduce((s, i) => s + (i.sell_price * i.qty), 0);
                document.getElementById('cartCountBadge').textContent = totalCount;
                document.getElementById('cartFloatingTotal').textContent = `$${totalPrice.toLocaleString()}`;
            } else {
                bar.style.display = 'none';
            }
            renderCartModalItems();
        }

        function renderCartModalItems() {
            const cont = document.getElementById('cartItemsContainer');
            cont.innerHTML = '';
            cart.forEach(item => {
                cont.innerHTML += `
                    <div style="display:flex; justify-content:space-between; align-items:center; background:rgba(255,255,255,0.04); padding:10px 12px; border-radius:12px; margin-bottom:6px;">
                        <div>
                            <strong style="font-size:13px;">${item.name}</strong>
                            <span style="display:block; font-size:11px; color:var(--text-muted);">$${item.sell_price} × ${item.qty}</span>
                        </div>
                        <div style="display:flex; align-items:center; gap:8px;">
                            <button onclick="changeQty(${item.id}, -1)" style="width:26px; height:26px; border-radius:8px; border:none; background:rgba(255,255,255,0.1); color:#fff;">-</button>
                            <span style="font-weight:800;">${item.qty}</span>
                            <button onclick="changeQty(${item.id}, 1)" style="width:26px; height:26px; border-radius:8px; border:none; background:rgba(255,255,255,0.1); color:#fff;">+</button>
                            <strong style="color:var(--ios-blue); margin-right:8px;">$${item.sell_price * item.qty}</strong>
                        </div>
                    </div>
                `;
            });
            updateCartTotals();
        }

        function changeQty(id, delta) {
            const it = cart.find(i => i.id === id);
            if (!it) return;
            it.qty += delta;
            if (it.qty <= 0) cart = cart.filter(i => i.id !== id);
            updateCartUI();
        }

        function clearCart() { cart = []; updateCartUI(); closeModal('cartModal'); }

        function updateCartTotals() {
            const subtotal = cart.reduce((s, i) => s + (i.sell_price * i.qty), 0);
            const disc = parseFloat(document.getElementById('cartDiscount').value) || 0;
            const grand = Math.max(0, subtotal - disc);

            document.getElementById('cartSubtotalText').textContent = `$${subtotal.toLocaleString()}`;
            document.getElementById('cartGrandTotalText').textContent = `$${grand.toLocaleString()}`;

            let paid = parseFloat(document.getElementById('cartPaidInput').value);
            if (isNaN(paid)) paid = grand;

            const rem = Math.max(0, grand - paid);
            document.getElementById('cartRemainingText').textContent = `$${rem.toLocaleString()}`;
        }

        function setPaymentMethod(method, el) {
            currentPayMethod = method;
            document.querySelectorAll('.pay-pill-btn').forEach(b => b.classList.remove('active'));
            el.classList.add('active');
        }

        async function submitCheckout() {
            if (cart.length === 0) return;
            const subtotal = cart.reduce((s, i) => s + (i.sell_price * i.qty), 0);
            const disc = parseFloat(document.getElementById('cartDiscount').value) || 0;
            const grand = Math.max(0, subtotal - disc);
            let paid = parseFloat(document.getElementById('cartPaidInput').value);
            if (isNaN(paid)) paid = grand;

            const custName = document.getElementById('cartCustName').value.trim();
            const custPhone = document.getElementById('cartCustPhone').value.trim();

            if (paid < grand && !custPhone) {
                alert("بۆ پارەی قەرز، ژمارەی مۆبایل پێویستە!");
                return;
            }

            const res = await fetch('/api/pos/checkout', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    cart: cart,
                    customer_name: custName,
                    customer_phone: custPhone,
                    discount: disc,
                    paid: paid,
                    payment_method: currentPayMethod
                })
            });

            const data = await res.json();
            if (res.ok) {
                closeModal('cartModal');
                printReceipt(data.invoice);
                clearCart();
                loadProducts();
                loadDashboard();
            } else {
                alert(data.message);
            }
        }

        function printReceipt(inv) {
            document.getElementById('recInvNo').textContent = inv.invoice_no;
            document.getElementById('recDate').textContent = inv.date;
            document.getElementById('recCustomer').textContent = inv.customer_name;
            const tb = document.getElementById('recItemsBody');
            tb.innerHTML = '';
            inv.items.forEach(i => {
                tb.innerHTML += `<tr><td>${i.name}</td><td style="text-align:center;">${i.qty}</td><td style="text-align:left;">$${i.sell_price * i.qty}</td></tr>`;
            });
            document.getElementById('recSub').textContent = `$${inv.subtotal}`;
            document.getElementById('recDisc').textContent = `$${inv.discount}`;
            document.getElementById('recTotal').textContent = `$${inv.grand_total}`;
            document.getElementById('recPaid').textContent = `$${inv.paid}`;
            document.getElementById('recRem').textContent = `$${inv.remaining}`;
            document.getElementById('recMethod').textContent = inv.payment_method;
            window.print();
        }

        // گۆڕینی خانەکانی زیادکردنی کاڵا بەپێی بەش (مۆبایل / سیمکارت / شەحنکەر)
        function switchAddCategory(cat) {
            document.getElementById('itemCatInput').value = cat;
            document.querySelectorAll('#addItemModal .cat-pill').forEach(b => b.classList.remove('active'));
            
            document.getElementById('mobFields').style.display = cat === 'موبایل' ? 'grid' : 'none';
            document.getElementById('simFields').style.display = cat === 'سیمکارت' ? 'grid' : 'none';
            document.getElementById('chargeFields').style.display = (cat === 'شەحنکەر' || cat === 'کاڤەر' || cat === 'ئەکسسوار') ? 'block' : 'none';

            if (cat === 'موبایل') {
                document.getElementById('pillMob').classList.add('active');
                document.getElementById('itemNameLabel').textContent = 'ناوی مۆبایل *';
                document.getElementById('itemName').placeholder = 'iPhone 15 Pro Max...';
            } else if (cat === 'سیمکارت') {
                document.getElementById('pillSim').classList.add('active');
                document.getElementById('itemNameLabel').textContent = 'ناوی جۆری سیمکارت *';
                document.getElementById('itemName').placeholder = 'سیمکارتی ئاسیاسێڵ VIP...';
            } else if (cat === 'شەحنکەر') {
                document.getElementById('pillCharge').classList.add('active');
                document.getElementById('itemNameLabel').textContent = 'ناوی شەحنکەر یان کێبڵ *';
                document.getElementById('itemName').placeholder = 'Apple 20W Charger...';
            } else if (cat === 'کاڤەر') {
                document.getElementById('pillCover').classList.add('active');
                document.getElementById('itemNameLabel').textContent = 'ناوی کاڤەر یان لەزگە *';
                document.getElementById('itemName').placeholder = 'کەڤەری ماگسەیف ئایفۆن...';
            } else {
                document.getElementById('pillAcc').classList.add('active');
                document.getElementById('itemNameLabel').textContent = 'ناوی ئەکسسوارات *';
                document.getElementById('itemName').placeholder = 'AirPods, Powerbank...';
            }
        }

        async function submitAddProduct() {
            const cat = document.getElementById('itemCatInput').value;
            let specs = {};

            if (cat === 'موبایل') {
                specs = { storage: document.getElementById('mobStorage').value, color: document.getElementById('mobColor').value.trim() };
            } else if (cat === 'سیمکارت') {
                specs = { operator: document.getElementById('simOperator').value, phone_no: document.getElementById('simNumber').value.trim() };
            } else {
                specs = { detail: document.getElementById('chargeSpecs').value.trim() };
            }

            const res = await fetch('/api/products', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    name: document.getElementById('itemName').value.trim(),
                    category: cat,
                    buy_price: document.getElementById('itemBuyPrice').value,
                    sell_price: document.getElementById('itemSellPrice').value,
                    stock_qty: document.getElementById('itemStock').value,
                    barcode: document.getElementById('itemBarcode').value.trim(),
                    specs: specs
                })
            });

            const data = await res.json();
            if (res.ok) {
                closeModal('addItemModal');
                document.getElementById('addItemForm').reset();
                loadProducts();
            } else {
                alert(data.message);
            }
        }

        function renderStockList() {
            const cont = document.getElementById('stockListContainer');
            cont.innerHTML = '';
            allProducts.forEach(p => {
                cont.innerHTML += `
                    <div style="background:var(--surface-card); padding:14px; border-radius:18px; border:1px solid var(--border-glass); margin-bottom:10px; display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <span style="font-size:10px; color:var(--ios-cyan); font-weight:800;">${p.category}</span>
                            <h4 style="font-size:14px; font-weight:800;">${p.name}</h4>
                            <span style="font-size:11px; color:var(--text-muted);">$${p.buy_price} ⬅ کڕین | فرۆشتن ➡ $${p.sell_price}</span>
                        </div>
                        <div style="text-align:left;">
                            <strong style="color:var(--ios-green); font-size:15px; display:block;">ماوە: ${p.stock_qty}</strong>
                            <button onclick="deleteProduct(${p.id})" style="border:none; background:rgba(255,69,58,0.15); color:var(--ios-red); padding:4px 8px; border-radius:6px; font-size:11px; cursor:pointer; margin-top:4px;">سڕینەوە</button>
                        </div>
                    </div>
                `;
            });
        }

        async function deleteProduct(id) {
            if (confirm('دڵنیایت لە سڕینەوە؟')) {
                await fetch(`/api/products/${id}`, { method: 'DELETE' });
                loadProducts();
            }
        }

        async function loadDashboard() {
            const res = await fetch('/api/dashboard/stats');
            const d = await res.json();
            document.getElementById('dashSales').textContent = `$${Number(d.today_sales).toLocaleString()}`;
            document.getElementById('dashProfit').textContent = `$${Number(d.today_profit).toLocaleString()}`;
            document.getElementById('dashDebt').textContent = `$${Number(d.total_debt).toLocaleString()}`;
        }

        async function loadDebts() {
            const res = await fetch('/api/debts');
            const debts = await res.json();
            const cont = document.getElementById('debtsContainer');
            cont.innerHTML = '';
            debts.forEach(d => {
                cont.innerHTML += `
                    <div style="background:var(--surface-card); padding:14px; border-radius:18px; border:1px solid var(--border-glass); margin-bottom:10px;">
                        <div style="display:flex; justify-content:space-between;">
                            <strong>${d.customer_name} (${d.customer_phone || ''})</strong>
                            <strong style="color:var(--ios-red);">$${d.remaining_amount}</strong>
                        </div>
                        <button onclick="payDebtPrompt(${d.id}, ${d.remaining_amount})" style="margin-top:10px; width:100%; padding:8px; border-radius:10px; border:none; background:var(--ios-green); color:#000; font-weight:800; cursor:pointer;">
                            وەرگرتنەوەی پارە
                        </button>
                    </div>
                `;
            });
        }

        async function payDebtPrompt(id, rem) {
            const p = prompt(`بڕی پارەی وەرگیراو بنووسە (کۆی ماوە: $${rem}):`, rem);
            if (!p || isNaN(p) || Number(p) <= 0) return;
            await fetch(`/api/debts/${id}/pay`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ amount: p })
            });
            loadDebts();
            loadDashboard();
        }

        function switchTab(tabId, el) {
            document.querySelectorAll('.tab-content').forEach(t => t.style.display = 'none');
            document.querySelectorAll('.tab-item').forEach(i => i.classList.remove('active'));
            document.getElementById(tabId).style.display = 'block';
            el.classList.add('active');
            if (tabId === 'tabStock') renderStockList();
            if (tabId === 'tabDashboard') loadDashboard();
            if (tabId === 'tabDebts') loadDebts();
        }

        function openModal(id) { document.getElementById(id).style.display = 'flex'; }
        function closeModal(id) { document.getElementById(id).style.display = 'none'; }
    </script>
</body>
</html>
