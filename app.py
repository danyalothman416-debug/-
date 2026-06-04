import streamlit as st
import pandas as pd
import os

# ڕێکخستنی پەیج
st.set_page_config(
    page_title="دوکانی مۆبایل",
    page_icon="📱",
    layout="wide"
)

# CSSـی تایبەت بۆ جوانترکردن
st.markdown("""
<style>
    .product-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        background-color: #fafafa;
    }
    .product-title {
        font-size: 20px;
        font-weight: bold;
        color: #1e3c72;
    }
    .product-price {
        font-size: 18px;
        color: #ff6600;
        font-weight: bold;
    }
    .btn-buy {
        background-color: #ff6600;
        color: white;
        padding: 8px 20px;
        border-radius: 5px;
        text-decoration: none;
    }
    .sidebar-header {
        font-size: 24px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ناونیشان
st.title("📱 دوکانی مۆبایل")
st.markdown("---")

# زانیاری مۆبایلەکان
products = [
    {
        "ناو": "iPhone 15 Pro Max",
        "براند": "Apple",
        "نرخ": 1299,
        "ڕەنگ": "تیتانیۆمی شین",
        "RAM": "8GB",
        "شاشە": "6.7 ئینج",
        "کامێرا": "48MP",
        "باتری": "4422mAh",
        "وێنە": "https://via.placeholder.com/300x200.png?text=iPhone+15+Pro+Max",
        "وەسف": "بەهێزترین مۆبایلی ئەپڵ بە چیپی A17 Pro"
    },
    {
        "ناو": "Samsung Galaxy S24 Ultra",
        "براند": "Samsung",
        "نرخ": 1199,
        "ڕەنگ": "ڕەشی تایبەت",
        "RAM": "12GB",
        "شاشە": "6.8 ئینج",
        "کامێرا": "200MP",
        "باتری": "5000mAh",
        "وێنە": "https://via.placeholder.com/300x200.png?text=Galaxy+S24+Ultra",
        "وەسف": "مۆبایلێکی ئەندرۆیدی پلە یەک بە S Pen"
    },
    {
        "ناو": "Xiaomi 14 Pro",
        "براند": "Xiaomi",
        "نرخ": 799,
        "ڕەنگ": "سپی",
        "RAM": "12GB",
        "شاشە": "6.73 ئینج",
        "کامێرا": "50MP",
        "باتری": "4880mAh",
        "وێنە": "https://via.placeholder.com/300x200.png?text=Xiaomi+14+Pro",
        "وەسف": "بە کوالێتی و نرخێکی گونجاو"
    },
    {
        "ناو": "Google Pixel 8 Pro",
        "براند": "Google",
        "نرخ": 899,
        "ڕەنگ": "خۆڵەمێشی",
        "RAM": "12GB",
        "شاشە": "6.7 ئینج",
        "کامێرا": "50MP",
        "باتری": "5050mAh",
        "وێنە": "https://via.placeholder.com/300x200.png?text=Pixel+8+Pro",
        "وەسف": "باشترین کامێرا و سیستەمی خاوێنی ئەندرۆید"
    },
    {
        "ناو": "OnePlus 12",
        "براند": "OnePlus",
        "نرخ": 699,
        "ڕەنگ": "شینی ئاسمان",
        "RAM": "16GB",
        "شاشە": "6.82 ئینج",
        "کامێرا": "50MP",
        "باتری": "5400mAh",
        "وێنە": "https://via.placeholder.com/300x200.png?text=OnePlus+12",
        "وەسف": "باتری بەهێز و بارگاوی خێرا"
    },
    {
        "ناو": "Nothing Phone (2)",
        "براند": "Nothing",
        "نرخ": 599,
        "ڕەنگ": "ڕەش",
        "RAM": "12GB",
        "شاشە": "6.7 ئینج",
        "کامێرا": "50MP",
        "باتری": "4700mAh",
        "وێنە": "https://via.placeholder.com/300x200.png?text=Nothing+Phone+2",
        "وەسف": "دیزاینێکی یەکتا بە LED Glyph Interface"
    },
]

# Sidebar - فلتەر و گەڕان
st.sidebar.title("🔍 فلتەر و گەڕان")

# گەڕان
search = st.sidebar.text_input("بە دوای مۆبایلێکدا بگەڕێ...")

# فلتەری براند
brands = ["هەموو", "Apple", "Samsung", "Xiaomi", "Google", "OnePlus", "Nothing"]
selected_brand = st.sidebar.selectbox("براند", brands)

# فلتەری نرخ
st.sidebar.subheader("مەزانی نرخ")
min_price, max_price = st.sidebar.slider(
    "نرخ (دۆلار)",
    min_value=0, max_value=2000,
    value=(0, 2000),
    step=50
)

# فلتەرکردنی بەرهەمەکان
filtered_products = products

if search:
    filtered_products = [p for p in filtered_products if search.lower() in p["ناو"].lower() or search.lower() in p["براند"].lower()]

if selected_brand != "هەموو":
    filtered_products = [p for p in filtered_products if p["براند"] == selected_brand]

filtered_products = [p for p in filtered_products if min_price <= p["نرخ"] <= max_price]

# سەبەتە (cart)
if "cart" not in st.session_state:
    st.session_state.cart = []

# نیشاندانی بەرهەمەکان
st.header(f"📱 بەرهەمەکان ({len(filtered_products)})")

cols = st.columns(3)
for idx, product in enumerate(filtered_products):
    col = cols[idx % 3]
    with col:
        with st.container():
            st.markdown(f"""
            <div class="product-card">
                <div style="text-align: center;">
                    <img src="{product['وێنە']}" width="100%">
                </div>
                <div class="product-title">{product['ناو']}</div>
                <div class="product-price">${product['نرخ']}</div>
                <p>{product['وەسف']}</p>
                <p><b>براند:</b> {product['براند']} | <b>ڕەنگ:</b> {product['ڕەنگ']}</p>
                <p><b>RAM:</b> {product['RAM']} | <b>شاشە:</b> {product['شاشە']}</p>
                <p><b>کامێرا:</b> {product['کامێرا']} | <b>باتری:</b> {product['باتری']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"🛒 زیادکردن بۆ سەبەتە", key=f"btn_{idx}"):
                st.session_state.cart.append(product)
                st.success(f"✅ {product['ناو']} زیاد کرا بۆ سەبەتە!")

# سەبەتە (Cart Page)
st.markdown("---")
st.header("🛒 سەبەتەی من")

if len(st.session_state.cart) == 0:
    st.info("سەبەتەکەت بەتاڵە!")
else:
    total = 0
    for i, item in enumerate(st.session_state.cart):
        col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
        with col1:
            st.write(item["ناو"])
        with col2:
            st.write(item["براند"])
        with col3:
            st.write(f"${item['نرخ']}")
        with col4:
            if st.button(f"❌ لابردن", key=f"remove_{i}"):
                st.session_state.cart.pop(i)
                st.rerun()
        total += item["نرخ"]
    
    st.markdown("---")
    st.subheader(f"📊 کۆی گشتی: **${total}**")
    
    if st.button("✅ تەواوکردنی کڕین"):
        st.balloons()
        st.success("سوپاس بۆ کڕینتان! پەیوەندیمان پێوە دەکەین بۆ پشتڕاستکردنەوە.")
        st.session_state.cart = []

# پێداچوونەوە (Footer)
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray;">
    <p>© 2024 دوکانی مۆبایل - هەموو مافەکان پارێزراون</p>
    <p>📞 پەیوەندی: 0770-XXX-XXXX | ✉️ ئیمەیل: mobile@shop.krd</p>
</div>
""", unsafe_allow_html=True)
