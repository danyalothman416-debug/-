import streamlit as st
from PIL import Image
import io
from datetime import date

# --- ١. ڕێکخستنی لاپەڕە و دیزاین ---
st.set_page_config(page_title="Golden Receipt VIP", page_icon="📜", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { border-radius: 12px; background-color: #003366; color: white; font-weight: bold; height: 3.5em; border: 2px solid #d4af37; }
    .receipt-card { 
        background: white; padding: 25px; border-radius: 20px; border: 4px solid #d4af37; 
        box-shadow: 0px 10px 25px rgba(0,0,0,0.1); direction: rtl; font-family: 'Tahoma', sans-serif;
        margin: auto; position: relative; width: 90%;
    }
    .description-box {
        background: linear-gradient(135deg, #003366 0%, #001a33 100%);
        color: white; padding: 25px; border-radius: 15px; border-bottom: 5px solid #d4af37;
        text-align: center; margin-bottom: 20px; direction: rtl;
    }
    .sample-title { color: #003366; text-align: center; margin-top: 30px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- ٢. داتابەیسی کلیلەکان ---
if 'valid_keys' not in st.session_state:
    st.session_state['valid_keys'] = {
        "GOLD-MON-8821-X": {"plan": "مانگانە", "expiry": date(2026, 4, 10), "device": None},
        "DR-KIRKUK-2026": {"plan": "بەڕێوەبەر (VIP)", "expiry": date(2030, 1, 1), "device": None}
    }

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# --- ٣. ڕووکاری پێشوازی و پێشانگای وەسڵە حازرەکان ---
if not st.session_state['authenticated']:
    st.markdown("""
    <div class="description-box">
        <h1 style="color: #d4af37; margin-bottom: 10px;">📜 سیستەمی وەسڵی گۆڵدن VIP</h1>
        <p style="font-size: 18px;">پسپۆڕ لە دروستکردنی وەسڵی شیک بۆ پەیجەکان</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🖼️ نموونەی وەسڵەکان", "🔐 چالاککردنی ئەژمار"])
    
    with tab1:
        st.markdown("<h3 class='sample-title'>سەیری کوالێتی وەسڵەکانمان بکە</h3>", unsafe_allow_html=True)
        
        # پیشاندانی وەسڵی حازر بە ناوی تۆوە
        st.markdown(f"""
        <div class="receipt-card">
            <h2 style="text-align:center; color:#003366;">گۆڵدن دێلیڤەری (نموونە)</h2>
            <p style="text-align:center; font-size:12px; color:#666;">کەرکوک - شەقامی سەرەکی | 07700000000</p>
            <hr style="border: 1px solid #d4af37;">
            <p><b>بۆ بەڕێز:</b> کڕیاری نموونەیی</p>
            <p><b>کاڵا:</b> جلی پیاوان - مۆدێل ٢٠٢٦</p>
            <h3 style="color:#cc0000; text-align:left;">کۆی گشتی: ٤٥,٠٠٠ دینار</h3>
            <hr style="border: 0.5px dashed #ccc;">
            <p style="text-align:center; font-size:11px;">ئەمە نموونەیەکە، دوای چالاککردن دەتوانیت وەسڵی تایبەت بەخۆت دروست بکەیت</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.info("💡 بۆ دروستکردنی وەسڵی هاوشێوە، کۆدی چالاککردن لە بەشی دووەم داخڵ بکە.")

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

# --- ٤. شاشەی کارکردن (دوای چوونەژوورەوە) ---
st.success(f"🌟 پلانی چالاک: {st.session_state['user_info']['plan']}")

with st.expander("📝 زانیاری وەسڵەکە پڕ بکەرەوە", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        shop_n = st.text_input("ناوی پەیج/دوکان", "گۆڵدن دێلیڤەری")
        phone = st.text_input("ژمارەی مۆبایل", "07XXXXXXXXX")
    with col2:
        address = st.text_input("ناونیشان", "کەرکوک")
        cust_n = st.text_input("ناوی کڕیار")
    
    item_n = st.text_input("جۆری کاڵا")
    price = st.number_input("نرخی کۆتایی (دینار)", step=250)

if st.button("✨ دروستکردنی وەسڵی کۆتایی"):
    st.markdown(f"""
    <div class="receipt-card">
        <h2 style="text-align:center; color:#003366; margin-bottom:5px;">{shop_n}</h2>
        <p style="text-align:center; font-size:13px; color:#666;">{address} | 📞 {phone}</p>
        <hr style="border: 1px solid #d4af37;">
        <div style="display: flex; justify-content: space-between; margin-top:10px;">
            <span><b>بەروار:</b> {date.today()}</span>
            <span><b>بۆ بەڕێز:</b> {cust_n}</span>
        </div>
        <div style="margin-top:20px; padding:15px; background:#f9f9f9; border-radius:10px;">
            <p><b>کاڵا:</b> {item_n}</p>
            <h3 style="color:#cc0000; text-align:left;">کۆی گشتی: {price:,} دینار</h3>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.balloons()
