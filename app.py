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
        # لێرە کلیلەکان و بەرواری بەسەرچوونیان دیاری دەکرێت
        initial_db = {
            # --- 📦 کلیلە مانگانەکان (بۆ ماوەی ٣٠ ڕۆژ - تا ١٠ی نیسانی ٢٠٢٦) ---
            "GOLD-MON-8821-X": {"plan": "مانگانە", "expiry": "2026-04-10", "device": None},
            "GOLD-MON-4432-Y": {"plan": "مانگانە", "expiry": "2026-04-10", "device": None},
            
            # --- 🌟 کلیلە ساڵانەکان (بۆ ماوەی ١ ساڵ - تا ١٠ی ئازاری ٢٠٢٧) ---
            "GOLD-25K-YEAR-001": {"plan": "ساڵانە", "expiry": "2027-03-10", "device": None},
            "GOLD-25K-YEAR-002": {"plan": "ساڵانە", "expiry": "2027-03-10", "device": None},
            
            # --- 👑 کلیلی بەڕێوەبەر (بۆ خۆت - هەمیشەیی) ---
            "DR-KIRKUK-2026": {"plan": "بەڕێوەبەر (VIP)", "expiry": "2030-01-01", "device": None}
        }
        save_db(initial_db)
        return initial_db

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f)

db_keys = load_db()

# --- ٢. دیزاین و وەسفی ڕووکار ---
st.set_page_config(page_title="Golden Receipt VIP", page_icon="📜")

st.markdown("""
    <style>
    .description-box {
        background: linear-gradient(135deg, #003366 0%, #001a33 100%);
        color: white; padding: 25px; border-radius: 15px; border-bottom: 5px solid #d4af37;
        text-align: center; margin-bottom: 20px; direction: rtl;
    }
    .receipt-card { 
        background: white; padding: 25px; border-radius: 20px; border: 4px solid #d4af37; 
        box-shadow: 0px 10px 25px rgba(0,0,0,0.1); direction: rtl; font-family: 'Tahoma', sans-serif;
        margin: auto; width: 90%;
    }
    .status-tag { background: #003366; color: #d4af37; padding: 5px 15px; border-radius: 20px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- ٣. ڕووکاری پێشوازی و چوونەژوورەوە ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    st.markdown("""
    <div class="description-box">
        <h1 style="color: #d4af37; margin-bottom: 10px;">📜 سیستەمی وەسڵی گۆڵدن VIP</h1>
        <p style="font-size: 18px;">پسپۆڕ لە ڕێکخستنی وەسڵی شیک بۆ پەیجەکان</p>
        <p style="font-size: 14px; color: #d4af37;">🔒 یەک مۆبایل | ⏳ کاتی دیاریکراو | 💎 دیزاینی شاهانە</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🖼️ وەسڵی نموونەیی", "🔐 چالاککردنی ئەژمار"])
    
    with tab1:
        st.markdown("<h3 style='text-align:center; color:#003366;'>شێوازی وەسڵەکانمان:</h3>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="receipt-card">
            <h2 style="text-align:center; color:#003366; margin-bottom:0;">گۆڵدن دێلیڤەری (نموونە)</h2>
            <p style="text-align:center; font-size:12px; color:#666;">کەرکوک - شەقامی سەرەکی | 07700000000</p>
            <hr style="border: 1px solid #d4af37;">
            <p><b>بۆ بەڕێز:</b> کڕیاری نموونەیی</p>
            <p><b>کاڵا:</b> نموونەی ساڵانە/مانگانە</p>
            <h3 style="color:#cc0000; text-align:left;">کۆی گشتی: ٥٠,٠٠٠ دینار</h3>
            <hr style="border: 0.5px dashed #ccc;">
            <p style="text-align:center; font-size:11px; color: #999;">تێبینی: لۆگۆ و زانیارییەکان دوای چالاککردن گۆڕاو دەبن</p>
        </div>
        """, unsafe_allow_html=True)

    with tab2:
        user_key = st.text_input("کۆدی چالاککردن داخڵ بکە", type="password").strip().upper()
        if st.button("پشکنینی کۆد"):
            if user_key in db_keys:
                k_data = db_keys[user_key]
                expiry_date = datetime.strptime(k_data["expiry"], "%Y-%m-%d").date()
                dev_id = st.context.headers.get("User-Agent")
                
                # پشکنینی بەرواری بەسەرچوون
                if date.today() > expiry_date:
                    st.error(f"❌ ببوورە! ماوەی ئەم کۆدە لە {k_data['expiry']} بەسەرچووە.")
                else:
                    # پشکنینی قوفڵی مۆبایل
                    if k_data["device"] is None:
                        db_keys[user_key]["device"] = dev_id
                        save_db(db_keys)
                        st.session_state['authenticated'] = True
                        st.session_state['user_info'] = k_data
                        st.rerun()
                    elif k_data["device"] == dev_id:
                        st.session_state['authenticated'] = True
                        st.session_state['user_info'] = k_data
                        st.rerun()
                    else:
                        st.error("❌ ئەم کۆدە تەنها لەسەر یەک مۆبایل کار دەکات و پێشتر بەکارهێنراوە.")
            else:
                st.error("❌ کۆدەکە هەڵەیە یان بوونی نییە.")
    st.stop()

# --- ٤. شاشەی وەسڵ بڕین (دوای چوونەژوورەوە) ---
expiry_val = st.session_state['user_info']['expiry']
st.markdown(f"<div style='text-align:center;'><span class='status-tag'>💎 پلان: {st.session_state['user_info']['plan']}</span> | <span class='status-tag'>⏳ بەسەرچوون: {expiry_val}</span></div>", unsafe_allow_html=True)

with st.expander("📝 پڕکردنەوەی وەسڵ", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        shop_n = st.text_input("ناوی پەیج/دوکان", "گۆڵدن دێلیڤەری")
        phone = st.text_input("ژمارەی مۆبایل", "07XXXXXXXXX")
    with col2:
        address = st.text_input("ناونیشان", "کەرکوک")
        cust_n = st.text_input("ناوی کڕیار")
    
    item_n = st.text_input("جۆری کاڵا")
    price = st.number_input("نرخی کۆتایی (دینار)", min_value=0, step=250)

if st.button("✨ دروستکردنی وەسڵی کۆتایی"):
    if not cust_n or not phone:
        st.warning("تکایە زانیارییەکان پڕ بکەرەوە")
    else:
        st.markdown(f"""
        <div class="receipt-card">
            <h2 style="text-align:center; color:#003366; margin-bottom:5px;">{shop_n}</h2>
            <p style="text-align:center; font-size:13px; color:#666;">{address} | 📞 {phone}</p>
            <hr style="border: 1px solid #d4af37;">
            <div style="display: flex; justify-content: space-between; margin-top:10px;">
                <span><b>بەروار:</b> {date.today()}</span>
                <span><b>بۆ بەڕێز:</b> {cust_n}</span>
            </div>
            <div style="margin-top:20px; padding:15px; background:#f9f9f9; border-radius:10px; border: 1px solid #eee;">
                <p style="font-size:16px;"><b>کاڵا:</b> {item_n}</p>
                <h3 style="color:#cc0000; text-align:left; font-size:20px;">کۆی گشتی: {price:,} دینار</h3>
            </div>
            <p style="text-align:center; font-size:12px; margin-top:15px; color:#888;">سوپاس بۆ کڕینەکەتان!</p>
        </div>
        """, unsafe_allow_html=True)
        st.balloons()
