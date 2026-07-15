# app.py - وەشانی تەواو بە سیستەمی پارەدان بۆ عێراق
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
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import qrcode
from io import BytesIO
import base64

# ڕێکخستنی لاپەڕە
st.set_page_config(
    page_title="دکتۆر دانیال - خوێندنی پزیشکی",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CONFIGURATION ====================
# زانیاری بانکی و پارەدان
BANK_ACCOUNTS = {
    'فاست پی': {
        'name': 'فاست پی (FastPay)',
        'number': '0770XXXXXXX',  # ژمارە مۆبایلەکەت
        'holder': 'ناوی تەواوت',
        'icon': '📱',
    },
    'ئاسیا حەواڵە': {
        'name': 'ئاسیا حەواڵە',
        'number': '0770XXXXXXX',  # ژمارە مۆبایلەکەت
        'holder': 'ناوی تەواوت',
        'icon': '🏦',
    },
    'زەین کاش': {
        'name': 'زەین کاش (ZainCash)',
        'number': '0780XXXXXXX',  # ژمارە مۆبایلەکەت
        'holder': 'ناوی تەواوت',
        'icon': '💳',
    },
}

# ئەکاونتی بانکی
BANK_ACCOUNT = {
    'bank_name': 'بانکی ...',  # ناوی بانکەکەت
    'account_name': 'ناوی تەواوی خاوەن حساب',
    'account_number': 'ژمارەی حسابەکەت',
    'iban': 'ژمارەی IBAN',
}

# نرخی پلانەکان (دیناری عێراقی)
PLAN_PRICES_IQD = {
    'monthly': {'price': 15000, 'price_text': '١٥,٠٠٠ دینار', 'duration': '٣٠ ڕۆژ', 'features': ['دەستگەیشتنی تەواو', 'نوێکردنەوەی ڕۆژانە', 'پشتگیری ئیمەیڵ']},
    'yearly': {'price': 150000, 'price_text': '١٥٠,٠٠٠ دینار', 'duration': '٣٦٥ ڕۆژ', 'features': ['دەستگەیشتنی تەواو', 'نوێکردنەوەی ڕۆژانە', 'پشتگیری پێشکەوتوو', '٢ مانگ خۆرایی']},
    'lifetime': {'price': 300000, 'price_text': '٣٠٠,٠٠٠ دینار', 'duration': 'هەمیشەیی', 'features': ['دەستگەیشتنی هەمیشەیی', 'هەموو نوێکارییەکان', 'پشتگیری VIP', 'بێ سنوور']},
}

# نرخی پلانەکان (دۆلار - ئەگەر بیەوێت)
PLAN_PRICES_USD = {
    'monthly': {'price': 10, 'price_text': '$10', 'duration': '٣٠ ڕۆژ', 'features': ['دەستگەیشتنی تەواو', 'نوێکردنەوەی ڕۆژانە', 'پشتگیری ئیمەیڵ']},
    'yearly': {'price': 100, 'price_text': '$100', 'duration': '٣٦٥ ڕۆژ', 'features': ['دەستگەیشتنی تەواو', 'نوێکردنەوەی ڕۆژانە', 'پشتگیری پێشکەوتوو', '٢ مانگ خۆرایی']},
    'lifetime': {'price': 200, 'price_text': '$200', 'duration': 'هەمیشەیی', 'features': ['دەستگەیشتنی هەمیشەیی', 'هەموو نوێکارییەکان', 'پشتگیری VIP', 'بێ سنوور']},
}

# هەڵبژاردنی دراو
CURRENCY = 'IQD'  # 'IQD' یان 'USD'

PLAN_PRICES = PLAN_PRICES_IQD if CURRENCY == 'IQD' else PLAN_PRICES_USD

# ئیمەیڵی بەڕێوەبەر
ADMIN_EMAIL = "your-email@gmail.com"
ADMIN_PASSWORD_APP = "your-app-password"
ADMIN_TELEGRAM = "@your_telegram"  # تێلیگرام
ADMIN_WHATSAPP = "+964770XXXXXXX"  # واتسئەپ

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
                      user_phone TEXT,
                      user_name TEXT,
                      license_type TEXT,
                      created_at TEXT,
                      expires_at TEXT,
                      is_active INTEGER DEFAULT 1,
                      last_used TEXT,
                      payment_status TEXT DEFAULT 'pending',
                      payment_method TEXT,
                      payment_ref TEXT,
                      payment_amount REAL,
                      payment_date TEXT)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS activation_attempts
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      license_key TEXT,
                      device_id TEXT,
                      attempt_time TEXT,
                      status TEXT)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS payments
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_name TEXT,
                      user_email TEXT,
                      user_phone TEXT,
                      plan_type TEXT,
                      amount REAL,
                      currency TEXT,
                      payment_method TEXT,
                      payment_ref TEXT,
                      license_key TEXT,
                      status TEXT DEFAULT 'pending',
                      created_at TEXT,
                      verified_at TEXT,
                      admin_notes TEXT)''')
        
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
                     (license_key, user_email, license_type, created_at, expires_at, is_active, payment_status)
                     VALUES (?, ?, ?, ?, ?, 1, 'pending')""",
                  (license_key, user_email, license_type, now, expires))
        
        conn.commit()
        conn.close()
        return license_key
    
    def register_payment_request(self, user_name, user_email, user_phone, plan_type, amount, currency, payment_method, payment_ref=''):
        """تۆمارکردنی داواکاری پارەدان"""
        conn = sqlite3.connect(self.license_file)
        c = conn.cursor()
        
        # دروستکردنی لایسەنس
        license_key = self.generate_license_key(plan_type, user_email)
        
        # تۆمارکردنی پارەدان
        c.execute("""INSERT INTO payments 
                     (user_name, user_email, user_phone, plan_type, amount, currency, 
                      payment_method, payment_ref, license_key, status, created_at)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?)""",
                  (user_name, user_email, user_phone, plan_type, amount, currency,
                   payment_method, payment_ref, license_key, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return license_key
    
    def verify_payment_by_admin(self, license_key):
        """پشتڕاستکردنەوەی پارەدان لەلایەن Admin"""
        conn = sqlite3.connect(self.license_file)
        c = conn.cursor()
        
        c.execute("""UPDATE payments SET status='completed', verified_at=? WHERE license_key=?""",
                  (datetime.now().isoformat(), license_key))
        c.execute("""UPDATE licenses SET payment_status='paid', is_active=1 WHERE license_key=?""",
                  (license_key,))
        
        # وەرگرتنی زانیاری بەکارهێنەر
        c.execute("SELECT user_email, user_name, license_type FROM payments WHERE license_key=?", (license_key,))
        user_info = c.fetchone()
        
        conn.commit()
        conn.close()
        
        # ناردنی لایسەنس بۆ بەکارهێنەر
        if user_info and user_info[0]:
            self.send_license_to_user(user_info[0], user_info[1], license_key, user_info[2])
        
        return True
    
    def activate_license(self, license_key, device_id):
        conn = sqlite3.connect(self.license_file)
        c = conn.cursor()
        
        c.execute("SELECT * FROM licenses WHERE license_key=? AND is_active=1", (license_key,))
        license_data = c.fetchone()
        
        if not license_data:
            self.log_attempt(license_key, device_id, 'invalid')
            conn.close()
            return {'status': 'invalid', 'message': '⛔ کۆدەکە نادروستە یان چالاک نییە'}
        
        # پشکنینی باری پارەدان
        if license_data[10] == 'pending':  # payment_status
            conn.close()
            return {'status': 'pending_payment', 'message': '💰 ئەم کۆدە هێشتا چالاک نەکراوە. چاوەڕێی پشتڕاستکردنەوەی پارەدان بکە.'}
        
        try:
            expires_at = datetime.fromisoformat(license_data[8])
            if expires_at < datetime.now():
                c.execute("UPDATE licenses SET is_active=0 WHERE license_key=?", (license_key,))
                conn.commit()
                self.log_attempt(license_key, device_id, 'expired')
                conn.close()
                return {'status': 'expired', 'message': '⏰ کۆدەکە بەسەرچووە. تکایە نوێی بکەرەوە'}
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
        
        is_active = license_data[9] == 1  # is_active
        payment_status = license_data[10] if len(license_data) > 10 else 'paid'
        
        try:
            expires_at = datetime.fromisoformat(license_data[8])
            is_expired = expires_at < datetime.now()
        except:
            is_expired = False
        
        if not is_active or is_expired or payment_status == 'pending':
            return {'status': 'inactive', 'expires_at': license_data[8]}
        
        stored_device = license_data[2] if license_data[2] else None
        if device_id and stored_device and stored_device != device_id:
            return {'status': 'device_mismatch'}
        
        return {
            'status': 'active',
            'expires_at': license_data[8],
            'device_id': license_data[2],
            'license_type': license_data[6]
        }
    
    def send_license_to_user(self, email, user_name, license_key, plan_type):
        """ناردنی لایسەنس بە ئیمەیڵ"""
        try:
            plan_names = {
                'monthly': 'مانگانە',
                'yearly': 'ساڵانە',
                'lifetime': 'هەمیشەیی'
            }
            plan_name = plan_names.get(plan_type, plan_type)
            
            msg = MIMEMultipart()
            msg['From'] = ADMIN_EMAIL
            msg['To'] = email
            msg['Subject'] = '✅ کلیلی لایسەنسی دکتۆر دانیال'
            
            body = f"""
            سڵاو {user_name}،
            
            سوپاس بۆ کڕینی پلانی {plan_name}!
            
            🔑 کلیلی لایسەنسی تۆ: {license_key}
            
            بۆ چالاککردن:
            ١. ئەپەکە بکەرەوە
            ٢. لە بەشی "خاوەن لایسەنسی؟" کلیک بکە
            ٣. ئەم کلیلە بنووسە: {license_key}
            
            بە هیوای سەرکەوتن،
            تیمی دکتۆر دانیال
            
            ---
            بۆ پرسیار: {ADMIN_TELEGRAM}
            """
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(ADMIN_EMAIL, ADMIN_PASSWORD_APP)
            server.send_message(msg)
            server.quit()
            
            return True
        except Exception as e:
            print(f"Email error: {e}")
            return False
    
    def get_pending_payments(self):
        """وەرگرتنی داواکارییە چاوەڕوانەکان"""
        conn = sqlite3.connect(self.license_file)
        c = conn.cursor()
        c.execute("SELECT * FROM payments WHERE status='pending' ORDER BY created_at DESC")
        payments = c.fetchall()
        conn.close()
        return payments
    
    def get_all_payments(self):
        conn = sqlite3.connect(self.license_file)
        c = conn.cursor()
        c.execute("SELECT * FROM payments ORDER BY created_at DESC")
        payments = c.fetchall()
        conn.close()
        return payments
    
    def get_payment_stats(self):
        conn = sqlite3.connect(self.license_file)
        c = conn.cursor()
        
        c.execute("SELECT COUNT(*) FROM payments WHERE status='completed'")
        total_payments = c.fetchone()[0]
        
        c.execute("SELECT COALESCE(SUM(amount), 0) FROM payments WHERE status='completed'")
        total_revenue = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM payments WHERE status='completed' AND created_at LIKE ?",
                  (datetime.now().strftime('%Y-%m-%d') + '%',))
        today_payments = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM payments WHERE status='pending'")
        pending_payments = c.fetchone()[0]
        
        conn.close()
        return {
            'total_payments': total_payments,
            'total_revenue': total_revenue,
            'today_payments': today_payments,
            'pending_payments': pending_payments
        }

# Initialize license system
license_system = LicenseSystem()

# ==================== DATABASE SETUP ====================
def init_db():
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE,
                  password TEXT,
                  role TEXT,
                  email TEXT,
                  created_at TEXT)''')
    
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
    
    c.execute('''CREATE TABLE IF NOT EXISTS general_notes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT NOT NULL,
                  content TEXT,
                  tags TEXT,
                  created_at TEXT,
                  updated_at TEXT)''')
    
    c.execute("SELECT * FROM users WHERE username='Danyal'")
    if not c.fetchone():
        hashed = hashlib.sha256('Admin@2024'.encode()).hexdigest()
        c.execute("INSERT INTO users (username, password, role, email, created_at) VALUES (?, ?, ?, ?, ?)",
                 ('Danyal', hashed, 'admin', ADMIN_EMAIL, datetime.now().isoformat()))
    
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
# هەموو CRUD functionـەکان وەک خۆیان دەمێننەوە
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
    c.execute("""UPDATE medicines 
                 SET name=?, brand=?, generic=?, dose=?, route=?, group_name=?, 
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

def add_lab_test(name, purpose, normal_range, preparation, priority, color_label, tags, notes):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute("""INSERT INTO lab_tests 
                 (name, purpose, normal_range, preparation, priority, color_label, tags, notes, created_at, updated_at)
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

def check_login(username, password):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    hashed = hashlib.sha256(password.encode()).hexdigest()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed))
    user = c.fetchone()
    conn.close()
    return user

def add_user(username, password, email='', role='user'):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    hashed = hashlib.sha256(password.encode()).hexdigest()
    try:
        c.execute("INSERT INTO users (username, password, role, email, created_at) VALUES (?, ?, ?, ?, ?)",
                 (username, hashed, role, email, datetime.now().isoformat()))
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
    st.session_state.current_page = '🏠 سەرەکی'
if 'edit_med_id' not in st.session_state:
    st.session_state.edit_med_id = None
if 'edit_test_id' not in st.session_state:
    st.session_state.edit_test_id = None
if 'edit_note_id' not in st.session_state:
    st.session_state.edit_note_id = None
if 'selected_plan' not in st.session_state:
    st.session_state.selected_plan = None
if 'payment_submitted' not in st.session_state:
    st.session_state.payment_submitted = False

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
            transition: transform 0.3s, box-shadow 0.3s;
        }}
        .glass-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}
        .main-header {{
            text-align: center;
            padding: 25px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            color: white;
            margin-bottom: 25px;
        }}
        .pricing-card {{
            background: {card_bg};
            backdrop-filter: blur(20px);
            border-radius: 20px;
            border: 2px solid {border_color};
            padding: 30px;
            text-align: center;
            transition: all 0.3s;
        }}
        .pricing-card:hover {{
            transform: translateY(-10px);
            box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4);
            border-color: #667eea;
        }}
        .pricing-card.featured {{
            border-color: gold;
            background: linear-gradient(135deg, rgba(255,215,0,0.1), rgba(102,126,234,0.1));
        }}
        .stButton > button {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 10px 20px;
            font-weight: 600;
            transition: all 0.3s;
        }}
        .stButton > button:hover {{
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.6);
        }}
        .buy-button > button {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            font-size: 18px;
            padding: 15px 30px;
        }}
        .price-tag {{
            font-size: 48px;
            font-weight: bold;
            color: #667eea;
            margin: 20px 0;
        }}
        .feature-list {{
            list-style: none;
            padding: 0;
            text-align: right;
        }}
        .feature-list li {{
            padding: 8px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        .payment-info-box {{
            background: rgba(102, 126, 234, 0.2);
            border: 2px solid #667eea;
            border-radius: 15px;
            padding: 20px;
            margin: 15px 0;
            text-align: center;
        }}
        .priority-high {{ border-left: 4px solid #ff4757; }}
        .priority-medium {{ border-left: 4px solid #ffa502; }}
        .priority-low {{ border-left: 4px solid #2ed573; }}
        @media (max-width: 768px) {{
            .glass-card {{ padding: 15px; }}
            .main-header {{ padding: 15px; }}
            .price-tag {{ font-size: 32px; }}
        }}
    </style>
    """, unsafe_allow_html=True)

# ==================== LANDING PAGE ====================
def show_landing_page():
    st.markdown("""
    <div class="main-header">
        <h1>🏥 دکتۆر دانیال</h1>
        <p style="font-size: 20px;">پلاتفۆرمی خوێندنی پزیشکی - دەستگەیشتن بە هەزاران زانیاری پزیشکی</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Features
    st.markdown("### ✨ بۆچی دکتۆر دانیال؟")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="glass-card" style="text-align: center;"><h2>💊</h2><h4>دەرمانەکان</h4><p>سەدان دەرمان بە وردەکاری تەواو</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="glass-card" style="text-align: center;"><h2>🧪</h2><h4>پشکنینەکان</h4><p>زانیاری تەواوی پشکنینە پزیشکییەکان</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="glass-card" style="text-align: center;"><h2>📝</h2><h4>تێبینییەکان</h4><p>ڕێکخستنی تێبینییە پزیشکییەکان</p></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="glass-card" style="text-align: center;"><h2>🔄</h2><h4>نوێکاری</h4><p>نوێکردنەوەی ڕۆژانە</p></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Pricing
    st.markdown("### 💰 پلانەکان")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        plan = PLAN_PRICES['monthly']
        st.markdown(f"""
        <div class="pricing-card">
            <h3>📅 مانگانە</h3>
            <div class="price-tag">{plan['price_text']}</div>
            <p>/ مانگ</p>
            <hr>
            <ul class="feature-list">
        """, unsafe_allow_html=True)
        for f in plan['features']:
            st.markdown(f"<li>✅ {f}</li>", unsafe_allow_html=True)
        st.markdown("</ul></div>", unsafe_allow_html=True)
        if st.button("💳 کڕینی پلانی مانگانە", key="buy_monthly", use_container_width=True):
            st.session_state.selected_plan = 'monthly'
            st.session_state.current_page = '💳 پارەدان'
            st.rerun()
    
    with col2:
        plan = PLAN_PRICES['yearly']
        st.markdown(f"""
        <div class="pricing-card featured">
            <div style="background: gold; color: black; padding: 5px 15px; border-radius: 20px; display: inline-block; margin-bottom: 10px;">⭐ پێشنیارکراو</div>
            <h3>📆 ساڵانە</h3>
            <div class="price-tag">{plan['price_text']}</div>
            <p>/ ساڵ</p>
            <p style="color: #ff4757;">💰 ٢ مانگ خۆرایی!</p>
            <hr>
            <ul class="feature-list">
        """, unsafe_allow_html=True)
        for f in plan['features']:
            st.markdown(f"<li>✅ {f}</li>", unsafe_allow_html=True)
        st.markdown("</ul></div>", unsafe_allow_html=True)
        if st.button("💳 کڕینی پلانی ساڵانە", key="buy_yearly", use_container_width=True):
            st.session_state.selected_plan = 'yearly'
            st.session_state.current_page = '💳 پارەدان'
            st.rerun()
    
    with col3:
        plan = PLAN_PRICES['lifetime']
        st.markdown(f"""
        <div class="pricing-card">
            <h3>💎 هەمیشەیی</h3>
            <div class="price-tag">{plan['price_text']}</div>
            <p>/ یەکجار</p>
            <hr>
            <ul class="feature-list">
        """, unsafe_allow_html=True)
        for f in plan['features']:
            st.markdown(f"<li>✅ {f}</li>", unsafe_allow_html=True)
        st.markdown("</ul></div>", unsafe_allow_html=True)
        if st.button("💳 کڕینی پلانی هەمیشەیی", key="buy_lifetime", use_container_width=True):
            st.session_state.selected_plan = 'lifetime'
            st.session_state.current_page = '💳 پارەدان'
            st.rerun()
    
    st.markdown("---")
    
    # License activation
    with st.expander("🔑 خاوەن لایسەنسی؟"):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### چالاککردنی لایسەنس")
            license_key = st.text_input("کۆدی لایسەنس", placeholder="DRD-XXXX-XXXX-XXXX")
            if st.button("✅ چالاککردن", use_container_width=True):
                if license_key:
                    with st.spinner("⏳ چالاکدەکرێت..."):
                        result = license_system.activate_license(license_key, st.session_state.device_id)
                    if result['status'] == 'success':
                        st.session_state.license_key = license_key
                        st.session_state.license_valid = True
                        st.success(result['message'])
                        st.rerun()
                    else:
                        st.error(result['message'])
            
            st.markdown("---")
            st.markdown("### 👤 چوونەژوورەوە (بەڕێوەبەر)")
            with st.form("admin_login"):
                username = st.text_input("ناوی بەکارهێنەر")
                password = st.text_input("ووشەی نهێنی", type="password")
                if st.form_submit_button("🔓 چوونەژوورەوە", use_container_width=True):
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

# ==================== PAYMENT PAGE ====================
def show_payment_page():
    st.markdown("### 💳 پارەدان")
    
    if 'selected_plan' not in st.session_state or not st.session_state.selected_plan:
        st.warning("تکایە یەکەم پلانێک هەڵبژێرە")
        if st.button("⬅️ گەڕانەوە بۆ پلانەکان"):
            st.session_state.current_page = '🏠 سەرەکی'
            st.rerun()
        return
    
    plan = st.session_state.selected_plan
    plan_info = PLAN_PRICES[plan]
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown(f"""
        <div class="glass-card">
            <h3>پلانی {plan}</h3>
            <div class="price-tag">{plan_info['price_text']}</div>
            <p>ماوە: {plan_info['duration']}</p>
            <hr>
            <h4>تایبەتمەندییەکان:</h4>
            <ul>
        """, unsafe_allow_html=True)
        for feature in plan_info['features']:
            st.markdown(f"<li>✅ {feature}</li>", unsafe_allow_html=True)
        st.markdown("</ul></div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 📝 زانیاری پارەدان")
        st.markdown(f"**نرخ:** {plan_info['price_text']}")
        st.markdown("---")
        
        st.markdown("### 📱 ڕێگاکانی پارەدان")
        st.info("""
        🔹 **فاست پی (FastPay)** - باوترین ڕێگای پارەدان لە عێراق
        🔹 **ئاسیا حەواڵە** - بەردەست لە هەموو شارەکان
        🔹 **زەین کاش (ZainCash)** - گونجاو بۆ بەکارهێنەرانی زەین
        """)
        
        st.markdown("---")
        
        st.markdown("### 📋 زانیاری پەیوەندی")
        
        user_name = st.text_input("👤 ناوی تەواو *", placeholder="ناوی تەواوت بنووسە")
        user_email = st.text_input("📧 ئیمەیڵ", placeholder="example@gmail.com")
        user_phone = st.text_input("📱 ژمارە مۆبایل *", placeholder="07XXXXXXXXX")
        
        st.markdown("---")
        
        st.markdown("### 🏦 هەنگاوەکانی پارەدان:")
        st.markdown(f"""
        1️⃣ پارەکە بنێرە بۆ یەکێک لەم ژمارانە:
        
        <div class="payment-info-box">
            <h4>{BANK_ACCOUNTS['فاست پی']['icon']} فاست پی: {BANK_ACCOUNTS['فاست پی']['number']}</h4>
            <p>ناوی خاوەن: {BANK_ACCOUNTS['فاست پی']['holder']}</p>
        </div>
        <div class="payment-info-box">
            <h4>{BANK_ACCOUNTS['ئاسیا حەواڵە']['icon']} ئاسیا حەواڵە: {BANK_ACCOUNTS['ئاسیا حەواڵە']['number']}</h4>
            <p>ناوی خاوەن: {BANK_ACCOUNTS['ئاسیا حەواڵە']['holder']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("### 📤 پشتڕاستکردنەوەی پارەدان")
        payment_method = st.selectbox("ڕێگای پارەدان *", ["فاست پی", "ئاسیا حەواڵە", "زەین کاش", "بانک"])
        payment_ref = st.text_input("ژمارەی سەرچاوەی پارەدان (Reference)", placeholder="کۆدی پشتڕاستکردنەوە یان ژمارەی مامەڵە")
        
        st.warning("⚠️ دوای ناردنی پارە، کلیلی لایسەنس دوای پشتڕاستکردنەوە دەنێردرێت بۆ ئیمەیڵت یان لێرە پیشان دەدرێت")
        
        if st.button("📤 ناردنی داواکاری", use_container_width=True, type="primary"):
            if not user_name or not user_phone:
                st.error("❌ ناوی تەواو و ژمارە مۆبایل پێویستە!")
            else:
                # تۆمارکردنی داواکاری
                license_key = license_system.register_payment_request(
                    user_name=user_name,
                    user_email=user_email,
                    user_phone=user_phone,
                    plan_type=plan,
                    amount=plan_info['price'],
                    currency='IQD' if CURRENCY == 'IQD' else 'USD',
                    payment_method=payment_method,
                    payment_ref=payment_ref
                )
                
                st.session_state.payment_submitted = True
                st.session_state.pending_license = license_key
                st.session_state.pending_plan = plan
                
                st.success("""
                ✅ داواکاری پارەدان تۆمارکرا!
                
                📋 **هەنگاوی دواتر:**
                1. پارەکە بنێرە بۆ یەکێک لە ژمارەکان
                2. پشتڕاستکردنەوەکە بنێرە بۆ:
                   - تێلیگرام: {} 
                   - واتسئەپ: {}
                
                ⏰ دوای پشتڕاستکردنەوە، کلیلی لایسەنس دەنێردرێت بۆ ئیمەیڵت
                """.format(ADMIN_TELEGRAM, ADMIN_WHATSAPP))
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("⬅️ گەڕانەوە بۆ پلانەکان"):
        st.session_state.current_page = '🏠 سەرەکی'
        st.rerun()

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
                st.warning("⚠️ لایسەنسەکە بەسەرچووە یان ناچالاکە")
    
    if not st.session_state.get('license_valid') and st.session_state.get('user_role') != 'admin':
        if st.session_state.current_page == '💳 پارەدان':
            show_payment_page()
        else:
            show_landing_page()
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
        
        pages = ["📊 داشبۆرد", "💊 دەرمانەکان", "🧪 پشکنینەکان", "📝 تێبینییەکان"]
        
        if st.session_state.get('user_role') == 'admin':
            pages.extend(["🔑 لایسەنس", "👥 بەکارهێنەران", "💰 پارەدانەکان"])
        
        pages.append("⚙️ ڕێکخستنەکان")
        
        for page in pages:
            if st.button(page, use_container_width=True, key=f"nav_{page}"):
                st.session_state.current_page = page
                st.rerun()
        
        st.markdown("---")
        
        if st.session_state.get('license_key'):
            st.info(f"🔑 لایسەنس: {st.session_state.license_key[:16]}...")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚪 دەرچوون", use_container_width=True):
                for key in ['logged_in', 'license_valid', 'license_key', 'user_role']:
                    st.session_state[key] = False if key != 'license_key' else None
                st.session_state.current_page = '🏠 سەرەکی'
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
    elif page == "💰 پارەدانەکان" and st.session_state.get('user_role') == 'admin':
        show_payment_manager()
    elif page == "⚙️ ڕێکخستنەکان":
        show_settings_page()

# ==================== ADMIN PAYMENT MANAGER ====================
def show_payment_manager():
    if st.session_state.get('user_role') != 'admin':
        st.error("⛔ تەنها بۆ بەڕێوەبەر")
        st.stop()
    
    st.markdown("### 💰 بەڕێوەبەری پارەدانەکان")
    
    tab1, tab2, tab3 = st.tabs(["⏳ چاوەڕوان", "✅ تەواوکراو", "📊 ئامار"])
    
    with tab1:
        st.markdown("#### ⏳ داواکارییە چاوەڕوانەکان")
        pending = license_system.get_pending_payments()
        
        if pending:
            for payment in pending:
                with st.container():
                    st.markdown(f"""
                    <div class="glass-card" style="border-left: 4px solid #ffa502;">
                        <h4>👤 {payment[1]} - {PLAN_PRICES.get(payment[3], {}).get('price_text', payment[4])}</h4>
                        <p>📧 {payment[2] or 'نییە'} | 📱 {payment[3] or 'نییە'}</p>
                        <p>💳 {payment[5]} | 🔢 سەرچاوە: {payment[6] or 'نییە'}</p>
                        <p>🔑 لایسەنس: <code>{payment[7]}</code></p>
                        <p>📅 {payment[9][:19] if payment[9] else ''}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✅ پشتڕاستکردنەوە", key=f"verify_{payment[0]}", use_container_width=True):
                            license_system.verify_payment_by_admin(payment[7])
                            st.success("✅ لایسەنس چالاک کرا و بۆ بەکارهێنەر نێردرا!")
                            st.rerun()
                    with col2:
                        if st.button("❌ ڕەتکردنەوە", key=f"reject_{payment[0]}", use_container_width=True):
                            conn = sqlite3.connect('licenses.db')
                            c = conn.cursor()
                            c.execute("UPDATE payments SET status='rejected' WHERE id=?", (payment[0],))
                            conn.commit()
                            conn.close()
                            st.warning("ڕەتکرایەوە")
                            st.rerun()
        else:
            st.info("هیچ داواکارییەکی چاوەڕوان نییە ✅")
    
    with tab2:
        payments = license_system.get_all_payments()
        completed = [p for p in payments if p[8] == 'completed']
        if completed:
            for payment in completed:
                st.markdown(f"""
                <div class="glass-card" style="border-left: 4px solid #2ed573;">
                    <p>✅ {payment[1]} - {PLAN_PRICES.get(payment[3], {}).get('price_text', payment[4])}</p>
                    <p>📅 {payment[9][:10] if payment[9] else ''} | 💳 {payment[5]}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("هیچ پارەدانێکی تەواوکراو نییە")
    
    with tab3:
        stats = license_system.get_payment_stats()
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("💰 کۆی داهات", f"{stats['total_revenue']:,.0f} دینار")
        with col2:
            st.metric("📦 کۆی فرۆشتن", stats['total_payments'])
        with col3:
            st.metric("📈 فرۆشتنی ئەمڕۆ", stats['today_payments'])
        with col4:
            st.metric("⏳ چاوەڕوان", stats['pending_payments'])

# ==================== OTHER PAGES ====================
# هەموو page functionـەکانی تر (داشبۆرد، دەرمان، پشکنین، تێبینی، لایسەنس، بەکارهێنەران، ڕێکخستنەکان)
# وەک کۆدی پێشوو دەمێننەوە - تەنها function ناوەکان وەک show_dashboard, show_medicines_page, show_lab_tests_page, 
# show_notes_page, show_license_manager, show_users_page, show_settings_page

# ئەم functionـانە هەر وەک کۆدی پێشووت دەبن، بۆ کورتکردنەوە لێرە نایاننووسمەوە
# دەتوانیت لە کۆدی پێشووتەوە کۆپی بکەیت

# ==================== RUN ====================
if __name__ == "__main__":
    main()
