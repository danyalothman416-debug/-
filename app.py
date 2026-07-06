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

# ڕێکخستنی لاپەڕە
st.set_page_config(
    page_title="دکتر دانیال - خوێندنی پزیشکی",
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
        
        # Licenses table
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
        
        # Activation attempts
        c.execute('''CREATE TABLE IF NOT EXISTS activation_attempts
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      license_key TEXT,
                      device_id TEXT,
                      attempt_time TEXT,
                      status TEXT)''')
        
        conn.commit()
        conn.close()
    
    def generate_license_key(self, license_type='yearly', user_email=None):
        """دروستکردنی کۆدی لایسەنس"""
        # Format: DRD-XXXX-XXXX-XXXX
        prefix = "DRD"
        parts = []
        for i in range(3):
            part = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4))
            parts.append(part)
        license_key = f"{prefix}-{'-'.join(parts)}"
        
        # Save to database
        conn = sqlite3.connect(self.license_file)
        c = conn.cursor()
        
        now = datetime.now().isoformat()
        if license_type == 'yearly':
            expires = (datetime.now() + timedelta(days=365)).isoformat()
        elif license_type == 'lifetime':
            expires = '2099-12-31T23:59:59'
        else:
            expires = (datetime.now() + timedelta(days=30)).isoformat()
        
        c.execute("""INSERT INTO licenses 
                     (license_key, user_email, license_type, created_at, expires_at, is_active)
                     VALUES (?, ?, ?, ?, ?, 1)""",
                  (license_key, user_email, license_type, now, expires))
        
        conn.commit()
        conn.close()
        return license_key
    
    def activate_license(self, license_key, device_id):
        """چالاککردنی کۆدی لایسەنس"""
        conn = sqlite3.connect(self.license_file)
        c = conn.cursor()
        
        # Check if license exists and is active
        c.execute("SELECT * FROM licenses WHERE license_key=? AND is_active=1", (license_key,))
        license_data = c.fetchone()
        
        if not license_data:
            conn.close()
            return {'status': 'invalid', 'message': 'کۆدەکە نادروستە یان چالاک نییە'}
        
        # Check if expired
        expires_at = datetime.fromisoformat(license_data[5])
        if expires_at < datetime.now():
            c.execute("UPDATE licenses SET is_active=0 WHERE license_key=?", (license_key,))
            conn.commit()
            conn.close()
            return {'status': 'expired', 'message': 'کۆدەکە بەسەرچووە'}
        
        # Check if already used on another device
        c.execute("SELECT device_id FROM licenses WHERE license_key=? AND device_id IS NOT NULL", (license_key,))
        existing_device = c.fetchone()
        
        if existing_device and existing_device[0] != device_id:
            conn.close()
            return {'status': 'used', 'message': 'کۆدەکە لەسەر ئامێرێکی تر چالاک کراوە'}
        
        # Activate
        c.execute("UPDATE licenses SET device_id=?, last_used=? WHERE license_key=?",
                 (device_id, datetime.now().isoformat(), license_key))
        conn.commit()
        conn.close()
        
        return {'status': 'success', 'message': 'کۆد بە سەرکەوتوویی چالاک کرا'}
    
    def deactivate_license(self, license_key):
        """ناچالاککردنی کۆد"""
        conn = sqlite3.connect(self.license_file)
        c = conn.cursor()
        c.execute("UPDATE licenses SET is_active=0 WHERE license_key=?", (license_key,))
        conn.commit()
        conn.close()
        return True
    
    def check_license_status(self, license_key):
        """پشکنینی دۆخی کۆد"""
        conn = sqlite3.connect(self.license_file)
        c = conn.cursor()
        c.execute("SELECT * FROM licenses WHERE license_key=?", (license_key,))
        license_data = c.fetchone()
        conn.close()
        
        if not license_data:
            return {'status': 'not_found'}
        
        is_active = license_data[6] == 1
        expires_at = datetime.fromisoformat(license_data[5])
        is_expired = expires_at < datetime.now()
        
        if not is_active or is_expired:
            return {'status': 'inactive', 'expires_at': license_data[5]}
        
        return {'status': 'active', 'expires_at': license_data[5], 'device_id': license_data[2]}
    
    def generate_bulk_licenses(self, count, license_type='yearly'):
        """دروستکردنی چەندین کۆد بە یەک جار"""
        keys = []
        for _ in range(count):
            key = self.generate_license_key(license_type)
            keys.append(key)
        return keys

# ==================== INITIALIZE LICENSE SYSTEM ====================
license_system = LicenseSystem()

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
    # Create unique device ID
    import uuid
    st.session_state.device_id = str(uuid.uuid4())
if 'license_key' not in st.session_state:
    st.session_state.license_key = None
if 'license_valid' not in st.session_state:
    st.session_state.license_valid = False

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
            transform: translateY(-8px) scale(1.01);
            box-shadow: 0 15px 45px 0 {shadow_color};
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
            padding: 12px 24px;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            width: 100%;
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
        }}
        
        .license-valid {{
            background: #2ed573;
            color: white;
        }}
        
        .license-invalid {{
            background: #ff4757;
            color: white;
        }}
        
        @media print {{
            .stApp {{ background: white !important; }}
            .glass-card {{ background: white !important; border: 1px solid #ddd !important; }}
            .stButton, .stDownloadButton {{ display: none !important; }}
        }}
        
        @media (max-width: 768px) {{
            .glass-card {{ padding: 15px; margin: 8px 0; }}
            .main-header {{ padding: 20px; font-size: 20px; }}
        }}
    </style>
    """, unsafe_allow_html=True)

# ==================== DATABASE FUNCTIONS ====================
def init_db():
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    
    # Users
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE,
                  password TEXT,
                  role TEXT,
                  created_at TEXT)''')
    
    # Medicines
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
    
    # Lab tests
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
    
    # Test trends
    c.execute('''CREATE TABLE IF NOT EXISTS test_trends
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  test_id INTEGER,
                  value REAL,
                  date TEXT,
                  notes TEXT)''')
    
    # General notes
    c.execute('''CREATE TABLE IF NOT EXISTS general_notes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT,
                  content TEXT,
                  image_path TEXT,
                  link TEXT,
                  attachment_path TEXT,
                  tags TEXT,
                  created_at TEXT)''')
    
    # Note templates
    c.execute('''CREATE TABLE IF NOT EXISTS note_templates
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  content TEXT,
                  created_at TEXT)''')
    
    # Categories
    c.execute('''CREATE TABLE IF NOT EXISTS categories
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  color TEXT,
                  type TEXT,
                  created_at TEXT)''')
    
    # Reminders
    c.execute('''CREATE TABLE IF NOT EXISTS reminders
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT,
                  description TEXT,
                  reminder_date TEXT,
                  completed INTEGER DEFAULT 0,
                  created_at TEXT)''')
    
    # History
    c.execute('''CREATE TABLE IF NOT EXISTS history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  action TEXT,
                  table_name TEXT,
                  record_id INTEGER,
                  details TEXT,
                  created_at TEXT)''')
    
    # Check and add columns
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
    
    # Insert default categories
    default_categories = [
        ('دەرمانی گشتی', '#667eea', 'medicine'),
        ('دەرمانی دڵ', '#ff6b6b', 'medicine'),
        ('دەرمانی دەماغ', '#feca57', 'medicine'),
        ('پشکنینی خوێن', '#48dbfb', 'lab_test'),
        ('پشکنینی میز', '#1dd1a1', 'lab_test'),
        ('پشکنینی وێنە', '#5f27cd', 'lab_test')
    ]
    
    for name, color, type_ in default_categories:
        c.execute("SELECT * FROM categories WHERE name=?", (name,))
        if not c.fetchone():
            c.execute("INSERT INTO categories (name, color, type, created_at) VALUES (?, ?, ?, ?)",
                     (name, color, type_, datetime.now().isoformat()))
    
    # Insert default admin
    c.execute("SELECT * FROM users WHERE username='admin'")
    if not c.fetchone():
        hashed = hashlib.sha256('admin123'.encode()).hexdigest()
        c.execute("INSERT INTO users (username, password, role, created_at) VALUES (?, ?, ?, ?)",
                 ('admin', hashed, 'admin', datetime.now().isoformat()))
    
    conn.commit()
    conn.close()

# ==================== LICENSE CHECK DECORATOR ====================
def require_license(func):
    """دکۆراتۆر بۆ پشکنینی لایسەنس پێش کارکردن"""
    def wrapper(*args, **kwargs):
        if not st.session_state.get('license_valid', False):
            st.error("⛔ تکایە یەکەم جار کۆدی لایسەنسەکەت چالاک بکە!")
            return None
        return func(*args, **kwargs)
    return wrapper

# ==================== CRUD FUNCTIONS ====================
def add_medicine(name, brand, generic, dose, route, group_name, priority, color_label, tags, notes):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute("""INSERT INTO medicines 
                 (name, brand, generic, dose, route, group_name, priority, color_label, tags, notes, created_at, updated_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
              (name, brand, generic, dose, route, group_name, priority, color_label, tags, notes, now, now))
    id = c.lastrowid
    conn.commit()
    conn.close()
    add_history('CREATE', 'medicines', id, f'Added medicine: {name}')
    update_achievements('items_added')
    auto_backup()
    return id

def get_medicines(search=None, group=None, priority=None, tag=None):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    
    query = "SELECT * FROM medicines"
    params = []
    conditions = []
    
    if search:
        conditions.append("(name LIKE ? OR brand LIKE ? OR generic LIKE ? OR tags LIKE ?)")
        params.extend([f'%{search}%', f'%{search}%', f'%{search}%', f'%{search}%'])
    
    if group:
        conditions.append("group_name = ?")
        params.append(group)
    
    if priority:
        conditions.append("priority = ?")
        params.append(priority)
    
    if tag:
        conditions.append("tags LIKE ?")
        params.append(f'%{tag}%')
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY pinned DESC, favorite DESC, priority DESC, name ASC"
    
    c.execute(query, params)
    data = c.fetchall()
    conn.close()
    return data

def update_medicine(id, name, brand, generic, dose, route, group_name, priority, color_label, tags, notes):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute("""UPDATE medicines 
                 SET name=?, brand=?, generic=?, dose=?, route=?, 
                     group_name=?, priority=?, color_label=?, tags=?, notes=?, updated_at=?
                 WHERE id=?""",
              (name, brand, generic, dose, route, group_name, priority, color_label, tags, notes, now, id))
    conn.commit()
    conn.close()
    add_history('UPDATE', 'medicines', id, f'Updated medicine: {name}')
    auto_backup()

def delete_medicine(id):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("SELECT name FROM medicines WHERE id=?", (id,))
    result = c.fetchone()
    if result:
        name = result[0]
        c.execute("DELETE FROM medicines WHERE id=?", (id,))
        conn.commit()
        conn.close()
        add_history('DELETE', 'medicines', id, f'Deleted medicine: {name}')
        st.session_state.undo_stack.append(('medicine', id, name))
        auto_backup()

def toggle_pin_medicine(id):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("SELECT pinned FROM medicines WHERE id=?", (id,))
    current = c.fetchone()[0]
    new_val = 0 if current else 1
    c.execute("UPDATE medicines SET pinned=? WHERE id=?", (new_val, id))
    conn.commit()
    conn.close()

def toggle_favorite_medicine(id):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("SELECT favorite FROM medicines WHERE id=?", (id,))
    current = c.fetchone()[0]
    new_val = 0 if current else 1
    c.execute("UPDATE medicines SET favorite=? WHERE id=?", (new_val, id))
    conn.commit()
    conn.close()
    if new_val:
        update_achievements('favorites')

# Lab tests
def add_lab_test(name, purpose, normal_range, preparation, priority, color_label, tags, notes):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute("""INSERT INTO lab_tests 
                 (name, purpose, normal_range, preparation, priority, color_label, tags, notes, created_at, updated_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
              (name, purpose, normal_range, preparation, priority, color_label, tags, notes, now, now))
    id = c.lastrowid
    conn.commit()
    conn.close()
    add_history('CREATE', 'lab_tests', id, f'Added lab test: {name}')
    update_achievements('items_added')
    auto_backup()
    return id

def get_lab_tests(search=None, priority=None, tag=None):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    
    query = "SELECT * FROM lab_tests"
    params = []
    conditions = []
    
    if search:
        conditions.append("(name LIKE ? OR purpose LIKE ? OR tags LIKE ?)")
        params.extend([f'%{search}%', f'%{search}%', f'%{search}%'])
    
    if priority:
        conditions.append("priority = ?")
        params.append(priority)
    
    if tag:
        conditions.append("tags LIKE ?")
        params.append(f'%{tag}%')
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY pinned DESC, favorite DESC, priority DESC, name ASC"
    
    c.execute(query, params)
    data = c.fetchall()
    conn.close()
    return data

def update_lab_test(id, name, purpose, normal_range, preparation, priority, color_label, tags, notes):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute("""UPDATE lab_tests 
                 SET name=?, purpose=?, normal_range=?, preparation=?, priority=?, color_label=?, tags=?, notes=?, updated_at=?
                 WHERE id=?""",
              (name, purpose, normal_range, preparation, priority, color_label, tags, notes, now, id))
    conn.commit()
    conn.close()
    add_history('UPDATE', 'lab_tests', id, f'Updated lab test: {name}')
    auto_backup()

def delete_lab_test(id):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("SELECT name FROM lab_tests WHERE id=?", (id,))
    result = c.fetchone()
    if result:
        name = result[0]
        c.execute("DELETE FROM lab_tests WHERE id=?", (id,))
        conn.commit()
        conn.close()
        add_history('DELETE', 'lab_tests', id, f'Deleted lab test: {name}')
        st.session_state.undo_stack.append(('lab_test', id, name))
        auto_backup()

def toggle_pin_lab_test(id):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("SELECT pinned FROM lab_tests WHERE id=?", (id,))
    current = c.fetchone()[0]
    new_val = 0 if current else 1
    c.execute("UPDATE lab_tests SET pinned=? WHERE id=?", (new_val, id))
    conn.commit()
    conn.close()

def toggle_favorite_lab_test(id):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("SELECT favorite FROM lab_tests WHERE id=?", (id,))
    current = c.fetchone()[0]
    new_val = 0 if current else 1
    c.execute("UPDATE lab_tests SET favorite=? WHERE id=?", (new_val, id))
    conn.commit()
    conn.close()
    if new_val:
        update_achievements('favorites')

def toggle_favorite(table, id):
    if table == 'medicines':
        toggle_favorite_medicine(id)
    elif table == 'lab_tests':
        toggle_favorite_lab_test(id)

def toggle_pin(table, id):
    if table == 'medicines':
        toggle_pin_medicine(id)
    elif table == 'lab_tests':
        toggle_pin_lab_test(id)

# History
def add_history(action, table_name, record_id, details):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO history (action, table_name, record_id, details, created_at) VALUES (?, ?, ?, ?, ?)",
             (action, table_name, record_id, details, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_history(limit=50):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("SELECT * FROM history ORDER BY created_at DESC LIMIT ?", (limit,))
    data = c.fetchall()
    conn.close()
    return data

# Templates
def add_template(name, content):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO note_templates (name, content, created_at) VALUES (?, ?, ?)",
             (name, content, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_templates():
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("SELECT * FROM note_templates ORDER BY name")
    data = c.fetchall()
    conn.close()
    return data

def delete_template(id):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("DELETE FROM note_templates WHERE id=?", (id,))
    conn.commit()
    conn.close()

# Reminders
def add_reminder(title, description, reminder_date):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO reminders (title, description, reminder_date, created_at) VALUES (?, ?, ?, ?)",
             (title, description, reminder_date, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_reminders(show_completed=False):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    if show_completed:
        c.execute("SELECT * FROM reminders ORDER BY reminder_date")
    else:
        c.execute("SELECT * FROM reminders WHERE completed=0 ORDER BY reminder_date")
    data = c.fetchall()
    conn.close()
    return data

def complete_reminder(id):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("UPDATE reminders SET completed=1 WHERE id=?", (id,))
    conn.commit()
    conn.close()

# General notes
def add_general_note(title, content, image_path=None, link=None, attachment_path=None, tags=None):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute("""INSERT INTO general_notes 
                 (title, content, image_path, link, attachment_path, tags, created_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?)""",
             (title, content, image_path, link, attachment_path, tags, now))
    conn.commit()
    conn.close()
    auto_backup()

def get_general_notes():
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("SELECT * FROM general_notes ORDER BY created_at DESC")
    data = c.fetchall()
    conn.close()
    return data

def delete_general_note(id):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("DELETE FROM general_notes WHERE id=?", (id,))
    conn.commit()
    conn.close()
    auto_backup()

# Achievements
def update_achievements(type_):
    today = datetime.now().date()
    if st.session_state.achievements['last_study_date'] != str(today):
        st.session_state.achievements['study_days'] += 1
        st.session_state.achievements['last_study_date'] = str(today)
    
    if type_ == 'items_added':
        st.session_state.achievements['items_added'] += 1
    elif type_ == 'favorites':
        st.session_state.achievements['favorites'] += 1

# Auto backup
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

# Medical Calculators
def calculate_bmi(weight, height):
    height_m = height / 100
    return weight / (height_m ** 2)

def calculate_bsa(weight, height):
    return ((height * weight) / 3600) ** 0.5

def calculate_creatinine_clearance(age, weight, creatinine, gender):
    if gender == 'male':
        return ((140 - age) * weight) / (72 * creatinine)
    else:
        return ((140 - age) * weight) * 0.85 / (72 * creatinine)

def calculate_anion_gap(na, cl, hco3):
    return na - (cl + hco3)

def calculate_corrected_calcium(calcium, albumin):
    return calcium + 0.8 * (4 - albumin)

def calculate_sodium_correction(na, glucose):
    return na + 0.016 * (glucose - 100)

def calculate_iv_drip_rate(volume, time, drop_factor):
    return (volume * drop_factor) / (time * 60)

# Authentication
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

# Export functions
def export_to_pdf(data, title):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#667eea'),
        alignment=1
    )
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 20))
    
    if data:
        headers = list(data[0].keys())
        table_data = [headers]
        for row in data:
            table_data.append([str(row.get(h, '')) for h in headers])
        
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def undo_delete():
    if st.session_state.undo_stack:
        item = st.session_state.undo_stack.pop()
        st.success(f"✅ {item[2]} گەڕێنرایەوە!")
        return True
    return False

def get_random_study_item():
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    
    c.execute("SELECT 'medicine' as type, id, name, brand, generic, dose, route, group_name, priority, notes FROM medicines")
    medicines = c.fetchall()
    
    c.execute("SELECT 'lab_test' as type, id, name, purpose, normal_range, preparation, priority, notes FROM lab_tests")
    lab_tests = c.fetchall()
    
    conn.close()
    
    all_items = list(medicines) + list(lab_tests)
    if all_items:
        return random.choice(all_items)
    return None

def get_categories(type_=None):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    if type_:
        c.execute("SELECT * FROM categories WHERE type=? ORDER BY name", (type_,))
    else:
        c.execute("SELECT * FROM categories ORDER BY name")
    data = c.fetchall()
    conn.close()
    return data

def add_category(name, color, type_):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO categories (name, color, type, created_at) VALUES (?, ?, ?, ?)",
             (name, color, type_, datetime.now().isoformat()))
    conn.commit()
    conn.close()

# ==================== LICENSE MANAGEMENT UI ====================
def show_license_manager():
    st.markdown("### 🔑 بەڕێوەبەری لایسەنس")
    
    tab1, tab2, tab3 = st.tabs(["🔑 چالاککردن", "📋 دروستکردنی کۆد", "📊 ئامار"])
    
    with tab1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("🔑 چالاککردنی لایسەنس")
        
        license_key = st.text_input("کۆدی لایسەنسەکەت بنووسە", placeholder="DRD-XXXX-XXXX-XXXX")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ چالاککردن", use_container_width=True):
                if license_key:
                    result = license_system.activate_license(license_key, st.session_state.device_id)
                    if result['status'] == 'success':
                        st.session_state.license_key = license_key
                        st.session_state.license_valid = True
                        st.success(f"✅ {result['message']}")
                        st.rerun()
                    else:
                        st.error(f"❌ {result['message']}")
                else:
                    st.warning("تکایە کۆدەکە بنووسە")
        
        with col2:
            if st.button("🔍 پشکنینی دۆخ", use_container_width=True):
                if license_key:
                    status = license_system.check_license_status(license_key)
                    if status['status'] == 'active':
                        st.success(f"✅ چالاکە - بەسەر دەچێت لە: {status['expires_at']}")
                    else:
                        st.error("❌ ناچالاکە یان بەسەرچووە")
                else:
                    st.warning("تکایە کۆدەکە بنووسە")
        
        # Show current license status
        if st.session_state.get('license_valid', False):
            st.markdown(f"""
            <div style="background: #2ed573; padding: 15px; border-radius: 15px; color: white; text-align: center; margin-top: 10px;">
                <h4>✅ لایسەنس چالاکە</h4>
                <p>کۆد: {st.session_state.license_key}</p>
                <p>ئامێر: {st.session_state.device_id[:8]}...</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📋 دروستکردنی کۆدی نوێ")
        
        st.warning("⚠️ ئەم بەشە تەنها بۆ بەڕێوەبەرە!")
        
        if st.session_state.get('user_role') == 'admin':
            license_type = st.selectbox("جۆری لایسەنس", ["yearly", "lifetime", "monthly"])
            user_email = st.text_input("ئیمەیڵی بەکارهێنەر")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("➕ دروستکردنی کۆد", use_container_width=True):
                    if user_email:
                        new_key = license_system.generate_license_key(license_type, user_email)
                        st.success(f"✅ کۆدی نوێ دروستکرا!")
                        st.code(f"{new_key}")
                        st.info(f"ئیمەیڵ: {user_email}")
                    else:
                        st.warning("تکایە ئیمەیڵ بنووسە")
            
            with col2:
                count = st.number_input("ژمارەی کۆد", min_value=1, max_value=100, value=10)
                if st.button("📦 دروستکردنی کۆدەکان", use_container_width=True):
                    keys = license_system.generate_bulk_licenses(count, license_type)
                    st.success(f"✅ {count} کۆد دروستکرا!")
                    for key in keys:
                        st.code(f"{key}")
        else:
            st.info("🔒 تەنها بۆ بەڕێوەبەرە")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📊 ئاماری لایسەنس")
        
        conn = sqlite3.connect('licenses.db')
        c = conn.cursor()
        
        c.execute("SELECT COUNT(*) FROM licenses")
        total = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM licenses WHERE is_active=1")
        active = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM licenses WHERE device_id IS NOT NULL")
        used = c.fetchone()[0]
        
        conn.close()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📦 کۆی کۆدەکان", total)
        with col2:
            st.metric("✅ کۆدی چالاک", active)
        with col3:
            st.metric("💻 کۆدی بەکارهێنراو", used)
        
        st.markdown('</div>', unsafe_allow_html=True)

# ==================== MAIN APP ====================
def main():
    init_db()
    load_css()
    
    # Session state init
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = ''
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = True
    if 'current_page' not in st.session_state:
        st.session_state.current_page = '📊 داشبۆرد'
    if 'font_size' not in st.session_state:
        st.session_state.font_size = 'medium'
    if 'language' not in st.session_state:
        st.session_state.language = 'کوردی'
    
    # Auto backup
    if not hasattr(st.session_state, 'last_backup'):
        st.session_state.last_backup = datetime.now()
    elif (datetime.now() - st.session_state.last_backup).seconds > 600:
        auto_backup()
        st.session_state.last_backup = datetime.now()
    
    # Update achievements
    update_achievements('study')
    
    # Check license validity
    if st.session_state.get('license_valid', False) and st.session_state.get('license_key'):
        status = license_system.check_license_status(st.session_state.license_key)
        if status['status'] != 'active':
            st.session_state.license_valid = False
            st.warning("⚠️ لایسەنسەکە بەسەرچووە یان ناچالاک کراوە. تکایە دووبارە چالاک بکە!")
    
    # LICENSE CHECK - Show activation if not valid
    if not st.session_state.get('license_valid', False):
        st.markdown("""
        <div class="main-header">
            <h1>🏥 دکتر دانیال</h1>
            <p>پلاتفۆرمی خوێندنی پزیشکی - پرۆفیشناڵ</p>
        </div>
        """, unsafe_allow_html=True)
        
        show_license_manager()
        
        # Try to login for admin
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.expander("👤 چوونەژوورەوە بۆ بەڕێوەبەر"):
                username = st.text_input("ناوی بەکارهێنەر")
                password = st.text_input("ووشەی نهێنی", type="password")
                if st.button("🔓 چوونەژوورەوە"):
                    user = check_login(username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.user_id = user[0]
                        st.session_state.user_role = user[3]
                        st.rerun()
                    else:
                        st.error("❌ هەڵە!")
        
        st.warning("""
        ⚠️ تکایە یەکەم جار لایسەنسەکەت چالاک بکە!
        
        - ئەگەر کۆدت نییە، پەیوەندی بە بەڕێوەبەرەوە بکە
        - کۆدەکە لە فۆرماتی **DRD-XXXX-XXXX-XXXX** دەبێت
        """)
        return
    
    # Main app - Only visible with valid license
    st.markdown(f"""
    <div class="main-header">
        <h1>🏥 دکتر دانیال</h1>
        <p>❤️ بەخێربێیت، {st.session_state.username}!</p>
        <p style="font-size: 14px; opacity: 0.8;">📅 {datetime.now().strftime('%A, %B %d, %Y')}</p>
        <div style="display: flex; justify-content: center; gap: 10px; margin-top: 10px; flex-wrap: wrap;">
            <span class="license-badge license-valid">🔑 {st.session_state.license_key[:12]}...</span>
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
        if st.button("📌 + پین", use_container_width=True):
            st.info("بابەتەکانت پین بکە بۆ ئاسانی دۆزینەوە")
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
            "📐 پزیشکی پزیشکی",
            "📊 هیتماپ",
            "🏆 دەستکەوتەکان"
        ]
        
        if st.session_state.get('user_role') == 'admin':
            pages.append("🔑 لایسەنس")
            pages.append("👥 بەکارهێنەران")
        pages.append("⚙️ ڕێکخستنەکان")
        
        for page in pages:
            if st.button(page, use_container_width=True):
                st.session_state.current_page = page
                st.rerun()
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🖨️ چاپ", use_container_width=True):
                st.write('<script>window.print();</script>', unsafe_allow_html=True)
        with col2:
            if st.button("🚪 دەرچوون", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.username = ''
                st.session_state.license_valid = False
                st.rerun()
    
    # Page content
    page = st.session_state.current_page
    
    if page == "📊 داشبۆرد":
        show_dashboard()
    elif page == "💊 دەرمانەکان":
        show_medicines()
    elif page == "🧪 پشکنینەکان":
        show_lab_tests()
    elif page == "📝 تێبینییەکان":
        show_notes()
    elif page == "🎯 شێوازی خوێندن":
        show_study_mode()
    elif page == "📐 پزیشکی پزیشکی":
        show_medical_calculators()
    elif page == "📊 هیتماپ":
        show_heatmap()
    elif page == "🏆 دەستکەوتەکان":
        show_achievements()
    elif page == "🔑 لایسەنس" and st.session_state.get('user_role') == 'admin':
        show_license_manager()
    elif page == "👥 بەکارهێنەران" and st.session_state.get('user_role') == 'admin':
        show_users()
    elif page == "⚙️ ڕێکخستنەکان":
        show_settings()

# ==================== PAGE FUNCTIONS ====================
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
        st.markdown(f"""
        <div class="glass-card" style="text-align: center;">
            <h2 style="font-size: 40px;">💊</h2>
            <h3>{total_meds}</h3>
            <p>دەرمانەکان</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center;">
            <h2 style="font-size: 40px;">🧪</h2>
            <h3>{total_tests}</h3>
            <p>پشکنینەکان</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center;">
            <h2 style="font-size: 40px;">⭐</h2>
            <h3>{fav_meds + fav_tests}</h3>
            <p>دڵخوازەکان</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center;">
            <h2 style="font-size: 40px;">📌</h2>
            <h3>{pinned_meds + pinned_tests}</h3>
            <p>پین کراوەکان</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📈 دابەشکردن")
        fig = go.Figure(data=[go.Pie(
            labels=['دەرمانەکان', 'پشکنینەکان'],
            values=[total_meds, total_tests],
            marker=dict(colors=['#667eea', '#764ba2']),
            hole=0.3
        )])
        fig.update_layout(showlegend=True, height=300, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("⭐ دڵخوازەکان")
        fig = go.Figure(data=[go.Bar(
            x=['دەرمانەکان', 'پشکنینەکان'],
            y=[fav_meds, fav_tests],
            marker_color=['#667eea', '#764ba2'],
            text=[fav_meds, fav_tests],
            textposition='auto'
        )])
        fig.update_layout(showlegend=False, height=300, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

def show_medicines():
    st.markdown("### 💊 بەڕێوەبەری دەرمانەکان")
    
    tab1, tab2, tab3 = st.tabs(["📋 بینین", "➕ زیادکردن", "🔍 گەڕان"])
    
    with tab1:
        st.markdown("#### هەموو دەرمانەکان")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            priority_filter = st.selectbox("فلتەر بە پریۆریتی", ["هەموو", "high", "medium", "low"])
        with col2:
            tag_filter = st.text_input("فلتەر بە تەگ", placeholder="تەگێک بنووسە...")
        with col3:
            if st.button("🔄 ڕێکخستنەوە", use_container_width=True):
                st.rerun()
        
        priority = None if priority_filter == "هەموو" else priority_filter
        meds = get_medicines(priority=priority, tag=tag_filter if tag_filter else None)
        
        if meds:
            for med in meds:
                priority_val = med[7] if len(med) > 7 else 'medium'
                color_label = med[8] if len(med) > 8 else '#667eea'
                favorite = med[10] if len(med) > 10 else 0
                pinned = med[11] if len(med) > 11 else 0
                tags = med[9] if len(med) > 9 else ''
                notes = med[12] if len(med) > 12 else ''
                
                priority_class = f"priority-{priority_val}" if priority_val else ""
                st.markdown(f"""
                <div class="glass-card {priority_class}">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h3>{"📌 " if pinned else ""}{"⭐ " if favorite else ""}{med[1]}</h3>
                        <div>
                            <span class="color-label" style="background: {color_label or '#667eea'}; color: white;">{color_label or 'گشتی'}</span>
                            <span class="color-label" style="background: {'#ff4757' if priority_val=='high' else '#ffa502' if priority_val=='medium' else '#2ed573'}; color: white;">{priority_val or 'medium'}</span>
                        </div>
                    </div>
                    <p><strong>🏷️ براند:</strong> {med[2]} | <strong>🔬 گەنەریک:</strong> {med[3]}</p>
                    <p><strong>💊 دۆز:</strong> {med[4]} | <strong>🔄 ڕێگا:</strong> {med[5]}</p>
                    <p><strong>📂 گرووپ:</strong> {med[6]}</p>
                    {f'<p><strong>🏷️ تەگەکان:</strong> {tags}</p>' if tags else ''}
                    <p><strong>📝 تێبینی:</strong> {notes}</p>
                    <div style="display: flex; gap: 10px; margin-top: 10px; flex-wrap: wrap;">
                """, unsafe_allow_html=True)
                
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    if st.button(f"⭐", key=f"fav_med_{med[0]}"):
                        toggle_favorite('medicines', med[0])
                        st.rerun()
                with col2:
                    if st.button(f"📌", key=f"pin_med_{med[0]}"):
                        toggle_pin('medicines', med[0])
                        st.rerun()
                with col3:
                    if st.button(f"✏️", key=f"edit_med_{med[0]}"):
                        st.session_state.edit_med = med
                        show_edit_medicine(med)
                with col4:
                    if st.button(f"🗑️", key=f"del_med_{med[0]}"):
                        delete_medicine(med[0])
                        st.rerun()
                with col5:
                    if st.button(f"📋", key=f"copy_med_{med[0]}"):
                        st.info("کۆپی کرا!")
                
                st.markdown("</div></div>", unsafe_allow_html=True)
        else:
            st.info("📝 هیچ دەرمانێک نەدۆزرایەوە.")
    
    with tab2:
        st.markdown("#### زیادکردنی دەرمانی نوێ")
        with st.form("add_medicine_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("ناوی دەرمان *")
                brand = st.text_input("براند")
                generic = st.text_input("گەنەریک")
                dose = st.text_input("دۆز")
            with col2:
                route = st.selectbox("ڕێگا", ["خواردنەوە", "IV", "IM", "ژێر پێست", "سەرپێست", "هەڵمکردن", "تر"])
                group = st.selectbox("گرووپ", ["دەردشکێن", "ئانتیبایۆتیک", "دەرمانی خەمۆکی", "دەرمانی فشاری خوێن", 
                                              "دەرمانی شەکەری خوێن", "دەرمانی هەستەوەری", "دەرمانی ترشەمێر", "ڤیتامینەکان", "تر"])
                priority = st.selectbox("پریۆریتی", ["high", "medium", "low"])
                color_label = st.selectbox("ڕەنگی لیبڵ", ["#667eea", "#ff6b6b", "#feca57", "#48dbfb", "#1dd1a1", "#5f27cd", "#ff9ff3"])
                tags = st.text_input("تەگەکان (بە کۆما جیابکەوە)", placeholder="مثال: دڵ, فشاری خوێن, شەکرە")
                notes = st.text_area("تێبینی")
            
            submitted = st.form_submit_button("💊 زیادکردنی دەرمان")
            if submitted and name:
                add_medicine(name, brand, generic, dose, route, group, priority, color_label, tags, notes)
                st.success("✅ دەرمان بە سەرکەوتوویی زیادکرا!")
                st.rerun()
    
    with tab3:
        st.markdown("#### گەڕانی پێشکەوتوو")
        search_term = st.text_input("گەڕان بە ناو، براند، گەنەریک، یان تەگ")
        if search_term:
            results = get_medicines(search=search_term)
            if results:
                for med in results:
                    st.markdown(f"""
                    <div class="glass-card">
                        <h4>{med[1]}</h4>
                        <p><strong>براند:</strong> {med[2]} | <strong>گەنەریک:</strong> {med[3]}</p>
                        <p><strong>تەگەکان:</strong> {med[9] if len(med) > 9 else ''}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("هیچ ئەنجامێک نەدۆزرایەوە!")

def show_edit_medicine(med):
    """Display edit form for medicine"""
    with st.expander(f"✏️ دەستکاری: {med[1]}"):
        with st.form(f"edit_med_form_{med[0]}"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("ناوی دەرمان", value=med[1])
                brand = st.text_input("براند", value=med[2] if med[2] else '')
                generic = st.text_input("گەنەریک", value=med[3] if med[3] else '')
                dose = st.text_input("دۆز", value=med[4] if med[4] else '')
            with col2:
                route = st.selectbox("ڕێگا", ["خواردنەوە", "IV", "IM", "ژێر پێست", "سەرپێست", "هەڵمکردن", "تر"], 
                                   index=["خواردنەوە", "IV", "IM", "ژێر پێست", "سەرپێست", "هەڵمکردن", "تر"].index(med[5]) if med[5] in ["خواردنەوە", "IV", "IM", "ژێر پێست", "سەرپێست", "هەڵمکردن", "تر"] else 0)
                group = st.selectbox("گرووپ", ["دەردشکێن", "ئانتیبایۆتیک", "دەرمانی خەمۆکی", "دەرمانی فشاری خوێن", 
                                              "دەرمانی شەکەری خوێن", "دەرمانی هەستەوەری", "دەرمانی ترشەمێر", "ڤیتامینەکان", "تر"],
                                   index=["دەردشکێن", "ئانتیبایۆتیک", "دەرمانی خەمۆکی", "دەرمانی فشاری خوێن", 
                                         "دەرمانی شەکەری خوێن", "دەرمانی هەستەوەری", "دەرمانی ترشەمێر", "ڤیتامینەکان", "تر"].index(med[6]) if med[6] in ["دەردشکێن", "ئانتیبایۆتیک", "دەرمانی خەمۆکی", "دەرمانی فشاری خوێن", 
                                         "دەرمانی شەکەری خوێن", "دەرمانی هەستەوەری", "دەرمانی ترشەمێر", "ڤیتامینەکان", "تر"] else 0)
                priority = st.selectbox("پریۆریتی", ["high", "medium", "low"], 
                                      index=["high", "medium", "low"].index(med[7]) if med[7] in ["high", "medium", "low"] else 1)
                color_label = st.selectbox("ڕەنگی لیبڵ", ["#667eea", "#ff6b6b", "#feca57", "#48dbfb", "#1dd1a1", "#5f27cd", "#ff9ff3"],
                                         index=["#667eea", "#ff6b6b", "#feca57", "#48dbfb", "#1dd1a1", "#5f27cd", "#ff9ff3"].index(med[8]) if med[8] in ["#667eea", "#ff6b6b", "#feca57", "#48dbfb", "#1dd1a1", "#5f27cd", "#ff9ff3"] else 0)
                tags = st.text_input("تەگەکان", value=med[9] if len(med) > 9 and med[9] else '')
                notes = st.text_area("تێبینی", value=med[12] if len(med) > 12 else '')
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("💾 پاشەکەوتکردن"):
                    update_medicine(med[0], name, brand, generic, dose, route, group, priority, color_label, tags, notes)
                    st.success("✅ دەرمان نوێکرایەوە!")
                    st.session_state.pop('edit_med', None)
                    st.rerun()
            with col2:
                if st.form_submit_button("❌ پەشیمانبوونەوە"):
                    st.session_state.pop('edit_med', None)
                    st.rerun()

def show_lab_tests():
    st.markdown("### 🧪 بەڕێوەبەری پشکنینەکان")
    
    tab1, tab2, tab3 = st.tabs(["📋 بینین", "➕ زیادکردن", "🔍 گەڕان"])
    
    with tab1:
        st.markdown("#### هەموو پشکنینەکان")
        
        col1, col2 = st.columns(2)
        with col1:
            priority_filter = st.selectbox("فلتەر بە پریۆریتی", ["هەموو", "high", "medium", "low"])
        with col2:
            tag_filter = st.text_input("فلتەر بە تەگ", placeholder="تەگێک بنووسە...")
        
        priority = None if priority_filter == "هەموو" else priority_filter
        tests = get_lab_tests(priority=priority, tag=tag_filter if tag_filter else None)
        
        if tests:
            for test in tests:
                priority_val = test[5] if len(test) > 5 else 'medium'
                color_label = test[6] if len(test) > 6 else '#667eea'
                favorite = test[8] if len(test) > 8 else 0
                pinned = test[9] if len(test) > 9 else 0
                tags = test[7] if len(test) > 7 else ''
                notes = test[10] if len(test) > 10 else ''
                
                priority_class = f"priority-{priority_val}" if priority_val else ""
                st.markdown(f"""
                <div class="glass-card {priority_class}">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h3>{"📌 " if pinned else ""}{"⭐ " if favorite else ""}{test[1]}</h3>
                        <div>
                            <span class="color-label" style="background: {color_label or '#667eea'}; color: white;">{color_label or 'گشتی'}</span>
                            <span class="color-label" style="background: {'#ff4757' if priority_val=='high' else '#ffa502' if priority_val=='medium' else '#2ed573'}; color: white;">{priority_val or 'medium'}</span>
                        </div>
                    </div>
                    <p><strong>🎯 ئامانج:</strong> {test[2]}</p>
                    <p><strong>📊 نرخی ئاسایی:</strong> {test[3]}</p>
                    <p><strong>🧑‍⚕️ ئامادەبوونی نەخۆش:</strong> {test[4]}</p>
                    {f'<p><strong>🏷️ تەگەکان:</strong> {tags}</p>' if tags else ''}
                    <p><strong>📝 تێبینی:</strong> {notes}</p>
                    <div style="display: flex; gap: 10px; margin-top: 10px; flex-wrap: wrap;">
                """, unsafe_allow_html=True)
                
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    if st.button(f"⭐", key=f"fav_test_{test[0]}"):
                        toggle_favorite('lab_tests', test[0])
                        st.rerun()
                with col2:
                    if st.button(f"📌", key=f"pin_test_{test[0]}"):
                        toggle_pin('lab_tests', test[0])
                        st.rerun()
                with col3:
                    if st.button(f"✏️", key=f"edit_test_{test[0]}"):
                        st.session_state.edit_test = test
                        show_edit_lab_test(test)
                with col4:
                    if st.button(f"🗑️", key=f"del_test_{test[0]}"):
                        delete_lab_test(test[0])
                        st.rerun()
                with col5:
                    if st.button(f"📋", key=f"copy_test_{test[0]}"):
                        st.info("کۆپی کرا!")
                
                st.markdown("</div></div>", unsafe_allow_html=True)
        else:
            st.info("📝 هیچ پشکنینێک نەدۆزرایەوە.")
    
    with tab2:
        st.markdown("#### زیادکردنی پشکنینی نوێ")
        with st.form("add_test_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("ناوی پشکنین *")
                purpose = st.text_area("ئامانج")
                normal_range = st.text_input("نرخی ئاسایی")
            with col2:
                preparation = st.text_area("ئامادەبوونی نەخۆش")
                priority = st.selectbox("پریۆریتی", ["high", "medium", "low"])
                color_label = st.selectbox("ڕەنگی لیبڵ", ["#667eea", "#ff6b6b", "#feca57", "#48dbfb", "#1dd1a1", "#5f27cd", "#ff9ff3"])
                tags = st.text_input("تەگەکان (بە کۆما جیابکەوە)", placeholder="مثال: خوێن, میز, گوردە")
                notes = st.text_area("تێبینی زیادە")
            
            submitted = st.form_submit_button("🧪 زیادکردنی پشکنین")
            if submitted and name:
                add_lab_test(name, purpose, normal_range, preparation, priority, color_label, tags, notes)
                st.success("✅ پشکنین بە سەرکەوتوویی زیادکرا!")
                st.rerun()
    
    with tab3:
        st.markdown("#### گەڕانی پێشکەوتوو")
        search_term = st.text_input("گەڕان بە ناو، ئامانج، یان تەگ")
        if search_term:
            results = get_lab_tests(search=search_term)
            if results:
                for test in results:
                    st.markdown(f"""
                    <div class="glass-card">
                        <h4>{test[1]}</h4>
                        <p><strong>ئامانج:</strong> {test[2]}</p>
                        <p><strong>تەگەکان:</strong> {test[7] if len(test) > 7 else ''}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("هیچ ئەنجامێک نەدۆزرایەوە!")

def show_edit_lab_test(test):
    """Display edit form for lab test"""
    with st.expander(f"✏️ دەستکاری: {test[1]}"):
        with st.form(f"edit_test_form_{test[0]}"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("ناوی پشکنین", value=test[1])
                purpose = st.text_area("ئامانج", value=test[2] if test[2] else '')
                normal_range = st.text_input("نرخی ئاسایی", value=test[3] if test[3] else '')
            with col2:
                preparation = st.text_area("ئامادەبوونی نەخۆش", value=test[4] if test[4] else '')
                priority = st.selectbox("پریۆریتی", ["high", "medium", "low"], 
                                      index=["high", "medium", "low"].index(test[5]) if test[5] in ["high", "medium", "low"] else 1)
                color_label = st.selectbox("ڕەنگی لیبڵ", ["#667eea", "#ff6b6b", "#feca57", "#48dbfb", "#1dd1a1", "#5f27cd", "#ff9ff3"],
                                         index=["#667eea", "#ff6b6b", "#feca57", "#48dbfb", "#1dd1a1", "#5f27cd", "#ff9ff3"].index(test[6]) if test[6] in ["#667eea", "#ff6b6b", "#feca57", "#48dbfb", "#1dd1a1", "#5f27cd", "#ff9ff3"] else 0)
                tags = st.text_input("تەگەکان", value=test[7] if len(test) > 7 and test[7] else '')
                notes = st.text_area("تێبینی", value=test[10] if len(test) > 10 else '')
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("💾 پاشەکەوتکردن"):
                    update_lab_test(test[0], name, purpose, normal_range, preparation, priority, color_label, tags, notes)
                    st.success("✅ پشکنین نوێکرایەوە!")
                    st.session_state.pop('edit_test', None)
                    st.rerun()
            with col2:
                if st.form_submit_button("❌ پەشیمانبوونەوە"):
                    st.session_state.pop('edit_test', None)
                    st.rerun()

def show_notes():
    st.markdown("### 📝 تێبینییەکان")
    
    tab1, tab2 = st.tabs(["📝 تێبینییەکان", "📋 تێمپڵەیتەکان"])
    
    with tab1:
        with st.expander("➕ زیادکردنی تێبینی نوێ"):
            with st.form("add_note_form"):
                title = st.text_input("ناونیشان *")
                content = st.text_area("ناوەرۆک")
                link = st.text_input("لینک")
                tags = st.text_input("تەگەکان (بە کۆما جیابکەوە)")
                uploaded_file = st.file_uploader("بارکردنی پێوەکراو", type=['png', 'jpg', 'jpeg', 'pdf', 'txt'])
                
                templates = get_templates()
                if templates:
                    template_names = [''] + [t[1] for t in templates]
                    selected_template = st.selectbox("بەکارهێنانی تێمپڵەیت", template_names)
                    if selected_template:
                        for t in templates:
                            if t[1] == selected_template:
                                content = t[2]
                                break
                
                submitted = st.form_submit_button("📝 پاشەکەوتکردنی تێبینی")
                if submitted and title:
                    image_path = None
                    attachment_path = None
                    if uploaded_file:
                        os.makedirs("attachments", exist_ok=True)
                        attachment_path = f"attachments/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uploaded_file.name}"
                        with open(attachment_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                    
                    add_general_note(title, content, image_path, link, attachment_path, tags)
                    st.success("✅ تێبینی بە سەرکەوتوویی زیادکرا!")
                    st.rerun()
        
        notes = get_general_notes()
        if notes:
            for note in notes:
                tags = note[6] if len(note) > 6 else ''
                st.markdown(f"""
                <div class="glass-card">
                    <h4>{note[1]}</h4>
                    <p>{note[2]}</p>
                    {f'<p><strong>🔗 لینک:</strong> <a href="{note[4]}" target="_blank">{note[4]}</a></p>' if note[4] else ''}
                    {f'<p><strong>🏷️ تەگەکان:</strong> {tags}</p>' if tags else ''}
                    <p><small>📅 {note[5]}</small></p>
                </div>
                """, unsafe_allow_html=True)
                
                if len(note) > 3 and note[3] and os.path.exists(note[3]):
                    if note[3].endswith(('.png', '.jpg', '.jpeg')):
                        st.image(note[3], use_container_width=True)
                
                if st.button(f"🗑️ سڕینەوە", key=f"del_note_{note[0]}"):
                    if len(note) > 3 and note[3] and os.path.exists(note[3]):
                        os.remove(note[3])
                    if len(note) > 5 and note[5] and os.path.exists(note[5]):
                        os.remove(note[5])
                    delete_general_note(note[0])
                    st.rerun()
                
                st.markdown("---")
        else:
            st.info("📝 هیچ تێبینییەک نییە.")
    
    with tab2:
        st.markdown("#### تێمپڵەیتەکان")
        
        with st.form("add_template_form"):
            template_name = st.text_input("ناوی تێمپڵەیت *")
            template_content = st.text_area("ناوەرۆک *")
            if st.form_submit_button("➕ زیادکردنی تێمپڵەیت"):
                if template_name and template_content:
                    add_template(template_name, template_content)
                    st.success("✅ تێمپڵەیت زیادکرا!")
                    st.rerun()
        
        templates = get_templates()
        if templates:
            for t in templates:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"""
                    <div class="glass-card" style="padding: 10px;">
                        <strong>{t[1]}</strong>
                        <p style="font-size: 14px; opacity: 0.8;">{t[2][:100]}...</p>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    if st.button(f"🗑️", key=f"del_temp_{t[0]}"):
                        delete_template(t[0])
                        st.rerun()

def show_study_mode():
    st.markdown("### 🎯 شێوازی خوێندن - فلاشکارت")
    
    item = get_random_study_item()
    
    if item:
        item_type = item[0]
        
        st.markdown("""
        <div style="text-align: center; margin: 20px 0;">
            <p style="font-size: 18px; opacity: 0.7;">👆 کرتە لەسەر کارت بکە بۆ گۆڕینی</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="glass-card" style="text-align: center; background: linear-gradient(145deg, #667eea, #764ba2); color: white;">', unsafe_allow_html=True)
            
            if item_type == 'medicine':
                st.markdown(f"""
                <h2>💊 {item[2]}</h2>
                <hr>
                <p><strong>🏷️ براند:</strong> {item[3]}</p>
                <p><strong>🔬 گەنەریک:</strong> {item[4]}</p>
                <p><strong>💊 دۆز:</strong> {item[5]}</p>
                <p><strong>🔄 ڕێگا:</strong> {item[6]}</p>
                <p><strong>📂 گرووپ:</strong> {item[7]}</p>
                <p><strong>📝 تێبینی:</strong> {item[9] if len(item) > 9 else ''}</p>
                """, unsafe_allow_html=True)
            
            elif item_type == 'lab_test':
                st.markdown(f"""
                <h2>🧪 {item[2]}</h2>
                <hr>
                <p><strong>🎯 ئامانج:</strong> {item[3]}</p>
                <p><strong>📊 نرخی ئاسایی:</strong> {item[4]}</p>
                <p><strong>🧑‍⚕️ ئامادەبوونی نەخۆش:</strong> {item[5]}</p>
                <p><strong>📝 تێبینی:</strong> {item[7] if len(item) > 7 else ''}</p>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            collection_name = st.text_input("ناوی کۆمەڵە", placeholder="ناوی کۆمەڵەکە")
            if st.button("➕ زیادکردن بۆ کۆمەڵە", use_container_width=True):
                if collection_name:
                    create_collection(collection_name, [item])
                    st.success("✅ زیادکرا بۆ کۆمەڵە!")
        
        with col2:
            if st.button("🔄 کارتی داهاتوو", use_container_width=True):
                st.rerun()
    else:
        st.info("📚 هیچ بابەتێک نییە بۆ خوێندن!")

def show_medical_calculators():
    st.markdown("### 📐 پزیشکی پزیشکی")
    
    calc_type = st.selectbox("جۆری حسابکەر", [
        "BMI",
        "BSA",
        "Creatinine Clearance",
        "Anion Gap",
        "Corrected Calcium",
        "Sodium Correction",
        "IV Drip Rate"
    ])
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    if calc_type == "BMI":
        col1, col2 = st.columns(2)
        with col1:
            weight = st.number_input("کێش (kg)", min_value=1.0, max_value=300.0, value=70.0)
        with col2:
            height = st.number_input("باڵا (cm)", min_value=50.0, max_value=300.0, value=175.0)
        
        if st.button("حسابکردن"):
            bmi = calculate_bmi(weight, height)
            st.markdown(f"""
            <div style="text-align: center; padding: 20px;">
                <h2>BMI: {bmi:.1f}</h2>
                <p>
                    {"کێشی کەم" if bmi < 18.5 else 
                     "کێشی ئاسایی" if bmi < 25 else 
                     "کێشی زیاد" if bmi < 30 else 
                     "قەڵەوی"}
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    elif calc_type == "BSA":
        col1, col2 = st.columns(2)
        with col1:
            weight = st.number_input("کێش (kg)", min_value=1.0, max_value=300.0, value=70.0)
        with col2:
            height = st.number_input("باڵا (cm)", min_value=50.0, max_value=300.0, value=175.0)
        
        if st.button("حسابکردن"):
            bsa = calculate_bsa(weight, height)
            st.markdown(f"""
            <div style="text-align: center; padding: 20px;">
                <h2>BSA: {bsa:.2f} m²</h2>
            </div>
            """, unsafe_allow_html=True)
    
    elif calc_type == "Creatinine Clearance":
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("تەمەن (ساڵ)", min_value=1, max_value=120, value=50)
            weight = st.number_input("کێش (kg)", min_value=1.0, max_value=300.0, value=70.0)
        with col2:
            creatinine = st.number_input("کریاتینین (mg/dL)", min_value=0.1, max_value=20.0, value=1.0)
            gender = st.selectbox("ڕەگەز", ["male", "female"])
        
        if st.button("حسابکردن"):
            crcl = calculate_creatinine_clearance(age, weight, creatinine, gender)
            st.markdown(f"""
            <div style="text-align: center; padding: 20px;">
                <h2>CrCl: {crcl:.1f} mL/min</h2>
            </div>
            """, unsafe_allow_html=True)
    
    elif calc_type == "Anion Gap":
        col1, col2, col3 = st.columns(3)
        with col1:
            na = st.number_input("Na (mEq/L)", min_value=100.0, max_value=200.0, value=140.0)
        with col2:
            cl = st.number_input("Cl (mEq/L)", min_value=50.0, max_value=150.0, value=100.0)
        with col3:
            hco3 = st.number_input("HCO3 (mEq/L)", min_value=5.0, max_value=50.0, value=24.0)
        
        if st.button("حسابکردن"):
            gap = calculate_anion_gap(na, cl, hco3)
            st.markdown(f"""
            <div style="text-align: center; padding: 20px;">
                <h2>Anion Gap: {gap:.1f} mEq/L</h2>
            </div>
            """, unsafe_allow_html=True)
    
    elif calc_type == "Corrected Calcium":
        col1, col2 = st.columns(2)
        with col1:
            calcium = st.number_input("کالسیۆم (mg/dL)", min_value=4.0, max_value=20.0, value=9.0)
        with col2:
            albumin = st.number_input("ئەلبومین (g/dL)", min_value=1.0, max_value=6.0, value=4.0)
        
        if st.button("حسابکردن"):
            corrected = calculate_corrected_calcium(calcium, albumin)
            st.markdown(f"""
            <div style="text-align: center; padding: 20px;">
                <h2>Corrected Calcium: {corrected:.2f} mg/dL</h2>
            </div>
            """, unsafe_allow_html=True)
    
    elif calc_type == "Sodium Correction":
        col1, col2 = st.columns(2)
        with col1:
            na = st.number_input("Na (mEq/L)", min_value=100.0, max_value=200.0, value=130.0)
        with col2:
            glucose = st.number_input("گلوکۆز (mg/dL)", min_value=50.0, max_value=1000.0, value=200.0)
        
        if st.button("حسابکردن"):
            corrected = calculate_sodium_correction(na, glucose)
            st.markdown(f"""
            <div style="text-align: center; padding: 20px;">
                <h2>Corrected Sodium: {corrected:.1f} mEq/L</h2>
            </div>
            """, unsafe_allow_html=True)
    
    elif calc_type == "IV Drip Rate":
        col1, col2, col3 = st.columns(3)
        with col1:
            volume = st.number_input("قەبارە (mL)", min_value=1.0, max_value=5000.0, value=1000.0)
        with col2:
            time = st.number_input("کات (خولەک)", min_value=1.0, max_value=1440.0, value=60.0)
        with col3:
            drop_factor = st.number_input("Drop Factor (gtt/mL)", min_value=10.0, max_value=60.0, value=20.0)
        
        if st.button("حسابکردن"):
            rate = calculate_iv_drip_rate(volume, time, drop_factor)
            st.markdown(f"""
            <div style="text-align: center; padding: 20px;">
                <h2>Drip Rate: {rate:.1f} gtt/min</h2>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_heatmap():
    st.markdown("### 📊 هیتماپی خوێندن")
    
    days = 90
    dates = [(datetime.now() - timedelta(days=i)).date() for i in range(days, 0, -1)]
    study_data = {date: random.randint(0, 5) for date in dates}
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("#### ڕۆژانی خوێندن (٩٠ ڕۆژی کۆتایی)")
    
    weeks = []
    for i in range(0, len(dates), 7):
        week = dates[i:i+7]
        weeks.append(week)
    
    for week in weeks:
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
                <div class="heatmap-cell" style="background: {color};" title="{date} - {count} items"></div>
                """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="display: flex; justify-content: center; gap: 20px; margin-top: 10px; flex-wrap: wrap;">
        <span>0</span>
        <span style="display: inline-block; width: 30px; height: 30px; background: #ebedf0; border-radius: 4px;"></span>
        <span style="display: inline-block; width: 30px; height: 30px; background: #9be9a8; border-radius: 4px;"></span>
        <span style="display: inline-block; width: 30px; height: 30px; background: #40c463; border-radius: 4px;"></span>
        <span style="display: inline-block; width: 30px; height: 30px; background: #30a14e; border-radius: 4px;"></span>
        <span style="display: inline-block; width: 30px; height: 30px; background: #1a4f2a; border-radius: 4px;"></span>
        <span>5+</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    total_study_days = sum(1 for v in study_data.values() if v > 0)
    total_items = sum(study_data.values())
    streak = 0
    for date in reversed(dates):
        if study_data.get(date, 0) > 0:
            streak += 1
        else:
            break
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center;">
            <h3>📚 {total_study_days}</h3>
            <p>ڕۆژانی خوێندن</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center;">
            <h3>📝 {total_items}</h3>
            <p>کۆی بابەتەکان</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center;">
            <h3>🔥 {streak}</h3>
            <p>بەردەوامی خوێندن</p>
        </div>
        """, unsafe_allow_html=True)

def show_achievements():
    st.markdown("### 🏆 دەستکەوتەکان")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center;">
            <h2 style="font-size: 40px;">📅</h2>
            <h3>{st.session_state.achievements['study_days']}</h3>
            <p>ڕۆژانی خوێندن</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center;">
            <h2 style="font-size: 40px;">📚</h2>
            <h3>{st.session_state.achievements['items_added']}</h3>
            <p>بابەتی زیادکراو</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center;">
            <h2 style="font-size: 40px;">⭐</h2>
            <h3>{st.session_state.achievements['favorites']}</h3>
            <p>دڵخوازەکان</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### 🎖️ مەدالیاکان")
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
            st.markdown(f"""
            <div class="glass-card" style="padding: 10px; text-align: center;">
                <h4>🏅 {badge}</h4>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("💪 بەردەوام بە بۆ بەدەستهێنانی مەدالیاکان!")

def show_users():
    if st.session_state.get('user_role') != 'admin':
        st.error("⛔ ڕێگەپێدراو نییە. تەنها بۆ بەڕێوەبەر.")
        return
    
    st.markdown("### 👥 بەڕێوەبەری بەکارهێنەران")
    
    with st.expander("➕ زیادکردنی بەکارهێنەری نوێ"):
        with st.form("add_user_form"):
            new_username = st.text_input("ناوی بەکارهێنەر *")
            new_password = st.text_input("ووشەی نهێنی *", type="password")
            role = st.selectbox("ڕۆڵ", ["user", "admin"])
            
            submitted = st.form_submit_button("👤 زیادکردنی بەکارهێنەر")
            if submitted and new_username and new_password:
                if add_user(new_username, new_password, role):
                    st.success("✅ بەکارهێنەر بە سەرکەوتوویی زیادکرا!")
                    st.rerun()
                else:
                    st.error("❌ ناوی بەکارهێنەر هەیە!")
    
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("SELECT id, username, role, created_at FROM users")
    users = c.fetchall()
    conn.close()
    
    for user in users:
        st.markdown(f"""
        <div class="glass-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h4>👤 {user[1]}</h4>
                    <p><strong>ڕۆڵ:</strong> {user[2]} | <strong>بەستوو:</strong> {user[3]}</p>
                </div>
                {f'<span class="license-badge license-valid">چالاک</span>' if user[0] != 1 else '<span class="license-badge license-invalid">بەڕێوەبەر</span>'}
            </div>
        </div>
        """, unsafe_allow_html=True)

def show_settings():
    st.markdown("### ⚙️ ڕێکخستنەکان")
    
    tab1, tab2, tab3, tab4 = st.tabs(["ڕووکار", "پشتگیری", "هەناردەکردن", "دەربارە"])
    
    with tab1:
        st.markdown("#### ڕووکار")
        dark_mode = st.toggle("🌙 ڕەوانەی تاریک", value=st.session_state.get('dark_mode', True))
        if dark_mode != st.session_state.get('dark_mode'):
            st.session_state.dark_mode = dark_mode
            st.rerun()
        
        font_size = st.selectbox("قەبارەی دەق", ["small", "medium", "large", "xlarge"], 
                               index=["small", "medium", "large", "xlarge"].index(st.session_state.get('font_size', 'medium')))
        if font_size != st.session_state.get('font_size'):
            st.session_state.font_size = font_size
            st.rerun()
        
        language = st.selectbox("زمان", ["کوردی", "English"], 
                               index=["کوردی", "English"].index(st.session_state.get('language', 'کوردی')))
        if language != st.session_state.get('language'):
            st.session_state.language = language
            st.rerun()
    
    with tab2:
        st.markdown("#### پشتگیری")
        if st.button("💾 پشتگیری دەستکرد"):
            auto_backup()
            st.success("✅ پشتگیری بە سەرکەوتوویی دروستکرا!")
        
        st.markdown("#### گەڕاندنەوەی پشتگیری")
        uploaded_file = st.file_uploader("📤 گەڕاندنەوەی پشتگیری", type=['db'])
        if uploaded_file:
            with open('medical_data.db', 'wb') as f:
                f.write(uploaded_file.getbuffer())
            st.success("✅ پشتگیری گەڕێنرایەوە!")
            st.rerun()
    
    with tab3:
        st.markdown("#### هەناردەکردن")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 PDF", use_container_width=True):
                medicines = get_medicines()
                med_data = []
                for m in medicines:
                    med_data.append({
                        "ناو": m[1], 
                        "براند": m[2], 
                        "گەنەریک": m[3], 
                        "دۆز": m[4], 
                        "ڕێگا": m[5],
                        "پریۆریتی": m[7] if len(m) > 7 else 'medium',
                        "تەگەکان": m[9] if len(m) > 9 else '',
                        "تێبینی": m[12] if len(m) > 12 else ''
                    })
                pdf_buffer = export_to_pdf(med_data, "دکتر دانیال - داتاکان")
                st.download_button(
                    label="📥 داگرتنی PDF",
                    data=pdf_buffer,
                    file_name=f"medical_data_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                )
        
        with col2:
            medicines = get_medicines()
            if medicines:
                df_data = []
                for m in medicines:
                    df_data.append({
                        'ناو': m[1],
                        'براند': m[2],
                        'گەنەریک': m[3],
                        'دۆز': m[4],
                        'ڕێگا': m[5],
                        'گرووپ': m[6],
                        'پریۆریتی': m[7] if len(m) > 7 else 'medium',
                        'تەگەکان': m[9] if len(m) > 9 else '',
                        'دڵخواز': 'بەڵێ' if (m[10] if len(m) > 10 else 0) else 'نەخێر',
                        'پین': 'بەڵێ' if (m[11] if len(m) > 11 else 0) else 'نەخێر'
                    })
                df = pd.DataFrame(df_data)
                csv = df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📊 CSV",
                    data=csv,
                    file_name=f"medical_data_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        with col3:
            medicines = get_medicines()
            if medicines:
                df_data = []
                for m in medicines:
                    df_data.append({
                        'ناو': m[1],
                        'براند': m[2],
                        'گەنەریک': m[3],
                        'دۆز': m[4],
                        'ڕێگا': m[5],
                        'گرووپ': m[6],
                        'پریۆریتی': m[7] if len(m) > 7 else 'medium',
                        'تەگەکان': m[9] if len(m) > 9 else '',
                        'دڵخواز': 'بەڵێ' if (m[10] if len(m) > 10 else 0) else 'نەخێر',
                        'پین': 'بەڵێ' if (m[11] if len(m) > 11 else 0) else 'نەخێر'
                    })
                df = pd.DataFrame(df_data)
                buffer = BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='دەرمانەکان', index=False)
                st.download_button(
                    label="📊 Excel",
                    data=buffer.getvalue(),
                    file_name=f"medical_data_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    
    with tab4:
        st.markdown("#### دەربارە")
        st.info("""
        **دکتر دانیال** 🏥
        
        پلاتفۆرمی خوێندنی پزیشکی بۆ خوێندکاران و پسپۆڕان.
        
        **وەشانی 4.0** - پرۆفیشناڵ
        
        **تایبەتمەندییەکان:**
        * 💊 دەرمانەکان (بە Priority, Color Labels, Tags, Pin)
        * 🧪 پشکنینەکان (بە Priority, Color Labels, Tags, Pin)
        * 📝 تێبینییەکان (بە تێمپڵەیت)
        * 🎯 شێوازی خوێندن (فلاشکارت)
        * 📐 پزیشکی پزیشکی (٧ حسابکەر)
        * 📊 هیتماپی خوێندن
        * 🏆 دەستکەوتەکان
        * 🔑 سیستەمی لایسەنس (Device Binding)
        * 💾 پشتگیری خۆکار
        * 📤 Export/Import
        
        **💰 فرۆشتن و لایسەنس:**
        * هەر کۆد تەنها لە یەک ئامێر کار دەکات
        * لایسەنس: Monthly / Yearly / Lifetime
        * دەتوانیت کۆد بۆ کڕیاران دروست بکەیت
        
        **❤️ بە هەموو دڵێک بۆ خوێندکارانی پزیشکی**
        """)

# ==================== RUN APP ====================
if __name__ == "__main__":
    main()
