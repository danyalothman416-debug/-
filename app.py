import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Golden Delivery", layout="wide", initial_sidebar_state="collapsed")

if 'page' not in st.session_state:
    st.session_state.page = "home"
if 'user_email' not in st.session_state:
    st.session_state.user_email = None

# --- 2. MULTI-LANGUAGE & UI STRINGS ---
languages = {
    "English 🇬🇧": {
        "dir": "ltr", "align": "left", "theme_label": "Theme", "light": "Light ☀️", "dark": "Dark 🌙",
        "title": "GOLDEN DELIVERY",
        "desc": "Experience the gold standard of logistics in Kirkuk. Fast, secure, and always on time.",
        "customer_name": "Customer Name", "shop_name": "Shop Name", 
        "shop_addr": "Shop Address", "phone": "Phone Number", 
        "area": "Neighborhood", "full_addr": "Address Details",
        "price": "Price (IQD)", "submit": "Confirm Order", 
        "nav_home": "Home", "nav_order": "Order", "nav_profile": "Account",
        "free_info": "🎁 Special: 1 out of every 3 deliveries is FREE!",
        "free_success": "🎊 Loyalty Reward: This delivery is 0 IQD!",
        "google_btn": "Sign in with Google", "logout": "Logout",
    },
    "کوردی 🇭🇺": {
        "dir": "rtl", "align": "right", "theme_label": "ڕووکار", "light": "ڕوون ☀️", "dark": "تاریک 🌙",
        "title": "گۆڵدن دلیڤەری",
        "desc": "بەرزترین کوالێتی گەیاندن لە کەرکوک. خێرا، پارێزراو، و هەمیشە لە کاتی خۆیدا.",
        "customer_name": "ناوی کڕیار", "shop_name": "ناوی دوکان", 
        "shop_addr": "ناونیشانی دوکان", "phone": "ژمارەی مۆبایل", 
        "area": "گەڕەک", "full_addr": "وردەکاری ناونیشان",
        "price": "نرخ (د.ع)", "submit": "تۆمارکردن", 
        "nav_home": "سەرەکی", "nav_order": "داواکردن", "nav_profile": "هەژمار",
        "free_info": "🎁 دیاری: یەکێک لە هەر ٣ گەیاندنێک بە خۆڕاییە!",
        "free_success": "🎊 پیرۆزە! ئەم گەیاندنەت بە ٠ دینارە!",
        "google_btn": "چوونەژوورەوە بە Google", "logout": "چوونەدەرەوە",
    },
    "العربية 🇮🇶": {
        "dir": "rtl", "align": "right", "theme_label": "المظهر", "light": "فاتح ☀️", "dark": "داكن 🌙",
        "title": "گولدن دليفري",
        "desc": "المعيار الذهبي للخدمات اللوجستية في كركوك. سرعة، أمان، ودقة في المواعيد.",
        "customer_name": "اسم الزبون", "shop_name": "اسم المحل", 
        "shop_addr": "عنوان المحل", "phone": "رقم الهاتف", 
        "area": "المنطقة", "full_addr": "تفاصيل العنوان",
        "price": "السعر (د.ع)", "submit": "تأكيد الطلب", 
        "nav_home": "الرئيسية", "nav_order": "طلب", "nav_profile": "الحساب",
        "free_info": "🎁 عرض: واحدة من كل ٣ توصيلات مجانية!",
        "free_success": "🎊 مبروك! هذه الطلبية بـ ٠ دينار!",
        "google_btn": "الدخول بواسطة Google", "logout": "خروج",
    }
}

# --- 3. NEIGHBORHOODS ---
KIRKUK_AREAS = sorted([
    "Arfa / عرفة", "Tis'in / تسعين", "Binja Ali / بنجة علي", "Shoraw / شوراو",
    "Rahim Awa / رحيماوة", "Laylawa / ليلان", "Wasit / واسطي", "Al-Musalla / مصلى",
    "Quraya / قورية", "Dumiz / دوميز", "Al-Khadra / الخضراء", "Al-Wasiti / الواسطي",
    "Al-Askari / الحي العسكري", "Al-Qadisiyya / القادسية", "Al-Nasr / النصر", 
    "Azadi / ازادي", "Shura / شورى", "Al-Nabi Yunus / النبي يونس", "Al-Shorja / الشورجة",
    "Wahid Huzairan / واحد حزيران", "Ronaki / رونكي", "Biriti / بريتي", "Sarhad / سرحد",
    "Shahidan / شهيدان", "Tarkalan / تركلان", "Haidar Khana / حيدر خانة", "Sayyada / صيادة",
    "Al-Mu'allimin / المعلمين", "Al-Muhandisin / المهندسين", "Al-Atibba / الاطباء",
    "Al-Adala / العدالة", "Al-Salam / السلام", "Taza Khurmato / تازة خورماتو", 
    "Yaychi / يايجي", "Daquq / داقوق", "Laylan / ليلان", "Malha / ملحة", 
    "Bashir / بشير", "Tarjala / ترجلة"
])

# --- 4. THEME ENGINE ---
lang_choice = st.sidebar.selectbox("🌐 Language", list(languages.keys()))
L = languages[lang_choice]
theme_choice = st.sidebar.radio(L['theme_label'], [L['light'], L['dark']])

is_dark = theme_choice == L['dark']
main_bg = "#0f1116" if is_dark else "#fdfdfd"
card_bg = "rgba(30, 34, 45, 0.7)" if is_dark else "rgba(255, 255, 255, 0.9)"
text_color = "#ffffff" if is_dark else "#1a1a1a"
accent = "#D4AF37"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {{
        background: {main_bg};
        color: {text_color} !important;
        font-family: 'Poppins', sans-serif;
        direction: {L['dir']};
    }}

    /* Visibility Fix: Force labels to be visible in Dark Mode */
    label, p, span, div {{
        color: {text_color} !important;
    }}

    .brand-header {{
        background: linear-gradient(135deg, #D4AF37 0%, #8A6D3B 100%);
        padding: 50px 20px;
        border-radius: 0 0 50px 50px;
        text-align: center;
        box-shadow: 0 15px 35px rgba(0,0,0,0.4);
        margin-bottom: 30px;
    }}

    /* Glassmorphism Card */
    .glass-card {{
        background: {card_bg};
        backdrop-filter: blur(12px);
        border: 1px solid rgba(212, 175, 55, 0.2);
        border-radius: 25px;
        padding: 30px;
        margin: 10px 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }}

    /* Form Input UI */
    .stTextInput input, .stSelectbox div, .stTextArea textarea {{
        background-color: rgba(255,255,255,0.05) !important;
        border: 1px solid {accent}44 !important;
        color: {text_color} !important;
        border-radius: 12px !important;
    }}

    /* Navigation Bar */
    .nav-holder {{
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        width: 90%;
        max-width: 450px;
        background: rgba(20, 20, 20, 0.85);
        backdrop-filter: blur(20px);
        border-radius: 30px;
        display: flex;
        justify-content: space-around;
        padding: 10px;
        border: 1px solid {accent}55;
        z-index: 1000;
    }}

    .stButton button {{
        border-radius: 15px !important;
        transition: 0.3s all ease;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. DATA LOGIC ---
DB_FILE = "deliveries.csv"
def load_data():
    if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE, dtype={"phone": str})
    return pd.DataFrame(columns=["date", "customer", "shop", "phone", "area", "address", "shop_addr", "price", "status", "user_email"])

# --- 6. PAGE ROUTING ---

if st.session_state.page == "home":
    st.markdown(f'<div class="brand-header"><h1 style="color:white; letter-spacing:2px;">{L["title"]}</h1></div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="text-align: center; padding: 20px;">
        <h2 style="color:{accent}; font-weight:600;">The Best in Kirkuk</h2>
        <p style="font-size: 1.2rem; opacity: 0.8;">{L["desc"]}</p>
        <div style="margin-top:40px; display:flex; justify-content:center; gap:30px; font-size:2rem;">
            <span>🚚</span><span>📦</span><span>💰</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

elif st.session_state.page == "order":
    st.markdown(f'<h2 style="text-align:center; color:{accent}; margin-top:20px;">{L["nav_order"]}</h2>', unsafe_allow_html=True)
    st.markdown(f'<div style="text-align:center; margin-bottom:15px; font-weight:bold;">{L["free_info"]}</div>', unsafe_allow_html=True)
    
    with st.container():
        df = load_data()
        phone_input = st.text_input(f"📱 {L['phone']}", placeholder="07xx xxx xxxx")
        
        is_free = False
        if phone_input:
            user_orders = len(df[df['phone'] == phone_input])
            is_free = (user_orders + 1) % 3 == 0
            if is_free:
                st.success(L["free_success"])

        with st.form("modern_form"):
            c1, c2 = st.columns(2)
            with c1:
                customer = st.text_input(L['customer_name'])
                shop = st.text_input(L['shop_name'])
                area = st.selectbox(L['area'], ["-- Select --"] + KIRKUK_AREAS)
            with c2:
                shop_addr = st.text_input(L['shop_addr'])
                full_addr = st.text_area(L['full_addr'])
                price = st.number_input(L['price'], value=0 if is_free else 3000)
            
            if st.form_submit_button(L['submit'], use_container_width=True):
                if customer and phone_input and "--" not in area:
                    new_row = pd.DataFrame([{
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "customer": customer, "shop": shop, "phone": phone_input, "area": area, 
                        "address": full_addr, "shop_addr": shop_addr, "price": price, 
                        "status": "Pending", "user_email": st.session_state.user_email
                    }])
                    pd.concat([df, new_row]).to_csv(DB_FILE, index=False)
                    st.balloons()
                    st.success("✅ Order Submitted")

elif st.session_state.page == "profile":
    st.markdown(f'<h2 style="text-align:center; color:{accent}; margin-top:20px;">{L["nav_profile"]}</h2>', unsafe_allow_html=True)
    
    with st.container():
        if st.session_state.user_email is None:
            if st.button(L["google_btn"], icon="🎯", use_container_width=True):
                st.session_state.user_email = "verified_user@gmail.com"
                st.rerun()
        else:
            st.info(f"Signed in as: {st.session_state.user_email}")
            if st.button(L["logout"]):
                st.session_state.user_email = None
                st.rerun()
            
            st.divider()
            admin_pwd = st.text_input("Admin Key", type="password")
            if admin_pwd == "golden2024":
                st.dataframe(load_data(), use_container_width=True)

# --- 7. MOBILE NAVIGATION BAR ---
st.markdown('<div style="height: 100px;"></div>', unsafe_allow_html=True)
nav1, nav2, nav3 = st.columns(3)
with nav1:
    if st.button(f"🏠 {L['nav_home']}", use_container_width=True): st.session_state.page="home"; st.rerun()
with nav2:
    if st.button(f"🚚 {L['nav_order']}", use_container_width=True): st.session_state.page="order"; st.rerun()
with nav3:
    if st.button(f"👤 {L['nav_profile']}", use_container_width=True): st.session_state.page="profile"; st.rerun()
