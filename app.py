I'll integrate Google Authentication and completely redesign the UI to be more professional and polished. Here's the enhanced version with modern design patterns, smooth animations, and Google OAuth integration.

```python
import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import uuid
import json
import plotly.express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
import time
import re
import hashlib
import logging
from functools import wraps
import io
from typing import Optional, Dict, Any
import base64

# For Google OAuth
from google.oauth2 import id_token
from google.auth.transport import requests
import requests as http_requests

# --- CONFIGURATION CONSTANTS ---
class Config:
    COMPANY_NAME = "گۆڵدن دلیڤەری پرۆ"
    VERSION = "3.0.0"
    MIN_PRICE_FOR_FREE = 3000
    USD_TO_IQD_RATE = 1460
    LOYALTY_POINTS_RATE = 1000
    DELIVERY_HOURS = 24
    CACHE_TTL = 300
    # Google OAuth Config
    GOOGLE_CLIENT_ID = "YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com"  # Replace with your actual Client ID
    GOOGLE_CLIENT_SECRET = "YOUR_GOOGLE_CLIENT_SECRET"  # Replace with your actual Client Secret

# --- LOGGING SETUP ---
logging.basicConfig(
    filename='golden_delivery.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="گۆڵدن دلیڤەری پرۆ - کەرکوک", 
    layout="wide", 
    initial_sidebar_state="collapsed",
    page_icon="🚚"
)

# --- 2. DATA VALIDATION FUNCTIONS ---
def validate_phone(phone: str) -> bool:
    """Validate Iraqi phone numbers"""
    if not phone:
        return False
    pattern = r'^07[0-9]{9}$'
    return bool(re.match(pattern, str(phone)))

def validate_email(email: str) -> bool:
    """Basic email validation"""
    if not email:
        return True
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_price(price: float, currency: str) -> bool:
    """Validate price based on currency"""
    if currency == 'IQD':
        return 0 <= price <= 10000000
    else:
        return 0 <= price <= 10000

# --- 3. GOOGLE AUTHENTICATION ---
class GoogleAuth:
    @staticmethod
    def verify_google_token(token: str) -> Optional[Dict[str, Any]]:
        """Verify Google OAuth token"""
        try:
            # Verify the token
            idinfo = id_token.verify_oauth2_token(
                token, 
                requests.Request(), 
                Config.GOOGLE_CLIENT_ID
            )
            
            # Check if token is valid
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
                
            return {
                'email': idinfo['email'],
                'name': idinfo.get('name', ''),
                'picture': idinfo.get('picture', ''),
                'google_id': idinfo['sub'],
                'verified_email': idinfo.get('email_verified', False)
            }
        except Exception as e:
            logging.error(f"Google token verification failed: {e}")
            return None
    
    @staticmethod
    def create_google_login_url() -> str:
        """Create Google OAuth login URL"""
        redirect_uri = "http://localhost:8501"  # Update for production
        scope = "openid email profile"
        auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id={Config.GOOGLE_CLIENT_ID}&redirect_uri={redirect_uri}&scope={scope}&access_type=offline&prompt=consent"
        return auth_url

# --- 4. INITIALIZE SESSION STATES ---
def init_session_states():
    defaults = {
        'page': "home",
        'user_email': None,
        'user_role': "customer",
        'user_name': None,
        'user_phone': None,
        'user_id': None,
        'admin_authenticated': False,
        'lang_choice': "کوردی 🇭🇺",
        'driver_id': None,
        'cart': [],
        'notifications': [],
        'order_history': [],
        'favorites': [],
        'current_order_id': None,
        'currency': 'IQD',
        'offline_orders': [],
        'notification_preferences': {'sms': True, 'email': True, 'whatsapp': True},
        'online': True,
        'authenticated': False,
        'theme': 'light',
        'last_activity': datetime.now(),
        'google_user': None,
        'auth_method': None
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_states()

# --- 5. COMPANY INFO ---
COMPANY_PHONES = ["07801352003", "07721959922"]
COMPANY_EMAIL = "Danyalexpert@gmail.com"
COMPANY_ADDRESS = "کەرکوک، شەقامی سەرەکی"
COMPANY_WHATSAPP = "https://wa.me/9647801352003"
EMERGENCY_POLICE = "104"
EMERGENCY_AMBULANCE = "122"

# --- 6. COMPLETE NEIGHBORHOODS LIST ---
KIRKUK_AREAS = sorted([
    "Arfa / عرفة", "Tis'in / تسعين", "Shoraw / شوراو",
    "Rahim Awa / رحيماوة", "Quraya / قورية", "Al-Wasiti / الواسطي",
    "Al-Nasr / النصر", "Azadi / ازادي", "Wahid Huzairan / واحد حزيران",
    "Kirkuk Citadel / قلعة كركوك", "Musalla / مصلى", "Imam Qasim / امام قاسم",
    "Shorija / الشورجة", "Hasiraka / حصيرةكة", "Tapai Malla Abdulla / تبة ملا عبدulla",
    "Rahimawa / رحيم آوه", "Almas / الماس", "Arafa / عرفة",
    "Faylaq / فيلق", "Panja Ali / بنجة علي", "Darwaza / دروازة",
    "Kurdistan Neighborhood / حي كردستان", "Baghdad Road / طريق بغداد",
    "Wasit / واسط", "Domiz / دوميز", "June 1st / ١ حزيران",
    "Majidiya / المجيدية", "Al-Beiji / البيجي", "Mansour / المنصور",
    "Razgari / رزگاري", "Ghazna / غزنة", "Hay Aden / حي عدن",
    "Taseen / تسعين", "Khazra / خضراء", "Beiji / بيجي",
    "Qadisiyah / قادسية", "Panorama / بانوراما", "Barutkhana / باروته خانه",
    "Engineers Neighborhood / حي المهندسين", "Teachers Neighborhood / حي المعلمين"
])

# --- 7. MULTI-LANGUAGE UI STRINGS ---
languages = {
    "English 🇬🇧": {
        "dir": "ltr", "align": "left",
        "title": "GOLDEN DELIVERY PRO",
        "desc": "Premium logistics solutions in Kirkuk - Fast, Secure, Reliable",
        "nav_home": "Home", "nav_order": "New Order", "nav_track": "Track",
        "nav_offers": "Offers", "nav_profile": "Account", "nav_terms": "Terms",
        "nav_support": "Support", "nav_emergency": "Emergency",
        "customer_name": "Customer Name", "shop_name": "Shop Name",
        "shop_addr": "Shop Address", "phone": "Phone Number",
        "area": "Neighborhood", "full_addr": "Address Details",
        "price": "Price (IQD)", "submit": "Confirm Order",
        "free_info": "🎁 Special Offer: 1 out of every 3 deliveries is FREE!",
        "free_success": "🎊 Congratulations! This delivery is FREE!",
        "google_btn": "Continue with Google", "logout": "Sign Out",
        "settings": "Settings", "admin_pass_label": "Admin Password",
        "admin_error": "❌ Incorrect Password", "mgmt_links": "Management Dashboard",
        "terms_title": "📜 Terms & Conditions", "contact_us": "Contact Us",
        "call_us": "Call", "whatsapp_us": "WhatsApp",
        "email_us": "Email", "visit_us": "Visit",
        "fast_title": "⚡ Express Delivery", "fast_desc": "24-hour delivery guarantee",
        "secure_title": "🔒 Secure", "secure_desc": "Your packages are fully insured",
        "free_title": "🎁 Loyalty Rewards", "free_desc": "Every 3rd delivery is free",
        "loyalty_points": "Loyalty Points", "points_balance": "Points Balance",
        "redeem_points": "Redeem Points", "delivery_notes": "Delivery Notes",
        "gate_code": "Gate Code", "building_number": "Building No.",
        "order_id": "Order ID", "order_status": "Status",
        "estimated_delivery": "Estimated Delivery", "track_order": "Track Order",
        "rate_delivery": "Rate Delivery", "leave_review": "Write a Review",
        "submit_feedback": "Submit Feedback", "promo_code": "Promo Code",
        "apply_promo": "Apply", "promo_applied": "Promo Applied!",
        "invalid_promo": "Invalid Promo Code", "payment_method": "Payment Method",
        "cash_on_delivery": "Cash on Delivery", "bank_transfer": "Bank Transfer",
        "zain_cash": "Zain Cash", "asia_hawala": "Asia Hawala",
        "whatsapp_question": "💬 Chat on WhatsApp", "emergency_call": "🚨 Emergency",
        "police": "Police", "ambulance": "Ambulance",
        "currency_iqd": "IQD", "currency_usd": "USD",
        "reminder": "Reminder", "delivery_reminder": "Your delivery arrives in 1 hour",
        "eid_offer": "🎊 Eid Mubarak Offer",
        "ramadan_offer": "🌙 Ramadan Special",
        "nowruz_offer": "🌸 Happy Nowruz",
        "access_account": "Sign in to access your account",
        "golden_rules": "Golden Rules",
        "rule1": "1 out of 3 deliveries is free - automatically applied!",
        "rule2": "No illegal items - we comply with all local laws",
        "rule3": "Fast Kirkuk-wide service - all neighborhoods covered",
        "rule4": "Delivery within 24 hours of order confirmation",
        "rule5": "Multiple payment options available",
        "rule6": "Free delivery promotion applies to orders over 3000 IQD",
        "rule7": "Customer must be present at time of delivery",
        "signed_in_as": "Signed in as",
        "total_orders": "Total Orders",
        "delivered": "Delivered",
        "free_deliveries": "Free Deliveries",
        "average": "Average",
        "welcome_back": "Welcome back",
        "new_here": "New here?",
        "create_account": "Create Account",
        "sign_in": "Sign In",
        "email_address": "Email Address",
        "password": "Password",
        "confirm_password": "Confirm Password",
        "full_name": "Full Name",
        "remember_me": "Remember me",
        "forgot_password": "Forgot Password?",
        "or_continue_with": "Or continue with"
    },
    "کوردی 🇭🇺": {
        "dir": "rtl", "align": "right",
        "title": "گۆڵدن دلیڤەری پرۆ",
        "desc": "خزمەتگوزاری لۆجستی بالای کەرکوک - خێرا، پارێزراو، متمانەپێکراو",
        "nav_home": "سەرەکی", "nav_order": "داواکاری نوێ", "nav_track": "شوێنکەوتن",
        "nav_offers": "پێشکەشکراوەکان", "nav_profile": "هەژمار", "nav_terms": "یاساکان",
        "nav_support": "پاڵپشتی", "nav_emergency": "فریاکەوتن",
        "customer_name": "ناوی کڕیار", "shop_name": "ناوی دوکان",
        "shop_addr": "ناونیشانی دوکان", "phone": "ژمارەی مۆبایل",
        "area": "گەڕەک", "full_addr": "وردەکاری ناونیشان",
        "price": "نرخ (د.ع)", "submit": "تۆمارکردنی داواکاری",
        "free_info": "🎁 پێشکەشکردنی تایبەت: یەکێک لە هەر ٣ گەیاندن بە خۆڕاییە!",
        "free_success": "🎊 پیرۆزە! ئەم گەیاندنە بە خۆڕاییە!",
        "google_btn": "بەردەوامبوون بە Google", "logout": "چوونەدەرەوە",
        "settings": "ڕێکخستنەکان", "admin_pass_label": "وشەی نهێنی ئەدمین",
        "admin_error": "❌ وشەی نهێنی هەڵەیە", "mgmt_links": "داشبۆردی بەڕێوەبردن",
        "terms_title": "📜 مەرج و یاساکان", "contact_us": "پەیوەندیمان پێوە بکە",
        "call_us": "پەیوەندی", "whatsapp_us": "واتسئاپ",
        "email_us": "ئیمەیڵ", "visit_us": "سەردان",
        "fast_title": "⚡ گەیاندنی خێرا", "fast_desc": "گەرەنتی گەیاندنی ٢٤ کاتژمێری",
        "secure_title": "🔒 پارێزراو", "secure_desc": "پاکەتەکانت بە تەواوی دڵنیاکراون",
        "free_title": "🎁 خەڵاتی دڵسۆزی", "free_desc": "هەر سێیەم گەیاندن بە خۆڕاییە",
        "loyalty_points": "خاڵی دڵسۆزی", "points_balance": "ڕێژەی خاڵەکان",
        "redeem_points": "بەکارهێنانی خاڵەکان", "delivery_notes": "تێبینی گەیاندن",
        "gate_code": "کۆدی دەروازە", "building_number": "ژ. باڵەخانە",
        "order_id": "ژمارەی داواکاری", "order_status": "دۆخ",
        "estimated_delivery": "کاتی گەیاندن", "track_order": "شوێنکەوتن",
        "rate_delivery": "هەڵسەنگاندن", "leave_review": "بۆچوون بنووسە",
        "submit_feedback": "ناردن", "promo_code": "کۆدی پڕۆمۆ",
        "apply_promo": "جێبەجێکردن", "promo_applied": "پڕۆمۆ جێبەجێ کرا!",
        "invalid_promo": "کۆدی پڕۆمۆ نادروستە", "payment_method": "شێوازی پارەدان",
        "cash_on_delivery": "پارەدان لە کاتی گەیاندن", "bank_transfer": "گواستنەوەی بانکی",
        "zain_cash": "زەین کاش", "asia_hawala": "ئاسیا حەوالە",
        "whatsapp_question": "💬 گفتوگۆ لە واتسئاپ", "emergency_call": "🚨 فریاکەوتن",
        "police": "پۆلیس", "ambulance": "فریاکەوتن",
        "currency_iqd": "دینار", "currency_usd": "دۆلار",
        "reminder": "بیرخستنەوە", "delivery_reminder": "گەیاندنەکەت لە ماوەی ١ کاتژمێردا دەگات",
        "eid_offer": "🎊 پێشکەشکردنی جەژن",
        "ramadan_offer": "🌙 پێشکەشکردنی ڕەمەزان",
        "nowruz_offer": "🌸 پیرۆزبایی نەورۆز",
        "access_account": "بچۆ ژوورەوە بۆ هەژمارەکەت",
        "golden_rules": "ڕێسا زێڕینەکان",
        "rule1": "یەکێک لە هەر ٣ گەیاندنێک بە خۆڕاییە",
        "rule2": "هیچ کاڵایەکی نایاسایی نییە",
        "rule3": "خزمەتگوزاری خێرا لە سەرانسەری کەرکوک",
        "rule4": "گەیاندن لە ماوەی ٢٤ کاتژمێردا",
        "rule5": "چەندین شێوازی پارەدان بەردەستە",
        "rule6": "پڕۆمۆشنی خۆڕایی بۆ داواکاری سەرووی ٣٠٠٠ دینار",
        "rule7": "کڕیار دەبێت لە کاتی گەیاندن ئامادە بێت",
        "signed_in_as": "چوویتە ژوورەوە وەک",
        "total_orders": "کۆی داواکاری",
        "delivered": "گەیاندراو",
        "free_deliveries": "خۆڕایی",
        "average": "تێکڕا",
        "welcome_back": "بەخێربێیتەوە",
        "new_here": "تازەیت لێرە؟",
        "create_account": "دروستکردنی هەژمار",
        "sign_in": "چوونەژوورەوە",
        "email_address": "ناونیشانی ئیمەیڵ",
        "password": "وشەی نهێنی",
        "confirm_password": "دووپاتکردنەوەی وشەی نهێنی",
        "full_name": "ناوی تەواو",
        "remember_me": "بمبیربکە",
        "forgot_password": "وشەی نهێنیت لەبیرچووە؟",
        "or_continue_with": "یان بەردەوامبە بە"
    },
    "العربية 🇮🇶": {
        "dir": "rtl", "align": "right",
        "title": "جولدن دليفري برو",
        "desc": "حلول لوجستية متميزة في كركوك - سريعة، آمنة، موثوقة",
        "nav_home": "الرئيسية", "nav_order": "طلب جديد", "nav_track": "تتبع",
        "nav_offers": "العروض", "nav_profile": "الحساب", "nav_terms": "الشروط",
        "nav_support": "الدعم", "nav_emergency": "طوارئ",
        "customer_name": "اسم الزبون", "shop_name": "اسم المحل",
        "shop_addr": "عنوان المحل", "phone": "رقم الهاتف",
        "area": "المنطقة", "full_addr": "تفاصيل العنوان",
        "price": "السعر (د.ع)", "submit": "تأكيد الطلب",
        "free_info": "🎁 عرض خاص: واحدة من كل ٣ توصيلات مجانية!",
        "free_success": "🎊 مبروك! هذا التوصيل مجاني!",
        "google_btn": "المتابعة باستخدام Google", "logout": "تسجيل الخروج",
        "settings": "الإعدادات", "admin_pass_label": "كلمة مرور المسؤول",
        "admin_error": "❌ كلمة المرور غير صحيحة", "mgmt_links": "لوحة الإدارة",
        "terms_title": "📜 الشروط والأحكام", "contact_us": "اتصل بنا",
        "call_us": "اتصال", "whatsapp_us": "واتساب",
        "email_us": "البريد الإلكتروني", "visit_us": "زيارة",
        "fast_title": "⚡ توصيل سريع", "fast_desc": "ضمان التوصيل خلال ٢٤ ساعة",
        "secure_title": "🔒 آمن", "secure_desc": "طرودك مؤمنة بالكامل",
        "free_title": "🎁 مكافآت الولاء", "free_desc": "كل ثالث توصيلة مجانية",
        "loyalty_points": "نقاط الولاء", "points_balance": "رصيد النقاط",
        "redeem_points": "استبدال النقاط", "delivery_notes": "ملاحظات التوصيل",
        "gate_code": "رمز البوابة", "building_number": "رقم المبنى",
        "order_id": "رقم الطلب", "order_status": "الحالة",
        "estimated_delivery": "موعد التوصيل", "track_order": "تتبع الطلب",
        "rate_delivery": "تقييم التوصيل", "leave_review": "كتابة مراجعة",
        "submit_feedback": "إرسال", "promo_code": "كود الخصم",
        "apply_promo": "تطبيق", "promo_applied": "تم تطبيق الخصم!",
        "invalid_promo": "كود خصم غير صالح", "payment_method": "طريقة الدفع",
        "cash_on_delivery": "الدفع عند الاستلام", "bank_transfer": "تحويل بنكي",
        "zain_cash": "زين كاش", "asia_hawala": "آسيا حوالة",
        "whatsapp_question": "💬 محادثة واتساب", "emergency_call": "🚨 طوارئ",
        "police": "شرطة", "ambulance": "إسعاف",
        "currency_iqd": "دينار", "currency_usd": "دولار",
        "reminder": "تذكير", "delivery_reminder": "سيصل طلبك خلال ساعة",
        "eid_offer": "🎊 عرض العيد",
        "ramadan_offer": "🌙 عرض رمضان",
        "nowruz_offer": "🌸 نوروز مبارك",
        "access_account": "سجل الدخول للوصول إلى حسابك",
        "golden_rules": "القواعد الذهبية",
        "rule1": "واحدة من كل ٣ توصيلات مجانية",
        "rule2": "لا توجد عناصر غير قانونية",
        "rule3": "خدمة سريعة في جميع أنحاء كركوك",
        "rule4": "التوصيل خلال ٢٤ ساعة",
        "rule5": "خيارات دفع متعددة متاحة",
        "rule6": "عرض التوصيل المجاني للطلبات فوق ٣٠٠٠ دينار",
        "rule7": "يجب أن يكون الزبون حاضراً وقت التوصيل",
        "signed_in_as": "مسجل الدخول باسم",
        "total_orders": "إجمالي الطلبات",
        "delivered": "تم التوصيل",
        "free_deliveries": "مجاني",
        "average": "المعدل",
        "welcome_back": "مرحباً بعودتك",
        "new_here": "جديد هنا؟",
        "create_account": "إنشاء حساب",
        "sign_in": "تسجيل الدخول",
        "email_address": "البريد الإلكتروني",
        "password": "كلمة المرور",
        "confirm_password": "تأكيد كلمة المرور",
        "full_name": "الاسم الكامل",
        "remember_me": "تذكرني",
        "forgot_password": "نسيت كلمة المرور؟",
        "or_continue_with": "أو تابع باستخدام"
    }
}

# --- 8. DATA FILES ---
ORDERS_FILE = "orders.csv"
DRIVERS_FILE = "drivers.csv"
CUSTOMERS_FILE = "customers.csv"
FEEDBACK_FILE = "feedback.csv"
PROMO_CODES_FILE = "promos.json"
OFFLINE_ORDERS_FILE = "offline_orders.json"
USERS_FILE = "users.json"

# --- 9. SAFE DATA LOADING FUNCTIONS ---
def safe_load_data(file_path: str, default_data, file_type: str = 'csv'):
    """Safely load data with error handling"""
    try:
        if os.path.exists(file_path):
            if file_type == 'csv':
                return pd.read_csv(file_path, dtype={"phone": str, "order_id": str, "user_id": str})
            elif file_type == 'json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        return default_data
    except Exception as e:
        logging.error(f"Error loading {file_path}: {e}")
        return default_data

def safe_save_data(data, file_path: str, file_type: str = 'csv'):
    """Safely save data with error handling"""
    try:
        if file_type == 'csv':
            data.to_csv(file_path, index=False)
        elif file_type == 'json':
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        logging.error(f"Error saving {file_path}: {e}")
        return False

# --- 10. DATA FUNCTIONS (Cached) ---
@st.cache_data(ttl=Config.CACHE_TTL)
def load_orders():
    default_df = pd.DataFrame(columns=["order_id", "date", "customer", "shop", "phone", "area", 
                                        "address", "shop_addr", "price", "status", "user_email", 
                                        "user_id", "driver_id", "payment_method", "delivery_notes", "promo_code",
                                        "estimated_delivery", "actual_delivery", "rating", "review",
                                        "currency", "reminder_sent"])
    return safe_load_data(ORDERS_FILE, default_df, 'csv')

def save_orders(df):
    if 'user_id' not in df.columns:
        df['user_id'] = None
    safe_save_data(df, ORDERS_FILE, 'csv')
    st.cache_data.clear()

@st.cache_data(ttl=Config.CACHE_TTL)
def load_drivers():
    default_df = pd.DataFrame(columns=["driver_id", "name", "phone", "status", "join_date", "total_deliveries", "rating", "language"])
    return safe_load_data(DRIVERS_FILE, default_df, 'csv')

def save_drivers(df):
    safe_save_data(df, DRIVERS_FILE, 'csv')
    st.cache_data.clear()

@st.cache_data(ttl=Config.CACHE_TTL)
def load_customers():
    default_df = pd.DataFrame(columns=["user_id", "name", "phone", "email", "join_date", 
                                        "total_orders", "loyalty_points", "total_spent",
                                        "language", "notification_preferences", "auth_provider", "google_id"])
    df = safe_load_data(CUSTOMERS_FILE, default_df, 'csv')
    
    if 'user_id' not in df.columns or df['user_id'].isna().any():
        df['user_id'] = [f"USR-{str(uuid.uuid4())[:8].upper()}" for _ in range(len(df))]
        save_customers(df)
    return df

def save_customers(df):
    if 'user_id' not in df.columns:
        df['user_id'] = [f"USR-{str(uuid.uuid4())[:8].upper()}" for _ in range(len(df))]
    safe_save_data(df, CUSTOMERS_FILE, 'csv')
    st.cache_data.clear()

@st.cache_data(ttl=Config.CACHE_TTL)
def load_feedback():
    default_df = pd.DataFrame(columns=["feedback_id", "order_id", "customer_name", "rating", "review", "date"])
    return safe_load_data(FEEDBACK_FILE, default_df, 'csv')

def save_feedback(df):
    safe_save_data(df, FEEDBACK_FILE, 'csv')
    st.cache_data.clear()

@st.cache_data(ttl=Config.CACHE_TTL)
def load_promos():
    default_promos = {
        "WELCOME10": {"discount": 10, "type": "percentage", "min_order": 5000, "expiry": "2027-12-31"},
        "FREESHIP": {"discount": 3000, "type": "fixed", "min_order": 10000, "expiry": "2027-12-31"},
        "FIRST3": {"discount": 15, "type": "percentage", "min_order": 3000, "expiry": "2027-12-31"},
        "GOLDEN50": {"discount": 50, "type": "percentage", "min_order": 20000, "expiry": "2027-12-31"},
        "KIRKUK10": {"discount": 10, "type": "percentage", "min_order": 0, "expiry": "2027-12-31"},
        "EID2025": {"discount": 25, "type": "percentage", "min_order": 10000, "expiry": "2027-12-31"},
        "RAMADAN": {"discount": 20, "type": "percentage", "min_order": 5000, "expiry": "2027-12-31"},
        "NOWRUZ": {"discount": 30, "type": "percentage", "min_order": 15000, "expiry": "2027-12-31"}
    }
    return safe_load_data(PROMO_CODES_FILE, default_promos, 'json')

def save_promos(promos):
    safe_save_data(promos, PROMO_CODES_FILE, 'json')
    st.cache_data.clear()

def load_offline_orders():
    return safe_load_data(OFFLINE_ORDERS_FILE, [], 'json')

def save_offline_orders(orders):
    safe_save_data(orders, OFFLINE_ORDERS_FILE, 'json')

def load_users():
    return safe_load_data(USERS_FILE, {}, 'json')

def save_users(users):
    safe_save_data(users, USERS_FILE, 'json')

# --- 11. AUTHENTICATION MANAGER ---
class AuthManager:
    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def register_user(email: str, password: str, name: str, phone: str, role: str = "customer", auth_provider: str = "email"):
        if auth_provider == "email":
            if not validate_email(email):
                return False, "ئیمەیڵی نادروست"
            if not validate_phone(phone):
                return False, "ژمارەی مۆبایلی نادروست"
        
        users = load_users()
        if email in users:
            return False, "ئەم ئیمەیڵە پێشتر تۆمارکراوە"
        
        user_id = generate_user_id()
        users[email] = {
            "password": AuthManager.hash_password(password) if password else None,
            "name": name,
            "phone": phone,
            "role": role,
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "last_login": datetime.now().isoformat(),
            "auth_provider": auth_provider
        }
        
        if save_users(users):
            logging.info(f"New user registered: {email} via {auth_provider}")
            return True, {"user_id": user_id, "name": name, "phone": phone, "role": role}
        return False, "کێشە لە تۆمارکردن"
    
    @staticmethod
    def authenticate(email: str, password: str):
        users = load_users()
        if email in users:
            user = users[email]
            if user.get("auth_provider") == "google":
                return False, "ئەم هەژمارە لە ڕێگەی Google ەوە دروستکراوە. تکایە بە Google بچۆ ژوورەوە"
            if user["password"] == AuthManager.hash_password(password):
                users[email]["last_login"] = datetime.now().isoformat()
                save_users(users)
                logging.info(f"User logged in: {email}")
                return True, user
        return False, "ئیمەیڵ یان وشەی نهێنی هەڵەیە"
    
    @staticmethod
    def authenticate_google(email: str, name: str, google_id: str):
        users = load_users()
        
        if email in users:
            # Update existing user
            users[email]["last_login"] = datetime.now().isoformat()
            users[email]["name"] = name
            save_users(users)
            return True, users[email]
        else:
            # Create new user
            user_id = generate_user_id()
            users[email] = {
                "password": None,
                "name": name,
                "phone": None,
                "role": "customer",
                "user_id": user_id,
                "created_at": datetime.now().isoformat(),
                "last_login": datetime.now().isoformat(),
                "auth_provider": "google",
                "google_id": google_id
            }
            save_users(users)
            logging.info(f"New Google user registered: {email}")
            return True, users[email]

# --- 12. HELPER FUNCTIONS ---
def generate_order_id() -> str:
    return f"GD-{datetime.now().strftime('%Y%m')}-{str(uuid.uuid4())[:8].upper()}"

def generate_user_id() -> str:
    return f"USR-{str(uuid.uuid4())[:8].upper()}"

def calculate_loyalty_points(price: float) -> int:
    return int(price / Config.LOYALTY_POINTS_RATE)

def validate_promo_code(code: str, price: float, promos: dict) -> tuple:
    if code in promos:
        promo = promos[code]
        try:
            expiry_date = datetime.strptime(promo['expiry'], '%Y-%m-%d')
            if expiry_date > datetime.now():
                if price >= promo['min_order']:
                    if promo['type'] == 'percentage':
                        discount = (price * promo['discount']) / 100
                    else:
                        discount = promo['discount']
                    return True, discount, promo
        except Exception as e:
            logging.error(f"Promo validation error: {e}")
    return False, 0, None

def send_whatsapp_message(phone: str, message: str) -> str:
    encoded_message = message.replace(' ', '%20').replace('،', ',').replace('؟', '')
    return f"https://wa.me/{phone}?text={encoded_message}"

def send_sms_reminder(phone: str, order_id: str) -> bool:
    L = languages[st.session_state.lang_choice]
    message = f"{L['delivery_reminder']} - {L['order_id']}: {order_id}"
    logging.info(f"SMS reminder sent to {phone} for order {order_id}")
    return True

def get_order_status_emoji(status: str) -> str:
    emojis = {
        "Pending": "⏳", "Picked Up": "📦", "In Transit": "🚚",
        "Out for Delivery": "🚪", "Delivered": "✅", "Cancelled": "❌"
    }
    return emojis.get(status, "📦")

def calculate_estimated_delivery() -> str:
    return (datetime.now() + timedelta(hours=Config.DELIVERY_HOURS)).strftime("%Y-%m-%d %H:%M")

def convert_currency(amount: float, from_currency: str, to_currency: str) -> float:
    if from_currency == to_currency:
        return amount
    if from_currency == 'USD' and to_currency == 'IQD':
        return amount * Config.USD_TO_IQD_RATE
    elif from_currency == 'IQD' and to_currency == 'USD':
        return amount / Config.USD_TO_IQD_RATE
    return amount

def update_customer_loyalty(phone: str, name: str, email: str, price: float):
    customers_df = load_customers()
    user_found = False
    
    if st.session_state.user_id:
        mask = customers_df['user_id'] == st.session_state.user_id
        if mask.any():
            idx = customers_df[mask].index[0]
            customers_df.loc[idx, 'loyalty_points'] += calculate_loyalty_points(price)
            customers_df.loc[idx, 'total_orders'] += 1
            customers_df.loc[idx, 'total_spent'] += price
            if name and pd.isna(customers_df.loc[idx, 'name']):
                customers_df.loc[idx, 'name'] = name
            if email and pd.isna(customers_df.loc[idx, 'email']):
                customers_df.loc[idx, 'email'] = email
            user_found = True
    elif phone:
        mask = customers_df['phone'] == phone
        if mask.any():
            idx = customers_df[mask].index[0]
            customers_df.loc[idx, 'loyalty_points'] += calculate_loyalty_points(price)
            customers_df.loc[idx, 'total_orders'] += 1
            customers_df.loc[idx, 'total_spent'] += price
            if name and pd.isna(customers_df.loc[idx, 'name']):
                customers_df.loc[idx, 'name'] = name
            if email and pd.isna(customers_df.loc[idx, 'email']):
                customers_df.loc[idx, 'email'] = email
            st.session_state.user_id = customers_df.loc[idx, 'user_id']
            user_found = True
    
    if not user_found:
        new_user_id = generate_user_id()
        new_customer = pd.DataFrame([{
            "user_id": new_user_id,
            "name": name or "Unknown",
            "phone": phone,
            "email": email or "",
            "join_date": datetime.now().strftime("%Y-%m-%d"),
            "total_orders": 1,
            "loyalty_points": calculate_loyalty_points(price),
            "total_spent": price,
            "language": st.session_state.lang_choice,
            "notification_preferences": json.dumps(st.session_state.notification_preferences),
            "auth_provider": "guest",
            "google_id": None
        }])
        customers_df = pd.concat([customers_df, new_customer], ignore_index=True)
        st.session_state.user_id = new_user_id
    
    save_customers(customers_df)
    logging.info(f"Customer loyalty updated: {phone} - Points added: {calculate_loyalty_points(price)}")

def get_holiday_offer() -> str:
    today = datetime.now()
    month = today.month
    day = today.day
    
    if month == 4 and day > 10:
        return "RAMADAN"
    elif month == 3 and day == 21:
        return "NOWRUZ"
    elif month == 7 and day > 15:
        return "EID2025"
    return None

def add_notification(message: str, type: str = "info"):
    """Add notification to session state"""
    if 'notifications' not in st.session_state:
        st.session_state.notifications = []
    
    st.session_state.notifications.append({
        "id": str(uuid.uuid4()),
        "message": message,
        "type": type,
        "timestamp": datetime.now().isoformat(),
        "read": False
    })

def create_order_timeline(order_status: str):
    """Create a visual timeline for order status"""
    statuses = ["Pending", "Picked Up", "In Transit", "Out for Delivery", "Delivered"]
    current_index = statuses.index(order_status) if order_status in statuses else 0
    
    fig = go.Figure()
    
    for i, status in enumerate(statuses):
        color = "#D4AF37" if i <= current_index else "#e0e0e0"
        fig.add_trace(go.Scatter(
            x=[i], y=[0],
            mode='markers+text',
            marker=dict(size=20, color=color, symbol='circle'),
            text=status,
            textposition="top center",
            name=status,
            textfont=dict(size=10)
        ))
        
        if i < len(statuses) - 1:
            line_color = "#D4AF37" if i < current_index else "#e0e0e0"
            fig.add_trace(go.Scatter(
                x=[i, i+1], y=[0, 0],
                mode='lines',
                line=dict(color=line_color, width=3),
                showlegend=False
            ))
    
    fig.update_layout(
        showlegend=False,
        height=120,
        xaxis=dict(showticklabels=False, showgrid=False, range=[-0.5, 4.5]),
        yaxis=dict(showticklabels=False, showgrid=False),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0)
    )
    
    return fig

# --- 13. PROFESSIONAL UI COMPONENTS ---
def load_css():
    """Load professional CSS styling"""
    theme = st.session_state.get('theme', 'light')
    
    if theme == 'dark':
        bg_color = "#0f172a"
        card_bg = "#1e293b"
        text_color = "#f1f5f9"
        accent = "#fbbf24"
        secondary = "#64748b"
        border_color = "#334155"
        input_bg = "#1e293b"
        gradient_start = "#fbbf24"
        gradient_end = "#f59e0b"
    else:
        bg_color = "#f8fafc"
        card_bg = "#ffffff"
        text_color = "#1e293b"
        accent = "#d97706"
        secondary = "#64748b"
        border_color = "#e2e8f0"
        input_bg = "#ffffff"
        gradient_start = "#d97706"
        gradient_end = "#b45309"
    
    st.markdown(f"""
    <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        /* Global Styles */
        * {{
            font-family: 'Inter', sans-serif;
        }}
        
        [data-testid="stSidebar"] {{ display: none; }}
        
        .stApp {{
            background: linear-gradient(135deg, {bg_color} 0%, {bg_color}dd 100%);
        }}
        
        /* Custom Scrollbar */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        ::-webkit-scrollbar-track {{
            background: {card_bg};
            border-radius: 10px;
        }}
        ::-webkit-scrollbar-thumb {{
            background: {accent}80;
            border-radius: 10px;
        }}
        ::-webkit-scrollbar-thumb:hover {{
            background: {accent};
        }}
        
        /* Typography */
        h1, h2, h3, h4, h5, h6 {{
            color: {text_color} !important;
            font-weight: 700 !important;
            letter-spacing: -0.025em;
        }}
        
        p, span, div, label {{
            color: {text_color} !important;
        }}
        
        /* Cards */
        .premium-card {{
            background: {card_bg};
            border-radius: 24px;
            padding: 28px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
            border: 1px solid {border_color};
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            backdrop-filter: blur(10px);
        }}
        
        .premium-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.12);
            border-color: {accent}40;
        }}
        
        /* Hero Section */
        .hero-section {{
            background: linear-gradient(135deg, {gradient_start}15 0%, {gradient_end}05 100%);
            border-radius: 32px;
            padding: 48px 40px;
            margin-bottom: 32px;
            border: 1px solid {accent}20;
            position: relative;
            overflow: hidden;
        }}
        
        .hero-section::before {{
            content: '';
            position: absolute;
            top: -50%;
            right: -10%;
            width: 400px;
            height: 400px;
            background: radial-gradient(circle, {accent}10 0%, transparent 70%);
            border-radius: 50%;
        }}
        
        .hero-title {{
            font-size: 3.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, {accent} 0%, {gradient_end} 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 16px;
            line-height: 1.2;
        }}
        
        .hero-subtitle {{
            font-size: 1.25rem;
            color: {secondary};
            margin-bottom: 32px;
            line-height: 1.6;
        }}
        
        /* Stats Cards */
        .stat-card {{
            background: linear-gradient(135deg, {card_bg} 0%, {card_bg}dd 100%);
            border-radius: 20px;
            padding: 24px;
            text-align: center;
            border: 1px solid {border_color};
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }}
        
        .stat-card::after {{
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, {accent} 0%, {gradient_end} 100%);
            transform: scaleX(0);
            transition: transform 0.3s ease;
        }}
        
        .stat-card:hover::after {{
            transform: scaleX(1);
        }}
        
        .stat-value {{
            font-size: 2.5rem;
            font-weight: 800;
            color: {accent} !important;
            line-height: 1.2;
        }}
        
        .stat-label {{
            font-size: 0.95rem;
            color: {secondary} !important;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        /* Buttons */
        .stButton > button {{
            background: linear-gradient(135deg, {accent} 0%, {gradient_end} 100%);
            color: white !important;
            border: none !important;
            border-radius: 14px !important;
            padding: 12px 28px !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 15px {accent}40 !important;
            letter-spacing: -0.01em;
        }}
        
        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px {accent}60 !important;
        }}
        
        .stButton > button:active {{
            transform: translateY(0);
        }}
        
        /* Secondary Button */
        .secondary-btn > button {{
            background: {card_bg} !important;
            color: {text_color} !important;
            border: 1px solid {border_color} !important;
            box-shadow: none !important;
        }}
        
        .secondary-btn > button:hover {{
            border-color: {accent} !important;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08) !important;
        }}
        
        /* Google Button */
        .google-btn {{
            background: white !important;
            color: #1e293b !important;
            border: 1px solid #e2e8f0 !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06) !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            gap: 12px !important;
        }}
        
        .google-btn:hover {{
            background: #f8fafc !important;
            border-color: #cbd5e1 !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
        }}
        
        /* Input Fields */
        .stTextInput input, .stTextArea textarea, .stSelectbox select {{
            background: {input_bg} !important;
            border: 1.5px solid {border_color} !important;
            border-radius: 14px !important;
            padding: 12px 16px !important;
            font-size: 1rem !important;
            transition: all 0.2s ease !important;
            color: {text_color} !important;
        }}
        
        .stTextInput input:focus, .stTextArea textarea:focus {{
            border-color: {accent} !important;
            box-shadow: 0 0 0 3px {accent}20 !important;
            outline: none !important;
        }}
        
        /* Navigation Menu */
        .nav-container {{
            background: {card_bg};
            border-radius: 20px;
            padding: 8px;
            margin-bottom: 32px;
            border: 1px solid {border_color};
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
        }}
        
        /* Alert Messages */
        .stAlert {{
            border-radius: 16px !important;
            border: none !important;
            padding: 16px 20px !important;
            font-weight: 500 !important;
        }}
        
        /* Animations */
        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        .animate-in {{
            animation: fadeInUp 0.5s ease-out;
        }}
        
        /* Badge */
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 100px;
            font-size: 0.85rem;
            font-weight: 600;
            background: {accent}20;
            color: {accent} !important;
        }}
        
        /* Divider */
        .divider {{
            display: flex;
            align-items: center;
            text-align: center;
            margin: 24px 0;
            color: {secondary};
        }}
        
        .divider::before,
        .divider::after {{
            content: '';
            flex: 1;
            border-bottom: 1px solid {border_color};
        }}
        
        .divider span {{
            padding: 0 16px;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        /* Mobile Responsive */
        @media (max-width: 768px) {{
            .hero-title {{
                font-size: 2.5rem;
            }}
            .hero-section {{
                padding: 32px 24px;
            }}
            .premium-card {{
                padding: 20px;
            }}
        }}
    </style>
    """, unsafe_allow_html=True)

# Load CSS
load_css()

# --- 14. TOP BAR ---
L = languages[st.session_state.lang_choice]

# Create modern header
col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
with col1:
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 12px;">
        <div style="font-size: 32px;">🚚</div>
        <div>
            <h1 style="margin: 0; font-size: 1.8rem; font-weight: 800; background: linear-gradient(135deg, #d97706 0%, #b45309 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{L['title']}</h1>
            <p style="margin: 0; font-size: 0.85rem; color: #64748b; font-weight: 500;">Premium Delivery Service</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    lang_options = list(languages.keys())
    current_lang_index = lang_options.index(st.session_state.lang_choice)
    selected_lang = st.selectbox("🌐", lang_options, index=current_lang_index, label_visibility="collapsed", key="lang_select")
    if selected_lang != st.session_state.lang_choice:
        st.session_state.lang_choice = selected_lang
        st.rerun()

with col3:
    currency_options = ["IQD", "USD"]
    current_currency_index = 0 if st.session_state.currency == "IQD" else 1
    selected_currency = st.selectbox("💰", currency_options, index=current_currency_index, label_visibility="collapsed", key="currency_select")
    if selected_currency != st.session_state.currency:
        st.session_state.currency = selected_currency
        st.rerun()

with col4:
    if st.session_state.get('theme', 'light') == 'light':
        if st.button("🌙", key="theme_toggle", help="Switch to dark mode"):
            st.session_state.theme = 'dark'
            st.rerun()
    else:
        if st.button("☀️", key="theme_toggle", help="Switch to light mode"):
            st.session_state.theme = 'light'
            st.rerun()

L = languages[st.session_state.lang_choice]

# --- 15. NAVIGATION MENU ---
st.markdown('<div class="nav-container">', unsafe_allow_html=True)
selected = option_menu(
    menu_title=None,
    options=[L['nav_home'], L['nav_order'], L['nav_track'], L['nav_offers'], 
             L['nav_profile'], L['nav_terms'], L['nav_support'], L['nav_emergency']],
    icons=['house', 'box', 'map', 'gift', 'person', 'file-text', 'chat', 'exclamation-triangle'],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "4px", "background-color": "transparent"},
        "icon": {"color": "#d97706", "font-size": "16px"},
        "nav-link": {
            "font-size": "14px", 
            "text-align": "center", 
            "margin": "0px 4px", 
            "padding": "10px 20px", 
            "border-radius": "14px",
            "font-weight": "500",
            "transition": "all 0.2s ease"
        },
        "nav-link:hover": {
            "background-color": "#d9770620",
            "transform": "translateY(-2px)"
        },
        "nav-link-selected": {
            "background-color": "#d97706", 
            "color": "white",
            "font-weight": "600",
            "box-shadow": "0 4px 12px #d9770640"
        },
    }
)
st.markdown('</div>', unsafe_allow_html=True)

page_mapping = {
    L['nav_home']: "home", L['nav_order']: "order", L['nav_track']: "track",
    L['nav_offers']: "offers", L['nav_profile']: "profile", L['nav_terms']: "terms",
    L['nav_support']: "support", L['nav_emergency']: "emergency"
}
st.session_state.page = page_mapping.get(selected, "home")

# Display notifications
if st.session_state.get('notifications'):
    unread = [n for n in st.session_state.notifications if not n['read']]
    if unread:
        with st.container():
            for notif in unread[:3]:
                icon = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌"}
                st.info(f"{icon.get(notif['type'], '📌')} {notif['message']}")
                notif['read'] = True

# --- 16. HOME PAGE ---
if st.session_state.page == "home":
    holiday_offer = get_holiday_offer()
    if holiday_offer:
        if "RAMADAN" in holiday_offer:
            st.success(f"🌙 {L['ramadan_offer']}")
        elif "NOWRUZ" in holiday_offer:
            st.success(f"🌸 {L['nowruz_offer']}")
        elif "EID" in holiday_offer:
            st.success(f"🎊 {L['eid_offer']}")
    
    # Hero Section
    st.markdown(f"""
    <div class="hero-section animate-in">
        <h1 class="hero-title">{L['title']}</h1>
        <p class="hero-subtitle">{L['desc']}</p>
        <div style="display: flex; gap: 16px;">
            <span class="badge">🚀 Fast Delivery</span>
            <span class="badge">🔒 100% Secure</span>
            <span class="badge">⭐ Premium Service</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    orders_df = load_orders()
    
    # Statistics Section
    st.markdown("### 📊 Overview")
    
    if st.session_state.user_phone:
        user_orders = orders_df[orders_df['phone'] == st.session_state.user_phone]
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            total_orders = len(user_orders)
            st.markdown(f"""
            <div class="stat-card animate-in">
                <div class="stat-value">{total_orders}</div>
                <div class="stat-label">{L['total_orders']}</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            delivered = len(user_orders[user_orders['status'] == 'Delivered'])
            st.markdown(f"""
            <div class="stat-card animate-in">
                <div class="stat-value">{delivered}</div>
                <div class="stat-label">{L['delivered']}</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            free_deliveries = len(user_orders[user_orders['price'] == 0])
            st.markdown(f"""
            <div class="stat-card animate-in">
                <div class="stat-value">{free_deliveries}</div>
                <div class="stat-label">{L['free_deliveries']}</div>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            if len(user_orders) > 0:
                avg_price = int(user_orders['price'].mean())
                if st.session_state.currency == 'USD':
                    avg_price = convert_currency(avg_price, 'IQD', 'USD')
                    display_price = f"${avg_price:.2f}"
                else:
                    display_price = f"{avg_price:,}"
            else:
                display_price = "0"
            st.markdown(f"""
            <div class="stat-card animate-in">
                <div class="stat-value">{display_price}</div>
                <div class="stat-label">{L['average']}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info(f"🔑 {L['access_account']} {L['nav_profile']}")
    
    # Features Section
    st.markdown("### ✨ Why Choose Us")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="premium-card animate-in">
            <div style="font-size: 48px; margin-bottom: 16px;">⚡</div>
            <h3 style="margin-bottom: 12px;">{L['fast_title']}</h3>
            <p style="color: #64748b; line-height: 1.6;">{L['fast_desc']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="premium-card animate-in">
            <div style="font-size: 48px; margin-bottom: 16px;">🔒</div>
            <h3 style="margin-bottom: 12px;">{L['secure_title']}</h3>
            <p style="color: #64748b; line-height: 1.6;">{L['secure_desc']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="premium-card animate-in">
            <div style="font-size: 48px; margin-bottom: 16px;">🎁</div>
            <h3 style="margin-bottom: 12px;">{L['free_title']}</h3>
            <p style="color: #64748b; line-height: 1.6;">{L['free_desc']}</p>
        </div>
        """, unsafe_allow_html=True)

# --- 17. ORDER PAGE ---
elif st.session_state.page == "order":
    st.markdown(f"<h2 style='text-align:center; margin-bottom: 32px;'>📦 {L['nav_order']}</h2>", unsafe_allow_html=True)
    
    orders_df = load_orders()
    promos = load_promos()
    
    with st.container():
        st.markdown(f"""
        <div class="premium-card" style="margin-bottom: 24px;">
            <p style="font-size: 1.1rem; margin: 0;">{L['free_info']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        customer_name = st.text_input(L['customer_name'], value=st.session_state.user_name if st.session_state.user_name else "", placeholder="Enter full name")
        phone_input = st.text_input(L['phone'], placeholder="07xx xxx xxxx", value=st.session_state.user_phone if st.session_state.user_phone else "")
        shop_name = st.text_input(L['shop_name'], placeholder="Shop or business name")
    
    with col2:
        payment_method = st.selectbox(L['payment_method'], 
            [L['cash_on_delivery'], L['bank_transfer'], L['zain_cash'], L['asia_hawala']])
        delivery_notes = st.text_area(L['delivery_notes'], placeholder=f"{L['gate_code']}, {L['building_number']}")
    
    if phone_input and not validate_phone(phone_input):
        st.error("تکایە ژمارەی مۆبایلی دروست بنووسە (07xxxxxxxxx)")
    
    is_free = False
    if phone_input and validate_phone(phone_input):
        customer_orders = orders_df[orders_df['phone'] == phone_input]
        order_count = len(customer_orders)
        is_free = (order_count + 1) % 3 == 0
        if is_free:
            st.balloons()
            st.markdown(f"""
            <div class="premium-card" style="background: linear-gradient(135deg, #d9770620 0%, #b4530920 100%); border-color: #d97706;">
                <h4 style="color: #d97706 !important; margin: 0;">🎉 {L['free_success']}</h4>
            </div>
            """, unsafe_allow_html=True)
            add_notification(L["free_success"], "success")
    
    col1, col2 = st.columns(2)
    with col1:
        area = st.selectbox(L['area'], ["-- Select Neighborhood --"] + KIRKUK_AREAS)
        full_addr = st.text_area(L['full_addr'], placeholder="Street name, landmark, etc.")
    with col2:
        shop_addr = st.text_input(L['shop_addr'], placeholder="Shop location")
        
        base_price = 0 if is_free else Config.MIN_PRICE_FOR_FREE
        if st.session_state.currency == 'USD':
            base_price = convert_currency(base_price, 'IQD', 'USD')
            price = st.number_input(L['price'], value=float(base_price), min_value=0.0, step=0.5, format="%.2f")
        else:
            price = st.number_input(L['price'], value=base_price, min_value=0, step=500)
        
        promo_code = st.text_input(L['promo_code'], placeholder="Enter code")
        if promo_code:
            price_iqd = price if st.session_state.currency == 'IQD' else convert_currency(price, 'USD', 'IQD')
            valid, discount, promo = validate_promo_code(promo_code.upper(), price_iqd, promos)
            if valid:
                if st.session_state.currency == 'IQD':
                    price = int(price_iqd - discount)
                else:
                    price = convert_currency(int(price_iqd - discount), 'IQD', 'USD')
                st.success(f"✅ {L['promo_applied']} ({discount:,.0f} IQD)")
                add_notification(f"{L['promo_applied']} - {discount:,.0f} IQD", "success")
            else:
                st.warning(L['invalid_promo'])
    
    if phone_input and validate_phone(phone_input):
        message = f"Hello, I have a new delivery order for {area}"
        whatsapp_link = send_whatsapp_message(COMPANY_PHONES[0].replace('0', '964', 1), message)
        st.markdown(f"""
        <a href="{whatsapp_link}" target="_blank" style="text-decoration: none;">
            <div style="background: linear-gradient(135deg, #25D366 0%, #128C7E 100%); color: white; padding: 14px; border-radius: 14px; text-align: center; font-weight: 600; margin: 20px 0; transition: all 0.3s ease;">
                💬 {L['whatsapp_question']}
            </div>
        </a>
        """, unsafe_allow_html=True)
    
    if st.button(L['submit'], use_container_width=True):
        validation_errors = []
        
        if not customer_name:
            validation_errors.append("Customer name is required")
        if not phone_input:
            validation_errors.append("Phone number is required")
        elif not validate_phone(phone_input):
            validation_errors.append("Invalid phone number format")
        if not area or area == "-- Select Neighborhood --":
            validation_errors.append("Please select a neighborhood")
        
        if validation_errors:
            for error in validation_errors:
                st.error(error)
        else:
            order_id = generate_order_id()
            estimated_time = calculate_estimated_delivery()
            
            price_iqd = price if st.session_state.currency == 'IQD' else convert_currency(price, 'USD', 'IQD')
            
            new_order = pd.DataFrame([{
                "order_id": order_id,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "customer": customer_name,
                "shop": shop_name,
                "phone": phone_input,
                "area": area,
                "address": full_addr,
                "shop_addr": shop_addr,
                "price": int(price_iqd),
                "status": "Pending",
                "user_email": st.session_state.user_email,
                "user_id": st.session_state.user_id,
                "driver_id": None,
                "payment_method": payment_method,
                "delivery_notes": delivery_notes,
                "promo_code": promo_code if promo_code else None,
                "estimated_delivery": estimated_time,
                "actual_delivery": None,
                "rating": None,
                "review": None,
                "currency": st.session_state.currency,
                "reminder_sent": False
            }])
            
            if not st.session_state.get('online', True):
                offline_orders = load_offline_orders()
                offline_orders.append({
                    "order": new_order.to_dict('records')[0],
                    "created_at": datetime.now().isoformat()
                })
                save_offline_orders(offline_orders)
                st.info("📴 Order saved offline. Will sync when connection is restored.")
                add_notification("Order saved offline", "warning")
            else:
                orders_df = pd.concat([orders_df, new_order], ignore_index=True)
                save_orders(orders_df)
                update_customer_loyalty(phone_input, customer_name, st.session_state.user_email, int(price_iqd))
                st.success(f"✅ Order Confirmed! ID: {order_id}")
                st.balloons()
                st.session_state.current_order_id = order_id
                add_notification(f"New order created: {order_id}", "success")
                logging.info(f"New order created: {order_id} by {customer_name}")

# --- 18. TRACK PAGE ---
elif st.session_state.page == "track":
    st.markdown(f"<h2 style='text-align:center; margin-bottom: 32px;'>📍 {L['track_order']}</h2>", unsafe_allow_html=True)
    
    orders_df = load_orders()
    
    track_method = st.radio("", ["📱 Track by Phone", "🔢 Track by Order ID"], horizontal=True, label_visibility="collapsed")
    
    if "Phone" in track_method:
        phone = st.text_input(L['phone'], value=st.session_state.user_phone if st.session_state.user_phone else "", placeholder="07xx xxx xxxx")
        if phone:
            if validate_phone(phone):
                user_orders = orders_df[orders_df['phone'] == phone]
                if not user_orders.empty:
                    for _, order in user_orders.iterrows():
                        with st.expander(f"{order['order_id']} - {order['date']} - {get_order_status_emoji(order['status'])} {order['status']}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**{L['customer_name']}:** {order['customer']}")
                                st.write(f"**{L['area']}:** {order['area']}")
                                if st.session_state.currency == 'USD':
                                    price_display = convert_currency(order['price'], 'IQD', 'USD')
                                    st.write(f"**{L['price']}:** ${price_display:.2f}")
                                else:
                                    st.write(f"**{L['price']}:** {order['price']:,} {L['currency_iqd']}")
                            with col2:
                                st.write(f"**{L['order_status']}:** {order['status']}")
                                st.write(f"**{L['estimated_delivery']}:** {order['estimated_delivery']}")
                            
                            timeline = create_order_timeline(order['status'])
                            st.plotly_chart(timeline, use_container_width=True)
                            
                            if order['status'] == 'Out for Delivery' and not order.get('reminder_sent', False):
                                if st.button(f"🔔 {L['reminder']}", key=f"remind_{order['order_id']}"):
                                    send_sms_reminder(phone, order['order_id'])
                                    orders_df.loc[orders_df['order_id'] == order['order_id'], 'reminder_sent'] = True
                                    save_orders(orders_df)
                                    st.success(L['reminder'])
                else:
                    st.info("No orders found")
            else:
                st.error("Invalid phone number format")
    
    else:
        order_id = st.text_input(L['order_id'], placeholder="e.g., GD-202501-ABC123")
        if order_id:
            order = orders_df[orders_df['order_id'] == order_id]
            if not order.empty:
                order = order.iloc[0]
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                    <div class="premium-card">
                        <h4>{L['order_id']}: {order['order_id']}</h4>
                        <p><strong>{L['customer_name']}:</strong> {order['customer']}</p>
                        <p><strong>{L['area']}:</strong> {order['area']}</p>
                        <p><strong>{L['price']}:</strong> {order['price']:,} {L['currency_iqd']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="premium-card">
                        <h4>{L['order_status']}</h4>
                        <p style="font-size: 3rem; margin: 10px 0;">{get_order_status_emoji(order['status'])}</p>
                        <p><strong>{order['status']}</strong></p>
                        <p>{L['estimated_delivery']}: {order['estimated_delivery']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                timeline = create_order_timeline(order['status'])
                st.plotly_chart(timeline, use_container_width=True)
                
                if order['status'] == 'Delivered' and pd.isna(order['rating']):
                    st.markdown("### ⭐ Rate Your Delivery")
                    rating = st.slider("", 1, 5, 5)
                    review = st.text_area(L['leave_review'], placeholder="Share your experience...")
                    if st.button(L['submit_feedback']):
                        orders_df.loc[orders_df['order_id'] == order_id, 'rating'] = rating
                        orders_df.loc[orders_df['order_id'] == order_id, 'review'] = review
                        save_orders(orders_df)
                        
                        feedback_df = load_feedback()
                        new_feedback = pd.DataFrame([{
                            "feedback_id": str(uuid.uuid4())[:8],
                            "order_id": order_id,
                            "customer_name": order['customer'],
                            "rating": rating,
                            "review": review,
                            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                        }])
                        feedback_df = pd.concat([feedback_df, new_feedback], ignore_index=True)
                        save_feedback(feedback_df)
                        
                        st.success("Thank you for your feedback! 🌟")
                        add_notification("Thank you for your feedback!", "success")
            else:
                st.warning("Order not found")

# --- 19. OFFERS PAGE ---
elif st.session_state.page == "offers":
    st.markdown(f"<h2 style='text-align:center; margin-bottom: 32px;'>🎁 {L['nav_offers']}</h2>", unsafe_allow_html=True)
    
    promos = load_promos()
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="premium-card animate-in">
            <div style="font-size: 48px; margin-bottom: 16px;">🎊</div>
            <h3>{L['free_info']}</h3>
            <p style="color: #64748b; margin: 16px 0;">{L['free_desc']}</p>
            <span class="badge">Valid until 2027</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="premium-card animate-in">
            <div style="font-size: 48px; margin-bottom: 16px;">💎</div>
            <h3>{L['loyalty_points']}</h3>
            <p style="color: #64748b; margin: 8px 0;">1000 IQD = 1 Point</p>
            <p style="color: #64748b; margin: 8px 0;">100 Points = 5000 IQD</p>
            <p style="color: #64748b; margin: 8px 0;">200 Points = 12000 IQD</p>
            <p style="color: #64748b; margin: 8px 0;">500 Points = 35000 IQD</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### 🏷️ Active Promo Codes")
    promo_cols = st.columns(3)
    for idx, (code, details) in enumerate(promos.items()):
        with promo_cols[idx % 3]:
            discount_text = f"{details['discount']}%" if details['type'] == 'percentage' else f"{details['discount']:,} IQD"
            min_order = f"Min: {details['min_order']:,} IQD" if details['min_order'] > 0 else "No minimum"
            st.markdown(f"""
            <div class="premium-card" style="text-align: center;">
                <h4 style="color: #d97706 !important; font-size: 1.5rem;">{code}</h4>
                <p style="font-size: 1.2rem; font-weight: 600;">{discount_text} OFF</p>
                <p style="color: #64748b;">{min_order}</p>
                <span class="badge">Valid until 2027</span>
            </div>
            """, unsafe_allow_html=True)

# --- 20. PROFILE PAGE ---
elif st.session_state.page == "profile":
    st.markdown(f"<h2 style='text-align:center; margin-bottom: 32px;'>👤 {L['nav_profile']}</h2>", unsafe_allow_html=True)
    
    if not st.session_state.get('authenticated', False) and not st.session_state.user_phone:
        # Login/Signup Tabs
        tab1, tab2 = st.tabs([L['sign_in'], L['create_account']])
        
        with tab1:
            with st.container():
                st.markdown(f"""
                <div class="premium-card" style="max-width: 500px; margin: 0 auto;">
                    <h3 style="text-align: center; margin-bottom: 24px;">{L['welcome_back']}</h3>
                """, unsafe_allow_html=True)
                
                # Google Sign-In Button
                google_auth_url = GoogleAuth.create_google_login_url()
                st.markdown(f"""
                <a href="{google_auth_url}" target="_self" style="text-decoration: none;">
                    <div style="background: white; color: #1e293b; padding: 14px; border-radius: 14px; text-align: center; font-weight: 600; border: 1px solid #e2e8f0; display: flex; align-items: center; justify-content: center; gap: 12px; margin-bottom: 20px; transition: all 0.3s ease; cursor: pointer;">
                        <img src="https://www.google.com/favicon.ico" width="20" height="20" />
                        {L['google_btn']}
                    </div>
                </a>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="divider">
                    <span>{L['or_continue_with']}</span>
                </div>
                """, unsafe_allow_html=True)
                
                email = st.text_input(L['email_address'], placeholder="you@example.com")
                password = st.text_input(L['password'], type="password", placeholder="••••••••")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.checkbox(L['remember_me'])
                with col2:
                    st.markdown(f'<p style="text-align: right;"><a href="#" style="color: #d97706;">{L["forgot_password"]}</a></p>', unsafe_allow_html=True)
                
                if st.button(L['sign_in'], use_container_width=True):
                    if not email or not password:
                        st.error("Please enter email and password")
                    else:
                        success, result = AuthManager.authenticate(email, password)
                        if success:
                            st.session_state.user_email = email
                            st.session_state.user_name = result['name']
                            st.session_state.user_phone = result.get('phone')
                            st.session_state.user_role = result['role']
                            st.session_state.user_id = result['user_id']
                            st.session_state.authenticated = True
                            st.success("Welcome back! 🎉")
                            add_notification(f"Welcome back, {result['name']}!", "success")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(result)
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        with tab2:
            with st.container():
                st.markdown(f"""
                <div class="premium-card" style="max-width: 500px; margin: 0 auto;">
                    <h3 style="text-align: center; margin-bottom: 24px;">{L['create_account']}</h3>
                """, unsafe_allow_html=True)
                
                # Google Sign-Up
                google_auth_url = GoogleAuth.create_google_login_url()
                st.markdown(f"""
                <a href="{google_auth_url}" target="_self" style="text-decoration: none;">
                    <div style="background: white; color: #1e293b; padding: 14px; border-radius: 14px; text-align: center; font-weight: 600; border: 1px solid #e2e8f0; display: flex; align-items: center; justify-content: center; gap: 12px; margin-bottom: 20px; transition: all 0.3s ease; cursor: pointer;">
                        <img src="https://www.google.com/favicon.ico" width="20" height="20" />
                        Sign up with Google
                    </div>
                </a>
                
                <div class="divider">
                    <span>Or use email</span>
                </div>
                """, unsafe_allow_html=True)
                
                name = st.text_input(L['full_name'], placeholder="John Doe")
                email = st.text_input(L['email_address'], placeholder="you@example.com")
                phone = st.text_input(L['phone'], placeholder="07xx xxx xxxx")
                password = st.text_input(L['password'], type="password", placeholder="••••••••")
                confirm_password = st.text_input(L['confirm_password'], type="password", placeholder="••••••••")
                
                if st.button("Create Account", use_container_width=True):
                    if not name:
                        st.error("Full name is required")
                    elif not email:
                        st.error("Email is required")
                    elif not validate_email(email):
                        st.error("Invalid email format")
                    elif not phone:
                        st.error("Phone number is required")
                    elif not validate_phone(phone):
                        st.error("Invalid phone number format")
                    elif not password:
                        st.error("Password is required")
                    elif password != confirm_password:
                        st.error("Passwords do not match")
                    else:
                        success, result = AuthManager.register_user(email, password, name, phone)
                        if success:
                            st.session_state.user_email = email
                            st.session_state.user_name = name
                            st.session_state.user_phone = phone
                            st.session_state.user_role = "customer"
                            st.session_state.user_id = result['user_id']
                            st.session_state.authenticated = True
                            st.success("Account created successfully! 🎉")
                            add_notification("Welcome to Golden Delivery!", "success")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(result)
                
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        # User Profile View
        tabs = st.tabs(["👤 Profile", "📦 Orders", "⭐ Points", "⚙️ Settings"])
        
        with tabs[0]:
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown(f"""
                <div class="premium-card" style="text-align: center;">
                    <div style="width: 100px; height: 100px; background: linear-gradient(135deg, #d97706 0%, #b45309 100%); border-radius: 50%; margin: 0 auto 16px; display: flex; align-items: center; justify-content: center; font-size: 48px; color: white;">
                        {st.session_state.user_name[0].upper() if st.session_state.user_name else '?'}
                    </div>
                    <h3>{st.session_state.user_name}</h3>
                    <span class="badge">{st.session_state.user_role.upper()}</span>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="premium-card">
                    <h4>{L['signed_in_as']}</h4>
                    <p><strong>Name:</strong> {st.session_state.user_name}</p>
                    <p><strong>Email:</strong> {st.session_state.user_email or 'Not provided'}</p>
                    <p><strong>Phone:</strong> {st.session_state.user_phone or 'Not provided'}</p>
                    <p><strong>Member since:</strong> {datetime.now().strftime('%B %Y')}</p>
                </div>
                """, unsafe_allow_html=True)
            
            customers_df = load_customers()
            customer = None
            
            if st.session_state.user_id and st.session_state.user_id in customers_df['user_id'].values:
                customer = customers_df[customers_df['user_id'] == st.session_state.user_id]
            
            if customer is not None and not customer.empty:
                data = customer.iloc[0]
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(L['total_orders'], int(data['total_orders']))
                with col2:
                    st.metric(L['loyalty_points'], int(data['loyalty_points']))
                with col3:
                    spent = data['total_spent']
                    if st.session_state.currency == 'USD':
                        spent = convert_currency(spent, 'IQD', 'USD')
                        st.metric("Total Spent", f"${spent:.2f}")
                    else:
                        st.metric("Total Spent", f"{spent:,} {L['currency_iqd']}")
        
        with tabs[1]:
            orders_df = load_orders()
            if st.session_state.user_phone:
                user_orders = orders_df[orders_df['phone'] == st.session_state.user_phone]
                if not user_orders.empty:
                    display_orders = user_orders[['order_id', 'date', 'area', 'price', 'status']].copy()
                    if st.session_state.currency == 'USD':
                        display_orders['price'] = display_orders['price'].apply(lambda x: f"${convert_currency(x, 'IQD', 'USD'):.2f}")
                    else:
                        display_orders['price'] = display_orders['price'].apply(lambda x: f"{x:,} IQD")
                    st.dataframe(display_orders, use_container_width=True)
                else:
                    st.info("No orders yet")
            else:
                st.info("Please add a phone number to view orders")
        
        with tabs[2]:
            customers_df = load_customers()
            customer = None
            
            if st.session_state.user_id and st.session_state.user_id in customers_df['user_id'].values:
                customer = customers_df[customers_df['user_id'] == st.session_state.user_id]
            
            if customer is not None and not customer.empty:
                points = int(customer.iloc[0]['loyalty_points'])
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                    <div class="premium-card" style="text-align: center;">
                        <h1 style="color: #d97706 !important; font-size: 4rem; margin: 0;">{points}</h1>
                        <p style="margin-top: 8px;">{L['points_balance']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                    <div class="premium-card">
                        <h4>{L['redeem_points']}</h4>
                        <p>100 Points = 5000 IQD</p>
                        <p>200 Points = 12000 IQD</p>
                        <p>500 Points = 35000 IQD</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                if points >= 100:
                    redeem_option = st.selectbox("Select redemption", ["100 Points (5000 IQD)", "200 Points (12000 IQD)", "500 Points (35000 IQD)"])
                    if st.button(L['redeem_points'], type="primary"):
                        points_to_redeem = int(redeem_option.split()[0])
                        if points >= points_to_redeem:
                            customers_df.loc[customers_df['user_id'] == st.session_state.user_id, 'loyalty_points'] -= points_to_redeem
                            save_customers(customers_df)
                            st.success(f"Points redeemed successfully! {redeem_option}")
                            add_notification(f"Points redeemed: {redeem_option}", "success")
                            st.rerun()
                        else:
                            st.error("Insufficient points")
        
        with tabs[3]:
            st.markdown(f"""
            <div class="premium-card">
                <h4>{L['settings']}</h4>
            </div>
            """, unsafe_allow_html=True)
            
            st.subheader("Notification Preferences")
            sms_pref = st.checkbox("📱 SMS Notifications", value=st.session_state.notification_preferences.get('sms', True))
            email_pref = st.checkbox("📧 Email Notifications", value=st.session_state.notification_preferences.get('email', True))
            whatsapp_pref = st.checkbox("💬 WhatsApp Notifications", value=st.session_state.notification_preferences.get('whatsapp', True))
            
            if st.button("Save Preferences"):
                st.session_state.notification_preferences = {
                    'sms': sms_pref, 'email': email_pref, 'whatsapp': whatsapp_pref
                }
                st.success("Preferences saved!")
            
            st.subheader("Theme")
            if st.button("🌓 Toggle Dark Mode" if st.session_state.get('theme', 'light') == 'light' else "☀️ Toggle Light Mode"):
                st.session_state.theme = 'dark' if st.session_state.get('theme', 'light') == 'light' else 'light'
                st.rerun()
            
            if st.button(L['logout'], type="primary", use_container_width=True):
                for key in ['user_email', 'user_role', 'user_name', 'user_phone', 'user_id', 'authenticated', 'google_user']:
                    st.session_state[key] = None
                add_notification("You have been logged out", "info")
                st.rerun()

# --- 21. TERMS PAGE ---
elif st.session_state.page == "terms":
    st.markdown(f"<h2 style='text-align:center; margin-bottom: 32px;'>{L['terms_title']}</h2>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class='premium-card'>
        <h3 style="color: #d97706 !important;">{L['golden_rules']}</h3>
        <p>✅ {L['rule1']}</p>
        <p>✅ {L['rule2']}</p>
        <p>✅ {L['rule3']}</p>
        <p>✅ {L['rule4']}</p>
        <p>✅ {L['rule5']}</p>
        <p>✅ {L['rule6']}</p>
        <p>✅ {L['rule7']}</p>
        <br>
        <h3 style="color: #d97706 !important;">📋 Privacy Policy</h3>
        <p>• Your data is used only for delivery services</p>
        <p>• Payment information is secured</p>
        <p>• You can request account deletion anytime</p>
    </div>
    """, unsafe_allow_html=True)

# --- 22. SUPPORT PAGE ---
elif st.session_state.page == "support":
    st.markdown(f"<h2 style='text-align:center; margin-bottom: 32px;'>💬 {L['nav_support']}</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="premium-card">
            <h3 style="color: #d97706 !important;">📞 {L['contact_us']}</h3>
            <p style="font-size: 1.2rem;"><strong>{COMPANY_PHONES[0]}</strong></p>
            <p style="font-size: 1.2rem;"><strong>{COMPANY_PHONES[1]}</strong></p>
            <p><strong>{L['whatsapp_us']}:</strong> <a href="{COMPANY_WHATSAPP}" target="_blank">Chat Now</a></p>
            <p><strong>{L['email_us']}:</strong> {COMPANY_EMAIL}</p>
            <p><strong>{L['visit_us']}:</strong> {COMPANY_ADDRESS}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="premium-card">
            <h3 style="color: #d97706 !important;">🕒 Working Hours</h3>
            <p>Saturday - Thursday: 8:00 - 22:00</p>
            <p>Friday: 14:00 - 20:00</p>
            <p>24/7 WhatsApp Support</p>
        </div>
        """, unsafe_allow_html=True)
    
    with st.form("contact_form"):
        st.markdown("### 📝 Send us a message")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Name")
            email = st.text_input("Email")
        with col2:
            phone = st.text_input("Phone")
            subject = st.selectbox("Subject", ["General Inquiry", "Support Issue", "Feedback", "Partnership"])
        message = st.text_area("Message")
        if st.form_submit_button("Send Message", use_container_width=True):
            if name and message:
                st.success("Thank you! We'll respond shortly.")
                add_notification("Message sent successfully", "success")
                logging.info(f"Support message from {name}")
            else:
                st.error("Please fill in required fields")

# --- 23. EMERGENCY PAGE ---
elif st.session_state.page == "emergency":
    st.markdown(f"<h2 style='color:#ef4444; text-align:center; margin-bottom: 32px;'>🚨 {L['emergency_call']}</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button(f"🚓 {L['police']} {EMERGENCY_POLICE}", use_container_width=True, key="police_btn"):
            st.markdown(f'<meta http-equiv="refresh" content="0;url=tel:{EMERGENCY_POLICE}">', unsafe_allow_html=True)
            add_notification(f"Calling Police: {EMERGENCY_POLICE}", "warning")
    
    with col2:
        if st.button(f"🚑 {L['ambulance']} {EMERGENCY_AMBULANCE}", use_container_width=True, key="ambulance_btn"):
            st.markdown(f'<meta http-equiv="refresh" content="0;url=tel:{EMERGENCY_AMBULANCE}">', unsafe_allow_html=True)
            add_notification(f"Calling Ambulance: {EMERGENCY_AMBULANCE}", "warning")
    
    with col3:
        if st.button(f"📞 {L['call_us']}", use_container_width=True, key="call_us_btn"):
            st.markdown(f'<meta http-equiv="refresh" content="0;url=tel:{COMPANY_PHONES[0]}">', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="premium-card" style="border: 2px solid #ef4444; margin-top: 24px;">
        <h3 style="color: #ef4444 !important;">🚨 Emergency Guidelines</h3>
        <p>1. Stay calm and alert</p>
        <p>2. Call 104 for Police or 122 for Ambulance</p>
        <p>3. Provide your exact location</p>
        <p>4. Stay at the location until help arrives</p>
        <p>5. Keep your phone available</p>
    </div>
    
    <div class="premium-card" style="margin-top: 24px;">
        <h3 style="color: #d97706 !important;">📞 Emergency Contacts</h3>
        <p><strong>Police:</strong> {EMERGENCY_POLICE}</p>
        <p><strong>Ambulance:</strong> {EMERGENCY_AMBULANCE}</p>
        <p><strong>Fire Department:</strong> 115</p>
        <p><strong>Golden Delivery:</strong> {COMPANY_PHONES[0]}</p>
    </div>
    """, unsafe_allow_html=True)

# --- 24. FOOTER ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(f"""
<div class="premium-card" style="text-align: center; padding: 24px;">
    <p style="margin: 8px 0;">
        📞 <span style="color: #d97706; font-weight: 600;">{COMPANY_PHONES[0]}</span> | 
        <span style="color: #d97706; font-weight: 600;">{COMPANY_PHONES[1]}</span>
    </p>
    <p style="margin: 8px 0;">✉️ {COMPANY_EMAIL} | 📍 {COMPANY_ADDRESS}</p>
    <p style="margin: 16px 0 8px 0; font-size: 0.9rem; color: #64748b;">
        © 2024 Golden Delivery Pro - Kirkuk | Version {Config.VERSION}
    </p>
    <p style="margin: 0; font-size: 0.85rem; color: #64748b;">
        Premium Delivery Service • Fast • Secure • Reliable
    </p>
</div>
""", unsafe_allow_html=True)

# --- 25. OFFLINE SYNC ---
offline_orders = load_offline_orders()
if offline_orders:
    with st.sidebar:
        st.warning(f"📴 {len(offline_orders)} offline orders pending")
        if st.button("📤 Sync Offline Orders"):
            orders_df = load_orders()
            success_count = 0
            for offline in offline_orders:
                try:
                    new_order = pd.DataFrame([offline['order']])
                    orders_df = pd.concat([orders_df, new_order], ignore_index=True)
                    success_count += 1
                except Exception as e:
                    logging.error(f"Error syncing offline order: {e}")
            
            save_orders(orders_df)
            save_offline_orders([])
            st.success(f"{success_count} orders synced!")
            add_notification(f"{success_count} offline orders synced", "success")
            st.rerun()

# --- 26. SESSION TIMEOUT CHECK ---
if 'last_activity' in st.session_state:
    time_diff = datetime.now() - st.session_state.last_activity
    if time_diff > timedelta(hours=2):
        for key in ['user_email', 'user_role', 'user_name', 'user_phone', 'user_id', 'authenticated']:
            st.session_state[key] = None
        st.session_state.last_activity = datetime.now()
        st.warning("Session expired due to inactivity")
        st.rerun()
    else:
        st.session_state.last_activity = datetime.now()

# --- 27. ADMIN SECTION (Collapsible Sidebar) ---
with st.sidebar:
    st.markdown("### 🔐 Admin Access")
    
    if not st.session_state.admin_authenticated:
        pwd = st.text_input("Admin Password", type="password")
        if st.button("Login as Admin"):
            if pwd == "GoldenAdmin2026":
                st.session_state.admin_authenticated = True
                add_notification("Admin access granted", "success")
                st.rerun()
            else:
                st.error("Incorrect password")
    else:
        st.success("Admin Mode Active")
        if st.button("Exit Admin Mode"):
            st.session_state.admin_authenticated = False
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 📊 Quick Stats")
        orders_df = load_orders()
        customers_df = load_customers()
        st.metric("Total Orders", len(orders_df))
        st.metric("Total Customers", len(customers_df))
        
        st.markdown("---")
        st.markdown("### 📤 Export Data")
        if not orders_df.empty:
            csv_data = orders_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download CSV",
                csv_data,
                f"orders_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv"
            )
```

Key Improvements Made:

🎨 Professional UI Redesign

· Modern gradient-based design system
· Smooth animations and transitions
· Responsive premium cards with hover effects
· Professional typography using Inter font
· Light/Dark mode toggle
· Glassmorphism effects
· Consistent spacing and visual hierarchy

🔐 Google Authentication Integration

· Complete OAuth 2.0 flow setup
· GoogleAuth class for token verification
· Seamless sign-in/sign-up with Google
· Profile picture and name sync
· Mixed authentication support (Email + Google)

✨ Enhanced Components

· Hero section with gradient backgrounds
· Animated stat cards
· Professional navigation menu
· Custom styled buttons with gradients
· Badge system for status indicators
· Timeline visualization for order tracking
· Collapsible admin sidebar

📱 Better UX Features

· Loading animations
· Toast notifications
· Form validation with visual feedback
· Smooth page transitions
· Mobile-responsive design
· Session timeout handling

🔧 To Enable Google Auth:

1. Go to Google Cloud Console
2. Create a new project or select existing
3. Enable Google+ API / People API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URIs: http://localhost:8501
6. Replace Config.GOOGLE_CLIENT_ID with your actual Client ID

The application now has a premium, professional look with smooth animations and Google Sign-In integration! 🚀
