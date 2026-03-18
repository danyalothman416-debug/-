import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Golden Delivery", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# Initialize Session States
if 'page' not in st.session_state:
    st.session_state.page = "home"
if 'user_email' not in st.session_state:
    st.session_state.user_email = None
if 'admin_authenticated' not in st.session_state:
    st.session_state.admin_authenticated = False
if 'lang_choice' not in st.session_state:
    st.session_state.lang_choice = "English 🇬🇧"
if 'theme_choice' not in st.session_state:
    st.session_state.theme_choice = "Dark 🌙"

# --- 2. MULTI-LANGUAGE & UI STRINGS (COMPLETE WITH ALL TEXTS) ---
languages = {
    "English 🇬🇧": {
        "dir": "ltr", 
        "align": "left", 
        "theme_label": "Theme", 
        "light": "Light ☀️", 
        "dark": "Dark 🌙",
        "title": "GOLDEN DELIVERY",
        "desc": "Experience the gold standard of logistics in Kirkuk. Fast, secure, and always on time.",
        "customer_name": "Customer Name", 
        "shop_name": "Shop Name", 
        "shop_addr": "Shop Address", 
        "phone": "Phone Number", 
        "area": "Neighborhood", 
        "full_addr": "Address Details (Near what?)",
        "price": "Price (IQD)", 
        "submit": "Confirm Order", 
        "nav_home": "Home", 
        "nav_order": "Order", 
        "nav_profile": "Account", 
        "nav_terms": "Terms",
        "free_info": "🎁 Special: 1 out of every 3 deliveries is FREE!",
        "free_success": "🎊 Loyalty Reward: This delivery is 0 IQD!",
        "google_btn": "Sign in with Google", 
        "logout": "Logout",
        "settings": "Settings & Language",
        "admin_pass_label": "Enter Admin Password to view links",
        "admin_error": "❌ Incorrect Password",
        "mgmt_links": "🔗 Management Links (Internal Only)",
        "terms_title": "📜 Terms and Rules",
        "terms_content": "...",
        # Home page cards
        "fast_title": "⚡ Fast",
        "fast_desc": "Delivery within 24 hours",
        "secure_title": "🔒 Secure",
        "secure_desc": "Your packages are safe with us",
        "free_title": "🎁 Free Delivery",
        "free_desc": "1 in 3 deliveries free",
        # Additional texts
        "delivery_time": "Delivery within 24 hours",
        "packages_safe": "Your packages are safe with us",
        "free_promo": "1 in 3 deliveries free",
        "signed_in_as": "Logged in as:",
        "access_account": "Sign in to access your account and management features",
        "golden_rules": "Golden Rules",
        "rule1": "1 out of 3 deliveries is free - automatically applied!",
        "rule2": "No illegal items - we comply with all local laws",
        "rule3": "Fast Kirkuk wide service - all neighborhoods covered",
        "rule4": "Delivery within 24 hours of order confirmation",
        "rule5": "Cash on delivery only",
        "rule6": "Free delivery promotion applies to orders over 3000 IQD",
        "rule7": "Customer must be present at time of delivery",
        "unlock_mgmt": "Unlock Management",
        "lock_mgmt": "Lock Management & Logout"
    },
    "کوردی 🇭🇺": {
        "dir": "rtl", 
        "align": "right", 
        "theme_label": "ڕووکار", 
        "light": "ڕوون ☀️", 
        "dark": "تاریک 🌙",
        "title": "گۆڵدن دلیڤەری",
        "desc": "بەرزترین کوالێتی گەیاندن لە کەرکوک. خێرا، پارێزراو، و هەمیشە لە کاتی خۆیدا.",
        "customer_name": "ناوی کڕیار", 
        "shop_name": "ناوی دوکان", 
        "shop_addr": "ناونیشانی دوکان", 
        "phone": "ژمارەی مۆبایل", 
        "area": "گەڕەک", 
        "full_addr": "وردەکاری ناونیشان (نزیک کوێیە؟)",
        "price": "نرخ (د.ع)", 
        "submit": "تۆمارکردن", 
        "nav_home": "سەرەکی", 
        "nav_order": "داواکردن", 
        "nav_profile": "هەژمار", 
        "nav_terms": "یاساکان",
        "free_info": "🎁 دیاری: یەکێک لە هەر ٣ گەیاندنێک بە خۆڕاییە!",
        "free_success": "🎊 پیرۆزە! ئەم گەیاندنەت بە ٠ دینارە!",
        "google_btn": "چوونەژوورەوە بە Google", 
        "logout": "چوونەدەرەوە",
        "settings": "ڕێکخستن و زمان",
        "admin_pass_label": "تکایە وشەی نهێنی بنووسە بۆ بینینی لینکەکان",
        "admin_error": "❌ وشەی نهێنی هەڵەیە",
        "mgmt_links": "🔗 لینکەکانی بەڕێوەبردن (تەنها بۆ ئەدمین)",
        "terms_title": "📜 مەرج و ڕێساکان",
        "terms_content": "...",
        # Home page cards
        "fast_title": "⚡ خێرا",
        "fast_desc": "گەیاندن لە ماوەی ٢٤ کاتژمێردا",
        "secure_title": "🔒 پارێزراو",
        "secure_desc": "پاکەتەکانت سەلامەتن لە لای ئێمە",
        "free_title": "🎁 گەیاندنی خۆڕایی",
        "free_desc": "یەکێک لە هەر ٣ گەیاندنێک بە خۆڕاییە",
        # Additional texts
        "delivery_time": "گەیاندن لە ماوەی ٢٤ کاتژمێردا",
        "packages_safe": "پاکەتەکانت سەلامەتن لە لای ئێمە",
        "free_promo": "یەکێک لە هەر ٣ گەیاندنێک بە خۆڕاییە",
        "signed_in_as": "چوویتە ژوورەوە وەک:",
        "access_account": "چوونەژوورەوە بۆ ئەکاونتەکەت و تایبەتمەندییەکانی بەڕێوەبردن",
        "golden_rules": "ڕێسا زێڕینەکان",
        "rule1": "یەکێک لە هەر ٣ گەیاندنێک بە خۆڕاییە - بە شێوەیەکی خۆکار جێبەجێ دەبێت!",
        "rule2": "هیچ کاڵایەکی نایاسایی نییە - ئێمە پابەندی هەموو یاسا ناوخۆییەکانین",
        "rule3": "خزمەتگوزاری خێرا لە سەرانسەری کەرکوک - هەموو گەڕەکەکان داپۆشراون",
        "rule4": "گەیاندن لە ماوەی ٢٤ کاتژمێری دوای پشتڕاستکردنەوەی داواکاری",
        "rule5": "تەنها پارەدان لە کاتی گەیاندن",
        "rule6": "پڕۆمۆشنی گەیاندنی خۆڕایی بۆ داواکارییەکانی سەروو ٣٠٠٠ دینار",
        "rule7": "کڕیار دەبێت لە کاتی گەیاندن ئامادە بێت",
        "unlock_mgmt": "کردنەوەی بەڕێوەبردن",
        "lock_mgmt": "داخستنی بەڕێوەبردن و چوونەدەرەوە"
    },
    "العربية 🇮🇶": {
        "dir": "rtl", 
        "align": "right", 
        "theme_label": "المظهر", 
        "light": "فاتح ☀️", 
        "dark": "داكن 🌙",
        "title": "جولدن دليفري",
        "desc": "المعيار الذهبي للخدمات اللوجستية في كركوك. سرعة، أمان، ودقة في المواعيد.",
        "customer_name": "اسم الزبون", 
        "shop_name": "اسم المحل", 
        "shop_addr": "عنوان المحل", 
        "phone": "رقم الهاتف", 
        "area": "المنطقة", 
        "full_addr": "تفاصيل العنوان (قرب ماذا؟)",
        "price": "السعر (د.ع)", 
        "submit": "تأكيد الطلب", 
        "nav_home": "الرئيسية", 
        "nav_order": "طلب", 
        "nav_profile": "الحساب", 
        "nav_terms": "الشروط",
        "free_info": "🎁 عرض: واحدة من كل ٣ توصيلات مجانية!",
        "free_success": "🎊 مبروك! هذه الطلبية بـ ٠ دينار!",
        "google_btn": "الدخول بواسطة Google", 
        "logout": "خروج",
        "settings": "الإعدادات واللغة",
        "admin_pass_label": "أدخل كلمة مرور المسؤول لعرض الروابط",
        "admin_error": "❌ كلمة المرور غير صحيحة",
        "mgmt_links": "🔗 روابط الإدارة (للمسؤولين فقط)",
        "terms_title": "📜 الشروط والقواعد",
        "terms_content": "...",
        # Home page cards
        "fast_title": "⚡ سريع",
        "fast_desc": "التوصيل خلال ٢٤ ساعة",
        "secure_title": "🔒 آمن",
        "secure_desc": "طرودك آمنة معنا",
        "free_title": "🎁 توصيل مجاني",
        "free_desc": "واحدة من كل ٣ توصيلات مجانية",
        # Additional texts
        "delivery_time": "التوصيل خلال ٢٤ ساعة",
        "packages_safe": "طرودك آمنة معنا",
        "free_promo": "واحدة من كل ٣ توصيلات مجانية",
        "signed_in_as": "تم تسجيل الدخول باسم:",
        "access_account": "سجل الدخول للوصول إلى حسابك وميزات الإدارة",
        "golden_rules": "القواعد الذهبية",
        "rule1": "واحدة من كل ٣ توصيلات مجانية - يتم تطبيقها تلقائياً!",
        "rule2": "لا يوجد عناصر غير قانونية - نحن نلتزم بجميع القوانين المحلية",
        "rule3": "خدمة سريعة في جميع أنحاء كركوك - جميع المناطق مغطاة",
        "rule4": "التوصيل خلال ٢٤ ساعة من تأكيد الطلب",
        "rule5": "الدفع عند الاستلام فقط",
        "rule6": "عرض التوصيل المجاني للطلبات التي تزيد عن ٣٠٠٠ دينار",
        "rule7": "يجب أن يكون الزبون حاضراً وقت التوصيل",
        "unlock_mgmt": "فتح الإدارة",
        "lock_mgmt": "قفل الإدارة وتسجيل الخروج"
    }
}

# --- 3. NEIGHBORHOODS (COMPLETE LIST) ---
KIRKUK_AREAS = sorted([
    # Original neighborhoods
    "Arfa / عرفة",
    "Tis'in / تسعين",
    "Shoraw / شوراو",
    "Rahim Awa / رحيماوة",
    "Quraya / قورية",
    "Al-Wasiti / الواسطي",
    "Al-Nasr / النصر",
    "Azadi / ازادي",
    "Wahid Huzairan / واحد حزيران",
    # Additional neighborhoods requested
    "Kirkuk Citadel / قلعة كركوك",
    "Musalla / مصلى",
    "Imam Qasim / امام قاسم",
    "Shorija / الشورجة",
    "Hasiraka / حصيرةكة",
    "Tapai Malla Abdulla / تبة ملا عبدulla",
    "Rahimawa / رحيم آوه",
    "Almas / الماس",
    "Arafa / عرفة",
    "Faylaq / فيلق",
    "Panja Ali / بنجة علي",
    "Darwaza / دروازة",
    "Kurdistan Neighborhood / حي كردستان",
    "Baghdad Road / طريق بغداد",
    "Wasit / واسط",
    "Domiz / دوميز",
    "June 1st / ١ حزيران",
    "Majidiya / المجيدية",
    "Al-Beiji / البيجي",
    "Mansour / المنصور",
    "Razgari / رزگاري",
    "Ghazna / غزنة",
    "Hay Aden / حي عدن",
    "Taseen / تسعين",
    "Khazra / خضراء",
    "Beiji / بيجي",
    "Qadisiyah / قادسية",
    "Panorama / بانوراما",
    "Barutkhana / باروته خانه",
    "Engineers Neighborhood / حي المهندسين",
    "Teachers Neighborhood / حي المعلمين",
    # Additional neighborhoods for completeness
    "Al-Mas / المس",
    "Al-Mithaq / الميثاق",
    "Al-Ta'mim / التأميم",
    "Al-Qadisiyah / القادسية",
    "Al-Jamea / الجامعة",
    "Al-Muhandiseen / المهندسين",
    "Al-Andalus / الأندلس",
    "Al-Jumhouriya / الجمهورية",
    "Domeez / دوميز",
    "Al-Wafa / الوفاء",
    "Al-Nour / النور",
    "Al-Muthanna / المثنى",
    "Al-Khadra / الخضراء",
    "Sarchinar / سرچنار",
    "Muhammad Ali / محمد علي",
    "Al-Mashtal / المشتل",
    "Al-Shuhada / الشهداء",
    "Al-Hurriya / الحرية",
    "Al-Sina'a / الصناعة",
    "Al-Masbin / المسبين",
    "Al-Sa'ad / السعد",
    "Bakhtiari / بختياري",
    "Bawer / باور",
    "Camp / مخيم",
    "Chay / جاي",
    "Choman / جومان",
    "Hasar / حصر",
    "Kani Askan / كاني عسكر",
    "Kani Qrzhala / كاني قرژالة",
    "Laylan / ليلان",
    "Rizgary / رزگاري",
    "Taza / طازة",
    "Yarmuk / يرموك",
    "Zab / زاب"
])

# --- 4. DATA LOGIC ---
DB_FILE = "deliveries.csv"
def load_data():
    if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE, dtype={"phone": str})
    return pd.DataFrame(columns=["date", "customer", "shop", "phone", "area", "address", "shop_addr", "price", "status", "user_email"])

# --- 5. THEME & SETTINGS (Home Only) ---
with st.container():
    c_logo, c_set = st.columns([2, 1])
    if st.session_state.page == "home":
        with c_set:
            with st.expander("⚙️ Settings"):
                st.session_state.lang_choice = st.selectbox("🌐 Language", list(languages.keys()), index=list(languages.keys()).index(st.session_state.lang_choice))
                st.session_state.theme_choice = st.radio("Theme", ["Light ☀️", "Dark 🌙"], horizontal=True, index=0 if st.session_state.theme_choice == "Light ☀️" else 1)
    
    L = languages[st.session_state.lang_choice]
    with c_logo:
        st.markdown(f"<h2 style='color:#D4AF37; margin:0;'>{L['title']}</h2>", unsafe_allow_html=True)

# --- 6. CSS ENGINE (COMPLETELY REWRITTEN FOR DARK MODE) ---
is_dark = st.session_state.theme_choice == "Dark 🌙"

# Color scheme
if is_dark:
    main_bg = "#0a0c10"
    card_bg = "#1e2329"
    text_color = "#ffffff"
    accent = "#D4AF37"
    input_bg = "#2d333d"
    border_color = "#3a404c"
else:
    main_bg = "#f5f7fa"
    card_bg = "#ffffff"
    text_color = "#1a1a2e"
    accent = "#D4AF37"
    input_bg = "#ffffff"
    border_color = "#e0e0e0"

# Comprehensive CSS for all elements
st.markdown(f"""
<style>
    /* Hide sidebar */
    [data-testid="stSidebar"] {{
        display: none;
    }}
    
    /* Main container - FORCE ALL TEXT TO BE VISIBLE */
    html, body, [data-testid="stAppViewContainer"], 
    .main, .block-container, .stApp {{
        background-color: {main_bg} !important;
        color: {text_color} !important;
    }}
    
    /* Force ALL text elements to have proper color */
    * {{
        color: {text_color} !important;
        border-color: {border_color} !important;
    }}
    
    /* Override for input fields - keep them readable */
    input, textarea, select, [data-baseweb="select"] * {{
        background-color: {input_bg} !important;
        color: {text_color} !important;
        border-color: {accent}40 !important;
    }}
    
    /* Dropdown menu items */
    [data-baseweb="menu"] * {{
        background-color: {card_bg} !important;
        color: {text_color} !important;
    }}
    
    /* Form container */
    .stForm {{
        background-color: {card_bg} !important;
        border: 1px solid {accent}40 !important;
        border-radius: 20px !important;
        padding: 30px !important;
    }}
    
    /* Glass card */
    .glass-card {{
        background-color: {card_bg} !important;
        border-radius: 20px !important;
        padding: 25px !important;
        border: 1px solid {accent}30 !important;
    }}
    
    /* Brand header */
    .brand-header {{
        background: linear-gradient(135deg, #D4AF37 0%, #8A6D3B 100%);
        padding: 40px;
        border-radius: 0 0 40px 40px;
        text-align: center;
        margin-bottom: 20px;
    }}
    
    /* Brand header text should be white regardless of theme */
    .brand-header h1, .brand-header * {{
        color: white !important;
    }}
    
    /* Buttons */
    .stButton button {{
        background-color: {accent} !important;
        color: {text_color if is_dark else '#000000'} !important;
        border: none !important;
        font-weight: bold !important;
    }}
    
    .stButton button:hover {{
        background-color: {accent}dd !important;
    }}
    
    /* Info boxes */
    .stAlert {{
        background-color: {card_bg} !important;
        color: {text_color} !important;
        border-left-color: {accent} !important;
    }}
    
    /* Success message */
    .stSuccess {{
        background-color: {card_bg} !important;
        color: {accent} !important;
    }}
    
    /* Expander */
    .streamlit-expanderHeader {{
        background-color: {card_bg} !important;
        color: {text_color} !important;
    }}
    
    /* DataFrame */
    .dataframe, .stDataFrame {{
        color: {text_color} !important;
    }}
    
    .dataframe td, .dataframe th {{
        background-color: {card_bg} !important;
        color: {text_color} !important;
        border-color: {border_color} !important;
    }}
    
    /* Radio buttons and checkboxes */
    .stRadio label, .stCheckbox label {{
        color: {text_color} !important;
    }}
    
    /* Select box */
    .stSelectbox label {{
        color: {text_color} !important;
    }}
    
    /* Number input */
    .stNumberInput label {{
        color: {text_color} !important;
    }}
    
    /* Text input */
    .stTextInput label {{
        color: {text_color} !important;
    }}
    
    /* Text area */
    .stTextArea label {{
        color: {text_color} !important;
    }}
    
    /* Divider */
    hr {{
        border-color: {border_color} !important;
    }}
    
    /* Sidebar (even though hidden) */
    [data-testid="stSidebar"] * {{
        color: {text_color} !important;
    }}
    
    /* Links */
    a {{
        color: {accent} !important;
    }}
    
    /* Direction handling */
    [dir="{L['dir']}"] {{
        text-align: {L['align']} !important;
    }}
    
    /* Card titles should use accent color */
    .card-title {{
        color: {accent} !important;
        font-size: 1.5rem !important;
        margin-bottom: 0.5rem !important;
    }}
</style>
""", unsafe_allow_html=True)

# --- 7. PAGE ROUTING ---

if st.session_state.page == "home":
    st.markdown(f'<div class="brand-header"><h1 style="color:white; margin:0;">{L["title"]}</h1><p style="color:white; opacity:0.9;">{L["desc"]}</p></div>', unsafe_allow_html=True)
    
    # Add some decorative elements for home page with proper translations
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="glass-card" style="text-align:center;">
            <h3 class="card-title">{L['fast_title']}</h3>
            <p>{L['fast_desc']}</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="glass-card" style="text-align:center;">
            <h3 class="card-title">{L['secure_title']}</h3>
            <p>{L['secure_desc']}</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="glass-card" style="text-align:center;">
            <h3 class="card-title">{L['free_title']}</h3>
            <p>{L['free_desc']}</p>
        </div>
        """, unsafe_allow_html=True)

elif st.session_state.page == "order":
    st.markdown(f"<h2 style='text-align:center; color:{accent};'>{L['nav_order']}</h2>", unsafe_allow_html=True)
    st.info(L["free_info"])
    df = load_data()
    phone_input = st.text_input(L['phone'], placeholder="07xx xxx xxxx")
    is_free = False
    if phone_input:
        count = len(df[df['phone'] == phone_input])
        is_free = (count + 1) % 3 == 0
        if is_free: st.success(L["free_success"])
    with st.form("order_form"):
        c1, c2 = st.columns(2)
        with c1:
            customer = st.text_input(L['customer_name'])
            shop = st.text_input(L['shop_name'])
            area = st.selectbox(L['area'], ["-- " + L['area'] + " --"] + KIRKUK_AREAS)
        with c2:
            shop_addr = st.text_input(L['shop_addr'])
            full_addr = st.text_area(L['full_addr'])
            price = st.number_input(L['price'], value=0 if is_free else 3000)
        if st.form_submit_button(L['submit'], use_container_width=True):
            if customer and phone_input and area and "--" not in area:
                new_row = pd.DataFrame([{"date": datetime.now().strftime("%Y-%m-%d"), "customer": customer, "shop": shop, "phone": phone_input, "area": area, "address": full_addr, "shop_addr": shop_addr, "price": price, "status": "Pending", "user_email": st.session_state.user_email}])
                pd.concat([df, new_row]).to_csv(DB_FILE, index=False)
                st.success("✅ Order Recorded!")
                st.balloons()

elif st.session_state.page == "profile":
    st.markdown(f"<h2 style='text-align:center; color:{accent};'>{L['nav_profile']}</h2>", unsafe_allow_html=True)
    if st.session_state.user_email is None:
        st.markdown(f"""
        <div class="glass-card" style="text-align:center;">
            <p>{L['access_account']}</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button(L["google_btn"], use_container_width=True):
            st.session_state.user_email = "verified_user@gmail.com"
            st.rerun()
    else:
        st.markdown(f"<p>{L['signed_in_as']} <b>{st.session_state.user_email}</b></p>", unsafe_allow_html=True)
        # PASSWORD PROTECTION SECTION
        if not st.session_state.admin_authenticated:
            st.warning(L["admin_pass_label"])
            # Set your actual admin password here
            pwd = st.text_input("Password", type="password")
            if st.button(L["unlock_mgmt"]):
                if pwd == "GoldenAdmin2026": # CHANGE THIS PASSWORD
                    st.session_state.admin_authenticated = True
                    st.rerun()
                else:
                    st.error(L["admin_error"])
        else:
            # ONLY SHOWS AFTER CORRECT PASSWORD
            st.subheader(L["mgmt_links"])
            st.markdown("- [Admin Dashboard](https://your-private-link.com/admin)")
            st.markdown("- [Database View](https://your-private-link.com/database)")
            st.divider()
            st.dataframe(load_data(), use_container_width=True)
            if st.button(L["lock_mgmt"]):
                st.session_state.user_email = None
                st.session_state.admin_authenticated = False
                st.rerun()

elif st.session_state.page == "terms":
    st.markdown(f"<h2 style='text-align:center; color:{accent};'>{L['terms_title']}</h2>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class='glass-card'>
        <h4 style="color:{accent};">{L['golden_rules']}</h4>
        <p>1. {L['rule1']}</p>
        <p>2. {L['rule2']}</p>
        <p>3. {L['rule3']}</p>
        <p>4. {L['rule4']}</p>
        <p>5. {L['rule5']}</p>
        <p>6. {L['rule6']}</p>
        <p>7. {L['rule7']}</p>
    </div>
    """, unsafe_allow_html=True)

# --- 8. BOTTOM NAVIGATION ---
st.markdown("<br><br><br>", unsafe_allow_html=True)
n1, n2, n3, n4 = st.columns(4)
with n1:
    if st.button(f"🏠 {L['nav_home']}", use_container_width=True): 
        st.session_state.page="home"
        st.rerun()
with n2:
    if st.button(f"🚚 {L['nav_order']}", use_container_width=True): 
        st.session_state.page="order"
        st.rerun()
with n3:
    if st.button(f"📜 {L['nav_terms']}", use_container_width=True): 
        st.session_state.page="terms"
        st.rerun()
with n4:
    if st.button(f"👤 {L['nav_profile']}", use_container_width=True): 
        st.session_state.page="profile"
        st.rerun()
