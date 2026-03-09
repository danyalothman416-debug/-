import streamlit as st
import pandas as pd
import os
import urllib.parse
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# --- 1. ڕێکخستنی لاپەڕە و ستایل ---
st.set_page_config(page_title="Golden Delivery", layout="wide")

st.markdown("""
    <style>
    section[data-testid="stSidebar"] { display: none !important; }
    html, body, [data-testid="stAppViewContainer"] { direction: rtl; text-align: right; }
    .brand-header {
        background: linear-gradient(135deg, #1a1a1a 0%, #333333 100%);
        padding: 25px; border-radius: 15px; border-bottom: 4px solid #D4AF37;
        text-align: center; margin-bottom: 20px;
    }
    .brand-title { color: #D4AF37; font-size: 32px; font-weight: bold; }
    .install-bar {
        position: fixed; bottom: 0; left: 0; width: 100%;
        background-color: #1a1a1a; color: white; padding: 12px;
        text-align: center; border-top: 3px solid #D4AF37; z-index: 9999;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ٢. دروستکردنی وێنەی وەسڵ (The Magic Part) ---
def create_receipt_image(data):
    # دروستکردنی وێنەیەکی ڕەش
    img = Image.new('RGB', (600, 800), color=(26, 26, 26))
    draw = ImageDraw.Draw(img)
    
    # کێشانی چوارگۆشەیەکی زێڕین لە دەوری
    draw.rectangle([10, 10, 590, 790], outline=(212, 175, 55), width=5)
    
    # نوسینی ناوی براند (لێرەدا دەتوانیت فۆنت دابنێیت، بەڵام بۆ سادەیی فۆنتی سستەم بەکاردێنین)
    draw.text((300, 80), "GOLDEN DELIVERY", fill=(212, 175, 55), anchor="mm")
    draw.text((300, 130), "وەسڵی گەیاندنی دیجیتاڵی", fill=(255, 255, 255), anchor="mm")
    
    # زانیارییەکان
    y_pos = 250
    items = [
        f"کات: {data['کات']}",
        f"کڕیار: {data['کڕیار']}",
        f"دوکان: {data['ناوی دوکان']}",
        f"ناونیشان: {data['ناونیشانی کڕیار']}",
        f"نرخ: {data['نرخ']:,} IQD",
        f"مۆبایل: {data['مۆبایل']}"
    ]
    
    for item in items:
        draw.text((50, y_pos), item, fill=(255, 255, 255))
        y_pos += 60
        
    draw.text((300, 700), "سوپاس بۆ متمانەتان", fill=(212, 175, 55), anchor="mm")
    
    img_path = "receipt.png"
    img.save(img_path)
    return img_path

# --- ٣. بەڕێوەبردنی داتا ---
ADMIN_PASSWORD = "dr_danyal_2024" 
DB_FILE = "global_deliveries.csv"
MY_WHATSAPP = "9647721959922"

def load_data():
    if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE, dtype={"مۆبایل": str})
    return pd.DataFrame(columns=["کات", "کڕیار", "ناوی دوکان", "ناونیشانی دوکان", "مۆبایل", "نرخ", "ناونیشانی کڕیار"])

def save_data(df): df.to_csv(DB_FILE, index=False)

# --- ٤. ڕووکاری کڕیار ---
st.markdown("""
    <div class="brand-header">
        <div class="brand-title">GOLDEN DELIVERY ✨</div>
        <div style="color:white;">خێراترین گەیاندن لە کەرکوک / أسرع خدمة توصيل في كركوك</div>
    </div>
""", unsafe_allow_html=True)

with st.form("delivery_form", clear_on_submit=False):
    col1, col2 = st.columns(2)
    with col1:
        customer = st.text_input("👤 ناوی کڕیار")
        shop_name = st.text_input("🏪 ناوی دوکان")
        shop_address = st.text_input("📍 ناونیشانی دوکان")
    with col2:
        phone = st.text_input("📞 ژمارەی مۆبایل")
        customer_address = st.text_input("🏘 ناونیشانی کڕیار")
        price = st.number_input("💰 نرخ", min_value=0, step=250)
    
    submit = st.form_submit_button("تۆمارکردن و دروستکردنی وەسڵ ✅")
    
    if submit:
        if not customer or not shop_name or not phone:
            st.error("⚠️ تکایە خانەکان پڕ بکەرەوە")
        else:
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            data = {"کات": now, "کڕیار": customer, "ناوی دوکان": shop_name, "ناونیشانی دوکان": shop_address, "مۆبایل": str(phone), "نرخ": price, "ناونیشانی کڕیار": customer_address}
            
            # پاشەکەوتکردن لە داتابەیس
            df = load_data()
            save_data(pd.concat([df, pd.DataFrame([data])], ignore_index=True))
            
            # دروستکردنی وێنە
            img_file = create_receipt_image(data)
            
            st.success("✅ وەسڵەکە بە سەرکەوتوویی تۆمارکرا!")
            
            # پیشاندانی وێنەکە و دوگمەی داگرتن
            st.image(img_file, caption="وەسڵی دیجیتاڵی تۆ", width=300)
            
            with open(img_file, "rb") as file:
                st.download_button(label="📥 دابەزاندنی وێنەی وەسڵ", data=file, file_name=f"Receipt_{customer}.png", mime="image/png")

            # ناردن بۆ واتسئەپ
            msg = f"Golden Delivery ✨\n📦 وەسڵێکی نوێ\n👤 کڕیار: {customer}\n💰 نرخ: {price:,} IQD"
            link = f"https://wa.me/{MY_WHATSAPP}?text={urllib.parse.quote(msg)}"
            st.markdown(f'<a href="{link}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:12px; border-radius:10px; font-weight:bold; cursor:pointer;">ناردنی نامە بۆ واتسئەپ 💬</button></a>', unsafe_allow_html=True)

st.markdown(f'<div style="text-align:center; padding:20px; margin-bottom:50px;">📞 0772 195 9922 | 0780 135 2003</div>', unsafe_allow_html=True)

# بەشی ئەدمین و بارەکەی خوارەوە وەک خۆیانن...
st.markdown("""<div class="install-bar">بۆ دابەزاندنی ئەپ: کلیک لە ⎙ یان ⋮ بکە و <b>Add to Home Screen</b> هەڵبژێرە</div>""", unsafe_allow_html=True)
