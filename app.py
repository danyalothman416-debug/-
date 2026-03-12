import streamlit as st
import pandas as pd
import os
import urllib.parse
from datetime import datetime

# --- 1. ڕێکخستنی لاپەڕە ---
st.set_page_config(page_title="Golden Delivery", layout="wide")

languages = {
    "کوردی 🇭🇺": {
        "dir": "rtl", "align": "right",
        "title": "GOLDEN DELIVERY ✨",
        "subtitle": "خێراترین و باوەڕپێکراوترین خزمەتگوزاری گەیاندن لە کەرکوک",
        "customer_name": "👤 ناوی کڕیار", 
        "shop_name": "🏪 ناوی دوکان", 
        "shop_addr": "📍 ناونیشانی دوکان",
        "phone": "📞 ژمارەی مۆبایل", 
        "area": "🏘 گەڕەکی کڕیار", 
        "full_addr": "🏠 وردەکاری ناونیشان (نزیک کوێیە؟)",
        "price": "💰 نرخ (د.ع)",
        "submit": "تۆمارکردنی داواکاری ✅", 
        "wa_btn": "ناردنی وەسڵ بۆ ئۆفیس 💬",
        "error": "⚠️ تکایە خانەکان پڕ بکەرەوە", 
        "success": "✅ بە سەرکەوتوویی تۆمارکرا",
        "admin_title": "🛠 پانێڵی بەڕێوەبەرایەتی", 
        "admin_pass": "پاسۆرد داخڵ بکە",
        "msg_delivered": "سڵاو، داواکارییەکەت گەیشت ✅\nسوپاس بۆ متمانەتان - Golden Delivery", 
        "msg_onway": "سڵاو، داواکارییەکەت لە ڕێگەیە و شۆفێرەکەمان بەڕێوەیە 🚚\nGolden Delivery",
        "app_guide": "📲 بۆ ئەوەی وەک ئەپڵیکەیشن بەکاری بهێنیت: کلیک لە سێ خاڵەکە بکە و 'Add to Home Screen' دابگرە."
    },
    "العربية 🇮🇶": {
        "dir": "rtl", "align": "right",
        "title": "گولدن دليفري ✨",
        "subtitle": "أسرع وخدمة توصيل موثوقة في كركوك",
        "customer_name": "👤 اسم الزبون", 
        "shop_name": "🏪 اسم المحل", 
        "shop_addr": "📍 عنوان المحل",
        "phone": "📞 رقم الموبايل", 
        "area": "🏘 منطقة الزبون", 
        "full_addr": "🏠 تفاصيل العنوان (قرب ماذا؟)",
        "price": "💰 السعر (د.ع)",
        "submit": "تسجيل الطلبية ✅", 
        "wa_btn": "إرسال البيانات للمكتب 💬",
        "error": "⚠️ يرجى ملء البيانات المطلوبة", 
        "success": "✅ تم التسجيل بنجاح",
        "admin_title": "🛠 لوحة التحكم", 
        "admin_pass": "أدخل كلمة المرور",
        "msg_delivered": "مرحباً، تم توصيل طلبيتك ✅\nشكراً لثقتكم - گولدن دليفري", 
        "msg_onway": "مرحباً، طلبيتك في الطريق والمندوب قادم إليك 🚚\nگولدن دليفري",
        "app_guide": "📲 لاستخدامه كتطبيق: اضغط على النقاط الثلاث واختر 'Add to Home Screen'."
    }
}

# --- ٢. زمان لە Sidebar ---
if "selected_lang" not in st.session_state:
    st.session_state.selected_lang = "کوردی 🇭🇺"

with st.sidebar:
    st.title("🌐 Language / زمان")
    lang_choice = st.radio("Choose Language", list(languages.keys()), index=list(languages.keys()).index(st.session_state.selected_lang))
    st.session_state.selected_lang = lang_choice

L = languages[st.session_state.selected_lang]

# --- ٣. لیستی گەڕەکەکان ---
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

# --- ٤. بارکردنی داتا ---
DB_FILE = "deliveries.csv"
def load_data():
    if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE, dtype={"phone": str})
    return pd.DataFrame(columns=["date", "customer", "shop", "phone", "area", "address", "price"])

# --- ٥. ستایلی لاپەڕە ---
st.markdown(f"""
    <style>
    html, body, [data-testid="stAppViewContainer"] {{ direction: {L['dir']}; text-align: {L['align']}; }}
    .brand-header {{ background: linear-gradient(135deg, #1a1a1a 0%, #333333 100%); padding: 30px; border-radius: 15px; border-bottom: 5px solid #D4AF37; text-align: center; margin-bottom: 25px; }}
    .brand-title {{ color: #D4AF37; font-size: 35px; font-weight: bold; text-shadow: 2px 2px 4px #000; }}
    .stForm {{ border: 2px solid #D4AF37 !important; border-radius: 15px; padding: 25px; background-color: #fcfcfc; }}
    .num-fix {{ direction: ltr !important; display: inline-block; }}
    .guide-box {{ background-color: #f1f3f5; border: 1px dashed #999; padding: 15px; border-radius: 10px; margin-top: 20px; text-align: center; color: #666; }}
    </style>
    """, unsafe_allow_html=True)

st.markdown(f'<div class="brand-header"><div class="brand-title">{L["title"]}</div><div style="color:white; font-size:18px;">{L["subtitle"]}</div></div>', unsafe_allow_html=True)

# --- ٦. فۆرمی کڕیار ---
with st.form("delivery_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        customer = st.text_input(L['customer_name'])
        shop = st.text_input(L['shop_name'])
    with col2:
        phone = st.text_input(L['phone'])
        selected_area = st.selectbox(L['area'], ["هەڵبژێرە..."] + KIRKUK_AREAS)
    
    col3, col4 = st.columns(2)
    with col3:
        price = st.number_input(L['price'], min_value=0, step=250)
    with col4:
        shop_addr = st.text_input(L['shop_addr'])
        
    full_addr = st.text_input(L['full_addr'])
    submit = st.form_submit_button(L['submit'])
    
    if submit:
        if not customer or not phone or "هەڵبژێرە" in selected_area:
            st.error(L['error'])
        else:
            df = load_data()
            new_row = pd.DataFrame([{"date": datetime.now().strftime("%Y-%m-%d"), "customer": customer, "shop": shop, "phone": phone, "area": selected_area, "address": full_addr, "price": price}])
            pd.concat([df, new_row]).to_csv(DB_FILE, index=False)
            
            msg_to_office = f"Golden Delivery ✨\n📦 داواکاری نوێ\n👤 کڕیار: {customer}\n🏪 دوکان: {shop}\n🏘 گەڕەک: {selected_area}\n🏠 ناونیشان: {full_addr}\n📞 مۆبایل: {phone}\n💰 نرخ: {price:,} IQD"
            link = f"https://wa.me/9647801352003?text={urllib.parse.quote(msg_to_office)}"
            st.success(L['success'])
            st.markdown(f'<a href="{link}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:15px; border-radius:10px; font-weight:bold; cursor:pointer; font-size:16px;">{L["wa_btn"]}</button></a>', unsafe_allow_html=True)

# --- ٧. پانێڵی ئەدمین ---
if st.query_params.get("role") == "boss":
    st.divider()
    st.subheader(L['admin_title'])
    
    pwd = st.text_input(L['admin_pass'], type="password")
    
    if pwd == "golden2024":
        data = load_data()
        if not data.empty:
            c1, c2 = st.columns(2)
            c1.metric("کۆی داواکارییەکان", len(data))
            c2.metric("کۆی پارەی کاڵاکان", f"{data['price'].sum():,} IQD")
            
            st.dataframe(data, use_container_width=True)
            
            st.write("--- 📩 ناردنی نامە بۆ کڕیارەکان ---")
            for i, row in data.iterrows():
                with st.expander(f"📦 {row['customer']} - {row['area']}"):
                    col_msg1, col_msg2 = st.columns(2)
                    
                    # پاککردنەوەی ژمارە بۆ واتسئەپ
                    raw_phone = str(row['phone']).strip()
                    if not raw_phone.startswith('964'):
                        if raw_phone.startswith('0'): raw_phone = '964' + raw_phone[1:]
                        else: raw_phone = '964' + raw_phone

                    with col_msg1:
                        m1 = urllib.parse.quote(L['msg_delivered'])
                        st.markdown(f'<a href="https://wa.me/{raw_phone}?text={m1}" target="_blank"><button style="width:100%; background:#4CAF50; color:white; border:none; padding:10px; border-radius:5px; cursor:pointer;">✅ نامەی گەیشت</button></a>', unsafe_allow_html=True)
                    
                    with col_msg2:
                        m2 = urllib.parse.quote(L['msg_onway'])
                        st.markdown(f'<a href="https://wa.me/{raw_phone}?text={m2}" target="_blank"><button style="width:100%; background:#FF9800; color:white; border:none; padding:10px; border-radius:5px; cursor:pointer;">🚚 نامەی لە ڕێگەیە</button></a>', unsafe_allow_html=True)
    elif pwd != "":
        st.error("❌ پاسۆردەکە هەڵەیە")

# --- ٨. فووتەر ---
st.markdown(f'<div class="guide-box">{L["app_guide"]}</div>', unsafe_allow_html=True)
st.markdown(f'<div style="text-align:center; padding:20px; font-weight:bold;">📞 <span class="num-fix">0780 135 2003</span> | <span class="num-fix">0772 195 9922</span></div>', unsafe_allow_html=True)
