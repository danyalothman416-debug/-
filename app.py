import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import uuid
import json
import plotly.express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
from io import BytesIO
import base64
import random
import time

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="گۆڵدن دلیڤەری پرۆ - کەرکوک", 
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
        'lang_choice': "کوردی 🇭🇺",
        'theme_choice': "Dark 🌙",
        'driver_id': None,
        'cart': [],
        'notifications': [],
        'order_history': [],
        'favorites': [],
        'current_order_id': None,
        'currency': 'IQD',
        'offline_orders': [],
        'notification_preferences': {'sms': True, 'email': True, 'whatsapp': True},
        'online': True
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_states()

# --- 3. COMPANY INFO ---
COMPANY_PHONES = ["07801352003", "07721959922"]
COMPANY_EMAIL = "Danyalexpert@gmail.com"
COMPANY_ADDRESS = "کەرکوک، شەقامی سەرەکی"
COMPANY_WHATSAPP = "https://wa.me/9647801352003"
EMERGENCY_POLICE = "104"
EMERGENCY_AMBULANCE = "122"

# --- 4. NEIGHBORHOOD ZONES ---
NEIGHBORHOOD_ZONES = {
    "باکوور": ["Arfa / عرفة", "Tis'in / تسعين", "Shoraw / شوراو", "Rahim Awa / رحيماوة", "Quraya / قورية"],
    "باشوور": ["Al-Wasiti / الواسطي", "Al-Nasr / النصر", "Azadi / ازادي", "Wahid Huzairan / واحد حزيران"],
    "ڕۆژهەڵات": ["Kirkuk Citadel / قلعة كركوك", "Musalla / مصلى", "Imam Qasim / امام قاسم", "Shorija / الشورجة"],
    "ڕۆژئاوا": ["Hasiraka / حصيرةكة", "Tapai Malla Abdulla / تبة ملا عبدulla", "Rahimawa / رحيم آوه", "Almas / الماس"]
}

# --- 5. COMPLETE NEIGHBORHOODS LIST ---
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

# --- 6. MULTI-LANGUAGE UI STRINGS (بە تەواوی) ---
languages = {
    "English 🇬🇧": {
        "dir": "ltr", "align": "left",
        "title": "GOLDEN DELIVERY PRO",
        "desc": "Experience the gold standard of logistics in Kirkuk.",
        "nav_home": "Home", "nav_order": "Order", "nav_track": "Track",
        "nav_offers": "Offers", "nav_profile": "Account", "nav_terms": "Terms",
        "nav_support": "Support",
        "customer_name": "Customer Name", "shop_name": "Shop Name",
        "shop_addr": "Shop Address", "phone": "Phone Number",
        "area": "Neighborhood", "full_addr": "Address Details",
        "price": "Price (IQD)", "submit": "Confirm Order",
        "free_info": "🎁 Special: 1 out of every 3 deliveries is FREE!",
        "free_success": "🎊 Loyalty Reward: This delivery is 0 IQD!",
        "google_btn": "Sign in with Google", "logout": "Logout",
        "settings": "Settings", "admin_pass_label": "Enter Admin Password",
        "admin_error": "❌ Incorrect Password", "mgmt_links": "Management Links",
        "terms_title": "📜 Terms and Rules", "contact_us": "Contact Us",
        "call_us": "Call Us", "whatsapp_us": "WhatsApp",
        "email_us": "Email Us", "visit_us": "Visit Us",
        "fast_title": "⚡ Fast", "fast_desc": "Delivery within 24 hours",
        "secure_title": "🔒 Secure", "secure_desc": "Your packages are safe with us",
        "free_title": "🎁 Free Delivery", "free_desc": "1 in 3 deliveries free",
        "loyalty_points": "Loyalty Points", "points_balance": "Your Points Balance",
        "redeem_points": "Redeem Points", "delivery_notes": "Delivery Notes",
        "gate_code": "Gate Code", "building_number": "Building Number",
        "order_id": "Order ID", "order_status": "Status",
        "estimated_delivery": "Estimated Delivery", "track_order": "Track Your Order",
        "rate_delivery": "Rate Your Delivery", "leave_review": "Leave a Review",
        "submit_feedback": "Submit Feedback", "promo_code": "Promo Code",
        "apply_promo": "Apply", "promo_applied": "Promo Code Applied!",
        "invalid_promo": "Invalid Promo Code", "payment_method": "Payment Method",
        "cash_on_delivery": "Cash on Delivery", "bank_transfer": "Bank Transfer",
        "zain_cash": "Zain Cash", "asia_hawala": "Asia Hawala",
        "whatsapp_question": "💬 Ask on WhatsApp", "emergency_call": "🚨 Emergency",
        "police": "Police", "ambulance": "Ambulance",
        "zone_north": "North Zone", "zone_south": "South Zone",
        "zone_east": "East Zone", "zone_west": "West Zone",
        "currency_iqd": "IQD", "currency_usd": "USD",
        "reminder": "Reminder", "delivery_reminder": "Your delivery will arrive in 1 hour",
        "eid_offer": "🎊 Eid Special Offer",
        "ramadan_offer": "🌙 Ramadan Special",
        "nowruz_offer": "🌸 Nowruz Greetings",
        "access_account": "Sign in to access your account",
        "golden_rules": "Golden Rules",
        "rule1": "1 out of 3 deliveries is free - automatically applied!",
        "rule2": "No illegal items - we comply with all local laws",
        "rule3": "Fast Kirkuk wide service - all neighborhoods covered",
        "rule4": "Delivery within 24 hours of order confirmation",
        "rule5": "Cash on delivery only",
        "rule6": "Free delivery promotion applies to orders over 3000 IQD",
        "rule7": "Customer must be present at time of delivery",
        "signed_in_as": "Logged in as"
    },
    "کوردی 🇭🇺": {
        "dir": "rtl", "align": "right",
        "title": "گۆڵدن دلیڤەری پرۆ",
        "desc": "بەرزترین کوالێتی گەیاندن لە کەرکوک. خێرا، پارێزراو، و هەمیشە لە کاتی خۆیدا.",
        "nav_home": "سەرەکی", "nav_order": "داواکردن", "nav_track": "شوێنکەوتن",
        "nav_offers": "پێشکەشکراوەکان", "nav_profile": "هەژمار", "nav_terms": "یاساکان",
        "nav_support": "پاڵپشتی",
        "customer_name": "ناوی کڕیار", "shop_name": "ناوی دوکان",
        "shop_addr": "ناونیشانی دوکان", "phone": "ژمارەی مۆبایل",
        "area": "گەڕەک", "full_addr": "وردەکاری ناونیشان",
        "price": "نرخ (د.ع)", "submit": "تۆمارکردن",
        "free_info": "🎁 دیاری: یەکێک لە هەر ٣ گەیاندنێک بە خۆڕاییە!",
        "free_success": "🎊 پیرۆزە! ئەم گەیاندنەت بە ٠ دینارە!",
        "google_btn": "چوونەژوورەوە بە Google", "logout": "چوونەدەرەوە",
        "settings": "ڕێکخستنەکان", "admin_pass_label": "وشەی نهێنی ئەدمین",
        "admin_error": "❌ وشەی نهێنی هەڵەیە", "mgmt_links": "بەستەرەکانی بەڕێوەبردن",
        "terms_title": "📜 یاسا و ڕێساکان", "contact_us": "پەیوەندیمان پێوە بکە",
        "call_us": "پەیوەندیمان پێوە بکە", "whatsapp_us": "واتسئاپ",
        "email_us": "ئیمەیڵ", "visit_us": "سەردانمان بکە",
        "fast_title": "⚡ خێرا", "fast_desc": "گەیاندن لە ماوەی ٢٤ کاتژمێردا",
        "secure_title": "🔒 پارێزراو", "secure_desc": "پاکەتەکانت سەلامەتن لە لای ئێمە",
        "free_title": "🎁 گەیاندنی خۆڕایی", "free_desc": "یەکێک لە هەر ٣ گەیاندنێک بە خۆڕاییە",
        "loyalty_points": "خاڵی دڵسۆزی", "points_balance": "ڕێژەی خاڵەکانت",
        "redeem_points": "بەکارهێنانی خاڵەکان", "delivery_notes": "تێبینی گەیاندن",
        "gate_code": "کۆدی دەروازە", "building_number": "ژمارەی باڵەخانە",
        "order_id": "ژمارەی داواکاری", "order_status": "دۆخ",
        "estimated_delivery": "گەیاندنی چاوەڕوانکراو", "track_order": "شوێنکەوتنی داواکاری",
        "rate_delivery": "هەڵسەنگاندنی گەیاندن", "leave_review": "بیروبۆچوون بنووسە",
        "submit_feedback": "ناردنی بیروبۆچوون", "promo_code": "کۆدی پڕۆمۆ",
        "apply_promo": "جێبەجێکردن", "promo_applied": "کۆدی پڕۆمۆ جێبەجێ کرا!",
        "invalid_promo": "کۆدی پڕۆمۆ نادروستە", "payment_method": "شێوازی پارەدان",
        "cash_on_delivery": "پارەدان لە کاتی گەیاندن", "bank_transfer": "گواستنەوەی بانکی",
        "zain_cash": "زەین کاش", "asia_hawala": "ئاسیا حەوالە",
        "whatsapp_question": "💬 پرسیار لە واتسئاپ", "emergency_call": "🚨 فریاکەوتن",
        "police": "پۆلیس", "ambulance": "فریاکەوتن",
        "zone_north": "ناوچەی باکوور", "zone_south": "ناوچەی باشوور",
        "zone_east": "ناوچەی ڕۆژهەڵات", "zone_west": "ناوچەی ڕۆژئاوا",
        "currency_iqd": "دینار", "currency_usd": "دۆلار",
        "reminder": "بیرخستنەوە", "delivery_reminder": "گەیاندنەکەت لە ماوەی ١ کاتژمێری دیکەدا دەگات",
        "eid_offer": "🎊 پێشکەشکردنی جەژن",
        "ramadan_offer": "🌙 پێشکەشکردنی ڕەمەزان",
        "nowruz_offer": "🌸 پیرۆزبایی نەورۆز",
        "access_account": "بچۆ ژوورەوە بۆ هەژمارەکەت",
        "golden_rules": "ڕێسا زێڕینەکان",
        "rule1": "یەکێک لە هەر ٣ گەیاندنێک بە خۆڕاییە",
        "rule2": "هیچ کاڵایەکی نایاسایی نییە",
        "rule3": "خزمەتگوزاری خێرا لە سەرانسەری کەرکوک",
        "rule4": "گەیاندن لە ماوەی ٢٤ کاتژمێردا",
        "rule5": "تەنها پارەدان لە کاتی گەیاندن",
        "rule6": "پڕۆمۆشنی خۆڕایی بۆ داواکاری ٣٠٠٠ دینار",
        "rule7": "کڕیار دەبێت لە کاتی گەیاندن ئامادە بێت",
        "signed_in_as": "چوویتە ژوورەوە وەک"
    },
    "العربية 🇮🇶": {
        "dir": "rtl", "align": "right",
        "title": "جولدن دليفري برو",
        "desc": "المعيار الذهبي للخدمات اللوجستية في كركوك.",
        "nav_home": "الرئيسية", "nav_order": "طلب", "nav_track": "تتبع",
        "nav_offers": "العروض", "nav_profile": "الحساب", "nav_terms": "الشروط",
        "nav_support": "الدعم",
        "customer_name": "اسم الزبون", "shop_name": "اسم المحل",
        "shop_addr": "عنوان المحل", "phone": "رقم الهاتف",
        "area": "المنطقة", "full_addr": "تفاصيل العنوان",
        "price": "السعر (د.ع)", "submit": "تأكيد الطلب",
        "free_info": "🎁 عرض: واحدة من كل ٣ توصيلات مجانية!",
        "free_success": "🎊 مبروك! هذه الطلبية بـ ٠ دينار!",
        "google_btn": "الدخول بواسطة Google", "logout": "خروج",
        "settings": "الإعدادات", "admin_pass_label": "كلمة مرور المسؤول",
        "admin_error": "❌ كلمة المرور غير صحيحة", "mgmt_links": "روابط الإدارة",
        "terms_title": "📜 الشروط والقواعد", "contact_us": "اتصل بنا",
        "call_us": "اتصل", "whatsapp_us": "واتساب",
        "email_us": "البريد الإلكتروني", "visit_us": "زورنا",
        "fast_title": "⚡ سريع", "fast_desc": "التوصيل خلال ٢٤ ساعة",
        "secure_title": "🔒 آمن", "secure_desc": "طرودك آمنة معنا",
        "free_title": "🎁 توصيل مجاني", "free_desc": "واحدة من كل ٣ توصيلات مجانية",
        "loyalty_points": "نقاط الولاء", "points_balance": "رصيد نقاطك",
        "redeem_points": "استبدال النقاط", "delivery_notes": "ملاحظات التوصيل",
        "gate_code": "رمز البوابة", "building_number": "رقم المبنى",
        "order_id": "رقم الطلب", "order_status": "الحالة",
        "estimated_delivery": "التوصيل المتوقع", "track_order": "تتبع طلبك",
        "rate_delivery": "قيم توصيلتك", "leave_review": "اترك تعليقاً",
        "submit_feedback": "إرسال التقييم", "promo_code": "كود العرض",
        "apply_promo": "تطبيق", "promo_applied": "تم تطبيق كود العرض!",
        "invalid_promo": "كود العرض غير صالح", "payment_method": "طريقة الدفع",
        "cash_on_delivery": "الدفع عند الاستلام", "bank_transfer": "تحويل بنكي",
        "zain_cash": "زين كاش", "asia_hawala": "آسيا حوالة",
        "whatsapp_question": "💬 اسأل على واتساب", "emergency_call": "🚨 طوارئ",
        "police": "شرطة", "ambulance": "إسعاف",
        "zone_north": "المنطقة الشمالية", "zone_south": "المنطقة الجنوبية",
        "zone_east": "المنطقة الشرقية", "zone_west": "المنطقة الغربية",
        "currency_iqd": "دينار", "currency_usd": "دولار",
        "reminder": "تذكير", "delivery_reminder": "سيصل طلبك خلال ساعة",
        "eid_offer": "🎊 عرض العيد",
        "ramadan_offer": "🌙 عرض رمضان",
        "nowruz_offer": "🌸 تهاني نوروز",
        "access_account": "سجل الدخول للوصول إلى حسابك",
        "golden_rules": "القواعد الذهبية",
        "rule1": "واحدة من كل ٣ توصيلات مجانية",
        "rule2": "لا يوجد عناصر غير قانونية",
        "rule3": "خدمة سريعة في جميع أنحاء كركوك",
        "rule4": "التوصيل خلال ٢٤ ساعة",
        "rule5": "الدفع عند الاستلام فقط",
        "rule6": "عرض التوصيل المجاني للطلبات فوق ٣٠٠٠ دينار",
        "rule7": "يجب أن يكون الزبون حاضراً وقت التوصيل",
        "signed_in_as": "تم تسجيل الدخول باسم"
    }
}

# --- 7. DATA FILES ---
ORDERS_FILE = "orders.csv"
DRIVERS_FILE = "drivers.csv"
CUSTOMERS_FILE = "customers.csv"
FEEDBACK_FILE = "feedback.csv"
PROMO_CODES_FILE = "promos.json"
OFFLINE_ORDERS_FILE = "offline_orders.json"

# --- 8. DATA FUNCTIONS ---
def load_orders():
    if os.path.exists(ORDERS_FILE):
        return pd.read_csv(ORDERS_FILE, dtype={"phone": str, "order_id": str})
    return pd.DataFrame(columns=["order_id", "date", "customer", "shop", "phone", "area", 
                                  "address", "shop_addr", "price", "status", "user_email", 
                                  "driver_id", "payment_method", "delivery_notes", "promo_code",
                                  "estimated_delivery", "actual_delivery", "rating", "review",
                                  "zone", "currency", "reminder_sent"])

def save_orders(df):
    df.to_csv(ORDERS_FILE, index=False)

def load_drivers():
    if os.path.exists(DRIVERS_FILE):
        return pd.read_csv(DRIVERS_FILE, dtype={"phone": str})
    return pd.DataFrame(columns=["driver_id", "name", "phone", "status", "zone", "join_date", "total_deliveries", "rating", "language"])

def save_drivers(df):
    df.to_csv(DRIVERS_FILE, index=False)

def load_customers():
    if os.path.exists(CUSTOMERS_FILE):
        return pd.read_csv(CUSTOMERS_FILE, dtype={"phone": str})
    return pd.DataFrame(columns=["customer_id", "name", "phone", "email", "join_date", 
                                  "total_orders", "loyalty_points", "favorite_zone", "total_spent",
                                  "language", "notification_preferences"])

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
        "KIRKUK10": {"discount": 10, "type": "percentage", "min_order": 0, "expiry": "2025-12-31"},
        "EID2025": {"discount": 25, "type": "percentage", "min_order": 10000, "expiry": "2025-07-15"},
        "RAMADAN": {"discount": 20, "type": "percentage", "min_order": 5000, "expiry": "2025-04-20"},
        "NOWRUZ": {"discount": 30, "type": "percentage", "min_order": 15000, "expiry": "2025-03-25"}
    }

def save_promos(promos):
    with open(PROMO_CODES_FILE, 'w') as f:
        json.dump(promos, f, indent=4)

def load_offline_orders():
    if os.path.exists(OFFLINE_ORDERS_FILE):
        with open(OFFLINE_ORDERS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_offline_orders(orders):
    with open(OFFLINE_ORDERS_FILE, 'w') as f:
        json.dump(orders, f, indent=4)

# --- 9. HELPER FUNCTIONS ---
def generate_order_id():
    return f"GD-{datetime.now().strftime('%Y%m')}-{str(uuid.uuid4())[:8].upper()}"

def calculate_loyalty_points(price):
    return int(price / 1000)

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

def send_whatsapp_message(phone, message):
    encoded_message = message.replace(' ', '%20').replace('،', ',').replace('؟', '')
    return f"https://wa.me/{phone}?text={encoded_message}"

def send_sms_reminder(phone, order_id):
    L = languages[st.session_state.lang_choice]
    message = f"{L['delivery_reminder']} - {L['order_id']}: {order_id}"
    return True

def get_order_status_emoji(status):
    emojis = {
        "Pending": "⏳", "Picked Up": "📦", "In Transit": "🚚",
        "Out for Delivery": "🚪", "Delivered": "✅", "Cancelled": "❌"
    }
    return emojis.get(status, "📦")

def calculate_estimated_delivery(zone):
    times = {
        "باکوور": 20, "باشوور": 24, "ڕۆژهەڵات": 18, "ڕۆژئاوا": 22
    }
    hours = times.get(zone, 24)
    return (datetime.now() + timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M")

def get_zone_from_area(area):
    for zone, areas in NEIGHBORHOOD_ZONES.items():
        if any(a in area for a in areas):
            return zone
    return "ناوەند"

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
            "favorite_zone": "",
            "total_spent": price,
            "language": st.session_state.lang_choice,
            "notification_preferences": json.dumps(st.session_state.notification_preferences)
        }])
        customers_df = pd.concat([customers_df, new_customer], ignore_index=True)
    save_customers(customers_df)

def convert_currency(price, from_currency, to_currency):
    if from_currency == to_currency:
        return price
    usd_to_iqd = 1460
    if from_currency == 'USD' and to_currency == 'IQD':
        return price * usd_to_iqd
    elif from_currency == 'IQD' and to_currency == 'USD':
        return price / usd_to_iqd
    return price

def get_holiday_offer():
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

# --- 10. TOP BAR ---
L = languages[st.session_state.lang_choice]

top_col1, top_col2, top_col3, top_col4 = st.columns([2, 1, 1, 1])
with top_col1:
    st.markdown(f"<h2 style='color:#D4AF37; margin:0;'>{L['title']}</h2>", unsafe_allow_html=True)
with top_col2:
    lang_options = list(languages.keys())
    current_lang_index = lang_options.index(st.session_state.lang_choice)
    selected_lang = st.selectbox("🌐", lang_options, index=current_lang_index, label_visibility="collapsed", key="lang_select")
    if selected_lang != st.session_state.lang_choice:
        st.session_state.lang_choice = selected_lang
        st.rerun()
with top_col3:
    theme_options = ["Light ☀️", "Dark 🌙"]
    current_theme_index = 0 if st.session_state.theme_choice == "Light ☀️" else 1
    selected_theme = st.selectbox("🎨", theme_options, index=current_theme_index, label_visibility="collapsed", key="theme_select")
    if selected_theme != st.session_state.theme_choice:
        st.session_state.theme_choice = selected_theme
        st.rerun()
with top_col4:
    currency_options = ["IQD", "USD"]
    current_currency_index = 0 if st.session_state.currency == "IQD" else 1
    selected_currency = st.selectbox("💰", currency_options, index=current_currency_index, label_visibility="collapsed", key="currency_select")
    if selected_currency != st.session_state.currency:
        st.session_state.currency = selected_currency
        st.rerun()

L = languages[st.session_state.lang_choice]

# --- 11. CSS STYLING ---
is_dark = st.session_state.theme_choice == "Dark 🌙"

if is_dark:
    main_bg = "#0a0c10"
    card_bg = "#1e2329"
    text_color = "#ffffff"
    accent = "#D4AF37"
    input_bg = "#2d333d"
    border_color = "#3a404c"
else:
    main_bg = "#f5f7fa"
    card_bg = "#ffffff"
    text_color = "#1a1a2e"
    accent = "#D4AF37"
    input_bg = "#ffffff"
    border_color = "#e0e0e0"

st.markdown(f"""
<style>
    [data-testid="stSidebar"] {{ display: none; }}
    html, body, [data-testid="stAppViewContainer"] {{ background-color: {main_bg} !important; color: {text_color} !important; }}
    h1, h2, h3, h4, h5, h6, p, span, div, label {{ color: {text_color} !important; }}
    input, textarea, .stTextInput input, .stTextArea textarea {{ background-color: {input_bg} !important; color: {text_color} !important; border: 1px solid {border_color} !important; }}
    .stSelectbox div[data-baseweb="select"] {{ background-color: {input_bg} !important; border-color: {border_color} !important; }}
    div[data-baseweb="menu"] {{ background-color: {input_bg} !important; }}
    .stForm {{ background-color: {card_bg} !important; border: 1px solid {accent}40 !important; border-radius: 20px !important; padding: 30px !important; }}
    .glass-card {{ background-color: {card_bg} !important; border-radius: 20px !important; padding: 25px !important; border: 1px solid {accent}30 !important; margin-bottom: 20px !important; }}
    .brand-header {{ background: linear-gradient(135deg, #D4AF37 0%, #8A6D3B 100%); padding: 30px; border-radius: 0 0 30px 30px; text-align: center; margin-bottom: 20px; }}
    .brand-header h1, .brand-header p {{ color: white !important; }}
    .stButton button {{ background-color: {accent} !important; color: {text_color if is_dark else '#000000'} !important; border: none !important; font-weight: bold !important; border-radius: 10px !important; padding: 10px 20px !important; transition: all 0.3s !important; }}
    .stButton button:hover {{ background-color: {accent}dd !important; transform: translateY(-2px) !important; }}
    .card-title {{ color: {accent} !important; font-size: 1.5rem !important; }}
    .phone-number {{ color: {accent} !important; font-weight: bold; margin: 0 10px; }}
    .emergency-button {{ background-color: #ff4444 !important; color: white !important; }}
    .whatsapp-button {{ background-color: #25D366 !important; color: white !important; }}
    [dir="{L['dir']}"] {{ text-align: {L['align']} !important; }}
</style>
""", unsafe_allow_html=True)

# --- 12. NAVIGATION MENU (بێ دوگمەی فریاکەوتن لە سەرەکی) ---
selected = option_menu(
    menu_title=None,
    options=[L['nav_home'], L['nav_order'], L['nav_track'], L['nav_offers'], 
             L['nav_profile'], L['nav_terms'], L['nav_support']],
    icons=['house-door', 'box', 'geo-alt', 'gift', 'person', 'file-text', 'headset'],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "transparent", "max-width": "1200px", "margin": "0 auto", "display": "flex", "justify-content": "center", "gap": "5px"},
        "icon": {"color": accent, "font-size": "16px"},
        "nav-link": {"font-size": "14px", "text-align": "center", "margin": "0px 2px", "padding": "8px 12px", "border-radius": "30px", "color": text_color, "background-color": card_bg},
        "nav-link:hover": {"background-color": f"{accent}20", "transform": "translateY(-2px)"},
        "nav-link-selected": {"background-color": accent, "color": "black", "font-weight": "bold"},
    }
)

page_mapping = {
    L['nav_home']: "home", L['nav_order']: "order", L['nav_track']: "track",
    L['nav_offers']: "offers", L['nav_profile']: "profile", L['nav_terms']: "terms",
    L['nav_support']: "support"
}
st.session_state.page = page_mapping.get(selected, "home")

# --- 13. HOME PAGE ---
if st.session_state.page == "home":
    holiday_offer = get_holiday_offer()
    if holiday_offer:
        if "RAMADAN" in holiday_offer:
            st.success(f"🌙 {L['ramadan_offer']}")
        elif "NOWRUZ" in holiday_offer:
            st.success(f"🌸 {L['nowruz_offer']}")
        elif "EID" in holiday_offer:
            st.success(f"🎊 {L['eid_offer']}")
    
    st.markdown(f'<div class="brand-header"><h1>{L["title"]}</h1><p>{L["desc"]}</p></div>', unsafe_allow_html=True)
    
    orders_df = load_orders()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total_orders = len(orders_df)
        st.metric("📦 کۆی داواکاری", f"{total_orders:,}")
    with col2:
        delivered = len(orders_df[orders_df['status'] == 'Delivered'])
        st.metric("✅ گەیاندراو", f"{delivered:,}")
    with col3:
        free_deliveries = len(orders_df[orders_df['price'] == 0])
        st.metric("🎁 خۆڕایی", f"{free_deliveries:,}")
    with col4:
        if len(orders_df) > 0:
            avg_price = int(orders_df['price'].mean())
            if st.session_state.currency == 'USD':
                avg_price = convert_currency(avg_price, 'IQD', 'USD')
                st.metric("💰 تێکڕا", f"${avg_price:.2f}")
            else:
                st.metric("💰 تێکڕا", f"{avg_price:,} {L['currency_iqd']}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="glass-card"><h3 class="card-title">{L["fast_title"]}</h3><p>{L["fast_desc"]}</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="glass-card"><h3 class="card-title">{L["secure_title"]}</h3><p>{L["secure_desc"]}</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="glass-card"><h3 class="card-title">{L["free_title"]}</h3><p>{L["free_desc"]}</p></div>', unsafe_allow_html=True)
    
    st.markdown(f"<h3 style='color:{accent};'>🗺️ {L['zone_north']} / {L['zone_south']} / {L['zone_east']} / {L['zone_west']}</h3>", unsafe_allow_html=True)
    zone_cols = st.columns(4)
    for idx, (zone, areas) in enumerate(NEIGHBORHOOD_ZONES.items()):
        with zone_cols[idx]:
            # ڕاستکردنەوەی کێشەکە - بەکارهێنانی ناوی ڕاستەوخۆ
            if zone == "باکوور":
                zone_name = L['zone_north']
            elif zone == "باشوور":
                zone_name = L['zone_south']
            elif zone == "ڕۆژهەڵات":
                zone_name = L['zone_east']
            elif zone == "ڕۆژئاوا":
                zone_name = L['zone_west']
            else:
                zone_name = zone
            st.markdown(f'<div class="glass-card"><h4 style="color:{accent};">{zone_name}</h4><p>{len(areas)} گەڕەک</p></div>', unsafe_allow_html=True)
    
    if not orders_df.empty:
        st.markdown(f"<h3 style='color:{accent};'>📋 دواین داواکارییەکان</h3>", unsafe_allow_html=True)
        recent = orders_df.tail(5)[['order_id', 'customer', 'area', 'price', 'status']].copy()
        if st.session_state.currency == 'USD':
            recent['price'] = recent['price'].apply(lambda x: f"${convert_currency(x, 'IQD', 'USD'):.2f}")
        else:
            recent['price'] = recent['price'].apply(lambda x: f"{x:,} {L['currency_iqd']}")
        st.dataframe(recent, use_container_width=True)

# --- 14. ORDER PAGE ---
elif st.session_state.page == "order":
    st.markdown(f"<h2 style='color:{accent}; text-align:center;'>{L['nav_order']}</h2>", unsafe_allow_html=True)
    
    orders_df = load_orders()
    promos = load_promos()
    
    st.info(L["free_info"])
    
    col1, col2 = st.columns(2)
    with col1:
        customer_name = st.text_input(L['customer_name'])
        phone_input = st.text_input(L['phone'], placeholder="07xx xxx xxxx")
        shop_name = st.text_input(L['shop_name'])
    
    with col2:
        payment_method = st.selectbox(L['payment_method'], 
            [L['cash_on_delivery'], L['bank_transfer'], L['zain_cash'], L['asia_hawala']])
        delivery_notes = st.text_area(L['delivery_notes'], placeholder=f"{L['gate_code']}, {L['building_number']}")
    
    is_free = False
    if phone_input:
        customer_orders = orders_df[orders_df['phone'] == phone_input]
        order_count = len(customer_orders)
        is_free = (order_count + 1) % 3 == 0
        if is_free:
            st.success(L["free_success"])
    
    col1, col2 = st.columns(2)
    with col1:
        area = st.selectbox(L['area'], ["-- هەڵبژاردن --"] + KIRKUK_AREAS)
        zone = get_zone_from_area(area) if area != "-- هەڵبژاردن --" else "ناوەند"
        full_addr = st.text_area(L['full_addr'])
    with col2:
        shop_addr = st.text_input(L['shop_addr'])
        
        base_price = 0 if is_free else 3000
        if st.session_state.currency == 'USD':
            base_price = convert_currency(base_price, 'IQD', 'USD')
            price = st.number_input(L['price'], value=float(base_price), min_value=0.0, step=0.5, format="%.2f")
        else:
            price = st.number_input(L['price'], value=base_price, min_value=0, step=500)
        
        promo_code = st.text_input(L['promo_code'])
        if promo_code:
            price_iqd = price if st.session_state.currency == 'IQD' else convert_currency(price, 'USD', 'IQD')
            valid, discount, promo = validate_promo_code(promo_code.upper(), price_iqd, promos)
            if valid:
                if st.session_state.currency == 'IQD':
                    price = price_iqd - discount
                else:
                    price = convert_currency(price_iqd - discount, 'IQD', 'USD')
                st.success(f"{L['promo_applied']} ({discount:,.0f} IQD)")
            else:
                st.warning(L['invalid_promo'])
    
    if phone_input:
        message = f"سڵاو، داواکارییەکی نوێم هەیە بۆ {area}"
        whatsapp_link = send_whatsapp_message(COMPANY_PHONES[0].replace('0', '964', 1), message)
        st.markdown(f'<a href="{whatsapp_link}" target="_blank"><button style="background-color:#25D366; color:white; padding:10px; border-radius:10px; width:100%; border:none; cursor:pointer;">💬 {L["whatsapp_question"]}</button></a>', unsafe_allow_html=True)
    
    if st.button(L['submit'], use_container_width=True):
        if customer_name and phone_input and area and area != "-- هەڵبژاردن --":
            order_id = generate_order_id()
            estimated_time = calculate_estimated_delivery(zone)
            
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
                "driver_id": None,
                "payment_method": payment_method,
                "delivery_notes": delivery_notes,
                "promo_code": promo_code if promo_code else None,
                "estimated_delivery": estimated_time,
                "actual_delivery": None,
                "rating": None,
                "review": None,
                "zone": zone,
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
                st.info("📴 داواکاری پاشەکەوت کرا، کاتێک ئینتەرنێت هات دەنێردرێت")
            else:
                orders_df = pd.concat([orders_df, new_order], ignore_index=True)
                save_orders(orders_df)
                update_customer_loyalty(phone_input, int(price_iqd))
                st.success(f"✅ {L['submit']}! {L['order_id']}: {order_id}")
                st.balloons()
                st.session_state.current_order_id = order_id
        else:
            st.error("تکایە هەموو خانەکان پڕ بکەرەوە")

# --- 15. TRACK PAGE ---
elif st.session_state.page == "track":
    st.markdown(f"<h2 style='color:{accent}; text-align:center;'>{L['track_order']}</h2>", unsafe_allow_html=True)
    
    orders_df = load_orders()
    
    track_method = st.radio("", ["📱 بە ژمارە مۆبایل", "🔢 بە ژمارەی داواکاری"], horizontal=True)
    
    if "بە ژمارە مۆبایل" in track_method:
        phone = st.text_input(L['phone'])
        if phone:
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
                        
                        if order['status'] == 'Out for Delivery' and not order['reminder_sent']:
                            if st.button(f"🔔 {L['reminder']}", key=f"remind_{order['order_id']}"):
                                send_sms_reminder(phone, order['order_id'])
                                orders_df.loc[orders_df['order_id'] == order['order_id'], 'reminder_sent'] = True
                                save_orders(orders_df)
                                st.success(L['reminder'])
            else:
                st.info("هیچ داواکارییەک نەدۆزرایەوە")
    
    else:
        order_id = st.text_input(L['order_id'])
        if order_id:
            order = orders_df[orders_df['order_id'] == order_id]
            if not order.empty:
                order = order.iloc[0]
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f'<div class="glass-card"><h4>{L["order_id"]}: {order["order_id"]}</h4><p>{L["customer_name"]}: {order["customer"]}</p><p>{L["area"]}: {order["area"]}</p>', unsafe_allow_html=True)
                    if st.session_state.currency == 'USD':
                        price_display = convert_currency(order['price'], 'IQD', 'USD')
                        st.markdown(f'<p>{L["price"]}: ${price_display:.2f}</p></div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<p>{L["price"]}: {order["price"]:,} {L["currency_iqd"]}</p></div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f'<div class="glass-card"><h4>{L["order_status"]}</h4><p style="font-size:2rem;">{get_order_status_emoji(order["status"])}</p><p>{order["status"]}</p><p>{L["estimated_delivery"]}: {order["estimated_delivery"]}</p></div>', unsafe_allow_html=True)
                
                if order['status'] == 'Delivered' and pd.isna(order['rating']):
                    st.markdown(f"<h4 style='color:{accent};'>{L['rate_delivery']}</h4>", unsafe_allow_html=True)
                    rating = st.slider("", 1, 5, 5)
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
                        
                        st.success("سوپاس بۆ هەڵسەنگاندنەکەت!")
            else:
                st.warning("داواکاری نەدۆزرایەوە")

# --- 16. OFFERS PAGE ---
elif st.session_state.page == "offers":
    st.markdown(f"<h2 style='color:{accent}; text-align:center;'>{L['nav_offers']}</h2>", unsafe_allow_html=True)
    
    promos = load_promos()
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="glass-card"><h4 style="color:{accent};">🎊 {L["free_info"]}</h4><p>{L["free_desc"]}</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="glass-card"><h4 style="color:{accent};">💎 {L["loyalty_points"]}</h4><p>1000 دینار = ١ خاڵ</p><p>١٠٠ خاڵ = ٥٠٠٠ دینار</p><p>٢٠٠ خاڵ = ١٢٠٠٠ دینار</p><p>٥٠٠ خاڵ = ٣٥٠٠٠ دینار</p></div>', unsafe_allow_html=True)
    
    st.markdown(f"<h3 style='color:{accent};'>🏷️ {L['promo_code']}</h3>", unsafe_allow_html=True)
    promo_cols = st.columns(3)
    for idx, (code, details) in enumerate(promos.items()):
        with promo_cols[idx % 3]:
            discount_text = f"{details['discount']}%" if details['type'] == 'percentage' else f"{details['discount']:,} IQD"
            min_order = f"کەمترین: {details['min_order']:,} IQD" if details['min_order'] > 0 else "بێ سنوور"
            st.markdown(f'<div class="glass-card" style="text-align:center;"><h4 style="color:{accent};">{code}</h4><p style="font-size:1.2rem;">{discount_text} دابەزین</p><p>{min_order}</p><p>بەسەرچوون: {details["expiry"]}</p></div>', unsafe_allow_html=True)

# --- 17. PROFILE PAGE ---
elif st.session_state.page == "profile":
    st.markdown(f"<h2 style='color:{accent}; text-align:center;'>{L['nav_profile']}</h2>", unsafe_allow_html=True)
    
    if st.session_state.user_email is None:
        tab1, tab2 = st.tabs(["🔑 چوونەژوورەوە", "📝 تۆمارکردن"])
        
        with tab1:
            st.markdown(f'<div class="glass-card"><p>{L["access_account"]}</p></div>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                if st.button("👤 کڕیار", use_container_width=True):
                    st.session_state.user_email = "customer@goldendelivery.iq"
                    st.session_state.user_role = "customer"
                    st.session_state.user_name = "Customer"
                    st.session_state.user_phone = "07701234567"
                    st.rerun()
            with col2:
                if st.button("🚚 شۆفێر", use_container_width=True):
                    st.session_state.user_email = "driver@goldendelivery.iq"
                    st.session_state.user_role = "driver"
                    st.session_state.user_name = "Driver"
                    st.session_state.user_phone = "07707654321"
                    st.rerun()
        
        with tab2:
            with st.form("register_form"):
                name = st.text_input("ناوی تەواو")
                email = st.text_input("ئیمەیڵ")
                phone = st.text_input("ژمارە مۆبایل", placeholder="07xx xxx xxxx")
                area = st.selectbox("ناوچە", KIRKUK_AREAS[:10])
                if st.form_submit_button("تۆمارکردن"):
                    if name and email and phone:
                        st.session_state.user_email = email
                        st.session_state.user_name = name
                        st.session_state.user_phone = phone
                        st.session_state.user_role = "customer"
                        st.success("تۆمارکردن سەرکەوتوو بوو!")
                        st.rerun()
                    else:
                        st.error("تکایە هەموو خانەکان پڕ بکەرەوە")
    else:
        tabs = st.tabs(["👤 پڕۆفایل", "📦 داواکارییەکان", "⭐ خاڵەکان", "⚙️ ڕێکخستنەکان"])
        
        with tabs[0]:
            st.markdown(f'<div class="glass-card"><h4 style="color:{accent};">{L["signed_in_as"]}</h4><p>ناو: {st.session_state.user_name}</p><p>ئیمەیڵ: {st.session_state.user_email}</p><p>ڕۆڵ: {st.session_state.user_role}</p></div>', unsafe_allow_html=True)
            
            if st.session_state.user_phone:
                customers_df = load_customers()
                customer = customers_df[customers_df['phone'] == st.session_state.user_phone]
                if not customer.empty:
                    data = customer.iloc[0]
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("کۆی داواکاری", int(data['total_orders']))
                    with col2:
                        st.metric(L['loyalty_points'], int(data['loyalty_points']))
                    with col3:
                        spent = data['total_spent']
                        if st.session_state.currency == 'USD':
                            spent = convert_currency(spent, 'IQD', 'USD')
                            st.metric("کۆی خەرجی", f"${spent:.2f}")
                        else:
                            st.metric("کۆی خەرجی", f"{spent:,} {L['currency_iqd']}")
        
        with tabs[1]:
            orders_df = load_orders()
            if st.session_state.user_phone:
                user_orders = orders_df[orders_df['phone'] == st.session_state.user_phone]
                if not user_orders.empty:
                    display_orders = user_orders[['order_id', 'date', 'area', 'price', 'status']].copy()
                    if st.session_state.currency == 'USD':
                        display_orders['price'] = display_orders['price'].apply(lambda x: f"${convert_currency(x, 'IQD', 'USD'):.2f}")
                    else:
                        display_orders['price'] = display_orders['price'].apply(lambda x: f"{x:,} {L['currency_iqd']}")
                    st.dataframe(display_orders, use_container_width=True)
                else:
                    st.info("هیچ داواکارییەک نییە")
        
        with tabs[2]:
            customers_df = load_customers()
            if st.session_state.user_phone:
                customer = customers_df[customers_df['phone'] == st.session_state.user_phone]
                if not customer.empty:
                    points = int(customer.iloc[0]['loyalty_points'])
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f'<div class="glass-card" style="text-align:center;"><h1 style="color:{accent}; font-size:3rem;">{points}</h1><p>{L["points_balance"]}</p></div>', unsafe_allow_html=True)
                    with col2:
                        st.markdown(f'<div class="glass-card"><h4 style="color:{accent};">{L["redeem_points"]}</h4><p>١٠٠ خاڵ = ٥٠٠٠ دینار</p><p>٢٠٠ خاڵ = ١٢٠٠٠ دینار</p><p>٥٠٠ خاڵ = ٣٥٠٠٠ دینار</p></div>', unsafe_allow_html=True)
                    
                    if points >= 100:
                        if st.button(f"{L['redeem_points']} 100 خاڵ"):
                            st.success("خاڵەکانت بەکارهێنران! ٥٠٠٠ دینار دابەزی")
        
        with tabs[3]:
            st.markdown(f'<div class="glass-card"><h4 style="color:{accent};">{L["settings"]}</h4></div>', unsafe_allow_html=True)
            sms_pref = st.checkbox("📱 پەیامی ئێس ئێم ئێس", value=True)
            email_pref = st.checkbox("📧 پەیامی ئیمەیڵ", value=True)
            whatsapp_pref = st.checkbox("💬 پەیامی واتسئاپ", value=True)
            
            st.session_state.notification_preferences = {
                'sms': sms_pref, 'email': email_pref, 'whatsapp': whatsapp_pref
            }
            
            if st.button(L["logout"]):
                for key in ['user_email', 'user_role', 'user_name', 'user_phone']:
                    st.session_state[key] = None
                st.rerun()
        
        # Admin section
        if not st.session_state.admin_authenticated:
            st.divider()
            st.warning(L["admin_pass_label"])
            pwd = st.text_input("وشەی نهێنی", type="password")
            if st.button("کردنەوە"):
                if pwd == "GoldenAdmin2026":
                    st.session_state.admin_authenticated = True
                    st.rerun()
                else:
                    st.error(L["admin_error"])
        else:
            st.divider()
            st.subheader(L["mgmt_links"])
            
            admin_tabs = st.tabs(["📊 داشبۆرد", "🚚 شۆفێران", "📦 داواکارییەکان", "📈 ئامار"])
            
            with admin_tabs[0]:
                orders_df = load_orders()
                customers_df = load_customers()
                drivers_df = load_drivers()
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("کۆی داواکاری", len(orders_df))
                with col2:
                    st.metric("کڕیاران", len(customers_df))
                with col3:
                    st.metric("شۆفێری چالاک", len(drivers_df[drivers_df['status'] == 'Available']))
                with col4:
                    revenue = orders_df['price'].sum()
                    if st.session_state.currency == 'USD':
                        revenue = convert_currency(revenue, 'IQD', 'USD')
                        st.metric("داهات", f"${revenue:,.2f}")
                    else:
                        st.metric("داهات", f"{revenue:,} {L['currency_iqd']}")
                
                st.subheader("دواین داواکارییەکان")
                st.dataframe(orders_df.tail(10), use_container_width=True)
            
            with admin_tabs[1]:
                drivers_df = load_drivers()
                with st.expander("➕ شۆفێری نوێ"):
                    with st.form("new_driver"):
                        col1, col2 = st.columns(2)
                        with col1:
                            name = st.text_input("ناوی شۆفێر")
                            phone = st.text_input("ژمارەی مۆبایل")
                        with col2:
                            zone = st.selectbox("ناوچە", list(NEIGHBORHOOD_ZONES.keys()))
                            status = st.selectbox("دۆخ", ["Available", "Busy", "Offline"])
                        if st.form_submit_button("زیادکردن"):
                            new_driver = pd.DataFrame([{
                                "driver_id": str(uuid.uuid4())[:8],
                                "name": name,
                                "phone": phone,
                                "status": status,
                                "zone": zone,
                                "join_date": datetime.now().strftime("%Y-%m-%d"),
                                "total_deliveries": 0,
                                "rating": 5.0,
                                "language": "کوردی"
                            }])
                            drivers_df = pd.concat([drivers_df, new_driver], ignore_index=True)
                            save_drivers(drivers_df)
                            st.success("زیادکرا!")
                            st.rerun()
                
                st.subheader("لیستی شۆفێران")
                st.dataframe(drivers_df, use_container_width=True)
            
            with admin_tabs[2]:
                orders_df = load_orders()
                drivers_df = load_drivers()
                
                status_filter = st.selectbox("پاڵاوتن بەپێی دۆخ", ["All", "Pending", "Picked Up", "In Transit", "Out for Delivery", "Delivered", "Cancelled"])
                
                if status_filter != "All":
                    filtered_orders = orders_df[orders_df['status'] == status_filter]
                else:
                    filtered_orders = orders_df
                
                for idx, order in filtered_orders.iterrows():
                    if pd.isna(order['driver_id']) and order['status'] != 'Delivered':
                        with st.expander(f"📦 {order['order_id']} - {order['customer']} - {order['area']}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**نرخ:** {order['price']:,} IQD")
                                st.write(f"**شوێن:** {order['area']}")
                            with col2:
                                available_drivers = drivers_df[drivers_df['status'] == 'Available']
                                if not available_drivers.empty:
                                    driver_choice = st.selectbox(f"دیاریکردنی شۆفێر", 
                                                                available_drivers['name'].tolist(),
                                                                key=f"driver_{order['order_id']}")
                                    if st.button(f"دیاریکردن", key=f"assign_{order['order_id']}"):
                                        driver_id = available_drivers[available_drivers['name'] == driver_choice].iloc[0]['driver_id']
                                        orders_df.loc[orders_df['order_id'] == order['order_id'], 'driver_id'] = driver_id
                                        orders_df.loc[orders_df['order_id'] == order['order_id'], 'status'] = 'Picked Up'
                                        save_orders(orders_df)
                                        
                                        drivers_df.loc[drivers_df['driver_id'] == driver_id, 'status'] = 'Busy'
                                        save_drivers(drivers_df)
                                        
                                        st.success(f"شۆفێر {driver_choice} دیاری کرا!")
                                        st.rerun()
                                else:
                                    st.warning("شۆفێری بەردەست نییە")
                
                st.subheader("هەموو داواکارییەکان")
                st.dataframe(filtered_orders, use_container_width=True)
            
            with admin_tabs[3]:
                orders_df = load_orders()
                
                if not orders_df.empty:
                    zone_stats = orders_df.groupby('zone').size().reset_index(name='count')
                    fig = px.bar(zone_stats, x='zone', y='count', title='داواکاری بەپێی ناوچە')
                    st.plotly_chart(fig, use_container_width=True)
                    
                    orders_df['date'] = pd.to_datetime(orders_df['date'])
                    daily = orders_df.groupby(orders_df['date'].dt.date)['price'].sum().reset_index()
                    fig2 = px.line(daily, x='date', y='price', title='داهاتی ڕۆژانە')
                    st.plotly_chart(fig2, use_container_width=True)
                    
                    status_counts = orders_df['status'].value_counts()
                    fig3 = px.pie(values=status_counts.values, names=status_counts.index, title='دۆخی داواکارییەکان')
                    st.plotly_chart(fig3, use_container_width=True)
                else:
                    st.info("هیچ زانیارییەک نییە")

# --- 18. TERMS PAGE ---
elif st.session_state.page == "terms":
    st.markdown(f"<h2 style='color:{accent}; text-align:center;'>{L['terms_title']}</h2>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class='glass-card'>
        <h4 style="color:{accent};">{L['golden_rules']}</h4>
        <p>١. {L['rule1']}</p>
        <p>٢. {L['rule2']}</p>
        <p>٣. {L['rule3']}</p>
        <p>٤. {L['rule4']}</p>
        <p>٥. {L['rule5']}</p>
        <p>٦. {L['rule6']}</p>
        <p>٧. {L['rule7']}</p>
    </div>
    """, unsafe_allow_html=True)

# --- 19. SUPPORT PAGE ---
elif st.session_state.page == "support":
    st.markdown(f"<h2 style='color:{accent}; text-align:center;'>{L['nav_support']}</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="glass-card">
            <h4 style="color:{accent};">📞 {L['contact_us']}</h4>
            <p class="phone-number">{COMPANY_PHONES[0]}</p>
            <p class="phone-number">{COMPANY_PHONES[1]}</p>
            <p><b>{L['whatsapp_us']}:</b> <a href="{COMPANY_WHATSAPP}" target="_blank">واتسئاپ</a></p>
            <p><b>{L['email_us']}:</b> {COMPANY_EMAIL}</p>
            <p><b>{L['visit_us']}:</b> {COMPANY_ADDRESS}</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="glass-card">
            <h4 style="color:{accent};">🕒 کاتی کار</h4>
            <p>شەممە - پێنجشەممە: ٨:٠٠ - ٢٢:٠٠</p>
            <p>هەینی: ١٤:٠٠ - ٢٠:٠٠</p>
            <p>٢٤/٧ پشتیوانی لە واتسئاپ</p>
        </div>
        """, unsafe_allow_html=True)
    
    with st.form("contact_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("ناو")
            email = st.text_input("ئیمەیڵ")
        with col2:
            phone = st.text_input("ژمارە مۆبایل")
            subject = st.selectbox("بابەت", ["پرسیار", "کێشە", "پێشنیار", "هاوبەشی"])
        message = st.text_area("پەیام")
        if st.form_submit_button("ناردن"):
            st.success("سوپاس! وەڵاممان دەوەیتەوە")

# --- 20. EMERGENCY PAGE (تەنها لەم بەشەدا) ---
elif st.session_state.page == "emergency":
    st.markdown(f"<h2 style='color:#ff4444; text-align:center;'>{L['emergency_call']}</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button(f"🚓 {L['police']} {EMERGENCY_POLICE}", use_container_width=True):
            st.markdown(f'<meta http-equiv="refresh" content="0;url=tel:{EMERGENCY_POLICE}">', unsafe_allow_html=True)
    with col2:
        if st.button(f"🚑 {L['ambulance']} {EMERGENCY_AMBULANCE}", use_container_width=True):
            st.markdown(f'<meta http-equiv="refresh" content="0;url=tel:{EMERGENCY_AMBULANCE}">', unsafe_allow_html=True)
    with col3:
        if st.button(f"📞 {L['call_us']}", use_container_width=True):
            st.markdown(f'<meta http-equiv="refresh" content="0;url=tel:{COMPANY_PHONES[0]}">', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="glass-card" style="text-align:center; margin-top:20px;">
        <h4 style="color:#ff4444;">🚨 ڕێنمایی فریاکەوتن</h4>
        <p>١. ئارام بە و هۆشیار بە</p>
        <p>٢. پەیوەندی بکە بە ١٠٤ یان ١٢٢</p>
        <p>٣. شوێنەکەت بە وردی بڵێ</p>
        <p>٤. لە شوێنەکە بمێنەوە هەتا یارمەتی دەگات</p>
    </div>
    """, unsafe_allow_html=True)

# --- 21. FOOTER ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(f"""
<div style="background-color:{card_bg}; padding:15px; border-radius:10px; text-align:center;">
    <p>📞 <span style="color:{accent};">{COMPANY_PHONES[0]}</span> | <span style="color:{accent};">{COMPANY_PHONES[1]}</span></p>
    <p>✉️ {COMPANY_EMAIL} | 📍 {COMPANY_ADDRESS}</p>
    <p style="font-size:0.9rem;">© ٢٠٢٤ گۆڵدن دلیڤەری پرۆ - کەرکوک</p>
</div>
""", unsafe_allow_html=True)

# --- 22. OFFLINE SYNC ---
offline_orders = load_offline_orders()
if offline_orders and st.button("📤 ناردنی داواکارییە پاشەکەوتکراوەکان"):
    orders_df = load_orders()
    for offline in offline_orders:
        new_order = pd.DataFrame([offline['order']])
        orders_df = pd.concat([orders_df, new_order], ignore_index=True)
    save_orders(orders_df)
    save_offline_orders([])
    st.success("هەموو داواکارییەکان نێردران!")
    st.rerun()
