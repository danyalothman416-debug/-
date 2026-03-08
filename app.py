import streamlit as st
import folium
from streamlit_folium import st_folium

# دیزاینی سەرەتایی ئەپەکە
st.set_page_config(page_title="Delivery App", layout="centered")
st.title("📦 ئەپی گەیاندن - تۆمارکردنی کڕیار")

# فۆرمی زانیارییەکان
with st.form("delivery_form"):
    name = st.text_input("ناوی کڕیار:")
    phone = st.text_input("ژمارەی مۆبایل:")
    item = st.text_input("جۆری کاڵا:")
    
    st.write("📍 لۆکەیشنی کڕیار لەسەر نەخشە دیاری بکە:")
    
    # دروستکردنی نەخشەیەک (لۆکەیشنی ناوەندی سلێمانی/هەولێر وەک نموونە)
    m = folium.Map(location=[35.56, 45.42], zoom_start=12)
    m.add_child(folium.LatLngPopup()) # ڕێگە دەدات بە کلیک کردن لۆکەیشن بزانیت
    
    map_data = st_folium(m, height=300, width=700)
    
    submit = st.form_submit_button("تۆمارکردنی داواکاری")

# پاشەکەوتکردنی زانیارییەکان دوای کلیک کردن
if submit:
    if map_data['last_clicked']:
        lat = map_data['last_clicked']['lat']
        lng = map_data['last_clicked']['lng']
        
        st.success(f"✅ داواکاری بۆ {name} تۆمارکرا!")
        st.write(f"📞 مۆبایل: {phone}")
        st.write(f"📍 لۆکەیشن: {lat}, {lng}")
        
        # لێرە دەتوانیت کۆد بنووسیت بۆ پاشەکەوتکردن لە Excel یان Database
    else:
        st.warning("تکایە سەرەتا لۆکەیشنەکە لەسەر نەخشەکە دیاری بکە!")
