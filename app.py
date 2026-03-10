import streamlit as st
import json
import os
from datetime import datetime, date

# --- ١. بەڕێوەبردنی داتابەیسی کلیلەکان (٢٠ کۆدی نوێ) ---
DB_FILE = "keys_database.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    else:
        # دروستکردنی کلیلەکان (١٠ مانگانە و ١٠ ساڵانە)
        initial_db = {
            # --- 📦 کلیلە مانگانەکان (٥,٠٠٠ دینار - تا ٢٠٢٦-٠٤-١٠) ---
            "GOLD-MON-01": {"plan": "مانگانە", "expiry": "2026-04-10", "device": None},
            "GOLD-MON-02": {"plan": "مانگانە", "expiry": "2026-04-10", "device": None},
            "GOLD-MON-03": {"plan": "مانگانە", "expiry": "2026-04-10", "device": None},
            "GOLD-MON-04": {"plan": "مانگانە", "expiry": "2026-04-10", "device": None},
            "GOLD-MON-05": {"plan": "مانگانە", "expiry": "2026-04-10", "device": None},
            "GOLD-MON-06": {"plan": "مانگانە", "expiry": "2026-04-10", "device": None},
            "GOLD-MON-07": {"plan": "مانگانە", "expiry": "2026-04-10", "device": None},
            "GOLD-MON-08": {"plan": "مانگانە", "expiry": "2026-04-10", "device": None},
            "GOLD-MON-09": {"plan": "مانگانە", "expiry": "2026-04-10", "device": None},
            "GOLD-MON-10": {"plan": "مانگانە", "expiry": "2026-04-10", "device": None},

            # --- 🌟 کلیلە ساڵانەکان (١٥,٠٠٠ دینار - تا ٢٠٢٧-٠٣-١٠) ---
            "GOLD-YEAR-01": {"plan": "ساڵانە", "expiry": "2027-03-10", "device": None},
            "GOLD-YEAR-02": {"plan": "ساڵانە", "expiry": "2027-03-10", "device": None},
            "GOLD-YEAR-03": {"plan": "ساڵانە", "expiry": "2027-03-10", "device": None},
            "GOLD-YEAR-04": {"plan": "ساڵانە", "expiry": "2027-03-10", "device": None},
            "GOLD-YEAR-05": {"plan": "ساڵانە", "expiry": "2027-03-10", "device": None},
            "GOLD-YEAR-06": {"plan": "ساڵانە", "expiry": "2027-03-10", "device": None},
            "GOLD-YEAR-07": {"plan": "ساڵانە", "expiry": "2027-03-10", "device": None},
            "GOLD-YEAR-08": {"plan": "ساڵانە", "expiry": "2027-03-10", "device": None},
            "GOLD-YEAR-09": {"plan": "ساڵانە", "expiry": "2027-03-10", "device": None},
            "GOLD-YEAR-10": {"plan": "ساڵانە", "expiry": "2027-03-10", "device": None},

            # کلیلی بەڕێوەبەر
            "DR-KIRKUK-2026": {"plan": "بەڕێوەبەر (VIP)", "expiry": "2030-01-01", "device": None}
        }
        save_db(initial_db)
        return initial_db

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f)

db_keys = load_db()

# --- ٢. ڕێکخستنی دیزاینی شاهانە ---
st.set_page_config(page_title="Golden Receipt VIP", page_icon="📜")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .hero-box {
        background: linear-gradient(135deg, #001a33 0%, #003366 100%);
        color: white; padding: 35px 20px; border-radius: 20px; border-bottom: 8px solid #d4af37;
        text-align: center; direction: rtl; margin-bottom: 25px;
    }
    .price-card {
        background: white; padding: 20px; border-radius: 15px; border: 2px solid #d4af37;
        text-align: center; margin-bottom: 15px; direction: rtl; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .payment-info {
        background: #fff3cd; color: #856404; padding: 20px; border-radius: 15px;
        border: 2px dashed #d4af37; text-align: center; direction: rtl; font-weight: bold;
    }
    .receipt-card { 
        background: white; padding: 30px; border-radius: 20px; border: 4px solid #d4af37; 
        box-shadow: 0px 10px 25px rgba(0,0,0,0.1); direction: rtl; font-family: 'Tahoma', sans-serif;
    }
    .stButton>button { border-radius: 12px; background-color: #003366; color: white; font-weight: bold; height: 3.5em; border: 2px solid #d4af37; }
    </style>
    """, unsafe_allow_html=True)

# --- ٣. ڕووکاری پێشوازی ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    st.markdown("""
    <div class="hero-box">
        <h1 style="color: #d4af37; font-size: 32px; margin-bottom: 10px;">📜 سیستەمی وەسڵی گۆڵدن VIP</h1>
        <p style="font-size: 19px; line-height: 1.6;">
            ئێمە ناسنامەیەکی شاهانە دەبەخشینە پەیجەکەت. وەسڵەکانمان تەنها پسوڵە نین، بەڵکو گوزارشت لە شەخسیات و متمانەی بازرگانییەکەت دەکەن. 
            بە ئاسانترین شێوە و بە جوانترین دیزاین، وەسڵی پرۆفیشناڵ دروست بکە.
        </p>
        <p style="color: #d4af37; font-size: 15px;">🔒 پارێزراو بۆ یەک مۆبایل | ⚡ خێرا و ئاسان | 💎 کوالێتی بەرز</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🖼️ وەسڵی نموونەیی", "💰 نرخ و کڕین", "🔐 چالاککردنی ئەژمار"])
    
    with tab1:
        st.markdown("<h3 style='text-align:center; color:#003366;'>شێوازی وەسڵەکانمان:</h3>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="receipt-card">
            <h2 style="text-align:center; color:#003366; margin-bottom:0;">گۆڵدن دێلیڤەری (نموونە)</h2>
            <p style="text-align:center; font-size:12px; color:#666;">کەرکوک - گەڕەکی ئازادی | 📞 07801352003</p>
            <hr style="border: 1px solid #d4af37;">
            <p><b>بۆ بەڕێز:</b> کڕیاری نموونەیی</p>
            <p><b>کاڵا:</b> وەسڵی ساڵانەی VIP</p>
            <h3 style="color:#cc0000; text-align:left;">کۆی گشتی: ٤٥,٠٠٠ دینار</h3>
            <hr style="border: 0.5px dashed #ccc;">
            <p style="text-align:center; font-size:11px;">دوای چالاککردن، هەموو زانیارییەکان بەپێی ویستی تۆ دەبن</p>
        </div>
        """, unsafe_allow_html=True)

    with tab2:
        st.markdown("<h3 style='text-align:center;'>پلانەکانی بەژداریکردن</h3>", unsafe_allow_html=True)
        col_m, col_y = st.columns(2)
        with col_m:
            st.markdown("""<div class="price-card"><h3>پلانى مانگانە</h3><h2 style="color:#003366;">5,000 IQD</h2><p>بۆ ماوەی ٣٠ ڕۆژ</p></div>""", unsafe_allow_html=True)
        with col_y:
            st.markdown("""<div class="price-card"><h3>پلانى ساڵانە</h3><h2 style="color:#d4af37;">15,000 IQD</h2><p>بۆ ماوەی ٣٦٥ ڕۆژ</p></div>""", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="payment-info">
            💳 شێوازی کڕینی کلیل:<br>
            ناردنی باڵانسی (ئاسیا، کۆرەک، زین) بۆ ئەم ژمارەیە:<br>
            <span style="font-size: 24px; color: #003366;">07801352003</span><br>
            <hr>
            دوای ناردن، وێنەی پسوڵەکە بنێرە بۆ واتسئەپی هەمان ژمارە بۆ وەرگرتنی کلیلەکەت.
        </div>
        """, unsafe_allow_html=True)

    with tab3:
        user_key = st.text_input("کۆدی چالاککردن (Key)", type="password").strip().upper()
        if st.button("پشکنین و چوونەژوورەوە"):
            if user_key in db_keys:
                k_data = db_keys[user_key]
                expiry_dt = datetime.strptime(k_data["expiry"], "%Y-%m-%d").date()
                dev_id = st.context.headers.get("User-Agent")
                
                if date.today() > expiry_dt:
                    st.error(f"❌ ماوەی ئەم کۆدە لە {k_data['expiry']} بەسەرچووە.")
                elif k_data["device"] is not None and k_data["device"] != dev_id:
                    st.error("❌ ئەم کۆدە تەنها لەسەر یەک مۆبایل کار دەکات و پێشتر چالاک کراوە!")
                else:
                    db_keys[user_key]["device"] = dev_id
                    save_db(db_keys)
                    st.session_state['authenticated'] = True
                    st.session_state['user_info'] = k_data
                    st.rerun()
            else:
                st.error("❌ کۆدەکە هەڵەیە، تکایە دڵنیا بەرەوە.")
    st.stop()

# --- ٤. شاشەی کارکردنی سەرەکی ---
st.success(f"✅ بەخێربێیتەوە! پلانی تۆ: {st.session_state['user_info']['plan']} | بەسەرچوون: {st.session_state['user_info']['expiry']}")

with st.expander("📝 دروستکردنی وەسڵی نوێ", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        shop_n = st.text_input("ناوی پەیج/دوکان", "گۆڵدن دێلیڤەری")
        phone_n = st.text_input("ژمارەی مۆبایل", "07XXXXXXXXX")
    with col2:
        addr = st.text_input("ناونیشان", "کەرکوک")
        cust_n = st.text_input("ناوی کڕیار")
    item_n = st.text_input("جۆری کاڵا")
    price_n = st.number_input("نرخی کۆتایی (دینار)", min_value=0, step=250)

if st.button("✨ دروستکردنی وەسڵ"):
    if not cust_n:
        st.warning("تکایە ناوی کڕیار بنووسە")
    else:
        st.markdown(f"""
        <div class="receipt-card">
            <h2 style="text-align:center; color:#003366; margin-bottom:5px;">{shop_n}</h2>
            <p style="text-align:center; font-size:13px; color:#666;">{addr} | 📞 {phone_n}</p>
            <hr style="border: 1px solid #d4af37;">
            <div style="display: flex; justify-content: space-between; margin-top:10px;">
                <span><b>بەروار:</b> {date.today()}</span>
                <span><b>بۆ بەڕێز:</b> {cust_n}</span>
            </div>
            <div style="margin-top:20px; padding:15px; background:#f9f9f9; border-radius:12px; border: 1px solid #eee;">
                <p style="font-size:16px;"><b>کاڵا:</b> {item_n}</p>
                <h3 style="color:#cc0000; text-align:left; font-size:20px;">کۆی گشتی: {price_n:,} دینار</h3>
            </div>
            <p style="text-align:center; font-size:12px; margin-top:15px; color:#888;">سوپاس بۆ متمانەتان، هەمیشە چاوەڕێتانین!</p>
        </div>
        """, unsafe_allow_html=True)
        st.balloons()
