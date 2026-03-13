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
        "subtitle": "خێراترین خزمەتگوزاری گەیاندن لە کەرکوک",
        "customer_name": "👤 ناوی کڕیار", 
        "shop_name": "🏪 ناوی دوکان", 
        "phone": "📞 ژمارەی مۆبایل", 
        "area": "🏘 گەڕەکی کڕیار", 
        "price": "💰 نرخ (د.ع)",
        "submit": "تۆمارکردنی داواکاری ✅", 
        "wa_btn": "ناردنی وەسڵ بۆ ئۆفیس 💬",
        "track_title": "🔍 بەدواداچوونی داواکاری",
        "track_btn": "بگەڕێ",
        "status_pending": "⏳ چاوەڕوان",
        "status_onway": "🚚 لە ڕێگەیە",
        "status_delivered": "✅ گەیشت",
        "admin_title": "🛠 پانێڵی بەڕێوەبەرایەتی",
        "admin_pass": "پاسۆرد"
    },
    "العربية 🇮🇶": {
        "dir": "rtl", "align": "right",
        "title": "گولدن دليفري ✨",
        "subtitle": "أسرع خدمة توصيل في كركوك",
        "customer_name": "👤 اسم الزبون", 
        "shop_name": "🏪 اسم المحل", 
        "phone": "📞 رقم الموبايل", 
        "area": "🏘 منطقة الزبون", 
        "price": "💰 السعر (د.ع)",
        "submit": "تسجيل الطلبية ✅", 
        "wa_btn": "إرسال للمكتب 💬",
        "track_title": "🔍 تتبع طلبيتك",
        "track_btn": "بحث",
        "status_pending": "⏳ قيد الانتظار",
        "status_onway": "🚚 في الطريق",
        "status_delivered": "✅ تم التوصيل",
        "admin_title": "🛠 لوحة التحكم",
        "admin_pass": "كلمة المرور"
    },
    "English 🇬🇧": {
        "dir": "ltr", "align": "left",
        "title": "GOLDEN DELIVERY ✨",
        "subtitle": "Fastest delivery service in Kirkuk",
        "customer_name": "👤 Customer Name", 
        "shop_name": "🏪 Shop Name", 
        "phone": "📞 Phone Number", 
        "area": "🏘 Customer Area", 
        "price": "💰 Price (IQD)",
        "submit": "Register Order ✅", 
        "wa_btn": "Send to Office 💬",
        "track_title": "🔍 Track Your Order",
        "track_btn": "Track",
        "status_pending": "⏳ Pending",
        "status_onway": "🚚 On the way",
        "status_delivered": "✅ Delivered",
        "admin_title": "🛠 Admin Panel",
        "admin_pass": "Password"
    }
}

# --- ٢. هەڵبژاردنی زمان لە سەرەوە ---
col_lang, col_empty = st.columns([1, 3])
with col_lang:
    lang_choice = st.selectbox("🌐 Choose Language / زمان هەڵبژێرە", list(languages.keys()))
    L = languages[lang_choice]

# --- ٣. بارکردنی داتا ---
DB_FILE = "deliveries.csv"
def load_data():
    if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE, dtype={"phone": str})
    return pd.DataFrame(columns=["date", "customer", "shop", "phone", "area", "price", "status"])

# --- ٤. ستایلی لاپەڕە ---
st.markdown(f"""
    <style>
    html, body, [data-testid="stAppViewContainer"] {{ direction: {L['dir']}; text-align: {L['align']}; }}
    .brand-header {{ background: linear-gradient(135deg, #1a1a1a 0%, #333333 100%); padding: 30px; border-radius: 15px; border-bottom: 5px solid #D4AF37; text-align: center; margin-bottom: 25px; }}
    .brand-title {{ color: #D4AF37; font-size: 35px; font-weight: bold; }}
    .stForm {{ border: 2px solid #D4AF37 !important; border-radius: 15px; padding: 25px; }}
    .status-box {{ padding: 10px; border-radius: 10px; background: #f0f2f6; border-right: 5px solid #D4AF37; margin: 10px 0; }}
    </style>
    """, unsafe_allow_html=True)

st.markdown(f'<div class="brand-header"><div class="brand-title">{L["title"]}</div><div style="color:white;">{L["subtitle"]}</div></div>', unsafe_allow_html=True)

# --- ٥. سیستەمی بەدواداچوون (Tracking) ---
with st.expander(L['track_title']):
    track_phone = st.text_input(f"{L['phone']} (لێرە ژمارەکەت بنووسە)")
    if st.button(L['track_btn']):
        df_track = load_data()
        res = df_track[df_track['phone'] == track_phone].tail(1)
        if not res.empty:
            current_status = res.iloc[0]['status']
            st.markdown(f'<div class="status-box"><b>{L["customer_name"]}:</b> {res.iloc[0]["customer"]}<br><b>بارودۆخ:</b> {current_status}</div>', unsafe_allow_html=True)
        else:
            st.warning("هیچ داواکارییەک بەم ژمارەیە نییە")

st.divider()

# --- ٦. فۆرمی تۆمارکردن ---
with st.form("delivery_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        customer = st.text_input(L['customer_name'])
        shop = st.text_input(L['shop_name'])
    with col2:
        phone = st.text_input(L['phone'])
        price = st.number_input(L['price'], min_value=0, step=250)
    
    selected_area = st.selectbox(L['area'], ["هەڵبژێرە..."] + sorted(["ڕەحیماوا", "ئیسکان", "تسعین", "واسطی", "ئازادی", "شۆراو", "پەنجاعەلی"]))
    submit = st.form_submit_button(L['submit'])
    
    if submit:
        if not customer or not phone or "هەڵبژێرە" in selected_area:
            st.error("تکایە هەموو زانیارییەکان پڕ بکەرەوە")
        else:
            df = load_data()
            new_row = pd.DataFrame([{"date": datetime.now().strftime("%Y-%m-%d"), "customer": customer, "shop": shop, "phone": phone, "area": selected_area, "price": price, "status": L['status_pending']}])
            pd.concat([df, new_row]).to_csv(DB_FILE, index=False)
            st.success("تۆمارکرا")
            
            msg = f"Golden Delivery ✨\n📦 داواکاری نوێ\n👤 کڕیار: {customer}\n🏪 دوکان: {shop}\n💰 نرخ: {price:,} IQD"
            link = f"https://wa.me/9647801352003?text={urllib.parse.quote(msg)}"
            st.markdown(f'<a href="{link}" target="_blank"><button style="width:100%; background:#25D366; color:white; border:none; padding:15px; border-radius:10px; cursor:pointer;">{L["wa_btn"]}</button></a>', unsafe_allow_html=True)

# --- ٧. پانێڵی ئەدمین (Boss) ---
if st.query_params.get("role") == "boss":
    st.divider()
    st.subheader(L['admin_title'])
    if st.text_input(L['admin_pass'], type="password") == "golden2024":
        data = load_data()
        if not data.empty:
            for i, row in data.iterrows():
                with st.expander(f"📦 {row['customer']} - {row['status']}"):
                    new_stat = st.selectbox("گۆڕینی بارودۆخ", [L['status_pending'], L['status_onway'], L['status_delivered']], key=f"stat_{i}")
                    if st.button("Update", key=f"btn_{i}"):
                        data.at[i, 'status'] = new_stat
                        data.to_csv(DB_FILE, index=False)
                        st.rerun()
                    
                    # ناردنی نامەی واتسئەپ
                    raw_p = str(row['phone']).replace('0', '964', 1) if str(row['phone']).startswith('0') else str(row['phone'])
                    m_link = f"https://wa.me/{raw_p}?text={urllib.parse.quote('داواکارییەکەت: ' + new_stat)}"
                    st.markdown(f'<a href="{m_link}" target="_blank">ناردنی نۆتیفیکەیشن بۆ کڕیار 📲</a>', unsafe_allow_html=True)

st.markdown(f'<div style="text-align:center; padding:20px;">📞 0780 135 2003 | 0772 195 9922</div>', unsafe_allow_html=True)
