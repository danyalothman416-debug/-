import streamlit as st
import pandas as pd
import os
import urllib.parse
from datetime import datetime
from fpdf import FPDF
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Golden Delivery",layout="wide")

DB="orders.csv"

# ---------------- Database ----------------

def load_orders():
    if os.path.exists(DB):
        return pd.read_csv(DB)
    return pd.DataFrame(columns=[
        "time","customer","phone","area",
        "address","price","status","driver",
        "lat","lon"
    ])

def save_orders(df):
    df.to_csv(DB,index=False)

df=load_orders()

# ---------------- Header ----------------

st.title("GOLDEN DELIVERY ✨")
st.caption("Professional Delivery System - Kirkuk")

# ---------------- Dashboard ----------------

col1,col2,col3,col4=st.columns(4)

with col1:
    st.metric("Total Orders",len(df))

with col2:
    if not df.empty:
        st.metric("Revenue",int(df["price"].sum()))
    else:
        st.metric("Revenue",0)

with col3:
    if not df.empty:
        delivered=len(df[df["status"]=="Delivered"])
        st.metric("Delivered",delivered)
    else:
        st.metric("Delivered",0)

with col4:
    if not df.empty:
        pending=len(df[df["status"]=="Pending"])
        st.metric("Pending",pending)
    else:
        st.metric("Pending",0)

st.divider()

# ---------------- New Order ----------------

st.subheader("➕ New Order")

with st.form("order_form"):

    col1,col2=st.columns(2)

    with col1:
        customer=st.text_input("Customer Name")
        phone=st.text_input("Phone")
        area=st.text_input("Area")

    with col2:
        address=st.text_input("Address")
        price=st.number_input("Price",0)
        driver=st.text_input("Driver")

    st.write("Location (optional)")

    col3,col4=st.columns(2)

    with col3:
        lat=st.number_input("Latitude",0.0)

    with col4:
        lon=st.number_input("Longitude",0.0)

    submit=st.form_submit_button("Add Order")

    if submit:

        new=pd.DataFrame([{
            "time":datetime.now(),
            "customer":customer,
            "phone":phone,
            "area":area,
            "address":address,
            "price":price,
            "status":"Pending",
            "driver":driver,
            "lat":lat,
            "lon":lon
        }])

        df=pd.concat([df,new])

        save_orders(df)

        msg=f"""
Golden Delivery ✨

Customer: {customer}
Phone: {phone}
Area: {area}
Address: {address}
Price: {price} IQD
"""

        wa=f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}"

        st.success("Order Added")

        st.link_button("Send WhatsApp",wa)

st.divider()

# ---------------- Search ----------------

st.subheader("🔎 Search Orders")

search=st.text_input("Search by Customer or Phone")

if search:
    df=df[
        df["customer"].astype(str).str.contains(search,case=False) |
        df["phone"].astype(str).str.contains(search,case=False)
    ]

# ---------------- Orders List ----------------

st.subheader("📦 Orders")

for i,row in df.iterrows():

    with st.expander(f"{row['customer']} - {row['area']}"):

        st.write("📞 Phone:",row["phone"])
        st.write("🏠 Address:",row["address"])
        st.write("💰 Price:",row["price"])
        st.write("🚚 Driver:",row["driver"])
        st.write("📊 Status:",row["status"])

        col1,col2,col3=st.columns(3)

        with col1:

            status=st.selectbox(
                "Change Status",
                ["Pending","On the Way","Delivered"],
                index=["Pending","On the Way","Delivered"].index(row["status"]),
                key=i
            )

            if st.button("Update Status",key=f"u{i}"):

                df.loc[i,"status"]=status
                save_orders(df)

                st.success("Updated")

        with col2:

            if st.button("Generate Receipt",key=f"p{i}"):

                pdf=FPDF()

                pdf.add_page()

                pdf.set_font("Arial",size=14)

                pdf.cell(200,10,"Golden Delivery Receipt",ln=True)

                pdf.cell(200,10,f"Customer: {row['customer']}",ln=True)
                pdf.cell(200,10,f"Phone: {row['phone']}",ln=True)
                pdf.cell(200,10,f"Area: {row['area']}",ln=True)
                pdf.cell(200,10,f"Price: {row['price']}",ln=True)

                file=f"receipt_{i}.pdf"

                pdf.output(file)

                with open(file,"rb") as f:
                    st.download_button(
                        "Download PDF",
                        f,
                        file
                    )

        with col3:

            if row["lat"]!=0 and row["lon"]!=0:

                m=folium.Map(
                    location=[row["lat"],row["lon"]],
                    zoom_start=15
                )

                folium.Marker(
                    [row["lat"],row["lon"]],
                    tooltip="Customer"
                ).add_to(m)

                st_folium(m,width=400)

st.divider()

# ---------------- Statistics ----------------

st.subheader("📊 Statistics")

if not df.empty:

    chart=df.groupby("status").size()

    st.bar_chart(chart)

st.divider()

# ---------------- Footer ----------------

st.markdown(
"""
<center>

Golden Delivery System  
Developed for Delivery Management

</center>
""",
unsafe_allow_html=True
)
