import streamlit as st
import pandas as pd
import os
import urllib.parse
from datetime import datetime

# --- 1. ڕێکخستنی لاپەڕە (بۆ مۆبایل centered باشترە) ---
st.set_page_config(page_title="Golden Delivery", layout="centered")

languages = {
    "کوردی 🇭🇺": {
        "dir": "rtl", "align": "right", "theme_label": "ڕووکار", "light": "ڕوون ☀️", "dark": "تاریک 🌙",
        "title": "GOLDEN DELIVERY ✨",
        "subtitle": "خێراترین خزمەتگوزاری گەیاندن لە کەرکوک",
        "customer_name": "👤 ناوی کڕیار", 
        "shop_name": "🏪 ناوی دوکان", 
        "shop_addr": "📍 ناونیشانی دوکان",
        "phone": "📞 ژمارەی مۆبایل", 
        "area": "🏘 گەڕەکی کڕیار", 
        "full_addr": "🏠 وردەکاری ناونیشان (نزیک کوێیە؟)",
        "price": "💰 نرخ (د.ع)",
        "submit": "تۆمارکردنی داواکاری ✅", 
        "wa_btn": "ناردنی وەسڵ بۆ ئۆفیس 💬",
        "track_title": "🔍 بەدواداچوونی داواکاری",
        "track_btn": "بگەڕێ",
        "admin_title": "🛠 پانێڵی بەڕێوەبەرایەتی",
        "admin_pass": "پاسۆرد",
        "status_pending": "⏳ چاوەڕوان", "status_onway": "🚚 لە ڕێگەیە", "status_delivered": "✅ گەیشت"
    },
    "العربية 🇮🇶": {
        "dir": "rtl", "align": "right", "theme_label": "المظهر", "light": "فاتح ☀️", "dark": "داكن 🌙",
        "title": "گولدن دليفري ✨",
        "subtitle": "أسرع خدمة توصيل في كركوك",
        "customer_name": "👤 اسم الزبون", 
        "shop_name": "🏪 اسم المحل", 
        "shop_addr": "📍 عنوان المحل",
        "phone": "📞 رقم الموبايل", 
        "area": "🏘 منطقة الزبون", 
        "full_addr": "🏠 تفاصيل العنوان (قرب ماذا؟)",
        "price": "💰 السعر (د.ع)",
        "submit": "تسجيل الطلبية ✅", 
        "wa_btn": "إرسال للمكتب 💬",
        "track_title": "🔍 تتبع طلبيتك",
        "track_btn": "بحث",
        "admin_title": "🛠 لوحة التحكم",
        "admin_pass": "كلمة المرور",
        "status_pending": "⏳ قيد الانتظار", "status_onway": "🚚 في الطريق", "status_delivered": "✅ تم التوصيل"
    },
    "English 🇬🇧": {
        "dir": "ltr", "align": "left", "theme_label": "Theme", "light": "Light ☀️", "dark": "Dark 🌙",
        "title": "GOLDEN DELIVERY ✨",
        "subtitle": "Fastest delivery service in Kirkuk",
        "customer_name": "👤 Customer Name", 
        "shop_name": "🏪 Shop Name", 
        "shop_addr": "📍 Shop Address",
        "phone": "📞 Phone Number", 
        "area": "🏘 Customer Area", 
        "full_addr": "🏠 Address Details",
        "price": "💰 Price (IQD)",
        "submit": "Register Order ✅", 
        "wa_btn": "Send to Office 💬",
        "track_title": "🔍 Track Your Order",
        "track_btn": "Track",
        "admin_title": "🛠 Admin Panel",
        "admin_pass": "Password",
        "status_pending": "⏳ Pending", "status_onway": "🚚 On the way", "status_delivered": "✅ Delivered"
    }
}

# --- ٢. هەڵبژاردنی زمان و ڕووکار ---
col_lang, col_theme = st.columns(2)
with col_lang:
    lang_choice = st.selectbox("🌐 Language", list(languages.keys()))
    L = languages[lang_choice]
with col_theme:
    theme_choice = st.radio(L['theme_label'], [L['light'], L['dark']], horizontal=True)

# --- ٣. تەنها مەرجەکان لە سایدبار (بە چاککراوی) ---
with st.sidebar:
    st.markdown(f"<h2 style='color:#D4AF37; text-align:center;'>📜 {L['track_title'].split()[-1] if ' ' in L['track_title'] else 'Rules'}</h2>", unsafe_allow_html=True)
    st.markdown("---")
    with st.expander("📦 Rules"):
        st.write("Delivery rules and conditions go here.")
    st.markdown("---")
    st.caption("Golden Delivery - Kirkuk")

# ڕێکخستنی ڕەنگەکان
is_dark = theme_choice == L['dark']
bg_color = "#0e1117" if is_dark else "#f0f2f6"
text_color = "#fafafa" if is_dark else "#31333F"
card_bg = "#161b22" if is_dark else "#ffffff"

# --- ٤. ستایل (گرنگترین بەش بۆ مۆبایل) ---
st.markdown(f"""
    <style>
    /* لادانی کێشەی سایدباری مۆبایل */
    [data-testid="stSidebar"] {{
        z-index: 1000000;
    }}
    
    [data-testid="stAppViewContainer"] {{ 
        direction: {L['dir']}; 
        text-align: {L['align']};
        background-color: {bg_color};
    }}
    
    .brand-header {{ 
        background: linear-gradient(135deg, {"#1a1a1a" if is_dark else "#D4AF37"} 0%, {"#2d2d2d" if is_dark else "#f39c12"} 100%); 
        padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 25px; 
    }}
    .brand-title {{ color: {"#D4AF37" if is_dark else "white"}; font-size: 28px; font-weight: bold; }}
    .stForm {{ border: 2px solid #D4AF37 !important; border-radius: 15px; padding: 15px; background-color: {card_bg} !important; }}
    label {{ color: #D4AF37 !important; font-weight: bold !important; }}
    </style>
    """, unsafe_allow_html=True)

st.markdown(f'<div class="brand-header"><div class="brand-title">{L["title"]}</div><div style="color:{"#ccc" if is_dark else "white"};">{L["subtitle"]}</div></div>', unsafe_allow_html=True)

# --- ٥. لیستی گەڕەکەکان ---
AREAS_WITH_PRICES = {"کوردستان": 3000, "ڕەحیماوا": 3000, "ئیسکان": 3000, "ڕێگای بەغداد": 4000, "واسطی": 4000}
display_areas = ["Choose..."] + [f"{area} - ({price:,})" for area, price in AREAS_WITH_PRICES.items()]

# --- ٦. فۆرمی تۆمارکردن ---
with st.form("delivery_form", clear_on_submit=True):
    customer = st.text_input(L['customer_name'])
    shop = st.text_input(L['shop_name'])
    shop_addr = st.text_input(L['shop_addr'])
    phone = st.text_input(L['phone'], placeholder="07xx xxx xxxx")
    area_selection = st.selectbox(L['area'], display_areas)
    
    selected_price = 0
    if area_selection != "Choose...":
        selected_price = AREAS_WITH_PRICES.get(area_selection.split(" - ")[0], 0)
    
    price = st.number_input(L['price'], min_value=0, step=250, value=selected_price)
    full_addr = st.text_input(L['full_addr'])
    submit = st.form_submit_button(L['submit'])
    
    if submit:
        if not customer or not phone or area_selection == "Choose...":
            st.error("⚠️ Fill all fields")
        else:
            st.success("✅ Registered")
            msg = f"Order: {customer} - {area_selection}"
            st.markdown(f'<a href="https://wa.me/9647801352003?text={urllib.parse.quote(msg)}" target="_blank"><button style="width:100%; background:#25D366; color:white; border:none; padding:15px; border-radius:10px; cursor:pointer; font-weight:bold;">{L["wa_btn"]}</button></a>', unsafe_allow_html=True)

# --- ٧. بەشی بەدواداچوون ---
st.markdown(f'<div style="background:{card_bg}; padding:20px; border-radius:15px; border:1px solid #D4AF37; margin-top:20px;"><h3>{L["track_title"]}</h3>', unsafe_allow_html=True)
track_phone = st.text_input(f"{L['phone']}", key="track_input")
if st.button(L['track_btn']):
    st.warning("Not Found")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div style="text-align:center; padding:20px; color:#666;">Golden Delivery 2024</div>', unsafe_allow_html=True)
