import streamlit as st
import pandas as pd
import os
import urllib.parse

# --- 1. ڕێکخستنی لاپەڕە و دیزاین ---
st.set_page_config(page_title="Golden Delivery", layout="wide")

st.markdown("""
    <style>
    section[data-testid="stSidebar"] { display: none !important; }
    html, body, [data-testid="stAppViewContainer"] { direction: rtl; text-align: right; }
    .brand-header {
        background: linear-gradient(135deg, #1a1a1a 0%, #333333 100%);
        padding: 25px; border-radius: 15px; border-bottom: 4px solid #D4AF37;
        text-align: center; margin-bottom: 20px;
    }
    .brand-title { color: #D4AF37; font-size: 32px; font-weight: bold; }
    .num-fix { direction: ltr !important; display: inline-block !important; color: #D4AF37; font-weight: bold; }
    .install-bar {
        position: fixed; bottom: 0; left: 0; width: 100%;
        background-color: #1a1a1a; color: white; padding: 12px;
        text-align: center; border-top: 3px solid #D4AF37; z-index: 9999;
    }
    .stExpander { border: 1px solid #D4AF37 !important; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- ٢. لۆژیکی داتا ---
ADMIN_PASSWORD = "dr_danyal_2024" 
DB_FILE = "global_deliveries.csv"
MY_WHATSAPP = "9647721959922"

def load_data():
    if os.path.exists(DB_FILE):
        # خوێندنەوەی ژمارەی مۆبایل وەک دەق بۆ ئەوەی سفرەکانی سەرەتا نەفەوتێن
        df = pd.read_csv(DB_FILE, dtype={"مۆبایل": str})
        return df
    return pd.DataFrame(columns=["کڕیار", "ناوی دوکان", "ناونیشانی دوکان", "مۆبایل", "نرخ", "ناونیشانی کڕیار"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

# --- ٣. ڕووکاری سەرەکی ---
st.markdown("""
    <div class="brand-header">
        <div class="brand-title">GOLDEN DELIVERY ✨</div>
        <div style="color:white;">خێراترین و باوەڕپێکراوترین خزمەتگوزاری گەیاندن لە کەرکوک</div>
    </div>
""", unsafe_allow_html=True)

# بەشی ڕێنمایی دابەزاندنی ئەپ بۆ کڕیار
with st.expander("📲 چۆن ئەپەکە دابەزێنم بۆ سەر شاشەی مۆبایلەکەم؟"):
    st.markdown("""
    <div style="text-align:right; font-size:14px;">
    ١. لە خوارەوەی شاشەکە کلیک لە نیشانەی <b>Share (📤)</b> بکە.<br>
    ٢. لە لیستەکە بگەڕێ بۆ <b>Add to Home Screen</b>.<br>
    ٣. کلیک لە <b>Add</b> بکە لە سەرەوە.<br>
    ✅ ئێستا ئەپەکە وەک بەرنامەکانی تر لەسەر شاشەکەت دەردەکەوێت.
    </div>
    """, unsafe_allow_html=True)

st.write("---")

with st.form("delivery_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        customer = st.text_input("👤 ناوی کڕیار")
        shop_name = st.text_input("🏪 ناوی دوکان")
        shop_address = st.text_input("📍 ناونیشانی دوکان")
    with col2:
        phone = st.text_input("📞 ژمارەی مۆبایل")
        customer_address = st.text_input("🏘 ناونیشانی کڕیار")
        price = st.number_input("💰 نرخ (د.ع)", min_value=0, step=250)
    
    submit = st.form_submit_button("تۆمارکردن و ناردنی وەسڵ ✅")
    
    if submit:
        if not customer or not shop_name or not phone:
            st.error("⚠️ تکایە زانیارییە سەرەکییەکان پڕ بکەرەوە")
        else:
            df = load_data()
            new_row = pd.DataFrame([{
                "کڕیار": customer, "ناوی دوکان": shop_name, "ناونیشانی دوکان": shop_address, 
                "مۆبایل": str(phone), "نرخ": price, "ناونیشانی کڕیار": customer_address
            }])
            save_data(pd.concat([df, new_row], ignore_index=True))
            
            # دروستکردنی نامەی واتسئەپ
            msg = f"Golden Delivery ✨\n📦 وەسڵێکی نوێ\n👤 کڕیار: {customer}\n📞 مۆبایل: {phone}\n💰 نرخ: {price:,} د.ع"
            link = f"https://wa.me/{MY_WHATSAPP}?text={urllib.parse.quote(msg)}"
            st.success("✅ زانیارییەکان بە سەرکەوتوویی تۆمارکران")
            st.markdown(f'<a href="{link}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:12px; border-radius:10px; font-weight:bold; cursor:pointer; font-size:16px;">ناردنی وەسڵ بۆ WhatsApp 💬</button></a>', unsafe_allow_html=True)

st.markdown(f'<div style="text-align:center; padding:30px;">📞 پەیوەندی: <span class="num-fix">0772 195 9922</span> | <span class="num-fix">0780 135 2003</span></div>', unsafe_allow_html=True)

# --- ٤. بەشی ئەدمینی نهێنی (تەنها بە لینکە تایبەتەکە دەردەکەوێت) ---
query_params = st.query_params
if query_params.get("role") == "boss":
    st.write("---")
    with st.expander("🛠 بەشی کارگێڕی (تەنها تۆ دەیبینیت)"):
        password_input = st.text_input("کۆدی نهێنی", type="password", key="admin_final")
        if password_input == ADMIN_PASSWORD:
            st.success("بەخێربێیت دکتۆر دانیال 👑")
            df_admin = load_data()
            
            # پۆلێنکردنی داتاکان (دواهەمین داواکاری لە سەرەوە بێت)
            st.dataframe(df_admin.style.format({"مۆبایل": lambda x: str(x)}), use_container_width=True)
            
            # دوگمەی سڕینەوەی گشت داتاکان
            if st.button("🗑 سڕینەوەی هەموو تۆمارەکان"):
                if st.checkbox("دڵنیام لە سڕینەوە"):
                    save_data(pd.DataFrame(columns=["کڕیار", "ناوی دوکان", "ناونیشانی دوکان", "مۆبایل", "نرخ", "ناونیشانی کڕیار"]))
                    st.rerun()
else:
    # نیشانەیەکی بچووک بۆ متمانە لە خوارەوە
    st.markdown('<div style="text-align:center; opacity:0.3; font-size:10px; padding-bottom:60px;">Golden Delivery System v1.2 - Secure Database</div>', unsafe_allow_html=True)

st.markdown("""<div class="install-bar">بۆ دابەزاندنی ئەپ: کلیک لە ⎙ یان ⋮ بکە و <b>Add to Home Screen</b> هەڵبژێرە</div>""", unsafe_allow_html=True)
