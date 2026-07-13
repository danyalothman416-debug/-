import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time
import json
import qrcode
from io import BytesIO
import base64
from fpdf import FPDF
import random
import string
import hashlib
import sqlite3
from contextlib import contextmanager
import calendar
from dateutil.relativedelta import relativedelta
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io

# ======================== CONFIGURATION ========================
st.set_page_config(
    page_title="کاشێری زیرەکی پێشکەوتوو | Smart Cashier Pro",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ======================== DATABASE SETUP ========================
@contextmanager
def get_db():
    conn = sqlite3.connect('smart_cashier.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_database():
    with get_db() as conn:
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'cashier',
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                icon TEXT,
                color TEXT,
                parent_id INTEGER,
                FOREIGN KEY (parent_id) REFERENCES categories(id)
            );
            
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                barcode TEXT UNIQUE,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                cost_price REAL,
                stock INTEGER DEFAULT 0,
                min_stock INTEGER DEFAULT 10,
                category_id INTEGER,
                unit TEXT DEFAULT 'دانە',
                tax_rate REAL DEFAULT 0,
                discount_allowed BOOLEAN DEFAULT 1,
                is_active BOOLEAN DEFAULT 1,
                image BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories(id)
            );
            
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                address TEXT,
                loyalty_points INTEGER DEFAULT 0,
                total_purchases REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT UNIQUE NOT NULL,
                customer_id INTEGER,
                user_id INTEGER NOT NULL,
                subtotal REAL NOT NULL,
                discount_amount REAL DEFAULT 0,
                tax_amount REAL DEFAULT 0,
                total_amount REAL NOT NULL,
                payment_method TEXT NOT NULL,
                payment_status TEXT DEFAULT 'completed',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            
            CREATE TABLE IF NOT EXISTS sale_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                discount REAL DEFAULT 0,
                total REAL NOT NULL,
                FOREIGN KEY (sale_id) REFERENCES sales(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            );
            
            CREATE TABLE IF NOT EXISTS stock_movements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                movement_type TEXT NOT NULL,
                reference_type TEXT,
                reference_id INTEGER,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(id)
            );
            
            CREATE TABLE IF NOT EXISTS discounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                description TEXT,
                discount_type TEXT NOT NULL,
                value REAL NOT NULL,
                min_purchase REAL,
                max_discount REAL,
                start_date TIMESTAMP,
                end_date TIMESTAMP,
                usage_limit INTEGER,
                used_count INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1
            );
            
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        
        # Insert default data if not exists
        cursor = conn.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            # Create admin user (password: admin123)
            admin_hash = hashlib.sha256("admin123".encode()).hexdigest()
            conn.execute(
                "INSERT INTO users (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)",
                ("admin", admin_hash, "بەڕێوەبەری سیستم", "admin")
            )
            # Create cashier user (password: cashier123)
            cashier_hash = hashlib.sha256("cashier123".encode()).hexdigest()
            conn.execute(
                "INSERT INTO users (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)",
                ("cashier", cashier_hash, "کاشێر", "cashier")
            )
        
        cursor = conn.execute("SELECT COUNT(*) FROM categories")
        if cursor.fetchone()[0] == 0:
            categories = [
                ("خۆراک", "🍚", "#FF6B6B", None),
                ("خواردنەوە", "🥤", "#4ECDC4", None),
                ("میوە و سەوزە", "🥬", "#45B7D1", None),
                ("پاککەرەوە", "🧹", "#96CEB4", None),
                ("شیرینی", "🍬", "#FFEAA7", None),
                ("جگەرە", "🚬", "#DDA0DD", None),
            ]
            conn.executemany(
                "INSERT INTO categories (name, icon, color, parent_id) VALUES (?, ?, ?, ?)",
                categories
            )
        
        conn.commit()

# ======================== AUTHENTICATION ========================
def login_user(username, password):
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    with get_db() as conn:
        user = conn.execute(
            "SELECT * FROM users WHERE username = ? AND password_hash = ? AND is_active = 1",
            (username, password_hash)
        ).fetchone()
        if user:
            conn.execute(
                "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
                (user['id'],)
            )
            conn.commit()
            return dict(user)
    return None

def check_permission(required_role):
    if 'user' not in st.session_state:
        return False
    user_role = st.session_state.user['role']
    role_hierarchy = {'admin': 3, 'manager': 2, 'cashier': 1}
    return role_hierarchy.get(user_role, 0) >= role_hierarchy.get(required_role, 0)

# ======================== UTILITY FUNCTIONS ========================
def generate_invoice_number():
    with get_db() as conn:
        count = conn.execute("SELECT COUNT(*) FROM sales WHERE date(created_at) = date('now', 'localtime')").fetchone()[0]
        return f"INV-{datetime.now().strftime('%Y%m%d')}-{count+1:04d}"

def generate_barcode():
    return ''.join(random.choices(string.digits, k=12))

def calculate_discount(code, subtotal):
    with get_db() as conn:
        discount = conn.execute(
            """SELECT * FROM discounts 
               WHERE code = ? AND is_active = 1 
               AND (start_date IS NULL OR start_date <= datetime('now', 'localtime'))
               AND (end_date IS NULL OR end_date >= datetime('now', 'localtime'))
               AND (usage_limit IS NULL OR used_count < usage_limit)""",
            (code,)
        ).fetchone()
        
        if not discount:
            return 0, "کۆدی داشکان نادروستە یان بەسەرچووە"
        
        if discount['min_purchase'] and subtotal < discount['min_purchase']:
            return 0, f"کڕینی کەمە. پێویستە لانیکەم {discount['min_purchase']:,.0f} دینار بێت"
        
        if discount['discount_type'] == 'percentage':
            amount = subtotal * (discount['value'] / 100)
            if discount['max_discount']:
                amount = min(amount, discount['max_discount'])
        else:  # fixed
            amount = discount['value']
        
        return amount, None

def get_low_stock_products():
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM products WHERE stock <= min_stock AND is_active = 1"
        ).fetchall()

def format_currency(amount):
    return f"{amount:,.0f} دینار"

def create_qr_code(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img

def generate_pdf_invoice(sale_data):
    pdf = FPDF()
    pdf.add_page()
    
    # Add Unicode font (you need to have a Kurdish-supporting font)
    # pdf.add_font('Kurdish', '', 'path/to/kurdish/font.ttf', uni=True)
    
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="کاشێری زیرەک - پسوڵەی فرۆشتن", ln=True, align='C')
    pdf.cell(200, 10, txt=f"ژمارەی پسوڵە: {sale_data['invoice_number']}", ln=True)
    pdf.cell(200, 10, txt=f"بەروار: {sale_data['created_at']}", ln=True)
    
    # Add items
    pdf.cell(200, 10, txt="="*50, ln=True)
    for item in sale_data['items']:
        pdf.cell(200, 10, txt=f"{item['name']} x {item['quantity']} = {item['total']:,.0f}", ln=True)
    
    pdf.cell(200, 10, txt="="*50, ln=True)
    pdf.cell(200, 10, txt=f"کۆی گشتی: {sale_data['total_amount']:,.0f} دینار", ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

# ======================== CUSTOM CSS ========================
def load_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@300;400;500;600;700&family=Cairo:wght@400;600;700&display=swap');
        
        * {
            font-family: 'Cairo', 'Rajdhani', sans-serif;
            direction: rtl;
        }
        
        /* Main Container */
        .main {
            padding: 0 !important;
        }
        
        /* Header */
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 15px 30px;
            color: white;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            position: sticky;
            top: 0;
            z-index: 1000;
        }
        
        .header-title {
            font-size: 24px;
            font-weight: 700;
        }
        
        .header-user {
            background: rgba(255,255,255,0.2);
            padding: 8px 15px;
            border-radius: 20px;
        }
        
        /* Product Grid */
        .product-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
            padding: 10px;
        }
        
        .product-card {
            background: white;
            border-radius: 15px;
            padding: 15px;
            cursor: pointer;
            transition: all 0.3s ease;
            border: 2px solid transparent;
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
            position: relative;
            overflow: hidden;
        }
        
        .product-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            border-color: #667eea;
        }
        
        .product-card.low-stock {
            border-color: #ff6b6b;
        }
        
        .product-card .stock-badge {
            position: absolute;
            top: 10px;
            left: 10px;
            background: #ff6b6b;
            color: white;
            padding: 3px 8px;
            border-radius: 10px;
            font-size: 12px;
        }
        
        /* Cart */
        .cart-container {
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 3px 15px rgba(0,0,0,0.1);
        }
        
        .cart-item {
            padding: 10px;
            border-bottom: 1px solid #eee;
            transition: background 0.3s;
        }
        
        .cart-item:hover {
            background: #f8f9fa;
        }
        
        /* Buttons */
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 25px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            width: 100%;
        }
        
        .btn-primary:hover {
            transform: scale(1.02);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .btn-danger {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 25px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        /* Stats Cards */
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 3px 15px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
        }
        
        .stat-value {
            font-size: 32px;
            font-weight: 700;
            color: #667eea;
        }
        
        .stat-label {
            color: #666;
            font-size: 14px;
        }
        
        /* Payment Modal */
        .payment-methods {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
        }
        
        .payment-method {
            padding: 20px;
            border: 2px solid #eee;
            border-radius: 15px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .payment-method:hover {
            border-color: #667eea;
            background: #f8f9fa;
        }
        
        .payment-method.selected {
            border-color: #667eea;
            background: rgba(102, 126, 234, 0.1);
        }
        
        /* Animations */
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        .slide-in {
            animation: slideIn 0.3s ease-out;
        }
        
        .fade-in {
            animation: fadeIn 0.5s ease-out;
        }
        </style>
    """, unsafe_allow_html=True)

# ======================== SESSION STATE ========================
def init_session_state():
    if 'cart' not in st.session_state:
        st.session_state.cart = []
    if 'payment_method' not in st.session_state:
        st.session_state.payment_method = 'cash'
    if 'discount_code' not in st.session_state:
        st.session_state.discount_code = None
    if 'discount_amount' not in st.session_state:
        st.session_state.discount_amount = 0
    if 'customer' not in st.session_state:
        st.session_state.customer = None
    if 'selected_category' not in st.session_state:
        st.session_state.selected_category = 'هەموو'

# ======================== MAIN APPLICATION ========================
def main():
    init_database()
    load_css()
    
    # Login Page
    if 'user' not in st.session_state:
        show_login_page()
        return
    
    init_session_state()
    
    # Main Interface
    st.markdown(f"""
        <div class="header">
            <div class="header-title">🛒 کاشێری زیرەک</div>
            <div class="header-user">
                {st.session_state.user['full_name']} | 
                {st.session_state.user['role']}
                <button onclick="logout()" style="margin-right:10px;">🚪</button>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Sidebar Navigation
    with st.sidebar:
        st.markdown("### 📱 مینوی سەرەکی")
        
        menu_options = {
            "🛒 فرۆشتن": "pos",
            "📦 بەرهەمەکان": "products",
            "👥 کڕیاران": "customers",
            "📊 ڕاپۆرتەکان": "reports",
            "⚙️ ڕێکخستنەکان": "settings"
        }
        
        if st.session_state.user['role'] == 'admin':
            menu_options["👨‍💼 بەڕێوەبەرایەتی"] = "admin"
        
        selected_menu = st.radio("", list(menu_options.keys()), label_visibility="collapsed")
        current_page = menu_options[selected_menu]
        
        # Quick Stats in Sidebar
        st.markdown("---")
        with get_db() as conn:
            today_sales = conn.execute(
                "SELECT COALESCE(SUM(total_amount), 0) FROM sales WHERE date(created_at) = date('now', 'localtime')"
            ).fetchone()[0]
            today_orders = conn.execute(
                "SELECT COUNT(*) FROM sales WHERE date(created_at) = date('now', 'localtime')"
            ).fetchone()[0]
            low_stock = conn.execute(
                "SELECT COUNT(*) FROM products WHERE stock <= min_stock AND is_active = 1"
            ).fetchone()[0]
        
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{format_currency(today_sales)}</div>
                <div class="stat-label">فرۆشتنی ئەمڕۆ</div>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("ژمارەی کڕین", today_orders)
        with col2:
            st.metric("کۆگای کەم", low_stock, delta_color="inverse")
    
    # Page Router
    if current_page == "pos":
        show_pos_page()
    elif current_page == "products":
        show_products_page()
    elif current_page == "customers":
        show_customers_page()
    elif current_page == "reports":
        show_reports_page()
    elif current_page == "settings":
        show_settings_page()
    elif current_page == "admin":
        show_admin_page()

def show_login_page():
    st.markdown("""
        <div style="display: flex; justify-content: center; align-items: center; height: 100vh;">
            <div style="text-align: center;">
                <h1 style="font-size: 48px; color: #667eea;">🛒</h1>
                <h1>کاشێری زیرەک</h1>
                <p style="color: #666;">تکایە بچۆ ژوورەوە بۆ بەردەوامبوون</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form"):
            username = st.text_input("👤 ناوی بەکارهێنەر", placeholder="admin")
            password = st.text_input("🔒 وشەی نهێنی", type="password", placeholder="admin123")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                login_btn = st.form_submit_button("🚪 چوونە ژوورەوە", use_container_width=True)
            with col_btn2:
                st.info("پێشفرض: admin / admin123")
            
            if login_btn:
                user = login_user(username, password)
                if user:
                    st.session_state.user = user
                    st.success("بە سەرکەوتوویی چوویتە ژوورەوە!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("ناوی بەکارهێنەر یان وشەی نهێنی هەڵەیە!")

# ======================== POS PAGE ========================
def show_pos_page():
    # Quick actions bar
    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
    
    with col1:
        search_term = st.text_input("🔍", placeholder="گەڕان بە ناو یان بارکۆد...", label_visibility="collapsed")
    with col2:
        if st.button("📷 سکان", use_container_width=True):
            st.info("کامێرا چالاکە (دیمۆ)")
    with col3:
        if st.button("👤 کڕیار", use_container_width=True):
            st.session_state.show_customer_select = not st.session_state.get('show_customer_select', False)
    with col4:
        if st.button("🏷️ داشکان", use_container_width=True):
            st.session_state.show_discount = not st.session_state.get('show_discount', False)
    with col5:
        if st.button("🔄 نوێکردنەوە", use_container_width=True):
            st.rerun()
    
    # Customer Selection Modal
    if st.session_state.get('show_customer_select', False):
        with st.expander("👥 هەڵبژاردنی کڕیار", expanded=True):
            with get_db() as conn:
                customers = conn.execute("SELECT * FROM customers WHERE 1=1 ORDER BY name").fetchall()
            
            customer_options = {"هیچ": None}
            for c in customers:
                customer_options[f"{c['name']} - {c['phone'] or 'بێ تەلەفۆن'}"] = c['id']
            
            selected = st.selectbox("کڕیار هەڵبژێرە", list(customer_options.keys()))
            if selected != "هیچ":
                st.session_state.customer = customer_options[selected]
            else:
                st.session_state.customer = None
    
    # Discount Modal
    if st.session_state.get('show_discount', False):
        with st.expander("🏷️ داشکان", expanded=True):
            discount_code = st.text_input("کۆدی داشکان بنووسە", placeholder="SALE2024")
            if discount_code:
                subtotal = sum(item['total'] for item in st.session_state.cart)
                discount_amount, error = calculate_discount(discount_code, subtotal)
                if error:
                    st.error(error)
                else:
                    st.session_state.discount_code = discount_code
                    st.session_state.discount_amount = discount_amount
                    st.success(f"داشکانی {format_currency(discount_amount)} زیادکرا!")
    
    # Main POS Layout
    col_products, col_cart = st.columns([3, 2])
    
    with col_products:
        st.markdown("### 📦 بەرهەمەکان")
        
        # Category Filter
        with get_db() as conn:
            categories = conn.execute("SELECT * FROM categories ORDER BY name").fetchall()
        
        cat_cols = st.columns(len(categories) + 1)
        with cat_cols[0]:
            if st.button("🎯 هەموو", use_container_width=True, 
                        type="primary" if st.session_state.selected_category == 'هەموو' else "secondary"):
                st.session_state.selected_category = 'هەموو'
                st.rerun()
        
        for idx, cat in enumerate(categories):
            with cat_cols[idx + 1]:
                if st.button(f"{cat['icon']} {cat['name']}", use_container_width=True,
                           type="primary" if st.session_state.selected_category == cat['name'] else "secondary"):
                    st.session_state.selected_category = cat['name']
                    st.rerun()
        
        # Products Grid
        with get_db() as conn:
            query = "SELECT p.*, c.name as category_name, c.icon as category_icon FROM products p LEFT JOIN categories c ON p.category_id = c.id WHERE p.is_active = 1"
            
            if st.session_state.selected_category != 'هەموو':
                query += f" AND c.name = '{st.session_state.selected_category}'"
            
            if search_term:
                query += f" AND (p.name LIKE '%{search_term}%' OR p.barcode LIKE '%{search_term}%')"
            
            products = conn.execute(query).fetchall()
        
        if not products:
            st.info("هیچ بەرهەمێک نەدۆزرایەوە")
        else:
            # Display in grid
            cols = st.columns(4)
            for idx, product in enumerate(products):
                with cols[idx % 4]:
                    low_stock = product['stock'] <= product['min_stock']
                    
                    st.markdown(f"""
                        <div class="product-card {'low-stock' if low_stock else ''}">
                            <div style="text-align: center;">
                                <div style="font-size: 40px;">{product.get('category_icon', '📦')}</div>
                                <h4>{product['name']}</h4>
                                <p style="color: #667eea; font-size: 18px; font-weight: bold;">
                                    {format_currency(product['price'])}
                                </p>
                                <p style="color: {'red' if low_stock else 'green'}; font-size: 12px;">
                                    📦 کۆگا: {product['stock']}
                                </p>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    col_qty, col_add = st.columns([1, 2])
                    with col_qty:
                        qty = st.number_input("دانە", 1, product['stock'], 1, 
                                            key=f"qty_{product['id']}", label_visibility="collapsed")
                    with col_add:
                        if st.button("➕", key=f"add_{product['id']}", use_container_width=True):
                            add_to_cart(product, qty)
                            st.rerun()
    
    with col_cart:
        st.markdown("### 🛒 سەبەتەی کڕین")
        show_cart()

def add_to_cart(product, quantity):
    """Add product to cart"""
    existing = [i for i, item in enumerate(st.session_state.cart) if item['id'] == product['id']]
    
    if existing:
        st.session_state.cart[existing[0]]['quantity'] += quantity
        st.session_state.cart[existing[0]]['total'] = (
            st.session_state.cart[existing[0]]['price'] * 
            st.session_state.cart[existing[0]]['quantity']
        )
    else:
        st.session_state.cart.append({
            'id': product['id'],
            'name': product['name'],
            'price': product['price'],
            'quantity': quantity,
            'total': product['price'] * quantity,
            'barcode': product.get('barcode')
        })
    
    # Update stock in database
    with get_db() as conn:
        conn.execute(
            "UPDATE products SET stock = stock - ? WHERE id = ?",
            (quantity, product['id'])
        )
        conn.execute(
            """INSERT INTO stock_movements (product_id, quantity, movement_type, reference_type, notes)
               VALUES (?, ?, 'sale', 'cart', 'زیادکرا بە سەبەتە')""",
            (product['id'], -quantity)
        )
        conn.commit()

def show_cart():
    """Display shopping cart"""
    if not st.session_state.cart:
        st.info("🛒 سەبەتەکەت بەتاڵە")
        return
    
    # Cart items
    subtotal = 0
    for idx, item in enumerate(st.session_state.cart):
        with st.container():
            col_name, col_qty, col_price, col_total, col_action = st.columns([3, 1, 1, 1, 1])
            
            with col_name:
                st.write(f"**{item['name']}**")
            with col_qty:
                new_qty = st.number_input("", 1, 999, item['quantity'], 
                                        key=f"cart_qty_{idx}", label_visibility="collapsed")
                if new_qty != item['quantity']:
                    difference = new_qty - item['quantity']
                    item['quantity'] = new_qty
                    item['total'] = item['price'] * new_qty
                    
                    # Update stock
                    with get_db() as conn:
                        conn.execute(
                            "UPDATE products SET stock = stock - ? WHERE id = ?",
                            (difference, item['id'])
                        )
                        conn.commit()
            with col_price:
                st.write(format_currency(item['price']))
            with col_total:
                st.write(f"**{format_currency(item['total'])}**")
            with col_action:
                if st.button("🗑️", key=f"del_{idx}"):
                    # Return to stock
                    with get_db() as conn:
                        conn.execute(
                            "UPDATE products SET stock = stock + ? WHERE id = ?",
                            (item['quantity'], item['id'])
                        )
                        conn.commit()
                    st.session_state.cart.pop(idx)
                    st.rerun()
            
            subtotal += item['total']
            st.markdown("<hr style='margin:5px 0'>", unsafe_allow_html=True)
    
    # Cart Summary
    st.markdown("---")
    
    discount_amount = st.session_state.discount_amount
    tax_rate = 0  # Can be configured
    tax_amount = (subtotal - discount_amount) * tax_rate
    total = subtotal - discount_amount + tax_amount
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("کۆی خاو:")
        if discount_amount > 0:
            st.write("داشکان:")
        if tax_amount > 0:
            st.write("باج:")
        st.write("### کۆی گشتی:")
    with col2:
        st.write(format_currency(subtotal))
        if discount_amount > 0:
            st.write(f"-{format_currency(discount_amount)}")
        if tax_amount > 0:
            st.write(format_currency(tax_amount))
        st.write(f"### {format_currency(total)}")
    
    # Payment Methods
    st.markdown("---")
    st.markdown("#### 💳 شێوازی پارەدان")
    
    payment_methods = {
        "cash": "💵 نەقد",
        "card": "💳 کارت",
        "mobile": "📱 مۆبایل",
        "credit": "📋 قەرز"
    }
    
    cols = st.columns(4)
    for idx, (method, label) in enumerate(payment_methods.items()):
        with cols[idx]:
            if st.button(label, key=f"pay_{method}", 
                        use_container_width=True,
                        type="primary" if st.session_state.payment_method == method else "secondary"):
                st.session_state.payment_method = method
    
    # Checkout Button
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("💳 پارەدان و تەواوکردن", type="primary", use_container_width=True):
        process_sale(total, discount_amount, tax_amount)
    
    # Clear Cart
    if st.button("🗑️ بەتاڵکردنەوەی سەبەتە", use_container_width=True):
        # Return all items to stock
        for item in st.session_state.cart:
            with get_db() as conn:
                conn.execute(
                    "UPDATE products SET stock = stock + ? WHERE id = ?",
                    (item['quantity'], item['id'])
                )
                conn.commit()
        st.session_state.cart = []
        st.session_state.discount_code = None
        st.session_state.discount_amount = 0
        st.rerun()

def process_sale(total, discount, tax):
    """Process the sale and save to database"""
    try:
        with get_db() as conn:
            # Generate invoice number
            invoice_number = generate_invoice_number()
            
            # Create sale record
            cursor = conn.execute(
                """INSERT INTO sales 
                   (invoice_number, customer_id, user_id, subtotal, discount_amount, tax_amount, total_amount, payment_method)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (invoice_number, st.session_state.customer, st.session_state.user['id'],
                 sum(item['total'] for item in st.session_state.cart),
                 discount, tax, total, st.session_state.payment_method)
            )
            sale_id = cursor.lastrowid
            
            # Create sale items
            for item in st.session_state.cart:
                conn.execute(
                    """INSERT INTO sale_items (sale_id, product_id, quantity, unit_price, discount, total)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (sale_id, item['id'], item['quantity'], item['price'], 0, item['total'])
                )
                
                # Record stock movement
                conn.execute(
                    """INSERT INTO stock_movements (product_id, quantity, movement_type, reference_type, reference_id)
                       VALUES (?, ?, 'sale', 'sale', ?)""",
                    (item['id'], -item['quantity'], sale_id)
                )
            
            # Update discount usage
            if st.session_state.discount_code:
                conn.execute(
                    "UPDATE discounts SET used_count = used_count + 1 WHERE code = ?",
                    (st.session_state.discount_code,)
                )
            
            # Update customer points if applicable
            if st.session_state.customer:
                points_earned = int(total / 1000)  # 1 point per 1000 IQD
                conn.execute(
                    """UPDATE customers 
                       SET loyalty_points = loyalty_points + ?, total_purchases = total_purchases + ?
                       WHERE id = ?""",
                    (points_earned, total, st.session_state.customer)
                )
            
            conn.commit()
        
        # Generate invoice PDF
        sale_data = {
            'invoice_number': invoice_number,
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'items': st.session_state.cart,
            'total_amount': total
        }
        pdf_bytes = generate_pdf_invoice(sale_data)
        
        # Show success and download button
        st.success(f"🎉 فرۆشتن بە سەرکەوتوویی تەواو بوو! ژمارەی پسوڵە: {invoice_number}")
        st.download_button(
            "📥 دابەزاندنی پسوڵە",
            pdf_bytes,
            f"invoice_{invoice_number}.pdf",
            "application/pdf"
        )
        
        # Clear cart
        st.session_state.cart = []
        st.session_state.discount_code = None
        st.session_state.discount_amount = 0
        st.session_state.customer = None
        
        time.sleep(2)
        st.rerun()
        
    except Exception as e:
        st.error(f"هەڵەیەک ڕوویدا: {str(e)}")
        # Rollback stock
        for item in st.session_state.cart:
            with get_db() as conn:
                conn.execute(
                    "UPDATE products SET stock = stock + ? WHERE id = ?",
                    (item['quantity'], item['id'])
                )
                conn.commit()

# ======================== PRODUCTS PAGE ========================
def show_products_page():
    st.markdown("### 📦 بەڕێوەبردنی بەرهەمەکان")
    
    tab1, tab2, tab3 = st.tabs(["📋 لیستی بەرهەمەکان", "➕ زیادکردن", "📊 هەناردەکردن"])
    
    with tab1:
        with get_db() as conn:
            products = conn.execute("""
                SELECT p.*, c.name as category_name 
                FROM products p 
                LEFT JOIN categories c ON p.category_id = c.id 
                ORDER BY p.name
            """).fetchall()
        
        if products:
            df = pd.DataFrame(products, columns=['id', 'barcode', 'name', 'description', 'price', 
                                                  'cost_price', 'stock', 'min_stock', 'category_id',
                                                  'unit', 'tax_rate', 'discount_allowed', 'is_active',
                                                  'image', 'created_at', 'updated_at', 'category_name'])
            
            # Search and filter
            col1, col2, col3 = st.columns(3)
            with col1:
                search = st.text_input("🔍 گەڕان", placeholder="ناو یان بارکۆد...")
            with col2:
                category_filter = st.selectbox("📂 پۆلێن", ["هەموو"] + [c['name'] for c in conn.execute("SELECT name FROM categories").fetchall()])
            with col3:
                stock_filter = st.selectbox("📦 کۆگا", ["هەموو", "کەم", "بەردەست", "تەواو بوو"])
            
            # Apply filters
            if search:
                df = df[df['name'].str.contains(search, case=False) | df['barcode'].str.contains(search, case=False)]
            if category_filter != "هەموو":
                df = df[df['category_name'] == category_filter]
            if stock_filter == "کەم":
                df = df[df['stock'] <= df['min_stock']]
            elif stock_filter == "بەردەست":
                df = df[df['stock'] > df['min_stock']]
            elif stock_filter == "تەواو بوو":
                df = df[df['stock'] == 0]
            
            # Display editable table
            edited_df = st.data_editor(
                df,
                column_config={
                    "id": st.column_config.NumberColumn("ID", disabled=True),
                    "name": st.column_config.TextColumn("ناوی بەرهەم", required=True),
                    "price": st.column_config.NumberColumn("نرخی فرۆشتن", format="%d دینار"),
                    "stock": st.column_config.NumberColumn("کۆگا"),
                    "min_stock": st.column_config.NumberColumn("کەمترین کۆگا"),
                },
                hide_index=True,
                use_container_width=True,
                num_rows="dynamic"
            )
            
            if st.button("💾 پاشەکەوتکردنی گۆڕانکارییەکان"):
                # Update database
                st.success("گۆڕانکارییەکان پاشەکەوت کران!")
    
    with tab2:
        with st.form("add_product_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("ناوی بەرهەم *", placeholder="نان")
                barcode = st.text_input("بارکۆد", placeholder=generate_barcode())
                price = st.number_input("نرخی فرۆشتن *", min_value=0, step=100)
                cost_price = st.number_input("نرخی کڕین", min_value=0, step=100)
                stock = st.number_input("دانە", min_value=0, value=10)
            
            with col2:
                with get_db() as conn:
                    categories = conn.execute("SELECT id, name FROM categories").fetchall()
                category = st.selectbox("پۆلێن", [c['name'] for c in categories])
                min_stock = st.number_input("کەمترین کۆگا", min_value=0, value=10)
                unit = st.selectbox("یەکە", ["دانە", "کەرت", "کیلۆ", "لیتر", "پاکەت"])
                tax_rate = st.number_input("ڕێژەی باج (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.5)
            
            description = st.text_area("وەسف", placeholder="وەسفی بەرهەم...")
            
            if st.form_submit_button("➕ زیادکردنی بەرهەم"):
                if name and price > 0:
                    with get_db() as conn:
                        cat_id = next((c['id'] for c in categories if c['name'] == category), None)
                        conn.execute(
                            """INSERT INTO products (barcode, name, description, price, cost_price, 
                               stock, min_stock, category_id, unit, tax_rate)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                            (barcode, name, description, price, cost_price, stock, min_stock, cat_id, unit, tax_rate)
                        )
                        conn.commit()
                    st.success(f"بەرهەمی {name} بە سەرکەوتوویی زیادکرا!")
                    st.rerun()
                else:
                    st.error("تکایە ناو و نرخی بەرهەم پڕبکەرەوە")

# ======================== REPORTS PAGE ========================
def show_reports_page():
    st.markdown("### 📊 ڕاپۆرت و ئامارەکان")
    
    # Date range selector
    col1, col2, col3 = st.columns(3)
    with col1:
        date_from = st.date_input("لە", datetime.now() - timedelta(days=30))
    with col2:
        date_to = st.date_input("بۆ", datetime.now())
    with col3:
        report_type = st.selectbox("جۆری ڕاپۆرت", 
                                   ["فرۆشتن", "بەرهەمەکان", "کڕیاران", "قازانج"])
    
    # Dashboard
    with get_db() as conn:
        # Sales statistics
        sales_stats = conn.execute("""
            SELECT 
                COUNT(*) as total_orders,
                COALESCE(SUM(total_amount), 0) as total_sales,
                COALESCE(AVG(total_amount), 0) as avg_order,
                COALESCE(SUM(discount_amount), 0) as total_discounts
            FROM sales 
            WHERE date(created_at) BETWEEN ? AND ?
        """, (date_from, date_to)).fetchone()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("کۆی فرۆشتن", format_currency(sales_stats['total_sales']))
    with col2:
        st.metric("ژمارەی کڕین", sales_stats['total_orders'])
    with col3:
        st.metric("مامناوەندی کڕین", format_currency(sales_stats['avg_order']))
    with col4:
        st.metric("کۆی داشکان", format_currency(sales_stats['total_discounts']))
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📈 فرۆشتنی ڕۆژانە")
        with get_db() as conn:
            daily_sales = conn.execute("""
                SELECT date(created_at) as date, SUM(total_amount) as total
                FROM sales
                WHERE date(created_at) BETWEEN ? AND ?
                GROUP BY date(created_at)
                ORDER BY date(created_at)
            """, (date_from, date_to)).fetchall()
        
        if daily_sales:
            df = pd.DataFrame(daily_sales)
            fig = px.line(df, x='date', y='total', title="ڕێژەی فرۆشتنی ڕۆژانە")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 🏆 پڕفرۆشترین بەرهەمەکان")
        with get_db() as conn:
            top_products = conn.execute("""
                SELECT p.name, SUM(si.quantity) as total_qty, SUM(si.total) as total_sales
                FROM sale_items si
                JOIN products p ON si.product_id = p.id
                JOIN sales s ON si.sale_id = s.id
                WHERE date(s.created_at) BETWEEN ? AND ?
                GROUP BY p.name
                ORDER BY total_sales DESC
                LIMIT 10
            """, (date_from, date_to)).fetchall()
        
        if top_products:
            df = pd.DataFrame(top_products)
            fig = px.bar(df, x='name', y='total_sales', title="پڕفرۆشترین بەرهەمەکان")
            st.plotly_chart(fig, use_container_width=True)

# ======================== ADMIN PAGE ========================
def show_admin_page():
    st.markdown("### 👨‍💼 پانێڵی بەڕێوەبەر")
    
    tab1, tab2, tab3, tab4 = st.tabs(["👥 بەکارهێنەران", "🏷️ داشکانەکان", "📂 پۆلێنەکان", "⚙️ ڕێکخستنەکانی سیستم"])
    
    with tab1:
        st.markdown("#### 👥 بەڕێوەبردنی بەکارهێنەران")
        
        with get_db() as conn:
            users = conn.execute("SELECT * FROM users").fetchall()
        
        if users:
            for user in users:
                with st.expander(f"{user['full_name']} ({user['role']})"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**ناوی بەکارهێنەر:** {user['username']}")
                        st.write(f"**ڕۆڵ:** {user['role']}")
                        st.write(f"**چالاکە:** {'بەڵێ' if user['is_active'] else 'نەخێر'}")
                    with col2:
                        st.write(f"**دوایین چوونەژوورەوە:** {user['last_login'] or 'هیچ'}")
                        st.write(f"**بەرواری دروستکردن:** {user['created_at']}")
                    
                    if st.button(f"🔄 چالاک/ناچالاک", key=f"toggle_{user['id']}"):
                        with get_db() as conn:
                            conn.execute(
                                "UPDATE users SET is_active = ? WHERE id = ?",
                                (not user['is_active'], user['id'])
                            )
                            conn.commit()
                        st.rerun()
        
        # Add new user
        with st.form("add_user_form"):
            st.markdown("#### ➕ زیادکردنی بەکارهێنەری نوێ")
            col1, col2 = st.columns(2)
            with col1:
                new_username = st.text_input("ناوی بەکارهێنەر")
                new_password = st.text_input("وشەی نهێنی", type="password")
                new_fullname = st.text_input("ناوی تەواو")
            with col2:
                new_role = st.selectbox("ڕۆڵ", ["cashier", "manager", "admin"])
            
            if st.form_submit_button("زیادکردن"):
                if new_username and new_password:
                    password_hash = hashlib.sha256(new_password.encode()).hexdigest()
                    with get_db() as conn:
                        try:
                            conn.execute(
                                "INSERT INTO users (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)",
                                (new_username, password_hash, new_fullname, new_role)
                            )
                            conn.commit()
                            st.success("بەکارهێنەر بە سەرکەوتوویی زیادکرا!")
                            st.rerun()
                        except:
                            st.error("ناوی بەکارهێنەر پێشتر بەکارهاتووە")
    
    with tab2:
        st.markdown("#### 🏷️ بەڕێوەبردنی داشکانەکان")
        
        # Add discount form
        with st.form("add_discount_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                code = st.text_input("کۆدی داشکان", placeholder="SALE2024")
                discount_type = st.selectbox("جۆری داشکان", ["percentage", "fixed"])
            with col2:
                value = st.number_input("بڕ", min_value=0.0, step=0.5)
                min_purchase = st.number_input("کەمترین کڕین", min_value=0.0, step=1000.0)
            with col3:
                max_discount = st.number_input("زۆرترین داشکان", min_value=0.0, step=1000.0)
                usage_limit = st.number_input("سنووری بەکارهێنان", min_value=0, value=100)
            
            start_date = st.date_input("بەرواری دەستپێک")
            end_date = st.date_input("بەرواری کۆتایی")
            description = st.text_area("وەسف")
            
            if st.form_submit_button("زیادکردنی داشکان"):
                if code:
                    with get_db() as conn:
                        conn.execute(
                            """INSERT INTO discounts (code, description, discount_type, value, min_purchase, 
                               max_discount, start_date, end_date, usage_limit)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                            (code, description, discount_type, value, min_purchase, max_discount,
                             start_date, end_date, usage_limit)
                        )
                        conn.commit()
                    st.success("داشکان بە سەرکەوتوویی زیادکرا!")
                    st.rerun()
        
        # Show existing discounts
        with get_db() as conn:
            discounts = conn.execute("SELECT * FROM discounts ORDER BY created_at DESC").fetchall()
        
        if discounts:
            for disc in discounts:
                with st.expander(f"{disc['code']} - {disc['description'] or 'بێ وەسف'}"):
                    st.write(f"**جۆر:** {disc['discount_type']}")
                    st.write(f"**بڕ:** {disc['value']}")
                    st.write(f"**بەکارهێنراوە:** {disc['used_count']}/{disc['usage_limit'] or '∞'}")
                    
                    if st.button("🗑️ سڕینەوە", key=f"del_disc_{disc['id']}"):
                        with get_db() as conn:
                            conn.execute("UPDATE discounts SET is_active = 0 WHERE id = ?", (disc['id'],))
                            conn.commit()
                        st.rerun()

def show_settings_page():
    st.markdown("### ⚙️ ڕێکخستنەکانی سیستم")
    
    with st.form("settings_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            store_name = st.text_input("ناوی دووکان", value="کاشێری زیرەک")
            store_phone = st.text_input("ژمارەی تەلەفۆن", value="0750-000-0000")
            currency = st.selectbox("دراو", ["دیناری عێراقی", "دۆلار"])
        
        with col2:
            tax_rate = st.number_input("ڕێژەی باج (%)", min_value=0.0, max_value=100.0, value=0.0)
            receipt_footer = st.text_area("تێکستی خواری پسوڵە", value="سوپاس بۆ کڕینتان!")
            low_stock_alert = st.checkbox("ئاگادارکردنەوەی کۆگای کەم", value=True)
        
        if st.form_submit_button("💾 پاشەکەوتکردن"):
            # Save to settings table
            st.success("ڕێکخستنەکان پاشەکەوت کران!")

def show_customers_page():
    st.markdown("### 👥 بەڕێوەبردنی کڕیاران")
    
    with get_db() as conn:
        customers = conn.execute("SELECT * FROM customers ORDER BY total_purchases DESC").fetchall()
    
    if customers:
        df = pd.DataFrame(customers)
        
        # Search
        search = st.text_input("🔍 گەڕان بەناو کڕیاراندا...")
        if search:
            df = df[df['name'].str.contains(search, case=False) | 
                   df['phone'].str.contains(search, case=False)]
        
        st.dataframe(df, use_container_width=True)
        
        # Customer details
        selected_customer = st.selectbox("کڕیار هەڵبژێرە", df['name'].tolist())
        if selected_customer:
            customer = df[df['name'] == selected_customer].iloc[0]
            st.markdown(f"""
                #### {customer['name']}
                - 📞 تەلەفۆن: {customer['phone'] or 'بێ تەلەفۆن'}
                - ⭐ خاڵەکانی وەفاداری: {customer['loyalty_points']}
                - 💰 کۆی کڕین: {format_currency(customer['total_purchases'])}
                - 📅 بەرواری زیادکردن: {customer['created_at']}
            """)

if __name__ == "__main__":
    main()
