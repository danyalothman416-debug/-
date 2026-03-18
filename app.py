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
        "subtitle": "١ لە ٣ گەیاندن بە خۆڕاییە! 🎁",
        "customer_name": "👤 ناوی کڕیار", "shop_name": "🏪 ناوی دوکان", 
        "shop_addr": "📍 ناونیشانی دوکان", "phone": "📞 ژمارەی مۆبایل", 
        "area": "🏘 گەڕەک (ناوچە)", "full_addr": "🏠 وردەکاری ناونیشان",
        "price": "💰 نرخ (د.ع)", "submit": "تۆمارکردن ✅", 
        "status_pending": "⏳ چاوەڕوان", "nav_home": "سەرەکی", 
        "nav_discount": "دیاری 🎁", "nav_profile": "هەژمار 👤",
        "free_msg": "🎁 پیرۆزە! ئەم گەیاندنەت بە خۆڕاییە (0 د.ع)!",
        "need_more": "ماوەتە بۆ گەیاندنی خۆڕایی: ",
        "google_btn": "چوونەژوورەوە بە Google", "logout": "چوونەدەرەوە",
        "login_req": "تکایە لە بەشی 'هەژمار' بچۆ ژوورەوە بۆ سوودمەندبوون لە دیارییەکان."
    },
    "العربية 🇮🇶": {
        "dir": "rtl", "align": "right", "theme_label": "المظهر", "light": "فاتح ☀️", "dark": "داكن 🌙",
        "title": "گولدن دليفري ✨",
        "subtitle": "١ من كل ٣ توصيلات مجانية! 🎁",
        "customer_name": "👤 اسم الزبون", "shop_name": "🏪 اسم المحل", 
        "shop_addr": "📍 عنوان المحل", "phone": "📞 رقم الموبايل", 
        "area": "🏘 المنطقة", "full_addr": "🏠 تفاصيل العنوان",
        "price": "💰 السعر (د.ع)", "submit": "تسجيل ✅", 
        "status_pending": "⏳ قيد الانتظار", "nav_home": "الرئيسية", 
        "nav_discount": "خصومات 🎁", "nav_profile": "الحساب 👤",
        "free_msg": "🎁 مبروك! هذه الطلبية مجانية (0 د.ع)!",
        "need_more": "متبقي للتوصيل المجاني: ",
        "google_btn": "تسجيل الدخول عبر Google", "logout": "تسجيل الخروج",
        "login_req": "يرجى تسجيل الدخول في قسم 'الحساب' للاستفادة من العروض."
    }
}

# --- 3. ALL KIRKUK NEIGHBORHOODS ---
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

# --- 4. DATA SETUP ---
DB_FILE = "deliveries.csv"
def load_data():
    if os.path.exists(DB_FILE): 
        return pd.read_csv(DB_FILE, dtype={"phone": str})
    return pd.DataFrame(columns=["date", "customer", "shop", "phone", "area", "address", "shop_addr", "price", "status", "user_email"])

# --- 5. UI & STYLING ---
col_lang, col_theme = st.columns(2)
with col_lang:
    lang_choice = st.selectbox("🌐 Language", list(languages.keys()))
    L = languages[lang_choice]
with col_theme:
    theme_choice = st.radio(L['theme_label'], [L['light'], L['dark']], horizontal=True)

is_dark = theme_choice == L['dark']
bg_color = "#121212" if is_dark else "#F4F7F9"
card_bg = "#1E1E1E" if is_dark else "#FFFFFF"
text_color = "#E0E0E0" if is_dark else "#2C3E50"
accent_gold = "#D4AF37"

st.markdown(f"""
    <style>
    [data-testid="stHeader"] {{visibility: hidden;}}
    .stApp {{ background-color: {bg_color}; color: {text_color}; }}
    .brand-header {{
        background: linear-gradient(135deg, {accent_gold} 0%, #8A6D3B 100%);
        padding: 25px; border-radius: 0 0 25px 25px; text-align: center; margin-bottom: 20px;
    }}
    .stForm {{ background-color: {card_bg} !important; border-radius: 15px; border: 1px solid {accent_gold}33; }}
    label {{ color: {accent_gold} !important; font-weight: bold !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 6. PAGE CONTENT ---
if st.session_state.page == "home":
    st.markdown(f'<div class="brand-header"><h1 style="color:white; margin:0;">{L["title"]}</h1><p style="color:white; opacity:0.9;">{L["subtitle"]}</p></div>', unsafe_allow_html=True)
    
    df = load_data()
    
    # Calculate Loyalty based on Phone Number
    with st.container():
        phone_input = st.text_input(L['phone'], key="check_phone", placeholder="07xx xxx xxxx")
        
        is_free = False
        if phone_input:
            user_orders = len(df[df['phone'] == phone_input])
            is_free = (user_orders + 1) % 3 == 0
            if is_free:
                st.balloons()
                st.warning(L["free_msg"])

        with st.form("delivery_form", clear_on_submit=True):
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
                    st.error("❌ Please fill in all details.")
                else:
                    new_row = pd.DataFrame([{
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "customer": customer, "shop": shop, "phone": phone_input, "area": area, 
                        "address": full_addr, "shop_addr": shop_addr, "price": price, 
                        "status": L['status_pending'], "user_email": st.session_state.user_email
                    }])
                    pd.concat([df, new_row]).to_csv(DB_FILE, index=False)
                    st.success("✅ Order Recorded!")

elif st.session_state.page == "offers":
    st.markdown(f'<div class="brand-header"><h2 style="color:white;">{L["nav_discount"]}</h2></div>', unsafe_allow_html=True)
    ph = st.text_input(L['phone'], key="loyalty_search")
    if ph:
        df = load_data()
        count = len(df[df['phone'] == ph])
        st.metric("Total Successful Deliveries", count)
        remaining = 3 - (count % 3)
        if remaining == 3 and count > 0:
            st.success("Your NEXT delivery is 100% FREE!")
        else:
            st.info(f"{L['need_more']} {remaining}")

elif st.session_state.page == "profile":
    st.markdown(f'<div class="brand-header"><h2 style="color:white;">{L["nav_profile"]}</h2></div>', unsafe_allow_html=True)
    
    if st.session_state.user_email is None:
        st.subheader("Login / چوونەژوورەوە")
        if st.button(L["google_btn"], icon="🎯", use_container_width=True):
            st.session_state.user_email = "verified_user@gmail.com" # Simulated login
            st.rerun()
    else:
        st.success(f"Verified: {st.session_state.user_email}")
        if st.button(L["logout"]):
            st.session_state.user_email = None
            st.rerun()
        
        st.divider()
        # Admin section within profile
        pwd = st.text_input("Admin Access", type="password")
        if pwd == "golden2024":
            st.dataframe(load_data(), use_container_width=True)

# --- 7. NAVIGATION BAR ---
st.markdown('<div style="height: 60px;"></div>', unsafe_allow_html=True)
n1, n2, n3 = st.columns(3)
with n1:
    if st.button(L["nav_home"], use_container_width=True): st.session_state.page = "home"; st.rerun()
with n2:
    if st.button(L["nav_discount"], use_container_width=True): st.session_state.page = "offers"; st.rerun()
with n3:
    if st.button(L["nav_profile"], use_container_width=True): st.session_state.page = "profile"; st.rerun()
