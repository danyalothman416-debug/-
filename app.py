import streamlit as st
from PIL import Image, ImageDraw
import io

# --- لیستێکی نموونەیی بۆ کلیلەکان (کە فرۆشتووتن) ---
if 'active_keys' not in st.session_state:
    st.session_state['active_keys'] = ["GOLDEN-780", "KIRKUK-2026", "VIP-USER"]

st.set_page_config(page_config_title="Golden Receipt", page_icon="📜")

# --- بەشی پارەدان و چالاککردن ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    st.title("🔑 چالاککردنی سیستەمی وەسڵی گۆڵدن")
    
    st.warning("⚠️ ئەم سیستەمە تەنها بۆ بەکارهێنەرە تایبەتەکانە.")
    
    # ڕونکردنەوەی شێوازی پارەدان
    st.info("""
    ### 💳 چۆن کلیل (Key) بەدەست دەهێنیت؟
    ئێمە تەنها لە ڕێگەی **باڵانس (کارتی مۆبایل)** پارە وەردەگرین:
    
    * **📦 ئۆفەری مانگانە:** ٥,٠٠٠ باڵانس (ئاسیا یان کۆڕەکت)
    * **🌟 ئۆفەری ساڵانە:** ٤٥,٠٠٠ باڵانس (٢ مانگ دیاری)
    
    **بۆ کڕینی کلیل:** وێنەی کارتەکە یان کۆدەکە بنێرە بۆ ئەم ژمارەیەی واتسئەپ:
    👉 [**07801352003**](https://wa.me/9647801352003)
    """)

    key_input = st.text_input("کلیلەکەت لێرە بنووسە (Activation Key):")
    
    if st.button("تەئکیدکردنەوە و چوونەژوورەوە"):
        if key_input in st.session_state['active_keys']:
            st.session_state['authenticated'] = True
            st.success("بە سەرکەوتوویی چالاک بوو! بەخێربێیت.")
            st.rerun()
        else:
            st.error("کلیلەکە هەڵەیە یان بەسەرچووە. تکایە پەیوەندی بە واتسئەپ بکە.")
    st.stop()

# --- ئەگەر کلیلەکە ڕاست بوو، ئەم بەشە دەکرێتەوە ---

st.title("📜 وەسڵ بڕینی دیجیتاڵی")
st.sidebar.write("✅ سیستەم چالاکە")

with st.form("main_form"):
    shop_name = st.text_input("ناوی دوکان/پەیج")
    cust_name = st.text_input("ناوی کڕیار")
    item = st.text_input("جۆری کاڵا")
    price = st.number_input("نرخ (دینار)", step=250)
    logo_file = st.file_uploader("لۆگۆی خۆت دابنێ (ئارەزوومەندانە)", type=['png', 'jpg'])
    
    if st.form_submit_button("دروستکردنی وەسڵ"):
        # لێرەدا کۆدی دروستکردنی وێنەکە کار دەکات
        st.success(f"وەسڵ بۆ {cust_name} بە سەرکەوتوویی دروست کرا!")
        # (کۆدی ImageDraw لێرە زیاد دەبێت وەک پێشتر)
