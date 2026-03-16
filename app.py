import streamlit as st
import pandas as pd
import os
import urllib.parse
from datetime import datetime
import plotly.express as px
import folium
from streamlit_folium import st_folium

# --- 1. ڕێکخستنی لاپەڕە ---
st.set_page_config(page_title="Golden Delivery", layout="wide", initial_sidebar_state="collapsed")

# پاراستنی لاپەڕەی ئێستا (بۆ ئەوەی وەک ئەپ خێرا بێت)
if 'page' not in st.session_state:
    st.session_state.page = "home"

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
        "status_pending": "⏳ چاوەڕوان", "status_onway": "🚚 لە ڕێگەیە", "status_delivered": "✅ گەیشت",
        "nav_home": "🏠 سەرەکی", "nav_discount": "🏷️ داشکاندن", "nav_profile": "👤 هەژمار",
        "free_msg": "🎁 پیرۆزە! تۆ ٣ گەیاندنت هەبووە، ئەمەیان بە خۆڕاییە!",
        "need_more": "ماوەتە بۆ گەیاندنی خۆڕایی: ",
        "acc_info": "زانیاری هەژمار"
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
        "status_pending": "⏳ قيد الانتظار", "status_onway": "🚚 في الطريق", "status_delivered": "✅ تم التوصيل",
        "nav_home": "🏠 الرئيسية", "nav_discount": "🏷️ الخصومات", "nav_profile": "👤 الحساب",
        "free_msg": "🎁 مبروك! لديك ٣ توصيلات سابقة، هذا التوصيل مجاني!",
        "need_more": "متبقي للتوصيل المجاني: ",
        "acc_info": "معلومات الحساب"
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
        "status_pending": "⏳ Pending", "status_onway": "🚚 On the way", "status_delivered": "✅ Delivered",
        "nav_home": "🏠 Home", "nav_discount": "🏷️ Discounts", "nav_profile": "👤 Account",
        "free_msg": "🎁 Congrats! You had 3 deliveries, this one is FREE!",
        "need_more": "Remaining for free delivery: ",
        "acc_info": "Account Info"
    }
}

# --- ٢. هەڵبژاردنی زمان و ڕووکار ---
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

# --- ٣. بارکردنی داتا ---
DB_FILE = "deliveries.csv"
def load_data():
    if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE, dtype={"phone": str})
    return pd.DataFrame(columns=["date", "customer", "shop", "phone", "area", "address", "shop_addr", "price", "status"])

# --- ٤. ستایل (بەشە مۆدێرنەکە) ---
st.markdown(f"""
    <style>
    [data-testid="stHeader"] {{visibility: hidden;}}
    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}}
    
    html, body, [data-testid="stAppViewContainer"] {{ 
        direction: {L['dir']}; text-align: {L['align']};
        background-color: {bg_color}; color: {text_color};
    }}

    /* Header */
    .brand-header {{ 
        background: linear-gradient(135deg, #D4AF37 0%, #8A6D3B 100%); 
        padding: 40px 20px; border-radius: 0 0 30px 30px; 
        text-align: center; margin-bottom: 30px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }}
    .brand-title {{ color: white; font-size: 32px; font-weight: bold; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }}

    /* Form UI */
    .stForm {{ border: none !important; border-radius: 20px; padding: 20px; background-color: {card_bg} !important; box-shadow: 0 10px 25px rgba(0,0,0,0.05); }}
    label {{ color: #D4AF37 !important; font-weight: 600 !important; font-size: 15px !important; }}
    
    /* Modern Bottom Navigation */
    .nav-container {{
        position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%);
        width: 90%; max-width: 500px;
        background: {"rgba(30, 30, 30, 0.9)" if is_dark else "rgba(255, 255, 255, 0.9)"};
        backdrop-filter: blur(10px);
        display: flex; justify-content: space-around; align-items: center;
        padding: 12px 10px; border-radius: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        z-index: 9999;
        border: 1px solid rgba(212, 175, 55, 0.3);
    }}
    .nav-link {{
        text-decoration: none; color: {text_color};
        display: flex; flex-direction: column; align-items: center;
        transition: 0.3s all ease; flex: 1;
    }}
    .nav-item-active {{ color: #D4AF37 !important; font-weight: bold; transform: translateY(-5px); }}
    .nav-icon {{ font-size: 22px; margin-bottom: 2px; }}
    .nav-text {{ font-size: 11px; }}

    /* Hide Streamlit default button styles in Nav */
    div.stButton > button {{
        background: transparent; border: none; color: inherit; padding: 0; height: auto; width: 100%;
    }}
    div.stButton > button:hover {{ background: transparent; color: #D4AF37; }}
    </style>
    """, unsafe_allow_html=True)

# --- ٥. لۆژیکی لاپەڕەکان ---
if st.session_state.page == "offers":
    st.markdown(f'<div class="brand-header"><div class="brand-title">{L["nav_discount"]}</div></div>', unsafe_allow_html=True)
    phone_check = st.text_input(L['phone'], placeholder="07xx xxx xxxx")
    if phone_check:
        df = load_data()
        count = len(df[df['phone'] == phone_check])
        if count >= 3:
            st.balloons()
            st.success(L['free_msg'])
        else:
            st.info(f"{L['need_more']} {3 - count}")

elif st.session_state.page == "profile":
    st.markdown(f'<div class="brand-header"><div class="brand-title">{L["nav_profile"]}</div></div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.subheader(L['acc_info'])
        user_p = st.text_input(L['phone'])
        if user_p:
            df = load_data()
            user_data = df[df['phone'] == user_p].tail(1)
            if not user_data.empty:
                st.write(f"👤 {L['customer_name']}: {user_data.iloc[0]['customer']}")
                st.write(f"📍 {L['area']}: {user_data.iloc[0]['area']}")
            else:
                st.warning("No data found")

else: # Home Page
    st.markdown(f'<div class="brand-header"><div class="brand-title">{L["title"]}</div><div style="color:white; opacity: 0.9;">{L["subtitle"]}</div></div>', unsafe_allow_html=True)
    
    AREA_COORDS = {
        "ڕەحیماوا / رحيماوة / Rahimawa": [35.4950, 44.3910],
        "ئیسکان / اسكان / Iskan": [35.4820, 44.3980],
        "ئازادی / ازادي / Azadi": [35.4750, 44.4050],
        "ڕێگای بەغداد / طريق بغداد / Baghdad Road": [35.4520, 44.3680],
        "تسعین / تسعين / Taseen": [35.4510, 44.3750],
        "واسطی / واسطي / Wasit": [35.4180, 44.3620],
        "کوردستان / كوردستان / Kurdistan": [35.5050, 44.4010],
        "موسەڵا / مصلى / Musalla": [35.4650, 44.3950],
        "عرفە / عرفة / Arafa": [35.4880, 44.3550],
        "دۆمیز / دوميز / Domiz": [35.4250, 44.3850],
        "حوزەیران / حزيران / Huzairan": [35.4150, 44.3750],
        "پەنجاعەلی / بنجة علي / Panja Ali": [35.4650, 44.4350]
    }
    NEARBY_AREAS = ["کوردستان / كوردستان / Kurdistan", "ڕەحیماوا / رحيماوة / Rahimawa", "ئیسکان / اسكان / Iskan", "ئازادی / ازادي / Azadi"]
    KIRKUK_AREAS = sorted(list(AREA_COORDS.keys()))

    with st.form("delivery_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            customer = st.text_input(L['customer_name'])
            shop = st.text_input(L['shop_name'])
            shop_addr = st.text_input(L['shop_addr'])
        with c2:
            phone = st.text_input(L['phone'], placeholder="07xx xxx xxxx")
            selected_area = st.selectbox(L['area'], ["Select..."] + KIRKUK_AREAS)
            default_price = 3000 if selected_area in NEARBY_AREAS else 4000 if selected_area != "Select..." else 0
            price = st.number_input(L['price'], min_value=0, step=250, value=default_price)
        
        full_addr = st.text_input(L['full_addr'])
        submit = st.form_submit_button(L['submit'])
        
        if submit:
            if not customer or not phone or "Select" in selected_area:
                st.error("⚠️ Please fill all fields")
            else:
                df = load_data()
                new_row = pd.DataFrame([{"date": datetime.now().strftime("%Y-%m-%d"), "customer": customer, "shop": shop, "phone": phone, "area": selected_area, "address": full_addr, "shop_addr": shop_addr, "price": price, "status": L['status_pending']}])
                pd.concat([df, new_row]).to_csv(DB_FILE, index=False)
                st.success("✅ Registered Successfully")

# --- ٦. پانێڵی ئەدمین (وەک خۆی مۆدەکەت) ---
if st.query_params.get("role") == "boss":
    st.divider()
    if st.text_input(L['admin_pass'], type="password") == "golden2024":
        data = load_data()
        st.dataframe(data, use_container_width=True)

# --- ٧. دروستکردنی Bottom NavBar بە دوگمەی Streamlit ---
# ئەم بەشە وادەکات کلیکەکە کاریگەر بێت و لاپەڕەکان بگۆڕێت
st.markdown("<br><br><br><br><br>", unsafe_allow_html=True) # بۆشایی بۆ ئەوەی ناوەڕۆک نەچێتە ژێر Nav

# دیزاینی CSS بۆ ئایکۆنەکان
nav_home_class = "nav-item-active" if st.session_state.page == "home" else ""
nav_off_class = "nav-item-active" if st.session_state.page == "offers" else ""
nav_prof_class = "nav-item-active" if st.session_state.page == "profile" else ""

# دروستکردنی کانتینەری ناو باڕ بە HTML و Button ی Streamlit لەناویدا
st.markdown(f"""
    <div class="nav-container">
        <div id="nav-prof" class="nav-link {nav_prof_class}"></div>
        <div id="nav-home" class="nav-link {nav_home_class}"></div>
        <div id="nav-off" class="nav-link {nav_off_class}"></div>
    </div>
""", unsafe_allow_html=True)

# دانانی دوگمەکان لەسەر کانتینەرەکان بە ئیفێکتێکی جوان
nav_cols = st.columns([1, 1, 1])
with nav_cols[0]:
    if st.button(L['nav_profile'], key="btn_profile"):
        st.session_state.page = "profile"
        st.rerun()
with nav_cols[1]:
    if st.button(L['nav_home'], key="btn_home"):
        st.session_state.page = "home"
        st.rerun()
with nav_cols[2]:
    if st.button(L['nav_discount'], key="btn_offers"):
        st.session_state.page = "offers"
        st.rerun()

# تێبینی: بەکارهێنانی st.session_state و st.rerun() وادەکات ئەپەکە Refresh نەبێت و تەنها ناوەڕۆکەکە بگۆڕێت
