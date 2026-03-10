import streamlit as st
from PIL import Image, ImageDraw
import io
from datetime import date

# --- 1. ڕێکخستنی شێوەی لاپەڕە ---
st.set_page_config(page_title="Golden Receipt VIP", page_icon="📜", layout="centered")

# دیزاینی CSS بۆ جوانکردنی ڕووکاری سایتەکە
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 10px; background-color: #003366; color: white; height: 3em; font-weight: bold; }
    h1 { color: #003366; text-align: center; border-bottom: 3px solid #d4af37; padding-bottom: 10px; }
    .stTextInput>div>div>input { text-align: center; }
    .expiry-text { color: #d4af37; font-weight: bold; text-align: center; font-size: 20px; background: #003366; padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. داتابەیسی کلیلەکان و کاتی بەسەرچوون ---
if 'valid_keys' not in st.session_state:
    st.session_state['valid_keys'] = {
        # مانگانە - تا 10ی نیسانی 2026
        "GOLD-MON-8821-X": {"plan": "مانگانە", "expiry": date(2026, 4, 10)},
        "GOLD-MON-4432-Y": {"plan": "مانگانە", "expiry": date(2026, 4, 10)},
        "GOLD-MON-1090-Z": {"plan": "مانگانە", "expiry": date(2026, 4, 10)},
        
        # ساڵانە - تا 10ی ئازاری 2027
        "GOLD-25K-YEAR-001": {"plan": "ساڵانە", "expiry": date(2027, 3, 10)},
        "GOLD-25K-YEAR-002": {"plan": "ساڵانە", "expiry": date(2027, 3, 10)},
        "DR-KIRKUK-2026": {"plan": "ساڵانە", "expiry": date(2027, 3, 10)}
    }

# --- 3. سیستەمی چوونەژوورەوە و قوفڵ ---
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

if not st.session_state['auth']:
    st.title("📜 سیستەمی وەسڵی گۆڵدن")
    st.write("### بەخێربێیت بۆ پێشکەوتووترین سیستەمی وەسڵ")
    
    with st.container():
        st.info("💳 بۆ کڕینی کلیل، وێنەی کارت بنێرە بۆ واتسئەپ: 07801352003")
        
        user_key = st.text_input("کلیلەکەت لێرە بنووسە (Activation Key)", type="password").strip().upper()
        
        if st.button("تەئکیدکردنەوە و چوونەژوورەوە"):
            if user_key in st.session_state['valid_keys']:
                key_data = st.session_state['valid_keys'][user_key]
                
                # پشکنینی بەسەرچوون
                if date.today() <= key_data["expiry"]:
                    st.session_state['auth'] = True
                    st.session_state['key_info'] = key_data
                    st.success("بە سەرکەوتوویی چالاک بوو!")
                    st.rerun()
                else:
                    st.error("⚠️ ببوورە، ماوەی ئەم کلیلە بەسەرچووە! تکایە نوێی بکەرەوە.")
            else:
                st.error("کلیلەکە هەڵەیە! تکایە دووبارە پشککنین بکەرەوە.")
    st.stop()

# --- 4. شاشەی کارکردن دوای چوونەژوورەوە ---
today = date.today()
expiry_date = st.session_state['key_info']["expiry"]
days_left = (expiry_date - today).days

st.title("📜 دروستکەری وەسڵی دیجیتاڵی")
st.markdown(f"<p class='expiry-text'>⏳ تەنها {max(0, days_left)} ڕۆژت ماوە بۆ بەسەرچوونی بەژدارییەکەت</p>", unsafe_allow_html=True)

if st.sidebar.button("چوونە دەرەوە (Logout)"):
    st.session_state['auth'] = False
    st.rerun()

# فۆرمی وەرگرتنی زانیارییەکان
with st.expander("📝 پڕکردنەوەی زانیاری وەسڵ", expanded=True):
    shop = st.text_input("ناوی دوکان یان پەیج", "گۆڵدن دێلیڤەری")
    cust = st.text_input("ناوی کڕیار")
    item = st.text_input("جۆری کاڵا")
    price = st.number_input("نرخی کاڵا (دینار)", min_value=0, step=250)
    delivery = st.number_input("کرێی گەیاندن (دینار)", min_value=0, step=250)
    logo = st.file_uploader("بارکردنی لۆگۆی تایبەت (ئارەزوومەندانە)", type=['png', 'jpg', 'jpeg'])
    
    btn_create = st.button("✨ دروستکردنی وەسڵ")

# --- 5. دروستکردنی وێنەی وەسڵەکە ---
if btn_create:
    if not cust or not item:
        st.warning("تکایە ناوی کڕیار و کاڵا بنووسە")
    else:
        img = Image.new('RGB', (500, 700), color='#ffffff')
        draw = ImageDraw.Draw(img)
        
        # دیزاینی چوارچێوە
        draw.rectangle([10, 10, 490, 690], outline="#d4af37", width=12) 
        draw.rectangle([22, 22, 478, 678], outline="#003366", width=2)
        
        # نووسینەکان (بە ئینگلیزی بۆ وێنەکە تا فۆنتت بۆ دانەنێم)
        draw.text((150, 40), "GOLDEN RECEIPT", fill="#003366")
        draw.text((50, 140), f"FROM: {shop}", fill="#000000")
        draw.text((50, 180), f"TO: {cust}", fill="#000000")
        draw.line((50, 230, 450, 230), fill="#d4af37", width=2)
        
        draw.text((50, 280), f"ITEM: {item}", fill="#000000")
        draw.text((50, 330), f"PRICE: {price:,} IQD", fill="#000000")
        draw.text((50, 380), f"DELIVERY: {delivery:,} IQD", fill="#000000")
        
        draw.line((50, 450, 450, 450), fill="#003366", width=3)
        total = price + delivery
        draw.text((50, 490), f"TOTAL: {total:,} IQD", fill="#cc0000")
        
        draw.text((150, 630), "Thank you for choosing us!", fill="#888888")

        if logo:
            user_l = Image.open(logo).convert("RGBA").resize((100, 100))
            img.paste(user_l, (360, 40), user_l)

        st.image(img, caption="وەسڵەکەت ئامادەیە", use_container_width=True)
        
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        st.download_button(label="💾 داگرتنی وەسڵ", data=buf.getvalue(), file_name=f"Receipt_{cust}.png", mime="image/png")
