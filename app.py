import streamlit as st
import pandas as pd
import os
import urllib.parse
from streamlit_js_eval import streamlit_js_eval

# --- 1. ڕێکخستنی لاپەڕە و زمان ---
st.set_page_config(page_title="Golden Delivery", layout="wide")

languages = {
    "کوردی 🇭🇺": {
        "get_gps": "📍 دیاریکردنی شوێنی کڕیار (GPS)",
        "gps_info": "تکایە ئەگەر مۆبایلەکەت داوای کرد، کلیک لە 'Allow' یان 'ڕێپێدان' بکە بۆ وەرگرتنی شوێنەکە.",
        "gps_success": "✅ شوێنەکەت دیاریکرا!",
        "location_label": "📍 لینکی نەخشە (خۆکار)",
        "title": "GOLDEN DELIVERY ✨",
        "subtitle": "خێراترین و باوەڕپێکراوترین خزمەتگوزاری گەیاندن لە کەرکوک",
        "customer_name": "👤 ناوی کڕیار",
        "shop_name": "🏪 ناوی دوکان",
        "shop_addr": "📍 ناونیشانی دوکان",
        "phone": "📞 ژمارەی مۆبایل",
        "area": "🏘 گەڕەکی کڕیار",
        "full_addr": "🏠 وردەکاری ناونیشان (نزیک کوێیە؟)",
        "price": "💰 نرخ (د.ع)",
        "submit": "تۆمارکردن و ناردنی وەسڵ ✅",
        "wa_btn": "ناردنی زانیاری بۆ ئۆفیس 💬",
        "error": "⚠️ تکایە ناوی کڕیار و مۆبایل و گەڕەک پڕ بکەرەوە",
        "success": "✅ بە سەرکەوتوویی تۆمارکرا",
        "footer": "بۆ دابەزاندنی ئەپ: کلیک لە ⎙ یان ⋮ بکە و Add to Home Screen هەڵبژێرە"
    },
    "العربية 🇮🇶": {
        "get_gps": "📍 تحديد موقع الزبون (GPS)",
        "gps_info": "يرجى الضغط على 'Allow' أو 'سماح' إذا طلب المتصفح ذلك لتحديد موقعك.",
        "gps_success": "✅ تم تحديد موقعك!",
        "location_label": "📍 رابط الخريطة (تلقائي)",
        "title": "گولدن دليفري ✨",
        "subtitle": "أسرع وخدمة توصيل موثوقة في كركوك",
        "customer_name": "👤 اسم الزبون",
        "shop_name": "🏪 اسم المحل",
        "shop_addr": "📍 عنوان المحل",
        "phone": "📞 رقم الموبايل",
        "area": "🏘 منطقة الزبون",
        "full_addr": "🏠 تفاصيل العنوان (قرب ماذا؟)",
        "price": "💰 السعر (د.ع)",
        "submit": "تسجيل وإرسال الوصل ✅",
        "wa_btn": "إرسال البيانات للمكتب 💬",
        "error": "⚠️ يرجى ملء اسم الزبون والموبايل والمنطقة",
        "success": "✅ تم التسجيل بنجاح",
        "footer": "لتثبيت التطبيق: اضغط على ⎙ أو ⋮ واختر Add to Home Screen"
    }
}

if "selected_lang" not in st.session_state:
    st.session_state.selected_lang = "کوردی 🇭🇺"

col_ref, col_lang, col_space = st.columns([0.5, 1.5, 4])
with col_ref:
    if st.button("🔄"): st.rerun()
with col_lang:
    lang_choice = st.selectbox("🌐 Language", list(languages.keys()), index=list(languages.keys()).index(st.session_state.selected_lang))
    st.session_state.selected_lang = lang_choice

L = languages[st.session_state.selected_lang]

# --- جی پی ئێس (GPS) ---
st.info(f"{L['gps_info']}")
# بانگکردنی فەنکشنەکە بۆ وەرگرتنی پۆتانەکان
loc = streamlit_js_eval(data_key='pos', func_name='getCurrentPosition', component_value=None)

gps_link = ""
if loc:
    lat = loc['coords']['latitude']
    lon = loc['coords']['longitude']
    # دروستکردنی لینکی ڕاستەقینەی گوگڵ ماپ
    gps_link = f"https://www.google.com/maps?q={lat},{lon}"
    st.success(L['gps_success'])

# --- هەموو گەڕەکەکانی کەرکوک ---
KIRKUK_AREAS = sorted([
    "ڕەحیماوا", "پەنجاعەلی", "شۆراو", "تەپە", "ئیمام قاسم", "ئازادی", "شۆڕش", 
    "ڕێگای بەغداد", "موسەڵا", "تسعین", "واسطی", "دۆمیز", "غرناطة", "حوزەیران", 
    "شیمال", "عرفە", "کوردستان", "دەروازە", "ناوەندی شار", "ڕووناكی", "ئەحمەد ئاغا",
    "ئیسکان", "قۆریە", "حەجیاوا", "برایەتی", "تەپەی مەلا عەبدوڵا", "بێستوون", 
    "شۆراو نوێ", "کۆمەڵگای نیشتەجێبوون", "سەربازی", "ئەڵماس", "بەرلێمان", "دەروازەی باکور",
    "کەنیسە", "حەی سەدام", "حەی مەنصور", "حەی ئەسرا و مەفقودین", "حەی بەعس",
    "حەی عەدەن", "پەنجای نوێ", "شۆراوی کۆن", "قادسیە ١", "قادسیە ٢", "فەیلەق", 
    "بڵاوەکان", "حەی حوسێن", "حەی ئەفسەران", "کۆمار", "شاتیلو", "تاریق", "حەی خەزرا", "ڕاپەڕین"
])

# --- ستایل ---
st.markdown(f"""
    <style>
    html, body, [data-testid="stAppViewContainer"] {{ direction: rtl; text-align: right; }}
    .brand-header {{ background: linear-gradient(135deg, #1a1a1a 0%, #333333 100%); padding: 20px; border-radius: 15px; border-bottom: 4px solid #D4AF37; text-align: center; margin-bottom: 15px; }}
    .brand-title {{ color: #D4AF37; font-size: 28px; font-weight: bold; }}
    .stForm {{ border: 1px solid #D4AF37 !important; border-radius: 15px; }}
    </style>
    """, unsafe_allow_html=True)

st.markdown(f'<div class="brand-header"><div class="brand-title">{L["title"]}</div><div style="color:white;">{L["subtitle"]}</div></div>', unsafe_allow_html=True)

with st.form("delivery_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        customer = st.text_input(L['customer_name'])
        shop_name = st.text_input(L['shop_name'])
        shop_address = st.text_input(L['shop_addr'])
    with col2:
        phone = st.text_input(L['phone'])
        selected_area = st.selectbox(L['area'], ["هەڵبژێرە..."] + KIRKUK_AREAS)
        full_address = st.text_input(L['full_addr'])
        final_location = st.text_input(L['location_label'], value=gps_link)
        price = st.number_input(L['price'], min_value=0, step=250)
    
    submit = st.form_submit_button(L['submit'])
    
    if submit:
        if not customer or not phone or "هەڵبژێرە" in selected_area:
            st.error(L['error'])
        else:
            msg = f"Golden Delivery ✨\n📦 داواکاری نوێ\n👤 کڕیار: {customer}\n🏘 گەڕەک: {selected_area}\n🏠 ناونیشان: {full_address}\n📍 نەخشە: {final_location}\n📞 مۆبایل: {phone}\n💰 نرخ: {price:,} IQD"
            link = f"https://wa.me/9647801352003?text={urllib.parse.quote(msg)}"
            st.success(L['success'])
            st.markdown(f'<a href="{link}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:12px; border-radius:10px; font-weight:bold; cursor:pointer;">{L["wa_btn"]}</button></a>', unsafe_allow_html=True)

st.markdown(f'<div style="text-align:center; padding:10px;">📞 0772 195 9922 | 0780 135 2003</div>', unsafe_allow_html=True)
