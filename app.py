import streamlit as st
from PIL import Image, ImageDraw
import io
import datetime

# --- داتابەیسی کلیلەکان (وەک نموونە) ---
# لێرەدا دەتوانیت کلیلەکان دیاری بکەیت کە فرۆشتووتن
VALID_KEYS = {
    "GOLDEN-1M-123": "Monthly",
    "GOLDEN-1Y-456": "Yearly",
    "DR-KIRKUK-VIP": "Yearly"
}

st.set_page_config(page_title="Golden Receipt VIP", page_icon="🔑")

# --- بەشی چوونە ژوورەوە و کلیل ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    st.title("🔑 چالاککردنی سیستەم")
    
    st.info("بۆ بەکارهێنانی سیستەمەکە، دەبێت کلیلێکی چالاککردنت هەبێت.")
    
    # پیشاندانی ئۆفەرەکان
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📦 ئۆفەری مانگانە")
        st.write("💰 ٥,٠٠٠ دینار")
        st.write("✅ وەسڵی بێ سنوور")
        st.write("✅ پشتگیری ٢٤ سەعات")
        
    with col2:
        st.subheader("🌟 ئۆفەری ساڵانە")
        st.write("💰 ٤٥,٠٠٠ دینار (٢ مانگ دیاری)")
        st.write("✅ هەموو تایبەتمەندییەکان")
        st.write("✅ لۆگۆی تایبەت بە خۆت")

    key_input = st.text_input("کلیلەکەت لێرە بنووسە:")
    if st.button("چالاککردن"):
        if key_input in VALID_KEYS:
            st.session_state['authenticated'] = True
            st.session_state['plan'] = VALID_KEYS[key_input]
            st.success(f"بە سەرکەوتوویی چالاک بوو! جۆری بەشداریکردن: {VALID_KEYS[key_input]}")
            st.rerun()
        else:
            st.error("کلیلەکە هەڵەیە! تکایە پەیوەندی بە بەڕێوەبەر بکە بۆ کڕینی کلیل.")
    
    st.write("---")
    st.write("بۆ کڕینی کلیل، نامە بنێرە بۆ تیکتۆک یان فاسێتپای بۆ ئەم ژمارەیە: `0750XXXXXXX`")
    st.stop()

# --- ئەگەر کلیلەکە ڕاست بوو، ئەم بەشەی خوارەوە دەردەکەوێت ---

st.title("📜 وەسڵ بڕینی گۆڵدن")
st.sidebar.success(f"پلانی ئێستا: {st.session_state['plan']}")

if st.sidebar.button("چوونە دەرەوە (Logout)"):
    st.session_state['authenticated'] = False
    st.rerun()

with st.form("receipt_form"):
    shop_name = st.text_input("ناوی دوکان", "Golden Shop")
    customer_name = st.text_input("ناوی کڕیار")
    item_name = st.text_input("ناوی کاڵا")
    price = st.number_input("نرخ", min_value=0, step=250)
    
    if st.form_submit_button("دروستکردن"):
        # (هەمان کۆدی دروستکردنی وێنەکە لێرە دادەنرێت)
        st.write(f"وەسڵ بۆ {customer_name} دروست کرا!")
