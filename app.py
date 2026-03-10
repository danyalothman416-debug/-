import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

# ڕێکخستنی لاپەڕەکە
st.set_page_config(page_title="Golden Receipt", page_icon="📜")

st.title("📜 دروستکەری وەسڵی گۆڵدن")
st.write("وەسڵێکی پرۆفیشناڵ دروست بکە و بۆ کڕیارەکەی بنێرە")

# وەرگرتنی زانیارییەکان لە فرۆشیار
with st.form("receipt_form"):
    shop_name = st.text_input("ناوی دوکانەکەت", "Golden Shop")
    customer_name = st.text_input("ناوی کڕیار")
    item_name = st.text_input("ناوی کاڵا")
    price = st.number_input("نرخ (دینار)", min_value=0, step=250)
    delivery_fee = st.number_input("کرێی گەیاندن", min_value=0, step=250)
    
    submit = st.form_submit_button("دروستکردنی وەسڵ")

if submit:
    if not customer_name or not item_name:
        st.error("تکایە هەموو زانیارییەکان پڕ بکەرەوە!")
    else:
        # دروستکردنی وێنەی وەسڵەکە
        width, height = 400, 500
        img = Image.new('RGB', (width, height), color=(255, 255, 255))
        d = ImageDraw.Draw(img)
        
        # ڕەنگ و چوارچێوە
        d.rectangle([10, 10, 390, 490], outline=(0, 51, 102), width=5)
        
        # نووسینی ناوەکان (لێرەدا وەک نموونە بە ئینگلیزی، چونکە پایتۆن فۆنتی کوردی تایبەتی دەوێت)
        try:
            # تێبینی: بۆ کوردی پێویستە فۆنتێکی وەک 'arial.ttf' لە تەنیشت کۆدەکە بێت
            d.text((120, 30), "GOLDEN RECEIPT", fill=(0, 51, 102))
            d.text((30, 80), f"Shop: {shop_name}", fill=(0, 0, 0))
            d.text((30, 120), f"Customer: {customer_name}", fill=(0, 0, 0))
            d.text((30, 180), "-"*40, fill=(200, 200, 200))
            d.text((30, 220), f"Item: {item_name}", fill=(0, 0, 0))
            d.text((30, 260), f"Price: {price:,} IQD", fill=(0, 0, 0))
            d.text((30, 300), f"Delivery: {delivery_fee:,} IQD", fill=(0, 0, 0))
            d.text((30, 340), "-"*40, fill=(200, 200, 200))
            total = price + delivery_fee
            d.text((30, 380), f"TOTAL: {total:,} IQD", fill=(204, 0, 0))
            d.text((80, 440), "Thank you for your trust!", fill=(0, 102, 51))
        except:
            st.warning("کێشەیەک لە نووسیندا هەبوو، بەڵام وەسڵەکە دروست بوو.")

        # پیشاندانی وێنەکە لە سایتەکە
        st.image(img, caption="وەسڵی ئامادەکراو", use_column_width=True)
        
        # دوگمەی داگرتن (Download)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        byte_im = buf.getvalue()
        
        st.download_button(
            label="داگرتنی وەسڵ (Download)",
            data=byte_im,
            file_name=f"Receipt_{customer_name}.png",
            mime="image/png",
        )
        st.success("وەسڵەکە ئامادەیە! دەتوانیت دایبەزێنیت و بە واتسئەپ بینێریت.")
