import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# --- Page config ---
st.set_page_config(page_title="گەیاندنی کەرکوک 🚚", layout="wide")

# --- RTL Style ---
st.markdown("""
<style>
.stApp {direction: rtl; text-align: right;}
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.title("🏢 بەڕێوەبەرایەتی")
st.sidebar.write("🧪 خوێندکاری شیکاری")
st.sidebar.write("🚗 بەرپرسی گەیاندن: کاک عەلی")

# --- Database in memory ---
if "deliveries" not in st.session_state:
    st.session_state["deliveries"] = []

st.title("📍 سیستەمی گەیاندنی کەرکوک")

# --- Add delivery ---
with st.expander("➕ تۆمارکردنی وەسڵ"):
    with st.form("delivery_form"):

        customer = st.text_input("ناوی کڕیار")
        shop = st.text_input("ناوی دوکان")
        phone = st.text_input("ژمارەی مۆبایل")
        price = st.number_input("نرخ", min_value=0)

        lat = st.number_input("Latitude", value=35.4676, format="%.6f")
        lon = st.number_input("Longitude", value=44.3921, format="%.6f")

        submit = st.form_submit_button("تۆمارکردن")

        if submit:

            if customer == "":
                st.error("ناوی کڕیار پێویستە")
            else:

                st.session_state["deliveries"].append({
                    "کڕیار": customer,
                    "دوکان": shop,
                    "مۆبایل": phone,
                    "نرخ": price,
                    "lat": lat,
                    "lon": lon
                })

                st.success("وەسڵ بە سەرکەوتوویی تۆمارکرا")

# --- Show map ---
if len(st.session_state["deliveries"]) > 0:

    st.subheader("🗺 نەخشە")

    m = folium.Map(location=[35.4676,44.3921], zoom_start=12)

    for d in st.session_state["deliveries"]:

        folium.Marker(
            location=[d["lat"], d["lon"]],
            popup=f"{d['کڕیار']} - {d['نرخ']}",
            tooltip=d["کڕیار"]
        ).add_to(m)

    st_folium(m, width=700, height=500)

    st.subheader("📋 لیستی وەسڵەکان")

    df = pd.DataFrame(st.session_state["deliveries"])
    st.dataframe(df)

    if st.button("پاککردنەوەی هەموو"):
        st.session_state["deliveries"] = []
        st.experimental_rerun()

else:
    st.info("هێشتا هیچ وەسڵێک تۆمار نەکراوە")
