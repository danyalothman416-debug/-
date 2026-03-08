import streamlit as st
import pandas as pd
import os
import urllib.parse

# --- 1. ڕێکخستنی لاپەڕە ---
st.set_page_config(page_title="Golden Delivery", layout="wide")

# CSS بۆ سڕینەوەی Sidebar و ڕاستکردنەوەی ژمارەکان
st.markdown("""
    <style>
    /* سڕینەوەی Sidebar و هەموو نیشانەکانی لای ڕاست و چەپ */
    [data-testid="stSidebar"], [data-testid="collapsedControl"] {
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
        unicode-bidi: bidi-override !important;
        display: inline-block !important;
    }
    .footer-text {
        text-align: center;
        font-size: 13px;
        color: #888;
        margin-top: 50px;
    }
    </style>
    """, unsafe_allow_html=True)

ADMIN_PASSWORD = "dr_danyal_2024" 
DB_FILE = "global_deliveries.csv"
MY_WHATSAPP = "9647721959922"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["کڕیار", "دوکان", "مۆبایل", "نرخ", "ناونیشان"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

# --- 2. ڕووکاری سەرەکی (تەنها فۆرمەکە لێرەیە) ---
st.markdown("""
    <div class="brand-header">
        <div class="brand-title">GOLDEN DELIVERY ✨ گۆڵدن دێلیڤەری</div>
        <div style="font-size: 16px; color: #555; margin-top:10px;">
            خێراترین و باوەڕپێکراوترین خزمەتگوزاری گەیاندن لە کەرکوک<br>
            أسرع وأكثر خدمة توصيل موثوقة في كركوك
        </div>
    </div>
""", unsafe_allow_html=True)

# فۆرمی تۆمارکردن
with st.form("delivery_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        customer = st.text_input("ناوی کڕیار / اسم الزبون")
        shop = st.text_input("ناوی دوکان / اسم المحل")
        price = st.number_input("نرخی کاڵا / سعر البضاعة", min_value=0, step=250)
    with col2:
        phone = st.text_input("ژمارەی مۆبایل / رقم الهاتف")
        address = st.text_input("ناونیشانی ورد / العنوان بالتفصيل")
    
    submit = st.form_submit_button("ناردنی وەسڵ / ارسال الوصل ✅")
    
    if submit:
        if not customer or not shop or not phone or not address:
            st.error("⚠️ تکایە هەموو خانەکان پڕ بکەرەوە")
        else:
            current_df = load_data()
            new_row = pd.DataFrame([{"کڕیار": customer, "دوکان": shop, "مۆبایل": phone, "نرخ": price, "ناونیشان": address}])
            save_data(pd.concat([current_df, new_row], ignore_index=True))
            
            message = f"Golden Delivery ✨\n📦 وەسڵێکی نوێ\n👤 کڕیار: {customer}\n🏪 دوکان: {shop}\n💰 نرخ: {price:,} د.ع\n📍 ناونیشان: {address}"
            encoded_msg = urllib.parse.quote(message)
            whatsapp_link = f"https://wa.me/{MY_WHATSAPP}?text={encoded_msg}"
            
            st.success("✅ وەسڵەکە تۆمارکرا.")
            st.markdown(f'<a href="{whatsapp_link}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:12px; border-radius:8px; font-weight:bold; cursor:pointer;">ناردنی کۆتایی بۆ WhatsApp 💬</button></a>', unsafe_allow_html=True)

# ژمارەکان لە خوارەوە بە ڕێکی
st.markdown("""
    <div class="footer-text">
        📞 <span class="num-fix">0772 195 9922</span> | <span class="num-fix">0780 135 2003</span>
    </div>
""", unsafe_allow_html=True)

st.write("---")

# --- 3. بەشی ئەدمین (شاراوە لە خوارەوەی هەموو شتێک) ---
with st.expander("🛠 بەشی کارگێڕی (بۆ خاوەن کار)"):
    admin_pass = st.text_input("کۆدی نهێنی بنووسە", type="password")
    if admin_pass == ADMIN_PASSWORD:
        st.write("### 📋 لیستی گشت وەسڵەکان")
        df_admin = load_data()
        st.dataframe(df_admin, use_container_width=True)
        if st.button("🗑 سڕینەوەی هەموو داتاکان"):
            save_data(pd.DataFrame(columns=["کڕیار", "دوکان", "مۆبایل", "نرخ", "ناونیشان"]))
            st.rerun()
    elif admin_pass:
        st.error("کۆدەکە هەڵەیە!")
