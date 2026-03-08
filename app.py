import streamlit as st
import pandas as pd
import os
import urllib.parse

# --- 1. ڕێکخستنی لاپەڕە و دیزاینی شیک ---
st.set_page_config(page_title="Golden Delivery", layout="wide")

st.markdown("""
    <style>
    /* شاردنەوەی Sidebar بە یەکجاری */
    section[data-testid="stSidebar"] { display: none !important; }
    
    html, body, [data-testid="stAppViewContainer"] {
        direction: rtl;
        text-align: right;
        background-color: #ffffff;
    }
    
    /* سندوقی سەرەکی براند */
    .brand-header {
        background: linear-gradient(135deg, #1a1a1a 0%, #333333 100%);
        padding: 30px;
        border-radius: 20px;
        border-bottom: 5px solid #D4AF37;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .brand-title {
        color: #D4AF37;
        font-size: 36px;
        font-weight: bold;
        letter-spacing: 1px;
        margin-bottom: 10px;
    }
    
    .brand-desc {
        color: #ffffff;
        font-size: 16px;
        line-height: 1.6;
    }

    /* ستایلی خانەکانی داخڵکردن */
    .stTextInput input, .stNumberInput input {
        border-radius: 10px !important;
        border: 1px solid #ddd !important;
        padding: 10px !important;
    }

    /* ستایلی دوگمەی ناردن */
    .stButton button {
        background-color: #D4AF37 !important;
        color: #1a1a1a !important;
        font-weight: bold !important;
        border-radius: 12px !important;
        border: none !important;
        height: 50px !important;
        font-size: 18px !important;
        transition: 0.3s;
    }
    
    .stButton button:hover {
        background-color: #b8962e !important;
        transform: scale(1.02);
    }

    .num-fix {
        direction: ltr !important;
        display: inline-block !important;
        unicode-bidi: bidi-override !important;
        font-weight: bold;
        color: #D4AF37;
    }

    .footer-text {
        text-align: center;
        background-color: #1a1a1a;
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin-top: 40px;
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

# --- 2. ڕووکاری سەرەکی ---
st.markdown("""
    <div class="brand-header">
        <div class="brand-title">GOLDEN DELIVERY ✨</div>
        <div class="brand-desc">
            <b>گۆڵدن دێلیڤەری: خێراترین و باوەڕپێکراوترین گەیاندن لە کەرکوک</b><br>
            گولدن ديلفيري: أسرع وأكثر خدمة توصيل موثوقة في كركوك
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
        price = st.number_input("💰 نرخی کاڵا / سعر البضاعة", min_value=0, step=250)
    
    st.write(" ")
    submit = st.form_submit_button("تۆمارکردن و ناردنی وەسڵ ✅")
    
    if submit:
        if not customer or not shop_name or not shop_address or not phone or not customer_address:
            st.error("⚠️ تکایە هەموو خانەکان پڕ بکەرەوە")
        else:
            current_df = load_data()
            new_row = pd.DataFrame([{
                "کڕیار": customer, "ناوی دوکان": shop_name, "ناونیشانی دوکان": shop_address, 
                "مۆبایل": phone, "نرخ": price, "ناونیشانی کڕیار": customer_address
            }])
            save_data(pd.concat([current_df, new_row], ignore_index=True))
            
            message = (f"Golden Delivery ✨\n📦 وەسڵێکی نوێ\n"
                       f"👤 کڕیار: {customer}\n🏪 دوکان: {shop_name}\n"
                       f"📍 ناونیشانی دوکان: {shop_address}\n💰 نرخ: {price:,} د.ع\n"
                       f"📞 مۆبایل: {phone}\n🏘 ناونیشانی کڕیار: {customer_address}")
            
            encoded_msg = urllib.parse.quote(message)
            whatsapp_link = f"https://wa.me/{MY_WHATSAPP}?text={encoded_msg}"
            
            st.success("✅ وەسڵەکە بە سەرکەوتوویی تۆمارکرا")
            st.markdown(f'<a href="{whatsapp_link}" target="_blank"><button style="width:100%; background-color:#25D366 !important; color:white !important; border:none; padding:15px; border-radius:12px; font-weight:bold; cursor:pointer; font-size:20px;">کلیک لێرە بکە بۆ ناردن (WhatsApp) 💬</button></a>', unsafe_allow_html=True)

# --- 3. بەشی ژمارەکان و ئەدمین لە خوارەوە ---
st.markdown(f"""
    <div class="footer-text">
        <p>بۆ هەر کێشەیەک پەیوەندی بکە بە:</p>
        <span class="num-fix">0772 195 9922</span> | <span class="num-fix">0780 135 2003</span>
    </div>
""", unsafe_allow_html=True)

with st.expander("🛠 بەشی کارگێڕی"):
    admin_pwd = st.text_input("کۆدی چوونەژوورەوە", type="password")
    if admin_pwd == ADMIN_PASSWORD:
        df = load_data()
        st.dataframe(df, use_container_width=True)
        if st.button("🗑 سڕینەوەی گشت داتاکان"):
            save_data(pd.DataFrame(columns=["کڕیار", "ناوی دوکان", "ناونیشانی دوکان", "مۆبایل", "نرخ", "ناونیشانی کڕیار"]))
            st.rerun()
