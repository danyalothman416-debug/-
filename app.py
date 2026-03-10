import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

# 1. ڕێکخستنی سەرەتایی لاپەڕە
st.set_page_config(page_title="Golden Receipt", page_icon="📜", layout="centered")

# 2. لیستی کلیلە چالاکەکان (مانگانە و ساڵانە)
if 'valid_keys' not in st.session_state:
    st.session_state['valid_keys'] = {
        # مانگانە - 5,000 باڵانس
        "GOLD-MON-8821-X": "Monthly",
        "GOLD-MON-4432-Y": "Monthly",
        "GOLD-MON-1090-Z": "Monthly",
        
        # ساڵانە - 25,000 باڵانس (ئۆفەری تایبەت)
        "GOLD-25K-YEAR-001": "Yearly VIP",
        "GOLD-25K-YEAR-002": "Yearly VIP",
        "GOLD-25K-YEAR-003": "Yearly VIP",
        "DR-KIRKUK-2026": "Yearly VIP"
    }

# 3. سیستەمی چوونەژوورەوە (Authentication)
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    st.title("🔑 چالاککردنی وەسڵی گۆڵدن")
    st.image("https://img.icons8.com/fluent/100/000000/key.png")
    
    st.markdown("""
    ### 💳 چۆن کلیل (Key) بەدەست دەهێنیت؟
    ئێمە تەنها لە ڕێگەی **باڵانس (کارتی مۆبایل)** پارە وەردەگرین:
    
    * **📦 ئۆفەری مانگانە:** ٥,٠٠٠ باڵانس
    * **🌟 ئۆفەری ساڵانە:** ٢٥,٠٠٠ باڵانس (داشکاندنی تایبەت)
    
    **بۆ کڕینی کلیل:** کۆدی کارتەکە بنێرە بۆ واتسئەپی ئەم ژمارەیە:
    👉 **07801352003**
    """)

    key_input = st.text_input("کلیلەکەت لێرە بنووسە (Activation Key):", type="password")
    
    if st.button("تەئکیدکردنەوە و چوونەژوورەوە"):
        if key_input in st.session_state['valid_keys']:
            st.session_state['authenticated'] = True
            st.session_state['user_plan'] = st.session_state['valid_keys'][key_input]
            st.success(f"بە سەرکەوتوویی چالاک بوو! پلان: {st.session_state['user_plan']}")
            st.rerun()
        else:
            st.error("کلیلەکە هەڵەیە! تکایە پەیوەندی بە واتسئەپ بکە بۆ کڕینی کلیل.")
    st.stop()

# 4. ئەگەر بەکارهێنەر چووە ژوورەوە، ئەم بەشە کار دەکات
st.title("📜 دروستکەری وەسڵی دیجیتاڵی")
st.sidebar.write(f"✅ باری سیستەم: چالاک ({st.session_state['user_plan']})")

if st.sidebar.button("Log out"):
    st.session_state['authenticated'] = False
    st.rerun()

# فۆرمی وەرگرتنی زانیاری وەسڵ
with st.form("receipt_form"):
    col1, col2 = st.columns(2)
    with col1:
        shop_name = st.text_input("ناوی دوکان/پەیج", "Golden Shop")
        cust_name = st.text_input("ناوی کڕیار")
    with col2:
        item_name = st.text_input("جۆری کاڵا")
        price = st.number_input("نرخی کاڵا (دینار)", min_value=0, step=250)
    
    delivery_fee = st.number_input("کرێی گەیاندن (دینار)", min_value=0, step=250)
    
    # بارکردنی لۆگۆ (تەنها بۆ پلانی ساڵانە چالاکە بە کرداری، بەڵام لێرە بۆ هەمووان دام ناوە)
    logo_file = st.file_uploader("لۆگۆی دوکانەکەت (ئارەزوومەندانە)", type=['png', 'jpg', 'jpeg'])
    
    submit = st.form_submit_button("دروستکردنی وەسڵ")

if submit:
    if not cust_name or not item_name:
        st.warning("تکایە ناوی کڕیار و کاڵا بنووسە")
    else:
        # دروستکردنی وێنەی وەسڵەکە
        width, height = 500, 700
        receipt = Image.new('RGB', (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(receipt)
        
        # دیزاینی چوارچێوە
        draw.rectangle([20, 20, 480, 680], outline=(0, 51, 102), width=8)
        
        # نووسینەکان (بە ئینگلیزی چونکە پایتۆن فۆنتی کوردی جیاوازی دەوێت)
        draw.text((160, 50), "GOLDEN RECEIPT", fill=(0, 51, 102))
        draw.text((50, 150), f"SHOP: {shop_name.upper()}", fill=(0, 0, 0))
        draw.text((50, 200), f"CUSTOMER: {cust_name}", fill=(0, 0, 0))
        draw.line((50, 250, 450, 250), fill=(200, 200, 200), width=2)
        
        draw.text((50, 300), f"ITEM: {item_name}", fill=(0, 0, 0))
        draw.text((50, 350), f"PRICE: {price:,} IQD", fill=(0, 0, 0))
        draw.text((50, 400), f"DELIVERY: {delivery_fee:,} IQD", fill=(0, 0, 0))
        
        draw.line((50, 480, 450, 480), fill=(0, 51, 102), width=3)
        total = price + delivery_fee
        draw.text((50, 520), f"TOTAL AMOUNT: {total:,} IQD", fill=(204, 0, 0))
        
        draw.text((120, 620), "Thank you for choosing us!", fill=(100, 100, 100))

        # ئەگەر لۆگۆی هەبوو، بیخە سەر وەسڵەکە
        if logo_file:
            user_logo = Image.open(logo_file).convert("RGBA")
            user_logo = user_logo.resize((100, 100))
            receipt.paste(user_logo, (350, 50), user_logo)

        # پیشاندانی وێنەکە
        st.image(receipt, caption="وەسڵەکەت ئامادەیە", use_container_width=True)
        
        # دوگمەی داگرتن
        buf = io.BytesIO()
        receipt.save(buf, format="PNG")
        st.download_button(
            label="💾 داگرتنی وەسڵ (Download)",
            data=buf.getvalue(),
            file_name=f"Receipt_{cust_name}.png",
            mime="image/png"
        )
