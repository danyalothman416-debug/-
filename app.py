import streamlit as st
from PIL import Image, ImageDraw
import io
from datetime import date

# --- ١. ڕێکخستنی سەرەتایی و دیزاین ---
st.set_page_config(page_title="Golden Receipt VIP", page_icon="📜", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #f4f7f6; }
    .stButton>button { width: 100%; border-radius: 12px; background-color: #003366; color: white; font-weight: bold; }
    .test-box { border: 2px dashed #d4af37; padding: 20px; border-radius: 10px; background-color: #fff3cd; text-align: center; }
    .expiry-info { background: #003366; color: #d4af37; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- ٢. داتابەیسی کلیلەکان و پاشەکەوتی مۆبایل ---
# تێبینی: device_id بۆ قوفڵکردنی کۆدەکە بەکاردێت لەسەر یەک مۆبایل
if 'valid_keys' not in st.session_state:
    st.session_state['valid_keys'] = {
        "GOLD-MON-8821-X": {"plan": "مانگانە", "expiry": date(2026, 4, 10), "device": None},
        "DR-KIRKUK-2026": {"plan": "ساڵانە", "expiry": date(2027, 3, 10), "device": None},
        "GOLD-25K-001": {"plan": "ساڵانە", "expiry": date(2027, 3, 10), "device": None}
    }

# بەکارهێنانی Cookies یان Session بۆ ئەوەی پێویست نەکات هەموو جارێک بچێتە ژوورەوە
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# --- ٣. ڕووکاری سەرەتا (بەخێرهاتن و تێست) ---
if not st.session_state['authenticated']:
    st.title("📜 سیستەمی وەسڵی گۆڵدن")
    
    tab1, tab2 = st.tabs(["✨ تاقیکردنەوەی بێبەرامبەر", "🔐 چالاککردنی ئەژمار"])
    
    with tab1:
        st.info("لێرەدا دەتوانیت دیزاینی وەسڵەکە تاقی بکەیتەوە")
        t_shop = st.text_input("ناوی دوکان (تێست)", "دوکانی نموونە")
        t_cust = st.text_input("ناوی کڕیار (تێست)", "کڕیاری ژمارە ١")
        if st.button("پیشاندانی وەسڵی تێست"):
            st.markdown('<div class="test-box">⚠️ ئەمە تەنها بۆ بینینە، بۆ داگرتن دەبێت ئەژمارەکەت چالاک بکەیت</div>', unsafe_allow_html=True)
            # وێنەیەکی سادە بۆ تێست
            t_img = Image.new('RGB', (500, 300), color='#ffffff')
            d = ImageDraw.Draw(t_img)
            d.rectangle([5, 5, 495, 295], outline="#d4af37", width=5)
            d.text((150, 100), f"SHOP: {t_shop}", fill="#000")
            d.text((150, 150), f"CUSTOMER: {t_cust}", fill="#000")
            st.image(t_img)

    with tab2:
        st.write("کۆدی چالاککردن داخڵ بکە بۆ چوونەژوورە هەمیشەیی")
        user_key = st.text_input("Activation Key", type="password").strip().upper()
        
        if st.button("چوونەژوورەوە"):
            if user_key in st.session_state['valid_keys']:
                k_data = st.session_state['valid_keys'][user_key]
                
                # وەرگرتنی ناسنامەی مۆبایل (User-Agent)
                current_device = st.context.headers.get("User-Agent")
                
                # پشکنینی قوفڵی مۆبایل
                if k_data["device"] is None or k_data["device"] == current_device:
                    if date.today() <= k_data["expiry"]:
                        st.session_state['valid_keys'][user_key]["device"] = current_device
                        st.session_state['authenticated'] = True
                        st.session_state['user_info'] = k_data
                        st.rerun()
                    else:
                        st.error("ماوەی کۆدەکەت بەسەرچووە")
                else:
                    st.error("❌ ئەم کۆدە لە مۆبایلێکی تر چالاک کراوە و ناتوانیت لێرە بەکاری بهێنیت!")
            else:
                st.error("کۆدەکە هەڵەیە")
    st.stop()

# --- ٤. ژووری کارکردنی سەرەکی (تەنها بۆ ئەوانەی چووینەتە ژوورەوە) ---
today = date.today()
days_left = (st.session_state['user_info']['expiry'] - today).days

st.title("📜 دروستکەری وەسڵی دیجیتاڵی")
st.markdown(f"<div class='expiry-info'>⏳ بەخێربێیتەوە! تەنها {days_left} ڕۆژت ماوە بۆ بەسەرچوونی بەژدارییەکەت</div>", unsafe_allow_html=True)

if st.sidebar.button("چوونە دەرەوە (Logout)"):
    st.session_state['authenticated'] = False
    st.rerun()

# فۆرمی وەسڵی ڕاستەقینە
with st.expander("📝 پڕکردنەوەی زانیاری وەسڵ", expanded=True):
    shop = st.text_input("ناوی دوکان/پەیج", "گۆڵدن دێلیڤەری")
    cust = st.text_input("ناوی کڕیار")
    item = st.text_input("جۆری کاڵا")
    price = st.number_input("نرخ (دینار)", min_value=0, step=250)
    delivery = st.number_input("گەیاندن (دینار)", min_value=0, step=250)
    logo = st.file_uploader("لۆگۆ پاشکۆ بکە", type=['png', 'jpg', 'jpeg'])

if st.button("✨ دروستکردنی وەسڵی کۆتایی"):
    if not cust or not item:
        st.warning("تکایە خانەکان پڕ بکەرەوە")
    else:
        # دروستکردنی وێنەی وەسڵ
        img = Image.new('RGB', (500, 700), color='#ffffff')
        draw = ImageDraw.Draw(img)
        draw.rectangle([10, 10, 490, 690], outline="#d4af37", width=15)
        draw.text((150, 50), "GOLDEN RECEIPT", fill="#003366")
        
        # لێرە زانیارییەکان دەنووسرێن (بە ئینگلیزی بۆ وێنەکە، یان بە بەکارهێنانی فۆنت بۆ کوردی)
        draw.text((60, 150), f"SHOP: {shop}", fill="#000")
        draw.text((60, 210), f"CUSTOMER: {cust}", fill="#000")
        draw.text((60, 310), f"ITEM: {item}", fill="#000")
        draw.text((60, 370), f"TOTAL: {price + delivery:,} IQD", fill="#cc0000")
        
        if logo:
            l_img = Image.open(logo).convert("RGBA").resize((100, 100))
            img.paste(l_img, (360, 40), l_img)
            
        st.image(img)
        
        # دوگمەی داگرتن
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        st.download_button("💾 داگرتنی وەسڵ", buf.getvalue(), f"receipt_{cust}.png", "image/png")
