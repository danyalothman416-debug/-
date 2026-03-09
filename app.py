import streamlit as st
import pandas as pd
import os
import urllib.parse
from datetime import datetime

# --- 1. ڕێکخستنی لاپەڕە و ستایلی شاهانە ---
st.set_page_config(page_title="Golden Delivery", layout="wide")

st.markdown("""
    <style>
    section[data-testid="stSidebar"] { display: none !important; }
    html, body, [data-testid="stAppViewContainer"] { direction: rtl; text-align: right; background-color: #ffffff; }
    .brand-header {
        background: linear-gradient(135deg, #1a1a1a 0%, #333333 100%);
        padding: 25px; border-radius: 15px; border-bottom: 4px solid #D4AF37;
        text-align: center; margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    .brand-title { color: #D4AF37; font-size: 32px; font-weight: bold; }
    .num-fix { direction: ltr !important; display: inline-block !important; color: #D4AF37; font-weight: bold; }
    .stat-card {
        background-color: #1a1a1a; color: #D4AF37; padding: 15px;
        border-radius: 10px; text-align: center; border: 1px solid #D4AF37;
    }
    .install-bar {
        position: fixed; bottom: 0; left: 0; width: 100%;
        background-color: #1a1a1a; color: white; padding: 12px;
        text-align: center; border-top: 3px solid #D4AF37; z-index: 9999;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ٢. بەڕێوەبردنی داتا ---
ADMIN_PASSWORD = "dr_danyal_2024" 
DB_FILE = "global_deliveries.csv"
MY_WHATSAPP = "9647721959922"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE, dtype={"مۆبایل": str})
    return pd.DataFrame(columns=["کات", "کڕیار", "ناوی دوکان", "ناونیشانی دوکان", "مۆبایل", "نرخ", "ناونیشانی کڕیار"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

# --- ٣. ڕووکاری سەرەکی کڕیار ---
st.markdown("""
    <div class="brand-header">
        <div class="brand-title">GOLDEN DELIVERY ✨</div>
        <div style="color:white; font-size:16px; margin-top:5px;">خێراترین و باوەڕپێکراوترین گەیاندن لە کەرکوک</div>
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
        if not customer or not shop_name or not phone:
            st.error("⚠️ تکایە خانە سەرەکییەکان پڕ بکەرەوە")
        else:
            df = load_data()
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            new_row = pd.DataFrame([{
                "کات": now, "کڕیار": customer, "ناوی دوکان": shop_name, 
                "ناونیشانی دوکان": shop_address, "مۆبایل": str(phone), 
                "نرخ": price, "ناونیشانی کڕیار": customer_address
            }])
            save_data(pd.concat([df, new_row], ignore_index=True))
            
            msg = f"Golden Delivery ✨\n📦 وەسڵێکی نوێ\n👤 کڕیار: {customer}\n🏪 دوکان: {shop_name}\n💰 نرخ: {price:,} د.ع\n📞 مۆبایل: {phone}"
            link = f"https://wa.me/{MY_WHATSAPP}?text={urllib.parse.quote(msg)}"
            st.success(f"✅ تۆمارکرا لە کاتژمێر {now}")
            st.markdown(f'<a href="{link}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:15px; border-radius:10px; font-weight:bold; cursor:pointer; font-size:18px;">ناردن بۆ WhatsApp 💬</button></a>', unsafe_allow_html=True)

st.markdown(f'<div style="text-align:center; padding:20px; margin-bottom:50px;">📞 <span class="num-fix">0772 195 9922</span> | <span class="num-fix">0780 135 2003</span></div>', unsafe_allow_html=True)

# --- ٤. بەشی کارگێڕی (ئامار + گەڕان) ---
with st.expander("🛠 بەشی کارگێڕی (تەنها بۆ خاوەن کار)"):
    if st.text_input("کۆدی نهێنی", type="password", key="admin_final") == ADMIN_PASSWORD:
        df_admin = load_data()
        
        # --- ئامارەکان (Dashboard) ---
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="stat-card">📦 وەسڵەکان<br><span style="font-size:20px;">{len(df_admin)}</span></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="stat-card">💰 کۆی پارە<br><span style="font-size:20px;">{df_admin["نرخ"].sum():,}</span></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="stat-card">🏪 دوکانەکان<br><span style="font-size:20px;">{df_admin["ناوی دوکان"].nunique()}</span></div>', unsafe_allow_html=True)
        
        st.write("---")
        
        # --- گەڕان ---
        search = st.text_input("🔍 گەڕان بەپێی ناوی دوکان یان کڕیار")
        if search:
            df_admin = df_admin[df_admin['ناوی دوکان'].str.contains(search, na=False) | df_admin['کڕیار'].str.contains(search, na=False)]
        
        st.dataframe(df_admin.style.format({"مۆبایل": lambda x: str(x)}), use_container_width=True)
        
        if st.button("🗑 سڕینەوەی گشت داتاکان"):
            save_data(pd.DataFrame(columns=["کات", "کڕیار", "ناوی دوکان", "ناونیشانی دوکان", "مۆبایل", "نرخ", "ناونیشانی کڕیار"]))
            st.rerun()

st.markdown("""<div class="install-bar">بۆ دابەزاندنی ئەپ: کلیک لە ⎙ یان ⋮ بکە و <b>Add to Home Screen</b> هەڵبژێرە</div>""", unsafe_allow_html=True)
