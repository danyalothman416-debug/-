import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# -------- Page Config --------
st.set_page_config(
    page_title="سیستەمی گەیاندنی کەرکوک 🚚",
    layout="wide"
)

# -------- Kurdish RTL Style --------
st.markdown("""
<style>

.stApp{
direction:rtl;
text-align:right;
font-size:18px;
}

h1,h2,h3{
text-align:center;
}

.block-container{
padding-top:2rem;
}

</style>
""", unsafe_allow_html=True)

# -------- Sidebar --------
with st.sidebar:
    st.title("🏢 بەڕێوەبەرایەتی")
    st.write("🧪 خوێندکاری شیکاری")
    st.write("🚚 بەرپرسی گەیاندن: کاک عەلی")
    st.divider()
    st.info("سیستەمی بەڕێوەبردنی وەسڵەکانی کەرکوک")

# -------- Database --------
if "deliveries" not in st.session_state:
    st.session_state.deliveries = []

# -------- Title --------
st.title("🚚 سیستەمی گەیاندنی زیرەکی کەرکوک")

# -------- Add Delivery --------
with st.expander("➕ تۆمارکردنی وەسڵی نوێ"):

    with st.form("delivery_form"):

        col1, col2 = st.columns(2)

        with col1:
            customer = st.text_input("ناوی کڕیار")
            shop = st.text_input("ناوی دوکان")
            price = st.number_input("نرخی کاڵا", min_value=0)

        with col2:
            phone = st.text_input("ژمارەی مۆبایل")
            lat = st.number_input("Latitude", value=35.4676, format="%.6f")
            lon = st.number_input("Longitude", value=44.3921, format="%.6f")

        submit = st.form_submit_button("تۆمارکردن")

        if submit:

            st.session_state.deliveries.append({
                "کڕیار":customer,
                "دوکان":shop,
                "مۆبایل":phone,
                "نرخ":price,
                "lat":lat,
                "lon":lon
            })

            st.success("وەسڵ بە سەرکەوتوویی تۆمارکرا ✅")

# -------- Map --------
if st.session_state.deliveries:

    st.subheader("🗺 نەخشەی گەیاندن")

    m = folium.Map(location=[35.4676,44.3921], zoom_start=12)

    for d in st.session_state.deliveries:

        folium.Marker(
            [d["lat"], d["lon"]],
            popup=f"""
            کڕیار: {d['کڕیار']} <br>
            دوکان: {d['دوکان']} <br>
            نرخ: {d['نرخ']}
            """,
            tooltip=d["کڕیار"]
        ).add_to(m)

    st_folium(m, height=500, width=900)

    st.subheader("📋 لیستی وەسڵەکان")

    df = pd.DataFrame(st.session_state.deliveries)

    st.dataframe(df,use_container_width=True)

    if st.button("🗑 پاککردنەوەی هەموو وەسڵەکان"):
        st.session_state.deliveries=[]
        st.experimental_rerun()

else:

    st.info("هێشتا هیچ وەسڵێک تۆمار نەکراوە")
