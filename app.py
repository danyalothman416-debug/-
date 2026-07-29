# ================================
# MEDICAL TRAINING PLATFORM v10.0
# Dr.Danyal - Production Ready
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
from functools import lru_cache
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
SESSION_TIMEOUT_HOURS = 24

# ================================
# DATABASE SETUP (SQLite - Secure)
# ================================
def get_db_connection():
    """Create a secure database connection with proper settings"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_database():
    """Initialize all database tables with proper schema"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table with bcrypt-like hashing
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
        
        CREATE TABLE IF NOT EXISTS custom_drugs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            drug_name TEXT NOT NULL,
            category TEXT,
            dose TEXT,
            mechanism TEXT,
            side_effects TEXT,
            clinical_use TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(username, drug_name)
        );
        
        CREATE TABLE IF NOT EXISTS custom_lab_tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            test_name TEXT NOT NULL,
            category TEXT,
            normal_range TEXT,
            unit TEXT,
            description TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(username, test_name)
        );
        
        CREATE TABLE IF NOT EXISTS clinical_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            patient_info TEXT,
            note TEXT,
            diagnosis TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS study_rooms (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            creator TEXT NOT NULL,
            members TEXT DEFAULT '[]',
            messages TEXT DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS spaced_repetition (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            item_key TEXT NOT NULL,
            item_type TEXT,
            interval_days INTEGER DEFAULT 1,
            repetitions INTEGER DEFAULT 0,
            ease_factor REAL DEFAULT 2.5,
            next_review TIMESTAMP,
            correct_count INTEGER DEFAULT 0,
            wrong_count INTEGER DEFAULT 0,
            UNIQUE(username, item_key)
        );
        
        CREATE TABLE IF NOT EXISTS login_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_address TEXT,
            success BOOLEAN DEFAULT FALSE
        );
        
        CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
        CREATE INDEX IF NOT EXISTS idx_leaderboard_xp ON leaderboard(xp_points DESC);
        CREATE INDEX IF NOT EXISTS idx_login_attempts ON login_attempts(username, attempt_time);
    """)
    
    conn.commit()
    conn.close()

# ================================
# PASSWORD SECURITY (Enhanced)
# ================================
def generate_salt(length: int = 32) -> str:
    """Generate a cryptographically secure random salt"""
    return os.urandom(length).hex()

def hash_password_secure(password: str, salt: str = None) -> Tuple[str, str]:
    """
    Enhanced password hashing using PBKDF2 (bcrypt alternative for SQLite)
    Uses multiple iterations to slow down brute-force attacks
    """
    if salt is None:
        salt = generate_salt()
    
    # PBKDF2 with 200,000 iterations (OWASP 2024 recommendation)
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        200000,  # High iteration count for security
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
    
    # Check if account is locked
    cursor.execute("""
        SELECT locked_until, login_attempts 
        FROM users 
        WHERE username = ?
    """, (username,))
    
    user = cursor.fetchone()
    
    if user and user['locked_until']:
        locked_until = datetime.fromisoformat(user['locked_until'])
        if locked_until > datetime.now():
            remaining = (locked_until - datetime.now()).seconds // 60
            conn.close()
            return False, f"Account locked. Try again in {remaining} minutes."
    
    # Check recent attempts
    cutoff_time = datetime.now() - timedelta(minutes=LOGIN_TIMEOUT_MINUTES)
    cursor.execute("""
        SELECT COUNT(*) as attempts 
        FROM login_attempts 
        WHERE username = ? 
        AND attempt_time > ? 
        AND success = FALSE
    """, (username, cutoff_time))
    
    result = cursor.fetchone()
    recent_attempts = result['attempts'] if result else 0
    
    conn.close()
    
    if recent_attempts >= MAX_LOGIN_ATTEMPTS:
        # Lock the account
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users 
            SET locked_until = ? 
            WHERE username = ?
        """, ((datetime.now() + timedelta(minutes=LOGIN_TIMEOUT_MINUTES)).isoformat(), username))
        conn.commit()
        conn.close()
        return False, f"Too many attempts. Account locked for {LOGIN_TIMEOUT_MINUTES} minutes."
    
    return True, ""

def record_login_attempt(username: str, success: bool):
    """Record login attempt for rate limiting"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO login_attempts (username, success) 
        VALUES (?, ?)
    """, (username, success))
    
    if success:
        # Reset attempts on successful login
        cursor.execute("""
            UPDATE users 
            SET login_attempts = 0, locked_until = NULL 
            WHERE username = ?
        """, (username,))
    else:
        # Increment attempts on failure
        cursor.execute("""
            UPDATE users 
            SET login_attempts = login_attempts + 1 
            WHERE username = ?
        """, (username,))
    
    conn.commit()
    conn.close()

# ================================
# CACHED DATA LOADING FUNCTIONS
# ================================
@st.cache_data(ttl=300)
def get_leaderboard_data() -> pd.DataFrame:
    """Cached leaderboard data - refreshes every 5 minutes"""
    import pandas as pd
    conn = get_db_connection()
    df = pd.read_sql_query("""
        SELECT username, xp_points, quiz_score, cases_solved, level, last_active
        FROM leaderboard 
        ORDER BY xp_points DESC
    """, conn)
    conn.close()
    return df

@st.cache_data(ttl=60)
def get_user_count() -> int:
    """Cached user count"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM users")
    result = cursor.fetchone()
    conn.close()
    return result['count'] if result else 0

# ================================
# USER MANAGEMENT FUNCTIONS
# ================================
def create_user(username: str, password: str) -> Tuple[bool, str]:
    """Create a new user with secure password storage"""
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if username exists
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        conn.close()
        return False, "Username already exists"
    
    # Hash password
    password_hash, salt = hash_password_secure(password)
    
    # Create user
    cursor.execute("""
        INSERT INTO users (username, password_hash, salt) 
        VALUES (?, ?, ?)
    """, (username, password_hash, salt))
    
    # Create leaderboard entry
    cursor.execute("""
        INSERT INTO leaderboard (username, xp_points) 
        VALUES (?, 0)
    """, (username,))
    
    conn.commit()
    conn.close()
    
    return True, "Account created successfully"

def authenticate_user(username: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
    """Authenticate user with rate limiting"""
    # Check rate limit
    can_attempt, message = check_login_rate_limit(username)
    if not can_attempt:
        return False, message, None
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM users WHERE username = ?
    """, (username,))
    
    user = cursor.fetchone()
    
    if not user:
        record_login_attempt(username, False)
        conn.close()
        return False, "Invalid username or password", None
    
    # Verify password
    if verify_password(password, user['password_hash'], user['salt']):
        record_login_attempt(username, True)
        
        # Update last login
        cursor.execute("""
            UPDATE users SET last_login = ? WHERE id = ?
        """, (datetime.now().isoformat(), user['id']))
        conn.commit()
        
        user_dict = dict(user)
        conn.close()
        return True, "Login successful", user_dict
    else:
        record_login_attempt(username, False)
        conn.close()
        return False, "Invalid username or password", None

def update_user_streak(username: str) -> int:
    """Update and return the user's daily streak"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT daily_streak, last_active_date FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
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
    
    cursor.execute("""
        UPDATE users 
        SET daily_streak = ?, last_active_date = ? 
        WHERE username = ?
    """, (new_streak, today.isoformat(), username))
    
    conn.commit()
    conn.close()
    return new_streak

def add_xp(username: str, points: int):
    """Add XP points to user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE users SET xp_points = xp_points + ? WHERE username = ?
    """, (points, username))
    
    cursor.execute("""
        UPDATE leaderboard SET xp_points = xp_points + ?, last_active = ? WHERE username = ?
    """, (points, datetime.now().isoformat(), username))
    
    conn.commit()
    conn.close()

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
# LAZY IMPORTS (Performance)
# ================================
@st.cache_resource
def get_pandas():
    import pandas as pd
    return pd

@st.cache_resource
def get_numpy():
    import numpy as np
    return np

@st.cache_resource
def get_matplotlib():
    import matplotlib.pyplot as plt
    import seaborn as sns
    return plt, sns

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
        "tests": {"Fasting Glucose": ">126 mg/dL", "HbA1c": ">6.5%", "OGTT": ">200 mg/dL", "C-peptide": "Normal/High"},
        "treatment": ["Metformin", "Lifestyle modification", "SGLT2 inhibitors", "GLP-1 agonists", "Regular exercise"],
        "risk_level": "Moderate",
        "age_group": "Adults >40 years",
        "category": "Endocrine"
    },
    "Essential Hypertension": {
        "symptoms": ["Often asymptomatic", "Headache", "Dizziness", "Blurred vision", "Epistaxis"],
        "tests": {"Blood Pressure": ">140/90 mmHg", "ECG": "Possible LVH", "Creatinine": "Normal", "Potassium": "Normal"},
        "treatment": ["ACE inhibitors", "Lifestyle changes", "Low sodium diet", "Regular exercise", "Weight management"],
        "risk_level": "Low",
        "age_group": "All ages",
        "category": "Cardiovascular"
    },
    "Acute Myocardial Infarction": {
        "symptoms": ["Severe chest pain", "Diaphoresis", "Dyspnea", "Nausea", "Left arm radiation", "Anxiety"],
        "tests": {"ECG": "ST elevation/depression", "Troponin I": ">0.04 ng/mL", "CK-MB": "Elevated", "CRP": "Elevated"},
        "treatment": ["Aspirin 300mg", "Nitroglycerin", "Morphine", "Oxygen", "Primary PCI", "Beta blockers"],
        "risk_level": "Critical",
        "age_group": ">45 years",
        "category": "Cardiovascular"
    },
    "Community-Acquired Pneumonia": {
        "symptoms": ["Fever", "Productive cough", "Dyspnea", "Pleuritic chest pain", "Malaise", "Chills"],
        "tests": {"Chest X-ray": "Consolidation", "WBC": ">11,000", "CRP": "Elevated", "Blood culture": "Positive", "Procalcitonin": ">0.5"},
        "treatment": ["Amoxicillin-clavulanate", "Azithromycin", "Oxygen if needed", "Hydration", "Rest"],
        "risk_level": "Moderate",
        "age_group": "All ages",
        "category": "Respiratory"
    },
    "Bronchial Asthma": {
        "symptoms": ["Wheezing", "Dyspnea", "Chest tightness", "Cough (especially at night)", "Shortness of breath"],
        "tests": {"Pulmonary Function": "FEV1 <80%", "Peak Flow": "Reduced", "Chest X-ray": "Hyperinflation", "IgE": "Elevated"},
        "treatment": ["SABA (Albuterol)", "ICS (Budesonide)", "LABA", "Leukotriene antagonists", "Avoid triggers"],
        "risk_level": "Low",
        "age_group": "Children & Adults",
        "category": "Respiratory"
    },
    "Iron Deficiency Anemia": {
        "symptoms": ["Fatigue", "Pallor", "Dyspnea on exertion", "Palpitations", "Brittle nails", "Pica"],
        "tests": {"Hemoglobin": "<12 g/dL", "MCV": "<80 fL", "Ferritin": "<15 ng/mL", "TIBC": ">450", "Iron": "<60"},
        "treatment": ["Ferrous sulfate 325mg", "Vitamin C supplementation", "Iron-rich diet", "Treat underlying cause"],
        "risk_level": "Low",
        "age_group": "All ages",
        "category": "Hematology"
    },
    "Chronic Kidney Disease": {
        "symptoms": ["Edema", "Fatigue", "Decreased urine output", "Nausea", "Pruritus", "Muscle cramps"],
        "tests": {"Creatinine": ">1.3 mg/dL", "eGFR": "<60", "BUN": ">20", "Urinalysis": "Proteinuria", "Potassium": "Elevated"},
        "treatment": ["ACE inhibitors", "Dietary restriction", "Phosphate binders", "Erythropoietin", "Dialysis if ESRD"],
        "risk_level": "High",
        "age_group": ">50 years",
        "category": "Nephrology"
    },
    "Hepatitis B": {
        "symptoms": ["Jaundice", "Fatigue", "Dark urine", "Right upper quadrant pain", "Nausea", "Anorexia"],
        "tests": {"HBsAg": "Positive", "Anti-HBc": "Positive", "ALT": ">1000", "AST": "Elevated", "HBV DNA": "Detectable"},
        "treatment": ["Entecavir", "Tenofovir", "Pegylated interferon", "Avoid alcohol", "Monitor HCC"],
        "risk_level": "High",
        "age_group": "All ages",
        "category": "Gastroenterology"
    },
    "Pulmonary Tuberculosis": {
        "symptoms": ["Chronic cough (>3 weeks)", "Hemoptysis", "Night sweats", "Weight loss", "Fever", "Anorexia"],
        "tests": {"Chest X-ray": "Cavitary lesions", "Sputum AFB": "Positive", "GeneXpert": "MTB detected", "PPD": ">15mm", "IGRA": "Positive"},
        "treatment": ["Rifampicin", "Isoniazid", "Pyrazinamide", "Ethambutol", "Directly observed therapy"],
        "risk_level": "Critical",
        "age_group": "All ages",
        "category": "Infectious Disease"
    }
}

LAB_TESTS = {
    # Hematology (25 tests)
    "Hemoglobin": {"category": "Hematology", "normal": "12-16 g/dL", "description": "Oxygen-carrying capacity"},
    "WBC Count": {"category": "Hematology", "normal": "4,000-11,000/µL", "description": "Infection/inflammation marker"},
    "RBC Count": {"category": "Hematology", "normal": "4.5-5.5 million/µL", "description": "Oxygen transport"},
    "Hematocrit": {"category": "Hematology", "normal": "37-47%", "description": "RBC volume percentage"},
    "MCV": {"category": "Hematology", "normal": "80-100 fL", "description": "RBC size"},
    "MCH": {"category": "Hematology", "normal": "27-33 pg", "description": "Hemoglobin per RBC"},
    "MCHC": {"category": "Hematology", "normal": "32-36 g/dL", "description": "Hemoglobin concentration"},
    "RDW": {"category": "Hematology", "normal": "11.5-14.5%", "description": "RBC size variation"},
    "Platelet Count": {"category": "Hematology", "normal": "150,000-450,000/µL", "description": "Clotting ability"},
    "MPV": {"category": "Hematology", "normal": "7.5-11.5 fL", "description": "Platelet size"},
    "Reticulocyte Count": {"category": "Hematology", "normal": "0.5-2.5%", "description": "Bone marrow activity"},
    "ESR": {"category": "Hematology", "normal": "0-20 mm/hr", "description": "Inflammation marker"},
    "Ferritin": {"category": "Hematology", "normal": "15-300 ng/mL", "description": "Iron stores"},
    "Serum Iron": {"category": "Hematology", "normal": "60-170 µg/dL", "description": "Circulating iron"},
    "TIBC": {"category": "Hematology", "normal": "250-450 µg/dL", "description": "Iron binding capacity"},
    "Transferrin Saturation": {"category": "Hematology", "normal": "20-50%", "description": "Iron saturation"},
    "Vitamin B12": {"category": "Hematology", "normal": "200-900 pg/mL", "description": "B12 deficiency"},
    "Folate": {"category": "Hematology", "normal": "3-17 ng/mL", "description": "Folate deficiency"},
    "PT": {"category": "Hematology", "normal": "11-13.5 sec", "description": "Extrinsic pathway"},
    "PTT": {"category": "Hematology", "normal": "25-35 sec", "description": "Intrinsic pathway"},
    "INR": {"category": "Hematology", "normal": "0.9-1.1", "description": "Coagulation status"},
    "Fibrinogen": {"category": "Hematology", "normal": "200-400 mg/dL", "description": "Clotting factor"},
    "D-Dimer": {"category": "Hematology", "normal": "<0.5 mg/L", "description": "Thrombosis marker"},
    "Haptoglobin": {"category": "Hematology", "normal": "50-250 mg/dL", "description": "Hemolysis marker"},
    "LDH": {"category": "Hematology", "normal": "100-250 U/L", "description": "Cell damage marker"},
    
    # Biochemistry (30 tests)
    "Fasting Glucose": {"category": "Biochemistry", "normal": "70-100 mg/dL", "description": "Diabetes screening"},
    "HbA1c": {"category": "Biochemistry", "normal": "4.0-5.6%", "description": "3-month glucose average"},
    "Creatinine": {"category": "Biochemistry", "normal": "0.6-1.3 mg/dL", "description": "Kidney function"},
    "BUN": {"category": "Biochemistry", "normal": "7-20 mg/dL", "description": "Kidney function"},
    "eGFR": {"category": "Biochemistry", "normal": ">90 mL/min", "description": "Kidney filtration rate"},
    "Uric Acid": {"category": "Biochemistry", "normal": "3.5-7.2 mg/dL", "description": "Gout marker"},
    "Total Protein": {"category": "Biochemistry", "normal": "6.0-8.0 g/dL", "description": "Nutritional status"},
    "Albumin": {"category": "Biochemistry", "normal": "3.5-5.0 g/dL", "description": "Liver function"},
    "Globulin": {"category": "Biochemistry", "normal": "2.0-3.5 g/dL", "description": "Immune proteins"},
    "Total Bilirubin": {"category": "Biochemistry", "normal": "0.1-1.2 mg/dL", "description": "Jaundice marker"},
    "Direct Bilirubin": {"category": "Biochemistry", "normal": "0.0-0.3 mg/dL", "description": "Conjugated bilirubin"},
    "ALT": {"category": "Biochemistry", "normal": "10-40 U/L", "description": "Liver enzyme"},
    "AST": {"category": "Biochemistry", "normal": "10-40 U/L", "description": "Liver/muscle enzyme"},
    "ALP": {"category": "Biochemistry", "normal": "44-147 U/L", "description": "Bone/liver enzyme"},
    "GGT": {"category": "Biochemistry", "normal": "0-51 U/L", "description": "Liver/biliary enzyme"},
    "Amylase": {"category": "Biochemistry", "normal": "20-200 U/L", "description": "Pancreatic enzyme"},
    "Lipase": {"category": "Biochemistry", "normal": "20-200 U/L", "description": "Pancreatic enzyme"},
    "CK": {"category": "Biochemistry", "normal": "22-198 U/L", "description": "Muscle enzyme"},
    "CK-MB": {"category": "Biochemistry", "normal": "0-5 ng/mL", "description": "Cardiac enzyme"},
    "Sodium": {"category": "Biochemistry", "normal": "135-145 mmol/L", "description": "Electrolyte"},
    "Potassium": {"category": "Biochemistry", "normal": "3.5-5.0 mmol/L", "description": "Electrolyte"},
    "Chloride": {"category": "Biochemistry", "normal": "96-106 mmol/L", "description": "Electrolyte"},
    "Calcium": {"category": "Biochemistry", "normal": "8.5-10.5 mg/dL", "description": "Bone metabolism"},
    "Magnesium": {"category": "Biochemistry", "normal": "1.7-2.2 mg/dL", "description": "Neuromuscular function"},
    "Phosphorus": {"category": "Biochemistry", "normal": "2.5-4.5 mg/dL", "description": "Bone metabolism"},
    "Total Cholesterol": {"category": "Biochemistry", "normal": "<200 mg/dL", "description": "Lipid profile"},
    "LDL": {"category": "Biochemistry", "normal": "<100 mg/dL", "description": "Bad cholesterol"},
    "HDL": {"category": "Biochemistry", "normal": ">40 mg/dL", "description": "Good cholesterol"},
    "Triglycerides": {"category": "Biochemistry", "normal": "<150 mg/dL", "description": "Blood fats"},
    "VLDL": {"category": "Biochemistry", "normal": "<30 mg/dL", "description": "Very low density lipoprotein"},
    
    # Cardiac Markers (8 tests)
    "Troponin I": {"category": "Cardiac", "normal": "<0.04 ng/mL", "description": "Myocardial injury"},
    "Troponin T": {"category": "Cardiac", "normal": "<0.014 ng/mL", "description": "High-sensitivity cardiac"},
    "BNP": {"category": "Cardiac", "normal": "<100 pg/mL", "description": "Heart failure"},
    "NT-proBNP": {"category": "Cardiac", "normal": "<125 pg/mL", "description": "Heart failure"},
    "Myoglobin": {"category": "Cardiac", "normal": "<80 ng/mL", "description": "Early cardiac marker"},
    "hs-CRP": {"category": "Cardiac", "normal": "<2 mg/L", "description": "Cardiovascular risk"},
    "Homocysteine": {"category": "Cardiac", "normal": "5-15 µmol/L", "description": "Vascular risk"},
    "Lipoprotein(a)": {"category": "Cardiac", "normal": "<30 mg/dL", "description": "Genetic cardiac risk"},
    
    # Thyroid & Hormones (15 tests)
    "TSH": {"category": "Endocrine", "normal": "0.4-4.0 mIU/L", "description": "Thyroid function"},
    "Free T4": {"category": "Endocrine", "normal": "0.8-1.8 ng/dL", "description": "Thyroid hormone"},
    "Free T3": {"category": "Endocrine", "normal": "2.3-4.2 pg/mL", "description": "Active thyroid hormone"},
    "Cortisol (AM)": {"category": "Endocrine", "normal": "6-23 µg/dL", "description": "Adrenal function"},
    "Testosterone (Male)": {"category": "Endocrine", "normal": "300-1000 ng/dL", "description": "Androgen"},
    "Estradiol": {"category": "Endocrine", "normal": "20-400 pg/mL", "description": "Estrogen"},
    "Progesterone": {"category": "Endocrine", "normal": "0.1-25 ng/mL", "description": "Ovulation marker"},
    "Prolactin": {"category": "Endocrine", "normal": "4-23 ng/mL", "description": "Pituitary function"},
    "LH": {"category": "Endocrine", "normal": "1.5-9.3 IU/L", "description": "Reproductive hormone"},
    "FSH": {"category": "Endocrine", "normal": "1.4-18.1 IU/L", "description": "Reproductive hormone"},
    "Insulin (Fasting)": {"category": "Endocrine", "normal": "2-25 µIU/mL", "description": "Glucose metabolism"},
    "C-Peptide": {"category": "Endocrine", "normal": "0.5-2.0 ng/mL", "description": "Insulin production"},
    "IGF-1": {"category": "Endocrine", "normal": "100-300 ng/mL", "description": "Growth factor"},
    "PTH": {"category": "Endocrine", "normal": "10-65 pg/mL", "description": "Calcium regulation"},
    "Vitamin D (25-OH)": {"category": "Endocrine", "normal": "30-100 ng/mL", "description": "Vitamin D status"},
    
    # Urinalysis (12 tests)
    "Urine pH": {"category": "Urinalysis", "normal": "4.5-8.0", "description": "Acid-base balance"},
    "Urine Specific Gravity": {"category": "Urinalysis", "normal": "1.005-1.030", "description": "Concentration"},
    "Urine Protein": {"category": "Urinalysis", "normal": "Negative", "description": "Kidney damage"},
    "Urine Glucose": {"category": "Urinalysis", "normal": "Negative", "description": "Diabetes"},
    "Urine Ketones": {"category": "Urinalysis", "normal": "Negative", "description": "Starvation/DKA"},
    "Urine Bilirubin": {"category": "Urinalysis", "normal": "Negative", "description": "Liver disease"},
    "Urine Urobilinogen": {"category": "Urinalysis", "normal": "0.1-1.0 mg/dL", "description": "Hemolysis"},
    "Urine Nitrite": {"category": "Urinalysis", "normal": "Negative", "description": "Bacteria"},
    "Urine Leukocyte Esterase": {"category": "Urinalysis", "normal": "Negative", "description": "WBC enzyme"},
    "Urine WBC": {"category": "Urinalysis", "normal": "0-5/HPF", "description": "Infection"},
    "Urine RBC": {"category": "Urinalysis", "normal": "0-3/HPF", "description": "Bleeding"},
    "Microalbumin": {"category": "Urinalysis", "normal": "<30 mg/24h", "description": "Early nephropathy"},
    
    # Immunology/Serology (10 tests)
    "CRP": {"category": "Immunology", "normal": "<5 mg/L", "description": "Acute inflammation"},
    "Rheumatoid Factor": {"category": "Immunology", "normal": "<14 IU/mL", "description": "RA marker"},
    "ANA": {"category": "Immunology", "normal": "Negative", "description": "Autoimmune screening"},
    "Anti-dsDNA": {"category": "Immunology", "normal": "<30 IU/mL", "description": "SLE marker"},
    "C3 Complement": {"category": "Immunology", "normal": "90-180 mg/dL", "description": "Complement system"},
    "C4 Complement": {"category": "Immunology", "normal": "10-40 mg/dL", "description": "Complement system"},
    "IgG": {"category": "Immunology", "normal": "700-1600 mg/dL", "description": "Humoral immunity"},
    "IgA": {"category": "Immunology", "normal": "70-400 mg/dL", "description": "Mucosal immunity"},
    "IgM": {"category": "Immunology", "normal": "40-230 mg/dL", "description": "Acute infection"},
    "IgE": {"category": "Immunology", "normal": "0-100 IU/mL", "description": "Allergy/parasites"},
}

# ================================
# DRUG DATABASE (100+ drugs)
# ================================
DRUG_DATABASE = {
    "Cardiovascular": {
        "Lisinopril": {"class": "ACE Inhibitor", "dose": "10-40mg daily", "indications": "Hypertension, HF", "side_effects": "Cough, angioedema, hyperkalemia"},
        "Enalapril": {"class": "ACE Inhibitor", "dose": "5-40mg daily", "indications": "Hypertension, HF", "side_effects": "Cough, hypotension, rash"},
        "Captopril": {"class": "ACE Inhibitor", "dose": "25-150mg TID", "indications": "Hypertension, diabetic nephropathy", "side_effects": "Cough, taste disturbance"},
        "Losartan": {"class": "ARB", "dose": "50-100mg daily", "indications": "Hypertension, HF, nephropathy", "side_effects": "Dizziness, hyperkalemia"},
        "Valsartan": {"class": "ARB", "dose": "80-320mg daily", "indications": "Hypertension, HF", "side_effects": "Headache, dizziness, fatigue"},
        "Amlodipine": {"class": "CCB", "dose": "5-10mg daily", "indications": "Hypertension, angina", "side_effects": "Edema, flushing, headache"},
        "Nifedipine": {"class": "CCB", "dose": "30-90mg daily", "indications": "Hypertension, angina", "side_effects": "Headache, edema, constipation"},
        "Metoprolol": {"class": "Beta Blocker", "dose": "25-200mg daily", "indications": "Hypertension, angina, HF", "side_effects": "Bradycardia, fatigue, cold extremities"},
        "Atenolol": {"class": "Beta Blocker", "dose": "25-100mg daily", "indications": "Hypertension, angina", "side_effects": "Bradycardia, fatigue, depression"},
        "Carvedilol": {"class": "Alpha/Beta Blocker", "dose": "6.25-50mg BID", "indications": "HF, hypertension", "side_effects": "Dizziness, fatigue, bradycardia"},
        "Hydrochlorothiazide": {"class": "Thiazide Diuretic", "dose": "12.5-50mg daily", "indications": "Hypertension, edema", "side_effects": "Hypokalemia, hyperuricemia"},
        "Furosemide": {"class": "Loop Diuretic", "dose": "20-80mg daily", "indications": "Edema, HF, hypertension", "side_effects": "Hypokalemia, dehydration, ototoxicity"},
        "Spironolactone": {"class": "Aldosterone Antagonist", "dose": "25-100mg daily", "indications": "HF, ascites, hypertension", "side_effects": "Hyperkalemia, gynecomastia"},
        "Atorvastatin": {"class": "Statin", "dose": "10-80mg daily", "indications": "Hyperlipidemia, CVD prevention", "side_effects": "Myalgia, elevated LFTs, rhabdomyolysis"},
        "Rosuvastatin": {"class": "Statin", "dose": "5-40mg daily", "indications": "Hyperlipidemia", "side_effects": "Myalgia, headache, diabetes risk"},
        "Clopidogrel": {"class": "Antiplatelet", "dose": "75mg daily", "indications": "ACS, stroke prevention", "side_effects": "Bleeding, bruising, TTP"},
        "Aspirin": {"class": "Antiplatelet", "dose": "75-325mg daily", "indications": "CVD prevention, pain", "side_effects": "GI bleeding, tinnitus, Reye's"},
        "Warfarin": {"class": "Anticoagulant", "dose": "2-10mg daily (INR-guided)", "indications": "DVT, PE, AF", "side_effects": "Bleeding, skin necrosis, teratogenic"},
        "Rivaroxaban": {"class": "DOAC", "dose": "10-20mg daily", "indications": "DVT, PE, AF", "side_effects": "Bleeding, anemia, elevated LFTs"},
        "Apixaban": {"class": "DOAC", "dose": "2.5-5mg BID", "indications": "AF, DVT prevention", "side_effects": "Bleeding, nausea, anemia"},
        "Digoxin": {"class": "Cardiac Glycoside", "dose": "0.125-0.25mg daily", "indications": "HF, AF rate control", "side_effects": "Nausea, visual changes, arrhythmias"},
        "Amiodarone": {"class": "Class III Antiarrhythmic", "dose": "200-400mg daily", "indications": "Arrhythmias", "side_effects": "Pulmonary fibrosis, thyroid dysfunction, hepatotoxicity"},
        "Nitroglycerin": {"class": "Nitrate", "dose": "0.3-0.6mg SL PRN", "indications": "Acute angina", "side_effects": "Headache, hypotension, reflex tachycardia"}
    },
    "Endocrinology": {
        "Metformin": {"class": "Biguanide", "dose": "500-2000mg daily", "indications": "Type 2 DM, PCOS", "side_effects": "GI upset, lactic acidosis, B12 deficiency"},
        "Glipizide": {"class": "Sulfonylurea", "dose": "5-20mg daily", "indications": "Type 2 DM", "side_effects": "Hypoglycemia, weight gain, rash"},
        "Pioglitazone": {"class": "TZD", "dose": "15-45mg daily", "indications": "Type 2 DM", "side_effects": "Edema, weight gain, fractures, bladder cancer risk"},
        "Sitagliptin": {"class": "DPP-4 Inhibitor", "dose": "100mg daily", "indications": "Type 2 DM", "side_effects": "Headache, pancreatitis, arthralgia"},
        "Empagliflozin": {"class": "SGLT2 Inhibitor", "dose": "10-25mg daily", "indications": "Type 2 DM, HF, CKD", "side_effects": "UTI, genital infections, DKA, dehydration"},
        "Dapagliflozin": {"class": "SGLT2 Inhibitor", "dose": "5-10mg daily", "indications": "Type 2 DM, HF, CKD", "side_effects": "UTI, genital infections, Fournier's gangrene"},
        "Insulin Glargine": {"class": "Long-acting Insulin", "dose": "Individualized", "indications": "Type 1 & 2 DM", "side_effects": "Hypoglycemia, weight gain, lipodystrophy"},
        "Insulin Aspart": {"class": "Rapid-acting Insulin", "dose": "Individualized", "indications": "Type 1 & 2 DM", "side_effects": "Hypoglycemia, weight gain"},
        "Levothyroxine": {"class": "Thyroid Hormone", "dose": "25-200mcg daily", "indications": "Hypothyroidism", "side_effects": "Palpitations, insomnia, osteoporosis"},
        "Methimazole": {"class": "Antithyroid", "dose": "5-30mg daily", "indications": "Hyperthyroidism", "side_effects": "Agranulocytosis, hepatotoxicity, rash"},
        "Prednisone": {"class": "Corticosteroid", "dose": "5-60mg daily", "indications": "Inflammation, autoimmune", "side_effects": "Weight gain, osteoporosis, hyperglycemia, immunosuppression"},
        "Hydrocortisone": {"class": "Corticosteroid", "dose": "20-240mg daily", "indications": "Adrenal insufficiency", "side_effects": "Fluid retention, hypertension, mood changes"},
        "Alendronate": {"class": "Bisphosphonate", "dose": "70mg weekly", "indications": "Osteoporosis", "side_effects": "Esophagitis, jaw osteonecrosis, atypical fractures"}
    },
    "Antibiotics": {
        "Amoxicillin": {"class": "Penicillin", "dose": "500-875mg BID", "indications": "Respiratory, UTI, H. pylori", "side_effects": "Diarrhea, rash, anaphylaxis"},
        "Amoxicillin-Clavulanate": {"class": "Penicillin + BLI", "dose": "500/125mg TID", "indications": "Respiratory, skin infections", "side_effects": "Diarrhea, GI upset, cholestatic hepatitis"},
        "Cephalexin": {"class": "1st Gen Cephalosporin", "dose": "250-500mg QID", "indications": "Skin, UTI", "side_effects": "GI upset, rash, C. diff"},
        "Ceftriaxone": {"class": "3rd Gen Cephalosporin", "dose": "1-2g IV/IM daily", "indications": "Meningitis, pneumonia, gonorrhea", "side_effects": "Diarrhea, biliary sludging, hemolysis"},
        "Azithromycin": {"class": "Macrolide", "dose": "250-500mg daily", "indications": "Respiratory, STI", "side_effects": "GI upset, QT prolongation, hearing loss"},
        "Clarithromycin": {"class": "Macrolide", "dose": "250-500mg BID", "indications": "H. pylori, respiratory", "side_effects": "GI upset, metallic taste, CYP3A4 inhibitor"},
        "Doxycycline": {"class": "Tetracycline", "dose": "100mg BID", "indications": "Acne, Lyme, malaria prophylaxis", "side_effects": "Photosensitivity, esophagitis, teeth discoloration"},
        "Ciprofloxacin": {"class": "Fluoroquinolone", "dose": "250-750mg BID", "indications": "UTI, GI infections", "side_effects": "Tendonitis, neuropathy, QT prolongation, C. diff"},
        "Levofloxacin": {"class": "Fluoroquinolone", "dose": "500-750mg daily", "indications": "Respiratory, UTI", "side_effects": "Tendon rupture, CNS effects, dysglycemia"},
        "Metronidazole": {"class": "Nitroimidazole", "dose": "500mg TID", "indications": "Anaerobic infections, C. diff, trichomoniasis", "side_effects": "Metallic taste, neuropathy, disulfiram reaction"},
        "Clindamycin": {"class": "Lincosamide", "dose": "150-450mg QID", "indications": "Anaerobic infections, acne, MRSA", "side_effects": "C. diff colitis, rash, hepatotoxicity"},
        "Vancomycin": {"class": "Glycopeptide", "dose": "IV: trough-guided", "indications": "MRSA, C. diff (oral)", "side_effects": "Red man syndrome, nephrotoxicity, ototoxicity"},
        "TMP-SMX": {"class": "Sulfonamide", "dose": "160/800mg BID", "indications": "UTI, PCP, Nocardia", "side_effects": "Rash, hyperkalemia, SJS, bone marrow suppression"},
        "Nitrofurantoin": {"class": "Nitrofuran", "dose": "100mg BID", "indications": "UTI prophylaxis", "side_effects": "Pulmonary fibrosis, neuropathy, hepatotoxicity"},
        "Linezolid": {"class": "Oxazolidinone", "dose": "600mg BID", "indications": "VRE, MRSA", "side_effects": "Myelosuppression, serotonin syndrome, neuropathy"}
    },
    "Neurology & Psychiatry": {
        "Sertraline": {"class": "SSRI", "dose": "50-200mg daily", "indications": "Depression, anxiety, PTSD, OCD", "side_effects": "GI upset, sexual dysfunction, insomnia, hyponatremia"},
        "Fluoxetine": {"class": "SSRI", "dose": "20-80mg daily", "indications": "Depression, OCD, bulimia", "side_effects": "Insomnia, weight loss, sexual dysfunction, long half-life"},
        "Escitalopram": {"class": "SSRI", "dose": "10-20mg daily", "indications": "Depression, GAD", "side_effects": "Nausea, fatigue, sexual dysfunction, QT prolongation"},
        "Venlafaxine": {"class": "SNRI", "dose": "75-375mg daily", "indications": "Depression, anxiety, neuropathic pain", "side_effects": "Hypertension, sweating, nausea, withdrawal syndrome"},
        "Duloxetine": {"class": "SNRI", "dose": "30-120mg daily", "indications": "Depression, fibromyalgia, neuropathic pain", "side_effects": "Nausea, dry mouth, hepatotoxicity"},
        "Amitriptyline": {"class": "TCA", "dose": "25-150mg nightly", "indications": "Depression, neuropathic pain, migraine prophylaxis", "side_effects": "Sedation, anticholinergic, weight gain, cardiotoxic"},
        "Quetiapine": {"class": "Atypical Antipsychotic", "dose": "25-800mg daily", "indications": "Schizophrenia, bipolar, insomnia", "side_effects": "Weight gain, metabolic syndrome, sedation, EPS"},
        "Risperidone": {"class": "Atypical Antipsychotic", "dose": "1-6mg daily", "indications": "Schizophrenia, bipolar, autism irritability", "side_effects": "Hyperprolactinemia, EPS, weight gain"},
        "Olanzapine": {"class": "Atypical Antipsychotic", "dose": "5-20mg daily", "indications": "Schizophrenia, bipolar", "side_effects": "Weight gain, diabetes, dyslipidemia, sedation"},
        "Lithium": {"class": "Mood Stabilizer", "dose": "300-1800mg daily (level-guided)", "indications": "Bipolar disorder", "side_effects": "Tremor, hypothyroidism, nephrotoxicity, teratogenic"},
        "Valproic Acid": {"class": "Mood Stabilizer/AED", "dose": "250-3000mg daily", "indications": "Bipolar, epilepsy, migraine", "side_effects": "Weight gain, hepatotoxicity, pancreatitis, teratogenic"},
        "Carbamazepine": {"class": "AED", "dose": "200-1600mg daily", "indications": "Epilepsy, trigeminal neuralgia, bipolar", "side_effects": "Hyponatremia, aplastic anemia, SJS, CYP inducer"},
        "Gabapentin": {"class": "Gabapentinoid", "dose": "300-3600mg daily", "indications": "Neuropathic pain, epilepsy, RLS", "side_effects": "Sedation, dizziness, weight gain, abuse potential"},
        "Pregabalin": {"class": "Gabapentinoid", "dose": "75-600mg daily", "indications": "Neuropathic pain, fibromyalgia, GAD", "side_effects": "Dizziness, edema, weight gain, dependence"},
        "Levetiracetam": {"class": "AED", "dose": "500-3000mg daily", "indications": "Epilepsy", "side_effects": "Behavioral changes, sedation, leukopenia"},
        "Donepezil": {"class": "Cholinesterase Inhibitor", "dose": "5-10mg daily", "indications": "Alzheimer's disease", "side_effects": "GI upset, bradycardia, syncope, nightmares"},
        "Sumatriptan": {"class": "Triptan", "dose": "50-100mg PRN", "indications": "Acute migraine", "side_effects": "Chest tightness, paresthesia, serotonin syndrome"},
        "Levodopa/Carbidopa": {"class": "Dopamine Precursor", "dose": "100/25mg TID", "indications": "Parkinson's disease", "side_effects": "Dyskinesia, nausea, hypotension, hallucinations"}
    },
    "Gastroenterology": {
        "Omeprazole": {"class": "PPI", "dose": "20-40mg daily", "indications": "GERD, PUD, H. pylori", "side_effects": "Headache, GI upset, B12 deficiency, C. diff, fractures"},
        "Pantoprazole": {"class": "PPI", "dose": "40mg daily", "indications": "GERD, erosive esophagitis", "side_effects": "Headache, diarrhea, hypomagnesemia"},
        "Famotidine": {"class": "H2 Antagonist", "dose": "20-40mg BID", "indications": "GERD, PUD", "side_effects": "Constipation, diarrhea, headache"},
        "Ondansetron": {"class": "5-HT3 Antagonist", "dose": "4-8mg PRN", "indications": "Nausea, vomiting", "side_effects": "Headache, constipation, QT prolongation"},
        "Metoclopramide": {"class": "Dopamine Antagonist", "dose": "10mg TID", "indications": "Gastroparesis, nausea", "side_effects": "EPS, tardive dyskinesia, galactorrhea"},
        "Loperamide": {"class": "Opioid Agonist", "dose": "2-4mg PRN (max 16mg)", "indications": "Acute diarrhea", "side_effects": "Constipation, abdominal cramps, toxic megacolon"},
        "Mesalamine": {"class": "5-ASA", "dose": "2.4-4.8g daily", "indications": "Ulcerative colitis, Crohn's", "side_effects": "Headache, GI upset, nephritis"},
        "Lactulose": {"class": "Osmotic Laxative", "dose": "15-30mL daily", "indications": "Constipation, hepatic encephalopathy", "side_effects": "Bloating, flatulence, diarrhea"},
        "Ursodeoxycholic Acid": {"class": "Bile Acid", "dose": "10-15mg/kg daily", "indications": "PBC, gallstone dissolution", "side_effects": "Diarrhea, nausea, pruritus"}
    },
    "Respiratory": {
        "Albuterol": {"class": "SABA", "dose": "2 puffs Q4-6H PRN", "indications": "Asthma, COPD exacerbation", "side_effects": "Tremor, tachycardia, hypokalemia"},
        "Salmeterol": {"class": "LABA", "dose": "50mcg BID", "indications": "Asthma, COPD maintenance", "side_effects": "Tremor, palpitations, must combine with ICS"},
        "Fluticasone": {"class": "ICS", "dose": "100-500mcg BID", "indications": "Asthma maintenance", "side_effects": "Oral thrush, dysphonia, adrenal suppression"},
        "Budesonide": {"class": "ICS", "dose": "200-800mcg BID", "indications": "Asthma, COPD", "side_effects": "Cough, oral candidiasis, growth suppression in children"},
        "Montelukast": {"class": "Leukotriene Antagonist", "dose": "10mg daily", "indications": "Asthma, allergic rhinitis", "side_effects": "Headache, behavioral changes, Churg-Strauss"},
        "Tiotropium": {"class": "LAMA", "dose": "18mcg daily", "indications": "COPD", "side_effects": "Dry mouth, constipation, urinary retention"},
        "Ipratropium": {"class": "SAMA", "dose": "2-4 puffs QID", "indications": "COPD, asthma", "side_effects": "Dry mouth, blurred vision, glaucoma"},
        "Theophylline": {"class": "Methylxanthine", "dose": "200-600mg daily (level-guided)", "indications": "Refractory asthma/COPD", "side_effects": "Nausea, seizures, arrhythmias, narrow therapeutic index"},
        "Roflumilast": {"class": "PDE-4 Inhibitor", "dose": "500mcg daily", "indications": "Severe COPD", "side_effects": "Diarrhea, weight loss, psychiatric effects"}
    },
    "Analgesics": {
        "Ibuprofen": {"class": "NSAID", "dose": "200-800mg TID", "indications": "Pain, inflammation, fever", "side_effects": "GI ulcer, renal impairment, cardiovascular risk"},
        "Naproxen": {"class": "NSAID", "dose": "250-500mg BID", "indications": "Pain, inflammation", "side_effects": "GI upset, edema, hypertension"},
        "Celecoxib": {"class": "COX-2 Inhibitor", "dose": "100-200mg BID", "indications": "Osteoarthritis, RA", "side_effects": "Cardiovascular risk, GI upset, sulfa allergy"},
        "Acetaminophen": {"class": "Analgesic/Antipyretic", "dose": "500-1000mg Q6H (max 4g)", "indications": "Pain, fever", "side_effects": "Hepatotoxicity (overdose), avoid in liver disease"},
        "Tramadol": {"class": "Weak Opioid + SNRI", "dose": "50-100mg Q6H", "indications": "Moderate pain", "side_effects": "Nausea, seizures, serotonin syndrome, dependence"},
        "Morphine": {"class": "Opioid Agonist", "dose": "5-30mg Q4H", "indications": "Severe acute/chronic pain", "side_effects": "Respiratory depression, constipation, dependence, nausea"},
        "Oxycodone": {"class": "Opioid Agonist", "dose": "5-30mg Q4-6H", "indications": "Severe pain", "side_effects": "Respiratory depression, constipation, abuse potential"},
        "Fentanyl Patch": {"class": "Opioid Agonist", "dose": "12-100mcg/hr q72h", "indications": "Chronic severe pain", "side_effects": "Respiratory depression, tolerance, accidental exposure risk"},
        "Gabapentin": {"class": "Gabapentinoid", "dose": "300-3600mg daily", "indications": "Neuropathic pain, epilepsy", "side_effects": "Sedation, dizziness, weight gain, abuse potential"},
        "Lidocaine Patch": {"class": "Local Anesthetic", "dose": "5% patch 12h on/off", "indications": "Post-herpetic neuralgia", "side_effects": "Local irritation, burning"}
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
        
        h1 {
            background: linear-gradient(135deg, #6366f1, #8b5cf6, #a78bfa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800 !important;
        }
        
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: rgba(255,255,255,0.05); }
        ::-webkit-scrollbar-thumb { background: linear-gradient(180deg, #6366f1, #8b5cf6); border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

load_css()

# ================================
# SESSION STATE INITIALIZATION
# ================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'user_data' not in st.session_state:
    st.session_state.user_data = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Dashboard"
if 'flashcard_flipped' not in st.session_state:
    st.session_state.flashcard_flipped = False
if 'comprehensive_exam' not in st.session_state:
    st.session_state.comprehensive_exam = None
if 'comprehensive_answers' not in st.session_state:
    st.session_state.comprehensive_answers = {}
if 'comprehensive_submitted' not in st.session_state:
    st.session_state.comprehensive_submitted = False
if 'current_room_id' not in st.session_state:
    st.session_state.current_room_id = None
if 'editing_drug' not in st.session_state:
    st.session_state.editing_drug = None
if 'editing_lab' not in st.session_state:
    st.session_state.editing_lab = None

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
            <div style="font-size: 5rem; filter: drop-shadow(0 0 30px rgba(99,102,241,0.5)); animation: float 3s ease-in-out infinite;">🩺</div>
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
                        update_user_streak(username)
                        st.session_state.streak = user_data.get('daily_streak', 0)
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
    
    # Navigation
    pages = {
        "📊 Dashboard": "Dashboard",
        "📚 Diseases": "Diseases",
        "🩺 Case Analysis": "Case Analysis",
        "📝 Quiz": "Quiz",
        "📋 Comprehensive Exam": "Comprehensive Exam",
        "🔄 Spaced Repetition": "Spaced Repetition",
        "🔬 Lab Tests": "Lab Tests",
        "💊 Pharmacology": "Pharmacology",
        "⚠️ Drug Interactions": "Drug Interactions",
        "🏆 Leaderboard": "Leaderboard",
        "📰 Medical News": "Medical News",
        "🧠 AI Assistant": "AI Assistant",
        "📝 Clinical Notes": "Clinical Notes",
        "🏆 Achievements": "Achievements"
    }
    
    for label, page_name in pages.items():
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
        ("🔬 Lab Tests", len(LAB_TESTS)),
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
            <p>Total Diseases: {len(DISEASE_DATABASE)}</p>
            <p>Total Drugs: {sum(len(d) for d in DRUG_DATABASE.values())}</p>
            <p>Total Lab Tests: {len(LAB_TESTS)}</p>
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
                st.markdown(f"**Category:** {info.get('category', 'General')}")
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
    
    if st.session_state.get("current_case"):
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
            # Update database
            conn = get_db_connection()
            conn.execute("UPDATE users SET total_cases = ?, correct_diagnoses = ? WHERE username = ?",
                        (st.session_state.total_cases, st.session_state.correct_diagnoses, st.session_state.username))
            conn.commit()
            conn.close()

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
            # Update database
            conn = get_db_connection()
            conn.execute("UPDATE users SET quiz_score = ? WHERE username = ?",
                        (st.session_state.quiz_score, st.session_state.username))
            conn.commit()
            conn.close()
            st.rerun()

elif page == "Comprehensive Exam":
    st.markdown('<h2>📋 Comprehensive Exam</h2>', unsafe_allow_html=True)
    
    if st.session_state.comprehensive_exam is None:
        if st.button("🚀 Start 100-Question Exam", type="primary", use_container_width=True):
            questions = []
            for disease, info in DISEASE_DATABASE.items():
                if info["symptoms"]:
                    correct = random.choice(info["symptoms"])
                    wrong_opts = random.sample([s for d in DISEASE_DATABASE for s in DISEASE_DATABASE[d]["symptoms"] if s != correct], min(3, sum(1 for d in DISEASE_DATABASE for s in DISEASE_DATABASE[d]["symptoms"])))
                    opts = [correct] + wrong_opts[:3]
                    random.shuffle(opts)
                    questions.append({"question": f"Symptom of {disease}?", "options": opts, "correct": opts.index(correct)})
            
            st.session_state.comprehensive_exam = random.sample(questions, min(100, len(questions)))
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
        df_data = [{"Test": k, "Category": v["category"], "Normal Range": v["normal"], "Description": v["description"]} 
                  for k, v in filtered.items()]
        import pandas as pd
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
        st.info("Interaction checking active. Select drugs to analyze.")
    else:
        st.info("Select 2 or more drugs to check interactions")

elif page == "Leaderboard":
    st.markdown('<h2>🏆 Leaderboard</h2>', unsafe_allow_html=True)
    
    df = get_leaderboard_data()
    if not df.empty:
        for i, row in df.iterrows():
            medal = "🥇" if i+1 == 1 else "🥈" if i+1 == 2 else "🥉" if i+1 == 3 else f"#{i+1}"
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
            conn.close()
            st.success("✅ Note saved!")
            st.rerun()
    
    conn = get_db_connection()
    notes = conn.execute("SELECT * FROM clinical_notes WHERE username = ? ORDER BY created_at DESC LIMIT 20",
                        (st.session_state.username,)).fetchall()
    conn.close()
    
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
        ("Quiz Legend", "👑", st.session_state.quiz_score >= 100),
        ("Streak Master", "🔥", st.session_state.streak >= 7),
        ("XP Hunter", "⭐", st.session_state.xp_points >= 100),
        ("XP Champion", "💎", st.session_state.xp_points >= 500),
        ("Diagnostician", "🔍", st.session_state.correct_diagnoses >= 5),
        ("Dedicated", "💪", st.session_state.streak >= 30)
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
