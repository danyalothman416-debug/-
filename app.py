import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Golden Delivery", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# Initialize Session States
if 'page' not in st.session_state: st.session_state.page = "home"
if 'user_email' not in st.session_state: st.session_state.user_email = None
if 'lang' not in st.session_state: st.session_state.lang = "English 🇬🇧"
if 'theme' not in st.session_state: st.session_state.theme = "Dark 🌙"

# --- 2. MULTI-LANGUAGE STRINGS ---
languages = {
    "English 🇬🇧": {
        "dir": "ltr", "title": "GOLDEN DELIVERY", "nav_home": "Home", "nav_order": "Order", "nav_terms": "Terms", "nav_profile": "Account",
        "phone": "Phone Number", "customer": "Customer Name", "shop": "Shop Name", "area": "Neighborhood", "addr": "Address Details", "price": "Price (IQD)",
        "submit": "Confirm Order", "support": "Customer Support", "whatsapp": "Message us on WhatsApp",
        "link_locked": "🔒 Complete all fields to unlock the link section.",
        "link_unlocked": "✅ Form Complete! You can now add your link below:"
    },
    "کوردی 🇭🇺": {
        "dir": "rtl", "title": "گۆڵدن دلیڤەری", "nav_home": "سەرەکی", "nav_order": "داواکردن", "nav_terms": "یاساکان", "nav_profile": "هەژمار",
        "phone": "ژمارەی مۆبایل", "customer": "ناوی کڕیار", "shop": "ناوی دوکان", "area": "گەڕەک", "addr": "ناونیشان", "price": "نرخ",
        "submit": "تۆمارکردن", "support": "پەیوەندی و پشتگیری", "whatsapp": "نامە بنێرە بۆ وەتسئەپ",
        "link_locked": "🔒 هەموو خانەکان پڕ بکەرەوە بۆ بینینی بەشی لینک.",
        "link_unlocked": "✅ زانیارییەکان تەواون! ئێستا دەتوانیت لینک زیاد بکەیت:"
    },
    "العربية 🇮🇶": {
        "dir": "rtl", "title": "گولدن دليفري", "nav_home": "الرئيسية", "nav_order": "طلب", "nav_terms": "الشروط", "nav_profile": "الحساب",
        "phone": "رقم الهاتف", "customer": "اسم الزبون", "shop": "اسم المحل", "area": "المنطقة", "addr": "العنوان", "price": "السعر",
        "submit": "تأكيد الطلب", "support": "الدعم الفني", "whatsapp": "تواصل معنا عبر واتساب",
        "link_locked": "🔒 أكمل جميع الحقول لفتح قسم الرابط.",
        "link_unlocked": "✅ البيانات كاملة! يمكنك الآن إضافة الرابط أدناه:"
    }
}

L = languages[st.session_state.lang]

# --- 3. ADVANCED CSS (DARK MODE STABILITY) ---
is_dark = st.session_state.theme == "Dark 🌙"
main_bg = "#0f1116" if is_dark else "#f9f9f9"
text_color = "#ffffff" if is_dark else "#121212"
accent = "#D4AF37"

st.markdown(f"""
    <style>
    [data-testid="stSidebar"] {{ display: none; }}
    
    /* Force Background and Text Contrast */
    html, body, [data-testid="stAppViewContainer"] {{
        background-color: {main_bg} !important;
        color: {text_color} !important;
        direction: {L['dir']};
    }}

    /* Global Text Visibility Fix */
    h1, h2, h3, h4, h5, h6, p, span, label, li, .stMarkdown {{
        color: {text_color} !important;
    }}

    /* Input Styling for visibility */
    .stTextInput input, .stTextArea textarea, .stSelectbox div {{
        background-color: rgba(255,255,255,0.08) !important;
        color: {text_color} !important;
        border: 1px solid {accent}66 !important;
    }}

    .brand-header {{
        background: linear-gradient(135deg, {accent} 0%, #8A6D3B 100%);
        padding: 30px; border-radius: 0 0 30px 30px; text-align: center;
    }}

    .footer-contact {{
        text-align: center; padding: 25px; border-top: 1px solid {accent}44; 
        margin-top: 40px; background: rgba(0,0,0,0.1); border-radius: 20px;
    }}

    .whatsapp-btn {{
        background-color: #25D366; color: white !important;
        padding: 10px 20px; border-radius: 50px; text-decoration: none;
        font-weight: bold; display: inline-block; margin-top: 10px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. TOP NAVIGATION (Settings on Home Only) ---
col_l, col_r = st.columns([2, 1])
with col_l:
    st.markdown(f"<h2 style='color:{accent}; margin:0;'>{L['title']}</h2>", unsafe_allow_html=True)
if st.session_state.page == "home":
    with col_r:
        with st.expander("⚙️ Settings"):
            st.session_state.lang = st.selectbox("Language", list(languages.keys()), index=list(languages.keys()).index(st.session_state.lang))
            st.session_state.theme = st.radio("Theme", ["Light ☀️", "Dark 🌙"], index=0 if st.session_state.theme == "Light ☀️" else 1, horizontal=True)

# --- 5. PAGE CONTENT ---

if st.session_state.page == "home":
    st.markdown(f'<div class="brand-header"><h1 style="color:white !important;">{L["title"]}</h1></div>', unsafe_allow_html=True)
    st.markdown(f"<div style='text-align:center; padding:40px;'><h3>{L['support']}</h3><p>Kirkuk's Trusted Golden Standard Delivery</p></div>", unsafe_allow_html=True)

elif st.session_state.page == "order":
    st.markdown(f"<h2 style='text-align:center; color:{accent};'>{L['nav_order']}</h2>", unsafe_allow_html=True)
    
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            p_phone = st.text_input(f"📞 {L['phone']}", placeholder="07xx xxx xxxx")
            p_cust = st.text_input(f"👤 {L['customer']}")
            p_shop = st.text_input(f"🏪 {L['shop']}")
        with c2:
            p_area = st.selectbox(f"📍 {L['area']}", ["--", "Arfa", "Tis'in", "Wasit", "Shorja", "Musalla"])
            p_addr = st.text_area(f"🏠 {L['addr']}")
            p_price = st.number_input(f"💰 {L['price']}", value=3000)

        # LINK LOGIC: Only show if all fields are filled
        all_filled = all([p_phone, p_cust, p_shop, p_area != "--", p_addr])
        
        if all_filled:
            st.success(L['link_unlocked'])
            user_link = st.text_input("🔗 Paste your link here / لینکی خۆت لێرە دابنێ")
        else:
            st.warning(L['link_locked'])

        if st.button(L['submit'], use_container_width=True):
            if all_filled:
                st.balloons()
                st.success("✅ Order Submitted Successfully!")
            else:
                st.error("❌ Please fill in all sections first.")

elif st.session_state.page == "terms":
    st.markdown(f"<h2>{L['nav_terms']}</h2>", unsafe_allow_html=True)
    st.write("1. 1/3 Free Loyalty Program. 2. No illegal items. 3. Quick service.")

elif st.session_state.page == "profile":
    st.markdown(f"<h2>{L['nav_profile']}</h2>", unsafe_allow_html=True)
    pwd = st.text_input("Admin Password", type="password")
    if pwd == "GoldenAdmin2026":
        st.info("🔓 Admin Access Granted. Management links visible.")
        st.markdown("- [Admin Dashboard](https://google.com)")

# --- 6. FOOTER (NUMBERS & WHATSAPP) ---
st.markdown(f"""
    <div class="footer-contact">
        <h4 style="margin-bottom:5px;">📞 {L['support']}</h4>
        <p style="font-size: 1.3rem; font-weight: bold; color:{accent} !important; margin-bottom:15px;">
            0772 1959922 &nbsp; | &nbsp; 0780 1352003
        </p>
        <a href="https://wa.me/9647721959922" class="whatsapp-btn">
            🟢 {L['whatsapp']}
        </a>
    </div>
    """, unsafe_allow_html=True)

# --- 7. STICKY NAVIGATION ---
st.markdown("<br><br><br>", unsafe_allow_html=True)
n1, n2, n3, n4 = st.columns(4)
with n1: 
    if st.button(f"🏠 {L['nav_home']}", use_container_width=True): st.session_state.page="home"; st.rerun()
with n2: 
    if st.button(f"🚚 {L['nav_order']}", use_container_width=True): st.session_state.page="order"; st.rerun()
with n3: 
    if st.button(f"📜 {L['nav_terms']}", use_container_width=True): st.session_state.page="terms"; st.rerun()
with n4: 
    if st.button(f"👤 {L['nav_profile']}", use_container_width=True): st.session_state.page="profile"; st.rerun()
