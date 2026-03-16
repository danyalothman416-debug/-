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
        "status_pending": "⏳ چاوەڕوان", "status_onway": "🚚 لە ڕێگەیە", "status_delivered": "✅ گەیشت",
        "nav_home": "سەرەکی", "nav_discount": "داشکاندن", "nav_profile": "بایەکانم"
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
        "status_pending": "⏳ Beklemede", "status_onway": "🚚 Yolda", "status_delivered": "✅ Teslim Edildi",
        "nav_home": "Ana Sayfa", "nav_discount": "İndirimler", "nav_profile": "Profilim"
    },
    "العربية 🇮🇶": {
        "dir": "rtl", "align": "right", "theme_label": "المظهر", "light": "فاتح ☀️", "dark": "داكن 🌙",
        "title": "گولدن دليفري ✨",
        "subtitle": "أسرع خدمة توصيل في كركوك",
        "customer_name": "👤 اسم الزبون", 
        "shop_name": "🏪 اسم المحل", 
        "shop_addr": "📍 عنوان المحل",
        "phone": "📞 رقم الموبايل", 
        "area": "منطقة الزبون", 
        "full_addr": "🏠 تفاصيل العنوان (قرب ماذا؟)",
        "price": "💰 السعر (د.ع)",
        "submit": "تسجيل الطلبية ✅", 
        "wa_btn": "إرسال للمكتب 💬",
        "track_title": "🔍 تتبع طلبيتك",
        "track_btn": "بحث",
        "admin_title": "🛠 لوحة التحكم",
        "admin_pass": "كلمة المرور",
        "status_pending": "⏳ قيد الانتظار", "status_onway": "🚚 في الطريق", "status_delivered": "✅ تم التوصيل",
        "nav_home": "الرئيسية", "nav_discount": "خصومات", "nav_profile": "بلي الخاصة بي"
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
        "status_pending": "⏳ Pending", "status_onway": "🚚 On the way", "status_delivered": "✅ Delivered",
        "nav_home": "Home", "nav_discount": "Offers", "nav_profile": "My Profile"
    }
}

# --- ٢. دەستپێکردنی باری لاپەڕە ---
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Home"

# --- ٣. هەڵبژاردنی زمان و ڕووکار ---
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

# --- ٤. ستایلی Navbar و لاپەڕە ---
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
    
    /* Navbar Container */
    .stHorizontalBlock {{
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: {card_bg};
        z-index: 9999;
        border-top: 1px solid #D4AF37;
        padding: 5px 0px;
    }}
    
    /* شاردنەوەی دوگمە ئەسڵییەکان و جوانکردنیان */
    div[data-testid="stColumn"] > div > button {{
        background-color: transparent !important;
        border: none !important;
        color: {text_color} !important;
        width: 100%;
        height: 60px;
    }}
    div[data-testid="stColumn"] > div > button:hover {{
        color: #D4AF37 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- ٥. دروستکردنی Navbar لە خوارەوە ---
# ئەم بەشە دوگمەی ڕاستەقینەیە بەڵام وەک Navbar دەردەکەوێت
nav_cols = st.columns(3)
with nav_cols[0]:
    if st.button(f"👤\n{L['nav_profile']}"):
        st.session_state.active_tab = "Profile"
with nav_cols[1]:
    if st.button(f"🏷️\n{L['nav_discount']}"):
        st.session_state.active_tab = "Offers"
with nav_cols[2]:
    if st.button(f"🏠\n{L['nav_home']}"):
        st.session_state.active_tab = "Home"

# --- ٦. لۆژیکی گۆڕینی ناوەڕۆک ---

if st.session_state.active_tab == "Home":
    st.markdown(f'<div class="brand-header"><div class="brand-title">{L["title"]}</div><div style="color:{"#e0e0e0" if is_dark else "white"};">{L["subtitle"]}</div></div>', unsafe_allow_html=True)
    
    # ئێرە هەمان فۆرم و کۆدەکەی پێشووی خۆتە
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

    DB_FILE = "deliveries.csv"
    def load_data():
        if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE, dtype={"phone": str})
        return pd.DataFrame(columns=["date", "customer", "shop", "phone", "area", "address", "shop_addr", "price", "status"])

    if "submitted" not in st.session_state: st.session_state.submitted = False

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
            if not customer or not phone or "Select" in selected_area: st.error("⚠️ Please fill all fields")
            else:
                df = load_data()
                new_row = pd.DataFrame([{"date": datetime.now().strftime("%Y-%m-%d"), "customer": customer, "shop": shop, "phone": phone, "area": selected_area, "address": full_addr, "shop_addr": shop_addr, "price": price, "status": L['status_pending']}])
                pd.concat([df, new_row]).to_csv(DB_FILE, index=False)
                st.session_state.submitted = True
                st.session_state.last_order = {"name": customer, "area": selected_area}
                st.success("✅ Registered Successfully")

    if st.session_state.submitted:
        msg = f"Golden Delivery ✨\n📦 New Order\n👤 Name: {st.session_state.last_order['name']}\n🏘 Area: {st.session_state.last_order['area']}"
        wa_url = f"https://wa.me/9647801352003?text={urllib.parse.quote(msg)}"
        st.markdown(f'<a href="{wa_url}" target="_blank"><button style="width:100%; background:#25D366; color:white; border:none; padding:15px; border-radius:10px; cursor:pointer; font-weight:bold; margin-bottom:20px;">{L["wa_btn"]}</button></a>', unsafe_allow_html=True)

elif st.session_state.active_tab == "Offers":
    st.title(L['nav_discount'])
    st.info("🎁 لێرەدا داشکاندنەکان نیشان دەدرێن")
    st.balloons()

elif st.session_state.active_tab == "Profile":
    st.title(L['nav_profile'])
    st.write("👤 بەخێربێیت بۆ هەژماری تایبەتی خۆت")
    # دەتوانی لێرە لیستی داواکارییە کۆنەکانی کڕیار نیشان بدەیت

# --- ٧. فووتەر ---
st.markdown("<br><br><br><hr>", unsafe_allow_html=True)
st.markdown('<div style="text-align:center; color:#D4AF37; font-size:12px; margin-bottom: 80px;">Golden Delivery System v1.8.0</div>', unsafe_allow_html=True)
