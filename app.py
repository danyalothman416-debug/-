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
        'user_role': None,  # None, "customer", "driver", "admin"
        'user_name': None,
        'user_phone': None,
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
        'logged_in': False
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
        "fast_title": "⚡ Fast",
        "fast_desc": "Delivery within 24 hours",
        "secure_title": "🔒 Secure",
        "secure_desc": "Your packages are safe with us",
        "free_title": "🎁 Free Delivery",
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
        "admin_portal": "Admin Portal"
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
        "fast_title": "⚡ خێرا",
        "fast_desc": "گەیاندن لە ماوەی ٢٤ کاتژمێردا",
        "secure_title": "🔒 پارێزراو",
        "secure_desc": "پاکەتەکانت سەلامەتن لە لای ئێمە",
        "free_title": "🎁 گەیاندنی خۆڕایی",
        "free_desc": "یەکێک لە هەر ٣ گەیاندنێک بە خۆڕاییە",
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
        "payment_method": "شێوازی پارەدان",
        "cash_on_delivery": "پارەدان لە کاتی گەیاندن",
        "bank_transfer": "گواستنەوەی بانکی",
        "credit_card": "کارتی کرێدت",
        "zain_cash": "زەین کاش",
        "asia_hawala": "ئاسیا حەوالە",
        "assign_driver": "دیاریکردنی شۆفێر",
        "driver_name": "ناوی شۆفێر",
        "driver_phone": "ژمارەی مۆبایلی شۆفێر",
        "driver_status": "دۆخی شۆفێر",
        "driver_available": "بەردەست",
        "driver_busy": "سەرقاڵ",
        "driver_offline": "دەرەوەی خزمەت",
        "rate_delivery": "هەڵسەنگاندنی گەیاندن",
        "leave_review": "بیروبۆچوون بنووسە",
        "submit_feedback": "ناردنی بیروبۆچوون",
        "enter_promo": "کۆدی پڕۆمۆ بنووسە",
        "apply_promo": "جێبەجێکردن",
        "promo_applied": "کۆدی پڕۆمۆ جێبەجێ کرا!",
        "invalid_promo": "کۆدی پڕۆمۆ نادروستە",
        "loyalty_points": "خاڵی دڵسۆزی",
        "points_balance": "ڕێژەی خاڵەکانت",
        "redeem_points": "بەکارهێنانی خاڵەکان",
        "delivery_notes": "تێبینی گەیاندن",
        "gate_code": "کۆدی دەروازە",
        "building_number": "ژمارەی باڵەخانە",
        "contact_us": "پەیوەندیمان پێوە بکە",
        "call_us": "پەیوەندیمان پێوە بکە",
        "whatsapp_us": "واتسئاپ",
        "email_us": "ئیمەیڵ",
        "visit_us": "سەردانمان بکە",
        "update_status": "گۆڕینی دۆخی داواکاری",
        "current_status": "دۆخی ئێستا",
        "new_status": "دۆخی نوێ",
        "change_status": "گۆڕینی دۆخ",
        "my_deliveries": "گەیاندنەکانی من",
        "register": "تۆماربوون",
        "login": "چوونەژوورەوە",
        "password": "وشەی نهێنی",
        "confirm_password": "دووپاتکردنەوەی وشەی نهێنی",
        "full_name": "ناوی تەواو",
        "register_success": "تۆماربوون سەرکەوتوو بوو! تکایە بچۆژوورەوە.",
        "login_success": "چوونەژوورەوە سەرکەوتوو بوو!",
        "login_error": "ئیمەیڵ یان وشەی نهێنی هەڵەیە",
        "password_mismatch": "وشەی نهێنییەکان یەک ناگرنەوە",
        "email_exists": "ئیمەیڵەکە پێشتر تۆمارکراوە",
        "driver_portal": "پۆرتاڵی شۆفێر",
        "admin_portal": "پۆرتاڵی بەڕێوەبەر"
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
        "fast_title": "⚡ سريع",
        "fast_desc": "التوصيل خلال ٢٤ ساعة",
        "secure_title": "🔒 آمن",
        "secure_desc": "طرودك آمنة معنا",
        "free_title": "🎁 توصيل مجاني",
        "free_desc": "واحدة من كل ٣ توصيلات مجانية",
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
        "payment_method": "طريقة الدفع",
        "cash_on_delivery": "الدفع عند الاستلام",
        "bank_transfer": "تحويل بنكي",
        "credit_card": "بطاقة ائتمان",
        "zain_cash": "زين كاش",
        "asia_hawala": "آسيا حوالة",
        "assign_driver": "تعيين سائق",
        "driver_name": "اسم السائق",
        "driver_phone": "رقم السائق",
        "driver_status": "حالة السائق",
        "driver_available": "متاح",
        "driver_busy": "مشغول",
        "driver_offline": "غير متصل",
        "rate_delivery": "قيم توصيلتك",
        "leave_review": "اترك تعليقاً",
        "submit_feedback": "إرسال التقييم",
        "enter_promo": "أدخل كود العرض",
        "apply_promo": "تطبيق",
        "promo_applied": "تم تطبيق كود العرض!",
        "invalid_promo": "كود العرض غير صالح",
        "loyalty_points": "نقاط الولاء",
        "points_balance": "رصيد نقاطك",
        "redeem_points": "استبدال النقاط",
        "delivery_notes": "ملاحظات التوصيل",
        "gate_code": "رمز البوابة",
        "building_number": "رقم المبنى",
        "contact_us": "اتصل بنا",
        "call_us": "اتصل",
        "whatsapp_us": "واتساب",
        "email_us": "البريد الإلكتروني",
        "visit_us": "زورنا",
        "update_status": "تحديث حالة الطلب",
        "current_status": "الحالة الحالية",
        "new_status": "الحالة الجديدة",
        "change_status": "تغيير الحالة",
        "my_deliveries": "توصيلاتي",
        "register": "تسجيل",
        "login": "دخول",
        "password": "كلمة المرور",
        "confirm_password": "تأكيد كلمة المرور",
        "full_name": "الاسم الكامل",
        "register_success": "تم التسجيل بنجاح! الرجاء تسجيل الدخول.",
        "login_success": "تم تسجيل الدخول بنجاح!",
        "login_error": "البريد الإلكتروني أو كلمة المرور غير صحيحة",
        "password_mismatch": "كلمات المرور غير متطابقة",
        "email_exists": "البريد الإلكتروني مسجل مسبقاً",
        "driver_portal": "بوابة السائق",
        "admin_portal": "بوابة المسؤول"
    }
}

# --- 5. NEIGHBORHOODS ---
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

# --- 6. DATA FILES ---
ORDERS_FILE = "orders.csv"
DRIVERS_FILE = "drivers.csv"
CUSTOMERS_FILE = "customers.csv"
FEEDBACK_FILE = "feedback.csv"
PROMO_CODES_FILE = "promos.json"
USERS_FILE = "users.json"

# --- 7. DATA FUNCTIONS WITH ERROR HANDLING ---
def safe_load_csv(file_path, columns):
    """Safely load a CSV file with error handling"""
    try:
        if os.path.exists(file_path):
            df = pd.read_csv(file_path, dtype={"phone": str, "order_id": str})
            # Ensure all expected columns exist
            for col in columns:
                if col not in df.columns:
                    df[col] = None
            return df
        return pd.DataFrame(columns=columns)
    except Exception as e:
        st.error(f"Error loading {file_path}: {e}")
        return pd.DataFrame(columns=columns)

def safe_save_csv(df, file_path):
    """Safely save DataFrame to CSV"""
    try:
        df.to_csv(file_path, index=False)
        return True
    except Exception as e:
        st.error(f"Error saving {file_path}: {e}")
        return False

def load_orders():
    columns = ["order_id", "date", "customer", "shop", "phone", "area", 
               "address", "shop_addr", "price", "status", "user_email", 
               "driver_id", "payment_method", "delivery_notes", "promo_code",
               "estimated_delivery", "actual_delivery", "rating", "review"]
    return safe_load_csv(ORDERS_FILE, columns)

def save_orders(df):
    return safe_save_csv(df, ORDERS_FILE)

def load_drivers():
    columns = ["driver_id", "name", "phone", "email", "status", "area", 
               "join_date", "total_deliveries", "rating", "current_order_id"]
    return safe_load_csv(DRIVERS_FILE, columns)

def save_drivers(df):
    return safe_save_csv(df, DRIVERS_FILE)

def load_customers():
    columns = ["customer_id", "name", "phone", "email", "join_date", 
               "total_orders", "loyalty_points", "favorite_area", "total_spent"]
    return safe_load_csv(CUSTOMERS_FILE, columns)

def save_customers(df):
    return safe_save_csv(df, CUSTOMERS_FILE)

def load_feedback():
    columns = ["feedback_id", "order_id", "customer_name", "rating", "review", "date"]
    return safe_load_csv(FEEDBACK_FILE, columns)

def save_feedback(df):
    return safe_save_csv(df, FEEDBACK_FILE)

def load_promos():
    try:
        if os.path.exists(PROMO_CODES_FILE):
            with open(PROMO_CODES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Error loading promos: {e}")
    return {
        "WELCOME10": {"discount": 10, "type": "percentage", "min_order": 5000, "expiry": "2025-12-31"},
        "FREESHIP": {"discount": 3000, "type": "fixed", "min_order": 10000, "expiry": "2025-12-31"},
        "FIRST3": {"discount": 15, "type": "percentage", "min_order": 3000, "expiry": "2025-12-31"},
        "GOLDEN50": {"discount": 50, "type": "percentage", "min_order": 20000, "expiry": "2025-06-30"},
        "KIRKUK10": {"discount": 10, "type": "percentage", "min_order": 0, "expiry": "2025-12-31"}
    }

def save_promos(promos):
    try:
        with open(PROMO_CODES_FILE, 'w', encoding='utf-8') as f:
            json.dump(promos, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Error saving promos: {e}")
        return False

def load_users():
    """Load users from JSON file"""
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Error loading users: {e}")
    return {"admin": [], "drivers": [], "customers": []}

def save_users(users_data):
    """Save users to JSON file"""
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users_data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Error saving users: {e}")
        return False

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def validate_iraq_phone(phone):
    """Validate Iraqi phone number format"""
    pattern = r'^07\d{9}$'
    return bool(re.match(pattern, str(phone)))

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

# --- 8. HELPER FUNCTIONS ---
def generate_order_id():
    return f"GD-{datetime.now().strftime('%Y%m')}-{str(uuid.uuid4())[:8].upper()}"

def calculate_loyalty_points(price):
    return int(price / 1000)

def validate_promo_code(code, price, promos):
    try:
        if code in promos:
            promo = promos[code]
            if datetime.strptime(promo['expiry'], '%Y-%m-%d') > datetime.now():
                if price >= promo['min_order']:
                    if promo['type'] == 'percentage':
                        discount = (price * promo['discount']) / 100
                    else:
                        discount = promo['discount']
                    return True, discount, promo
    except:
        pass
    return False, 0, None

def send_sms_notification(phone, message):
    """Simulate SMS notification (replace with real API later)"""
    try:
        notification = {
            'type': 'sms',
            'to': phone,
            'message': message,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'status': 'sent'
        }
        if 'notifications' in st.session_state:
            st.session_state.notifications.append(notification)
        print(f"SMS to {phone}: {message}")
        return True
    except:
        return False

def send_email_notification(email, subject, message):
    """Simulate email notification (replace with real API later)"""
    try:
        notification = {
            'type': 'email',
            'to': email,
            'subject': subject,
            'message': message,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'status': 'sent'
        }
        if 'notifications' in st.session_state:
            st.session_state.notifications.append(notification)
        print(f"Email to {email}: {subject} - {message}")
        return True
    except:
        return False

def add_in_app_notification(message, type="info"):
    """Add in-app notification"""
    if 'notifications' in st.session_state:
        st.session_state.notifications.append({
            'type': 'in_app',
            'message': message,
            'notification_type': type,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'read': False
        })

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

def update_customer_loyalty(phone, price, name="Unknown"):
    try:
        customers_df = load_customers()
        if phone in customers_df['phone'].values:
            idx = customers_df[customers_df['phone'] == phone].index[0]
            customers_df.loc[idx, 'loyalty_points'] += calculate_loyalty_points(price)
            customers_df.loc[idx, 'total_orders'] += 1
            customers_df.loc[idx, 'total_spent'] += price
        else:
            new_customer = pd.DataFrame([{
                "customer_id": str(uuid.uuid4())[:8],
                "name": name,
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
        return True
    except Exception as e:
        st.error(f"Error updating customer loyalty: {e}")
        return False

def update_order_status(order_id, new_status):
    """Update order status and handle related updates"""
    try:
        orders_df = load_orders()
        drivers_df = load_drivers()
        
        if order_id in orders_df['order_id'].values:
            idx = orders_df[orders_df['order_id'] == order_id].index[0]
            old_status = orders_df.loc[idx, 'status']
            
            # Update order status
            orders_df.loc[idx, 'status'] = new_status
            
            # If delivered, set actual delivery time
            if new_status == "Delivered":
                orders_df.loc[idx, 'actual_delivery'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                
                # Free up driver
                driver_id = orders_df.loc[idx, 'driver_id']
                if pd.notna(driver_id):
                    driver_idx = drivers_df[drivers_df['driver_id'] == driver_id].index
                    if len(driver_idx) > 0:
                        drivers_df.loc[driver_idx[0], 'status'] = 'Available'
                        drivers_df.loc[driver_idx[0], 'total_deliveries'] += 1
                        drivers_df.loc[driver_idx[0], 'current_order_id'] = None
                
                # Send notification
                phone = orders_df.loc[idx, 'phone']
                send_sms_notification(phone, f"Your order {order_id} has been delivered!")
            
            # If cancelled, free up driver
            if new_status == "Cancelled":
                driver_id = orders_df.loc[idx, 'driver_id']
                if pd.notna(driver_id):
                    driver_idx = drivers_df[drivers_df['driver_id'] == driver_id].index
                    if len(driver_idx) > 0:
                        drivers_df.loc[driver_idx[0], 'status'] = 'Available'
                        drivers_df.loc[driver_idx[0], 'current_order_id'] = None
            
            save_orders(orders_df)
            save_drivers(drivers_df)
            
            add_in_app_notification(f"Order {order_id} status changed from {old_status} to {new_status}", "info")
            return True, f"Status updated to {new_status}"
        return False, "Order not found"
    except Exception as e:
        return False, f"Error updating status: {e}"

def assign_driver_to_order(order_id, driver_id):
    """Assign a driver to an order"""
    try:
        orders_df = load_orders()
        drivers_df = load_drivers()
        
        if order_id in orders_df['order_id'].values:
            # Update order
            orders_df.loc[orders_df['order_id'] == order_id, 'driver_id'] = driver_id
            orders_df.loc[orders_df['order_id'] == order_id, 'status'] = 'Picked Up'
            
            # Update driver
            drivers_df.loc[drivers_df['driver_id'] == driver_id, 'status'] = 'Busy'
            drivers_df.loc[drivers_df['driver_id'] == driver_id, 'current_order_id'] = order_id
            
            save_orders(orders_df)
            save_drivers(drivers_df)
            
            # Send notification to driver
            driver = drivers_df[drivers_df['driver_id'] == driver_id].iloc[0]
            add_in_app_notification(f"Driver {driver['name']} assigned to order {order_id}", "info")
            
            return True
    except Exception as e:
        st.error(f"Error assigning driver: {e}")
    return False

# --- 9. TOP BAR ---
L = languages[st.session_state.lang_choice]

top_col1, top_col2, top_col3 = st.columns([2, 1, 1])
with top_col1:
    st.markdown(f"<h2 style='color:#D4AF37; margin:0;'>{L['title']}</h2>", unsafe_allow_html=True)
with top_col2:
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

L = languages[st.session_state.lang_choice]

# --- 10. CSS STYLING ---
is_dark = st.session_state.theme_choice == "Dark 🌙"

if is_dark:
    main_bg = "#0a0c10"
    card_bg = "#1e2329"
    text_color = "#ffffff"
    text_secondary = "#e0e0e0"
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

st.markdown(f"""
<style>
    [data-testid="stSidebar"] {{ display: none; }}
    
    html, body, [data-testid="stAppViewContainer"], 
    .main, .block-container, .stApp {{
        background-color: {main_bg} !important;
        color: {text_color} !important;
    }}
    
    h1, h2, h3, h4, h5, h6, p, span, div, label, .stMarkdown {{
        color: {text_color} !important;
    }}
    
    .secondary-text, .stCaption, .stMarkdown small {{
        color: {text_secondary} !important;
    }}
    
    input, textarea, .stTextInput input, .stTextArea textarea {{
        background-color: {input_bg} !important;
        color: {text_color} !important;
        border: 1px solid {border_color} !important;
    }}
    
    .stSelectbox div[data-baseweb="select"] {{
        background-color: {input_bg} !important;
        border-color: {border_color} !important;
    }}
    
    .stSelectbox div[data-baseweb="select"] span {{
        color: {text_color} !important;
    }}
    
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
    
    .stForm {{
        background-color: {card_bg} !important;
        border: 1px solid {accent}40 !important;
        border-radius: 20px !important;
        padding: 30px !important;
    }}
    
    .glass-card {{
        background-color: {card_bg} !important;
        border-radius: 20px !important;
        padding: 25px !important;
        border: 1px solid {accent}30 !important;
        margin-bottom: 20px !important;
        color: {text_color} !important;
    }}
    
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
    
    .stButton button {{
        background-color: {accent} !important;
        color: {'black' if not is_dark else 'white'} !important;
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
    
    .stAlert {{
        background-color: {card_bg} !important;
        color: {text_color} !important;
        border-left-color: {accent} !important;
    }}
    
    .stSuccess {{
        background-color: {card_bg} !important;
        color: #00C851 !important;
    }}
    
    .streamlit-expanderHeader {{
        background-color: {card_bg} !important;
        color: {text_color} !important;
    }}
    
    .dataframe, .stDataFrame, .stDataFrame div {{
        color: {text_color} !important;
    }}
    
    .dataframe td, .dataframe th {{
        background-color: {card_bg} !important;
        color: {text_color} !important;
        border-color: {border_color} !important;
    }}
    
    [data-testid="stMetricValue"] {{
        color: {accent} !important;
        font-size: 2rem !important;
    }}
    
    .card-title {{
        color: {accent} !important;
        font-size: 1.5rem !important;
    }}
    
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
    
    [dir="{L['dir']}"] {{
        text-align: {L['align']} !important;
    }}
    
    .notification-badge {{
        background-color: red;
        color: white;
        border-radius: 50%;
        padding: 2px 8px;
        font-size: 0.8em;
        margin-left: 5px;
    }}
</style>
""", unsafe_allow_html=True)

# --- 11. NAVIGATION ---
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
    
    if not orders_df.empty:
        st.markdown(f"<h3 style='color:{accent};'>📋 Recent Orders</h3>", unsafe_allow_html=True)
        recent_orders = orders_df.tail(5)[['order_id', 'customer', 'area', 'price', 'status']]
        st.dataframe(recent_orders, use_container_width=True)

# ORDER PAGE
elif st.session_state.page == "order":
    st.markdown(f"<h2 style='text-align:center; color:{accent};'>{L['nav_order']}</h2>", unsafe_allow_html=True)
    
    st.info(L["free_info"])
    
    orders_df = load_orders()
    promos = load_promos()
    
    col1, col2 = st.columns(2)
    with col1:
        customer_name = st.text_input(L['customer_name'])
        phone_input = st.text_input(L['phone'], placeholder="07xx xxx xxxx", 
                                   value=st.session_state.user_phone if st.session_state.user_phone else "")
        shop_name = st.text_input(L['shop_name'])
    
    with col2:
        payment_method = st.selectbox(L['payment_method'], 
                                      [L['cash_on_delivery'], L['bank_transfer'], 
                                       L['credit_card'], L['zain_cash'], L['asia_hawala']])
        delivery_notes = st.text_area(L['delivery_notes'], placeholder=L['gate_code'])
    
    is_free = False
    if phone_input:
        customer_orders = orders_df[orders_df['phone'] == phone_input]
        order_count = len(customer_orders)
        is_free = (order_count + 1) % 3 == 0
        if is_free:
            st.success(L["free_success"])
        
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
    
    col1, col2 = st.columns(2)
    with col1:
        area = st.selectbox(L['area'], ["-- " + L['area'] + " --"] + KIRKUK_AREAS)
        full_addr = st.text_area(L['full_addr'])
    with col2:
        shop_addr = st.text_input(L['shop_addr'])
        
        base_price = 0 if is_free else 3000
        price = st.number_input(L['price'], value=base_price, min_value=0, step=1000)
        
        promo_code = st.text_input(L['enter_promo'])
        if promo_code:
            valid, discount, promo = validate_promo_code(promo_code, price, promos)
            if valid:
                price = price - discount
                st.success(f"{L['promo_applied']} Discount: {discount:,.0f} IQD")
            else:
                st.warning(L['invalid_promo'])
    
    if st.button(L['submit'], use_container_width=True):
        if customer_name and phone_input and area and "--" not in area:
            if not validate_iraq_phone(phone_input):
                st.error("Please enter a valid Iraqi phone number (07xx xxx xxxx)")
            else:
                order_id = generate_order_id()
                estimated_time = calculate_estimated_delivery()
                
                # FIXED: Added shop_addr to the new order
                new_order = pd.DataFrame([{
                    "order_id": order_id,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "customer": customer_name,
                    "shop": shop_name,
                    "phone": phone_input,
                    "area": area,
                    "address": full_addr,
                    "shop_addr": shop_addr,  # This was missing
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
                
                orders_df = pd.concat([orders_df, new_order], ignore_index=True)
                if save_orders(orders_df):
                    update_customer_loyalty(phone_input, price, customer_name)
                    send_sms_notification(phone_input, f"Golden Delivery: Order {order_id} confirmed! Estimated delivery: {estimated_time}")
                    if st.session_state.user_email:
                        send_email_notification(st.session_state.user_email, f"Order Confirmation {order_id}", 
                                              f"Your order has been confirmed. Estimated delivery: {estimated_time}")
                    
                    add_in_app_notification(f"New order created: {order_id}", "success")
                    
                    st.success(f"✅ {L['submit']} Successful! Order ID: {order_id}")
                    st.balloons()
                    st.session_state.current_order_id = order_id
        else:
            st.error("Please fill all required fields")

# TRACK PAGE
elif st.session_state.page == "track":
    st.markdown(f"<h2 style='text-align:center; color:{accent};'>{L['track_order']}</h2>", unsafe_allow_html=True)
    
    orders_df = load_orders()
    
    track_method = st.radio("Track by:", ["Order ID", "Phone Number"], horizontal=True)
    
    if track_method == "Order ID":
        order_id = st.text_input(L['enter_order_id'])
        if order_id:
            order = orders_df[orders_df['order_id'] == order_id]
            if not order.empty:
                order = order.iloc[0]
                
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
                
                st.markdown(f"<h4 style='color:{accent};'>Delivery Timeline</h4>", unsafe_allow_html=True)
                timeline_data = {
                    "Order Placed": order['date'],
                    "Picked Up": order['date'] if order['status'] not in ["Pending"] else "Pending",
                    "In Transit": order['date'] if order['status'] in ["In Transit", "Out for Delivery", "Delivered"] else "Pending",
                    "Out for Delivery": order['date'] if order['status'] in ["Out for Delivery", "Delivered"] else "Pending",
                    "Delivered": order['actual_delivery'] if order['status'] == "Delivered" else "Pending"
                }
                
                for event, time in timeline_data.items():
                    if time != "Pending" and pd.notna(time):
                        st.success(f"✅ {event}: {time}")
                    else:
                        st.info(f"⏳ {event}: Pending")
                
                if status == "Delivered" and pd.isna(order['rating']):
                    st.markdown(f"<h4 style='color:{accent};'>{L['rate_delivery']}</h4>", unsafe_allow_html=True)
                    rating = st.slider("Rating", 1, 5, 5)
                    review = st.text_area(L['leave_review'])
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
                        
                        st.success("Thank you for your feedback!")
            else:
                st.warning("Order not found")
    
    else:
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
    
    # Check if user is logged in
    if not st.session_state.get('logged_in', False):
        # Login/Register
        tab1, tab2 = st.tabs([f"🔑 {L['login']}", f"📝 {L['register']}"])
        
        with tab1:
            st.markdown(f"""
            <div class="glass-card" style="text-align:center;">
                <p>{L['access_account']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.form("login_form"):
                email = st.text_input("Email")
                password = st.text_input(L['password'], type="password")
                role = st.selectbox("Login as", ["Customer", "Driver", "Admin"])
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button(L['login']):
                        users_data = load_users()
                        
                        if role == "Admin":
                            # Admin login
                            admin_email = "admin@goldendelivery.com"
                            admin_password_hash = hash_password("Admin@2026")
                            
                            if email == admin_email and hash_password(password) == admin_password_hash:
                                st.session_state.user_email = email
                                st.session_state.user_role = "admin"
                                st.session_state.user_name = "Administrator"
                                st.session_state.logged_in = True
                                st.session_state.admin_authenticated = True
                                add_in_app_notification("Admin logged in", "info")
                                st.success(L['login_success'])
                                st.rerun()
                            else:
                                st.error(L['login_error'])
                        
                        elif role == "Driver":
                            # Driver login
                            for driver in users_data.get('drivers', []):
                                if driver['email'] == email and hash_password(password) == driver['password_hash']:
                                    st.session_state.user_email = email
                                    st.session_state.user_role = "driver"
                                    st.session_state.user_name = driver['name']
                                    st.session_state.driver_id = driver['driver_id']
                                    st.session_state.logged_in = True
                                    st.success(L['login_success'])
                                    st.rerun()
                            st.error(L['login_error'])
                        
                        else:  # Customer
                            for customer in users_data.get('customers', []):
                                if customer['email'] == email and hash_password(password) == customer['password_hash']:
                                    st.session_state.user_email = email
                                    st.session_state.user_role = "customer"
                                    st.session_state.user_name = customer['name']
                                    st.session_state.user_phone = customer['phone']
                                    st.session_state.logged_in = True
                                    st.success(L['login_success'])
                                    st.rerun()
                            st.error(L['login_error'])
        
        with tab2:
            with st.form("register_form"):
                name = st.text_input(L['full_name'])
                email = st.text_input("Email")
                phone = st.text_input(L['phone'], placeholder="07xx xxx xxxx")
                password = st.text_input(L['password'], type="password")
                confirm_password = st.text_input(L['confirm_password'], type="password")
                area = st.selectbox(L['area'], KIRKUK_AREAS[:10])
                
                if st.form_submit_button(L['register']):
                    if password != confirm_password:
                        st.error(L['password_mismatch'])
                    elif not validate_email(email):
                        st.error("Invalid email format")
                    elif not validate_iraq_phone(phone):
                        st.error("Invalid phone number")
                    else:
                        users_data = load_users()
                        
                        # Check if email exists
                        all_users = users_data['customers'] + users_data['drivers']
                        if any(u['email'] == email for u in all_users):
                            st.error(L['email_exists'])
                        else:
                            new_user = {
                                "name": name,
                                "email": email,
                                "phone": phone,
                                "password_hash": hash_password(password),
                                "join_date": datetime.now().strftime("%Y-%m-%d"),
                                "area": area
                            }
                            users_data['customers'].append(new_user)
                            if save_users(users_data):
                                st.success(L['register_success'])
    else:
        # Logged in user profile
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["👤 Profile", "📦 Orders", "⭐ Loyalty", "🔔 Notifications", "⚙️ Settings"])
        
        with tab1:
            st.markdown(f"""
            <div class="glass-card">
                <h4 style="color:{accent};">{L['signed_in_as']}</h4>
                <p><b>Name:</b> {st.session_state.user_name}</p>
                <p><b>Email:</b> {st.session_state.user_email}</p>
                <p><b>Role:</b> {st.session_state.user_role}</p>
            </div>
            """, unsafe_allow_html=True)
            
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
            if st.session_state.user_role == "driver" and st.session_state.driver_id:
                # Driver's deliveries
                st.subheader(L['my_deliveries'])
                driver_orders = orders_df[orders_df['driver_id'] == st.session_state.driver_id]
                if not driver_orders.empty:
                    st.dataframe(driver_orders[['order_id', 'date', 'customer', 'area', 'price', 'status']], use_container_width=True)
                    
                    # Driver can update status
                    st.subheader(L['update_status'])
                    for idx, order in driver_orders.iterrows():
                        if order['status'] not in ['Delivered', 'Cancelled']:
                            with st.expander(f"Order {order['order_id']} - {order['status']}"):
                                st.write(f"**Customer:** {order['customer']}")
                                st.write(f"**Area:** {order['area']}")
                                st.write(f"**Current Status:** {order['status']}")
                                
                                status_options = ["Pending", "Picked Up", "In Transit", "Out for Delivery", "Delivered"]
                                current_idx = status_options.index(order['status']) if order['status'] in status_options else 0
                                new_status = st.selectbox(L['new_status'], status_options[current_idx+1:], key=f"driver_status_{order['order_id']}")
                                
                                if st.button(f"{L['change_status']} - {order['order_id']}", key=f"update_{order['order_id']}"):
                                    success, message = update_order_status(order['order_id'], new_status)
                                    if success:
                                        st.success(message)
                                        st.rerun()
                                    else:
                                        st.error(message)
                else:
                    st.info("No deliveries assigned yet")
            
            elif st.session_state.user_phone:
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
            st.subheader("🔔 Notifications")
            if st.session_state.notifications:
                for notif in reversed(st.session_state.notifications[-10:]):
                    if notif['type'] == 'in_app':
                        icon = "🔔" if notif['notification_type'] == 'info' else "✅" if notif['notification_type'] == 'success' else "❌"
                        st.info(f"{icon} {notif['message']} - {notif['timestamp']}")
                if st.button("Clear Notifications"):
                    st.session_state.notifications = []
                    st.rerun()
            else:
                st.info("No notifications")
        
        with tab5:
            st.markdown(f"""
            <div class="glass-card">
                <h4 style="color:{accent};">Settings</h4>
            </div>
            """, unsafe_allow_html=True)
            
            st.checkbox("📱 SMS Notifications", value=True)
            st.checkbox("📧 Email Notifications", value=True)
            st.checkbox("💬 WhatsApp Updates", value=True)
            
            if st.button(L["logout"]):
                for key in ['user_email', 'user_role', 'user_name', 'user_phone', 'logged_in', 'admin_authenticated', 'driver_id']:
                    st.session_state[key] = None
                st.rerun()
        
        # ADMIN PORTAL
        if st.session_state.user_role == "admin" and st.session_state.logged_in:
            st.divider()
            st.subheader(f"🔐 {L['admin_portal']}")
            
            admin_tab1, admin_tab2, admin_tab3, admin_tab4, admin_tab5 = st.tabs([
                "📊 Dashboard", "🚚 Drivers", "📦 Orders", "📈 Analytics", "👥 Users"
            ])
            
            with admin_tab1:
                orders_df = load_orders()
                customers_df = load_customers()
                drivers_df = load_drivers()
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Orders", len(orders_df))
                with col2:
                    st.metric("Total Customers", len(customers_df))
                with col3:
                    st.metric("Active Drivers", len(drivers_df[drivers_df['status'] == 'Available']))
                with col4:
                    st.metric("Revenue", f"{orders_df['price'].sum():,} IQD")
                
                st.subheader("Recent Orders")
                st.dataframe(orders_df.tail(10), use_container_width=True)
            
            with admin_tab2:
                drivers_df = load_drivers()
                
                with st.expander("➕ Add New Driver"):
                    with st.form("add_driver_form"):
                        col1, col2 = st.columns(2)
                        with col1:
                            driver_name = st.text_input("Driver Name")
                            driver_phone = st.text_input("Driver Phone")
                            driver_email = st.text_input("Driver Email")
                        with col2:
                            driver_area = st.selectbox("Assigned Area", KIRKUK_AREAS)
                            driver_status = st.selectbox("Status", ["Available", "Busy", "Offline"])
                            driver_password = st.text_input("Password", type="password")
                        
                        if st.form_submit_button("Add Driver"):
                            driver_id = str(uuid.uuid4())[:8]
                            new_driver = pd.DataFrame([{
                                "driver_id": driver_id,
                                "name": driver_name,
                                "phone": driver_phone,
                                "email": driver_email,
                                "status": driver_status,
                                "area": driver_area,
                                "join_date": datetime.now().strftime("%Y-%m-%d"),
                                "total_deliveries": 0,
                                "rating": 5.0,
                                "current_order_id": None
                            }])
                            drivers_df = pd.concat([drivers_df, new_driver], ignore_index=True)
                            save_drivers(drivers_df)
                            
                            # Add to users
                            users_data = load_users()
                            users_data['drivers'].append({
                                "driver_id": driver_id,
                                "name": driver_name,
                                "email": driver_email,
                                "phone": driver_phone,
                                "password_hash": hash_password(driver_password),
                                "area": driver_area
                            })
                            save_users(users_data)
                            
                            st.success("Driver added!")
                            st.rerun()
                
                st.subheader("Drivers List")
                st.dataframe(drivers_df, use_container_width=True)
            
            with admin_tab3:
                orders_df = load_orders()
                drivers_df = load_drivers()
                
                # Order Management
                st.subheader("Order Management")
                status_filter = st.selectbox("Filter by Status", 
                    ["All", "Pending", "Picked Up", "In Transit", "Out for Delivery", "Delivered", "Cancelled"])
                
                if status_filter != "All":
                    filtered_orders = orders_df[orders_df['status'] == status_filter]
                else:
                    filtered_orders = orders_df
                
                # Assign drivers to pending orders
                for idx, order in filtered_orders.iterrows():
                    if pd.isna(order['driver_id']) and order['status'] not in ['Delivered', 'Cancelled']:
                        with st.expander(f"Order {order['order_id']} - {order['customer']} - {order['area']}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Area:** {order['area']}")
                                st.write(f"**Price:** {int(order['price']):,} IQD")
                            with col2:
                                available_drivers = drivers_df[drivers_df['status'] == 'Available']
                                if not available_drivers.empty:
                                    driver_choice = st.selectbox("Assign Driver", 
                                                                available_drivers['name'].tolist(),
                                                                key=f"admin_driver_{order['order_id']}")
                                    if st.button("Assign", key=f"admin_assign_{order['order_id']}"):
                                        driver = available_drivers[available_drivers['name'] == driver_choice].iloc[0]
                                        if assign_driver_to_order(order['order_id'], driver['driver_id']):
                                            st.success(f"Driver {driver_choice} assigned!")
                                            st.rerun()
                                else:
                                    st.warning("No available drivers")
                
                # Update order status
                st.subheader(L['update_status'])
                order_to_update = st.selectbox("Select Order", 
                    [f"{o['order_id']} - {o['customer']} ({o['status']})" for _, o in filtered_orders.iterrows()])
                
                if order_to_update:
                    order_id = order_to_update.split(" - ")[0]
                    order = orders_df[orders_df['order_id'] == order_id].iloc[0]
                    
                    st.write(f"**Current Status:** {order['status']}")
                    status_options = ["Pending", "Picked Up", "In Transit", "Out for Delivery", "Delivered", "Cancelled"]
                    new_status = st.selectbox(L['new_status'], status_options, key="admin_update_status")
                    
                    if st.button(L['change_status']):
                        success, message = update_order_status(order_id, new_status)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                
                st.subheader("All Orders")
                st.dataframe(filtered_orders, use_container_width=True)
            
            with admin_tab4:
                orders_df = load_orders()
                
                area_stats = orders_df.groupby('area').agg({
                    'order_id': 'count',
                    'price': 'sum'
                }).reset_index()
                area_stats.columns = ['Area', 'Orders', 'Revenue']
                
                fig = px.bar(area_stats, x='Area', y='Orders', title='Orders by Area')
                st.plotly_chart(fig, use_container_width=True)
                
                orders_df['date'] = pd.to_datetime(orders_df['date'])
                daily_revenue = orders_df.groupby(orders_df['date'].dt.date)['price'].sum().reset_index()
                
                fig2 = px.line(daily_revenue, x='date', y='price', title='Daily Revenue')
                st.plotly_chart(fig2, use_container_width=True)
                
                status_counts = orders_df['status'].value_counts()
                fig3 = px.pie(values=status_counts.values, names=status_counts.index, title='Order Status Distribution')
                st.plotly_chart(fig3, use_container_width=True)
            
            with admin_tab5:
                users_data = load_users()
                
                st.subheader("Customers")
                if users_data['customers']:
                    customers_list = pd.DataFrame(users_data['customers'])
                    st.dataframe(customers_list[['name', 'email', 'phone', 'join_date', 'area']], use_container_width=True)
                else:
                    st.info("No customers registered")
                
                st.subheader("Drivers")
                if users_data['drivers']:
                    drivers_list = pd.DataFrame(users_data['drivers'])
                    st.dataframe(drivers_list[['name', 'email', 'phone', 'area']], use_container_width=True)
                else:
                    st.info("No drivers registered")

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

# --- 13. FOOTER ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(f"""
<div class="footer-contact">
    <p style="margin-bottom: 10px;">📞 <span class="phone-number">{COMPANY_PHONES[0]}</span> | <span class="phone-number">{COMPANY_PHONES[1]}</span></p>
    <p>✉️ {COMPANY_EMAIL} | 📍 {COMPANY_ADDRESS}</p>
    <p style="font-size: 0.9rem; opacity: 0.8;">© 2024 Golden Delivery Pro - All rights reserved</p>
</div>
""", unsafe_allow_html=True)
