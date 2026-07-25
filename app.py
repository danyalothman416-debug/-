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
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors
from sklearn.feature_extraction.text import TfidfVectorizer
import warnings
warnings.filterwarnings('ignore')
import sqlite3
import os
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import hashlib
import uuid

# ================================
# 1. ڕێکخستنی ڕووکاری پەڕە
# ================================
st.set_page_config(
    page_title="Dr.Danyal - ڕاهێنەری پزیشکی Pro Max",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================================
# 1.5 سیستەمی لۆگین و خەزنکردنی داتا
# ================================
DATA_DIR = "user_data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

USERS_FILE = os.path.join(DATA_DIR, "users.json")

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def load_users() -> Dict:
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_users(users: Dict):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

def create_user(username: str, password: str) -> bool:
    users = load_users()
    if username in users:
        return False
    users[username] = {
        "password": hash_password(password),
        "created_at": datetime.now().isoformat(),
        "custom_lab_tests": {},
        "custom_drugs": {}
    }
    save_users(users)
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

def auto_save():
    if st.session_state.get('logged_in', False):
        save_user_data(st.session_state.username, {
            "custom_lab_tests": st.session_state.custom_lab_tests,
            "custom_drugs": st.session_state.custom_drugs
        })

# دەستپێکردنی ستەیتی لۆگین
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'custom_lab_tests' not in st.session_state:
    st.session_state.custom_lab_tests = {}
if 'custom_drugs' not in st.session_state:
    st.session_state.custom_drugs = {}

# ================================
# 2. CSS و ستایلە پێشکەوتووەکان
# ================================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e, #0f0c29);
        min-height: 100vh;
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
    }
    @keyframes gradientBG { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    .main {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border-radius: 35px;
        padding: 2.5rem;
        margin: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.05);
        box-shadow: 0 30px 80px rgba(0, 0, 0, 0.4);
        animation: fadeIn 1s ease-out;
    }
    @keyframes fadeIn { from { opacity: 0; transform: scale(0.95); } to { opacity: 1; transform: scale(1); } }
    .logo-container { display: flex; align-items: center; justify-content: center; gap: 15px; animation: float 4s ease-in-out infinite; background: rgba(255,255,255,0.05); padding: 15px 30px; border-radius: 60px; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); margin-bottom: 20px; box-shadow: 0 10px 40px rgba(102,126,234,0.2); }
    .logo-icon { font-size: 4rem; animation: pulse 2s infinite; filter: drop-shadow(0 0 20px rgba(102,126,234,0.5)); }
    .logo-text { font-size: 2.2rem; font-weight: bold; background: linear-gradient(135deg, #667eea, #f093fb, #4facfe, #667eea); background-size: 300% 300%; animation: textShimmer 4s ease infinite; -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; letter-spacing: 1px; }
    @keyframes textShimmer { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    @keyframes float { 0% { transform: translateY(0px); } 50% { transform: translateY(-12px); } 100% { transform: translateY(0px); } }
    @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.05); } 100% { transform: scale(1); } }
    .main-header { font-size: 3.8rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 30%, #f093fb 60%, #4facfe 100%); background-size: 300% 300%; animation: headerGradient 4s ease infinite; color: white; text-align: center; padding: 2.8rem; border-radius: 35px; margin-bottom: 2.5rem; box-shadow: 0 25px 70px rgba(102, 126, 234, 0.5); border: 1px solid rgba(255, 255, 255, 0.15); text-shadow: 0 4px 20px rgba(0,0,0,0.3); position: relative; overflow: hidden; }
    @keyframes headerGradient { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    .case-card { background: rgba(255, 255, 255, 0.06); backdrop-filter: blur(15px); padding: 2.2rem; border-radius: 28px; border-left: 8px solid #667eea; margin: 1.2rem 0; transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1); box-shadow: 0 10px 40px rgba(0,0,0,0.2); border: 1px solid rgba(255, 255, 255, 0.06); animation: slideInLeft 0.6s ease-out; color: #fff; position: relative; overflow: hidden; }
    .case-card:hover { transform: translateY(-10px) scale(1.01); box-shadow: 0 25px 70px rgba(102, 126, 234, 0.3); border-color: #764ba2; background: rgba(255, 255, 255, 0.1); }
    .success-box { background: linear-gradient(135deg, rgba(40, 167, 69, 0.3), rgba(40, 167, 69, 0.08)); backdrop-filter: blur(15px); padding: 2.2rem; border-radius: 25px; border-left: 8px solid #28a745; box-shadow: 0 10px 45px rgba(40, 167, 69, 0.2); animation: pulse 2s infinite; color: #fff; border: 1px solid rgba(40, 167, 69, 0.15); }
    .error-box { background: linear-gradient(135deg, rgba(220, 53, 69, 0.3), rgba(220, 53, 69, 0.08)); backdrop-filter: blur(15px); padding: 2.2rem; border-radius: 25px; border-left: 8px solid #dc3545; box-shadow: 0 10px 45px rgba(220, 53, 69, 0.2); color: #fff; border: 1px solid rgba(220, 53, 69, 0.15); }
    .quiz-card { background: rgba(255, 255, 255, 0.06); backdrop-filter: blur(20px); padding: 3rem; border-radius: 32px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); margin: 1.5rem 0; border: 2px solid rgba(102, 126, 234, 0.15); transition: all 0.4s ease; color: #fff; position: relative; overflow: hidden; }
    .progress-container { background: rgba(255, 255, 255, 0.08); border-radius: 25px; height: 22px; overflow: hidden; margin: 1rem 0; box-shadow: inset 0 3px 8px rgba(0,0,0,0.2); position: relative; }
    .progress-fill { height: 100%; background: linear-gradient(90deg, #667eea, #764ba2, #f093fb, #4facfe, #667eea); background-size: 400% 100%; border-radius: 25px; transition: width 1.5s cubic-bezier(0.4, 0, 0.2, 1); }
    .stat-card { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(15px); padding: 2.2rem; border-radius: 25px; box-shadow: 0 10px 40px rgba(0,0,0,0.15); text-align: center; border-top: 6px solid #667eea; transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1); color: #fff; border: 1px solid rgba(255, 255, 255, 0.04); cursor: default; animation: float 6s ease-in-out infinite; }
    .stat-number { font-size: 4rem; font-weight: bold; background: linear-gradient(135deg, #667eea, #f093fb, #4facfe); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
    .badge-level { display: inline-block; padding: 0.6rem 2.2rem; border-radius: 40px; font-weight: bold; background: linear-gradient(135deg, #667eea, #f093fb); color: white; box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4); animation: pulse 3s infinite; font-size: 1.2rem; letter-spacing: 1px; }
    .footer-style { text-align: center; padding: 3.5rem; background: rgba(255, 255, 255, 0.04); backdrop-filter: blur(20px); color: white; border-radius: 35px; margin-top: 3rem; box-shadow: 0 25px 60px rgba(0,0,0,0.2); border: 1px solid rgba(255, 255, 255, 0.04); animation: fadeIn 1s ease-out; }
    .drug-card { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(15px); padding: 1.8rem; border-radius: 22px; border: 2px solid rgba(102, 126, 234, 0.08); margin: 0.8rem 0; transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1); color: #fff; position: relative; }
    .drug-card:hover { transform: translateY(-6px) scale(1.01); border-color: #764ba2; box-shadow: 0 15px 50px rgba(102, 126, 234, 0.2); background: rgba(255, 255, 255, 0.1); }
    .lab-result-card { background: rgba(0, 0, 0, 0.2); padding: 1.2rem; border-radius: 15px; margin: 0.5rem 0; border-left: 4px solid #667eea; transition: all 0.3s ease; }
    .lab-result-card:hover { background: rgba(0, 0, 0, 0.3); transform: translateX(5px); }
    .lab-normal { border-left-color: #28a745; } .lab-high { border-left-color: #dc3545; } .lab-low { border-left-color: #ffc107; }
    .login-container { display: flex; justify-content: center; align-items: center; min-height: 80vh; }
    .login-box { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(30px); padding: 3rem; border-radius: 30px; border: 1px solid rgba(255, 255, 255, 0.1); box-shadow: 0 30px 80px rgba(0, 0, 0, 0.4); text-align: center; max-width: 450px; width: 100%; animation: fadeIn 1s ease-out; }
</style>
""", unsafe_allow_html=True)

# ================================
# 3. سیستەمی ئاستەکان (Levels)
# ================================
LEVELS = {
    1: {"name": "سەرەتایی (Beginner)", "min_score": 0, "max_score": 9, "color": "#28a745", "quizzes": 50, "icon": "🌱", "description": "دەستپێکی ڕێگای پزیشکی", "requirements": "هیچ"},
    2: {"name": "فێرخواز (Learner)", "min_score": 10, "max_score": 29, "color": "#17a2b8", "quizzes": 100, "icon": "📖", "description": "فێربوونی بنەماکانی پزیشکی", "requirements": "تەواوکردنی ئاست ١"},
    3: {"name": "پێشکەوتوو (Advanced)", "min_score": 30, "max_score": 59, "color": "#ffc107", "quizzes": 150, "icon": "🚀", "description": "پێشکەوتن لە زانستە پزیشکییەکان", "requirements": "تەواوکردنی ئاست ٢"},
    4: {"name": "شارەزا (Expert)", "min_score": 60, "max_score": 89, "color": "#ff9f1c", "quizzes": 200, "icon": "🏆", "description": "شارەزایی لە نەخۆشییەکان", "requirements": "تەواوکردنی ئاست ٣"},
    5: {"name": "پزیشک (Master)", "min_score": 90, "max_score": 100, "color": "#dc3545", "quizzes": 500, "icon": "👨‍⚕️", "description": "پزیشکی لێهاتوو و شارەزا", "requirements": "تەواوکردنی ئاست ٤"}
}

def get_user_level(score: int) -> int:
    for level, info in LEVELS.items():
        if info["min_score"] <= score <= info["max_score"]:
            return level
    return 1

def get_level_info(level: int) -> Dict:
    return LEVELS.get(level, LEVELS[1])

def get_next_level(level: int) -> int:
    return min(level + 1, 5)

def get_level_progress(score: int) -> float:
    level = get_user_level(score)
    if level == 5: return 100.0
    current = LEVELS[level]
    next_level = get_next_level(level)
    if next_level == 5:
        total = 100 - current["min_score"]
        achieved = score - current["min_score"]
        return min((achieved / total) * 100, 100)
    total = LEVELS[next_level]["min_score"] - current["min_score"]
    achieved = score - current["min_score"]
    return min((achieved / total) * 100, 100)

def get_level_icon(level: int) -> str:
    return get_level_info(level).get("icon", "📚")

# ================================
# 4. داتابەسی نەخۆشییەکان (نموونە کەمکراوەتەوە بۆ جێگیربوونی کۆد، بەڵام سیستەمەکە تەواوە)
# ================================
DISEASE_DATABASE = {
    "شەکرەی جۆری 2": {
        "نیشانەکان": ["تینوویەتی زۆر", "میزی زۆر", "ماندوویی", "کێش کەمبوونەوە", "بینی تەڵخ", "برسێتی زۆر", "پێست وشک"],
        "پشکنینەکان": {"FBS": ">126 mg/dL", "HbA1c": ">6.5%", "OGTT": ">200 mg/dL", "C-peptide": "نۆرماڵ یان بەرز", "Insulin": "بەرز"},
        "چارەسەر": ["مێتفۆرمین 500mg", "گۆڕینی شێوازی ژیان", "وەرزشی ڕۆژانە 30 خولەک", "شێوازی خواردن کەم کاربۆهیدرات", "پێوانەکردنی شەکر"],
        "ئاستی مەترسی": "مەترسیدار",
        "تایبەتمەندی": "FBS بەرز + HbA1c بەرز + تەمەن > 40 ساڵ",
        "ڕێپیشگیری": ["شێوازی خواردنی تەندروست", "چالاکی جەستەیی", "پێوانەکردنی شەکر بەردەوام", "کەمکردنەوەی کێش"],
        "گروپی تەمەن": "تەمەن مامناوەند و پیر",
        "ڕێژەی تووشبوون": "8.5%",
        "جۆری نەخۆشی": "مێتابۆلیک"
    },
    "پەستانی خوێنی سەرەتایی": {
        "نیشانەکان": ["سەرئێشە", "سەرگێژخواردن", "فشاری پشت چاو", "خێرالێدانی دڵ", "ئەرەقەکردن", "مەلە", "خوێن لە لووتدا"],
        "پشکنینەکان": {"BP": ">140/90 mmHg", "ECG": "Left ventricular hypertrophy", "Creatinine": "نۆرماڵ", "Potassium": "نۆرماڵ", "Echocardiogram": "نۆرماڵ"},
        "چارەسەر": ["کاپتۆپریل 25mg", "کەمکردنەوەی نمەک", "وەرزشی ئیروبیک", "کەمکردنەوەی کێش", "پێوانەکردنی BP"],
        "ئاستی مەترسی": "مامناوەند",
        "تایبەتمەندی": "BP بەرز بەبێ هۆکاری دیکە",
        "ڕێپیشگیری": ["پێوانەکردنی BP بەردەوام", "شێوازی خواردنی کەم نمەک", "ڕاهێنانی ڕۆژانە"],
        "گروپی تەمەن": "هەموو تەمەنەکان",
        "ڕێژەی تووشبوون": "25%",
        "جۆری نەخۆشی": "دڵ و خوێن"
    },
    "هەوکردنی سییەکان (Pneumonia)": {
        "نیشانەکان": ["تا", "کۆخە", "هەناسەدان بە زەحمەت", "ئازاری سنگ", "ڕژانی لووت", "ماندوویی", "ئارەقەکردن", "لەرزین"],
        "پشکنینەکان": {"Chest X-ray": "Consolidation", "CRP": "بەرز >10", "WBC": "بەرز >11", "Sputum culture": "بەکتریا", "O2 saturation": "کەم"},
        "چارەسەر": ["ئەمۆکسیسیلین 500mg", "ئۆکسجین", "شلەمەنی", "دەرمانی دژە تا", "پشوو"],
        "ئاستی مەترسی": "مامناوەند",
        "تایبەتمەندی": "Consolidation لە X-ray + CRP بەرز",
        "ڕێپیشگیری": ["کوتان (Vaccination)", "دەستشۆردن", "دوورکەوتنەوە لە کەسانی تووشبوو"],
        "گروپی تەمەن": "هەموو تەمەنەکان",
        "ڕێژەی تووشبوون": "3%",
        "جۆری نەخۆشی": "هەوکردن"
    }
}

# ================================
# 5. داتابەسی پشکنینەکانی تاقیگە
# ================================
LAB_TESTS = {}
blood_tests = {
    "CBC": {"گروپ": "خوێن", "نۆرماڵ": (4.0, 11.0), "یەکە": "x10³/µL", "تەفسیر": "خڕۆکە سپیەکان", "ئامێر": "ئۆتۆماتیک سێل کاونتر (Sysmex XN-9000)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "Hemoglobin": {"گروپ": "خوێن", "نۆرماڵ": (12.0, 16.0), "یەکە": "g/dL", "تەفسیر": "هیمۆگلۆبین", "ئامێر": "هیمۆگلۆبینۆمیتەر (HemoCue 201+)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
}
biochem_tests = {
    "Glucose": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (70, 126), "یەکە": "mg/dL", "تەفسیر": "شەکری خوێن", "ئامێر": "گلوکۆمیتەر (Roche Cobas c502)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "HbA1c": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (4.0, 5.6), "یەکە": "%", "تەفسیر": "شەکری درێژخایەن", "ئامێر": "HPLC (Bio-Rad D-100)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
}
for test_dict in [blood_tests, biochem_tests]:
    LAB_TESTS.update(test_dict)

# ================================
# 6. داتابەسی دەرمانەکان
# ================================
DRUG_DATABASE = {
    "دژە پەستانی خوێن": {
        "کاپتۆپریل": {"ڕێژە": "25-50mg", "میکانیزم": "ACE inhibitor", "کاریگەری لاوەکی": "کۆخە, سەرگێژخواردن", "پێچەوانە": "حەملی دووگانی", "وەسف": "دەرمانی ACE inhibitor کە پەستانی خوێن کەم دەکاتەوە بە فراوانکردنی خوێنبەرەکان", "بۆچی": "بۆ کەمکردنەوەی پەستانی خوێن و پاراستنی گورچیلە لە نەخۆشانی شەکرە", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    },
    "دژە شەکرە": {
        "مێتفۆرمین": {"ڕێژە": "500-2000mg", "میکانیزم": "Biguanide", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "دەرمانی هێڵی یەکەم بۆ شەکرەی جۆری ٢ - کەمکردنی بەرهەمهێنانی شەکر لە جگەر و زیادکردنی هەستی ئەنسولین", "بۆچی": "بۆ کۆنتڕۆڵکردنی شەکری خوێن لە نەخۆشانی شەکرەی جۆری ٢", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    },
    "دژە کۆخە و هەوکردن": {
        "ئەمۆکسیسیلین": {"ڕێژە": "500mg", "میکانیزم": "Beta-lactam", "کاریگەری لاوەکی": "زکچوون", "پێچەوانە": "هەستیاری پێنیسیلین", "وەسف": "ئەنتیبایۆتیکی پێنیسیلین بۆ هەوکردنی بەکتریایی", "بۆچی": "بۆ هەوکردنی سییەکان، گەدە، میز", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    }
}

def get_drug_count() -> int:
    total = 0
    for category in DRUG_DATABASE.values():
        total += len(category)
    return total

def get_disease_count() -> int:
    return len(DISEASE_DATABASE)

def get_lab_count() -> int:
    return len(LAB_TESTS)

# ================================
# 7. دروستکردنی کویز
# ================================
def generate_quizzes_by_level():
    quizzes = []
    level1_questions = [
        {"پرسیار": "نیشانەی سەرەکی شەکرەی جۆری ٢ چییە؟", "هەڵبژاردەکان": ["تینوویەتی زۆر", "سەرئێشە", "ئازاری سنگ", "کۆخە"], "وەڵامی ڕاست": 0},
        {"پرسیار": "پەستانی خوێنی نۆرماڵ چەندە؟", "هەڵبژاردەکان": ["120/80", "140/90", "160/100", "180/110"], "وەڵامی ڕاست": 0},
    ]
    level_questions = {1: level1_questions}
    for level, questions in level_questions.items():
        for i in range(LEVELS[level]["quizzes"]):
            q = random.choice(questions)
            quizzes.append({
                "پرسیار": q["پرسیار"], "هەڵبژاردەکان": q["هەڵبژاردەکان"], "وەڵامی ڕاست": q["وەڵامی ڕاست"],
                "ئاست": level, "ئاستی ناو": LEVELS[level]["name"], "ڕوونکردنەوە": f"ئاستی {LEVELS[level]['name']} - کویز ژمارە {i+1}"
            })
    return quizzes

MEDICAL_QUIZZES = generate_quizzes_by_level()

def get_quiz_count() -> int:
    return len(MEDICAL_QUIZZES)

# ================================
# 8. فانکشنە یارمەتیدەرەکان
# ================================
def calculate_risk_score(disease: str, age: int, gender: str, symptoms: List[str] = None) -> int:
    base_risk = {"زۆر مەترسیدار": 80, "مەترسیدار": 60, "مامناوەند": 40, "کەم": 20}
    disease_info = DISEASE_DATABASE.get(disease, {})
    risk = base_risk.get(disease_info.get('ئاستی مەترسی', 'کەم'), 40)
    if age > 60: risk += 15
    if symptoms: risk += min(len(symptoms) * 3, 15)
    return min(risk, 100)

def get_age_group(age: int) -> str:
    if age < 18: return "منداڵ"
    elif age < 40: return "گەنج"
    elif age < 60: return "تەمەن مامناوەند"
    else: return "پیر"

def get_risk_color(risk_level: str) -> str:
    colors = {"زۆر مەترسیدار": "#ff6b6b", "مەترسیدار": "#ffd93d", "مامناوەند": "#ffc107", "کەم": "#6bcb77"}
    return colors.get(risk_level, "#6c757d")

def analyze_lab_result(test_name: str, value: float, all_tests: Dict) -> Dict:
    if test_name not in all_tests:
        return {"status": "نەزانراو", "color": "#6c757d", "interpretation": "پشکنین نەدۆزرایەوە"}
    low, high = all_tests[test_name]["نۆرماڵ"]
    if value < low:
        return {"status": "نزم", "color": "#ffc107", "interpretation": f"{all_tests[test_name]['تەفسیر']} نزمە (نزمتر لە نۆرماڵ)"}
    elif value > high:
        return {"status": "بەرز", "color": "#dc3545", "interpretation": f"{all_tests[test_name]['تەفسیر']} بەرزە (بەرزتر لە نۆرماڵ)"}
    else:
        return {"status": "نۆرماڵ", "color": "#28a745", "interpretation": f"{all_tests[test_name]['تەفسیر']} نۆرماڵە (لە مەودای نۆرماڵدایە)"}

# ================================
# 9. ستەیتەکانی ئەپ
# ================================
if 'current_case' not in st.session_state: st.session_state.current_case = None
if 'diagnosis_submitted' not in st.session_state: st.session_state.diagnosis_submitted = False
if 'quiz_index' not in st.session_state: st.session_state.quiz_index = 0
if 'quiz_score' not in st.session_state: st.session_state.quiz_score = 0
if 'quiz_completed' not in st.session_state: st.session_state.quiz_completed = False
if 'total_cases_solved' not in st.session_state: st.session_state.total_cases_solved = 0
if 'correct_diagnoses' not in st.session_state: st.session_state.correct_diagnoses = 0
if 'last_activity' not in st.session_state: st.session_state.last_activity = datetime.now()
if 'student_level' not in st.session_state: st.session_state.student_level = "ساڵی یەکەم"
if 'streak_days' not in st.session_state: st.session_state.streak_days = 0
if 'last_study_date' not in st.session_state: st.session_state.last_study_date = datetime.now().date()
if 'achievements' not in st.session_state: st.session_state.achievements = []
if 'study_time' not in st.session_state: st.session_state.study_time = 0
if 'level_1_done' not in st.session_state: st.session_state.level_1_done = 0

# ================================
# 10. پەڕەی لۆگین
# ================================
if not st.session_state.logged_in:
    st.markdown('<div class="login-container"><div class="login-box">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:4rem;text-align:center;">🩺</div><h2 style="color:white;text-align:center;">Dr.Danyal</h2><p style="color:rgba(255,255,255,0.6);text-align:center;">تکایە بچۆ ژوورەوە یان هەژمارێکی نوێ دروست بکە</p>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["چوونە ژوورەوە", "دروستکردنی هەژمار"])
    with tab1:
        with st.form("login_form"):
            login_username = st.text_input("👤 ناوی بەکارهێنەری", key="login_username")
            login_password = st.text_input("🔒 وشەی نهێنی", type="password", key="login_password")
            if st.form_submit_button("🚪 چوونە ژوورەوە", type="primary"):
                if authenticate_user(login_username, login_password):
                    st.session_state.logged_in = True
                    st.session_state.username = login_username
                    user_data = load_user_data(login_username)
                    st.session_state.custom_lab_tests = user_data.get("custom_lab_tests", {})
                    st.session_state.custom_drugs = user_data.get("custom_drugs", {})
                    st.rerun()
                else:
                    st.error("❌ ناوی بەکارهێنەری یان وشەی نهێنی هەڵەیە")
    with tab2:
        with st.form("register_form"):
            new_username = st.text_input("👤 ناوی بەکارهێنەری نوێ", key="new_username")
            new_password = st.text_input("🔒 وشەی نهێنی", type="password", key="new_password")
            if st.form_submit_button("📝 دروستکردنی هەژمار", type="primary"):
                if new_username and new_password and len(new_password) >= 4:
                    if create_user(new_username, new_password):
                        st.success("✅ هەژمارەکەت دروست کرا! ئێستا بچۆ ژوورەوە")
                    else:
                        st.error("❌ ئەم ناوە پێشتر بەکارهاتووە")
                else:
                    st.error("تکایە ناو و وشەی نهێنی (لانیکەم ٤ پیت) بنووسە")
    st.markdown('</div></div>', unsafe_allow_html=True)
    st.stop()

# ================================
# 11. سایدبار
# ================================
with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center;padding:10px 0;">
        <div style="font-size:3rem;">🩺</div>
        <div style="font-size:1.5rem;font-weight:bold;color:white;">Dr.Danyal</div>
        <div style="color:rgba(255,255,255,0.5);font-size:0.8rem;">ڕاهێنەری پزیشکی Pro Max</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"**👤 بەکارهێنەر:** {st.session_state.username}")
    st.markdown(f"**🔬 پشکنین:** {len(LAB_TESTS) + len(st.session_state.custom_lab_tests)}")
    st.markdown(f"**💊 دەرمان:** {get_drug_count() + len(st.session_state.custom_drugs)}")
    st.markdown("---")
    page = st.radio("📋 بەشەکان:", ["🏠 داشبۆرد", "📚 نەخۆشییەکان", "🩺 شیکاری کەیس", "📝 کویز", "🔬 تاقیگە", "💊 فارماکۆلۆجی", "🏆 دەستکەوتەکان"])
    st.markdown("---")
    if st.button("🚪 چوونە دەرەوە", type="primary"):
        auto_save()
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.custom_lab_tests = {}
        st.session_state.custom_drugs = {}
        st.rerun()

# ================================
# 12. پەڕەی داشبۆرد
# ================================
if page == "🏠 داشبۆرد":
    st.markdown('<div class="main"><h1 class="main-header">🎓 ڕاهێنەری پزیشکی Pro Max</h1></div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.markdown(f'<div class="stat-card"><h3>📚</h3><div class="stat-number">{get_disease_count()}</div><p>نەخۆشی</p></div>', unsafe_allow_html=True)
    with col2: st.markdown(f'<div class="stat-card"><h3>💊</h3><div class="stat-number">{get_drug_count() + len(st.session_state.custom_drugs)}</div><p>دەرمان</p></div>', unsafe_allow_html=True)
    with col3: st.markdown(f'<div class="stat-card"><h3>🔬</h3><div class="stat-number">{get_lab_count() + len(st.session_state.custom_lab_tests)}</div><p>پشکنین</p></div>', unsafe_allow_html=True)
    with col4: st.markdown(f'<div class="stat-card"><h3>📝</h3><div class="stat-number">{st.session_state.quiz_score}/100</div><p>کویز</p></div>', unsafe_allow_html=True)

# ================================
# 13. پەڕەی تاقیگە (زیادکردن، دەستکاری، سڕینەوە)
# ================================
elif page == "🔬 تاقیگە":
    st.markdown('<div class="main"><h2>🔬 تاقیگەی ڤێرچواڵ - Dr.Danyal</h2><p style="color:#aaa;">پشکنینەکانی تاقیگە لەگەڵ ئامێرەکان و تێبینی تایبەتی خۆت</p></div>', unsafe_allow_html=True)
    
    all_lab_tests = {**LAB_TESTS, **st.session_state.custom_lab_tests}
    
    st.markdown("### ➕ پشکنینێکی نوێ زیاد بکە (بۆ هەمیشە خەزن دەکرێت)")
    with st.form("add_lab_test_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            new_lab_name = st.text_input("ناوی پشکنین:")
            new_lab_group = st.selectbox("گروپ:", ["گشتی", "خوێن", "بایۆکیمیایی", "دڵ", "هەوکردن", "هۆرمۆن", "میز", "ڤیتامین", "معدن"])
            new_lab_low = st.number_input("نزمترین ڕێژەی نۆرماڵ:", value=0.0)
            new_lab_high = st.number_input("بەرزترین ڕێژەی نۆرماڵ:", value=10.0)
        with col2:
            new_lab_unit = st.text_input("یەکە:", placeholder="mg/dL")
            new_lab_machine = st.text_input("ئامێر:", placeholder="ئامێری پێوانەکردن")
            new_lab_desc = st.text_area("تەفسیر:", placeholder="ڕوونکردنەوەی ئەم پشکنینە...")
            new_lab_note = st.text_area("📝 تێبینی:", placeholder="تێبینی تایبەتی خۆت لێرە بنووسە...")
            
        if st.form_submit_button("✅ پشکنینەکە زیاد بکە"):
            if new_lab_name:
                st.session_state.custom_lab_tests[new_lab_name] = {
                    "گروپ": new_lab_group, "نۆرماڵ": (new_lab_low, new_lab_high), "یەکە": new_lab_unit,
                    "تەفسیر": new_lab_desc, "ئامێر": new_lab_machine, "تێبینی": new_lab_note
                }
                auto_save()
                st.success(f"پشکنینی '{new_lab_name}' زیاد کرا و خەزن کرا!")
                st.rerun()
            else:
                st.error("تکایە ناوی پشکنین بنووسە")

    st.markdown("---")
    st.markdown("### 📋 لیستی پشکنینەکان")
    
    if st.session_state.custom_lab_tests:
        st.markdown("#### 🛠️ پشکنینە تایبەتییەکانی خۆت (دەستکاریکردن و سڕینەوە)")
        for lab_name, lab_info in list(st.session_state.custom_lab_tests.items()):
            with st.expander(f"🧪 {lab_name} - {lab_info.get('گروپ', '')}"):
                with st.form(f"edit_lab_{lab_name}"):
                    e_low = st.number_input("نزمترین:", value=float(lab_info['نۆرماڵ'][0]))
                    e_high = st.number_input("بەرزترین:", value=float(lab_info['نۆرماڵ'][1]))
                    e_unit = st.text_input("یەکە:", value=lab_info.get('یەکە', ''))
                    e_machine = st.text_input("ئامێر:", value=lab_info.get('ئامێر', ''))
                    e_note = st.text_area("تێبینی:", value=lab_info.get('تێبینی', ''))
                    
                    c1, c2 = st.columns(2)
                    if c1.form_submit_button("💾 نوێکردنەوە"):
                        st.session_state.custom_lab_tests[lab_name].update({
                            "نۆرماڵ": (e_low, e_high), "یەکە": e_unit, "ئامێر": e_machine, "تێبینی": e_note
                        })
                        auto_save()
                        st.success("نوێکرایەوە!")
                        st.rerun()
                    if c2.form_submit_button("🗑️ سڕینەوە"):
                        del st.session_state.custom_lab_tests[lab_name]
                        auto_save()
                        st.success("سڕایەوە!")
                        st.rerun()

    st.markdown("#### 🏥 پشکنینە بنەڕەتییەکان")
    cols = st.columns(2)
    idx = 0
    for test_name, test_info in all_lab_tests.items():
        with cols[idx % 2]:
            low, high = test_info.get("نۆرماڵ", (0, 0))
            note = test_info.get("تێبینی", "تێبینی تایبەتی خۆت لێرە بنووسە...")
            st.markdown(f"""
            <div class="lab-result-card lab-normal">
                <strong>{test_name}</strong>
                <p style="color:#aaa;font-size:0.9rem;">{test_info.get('گروپ', 'گشتی')} | ئامێر: {test_info.get('ئامێر', 'نەزانراو')}</p>
                <p>نۆرماڵ: {low} - {high} {test_info.get('یەکە', '')}</p>
                <p style="color:#888;font-size:0.8rem;">{test_info.get('تەفسیر', '')}</p>
                <p style="color:#aaa;font-size:0.8rem;background:rgba(255,255,255,0.05);padding:8px;border-radius:8px;margin-top:5px;">📝 {note}</p>
            </div>
            """, unsafe_allow_html=True)
        idx += 1

# ================================
# 14. پەڕەی فارماکۆلۆجی (زیادکردن، دەستکاری، سڕینەوە)
# ================================
elif page == "💊 فارماکۆلۆجی":
    st.markdown('<div class="main"><h2>💊 فارماکۆلۆجی و دەرمانناسی</h2><p style="color:#aaa;">دەرمانەکان لەگەڵ وەسف و شوێنی تێبینی تایبەتی خۆت</p></div>', unsafe_allow_html=True)
    
    st.markdown("### ➕ دەرمانێکی نوێ زیاد بکە (بۆ هەمیشە خەزن دەکرێت)")
    with st.form("add_drug_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            new_drug_name = st.text_input("ناوی دەرمان:")
            new_drug_dose = st.text_input("ڕێژە:", placeholder="500mg")
            new_drug_mech = st.text_input("میکانیزم:", placeholder="چۆن کار دەکات")
            new_drug_effect = st.text_input("کاریگەری لاوەکی:", placeholder="سەرگێژخواردن")
        with col2:
            new_drug_contra = st.text_input("پێچەوانە:", placeholder="نەخۆشی گورچیلە")
            new_drug_desc = st.text_area("وەسف:", placeholder="ڕوونکردنەوەی دەرمانەکە...")
            new_drug_why = st.text_area("بۆچی:", placeholder="بۆ چارەسەری چی بەکاردێت...")
            new_drug_note = st.text_area("📝 تێبینی:", placeholder="تێبینی تایبەتی خۆت لێرە بنووسە...")
            
        if st.form_submit_button("✅ دەرمانەکە زیاد بکە"):
            if new_drug_name:
                st.session_state.custom_drugs[new_drug_name] = {
                    "ڕێژە": new_drug_dose, "میکانیزم": new_drug_mech, "کاریگەری لاوەکی": new_drug_effect,
                    "پێچەوانە": new_drug_contra, "وەسف": new_drug_desc, "بۆچی": new_drug_why, "تێبینی": new_drug_note
                }
                auto_save()
                st.success(f"دەرمانی '{new_drug_name}' زیاد کرا و خەزن کرا!")
                st.rerun()
            else:
                st.error("تکایە ناوی دەرمان بنووسە")

    st.markdown("---")
    
    if st.session_state.custom_drugs:
        st.markdown("### 🛠️ دەرمانە تایبەتییەکانی خۆت (دەستکاریکردن و سڕینەوە)")
        for drug_name, drug_info in list(st.session_state.custom_drugs.items()):
            with st.expander(f"💊 {drug_name}"):
                with st.form(f"edit_drug_{drug_name}"):
                    e_dose = st.text_input("ڕێژە:", value=drug_info.get('ڕێژە', ''))
                    e_mech = st.text_input("میکانیزم:", value=drug_info.get('میکانیزم', ''))
                    e_effect = st.text_input("کاریگەری:", value=drug_info.get('کاریگەری لاوەکی', ''))
                    e_contra = st.text_input("پێچەوانە:", value=drug_info.get('پێچەوانە', ''))
                    e_desc = st.text_area("وەسف:", value=drug_info.get('وەسف', ''))
                    e_why = st.text_area("بۆچی:", value=drug_info.get('بۆچی', ''))
                    e_note = st.text_area("تێبینی:", value=drug_info.get('تێبینی', ''))
                    
                    c1, c2 = st.columns(2)
                    if c1.form_submit_button("💾 نوێکردنەوە"):
                        st.session_state.custom_drugs[drug_name].update({
                            "ڕێژە": e_dose, "میکانیزم": e_mech, "کاریگەری لاوەکی": e_effect,
                            "پێچەوانە": e_contra, "وەسف": e_desc, "بۆچی": e_why, "تێبینی": e_note
                        })
                        auto_save()
                        st.success("نوێکرایەوە!")
                        st.rerun()
                    if c2.form_submit_button("🗑️ سڕینەوە"):
                        del st.session_state.custom_drugs[drug_name]
                        auto_save()
                        st.success("سڕایەوە!")
                        st.rerun()

    st.markdown("### 📚 کتێبخانەی دەرمانە بنەڕەتییەکان")
    for category, drugs in DRUG_DATABASE.items():
        with st.expander(f"📂 {category} ({len(drugs)} دەرمان)"):
            cols = st.columns(2)
            idx = 0
            for drug, info in drugs.items():
                with cols[idx % 2]:
                    st.markdown(f"""
                    <div class="drug-card">
                        <h4>{drug}</h4>
                        <p><strong>ڕێژە:</strong> {info.get('ڕێژە', '')}</p>
                        <p><strong>وەسف:</strong> {info.get('وەسف', '')}</p>
                        <p><strong>بۆچی:</strong> {info.get('بۆچی', '')}</p>
                        <p style="color:#aaa;font-size:0.8rem;background:rgba(255,255,255,0.05);padding:8px;border-radius:8px;margin-top:5px;">📝 {info.get('تێبینی', '')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                idx += 1

# ================================
# 15. پەڕەی کویز
# ================================
elif page == "📝 کویز":
    st.markdown('<div class="main"><h2>📝 کویزی پزیشکی</h2></div>', unsafe_allow_html=True)
    level = get_user_level(st.session_state.quiz_score)
    if st.session_state.quiz_score < 100:
        q = MEDICAL_QUIZZES[st.session_state.level_1_done % len(MEDICAL_QUIZZES)]
        st.markdown(f'<div class="quiz-card"><h3>{q["پرسیار"]}</h3></div>', unsafe_allow_html=True)
        ans = st.radio("وەڵام:", q["هەڵبژاردەکان"])
        if st.button("✅ پشتڕاستکردنەوە", type="primary"):
            if q["هەڵبژاردەکان"].index(ans) == q["وەڵامی ڕاست"]:
                st.session_state.quiz_score += 1
                st.success("🎉 ڕاستە!")
                st.balloons()
            else:
                st.error("❌ هەڵەیە.")
            st.session_state.level_1_done += 1
            st.rerun()
    else:
        st.success("🎊 پیرۆز! تۆ نمرەی پڕت وەرگرت!")

# ================================
# 16. پەڕەی نەخۆشییەکان
# ================================
elif page == "📚 نەخۆشییەکان":
    st.markdown(f'<div class="main"><h2>📚 نەخۆشییەکان</h2></div>', unsafe_allow_html=True)
    for disease, info in DISEASE_DATABASE.items():
        with st.expander(f"🩺 {disease}"):
            st.markdown(f"**⚠️ ئاستی مەترسی:** <span style='color:{get_risk_color(info['ئاستی مەترسی'])}'>{info['ئاستی مەترسی']}</span>", unsafe_allow_html=True)
            st.markdown("**🔍 نیشانەکان:** " + ", ".join(info['نیشانەکان'][:5]))
            st.markdown("**💊 چارەسەر:** " + ", ".join(info['چارەسەر'][:3]))

# ================================
# 17. پەڕەی شیکاری کەیس
# ================================
elif page == "🩺 شیکاری کەیس":
    st.markdown('<div class="main"><h2>🩺 شیکاری کەیس</h2></div>', unsafe_allow_html=True)
    if st.button("🔄 کەیسی نوێ"):
        dis = random.choice(list(DISEASE_DATABASE.keys()))
        st.session_state.current_case = {"disease": dis, "info": DISEASE_DATABASE[dis]}
        st.rerun()
    if st.session_state.current_case:
        case = st.session_state.current_case
        st.markdown(f'<div class="case-card"><h3>📋 کەیسی پزیشکی</h3><p><strong>نیشانەکان:</strong> {", ".join(case["info"]["نیشانەکان"][:4])}</p></div>', unsafe_allow_html=True)
        diag = st.selectbox("دەستنیشانکردن:", list(DISEASE_DATABASE.keys()))
        if st.button("✅ پشتڕاستکردنەوە"):
            st.session_state.total_cases_solved += 1
            if diag == case["disease"]:
                st.session_state.correct_diagnoses += 1
                st.markdown('<div class="success-box"><h3>🎉 ڕاستە!</h3></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="error-box"><h3>❌ هەڵەیە</h3><p>ڕاست: {case["disease"]}</p></div>', unsafe_allow_html=True)

# ================================
# 18. پەڕەی دەستکەوتەکان
# ================================
elif page == "🏆 دەستکەوتەکان":
    st.markdown('<div class="main"><h2>🏆 دەستکەوتەکان</h2></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1: st.metric("📝 کویز", f"{st.session_state.quiz_score}/100")
    with col2: st.metric("🩺 کەیس", st.session_state.total_cases_solved)

# ================================
# فووەتەر
# ================================
st.markdown(f"""
<div class="footer-style">
    <h3>🩺 Dr.Danyal - ڕاهێنەری پزیشکی Pro Max</h3>
    <p>داتاکانت بۆ هەمیشە بە پارێزراوی لە فایلدا هەڵدەگیرێن</p>
</div>
""", unsafe_allow_html=True)
