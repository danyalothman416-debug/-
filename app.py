import streamlit as st
import pandas as pd
import os
import urllib.parse
from datetime import datetime
import plotly.express as px
import folium
from streamlit_folium import st_folium

# --- 1. ڕێکخستنی لاپەڕە ---
st.set_page_config(page_title="Golden Delivery", layout="wide", page_icon="✨")

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
        "status_pending": "⏳ چاوەڕوان", "status_onway": "🚚 لە ڕێگەیە", "status_delivered": "✅ گەیشت"
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
        "status_pending": "قيد الانتظار ⏳", "status_onway": "في الطريق 🚚", "status_delivered": "تم التوصيل ✅"
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
        "status_pending": "Pending ⏳", "status_onway": "On the way 🚚", "status_delivered": "Delivered ✅"
    }
}

# --- ٢. لیستی گەڕەکەکانی کەرکوک (نوێکراوە) ---
AREA_COORDS = {
    # ناوەند و نزیک
    "ئیسکان / اسكان": [35.4820, 44.3980],
    "ڕەحیماوا / رحيماوة": [35.4950, 44.3910],
    "ئازادی / ازادي": [35.4750, 44.4050],
    "قۆریە / قورية": [35.4670, 44.3880],
    "شۆرجە / شورجة": [35.4780, 44.4150],
    "موسەڵا / مصلى": [35.4650, 44.3950],
    "ئیمام قاسم / امام قاسم": [35.4850, 44.4080],
    "تسعین / تسعين": [35.4510, 44.3750],
    
    # باشوور و ڕێگای بەغداد
    "ڕێگای بەغداد / طريق بغداد": [35.4520, 44.3680],
    "واسطی / واسطي": [35.4180, 44.3620],
    "دۆمیز / دوميز": [35.4250, 44.3850],
    "حوزەیران / حزيران": [35.4150, 44.3750],
    "غرناطة / غرناطة": [35.4450, 44.3720],
    "واحد اذار / ١ اذار": [35.4280, 44.3700],
    
    # باکوور و دەوروبەر
    "کوردستان / كوردستان": [35.5050, 44.4010],
    "عەرەفە / عرفة": [35.4880, 44.3550],
    "ئەڵماس / الماس": [35.4720, 44.3780],
    "سەربازی / معسكر": [35.4920, 44.4250],
    
    # ڕۆژهەڵات و گەڕەکەکانی تر
    "پەنجاعەلی / بنجة علي": [35.4650, 44.4350],
    "فەیلق / فيلق": [35.4900, 44.4450],
    "باروتخانە / باروتخانة": [35.4820, 44.4150],
    "تەپە / تبة": [35.4880, 44.3980],
    "الحرية / الحرية": [35.4550, 44.4100]
}

# گەڕەکە نزیکەکان بۆ دیاریکردنی نرخ (3000 دینار)
NEARBY_AREAS = ["ئیسکان / اسكان", "ڕەحیماوا / رحيماوة", "ئازادی / ازادي", "قۆریە / قورية", "شۆرجە / شورجة", "موسەڵا / مصلى"]
KIRKUK_AREAS = sorted(list(AREA_COORDS.keys()))

# --- ٣. هەڵبژاردنی زمان و ڕووکار ---
col_lang, col_theme = st.columns(2)
with col_lang:
    lang_choice = st.selectbox("🌐 Language / زمان", list(languages.keys()))
    L = languages[lang_choice]
with col_theme:
    theme_choice = st.radio(L['theme_label'], [L['light'], L['dark']], horizontal=True)

is_dark = theme_choice == L['dark']
bg_color = "#0e1117" if is_dark else "#f0f2f6"
text_color = "#fafafa" if is_dark else "#31333F"
card_bg = "#161b22" if is_dark else "#ffffff"

# --- ٤. بارکردنی داتا ---
DB_FILE = "deliveries.csv"
def load_data():
    if os.path.exists(DB_FILE): 
        return pd.read_csv(DB_FILE, dtype={"phone": str})
    return pd.DataFrame(columns=["date", "customer", "shop", "phone", "area", "address", "shop_addr", "price", "status"])

# --- ٥. ستایلی CSS ---
st.markdown(f"""
    <style>
    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}} header {{visibility: hidden;}}
    html, body, [data-testid="stAppViewContainer"] {{ 
        direction: {L['dir']}; text-align: {L['align']};
        background-color: {bg_color}; color: {text_color};
    }}
    .brand-header {{ 
        background: linear-gradient(135deg, {"#1a1a1a" if is_dark else "#D4AF37"} 0%, {"#2d2d2d" if is_dark else "#f39c12"} 100%); 
        padding: 30px; border-radius: 15px; border-bottom: 5px solid #D4AF37; text-align: center; margin-bottom: 25px; 
    }}
    .brand-title {{ color: {"#D4AF37" if is_dark else "white"}; font-size: 35px; font-weight: bold; }}
    .stForm {{ border: 2px solid #D4AF37 !important; border-radius: 15px; padding: 25px; background-color: {card_bg} !important; }}
    label {{ color: #D4AF37 !important; font-weight: bold !important; }}
    </style>
    """, unsafe_allow_html=True)

st.markdown(f'<div class="brand-header"><div class="brand-title">{L["title"]}</div><div style="color:{"#e0e0e0" if is_dark else "white"};">{L["subtitle"]}</div></div>', unsafe_allow_html=True)

# --- ٦. فۆرمی تۆمارکردن ---
with st.form("delivery_form", clear_on_submit=True):
    c1, c2 = st.columns(2)
    with c1:
        customer = st.text_input(L['customer_name'])
        shop = st.text_input(L['shop_name'])
        shop_addr = st.text_input(L['shop_addr'])
    with c2:
        phone = st.text_input(L['phone'], placeholder="07xx xxx xxxx")
        selected_area = st.selectbox(L['area'], ["هەڵبژێرە..."] + KIRKUK_AREAS)
        
        # دیاریکردنی نرخ بەپێی گەڕەک
        default_price = 0
        if selected_area != "هەڵبژێرە...":
            default_price = 3000 if selected_area in NEARBY_AREAS else 4000
            
        price = st.number_input(L['price'], min_value=0, step=250, value=default_price)
    
    full_addr = st.text_input(L['full_addr'])
    submit = st.form_submit_button(L['submit'])
    
    if submit:
        if not customer or not phone or "هەڵبژێرە" in selected_area:
            st.error("⚠️ تکایە هەموو خانەکان پڕ بکەرەوە")
        else:
            df = load_data()
            new_row = pd.DataFrame([{
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"), 
                "customer": customer, 
                "shop": shop, 
                "phone": phone, 
                "area": selected_area, 
                "address": full_addr, 
                "shop_addr": shop_addr, 
                "price": price, 
                "status": L['status_pending']
            }])
            pd.concat([df, new_row]).to_csv(DB_FILE, index=False)
            st.success("✅ بەسەرکەوتوویی تۆمارکرا")
            st.rerun()

# --- ٧. بەشی بەدواداچوون (Track) ---
st.markdown(f'<div style="background:{card_bg}; padding:20px; border-radius:15px; border:1px solid #D4AF37; margin-top:30px;"><h3>{L["track_title"]}</h3>', unsafe_allow_html=True)
track_phone = st.text_input(f"{L['phone']}", key="track_input")
if st.button(L['track_btn']):
    df_track = load_data()
    res = df_track[df_track['phone'] == track_phone].tail(1)
    if not res.empty: 
        st.success(f"📍 {res.iloc[0]['customer']} | Status: **{res.iloc[0]['status']}**")
    else: 
        st.warning("داواکارییەک نەدۆزرایەوە")
st.markdown('</div>', unsafe_allow_html=True)

# --- ٨. پانێڵی بەڕێوەبەر (Admin) ---
if st.query_params.get("role") == "boss":
    st.divider()
    st.markdown(f"## {L['admin_title']}")
    if st.text_input(L['admin_pass'], type="password") == "golden2024":
        data = load_data()
        
        # --- نەخشەی ڕێدۆزی ---
        st.markdown("### 🗺️ نەخشەی گەیاندن")
        m = folium.Map(location=[35.4687, 44.3925], zoom_start=12)
        
        for i, row in data.iterrows():
            if row['area'] in AREA_COORDS:
                lat, lon = AREA_COORDS[row['area']]
                color = "green" if row['status'] == L['status_delivered'] else "orange" if row['status'] == L['status_onway'] else "red"
                
                g_maps = f"https://www.google.com/maps?q={lat},{lon}"
                
                popup_html = f"""
                <div style='font-family:Tahoma; text-align:right; direction:rtl;'>
                    <b style='color:#D4AF37;'>{row['customer']}</b><br>
                    📍 {row['area']}<br>
                    💰 {row['price']:,} د.ع<br><hr>
                    <a href='{g_maps}' target='_blank'>
                        <button style='background:#25D366; color:white; border:none; padding:10px; border-radius:5px; width:100%; cursor:pointer;'>🚗 کردنەوەی GPS</button>
                    </a>
                </div>
                """
                folium.Marker(
                    [lat, lon], 
                    popup=folium.Popup(popup_html, max_width=250), 
                    tooltip=row['customer'],
                    icon=folium.Icon(color=color, icon='info-sign')
                ).add_to(m)
        
        st_folium(m, width="100%", height=500, key="main_map")

        # --- داتا و گرافیک ---
        if not data.empty:
            st.markdown("### 📊 ئاماری گشتی")
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                st.plotly_chart(px.pie(data, names='area', title='دابەشبوونی گەڕەکەکان'), use_container_width=True)
            with col_chart2:
                st.plotly_chart(px.bar(data, x='status', title='بارودۆخی گەیاندن'), use_container_width=True)
            
            st.dataframe(data, use_container_width=True)

# --- ٩. فووتەر ---
st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown('<div style="text-align:center; color:#D4AF37; font-size:12px;">Golden Delivery System v2.0 | Kirkuk City Map Update</div>', unsafe_allow_html=True)
