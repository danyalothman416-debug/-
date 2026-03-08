import streamlit as st
import pandas as pd

st.title("سیستەمی گەیاندنی کەرکوک 🚀")

# دروستکردنی فۆڕمی وەرگرتنی زانیاری
with st.form("delivery_form"):
    customer_name = st.text_input("ناوی کڕیار")
    phone = st.text_input("ژمارەی مۆبایل")
    address = st.selectbox("گەڕەک", ["ڕێگای بەغدا", "ئیسکان", "ڕەحیماوا", "واسطی", "پەنجە عەلی"])
    price = st.number_input("نرخی کاڵا (دینار)", value=0)
    delivery_fee = st.number_input("کرێی گەیاندن", value=5000)
    
    submitted = st.form_submit_button("تۆمارکردن")

# پاشەکەوتکردنی داتا (بۆ تاقیکردنەوە لێرەدا تەنها نیشانی دەدەین)
if submitted:
    st.success(f"وەسڵی {customer_name} بە سەرکەوتوویی تۆمارکرا!")
    st.write(f"کۆی گشتی وەرگیراو: {price + delivery_fee} دینار")
