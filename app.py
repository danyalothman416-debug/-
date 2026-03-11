import streamlit as st
import pandas as pd
import os
import urllib.parse
from streamlit_js_eval import streamlit_js_eval

# --- 1. ڕێکخستنی لاپەڕە و زمان ---
st.set_page_config(page_title="Golden Delivery", layout="wide")

languages = {
    "کوردی 🇭🇺": {
        "dir": "rtl", "align": "right",
        "title": "GOLDEN DELIVERY ✨",
        "subtitle": "خێراترین و باوەڕپێکراوترین خزمەتگوزاری گەیاندن لە کەرکوک",
        "get_gps_btn": "📍 کلیک لێرە بکە بۆ دۆزینەوەی شوێنەکەت",
        "gps_success": "✅ شوێنەکەت دیاریکرا",
        "customer_name": "👤 ناوی کڕیار", 
        "shop_name": "🏪 ناوی دوکان", 
        "shop_addr": "📍 ناونیشانی دوکان",
        "phone": "📞 ژمارەی مۆبایل", 
        "area": "🏘 گەڕەکی کڕیار", 
        "full_addr": "🏠 وردەکاری ناونیشان (نزیک کوێیە؟)",
        "price": "💰 نرخ (د.ع)",
        "submit": "تۆمارکردن و ناردنی وەسڵ ✅", 
        "wa_btn": "ناردنی زانیاری بۆ ئۆفیس 💬",
        "error": "⚠️ تکایە خانەکان پڕ بکەرەوە", 
        "success": "✅ بە سەرکەوتوویی تۆمارکرا",
        "admin_title": "🛠 پانێڵی بەڕێوەبەرایەتی", 
        "admin_pass": "پاسۆرد داخڵ بکە",
        "msg_delivered": "سڵاو، داواکارییەکەت گەیشت ✅", 
        "msg_onway": "سڵاو، داواکارییەکەت لە ڕێگەیە 🚚"
    },
    "العربية 🇮🇶": {
        "dir": "rtl", "align": "right",
        "title": "گولدن دليفري ✨",
        "subtitle": "أسرع وخدمة توصيل موثوقة في كركوك",
        "get_gps_btn": "📍 اضغط هنا لتحديد موقعك",
        "gps_success": "✅ تم تحديد موقعك",
        "customer_name": "👤 اسم الزبون", 
        "shop_name": "🏪 اسم المحل", 
        "shop_addr": "📍 عنوان المحل",
        "phone": "📞 رقم الموبايل", 
        "area": "🏘 منطقة الزبون", 
        "full_addr": "🏠 تفاصيل العنوان (قرب ماذا؟)",
        "price": "💰 السعر (د.ع)",
        "submit": "تسجيل وإرسال الوصل ✅", 
        "wa_btn": "إرسال البيانات للمكتب 💬",
        "error": "⚠️ يرجى ملء البيانات المطلوبة", 
        "success": "✅ تم التسجيل بنجاح",
        "admin_title": "🛠 لوحة التحكم", 
        "admin_pass": "أدخل كلمة المرور",
        "msg_delivered": "مرحباً، تم توصيل طلبيتك ✅", 
        "msg_onway": "مرحباً، طلبيتك في الطريق 🚚"
    },
    "English 🇬🇧": {
        "dir": "ltr", "align": "left",
        "title": "GOLDEN DELIVERY ✨",
        "subtitle": "Fastest and most reliable delivery service in Kirkuk",
        "get_gps_btn": "📍 Click here to get your location",
        "gps_success": "✅ Location captured",
        "customer_name": "👤 Customer Name", 
        "shop_name": "🏪 Shop Name", 
        "shop_addr": "📍 Shop Address",
        "phone": "📞 Phone Number", 
        "area": "🏘 Customer Area", 
        "full_addr": "🏠 Address Details",
        "price": "💰 Price (IQD)",
        "submit": "Register and Send ✅", 
        "wa_btn": "Send to Office 💬",
        "error": "⚠️ Please fill all fields", 
        "success": "✅ Successfully Registered",
        "admin_title": "🛠 Admin Panel", 
        "admin_pass": "Enter Password",
        "msg_delivered": "Hello, your order has arrived ✅", 
        "msg_onway": "Hello, your order is on the way 🚚"
    }
}

if "selected_lang" not in st.session_state:
    st.session_state.selected_lang = "کوردی 🇭🇺"

# هەڵبژاردنی زمان
col_ref, col_lang, col_space = st.columns([0.5, 1.5, 4])
with col_ref:
    if st.button("🔄"): st.rerun()
with col_lang:
    lang_choice = st.selectbox("🌐 Language", list(languages.keys()), index=list(languages.keys()).index(st.session_state.selected_lang))
    st.session_state.selected_lang = lang_choice

L = languages[st.session_state.selected_lang]

# --- ٢. هەموو گەڕەکەکانی کەرکوک (وەک خۆی) ---
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

# --- ٣. داتا ---
DB_FILE = "deliveries.csv"
def load_data():
    if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE, dtype={"phone": str})
    return pd.DataFrame(columns=["customer", "shop", "phone", "area", "address", "price", "location"])

# --- ٤. ستایل ---
st.markdown(f"""
    <style>
    html, body, [data-testid="stAppViewContainer"] {{ direction: {L['dir']}; text-align: {L['align']}; }}
    .brand-header {{ background: linear-gradient(135deg, #1a1a1a 0%, #333333 100%); padding: 20px; border-radius: 15px; border-bottom: 4px solid #D4AF37; text-align: center; margin-bottom: 15px; }}
    .brand-title {{ color: #D4AF37; font-size: 28px; font-weight: bold; }}
    .stForm {{ border: 1px solid #D4AF37 !important; border-radius: 15px; padding: 20px; }}
    .num-fix {{ direction: ltr !important; display: inline-block; }}
    .gps-box {{ background-color: #f0f2f6; padding: 15px; border-radius: 10px; border: 1px dashed #D4AF37; margin: 10px 0; }}
    </style>
    """, unsafe_allow_html=True)

st.markdown(f'<div class="brand-header"><div class="brand-title">{L["title"]}</div><div style="color:white;">{L["subtitle"]}</div></div>', unsafe_allow_html=True)

# --- ٥. بەشی GPS (لە دەرەوەی فۆرم بۆ ئەوەی کلیک بکات) ---
st.markdown(f'<div class="gps-box">', unsafe_allow_html=True)
loc = streamlit_js_eval(data_key='pos', func_name='getCurrentPosition', component_value=None)
gps_link = ""
if loc:
    lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
    gps_link = f"https://www.google.com/maps?q={lat},{lon}"
    st.success(L['gps_success'])
else:
    st.info(L['get_gps_btn'])
st.markdown('</div>', unsafe_allow_html=True)

# --- ٦. فۆرمی کڕیار ---
with st.form("delivery_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        customer = st.text_input(L['customer_name'])
        shop = st.text_input(L['shop_name'])
        shop_addr = st.text_input(L['shop_addr'])
    with col2:
        phone = st.text_input(L['phone'])
        selected_area = st.selectbox(L['area'], ["هەڵبژێرە..."] + KIRKUK_AREAS)
        price = st.number_input(L['price'], min_value=0, step=250)
    
    full_addr = st.text_input(L['full_addr'])
    
    submit = st.form_submit_button(L['submit'])
    
    if submit:
        if not customer or not phone or "هەڵبژێرە" in selected_area:
            st.error(L['error'])
        else:
            df = load_data()
            new_row = pd.DataFrame([{"customer": customer, "shop": shop, "phone": phone, "area": selected_area, "address": full_addr, "price": price, "location": gps_link}])
            pd.concat([df, new_row]).to_csv(DB_FILE, index=False)
            
            msg = f"Golden Delivery ✨\n📦 داواکاری نوێ\n👤 کڕیار: {customer}\n🏘 گەڕەک: {selected_area}\n📍 نەخشە: {gps_link}\n📞 مۆبایل: {phone}\n💰 نرخ: {price:,} IQD"
            link = f"https://wa.me/9647801352003?text={urllib.parse.quote(msg)}"
            st.success(L['success'])
            st.markdown(f'<a href="{link}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:12px; border-radius:10px; font-weight:bold; cursor:pointer;">{L["wa_btn"]}</button></a>', unsafe_allow_html=True)

# --- ٧. پانێڵی بەڕێوەبەر ---
if st.query_params.get("role") == "boss":
    st.divider()
    st.subheader(L['admin_title'])
    if st.text_input(L['admin_pass'], type="password") == "dr_danyal_2024":
        data = load_data()
        if not data.empty:
            st.dataframe(data, use_container_width=True)
            for i, row in data.iterrows():
                with st.expander(f"📦 {row['customer']} - {row['area']}"):
                    c_del, c_onw = st.columns(2)
                    with c_del:
                        m1 = urllib.parse.quote(f"سڵاو {row['customer']}\n{L['msg_delivered']}\nGolden Delivery ✨")
                        st.markdown(f'<a href="https://wa.me/{row["phone"]}?text={m1}" target="_blank"><button style="width:100%; background:#4CAF50; color:white; border:none; padding:8px; border-radius:5px; cursor:pointer;">✅ گەیشت</button></a>', unsafe_allow_html=True)
                    with c_onw:
                        m2 = urllib.parse.quote(f"سڵاو {row['customer']}\n{L['msg_onway']}\nGolden Delivery ✨")
                        st.markdown(f'<a href="https://wa.me/{row["phone"]}?text={m2}" target="_blank"><button style="width:100%; background:#FF9800; color:white; border:none; padding:8px; border-radius:5px; cursor:pointer;">🚚 لە ڕێگەیە</button></a>', unsafe_allow_html=True)

st.markdown(f'<div style="text-align:center; padding:10px;">📞 <span class="num-fix">0780 135 2003</span> | <span class="num-fix">0772 195 9922</span></div>', unsafe_allow_html=True)
