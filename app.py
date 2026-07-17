# supermarket_pro_system.py
import streamlit as st
import json
import os
from datetime import datetime, timedelta
import pandas as pd
import hashlib
import random
import time
from typing import Dict, List, Optional

# -------------------- کۆنفیگی سیستەم --------------------
st.set_page_config(
    page_title="سیستەمی سوپەرمارکێتی پیشەیی",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------- کلاسەکان (Object-Oriented) --------------------
class Product:
    def __init__(self, data: Dict):
        self.id = data.get('id', self.generate_id())
        self.name = data.get('name', '')
        self.price = data.get('price', 0)
        self.category = data.get('category', 'گشتی')
        self.subcategory = data.get('subcategory', '')
        self.stock = data.get('stock', 0)
        self.min_stock = data.get('min_stock', 10)
        self.barcode = data.get('barcode', self.generate_barcode())
        self.icon = data.get('icon', '📦')
        self.supplier = data.get('supplier', '')
        self.cost_price = data.get('cost_price', 0)
        self.discount = data.get('discount', 0)
        self.tax_rate = data.get('tax_rate', 0.15)
        self.created_at = data.get('created_at', datetime.now().isoformat())
        self.updated_at = data.get('updated_at', datetime.now().isoformat())
    
    @staticmethod
    def generate_id():
        return f"PRD{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(100,999)}"
    
    @staticmethod
    def generate_barcode():
        return f"{random.randint(10000000, 99999999)}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'category': self.category,
            'subcategory': self.subcategory,
            'stock': self.stock,
            'min_stock': self.min_stock,
            'barcode': self.barcode,
            'icon': self.icon,
            'supplier': self.supplier,
            'cost_price': self.cost_price,
            'discount': self.discount,
            'tax_rate': self.tax_rate,
            'created_at': self.created_at,
            'updated_at': datetime.now().isoformat()
        }

class Sale:
    def __init__(self, data: Dict):
        self.id = data.get('id', Sale.generate_id())
        self.items = data.get('items', [])
        self.subtotal = data.get('subtotal', 0)
        self.tax = data.get('tax', 0)
        self.discount = data.get('discount', 0)
        self.total = data.get('total', 0)
        self.payment_method = data.get('payment_method', 'نقدی')
        self.customer_id = data.get('customer_id', '')
        self.cashier_id = data.get('cashier_id', '')
        self.date = data.get('date', datetime.now().isoformat())
        self.status = data.get('status', 'completed')
    
    @staticmethod
    def generate_id():
        return f"SL{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(10,99)}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'items': self.items,
            'subtotal': self.subtotal,
            'tax': self.tax,
            'discount': self.discount,
            'total': self.total,
            'payment_method': self.payment_method,
            'customer_id': self.customer_id,
            'cashier_id': self.cashier_id,
            'date': self.date,
            'status': self.status
        }

class Customer:
    def __init__(self, data: Dict):
        self.id = data.get('id', Customer.generate_id())
        self.name = data.get('name', '')
        self.phone = data.get('phone', '')
        self.email = data.get('email', '')
        self.loyalty_points = data.get('loyalty_points', 0)
        self.total_spent = data.get('total_spent', 0)
        self.registered_at = data.get('registered_at', datetime.now().isoformat())
        self.tier = data.get('tier', 'برۆنزی')
    
    @staticmethod
    def generate_id():
        return f"CUS{datetime.now().strftime('%Y%m%d')}{random.randint(100,999)}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'loyalty_points': self.loyalty_points,
            'total_spent': self.total_spent,
            'registered_at': self.registered_at,
            'tier': self.tier
        }

# -------------------- داتابەیس --------------------
DATA_FILE = "supermarket_pro.json"

def load_data():
    default_data = {
        'products': [],
        'sales': [],
        'customers': [],
        'users': [],
        'settings': {
            'shop_name': 'سوپەرمارکێتی گەورە',
            'tax_rate': 0.15,
            'currency': 'IQD',
            'receipt_footer': 'سوپاس بۆ کڕین',
            'loyalty_points_rate': 0.01,
            'opening_time': '08:00',
            'closing_time': '22:00'
        },
        'inventory_logs': [],
        'counter': 0
    }
    
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Merge with default to handle new fields
                for key in default_data:
                    if key not in data:
                        data[key] = default_data[key]
                return data
        except:
            return default_data
    return default_data

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# -------------------- CSS پیشەیی --------------------
st.markdown("""
<style>
    /* Professional Supermarket Theme */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Kufi+Arabic:wght@400;700&display=swap');
    
    * {
        font-family: 'Noto Kufi Arabic', sans-serif;
    }
    
    .main {
        background: #f0f2f6;
    }
    
    /* Header */
    .header-pro {
        background: linear-gradient(135deg, #003366 0%, #0055a4 100%);
        color: white;
        padding: 15px 25px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .header-pro h1 {
        margin: 0;
        font-size: 1.8rem;
        font-weight: 700;
    }
    
    .header-pro .time-display {
        font-size: 1.2rem;
        background: rgba(255,255,255,0.15);
        padding: 8px 18px;
        border-radius: 25px;
        backdrop-filter: blur(10px);
    }
    
    /* Product Card Pro */
    .product-card-pro {
        background: white;
        border-radius: 15px;
        padding: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
        transition: all 0.3s ease;
        border: 2px solid transparent;
        position: relative;
        cursor: pointer;
        height: 100%;
    }
    
    .product-card-pro:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
        border-color: #003366;
    }
    
    .product-card-pro .p-icon {
        font-size: 2.5rem;
        text-align: center;
        margin-bottom: 8px;
    }
    
    .product-card-pro .p-name {
        font-weight: 600;
        font-size: 1rem;
        color: #1a1a2e;
        text-align: center;
    }
    
    .product-card-pro .p-price {
        color: #003366;
        font-weight: 700;
        font-size: 1.3rem;
        text-align: center;
        margin: 5px 0;
    }
    
    .product-card-pro .p-barcode {
        font-size: 0.6rem;
        color: #999;
        text-align: center;
        background: #f5f5f5;
        padding: 2px 10px;
        border-radius: 10px;
        display: inline-block;
        margin: 0 auto;
    }
    
    .product-card-pro .p-stock {
        position: absolute;
        top: 10px;
        right: 10px;
        padding: 2px 12px;
        border-radius: 15px;
        font-size: 0.7rem;
        font-weight: 600;
    }
    
    .p-stock.low {
        background: #ff6b6b;
        color: white;
    }
    
    .p-stock.medium {
        background: #ffd93d;
        color: #333;
    }
    
    .p-stock.high {
        background: #6bcb77;
        color: white;
    }
    
    .p-stock.out {
        background: #ddd;
        color: #666;
    }
    
    .p-discount {
        position: absolute;
        top: 10px;
        left: 10px;
        background: #ff4757;
        color: white;
        padding: 2px 10px;
        border-radius: 15px;
        font-size: 0.7rem;
        font-weight: 700;
    }
    
    /* Cart Pro */
    .cart-pro {
        background: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 2px 15px rgba(0,0,0,0.08);
        max-height: 700px;
        overflow-y: auto;
        position: sticky;
        top: 20px;
    }
    
    .cart-pro .cart-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0;
        border-bottom: 1px solid #f0f0f0;
    }
    
    .cart-pro .item-details {
        display: flex;
        flex-direction: column;
    }
    
    .cart-pro .item-name {
        font-weight: 500;
        font-size: 0.95rem;
    }
    
    .cart-pro .item-meta {
        font-size: 0.8rem;
        color: #888;
    }
    
    .cart-pro .item-total {
        font-weight: 600;
        color: #003366;
    }
    
    .cart-pro .cart-total-box {
        background: linear-gradient(135deg, #003366, #0055a4);
        color: white;
        padding: 20px;
        border-radius: 12px;
        margin-top: 15px;
    }
    
    .cart-pro .cart-total-box .total-row {
        display: flex;
        justify-content: space-between;
        padding: 5px 0;
    }
    
    .cart-pro .cart-total-box .grand-total {
        border-top: 2px solid rgba(255,255,255,0.3);
        padding-top: 10px;
        margin-top: 10px;
        font-size: 1.4rem;
        font-weight: 700;
    }
    
    /* Receipt Pro */
    .receipt-pro {
        background: white;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        max-width: 380px;
        margin: 0 auto;
        font-family: 'Courier New', monospace;
        border: 2px dashed #ccc;
    }
    
    .receipt-pro .r-header {
        text-align: center;
        border-bottom: 1px dashed #ccc;
        padding-bottom: 10px;
        margin-bottom: 15px;
    }
    
    .receipt-pro .r-item {
        display: flex;
        justify-content: space-between;
        padding: 3px 0;
        font-size: 0.9rem;
    }
    
    .receipt-pro .r-total {
        border-top: 2px solid #000;
        padding-top: 10px;
        margin-top: 10px;
        font-weight: 700;
        font-size: 1.1rem;
    }
    
    .receipt-pro .r-footer {
        text-align: center;
        border-top: 1px dashed #ccc;
        padding-top: 10px;
        margin-top: 15px;
        font-size: 0.8rem;
        color: #666;
    }
    
    /* Category buttons */
    .category-tabs-pro {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin: 15px 0;
        padding: 12px;
        background: white;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .category-tabs-pro .cat-btn {
        padding: 6px 18px;
        border-radius: 20px;
        border: 2px solid #e0e0e0;
        background: white;
        cursor: pointer;
        transition: 0.3s;
        font-weight: 500;
        font-size: 0.85rem;
    }
    
    .category-tabs-pro .cat-btn:hover {
        background: #003366;
        color: white;
        border-color: #003366;
    }
    
    .category-tabs-pro .cat-btn.active {
        background: #003366;
        color: white;
        border-color: #003366;
    }
    
    /* Buttons */
    .stButton button {
        border-radius: 10px;
        font-weight: 600;
        transition: 0.3s;
    }
    
    .stButton button:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    }
    
    /* Metrics */
    .metric-box {
        background: white;
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .metric-box .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #003366;
    }
    
    .metric-box .metric-label {
        font-size: 0.85rem;
        color: #666;
        margin-top: 5px;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #003366;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #0055a4;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease;
    }
</style>
""", unsafe_allow_html=True)

# -------------------- لۆجیکی سەرەکی --------------------
data = load_data()

# Session state initialization
if 'cart' not in st.session_state:
    st.session_state.cart = []
if 'selected_category' not in st.session_state:
    st.session_state.selected_category = 'هموو'
if 'current_customer' not in st.session_state:
    st.session_state.current_customer = None
if 'receipt_data' not in st.session_state:
    st.session_state.receipt_data = None
if 'show_receipt' not in st.session_state:
    st.session_state.show_receipt = False
if 'last_sale_id' not in st.session_state:
    st.session_state.last_sale_id = None
if 'notification' not in st.session_state:
    st.session_state.notification = None

# -------------------- فەنکشنە یارمەتیدەرەکان --------------------
def get_stock_status(stock, min_stock):
    if stock <= 0:
        return 'out', 'بەتاڵە', '#ddd'
    elif stock < min_stock:
        return 'low', 'کەمە', '#ff6b6b'
    elif stock < min_stock * 3:
        return 'medium', 'مامناوەند', '#ffd93d'
    else:
        return 'high', 'زۆرە', '#6bcb77'

def calculate_cart_totals(cart):
    subtotal = sum(item['total'] for item in cart)
    discount = sum(item.get('discount_amount', 0) for item in cart)
    taxable = sum(item.get('taxable', 0) for item in cart)
    tax = taxable * data['settings']['tax_rate']
    total = subtotal - discount + tax
    return {
        'subtotal': subtotal,
        'discount': discount,
        'tax': tax,
        'total': total,
        'item_count': len(cart),
        'qty_total': sum(item['qty'] for item in cart)
    }

def add_to_cart(product, qty=1):
    # Check stock
    if product['stock'] < qty:
        st.error(f"⚠️ کۆتای {product['name']} ناکافیە! تەنها {product['stock']} ماوە")
        return False
    
    # Check if already in cart
    for item in st.session_state.cart:
        if item['product_id'] == product['id']:
            if product['stock'] < item['qty'] + qty:
                st.error(f"⚠️ کۆتای ناکافیە! تەنها {product['stock'] - item['qty']} تر دەتوانیت زیاد بکەیت")
                return False
            item['qty'] += qty
            item['total'] = item['price'] * item['qty']
            st.session_state.cart = st.session_state.cart
            st.success(f"✅ {product['name']} زیاد کرا (کۆی گشتی: {item['qty']})")
            return True
    
    # Add new item
    st.session_state.cart.append({
        'product_id': product['id'],
        'name': product['name'],
        'price': product['price'],
        'qty': qty,
        'total': product['price'] * qty,
        'icon': product.get('icon', '📦'),
        'barcode': product.get('barcode', ''),
        'discount': product.get('discount', 0),
        'discount_amount': product['price'] * qty * (product.get('discount', 0) / 100),
        'taxable': product['price'] * qty * (1 - product.get('discount', 0) / 100)
    })
    st.success(f"✅ {qty} x {product['name']} زیاد کرا")
    return True

def complete_sale(payment_method='نقدی'):
    if not st.session_state.cart:
        st.warning("⚠️ سەبەتە بەتاڵە")
        return False
    
    totals = calculate_cart_totals(st.session_state.cart)
    
    # Create sale object
    sale = Sale({
        'items': st.session_state.cart.copy(),
        'subtotal': totals['subtotal'],
        'tax': totals['tax'],
        'discount': totals['discount'],
        'total': totals['total'],
        'payment_method': payment_method,
        'customer_id': st.session_state.current_customer.get('id', '') if st.session_state.current_customer else '',
        'cashier_id': st.session_state.get('user_id', 'cashier_001'),
        'date': datetime.now().isoformat(),
        'status': 'completed'
    })
    
    # Update inventory
    for cart_item in st.session_state.cart:
        for product in data['products']:
            if product['id'] == cart_item['product_id']:
                product['stock'] -= cart_item['qty']
                # Log inventory change
                data['inventory_logs'].append({
                    'product_id': product['id'],
                    'product_name': product['name'],
                    'change': -cart_item['qty'],
                    'new_stock': product['stock'],
                    'reason': 'فرۆشتن',
                    'sale_id': sale.id,
                    'date': datetime.now().isoformat()
                })
                break
    
    # Update customer loyalty
    if st.session_state.current_customer:
        customer = st.session_state.current_customer
        customer['total_spent'] += totals['total']
        customer['loyalty_points'] += int(totals['total'] * data['settings']['loyalty_points_rate'])
        # Update tier
        if customer['total_spent'] >= 1000000:
            customer['tier'] = 'پلاتینیوم'
        elif customer['total_spent'] >= 500000:
            customer['tier'] = 'زێر'
        elif customer['total_spent'] >= 100000:
            customer['tier'] = 'نقره‌'
        else:
            customer['tier'] = 'برۆنزی'
    
    # Save sale
    data['sales'].append(sale.to_dict())
    data['counter'] += 1
    save_data(data)
    
    # Store receipt
    st.session_state.receipt_data = {
        'sale': sale.to_dict(),
        'totals': totals,
        'customer': st.session_state.current_customer
    }
    st.session_state.show_receipt = True
    st.session_state.last_sale_id = sale.id
    
    # Clear cart
    st.session_state.cart = []
    
    st.balloons()
    st.success("🎉 فرۆشتن بە سەرکەوتوویی تەواو بوو!")
    return True

# -------------------- SIDEBAR - Admin Panel --------------------
with st.sidebar:
    st.markdown("""
        <div style="text-align:center; padding:10px 0; background:linear-gradient(135deg,#003366,#0055a4); border-radius:12px; margin-bottom:20px;">
            <h3 style="color:white; margin:0;">⚙️ بەڕێوەبردنی کۆگا</h3>
        </div>
    """, unsafe_allow_html=True)
    
    admin_tabs = st.radio(
        "بەشەکان",
        ["📦 کاڵا", "👥 دروستکەر", "📊 ڕاپۆرت", "⚙️ کۆنفیگ", "📋 مێژوو"],
        label_visibility="collapsed"
    )
    
    # ============ ADMIN: PRODUCTS ============
    if admin_tabs == "📦 کاڵا":
        st.subheader("➕ زیادکردنی کاڵا")
        
        with st.form("add_product_pro", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("🏷️ ناوی کاڵا", placeholder="ناوێک بنووسە...")
                price = st.number_input("💰 نخی فرۆشتن", min_value=100, value=1000, step=500)
                cost = st.number_input("💰 نخی کڕین", min_value=0, value=int(price*0.7), step=500)
            with col2:
                category = st.selectbox("📂 پۆل", ["خواردن", "خواردنەوە", "پاککەرەوە", "کەلوپەل", "ئیکسسوارات", "جلوبەرگ", "تر"])
                subcategory = st.text_input("📁 پۆلی بچووک", placeholder="وەک: شیری، گۆشت...")
                supplier = st.text_input("🏢 دابینکەر", placeholder="ناوی دابینکەر")
            
            col3, col4 = st.columns(2)
            with col3:
                stock = st.number_input("📦 کۆتا", min_value=0, value=50, step=10)
                min_stock = st.number_input("⚠️ کەمترین کۆتا", min_value=1, value=10, step=5)
            with col4:
                discount = st.slider("🏷️ دەسکەونت (%)", 0, 80, 0, 5)
                tax_rate = st.slider("📊 باج (%)", 0, 30, int(data['settings']['tax_rate']*100), 1)
            
            icon = st.selectbox("🎨 ئایکۆن", ["📦", "🥫", "🧃", "🥛", "🍞", "🥩", "🍎", "🧴", "🧹", "📱", "👕", "🛋️", "🍪", "🥫", "🧊"])
            
            if st.form_submit_button("➕ زیادکردن", use_container_width=True, type="primary"):
                if name and price > 0:
                    product = Product({
                        'name': name,
                        'price': price,
                        'category': category,
                        'subcategory': subcategory,
                        'stock': stock,
                        'min_stock': min_stock,
                        'icon': icon,
                        'supplier': supplier,
                        'cost_price': cost,
                        'discount': discount/100,
                        'tax_rate': tax_rate/100
                    })
                    data['products'].append(product.to_dict())
                    save_data(data)
                    st.success(f"✅ {name} بە سەرکەوتوویی زیاد کرا")
                    st.rerun()
                else:
                    st.error("⚠️ تکایە ناو و نرخێکی دروست داخل بکە")
        
        # Import bulk
        with st.expander("📥 هەناردەکردنی فرە کاڵا"):
            st.write("کاڵاکان بەم شێوەیە بنووسە: **ناو,نرخ,پۆل,کۆتا**")
            bulk = st.text_area("کاڵاکان", height=150, placeholder="شیر,1500,خواردن,100\nنان,1000,خواردن,50")
            if st.button("📥 زیادکردنی هەمووی"):
                added = 0
                for line in bulk.strip().split('\n'):
                    if ',' in line:
                        parts = line.split(',')
                        try:
                            name = parts[0].strip()
                            price = int(parts[1].strip())
                            category = parts[2].strip() if len(parts) > 2 else 'گشتی'
                            stock = int(parts[3].strip()) if len(parts) > 3 else 20
                            product = Product({
                                'name': name,
                                'price': price,
                                'category': category,
                                'stock': stock
                            })
                            data['products'].append(product.to_dict())
                            added += 1
                        except:
                            pass
                if added > 0:
                    save_data(data)
                    st.success(f"✅ {added} کاڵا زیاد کران")
                    st.rerun()
    
    # ============ ADMIN: CUSTOMERS ============
    elif admin_tabs == "👥 دروستکەر":
        st.subheader("👥 بەڕێوەبردنی دروستکەر")
        
        with st.form("add_customer"):
            name = st.text_input("📛 ناوی دروستکەر")
            phone = st.text_input("📱 ژمارەی تەلەفۆن")
            email = st.text_input("📧 ئیمەیڵ")
            
            if st.form_submit_button("➕ زیادکردن"):
                customer = Customer({
                    'name': name,
                    'phone': phone,
                    'email': email
                })
                data['customers'].append(customer.to_dict())
                save_data(data)
                st.success(f"✅ {name} زیاد کرا")
                st.rerun()
        
        st.subheader("📋 لیستی دروستکەران")
        if data['customers']:
            for customer in data['customers']:
                tier_color = {
                    'پلاتینیوم': '💎',
                    'زێر': '🥇',
                    'نقره‌': '🥈',
                    'برۆنزی': '🥉'
                }.get(customer.get('tier', 'برۆنزی'), '⭐')
                
                st.markdown(f"""
                    <div style="background:white; padding:12px; border-radius:10px; margin:5px 0; border-left:4px solid #003366;">
                        <div style="display:flex; justify-content:space-between;">
                            <div>
                                <b>{customer['name']}</b>
                                <br>
                                <span style="font-size:0.8rem; color:#666;">{customer.get('phone', '')}</span>
                            </div>
                            <div style="text-align:right;">
                                <div>{tier_color} {customer.get('tier', 'برۆنزی')}</div>
                                <div style="font-size:0.8rem; color:#666;">⭐ {customer.get('loyalty_points', 0)} خاڵ</div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"انتخاب کردن", key=f"select_cust_{customer['id']}"):
                    st.session_state.current_customer = customer
                    st.success(f"✅ {customer['name']} هەڵبژێردرا")
                    st.rerun()
        
        if st.session_state.current_customer:
            st.info(f"👤 دروستکەری ئێستا: {st.session_state.current_customer['name']}")
            if st.button("🚫 لابردنی دروستکەر"):
                st.session_state.current_customer = None
                st.rerun()
    
    # ============ ADMIN: REPORTS ============
    elif admin_tabs == "📊 ڕاپۆرت":
        st.subheader("📊 ڕاپۆرتی فرۆشتن")
        
        if data['sales']:
            df = pd.DataFrame(data['sales'])
            df['date'] = pd.to_datetime(df['date'])
            
            total_revenue = df['total'].sum()
            total_sales = len(df)
            avg_sale = df['total'].mean()
            
            col1, col2, col3 = st.columns(3)
            col1.metric("💰 داهات", f"{total_revenue:,.0f} IQD")
            col2.metric("🧾 فرۆشتن", total_sales)
            col3.metric("📊 تێکڕا", f"{avg_sale:,.0f} IQD")
            
            # Daily chart
            st.subheader("📈 داهاتی ڕۆژانە")
            daily = df.groupby(df['date'].dt.date)['total'].sum().reset_index()
            st.bar_chart(daily.set_index('date'))
            
            # Sales by category
            st.subheader("📊 فرۆشتن بەپێی پۆل")
            category_sales = {}
            for sale in data['sales']:
                for item in sale['items']:
                    # Find product category
                    product = next((p for p in data['products'] if p['id'] == item.get('product_id', '')), None)
                    if product:
                        cat = product.get('category', 'گشتی')
                        category_sales[cat] = category_sales.get(cat, 0) + item['total']
            
            if category_sales:
                cat_df = pd.DataFrame(category_sales.items(), columns=['پۆل', 'داهات'])
                st.dataframe(cat_df, use_container_width=True)
            
            # Export
            csv = df[['id', 'date', 'total']].to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 دابەزاندنی ڕاپۆرت (CSV)",
                csv,
                f"report_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv"
            )
        else:
            st.info("هیچ فرۆشتنێک نیە")
    
    # ============ ADMIN: SETTINGS ============
    elif admin_tabs == "⚙️ کۆنفیگ":
        st.subheader("⚙️ کۆنفیگی سیستەم")
        
        shop_name = st.text_input("🏪 ناوی فرۆشگا", data['settings']['shop_name'])
        tax_rate = st.slider("📊 باج", 0.0, 0.30, data['settings']['tax_rate'], 0.01)
        currency = st.text_input("💰 دراو", data['settings']['currency'])
        loyalty_rate = st.slider("⭐ خاڵی دڵسۆزی", 0.0, 0.05, data['settings']['loyalty_points_rate'], 0.001)
        footer = st.text_area("📝 پێنووسی وەچە", data['settings']['receipt_footer'])
        
        if st.button("💾 هەڵگرتن", use_container_width=True, type="primary"):
            data['settings']['shop_name'] = shop_name
            data['settings']['tax_rate'] = tax_rate
            data['settings']['currency'] = currency
            data['settings']['loyalty_points_rate'] = loyalty_rate
            data['settings']['receipt_footer'] = footer
            save_data(data)
            st.success("✅ کۆنفیگ هەڵگیرا")
            st.rerun()
        
        st.write("---")
        
        # System reset
        with st.expander("⚠️ سڕینەوەی داتا"):
            if st.button("🗑️ سڕینەوەی هەموو داتاکان", use_container_width=True):
                if st.checkbox("دڵنیای لە سڕینەوە؟"):
                    data['products'] = []
                    data['sales'] = []
                    data['customers'] = []
                    data['inventory_logs'] = []
                    data['counter'] = 0
                    save_data(data)
                    st.session_state.cart = []
                    st.success("✅ هەموو داتاکان سڕدرانەوە")
                    st.rerun()
    
    # ============ ADMIN: INVENTORY LOGS ============
    elif admin_tabs == "📋 مێژوو":
        st.subheader("📋 مێژووی کۆتا")
        
        if data['inventory_logs']:
            for log in data['inventory_logs'][-20:]:
                change_color = "#6bcb77" if log['change'] > 0 else "#ff6b6b"
                st.markdown(f"""
                    <div style="background:white; padding:10px; border-radius:8px; margin:5px 0; border-right:4px solid {change_color};">
                        <div style="display:flex; justify-content:space-between;">
                            <div>
                                <b>{log['product_name']}</b>
                                <br>
                                <span style="font-size:0.8rem; color:#666;">{log['reason']}</span>
                            </div>
                            <div style="text-align:right;">
                                <div style="color:{change_color};">
                                    {'+' if log['change'] > 0 else ''}{log['change']}
                                </div>
                                <div style="font-size:0.8rem; color:#666;">کۆتا: {log['new_stock']}</div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("هیچ مێژوویەک نیە")

# ==================== MAIN PAGE ====================
# Header
st.markdown(f"""
    <div class="header-pro fade-in">
        <div>
            <h1>🏪 {data['settings']['shop_name']}</h1>
            <div style="opacity:0.8; font-size:0.9rem;">
                {datetime.now().strftime('%A, %B %d, %Y')}
            </div>
        </div>
        <div class="time-display">
            ⏰ {datetime.now().strftime('%H:%M')}
        </div>
    </div>
""", unsafe_allow_html=True)

# Stats banner
total_products = len(data['products'])
total_customers = len(data['customers'])
today_sales = len([s for s in data['sales'] if datetime.fromisoformat(s['date']).date() == datetime.now().date()])
today_revenue = sum(s['total'] for s in data['sales'] if datetime.fromisoformat(s['date']).date() == datetime.now().date())

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value">{total_products}</div>
            <div class="metric-label">📦 کاڵا</div>
        </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value">{total_customers}</div>
            <div class="metric-label">👥 دروستکەر</div>
        </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value">{today_sales}</div>
            <div class="metric-label">🧾 فرۆشتن (ئەمڕۆ)</div>
        </div>
    """, unsafe_allow_html=True)
with col4:
    st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value">{today_revenue:,.0f}</div>
            <div class="metric-label">💰 داهات (ئەمڕۆ)</div>
        </div>
    """, unsafe_allow_html=True)

# ==================== POS SYSTEM ====================
col_left, col_right = st.columns([2, 1])

with col_left:
    # Categories
    st.markdown('<div class="category-tabs-pro">', unsafe_allow_html=True)
    
    # Get all categories
    all_cats = list(set(p.get('category', 'گشتی') for p in data['products']))
    categories_display = ['هموو'] + sorted(all_cats)
    
    cols = st.columns(min(len(categories_display), 6))
    for idx, cat in enumerate(categories_display):
        if idx < len(cols):
            with cols[idx % len(cols)]:
                if st.button(
                    cat[:15],  # Truncate long names
                    key=f"cat_pro_{idx}",
                    use_container_width=True,
                    type="primary" if st.session_state.selected_category == cat else "secondary"
                ):
                    st.session_state.selected_category = cat
                    st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Search
    search_col1, search_col2, search_col3 = st.columns([2, 1, 1])
    with search_col1:
        search = st.text_input("🔍 گەڕان", placeholder="ناو یان بارکۆد...")
    with search_col2:
        if st.button("📷 سکان", use_container_width=True):
            st.info("پشتیوانی سکانەر...")
    with search_col3:
        if st.button("🔄 نوێ", use_container_width=True):
            st.rerun()
    
    # Products grid
    filtered = data['products']
    if st.session_state.selected_category != 'هموو':
        filtered = [p for p in filtered if p.get('category', 'گشتی') == st.session_state.selected_category]
    if search:
        filtered = [p for p in filtered if search.lower() in p['name'].lower() or search in p.get('barcode', '')]
    
    if filtered:
        # Pagination
        per_page = 12
        page = st.number_input('', min_value=1, max_value=(len(filtered)-1)//per_page+1, value=1, label_visibility='collapsed')
        start_idx = (page - 1) * per_page
        end_idx = min(start_idx + per_page, len(filtered))
        
        cols = st.columns(4)
        for idx, product in enumerate(filtered[start_idx:end_idx]):
            with cols[idx % 4]:
                stock_status, stock_label, stock_color = get_stock_status(product['stock'], product.get('min_stock', 10))
                
                st.markdown(f"""
                    <div class="product-card-pro">
                        <div class="p-icon">{product.get('icon', '📦')}</div>
                        <div class="p-name">{product['name'][:20]}</div>
                        <div class="p-price">{product['price']:,} IQD</div>
                        <div style="text-align:center;">
                            <span class="p-barcode">#{product.get('barcode', '')}</span>
                        </div>
                        <div class="p-stock {stock_status}">{stock_label}</div>
                        {f'<div class="p-discount">-{int(product.get("discount", 0)*100)}%</div>' if product.get('discount', 0) > 0 else ''}
                    </div>
                """, unsafe_allow_html=True)
                
                qty = st.number_input(
                    'ژ',
                    min_value=1,
                    max_value=product['stock'] if product['stock'] > 0 else 1,
                    value=1,
                    step=1,
                    key=f"qty_pro_{product['id']}",
                    label_visibility='collapsed'
                )
                
                if st.button(
                    '➕ زیاد',
                    key=f"add_pro_{product['id']}",
                    use_container_width=True,
                    disabled=product['stock'] <= 0,
                    type="primary" if product['stock'] > 0 else "secondary"
                ):
                    add_to_cart(product, qty)
                    st.rerun()
        
        # Pagination info
        st.write(f"نمایش {start_idx+1}-{end_idx} لە {len(filtered)} کاڵا")
    else:
        st.warning("هیچ کاڵایەک نەدۆزرایەوە")

with col_right:
    # ==================== CART ====================
    st.markdown('<div class="cart-pro">', unsafe_allow_html=True)
    st.subheader("🛒 سەبەتە")
    
    # Customer info
    if st.session_state.current_customer:
        st.info(f"👤 {st.session_state.current_customer['name']}")
        st.caption(f"⭐ {st.session_state.current_customer.get('loyalty_points', 0)} خاڵ")
    
    if st.session_state.cart:
        totals = calculate_cart_totals(st.session_state.cart)
        
        # Items
        for idx, item in enumerate(st.session_state.cart):
            st.markdown(f"""
                <div class="cart-item">
                    <div class="item-details">
                        <span class="item-name">{item.get('icon', '')} {item['name']}</span>
                        <span class="item-meta">{item['qty']} × {item['price']:,} IQD</span>
                    </div>
                    <div style="display:flex; align-items:center; gap:10px;">
                        <span class="item-total">{item['total']:,}</span>
                        <button onclick="alert('سڕدرایەوە')" style="background:none; border:none; color:red; cursor:pointer; font-size:1.2rem;">✕</button>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"🗑️", key=f"remove_cart_pro_{idx}"):
                st.session_state.cart.pop(idx)
                st.rerun()
        
        # Totals
        st.markdown(f"""
            <div class="cart-total-box">
                <div class="total-row">
                    <span>کۆی گشتی:</span>
                    <span>{totals['subtotal']:,} IQD</span>
                </div>
                <div class="total-row" style="color:#ffd93d;">
                    <span>دەسکەونت:</span>
                    <span>- {totals['discount']:,.0f} IQD</span>
                </div>
                <div class="total-row" style="opacity:0.8;">
                    <span>باج ({int(data['settings']['tax_rate']*100)}%):</span>
                    <span>+ {totals['tax']:,.0f} IQD</span>
                </div>
                <div class="grand-total">
                    <span>💰 کۆی گشتی:</span>
                    <span>{totals['total']:,.0f} IQD</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.write(f"📦 {totals['qty_total']} کاڵا | 🧾 {totals['item_count']} جۆر")
        
        # Payment methods
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            if st.button("💵 نقدی", use_container_width=True, type="primary"):
                complete_sale('نقدی')
                st.rerun()
        with col_p2:
            if st.button("💳 کارت", use_container_width=True):
                complete_sale('کارت')
                st.rerun()
        with col_p3:
            if st.button("📱 موبایل", use_container_width=True):
                complete_sale('موبایل')
                st.rerun()
        
        if st.button("🗑️ پاککردنەوەی سەبەتە", use_container_width=True):
            st.session_state.cart = []
            st.rerun()
    
    else:
        st.markdown("""
            <div style="text-align:center; padding:40px 0; color:#999;">
                <div style="font-size:4rem;">🛍️</div>
                <p style="font-size:1.1rem; margin-top:10px;">سەبەتە بەتاڵە</p>
                <p style="font-size:0.9rem;">تکایە کاڵاکانت هەڵبژێرە</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== RECEIPT ====================
if st.session_state.show_receipt and st.session_state.receipt_data:
    st.markdown("---")
    st.markdown("### 🧾 وەچەی فرۆشتن")
    
    data_rec = st.session_state.receipt_data
    sale = data_rec['sale']
    totals = data_rec['totals']
    customer = data_rec.get('customer')
    
    st.markdown(f"""
        <div class="receipt-pro">
            <div class="r-header">
                <h3>{data['settings']['shop_name']}</h3>
                <p style="margin:3px 0; font-size:0.8rem;">{datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
                <p style="margin:3px 0; font-size:0.8rem; font-weight:bold;">وەچە # {sale['id']}</p>
                {f'<p style="margin:3px 0; font-size:0.8rem;">👤 {customer["name"]}</p>' if customer else ''}
            </div>
    """, unsafe_allow_html=True)
    
    for item in sale['items']:
        st.markdown(f"""
            <div class="r-item">
                <span>{item.get('icon', '')} {item['name']} × {item['qty']}</span>
                <span>{item['total']:,}</span>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown(f"""
            <div class="r-item">
                <span>کۆی گشتی</span>
                <span>{totals['subtotal']:,}</span>
            </div>
            <div class="r-item" style="color:#ff6b6b;">
                <span>دەسکەونت</span>
                <span>-{totals['discount']:,.0f}</span>
            </div>
            <div class="r-item">
                <span>باج</span>
                <span>+{totals['tax']:,.0f}</span>
            </div>
            <div class="r-total">
                <span>💰 کۆی گشتی</span>
                <span>{totals['total']:,.0f} IQD</span>
            </div>
            <div class="r-item" style="font-size:0.8rem; color:#666; border-top:1px dashed #ccc; padding-top:10px;">
                <span>شێوەی پارەدان</span>
                <span>{sale['payment_method']}</span>
            </div>
            {f'<div class="r-item" style="font-size:0.8rem; color:#666;">⭐ خاڵ: +{int(totals["total"] * data["settings"]["loyalty_points_rate"])}</div>' if customer else ''}
            <div class="r-footer">
                {data['settings']['receipt_footer']}
                <br>
                سوپاس بۆ کڕین
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    col_r1, col_r2, col_r3 = st.columns(3)
    with col_r1:
        if st.button("🖨️ چاپ", use_container_width=True):
            st.info("پشتیوانی چاپ لە وەشانی داهاتوو")
    with col_r2:
        if st.button("📧 ناردن", use_container_width=True):
            st.info("پشتیوانی ناردن لە وەشانی داهاتوو")
    with col_r3:
        if st.button("✕ داخستن", use_container_width=True):
            st.session_state.show_receipt = False
            st.session_state.receipt_data = None
            st.rerun()

# ==================== FOOTER ====================
st.markdown("""
    <hr style="margin:30px 0 20px 0;">
    <div style="text-align:center; color:#999; font-size:0.8rem; padding-bottom:20px;">
        <p>🏪 سیستەمی سوپەرمارکێتی پیشەیی © 2026</p>
        <p style="font-size:0.7rem;">وەشانی 3.0 | دروست کراوە بە ❤️</p>
    </div>
""", unsafe_allow_html=True)
