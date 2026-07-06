# app.py - نسخەی فرۆشتن بە License System
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import hashlib
import json
import base64
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import os
import random
from PIL import Image
import time
import shutil
import pickle
from collections import defaultdict
import re
import secrets
import string
import uuid

# ڕێکخستنی لاپەڕە
st.set_page_config(
    page_title="دکتۆر دانیال - خوێندنی پزیشکی",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== LICENSE SYSTEM ====================
class LicenseSystem:
    def __init__(self):
        self.license_file = 'licenses.db'
        self.init_license_db()
    
    def init_license_db(self):
        conn = sqlite3.connect(self.license_file)
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS licenses
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      license_key TEXT UNIQUE,
                      device_id TEXT,
                      user_email TEXT,
                      license_type TEXT,
                      created_at TEXT,
                      expires_at TEXT,
                      is_active INTEGER DEFAULT 1,
                      last_used TEXT)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS activation_attempts
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      license_key TEXT,
                      device_id TEXT,
                      attempt_time TEXT,
                      status TEXT)''')
        
        conn.commit()
        conn.close()
    
    def generate_license_key(self, license_type='lifetime', user_email=None):
        prefix = "DRD"
        parts = []
        for i in range(3):
            part = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4))
            parts.append(part)
        license_key = f"{prefix}-{'-'.join(parts)}"
        
        conn = sqlite3.connect(self.license_file)
        c = conn.cursor()
        
        now = datetime.now().isoformat()
        if license_type == 'monthly':
            expires = (datetime.now() + timedelta(days=30)).isoformat()
        elif license_type == 'yearly':
            expires = (datetime.now() + timedelta(days=365)).isoformat()
        else:
            expires = '2100-12-31T23:59:59'
        
        c.execute("""INSERT INTO licenses 
                     (license_key, user_email, license_type, created_at, expires_at, is_active)
                     VALUES (?, ?, ?, ?, ?, 1)""",
                  (license_key, user_email, license_type, now, expires))
        
        conn.commit()
        conn.close()
        return license_key
    
    def activate_license(self, license_key, device_id):
        conn = sqlite3.connect(self.license_file)
        c = conn.cursor()
        
        c.execute("SELECT * FROM licenses WHERE license_key=? AND is_active=1", (license_key,))
        license_data = c.fetchone()
        
        if not license_data:
            self.log_attempt(license_key, device_id, 'invalid')
            conn.close()
            return {'status': 'invalid', 'message': '⛔ کۆدەکە نادروستە یان چالاک نییە'}
        
        try:
            expires_at = datetime.fromisoformat(license_data[5])
            if expires_at < datetime.now():
                c.execute("UPDATE licenses SET is_active=0 WHERE license_key=?", (license_key,))
                conn.commit()
                self.log_attempt(license_key, device_id, 'expired')
                conn.close()
                return {'status': 'expired', 'message': '⏰ کۆدەکە بەسەرچووە'}
        except:
            pass
        
        c.execute("SELECT device_id FROM licenses WHERE license_key=? AND device_id IS NOT NULL AND device_id != ''", (license_key,))
        existing_device = c.fetchone()
        
        if existing_device and existing_device[0] != device_id:
            self.log_attempt(license_key, device_id, 'used')
            conn.close()
            return {'status': 'used', 'message': '🔒 کۆدەکە لەسەر ئامێرێکی تر چالاک کراوە'}
        
        c.execute("UPDATE licenses SET device_id=?, last_used=? WHERE license_key=?",
                 (device_id, datetime.now().isoformat(), license_key))
        conn.commit()
        
        self.log_attempt(license_key, device_id, 'success')
        conn.close()
        
        return {'status': 'success', 'message': '✅ کۆد بە سەرکەوتوویی چالاک کرا'}
    
    def log_attempt(self, license_key, device_id, status):
        conn = sqlite3.connect(self.license_file)
        c = conn.cursor()
        c.execute("INSERT INTO activation_attempts (license_key, device_id, attempt_time, status) VALUES (?, ?, ?, ?)",
                 (license_key, device_id, datetime.now().isoformat(), status))
        conn.commit()
        conn.close()
    
    def check_license_status(self, license_key, device_id=None):
        conn = sqlite3.connect(self.license_file)
        c = conn.cursor()
        c.execute("SELECT * FROM licenses WHERE license_key=?", (license_key,))
        license_data = c.fetchone()
        conn.close()
        
        if not license_data:
            return {'status': 'not_found'}
        
        is_active = license_data[6] == 1
        
        try:
            expires_at = datetime.fromisoformat(license_data[5])
            is_expired = expires_at < datetime.now()
        except:
            is_expired = False
        
        if not is_active or is_expired:
            return {'status': 'inactive', 'expires_at': license_data[5]}
        
        stored_device = license_data[2] if license_data[2] else None
        if device_id and stored_device and stored_device != device_id:
            return {'status': 'device_mismatch'}
        
        return {
            'status': 'active',
            'expires_at': license_data[5],
            'device_id': license_data[2],
            'license_type': license_data[4]
        }
    
    def generate_bulk_licenses(self, count, license_type='lifetime'):
        keys = []
        for _ in range(count):
            key = self.generate_license_key(license_type)
            keys.append(key)
        return keys
    
    def get_all_licenses(self):
        conn = sqlite3.connect(self.license_file)
        c = conn.cursor()
        c.execute("SELECT * FROM licenses ORDER BY created_at DESC")
        licenses = c.fetchall()
        conn.close()
        return licenses
    
    def get_license_stats(self):
        conn = sqlite3.connect(self.license_file)
        c = conn.cursor()
        
        c.execute("SELECT COUNT(*) FROM licenses")
        total = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM licenses WHERE is_active=1")
        active = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM licenses WHERE device_id IS NOT NULL AND device_id != ''")
        used = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM licenses WHERE license_type='lifetime' AND is_active=1")
        lifetime = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM licenses WHERE license_type='yearly' AND is_active=1")
        yearly = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM licenses WHERE license_type='monthly' AND is_active=1")
        monthly = c.fetchone()[0]
        
        conn.close()
        return {
            'total': total,
            'active': active,
            'used': used,
            'lifetime': lifetime,
            'yearly': yearly,
            'monthly': monthly
        }

# Initialize license system
license_system = LicenseSystem()

# ==================== GENERATE INITIAL LICENSES ====================
def generate_initial_licenses():
    conn = sqlite3.connect('licenses.db')
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM licenses")
    count = c.fetchone()[0]
    
    if count == 0:
        license_keys = []
        for i in range(500):
            prefix = "DRD"
            parts = []
            for j in range(3):
                part = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4))
                parts.append(part)
            license_key = f"{prefix}-{'-'.join(parts)}"
            license_keys.append(license_key)
            
            now = datetime.now().isoformat()
            expires = '2100-12-31T23:59:59'
            
            c.execute("""INSERT INTO licenses 
                         (license_key, user_email, license_type, created_at, expires_at, is_active)
                         VALUES (?, ?, ?, ?, ?, 1)""",
                      (license_key, f"license_{i+1}@drdaniel.com", 'lifetime', now, expires))
        
        conn.commit()
        
        with open('licenses_list.txt', 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("کۆدی لایسەنسەکانی دکتۆر دانیال - ٥٠٠ کۆد (Lifetime)\n")
            f.write("=" * 60 + "\n")
            f.write("بەرواری بەسەرچوون: 2100-12-31\n")
            f.write("جۆر: Lifetime (هەمیشەیی)\n")
            f.write("=" * 60 + "\n\n")
            for i, key in enumerate(license_keys, 1):
                f.write(f"{i:3d}. {key}\n")
            f.write("\n" + "=" * 60 + "\n")
            f.write(f"کۆی گشتی: {len(license_keys)} کۆد\n")
            f.write("=" * 60 + "\n")
        
        return license_keys
    else:
        return None

# Generate initial licenses
generated_keys = generate_initial_licenses()

# ==================== SESSION STATE ====================
if 'language' not in st.session_state:
    st.session_state.language = 'کوردی'
if 'undo_stack' not in st.session_state:
    st.session_state.undo_stack = []
if 'study_collections' not in st.session_state:
    st.session_state.study_collections = []
if 'study_history' not in st.session_state:
    st.session_state.study_history = []
if 'achievements' not in st.session_state:
    st.session_state.achievements = {
        'study_days': 0,
        'items_added': 0,
        'favorites': 0,
        'last_study_date': None
    }
if 'device_id' not in st.session_state:
    st.session_state.device_id = str(uuid.uuid4())
if 'license_key' not in st.session_state:
    st.session_state.license_key = None
if 'license_valid' not in st.session_state:
    st.session_state.license_valid = False
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ''
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True
if 'current_page' not in st.session_state:
    st.session_state.current_page = '📊 داشبۆرد'
if 'font_size' not in st.session_state:
    st.session_state.font_size = 'medium'

# ==================== CSS ====================
def load_css():
    dark_mode = st.session_state.get('dark_mode', True)
    font_size = st.session_state.get('font_size', 'medium')
    
    if dark_mode:
        bg_gradient = "linear-gradient(135deg, #0f0c29, #302b63, #24243e)"
        card_bg = "rgba(255,255,255,0.08)"
        text_color = "#ffffff"
        border_color = "rgba(255,255,255,0.15)"
        shadow_color = "rgba(31, 38, 135, 0.5)"
    else:
        bg_gradient = "linear-gradient(135deg, #f5f7fa, #c3cfe2)"
        card_bg = "rgba(255,255,255,0.75)"
        text_color = "#1a1a2e"
        border_color = "rgba(0,0,0,0.1)"
        shadow_color = "rgba(31, 38, 135, 0.2)"
    
    font_sizes = {
        'small': '14px',
        'medium': '16px',
        'large': '18px',
        'xlarge': '20px'
    }
    
    st.markdown(f"""
    <style>
        .stApp {{
            background: {bg_gradient};
            color: {text_color};
            min-height: 100vh;
            font-size: {font_sizes[font_size]};
        }}
        
        .glass-card {{
            background: {card_bg};
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-radius: 25px;
            border: 1px solid {border_color};
            padding: 25px;
            margin: 12px 0;
            box-shadow: 0 8px 32px 0 {shadow_color};
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            animation: fadeInUp 0.6s ease-out;
        }}
        
        .glass-card:hover {{
            transform: translateY(-5px);
        }}
        
        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(30px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .main-header {{
            text-align: center;
            padding: 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 25px;
            color: white;
            margin-bottom: 30px;
            animation: fadeInUp 0.8s ease-out;
            box-shadow: 0 10px 40px rgba(102, 126, 234, 0.4);
        }}
        
        .stButton > button {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 15px;
            padding: 10px 20px;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            width: 100%;
            cursor: pointer;
        }}
        
        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
        }}
        
        .license-badge {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            margin: 3px;
        }}
        
        .license-valid {{
            background: #2ed573;
            color: white;
        }}
        
        .license-invalid {{
            background: #ff4757;
            color: white;
        }}
        
        .license-warning {{
            background: #ffa502;
            color: white;
        }}
        
        .color-label {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 15px;
            font-size: 11px;
            margin: 2px;
        }}
        
        @media (max-width: 768px) {{
            .glass-card {{ padding: 15px; margin: 8px 0; }}
            .main-header {{ padding: 20px; }}
        }}
    </style>
    """, unsafe_allow_html=True)

# ==================== DATABASE FUNCTIONS ====================
def init_db():
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE,
                  password TEXT,
                  role TEXT,
                  created_at TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS medicines
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  brand TEXT,
                  generic TEXT,
                  dose TEXT,
                  route TEXT,
                  group_name TEXT,
                  priority TEXT DEFAULT 'medium',
                  color_label TEXT,
                  tags TEXT,
                  notes TEXT,
                  favorite INTEGER DEFAULT 0,
                  pinned INTEGER DEFAULT 0,
                  created_at TEXT,
                  updated_at TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS lab_tests
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  purpose TEXT,
                  normal_range TEXT,
                  preparation TEXT,
                  priority TEXT DEFAULT 'medium',
                  color_label TEXT,
                  tags TEXT,
                  notes TEXT,
                  favorite INTEGER DEFAULT 0,
                  pinned INTEGER DEFAULT 0,
                  created_at TEXT,
                  updated_at TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS general_notes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT,
                  content TEXT,
                  image_path TEXT,
                  link TEXT,
                  attachment_path TEXT,
                  tags TEXT,
                  created_at TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS note_templates
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  content TEXT,
                  created_at TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS categories
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  color TEXT,
                  type TEXT,
                  created_at TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS reminders
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT,
                  description TEXT,
                  reminder_date TEXT,
                  completed INTEGER DEFAULT 0,
                  created_at TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  action TEXT,
                  table_name TEXT,
                  record_id INTEGER,
                  details TEXT,
                  created_at TEXT)''')
    
    try:
        c.execute("SELECT tags FROM medicines LIMIT 1")
    except:
        c.execute("ALTER TABLE medicines ADD COLUMN tags TEXT")
    
    try:
        c.execute("SELECT pinned FROM medicines LIMIT 1")
    except:
        c.execute("ALTER TABLE medicines ADD COLUMN pinned INTEGER DEFAULT 0")
    
    try:
        c.execute("SELECT tags FROM lab_tests LIMIT 1")
    except:
        c.execute("ALTER TABLE lab_tests ADD COLUMN tags TEXT")
    
    try:
        c.execute("SELECT pinned FROM lab_tests LIMIT 1")
    except:
        c.execute("ALTER TABLE lab_tests ADD COLUMN pinned INTEGER DEFAULT 0")
    
    try:
        c.execute("SELECT tags FROM general_notes LIMIT 1")
    except:
        c.execute("ALTER TABLE general_notes ADD COLUMN tags TEXT")
    
    c.execute("SELECT * FROM users WHERE username='Danyal'")
    if not c.fetchone():
        hashed = hashlib.sha256('Admin@2024'.encode()).hexdigest()
        c.execute("INSERT INTO users (username, password, role, created_at) VALUES (?, ?, ?, ?)",
                 ('Danyal', hashed, 'admin', datetime.now().isoformat()))
    
    conn.commit()
    conn.close()

# ==================== UTILITY FUNCTIONS ====================
def add_history(action, table_name, record_id, details):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO history (action, table_name, record_id, details, created_at) VALUES (?, ?, ?, ?, ?)",
             (action, table_name, record_id, details, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def auto_backup():
    try:
        if os.path.exists('medical_data.db'):
            backup_dir = 'backups'
            os.makedirs(backup_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f'{backup_dir}/backup_{timestamp}.db'
            shutil.copy2('medical_data.db', backup_path)
            
            backups = sorted([f for f in os.listdir(backup_dir) if f.endswith('.db')])
            if len(backups) > 10:
                for old_backup in backups[:-10]:
                    os.remove(os.path.join(backup_dir, old_backup))
    except:
        pass

def update_achievements(type_):
    today = datetime.now().date()
    if st.session_state.achievements['last_study_date'] != str(today):
        st.session_state.achievements['study_days'] += 1
        st.session_state.achievements['last_study_date'] = str(today)
    
    if type_ == 'items_added':
        st.session_state.achievements['items_added'] += 1
    elif type_ == 'favorites':
        st.session_state.achievements['favorites'] += 1

def check_login(username, password):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    hashed = hashlib.sha256(password.encode()).hexdigest()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed))
    user = c.fetchone()
    conn.close()
    return user

def add_user(username, password, role='user'):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    hashed = hashlib.sha256(password.encode()).hexdigest()
    try:
        c.execute("INSERT INTO users (username, password, role, created_at) VALUES (?, ?, ?, ?)",
                 (username, hashed, role, datetime.now().isoformat()))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

# ==================== LICENSE UI ====================
def show_license_activation():
    st.markdown("""
    <div class="main-header">
        <h1>🏥 دکتۆر دانیال</h1>
        <p>پلاتفۆرمی خوێندنی پزیشکی - پرۆفیشناڵ</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🔑 چالاککردنی لایسەنس")
        
        st.info("""
        **تکایە کۆدی لایسەنسەکەت بنووسە بۆ چالاککردن**
        
        کۆدەکەت لە شێوەی **DRD-XXXX-XXXX-XXXX** دەبێت
        """)
        
        license_key = st.text_input("کۆدی لایسەنس", placeholder="DRD-XXXX-XXXX-XXXX", key="license_input")
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("✅ چالاککردن", use_container_width=True, key="activate_btn"):
                if license_key:
                    with st.spinner("⏳ چالاکدەکرێت..."):
                        result = license_system.activate_license(license_key, st.session_state.device_id)
                    
                    if result['status'] == 'success':
                        st.session_state.license_key = license_key
                        st.session_state.license_valid = True
                        st.success(result['message'])
                        time.sleep(1)
                        st.rerun()
                    elif result['status'] == 'expired':
                        st.error("⏰ ئەم کۆدە بەسەرچووە. ئەگەر لایسەنسەکەت Lifetime یان Yearly بێت و هێشتا ماوەکەی نەبەسەرچووبێت، تکایە پەیوەندی بە پشتگیرییەوە بکە.")
                    elif result['status'] == 'used':
                        st.error("🔒 ئەم کۆدە لەسەر ئامێرێکی تر چالاک کراوە. هەر کۆدێک تەنها لە یەک ئامێر کار دەکات.")
                    else:
                        st.error(result['message'])
                else:
                    st.warning("⚠️ تکایە کۆدی لایسەنس بنووسە")
        
        with col_b:
            if st.button("🔍 پشکنینی دۆخ", use_container_width=True, key="check_status_btn"):
                if license_key:
                    status = license_system.check_license_status(license_key)
                    if status['status'] == 'active':
                        st.success(f"""
                        ✅ **چالاکە**
                        - جۆر: {status.get('license_type', 'نادیار')}
                        - بەسەردەچێت: {status.get('expires_at', 'نادیار')}
                        """)
                    elif status['status'] == 'inactive':
                        st.error("❌ ناچالاکە یان بەسەرچووە")
                    else:
                        st.warning("🔍 کۆد نەدۆزرایەوە")
                else:
                    st.warning("⚠️ تکایە کۆدی لایسەنس بنووسە")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 👤 چوونەژوورەوە بۆ بەڕێوەبەر")
        
        with st.form("admin_login_form"):
            username = st.text_input("ناوی بەکارهێنەر")
            password = st.text_input("ووشەی نهێنی", type="password")
            
            if st.form_submit_button("🔓 چوونەژوورەوە"):
                if username and password:
                    user = check_login(username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.user_id = user[0]
                        st.session_state.user_role = user[3]
                        st.session_state.license_valid = True
                        st.success(f"✅ بەخێربێیت {username}!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ ناوی بەکارهێنەر یان پاسۆرد هەڵەیە!")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div style="text-align: center; padding: 20px; opacity: 0.7;">
            <p>📧 بۆ کڕینی کۆدی لایسەنس پەیوەندی بکە بە: <strong>drdaniel@medical.com</strong></p>
            <p>💰 نرخی لایسەنس: Lifetime = 50$ | Yearly = 20$ | Monthly = 5$</p>
        </div>
        """, unsafe_allow_html=True)

def show_license_manager():
    st.markdown("### 🔑 بەڕێوەبەری لایسەنس")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 ئامار", "➕ دروستکردن", "📋 لیست", "📥 هەناردە"])
    
    with tab1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📊 ئاماری گشتی")
        
        stats = license_system.get_license_stats()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📦 کۆی گشتی", stats['total'])
        with col2:
            st.metric("✅ چالاک", stats['active'])
        with col3:
            st.metric("💻 بەکارهێنراو", stats['used'])
        with col4:
            st.metric("🎖️ Lifetime", stats['lifetime'])
        
        col1, col2 = st.columns(2)
        with col1:
            fig = go.Figure(data=[go.Pie(
                labels=['چالاک', 'ناچالاک'],
                values=[stats['active'], stats['total'] - stats['active']],
                marker=dict(colors=['#2ed573', '#ff4757']),
                hole=0.3
            )])
            fig.update_layout(title="ڕێژەی چالاکی", paper_bgcolor='rgba(0,0,0,0)', height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = go.Figure(data=[go.Pie(
                labels=['Lifetime', 'Yearly', 'Monthly'],
                values=[stats['lifetime'], stats['yearly'], stats['monthly']],
                marker=dict(colors=['#667eea', '#ffa502', '#ff6b6b']),
                hole=0.3
            )])
            fig.update_layout(title="جۆری لایسەنس", paper_bgcolor='rgba(0,0,0,0)', height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("➕ دروستکردنی کۆدی نوێ")
        
        col1, col2 = st.columns(2)
        with col1:
            license_type = st.selectbox("جۆری لایسەنس", ["lifetime", "yearly", "monthly"])
        with col2:
            count = st.number_input("ژمارەی کۆد", min_value=1, max_value=500, value=1)
        
        user_email = st.text_input("ئیمەیڵی بەکارهێنەر (ئارەزوومەندانە)", placeholder="user@example.com")
        
        if st.button("🔑 دروستکردنی کۆد", use_container_width=True):
            if count == 1:
                key = license_system.generate_license_key(license_type, user_email if user_email else None)
                st.success("✅ کۆدی نوێ دروستکرا!")
                st.code(key, language="")
                st.info(f"جۆر: {license_type} | ئیمەیڵ: {user_email if user_email else 'دیاری نەکراو'}")
            else:
                keys = license_system.generate_bulk_licenses(count, license_type)
                st.success(f"✅ {count} کۆد دروستکرا!")
                
                keys_text = "\n".join(keys)
                st.download_button(
                    label=f"📥 داگرتنی {count} کۆد",
                    data=keys_text,
                    file_name=f"licenses_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
                
                with st.expander("🔍 بینینی کۆدەکان"):
                    for i, key in enumerate(keys, 1):
                        st.code(f"{i}. {key}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📋 لیستی لایسەنسەکان")
        
        licenses = license_system.get_all_licenses()
        
        if licenses:
            license_data = []
            for lic in licenses:
                try:
                    expires_at = datetime.fromisoformat(lic[5])
                    is_expired = expires_at < datetime.now()
                except:
                    is_expired = False
                
                status = "✅ چالاک" if lic[6] == 1 and not is_expired else "❌ ناچالاک"
                if lic[2]:
                    status += " (بەکارهێنراو)"
                
                license_data.append({
                    "ID": lic[0],
                    "کۆد": lic[1],
                    "جۆر": lic[4],
                    "بەسەردەچێت": lic[5][:10] if lic[5] else "نادیار",
                    "دۆخ": status,
                    "ئیمەیڵ": lic[3] if lic[3] else "-"
                })
            
            df = pd.DataFrame(license_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("هیچ لایسەنسێک نییە")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab4:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📥 هەناردەکردنی کۆدەکان")
        
        if os.path.exists('licenses_list.txt'):
            with open('licenses_list.txt', 'r', encoding='utf-8') as f:
                content = f.read()
            
            st.download_button(
                label="📄 داگرتنی هەموو کۆدەکان (TXT)",
                data=content,
                file_name=f"all_licenses_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        else:
            st.warning("فایلی کۆدەکان نەدۆزرایەوە")
        
        st.markdown('</div>', unsafe_allow_html=True)

# ==================== CRUD FUNCTIONS (Simplified for brevity) ====================
def get_medicines(search=None, group=None, priority=None, tag=None):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    
    query = "SELECT * FROM medicines WHERE 1=1"
    params = []
    
    if search:
        query += " AND (name LIKE ? OR brand LIKE ? OR generic LIKE ? OR tags LIKE ?)"
        params.extend([f'%{search}%'] * 4)
    
    if group:
        query += " AND group_name = ?"
        params.append(group)
    
    if priority:
        query += " AND priority = ?"
        params.append(priority)
    
    if tag:
        query += " AND tags LIKE ?"
        params.append(f'%{tag}%')
    
    query += " ORDER BY pinned DESC, favorite DESC, name ASC"
    
    c.execute(query, params)
    data = c.fetchall()
    conn.close()
    return data

def get_lab_tests(search=None, priority=None, tag=None):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    
    query = "SELECT * FROM lab_tests WHERE 1=1"
    params = []
    
    if search:
        query += " AND (name LIKE ? OR purpose LIKE ? OR tags LIKE ?)"
        params.extend([f'%{search}%'] * 3)
    
    if priority:
        query += " AND priority = ?"
        params.append(priority)
    
    if tag:
        query += " AND tags LIKE ?"
        params.append(f'%{tag}%')
    
    query += " ORDER BY pinned DESC, favorite DESC, name ASC"
    
    c.execute(query, params)
    data = c.fetchall()
    conn.close()
    return data

def toggle_favorite(table, id):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute(f"SELECT favorite FROM {table} WHERE id=?", (id,))
    current = c.fetchone()[0]
    new_val = 0 if current else 1
    c.execute(f"UPDATE {table} SET favorite=? WHERE id=?", (new_val, id))
    conn.commit()
    conn.close()
    if new_val:
        update_achievements('favorites')

def toggle_pin(table, id):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute(f"SELECT pinned FROM {table} WHERE id=?", (id,))
    current = c.fetchone()[0]
    new_val = 0 if current else 1
    c.execute(f"UPDATE {table} SET pinned=? WHERE id=?", (new_val, id))
    conn.commit()
    conn.close()

def undo_delete():
    if st.session_state.undo_stack:
        st.session_state.undo_stack.pop()
        return True
    return False

# ==================== MAIN APP ====================
def main():
    init_db()
    load_css()
    
    # License check
    if st.session_state.get('license_valid', False) and st.session_state.get('license_key'):
        status = license_system.check_license_status(
            st.session_state.license_key, 
            st.session_state.device_id
        )
        if status['status'] != 'active':
            st.session_state.license_valid = False
            st.warning("⚠️ لایسەنسەکە بەسەرچووە یان ناچالاک کراوە. تکایە دووبارە چالاک بکە!")
    
    # Show activation page if not licensed
    if not st.session_state.get('license_valid', False):
        show_license_activation()
        return
    
    # Main app
    update_achievements('study')
    
    st.markdown(f"""
    <div class="main-header">
        <h1>🏥 دکتۆر دانیال</h1>
        <p>❤️ بەخێربێیت، {st.session_state.username or 'بەکارهێنەر'}!</p>
        <div style="display: flex; justify-content: center; gap: 10px; margin-top: 10px; flex-wrap: wrap;">
            <span class="license-badge license-valid">🔑 لایسەنس چالاکە</span>
            <span class="color-label" style="background: #ff4757; color: white;">🏆 {st.session_state.achievements['study_days']} ڕۆژ</span>
            <span class="color-label" style="background: #2ed573; color: white;">📚 {st.session_state.achievements['items_added']} بابەت</span>
            <span class="color-label" style="background: #ffa502; color: white;">⭐ {st.session_state.achievements['favorites']} دڵخواز</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick actions
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("💊 + دەرمان", use_container_width=True):
            st.session_state.current_page = "💊 دەرمانەکان"
            st.rerun()
    with col2:
        if st.button("🧪 + پشکنین", use_container_width=True):
            st.session_state.current_page = "🧪 پشکنینەکان"
            st.rerun()
    with col3:
        if st.button("📝 + تێبینی", use_container_width=True):
            st.session_state.current_page = "📝 تێبینییەکان"
            st.rerun()
    with col4:
        if st.button("🔄 نوێکردنەوە", use_container_width=True):
            st.rerun()
    with col5:
        if st.button("↩️ گەڕاندنەوە", use_container_width=True):
            if undo_delete():
                st.rerun()
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 📚 ڕێبەرایەتی")
        
        pages = [
            "📊 داشبۆرد",
            "💊 دەرمانەکان",
            "🧪 پشکنینەکان",
            "📝 تێبینییەکان",
            "🎯 شێوازی خوێندن",
            "📐 حسابکەری پزیشکی",
            "📊 هیتماپ",
            "🏆 دەستکەوتەکان"
        ]
        
        if st.session_state.get('user_role') == 'admin':
            pages.extend(["🔑 لایسەنس", "👥 بەکارهێنەران"])
        pages.append("⚙️ ڕێکخستنەکان")
        
        for page in pages:
            if st.button(page, use_container_width=True, key=f"nav_{page}"):
                st.session_state.current_page = page
                st.rerun()
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚪 دەرچوون", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.license_valid = False
                st.session_state.license_key = None
                st.rerun()
        with col2:
            if st.button("🔄 فرێش", use_container_width=True):
                st.rerun()
    
    # Page routing
    page = st.session_state.current_page
    
    if page == "📊 داشبۆرد":
        show_dashboard()
    elif page == "💊 دەرمانەکان":
        show_medicines_page()
    elif page == "🧪 پشکنینەکان":
        show_lab_tests_page()
    elif page == "📝 تێبینییەکان":
        show_notes_page()
    elif page == "🎯 شێوازی خوێندن":
        show_study_mode_page()
    elif page == "📐 حسابکەری پزیشکی":
        show_calculators_page()
    elif page == "📊 هیتماپ":
        show_heatmap_page()
    elif page == "🏆 دەستکەوتەکان":
        show_achievements_page()
    elif page == "🔑 لایسەنس":
        show_license_manager()
    elif page == "👥 بەکارهێنەران":
        show_users_page()
    elif page == "⚙️ ڕێکخستنەکان":
        show_settings_page()

def show_dashboard():
    st.markdown("### 📊 داشبۆرد")
    
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM medicines")
    total_meds = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM lab_tests")
    total_tests = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM medicines WHERE favorite=1")
    fav_meds = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM lab_tests WHERE favorite=1")
    fav_tests = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM medicines WHERE pinned=1")
    pinned_meds = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM lab_tests WHERE pinned=1")
    pinned_tests = c.fetchone()[0]
    
    conn.close()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💊 دەرمانەکان", total_meds)
    with col2:
        st.metric("🧪 پشکنینەکان", total_tests)
    with col3:
        st.metric("⭐ دڵخوازەکان", fav_meds + fav_tests)
    with col4:
        st.metric("📌 پین کراوەکان", pinned_meds + pinned_tests)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        fig = go.Figure(data=[go.Pie(
            labels=['دەرمانەکان', 'پشکنینەکان'],
            values=[total_meds, total_tests],
            marker=dict(colors=['#667eea', '#764ba2']),
            hole=0.3
        )])
        fig.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        fig = go.Figure(data=[go.Bar(
            x=['دەرمان', 'پشکنین', 'دڵخواز', 'پین'],
            y=[total_meds, total_tests, fav_meds + fav_tests, pinned_meds + pinned_tests],
            marker_color=['#667eea', '#764ba2', '#ffa502', '#ff4757'],
            text=[total_meds, total_tests, fav_meds + fav_tests, pinned_meds + pinned_tests],
            textposition='auto'
        )])
        fig.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

def show_medicines_page():
    st.markdown("### 💊 دەرمانەکان")
    
    search = st.text_input("🔍 گەڕان", placeholder="ناو، براند، گەنەریک...")
    
    meds = get_medicines(search=search if search else None)
    
    if meds:
        for med in meds:
            with st.container():
                st.markdown(f"""
                <div class="glass-card">
                    <h4>{"📌 " if med[11] else ""}{"⭐ " if med[10] else ""}{med[1]}</h4>
                    <p><strong>براند:</strong> {med[2] or '-'} | <strong>گەنەریک:</strong> {med[3] or '-'}</p>
                    <p><strong>دۆز:</strong> {med[4] or '-'} | <strong>ڕێگا:</strong> {med[5] or '-'} | <strong>گرووپ:</strong> {med[6] or '-'}</p>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("⭐", key=f"fav_m_{med[0]}", use_container_width=True):
                        toggle_favorite('medicines', med[0])
                        st.rerun()
                with col2:
                    if st.button("📌", key=f"pin_m_{med[0]}", use_container_width=True):
                        toggle_pin('medicines', med[0])
                        st.rerun()
                with col3:
                    if st.button("ℹ️", key=f"info_m_{med[0]}", use_container_width=True):
                        st.info(f"تێبینی: {med[12] if len(med) > 12 else 'نییە'}")
    else:
        st.info("هیچ دەرمانێک نەدۆزرایەوە")

def show_lab_tests_page():
    st.markdown("### 🧪 پشکنینەکان")
    
    search = st.text_input("🔍 گەڕان", placeholder="ناو، ئامانج...")
    
    tests = get_lab_tests(search=search if search else None)
    
    if tests:
        for test in tests:
            with st.container():
                st.markdown(f"""
                <div class="glass-card">
                    <h4>{"📌 " if test[9] else ""}{"⭐ " if test[8] else ""}{test[1]}</h4>
                    <p><strong>ئامانج:</strong> {test[2] or '-'}</p>
                    <p><strong>نرخی ئاسایی:</strong> {test[3] or '-'}</p>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("⭐", key=f"fav_t_{test[0]}", use_container_width=True):
                        toggle_favorite('lab_tests', test[0])
                        st.rerun()
                with col2:
                    if st.button("📌", key=f"pin_t_{test[0]}", use_container_width=True):
                        toggle_pin('lab_tests', test[0])
                        st.rerun()
                with col3:
                    if st.button("ℹ️", key=f"info_t_{test[0]}", use_container_width=True):
                        st.info(f"ئامادەبوون: {test[4] or 'نییە'}")
    else:
        st.info("هیچ پشکنینێک نەدۆزرایەوە")

def show_notes_page():
    st.markdown("### 📝 تێبینییەکان")
    st.info("بەشی تێبینییەکان - لە وەشانی داهاتوودا زیاد دەکرێت")

def show_study_mode_page():
    st.markdown("### 🎯 شێوازی خوێندن")
    
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("SELECT 'medicine' as type, name, brand, generic, dose, route, group_name, notes FROM medicines ORDER BY RANDOM() LIMIT 1")
    med = c.fetchone()
    
    if not med:
        c.execute("SELECT 'lab_test' as type, name, purpose, normal_range, preparation, notes FROM lab_tests ORDER BY RANDOM() LIMIT 1")
        med = c.fetchone()
    
    conn.close()
    
    if med:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center; background: linear-gradient(145deg, #667eea, #764ba2); color: white;">
            <h2>{'💊' if med[0] == 'medicine' else '🧪'} {med[1]}</h2>
            <hr>
            <p><strong>{'براند' if med[0] == 'medicine' else 'ئامانج'}:</strong> {med[2] or '-'}</p>
            <p><strong>{'گەنەریک' if med[0] == 'medicine' else 'نرخی ئاسایی'}:</strong> {med[3] or '-'}</p>
            <p><strong>{'دۆز' if med[0] == 'medicine' else 'ئامادەبوون'}:</strong> {med[4] or '-'}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 کارتی داهاتوو", use_container_width=True):
            st.rerun()
    else:
        st.info("هیچ بابەتێک نییە بۆ خوێندن")

def show_calculators_page():
    st.markdown("### 📐 حسابکەری پزیشکی")
    
    calc_type = st.selectbox("جۆری حسابکەر", ["BMI", "BSA", "Creatinine Clearance", "Anion Gap"])
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    if calc_type == "BMI":
        col1, col2 = st.columns(2)
        with col1:
            weight = st.number_input("کێش (kg)", 1.0, 300.0, 70.0)
        with col2:
            height = st.number_input("باڵا (cm)", 50.0, 300.0, 175.0)
        
        if st.button("حسابکردن", use_container_width=True):
            bmi = weight / ((height/100) ** 2)
            status = "کێشی کەم" if bmi < 18.5 else "ئاسایی" if bmi < 25 else "زیاد" if bmi < 30 else "قەڵەوی"
            st.markdown(f"### BMI: {bmi:.1f} - {status}")
    
    elif calc_type == "BSA":
        col1, col2 = st.columns(2)
        with col1:
            weight = st.number_input("کێش (kg)", 1.0, 300.0, 70.0)
        with col2:
            height = st.number_input("باڵا (cm)", 50.0, 300.0, 175.0)
        
        if st.button("حسابکردن", use_container_width=True):
            bsa = ((height * weight) / 3600) ** 0.5
            st.markdown(f"### BSA: {bsa:.2f} m²")
    
    elif calc_type == "Creatinine Clearance":
        col1, col2, col3 = st.columns(3)
        with col1:
            age = st.number_input("تەمەن", 1, 120, 50)
        with col2:
            weight = st.number_input("کێش (kg)", 1.0, 300.0, 70.0)
        with col3:
            creatinine = st.number_input("کریاتینین (mg/dL)", 0.1, 20.0, 1.0)
        gender = st.selectbox("ڕەگەز", ["نێر", "مێ"])
        
        if st.button("حسابکردن", use_container_width=True):
            crcl = ((140 - age) * weight) / (72 * creatinine)
            if gender == "مێ":
                crcl *= 0.85
            st.markdown(f"### CrCl: {crcl:.1f} mL/min")
    
    elif calc_type == "Anion Gap":
        col1, col2, col3 = st.columns(3)
        with col1:
            na = st.number_input("Na", 100.0, 200.0, 140.0)
        with col2:
            cl = st.number_input("Cl", 50.0, 150.0, 100.0)
        with col3:
            hco3 = st.number_input("HCO3", 5.0, 50.0, 24.0)
        
        if st.button("حسابکردن", use_container_width=True):
            gap = na - (cl + hco3)
            st.markdown(f"### Anion Gap: {gap:.1f} mEq/L")
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_heatmap_page():
    st.markdown("### 📊 هیتماپی خوێندن")
    
    days = 90
    dates = [(datetime.now() - timedelta(days=i)).date() for i in range(days, 0, -1)]
    study_data = {date: random.randint(0, 5) for date in dates}
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    cols = st.columns(7)
    day_names = ['دووشەممە', 'سێشەممە', 'چوارشەممە', 'پێنجشەممە', 'هەینی', 'شەممە', 'یەکشەممە']
    
    for i, day in enumerate(day_names):
        with cols[i]:
            st.markdown(f"<small>{day}</small>", unsafe_allow_html=True)
    
    weeks = []
    for i in range(0, len(dates), 7):
        week = dates[i:i+7]
        weeks.append(week)
    
    for week in weeks[-12:]:
        cols = st.columns(7)
        for idx, date in enumerate(week):
            with cols[idx]:
                count = study_data.get(date, 0)
                color = {
                    0: '#ebedf0',
                    1: '#9be9a8',
                    2: '#40c463',
                    3: '#30a14e',
                    4: '#216e39',
                    5: '#1a4f2a'
                }.get(count, '#ebedf0')
                st.markdown(f"""
                <div style="background: {color}; width: 30px; height: 30px; border-radius: 4px; margin: 2px;" title="{date}"></div>
                """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_achievements_page():
    st.markdown("### 🏆 دەستکەوتەکان")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📅 ڕۆژانی خوێندن", st.session_state.achievements['study_days'])
    with col2:
        st.metric("📚 بابەتی زیادکراو", st.session_state.achievements['items_added'])
    with col3:
        st.metric("⭐ دڵخوازەکان", st.session_state.achievements['favorites'])
    
    badges = []
    if st.session_state.achievements['study_days'] >= 7:
        badges.append("🔥 7 ڕۆژ بەردەوامی")
    if st.session_state.achievements['study_days'] >= 30:
        badges.append("🌟 30 ڕۆژ بەردەوامی")
    if st.session_state.achievements['items_added'] >= 20:
        badges.append("📚 کتێبخانە")
    if st.session_state.achievements['favorites'] >= 10:
        badges.append("⭐ خوێندکاری زیرەک")
    
    if badges:
        for badge in badges:
            st.markdown(f"🏅 {badge}")
    else:
        st.info("💪 بەردەوام بە بۆ بەدەستهێنانی مەدالیاکان!")

def show_users_page():
    if st.session_state.get('user_role') != 'admin':
        st.error("⛔ تەنها بۆ بەڕێوەبەر")
        return
    
    st.markdown("### 👥 بەکارهێنەران")
    
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("SELECT id, username, role, created_at FROM users")
    users = c.fetchall()
    conn.close()
    
    for user in users:
        st.markdown(f"""
        <div class="glass-card">
            <h4>👤 {user[1]}</h4>
            <p>ڕۆڵ: {user[2]} | بەستوو: {user[3]}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with st.expander("➕ زیادکردنی بەکارهێنەر"):
        with st.form("add_user"):
            username = st.text_input("ناوی بەکارهێنەر")
            password = st.text_input("ووشەی نهێنی", type="password")
            role = st.selectbox("ڕۆڵ", ["user", "admin"])
            if st.form_submit_button("زیادکردن"):
                if username and password:
                    if add_user(username, password, role):
                        st.success("✅ زیادکرا!")
                        st.rerun()
                    else:
                        st.error("❌ ناوەکە هەیە!")

def show_settings_page():
    st.markdown("### ⚙️ ڕێکخستنەکان")
    
    dark_mode = st.toggle("🌙 ڕەوانەی تاریک", value=st.session_state.get('dark_mode', True))
    if dark_mode != st.session_state.dark_mode:
        st.session_state.dark_mode = dark_mode
        st.rerun()
    
    font_size = st.selectbox("قەبارەی دەق", ["small", "medium", "large", "xlarge"], 
                           index=["small", "medium", "large", "xlarge"].index(st.session_state.get('font_size', 'medium')))
    if font_size != st.session_state.font_size:
        st.session_state.font_size = font_size
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 💾 پشتگیری")
    if st.button("دروستکردنی پشتگیری", use_container_width=True):
        auto_backup()
        st.success("✅ پشتگیری دروستکرا!")
    
    st.markdown("---")
    st.markdown("### 📱 زانیاری ئامێر")
    st.code(f"Device ID: {st.session_state.device_id}")
    if st.session_state.get('license_key'):
        st.code(f"License: {st.session_state.license_key}")

# ==================== RUN APP ====================
if __name__ == "__main__":
    main()
