import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# ---------- Page ----------
st.set_page_config(page_title="Kirkuk Delivery", layout="wide")

# ---------- Sidebar ----------
with st.sidebar:
    st.title("📦 Kirkuk Delivery System")
    st.info("Smart delivery system for Kirkuk")

# ---------- Database ----------
if "deliveries" not in st.session_state:
    st.session_state.deliveries = []

# ---------- Title ----------
st.title("📦 Kirkuk Delivery System")

# ---------- Add Delivery ----------
with st.expander("➕ Add Delivery"):

    with st.form("delivery_form"):

        col1, col2 = st.columns(2)

        with col1:
            customer = st.text_input("Customer Name")
            shop = st.text_input("Shop Name")
            price = st.number_input("Price", min_value=0)

        with col2:
            phone = st.text_input("Phone")

            st.markdown("**Click on the map below to select location**")
            # Create a small map for selecting Lat/Lon
            m_select = folium.Map(location=[35.4676,44.3921], zoom_start=13)

            # If there is a previous click, mark it
            if 'click_location' in st.session_state:
                folium.Marker(
                    st.session_state.click_location,
                    tooltip="Selected Location",
                    icon=folium.Icon(color='blue', icon='map-marker', prefix='fa')
                ).add_to(m_select)

            # Display map
            map_data = st_folium(m_select, height=300, width=500, returned_objects=[])

            # Capture click
            if map_data and map_data['last_clicked']:
                lat = map_data['last_clicked']['lat']
                lon = map_data['last_clicked']['lng']
                st.session_state.click_location = (lat, lon)
            else:
                # Default to Kirkuk
                lat = 35.4676
                lon = 44.3921

        submit = st.form_submit_button("Add Delivery")

        if submit:
            st.session_state.deliveries.append({
                "Customer": customer,
                "Shop": shop,
                "Phone": phone,
                "Price": price,
                "lat": lat,
                "lon": lon
            })
            st.success("Delivery added successfully ✅")

# ---------- Map ----------
if st.session_state.deliveries:

    st.subheader("🗺 Delivery Map (Kirkuk)")

    m = folium.Map(location=[35.4676,44.3921], zoom_start=13, tiles="OpenStreetMap")

    for d in st.session_state.deliveries:
        folium.Marker(
            [d["lat"], d["lon"]],
            popup=f"{d['Customer']} - {d['Price']}",
            tooltip=d["Customer"],
            icon=folium.Icon(color="red", icon="shopping-cart", prefix="fa")
        ).add_to(m)

    st_folium(m, height=500, width=900)

    st.subheader("📋 Delivery List")
    df = pd.DataFrame(st.session_state.deliveries)
    st.dataframe(df, use_container_width=True)

    if st.button("🗑 Delete All Deliveries"):
        st.session_state.deliveries = []
        st.experimental_rerun()

else:
    st.info("No deliveries yet")
