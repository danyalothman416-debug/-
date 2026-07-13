import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import time

# Page configuration
st.set_page_config(
    page_title="کاشێری زیرەک | Smart Cashier",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'cart' not in st.session_state:
    st.session_state.cart = []
if 'products' not in st.session_state:
    st.session_state.products = [
        {"id": 1, "name": "نان", "price": 500, "category": "خۆراک", "stock": 50},
        {"id": 2, "name": "شیر", "price": 1500, "category": "خواردنەوە", "stock": 30},
        {"id": 3, "name": "برنج", "price": 3000, "category": "خۆراک", "stock": 25},
        {"id": 4, "name": "ڕۆن", "price": 2500, "category": "خۆراک", "stock": 20},
        {"id": 5, "name": "شەکر", "price": 1000, "category": "خۆراک", "stock": 40},
        {"id": 6, "name": "چای", "price": 2000, "category": "خواردنەوە", "stock": 35},
        {"id": 7, "name": "سێو", "price": 750, "category": "میوە", "stock": 60},
        {"id": 8, "name": "پرتەقاڵ", "price": 600, "category": "میوە", "stock": 45},
        {"id": 9, "name": "هێلکە", "price": 4000, "category": "خۆراک", "stock": 15},
        {"id": 10, "name": "ماکارۆنی", "price": 1500, "category": "خۆراک", "stock": 30},
    ]
if 'total_sales' not in st.session_state:
    st.session_state.total_sales = 0
if 'sale_history' not in st.session_state:
    st.session_state.sale_history = []

# Custom CSS for RTL and styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@300;400;500;600;700&display=swap');
    
    * {
        direction: rtl;
        font-family: 'Rajdhani', sans-serif;
    }
    
    .main-header {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .product-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        transition: transform 0.3s;
        margin: 10px 0;
    }
    
    .product-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.2);
    }
    
    .cart-item {
        padding: 10px;
        margin: 5px 0;
        border-bottom: 1px solid #eee;
    }
    
    .total-section {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        font-size: 24px;
        font-weight: bold;
    }
    
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        font-weight: 600;
        padding: 10px;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        transform: scale(1.05);
    }
    </style>
""", unsafe_allow_html=True)

# Main Header
st.markdown("""
    <div class="main-header">
        <h1>🛒 کاشێری زیرەک</h1>
        <p style="font-size: 18px;">سیستەمی زیرەکی فرۆشتن و بەڕێوەبردنی کڕین</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## ⚙️ **ڕێکخستنەکان**")
    
    # User type selection
    user_type = st.radio("جۆری بەکارهێنەر:", ["👤 کاشێر", "👨‍💼 بەڕێوەبەر"])
    
    st.markdown("---")
    
    if user_type == "👨‍💼 بەڕێوەبەر":
        st.markdown("### 📊 **ئامارەکان**")
        total_products = len(st.session_state.products)
        total_stock = sum(p['stock'] for p in st.session_state.products)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("کۆی بەرهەمەکان", total_products)
        with col2:
            st.metric("کۆی کۆگا", total_stock)
        
        st.metric("کۆی فرۆشتن", f"{st.session_state.total_sales:,.0f} دینار")
    
    st.markdown("---")
    st.markdown("### 🔍 **گەڕان**")
    search_query = st.text_input("ناوی بەرهەم بگەڕێ...")

# Main layout
if user_type == "👤 کاشێر":
    # Cashier Interface
    tab1, tab2 = st.tabs(["🛍️ فرۆشتن", "📋 مێژووی فرۆشتن"])
    
    with tab1:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 📦 **بەرهەمە بەردەستەکان**")
            
            # Filter products based on search
            if search_query:
                filtered_products = [p for p in st.session_state.products 
                                   if search_query.lower() in p['name'].lower()]
            else:
                filtered_products = st.session_state.products
            
            # Display products in grid
            cols = st.columns(3)
            for idx, product in enumerate(filtered_products):
                with cols[idx % 3]:
                    with st.container():
                        st.markdown(f"""
                            <div class="product-card">
                                <h4>{product['name']}</h4>
                                <p>💰 {product['price']:,.0f} دینار</p>
                                <p>📦 کۆگا: {product['stock']}</p>
                                <p>🏷️ {product['category']}</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        col_add, col_qty = st.columns([2, 1])
                        with col_qty:
                            quantity = st.number_input(
                                "دانە",
                                min_value=1,
                                max_value=product['stock'],
                                value=1,
                                key=f"qty_{product['id']}_{idx}"
                            )
                        with col_add:
                            if st.button(f"➕ زیادبکە", key=f"add_{product['id']}_{idx}"):
                                # Add to cart
                                cart_item = {
                                    'id': product['id'],
                                    'name': product['name'],
                                    'price': product['price'],
                                    'quantity': quantity,
                                    'total': product['price'] * quantity
                                }
                                
                                # Check if product already in cart
                                existing = [i for i, item in enumerate(st.session_state.cart) 
                                          if item['id'] == product['id']]
                                if existing:
                                    st.session_state.cart[existing[0]]['quantity'] += quantity
                                    st.session_state.cart[existing[0]]['total'] = (
                                        st.session_state.cart[existing[0]]['price'] * 
                                        st.session_state.cart[existing[0]]['quantity']
                                    )
                                else:
                                    st.session_state.cart.append(cart_item)
                                
                                # Update stock
                                product['stock'] -= quantity
                                st.success(f"{product['name']} زیادکرا بە سەربەرستی!")
                                st.rerun()
        
        with col2:
            st.markdown("### 🛒 **سەبەتەی کڕین**")
            
            if not st.session_state.cart:
                st.info("سەبەتەکەت بەتاڵە. بەرهەم زیادبکە بۆ دەستپێکردن.")
            else:
                # Display cart items
                total_amount = 0
                for idx, item in enumerate(st.session_state.cart):
                    st.markdown(f"""
                        <div class="cart-item">
                            <strong>{item['name']}</strong><br>
                            <small>{item['quantity']} × {item['price']:,.0f} = {item['total']:,.0f} دینار</small>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    col_edit, col_del = st.columns([1, 1])
                    with col_edit:
                        new_qty = st.number_input(
                            "چاککردنەوە",
                            min_value=1,
                            value=item['quantity'],
                            key=f"edit_{idx}"
                        )
                        if new_qty != item['quantity']:
                            # Update stock
                            old_product = next(p for p in st.session_state.products if p['id'] == item['id'])
                            old_product['stock'] += item['quantity'] - new_qty
                            item['quantity'] = new_qty
                            item['total'] = item['price'] * new_qty
                            st.rerun()
                    
                    with col_del:
                        if st.button("🗑️", key=f"del_{idx}"):
                            # Return to stock
                            old_product = next(p for p in st.session_state.products if p['id'] == item['id'])
                            old_product['stock'] += item['quantity']
                            st.session_state.cart.pop(idx)
                            st.rerun()
                    
                    total_amount += item['total']
                    st.markdown("---")
                
                # Total and checkout
                st.markdown(f"""
                    <div class="total-section">
                        <center>
                            <h3>کۆی گشتی</h3>
                            <h2>{total_amount:,.0f} دینار</h2>
                        </center>
                    </div>
                """, unsafe_allow_html=True)
                
                col_checkout, col_clear = st.columns(2)
                with col_checkout:
                    if st.button("💳 پارەدان", type="primary", use_container_width=True):
                        # Process sale
                        sale_record = {
                            'time': datetime.now(),
                            'items': st.session_state.cart.copy(),
                            'total': total_amount
                        }
                        st.session_state.sale_history.append(sale_record)
                        st.session_state.total_sales += total_amount
                        st.session_state.cart = []
                        st.success("فرۆشتن بە سەرکەوتوویی ئەنجامدرا!")
                        st.balloons()
                        st.rerun()
                
                with col_clear:
                    if st.button("🗑️ بەتاڵکردنەوە", use_container_width=True):
                        # Return all items to stock
                        for item in st.session_state.cart:
                            product = next(p for p in st.session_state.products if p['id'] == item['id'])
                            product['stock'] += item['quantity']
                        st.session_state.cart = []
                        st.rerun()
    
    with tab2:
        st.markdown("### 📋 **مێژووی فرۆشتن**")
        
        if not st.session_state.sale_history:
            st.info("هێشتا هیچ فرۆشتنێک نەکراوە.")
        else:
            for idx, sale in enumerate(reversed(st.session_state.sale_history)):
                with st.expander(f"فرۆشتن {len(st.session_state.sale_history) - idx} - {sale['time'].strftime('%Y-%m-%d %H:%M:%S')}"):
                    # Create DataFrame for items
                    items_df = pd.DataFrame(sale['items'])
                    items_df['total'] = items_df['total'].apply(lambda x: f"{x:,.0f} دینار")
                    st.dataframe(items_df[['name', 'quantity', 'price', 'total']], use_container_width=True)
                    st.markdown(f"**کۆی گشتی: {sale['total']:,.0f} دینار**")

else:
    # Admin Interface
    tab1, tab2, tab3 = st.tabs(["📊 داشبۆرد", "📦 بەرهەمەکان", "📈 ڕاپۆرت"])
    
    with tab1:
        st.markdown("### 📊 **داشبۆردی بەڕێوەبەر**")
        
        # Statistics cards
        col1, col2, col3, col4 = st.columns(4)
        
        total_products = len(st.session_state.products)
        total_stock = sum(p['stock'] for p in st.session_state.products)
        total_value = sum(p['stock'] * p['price'] for p in st.session_state.products)
        avg_price = sum(p['price'] for p in st.session_state.products) / total_products if total_products > 0 else 0
        
        with col1:
            st.metric("کۆی بەرهەمەکان", total_products)
        with col2:
            st.metric("کۆی کۆگا", total_stock, delta="10%")
        with col3:
            st.metric("بەهای کۆگا", f"{total_value:,.0f} دینار")
        with col4:
            st.metric("نرخی مامناوەند", f"{avg_price:,.0f} دینار")
        
        st.markdown("---")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 دابەشبوونی بەرهەمەکان بەپێی پۆلێن")
            categories = {}
            for product in st.session_state.products:
                cat = product['category']
                if cat in categories:
                    categories[cat] += product['stock']
                else:
                    categories[cat] = product['stock']
            
            fig = px.pie(
                values=list(categories.values()),
                names=list(categories.keys()),
                title="پۆلێنەکان"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### 📈 بەرهەمەکان بەپێی نرخ")
            products_df = pd.DataFrame(st.session_state.products)
            fig = px.bar(
                products_df,
                x='name',
                y='price',
                color='category',
                title="نرخی بەرهەمەکان"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.markdown("### 📦 **بەڕێوەبردنی بەرهەمەکان**")
        
        # Add new product
        with st.expander("➕ زیادکردنی بەرهەمی نوێ", expanded=False):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                new_name = st.text_input("ناوی بەرهەم")
            with col2:
                new_price = st.number_input("نرخ", min_value=0, value=1000)
            with col3:
                new_category = st.selectbox("پۆلێن", ["خۆراک", "خواردنەوە", "میوە", "پاککەرەوە", "تری"])
            with col4:
                new_stock = st.number_input("دانە", min_value=0, value=10)
            
            if st.button("زیادکردنی بەرهەم", type="primary"):
                if new_name:
                    new_id = max([p['id'] for p in st.session_state.products]) + 1 if st.session_state.products else 1
                    st.session_state.products.append({
                        "id": new_id,
                        "name": new_name,
                        "price": new_price,
                        "category": new_category,
                        "stock": new_stock
                    })
                    st.success(f"بەرهەمی {new_name} بە سەرکەوتوویی زیادکرا!")
                    st.rerun()
                else:
                    st.error("تکایە ناوی بەرهەم بنووسە")
        
        # Edit products table
        st.markdown("#### ✏️ دەستکاری بەرهەمەکان")
        
        products_df = pd.DataFrame(st.session_state.products)
        edited_df = st.data_editor(
            products_df,
            column_config={
                "id": st.column_config.NumberColumn("ID", disabled=True),
                "name": st.column_config.TextColumn("ناو"),
                "price": st.column_config.NumberColumn("نرخ", format="%d دینار"),
                "category": st.column_config.SelectboxColumn("پۆلێن", options=["خۆراک", "خواردنەوە", "میوە", "پاککەرەوە", "تری"]),
                "stock": st.column_config.NumberColumn("کۆگا")
            },
            hide_index=True,
            use_container_width=True
        )
        
        if st.button("💾 پاشەکەوتکردنی گۆڕانکارییەکان"):
            st.session_state.products = edited_df.to_dict('records')
            st.success("گۆڕانکارییەکان پاشەکەوت کران!")
            st.rerun()
    
    with tab3:
        st.markdown("### 📈 **ڕاپۆرتەکان**")
        
        # Sales report
        st.markdown("#### 💰 ڕاپۆرتی فرۆشتن")
        
        if st.session_state.sale_history:
            sales_data = []
            for sale in st.session_state.sale_history:
                for item in sale['items']:
                    sales_data.append({
                        'کات': sale['time'],
                        'بەرهەم': item['name'],
                        'دانە': item['quantity'],
                        'نرخ': item['price'],
                        'کۆ': item['total']
                    })
            
            sales_df = pd.DataFrame(sales_data)
            
            # Filter by date
            col1, col2 = st.columns(2)
            with col1:
                if not sales_df.empty:
                    min_date = sales_df['کات'].min().date()
                    max_date = sales_df['کات'].max().date()
                    date_range = st.date_input("مەودای ڕێکەوت", [min_date, max_date])
            
            # Display sales table
            st.dataframe(sales_df, use_container_width=True)
            
            # Download report
            csv = sales_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                "📥 دابەزاندنی ڕاپۆرت",
                csv,
                "sales_report.csv",
                "text/csv",
                key='download-csv'
            )
        else:
            st.info("هێشتا هیچ فرۆشتنێک نەکراوە بۆ دروستکردنی ڕاپۆرت.")

# Footer
st.markdown("---")
st.markdown("""
    <center>
        <p style="color: #666;">
            © 2024 کاشێری زیرەک | دروستکراوە بە ❤️ لەلایەن تیمەکەمان
        </p>
    </center>
""", unsafe_allow_html=True)
