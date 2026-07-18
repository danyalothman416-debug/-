```python
# app.py - وەشانی تەواو چاککراو
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import hashlib
import os
import secrets
import string
import uuid
import plotly.express as px
import plotly.graph_objects as go

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
            expires_at = datetime.fromisoformat(license_data[6])
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
        
        is_active = license_data[7] == 1
        
        try:
            expires_at = datetime.fromisoformat(license_data[6])
            is_expired = expires_at < datetime.now()
        except:
            is_expired = False
        
        if not is_active or is_expired:
            return {'status': 'inactive', 'expires_at': license_data[6]}
        
        stored_device = license_data[2] if license_data[2] else None
        if device_id and stored_device and stored_device != device_id:
            return {'status': 'device_mismatch'}
        
        return {
            'status': 'active',
            'expires_at': license_data[6],
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
        
        conn.close()
        return {'total': total, 'active': active, 'used': used, 'lifetime': lifetime}

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
            f.write("=" * 60 + "\n\n")
            for i, key in enumerate(license_keys, 1):
                f.write(f"{i:3d}. {key}\n")
            f.write("\n" + "=" * 60 + "\n")
            f.write(f"کۆی گشتی: {len(license_keys)} کۆد\n")
            f.write("=" * 60 + "\n")
        
        conn.close()
        return license_keys
    else:
        conn.close()
        return None

# Generate initial licenses
generated_keys = generate_initial_licenses()

# ==================== DATABASE SETUP ====================
def init_db():
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE,
                  password TEXT,
                  role TEXT,
                  created_at TEXT)''')
    
    # Medicines table
    c.execute('''CREATE TABLE IF NOT EXISTS medicines
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  brand TEXT,
                  generic TEXT,
                  dose TEXT,
                  route TEXT,
                  group_name TEXT,
                  priority TEXT DEFAULT 'medium',
                  color_label TEXT DEFAULT '#667eea',
                  tags TEXT,
                  notes TEXT,
                  favorite INTEGER DEFAULT 0,
                  pinned INTEGER DEFAULT 0,
                  created_at TEXT,
                  updated_at TEXT)''')
    
    # Lab tests table
    c.execute('''CREATE TABLE IF NOT EXISTS lab_tests
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  purpose TEXT,
                  normal_range TEXT,
                  preparation TEXT,
                  priority TEXT DEFAULT 'medium',
                  color_label TEXT DEFAULT '#667eea',
                  tags TEXT,
                  notes TEXT,
                  favorite INTEGER DEFAULT 0,
                  pinned INTEGER DEFAULT 0,
                  created_at TEXT,
                  updated_at TEXT)''')
    
    # General notes table
    c.execute('''CREATE TABLE IF NOT EXISTS general_notes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT NOT NULL,
                  content TEXT,
                  tags TEXT,
                  created_at TEXT,
                  updated_at TEXT)''')
    
    # Insert default admin user (username: Danyal, password: Admin@2024)
    c.execute("SELECT * FROM users WHERE username='Danyal'")
    if not c.fetchone():
        hashed = hashlib.sha256('Admin@2024'.encode()).hexdigest()
        c.execute("INSERT INTO users (username, password, role, created_at) VALUES (?, ?, ?, ?)",
                 ('Danyal', hashed, 'admin', datetime.now().isoformat()))
    
    # Insert sample medicines
    c.execute("SELECT COUNT(*) FROM medicines")
    if c.fetchone()[0] == 0:
        sample_medicines = [
            ('Paracetamol', 'Panadol', 'Acetaminophen', '500mg', 'Oral', 'Pain Killer', 'high', '#ff6b6b', 'pain,fever', 'Take after meals', 0, 0),
            ('Ibuprofen', 'Brufen', 'Ibuprofen', '400mg', 'Oral', 'NSAID', 'medium', '#feca57', 'pain,inflammation', 'Avoid on empty stomach', 0, 0),
            ('Omeprazole', 'Losec', 'Omeprazole', '20mg', 'Oral', 'PPI', 'high', '#48dbfb', 'GERD,ulcer', 'Take before breakfast', 0, 0),
            ('Amoxicillin', 'Augmentin', 'Amoxicillin', '500mg', 'Oral', 'Antibiotic', 'high', '#1dd1a1', 'infection,bacteria', 'Complete the full course', 0, 0),
            ('Metformin', 'Glucophage', 'Metformin', '500mg', 'Oral', 'Antidiabetic', 'high', '#5f27cd', 'diabetes,sugar', 'Take with meals', 0, 0),
            ('Atorvastatin', 'Lipitor', 'Atorvastatin', '20mg', 'Oral', 'Statin', 'medium', '#667eea', 'cholesterol,lipid', 'Take at night', 0, 0),
            ('Amlodipine', 'Norvasc', 'Amlodipine', '5mg', 'Oral', 'CCB', 'high', '#ff9ff3', 'hypertension,BP', 'Monitor blood pressure', 0, 0),
            ('Aspirin', 'Aspirin', 'Acetylsalicylic Acid', '100mg', 'Oral', 'Antiplatelet', 'high', '#ff4757', 'blood thinner,heart', 'Take after food', 0, 0),
        ]
        
        now = datetime.now().isoformat()
        for med in sample_medicines:
            c.execute("""INSERT INTO medicines 
                         (name, brand, generic, dose, route, group_name, priority, color_label, tags, notes, favorite, pinned, created_at, updated_at)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                      (*med, now, now))
    
    # Insert sample lab tests
    c.execute("SELECT COUNT(*) FROM lab_tests")
    if c.fetchone()[0] == 0:
        sample_tests = [
            ('CBC', 'Complete Blood Count', 'RBC: 4.5-5.5, WBC: 4-11, Hb: 13-17', 'No special preparation', 'high', '#667eea', 'blood,complete', 'Basic blood test', 0, 0),
            ('Fasting Blood Sugar', 'Blood Glucose Fasting', '70-110 mg/dL', 'Fast for 8-12 hours', 'high', '#ff6b6b', 'diabetes,sugar,fasting', 'Check fasting', 0, 0),
            ('HbA1c', 'Glycated Hemoglobin', '< 5.7% normal, 5.7-6.4% prediabetes', 'No fasting needed', 'high', '#feca57', 'diabetes,long term', 'Shows 3 months average', 0, 0),
            ('Lipid Profile', 'Cholesterol Test', 'Total: <200, LDL: <100, HDL: >40', 'Fast for 9-12 hours', 'medium', '#48dbfb', 'cholesterol,lipid,heart', 'Cardiac risk assessment', 0, 0),
            ('Liver Function Test', 'LFT', 'ALT: 7-56, AST: 10-40', 'No special preparation', 'medium', '#1dd1a1', 'liver,function', 'Check liver health', 0, 0),
            ('Kidney Function Test', 'RFT', 'Creatinine: 0.6-1.2, BUN: 7-20', 'No special preparation', 'medium', '#5f27cd', 'kidney,renal', 'Check kidney health', 0, 0),
            ('Thyroid Profile', 'TSH, T3, T4', 'TSH: 0.4-4.0 mIU/L', 'No special preparation', 'medium', '#ff9ff3', 'thyroid,hormone', 'Thyroid function', 0, 0),
            ('Urinalysis', 'Urine Test', 'Normal: No protein, glucose, blood', 'Clean catch midstream', 'low', '#ff4757', 'urine,infection', 'Basic urine test', 0, 0),
        ]
        
        now = datetime.now().isoformat()
        for test in sample_tests:
            c.execute("""INSERT INTO lab_tests 
                         (name, purpose, normal_range, preparation, priority, color_label, tags, notes, favorite, pinned, created_at, updated_at)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                      (*test, now, now))
    
    conn.commit()
    conn.close()

# ==================== CRUD FUNCTIONS ====================
def add_medicine(name, brand, generic, dose, route, group_name, priority, color_label, tags, notes):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute("""INSERT INTO medicines 
                 (name, brand, generic, dose, route, group_name, priority, color_label, tags, notes, created_at, updated_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
              (name, brand, generic, dose, route, group_name, priority, color_label, tags, notes, now, now))
    conn.commit()
    conn.close()
    return True

def update_medicine(id, name, brand, generic, dose, route, group_name, priority, color_label, tags, notes):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute("""UPDATE medicines                 SET name=?, brand=?, generic=?, dose=?, route=?, group_name=?, 
                     priority=?, color_label=?, tags=?, notes=?, updated_at=?
                 WHERE id=?""",
              (name, brand, generic, dose, route, group_name, priority, color_label, tags, notes, now, id))
    conn.commit()
    conn.close()
    return True

def delete_medicine(id):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("DELETE FROM medicines WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return True

def get_medicines(search=None, priority=None):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    
    query = "SELECT * FROM medicines WHERE 1=1"
    params = []
    
    if search:
        query += " AND (name LIKE ? OR brand LIKE ? OR generic LIKE ? OR tags LIKE ? OR notes LIKE ?)"
        params.extend([f'%{search}%'] * 5)
    
    if priority:
        query += " AND priority = ?"
        params.append(priority)
    
    query += " ORDER BY pinned DESC, favorite DESC, name ASC"
    
    c.execute(query, params)
    data = c.fetchall()
    conn.close()
    return data

def toggle_favorite_medicine(id):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("SELECT favorite FROM medicines WHERE id=?", (id,))
    current = c.fetchone()
    if current:
        new_val = 0 if current[0] else 1
        c.execute("UPDATE medicines SET favorite=? WHERE id=?", (new_val, id))
        conn.commit()
    conn.close()

def toggle_pin_medicine(id):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("SELECT pinned FROM medicines WHERE id=?", (id,))
    current = c.fetchone()
    if current:
        new_val = 0 if current[0] else 1
        c.execute("UPDATE medicines SET pinned=? WHERE id=?", (new_val, id))
        conn.commit()
    conn.close()

# Lab tests CRUD
def add_lab_test(name, purpose, normal_range, preparation, priority, color_label, tags, notes):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute("""INSERT INTO lab_tests (name, purpose, normal_range, preparation, priority, color_label, tags, notes, created_at, updated_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
              (name, purpose, normal_range, preparation, priority, color_label, tags, notes, now, now))
    conn.commit()
    conn.close()
    return True

def update_lab_test(id, name, purpose, normal_range, preparation, priority, color_label, tags, notes):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute("""UPDATE lab_tests 
                 SET name=?, purpose=?, normal_range=?, preparation=?, priority=?, 
                     color_label=?, tags=?, notes=?, updated_at=?
                 WHERE id=?""",
              (name, purpose, normal_range, preparation, priority, color_label, tags, notes, now, id))
    conn.commit()
    conn.close()
    return True

def delete_lab_test(id):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("DELETE FROM lab_tests WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return True

def get_lab_tests(search=None, priority=None):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    
    query = "SELECT * FROM lab_tests WHERE 1=1"
    params = []
    
    if search:
        query += " AND (name LIKE ? OR purpose LIKE ? OR tags LIKE ? OR notes LIKE ?)"
        params.extend([f'%{search}%'] * 4)
    
    if priority:
        query += " AND priority = ?"
        params.append(priority)
    
    query += " ORDER BY pinned DESC, favorite DESC, name ASC"
    
    c.execute(query, params)
    data = c.fetchall()
    conn.close()
    return data

def toggle_favorite_lab_test(id):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("SELECT favorite FROM lab_tests WHERE id=?", (id,))
    current = c.fetchone()
    if current:
        new_val = 0 if current[0] else 1
        c.execute("UPDATE lab_tests SET favorite=? WHERE id=?", (new_val, id))
        conn.commit()
    conn.close()

def toggle_pin_lab_test(id):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("SELECT pinned FROM lab_tests WHERE id=?", (id,))
    current = c.fetchone()
    if current:
        new_val = 0 if current[0] else 1
        c.execute("UPDATE lab_tests SET pinned=? WHERE id=?", (new_val, id))
        conn.commit()
    conn.close()

# Notes CRUD
def add_note(title, content, tags):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute("""INSERT INTO general_notes (title, content, tags, created_at, updated_at)
                 VALUES (?, ?, ?, ?, ?)""",
              (title, content, tags, now, now))
    conn.commit()
    conn.close()
    return True

def update_note(id, title, content, tags):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute("""UPDATE general_notes SET title=?, content=?, tags=?, updated_at=? WHERE id=?""",
              (title, content, tags, now, id))
    conn.commit()
    conn.close()
    return True

def delete_note(id):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("DELETE FROM general_notes WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return True

def get_notes(search=None):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    
    query = "SELECT * FROM general_notes WHERE 1=1"
    params = []
    
    if search:
        query += " AND (title LIKE ? OR content LIKE ? OR tags LIKE ?)"
        params.extend([f'%{search}%'] * 3)
    
    query += " ORDER BY updated_at DESC"
    
    c.execute(query, params)
    data = c.fetchall()
    conn.close()
    return data

# ==================== AUTH FUNCTIONS ====================
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

# ==================== SESSION STATE ====================
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
if 'edit_med_id' not in st.session_state:
    st.session_state.edit_med_id = None
if 'edit_test_id' not in st.session_state:
    st.session_state.edit_test_id = None
if 'edit_note_id' not in st.session_state:
    st.session_state.edit_note_id = None

# ==================== CSS ====================
def load_css():
    dark_mode = st.session_state.get('dark_mode', True)
    
    if dark_mode:
        bg_gradient = "linear-gradient(135deg, #0f0c29, #302b63, #24243e)"
        card_bg = "rgba(255,255,255,0.08)"
        text_color = "#ffffff"
        border_color = "rgba(255,255,255,0.15)"
    else:
        bg_gradient = "linear-gradient(135deg, #f5f7fa, #c3cfe2)"
        card_bg = "rgba(255,255,255,0.9)"
        text_color = "#1a1a2e"
        border_color = "rgba(0,0,0,0.1)"
    
    st.markdown(f"""
    <style>
        .stApp {{
            background: {bg_gradient};
            color: {text_color};
        }}
        
        .glass-card {{
            background: {card_bg};
            backdrop-filter: blur(20px);
            border-radius: 20px;
            border: 1px solid {border_color};
            padding: 20px;
            margin: 10px 0;
        }}
        
        .main-header {{
            text-align: center;
            padding: 25px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            color: white;
            margin-bottom: 25px;
        }}
        
        .stButton > button {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 8px 16px;
            font-weight: 600;
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
        
        .license-valid {{ background: #2ed573; color: white; }}
        .license-invalid {{ background: #ff4757; color: white; }}
        
        .priority-high {{ border-left: 4px solid #ff4757; }}
        .priority-medium {{ border-left: 4px solid #ffa502; }}
        .priority-low {{ border-left: 4px solid #2ed573; }}
        
        @media (max-width: 768px) {{
            .glass-card {{ padding: 15px; }}
            .main-header {{ padding: 15px; }}
        }}
    </style>
    """, unsafe_allow_html=True)

# ==================== LICENSE ACTIVATION PAGE ====================
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
        
        st.info("کۆدی لایسەنسەکەت لە شێوەی **DRD-XXXX-XXXX-XXXX** دەبێت")
        
        license_key = st.text_input("کۆدی لایسەنس", placeholder="DRD-XXXX-XXXX-XXXX")
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("✅ چالاککردن", use_container_width=True):
                if license_key:
                    with st.spinner("⏳ چالاکدەکرێت..."):
                        result = license_system.activate_license(license_key, st.session_state.device_id)
                    
                    if result['status'] == 'success':
                        st.session_state.license_key = license_key
                        st.session_state.license_valid = True
                        st.success(result['message'])
                        st.rerun()
                    elif result['status'] == 'expired':
                        st.error("⏰ ئەم کۆدە بەسەرچووە")
                    elif result['status'] == 'used':
                        st.error("🔒 ئەم کۆدە لەسەر ئامێرێکی تر چالاک کراوە")
                    else:
                        st.error(result['message'])
                else:
                    st.warning("⚠️ تکایە کۆدی لایسەنس بنووسە")
        
        with col_b:
            if st.button("🔍 پشکنین", use_container_width=True):
                if license_key:
                    status = license_system.check_license_status(license_key)
                    if status['status'] == 'active':
                        st.success(f"✅ چالاکە - {status.get('license_type', '')}")
                    elif status['status'] == 'inactive':
                        st.error("❌ ناچالاکە")
                    else:
                        st.warning("🔍 نەدۆزرایەوە")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Admin login
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 👤 چوونەژوورەوە (بەڕێوەبەر)")
        
        with st.form("admin_login"):
            username = st.text_input("ناوی بەکارهێنەر")
            password = st.text_input("ووشەی نهێنی", type="password")
            
            if st.form_submit_button("🔓 چوونەژوورەوە", use_container_width=True):
                if username and password:
                    user = check_login(username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.user_id = user[0]
                        st.session_state.user_role = user[3]
                        if user[3] == 'admin':
                            st.session_state.license_valid = True
                        st.success(f"✅ بەخێربێیت {username}!")
                        st.rerun()
                    else:
                        st.error("❌ ناوی بەکارهێنەر یان پاسۆرد هەڵەیە!")
        
        st.markdown('</div>', unsafe_allow_html=True)

# ==================== MAIN APP ====================
def main():
    init_db()
    load_css()
    
    # Check license
    if st.session_state.get('license_valid') and st.session_state.get('license_key'):
        status = license_system.check_license_status(st.session_state.license_key, st.session_state.device_id)
        if status['status'] != 'active':
            st.session_state.license_valid = False
            if st.session_state.user_role != 'admin':
                st.warning("⚠️ لایسەنسەکە بەسەرچووە")
    
    if not st.session_state.get('license_valid') and st.session_state.get('user_role') != 'admin':
        show_license_activation()
        return
    
    # ========== MAIN APP CONTENT ==========
    st.markdown(f"""
    <div class="main-header">
        <h1>🏥 دکتۆر دانیال</h1>
        <p>❤️ بەخێربێیت، {st.session_state.username or 'بەکارهێنەر'}!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick actions
    col1, col2, col3, col4 = st.columns(4)
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
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 📚 مینیو")
        
        pages = [
            "📊 داشبۆرد",
            "💊 دەرمانەکان",
            "🧪 پشکنینەکان",
            "📝 تێبینییەکان",
        ]
        
        # Only admin can see license and users pages
        if st.session_state.get('user_role') == 'admin':
            pages.append("🔑 لایسەنس")
            pages.append("👥 بەکارهێنەران")
        
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
                st.session_state.user_role = None
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
    elif page == "🔑 لایسەنس" and st.session_state.get('user_role') == 'admin':
        show_license_manager()
    elif page == "👥 بەکارهێنەران" and st.session_state.get('user_role') == 'admin':
        show_users_page()
    elif page == "⚙️ ڕێکخستنەکان":
        show_settings_page()

# ==================== PAGE FUNCTIONS ====================
def show_dashboard():
    st.markdown("### 📊 داشبۆرد")
    
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM medicines")
    total_meds = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM lab_tests")
    total_tests = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM general_notes")
    total_notes = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM medicines WHERE favorite=1")
    fav_meds = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM lab_tests WHERE favorite=1")
    fav_tests = c.fetchone()[0]
    
    conn.close()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💊 دەرمانەکان", total_meds)
    with col2:
        st.metric("🧪 پشکنینەکان", total_tests)
    with col3:
        st.metric("📝 تێبینییەکان", total_notes)
    with col4:
        st.metric("⭐ دڵخوازەکان", fav_meds + fav_tests)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("دابەشکردن")
        fig = go.Figure(data=[go.Pie(
            labels=['دەرمان', 'پشکنین', 'تێبینی'],
            values=[total_meds, total_tests, total_notes],
            marker=dict(colors=['#667eea', '#764ba2', '#ffa502']),
            hole=0.3
        )])
        fig.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("ڕێژەکان")
        fig = go.Figure(data=[go.Bar(
            x=['دەرمان', 'پشکنین', 'دڵخواز'],
            y=[total_meds, total_tests, fav_meds + fav_tests],
            marker_color=['#667eea', '#764ba2', '#ffa502'],
            text=[total_meds, total_tests, fav_meds + fav_tests],
            textposition='auto'
        )])
        fig.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

def show_medicines_page():
    st.markdown("### 💊 بەڕێوەبەری دەرمانەکان")
    
    tab1, tab2, tab3 = st.tabs(["📋 هەموو دەرمانەکان", "➕ زیادکردن", "✏️ دەستکاری"])
    
    with tab1:
        search = st.text_input("🔍 گەڕان", placeholder="ناو، براند، گەنەریک...", key="med_search")
        priority_filter = st.selectbox("پریۆریتی", ["هەموو", "high", "medium", "low"], key="med_priority")
        
        priority = None if priority_filter == "هەموو" else priority_filter
        meds = get_medicines(search=search if search else None, priority=priority)
        
        if meds:
            for med in meds:
                priority_class = f"priority-{med[7]}" if med[7] else ""
                
                with st.container():
                    st.markdown(f"""
                    <div class="glass-card {priority_class}">
                        <h4>{"📌 " if med[12] else ""}{"⭐ " if med[11] else ""}{med[1]}</h4>
                        <p><strong>براند:</strong> {med[2] or '-'} | <strong>گەنەریک:</strong> {med[3] or '-'}</p>
                        <p><strong>دۆز:</strong> {med[4] or '-'} | <strong>ڕێگا:</strong> {med[5] or '-'}</p>
                        <p><strong>گرووپ:</strong> {med[6] or '-'} | <strong>پریۆریتی:</strong> {med[7] or '-'}</p>
                        <p><strong>تێبینی:</strong> {med[10] or 'نییە'}</p>
                        <p><small>تەگەکان: {med[9] or 'نییە'}</small></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        if st.button("⭐ دڵخواز", key=f"fav_m_{med[0]}", use_container_width=True):
                            toggle_favorite_medicine(med[0])
                            st.rerun()
                    with col2:
                        if st.button("📌 پین", key=f"pin_m_{med[0]}", use_container_width=True):
                            toggle_pin_medicine(med[0])
                            st.rerun()
                    with col3:
                        if st.button("✏️ دەستکاری", key=f"edit_m_{med[0]}", use_container_width=True):
                            st.session_state.edit_med_id = med[0]
                            st.rerun()
                    with col4:
                        if st.button("🗑️ سڕینەوە", key=f"del_m_{med[0]}", use_container_width=True):
                            delete_medicine(med[0])
                            st.success("✅ سڕایەوە!")
                            st.rerun()
        else:
            st.info("هیچ دەرمانێک نەدۆزرایەوە")
    
    with tab2:
        st.markdown("#### ➕ زیادکردنی دەرمانی نوێ")
        
        with st.form("add_medicine_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("ناوی دەرمان *")
                brand = st.text_input("براند")
                generic = st.text_input("گەنەریک")
                dose = st.text_input("دۆز")
            with col2:
                route = st.selectbox("ڕێگا", ["Oral", "IV", "IM", "SC", "Topical", "Inhalation", "Other"])
                group_name = st.selectbox("گرووپ", [
                    "Pain Killer", "NSAID", "Antibiotic", "PPI", "Antidiabetic",
                    "Statin", "CCB", "Antiplatelet", "Antidepressant", "Antihistamine",
                    "Vitamin", "Other"
                ])
                priority = st.selectbox("پریۆریتی", ["high", "medium", "low"])
                color_label = st.selectbox("ڕەنگ", ["#667eea", "#ff6b6b", "#feca57", "#48dbfb", "#1dd1a1", "#5f27cd", "#ff9ff3"])
                tags = st.text_input("تەگەکان (بە کۆما جیابکەوە)", placeholder="pain, fever, headache")
                notes = st.text_area("تێبینی")
            
            if st.form_submit_button("💊 زیادکردن", use_container_width=True):
                if name:
                    add_medicine(name, brand, generic, dose, route, group_name, priority, color_label, tags, notes)
                    st.success("✅ دەرمان زیادکرا!")
                    st.rerun()
                else:
                    st.warning("ناوی دەرمان پێویستە!")
    
    with tab3:
        if st.session_state.edit_med_id:
            med_id = st.session_state.edit_med_id
            conn = sqlite3.connect('medical_data.db')
            c = conn.cursor()
            c.execute("SELECT * FROM medicines WHERE id=?", (med_id,))
            med = c.fetchone()
            conn.close()
            
            if med:
                st.markdown(f"#### ✏️ دەستکاری: {med[1]}")
                
                with st.form("edit_medicine_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        name = st.text_input("ناوی دەرمان *", value=med[1])
                        brand = st.text_input("براند", value=med[2] or '')
                        generic = st.text_input("گەنەریک", value=med[3] or '')
                        dose = st.text_input("دۆز", value=med[4] or '')
                    with col2:
                        routes = ["Oral", "IV", "IM", "SC", "Topical", "Inhalation", "Other"]
                        route = st.selectbox("ڕێگا", routes, index=routes.index(med[5]) if med[5] in routes else 0)
                        
                        groups = ["Pain Killer", "NSAID", "Antibiotic", "PPI", "Antidiabetic", "Statin", "CCB", "Antiplatelet", "Other"]
                        group_name = st.selectbox("گرووپ", groups, index=groups.index(med[6]) if med[6] in groups else 0)
                        
                        priorities = ["high", "medium", "low"]
                        priority = st.selectbox("پریۆریتی", priorities, index=priorities.index(med[7]) if med[7] in priorities else 1)
                        
                        colors = ["#667eea", "#ff6b6b", "#feca57", "#48dbfb", "#1dd1a1", "#5f27cd", "#ff9ff3"]
                        color_label = st.selectbox("ڕەنگ", colors, index=colors.index(med[8]) if med[8] in colors else 0)
                        
                        tags = st.text_input("تەگەکان", value=med[9] or '')
                        notes = st.text_area("تێبینی", value=med[10] or '')
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("💾 پاشەکەوت", use_container_width=True):
                            update_medicine(med_id, name, brand, generic, dose, route, group_name, priority, color_label, tags, notes)
                            st.success("✅ نوێکرایەوە!")
                            st.session_state.edit_med_id = None
                            st.rerun()
                    with col2:
                        if st.form_submit_button("❌ پەشیمانبوونەوە", use_container_width=True):
                            st.session_state.edit_med_id = None
                            st.rerun()
            else:
                st.error("دەرمان نەدۆزرایەوە")
        else:
            st.info("هیچ دەرمانێک بۆ دەستکاری هەڵنەبژێردراوە. لە تابێکی یەکەم دەرمانێک هەڵبژێرە.")

def show_lab_tests_page():
    st.markdown("### 🧪 بەڕێوەبەری پشکنینەکان")
    
    tab1, tab2, tab3 = st.tabs(["📋 هەموو پشکنینەکان", "➕ زیادکردن", "✏️ دەستکاری"])
    
    with tab1:
        search = st.text_input("🔍 گەڕان", placeholder="ناو، ئامانج...", key="test_search")
        priority_filter = st.selectbox("پریۆریتی", ["هەموو", "high", "medium", "low"], key="test_priority")
        
        priority = None if priority_filter == "هەموو" else priority_filter
        tests = get_lab_tests(search=search if search else None, priority=priority)
        
        if tests:
            for test in tests:
                priority_class = f"priority-{test[5]}" if test[5] else ""
                
                with st.container():
                    st.markdown(f"""
                    <div class="glass-card {priority_class}">
                        <h4>{"📌 " if test[9] else ""}{"⭐ " if test[8] else ""}{test[1]}</h4>
                        <p><strong>ئامانج:</strong> {test[2] or '-'}</p>
                        <p><strong>نرخی ئاسایی:</strong> {test[3] or '-'}</p>
                        <p><strong>ئامادەبوون:</strong> {test[4] or '-'}</p>
                        <p><strong>تێبینی:</strong> {test[7] or 'نییە'}</p>
                        <p><small>تەگەکان: {test[6] or 'نییە'}</small></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        if st.button("⭐ دڵخواز", key=f"fav_t_{test[0]}", use_container_width=True):
                            toggle_favorite_lab_test(test[0])
                            st.rerun()
                    with col2:
                        if st.button("📌 پین", key=f"pin_t_{test[0]}", use_container_width=True):
                            toggle_pin_lab_test(test[0])
                            st.rerun()
                    with col3:
                        if st.button("✏️ دەستکاری", key=f"edit_t_{test[0]}", use_container_width=True):
                            st.session_state.edit_test_id = test[0]
                            st.rerun()
                    with col4:
                        if st.button("🗑️ سڕینەوە", key=f"del_t_{test[0]}", use_container_width=True):
                            delete_lab_test(test[0])
                            st.success("✅ سڕایەوە!")
                            st.rerun()
        else:
            st.info("هیچ پشکنینێک نەدۆزرایەوە")
    
    with tab2:
        st.markdown("#### ➕ زیادکردنی پشکنینی نوێ")
        
        with st.form("add_test_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("ناوی پشکنین *")
                purpose = st.text_area("ئامانج")
                normal_range = st.text_input("نرخی ئاسایی")
            with col2:
                preparation = st.text_area("ئامادەبوونی نەخۆش")
                priority = st.selectbox("پریۆریتی", ["high", "medium", "low"])
                color_label = st.selectbox("ڕەنگ", ["#667eea", "#ff6b6b", "#feca57", "#48dbfb", "#1dd1a1", "#5f27cd", "#ff9ff3"])
                tags = st.text_input("تەگەکان (بە کۆما جیابکەوە)", placeholder="blood, kidney, liver")
                notes = st.text_area("تێبینی")
            
            if st.form_submit_button("🧪 زیادکردن", use_container_width=True):
                if name:
                    add_lab_test(name, purpose, normal_range, preparation, priority, color_label, tags, notes)
                    st.success("✅ پشکنین زیادکرا!")
                    st.rerun()
                else:
                    st.warning("ناوی پشکنین پێویستە!")
    
    with tab3:
        if st.session_state.edit_test_id:
            test_id = st.session_state.edit_test_id
            conn = sqlite3.connect('medical_data.db')
            c = conn.cursor()
            c.execute("SELECT * FROM lab_tests WHERE id=?", (test_id,))
            test = c.fetchone()
            conn.close()
            
            if test:
                st.markdown(f"#### ✏️ دەستکاری: {test[1]}")
                
                with st.form("edit_test_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        name = st.text_input("ناوی پشکنین *", value=test[1])
                        purpose = st.text_area("ئامانج", value=test[2] or '')
                        normal_range = st.text_input("نرخی ئاسایی", value=test[3] or '')
                    with col2:
                        preparation = st.text_area("ئامادەبوون", value=test[4] or '')
                        
                        priorities = ["high", "medium", "low"]
                        priority = st.selectbox("پریۆریتی", priorities, index=priorities.index(test[5]) if test[5] in priorities else 1)
                        
                        colors = ["#667eea", "#ff6b6b", "#feca57", "#48dbfb", "#1dd1a1", "#5f27cd", "#ff9ff3"]
                        color_label = st.selectbox("ڕەنگ", colors, index=colors.index(test[6]) if test[6] in colors else 0)
                        
                        tags = st.text_input("تەگەکان", value=test[7] or '')
                        notes = st.text_area("تێبینی", value=test[8] or '')
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("💾 پاشەکەوت", use_container_width=True):
                            update_lab_test(test_id, name, purpose, normal_range, preparation, priority, color_label, tags, notes)
                            st.success("✅ نوێکرایەوە!")
                            st.session_state.edit_test_id = None
                            st.rerun()
                    with col2:
                        if st.form_submit_button("❌ پەشیمانبوونەوە", use_container_width=True):
                            st.session_state.edit_test_id = None
                            st.rerun()
        else:
            st.info("هیچ پشکنینێک بۆ دەستکاری هەڵنەبژێردراوە")

def show_notes_page():
    st.markdown("### 📝 بەڕێوەبەری تێبینییەکان")
    
    tab1, tab2, tab3 = st.tabs(["📋 هەموو تێبینییەکان", "➕ زیادکردن", "✏️ دەستکاری"])
    
    with tab1:
        search = st.text_input("🔍 گەڕان", placeholder="ناونیشان، ناوەرۆک...", key="note_search")
        
        notes = get_notes(search=search if search else None)
        
        if notes:
            for note in notes:
                with st.container():
                    st.markdown(f"""
                    <div class="glass-card">
                        <h4>📝 {note[1]}</h4>
                        <p>{note[2][:200] if note[2] else '...'}</p>
                        <p><small>تەگەکان: {note[3] or 'نییە'} | بەروار: {note[5][:10] if note[5] else note[4][:10] if note[4] else ''}</small></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✏️ دەستکاری", key=f"edit_n_{note[0]}", use_container_width=True):
                            st.session_state.edit_note_id = note[0]
                            st.rerun()
                    with col2:
                        if st.button("🗑️ سڕینەوە", key=f"del_n_{note[0]}", use_container_width=True):
                            delete_note(note[0])
                            st.success("✅ سڕایەوە!")
                            st.rerun()
        else:
            st.info("هیچ تێبینییەک نەدۆزرایەوە")
    
    with tab2:
        st.markdown("#### ➕ زیادکردنی تێبینی نوێ")
        
        with st.form("add_note_form"):
            title = st.text_input("ناونیشان *")
            content = st.text_area("ناوەرۆک", height=200)
            tags = st.text_input("تەگەکان (بە کۆما جیابکەوە)", placeholder="study, exam, important")
            
            if st.form_submit_button("📝 زیادکردن", use_container_width=True):
                if title:
                    add_note(title, content, tags)
                    st.success("✅ تێبینی زیادکرا!")
                    st.rerun()
                else:
                    st.warning("ناونیشان پێویستە!")
    
    with tab3:
        if st.session_state.edit_note_id:
            note_id = st.session_state.edit_note_id
            conn = sqlite3.connect('medical_data.db')
            c = conn.cursor()
            c.execute("SELECT * FROM general_notes WHERE id=?", (note_id,))
            note = c.fetchone()
            conn.close()
            
            if note:
                st.markdown(f"#### ✏️ دەستکاری: {note[1]}")
                
                with st.form("edit_note_form"):
                    title = st.text_input("ناونیشان *", value=note[1])
                    content = st.text_area("ناوەرۆک", value=note[2] or '', height=200)
                    tags = st.text_input("تەگەکان", value=note[3] or '')
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("💾 پاشەکەوت", use_container_width=True):
                            update_note(note_id, title, content, tags)
                            st.success("✅ نوێکرایەوە!")
                            st.session_state.edit_note_id = None
                            st.rerun()
                    with col2:
                        if st.form_submit_button("❌ پەشیمانبوونەوە", use_container_width=True):
                            st.session_state.edit_note_id = None
                            st.rerun()
        else:
            st.info("هیچ تێبینییەک بۆ دەستکاری هەڵنەبژێردراوە")

def show_license_manager():
    # 🔒 DOUBLE CHECK: Only admin can access
    if st.session_state.get('user_role') != 'admin':
        st.error("⛔ تەنها بەڕێوەبەر دەتوانێت ئەم بەشە ببینێت!")
        st.stop()
    
    st.markdown("### 🔑 بەڕێوەبەری لایسەنس (تەنها Admin)")
    
    st.warning("⚠️ ئەم بەشە تەنها بۆ بەڕێوەبەرە و کەسی تر ناتوانێت بیبینێت!")
    
    tab1, tab2, tab3 = st.tabs(["📊 ئامار", "➕ دروستکردن", "📋 لیست"])
    
    with tab1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
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
        
        fig = go.Figure(data=[go.Pie(
            labels=['چالاک', 'ناچالاک'],
            values=[stats['active'], stats['total'] - stats['active']],
            marker=dict(colors=['#2ed573', '#ff4757']),
            hole=0.3
        )])
        fig.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("➕ دروستکردنی کۆدی نوێ")
        
        col1, col2 = st.columns(2)
        with col1:
            license_type = st.selectbox("جۆر", ["lifetime", "yearly", "monthly"])
        with col2:
            count = st.number_input("ژمارە", 1, 500, 1)
        
        user_email = st.text_input("ئیمەیڵ (ئارەزوومەندانە)")
        
        if st.button("🔑 دروستکردن", use_container_width=True):
            if count == 1:
                key = license_system.generate_license_key(license_type, user_email)
                st.success("✅ دروستکرا!")
                st.code(key)
            else:
                keys = license_system.generate_bulk_licenses(count, license_type)
                st.success(f"✅ {count} کۆد دروستکرا!")
                keys_text = "\n".join(keys)
                st.download_button(f"📥 داگرتنی {count} کۆد", keys_text, f"licenses_{datetime.now().strftime('%Y%m%d')}.txt")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        licenses = license_system.get_all_licenses()
        if licenses:
            for lic in licenses[:50]:
                try:
                    expires = datetime.fromisoformat(lic[6])
                    is_expired = expires < datetime.now()
                except:
                    is_expired = False
                
                status = "✅" if lic[7] and not is_expired else "❌"
                st.markdown(f"{status} `{lic[1][:16]}...` | {lic[4]} | {lic[6][:10] if lic[6] else ''} | {'بەکارهێنراو' if lic[2] else 'ئازاد'}")
        st.markdown('</div>', unsafe_allow_html=True)

def show_users_page():
    if st.session_state.get('user_role') != 'admin':
        st.error("⛔ تەنها بۆ بەڕێوەبەر")
        st.stop()
    
    st.markdown("### 👥 بەکارهێنەران (تەنها Admin)")
    
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("SELECT id, username, role, created_at FROM users")
    users = c.fetchall()
    conn.close()
    
    for user in users:
        st.markdown(f"""
        <div class="glass-card">
            <h4>👤 {user[1]} <small>({user[2]})</small></h4>
            <p>بەرواری دروستکردن: {user[3][:10] if user[3] else ''}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with st.expander("➕ زیادکردنی بەکارهێنەر"):
        with st.form("add_user_form"):
            username = st.text_input("ناوی بەکارهێنەر")
            password = st.text_input("ووشەی نهێنی", type="password")
            role = st.selectbox("ڕۆڵ", ["user", "admin"])
            if st.form_submit_button("زیادکردن"):
                if username and password:
                    if add_user(username, password, role):
                        st.success("✅ زیادکرا!")
                        st.rerun()
                    else:
                        st.error("❌ هەیە!")

def show_settings_page():
    st.markdown("### ⚙️ ڕێکخستنەکان")
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    dark_mode = st.toggle("🌙 ڕەوانەی تاریک", value=st.session_state.dark_mode)
    if dark_mode != st.session_state.dark_mode:
        st.session_state.dark_mode = dark_mode
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📱 زانیاری")
    st.code(f"Device ID: {st.session_state.device_id[:20]}...")
    if st.session_state.get('license_key'):
        st.code(f"License: {st.session_state.license_key}")
    st.code(f"Role: {st.session_state.get('user_role', 'none')}")
    
    st.markdown("---")
    if st.button("🚪 چوونەدەرەوە", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.license_valid = False
        st.session_state.license_key = None
        st.session_state.user_role = None
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== RUN ====================
if __name__ == "__main__":
    main()
```
