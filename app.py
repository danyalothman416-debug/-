import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. Page Config ---
st.set_page_config(page_title="Golden Delivery", layout="wide", initial_sidebar_state="collapsed")

if 'page' not in st.session_state:
    st.session_state.page = "home"

languages = {
    "کوردی 🇭🇺": {
        "dir": "rtl","align": "right","theme_label": "ڕووکار","light": "ڕوون ☀️","dark": "تاریک 🌙",
        "title": "GOLDEN DELIVERY ✨",
        "subtitle": "خێراترین خزمەتگوزاری گەیاندن لە کەرکوک",
        "customer_name": "👤 ناوی کڕیار",
        "shop_name": "🏪 ناوی دوکان",
        "shop_addr": "📍 ناونیشانی دوکان",
        "phone": "📞 ژمارەی مۆبایل",
        "area": "🏘 گەڕەکی کڕیار",
        "full_addr": "🏠 وردەکاری ناونیشان",
        "price": "💰 نرخ (د.ع)",
        "submit": "تۆمارکردنی داواکاری ✅",
        "nav_home": "🏠 سەرەکی",
        "nav_discount": "🏷️ داشکاندن",
        "nav_profile": "👤 هەژمار",
        "free_msg": "🎁 پیرۆزە! تۆ ٣ گەیاندنت هەبووە، ئەمەیان بە خۆڕاییە!",
        "need_more": "ماوەتە بۆ گەیاندنی خۆڕایی:",
        "acc_info": "زانیاری هەژمار",
        "status_pending": "⏳ چاوەڕوان"
    },

    "العربية 🇮🇶": {
        "dir": "rtl","align": "right","theme_label": "المظهر","light": "فاتح ☀️","dark": "داكن 🌙",
        "title": "گولدن دليفري ✨",
        "subtitle": "أسرع خدمة توصيل في كركوك",
        "customer_name": "👤 اسم الزبون",
        "shop_name": "🏪 اسم المحل",
        "shop_addr": "📍 عنوان المحل",
        "phone": "📞 رقم الموبايل",
        "area": "🏘 منطقة الزبون",
        "full_addr": "🏠 تفاصيل العنوان",
        "price": "💰 السعر (د.ع)",
        "submit": "تسجيل الطلبية ✅",
        "nav_home": "🏠 الرئيسية",
        "nav_discount": "🏷️ الخصومات",
        "nav_profile": "👤 الحساب",
        "free_msg": "🎁 مبروك! لديك ٣ توصيلات سابقة، هذا التوصيل مجاني!",
        "need_more": "متبقي للتوصيل المجاني:",
        "acc_info": "معلومات الحساب",
        "status_pending": "⏳ قيد الانتظار"
    },

    "English 🇬🇧": {
        "dir": "ltr","align": "left","theme_label": "Theme","light": "Light ☀️","dark": "Dark 🌙",
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
        "nav_home": "🏠 Home",
        "nav_discount": "🏷️ Offers",
        "nav_profile": "👤 Account",
        "free_msg": "🎁 Congrats! You had 3 deliveries, this one is FREE!",
        "need_more": "Remaining for free delivery:",
        "acc_info": "Account Info",
        "status_pending": "⏳ Pending"
    }
}

# --- Language / Theme ---
col_lang, col_theme = st.columns(2)

with col_lang:
    lang_choice = st.selectbox("🌐 Language", list(languages.keys()))
    L = languages[lang_choice]

with col_theme:
    theme_choice = st.radio(L['theme_label'], [L['light'], L['dark']], horizontal=True)

is_dark = theme_choice == L['dark']
bg_color = "#121212" if is_dark else "#f7f9fc"
text_color = "#ffffff" if is_dark else "#2c3e50"
card_bg = "#1e1e1e" if is_dark else "#ffffff"

# --- Data ---
DB_FILE = "deliveries.csv"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE, dtype={"phone": str})
    return pd.DataFrame(columns=["date","customer","shop","phone","area","address","shop_addr","price","status"])

# --- CSS ---
st.markdown(f"""
<style>

[data-testid="stHeader"]{{visibility:hidden}}
#MainMenu{{visibility:hidden}}
footer{{visibility:hidden}}

html,body,[data-testid="stAppViewContainer"]{{
direction:{L['dir']};
text-align:{L['align']};
background:{bg_color};
color:{text_color};
}}

.brand-header{{
background:linear-gradient(135deg,#D4AF37,#8A6D3B);
padding:40px 20px;
border-radius:0 0 30px 30px;
text-align:center;
margin-bottom:30px;
}}

.brand-title{{
color:white;
font-size:28px;
font-weight:bold;
}}

.main-content{{
padding-bottom:120px;
}}

.bottom-nav{{
position:fixed;
bottom:0;
left:0;
width:100%;
background:{card_bg};
border-top:1px solid rgba(212,175,55,0.4);
display:flex;
justify-content:space-around;
padding:10px 0;
z-index:999999;
}}

.bottom-nav button{{
background:none;
border:none;
font-size:14px;
color:{text_color};
}}

.bottom-nav button:hover{{
color:#D4AF37;
}}

</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-content">', unsafe_allow_html=True)

# --- Pages ---
if st.session_state.page == "offers":

    st.markdown(f'<div class="brand-header"><div class="brand-title">{L["nav_discount"]}</div></div>', unsafe_allow_html=True)

    phone_check = st.text_input(L['phone'], placeholder="07xx xxx xxxx")

    if phone_check:
        df = load_data()
        count = len(df[df['phone']==phone_check])

        if count >= 3:
            st.balloons()
            st.success(L['free_msg'])
        else:
            st.info(f"{L['need_more']} {3-count}")

elif st.session_state.page == "profile":

    st.markdown(f'<div class="brand-header"><div class="brand-title">{L["nav_profile"]}</div></div>', unsafe_allow_html=True)

    user_p = st.text_input(L['phone'])

    if user_p:
        df = load_data()
        user_data = df[df['phone']==user_p].tail(1)

        if not user_data.empty:
            st.info(f"👤 {L['customer_name']}: {user_data.iloc[0]['customer']}")

else:

    st.markdown(f'<div class="brand-header"><div class="brand-title">{L["title"]}</div><div style="color:white">{L["subtitle"]}</div></div>', unsafe_allow_html=True)

    with st.form("delivery_form"):

        c1,c2 = st.columns(2)

        with c1:
            customer = st.text_input(L['customer_name'])
            shop = st.text_input(L['shop_name'])

        with c2:
            phone = st.text_input(L['phone'])
            area = st.selectbox(L['area'],["Kirkuk Center","Rahimawa","Iskan"])

        price = st.number_input(L['price'],value=3000)

        if st.form_submit_button(L['submit']):

            df = load_data()

            new_row = pd.DataFrame([{
                "date":datetime.now().strftime("%Y-%m-%d"),
                "customer":customer,
                "shop":shop,
                "phone":phone,
                "area":area,
                "status":L['status_pending']
            }])

            pd.concat([df,new_row]).to_csv(DB_FILE,index=False)

            st.success("Done!")

st.markdown('</div>', unsafe_allow_html=True)

# --- Bottom Navigation ---
st.markdown('<div class="bottom-nav">', unsafe_allow_html=True)

col1,col2,col3 = st.columns(3)

with col1:
    if st.button(L['nav_profile']):
        st.session_state.page="profile"
        st.rerun()

with col2:
    if st.button(L['nav_home']):
        st.session_state.page="home"
        st.rerun()

with col3:
    if st.button(L['nav_discount']):
        st.session_state.page="offers"
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
