import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import uuid
import json
import plotly.express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Golden Delivery Pro", 
    layout="wide", 
    initial_sidebar_state="collapsed",
    page_icon="🚚"
)

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
        'current_order_id': None
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_states()

# --- 3. COMPANY INFO ---
COMPANY_PHONES = ["07801352003", "07721959922"]
COMPANY_EMAIL = "Danyalexpert@gmail.com"  # Updated email
COMPANY_ADDRESS = "Kirkuk, Iraq"
COMPANY_WHATSAPP = "https://wa.me/9647801352003"

# --- 4. MULTI-LANGUAGE & UI STRINGS (COMPLETE WITH ALL TEXTS) ---
languages = {
    "English 🇬🇧": {
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
        "nav_order": "Order", 
        "nav_profile": "Account", 
        "nav_terms": "Terms",
        "nav_track": "Track",
        "nav_offers": "Offers",
        "nav_support": "Support",
        "free_info": "🎁 Special: 1 out of every 3 deliveries is FREE!",
        "free_success": "🎊 Loyalty Reward: This delivery is 0 IQD!",
        "google_btn": "Sign in with Google", 
        "logout": "Logout",
        "settings": "Settings & Language",
        "admin_pass_label": "Enter Admin Password to view links",
        "admin_error": "❌ Incorrect Password",
        "mgmt_links": "🔗 Management Links (Internal Only)",
        "terms_title": "📜 Terms and Rules",
        "terms_content": "...",
        # Home page cards
        "fast_title": "⚡ Fast",
        "fast_desc": "Delivery within 24 hours",
        "secure_title": "🔒 Secure",
        "secure_desc": "Your packages are safe with us",
        "free_title": "🎁 Free Delivery",
        "free_desc": "1 in 3 deliveries free",
        # Additional texts
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
        # Order tracking
        "order_id": "Order ID",
        "order_status": "Status",
        "order_date": "Date",
        "estimated_delivery": "Estimated Delivery",
        "track_order": "Track Your Order",
        "enter_order_id": "Enter Order ID",
        "status_pending": "⏳ Pending",
        "status_picked": "📦 Picked Up",
        "status_transit": "🚚 In Transit",
        "status_delivery": "🚪 Out for Delivery",
        "status_delivered": "✅ Delivered",
        "status_cancelled": "❌ Cancelled",
        # Payment methods
        "payment_method": "Payment Method",
        "cash_on_delivery": "Cash on Delivery",
        "bank_transfer": "Bank Transfer",
        "credit_card": "Credit Card",
        "zain_cash": "Zain Cash",
        "asia_hawala": "Asia Hawala",
        # Driver management
        "assign_driver": "Assign Driver",
        "driver_name": "Driver Name",
        "driver_phone": "Driver Phone",
        "driver_status": "Driver Status",
        "driver_available": "Available",
        "driver_busy": "Busy",
        "driver_offline": "Offline",
        # Feedback
        "rate_delivery": "Rate Your Delivery",
        "leave_review": "Leave a Review",
        "submit_feedback": "Submit Feedback",
        # Promo codes
        "enter_promo": "Enter Promo Code",
        "apply_promo": "Apply",
        "promo_applied": "Promo Code Applied!",
        "invalid_promo": "Invalid Promo Code",
        # Loyalty points
        "loyalty_points": "Loyalty Points",
        "points_balance": "Your Points Balance",
        "redeem_points": "Redeem Points",
        # Delivery notes
        "delivery_notes": "Delivery Notes",
        "gate_code": "Gate Code",
        "building_number": "Building Number",
        # Contact
        "contact_us": "Contact Us",
        "call_us": "Call Us",
        "whatsapp_us": "WhatsApp",
        "email_us": "Email Us",
        "visit_us": "Visit Us"
    },
    "کوردی 🇭🇺": {
        "dir": "rtl", 
        "align": "right", 
        "theme_label": "ڕووکار", 
        "light": "ڕوون ☀️", 
        "dark": "تاریک 🌙",
        "title": "گۆڵدن دلیڤەری پرۆ",
        "desc": "بەرزترین کوالێتی گەیاندن لە کەرکوک. خێرا، پارێزراو، و هەمیشە لە کاتی خۆیدا.",
        "customer_name": "ناوی کڕیار", 
        "shop_name": "ناوی دوکان", 
        "shop_addr": "ناونیشانی دوکان", 
        "phone": "ژمارەی مۆبایل", 
        "area": "گەڕەک", 
        "full_addr": "وردەکاری ناونیشان (نزیک کوێیە؟)",
        "price": "نرخ (د.ع)", 
        "submit": "تۆمارکردن", 
        "nav_home": "سەرەکی", 
        "nav_order": "داواکردن", 
        "nav_profile": "هەژمار", 
        "nav_terms": "یاساکان",
        "nav_track": "شوێنکەوتن",
        "nav_offers": "پێشکەشکراوەکان",
        "nav_support": "پاڵپشتی",
        "free_info": "🎁 دیاری: یەکێک لە هەر ٣ گەیاندنێک بە خۆڕاییە!",
        "free_success": "🎊 پیرۆزە! ئەم گەیاندنەت بە ٠ دینارە!",
        "google_btn": "چوونەژوورەوە بە Google", 
        "logout": "چوونەدەرەوە",
        "settings": "ڕێکخستن و زمان",
        "admin_pass_label": "تکایە وشەی نهێنی بنووسە بۆ بینینی لینکەکان",
        "admin_error": "❌ وشەی نهێنی هەڵەیە",
        "mgmt_links": "🔗 لینکەکانی بەڕێوەبردن (تەنها بۆ ئەدمین)",
        "terms_title": "📜 مەرج و ڕێساکان",
        "terms_content": "...",
        # Home page cards
        "fast_title": "⚡ خێرا",
        "fast_desc": "گەیاندن لە ماوەی ٢٤ کاتژمێردا",
        "secure_title": "🔒 پارێزراو",
        "secure_desc": "پاکەتەکانت سەلامەتن لە لای ئێمە",
        "free_title": "🎁 گەیاندنی خۆڕایی",
        "free_desc": "یەکێک لە هەر ٣ گەیاندنێک بە خۆڕاییە",
        # Additional texts
        "delivery_time": "گەیاندن لە ماوەی ٢٤ کاتژمێردا",
        "packages_safe": "پاکەتەکانت سەلامەتن لە لای ئێمە",
        "free_promo": "یەکێک لە هەر ٣ گەیاندنێک بە خۆڕاییە",
        "signed_in_as": "چوویتە ژوورەوە وەک:",
        "access_account": "چوونەژوورەوە بۆ ئەکاونتەکەت و تایبەتمەندییەکانی بەڕێوەبردن",
        "golden_rules": "ڕێسا زێڕینەکان",
        "rule1": "یەکێک لە هەر ٣ گەیاندنێک بە خۆڕاییە - بە شێوەیەکی خۆکار جێبەجێ دەبێت!",
        "rule2": "هیچ کاڵایەکی نایاسایی نییە - ئێمە پابەندی هەموو یاسا ناوخۆییەکانین",
        "rule3": "خزمەتگوزاری خێرا لە سەرانسەری کەرکوک - هەموو گەڕەکەکان داپۆشراون",
        "rule4": "گەیاندن لە ماوەی ٢٤ کاتژمێری دوای پشتڕاستکردنەوەی داواکاری",
        "rule5": "تەنها پارەدان لە کاتی گەیاندن",
        "rule6": "پڕۆمۆشنی گەیاندنی خۆڕایی بۆ داواکارییەکانی سەروو ٣٠٠٠ دینار",
        "rule7": "کڕیار دەبێت لە کاتی گەیاندن ئامادە بێت",
        "unlock_mgmt": "کردنەوەی بەڕێوەبردن",
        "lock_mgmt": "داخستنی بەڕێوەبردن و چوونەدەرەوە",
        # Order tracking
        "order_id": "ژمارەی داواکاری",
        "order_status": "دۆخ",
        "order_date": "بەروار",
        "estimated_delivery": "گەیاندنی چاوەڕوانکراو",
        "track_order": "شوێنکەوتنی داواکاری",
        "enter_order_id": "ژمارەی داواکاری بنووسە",
        "status_pending": "⏳ چاوەڕوانی",
        "status_picked": "📦 وەرگیرا",
        "status_transit": "🚚 لە ڕێگادا",
        "status_delivery": "🚪 لە ڕێگەی گەیاندن",
        "status_delivered": "✅ گەیاندرا",
        "status_cancelled": "❌ هەڵوەشایەوە",
        # Payment methods
        "payment_method": "شێوازی پارەدان",
        "cash_on_delivery": "پارەدان لە کاتی گەیاندن",
        "bank_transfer": "گواستنەوەی بانکی",
        "credit_card": "کارتی کرێدت",
        "zain_cash": "زەین کاش",
        "asia_hawala": "ئاسیا حەوالە",
        # Driver management
        "assign_driver": "دیاریکردنی شۆفێر",
        "driver_name": "ناوی شۆفێر",
        "driver_phone": "ژمارەی مۆبایلی شۆفێر",
        "driver_status": "دۆخی شۆفێر",
        "driver_available": "بەردەست",
        "driver_busy": "سەرقاڵ",
        "driver_offline": "دەرەوەی خزمەت",
        # Feedback
        "rate_delivery": "هەڵسەنگاندنی گەیاندن",
        "leave_review": "بیروبۆچوون بنووسە",
        "submit_feedback": "ناردنی بیروبۆچوون",
        # Promo codes
        "enter_promo": "کۆدی پڕۆمۆ بنووسە",
        "apply_promo": "جێبەجێکردن",
        "promo_applied": "کۆدی پڕۆمۆ جێبەجێ کرا!",
        "invalid_promo": "کۆدی پڕۆمۆ نادروستە",
        # Loyalty points
        "loyalty_points": "خاڵی دڵسۆزی",
        "points_balance": "ڕێژەی خاڵەکانت",
        "redeem_points": "بەکارهێنانی خاڵەکان",
        # Delivery notes
        "delivery_notes": "تێبینی گەیاندن",
        "gate_code": "کۆدی دەروازە",
        "building_number": "ژمارەی باڵەخانە",
        # Contact
        "contact_us": "پەیوەندیمان پێوە بکە",
        "call_us": "پەیوەندیمان پێوە بکە",
        "whatsapp_us": "واتسئاپ",
        "email_us": "ئیمەیڵ",
        "visit_us": "سەردانمان بکە"
    },
    "العربية 🇮🇶": {
        "dir": "rtl", 
        "align": "right", 
        "theme_label": "المظهر", 
        "light": "فاتح ☀️", 
        "dark": "داكن 🌙",
        "title": "جولدن دليفري برو",
        "desc": "المعيار الذهبي للخدمات اللوجستية في كركوك. سرعة، أمان، ودقة في المواعيد.",
        "customer_name": "اسم الزبون", 
        "shop_name": "اسم المحل", 
        "shop_addr": "عنوان المحل", 
        "phone": "رقم الهاتف", 
        "area": "المنطقة", 
        "full_addr": "تفاصيل العنوان (قرب ماذا؟)",
        "price": "السعر (د.ع)", 
        "submit": "تأكيد الطلب", 
        "nav_home": "الرئيسية", 
        "nav_order": "طلب", 
        "nav_profile": "الحساب", 
        "nav_terms": "الشروط",
        "nav_track": "تتبع",
        "nav_offers": "العروض",
        "nav_support": "الدعم",
        "free_info": "🎁 عرض: واحدة من كل ٣ توصيلات مجانية!",
        "free_success": "🎊 مبروك! هذه الطلبية بـ ٠ دينار!",
        "google_btn": "الدخول بواسطة Google", 
        "logout": "خروج",
        "settings": "الإعدادات واللغة",
        "admin_pass_label": "أدخل كلمة مرور المسؤول لعرض الروابط",
        "admin_error": "❌ كلمة المرور غير صحيحة",
        "mgmt_links": "🔗 روابط الإدارة (للمسؤولين فقط)",
        "terms_title": "📜 الشروط والقواعد",
        "terms_content": "...",
        # Home page cards
        "fast_title": "⚡ سريع",
        "fast_desc": "التوصيل خلال ٢٤ ساعة",
        "secure_title": "🔒 آمن",
        "secure_desc": "طرودك آمنة معنا",
        "free_title": "🎁 توصيل مجاني",
        "free_desc": "واحدة من كل ٣ توصيلات مجانية",
        # Additional texts
        "delivery_time": "التوصيل خلال ٢٤ ساعة",
        "packages_safe": "طرودك آمنة معنا",
        "free_promo": "واحدة من كل ٣ توصيلات مجانية",
        "signed_in_as": "تم تسجيل الدخول باسم:",
        "access_account": "سجل الدخول للوصول إلى حسابك وميزات الإدارة",
        "golden_rules": "القواعد الذهبية",
        "rule1": "واحدة من كل ٣ توصيلات مجانية - يتم تطبيقها تلقائياً!",
        "rule2": "لا يوجد عناصر غير قانونية - نحن نلتزم بجميع القوانين المحلية",
        "rule3": "خدمة سريعة في جميع أنحاء كركوك - جميع المناطق مغطاة",
        "rule4": "التوصيل خلال ٢٤ ساعة من تأكيد الطلب",
        "rule5": "الدفع عند الاستلام فقط",
        "rule6": "عرض التوصيل المجاني للطلبات التي تزيد عن ٣٠٠٠ دينار",
        "rule7": "يجب أن يكون الزبون حاضراً وقت التوصيل",
        "unlock_mgmt": "فتح الإدارة",
        "lock_mgmt": "قفل الإدارة وتسجيل الخروج",
        # Order tracking
        "order_id": "رقم الطلب",
        "order_status": "الحالة",
        "order_date": "التاريخ",
        "estimated_delivery": "التوصيل المتوقع",
        "track_order": "تتبع طلبك",
        "enter_order_id": "أدخل رقم الطلب",
        "status_pending": "⏳ قيد الانتظار",
        "status_picked": "📦 تم الاستلام",
        "status_transit": "🚚 في الطريق",
        "status_delivery": "🚪 جاري التوصيل",
        "status_delivered": "✅ تم التوصيل",
        "status_cancelled": "❌ ملغي",
        # Payment methods
        "payment_method": "طريقة الدفع",
        "cash_on_delivery": "الدفع عند الاستلام",
        "bank_transfer": "تحويل بنكي",
        "credit_card": "بطاقة ائتمان",
        "zain_cash": "زين كاش",
        "asia_hawala": "آسيا حوالة",
        # Driver management
        "assign_driver": "تعيين سائق",
        "driver_name": "اسم السائق",
        "driver_phone": "رقم السائق",
        "driver_status": "حالة السائق",
        "driver_available": "متاح",
        "driver_busy": "مشغول",
        "driver_offline": "غير متصل",
        # Feedback
        "rate_delivery": "قيم توصيلتك",
        "leave_review": "اترك تعليقاً",
        "submit_feedback": "إرسال التقييم",
        # Promo codes
        "enter_promo": "أدخل كود العرض",
        "apply_promo": "تطبيق",
        "promo_applied": "تم تطبيق كود العرض!",
        "invalid_promo": "كود العرض غير صالح",
        # Loyalty points
        "loyalty_points": "نقاط الولاء",
        "points_balance": "رصيد نقاطك",
        "redeem_points": "استبدال النقاط",
        # Delivery notes
        "delivery_notes": "ملاحظات التوصيل",
        "gate_code": "رمز البوابة",
        "building_number": "رقم المبنى",
        # Contact
        "contact_us": "اتصل بنا",
        "call_us": "اتصل",
        "whatsapp_us": "واتساب",
        "email_us": "البريد الإلكتروني",
        "visit_us": "زورنا"
    }
}

# --- 5. NEIGHBORHOODS (COMPLETE LIST) ---
KIRKUK_AREAS = sorted([
    # Original neighborhoods
    "Arfa / عرفة",
    "Tis'in / تسعين",
    "Shoraw / شوراو",
    "Rahim Awa / رحيماوة",
    "Quraya / قورية",
    "Al-Wasiti / الواسطي",
    "Al-Nasr / النصر",
    "Azadi / ازادي",
    "Wahid Huzairan / واحد حزيران",
    # Additional neighborhoods requested
    "Kirkuk Citadel / قلعة كركوك",
    "Musalla / مصلى",
    "Imam Qasim / امام قاسم",
    "Shorija / الشورجة",
    "Hasiraka / حصيرةكة",
    "Tapai Malla Abdulla / تبة ملا عبدulla",
    "Rahimawa / رحيم آوه",
    "Almas / الماس",
    "Arafa / عرفة",
    "Faylaq / فيلق",
    "Panja Ali / بنجة علي",
    "Darwaza / دروازة",
    "Kurdistan Neighborhood / حي كردستان",
    "Baghdad Road / طريق بغداد",
    "Wasit / واسط",
    "Domiz / دوميز",
    "June 1st / ١ حزيران",
    "Majidiya / المجيدية",
    "Al-Beiji / البيجي",
    "Mansour / المنصور",
    "Razgari / رزگاري",
    "Ghazna / غزنة",
    "Hay Aden / حي عدن",
    "Taseen / تسعين",
    "Khazra / خضراء",
    "Beiji / بيجي",
    "Qadisiyah / قادسية",
    "Panorama / بانوراما",
    "Barutkhana / باروته خانه",
    "Engineers Neighborhood / حي المهندسين",
    "Teachers Neighborhood / حي المعلمين",
    # Additional neighborhoods for completeness
    "Al-Mas / المس",
    "Al-Mithaq / الميثاق",
    "Al-Ta'mim / التأميم",
    "Al-Qadisiyah / القادسية",
    "Al-Jamea / الجامعة",
    "Al-Muhandiseen / المهندسين",
    "Al-Andalus / الأندلس",
    "Al-Jumhouriya / الجمهورية",
    "Domeez / دوميز",
    "Al-Wafa / الوفاء",
    "Al-Nour / النور",
    "Al-Muthanna / المثنى",
    "Al-Khadra / الخضراء",
    "Sarchinar / سرچنار",
    "Muhammad Ali / محمد علي",
    "Al-Mashtal / المشتل",
    "Al-Shuhada / الشهداء",
    "Al-Hurriya / الحرية",
    "Al-Sina'a / الصناعة",
    "Al-Masbin / المسبين",
    "Al-Sa'ad / السعد",
    "Bakhtiari / بختياري",
    "Bawer / باور",
    "Camp / مخيم",
    "Chay / جاي",
    "Choman / جومان",
    "Hasar / حصر",
    "Kani Askan / كاني عسكر",
    "Kani Qrzhala / كاني قرژالة",
    "Laylan / ليلان",
    "Rizgary / رزگاري",
    "Taza / طازة",
    "Yarmuk / يرموك",
    "Zab / زاب"
])

# --- 6. DATA FILES ---
ORDERS_FILE = "orders.csv"
DRIVERS_FILE = "drivers.csv"
CUSTOMERS_FILE = "customers.csv"
FEEDBACK_FILE = "feedback.csv"
PROMO_CODES_FILE = "promos.json"

# --- 7. DATA FUNCTIONS ---
def load_orders():
    if os.path.exists(ORDERS_FILE):
        return pd.read_csv(ORDERS_FILE, dtype={"phone": str, "order_id": str})
    return pd.DataFrame(columns=["order_id", "date", "customer", "shop", "phone", "area", 
                                  "address", "shop_addr", "price", "status", "user_email", 
                                  "driver_id", "payment_method", "delivery_notes", "promo_code",
                                  "estimated_delivery", "actual_delivery", "rating", "review"])

def save_orders(df):
    df.to_csv(ORDERS_FILE, index=False)

def load_drivers():
    if os.path.exists(DRIVERS_FILE):
        return pd.read_csv(DRIVERS_FILE, dtype={"phone": str})
    return pd.DataFrame(columns=["driver_id", "name", "phone", "status", "area", "join_date", "total_deliveries", "rating"])

def save_drivers(df):
    df.to_csv(DRIVERS_FILE, index=False)

def load_customers():
    if os.path.exists(CUSTOMERS_FILE):
        return pd.read_csv(CUSTOMERS_FILE, dtype={"phone": str})
    return pd.DataFrame(columns=["customer_id", "name", "phone", "email", "join_date", 
                                  "total_orders", "loyalty_points", "favorite_area", "total_spent"])

def save_customers(df):
    df.to_csv(CUSTOMERS_FILE, index=False)

def load_feedback():
    if os.path.exists(FEEDBACK_FILE):
        return pd.read_csv(FEEDBACK_FILE)
    return pd.DataFrame(columns=["feedback_id", "order_id", "customer_name", "rating", "review", "date"])

def save_feedback(df):
    df.to_csv(FEEDBACK_FILE, index=False)

def load_promos():
    if os.path.exists(PROMO_CODES_FILE):
        with open(PROMO_CODES_FILE, 'r') as f:
            return json.load(f)
    return {
        "WELCOME10": {"discount": 10, "type": "percentage", "min_order": 5000, "expiry": "2025-12-31"},
        "FREESHIP": {"discount": 3000, "type": "fixed", "min_order": 10000, "expiry": "2025-12-31"},
        "FIRST3": {"discount": 15, "type": "percentage", "min_order": 3000, "expiry": "2025-12-31"},
        "GOLDEN50": {"discount": 50, "type": "percentage", "min_order": 20000, "expiry": "2025-06-30"},
        "KIRKUK10": {"discount": 10, "type": "percentage", "min_order": 0, "expiry": "2025-12-31"}
    }

def save_promos(promos):
    with open(PROMO_CODES_FILE, 'w') as f:
        json.dump(promos, f, indent=4)

# --- 8. HELPER FUNCTIONS ---
def generate_order_id():
    return f"GD-{datetime.now().strftime('%Y%m')}-{str(uuid.uuid4())[:8].upper()}"

def calculate_loyalty_points(price):
    return int(price / 1000)  # 1 point per 1000 IQD

def validate_promo_code(code, price, promos):
    if code in promos:
        promo = promos[code]
        if datetime.strptime(promo['expiry'], '%Y-%m-%d') > datetime.now():
            if price >= promo['min_order']:
                if promo['type'] == 'percentage':
                    discount = (price * promo['discount']) / 100
                else:
                    discount = promo['discount']
                return True, discount, promo
    return False, 0, None

def send_sms_notification(phone, message):
    # This would integrate with SMS provider API
    # For now, we'll just log it
    print(f"SMS to {phone}: {message}")
    return True

def send_email_notification(email, subject, message):
    # This would integrate with email service
    print(f"Email to {email}: {subject} - {message}")
    return True

def get_order_status_emoji(status):
    emojis = {
        "Pending": "⏳",
        "Picked Up": "📦",
        "In Transit": "🚚",
        "Out for Delivery": "🚪",
        "Delivered": "✅",
        "Cancelled": "❌"
    }
    return emojis.get(status, "📦")

def calculate_estimated_delivery():
    return (datetime.now() + timedelta(hours=24)).strftime("%Y-%m-%d %H:%M")

def update_customer_loyalty(phone, price):
    customers_df = load_customers()
    if phone in customers_df['phone'].values:
        idx = customers_df[customers_df['phone'] == phone].index[0]
        customers_df.loc[idx, 'loyalty_points'] += calculate_loyalty_points(price)
        customers_df.loc[idx, 'total_orders'] += 1
        customers_df.loc[idx, 'total_spent'] += price
    else:
        new_customer = pd.DataFrame([{
            "customer_id": str(uuid.uuid4())[:8],
            "name": st.session_state.user_name or "Unknown",
            "phone": phone,
            "email": st.session_state.user_email or "",
            "join_date": datetime.now().strftime("%Y-%m-%d"),
            "total_orders": 1,
            "loyalty_points": calculate_loyalty_points(price),
            "favorite_area": "",
            "total_spent": price
        }])
        customers_df = pd.concat([customers_df, new_customer], ignore_index=True)
    save_customers(customers_df)

# --- 9. IMPROVED TOP BAR WITH SETTINGS ---
# Get current language
L = languages[st.session_state.lang_choice]

# Create a clean top bar
top_col1, top_col2, top_col3 = st.columns([2, 1, 1])
with top_col1:
    st.markdown(f"<h2 style='color:#D4AF37; margin:0;'>{L['title']}</h2>", unsafe_allow_html=True)
with top_col2:
    # Language selector - FIXED to actually change language
    lang_options = list(languages.keys())
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
with top_col3:
    # Theme toggle - FIXED to work properly
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

# Update L after potential language change
L = languages[st.session_state.lang_choice]

# --- 10. IMPROVED CSS WITH FIXED DARK MODE ---
is_dark = st.session_state.theme_choice == "Dark 🌙"

# Enhanced color scheme with better contrast
if is_dark:
    main_bg = "#0a0c10"
    card_bg = "#1e2329"
    text_color = "#ffffff"
    text_secondary = "#e0e0e0"  # Lighter gray for better visibility
    accent = "#D4AF37"
    input_bg = "#2d333d"
    border_color = "#3a404c"
    dropdown_bg = "#2d333d"
    dropdown_text = "#ffffff"
else:
    main_bg = "#f5f7fa"
    card_bg = "#ffffff"
    text_color = "#1a1a2e"
    text_secondary = "#2d3748"
    accent = "#D4AF37"
    input_bg = "#ffffff"
    border_color = "#e0e0e0"
    dropdown_bg = "#ffffff"
    dropdown_text = "#1a1a2e"

# Comprehensive CSS with fixed dark mode
st.markdown(f"""
<style>
    /* Hide sidebar */
    [data-testid="stSidebar"] {{ display: none; }}
    
    /* Main container */
    html, body, [data-testid="stAppViewContainer"], 
    .main, .block-container, .stApp {{
        background-color: {main_bg} !important;
        color: {text_color} !important;
    }}
    
    /* Base text colors */
    h1, h2, h3, h4, h5, h6, p, span, div, label, .stMarkdown {{
        color: {text_color} !important;
    }}
    
    /* Secondary text (subtitles, hints) */
    .secondary-text, .stCaption, .stMarkdown small {{
        color: {text_secondary} !important;
    }}
    
    /* Input fields - FIXED for dark mode */
    input, textarea, .stTextInput input, .stTextArea textarea {{
        background-color: {input_bg} !important;
        color: {text_color} !important;
        border: 1px solid {border_color} !important;
    }}
    
    /* Select boxes - FIXED for dark mode */
    .stSelectbox div[data-baseweb="select"] {{
        background-color: {input_bg} !important;
        border-color: {border_color} !important;
    }}
    
    .stSelectbox div[data-baseweb="select"] span {{
        color: {text_color} !important;
    }}
    
    /* Dropdown menu - FIXED for dark mode */
    div[data-baseweb="menu"] {{
        background-color: {dropdown_bg} !important;
        border: 1px solid {border_color} !important;
    }}
    
    div[data-baseweb="menu"] li {{
        background-color: {dropdown_bg} !important;
        color: {dropdown_text} !important;
    }}
    
    div[data-baseweb="menu"] li:hover {{
        background-color: {accent}30 !important;
    }}
    
    /* Form container */
    .stForm {{
        background-color: {card_bg} !important;
        border: 1px solid {accent}40 !important;
        border-radius: 20px !important;
        padding: 30px !important;
    }}
    
    /* Glass card */
    .glass-card {{
        background-color: {card_bg} !important;
        border-radius: 20px !important;
        padding: 25px !important;
        border: 1px solid {accent}30 !important;
        margin-bottom: 20px !important;
        color: {text_color} !important;
    }}
    
    /* Brand header */
    .brand-header {{
        background: linear-gradient(135deg, #D4AF37 0%, #8A6D3B 100%);
        padding: 30px;
        border-radius: 0 0 30px 30px;
        text-align: center;
        margin-bottom: 20px;
    }}
    
    .brand-header h1, .brand-header p {{
        color: white !important;
    }}
    
    /* Buttons */
    .stButton button {{
        background-color: {accent} !important;
        color: {text_color if is_dark else '#000000'} !important;
        border: none !important;
        font-weight: bold !important;
        border-radius: 10px !important;
        padding: 10px 20px !important;
        transition: all 0.3s !important;
    }}
    
    .stButton button:hover {{
        background-color: {accent}dd !important;
        transform: translateY(-2px) !important;
    }}
    
    /* Info boxes */
    .stAlert {{
        background-color: {card_bg} !important;
        color: {text_color} !important;
        border-left-color: {accent} !important;
    }}
    
    /* Success message */
    .stSuccess {{
        background-color: {card_bg} !important;
        color: #00C851 !important;
    }}
    
    /* Expander */
    .streamlit-expanderHeader {{
        background-color: {card_bg} !important;
        color: {text_color} !important;
    }}
    
    /* DataFrames */
    .dataframe, .stDataFrame, .stDataFrame div {{
        color: {text_color} !important;
    }}
    
    .dataframe td, .dataframe th {{
        background-color: {card_bg} !important;
        color: {text_color} !important;
        border-color: {border_color} !important;
    }}
    
    /* Metrics */
    [data-testid="stMetricValue"] {{
        color: {accent} !important;
        font-size: 2rem !important;
    }}
    
    /* Card title */
    .card-title {{
        color: {accent} !important;
        font-size: 1.5rem !important;
    }}
    
    /* Contact info in footer */
    .footer-contact {{
        background-color: {card_bg} !important;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin-top: 30px;
    }}
    
    .phone-number {{
        color: {accent} !important;
        font-weight: bold;
        margin: 0 10px;
    }}
    
    /* Direction handling */
    [dir="{L['dir']}"] {{
        text-align: {L['align']} !important;
    }}
</style>
""", unsafe_allow_html=True)

# --- 11. CLEAN, PROFESSIONAL NAVIGATION MENU ---
# Create a styled navigation menu
selected = option_menu(
    menu_title=None,
    options=[
        L['nav_home'], 
        L['nav_order'], 
        L['nav_track'], 
        L['nav_offers'], 
        L['nav_profile'], 
        L['nav_terms'], 
        L['nav_support']
    ],
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
            "justify-content": "center",
            "gap": "5px"
        },
        "icon": {"color": accent, "font-size": "16px"},
        "nav-link": {
            "font-size": "15px", 
            "text-align": "center", 
            "margin": "0px 2px",
            "padding": "10px 15px",
            "border-radius": "30px",
            "color": text_color,
            "background-color": card_bg,
            "transition": "all 0.3s"
        },
        "nav-link:hover": {
            "background-color": f"{accent}20",
            "transform": "translateY(-2px)"
        },
        "nav-link-selected": {
            "background-color": accent,
            "color": "black",
            "font-weight": "bold"
        },
    }
)

# Map selection to page
page_mapping = {
    L['nav_home']: "home",
    L['nav_order']: "order",
    L['nav_track']: "track",
    L['nav_offers']: "offers",
    L['nav_profile']: "profile",
    L['nav_terms']: "terms",
    L['nav_support']: "support"
}
st.session_state.page = page_mapping.get(selected, "home")

# --- 12. PAGE ROUTING ---

# HOME PAGE
if st.session_state.page == "home":
    st.markdown(f'<div class="brand-header"><h1 style="color:white; margin:0;">{L["title"]}</h1><p style="color:white; opacity:0.9;">{L["desc"]}</p></div>', unsafe_allow_html=True)
    
    # Statistics cards
    orders_df = load_orders()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total_orders = len(orders_df)
        st.metric("📦 Total Orders", total_orders)
    with col2:
        delivered = len(orders_df[orders_df['status'] == 'Delivered'])
        st.metric("✅ Delivered", delivered)
    with col3:
        free_deliveries = len(orders_df[orders_df['price'] == 0])
        st.metric("🎁 Free Deliveries", free_deliveries)
    with col4:
        if len(orders_df) > 0:
            avg_price = int(orders_df['price'].mean())
        else:
            avg_price = 0
        st.metric("💰 Avg. Order", f"{avg_price:,} IQD")
    
    # Feature cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="glass-card" style="text-align:center;">
            <h3 class="card-title">{L['fast_title']}</h3>
            <p>{L['fast_desc']}</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="glass-card" style="text-align:center;">
            <h3 class="card-title">{L['secure_title']}</h3>
            <p>{L['secure_desc']}</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="glass-card" style="text-align:center;">
            <h3 class="card-title">{L['free_title']}</h3>
            <p>{L['free_desc']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Recent orders preview
    if not orders_df.empty:
        st.markdown(f"<h3 style='color:{accent};'>📋 Recent Orders</h3>", unsafe_allow_html=True)
        recent_orders = orders_df.tail(5)[['order_id', 'customer', 'area', 'price', 'status']]
        st.dataframe(recent_orders, use_container_width=True)

# ORDER PAGE
elif st.session_state.page == "order":
    st.markdown(f"<h2 style='text-align:center; color:{accent};'>{L['nav_order']}</h2>", unsafe_allow_html=True)
    
    # Free delivery info
    st.info(L["free_info"])
    
    # Load data
    orders_df = load_orders()
    promos = load_promos()
    
    # Customer info
    col1, col2 = st.columns(2)
    with col1:
        customer_name = st.text_input(L['customer_name'])
        phone_input = st.text_input(L['phone'], placeholder="07xx xxx xxxx", value=st.session_state.user_phone if st.session_state.user_phone else "")
        shop_name = st.text_input(L['shop_name'])
    
    with col2:
        payment_method = st.selectbox(L['payment_method'], 
                                      [L['cash_on_delivery'], L['bank_transfer'], 
                                       L['credit_card'], L['zain_cash'], L['asia_hawala']])
        delivery_notes = st.text_area(L['delivery_notes'], placeholder=L['gate_code'])
    
    # Check free delivery eligibility
    is_free = False
    if phone_input:
        customer_orders = orders_df[orders_df['phone'] == phone_input]
        order_count = len(customer_orders)
        is_free = (order_count + 1) % 3 == 0
        if is_free:
            st.success(L["free_success"])
        
        # Show customer stats
        if order_count > 0:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Previous Orders", order_count)
            with col2:
                next_free = 3 - ((order_count + 1) % 3)
                st.metric("Until Free", next_free)
            with col3:
                customers_df = load_customers()
                customer_data = customers_df[customers_df['phone'] == phone_input]
                if not customer_data.empty:
                    st.metric(L['loyalty_points'], int(customer_data.iloc[0]['loyalty_points']))
    
    # Address details
    col1, col2 = st.columns(2)
    with col1:
        area = st.selectbox(L['area'], ["-- " + L['area'] + " --"] + KIRKUK_AREAS)
        full_addr = st.text_area(L['full_addr'])
    with col2:
        shop_addr = st.text_input(L['shop_addr'])
        
        # Price with promo
        base_price = 0 if is_free else 3000
        price = st.number_input(L['price'], value=base_price, min_value=0, step=1000)
        
        # Promo code
        promo_code = st.text_input(L['enter_promo'])
        if promo_code:
            valid, discount, promo = validate_promo_code(promo_code, price, promos)
            if valid:
                price = price - discount
                st.success(f"{L['promo_applied']} Discount: {discount:,} IQD")
            else:
                st.warning(L['invalid_promo'])
    
    # Submit order
    if st.button(L['submit'], use_container_width=True):
        if customer_name and phone_input and area and "--" not in area:
            # Generate order ID
            order_id = generate_order_id()
            estimated_time = calculate_estimated_delivery()
            
            # Create order
            new_order = pd.DataFrame([{
                "order_id": order_id,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "customer": customer_name,
                "shop": shop_name,
                "phone": phone_input,
                "area": area,
                "address": full_addr,
                "shop_addr": shop_addr,
                "price": price,
                "status": "Pending",
                "user_email": st.session_state.user_email,
                "driver_id": None,
                "payment_method": payment_method,
                "delivery_notes": delivery_notes,
                "promo_code": promo_code if promo_code else None,
                "estimated_delivery": estimated_time,
                "actual_delivery": None,
                "rating": None,
                "review": None
            }])
            
            # Save order
            orders_df = pd.concat([orders_df, new_order], ignore_index=True)
            save_orders(orders_df)
            
            # Update customer loyalty
            update_customer_loyalty(phone_input, price)
            
            # Send notifications
            send_sms_notification(phone_input, f"Golden Delivery: Order {order_id} confirmed! Estimated delivery: {estimated_time}")
            if st.session_state.user_email:
                send_email_notification(st.session_state.user_email, f"Order Confirmation {order_id}", 
                                      f"Your order has been confirmed. Estimated delivery: {estimated_time}")
            
            # Success message
            st.success(f"✅ {L['submit']} Successful! Order ID: {order_id}")
            st.balloons()
            
            # Store order ID in session
            st.session_state.current_order_id = order_id
        else:
            st.error("Please fill all required fields")

# TRACK PAGE
elif st.session_state.page == "track":
    st.markdown(f"<h2 style='text-align:center; color:{accent};'>{L['track_order']}</h2>", unsafe_allow_html=True)
    
    orders_df = load_orders()
    
    # Track by Order ID
    track_method = st.radio("Track by:", ["Order ID", "Phone Number"], horizontal=True)
    
    if track_method == "Order ID":
        order_id = st.text_input(L['enter_order_id'])
        if order_id:
            order = orders_df[orders_df['order_id'] == order_id]
            if not order.empty:
                order = order.iloc[0]
                
                # Display order details
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                    <div class="glass-card">
                        <h4>Order Details</h4>
                        <p><b>{L['order_id']}:</b> {order['order_id']}</p>
                        <p><b>{L['customer_name']}:</b> {order['customer']}</p>
                        <p><b>{L['area']}:</b> {order['area']}</p>
                        <p><b>{L['price']}:</b> {int(order['price']):,} IQD</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    # Status with progress
                    status = order['status']
                    status_emoji = get_order_status_emoji(status)
                    
                    st.markdown(f"""
                    <div class="glass-card">
                        <h4>{L['order_status']}</h4>
                        <p style="font-size: 2rem; text-align: center;">{status_emoji}</p>
                        <p style="text-align: center; font-size: 1.2rem;"><b>{status}</b></p>
                        <p><b>{L['order_date']}:</b> {order['date']}</p>
                        <p><b>{L['estimated_delivery']}:</b> {order['estimated_delivery']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Timeline
                st.markdown(f"<h4 style='color:{accent};'>Delivery Timeline</h4>", unsafe_allow_html=True)
                timeline_data = {
                    "Order Placed": order['date'],
                    "Picked Up": order['date'] if order['status'] != "Pending" else "Pending",
                    "In Transit": order['date'] if order['status'] in ["In Transit", "Out for Delivery", "Delivered"] else "Pending",
                    "Out for Delivery": order['date'] if order['status'] in ["Out for Delivery", "Delivered"] else "Pending",
                    "Delivered": order['actual_delivery'] if order['status'] == "Delivered" else "Pending"
                }
                
                for event, time in timeline_data.items():
                    if time != "Pending":
                        st.success(f"✅ {event}: {time}")
                    else:
                        st.info(f"⏳ {event}: Pending")
                
                # Rating section (if delivered)
                if status == "Delivered" and pd.isna(order['rating']):
                    st.markdown(f"<h4 style='color:{accent};'>{L['rate_delivery']}</h4>", unsafe_allow_html=True)
                    rating = st.slider("Rating", 1, 5, 5)
                    review = st.text_area(L['leave_review'])
                    if st.button(L['submit_feedback']):
                        # Update order with rating
                        orders_df.loc[orders_df['order_id'] == order_id, 'rating'] = rating
                        orders_df.loc[orders_df['order_id'] == order_id, 'review'] = review
                        save_orders(orders_df)
                        
                        # Save feedback
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
                        
                        st.success("Thank you for your feedback!")
            else:
                st.warning("Order not found")
    
    else:  # Track by Phone
        phone = st.text_input(L['phone'], placeholder="07xx xxx xxxx")
        if phone:
            customer_orders = orders_df[orders_df['phone'] == phone]
            if not customer_orders.empty:
                st.markdown(f"<h4 style='color:{accent};'>Your Orders</h4>", unsafe_allow_html=True)
                for idx, order in customer_orders.iterrows():
                    with st.expander(f"Order {order['order_id']} - {order['date']} - {order['status']}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**{L['order_id']}:** {order['order_id']}")
                            st.write(f"**{L['customer_name']}:** {order['customer']}")
                            st.write(f"**{L['area']}:** {order['area']}")
                        with col2:
                            st.write(f"**{L['order_status']}:** {get_order_status_emoji(order['status'])} {order['status']}")
                            st.write(f"**{L['price']}:** {int(order['price']):,} IQD")
                            st.write(f"**{L['estimated_delivery']}:** {order['estimated_delivery']}")
            else:
                st.info("No orders found for this phone number")

# OFFERS PAGE
elif st.session_state.page == "offers":
    st.markdown(f"<h2 style='text-align:center; color:{accent};'>{L['nav_offers']}</h2>", unsafe_allow_html=True)
    
    promos = load_promos()
    
    # Active promotions
    st.markdown(f"<h3 style='color:{accent};'>🎁 Active Promotions</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="glass-card">
            <h4 style="color:{accent};">🎊 Free Delivery Every 3rd Order</h4>
            <p>{L['free_promo']}</p>
            <p><b>Valid:</b> Always</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="glass-card">
            <h4 style="color:{accent};">💎 Loyalty Points</h4>
            <p>Earn 1 point for every 1000 IQD spent</p>
            <p>Redeem 100 points for 5000 IQD discount</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Promo codes
    st.markdown(f"<h3 style='color:{accent};'>🏷️ Promo Codes</h3>", unsafe_allow_html=True)
    
    promo_cols = st.columns(3)
    for idx, (code, details) in enumerate(promos.items()):
        col_idx = idx % 3
        with promo_cols[col_idx]:
            discount_text = f"{details['discount']}%" if details['type'] == 'percentage' else f"{details['discount']:,} IQD"
            min_order_text = f"Min. order: {details['min_order']:,} IQD" if details['min_order'] > 0 else "No minimum"
            st.markdown(f"""
            <div class="glass-card" style="text-align:center;">
                <h4 style="color:{accent};">{code}</h4>
                <p style="font-size:1.2rem;">{discount_text} OFF</p>
                <p>{min_order_text}</p>
                <p>Valid until: {details['expiry']}</p>
            </div>
            """, unsafe_allow_html=True)

# PROFILE PAGE
elif st.session_state.page == "profile":
    st.markdown(f"<h2 style='text-align:center; color:{accent};'>{L['nav_profile']}</h2>", unsafe_allow_html=True)
    
    if st.session_state.user_email is None:
        # Login/Register
        tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])
        
        with tab1:
            st.markdown(f"""
            <div class="glass-card" style="text-align:center;">
                <p>{L['access_account']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("👤 Customer Login", use_container_width=True):
                    st.session_state.user_email = "customer@gmail.com"
                    st.session_state.user_role = "customer"
                    st.rerun()
            with col2:
                if st.button("🚚 Driver Login", use_container_width=True):
                    st.session_state.user_email = "driver@gmail.com"
                    st.session_state.user_role = "driver"
                    st.rerun()
        
        with tab2:
            with st.form("register_form"):
                st.text_input("Full Name")
                st.text_input("Email")
                st.text_input("Phone", placeholder="07xx xxx xxxx")
                st.selectbox("Area", KIRKUK_AREAS[:10])
                if st.form_submit_button("Register"):
                    st.success("Registration successful! Please login.")
    else:
        # User profile
        tab1, tab2, tab3, tab4 = st.tabs(["👤 Profile", "📦 My Orders", "⭐ Loyalty", "⚙️ Settings"])
        
        with tab1:
            st.markdown(f"""
            <div class="glass-card">
                <h4 style="color:{accent};">{L['signed_in_as']}</h4>
                <p><b>Email:</b> {st.session_state.user_email}</p>
                <p><b>Role:</b> {st.session_state.user_role}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Load customer data
            if st.session_state.user_phone:
                customers_df = load_customers()
                customer_data = customers_df[customers_df['phone'] == st.session_state.user_phone]
                if not customer_data.empty:
                    data = customer_data.iloc[0]
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Orders", int(data['total_orders']))
                    with col2:
                        st.metric("Loyalty Points", int(data['loyalty_points']))
                    with col3:
                        st.metric("Total Spent", f"{int(data['total_spent']):,} IQD")
        
        with tab2:
            orders_df = load_orders()
            if st.session_state.user_phone:
                user_orders = orders_df[orders_df['phone'] == st.session_state.user_phone]
                if not user_orders.empty:
                    st.dataframe(user_orders[['order_id', 'date', 'area', 'price', 'status']], use_container_width=True)
                else:
                    st.info("No orders yet")
        
        with tab3:
            st.markdown(f"<h3 style='color:{accent};'>{L['loyalty_points']}</h3>", unsafe_allow_html=True)
            
            customers_df = load_customers()
            if st.session_state.user_phone:
                customer_data = customers_df[customers_df['phone'] == st.session_state.user_phone]
                if not customer_data.empty:
                    points = int(customer_data.iloc[0]['loyalty_points'])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"""
                        <div class="glass-card" style="text-align:center;">
                            <h1 style="color:{accent}; font-size:3rem;">{points}</h1>
                            <p>{L['points_balance']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div class="glass-card">
                            <h4 style="color:{accent};">Redeem Points</h4>
                            <p>100 points = 5000 IQD discount</p>
                            <p>200 points = 12000 IQD discount</p>
                            <p>500 points = 35000 IQD discount</p>
                        </div>
                        """, unsafe_allow_html=True)
        
        with tab4:
            st.markdown(f"""
            <div class="glass-card">
                <h4 style="color:{accent};">Settings</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # Notification preferences
            st.checkbox("📱 SMS Notifications", value=True)
            st.checkbox("📧 Email Notifications", value=True)
            st.checkbox("💬 WhatsApp Updates", value=True)
            
            if st.button(L["logout"]):
                st.session_state.user_email = None
                st.session_state.user_role = "customer"
                st.session_state.user_name = None
                st.session_state.user_phone = None
                st.rerun()
        
        # Admin section (password protected)
        if not st.session_state.admin_authenticated:
            st.divider()
            st.warning(L["admin_pass_label"])
            pwd = st.text_input("Password", type="password")
            if st.button(L["unlock_mgmt"]):
                if pwd == "GoldenAdmin2026":
                    st.session_state.admin_authenticated = True
                    st.rerun()
                else:
                    st.error(L["admin_error"])
        else:
            st.divider()
            st.subheader(L["mgmt_links"])
            
            # Admin tabs
            admin_tab1, admin_tab2, admin_tab3, admin_tab4 = st.tabs(["📊 Dashboard", "🚚 Drivers", "📦 Orders", "📈 Analytics"])
            
            with admin_tab1:
                orders_df = load_orders()
                customers_df = load_customers()
                drivers_df = load_drivers()
                
                # Key metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Orders", len(orders_df))
                with col2:
                    st.metric("Total Customers", len(customers_df))
                with col3:
                    st.metric("Active Drivers", len(drivers_df[drivers_df['status'] == 'Available']))
                with col4:
                    st.metric("Revenue", f"{orders_df['price'].sum():,} IQD")
                
                # Recent orders
                st.subheader("Recent Orders")
                st.dataframe(orders_df.tail(10), use_container_width=True)
            
            with admin_tab2:
                drivers_df = load_drivers()
                
                # Add new driver
                with st.expander("➕ Add New Driver"):
                    with st.form("add_driver"):
                        col1, col2 = st.columns(2)
                        with col1:
                            driver_name = st.text_input("Driver Name")
                            driver_phone = st.text_input("Driver Phone")
                        with col2:
                            driver_area = st.selectbox("Assigned Area", KIRKUK_AREAS)
                            driver_status = st.selectbox("Status", ["Available", "Busy", "Offline"])
                        
                        if st.form_submit_button("Add Driver"):
                            new_driver = pd.DataFrame([{
                                "driver_id": str(uuid.uuid4())[:8],
                                "name": driver_name,
                                "phone": driver_phone,
                                "status": driver_status,
                                "area": driver_area,
                                "join_date": datetime.now().strftime("%Y-%m-%d"),
                                "total_deliveries": 0,
                                "rating": 5.0
                            }])
                            drivers_df = pd.concat([drivers_df, new_driver], ignore_index=True)
                            save_drivers(drivers_df)
                            st.success("Driver added!")
                            st.rerun()
                
                # Drivers list
                st.subheader("Drivers List")
                st.dataframe(drivers_df, use_container_width=True)
            
            with admin_tab3:
                orders_df = load_orders()
                drivers_df = load_drivers()
                
                # Filter orders
                status_filter = st.selectbox("Filter by Status", ["All", "Pending", "Picked Up", "In Transit", "Out for Delivery", "Delivered", "Cancelled"])
                
                if status_filter != "All":
                    filtered_orders = orders_df[orders_df['status'] == status_filter]
                else:
                    filtered_orders = orders_df
                
                # Assign drivers
                for idx, order in filtered_orders.iterrows():
                    if pd.isna(order['driver_id']) and order['status'] != 'Delivered':
                        with st.expander(f"Order {order['order_id']} - {order['customer']}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Area:** {order['area']}")
                                st.write(f"**Price:** {int(order['price']):,} IQD")
                            with col2:
                                available_drivers = drivers_df[drivers_df['status'] == 'Available']
                                if not available_drivers.empty:
                                    driver_choice = st.selectbox(f"Assign Driver", 
                                                                 available_drivers['name'].tolist(),
                                                                 key=f"driver_{order['order_id']}")
                                    if st.button(f"Assign", key=f"assign_{order['order_id']}"):
                                        driver_id = available_drivers[available_drivers['name'] == driver_choice].iloc[0]['driver_id']
                                        orders_df.loc[orders_df['order_id'] == order['order_id'], 'driver_id'] = driver_id
                                        orders_df.loc[orders_df['order_id'] == order['order_id'], 'status'] = 'Picked Up'
                                        save_orders(orders_df)
                                        
                                        # Update driver status
                                        drivers_df.loc[drivers_df['driver_id'] == driver_id, 'status'] = 'Busy'
                                        save_drivers(drivers_df)
                                        
                                        st.success(f"Driver {driver_choice} assigned!")
                                        st.rerun()
                                else:
                                    st.warning("No available drivers")
                
                st.subheader("All Orders")
                st.dataframe(filtered_orders, use_container_width=True)
            
            with admin_tab4:
                orders_df = load_orders()
                
                # Delivery statistics by area
                area_stats = orders_df.groupby('area').agg({
                    'order_id': 'count',
                    'price': 'sum'
                }).reset_index()
                area_stats.columns = ['Area', 'Orders', 'Revenue']
                
                fig = px.bar(area_stats, x='Area', y='Orders', title='Orders by Area')
                st.plotly_chart(fig, use_container_width=True)
                
                # Revenue over time
                orders_df['date'] = pd.to_datetime(orders_df['date'])
                daily_revenue = orders_df.groupby(orders_df['date'].dt.date)['price'].sum().reset_index()
                
                fig2 = px.line(daily_revenue, x='date', y='price', title='Daily Revenue')
                st.plotly_chart(fig2, use_container_width=True)
                
                # Status distribution
                status_counts = orders_df['status'].value_counts()
                fig3 = px.pie(values=status_counts.values, names=status_counts.index, title='Order Status Distribution')
                st.plotly_chart(fig3, use_container_width=True)

# TERMS PAGE
elif st.session_state.page == "terms":
    st.markdown(f"<h2 style='text-align:center; color:{accent};'>{L['terms_title']}</h2>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class='glass-card'>
        <h4 style="color:{accent};">{L['golden_rules']}</h4>
        <p>1. {L['rule1']}</p>
        <p>2. {L['rule2']}</p>
        <p>3. {L['rule3']}</p>
        <p>4. {L['rule4']}</p>
        <p>5. {L['rule5']}</p>
        <p>6. {L['rule6']}</p>
        <p>7. {L['rule7']}</p>
    </div>
    """, unsafe_allow_html=True)

# SUPPORT PAGE
elif st.session_state.page == "support":
    st.markdown(f"<h2 style='text-align:center; color:{accent};'>{L['nav_support']}</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="glass-card">
            <h4 style="color:{accent};">📞 {L['contact_us']}</h4>
            <p><b>{L['call_us']}:</b></p>
            <p class="phone-number">{COMPANY_PHONES[0]}</p>
            <p class="phone-number">{COMPANY_PHONES[1]}</p>
            <p><b>{L['whatsapp_us']}:</b></p>
            <a href="{COMPANY_WHATSAPP}" target="_blank">Click to WhatsApp</a>
            <p><b>{L['email_us']}:</b> {COMPANY_EMAIL}</p>
            <p><b>{L['visit_us']}:</b> {COMPANY_ADDRESS}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="glass-card">
            <h4 style="color:{accent};">🕒 Working Hours</h4>
            <p>Saturday - Thursday: 8:00 AM - 10:00 PM</p>
            <p>Friday: 2:00 PM - 8:00 PM</p>
            <p>24/7 Online Support via WhatsApp</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Contact form
    st.markdown(f"<h4 style='color:{accent};'>Send us a message</h4>", unsafe_allow_html=True)
    with st.form("contact_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Your Name")
            email = st.text_input("Your Email")
        with col2:
            phone = st.text_input("Your Phone")
            subject = st.selectbox("Subject", ["General Inquiry", "Order Issue", "Complaint", "Suggestion", "Partnership"])
        
        message = st.text_area("Message")
        
        if st.form_submit_button("Send Message"):
            st.success("Thank you for contacting us! We'll respond within 24 hours.")

# --- 13. CLEAN FOOTER WITH CONTACT INFO ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(f"""
<div class="footer-contact">
    <p style="margin-bottom: 10px;">📞 <span class="phone-number">{COMPANY_PHONES[0]}</span> | <span class="phone-number">{COMPANY_PHONES[1]}</span></p>
    <p>✉️ {COMPANY_EMAIL} | 📍 {COMPANY_ADDRESS}</p>
    <p style="font-size: 0.9rem; opacity: 0.8;">© 2024 Golden Delivery Pro - All rights reserved</p>
</div>
""", unsafe_allow_html=True)
