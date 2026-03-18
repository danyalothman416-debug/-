import streamlit as st
import pandas as pd
import os
from datetime import datetime
import uuid
import urllib.parse
import folium
from streamlit_folium import st_folium

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Golden Delivery", layout="wide")

DB_FILE = "deliveries.csv"

# ---------------- LANGUAGE SYSTEM ----------------
LANG = {
    "English": {
        "dir": "ltr",
        "title": "Golden Delivery",
        "home": "Home",
        "track": "Track",
        "profile": "Profile",
        "name": "Customer Name",
        "phone": "Phone Number",
        "area": "Area",
        "address": "Address",
        "submit": "Submit Order",
        "track_title": "Track Order",
        "status": "Status"
    },
    "العربية": {
        "dir": "rtl",
        "title": "جولدن دليفري",
        "home": "الرئيسية",
        "track": "تتبع",
        "profile": "الحساب",
        "name": "اسم الزبون",
        "phone": "رقم الهاتف",
        "area": "المنطقة",
        "address": "العنوان",
        "submit": "إرسال الطلب",
        "track_title": "تتبع الطلب",
        "status": "الحالة"
    },
    "کوردی": {
        "dir": "rtl",
        "title": "گۆڵدن دلیڤەری",
        "home": "سەرەکی",
        "track": "شوێنکەوتن",
        "profile": "هەژمار",
        "name": "ناوی کڕیار",
        "phone": "ژمارە",
        "area": "گەڕەک",
        "address": "ناونیشان",
        "submit": "ناردن",
        "track_title": "شوێنکەوتنی داواکاری",
        "status": "دۆخ"
    }
}

# ---------------- STATE ----------------
if "lang" not in st.session_state:
    st.session_state.lang = "English"

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

if "page" not in st.session_state:
    st.session_state.page = "home"

L = LANG[st.session_state.lang]

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("⚙️ Settings")

    st.session_state.lang = st.selectbox("Language", list(LANG.keys()))

    st.session_state.theme = st.radio("Theme", ["light", "dark"])

    st.divider()
    st.subheader("📄 About App")
    st.write("Golden Delivery - Kirkuk")

    st.subheader("⚖️ Policy")
    st.write("All deliveries follow local regulations.")

# ---------------- DARK MODE ----------------
if st.session_state.theme == "dark":
    bg = "#0e1117"
    text = "#ffffff"
else:
    bg = "#ffffff"
    text = "#000000"

st.markdown(f"""
<style>
body {{
    background-color:{bg};
    color:{text};
}}
</style>
""", unsafe_allow_html=True)

# ---------------- DATA ----------------
def load():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE, dtype={"phone": str})
    return pd.DataFrame(columns=["id","name","phone","area","address","status"])

def save(df):
    df.to_csv(DB_FILE, index=False)

# ---------------- KIRKUK AREAS ----------------
AREAS = [
    "Rahimawa","Iskan","Azadi","Baghdad Road","Taseen",
    "Wasit","Kurdistan","Musalla","Arafa","Domiz",
    "Huzairan","Panja Ali","Shoraw","Yaychi","Laylan"
]

AREA_COORDS = {
    "Rahimawa":[35.49,44.39],
    "Iskan":[35.48,44.39],
    "Azadi":[35.47,44.40],
    "Arafa":[35.48,44.35],
    "Domiz":[35.42,44.38]
}

# ---------------- GPS ----------------
st.markdown("""
<script>
navigator.geolocation.getCurrentPosition(function(pos){
    console.log(pos.coords.latitude, pos.coords.longitude);
});
</script>
""", unsafe_allow_html=True)

# ---------------- HOME ----------------
if st.session_state.page == "home":

    st.title(L["title"])

    with st.form("form"):
        name = st.text_input(L["name"])
        phone = st.text_input(L["phone"])
        area = st.selectbox(L["area"], AREAS)
        address = st.text_input(L["address"])

        if st.form_submit_button(L["submit"]):

            df = load()

            order_id = str(uuid.uuid4())[:8]

            new = pd.DataFrame([{
                "id":order_id,
                "name":name,
                "phone":phone,
                "area":area,
                "address":address,
                "status":"Pending"
            }])

            df = pd.concat([df,new])
            save(df)

            msg = f"Order {order_id} - {name}"
            url = f"https://wa.me/?text={urllib.parse.quote(msg)}"

            st.success(f"Saved ✅ ID: {order_id}")
            st.markdown(f"[Send WhatsApp]({url})")

# ---------------- TRACK ----------------
elif st.session_state.page == "track":

    st.subheader(L["track_title"])

    order = st.text_input("ID")

    if order:
        df = load()
        res = df[df["id"] == order]

        if not res.empty:
            st.success(res.iloc[0]["status"])

# ---------------- PROFILE ----------------
elif st.session_state.page == "profile":

    st.subheader("Profile")

    phone = st.text_input("Phone")

    if phone:
        df = load()
        user = df[df["phone"] == phone]

        st.write(user)

# ---------------- MAP ----------------
st.divider()

m = folium.Map(location=[35.47,44.39], zoom_start=12)

for name, coord in AREA_COORDS.items():
    folium.Marker(coord, popup=name).add_to(m)

st_folium(m)

# ---------------- MOBILE NAV ----------------
st.markdown("<br><br><br>", unsafe_allow_html=True)

col1,col2,col3 = st.columns(3)

with col1:
    if st.button("🏠"):
        st.session_state.page="home"
        st.rerun()

with col2:
    if st.button("🔍"):
        st.session_state.page="track"
        st.rerun()

with col3:
    if st.button("👤"):
        st.session_state.page="profile"
        st.rerun()
