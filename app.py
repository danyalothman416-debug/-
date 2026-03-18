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
    "کوردی 🇭🇺": {
        "dir": "rtl", "align": "right", "theme_label": "ڕووکار", "light": "ڕوون ☀️", "dark": "تاریک 🌙",
        "title": "GOLDEN DELIVERY ✨",
        "desc": "بەخێربێن بۆ گۆڵدن دلیڤەری! خێراترین و باوەڕپێکراوترین خزمەتگوزاری گەیاندن لە شارە جوانەکەی کەرکوک. ئێمە لێرەین بۆ ئەوەی کاڵاکانتان بەوپەڕی پاراستن و خێرایی بگەیەنینە جێگەی مەبەست. متمانەی ئێوە، ئامانجی ئێمەیە.",
        "customer_name": "👤 ناوی کڕیار", "shop_name": "🏪 ناوی دوکان", 
        "shop_addr": "📍 ناونیشانی دوکان", "phone": "📞 ژمارەی مۆبایل", 
        "area": "🏘 گەڕەک (ناوچە)", "full_addr": "🏠 وردەکاری ناونیشان",
        "price": "💰 نرخ (د.ع)", "submit": "تۆمارکردنی داواکاری ✅", 
        "status_pending": "⏳ چاوەڕوان", "nav_home": "سەرەکی", 
        "nav_order": "داواکردن 🚚", "nav_profile": "هەژمار 👤",
        "free_info": "🎁 ئۆفەری تایبەت: لە هەر ٣ گەیاندن، یەکێکیان بە خۆڕاییە!",
        "free_success": "🎊 پیرۆزە! ئەمە سێیەم گەیاندنە و ئەمڕۆ بڕی ٠ دینار دەدەیت!",
        "google_btn": "چوونەژوورەوە بە Google", "logout": "چوونەدەرەوە",
        "login_req": "تکایە لە بەشی هەژمار بچۆ ژوورەوە."
    },
    "العربية 🇮🇶": {
        "dir": "rtl", "align": "right", "theme_label": "المظهر", "light": "فاتح ☀️", "dark": "داكن 🌙",
        "title": "گولدن دليفري ✨",
        "desc": "أهلاً بكم في گولدن دليفري! أسرع خدمة توصيل وأكثرها موثوقية في مدينة كركوك الجميلة. نحن هنا لنقل بضائعكم بكل أمان وسرعة فائقة. ثقتكم هي هدفنا الأسمى.",
        "customer_name": "👤 اسم الزبون", "shop_name": "🏪 اسم المحل", 
        "shop_addr": "📍 عنوان المحل", "phone": "📞 رقم الموبايل", 
        "area": "🏘 المنطقة", "full_addr": "🏠 تفاصيل العنوان",
        "price": "💰 السعر (د.ع)", "submit": "تسجيل الطلب ✅", 
        "status_pending": "⏳ قيد الانتظار", "nav_home": "الرئيسية", 
        "nav_order": "طلب توصيل 🚚", "nav_profile": "الحساب 👤",
        "free_info": "🎁 عرض خاص: واحدة من كل ٣ توصيلات مجانية تماماً!",
        "free_success": "🎊 مبروك! هذا هو التوصيل الثالث، ستدفع ٠ دينار اليوم!",
        "google_btn": "تسجيل الدخول عبر Google", "logout": "تسجيل الخروج",
        "login_req": "يرجى تسجيل الدخول في قسم الحساب."
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

# --- 4. DATA LOGIC ---
DB_FILE = "deliveries.csv"
def load_data():
    if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE, dtype={"phone": str})
    return pd.DataFrame(columns=["date", "customer", "shop", "phone", "area", "address", "shop_addr", "price", "status", "user_email"])

# --- 5. THEME & STYLING ---
col_lang, col_theme = st.columns(2)
with col_lang:
    lang_choice = st.selectbox("🌐", list(languages.keys()))
    L = languages[lang_choice]
with col_theme:
    theme_choice = st.radio(L['theme_label'], [L['light'], L['dark']], horizontal=True)

is_dark = theme_choice == L['dark']
bg_color = "#121212" if is_dark else "#F8F9FA"
card_bg = "#1E1E1E" if is_dark else "#FFFFFF"
text_color = "#EEEEEE" if is_dark else "#2C3E50"
accent_gold = "#D4AF37"

st.markdown(f"""
    <style>
    [data-testid="stHeader"] {{visibility: hidden;}}
    .stApp {{ background-color: {bg_color}; color: {text_color}; }}
    .brand-header {{
        background: linear-gradient(135deg, {accent_gold} 0%, #B8860B 100%);
        padding: 40px 20px; border-radius: 0 0 40px 40px; text-align: center; margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }}
    .hero-text {{ font-size: 1.2rem; line-height: 1.6; opacity: 0.95; padding: 20px; }}
    label {{ color: {accent_gold} !important; font-weight: bold !important; }}
    .stForm {{ background-color: {card_bg} !important; border-radius: 20px; border: 1px solid {accent_gold}44; }}
    </style>
    """, unsafe_allow_html=True)

# --- 6. PAGE LOGIC ---

# HOME PAGE
if st.session_state.page == "home":
    st.markdown(f'<div class="brand-header"><h1 style="color:white; margin:0;">{L["title"]}</h1></div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="text-align: center; max-width: 800px; margin: auto;">
        <h2 style="color:{accent_gold};">Kirkuk's #1 Delivery Partner</h2>
        <p class="hero-text">{L["desc"]}</p>
        <hr style="border: 0.5px solid {accent_gold}55;">
        <div style="display: flex; justify-content: space-around; margin-top: 20px;">
            <div>🚀 <b>خێرا</b></div>
            <div>🛡️ <b>پارێزراو</b></div>
            <div>💰 <b>گونجاو</b></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# DELIVERY PAGE
elif st.session_state.page == "order":
    st.markdown(f'<div class="brand-header"><h2 style="color:white; margin:0;">{L["nav_order"]}</h2></div>', unsafe_allow_html=True)
    
    # Loyalty Announcement
    st.info(L["free_info"])
    
    df = load_data()
    phone_input = st.text_input(L['phone'], placeholder="07xx xxx xxxx")
    
    is_free = False
    if phone_input:
        user_orders = len(df[df['phone'] == phone_input])
        is_free = (user_orders + 1) % 3 == 0
        if is_free:
            st.success(L["free_success"])

    with st.form("main_order_form"):
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
            if not customer or not phone_input or "--" in area:
                st.error("⚠️ Fill all required fields.")
            else:
                new_row = pd.DataFrame([{
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "customer": customer, "shop": shop, "phone": phone_input, "area": area, 
                    "address": full_addr, "shop_addr": shop_addr, "price": price, 
                    "status": L['status_pending'], "user_email": st.session_state.user_email
                }])
                pd.concat([df, new_row]).to_csv(DB_FILE, index=False)
                st.balloons()
                st.success("✅ Order Sent!")

# PROFILE PAGE
elif st.session_state.page == "profile":
    st.markdown(f'<div class="brand-header"><h2 style="color:white; margin:0;">{L["nav_profile"]}</h2></div>', unsafe_allow_html=True)
    
    if st.session_state.user_email is None:
        st.subheader("Login with Google")
        if st.button(L["google_btn"], icon="🎯", use_container_width=True):
            st.session_state.user_email = "user@gmail.com" # Simulated
            st.rerun()
    else:
        st.write(f"Account: **{st.session_state.user_email}**")
        if st.button(L["logout"]):
            st.session_state.user_email = None
            st.rerun()
        
        st.divider()
        pwd = st.text_input("Admin", type="password")
        if pwd == "golden2024":
            st.dataframe(load_data(), use_container_width=True)

# --- 7. STICKY NAV ---
st.markdown('<div style="height: 80px;"></div>', unsafe_allow_html=True)
n1, n2, n3 = st.columns(3)
with n1:
    if st.button(L["nav_home"], use_container_width=True): st.session_state.page = "home"; st.rerun()
with n2:
    if st.button(L["nav_order"], use_container_width=True): st.session_state.page = "order"; st.rerun()
with n3:
    if st.button(L["nav_profile"], use_container_width=True): st.session_state.page = "profile"; st.rerun()
