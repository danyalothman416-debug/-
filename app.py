import streamlit as st
import pandas as pd
import os
import urllib.parse
# پێویستە ئەمە لای خۆت دابەزێنیت: pip install streamlit-js-eval
from streamlit_js_eval import streamlit_js_eval

# --- 1. ڕێکخستنی لاپەڕە و زمان ---
st.set_page_config(page_title="Golden Delivery", layout="wide")

# فەرهەنگی وەرگێڕان لەگەڵ ئاڵاکان و تایبەتمەندی نوێ
languages = {
    "کوردی 🇭🇺": {
        "id": "Kurdish", "dir": "rtl", "align": "right",
        "title": "GOLDEN DELIVERY ✨",
        "subtitle": "خێراترین و باوەڕپێکراوترین خزمەتگوزاری گەیاندن لە کەرکوک",
        "get_loc": "📍 دیاریکردنی شوێنەکەم (GPS)",
        "loc_success": "✅ شوێنەکەت بە سەرکەوتوویی وەرگیرا",
        "customer_name": "👤 ناوی کڕیار",
        "shop_name": "🏪 ناوی دوکان",
        "shop_addr": "📍 ناونیشانی دوکان",
        "phone": "📞 ژمارەی مۆبایل",
        "area": "🏘 گەڕەکی کڕیار",
        "full_addr": "🏠 وردەکاری ناونیشان (نزیک کوێیە؟)",
        "location": "🔗 لینکی نەخشە (ئۆتۆماتیکی دروست دەبێت)",
        "price": "💰 نرخ (د.ع)",
        "submit": "تۆمارکردن و ناردنی وەسڵ ✅",
        "wa_btn": "ناردنی زانیاری بۆ ئۆفیس 💬",
        "error": "⚠️ تکایە ناوی کڕیار و مۆبایل و گەڕەک پڕ بکەرەوە",
        "success": "✅ بە سەرکەوتوویی تۆمارکرا",
        "footer": "بۆ دابەزاندنی ئەپ: کلیک لە ⎙ یان ⋮ بکە و Add to Home Screen هەڵبژێرە"
    },
    "العربية 🇮🇶": {
        "id": "Arabic", "dir": "rtl", "align": "right",
        "title": "گولدن دليفري ✨",
        "subtitle": "أسرع وخدمة توصيل موثوقة في كركوك",
        "get_loc": "📍 تحديد موقعي (GPS)",
        "loc_success": "✅ تم تحديد موقعك بنجاح",
        "customer_name": "👤 اسم الزبون",
        "shop_name": "🏪 اسم المحل",
        "shop_addr": "📍 عنوان المحل",
        "phone": "📞 رقم الموبايل",
        "area": "🏘 منطقة الزبون",
        "full_addr": "🏠 تفاصيل العنوان (قرب ماذا؟)",
        "location": "🔗 رابط الخريطة (يتم إنشاؤه تلقائياً)",
        "price": "💰 السعر (د.ع)",
        "submit": "تسجيل وإرسال الوصل ✅",
        "wa_btn": "إرسال البيانات للمكتب 💬",
        "error": "⚠️ يرجى ملء اسم الزبون والموبايل والمنطقة",
        "success": "✅ تم التسجيل بنجاح",
        "footer": "لتثبيت التطبيق: اضغط على ⎙ أو ⋮ واختر Add to Home Screen"
    }
}

# هەڵبژاردنی زمان
if "selected_lang" not in st.session_state:
    st.session_state.selected_lang = "کوردی 🇭🇺"

col_ref, col_lang, col_space = st.columns([0.5, 1.5, 4])
with col_ref:
    if st.button("🔄"): st.rerun()
with col_lang:
    lang_choice = st.selectbox("🌐 Language", list(languages.keys()), index=list(languages.keys()).index(st.session_state.selected_lang))
    st.session_state.selected_lang = lang_choice

L = languages[st.session_state.selected_lang]

# --- وەرگرتنی GPS (لێرەدا جێگیر کراوە بۆ ئەوەی پێش فۆرمەکە ئامادە بێت) ---
st.write(f"### {L['get_loc']}")
# ئەم کۆدە داوا لە وێبگەڕ دەکات شوێنەکە وەرگرێت
loc = streamlit_js_eval(data_key='pos', func_name='getCurrentPosition', component_value=None)
auto_loc_url = ""
if loc:
    lat = loc['coords']['latitude']
    lon = loc['coords']['longitude']
    auto_loc_url = f"https://www.google.com/maps?q={lat},{lon}"
    st.success(L['loc_success'])

# --- ستایلی لاپەڕە ---
st.markdown(f"""
    <style>
    section[data-testid="stSidebar"] {{ display: none !important; }}
    html, body, [data-testid="stAppViewContainer"] {{ direction: {L['dir']}; text-align: {L['align']}; }}
    .brand-header {{
        background: linear-gradient(135deg, #1a1a1a 0%, #333333 100%);
        padding: 25px; border-radius: 15px; border-bottom: 4px solid #D4AF37;
        text-align: center; margin-bottom: 20px;
    }}
    .brand-title {{ color: #D4AF37; font-size: 32px; font-weight: bold; }}
    .num-fix {{ direction: ltr !important; display: inline-block !important; color: #D4AF37; font-weight: bold; }}
    .install-bar {{
        position: fixed; bottom: 0; left: 0; width: 100%;
        background-color: #1a1a1a; color: white; padding: 12px;
        text-align: center; border-top: 3px solid #D4AF37; z-index: 9999;
    }}
    .stForm {{ border: 1px solid #D4AF37 !important; border-radius: 15px !important; padding: 20px !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- ٢. لۆژیکی داتا ---
ADMIN_PASSWORD = "dr_danyal_2024" 
DB_FILE = "global_deliveries.csv"
MY_WHATSAPP = "9647801352003" 

KIRKUK_AREAS = sorted(["ڕەحیماوا", "پەنجاعەلی", "شۆراو", "تەپە", "ئیمام قاسم", "ئازادی", "شۆڕش", "ڕێگای بەغداد", "موسەڵا", "تسعین", "واسطی", "دۆمیز", "غرناطة", "حوزەیران", "شیمال", "عرفە", "کوردستان", "دەروازە", "ناوەندی شار"])

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE, dtype={"مۆبایل": str})
        return df
    return pd.DataFrame(columns=["کڕیار", "ناوی دوکان", "مۆبایل", "نرخ", "گەڕەک", "شوێن", "دۆخی داواکاری"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

# --- ٣. ڕووکاری سەرەکی ---
st.markdown(f"""<div class="brand-header"><div class="brand-title">{L['title']}</div><div style="color:white; font-size:14px;">{L['subtitle']}</div></div>""", unsafe_allow_html=True)

with st.form("delivery_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        customer = st.text_input(L['customer_name'])
        shop_name = st.text_input(L['shop_name'])
        shop_address = st.text_input(L['shop_addr'])
    with col2:
        phone = st.text_input(L['phone'])
        selected_area = st.selectbox(L['area'], ["Select / هەڵبژاردن"] + KIRKUK_AREAS)
        full_address = st.text_input(L['full_addr'])
        # ئۆتۆماتیکی لینکەکە لێرە دادەنرێت
        loc_url = st.text_input(L['location'], value=auto_loc_url)
        price = st.number_input(L['price'], min_value=0, step=250)
    
    submit = st.form_submit_button(L['submit'])
    
    if submit:
        if not customer or not phone or "Select" in selected_area:
            st.error(L['error'])
        else:
            df = load_data()
            new_row = pd.DataFrame([{"کڕیار": customer, "ناوی دوکان": shop_name, "مۆبایل": str(phone), "نرخ": price, "گەڕەک": selected_area, "شوێن": loc_url, "دۆخی داواکاری": "وەرگیرا 📥"}])
            save_data(pd.concat([df, new_row], ignore_index=True))
            
            msg = (f"Golden Delivery ✨\n👤 کڕیار: {customer}\n🏘 گەڕەک: {selected_area}\n📍 نەخشە: {loc_url}\n📞 مۆبایل: {phone}\n💰 نرخ: {price:,} د.ع")
            link = f"https://wa.me/{MY_WHATSAPP}?text={urllib.parse.quote(msg)}"
            st.success(L['success'])
            st.markdown(f'<a href="{link}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:12px; border-radius:10px; font-weight:bold; cursor:pointer;">{L["wa_btn"]}</button></a>', unsafe_allow_html=True)

st.markdown(f'<div style="text-align:center; padding:15px; color:#D4AF37;">📞 <span class="num-fix">0772 195 9922</span> | <span class="num-fix">0780 135 2003</span></div>', unsafe_allow_html=True)
st.markdown(f"""<div class="install-bar">{L['footer']}</div>""", unsafe_allow_html=True)
