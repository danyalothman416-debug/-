import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import uuid
import hashlib
import re
import plotly.express as px
from streamlit_option_menu import option_menu
from pytz import timezone
import os

# ==================== CONFIG ====================
st.set_page_config(page_title="Golden Delivery", layout="wide", page_icon="🚚")
baghdad_tz = timezone('Asia/Baghdad')

# ==================== DATABASE SETUP ====================
DB_PATH = "golden_delivery.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Orders table
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
        order_id TEXT PRIMARY KEY,
        date TEXT,
        customer TEXT,
        shop TEXT,
        phone TEXT,
        area TEXT,
        address TEXT,
        shop_addr TEXT,
        price REAL,
        status TEXT,
        user_email TEXT,
        driver_id TEXT,
        payment_method TEXT,
        delivery_notes TEXT,
        promo_code TEXT,
        estimated_delivery TEXT,
        actual_delivery TEXT,
        rating REAL,
        review TEXT
    )''')
    
    # Drivers table
    c.execute('''CREATE TABLE IF NOT EXISTS drivers (
        driver_id TEXT PRIMARY KEY,
        name TEXT,
        phone TEXT,
        email TEXT,
        status TEXT,
        area TEXT,
        join_date TEXT,
        total_deliveries INTEGER,
        rating REAL,
        current_order_id TEXT
    )''')
    
    # Customers table
    c.execute('''CREATE TABLE IF NOT EXISTS customers (
        customer_id TEXT PRIMARY KEY,
        name TEXT,
        phone TEXT UNIQUE,
        email TEXT,
        join_date TEXT,
        total_orders INTEGER,
        loyalty_points INTEGER,
        favorite_area TEXT,
        total_spent REAL
    )''')
    
    # Users table (auth)
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        name TEXT,
        email TEXT UNIQUE,
        phone TEXT,
        password_hash TEXT,
        role TEXT,
        join_date TEXT,
        area TEXT,
        driver_id TEXT
    )''')
    
    # Notifications table
    c.execute('''CREATE TABLE IF NOT EXISTS notifications (
        notif_id TEXT PRIMARY KEY,
        user_email TEXT,
        message TEXT,
        type TEXT,
        timestamp TEXT,
        read INTEGER DEFAULT 0
    )''')
    
    # Feedback table
    c.execute('''CREATE TABLE IF NOT EXISTS feedback (
        feedback_id TEXT PRIMARY KEY,
        order_id TEXT,
        customer_name TEXT,
        rating REAL,
        review TEXT,
        date TEXT
    )''')
    
    # Promos table
    c.execute('''CREATE TABLE IF NOT EXISTS promos (
        code TEXT PRIMARY KEY,
        discount REAL,
        type TEXT,
        min_order REAL,
        expiry TEXT
    )''')
    
    # Insert default admin if not exists
    admin_hash = hashlib.sha256("admin123".encode()).hexdigest()
    c.execute("SELECT * FROM users WHERE email = 'admin@golden.com'")
    if not c.fetchone():
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                  (str(uuid.uuid4())[:8], "Administrator", "admin@golden.com", "", admin_hash, "admin", 
                   datetime.now(baghdad_tz).strftime("%Y-%m-%d"), "", ""))
    
    # Insert default driver
    driver_hash = hashlib.sha256("driver123".encode()).hexdigest()
    c.execute("SELECT * FROM users WHERE email = 'driver@golden.com'")
    if not c.fetchone():
        driver_id = str(uuid.uuid4())[:8]
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                  (str(uuid.uuid4())[:8], "Rezhan Driver", "driver@golden.com", "07701234567", driver_hash, "driver",
                   datetime.now(baghdad_tz).strftime("%Y-%m-%d"), "Kirkuk Citadel", driver_id))
        c.execute("INSERT INTO drivers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                  (driver_id, "Rezhan Driver", "07701234567", "driver@golden.com", "Available", "Kirkuk Citadel",
                   datetime.now(baghdad_tz).strftime("%Y-%m-%d"), 0, 5.0, None))
    
    # Insert default promos
    default_promos = [
        ("WELCOME10", 10, "percentage", 5000, "2025-12-31"),
        ("FREESHIP", 3000, "fixed", 10000, "2025-12-31"),
        ("GOLDEN50", 50, "percentage", 20000, "2025-06-30"),
    ]
    for promo in default_promos:
        c.execute("INSERT OR IGNORE INTO promos VALUES (?, ?, ?, ?, ?)", promo)
    
    conn.commit()
    conn.close()

init_db()

def run_query(query, params=(), fetch=True):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(query, params)
    if fetch:
        result = c.fetchall()
        conn.close()
        return result
    conn.commit()
    conn.close()
    return None

# ==================== HELPERS ====================
def hash_password(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

def validate_iraq_phone(phone):
    return bool(re.match(r'^07\d{9}$', str(phone)))

def validate_email(email):
    return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))

def generate_order_id():
    return f"GD-{datetime.now(baghdad_tz).strftime('%Y%m')}-{str(uuid.uuid4())[:8].upper()}"

def add_notification(user_email, message, notif_type="info"):
    notif_id = str(uuid.uuid4())[:8]
    run_query("INSERT INTO notifications VALUES (?, ?, ?, ?, ?, 0)",
              (notif_id, user_email, message, notif_type, datetime.now(baghdad_tz).strftime("%Y-%m-%d %H:%M")), fetch=False)

# ==================== LANGUAGES ====================
languages = {
    "English 🇬🇧": {
        "dir": "ltr", "align": "left", "title": "GOLDEN DELIVERY", "desc": "Fast. Safe. Reliable",
        "nav_home": "Home", "nav_order": "Send Package", "nav_track": "Track", "nav_profile": "Profile",
        "nav_terms": "Terms", "nav_support": "Support",
        "customer_name": "Customer Name", "shop_name": "Shop Name", "phone": "Phone", "area": "Area",
        "full_addr": "Full Address", "price": "Price (IQD)", "submit": "Continue", "free_info": "🎁 1 out of 3 deliveries is FREE!",
        "order_id": "Order ID", "status": "Status", "estimated": "Est. Delivery", "login": "Login", "register": "Register",
        "logout": "Log Out", "my_orders": "My Orders", "recent_orders": "Recent Orders",
        "track_order": "Track Order", "profile": "Profile", "address_book": "Address Book", 
        "payment_methods": "Payment Methods", "notifications": "Notifications", "help_center": "Help Center",
        "about_us": "About Us", "log_out": "Log Out", "hi": "Hi", "estimated_price": "Estimated Price",
        "weight": "Weight (kg)", "box": "Box", "delivery_type": "Delivery Type", "standard": "Standard",
        "express": "Express", "in_transit": "In Transit", "continue": "Continue", "welcome": "Welcome back!"
    },
    "کوردی 🇭🇺": {
        "dir": "rtl", "align": "right", "title": "گۆڵدن دلیڤەری", "desc": "خێرا. پارێزراو. باوەرپێکراو",
        "nav_home": "سەرەکی", "nav_order": "ناردنی پاکەت", "nav_track": "شوێنکەوتن", "nav_profile": "پڕۆفایل",
        "nav_terms": "یاساکان", "nav_support": "پاڵپشتی",
        "customer_name": "ناوی کڕیار", "shop_name": "ناوی دوکان", "phone": "مۆبایل", "area": "گەڕەک",
        "full_addr": "ناونیشانی تەواو", "price": "نرخ (د.ع)", "submit": "بەردەوام بە", "free_info": "🎁 یەکێک لە هەر ۳ گەیاندنێک بەخۆڕاییە!",
        "order_id": "ژ. داواکاری", "status": "دۆخ", "estimated": "گەیاندنی چاوەڕوان", "login": "چوونەژوورەوە", "register": "تۆماربوون",
        "logout": "چوونەدەرەوە", "my_orders": "داواکارییەکانی من", "recent_orders": "داواکارییە نوێیەکان",
        "track_order": "شوێنکەوتنی داواکاری", "profile": "پڕۆفایل", "address_book": "ناونیشانەکان",
        "payment_methods": "شێوازەکانی پارەدان", "notifications": "ئاگادارکردنەوەکان", "help_center": "ناوەندی یارمەتی",
        "about_us": "دەربارەی ئێمە", "log_out": "چوونەدەرەوە", "hi": "سڵاو", "estimated_price": "نرخی خەملێنراو",
        "weight": "کێش (کگ)", "box": "بۆکس", "delivery_type": "جۆری گەیاندن", "standard": "ئاسایی",
        "express": "خێرا", "in_transit": "لە ڕێگادا", "continue": "بەردەوام بە", "welcome": "بەخێربێیتەوە!"
    }
}

# ==================== SESSION STATE ====================
if 'lang' not in st.session_state:
    st.session_state.lang = "English 🇬🇧"
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = None
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = None
if 'user_phone' not in st.session_state:
    st.session_state.user_phone = None

L = languages[st.session_state.lang]

# ==================== HEADER ====================
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.markdown(f"<h1 style='color:#D4AF37; margin:0;'>{L['title']}</h1><p style='margin-top:-10px'>{L['desc']}</p>", unsafe_allow_html=True)
with col2:
    lang_sel = st.selectbox("", list(languages.keys()), index=list(languages.keys()).index(st.session_state.lang), label_visibility="collapsed")
    if lang_sel != st.session_state.lang:
        st.session_state.lang = lang_sel
        st.rerun()
with col3:
    if st.session_state.logged_in:
        st.button(L['logout'], on_click=lambda: [st.session_state.update({k: None for k in ['logged_in','user_email','user_role','user_name','user_phone']}), st.rerun()])

# ==================== SIDEBAR NAVIGATION (Horizontal) ====================
selected = option_menu(
    menu_title=None,
    options=[L['nav_home'], L['nav_order'], L['nav_track'], L['nav_profile'], L['nav_terms'], L['nav_support']],
    icons=['house', 'box', 'geo-alt', 'person', 'file-text', 'headset'],
    orientation="horizontal",
    styles={"container": {"max-width": "100%", "padding": 0}, "nav-link": {"border-radius": "30px", "margin": "0 5px"}}
)

# ==================== MAIN LAYOUT ====================
if selected == L['nav_home']:
    col_left, col_right = st.columns(2, gap="large")
    
    # LEFT COLUMN
    with col_left:
        # Recent Orders
        st.markdown(f"<h3 style='color:#D4AF37;'>📋 {L['recent_orders']}</h3>", unsafe_allow_html=True)
        orders = run_query("SELECT order_id, area, price, date, status FROM orders ORDER BY date DESC LIMIT 4")
        if orders:
            for o in orders:
                st.markdown(f"""
                <div style='background:#1e1e2e; padding:12px; border-radius:12px; margin-bottom:10px; border-left:4px solid #D4AF37;'>
                    <b>Order #{o[0]}</b><br>
                    {o[1]} • {o[2]} IQD<br>
                    <span style='font-size:12px; color:#aaa;'>{o[3][:16]}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No orders yet")
        
        # Send a Package Form
        st.markdown(f"<h3 style='color:#D4AF37; margin-top:30px;'>📦 {L['nav_order']}</h3>", unsafe_allow_html=True)
        with st.form("send_package"):
            from_area = st.text_input("From", value="Erbil, Kurdistan", disabled=True)
            to_area = st.selectbox("To", ["Duhok, Kurdistan", "Sulaymaniyah, Kurdistan", "Kirkuk, Kurdistan"])
            col_w1, col_w2 = st.columns(2)
            with col_w1:
                weight = st.number_input(L['weight'], min_value=0.5, max_value=50.0, value=2.5, step=0.5)
            with col_w2:
                price_calc = 3000 if weight <= 2 else 3000 + (weight-2)*500
                st.markdown(f"<b>{L['box']}</b><br>${price_calc/1500:.2f}", unsafe_allow_html=True)
            delivery_type = st.radio(L['delivery_type'], [L['standard'], L['express']], horizontal=True)
            est_price = price_calc if delivery_type == L['standard'] else price_calc + 2000
            st.markdown(f"<h4>{L['estimated_price']}: {est_price:,} IQD</h4>", unsafe_allow_html=True)
            if st.form_submit_button(L['continue']):
                st.success("Order placed! Use tracking ID.")
    
    # RIGHT COLUMN
    with col_right:
        # Track Order
        st.markdown(f"<h3 style='color:#D4AF37;'>🔍 {L['track_order']}</h3>", unsafe_allow_html=True)
        track_id = st.text_input(L['order_id'], placeholder="GD-2025-XXXX")
        if track_id:
            order = run_query("SELECT * FROM orders WHERE order_id = ?", (track_id,), fetch=True)
            if order:
                o = order[0]
                st.markdown(f"""
                <div style='background:#1e1e2e; padding:15px; border-radius:12px;'>
                    <b>{L['order_id']}:</b> {o[0]}<br>
                    <b>{L['status']}:</b> {o[9]}<br>
                    <b>{L['estimated']}:</b> {o[15] if o[15] else 'Not set'}<br>
                    <b>From:</b> Erbil → {o[5]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("Order not found")
        
        # Profile Section (if logged in)
        if st.session_state.logged_in:
            st.markdown(f"<h3 style='color:#D4AF37; margin-top:20px;'>👤 {L['profile']}</h3>", unsafe_allow_html=True)
            st.markdown(f"**{L['hi']}, {st.session_state.user_name}**  \n{st.session_state.user_email}")
            
            # My Orders
            st.markdown(f"<h4>{L['my_orders']}</h4>", unsafe_allow_html=True)
            my_orders = run_query("SELECT order_id, area, price, status FROM orders WHERE user_email = ? OR phone = ? ORDER BY date DESC LIMIT 5", 
                                  (st.session_state.user_email, st.session_state.user_phone or ""))
            if my_orders:
                for mo in my_orders:
                    st.markdown(f"- **{mo[0]}** - {mo[1]} - {mo[2]:,} IQD - {mo[3]}")
            else:
                st.caption(L['no_orders'])
            
            # Address Book
            st.markdown(f"<h4>{L['address_book']}</h4>", unsafe_allow_html=True)
            st.markdown("🏠 Home: 60m Street, Erbil  \n🏢 Office: Italian City, Erbil")
            
            # Payment Methods
            st.markdown(f"<h4>{L['payment_methods']}</h4>", unsafe_allow_html=True)
            st.markdown("💳 VISA •••• 4242  \n💳 Mastercard •••• 8888")
        else:
            # Login / Register
            with st.expander(f"🔐 {L['login']} / {L['register']}"):
                tab_login, tab_reg = st.tabs([L['login'], L['register']])
                with tab_login:
                    email = st.text_input("Email")
                    pwd = st.text_input("Password", type="password")
                    if st.button(L['login']):
                        user = run_query("SELECT name, email, phone, role FROM users WHERE email = ? AND password_hash = ?", 
                                        (email, hash_password(pwd)))
                        if user:
                            u = user[0]
                            st.session_state.logged_in = True
                            st.session_state.user_email = u[1]
                            st.session_state.user_name = u[0]
                            st.session_state.user_role = u[3]
                            st.session_state.user_phone = u[2] if u[2] else ""
                            add_notification(u[1], f"Welcome back {u[0]}!", "success")
                            st.rerun()
                        else:
                            st.error("Invalid credentials")
                with tab_reg:
                    name = st.text_input("Full Name")
                    email = st.text_input("Email")
                    phone = st.text_input("Phone (07xx...)")
                    pwd = st.text_input("Password", type="password")
                    if st.button(L['register']):
                        if validate_iraq_phone(phone) and validate_email(email):
                            user_id = str(uuid.uuid4())[:8]
                            run_query("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                     (user_id, name, email, phone, hash_password(pwd), "customer",
                                      datetime.now(baghdad_tz).strftime("%Y-%m-%d"), "", ""), fetch=False)
                            st.success("Registered! Please login.")
                        else:
                            st.error("Invalid phone or email")

elif selected == L['nav_order']:
    st.markdown(f"<h2 style='text-align:center; color:#D4AF37;'>{L['nav_order']}</h2>", unsafe_allow_html=True)
    st.info(L['free_info'])
    
    with st.form("order_form"):
        col1, col2 = st.columns(2)
        with col1:
            customer = st.text_input(L['customer_name'])
            phone = st.text_input(L['phone'])
            shop = st.text_input(L['shop_name'])
        with col2:
            area = st.selectbox(L['area'], ["Kirkuk Citadel", "Tis'in", "Shoraw", "Rahim Awa", "Azadi", "Al-Wasiti"])
            address = st.text_area(L['full_addr'])
            price = st.number_input(L['price'], min_value=0, value=3000, step=1000)
        
        if st.form_submit_button(L['submit']):
            if customer and phone and validate_iraq_phone(phone):
                order_id = generate_order_id()
                run_query("""INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                         (order_id, datetime.now(baghdad_tz).strftime("%Y-%m-%d %H:%M"), customer, shop, phone, area,
                          address, "", price, "Pending", st.session_state.user_email if st.session_state.logged_in else "",
                          "", "Cash", "", "", (datetime.now(baghdad_tz)+timedelta(hours=24)).strftime("%Y-%m-%d %H:%M"), None, None, None),
                         fetch=False)
                add_notification(st.session_state.user_email or "guest", f"Order {order_id} created!")
                st.success(f"✅ Order {order_id} confirmed!")
                st.balloons()
            else:
                st.error("Valid phone number required")

elif selected == L['nav_track']:
    st.markdown(f"<h2 style='text-align:center; color:#D4AF37;'>{L['track_order']}</h2>", unsafe_allow_html=True)
    track_id = st.text_input(L['order_id'])
    if track_id:
        order = run_query("SELECT * FROM orders WHERE order_id = ?", (track_id,), fetch=True)
        if order:
            o = order[0]
            st.markdown(f"""
            <div style='background:#1e1e2e; padding:20px; border-radius:15px;'>
                <b>{L['order_id']}:</b> {o[0]}<br>
                <b>Status:</b> {o[9]}<br>
                <b>From:</b> Erbil → {o[5]}<br>
                <b>{L['estimated']}:</b> {o[15]}<br>
                <b>Price:</b> {int(o[8]):,} IQD
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("Not found")

elif selected == L['nav_profile']:
    if not st.session_state.logged_in:
        st.warning("Please login first")
    else:
        st.markdown(f"<h2 style='color:#D4AF37;'>{L['profile']}</h2>", unsafe_allow_html=True)
        st.markdown(f"**{L['hi']}, {st.session_state.user_name}**  \n📧 {st.session_state.user_email}  \n📞 {st.session_state.user_phone}")
        
        # My Orders Full List
        st.subheader(L['my_orders'])
        my_orders = run_query("SELECT order_id, date, area, price, status FROM orders WHERE user_email = ? OR phone = ? ORDER BY date DESC", 
                              (st.session_state.user_email, st.session_state.user_phone or ""))
        if my_orders:
            for mo in my_orders:
                st.markdown(f"🔹 **{mo[0]}** - {mo[2]} - {int(mo[3]):,} IQD - {mo[4]} ({mo[1][:10]})")
        else:
            st.info(L['no_orders'])
        
        # Notifications
        st.subheader("🔔 Notifications")
        notifs = run_query("SELECT message, timestamp FROM notifications WHERE user_email = ? ORDER BY timestamp DESC LIMIT 5", 
                          (st.session_state.user_email,))
        if notifs:
            for n in notifs:
                st.caption(f"📢 {n[0]} - {n[1]}")
        else:
            st.caption("No notifications")

elif selected == L['nav_terms']:
    st.markdown(f"<h2 style='color:#D4AF37;'>{L['nav_terms']}</h2>", unsafe_allow_html=True)
    st.markdown("""
    1. 1 out of 3 deliveries is free - automatically applied!  
    2. No illegal items - we comply with all local laws  
    3. Fast Kirkuk wide service - all neighborhoods covered  
    4. Delivery within 24 hours of order confirmation  
    5. Cash on delivery only  
    6. Free delivery promotion applies to orders over 3000 IQD  
    7. Customer must be present at time of delivery
    """)

elif selected == L['nav_support']:
    st.markdown(f"<h2 style='color:#D4AF37;'>{L['nav_support']}</h2>", unsafe_allow_html=True)
    st.markdown("""
    📞 **Call us:** 07801352003 / 07721959922  
    💬 **WhatsApp:** [Click to chat](https://wa.me/9647801352003)  
    📧 **Email:** Danyalexpert@gmail.com  
    🏢 **Address:** Kirkuk, Iraq  
    🕒 **Hours:** Sat-Thu 8AM-10PM, Fri 2PM-8PM
    """)

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("<p style='text-align:center; font-size:12px;'>© 2025 Golden Delivery - Fast. Safe. Reliable.</p>", unsafe_allow_html=True)
