# shop_simple.py
# کاشێری سادە بۆ دووکانی مۆبایل - تەنها ١٠٠ هێڵ

import streamlit as st
import json
import os
from datetime import datetime

# -------------------- کۆنفیگ --------------------
st.set_page_config(page_title="دووکان - کاشێر", layout="wide")
st.title("📱 دووکانی مۆبایل - کاشێر")

# -------------------- داتا --------------------
DATA_FILE = "shop_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"products": [], "sales": [], "counter": 0}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

data = load_data()

# -------------------- سەبەتە --------------------
if "cart" not in st.session_state:
    st.session_state.cart = []

# ==================== ١. زیادکردنی کاڵا ====================
st.markdown("### ➕ زیادکردنی کاڵا")

col1, col2, col3 = st.columns(3)
with col1:
    name = st.text_input("ناوی کاڵا", placeholder="بۆ نموونە: iPhone 15")
with col2:
    price = st.number_input("نرخ (دینار)", min_value=100, value=10000, step=1000)
with col3:
    stock = st.number_input("کۆتا", min_value=0, value=5, step=1)

if st.button("➕ زیادکردن", use_container_width=True, type="primary"):
    if name and price > 0:
        data["products"].append({
            "id": len(data["products"]) + 1,
            "name": name,
            "price": price,
            "stock": stock
        })
        save_data(data)
        st.success(f"✅ {name} زیاد کرا")
        st.rerun()

# ==================== ٢. لیستی کاڵاکان و فرۆشتن ====================
st.markdown("---")
st.markdown("### 🛒 فرۆشتن")

if data["products"]:
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.markdown("#### کاڵاکان")
        
        # نمایشی کاڵاکان بە شێوەی کارت
        for product in data["products"]:
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            with col1:
                st.write(f"**{product['name']}**")
                st.caption(f"کۆتا: {product['stock']}")
            with col2:
                st.write(f"💰 {product['price']:,} دینار")
            with col3:
                qty = st.number_input("ژ", min_value=1, value=1, key=f"qty_{product['id']}", label_visibility="collapsed")
            with col4:
                if st.button("➕ زیاد", key=f"add_{product['id']}", use_container_width=True):
                    st.session_state.cart.append({
                        "name": product["name"],
                        "price": product["price"],
                        "qty": qty,
                        "total": product["price"] * qty
                    })
                    st.success(f"✅ {qty} x {product['name']} زیاد کرا")
                    st.rerun()
    
    with col_right:
        st.markdown("#### 🛒 سەبەتە")
        
        if st.session_state.cart:
            total = sum(item["total"] for item in st.session_state.cart)
            
            for item in st.session_state.cart:
                st.write(f"{item['name']} × {item['qty']} = {item['total']:,} دینار")
            
            st.markdown(f"**کۆی گشتی: {total:,} دینار**")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ تەواوکردن", use_container_width=True, type="primary"):
                    # کەمکردنەوەی کۆتا
                    for cart_item in st.session_state.cart:
                        for product in data["products"]:
                            if product["name"] == cart_item["name"]:
                                product["stock"] -= cart_item["qty"]
                    
                    data["sales"].append({
                        "id": data["counter"] + 1,
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "items": st.session_state.cart.copy(),
                        "total": total
                    })
                    data["counter"] += 1
                    save_data(data)
                    st.session_state.cart = []
                    st.success("🎉 فرۆشتن تەواو بوو!")
                    st.balloons()
                    st.rerun()
            
            with col2:
                if st.button("🗑️ پاککردنەوە", use_container_width=True):
                    st.session_state.cart = []
                    st.rerun()
        else:
            st.info("سەبەتە بەتاڵە")

# ==================== ٣. داهات ====================
st.markdown("---")
st.markdown("### 📊 داهات")

if data["sales"]:
    total_revenue = sum(s["total"] for s in data["sales"])
    total_sales = len(data["sales"])
    
    col1, col2, col3 = st.columns(3)
    col1.metric("💰 کۆی داهات", f"{total_revenue:,} دینار")
    col2.metric("🧾 ژمارەی فرۆشتن", total_sales)
    col3.metric("📅 دوایین فرۆشتن", data["sales"][-1]["date"][:10])
    
    if st.button("📥 دابەزاندنی ڕاپۆرت", use_container_width=True):
        st.info("پشتیوانی دابەزاندن لە وەشانی داهاتوو")
else:
    st.info("هیچ فرۆشتنێک تۆمار نەکراوە")

# ==================== ٤. ڕێنمایی ====================
with st.expander("📖 ڕێنمایی بۆ بەکارهێنان"):
    st.markdown("""
    1. **زیادکردنی کاڵا:** ناو و نرخ و کۆتا بنووسە، دوگمەی "زیادکردن" کلیک بکە.
    2. **فرۆشتن:** کاڵاکان لە لیستەکە هەڵبژێرە، ژماردەکە دیاری بکە، کلیک لە "زیاد" بکە.
    3. **تەواوکردنی فرۆشتن:** دوای زیادکردنی هەموو کاڵاکان، کلیک لە "تەواوکردن" بکە.
    4. **داهات:** هەموو فرۆشتنەکان خۆکار تۆمار دەکرێن و داهات پیشان دەدرێت.
    """)
