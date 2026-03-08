import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import firebase_admin
from firebase_admin import credentials, firestore

# ---------------------------
# Firebase setup
# ---------------------------
cred = credentials.Certificate("firebase_key.json")  # place your Firebase JSON key here
firebase_admin.initialize_app(cred)
db = firestore.client()

# ---------------------------
# Page config + header
# ---------------------------
st.set_page_config(page_title="Delivery System - Kirkuk", layout="wide")
st.markdown("<div style='text-align:center; font-size:18px; color:gray;'>Developed by Dr. Danyal & Eng. Ali</div>", unsafe_allow_html=True)

# ---------------------------
# User login
# ---------------------------
st.sidebar.header("Login")
username = st.sidebar.text_input("ناوی بەکارهێنەر")
role = st.sidebar.selectbox("Role", ["Owner", "Delivery"])
login_btn = st.sidebar.button("Login")

if not username or not login_btn:
    st.warning("تکایە ناوی بەکارهێنەر هەڵبژێرە و login بکە")
    st.stop()

# ---------------------------
# Load deliveries from Firebase
# ---------------------------
def load_deliveries():
    docs = db.collection("deliveries").stream()
    deliveries = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        deliveries.append(data)
    return deliveries

def add_delivery(data):
    db.collection("deliveries").add(data)

def delete_delivery(doc_id):
    db.collection("deliveries").document(doc_id).delete()

def mark_delivered(doc_id):
    db.collection("deliveries").document(doc_id).update({"delivered": True})

deliveries = load_deliveries()

# ---------------------------
# Add delivery (Owner only)
# ---------------------------
if role == "Owner":
    with st.expander("➕ زیادکردنی وەسڵ"):
        with st.form("add_delivery_form"):
            col1, col2 = st.columns(2)
            with col1:
                customer = st.text_input("ناوی کڕیار")
                shop = st.text_input("ناوی دوکان")
                price = st.number_input("نرخی کاڵا", min_value=0)
            with col2:
                phone = st.text_input("ژمارەی مۆبایل")
                address = st.text_input("ناونیشانی کڕیار")
            submit = st.form_submit_button("زیادکردنی وەسڵ")
            if submit:
                add_delivery({
                    "کڕیار": customer,
                    "دوکان": shop,
                    "مۆبایل": phone,
                    "نرخ": price,
                    "ناونیشان": address,
                    "delivered": False
                })
                st.success("وەسڵ زیادکرا ✅")
                st.experimental_rerun()

# ---------------------------
# Map with delivery markers
# ---------------------------
st.subheader("🗺 Map with Delivery Markers")
map_center = [35.4676, 44.3921]
m = folium.Map(location=map_center, zoom_start=13, tiles="OpenStreetMap")
bounds = [map_center]

for d in deliveries:
    dest = map_center  # Default Kirkuk center (replace with geocoding for real address)
    bounds.append(dest)
    popup_text = f"""
    کڕیار: {d['کڕیار']}<br>
    دوکان: {d['دوکان']}<br>
    نرخ: {d['نرخ']}<br>
    ناونیشان: {d['ناونیشان']}<br>
    Delivered: {"✅" if d.get("delivered") else "❌"}
    """
    folium.Marker(dest, popup=popup_text, tooltip=d['کڕیار'],
                  icon=folium.Icon(color="green" if d.get("delivered") else "red",
                                   icon="shopping-cart", prefix="fa")).add_to(m)

m.fit_bounds(bounds)
st_folium(m, height=600, width=900)

# ---------------------------
# Delivery list + actions
# ---------------------------
st.subheader("📋 Delivery List")
if deliveries:
    df = pd.DataFrame(deliveries)
    st.dataframe(df[["کڕیار", "دوکان", "مۆبایل", "نرخ", "ناونیشان", "delivered"]], use_container_width=True)

    if role == "Owner":
        st.markdown("### 🗑 Owner Actions")
        for d in deliveries:
            if st.button(f"Delete {d['کڕیار']}"):
                delete_delivery(d["id"])
                st.experimental_rerun()
    elif role == "Delivery":
        st.markdown("### ✅ Mark as Delivered")
        for d in deliveries:
            if not d.get("delivered"):
                if st.button(f"Delivered {d['کڕیار']}"):
                    mark_delivered(d["id"])
                    st.experimental_rerun()
else:
    st.info("هێشتا هیچ وەسڵێک تۆمار نەکراوە")
