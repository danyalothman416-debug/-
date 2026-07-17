# supermarket_cashier.py
import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
import hashlib

# -------------------- کۆنفیگ --------------------
st.set_page_config(
    page_title="سوپەرمارکێت کاشێر پڕۆ",
    page_icon="🏪",
    layout="wide"
)

# -------------------- داتابەیس --------------------
DATA_FILE = "supermarket_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "products": [],
        "categories": [],
        "sales": [],
        "users": [],
        "inventory": [],
        "counter": 0,
        "settings": {
            "shop_name": "سوپەرمارکێت",
            "tax_rate": 0.15,
            "currency": "IQD",
            "receipt_footer": "سوپاس بۆ کڕین"
        }
    }

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# -------------------- دیزاینی پیشەیی --------------------
st.markdown("""
    <style>
        /* Professional Supermarket Style */
        .main {
            background: #f5f5f5;
        }
        
        /* Header like Carrefour */
        .super-header {
            background: linear-gradient(135deg, #003366, #004d99);
            color: white;
            padding: 20px 30px;
            border-radius: 12px;
            margin-bottom: 25px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }
        
        .super-header h1 {
            margin: 0;
            font-size: 2rem;
            font-weight: 700;
        }
        
        .super-header .shop-info {
            text-align: right;
            font-size: 0.9rem;
            opacity: 0.9;
        }
        
        /* Product Categories */
        .category-tabs {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin: 15px 0;
            padding: 10px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        }
        
        .category-btn {
            padding: 8px 20px;
            border-radius: 20px;
            border: 2px solid #e0e0e0;
            background: white;
            cursor: pointer;
            transition: 0.3s;
            font-weight: 500;
        }
        
        .category-btn:hover, .category-btn.active {
            background: #003366;
            color: white;
            border-color: #003366;
        }
        
        /* Product Card like supermarket */
        .product-card-super {
            background: white;
            border-radius: 12px;
            padding: 15px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            transition: 0.3s;
            border: 2px solid transparent;
            position: relative;
            text-align: center;
        }
        
        .product-card-super:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.12);
            border-color: #003366;
        }
        
        .product-card-super .product-icon {
            font-size: 3rem;
            margin-bottom: 10px;
        }
        
        .product-card-super .product-name {
            font-weight: 600;
            font-size: 1rem;
            color: #333;
            margin: 5px 0;
        }
        
        .product-card-super .product-price {
            color: #003366;
            font-weight: 700;
            font-size: 1.2rem;
            margin: 5px 0;
        }
        
        .product-card-super .product-barcode {
            font-size: 0.7rem;
            color: #999;
            background: #f5f5f5;
            padding: 2px 8px;
            border-radius: 4px;
            display: inline-block;
        }
        
        .product-card-super .stock-badge {
            position: absolute;
            top: 10px;
            right: 10px;
            background: #ff6b6b;
            color: white;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 0.7rem;
        }
        
        .product-card-super .stock-badge.in-stock {
            background: #51cf66;
        }
        
        /* Cart - like supermarket receipt */
        .cart-super {
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
            max-height: 600px;
            overflow-y: auto;
        }
        
        .cart-item-super {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid #f0f0f0;
        }
        
        .cart-item-super .item-info {
            display: flex;
            flex-direction: column;
        }
        
        .cart-item-super .item-name {
            font-weight: 500;
        }
        
        .cart-item-super .item-price {
            color: #666;
            font-size: 0.9rem;
        }
        
        .cart-total-super {
            background: linear-gradient(135deg, #003366, #004d99);
            color: white;
            padding: 20px;
            border-radius: 12px;
            margin-top: 15px;
        }
        
        /* Receipt style */
        .receipt {
            background: white;
            padding: 20px;
            border-radius: 8px;
            font-family: monospace;
            border: 2px dashed #ccc;
            max-width: 400px;
            margin: 0 auto;
        }
        
        .receipt .receipt-header {
            text-align: center;
            border-bottom: 1px dashed #ccc;
            padding-bottom: 10px;
            margin-bottom: 10px;
        }
        
        .receipt .receipt-item {
            display: flex;
            justify-content: space-between;
            padding: 3px 0;
        }
        
        .receipt .receipt-total {
            border-top: 2px solid #000;
            padding-top: 10px;
            margin-top: 10px;
            font-weight: bold;
        }
        
        /* Professional buttons */
        .stButton button {
            border-radius: 8px;
            font-weight: 600;
            transition: 0.3s;
        }
        
        .stButton button:hover {
            transform: scale(1.02);
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        
        /* Professional input */
        .stTextInput input, .stNumberInput input {
            border-radius: 8px;
            border: 2px solid #e0e0e0;
            padding: 10px;
        }
        
        .stTextInput input:focus, .stNumberInput input:focus {
            border-color: #003366;
        }
    </style>
""", unsafe_allow_html=True)

data = load_data()

# Initialize session state
if "cart" not in st.session_state:
    st.session_state.cart = []
if "selected_category" not in st.session_state:
    st.session_state.selected_category = "هموو"
if "receipt_show" not in st.session_state:
    st.session_state.receipt_show = False
if "last_sale" not in st.session_state:
    st.session_state.last_sale = None

# ==================== HEADER - Professional ====================
st.markdown(f"""
    <div class="super-header">
        <div>
            <h1>🏪 {data['settings']['shop_name']}</h1>
            <p style="margin:0; opacity:0.8;">سیستەمی کاشێری پیشەیی</p>
        </div>
        <div class="shop-info">
            <div>📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
            <div>👤 کاشێر: ئەحمەد</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# ==================== MAIN LAYOUT ====================
col_left, col_right = st.columns([2, 1])

# ==================== LEFT COLUMN - Products ====================
with col_left:
    st.markdown('<div style="background:white; padding:15px; border-radius:12px; margin-bottom:15px;">', unsafe_allow_html=True)
    
    # Search Bar like supermarket
    search_col1, search_col2, search_col3 = st.columns([3, 1, 1])
    with search_col1:
        search = st.text_input("🔍 گەڕان بەدوای کاڵا", placeholder="ناو یان بارکۆد...")
    with search_col2:
        if st.button("📷 سکان", use_container_width=True):
            st.info("پشتیوانی سکانەر لە وەشانی داهاتوودا")
    with search_col3:
        if st.button("🔄 نوێکردنەوە", use_container_width=True):
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Categories like supermarket
    st.markdown('<div class="category-tabs">', unsafe_allow_html=True)
    
    # Get all categories from products
    all_categories = list(set([p.get("category", "گشتی") for p in data["products"]]))
    categories = ["هموو"] + all_categories
    
    cols = st.columns(len(categories))
    for idx, cat in enumerate(categories):
        with cols[idx]:
            if st.button(
                cat,
                key=f"cat_{idx}",
                use_container_width=True,
                type="primary" if st.session_state.selected_category == cat else "secondary"
            ):
                st.session_state.selected_category = cat
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Products Grid - like supermarket shelves
    st.markdown('<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 15px;">', unsafe_allow_html=True)
    
    # Filter products
    filtered_products = data["products"]
    if st.session_state.selected_category != "هموو":
        filtered_products = [p for p in data["products"] if p.get("category", "گشتی") == st.session_state.selected_category]
    
    if search:
        filtered_products = [p for p in filtered_products if search.lower() in p["name"].lower() or search in p.get("barcode", "")]
    
    # Display products
    if filtered_products:
        for product in filtered_products:
            with st.container():
                # Determine stock status
                stock_qty = product.get("stock", 999)
                in_stock = stock_qty > 0
                
                st.markdown(f"""
                    <div class="product-card-super">
                        <div class="product-icon">{product.get('icon', '📦')}</div>
                        <div class="product-name">{product['name']}</div>
                        <div class="product-price">{product['price']:,} IQD</div>
                        <div class="product-barcode">#{product.get('barcode', product['name'][:6].upper())}</div>
                        <div class="stock-badge {'in-stock' if in_stock else ''}">
                            {f'{stock_qty}' if in_stock else 'بەتاڵە'}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Add to cart button
                col_qty, col_btn = st.columns([1, 2])
                with col_qty:
                    qty = st.number_input(
                        "ژ",
                        min_value=1,
                        value=1,
                        step=1,
                        key=f"qty_{product['name']}_{product['price']}",
                        label_visibility="collapsed"
                    )
                with col_btn:
                    if st.button(
                        "➕ زیاد",
                        key=f"add_{product['name']}_{product['price']}",
                        use_container_width=True,
                        disabled=not in_stock
                    ):
                        st.session_state.cart.append({
                            "name": product["name"],
                            "price": product["price"],
                            "qty": qty,
                            "total": product["price"] * qty,
                            "barcode": product.get("barcode", ""),
                            "icon": product.get("icon", "📦")
                        })
                        st.success(f"✅ {qty} x {product['name']} زیاد کرا")
                        st.rerun()
    else:
        st.warning("هیچ کاڵایەک نەدۆزرایەوە")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== RIGHT COLUMN - Cart ====================
with col_right:
    st.markdown('<div class="cart-super">', unsafe_allow_html=True)
    st.subheader("🛒 سەبەتە")
    
    if st.session_state.cart:
        total = sum(item["total"] for item in st.session_state.cart)
        total_items = sum(item["qty"] for item in st.session_state.cart)
        
        # Show items
        for idx, item in enumerate(st.session_state.cart):
            st.markdown(f"""
                <div class="cart-item-super">
                    <div class="item-info">
                        <span class="item-name">{item.get('icon', '')} {item['name']}</span>
                        <span class="item-price">{item['qty']} x {item['price']:,} IQD</span>
                    </div>
                    <div style="display:flex; align-items:center; gap:10px;">
                        <span style="font-weight:bold;">{item['total']:,}</span>
                        <button onclick="alert('سڕدرایەوە')" style="background:none; border:none; color:red; cursor:pointer;">✕</button>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"🗑️ سڕ", key=f"remove_cart_{idx}"):
                st.session_state.cart.pop(idx)
                st.rerun()
        
        # Total with tax
        tax = total * data["settings"]["tax_rate"]
        total_with_tax = total + tax
        
        st.markdown(f"""
            <div class="cart-total-super">
                <div style="display:flex; justify-content:space-between; padding:5px 0;">
                    <span>ژمارەی کاڵا:</span>
                    <span>{total_items}</span>
                </div>
                <div style="display:flex; justify-content:space-between; padding:5px 0;">
                    <span>کۆی گشتی:</span>
                    <span>{total:,} IQD</span>
                </div>
                <div style="display:flex; justify-content:space-between; padding:5px 0; border-top:1px solid rgba(255,255,255,0.3);">
                    <span>باج ({int(data['settings']['tax_rate']*100)}%):</span>
                    <span>+ {tax:,.0f} IQD</span>
                </div>
                <div style="display:flex; justify-content:space-between; padding:10px 0 0 0; border-top:2px solid rgba(255,255,255,0.5); font-size:1.4rem;">
                    <span>کۆی گشتی بە باج:</span>
                    <span>{total_with_tax:,.0f} IQD</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Payment options
        col_pay1, col_pay2 = st.columns(2)
        with col_pay1:
            if st.button("💵 پارەدان", use_container_width=True, type="primary"):
                if st.session_state.cart:
                    sale = {
                        "id": data["counter"] + 1,
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "items": st.session_state.cart.copy(),
                        "subtotal": total,
                        "tax": tax,
                        "total": total_with_tax,
                        "payment_method": "نقدی"
                    }
                    data["sales"].append(sale)
                    data["counter"] += 1
                    
                    # Update inventory
                    for item in st.session_state.cart:
                        for product in data["products"]:
                            if product["name"] == item["name"]:
                                product["stock"] = product.get("stock", 999) - item["qty"]
                    
                    save_data(data)
                    st.session_state.last_sale = sale
                    st.session_state.receipt_show = True
                    st.session_state.cart = []
                    st.success("🎉 فرۆشتن تەواو بوو!")
                    st.balloons()
                    st.rerun()
        
        with col_pay2:
            if st.button("🗑️ پاککردنەوە", use_container_width=True):
                st.session_state.cart = []
                st.rerun()
        
        # Receipt
        if st.session_state.receipt_show and st.session_state.last_sale:
            st.markdown("---")
            st.markdown("### 🧾 وەچە (Receipt)")
            sale = st.session_state.last_sale
            
            st.markdown(f"""
                <div class="receipt">
                    <div class="receipt-header">
                        <h3>{data['settings']['shop_name']}</h3>
                        <p>{datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
                        <p>وەچە # {sale['id']}</p>
                    </div>
            """, unsafe_allow_html=True)
            
            for item in sale["items"]:
                st.markdown(f"""
                    <div class="receipt-item">
                        <span>{item['name']} × {item['qty']}</span>
                        <span>{item['total']:,} IQD</span>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown(f"""
                    <div class="receipt-item">
                        <span>کۆی گشتی</span>
                        <span>{sale['subtotal']:,} IQD</span>
                    </div>
                    <div class="receipt-item">
                        <span>باج</span>
                        <span>{sale['tax']:,.0f} IQD</span>
                    </div>
                    <div class="receipt-total">
                        <div class="receipt-item">
                            <span>کۆی گشتی</span>
                            <span>{sale['total']:,.0f} IQD</span>
                        </div>
                    </div>
                    <div style="text-align:center; margin-top:15px; padding-top:10px; border-top:1px dashed #ccc; font-size:0.8rem; color:#999;">
                        {data['settings']['receipt_footer']}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("🖨️ چاپکردن"):
                st.info("پشتیوانی چاپ لە وەشانی داهاتوودا")
            
            if st.button("✕ داخستنی وەچە"):
                st.session_state.receipt_show = False
                st.rerun()
    
    else:
        st.info("🛍️ سەبەتە بەتاڵە")
        st.markdown("""
            <div style="text-align:center; padding:30px 0; color:#999;">
                <p style="font-size:3rem;">🛒</p>
                <p>تکایە کاڵاکانت هەڵبژێرە</p>
                <p style="font-size:0.8rem;">بۆ دەستپێکردنی فرۆشتن</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== ADMIN PANEL (sidebar) ====================
with st.sidebar:
    st.markdown("### ⚙️ بەڕێوەبردنی کۆگا")
    
    admin_tab = st.radio(
        "هەڵبژێرە",
        ["➕ زیادکردنی کاڵا", "📦 لیستی کاڵا", "📊 ڕاپۆرت", "⚙️ کۆنفیگ"],
        label_visibility="collapsed"
    )
    
    if admin_tab == "➕ زیادکردنی کاڵا":
        st.subheader("➕ کاڵای نوێ")
        
        with st.form("add_product_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("🏷️ ناو")
                price = st.number_input("💰 نرخ", min_value=100, value=1000, step=500)
            with col2:
                category = st.text_input("📂 پۆل", value="گشتی")
                stock = st.number_input("📦 کۆتا", min_value=0, value=100, step=10)
                barcode = st.text_input("🔢 بارکۆد", value=datetime.now().strftime("%Y%m%d%H%M")[-8:])
            
            icon = st.selectbox("🎨 ئایکۆن", ["📦", "🥫", "🧃", "🥛", "🍞", "🥩", "🍎", "🧴", "🧹", "📱", "👕", "🛋️"])
            
            if st.form_submit_button("➕ زیادکردن", use_container_width=True, type="primary"):
                data["products"].append({
                    "name": name,
                    "price": price,
                    "category": category,
                    "stock": stock,
                    "barcode": barcode,
                    "icon": icon
                })
                save_data(data)
                st.success(f"✅ {name} زیاد کرا")
                st.rerun()
    
    elif admin_tab == "📦 لیستی کاڵا":
        st.subheader("📦 هەموو کاڵاکان")
        
        if data["products"]:
            for product in data["products"]:
                st.markdown(f"""
                    <div style="background:white; padding:10px; border-radius:8px; margin:5px 0; border-left:4px solid #003366;">
                        <div style="display:flex; justify-content:space-between;">
                            <div>
                                <b>{product.get('icon', '')} {product['name']}</b>
                                <br>
                                <span style="font-size:0.8rem; color:#666;">{product.get('category', 'گشتی')}</span>
                            </div>
                            <div style="text-align:right;">
                                <div style="font-weight:bold; color:#003366;">{product['price']:,} IQD</div>
                                <div style="font-size:0.8rem; color:#999;">کۆتا: {product.get('stock', 0)}</div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"🗑️ سڕ", key=f"del_admin_{product['name']}"):
                    data["products"].remove(product)
                    save_data(data)
                    st.rerun()
        else:
            st.info("هیچ کاڵایەک نیە")
    
    elif admin_tab == "📊 ڕاپۆرت":
        st.subheader("📊 ئاماری فرۆشتن")
        
        if data["sales"]:
            df = pd.DataFrame(data["sales"])
            total_sales = df["total"].sum()
            count_sales = len(df)
            
            col1, col2 = st.columns(2)
            col1.metric("💰 داهات", f"{total_sales:,.0f} IQD")
            col2.metric("🧾 فرۆشتن", count_sales)
            
            st.write("---")
            st.write("**دوایین 5 فرۆشتن:**")
            for sale in data["sales"][-5:]:
                st.write(f"#{sale['id']} - {sale['total']:,.0f} IQD")
        else:
            st.info("هیچ فرۆشتنێک نیە")
    
    elif admin_tab == "⚙️ کۆنفیگ":
        st.subheader("⚙️ کۆنفیگ")
        
        shop_name = st.text_input("🏪 ناوی فرۆشگا", value=data["settings"]["shop_name"])
        tax_rate = st.slider("📊 باج", 0.0, 0.30, data["settings"]["tax_rate"], 0.01)
        footer = st.text_area("📝 پێنووسی وەچە", value=data["settings"]["receipt_footer"])
        
        if st.button("💾 هەڵگرتنی کۆنفیگ", use_container_width=True):
            data["settings"]["shop_name"] = shop_name
            data["settings"]["tax_rate"] = tax_rate
            data["settings"]["receipt_footer"] = footer
            save_data(data)
            st.success("✅ کۆنفیگ هەڵگیرا")
            st.rerun()
        
        st.write("---")
        if st.button("🗑️ سڕینەوەی هەموو داتاکان", use_container_width=True):
            if st.checkbox("دڵنیای؟"):
                data = {"products": [], "categories": [], "sales": [], "users": [], "inventory": [], "counter": 0, "settings": data["settings"]}
                save_data(data)
                st.success("✅ هەموو داتاکان سڕدرانەوە")
                st.rerun()
