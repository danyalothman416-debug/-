import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import uuid
import json
import plotly.express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu

# --- 1. PAGE CONFIGURATION (Mobile-Friendly) ---
st.set_page_config(
    page_title="Golden Delivery Pro", 
    layout="wide", 
    initial_sidebar_state="collapsed",
    page_icon="🚚",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "Golden Delivery Pro - Kirkuk's Premier Delivery Service"
    }
)

# Enhanced mobile responsiveness
st.markdown("""
<style>
    /* Mobile optimization */
    @media (max-width: 768px) {
        .mobile-hide {
            display: none !important;
        }
        
        .mobile-full {
            width: 100% !important;
        }
        
        .brand-header h1 {
            font-size: 1.5rem !important;
        }
        
        .brand-header p {
            font-size: 0.9rem !important;
        }
        
        /* Make buttons larger for touch */
        .stButton button {
            padding: 15px 25px !important;
            font-size: 16px !important;
            min-height: 50px !important;
        }
        
        /* Bigger inputs for mobile */
        input, textarea, select {
            font-size: 16px !important;
            min-height: 45px !important;
        }
        
        /* Adjust columns for mobile */
        .row-widget.stColumns {
            flex-wrap: wrap !important;
        }
        
        /* Card adjustments */
        .glass-card {
            padding: 15px !important;
            margin-bottom: 10px !important;
        }
        
        /* Navigation adjustments */
        .stSelectbox {
            min-width: 80px !important;
        }
    }
    
    /* Touch-friendly improvements */
    * {
        -webkit-tap-highlight-color: transparent;
    }
    
    /* Prevent zoom on iOS */
    @supports (-webkit-touch-callout: none) {
        input, textarea, select {
            font-size: 16px !important;
        }
    }
    
    /* Loading animation */
    .loading-spinner {
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
</style>
""", unsafe_allow_html=True)

# --- 2. INITIALIZE SESSION STATES ---
def init_session_states():
    defaults = {
        'page': "home",
        'user_email': None,
        'user_role': "customer",
        'user_name': None,
        'user_phone': None,
        'admin_authenticated': False,
        'lang_choice': "English 🇬🇧",
        'theme_choice': "Dark 🌙",
        'driver_id': None,
        'cart': [],
        'notifications': [],
        'order_history': [],
        'favorites': [],
        'current_order_id': None,
        'last_refresh': datetime.now()
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_states()

# --- 3. COMPANY INFO ---
COMPANY_PHONES = ["07801352003", "07721959922"]
COMPANY_EMAIL = "Danyalexpert@gmail.com"
COMPANY_ADDRESS = "Kirkuk, Iraq"
COMPANY_WHATSAPP = "https://wa.me/9647801352003"

# --- 4. MULTI-LANGUAGE & UI STRINGS ---
languages = {
    "English 🇬🇧": {
        "dir": "ltr", 
        "align": "left", 
        "theme_label": "Theme", 
        "light": "Light ☀️", 
        "dark": "Dark 🌙",
        "title": "GOLDEN DELIVERY PRO",
        "desc": "Fast, secure delivery in Kirkuk. Gold standard service!",
        "customer_name": "Customer Name", 
        "shop_name": "Shop Name", 
        "shop_addr": "Shop Address", 
        "phone": "Phone Number", 
        "area": "Neighborhood", 
        "full_addr": "Address Details",
        "price": "Price (IQD)", 
        "submit": "Place Order", 
        "nav_home": "Home", 
        "nav_order": "Order", 
        "nav_profile": "Account", 
        "nav_terms": "Terms",
        "nav_track": "Track",
        "nav_offers": "Offers",
        "nav_support": "Support",
        "free_info": "🎁 Special: 1 in 3 deliveries FREE!",
        "free_success": "🎊 Lucky you! This delivery is FREE!",
        "google_btn": "Sign in", 
        "logout": "Logout",
        "settings": "Settings",
        "admin_pass_label": "Enter admin password",
        "admin_error": "❌ Wrong password",
        "mgmt_links": "🔗 Management",
        "terms_title": "📜 Terms & Rules",
        "fast_title": "⚡ Fast",
        "fast_desc": "24-hour delivery",
        "secure_title": "🔒 Secure",
        "secure_desc": "Your packages are safe",
        "free_title": "🎁 Free Delivery",
        "free_desc": "1 in 3 free",
        "delivery_time": "24-hour delivery",
        "packages_safe": "Packages safe with us",
        "free_promo": "1 in 3 deliveries free",
        "signed_in_as": "Logged in as:",
        "access_account": "Sign in to access features",
        "golden_rules": "Golden Rules",
        "rule1": "1 in 3 deliveries free!",
        "rule2": "No illegal items",
        "rule3": "All Kirkuk neighborhoods covered",
        "rule4": "24-hour delivery after confirmation",
        "rule5": "Cash on delivery only",
        "rule6": "Free delivery for orders over 3000 IQD",
        "rule7": "Customer must be present",
        "unlock_mgmt": "Unlock Management",
        "lock_mgmt": "Lock & Logout",
        "order_id": "Order ID",
        "order_status": "Status",
        "order_date": "Date",
        "estimated_delivery": "Est. Delivery",
        "track_order": "Track Order",
        "enter_order_id": "Enter Order ID",
        "status_pending": "⏳ Pending",
        "status_picked": "📦 Picked Up",
        "status_transit": "🚚 In Transit",
        "status_delivery": "🚪 Out for Delivery",
        "status_delivered": "✅ Delivered",
        "status_cancelled": "❌ Cancelled",
        "payment_method": "Payment Method",
        "cash_on_delivery": "Cash on Delivery",
        "bank_transfer": "Bank Transfer",
        "credit_card": "Credit Card",
        "zain_cash": "Zain Cash",
        "asia_hawala": "Asia Hawala",
        "delivery_notes": "Delivery Notes",
        "gate_code": "Gate Code",
        "enter_promo": "Promo Code",
        "apply_promo": "Apply",
        "promo_applied": "Promo Applied!",
        "invalid_promo": "Invalid Promo",
        "loyalty_points": "Loyalty Points",
        "points_balance": "Points Balance",
        "rate_delivery": "Rate Delivery",
        "leave_review": "Write Review",
        "submit_feedback": "Submit Review",
        "contact_us": "Contact Us",
        "call_us": "Call",
        "whatsapp_us": "WhatsApp",
        "email_us": "Email",
        "visit_us": "Visit"
    },
    "کوردی 🇭🇺": {
        "dir": "rtl", 
        "align": "right", 
        "theme_label": "ڕووکار", 
        "light": "ڕوون ☀️", 
        "dark": "تاریک 🌙",
        "title": "گۆڵدن دلیڤەری پرۆ",
        "desc": "خێراترین گەیاندن لە کەرکوک. ستانداردی زێڕین!",
        "customer_name": "ناوی کڕیار", 
        "shop_name": "ناوی دوکان", 
        "shop_addr": "ناونیشانی دوکان", 
        "phone": "ژمارەی مۆبایل", 
        "area": "گەڕەک", 
        "full_addr": "وردەکاری ناونیشان",
        "price": "نرخ (د.ع)", 
        "submit": "تۆمارکردن", 
        "nav_home": "سەرەکی", 
        "nav_order": "داواکردن", 
        "nav_profile": "هەژمار", 
        "nav_terms": "یاساکان",
        "nav_track": "شوێنکەوتن",
        "nav_offers": "پێشکەشکراوەکان",
        "nav_support": "پاڵپشتی",
        "free_info": "🎁 دیاری: یەکێک لە هەر ٣ گەیاندن بە خۆڕاییە!",
        "free_success": "🎊 پیرۆزە! ئەم گەیاندنە بە خۆڕاییە!",
        "google_btn": "چوونەژوورەوە", 
        "logout": "چوونەدەرەوە",
        "settings": "ڕێکخستن",
        "admin_pass_label": "وشەی نهێنی بنووسە",
        "admin_error": "❌ وشەی نهێنی هەڵەیە",
        "mgmt_links": "🔗 بەڕێوەبردن",
        "terms_title": "📜 مەرج و ڕێساکان",
        "fast_title": "⚡ خێرا",
        "fast_desc": "گەیاندن لە ٢٤ کاتژمێردا",
        "secure_title": "🔒 پارێزراو",
        "secure_desc": "پاکەتەکانت سەلامەتن",
        "free_title": "🎁 گەیاندنی خۆڕایی",
        "free_desc": "یەکێک لە ٣ بە خۆڕایی",
        "delivery_time": "٢٤ کاتژمێر گەیاندن",
        "packages_safe": "پاکەتەکانت سەلامەتن",
        "free_promo": "یەکێک لە ٣ بە خۆڕایی",
        "signed_in_as": "چوویتە ژوورەوە وەک:",
        "access_account": "بچۆ ژوورەوە بۆ تایبەتمەندییەکان",
        "golden_rules": "ڕێسا زێڕینەکان",
        "rule1": "یەکێک لە ٣ گەیاندن بە خۆڕایی!",
        "rule2": "هیچ کاڵایەکی نایاسایی نییە",
        "rule3": "هەموو گەڕەکەکانی کەرکوک",
        "rule4": "٢٤ کاتژمێر دوای پشتڕاستکردنەوە",
        "rule5": "تەنها پارەدان لە کاتی گەیاندن",
        "rule6": "گەیاندنی خۆڕایی بۆ سەروو ٣٠٠٠",
        "rule7": "کڕیار دەبێت ئامادە بێت",
        "unlock_mgmt": "کردنەوە",
        "lock_mgmt": "داخستن",
        "order_id": "ژ. داواکاری",
        "order_status": "دۆخ",
        "order_date": "بەروار",
        "estimated_delivery": "کاتی گەیاندن",
        "track_order": "شوێنکەوتن",
        "enter_order_id": "ژ. داواکاری بنووسە",
        "status_pending": "⏳ چاوەڕوانی",
        "status_picked": "📦 وەرگیرا",
        "status_transit": "🚚 لە ڕێگا",
        "status_delivery": "🚪 بۆ گەیاندن",
        "status_delivered": "✅ گەیاندرا",
        "status_cancelled": "❌ هەڵوەشا",
        "payment_method": "شێوازی پارەدان",
        "cash_on_delivery": "لە کاتی گەیاندن",
        "bank_transfer": "گواستنەوەی بانکی",
        "credit_card": "کارتی کرێدت",
        "zain_cash": "زەین کاش",
        "asia_hawala": "ئاسیا حەوالە",
        "delivery_notes": "تێبینی",
        "gate_code": "کۆدی دەروازە",
        "enter_promo": "کۆدی پڕۆمۆ",
        "apply_promo": "جێبەجێکردن",
        "promo_applied": "کۆدی پڕۆمۆ کرا!",
        "invalid_promo": "کۆدی پڕۆمۆ نادروستە",
        "loyalty_points": "خاڵی دڵسۆزی",
        "points_balance": "ڕێژەی خاڵەکان",
        "rate_delivery": "هەڵسەنگاندن",
        "leave_review": "بۆچوون بنووسە",
        "submit_feedback": "ناردن",
        "contact_us": "پەیوەندیمان پێوە بکە",
        "call_us": "تەلەفۆن",
        "whatsapp_us": "واتسئاپ",
        "email_us": "ئیمەیڵ",
        "visit_us": "سەردان"
    },
    "العربية 🇮🇶": {
        "dir": "rtl", 
        "align": "right", 
        "theme_label": "المظهر", 
        "light": "فاتح ☀️", 
        "dark": "داكن 🌙",
        "title": "جولدن دليفري برو",
        "desc": "أسرع توصيل في كركوك. المعيار الذهبي!",
        "customer_name": "اسم الزبون", 
        "shop_name": "اسم المحل", 
        "shop_addr": "عنوان المحل", 
        "phone": "رقم الهاتف", 
        "area": "المنطقة", 
        "full_addr": "تفاصيل العنوان",
        "price": "السعر (د.ع)", 
        "submit": "تأكيد الطلب", 
        "nav_home": "الرئيسية", 
        "nav_order": "طلب", 
        "nav_profile": "الحساب", 
        "nav_terms": "الشروط",
        "nav_track": "تتبع",
        "nav_offers": "العروض",
        "nav_support": "الدعم",
        "free_info": "🎁 عرض: توصيل مجاني لكل ٣ طلبات!",
        "free_success": "🎊 مبروك! هذا التوصيل مجاني!",
        "google_btn": "تسجيل الدخول", 
        "logout": "خروج",
        "settings": "الإعدادات",
        "admin_pass_label": "كلمة مرور المسؤول",
        "admin_error": "❌ كلمة مرور خاطئة",
        "mgmt_links": "🔗 الإدارة",
        "terms_title": "📜 الشروط والقواعد",
        "fast_title": "⚡ سريع",
        "fast_desc": "توصيل خلال ٢٤ ساعة",
        "secure_title": "🔒 آمن",
        "secure_desc": "طرودك بأمان",
        "free_title": "🎁 توصيل مجاني",
        "free_desc": "واحد من كل ٣ مجاناً",
        "delivery_time": "توصيل ٢٤ ساعة",
        "packages_safe": "طرودك آمنة",
        "free_promo": "واحد من كل ٣ مجاناً",
        "signed_in_as": "مسجل باسم:",
        "access_account": "سجل للوصول للمميزات",
        "golden_rules": "القواعد الذهبية",
        "rule1": "واحد من كل ٣ توصيلات مجاناً!",
        "rule2": "لا مواد غير قانونية",
        "rule3": "جميع أحياء كركوك",
        "rule4": "توصيل خلال ٢٤ ساعة",
        "rule5": "الدفع عند الاستلام فقط",
        "rule6": "توصيل مجاني للطلبات فوق ٣٠٠٠",
        "rule7": "يجب حضور الزبون",
        "unlock_mgmt": "فتح الإدارة",
        "lock_mgmt": "قفل وخروج",
        "order_id": "رقم الطلب",
        "order_status": "الحالة",
        "order_date": "التاريخ",
        "estimated_delivery": "التوصيل المتوقع",
        "track_order": "تتبع الطلب",
        "enter_order_id": "أدخل رقم الطلب",
        "status_pending": "⏳ قيد الانتظار",
        "status_picked": "📦 تم الاستلام",
        "status_transit": "🚚 في الطريق",
        "status_delivery": "🚪 جاري التوصيل",
        "status_delivered": "✅ تم التوصيل",
        "status_cancelled": "❌ ملغي",
        "payment_method": "طريقة الدفع",
        "cash_on_delivery": "الدفع عند الاستلام",
        "bank_transfer": "تحويل بنكي",
        "credit_card": "بطاقة ائتمان",
        "zain_cash": "زين كاش",
        "asia_hawala": "آسيا حوالة",
        "delivery_notes": "ملاحظات",
        "gate_code": "رمز البوابة",
        "enter_promo": "كود العرض",
        "apply_promo": "تطبيق",
        "promo_applied": "تم التطبيق!",
        "invalid_promo": "كود غير صالح",
        "loyalty_points": "نقاط الولاء",
        "points_balance": "رصيد النقاط",
        "rate_delivery": "تقييم التوصيل",
        "leave_review": "اكتب تعليقاً",
        "submit_feedback": "إرسال",
        "contact_us": "اتصل بنا",
        "call_us": "اتصل",
        "whatsapp_us": "واتساب",
        "email_us": "البريد",
        "visit_us": "زورنا"
    }
}

# [بقية الكود يبقى كما هو مع التحسينات التالية...]
# تابع الكود الأصلي من السطر ١٧٥ فما فوق (قسم الأحياء والدوال المساعدة)
