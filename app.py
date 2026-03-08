import streamlit as st
import pandas as pd
import os
import urllib.parse

# --- دیزاینی شیک و گەرەنتی کراو ---
st.set_page_config(page_title="Golden Delivery", layout="wide")

st.markdown("""
    <style>
    section[data-testid="stSidebar"] { display: none !important; }
    html, body, [data-testid="stAppViewContainer"] {
        direction: rtl;
        text-align: right;
    }
    .brand-header {
        background: linear-gradient(135deg, #1a1a1a 0%, #333333 100%);
        padding: 25px;
        border-radius: 15px;
        border-bottom: 4px solid #D4AF37;
        text-align: center;
        margin-bottom: 20px;
    }
    .brand-title { color: #D4AF37; font-size: 30px; font-weight: bold; }
    .brand-desc { color: #ffffff; font-size: 15px; }
    .num-fix { direction: ltr !important; display: inline-block !important; color: #D4AF37; font-weight: bold; }
    .footer-text { text-align: center; background-color: #1a1a1a; color: white; padding: 15px; border-radius: 10px; margin-top: 30px; }
    </style>
    """, unsafe_allow_html=True)

ADMIN_PASSWORD = "dr_danyal_2024" 
DB_FILE = "global_deliveries.csv"
MY_WHATSAPP = "9647721959922"

def load_data():
    if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["کڕیار", "ناوی دوکان", "ناونیشانی دوکان", "مۆبایل", "نرخ", "ناونیشانی کڕیار"])

def save_data(df): df.to_csv(DB_FILE, index=False)

# --- ڕووکاری سەرەکی ---
st.markdown("""
    <div class="brand-header">
        <div class="brand-title">GOLDEN DELIVERY ✨</div>
        <div class="brand-desc">
            خێراترین و باوەڕپێکراوترین گەیاندن لە کەرکوک<br>
            أسرع وأكثر خدمة توصيل موثوقة في كركوك
        </div>
    </div>
""", unsafe_allow_html=True)

with st.form("delivery_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        customer = st.text_input("👤 ناوی کڕیار / اسم الزبون")
        shop_name = st.text_input("🏪 ناوی دوکان / اسم المحل")
        shop_address = st.text_input("📍 ناونیشانی دوکان / عنوان المحل")
    with col2:
        phone = st.text_input("📞 ژمارەی مۆبایل / رقم الهاتف")
        customer_address = st.text_input("🏘 ناونیشانی کڕیار / عنوان الزبون")
        price = st.number_input("💰 نرخ / السعر", min_value=0, step=250)
    
    submit = st.form_submit_button("تۆمارکردن و ناردنی وەسڵ ✅")
    
    if submit:
        if not customer or not shop_name or not shop_address or not phone or not customer_address:
            st.error("⚠️ تکایە هەموو خانەکان پڕ بکەرەوە")
        else:
            df = load_data()
            new_row = pd.DataFrame([{"کڕیار": customer, "ناوی دوکان": shop_name, "ناونیشانی دوکان": shop_address, "مۆبایل": phone, "نرخ": price, "ناونیشانی کڕیار": customer_address}])
            save_data(pd.concat([df, new_row], ignore_index=True))
            
            msg = f"Golden Delivery ✨\n📦 وەسڵێکی نوێ\n👤 کڕیار: {customer}\n🏪 دوکان: {shop_name}\n📍 ناونیشانی دوکان: {shop_address}\n💰 نرخ: {price:,} د.ع\n📞 مۆبایل: {phone}\n🏘 ناونیشانی کڕیار: {customer_address}"
            link = f"https://wa.me/{MY_WHATSAPP}?text={urllib.parse.quote(msg)}"
            st.success("✅ تۆمارکرا")
            st.markdown(f'<a href="{link}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:12px; border-radius:10px; font-weight:bold; cursor:pointer;">ناردن بۆ واتسئەپ 💬</button></a>', unsafe_allow_html=True)

st.markdown(f'<div class="footer-text">📞 <span class="num-fix">0772 195 9922</span> | <span class="num-fix">0780 135 2003</span></div>', unsafe_allow_html=True)

with st.expander("🛠 بەشی کارگێڕی"):
    if st.text_input("کۆد", type="password") == ADMIN_PASSWORD:
        st.dataframe(load_data())
        if st.button("🗑 سڕینەوە"):
            save_data(pd.DataFrame(columns=["کڕیار", "ناوی دوکان", "ناونیشانی دوکان", "مۆبایل", "نرخ", "ناونیشانی کڕیار"]))
            st.rerun()
