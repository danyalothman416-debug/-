import streamlit as st
import json
import os
from datetime import datetime, date

# --- ١. بەڕێوەبردنی کلیلەکان (٤٠ کلیل + ٢ نرخ) ---
DB_FILE = "keys_database.json"

def get_full_keys():
    """دروستکردنی لیستی تەواوی ٤٠ کلیلەکە"""
    keys = {}
    # ٢٠ کلیلی مانگانە
    for i in range(1, 21):
        k = f"GOLD-MON-{i:02d}"
        keys[k] = {"plan": "مانگانە", "expiry": "2026-04-10", "device": None}
    # ٢٠ کلیلی ساڵانە
    for i in range(1, 21):
        k = f"GOLD-YEAR-{i:02d}"
        keys[k] = {"plan": "ساڵانە", "expiry": "2027-03-10", "device": None}
    # کلیلی بەڕێوەبەر
    keys["DR-KIRKUK-2026"] = {"plan": "بەڕێوەبەر (VIP)", "expiry": "2030-01-01", "device": None}
    return keys

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            current_db = json.load(f)
        # ئەگەر کلیلە نوێیەکان لە فایلەکە نەبوون، زیادکرانیان بۆ بکە
        full_keys = get_full_keys()
        updated = False
        for k, v in full_keys.items():
            if k not in current_db:
                current_db[k] = v
                updated = True
        if updated:
            save_db(current_db)
        return current_db
    else:
        db = get_full_keys()
        save_db(db)
        return db

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f)

db_keys = load_db()

# --- ٢. دیزاین و ڕووکاری شاهانە ---
st.set_page_config(page_title="Golden Receipt VIP", page_icon="📜", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .hero-box {
        background: linear-gradient(135deg, #001a33 0%, #003366 100%);
        color: white; padding: 40px 25px; border-radius: 20px; border-bottom: 8px solid #d4af37;
        text-align: center; direction: rtl; margin-bottom: 30px; box-shadow: 0px 10px 20px rgba(0,0,0,0.2);
    }
    .price-card {
        background: white; padding: 20px; border-radius: 15px; border: 2px solid #d4af37;
        text-align: center; direction: rtl; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .payment-info {
        background: #fff3cd; color: #856404; padding: 25px; border-radius: 15px;
        border: 2px dashed #d4af37; text-align: center; direction: rtl; font-weight: bold; margin-top: 20px;
    }
    .receipt-card { 
        background: white; padding: 30px; border-radius: 20px; border: 4px solid #d4af37; 
        box-shadow: 0px 15px 35px rgba(0,0,0,0.1); direction: rtl; font-family: 'Tahoma', sans-serif;
    }
    .stButton>button { 
        border-radius: 12px; background-color: #003366; color: white; 
        font-weight: bold; height: 3.5em; border: 2px solid #d4af37; width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ٣. ڕووکاری پێشوازی و کڕین ---
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

if not st.session_state['auth']:
    st.markdown("""
    <div class="hero-box">
        <h1 style="color: #d4af37; font-size: 38px; margin-bottom: 15px;">📜 گۆڵدن ڕیسێت VIP</h1>
        <p style="font-size: 21px; line-height: 1.7;">
            ئێمە متمانە و شکۆ دەبەخشین بە بزنسەکەت. وەسڵەکانمان تەنها کاغەز نین، بەڵکو پەنجەمۆری پرۆفیشناڵی تۆن لەلای کڕیار.
            بە سیستمێکی زیرەک و پارێزراو، کارەکانت ڕێکبخە و وەسڵی شاهانە ببڕە.
        </p>
        <p style="color: #d4af37; font-size: 16px;">💎 یەک مۆبایل | 💎 کاتی دیاریکراو | 💎 دیزاینی ناوازە</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🖼️ پێشانگای وەسڵ", "💰 کڕینی کلیل", "🔐 چالاککردنی ئەژمار"])
    
    with tab1:
        st.markdown(f"""
        <div class="receipt-card">
            <h2 style="text-align:center; color:#003366; margin-bottom:5px;">گۆڵدن دێلیڤەری</h2>
            <p style="text-align:center; font-size:12px; color:#666;">کەرکوک - گەڕەکی ئازادی | 📞 07801352003</p>
            <hr style="border: 1px solid #d4af37;">
            <p><b>بۆ بەڕێز:</b> کڕیاری نموونەیی</p>
            <p><b>کاڵا:</b> وەسڵی ساڵانەی VIP</p>
            <h3 style="color:#cc0000; text-align:left; font-size:24px;">کۆی گشتی: ١٥,٠٠٠ دینار</h3>
            <hr style="border: 0.5px dashed #ccc;">
            <p style="text-align:center; font-size:11px; color:#888;">ئەمە نموونەیەکە، وەسڵی تۆ بە لۆگۆ و ناوی خۆت دەبێت</p>
        </div>
        """, unsafe_allow_html=True)

    with tab2:
        st.markdown("<h3 style='text-align:center;'>نرخی کلیلەکان</h3>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1: st.markdown("""<div class="price-card"><h3>مانگانە</h3><h2 style="color:#003366;">5,000 IQD</h2><p>٣٠ ڕۆژ</p></div>""", unsafe_allow_html=True)
        with c2: st.markdown("""<div class="price-card"><h3>ساڵانە</h3><h2 style="color:#d4af37;">15,000 IQD</h2><p>٣٦٥ ڕۆژ</p></div>""", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="payment-info">
            💳 ناردنی باڵانسی (ئاسیا، کۆرەک، زین) بۆ ژمارەی:<br>
            <span style="font-size: 26px; color: #003366;">07801352003</span><br>
            <hr style="border-color:#d4af37;">
            دوای ناردن، وێنەی پسوڵەکە بنێرە بۆ واتسئەپی هەمان ژمارە بۆ وەرگرتنی کلیلەکەت.
        </div>
        """, unsafe_allow_html=True)

    with tab3:
        user_key = st.text_input("کۆدی چالاککردن (Key)", type="password").strip().upper()
        if st.button("چوونەژوورەوە"):
            if user_key in db_keys:
                k_data = db_keys[user_key]
                expiry_dt = datetime.strptime(k_data["expiry"], "%Y-%m-%d").date()
                dev_id = st.context.headers.get("User-Agent")
                
                if date.today() > expiry_dt:
                    st.error(f"❌ ئەم کۆدە لە ڕێکەوتی {k_data['expiry']} بەسەرچووە.")
                elif k_data["device"] is not None and k_data["device"] != dev_id:
                    st.error("❌ ئەم کۆدە تەنها لەسەر یەک مۆبایل کار دەکات!")
                else:
                    db_keys[user_key]["device"] = dev_id
                    save_db(db_keys)
                    st.session_state['auth'] = True
                    st.session_state['u_info'] = k_data
                    st.rerun()
            else:
                st.error("❌ کۆدەکە هەڵەیە یان بوونی نییە.")
    st.stop()

# --- ٤. شاشەی کارکردنی سەرەکی ---
st.success(f"🌟 بەخێربێیت! پلان: {st.session_state['u_info']['plan']} | بەسەرچوون: {st.session_state['u_info']['expiry']}")

with st.expander("📝 زانیاری وەسڵ", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        shop_n = st.text_input("ناوی دوکان", "گۆڵدن دێلیڤەری")
        phone_n = st.text_input("مۆبایل", "07XXXXXXXXX")
    with col2:
        addr = st.text_input("ناونیشان", "کەرکوک")
        cust_n = st.text_input("ناوی کڕیار")
    item_n = st.text_input("کاڵا")
    price_n = st.number_input("نرخ", min_value=0, step=250)

if st.button("✨ دروستکردنی وەسڵ"):
    if not cust_n: st.warning("ناوی کڕیار بنووسە")
    else:
        st.markdown(f"""
        <div class="receipt-card">
            <h2 style="text-align:center; color:#003366;">{shop_n}</h2>
            <p style="text-align:center; font-size:13px; color:#666;">{addr} | 📞 {phone_n}</p>
            <hr style="border: 1px solid #d4af37;">
            <div style="display: flex; justify-content: space-between;">
                <span><b>بەروار:</b> {date.today()}</span>
                <span><b>بۆ بەڕێز:</b> {cust_n}</span>
            </div>
            <div style="margin-top:20px; padding:15px; background:#f9f9f9; border-radius:12px; border: 1px solid #eee;">
                <p><b>کاڵا:</b> {item_n}</p>
                <h3 style="color:#cc0000; text-align:left;">کۆی گشتی: {price_n:,} دینار</h3>
            </div>
            <p style="text-align:center; font-size:12px; margin-top:15px; color:#888;">سوپاس بۆ متمانەتان!</p>
        </div>
        """, unsafe_allow_html=True)
        st.balloons()
