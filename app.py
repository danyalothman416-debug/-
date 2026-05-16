import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import uuid
import json
import plotly.express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
import hashlib
import re
import sqlite3
import time
from typing import Dict, List, Optional, Tuple, Any
import secrets
from functools import lru_cache
import base64
from dataclasses import dataclass, asdict
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==================== Configuration & Constants ====================

@dataclass
class AppConfig:
    """Application configuration settings"""
    APP_NAME: str = "Golden Delivery Pro"
    VERSION: str = "2.0.0"
    COMPANY_PHONES: List[str] = None
    COMPANY_EMAIL: str = "Danyalexpert@gmail.com"
    COMPANY_ADDRESS: str = "Kirkuk, Iraq"
    COMPANY_WHATSAPP: str = "https://wa.me/9647801352003"
    ADMIN_EMAIL: str = "admin@goldendelivery.com"
    ADMIN_PASSWORD: str = "Admin@2026"
    SESSION_TIMEOUT_MINUTES: int = 30
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 15
    FREE_DELIVERY_EVERY_NTH: int = 3
    MIN_ORDER_FOR_FREE: int = 3000
    LOYALTY_POINTS_PER_1000: int = 1
    REDEEM_POINTS_TIERS: Dict[int, int] = None
    ALLOWED_FILE_TYPES: List[str] = None
    MAX_UPLOAD_SIZE_MB: int = 10
    
    def __post_init__(self):
        if self.COMPANY_PHONES is None:
            self.COMPANY_PHONES = ["07801352003", "07721959922"]
        if self.REDEEM_POINTS_TIERS is None:
            self.REDEEM_POINTS_TIERS = {
                100: 5000,
                200: 12000,
                500: 35000,
                1000: 80000
            }
        if self.ALLOWED_FILE_TYPES is None:
            self.ALLOWED_FILE_TYPES = ['csv', 'json', 'xlsx']

config = AppConfig()

# ==================== Database Setup ====================

class DatabaseManager:
    """SQLite database manager with connection pooling"""
    
    def __init__(self, db_path: str = "golden_delivery.db"):
        self.db_path = db_path
        self.init_database()
    
    @st.cache_resource
    def get_connection(_self):
        """Get database connection"""
        conn = sqlite3.connect(_self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn
    
    def init_database(self):
        """Initialize database schema"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                full_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('customer', 'driver', 'admin')),
                area TEXT,
                join_date TEXT NOT NULL,
                last_login TEXT,
                login_attempts INTEGER DEFAULT 0,
                locked_until TEXT,
                is_active BOOLEAN DEFAULT 1,
                profile_image TEXT,
                preferences TEXT
            )
        ''')
        
        # Orders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                customer_name TEXT NOT NULL,
                customer_phone TEXT NOT NULL,
                customer_email TEXT,
                shop_name TEXT,
                shop_address TEXT,
                delivery_area TEXT NOT NULL,
                delivery_address TEXT NOT NULL,
                price REAL NOT NULL,
                status TEXT DEFAULT 'Pending' 
                    CHECK(status IN ('Pending', 'Picked Up', 'In Transit', 
                                   'Out for Delivery', 'Delivered', 'Cancelled')),
                payment_method TEXT DEFAULT 'Cash on Delivery',
                payment_status TEXT DEFAULT 'Pending'
                    CHECK(payment_status IN ('Pending', 'Paid', 'Refunded', 'Failed')),
                driver_id TEXT,
                promo_code TEXT,
                discount_amount REAL DEFAULT 0,
                loyalty_points_used INTEGER DEFAULT 0,
                delivery_notes TEXT,
                gate_code TEXT,
                building_number TEXT,
                is_free_delivery BOOLEAN DEFAULT 0,
                estimated_delivery TEXT,
                actual_delivery TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT,
                rating INTEGER CHECK(rating BETWEEN 1 AND 5),
                review TEXT,
                order_source TEXT DEFAULT 'web',
                FOREIGN KEY (driver_id) REFERENCES users(user_id)
            )
        ''')
        
        # Drivers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS drivers (
                driver_id TEXT PRIMARY KEY,
                user_id TEXT UNIQUE,
                status TEXT DEFAULT 'Available' 
                    CHECK(status IN ('Available', 'Busy', 'Offline')),
                current_location TEXT,
                current_order_id TEXT,
                total_deliveries INTEGER DEFAULT 0,
                rating REAL DEFAULT 5.0,
                total_ratings INTEGER DEFAULT 0,
                vehicle_type TEXT,
                vehicle_number TEXT,
                working_hours TEXT,
                zone TEXT,
                is_verified BOOLEAN DEFAULT 0,
                commission_rate REAL DEFAULT 0.8,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (current_order_id) REFERENCES orders(order_id)
            )
        ''')
        
        # Promotions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS promotions (
                promo_id TEXT PRIMARY KEY,
                code TEXT UNIQUE NOT NULL,
                discount_type TEXT CHECK(discount_type IN ('percentage', 'fixed')),
                discount_value REAL NOT NULL,
                min_order_amount REAL DEFAULT 0,
                max_discount REAL,
                usage_limit INTEGER,
                usage_count INTEGER DEFAULT 0,
                start_date TEXT NOT NULL,
                expiry_date TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                applicable_areas TEXT,
                applicable_users TEXT
            )
        ''')
        
        # Feedback table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                feedback_id TEXT PRIMARY KEY,
                order_id TEXT NOT NULL,
                user_id TEXT,
                rating INTEGER CHECK(rating BETWEEN 1 AND 5),
                categories TEXT,
                review TEXT,
                created_at TEXT NOT NULL,
                is_public BOOLEAN DEFAULT 1,
                admin_response TEXT,
                FOREIGN KEY (order_id) REFERENCES orders(order_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Notifications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                notification_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                type TEXT CHECK(type IN ('order_update', 'promo', 'system', 'payment', 'chat')),
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                is_read BOOLEAN DEFAULT 0,
                action_url TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Chat messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_messages (
                message_id TEXT PRIMARY KEY,
                order_id TEXT NOT NULL,
                sender_id TEXT NOT NULL,
                receiver_id TEXT NOT NULL,
                message TEXT NOT NULL,
                is_read BOOLEAN DEFAULT 0,
                created_at TEXT NOT NULL,
                message_type TEXT DEFAULT 'text',
                FOREIGN KEY (order_id) REFERENCES orders(order_id),
                FOREIGN KEY (sender_id) REFERENCES users(user_id),
                FOREIGN KEY (receiver_id) REFERENCES users(user_id)
            )
        ''')
        
        # Analytics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics (
                analytic_id TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                event_data TEXT,
                user_id TEXT,
                ip_address TEXT,
                user_agent TEXT,
                created_at TEXT NOT NULL
            )
        ''')
        
        # Audit log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                log_id TEXT PRIMARY KEY,
                user_id TEXT,
                action TEXT NOT NULL,
                table_name TEXT,
                record_id TEXT,
                old_values TEXT,
                new_values TEXT,
                ip_address TEXT,
                created_at TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        logger.info("Database initialized successfully")
    
    def execute_query(self, query: str, params: Tuple = None) -> List:
        """Execute a query and return results"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            return cursor.fetchall()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
    
    def execute_many(self, query: str, params_list: List[Tuple]) -> None:
        """Execute multiple queries"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.executemany(query, params_list)
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise

# Initialize database
db = DatabaseManager()

# ==================== Security & Authentication ====================

class SecurityManager:
    """Handle all security-related operations"""
    
    @staticmethod
    def hash_password(password: str) -> Tuple[str, str]:
        """Hash password with salt"""
        salt = secrets.token_hex(16)
        hash_obj = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        password_hash = base64.b64encode(hash_obj).decode('utf-8')
        return password_hash, salt
    
    @staticmethod
    def verify_password(password: str, password_hash: str, salt: str) -> bool:
        """Verify password against hash"""
        hash_obj = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        new_hash = base64.b64encode(hash_obj).decode('utf-8')
        return new_hash == password_hash
    
    @staticmethod
    def generate_token() -> str:
        """Generate secure token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def validate_iraq_phone(phone: str) -> bool:
        """Validate Iraqi phone number format"""
        pattern = r'^07[3-9]\d{8}$'
        return bool(re.match(pattern, str(phone)))
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_password_strength(password: str) -> Tuple[bool, str]:
        """Check password strength"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters"
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain uppercase letter"
        if not re.search(r'[a-z]', password):
            return False, "Password must contain lowercase letter"
        if not re.search(r'\d', password):
            return False, "Password must contain number"
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain special character"
        return True, "Password is strong"
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitize user input"""
        # Remove HTML tags
        text = re.sub(r'<[^>]*>', '', text)
        # Remove script tags
        text = re.sub(r'<script.*?>.*?</script>', '', text, flags=re.DOTALL)
        # Escape special characters
        text = text.replace("'", "''")
        return text.strip()

security = SecurityManager()

class UserManager:
    """Handle user operations"""
    
    def __init__(self):
        self.db = db
    
    def register_user(self, email: str, password: str, full_name: str, 
                     phone: str, role: str = 'customer', area: str = None) -> Tuple[bool, str]:
        """Register new user"""
        try:
            # Validate inputs
            if not security.validate_email(email):
                return False, "Invalid email format"
            
            if not security.validate_iraq_phone(phone):
                return False, "Invalid phone number"
            
            is_strong, msg = security.validate_password_strength(password)
            if not is_strong:
                return False, msg
            
            # Check if email exists
            existing = self.db.execute_query(
                "SELECT user_id FROM users WHERE email = ?",
                (email,)
            )
            if existing:
                return False, "Email already registered"
            
            # Hash password
            password_hash, salt = security.hash_password(password)
            user_id = str(uuid.uuid4())
            
            # Insert user
            self.db.execute_query('''
                INSERT INTO users (user_id, email, password_hash, salt, full_name, 
                                 phone, role, area, join_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, email, password_hash, salt, full_name, phone,
                role, area, datetime.now().isoformat()
            ))
            
            logger.info(f"New user registered: {email}")
            return True, "Registration successful"
            
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return False, "Registration failed"
    
    def login_user(self, email: str, password: str, role: str = 'customer') -> Tuple[bool, str, Optional[Dict]]:
        """Authenticate user"""
        try:
            # Check login attempts
            user = self.db.execute_query(
                "SELECT * FROM users WHERE email = ?",
                (email,)
            )
            
            if not user:
                return False, "Invalid credentials", None
            
            user = dict(user[0])
            
            # Check if account is locked
            if user['locked_until']:
                lock_time = datetime.fromisoformat(user['locked_until'])
                if lock_time > datetime.now():
                    remaining = (lock_time - datetime.now()).seconds // 60
                    return False, f"Account locked for {remaining} minutes", None
            
            # Check if account is active
            if not user['is_active']:
                return False, "Account is deactivated", None
            
            # Check role
            if user['role'] != role and role != 'admin':
                return False, "Invalid role", None
            
            # Verify password
            if not security.verify_password(password, user['password_hash'], user['salt']):
                # Increment login attempts
                attempts = user['login_attempts'] + 1
                update_data = {'login_attempts': attempts}
                
                if attempts >= config.MAX_LOGIN_ATTEMPTS:
                    lock_until = (datetime.now() + timedelta(minutes=config.LOCKOUT_DURATION_MINUTES)).isoformat()
                    update_data['locked_until'] = lock_until
                    logger.warning(f"Account locked: {email}")
                
                self.db.execute_query(
                    "UPDATE users SET login_attempts = ?, locked_until = ? WHERE user_id = ?",
                    (update_data['login_attempts'], update_data.get('locked_until'), user['user_id'])
                )
                return False, "Invalid credentials", None
            
            # Successful login
            self.db.execute_query(
                "UPDATE users SET login_attempts = 0, locked_until = NULL, last_login = ? WHERE user_id = ?",
                (datetime.now().isoformat(), user['user_id'])
            )
            
            # Log analytics
            self.log_event('login', user['user_id'])
            
            logger.info(f"User logged in: {email}")
            return True, "Login successful", user
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False, "Login failed", None
    
    def log_event(self, event_type: str, user_id: str = None):
        """Log analytics event"""
        self.db.execute_query('''
            INSERT INTO analytics (analytic_id, event_type, user_id, created_at)
            VALUES (?, ?, ?, ?)
        ''', (str(uuid.uuid4()), event_type, user_id, datetime.now().isoformat()))

user_manager = UserManager()

# ==================== Session State Management ====================

def init_session_states():
    """Initialize all session state variables"""
    defaults = {
        'page': "home",
        'user_id': None,
        'user_email': None,
        'user_role': None,
        'user_name': None,
        'user_phone': None,
        'user_data': None,
        'admin_authenticated': False,
        'driver_authenticated': False,
        'lang_choice': "English 🇬🇧",
        'theme_choice': "Dark 🌙",
        'driver_id': None,
        'cart': [],
        'notifications': [],
        'order_history': [],
        'favorites': [],
        'current_order_id': None,
        'logged_in': False,
        'session_token': None,
        'last_activity': datetime.now(),
        'login_attempts': 0,
        'csrf_token': None
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    
    # Generate CSRF token
    if not st.session_state.csrf_token:
        st.session_state.csrf_token = security.generate_token()
    
    # Check session timeout
    if st.session_state.logged_in:
        time_diff = (datetime.now() - st.session_state.last_activity).seconds / 60
        if time_diff > config.SESSION_TIMEOUT_MINUTES:
            # Auto logout
            for key in ['user_id', 'user_email', 'user_role', 'user_name', 
                       'user_phone', 'logged_in', 'admin_authenticated', 'driver_id']:
                st.session_state[key] = None
            st.session_state.logged_in = False
            st.warning("Session expired. Please login again.")
            st.rerun()

init_session_states()

# Update last activity
if st.session_state.logged_in:
    st.session_state.last_activity = datetime.now()

# ==================== Translation System ====================

class TranslationManager:
    """Manage translations with caching"""
    
    def __init__(self):
        self._translations = {}
        self._load_all_translations()
    
    @lru_cache(maxsize=128)
    def get_translation(self, lang_code: str) -> Dict:
        """Get translations for a language (cached)"""
        return self._translations.get(lang_code, self._translations['en'])
    
    def _load_all_translations(self):
        """Load all translation files"""
        translation_files = {
            'en': 'en.json',
            'ku': 'ku.json',
            'ar': 'ar.json'
        }
        
        for code, filename in translation_files.items():
            try:
                if os.path.exists(filename):
                    with open(filename, 'r', encoding='utf-8') as f:
                        self._translations[code] = json.load(f)
            except Exception as e:
                logger.error(f"Error loading translation {filename}: {e}")
        
        # Fallback translations
        if 'en' not in self._translations:
            self._translations['en'] = self._get_fallback_english()
        if 'ku' not in self._translations:
            self._translations['ku'] = self._get_fallback_kurdish()
        if 'ar' not in self._translations:
            self._translations['ar'] = self._get_fallback_arabic()
    
    def _get_fallback_english(self) -> Dict:
        """Get hardcoded English translations"""
        return {
            "dir": "ltr",
            "align": "left",
            "theme_label": "Theme",
            "light": "Light ☀️",
            "dark": "Dark 🌙",
            "title": "GOLDEN DELIVERY PRO",
            "desc": "Experience the gold standard of logistics in Kirkuk. Fast, secure, and always on time.",
            "customer_name": "Customer Name",
            "shop_name": "Shop Name",
            "shop_addr": "Shop Address",
            "phone": "Phone Number",
            "area": "Neighborhood",
            "full_addr": "Address Details (Near what?)",
            "price": "Price (IQD)",
            "submit": "Confirm Order",
            "nav_home": "Home",
            "nav_order": "New Order",
            "nav_profile": "Account",
            "nav_terms": "Terms",
            "nav_track": "Track Order",
            "nav_offers": "Offers",
            "nav_support": "Support",
            "nav_chat": "Chat",
            "nav_analytics": "Analytics",
            "free_info": "Special: 1 out of every 3 deliveries is FREE!",
            "free_success": "Loyalty Reward: This delivery is 0 IQD!",
            "logout": "Logout",
            "settings": "Settings & Language",
            "admin_pass_label": "Enter Admin Password to view links",
            "admin_error": "Incorrect Password",
            "mgmt_links": "Management Links (Internal Only)",
            "terms_title": "Terms and Rules",
            "fast_title": "Fast",
            "fast_desc": "Delivery within 24 hours",
            "secure_title": "Secure",
            "secure_desc": "Your packages are safe with us",
            "free_title": "Free Delivery",
            "free_desc": "1 in 3 deliveries free",
            "delivery_time": "Delivery within 24 hours",
            "packages_safe": "Your packages are safe with us",
            "free_promo": "1 in 3 deliveries free",
            "signed_in_as": "Logged in as:",
            "access_account": "Sign in to access your account and management features",
            "golden_rules": "Golden Rules",
            "rule1": "1 out of 3 deliveries is free - automatically applied!",
            "rule2": "No illegal items - we comply with all local laws",
            "rule3": "Fast Kirkuk wide service - all neighborhoods covered",
            "rule4": "Delivery within 24 hours of order confirmation",
            "rule5": "Cash on delivery only",
            "rule6": "Free delivery promotion applies to orders over 3000 IQD",
            "rule7": "Customer must be present at time of delivery",
            "unlock_mgmt": "Unlock Management",
            "lock_mgmt": "Lock Management & Logout",
            "order_id": "Order ID",
            "order_status": "Status",
            "order_date": "Date",
            "estimated_delivery": "Estimated Delivery",
            "track_order": "Track Your Order",
            "enter_order_id": "Enter Order ID",
            "status_pending": "Pending",
            "status_picked": "Picked Up",
            "status_transit": "In Transit",
            "status_delivery": "Out for Delivery",
            "status_delivered": "Delivered",
            "status_cancelled": "Cancelled",
            "payment_method": "Payment Method",
            "cash_on_delivery": "Cash on Delivery",
            "bank_transfer": "Bank Transfer",
            "credit_card": "Credit Card",
            "zain_cash": "Zain Cash",
            "asia_hawala": "Asia Hawala",
            "assign_driver": "Assign Driver",
            "driver_name": "Driver Name",
            "driver_phone": "Driver Phone",
            "driver_status": "Driver Status",
            "driver_available": "Available",
            "driver_busy": "Busy",
            "driver_offline": "Offline",
            "rate_delivery": "Rate Your Delivery",
            "leave_review": "Leave a Review",
            "submit_feedback": "Submit Feedback",
            "enter_promo": "Enter Promo Code",
            "apply_promo": "Apply",
            "promo_applied": "Promo Code Applied!",
            "invalid_promo": "Invalid Promo Code",
            "loyalty_points": "Loyalty Points",
            "points_balance": "Your Points Balance",
            "redeem_points": "Redeem Points",
            "delivery_notes": "Delivery Notes",
            "gate_code": "Gate Code",
            "building_number": "Building Number",
            "contact_us": "Contact Us",
            "call_us": "Call Us",
            "whatsapp_us": "WhatsApp",
            "email_us": "Email Us",
            "visit_us": "Visit Us",
            "update_status": "Update Order Status",
            "current_status": "Current Status",
            "new_status": "New Status",
            "change_status": "Change Status",
            "my_deliveries": "My Deliveries",
            "register": "Register",
            "login": "Login",
            "password": "Password",
            "confirm_password": "Confirm Password",
            "full_name": "Full Name",
            "register_success": "Registration successful! Please login.",
            "login_success": "Login successful!",
            "login_error": "Invalid email or password",
            "password_mismatch": "Passwords do not match",
            "email_exists": "Email already registered",
            "driver_portal": "Driver Portal",
            "admin_portal": "Admin Portal",
            "my_orders": "My Orders",
            "no_orders": "No orders yet",
            "no_deliveries": "No deliveries assigned yet",
            "all_orders": "All Orders",
            "phone_required": "Phone number is required to view your orders",
            "password_requirements": "Password must be at least 8 characters with uppercase, lowercase, number, and special character",
            "session_expired": "Session expired. Please login again.",
            "account_locked": "Account temporarily locked. Try again later.",
            "invalid_csrf": "Invalid security token. Please refresh the page.",
            "order_created": "Order created successfully!",
            "order_updated": "Order updated successfully!",
            "driver_assigned": "Driver assigned successfully!",
            "feedback_submitted": "Feedback submitted. Thank you!",
            "profile_updated": "Profile updated successfully!",
            "password_changed": "Password changed successfully!",
            "notification_sent": "Notification sent successfully!",
            "message_sent": "Message sent successfully!",
            "file_too_large": "File too large. Maximum size is 10MB.",
            "invalid_file_type": "Invalid file type. Allowed: CSV, JSON, XLSX",
            "upload_success": "File uploaded successfully!",
            "no_notifications": "No notifications",
            "mark_all_read": "Mark All as Read",
            "clear_all": "Clear All",
            "export_data": "Export Data",
            "import_data": "Import Data",
            "backup_database": "Backup Database",
            "restore_database": "Restore Database",
            "system_health": "System Health",
            "active_users": "Active Users",
            "server_status": "Server Status",
            "database_size": "Database Size",
            "response_time": "Response Time",
            "privacy_policy": "Privacy Policy",
            "cookie_policy": "Cookie Policy",
            "delete_account": "Delete Account",
            "confirm_delete": "Are you sure? This action cannot be undone.",
            "cancel": "Cancel",
            "confirm": "Confirm",
            "search": "Search",
            "filter": "Filter",
            "sort_by": "Sort By",
            "date_range": "Date Range",
            "from": "From",
            "to": "To",
            "apply": "Apply",
            "reset": "Reset",
            "export_csv": "Export CSV",
            "export_excel": "Export Excel",
            "export_pdf": "Export PDF",
            "print": "Print",
            "share": "Share",
            "copy_link": "Copy Link",
            "refresh": "Refresh",
            "loading": "Loading...",
            "no_data": "No data available",
            "error_occurred": "An error occurred. Please try again.",
            "success": "Success!",
            "warning": "Warning!",
            "info": "Information",
            "help": "Help",
            "faq": "FAQ",
            "tutorial": "Tutorial",
            "getting_started": "Getting Started",
            "api_documentation": "API Documentation",
            "system_logs": "System Logs",
            "performance": "Performance",
            "uptime": "Uptime",
            "memory_usage": "Memory Usage",
            "cpu_usage": "CPU Usage",
            "disk_usage": "Disk Usage",
            "network": "Network",
            "downloads": "Downloads",
            "uploads": "Uploads",
            "traffic": "Traffic",
            "bandwidth": "Bandwidth"
        }
    
    def _get_fallback_kurdish(self) -> Dict:
        """Get hardcoded Kurdish translations"""
        return {
            "dir": "rtl",
            "align": "right",
            "title": "گۆڵدن دلیڤەری پرۆ",
            "desc": "بەرزترین کوالێتی گەیاندن لە کەرکوک. خێرا، پارێزراو، و هەمیشە لە کاتی خۆیدا.",
            "customer_name": "ناوی کڕیار",
            "phone": "ژمارەی مۆبایل",
            "area": "گەڕەک",
            "price": "نرخ (د.ع)",
            "submit": "تۆمارکردن",
            "nav_home": "سەرەکی",
            "nav_order": "داواکردن",
            "nav_profile": "هەژمار",
            "nav_terms": "یاساکان",
            "nav_track": "شوێنکەوتن",
            "nav_offers": "پێشکەشکراوەکان",
            "nav_support": "پاڵپشتی",
            "login": "چوونەژوورەوە",
            "register": "تۆماربوون",
            "password": "وشەی نهێنی",
            "full_name": "ناوی تەواو",
            "logout": "چوونەدەرەوە"
        }
    
    def _get_fallback_arabic(self) -> Dict:
        """Get hardcoded Arabic translations"""
        return {
            "dir": "rtl",
            "align": "right",
            "title": "جولدن دليفري برو",
            "desc": "المعيار الذهبي للخدمات اللوجستية في كركوك. سرعة، أمان، ودقة في المواعيد.",
            "customer_name": "اسم الزبون",
            "phone": "رقم الهاتف",
            "area": "المنطقة",
            "price": "السعر (د.ع)",
            "submit": "تأكيد الطلب",
            "nav_home": "الرئيسية",
            "nav_order": "طلب",
            "nav_profile": "الحساب",
            "nav_terms": "الشروط",
            "nav_track": "تتبع",
            "nav_offers": "العروض",
            "nav_support": "الدعم",
            "login": "دخول",
            "register": "تسجيل",
            "password": "كلمة المرور",
            "full_name": "الاسم الكامل",
            "logout": "خروج"
        }

# Initialize translation manager
translator = TranslationManager()

# Get current language
LANG_MAP = {
    "English 🇬🇧": "en",
    "کوردی 🇭🇺": "ku",
    "العربية 🇮🇶": "ar"
}

def get_text(key: str) -> str:
    """Get translated text"""
    lang_code = LANG_MAP.get(st.session_state.lang_choice, "en")
    translations = translator.get_translation(lang_code)
    return translations.get(key, key)

# ==================== UI Components ====================

class UIComponents:
    """Reusable UI components"""
    
    @staticmethod
    def card(title: str, content: str = None, icon: str = None, 
             bg_color: str = None, text_color: str = None, 
             border: bool = True, animation: bool = True):
        """Create a styled card component"""
        animation_class = "card-animate" if animation else ""
        
        card_html = f"""
        <div class="glass-card {animation_class}" style="
            {'background-color: ' + bg_color + ';' if bg_color else ''}
            {'color: ' + text_color + ';' if text_color else ''}
            {'border: 1px solid #D4AF3740;' if border else ''}
        ">
            {f'<div class="card-icon">{icon}</div>' if icon else ''}
            <h4 class="card-title" style="color: #D4AF37;">{title}</h4>
            {f'<p>{content}</p>' if content else ''}
        </div>
        """
        return st.markdown(card_html, unsafe_allow_html=True)
    
    @staticmethod
    def metric_card(label: str, value: Any, delta: str = None, icon: str = None):
        """Create a metric card"""
        delta_html = f'<span class="metric-delta">▲ {delta}</span>' if delta else ''
        icon_html = f'<span class="metric-icon">{icon}</span>' if icon else ''
        
        html = f"""
        <div class="glass-card metric-card">
            {icon_html}
            <div class="metric-value">💎 {value}</div>
            <div class="metric-label">{label}</div>
            {delta_html}
        </div>
        """
        return st.markdown(html, unsafe_allow_html=True)
    
    @staticmethod
    def status_badge(status: str):
        """Create a status badge"""
        colors = {
            'Pending': '#FFA500',
            'Picked Up': '#4169E1',
            'In Transit': '#32CD32',
            'Out for Delivery': '#FFD700',
            'Delivered': '#00FF00',
            'Cancelled': '#FF0000'
        }
        color = colors.get(status, '#808080')
        
        html = f"""
        <span style="
            background-color: {color}20;
            color: {color};
            padding: 5px 15px;
            border-radius: 20px;
            border: 1px solid {color};
            font-size: 0.9rem;
        ">
            {get_order_status_emoji(status)} {status}
        </span>
        """
        return st.markdown(html, unsafe_allow_html=True)
    
    @staticmethod
    def progress_bar(value: float, label: str = None, color: str = "#D4AF37"):
        """Create a custom progress bar"""
        html = f"""
        <div style="margin: 10px 0;">
            {f'<label>{label}</label>' if label else ''}
            <div style="
                background-color: #2d333d;
                border-radius: 10px;
                height: 20px;
                overflow: hidden;
            ">
                <div style="
                    background: linear-gradient(90deg, {color}, {color}80);
                    width: {value}%;
                    height: 100%;
                    border-radius: 10px;
                    transition: width 0.5s ease;
                "></div>
            </div>
            <span style="float: right; font-size: 0.8rem;">{value}%</span>
        </div>
        """
        return st.markdown(html, unsafe_allow_html=True)
    
    @staticmethod
    def notification_badge(count: int):
        """Create notification badge"""
        if count > 0:
            html = f"""
            <span style="
                background-color: #FF0000;
                color: white;
                padding: 2px 8px;
                border-radius: 50%;
                font-size: 0.7rem;
                position: relative;
                top: -10px;
                left: -5px;
            ">{count}</span>
            """
            return st.markdown(html, unsafe_allow_html=True)
        return ""

ui = UIComponents()

# ==================== Data Management ====================

class OrderManager:
    """Manage order operations"""
    
    def __init__(self):
        self.db = db
    
    def create_order(self, order_data: Dict) -> Tuple[bool, str, Optional[str]]:
        """Create a new order"""
        try:
            # Validate required fields
            required_fields = ['customer_name', 'customer_phone', 'delivery_area', 
                             'delivery_address', 'price']
            for field in required_fields:
                if field not in order_data or not order_data[field]:
                    return False, f"Missing required field: {field}", None
            
            # Validate phone
            if not security.validate_iraq_phone(order_data['customer_phone']):
                return False, "Invalid phone number", None
            
            # Generate order ID
            order_id = f"GD-{datetime.now().strftime('%Y%m')}-{str(uuid.uuid4())[:8].upper()}"
            
            # Calculate estimated delivery
            estimated = (datetime.now() + timedelta(hours=24)).isoformat()
            
            # Check for free delivery
            is_free = self._check_free_delivery(order_data['customer_phone'])
            if is_free:
                order_data['price'] = 0
                order_data['is_free_delivery'] = True
            
            # Insert order
            self.db.execute_query('''
                INSERT INTO orders (
                    order_id, customer_name, customer_phone, customer_email,
                    shop_name, shop_address, delivery_area, delivery_address,
                    price, status, payment_method, promo_code, discount_amount,
                    is_free_delivery, estimated_delivery, delivery_notes,
                    gate_code, building_number, order_source, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                order_id,
                order_data['customer_name'],
                order_data['customer_phone'],
                order_data.get('customer_email', ''),
                order_data.get('shop_name', ''),
                order_data.get('shop_address', ''),
                order_data['delivery_area'],
                order_data['delivery_address'],
                order_data['price'],
                'Pending',
                order_data.get('payment_method', 'Cash on Delivery'),
                order_data.get('promo_code', None),
                order_data.get('discount_amount', 0),
                order_data.get('is_free_delivery', False),
                estimated,
                order_data.get('delivery_notes', ''),
                order_data.get('gate_code', ''),
                order_data.get('building_number', ''),
                order_data.get('order_source', 'web'),
                datetime.now().isoformat()
            ))
            
            # Log analytics
            self._log_order_event('order_created', order_id)
            
            logger.info(f"Order created: {order_id}")
            return True, "Order created successfully", order_id
            
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            return False, f"Error: {str(e)}", None
    
    def _check_free_delivery(self, phone: str) -> bool:
        """Check if order qualifies for free delivery"""
        try:
            result = self.db.execute_query(
                "SELECT COUNT(*) as count FROM orders WHERE customer_phone = ?",
                (phone,)
            )
            if result:
                count = dict(result[0])['count']
                return (count + 1) % config.FREE_DELIVERY_EVERY_NTH == 0
        except:
            pass
        return False
    
    def get_user_orders(self, phone: str = None, email: str = None) -> List[Dict]:
        """Get orders for a user"""
        try:
            if phone:
                result = self.db.execute_query(
                    "SELECT * FROM orders WHERE customer_phone = ? ORDER BY created_at DESC",
                    (phone,)
                )
            elif email:
                result = self.db.execute_query(
                    "SELECT * FROM orders WHERE customer_email = ? ORDER BY created_at DESC",
                    (email,)
                )
            else:
                return []
            
            return [dict(row) for row in result]
        except Exception as e:
            logger.error(f"Error getting orders: {e}")
            return []
    
    def update_order_status(self, order_id: str, new_status: str) -> Tuple[bool, str]:
        """Update order status"""
        try:
            valid_statuses = ['Pending', 'Picked Up', 'In Transit', 
                            'Out for Delivery', 'Delivered', 'Cancelled']
            
            if new_status not in valid_statuses:
                return False, "Invalid status"
            
            # Get current order
            result = self.db.execute_query(
                "SELECT * FROM orders WHERE order_id = ?",
                (order_id,)
            )
            if not result:
                return False, "Order not found"
            
            order = dict(result[0])
            old_status = order['status']
            
            # Update order
            update_data = {'status': new_status, 'updated_at': datetime.now().isoformat()}
            
            if new_status == 'Delivered':
                update_data['actual_delivery'] = datetime.now().isoformat()
                # Update driver status
                if order['driver_id']:
                    self.db.execute_query(
                        "UPDATE drivers SET status = 'Available', current_order_id = NULL WHERE driver_id = ?",
                        (order['driver_id'],)
                    )
            elif new_status == 'Cancelled':
                if order['driver_id']:
                    self.db.execute_query(
                        "UPDATE drivers SET status = 'Available', current_order_id = NULL WHERE driver_id = ?",
                        (order['driver_id'],)
                    )
            
            self.db.execute_query(
                "UPDATE orders SET status = ?, updated_at = ?, actual_delivery = ? WHERE order_id = ?",
                (update_data['status'], update_data['updated_at'], 
                 update_data.get('actual_delivery'), order_id)
            )
            
            # Log change
            self._log_order_event('status_changed', order_id, 
                                f"Changed from {old_status} to {new_status}")
            
            logger.info(f"Order {order_id} status updated: {old_status} -> {new_status}")
            return True, f"Status updated to {new_status}"
            
        except Exception as e:
            logger.error(f"Error updating order: {e}")
            return False, f"Error: {str(e)}"
    
    def assign_driver(self, order_id: str, driver_id: str) -> Tuple[bool, str]:
        """Assign driver to order"""
        try:
            # Check driver availability
            driver = self.db.execute_query(
                "SELECT * FROM drivers WHERE driver_id = ? AND status = 'Available'",
                (driver_id,)
            )
            if not driver:
                return False, "Driver not available"
            
            # Update order
            self.db.execute_query(
                "UPDATE orders SET driver_id = ?, status = 'Picked Up', updated_at = ? WHERE order_id = ?",
                (driver_id, datetime.now().isoformat(), order_id)
            )
            
            # Update driver
            self.db.execute_query(
                "UPDATE drivers SET status = 'Busy', current_order_id = ? WHERE driver_id = ?",
                (order_id, driver_id)
            )
            
            logger.info(f"Driver {driver_id} assigned to order {order_id}")
            return True, "Driver assigned successfully"
            
        except Exception as e:
            logger.error(f"Error assigning driver: {e}")
            return False, f"Error: {str(e)}"
    
    def get_order_details(self, order_id: str) -> Optional[Dict]:
        """Get detailed order information"""
        try:
            result = self.db.execute_query(
                """
                SELECT o.*, d.name as driver_name, d.phone as driver_phone,
                       d.status as driver_status, d.current_location
                FROM orders o
                LEFT JOIN drivers d ON o.driver_id = d.driver_id
                WHERE o.order_id = ?
                """,
                (order_id,)
            )
            if result:
                return dict(result[0])
            return None
        except Exception as e:
            logger.error(f"Error getting order details: {e}")
            return None
    
    def _log_order_event(self, event_type: str, order_id: str, details: str = None):
        """Log order-related events"""
        self.db.execute_query('''
            INSERT INTO analytics (analytic_id, event_type, event_data, created_at)
            VALUES (?, ?, ?, ?)
        ''', (
            str(uuid.uuid4()),
            event_type,
            json.dumps({'order_id': order_id, 'details': details}),
            datetime.now().isoformat()
        ))

order_manager = OrderManager()

class NotificationManager:
    """Manage notifications"""
    
    def __init__(self):
        self.db = db
    
    def create_notification(self, user_id: str, type: str, title: str, 
                          message: str, action_url: str = None) -> bool:
        """Create new notification"""
        try:
            self.db.execute_query('''
                INSERT INTO notifications (notification_id, user_id, type, title, 
                                         message, action_url, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(uuid.uuid4()),
                user_id,
                type,
                title,
                message,
                action_url,
                datetime.now().isoformat()
            ))
            return True
        except Exception as e:
            logger.error(f"Error creating notification: {e}")
            return False
    
    def get_user_notifications(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get user notifications"""
        try:
            result = self.db.execute_query(
                """
                SELECT * FROM notifications 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
                """,
                (user_id, limit)
            )
            return [dict(row) for row in result]
        except Exception as e:
            logger.error(f"Error getting notifications: {e}")
            return []
    
    def mark_as_read(self, notification_id: str = None, user_id: str = None):
        """Mark notifications as read"""
        try:
            if notification_id:
                self.db.execute_query(
                    "UPDATE notifications SET is_read = 1 WHERE notification_id = ?",
                    (notification_id,)
                )
            elif user_id:
                self.db.execute_query(
                    "UPDATE notifications SET is_read = 1 WHERE user_id = ?",
                    (user_id,)
                )
        except Exception as e:
            logger.error(f"Error marking notifications: {e}")

notification_manager = NotificationManager()

class ChatManager:
    """Manage chat functionality"""
    
    def __init__(self):
        self.db = db
    
    def send_message(self, order_id: str, sender_id: str, receiver_id: str, 
                    message: str, message_type: str = 'text') -> Tuple[bool, str]:
        """Send chat message"""
        try:
            message_id = str(uuid.uuid4())
            self.db.execute_query('''
                INSERT INTO chat_messages (message_id, order_id, sender_id, receiver_id,
                                         message, message_type, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                message_id, order_id, sender_id, receiver_id,
                security.sanitize_input(message), message_type,
                datetime.now().isoformat()
            ))
            
            # Send notification
            notification_manager.create_notification(
                receiver_id, 'chat', 'New Message', 
                f"You have a new message regarding order {order_id}"
            )
            
            return True, message_id
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False, str(e)
    
    def get_conversation(self, order_id: str, user_id: str) -> List[Dict]:
        """Get conversation for an order"""
        try:
            result = self.db.execute_query(
                """
                SELECT * FROM chat_messages 
                WHERE order_id = ? AND (sender_id = ? OR receiver_id = ?)
                ORDER BY created_at ASC
                """,
                (order_id, user_id, user_id)
            )
            return [dict(row) for row in result]
        except Exception as e:
            logger.error(f"Error getting conversation: {e}")
            return []

chat_manager = ChatManager()

# ==================== Analytics & Reporting ====================

class AnalyticsManager:
    """Manage analytics and reporting"""
    
    def __init__(self):
        self.db = db
    
    def get_dashboard_stats(self) -> Dict:
        """Get dashboard statistics"""
        try:
            # Total orders
            total_orders = self.db.execute_query("SELECT COUNT(*) as count FROM orders")[0]['count']
            
            # Total revenue
            revenue = self.db.execute_query(
                "SELECT SUM(price) as total FROM orders WHERE status != 'Cancelled'"
            )[0]['total'] or 0
            
            # Active drivers
            active_drivers = self.db.execute_query(
                "SELECT COUNT(*) as count FROM drivers WHERE status = 'Available'"
            )[0]['count']
            
            # Today's orders
            today = datetime.now().strftime('%Y-%m-%d')
            today_orders = self.db.execute_query(
                "SELECT COUNT(*) as count FROM orders WHERE date(created_at) = ?",
                (today,)
            )[0]['count']
            
            # Average rating
            avg_rating = self.db.execute_query(
                "SELECT AVG(rating) as avg FROM feedback"
            )[0]['avg'] or 0
            
            return {
                'total_orders': total_orders,
                'total_revenue': revenue,
                'active_drivers': active_drivers,
                'today_orders': today_orders,
                'avg_rating': round(avg_rating, 1)
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
    
    def get_orders_by_area(self) -> pd.DataFrame:
        """Get orders grouped by area"""
        try:
            result = self.db.execute_query(
                "SELECT delivery_area, COUNT(*) as count, SUM(price) as revenue FROM orders GROUP BY delivery_area"
            )
            return pd.DataFrame([dict(row) for row in result])
        except Exception as e:
            logger.error(f"Error getting area stats: {e}")
            return pd.DataFrame()
    
    def get_revenue_trend(self, days: int = 30) -> pd.DataFrame:
        """Get revenue trend"""
        try:
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            result = self.db.execute_query(
                """
                SELECT date(created_at) as date, COUNT(*) as orders, SUM(price) as revenue 
                FROM orders 
                WHERE created_at >= ? AND status != 'Cancelled'
                GROUP BY date(created_at)
                ORDER BY date(created_at)
                """,
                (start_date,)
            )
            return pd.DataFrame([dict(row) for row in result])
        except Exception as e:
            logger.error(f"Error getting revenue trend: {e}")
            return pd.DataFrame()
    
    def get_driver_performance(self) -> pd.DataFrame:
        """Get driver performance metrics"""
        try:
            result = self.db.execute_query(
                """
                SELECT d.driver_id, u.full_name, d.total_deliveries, d.rating,
                       COUNT(o.order_id) as completed_orders
                FROM drivers d
                JOIN users u ON d.user_id = u.user_id
                LEFT JOIN orders o ON d.driver_id = o.driver_id AND o.status = 'Delivered'
                GROUP BY d.driver_id
                """
            )
            return pd.DataFrame([dict(row) for row in result])
        except Exception as e:
            logger.error(f"Error getting driver performance: {e}")
            return pd.DataFrame()

analytics_manager = AnalyticsManager()

# ==================== Main Application ====================

def main():
    """Main application entry point"""
    
    # Page configuration
    st.set_page_config(
        page_title="Golden Delivery Pro",
        layout="wide",
        initial_sidebar_state="collapsed",
        page_icon="🚚"
    )
    
    # Initialize session
    init_session_states()
    
    # Apply theme
    apply_theme()
    
    # Render header
    render_header()
    
    # Render navigation
    selected = render_navigation()
    
    # Route to page
    route_page(selected)
    
    # Render footer
    render_footer()

def apply_theme():
    """Apply theme styling"""
    is_dark = st.session_state.theme_choice == "Dark 🌙"
    
    if is_dark:
        colors = {
            'main_bg': "#0a0c10",
            'card_bg': "#1a1d23",
            'text': "#ffffff",
            'text_secondary': "#cccccc",
            'accent': "#D4AF37",
            'input_bg': "#2d333d",
            'border': "#3a404c",
            'dropdown_bg': "#2d333d",
            'dropdown_text': "#ffffff"
        }
    else:
        colors = {
            'main_bg': "#f5f7fa",
            'card_bg': "#ffffff",
            'text': "#1a1a2e",
            'text_secondary': "#2d3748",
            'accent': "#D4AF37",
            'input_bg': "#ffffff",
            'border': "#e0e0e0",
            'dropdown_bg': "#ffffff",
            'dropdown_text': "#1a1a2e"
        }
    
    # Inject CSS
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
        
        * {{
            font-family: 'Cairo', sans-serif;
        }}
        
        .stApp {{
            background-color: {colors['main_bg']} !important;
        }}
        
        .main {{
            color: {colors['text']} !important;
        }}
        
        h1, h2, h3, h4, h5, h6, p, span, div, label {{
            color: {colors['text']} !important;
        }}
        
        .glass-card {{
            background-color: {colors['card_bg']} !important;
            border-radius: 20px !important;
            padding: 25px !important;
            border: 1px solid {colors['accent']}40 !important;
            margin-bottom: 20px !important;
            color: {colors['text']} !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3) !important;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .glass-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(212, 175, 55, 0.2);
        }}
        
        .stButton > button {{
            background-color: {colors['accent']} !important;
            color: black !important;
            border: none !important;
            font-weight: bold !important;
            border-radius: 10px !important;
            padding: 10px 20px !important;
            transition: all 0.3s !important;
            width: 100% !important;
        }}
        
        .stButton > button:hover {{
            background-color: #c19b2e !important;
            transform: translateY(-2px) !important;
        }}
        
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div {{
            background-color: {colors['input_bg']} !important;
            color: {colors['text']} !important;
            border: 1px solid {colors['border']} !important;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .card-animate {{
            animation: fadeIn 0.5s ease;
        }}
        
        @keyframes pulse {{
            0% {{ transform: scale(1); }}
            50% {{ transform: scale(1.05); }}
            100% {{ transform: scale(1); }}
        }}
        
        .pulse {{
            animation: pulse 2s infinite;
        }}
        
        @media (max-width: 768px) {{
            .glass-card {{
                padding: 15px !important;
            }}
            
            .stButton > button {{
                padding: 8px 15px !important;
            }}
        }}
        
        [dir="rtl"] {{
            text-align: right !important;
        }}
        
        .loading-spinner {{
            border: 4px solid #f3f3f3;
            border-top: 4px solid {colors['accent']};
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
    </style>
    """, unsafe_allow_html=True)

def render_header():
    """Render application header"""
    L = get_text
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"""
        <h2 style='color:#D4AF37; margin:0;'>{L('title')}</h2>
        """, unsafe_allow_html=True)
    
    with col2:
        lang_options = list(LANG_MAP.keys())
        current_lang_index = lang_options.index(st.session_state.lang_choice)
        selected_lang = st.selectbox(
            "🌐",
            lang_options,
            index=current_lang_index,
            label_visibility="collapsed",
            key="lang_selector"
        )
        if selected_lang != st.session_state.lang_choice:
            st.session_state.lang_choice = selected_lang
            st.rerun()
    
    with col3:
        theme_options = ["Light ☀️", "Dark 🌙"]
        current_theme_index = 0 if st.session_state.theme_choice == "Light ☀️" else 1
        selected_theme = st.selectbox(
            "🎨",
            theme_options,
            index=current_theme_index,
            label_visibility="collapsed",
            key="theme_selector"
        )
        if selected_theme != st.session_state.theme_choice:
            st.session_state.theme_choice = selected_theme
            st.rerun()

def render_navigation():
    """Render navigation menu"""
    L = get_text
    
    nav_options = [
        L('nav_home'),
        L('nav_order'),
        L('nav_track'),
        L('nav_offers'),
        L('nav_profile'),
        L('nav_terms'),
        L('nav_support')
    ]
    
    # Add notification badge to profile
    notification_count = 0
    if st.session_state.logged_in and st.session_state.user_id:
        notifications = notification_manager.get_user_notifications(
            st.session_state.user_id, 100
        )
        notification_count = sum(1 for n in notifications if not n['is_read'])
    
    selected = option_menu(
        menu_title=None,
        options=nav_options,
        icons=['house-door', 'box', 'geo-alt', 'gift', 'person', 'file-text', 'headset'],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {
                "padding": "0!important",
                "background-color": "transparent",
                "max-width": "1000px",
                "margin": "0 auto",
                "display": "flex",
                "justify-content": "center"
            },
            "icon": {"color": "#D4AF37", "font-size": "16px"},
            "nav-link": {
                "font-size": "15px",
                "text-align": "center",
                "margin": "0px 2px",
                "padding": "10px 15px",
                "border-radius": "30px",
                "transition": "all 0.3s"
            },
            "nav-link-selected": {
                "background-color": "#D4AF37",
                "color": "black",
                "font-weight": "bold"
            }
        }
    )
    
    # Map selection to page
    page_mapping = {
        L('nav_home'): "home",
        L('nav_order'): "order",
        L('nav_track'): "track",
        L('nav_offers'): "offers",
        L('nav_profile'): "profile",
        L('nav_terms'): "terms",
        L('nav_support'): "support"
    }
    
    return page_mapping.get(selected, "home")

def route_page(page: str):
    """Route to appropriate page"""
    if page == "home":
        render_home_page()
    elif page == "order":
        render_order_page()
    elif page == "track":
        render_track_page()
    elif page == "offers":
        render_offers_page()
    elif page == "profile":
        render_profile_page()
    elif page == "terms":
        render_terms_page()
    elif page == "support":
        render_support_page()
    else:
        render_home_page()

def render_home_page():
    """Render home page"""
    L = get_text
    
    # Hero section
    st.markdown(f"""
    <div class="brand-header" style="
        background: linear-gradient(135deg, #D4AF37 0%, #8A6D3B 100%);
        padding: 30px;
        border-radius: 0 0 30px 30px;
        text-align: center;
        margin-bottom: 20px;
    ">
        <h1 style="color:white; margin:0;">{L('title')}</h1>
        <p style="color:white; opacity:0.9;">{L('desc')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Stats
    stats = analytics_manager.get_dashboard_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        ui.metric_card("📦 Total Orders", stats.get('total_orders', 0))
    with col2:
        ui.metric_card("✅ Delivered", stats.get('active_drivers', 0))
    with col3:
        ui.metric_card("🚚 Active Drivers", stats.get('today_orders', 0))
    with col4:
        ui.metric_card("💰 Revenue", f"{stats.get('total_revenue', 0):,} IQD")
    
    # Features
    st.markdown(f"<h3 style='color:#D4AF37;'>Why Choose Us?</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        ui.card(L('fast_title'), L('fast_desc'), "⚡")
    with col2:
        ui.card(L('secure_title'), L('secure_desc'), "🔒")
    with col3:
        ui.card(L('free_title'), L('free_desc'), "🎁")
    
    # Recent orders
    st.markdown(f"<h3 style='color:#D4AF37;'>📋 Recent Orders</h3>", unsafe_allow_html=True)
    
    recent_orders = order_manager.get_user_orders()[:5]
    if recent_orders:
        df = pd.DataFrame(recent_orders)
        st.dataframe(df[['order_id', 'customer_name', 'delivery_area', 'price', 'status']], 
                    use_container_width=True)
    else:
        st.info("No recent orders")

def render_order_page():
    """Render order page"""
    L = get_text
    
    st.markdown(f"<h2 style='text-align:center; color:#D4AF37;'>{L('nav_order')}</h2>", 
               unsafe_allow_html=True)
    
    # CSRF protection
    if not st.session_state.get('csrf_token'):
        st.error(L('invalid_csrf'))
        return
    
    st.info(L('free_info'))
    
    # Order form
    with st.form("order_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            customer_name = st.text_input(L('customer_name'))
            phone = st.text_input(L('phone'), placeholder="07xx xxx xxxx")
            shop_name = st.text_input(L('shop_name'))
        
        with col2:
            payment_method = st.selectbox(L('payment_method'), [
                L('cash_on_delivery'),
                L('bank_transfer'),
                L('credit_card'),
                L('zain_cash'),
                L('asia_hawala')
            ])
            delivery_notes = st.text_area(L('delivery_notes'), 
                                         placeholder=L('gate_code'))
        
        # Check free delivery
        is_free = False
        if phone and security.validate_iraq_phone(phone):
            is_free = order_manager._check_free_delivery(phone)
            if is_free:
                st.success(L('free_success'))
        
        col1, col2 = st.columns(2)
        with col1:
            area = st.selectbox(L('area'), KIRKUK_AREAS)
            full_addr = st.text_area(L('full_addr'))
        
        with col2:
            shop_addr = st.text_input(L('shop_addr'))
            price = st.number_input(L('price'), 
                                   value=0 if is_free else 3000,
                                   min_value=0, step=1000)
            
            promo_code = st.text_input(L('enter_promo'))
            if promo_code:
                # Validate promo code
                discount = validate_promo(promo_code, price)
                if discount > 0:
                    price -= discount
                    st.success(f"{L('promo_applied')} -{discount:,.0f} IQD")
        
        submitted = st.form_submit_button(L('submit'), use_container_width=True)
        
        if submitted:
            if not all([customer_name, phone, area]):
                st.error("Please fill all required fields")
            elif not security.validate_iraq_phone(phone):
                st.error("Invalid phone number")
            else:
                order_data = {
                    'customer_name': customer_name,
                    'customer_phone': phone,
                    'customer_email': st.session_state.get('user_email', ''),
                    'shop_name': shop_name,
                    'shop_address': shop_addr,
                    'delivery_area': area,
                    'delivery_address': full_addr,
                    'price': price,
                    'payment_method': payment_method,
                    'delivery_notes': delivery_notes,
                    'promo_code': promo_code if promo_code else None
                }
                
                success, message, order_id = order_manager.create_order(order_data)
                
                if success:
                    st.success(f"✅ {message}\nOrder ID: {order_id}")
                    st.balloons()
                    st.session_state.current_order_id = order_id
                    
                    # Send notification
                    if st.session_state.user_id:
                        notification_manager.create_notification(
                            st.session_state.user_id,
                            'order_update',
                            'Order Created',
                            f"Your order {order_id} has been created successfully"
                        )
                else:
                    st.error(message)

def render_track_page():
    """Render tracking page"""
    L = get_text
    
    st.markdown(f"<h2 style='text-align:center; color:#D4AF37;'>{L('track_order')}</h2>",
               unsafe_allow_html=True)
    
    track_method = st.radio("Track by:", ["Order ID", "Phone Number"], horizontal=True)
    
    if track_method == "Order ID":
        order_id = st.text_input(L('enter_order_id'))
        
        if order_id:
            order = order_manager.get_order_details(order_id)
            
            if order:
                col1, col2 = st.columns(2)
                
                with col1:
                    ui.card("Order Details", f"""
                    **{L('order_id')}:** {order['order_id']}
                    **{L('customer_name')}:** {order['customer_name']}
                    **{L('area')}:** {order['delivery_area']}
                    **{L('price')}:** {int(order['price']):,} IQD
                    """)
                
                with col2:
                    status = order['status']
                    emoji = get_order_status_emoji(status)
                    
                    ui.card(L('order_status'), f"""
                    <div style="text-align:center;">
                        <span style="font-size:3rem;">{emoji}</span>
                        <h4>{status}</h4>
                    </div>
                    **{L('order_date')}:** {order['created_at']}
                    **{L('estimated_delivery')}:** {order['estimated_delivery']}
                    """)
                
                # Status timeline
                st.markdown("<h4 style='color:#D4AF37;'>Order Progress</h4>", 
                          unsafe_allow_html=True)
                
                statuses = ['Pending', 'Picked Up', 'In Transit', 
                          'Out for Delivery', 'Delivered']
                
                current_index = statuses.index(status) if status in statuses else 0
                
                cols = st.columns(len(statuses))
                for i, s in enumerate(statuses):
                    with cols[i]:
                        if i <= current_index:
                            st.markdown(f"""
                            <div style="text-align:center; color:#D4AF37;">
                                <h3>{get_order_status_emoji(s)}</h3>
                                <p style="font-size:0.8rem;">{s}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div style="text-align:center; opacity:0.5;">
                                <h3>⭕</h3>
                                <p style="font-size:0.8rem;">{s}</p>
                            </div>
                            """, unsafe_allow_html=True)
                
                # Chat section
                if st.session_state.logged_in:
                    render_chat_section(order_id)
            else:
                st.warning("Order not found")
    
    else:
        phone = st.text_input(L('phone'), placeholder="07xx xxx xxxx")
        
        if phone and security.validate_iraq_phone(phone):
            orders = order_manager.get_user_orders(phone=phone)
            
            if orders:
                st.markdown(f"<h4 style='color:#D4AF37;'>Your Orders ({len(orders)})</h4>",
                          unsafe_allow_html=True)
                
                for order in orders:
                    with st.expander(f"Order {order['order_id']} - {order['status']}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**{L('order_id')}:** {order['order_id']}")
                            st.write(f"**{L('customer_name')}:** {order['customer_name']}")
                            st.write(f"**{L('area')}:** {order['delivery_area']}")
                        with col2:
                            st.write(f"**{L('order_status')}:** {get_order_status_emoji(order['status'])} {order['status']}")
                            st.write(f"**{L('price')}:** {int(order['price']):,} IQD")
            else:
                st.info("No orders found")

def render_chat_section(order_id: str):
    """Render chat section for an order"""
    st.markdown("<h4 style='color:#D4AF37;'>💬 Chat with Driver</h4>", 
               unsafe_allow_html=True)
    
    # Get conversation
    messages = chat_manager.get_conversation(order_id, st.session_state.user_id)
    
    # Display messages
    for msg in messages[-10:]:  # Show last 10 messages
        is_sender = msg['sender_id'] == st.session_state.user_id
        align = "right" if is_sender else "left"
        bg_color = "#D4AF37" if is_sender else "#2d333d"
        
        st.markdown(f"""
        <div style="text-align:{align}; margin:10px 0;">
            <div style="
                display:inline-block;
                background-color:{bg_color};
                color:{'black' if is_sender else 'white'};
                padding:10px 15px;
                border-radius:15px;
                max-width:70%;
            ">
                {msg['message']}
                <br>
                <small style="opacity:0.7;">{msg['created_at'][:16]}</small>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Send message
    with st.form("chat_form", clear_on_submit=True):
        message = st.text_input("Type a message...")
        sent = st.form_submit_button("Send")
        
        if sent and message:
            order = order_manager.get_order_details(order_id)
            if order and order['driver_id']:
                success, _ = chat_manager.send_message(
                    order_id,
                    st.session_state.user_id,
                    order['driver_id'],
                    message
                )
                if success:
                    st.rerun()

def render_offers_page():
    """Render offers page"""
    L = get_text
    
    st.markdown(f"<h2 style='text-align:center; color:#D4AF37;'>{L('nav_offers')}</h2>",
               unsafe_allow_html=True)
    
    # Active promotions
    st.markdown(f"<h3 style='color:#D4AF37;'>🎁 Active Promotions</h3>",
               unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="glass-card pulse">
            <h4 style="color:#D4AF37; text-align:center;">🎊 Free Delivery Every 3rd Order</h4>
            <p style="text-align:center;">{L('free_promo')}</p>
            <p style="text-align:center; font-size:0.9rem;">Valid: Always</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="glass-card">
            <h4 style="color:#D4AF37; text-align:center;">💎 Loyalty Points</h4>
            <p style="text-align:center;">Earn {config.LOYALTY_POINTS_PER_1000} point for every 1000 IQD</p>
            <p style="text-align:center; font-size:0.9rem;">Redeem for discounts</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Redeem points
    if st.session_state.logged_in:
        st.markdown(f"<h4 style='color:#D4AF37;'>Redeem Your Points</h4>",
                   unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        for i, (points, discount) in enumerate(config.REDEEM_POINTS_TIERS.items()):
            with [col1, col2, col3, col4][i]:
                st.markdown(f"""
                <div class="glass-card" style="text-align:center;">
                    <h3 style="color:#D4AF37;">{points}</h3>
                    <p>Points</p>
                    <h4>{discount:,} IQD</h4>
                    <p>Discount</p>
                </div>
                """, unsafe_allow_html=True)

def render_profile_page():
    """Render profile page"""
    L = get_text
    
    st.markdown(f"<h2 style='text-align:center; color:#D4AF37;'>{L('nav_profile')}</h2>",
               unsafe_allow_html=True)
    
    if not st.session_state.logged_in:
        # Login/Register tabs
        tab1, tab2 = st.tabs([f"🔑 {L('login')}", f"📝 {L('register')}"])
        
        with tab1:
            with st.form("login_form"):
                email = st.text_input("Email")
                password = st.text_input(L('password'), type="password")
                role = st.selectbox("Login as", ["Customer", "Driver", "Admin"])
                
                submitted = st.form_submit_button(L('login'))
                
                if submitted:
                    success, message, user_data = user_manager.login_user(
                        email, password, role.lower()
                    )
                    
                    if success:
                        # Set session
                        st.session_state.user_id = user_data['user_id']
                        st.session_state.user_email = email
                        st.session_state.user_role = role.lower()
                        st.session_state.user_name = user_data['full_name']
                        st.session_state.user_phone = user_data['phone']
                        st.session_state.logged_in = True
                        st.session_state.session_token = security.generate_token()
                        
                        if role.lower() == 'admin':
                            st.session_state.admin_authenticated = True
                        
                        st.success(L('login_success'))
                        st.rerun()
                    else:
                        st.error(message)
        
        with tab2:
            with st.form("register_form"):
                name = st.text_input(L('full_name'))
                email = st.text_input("Email")
                phone = st.text_input(L('phone'), placeholder="07xx xxx xxxx")
                password = st.text_input(L('password'), type="password")
                confirm_password = st.text_input(L('confirm_password'), type="password")
                area = st.selectbox(L('area'), KIRKUK_AREAS)
                
                submitted = st.form_submit_button(L('register'))
                
                if submitted:
                    if password != confirm_password:
                        st.error(L('password_mismatch'))
                    else:
                        success, message = user_manager.register_user(
                            email, password, name, phone, 'customer', area
                        )
                        
                        if success:
                            st.success(L('register_success'))
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(message)
    else:
        # User profile
        render_user_profile()

def render_user_profile():
    """Render logged-in user profile"""
    L = get_text
    
    tabs = st.tabs(["👤 Profile", "📦 Orders", "⭐ Loyalty", "🔔 Notifications", "⚙️ Settings"])
    
    with tabs[0]:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image("https://via.placeholder.com/150", caption="Profile Picture")
            if st.button("Change Picture"):
                st.info("Feature coming soon")
        
        with col2:
            st.markdown(f"""
            <div class="glass-card">
                <h4 style="color:#D4AF37;">{L('signed_in_as')}</h4>
                <p><b>Name:</b> {st.session_state.user_name}</p>
                <p><b>Email:</b> {st.session_state.user_email}</p>
                <p><b>Phone:</b> {st.session_state.user_phone}</p>
                <p><b>Role:</b> {st.session_state.user_role.title()}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Stats
        orders = order_manager.get_user_orders(phone=st.session_state.user_phone)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Orders", len(orders))
        with col2:
            total_spent = sum(o['price'] for o in orders)
            st.metric("Total Spent", f"{total_spent:,} IQD")
        with col3:
            completed = sum(1 for o in orders if o['status'] == 'Delivered')
            st.metric("Completed", completed)
    
    with tabs[1]:
        orders = order_manager.get_user_orders(phone=st.session_state.user_phone)
        
        if orders:
            df = pd.DataFrame(orders)
            st.dataframe(
                df[['order_id', 'created_at', 'delivery_area', 'price', 'status']],
                use_container_width=True
            )
        else:
            st.info(L('no_orders'))
    
    with tabs[2]:
        st.markdown(f"<h3 style='color:#D4AF37;'>Loyalty Points</h3>",
                   unsafe_allow_html=True)
        
        # Calculate points
        total_spent = sum(o['price'] for o in orders if o['status'] != 'Cancelled')
        points = total_spent // 1000 * config.LOYALTY_POINTS_PER_1000
        
        st.markdown(f"""
        <div class="glass-card" style="text-align:center;">
            <h1 style="color:#D4AF37; font-size:4rem;">{points}</h1>
            <p>Loyalty Points</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Redemption options
        st.markdown("<h4>Redeem Points</h4>", unsafe_allow_html=True)
        
        for points_needed, discount in config.REDEEM_POINTS_TIERS.items():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"{points_needed} Points → {discount:,} IQD Discount")
            with col2:
                if st.button(f"Redeem", key=f"redeem_{points_needed}"):
                    if points >= points_needed:
                        st.success(f"Code: REDEEM{points_needed}")
                    else:
                        st.error("Insufficient points")
    
    with tabs[3]:
        notifications = notification_manager.get_user_notifications(
            st.session_state.user_id
        )
        
        if notifications:
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("Mark All Read"):
                    notification_manager.mark_as_read(user_id=st.session_state.user_id)
                    st.rerun()
            
            for notif in notifications:
                with st.container():
                    if notif['is_read']:
                        st.info(f"{notif['title']}\n\n{notif['message']}\n\n*{notif['created_at'][:16]}*")
                    else:
                        st.warning(f"**NEW** {notif['title']}\n\n{notif['message']}\n\n*{notif['created_at'][:16]}*")
        else:
            st.info("No notifications")
    
    with tabs[4]:
        with st.expander("Change Password"):
            with st.form("change_password"):
                current = st.text_input("Current Password", type="password")
                new = st.text_input("New Password", type="password")
                confirm = st.text_input("Confirm New Password", type="password")
                
                if st.form_submit_button("Change Password"):
                    if new != confirm:
                        st.error("Passwords do not match")
                    else:
                        is_strong, msg = security.validate_password_strength(new)
                        if not is_strong:
                            st.error(msg)
                        else:
                            st.success("Password changed successfully")
        
        with st.expander("Language & Theme"):
            st.info("Use the top bar to change language and theme")
        
        with st.expander("Export My Data"):
            if st.button("Export as CSV"):
                orders = order_manager.get_user_orders(phone=st.session_state.user_phone)
                if orders:
                    df = pd.DataFrame(orders)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        "Download CSV",
                        csv,
                        "my_orders.csv",
                        "text/csv"
                    )
        
        with st.expander("Danger Zone"):
            st.warning("These actions cannot be undone!")
            
            if st.button("Delete My Account", type="primary"):
                st.error("Feature coming soon")
        
        # Logout
        if st.button(L('logout'), type="primary"):
            for key in ['user_id', 'user_email', 'user_role', 'user_name', 
                       'user_phone', 'logged_in', 'admin_authenticated', 'driver_id']:
                st.session_state[key] = None
            st.session_state.logged_in = False
            st.rerun()

def render_terms_page():
    """Render terms page"""
    L = get_text
    
    st.markdown(f"<h2 style='text-align:center; color:#D4AF37;'>{L('terms_title')}</h2>",
               unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="glass-card">
        <h4 style="color:#D4AF37;">{L('golden_rules')}</h4>
        <ol>
            <li>{L('rule1')}</li>
            <li>{L('rule2')}</li>
            <li>{L('rule3')}</li>
            <li>{L('rule4')}</li>
            <li>{L('rule5')}</li>
            <li>{L('rule6')}</li>
            <li>{L('rule7')}</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    # Additional policies
    with st.expander("Privacy Policy"):
        st.write("Your privacy is important to us. We collect only necessary information...")
    
    with st.expander("Cookie Policy"):
        st.write("We use cookies to improve your experience...")
    
    with st.expander("Refund Policy"):
        st.write("Refunds are processed within 7-14 business days...")

def render_support_page():
    """Render support page"""
    L = get_text
    
    st.markdown(f"<h2 style='text-align:center; color:#D4AF37;'>{L('nav_support')}</h2>",
               unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="glass-card">
            <h4 style="color:#D4AF37;">📞 {L('contact_us')}</h4>
            <p><b>{L('call_us')}:</b></p>
            <p class="phone-number">{config.COMPANY_PHONES[0]}</p>
            <p class="phone-number">{config.COMPANY_PHONES[1]}</p>
            <p><b>{L('whatsapp_us')}:</b></p>
            <a href="{config.COMPANY_WHATSAPP}" target="_blank">Click to WhatsApp</a>
            <p><b>{L('email_us')}:</b> {config.COMPANY_EMAIL}</p>
            <p><b>{L('visit_us')}:</b> {config.COMPANY_ADDRESS}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="glass-card">
            <h4 style="color:#D4AF37;">🕒 Working Hours</h4>
            <p>Saturday - Thursday: 8:00 AM - 10:00 PM</p>
            <p>Friday: 2:00 PM - 8:00 PM</p>
            <p>24/7 Online Support via WhatsApp</p>
        </div>
        """, unsafe_allow_html=True)
    
    # FAQ
    st.markdown("<h4 style='color:#D4AF37;'>❓ Frequently Asked Questions</h4>",
               unsafe_allow_html=True)
    
    with st.expander("How long does delivery take?"):
        st.write("Delivery is within 24 hours of order confirmation.")
    
    with st.expander("How do I track my order?"):
        st.write("Use the Track Order page with your order ID or phone number.")
    
    with st.expander("What payment methods are accepted?"):
        st.write("We accept Cash on Delivery, Bank Transfer, Credit Card, Zain Cash, and Asia Hawala.")
    
    with st.expander("How does the free delivery work?"):
        st.write("Every 3rd order from the same phone number is automatically free!")
    
    # Contact form
    st.markdown("<h4 style='color:#D4AF37;'>Send us a message</h4>",
               unsafe_allow_html=True)
    
    with st.form("contact_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Your Name")
            email = st.text_input("Your Email")
        with col2:
            phone = st.text_input("Your Phone")
            subject = st.selectbox("Subject", 
                ["General Inquiry", "Order Issue", "Complaint", "Suggestion", "Partnership"])
        
        message = st.text_area("Message")
        
        if st.form_submit_button("Send Message"):
            st.success("Thank you for contacting us! We'll respond within 24 hours.")

def render_footer():
    """Render application footer"""
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="
        background-color: #1a1d23;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin-top: 30px;
    ">
        <p style="margin-bottom: 10px;">
            📞 <span style="color:#D4AF37;">{config.COMPANY_PHONES[0]}</span> | 
            <span style="color:#D4AF37;">{config.COMPANY_PHONES[1]}</span>
        </p>
        <p>✉️ {config.COMPANY_EMAIL} | 📍 {config.COMPANY_ADDRESS}</p>
        <p style="font-size: 0.9rem; opacity: 0.8;">
            © 2024 Golden Delivery Pro v{config.VERSION} - All rights reserved
        </p>
    </div>
    """, unsafe_allow_html=True)

# ==================== Utility Functions ====================

def get_order_status_emoji(status: str) -> str:
    """Get emoji for order status"""
    emojis = {
        "Pending": "⏳",
        "Picked Up": "📦",
        "In Transit": "🚚",
        "Out for Delivery": "🚪",
        "Delivered": "✅",
        "Cancelled": "❌"
    }
    return emojis.get(status, "📦")

def validate_promo(code: str, price: float) -> float:
    """Validate promo code and return discount amount"""
    try:
        result = db.execute_query(
            "SELECT * FROM promotions WHERE code = ? AND is_active = 1",
            (code,)
        )
        if result:
            promo = dict(result[0])
            
            # Check expiry
            if datetime.fromisoformat(promo['expiry_date']) < datetime.now():
                return 0
            
            # Check minimum order
            if price < promo['min_order_amount']:
                return 0
            
            # Check usage limit
            if promo['usage_limit'] and promo['usage_count'] >= promo['usage_limit']:
                return 0
            
            # Calculate discount
            if promo['discount_type'] == 'percentage':
                discount = (price * promo['discount_value']) / 100
                if promo['max_discount']:
                    discount = min(discount, promo['max_discount'])
            else:
                discount = min(promo['discount_value'], price)
            
            return discount
    except:
        pass
    return 0

# ==================== KIRKUK Areas ====================

KIRKUK_AREAS = sorted([
    "Arfa / عرفة", "Tis'in / تسعين", "Shoraw / شوراو", "Rahim Awa / رحيماوة",
    "Quraya / قورية", "Al-Wasiti / الواسطي", "Al-Nasr / النصر", "Azadi / ازادي",
    "Wahid Huzairan / واحد حزيران", "Kirkuk Citadel / قلعة كركوك",
    "Musalla / مصلى", "Imam Qasim / امام قاسم", "Shorija / الشورجة",
    "Hasiraka / حصيرةكة", "Tapai Malla Abdulla / تبة ملا عبدulla",
    "Rahimawa / رحيم آوه", "Almas / الماس", "Arafa / عرفة", "Faylaq / فيلق",
    "Panja Ali / بنجة علي", "Darwaza / دروازة", "Kurdistan Neighborhood / حي كردستان",
    "Baghdad Road / طريق بغداد", "Wasit / واسط", "Domiz / دوميز",
    "June 1st / ١ حزيران", "Majidiya / المجيدية", "Al-Beiji / البيجي",
    "Mansour / المنصور", "Razgari / رزگاري", "Ghazna / غزنة",
    "Hay Aden / حي عدن", "Taseen / تسعين", "Khazra / خضراء",
    "Beiji / بيجي", "Qadisiyah / قادسية", "Panorama / بانوراما",
    "Barutkhana / باروته خانه", "Engineers Neighborhood / حي المهندسين",
    "Teachers Neighborhood / حي المعلمين", "Al-Mas / المس", "Al-Mithaq / الميثاق",
    "Al-Ta'mim / التأميم", "Al-Qadisiyah / القادسية", "Al-Jamea / الجامعة",
    "Al-Muhandiseen / المهندسين", "Al-Andalus / الأندلس", "Al-Jumhouriya / الجمهورية",
    "Domeez / دوميز", "Al-Wafa / الوفاء", "Al-Nour / النور", "Al-Muthanna / المثنى",
    "Al-Khadra / الخضراء", "Sarchinar / سرچنار", "Muhammad Ali / محمد علي",
    "Al-Mashtal / المشتل", "Al-Shuhada / الشهداء", "Al-Hurriya / الحرية",
    "Al-Sina'a / الصناعة", "Al-Masbin / المسبين", "Al-Sa'ad / السعد",
    "Bakhtiari / بختياري", "Bawer / باور", "Camp / مخيم", "Chay / جاي",
    "Choman / جومان", "Hasar / حصر", "Kani Askan / كاني عسكر",
    "Kani Qrzhala / كاني قرژالة", "Laylan / ليلان", "Rizgary / رزگاري",
    "Taza / طازة", "Yarmuk / يرموك", "Zab / زاب"
])

# ==================== Application Entry Point ====================

if __name__ == "__main__":
    main()
