import streamlit as st
import pandas as pd
import os
import urllib.parse
from datetime import datetime
import plotly.express as px
import folium
from streamlit_folium import st_folium
import uuid

st.set_page_config(page_title="Golden Delivery", layout="wide")

DB_FILE = "deliveries.csv"

# ------------------ LOAD DATA ------------------
def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE, dtype={"phone": str})
    return pd.DataFrame(columns=[
        "id","date","customer","shop","phone","area",
        "address","shop_addr","price","status"
    ])

# ------------------ SAVE ------------------
def save_data(df):
    df.to_csv(DB_FILE, index=False)

# ------------------ HEADER ------------------
st.title("🚚 GOLDEN DELIVERY")

# ------------------ PAGE STATE ------------------
if "page" not in st.session_state:
    st.session_state.page = "home"

# ------------------ AREAS ------------------
AREA_COORDS = {
    "Rahimawa":[35.4950,44.3910],
    "Iskan":[35.4820,44.3980],
    "Azadi":[35.4750,44.4050],
}

# ------------------ HOME ------------------
if st.session_state.page == "home":

    with st.form("form"):
        name = st.text_input("Name")
        phone = st.text_input("Phone")
        area = st.selectbox("Area", list(AREA_COORDS.keys()))
        address = st.text_input("Address")
        price = st.number_input("Price", value=3000)

        submit = st.form_submit_button("Submit")

        if submit:
            if not name or not phone:
                st.error("Fill all fields")
            else:
                df = load_data()

                order_id = str(uuid.uuid4())[:8]

                new = pd.DataFrame([{
                    "id":order_id,
                    "date":datetime.now(),
                    "customer":name,
                    "shop":"",
                    "phone":phone,
                    "area":area,
                    "address":address,
                    "shop_addr":"",
                    "price":price,
                    "status":"Pending"
                }])

                df = pd.concat([df,new])
                save_data(df)

                # WhatsApp message
                msg = f"Order ID: {order_id}\nName:{name}\nPhone:{phone}\nArea:{area}\nPrice:{price}"
                url = f"https://wa.me/9647XXXXXXXX?text={urllib.parse.quote(msg)}"

                st.success(f"Order Saved ✅ ID: {order_id}")
                st.markdown(f"[📲 Send WhatsApp]({url})")

# ------------------ TRACK ------------------
elif st.session_state.page == "track":

    st.subheader("🔍 Track Order")

    track_id = st.text_input("Enter Order ID")

    if track_id:
        df = load_data()
        result = df[df["id"] == track_id]

        if not result.empty:
            st.success(result.iloc[0]["status"])
        else:
            st.error("Not found")

# ------------------ ADMIN ------------------
elif st.session_state.page == "admin":

    if st.text_input("Password", type="password") == "admin123":
        df = load_data()

        st.dataframe(df)

        # Chart
        chart = df["status"].value_counts()
        fig = px.pie(values=chart.values, names=chart.index, title="Orders Status")
        st.plotly_chart(fig)

        # Map
        m = folium.Map(location=[35.47,44.39], zoom_start=12)

        for _, row in df.iterrows():
            if row["area"] in AREA_COORDS:
                folium.Marker(
                    location=AREA_COORDS[row["area"]],
                    popup=row["customer"]
                ).add_to(m)

        st_folium(m, width=700)

# ------------------ NAV ------------------
col1,col2,col3 = st.columns(3)

with col1:
    if st.button("🏠 Home"):
        st.session_state.page="home"
        st.rerun()

with col2:
    if st.button("🔍 Track"):
        st.session_state.page="track"
        st.rerun()

with col3:
    if st.button("🛠 Admin"):
        st.session_state.page="admin"
        st.rerun()
