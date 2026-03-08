import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from datetime import datetime

# ڕێکخستنی شێوەی ئەپەکە
st.set_page_config(page_title="سیستەمی گەیاندن", page_icon="📦", layout="centered")

# ستایلی کوردی (ڕاست بۆ چەپ)
st.markdown("""
    <style>
    .main { text-align: right; direction: rtl; }
    div.stButton > button:first-child { background-color: #00ff00; color: white; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

st.title("📦 سیستەمی تۆمارکردنی داواکاری")
st.subheader("تایبەت بە گەنجانی خاوەن بزنس")

# دروستکردنی فۆڕمی وەرگرتنی زانیاری
with st.form("delivery_form"):
    name = st.text_input("ناوی کڕیار:")
    phone = st.text_input("ژمارەی مۆبایل:")
    item = st.text_input("جۆری کاڵا:")
    price = st.number_input("کۆی گشتی پارە (دینار):", value=0, step=250)
    
    st.write("📍 لۆکەیشنی کڕیار لەسەر نەخشە دیاری بکە:")
    
    # دروستکردنی نەخشە
    m = folium.Map(location=[35.56, 45.42], zoom_start=12)
    m.add_child(folium.LatLngPopup())
    
    # پیشاندانی نەخشە
    map_data = st_folium(m, height=350, width=700)
    
    submit = st.form_submit_button("تۆمارکردنی داواکاری ✅")

# ئەنجامی کلیک کردن
if submit:
    if map_data['last_clicked']:
        lat = map_data['last_clicked']['lat']
        lng = map_data['last_clicked']['lng']
        time_now = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        st.success(f"داواکارییەکە بۆ {name} تۆمارکرا!")
        
        # دروستکردنی لینکی گوگڵ ماپ بۆ شۆفێر
        g_link = f"https://www.google.com/maps?q={lat},{lng}"
        
        # پیشاندانی زانیارییەکان
        res = {
            "کاتی تۆمارکردن": [time_now],
            "ناو": [name],
            "مۆبایل": [phone],
            "کاڵا": [item],
            "پارە": [price]
        }
        st.table(pd.DataFrame(res))
        st.markdown(f"🔗 [بۆ بینینی لۆکەیشن لێرە کلیک بکە]({g_link})")
    else:
        st.error("⚠️ تکایە سەرەتا شوێنەکە لەسەر نەخشەکە دیاری بکە!")
