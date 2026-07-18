# mobile_shop_app.py
# ئەپلیکەیشنی کاشێر بۆ دووکانی مۆبایل

import streamlit as st
import json
import os
from datetime import datetime

# -------------------- کۆنفیگ --------------------
st.set_page_config(
    page_title="دووکانی مۆبایل - کاشێر",
    page_icon="📱",
    layout="wide"
)

st.markdown("""
    <style>
        .main { background: #f0f2f6; }
        .product-box {
            background: white;
            padding: 15px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            margin-bottom: 10px;
            border: 1px solid #e0e0e0;
        }
        .cart-box {
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            position: sticky;
            top: 20px;
        }
        .total-box {
            background: #1a1a2e;
            color: white;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            margin-top: 15px;
        }
        .product-icon {
            font-size: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

# -------------------- داتا --------------------
DATA_FILE = "mobile_shop_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "products": [
            {"id": 1, "name": "مۆبایل ئاسیا", "price": 350000, "stock": 10, "icon": "📱"},
            {"id": 2, "name": "مۆبایل زێن", "price": 450000, "stock": 8, "icon": "📱"},
            {"id": 3, "name": "مۆبایل بلو", "price": 280000, "stock": 12, "icon": "📱"},
            {"id": 4, "name": "یوسی پۆبجی (UC)", "price": 25000, "stock": 50, "icon": "🎮"},
            {"id": 5, "name": "سپۆنسەری تیکتۆک", "price": 150000, "stock": 20, "icon": "🎵"},
            {"id": 6, "name": "سپۆنسەری یوتیوب", "price": 200000, "stock": 15, "icon": "🎥"},
            {"id": 7, "name": "کارتی کۆرەک", "price": 50000, "stock": 30, "icon": "💳"},
            {"id": 8, "name": "ژمارەی ناوازە (ئاسیا)", "price": 75000, "stock": 5, "icon": "🌟"},
            {"id": 9, "name": "ژمارەی ناوازە (زێن)", "price": 100000, "stock": 3, "icon": "🌟"}
        ],
        "sales": [],
        "counter": 0
    }

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

data = load_data()

# -------------------- سەبەتە --------------------
if "cart" not in st.session_state:
    st.session_state.cart = []

# -------------------- هێدر --------------------
st.title("📱 دووکانی مۆبایل - کاشێر")
st.caption(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# ==================== بەشی سەرەکی ====================
col_products, col_cart = st.columns([2, 1])

with col_products:
    st.markdown("### 🛍️ کاڵاکان")
    
    # گەڕان
    search = st.text_input("🔍 گەڕان", placeholder="ناوی کاڵا بنووسە...")
    
    # پاڵاوتنی کاڵاکان
    products = data["products"]
    if search:
        products = [p for p in products if search.lower() in p["name"].lower()]
    
    # نمایشی کاڵاکان
    for product in products:
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([2, 1.5, 1, 1, 1.2])
            
            with col1:
                st.markdown(f"""
                    <div class="product-box">
                        <span class="product-icon">{product['icon']}</span>
                        <b>{product['name']}</b>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.write(f"💰 {product['price']:,} دینار")
            
            with col3:
                st.write(f"📦 کۆتا: {product['stock']}")
            
            with col4:
                qty = st.number_input(
                    "ژ",
                    min_value=1,
                    max_value=product['stock'] if product['stock'] > 0 else 1,
                    value=1,
                    key=f"qty_{product['id']}",
                    label_visibility="collapsed"
                )
            
            with col5:
                if st.button(
                    "➕ زیاد",
                    key=f"add_{product['id']}",
                    use_container_width=True,
                    disabled=product['stock'] <= 0,
                    type="primary" if product['stock'] > 0 else "secondary"
                ):
                    st.session_state.cart.append({
                        "product_id": product['id'],
                        "name": product['name'],
                        "price": product['price'],
                        "qty": qty,
                        "total": product['price'] * qty,
                        "icon": product['icon']
                    })
                    st.success(f"✅ {qty} x {product['name']} زیاد کرا")
                    st.rerun()
            
            st.divider()

with col_cart:
    st.markdown("### 🛒 سەبەتە")
    
    with st.container():
        if st.session_state.cart:
            total = sum(item["total"] for item in st.session_state.cart)
            total_items = sum(item["qty"] for item in st.session_state.cart)
            
            # نمایشی کاڵاکانی سەبەتە
            for idx, item in enumerate(st.session_state.cart):
                st.markdown(f"""
                    <div style="display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #eee;">
                        <div>
                            <span>{item['icon']}</span>
                            <span>{item['name']}</span>
                            <span style="color:#666; font-size:0.8rem;">×{item['qty']}</span>
                        </div>
                        <div>
                            <span style="font-weight:bold;">{item['total']:,} دینار</span>
                            <button onclick="alert('سڕدرایەوە')" style="background:none; border:none; color:red; cursor:pointer;">✕</button>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"🗑️", key=f"remove_{idx}", help="سڕینەوە"):
                    st.session_state.cart.pop(idx)
                    st.rerun()
            
            # کۆی گشتی
            st.markdown(f"""
                <div class="total-box">
                    <div style="font-size:1.2rem; font-weight:bold;">
                        کۆی گشتی: {total:,} دینار
                    </div>
                    <div style="font-size:0.9rem; opacity:0.8;">
                        {total_items} کاڵا
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # دوگمەکان
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ تەواوکردن", use_container_width=True, type="primary"):
                    # کەمکردنەوەی کۆتا
                    for cart_item in st.session_state.cart:
                        for product in data["products"]:
                            if product["id"] == cart_item["product_id"]:
                                product["stock"] -= cart_item["qty"]
                    
                    # تۆمارکردنی فرۆشتن
                    data["sales"].append({
                        "id": data["counter"] + 1,
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "items": st.session_state.cart.copy(),
                        "total": total,
                        "items_count": total_items
                    })
                    data["counter"] += 1
                    save_data(data)
                    
                    # پاککردنەوەی سەبەتە
                    st.session_state.cart = []
                    st.success("🎉 فرۆشتن تەواو بوو!")
                    st.balloons()
                    st.rerun()
            
            with col2:
                if st.button("🗑️ پاککردنەوە", use_container_width=True):
                    st.session_state.cart = []
                    st.rerun()
        
        else:
            st.info("🛍️ سەبەتە بەتاڵە")
            st.markdown("""
                <div style="text-align:center; padding:30px 0; color:#999;">
                    <p style="font-size:3rem;">🛒</p>
                    <p>تکایە کاڵاکانت هەڵبژێرە</p>
                </div>
            """, unsafe_allow_html=True)

# ==================== تابەکانی تر ====================
tab1, tab2, tab3 = st.tabs(["📊 داهات", "📦 بەڕێوەبردنی کاڵا", "⚙️ کۆنفیگ"])

with tab1:
    st.markdown("### 📊 داهات")
    
    if data["sales"]:
        total_revenue = sum(s["total"] for s in data["sales"])
        total_sales = len(data["sales"])
        
        col1, col2, col3 = st.columns(3)
        col1.metric("💰 کۆی داهات", f"{total_revenue:,} دینار")
        col2.metric("🧾 ژمارەی فرۆشتن", total_sales)
        
        # دوایین ١٠ فرۆشتن
        st.markdown("#### 📋 دوایین فرۆشتنەکان")
        for sale in data["sales"][-10:][::-1]:
            st.markdown(f"""
                <div style="background:white; padding:10px; border-radius:8px; margin:5px 0; border-right:4px solid #1a1a2e;">
                    <div style="display:flex; justify-content:space-between;">
                        <div>
                            <b>#{sale['id']}</b>
                            <span style="font-size:0.8rem; color:#666;">{sale['date'][:16]}</span>
                        </div>
                        <div style="font-weight:bold; color:#1a1a2e;">
                            {sale['total']:,} دینار
                        </div>
                    </div>
                    <div style="font-size:0.8rem; color:#888;">
                        {sale['items_count']} کاڵا
                    </div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("هیچ فرۆشتنێک تۆمار نەکراوە")

with tab2:
    st.markdown("### 📦 بەڕێوەبردنی کاڵا")
    
    with st.expander("➕ زیادکردنی کاڵای نوێ", expanded=False):
        with st.form("add_product"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("🏷️ ناوی کاڵا")
                price = st.number_input("💰 نرخ", min_value=100, value=10000, step=1000)
            with col2:
                stock = st.number_input("📦 کۆتا", min_value=0, value=10, step=1)
                icon = st.selectbox("🎨 ئایکۆن", ["📱", "🎮", "🎵", "🎥", "💳", "🌟", "📲", "🕹️", "🎯"])
            
            if st.form_submit_button("➕ زیادکردن", use_container_width=True, type="primary"):
                if name and price > 0:
                    data["products"].append({
                        "id": len(data["products"]) + 1,
                        "name": name,
                        "price": price,
                        "stock": stock,
                        "icon": icon
                    })
                    save_data(data)
                    st.success(f"✅ {name} زیاد کرا")
                    st.rerun()
    
    st.markdown("#### 📋 لیستی کاڵاکان")
    
    for product in data["products"]:
        col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
        with col1:
            st.write(f"{product['icon']} **{product['name']}**")
        with col2:
            st.write(f"💰 {product['price']:,} دینار")
        with col3:
            st.write(f"📦 {product['stock']}")
        with col4:
            if st.button("🗑️", key=f"del_{product['id']}"):
                data["products"].remove(product)
                save_data(data)
                st.rerun()
        st.divider()

with tab3:
    st.markdown("### ⚙️ کۆنفیگ")
    
    if st.button("🗑️ سڕینەوەی هەموو داتاکان", use_container_width=True):
        if st.checkbox("دڵنیای لە سڕینەوە؟"):
            data = {"products": data["products"], "sales": [], "counter": 0}
            save_data(data)
            st.session_state.cart = []
            st.success("✅ هەموو داتاکان سڕدرانەوە")
            st.rerun()
    
    st.caption(f"📁 پەڕگەی داتا: {DATA_FILE}")
    st.caption(f"📊 ژمارەی کاڵا: {len(data['products'])}")
    st.caption(f"🧾 ژمارەی فرۆشتن: {len(data['sales'])}")

# ==================== فووتەر ====================
st.markdown("---")
st.markdown("""
    <div style="text-align:center; color:#999; font-size:0.8rem;">
        📱 دووکانی مۆبایل - کاشێر | دروست کراوە بە ❤️
    </div>
""", unsafe_allow_html=True)
