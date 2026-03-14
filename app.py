import streamlit as st
import pandas as pd
import os
import urllib.parse
from datetime import datetime

# --- 1. ڕێکخستنی لاپەڕە ---
st.set_page_config(page_title="Golden Delivery", layout="wide")

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
    }
}

# --- ٢. سایدبار: تەنها لێرە مەرجەکان دەردەکەون ---
with st.sidebar:
    # هەڵبژاردنی زمان و تێم
    lang_choice = st.selectbox("🌐 Language / زمان", list(languages.keys()))
    L = languages[lang_choice]
    theme_choice = st.radio(L['theme_label'], [L['light'], L['dark']], horizontal=True)
    
    st.markdown("---")
    st.markdown(f"<h2 style='color:#D4AF37; text-align:center;'>📜 مەرج و ڕێساکان</h2>", unsafe_allow_html=True)
    
    with st.expander("📦 پاراستنی کەلوپەل"):
        st.write("دوکان بەرپرسە لە پێچانەوەی توندوتۆڵ. شۆفێر بەرپرسە لە گەیاندنی بە ساغی بەبێ زیانی دەرەکی.")
    
    with st.expander("⏳ کاتەکانی گەیاندن"):
        st.write("گەیاندن ٢ بۆ ٦ کاتژمێر دەخایەنێت. داواکاری دوای ٤ی ئێوارە دەچێتە ڕۆژی دواتر.")
    
    with st.expander("💰 گەڕانەوە (مەرتووع)"):
        st.write("ئەگەر کڕیار بارەکەی وەرنەگرت، دوکان حەقی ڕێگای شۆفێر (٢,٠٠٠ دینار) دابین دەکات.")
        
    with st.expander("💵 تەسلیمکردنی پارە"):
        st.write("پارەی وەسڵەکان لە ماوەی ٢٤ بۆ ٤٨ کاتژمێردا تەسلیمی دوکان دەکرێتەوە.")
    
    st.markdown("---")
    st.caption("Golden Delivery - Kirkuk")

# ڕێکخستنی ڕەنگەکان
is_dark = theme_choice == L['dark']
bg_color = "#0e1117" if is_dark else "#f0f2f6"
text_color = "#fafafa" if is_dark else "#31333F"
card_bg = "#161b22" if is_dark else "#ffffff"

# --- ٣. ستایل ---
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{ 
        direction: {L['dir']}; 
        text-align: {L['align']};
        background-color: {bg_color};
    }}
    .brand-header {{ 
        background: linear-gradient(135deg, {"#1a1a1a" if is_dark else "#D4AF37"} 0%, {"#2d2d2d" if is_dark else "#f39c12"} 100%); 
        padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 25px; 
    }}
    .brand-title {{ color: {"#D4AF37" if is_dark else "white"}; font-size: 30px; font-weight: bold; }}
    .stForm {{ border: 2px solid #D4AF37 !important; border-radius: 15px; padding: 25px; background-color: {card_bg} !important; }}
    label {{ color: #D4AF37 !important; font-weight: bold !important; }}
    </style>
    """, unsafe_allow_html=True)

st.markdown(f'<div class="brand-header"><div class="brand-title">{L["title"]}</div><div style="color:{"#ccc" if is_dark else "white"};">{L["subtitle"]}</div></div>', unsafe_allow_html=True)

# --- ٤. لیستی گەڕەکەکان ---
AREAS_WITH_PRICES = {
    "کوردستان": 3000, "ڕەحیماوا": 3000, "ئیسکان": 3000, "ئازادی": 3000, "شۆراو": 3000,
    "ئەڵماس": 3000, "عرفە": 3000, "ڕێگای بەغداد": 4000, "تسعین": 4000, "واسطی": 4000,
    "دۆمیز": 4000, "پەنجاعەلی": 4000, "حوزەیران": 4000, "موسەڵا": 4000
}
display_areas = ["هەڵبژێرە..."] + [f"{area} - ({price:,} د.ع)" for area, price in AREAS_WITH_PRICES.items()]

# --- ٥. بارکردنی داتا ---
DB_FILE = "deliveries.csv"
def load_data():
    if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE, dtype={"phone": str})
    return pd.DataFrame(columns=["date", "customer", "shop", "phone", "area", "address", "shop_addr", "price", "status"])

# --- ٦. فۆرمی تۆمارکردن ---
with st.form("delivery_form", clear_on_submit=True):
    c1, c2 = st.columns(2)
    with c1:
        customer = st.text_input(L['customer_name'])
        shop = st.text_input(L['shop_name'])
        shop_addr = st.text_input(L['shop_addr'])
    with c2:
        phone = st.text_input(L['phone'], placeholder="07xx xxx xxxx")
        area_selection = st.selectbox(L['area'], display_areas)
        
        selected_price = 0
        pure_area_name = ""
        if area_selection != "هەڵبژێرە...":
            pure_area_name = area_selection.split(" - (")[0]
            selected_price = AREAS_WITH_PRICES.get(pure_area_name, 0)
        price = st.number_input(L['price'], min_value=0, step=250, value=selected_price)
    
    full_addr = st.text_input(L['full_addr'])
    submit = st.form_submit_button(L['submit'])
    
    if submit:
        if not customer or not phone or area_selection == "هەڵبژێرە...":
            st.error("⚠️ تکایە هەموو خانەکان پڕ بکەرەوە")
        else:
            df = load_data()
            new_row = pd.DataFrame([{"date": datetime.now().strftime("%Y-%m-%d"), "customer": customer, "shop": shop, "phone": phone, "area": pure_area_name, "address": full_addr, "shop_addr": shop_addr, "price": price, "status": L['status_pending']}])
            pd.concat([df, new_row]).to_csv(DB_FILE, index=False)
            st.success("✅ بەسەرکەوتوویی تۆمارکرا")
            msg = f"Golden Delivery ✨\n📦 NEW ORDER\n👤 Name: {customer}\n🏪 Shop: {shop}\n🏘 Area: {pure_area_name}\n💰 Price: {price:,} IQD"
            st.markdown(f'<a href="https://wa.me/9647801352003?text={urllib.parse.quote(msg)}" target="_blank"><button style="width:100%; background:#25D366; color:white; border:none; padding:15px; border-radius:10px; cursor:pointer; font-weight:bold;">{L["wa_btn"]}</button></a>', unsafe_allow_html=True)

# --- ٧. بەشی بەدواداچوون ---
st.markdown(f'<div style="background:{card_bg}; padding:20px; border-radius:15px; border:1px solid #D4AF37; margin-top:30px;"><h3>{L["track_title"]}</h3>', unsafe_allow_html=True)
track_phone = st.text_input(f"{L['phone']}", key="track_input")
if st.button(L['track_btn']):
    df_track = load_data()
    res = df_track[df_track['phone'] == track_phone].tail(1)
    if not res.empty:
        st.success(f"📍 {res.iloc[0]['customer']} | Status: **{res.iloc[0]['status']}**")
    else: st.warning("داواکارییەک بەم ژمارەیە نەدۆزرایەوە")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown(f'<div style="text-align:center; padding:20px; color:#666;">Golden Delivery System 2024</div>', unsafe_allow_html=True)
