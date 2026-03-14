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

# --- ٣. لیستی گەڕەکەکان و سیستەمی نرخی زیرەک ---
NEARBY_AREAS = [
    "کوردستان / كوردستان / Kurdistan", "ڕەحیماوا / رحيماوة / Rahimawa / Rahimava", 
    "ئیسکان / اسكان / Iskan", "ئازادی / ازادي / Azadi", "شۆراو / شوراو / Shoraw / Şorav",
    "ئەحمەد ئاغا / احمد آغا / Ahmed Agha", "ئەڵماس / الماس / Almas", "عرفە / عرفة / Arafa / Arife",
    "فەیلەق / فيلق / Faylaq / Feylak", "شیمال / شمال / Shimal / Şimal", "ڕووناكی / روناقي / Runaki",
    "برایەتی / برايتي / Brayati", "شۆڕش / شورش / Shorsh / Şuraş", "تەپە / تبة / Tapa / Tepe"
]

KIRKUK_AREAS = sorted([
    "ڕەحیماوا / رحيماوة / Rahimawa / Rahimava", "ئیسکان / اسكان / Iskan", "ئازادی / ازادي / Azadi",
    "ڕێگای بەغداد / طريق بغداد / Baghdad Road / Bağdat Yolu", "تسعین / تسعين / Taseen / Tisin",
    "واسطی / واسطي / Wasit / Vasit", "دۆمیز / دوميز / Domiz", "غرناطة / غرناطة / Gharnata",
    "حوزەیران / حزيران / Huzairan / Haziran", "پەنجاعەلی / بنجة علي / Panja Ali / Pençe Ali",
    "شۆراو / شوراو / Shoraw / Şorav", "تەپە / تبة / Tapa / Tepe", "ئیمام قاسم / امام قاسم / Imam Qasim",
    "شۆڕش / شورش / Shorsh / Şuraş", "موسەڵا / مصلى / Musalla", "شیمال / شمال / Shimal / Şimal",
    "عرفە / عرفة / Arafa / Arife", "کوردستان / كوردستان / Kurdistan", "دەروازە / دروازة / Darwaza / Dervaze",
    "ناوەندی شار / مركز المدينة / City Center / Şehir Merkezi", "ڕووناكی / روناقي / Runaki",
    "ئەحمەد ئاغا / احمد آغا / Ahmed Agha", "قۆریە / قورية / Qorya / Kurye", "حەجیاوا / حجياوة / Hajiawa / Hacıava",
    "برایەتی / برايتي / Brayati", "تەپەی مەلا عەبدوڵا / تبة ملا عبدالله / Tapa Mala Abdulla",
    "بێستوون / بيستون / Bestun", "شۆراو نوێ / شوراو الجديد / New Shoraw", "سەربازی / حي العسكري / Askari / Askeri",
    "ئەڵماس / الماس / Almas", "بەرلێمان / برليمان / Barleman", "دەروازەی باکور / بوابة الشمال / North Gate",
    "کەنیسە / كنيسة / Kanisa / Kilise", "حەی سەدام / حي صدام / Hai Saddam", "حەی مەنصور / حي المنصور / Mansour",
    "حەی ئەسرا و مەفقودین / الاسرى والمفقودين / Asra o Mafqudin", "حەی بەعس / حي البعث / Baath",
    "حەی عەدەن / حي عدن / Aden", "پەنجای نوێ / بنجة علي الجديد / New Panja Ali", "شۆراوی کۆن / شوراو القديم / Old Shoraw",
    "قادسیە ١ / قادسية ١ / Qadisiya 1", "قادسیە ٢ / قادسية ٢ / Qadisiya 2", "فەیلەق / فيلق / Faylaq / Feylak",
    "بڵاوەکان / حي البلديات / Baladiyat", "حەی حوسێن / حي الحسين / Hai Hussein", "حەی ئەفسەران / حي الضباط / Officers / Subaylar",
    "کۆمار / جمهوري / Jumhuri / Cumhuriyeti", "شاتیلو / شاتلو / Shatilu", "تاریق / طارق / Tariq",
    "حەی خەزرا / حي الخضراء / Khadra / Hazra", "ڕاپەڕین / رابرين / Raparin"
])

# --- ٤. بارکردنی داتا ---
DB_FILE = "deliveries.csv"
def load_data():
    if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE, dtype={"phone": str})
    return pd.DataFrame(columns=["date", "customer", "shop", "phone", "area", "address", "shop_addr", "price", "status"])

# --- ٥. ستایلی داینامیکی ڕووکار و لابردنی لۆگۆی Streamlit ---
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
    
    [data-testid="stNumberInput"] input, 
    [data-testid="stTextInput"] input {{
        direction: ltr !important;
        text-align: left !important;
    }}
    
    .brand-header {{ 
        background: linear-gradient(135deg, {"#1a1a1a" if is_dark else "#D4AF37"} 0%, {"#2d2d2d" if is_dark else "#f39c12"} 100%); 
        padding: 30px; 
        border-radius: 15px; 
        border-bottom: 5px solid #D4AF37; 
        text-align: center; 
        margin-bottom: 25px; 
    }}
    
    .brand-title {{ color: {"#D4AF37" if is_dark else "white"}; font-size: 35px; font-weight: bold; }}
    
    .stForm {{ 
        border: 2px solid #D4AF37 !important; 
        border-radius: 15px; 
        padding: 25px; 
        background-color: {card_bg} !important;
    }}
    
    .track-section {{ 
        background: {card_bg}; 
        padding: 20px; 
        border-radius: 15px; 
        border: 1px solid #D4AF37; 
        margin-top: 30px; 
    }}

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
        # بەکارهێنانی selectbox بۆ گەڕەک
        selected_area = st.selectbox(L['area'], ["هەڵبژێرە..."] + KIRKUK_AREAS)
        
        # دیاریکردنی نرخ بەپێی گەڕەک (Smart Pricing)
        default_price = 0
        if selected_area in NEARBY_AREAS:
            default_price = 3000
        elif selected_area != "هەڵبژێرە...":
            default_price = 4000
            
        price = st.number_input(L['price'], min_value=0, step=250, value=default_price)
    
    full_addr = st.text_input(L['full_addr'])
    submit = st.form_submit_button(L['submit'])
    
    if submit:
        if not customer or not phone or "هەڵبژێرە" in selected_area:
            st.error("⚠️ تکایە هەموو خانەکان پڕ بکەرەوە")
        else:
            df = load_data()
            new_row = pd.DataFrame([{"date": datetime.now().strftime("%Y-%m-%d"), "customer": customer, "shop": shop, "phone": phone, "area": selected_area, "address": full_addr, "shop_addr": shop_addr, "price": price, "status": L['status_pending']}])
            pd.concat([df, new_row]).to_csv(DB_FILE, index=False)
            st.success("✅ بەسەرکەوتوویی تۆمارکرا")
            msg = f"Golden Delivery ✨\n📦 NEW ORDER\n👤 Name: {customer}\n🏪 Shop: {shop}\n🏘 Area: {selected_area}\n💰 Price: {price:,} IQD"
            st.markdown(f'<a href="https://wa.me/9647801352003?text={urllib.parse.quote(msg)}" target="_blank"><button style="width:100%; background:#25D366; color:white; border:none; padding:15px; border-radius:10px; cursor:pointer; font-weight:bold;">{L["wa_btn"]}</button></a>', unsafe_allow_html=True)

# --- ٧. بەشی بەدواداچوون ---
st.markdown(f'<div class="track-section"><h3>{L["track_title"]}</h3>', unsafe_allow_html=True)
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
        for i, row in data.iterrows():
            with st.expander(f"📦 {row['customer']}"):
                ns = st.selectbox("Status", [L['status_pending'], L['status_onway'], L['status_delivered']], key=f"s_{i}")
                if st.button("Update", key=f"b_{i}"):
                    data.at[i, 'status'] = ns
                    data.to_csv(DB_FILE, index=False)
                    st.rerun()

# --- ٩. فووتەر و ڤێرژن ---
st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown(f'<div style="text-align:center; padding:10px; color:#D4AF37;">📞 <span style="direction:ltr; display:inline-block;">0780 135 2003</span> | <span style="direction:ltr; display:inline-block;">0772 195 9922</span></div>', unsafe_allow_html=True)
st.markdown('<div style="text-align:center; color:#666; font-size:12px; padding-bottom:20px;">Golden Delivery System - Version 1.2.0 Build 2024</div>', unsafe_allow_html=True)
