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
        background: white; 
        padding: 30px; 
        border-radius: 20px; 
        border: 5px solid #d4af37; 
        box-shadow: 0px 15px 35px rgba(0,0,0,0.2); 
        direction: rtl; 
        font-family: 'Tahoma', sans-serif;
        max-width: 550px;
        margin: auto;
        position: relative;
    }
    .watermark {
        position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%) rotate(-45deg);
        font-size: 70px; color: rgba(255, 0, 0, 0.1); font-weight: bold; pointer-events: none;
    }
    .expiry-tag { background: #003366; color: #d4af37; padding: 10px; border-radius: 50px; text-align: center; font-weight: bold; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- ٢. داتابەیسی کلیلەکان و قوفڵی مۆبایل ---
if 'valid_keys' not in st.session_state:
    st.session_state['valid_keys'] = {
        # مانگانە
        "GOLD-MON-8821-X": {"plan": "مانگانە", "expiry": date(2026, 4, 10), "device": None},
        "GOLD-MON-4432-Y": {"plan": "مانگانە", "expiry": date(2026, 4, 10), "device": None},
        # ساڵانە
        "GOLD-25K-YEAR-001": {"plan": "ساڵانە", "expiry": date(2027, 3, 10), "device": None},
        "DR-KIRKUK-2026": {"plan": "بەڕێوەبەر (VIP)", "expiry": date(2030, 1, 1), "device": None}
    }

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# --- ٣. ڕووکاری چوونەژوورەوە و تێست ---
if not st.session_state['authenticated']:
    st.title("📜 سیستەمی گۆڵدن بۆ وەسڵی دیجیتاڵی")
    st.write("### متمانە و جوانی بۆ بازرگانییەکەت")
    
    tab1, tab2 = st.tabs(["✨ تاقیکردنەوەی بێبەرامبەر", "🔐 چالاککردنی کۆد"])
    
    with tab1:
        st.info("لێرەدا دەتوانیت وەسڵەکە تاقی بکەیتەوە پێش کڕین")
        test_shop = st.text_input("ناوی دوکان (تێست)")
        if st.button("پێشبینینی وەسڵی تێست"):
            st.markdown(f"""
            <div class="receipt-card" style="background-color: #fcfcfc;">
                <div class="watermark">نموونەی تێست / TEST</div>
                <h2 style="text-align:center; color:#003366;">{test_shop if test_shop else "ناوی دوکان"}</h2>
                <p><b>کڕیار:</b> کڕیاری تێست</p>
                <hr>
                <p style="text-align:center; color:red;">ئەم وەسڵە ناتوانرێت وەک وەسڵی ڕاستەقینە بەکاربێت</p>
            </div>
            """, unsafe_allow_html=True)

    with tab2:
        user_key = st.text_input("کۆدی چالاککردن (Activation Key)", type="password").strip().upper()
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
                    else: st.error("⚠️ کۆدەکەت بەسەرچووە!")
                else: st.error("❌ ئەم کۆدە تەنها لەسەر یەک مۆبایل کار دەکات!")
            else: st.error("کۆدەکە هەڵەیە!")
    st.stop()

# --- ٤. شاشەی کارکردنی سەرەکی دوای چوونەژوورەوە ---
days_left = (st.session_state['user_info']['expiry'] - date.today()).days
st.markdown(f"<div class='expiry-tag'>💎 پلان: {st.session_state['user_info']['plan']} | ⏳ ماوە: {days_left} ڕۆژ</div>", unsafe_allow_html=True)

with st.expander("📝 زانیارییەکان ڕێکبخە", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        shop_name = st.text_input("ناوی پەیج/دوکان", "گۆڵدن دێلیڤەری")
        address = st.text_input("ناونیشان", "کەرکوک - شەقامی سەرەکی")
    with col2:
        phone = st.text_input("ژمارەی مۆبایل", "07XXXXXXXXX")
        cust_name = st.text_input("ناوی کڕیار")
    
    item_detail = st.text_input("جۆری کاڵا")
    total_price = st.number_input("نرخی کۆتایی (دینار)", min_value=0, step=250)

if st.button("✨ دروستکردنی وەسڵی VIP"):
    if not cust_name or not item_detail:
        st.warning("تکایە هەموو زانیارییەکان پڕ بکەرەوە")
    else:
        st.markdown(f"""
        <div class="receipt-card">
            <h2 style="text-align:center; color:#003366; margin-bottom:5px;">{shop_name}</h2>
            <p style="text-align:center; font-size:13px; color:#666; margin-top:0;">{address} | 📞 {phone}</p>
            <hr style="border: 1px solid #d4af37;">
            <div style="display: flex; justify-content: space-between; margin-top:15px; font-size:15px;">
                <span><b>بەروار:</b> {date.today()}</span>
                <span><b>بۆ بەڕێز:</b> {cust_name}</span>
            </div>
            <div style="margin-top:20px; padding:20px; background:#f9f9f9; border-radius:12px; border: 1px solid #eee;">
                <p style="font-size:18px;"><b>کاڵا:</b> {item_detail}</p>
                <h3 style="color:#cc0000; text-align:left; font-size:22px;">کۆی گشتی: {total_price:,} دینار</h3>
            </div>
            <p style="text-align:center; font-size:13px; margin-top:20px; color:#888;">سوپاس بۆ کڕینەکەتان، هەمیشە چاوەڕێتانین!</p>
        </div>
        """, unsafe_allow_html=True)
        st.balloons()
