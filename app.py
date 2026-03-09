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

# --- ٢. سیستەمی زمان و دارک مۆد ---
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
        'install': 'بۆ دابەزاندنی ئەپ: کلیک لە ⎙ بکە و Add to Home Screen هەڵبژێرە',
        'lang_label': 'زمان هەڵبژێرە / اختر اللغة'
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
        'install': 'لتثبيت التطبيق: اضغط على ⎙ واختر Add to Home Screen',
        'lang_label': 'زمان هەڵبژێرە / اختر اللغة'
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
        'install': 'To install: Click ⎙ and select Add to Home Screen',
        'lang_label': 'Choose Language'
    }
}

L = texts[st.session_state.lang]

# --- ٣. ستایلی CSS مۆدێرن ---
bg_color = "#121212" if st.session_state.theme == 'dark' else "#ffffff"
text_color = "#e0e0e0" if st.session_state.theme == 'dark' else "#1a1a1a"
card_bg = "#1e1e1e" if st.session_state.theme == 'dark' else "#f0f2f6"

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
        padding: 30px; border-radius: 20px; border-bottom: 5px solid #D4AF37;
        text-align: center; margin-bottom: 25px; box-shadow: 0 10px 20px rgba(0,0,0,0.3);
    }}
    .selector-card {{
        background-color: {card_bg}; padding: 15px; border-radius: 15px;
        border: 1px solid #D4AF37; margin-bottom: 20px;
    }}
    .live-clock {{
        background-color: {card_bg}; color: #D4AF37; padding: 12px;
        border-radius: 12px; text-align: center; font-weight: bold;
        border: 1px dashed #D4AF37; margin-bottom: 20px;
    }}
    .install-bar {{
        position: fixed; bottom: 0; left: 0; width: 100%;
        background-color: #1a1a1a; color: white; padding: 12px;
        text-align: center; border-top: 3px solid #D4AF37; z-index: 9999;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- ٤. کۆنتڕۆڵەکان (زمان و ڕەنگ لە یەک چوارگۆشەدا) ---
with st.container():
    st.markdown(f'<div class="selector-card">', unsafe_allow_html=True)
    c1, c2 = st.columns([3, 1])
    
    with c1:
        # هەڵبژاردنی زمان بە ئاڵاکانەوە لە یەک ڕیزدا
        new_lang = st.radio(
            L['lang_label'],
            options=['کوردی', 'عربي', 'English'],
            index=['کوردی', 'عربي', 'English'].index(st.session_state.lang),
            horizontal=True,
            format_func=lambda x: "☀️💚🤍❤️ کوردی" if x == 'کوردی' else ("🇮🇶 عربي" if x == 'عربي' else "🇺🇸 English")
        )
        if new_lang != st.session_state.lang:
            st.session_state.lang = new_lang
            st.rerun()

    with c2:
        if st.button("🌓 Mode"):
            st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- ٥. ڕووکاری سەرەکی ---
st.markdown(f"""
    <div class="brand-header">
        <div style="color:#D4AF37; font-size:38px; font-weight:bold; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);">{L['title']}</div>
        <div style="color:white; font-size:18px; opacity: 0.9;">{L['desc']}</div>
    </div>
    <div class="live-clock">{L['clock']} {current_time}</div>
""", unsafe_allow_html=True)

# فۆرمەکە (بە داینامیکی بەپێی زمان)
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
        if customer and shop_name and phone:
            st.balloons()
            st.success("✅ Done!")
        else:
            st.error("⚠️ Please fill all fields")

# بەشی ئەدمین
st.write("---")
with st.expander(L['admin']):
    pwd = st.text_input("🔑 Password", type="password")
    if pwd == "dr_danyal_2024":
        st.info("Admin Access Granted")

st.markdown(f'<div class="install-bar">{L["install"]}</div>', unsafe_allow_html=True)
