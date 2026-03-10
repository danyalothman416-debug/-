import streamlit as st
from PIL import Image, ImageDraw
import io
from datetime import date

# --- ١. ڕێکخستنی لاپەڕە و دیزاینی VIP ---
st.set_page_config(page_title="Golden Receipt VIP", page_icon="📜")

st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { border-radius: 8px; background-color: #003366; color: white; font-weight: bold; }
    .receipt-card { background: white; padding: 20px; border-radius: 15px; border-left: 10px solid #d4af37; box-shadow: 0px 4px 15px rgba(0,0,0,0.1); direction: rtl; }
    .test-watermark { color: rgba(255, 0, 0, 0.2); font-size: 50px; position: absolute; transform: rotate(-45deg); z-index: 10; }
    </style>
    """, unsafe_allow_html=True)

# --- ٢. داتابەیسی کلیلەکان و پاراستنی ئامێر ---
if 'valid_keys' not in st.session_state:
    st.session_state['valid_keys'] = {
        "GOLD-MON-8821-X": {"plan": "مانگانە", "expiry": date(2026, 4, 10), "device": None},
        "DR-KIRKUK-2026": {"plan": "ساڵانە", "expiry": date(2027, 3, 10), "device": None}
    }

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# --- ٣. ڕووکاری سەرەتا و فێرکاری تێست ---
if not st.session_state['authenticated']:
    st.title("📜 سیستەمی وەسڵی گۆڵدن")
    st.write("پێشکەوتووترین و جوانترین دیزاین بۆ وەسڵی پەیجەکان")
    
    tab1, tab2 = st.tabs(["🔍 تاقیکردنەوەی سیستەم", "🔓 چالاککردنی ئەژمار"])
    
    with tab1:
        st.subheader("چۆن وەسڵ دروست دەکەیت؟")
        st.write("١- ناوی خۆت و کڕیار بنووسە. ٢- نرخ دیاری بکە. ٣- وەسڵێکی شیکت بۆ دروست دەبێت.")
        t_cust = st.text_input("ناوی کڕیار (تێست)")
        if st.button("پیشاندانی نموونە"):
            # وەسڵی تێست کە سکرین شۆت ناکرێت چونکە "نموونە"ی گەورەی لەسەرە
            st.markdown(f"""
            <div style="position: relative; border: 5px solid #ccc; padding: 20px; color: #888;">
                <h1 style="color: rgba(255,0,0,0.1); position: absolute; top: 50%; left: 20%; transform: rotate(-30deg); font-size: 80px;">TEST / نموونە</h1>
                <p>ناوی کڕیار: {t_cust}</p>
                <p>کاڵا: نموونەی تێست</p>
                <p>نرخ: 0 دینار</p>
            </div>
            """, unsafe_allow_html=True)
            st.warning("بۆ لابردنی وشەی (نموونە) و داگرتنی وەسڵی ڕاستەقینە، دەبێت کۆدەکەت چالاک بکەیت.")

    with tab2:
        user_key = st.text_input("کۆدی چالاککردن (Key)", type="password").strip().upper()
        if st.button("چوونەژوورەوە"):
            if user_key in st.session_state['valid_keys']:
                k_data = st.session_state['valid_keys'][user_key]
                dev_id = st.context.headers.get("User-Agent")
                if k_data["device"] is None or k_data["device"] == dev_id:
                    if date.today() <= k_data["expiry"]:
                        st.session_state['valid_keys'][user_key]["device"] = dev_id
                        st.session_state['authenticated'] = True
                        st.session_state['user_info'] = k_data
                        st.rerun()
                else: st.error("ئەم کۆدە تەنها بۆ یەک مۆبایلە!")
            else: st.error("کۆدەکە هەڵەیە")
    st.stop()

# --- ٤. ژووری کارکردنی VIP (دوای چوونەژوورەوە) ---
st.markdown(f"<div style='text-align:center; color:#d4af37;'>🌟 ئەژمارەکەت چالاکە بۆ ماوەی {(st.session_state['user_info']['expiry'] - date.today()).days} ڕۆژی تر</div>", unsafe_allow_html=True)

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        shop_name = st.text_input("ناوی پەیج", "گۆڵدن دێلیڤەری")
        cust_name = st.text_input("ناوی کڕیار")
    with col2:
        item_name = st.text_input("جۆری کاڵا")
        total_price = st.number_input("کۆی گشتی (دینار)", step=250)

if st.button("✨ دروستکردنی وەسڵی کوردی"):
    if not cust_name:
        st.error("تکایە ناوی کڕیار بنووسە")
    else:
        # ئەمە وەسڵە کوردییە ڕاستەقینەکەیە کە پیتەکانی تێک ناچێت
        st.markdown(f"""
        <div class="receipt-card">
            <h2 style="text-align:center; color:#003366;">📜 وەسڵی فرۆشتن</h2>
            <hr style="border: 1px solid #d4af37;">
            <p style="font-size:18px;"><b>بۆ بەڕێز:</b> {cust_name}</p>
            <p style="font-size:18px;"><b>کاڵا:</b> {item_name}</p>
            <p style="font-size:18px;"><b>نرخی کۆتایی:</b> {total_price:,} دینار</p>
            <hr>
            <p style="text-align:center; font-size:14px; color:#888;">سوپاس بۆ متمانەتان بە {shop_name}</p>
        </div>
        """, unsafe_allow_html=True)
        st.info("دەتوانیت ئێستا سکرین شۆتی ئەم وەسڵە جوانە بکەیت و بۆ کڕیاری بنێریت.")
