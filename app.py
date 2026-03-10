import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

# --- 1. ڕێکخستنی شێوە و دیزاینی لاپەڕە ---
st.set_page_config(page_title="Golden Receipt VIP", page_icon="📜", layout="centered")

# ستایلێکی جوان بۆ نووسینەکان
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #003366; color: white; }
    h1 { color: #003366; text-align: center; border-bottom: 2px solid #d4af37; padding-bottom: 10px; }
    .stAlert { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. داتابەیسی کلیلەکان ---
if 'valid_keys' not in st.session_state:
    st.session_state['valid_keys'] = {
        "GOLD-MON-1": "مانگانە", 
        "GOLD-25K-YEAR-1": "ساڵانە",
        "DR-KIRKUK-2026": "ساڵانە"
    }

# --- 3. قۆناغی یەکەم: قوفڵ و کلیل (Login) ---
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

if not st.session_state['auth']:
    st.title("📜 سیستەمی وەسڵی گۆڵدن")
    st.subheader("تکایە کلیلەکەت داخل بکە بۆ دەستپێکردن")
    
    with st.container():
        st.info("💳 بۆ کڕینی کلیل، کارت بنێرە بۆ واتسئەپ: 07801352003")
        user_key = st.text_input("Activation Key", type="password", placeholder="کلیلەکە لێرە بنووسە...")
        
        if st.button("پشکنینی کلیل"):
            if user_key in st.session_state['valid_keys']:
                st.session_state['auth'] = True
                st.session_state['plan'] = st.session_state['valid_keys'][user_key]
                st.success("بەخێربێیت! سیستەم چالاک بوو.")
                st.rerun()
            else:
                st.error("کلیلەکە هەڵەیە!")
    st.stop()

# --- 4. قۆناغی دووەم: ژووری کارکردن (Dashboard) ---
st.title("📜 دروستکەری وەسڵی دیجیتاڵی")
st.sidebar.markdown(f"### 👤 جۆری بەژداری: \n **{st.session_state['plan']}**")

with st.expander("📝 پڕکردنەوەی زانیاری وەسڵ", expanded=True):
    shop = st.text_input("ناوی دوکان/پەیج")
    cust = st.text_input("ناوی کڕیار")
    item = st.text_input("ناوی کاڵا")
    price = st.number_input("نرخ (دینار)", step=250)
    logo = st.file_uploader("بارکردنی لۆگۆ", type=['png', 'jpg'])
    
    btn_create = st.button("✨ دروستکردنی وەسڵی شیک")

# --- 5. قۆناغی سێیەم: دروستکردنی وێنەی وەسڵەکە ---
if btn_create:
    if not shop or not cust:
        st.warning("تکایە ناوی دوکان و کڕیار بنووسە")
    else:
        # دروستکردنی وێنە بە قەبارەی وەسڵ
        img = Image.new('RGB', (500, 700), color='#ffffff')
        draw = ImageDraw.Draw(img)
        
        # دیزاینی چوارچێوەی زێڕین
        draw.rectangle([15, 15, 485, 685], outline="#d4af37", width=10)
        draw.rectangle([25, 25, 475, 675], outline="#003366", width=2)
        
        # نووسینەکان (بە ئینگلیزی بۆ تێست، دواتر فۆنتی کوردی دادەنێین)
        draw.text((150, 50), "GOLDEN RECEIPT", fill="#003366")
        draw.text((60, 150), f"FROM: {shop.upper()}", fill="#000000")
        draw.text((60, 200), f"TO: {cust}", fill="#000000")
        draw.line((60, 250, 440, 250), fill="#d4af37", width=2)
        
        draw.text((60, 320), f"ITEM: {item}", fill="#000000")
        draw.text((60, 380), f"PRICE: {price:,} IQD", fill="#003366")
        
        draw.text((130, 600), "Thank you for your business!", fill="#666666")

        if logo:
            user_l = Image.open(logo).resize((100, 100))
            img.paste(user_l, (350, 40))

        st.image(img, caption="ئەمە شێوەی وەسڵەکەتە")
        
        # دوگمەی داگرتن
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        st.download_button("💾 داگرتنی وەسڵ", buf.getvalue(), f"{cust}.png", "image/png")
