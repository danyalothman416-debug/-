"""
🏥 دکتۆر دانیال - پلاتفۆرمی خوێندنی پزیشکی
وەشانی سۆرس کۆد - بۆ گیت هەب و بەکارهێنانی گشتی
هەموو مافەکان پارێزراون © 2026
"""

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import hashlib
import os
import secrets
import string
import uuid
import json
import base64
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import time
import shutil

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="دکتۆر دانیال - پلاتفۆرمی پزیشکی",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== SESSION STATE INITIALIZATION ====================
def init_session_state():
    defaults = {
        'language': 'کوردی',
        'dark_mode': True,
        'current_page': '📊 داشبۆرد',
        'logged_in': False,
        'username': '',
        'user_id': None,
        'user_role': None,
        'device_id': str(uuid.uuid4()),
        'session_start': datetime.now(),
        'last_activity': datetime.now(),
        'favorites': {'medicines': [], 'tests': [], 'notes': []},
        'recently_viewed': [],
        'audit_logs': [],
        'ai_chat_history': [],
        'notifications': [],
        'font_size': 'medium',
        'sidebar_collapsed': False,
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# ==================== DATABASE SETUP ====================
class DatabaseManager:
    def __init__(self):
        self.db_path = 'medical_platform.db'
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        conn = self.get_connection()
        c = conn.cursor()
        
        # Users table
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      username TEXT UNIQUE NOT NULL,
                      email TEXT UNIQUE,
                      password_hash TEXT NOT NULL,
                      role TEXT DEFAULT 'student',
                      two_factor_enabled INTEGER DEFAULT 0,
                      two_factor_secret TEXT,
                      profile_image TEXT,
                      phone TEXT,
                      specialization TEXT,
                      created_at TEXT,
                      last_login TEXT,
                      is_active INTEGER DEFAULT 1)''')
        
        # Sessions table
        c.execute('''CREATE TABLE IF NOT EXISTS sessions
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id INTEGER,
                      session_token TEXT UNIQUE,
                      device_id TEXT,
                      ip_address TEXT,
                      created_at TEXT,
                      expires_at TEXT,
                      is_active INTEGER DEFAULT 1,
                      FOREIGN KEY (user_id) REFERENCES users(id))''')
        
        # Audit logs
        c.execute('''CREATE TABLE IF NOT EXISTS audit_logs
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id INTEGER,
                      action TEXT,
                      table_name TEXT,
                      record_id INTEGER,
                      details TEXT,
                      ip_address TEXT,
                      created_at TEXT)''')
        
        # Medicines table (Enhanced)
        c.execute('''CREATE TABLE IF NOT EXISTS medicines
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT NOT NULL,
                      generic_name TEXT,
                      brand_names TEXT,
                      drug_class TEXT,
                      category TEXT,
                      pregnancy_category TEXT,
                      lactation_safety TEXT,
                      contraindications TEXT,
                      side_effects TEXT,
                      adult_dose TEXT,
                      pediatric_dose TEXT,
                      renal_dose_adjustment TEXT,
                      hepatic_dose_adjustment TEXT,
                      drug_interactions TEXT,
                      mechanism_of_action TEXT,
                      route_of_administration TEXT,
                      storage_instructions TEXT,
                      priority TEXT DEFAULT 'medium',
                      color_label TEXT DEFAULT '#667eea',
                      tags TEXT,
                      notes TEXT,
                      favorite_count INTEGER DEFAULT 0,
                      view_count INTEGER DEFAULT 0,
                      pinned INTEGER DEFAULT 0,
                      created_by INTEGER,
                      created_at TEXT,
                      updated_at TEXT,
                      FOREIGN KEY (created_by) REFERENCES users(id))''')
        
        # Lab Tests table (Enhanced)
        c.execute('''CREATE TABLE IF NOT EXISTS lab_tests
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT NOT NULL,
                      category TEXT,
                      purpose TEXT,
                      normal_range_adult TEXT,
                      normal_range_pediatric TEXT,
                      normal_range_male TEXT,
                      normal_range_female TEXT,
                      preparation TEXT,
                      clinical_interpretation TEXT,
                      related_diseases TEXT,
                      specimen_type TEXT,
                      turnaround_time TEXT,
                      priority TEXT DEFAULT 'medium',
                      color_label TEXT DEFAULT '#667eea',
                      tags TEXT,
                      notes TEXT,
                      favorite_count INTEGER DEFAULT 0,
                      view_count INTEGER DEFAULT 0,
                      pinned INTEGER DEFAULT 0,
                      created_by INTEGER,
                      created_at TEXT,
                      updated_at TEXT,
                      FOREIGN KEY (created_by) REFERENCES users(id))''')
        
        # Notes table (Enhanced)
        c.execute('''CREATE TABLE IF NOT EXISTS medical_notes
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      title TEXT NOT NULL,
                      content TEXT,
                      content_markdown TEXT,
                      category TEXT,
                      tags TEXT,
                      image_path TEXT,
                      pdf_path TEXT,
                      is_bookmarked INTEGER DEFAULT 0,
                      view_count INTEGER DEFAULT 0,
                      created_by INTEGER,
                      created_at TEXT,
                      updated_at TEXT,
                      FOREIGN KEY (created_by) REFERENCES users(id))''')
        
        # Categories
        c.execute('''CREATE TABLE IF NOT EXISTS categories
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT NOT NULL,
                      type TEXT,
                      color TEXT,
                      icon TEXT,
                      created_at TEXT)''')
        
        # Notifications
        c.execute('''CREATE TABLE IF NOT EXISTS notifications
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id INTEGER,
                      title TEXT,
                      message TEXT,
                      type TEXT,
                      is_read INTEGER DEFAULT 0,
                      link TEXT,
                      created_at TEXT,
                      FOREIGN KEY (user_id) REFERENCES users(id))''')
        
        # Announcements
        c.execute('''CREATE TABLE IF NOT EXISTS announcements
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      title TEXT,
                      content TEXT,
                      priority TEXT DEFAULT 'normal',
                      is_active INTEGER DEFAULT 1,
                      created_by INTEGER,
                      created_at TEXT,
                      expires_at TEXT)''')
        
        # Feedback
        c.execute('''CREATE TABLE IF NOT EXISTS feedback
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id INTEGER,
                      rating INTEGER,
                      comment TEXT,
                      category TEXT,
                      created_at TEXT,
                      FOREIGN KEY (user_id) REFERENCES users(id))''')
        
        # Disease Encyclopedia
        c.execute('''CREATE TABLE IF NOT EXISTS diseases
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT NOT NULL,
                      icd10_code TEXT,
                      description TEXT,
                      symptoms TEXT,
                      diagnosis TEXT,
                      treatment TEXT,
                      prevention TEXT,
                      category TEXT,
                      tags TEXT,
                      created_at TEXT)''')
        
        # Medical Calculators History
        c.execute('''CREATE TABLE IF NOT EXISTS calculator_history
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id INTEGER,
                      calculator_type TEXT,
                      inputs TEXT,
                      result TEXT,
                      created_at TEXT,
                      FOREIGN KEY (user_id) REFERENCES users(id))''')
        
        # Drug Interactions table
        c.execute('''CREATE TABLE IF NOT EXISTS drug_interactions
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      drug1_id INTEGER,
                      drug2_id INTEGER,
                      severity TEXT,
                      description TEXT,
                      recommendation TEXT,
                      FOREIGN KEY (drug1_id) REFERENCES medicines(id),
                      FOREIGN KEY (drug2_id) REFERENCES medicines(id))''')
        
        # Insert default admin
        c.execute("SELECT * FROM users WHERE username='admin'")
        if not c.fetchone():
            hashed = hashlib.sha256('Admin@2024'.encode()).hexdigest()
            c.execute("""INSERT INTO users 
                         (username, email, password_hash, role, created_at)
                         VALUES (?, ?, ?, ?, ?)""",
                      ('admin', 'admin@drdanial.com', hashed, 'admin', datetime.now().isoformat()))
        
        # Insert default categories
        default_categories = [
            ('Cardiology', 'medicine', '#ff6b6b', '❤️'),
            ('Neurology', 'medicine', '#feca57', '🧠'),
            ('Gastroenterology', 'medicine', '#48dbfb', '🫄'),
            ('Endocrinology', 'medicine', '#1dd1a1', '🦋'),
            ('Infectious Disease', 'medicine', '#ff4757', '🦠'),
            ('Hematology', 'test', '#667eea', '🩸'),
            ('Biochemistry', 'test', '#764ba2', '🧪'),
            ('Microbiology', 'test', '#ff9ff3', '🔬'),
            ('Immunology', 'test', '#5f27cd', '🛡️'),
        ]
        
        for name, type_, color, icon in default_categories:
            c.execute("SELECT * FROM categories WHERE name=?", (name,))
            if not c.fetchone():
                c.execute("""INSERT INTO categories (name, type, color, icon, created_at)
                             VALUES (?, ?, ?, ?, ?)""",
                          (name, type_, color, icon, datetime.now().isoformat()))
        
        # Insert sample data
        self.insert_sample_data(c)
        
        conn.commit()
        conn.close()
    
    def insert_sample_data(self, c):
        """Insert sample medicines, tests, and diseases"""
        now = datetime.now().isoformat()
        
        # Sample medicines
        c.execute("SELECT COUNT(*) FROM medicines")
        if c.fetchone()[0] == 0:
            medicines = [
                ('Paracetamol (Acetaminophen)', 'Acetaminophen', 'Panadol, Tylenol, Calpol',
                 'Analgesic', 'Pain Management', 'B', 'Safe', 
                 'Liver disease, alcoholism', 'Nausea, rash (rare)',
                 '500-1000mg q6h, max 4g/day', '10-15mg/kg q6h, max 75mg/kg/day',
                 'No adjustment needed', 'Avoid in severe hepatic impairment',
                 'Warfarin (slight INR increase)', 'COX inhibitor in CNS',
                 'Oral, IV, Rectal', 'Room temperature', 'high', '#ff6b6b',
                 'pain,fever,headache,analgesic', 'First-line for pain and fever'),
                
                ('Metformin', 'Metformin HCl', 'Glucophage, Fortamet',
                 'Biguanide', 'Diabetes', 'B', 'Limited data, caution advised',
                 'Renal impairment (eGFR<30), metabolic acidosis', 'GI upset, diarrhea, B12 deficiency',
                 '500mg BID, max 2550mg/day', 'Not recommended <10 years',
                 'Stop if eGFR<30', 'Avoid in hepatic impairment',
                 'Contrast dye (risk of lactic acidosis)', 'Decreases hepatic glucose production',
                 'Oral', 'Room temperature', 'high', '#1dd1a1',
                 'diabetes,sugar,insulin,type2', 'First-line for type 2 diabetes'),
                
                ('Atorvastatin', 'Atorvastatin Calcium', 'Lipitor, Atorva',
                 'Statin', 'Cardiovascular', 'X', 'Contraindicated',
                 'Active liver disease, pregnancy', 'Myalgia, elevated LFTs',
                 '10-80mg once daily', 'Not recommended <10 years',
                 'No adjustment needed', 'Avoid in active liver disease',
                 'CYP3A4 inhibitors increase risk of myopathy', 'HMG-CoA reductase inhibitor',
                 'Oral', 'Room temperature', 'high', '#667eea',
                 'cholesterol,lipid,statin,heart', 'Take at night for best effect'),
                
                ('Amoxicillin', 'Amoxicillin', 'Amoxil, Trimox, Augmentin (with clavulanate)',
                 'Penicillin Antibiotic', 'Infectious Disease', 'B', 'Safe',
                 'Penicillin allergy, mononucleosis', 'Rash, diarrhea, allergic reactions',
                 '250-500mg TID', '20-50mg/kg/day divided TID',
                 'Adjust dose if CrCl<30', 'No adjustment needed',
                 'Probenecid increases levels, warfarin (INR changes)',
                 'Cell wall synthesis inhibitor', 'Oral, IV', 'Refrigerate suspension', 'medium', '#feca57',
                 'antibiotic,infection,bacteria,respiratory', 'Complete full course'),
            ]
            
            for med in medicines:
                c.execute("""INSERT INTO medicines 
                             (name, generic_name, brand_names, drug_class, category,
                              pregnancy_category, lactation_safety, contraindications,
                              side_effects, adult_dose, pediatric_dose, renal_dose_adjustment,
                              hepatic_dose_adjustment, drug_interactions, mechanism_of_action,
                              route_of_administration, storage_instructions, priority,
                              color_label, tags, notes, created_at, updated_at)
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                          med + (now, now))
        
        # Sample lab tests
        c.execute("SELECT COUNT(*) FROM lab_tests")
        if c.fetchone()[0] == 0:
            tests = [
                ('Complete Blood Count (CBC)', 'Hematology',
                 'Evaluate overall health, detect disorders', 
                 'RBC: 4.5-5.5, WBC: 4-11, Hb: 13-17, Hct: 40-50%, Platelets: 150-400',
                 'RBC: 4.0-5.0, WBC: 5-15, Hb: 11-15', 
                 'RBC: 4.5-5.5, Hb: 13-17', 'RBC: 4.0-5.0, Hb: 12-15',
                 'No special preparation', 'Abnormal values indicate various conditions',
                 'Anemia, infection, leukemia, bleeding disorders',
                 'Whole blood (EDTA tube)', '1-2 hours', 'high', '#667eea',
                 'blood,CBC,hematology,complete', 'Basic hematology panel'),
                
                ('Fasting Blood Glucose', 'Biochemistry',
                 'Screen for diabetes mellitus', '70-110 mg/dL (3.9-6.1 mmol/L)',
                 '60-100 mg/dL', '70-110 mg/dL', '70-110 mg/dL',
                 'Fast for 8-12 hours, water allowed', 
                 '>126 mg/dL indicates diabetes, 100-125 prediabetes',
                 'Diabetes mellitus, hypoglycemia, metabolic syndrome',
                 'Serum (SST tube)', '1 hour', 'high', '#ff6b6b',
                 'sugar,diabetes,glucose,fasting', 'Most common diabetes screening test'),
                
                ('HbA1c (Glycated Hemoglobin)', 'Biochemistry',
                 'Monitor long-term glucose control', '<5.7% normal, 5.7-6.4% prediabetes, >6.5% diabetes',
                 '<5.7%', '<5.7%', '<5.7%',
                 'No fasting required', 'Reflects average glucose over 2-3 months',
                 'Diabetes mellitus, hemoglobinopathies',
                 'Whole blood (EDTA tube)', '1-2 hours', 'high', '#feca57',
                 'diabetes,HbA1c,sugar,long-term', 'Gold standard for diabetes monitoring'),
            ]
            
            for test in tests:
                c.execute("""INSERT INTO lab_tests 
                             (name, category, purpose, normal_range_adult, normal_range_pediatric,
                              normal_range_male, normal_range_female, preparation,
                              clinical_interpretation, related_diseases, specimen_type,
                              turnaround_time, priority, color_label, tags, notes, created_at, updated_at)
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                          test + (now, now))
        
        # Sample diseases
        c.execute("SELECT COUNT(*) FROM diseases")
        if c.fetchone()[0] == 0:
            diseases = [
                ('Essential Hypertension', 'I10', 'Chronic medical condition with elevated blood pressure',
                 'Often asymptomatic, headaches, dizziness, nosebleeds',
                 'BP measurement >130/80 on multiple occasions',
                 'Lifestyle changes, antihypertensive medications',
                 'Healthy diet, exercise, stress management',
                 'Cardiovascular', 'hypertension,BP,heart'),
                
                ('Type 2 Diabetes Mellitus', 'E11', 'Metabolic disorder with insulin resistance',
                 'Polyuria, polydipsia, polyphagia, weight loss, fatigue',
                 'Fasting glucose >126, HbA1c >6.5%, OGTT >200',
                 'Metformin, lifestyle changes, insulin if needed',
                 'Healthy diet, exercise, weight management',
                 'Endocrine', 'diabetes,sugar,metabolic'),
            ]
            
            for disease in diseases:
                c.execute("""INSERT INTO diseases 
                             (name, icd10_code, description, symptoms, diagnosis,
                              treatment, prevention, category, tags, created_at)
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                          disease + (now,))

# Initialize database
db = DatabaseManager()

# ==================== AUTHENTICATION SYSTEM ====================
class AuthSystem:
    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def verify_password(password, hashed):
        return hashlib.sha256(password.encode()).hexdigest() == hashed
    
    @staticmethod
    def login(username, password):
        conn = db.get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND is_active=1", (username,))
        user = c.fetchone()
        conn.close()
        
        if user and AuthSystem.verify_password(password, user[3]):
            # Update last login
            conn = db.get_connection()
            c = conn.cursor()
            c.execute("UPDATE users SET last_login=? WHERE id=?", 
                     (datetime.now().isoformat(), user[0]))
            conn.commit()
            conn.close()
            return {'success': True, 'user': user}
        return {'success': False, 'message': 'Invalid credentials'}
    
    @staticmethod
    def register(username, email, password, role='student'):
        conn = db.get_connection()
        c = conn.cursor()
        hashed = AuthSystem.hash_password(password)
        try:
            c.execute("""INSERT INTO users (username, email, password_hash, role, created_at)
                         VALUES (?, ?, ?, ?, ?)""",
                      (username, email, hashed, role, datetime.now().isoformat()))
            conn.commit()
            return {'success': True, 'user_id': c.lastrowid}
        except sqlite3.IntegrityError:
            return {'success': False, 'message': 'Username or email already exists'}
        finally:
            conn.close()
    
    @staticmethod
    def check_session_timeout():
        if 'last_activity' in st.session_state:
            timeout = timedelta(minutes=30)
            if datetime.now() - st.session_state.last_activity > timeout:
                st.session_state.logged_in = False
                st.session_state.username = ''
                st.warning("⏰ Session expired. Please login again.")
                return True
        return False

# ==================== AUDIT LOGGER ====================
class AuditLogger:
    @staticmethod
    def log(user_id, action, table_name, record_id=None, details=None):
        conn = db.get_connection()
        c = conn.cursor()
        c.execute("""INSERT INTO audit_logs 
                     (user_id, action, table_name, record_id, details, created_at)
                     VALUES (?, ?, ?, ?, ?, ?)""",
                  (user_id, action, table_name, record_id, details, datetime.now().isoformat()))
        conn.commit()
        conn.close()

# ==================== CSS STYLING ====================
def load_css():
    dark_mode = st.session_state.get('dark_mode', True)
    
    if dark_mode:
        bg = "#0f0c29"
        card_bg = "rgba(255,255,255,0.05)"
        glass_bg = "rgba(255,255,255,0.08)"
        text = "#ffffff"
        border = "rgba(255,255,255,0.1)"
    else:
        bg = "#f5f7fa"
        card_bg = "#ffffff"
        glass_bg = "rgba(255,255,255,0.9)"
        text = "#1a1a2e"
        border = "rgba(0,0,0,0.1)"
    
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        * {{ font-family: 'Inter', sans-serif; }}
        
        .stApp {{
            background: linear-gradient(135deg, {bg}, {bg});
            color: {text};
        }}
        
        .glass-card {{
            background: {glass_bg};
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-radius: 24px;
            border: 1px solid {border};
            padding: 28px;
            margin: 14px 0;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            animation: fadeInUp 0.5s ease-out;
        }}
        
        .glass-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 12px 40px rgba(0,0,0,0.2);
        }}
        
        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(30px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.05); }}
        }}
        
        .main-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 24px;
            padding: 40px;
            text-align: center;
            color: white;
            margin-bottom: 30px;
            box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);
            animation: fadeInUp 0.8s ease-out;
        }}
        
        .gradient-text {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
        }}
        
        .stButton > button {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 14px;
            padding: 12px 24px;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            width: 100%;
            cursor: pointer;
            font-size: 15px;
        }}
        
        .stButton > button:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 30px rgba(102, 126, 234, 0.6);
        }}
        
        .stat-card {{
            background: {glass_bg};
            border-radius: 20px;
            padding: 24px;
            text-align: center;
            border: 1px solid {border};
            transition: all 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
        }}
        
        .badge {{
            display: inline-block;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            margin: 3px;
        }}
        
        .badge-primary {{ background: #667eea; color: white; }}
        .badge-success {{ background: #2ed573; color: white; }}
        .badge-warning {{ background: #ffa502; color: white; }}
        .badge-danger {{ background: #ff4757; color: white; }}
        .badge-info {{ background: #1e90ff; color: white; }}
        
        .skeleton {{
            background: linear-gradient(90deg, {glass_bg} 25%, rgba(255,255,255,0.15) 50%, {glass_bg} 75%);
            background-size: 200% 100%;
            animation: shimmer 1.5s infinite;
            border-radius: 12px;
            height: 60px;
            margin: 10px 0;
        }}
        
        @keyframes shimmer {{
            0% {{ background-position: -200% 0; }}
            100% {{ background-position: 200% 0; }}
        }}
        
        /* RTL Support */
        [dir="rtl"] {{
            direction: rtl;
            text-align: right;
        }}
        
        [dir="ltr"] {{
            direction: ltr;
            text-align: left;
        }}
        
        /* Scrollbar */
        ::-webkit-scrollbar {{
            width: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: transparent;
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            border-radius: 10px;
        }}
        
        /* Mobile responsive */
        @media (max-width: 768px) {{
            .glass-card {{ padding: 16px; margin: 8px 0; }}
            .main-header {{ padding: 20px; }}
            .stat-card {{ padding: 16px; }}
        }}
        
        /* Print styles */
        @media print {{
            .stButton, .stDownloadButton, .sidebar {{ display: none !important; }}
            .glass-card {{ box-shadow: none; border: 1px solid #ddd; }}
        }}
    </style>
    """, unsafe_allow_html=True)

# ==================== LANGUAGE SYSTEM ====================
LANGUAGES = {
    'کوردی': {
        'dashboard': '📊 داشبۆرد',
        'medicines': '💊 دەرمانەکان',
        'lab_tests': '🧪 پشکنینەکان',
        'notes': '📝 تێبینییەکان',
        'ai_assistant': '🤖 یارمەتیدەری زیرەک',
        'calculators': '📐 حسابکەری پزیشکی',
        'diseases': '📚 نەخۆشییەکان',
        'search': '🔍 گەڕان',
        'settings': '⚙️ ڕێکخستنەکان',
        'login': '🔓 چوونەژوورەوە',
        'logout': '🚪 دەرچوون',
        'welcome': 'بەخێربێیت',
        'add_medicine': '➕ زیادکردنی دەرمان',
        'edit_medicine': '✏️ دەستکاری دەرمان',
        'delete': '🗑️ سڕینەوە',
        'save': '💾 پاشەکەوت',
        'cancel': '❌ پەشیمانبوونەوە',
        'search_placeholder': 'گەڕان...',
        'no_results': 'هیچ ئەنجامێک نەدۆزرایەوە',
        'loading': 'چاوەڕوان بە...',
        'error': 'هەڵەیەک ڕوویدا',
        'success': 'بە سەرکەوتوویی ئەنجامدرا',
    },
    'English': {
        'dashboard': '📊 Dashboard',
        'medicines': '💊 Medicines',
        'lab_tests': '🧪 Lab Tests',
        'notes': '📝 Notes',
        'ai_assistant': '🤖 AI Assistant',
        'calculators': '📐 Medical Calculators',
        'diseases': '📚 Diseases',
        'search': '🔍 Search',
        'settings': '⚙️ Settings',
        'login': '🔓 Login',
        'logout': '🚪 Logout',
        'welcome': 'Welcome',
        'add_medicine': '➕ Add Medicine',
        'edit_medicine': '✏️ Edit Medicine',
        'delete': '🗑️ Delete',
        'save': '💾 Save',
        'cancel': '❌ Cancel',
        'search_placeholder': 'Search...',
        'no_results': 'No results found',
        'loading': 'Loading...',
        'error': 'An error occurred',
        'success': 'Successfully completed',
    }
}

def t(key):
    """Translate function"""
    lang = st.session_state.get('language', 'English')
    return LANGUAGES.get(lang, LANGUAGES['English']).get(key, key)

# ==================== MAIN APPLICATION ====================
def main():
    load_css()
    
    # Initialize database
    db = DatabaseManager()
    
    # Check session timeout
    if st.session_state.get('logged_in'):
        if AuthSystem.check_session_timeout():
            st.rerun()
    
    # ========== LOGIN PAGE ==========
    if not st.session_state.get('logged_in'):
        show_login_page()
        return
    
    # Update last activity
    st.session_state.last_activity = datetime.now()
    
    # ========== MAIN APPLICATION CONTENT ==========
    
    # Header
    lang = st.session_state.get('language', 'English')
    welcome_text = 'بەخێربێیت' if lang == 'کوردی' else 'Welcome'
    
    st.markdown(f"""
    <div class="main-header">
        <h1 style="font-size: 2.5rem; font-weight: 700;">🏥 دکتۆر دانیال</h1>
        <p style="font-size: 1.2rem; opacity: 0.9;">{welcome_text}, {st.session_state.username}! 👋</p>
        <p style="font-size: 0.9rem; opacity: 0.7;">{datetime.now().strftime('%A, %B %d, %Y')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick actions row
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        if st.button("💊 " + t('add_medicine'), use_container_width=True):
            st.session_state.current_page = '💊 دەرمانەکان'
            st.session_state.show_add_medicine = True
            st.rerun()
    with col2:
        if st.button("🧪 + پشکنین", use_container_width=True):
            st.session_state.current_page = '🧪 پشکنینەکان'
            st.session_state.show_add_test = True
            st.rerun()
    with col3:
        if st.button("📝 + تێبینی", use_container_width=True):
            st.session_state.current_page = '📝 تێبینییەکان'
            st.session_state.show_add_note = True
            st.rerun()
    with col4:
        if st.button("🤖 AI", use_container_width=True):
            st.session_state.current_page = '🤖 یارمەتیدەری زیرەک'
            st.rerun()
    with col5:
        if st.button("📐 حسابکەر", use_container_width=True):
            st.session_state.current_page = '📐 حسابکەری پزیشکی'
            st.rerun()
    with col6:
        if st.button("🔄 نوێکردنەوە", use_container_width=True):
            st.rerun()
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🏥 " + t('dashboard'))
        
        # User profile section
        st.markdown(f"""
        <div style="text-align: center; padding: 15px;">
            <div style="width: 60px; height: 60px; background: linear-gradient(135deg, #667eea, #764ba2); 
                        border-radius: 50%; display: inline-flex; align-items: center; justify-content: center;
                        font-size: 24px; color: white; margin-bottom: 10px;">
                {st.session_state.username[0].upper()}
            </div>
            <p style="font-weight: 600; margin: 5px 0;">{st.session_state.username}</p>
            <span class="badge badge-primary">{st.session_state.user_role}</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation
        pages = [
            "📊 داشبۆرد",
            "💊 دەرمانەکان",
            "🧪 پشکنینەکان",
            "📝 تێبینییەکان",
            "📚 نەخۆشییەکان",
            "🤖 یارمەتیدەری زیرەک",
            "📐 حسابکەری پزیشکی",
        ]
        
        if st.session_state.user_role == 'admin':
            pages.extend([
                "👥 بەکارهێنەران",
                "📋 ڕاپۆرتەکان",
                "🔔 ڕاگەیاندنەکان",
                "📊 ئامارەکان",
            ])
        
        pages.append("⚙️ ڕێکخستنەکان")
        
        for page in pages:
            icon = page.split()[0]
            if st.button(page, use_container_width=True, key=f"nav_{page}"):
                st.session_state.current_page = page
                st.rerun()
        
        st.markdown("---")
        
        # Language switcher
        lang_options = ['English', 'کوردی']
        current_lang = st.session_state.get('language', 'English')
        lang_index = lang_options.index(current_lang) if current_lang in lang_options else 0
        selected_lang = st.selectbox("🌍 Language / زمان", lang_options, index=lang_index)
        if selected_lang != current_lang:
            st.session_state.language = selected_lang
            st.rerun()
        
        # Dark mode toggle
        dark_mode = st.toggle("🌙 Dark Mode", value=st.session_state.get('dark_mode', True))
        if dark_mode != st.session_state.dark_mode:
            st.session_state.dark_mode = dark_mode
            st.rerun()
        
        st.markdown("---")
        
        if st.button("🚪 " + t('logout'), use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ''
            st.session_state.user_role = None
            st.rerun()
    
    # ========== PAGE ROUTING ==========
    page = st.session_state.get('current_page', '📊 داشبۆرد')
    
    if page == "📊 داشبۆرد":
        show_dashboard()
    elif page == "💊 دەرمانەکان":
        show_medicines_page()
    elif page == "🧪 پشکنینەکان":
        show_lab_tests_page()
    elif page == "📝 تێبینییەکان":
        show_notes_page()
    elif page == "📚 نەخۆشییەکان":
        show_diseases_page()
    elif page == "🤖 یارمەتیدەری زیرەک":
        show_ai_assistant()
    elif page == "📐 حسابکەری پزیشکی":
        show_calculators()
    elif page == "👥 بەکارهێنەران":
        show_users_page()
    elif page == "📋 ڕاپۆرتەکان":
        show_reports_page()
    elif page == "🔔 ڕاگەیاندنەکان":
        show_announcements_page()
    elif page == "📊 ئامارەکان":
        show_statistics_page()
    elif page == "⚙️ ڕێکخستنەکان":
        show_settings_page()

# ==================== LOGIN PAGE ====================
def show_login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 50px 0;">
            <h1 style="font-size: 4rem;">🏥</h1>
            <h1 style="background: linear-gradient(135deg, #667eea, #764ba2); 
                       -webkit-background-clip: text; 
                       -webkit-text-fill-color: transparent;
                       font-size: 3rem;">
                دکتۆر دانیال
            </h1>
            <p style="font-size: 1.2rem; opacity: 0.7;">پلاتفۆرمی خوێندنی پزیشکی</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔓 چوونەژوورەوە", "📝 تۆمارکردن"])
        
        with tab1:
            with st.form("login_form"):
                username = st.text_input("👤 ناوی بەکارهێنەر")
                password = st.text_input("🔒 ووشەی نهێنی", type="password")
                
                col1, col2 = st.columns(2)
                with col1:
                    submitted = st.form_submit_button("🔓 چوونەژوورەوە", use_container_width=True)
                with col2:
                    st.markdown("<br>", unsafe_allow_html=True)
                
                if submitted:
                    if username and password:
                        result = AuthSystem.login(username, password)
                        if result['success']:
                            user = result['user']
                            st.session_state.logged_in = True
                            st.session_state.username = username
                            st.session_state.user_id = user[0]
                            st.session_state.user_role = user[4]
                            st.session_state.last_activity = datetime.now()
                            
                            # Log audit
                            AuditLogger.log(user[0], 'LOGIN', 'users', user[0], 'User logged in')
                            
                            st.success("✅ بەخێربێیت!")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error("❌ ناوی بەکارهێنەر یان ووشەی نهێنی هەڵەیە")
                    else:
                        st.warning("⚠️ تکایە هەموو خانەکان پڕ بکەوە")
        
        with tab2:
            with st.form("register_form"):
                new_username = st.text_input("👤 ناوی بەکارهێنەر *")
                email = st.text_input("📧 ئیمەیڵ *")
                new_password = st.text_input("🔒 ووشەی نهێنی *", type="password")
                confirm_password = st.text_input("🔒 دووبارە ووشەی نهێنی *", type="password")
                role = st.selectbox("👨‍⚕️ ڕۆڵ", ["student", "doctor"])
                
                if st.form_submit_button("📝 تۆمارکردن", use_container_width=True):
                    if new_username and email and new_password and confirm_password:
                        if new_password != confirm_password:
                            st.error("❌ ووشەی نهێنی یەک ناگرێتەوە")
                        elif len(new_password) < 6:
                            st.error("❌ ووشەی نهێنی دەبێت لە ٦ پیت کەمتر نەبێت")
                        else:
                            result = AuthSystem.register(new_username, email, new_password, role)
                            if result['success']:
                                st.success("✅ بە سەرکەوتوویی تۆمارکرایت! ئێستا دەتوانیت بچیتە ژوورەوە")
                            else:
                                st.error(f"❌ {result['message']}")
                    else:
                        st.warning("⚠️ تکایە هەموو خانەکان پڕ بکەوە")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Demo credentials
        with st.expander("🔑 زانیاری Demo"):
            st.info("""
            **بەڕێوەبەر (Admin):**
            - ناوی بەکارهێنەر: `admin`
            - ووشەی نهێنی: `Admin@2024`
            
            **خوێندکار (Student):**
            - ناوی بەکارهێنەر: `student`
            - ووشەی نهێنی: `Student@2024`
            """)

# ==================== DASHBOARD ====================
def show_dashboard():
    st.markdown(f"### {t('dashboard')}")
    
    conn = db.get_connection()
    c = conn.cursor()
    
    # Get counts
    c.execute("SELECT COUNT(*) FROM medicines")
    total_meds = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM lab_tests")
    total_tests = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM medical_notes")
    total_notes = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM diseases")
    total_diseases = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]
    
    # Most viewed medicines
    c.execute("SELECT name, view_count FROM medicines ORDER BY view_count DESC LIMIT 5")
    top_medicines = c.fetchall()
    
    # Most viewed tests
    c.execute("SELECT name, view_count FROM lab_tests ORDER BY view_count DESC LIMIT 5")
    top_tests = c.fetchall()
    
    conn.close()
    
    # Statistics cards
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <h2>💊</h2>
            <h3>{total_meds}</h3>
            <p>دەرمان</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <h2>🧪</h2>
            <h3>{total_tests}</h3>
            <p>پشکنین</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <h2>📝</h2>
            <h3>{total_notes}</h3>
            <p>تێبینی</p>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <h2>📚</h2>
            <h3>{total_diseases}</h3>
            <p>نەخۆشی</p>
        </div>
        """, unsafe_allow_html=True)
    with col5:
        st.markdown(f"""
        <div class="stat-card">
            <h2>👥</h2>
            <h3>{total_users}</h3>
            <p>بەکارهێنەر</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📊 دابەشکردنی داتاکان")
        fig = go.Figure(data=[go.Pie(
            labels=['دەرمان', 'پشکنین', 'تێبینی', 'نەخۆشی'],
            values=[total_meds, total_tests, total_notes, total_diseases],
            marker=dict(colors=['#667eea', '#764ba2', '#ffa502', '#ff4757']),
            hole=0.3
        )])
        fig.update_layout(height=350, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("🔥 زۆرترین بینراوەکان")
        
        if top_medicines:
            fig = go.Figure(data=[go.Bar(
                x=[m[0][:20] for m in top_medicines],
                y=[m[1] for m in top_medicines],
                marker_color='#667eea',
                text=[m[1] for m in top_medicines],
                textposition='auto'
            )])
            fig.update_layout(height=350, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ==================== MEDICINES PAGE ====================
def show_medicines_page():
    st.markdown("### 💊 دەرمانەکان")
    
    tab1, tab2, tab3 = st.tabs(["📋 هەموو دەرمانەکان", "➕ زیادکردن", "🔍 گەڕانی پێشکەوتوو"])
    
    with tab1:
        search = st.text_input("🔍 گەڕان", placeholder="ناو، گەنەریک، براند...")
        
        conn = db.get_connection()
        c = conn.cursor()
        
        query = "SELECT * FROM medicines WHERE 1=1"
        params = []
        
        if search:
            query += " AND (name LIKE ? OR generic_name LIKE ? OR brand_names LIKE ? OR tags LIKE ?)"
            params.extend([f'%{search}%'] * 4)
        
        query += " ORDER BY view_count DESC, name ASC"
        c.execute(query, params)
        medicines = c.fetchall()
        conn.close()
        
        if medicines:
            for med in medicines:
                with st.expander(f"{med[1]} ({med[2]})", expanded=False):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"""
                        **گەنەریک:** {med[2]}
                        **براندەکان:** {med[3]}
                        **پۆلێن:** {med[4]} | **بەش:** {med[5]}
                        **Pregnancy:** {med[6]} | **Lactation:** {med[7]}
                        **Contraindications:** {med[8]}
                        **Side Effects:** {med[9]}
                        **Adult Dose:** {med[10]}
                        **Pediatric Dose:** {med[11]}
                        **Renal Adjustment:** {med[12]}
                        **Hepatic Adjustment:** {med[13]}
                        **Drug Interactions:** {med[14]}
                        **Mechanism:** {med[15]}
                        """)
                    
                    with col2:
                        st.markdown(f"""
                        <span class="badge badge-primary">{med[17]}</span>
                        <span class="badge badge-info">👁️ {med[20]}</span>
                        """, unsafe_allow_html=True)
                        
                        if st.button("❤️ دڵخواز", key=f"fav_med_{med[0]}"):
                            st.success("✅ زیادکرا بۆ دڵخوازەکان")
        else:
            st.info(t('no_results'))
    
    with tab2:
        st.markdown("#### ➕ زیادکردنی دەرمانی نوێ")
        
        with st.form("add_medicine"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                name = st.text_input("ناوی دەرمان *")
                generic_name = st.text_input("ناوی گەنەریک")
                brand_names = st.text_input("ناوی براندەکان")
                drug_class = st.text_input("پۆلێنی دەرمان")
                category = st.selectbox("بەش", [
                    "Pain Management", "Cardiovascular", "Endocrinology",
                    "Infectious Disease", "Gastroenterology", "Neurology",
                    "Psychiatry", "Respiratory", "Other"
                ])
            
            with col2:
                pregnancy_category = st.selectbox("Pregnancy Category", 
                    ["A", "B", "C", "D", "X", "Unknown"])
                lactation_safety = st.selectbox("Lactation Safety",
                    ["Safe", "Caution", "Contraindicated", "Unknown"])
                contraindications = st.text_area("Contraindications")
                side_effects = st.text_area("Side Effects")
                adult_dose = st.text_input("Adult Dose")
            
            with col3:
                pediatric_dose = st.text_input("Pediatric Dose")
                renal_adjustment = st.text_input("Renal Dose Adjustment")
                hepatic_adjustment = st.text_input("Hepatic Dose Adjustment")
                drug_interactions = st.text_area("Drug Interactions")
                mechanism = st.text_input("Mechanism of Action")
                route = st.selectbox("Route", ["Oral", "IV", "IM", "SC", "Topical", "Inhalation"])
            
            priority = st.select_slider("Priority", ["low", "medium", "high"], value="medium")
            tags = st.text_input("Tags (comma separated)")
            notes = st.text_area("Additional Notes")
            
            if st.form_submit_button("💊 زیادکردن", use_container_width=True):
                if name:
                    conn = db.get_connection()
                    c = conn.cursor()
                    now = datetime.now().isoformat()
                    c.execute("""INSERT INTO medicines 
                                 (name, generic_name, brand_names, drug_class, category,
                                  pregnancy_category, lactation_safety, contraindications,
                                  side_effects, adult_dose, pediatric_dose, renal_dose_adjustment,
                                  hepatic_dose_adjustment, drug_interactions, mechanism_of_action,
                                  route_of_administration, priority, tags, notes, created_by, created_at, updated_at)
                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                              (name, generic_name, brand_names, drug_class, category,
                               pregnancy_category, lactation_safety, contraindications,
                               side_effects, adult_dose, pediatric_dose, renal_adjustment,
                               hepatic_adjustment, drug_interactions, mechanism,
                               route, priority, tags, notes,
                               st.session_state.user_id, now, now))
                    conn.commit()
                    conn.close()
                    
                    AuditLogger.log(st.session_state.user_id, 'CREATE', 'medicines', 
                                   c.lastrowid, f'Added medicine: {name}')
                    
                    st.success("✅ دەرمان بە سەرکەوتوویی زیادکرا!")
                    st.rerun()
                else:
                    st.error("ناوی دەرمان پێویستە!")

def show_lab_tests_page():
    st.markdown("### 🧪 پشکنینەکان")
    
    tab1, tab2 = st.tabs(["📋 هەموو پشکنینەکان", "➕ زیادکردن"])
    
    with tab1:
        search = st.text_input("🔍 گەڕان", placeholder="ناوی پشکنین...")
        
        conn = db.get_connection()
        c = conn.cursor()
        
        query = "SELECT * FROM lab_tests WHERE 1=1"
        params = []
        
        if search:
            query += " AND (name LIKE ? OR category LIKE ? OR tags LIKE ?)"
            params.extend([f'%{search}%'] * 3)
        
        query += " ORDER BY view_count DESC, name ASC"
        c.execute(query, params)
        tests = c.fetchall()
        conn.close()
        
        if tests:
            for test in tests:
                with st.expander(f"🧪 {test[1]} ({test[2]})", expanded=False):
                    st.markdown(f"""
                    **Category:** {test[2]}
                    **Purpose:** {test[3]}
                    **Normal Range (Adult):** {test[4]}
                    **Normal Range (Pediatric):** {test[5]}
                    **Male Range:** {test[6]} | **Female Range:** {test[7]}
                    **Preparation:** {test[8]}
                    **Clinical Interpretation:** {test[9]}
                    **Related Diseases:** {test[10]}
                    **Specimen:** {test[11]} | **Turnaround:** {test[12]}
                    """)
                    
                    if st.button("📌 بینینی", key=f"view_test_{test[0]}"):
                        conn = db.get_connection()
                        c = conn.cursor()
                        c.execute("UPDATE lab_tests SET view_count = view_count + 1 WHERE id=?", (test[0],))
                        conn.commit()
                        conn.close()
        else:
            st.info(t('no_results'))
    
    with tab2:
        st.markdown("#### ➕ زیادکردنی پشکنینی نوێ")
        
        with st.form("add_test"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("ناوی پشکنین *")
                category = st.selectbox("بەش", [
                    "Hematology", "Biochemistry", "Microbiology", 
                    "Immunology", "Endocrinology", "Other"
                ])
                purpose = st.text_area("Purpose")
                normal_range_adult = st.text_input("Normal Range (Adult)")
                normal_range_pediatric = st.text_input("Normal Range (Pediatric)")
            
            with col2:
                normal_range_male = st.text_input("Male Range")
                normal_range_female = st.text_input("Female Range")
                preparation = st.text_area("Preparation")
                clinical_interpretation = st.text_area("Clinical Interpretation")
                related_diseases = st.text_input("Related Diseases")
                specimen_type = st.text_input("Specimen Type")
                turnaround_time = st.text_input("Turnaround Time")
            
            tags = st.text_input("Tags")
            notes = st.text_area("Additional Notes")
            
            if st.form_submit_button("🧪 زیادکردن", use_container_width=True):
                if name:
                    conn = db.get_connection()
                    c = conn.cursor()
                    now = datetime.now().isoformat()
                    c.execute("""INSERT INTO lab_tests 
                                 (name, category, purpose, normal_range_adult, normal_range_pediatric,
                                  normal_range_male, normal_range_female, preparation,
                                  clinical_interpretation, related_diseases, specimen_type,
                                  turnaround_time, tags, notes, created_by, created_at, updated_at)
                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                              (name, category, purpose, normal_range_adult, normal_range_pediatric,
                               normal_range_male, normal_range_female, preparation,
                               clinical_interpretation, related_diseases, specimen_type,
                               turnaround_time, tags, notes, st.session_state.user_id, now, now))
                    conn.commit()
                    conn.close()
                    
                    st.success("✅ پشکنین زیادکرا!")
                    st.rerun()

def show_notes_page():
    st.markdown("### 📝 تێبینییەکان")
    
    tab1, tab2 = st.tabs(["📋 تێبینییەکان", "➕ زیادکردن"])
    
    with tab1:
        conn = db.get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM medical_notes WHERE created_by=? ORDER BY updated_at DESC", 
                 (st.session_state.user_id,))
        notes = c.fetchall()
        conn.close()
        
        if notes:
            for note in notes:
                with st.expander(f"📝 {note[1]}", expanded=False):
                    st.markdown(note[3] if note[3] else note[2])
                    st.caption(f"Tags: {note[5]} | Created: {note[9][:10]}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✏️ دەستکاری", key=f"edit_note_{note[0]}"):
                            st.info("دەستکاری لە وەشانی داهاتوودا")
                    with col2:
                        if st.button("🗑️ سڕینەوە", key=f"del_note_{note[0]}"):
                            conn = db.get_connection()
                            c = conn.cursor()
                            c.execute("DELETE FROM medical_notes WHERE id=?", (note[0],))
                            conn.commit()
                            conn.close()
                            st.rerun()
        else:
            st.info("هیچ تێبینییەکت نییە")
    
    with tab2:
        with st.form("add_note"):
            title = st.text_input("ناونیشان *")
            content = st.text_area("ناوەرۆک", height=200)
            category = st.selectbox("بەش", ["General", "Clinical", "Study", "Research", "Other"])
            tags = st.text_input("Tags")
            
            uploaded_image = st.file_uploader("وێنە", type=['png', 'jpg', 'jpeg'])
            uploaded_pdf = st.file_uploader("PDF", type=['pdf'])
            
            if st.form_submit_button("📝 زیادکردن", use_container_width=True):
                if title:
                    conn = db.get_connection()
                    c = conn.cursor()
                    now = datetime.now().isoformat()
                    
                    image_path = None
                    pdf_path = None
                    
                    if uploaded_image:
                        os.makedirs('uploads/images', exist_ok=True)
                        image_path = f"uploads/images/{uuid.uuid4()}_{uploaded_image.name}"
                        with open(image_path, 'wb') as f:
                            f.write(uploaded_image.getbuffer())
                    
                    if uploaded_pdf:
                        os.makedirs('uploads/pdfs', exist_ok=True)
                        pdf_path = f"uploads/pdfs/{uuid.uuid4()}_{uploaded_pdf.name}"
                        with open(pdf_path, 'wb') as f:
                            f.write(uploaded_pdf.getbuffer())
                    
                    c.execute("""INSERT INTO medical_notes 
                                 (title, content, category, tags, image_path, pdf_path, 
                                  created_by, created_at, updated_at)
                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                              (title, content, category, tags, image_path, pdf_path,
                               st.session_state.user_id, now, now))
                    conn.commit()
                    conn.close()
                    
                    st.success("✅ تێبینی زیادکرا!")
                    st.rerun()

def show_diseases_page():
    st.markdown("### 📚 نەخۆشییەکان")
    
    search = st.text_input("🔍 گەڕان بە ناوی نەخۆشی یان کۆدی ICD-10")
    
    conn = db.get_connection()
    c = conn.cursor()
    
    query = "SELECT * FROM diseases WHERE 1=1"
    params = []
    
    if search:
        query += " AND (name LIKE ? OR icd10_code LIKE ? OR description LIKE ? OR symptoms LIKE ?)"
        params.extend([f'%{search}%'] * 4)
    
    query += " ORDER BY name ASC"
    c.execute(query, params)
    diseases = c.fetchall()
    conn.close()
    
    if diseases:
        for disease in diseases:
            with st.expander(f"📚 {disease[1]} (ICD-10: {disease[2]})", expanded=False):
                st.markdown(f"""
                **Description:** {disease[3]}
                **Symptoms:** {disease[4]}
                **Diagnosis:** {disease[5]}
                **Treatment:** {disease[6]}
                **Prevention:** {disease[7]}
                **Category:** {disease[8]}
                """)

def show_ai_assistant():
    st.markdown("### 🤖 یارمەتیدەری زیرەکی پزیشکی")
    
    st.info("""
    🧠 **AI Medical Assistant**
    
    ئەم بەشە یارمەتیت دەدات لە:
    - گەڕانی زانیاری پزیشکی
    - وەرگێڕانی دەقە پزیشکییەکان
    - کورتکردنەوەی بابەتە پزیشکییەکان
    - ڕێنمایی خێرا بۆ دەرمان و پشکنینەکان
    
    > 💡 بۆ بەکارهێنانی AI، پێویستت بە API key ی OpenAI یان Claude هەیە.
    """)
    
    with st.form("ai_chat"):
        user_message = st.text_area("پرسیارەکەت بنووسە...", height=100)
        
        col1, col2 = st.columns(2)
        with col1:
            task = st.selectbox("جۆری کار", ["General Chat", "Medical Search", "Translation", "Summary"])
        with col2:
            target_lang = st.selectbox("زمانی ئامانج", ["English", "کوردی", "عربي"]) if task == "Translation" else None
        
        if st.form_submit_button("🤖 ناردن", use_container_width=True):
            if user_message:
                # Simulate AI response
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown("### 🤖 وەڵام")
                st.info(f"""
                **تێبینی:** ئەمە وەڵامی Demo یە. بۆ بەکارهێنانی AI ڕاستەقینە،
                پێویستت بە API key هەیە.
                
                **پرسیارەکەت:** {user_message[:100]}...
                **جۆری کار:** {task}
                """)
                st.markdown('</div>', unsafe_allow_html=True)

def show_calculators():
    st.markdown("### 📐 حسابکەری پزیشکی")
    
    calc_type = st.selectbox("جۆری حسابکەر", [
        "BMI (Body Mass Index)",
        "BSA (Body Surface Area)",
        "CrCl (Creatinine Clearance)",
        "Corrected Calcium",
        "Anion Gap",
        "Sodium Correction",
        "IV Drip Rate",
        "GFR (eGFR)",
        "Wells Score (DVT)",
        "CURB-65 (Pneumonia)",
    ])
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    if calc_type == "BMI (Body Mass Index)":
        col1, col2 = st.columns(2)
        with col1:
            weight = st.number_input("کێش (kg)", 1.0, 300.0, 70.0)
            height = st.number_input("باڵا (cm)", 50.0, 300.0, 175.0)
        
        if st.button("حسابکردن", use_container_width=True):
            bmi = weight / ((height/100) ** 2)
            if bmi < 18.5:
                status = "کێشی کەم (Underweight)"
            elif bmi < 25:
                status = "کێشی ئاسایی (Normal)"
            elif bmi < 30:
                status = "کێشی زیاد (Overweight)"
            elif bmi < 35:
                status = "قەڵەوی پلە ١ (Obese Class I)"
            elif bmi < 40:
                status = "قەڵەوی پلە ٢ (Obese Class II)"
            else:
                status = "قەڵەوی پلە ٣ (Obese Class III)"
            
            st.success(f"**BMI: {bmi:.1f}** - {status}")
    
    elif calc_type == "BSA (Body Surface Area)":
        col1, col2 = st.columns(2)
        with col1:
            weight = st.number_input("کێش (kg)", 1.0, 300.0, 70.0)
            height = st.number_input("باڵا (cm)", 50.0, 300.0, 175.0)
        
        if st.button("حسابکردن", use_container_width=True):
            bsa = ((height * weight) / 3600) ** 0.5
            st.success(f"**BSA: {bsa:.2f} m²**")
    
    elif calc_type == "CrCl (Creatinine Clearance)":
        col1, col2, col3 = st.columns(3)
        with col1:
            age = st.number_input("تەمەن (ساڵ)", 1, 120, 50)
            weight = st.number_input("کێش (kg)", 1.0, 300.0, 70.0)
        with col2:
            creatinine = st.number_input("کریاتینین (mg/dL)", 0.1, 20.0, 1.0)
            gender = st.selectbox("ڕەگەز", ["نێر (Male)", "مێ (Female)"])
        
        if st.button("حسابکردن", use_container_width=True):
            crcl = ((140 - age) * weight) / (72 * creatinine)
            if "مێ" in gender:
                crcl *= 0.85
            st.success(f"**CrCl: {crcl:.1f} mL/min**")
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_users_page():
    if st.session_state.user_role != 'admin':
        st.error("⛔ تەنها بەڕێوەبەر دەتوانێت ئەم بەشە ببینێت")
        return
    
    st.markdown("### 👥 بەڕێوەبەری بەکارهێنەران")
    
    conn = db.get_connection()
    c = conn.cursor()
    c.execute("SELECT id, username, email, role, created_at, last_login, is_active FROM users ORDER BY created_at DESC")
    users = c.fetchall()
    conn.close()
    
    # Users table
    user_data = []
    for user in users:
        user_data.append({
            "ID": user[0],
            "Username": user[1],
            "Email": user[2] or '-',
            "Role": user[3],
            "Created": user[4][:10] if user[4] else '-',
            "Last Login": user[5][:10] if user[5] else '-',
            "Active": "✅" if user[6] else "❌"
        })
    
    if user_data:
        df = pd.DataFrame(user_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Add user form
    with st.expander("➕ زیادکردنی بەکارهێنەری نوێ"):
        with st.form("add_user_admin"):
            col1, col2 = st.columns(2)
            with col1:
                username = st.text_input("ناوی بەکارهێنەر")
                email = st.text_input("ئیمەیڵ")
            with col2:
                password = st.text_input("ووشەی نهێنی", type="password")
                role = st.selectbox("ڕۆڵ", ["student", "doctor", "admin"])
            
            if st.form_submit_button("👤 زیادکردن"):
                result = AuthSystem.register(username, email, password, role)
                if result['success']:
                    st.success("✅ بەکارهێنەر زیادکرا!")
                    st.rerun()
                else:
                    st.error(result['message'])

def show_reports_page():
    if st.session_state.user_role != 'admin':
        st.error("⛔ تەنها بەڕێوەبەر")
        return
    
    st.markdown("### 📋 ڕاپۆرتەکان")
    
    conn = db.get_connection()
    c = conn.cursor()
    
    # Audit logs
    st.subheader("📝 Audit Logs (دوایین ٥٠ ڕووداو)")
    c.execute("""SELECT a.id, u.username, a.action, a.table_name, a.details, a.created_at 
                 FROM audit_logs a LEFT JOIN users u ON a.user_id = u.id 
                 ORDER BY a.created_at DESC LIMIT 50""")
    logs = c.fetchall()
    
    if logs:
        log_data = []
        for log in logs:
            log_data.append({
                "ID": log[0],
                "User": log[1] or '-',
                "Action": log[2],
                "Table": log[3],
                "Details": log[4][:50] if log[4] else '-',
                "Date": log[5][:19] if log[5] else '-'
            })
        df = pd.DataFrame(log_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    conn.close()

def show_announcements_page():
    if st.session_state.user_role != 'admin':
        st.error("⛔ تەنها بەڕێوەبەر")
        return
    
    st.markdown("### 🔔 ڕاگەیاندنەکان")
    
    with st.form("add_announcement"):
        title = st.text_input("ناونیشان")
        content = st.text_area("ناوەرۆک")
        priority = st.selectbox("پریۆرتی", ["normal", "important", "urgent"])
        
        if st.form_submit_button("🔔 ناردن"):
            conn = db.get_connection()
            c = conn.cursor()
            c.execute("""INSERT INTO announcements 
                         (title, content, priority, created_by, created_at)
                         VALUES (?, ?, ?, ?, ?)""",
                      (title, content, priority, st.session_state.user_id, datetime.now().isoformat()))
            conn.commit()
            conn.close()
            st.success("✅ ڕاگەیەندرا!")
            st.rerun()
    
    # Show announcements
    conn = db.get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM announcements ORDER BY created_at DESC LIMIT 10")
    announcements = c.fetchall()
    conn.close()
    
    for ann in announcements:
        priority_color = {'normal': 'info', 'important': 'warning', 'urgent': 'danger'}.get(ann[3], 'info')
        st.markdown(f"""
        <div class="glass-card">
            <span class="badge badge-{priority_color}">{ann[3]}</span>
            <h4>{ann[1]}</h4>
            <p>{ann[2]}</p>
            <small>{ann[5][:10] if ann[5] else ''}</small>
        </div>
        """, unsafe_allow_html=True)

def show_statistics_page():
    if st.session_state.user_role != 'admin':
        st.error("⛔ تەنها بەڕێوەبەر")
        return
    
    st.markdown("### 📊 ئامارەکان")
    
    conn = db.get_connection()
    c = conn.cursor()
    
    # User statistics
    c.execute("SELECT role, COUNT(*) FROM users GROUP BY role")
    user_roles = c.fetchall()
    
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM medicines")
    total_meds = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM lab_tests")
    total_tests = c.fetchone()[0]
    
    c.execute("SELECT SUM(view_count) FROM medicines")
    total_views = c.fetchone()[0] or 0
    
    conn.close()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👥 بەکارهێنەران", total_users)
    with col2:
        st.metric("💊 دەرمانەکان", total_meds)
    with col3:
        st.metric("🧪 پشکنینەکان", total_tests)
    with col4:
        st.metric("👁️ بینینەکان", total_views)
    
    if user_roles:
        fig = go.Figure(data=[go.Pie(
            labels=[r[0] for r in user_roles],
            values=[r[1] for r in user_roles],
            hole=0.3
        )])
        fig.update_layout(title="ڕۆڵی بەکارهێنەران", height=400)
        st.plotly_chart(fig, use_container_width=True)

def show_settings_page():
    st.markdown("### ⚙️ ڕێکخستنەکان")
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    st.subheader("🌍 زمان / Language")
    lang = st.selectbox("زمانی ڕووکار", ["English", "کوردی"], 
                        index=0 if st.session_state.get('language') == 'English' else 1)
    if lang != st.session_state.get('language'):
        st.session_state.language = lang
        st.rerun()
    
    st.subheader("🎨 ڕووکار")
    dark_mode = st.toggle("🌙 Dark Mode", value=st.session_state.get('dark_mode', True))
    if dark_mode != st.session_state.dark_mode:
        st.session_state.dark_mode = dark_mode
        st.rerun()
    
    font_size = st.select_slider("قەبارەی دەق", ["small", "medium", "large"])
    if font_size != st.session_state.get('font_size'):
        st.session_state.font_size = font_size
        st.rerun()
    
    st.subheader("💾 پشتگیری و گەڕاندنەوە")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 پشتگیری", use_container_width=True):
            shutil.copy2('medical_platform.db', f'backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
            st.success("✅ پشتگیری دروستکرا!")
    
    with col2:
        uploaded = st.file_uploader("گەڕاندنەوە", type=['db'])
        if uploaded:
            with open('medical_platform.db', 'wb') as f:
                f.write(uploaded.getbuffer())
            st.success("✅ گەڕێنرایەوە!")
            st.rerun()
    
    with col3:
        if st.button("📥 Export CSV", use_container_width=True):
            conn = db.get_connection()
            df = pd.read_sql_query("SELECT * FROM medicines", conn)
            conn.close()
            csv = df.to_csv(index=False)
            st.download_button("📥 داگرتن", csv, "medicines.csv", "text/csv")
    
    st.subheader("📱 زانیاری ئامێر")
    st.code(f"Device ID: {st.session_state.device_id}")
    st.code(f"Session Start: {st.session_state.session_start}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== RUN APPLICATION ====================
if __name__ == "__main__":
    main()
