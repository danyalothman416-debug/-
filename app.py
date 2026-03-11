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
        "get_gps": "📍 دیاریکردنی شوێنی کڕیار (GPS)",
        "gps_info": "تکایە کلیک لە 'Allow' یان 'ڕێپێدان' بکە بۆ وەرگرتنی شوێنەکە.",
        "gps_success": "✅ شوێنەکەت دیاریکرا!",
        "customer_name": "👤 ناوی کڕیار", "shop_name": "🏪 ناوی دوکان", "shop_addr": "📍 ناونیشانی دوکان",
        "phone": "📞 ژمارەی مۆبایل", "area": "🏘 گەڕەکی کڕیار", "full_addr": "🏠 وردەکاری ناونیشان",
        "location_label": "📍 لینکی نەخشە (خۆکار)", "price": "💰 نرخ (د.ع)",
        "submit": "تۆمارکردن و ناردنی وەسڵ ✅", "wa_btn": "ناردنی زانیاری بۆ ئۆفیس 💬",
        "error": "⚠️ تکایە خانەکان پڕ بکەرەوە", "success": "✅ بە سەرکەوتوویی تۆمارکرا",
        "admin_title": "🛠 پانێڵی بەڕێوەبەر", "admin_pass": "پاسۆرد داخڵ بکە",
        "msg_delivered": "سڵاو، داواکارییەکەت گەیشت ✅", "msg_onway": "سڵاو، داواکارییەکەت لە ڕێگەیە 🚚"
    },
    "العربية 🇮🇶": {
        "dir": "rtl", "align": "right",
        "title": "گولدن دليفري ✨",
        "subtitle": "أسرع وخدمة توصيل موثوقة في كركوك",
        "get_gps": "📍 تحديد موقع الزبون (GPS)",
        "gps_info": "يرجى الضغط على 'Allow' لتحديد موقعك.",
        "gps_success": "✅ تم تحديد موقعك!",
        "customer_name": "👤 اسم الزبون", "shop_name": "🏪 اسم المحل", "shop_addr": "📍 عنوان المحل",
        "phone": "📞 رقم الموبايل", "area": "🏘 منطقة الزبون", "full_addr": "🏠 تفاصيل العنوان",
        "location_label": "📍 رابط الخريطة (تلقائي)", "price": "💰 السعر (د.ع)",
        "submit": "تسجيل وإرسال الوصل ✅", "wa_btn": "إرسال البيانات للمكتب 💬",
        "error": "⚠️ يرجى ملء البيانات", "success": "✅ تم التسجيل بنجاح",
        "admin_title": "🛠 لوحة التحكم", "admin_pass": "أدخل كلمة المرور",
        "msg_delivered": "مرحباً، تم توصيل طلبيتك ✅", "msg_onway": "مرحباً، طلبيتك في الطريق 🚚"
    },
    "English 🇬🇧": {
        "dir": "ltr", "align": "left",
        "title": "GOLDEN DELIVERY ✨",
        "subtitle": "Fastest Delivery Service in Kirkuk",
        "get_gps": "📍 Get Customer Location (GPS)",
        "gps_info": "Please click 'Allow' to share your location.",
        "gps_success": "✅ Location Captured!",
        "customer_name": "👤 Customer Name", "shop_name": "🏪 Shop Name", "shop_addr": "📍 Shop Address",
        "phone": "📞 Phone Number", "area": "🏘 Customer Area", "full_addr": "🏠 Address Details",
        "location_label": "📍 Map Link (Auto)", "price": "💰 Price (IQD)",
        "submit": "Register & Send Receipt ✅", "wa_btn": "Send to Office 💬",
        "error": "⚠️ Please fill all fields", "success": "✅ Registered Successfully",
        "admin_title": "🛠 Admin Panel", "admin_pass": "Enter Password",
        "msg_delivered": "Hello, your order has been delivered ✅", "msg_onway": "Hello, your order is on the way 🚚"
    }
}

if "selected_lang" not in st.session_state: st.session_state.selected_lang = "کوردی 🇭🇺"

col_ref, col_lang, col_space = st.columns([0.5, 1.5, 4])
with col_ref:
    if st.button("🔄"): st.rerun()
with col_lang:
    lang_choice = st.selectbox("🌐 Language", list(languages.keys()), index=list(languages.keys()).index(st.session_state.selected_lang))
    st.session_state.selected_lang = lang_choice

L = languages[st.session_state.selected_lang]

# --- جی پی ئێس (GPS) ---
st.info(f"{L['get_gps']}: {L['gps_info']}")
loc = streamlit_js_eval(data_key='pos', func_name='getCurrentPosition', component_value=None)
gps_link = ""
if loc:
    lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
    gps_link = f"https://www.google.com/maps?q={lat},{lon}"
    st.success(L['gps_success'])

# --- داتا ---
DB_FILE = "deliveries.csv"
def load_data():
    if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE, dtype={"phone": str})
    return pd.DataFrame(columns=["customer", "shop", "phone", "area", "address", "price", "location"])

# --- ستایل ---
st.markdown(f"""<style>
    html, body, [data-testid="stAppViewContainer"] {{ direction: {L['dir']}; text-align: {L['align']}; }}
    .brand-header {{ background: linear-gradient(135deg, #1a1a1a 0%, #333333 100%); padding: 20px; border-radius: 15px; border-bottom: 4px solid #D4AF37; text-align: center; margin-bottom: 15px; }}
    .brand-title {{ color: #D4AF37; font-size: 28px; font-weight: bold; }}
    .stForm {{ border: 1px solid #D4AF37 !important; border-radius: 15px; }}
</style>""", unsafe_allow_html=True)

st.markdown(f'<div class="brand-header"><div class="brand-title">{L["title"]}</div><div style="color:white;">{L["subtitle"]}</div></div>', unsafe_allow_html=True)

# --- فۆرمی سەرەکی ---
with st.form("delivery_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        customer = st.text_input(L['customer_name'])
        shop = st.text_input(L['shop_name'])
        shop_addr = st.text_input(L['shop_addr'])
    with col2:
        phone = st.text_input(L['phone'])
        area_input = st.text_input(L['area'])
        full_addr = st.text_input(L['full_addr'])
        location = st.text_input(L['location_label'], value=gps_link)
        price = st.number_input(L['price'], min_value=0, step=250)
    
    if st.form_submit_button(L['submit']):
        if not customer or not phone:
            st.error(L['error'])
        else:
            df = load_data()
            new_row = pd.DataFrame([{"customer": customer, "shop": shop, "phone": phone, "area": area_input, "address": full_addr, "price": price, "location": location}])
            pd.concat([df, new_row]).to_csv(DB_FILE, index=False)
            
            wa_msg = f"Golden Delivery ✨\n👤 کڕیار: {customer}\n🏘 گەڕەک: {area_input}\n📍 شوێن: {location}\n📞 مۆبایل: {phone}\n💰 نرخ: {price:,} IQD"
            link = f"https://wa.me/9647801352003?text={urllib.parse.quote(wa_msg)}"
            st.success(L['success'])
            st.markdown(f'<a href="{link}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:12px; border-radius:10px; font-weight:bold; cursor:pointer;">{L["wa_btn"]}</button></a>', unsafe_allow_html=True)

# --- 🛠 بەشی ئەدمین (Admin) ---
st.divider()
with st.expander(L['admin_title']):
    if st.text_input(L['admin_pass'], type="password") == "dr_danyal_2024":
        data = load_data()
        if not data.empty:
            st.dataframe(data, use_container_width=True)
            for i, row in data.iterrows():
                col_n, col_d, col_w = st.columns([2, 2, 2])
                with col_n: st.write(f"👤 {row['customer']}")
                with col_d:
                    # دوگمەی گەیشت
                    m_del = urllib.parse.quote(L['msg_delivered'])
                    st.markdown(f'<a href="https://wa.me/{row["phone"]}?text={m_del}" target="_blank"><button style="background:#4CAF50; color:white; border:none; padding:5px; border-radius:5px; width:100%;">✅ گەیشت</button></a>', unsafe_allow_html=True)
                with col_w:
                    # دوگمەی لە ڕێگەیە
                    m_way = urllib.parse.quote(L['msg_onway'])
                    st.markdown(f'<a href="https://wa.me/{row["phone"]}?text={m_way}" target="_blank"><button style="background:#FF9800; color:white; border:none; padding:5px; border-radius:5px; width:100%;">🚚 لە ڕێگەیە</button></a>', unsafe_allow_html=True)
