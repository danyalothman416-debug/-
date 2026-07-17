# supermarket_enterprise.py
import streamlit as st
import json
import os
from datetime import datetime, timedelta
import pandas as pd
import hashlib
import random
import time
import re
import base64
from typing import Dict, List, Optional, Tuple
import uuid
import plotly.graph_objects as go
import plotly.express as px
from io import BytesIO
import qrcode
from PIL import Image

# -------------------- کۆنفیگی سیستەم --------------------
st.set_page_config(
    page_title="سیستەمی سوپەرمارکێتی پڕۆ - Enterprise",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------- کلاسە پێشکەوتووەکان --------------------
class User:
    """بەڕێوەبردنی بەکارهێنەران"""
    def __init__(self, data: Dict):
        self.id = data.get('id', self.generate_id())
        self.username = data.get('username', '')
        self.password_hash = data.get('password_hash', self.hash_password('123456'))
        self.full_name = data.get('full_name', '')
        self.role = data.get('role', 'cashier')  # admin, manager, cashier, stock_manager
        self.permissions = data.get('permissions', [])
        self.active = data.get('active', True)
        self.last_login = data.get('last_login', '')
        self.created_at = data.get('created_at', datetime.now().isoformat())
    
    @staticmethod
    def generate_id():
        return f"USR{datetime.now().strftime('%Y%m%d')}{random.randint(100,999)}"
    
    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'password_hash': self.password_hash,
            'full_name': self.full_name,
            'role': self.role,
            'permissions': self.permissions,
            'active': self.active,
            'last_login': self.last_login,
            'created_at': self.created_at
        }

class Supplier:
    """بەڕێوەبردنی دابینکەران"""
    def __init__(self, data: Dict):
        self.id = data.get('id', self.generate_id())
        self.name = data.get('name', '')
        self.contact_person = data.get('contact_person', '')
        self.phone = data.get('phone', '')
        self.email = data.get('email', '')
        self.address = data.get('address', '')
        self.tax_id = data.get('tax_id', '')
        self.rating = data.get('rating', 0)
        self.products_count = data.get('products_count', 0)
        self.total_orders = data.get('total_orders', 0)
        self.created_at = data.get('created_at', datetime.now().isoformat())
    
    @staticmethod
    def generate_id():
        return f"SUP{datetime.now().strftime('%Y%m%d')}{random.randint(100,999)}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'contact_person': self.contact_person,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'tax_id': self.tax_id,
            'rating': self.rating,
            'products_count': self.products_count,
            'total_orders': self.total_orders,
            'created_at': self.created_at
        }

class PurchaseOrder:
    """داواکاری کڕین (Purchase Order)"""
    def __init__(self, data: Dict):
        self.id = data.get('id', self.generate_id())
        self.supplier_id = data.get('supplier_id', '')
        self.items = data.get('items', [])
        self.total = data.get('total', 0)
        self.status = data.get('status', 'pending')  # pending, approved, received, cancelled
        self.created_by = data.get('created_by', '')
        self.approved_by = data.get('approved_by', '')
        self.created_at = data.get('created_at', datetime.now().isoformat())
        self.approved_at = data.get('approved_at', '')
        self.received_at = data.get('received_at', '')
        self.notes = data.get('notes', '')
    
    @staticmethod
    def generate_id():
        return f"PO{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(10,99)}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'supplier_id': self.supplier_id,
            'items': self.items,
            'total': self.total,
            'status': self.status,
            'created_by': self.created_by,
            'approved_by': self.approved_by,
            'created_at': self.created_at,
            'approved_at': self.approved_at,
            'received_at': self.received_at,
            'notes': self.notes
        }

class Return:
    """گەڕاندنەوەی کاڵا"""
    def __init__(self, data: Dict):
        self.id = data.get('id', self.generate_id())
        self.sale_id = data.get('sale_id', '')
        self.items = data.get('items', [])
        self.reason = data.get('reason', '')
        self.total = data.get('total', 0)
        self.status = data.get('status', 'pending')
        self.created_at = data.get('created_at', datetime.now().isoformat())
        self.approved_by = data.get('approved_by', '')
        self.approved_at = data.get('approved_at', '')
    
    @staticmethod
    def generate_id():
        return f"RET{datetime.now().strftime('%Y%m%d')}{random.randint(100,999)}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'sale_id': self.sale_id,
            'items': self.items,
            'reason': self.reason,
            'total': self.total,
            'status': self.status,
            'created_at': self.created_at,
            'approved_by': self.approved_by,
            'approved_at': self.approved_at
        }

class Shift:
    """وەرزی کارکردن (Shift)"""
    def __init__(self, data: Dict):
        self.id = data.get('id', self.generate_id())
        self.user_id = data.get('user_id', '')
        self.start_time = data.get('start_time', datetime.now().isoformat())
        self.end_time = data.get('end_time', '')
        self.total_sales = data.get('total_sales', 0)
        self.total_transactions = data.get('total_transactions', 0)
        self.cash_start = data.get('cash_start', 0)
        self.cash_end = data.get('cash_end', 0)
        self.difference = data.get('difference', 0)
        self.status = data.get('status', 'open')
    
    @staticmethod
    def generate_id():
        return f"SFT{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(10,99)}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'total_sales': self.total_sales,
            'total_transactions': self.total_transactions,
            'cash_start': self.cash_start,
            'cash_end': self.cash_end,
            'difference': self.difference,
            'status': self.status
        }

# -------------------- داتابەیس --------------------
DATA_FILE = "supermarket_enterprise.json"

def get_default_data():
    """داتای بنەڕەتی بۆ سیستەم"""
    return {
        'products': [],
        'sales': [],
        'customers': [],
        'users': [],
        'suppliers': [],
        'purchase_orders': [],
        'returns': [],
        'shifts': [],
        'inventory_logs': [],
        'settings': {
            'shop_name': 'سوپەرمارکێتی گەورە',
            'tax_rate': 0.15,
            'currency': 'IQD',
            'receipt_footer': 'سوپاس بۆ کڕین',
            'loyalty_points_rate': 0.01,
            'opening_time': '08:00',
            'closing_time': '22:00',
            'auto_backup': True,
            'backup_interval': 24,  # hours
            'max_returns': 30,  # days
            'exchange_rate': 1.0,
            'notification_emails': [],
            'print_receipt': True,
            'receipt_template': 'standard'
        },
        'backups': [],
        'audit_logs': [],
        'counter': 0,
        'last_backup': datetime.now().isoformat()
    }

def load_data():
    """بارکردنی داتا لە پەڕگە"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Merge with default to handle new fields
                default = get_default_data()
                for key in default:
                    if key not in data:
                        data[key] = default[key]
                return data
        except:
            return get_default_data()
    return get_default_data()

def save_data(data):
    """هەڵگرتنی داتا لە پەڕگە"""
    # Auto backup
    if data['settings']['auto_backup']:
        last_backup = datetime.fromisoformat(data['last_backup']) if data['last_backup'] else datetime.now()
        hours_since = (datetime.now() - last_backup).total_seconds() / 3600
        if hours_since >= data['settings']['backup_interval']:
            backup_data = {
                'timestamp': datetime.now().isoformat(),
                'data': data.copy()
            }
            data['backups'].append(backup_data)
            # Keep only last 10 backups
            if len(data['backups']) > 10:
                data['backups'] = data['backups'][-10:]
            data['last_backup'] = datetime.now().isoformat()
    
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# -------------------- فەنکشنە یارمەتیدەرەکان --------------------
def get_stock_status(stock: int, min_stock: int) -> Tuple[str, str, str]:
    """دۆخی کۆتا بژمێرە"""
    if stock <= 0:
        return 'out', 'بەتاڵە', '#ff6b6b'
    elif stock < min_stock:
        return 'low', 'کەمە', '#ffd93d'
    elif stock < min_stock * 3:
        return 'medium', 'مامناوەند', '#ffa94d'
    else:
        return 'high', 'زۆرە', '#6bcb77'

def calculate_cart_totals(cart: List[Dict]) -> Dict:
    """کۆی گشتی سەبەتە بژمێرە"""
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

def generate_barcode() -> str:
    """بارکۆدی تایبەت دروست بکە"""
    return f"{random.randint(10000000, 99999999)}"

def generate_qr(data: str) -> str:
    """QR کۆد دروست بکە"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def format_currency(amount: float) -> str:
    """نرخ بە شێوەی دراو پیشان بدە"""
    return f"{amount:,.0f} {data['settings']['currency']}"

def log_audit(action: str, user: str, details: str):
    """مێژووی چالاکی تۆمار بکە"""
    data['audit_logs'].append({
        'timestamp': datetime.now().isoformat(),
        'user': user,
        'action': action,
        'details': details,
        'ip': '127.0.0.1'  # Would get from request in production
    })
    save_data(data)

# -------------------- CSS --------------------
st.markdown("""
<style>
    /* Professional Enterprise Theme */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Kufi+Arabic:wght@300;400;700;900&display=swap');
    
    * {
        font-family: 'Noto Kufi Arabic', sans-serif;
    }
    
    .main {
        background: #f0f2f6;
    }
    
    /* Enterprise Header */
    .header-enterprise {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: white;
        padding: 20px 30px;
        border-radius: 16px;
        margin-bottom: 25px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.2);
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: relative;
        overflow: hidden;
    }
    
    .header-enterprise::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.05) 0%, transparent 70%);
        animation: pulse 20s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); }
    }
    
    .header-enterprise h1 {
        margin: 0;
        font-size: 2rem;
        font-weight: 900;
        position: relative;
        z-index: 1;
    }
    
    .header-enterprise .subtitle {
        opacity: 0.8;
        font-size: 0.9rem;
        position: relative;
        z-index: 1;
    }
    
    .header-enterprise .header-right {
        text-align: right;
        position: relative;
        z-index: 1;
    }
    
    .header-enterprise .time-display {
        font-size: 1.1rem;
        background: rgba(255,255,255,0.1);
        padding: 8px 20px;
        border-radius: 25px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
        display: inline-block;
    }
    
    /* Product Card Enterprise */
    .product-card-enterprise {
        background: white;
        border-radius: 16px;
        padding: 18px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: 2px solid transparent;
        position: relative;
        cursor: pointer;
        height: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    
    .product-card-enterprise:hover {
        transform: translateY(-6px) scale(1.02);
        box-shadow: 0 12px 40px rgba(0,0,0,0.12);
        border-color: #302b63;
    }
    
    .product-card-enterprise .p-icon {
        font-size: 3rem;
        margin-bottom: 8px;
    }
    
    .product-card-enterprise .p-name {
        font-weight: 600;
        font-size: 1rem;
        color: #1a1a2e;
        text-align: center;
        margin: 5px 0;
        height: 2.8em;
        overflow: hidden;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
    }
    
    .product-card-enterprise .p-price {
        color: #302b63;
        font-weight: 900;
        font-size: 1.4rem;
        margin: 5px 0;
    }
    
    .product-card-enterprise .p-barcode {
        font-size: 0.6rem;
        color: #999;
        background: #f5f5f5;
        padding: 3px 12px;
        border-radius: 12px;
        font-family: monospace;
    }
    
    .product-card-enterprise .p-stock {
        position: absolute;
        top: 12px;
        right: 12px;
        padding: 3px 14px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .p-stock.out { background: #ff6b6b; color: white; }
    .p-stock.low { background: #ffd93d; color: #333; }
    .p-stock.medium { background: #ffa94d; color: white; }
    .p-stock.high { background: #6bcb77; color: white; }
    
    .product-card-enterprise .p-discount {
        position: absolute;
        top: 12px;
        left: 12px;
        background: linear-gradient(135deg, #ff4757, #ff6b81);
        color: white;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 800;
        box-shadow: 0 2px 10px rgba(255,71,87,0.3);
        animation: discount-pulse 2s infinite;
    }
    
    @keyframes discount-pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    /* Cart Enterprise */
    .cart-enterprise {
        background: white;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        max-height: 750px;
        overflow-y: auto;
        position: sticky;
        top: 20px;
    }
    
    .cart-enterprise .cart-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 0;
        border-bottom: 1px solid #f0f0f0;
        transition: 0.2s;
    }
    
    .cart-enterprise .cart-item:hover {
        background: #f8f9fa;
        margin: 0 -10px;
        padding: 12px 10px;
        border-radius: 8px;
    }
    
    .cart-enterprise .item-details {
        display: flex;
        flex-direction: column;
    }
    
    .cart-enterprise .item-name {
        font-weight: 600;
        font-size: 0.95rem;
    }
    
    .cart-enterprise .item-meta {
        font-size: 0.8rem;
        color: #888;
    }
    
    .cart-enterprise .item-total {
        font-weight: 700;
        color: #302b63;
        font-size: 1.05rem;
    }
    
    .cart-enterprise .cart-total-box {
        background: linear-gradient(135deg, #0f0c29, #302b63);
        color: white;
        padding: 25px;
        border-radius: 14px;
        margin-top: 20px;
        box-shadow: 0 4px 20px rgba(48,43,99,0.3);
    }
    
    .cart-enterprise .cart-total-box .total-row {
        display: flex;
        justify-content: space-between;
        padding: 6px 0;
        font-size: 0.95rem;
    }
    
    .cart-enterprise .cart-total-box .grand-total {
        border-top: 2px solid rgba(255,255,255,0.2);
        padding-top: 12px;
        margin-top: 12px;
        font-size: 1.5rem;
        font-weight: 900;
        display: flex;
        justify-content: space-between;
    }
    
    /* Category Tabs */
    .category-tabs-enterprise {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin: 15px 0;
        padding: 15px;
        background: white;
        border-radius: 14px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.04);
    }
    
    .category-tabs-enterprise .cat-btn {
        padding: 8px 22px;
        border-radius: 25px;
        border: 2px solid #e0e0e0;
        background: white;
        cursor: pointer;
        transition: 0.3s;
        font-weight: 600;
        font-size: 0.85rem;
    }
    
    .category-tabs-enterprise .cat-btn:hover {
        background: #302b63;
        color: white;
        border-color: #302b63;
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(48,43,99,0.2);
    }
    
    .category-tabs-enterprise .cat-btn.active {
        background: #302b63;
        color: white;
        border-color: #302b63;
        box-shadow: 0 4px 15px rgba(48,43,99,0.3);
    }
    
    /* Receipt Enterprise */
    .receipt-enterprise {
        background: white;
        padding: 30px;
        border-radius: 16px;
        box-shadow: 0 8px 40px rgba(0,0,0,0.12);
        max-width: 400px;
        margin: 0 auto;
        font-family: 'Courier New', monospace;
        border: 2px solid #e0e0e0;
        position: relative;
    }
    
    .receipt-enterprise::before {
        content: '🏪';
        position: absolute;
        top: -15px;
        left: 50%;
        transform: translateX(-50%);
        background: white;
        padding: 0 10px;
        font-size: 1.5rem;
    }
    
    .receipt-enterprise .r-header {
        text-align: center;
        border-bottom: 2px dashed #ddd;
        padding-bottom: 15px;
        margin-bottom: 15px;
    }
    
    .receipt-enterprise .r-header h3 {
        margin: 0;
        font-size: 1.2rem;
        color: #302b63;
    }
    
    .receipt-enterprise .r-item {
        display: flex;
        justify-content: space-between;
        padding: 4px 0;
        font-size: 0.9rem;
    }
    
    .receipt-enterprise .r-total {
        border-top: 2px solid #000;
        padding-top: 12px;
        margin-top: 12px;
        font-weight: 800;
        font-size: 1.2rem;
    }
    
    .receipt-enterprise .r-footer {
        text-align: center;
        border-top: 2px dashed #ddd;
        padding-top: 15px;
        margin-top: 15px;
        font-size: 0.8rem;
        color: #666;
    }
    
    /* Dashboard Metrics */
    .metric-enterprise {
        background: white;
        padding: 20px;
        border-radius: 14px;
        text-align: center;
        box-shadow: 0 2px 12px rgba(0,0,0,0.05);
        transition: 0.3s;
        border-bottom: 4px solid #302b63;
    }
    
    .metric-enterprise:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.1);
    }
    
    .metric-enterprise .metric-value {
        font-size: 2rem;
        font-weight: 900;
        color: #302b63;
    }
    
    .metric-enterprise .metric-label {
        font-size: 0.85rem;
        color: #666;
        margin-top: 5px;
    }
    
    .metric-enterprise .metric-icon {
        font-size: 2rem;
        margin-bottom: 5px;
    }
    
    /* Buttons */
    .stButton button {
        border-radius: 12px;
        font-weight: 700;
        transition: 0.3s;
        border: none;
        padding: 8px 20px;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }
    
    .stButton button:active {
        transform: translateY(0px);
    }
    
    /* Input fields */
    .stTextInput input, .stNumberInput input, .stTextArea textarea, .stSelectbox select {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        padding: 10px 15px;
        transition: 0.3s;
    }
    
    .stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {
        border-color: #302b63;
        box-shadow: 0 0 0 3px rgba(48,43,99,0.1);
    }
    
    /* Dataframe */
    .dataframe {
        border-radius: 12px !important;
        overflow: hidden !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #0f0c29, #302b63);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #24243e;
    }
    
    /* Animations */
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .slide-in {
        animation: slideIn 0.5s ease;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    .fade-in {
        animation: fadeIn 0.3s ease;
    }
    
    /* Toast notification */
    .toast {
        position: fixed;
        top: 20px;
        right: 20px;
        background: #302b63;
        color: white;
        padding: 15px 25px;
        border-radius: 12px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.2);
        z-index: 9999;
        animation: slideIn 0.5s ease;
    }
</style>
""", unsafe_allow_html=True)

# -------------------- بارکردنی داتا --------------------
data = load_data()

# -------------------- Initialize Session State --------------------
if 'cart' not in st.session_state:
    st.session_state.cart = []
if 'selected_category' not in st.session_state:
    st.session_state.selected_category = 'هموو'
if 'current_customer' not in st.session_state:
    st.session_state.current_customer = None
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'receipt_data' not in st.session_state:
    st.session_state.receipt_data = None
if 'show_receipt' not in st.session_state:
    st.session_state.show_receipt = False
if 'last_sale_id' not in st.session_state:
    st.session_state.last_sale_id = None
if 'notification' not in st.session_state:
    st.session_state.notification = None
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = 'grid'  # grid or list
if 'selected_product' not in st.session_state:
    st.session_state.selected_product = None
if 'current_shift' not in st.session_state:
    st.session_state.current_shift = None
if 'dashboard_refresh' not in st.session_state:
    st.session_state.dashboard_refresh = 0

# -------------------- فەنکشنەکانی فرۆشتن --------------------
def add_to_cart(product: Dict, qty: int = 1) -> bool:
    """کاڵا زیاد بکە بۆ سەبەتە"""
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
            item['discount_amount'] = item['price'] * item['qty'] * (item.get('discount', 0) / 100)
            item['taxable'] = item['price'] * item['qty'] * (1 - item.get('discount', 0) / 100)
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
        'taxable': product['price'] * qty * (1 - product.get('discount', 0) / 100),
        'category': product.get('category', 'گشتی')
    })
    st.success(f"✅ {qty} x {product['name']} زیاد کرا")
    return True

def remove_from_cart(index: int):
    """کاڵا لە سەبەتە بسڕەوە"""
    st.session_state.cart.pop(index)
    st.rerun()

def clear_cart():
    """سەبەتە پاک بکەرەوە"""
    st.session_state.cart = []
    st.rerun()

def complete_sale(payment_method: str = 'نقدی', customer_id: str = '') -> bool:
    """فرۆشتن تەواو بکە"""
    if not st.session_state.cart:
        st.warning("⚠️ سەبەتە بەتاڵە")
        return False
    
    totals = calculate_cart_totals(st.session_state.cart)
    
    # Create sale object
    sale = {
        'id': f"SL{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(10,99)}",
        'items': st.session_state.cart.copy(),
        'subtotal': totals['subtotal'],
        'tax': totals['tax'],
        'discount': totals['discount'],
        'total': totals['total'],
        'payment_method': payment_method,
        'customer_id': customer_id if customer_id else '',
        'cashier_id': st.session_state.current_user.get('id', '') if st.session_state.current_user else 'cashier_001',
        'date': datetime.now().isoformat(),
        'status': 'completed',
        'shift_id': st.session_state.current_shift.get('id', '') if st.session_state.current_shift else ''
    }
    
    # Update inventory
    for cart_item in st.session_state.cart:
        for product in data['products']:
            if product['id'] == cart_item['product_id']:
                old_stock = product['stock']
                product['stock'] -= cart_item['qty']
                # Log inventory change
                data['inventory_logs'].append({
                    'product_id': product['id'],
                    'product_name': product['name'],
                    'change': -cart_item['qty'],
                    'old_stock': old_stock,
                    'new_stock': product['stock'],
                    'reason': 'فرۆشتن',
                    'sale_id': sale['id'],
                    'date': datetime.now().isoformat()
                })
                break
    
    # Update customer loyalty
    if customer_id:
        customer = next((c for c in data['customers'] if c['id'] == customer_id), None)
        if customer:
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
    
    # Update shift
    if st.session_state.current_shift:
        shift = st.session_state.current_shift
        shift['total_sales'] += totals['total']
        shift['total_transactions'] += 1
    
    # Save sale
    data['sales'].append(sale)
    data['counter'] += 1
    save_data(data)
    
    # Log audit
    log_audit('sale_completed', 
              st.session_state.current_user.get('username', 'unknown') if st.session_state.current_user else 'unknown',
              f"Sale {sale['id']} - {format_currency(totals['total'])}")
    
    # Store receipt
    st.session_state.receipt_data = {
        'sale': sale,
        'totals': totals,
        'customer': customer if customer_id else None
    }
    st.session_state.show_receipt = True
    st.session_state.last_sale_id = sale['id']
    
    # Clear cart
    st.session_state.cart = []
    
    st.balloons()
    st.success("🎉 فرۆشتن بە سەرکەوتوویی تەواو بوو!")
    return True

# -------------------- Header --------------------
st.markdown(f"""
    <div class="header-enterprise slide-in">
        <div>
            <h1>🏪 {data['settings']['shop_name']}</h1>
            <div class="subtitle">سیستەمی کاشێری پیشەیی - Enterprise</div>
            <div style="font-size:0.8rem; opacity:0.6; margin-top:5px;">
                {datetime.now().strftime('%A, %B %d, %Y')}
            </div>
        </div>
        <div class="header-right">
            <div class="time-display">
                ⏰ {datetime.now().strftime('%H:%M:%S')}
            </div>
            <div style="margin-top:8px; font-size:0.8rem; opacity:0.7;">
                {f'👤 {st.session_state.current_user["full_name"] if st.session_state.current_user else "گەست"}'}
                {f' | {st.session_state.current_user["role"] if st.session_state.current_user else ""}' if st.session_state.current_user else ''}
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# -------------------- Sidebar - Enterprise Admin --------------------
with st.sidebar:
    st.markdown("""
        <div style="text-align:center; padding:15px 0; background:linear-gradient(135deg,#0f0c29,#302b63); border-radius:14px; margin-bottom:20px;">
            <h3 style="color:white; margin:0;">⚙️ بەڕێوەبردنی کۆگا</h3>
            <p style="color:rgba(255,255,255,0.6); font-size:0.8rem; margin:5px 0 0 0;">Enterprise Management</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Admin Tabs - Organized
    admin_section = st.radio(
        "بەشە سەرەکییەکان",
        ["📊 داشبۆرد", "📦 کاڵا", "👥 دروستکەر", "🏢 دابینکەر", "📋 داواکاری", "📊 ڕاپۆرت", "⚙️ کۆنفیگ"],
        label_visibility="collapsed"
    )
    
    # ==================== 1. DASHBOARD ====================
    if admin_section == "📊 داشبۆرد":
        st.markdown("### 📊 داشبۆردی کۆگا")
        
        # Quick stats
        total_products = len(data['products'])
        total_sales = len(data['sales'])
        total_revenue = sum(s['total'] for s in data['sales'])
        total_customers = len(data['customers'])
        low_stock = len([p for p in data['products'] if p['stock'] < p.get('min_stock', 10)])
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📦 کاڵا", total_products, f"{low_stock} کەم" if low_stock > 0 else "✅ تەواو")
        with col2:
            st.metric("🧾 فرۆشتن", total_sales)
        
        col3, col4 = st.columns(2)
        with col3:
            st.metric("💰 داهات", format_currency(total_revenue))
        with col4:
            st.metric("👥 دروستکەر", total_customers)
        
        # Today's stats
        st.markdown("---")
        st.markdown("#### 📅 ئەمڕۆ")
        today = datetime.now().date()
        today_sales = [s for s in data['sales'] if datetime.fromisoformat(s['date']).date() == today]
        today_revenue = sum(s['total'] for s in today_sales)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🧾 فرۆشتن", len(today_sales))
        with col2:
            st.metric("💰 داهات", format_currency(today_revenue))
        with col3:
            avg = today_revenue / len(today_sales) if today_sales else 0
            st.metric("📊 تێکڕا", format_currency(avg))
        
        # Quick actions
        st.markdown("---")
        st.markdown("#### ⚡ کارکردنی خێرا")
        if st.button("🔄 نوێکردنەوەی داشبۆرد", use_container_width=True):
            st.session_state.dashboard_refresh += 1
            st.rerun()
        
        if st.button("💾 پشتیوانی دەستی", use_container_width=True):
            save_data(data)
            st.success("✅ پشتیوانی هەڵگیرا")
        
        # System status
        st.markdown("---")
        st.markdown("#### 🟢 دۆخی سیستەم")
        st.info("✅ سیستەم بە خێرایی کار دەکات")
        st.caption(f"📁 داتا: {DATA_FILE}")
        st.caption(f"📅 دوایین پشتیوانی: {data.get('last_backup', 'بەتاڵ')}")
        st.caption(f"💾 ژمارەی پشتیوانی: {len(data.get('backups', []))}")
    
    # ==================== 2. PRODUCTS ====================
    elif admin_section == "📦 کاڵا":
        st.markdown("### 📦 بەڕێوەبردنی کاڵا")
        
        # Add product form
        with st.expander("➕ زیادکردنی کاڵای نوێ", expanded=False):
            with st.form("add_product_enterprise", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("🏷️ ناوی کاڵا", placeholder="ناوێک بنووسە...")
                    price = st.number_input("💰 نخی فرۆشتن", min_value=100, value=1000, step=500)
                    cost = st.number_input("📊 نخی کڕین", min_value=0, value=int(price*0.7), step=500)
                with col2:
                    category = st.selectbox("📂 پۆل", ["خواردن", "خواردنەوە", "پاککەرەوە", "کەلوپەل", "ئیکسسوارات", "جلوبەرگ", "تر"])
                    subcategory = st.text_input("📁 پۆلی بچووک", placeholder="وەک: شیری، گۆشت...")
                    supplier_id = st.selectbox("🏢 دابینکەر", [""] + [s['id'] for s in data.get('suppliers', [])], format_func=lambda x: next((s['name'] for s in data.get('suppliers', []) if s['id'] == x), x))
                
                col3, col4 = st.columns(2)
                with col3:
                    stock = st.number_input("📦 کۆتا", min_value=0, value=50, step=10)
                    min_stock = st.number_input("⚠️ کەمترین کۆتا", min_value=1, value=10, step=5)
                    barcode = st.text_input("🔢 بارکۆد", value=generate_barcode())
                with col4:
                    discount = st.slider("🏷️ دەسکەونت (%)", 0, 80, 0, 5)
                    tax_rate = st.slider("📊 باج (%)", 0, 30, int(data['settings']['tax_rate']*100), 1)
                    icon = st.selectbox("🎨 ئایکۆن", ["📦", "🥫", "🧃", "🥛", "🍞", "🥩", "🍎", "🧴", "🧹", "📱", "👕", "🛋️", "🍪", "🥫", "🧊", "🎮", "📚", "🔧", "🪴"])
                
                # Additional fields
                st.markdown("#### 📝 زانیاری زیادە")
                col5, col6 = st.columns(2)
                with col5:
                    weight = st.text_input("⚖️ کێش/قەبارە", placeholder="وەک: 1kg, 500ml")
                with col6:
                    expiry_date = st.date_input("📅 بەرواری بەسەرچوون", value=None, help="ئەگەر هەیە")
                
                notes = st.text_area("📝 تێبینی", placeholder="تێبینی زیادە...", height=60)
                
                if st.form_submit_button("➕ زیادکردن", use_container_width=True, type="primary"):
                    if name and price > 0:
                        product = {
                            'id': f"PRD{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(100,999)}",
                            'name': name,
                            'price': price,
                            'cost_price': cost,
                            'category': category,
                            'subcategory': subcategory,
                            'stock': stock,
                            'min_stock': min_stock,
                            'barcode': barcode,
                            'icon': icon,
                            'supplier_id': supplier_id if supplier_id else '',
                            'discount': discount/100,
                            'tax_rate': tax_rate/100,
                            'weight': weight,
                            'expiry_date': expiry_date.isoformat() if expiry_date else '',
                            'notes': notes,
                            'created_at': datetime.now().isoformat(),
                            'updated_at': datetime.now().isoformat()
                        }
                        data['products'].append(product)
                        save_data(data)
                        log_audit('product_added', 
                                 st.session_state.current_user.get('username', 'unknown') if st.session_state.current_user else 'unknown',
                                 f"Added {name}")
                        st.success(f"✅ {name} بە سەرکەوتوویی زیاد کرا")
                        st.rerun()
                    else:
                        st.error("⚠️ تکایە ناو و نرخێکی دروست داخل بکە")
        
        # Bulk import
        with st.expander("📥 هەناردەکردنی فرە کاڵا", expanded=False):
            st.write("کاڵاکان بەم شێوەیە بنووسە: **ناو,نرخ,پۆل,کۆتا**")
            bulk = st.text_area("کاڵاکان", height=120, placeholder="شیر,1500,خواردن,100\nنان,1000,خواردن,50")
            if st.button("📥 زیادکردنی هەمووی", use_container_width=True):
                added = 0
                for line in bulk.strip().split('\n'):
                    if ',' in line:
                        parts = line.split(',')
                        try:
                            name = parts[0].strip()
                            price = int(parts[1].strip())
                            category = parts[2].strip() if len(parts) > 2 else 'گشتی'
                            stock = int(parts[3].strip()) if len(parts) > 3 else 20
                            product = {
                                'id': f"PRD{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(100,999)}",
                                'name': name,
                                'price': price,
                                'cost_price': int(price * 0.7),
                                'category': category,
                                'stock': stock,
                                'min_stock': 10,
                                'barcode': generate_barcode(),
                                'icon': '📦',
                                'discount': 0,
                                'tax_rate': data['settings']['tax_rate'],
                                'created_at': datetime.now().isoformat(),
                                'updated_at': datetime.now().isoformat()
                            }
                            data['products'].append(product)
                            added += 1
                        except:
                            pass
                if added > 0:
                    save_data(data)
                    st.success(f"✅ {added} کاڵا زیاد کران")
                    st.rerun()
        
        # Product list with filters
        st.markdown("#### 📋 لیستی کاڵاکان")
        
        # Filters
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            search_filter = st.text_input("🔍 گەڕان", placeholder="ناو یان بارکۆد...")
        with col_f2:
            cat_filter = st.selectbox("📂 پۆل", ["هموو"] + list(set(p.get('category', 'گشتی') for p in data['products'])))
        with col_f3:
            stock_filter = st.selectbox("📦 کۆتا", ["هموو", "کەم", "مامناوەند", "زۆر", "بەتاڵ"])
        
        # Filter products
        filtered_products = data['products']
        if search_filter:
            filtered_products = [p for p in filtered_products if search_filter.lower() in p['name'].lower() or search_filter in p.get('barcode', '')]
        if cat_filter != "هموو":
            filtered_products = [p for p in filtered_products if p.get('category', 'گشتی') == cat_filter]
        if stock_filter != "هموو":
            if stock_filter == "کەم":
                filtered_products = [p for p in filtered_products if 0 < p['stock'] < p.get('min_stock', 10)]
            elif stock_filter == "مامناوەند":
                filtered_products = [p for p in filtered_products if p.get('min_stock', 10) <= p['stock'] < p.get('min_stock', 10) * 3]
            elif stock_filter == "زۆر":
                filtered_products = [p for p in filtered_products if p['stock'] >= p.get('min_stock', 10) * 3]
            elif stock_filter == "بەتاڵ":
                filtered_products = [p for p in filtered_products if p['stock'] <= 0]
        
        # Display as table
        if filtered_products:
            for product in filtered_products:
                stock_status, _, _ = get_stock_status(product['stock'], product.get('min_stock', 10))
                with st.container():
                    col1, col2, col3, col4, col5 = st.columns([2, 1.5, 1.5, 1, 0.8])
                    with col1:
                        st.write(f"{product.get('icon', '📦')} **{product['name']}**")
                        st.caption(f"#{product.get('barcode', '')}")
                    with col2:
                        st.write(f"{format_currency(product['price'])}")
                        st.caption(f"کڕین: {format_currency(product.get('cost_price', 0))}")
                    with col3:
                        status_color = {'high': '🟢', 'medium': '🟡', 'low': '🟠', 'out': '🔴'}.get(stock_status, '⚪')
                        st.write(f"{status_color} {product['stock']} ({product.get('min_stock', 10)})")
                    with col4:
                        st.write(f"📂 {product.get('category', '')}")
                    with col5:
                        if st.button("🗑️", key=f"del_{product['id']}"):
                            data['products'].remove(product)
                            save_data(data)
                            st.rerun()
                st.divider()
        else:
            st.info("هیچ کاڵایەک نەدۆزرایەوە")
    
    # ==================== 3. CUSTOMERS ====================
    elif admin_section == "👥 دروستکەر":
        st.markdown("### 👥 بەڕێوەبردنی دروستکەر")
        
        with st.expander("➕ زیادکردنی دروستکەر", expanded=False):
            with st.form("add_customer_enterprise"):
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("📛 ناوی دروستکەر")
                    phone = st.text_input("📱 ژمارەی تەلەفۆن")
                with col2:
                    email = st.text_input("📧 ئیمەیڵ")
                    address = st.text_input("📍 ناونیشان")
                
                if st.form_submit_button("➕ زیادکردن", use_container_width=True):
                    if name:
                        customer = {
                            'id': f"CUS{datetime.now().strftime('%Y%m%d')}{random.randint(100,999)}",
                            'name': name,
                            'phone': phone,
                            'email': email,
                            'address': address,
                            'loyalty_points': 0,
                            'total_spent': 0,
                            'tier': 'برۆنزی',
                            'registered_at': datetime.now().isoformat()
                        }
                        data['customers'].append(customer)
                        save_data(data)
                        st.success(f"✅ {name} زیاد کرا")
                        st.rerun()
        
        st.markdown("#### 📋 لیستی دروستکەران")
        
        # Search
        search_cust = st.text_input("🔍 گەڕان", placeholder="ناو یان ژمارە...")
        
        customers = data['customers']
        if search_cust:
            customers = [c for c in customers if search_cust.lower() in c['name'].lower() or search_cust in c.get('phone', '')]
        
        if customers:
            for customer in customers:
                tier_colors = {
                    'پلاتینیوم': '💎',
                    'زێر': '🥇',
                    'نقره‌': '🥈',
                    'برۆنزی': '🥉'
                }
                tier_icon = tier_colors.get(customer.get('tier', 'برۆنزی'), '⭐')
                
                col1, col2, col3, col4 = st.columns([2, 1.5, 1.5, 1])
                with col1:
                    st.write(f"**{customer['name']}**")
                    st.caption(f"📱 {customer.get('phone', '')}")
                with col2:
                    st.write(f"{tier_icon} {customer.get('tier', 'برۆنزی')}")
                    st.caption(f"⭐ {customer.get('loyalty_points', 0)} خاڵ")
                with col3:
                    st.write(f"💰 {format_currency(customer.get('total_spent', 0))}")
                with col4:
                    if st.button("انتخاب", key=f"sel_{customer['id']}"):
                        st.session_state.current_customer = customer
                        st.success(f"✅ {customer['name']} هەڵبژێردرا")
                        st.rerun()
                    if st.button("🗑️", key=f"del_cust_{customer['id']}"):
                        data['customers'].remove(customer)
                        save_data(data)
                        st.rerun()
                st.divider()
        else:
            st.info("هیچ دروستکەرێک نەدۆزرایەوە")
    
    # ==================== 4. SUPPLIERS ====================
    elif admin_section == "🏢 دابینکەر":
        st.markdown("### 🏢 بەڕێوەبردنی دابینکەران")
        
        with st.expander("➕ زیادکردنی دابینکەر", expanded=False):
            with st.form("add_supplier"):
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("🏢 ناوی دابینکەر")
                    contact = st.text_input("📇 کەسی پەیوەندی")
                with col2:
                    phone = st.text_input("📱 ژمارە")
                    email = st.text_input("📧 ئیمەیڵ")
                address = st.text_input("📍 ناونیشان")
                tax_id = st.text_input("🆔 ژمارەی باج")
                
                if st.form_submit_button("➕ زیادکردن", use_container_width=True):
                    if name:
                        supplier = {
                            'id': f"SUP{datetime.now().strftime('%Y%m%d')}{random.randint(100,999)}",
                            'name': name,
                            'contact_person': contact,
                            'phone': phone,
                            'email': email,
                            'address': address,
                            'tax_id': tax_id,
                            'rating': 0,
                            'products_count': 0,
                            'total_orders': 0,
                            'created_at': datetime.now().isoformat()
                        }
                        data['suppliers'].append(supplier)
                        save_data(data)
                        st.success(f"✅ {name} زیاد کرا")
                        st.rerun()
        
        st.markdown("#### 📋 لیستی دابینکەران")
        
        if data.get('suppliers', []):
            for supplier in data['suppliers']:
                col1, col2, col3 = st.columns([2, 1.5, 1])
                with col1:
                    st.write(f"**{supplier['name']}**")
                    st.caption(f"📇 {supplier.get('contact_person', '')}")
                with col2:
                    st.write(f"📱 {supplier.get('phone', '')}")
                    st.caption(f"📧 {supplier.get('email', '')}")
                with col3:
                    st.write(f"⭐ {supplier.get('rating', 0)}/5")
                    st.caption(f"📦 {supplier.get('products_count', 0)} کاڵا")
                st.divider()
        else:
            st.info("هیچ دابینکەرێک نیە")
    
    # ==================== 5. PURCHASE ORDERS ====================
    elif admin_section == "📋 داواکاری":
        st.markdown("### 📋 داواکاری کڕین")
        
        with st.expander("➕ داواکاری نوێ", expanded=False):
            with st.form("add_po"):
                col1, col2 = st.columns(2)
                with col1:
                    supplier = st.selectbox("🏢 دابینکەر", [""] + [s['id'] for s in data.get('suppliers', [])], 
                                          format_func=lambda x: next((s['name'] for s in data.get('suppliers', []) if s['id'] == x), x) if x else "هەڵبژێرە")
                with col2:
                    notes = st.text_input("📝 تێبینی")
                
                st.write("#### کاڵاکان")
                po_items = []
                num_items = st.number_input("ژمارەی کاڵا", min_value=1, max_value=20, value=1)
                
                for i in range(num_items):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        product_name = st.text_input(f"ناوی کاڵا {i+1}", key=f"po_name_{i}")
                    with col2:
                        qty = st.number_input(f"ژمارد {i+1}", min_value=1, value=10, key=f"po_qty_{i}")
                    with col3:
                        price = st.number_input(f"نرخ {i+1}", min_value=100, value=1000, key=f"po_price_{i}")
                    if product_name:
                        po_items.append({'name': product_name, 'qty': qty, 'price': price})
                
                if st.form_submit_button("📋 دروستکردنی داواکاری", use_container_width=True, type="primary"):
                    if supplier and po_items:
                        total = sum(item['qty'] * item['price'] for item in po_items)
                        po = {
                            'id': f"PO{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(10,99)}",
                            'supplier_id': supplier,
                            'items': po_items,
                            'total': total,
                            'status': 'pending',
                            'created_by': st.session_state.current_user.get('id', '') if st.session_state.current_user else '',
                            'created_at': datetime.now().isoformat(),
                            'notes': notes
                        }
                        data['purchase_orders'].append(po)
                        save_data(data)
                        st.success(f"✅ داواکاری دروست کرا - کۆی گشتی: {format_currency(total)}")
                        st.rerun()
        
        st.markdown("#### 📋 لیستی داواکارییەکان")
        
        if data.get('purchase_orders', []):
            for po in data['purchase_orders'][-10:]:
                status_colors = {
                    'pending': '🟡',
                    'approved': '🟢',
                    'received': '🔵',
                    'cancelled': '🔴'
                }
                status_icon = status_colors.get(po.get('status', 'pending'), '⚪')
                
                col1, col2, col3, col4 = st.columns([1.5, 1.5, 1, 1])
                with col1:
                    st.write(f"**{po['id']}**")
                    st.caption(f"📅 {po.get('created_at', '')[:10]}")
                with col2:
                    supplier = next((s['name'] for s in data.get('suppliers', []) if s['id'] == po.get('supplier_id', '')), '')
                    st.write(f"🏢 {supplier}")
                with col3:
                    st.write(f"{status_icon} {po.get('status', 'pending')}")
                with col4:
                    st.write(f"💰 {format_currency(po.get('total', 0))}")
                st.divider()
        else:
            st.info("هیچ داواکارییەک نیە")
    
    # ==================== 6. REPORTS ====================
    elif admin_section == "📊 ڕاپۆرت":
        st.markdown("### 📊 ڕاپۆرتی پێشکەوتوو")
        
        if data['sales']:
            df = pd.DataFrame(data['sales'])
            df['date'] = pd.to_datetime(df['date'])
            
            # Date range filter
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("لە", value=datetime.now() - timedelta(days=30))
            with col2:
                end_date = st.date_input("بۆ", value=datetime.now())
            
            df_filtered = df[(df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)]
            
            if not df_filtered.empty:
                total_revenue = df_filtered['total'].sum()
                total_sales = len(df_filtered)
                avg_sale = df_filtered['total'].mean()
                max_sale = df_filtered['total'].max()
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown(f"""
                        <div class="metric-enterprise">
                            <div class="metric-icon">💰</div>
                            <div class="metric-value">{format_currency(total_revenue)}</div>
                            <div class="metric-label">کۆی داهات</div>
                        </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                        <div class="metric-enterprise">
                            <div class="metric-icon">🧾</div>
                            <div class="metric-value">{total_sales}</div>
                            <div class="metric-label">ژمارەی فرۆشتن</div>
                        </div>
                    """, unsafe_allow_html=True)
                with col3:
                    st.markdown(f"""
                        <div class="metric-enterprise">
                            <div class="metric-icon">📊</div>
                            <div class="metric-value">{format_currency(avg_sale)}</div>
                            <div class="metric-label">تێکڕا</div>
                        </div>
                    """, unsafe_allow_html=True)
                with col4:
                    st.markdown(f"""
                        <div class="metric-enterprise">
                            <div class="metric-icon">🏆</div>
                            <div class="metric-value">{format_currency(max_sale)}</div>
                            <div class="metric-label">بەرزترین</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                # Charts
                st.markdown("#### 📈 داهاتی ڕۆژانە")
                daily = df_filtered.groupby(df_filtered['date'].dt.date)['total'].sum().reset_index()
                fig = px.bar(daily, x='date', y='total', title='داهاتی ڕۆژانە', 
                            labels={'date': 'بەروار', 'total': 'داهات (IQD)'})
                fig.update_layout(plot_bgcolor='white', height=300)
                st.plotly_chart(fig, use_container_width=True)
                
                # Payment methods
                st.markdown("#### 💳 شێوەی پارەدان")
                payment_counts = df_filtered['payment_method'].value_counts().reset_index()
                payment_counts.columns = ['شێوەی پارەدان', 'ژمارە']
                fig = px.pie(payment_counts, values='ژمارە', names='شێوەی پارەدان', title='پارەدان بەپێی شێوە')
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
                
                # Export
                st.markdown("#### 📥 هەناردەکردن")
                csv = df_filtered[['id', 'date', 'total', 'payment_method']].to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 دابەزاندنی ڕاپۆرت (CSV)",
                    csv,
                    f"report_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv",
                    use_container_width=True
                )
                
                if st.button("🖨️ چاپکردنی ڕاپۆرت", use_container_width=True):
                    st.info("پشتیوانی چاپ...")
            else:
                st.info("هیچ داتایەک لەم ماوەیەدا نیە")
        else:
            st.info("هیچ فرۆشتنێک تۆمار نەکراوە")
    
    # ==================== 7. SETTINGS ====================
    elif admin_section == "⚙️ کۆنفیگ":
        st.markdown("### ⚙️ کۆنفیگی سیستەم")
        
        with st.expander("🔧 کۆنفیگی گشتی", expanded=True):
            shop_name = st.text_input("🏪 ناوی فرۆشگا", data['settings']['shop_name'])
            currency = st.text_input("💰 دراو", data['settings']['currency'])
            tax_rate = st.slider("📊 باج", 0.0, 0.30, data['settings']['tax_rate'], 0.01)
            loyalty_rate = st.slider("⭐ خاڵی دڵسۆزی", 0.0, 0.05, data['settings']['loyalty_points_rate'], 0.001)
            
            col1, col2 = st.columns(2)
            with col1:
                opening_time = st.text_input("🕐 کاتی کردنەوە", data['settings']['opening_time'])
            with col2:
                closing_time = st.text_input("🕐 کاتی داخستن", data['settings']['closing_time'])
            
            footer = st.text_area("📝 پێنووسی وەچە", data['settings']['receipt_footer'], height=60)
            
            if st.button("💾 هەڵگرتنی کۆنفیگ", use_container_width=True, type="primary"):
                data['settings']['shop_name'] = shop_name
                data['settings']['currency'] = currency
                data['settings']['tax_rate'] = tax_rate
                data['settings']['loyalty_points_rate'] = loyalty_rate
                data['settings']['opening_time'] = opening_time
                data['settings']['closing_time'] = closing_time
                data['settings']['receipt_footer'] = footer
                save_data(data)
                st.success("✅ کۆنفیگ هەڵگیرا")
                st.rerun()
        
        with st.expander("🔄 پشتیوانی"):
            st.write("**پشتیوانی خۆکار:**", "✅ چالاکە" if data['settings']['auto_backup'] else "❌ ناچالاکە")
            st.write(f"**ماوەی پشتیوانی:** {data['settings']['backup_interval']} کاتژمێر")
            
            if st.button("💾 پشتیوانی دەستی", use_container_width=True):
                backup_data = {
                    'timestamp': datetime.now().isoformat(),
                    'data': data.copy()
                }
                data['backups'].append(backup_data)
                save_data(data)
                st.success("✅ پشتیوانی هەڵگیرا")
            
            # Download backup
            backup_json = json.dumps(data, ensure_ascii=False, indent=2)
            st.download_button(
                "📥 دابەزاندنی پشتیوانی",
                backup_json,
                f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "application/json",
                use_container_width=True
            )
        
        with st.expander("🗑️ سڕینەوەی داتا", expanded=False):
            st.warning("⚠️ ئاگادار! ئەم کردارە هەموو داتاکان بەهەمیشەیی دەسڕێتەوە")
            if st.button("🗑️ سڕینەوەی هەموو داتاکان", use_container_width=True):
                if st.checkbox("دڵنیای لە سڕینەوە؟"):
                    data['products'] = []
                    data['sales'] = []
                    data['customers'] = []
                    data['suppliers'] = []
                    data['purchase_orders'] = []
                    data['returns'] = []
                    data['inventory_logs'] = []
                    data['audit_logs'] = []
                    data['counter'] = 0
                    save_data(data)
                    st.session_state.cart = []
                    st.success("✅ هەموو داتاکان سڕدرانەوە")
                    st.rerun()
        
        # System info
        st.markdown("---")
        st.markdown("#### ℹ️ زانیاری سیستەم")
        st.caption(f"📁 پەڕگەی داتا: {DATA_FILE}")
        st.caption(f"📊 ژمارەی کاڵا: {len(data['products'])}")
        st.caption(f"🧾 ژمارەی فرۆشتن: {len(data['sales'])}")
        st.caption(f"👥 ژمارەی دروستکەر: {len(data['customers'])}")
        st.caption(f"💾 ژمارەی پشتیوانی: {len(data.get('backups', []))}")
        st.caption(f"📋 مێژووی چالاکی: {len(data.get('audit_logs', []))}")

# ==================== MAIN POS SYSTEM ====================
# POS Layout
pos_col1, pos_col2 = st.columns([2.2, 1])

with pos_col1:
    # Search Bar
    col_search1, col_search2, col_search3, col_search4 = st.columns([2, 0.8, 0.8, 0.8])
    with col_search1:
        search = st.text_input("🔍 گەڕان", placeholder="ناو، بارکۆد...", key="pos_search")
    with col_search2:
        if st.button("📷 سکان", use_container_width=True):
            st.info("پشتیوانی سکانەر لە وەشانی داهاتوو")
    with col_search3:
        if st.button("🔄 نوێ", use_container_width=True):
            st.rerun()
    with col_search4:
        view_toggle = st.button("📋 📊", use_container_width=True, help="گۆڕینی شێوەی پیشاندان")
        if view_toggle:
            st.session_state.view_mode = 'list' if st.session_state.view_mode == 'grid' else 'grid'
    
    # Categories
    st.markdown('<div class="category-tabs-enterprise">', unsafe_allow_html=True)
    all_cats = list(set(p.get('category', 'گشتی') for p in data['products']))
    categories_display = ['هموو'] + sorted(all_cats)
    
    # Show only first 6 categories, rest in dropdown
    visible_cats = categories_display[:6]
    remaining_cats = categories_display[6:]
    
    for cat in visible_cats:
        if st.button(
            cat,
            key=f"cat_pos_{cat}",
            use_container_width=True,
            type="primary" if st.session_state.selected_category == cat else "secondary"
        ):
            st.session_state.selected_category = cat
            st.rerun()
    
    if remaining_cats:
        with st.container():
            more_cat = st.selectbox("...زیاتر", [""] + remaining_cats, key="more_cats", label_visibility="collapsed")
            if more_cat:
                st.session_state.selected_category = more_cat
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Products display
    filtered = data['products']
    if st.session_state.selected_category != 'هموو':
        filtered = [p for p in filtered if p.get('category', 'گشتی') == st.session_state.selected_category]
    if search:
        filtered = [p for p in filtered if search.lower() in p['name'].lower() or search in p.get('barcode', '')]
    
    # Sort products - show low stock first
    filtered = sorted(filtered, key=lambda p: p['stock'] < p.get('min_stock', 10), reverse=True)
    
    if filtered:
        # Pagination
        per_page = 12 if st.session_state.view_mode == 'grid' else 20
        total_pages = (len(filtered) + per_page - 1) // per_page
        page = st.number_input('', min_value=1, max_value=total_pages, value=1, label_visibility='collapsed', key='pos_page')
        start_idx = (page - 1) * per_page
        end_idx = min(start_idx + per_page, len(filtered))
        
        if st.session_state.view_mode == 'grid':
            # Grid view
            cols = st.columns(4)
            for idx, product in enumerate(filtered[start_idx:end_idx]):
                with cols[idx % 4]:
                    stock_status, stock_label, _ = get_stock_status(product['stock'], product.get('min_stock', 10))
                    discount = product.get('discount', 0)
                    
                    st.markdown(f"""
                        <div class="product-card-enterprise" onclick="alert('{product['name']}')">
                            <div class="p-icon">{product.get('icon', '📦')}</div>
                            <div class="p-name">{product['name'][:25]}</div>
                            <div class="p-price">{format_currency(product['price'])}</div>
                            <div class="p-barcode">#{product.get('barcode', '')[:8]}</div>
                            <div class="p-stock {stock_status}">{stock_label}</div>
                            {f'<div class="p-discount">-{int(discount*100)}%</div>' if discount > 0 else ''}
                        </div>
                    """, unsafe_allow_html=True)
                    
                    qty = st.number_input(
                        'ژ',
                        min_value=1,
                        max_value=product['stock'] if product['stock'] > 0 else 1,
                        value=1,
                        step=1,
                        key=f"qty_pos_{product['id']}",
                        label_visibility='collapsed'
                    )
                    
                    if st.button(
                        '➕ زیاد',
                        key=f"add_pos_{product['id']}",
                        use_container_width=True,
                        disabled=product['stock'] <= 0,
                        type="primary" if product['stock'] > 0 else "secondary"
                    ):
                        add_to_cart(product, qty)
                        st.rerun()
        else:
            # List view
            for product in filtered[start_idx:end_idx]:
                stock_status, stock_label, _ = get_stock_status(product['stock'], product.get('min_stock', 10))
                with st.container():
                    col1, col2, col3, col4, col5 = st.columns([2, 1.5, 1, 0.8, 1])
                    with col1:
                        st.write(f"{product.get('icon', '📦')} **{product['name']}**")
                        st.caption(f"#{product.get('barcode', '')}")
                    with col2:
                        st.write(f"**{format_currency(product['price'])}**")
                    with col3:
                        status_color = {'high': '🟢', 'medium': '🟡', 'low': '🟠', 'out': '🔴'}.get(stock_status, '⚪')
                        st.write(f"{status_color} {product['stock']}")
                    with col4:
                        if product.get('discount', 0) > 0:
                            st.write(f"🏷️ -{int(product['discount']*100)}%")
                    with col5:
                        qty = st.number_input(
                            'ژ',
                            min_value=1,
                            max_value=product['stock'] if product['stock'] > 0 else 1,
                            value=1,
                            step=1,
                            key=f"qty_list_{product['id']}",
                            label_visibility='collapsed'
                        )
                        if st.button(
                            '➕',
                            key=f"add_list_{product['id']}",
                            disabled=product['stock'] <= 0
                        ):
                            add_to_cart(product, qty)
                            st.rerun()
                st.divider()
        
        # Pagination info
        st.caption(f"نمایش {start_idx+1}-{end_idx} لە {len(filtered)} کاڵا | پەڕە {page}/{total_pages}")
    else:
        st.warning("هیچ کاڵایەک نەدۆزرایەوە")

with pos_col2:
    # Cart
    st.markdown('<div class="cart-enterprise">', unsafe_allow_html=True)
    st.subheader("🛒 سەبەتە")
    
    # Customer info in cart
    if st.session_state.current_customer:
        st.info(f"👤 {st.session_state.current_customer['name']} | ⭐ {st.session_state.current_customer.get('loyalty_points', 0)} خاڵ")
    
    if st.session_state.cart:
        totals = calculate_cart_totals(st.session_state.cart)
        
        # Items
        for idx, item in enumerate(st.session_state.cart):
            st.markdown(f"""
                <div class="cart-item">
                    <div class="item-details">
                        <span class="item-name">{item.get('icon', '')} {item['name'][:20]}</span>
                        <span class="item-meta">{item['qty']} × {format_currency(item['price'])}</span>
                    </div>
                    <div style="display:flex; align-items:center; gap:8px;">
                        <span class="item-total">{format_currency(item['total'])}</span>
                        <button onclick="alert('سڕدرایەوە')" style="background:none; border:none; color:#ff6b6b; cursor:pointer; font-size:1.2rem; font-weight:bold;">✕</button>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"🗑️", key=f"remove_cart_enterprise_{idx}", help="سڕینەوە"):
                remove_from_cart(idx)
        
        # Totals
        st.markdown(f"""
            <div class="cart-total-box">
                <div class="total-row">
                    <span>کۆی گشتی:</span>
                    <span>{format_currency(totals['subtotal'])}</span>
                </div>
                <div class="total-row" style="color:#ffd93d;">
                    <span>دەسکەونت:</span>
                    <span>- {format_currency(totals['discount'])}</span>
                </div>
                <div class="total-row" style="opacity:0.8;">
                    <span>باج ({int(data['settings']['tax_rate']*100)}%):</span>
                    <span>+ {format_currency(totals['tax'])}</span>
                </div>
                <div class="grand-total">
                    <span>💰 کۆی گشتی:</span>
                    <span>{format_currency(totals['total'])}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.caption(f"📦 {totals['qty_total']} کاڵا | 🧾 {totals['item_count']} جۆر")
        
        # Payment methods
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            if st.button("💵 نقدی", use_container_width=True, type="primary"):
                if complete_sale('نقدی', st.session_state.current_customer.get('id', '') if st.session_state.current_customer else ''):
                    st.rerun()
        with col_p2:
            if st.button("💳 کارت", use_container_width=True):
                if complete_sale('کارت', st.session_state.current_customer.get('id', '') if st.session_state.current_customer else ''):
                    st.rerun()
        with col_p3:
            if st.button("📱 موبایل", use_container_width=True):
                if complete_sale('موبایل', st.session_state.current_customer.get('id', '') if st.session_state.current_customer else ''):
                    st.rerun()
        
        # Clear cart
        if st.button("🗑️ پاککردنەوەی سەبەتە", use_container_width=True):
            clear_cart()
    else:
        st.markdown("""
            <div style="text-align:center; padding:50px 0; color:#999;">
                <div style="font-size:4rem;">🛍️</div>
                <p style="font-size:1.1rem; margin-top:10px; font-weight:600; color:#666;">سەبەتە بەتاڵە</p>
                <p style="font-size:0.9rem;">تکایە کاڵاکانت هەڵبژێرە</p>
                <p style="font-size:0.8rem; color:#bbb;">کاڵاکان لە کۆگا</p>
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
    
    # Generate QR for receipt
    qr_data = f"Sale: {sale['id']}, Total: {totals['total']}, Date: {datetime.now()}"
    qr_base64 = generate_qr(qr_data)
    
    st.markdown(f"""
        <div class="receipt-enterprise">
            <div class="r-header">
                <h3>{data['settings']['shop_name']}</h3>
                <p style="margin:3px 0; font-size:0.8rem;">{datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
                <p style="margin:3px 0; font-size:0.8rem; font-weight:bold; color:#302b63;"># {sale['id']}</p>
                {f'<p style="margin:3px 0; font-size:0.8rem;">👤 {customer["name"]}</p>' if customer else ''}
                <p style="margin:3px 0; font-size:0.7rem; color:#888;">💳 {sale['payment_method']}</p>
            </div>
    """, unsafe_allow_html=True)
    
    for item in sale['items']:
        st.markdown(f"""
            <div class="r-item">
                <span>{item.get('icon', '')} {item['name']} × {item['qty']}</span>
                <span>{format_currency(item['total'])}</span>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown(f"""
            <div class="r-item">
                <span>کۆی گشتی</span>
                <span>{format_currency(totals['subtotal'])}</span>
            </div>
            <div class="r-item" style="color:#ff6b6b;">
                <span>دەسکەونت</span>
                <span>-{format_currency(totals['discount'])}</span>
            </div>
            <div class="r-item" style="opacity:0.7;">
                <span>باج</span>
                <span>+{format_currency(totals['tax'])}</span>
            </div>
            <div class="r-total">
                <span>💰 کۆی گشتی</span>
                <span>{format_currency(totals['total'])}</span>
            </div>
            {f'<div class="r-item" style="font-size:0.8rem; color:#888; border-top:1px dashed #ccc; padding-top:10px;">⭐ خاڵ: +{int(totals["total"] * data["settings"]["loyalty_points_rate"])}</div>' if customer else ''}
            <div class="r-footer">
                <img src="data:image/png;base64,{qr_base64}" style="width:80px; height:80px; margin:5px auto; display:block;">
                {data['settings']['receipt_footer']}
                <br>
                سوپاس بۆ کڕین
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    col_r1, col_r2, col_r3 = st.columns(3)
    with col_r1:
        if st.button("🖨️ چاپ", use_container_width=True):
            st.info("پشتیوانی چاپ...")
    with col_r2:
        if st.button("📧 ناردن", use_container_width=True):
            st.info("پشتیوانی ناردن...")
    with col_r3:
        if st.button("✕ داخستن", use_container_width=True):
            st.session_state.show_receipt = False
            st.session_state.receipt_data = None
            st.rerun()

# ==================== FOOTER ====================
st.markdown("""
    <hr style="margin:30px 0 20px 0; border: none; height: 2px; background: linear-gradient(to right, transparent, #302b63, transparent);">
    <div style="text-align:center; color:#999; font-size:0.8rem; padding-bottom:20px;">
        <p>🏪 سیستەمی سوپەرمارکێتی پڕۆ - Enterprise</p>
        <p style="font-size:0.7rem; opacity:0.6;">وەشانی 4.0 | دروست کراوە بە ❤️ | 2,000+ هێڵی کۆد</p>
        <p style="font-size:0.7rem; opacity:0.4;">© 2026 - هەموو مافەکان پارێزراون</p>
    </div>
""", unsafe_allow_html=True)
