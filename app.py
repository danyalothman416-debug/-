import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px
import folium
from streamlit_folium import st_folium

# --- 1. ڕێکخستنی لاپەڕە ---
st.set_page_config(page_title="Golden Delivery", layout="wide", page_icon="✨")

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
        "status_pending": "قيد الانتظار ⏳", "status_onway": "في الطريق 🚚", "status_delivered": "تم التوصيل ✅"
    }
}

# --- ٢. لیستی گەڕەکەکان ---
AREA_COORDS = {
    "ئیسکان / اسكان": [35.4820, 44.3980],
    "ڕەحیماوا / رحيماوة": [35.4950, 44.3910],
    "ئازادی / ازادي": [35.4750, 44.4050],
    "قۆریە / قورية": [35.4670, 44.3880],
    "شۆرجە / شورجة": [35.4780, 44.4150],
    "موسەڵا / مصلى": [35.4650, 44.3950],
    "ئیمام قاسم / امام قاسم": [35.4850, 44.4080],
    "تسعین / تسعين": [35.4510, 44.3750],
    "ڕێگای بەغداد / طريق بغداد": [35.4520, 44.3680],
    "واسطی / واسطي": [35.4180, 44.3620],
    "دۆمیز / دوميز": [35.4250, 44.3850],
    "حوزەیران / حزيران": [35.4150, 44.3750],
    "کوردستان / كوردستان": [35.5050, 44.4010],
    "پەنجاعەلی / بنجة علي": [35.4650, 44.4350],
}
NEARBY_AREAS = ["ئیسکان / اسكان", "ڕەحیماوا / رحيماوة", "ئازادی / ازادي", "قۆریە / قورية", "شۆرجە / شورجة"]
KIRKUK_AREAS = sorted(list(AREA_COORDS.keys()))

# --- ٣. زمان و ڕووکار ---
col_lang, col_theme = st.columns(2)
with col_lang:
    lang_choice = st.selectbox("🌐 Language", list(languages.keys()))
    L = languages[lang_choice]
with col_theme:
    theme_choice = st.radio(L['theme_label'], [L['light'], L['dark']], horizontal=True)

is_dark = theme_choice == L['dark']
bg_color = "#0e1117" if is_dark else "#f0f2f6"
card_bg = "#161b22" if is_dark else "#ffffff"

# --- ٤. بارکردنی داتا ---
DB_FILE = "deliveries.csv"
def load_data():
    if os.path.exists(DB_FILE): 
        return pd.read_csv(DB_FILE, dtype={"phone": str})
    return pd.DataFrame(columns=["date", "customer", "shop", "phone", "area", "address", "shop_addr", "price", "status"])

# --- ٥. ستایلی CSS ---
st.markdown(f"""
    <style>
    html, body, [data-testid="stAppViewContainer"] {{ 
        direction: {L['dir']}; text-align: {L['align']};
        background-color: {bg_color};
    }}
    .brand-header {{ 
        background: linear-gradient(135deg, #1a1a1a 0%, #D4AF37 100%); 
        padding: 25px; border-radius: 15px; text-align: center; margin-bottom: 20px; color: white;
    }}
    .invoice-box {{
        border: 2px solid #D4AF37; padding: 20px; border-radius: 15px; background-color: white; 
        color: #333; direction: rtl; font-family: 'Tahoma'; margin-top: 20px;
    }}
    </style>
    """, unsafe_allow_html=True)

st.markdown(f'<div class="brand-header"><h1>{L["title"]}</h1><p>{L["subtitle"]}</p></div>', unsafe_allow_html=True)

# --- ٦. فۆرم و لۆژیکی تۆمارکردن ---
if 'submitted_data' not in st.session_state:
    st.session_state.submitted_data = None

with st.form("delivery_form"):
    c1, c2 = st.columns(2)
    with c1:
        customer = st.text_input(L['customer_name'])
        shop = st.text_input(L['shop_name'])
    with c2:
        phone = st.text_input(L['phone'])
        selected_area = st.selectbox(L['area'], ["هەڵبژێرە..."] + KIRKUK_AREAS)
        
    price_val = 3000 if selected_area in NEARBY_AREAS else 4000
    price = st.number_input(L['price'], value=price_val)
    full_addr = st.text_input(L['full_addr'])
    
    submit_btn = st.form_submit_button(L['submit'])

    if submit_btn:
        if not customer or not phone or "هەڵبژێرە" in selected_area:
            st.error("⚠️ تکایە زانیارییەکان تەواو بکە")
        else:
            df = load_data()
            new_data = {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"), 
                "customer": customer, "shop": shop, "phone": phone, 
                "area": selected_area, "address": full_addr, "price": price, "status": L['status_pending']
            }
            pd.concat([df, pd.DataFrame([new_data])], ignore_index=True).to_csv(DB_FILE, index=False)
            st.session_state.submitted_data = new_data
            st.success("✅ بەسەرکەوتوویی تۆمارکرا")

# --- ٧. پیشاندانی وەسڵ (ئەگەر تۆمارکرابوو) ---
if st.session_state.submitted_data:
    sd = st.session_state.submitted_data
    st.markdown(f"""
    <div class="invoice-box">
        <h2 style="text-align:center; color:#D4AF37;">وەسڵی گەیاندن ✨</h2>
        <hr>
        <p><b>👤 کڕیار:</b> {sd['customer']}</p>
        <p><b>📞 مۆبایل:</b> {sd['phone']}</p>
        <p><b>🏘 گەڕەک:</b> {sd['area']}</p>
        <p><b>🏪 لەلایەن:</b> {sd['shop']}</p>
        <h3 style="background:#f9f9f9; padding:10px; border-right:5px solid #D4AF37;">💰 بڕی پارە: {sd['price']:,} د.ع</h3>
        <p style="text-align:center; font-size:12px; color:gray;">📸 سکرین شۆتی ئەم وەسڵە بۆ کڕیار بنێرە</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("تۆمارکردنی داواکارییەکی نوێ ➕"):
        st.session_state.submitted_data = None
        st.rerun()

# --- ٨. بەدواداچوون و پانێڵی ئەدمین ---
st.divider()
tab1, tab2 = st.tabs([L['track_title'], L['admin_title']])

with tab1:
    track_input = st.text_input("ژمارەی مۆبایل بنووسە")
    if st.button(L['track_btn']):
        df = load_data()
        res = df[df['phone'] == track_input].tail(1)
        if not res.empty: st.info(f"بارودۆخ: {res.iloc[0]['status']}")
        else: st.warning("نەدۆزرایەوە")

with tab2:
    if st.text_input(L['admin_pass'], type="password") == "golden2024":
        data = load_data()
        st.write("### 🗺️ نەخشەی کارەکان")
        m = folium.Map(location=[35.4687, 44.3925], zoom_start=12)
        for _, row in data.iterrows():
            if row['area'] in AREA_COORDS:
                lat, lon = AREA_COORDS[row['area']]
                g_nav = f"https://www.google.com/maps?q={lat},{lon}"
                popup_c = f"<b>{row['customer']}</b><br><a href='{g_nav}' target='_blank'>🚗 GPS</a>"
                folium.Marker([lat, lon], popup=popup_c).add_to(m)
        st_folium(m, width="100%", height=400)
        st.dataframe(data)
