import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import uuid
import json
import plotly.express as px
from streamlit_option_menu import option_menu

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Golden Delivery Pro", 
    layout="wide", 
    initial_sidebar_state="collapsed",
    page_icon="🚚"
)

# --- 2. INITIALIZE SESSION STATES ---
def init_session_states():
    defaults = {
        'page': "home",
        'user_email': None,
        'user_role': "customer",
        'user_name': None,
        'user_phone': None,
        'admin_authenticated': False,
        'lang_choice': "English 🇬🇧",
        'theme_choice': "Dark 🌙",
        'driver_id': None,
        'current_order_id': None
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_states()

# --- 3. COMPANY INFO ---
COMPANY_PHONES = ["07801352003", "07721959922"]
COMPANY_EMAIL = "Danyalexpert@gmail.com"  # Updated email
COMPANY_ADDRESS = "Kirkuk, Iraq"
COMPANY_WHATSAPP = "https://wa.me/9647801352003"

# --- 4. MULTI-LANGUAGE UI STRINGS ---
languages = {
    "English 🇬🇧": {
        "dir": "ltr", 
        "align": "left",
        # Navigation
        "nav_home": "Home", 
        "nav_order": "Order", 
        "nav_track": "Track",
        "nav_offers": "Offers", 
        "nav_profile": "Account", 
        "nav_terms": "Terms",
        "nav_support": "Support",
        # Rest of your English strings...
        "title": "GOLDEN DELIVERY PRO",
        "desc": "Experience the gold standard of logistics in Kirkuk.",
        # Add all other English strings from your original code
    },
    "کوردی 🇭🇺": {
        "dir": "rtl", 
        "align": "right",
        # Navigation
        "nav_home": "سەرەکی", 
        "nav_order": "داواکردن", 
        "nav_track": "شوێنکەوتن",
        "nav_offers": "پێشکەشکراوەکان", 
        "nav_profile": "هەژمار", 
        "nav_terms": "یاساکان",
        "nav_support": "پاڵپشتی",
        # Rest of your Kurdish strings...
        "title": "گۆڵدن دلیڤەری پرۆ",
        "desc": "بەرزترین کوالێتی گەیاندن لە کەرکوک.",
        # Add all other Kurdish strings
    },
    "العربية 🇮🇶": {
        "dir": "rtl", 
        "align": "right",
        # Navigation
        "nav_home": "الرئيسية", 
        "nav_order": "طلب", 
        "nav_track": "تتبع",
        "nav_offers": "العروض", 
        "nav_profile": "الحساب", 
        "nav_terms": "الشروط",
        "nav_support": "الدعم",
        # Rest of your Arabic strings...
        "title": "جولدن دليفري برو",
        "desc": "المعيار الذهبي للخدمات اللوجستية في كركوك.",
        # Add all other Arabic strings
    }
}

# --- 5. NEIGHBORHOODS LIST (Keep your complete list) ---
KIRKUK_AREAS = sorted([
    "Arfa / عرفة", "Tis'in / تسعين", "Shoraw / شوراو", 
    "Rahim Awa / رحيماوة", "Quraya / قورية", "Al-Wasiti / الواسطي",
    "Al-Nasr / النصر", "Azadi / ازادي", "Wahid Huzairan / واحد حزيران",
    "Kirkuk Citadel / قلعة كركوك", "Musalla / مصلى", "Imam Qasim / امام قاسم",
    "Shorija / الشورجة", "Hasiraka / حصيرةكة", "Tapai Malla Abdulla / تبة ملا عبدulla",
    "Rahimawa / رحيم آوه", "Almas / الماس", "Arafa / عرفة",
    "Faylaq / فيلق", "Panja Ali / بنجة علي", "Darwaza / دروازة",
    "Kurdistan Neighborhood / حي كردستان", "Baghdad Road / طريق بغداد",
    "Wasit / واسط", "Domiz / دوميز", "June 1st / ١ حزيران",
    "Majidiya / المجيدية", "Al-Beiji / البيجي", "Mansour / المنصور",
    "Razgari / رزگاري", "Ghazna / غزنة", "Hay Aden / حي عدن",
    "Taseen / تسعين", "Khazra / خضراء", "Beiji / بيجي",
    "Qadisiyah / قادسية", "Panorama / بانوراما", "Barutkhana / باروته خانه",
    "Engineers Neighborhood / حي المهندسين", "Teachers Neighborhood / حي المعلمين",
    "Al-Mas / المس", "Al-Mithaq / الميثاق", "Al-Ta'mim / التأميم",
    "Al-Qadisiyah / القادسية", "Al-Jamea / الجامعة", "Al-Muhandiseen / المهندسين",
    "Al-Andalus / الأندلس", "Al-Jumhouriya / الجمهورية", "Domeez / دوميز",
    "Al-Wafa / الوفاء", "Al-Nour / النور", "Al-Muthanna / المثنى",
    "Al-Khadra / الخضراء", "Sarchinar / سرچنار", "Muhammad Ali / محمد علي",
    "Al-Mashtal / المشتل", "Al-Shuhada / الشهداء", "Al-Hurriya / الحرية",
    "Al-Sina'a / الصناعة", "Al-Masbin / المسبين", "Al-Sa'ad / السعد",
    "Bakhtiari / بختياري", "Bawer / باور", "Camp / مخيم",
    "Chay / جاي", "Choman / جومان", "Hasar / حصر",
    "Kani Askan / كاني عسكر", "Kani Qrzhala / كاني قرژالة", "Laylan / ليلان",
    "Rizgary / رزگاري", "Taza / طازة", "Yarmuk / يرموك", "Zab / زاب"
])

# --- 6. DATA FILES (Keep all your data functions) ---
ORDERS_FILE = "orders.csv"
DRIVERS_FILE = "drivers.csv"
CUSTOMERS_FILE = "customers.csv"
FEEDBACK_FILE = "feedback.csv"
PROMO_CODES_FILE = "promos.json"

# [Include all your data loading/saving functions here - load_orders(), save_orders(), etc.]

# --- 7. IMPROVED TOP BAR WITH SETTINGS ---
# Get current language
L = languages[st.session_state.lang_choice]

# Create a clean top bar
top_col1, top_col2, top_col3 = st.columns([2, 1, 1])
with top_col1:
    st.markdown(f"<h2 style='color:#D4AF37; margin:0;'>{L['title']}</h2>", unsafe_allow_html=True)
with top_col2:
    # Language selector - FIXED to actually change language
    lang_options = list(languages.keys())
    current_lang_index = lang_options.index(st.session_state.lang_choice)
    selected_lang = st.selectbox(
        "🌐", 
        lang_options, 
        index=current_lang_index,
        label_visibility="collapsed",
        key="lang_selector"
    )
    if selected_lang != st.session_state.lang_choice:
        st.session_state.lang_choice = selected_lang
        st.rerun()
with top_col3:
    # Theme toggle - FIXED to work properly
    theme_options = ["Light ☀️", "Dark 🌙"]
    current_theme_index = 0 if st.session_state.theme_choice == "Light ☀️" else 1
    selected_theme = st.selectbox(
        "🎨", 
        theme_options, 
        index=current_theme_index,
        label_visibility="collapsed",
        key="theme_selector"
    )
    if selected_theme != st.session_state.theme_choice:
        st.session_state.theme_choice = selected_theme
        st.rerun()

# Update L after potential language change
L = languages[st.session_state.lang_choice]

# --- 8. IMPROVED CSS WITH FIXED DARK MODE ---
is_dark = st.session_state.theme_choice == "Dark 🌙"

# Enhanced color scheme with better contrast
if is_dark:
    main_bg = "#0a0c10"
    card_bg = "#1e2329"
    text_color = "#ffffff"
    text_secondary = "#e0e0e0"  # Lighter gray for better visibility
    accent = "#D4AF37"
    input_bg = "#2d333d"
    border_color = "#3a404c"
    dropdown_bg = "#2d333d"
    dropdown_text = "#ffffff"
else:
    main_bg = "#f5f7fa"
    card_bg = "#ffffff"
    text_color = "#1a1a2e"
    text_secondary = "#2d3748"
    accent = "#D4AF37"
    input_bg = "#ffffff"
    border_color = "#e0e0e0"
    dropdown_bg = "#ffffff"
    dropdown_text = "#1a1a2e"

# Comprehensive CSS with fixed dark mode
st.markdown(f"""
<style>
    /* Hide sidebar */
    [data-testid="stSidebar"] {{ display: none; }}
    
    /* Main container */
    html, body, [data-testid="stAppViewContainer"], 
    .main, .block-container, .stApp {{
        background-color: {main_bg} !important;
        color: {text_color} !important;
    }}
    
    /* Base text colors */
    h1, h2, h3, h4, h5, h6, p, span, div, label, .stMarkdown {{
        color: {text_color} !important;
    }}
    
    /* Secondary text (subtitles, hints) */
    .secondary-text, .stCaption, .stMarkdown small {{
        color: {text_secondary} !important;
    }}
    
    /* Input fields - FIXED for dark mode */
    input, textarea, .stTextInput input, .stTextArea textarea {{
        background-color: {input_bg} !important;
        color: {text_color} !important;
        border: 1px solid {border_color} !important;
    }}
    
    /* Select boxes - FIXED for dark mode */
    .stSelectbox div[data-baseweb="select"] {{
        background-color: {input_bg} !important;
        border-color: {border_color} !important;
    }}
    
    .stSelectbox div[data-baseweb="select"] span {{
        color: {text_color} !important;
    }}
    
    /* Dropdown menu - FIXED for dark mode */
    div[data-baseweb="menu"] {{
        background-color: {dropdown_bg} !important;
        border: 1px solid {border_color} !important;
    }}
    
    div[data-baseweb="menu"] li {{
        background-color: {dropdown_bg} !important;
        color: {dropdown_text} !important;
    }}
    
    div[data-baseweb="menu"] li:hover {{
        background-color: {accent}30 !important;
    }
    
    /* Form container */
    .stForm {{
        background-color: {card_bg} !important;
        border: 1px solid {accent}40 !important;
        border-radius: 20px !important;
        padding: 30px !important;
    }}
    
    /* Glass card */
    .glass-card {{
        background-color: {card_bg} !important;
        border-radius: 20px !important;
        padding: 25px !important;
        border: 1px solid {accent}30 !important;
        margin-bottom: 20px !important;
        color: {text_color} !important;
    }}
    
    /* Brand header */
    .brand-header {{
        background: linear-gradient(135deg, #D4AF37 0%, #8A6D3B 100%);
        padding: 30px;
        border-radius: 0 0 30px 30px;
        text-align: center;
        margin-bottom: 20px;
    }}
    
    .brand-header h1, .brand-header p {{
        color: white !important;
    }}
    
    /* Buttons */
    .stButton button {{
        background-color: {accent} !important;
        color: {text_color if is_dark else '#000000'} !important;
        border: none !important;
        font-weight: bold !important;
        border-radius: 10px !important;
        padding: 10px 20px !important;
        transition: all 0.3s !important;
    }}
    
    .stButton button:hover {{
        background-color: {accent}dd !important;
        transform: translateY(-2px) !important;
    }}
    
    /* Info boxes */
    .stAlert {{
        background-color: {card_bg} !important;
        color: {text_color} !important;
        border-left-color: {accent} !important;
    }}
    
    /* Success message */
    .stSuccess {{
        background-color: {card_bg} !important;
        color: #00C851 !important;
    }}
    
    /* Expander */
    .streamlit-expanderHeader {{
        background-color: {card_bg} !important;
        color: {text_color} !important;
    }}
    
    /* DataFrames */
    .dataframe, .stDataFrame, .stDataFrame div {{
        color: {text_color} !important;
    }}
    
    .dataframe td, .dataframe th {{
        background-color: {card_bg} !important;
        color: {text_color} !important;
        border-color: {border_color} !important;
    }}
    
    /* Metrics */
    [data-testid="stMetricValue"] {{
        color: {accent} !important;
        font-size: 2rem !important;
    }}
    
    /* Card title */
    .card-title {{
        color: {accent} !important;
        font-size: 1.5rem !important;
    }}
    
    /* Contact info in footer */
    .footer-contact {{
        background-color: {card_bg} !important;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin-top: 30px;
    }}
    
    .phone-number {{
        color: {accent} !important;
        font-weight: bold;
        margin: 0 10px;
    }}
    
    /* Direction handling */
    [dir="{L['dir']}"] {{
        text-align: {L['align']} !important;
    }}
</style>
""", unsafe_allow_html=True)

# --- 9. CLEAN, PROFESSIONAL NAVIGATION MENU ---
# Create a styled navigation menu
selected = option_menu(
    menu_title=None,
    options=[
        L['nav_home'], 
        L['nav_order'], 
        L['nav_track'], 
        L['nav_offers'], 
        L['nav_profile'], 
        L['nav_terms'], 
        L['nav_support']
    ],
    icons=['house-door', 'box', 'geo-alt', 'gift', 'person', 'file-text', 'headset'],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {
            "padding": "0!important", 
            "background-color": "transparent",
            "max-width": "1000px",
            "margin": "0 auto",
            "display": "flex",
            "justify-content": "center",
            "gap": "5px"
        },
        "icon": {"color": accent, "font-size": "16px"},
        "nav-link": {
            "font-size": "15px", 
            "text-align": "center", 
            "margin": "0px 2px",
            "padding": "10px 15px",
            "border-radius": "30px",
            "color": text_color,
            "background-color": card_bg,
            "transition": "all 0.3s"
        },
        "nav-link:hover": {
            "background-color": f"{accent}20",
            "transform": "translateY(-2px)"
        },
        "nav-link-selected": {
            "background-color": accent,
            "color": "black",
            "font-weight": "bold"
        },
    }
)

# Map selection to page
page_mapping = {
    L['nav_home']: "home",
    L['nav_order']: "order",
    L['nav_track']: "track",
    L['nav_offers']: "offers",
    L['nav_profile']: "profile",
    L['nav_terms']: "terms",
    L['nav_support']: "support"
}
st.session_state.page = page_mapping.get(selected, "home")

# --- 10. PAGE CONTENT ---
# [Insert all your page content here - home, order, track, offers, profile, terms, support]
# Keep all your existing page code, just remove the old top contact bar

# --- 11. CLEAN FOOTER WITH CONTACT INFO ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(f"""
<div class="footer-contact">
    <p style="margin-bottom: 10px;">📞 <span class="phone-number">{COMPANY_PHONES[0]}</span> | <span class="phone-number">{COMPANY_PHONES[1]}</span></p>
    <p>✉️ {COMPANY_EMAIL} | 📍 {COMPANY_ADDRESS}</p>
    <p style="font-size: 0.9rem; opacity: 0.8;">© 2024 Golden Delivery Pro - All rights reserved</p>
</div>
""", unsafe_allow_html=True)
