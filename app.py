# mobile_shop_pro.py
# سیستەمی کاشێری پیشەیی بۆ دووکانی مۆبایل - 3000+ هێڵ
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
import csv
from collections import defaultdict

# -------------------- کۆنفیگی سیستەم --------------------
st.set_page_config(
    page_title="دووکانی مۆبایل - کاشێری پیشەیی",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------- کلاسە پێشکەوتووەکان --------------------
class Product:
    """کاڵا - مۆبایل، ئیکسسوارات، نۆرم"""
    def __init__(self, data: Dict):
        self.id = data.get('id', self.generate_id())
        self.name = data.get('name', '')
        self.brand = data.get('brand', '')
        self.model = data.get('model', '')
        self.price = data.get('price', 0)
        self.cost_price = data.get('cost_price', 0)
        self.category = data.get('category', 'مۆبایل')
        self.subcategory = data.get('subcategory', '')
        self.stock = data.get('stock', 0)
        self.min_stock = data.get('min_stock', 5)
        self.barcode = data.get('barcode', self.generate_barcode())
        self.serial_number = data.get('serial_number', '')
        self.warranty_months = data.get('warranty_months', 12)
        self.color = data.get('color', '')
        self.storage = data.get('storage', '')
        self.ram = data.get('ram', '')
        self.condition = data.get('condition', 'نوێ')  # نوێ، بەکارهاتوو
        self.supplier = data.get('supplier', '')
        self.discount = data.get('discount', 0)
        self.tax_rate = data.get('tax_rate', 0.0)
        self.icon = data.get('icon', '📱')
        self.images = data.get('images', [])
        self.description = data.get('description', '')
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
            'brand': self.brand,
            'model': self.model,
            'price': self.price,
            'cost_price': self.cost_price,
            'category': self.category,
            'subcategory': self.subcategory,
            'stock': self.stock,
            'min_stock': self.min_stock,
            'barcode': self.barcode,
            'serial_number': self.serial_number,
            'warranty_months': self.warranty_months,
            'color': self.color,
            'storage': self.storage,
            'ram': self.ram,
            'condition': self.condition,
            'supplier': self.supplier,
            'discount': self.discount,
            'tax_rate': self.tax_rate,
            'icon': self.icon,
            'images': self.images,
            'description': self.description,
            'created_at': self.created_at,
            'updated_at': datetime.now().isoformat()
        }

class Sale:
    """فرۆشتن"""
    def __init__(self, data: Dict):
        self.id = data.get('id', self.generate_id())
        self.items = data.get('items', [])
        self.subtotal = data.get('subtotal', 0)
        self.tax = data.get('tax', 0)
        self.discount = data.get('discount', 0)
        self.total = data.get('total', 0)
        self.payment_method = data.get('payment_method', 'نقدی')
        self.customer_id = data.get('customer_id', '')
        self.customer_name = data.get('customer_name', '')
        self.customer_phone = data.get('customer_phone', '')
        self.cashier_id = data.get('cashier_id', '')
        self.cashier_name = data.get('cashier_name', '')
        self.date = data.get('date', datetime.now().isoformat())
        self.status = data.get('status', 'completed')
        self.notes = data.get('notes', '')
        self.device_imei = data.get('device_imei', '')
        self.warranty_start = data.get('warranty_start', '')
        self.warranty_end = data.get('warranty_end', '')
    
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
            'customer_name': self.customer_name,
            'customer_phone': self.customer_phone,
            'cashier_id': self.cashier_id,
            'cashier_name': self.cashier_name,
            'date': self.date,
            'status': self.status,
            'notes': self.notes,
            'device_imei': self.device_imei,
            'warranty_start': self.warranty_start,
            'warranty_end': self.warranty_end
        }

class Customer:
    """دروستکەر"""
    def __init__(self, data: Dict):
        self.id = data.get('id', self.generate_id())
        self.name = data.get('name', '')
        self.phone = data.get('phone', '')
        self.email = data.get('email', '')
        self.address = data.get('address', '')
        self.loyalty_points = data.get('loyalty_points', 0)
        self.total_spent = data.get('total_spent', 0)
        self.total_purchases = data.get('total_purchases', 0)
        self.tier = data.get('tier', 'برۆنزی')
        self.registered_at = data.get('registered_at', datetime.now().isoformat())
        self.last_purchase = data.get('last_purchase', '')
        self.notes = data.get('notes', '')
    
    @staticmethod
    def generate_id():
        return f"CUS{datetime.now().strftime('%Y%m%d')}{random.randint(100,999)}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'loyalty_points': self.loyalty_points,
            'total_spent': self.total_spent,
            'total_purchases': self.total_purchases,
            'tier': self.tier,
            'registered_at': self.registered_at,
            'last_purchase': self.last_purchase,
            'notes': self.notes
        }

class Service:
    """خزمەتگوزاری - چاکسازی مۆبایل"""
    def __init__(self, data: Dict):
        self.id = data.get('id', self.generate_id())
        self.name = data.get('name', '')
        self.price = data.get('price', 0)
        self.duration = data.get('duration', '')
        self.description = data.get('description', '')
        self.category = data.get('category', 'چاکسازی')
        self.phone_models = data.get('phone_models', [])
        self.created_at = data.get('created_at', datetime.now().isoformat())
    
    @staticmethod
    def generate_id():
        return f"SRV{datetime.now().strftime('%Y%m%d')}{random.randint(100,999)}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'duration': self.duration,
            'description': self.description,
            'category': self.category,
            'phone_models': self.phone_models,
            'created_at': self.created_at
        }

class RepairOrder:
    """داواکاری چاکسازی"""
    def __init__(self, data: Dict):
        self.id = data.get('id', self.generate_id())
        self.customer_id = data.get('customer_id', '')
        self.customer_name = data.get('customer_name', '')
        self.customer_phone = data.get('customer_phone', '')
        self.device_model = data.get('device_model', '')
        self.device_imei = data.get('device_imei', '')
        self.device_color = data.get('device_color', '')
        self.problem = data.get('problem', '')
        self.services = data.get('services', [])
        self.total = data.get('total', 0)
        self.status = data.get('status', 'pending')  # pending, in_progress, done, delivered
        self.notes = data.get('notes', '')
        self.created_at = data.get('created_at', datetime.now().isoformat())
        self.updated_at = data.get('updated_at', datetime.now().isoformat())
        self.done_at = data.get('done_at', '')
        self.delivered_at = data.get('delivered_at', '')
    
    @staticmethod
    def generate_id():
        return f"REP{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(10,99)}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'customer_name': self.customer_name,
            'customer_phone': self.customer_phone,
            'device_model': self.device_model,
            'device_imei': self.device_imei,
            'device_color': self.device_color,
            'problem': self.problem,
            'services': self.services,
            'total': self.total,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at,
            'updated_at': datetime.now().isoformat(),
            'done_at': self.done_at,
            'delivered_at': self.delivered_at
        }

class User:
    """بەکارهێنەر"""
    def __init__(self, data: Dict):
        self.id = data.get('id', self.generate_id())
        self.username = data.get('username', '')
        self.password_hash = data.get('password_hash', self.hash_password('123456'))
        self.full_name = data.get('full_name', '')
        self.role = data.get('role', 'cashier')
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
    """دابینکەر"""
    def __init__(self, data: Dict):
        self.id = data.get('id', self.generate_id())
        self.name = data.get('name', '')
        self.contact_person = data.get('contact_person', '')
        self.phone = data.get('phone', '')
        self.email = data.get('email', '')
        self.address = data.get('address', '')
        self.brand_specialty = data.get('brand_specialty', [])
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
            'brand_specialty': self.brand_specialty,
            'rating': self.rating,
            'products_count': self.products_count,
            'total_orders': self.total_orders,
            'created_at': self.created_at
        }

class IMEITracker:
    """پاراستن و پشتیوانی IMEI"""
    def __init__(self):
        self.imei_data = {}
    
    def add_imei(self, imei: str, product_id: str, customer_id: str = ''):
        self.imei_data[imei] = {
            'product_id': product_id,
            'customer_id': customer_id,
            'sale_date': datetime.now().isoformat(),
            'status': 'available'
        }
    
    def check_imei(self, imei: str) -> Dict:
        return self.imei_data.get(imei, {})

# -------------------- داتابەیس --------------------
DATA_FILE = "mobile_shop_pro.json"

def get_default_data():
    return {
        'products': [],
        'sales': [],
        'customers': [],
        'users': [],
        'suppliers': [],
        'services': [],
        'repair_orders': [],
        'imei_tracker': {},
        'inventory_logs': [],
        'audit_logs': [],
        'settings': {
            'shop_name': 'دووکانی مۆبایل',
            'tax_rate': 0.0,
            'currency': 'IQD',
            'receipt_footer': 'سوپاس بۆ کڕین',
            'loyalty_points_rate': 0.02,
            'opening_time': '09:00',
            'closing_time': '21:00',
            'auto_backup': True,
            'backup_interval': 24,
            'max_returns': 7,
            'warranty_default': 12,
            'imei_required': True,
            'print_receipt': True,
            'receipt_template': 'mobile'
        },
        'backups': [],
        'counter': 0,
        'last_backup': datetime.now().isoformat()
    }

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                default = get_default_data()
                for key in default:
                    if key not in data:
                        data[key] = default[key]
                return data
        except:
            return get_default_data()
    return get_default_data()

def save_data(data):
    if data['settings']['auto_backup']:
        last_backup = datetime.fromisoformat(data['last_backup']) if data['last_backup'] else datetime.now()
        hours_since = (datetime.now() - last_backup).total_seconds() / 3600
        if hours_since >= data['settings']['backup_interval']:
            backup_data = {
                'timestamp': datetime.now().isoformat(),
                'data': data.copy()
            }
            data['backups'].append(backup_data)
            if len(data['backups']) > 10:
                data['backups'] = data['backups'][-10:]
            data['last_backup'] = datetime.now().isoformat()
    
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# -------------------- فەنکشنە یارمەتیدەرەکان --------------------
def get_stock_status(stock: int, min_stock: int) -> Tuple[str, str, str]:
    if stock <= 0:
        return 'out', 'بەتاڵە', '#ff6b6b'
    elif stock < min_stock:
        return 'low', 'کەمە', '#ffd93d'
    elif stock < min_stock * 3:
        return 'medium', 'مامناوەند', '#ffa94d'
    else:
        return 'high', 'زۆرە', '#6bcb77'

def calculate_cart_totals(cart: List[Dict]) -> Dict:
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

def format_currency(amount: float) -> str:
    return f"{amount:,.0f} {data['settings']['currency']}"

def generate_barcode():
    return f"{random.randint(10000000, 99999999)}"

def generate_qr(data_str: str) -> str:
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data_str)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def log_audit(action: str, user: str, details: str):
    data['audit_logs'].append({
        'timestamp': datetime.now().isoformat(),
        'user': user,
        'action': action,
        'details': details
    })
    save_data(data)

def validate_imei(imei: str) -> bool:
    """پشتڕاستکردنەوەی IMEI - 15 ژمارە"""
    return bool(re.match(r'^\d{15}$', imei))

# -------------------- CSS - پرۆ --------------------
st.markdown("""
<style>
    /* Mobile Shop Theme */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Kufi+Arabic:wght@300;400;700;900&display=swap');
    
    * {
        font-family: 'Noto Kufi Arabic', sans-serif;
    }
    
    .main {
        background: #f0f2f6;
    }
    
    /* Header */
    .header-mobile {
        background: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460);
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
    
    .header-mobile::before {
        content: '📱';
        position: absolute;
        right: -20px;
        top: -20px;
        font-size: 150px;
        opacity: 0.05;
    }
    
    .header-mobile h1 {
        margin: 0;
        font-size: 1.8rem;
        font-weight: 900;
        position: relative;
        z-index: 1;
    }
    
    .header-mobile .subtitle {
        opacity: 0.8;
        font-size: 0.9rem;
        position: relative;
        z-index: 1;
    }
    
    .header-mobile .time-display {
        font-size: 1rem;
        background: rgba(255,255,255,0.1);
        padding: 8px 20px;
        border-radius: 25px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Product Card */
    .product-card-mobile {
        background: white;
        border-radius: 16px;
        padding: 18px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        transition: all 0.3s ease;
        border: 2px solid transparent;
        position: relative;
        height: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        cursor: pointer;
    }
    
    .product-card-mobile:hover {
        transform: translateY(-6px) scale(1.02);
        box-shadow: 0 12px 40px rgba(15,52,96,0.15);
        border-color: #0f3460;
    }
    
    .product-card-mobile .p-icon {
        font-size: 3.5rem;
        margin-bottom: 8px;
    }
    
    .product-card-mobile .p-name {
        font-weight: 700;
        font-size: 1rem;
        color: #1a1a2e;
        text-align: center;
    }
    
    .product-card-mobile .p-brand {
        font-size: 0.8rem;
        color: #666;
    }
    
    .product-card-mobile .p-price {
        color: #0f3460;
        font-weight: 900;
        font-size: 1.3rem;
        margin: 5px 0;
    }
    
    .product-card-mobile .p-stock {
        position: absolute;
        top: 10px;
        right: 10px;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 700;
    }
    
    .p-stock.out { background: #ff6b6b; color: white; }
    .p-stock.low { background: #ffd93d; color: #333; }
    .p-stock.medium { background: #ffa94d; color: white; }
    .p-stock.high { background: #6bcb77; color: white; }
    
    .product-card-mobile .p-discount {
        position: absolute;
        top: 10px;
        left: 10px;
        background: linear-gradient(135deg, #ff4757, #ff6b81);
        color: white;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 800;
        box-shadow: 0 2px 10px rgba(255,71,87,0.3);
    }
    
    .product-card-mobile .p-badge {
        background: #0f3460;
        color: white;
        padding: 2px 10px;
        border-radius: 10px;
        font-size: 0.6rem;
        margin-top: 3px;
    }
    
    /* Cart */
    .cart-mobile {
        background: white;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        max-height: 750px;
        overflow-y: auto;
        position: sticky;
        top: 20px;
    }
    
    .cart-mobile .cart-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 0;
        border-bottom: 1px solid #f0f0f0;
    }
    
    .cart-mobile .item-details {
        display: flex;
        flex-direction: column;
    }
    
    .cart-mobile .item-name {
        font-weight: 600;
        font-size: 0.95rem;
    }
    
    .cart-mobile .item-meta {
        font-size: 0.8rem;
        color: #888;
    }
    
    .cart-mobile .item-total {
        font-weight: 700;
        color: #0f3460;
        font-size: 1rem;
    }
    
    .cart-mobile .cart-total-box {
        background: linear-gradient(135deg, #1a1a2e, #0f3460);
        color: white;
        padding: 20px;
        border-radius: 14px;
        margin-top: 20px;
        box-shadow: 0 4px 20px rgba(15,52,96,0.3);
    }
    
    .cart-mobile .cart-total-box .total-row {
        display: flex;
        justify-content: space-between;
        padding: 5px 0;
        font-size: 0.95rem;
    }
    
    .cart-mobile .cart-total-box .grand-total {
        border-top: 2px solid rgba(255,255,255,0.2);
        padding-top: 12px;
        margin-top: 12px;
        font-size: 1.4rem;
        font-weight: 900;
        display: flex;
        justify-content: space-between;
    }
    
    /* Category Tabs */
    .category-tabs-mobile {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin: 15px 0;
        padding: 15px;
        background: white;
        border-radius: 14px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.04);
    }
    
    .category-tabs-mobile .cat-btn {
        padding: 8px 22px;
        border-radius: 25px;
        border: 2px solid #e0e0e0;
        background: white;
        cursor: pointer;
        transition: 0.3s;
        font-weight: 600;
        font-size: 0.85rem;
    }
    
    .category-tabs-mobile .cat-btn:hover {
        background: #0f3460;
        color: white;
        border-color: #0f3460;
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(15,52,96,0.2);
    }
    
    .category-tabs-mobile .cat-btn.active {
        background: #0f3460;
        color: white;
        border-color: #0f3460;
        box-shadow: 0 4px 15px rgba(15,52,96,0.3);
    }
    
    /* Receipt */
    .receipt-mobile {
        background: white;
        padding: 25px;
        border-radius: 16px;
        box-shadow: 0 8px 40px rgba(0,0,0,0.12);
        max-width: 380px;
        margin: 0 auto;
        font-family: 'Courier New', monospace;
        border: 2px solid #e0e0e0;
    }
    
    .receipt-mobile .r-header {
        text-align: center;
        border-bottom: 2px dashed #ddd;
        padding-bottom: 15px;
        margin-bottom: 15px;
    }
    
    .receipt-mobile .r-header h3 {
        margin: 0;
        font-size: 1.1rem;
        color: #0f3460;
    }
    
    .receipt-mobile .r-item {
        display: flex;
        justify-content: space-between;
        padding: 4px 0;
        font-size: 0.85rem;
    }
    
    .receipt-mobile .r-total {
        border-top: 2px solid #000;
        padding-top: 12px;
        margin-top: 12px;
        font-weight: 800;
        font-size: 1.1rem;
    }
    
    .receipt-mobile .r-footer {
        text-align: center;
        border-top: 2px dashed #ddd;
        padding-top: 15px;
        margin-top: 15px;
        font-size: 0.8rem;
        color: #666;
    }
    
    /* Metrics */
    .metric-mobile {
        background: white;
        padding: 20px;
        border-radius: 14px;
        text-align: center;
        box-shadow: 0 2px 12px rgba(0,0,0,0.05);
        transition: 0.3s;
        border-bottom: 4px solid #0f3460;
    }
    
    .metric-mobile:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.1);
    }
    
    .metric-mobile .metric-value {
        font-size: 2rem;
        font-weight: 900;
        color: #0f3460;
    }
    
    .metric-mobile .metric-label {
        font-size: 0.85rem;
        color: #666;
        margin-top: 5px;
    }
    
    /* Status Badges */
    .badge-pending {
        background: #ffd93d;
        color: #333;
        padding: 3px 12px;
        border-radius: 12px;
        font-size: 0.7rem;
        font-weight: 700;
    }
    
    .badge-in-progress {
        background: #ffa94d;
        color: white;
        padding: 3px 12px;
        border-radius: 12px;
        font-size: 0.7rem;
        font-weight: 700;
    }
    
    .badge-done {
        background: #6bcb77;
        color: white;
        padding: 3px 12px;
        border-radius: 12px;
        font-size: 0.7rem;
        font-weight: 700;
    }
    
    .badge-delivered {
        background: #0f3460;
        color: white;
        padding: 3px 12px;
        border-radius: 12px;
        font-size: 0.7rem;
        font-weight: 700;
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
    
    /* Animations */
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .slide-in {
        animation: slideIn 0.5s ease;
    }
</style>
""", unsafe_allow_html=True)

# -------------------- بارکردنی داتا --------------------
data = load_data()

# -------------------- Session State --------------------
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
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = 'grid'
if 'imei_input' not in st.session_state:
    st.session_state.imei_input = ''
if 'selected_repair' not in st.session_state:
    st.session_state.selected_repair = None

# -------------------- فەنکشنەکانی فرۆشتن --------------------
def add_to_cart(product: Dict, qty: int = 1) -> bool:
    if product['stock'] < qty:
        st.error(f"⚠️ کۆتای {product['name']} ناکافیە! تەنها {product['stock']} ماوە")
        return False
    
    for item in st.session_state.cart:
        if item['product_id'] == product['id']:
            if product['stock'] < item['qty'] + qty:
                st.error(f"⚠️ کۆتای ناکافیە! تەنها {product['stock'] - item['qty']} تر")
                return False
            item['qty'] += qty
            item['total'] = item['price'] * item['qty']
            item['discount_amount'] = item['price'] * item['qty'] * (item.get('discount', 0) / 100)
            item['taxable'] = item['price'] * item['qty'] * (1 - item.get('discount', 0) / 100)
            st.success(f"✅ {product['name']} زیاد کرا ({item['qty']})")
            return True
    
    st.session_state.cart.append({
        'product_id': product['id'],
        'name': product['name'],
        'brand': product.get('brand', ''),
        'price': product['price'],
        'qty': qty,
        'total': product['price'] * qty,
        'icon': product.get('icon', '📱'),
        'barcode': product.get('barcode', ''),
        'discount': product.get('discount', 0),
        'discount_amount': product['price'] * qty * (product.get('discount', 0) / 100),
        'taxable': product['price'] * qty * (1 - product.get('discount', 0) / 100),
        'category': product.get('category', 'مۆبایل'),
        'serial_number': product.get('serial_number', ''),
        'warranty_months': product.get('warranty_months', 12)
    })
    st.success(f"✅ {qty} x {product['name']} زیاد کرا")
    return True

def complete_sale(payment_method: str = 'نقدی') -> bool:
    if not st.session_state.cart:
        st.warning("⚠️ سەبەتە بەتاڵە")
        return False
    
    totals = calculate_cart_totals(st.session_state.cart)
    
    sale = {
        'id': f"SL{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(10,99)}",
        'items': st.session_state.cart.copy(),
        'subtotal': totals['subtotal'],
        'tax': totals['tax'],
        'discount': totals['discount'],
        'total': totals['total'],
        'payment_method': payment_method,
        'customer_id': st.session_state.current_customer.get('id', '') if st.session_state.current_customer else '',
        'customer_name': st.session_state.current_customer.get('name', '') if st.session_state.current_customer else '',
        'customer_phone': st.session_state.current_customer.get('phone', '') if st.session_state.current_customer else '',
        'cashier_id': st.session_state.current_user.get('id', '') if st.session_state.current_user else '',
        'cashier_name': st.session_state.current_user.get('full_name', '') if st.session_state.current_user else '',
        'date': datetime.now().isoformat(),
        'status': 'completed',
        'notes': '',
        'device_imei': st.session_state.imei_input if st.session_state.imei_input else '',
        'warranty_start': datetime.now().isoformat(),
        'warranty_end': (datetime.now() + timedelta(days=365)).isoformat()
    }
    
    # Update inventory
    for cart_item in st.session_state.cart:
        for product in data['products']:
            if product['id'] == cart_item['product_id']:
                old_stock = product['stock']
                product['stock'] -= cart_item['qty']
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
    
    # Update customer
    if st.session_state.current_customer:
        customer = st.session_state.current_customer
        customer['total_spent'] += totals['total']
        customer['total_purchases'] += 1
        customer['loyalty_points'] += int(totals['total'] * data['settings']['loyalty_points_rate'])
        customer['last_purchase'] = datetime.now().isoformat()
        if customer['total_spent'] >= 1000000:
            customer['tier'] = 'پلاتینیوم'
        elif customer['total_spent'] >= 500000:
            customer['tier'] = 'زێر'
        elif customer['total_spent'] >= 100000:
            customer['tier'] = 'نقره‌'
        else:
            customer['tier'] = 'برۆنزی'
    
    # Save IMEI
    if st.session_state.imei_input and validate_imei(st.session_state.imei_input):
        data['imei_tracker'][st.session_state.imei_input] = {
            'product_id': cart_item['product_id'] if cart_item else '',
            'sale_id': sale['id'],
            'customer_id': st.session_state.current_customer.get('id', '') if st.session_state.current_customer else '',
            'sale_date': datetime.now().isoformat(),
            'status': 'sold'
        }
    
    data['sales'].append(sale)
    data['counter'] += 1
    save_data(data)
    
    log_audit('sale_completed', 
              st.session_state.current_user.get('username', 'unknown') if st.session_state.current_user else 'unknown',
              f"Sale {sale['id']} - {format_currency(totals['total'])}")
    
    st.session_state.receipt_data = {
        'sale': sale,
        'totals': totals,
        'customer': st.session_state.current_customer
    }
    st.session_state.show_receipt = True
    
    st.session_state.cart = []
    st.session_state.imei_input = ''
    
    st.balloons()
    st.success("🎉 فرۆشتن تەواو بوو!")
    return True

# -------------------- Header --------------------
st.markdown(f"""
    <div class="header-mobile slide-in">
        <div>
            <h1>📱 {data['settings']['shop_name']}</h1>
            <div class="subtitle">سیستەمی کاشێری مۆبایل - پیشەیی</div>
            <div style="font-size:0.8rem; opacity:0.6; margin-top:5px;">
                {datetime.now().strftime('%A, %B %d, %Y')}
            </div>
        </div>
        <div class="time-display">
            ⏰ {datetime.now().strftime('%H:%M:%S')}
        </div>
    </div>
""", unsafe_allow_html=True)

# -------------------- Sidebar - Admin --------------------
with st.sidebar:
    st.markdown("""
        <div style="text-align:center; padding:15px 0; background:linear-gradient(135deg,#1a1a2e,#0f3460); border-radius:14px; margin-bottom:20px;">
            <h3 style="color:white; margin:0;">⚙️ بەڕێوەبردنی کۆگا</h3>
            <p style="color:rgba(255,255,255,0.6); font-size:0.8rem; margin:5px 0 0 0;">دووکانی مۆبایل</p>
        </div>
    """, unsafe_allow_html=True)
    
    admin_section = st.radio(
        "بەشەکان",
        ["📊 داشبۆرد", "📦 کاڵا", "👥 دروستکەر", "🔧 چاکسازی", "📊 ڕاپۆرت", "⚙️ کۆنفیگ"],
        label_visibility="collapsed"
    )
    
    # ==================== DASHBOARD ====================
    if admin_section == "📊 داشبۆرد":
        st.markdown("### 📊 داشبۆرد")
        
        total_products = len(data['products'])
        total_sales = len(data['sales'])
        total_revenue = sum(s['total'] for s in data['sales'])
        total_customers = len(data['customers'])
        total_repairs = len(data.get('repair_orders', []))
        low_stock = len([p for p in data['products'] if p['stock'] < p.get('min_stock', 5)])
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📦 کاڵا", total_products, f"{low_stock} کەم")
        with col2:
            st.metric("🧾 فرۆشتن", total_sales)
        
        col3, col4 = st.columns(2)
        with col3:
            st.metric("💰 داهات", format_currency(total_revenue))
        with col4:
            st.metric("👥 دروستکەر", total_customers)
        
        st.markdown("---")
        st.metric("🔧 چاکسازی", total_repairs)
        
        today = datetime.now().date()
        today_sales = [s for s in data['sales'] if datetime.fromisoformat(s['date']).date() == today]
        st.metric("📅 ئەمڕۆ", f"{len(today_sales)} فرۆشتن", f"{format_currency(sum(s['total'] for s in today_sales))}")
        
        if st.button("🔄 نوێکردنەوە", use_container_width=True):
            st.rerun()
    
    # ==================== PRODUCTS ====================
    elif admin_section == "📦 کاڵا":
        st.markdown("### 📦 کاڵا")
        
        with st.expander("➕ زیادکردنی کاڵا", expanded=False):
            with st.form("add_product_mobile", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("🏷️ ناو", placeholder="ناوی مۆبایل یان ئیکسسوارات")
                    brand = st.text_input("🏢 براند", placeholder="Apple, Samsung, Huawei...")
                    model = st.text_input("📱 مۆدێل", placeholder="iPhone 15, S24...")
                    price = st.number_input("💰 نرخ", min_value=100, value=50000, step=1000)
                    cost_price = st.number_input("📊 نخی کڕین", min_value=0, value=int(price*0.7), step=1000)
                with col2:
                    category = st.selectbox("📂 پۆل", ["مۆبایل", "ئیکسسوارات", "نۆرم", "بەکارهاتوو"])
                    subcategory = st.text_input("📁 پۆلی بچووک", placeholder="شارژەر، کێس، گوێهێڵ...")
                    color = st.text_input("🎨 ڕەنگ")
                    storage = st.selectbox("💾 بیرگە", ["", "64GB", "128GB", "256GB", "512GB", "1TB"])
                    ram = st.selectbox("🧠 RAM", ["", "4GB", "6GB", "8GB", "12GB", "16GB"])
                
                col3, col4 = st.columns(2)
                with col3:
                    stock = st.number_input("📦 کۆتا", min_value=0, value=5, step=1)
                    min_stock = st.number_input("⚠️ کەمترین کۆتا", min_value=1, value=3, step=1)
                    serial_number = st.text_input("🔢 ژمارەی زنجیرەیی", placeholder="SN...")
                with col4:
                    warranty = st.number_input("🛡️ گارانتی (مانگ)", min_value=0, value=12, step=6)
                    discount = st.slider("🏷️ دەسکەونت (%)", 0, 80, 0, 5)
                    condition = st.selectbox("دۆخ", ["نوێ", "بەکارهاتوو", "نۆرم"])
                    icon = st.selectbox("🎨 ئایکۆن", ["📱", "📲", "⌚", "🎧", "📷", "🔋", "📶", "🔄"])
                
                supplier = st.text_input("🏢 دابینکەر")
                description = st.text_area("📝 وەسف", height=60, placeholder="تایبەتمەندییەکان...")
                
                if st.form_submit_button("➕ زیادکردن", use_container_width=True, type="primary"):
                    if name and price > 0:
                        product = {
                            'id': f"PRD{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(100,999)}",
                            'name': name,
                            'brand': brand,
                            'model': model,
                            'price': price,
                            'cost_price': cost_price,
                            'category': category,
                            'subcategory': subcategory,
                            'stock': stock,
                            'min_stock': min_stock,
                            'barcode': generate_barcode(),
                            'serial_number': serial_number,
                            'warranty_months': warranty,
                            'color': color,
                            'storage': storage,
                            'ram': ram,
                            'condition': condition,
                            'supplier': supplier,
                            'discount': discount/100,
                            'tax_rate': 0,
                            'icon': icon,
                            'description': description,
                            'created_at': datetime.now().isoformat(),
                            'updated_at': datetime.now().isoformat()
                        }
                        data['products'].append(product)
                        save_data(data)
                        st.success(f"✅ {name} زیاد کرا")
                        st.rerun()
        
        st.markdown("#### 📋 لیستی کاڵاکان")
        
        search = st.text_input("🔍 گەڕان", placeholder="ناو، براند، بارکۆد...")
        
        filtered = data['products']
        if search:
            filtered = [p for p in filtered if search.lower() in p['name'].lower() or 
                       search.lower() in p.get('brand', '').lower() or
                       search in p.get('barcode', '')]
        
        if filtered:
            for product in filtered:
                stock_status, _, _ = get_stock_status(product['stock'], product.get('min_stock', 5))
                col1, col2, col3, col4, col5 = st.columns([2, 1.5, 1.5, 1, 0.8])
                with col1:
                    st.write(f"{product.get('icon', '📱')} **{product['name']}**")
                    st.caption(f"{product.get('brand', '')} {product.get('model', '')}")
                with col2:
                    st.write(f"{format_currency(product['price'])}")
                    st.caption(f"کۆتا: {product['stock']}")
                with col3:
                    status_color = {'high': '🟢', 'medium': '🟡', 'low': '🟠', 'out': '🔴'}.get(stock_status, '⚪')
                    st.write(f"{status_color} {product.get('min_stock', 5)}")
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
    
    # ==================== CUSTOMERS ====================
    elif admin_section == "👥 دروستکەر":
        st.markdown("### 👥 دروستکەر")
        
        with st.expander("➕ زیادکردن", expanded=False):
            with st.form("add_customer_mobile"):
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("📛 ناو")
                    phone = st.text_input("📱 ژمارە")
                with col2:
                    email = st.text_input("📧 ئیمەیڵ")
                    address = st.text_input("📍 ناونیشان")
                
                if st.form_submit_button("➕ زیادکردن", use_container_width=True):
                    if name and phone:
                        customer = {
                            'id': f"CUS{datetime.now().strftime('%Y%m%d')}{random.randint(100,999)}",
                            'name': name,
                            'phone': phone,
                            'email': email,
                            'address': address,
                            'loyalty_points': 0,
                            'total_spent': 0,
                            'total_purchases': 0,
                            'tier': 'برۆنزی',
                            'registered_at': datetime.now().isoformat(),
                            'last_purchase': '',
                            'notes': ''
                        }
                        data['customers'].append(customer)
                        save_data(data)
                        st.success(f"✅ {name} زیاد کرا")
                        st.rerun()
        
        st.markdown("#### 📋 لیست")
        search_cust = st.text_input("🔍 گەڕان")
        
        customers = data['customers']
        if search_cust:
            customers = [c for c in customers if search_cust.lower() in c['name'].lower() or search_cust in c.get('phone', '')]
        
        for customer in customers:
            tier_icons = {'پلاتینیوم': '💎', 'زێر': '🥇', 'نقره‌': '🥈', 'برۆنزی': '🥉'}
            col1, col2, col3, col4 = st.columns([2, 1.5, 1.5, 1])
            with col1:
                st.write(f"**{customer['name']}**")
                st.caption(f"📱 {customer.get('phone', '')}")
            with col2:
                st.write(f"{tier_icons.get(customer.get('tier', 'برۆنزی'), '⭐')} {customer.get('tier', 'برۆنزی')}")
                st.caption(f"⭐ {customer.get('loyalty_points', 0)} خاڵ")
            with col3:
                st.write(f"💰 {format_currency(customer.get('total_spent', 0))}")
            with col4:
                if st.button("انتخاب", key=f"sel_{customer['id']}"):
                    st.session_state.current_customer = customer
                    st.success(f"✅ {customer['name']} هەڵبژێردرا")
                    st.rerun()
            st.divider()
    
    # ==================== REPAIRS ====================
    elif admin_section == "🔧 چاکسازی":
        st.markdown("### 🔧 چاکسازی")
        
        with st.expander("➕ داواکاری چاکسازی", expanded=False):
            with st.form("add_repair"):
                col1, col2 = st.columns(2)
                with col1:
                    customer_name = st.text_input("👤 ناوی دروستکەر")
                    customer_phone = st.text_input("📱 ژمارە")
                    device_model = st.text_input("📱 مۆدێلی مۆبایل")
                with col2:
                    device_imei = st.text_input("🔢 IMEI")
                    device_color = st.text_input("🎨 ڕەنگ")
                    problem = st.text_area("🛠️ کێشە", height=60)
                
                st.write("#### خزمەتگوزارییەکان")
                services = []
                for i in range(3):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        s_name = st.text_input(f"ناو {i+1}", key=f"s_name_{i}")
                    with col2:
                        s_price = st.number_input(f"نرخ {i+1}", min_value=0, value=5000, key=f"s_price_{i}")
                    with col3:
                        s_duration = st.text_input(f"ماوە {i+1}", key=f"s_dur_{i}", placeholder="٢ کاتژمێر")
                    if s_name:
                        services.append({'name': s_name, 'price': s_price, 'duration': s_duration})
                
                notes = st.text_area("📝 تێبینی", height=60)
                
                if st.form_submit_button("➕ دروستکردن", use_container_width=True, type="primary"):
                    if customer_name and device_model:
                        total = sum(s['price'] for s in services)
                        repair = {
                            'id': f"REP{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(10,99)}",
                            'customer_name': customer_name,
                            'customer_phone': customer_phone,
                            'device_model': device_model,
                            'device_imei': device_imei,
                            'device_color': device_color,
                            'problem': problem,
                            'services': services,
                            'total': total,
                            'status': 'pending',
                            'notes': notes,
                            'created_at': datetime.now().isoformat(),
                            'updated_at': datetime.now().isoformat(),
                            'done_at': '',
                            'delivered_at': ''
                        }
                        data['repair_orders'].append(repair)
                        save_data(data)
                        st.success(f"✅ داواکاری چاکسازی دروست کرا - {format_currency(total)}")
                        st.rerun()
        
        st.markdown("#### 📋 داواکارییەکان")
        
        repairs = data.get('repair_orders', [])
        status_filter = st.selectbox("دۆخ", ["هموو", "pending", "in_progress", "done", "delivered"])
        if status_filter != "هموو":
            repairs = [r for r in repairs if r['status'] == status_filter]
        
        for repair in repairs:
            status_icons = {'pending': '🟡', 'in_progress': '🟠', 'done': '🟢', 'delivered': '🔵'}
            status_labels = {'pending': 'چاوەڕوان', 'in_progress': 'لە جێبەجێکردندایە', 'done': 'تەواو', 'delivered': 'دەستپێگەیشت'}
            
            col1, col2, col3, col4 = st.columns([2, 1.5, 1.5, 1])
            with col1:
                st.write(f"**{repair['customer_name']}**")
                st.caption(f"📱 {repair['device_model']}")
            with col2:
                st.write(f"{status_icons.get(repair['status'], '⚪')} {status_labels.get(repair['status'], repair['status'])}")
                st.caption(f"📅 {repair['created_at'][:10]}")
            with col3:
                st.write(f"💰 {format_currency(repair['total'])}")
            with col4:
                if repair['status'] == 'pending':
                    if st.button("▶️ دەستپێبکە", key=f"start_{repair['id']}"):
                        repair['status'] = 'in_progress'
                        repair['updated_at'] = datetime.now().isoformat()
                        save_data(data)
                        st.rerun()
                elif repair['status'] == 'in_progress':
                    if st.button("✅ تەواو", key=f"done_{repair['id']}"):
                        repair['status'] = 'done'
                        repair['done_at'] = datetime.now().isoformat()
                        repair['updated_at'] = datetime.now().isoformat()
                        save_data(data)
                        st.rerun()
                elif repair['status'] == 'done':
                    if st.button("📦 دەستپێگەیشت", key=f"deliver_{repair['id']}"):
                        repair['status'] = 'delivered'
                        repair['delivered_at'] = datetime.now().isoformat()
                        repair['updated_at'] = datetime.now().isoformat()
                        save_data(data)
                        st.rerun()
            st.divider()
    
    # ==================== REPORTS ====================
    elif admin_section == "📊 ڕاپۆرت":
        st.markdown("### 📊 ڕاپۆرت")
        
        if data['sales']:
            df = pd.DataFrame(data['sales'])
            df['date'] = pd.to_datetime(df['date'])
            
            total_revenue = df['total'].sum()
            total_sales = len(df)
            avg_sale = df['total'].mean()
            
            col1, col2, col3 = st.columns(3)
            col1.metric("💰 داهات", format_currency(total_revenue))
            col2.metric("🧾 فرۆشتن", total_sales)
            col3.metric("📊 تێکڕا", format_currency(avg_sale))
            
            st.markdown("#### 📈 داهاتی ڕۆژانە")
            daily = df.groupby(df['date'].dt.date)['total'].sum().reset_index()
            fig = px.bar(daily, x='date', y='total', title='داهاتی ڕۆژانە')
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("#### 💳 شێوەی پارەدان")
            payment_counts = df['payment_method'].value_counts().reset_index()
            payment_counts.columns = ['شێوە', 'ژمارە']
            fig = px.pie(payment_counts, values='ژمارە', names='شێوە', title='پارەدان')
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
            
            csv = df[['id', 'date', 'total', 'payment_method']].to_csv(index=False).encode('utf-8')
            st.download_button("📥 دابەزاندن", csv, f"report_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv", use_container_width=True)
        else:
            st.info("هیچ فرۆشتنێک نیە")
    
    # ==================== SETTINGS ====================
    elif admin_section == "⚙️ کۆنفیگ":
        st.markdown("### ⚙️ کۆنفیگ")
        
        shop_name = st.text_input("🏪 ناوی دووکان", data['settings']['shop_name'])
        currency = st.text_input("💰 دراو", data['settings']['currency'])
        tax_rate = st.slider("📊 باج", 0.0, 0.30, data['settings']['tax_rate'], 0.01)
        loyalty_rate = st.slider("⭐ خاڵی دڵسۆزی", 0.0, 0.05, data['settings']['loyalty_points_rate'], 0.001)
        warranty_default = st.number_input("🛡️ گارانتی بنەڕەت (مانگ)", min_value=0, value=data['settings']['warranty_default'], step=1)
        footer = st.text_area("📝 پێنووسی وەچە", data['settings']['receipt_footer'])
        
        if st.button("💾 هەڵگرتن", use_container_width=True, type="primary"):
            data['settings']['shop_name'] = shop_name
            data['settings']['currency'] = currency
            data['settings']['tax_rate'] = tax_rate
            data['settings']['loyalty_points_rate'] = loyalty_rate
            data['settings']['warranty_default'] = warranty_default
            data['settings']['receipt_footer'] = footer
            save_data(data)
            st.success("✅ کۆنفیگ هەڵگیرا")
            st.rerun()
        
        st.markdown("---")
        if st.button("🗑️ سڕینەوەی هەموو داتا", use_container_width=True):
            if st.checkbox("دڵنیای؟"):
                data['products'] = []
                data['sales'] = []
                data['customers'] = []
                data['repair_orders'] = []
                data['inventory_logs'] = []
                data['audit_logs'] = []
                data['counter'] = 0
                save_data(data)
                st.session_state.cart = []
                st.success("✅ سڕدرایەوە")
                st.rerun()

# ==================== MAIN POS ====================
pos_col1, pos_col2 = st.columns([2.2, 1])

with pos_col1:
    # Search
    col_s1, col_s2, col_s3 = st.columns([2, 1, 1])
    with col_s1:
        search = st.text_input("🔍 گەڕان", placeholder="ناو، براند، بارکۆد...", key="pos_search")
    with col_s2:
        if st.button("🔄 نوێ", use_container_width=True):
            st.rerun()
    with col_s3:
        view_toggle = st.button("📋 📊", use_container_width=True, help="گۆڕینی شێوە")
        if view_toggle:
            st.session_state.view_mode = 'list' if st.session_state.view_mode == 'grid' else 'grid'
    
    # Categories
    st.markdown('<div class="category-tabs-mobile">', unsafe_allow_html=True)
    all_cats = list(set(p.get('category', 'مۆبایل') for p in data['products']))
    cats = ['هموو'] + sorted(all_cats)
    for cat in cats[:6]:
        if st.button(cat, key=f"cat_{cat}", use_container_width=True,
                    type="primary" if st.session_state.selected_category == cat else "secondary"):
            st.session_state.selected_category = cat
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Products
    filtered = data['products']
    if st.session_state.selected_category != 'هموو':
        filtered = [p for p in filtered if p.get('category', 'مۆبایل') == st.session_state.selected_category]
    if search:
        filtered = [p for p in filtered if search.lower() in p['name'].lower() or 
                   search.lower() in p.get('brand', '').lower() or
                   search in p.get('barcode', '')]
    
    if filtered:
        per_page = 12 if st.session_state.view_mode == 'grid' else 20
        total_pages = (len(filtered) + per_page - 1) // per_page
        page = st.number_input('', min_value=1, max_value=total_pages, value=1, label_visibility='collapsed', key='pos_page')
        start_idx = (page - 1) * per_page
        end_idx = min(start_idx + per_page, len(filtered))
        
        if st.session_state.view_mode == 'grid':
            cols = st.columns(4)
            for idx, product in enumerate(filtered[start_idx:end_idx]):
                with cols[idx % 4]:
                    stock_status, stock_label, _ = get_stock_status(product['stock'], product.get('min_stock', 5))
                    discount = product.get('discount', 0)
                    
                    st.markdown(f"""
                        <div class="product-card-mobile">
                            <div class="p-icon">{product.get('icon', '📱')}</div>
                            <div class="p-name">{product['name'][:20]}</div>
                            <div class="p-brand">{product.get('brand', '')} {product.get('model', '')}</div>
                            <div class="p-price">{format_currency(product['price'])}</div>
                            <div class="p-stock {stock_status}">{stock_label}</div>
                            {f'<div class="p-discount">-{int(discount*100)}%</div>' if discount > 0 else ''}
                            <div class="p-badge">{product.get('storage', '')} {product.get('ram', '')}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    qty = st.number_input('ژ', min_value=1, max_value=product['stock'] if product['stock'] > 0 else 1,
                                        value=1, step=1, key=f"qty_{product['id']}", label_visibility='collapsed')
                    if st.button('➕ زیاد', key=f"add_{product['id']}", use_container_width=True,
                               disabled=product['stock'] <= 0):
                        add_to_cart(product, qty)
                        st.rerun()
        else:
            for product in filtered[start_idx:end_idx]:
                stock_status, stock_label, _ = get_stock_status(product['stock'], product.get('min_stock', 5))
                col1, col2, col3, col4, col5 = st.columns([2, 1.5, 1, 1, 1])
                with col1:
                    st.write(f"{product.get('icon', '📱')} **{product['name']}**")
                    st.caption(f"{product.get('brand', '')} {product.get('model', '')}")
                with col2:
                    st.write(f"**{format_currency(product['price'])}**")
                with col3:
                    status_color = {'high': '🟢', 'medium': '🟡', 'low': '🟠', 'out': '🔴'}.get(stock_status, '⚪')
                    st.write(f"{status_color} {product['stock']}")
                with col4:
                    if product.get('discount', 0) > 0:
                        st.write(f"🏷️ -{int(product['discount']*100)}%")
                with col5:
                    qty = st.number_input('ژ', min_value=1, max_value=product['stock'] if product['stock'] > 0 else 1,
                                        value=1, step=1, key=f"qty_list_{product['id']}", label_visibility='collapsed')
                    if st.button('➕', key=f"add_list_{product['id']}", disabled=product['stock'] <= 0):
                        add_to_cart(product, qty)
                        st.rerun()
                st.divider()
    else:
        st.warning("هیچ کاڵایەک نەدۆزرایەوە")

with pos_col2:
    st.markdown('<div class="cart-mobile">', unsafe_allow_html=True)
    st.subheader("🛒 سەبەتە")
    
    if st.session_state.current_customer:
        st.info(f"👤 {st.session_state.current_customer['name']} | ⭐ {st.session_state.current_customer.get('loyalty_points', 0)}")
    
    # IMEI Input
    if data['settings']['imei_required']:
        imei = st.text_input("🔢 IMEI", placeholder="١٥ ژمارە", key="imei_input",
                            help="ژمارەی IMEI ی مۆبایلەکە داخل بکە")
        if imei and not validate_imei(imei):
            st.warning("⚠️ IMEI دەبێت ١٥ ژمارە بێت")
    
    if st.session_state.cart:
        totals = calculate_cart_totals(st.session_state.cart)
        
        for idx, item in enumerate(st.session_state.cart):
            st.markdown(f"""
                <div class="cart-item">
                    <div class="item-details">
                        <span class="item-name">{item.get('icon', '📱')} {item['name']}</span>
                        <span class="item-meta">{item['qty']} × {format_currency(item['price'])}</span>
                    </div>
                    <div style="display:flex; align-items:center; gap:8px;">
                        <span class="item-total">{format_currency(item['total'])}</span>
                        <button onclick="alert('سڕدرایەوە')" style="background:none; border:none; color:#ff6b6b; cursor:pointer; font-size:1.2rem;">✕</button>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"🗑️", key=f"remove_{idx}"):
                st.session_state.cart.pop(idx)
                st.rerun()
        
        st.markdown(f"""
            <div class="cart-total-box">
                <div class="total-row"><span>کۆی گشتی:</span><span>{format_currency(totals['subtotal'])}</span></div>
                <div class="total-row" style="color:#ffd93d;"><span>دەسکەونت:</span><span>-{format_currency(totals['discount'])}</span></div>
                <div class="grand-total"><span>💰 کۆی گشتی:</span><span>{format_currency(totals['total'])}</span></div>
            </div>
        """, unsafe_allow_html=True)
        
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            if st.button("💵 نقدی", use_container_width=True, type="primary"):
                if imei and not validate_imei(imei):
                    st.error("⚠️ IMEI نادروستە")
                else:
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
        
        if st.button("🗑️ پاککردنەوە", use_container_width=True):
            st.session_state.cart = []
            st.rerun()
    else:
        st.markdown("""
            <div style="text-align:center; padding:40px 0; color:#999;">
                <div style="font-size:4rem;">🛍️</div>
                <p style="font-size:1.1rem; font-weight:600; color:#666;">سەبەتە بەتاڵە</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== RECEIPT ====================
if st.session_state.show_receipt and st.session_state.receipt_data:
    st.markdown("---")
    st.markdown("### 🧾 وەچە")
    
    rec = st.session_state.receipt_data
    sale = rec['sale']
    totals = rec['totals']
    customer = rec.get('customer')
    
    qr_data = f"Sale: {sale['id']}, Total: {totals['total']}, Date: {datetime.now()}"
    qr_base64 = generate_qr(qr_data)
    
    st.markdown(f"""
        <div class="receipt-mobile">
            <div class="r-header">
                <h3>📱 {data['settings']['shop_name']}</h3>
                <p style="margin:3px 0; font-size:0.8rem;">{datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
                <p style="margin:3px 0; font-weight:bold; color:#0f3460;"># {sale['id']}</p>
                {f'<p>👤 {customer["name"]}</p>' if customer else ''}
                <p style="font-size:0.7rem; color:#888;">💳 {sale['payment_method']}</p>
                {f'<p style="font-size:0.7rem; color:#888;">🔢 IMEI: {sale.get("device_imei", "")}</p>' if sale.get('device_imei') else ''}
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
            <div class="r-total">
                <span>💰 کۆی گشتی</span>
                <span>{format_currency(totals['total'])}</span>
            </div>
            {f'<div style="font-size:0.8rem; color:#888; border-top:1px dashed #ccc; padding-top:10px;">⭐ خاڵ: +{int(totals["total"] * data["settings"]["loyalty_points_rate"])}</div>' if customer else ''}
            <div class="r-footer">
                <img src="data:image/png;base64,{qr_base64}" style="width:60px; height:60px; margin:5px auto; display:block;">
                {data['settings']['receipt_footer']}
                <br>🛡️ گارانتی {sale.get('warranty_start', '')[:10]} - {sale.get('warranty_end', '')[:10]}
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("✕ داخستن", use_container_width=True):
        st.session_state.show_receipt = False
        st.session_state.receipt_data = None
        st.rerun()

# ==================== FOOTER ====================
st.markdown("""
    <hr style="margin:30px 0 20px 0; border:none; height:2px; background:linear-gradient(to right, transparent, #0f3460, transparent);">
    <div style="text-align:center; color:#999; font-size:0.8rem; padding-bottom:20px;">
        <p>📱 دووکانی مۆبایل - کاشێری پیشەیی</p>
        <p style="font-size:0.7rem; opacity:0.6;">وەشانی 5.0 | 3000+ هێڵی کۆد</p>
    </div>
""", unsafe_allow_html=True)
