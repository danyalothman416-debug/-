# ================================
# MEDICAL TRAINING PLATFORM v10.0
# Dr.Danyal - Production Ready
# Complete Fixed Version
# ================================

import streamlit as st
import hashlib
import json
import os
import sqlite3
import time
import uuid
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import warnings
warnings.filterwarnings('ignore')

# ================================
# PAGE CONFIGURATION
# ================================
st.set_page_config(
    page_title="Dr.Danyal Medical Platform",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================================
# CONSTANTS & CONFIGURATION
# ================================
DB_PATH = "medical_platform.db"
MAX_LOGIN_ATTEMPTS = 5
LOGIN_TIMEOUT_MINUTES = 15

# ================================
# DATABASE SETUP (SQLite - Secure)
# ================================
@st.cache_resource
def get_db_connection():
    """Create a secure database connection with proper settings"""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_database():
    """Initialize all database tables with proper schema"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            login_attempts INTEGER DEFAULT 0,
            locked_until TIMESTAMP,
            xp_points INTEGER DEFAULT 0,
            quiz_score INTEGER DEFAULT 0,
            total_cases INTEGER DEFAULT 0,
            correct_diagnoses INTEGER DEFAULT 0,
            daily_streak INTEGER DEFAULT 0,
            last_active_date DATE,
            badges TEXT DEFAULT '[]',
            achievements TEXT DEFAULT '[]'
        );
        
        CREATE TABLE IF NOT EXISTS leaderboard (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            xp_points INTEGER DEFAULT 0,
            quiz_score INTEGER DEFAULT 0,
            cases_solved INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS clinical_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            patient_info TEXT,
            note TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS login_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            success BOOLEAN DEFAULT FALSE
        );
        
        CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
        CREATE INDEX IF NOT EXISTS idx_leaderboard_xp ON leaderboard(xp_points DESC);
        CREATE INDEX IF NOT EXISTS idx_login_attempts ON login_attempts(username, attempt_time);
    """)
    
    conn.commit()

# ================================
# PASSWORD SECURITY (Enhanced)
# ================================
def generate_salt(length: int = 32) -> str:
    """Generate a cryptographically secure random salt"""
    return os.urandom(length).hex()

def hash_password_secure(password: str, salt: str = None) -> Tuple[str, str]:
    """
    Enhanced password hashing using PBKDF2
    Uses multiple iterations to slow down brute-force attacks
    """
    if salt is None:
        salt = generate_salt()
    
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        200000,
        dklen=64
    )
    
    return key.hex(), salt

def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    """Verify password against stored hash"""
    computed_hash, _ = hash_password_secure(password, salt)
    return computed_hash == stored_hash

# ================================
# RATE LIMITING SYSTEM
# ================================
def check_login_rate_limit(username: str) -> Tuple[bool, str]:
    """Check if login attempts are rate-limited"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT locked_until FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    
    if user and user['locked_until']:
        locked_until = datetime.fromisoformat(user['locked_until'])
        if locked_until > datetime.now():
            remaining = (locked_until - datetime.now()).seconds // 60
            return False, f"Account locked. Try again in {remaining} minutes."
    
    cutoff_time = datetime.now() - timedelta(minutes=LOGIN_TIMEOUT_MINUTES)
    cursor.execute("""
        SELECT COUNT(*) as attempts FROM login_attempts 
        WHERE username = ? AND attempt_time > ? AND success = FALSE
    """, (username, cutoff_time))
    
    result = cursor.fetchone()
    recent_attempts = result['attempts'] if result else 0
    
    if recent_attempts >= MAX_LOGIN_ATTEMPTS:
        cursor.execute("UPDATE users SET locked_until = ? WHERE username = ?",
                      ((datetime.now() + timedelta(minutes=LOGIN_TIMEOUT_MINUTES)).isoformat(), username))
        conn.commit()
        return False, f"Too many attempts. Account locked for {LOGIN_TIMEOUT_MINUTES} minutes."
    
    return True, ""

def record_login_attempt(username: str, success: bool):
    """Record login attempt for rate limiting"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO login_attempts (username, success) VALUES (?, ?)", (username, success))
    
    if success:
        cursor.execute("UPDATE users SET login_attempts = 0, locked_until = NULL WHERE username = ?", (username,))
    else:
        cursor.execute("UPDATE users SET login_attempts = login_attempts + 1 WHERE username = ?", (username,))
    
    conn.commit()

# ================================
# CACHED DATA FUNCTIONS
# ================================
@st.cache_data(ttl=300)
def get_leaderboard_data():
    """Cached leaderboard data"""
    import pandas as pd
    conn = get_db_connection()
    df = pd.read_sql_query("""
        SELECT username, xp_points, quiz_score, cases_solved, level, last_active
        FROM leaderboard ORDER BY xp_points DESC
    """, conn)
    return df

@st.cache_data(ttl=60)
def get_user_count() -> int:
    """Cached user count"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM users")
    result = cursor.fetchone()
    return result['count'] if result else 0

# ================================
# USER MANAGEMENT
# ================================
def create_user(username: str, password: str) -> Tuple[bool, str]:
    """Create a new user with secure password storage"""
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        return False, "Username already exists"
    
    password_hash, salt = hash_password_secure(password)
    
    cursor.execute("INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
                  (username, password_hash, salt))
    cursor.execute("INSERT INTO leaderboard (username, xp_points) VALUES (?, 0)", (username,))
    
    conn.commit()
    return True, "Account created successfully"

def authenticate_user(username: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
    """Authenticate user with rate limiting"""
    can_attempt, message = check_login_rate_limit(username)
    if not can_attempt:
        return False, message, None
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    
    if not user:
        record_login_attempt(username, False)
        return False, "Invalid username or password", None
    
    if verify_password(password, user['password_hash'], user['salt']):
        record_login_attempt(username, True)
        cursor.execute("UPDATE users SET last_login = ? WHERE id = ?",
                      (datetime.now().isoformat(), user['id']))
        conn.commit()
        return True, "Login successful", dict(user)
    else:
        record_login_attempt(username, False)
        return False, "Invalid username or password", None

def update_user_streak(username: str) -> int:
    """Update and return the user's daily streak"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT daily_streak, last_active_date FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    
    if not user:
        return 0
    
    today = datetime.now().date()
    last_active = datetime.fromisoformat(user['last_active_date']).date() if user['last_active_date'] else None
    
    if last_active:
        yesterday = today - timedelta(days=1)
        if last_active == yesterday:
            new_streak = user['daily_streak'] + 1
        elif last_active == today:
            new_streak = user['daily_streak']
        else:
            new_streak = 1
    else:
        new_streak = 1
    
    cursor.execute("UPDATE users SET daily_streak = ?, last_active_date = ? WHERE username = ?",
                  (new_streak, today.isoformat(), username))
    conn.commit()
    return new_streak

def add_xp(username: str, points: int):
    """Add XP points to user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("UPDATE users SET xp_points = xp_points + ? WHERE username = ?", (points, username))
    cursor.execute("UPDATE leaderboard SET xp_points = xp_points + ?, last_active = ? WHERE username = ?",
                  (points, datetime.now().isoformat(), username))
    conn.commit()

# ================================
# LEVEL SYSTEM
# ================================
LEVELS = {
    1: {"name": "Medical Student", "icon": "🌱", "min_xp": 0, "max_xp": 99},
    2: {"name": "Intern", "icon": "📖", "min_xp": 100, "max_xp": 299},
    3: {"name": "Resident", "icon": "🚀", "min_xp": 300, "max_xp": 599},
    4: {"name": "Specialist", "icon": "🏆", "min_xp": 600, "max_xp": 999},
    5: {"name": "Consultant", "icon": "👨‍⚕️", "min_xp": 1000, "max_xp": 1999},
    6: {"name": "Professor", "icon": "🎓", "min_xp": 2000, "max_xp": 4999},
    7: {"name": "Legend", "icon": "👑", "min_xp": 5000, "max_xp": float('inf')}
}

def get_user_level(xp_points: int) -> int:
    """Determine user level based on XP points"""
    for level in range(7, 0, -1):
        if xp_points >= LEVELS[level]["min_xp"]:
            return level
    return 1

def get_level_progress(xp_points: int) -> float:
    """Calculate progress to next level"""
    current_level = get_user_level(xp_points)
    if current_level >= 7:
        return 100.0
    
    current_min = LEVELS[current_level]["min_xp"]
    next_min = LEVELS[current_level + 1]["min_xp"]
    
    progress = ((xp_points - current_min) / (next_min - current_min)) * 100
    return min(progress, 100)

# ================================
# DATA DATABASES
# ================================
DISEASE_DATABASE = {
    "Diabetes Mellitus Type 1": {
        "symptoms": ["Polyuria", "Polydipsia", "Weight loss", "Fatigue", "Blurred vision", "Ketoacidosis"],
        "tests": {"Fasting Glucose": ">126 mg/dL", "HbA1c": ">6.5%", "C-peptide": "Low", "Anti-GAD": "Positive"},
        "treatment": ["Insulin therapy", "Carbohydrate counting", "Regular exercise", "Blood glucose monitoring"],
        "risk_level": "High",
        "age_group": "Children & Young Adults",
        "category": "Endocrine"
    },
    "Diabetes Mellitus Type 2": {
        "symptoms": ["Polyuria", "Polydipsia", "Fatigue", "Slow wound healing", "Recurrent infections", "Blurred vision"],
        "tests": {"Fasting Glucose": ">126 mg/dL", "HbA1c": ">6.5%", "OGTT": ">200 mg/dL"},
        "treatment": ["Metformin", "Lifestyle modification", "SGLT2 inhibitors", "GLP-1 agonists", "Regular exercise"],
        "risk_level": "Moderate",
        "age_group": "Adults >40 years",
        "category": "Endocrine"
    },
    "Essential Hypertension": {
        "symptoms": ["Often asymptomatic", "Headache", "Dizziness", "Blurred vision", "Epistaxis"],
        "tests": {"Blood Pressure": ">140/90 mmHg", "ECG": "Possible LVH", "Creatinine": "Normal"},
        "treatment": ["ACE inhibitors", "Lifestyle changes", "Low sodium diet", "Regular exercise"],
        "risk_level": "Low",
        "age_group": "All ages",
        "category": "Cardiovascular"
    },
    "Acute Myocardial Infarction": {
        "symptoms": ["Severe chest pain", "Diaphoresis", "Dyspnea", "Nausea", "Left arm radiation", "Anxiety"],
        "tests": {"ECG": "ST elevation", "Troponin I": ">0.04 ng/mL", "CK-MB": "Elevated"},
        "treatment": ["Aspirin 300mg", "Nitroglycerin", "Morphine", "Oxygen", "Primary PCI"],
        "risk_level": "Critical",
        "age_group": ">45 years",
        "category": "Cardiovascular"
    },
    "Community-Acquired Pneumonia": {
        "symptoms": ["Fever", "Productive cough", "Dyspnea", "Pleuritic chest pain", "Malaise", "Chills"],
        "tests": {"Chest X-ray": "Consolidation", "WBC": ">11,000", "CRP": "Elevated"},
        "treatment": ["Amoxicillin-clavulanate", "Azithromycin", "Oxygen if needed", "Hydration"],
        "risk_level": "Moderate",
        "age_group": "All ages",
        "category": "Respiratory"
    },
    "Bronchial Asthma": {
        "symptoms": ["Wheezing", "Dyspnea", "Chest tightness", "Cough (especially at night)", "Shortness of breath"],
        "tests": {"Pulmonary Function": "FEV1 <80%", "Peak Flow": "Reduced", "Chest X-ray": "Hyperinflation"},
        "treatment": ["SABA (Albuterol)", "ICS (Budesonide)", "LABA", "Avoid triggers"],
        "risk_level": "Low",
        "age_group": "Children & Adults",
        "category": "Respiratory"
    },
    "Iron Deficiency Anemia": {
        "symptoms": ["Fatigue", "Pallor", "Dyspnea on exertion", "Palpitations", "Brittle nails", "Pica"],
        "tests": {"Hemoglobin": "<12 g/dL", "MCV": "<80 fL", "Ferritin": "<15 ng/mL"},
        "treatment": ["Ferrous sulfate 325mg", "Vitamin C supplementation", "Iron-rich diet"],
        "risk_level": "Low",
        "age_group": "All ages",
        "category": "Hematology"
    },
    "Chronic Kidney Disease": {
        "symptoms": ["Edema", "Fatigue", "Decreased urine output", "Nausea", "Pruritus"],
        "tests": {"Creatinine": ">1.3 mg/dL", "eGFR": "<60", "BUN": ">20", "Urinalysis": "Proteinuria"},
        "treatment": ["ACE inhibitors", "Dietary restriction", "Phosphate binders", "Dialysis if ESRD"],
        "risk_level": "High",
        "age_group": ">50 years",
        "category": "Nephrology"
    },
    "Hepatitis B": {
        "symptoms": ["Jaundice", "Fatigue", "Dark urine", "Right upper quadrant pain", "Nausea", "Anorexia"],
        "tests": {"HBsAg": "Positive", "Anti-HBc": "Positive", "ALT": ">1000", "AST": "Elevated"},
        "treatment": ["Entecavir", "Tenofovir", "Pegylated interferon", "Avoid alcohol"],
        "risk_level": "High",
        "age_group": "All ages",
        "category": "Gastroenterology"
    },
    "Pulmonary Tuberculosis": {
        "symptoms": ["Chronic cough (>3 weeks)", "Hemoptysis", "Night sweats", "Weight loss", "Fever", "Anorexia"],
        "tests": {"Chest X-ray": "Cavitary lesions", "Sputum AFB": "Positive", "GeneXpert": "MTB detected"},
        "treatment": ["Rifampicin", "Isoniazid", "Pyrazinamide", "Ethambutol", "DOT"],
        "risk_level": "Critical",
        "age_group": "All ages",
        "category": "Infectious Disease"
    }
}

LAB_TESTS = {
    "Hemoglobin": {"category": "Hematology", "normal": "12-16 g/dL", "description": "Oxygen-carrying capacity"},
    "WBC Count": {"category": "Hematology", "normal": "4,000-11,000/µL", "description": "Infection/inflammation marker"},
    "RBC Count": {"category": "Hematology", "normal": "4.5-5.5 million/µL", "description": "Oxygen transport"},
    "Hematocrit": {"category": "Hematology", "normal": "37-47%", "description": "RBC volume percentage"},
    "MCV": {"category": "Hematology", "normal": "80-100 fL", "description": "RBC size"},
    "MCH": {"category": "Hematology", "normal": "27-33 pg", "description": "Hemoglobin per RBC"},
    "MCHC": {"category": "Hematology", "normal": "32-36 g/dL", "description": "Hemoglobin concentration"},
    "RDW": {"category": "Hematology", "normal": "11.5-14.5%", "description": "RBC size variation"},
    "Platelet Count": {"category": "Hematology", "normal": "150,000-450,000/µL", "description": "Clotting ability"},
    "ESR": {"category": "Hematology", "normal": "0-20 mm/hr", "description": "Inflammation marker"},
    "Ferritin": {"category": "Hematology", "normal": "15-300 ng/mL", "description": "Iron stores"},
    "Serum Iron": {"category": "Hematology", "normal": "60-170 µg/dL", "description": "Circulating iron"},
    "TIBC": {"category": "Hematology", "normal": "250-450 µg/dL", "description": "Iron binding capacity"},
    "Vitamin B12": {"category": "Hematology", "normal": "200-900 pg/mL", "description": "B12 deficiency marker"},
    "Folate": {"category": "Hematology", "normal": "3-17 ng/mL", "description": "Folate deficiency marker"},
    "PT": {"category": "Hematology", "normal": "11-13.5 sec", "description": "Extrinsic pathway"},
    "PTT": {"category": "Hematology", "normal": "25-35 sec", "description": "Intrinsic pathway"},
    "INR": {"category": "Hematology", "normal": "0.9-1.1", "description": "Coagulation status"},
    "Fibrinogen": {"category": "Hematology", "normal": "200-400 mg/dL", "description": "Clotting factor"},
    "D-Dimer": {"category": "Hematology", "normal": "<0.5 mg/L", "description": "Thrombosis marker"},
    "Fasting Glucose": {"category": "Biochemistry", "normal": "70-100 mg/dL", "description": "Diabetes screening"},
    "HbA1c": {"category": "Biochemistry", "normal": "4.0-5.6%", "description": "3-month glucose average"},
    "Creatinine": {"category": "Biochemistry", "normal": "0.6-1.3 mg/dL", "description": "Kidney function"},
    "BUN": {"category": "Biochemistry", "normal": "7-20 mg/dL", "description": "Kidney function"},
    "eGFR": {"category": "Biochemistry", "normal": ">90 mL/min", "description": "Kidney filtration rate"},
    "Uric Acid": {"category": "Biochemistry", "normal": "3.5-7.2 mg/dL", "description": "Gout marker"},
    "Total Protein": {"category": "Biochemistry", "normal": "6.0-8.0 g/dL", "description": "Nutritional status"},
    "Albumin": {"category": "Biochemistry", "normal": "3.5-5.0 g/dL", "description": "Liver function"},
    "Total Bilirubin": {"category": "Biochemistry", "normal": "0.1-1.2 mg/dL", "description": "Jaundice marker"},
    "ALT": {"category": "Biochemistry", "normal": "10-40 U/L", "description": "Liver enzyme"},
    "AST": {"category": "Biochemistry", "normal": "10-40 U/L", "description": "Liver/muscle enzyme"},
    "ALP": {"category": "Biochemistry", "normal": "44-147 U/L", "description": "Bone/liver enzyme"},
    "GGT": {"category": "Biochemistry", "normal": "0-51 U/L", "description": "Liver/biliary enzyme"},
    "Amylase": {"category": "Biochemistry", "normal": "20-200 U/L", "description": "Pancreatic enzyme"},
    "Lipase": {"category": "Biochemistry", "normal": "20-200 U/L", "description": "Pancreatic enzyme"},
    "CK": {"category": "Biochemistry", "normal": "22-198 U/L", "description": "Muscle enzyme"},
    "Sodium": {"category": "Biochemistry", "normal": "135-145 mmol/L", "description": "Electrolyte"},
    "Potassium": {"category": "Biochemistry", "normal": "3.5-5.0 mmol/L", "description": "Electrolyte"},
    "Chloride": {"category": "Biochemistry", "normal": "96-106 mmol/L", "description": "Electrolyte"},
    "Calcium": {"category": "Biochemistry", "normal": "8.5-10.5 mg/dL", "description": "Bone metabolism"},
    "Magnesium": {"category": "Biochemistry", "normal": "1.7-2.2 mg/dL", "description": "Neuromuscular function"},
    "Phosphorus": {"category": "Biochemistry", "normal": "2.5-4.5 mg/dL", "description": "Bone metabolism"},
    "Total Cholesterol": {"category": "Lipids", "normal": "<200 mg/dL", "description": "Lipid profile"},
    "LDL Cholesterol": {"category": "Lipids", "normal": "<100 mg/dL", "description": "Bad cholesterol"},
    "HDL Cholesterol": {"category": "Lipids", "normal": ">40 mg/dL", "description": "Good cholesterol"},
    "Triglycerides": {"category": "Lipids", "normal": "<150 mg/dL", "description": "Blood fats"},
    "Troponin I": {"category": "Cardiac", "normal": "<0.04 ng/mL", "description": "Myocardial injury"},
    "Troponin T": {"category": "Cardiac", "normal": "<0.014 ng/mL", "description": "High-sensitivity cardiac"},
    "BNP": {"category": "Cardiac", "normal": "<100 pg/mL", "description": "Heart failure"},
    "CK-MB": {"category": "Cardiac", "normal": "0-5 ng/mL", "description": "Cardiac enzyme"},
    "TSH": {"category": "Endocrine", "normal": "0.4-4.0 mIU/L", "description": "Thyroid function"},
    "Free T4": {"category": "Endocrine", "normal": "0.8-1.8 ng/dL", "description": "Thyroid hormone"},
    "Free T3": {"category": "Endocrine", "normal": "2.3-4.2 pg/mL", "description": "Active thyroid hormone"},
    "Cortisol (AM)": {"category": "Endocrine", "normal": "6-23 µg/dL", "description": "Adrenal function"},
    "Testosterone (Male)": {"category": "Endocrine", "normal": "300-1000 ng/dL", "description": "Androgen"},
    "Vitamin D (25-OH)": {"category": "Endocrine", "normal": "30-100 ng/mL", "description": "Vitamin D status"},
    "CRP": {"category": "Immunology", "normal": "<5 mg/L", "description": "Acute inflammation"},
    "Rheumatoid Factor": {"category": "Immunology", "normal": "<14 IU/mL", "description": "RA marker"},
    "ANA": {"category": "Immunology", "normal": "Negative", "description": "Autoimmune screening"},
    "Urine pH": {"category": "Urinalysis", "normal": "4.5-8.0", "description": "Acid-base balance"},
    "Urine Protein": {"category": "Urinalysis", "normal": "Negative", "description": "Kidney damage"},
    "Urine Glucose": {"category": "Urinalysis", "normal": "Negative", "description": "Diabetes"},
    "Urine WBC": {"category": "Urinalysis", "normal": "0-5/HPF", "description": "Infection"},
    "Urine RBC": {"category": "Urinalysis", "normal": "0-3/HPF", "description": "Bleeding"},
}

DRUG_DATABASE = {
    "Cardiovascular": {
        "Lisinopril": {"class": "ACE Inhibitor", "dose": "10-40mg daily", "indications": "Hypertension, HF", "side_effects": "Cough, angioedema"},
        "Losartan": {"class": "ARB", "dose": "50-100mg daily", "indications": "Hypertension, HF", "side_effects": "Dizziness, hyperkalemia"},
        "Amlodipine": {"class": "CCB", "dose": "5-10mg daily", "indications": "Hypertension, angina", "side_effects": "Edema, flushing"},
        "Metoprolol": {"class": "Beta Blocker", "dose": "25-200mg daily", "indications": "Hypertension, angina", "side_effects": "Bradycardia, fatigue"},
        "Hydrochlorothiazide": {"class": "Thiazide Diuretic", "dose": "12.5-50mg daily", "indications": "Hypertension, edema", "side_effects": "Hypokalemia"},
        "Furosemide": {"class": "Loop Diuretic", "dose": "20-80mg daily", "indications": "Edema, HF", "side_effects": "Hypokalemia, dehydration"},
        "Atorvastatin": {"class": "Statin", "dose": "10-80mg daily", "indications": "Hyperlipidemia", "side_effects": "Myalgia, elevated LFTs"},
        "Clopidogrel": {"class": "Antiplatelet", "dose": "75mg daily", "indications": "ACS, stroke prevention", "side_effects": "Bleeding"},
        "Aspirin": {"class": "Antiplatelet", "dose": "75-325mg daily", "indications": "CVD prevention", "side_effects": "GI bleeding"},
        "Warfarin": {"class": "Anticoagulant", "dose": "2-10mg daily", "indications": "DVT, PE, AF", "side_effects": "Bleeding"},
        "Rivaroxaban": {"class": "DOAC", "dose": "10-20mg daily", "indications": "DVT, PE, AF", "side_effects": "Bleeding"},
        "Apixaban": {"class": "DOAC", "dose": "2.5-5mg BID", "indications": "AF, DVT prevention", "side_effects": "Bleeding"},
        "Digoxin": {"class": "Cardiac Glycoside", "dose": "0.125-0.25mg daily", "indications": "HF, AF", "side_effects": "Nausea, visual changes"},
        "Amiodarone": {"class": "Antiarrhythmic", "dose": "200-400mg daily", "indications": "Arrhythmias", "side_effects": "Pulmonary fibrosis"},
        "Nitroglycerin": {"class": "Nitrate", "dose": "0.3-0.6mg SL PRN", "indications": "Acute angina", "side_effects": "Headache, hypotension"}
    },
    "Endocrinology": {
        "Metformin": {"class": "Biguanide", "dose": "500-2000mg daily", "indications": "Type 2 DM", "side_effects": "GI upset, lactic acidosis"},
        "Glipizide": {"class": "Sulfonylurea", "dose": "5-20mg daily", "indications": "Type 2 DM", "side_effects": "Hypoglycemia, weight gain"},
        "Sitagliptin": {"class": "DPP-4 Inhibitor", "dose": "100mg daily", "indications": "Type 2 DM", "side_effects": "Headache, pancreatitis"},
        "Empagliflozin": {"class": "SGLT2 Inhibitor", "dose": "10-25mg daily", "indications": "Type 2 DM, HF", "side_effects": "UTI, DKA"},
        "Insulin Glargine": {"class": "Long-acting Insulin", "dose": "Individualized", "indications": "Type 1 & 2 DM", "side_effects": "Hypoglycemia"},
        "Levothyroxine": {"class": "Thyroid Hormone", "dose": "25-200mcg daily", "indications": "Hypothyroidism", "side_effects": "Palpitations"},
        "Methimazole": {"class": "Antithyroid", "dose": "5-30mg daily", "indications": "Hyperthyroidism", "side_effects": "Agranulocytosis"},
        "Prednisone": {"class": "Corticosteroid", "dose": "5-60mg daily", "indications": "Inflammation", "side_effects": "Weight gain, osteoporosis"}
    },
    "Antibiotics": {
        "Amoxicillin": {"class": "Penicillin", "dose": "500-875mg BID", "indications": "Respiratory, UTI", "side_effects": "Diarrhea, rash"},
        "Ceftriaxone": {"class": "3rd Gen Cephalosporin", "dose": "1-2g IV daily", "indications": "Serious infections", "side_effects": "Diarrhea"},
        "Azithromycin": {"class": "Macrolide", "dose": "250-500mg daily", "indications": "Respiratory infections", "side_effects": "GI upset"},
        "Doxycycline": {"class": "Tetracycline", "dose": "100mg BID", "indications": "Acne, Lyme", "side_effects": "Photosensitivity"},
        "Ciprofloxacin": {"class": "Fluoroquinolone", "dose": "250-750mg BID", "indications": "UTI, GI", "side_effects": "Tendonitis"},
        "Metronidazole": {"class": "Nitroimidazole", "dose": "500mg TID", "indications": "Anaerobic infections", "side_effects": "Metallic taste"},
        "Vancomycin": {"class": "Glycopeptide", "dose": "IV trough-guided", "indications": "MRSA", "side_effects": "Red man syndrome"},
        "TMP-SMX": {"class": "Sulfonamide", "dose": "160/800mg BID", "indications": "UTI, PCP", "side_effects": "Rash, hyperkalemia"}
    },
    "Neurology/Psychiatry": {
        "Sertraline": {"class": "SSRI", "dose": "50-200mg daily", "indications": "Depression, anxiety", "side_effects": "Sexual dysfunction"},
        "Fluoxetine": {"class": "SSRI", "dose": "20-80mg daily", "indications": "Depression, OCD", "side_effects": "Insomnia, weight loss"},
        "Venlafaxine": {"class": "SNRI", "dose": "75-375mg daily", "indications": "Depression, anxiety", "side_effects": "Hypertension"},
        "Quetiapine": {"class": "Atypical Antipsychotic", "dose": "25-800mg daily", "indications": "Schizophrenia, bipolar", "side_effects": "Weight gain"},
        "Lithium": {"class": "Mood Stabilizer", "dose": "300-1800mg daily", "indications": "Bipolar disorder", "side_effects": "Tremor, nephrotoxicity"},
        "Gabapentin": {"class": "Gabapentinoid", "dose": "300-3600mg daily", "indications": "Neuropathic pain", "side_effects": "Sedation, dizziness"},
        "Pregabalin": {"class": "Gabapentinoid", "dose": "75-600mg daily", "indications": "Neuropathic pain", "side_effects": "Dizziness, edema"},
        "Levetiracetam": {"class": "AED", "dose": "500-3000mg daily", "indications": "Epilepsy", "side_effects": "Behavioral changes"},
        "Donepezil": {"class": "Cholinesterase Inhibitor", "dose": "5-10mg daily", "indications": "Alzheimer's", "side_effects": "Bradycardia"},
        "Sumatriptan": {"class": "Triptan", "dose": "50-100mg PRN", "indications": "Acute migraine", "side_effects": "Chest tightness"}
    },
    "Gastroenterology": {
        "Omeprazole": {"class": "PPI", "dose": "20-40mg daily", "indications": "GERD, PUD", "side_effects": "B12 deficiency"},
        "Famotidine": {"class": "H2 Antagonist", "dose": "20-40mg BID", "indications": "GERD", "side_effects": "Constipation"},
        "Ondansetron": {"class": "5-HT3 Antagonist", "dose": "4-8mg PRN", "indications": "Nausea/vomiting", "side_effects": "Headache"},
        "Loperamide": {"class": "Opioid Agonist", "dose": "2-4mg PRN", "indications": "Diarrhea", "side_effects": "Constipation"},
        "Lactulose": {"class": "Osmotic Laxative", "dose": "15-30mL daily", "indications": "Constipation", "side_effects": "Bloating"}
    },
    "Respiratory": {
        "Albuterol": {"class": "SABA", "dose": "2 puffs Q4-6H PRN", "indications": "Asthma", "side_effects": "Tremor, tachycardia"},
        "Fluticasone": {"class": "ICS", "dose": "100-500mcg BID", "indications": "Asthma maintenance", "side_effects": "Oral thrush"},
        "Montelukast": {"class": "Leukotriene Antagonist", "dose": "10mg daily", "indications": "Asthma, allergies", "side_effects": "Headache"},
        "Tiotropium": {"class": "LAMA", "dose": "18mcg daily", "indications": "COPD", "side_effects": "Dry mouth"}
    },
    "Analgesics": {
        "Ibuprofen": {"class": "NSAID", "dose": "200-800mg TID", "indications": "Pain, inflammation", "side_effects": "GI ulcer"},
        "Naproxen": {"class": "NSAID", "dose": "250-500mg BID", "indications": "Pain, inflammation", "side_effects": "GI upset"},
        "Acetaminophen": {"class": "Analgesic", "dose": "500-1000mg Q6H", "indications": "Pain, fever", "side_effects": "Hepatotoxicity"},
        "Tramadol": {"class": "Weak Opioid", "dose": "50-100mg Q6H", "indications": "Moderate pain", "side_effects": "Nausea, seizures"},
        "Morphine": {"class": "Opioid Agonist", "dose": "5-30mg Q4H", "indications": "Severe pain", "side_effects": "Respiratory depression"},
        "Oxycodone": {"class": "Opioid Agonist", "dose": "5-30mg Q4-6H", "indications": "Severe pain", "side_effects": "Respiratory depression"}
    }
}

# ================================
# CSS STYLING (Optimized)
# ================================
def load_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        * { font-family: 'Inter', sans-serif; }
        
        .stApp {
            background: linear-gradient(135deg, #0a0a1a, #1a1a3e, #0a0a1a);
        }
        
        .glass-card {
            background: rgba(255,255,255,0.03);
            backdrop-filter: blur(20px);
            border-radius: 16px;
            padding: 1.5rem;
            border: 1px solid rgba(99,102,241,0.2);
            margin: 1rem 0;
            transition: all 0.3s ease;
        }
        
        .glass-card:hover {
            border-color: rgba(139,92,246,0.4);
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(99,102,241,0.1);
        }
        
        .stat-card {
            background: linear-gradient(135deg, rgba(99,102,241,0.1), rgba(139,92,246,0.05));
            border-radius: 16px;
            padding: 1.2rem;
            text-align: center;
            border: 1px solid rgba(99,102,241,0.2);
        }
        
        .stat-number {
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #6366f1, #a78bfa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .badge {
            display: inline-block;
            padding: 0.3rem 1rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        
        .badge-primary { background: rgba(99,102,241,0.2); color: #a78bfa; }
        .badge-success { background: rgba(16,185,129,0.2); color: #10b981; }
        .badge-danger { background: rgba(239,68,68,0.2); color: #ef4444; }
        .badge-warning { background: rgba(251,191,36,0.2); color: #fbbf24; }
        
        .stButton > button {
            background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }
        
        .stButton > button:hover {
            background: linear-gradient(135deg, #8b5cf6, #a78bfa) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px rgba(99,102,241,0.3) !important;
        }
        
        .stTextInput > div > div, .stTextArea > div > div {
            background: rgba(255,255,255,0.05) !important;
            border: 1px solid rgba(99,102,241,0.2) !important;
            border-radius: 10px !important;
            color: white !important;
        }
        
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0a0a1a, #1a1a3e, #0a0a1a) !important;
            border-right: 2px solid rgba(99,102,241,0.2) !important;
        }
        
        [data-testid="stSidebar"] .stButton > button {
            background: rgba(99,102,241,0.1) !important;
            border: 1px solid rgba(99,102,241,0.2) !important;
            color: white !important;
            text-align: left !important;
            padding: 0.5rem 1rem !important;
            margin: 2px 0 !important;
        }
        
        [data-testid="stSidebar"] .stButton > button:hover {
            background: rgba(99,102,241,0.2) !important;
            border-color: rgba(139,92,246,0.4) !important;
            transform: translateX(5px) !important;
        }
        
        h1 {
            background: linear-gradient(135deg, #6366f1, #8b5cf6, #a78bfa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800 !important;
        }
        
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: rgba(255,255,255,0.05); }
        ::-webkit-scrollbar-thumb { background: linear-gradient(180deg, #6366f1, #8b5cf6); border-radius: 10px; }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
        }
    </style>
    """, unsafe_allow_html=True)

load_css()

# ================================
# SESSION STATE INITIALIZATION (ALL VARIABLES DEFINED)
# ================================
def init_session_state():
    """Initialize all session state variables with defaults"""
    defaults = {
        'logged_in': False,
        'username': "",
        'user_data': None,
        'xp_points': 0,
        'quiz_score': 0,
        'total_cases': 0,
        'correct_diagnoses': 0,
        'streak': 0,  # THIS WAS MISSING
        'current_page': "Dashboard",
        'flashcard_flipped': False,
        'comprehensive_exam': None,
        'comprehensive_answers': {},
        'comprehensive_submitted': False,
        'comprehensive_score': 0,
        'current_room_id': None,
        'editing_drug': None,
        'editing_lab': None,
        'current_case': None,
        'achievements': [],
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# ================================
# INITIALIZE DATABASE
# ================================
init_database()

# ================================
# LOGIN PAGE
# ================================
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 3rem 0;">
            <div style="font-size: 5rem; animation: float 3s ease-in-out infinite;">🩺</div>
            <h1 style="font-size: 3rem;">Dr.Danyal</h1>
            <p style="color: rgba(255,255,255,0.6); font-size: 1.1rem;">Advanced Medical Training Platform</p>
        </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])
        
        with tab1:
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter username")
                password = st.text_input("Password", type="password", placeholder="Enter password")
                
                if st.form_submit_button("🚀 Login", type="primary", use_container_width=True):
                    success, message, user_data = authenticate_user(username, password)
                    
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.user_data = user_data
                        st.session_state.xp_points = user_data['xp_points']
                        st.session_state.quiz_score = user_data['quiz_score']
                        st.session_state.total_cases = user_data['total_cases']
                        st.session_state.correct_diagnoses = user_data['correct_diagnoses']
                        st.session_state.streak = update_user_streak(username)
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
        
        with tab2:
            with st.form("register_form"):
                new_username = st.text_input("Choose Username", placeholder="Min 3 characters")
                new_password = st.text_input("Choose Password", type="password", placeholder="Min 6 characters")
                confirm_password = st.text_input("Confirm Password", type="password")
                
                if st.form_submit_button("✨ Create Account", type="primary", use_container_width=True):
                    if new_password != confirm_password:
                        st.error("❌ Passwords don't match")
                    else:
                        success, message = create_user(new_username, new_password)
                        if success:
                            st.success(f"✅ {message} Please login.")
                        else:
                            st.error(f"❌ {message}")
    
    st.stop()

# ================================
# SIDEBAR
# ================================
with st.sidebar:
    level = get_user_level(st.session_state.xp_points)
    level_info = LEVELS[level]
    progress = get_level_progress(st.session_state.xp_points)
    
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem 0;">
        <div style="font-size: 3rem;">{level_info['icon']}</div>
        <div style="font-weight: 700; color: #a78bfa;">{st.session_state.username}</div>
        <span class="badge badge-primary">{level_info['name']}</span>
    </div>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin: 1rem 0;">
        <div style="background: rgba(99,102,241,0.1); padding: 0.5rem; border-radius: 10px; text-align: center;">
            <div style="font-weight: 700; color: #a78bfa;">⭐ {st.session_state.xp_points}</div>
            <div style="font-size: 0.65rem; color: #888;">XP</div>
        </div>
        <div style="background: rgba(99,102,241,0.1); padding: 0.5rem; border-radius: 10px; text-align: center;">
            <div style="font-weight: 700; color: #a78bfa;">📊 {st.session_state.quiz_score}</div>
            <div style="font-size: 0.65rem; color: #888;">Quiz</div>
        </div>
        <div style="background: rgba(99,102,241,0.1); padding: 0.5rem; border-radius: 10px; text-align: center;">
            <div style="font-weight: 700; color: #a78bfa;">🔥 {st.session_state.streak}</div>
            <div style="font-size: 0.65rem; color: #888;">Streak</div>
        </div>
        <div style="background: rgba(99,102,241,0.1); padding: 0.5rem; border-radius: 10px; text-align: center;">
            <div style="font-weight: 700; color: #a78bfa;">🩺 {st.session_state.total_cases}</div>
            <div style="font-size: 0.65rem; color: #888;">Cases</div>
        </div>
    </div>
    
    <div style="width: 100%; height: 6px; background: rgba(255,255,255,0.1); border-radius: 10px; overflow: hidden; margin: 0.5rem 0;">
        <div style="width: {progress:.1f}%; height: 100%; background: linear-gradient(90deg, #6366f1, #8b5cf6); border-radius: 10px;"></div>
    </div>
    <div style="font-size: 0.65rem; color: #888; text-align: right;">Level {progress:.0f}%</div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation buttons
    pages = [
        ("📊 Dashboard", "Dashboard"),
        ("📚 Diseases", "Diseases"),
        ("🩺 Case Analysis", "Case Analysis"),
        ("📝 Quiz", "Quiz"),
        ("📋 Comprehensive Exam", "Comprehensive Exam"),
        ("🔄 Spaced Repetition", "Spaced Repetition"),
        ("🔬 Lab Tests", "Lab Tests"),
        ("💊 Pharmacology", "Pharmacology"),
        ("⚠️ Drug Interactions", "Drug Interactions"),
        ("🏆 Leaderboard", "Leaderboard"),
        ("📰 Medical News", "Medical News"),
        ("🧠 AI Assistant", "AI Assistant"),
        ("📝 Clinical Notes", "Clinical Notes"),
        ("🏆 Achievements", "Achievements"),
    ]
    
    for label, page_name in pages:
        if st.button(label, use_container_width=True, key=f"nav_{page_name}"):
            st.session_state.current_page = page_name
            st.rerun()
    
    st.markdown("---")
    
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()
    
    st.markdown("""
    <div style="text-align: center; padding: 0.5rem; font-size: 0.7rem; color: #666;">
        <span class="badge badge-primary">v10.0</span>
        <p>© 2024 Dr.Danyal</p>
    </div>
    """, unsafe_allow_html=True)

# ================================
# PAGE ROUTING
# ================================
page = st.session_state.current_page

if page == "Dashboard":
    st.markdown('<h1 style="text-align: center;">📊 Medical Training Dashboard</h1>', unsafe_allow_html=True)
    
    cols = st.columns(5)
    metrics = [
        ("📚 Diseases", len(DISEASE_DATABASE)),
        ("💊 Drugs", sum(len(d) for d in DRUG_DATABASE.values())),
        ("🔬 Tests", len(LAB_TESTS)),
        ("⭐ XP", st.session_state.xp_points),
        ("🔥 Streak", st.session_state.streak)
    ]
    
    for col, (label, value) in zip(cols, metrics):
        with col:
            st.markdown(f'<div class="stat-card"><h3>{label}</h3><div class="stat-number">{value}</div></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="glass-card">
            <h3>Your Progress</h3>
            <p>Level: {level_info['icon']} {level_info['name']}</p>
            <p>Quiz Score: {st.session_state.quiz_score}</p>
            <p>Cases Solved: {st.session_state.total_cases}</p>
            <p>Accuracy: {(st.session_state.correct_diagnoses / max(st.session_state.total_cases, 1) * 100):.1f}%</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="glass-card">
            <h3>Platform Stats</h3>
            <p>Total Users: {get_user_count()}</p>
            <p>Diseases: {len(DISEASE_DATABASE)}</p>
            <p>Drugs: {sum(len(d) for d in DRUG_DATABASE.values())}</p>
            <p>Lab Tests: {len(LAB_TESTS)}</p>
        </div>
        """, unsafe_allow_html=True)

elif page == "Diseases":
    st.markdown('<h2>📚 Disease Library</h2>', unsafe_allow_html=True)
    
    search = st.text_input("🔍 Search:", placeholder="Type disease name...")
    risk_filter = st.selectbox("Risk Level:", ["All", "Critical", "High", "Moderate", "Low"])
    
    filtered = DISEASE_DATABASE.copy()
    if search:
        filtered = {k: v for k, v in filtered.items() if search.lower() in k.lower()}
    if risk_filter != "All":
        filtered = {k: v for k, v in filtered.items() if v.get("risk_level") == risk_filter}
    
    cols = st.columns(2)
    for i, (disease, info) in enumerate(filtered.items()):
        with cols[i % 2]:
            with st.expander(f"🩺 {disease}"):
                risk_color = {"Critical": "#ef4444", "High": "#f59e0b", "Moderate": "#06b6d4", "Low": "#10b981"}
                st.markdown(f"**Risk:** <span style='color:{risk_color.get(info.get('risk_level', 'Low'))}'>{info.get('risk_level')}</span>", unsafe_allow_html=True)
                st.markdown(f"**Symptoms:** {', '.join(info.get('symptoms', [])[:5])}")
                st.markdown(f"**Treatment:** {', '.join(info.get('treatment', [])[:3])}")

elif page == "Case Analysis":
    st.markdown('<h2>🩺 Clinical Case Analysis</h2>', unsafe_allow_html=True)
    
    if st.button("🔄 Generate New Case", type="primary", use_container_width=True):
        disease = random.choice(list(DISEASE_DATABASE.keys()))
        info = DISEASE_DATABASE[disease]
        st.session_state.current_case = {
            "id": f"CASE-{random.randint(1000,9999)}",
            "age": random.randint(18, 85),
            "gender": random.choice(["Male", "Female"]),
            "symptoms": random.sample(info["symptoms"], min(5, len(info["symptoms"]))),
            "diagnosis": disease,
            "risk": info["risk_level"]
        }
        st.rerun()
    
    if st.session_state.current_case:
        case = st.session_state.current_case
        st.markdown(f"""
        <div class="glass-card">
            <h3>Case #{case['id']}</h3>
            <p><strong>Patient:</strong> {case['age']} y/o {case['gender']}</p>
            <p><strong>Symptoms:</strong> {', '.join(case['symptoms'])}</p>
        </div>
        """, unsafe_allow_html=True)
        
        diagnosis = st.selectbox("Your Diagnosis:", list(DISEASE_DATABASE.keys()))
        
        if st.button("✅ Submit", type="primary"):
            st.session_state.total_cases += 1
            if diagnosis == case["diagnosis"]:
                st.session_state.correct_diagnoses += 1
                add_xp(st.session_state.username, 20)
                st.success(f"🎉 Correct! It's {case['diagnosis']}")
            else:
                st.error(f"❌ Wrong. Correct: {case['diagnosis']}")
            
            conn = get_db_connection()
            conn.execute("UPDATE users SET total_cases = ?, correct_diagnoses = ? WHERE username = ?",
                        (st.session_state.total_cases, st.session_state.correct_diagnoses, st.session_state.username))
            conn.commit()

elif page == "Quiz":
    st.markdown('<h2>📝 Medical Quiz</h2>', unsafe_allow_html=True)
    
    diseases = list(DISEASE_DATABASE.keys())
    if diseases:
        disease = random.choice(diseases)
        info = DISEASE_DATABASE[disease]
        correct = info["symptoms"][0]
        wrong = [s for d in diseases if d != disease for s in DISEASE_DATABASE[d]["symptoms"][:1] if s != correct][:3]
        options = [correct] + wrong
        random.shuffle(options)
        
        st.markdown(f'<div class="glass-card"><h3>Which is most characteristic of <strong>{disease}</strong>?</h3></div>', unsafe_allow_html=True)
        
        answer = st.radio("Select:", options, key="quiz_ans")
        
        if st.button("✅ Submit", type="primary"):
            if answer == correct:
                st.session_state.quiz_score += 1
                add_xp(st.session_state.username, 10)
                st.success(f"🎉 Correct! {correct}")
            else:
                st.error(f"❌ Wrong. Answer: {correct}")
            
            conn = get_db_connection()
            conn.execute("UPDATE users SET quiz_score = ? WHERE username = ?",
                        (st.session_state.quiz_score, st.session_state.username))
            conn.commit()
            st.rerun()

elif page == "Comprehensive Exam":
    st.markdown('<h2>📋 Comprehensive Exam</h2>', unsafe_allow_html=True)
    
    if st.session_state.comprehensive_exam is None:
        if st.button("🚀 Start Exam", type="primary", use_container_width=True):
            questions = []
            for disease, info in DISEASE_DATABASE.items():
                if info["symptoms"]:
                    correct = random.choice(info["symptoms"])
                    all_symptoms = [s for d in DISEASE_DATABASE for s in DISEASE_DATABASE[d]["symptoms"] if s != correct]
                    wrong_opts = random.sample(all_symptoms, min(3, len(all_symptoms)))
                    opts = [correct] + wrong_opts[:3]
                    random.shuffle(opts)
                    questions.append({
                        "question": f"Symptom of {disease}?",
                        "options": opts,
                        "correct": opts.index(correct)
                    })
            
            st.session_state.comprehensive_exam = random.sample(questions, min(len(DISEASE_DATABASE), len(questions)))
            st.session_state.comprehensive_answers = {}
            st.session_state.comprehensive_submitted = False
            st.rerun()
    
    elif not st.session_state.comprehensive_submitted:
        for i, q in enumerate(st.session_state.comprehensive_exam):
            st.markdown(f"**{i+1}. {q['question']}**")
            ans = st.radio(f"Q{i}", q["options"], key=f"exam_{i}", label_visibility="collapsed")
            st.session_state.comprehensive_answers[i] = q["options"].index(ans) if ans else -1
        
        if st.button("📤 Submit Exam", type="primary"):
            score = sum(1 for i, q in enumerate(st.session_state.comprehensive_exam) 
                       if st.session_state.comprehensive_answers.get(i) == q["correct"])
            st.session_state.comprehensive_score = score
            st.session_state.comprehensive_submitted = True
            add_xp(st.session_state.username, score * 2)
            st.rerun()
    
    else:
        score = st.session_state.comprehensive_score
        total = len(st.session_state.comprehensive_exam)
        st.markdown(f'<div class="glass-card"><h2>🎉 Score: {score}/{total} ({(score/total*100):.1f}%)</h2></div>', unsafe_allow_html=True)
        if st.button("🔄 Retake"):
            st.session_state.comprehensive_exam = None
            st.rerun()

elif page == "Spaced Repetition":
    st.markdown('<h2>🔄 Spaced Repetition</h2>', unsafe_allow_html=True)
    
    disease = random.choice(list(DISEASE_DATABASE.keys()))
    info = DISEASE_DATABASE[disease]
    
    if st.session_state.flashcard_flipped:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center; padding: 2rem;">
            <h3>{disease}</h3>
            <p><strong>Symptoms:</strong> {', '.join(info['symptoms'][:4])}</p>
            <p style="color: #a78bfa;"><strong>Treatment:</strong> {', '.join(info.get('treatment', [])[:3])}</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Knew It", type="primary", use_container_width=True):
                st.session_state.flashcard_flipped = False
                add_xp(st.session_state.username, 5)
                st.rerun()
        with col2:
            if st.button("❌ Review Again", use_container_width=True):
                st.session_state.flashcard_flipped = False
                st.rerun()
    else:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center; padding: 3rem;">
            <h3>What are the symptoms of {disease}?</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 Reveal Answer", use_container_width=True):
            st.session_state.flashcard_flipped = True
            st.rerun()

elif page == "Lab Tests":
    st.markdown(f'<h2>🔬 Laboratory Tests ({len(LAB_TESTS)} tests)</h2>', unsafe_allow_html=True)
    
    search = st.text_input("🔍 Search tests:")
    category = st.selectbox("Category:", ["All"] + sorted(set(t["category"] for t in LAB_TESTS.values())))
    
    filtered = {k: v for k, v in LAB_TESTS.items() 
               if (not search or search.lower() in k.lower()) 
               and (category == "All" or v["category"] == category)}
    
    if filtered:
        import pandas as pd
        df_data = [{"Test": k, "Category": v["category"], "Normal Range": v["normal"], "Description": v["description"]} 
                  for k, v in filtered.items()]
        st.dataframe(pd.DataFrame(df_data), use_container_width=True, height=400)
    else:
        st.info("No tests found")

elif page == "Pharmacology":
    st.markdown(f'<h2>💊 Pharmacology ({sum(len(d) for d in DRUG_DATABASE.values())} drugs)</h2>', unsafe_allow_html=True)
    
    search = st.text_input("🔍 Search drugs:")
    
    for category, drugs in DRUG_DATABASE.items():
        cat_drugs = {k: v for k, v in drugs.items() if not search or search.lower() in k.lower()}
        if cat_drugs:
            with st.expander(f"📂 {category} ({len(cat_drugs)} drugs)"):
                for drug, info in cat_drugs.items():
                    st.markdown(f"""
                    <div class="glass-card">
                        <h4>{drug}</h4>
                        <p><strong>Class:</strong> {info['class']} | <strong>Dose:</strong> {info['dose']}</p>
                        <p><strong>Indications:</strong> {info['indications']}</p>
                        <p style="color: #ef4444;"><strong>Side Effects:</strong> {info['side_effects']}</p>
                    </div>
                    """, unsafe_allow_html=True)

elif page == "Drug Interactions":
    st.markdown('<h2>⚠️ Drug Interaction Checker</h2>', unsafe_allow_html=True)
    
    all_drugs = [drug for drugs in DRUG_DATABASE.values() for drug in drugs]
    selected = st.multiselect("Select drugs:", all_drugs)
    
    if len(selected) >= 2:
        st.info(f"Selected {len(selected)} drugs. Interaction analysis ready.")
    else:
        st.info("Select 2 or more drugs to check interactions")

elif page == "Leaderboard":
    st.markdown('<h2>🏆 Leaderboard</h2>', unsafe_allow_html=True)
    
    df = get_leaderboard_data()
    if not df.empty:
        for i, (_, row) in enumerate(df.iterrows()):
            medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"#{i+1}"
            st.markdown(f"""
            <div class="glass-card">
                <h3>{medal} {row['username']}</h3>
                <p>⭐ {row['xp_points']} XP | 📊 {row['quiz_score']} Quiz | 🩺 {row['cases_solved']} Cases</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No data yet")

elif page == "Medical News":
    st.markdown('<h2>📰 Medical News</h2>', unsafe_allow_html=True)
    
    news_items = [
        ("New Diabetes Treatment", "GLP-1/GIP dual agonist shows superior glycemic control", "NEJM"),
        ("AI in Radiology", "Machine learning improves cancer detection by 30%", "The Lancet"),
        ("mRNA Vaccines", "Beyond COVID - New applications in cancer therapy", "Nature Medicine"),
        ("Antibiotic Resistance", "WHO warns of critical antimicrobial resistance crisis", "WHO Bulletin"),
        ("Alzheimer's Breakthrough", "New monoclonal antibody slows cognitive decline", "JAMA")
    ]
    
    for title, summary, source in news_items:
        st.markdown(f"""
        <div class="glass-card">
            <h4>📰 {title}</h4>
            <p>{summary}</p>
            <p style="color: #888;">Source: {source}</p>
        </div>
        """, unsafe_allow_html=True)

elif page == "AI Assistant":
    st.markdown('<h2>🧠 AI Symptom Checker</h2>', unsafe_allow_html=True)
    
    symptoms = st.text_area("Enter symptoms (comma-separated):", placeholder="e.g., fever, cough, fatigue")
    
    if st.button("🔍 Analyze", type="primary") and symptoms:
        symptom_list = [s.strip().lower() for s in symptoms.split(",")]
        results = []
        
        for disease, info in DISEASE_DATABASE.items():
            matches = len(set(symptom_list) & set(s.lower() for s in info["symptoms"]))
            if matches > 0:
                results.append((disease, (matches / len(info["symptoms"])) * 100, info["risk_level"]))
        
        results.sort(key=lambda x: x[1], reverse=True)
        
        for disease, match, risk in results[:5]:
            risk_color = {"Critical": "#ef4444", "High": "#f59e0b", "Moderate": "#06b6d4", "Low": "#10b981"}
            st.markdown(f"""
            <div class="glass-card">
                <h4>{disease}</h4>
                <p>Match: {match:.0f}% | Risk: <span style="color:{risk_color.get(risk, '#888')}">{risk}</span></p>
            </div>
            """, unsafe_allow_html=True)

elif page == "Clinical Notes":
    st.markdown('<h2>📝 Clinical Notes</h2>', unsafe_allow_html=True)
    
    with st.form("add_note"):
        patient = st.text_input("Patient Info:")
        note = st.text_area("Clinical Note:")
        if st.form_submit_button("💾 Save", type="primary"):
            conn = get_db_connection()
            conn.execute("INSERT INTO clinical_notes (username, patient_info, note) VALUES (?, ?, ?)",
                        (st.session_state.username, patient, note))
            conn.commit()
            st.success("✅ Note saved!")
            st.rerun()
    
    conn = get_db_connection()
    notes = conn.execute("SELECT * FROM clinical_notes WHERE username = ? ORDER BY created_at DESC LIMIT 20",
                        (st.session_state.username,)).fetchall()
    
    for note in notes:
        st.markdown(f"""
        <div class="glass-card">
            <p><strong>Patient:</strong> {note['patient_info']}</p>
            <p>{note['note']}</p>
            <p style="color: #888;">{note['created_at'][:10]}</p>
        </div>
        """, unsafe_allow_html=True)

elif page == "Achievements":
    st.markdown('<h2>🏆 Achievements</h2>', unsafe_allow_html=True)
    
    achievements = [
        ("First Steps", "🩺", st.session_state.total_cases >= 1),
        ("Case Master", "🏆", st.session_state.total_cases >= 20),
        ("Quiz Beginner", "📝", st.session_state.quiz_score >= 10),
        ("Quiz Expert", "🎓", st.session_state.quiz_score >= 50),
        ("Streak Master", "🔥", st.session_state.streak >= 7),
        ("XP Hunter", "⭐", st.session_state.xp_points >= 100),
        ("XP Champion", "💎", st.session_state.xp_points >= 500),
        ("Diagnostician", "🔍", st.session_state.correct_diagnoses >= 5),
    ]
    
    cols = st.columns(3)
    for i, (name, icon, earned) in enumerate(achievements):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="glass-card" style="text-align: center; opacity: {1 if earned else 0.5};">
                <div style="font-size: 3rem;">{icon}</div>
                <h4>{name}</h4>
                <span class="badge {'badge-success' if earned else 'badge-warning'}">{'✅ Earned' if earned else '🔒 Locked'}</span>
            </div>
            """, unsafe_allow_html=True)

# ================================
# FOOTER
# ================================
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; padding: 2rem; color: rgba(255,255,255,0.3);">
    <p>🩺 Dr.Danyal Medical Training Platform v10.0</p>
    <p style="font-size: 0.8rem;">{len(DISEASE_DATABASE)} Diseases | {sum(len(d) for d in DRUG_DATABASE.values())} Drugs | {len(LAB_TESTS)} Lab Tests | {get_user_count()} Users</p>
    <p style="font-size: 0.7rem;">© {datetime.now().year} All rights reserved. Secure Platform.</p>
</div>
""", unsafe_allow_html=True)
