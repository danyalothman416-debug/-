import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Golden Delivery", layout="wide", initial_sidebar_state="collapsed")

if 'page' not in st.session_state:
    st.session_state.page = "home"

# --- 2. MULTI-LANGUAGE & UI STRINGS ---
languages = {
    "کوردی 🇭🇺": {
        "dir": "rtl", "align": "right", "theme_label": "ڕووکار", "light": "ڕوون ☀️", "dark": "تاریک 🌙",
        "title": "GOLDEN DELIVERY ✨",
        "subtitle": "خێراترین گەیاندن لە کەرکوک",
        "customer_name": "👤 ناوی کڕیار", "shop_name": "🏪 ناوی دوکان", 
        "shop_addr": "📍 ناونیشانی دوکان", "phone": "📞 ژمارەی مۆبایل", 
        "area": "🏘 گەڕەک (ناوچە)", "full_addr": "🏠 وردەکاری ناونیشان",
        "price": "💰 نرخ (د.ع)", "submit": "تۆمارکردن ✅", 
        "status_pending": "⏳ چاوەڕوان", "nav_home": "سەرەکی", 
        "nav_discount": "دیاری", "nav_profile": "هەژمار",
        "free_msg": "🎁 پیرۆزە! ئەم گەیاندنە بە خۆڕاییە!",
        "need_more": "ماوەتە بۆ دیاری: ", "search": "بگەڕێ"
    },
    "العربية 🇮🇶": {
        "dir": "rtl", "align": "right", "theme_label": "المظهر", "light": "فاتح ☀️", "dark": "داكن 🌙",
        "title": "گولدن دليفري ✨",
        "subtitle": "أسرع خدمة توصيل في كركوك",
        "customer_name": "👤 اسم الزبون", "shop_name": "🏪 اسم المحل", 
        "shop_addr": "📍 عنوان المحل", "phone": "📞 رقم الموبايل", 
        "area": "🏘 المنطقة", "full_addr": "🏠 تفاصيل العنوان",
        "price": "💰 السعر (د.ع)", "submit": "تسجيل ✅", 
        "status_pending": "⏳ قيد الانتظار", "nav_home": "الرئيسية", 
        "nav_discount": "خصومات", "nav_profile": "الحساب",
        "free_msg": "🎁 مبروك! هذا التوصيل مجاني!",
        "need_more": "متبقي للخصم: ", "search": "بحث"
    }
}

# --- 3. UPDATED NEIGHBORHOOD DATA ---
# Includes all requested areas
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

# --- 4. REFINED DARK MODE & THEME ---
col_lang, col_theme = st.columns(2)
with col_lang:
    lang_choice = st.selectbox("🌐 Language", list(languages.keys()))
    L = languages[lang_choice]
with col_theme:
    theme_choice = st.radio(L['theme_label'], [L['light'], L['dark']], horizontal=True)

is_dark = theme_choice == L['dark']

# Elegant Dark Mode Palette
bg_color = "#121212" if is_dark else "#F4F7F9"
card_bg = "#1E1E1E" if is_dark else "#FFFFFF"
text_color = "#E0E0E0" if is_dark else "#2C3E50"
accent_gold = "#D4AF37"
input_fill = "#2D2D2D" if is_dark else "#F9F9F9"

st.markdown(f"""
    <style>
    [data-testid="stHeader"] {{visibility: hidden;}}
    .stApp {{ background-color: {bg_color}; }}
    
    html, body, [data-testid="stAppViewContainer"] {{
        background-color: {bg_color};
        color: {text_color};
        direction: {L['dir']};
        text-align: {L['align']};
    }}

    /* Header Styling */
    .brand-header {{
        background: linear-gradient(135deg, {accent_gold} 0%, #8A6D3B 100%);
        padding: 35px 20px; border-radius: 0 0 40px 40px;
        text-align: center; margin-bottom: 20px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.3);
    }}
    
    /* Inputs Styling */
    div[data-baseweb="input"], div[data-baseweb="select"], .stTextArea textarea {{
        background-color: {input_fill} !important;
        border: 1px solid {accent_gold}33 !important;
        border-radius: 12px !important;
        color: {text_color} !important;
    }}
    
    label {{ color: {accent_gold} !important; font-weight: bold !important; }}

    /* Custom Form Card */
    .stForm {{
        background-color: {card_bg} !important;
        border-radius: 20px !important;
        padding: 25px !important;
        border: 1px solid {accent_gold}22 !important;
        box-shadow: 0 8px 32px rgba(0,0,0,0.2) !important;
    }}

    /* Bottom Nav Bar */
    .nav-container {{
        position: fixed; bottom: 0; left: 0; width: 100%;
        background-color: {card_bg};
        display: flex; justify-content: space-around;
        padding: 15px 0; border-top: 2px solid {accent_gold};
        z-index: 999;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. DATA MANAGEMENT ---
DB_FILE = "deliveries.csv"
def load_data():
    if os.path.exists(DB_FILE): 
        return pd.read_csv(DB_FILE, dtype={"phone": str})
    return pd.DataFrame(columns=["date", "customer", "shop", "phone", "area", "address", "shop_addr", "price", "status"])

# --- 6. PAGE LOGIC ---
if st.session_state.page == "home":
    st.markdown(f'<div class="brand-header"><h1 style="color:white; margin:0; font-size: 2.5rem;">{L["title"]}</h1><p style="color:white; opacity:0.9;">{L["subtitle"]}</p></div>', unsafe_allow_html=True)
    
    with st.form("delivery_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            customer = st.text_input(L['customer_name'])
            phone = st.text_input(L['phone'], placeholder="07xx xxx xxxx")
            area = st.selectbox(L['area'], ["-- Select Area --"] + KIRKUK_AREAS)
        with c2:
            shop = st.text_input(L['shop_name'])
            shop_addr = st.text_input(L['shop_addr'])
            price = st.number_input(L['price'], min_value=0, step=250, value=3000)
            
        full_addr = st.text_area(L['full_addr'])
        
        submit = st.form_submit_button(L['submit'], use_container_width=True)
        
        if submit:
            if not customer or not phone or "--" in area:
                st.error("⚠️ Please fill in the Customer, Phone, and Area.")
            else:
                df = load_data()
                new_row = pd.DataFrame([{
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "customer": customer, "shop": shop, "phone": phone,
                    "area": area, "address": full_addr, 
                    "shop_addr": shop_addr, "price": price, 
                    "status": L['status_pending']
                }])
                pd.concat([df, new_row]).to_csv(DB_FILE, index=False)
                st.success("✅ Order Registered!")

elif st.session_state.page == "offers":
    st.markdown(f'<div class="brand-header"><h2 style="color:white;">{L["nav_discount"]}</h2></div>', unsafe_allow_html=True)
    search_p = st.text_input(L['phone'], key="search_loyalty")
    if search_p:
        df = load_data()
        count = len(df[df['phone'] == search_p])
        st.subheader(f"Total Deliveries: {count}")
        if count >= 3:
            st.balloons()
            st.success(L['free_msg'])
        else:
            st.info(f"{L['need_more']} {3 - count}")

elif st.session_state.page == "profile":
    st.markdown(f'<div class="brand-header"><h2 style="color:white;">{L["nav_profile"]}</h2></div>', unsafe_allow_html=True)
    pwd = st.text_input("Admin Password", type="password")
    if pwd == "golden2024":
        df = load_data()
        st.dataframe(df, use_container_width=True)

# --- 7. STICKY NAVIGATION ---
st.markdown('<div style="height: 100px;"></div>', unsafe_allow_html=True)
nav_cols = st.columns(3)
with nav_cols[0]:
    if st.button(f"🏠 {L['nav_home']}", use_container_width=True):
        st.session_state.page = "home"
        st.rerun()
with nav_cols[1]:
    if st.button(f"🏷️ {L['nav_discount']}", use_container_width=True):
        st.session_state.page = "offers"
        st.rerun()
with nav_cols[2]:
    if st.button(f"⚙️ {L['nav_profile']}", use_container_width=True):
        st.session_state.page = "profile"
        st.rerun()
