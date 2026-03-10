import streamlit as st
import json
import os
from datetime import date

# --- ١. ڕێکخستنی داتابەیس و قوفڵی مۆبایل ---
DB_FILE = "keys_database.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    else:
        # کلیلە سەرەتاییەکان (ئەگەر فایلەکە نەبوو دروستی دەکات)
        initial_db = {
            "GOLD-MON-8821-X": {"plan": "مانگانە", "expiry": "2026-04-10", "device": None},
            "GOLD-MON-4432-Y": {"plan": "مانگانە", "expiry": "2026-04-10", "device": None},
            "GOLD-25K-YEAR-001": {"plan": "ساڵانە", "expiry": "2027-03-10", "device": None},
            "DR-KIRKUK-2026": {"plan": "بەڕێوەبەر (VIP)", "expiry": "2030-01-01", "device": None}
        }
        save_db(initial_db)
        return initial_db

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f)

db_keys = load_db()

# --- ٢. ڕێکخستنی لاپەڕە و دیزاینی VIP ---
st.set_page_config(page_title="Golden Receipt VIP", page_icon="📜", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { border-radius: 12px; background-color: #003366; color: white; font-weight: bold; height: 3.5em; border: 2px solid #d4af37; }
    .receipt-card { 
        background: white; padding: 25px; border-radius: 20px; border: 4px solid #d4af37; 
        box-shadow: 0px 10px 25px rgba(0,0,0,0.1); direction: rtl; font-family: 'Tahoma', sans-serif;
        margin: auto; width: 90%;
    }
    .description-box {
        background: linear-gradient(135deg, #003366 0%, #001a33 100%);
        color: white; padding: 25px; border-radius: 15px; border-bottom: 5px solid #d4af37;
        text-align: center; margin-bottom: 20px; direction: rtl;
    }
    .feature-list { text-align: right; font-size: 14px; list-style-type: '⭐'; padding-right: 20px; color: #d4af37; }
    </style>
    """, unsafe_allow_html=True)

# --- ٣. ڕووکاری پێشوازی و چوونەژوورەوە ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    st.markdown("""
    <div class="description-box">
        <h1 style="color: #d4af37; margin-bottom: 10px;">📜 سیستەمی وەسڵی گۆڵدن VIP</h1>
        <p style="font-size: 18px;">پسپۆڕ لە دروستکردنی وەسڵی شیک و شاهانە بۆ پەیجەکان</p>
        <div class="feature-list">
            <li>دیزاینێکی پرۆفیشناڵ کە متمانەی کڕیار زیاد دەکات.</li>
            <li>قوفڵکردنی کۆد لەسەر تەنها یەک مۆبایل بۆ پاراستنی مافەکانت.</li>
            <li>پشتیگیری تەواوی زمانی کوردی بێ تێکچوونی پیتەکان.</li>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🖼️ نموونەی وەسڵەکان", "🔐 چالاککردنی ئەژمار"])
    
    with tab1:
        st.markdown("<h3 style='text-align:center; color:#003366;'>وەسڵەکانت بەم شێوەیە دەردەچن:</h3>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="receipt-card">
            <h2 style="text-align:center; color:#003366;">گۆڵدن دێلیڤەری (نموونە)</h2>
            <p style="text-align:center; font-size:12px; color:#666;">کەرکوک - شەقامی سەرەکی | 07700000000</p>
            <hr style="border: 1px solid #d4af37;">
            <p><b>بۆ بەڕێز:</b> کڕیاری نموونەیی</p>
            <p><b>کاڵا:</b> تاقیکردنەوەی سیستەم</p>
            <h3 style="color:#cc0000; text-align:left;">کۆی گشتی: ٥٠,٠٠٠ دینار</h3>
            <hr style="border: 0.5px dashed #ccc;">
            <p style="text-align:center; font-size:11px;">دوای چالاککردنی کۆد، دەتوانیت ناونیشان و لۆگۆی خۆت دابنێیت</p>
        </div>
        """, unsafe_allow_html=True)

    with tab2:
        user_key = st.text_input("کۆدی چالاککردن داخڵ بکە", type="password").strip().upper()
        if st.button("بەردەوامبە"):
            if user_key in db_keys:
                k_data = db_keys[user_key]
                dev_id = st.context.headers.get("User-Agent")
                
                # پشکنینی قوفڵی مۆبایل لە داتابەیس
                if k_data["device"] is None:
                    # قوفڵکردنی یەکەمجار
                    db_keys[user_key]["device"] = dev_id
                    save_db(db_keys)
                    st.session_state['authenticated'] = True
                    st.session_state['user_info'] = k_data
                    st.rerun()
                elif k_data["device"] == dev_id:
                    # هەمان مۆبایلە
                    st.session_state['authenticated'] = True
                    st.session_state['user_info'] = k_data
                    st.rerun()
                else:
                    # مۆبایلێکی ترە
                    st.error("❌ ببوورە! ئەم کۆدە تەنها لەسەر یەک مۆبایل کار دەکات و پێشتر بەکارهێنراوە.")
            else:
                st.error("❌ کۆدەکە هەڵەیە یان بوونی نییە.")
    st.stop()

# --- ٤. شاشەی کارکردنی سەرەکی (دوای چوونەژوورەوە) ---
st.success(f"🌟 بەخێربێیتەوە! پلانی تۆ: {st.session_state['user_info']['plan']}")

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
    if not cust_n or not phone:
        st.warning("تکایە ناوی کڕیار و ژمارەی مۆبایل پڕ بکەرەوە")
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
            <p style="text-align:center; font-size:12px; margin-top:15px; color:#888;">سوپاس بۆ کڕینەکەتان، هەمیشە چاوەڕێتانین!</p>
        </div>
        """, unsafe_allow_html=True)
        st.balloons()
        st.info("📸 ئێستا سکرین شۆتی وەسڵەکە بکە و بۆ کڕیاری بنێرە.")
