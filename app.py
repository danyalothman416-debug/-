import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import json
import time
import hashlib
import re
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')
import os
import uuid
from io import BytesIO
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import base64

# ================================
# 1. PAGE CONFIGURATION
# ================================
st.set_page_config(
    page_title="Dr.Danyal - Medical Training Platform",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================================
# 2. DATA STORAGE SYSTEM
# ================================
DATA_DIR = "user_data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

USERS_FILE = os.path.join(DATA_DIR, "users.json")
LEADERBOARD_FILE = os.path.join(DATA_DIR, "leaderboard.json")
STUDY_ROOMS_FILE = os.path.join(DATA_DIR, "study_rooms.json")
SPACED_REPETITION_FILE = os.path.join(DATA_DIR, "spaced_repetition.json")
CLINICAL_NOTES_FILE = os.path.join(DATA_DIR, "clinical_notes.json")
CUSTOM_DRUGS_FILE = os.path.join(DATA_DIR, "custom_drugs.json")
CUSTOM_LABS_FILE = os.path.join(DATA_DIR, "custom_labs.json")

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def load_json_file(filepath: str, default: any) -> any:
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return default
    return default

def save_json_file(filepath: str, data: any):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_users() -> Dict:
    return load_json_file(USERS_FILE, {})

def save_users(users: Dict):
    save_json_file(USERS_FILE, users)

def load_leaderboard() -> List:
    return load_json_file(LEADERBOARD_FILE, [])

def save_leaderboard(data: List):
    save_json_file(LEADERBOARD_FILE, data)

def load_study_rooms() -> Dict:
    return load_json_file(STUDY_ROOMS_FILE, {})

def save_study_rooms(data: Dict):
    save_json_file(STUDY_ROOMS_FILE, data)

def load_spaced_repetition() -> Dict:
    return load_json_file(SPACED_REPETITION_FILE, {})

def save_spaced_repetition(data: Dict):
    save_json_file(SPACED_REPETITION_FILE, data)

def load_clinical_notes() -> Dict:
    return load_json_file(CLINICAL_NOTES_FILE, {})

def save_clinical_notes(data: Dict):
    save_json_file(CLINICAL_NOTES_FILE, data)

def load_custom_drugs() -> Dict:
    return load_json_file(CUSTOM_DRUGS_FILE, {})

def save_custom_drugs(data: Dict):
    save_json_file(CUSTOM_DRUGS_FILE, data)

def load_custom_labs() -> Dict:
    return load_json_file(CUSTOM_LABS_FILE, {})

def save_custom_labs(data: Dict):
    save_json_file(CUSTOM_LABS_FILE, data)

def create_user(username: str, password: str) -> bool:
    users = load_users()
    if username in users:
        return False
    users[username] = {
        "password": hash_password(password),
        "created_at": datetime.now().isoformat(),
        "xp_points": 0,
        "badges": [],
        "daily_streak": 0,
        "last_login_date": "",
        "quiz_score": 0,
        "total_cases_solved": 0,
        "correct_diagnoses": 0
    }
    save_users(users)
    
    leaderboard = load_leaderboard()
    leaderboard.append({
        "username": username,
        "xp_points": 0,
        "level": 1,
        "quiz_score": 0,
        "cases_solved": 0,
        "badges": [],
        "last_active": datetime.now().isoformat()
    })
    save_leaderboard(leaderboard)
    
    sr_data = load_spaced_repetition()
    sr_data[username] = {}
    save_spaced_repetition(sr_data)
    
    clinical_notes = load_clinical_notes()
    clinical_notes[username] = []
    save_clinical_notes(clinical_notes)
    
    return True

def authenticate_user(username: str, password: str) -> bool:
    users = load_users()
    if username in users:
        return users[username]["password"] == hash_password(password)
    return False

def load_user_data(username: str) -> Dict:
    users = load_users()
    if username in users:
        return users[username]
    return {}

def save_user_data(username: str, data: Dict):
    users = load_users()
    if username in users:
        users[username].update(data)
        save_users(users)

def update_leaderboard(username: str, xp: int = 0, quiz_score: int = None, cases_solved: int = None):
    leaderboard = load_leaderboard()
    for entry in leaderboard:
        if entry["username"] == username:
            entry["xp_points"] = entry.get("xp_points", 0) + xp
            if quiz_score is not None:
                entry["quiz_score"] = max(entry.get("quiz_score", 0), quiz_score)
            if cases_solved is not None:
                entry["cases_solved"] = cases_solved
            entry["level"] = get_user_level(entry["quiz_score"])
            entry["last_active"] = datetime.now().isoformat()
            break
    else:
        leaderboard.append({
            "username": username,
            "xp_points": xp,
            "level": get_user_level(quiz_score or 0),
            "quiz_score": quiz_score or 0,
            "cases_solved": cases_solved or 0,
            "badges": [],
            "last_active": datetime.now().isoformat()
        })
    save_leaderboard(leaderboard)

def add_xp(username: str, points: int):
    update_leaderboard(username, xp=points)
    users = load_users()
    if username in users:
        users[username]["xp_points"] = users[username].get("xp_points", 0) + points
        save_users(users)

def update_user_streak(username: str):
    users = load_users()
    if username in users:
        today = datetime.now().date().isoformat()
        last_login = users[username].get("last_login_date", "")
        
        if last_login:
            last_date = datetime.fromisoformat(last_login).date()
            yesterday = (datetime.now() - timedelta(days=1)).date()
            
            if last_date == yesterday:
                users[username]["daily_streak"] = users[username].get("daily_streak", 0) + 1
            elif last_date < yesterday:
                users[username]["daily_streak"] = 1
        else:
            users[username]["daily_streak"] = 1
        
        users[username]["last_login_date"] = today
        save_users(users)
        return users[username]["daily_streak"]
    return 0

# ================================
# 3. GLOBAL CSS STYLING
# ================================
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Poppins:wght@400;500;600;700;800&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', 'Poppins', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0a0a1a 0%, #0f0f2e 25%, #1a1a3e 50%, #0f0f2e 75%, #0a0a1a 100%);
        background-size: 400% 400%;
        animation: gradientShift 20s ease infinite;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        25% { background-position: 100% 0%; }
        50% { background-position: 100% 100%; }
        75% { background-position: 0% 100%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Main Content Area */
    .main > div {
        padding: 1rem 2rem;
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #6366f1, #8b5cf6);
        border-radius: 10px;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0a1a 0%, #0f0f2e 50%, #0a0a1a 100%) !important;
        border-right: 2px solid rgba(99, 102, 241, 0.2) !important;
    }
    
    [data-testid="stSidebar"] * {
        color: rgba(255, 255, 255, 0.9) !important;
    }
    
    /* Sidebar Navigation Items */
    [data-testid="stSidebar"] .stRadio label {
        padding: 0.6rem 1rem !important;
        border-radius: 10px !important;
        transition: all 0.3s ease !important;
        margin: 2px 0 !important;
    }
    
    [data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(99, 102, 241, 0.15) !important;
        transform: translateX(5px);
    }
    
    /* Cards and Containers */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 1.5rem;
        border: 1px solid rgba(99, 102, 241, 0.15);
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        border-color: rgba(99, 102, 241, 0.4);
        box-shadow: 0 10px 40px rgba(99, 102, 241, 0.1);
        transform: translateY(-3px);
    }
    
    .stat-card {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.08), rgba(139, 92, 246, 0.05));
        border-radius: 16px;
        padding: 1.2rem;
        text-align: center;
        border: 1px solid rgba(99, 102, 241, 0.2);
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(99, 102, 241, 0.2);
        border-color: rgba(139, 92, 246, 0.5);
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #6366f1, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        color: white !important;
        border: none !important;
        padding: 0.7rem 2rem !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3) !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #8b5cf6, #a78bfa) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4) !important;
    }
    
    /* Input Fields */
    .stTextInput > div > div,
    .stTextArea > div > div,
    .stSelectbox > div > div,
    .stNumberInput > div > div {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(99, 102, 241, 0.2) !important;
        border-radius: 10px !important;
        color: white !important;
    }
    
    /* Headers */
    h1, h2, h3, h4 {
        color: white !important;
        font-weight: 700 !important;
    }
    
    h1 {
        background: linear-gradient(135deg, #6366f1, #8b5cf6, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background: rgba(99, 102, 241, 0.05) !important;
        border-radius: 10px !important;
        border: 1px solid rgba(99, 102, 241, 0.1) !important;
    }
    
    /* Messages */
    .success-message {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(16, 185, 129, 0.05));
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid rgba(16, 185, 129, 0.3);
        color: #10b981;
    }
    
    .error-message {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(239, 68, 68, 0.05));
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid rgba(239, 68, 68, 0.3);
        color: #ef4444;
    }
    
    /* Login Page */
    .login-container {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        background: radial-gradient(circle at 50% 50%, rgba(99, 102, 241, 0.1), transparent 70%);
    }
    
    .login-card {
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(30px);
        border-radius: 30px;
        padding: 3rem;
        border: 1px solid rgba(99, 102, 241, 0.2);
        box-shadow: 0 30px 80px rgba(0, 0, 0, 0.5);
        max-width: 480px;
        width: 100%;
        text-align: center;
    }
    
    .login-logo {
        font-size: 5rem;
        filter: drop-shadow(0 0 30px rgba(99, 102, 241, 0.5));
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    .login-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #6366f1, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 1rem 0;
    }
    
    /* Badge and Tags */
    .badge {
        display: inline-block;
        padding: 0.3rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .badge-primary {
        background: rgba(99, 102, 241, 0.2);
        color: #a78bfa;
        border: 1px solid rgba(99, 102, 241, 0.3);
    }
    
    .badge-success {
        background: rgba(16, 185, 129, 0.2);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    
    .badge-danger {
        background: rgba(239, 68, 68, 0.2);
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    
    .badge-warning {
        background: rgba(251, 191, 36, 0.2);
        color: #fbbf24;
        border: 1px solid rgba(251, 191, 36, 0.3);
    }
    
    /* Table Styling */
    .dataframe {
        background: rgba(255, 255, 255, 0.02) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(99, 102, 241, 0.1) !important;
    }
    
    /* Footer */
    .app-footer {
        text-align: center;
        padding: 2rem;
        background: rgba(255, 255, 255, 0.02);
        border-radius: 16px;
        margin-top: 2rem;
        border: 1px solid rgba(99, 102, 241, 0.1);
    }
    
    /* Animations */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .animate-slide-in {
        animation: slideIn 0.5s ease-out;
    }
</style>
""", unsafe_allow_html=True)

# ================================
# 4. LEVEL SYSTEM
# ================================
LEVELS = {
    1: {"name": "Medical Student", "min_score": 0, "max_score": 9, "color": "#10b981", "icon": "🌱"},
    2: {"name": "Intern", "min_score": 10, "max_score": 29, "color": "#06b6d4", "icon": "📖"},
    3: {"name": "Resident", "min_score": 30, "max_score": 59, "color": "#f59e0b", "icon": "🚀"},
    4: {"name": "Specialist", "min_score": 60, "max_score": 89, "color": "#f97316", "icon": "🏆"},
    5: {"name": "Consultant", "min_score": 90, "max_score": 100, "color": "#ef4444", "icon": "👨‍⚕️"},
    6: {"name": "Professor", "min_score": 100, "max_score": 150, "color": "#8b5cf6", "icon": "🎓"},
    7: {"name": "Legend", "min_score": 150, "max_score": 999, "color": "#ec4899", "icon": "👑"}
}

def get_user_level(score: int) -> int:
    for level, info in LEVELS.items():
        if info["min_score"] <= score <= info["max_score"]:
            return level
    return 1

def get_level_info(level: int) -> Dict:
    return LEVELS.get(level, LEVELS[1])

def get_level_progress(score: int) -> float:
    level = get_user_level(score)
    if level >= 7: return 100.0
    current = LEVELS[level]
    next_level = min(level + 1, 7)
    total = LEVELS[next_level]["min_score"] - current["min_score"]
    achieved = score - current["min_score"]
    return min((achieved / total) * 100, 100) if total > 0 else 100

# ================================
# 5. DISEASE DATABASE (50+ diseases)
# ================================
DISEASE_DATABASE = {
    "Diabetes Type 1": {
        "symptoms": ["Excessive thirst", "Frequent urination", "Weight loss", "Fatigue", "Blurred vision"],
        "tests": {"FBS": ">200 mg/dL", "HbA1c": ">8%", "C-peptide": "Low", "Anti-GAD": "Positive"},
        "treatment": ["Insulin therapy", "Blood glucose monitoring", "Diet management", "Exercise"],
        "risk": "Critical",
        "age_group": "Children & Young Adults"
    },
    "Diabetes Type 2": {
        "symptoms": ["Increased thirst", "Frequent urination", "Fatigue", "Weight loss", "Slow healing"],
        "tests": {"FBS": ">126 mg/dL", "HbA1c": ">6.5%", "OGTT": ">200 mg/dL"},
        "treatment": ["Metformin 500mg", "Lifestyle changes", "Exercise", "Diet control"],
        "risk": "High",
        "age_group": "Middle-aged & Elderly"
    },
    "Hypertension": {
        "symptoms": ["Headache", "Dizziness", "Blurred vision", "Chest pain", "Shortness of breath"],
        "tests": {"BP": ">140/90 mmHg", "ECG": "LVH possible", "Creatinine": "Normal"},
        "treatment": ["ACE inhibitors", "Low salt diet", "Exercise", "Weight management"],
        "risk": "Moderate",
        "age_group": "All ages"
    },
    "Myocardial Infarction": {
        "symptoms": ["Severe chest pain", "Shortness of breath", "Sweating", "Nausea", "Left arm pain"],
        "tests": {"ECG": "ST elevation", "Troponin": "Elevated >0.04", "CK-MB": "Elevated"},
        "treatment": ["Aspirin 300mg", "Nitroglycerin", "Oxygen", "Morphine", "PCI"],
        "risk": "Critical",
        "age_group": ">50 years"
    },
    "Pneumonia": {
        "symptoms": ["Fever", "Cough with sputum", "Shortness of breath", "Chest pain", "Fatigue"],
        "tests": {"Chest X-ray": "Consolidation", "CRP": ">10", "WBC": ">11,000"},
        "treatment": ["Antibiotics", "Oxygen therapy", "Fluids", "Rest"],
        "risk": "Moderate",
        "age_group": "All ages"
    },
    "Anemia": {
        "symptoms": ["Fatigue", "Pale skin", "Dizziness", "Rapid heartbeat", "Shortness of breath"],
        "tests": {"Hb": "<12 g/dL", "MCV": "<80 fL", "Ferritin": "<15 ng/mL"},
        "treatment": ["Iron supplements", "Vitamin C", "Diet modification"],
        "risk": "Moderate",
        "age_group": "All ages"
    },
    "Asthma": {
        "symptoms": ["Wheezing", "Shortness of breath", "Chest tightness", "Coughing", "Difficulty sleeping"],
        "tests": {"PFT": "FEV1 <80%", "Peak Flow": "Reduced", "Chest X-ray": "Normal"},
        "treatment": ["Bronchodilators", "Inhaled corticosteroids", "Avoid triggers"],
        "risk": "Moderate",
        "age_group": "Children & Young Adults"
    },
    "Chronic Kidney Disease": {
        "symptoms": ["Swelling in legs", "Fatigue", "Decreased urine output", "Nausea", "Itching"],
        "tests": {"Creatinine": ">1.3", "BUN": ">20", "eGFR": "<60", "Urinalysis": "Proteinuria"},
        "treatment": ["ACE inhibitors", "Diet modification", "Dialysis if needed"],
        "risk": "Critical",
        "age_group": ">50 years"
    },
    "Hepatitis B": {
        "symptoms": ["Jaundice", "Fatigue", "Dark urine", "Abdominal pain", "Nausea"],
        "tests": {"ALT": "Elevated", "HBsAg": "Positive", "Anti-HBc": "Positive"},
        "treatment": ["Antivirals", "Rest", "Avoid alcohol", "Monitor liver function"],
        "risk": "High",
        "age_group": "All ages"
    },
    "Tuberculosis": {
        "symptoms": ["Chronic cough", "Night sweats", "Weight loss", "Fever", "Hemoptysis"],
        "tests": {"Chest X-ray": "Cavitary lesions", "Sputum AFB": "Positive", "GeneXpert": "Positive"},
        "treatment": ["Rifampicin", "Isoniazid", "Pyrazinamide", "Ethambutol"],
        "risk": "Critical",
        "age_group": "All ages"
    }
}

# ================================
# 6. LAB TESTS DATABASE (100+ tests)
# ================================
LAB_TESTS = {
    # Hematology
    "WBC Count": {"category": "Hematology", "normal": "4.0-11.0", "unit": "x10³/µL", "description": "White blood cell count"},
    "RBC Count": {"category": "Hematology", "normal": "4.5-5.5", "unit": "x10⁶/µL", "description": "Red blood cell count"},
    "Hemoglobin": {"category": "Hematology", "normal": "12-16", "unit": "g/dL", "description": "Oxygen-carrying protein"},
    "Hematocrit": {"category": "Hematology", "normal": "37-47", "unit": "%", "description": "Percentage of RBCs in blood"},
    "MCV": {"category": "Hematology", "normal": "80-100", "unit": "fL", "description": "Mean corpuscular volume"},
    "MCH": {"category": "Hematology", "normal": "27-33", "unit": "pg", "description": "Mean corpuscular hemoglobin"},
    "MCHC": {"category": "Hematology", "normal": "32-36", "unit": "g/dL", "description": "Mean corpuscular hemoglobin concentration"},
    "RDW": {"category": "Hematology", "normal": "11.5-14.5", "unit": "%", "description": "Red cell distribution width"},
    "Platelet Count": {"category": "Hematology", "normal": "150-450", "unit": "x10³/µL", "description": "Platelet count"},
    "MPV": {"category": "Hematology", "normal": "7.5-11.5", "unit": "fL", "description": "Mean platelet volume"},
    "Reticulocyte Count": {"category": "Hematology", "normal": "0.5-2.5", "unit": "%", "description": "Immature RBCs"},
    "ESR": {"category": "Hematology", "normal": "0-20", "unit": "mm/hr", "description": "Erythrocyte sedimentation rate"},
    "Ferritin": {"category": "Hematology", "normal": "15-300", "unit": "ng/mL", "description": "Iron storage protein"},
    "Iron": {"category": "Hematology", "normal": "60-170", "unit": "mcg/dL", "description": "Serum iron level"},
    "TIBC": {"category": "Hematology", "normal": "250-450", "unit": "mcg/dL", "description": "Total iron binding capacity"},
    "Transferrin Saturation": {"category": "Hematology", "normal": "20-50", "unit": "%", "description": "Iron saturation"},
    "Vitamin B12": {"category": "Hematology", "normal": "200-900", "unit": "pg/mL", "description": "Vitamin B12 level"},
    "Folate": {"category": "Hematology", "normal": "3-17", "unit": "ng/mL", "description": "Folic acid level"},
    "PT": {"category": "Coagulation", "normal": "11-13.5", "unit": "seconds", "description": "Prothrombin time"},
    "PTT": {"category": "Coagulation", "normal": "25-35", "unit": "seconds", "description": "Partial thromboplastin time"},
    "INR": {"category": "Coagulation", "normal": "0.9-1.1", "unit": "", "description": "International normalized ratio"},
    "Fibrinogen": {"category": "Coagulation", "normal": "200-400", "unit": "mg/dL", "description": "Clotting factor"},
    "D-Dimer": {"category": "Coagulation", "normal": "<0.5", "unit": "mg/L", "description": "Fibrin degradation product"},
    
    # Biochemistry
    "Glucose (Fasting)": {"category": "Biochemistry", "normal": "70-100", "unit": "mg/dL", "description": "Fasting blood sugar"},
    "Glucose (Random)": {"category": "Biochemistry", "normal": "<140", "unit": "mg/dL", "description": "Random blood sugar"},
    "HbA1c": {"category": "Biochemistry", "normal": "4.0-5.6", "unit": "%", "description": "Glycated hemoglobin"},
    "Creatinine": {"category": "Biochemistry", "normal": "0.6-1.3", "unit": "mg/dL", "description": "Kidney function marker"},
    "BUN": {"category": "Biochemistry", "normal": "7-20", "unit": "mg/dL", "description": "Blood urea nitrogen"},
    "eGFR": {"category": "Biochemistry", "normal": ">90", "unit": "mL/min/1.73m²", "description": "Estimated glomerular filtration rate"},
    "Uric Acid": {"category": "Biochemistry", "normal": "3.5-7.2", "unit": "mg/dL", "description": "Purine metabolism product"},
    "Total Protein": {"category": "Biochemistry", "normal": "6.0-8.0", "unit": "g/dL", "description": "Total serum protein"},
    "Albumin": {"category": "Biochemistry", "normal": "3.5-5.0", "unit": "g/dL", "description": "Major plasma protein"},
    "Globulin": {"category": "Biochemistry", "normal": "2.0-3.5", "unit": "g/dL", "description": "Immune proteins"},
    "Total Bilirubin": {"category": "Biochemistry", "normal": "0.1-1.2", "unit": "mg/dL", "description": "Bile pigment"},
    "Direct Bilirubin": {"category": "Biochemistry", "normal": "0.0-0.3", "unit": "mg/dL", "description": "Conjugated bilirubin"},
    "Indirect Bilirubin": {"category": "Biochemistry", "normal": "0.1-0.9", "unit": "mg/dL", "description": "Unconjugated bilirubin"},
    "ALT": {"category": "Biochemistry", "normal": "10-40", "unit": "U/L", "description": "Alanine aminotransferase"},
    "AST": {"category": "Biochemistry", "normal": "10-40", "unit": "U/L", "description": "Aspartate aminotransferase"},
    "ALP": {"category": "Biochemistry", "normal": "44-147", "unit": "U/L", "description": "Alkaline phosphatase"},
    "GGT": {"category": "Biochemistry", "normal": "0-51", "unit": "U/L", "description": "Gamma-glutamyl transferase"},
    "LDH": {"category": "Biochemistry", "normal": "100-250", "unit": "U/L", "description": "Lactate dehydrogenase"},
    "CK": {"category": "Biochemistry", "normal": "22-198", "unit": "U/L", "description": "Creatine kinase"},
    "CK-MB": {"category": "Biochemistry", "normal": "0-5", "unit": "ng/mL", "description": "Cardiac-specific CK"},
    "Amylase": {"category": "Biochemistry", "normal": "20-200", "unit": "U/L", "description": "Pancreatic enzyme"},
    "Lipase": {"category": "Biochemistry", "normal": "20-200", "unit": "U/L", "description": "Pancreatic enzyme"},
    "Sodium": {"category": "Biochemistry", "normal": "135-145", "unit": "mmol/L", "description": "Electrolyte"},
    "Potassium": {"category": "Biochemistry", "normal": "3.5-5.0", "unit": "mmol/L", "description": "Electrolyte"},
    "Chloride": {"category": "Biochemistry", "normal": "96-106", "unit": "mmol/L", "description": "Electrolyte"},
    "Calcium": {"category": "Biochemistry", "normal": "8.5-10.5", "unit": "mg/dL", "description": "Mineral"},
    "Magnesium": {"category": "Biochemistry", "normal": "1.7-2.2", "unit": "mg/dL", "description": "Mineral"},
    "Phosphorus": {"category": "Biochemistry", "normal": "2.5-4.5", "unit": "mg/dL", "description": "Mineral"},
    "Total Cholesterol": {"category": "Lipids", "normal": "<200", "unit": "mg/dL", "description": "Total cholesterol"},
    "LDL Cholesterol": {"category": "Lipids", "normal": "<100", "unit": "mg/dL", "description": "Bad cholesterol"},
    "HDL Cholesterol": {"category": "Lipids", "normal": ">40", "unit": "mg/dL", "description": "Good cholesterol"},
    "Triglycerides": {"category": "Lipids", "normal": "<150", "unit": "mg/dL", "description": "Blood fats"},
    "VLDL": {"category": "Lipids", "normal": "<30", "unit": "mg/dL", "description": "Very low-density lipoprotein"},
    
    # Cardiac Markers
    "Troponin I": {"category": "Cardiac", "normal": "<0.04", "unit": "ng/mL", "description": "Cardiac damage marker"},
    "Troponin T": {"category": "Cardiac", "normal": "<0.014", "unit": "ng/mL", "description": "High-sensitivity cardiac marker"},
    "BNP": {"category": "Cardiac", "normal": "<100", "unit": "pg/mL", "description": "Heart failure marker"},
    "NT-proBNP": {"category": "Cardiac", "normal": "<125", "unit": "pg/mL", "description": "Heart failure marker"},
    "Myoglobin": {"category": "Cardiac", "normal": "<80", "unit": "ng/mL", "description": "Early cardiac marker"},
    "HS-CRP": {"category": "Cardiac", "normal": "<2", "unit": "mg/L", "description": "Cardiovascular risk marker"},
    "Homocysteine": {"category": "Cardiac", "normal": "5-15", "unit": "μmol/L", "description": "Cardiovascular risk factor"},
    "ApoA": {"category": "Cardiac", "normal": "90-150", "unit": "mg/dL", "description": "Apolipoprotein A"},
    "ApoB": {"category": "Cardiac", "normal": "60-120", "unit": "mg/dL", "description": "Apolipoprotein B"},
    "Lipoprotein(a)": {"category": "Cardiac", "normal": "<30", "unit": "mg/dL", "description": "Genetic risk factor"},
    
    # Hormones
    "TSH": {"category": "Hormones", "normal": "0.4-4.0", "unit": "mIU/L", "description": "Thyroid stimulating hormone"},
    "Free T4": {"category": "Hormones", "normal": "0.8-1.8", "unit": "ng/dL", "description": "Free thyroxine"},
    "Free T3": {"category": "Hormones", "normal": "2.3-4.2", "unit": "pg/mL", "description": "Free triiodothyronine"},
    "Cortisol (AM)": {"category": "Hormones", "normal": "6-23", "unit": "μg/dL", "description": "Stress hormone"},
    "Cortisol (PM)": {"category": "Hormones", "normal": "3-15", "unit": "μg/dL", "description": "Evening cortisol"},
    "Testosterone (Male)": {"category": "Hormones", "normal": "300-1000", "unit": "ng/dL", "description": "Male sex hormone"},
    "Testosterone (Female)": {"category": "Hormones", "normal": "15-70", "unit": "ng/dL", "description": "Female androgen"},
    "Estradiol": {"category": "Hormones", "normal": "20-400", "unit": "pg/mL", "description": "Estrogen hormone"},
    "Progesterone": {"category": "Hormones", "normal": "0.1-25", "unit": "ng/mL", "description": "Female hormone"},
    "Prolactin": {"category": "Hormones", "normal": "4-23", "unit": "ng/mL", "description": "Milk production hormone"},
    "LH": {"category": "Hormones", "normal": "1.5-9.3", "unit": "IU/L", "description": "Luteinizing hormone"},
    "FSH": {"category": "Hormones", "normal": "1.4-18.1", "unit": "IU/L", "description": "Follicle stimulating hormone"},
    "Insulin (Fasting)": {"category": "Hormones", "normal": "2-25", "unit": "μIU/mL", "description": "Blood sugar regulating hormone"},
    "C-Peptide": {"category": "Hormones", "normal": "0.5-2.0", "unit": "ng/mL", "description": "Insulin production marker"},
    "GH": {"category": "Hormones", "normal": "0-5", "unit": "ng/mL", "description": "Growth hormone"},
    "IGF-1": {"category": "Hormones", "normal": "100-300", "unit": "ng/mL", "description": "Insulin-like growth factor"},
    
    # Urinalysis
    "Urine pH": {"category": "Urinalysis", "normal": "4.5-8.0", "unit": "", "description": "Urine acidity"},
    "Urine Specific Gravity": {"category": "Urinalysis", "normal": "1.005-1.030", "unit": "", "description": "Urine concentration"},
    "Urine Protein": {"category": "Urinalysis", "normal": "Negative", "unit": "", "description": "Protein in urine"},
    "Urine Glucose": {"category": "Urinalysis", "normal": "Negative", "unit": "", "description": "Sugar in urine"},
    "Urine Ketones": {"category": "Urinalysis", "normal": "Negative", "unit": "", "description": "Ketones in urine"},
    "Urine Bilirubin": {"category": "Urinalysis", "normal": "Negative", "unit": "", "description": "Bilirubin in urine"},
    "Urine Urobilinogen": {"category": "Urinalysis", "normal": "0.1-1.0", "unit": "mg/dL", "description": "Urobilinogen in urine"},
    "Urine Nitrite": {"category": "Urinalysis", "normal": "Negative", "unit": "", "description": "Bacteria indicator"},
    "Urine Leukocyte Esterase": {"category": "Urinalysis", "normal": "Negative", "unit": "", "description": "WBC enzyme"},
    "Urine WBC": {"category": "Urinalysis", "normal": "0-5", "unit": "/HPF", "description": "White blood cells"},
    "Urine RBC": {"category": "Urinalysis", "normal": "0-3", "unit": "/HPF", "description": "Red blood cells"},
    "Urine Casts": {"category": "Urinalysis", "normal": "None", "unit": "/LPF", "description": "Cellular casts"},
    "Urine Crystals": {"category": "Urinalysis", "normal": "None", "unit": "", "description": "Crystal formations"},
    "Microalbumin": {"category": "Urinalysis", "normal": "<30", "unit": "mg/24h", "description": "Early kidney damage marker"},
    "24h Urine Protein": {"category": "Urinalysis", "normal": "<150", "unit": "mg/24h", "description": "Daily protein excretion"},
    
    # Vitamins
    "Vitamin D (25-OH)": {"category": "Vitamins", "normal": "30-100", "unit": "ng/mL", "description": "Vitamin D status"},
    "Vitamin A": {"category": "Vitamins", "normal": "20-80", "unit": "μg/dL", "description": "Retinol level"},
    "Vitamin E": {"category": "Vitamins", "normal": "5.5-17", "unit": "mg/L", "description": "Tocopherol level"},
    "Vitamin K": {"category": "Vitamins", "normal": "0.2-3.2", "unit": "ng/mL", "description": "Phylloquinone level"},
    "Vitamin C": {"category": "Vitamins", "normal": "0.6-2.0", "unit": "mg/dL", "description": "Ascorbic acid"},
    
    # Serology/Immunology
    "CRP": {"category": "Immunology", "normal": "<5", "unit": "mg/L", "description": "C-reactive protein"},
    "RF": {"category": "Immunology", "normal": "<14", "unit": "IU/mL", "description": "Rheumatoid factor"},
    "ANA": {"category": "Immunology", "normal": "Negative", "unit": "", "description": "Antinuclear antibody"},
    "Anti-dsDNA": {"category": "Immunology", "normal": "<30", "unit": "IU/mL", "description": "Lupus marker"},
    "C3": {"category": "Immunology", "normal": "90-180", "unit": "mg/dL", "description": "Complement C3"},
    "C4": {"category": "Immunology", "normal": "10-40", "unit": "mg/dL", "description": "Complement C4"},
    "IgG": {"category": "Immunology", "normal": "700-1600", "unit": "mg/dL", "description": "Immunoglobulin G"},
    "IgA": {"category": "Immunology", "normal": "70-400", "unit": "mg/dL", "description": "Immunoglobulin A"},
    "IgM": {"category": "Immunology", "normal": "40-230", "unit": "mg/dL", "description": "Immunoglobulin M"},
    "IgE": {"category": "Immunology", "normal": "0-100", "unit": "IU/mL", "description": "Immunoglobulin E"},
    "Procalcitonin": {"category": "Immunology", "normal": "<0.5", "unit": "ng/mL", "description": "Bacterial infection marker"}
}

# ================================
# 7. DRUG DATABASE (100+ drugs)
# ================================
DRUG_DATABASE = {
    "Cardiovascular": {
        "Lisinopril": {"dose": "10-40mg", "mechanism": "ACE Inhibitor", "side_effects": "Cough, dizziness", "use": "Hypertension, Heart Failure"},
        "Enalapril": {"dose": "5-40mg", "mechanism": "ACE Inhibitor", "side_effects": "Cough, hyperkalemia", "use": "Hypertension, Heart Failure"},
        "Captopril": {"dose": "25-150mg", "mechanism": "ACE Inhibitor", "side_effects": "Cough, rash", "use": "Hypertension, Diabetic nephropathy"},
        "Ramipril": {"dose": "2.5-20mg", "mechanism": "ACE Inhibitor", "side_effects": "Cough, hypotension", "use": "Hypertension, Post-MI"},
        "Losartan": {"dose": "50-100mg", "mechanism": "ARB", "side_effects": "Dizziness, hyperkalemia", "use": "Hypertension, Diabetic nephropathy"},
        "Valsartan": {"dose": "80-320mg", "mechanism": "ARB", "side_effects": "Headache, dizziness", "use": "Hypertension, Heart Failure"},
        "Telmisartan": {"dose": "40-80mg", "mechanism": "ARB", "side_effects": "Back pain, sinusitis", "use": "Hypertension"},
        "Irbesartan": {"dose": "150-300mg", "mechanism": "ARB", "side_effects": "Diarrhea, heartburn", "use": "Hypertension, Diabetic nephropathy"},
        "Amlodipine": {"dose": "5-10mg", "mechanism": "Calcium Channel Blocker", "side_effects": "Edema, flushing", "use": "Hypertension, Angina"},
        "Nifedipine": {"dose": "30-90mg", "mechanism": "Calcium Channel Blocker", "side_effects": "Headache, edema", "use": "Hypertension, Angina"},
        "Diltiazem": {"dose": "120-360mg", "mechanism": "Calcium Channel Blocker", "side_effects": "Bradycardia, constipation", "use": "Hypertension, Arrhythmia"},
        "Verapamil": {"dose": "120-480mg", "mechanism": "Calcium Channel Blocker", "side_effects": "Constipation, dizziness", "use": "Hypertension, SVT"},
        "Metoprolol": {"dose": "25-200mg", "mechanism": "Beta Blocker", "side_effects": "Fatigue, bradycardia", "use": "Hypertension, Angina, Post-MI"},
        "Atenolol": {"dose": "25-100mg", "mechanism": "Beta Blocker", "side_effects": "Cold extremities, fatigue", "use": "Hypertension, Angina"},
        "Propranolol": {"dose": "40-320mg", "mechanism": "Beta Blocker", "side_effects": "Sleep disturbance, fatigue", "use": "Hypertension, Migraine, Anxiety"},
        "Carvedilol": {"dose": "6.25-50mg", "mechanism": "Beta/Alpha Blocker", "side_effects": "Dizziness, fatigue", "use": "Heart Failure, Hypertension"},
        "Hydrochlorothiazide": {"dose": "12.5-50mg", "mechanism": "Thiazide Diuretic", "side_effects": "Hypokalemia, hyperuricemia", "use": "Hypertension, Edema"},
        "Furosemide": {"dose": "20-80mg", "mechanism": "Loop Diuretic", "side_effects": "Hypokalemia, dehydration", "use": "Edema, Heart Failure, Hypertension"},
        "Spironolactone": {"dose": "25-100mg", "mechanism": "Aldosterone Antagonist", "side_effects": "Hyperkalemia, gynecomastia", "use": "Heart Failure, Ascites"},
        "Digoxin": {"dose": "0.125-0.25mg", "mechanism": "Cardiac Glycoside", "side_effects": "Nausea, visual changes", "use": "Heart Failure, Atrial Fibrillation"},
        "Amiodarone": {"dose": "200-400mg", "mechanism": "Class III Antiarrhythmic", "side_effects": "Pulmonary fibrosis, thyroid dysfunction", "use": "Arrhythmias"},
        "Atorvastatin": {"dose": "10-80mg", "mechanism": "Statin", "side_effects": "Myalgia, elevated liver enzymes", "use": "Hyperlipidemia"},
        "Rosuvastatin": {"dose": "5-40mg", "mechanism": "Statin", "side_effects": "Myalgia, headache", "use": "Hyperlipidemia"},
        "Simvastatin": {"dose": "10-40mg", "mechanism": "Statin", "side_effects": "Myopathy, GI upset", "use": "Hyperlipidemia"},
        "Clopidogrel": {"dose": "75mg", "mechanism": "Antiplatelet (P2Y12)", "side_effects": "Bleeding, bruising", "use": "ACS, Post-stent"},
        "Aspirin": {"dose": "75-325mg", "mechanism": "Antiplatelet (COX inhibitor)", "side_effects": "GI bleeding, tinnitus", "use": "Cardiovascular prevention"},
        "Warfarin": {"dose": "2-10mg", "mechanism": "Vitamin K Antagonist", "side_effects": "Bleeding, skin necrosis", "use": "Anticoagulation"},
        "Rivaroxaban": {"dose": "10-20mg", "mechanism": "Factor Xa Inhibitor", "side_effects": "Bleeding, anemia", "use": "DVT, PE, AF"},
        "Apixaban": {"dose": "2.5-5mg", "mechanism": "Factor Xa Inhibitor", "side_effects": "Bleeding, nausea", "use": "AF, DVT Prevention"},
        "Nitroglycerin": {"dose": "0.3-0.6mg SL", "mechanism": "Nitrate Vasodilator", "side_effects": "Headache, hypotension", "use": "Acute Angina"}
    },
    "Endocrinology": {
        "Metformin": {"dose": "500-2000mg", "mechanism": "Biguanide", "side_effects": "GI upset, lactic acidosis", "use": "Type 2 Diabetes"},
        "Glipizide": {"dose": "5-20mg", "mechanism": "Sulfonylurea", "side_effects": "Hypoglycemia, weight gain", "use": "Type 2 Diabetes"},
        "Glyburide": {"dose": "2.5-10mg", "mechanism": "Sulfonylurea", "side_effects": "Hypoglycemia, nausea", "use": "Type 2 Diabetes"},
        "Pioglitazone": {"dose": "15-45mg", "mechanism": "Thiazolidinedione", "side_effects": "Edema, weight gain, fractures", "use": "Type 2 Diabetes"},
        "Sitagliptin": {"dose": "100mg", "mechanism": "DPP-4 Inhibitor", "side_effects": "Headache, pancreatitis", "use": "Type 2 Diabetes"},
        "Empagliflozin": {"dose": "10-25mg", "mechanism": "SGLT2 Inhibitor", "side_effects": "UTI, dehydration", "use": "Type 2 Diabetes, Heart Failure"},
        "Dapagliflozin": {"dose": "5-10mg", "mechanism": "SGLT2 Inhibitor", "side_effects": "Genital infections, UTI", "use": "Type 2 Diabetes, CKD"},
        "Insulin Glargine": {"dose": "Individualized", "mechanism": "Long-acting Insulin", "side_effects": "Hypoglycemia, lipodystrophy", "use": "Type 1 & 2 Diabetes"},
        "Insulin Aspart": {"dose": "Individualized", "mechanism": "Rapid-acting Insulin", "side_effects": "Hypoglycemia, weight gain", "use": "Type 1 & 2 Diabetes"},
        "Levothyroxine": {"dose": "25-200mcg", "mechanism": "Thyroid Hormone Replacement", "side_effects": "Palpitations, insomnia", "use": "Hypothyroidism"},
        "Methimazole": {"dose": "5-30mg", "mechanism": "Antithyroid (Thionamide)", "side_effects": "Agranulocytosis, rash", "use": "Hyperthyroidism"},
        "Propylthiouracil": {"dose": "100-300mg", "mechanism": "Antithyroid", "side_effects": "Hepatotoxicity, agranulocytosis", "use": "Hyperthyroidism (pregnancy)"},
        "Prednisone": {"dose": "5-60mg", "mechanism": "Corticosteroid", "side_effects": "Weight gain, osteoporosis, hyperglycemia", "use": "Inflammation, Autoimmune"},
        "Hydrocortisone": {"dose": "20-240mg", "mechanism": "Corticosteroid", "side_effects": "Fluid retention, hypertension", "use": "Adrenal insufficiency"},
        "Dexamethasone": {"dose": "0.5-10mg", "mechanism": "Corticosteroid", "side_effects": "Insomnia, increased appetite", "use": "Inflammation, Cerebral edema"},
        "Fludrocortisone": {"dose": "0.1mg", "mechanism": "Mineralocorticoid", "side_effects": "Hypertension, edema", "use": "Addison's Disease"}
    },
    "Antibiotics": {
        "Amoxicillin": {"dose": "500-875mg", "mechanism": "Penicillin (Cell wall synthesis inhibitor)", "side_effects": "Diarrhea, rash", "use": "Respiratory, UTI infections"},
        "Amoxicillin-Clavulanate": {"dose": "500/125mg", "mechanism": "Penicillin + Beta-lactamase inhibitor", "side_effects": "Diarrhea, GI upset", "use": "Broad spectrum infections"},
        "Cephalexin": {"dose": "250-500mg", "mechanism": "1st Gen Cephalosporin", "side_effects": "GI upset, rash", "use": "Skin infections, UTI"},
        "Ceftriaxone": {"dose": "1-2g IV", "mechanism": "3rd Gen Cephalosporin", "side_effects": "Diarrhea, biliary sludging", "use": "Serious infections, Meningitis"},
        "Cefuroxime": {"dose": "250-500mg", "mechanism": "2nd Gen Cephalosporin", "side_effects": "Diarrhea, headache", "use": "Respiratory, Skin infections"},
        "Azithromycin": {"dose": "250-500mg", "mechanism": "Macrolide (Protein synthesis inhibitor)", "side_effects": "GI upset, prolonged QT", "use": "Respiratory infections"},
        "Clarithromycin": {"dose": "250-500mg", "mechanism": "Macrolide", "side_effects": "GI upset, taste disturbance", "use": "H. pylori, Respiratory infections"},
        "Doxycycline": {"dose": "100mg", "mechanism": "Tetracycline", "side_effects": "Photosensitivity, esophagitis", "use": "Acne, Lyme disease, Malaria prophylaxis"},
        "Ciprofloxacin": {"dose": "250-750mg", "mechanism": "Fluoroquinolone (DNA gyrase inhibitor)", "side_effects": "Tendonitis, neuropathy", "use": "UTI, GI infections"},
        "Levofloxacin": {"dose": "500-750mg", "mechanism": "Fluoroquinolone", "side_effects": "Tendon rupture, CNS effects", "use": "Respiratory, UTI infections"},
        "Metronidazole": {"dose": "500mg", "mechanism": "Nitroimidazole (DNA synthesis inhibitor)", "side_effects": "Metallic taste, nausea", "use": "Anaerobic infections, C. diff"},
        "Clindamycin": {"dose": "150-450mg", "mechanism": "Lincosamide", "side_effects": "C. diff colitis, rash", "use": "Anaerobic infections, Acne"},
        "Vancomycin": {"dose": "IV based on levels", "mechanism": "Glycopeptide", "side_effects": "Red man syndrome, nephrotoxicity", "use": "MRSA, C. diff (oral)"},
        "Trimethoprim-Sulfamethoxazole": {"dose": "160/800mg", "mechanism": "Folate synthesis inhibitor", "side_effects": "Rash, hyperkalemia", "use": "UTI, PCP prophylaxis"},
        "Nitrofurantoin": {"dose": "100mg", "mechanism": "Bacterial enzyme inhibitor", "side_effects": "Pulmonary fibrosis, neuropathy", "use": "UTI prophylaxis"}
    },
    "Neurology/Psychiatry": {
        "Sertraline": {"dose": "50-200mg", "mechanism": "SSRI", "side_effects": "GI upset, sexual dysfunction", "use": "Depression, Anxiety, PTSD"},
        "Fluoxetine": {"dose": "20-80mg", "mechanism": "SSRI", "side_effects": "Insomnia, weight changes", "use": "Depression, OCD, Bulimia"},
        "Escitalopram": {"dose": "10-20mg", "mechanism": "SSRI", "side_effects": "Nausea, fatigue", "use": "Depression, Generalized Anxiety"},
        "Venlafaxine": {"dose": "75-375mg", "mechanism": "SNRI", "side_effects": "Hypertension, sweating", "use": "Depression, Anxiety"},
        "Duloxetine": {"dose": "30-120mg", "mechanism": "SNRI", "side_effects": "Nausea, dry mouth", "use": "Depression, Neuropathic pain"},
        "Amitriptyline": {"dose": "25-150mg", "mechanism": "TCA", "side_effects": "Sedation, dry mouth, weight gain", "use": "Depression, Neuropathic pain, Migraine"},
        "Quetiapine": {"dose": "25-800mg", "mechanism": "Atypical Antipsychotic", "side_effects": "Weight gain, sedation, metabolic syndrome", "use": "Schizophrenia, Bipolar, Insomnia"},
        "Risperidone": {"dose": "1-6mg", "mechanism": "Atypical Antipsychotic", "side_effects": "Weight gain, hyperprolactinemia", "use": "Schizophrenia, Bipolar"},
        "Olanzapine": {"dose": "5-20mg", "mechanism": "Atypical Antipsychotic", "side_effects": "Weight gain, diabetes risk", "use": "Schizophrenia, Bipolar"},
        "Lithium": {"dose": "300-1800mg", "mechanism": "Mood Stabilizer", "side_effects": "Tremor, thyroid dysfunction, nephrotoxicity", "use": "Bipolar Disorder"},
        "Valproic Acid": {"dose": "250-3000mg", "mechanism": "Mood Stabilizer/Anticonvulsant", "side_effects": "Weight gain, hepatotoxicity, teratogenicity", "use": "Bipolar, Epilepsy"},
        "Carbamazepine": {"dose": "200-1600mg", "mechanism": "Anticonvulsant", "side_effects": "Hyponatremia, aplastic anemia, rash", "use": "Epilepsy, Trigeminal neuralgia"},
        "Gabapentin": {"dose": "300-3600mg", "mechanism": "Calcium channel modulator", "side_effects": "Sedation, dizziness", "use": "Neuropathic pain, Epilepsy"},
        "Pregabalin": {"dose": "75-600mg", "mechanism": "Calcium channel modulator", "side_effects": "Dizziness, weight gain", "use": "Neuropathic pain, Fibromyalgia"},
        "Levetiracetam": {"dose": "500-3000mg", "mechanism": "Anticonvulsant (SV2A modulator)", "side_effects": "Behavioral changes, sedation", "use": "Epilepsy"},
        "Donepezil": {"dose": "5-10mg", "mechanism": "Cholinesterase Inhibitor", "side_effects": "GI upset, bradycardia", "use": "Alzheimer's Disease"},
        "Sumatriptan": {"dose": "50-100mg", "mechanism": "5-HT1 Agonist", "side_effects": "Chest tightness, paresthesia", "use": "Acute Migraine"}
    },
    "Gastroenterology": {
        "Omeprazole": {"dose": "20-40mg", "mechanism": "PPI", "side_effects": "Headache, GI upset, B12 deficiency", "use": "GERD, Peptic Ulcer"},
        "Pantoprazole": {"dose": "40mg", "mechanism": "PPI", "side_effects": "Headache, diarrhea", "use": "GERD, Erosive Esophagitis"},
        "Esomeprazole": {"dose": "20-40mg", "mechanism": "PPI", "side_effects": "GI upset, headache", "use": "GERD, H. pylori eradication"},
        "Ranitidine": {"dose": "150-300mg", "mechanism": "H2 Antagonist", "side_effects": "Headache, dizziness", "use": "GERD, Peptic Ulcer"},
        "Famotidine": {"dose": "20-40mg", "mechanism": "H2 Antagonist", "side_effects": "Constipation, diarrhea", "use": "GERD, Hypersecretory conditions"},
        "Ondansetron": {"dose": "4-8mg", "mechanism": "5-HT3 Antagonist", "side_effects": "Headache, constipation, QT prolongation", "use": "Nausea, Vomiting"},
        "Metoclopramide": {"dose": "10mg", "mechanism": "Dopamine Antagonist", "side_effects": "EPS, tardive dyskinesia", "use": "Gastroparesis, Nausea"},
        "Loperamide": {"dose": "2-4mg", "mechanism": "Opioid Agonist (peripheral)", "side_effects": "Constipation, abdominal cramps", "use": "Diarrhea"},
        "Mesalamine": {"dose": "2.4-4.8g", "mechanism": "5-ASA Anti-inflammatory", "side_effects": "Headache, GI upset", "use": "Ulcerative Colitis"},
        "Lactulose": {"dose": "15-30mL", "mechanism": "Osmotic Laxative", "side_effects": "Bloating, flatulence", "use": "Constipation, Hepatic encephalopathy"}
    },
    "Respiratory": {
        "Albuterol": {"dose": "2 puffs PRN", "mechanism": "Beta-2 Agonist (SABA)", "side_effects": "Tremor, tachycardia", "use": "Asthma, COPD"},
        "Salmeterol": {"dose": "50mcg BID", "mechanism": "Beta-2 Agonist (LABA)", "side_effects": "Tremor, palpitations", "use": "Asthma, COPD maintenance"},
        "Fluticasone": {"dose": "100-500mcg BID", "mechanism": "Inhaled Corticosteroid", "side_effects": "Oral thrush, dysphonia", "use": "Asthma maintenance"},
        "Budesonide": {"dose": "200-800mcg BID", "mechanism": "Inhaled Corticosteroid", "side_effects": "Cough, oral candidiasis", "use": "Asthma, COPD"},
        "Montelukast": {"dose": "10mg", "mechanism": "Leukotriene Receptor Antagonist", "side_effects": "Headache, behavioral changes", "use": "Asthma, Allergic Rhinitis"},
        "Tiotropium": {"dose": "18mcg daily", "mechanism": "Anticholinergic (LAMA)", "side_effects": "Dry mouth, constipation", "use": "COPD"},
        "Ipratropium": {"dose": "2-4 puffs QID", "mechanism": "Anticholinergic (SAMA)", "side_effects": "Dry mouth, blurred vision", "use": "COPD, Asthma"},
        "Theophylline": {"dose": "200-600mg", "mechanism": "Phosphodiesterase Inhibitor", "side_effects": "Nausea, seizures, arrhythmias", "use": "Asthma, COPD (refractory)"}
    },
    "Pain Management": {
        "Ibuprofen": {"dose": "200-800mg", "mechanism": "NSAID", "side_effects": "GI ulcer, renal impairment", "use": "Pain, Inflammation, Fever"},
        "Naproxen": {"dose": "250-500mg BID", "mechanism": "NSAID", "side_effects": "GI upset, edema", "use": "Pain, Inflammation"},
        "Celecoxib": {"dose": "100-200mg BID", "mechanism": "COX-2 Selective NSAID", "side_effects": "Cardiovascular risk, GI upset", "use": "Osteoarthritis, RA"},
        "Acetaminophen": {"dose": "500-1000mg", "mechanism": "Analgesic/Antipyretic", "side_effects": "Hepatotoxicity (overdose)", "use": "Pain, Fever"},
        "Tramadol": {"dose": "50-100mg", "mechanism": "Opioid + SNRI", "side_effects": "Nausea, seizures, dependence", "use": "Moderate to severe pain"},
        "Morphine": {"dose": "5-30mg", "mechanism": "Opioid Agonist", "side_effects": "Respiratory depression, constipation, dependence", "use": "Severe acute/chronic pain"},
        "Oxycodone": {"dose": "5-30mg", "mechanism": "Opioid Agonist", "side_effects": "Respiratory depression, constipation", "use": "Severe pain"},
        "Fentanyl": {"dose": "12-100mcg/hr patch", "mechanism": "Opioid Agonist", "side_effects": "Respiratory depression, tolerance", "use": "Chronic severe pain"},
        "Gabapentin": {"dose": "300-3600mg", "mechanism": "α2δ ligand", "side_effects": "Dizziness, sedation, weight gain", "use": "Neuropathic pain"},
        "Pregabalin": {"dose": "75-600mg", "mechanism": "α2δ ligand", "side_effects": "Dizziness, edema, weight gain", "use": "Neuropathic pain, Fibromyalgia"}
    }
}

# ================================
# 8. HELPER FUNCTIONS
# ================================
def get_disease_count() -> int:
    return len(DISEASE_DATABASE)

def get_drug_count() -> int:
    total = sum(len(drugs) for drugs in DRUG_DATABASE.values())
    custom_drugs = load_custom_drugs()
    return total + len(custom_drugs)

def get_lab_count() -> int:
    total = len(LAB_TESTS)
    custom_labs = load_custom_labs()
    return total + len(custom_labs)

def get_all_drugs() -> Dict:
    all_drugs = {}
    for category, drugs in DRUG_DATABASE.items():
        for drug_name, drug_info in drugs.items():
            all_drugs[drug_name] = {**drug_info, "category": category}
    custom_drugs = load_custom_drugs()
    all_drugs.update(custom_drugs)
    return all_drugs

def get_all_labs() -> Dict:
    all_labs = dict(LAB_TESTS)
    custom_labs = load_custom_labs()
    all_labs.update(custom_labs)
    return all_labs

def get_risk_color(risk: str) -> str:
    colors = {"Critical": "#ef4444", "High": "#f59e0b", "Moderate": "#06b6d4", "Low": "#10b981"}
    return colors.get(risk, "#6b7280")

def check_drug_interactions(drugs: List[str]) -> List[Dict]:
    interactions = []
    interaction_db = {
        ("Warfarin", "Aspirin"): ("Critical", "Major bleeding risk"),
        ("Warfarin", "Ibuprofen"): ("Critical", "Increased bleeding risk"),
        ("Lisinopril", "Spironolactone"): ("High", "Hyperkalemia risk"),
        ("Metformin", "Furosemide"): ("Moderate", "Increased lactic acidosis risk"),
        ("Amiodarone", "Warfarin"): ("High", "Increased INR"),
        ("Fluoxetine", "Tramadol"): ("Critical", "Serotonin syndrome risk"),
        ("Ciprofloxacin", "Theophylline"): ("High", "Theophylline toxicity"),
        ("Omeprazole", "Clopidogrel"): ("Moderate", "Reduced clopidogrel efficacy")
    }
    
    for i in range(len(drugs)):
        for j in range(i+1, len(drugs)):
            pair = (drugs[i], drugs[j])
            reverse = (drugs[j], drugs[i])
            if pair in interaction_db:
                severity, effect = interaction_db[pair]
                interactions.append({"drug1": drugs[i], "drug2": drugs[j], "severity": severity, "effect": effect})
            elif reverse in interaction_db:
                severity, effect = interaction_db[reverse]
                interactions.append({"drug1": drugs[j], "drug2": drugs[i], "severity": severity, "effect": effect})
    return interactions

def get_leaderboard_df() -> pd.DataFrame:
    leaderboard = load_leaderboard()
    if leaderboard:
        df = pd.DataFrame(leaderboard)
        return df.sort_values("xp_points", ascending=False)
    return pd.DataFrame()

def create_study_room(room_name: str, creator: str) -> str:
    rooms = load_study_rooms()
    room_id = str(uuid.uuid4())[:8]
    rooms[room_id] = {
        "name": room_name,
        "creator": creator,
        "members": [creator],
        "messages": [],
        "created_at": datetime.now().isoformat()
    }
    save_study_rooms(rooms)
    return room_id

def join_study_room(room_id: str, username: str) -> bool:
    rooms = load_study_rooms()
    if room_id in rooms:
        if username not in rooms[room_id]["members"]:
            rooms[room_id]["members"].append(username)
            save_study_rooms(rooms)
        return True
    return False

def send_room_message(room_id: str, username: str, message: str):
    rooms = load_study_rooms()
    if room_id in rooms:
        rooms[room_id]["messages"].append({
            "username": username,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        save_study_rooms(rooms)

def add_clinical_note(username: str, note: Dict):
    notes = load_clinical_notes()
    if username not in notes:
        notes[username] = []
    note["timestamp"] = datetime.now().isoformat()
    notes[username].append(note)
    save_clinical_notes(notes)

def get_clinical_notes(username: str) -> List:
    notes = load_clinical_notes()
    return notes.get(username, [])

def fetch_medical_news() -> List:
    return [
        {"title": "New Diabetes Drug Shows Promise in Clinical Trials", "summary": "A novel GLP-1 receptor agonist demonstrates superior glycemic control with fewer side effects in Phase 3 trials.", "source": "NEJM", "date": "2024-01-20"},
        {"title": "AI-Assisted Diagnosis Improves Cancer Detection Rates", "summary": "Machine learning algorithms show 95% accuracy in early-stage lung cancer detection from CT scans.", "source": "The Lancet", "date": "2024-01-18"},
        {"title": "mRNA Technology Beyond COVID-19", "summary": "Researchers develop mRNA vaccines for malaria and tuberculosis with promising early results.", "source": "Nature Medicine", "date": "2024-01-15"},
        {"title": "Breakthrough in Alzheimer's Treatment", "summary": "New monoclonal antibody shows significant slowing of cognitive decline in early Alzheimer's patients.", "source": "JAMA", "date": "2024-01-12"},
        {"title": "Global Antibiotic Resistance Crisis Deepens", "summary": "WHO reports alarming increase in multidrug-resistant bacterial infections worldwide.", "source": "WHO", "date": "2024-01-10"}
    ]

def generate_comprehensive_exam(num_questions: int = 100) -> List[Dict]:
    questions = []
    for disease, info in DISEASE_DATABASE.items():
        if info["symptoms"]:
            correct = random.choice(info["symptoms"])
            wrong_options = random.sample([s for d in DISEASE_DATABASE.values() for s in d.get("symptoms", []) if s != correct], min(3, len(DISEASE_DATABASE)))
            options = [correct] + wrong_options[:3]
            random.shuffle(options)
            questions.append({
                "question": f"Which symptom is characteristic of {disease}?",
                "options": options,
                "correct": options.index(correct),
                "explanation": f"{disease}: {', '.join(info['symptoms'][:3])}"
            })
    return random.sample(questions, min(num_questions, len(questions)))

def generate_microscope_view(cell_type: str):
    fig, ax = plt.subplots(figsize=(4, 4), facecolor='#0a0a1a')
    ax.set_facecolor('#0a0a1a')
    
    if cell_type == "RBC":
        for _ in range(40):
            x, y = random.uniform(0, 1), random.uniform(0, 1)
            circle = plt.Circle((x, y), random.uniform(0.02, 0.05), color='#ef4444', alpha=0.7, ec='#dc2626')
            ax.add_patch(circle)
        ax.set_title("Red Blood Cells (RBCs)", color='white', fontsize=14, fontweight='bold')
    elif cell_type == "WBC":
        for _ in range(15):
            x, y = random.uniform(0, 1), random.uniform(0, 1)
            circle = plt.Circle((x, y), random.uniform(0.04, 0.08), color=random.choice(['#8b5cf6', '#6366f1']), alpha=0.6)
            ax.add_patch(circle)
            inner = plt.Circle((x, y), random.uniform(0.02, 0.04), color='#4c1d95', alpha=0.8)
            ax.add_patch(inner)
        ax.set_title("White Blood Cells (WBCs)", color='white', fontsize=14, fontweight='bold')
    elif cell_type == "Platelets":
        for _ in range(60):
            x, y = random.uniform(0, 1), random.uniform(0, 1)
            circle = plt.Circle((x, y), random.uniform(0.008, 0.02), color='#a78bfa', alpha=0.6)
            ax.add_patch(circle)
        ax.set_title("Platelets", color='white', fontsize=14, fontweight='bold')
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    st.pyplot(fig)
    plt.close()

def auto_save():
    if st.session_state.logged_in:
        save_user_data(st.session_state.username, {
            "xp_points": st.session_state.xp_points,
            "badges": st.session_state.badges,
            "quiz_score": st.session_state.quiz_score,
            "total_cases_solved": st.session_state.total_cases_solved,
            "correct_diagnoses": st.session_state.correct_diagnoses
        })

# ================================
# 9. SESSION STATE INITIALIZATION
# ================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'xp_points' not in st.session_state:
    st.session_state.xp_points = 0
if 'badges' not in st.session_state:
    st.session_state.badges = []
if 'quiz_score' not in st.session_state:
    st.session_state.quiz_score = 0
if 'total_cases_solved' not in st.session_state:
    st.session_state.total_cases_solved = 0
if 'correct_diagnoses' not in st.session_state:
    st.session_state.correct_diagnoses = 0
if 'streak_days' not in st.session_state:
    st.session_state.streak_days = 0
if 'current_case' not in st.session_state:
    st.session_state.current_case = None
if 'achievements' not in st.session_state:
    st.session_state.achievements = []
if 'comprehensive_exam_questions' not in st.session_state:
    st.session_state.comprehensive_exam_questions = None
if 'comprehensive_exam_submitted' not in st.session_state:
    st.session_state.comprehensive_exam_submitted = False
if 'comprehensive_exam_score' not in st.session_state:
    st.session_state.comprehensive_exam_score = 0
if 'flashcard_index' not in st.session_state:
    st.session_state.flashcard_index = 0
if 'flashcard_flipped' not in st.session_state:
    st.session_state.flashcard_flipped = False
if 'current_room_id' not in st.session_state:
    st.session_state.current_room_id = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = "🏠 Dashboard"
if 'editing_drug' not in st.session_state:
    st.session_state.editing_drug = None
if 'editing_lab' not in st.session_state:
    st.session_state.editing_lab = None

# ================================
# 10. LOGIN PAGE
# ================================
if not st.session_state.logged_in:
    # Animated background particles CSS
    st.markdown("""
    <style>
    .particles-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: 0;
        overflow: hidden;
    }
    
    .particle {
        position: absolute;
        background: radial-gradient(circle, rgba(99, 102, 241, 0.3), transparent);
        border-radius: 50%;
        animation: float-particle 15s infinite;
    }
    
    @keyframes float-particle {
        0% { transform: translateY(100vh) scale(0); opacity: 0; }
        10% { opacity: 1; }
        90% { opacity: 1; }
        100% { transform: translateY(-100vh) scale(1); opacity: 0; }
    }
    </style>
    
    <div class="particles-container">
        <div class="particle" style="left: 10%; width: 200px; height: 200px; animation-delay: 0s;"></div>
        <div class="particle" style="left: 30%; width: 150px; height: 150px; animation-delay: 3s;"></div>
        <div class="particle" style="left: 50%; width: 250px; height: 250px; animation-delay: 6s;"></div>
        <div class="particle" style="left: 70%; width: 180px; height: 180px; animation-delay: 9s;"></div>
        <div class="particle" style="left: 90%; width: 220px; height: 220px; animation-delay: 12s;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        
        st.markdown('<div class="login-logo">🩺</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-title">Dr.Danyal</div>', unsafe_allow_html=True)
        st.markdown('<p style="color: rgba(255,255,255,0.6); margin-bottom: 2rem;">Advanced Medical Training Platform</p>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])
        
        with tab1:
            with st.form("login_form"):
                login_user = st.text_input("Username", placeholder="Enter your username", key="login_user")
                login_pass = st.text_input("Password", type="password", placeholder="Enter your password", key="login_pass")
                
                col_a, col_b, col_c = st.columns([1, 2, 1])
                with col_b:
                    submitted = st.form_submit_button("🚀 Login", type="primary", use_container_width=True)
                
                if submitted:
                    if authenticate_user(login_user, login_pass):
                        st.session_state.logged_in = True
                        st.session_state.username = login_user
                        user_data = load_user_data(login_user)
                        st.session_state.xp_points = user_data.get("xp_points", 0)
                        st.session_state.badges = user_data.get("badges", [])
                        st.session_state.quiz_score = user_data.get("quiz_score", 0)
                        st.session_state.total_cases_solved = user_data.get("total_cases_solved", 0)
                        st.session_state.correct_diagnoses = user_data.get("correct_diagnoses", 0)
                        st.session_state.streak_days = update_user_streak(login_user)
                        add_xp(login_user, 1)
                        st.success(f"✅ Welcome back, {login_user}!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")
        
        with tab2:
            with st.form("register_form"):
                new_user = st.text_input("Choose Username", placeholder="Enter username", key="new_user")
                new_pass = st.text_input("Choose Password", type="password", placeholder="Enter password", key="new_pass")
                confirm_pass = st.text_input("Confirm Password", type="password", placeholder="Confirm password", key="confirm_pass")
                
                col_a, col_b, col_c = st.columns([1, 2, 1])
                with col_b:
                    reg_submitted = st.form_submit_button("✨ Create Account", type="primary", use_container_width=True)
                
                if reg_submitted:
                    if not new_user or not new_pass:
                        st.error("❌ Please fill all fields")
                    elif new_pass != confirm_pass:
                        st.error("❌ Passwords don't match")
                    elif len(new_pass) < 4:
                        st.error("❌ Password must be at least 4 characters")
                    elif create_user(new_user, new_pass):
                        st.success("✅ Account created! Please login.")
                    else:
                        st.error("❌ Username already exists")
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.stop()

# ================================
# 11. SIDEBAR
# ================================
with st.sidebar:
    # User Profile
    level = get_user_level(st.session_state.quiz_score)
    level_info = get_level_info(level)
    progress = get_level_progress(st.session_state.quiz_score)
    
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem 0;">
        <div style="font-size: 3rem; filter: drop-shadow(0 0 20px rgba(99,102,241,0.5));">{level_info['icon']}</div>
        <div style="font-size: 1.3rem; font-weight: 700; background: linear-gradient(135deg, #6366f1, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin: 0.5rem 0;">
            {st.session_state.username}
        </div>
        <span class="badge badge-primary">{level_info['name']}</span>
    </div>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin: 1rem 0;">
        <div style="background: rgba(99,102,241,0.1); padding: 0.7rem; border-radius: 10px; text-align: center;">
            <div style="font-size: 1.2rem; font-weight: 700; color: #a78bfa;">⭐ {st.session_state.xp_points}</div>
            <div style="font-size: 0.65rem; color: rgba(255,255,255,0.5);">XP Points</div>
        </div>
        <div style="background: rgba(99,102,241,0.1); padding: 0.7rem; border-radius: 10px; text-align: center;">
            <div style="font-size: 1.2rem; font-weight: 700; color: #a78bfa;">📊 {st.session_state.quiz_score}</div>
            <div style="font-size: 0.65rem; color: rgba(255,255,255,0.5);">Quiz Score</div>
        </div>
        <div style="background: rgba(99,102,241,0.1); padding: 0.7rem; border-radius: 10px; text-align: center;">
            <div style="font-size: 1.2rem; font-weight: 700; color: #a78bfa;">🔥 {st.session_state.streak_days}</div>
            <div style="font-size: 0.65rem; color: rgba(255,255,255,0.5);">Day Streak</div>
        </div>
        <div style="background: rgba(99,102,241,0.1); padding: 0.7rem; border-radius: 10px; text-align: center;">
            <div style="font-size: 1.2rem; font-weight: 700; color: #a78bfa;">🩺 {st.session_state.total_cases_solved}</div>
            <div style="font-size: 0.65rem; color: rgba(255,255,255,0.5);">Cases Solved</div>
        </div>
    </div>
    
    <div style="margin: 0.5rem 0;">
        <div style="width: 100%; height: 6px; background: rgba(255,255,255,0.1); border-radius: 10px; overflow: hidden;">
            <div style="width: {progress:.1f}%; height: 100%; background: linear-gradient(90deg, #6366f1, #8b5cf6, #a78bfa); border-radius: 10px; transition: width 0.5s ease;"></div>
        </div>
        <div style="font-size: 0.65rem; color: rgba(255,255,255,0.5); text-align: right; margin-top: 0.2rem;">Level Progress: {progress:.0f}%</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation with buttons for reliable navigation
    st.markdown("### 📋 Navigation")
    
    # Main Section
    with st.expander("🏠 MAIN", expanded=True):
        if st.button("📊 Dashboard", use_container_width=True, key="nav_dashboard"):
            st.session_state.current_page = "🏠 Dashboard"
            st.rerun()
        if st.button("📚 Diseases Library", use_container_width=True, key="nav_diseases"):
            st.session_state.current_page = "📚 Diseases"
            st.rerun()
        if st.button("🩺 Case Analysis", use_container_width=True, key="nav_cases"):
            st.session_state.current_page = "🩺 Case Analysis"
            st.rerun()
        if st.button("📝 Quiz Mode", use_container_width=True, key="nav_quiz"):
            st.session_state.current_page = "📝 Quiz"
            st.rerun()
        if st.button("📋 Comprehensive Exam", use_container_width=True, key="nav_exam"):
            st.session_state.current_page = "📋 Comprehensive Exam"
            st.rerun()
    
    # Learning Section
    with st.expander("📖 LEARNING", expanded=False):
        if st.button("🔄 Spaced Repetition", use_container_width=True, key="nav_sr"):
            st.session_state.current_page = "🔄 Spaced Repetition"
            st.rerun()
        if st.button("🔬 Lab Tests (100+)", use_container_width=True, key="nav_labs"):
            st.session_state.current_page = "🔬 Lab Tests"
            st.rerun()
        if st.button("💊 Pharmacology (100+)", use_container_width=True, key="nav_drugs"):
            st.session_state.current_page = "💊 Pharmacology"
            st.rerun()
        if st.button("⚠️ Drug Interactions", use_container_width=True, key="nav_interactions"):
            st.session_state.current_page = "⚠️ Drug Interactions"
            st.rerun()
    
    # Community Section
    with st.expander("👥 COMMUNITY", expanded=False):
        if st.button("🏆 Leaderboard", use_container_width=True, key="nav_leaderboard"):
            st.session_state.current_page = "🏆 Leaderboard"
            st.rerun()
        if st.button("👥 Study Rooms", use_container_width=True, key="nav_rooms"):
            st.session_state.current_page = "👥 Study Rooms"
            st.rerun()
        if st.button("📰 Medical News", use_container_width=True, key="nav_news"):
            st.session_state.current_page = "📰 Medical News"
            st.rerun()
    
    # Advanced Section
    with st.expander("🔬 ADVANCED", expanded=False):
        if st.button("🔬 Virtual Microscope", use_container_width=True, key="nav_microscope"):
            st.session_state.current_page = "🔬 Microscope"
            st.rerun()
        if st.button("📝 Clinical Notes", use_container_width=True, key="nav_notes"):
            st.session_state.current_page = "📝 Clinical Notes"
            st.rerun()
        if st.button("🧠 AI Assistant", use_container_width=True, key="nav_ai"):
            st.session_state.current_page = "🧠 AI Assistant"
            st.rerun()
        if st.button("🏆 Achievements", use_container_width=True, key="nav_achievements"):
            st.session_state.current_page = "🏆 Achievements"
            st.rerun()
    
    st.markdown("---")
    
    # Logout
    if st.button("🚪 Logout", use_container_width=True, type="primary"):
        auto_save()
        st.session_state.logged_in = False
        st.rerun()
    
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0; font-size: 0.7rem; color: rgba(255,255,255,0.3);">
        <span class="badge badge-primary">v9.0 Pro</span>
        <p style="margin-top: 0.5rem;">© 2024 Dr.Danyal</p>
    </div>
    """, unsafe_allow_html=True)

# ================================
# 12. PAGE CONTENT BASED ON NAVIGATION
# ================================
page = st.session_state.current_page

if page == "🏠 Dashboard":
    st.markdown('<h1 style="text-align: center; margin-bottom: 2rem;">📊 Medical Training Dashboard</h1>', unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f'<div class="stat-card"><h3>📚</h3><div class="stat-number">{get_disease_count()}</div><p>Diseases</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="stat-card"><h3>💊</h3><div class="stat-number">{get_drug_count()}</div><p>Drugs</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="stat-card"><h3>🔬</h3><div class="stat-number">{get_lab_count()}</div><p>Lab Tests</p></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="stat-card"><h3>⭐</h3><div class="stat-number">{st.session_state.xp_points}</div><p>XP</p></div>', unsafe_allow_html=True)
    with col5:
        st.markdown(f'<div class="stat-card"><h3>🔥</h3><div class="stat-number">{st.session_state.streak_days}</div><p>Streak</p></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="glass-card">
            <h3>📊 Your Progress</h3>
            <p><strong>Level:</strong> {get_level_info(level)['icon']} {get_level_info(level)['name']}</p>
            <p><strong>Quiz Score:</strong> {st.session_state.quiz_score}/100</p>
            <p><strong>Cases Solved:</strong> {st.session_state.total_cases_solved}</p>
            <p><strong>Correct Diagnoses:</strong> {st.session_state.correct_diagnoses}</p>
            <p><strong>XP Points:</strong> {st.session_state.xp_points}</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="glass-card">
            <h3>🎯 Quick Stats</h3>
            <p><strong>Accuracy:</strong> {(st.session_state.correct_diagnoses / max(st.session_state.total_cases_solved, 1) * 100):.1f}%</p>
            <p><strong>Level Progress:</strong> {progress:.1f}%</p>
            <p><strong>Daily Streak:</strong> {st.session_state.streak_days} days</p>
            <p><strong>Achievements:</strong> {len(st.session_state.achievements)} earned</p>
        </div>
        """, unsafe_allow_html=True)

elif page == "📚 Diseases":
    st.markdown('<h2>📚 Disease Library</h2>', unsafe_allow_html=True)
    
    search = st.text_input("🔍 Search diseases:", placeholder="Type disease name...")
    risk_filter = st.selectbox("Filter by risk:", ["All", "Critical", "High", "Moderate", "Low"])
    
    filtered = DISEASE_DATABASE.copy()
    if search:
        filtered = {k: v for k, v in filtered.items() if search.lower() in k.lower()}
    if risk_filter != "All":
        filtered = {k: v for k, v in filtered.items() if v.get("risk") == risk_filter}
    
    cols = st.columns(2)
    for i, (disease, info) in enumerate(filtered.items()):
        with cols[i % 2]:
            with st.expander(f"🩺 {disease}"):
                st.markdown(f"**Risk:** <span style='color:{get_risk_color(info.get('risk', 'Low'))}'>{info.get('risk', 'N/A')}</span>", unsafe_allow_html=True)
                st.markdown(f"**Age Group:** {info.get('age_group', 'All ages')}")
                st.markdown(f"**Symptoms:** {', '.join(info.get('symptoms', [])[:5])}")
                st.markdown(f"**Treatment:** {', '.join(info.get('treatment', [])[:3])}")
                if info.get('tests'):
                    st.markdown("**Key Tests:**")
                    for test, value in list(info['tests'].items())[:3]:
                        st.markdown(f"- {test}: {value}")

elif page == "🩺 Case Analysis":
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
            "risk": info["risk"]
        }
        st.rerun()
    
    if st.session_state.current_case:
        case = st.session_state.current_case
        st.markdown(f"""
        <div class="glass-card">
            <h3>📋 Case #{case['id']}</h3>
            <p><strong>Patient:</strong> {case['age']} year old {case['gender']}</p>
            <p><strong>Symptoms:</strong> {', '.join(case['symptoms'])}</p>
            <p><strong>Risk Level:</strong> <span style='color:{get_risk_color(case['risk'])}'>{case['risk']}</span></p>
        </div>
        """, unsafe_allow_html=True)
        
        diagnosis = st.selectbox("Your Diagnosis:", list(DISEASE_DATABASE.keys()))
        
        if st.button("✅ Submit Diagnosis", type="primary"):
            st.session_state.total_cases_solved += 1
            if diagnosis == case["diagnosis"]:
                st.session_state.correct_diagnoses += 1
                add_xp(st.session_state.username, 20)
                st.markdown(f'<div class="success-message"><h3>🎉 Correct!</h3><p>Diagnosis: {case["diagnosis"]}</p></div>', unsafe_allow_html=True)
                st.balloons()
            else:
                st.markdown(f'<div class="error-message"><h3>❌ Incorrect</h3><p>Correct: {case["diagnosis"]}</p></div>', unsafe_allow_html=True)

elif page == "📝 Quiz":
    st.markdown('<h2>📝 Medical Quiz</h2>', unsafe_allow_html=True)
    
    diseases = list(DISEASE_DATABASE.keys())
    if diseases:
        disease = random.choice(diseases)
        info = DISEASE_DATABASE[disease]
        correct = info["symptoms"][0]
        wrong = [s for d in diseases if d != disease for s in DISEASE_DATABASE[d]["symptoms"][:1] if s != correct][:3]
        options = [correct] + wrong
        random.shuffle(options)
        
        st.markdown(f"""
        <div class="glass-card">
            <h3>Which symptom is most characteristic of <strong>{disease}</strong>?</h3>
        </div>
        """, unsafe_allow_html=True)
        
        answer = st.radio("Select your answer:", options, key="quiz_answer")
        
        if st.button("✅ Submit Answer", type="primary"):
            if answer == correct:
                st.session_state.quiz_score += 1
                add_xp(st.session_state.username, 10)
                st.success(f"🎉 Correct! It's {correct}.")
            else:
                st.error(f"❌ Wrong. The correct answer is: {correct}")
            st.rerun()

elif page == "📋 Comprehensive Exam":
    st.markdown('<h2>📋 Comprehensive Medical Exam</h2>', unsafe_allow_html=True)
    
    if st.session_state.comprehensive_exam_questions is None:
        if st.button("🚀 Start 100-Question Exam", type="primary", use_container_width=True):
            st.session_state.comprehensive_exam_questions = generate_comprehensive_exam(100)
            st.session_state.comprehensive_exam_answers = {}
            st.session_state.comprehensive_exam_submitted = False
            st.rerun()
    elif not st.session_state.comprehensive_exam_submitted:
        questions = st.session_state.comprehensive_exam_questions
        for i, q in enumerate(questions):
            st.markdown(f"**{i+1}. {q['question']}**")
            ans = st.radio(f"Answer {i+1}:", q["options"], key=f"exam_{i}")
            st.session_state.comprehensive_exam_answers[i] = q["options"].index(ans) if ans else -1
        
        if st.button("📤 Submit Exam", type="primary"):
            score = sum(1 for i, q in enumerate(questions) if st.session_state.comprehensive_exam_answers.get(i) == q["correct"])
            st.session_state.comprehensive_exam_score = score
            st.session_state.comprehensive_exam_submitted = True
            add_xp(st.session_state.username, score * 2)
            st.rerun()
    else:
        score = st.session_state.comprehensive_exam_score
        total = len(st.session_state.comprehensive_exam_questions)
        pct = (score / total) * 100
        st.markdown(f'<div class="success-message"><h2>🎉 Score: {score}/{total} ({pct:.1f}%)</h2></div>', unsafe_allow_html=True)
        if st.button("🔄 Retake Exam"):
            st.session_state.comprehensive_exam_questions = None
            st.rerun()

elif page == "🔄 Spaced Repetition":
    st.markdown('<h2>🔄 Spaced Repetition Flashcards</h2>', unsafe_allow_html=True)
    
    diseases = list(DISEASE_DATABASE.keys())
    if diseases:
        disease = random.choice(diseases)
        info = DISEASE_DATABASE[disease]
        
        if st.session_state.flashcard_flipped:
            st.markdown(f"""
            <div class="glass-card" style="text-align: center; padding: 3rem;">
                <h3>Answer for {disease}:</h3>
                <p style="font-size: 1.2rem;">Symptoms: {', '.join(info['symptoms'][:4])}</p>
                <p style="color: #a78bfa;">Treatment: {', '.join(info.get('treatment', [])[:3])}</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ I Knew It", type="primary", use_container_width=True):
                    st.session_state.flashcard_flipped = False
                    add_xp(st.session_state.username, 5)
                    st.rerun()
            with col2:
                if st.button("❌ Need Review", use_container_width=True):
                    st.session_state.flashcard_flipped = False
                    st.rerun()
        else:
            st.markdown(f"""
            <div class="glass-card" style="text-align: center; padding: 3rem;">
                <h3>What are the key symptoms of <strong>{disease}</strong>?</h3>
                <p style="color: #888;">Click to reveal answer</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🔄 Flip Card", use_container_width=True):
                st.session_state.flashcard_flipped = True
                st.rerun()

elif page == "🔬 Lab Tests":
    st.markdown(f'<h2>🔬 Laboratory Tests ({get_lab_count()} Tests)</h2>', unsafe_allow_html=True)
    
    # Add new lab test
    with st.expander("➕ Add New Lab Test"):
        with st.form("add_lab"):
            col1, col2 = st.columns(2)
            with col1:
                new_lab_name = st.text_input("Test Name")
                new_lab_category = st.text_input("Category")
            with col2:
                new_lab_normal = st.text_input("Normal Range")
                new_lab_unit = st.text_input("Unit")
            new_lab_desc = st.text_input("Description")
            
            if st.form_submit_button("✅ Add Test"):
                if new_lab_name:
                    custom_labs = load_custom_labs()
                    custom_labs[new_lab_name] = {
                        "category": new_lab_category,
                        "normal": new_lab_normal,
                        "unit": new_lab_unit,
                        "description": new_lab_desc
                    }
                    save_custom_labs(custom_labs)
                    st.success(f"✅ Added {new_lab_name}")
                    st.rerun()
    
    # Search and filter
    search = st.text_input("🔍 Search tests:", placeholder="Type test name...")
    category_filter = st.selectbox("Filter by category:", ["All"] + list(set(t.get("category", "") for t in get_all_labs().values())))
    
    all_labs = get_all_labs()
    
    # Edit mode
    if st.session_state.editing_lab:
        lab_name = st.session_state.editing_lab
        lab_info = all_labs.get(lab_name, {})
        
        st.markdown(f"### ✏️ Editing: {lab_name}")
        with st.form("edit_lab"):
            col1, col2 = st.columns(2)
            with col1:
                edit_normal = st.text_input("Normal Range", value=lab_info.get("normal", ""))
                edit_category = st.text_input("Category", value=lab_info.get("category", ""))
            with col2:
                edit_unit = st.text_input("Unit", value=lab_info.get("unit", ""))
            edit_desc = st.text_input("Description", value=lab_info.get("description", ""))
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("💾 Save Changes"):
                    custom_labs = load_custom_labs()
                    custom_labs[lab_name] = {
                        "category": edit_category,
                        "normal": edit_normal,
                        "unit": edit_unit,
                        "description": edit_desc
                    }
                    save_custom_labs(custom_labs)
                    st.session_state.editing_lab = None
                    st.success("✅ Updated!")
                    st.rerun()
            with col2:
                if st.form_submit_button("❌ Cancel"):
                    st.session_state.editing_lab = None
                    st.rerun()
    
    # Display tests in a table
    filtered_labs = {k: v for k, v in all_labs.items() if (not search or search.lower() in k.lower()) and (category_filter == "All" or v.get("category") == category_filter)}
    
    if filtered_labs:
        df_data = []
        for name, info in filtered_labs.items():
            df_data.append({
                "Test": name,
                "Category": info.get("category", ""),
                "Normal Range": info.get("normal", ""),
                "Unit": info.get("unit", ""),
                "Description": info.get("description", "")
            })
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True, height=400)
        
        # Edit and delete buttons
        selected_test = st.selectbox("Select test to edit/delete:", list(filtered_labs.keys()))
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✏️ Edit Selected", use_container_width=True):
                st.session_state.editing_lab = selected_test
                st.rerun()
        with col2:
            if st.button("🗑️ Delete Selected", use_container_width=True):
                custom_labs = load_custom_labs()
                if selected_test in custom_labs:
                    del custom_labs[selected_test]
                    save_custom_labs(custom_labs)
                    st.success(f"🗑️ Deleted {selected_test}")
                    st.rerun()
                else:
                    st.warning("Cannot delete default lab tests")
    else:
        st.info("No tests found matching your criteria")

elif page == "💊 Pharmacology":
    st.markdown(f'<h2>💊 Pharmacology Database ({get_drug_count()} Drugs)</h2>', unsafe_allow_html=True)
    
    # Add new drug
    with st.expander("➕ Add New Drug"):
        with st.form("add_drug"):
            col1, col2 = st.columns(2)
            with col1:
                new_drug_name = st.text_input("Drug Name")
                new_drug_category = st.text_input("Category")
                new_drug_dose = st.text_input("Dose")
            with col2:
                new_drug_mechanism = st.text_input("Mechanism of Action")
                new_drug_side_effects = st.text_input("Side Effects")
            new_drug_use = st.text_input("Clinical Use")
            
            if st.form_submit_button("✅ Add Drug"):
                if new_drug_name:
                    custom_drugs = load_custom_drugs()
                    custom_drugs[new_drug_name] = {
                        "category": new_drug_category,
                        "dose": new_drug_dose,
                        "mechanism": new_drug_mechanism,
                        "side_effects": new_drug_side_effects,
                        "use": new_drug_use
                    }
                    save_custom_drugs(custom_drugs)
                    st.success(f"✅ Added {new_drug_name}")
                    st.rerun()
    
    # Search
    search = st.text_input("🔍 Search drugs:", placeholder="Type drug name...")
    
    # Edit mode
    if st.session_state.editing_drug:
        drug_name = st.session_state.editing_drug
        all_drugs = get_all_drugs()
        drug_info = all_drugs.get(drug_name, {})
        
        st.markdown(f"### ✏️ Editing: {drug_name}")
        with st.form("edit_drug"):
            col1, col2 = st.columns(2)
            with col1:
                edit_dose = st.text_input("Dose", value=drug_info.get("dose", ""))
                edit_mechanism = st.text_input("Mechanism", value=drug_info.get("mechanism", ""))
            with col2:
                edit_category = st.text_input("Category", value=drug_info.get("category", ""))
                edit_side_effects = st.text_input("Side Effects", value=drug_info.get("side_effects", ""))
            edit_use = st.text_input("Clinical Use", value=drug_info.get("use", ""))
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("💾 Save Changes"):
                    custom_drugs = load_custom_drugs()
                    custom_drugs[drug_name] = {
                        "category": edit_category,
                        "dose": edit_dose,
                        "mechanism": edit_mechanism,
                        "side_effects": edit_side_effects,
                        "use": edit_use
                    }
                    save_custom_drugs(custom_drugs)
                    st.session_state.editing_drug = None
                    st.success("✅ Updated!")
                    st.rerun()
            with col2:
                if st.form_submit_button("❌ Cancel"):
                    st.session_state.editing_drug = None
                    st.rerun()
    
    # Display drugs by category
    all_drugs = get_all_drugs()
    categories = set()
    for info in all_drugs.values():
        categories.add(info.get("category", "Uncategorized"))
    
    for category in sorted(categories):
        cat_drugs = {k: v for k, v in all_drugs.items() if v.get("category") == category and (not search or search.lower() in k.lower())}
        if cat_drugs:
            with st.expander(f"📂 {category} ({len(cat_drugs)} drugs)"):
                df_data = []
                for name, info in cat_drugs.items():
                    df_data.append({
                        "Drug": name,
                        "Dose": info.get("dose", ""),
                        "Mechanism": info.get("mechanism", ""),
                        "Side Effects": info.get("side_effects", ""),
                        "Use": info.get("use", "")
                    })
                df = pd.DataFrame(df_data)
                st.dataframe(df, use_container_width=True)
                
                selected_drug = st.selectbox(f"Select drug in {category}:", list(cat_drugs.keys()), key=f"select_{category}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"✏️ Edit", key=f"edit_{category}", use_container_width=True):
                        st.session_state.editing_drug = selected_drug
                        st.rerun()
                with col2:
                    if st.button(f"🗑️ Delete", key=f"delete_{category}", use_container_width=True):
                        custom_drugs = load_custom_drugs()
                        if selected_drug in custom_drugs:
                            del custom_drugs[selected_drug]
                            save_custom_drugs(custom_drugs)
                            st.success(f"🗑️ Deleted {selected_drug}")
                            st.rerun()
                        else:
                            st.warning("Cannot delete default drugs")

elif page == "⚠️ Drug Interactions":
    st.markdown('<h2>⚠️ Drug Interaction Checker</h2>', unsafe_allow_html=True)
    
    all_drug_names = list(get_all_drugs().keys())
    selected_drugs = st.multiselect("Select drugs to check:", all_drug_names, placeholder="Choose 2 or more drugs...")
    
    if len(selected_drugs) >= 2:
        interactions = check_drug_interactions(selected_drugs)
        if interactions:
            for ix in interactions:
                severity_color = {"Critical": "#ef4444", "High": "#f59e0b", "Moderate": "#06b6d4"}
                color = severity_color.get(ix["severity"], "#6b7280")
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.03); padding: 1rem; border-radius: 12px; border-left: 4px solid {color}; margin: 0.5rem 0;">
                    <h4>{ix['drug1']} + {ix['drug2']}</h4>
                    <p><strong>Severity:</strong> <span style="color:{color}">{ix['severity']}</span></p>
                    <p><strong>Effect:</strong> {ix['effect']}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ No known interactions found")
    else:
        st.info("Select at least 2 drugs to check for interactions")

elif page == "🏆 Leaderboard":
    st.markdown('<h2>🏆 Global Leaderboard</h2>', unsafe_allow_html=True)
    
    df = get_leaderboard_df()
    if not df.empty:
        for i, (_, row) in enumerate(df.iterrows()):
            rank = i + 1
            medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"#{rank}"
            card_class = "leaderboard-top1" if rank == 1 else "leaderboard-top2" if rank == 2 else "leaderboard-top3" if rank == 3 else ""
            
            st.markdown(f"""
            <div class="glass-card" style="margin: 0.5rem 0; border-color: {'#fbbf24' if rank == 1 else '#94a3b8' if rank == 2 else '#d97706' if rank == 3 else 'rgba(99,102,241,0.2)'}">
                <h3>{medal} {row['username']}</h3>
                <p>⭐ {row['xp_points']} XP | 📊 Quiz: {row['quiz_score']} | 🩺 Cases: {row['cases_solved']} | 🎓 Level {row.get('level', 1)}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No data yet. Start solving cases and taking quizzes!")

elif page == "👥 Study Rooms":
    st.markdown('<h2>👥 Collaborative Study Rooms</h2>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Create Room", "Join Room"])
    
    with tab1:
        with st.form("create_room"):
            room_name = st.text_input("Room Name:", placeholder="e.g., Cardiology Study Group")
            if st.form_submit_button("✅ Create Room", type="primary"):
                room_id = create_study_room(room_name, st.session_state.username)
                st.session_state.current_room_id = room_id
                st.success(f"Room created! Share this ID: **{room_id}**")
                st.rerun()
    
    with tab2:
        with st.form("join_room"):
            room_id = st.text_input("Room ID:", placeholder="Enter room ID to join")
            if st.form_submit_button("🚪 Join Room", type="primary"):
                if join_study_room(room_id, st.session_state.username):
                    st.session_state.current_room_id = room_id
                    st.success("Joined successfully!")
                    st.rerun()
                else:
                    st.error("Room not found")
    
    if st.session_state.current_room_id:
        rooms = load_study_rooms()
        room = rooms.get(st.session_state.current_room_id)
        if room:
            st.markdown(f"### 📚 {room['name']} ({len(room['members'])} members)")
            
            for msg in room["messages"][-20:]:
                is_own = msg["username"] == st.session_state.username
                st.markdown(f"""
                <div style="background: {'rgba(99,102,241,0.1)' if is_own else 'rgba(255,255,255,0.03)'}; padding: 0.8rem; border-radius: 10px; margin: 0.3rem 0;">
                    <strong>{msg['username']}:</strong> {msg['message']}
                </div>
                """, unsafe_allow_html=True)
            
            with st.form("send_msg"):
                msg = st.text_input("Message:", placeholder="Type your message...")
                if st.form_submit_button("📤 Send"):
                    send_room_message(st.session_state.current_room_id, st.session_state.username, msg)
                    st.rerun()

elif page == "📰 Medical News":
    st.markdown('<h2>📰 Latest Medical News</h2>', unsafe_allow_html=True)
    
    news = fetch_medical_news()
    for item in news:
        st.markdown(f"""
        <div class="glass-card" style="margin: 1rem 0;">
            <h4>📰 {item['title']}</h4>
            <p>{item['summary']}</p>
            <p style="color: #888; font-size: 0.8rem;">📅 {item['date']} | 📚 {item['source']}</p>
        </div>
        """, unsafe_allow_html=True)

elif page == "🔬 Microscope":
    st.markdown('<h2>🔬 Virtual Microscope Simulator</h2>', unsafe_allow_html=True)
    
    cell_type = st.selectbox("Select cell type:", ["RBC", "WBC", "Platelets"])
    if st.button("🔬 View Sample", type="primary", use_container_width=True):
        generate_microscope_view(cell_type)

elif page == "📝 Clinical Notes":
    st.markdown('<h2>📝 Clinical Notes</h2>', unsafe_allow_html=True)
    
    with st.form("add_note"):
        patient = st.text_input("Patient Name/ID:")
        note = st.text_area("Clinical Note:", placeholder="Enter your clinical observations...")
        if st.form_submit_button("💾 Save Note", type="primary"):
            add_clinical_note(st.session_state.username, {"patient": patient, "note": note})
            st.success("✅ Note saved!")
            st.rerun()
    
    notes = get_clinical_notes(st.session_state.username)
    for note in reversed(notes[-20:]):
        st.markdown(f"""
        <div class="glass-card" style="margin: 0.5rem 0;">
            <p><strong>Patient:</strong> {note.get('patient', 'N/A')}</p>
            <p>{note.get('note', '')}</p>
            <p style="color: #888; font-size: 0.8rem;">📅 {note.get('timestamp', '')[:10]}</p>
        </div>
        """, unsafe_allow_html=True)

elif page == "🧠 AI Assistant":
    st.markdown('<h2>🧠 AI-Powered Symptom Checker</h2>', unsafe_allow_html=True)
    
    symptoms_input = st.text_area("Enter symptoms (comma-separated):", placeholder="e.g., fever, headache, fatigue, cough")
    
    if st.button("🔍 Analyze Symptoms", type="primary", use_container_width=True) and symptoms_input:
        symptoms_list = [s.strip().lower() for s in symptoms_input.split(",") if s.strip()]
        results = []
        
        for disease, info in DISEASE_DATABASE.items():
            disease_symptoms = [s.lower() for s in info["symptoms"]]
            matches = len(set(symptoms_list) & set(disease_symptoms))
            if matches > 0:
                pct = (matches / len(disease_symptoms)) * 100
                results.append({"disease": disease, "match": round(pct, 1), "risk": info.get("risk", "Low")})
        
        results.sort(key=lambda x: x["match"], reverse=True)
        
        st.markdown("### 📊 Top Matches")
        for r in results[:5]:
            st.markdown(f"""
            <div class="glass-card" style="margin: 0.5rem 0;">
                <h4>{r['disease']} - <span style="color:{get_risk_color(r['risk'])}">{r['risk']} Risk</span></h4>
                <p>Match: {r['match']}%</p>
            </div>
            """, unsafe_allow_html=True)

elif page == "🏆 Achievements":
    st.markdown('<h2>🏆 Achievements & Badges</h2>', unsafe_allow_html=True)
    
    achievements = [
        {"name": "First Case Solved", "icon": "🩺", "condition": st.session_state.total_cases_solved >= 1},
        {"name": "Case Master", "icon": "🏆", "condition": st.session_state.total_cases_solved >= 20},
        {"name": "Quiz Apprentice", "icon": "📝", "condition": st.session_state.quiz_score >= 10},
        {"name": "Quiz Expert", "icon": "🎓", "condition": st.session_state.quiz_score >= 50},
        {"name": "Quiz Legend", "icon": "👑", "condition": st.session_state.quiz_score >= 100},
        {"name": "7-Day Streak", "icon": "🔥", "condition": st.session_state.streak_days >= 7},
        {"name": "30-Day Streak", "icon": "💪", "condition": st.session_state.streak_days >= 30},
        {"name": "Diagnostician", "icon": "🔍", "condition": st.session_state.correct_diagnoses >= 5},
        {"name": "XP Hunter", "icon": "⭐", "condition": st.session_state.xp_points >= 100},
        {"name": "XP Master", "icon": "💎", "condition": st.session_state.xp_points >= 500}
    ]
    
    for ach in achievements:
        if ach["condition"] and ach["name"] not in st.session_state.achievements:
            st.session_state.achievements.append(ach["name"])
    
    cols = st.columns(3)
    for i, ach in enumerate(achievements):
        with cols[i % 3]:
            earned = ach["name"] in st.session_state.achievements
            st.markdown(f"""
            <div class="glass-card" style="text-align: center; opacity: {1 if earned else 0.5};">
                <div style="font-size: 3rem;">{ach['icon']}</div>
                <h4>{ach['name']}</h4>
                <span class="badge {'badge-success' if earned else 'badge-warning'}">{'✅ Earned' if earned else '🔒 Locked'}</span>
            </div>
            """, unsafe_allow_html=True)

# ================================
# 13. FOOTER
# ================================
st.markdown("---")
st.markdown(f"""
<div class="app-footer">
    <h3 style="background: linear-gradient(135deg, #6366f1, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
        🩺 Dr.Danyal Medical Training Platform v9.0
    </h3>
    <p style="color: rgba(255,255,255,0.6);">
        {get_disease_count()} Diseases | {get_drug_count()} Medications | {get_lab_count()} Lab Tests
    </p>
    <p style="color: rgba(255,255,255,0.3); font-size: 0.8rem;">
        © {datetime.now().year} Dr.Danyal. All rights reserved.
    </p>
</div>
""", unsafe_allow_html=True)
