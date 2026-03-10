import streamlit as st
import json
import os
from datetime import datetime, date

# --- ١. بەڕێوەبردنی داتابەیسی کلیلەکان ---
DB_FILE = "keys_database.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    else:
        # دروستکردنی ٤٠ کلیل (٢٠ مانگانە + ٢٠ ساڵانە)
        initial_db = {}
        
        # دروستکردنی ٢٠ کلیلی مانگانە
        for i in range(1, 21):
            key = f"GOLD-MON-{i:02d}"
            initial_db[key] = {"plan": "مانگانە", "expiry": "2026-04-10", "device": None}
            
        # دروستکردنی ٢٠ کلیلی ساڵانە
        for i in range(1, 21):
            key = f"GOLD-YEAR-{i:02d}"
            initial_db[key] = {"plan": "ساڵانە", "expiry": "2027-03-10", "device": None}
            
        # کلیلی تایبەتی خۆت
        initial_db["DR-KIRKUK-2026"] = {"plan": "بەڕێوەبەر (VIP)", "expiry": "2030-01-01", "device": None}
        
        save_db(initial_db)
        return initial_db

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f)

db_keys = load_db()

# --- ٢. دیزاین و وەسفی شاهانە ---
st.set_page_config(page_title="Golden Receipt VIP", page_icon="📜")

st.markdown("""
    <style>
    .hero-box {
        background: linear-gradient(135deg, #001a33 0%, #003366 100%);
        color: white; padding: 35px; border-radius: 20px; border-bottom: 8px solid #d4af37;
        text-align: center; direction: rtl; margin-bottom: 25px;
    }
    .price-card {
        background: white; padding: 15px; border-radius: 12px; border: 2px solid #d4af37;
        text-align: center; direction: rtl;
    }
    .payment-info {
        background: #fff3cd; color: #856404; padding: 20px; border-radius: 15px;
        border: 2px dashed #d4af37; text-align: center; direction: rtl;
    }
    .receipt-card { 
        background: white; padding: 25px; border-radius: 20px; border: 4px solid #d4af37; 
        box-shadow: 0px 10px 25px rgba(0,0,0,0.1); direction: rtl;
    }
    .stButton>button { border-radius: 10px; background-color: #003366; color: white; font-weight: bold; border: 2px solid #d4af37; }
    </style>
    """, unsafe_allow_html=True)

# --- ٣. ڕووکاری پێشوازی ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    st.markdown("""
    <div class="hero-box">
        <h1 style="color: #d4af37;">📜 سیستەمی وەسڵی گۆڵدن VIP</h1>
        <p style="font-size: 19px;">
            ئێمە ناسنامەیەکی شاهانە دەبەخشینە پەیجەکەت. هەر وەسڵێک گوزارشت لە شەخسیات و متمانەی بازرگانییەکەت دەکات. 
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🖼️ وەسڵی نموونەیی", "💰 نرخ و کڕین", "🔐 چالاککردنی ئەژمار"])
    
    with tab1:
        st.markdown(f"""
        <div class="receipt-card">
            <h2 style="text-align:center; color:#003366;">گۆڵدن دێلیڤەری (نموونە)</h2>
            <p style="text-align:center; font-size:12px; color:#666;">کەرکوک | 📞 07801352003</p>
            <hr style="border: 1px solid #d4af37;">
            <p><b>بۆ بەڕێز:</b> کڕیاری نموونەیی</p>
            <p><b>کاڵا:</b> وەسڵی VIP</p>
            <h3 style="color:#cc0000; text-align:left;">کۆی گشتی: ١٥,٠٠٠ دینار</h3>
        </div>
        """, unsafe_allow_html=True)

    with tab2:
        st.markdown("<h3 style='text-align:center;'>پلانەکانی بەژداریکردن</h3>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1: st.markdown("""<div class="price-card"><h4>مانگانە</h4><h2 style="color:#003366;">5,000 IQD</h2></div>""", unsafe_allow_html=True)
        with c2: st.markdown("""<div class="price-card"><h4>ساڵانە</h4><h2 style="color:#d4af37;">15,000 IQD</h2></div>""", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="payment-info">
            💳 ناردنی باڵانسی (ئاسیا، کۆرەک، زین) بۆ ژمارەی:<br>
            <span style="font-size: 24px; color: #003366;">07801352003</span><br>
            پسوڵەکە بنێرە بۆ واتسئەپی هەمان ژمارە بۆ وەرگرتنی کلیل.
        </div>
        """, unsafe_allow_html=True)

    with tab3:
        user_key = st.text_input("کۆدی چالاککردن", type="password").strip().upper()
        if st.button("پشکنینی کۆد"):
            if user_key in db_keys:
                k_data = db_keys[user_key]
                expiry_dt = datetime.strptime(k_data["expiry"], "%Y-%m-%d").date()
                dev_id = st.context.headers.get("User-Agent")
                
                if date.today() > expiry_dt:
                    st.error("❌ ماوەی ئەم کۆدە بەسەرچووە.")
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

# --- ٤. ناوەوەی بەرنامە ---
st.success(f"✅ پلان: {st.session_state['user_info']['plan']} | بەسەرچوون: {st.session_state['user_info']['expiry']}")
# (لێرەدا کۆدی دروستکردنی وەسڵەکە بەردەوام دەبێت...)
