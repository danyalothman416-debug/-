import streamlit as st
import pandas as pd
import os
import urllib.parse

# --- 1. ڕێکخستنی لاپەڕە و دیزاین ---
st.set_page_config(page_title="Golden Delivery", layout="wide")

st.markdown("""
    <style>
    /* سڕینەوەی تەواوەتی Sidebar بۆ ئەوەی کۆدەکە دیار نەبێت */
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    .stAppDeployButton {
        display: none !important;
    }
    html, body, [data-testid="stAppViewContainer"] {
        direction: rtl;
        text-align: right;
    }
    .brand-header {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #D4AF37;
        text-align: center;
        margin-bottom: 20px;
    }
    .brand-title {
        color: #D4AF37;
        font-size: 32px;
        font-weight: bold;
    }
    .num-fix {
        direction: ltr !important;
        display: inline-block !important;
        unicode-bidi: bidi-override !important;
    }
    .footer-text {
        text-align: center;
        font-size: 14px;
        color: #888;
        margin-top: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

ADMIN_PASSWORD = "dr_danyal_2024" 
DB_FILE = "global_deliveries.csv"
MY_WHATSAPP = "9647721959922"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["کڕیار", "ناوی دوکان", "ناونیشانی دوکان", "مۆبایل", "نرخ", "ناونیشانی کڕیار"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

# --- 2. ڕووکاری سەرەکی (بۆ هەمووان) ---
st.markdown("""
    <div class="brand-header">
        <div class="brand-title">GOLDEN DELIVERY ✨ گۆڵدن دێلیڤەری</div>
        <div style="font-size: 18px; color: #333; margin-top:10px;">
            <b>خێراترین و باوەڕپێکراوترین خزمەتگوزاری گەیاندن لە کەرکوک.</b><br>
            <b>أسرع وأكثر خدمة توصيل موثوقة في كركوك.</b>
        </div>
    </div>
""", unsafe_allow_html=True)

with st.form("delivery_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        customer = st.text_input("ناوی کڕیار / اسم الزبون")
        shop_name = st.text_input("ناوی دوکان / اسم المحل")
        shop_address = st.text_input("ناونیشانی دوکان / عنوان المحل")
        price = st.number_input("نرخی کاڵا / سعر البضاعة", min_value=0, step=250)
    with col2:
        phone = st.text_input("ژمارەی مۆبایل / رقم الهاتف")
        customer_address = st.text_input("ناونیشانی کڕیار / عنوان الزبون بالتفصيل")
    
    submit = st.form_submit_button("ناردنی وەسڵ / ارسال الوصل ✅")
    
    if submit:
        if not customer or not shop_name or not shop_address or not phone or not customer_address:
            st.error("⚠️ تکایە هەموو خانەکان پڕ بکەرەوە / يرجى ملء جميع الحقول")
        else:
            current_df = load_data()
            new_row = pd.DataFrame([{
                "کڕیار": customer, 
                "ناوی دوکان": shop_name, 
                "ناونیشانی دوکان": shop_address, 
                "مۆبایل": phone, 
                "نرخ": price, 
                "ناونیشانی کڕیار": customer_address
            }])
            save_data(pd.concat([current_df, new_row], ignore_index=True))
            
            message = (f"Golden Delivery ✨\n📦 وەسڵێکی نوێ\n"
                       f"👤 کڕیار: {customer}\n"
                       f"🏪 دوکان: {shop_name}\n"
                       f"📍 ناونیشانی دوکان: {shop_address}\n"
                       f"💰 نرخ: {price:,} د.ع\n"
                       f"📞 مۆبایل: {phone}\n"
                       f"🏘 ناونیشانی کڕیار: {customer_address}")
            
            encoded_msg = urllib.parse.quote(message)
            whatsapp_link = f"https://wa.me/{MY_WHATSAPP}?text={encoded_msg}"
            
            st.success("✅ وەسڵەکە تۆمارکرا / تم تسجيل الوصل")
            st.markdown(f'<a href="{whatsapp_link}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:12px; border-radius:8px; font-weight:bold; cursor:pointer;">ناردنی کۆتایی بۆ WhatsApp 💬</button></a>', unsafe_allow_html=True)

# ژمارە تەلەفۆنەکان
st.markdown("""
    <div class="footer-text">
        📞 <span class="num-fix">0772 195 9922</span> | <span class="num-fix">0780 135 2003</span>
    </div>
""", unsafe_allow_html=True)

st.write("---")

# --- 3. بەشی بەڕێوەبەر (شاراوە لە خوارەوەی خوارەوە) ---
with st.expander("🛠 بەشی کارگێڕی (تەنها بۆ خاوەن کار)"):
    admin_pwd = st.text_input("کۆدی نهێنی", type="password", key="admin_key")
    if admin_pwd == ADMIN_PASSWORD:
        st.write("### 📋 لیستی وەسڵەکان")
        df = load_data()
        st.dataframe(df, use_container_width=True)
        if st.button("🗑 سڕینەوەی هەموو داتاکان"):
            save_data(pd.DataFrame(columns=["کڕیار", "ناوی دوکان", "ناونیشانی دوکان", "مۆبایل", "نرخ", "ناونیشانی کڕیار"]))
            st.rerun()
    elif admin_pwd:
        st.error("کۆدەکە هەڵەیە!")
