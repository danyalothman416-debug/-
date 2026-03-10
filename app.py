import streamlit as st
from PIL import Image, ImageDraw
import io
from datetime import date

# --- 1. ڕێکخستنی لاپەڕە ---
st.set_page_config(page_title="Golden Receipt VIP", page_icon="📜", layout="centered")

# ستایل بۆ جوانکردنی ڕووکاری سایتەکە
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { width: 100%; border-radius: 10px; background-color: #003366; color: white; height: 3em; font-weight: bold; }
    h1 { color: #003366; text-align: center; border-bottom: 3px solid #d4af37; padding-bottom: 10px; font-family: 'Tahoma'; }
    .expiry-info { background: #003366; color: #d4af37; padding: 15px; border-radius: 10px; text-align: center; font-weight: bold; margin-bottom: 20px; }
    .receipt-box { border: 2px dashed #003366; padding: 20px; border-radius: 10px; background: white; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. داتابەیسی کلیلەکان و کاتی بەسەرچوون ---
if 'valid_keys' not in st.session_state:
    st.session_state['valid_keys'] = {
        # مانگانە
        "GOLD-MON-8821-X": {"plan": "مانگانە", "expiry": date(2026, 4, 10)},
        "GOLD-MON-4432-Y": {"plan": "مانگانە", "expiry": date(2026, 4, 15)},
        # ساڵانە
        "GOLD-25K-YEAR-001": {"plan": "ساڵانە", "expiry": date(2027, 3, 10)},
        "DR-KIRKUK-2026": {"plan": "ساڵانە", "expiry": date(2027, 3, 10)}
    }

# --- 3. سیستەمی چوونەژوورەوە ---
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

if not st.session_state['auth']:
    st.title("🔑 چالاککردنی وەسڵی گۆڵدن")
    st.info("💳 بۆ کڕینی کلیل، وێنەی کارت بنێرە بۆ واتسئەپ: 07801352003")
    
    user_key = st.text_input("Activation Key", type="password").strip().upper()
    
    if st.button("تەئکیدکردنەوە"):
        if user_key in st.session_state['valid_keys']:
            key_data = st.session_state['valid_keys'][user_key]
            if date.today() <= key_data["expiry"]:
                st.session_state['auth'] = True
                st.session_state['key_info'] = key_data
                st.rerun()
            else:
                st.error("⚠️ ماوەی ئەم کلیلە بەسەرچووە!")
        else:
            st.error("کلیلەکە هەڵەیە!")
    st.stop()

# --- 4. شاشەی کارکردن ---
today = date.today()
expiry_date = st.session_state['key_info']["expiry"]
days_left = (expiry_date - today).days

st.title("📜 دروستکەری وەسڵی دیجیتاڵی")
st.markdown(f"<div class='expiry-info'>⏳ ماوەی ماوە: {max(0, days_left)} ڕۆژ (پلان: {st.session_state['key_info']['plan']})</div>", unsafe_allow_html=True)

if st.sidebar.button("چوونە دەرەوە"):
    st.session_state['auth'] = False
    st.rerun()

# فۆرمی وەرگرتنی زانیارییەکان
with st.form("my_form"):
    shop = st.text_input("ناوی دوکان/پەیج", "گۆڵدن دێلیڤەری")
    cust = st.text_input("ناوی کڕیار")
    item = st.text_input("جۆری کاڵا")
    price = st.number_input("نرخی کاڵا (دینار)", min_value=0, step=250)
    delivery = st.number_input("کرێی گەیاندن (دینار)", min_value=0, step=250)
    logo = st.file_uploader("بارکردنی لۆگۆ", type=['png', 'jpg', 'jpeg'])
    
    submit = st.form_submit_button("✨ دروستکردنی وەسڵ")

# --- 5. دروستکردن و پیشاندان ---
if submit:
    if not cust or not item:
        st.warning("تکایە ناوی کڕیار و کاڵا بنووسە")
    else:
        # دروستکردنی وێنەی وەسڵەکە (بۆ دیزاین)
        img = Image.new('RGB', (500, 400), color='#ffffff')
        draw = ImageDraw.Draw(img)
        draw.rectangle([10, 10, 490, 390], outline="#d4af37", width=12) # چوارچێوەی زێڕین
        draw.text((150, 40), "GOLDEN RECEIPT", fill="#003366")
        
        if logo:
            user_logo = Image.open(logo).convert("RGBA").resize((100, 100))
            img.paste(user_logo, (350, 30), user_logo)

        # پیشاندانی وێنەکە
        st.image(img, use_container_width=True)

        # پیشاندانی زانیارییەکان بە زمانی کوردی (بە شێوەی دەق بۆ ئەوەی تێک نەچێت)
        st.markdown(f"""
        <div class="receipt-box">
            <h2 style='text-align: center; color: #003366;'>📋 زانیاری وەسڵ</h2>
            <p style='text-align: right;'><b>ناوی دوکان:</b> {shop}</p>
            <p style='text-align: right;'><b>ناوی کڕیار:</b> {cust}</p>
            <p style='text-align: right;'><b>کاڵا:</b> {item}</p>
            <hr>
            <p style='text-align: right;'><b>نرخی کاڵا:</b> {price:,} دینار</p>
            <p style='text-align: right;'><b>گەیاندن:</b> {delivery:,} دینار</p>
            <h3 style='text-align: right; color: #cc0000;'><b>کۆی گشتی:</b> {price + delivery:,} دینار</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.success("وەسڵەکە بە سەرکەوتوویی دروست کرا! دەتوانیت وێنەی شاشەکە (Screenshot) بگریت و بۆ کڕیاری بنێریت.")
