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

# وێنەی ئاڵاکان (لینکەکان)
FLAG_KURD = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/35/Flag_of_Kurdistan.svg/320px-Flag_of_Kurdistan.svg.png"
FLAG_IRAQ = "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Flag_of_Iraq.svg/320px-Flag_of_Iraq.svg.png"
FLAG_USA = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a4/Flag_of_the_United_States.svg/320px-Flag_of_the_United_States.svg.png"

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

# --- ٣. ستایلی CSS ---
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
        text-align: center; margin-bottom: 25px;
    }}
    .selector-card {{
        background-color: {card_bg}; padding: 20px; border-radius: 15px;
        border: 1px solid #D4AF37; margin-bottom: 20px;
    }}
    .flag-img {{ width: 25px; vertical-align: middle; margin: 0 5px; border-radius: 3px; }}
    .install-bar {{
        position: fixed; bottom: 0; left: 0; width: 100%;
        background-color: #1a1a1a; color: white; padding: 12px;
        text-align: center; border-top: 3px solid #D4AF37; z-index: 9999;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- ٤. کۆنتڕۆڵەکان (زمان و ڕەنگ بە وێنەی ئاڵاکانەوە) ---
with st.container():
    st.markdown('<div class="selector-card">', unsafe_allow_html=True)
    col_lang, col_mode = st.columns([4, 1])
    
    with col_lang:
        st.write(f"**{L['lang_label']}**")
        # دروستکردنی ٣ دوگمە بۆ زمانەکان بە وێنەی ئاڵاوە
        c1, c2, c3 = st.columns(3)
        if c1.button("☀️ کوردی"): 
            st.session_state.lang = 'کوردی'; st.rerun()
        if c2.button("🇮🇶 عربي"): 
            st.session_state.lang = 'عربي'; st.rerun()
        if c3.button("🇺🇸 English"): 
            st.session_state.lang = 'English'; st.rerun()
        
        # پیشاندانی ئاڵا ڕاستەقینەکان لە ژێر دوگمەکان وەک هێما
        st.markdown(f"""
            <div style="margin-top: 5px;">
                <img src="{FLAG_KURD}" class="flag-img"> <img src="{FLAG_IRAQ}" class="flag-img"> <img src="{FLAG_USA}" class="flag-img">
            </div>
        """, unsafe_allow_html=True)

    with col_mode:
        if st.button("🌓 Mode"):
            st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- ٥. ڕووکاری سەرەکی ---
st.markdown(f"""
    <div class="brand-header">
        <div style="color:#D4AF37; font-size:38px; font-weight:bold;">{L['title']}</div>
        <div style="color:white; font-size:18px;">{L['desc']}</div>
    </div>
    <div style="background-color:{card_bg}; padding:10px; border-radius:10px; text-align:center; border:1px solid #D4AF37; margin-bottom:20px;">
        {L['clock']} <b>{current_time}</b>
    </div>
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
        if customer and shop_name and phone:
            st.success("✅ Done!")
        else:
            st.error("⚠️ Fill all fields")

# بەشی ئەدمین
with st.expander(L['admin']):
    if st.text_input("🔑 Password", type="password") == "dr_danyal_2024":
        st.write("Admin access...")

st.markdown(f'<div class="install-bar">{L["install"]}</div>', unsafe_allow_html=True)
