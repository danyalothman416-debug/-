# ============================================================
# Dr.Danyal - ڕاهێنەری پزیشکی Pro Max v6.0 (چاککراو)
# پارت ١: ئیمپۆرت، ڕێکخستن، سیستەمی لۆگین
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import json
import os
import hashlib
import re
from typing import Dict, List, Tuple, Optional

# ML imports (تەنها ئەوانەی بەکاردهێنرێن)
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score

import warnings
warnings.filterwarnings('ignore')

# ============================================================
# ١. ڕێکخستنی پەڕە
# ============================================================
st.set_page_config(
    page_title="Dr.Danyal - ڕاهێنەری پزیشکی Pro Max",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# ٢. سیستەمی لۆگین و خەزنکردن
# ============================================================
DATA_DIR = "user_data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

USERS_FILE = os.path.join(DATA_DIR, "users.json")


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def load_users() -> Dict:
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_users(users: Dict):
    tmp = USERS_FILE + ".tmp"
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=4)
    os.replace(tmp, USERS_FILE)  # ⬅️ نووسینەوەی ئەتۆمیک


def create_user(username: str, password: str) -> bool:
    users = load_users()
    if username in users:
        return False
    users[username] = {
        "password": hash_password(password),
        "created_at": datetime.now().isoformat(),
        "custom_lab_tests": {},
        "custom_drugs": {},
        "lab_notes": {},
        "drug_notes": {}
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
    return users.get(username, {})


def save_user_data(username: str, data: Dict):
    users = load_users()
    if username in users:
        users[username].update(data)
        save_users(users)


# ============================================================
# ٣. دەستپێکردنی session_state (تەنها جارێک)
# ============================================================
DEFAULT_STATE = {
    "logged_in": False,
    "username": "",
    "custom_lab_tests": {},
    "custom_drugs": {},
    "lab_notes": {},
    "drug_notes": {},
    "current_case": None,
    "diagnosis_submitted": False,
    "quiz_index": 0,
    "quiz_score": 0,
    "quiz_completed": False,
    "case_history": [],
    "total_cases_solved": 0,
    "correct_diagnoses": 0,
    "last_activity": datetime.now(),
    "student_level": "ساڵی یەکەم",
    "quiz_answers": [],
    "streak_days": 0,
    "last_study_date": datetime.now().date(),
    "achievements": [],
    "favorite_diseases": [],
    "study_notes": "",
    "study_time": 0,
    "quiz_attempts": 0,
    "simulation_count": 0,
    "current_level": 1,
    "level_1_done": 0,
    "level_2_done": 0,
    "level_3_done": 0,
    "level_4_done": 0,
    "level_5_done": 0,
    "lab_history": [],
    "toast_msg": None,
}

for key, default in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = default
# ============================================================
# ٤. CSS (کورتکراوە، بێ keyframes ی دووبارە)
# ============================================================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e, #0f0c29);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        min-height: 100vh;
    }
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: scale(0.95); }
        to { opacity: 1; transform: scale(1); }
    }
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-12px); }
        100% { transform: translateY(0px); }
    }
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(100px); }
        to { opacity: 1; transform: translateX(0); }
    }
    @keyframes shimmer {
        0% { background-position: 400% 0; }
        100% { background-position: -400% 0; }
    }
    @keyframes textShimmer {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    @keyframes headerGradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    @keyframes numberGradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .main {
        background: rgba(255,255,255,0.03);
        backdrop-filter: blur(20px);
        border-radius: 35px;
        padding: 2.5rem;
        margin: 1rem;
        border: 1px solid rgba(255,255,255,0.05);
        box-shadow: 0 30px 80px rgba(0,0,0,0.4);
        animation: fadeIn 1s ease-out;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a1929 0%, #0d2137 50%, #0a1929 100%) !important;
        border-right: 1px solid rgba(79,172,254,0.15) !important;
        box-shadow: 5px 0 40px rgba(0,0,0,0.5) !important;
    }
    [data-testid="stSidebar"] * { color: rgba(255,255,255,0.9) !important; }
    [data-testid="stSidebar"] hr { border-color: rgba(79,172,254,0.2) !important; }

    .stButton > button {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%) !important;
        border: none !important;
        color: #0a1929 !important;
        font-weight: 700 !important;
        padding: 0.8rem 2rem !important;
        border-radius: 50px !important;
        box-shadow: 0 8px 25px rgba(79,172,254,0.35) !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%) !important;
        transform: translateY(-3px) !important;
    }
    [data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05)) !important;
        border: 1px solid rgba(79,172,254,0.3) !important;
        color: white !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: linear-gradient(135deg, #ff6b6b, #ee5a24) !important;
    }

    .main-header {
        font-size: 3rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 30%, #f093fb 60%, #4facfe 100%);
        background-size: 300% 300%;
        animation: headerGradient 4s ease infinite;
        color: white;
        text-align: center;
        padding: 2.5rem;
        border-radius: 35px;
        margin-bottom: 2rem;
        box-shadow: 0 25px 70px rgba(102,126,234,0.5);
    }

    .logo-container {
        display: flex; align-items: center; justify-content: center;
        gap: 15px; animation: float 4s ease-in-out infinite;
        background: rgba(255,255,255,0.05);
        padding: 15px 30px; border-radius: 60px;
        border: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 20px;
    }
    .logo-icon { font-size: 4rem; animation: pulse 2s infinite; }
    .logo-text {
        font-size: 2.2rem; font-weight: bold;
        background: linear-gradient(135deg, #667eea, #f093fb, #4facfe, #667eea);
        background-size: 300% 300%;
        animation: textShimmer 4s ease infinite;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .case-card, .quiz-card, .drug-card, .lab-result-card {
        background: rgba(255,255,255,0.06);
        backdrop-filter: blur(15px);
        padding: 1.5rem;
        border-radius: 20px;
        border-left: 6px solid #667eea;
        margin: 0.8rem 0;
        color: #fff;
        transition: all 0.3s ease;
    }
    .case-card:hover, .quiz-card:hover, .drug-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 50px rgba(102,126,234,0.25);
    }

    .success-box {
        background: linear-gradient(135deg, rgba(40,167,69,0.3), rgba(40,167,69,0.08));
        padding: 1.5rem; border-radius: 20px;
        border-left: 6px solid #28a745;
        color: #fff;
    }
    .error-box {
        background: linear-gradient(135deg, rgba(220,53,69,0.3), rgba(220,53,69,0.08));
        padding: 1.5rem; border-radius: 20px;
        border-left: 6px solid #dc3545;
        color: #fff;
    }

    .stat-card {
        background: rgba(255,255,255,0.05);
        backdrop-filter: blur(15px);
        padding: 1.5rem;
        border-radius: 20px;
        text-align: center;
        border-top: 5px solid #667eea;
        color: #fff;
        transition: all 0.3s ease;
    }
    .stat-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 50px rgba(102,126,234,0.25);
    }
    .stat-number {
        font-size: 2.5rem; font-weight: bold;
        background: linear-gradient(135deg, #667eea, #f093fb, #4facfe);
        background-size: 200% 200%;
        animation: numberGradient 3s ease infinite;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .badge-level {
        display: inline-block;
        padding: 0.5rem 1.8rem;
        border-radius: 40px;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea, #f093fb);
        color: white;
        box-shadow: 0 10px 30px rgba(102,126,234,0.4);
        font-size: 1rem;
    }

    .progress-container {
        background: rgba(255,255,255,0.08);
        border-radius: 25px;
        height: 18px;
        overflow: hidden;
        margin: 0.8rem 0;
    }
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #667eea, #764ba2, #f093fb, #4facfe, #667eea);
        background-size: 400% 100%;
        border-radius: 25px;
        transition: width 1.2s ease;
        animation: shimmer 4s infinite linear;
    }

    .risk-high { color: #ff6b6b; font-weight: bold; }
    .risk-medium { color: #ffd93d; font-weight: bold; }
    .risk-low { color: #6bcb77; font-weight: bold; }

    /* ⬅️ چاککراو: کلاسە ئینگلیزییەکان بۆ دۆخی پشکنین */
    .lab-result-card.lab-normal { border-left-color: #28a745; }
    .lab-result-card.lab-high   { border-left-color: #dc3545; }
    .lab-result-card.lab-low    { border-left-color: #ffc107; }
    .lab-result-card.lab-unknown{ border-left-color: #6c757d; }

    .dr-icon {
        font-size: 3rem;
        animation: pulse 2s infinite, float 4s ease-in-out infinite;
        display: inline-block;
    }

    .login-box {
        background: rgba(255,255,255,0.05);
        backdrop-filter: blur(30px);
        padding: 2.5rem;
        border-radius: 30px;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 30px 80px rgba(0,0,0,0.4);
        max-width: 480px;
        margin: 3rem auto;
        text-align: center;
    }

    .footer-style {
        text-align: center;
        padding: 2.5rem;
        background: rgba(255,255,255,0.04);
        color: white;
        border-radius: 35px;
        margin-top: 2rem;
        border: 1px solid rgba(255,255,255,0.04);
    }

    .symptom-tag {
        display: inline-block;
        background: rgba(102,126,234,0.25);
        padding: 0.3rem 1rem;
        border-radius: 20px;
        margin: 0.2rem;
        font-size: 0.8rem;
        color: #c8d0ff;
    }

    @media (max-width: 768px) {
        .main-header { font-size: 1.8rem; padding: 1.2rem; }
        .stat-number { font-size: 1.8rem; }
        .logo-text { font-size: 1.5rem; }
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# ٥. سیستەمی ئاستەکان
# ============================================================
LEVELS = {
    1: {"name": "سەرەتایی", "min_score": 0, "max_score": 9,
        "color": "#28a745", "quizzes": 50, "icon": "🌱",
        "description": "دەستپێکی ڕێگای پزیشکی", "requirements": "هیچ"},
    2: {"name": "فێرخواز", "min_score": 10, "max_score": 29,
        "color": "#17a2b8", "quizzes": 100, "icon": "📖",
        "description": "فێربوونی بنەماکانی پزیشکی", "requirements": "تەواوکردنی ئاست ١"},
    3: {"name": "پێشکەوتوو", "min_score": 30, "max_score": 59,
        "color": "#ffc107", "quizzes": 150, "icon": "🚀",
        "description": "پێشکەوتن لە زانستە پزیشکییەکان", "requirements": "تەواوکردنی ئاست ٢"},
    4: {"name": "شارەزا", "min_score": 60, "max_score": 89,
        "color": "#ff9f1c", "quizzes": 200, "icon": "🏆",
        "description": "شارەزایی لە نەخۆشییەکان", "requirements": "تەواوکردنی ئاست ٣"},
    5: {"name": "پزیشک", "min_score": 90, "max_score": 100,
        "color": "#dc3545", "quizzes": 500, "icon": "👨‍⚕️",
        "description": "پزیشکی لێهاتوو و شارەزا", "requirements": "تەواوکردنی ئاست ٤"},
}


def get_user_level(score: int) -> int:
    for level in sorted(LEVELS.keys(), reverse=True):
        if score >= LEVELS[level]["min_score"]:
            return level
    return 1


def get_level_info(level: int) -> Dict:
    return LEVELS.get(level, LEVELS[1])


def get_next_level(level: int) -> int:
    return min(level + 1, 5)


def get_level_progress(score: int) -> float:
    level = get_user_level(score)
    if level == 5:
        return 100.0
    current = LEVELS[level]
    next_level = get_next_level(level)
    total = LEVELS[next_level]["min_score"] - current["min_score"]
    achieved = score - current["min_score"]
    return min((achieved / total) * 100, 100) if total > 0 else 100.0


def get_level_icon(level: int) -> str:
    return get_level_info(level).get("icon", "📚")


def get_risk_color(risk_level: str) -> str:
    colors = {
        "زۆر مەترسیدار": "#ff6b6b",
        "مەترسیدار": "#ffd93d",
        "مامناوەند": "#ffc107",
        "کەم": "#6bcb77"
    }
    return colors.get(risk_level, "#6c757d")


def get_age_group(age: int) -> str:
    if age < 18: return "منداڵ"
    if age < 40: return "گەنج"
    if age < 60: return "تەمەن مامناوەند"
    return "پیر"


# ============================================================
# ٦. داتابەسی نەخۆشییەکان
# ============================================================
DISEASE_DATABASE = {
    "شەکرەی جۆری 1": {
        "نیشانەکان": ["تینوویەتی زۆر", "میزی زۆر", "کێش کەمبوونەوە", "ماندوویی", "بینی تەڵخ", "برسێتی زۆر"],
        "پشکنینەکان": {"FBS": ">200 mg/dL", "HbA1c": ">8%", "C-peptide": "نزم", "Anti-GAD": "positive"},
        "چارەسەر": ["ئەنسولین", "پێوانەکردنی شەکر", "شێوازی خواردن", "وەرزش"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندی": "تەمەن < 30 + C-peptide نزم + Anti-GAD positive",
        "ڕێپیشگیری": ["پشکنینی بۆماوەیی"],
        "گروپی تەمەن": "منداڵان و گەنجان",
        "ڕێژەی تووشبوون": "0.5%",
        "جۆری نەخۆشی": "خۆئەگەر"
    },
    "شەکرەی جۆری 2": {
        "نیشانەکان": ["تینوویەتی زۆر", "میزی زۆر", "ماندوویی", "کێش کەمبوونەوە", "بینی تەڵخ", "برسێتی زۆر", "پێست وشک", "هەستی بەمەزە"],
        "پشکنینەکان": {"FBS": ">126 mg/dL", "HbA1c": ">6.5%", "OGTT": ">200 mg/dL", "C-peptide": "نۆرماڵ/بەرز"},
        "چارەسەر": ["مێتفۆرمین", "گۆڕینی شێوازی ژیان", "وەرزش", "شێوازی خواردن"],
        "ئاستی مەترسی": "مەترسیدار",
        "تایبەتمەندی": "FBS بەرز + HbA1c بەرز + تەمەن > 40",
        "ڕێپیشگیری": ["شێوازی خواردن", "چالاکی جەستەیی", "کەمکردنەوەی کێش"],
        "گروپی تەمەن": "تەمەن مامناوەند و پیر",
        "ڕێژەی تووشبوون": "8.5%",
        "جۆری نەخۆشی": "مێتابۆلیک"
    },
    "پەستانی خوێنی سەرەتایی": {
        "نیشانەکان": ["سەرئێشە", "سەرگێژخواردن", "فشاری پشت چاو", "خێرالێدانی دڵ", "ئارەقەکردن"],
        "پشکنینەکان": {"BP": ">140/90 mmHg", "ECG": "LVH", "Creatinine": "نۆرماڵ"},
        "چارەسەر": ["کاپتۆپریل", "کەمکردنەوەی نمەک", "وەرزشی ئیروبیک", "کەمکردنەوەی کێش"],
        "ئاستی مەترسی": "مامناوەند",
        "تایبەتمەندی": "BP بەرز بەبێ هۆکاری دیکە",
        "ڕێپیشگیری": ["پێوانەکردنی BP", "شێوازی خواردن", "ڕاهێنان"],
        "گروپی تەمەن": "هەموو تەمەنەکان",
        "ڕێژەی تووشبوون": "25%",
        "جۆری نەخۆشی": "دڵ و خوێن"
    },
    "نەخۆشی دڵی ئیسکیمیک": {
        "نیشانەکان": ["ئازاری سنگ", "کورتی هەناسە", "ئارەقەکردن", "ئازاری شان", "خێرالێدانی دڵ"],
        "پشکنینەکان": {"ECG": "ST depression", "Troponin": ">0.04", "CK-MB": ">5", "CAG": "تەنگی کرۆنەری"},
        "چارەسەر": ["ئەسپیرین", "نایترۆگلیسیرین", "بێتا بلاکەر", "هێپارین"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندی": "ST changes + Troponin elevated",
        "ڕێپیشگیری": ["کۆنتڕۆڵی BP", "وەرزش", "وەستانی جگەرە"],
        "گروپی تەمەن": "تەمەن > 50",
        "ڕێژەی تووشبوون": "7%",
        "جۆری نەخۆشی": "دڵ و خوێن"
    },
    "ئەنیمیا": {
        "نیشانەکان": ["ماندوویی", "ڕەنگی پێست زەرد", "سەرگێژخواردن", "لێدانی دڵ خێرا", "پڕۆشتن"],
        "پشکنینەکان": {"Hb": "<12 g/dL", "MCV": "<80 fL", "Ferritin": "<15", "TIBC": ">450"},
        "چارەسەر": ["فێروس سولفەیت", "گۆڕینی خواردن", "دۆزینەوەی هۆکار", "ڤیتامین C"],
        "ئاستی مەترسی": "مامناوەند",
        "تایبەتمەندی": "Hb نزم + MCV نزم + Ferritin نزم",
        "ڕێپیشگیری": ["خواردنی ئاسن", "پشکنینی خوێن"],
        "گروپی تەمەن": "هەموو تەمەنەکان",
        "ڕێژەی تووشبوون": "25%",
        "جۆری نەخۆشی": "خوێن"
    },
    "هەوکردنی سییەکان": {
        "نیشانەکان": ["تا", "کۆخە", "هەناسەدان بە زەحمەت", "ئازاری سنگ", "ماندوویی", "لەرزین"],
        "پشکنینەکان": {"Chest X-ray": "Consolidation", "CRP": ">10", "WBC": ">11"},
        "چارەسەر": ["ئەمۆکسیسیلین", "ئۆکسجین", "شلەمەنی", "پشوو"],
        "ئاستی مەترسی": "مامناوەند",
        "تایبەتمەندی": "Consolidation + CRP بەرز",
        "ڕێپیشگیری": ["کوتان", "دەستشۆردن"],
        "گروپی تەمەن": "هەموو تەمەنەکان",
        "ڕێژەی تووشبوون": "3%",
        "جۆری نەخۆشی": "هەوکردن"
    },
    "نەخۆشی گورچیلە": {
        "نیشانەکان": ["ئاوسانی ڕوو و قاچ", "میزی کەم", "ماندوویی", "سەرئێشە", "خوێن لە میزدا"],
        "پشکنینەکان": {"Creatinine": ">1.3", "BUN": ">20", "eGFR": "<60", "Urinalysis": "پڕۆتین + خوێن"},
        "چارەسەر": ["ACE inhibitor", "کەمکردنەوەی پڕۆتین", "کۆنتڕۆڵی BP"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندی": "Creatinine بەرز + eGFR نزم",
        "ڕێپیشگیری": ["کۆنتڕۆڵی شەکرە", "کۆنتڕۆڵی BP"],
        "گروپی تەمەن": "تەمەن > 50",
        "ڕێژەی تووشبوون": "10%",
        "جۆری نەخۆشی": "گورچیلە"
    },
    "نەخۆشی جگەر B": {
        "نیشانەکان": ["ماندوویی", "زەردبوون", "میز تۆخ", "ئازاری سک", "سکچوون"],
        "پشکنینەکان": {"ALT": "بەرز", "HBsAg": "positive", "Anti-HBc": "positive"},
        "چارەسەر": ["Entecavir", "Tenofovir", "پشکنینی بەردەوام"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندی": "HBsAg positive",
        "ڕێپیشگیری": ["کوتان", "پارێزی لە پەیوەندی خوێن"],
        "گروپی تەمەن": "هەموو تەمەنەکان",
        "ڕێژەی تووشبوون": "3%",
        "جۆری نەخۆشی": "جگەر"
    },
    "نەخۆشی کۆکە": {
        "نیشانەکان": ["هەناسەدان بە زەحمەت", "کۆخە", "تنگەنەفەسی", "فیشک", "فشاری سنگ"],
        "پشکنینەکان": {"Pulmonary function": "FEV1 < 80%", "Peak flow": "کەم", "IgE": "بەرز"},
        "چارەسەر": ["Bronchodilator", "Steroid inhaler", "پارێزی لە هۆکارەکان"],
        "ئاستی مەترسی": "مامناوەند",
        "تایبەتمەندی": "FEV1 کەم + فیشک",
        "ڕێپیشگیری": ["پارێزی لە هۆکارەکان", "وەرزش"],
        "گروپی تەمەن": "منداڵان و گەنجان",
        "ڕێژەی تووشبوون": "5%",
        "جۆری نەخۆشی": "هەناسە"
    },
    "نەخۆشی سیل": {
        "نیشانەکان": ["کۆخە بە خوێن", "تا", "ئارەقەکردنی شەو", "کێش کەمبوونەوە", "ماندوویی"],
        "پشکنینەکان": {"Chest X-ray": "تەوەرەکان", "Sputum AFB": "positive", "PPD": "positive"},
        "چارەسەر": ["Rifampicin", "Isoniazid", "Pyrazinamide", "Ethambutol"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندی": "کۆخەی خوێناوی + X-ray",
        "ڕێپیشگیری": ["BCG vaccine", "پارێزی"],
        "گروپی تەمەن": "هەموو تەمەنەکان",
        "ڕێژەی تووشبوون": "0.5%",
        "جۆری نەخۆشی": "هەناسە"
    },
    "Parkinson": {
        "نیشانەکان": ["لەرزین", "خاوکردنەوەی جوڵە", "سختی ماسوولکە", "مشکێتی ڕۆیشتن"],
        "پشکنینەکان": {"Clinical exam": "Parkinsonian", "DAT scan": "کەم", "MRI": "نۆرماڵ"},
        "چارەسەر": ["Levodopa", "Carbidopa", "Pramipexole"],
        "ئاستی مەترسی": "مەترسیدار",
        "تایبەتمەندی": "لەرزین + سختی ماسوولکە",
        "ڕێپیشگیری": ["وەرزش"],
        "گروپی تەمەن": "تەمەن > 60",
        "ڕێژەی تووشبوون": "1%",
        "جۆری نەخۆشی": "دەمار"
    },
    "Alzheimer": {
        "نیشانەکان": ["بیرچون", "کەمبوونی بیر", "گۆڕانی کەسایەتی", "بێئاگایی"],
        "پشکنینەکان": {"MRI": "Atrophy", "PET": "Abnormal", "Cognitive test": "کەم"},
        "چارەسەر": ["Donepezil", "Rivastigmine", "Memantine"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندی": "بیرچون + MRI atrophy",
        "ڕێپیشگیری": ["مەشقی مێشک", "وەرزش"],
        "گروپی تەمەن": "تەمەن > 65",
        "ڕێژەی تووشبوون": "5%",
        "جۆری نەخۆشی": "دەمار"
    },
}
# ============================================================
# ٧. داتابەسی پشکنینەکان (بێ کلیلی دووبارە)
# ============================================================
LAB_TESTS = {
    # خوێن
    "CBC":              {"گروپ": "خوێن", "نۆرماڵ": (4.0, 11.0),  "یەکە": "x10³/µL", "تەفسیر": "خڕۆکە سپیەکان", "ئامێر": "Sysmex XN-9000", "تێبینی": ""},
    "Hemoglobin":       {"گروپ": "خوێن", "نۆرماڵ": (12.0, 16.0), "یەکە": "g/dL",    "تەفسیر": "هیمۆگلۆبین",     "ئامێر": "HemoCue 201+",  "تێبینی": ""},
    "Platelets":        {"گروپ": "خوێن", "نۆرماڵ": (150, 450),   "یەکە": "x10³/µL", "تەفسیر": "پلەیتلێت",      "ئامێر": "Sysmex XN-9000", "تێبینی": ""},
    "MCV":              {"گروپ": "خوێن", "نۆرماڵ": (80, 100),    "یەکە": "fL",      "تەفسیر": "قەبارەی خڕۆکە", "ئامێر": "Sysmex XN-9000", "تێبینی": ""},
    "MCH":              {"گروپ": "خوێن", "نۆرماڵ": (27, 33),     "یەکە": "pg",      "تەفسیر": "کەمی هیمۆگلۆبین", "ئامێر": "Sysmex XN-9000", "تێبینی": ""},
    "MCHC":             {"گروپ": "خوێن", "نۆرماڵ": (32, 36),     "یەکە": "g/dL",    "تەفسیر": "چڕی هیمۆگلۆبین","ئامێر": "Sysmex XN-9000", "تێبینی": ""},
    "RDW":              {"گروپ": "خوێن", "نۆرماڵ": (11.5, 14.5), "یەکە": "%",       "تەفسیر": "جیاوازی قەبارە", "ئامێر": "Sysmex XN-9000", "تێبینی": ""},
    "Reticulocyte":     {"گروپ": "خوێن", "نۆرماڵ": (0.5, 2.5),   "یەکە": "%",       "تەفسیر": "خڕۆکە نوێکان",  "ئامێر": "BD FACSCalibur", "تێبینی": ""},
    "Ferritin":         {"گروپ": "خوێن", "نۆرماڵ": (15, 300),    "یەکە": "ng/mL",   "تەفسیر": "ئاسن",          "ئامێر": "Roche Cobas e411","تێبینی": ""},
    "TIBC":             {"گروپ": "خوێن", "نۆرماڵ": (250, 450),   "یەکە": "mcg/dL",  "تەفسیر": "ئاسن",          "ئامێر": "Roche Cobas c502","تێبینی": ""},
    "Iron":             {"گروپ": "خوێن", "نۆرماڵ": (60, 170),    "یەکە": "mcg/dL",  "تەفسیر": "ئاسن",          "ئامێر": "Roche Cobas c502","تێبینی": ""},
    "Vitamin B12":      {"گروپ": "خوێن", "نۆرماڵ": (200, 900),   "یەکە": "pg/mL",   "تەفسیر": "ڤیتامین B12",   "ئامێر": "Roche Cobas e411","تێبینی": ""},
    "Folate":           {"گروپ": "خوێن", "نۆرماڵ": (3, 17),      "یەکە": "ng/mL",   "تەفسیر": "فۆلیک ئەسید",   "ئامێر": "Roche Cobas e411","تێبینی": ""},
    "LDH":              {"گروپ": "خوێن", "نۆرماڵ": (100, 250),   "یەکە": "U/L",     "تەفسیر": "ئەنزیم",        "ئامێر": "Beckman AU480", "تێبینی": ""},
    "Haptoglobin":      {"گروپ": "خوێن", "نۆرماڵ": (50, 250),    "یەکە": "mg/dL",   "تەفسیر": "پروتێین",       "ئامێر": "Siemens BNII",  "تێبینی": ""},
    "ESR":              {"گروپ": "خوێن", "نۆرماڵ": (0, 20),      "یەکە": "mm/hr",   "تەفسیر": "خێرایی تەنیشتن","ئامێر": "Ves-Matic 20",  "تێبینی": ""},
    "CRP":              {"گروپ": "خوێن", "نۆرماڵ": (0, 5),       "یەکە": "mg/L",    "تەفسیر": "هەوکردن",       "ئامێر": "Roche Cobas c502","تێبینی": ""},
    "Procalcitonin":    {"گروپ": "خوێن", "نۆرماڵ": (0, 0.5),     "یەکە": "ng/mL",   "تەفسیر": "هەوکردنی بەکتریایی","ئامێر": "Roche Cobas e411","تێبینی": ""},

    # بایۆکیمیایی
    "Glucose":          {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (70, 126),  "یەکە": "mg/dL", "تەفسیر": "شەکری خوێن",  "ئامێر": "Roche Cobas c502","تێبینی": ""},
    "HbA1c":            {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (4.0, 5.6), "یەکە": "%",     "تەفسیر": "شەکری درێژخایەن","ئامێر": "Bio-Rad D-100", "تێبینی": ""},
    "Creatinine":       {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (0.6, 1.3), "یەکە": "mg/dL", "تەفسیر": "گورچیلە",     "ئامێر": "Roche Cobas c502","تێبینی": ""},
    "BUN":              {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (7, 20),    "یەکە": "mg/dL", "تەفسیر": "یوریا",       "ئامێر": "Roche Cobas c502","تێبینی": ""},
    "ALT":              {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (10, 40),   "یەکە": "U/L",   "تەفسیر": "جگەر",        "ئامێر": "Roche Cobas c502","تێبینی": ""},
    "AST":              {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (10, 40),   "یەکە": "U/L",   "تەفسیر": "جگەر",        "ئامێر": "Roche Cobas c502","تێبینی": ""},
    "Bilirubin":        {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (0.1, 1.2), "یەکە": "mg/dL", "تەفسیر": "زەرداوی",     "ئامێر": "Roche Cobas c502","تێبینی": ""},
    "Albumin":          {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (3.5, 5.0), "یەکە": "g/dL",  "تەفسیر": "ئەلبومین",    "ئامێر": "Roche Cobas c502","تێبینی": ""},
    "Potassium":        {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (3.5, 5.0), "یەکە": "mmol/L","تەفسیر": "پۆتاسیۆم",    "ئامێر": "Roche Cobas c502","تێبینی": ""},
    "Sodium":           {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (135, 145), "یەکە": "mmol/L","تەفسیر": "سۆدیۆم",      "ئامێر": "Roche Cobas c502","تێبینی": ""},
    "Calcium":          {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (8.5, 10.5),"یەکە": "mg/dL", "تەفسیر": "کالسیۆم",     "ئامێر": "Roche Cobas c502","تێبینی": ""},
    "Amylase":          {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (20, 200),  "یەکە": "U/L",   "تەفسیر": "پەنکریاس",    "ئامێر": "Roche Cobas c502","تێبینی": ""},
    "Lipase":           {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (20, 200),  "یەکە": "U/L",   "تەفسیر": "پەنکریاس",    "ئامێر": "Roche Cobas c502","تێبینی": ""},
    "Cholesterol":      {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (0, 200),   "یەکە": "mg/dL", "تەفسیر": "کۆلسترۆل",    "ئامێر": "Roche Cobas c502","تێبینی": ""},
    "LDL":              {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (0, 100),   "یەکە": "mg/dL", "تەفسیر": "کۆلسترۆلی خراپ","ئامێر": "Roche Cobas c502","تێبینی": ""},
    "HDL":              {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (40, 60),   "یەکە": "mg/dL", "تەفسیر": "کۆلسترۆلی باش","ئامێر": "Roche Cobas c502","تێبینی": ""},
    "Triglycerides":    {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (0, 150),   "یەکە": "mg/dL", "تەفسیر": "تریگلیسیرید", "ئامێر": "Roche Cobas c502","تێبینی": ""},

    # دڵ
    "Troponin I":       {"گروپ": "دڵ", "نۆرماڵ": (0, 0.04),   "یەکە": "ng/mL", "تەفسیر": "دڵ",     "ئامێر": "Roche Cobas e411","تێبینی": ""},
    "Troponin T":       {"گروپ": "دڵ", "نۆرماڵ": (0, 0.014),  "یەکە": "ng/mL", "تەفسیر": "دڵ",     "ئامێر": "Roche Cobas e411","تێبینی": ""},
    "CK-MB":            {"گروپ": "دڵ", "نۆرماڵ": (0, 5),      "یەکە": "ng/mL", "تەفسیر": "دڵ",     "ئامێر": "Roche Cobas e411","تێبینی": ""},
    "BNP":              {"گروپ": "دڵ", "نۆرماڵ": (0, 100),    "یەکە": "pg/mL", "تەفسیر": "دڵ",     "ئامێر": "Roche Cobas e411","تێبینی": ""},
    "HS-CRP":           {"گروپ": "دڵ", "نۆرماڵ": (0, 2),      "یەکە": "mg/L",  "تەفسیر": "هەوکردنی دڵ","ئامێر": "Roche Cobas c502","تێبینی": ""},

    # هۆرمۆن
    "TSH":              {"گروپ": "هۆرمۆن", "نۆرماڵ": (0.4, 4.0), "یەکە": "mIU/L", "تەفسیر": "دراوان",  "ئامێر": "Roche Cobas e411","تێبینی": ""},
    "T4":               {"گروپ": "هۆرمۆن", "نۆرماڵ": (5, 12),    "یەکە": "μg/dL", "تەفسیر": "دراوان",  "ئامێر": "Roche Cobas e411","تێبینی": ""},
    "T3":               {"گروپ": "هۆرمۆن", "نۆرماڵ": (80, 200),  "یەکە": "ng/dL", "تەفسیر": "دراوان",  "ئامێر": "Roche Cobas e411","تێبینی": ""},
    "Cortisol":         {"گروپ": "هۆرمۆن", "نۆرماڵ": (5, 25),    "یەکە": "μg/dL", "تەفسیر": "کۆرتیزۆل","ئامێر": "Roche Cobas e411","تێبینی": ""},
    "Insulin":          {"گروپ": "هۆرمۆن", "نۆرماڵ": (2, 25),    "یەکە": "μIU/mL","تەفسیر": "ئەنسولین","ئامێر": "Roche Cobas e411","تێبینی": ""},

    # میز
    "Urine Protein":    {"گروپ": "میز", "نۆرماڵ": (0, 0.3),   "یەکە": "g/24h", "تەفسیر": "پڕۆتینی میز","ئامێر": "Roche Cobas c502","تێبینی": ""},
    "Urine Glucose":    {"گروپ": "میز", "نۆرماڵ": (0, 0),     "یەکە": "mg/dL", "تەفسیر": "شەکری میز",  "ئامێر": "Roche Cobas c502","تێبینی": ""},
    "Urine pH":         {"گروپ": "میز", "نۆرماڵ": (5.0, 8.0), "یەکە": "",      "تەفسیر": "pH میز",     "ئامێر": "Hanna HI221",    "تێبینی": ""},

    # ڤیتامین
    "Vitamin D":        {"گروپ": "ڤیتامین", "نۆرماڵ": (30, 100), "یەکە": "ng/mL", "تەفسیر": "ڤیتامین D","ئامێر": "Roche Cobas e411","تێبینی": ""},
    "Vitamin A":        {"گروپ": "ڤیتامین", "نۆرماڵ": (20, 80),  "یەکە": "μg/dL", "تەفسیر": "ڤیتامین A","ئامێر": "Agilent 1200",   "تێبینی": ""},
    "Vitamin E":        {"گروپ": "ڤیتامین", "نۆرماڵ": (5, 18),   "یەکە": "mg/L",  "تەفسیر": "ڤیتامین E","ئامێر": "Agilent 1200",   "تێبینی": ""},
    "Vitamin K":        {"گروپ": "ڤیتامین", "نۆرماڵ": (0.2, 3.0),"یەکە": "ng/mL", "تەفسیر": "ڤیتامین K","ئامێر": "Agilent 1200",   "تێبینی": ""},

    # معدن
    "Zinc":             {"گروپ": "معدن", "نۆرماڵ": (70, 120), "یەکە": "μg/dL", "تەفسیر": "زینک",     "ئامێر": "Agilent 7800", "تێبینی": ""},
    "Selenium":         {"گروپ": "معدن", "نۆرماڵ": (70, 150), "یەکە": "μg/L",  "تەفسیر": "سێلینیۆم","ئامێر": "Agilent 7800", "تێبینی": ""},
    "Copper":           {"گروپ": "معدن", "نۆرماڵ": (70, 140), "یەکە": "μg/dL", "تەفسیر": "کۆپر",    "ئامێر": "Agilent 7800", "تێبینی": ""},
    "Magnesium":        {"گروپ": "معدن", "نۆرماڵ": (1.7, 2.5),"یەکە": "mg/dL", "تەفسیر": "مەگنیسیۆم","ئامێر": "Roche Cobas c502","تێبینی": ""},
    "Phosphorus":       {"گروپ": "معدن", "نۆرماڵ": (2.5, 4.5),"یەکە": "mg/dL", "تەفسیر": "فۆسفۆر",  "ئامێر": "Roche Cobas c502","تێبینی": ""},
}


# ============================================================
# ٨. داتابەسی دەرمانەکان
# ============================================================
DRUG_DATABASE = {
    "دژە پەستانی خوێن": {
        "کاپتۆپریل":     {"ڕێژە": "25-50mg",  "میکانیزم": "ACE inhibitor",       "کاریگەری لاوەکی": "کۆخە",        "پێچەوانە": "حەمل",       "وەسف": "کەمکردنەوەی پەستانی خوێن",  "بۆچی": "BP + پاراستنی گورچیلە", "تێبینی": ""},
        "ئەملۆدیپین":    {"ڕێژە": "5-10mg",   "میکانیزم": "Calcium blocker",     "کاریگەری لاوەکی": "ئاوسانی قاچ","پێچەوانە": "هەستیاری",   "وەسف": "فراوانکردنی خوێنبەر",       "بۆچی": "BP + ئازاری سنگ",       "تێبینی": ""},
        "لۆسارتان":      {"ڕێژە": "50-100mg", "میکانیزم": "ARB",                 "کاریگەری لاوەکی": "سەرگێژخواردن","پێچەوانە": "نەخۆشی گورچیلە","وەسف": "فراوانکردنی خوێنبەر",    "بۆچی": "BP",                    "تێبینی": ""},
        "بایسۆپرۆلۆل":  {"ڕێژە": "2.5-10mg", "میکانیزم": "Beta blocker",        "کاریگەری لاوەکی": "خاوکردنەوەی دڵ","پێچەوانە": "ئەستما",  "وەسف": "خاوکردنەوەی دڵ",          "بۆچی": "BP + دڵ",               "تێبینی": ""},
        "فورۆسیماید":    {"ڕێژە": "20-40mg",  "میکانیزم": "Loop diuretic",       "کاریگەری لاوەکی": "K نزم",       "پێچەوانە": "گورچیلە",   "وەسف": "دەرکردنی ئاو",              "بۆچی": "BP + ئاوسان",           "تێبینی": ""},
    },
    "دژە شەکرە": {
        "مێتفۆرمین":     {"ڕێژە": "500-2000mg","میکانیزم": "Biguanide",      "کاریگەری لاوەکی": "سکچوون",   "پێچەوانە": "گورچیلە",    "وەسف": "کەمکردنی شەکری جگەر",  "بۆچی": "شەکرەی جۆری ٢", "تێبینی": ""},
        "گلیپیزاید":     {"ڕێژە": "5-20mg",   "میکانیزم": "Sulfonylurea",    "کاریگەری لاوەکی": "هایپۆگلایسیمیا","پێچەوانە": "هەستیاری","وەسف": "هاندانی پەنکریاس",      "بۆچی": "شەکرەی جۆری ٢", "تێبینی": ""},
        "ئەنسولین Glargine":{"ڕێژە": "10-40 IU","میکانیزم": "Insulin analog","کاریگەری لاوەکی": "هایپۆگلایسیمیا","پێچەوانە": "هایپۆگلایسیمیا","وەسف": "ئەنسولینی درێژخایەن",  "بۆچی": "شەکرە",         "تێبینی": ""},
        "سیتاگلیپتین":   {"ڕێژە": "100mg",    "میکانیزم": "DPP-4 inhibitor", "کاریگەری لاوەکی": "سەرئێشە",  "پێچەوانە": "پەنکریاس",   "وەسف": "زیادکردنی GLP-1",      "بۆچی": "شەکرەی جۆری ٢", "تێبینی": ""},
        "لیراگلوتاید":   {"ڕێژە": "0.6-1.8mg","میکانیزم": "GLP-1 agonist",   "کاریگەری لاوەکی": "سکچوون",   "پێچەوانە": "پەنکریاس",   "وەسف": "کەمکردنەوەی کێش",      "بۆچی": "شەکرە + کێش",   "تێبینی": ""},
    },
    "دژە کۆخە": {
        "ئەمۆکسیسیلین": {"ڕێژە": "500mg", "میکانیزم": "Beta-lactam",  "کاریگەری لاوەکی": "زکچوون","پێچەوانە": "پێنیسیلین","وەسف": "ئەنتیبایۆتیک",      "بۆچی": "هەوکردن",       "تێبینی": ""},
        "ئازیترۆمایسین": {"ڕێژە": "500mg", "میکانیزم": "Macrolide",    "کاریگەری لاوەکی": "سکچوون","پێچەوانە": "دڵ",       "وەسف": "ئەنتیبایۆتیک",      "بۆچی": "هەوکردنی هەناسە","تێبینی": ""},
        "سیپرۆفلۆکساسین":{"ڕێژە": "500mg", "میکانیزم": "Fluoroquinolone","کاریگەری لاوەکی": "ئازاری ماسوولکە","پێچەوانە": "منداڵان","وەسف": "ئەنتیبایۆتیک",  "بۆچی": "هەوکردنی میز",   "تێبینی": ""},
        "سێفتریاکسۆن":   {"ڕێژە": "1-2g",  "میکانیزم": "Cephalosporin", "کاریگەری لاوەکی": "سکچوون","پێچەوانە": "هەستیاری", "وەسف": "ئەنتیبایۆتیک",      "بۆچی": "هەوکردنی توند",  "تێبینی": ""},
        "دۆکسیسایکلین":  {"ڕێژە": "100mg", "میکانیزم": "Tetracycline",  "کاریگەری لاوەکی": "زکچوون","پێچەوانە": "منداڵان",  "وەسف": "ئەنتیبایۆتیک",      "بۆچی": "هەوکردن",       "تێبینی": ""},
    },
    "دژە ئازار": {
        "ئەسپیرین":      {"ڕێژە": "75-300mg", "میکانیزم": "NSAID",     "کاریگەری لاوەکی": "سکچوون",   "پێچەوانە": "خوێنبەربوون","وەسف": "دژە ئازار + دژە تەمەن","بۆچی": "ئازار + مەبەست",  "تێبینی": ""},
        "ئیبۆپروفین":    {"ڕێژە": "200-400mg","میکانیزم": "NSAID",     "کاریگەری لاوەکی": "سکچوون",   "پێچەوانە": "گورچیلە",   "وەسف": "دژە ئازار",            "بۆچی": "ئازاری ماسوولکە", "تێبینی": ""},
        "پاراستامۆل":    {"ڕێژە": "500-1000mg","میکانیزم": "Analgesic","کاریگەری لاوەکی": "زیان بە جگەر","پێچەوانە": "جگەر",  "وەسف": "دژە ئازار",            "بۆچی": "سەرئێشە + تا",    "تێبینی": ""},
        "مۆرفین":        {"ڕێژە": "5-10mg",   "میکانیزم": "Opioid",    "کاریگەری لاوەکی": "خەوی",     "پێچەوانە": "هەناسە",    "وەسف": "دژە ئازاری بەهێز",     "بۆچی": "ئازاری توند",     "تێبینی": ""},
        "ترامادۆل":      {"ڕێژە": "50mg",     "میکانیزم": "Opioid",    "کاریگەری لاوەکی": "سەرگێژخواردن","پێچەوانە": "دڵ",     "وەسف": "دژە ئازار",            "بۆچی": "ئازاری مامناوەند","تێبینی": ""},
    },
    "دژە خوێن": {
        "وارفارین":       {"ڕێژە": "5mg",     "میکانیزم": "Vit K antagonist","کاریگەری لاوەکی": "خوێنبەربوون","پێچەوانە": "حەمل","وەسف": "دژە خوێن",   "بۆچی": "مەبەست",       "تێبینی": ""},
        "هێپارین":        {"ڕێژە": "5000 IU", "میکانیزم": "Anticoagulant",  "کاریگ make_q("پەستانی خوێنی نۆرماەری لاوەکی": "خوێنبەربوون","پێچەوانە": "خوێنبەربوون","وەسف": "دژە خوێنی خێرا","بۆچی": "مەبەست",  "تێبینی": ""},
        "کلۆپیدۆگرێل":   {"ڕێژە": "75mg",    "میکانیزم": "Antiplatelet",   "کاریگەری لاوەکی": "خوێنبەربوون","پێچەوانە": "خوێنبەربوون","وەسف": "دژە پلەیتلێت","بۆچی": "دڵی ئیسکیمیک","تێبینی": ""},
    },
    "دژە سکچوون": {
        "ئومەپرازۆل":   {"ڕێژە": "20-40mg","میکانیزم": "PPI",           "کاریگەری لاوەکی": "سەرئێشە","پێچەوانە": "جگەر","وەسف": "کەمکردنەوەی ترشێتی گەدە","بۆچی": "سکچوون",      "تێبینی": ""},
        "ڕانیتیدین":     {"ڕێژە": "150mg",  "میکانیزم": "H2 blocker",    "کاریگەری لاوەکی": "سەرگێژخواردن","پێچەوانە": "گورچیلە","وەسف": "کەمکردنەوەی ترشێتی","بۆچی": "سکچوون",      "تێبینی": ""},
    },
}


def get_drug_count() -> int:
    return sum(len(v) for v in DRUG_DATABASE.values())


def get_disease_count() -> int:
    return len(DISEASE_DATABASE)


def get_lab_count() -> int:
    return len(LAB_TESTS)
# ============================================================
# ٩. کویزەکان (بێ random — deterministic)
# ============================================================
# ⬅️ چاککراو: seed = 42 بۆ ئەوەی هەر جار کویزەکان یەکسان بن
@st.cache_data(show_spinner=False)
def generate_quizzes_by_level() -> List[Dict]:
    rng = random.Random(42)  # ⬅️ local RNG، جیاکراوە لە global

    def make_q(p, opts, ans):
        return {"پرسیار": p, "هەڵبژاردەکان": opts, "وەڵامی ڕاست": ans}

    pool = {
        1: [
            make_q("نیشانەی سەرەکی شەکرەی جۆری ٢ چییە؟", ["تینوویەتی زۆر", "سەرئێشە", "ئازاری سنگ", "کۆخە"], 0),
            make_q("پەستانی خوێنی نۆرماڵ چەندە؟", ["120/80", "140/90", "160/100", "180/110"], 0),
            make_q("کام دەرمانە بۆ شەکرە؟", ["مێتفۆرمین", "ئەسپیرین", "کاپتۆپرIL", "ئەمۆکسیسیلین"], 0),
            make_q("نیشانەی ئەنیمیا چییە؟", ["ماندوویی", "سەرئێشە", "ئازاری سنگ", "کۆخە"], 0),
            make_q("کام پشکنینە بۆ شەکرە؟", ["FBS", "ECG", "X-ray", "MRI"], 0),
            make_q("نیشانەی پەستانی خوێن چییە؟", ["سەرئێشە", "کۆخە", "تا", "سکچوون"], 0),
            make_q("کام دەرمانە بۆ ئازار؟", ["ئەسپیرین", "مێتفۆرمین", "ئەنسولین", "کاپتۆپریل"], 0),
            make_q("نیشانەی هەوکردنی سی چییە؟", ["تا و کۆخە", "سەرئێشە", "ئازاری سنگ", "ماندوویی"], 0),
        ],
        2: [
            make_q("HbA1c > 6.5% ئاماژەیە بۆ؟", ["شەکرە", "ئەنیمیا", "دڵ", "هەوکردن"], 0),
            make_q("BP > 140/90 نیشانەی؟", ["پەستانی خوێن", "دڵ", "شەکرە", "هەوکردن"], 0),
            make_q("MCV < 80 fL نیشانەی؟", ["ئەنیمیای مایکرۆسایتیک", "ماکرۆسایتیک", "نۆرمۆ", "هیمۆلایتیک"], 0),
            make_q("Troponin بەرز نیشانەی؟", ["نەخۆشی دڵ", "شەکرە", "هەوکردن", "ئەنیمیا"], 0),
            make_q("Creatinine بەرز نیشانەی؟", ["نەخۆشی گورچیلە", "جگەر", "دڵ", "شەکرە"], 0),
            make_q("ALT بەرز نیشانەی؟", ["نەخۆشی جگەر", "گورچیلە", "دڵ", "شەکرە"], 0),
            make_q("Ferritin نزم نیشانەی؟", ["ئەنیمیای ئاسن", "ماکرۆسایتیک", "هیمۆلایتیک", "شەکرە"], 0),
            make_q("C-peptide نزم لە شەکرەی جۆری؟", ["1", "2", "حەملی", "پێش شەکرە"], 0),
        ],
        3: [
            make_q("ST depression + Troponin elevated نیشانەی؟", ["نەخۆشی دڵی ئیسکیمیک", "شەکرە", "هەوکردن", "ئەنیمیا"], 0),
            make_q("Oligoclonal bands لە CSF نیشانەی؟", ["MS", "Alzheimer", "Parkinson", "Stroke"], 0),
            make_q("CAG تەنگی کرۆنەری نیشانەی؟", ["نەخۆشی دڵ", "شەکرە", "هەوکردن", "ئەنیمیا"], 0),
            make_q("AFP > 400 نیشانەی؟", ["نەخۆشی جگەر", "گورچیلە", "شەکرە", "هەوکردن"], 0),
            make_q("DAT scan کەم نیشانەی؟", ["Parkinson", "Alzheimer", "MS", "Stroke"], 0),
            make_q("MRI atrophy نیشانەی؟", ["Alzheimer", "Parkinson", "MS", "Stroke"], 0),
            make_q("Sputum AFB positive نیشانەی؟", ["سیل", "هەوکردن", "شەکرە", "دڵ"], 0),
            make_q("Echocardiogram EF < 40% نیشانەی؟", ["دڵی شکان", "ئیسکیمیک", "شەکرە", "هەوکردن"], 0),
        ],
        4: [
            make_q("CA19-9 بەرز نیشانەی؟", ["پەنکریاس", "جگەر", "گورچیلە", "شەکرە"], 0),
            make_q("PSA بەرز نیشانەی؟", ["پڕۆستات", "گورچیلە", "شەکرە", "هەوکردن"], 0),
            make_q("CA125 بەرز نیشانەی؟", ["هێلکەدان", "جگەر", "گورچیلە", "شەکرە"], 0),
            make_q("CEA بەرز نیشانەی؟", ["کۆلۆن", "جگەر", "گورچیلە", "شەکرە"], 0),
            make_q("LDH بەرز نیشانەی؟", ["هیمۆلایسیس", "جگەر", "گورچیلە", "شەکرە"], 0),
            make_q("Reticulocyte بەرز نیشانەی؟", ["هیمۆلایسیس", "جگەر", "گورچیلە", "شەکرە"], 0),
        ],
        5: [
            make_q("کام دەرمانە بۆ Hep C؟", ["Sofosbuvir", "Rifampicin", "Levodopa", "Warfarin"], 0),
            make_q("MRI plagues نیشانەی؟", ["MS", "Alzheimer", "Parkinson", "Stroke"], 0),
            make_q("VEP کەم نیشانەی؟", ["MS", "Alzheimer", "Parkinson", "Stroke"], 0),
            make_q("Bone marrow blast cells نیشانەی؟", ["لەوسیمیا", "جگەر", "گورچیلە", "شەکرە"], 0),
            make_q("PTT درێژ نیشانەی؟", ["هیمۆفیلیا", "جگەر", "گورچیلە", "شەکرە"], 0),
            make_q("Factor VIII نزم نیشانەی؟", ["هیمۆفیلیا A", "هیمۆفیلیا B", "جگەر", "شەکرە"], 0),
        ],
    }

    quizzes = []
    for level, questions in pool.items():
        for i in range(LEVELS[level]["quizzes"]):
            q = questions[i % len(questions)]
            quizzes.append({
                "پرسیار": q["پرسیار"],
                "هەڵبژاردەکان": q["هەڵبژاردەکان"],
                "وەڵامی ڕاست": q["وەڵامی ڕاست"],
                "ئاست": level,
                "ئاستی ناو": LEVELS[level]["name"],
                "ڕوونکردنەوە": f"ئاستی {LEVELS[level]['name']} - کویز {i+1}",
            })
    return quizzes


MEDICAL_QUIZZES = generate_quizzes_by_level()


def get_quizzes_for_level(level: int) -> List[Dict]:
    return [q for q in MEDICAL_QUIZZES if q.get("ئاست", 1) == level]


def get_quiz_count() -> int:
    return len(MEDICAL_QUIZZES)


# ============================================================
# ١٠. فانکشنە یاریدەدەرەکان
# ============================================================
def calculate_risk_score(disease: str, age: int, gender: str, symptoms: List[str] = None) -> int:
    base_risk = {"زۆر مەترسیدار": 80, "مەترسیدار": 60, "مامناوەند": 40, "کەم": 20}
    disease_info = DISEASE_DATABASE.get(disease, {})
    risk = base_risk.get(disease_info.get('ئاستی مەترسی', 'کەم'), 40)
    if age > 70: risk += 20
    elif age > 60: risk += 15
    elif age > 50: risk += 10
    elif age > 40: risk += 5
    if gender == 'نێر' and disease in ['نەخۆشی دڵی ئیسکیمیک']:
        risk += 10
    if symptoms:
        risk += min(len(symptoms) * 3, 15)
    return min(risk, 100)


def analyze_symptoms_advanced(symptoms: List[str], disease: str) -> Dict:
    disease_symptoms = set(DISEASE_DATABASE[disease]['نیشانەکان'])
    patient_symptoms = set(symptoms)
    match_count = len(patient_symptoms & disease_symptoms)
    total_disease = len(disease_symptoms)
    total_patient = len(patient_symptoms)
    return {
        "match_count": match_count,
        "match_percentage": round((match_count / total_disease) * 100, 1) if total_disease else 0,
        "coverage_percentage": round((match_count / total_patient) * 100, 1) if total_patient else 0,
        "matched_symptoms": list(patient_symptoms & disease_symptoms),
        "unmatched_disease_symptoms": list(disease_symptoms - patient_symptoms),
        "unmatched_patient_symptoms": list(patient_symptoms - disease_symptoms),
    }


def generate_random_lab_results() -> Dict:
    results = {}
    for test, info in LAB_TESTS.items():
        low, high = info["نۆرماڵ"]
        if random.random() < 0.7:
            value = round(random.uniform(low, high), 2)
            status = "نۆرماڵ"
        elif random.random() < 0.5:
            value = round(random.uniform(high, max(high * 1.5, high + 1)), 2)
            status = "بەرز"
        else:
            value = round(random.uniform(max(low * 0.5, 0), low), 2)
            status = "نزم"
        results[test] = {"value": value, "status": status, "unit": info["یەکە"]}
    return results


def analyze_lab_result(test_name: str, value: float) -> Dict:
    """⬅️ چاککراو: status ئینگلیزییە بۆ CSS"""
    if test_name not in LAB_TESTS:
        return {"status": "unknown", "label": "نەزانراو", "color": "#6c757d",
                "interpretation": "پشکنین نەدۆزرایەوە"}
    low, high = LAB_TESTS[test_name]["نۆرماڵ"]
    desc = LAB_TESTS[test_name]["تەفسیر"]
    if value < low:
        return {"status": "low", "label": "نزم", "color": "#ffc107",
                "interpretation": f"{desc} نزمە (نزمتر لە نۆرماڵ)"}
    if value > high:
        return {"status": "high", "label": "بەرز", "color": "#dc3545",
                "interpretation": f"{desc} بەرزە (بەرزتر لە نۆرماڵ)"}
    return {"status": "normal", "label": "نۆرماڵ", "color": "#28a745",
            "interpretation": f"{desc} نۆرماڵە"}


def generate_case_id() -> str:
    return f"CASE-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}"


def auto_save():
    if st.session_state.get("logged_in"):
        save_user_data(st.session_state.username, {
            "custom_lab_tests": st.session_state.custom_lab_tests,
            "custom_drugs": st.session_state.custom_drugs,
            "lab_notes": st.session_state.lab_notes,
            "drug_notes": st.session_state.drug_notes,
        })


# ============================================================
# ١١. داتای ڕاهێنان + مۆدێل (چاککراو)
# ============================================================
@st.cache_data(show_spinner=False)
def generate_training_data() -> pd.DataFrame:
    rng = random.Random(123)
    cases = []
    cid = 1
    for disease, info in DISEASE_DATABASE.items():
        for _ in range(8):
            age = rng.randint(18, 80)
            gender = rng.choice(['نێر', 'مێ'])
            syms = rng.sample(info['نیشانەکان'], min(3, len(info['نیشانەکان'])))
            cases.append({
                'case_id': f"CASE-{cid:04d}",
                'تەمەن': age,
                'ڕەگەز': gender,
                'نیشانە سەرەکییەکان': syms,
                'ئاستی مەترسی': info['ئاستی مەترسی'],
                'دەستنیشانکردن': disease,
                'نمرەی مەترسی': calculate_risk_score(disease, age, gender, syms),
            })
            cid += 1
    return pd.DataFrame(cases)


training_data = generate_training_data()


@st.cache_resource(show_spinner=False)
def train_prediction_model() -> Tuple:
    """
    ⬅️ چاککراو:
    - train_test_split بەکاردێت (نەک training accuracy)
    - نیشانەکان وەک boolean features (نەک لیست)
    - دروستی ڕاستەقینە پێوانە دەکرێت
    """
    try:
        data = training_data.copy()

        # کۆکردنەوەی هەموو نیشانەکان
        all_symptoms = set()
        for syms in data['نیشانە سەرەکییەکان']:
            all_symptoms.update(syms)
        all_symptoms = sorted(all_symptoms)

        # دروستکردنی feature matrix
        rows = []
        for _, r in data.iterrows():
            row = {
                'تەمەن': r['تەمەن'],
                'ڕەگەز_نێر': 1 if r['ڕەگەز'] == 'نێر' else 0,
            }
            for s in all_symptoms:
                row[f"sym_{s}"] = 1 if s in r['نیشانە سەرەکییەکان'] else 0
            rows.append(row)

        X = pd.DataFrame(rows)
        y = data['دەستنیشانکردن'].values

        # train/test split
        X_tr, X_te, y_tr, y_te = train_test_split(
            X, y, test_size=0.25, random_state=42, stratify=y
        )

        scaler = StandardScaler()
        X_tr_s = scaler.fit_transform(X_tr)
        X_te_s = scaler.transform(X_te)

        model = RandomForestClassifier(
            n_estimators=150, max_depth=12,
            min_samples_split=4, random_state=42, n_jobs=-1
        )
        model.fit(X_tr_s, y_tr)

        y_pred = model.predict(X_te_s)
        accuracy = accuracy_score(y_te, y_pred)

        return model, scaler, accuracy, list(X.columns)
    except Exception as e:
        return None, None, 0.0, []


model, scaler, model_accuracy, feature_cols = train_prediction_model()
# ============================================================
# ٩. کویزەکان (بێ random — deterministic)
# ============================================================
# ⬅️ چاککراو: seed = 42 بۆ ئەوەی هەر جار کویزەکان یەکسان بن
@st.cache_data(show_spinner=False)
def generate_quizzes_by_level() -> List[Dict]:
    rng = random.Random(42)  # ⬅️ local RNG، جیاکراوە لە global

    def make_q(p, opts, ans):
        return {"پرسیار": p, "هەڵبژاردەکان": opts, "وەڵامی ڕاست": ans}

    pool = {
        1: [
            make_q("نیشانەی سەرەکی شەکرەی جۆری ٢ چییە؟", ["تینوویەتی زۆر", "سەرئێشە", "ئازاری سنگ", "کۆخە"], 0),
            make_q("پەستانی خوێنی نۆرماڵ چەندە؟", ["120/80", "140/90", "160/100", "180/110"], 0),
            make_q("کام دەرمانە بۆ شەکرە؟", ["مێتفۆرمین", "ئەسپیرین", "کاپتۆپرIL", "ئەمۆکسیسیلین"], 0),
            make_q("نیشانەی ئەنیمیا چییە؟", ["ماندوویی", "سەرئێشە", "ئازاری سنگ", "کۆخە"], 0),
            make_q("کام پشکنینە بۆ شەکرە؟", ["FBS", "ECG", "X-ray", "MRI"], 0),
            make_q("نیشانەی پەستانی خوێن چییە؟", ["سەرئێشە", "کۆخە", "تا", "سکچوون"], 0),
            make_q("کام دەرمانە بۆ ئازار؟", ["ئەسپیرین", "مێتفۆرمین", "ئەنسولین", "کاپتۆپریل"], 0),
            make_q("نیشانەی هەوکردنی سی چییە؟", ["تا و کۆخە", "سەرئێشە", "ئازاری سنگ", "ماندوویی"], 0),
        ],
        2: [
            make_q("HbA1c > 6.5% ئاماژەیە بۆ؟", ["شەکرە", "ئەنیمیا", "دڵ", "هەوکردن"], 0),
            make_q("BP > 140/90 نیشانەی؟", ["پەستانی خوێن", "دڵ", "شەکرە", "هەوکردن"], 0),
            make_q("MCV < 80 fL نیشانەی؟", ["ئەنیمیای مایکرۆسایتیک", "ماکرۆسایتیک", "نۆرمۆ", "هیمۆلایتیک"], 0),
            make_q("Troponin بەرز نیشانەی؟", ["نەخۆشی دڵ", "شەکرە", "هەوکردن", "ئەنیمیا"], 0),
            make_q("Creatinine بەرز نیشانەی؟", ["نەخۆشی گورچیلە", "جگەر", "دڵ", "شەکرە"], 0),
            make_q("ALT بەرز نیشانەی؟", ["نەخۆشی جگەر", "گورچیلە", "دڵ", "شەکرە"], 0),
            make_q("Ferritin نزم نیشانەی؟", ["ئەنیمیای ئاسن", "ماکرۆسایتیک", "هیمۆلایتیک", "شەکرە"], 0),
            make_q("C-peptide نزم لە شەکرەی جۆری؟", ["1", "2", "حەملی", "پێش شەکرە"], 0),
        ],
        3: [
            make_q("ST depression + Troponin elevated نیشانەی؟", ["نەخۆشی دڵی ئیسکیمیک", "شەکرە", "هەوکردن", "ئەنیمیا"], 0),
            make_q("Oligoclonal bands لە CSF نیشانەی؟", ["MS", "Alzheimer", "Parkinson", "Stroke"], 0),
            make_q("CAG تەنگی کرۆنەری نیشانەی؟", ["نەخۆشی دڵ", "شەکرە", "هەوکردن", "ئەنیمیا"], 0),
            make_q("AFP > 400 نیشانەی؟", ["نەخۆشی جگەر", "گورچیلە", "شەکرە", "هەوکردن"], 0),
            make_q("DAT scan کەم نیشانەی؟", ["Parkinson", "Alzheimer", "MS", "Stroke"], 0),
            make_q("MRI atrophy نیشانەی؟", ["Alzheimer", "Parkinson", "MS", "Stroke"], 0),
            make_q("Sputum AFB positive نیشانەی؟", ["سیل", "هەوکردن", "شەکرە", "دڵ"], 0),
            make_q("Echocardiogram EF < 40% نیشانەی؟", ["دڵی شکان", "ئیسکیمیک", "شەکرە", "هەوکردن"], 0),
        ],
        4: [
            make_q("CA19-9 بەرز نیشانەی؟", ["پەنکریاس", "جگەر", "گورچیلە", "شەکرە"], 0),
            make_q("PSA بەرز نیشانەی؟", ["پڕۆستات", "گورچیلە", "شەکرە", "هەوکردن"], 0),
            make_q("CA125 بەرز نیشانەی؟", ["هێلکەدان", "جگەر", "گورچیلە", "شەکرە"], 0),
            make_q("CEA بەرز نیشانەی؟", ["کۆلۆن", "جگەر", "گورچیلە", "شەکرە"], 0),
            make_q("LDH بەرز نیشانەی؟", ["هیمۆلایسیس", "جگەر", "گورچیلە", "شەکرە"], 0),
            make_q("Reticulocyte بەرز نیشانەی؟", ["هیمۆلایسیس", "جگەر", "گورچیلە", "شەکرە"], 0),
        ],
        5: [
            make_q("کام دەرمانە بۆ Hep C؟", ["Sofosbuvir", "Rifampicin", "Levodopa", "Warfarin"], 0),
            make_q("MRI plagues نیشانەی؟", ["MS", "Alzheimer", "Parkinson", "Stroke"], 0),
            make_q("VEP کەم نیشانەی؟", ["MS", "Alzheimer", "Parkinson", "Stroke"], 0),
            make_q("Bone marrow blast cells نیشانەی؟", ["لەوسیمیا", "جگەر", "گورچیلە", "شەکرە"], 0),
            make_q("PTT درێژ نیشانەی؟", ["هیمۆفیلیا", "جگەر", "گورچیلە", "شەکرە"], 0),
            make_q("Factor VIII نزم نیشانەی؟", ["هیمۆفیلیا A", "هیمۆفیلیا B", "جگەر", "شەکرە"], 0),
        ],
    }

    quizzes = []
    for level, questions in pool.items():
        for i in range(LEVELS[level]["quizzes"]):
            q = questions[i % len(questions)]
            quizzes.append({
                "پرسیار": q["پرسیار"],
                "هەڵبژاردەکان": q["هەڵبژاردەکان"],
                "وەڵامی ڕاست": q["وەڵامی ڕاست"],
                "ئاست": level,
                "ئاستی ناو": LEVELS[level]["name"],
                "ڕوونکردنەوە": f"ئاستی {LEVELS[level]['name']} - کویز {i+1}",
            })
    return quizzes


MEDICAL_QUIZZES = generate_quizzes_by_level()


def get_quizzes_for_level(level: int) -> List[Dict]:
    return [q for q in MEDICAL_QUIZZES if q.get("ئاست", 1) == level]


def get_quiz_count() -> int:
    return len(MEDICAL_QUIZZES)


# ============================================================
# ١٠. فانکشنە یاریدەدەرەکان
# ============================================================
def calculate_risk_score(disease: str, age: int, gender: str, symptoms: List[str] = None) -> int:
    base_risk = {"زۆر مەترسیدار": 80, "مەترسیدار": 60, "مامناوەند": 40, "کەم": 20}
    disease_info = DISEASE_DATABASE.get(disease, {})
    risk = base_risk.get(disease_info.get('ئاستی مەترسی', 'کەم'), 40)
    if age > 70: risk += 20
    elif age > 60: risk += 15
    elif age > 50: risk += 10
    elif age > 40: risk += 5
    if gender == 'نێر' and disease in ['نەخۆشی دڵی ئیسکیمیک']:
        risk += 10
    if symptoms:
        risk += min(len(symptoms) * 3, 15)
    return min(risk, 100)


def analyze_symptoms_advanced(symptoms: List[str], disease: str) -> Dict:
    disease_symptoms = set(DISEASE_DATABASE[disease]['نیشانەکان'])
    patient_symptoms = set(symptoms)
    match_count = len(patient_symptoms & disease_symptoms)
    total_disease = len(disease_symptoms)
    total_patient = len(patient_symptoms)
    return {
        "match_count": match_count,
        "match_percentage": round((match_count / total_disease) * 100, 1) if total_disease else 0,
        "coverage_percentage": round((match_count / total_patient) * 100, 1) if total_patient else 0,
        "matched_symptoms": list(patient_symptoms & disease_symptoms),
        "unmatched_disease_symptoms": list(disease_symptoms - patient_symptoms),
        "unmatched_patient_symptoms": list(patient_symptoms - disease_symptoms),
    }


def generate_random_lab_results() -> Dict:
    results = {}
    for test, info in LAB_TESTS.items():
        low, high = info["نۆرماڵ"]
        if random.random() < 0.7:
            value = round(random.uniform(low, high), 2)
            status = "نۆرماڵ"
        elif random.random() < 0.5:
            value = round(random.uniform(high, max(high * 1.5, high + 1)), 2)
            status = "بەرز"
        else:
            value = round(random.uniform(max(low * 0.5, 0), low), 2)
            status = "نزم"
        results[test] = {"value": value, "status": status, "unit": info["یەکە"]}
    return results


def analyze_lab_result(test_name: str, value: float) -> Dict:
    """⬅️ چاککراو: status ئینگلیزییە بۆ CSS"""
    if test_name not in LAB_TESTS:
        return {"status": "unknown", "label": "نەزانراو", "color": "#6c757d",
                "interpretation": "پشکنین نەدۆزرایەوە"}
    low, high = LAB_TESTS[test_name]["نۆرماڵ"]
    desc = LAB_TESTS[test_name]["تەفسیر"]
    if value < low:
        return {"status": "low", "label": "نزم", "color": "#ffc107",
                "interpretation": f"{desc} نزمە (نزمتر لە نۆرماڵ)"}
    if value > high:
        return {"status": "high", "label": "بەرز", "color": "#dc3545",
                "interpretation": f"{desc} بەرزە (بەرزتر لە نۆرماڵ)"}
    return {"status": "normal", "label": "نۆرماڵ", "color": "#28a745",
            "interpretation": f"{desc} نۆرماڵە"}


def generate_case_id() -> str:
    return f"CASE-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}"


def auto_save():
    if st.session_state.get("logged_in"):
        save_user_data(st.session_state.username, {
            "custom_lab_tests": st.session_state.custom_lab_tests,
            "custom_drugs": st.session_state.custom_drugs,
            "lab_notes": st.session_state.lab_notes,
            "drug_notes": st.session_state.drug_notes,
        })


# ============================================================
# ١١. داتای ڕاهێنان + مۆدێل (چاککراو)
# ============================================================
@st.cache_data(show_spinner=False)
def generate_training_data() -> pd.DataFrame:
    rng = random.Random(123)
    cases = []
    cid = 1
    for disease, info in DISEASE_DATABASE.items():
        for _ in range(8):
            age = rng.randint(18, 80)
            gender = rng.choice(['نێر', 'مێ'])
            syms = rng.sample(info['نیشانەکان'], min(3, len(info['نیشانەکان'])))
            cases.append({
                'case_id': f"CASE-{cid:04d}",
                'تەمەن': age,
                'ڕەگەز': gender,
                'نیشانە سەرەکییەکان': syms,
                'ئاستی مەترسی': info['ئاستی مەترسی'],
                'دەستنیشانکردن': disease,
                'نمرەی مەترسی': calculate_risk_score(disease, age, gender, syms),
            })
            cid += 1
    return pd.DataFrame(cases)


training_data = generate_training_data()


@st.cache_resource(show_spinner=False)
def train_prediction_model() -> Tuple:
    """
    ⬅️ چاککراو:
    - train_test_split بەکاردێت (نەک training accuracy)
    - نیشانەکان وەک boolean features (نەک لیست)
    - دروستی ڕاستەقینە پێوانە دەکرێت
    """
    try:
        data = training_data.copy()

        # کۆکردنەوەی هەموو نیشانەکان
        all_symptoms = set()
        for syms in data['نیشانە سەرەکییەکان']:
            all_symptoms.update(syms)
        all_symptoms = sorted(all_symptoms)

        # دروستکردنی feature matrix
        rows = []
        for _, r in data.iterrows():
            row = {
                'تەمەن': r['تەمەن'],
                'ڕەگەز_نێر': 1 if r['ڕەگەز'] == 'نێر' else 0,
            }
            for s in all_symptoms:
                row[f"sym_{s}"] = 1 if s in r['نیشانە سەرەکییەکان'] else 0
            rows.append(row)

        X = pd.DataFrame(rows)
        y = data['دەستنیشانکردن'].values

        # train/test split
        X_tr, X_te, y_tr, y_te = train_test_split(
            X, y, test_size=0.25, random_state=42, stratify=y
        )

        scaler = StandardScaler()
        X_tr_s = scaler.fit_transform(X_tr)
        X_te_s = scaler.transform(X_te)

        model = RandomForestClassifier(
            n_estimators=150, max_depth=12,
            min_samples_split=4, random_state=42, n_jobs=-1
        )
        model.fit(X_tr_s, y_tr)

        y_pred = model.predict(X_te_s)
        accuracy = accuracy_score(y_te, y_pred)

        return model, scaler, accuracy, list(X.columns)
    except Exception as e:
        return None, None, 0.0, []


model, scaler, model_accuracy, feature_cols = train_prediction_model()
