import streamlit as st
import pandas as pd
import os
import urllib.parse
from datetime import datetime
import plotly.express as px
import folium
from streamlit_folium import st_folium

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
    "Türkmençe 🇮🇶": {
        "dir": "ltr", "align": "left", "theme_label": "Tema", "light": "Açık ☀️", "dark": "Karanlık 🌙",
        "title": "GOLDEN DELIVERY ✨",
        "subtitle": "Kerkük'te en hızlı teslimat hizmeti",
        "customer_name": "👤 Müşteri Adı", 
        "shop_name": "🏪 Mağaza Adı", 
        "shop_addr": "📍 Mağaza Adresi",
        "phone": "📞 Telefon Numarası", 
        "area": "🏘 Bölge / Semt", 
        "full_addr": "🏠 Adres Detayı (Nereye yakın?)",
        "price": "💰 Fiyat (IQD)",
        "submit": "Siparişi Kaydet ✅", 
        "wa_btn": "Ofise Gönder 💬",
        "track_title": "🔍 Sipariş Takibi",
        "track_btn": "Ara",
        "admin_title": "🛠 Yönetici Paneli",
        "admin_pass": "Şifre",
        "status_pending": "⏳ Beklemede", "status_onway": "🚚 Yolda", "status_delivered": "✅ Teslim Edildi"
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

is_dark = theme_choice == L['dark']
bg_color = "#0e1117" if is_dark else "#f0f2f6"
text_color = "#fafafa" if is_dark else "#31333F"
card_bg = "#161b22" if is_dark else "#ffffff"

# پۆتانی وردی گەڕەکەکان
AREA_COORDS = {
    "ڕەحیماوا / رحيماوة / Rahimawa": [35.4950, 44.3910],
    "ئیسکان / اسكان / Iskan": [35.4820, 44.3980],
    "ئازادی / ازادي / Azadi": [35.4750, 44.4050],
    "ڕێگای بەغداد / طريق بغداد / Baghdad Road": [35.4520, 44.3680],
    "تسعین / تسعين / Taseen": [35.4510, 44.3750],
    "واسطی / واسطي / Wasit": [35.4180, 44.3620],
    "کوردستان / كوردستان / Kurdistan": [35.5050, 44.4010],
    "موسەڵا / مصلى / Musalla": [35.4650, 44.3950],
    "عرفە / عرفة / Arafa": [35.4880, 44.3550],
    "دۆمیز / دوميز / Domiz": [35.4250, 44.3850],
    "حوزەیران / حزيران / Huzairan": [35.4150, 44.3750],
    "پەنجاعەلی / بنجة علي / Panja Ali": [35.4650, 44.4350]
}

NEARBY_AREAS = ["کوردستان / كوردستان / Kurdistan", "ڕەحیماوا / رحيماوة / Rahimawa", "ئیسکان / اسكان / Iskan", "ئازادی / ازادي / Azadi"]
KIRKUK_AREAS = sorted(list(AREA_COORDS.keys()))

# --- ٣. بارکردنی داتا ---
DB_FILE = "deliveries.csv"
def load_data():
    if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE, dtype={"phone": str})
    return pd.DataFrame(columns=["date", "customer", "shop", "phone", "area", "address", "shop_addr", "price", "status"])

# --- ٤. ستایل ---
st.markdown(f"""
    <style>
    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}} header {{visibility: hidden;}}
    html, body, [data-testid="stAppViewContainer"] {{ 
        direction: {L['dir']}; text-align: {L['align']};
        background-color: {bg_color}; color: {text_color};
    }}
    .brand-header {{ 
        background: linear-gradient(135deg, {"#1a1a1a" if is_dark else "#D4AF37"} 0%, {"#2d2d2d" if is_dark else "#f39c12"} 100%); 
        padding: 30px; border-radius: 15px; border-bottom: 5px solid #D4AF37; text-align: center; margin-bottom: 25px; 
    }}
    .brand-title {{ color: {"#D4AF37" if is_dark else "white"}; font-size: 35px; font-weight: bold; }}
    .stForm {{ border: 2px solid #D4AF37 !important; border-radius: 15px; padding: 25px; background-color: {card_bg} !important; }}
    label {{ color: #D4AF37 !important; font-weight: bold !important; }}
    </style>
    """, unsafe_allow_html=True)

st.markdown(f'<div class="brand-header"><div class="brand-title">{L["title"]}</div><div style="color:{"#e0e0e0" if is_dark else "white"};">{L["subtitle"]}</div></div>', unsafe_allow_html=True)

# --- ٥. فۆرمی تۆمارکردن ---
if "submitted" not in st.session_state:
    st.session_state.submitted = False

with st.form("delivery_form", clear_on_submit=True):
    c1, c2 = st.columns(2)
    with c1:
        customer = st.text_input(L['customer_name'])
        shop = st.text_input(L['shop_name'])
        shop_addr = st.text_input(L['shop_addr'])
    with c2:
        phone = st.text_input(L['phone'], placeholder="07xx xxx xxxx")
        selected_area = st.selectbox(L['area'], ["Select..."] + KIRKUK_AREAS)
        default_price = 3000 if selected_area in NEARBY_AREAS else 4000 if selected_area != "Select..." else 0
        price = st.number_input(L['price'], min_value=0, step=250, value=default_price)
    
    full_addr = st.text_input(L['full_addr'])
    submit = st.form_submit_button(L['submit'])
    
    if submit:
        if not customer or not phone or "Select" in selected_area:
            st.error("⚠️ Please fill all fields")
        else:
            df = load_data()
            new_row = pd.DataFrame([{"date": datetime.now().strftime("%Y-%m-%d"), "customer": customer, "shop": shop, "phone": phone, "area": selected_area, "address": full_addr, "shop_addr": shop_addr, "price": price, "status": L['status_pending']}])
            pd.concat([df, new_row]).to_csv(DB_FILE, index=False)
            st.session_state.submitted = True
            st.session_state.last_order = {"name": customer, "area": selected_area}
            st.success("✅ Registered Successfully")

# --- ٦. بەشی بەدواداچوون ---
st.markdown(f'<div style="background:{card_bg}; padding:20px; border-radius:15px; border:1px solid #D4AF37; margin-top:30px;"><h3>{L["track_title"]}</h3>', unsafe_allow_html=True)
track_phone = st.text_input(f"{L['phone']}", key="track_input")
if st.button(L['track_btn']):
    df_track = load_data()
    res = df_track[df_track['phone'] == track_phone].tail(1)
    if not res.empty: st.success(f"📍 {res.iloc[0]['customer']} | Status: **{res.iloc[0]['status']}**")
    else: st.warning("No order found")
st.markdown('</div>', unsafe_allow_html=True)

# --- ٧. پانێڵی ئەدمین ---
if st.query_params.get("role") == "boss":
    st.divider()
    if st.text_input(L['admin_pass'], type="password") == "golden2024":
        data = load_data()
        st.dataframe(data, use_container_width=True)

# --- ٨. بارەکەی خوارەوە (NavBar) بە شێوەیەکی سادە ---
st.markdown("""<style>
    .nav-wrapper { position: fixed; bottom: 0; left: 0; width: 100%; background: white; border-top: 1px solid #ddd; z-index: 999; display: flex; justify-content: space-around; padding: 10px 0; }
    .nav-item { text-align: center; color: #333; text-decoration: none; font-size: 14px; flex: 1; cursor: pointer; }
</style>""", unsafe_allow_html=True)

# لێرەدا بە HTML دروستمان کردووە بۆ ئەوەی تێک نەچێت
# بۆ ئەوەی کلیک بکرێت، دەتوانی لینک (a tag) بەکاربهێنیت
nav_html = f"""
<div class="nav-wrapper">
    <a href="?page=profile" class="nav-item">👤<br>بایەکانم</a>
    <a href="?page=offers" class="nav-item">🏷️<br>داشکاندن</a>
    <a href="?page=home" class="nav-item" style="color:#D4AF37;">🏠<br>سەرەکی</a>
</div>
"""
st.markdown(nav_html, unsafe_allow_html=True)

# پشکنینی ئەوەی کلیک لە کامە کراوە (ئەگەر ویستت لاپەڕە بگۆڕیت)
page = st.query_params.get("page", "home")
if page == "offers":
    st.toast("بۆنە و داشکاندنەکان بەم زووانە...")
elif page == "profile":
    st.toast("هەژماری من...")

st.markdown("<br><br><br><br>", unsafe_allow_html=True) # بۆ ئەوەی ناوەڕۆک نەچێتە ژێر بارەکە
