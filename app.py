import streamlit as st
import pandas as pd
import os
import urllib.parse
from datetime import datetime
import pytz

# --- 1. ڕێکخستنی سەرەتایی ---
st.set_page_config(page_title="Golden Delivery", layout="wide")

# کاتی بەغداد
baghdad_tz = pytz.timezone('Asia/Baghdad')
current_time = datetime.now(baghdad_tz).strftime("%Y-%m-%d | %I:%M %p")

# --- ٢. سیستەمی زمان و دارک مۆد (State Management) ---
if 'lang' not in st.session_state:
    st.session_state.lang = 'کوردی'

if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

# فەرهەنگی زمانەکان
texts = {
    'کوردی': {
        'title': 'GOLDEN DELIVERY ✨',
        'desc': 'خێراترین و باوەڕپێکراوترین خزمەتگوزاری گەیاندن لە کەرکوک.',
        'clock': '🕒 کاتی ئێستا (بەغداد):',
        'customer': '👤 ناوی کڕیار',
        'shop': '🏪 ناوی دوکان',
        'shop_addr': '📍 ناونیشانی دوکان',
        'phone': '📞 ژمارەی مۆبایل',
        'cust_addr': '🏘 ناونیشانی کڕیار',
        'price': '💰 نرخ',
        'submit': 'تۆمارکردن و ناردن ✅',
        'admin': '🛠 بەشی کارگێڕی',
        'search': '🔍 گەڕان...',
        'install': 'بۆ دابەزاندنی ئەپ: کلیک لە ⎙ بکە و Add to Home Screen هەڵبژێرە'
    },
    'عربي': {
        'title': 'گۆڵدن دیلیڤەری ✨',
        'desc': 'أسرع وأكثر خدمة توصيل موثوقة في كركوك.',
        'clock': '🕒 الوقت الحالي (بغداد):',
        'customer': '👤 اسم الزبون',
        'shop': '🏪 اسم المحل',
        'shop_addr': '📍 عنوان المحل',
        'phone': '📞 رقم الهاتف',
        'cust_addr': '🏘 عنوان الزبون',
        'price': '💰 السعر',
        'submit': 'تسجيل وإرسال ✅',
        'admin': '🛠 قسم الإدارة',
        'search': '🔍 بحث...',
        'install': 'لتثبيت التطبيق: اضغط على ⎙ واختر Add to Home Screen'
    },
    'English': {
        'title': 'GOLDEN DELIVERY ✨',
        'desc': 'The fastest and most reliable delivery service in Kirkuk.',
        'clock': '🕒 Current Time (Baghdad):',
        'customer': '👤 Customer Name',
        'shop': '🏪 Shop Name',
        'shop_addr': '📍 Shop Address',
        'phone': '📞 Phone Number',
        'cust_addr': '🏘 Customer Address',
        'price': '💰 Price',
        'submit': 'Save & Send ✅',
        'admin': '🛠 Admin Panel',
        'search': '🔍 Search...',
        'install': 'To install: Click ⎙ and select Add to Home Screen'
    }
}

L = texts[st.session_state.lang]

# --- ٣. ستایلی CSS (داینامیک بۆ دارک مۆد) ---
bg_color = "#1a1a1a" if st.session_state.theme == 'dark' else "#ffffff"
text_color = "#ffffff" if st.session_state.theme == 'dark' else "#1a1a1a"
card_bg = "#333333" if st.session_state.theme == 'dark' else "#f8f9fa"

st.markdown(f"""
    <style>
    section[data-testid="stSidebar"] {{ display: none !important; }}
    html, body, [data-testid="stAppViewContainer"] {{ 
        direction: {"rtl" if st.session_state.lang != "English" else "ltr"}; 
        text-align: {"right" if st.session_state.lang != "English" else "left"}; 
        background-color: {bg_color}; color: {text_color};
    }}
    .brand-header {{
        background: linear-gradient(135deg, #1a1a1a 0%, #D4AF37 150%);
        padding: 25px; border-radius: 15px; border-bottom: 4px solid #D4AF37;
        text-align: center; margin-bottom: 20px;
    }}
    .live-clock {{
        background-color: {card_bg}; color: {text_color};
        padding: 10px; border-radius: 10px; text-align: center;
        border: 1px solid #D4AF37; margin-bottom: 15px;
    }}
    .install-bar {{
        position: fixed; bottom: 0; left: 0; width: 100%;
        background-color: #1a1a1a; color: white; padding: 12px;
        text-align: center; border-top: 3px solid #D4AF37; z-index: 9999;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- ٤. کۆنتڕۆڵی سەرەوە (زمان و ڕەنگ) ---
col_l, col_r = st.columns([2, 1])
with col_l:
    c1, c2, c3 = st.columns(3)
    if c1.button("☀️ کوردی"): st.session_state.lang = 'کوردی'; st.rerun()
    if c2.button("🇮🇶 عربي"): st.session_state.lang = 'عربي'; st.rerun()
    if c3.button("🇺🇸 English"): st.session_state.lang = 'English'; st.rerun()

with col_r:
    if st.button("🌓 Dark/Light"):
        st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
        st.rerun()

# --- ٥. ڕووکاری سەرەکی ---
st.markdown(f"""
    <div class="brand-header">
        <div style="color:#D4AF37; font-size:32px; font-weight:bold;">{L['title']}</div>
        <div style="color:white; font-size:16px;">{L['desc']}</div>
    </div>
    <div class="live-clock">{L['clock']} {current_time}</div>
""", unsafe_allow_html=True)

# فۆرمەکە
with st.form("delivery_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        customer = st.text_input(L['customer'])
        shop_name = st.text_input(L['shop'])
        shop_address = st.text_input(L['shop_addr'])
    with col2:
        phone = st.text_input(L['phone'])
        customer_address = st.text_input(L['cust_addr'])
        price = st.number_input(L['price'], min_value=0, step=250)
    
    if st.form_submit_button(L['submit']):
        # لۆژیکی سەیڤکردن (هەمان کۆدی پێشوو)
        st.success("✅ Done!")

# بەشی ئەدمین
with st.expander(L['admin']):
    pwd = st.text_input("Password", type="password")
    if pwd == "dr_danyal_2024":
        st.write("Data loading...")

st.markdown(f'<div class="install-bar">{L["install"]}</div>', unsafe_allow_html=True)
