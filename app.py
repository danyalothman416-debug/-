import streamlit as st
from PIL import Image
import io
from datetime import date

# --- ١. ڕێکخستنی لاپەڕە و دیزاینی VIP ---
st.set_page_config(page_title="Golden Receipt VIP", page_icon="📜", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { border-radius: 12px; background-color: #003366; color: white; font-weight: bold; height: 3.5em; border: 2px solid #d4af37; }
    .receipt-card { 
        background: white; padding: 30px; border-radius: 20px; border: 5px solid #d4af37; 
        box-shadow: 0px 15px 35px rgba(0,0,0,0.2); direction: rtl; font-family: 'Tahoma', sans-serif;
        max-width: 550px; margin: auto; position: relative;
    }
    .watermark {
        position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%) rotate(-45deg);
        font-size: 70px; color: rgba(255, 0, 0, 0.1); font-weight: bold; pointer-events: none;
    }
    .description-box {
        background: linear-gradient(135deg, #003366 0%, #001a33 100%);
        color: white; padding: 25px; border-radius: 15px; border-bottom: 5px solid #d4af37;
        text-align: center; margin-bottom: 30px; direction: rtl;
    }
    .feature-list { text-align: right; font-size: 14px; list-style-type: '⭐'; padding-right: 20px; }
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

# --- ٣. ڕووکاری پێشوازی و وەسفی بەرنامە ---
if not st.session_state['authenticated']:
    # --- لێرەدا وەسفەکە زیاد کراوە بۆ ئەوەی لە سەرەتای سایتەکە دیار بێت ---
    st.markdown("""
    <div class="description-box">
        <h1 style="color: #d4af37; margin-bottom: 10px;">📜 سیستەمی وەسڵی گۆڵدن VIP</h1>
        <p style="font-size: 18px;">سکرتێرێکی زیرەک بۆ ڕێکخستنی فرۆشتنی پەیج و بازرگانییەکان</p>
        <hr style="border-color: rgba(212, 175, 55, 0.3);">
        <div class="feature-list">
            <li>دیزاینێکی شاهانە و پرۆفیشناڵ کە متمانەی کڕیار زیاد دەکات.</li>
            <li>پشتیگیری تەواوی زمانی کوردی بە بێ تێکچوونی پیتەکان.</li>
            <li>قوفڵکردنی کۆد لەسەر یەک مۆبایل بۆ پاراستنی مافی بەکارهێنەر.</li>
            <li>سیستەمی تاقیکردنەوەی بێبەرامبەر پێش کڕینی کلیل.</li>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["✨ تاقیکردنەوەی بێبەرامبەر", "🔐 چالاککردنی ئەژمار"])
    
    with tab1:
        st.info("لێرەدا دەتوانیت وەسڵەکە تاقی بکەیتەوە")
        t_shop = st.text_input("ناوی دوکان (تێست)")
        if st.button("پێشبینینی وەسڵی تێست"):
            st.markdown(f"""
            <div class="receipt-card">
                <div class="watermark">نموونە / TEST</div>
                <h2 style="text-align:center; color:#003366;">{t_shop if t_shop else "ناوی دوکان"}</h2>
                <p><b>کڕیار:</b> کڕیاری نموونە</p>
                <hr>
                <p style="text-align:center; color:red;">بۆ لابردنی ئەم نیشانەیە و داگرتنی وەسڵ، کۆد داخل بکە</p>
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

# --- ٤. شاشەی کارکردن (دوای چوونەژوورەوە) ---
st.success(f"🌟 بەخێربێیتەوە! پلانی تۆ: {st.session_state['user_info']['plan']}")

with st.expander("📝 زانیارییەکان ڕێکبخە", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        shop_n = st.text_input("ناوی پەیج/دوکان", "گۆڵدن دێلیڤەری")
        phone = st.text_input("ژمارەی مۆبایل", "07XXXXXXXXX")
    with col2:
        address = st.text_input("ناونیشان", "کەرکوک")
        cust_n = st.text_input("ناوی کڕیار")
    
    item_n = st.text_input("جۆری کاڵا")
    price = st.number_input("نرخی کۆتایی", step=250)

if st.button("✨ دروستکردنی وەسڵ"):
    st.markdown(f"""
    <div class="receipt-card">
        <h2 style="text-align:center; color:#003366;">{shop_n}</h2>
        <p style="text-align:center; font-size:12px; color:#666;">{address} | {phone}</p>
        <hr style="border: 1px solid #d4af37;">
        <p><b>بۆ بەڕێز:</b> {cust_n}</p>
        <p><b>کاڵا:</b> {item_n}</p>
        <h3 style="color:#cc0000; text-align:left;">کۆی گشتی: {price:,} دینار</h3>
        <hr style="border: 0.5px dashed #ccc;">
        <p style="text-align:center; font-size:12px;">بەروار: {date.today()}</p>
    </div>
    """, unsafe_allow_html=True)
