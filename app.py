import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import date

# --- 1. ڕێکخستنی لاپەڕە ---
st.set_page_config(page_title="Golden Receipt VIP", page_icon="📜")

# دیزاینی CSS بۆ جوانکاری
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 10px; background-color: #003366; color: white; font-weight: bold; }
    h1, h2 { color: #003366; text-align: center; font-family: 'Tahoma'; }
    .expiry-text { color: #d4af37; font-weight: bold; text-align: center; font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. داتابەیسی کلیلەکان و کاتی بەسەرچوون ---
# تێبینی: بەروارەکان بەم شێوەیەن (ساڵ، مانگ، ڕۆژ)
if 'valid_keys' not in st.session_state:
    st.session_state['valid_keys'] = {
        # مانگانە - تا مانگێکی تر
        "GOLD-MON-8821-X": {"plan": "مانگانە", "expiry": date(2026, 4, 10)},
        "GOLD-MON-4432-Y": {"plan": "مانگانە", "expiry": date(2026, 4, 15)},
        
        # ساڵانە - تا ساڵی داهاتوو
        "GOLD-25K-YEAR-001": {"plan": "ساڵانە", "expiry": date(2027, 3, 10)},
        "DR-KIRKUK-2026": {"plan": "ساڵانە", "expiry": date(2027, 3, 10)}
    }

# --- 3. سیستەمی چوونەژوورەوە ---
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

if not st.session_state['auth']:
    st.title("🔑 چالاککردنی وەسڵی گۆڵدن")
    st.info("💳 بۆ کڕینی کلیل، وێنەی کارت بنێرە بۆ واتسئەپ: 07801352003")
    
    user_key = st.text_input("کلیلەکەت لێرە بنووسە (Activation Key)", type="password").strip().upper()
    
    if st.button("تەئکیدکردنەوە"):
        if user_key in st.session_state['valid_keys']:
            key_data = st.session_state['valid_keys'][user_key]
            if date.today() <= key_data["expiry"]:
                st.session_state['auth'] = True
                st.session_state['key_info'] = key_data
                st.success("بە سەرکەوتوویی چالاک بوو!")
                st.rerun()
            else:
                st.error("⚠️ ببوورە، ماوەی ئەم کلیلە بەسەرچووە!")
        else:
            st.error("کلیلەکە هەڵەیە!")
    st.stop()

# --- 4. شاشەی کارکردن ---
today = date.today()
expiry_date = st.session_state['key_info']["expiry"]
days_left = (expiry_date - today).days

st.title("📜 دروستکەری وەسڵی دیجیتاڵی")
st.markdown(f"<p class='expiry-text'>⏳ تەنها {days_left} ڕۆژت ماوە بۆ بەسەرچوونی بەژدارییەکەت</p>", unsafe_allow_html=True)

if st.sidebar.button("چوونە دەرەوە"):
    st.session_state['auth'] = False
    st.rerun()

# فۆرمی وەسڵ بە کوردی
with st.expander("📝 پڕکردنەوەی زانیاری وەسڵ", expanded=True):
    shop = st.text_input("ناوی دوکان/پەیج", "گۆڵدن دێلیڤەری")
    cust = st.text_input("ناوی کڕیار")
    item = st.text_input("جۆری کاڵا")
    price = st.number_input("نرخی کاڵا (دینار)", min_value=0, step=250)
    delivery = st.number_input("کرێی گەیاندن (دینار)", min_value=0, step=250)
    logo = st.file_uploader("لۆگۆی تایبەت", type=['png', 'jpg', 'jpeg'])
    
    btn_create = st.button("✨ دروستکردنی وەسڵ")

# --- 5. دروستکردنی وێنەی وەسڵەکە بە دیزاینی کوردی ---
if btn_create:
    if not cust:
        st.warning("تکایە ناوی کڕیار بنووسە")
    else:
        # دروستکردنی وێنە
        img = Image.new('RGB', (500, 750), color='#ffffff')
        draw = ImageDraw.Draw(img)
        
        # دیزاینی چوارچێوە
        draw.rectangle([10, 10, 490, 740], outline="#d4af37", width=15)
        draw.rectangle([25, 25, 475, 725], outline="#003366", width=2)
        
        # نووسینەکان (تێبینی: لێرەدا وەک نموونە بەکارھاتووە، بۆ ئەنجامی باشتر دەبێت فۆنتێکی کوردی .ttf باربکەیت)
        draw.text((150, 50), "GOLDEN RECEIPT", fill="#003366")
        
        # بەشە کوردییەکان (بۆ دیزاین)
        y_pos = 150
        draw.text((50, y_pos), f"SHOP: {shop}", fill="#000000")
        draw.text((50, y_pos+50), f"CUSTOMER: {cust}", fill="#000000")
        draw.line((50, y_pos+100, 450, y_pos+100), fill="#d4af37", width=2)
        
        draw.text((50, y_pos+150), f"ITEM: {item}", fill="#000000")
        draw.text((50, y_pos+200), f"PRICE: {price:,} IQD", fill="#000000")
        draw.text((50, y_pos+250), f"DELIVERY: {delivery:,} IQD", fill="#000000")
        
        draw.line((50, y_pos+320, 450, y_pos+320), fill="#003366", width=4)
        total = price + delivery
        draw.text((50, y_pos+350), f"TOTAL: {total:,} IQD", fill="#cc0000")
        
        draw.text((140, 680), "سوپاس بۆ متمانەکەتان", fill="#888888")

        if logo:
            user_l = Image.open(logo).convert("RGBA").resize((100, 100))
            img.paste(user_l, (360, 45), user_l)

        st.image(img, caption="وەسڵەکە ئامادەیە", use_container_width=True)
        
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        st.download_button("💾 داگرتنی وەسڵ", buf.getvalue(), f"receipt_{cust}.png", "image/png")
