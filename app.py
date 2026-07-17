# super_cashier.py
import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# -------------------- کۆنفیگ --------------------
st.set_page_config(
    page_title="سوپەر کاشێر",
    page_icon="🛒",
    layout="wide"
)

# -------------------- داتابەیس (JSON) --------------------
DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"products": [], "sales": [], "counter": 0}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# -------------------- دیزاینی CSS --------------------
st.markdown("""
    <style>
        .main { background-color: #f0f2f6; }
        .card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            margin-bottom: 20px;
        }
        .product-card {
            background: white;
            padding: 15px;
            border-radius: 12px;
            border: 1px solid #e0e0e0;
            transition: 0.3s;
            margin: 8px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .product-card:hover {
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            transform: translateY(-2px);
            border-color: #4CAF50;
        }
        .price-tag {
            color: #2e7d32;
            font-weight: bold;
            font-size: 1.2rem;
        }
        .total-box {
            background: linear-gradient(135deg, #1a237e, #283593);
            color: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            margin-top: 15px;
        }
        .cart-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }
        .btn-primary {
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            border: none;
            font-weight: bold;
        }
        .btn-danger {
            background-color: #f44336;
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            border: none;
            font-weight: bold;
        }
        .product-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
            margin: 15px 0;
        }
        .product-grid-item {
            background: white;
            padding: 15px;
            border-radius: 12px;
            border: 2px solid #e0e0e0;
            text-align: center;
            cursor: pointer;
            transition: 0.3s;
        }
        .product-grid-item:hover {
            border-color: #4CAF50;
            transform: scale(1.02);
            box-shadow: 0 4px 15px rgba(76, 175, 80, 0.2);
        }
        .stButton button {
            border-radius: 8px;
            font-weight: bold;
            transition: 0.3s;
        }
        .stButton button:hover {
            transform: scale(1.02);
        }
    </style>
""", unsafe_allow_html=True)

# بارکردنی داتا
data = load_data()

# Initialize session state
if "cart" not in st.session_state:
    st.session_state.cart = []
if "selected_product" not in st.session_state:
    st.session_state.selected_product = None

# ==================== ناوی فرۆشگا ====================
st.markdown("""
    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #1a237e, #0d47a1); border-radius: 15px; margin-bottom: 30px;">
        <h1 style="color: white; margin: 0;">🛒 سوپەر کاشێر</h1>
        <p style="color: #e3f2fd; margin: 5px 0;">سیستەمی پیشەیی بەڕێوەبردنی فرۆشتن</p>
    </div>
""", unsafe_allow_html=True)

# ==================== تابەکان ====================
tab1, tab2, tab3, tab4 = st.tabs(["🧾 فرۆشتن", "📦 بەڕێوەبردنی کاڵا", "📊 ڕاپۆرت", "⚙️ کۆنفیگ"])

# ==================== تاب 1: فرۆشتن ====================
with tab1:
    st.header("🧾 فرۆشتن")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📦 کاڵاکان")
        
        # نمایش بە شێوەی گرید
        if data["products"]:
            # Searching
            search = st.text_input("🔍 گەڕان بەدوای کاڵا", placeholder="ناوی کاڵا بنووسە...")
            
            # Filter products
            filtered_products = data["products"]
            if search:
                filtered_products = [p for p in data["products"] if search.lower() in p["name"].lower()]
            
            if filtered_products:
                # نمایش بە شێوەی کارت
                cols = st.columns(3)
                for idx, product in enumerate(filtered_products):
                    with cols[idx % 3]:
                        with st.container():
                            st.markdown(f"""
                                <div class="product-grid-item" onclick="alert('{product['name']}')">
                                    <div style="font-size: 3rem;">📦</div>
                                    <h4>{product['name']}</h4>
                                    <p class="price-tag">{product['price']:,} IQD</p>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            col_qty, col_btn = st.columns([1, 2])
                            with col_qty:
                                qty = st.number_input("ژمارد", min_value=1, value=1, step=1, key=f"qty_{idx}")
                            with col_btn:
                                if st.button("➕ زیاد بکە", key=f"add_{idx}", use_container_width=True):
                                    st.session_state.cart.append({
                                        "name": product["name"],
                                        "price": product["price"],
                                        "qty": qty,
                                        "total": product["price"] * qty
                                    })
                                    st.success(f"✅ {qty} x {product['name']} زیاد کرا")
                                    st.rerun()
            else:
                st.warning("هیچ کاڵایەک نەدۆزرایەوە")
        else:
            st.warning("⚠️ هیچ کاڵایەک نیە! تکایە سەرەتا کاڵا زیاد بکە لە تابەکەی 'بەڕێوەبردنی کاڵا'")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🛒 سەبەتە")
        
        if st.session_state.cart:
            total = sum(item["total"] for item in st.session_state.cart)
            
            # نمایشی کاڵاکانی سەبەتە
            for i, item in enumerate(st.session_state.cart):
                st.markdown(f"""
                    <div class="cart-item">
                        <div>
                            <b>{item['name']}</b>
                            <span style="color: #666;">× {item['qty']}</span>
                        </div>
                        <div>
                            <span class="price-tag">{item['total']:,} IQD</span>
                            <button onclick="alert('سڕدرایەوە')" style="background: none; border: none; color: red; cursor: pointer;">✕</button>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Delete individual item
                if st.button(f"🗑️ سڕینەوە", key=f"remove_{i}"):
                    st.session_state.cart.pop(i)
                    st.rerun()
            
            # کۆی گشتی
            st.markdown(f"""
                <div class="total-box">
                    <h3>💰 کۆی گشتی</h3>
                    <h2 style="font-size: 2.5rem; margin: 10px 0;">{total:,} IQD</h2>
                </div>
            """, unsafe_allow_html=True)
            
            # دوگمەکان
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("✅ تەواوکردنی فرۆشتن", use_container_width=True, type="primary"):
                    if st.session_state.cart:
                        sale = {
                            "id": data["counter"] + 1,
                            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "items": st.session_state.cart.copy(),
                            "total": total
                        }
                        data["sales"].append(sale)
                        data["counter"] += 1
                        save_data(data)
                        st.session_state.cart = []
                        st.success("🎉 فرۆشتن تۆمار کرا! سوپاس")
                        st.balloons()
                        st.rerun()
            with col_btn2:
                if st.button("🗑️ پاککردنەوە", use_container_width=True):
                    st.session_state.cart = []
                    st.rerun()
        else:
            st.info("🛒 سەبەتە بەتاڵە")
            st.markdown("""
                <div style="text-align: center; padding: 20px; color: #999;">
                    <p style="font-size: 3rem;">🛍️</p>
                    <p>هیچ کاڵایەک نیە لە سەبەتەدا</p>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# ==================== تاب 2: بەڕێوەبردنی کاڵا ====================
with tab2:
    st.header("📦 بەڕێوەبردنی کاڵا")
    
    # زیادکردنی کاڵا - فۆرم
    with st.expander("➕ زیادکردنی کاڵای نوێ", expanded=True):
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("زیادکردنی کاڵا")
        
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            new_name = st.text_input("🏷️ ناوی کاڵا", placeholder="وشەی کاڵا بنووسە...")
        with col2:
            new_price = st.number_input("💰 نرخ (IQD)", min_value=100, value=1000, step=500)
        with col3:
            st.write(" ")
            if st.button("➕ زیاد بکە", use_container_width=True, type="primary"):
                if new_name and new_price > 0:
                    # Check if product already exists
                    existing = [p for p in data["products"] if p["name"].lower() == new_name.lower()]
                    if existing:
                        st.warning(f"⚠️ کاڵای '{new_name}' پێشتر هەیە!")
                    else:
                        data["products"].append({"name": new_name, "price": new_price})
                        save_data(data)
                        st.success(f"✅ '{new_name}' بە سەرکەوتوویی زیاد کرا")
                        st.rerun()
                else:
                    st.error("⚠️ تکایە ناو و نرخێکی دروست داخل بکە")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # زیادکردنی چەندین کاڵا لە یەک جار
    with st.expander("📥 زیادکردنی چەندین کاڵا لە یەک جار", expanded=False):
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.write("کاڵاکان بەم شێوەیە بنووسە: **ناو,نرخ** (هەر کاڵا لە هێڵێکدا)")
        
        bulk_input = st.text_area(
            "کاڵاکان",
            height=150,
            placeholder="شیر,1500\nنان,1000\nپەنیر,2500\nکەرە,3000",
            help="هەر کاڵا لە هێڵێکدا بنووسە، بە کۆما جیای بکەوە"
        )
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("📥 زیادکردنی هەمووی", use_container_width=True, type="primary"):
                if bulk_input:
                    added = 0
                    for line in bulk_input.strip().split("\n"):
                        if "," in line:
                            try:
                                name, price = line.split(",")
                                name = name.strip()
                                price = int(price.strip())
                                if name and price > 0:
                                    # Check for duplicates
                                    existing = [p for p in data["products"] if p["name"].lower() == name.lower()]
                                    if not existing:
                                        data["products"].append({"name": name, "price": price})
                                        added += 1
                            except:
                                pass
                    if added > 0:
                        save_data(data)
                        st.success(f"✅ {added} کاڵا بە سەرکەوتوویی زیاد کران")
                        st.rerun()
                    else:
                        st.warning("⚠️ هیچ کاڵایەک زیاد نەکرا! تکایە فۆرماتەکە ڕێک بکە")
                else:
                    st.warning("⚠️ تکایە کاڵاکان بنووسە")
        
        with col_btn2:
            if st.button("📋 نموونە", use_container_width=True):
                st.info("""
                نموونە:
                ```
                شیر,1500
                نان,1000
                پەنیر,2500
                کەرە,3000
                تۆمات,500
                بەیبی,750
                ```
                """)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # لیستی کاڵاکان
    st.subheader("📋 لیستی کاڵاکان")
    
    if data["products"]:
        # Search and filter
        search_products = st.text_input("🔍 گەڕان لەناو کاڵاکان", placeholder="ناوی کاڵا بنووسە...")
        
        display_products = data["products"]
        if search_products:
            display_products = [p for p in data["products"] if search_products.lower() in p["name"].lower()]
        
        # نمایش بە شێوەی خشتە
        for idx, product in enumerate(display_products):
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            with col1:
                st.write(f"🏷️ **{product['name']}**")
            with col2:
                st.write(f"💰 {product['price']:,} IQD")
            with col3:
                # Edit price
                new_price = st.number_input(
                    "نوێ",
                    min_value=100,
                    value=product['price'],
                    step=500,
                    key=f"edit_{idx}",
                    label_visibility="collapsed"
                )
                if new_price != product['price']:
                    if st.button("💾 نوێکردنەوە", key=f"update_{idx}"):
                        product['price'] = new_price
                        save_data(data)
                        st.success(f"✅ نرخی {product['name']} نوێکرایەوە")
                        st.rerun()
            with col4:
                if st.button("🗑️", key=f"del_{idx}", help="سڕینەوەی کاڵا"):
                    data["products"].pop(data["products"].index(product))
                    save_data(data)
                    st.rerun()
        
        # ئاماری کاڵاکان
        st.markdown(f"""
            <div style="background: #e3f2fd; padding: 15px; border-radius: 10px; margin-top: 15px;">
                <b>📊 ئامار:</b> {len(data['products'])} کاڵا لە کۆگادا
                | 💰 نرخی تێکڕا: {sum(p['price'] for p in data['products']) / len(data['products']):,.0f} IQD
                | 💎 گرانترین: {max(data['products'], key=lambda x: x['price'])['name']} ({max(data['products'], key=lambda x: x['price'])['price']:,} IQD)
            </div>
        """, unsafe_allow_html=True)
    else:
        st.info("📭 هیچ کاڵایەک نیە! سەرەتا کاڵا زیاد بکە")

# ==================== تاب 3: ڕاپۆرت ====================
with tab3:
    st.header("📊 ڕاپۆرت و داهات")
    
    if data["sales"]:
        df = pd.DataFrame(data["sales"])
        df["date"] = pd.to_datetime(df["date"])
        
        # ئاماری سەرەکی
        total_revenue = df["total"].sum()
        total_sales = len(df)
        avg_sale = df["total"].mean() if total_sales > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("💰 کۆی داهات", f"{total_revenue:,} IQD")
        col2.metric("🧾 ژمارەی فرۆشتن", total_sales)
        col3.metric("📊 تێکڕای فرۆشتن", f"{avg_sale:,.0f} IQD")
        col4.metric("📅 دوایین فرۆشتن", df["date"].max().strftime("%Y-%m-%d") if total_sales > 0 else "نیە")
        
        # گرافی ڕۆژانە
        st.subheader("📈 ئاماری ڕۆژانە")
        daily = df.groupby(df["date"].dt.date)["total"].sum().reset_index()
        st.bar_chart(daily.set_index("date"))
        
        # گرافی مانگانە
        st.subheader("📊 ئاماری مانگانە")
        monthly = df.groupby(df["date"].dt.strftime("%Y-%m"))["total"].sum().reset_index()
        st.line_chart(monthly.set_index("date"))
        
        # خشتەی فرۆشتنەکان
        with st.expander("📋 بینینی هەموو فرۆشتنەکان", expanded=False):
            st.dataframe(
                df[["id", "date", "total"]].sort_values("date", ascending=False),
                use_container_width=True,
                column_config={
                    "id": "ژمارە",
                    "date": "کات",
                    "total": st.column_config.NumberColumn("کۆی گشتی", format="%d IQD")
                }
            )
            
            # Export to CSV
            csv = df[["id", "date", "total"]].to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 دابەزاندنی ڕاپۆرت (CSV)",
                data=csv,
                file_name=f"report_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    else:
        st.info("📭 هیچ فرۆشتنێک تۆمار نەکراوە")
        st.markdown("""
            <div style="text-align: center; padding: 40px; color: #999;">
                <p style="font-size: 4rem;">📊</p>
                <p>هیچ داتایەک نیە بۆ پیشاندان</p>
                <p style="font-size: 0.9rem;">دوای تۆمارکردنی یەکەم فرۆشتن، ڕاپۆرتەکان دەردەکەون</p>
            </div>
        """, unsafe_allow_html=True)

# ==================== تاب 4: کۆنفیگ ====================
with tab4:
    st.header("⚙️ کۆنفیگ و بەڕێوەبردنی سیستەم")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🗄️ داتاکان")
        st.write(f"📁 پەڕگەی داتا: `{DATA_FILE}`")
        st.write(f"📊 ژمارەی کاڵا: {len(data['products'])}")
        st.write(f"🧾 ژمارەی فرۆشتن: {len(data['sales'])}")
        st.write(f"📈 کۆی داهات: {sum(s['total'] for s in data['sales']):,} IQD")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🛠️ ئامرازەکان")
        
        # دابەزاندنی backup
        if data["sales"] or data["products"]:
            backup_data = json.dumps(data, ensure_ascii=False, indent=2)
            st.download_button(
                label="💾 دابەزاندنی پشتیوانی (Backup)",
                data=backup_data,
                file_name=f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        # سڕینەوەی هەموو داتاکان
        with st.expander("⚠️ سڕینەوەی هەموو داتاکان", expanded=False):
            st.warning("ئاگادار! ئەم کردارە هەموو داتاکان بەهەمیشەیی دەسڕێتەوە")
            if st.button("🗑️ سڕینەوەی هەموو داتاکان", use_container_width=True):
                if st.checkbox("دڵنیای لە سڕینەوەی هەموو داتاکان؟"):
                    data = {"products": [], "sales": [], "counter": 0}
                    save_data(data)
                    st.session_state.cart = []
                    st.success("✅ هەموو داتاکان بە سەرکەوتوویی سڕدرانەوە")
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # زانیاری زیاتر
    st.markdown("""
        <div style="background: #e8f5e9; padding: 20px; border-radius: 15px; margin-top: 20px; border-left: 5px solid #4CAF50;">
            <h4>💡 ڕێنمایی</h4>
            <ul>
                <li>کاڵا زیاد بکە لە تابەکەی "بەڕێوەبردنی کاڵا"</li>
                <li>فرۆشتن ئەنجام بدە لە تابەکەی "فرۆشتن"</li>
                <li>ڕاپۆرتەکان ببینە لە تابەکەی "ڕاپۆرت"</li>
                <li>پشتیوانی لە داتاکان بگرە لە تابەکەی "کۆنفیگ"</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

# ==================== Footer ====================
st.markdown("""
    <hr>
    <div style="text-align: center; color: #999; padding: 20px;">
        <p>🛒 سوپەر کاشێر © 2026 | دروست کراوە بە ❤️ و Streamlit</p>
        <p style="font-size: 0.8rem;">هەموو کاڵاکان لە کۆگادا</p>
    </div>
""", unsafe_allow_html=True)
