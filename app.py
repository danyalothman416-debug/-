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
if 'page' not in st.session_state:
    st.session_state.page = "home"
if 'user_email' not in st.session_state:
    st.session_state.user_email = None

# --- 2. MULTI-LANGUAGE & UI STRINGS ---
languages = {
    "English 🇬🇧": {
        "dir": "ltr", "align": "left", "theme_label": "Theme", "light": "Light ☀️", "dark": "Dark 🌙",
        "title": "GOLDEN DELIVERY",
        "desc": "Experience the gold standard of logistics in Kirkuk. Fast, secure, and always on time.",
        "customer_name": "Customer Name", "shop_name": "Shop Name", 
        "shop_addr": "Shop Address", "phone": "Phone Number", 
        "area": "Neighborhood", "full_addr": "Address Details (Near what?)",
        "price": "Price (IQD)", "submit": "Confirm Order", 
        "nav_home": "Home", "nav_order": "Order", "nav_profile": "Account",
        "free_info": "🎁 Special: 1 out of every 3 deliveries is FREE!",
        "free_success": "🎊 Loyalty Reward: This delivery is 0 IQD!",
        "google_btn": "Sign in with Google", "logout": "Logout",
        "settings": "Settings & Language"
    },
    "کوردی 🇭🇺": {
        "dir": "rtl", "align": "right", "theme_label": "ڕووکار", "light": "ڕوون ☀️", "dark": "تاریک 🌙",
        "title": "گۆڵدن دلیڤەری",
        "desc": "بەرزترین کوالێتی گەیاندن لە کەرکوک. خێرا، پارێزراو، و هەمیشە لە کاتی خۆیدا.",
        "customer_name": "ناوی کڕیار", "shop_name": "ناوی دوکان", 
        "shop_addr": "ناونیشانی دوکان", "phone": "ژمارەی مۆبایل", 
        "area": "گەڕەک", "full_addr": "وردەکاری ناونیشان (نزیک کوێیە؟)",
        "price": "نرخ (د.ع)", "submit": "تۆمارکردن", 
        "nav_home": "سەرەکی", "nav_order": "داواکردن", "nav_profile": "هەژمار",
        "free_info": "🎁 دیاری: یەکێک لە هەر ٣ گەیاندنێک بە خۆڕاییە!",
        "free_success": "🎊 پیرۆزە! ئەم گەیاندنەت بە ٠ دینارە!",
        "google_btn": "چوونەژوورەوە بە Google", "logout": "چوونەدەرەوە",
        "settings": "ڕێکخستن و زمان"
    },
    "العربية 🇮🇶": {
        "dir": "rtl", "align": "right", "theme_label": "المظهر", "light": "فاتح ☀️", "dark": "داكن 🌙",
        "title": "گولدن دليفري",
        "desc": "المعيار الذهبي للخدمات اللوجستية في كركوك. سرعة، أمان، ودقة في المواعيد.",
        "customer_name": "اسم الزبون", "shop_name": "اسم المحل", 
        "shop_addr": "عنوان المحل", "phone": "رقم الهاتف", 
        "area": "المنطقة", "full_addr": "تفاصيل العنوان (قرب ماذا؟)",
        "price": "السعر (د.ع)", "submit": "تأكيد الطلب", 
        "nav_home": "الرئيسية", "nav_order": "طلب", "nav_profile": "الحساب",
        "free_info": "🎁 عرض: واحدة من كل ٣ توصيلات مجانية!",
        "free_success": "🎊 مبروك! هذه الطلبية بـ ٠ دينار!",
        "google_btn": "الدخول بواسطة Google", "logout": "خروج",
        "settings": "الإعدادات واللغة"
    }
}

# --- 3. NEIGHBORHOODS ---
KIRKUK_AREAS = sorted([
    "Arfa / عرفة", "Tis'in / تسعين", "Binja Ali / بنجة علي", "Shoraw / شوراو",
    "Rahim Awa / رحيماوة", "Laylawa / ليلان", "Wasit / واسطي", "Al-Musalla / مصلى",
    "Quraya / قورية", "Dumiz / دوميز", "Al-Khadra / الخضراء", "Al-Wasiti / الواسطي",
    "Al-Askari / الحي العسكري", "Al-Qadisiyya / القادسية", "Al-Nasr / النصر", 
    "Azadi / ازادي", "Shura / شورى", "Al-Nabi Yunus / النبي يونس", "Al-Shorja / الشورجة",
    "Wahid Huzairan / واحد حزيران", "Ronaki / رونكي", "Biriti / بريتي", "Sarhad / سرحد",
    "Shahidan / شهيدان", "Tarkalan / تركلان", "Haidar Khana / حيدر خانة", "Sayyada / صيادة",
    "Al-Mu'allimin / المعلمين", "Al-Muhandisin / المهندسين", "Al-Atibba / الاطباء",
    "Al-Adala / العدالة", "Al-Salam / السلام", "Taza Khurmato / تازة خورماتو", 
    "Yaychi / يايجي", "Daquq / داقوق", "Laylan / ليلان", "Malha / ملحة", 
    "Bashir / بشير", "Tarjala / ترجلة"
])

# --- 4. TOP NAVIGATION & GLOBAL SETTINGS ---
# Consolidating everything that was in the sidebar into one "Settings" dropdown
with st.container():
    col_logo, col_set = st.columns([2, 1])
    with col_set:
        with st.expander("⚙️ Settings / ڕێکخستن"):
            lang_choice = st.selectbox("🌐 Language", list(languages.keys()))
            L = languages[lang_choice]
            theme_choice = st.radio(L['theme_label'], [L['light'], L['dark']], horizontal=True)
    with col_logo:
        L = languages[lang_choice] # Update L based on selection
        st.markdown(f"<h2 style='color:#D4AF37; margin:0;'>{L['title']}</h2>", unsafe_allow_html=True)

# --- 5. THEME ENGINE & CUSTOM CSS ---
is_dark = theme_choice == L['dark']
main_bg = "#0f1116" if is_dark else "#fdfdfd"
card_bg = "rgba(30, 34, 45, 0.8)" if is_dark else "rgba(255, 255, 255, 0.95)"
text_color = "#ffffff" if is_dark else "#1a1a1a"
accent = "#D4AF37"

st.markdown(f"""
    <style>
    /* Hide the Sidebar entirely */
    [data-testid="stSidebar"] {{ display: none; }}
    
    html, body, [data-testid="stAppViewContainer"] {{
        background: {main_bg};
        color: {text_color} !important;
        direction: {L['dir']};
    }}

    /* Global text visibility fix */
    label, p, span, h1, h2, h3, .stMarkdown div {{
        color: {text_color} !important;
    }}

    /* Professional Header */
    .brand-header {{
        background: linear-gradient(135deg, #D4AF37 0%, #8A6D3B 100%);
        padding: 40px 10px;
        border-radius: 0 0 40px 40px;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.4);
        margin-bottom: 25px;
    }}

    /* Container Styling */
    .stForm {{
        background: {card_bg} !important;
        backdrop-filter: blur(15px);
        border: 1px solid {accent}44 !important;
        border-radius: 25px !important;
        padding: 25px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2) !important;
    }}

    /* Input Styling */
    .stTextInput input, .stSelectbox div, .stTextArea textarea, .stNumberInput input {{
        background-color: rgba(255,255,255,0.05) !important;
        border: 1px solid {accent}55 !important;
        color: {text_color} !important;
        border-radius: 12px !important;
        font-size: 16px !important;
    }}

    /* Bottom Sticky Nav Fix */
    .nav-container {{
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background: {card_bg};
        border-top: 2px solid {accent};
        padding: 10px 0;
        z-index: 999;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 6. DATA LOGIC ---
DB_FILE = "deliveries.csv"
def load_data():
    if os.path.exists(DB_FILE): 
        return pd.read_csv(DB_FILE, dtype={"phone": str})
    return pd.DataFrame(columns=["date", "customer", "shop", "phone", "area", "address", "shop_addr", "price", "status", "user_email"])

# --- 7. PAGE ROUTING ---

# HOME PAGE
if st.session_state.page == "home":
    st.markdown(f'<div class="brand-header"><h1 style="color:white; margin:0;">{L["title"]}</h1></div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="text-align: center; padding: 30px; max-width: 900px; margin: auto;">
        <h2 style="color:{accent};">Kirkuk's Trusted Delivery Expert</h2>
        <p style="font-size: 1.25rem; line-height: 1.6;">{L["desc"]}</p>
        <div style="display: flex; justify-content: space-around; margin-top: 40px;">
            <div style="font-size: 1.1rem;">⚡ Fast Delivery</div>
            <div style="font-size: 1.1rem;">🛡️ Safe Handling</div>
            <div style="font-size: 1.1rem;">💎 Golden Quality</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ORDER PAGE
elif st.session_state.page == "order":
    st.markdown(f'<h2 style="text-align:center; color:{accent}; padding-top:10px;">{L["nav_order"]}</h2>', unsafe_allow_html=True)
    st.markdown(f'<p style="text-align:center;">{L["free_info"]}</p>', unsafe_allow_html=True)
    
    df = load_data()
    phone_input = st.text_input(f"📞 {L['phone']}", placeholder="07xx xxx xxxx")
    
    is_free = False
    if phone_input:
        user_orders = len(df[df['phone'] == phone_input])
        is_free = (user_orders + 1) % 3 == 0
        if is_free:
            st.balloons()
            st.success(L["free_success"])

    with st.form("professional_order_form"):
        c1, c2 = st.columns(2)
        with c1:
            customer = st.text_input(L['customer_name'])
            shop = st.text_input(L['shop_name'])
            area = st.selectbox(L['area'], ["-- Select Area --"] + KIRKUK_AREAS)
        with c2:
            shop_addr = st.text_input(L['shop_addr'])
            full_addr = st.text_area(L['full_addr'])
            price = st.number_input(L['price'], value=0 if is_free else 3000, step=250)
        
        if st.form_submit_button(L['submit'], use_container_width=True):
            if customer and phone_input and "--" not in area:
                new_row = pd.DataFrame([{
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "customer": customer, "shop": shop, "phone": phone_input, "area": area, 
                    "address": full_addr, "shop_addr": shop_addr, "price": price, 
                    "status": "Pending", "user_email": st.session_state.user_email
                }])
                pd.concat([df, new_row]).to_csv(DB_FILE, index=False)
                st.success("✅ Order Successfully Registered!")
            else:
                st.error("⚠️ Please fill in all mandatory fields.")

# ACCOUNT PAGE
elif st.session_state.page == "profile":
    st.markdown(f'<h2 style="text-align:center; color:{accent}; padding-top:10px;">{L["nav_profile"]}</h2>', unsafe_allow_html=True)
    
    with st.container():
        if st.session_state.user_email is None:
            st.markdown(f"<div style='text-align:center;'>", unsafe_allow_html=True)
            if st.button(L["google_btn"], use_container_width=True):
                st.session_state.user_email = "verified_user@gmail.com"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.success(f"Verified Account: {st.session_state.user_email}")
            if st.button(L["logout"], use_container_width=True):
                st.session_state.user_email = None
                st.rerun()
            
            st.divider()
            # Admin Section
            admin_pwd = st.text_input("Admin Password", type="password")
            if admin_pwd == "golden2024":
                st.dataframe(load_data(), use_container_width=True)

# --- 8. STICKY BOTTOM NAVIGATION ---
st.markdown("<br><br><br><br>", unsafe_allow_html=True)
nav_cols = st.columns(3)
with nav_cols[0]:
    if st.button(f"🏠 {L['nav_home']}", use_container_width=True):
        st.session_state.page = "home"
        st.rerun()
with nav_cols[1]:
    if st.button(f"🚚 {L['nav_order']}", use_container_width=True):
        st.session_state.page = "order"
        st.rerun()
with nav_cols[2]:
    if st.button(f"👤 {L['nav_profile']}", use_container_width=True):
        st.session_state.page = "profile"
        st.rerun()

