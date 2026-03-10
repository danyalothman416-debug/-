import streamlit as st
from PIL import Image
import io
from datetime import date

# --- ١. ڕێکخستنی لاپەڕە و ستایل ---
st.set_page_config(page_title="Golden Receipt VIP", page_icon="📜")

st.markdown("""
    <style>
    .main { background-color: #f4f7f6; }
    .stButton>button { border-radius: 10px; background-color: #003366; color: white; font-weight: bold; height: 3em; }
    .receipt-container { 
        background: white; 
        padding: 30px; 
        border-radius: 20px; 
        border: 4px solid #d4af37; 
        box-shadow: 0px 10px 30px rgba(0,0,0,0.1); 
        direction: rtl; 
        font-family: 'Tahoma', sans-serif;
        max-width: 500px;
        margin: auto;
    }
    .test-mode { 
        background-image: url('https://www.transparenttextures.com/patterns/stardust.png');
        background-color: #ffcccc !important;
        opacity: 0.7;
    }
    .watermark {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%) rotate(-45deg);
        font-size: 60px;
        color: rgba(255, 0, 0, 0.2);
        font-weight: bold;
        pointer-events: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ٢. داتابەیسی کلیلەکان و قوفڵی مۆبایل ---
if 'valid_keys' not in st.session_state:
    st.session_state['valid_keys'] = {
        "GOLD-MON-8821-X": {"plan": "مانگانە", "expiry": date(2026, 4, 10), "device": None},
        "DR-KIRKUK-2026": {"plan": "ساڵانە", "expiry": date(2027, 3, 10), "device": None}
    }

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# --- ٣. بەشی چوونەژوورەوە و تێست ---
if not st.session_state['authenticated']:
    st.title("📜 سیستەمی وەسڵی گۆڵدن")
    tab1, tab2 = st.tabs(["🔍 تاقیکردنەوە", "🔐 چالاککردنی کۆد"])
    
    with tab1:
        st.info("زانیارییەکان بنووسە بۆ بینینی نموونە")
        t_shop = st.text_input("ناوی پەیج (تێست)")
        if st.button("پێشبینینی وەسڵ"):
            st.markdown(f"""
            <div class="receipt-container test-mode" style="position: relative;">
                <div class="watermark">نموونەی تێست</div>
                <h2 style="text-align:center; color:#003366;">وەسڵی فرۆشتن</h2>
                <p><b>دوکان:</b> {t_shop}</p>
                <p><b>کڕیار:</b> نموونە</p>
                <hr>
                <p style="text-align:center;">ئەم وەسڵە بۆ چاپ نابێت تا کۆدەکەت چالاک نەکەیت</p>
            </div>
            """, unsafe_allow_html=True)

    with tab2:
        user_key = st.text_input("کۆدی چالاککردن", type="password").strip().upper()
        if st.button("بەردەوامبە"):
            if user_key in st.session_state['valid_keys']:
                k_data = st.session_state['valid_keys'][user_key]
                dev_id = st.context.headers.get("User-Agent")
                if k_data["device"] is None or k_data["device"] == dev_id:
                    if date.today() <= k_data["expiry"]:
                        st.session_state['valid_keys'][user_key]["device"] = dev_id
                        st.session_state['authenticated'] = True
                        st.session_state['user_info'] = k_data
                        st.rerun()
                else: st.error("تەنها یەک مۆبایل ڕێگەی پێدراوە!")
            else: st.error("کۆدەکە هەڵەیە")
    st.stop()

# --- ٤. بەشی وەسڵی ڕاستەقینە (دوای چوونەژوورەوە) ---
st.success(f"🌟 پلانی تۆ: {st.session_state['user_info']['plan']}")

with st.expander("🛠 ڕێکخستنی زانیارییەکان", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        shop_n = st.text_input("ناوی پەیج/دوکان", "گۆڵدن دێلیڤەری")
        phone = st.text_input("ژمارەی مۆبایل", "07XXXXXXXXX")
    with col2:
        address = st.text_input("ناونیشان", "کەرکوک - گەڕەکی ...")
        cust_n = st.text_input("ناوی کڕیار")
    
    item_n = st.text_input("جۆری کاڵا")
    price = st.number_input("نرخی کۆتایی", step=250)

if st.button("✨ دروستکردنی وەسڵی کۆتایی"):
    if not cust_n or not phone:
        st.warning("تکایە هەموو خانەکان پڕ بکەرەوە")
    else:
        st.markdown(f"""
        <div class="receipt-container">
            <h2 style="text-align:center; color:#003366; margin-bottom:0;">{shop_n}</h2>
            <p style="text-align:center; font-size:12px; color:#666; margin-top:0;">{address} | {phone}</p>
            <hr style="border: 1px solid #d4af37;">
            <div style="display: flex; justify-content: space-between; margin-top:20px;">
                <span><b>بەروار:</b> {date.today()}</span>
                <span><b>بۆ بەڕێز:</b> {cust_n}</span>
            </div>
            <div style="margin-top:20px; padding:15px; background:#f9f9f9; border-radius:10px;">
                <p><b>کاڵا:</b> {item_n}</p>
                <h3 style="color:#cc0000; text-align:left;">کۆی گشتی: {price:,} دینار</h3>
            </div>
            <hr style="border: 0.5px dashed #ccc;">
            <p style="text-align:center; font-size:12px;">سوپاس بۆ کڕینەکەتان، هەمیشە چاوەڕێتانین!</p>
        </div>
        """, unsafe_allow_html=True)
        st.balloons()
        st.info("ئێستا سکرین شۆتی وەسڵەکە بکە و بۆ کڕیاری بنێرە.")
