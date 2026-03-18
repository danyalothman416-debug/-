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

# --- 3. NEIGHBORHOOD DATA ---
# Expanded Kirkuk Neighborhoods
KIRKUK_AREAS = sorted([
    "ڕەحیماوا / رحيماوة", "ئیسکان / اسكان", "ئازادی / ازادي", "شۆرجە / شورجة",
    "تەپە / تبة", "ئیمام قاسم / امام قاسم", "قۆریە / قورية", "تسعین / تسعين",
    "طریق بغداد / ڕێگای بەغداد", "واسطی / واسطي", "دۆمیز / دوميز", "غرناطة / غەرناتە",
    "حوزەیران / حزيران", "واحد اذار / یەکی ئازار", "پەنجاعەلی / بنجة علي", 
    "فەیلەق / فيلق", "شۆراو / شوراو", "عرفە / عرفة", "العمل الشعبي", "روناكي / ڕووناکی",
    "الخضراء / گەڕەکی سەوز", "بڕایەتی / برايتي", "الماس / ئەڵماس", "حی عەسکەری / الحي العسكري"
])

# --- 4. THEME & STYLING ---
col_lang, col_theme = st.columns(2)
with col_lang:
    lang_choice = st.selectbox("🌐 Language", list(languages.keys()))
    L = languages[lang_choice]
with col_theme:
    theme_choice = st.radio(L['theme_label'], [L['light'], L['dark']], horizontal=True)

is_dark = theme_choice == L['dark']

# Refined Color Palette
primary_gold = "#D4AF37"
bg_color = "#1a1a1a" if is_dark else "#f0f2f6"
card_bg = "#262626" if is_dark else "#ffffff"
text_color = "#eeeeee" if is_dark else "#1f1f1f"
input_bg = "#333333" if is_dark else "#ffffff"

st.markdown(f"""
    <style>
    [data-testid="stHeader"] {{visibility: hidden;}}
    html, body, [data-testid="stAppViewContainer"] {{
        background-color: {bg_color};
        color: {text_color};
        direction: {L['dir']};
        text-align: {L['align']};
    }}
    .stApp {{ background-color: {bg_color}; }}
    
    /* Header Card */
    .brand-header {{
        background: linear-gradient(135deg, #D4AF37 0%, #B8860B 100%);
        padding: 30px; border-radius: 0 0 25px 25px;
        text-align: center; margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }}
    
    /* Input Fields styling for Dark Mode */
    div[data-baseweb="input"], div[data-baseweb="select"] {{
        background-color: {input_bg} !important;
        border-radius: 10px;
    }}

    /* Bottom Navigation */
    .nav-bar {{
        position: fixed; bottom: 0; left: 0; width: 100%;
        background: {card_bg};
        display: flex; justify-content: space-around;
        padding: 10px 0; border-top: 2px solid {primary_gold};
        z-index: 100;
    }}
    .stButton button {{
        width: 100%; border-radius: 12px;
        border: 1px solid {primary_gold};
        background-color: {card_bg}; color: {text_color};
    }}
    .stButton button:hover {{
        background-color: {primary_gold}; color: white;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. DATA LOGIC ---
DB_FILE = "deliveries.csv"
def load_data():
    if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE, dtype={"phone": str})
    return pd.DataFrame(columns=["date", "customer", "shop", "phone", "area", "address", "shop_addr", "price", "status"])

# --- 6. PAGE CONTENT ---
if st.session_state.page == "home":
    st.markdown(f'<div class="brand-header"><h1 style="color:white; margin:0;">{L["title"]}</h1><p style="color:white; opacity:0.9;">{L["subtitle"]}</p></div>', unsafe_allow_html=True)
    
    with st.container():
        with st.form("main_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                cust = st.text_input(L['customer_name'])
                ph = st.text_input(L['phone'])
                area = st.selectbox(L['area'], ["---"] + KIRKUK_AREAS)
            with col2:
                sh = st.text_input(L['shop_name'])
                sh_ad = st.text_input(L['shop_addr'])
                pr = st.number_input(L['price'], step=500, value=3000)
            
            addr = st.text_area(L['full_addr'])
            if st.form_submit_button(L['submit']):
                if cust and ph and area != "---":
                    df = load_data()
                    new_data = pd.DataFrame([{"date": datetime.now().strftime("%Y-%m-%d"), "customer": cust, "shop": sh, "phone": ph, "area": area, "address": addr, "shop_addr": sh_ad, "price": pr, "status": L['status_pending']}])
                    pd.concat([df, new_data]).to_csv(DB_FILE, index=False)
                    st.success("✅ Saved!")
                else:
                    st.error("❌ Fill required fields")

elif st.session_state.page == "offers":
    st.markdown(f'<div class="brand-header"><h2 style="color:white;">{L["nav_discount"]}</h2></div>', unsafe_allow_html=True)
    search_ph = st.text_input(L['phone'], key="search_off")
    if search_ph:
        df = load_data()
        count = len(df[df['phone'] == search_ph])
        st.metric(label="Total Deliveries", value=count)
        if count >= 5: st.balloons(); st.success(L['free_msg'])
        else: st.info(f"{L['need_more']} {5 - count}")

elif st.session_state.page == "profile":
    st.markdown(f'<div class="brand-header"><h2 style="color:white;">{L["nav_profile"]}</h2></div>', unsafe_allow_html=True)
    admin_pass = st.text_input("Admin Access", type="password")
    if admin_pass == "golden2026":
        st.dataframe(load_data(), use_container_width=True)

# --- 7. STICKY BOTTOM NAVIGATION ---
st.markdown("<br><br><br>", unsafe_allow_html=True)
nav_cols = st.columns(3)
with nav_cols[0]:
    if st.button(f"🏠 {L['nav_home']}"):
        st.session_state.page = "home"
        st.rerun()
with nav_cols[1]:
    if st.button(f"🎁 {L['nav_discount']}"):
        st.session_state.page = "offers"
        st.rerun()
with nav_cols[2]:
    if st.button(f"👤 {L['nav_profile']}"):
        st.session_state.page = "profile"
        st.rerun()
