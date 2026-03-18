import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Golden Delivery", layout="wide", initial_sidebar_state="collapsed")

# Initialize Session States
if 'page' not in st.session_state: st.session_state.page = "home"
if 'user_email' not in st.session_state: st.session_state.user_email = None
if 'admin_auth' not in st.session_state: st.session_state.admin_auth = False
if 'lang' not in st.session_state: st.session_state.lang = "English 🇬🇧"
if 'theme' not in st.session_state: st.session_state.theme = "Dark 🌙"

# --- 2. MULTI-LANGUAGE STRINGS ---
languages = {
    "English 🇬🇧": {
        "dir": "ltr", "title": "GOLDEN DELIVERY", "nav_home": "Home", "nav_order": "Order", "nav_terms": "Terms", "nav_profile": "Account",
        "phone": "Phone Number", "customer": "Customer Name", "shop": "Shop Name", "area": "Neighborhood", "addr": "Address Details", "price": "Price (IQD)",
        "submit": "Confirm Order", "desc": "Fast and secure delivery in Kirkuk.", "support": "Contact Support", "secret_msg": "🌟 Form Complete! Click here for your link:"
    },
    "کوردی 🇭🇺": {
        "dir": "rtl", "title": "گۆڵدن دلیڤەری", "nav_home": "سەرەکی", "nav_order": "داواکردن", "nav_terms": "یاساکان", "nav_profile": "هەژمار",
        "phone": "ژمارەی مۆبایل", "customer": "ناوی کڕیار", "shop": "ناوی دوکان", "area": "گەڕەک", "addr": "ناونیشان", "price": "نرخ",
        "submit": "تۆمارکردن", "desc": "گەیاندنی خێرا و پارێزراو لە کەرکوک.", "support": "پەیوەندی", "secret_msg": "🌟 زانیارییەکان تەواون! کرتە لێرە بکە بۆ لینکەکە:"
    },
    "العربية 🇮🇶": {
        "dir": "rtl", "title": "گولدن دليفري", "nav_home": "الرئيسية", "nav_order": "طلب", "nav_terms": "الشروط", "nav_profile": "الحساب",
        "phone": "رقم الهاتف", "customer": "اسم الزبون", "shop": "اسم المحل", "area": "المنطقة", "addr": "العنوان", "price": "السعر",
        "submit": "تأكيد الطلب", "desc": "توصيل سريع وآمن في كركوك.", "support": "الدعم الفني", "secret_msg": "🌟 البيانات كاملة! اضغط هنا للرابط:"
    }
}

L = languages[st.session_state.lang]

# --- 3. CUSTOM CSS (FIXING DARK MODE VISIBILITY) ---
is_dark = st.session_state.theme == "Dark 🌙"
bg = "#0f1116" if is_dark else "#ffffff"
txt = "#ffffff" if is_dark else "#1a1a1a"
accent = "#D4AF37"

st.markdown(f"""
    <style>
    [data-testid="stSidebar"] {{ display: none; }}
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
        background-color: {bg} !important;
        color: {txt} !important;
        direction: {L['dir']};
    }}
    /* Force visibility on all text elements */
    h1, h2, h3, h4, p, span, label, .stMarkdown, .stSelectbox label, .stTextInput label {{
        color: {txt} !important;
    }}
    /* Style Inputs for Dark Mode */
    input, textarea, .stSelectbox div[data-baseweb="select"] {{
        background-color: rgba(255,255,255,0.1) !important;
        color: {txt} !important;
        border: 1px solid {accent} !important;
    }}
    .brand-header {{
        background: linear-gradient(135deg, {accent} 0%, #8A6D3B 100%);
        padding: 30px; border-radius: 0 0 30px 30px; text-align: center; color: white !important;
    }}
    .footer-contact {{
        text-align: center; padding: 20px; border-top: 1px solid {accent}55; margin-top: 50px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. TOP BAR (LANGUAGE ONLY ON HOME) ---
c1, c2 = st.columns([2, 1])
with c1: st.markdown(f"<h2 style='color:{accent};'>{L['title']}</h2>", unsafe_allow_html=True)
if st.session_state.page == "home":
    with c2:
        with st.expander("🌐 Settings"):
            st.session_state.lang = st.selectbox("Language", list(languages.keys()), index=list(languages.keys()).index(st.session_state.lang))
            st.session_state.theme = st.radio("Theme", ["Light ☀️", "Dark 🌙"], index=0 if not is_dark else 1, horizontal=True)

# --- 5. PAGE LOGIC ---

if st.session_state.page == "home":
    st.markdown(f'<div class="brand-header"><h1 style="color:white !important;">{L["title"]}</h1></div>', unsafe_allow_html=True)
    st.markdown(f"<div style='text-align:center; padding:40px;'><h3>{L['desc']}</h3></div>", unsafe_allow_html=True)

elif st.session_state.page == "order":
    st.markdown(f"<h2 style='text-align:center; color:{accent};'>{L['nav_order']}</h2>", unsafe_allow_html=True)
    
    # Order Form
    with st.container():
        phone_val = st.text_input(L['phone'])
        cust_val = st.text_input(L['customer'])
        shop_val = st.text_input(L['shop'])
        area_val = st.selectbox(L['area'], ["--", "Arfa", "Tis'in", "Shorja", "Musalla", "Wasit", "Quraya"])
        addr_val = st.text_area(L['addr'])
        price_val = st.number_input(L['price'], value=3000)

        # LINK LOGIC: Show link only if all fields are filled
        if all([phone_val, cust_val, shop_val, area_val != "--", addr_val]):
            st.markdown(f"**{L['secret_msg']}** [www.goldendelivery-special.com](https://www.google.com)")

        if st.button(L['submit'], use_container_width=True):
            st.success("✅ Order Sent!")

elif st.session_state.page == "terms":
    st.markdown(f"<h2>{L['nav_terms']}</h2>", unsafe_allow_html=True)
    st.write("1. 1/3 Free. 2. No illegal goods. 3. Quick Kirkuk service.")

elif st.session_state.page == "profile":
    st.markdown(f"<h2>{L['nav_profile']}</h2>", unsafe_allow_html=True)
    pwd = st.text_input("Admin Password", type="password")
    if pwd == "GoldenAdmin2026":
        st.write("🔗 [Private Admin Dashboard](https://your-private-link.com)")
        st.write("🔗 [Inventory Link](https://your-private-link.com/inventory)")
    else:
        st.info("Please enter password to see management links.")

# --- 6. FOOTER (NUMBERS) ---
st.markdown(f"""
    <div class="footer-contact">
        <h4>📞 {L['support']}</h4>
        <p style="font-size: 1.2rem; color:{accent} !important;">
            07721959922 &nbsp; | &nbsp; 07801352003
        </p>
    </div>
    """, unsafe_allow_html=True)

# --- 7. STICKY NAV ---
st.markdown("<br><br>", unsafe_allow_html=True)
n1, n2, n3, n4 = st.columns(4)
with n1: 
    if st.button(f"🏠 {L['nav_home']}", use_container_width=True): st.session_state.page="home"; st.rerun()
with n2: 
    if st.button(f"🚚 {L['nav_order']}", use_container_width=True): st.session_state.page="order"; st.rerun()
with n3: 
    if st.button(f"📜 {L['nav_terms']}", use_container_width=True): st.session_state.page="terms"; st.rerun()
with n4: 
    if st.button(f"👤 {L['nav_profile']}", use_container_width=True): st.session_state.page="profile"; st.rerun()
