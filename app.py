import streamlit as st
from PIL import Image, ImageDraw
import io

# --- 1. ڕێکخستنی شێوە و دیزاینی لاپەڕە ---
st.set_page_config(page_title="Golden Receipt VIP", page_icon="📜", layout="centered")

# ستایل بۆ جوانکردنی ڕووکاری سایتەکە
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { width: 100%; border-radius: 10px; background-color: #003366; color: white; height: 3em; font-weight: bold; }
    h1 { color: #003366; text-align: center; border-bottom: 3px solid #d4af37; padding-bottom: 10px; }
    .stTextInput>div>div>input { text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. داتابەیسی کلیلەکان (بە پیتە گەورەکان پاشەکەوت کراون) ---
if 'valid_keys' not in st.session_state:
    st.session_state['valid_keys'] = {
        # مانگانە - 5,000 باڵانس
        "GOLD-MON-8821-X": "مانگانە",
        "GOLD-MON-4432-Y": "مانگانە",
        "GOLD-MON-1090-Z": "مانگانە",
        "GOLD-MON-7756-A": "مانگانە",
        "GOLD-MON-3312-B": "مانگانە",
        
        # ساڵانە - 25,000 باڵانس
        "GOLD-25K-YEAR-001": "ساڵانە",
        "GOLD-25K-YEAR-002": "ساڵانە",
        "GOLD-25K-YEAR-003": "ساڵانە",
        "GOLD-25K-YEAR-004": "ساڵانە",
        "GOLD-25K-YEAR-005": "ساڵانە",
        "DR-KIRKUK-2026": "ساڵانە"
    }

# --- 3. سیستەمی قوفڵ و پاراستن (Login) ---
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

if not st.session_state['auth']:
    st.title("📜 سیستەمی وەسڵی گۆڵدن")
    st.write("### بەخێربێیت بۆ پێشکەوتووترین سیستەمی وەسڵ لە کەرکوک")
    
    with st.container():
        st.info("💳 بۆ کڕینی کلیل (Key)، کارت بنێرە بۆ واتسئەپ: 07801352003")
        
        # .strip().upper() بۆ ئەوەی پیتە بچووک و بۆشاییەکان کێشە دروست نەکەن
        user_key = st.text_input("کلیلەکەت لێرە بنووسە (Activation Key)", type="password").strip().upper()
        
        if st.button("تەئکیدکردنەوە و چوونەژوورەوە"):
            if user_key in st.session_state['valid_keys']:
                st.session_state['auth'] = True
                st.session_state['plan'] = st.session_state['valid_keys'][user_key]
                st.success("بە سەرکەوتوویی چالاک بوو!")
                st.rerun()
            else:
                st.error("کلیلەکە هەڵەیە! تکایە دووبارە پشککنین بکەرەوە.")
    st.stop()

# --- 4. ژووری کارکردن دوای چوونەژوورەوە ---
st.title("📜 دروستکەری وەسڵی دیجیتاڵی")
st.sidebar.markdown(f"### 👤 باری بەژداری: \n **{st.session_state['plan']}**")

if st.sidebar.button("چوونە دەرەوە (Logout)"):
    st.session_state['auth'] = False
    st.rerun()

# فۆرمی وەرگرتنی زانیارییەکان
with st.expander("📝 پڕکردنەوەی زانیاری وەسڵ", expanded=True):
    shop = st.text_input("ناوی دوکان یان پەیج", "Golden Delivery")
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
        # دروستکردنی وێنەیەکی سپی
        img = Image.new('RGB', (500, 700), color='#ffffff')
        draw = ImageDraw.Draw(img)
        
        # دیزاینی چوارچێوەی پرۆفیشناڵ (شین و زێڕین)
        draw.rectangle([10, 10, 490, 690], outline="#d4af37", width=12) # زێڕین
        draw.rectangle([22, 22, 478, 678], outline="#003366", width=2)  # شین
        
        # نووسینی ناوەکان (تێبینی: بۆ نووسینی کوردی پێویستە فۆنتێک لە تەنیشت کۆدەکە بێت)
        draw.text((150, 40), "GOLDEN RECEIPT", fill="#003366")
        draw.text((50, 140), f"FROM: {shop.upper()}", fill="#000000")
        draw.text((50, 180), f"TO: {cust.upper()}", fill="#000000")
        draw.line((50, 230, 450, 230), fill="#d4af37", width=2)
        
        draw.text((50, 280), f"ITEM: {item}", fill="#000000")
        draw.text((50, 330), f"PRICE: {price:,} IQD", fill="#000000")
        draw.text((50, 380), f"DELIVERY: {delivery:,} IQD", fill="#000000")
        
        draw.line((50, 450, 450, 450), fill="#003366", width=3)
        total = price + delivery
        draw.text((50, 490), f"TOTAL AMOUNT: {total:,} IQD", fill="#cc0000")
        
        draw.text((120, 630), "Thank you for choosing us!", fill="#888888")

        # ئەگەر لۆگۆ هەبوو، بیخە سەر وێنەکە
        if logo:
            user_l = Image.open(logo).convert("RGBA").resize((100, 100))
            img.paste(user_l, (360, 40), user_l)

        # پیشاندانی وێنەکە لە سایتەکە
        st.image(img, caption="وەسڵەکەت ئامادەیە", use_container_width=True)
        
        # دوگمەی داگرتن (Download)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        st.download_button(label="💾 داگرتنی وەسڵ", data=buf.getvalue(), file_name=f"Receipt_{cust}.png", mime="image/png")
