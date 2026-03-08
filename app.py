import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from datetime import datetime

# ڕێکخستنی لاپەڕەکە
st.set_page_config(page_title="Delivery System", page_icon="📦")

st.title("📦 سیستەمی گەیاندنی زیرەک")
st.write("زانیارییەکانی کڕیار و شوێنەکەی تۆمار بکە")

# دروستکردنی فۆڕم بۆ زانیارییەکان
with st.form("my_form"):
    col1, col2 = st.columns(2)
    with col1:
        customer_name = st.text_input("ناوی کڕیار")
        phone_number = st.text_input("ژمارەی مۆبایل")
    with col2:
        item_type = st.text_input("جۆری کاڵا")
        price = st.number_input("نرخی گەیاندن (دینار)", value=5000, step=500)

    st.write("📍 لۆکەیشنی کڕیار لەسەر نەخشە دیاری بکە:")
    
    # دروستکردنی نەخشەی سەرەتایی (ناوەندی کوردستان)
    m = folium.Map(location=[35.56, 45.42], zoom_start=12)
    m.add_child(folium.LatLngPopup()) # بۆ ئەوەی لۆکەیشن پیشان بدات کاتێک کلیک دەکەیت
    
    # پیشاندانی نەخشەکە لەناو ئەپەکەدا
    map_data = st_folium(m, height=350, width=700)
    
    submitted = st.form_submit_button("تۆمارکردنی داواکاری")

# ئەگەر دوگمەی تۆمارکردن داگیرا
if submitted:
    if map_data['last_clicked']:
        lat = map_data['last_clicked']['lat']
        lng = map_data['last_clicked']['lng']
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # پیشاندانی ئەنجام بۆ بەکارهێنەر
        st.success(f"✅ داواکارییەکەی {customer_name} بە سەرکەوتووی تۆمارکرا!")
        
        # دروستکردنی خشتەیەک بۆ زانیارییەکان
        data = {
            "کاتی تۆمارکردن": [current_time],
            "ناوی کڕیار": [customer_name],
            "مۆبایل": [phone_number],
            "کاڵا": [item_type],
            "Latitude": [lat],
            "Longitude": [lng]
        }
        df = pd.DataFrame(data)
        st.table(df)
        
        # دروستکردنی لینکی Google Maps بۆ ئەوەی شۆفێرەکە بەکاری بهێنێت
        google_maps_link = f"https://www.google.com/maps?q={lat},{lng}"
        st.markdown(f"🔗 [کردنەوەی لۆکەیشن لە Google Maps]({google_maps_link})")
    else:
        st.error("⚠️ تکایە سەرەتا خاڵێک لەسەر نەخشەکە دیاری بکە بۆ لۆکەیشن!")

