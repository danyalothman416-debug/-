import streamlit as st
import pandas as pd
import os
import urllib.parse

# --- 1. ڕێکخستنی لاپەڕە و دیزاین ---
st.set_page_config(page_title="Golden Delivery", layout="wide")

st.markdown("""
    <style>
    /* سڕینەوەی Sidebar */
    section[data-testid="stSidebar"] { display: none !important; }
    
    html, body, [data-testid="stAppViewContainer"] {
        direction: rtl;
        text-align: right;
        background-color: #ffffff;
    }
    
    /* سندوقی سەرەکی براند */
    .brand-header {
        background: linear-gradient(135deg, #1a1a1a 0%, #333333 100%);
        padding: 25px;
        border-radius: 15px;
        border-bottom: 4px solid #D4AF37;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    
    .brand-title { color: #D4AF37; font-size: 32px; font-weight: bold; }
    .brand-desc { color: #ffffff; font-size: 16px; margin-top: 10px; }

    /* ڕێککردنەوەی ژمارەکان */
    .num-fix {
        direction: ltr !important;
        display: inline-block !important;
        unicode-bidi: bidi-override !important;
        font-weight: bold;
        color: #D4AF37;
    }

    /* بارەکەی خوارەوە بۆ Add to Home Screen */
    .install-bar {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #1a1a1a;
        color: white;
        padding: 12px;
        text-align: center;
        border-top: 3px solid #D4AF37;
        z-index: 9999;
        font-size: 14px;
    }
    .install-icon {
        background-color: #D4AF37;
        color: #1a1a1a;
        padding: 2px 8px;
        border-radius: 5px;
        font-weight: bold;
        margin: 0 5px;
    }
    
    .footer-section {
        text-align: center;
        padding: 20px;
        margin-bottom: 70px; /* بۆ ئەوەی نەکەوێتە ژێر بارەکە */
        border-top: 1px solid #eee;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ٢. لۆژیکی داتا ---
ADMIN_PASSWORD = "dr_danyal_2024" 
DB_FILE = "global_deliveries.csv"
MY_WHATSAPP = "9647721959922"

def load_data():
    if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["کڕیار", "ناوی دوکان", "ناونیشانی دوکان", "مۆبایل", "نرخ", "ناونیشانی کڕیار"])

def save_data(df): df.to_csv(DB_FILE, index=False)

# --- ٣. ڕووکاری سەرەکی ---
st.markdown("""
    <div class="brand-header">
        <div class="brand-title">GOLDEN DELIVERY ✨</div>
        <div class="brand-desc">
            <b>خێراترین و باوەڕپێکراوترین خزمەتگوزاری گەیاندن لە کەرکوک.</b><br>
            أسرع وأكثر خدمة توصيل موثوقة في كركوك.
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
    
    st.write("")
    submit = st.form_submit_button("تۆمارکردن و ناردنی وەسڵ ✅")
    
    if submit:
        if not customer or not shop_name or not shop_address or not phone or not customer_address:
            st.error("⚠️ تکایە هەموو خانەکان پڕ بکەرەوە")
        else:
            df = load_data()
            new_row = pd.DataFrame([{
                "کڕیار": customer, "ناوی دوکان": shop_name, "ناونیشانی دوکان": shop_address, 
                "مۆبایل": phone, "نرخ": price, "ناونیشانی کڕیار": customer_address
            }])
            save_data(pd.concat([df, new_row], ignore_index=True))
            
            msg = (f"Golden Delivery ✨\n📦 وەسڵێکی نوێ\n👤 کڕیار: {customer}\n"
                   f"🏪 دوکان: {shop_name}\n📍 ناونیشانی دوکان: {shop_address}\n"
                   f"💰 نرخ: {price:,} د.ع\n📞 مۆبایل: {phone}\n🏘 ناونیشانی کڕیار: {customer_address}")
            
            link = f"https://wa.me/{MY_WHATSAPP}?text={urllib.parse.quote(msg)}"
            st.success("✅ وەسڵەکە تۆمارکرا")
            st.markdown(f'<a href="{link}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:12px; border-radius:10px; font-weight:bold; cursor:pointer; font-size:18px;">ناردن بۆ WhatsApp 💬</button></a>', unsafe_allow_html=True)

# پیشاندانی هەردوو ژمارەکە بە ڕێکی
st.markdown(f"""
    <div class="footer-section">
        <p>بۆ پەیوەندی و پشتگیری:</p>
        <span class="num-fix">0772 195 9922</span> | <span class="num-fix">0780 135 2003</span>
    </div>
""", unsafe_allow_html=True)

# بارەکەی خوارەوە بۆ ڕێنمایی ئەپڵیکەیشن
st.markdown("""
    <div class="install-bar">
        بۆ ئەوەی وەک ئەپ دایببەزێنیت: کلیک لە <span class="install-icon">⎙</span> یان <span class="install-icon">⋮</span> بکە و <b>Add to Home Screen</b> هەڵبژێرە
    </div>
""", unsafe_allow_html=True)

# بەشی ئەدمین (شاراوە لە خوارەوە)
with st.expander("🛠 بەشی کارگێڕی"):
    if st.text_input("کۆدی نهێنی بنووسە", type="password", key="admin_final") == ADMIN_PASSWORD:
        st.write("### 📋 لیستی گشت وەسڵەکان")
        st.dataframe(load_data(), use_container_width=True)
        if st.button("🗑 سڕینەوەی هەموو داتاکان"):
            save_data(pd.DataFrame(columns=["کڕیار", "ناوی دوکان", "ناونیشانی دوکان", "مۆبایل", "نرخ", "ناونیشانی کڕیار"]))
            st.rerun()
