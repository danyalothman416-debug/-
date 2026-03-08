import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# ---------- Page Config ----------
st.set_page_config(
    page_title="Kirkuk Delivery",
    layout="wide"
)

# ---------- Style ----------
st.markdown("""
<style>

.stApp{
direction:rtl;
text-align:right;
font-size:18px;
}

h1{
text-align:center;
}

</style>
""", unsafe_allow_html=True)

# ---------- Sidebar ----------
with st.sidebar:

    st.title("🚚 Kirkuk Delivery")

    st.write("👤 Owner: **Danyal**")
    st.write("🚗 Driver: **Ali**")

    st.divider()

    st.caption("Smart Delivery System")

# ---------- Database ----------
if "deliveries" not in st.session_state:
    st.session_state.deliveries = []

# ---------- Title ----------
st.title("📦 سیستەمی گەیاندنی کەرکوک")

# ---------- Add Delivery ----------
with st.expander("➕ تۆمارکردنی وەسڵ"):

    with st.form("delivery_form"):

        col1, col2 = st.columns(2)

        with col1:
            customer = st.text_input("ناوی کڕیار")
            shop = st.text_input("ناوی دوکان")
            price = st.number_input("نرخ", min_value=0)

        with col2:
            phone = st.text_input("مۆبایل")
            lat = st.number_input("Latitude", value=35.4676, format="%.6f")
            lon = st.number_input("Longitude", value=44.3921, format="%.6f")

        submit = st.form_submit_button("تۆمارکردن")

        if submit:

            st.session_state.deliveries.append({
                "Customer": customer,
                "Shop": shop,
                "Phone": phone,
                "Price": price,
                "lat": lat,
                "lon": lon
            })

            st.success("وەسڵ تۆمارکرا ✅")

# ---------- Map ----------
if st.session_state.deliveries:

    st.subheader("🗺 Delivery Map")

    m = folium.Map(location=[35.4676,44.3921], zoom_start=12)

    for d in st.session_state.deliveries:

        folium.Marker(
            [d["lat"], d["lon"]],
            popup=f"""
            Customer: {d['Customer']} <br>
            Shop: {d['Shop']} <br>
            Price: {d['Price']}
            """,
            tooltip=d["Customer"]
        ).add_to(m)

    st_folium(m, height=500)

    st.subheader("📋 Delivery List")

    df = pd.DataFrame(st.session_state.deliveries)

    st.dataframe(df,use_container_width=True)

    if st.button("🗑 Delete All"):
        st.session_state.deliveries=[]
        st.experimental_rerun()

else:

    st.info("هێشتا هیچ وەسڵێک تۆمار نەکراوە")
