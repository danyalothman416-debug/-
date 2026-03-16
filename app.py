import streamlit as st
import pandas as pd
import os
import urllib.parse
from datetime import datetime
import plotly.express as px
import folium
from streamlit_folium import st_folium

# --- 1. ڕێکخستنی لاپەڕە ---
st.set_page_config(page_title="Golden Delivery", layout="wide", initial_sidebar_state="collapsed")

# --- ٢. زمانەکان (هەموو زمانەکان بە وردی) ---
languages = {
    "کوردی 🇭🇺": {
        "dir": "rtl", "title": "گۆڵدن دێلیڤەری ✨", "subtitle": "خێراترین گەیاندن لە کەرکوک",
        "customer": "👤 ناوی کڕیار", "shop": "🏪 ناوی دوکان", "phone": "📞 مۆبایل",
        "area": "🏘 گەڕەک", "price": "💰 نرخ", "submit": "تۆمارکردن ✅",
        "wa": "ناردنی وەسڵ 💬", "track": "🔍 بەدواداچوونی داواکاری", "admin": "🛠 پانێڵی بەڕێوەبەر"
    },
    "Türkmençe 🇮🇶": {
        "dir": "ltr", "title": "Golden Delivery ✨", "subtitle": "Kerkük'te en hızlı hizmet",
        "customer": "👤 Müşteri", "shop": "🏪 Mağaza", "phone": "📞 Telefon",
        "area": "🏘 Bölge", "price": "💰 Fiyat", "submit": "Kaydet ✅",
        "wa": "WhatsApp'a Gönder 💬", "track": "🔍 Sipariş Takibi", "admin": "🛠 Yönetici Paneli"
    },
    "العربية 🇮🇶": {
        "dir": "rtl", "title": "گولدن دليفري ✨", "subtitle": "أسرع خدمة في كركوك",
        "customer": "👤 الاسم", "shop": "🏪 المحل", "phone": "📞 الهاتف",
        "area": "🏘 المنطقة", "price": "💰 السعر", "submit": "تسجيل ✅",
        "wa": "إرسال واتساب 💬", "track": "🔍 تتبع طلبيتك", "admin": "🛠 لوحة التحكم"
    }
}

# --- ٣. دیزاینی پێشکەوتوو (CSS) بۆ ئەوەی وەک ئەپی بڵی بێت ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Tajawal', sans-serif;
        background: linear-gradient(180deg, #0f0f0f 0%, #1a1a1a 100%);
        color: #ffffff;
    }
    
    /* کارتەکان */
    .app-card {
        background: rgba(255, 255, 255, 0.05);
        padding: 25px;
        border-radius: 25px;
        border: 1px solid rgba(212, 175, 55, 0.3);
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        margin-bottom: 20px;
    }
    
    /* دیزاینی دوگمەکان */
    .stButton>button {
        width: 100%;
        border-radius: 15px;
        background: linear-gradient(90deg, #D4AF37 0%, #f39c12 100%) !important;
        color: black !important;
        font-weight: bold;
        border: none;
        padding: 15px;
        font-size: 18px;
        transition: 0.3s;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(212, 175, 55, 0.4);
    }

    /* ئینپوتەکان */
    input, select, .stNumberInput {
        border-radius: 12px !important;
        background-color: #262626 !important;
        color: white !important;
        border: 1px solid #444 !important;
    }
    
    label { color: #D4AF37 !important; font-size: 14px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- ٤. هەڵبژاردنی زمان ---
lang_choice = st.selectbox("🌐 Language / زمان", list(languages.keys()))
L = languages[lang_choice]

# --- ٥. نەخشە و زانیارییەکان (وەک کۆدەکەی خۆت) ---
AREA_COORDS = {
    "ڕەحیماوا / Rahimawa": [35.4950, 44.3910], "ئیسکان / Iskan": [35.4820, 44.3980],
    "ئازادی / Azadi": [35.4750, 44.4050], "ڕێگای بەغداد / Baghdad Road": [35.4520, 44.3680],
    "تسعین / Taseen": [35.4510, 44.3750], "واسطی / Wasit": [35.4180, 44.3620],
    "کوردستان / Kurdistan": [35.5050, 44.4010], "موسەڵا / Musalla": [35.4650, 44.3950],
    "دۆمیز / Domiz": [35.4250, 44.3850], "حوزەیران / Huzairan": [35.4150, 44.3750],
    "پەنجاعەلی / Panja Ali": [35.4650, 44.4350]
}

# --- ٦. لۆگۆ و سەردێڕ ---
st.markdown(f"""
    <div style="text-align:center; padding: 20px;">
        <h1 style="color:#D4AF37; margin-bottom:0;">{L['title']}</h1>
        <p style="color:#888;">{L['subtitle']}</p>
    </div>
    """, unsafe_allow_html=True)

# --- ٧. فۆرمی تۆمارکردن (بە شێوەی کارت) ---
st.markdown('<div class="app-card">', unsafe_allow_html=True)
with st.form("delivery_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        customer = st.text_input(L['customer'])
        shop = st.text_input(L['shop'])
    with col2:
        phone = st.text_input(L['phone'])
        area = st.selectbox(L['area'], list(AREA_COORDS.keys()))
    
    price = st.number_input(L['price'], value=4000, step=500)
    submit = st.form_submit_button(L['submit'])
    
    if submit:
        if customer and phone:
            st.success("✅ بەسەرکەوتوویی تۆمارکرا")
            st.session_state.submitted = True
            st.session_state.last_order = {"name": customer, "area": area}
st.markdown('</div>', unsafe_allow_html=True)

# دوگمەی واتسئاپ
if st.session_state.get("submitted"):
    msg = f"📦 داواکاری نوێ\n👤 کڕیار: {st.session_state.last_order['name']}\n📍 گەڕەک: {st.session_state.last_order['area']}"
    wa_url = f"https://wa.me/9647801352003?text={urllib.parse.quote(msg)}"
    st.markdown(f'<a href="{wa_url}" target="_blank"><button style="width:100%; background:#25D366; color:white; border:none; padding:15px; border-radius:15px; cursor:pointer; font-weight:bold; margin-bottom:20px;">{L["wa"]}</button></a>', unsafe_allow_html=True)

# --- ٨. بەشی بەدواداچوون ---
st.markdown(f'<div class="app-card"><h3>{L["track"]}</h3>', unsafe_allow_html=True)
t_phone = st.text_input("ژمارەی مۆبایل بنووسە")
if st.button("گەڕان 🔎"):
    st.info("لێرەدا زانیارییەکان پیشان دەدرێن")
st.markdown('</div>', unsafe_allow_html=True)

# --- ٩. پانێڵی ئەدمین ---
if st.query_params.get("role") == "boss":
    st.markdown(f'<div class="app-card"><h3>{L["admin"]}</h3>', unsafe_allow_html=True)
    if st.text_input("Password", type="password") == "golden2024":
        m = folium.Map(location=[35.4687, 44.3925], zoom_start=12)
        st_folium(m, width="100%", height=400)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<p style="text-align:center; color:#444;">Golden Delivery v2.0</p>', unsafe_allow_html=True)
