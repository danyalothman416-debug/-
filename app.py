import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os
import urllib.parse

# --- 1. ڕێکخستنی لاپەڕە ---
st.set_page_config(page_title="سیستەمی گەیاندنی کەرکوک", layout="wide")

st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        direction: rtl;
        text-align: right;
    }
    /* بچووککردنەوەی فۆنتی ژمارە تەلەفۆنەکان لە خوارەوە */
    .footer-text {
        text-align: center;
        font-size: 14px;
        color: #555;
        margin-top: 30px;
        border-top: 1px solid #eee;
        padding-top: 10px;
    }
    .phone-number {
        direction: ltr !important;
        display: inline-block;
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

# --- 2. لۆژیکی گەڕانەوە ---
if "back_to_home" in st.session_state and st.session_state.back_to_home:
    st.session_state.clear()
    st.rerun()

# --- 3. شریتی لای ڕاست (تەنها خانەی کۆد) ---
with st.sidebar:
    password = st.text_input("", type="password", placeholder="...", key="admin_pwd")

# --- 4. لاپەڕەی سەرەکی ---
if password == ADMIN_PASSWORD:
    st.header("👨‍⚕️ بەشی بەڕێوەبەر / قسم المدير")
    df_to_show = load_data()
    if not df_to_show.empty:
        st.table(df_to_show) 
        if st.button("🗑 سڕینەوە / مسح"):
            save_data(pd.DataFrame(columns=["کڕیار", "دوکان", "مۆبایل", "نرخ", "ناونیشان"]))
            st.rerun()
        if st.button("⬅️ گەڕانەوە"):
            st.session_state.back_to_home = True
            st.rerun()
    else:
        st.info("هیچ وەسڵێک نییە.")
        if st.button("⬅️ گەڕانەوە"):
            st.session_state.back_to_home = True
            st.rerun()
else:
    # لاپەڕەی کڕیار
    st.title("📦 فۆرمی تۆمارکردنی وەسڵ / استمارة الوصل")
    
    # فۆرمی وەسڵەکە
    with st.form("delivery_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            customer = st.text_input("ناوی کڕیار / اسم الزبون")
            shop = st.text_input("ناوی دوکان / اسم المحل")
            price = st.number_input("نرخی کاڵا / سعر البضاعة", min_value=0, step=250)
        with col2:
            phone = st.text_input("ژمارەی مۆبایل / رقم الهاتف")
            address = st.text_input("ناونیشانی ورد / العنوان بالتفصيل")
        
        # دوگمەی ناردن ڕێک لە ژێر خانەکانە
        submit = st.form_submit_button("ناردنی وەسڵ / ارسال الوصل ✅")
        
        if submit:
            if not customer or not shop or not phone or not address:
                st.error("⚠️ تکایە هەموو خانەکان پڕ بکەرەوە")
            else:
                current_df = load_data()
                new_row = pd.DataFrame([{"کڕیار": customer, "دوکان": shop, "مۆبایل": phone, "نرخ": price, "ناونیشان": address}])
                save_data(pd.concat([current_df, new_row], ignore_index=True))
                
                # ئامادەکردنی لینک بۆ واتسئەپ
                message = f"وەسڵێکی نوێ 📦\n👤 کڕیار: {customer}\n🏪 دوکان: {shop}\n💰 نرخ: {price:,} د.ع\n📞 مۆبایل: {phone}\n📍 ناونیشان: {address}"
                encoded_msg = urllib.parse.quote(message)
                whatsapp_link = f"https://wa.me/{MY_WHATSAPP}?text={encoded_msg}"
                
                st.success("✅ وەسڵەکە تۆمارکرا.")
                st.markdown(f'<a href="{whatsapp_link}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:12px; border-radius:8px; font-weight:bold; cursor:pointer;">کرتە بکە بۆ ناردنی کۆتایی (WhatsApp)</button></a>', unsafe_allow_html=True)

    # ژمارە تەلەفۆنەکان لە خوارەوەی هەموو شتێک بە بچووکی
    st.markdown("""
        <div class="footer-text">
            پەیوەندی: 
            <span class="phone-number">0772 195 9922</span> | 
            <span class="phone-number">0780 135 2003</span>
        </div>
    """, unsafe_allow_html=True)
