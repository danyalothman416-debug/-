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
    lang_choice = st.selectbox("🌐 Language / زمان", list(languages.keys()))
    L = languages[lang_choice]
with col_theme:
    theme_choice = st.radio(L['theme_label'], [L['light'], L['dark']], horizontal=True)

is_dark = theme_choice == L['dark']
bg_color = "#0e1117" if is_dark else "#f0f2f6"
text_color = "#fafafa" if is_dark else "#31333F"
card_bg = "#161b22" if is_dark else "#ffffff"

# --- ٣. لیستی گەڕەکەکان و نرخەکان ---
# لێرەدا ناوی گەڕەکەکان و نرخەکانیان دیاری کراوە
AREAS_WITH_PRICES = {
    "کوردستان / كوردستان / Kurdistan": 3000,
    "ڕەحیماوا / رحيماوة / Rahimawa / Rahimava": 3000,
    "ئیسکان / اسكان / Iskan": 3000,
    "ئازادی / ازادي / Azadi": 3000,
    "شۆراو / شوراو / Shoraw / Şorav": 3000,
    "ئەحمەد ئاغا / احمد آغا / Ahmed Agha": 3000,
    "ئەڵماس / الماس / Almas": 3000,
    "عرفە / عرفة / Arafa / Arife": 3000,
    "فەیلەق / فيلق / Faylaq / Feylak": 3000,
    "شیمال / شمال / Shimal / Şimal": 3000,
    "ڕووناكی / روناقي / Runaki": 3000,
    "برایەتی / برايتي / Brayati": 3000,
    "شۆڕش / شورش / Shorsh / Şuraş": 3000,
    "تەپە / تبة / Tapa / Tepe": 3000,
    "ڕێگای بەغداد / طريق بغداد / Baghdad Road": 4000,
    "تسعین / تسعين / Taseen / Tisin": 4000,
    "واسطی / واسطي / Wasit / Vasit": 4000,
    "دۆمیز / دوميز / Domiz": 4000,
    "غرناطة / غرناطة / Gharnata": 4000,
    "حوزەیران / حزيران / Huzairan": 4000,
    "پەنجاعەلی / بنجة علي / Panja Ali": 4000,
    "ئیمام قاسم / امام قاسم / Imam Qasim": 4000,
    "موسەڵا / مصلى / Musalla": 4000,
    "دەروازە / دروازة / Darwaza / Dervaze": 4000,
    "ناوەندی شار / مركز المدينة / City Center": 4000,
    "قۆریە / قورية / Qorya / Kurye": 4000,
    "حەجیاوا / حجياوة / Hajiawa": 4000,
    "تەپەی مەلا عەبدوڵا / تبة ملا عبدالله": 4000,
    "بێستوون / بيستون / Bestun": 4000,
    "شۆراو نوێ / شوراو الجديد / New Shoraw": 4000,
    "سەربازی / حي العسكري / Askari": 4000,
    "بەرلێمان / برليمان / Barleman": 4000,
    "دەروازەی باکور / بوابة الشمال / North Gate": 4000,
    "کەنیسە / كنيسة / Kanisa / Kilise": 4000,
    "حەی سەدام / حي صدام / Hai Saddam": 4000,
    "حەی مەنصور / حي المنصور / Mansour": 4000,
    "حەی ئەسرا و مەفقودین / الاسرى والمفقودين": 4000,
    "حەی بەعس / حي البعث / Baath": 4000,
    "حەی عەدەن / حي عدن / Aden": 4000,
    "پەنجای نوێ / بنجة علي الجديد": 4000,
    "شۆراوی کۆن / شوراو القديم / Old Shoraw": 4000,
    "قادسیە ١ / قادسية ١ / Qadisiya 1": 4000,
    "قادسیە ٢ / قادسية ٢ / Qadisiya 2": 4000,
    "بڵاوەکان / حي البلديات / Baladiyat": 4000,
    "حەی حوسێن / حي الحسين / Hai Hussein": 4000,
    "حەی ئەفسەران / حي الضباط / Officers": 4000,
    "کۆمار / جمهوري / Jumhuri": 4000,
    "شاتیلو / شاتلو / Shatilu": 4000,
    "تاریق / طارق / Tariq": 4000,
    "حەی خەزرا / حي الخضراء / Khadra": 4000,
    "ڕاپەڕین / رابرين / Raparin": 4000
}

# دروستکردنی لیستی گەڕەکەکان بۆ ناو Selectbox بە پیشاندانی نرخ
display_areas = ["هەڵبژێرە..."] + [f"{area} - ({price:,} د.ع)" for area, price in AREAS_WITH_PRICES.items()]

# --- ٤. بارکردنی داتا ---
DB_FILE = "deliveries.csv"
def load_data():
    if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE, dtype={"phone": str})
    return pd.DataFrame(columns=["date", "customer", "shop", "phone", "area", "address", "shop_addr", "price", "status"])

# --- ٥. ستایل ---
st.markdown(f"""
    <style>
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    html, body, [data-testid="stAppViewContainer"] {{ 
        direction: {L['dir']}; 
        text-align: {L['align']};
        background-color: {bg_color};
        color: {text_color};
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

# --- ٦. فۆرمی تۆمارکردن ---
with st.form("delivery_form", clear_on_submit=True):
    c1, c2 = st.columns(2)
    with c1:
        customer = st.text_input(L['customer_name'])
        shop = st.text_input(L['shop_name'])
        shop_addr = st.text_input(L['shop_addr'])
    with c2:
        phone = st.text_input(L['phone'], placeholder="07xx xxx xxxx")
        # هەڵبژاردنی گەڕەک
        area_selection = st.selectbox(L['area'], display_areas)
        
        # دۆزینەوەی نرخەکە لە لیستەکە
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

# --- ٨. پانێڵی ئەدمین ---
if st.query_params.get("role") == "boss":
    st.divider()
    if st.text_input(L['admin_pass'], type="password") == "golden2024":
        data = load_data()
        st.dataframe(data, use_container_width=True)

st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown(f'<div style="text-align:center; padding:10px; color:#D4AF37;">📞 0780 135 2003 | 0772 195 9922</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align:center; color:#666; font-size:12px; padding-bottom:20px;">Golden Delivery System - Version 1.3.0 Build 2024</div>', unsafe_allow_html=True)
