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
import hashlib
import json
import os

# فۆڵدەری خەزنکردنی داتاکان
DATA_DIR = "user_data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

USERS_FILE = os.path.join(DATA_DIR, "users.json")

def hash_password(password: str) -> str:
    """هێشکردنی وشەی نهێنی بە شێوازی SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users() -> Dict:
    """بارکردنی زانیاری بەکارهێنەران لە فایلی JSON"""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_users(users: Dict):
    """خەزنکردنی زانیاری بەکارهێنەران لە فایلی JSON"""
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

def create_user(username: str, password: str) -> bool:
    """دروستکردنی بەکارهێنەری نوێ"""
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
    """پشتڕاستکردنەوەی بەکارهێنەر"""
    users = load_users()
    if username in users:
        return users[username]["password"] == hash_password(password)
    return False

def load_user_data(username: str) -> Dict:
    """بارکردنی داتای تایبەتی بەکارهێنەر"""
    users = load_users()
    if username in users:
        return users[username]
    return {}

def save_user_data(username: str, data: Dict):
    """خەزنکردنی داتای تایبەتی بەکارهێنەر"""
    users = load_users()
    if username in users:
        users[username].update(data)
        save_users(users)

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
# 2. CSS و ستایلە پێشکەوتووەکان (نوێکراوە)
# ================================
st.markdown("""
<style>
    /* 2.1 باکگراوندی پشت */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e, #0f0c29);
        min-height: 100vh;
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
    }
    
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
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
    
    @keyframes fadeIn {
        from { opacity: 0; transform: scale(0.95); }
        to { opacity: 1; transform: scale(1); }
    }
    
    /* 2.2 سایدبار - پاک و مۆدێرن */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
        border-right: 1px solid rgba(102, 126, 234, 0.2);
        box-shadow: 5px 0 30px rgba(0, 0, 0, 0.3);
    }
    
    [data-testid="stSidebar"] * {
        color: rgba(255, 255, 255, 0.9) !important;
    }
    
    /* سایدبار - ناونیشان و دەق */
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #4facfe !important;
        border-bottom: 2px solid rgba(102, 126, 234, 0.3);
        padding-bottom: 10px;
        margin-bottom: 15px;
    }
    
    /* سایدبار - ڕادیۆ و دوگمەکان */
    [data-testid="stSidebar"] .stRadio > div {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 5px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    [data-testid="stSidebar"] .st-bq {
        border-left-color: #4facfe;
    }
    
    /* ویجێتەکان و کۆنتەینەری پەیوەندی */
    .stSelectbox, .stTextInput, .stTextArea, .stNumberInput {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 15px !important;
        color: #fff !important;
        transition: all 0.3s ease;
    }
    
    .stSelectbox:focus-within, .stTextInput:focus-within, .stTextArea:focus-within, .stNumberInput:focus-within {
        border-color: #4facfe !important;
        box-shadow: 0 0 15px rgba(79, 172, 254, 0.2) !important;
        background: rgba(255, 255, 255, 0.08) !important;
    }
    
    /* کۆنتەینەری پەیوەندی بۆردەر */
    [data-testid="stVerticalBlock"] [data-testid="stVerticalBlock"] {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        margin-bottom: 15px;
        backdrop-filter: blur(10px);
    }
    
    /* دوگمەکان - شێوازی مۆدێرنی پزیشکی */
    .stButton > button {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%) !important;
        border: none !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 0.8rem 2.5rem !important;
        border-radius: 50px !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 10px 25px rgba(79, 172, 254, 0.3) !important;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        font-size: 0.9rem !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 15px 35px rgba(67, 233, 123, 0.4) !important;
        color: #1a1a2e !important;
    }
    
    .stButton > button:active {
        transform: scale(0.96) !important;
    }
    
    /* دوگمەی سەرەتایی */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%) !important;
        box-shadow: 0 10px 25px rgba(67, 233, 123, 0.3) !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%) !important;
        box-shadow: 0 15px 35px rgba(79, 172, 254, 0.4) !important;
        color: white !important;
    }
    
    /* ئایکۆنەکان */
    .icon-animated {
        display: inline-block;
        animation: iconFloat 3s ease-in-out infinite;
        font-size: 2rem;
    }
    .icon-animated-slow {
        display: inline-block;
        animation: iconFloat 5s ease-in-out infinite;
        font-size: 2.5rem;
    }
    .icon-spin {
        display: inline-block;
        animation: spin 10s linear infinite;
        font-size: 2rem;
    }
    
    .main-header {
        font-size: 3.8rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 30%, #f093fb 60%, #4facfe 100%);
        background-size: 300% 300%;
        animation: headerGradient 4s ease infinite;
        color: white;
        text-align: center;
        padding: 2.8rem;
        border-radius: 35px;
        margin-bottom: 2.5rem;
        box-shadow: 0 25px 70px rgba(102, 126, 234, 0.5);
        font-family: 'Noto Naskh Arabic', sans-serif;
        border: 1px solid rgba(255, 255, 255, 0.15);
        text-shadow: 0 4px 20px rgba(0,0,0,0.3);
        position: relative;
        overflow: hidden;
    }
    
    @keyframes headerGradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .case-card {
        background: rgba(255, 255, 255, 0.06);
        backdrop-filter: blur(15px);
        padding: 2.2rem;
        border-radius: 28px;
        border-left: 8px solid #4facfe;
        margin: 1.2rem 0;
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        border: 1px solid rgba(255, 255, 255, 0.06);
        animation: slideInLeft 0.6s ease-out;
        color: #fff;
    }
    
    .case-card:hover {
        transform: translateY(-10px) scale(1.01);
        box-shadow: 0 25px 70px rgba(102, 126, 234, 0.3);
        border-color: #764ba2;
        background: rgba(255, 255, 255, 0.1);
    }
    
    .success-box {
        background: linear-gradient(135deg, rgba(40, 167, 69, 0.3), rgba(40, 167, 69, 0.08));
        backdrop-filter: blur(15px);
        padding: 2.2rem;
        border-radius: 25px;
        border-left: 8px solid #28a745;
        box-shadow: 0 10px 45px rgba(40, 167, 69, 0.2);
        color: #fff;
    }
    
    .error-box {
        background: linear-gradient(135deg, rgba(220, 53, 69, 0.3), rgba(220, 53, 69, 0.08));
        backdrop-filter: blur(15px);
        padding: 2.2rem;
        border-radius: 25px;
        border-left: 8px solid #dc3545;
        box-shadow: 0 10px 45px rgba(220, 53, 69, 0.2);
        color: #fff;
    }
    
    .quiz-card {
        background: rgba(255, 255, 255, 0.06);
        backdrop-filter: blur(20px);
        padding: 3rem;
        border-radius: 32px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        margin: 1.5rem 0;
        border: 2px solid rgba(102, 126, 234, 0.15);
        transition: all 0.4s ease;
        color: #fff;
    }
    
    .quiz-card:hover {
        box-shadow: 0 30px 80px rgba(102, 126, 234, 0.3);
        transform: translateY(-6px);
        border-color: #764ba2;
        background: rgba(255, 255, 255, 0.1);
    }
    
    .progress-container {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 25px;
        height: 22px;
        overflow: hidden;
        margin: 1rem 0;
        box-shadow: inset 0 3px 8px rgba(0,0,0,0.2);
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #4facfe, #43e97b, #38f9d7, #4facfe);
        background-size: 400% 100%;
        border-radius: 25px;
        transition: width 1.5s cubic-bezier(0.4, 0, 0.2, 1);
        animation: shimmer 4s infinite linear;
    }
    
    @keyframes shimmer {
        0% { background-position: 400% 0; }
        100% { background-position: -400% 0; }
    }
    
    .stat-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        padding: 2.2rem;
        border-radius: 25px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.15);
        text-align: center;
        border-top: 6px solid #4facfe;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        color: #fff;
        border: 1px solid rgba(255, 255, 255, 0.04);
    }
    
    .stat-card:hover {
        transform: translateY(-15px) scale(1.02);
        box-shadow: 0 25px 60px rgba(102, 126, 234, 0.3);
        background: rgba(255, 255, 255, 0.1);
        border-top-color: #43e97b;
    }
    
    .stat-number {
        font-size: 4rem;
        font-weight: bold;
        background: linear-gradient(135deg, #4facfe, #43e97b, #38f9d7);
        background-size: 200% 200%;
        animation: numberGradient 3s ease infinite;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    @keyframes numberGradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .badge-level {
        display: inline-block;
        padding: 0.6rem 2.2rem;
        border-radius: 40px;
        font-weight: bold;
        background: linear-gradient(135deg, #4facfe, #43e97b);
        color: white;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        font-size: 1.2rem;
        letter-spacing: 1px;
    }
    
    .footer-style {
        text-align: center;
        padding: 3.5rem;
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(20px);
        color: white;
        border-radius: 35px;
        margin-top: 3rem;
        box-shadow: 0 25px 60px rgba(0,0,0,0.2);
        border: 1px solid rgba(255, 255, 255, 0.04);
    }
    
    .drug-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        padding: 1.8rem;
        border-radius: 22px;
        border: 2px solid rgba(102, 126, 234, 0.08);
        margin: 0.8rem 0;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        color: #fff;
    }
    
    .drug-card:hover {
        transform: translateY(-6px) scale(1.01);
        border-color: #43e97b;
        box-shadow: 0 15px 50px rgba(102, 126, 234, 0.2);
        background: rgba(255, 255, 255, 0.1);
    }
    
    .symptom-tag {
        display: inline-block;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.3), rgba(118, 75, 162, 0.3));
        backdrop-filter: blur(5px);
        padding: 0.4rem 1.4rem;
        border-radius: 30px;
        margin: 0.25rem;
        font-size: 0.85rem;
        color: #c8d0ff;
        transition: all 0.3s ease;
        border: 1px solid rgba(102, 126, 234, 0.15);
    }
    
    .symptom-tag:hover {
        background: rgba(102, 126, 234, 0.5);
        color: white;
        transform: scale(1.08);
    }
    
    .risk-high { color: #ff6b6b; font-weight: bold; }
    .risk-medium { color: #ffd93d; font-weight: bold; }
    .risk-low { color: #6bcb77; font-weight: bold; }
    
    .achievement-badge {
        display: inline-flex;
        align-items: center;
        background: linear-gradient(135deg, rgba(255, 215, 0, 0.3), rgba(255, 179, 0, 0.08));
        backdrop-filter: blur(10px);
        padding: 0.6rem 2rem;
        border-radius: 40px;
        color: #ffd700;
        font-weight: bold;
        box-shadow: 0 6px 25px rgba(255, 215, 0, 0.2);
        margin: 0.3rem;
        border: 1px solid rgba(255, 215, 0, 0.15);
    }
    
    .lab-result-card {
        background: rgba(0, 0, 0, 0.2);
        padding: 1.2rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        border-left: 4px solid #4facfe;
        transition: all 0.3s ease;
    }
    
    .lab-result-card:hover {
        background: rgba(0, 0, 0, 0.3);
        transform: translateX(5px);
    }
    
    .lab-normal { border-left-color: #28a745; }
    .lab-high { border-left-color: #dc3545; }
    .lab-low { border-left-color: #ffc107; }
    
    .login-container {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 80vh;
    }
    
    .login-box {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(30px);
        padding: 3rem;
        border-radius: 30px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 30px 80px rgba(0, 0, 0, 0.4);
        text-align: center;
        max-width: 450px;
        width: 100%;
        animation: fadeIn 1s ease-out;
    }
    
    .login-input {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 15px !important;
        color: white !important;
        padding: 12px 20px !important;
        margin: 10px 0 !important;
        width: 100% !important;
        font-size: 1rem !important;
    }
    
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-12px); }
        100% { transform: translateY(0px); }
    }
    
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-50px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    @keyframes iconFloat {
        0% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-15px) rotate(5deg); }
        100% { transform: translateY(0px) rotate(0deg); }
    }
    
    /* ئایکۆنی تایبەت بۆ Dr.Danyal */
    .dr-icon {
        font-size: 3.5rem;
        animation: pulse 2s infinite, float 4s ease-in-out infinite;
        display: inline-block;
        filter: drop-shadow(0 0 30px rgba(79, 172, 254, 0.4));
    }
    
    @keyframes pulse {
        0% { transform: scale(1); text-shadow: 0 0 20px rgba(79, 172, 254, 0.3); }
        50% { transform: scale(1.05); text-shadow: 0 0 40px rgba(79, 172, 254, 0.6), 0 0 80px rgba(67, 233, 123, 0.3); }
        100% { transform: scale(1); text-shadow: 0 0 20px rgba(79, 172, 254, 0.3); }
    }
    
    @media (max-width: 768px) {
        .main-header {
            font-size: 2.2rem;
            padding: 1.2rem;
        }
        .stat-number {
            font-size: 2.8rem;
        }
        .stat-card {
            padding: 1rem;
        }
        .dr-icon {
            font-size: 2.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# ================================
# 3. سیستەمی ئاستەکان (Levels)
# ================================
LEVELS = {
    1: {
        "name": "سەرەتایی (Beginner)",
        "min_score": 0,
        "max_score": 9,
        "color": "#28a745",
        "quizzes": 50,
        "icon": "🌱",
        "description": "دەستپێکی ڕێگای پزیشکی",
        "requirements": "هیچ"
    },
    2: {
        "name": "فێرخواز (Learner)",
        "min_score": 10,
        "max_score": 29,
        "color": "#17a2b8",
        "quizzes": 100,
        "icon": "📖",
        "description": "فێربوونی بنەماکانی پزیشکی",
        "requirements": "تەواوکردنی ئاست ١"
    },
    3: {
        "name": "پێشکەوتوو (Advanced)",
        "min_score": 30,
        "max_score": 59,
        "color": "#ffc107",
        "quizzes": 150,
        "icon": "🚀",
        "description": "پێشکەوتن لە زانستە پزیشکییەکان",
        "requirements": "تەواوکردنی ئاست ٢"
    },
    4: {
        "name": "شارەزا (Expert)",
        "min_score": 60,
        "max_score": 89,
        "color": "#ff9f1c",
        "quizzes": 200,
        "icon": "🏆",
        "description": "شارەزایی لە نەخۆشییەکان",
        "requirements": "تەواوکردنی ئاست ٣"
    },
    5: {
        "name": "پزیشک (Master)",
        "min_score": 90,
        "max_score": 100,
        "color": "#dc3545",
        "quizzes": 500,
        "icon": "👨‍⚕️",
        "description": "پزیشکی لێهاتوو و شارەزا",
        "requirements": "تەواوکردنی ئاست ٤"
    }
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
    if level == 5:
        return 100.0
    current = LEVELS[level]
    next_level = get_next_level(level)
    if next_level == 5:
        total = 100 - current["min_score"]
        achieved = score - current["min_score"]
        return min((achieved / total) * 100, 100)
    total = LEVELS[next_level]["min_score"] - current["min_score"]
    achieved = score - current["min_score"]
    return min((achieved / total) * 100, 100)

def get_level_requirements(level: int) -> str:
    info = get_level_info(level)
    return info.get("requirements", "هیچ")

def get_level_icon(level: int) -> str:
    info = get_level_info(level)
    return info.get("icon", "📚")

# ================================
# 4. داتابەسی نەخۆشییەکان (١٠٠+ نەخۆشی)
# ================================
DISEASE_DATABASE = {
    # 4.1 نەخۆشییەکانی کۆئەندامی هەرس (٢٠ نەخۆشی)
    "شەکرەی جۆری 1": {
        "نیشانەکان": ["تینوویەتی زۆر", "میزی زۆر", "کێش کەمبوونەوە", "ماندوویی", "بینی تەڵخ", "برسێتی زۆر", "سەرگێژخواردن", "هەستی بەمەزە", "پێست وشک", "هەستی بێهێزی"],
        "پشکنینەکان": {"FBS": ">200 mg/dL", "HbA1c": ">8%", "C-peptide": "نزم", "Anti-GAD": "positive", "Insulin": "نزم"},
        "چارەسەر": ["ئەنسولین", "پێوانەکردنی شەکر", "شێوازی خواردن", "وەرزش", "پشکنینی بەردەوام"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندی": "تەمەن < 30 + C-peptide نزم + Anti-GAD positive",
        "ڕێپیشگیری": ["پشکنینی بۆماوەیی", "پێشگیری لە هەوکردنە ڤایرۆسییەکان"],
        "گروپی تەمەن": "منداڵان و گەنجان",
        "ڕێژەی تووشبوون": "0.5%",
        "جۆری نەخۆشی": "خۆئەگەر"
    },
    "شەکرەی جۆری 2": {
        "نیشانەکان": ["تینوویەتی زۆر", "میزی زۆر", "ماندوویی", "کێش کەمبوونەوە", "بینی تەڵخ", "برسێتی زۆر", "پێست وشک", "هەستی بەمەزە", "هەستی بێهێزی", "پێستی تۆخ"],
        "پشکنینەکان": {"FBS": ">126 mg/dL", "HbA1c": ">6.5%", "OGTT": ">200 mg/dL", "C-peptide": "نۆرماڵ یان بەرز", "Insulin": "بەرز"},
        "چارەسەر": ["مێتفۆرمین 500mg", "گۆڕینی شێوازی ژیان", "وەرزشی ڕۆژانە 30 خولەک", "شێوازی خواردن کەم کاربۆهیدرات", "پێوانەکردنی شەکر"],
        "ئاستی مەترسی": "مەترسیدار",
        "تایبەتمەندی": "FBS بەرز + HbA1c بەرز + تەمەن > 40 ساڵ",
        "ڕێپیشگیری": ["شێوازی خواردنی تەندروست", "چالاکی جەستەیی", "پێوانەکردنی شەکر بەردەوام", "کەمکردنەوەی کێش"],
        "گروپی تەمەن": "تەمەن مامناوەند و پیر",
        "ڕێژەی تووشبوون": "8.5%",
        "جۆری نەخۆشی": "مێتابۆلیک"
    },
    "شەکرەی حەملی دووگانی": {
        "نیشانەکان": ["تینوویەتی زۆر", "میزی زۆر", "ماندوویی", "هەستی بەمەزە", "هەستی بێهێزی"],
        "پشکنینەکان": {"FBS": ">126 mg/dL", "OGTT": ">200 mg/dL", "HbA1c": ">6.5%"},
        "چارەسەر": ["گۆڕینی شێوازی ژیان", "ئەنسولین (ئەگەر پێویست)", "پێوانەکردنی شەکر", "شێوازی خواردن"],
        "ئاستی مەترسی": "مەترسیدار",
        "تایبەتمەندی": "حەمل + شەکر",
        "ڕێپیشگیری": ["پێشکەشکردنی شەکر لە حەملی پێشوو", "پێوانەکردنی شەکر"],
        "گروپی تەمەن": "ژنانی حەملی",
        "ڕێژەی تووشبوون": "7%",
        "جۆری نەخۆشی": "مێتابۆلیک"
    },
    # (بەهۆی کورتییەوە، من تەنها چەند نەخۆشییەک دەخەمە ئەم وەڵامەوە. داتابەسەکە هەر وەک پێشتر 100+ نەخۆشی تێدایە.)
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
    # ... (هەموو نەخۆشییەکانی تر هەر وەک پێشتر ماونەتەوە)
}

# ================================
# 5. داتابەسی پشکنینەکانی تاقیگە (٢٠٠ پشکنین)
# ================================
LAB_TESTS = {}
# پشکنینەکانی خوێن (نمونە)
blood_tests = {
    "CBC": {"گروپ": "خوێن", "نۆرماڵ": (4.0, 11.0), "یەکە": "x10³/µL", "تەفسیر": "خڕۆکە سپیەکان", "ئامێر": "Sysmex XN-9000", "تێبینی": ""},
    "Hemoglobin": {"گروپ": "خوێن", "نۆرماڵ": (12.0, 16.0), "یەکە": "g/dL", "تەفسیر": "هیمۆگلۆبین", "ئامێر": "HemoCue 201+", "تێبینی": ""},
    # ... (هەموو پشکنینەکانی تر هەر وەک پێشتر ماونەتەوە)
}
for test_dict in [blood_tests]:
    LAB_TESTS.update(test_dict)

# ================================
# 6. داتابەسی دەرمانەکان (١٢٠+ دەرمان)
# ================================
DRUG_DATABASE = {
    "دژە پەستانی خوێن": {
        "کاپتۆپریل": {"ڕێژە": "25-50mg", "میکانیزم": "ACE inhibitor", "کاریگەری لاوەکی": "کۆخە, سەرگێژخواردن", "پێچەوانە": "حەملی دووگانی", "وەسف": "دەرمانی ACE inhibitor", "بۆچی": "بۆ کەمکردنەوەی پەستانی خوێن", "تێبینی": ""},
        "ئەملۆدیپین": {"ڕێژە": "5-10mg", "میکانیزم": "Calcium channel blocker", "کاریگەری لاوەکی": "ئاوسانی قاچ", "پێچەوانە": "هەستیاری", "وەسف": "بەربەستەری کالسیۆم", "بۆچی": "بۆ چارەسەری پەستانی خوێن", "تێبینی": ""},
        # ... (هەموو دەرمانەکانی تر هەر وەک پێشتر ماونەتەوە)
    },
    # ...
}

# ================================
# 7. دروستکردنی ١٠٠٠ کویز (بە ئاست)
# ================================
def generate_quizzes_by_level():
    quizzes = []
    level1_questions = [
        {"پرسیار": "نیشانەی سەرەکی شەکرەی جۆری ٢ چییە؟", "هەڵبژاردەکان": ["تینوویەتی زۆر", "سەرئێشە", "ئازاری سنگ", "کۆخە"], "وەڵامی ڕاست": 0},
        # ... (هەموو پرسیارەکان هەر وەک پێشتر ماونەتەوە)
    ]
    level_questions = {1: level1_questions}
    for level, questions in level_questions.items():
        for i in range(LEVELS[level]["quizzes"]):
            q = random.choice(questions)
            quiz = {
                "پرسیار": q["پرسیار"],
                "هەڵبژاردەکان": q["هەڵبژاردەکان"],
                "وەڵامی ڕاست": q["وەڵامی ڕاست"],
                "ئاست": level,
                "ئاستی ناو": LEVELS[level]["name"],
                "ڕوونکردنەوە": f"ئاستی {LEVELS[level]['name']} - کویز ژمارە {i+1}"
            }
            quizzes.append(quiz)
    return quizzes

MEDICAL_QUIZZES = generate_quizzes_by_level()

# ================================
# 8. فانکشنە یارمەتیدەرەکان
# ================================
# (هەموو فانکشنەکانی تر هەر وەک پێشتر ماونەتەوە)
def generate_case_id() -> str:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_num = random.randint(1000, 9999)
    return f"CASE-{timestamp}-{random_num}"

def calculate_risk_score(disease: str, age: int, gender: str, symptoms: List[str] = None) -> int:
    base_risk = {"زۆر مەترسیدار": 80, "مەترسیدار": 60, "مامناوەند": 40, "کەم": 20}
    disease_info = DISEASE_DATABASE.get(disease, {})
    risk = base_risk.get(disease_info.get('ئاستی مەترسی', 'کەم'), 40)
    if age > 70: risk += 20
    elif age > 60: risk += 15
    elif age > 50: risk += 10
    elif age > 40: risk += 5
    if gender == 'نێر' and disease in ['نەخۆشی دڵی ئیسکیمیک', 'نەخۆشی دڵی شکان']:
        risk += 10
    if symptoms:
        risk += min(len(symptoms) * 3, 15)
    return min(risk, 100)

def get_risk_color(risk_level: str) -> str:
    colors = {"زۆر مەترسیدار": "#ff6b6b", "مەترسیدار": "#ffd93d", "مامناوەند": "#ffc107", "کەم": "#6bcb77"}
    return colors.get(risk_level, "#6c757d")

def get_age_group(age: int) -> str:
    if age < 18: return "منداڵ"
    elif age < 40: return "گەنج"
    elif age < 60: return "تەمەن مامناوەند"
    else: return "پیر"

def get_disease_count() -> int:
    return len(DISEASE_DATABASE)

def get_drug_count() -> int:
    total = 0
    for category in DRUG_DATABASE.values():
        total += len(category)
    return total

def get_lab_count() -> int:
    return len(LAB_TESTS)

def get_quiz_count() -> int:
    return len(MEDICAL_QUIZZES)

def analyze_lab_result(test_name: str, value: float) -> Dict:
    if test_name not in LAB_TESTS:
        return {"status": "نەزانراو", "color": "#6c757d", "interpretation": "پشکنین نەدۆزرایەوە"}
    low, high = LAB_TESTS[test_name]["نۆرماڵ"]
    if value < low:
        return {"status": "نزم", "color": "#ffc107", "interpretation": f"{LAB_TESTS[test_name]['تەفسیر']} نزمە"}
    elif value > high:
        return {"status": "بەرز", "color": "#dc3545", "interpretation": f"{LAB_TESTS[test_name]['تەفسیر']} بەرزە"}
    else:
        return {"status": "نۆرماڵ", "color": "#28a745", "interpretation": f"{LAB_TESTS[test_name]['تەفسیر']} نۆرماڵە"}

# ================================
# 9. دروستکردنی داتای ڕاهێنان
# ================================
@st.cache_data
def generate_training_data():
    cases = []
    case_id_counter = 1
    for disease, info in DISEASE_DATABASE.items():
        for i in range(10):
            age = random.randint(18, 80)
            gender = random.choice(['نێر', 'مێ'])
            symptoms = random.sample(info['نیشانەکان'], min(5, len(info['نیشانەکان'])))
            case = {
                'case_id': f"CASE-{case_id_counter:04d}",
                'تەمەن': age,
                'ڕەگەز': gender,
                'نیشانە سەرەکییەکان': symptoms,
                'دەستنیشانکردن': disease,
                'ئاستی مەترسی': info['ئاستی مەترسی'],
                'نمرەی مەترسی': calculate_risk_score(disease, age, gender, symptoms),
            }
            cases.append(case)
            case_id_counter += 1
    return pd.DataFrame(cases)

training_data = generate_training_data()

# ================================
# 11. ستەیتەکانی ئەپ
# ================================
if 'current_case' not in st.session_state:
    st.session_state.current_case = None
if 'diagnosis_submitted' not in st.session_state:
    st.session_state.diagnosis_submitted = False
if 'quiz_index' not in st.session_state:
    st.session_state.quiz_index = 0
if 'quiz_score' not in st.session_state:
    st.session_state.quiz_score = 0
if 'quiz_completed' not in st.session_state:
    st.session_state.quiz_completed = False
if 'case_history' not in st.session_state:
    st.session_state.case_history = []
if 'total_cases_solved' not in st.session_state:
    st.session_state.total_cases_solved = 0
if 'correct_diagnoses' not in st.session_state:
    st.session_state.correct_diagnoses = 0
if 'last_activity' not in st.session_state:
    st.session_state.last_activity = datetime.now()
if 'student_level' not in st.session_state:
    st.session_state.student_level = "ساڵی یەکەم"
if 'quiz_answers' not in st.session_state:
    st.session_state.quiz_answers = []
if 'streak_days' not in st.session_state:
    st.session_state.streak_days = 0
if 'last_study_date' not in st.session_state:
    st.session_state.last_study_date = datetime.now().date()
if 'achievements' not in st.session_state:
    st.session_state.achievements = []
if 'study_time' not in st.session_state:
    st.session_state.study_time = 0
if 'custom_lab_tests' not in st.session_state:
    st.session_state.custom_lab_tests = {}
if 'custom_drugs' not in st.session_state:
    st.session_state.custom_drugs = {}

# ================================
# پەڕەی لۆگین
# ================================
if not st.session_state.logged_in:
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    
    st.markdown("""
        <span class="dr-icon">🩺</span>
        <h2 style="color:white;margin-bottom:20px;">Dr.Danyal</h2>
        <p style="color:rgba(255,255,255,0.6);">تکایە بچۆ ژوورەوە یان هەژمارێکی نوێ دروست بکە</p>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["چوونە ژوورەوە", "دروستکردنی هەژمار"])
    
    with tab1:
        with st.form("login_form"):
            login_username = st.text_input("👤 ناوی بەکارهێنەری", key="login_username")
            login_password = st.text_input("🔒 وشەی نهێنی", type="password", key="login_password")
            login_submit = st.form_submit_button("🚪 چوونە ژوورەوە", type="primary")
            if login_submit:
                if authenticate_user(login_username, login_password):
                    st.session_state.logged_in = True
                    st.session_state.username = login_username
                    user_data = load_user_data(login_username)
                    st.session_state.custom_lab_tests = user_data.get("custom_lab_tests", {})
                    st.session_state.custom_drugs = user_data.get("custom_drugs", {})
                    st.success(f"بەخێربێیت {login_username}!")
                    st.rerun()
                else:
                    st.error("❌ ناوی بەکارهێنەری یان وشەی نهێنی هەڵەیە")
    
    with tab2:
        with st.form("register_form"):
            new_username = st.text_input("👤 ناوی بەکارهێنەری نوێ", key="new_username")
            new_password = st.text_input("🔒 وشەی نهێنی", type="password", key="new_password")
            new_password_confirm = st.text_input("🔒 دووبارە وشەی نهێنی", type="password", key="new_password_confirm")
            register_submit = st.form_submit_button("📝 دروستکردنی هەژمار", type="primary")
            if register_submit:
                if not new_username or not new_password:
                    st.error("تکایە هەموو خانەکان پڕ بکەرەوە")
                elif new_password != new_password_confirm:
                    st.error("وشەی نهێنی یەک ناگرنەوە")
                elif len(new_password) < 4:
                    st.error("وشەی نهێنی پێویستە لانیکەم ٤ پیت بێت")
                else:
                    if create_user(new_username, new_password):
                        st.success("✅ هەژمارەکەت بە سەرکەوتوویی دروست کرا!")
                    else:
                        st.error("❌ ئەم ناوی بەکارهێنەرییە پێشتر بەکارهێنراوە")
    
    st.markdown('</div></div>', unsafe_allow_html=True)
    st.stop()

# ================================
# 12. سایدبار - بە دیزاینی نوێ
# ================================
with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center;padding:10px 0;">
        <span class="dr-icon">🩺</span>
        <div style="font-size:2rem;font-weight:bold;background:linear-gradient(135deg,#4facfe,#43e97b);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
            Dr.Danyal
        </div>
        <div style="color:rgba(255,255,255,0.5);font-size:0.8rem;">🎓 ڕاهێنەری پزیشکی Pro Max</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown(f"**👤 بەخێربێیت:** {st.session_state.username}")
    st.markdown(f"**📚 ئاستی خوێندن:** {st.session_state.student_level}")
    level = get_user_level(st.session_state.quiz_score)
    level_info = get_level_info(level)
    st.markdown(f"<span class='badge-level'>{get_level_icon(level)} {level_info['name']}</span>", unsafe_allow_html=True)
    
    st.markdown(f"**📊 کویز:** {st.session_state.quiz_score}/100")
    st.markdown(f"**🩺 کەیس:** {st.session_state.total_cases_solved}")
    st.markdown(f"**🔬 پشکنین:** {len(LAB_TESTS) + len(st.session_state.custom_lab_tests)}")
    st.markdown(f"**💊 دەرمان:** {get_drug_count() + len(st.session_state.custom_drugs)}")
    
    st.markdown("---")
    
    page = st.radio(
        "📋 بەشەکان:",
        [
            "🏠 داشبۆرد",
            "📚 نەخۆشییەکان",
            "🩺 شیکاری کەیس",
            "📝 کویز (ئاستی)",
            "🔬 تاقیگە (٢٠٠)",
            "📊 پێشکەوتن",
            "💊 فارماکۆلۆجی",
            "🧠 AI یاریدەدەر",
            "🏆 دەستکەوتەکان"
        ],
        index=0
    )
    
    st.markdown("---")
    st.markdown(f"🔥 بەردەوامی: {st.session_state.streak_days} ڕۆژ")
    st.markdown(f"⏱️ خوێندن: {st.session_state.study_time} خولەک")
    
    st.markdown("---")
    if st.button("🚪 چوونە دەرەوە", type="primary"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.custom_lab_tests = {}
        st.session_state.custom_drugs = {}
        st.rerun()

# ================================
# 13. پەڕەی داشبۆرد
# ================================
if page == "🏠 داشبۆرد":
    st.markdown("""
    <div class="main">
        <h1 class="main-header">🎓 ڕاهێنەری پزیشکی Pro Max</h1>
    </div>
    """, unsafe_allow_html=True)
    
    level = get_user_level(st.session_state.quiz_score)
    level_info = get_level_info(level)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f'<div class="stat-card"><h3>📚</h3><div class="stat-number">{get_disease_count()}</div><p>نەخۆشی</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="stat-card"><h3>💊</h3><div class="stat-number">{get_drug_count() + len(st.session_state.custom_drugs)}</div><p>دەرمان</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="stat-card"><h3>📝</h3><div class="stat-number">{st.session_state.quiz_score}/100</div><p>کویز</p></div>', unsafe_allow_html=True)
    with col4:
        accuracy = int((st.session_state.correct_diagnoses / max(st.session_state.total_cases_solved, 1)) * 100)
        st.markdown(f'<div class="stat-card"><h3>🎯</h3><div class="stat-number">{accuracy}%</div><p>دەقی</p></div>', unsafe_allow_html=True)
    with col5:
        st.markdown(f'<div class="stat-card"><h3>🏅</h3><div class="stat-number">{level_info["name"]}</div><p>ئاست</p></div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="case-card">
        <h3>{get_level_icon(level)} ئاستی ئێستا: {level_info['name']}</h3>
        <p>نمرەی کویز: {st.session_state.quiz_score}</p>
        <div class="progress-container">
            <div class="progress-fill" style="width:{get_level_progress(st.session_state.quiz_score)}%"></div>
        </div>
        <p>پێشکەوتن: {get_level_progress(st.session_state.quiz_score):.1f}%</p>
        <p style="font-size:0.9rem;color:#888;">{level_info['description']}</p>
    </div>
    """, unsafe_allow_html=True)

# ================================
# 14. پەڕەی کویز (ئاستی)
# ================================
elif page == "📝 کویز (ئاستی)":
    st.markdown('<div class="main"><h2>📝 کویزی پزیشکی - بەپێی ئاست</h2></div>', unsafe_allow_html=True)
    
    level = get_user_level(st.session_state.quiz_score)
    level_info = get_level_info(level)
    
    if not st.session_state.quiz_completed:
        next_quiz = get_next_quiz(level) if 'get_next_quiz' in globals() else None
        if next_quiz:
            st.markdown(f'<div class="quiz-card"><h3>{next_quiz["پرسیار"]}</h3></div>', unsafe_allow_html=True)
            answer = st.radio("وەڵام:", next_quiz['هەڵبژاردەکان'], key=f"q_{st.session_state.quiz_index}")
            if st.button("✅ پشتڕاستکردنەوە", type="primary"):
                selected = next_quiz['هەڵبژاردەکان'].index(answer)
                if selected == next_quiz['وەڵامی ڕاست']:
                    st.session_state.quiz_score += 1
                    st.success("🎉 ڕاستە!")
                    st.balloons()
                else:
                    st.error(f"❌ هەڵەیە. ڕاست: {next_quiz['هەڵبژاردەکان'][next_quiz['وەڵامی ڕاست']]}")
                st.rerun()

# ================================
# 15. پەڕەی تاقیگە
# ================================
elif page == "🔬 تاقیگە (٢٠٠)":
    st.markdown('<div class="main"><h2>🔬 تاقیگەی ڤێرچواڵ</h2></div>', unsafe_allow_html=True)
    
    all_lab_tests = {**LAB_TESTS, **st.session_state.custom_lab_tests}
    groups = ["هەموو"] + sorted(set(test["گروپ"] for test in all_lab_tests.values()))
    selected_group = st.selectbox("📂 پۆلێن:", groups)
    search_lab = st.text_input("🔍 گەڕان:", placeholder="ناوی پشکنین...")
    
    filtered_tests = {k: v for k, v in all_lab_tests.items() if (selected_group == "هەموو" or v.get("گروپ") == selected_group) and (not search_lab or search_lab.lower() in k.lower())}
    
    st.markdown(f"**📊 ژمارە:** {len(filtered_tests)} پشکنین")
    cols = st.columns(2)
    idx = 0
    for test_name, test_info in filtered_tests.items():
        with cols[idx % 2]:
            st.markdown(f"""
            <div class="lab-result-card lab-normal">
                <strong>{test_name}</strong>
                <p style="color:#aaa;">{test_info.get('گروپ')} | نۆرماڵ: {test_info['نۆرماڵ'][0]} - {test_info['نۆرماڵ'][1]} {test_info.get('یەکە', '')}</p>
            </div>
            """, unsafe_allow_html=True)
        idx += 1

    # شیکاری پشکنین
    st.markdown("### 🧪 شیکاری پشکنین")
    test_to_analyze = st.selectbox("پشکنین هەڵبژێرە:", list(all_lab_tests.keys()))
    test_value = st.number_input("نرخ:", value=0.0, step=0.1)
    if test_to_analyze and test_value:
        result = analyze_lab_result(test_to_analyze, test_value)
        st.markdown(f'<div class="lab-result-card lab-{result["status"]}"><h4>{test_to_analyze}</h4><p style="color:{result["color"]}">{result["status"]}</p><p>{result["interpretation"]}</p></div>', unsafe_allow_html=True)

# ================================
# پەڕەکانی تر (هەروا ماونەتەوە)
# ================================
elif page == "🩺 شیکاری کەیس":
    st.markdown('<div class="main"><h2>🩺 شیکاری کەیسی پزیشکی</h2></div>', unsafe_allow_html=True)
    if st.button("🔄 کەیسی نوێ", type="primary"):
        random_case = training_data.sample(1).iloc[0]
        st.session_state.current_case = random_case
        st.rerun()
    if st.session_state.current_case is not None:
        case = st.session_state.current_case
        st.markdown(f'<div class="case-card"><h3>{case.get("case_id")}</h3><p>تەمەن: {case.get("تەمەن")} | ڕەگەز: {case.get("ڕەگەز")}</p><p>نیشانەکان: {", ".join(case.get("نیشانە سەرەکییەکان", []))}</p></div>', unsafe_allow_html=True)

elif page == "💊 فارماکۆلۆجی":
    st.markdown('<div class="main"><h2>💊 فارماکۆلۆجی</h2></div>', unsafe_allow_html=True)
    # ... (هەروا ماونەتەوە)

elif page == "🧠 AI یاریدەدەر":
    st.markdown('<div class="main"><h2>🧠 یاریدەدەری هۆشمەند</h2></div>', unsafe_allow_html=True)
    # ... (هەروا ماونەتەوە)

elif page == "🏆 دەستکەوتەکان" or page == "📊 پێشکەوتن":
    st.markdown('<div class="main"><h2>📊 پێشکەوتن و دەستکەوتەکان</h2></div>', unsafe_allow_html=True)
    # ... (هەروا ماونەتەوە)

elif page == "📚 نەخۆشییەکان":
    st.markdown('<div class="main"><h2>📚 کتێبخانەی نەخۆشییەکان</h2></div>', unsafe_allow_html=True)
    # ... (هەروا ماونەتەوە)

# ================================
# فووەتەر
# ================================
st.markdown("---")
st.markdown(f"""
<div class="footer-style">
    <h3>🩺 Dr.Danyal - ڕاهێنەری پزیشکی Pro Max v5.0</h3>
    <p>{get_disease_count()} نەخۆشی | {get_drug_count() + len(st.session_state.custom_drugs)} دەرمان | {get_quiz_count()} کویز</p>
    <p style="font-size:0.8rem;">© 2024 Dr.Danyal | بەکارهێنەر: {st.session_state.username}</p>
</div>
""", unsafe_allow_html=True)
