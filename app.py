import streamlit as st
import json
import os
from datetime import datetime, date

# --- ١. بەڕێوەبردنی داتابەیس ---
DB_FILE = "keys_database.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    else:
        initial_db = {
            "GOLD-MON-TEST": {"plan": "مانگانە", "expiry": "2026-04-10", "device": None},
            "GOLD-YEAR-TEST": {"plan": "ساڵانە", "expiry": "2027-03-10", "device": None},
            "DR-KIRKUK-2026": {"plan": "بەڕێوەبەر (VIP)", "expiry": "2030-01-01", "device": None}
        }
        save_db(initial_db)
        return initial_db

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f)

db_keys = load_db()

# --- ٢. دیزاین و ستایلی VIP ---
st.set_page_config(page_title="Golden Receipt VIP", page_icon="📜")

st.markdown("""
    <style>
    .main { background-color: #f4f7f6; }
    .stButton>button { border-radius: 12px; background-color: #003366; color: white; font-weight: bold; height: 3.5em; border: 2px solid #d4af37; }
    .hero-box {
        background: linear-gradient(135deg, #001a33 0%, #003366 100%);
        color: white; padding: 40px 20px; border-radius: 20px; border-bottom: 8px solid #d4af37;
        text-align: center; direction: rtl; margin-bottom: 30px;
    }
    .price-card {
        background: white; padding: 20px; border-radius: 15px; border: 2px solid #d4af37;
        text-align: center; margin-bottom: 10px; direction: rtl;
    }
    .payment-info {
        background: #fff3cd; color: #856404; padding: 15px; border-radius: 10px;
        border: 1px solid #ffeeba; text-align: center; direction: rtl; font-weight: bold;
    }
    .receipt-card { 
        background: white; padding: 25px; border-radius: 20px; border: 4px solid #d4af37; 
        box-shadow: 0px 10px 25px rgba(0,0,0,0.1); direction: rtl;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ٣. ڕووکاری پێشوازی (Landing Page) ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    # --- خانەی یەکەمی وەسفی بەرنامە (شەخسیاتی و بەهێز) ---
    st.markdown("""
    <div class="hero-box">
        <h1 style="color: #d4af37; font-size: 35px; margin-bottom: 15px;">📜 سیستەمی وەسڵی گۆڵدن VIP</h1>
        <p style="font-size: 20px; line-height: 1.6;">
            ئێمە لێرەین بۆ ئەوەی شکۆ و ناسنامەیەکی شاهانە بە بازرگانییەکەت ببەخشین. 
            ئەم بەرنامەیە تەنها دروستکەری وەسڵ نییە، بەڵکو پارێزەری متمانەی تۆ و کڕیارەکانتە. 
            بە دیزاینە ناوازەکانمان، هەر وەسڵێک دەبێتە ڕیکلامێکی پرۆفیشناڵ بۆ پەیجەکەت.
        </p>
        <p style="color: #d4af37; font-size: 16px;">✨ خێرا | ✨ پارێزراو | ✨ بێ وێنە</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🖼️ وەسڵی نموونەیی", "💰 نرخ و کڕینی کلیل", "🔐 چالاککردنی ئەژمار"])
    
    with tab1:
        st.markdown("<h3 style='text-align:center; color:#003366;'>کوالێتی کارەکانمان ببینە:</h3>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="receipt-card">
            <h2 style="text-align:center; color:#003366; margin-bottom:0;">گۆڵدن دێلیڤەری (نموونە)</h2>
            <p style="text-align:center; font-size:12px; color:#666;">کەرکوک - گەڕەکی ئازادی | 📞 07801352003</p>
            <hr style="border: 1px solid #d4af37;">
            <p><b>بۆ بەڕێز:</b> کڕیاری نموونەیی</p>
            <p><b>کاڵا:</b> وەسڵی ساڵانەی VIP</p>
            <h3 style="color:#cc0000; text-align:left;">کۆی گشتی: ٧٥,٠٠٠ دینار</h3>
            <hr style="border: 0.5px dashed #ccc;">
            <p style="text-align:center; font-size:11px;">تێبینی: لۆگۆ و ناونیشان بەپێی ویستی تۆ دەگۆڕدرێت</p>
        </div>
        """, unsafe_allow_html=True)

    with tab2:
        st.markdown("<h3 style='text-align:center;'>پلانەکانی بەژداریکردن</h3>", unsafe_allow_html=True)
        col_m, col_y = st.columns(2)
        with col_m:
            st.markdown("""<div class="price-card"><h3>مانگانە</h3><h2 style="color:#003366;">10,000 IQD</h2><p>بۆ ماوەی ٣٠ ڕۆژ</p></div>""", unsafe_allow_html=True)
        with col_y:
            st.markdown("""<div class="price-card"><h3>ساڵانە</h3><h2 style="color:#d4af37;">25,000 IQD</h2><p>بۆ ماوەی ٣٦٥ ڕۆژ</p></div>""", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="payment-info">
            💳 شێوازی کڕین:<br>
            ناردنی باڵانسی (ئاسیا، کۆرەک، زین) بۆ ژمارەی:<br>
            <span style="font-size: 22px; color: #003366;">07801352003</span><br>
            دوای ناردن، وێنەی پسوڵەکە بنێرە بۆ واتسئەپی هەمان ژمارە بۆ وەرگرتنی کلیل.
        </div>
        """, unsafe_allow_html=True)

    with tab3:
        user_key = st.text_input("کۆدی چالاککردن داخڵ بکە", type="password").strip().upper()
        if st.button("پشکنینی کۆد و چوونەژوورەوە"):
            if user_key in db_keys:
                k_data = db_keys[user_key]
                expiry_dt = datetime.strptime(k_data["expiry"], "%Y-%m-%d").date()
                dev_id = st.context.headers.get("User-Agent")
                
                if date.today() > expiry_dt:
                    st.error(f"❌ ماوەی ئەم کۆدە لە {k_data['expiry']} بەسەرچووە.")
                elif k_data["device"] is not None and k_data["device"] != dev_id:
                    st.error("❌ ئەم کۆدە تەنها لەسەر یەک مۆبایل کار دەکات!")
                else:
                    db_keys[user_key]["device"] = dev_id
                    save_db(db_keys)
                    st.session_state['authenticated'] = True
                    st.session_state['user_info'] = k_data
                    st.rerun()
            else:
                st.error("❌ کۆدەکە هەڵەیە.")
    st.stop()

# --- ٤. شاشەی کارکردنی ناوەوە ---
st.success(f"✅ بەخێربێیت! پلان: {st.session_state['user_info']['plan']} | بەسەرچوون: {st.session_state['user_info']['expiry']}")

with st.expander("📝 دروستکردنی وەسڵ", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        shop_n = st.text_input("ناوی پەیج/دوکان", "گۆڵدن دێلیڤەری")
        phone_n = st.text_input("ژمارەی مۆبایل", "07XXXXXXXXX")
    with col2:
        addr = st.text_input("ناونیشان", "کەرکوک")
        cust_n = st.text_input("ناوی کڕیار")
    item_n = st.text_input("جۆری کاڵا")
    price_n = st.number_input("نرخی کۆتایی", step=250)

if st.button("✨ دروستکردن"):
    st.markdown(f"""
    <div class="receipt-card">
        <h2 style="text-align:center; color:#003366;">{shop_n}</h2>
        <p style="text-align:center; font-size:13px; color:#666;">{addr} | 📞 {phone_n}</p>
        <hr style="border: 1px solid #d4af37;">
        <p><b>بۆ بەڕێز:</b> {cust_n}</p>
        <p><b>کاڵا:</b> {item_n}</p>
        <h3 style="color:#cc0000; text-align:left;">کۆی گشتی: {price_n:,} دینار</h3>
    </div>
    """, unsafe_allow_html=True)
    st.balloons()
