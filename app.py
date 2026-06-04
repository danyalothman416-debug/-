import streamlit as st
import sqlite3
from datetime import datetime
import hashlib
import os
from PIL import Image
import io
import base64
import pandas as pd

# ڕێکخستنی پەیج
st.set_page_config(
    page_title="📱 دوکانی مۆبایل - Mobile Shop",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS بۆ جوانکاری
st.markdown("""
<style>
    /* سەرەکی */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Naskh+Arabic&display=swap');
    
    * {
        font-family: 'Noto Naskh Arabic', sans-serif;
        direction: rtl;
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    /* کارتی بەرهەم */
    .product-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        transition: transform 0.3s, box-shadow 0.3s;
        margin-bottom: 1rem;
        border: 2px solid #f0f0f0;
    }
    
    .product-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        border-color: #667eea;
    }
    
    .price-tag {
        font-size: 1.8rem;
        font-weight: bold;
        color: #28a745;
        background: #f0fff4;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
    }
    
    .old-price {
        text-decoration: line-through;
        color: #dc3545;
        font-size: 1.2rem;
    }
    
    .discount-badge {
        background: #dc3545;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 0.9rem;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .category-btn {
        padding: 10px;
        border-radius: 25px;
        border: 2px solid #667eea;
        background: transparent;
        color: #667eea;
        cursor: pointer;
        transition: all 0.3s;
        text-align: center;
        margin: 5px;
    }
    
    .category-btn:hover, .category-btn.active {
        background: #667eea;
        color: white;
    }
    
    .cart-icon {
        font-size: 2rem;
        position: relative;
    }
    
    .cart-count {
        position: absolute;
        top: -10px;
        right: -10px;
        background: #dc3545;
        color: white;
        border-radius: 50%;
        padding: 2px 8px;
        font-size: 0.8rem;
    }
    
    /* سەبەتە */
    .cart-item {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .total-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ==================== DATABASE SETUP ====================
def init_db():
    """دروستکردنی بنکەدراوە"""
    conn = sqlite3.connect('mobile_shop.db')
    c = conn.cursor()
    
    # خشتەی بەرهەمەکان
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            brand TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            old_price REAL,
            description TEXT,
            specs TEXT,
            image_url TEXT,
            stock INTEGER DEFAULT 10,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # خشتەی کارت
    c.execute('''
        CREATE TABLE IF NOT EXISTS cart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            quantity INTEGER DEFAULT 1,
            session_id TEXT,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    
    # خشتەی داواکارییەکان
    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT,
            total_amount REAL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # خشتەی وردەکاری داواکاری
    c.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            price REAL,
            FOREIGN KEY (order_id) REFERENCES orders (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def add_sample_products():
    """زیادکردنی بەرهەمی نموونە"""
    conn = sqlite3.connect('mobile_shop.db')
    c = conn.cursor()
    
    # سڕینەوەی داتا کۆنەکان
    c.execute('DELETE FROM products')
    
    # بەرهەمی نموونە
    products = [
        ('ئایفۆن ١٥ پرۆ مەکس', 'Apple', 'آیفون', 1450000, 1650000,
         'نوێترین ئایفۆن لەگەڵ کامێرای ٤٨ مێگاپێکسڵ و پڕۆسێسەری A17 Pro',
         '{"پەردە": "6.7 ئینج OLED", "کامێرا": "48MP + 12MP + 12MP", "پڕۆسێسەر": "A17 Pro", "بەتری": "4422mAh", "بیرگە": "256GB"}',
         'https://fdn2.gsmarena.com/vv/pics/apple/apple-iphone-15-pro-max-1.jpg', 15),
        
        ('سامسونگ گالاکسی S24 ئەلترا', 'Samsung', 'سامسونگ', 1350000, 1500000,
         'گالاکسی S24 ئەلترا لەگەڵ پێنسی S-Pen و کامێرای ٢٠٠ مێگاپێکسڵ',
         '{"پەردە": "6.8 ئینج Dynamic AMOLED", "کامێرا": "200MP + 50MP + 12MP + 10MP", "پڕۆسێسەر": "Snapdragon 8 Gen 3", "بەتری": "5000mAh", "بیرگە": "512GB"}',
         'https://fdn2.gsmarena.com/vv/pics/samsung/samsung-galaxy-s24-ultra-1.jpg', 12),
        
        ('شیاومی ١٤ پرۆ', 'Xiaomi', 'شیاومی', 850000, 950000,
         'مۆبایلی بەهێز لەگەڵ کامێرای لایکا و پڕۆسێسەری Snapdragon 8 Gen 3',
         '{"پەردە": "6.73 ئینج AMOLED", "کامێرا": "50MP + 50MP + 50MP", "پڕۆسێسەر": "Snapdragon 8 Gen 3", "بەتری": "4880mAh", "بیرگە": "256GB"}',
         'https://fdn2.gsmarena.com/vv/pics/xiaomi/xiaomi-14-pro-1.jpg', 20),
        
        ('گوگڵ پێکسڵ ٨ پرۆ', 'Google', 'گوگڵ', 1100000, 1200000,
         'مۆبایلی گوگڵ لەگەڵ ئەندڕۆیدی پاك و کامێرای ژیری دەستکرد',
         '{"پەردە": "6.7 ئینج LTPO OLED", "کامێرا": "50MP + 48MP + 48MP", "پڕۆسێسەر": "Tensor G3", "بەتری": "5050mAh", "بیرگە": "128GB"}',
         'https://fdn2.gsmarena.com/vv/pics/google/google-pixel-8-pro-1.jpg', 8),
        
        ('وەن پڵەس ١٢', 'OnePlus', 'وەن پڵەس', 950000, 1050000,
         'مۆبایلی خێرا و بەهێز لەگەڵ شاشەی 120Hz و بارگاویکەری خێرا',
         '{"پەردە": "6.82 ئینج LTPO AMOLED", "کامێرا": "50MP + 64MP + 48MP", "پڕۆسێسەر": "Snapdragon 8 Gen 3", "بەتری": "5400mAh", "بیرگە": "256GB"}',
         'https://fdn2.gsmarena.com/vv/pics/oneplus/oneplus-12-1.jpg', 10),
        
        ('هواوی P60 پرۆ', 'Huawei', 'هواوی', 750000, 850000,
         'مۆبایلی هواوی لەگەڵ کامێرای نایاب و دیزاینی جوان',
         '{"پەردە": "6.67 ئینج OLED", "کامێرا": "48MP + 48MP + 13MP", "پڕۆسێسەر": "Snapdragon 8+ Gen 1", "بەتری": "4815mAh", "بیرگە": "256GB"}',
         'https://fdn2.gsmarena.com/vv/pics/huawei/huawei-p60-pro-1.jpg', 7),
    ]
    
    c.executemany('''
        INSERT INTO products (name, brand, category, price, old_price, description, specs, image_url, stock)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', products)
    
    conn.commit()
    conn.close()

# دەستپێکردنی بنکەدراوە
init_db()
# زیادکردنی بەرهەمی نموونە (تەنها یەک جار)
conn = sqlite3.connect('mobile_shop.db')
c = conn.cursor()
c.execute('SELECT COUNT(*) FROM products')
if c.fetchone()[0] == 0:
    add_sample_products()
conn.close()

# ==================== FUNCTIONS ====================
def get_products(category=None, search=None):
    """وەرگرتنی بەرهەمەکان لە بنکەدراوە"""
    conn = sqlite3.connect('mobile_shop.db')
    query = "SELECT * FROM products WHERE 1=1"
    params = []
    
    if category and category != "هەموو":
        query += " AND category = ?"
        params.append(category)
    
    if search:
        query += " AND (name LIKE ? OR brand LIKE ? OR description LIKE ?)"
        search_param = f"%{search}%"
        params.extend([search_param, search_param, search_param])
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def add_to_cart(product_id, session_id):
    """زیادکردنی بەرهەم بۆ سەبەتە"""
    conn = sqlite3.connect('mobile_shop.db')
    c = conn.cursor()
    
    # بڕوانین ئایا بەرهەمەکە هەیە لە سەبەتە
    c.execute('SELECT id, quantity FROM cart WHERE product_id = ? AND session_id = ?',
             (product_id, session_id))
    existing = c.fetchone()
    
    if existing:
        c.execute('UPDATE cart SET quantity = quantity + 1 WHERE id = ?', (existing[0],))
    else:
        c.execute('INSERT INTO cart (product_id, session_id) VALUES (?, ?)',
                 (product_id, session_id))
    
    conn.commit()
    conn.close()

def get_cart(session_id):
    """وەرگرتنی ناوەڕۆکی سەبەتە"""
    conn = sqlite3.connect('mobile_shop.db')
    query = '''
        SELECT p.id, p.name, p.price, p.image_url, c.quantity, 
               (p.price * c.quantity) as total
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.session_id = ?
    '''
    df = pd.read_sql_query(query, conn, params=[session_id])
    conn.close()
    return df

def remove_from_cart(cart_id):
    """سڕینەوەی بەرهەم لە سەبەتە"""
    conn = sqlite3.connect('mobile_shop.db')
    c = conn.cursor()
    c.execute('DELETE FROM cart WHERE id = ?', (cart_id,))
    conn.commit()
    conn.close()

def create_order(name, phone, address, session_id):
    """دروستکردنی داواکاری نوێ"""
    conn = sqlite3.connect('mobile_shop.db')
    c = conn.cursor()
    
    # وەرگرتنی ناوەڕۆکی سەبەتە
    cart_df = get_cart(session_id)
    total = cart_df['total'].sum()
    
    # دروستکردنی داواکاری
    c.execute('''
        INSERT INTO orders (customer_name, phone, address, total_amount)
        VALUES (?, ?, ?, ?)
    ''', (name, phone, address, total))
    
    order_id = c.lastrowid
    
    # زیادکردنی بەرهەمەکان بۆ داواکاری
    for _, item in cart_df.iterrows():
        c.execute('''
            INSERT INTO order_items (order_id, product_id, quantity, price)
            VALUES (?, ?, ?, ?)
        ''', (order_id, item['id'], item['quantity'], item['price']))
        
        # کەمکردنەوەی ستۆک
        c.execute('UPDATE products SET stock = stock - ? WHERE id = ?',
                 (item['quantity'], item['id']))
    
    # سڕینەوەی سەبەتە
    c.execute('DELETE FROM cart WHERE session_id = ?', (session_id,))
    
    conn.commit()
    conn.close()
    return order_id

# ==================== SESSION STATE ====================
if 'session_id' not in st.session_state:
    st.session_state.session_id = hashlib.md5(str(datetime.now()).encode()).hexdigest()[:10]

if 'cart_count' not in st.session_state:
    st.session_state.cart_count = 0

# ==================== HEADER ====================
st.markdown("""
<div class="main-header">
    <h1>📱 دوکانی مۆبایل</h1>
    <h3>نوێترین مۆبایلەکان بە باشترین نرخ</h3>
    <p style="font-size: 1.2rem;">🚚 گەیاندنی خێرا | 💯 کەفالەتی ڕەسەنایەتی | 💰 گەرەنتی باشترین نرخ</p>
</div>
""", unsafe_allow_html=True)

# ==================== NAVIGATION ====================
col1, col2, col3 = st.columns([3, 1, 1])

with col3:
    cart_df = get_cart(st.session_state.session_id)
    cart_count = cart_df['quantity'].sum()
    st.session_state.cart_count = cart_count
    
    if st.button(f"🛒 سەبەتە ({cart_count})", use_container_width=True):
        st.session_state.page = "cart"

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("## 🔍 گەڕان")
    search_term = st.text_input("🔎 ناوی مۆبایل بنووسە...", placeholder="بۆ نموونە: ئایفۆن، سامسونگ...")
    
    st.markdown("## 📂 بەشەکان")
    categories = ["هەموو", "ئایفۆن", "سامسونگ", "شیاومی", "گوگڵ", "وەن پڵەس", "هواوی"]
    
    if 'selected_category' not in st.session_state:
        st.session_state.selected_category = "هەموو"
    
    for cat in categories:
        if st.button(cat, use_container_width=True, 
                    type="primary" if st.session_state.selected_category == cat else "secondary"):
            st.session_state.selected_category = cat
            st.rerun()
    
    st.markdown("---")
    st.markdown("## ⚙️ ڕێکخستنەکان")
    sort_by = st.selectbox("ڕیزکردن بەپێی:", ["نرخ (کەم بۆ زۆر)", "نرخ (زۆر بۆ کەم)", "ناو"])
    
    st.markdown("---")
    st.markdown("""
    ### 📞 پەیوەندیمان پێوەبکە
    - 📱 0770-123-4567
    - 📧 info@mobileshop.com
    - 📍 سلێمانی، شەقامی سالم
    """)

# ==================== MAIN CONTENT ====================
# هەڵگرتنی پەیج
if 'page' not in st.session_state:
    st.session_state.page = "home"

if st.session_state.page == "home":
    # وەرگرتنی بەرهەمەکان
    products_df = get_products(
        category=None if st.session_state.selected_category == "هەموو" else st.session_state.selected_category,
        search=search_term if search_term else None
    )
    
    # ڕیزکردن
    if sort_by == "نرخ (کەم بۆ زۆر)":
        products_df = products_df.sort_values('price', ascending=True)
    elif sort_by == "نرخ (زۆر بۆ کەم)":
        products_df = products_df.sort_values('price', ascending=False)
    
    if len(products_df) == 0:
        st.warning("⚠️ هیچ بەرهەمێک نەدۆزرایەوە!")
    else:
        # نمایشکردنی بەرهەمەکان لە گرید
        cols = st.columns(3)
        
        for idx, (_, product) in enumerate(products_df.iterrows()):
            with cols[idx % 3]:
                st.markdown(f"""
                <div class="product-card">
                    <h3>{product['name']}</h3>
                    <p style="color: #666;">{product['brand']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # وێنەی بەرهەم
                try:
                    st.image(product['image_url'], use_column_width=True)
                except:
                    st.image("https://via.placeholder.com/300x300?text=No+Image", use_column_width=True)
                
                # نرخ
                col_price1, col_price2 = st.columns(2)
                with col_price1:
                    if product['old_price'] and product['old_price'] > product['price']:
                        st.markdown(f'<p class="old-price">{product["old_price"]:,.0f} د.ع</p>', 
                                  unsafe_allow_html=True)
                with col_price2:
                    if product['old_price'] and product['old_price'] > product['price']:
                        discount = int((1 - product['price']/product['old_price']) * 100)
                        st.markdown(f'<span class="discount-badge">-{discount}%</span>', 
                                  unsafe_allow_html=True)
                
                st.markdown(f'<p class="price-tag">{product["price"]:,.0f} د.ع</p>', 
                          unsafe_allow_html=True)
                
                # تایبەتمەندییەکان
                with st.expander("📋 تایبەتمەندییەکان"):
                    try:
                        specs = eval(product['specs'])
                        for key, value in specs.items():
                            st.write(f"**{key}:** {value}")
                    except:
                        st.write(product['description'])
                
                # دوگمەی زیادکردن بۆ سەبەتە
                if product['stock'] > 0:
                    if st.button(f"🛒 زیادکردن بۆ سەبەتە", key=f"add_{product['id']}", use_container_width=True):
                        add_to_cart(product['id'], st.session_state.session_id)
                        st.success(f"✅ {product['name']} زیادکرا بۆ سەبەتە!")
                        st.rerun()
                else:
                    st.error("❌ تەواو بووە!")

elif st.session_state.page == "cart":
    st.markdown("<h2>🛒 سەبەتەی کڕین</h2>", unsafe_allow_html=True)
    
    cart_df = get_cart(st.session_state.session_id)
    
    if len(cart_df) == 0:
        st.info("🛒 سەبەتەکەت بەتاڵە!")
        if st.button("🔙 بگەڕێوە بۆ دوکان", type="primary"):
            st.session_state.page = "home"
            st.rerun()
    else:
        # نمایشکردنی بەرهەمەکانی سەبەتە
        for _, item in cart_df.iterrows():
            with st.container():
                col1, col2, col3, col4 = st.columns([1, 2, 1, 1])
                
                with col1:
                    try:
                        st.image(item['image_url'], width=100)
                    except:
                        st.image("https://via.placeholder.com/100x100?text=No+Image", width=100)
                
                with col2:
                    st.markdown(f"### {item['name']}")
                    st.write(f"بڕ: {item['quantity']}")
                
                with col3:
                    st.markdown(f"<p class='price-tag'>{item['total']:,.0f} د.ع</p>", 
                              unsafe_allow_html=True)
                
                with col4:
                    if st.button("🗑️", key=f"remove_{item['id']}"):
                        remove_from_cart(item['id'])
                        st.rerun()
        
        # کۆی گشتی
        total_amount = cart_df['total'].sum()
        st.markdown(f"""
        <div class="total-section">
            <h2>💰 کۆی گشتی: {total_amount:,.0f} دیناری عێراقی</h2>
            <p>{len(cart_df)} بەرهەم</p>
        </div>
        """, unsafe_allow_html=True)
        
        # فۆرمی داواکاری
        st.markdown("### 📝 زانیاری داواکاری")
        
        with st.form("order_form"):
            col1, col2 = st.columns(2)
            with col1:
                customer_name = st.text_input("👤 ناوی تەواو", placeholder="ناوی خۆت بنووسە")
                phone = st.text_input("📱 ژمارەی تەلەفۆن", placeholder="0770-XXX-XXXX")
            with col2:
                address = st.text_area("📍 ناونیشان", placeholder="ناونیشانی تەواوت بنووسە")
                city = st.selectbox("🏙️ شار", ["سلێمانی", "هەولێر", "دهۆک", "کەرکوک", "بەغداد"])
            
            submitted = st.form_submit_button("📦 تەواوکردنی داواکاری", type="primary", use_container_width=True)
            
            if submitted:
                if customer_name and phone and address:
                    full_address = f"{address}, {city}"
                    order_id = create_order(customer_name, phone, full_address, st.session_state.session_id)
                    st.success(f"""
                    ✅ داواکاریت بە سەرکەوتوویی تۆمارکرا!
                    
                    ژمارەی داواکاری: #{order_id}
                    بڕی پارە: {total_amount:,.0f} د.ع
                    
                    📞 پەیوەندیت پێوە دەکەین بۆ پشتڕاستکردنەوە.
                    """)
                    st.balloons()
                else:
                    st.error("⚠️ تکایە هەموو زانیارییەکان پڕبکەرەوە!")
        
        if st.button("🔙 بەردەوامبوون لە کڕین"):
            st.session_state.page = "home"
            st.rerun()

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px; color: #666;">
    <p>© 2024 دوکانی مۆبایل. هەموو مافەکان پارێزراون.</p>
    <p>دروستکراوە بە ❤️ لە کوردستان</p>
</div>
""", unsafe_allow_html=True)
