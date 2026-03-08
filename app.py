import streamlit as st
import pandas as pd

st.set_page_config(page_title="گەیاندنی کەرکوک 🚚", layout="wide")

st.title("سیستەمی گەیاندن و نەخشە 📍")

# دروستکردنی بنکەی داتا لەناو بەرنامەکەدا
if 'deliveries' not in st.session_state:
    st.session_state.deliveries = []

# بەشی تۆمارکردنی وەسڵی نوێ
with st.expander("📝 تۆمارکردنی وەسڵێکی نوێ"):
    with st.form("delivery_form"):
        col1, col2 = st.columns(2)
        with col1:
            customer_name = st.text_input("ناوی کڕیار")
            shop_name = st.text_input("ناوی دوکان")
            item_price = st.number_input("نرخی کاڵا", value=0)
        with col2:
            phone = st.text_input("ژمارەی مۆبایل")
            location_link = st.text_input("لینکی لۆکەیشن (Google Maps Link)")
            status = st.selectbox("دۆخی وەسڵ", ["لە چاوەڕوانیدا", "لای شۆفێرە", "گەیەندرا"])
        
        submitted = st.form_submit_button("تۆمارکردن ✅")
        if submitted:
            st.session_state.deliveries.append({
                "کڕیار": customer_name,
                "دوکان": shop_name,
                "مۆبایل": phone,
                "نرخ": item_price,
                "لۆکەیشن": location_link,
                "دۆخ": status
            })
            st.success("وەسڵەکە تۆمارکرا!")

# نیشاندانی وەسڵەکان بۆ کاک عەلی
st.subheader("📋 وەسڵەکان و لۆکەیشن")

if st.session_state.deliveries:
    for i, delivery in enumerate(st.session_state.deliveries):
        with st.container():
            col_a, col_b, col_c = st.columns([2, 1, 1])
            with col_a:
                st.write(f"👤 **{delivery['کڕیار']}** | 📞 {delivery['مۆبایل']} | 🏢 {delivery['دوکان']}")
            with col_b:
                # دوگمەی لۆکەیشن: کاتێک کاک عەلی کلیکی لێ دەکات، گۆگڵ ماپ دەبێتەوە
                if delivery['لۆکەیشن']:
                    st.link_button("📍 کردنەوەی لۆکەیشن", delivery['لۆکەیشن'])
                else:
                    st.write("📍 لۆکەیشن نییە")
            with col_c:
                st.write(f"💰 {delivery['نرخ']:,} دینار")
            st.divider()
else:
    st.info("هیچ وەسڵێک نییە.")
