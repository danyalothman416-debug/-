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
# 2. CSS و ستایلە پێشکەوتووەکان (دیزاینی نوێ پزیشکی پڕۆفیشناڵ)
# ================================
st.markdown("""
<style>
    /* 2.1 باکگراوندی پشت - ڕوون و پزیشکی */
    .stApp {
        background: #f4f7f6;
        background-image: radial-gradient(#e2e8e0 1px, transparent 1px);
        background-size: 20px 20px;
    }
    
    .main {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 2.5rem;
        margin: 1rem;
        border: 1px solid #dfe6e9;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
        animation: fadeIn 0.8s ease-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* 2.2 سایدبار - ڕوون و ئاسان */
    [data-testid="stSidebar"] {
        background: #ffffff !important;
        border-right: 2px solid #e2e8e0 !important;
        box-shadow: 2px 0 15px rgba(0, 0, 0, 0.03) !important;
    }
    
    [data-testid="stSidebar"] * {
        color: #2d3436 !important;
    }
    
    /* سایدبار - هەموو دەقەکان */
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown span,
    [data-testid="stSidebar"] label {
        color: #636e72 !important;
        font-weight: 500 !important;
    }
    
    /* سایدبار - دابەشکەر */
    [data-testid="stSidebar"] hr {
        border-color: #e2e8e0 !important;
    }
    
    /* سایدبار - ڕادیۆ بەتنی پاک */
    [data-testid="stSidebar"] .stRadio > div {
        background: #f8f9fa !important;
        border-radius: 10px !important;
        padding: 5px !important;
        border: 1px solid #e2e8e0 !important;
        transition: all 0.3s ease !important;
    }
    
    [data-testid="stSidebar"] .stRadio > div:hover {
        background: #eef2f5 !important;
        border-color: #00b894 !important;
    }
    
    [data-testid="stSidebar"] .stRadio [role="radiogroup"] label {
        transition: all 0.2s ease !important;
        padding: 8px 12px !important;
        border-radius: 8px !important;
        color: #2d3436 !important;
    }
    
    [data-testid="stSidebar"] .stRadio [role="radiogroup"] label:hover {
        background: #00b894 !important;
        color: #ffffff !important;
    }
    
    /* 2.3 ویجێتەکان - چوارچێوەی جوان */
    .stSelectbox > div > div,
    .stTextInput > div > div,
    .stTextArea > div > div,
    .stNumberInput > div > div {
        background: #ffffff !important;
        border: 1px solid #dfe6e9 !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
        color: #2d3436 !important;
    }
    
    .stSelectbox > div > div:focus-within,
    .stTextInput > div > div:focus-within,
    .stTextArea > div > div:focus-within,
    .stNumberInput > div > div:focus-within {
        border-color: #00b894 !important;
        box-shadow: 0 0 0 3px rgba(0, 184, 148, 0.1) !important;
        background: #ffffff !important;
    }
    
    /* کۆنتەینەری پەیوەندی بۆردەر */
    [data-testid="stVerticalBlock"] [data-testid="stVerticalBlock"] {
        background: #f8f9fa;
        border-radius: 12px;
        border: 1px solid #e9ecef;
        padding: 20px;
        margin-bottom: 20px;
    }
    
    /* 2.4 دوگمەکان - شێوازی پزیشکی (سەوز و شینی تاریک) */
    .stButton > button {
        background: #00b894 !important;
        border: none !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        padding: 0.6rem 2rem !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 6px rgba(0, 184, 148, 0.2) !important;
        font-size: 0.95rem !important;
    }
    
    .stButton > button:hover {
        background: #00a381 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 7px 14px rgba(0, 184, 148, 0.3) !important;
    }
    
    .stButton > button:active {
        transform: scale(0.98) !important;
    }
    
    /* دوگمەی سەرەتایی */
    .stButton > button[kind="primary"] {
        background: #0984e3 !important;
        box-shadow: 0 4px 6px rgba(9, 132, 227, 0.2) !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: #0773c5 !important;
        box-shadow: 0 7px 14px rgba(9, 132, 227, 0.3) !important;
    }
    
    /* دوگمەی چوونە دەرەوە */
    [data-testid="stSidebar"] .stButton > button {
        background: #ffffff !important;
        border: 1px solid #d63031 !important;
        color: #d63031 !important;
        box-shadow: none !important;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background: #d63031 !important;
        color: #ffffff !important;
    }
    
    /* 2.5 لۆگۆی Dr.Danyal */
    .logo-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
        background: linear-gradient(135deg, #0984e3, #00b894);
        padding: 15px 30px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 8px 20px rgba(9, 132, 227, 0.2);
    }
    .logo-icon {
        font-size: 3.5rem;
    }
    .logo-text {
        font-size: 2.2rem;
        font-weight: bold;
        color: #ffffff;
        letter-spacing: 1px;
    }
    .logo-sub {
        font-size: 0.9rem;
        color: rgba(255,255,255,0.8);
        text-align: center;
        margin-top: -5px;
    }
    
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-8px); }
        100% { transform: translateY(0px); }
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.03); }
        100% { transform: scale(1); }
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-30px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(30px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }
    
    @keyframes iconFloat {
        0% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-10px) rotate(3deg); }
        100% { transform: translateY(0px) rotate(0deg); }
    }
    
    /* ئایکۆنەکان بە ئەنیمەیشن */
    .icon-animated {
        display: inline-block;
        animation: iconFloat 3s ease-in-out infinite;
        font-size: 2rem;
    }
    .icon-spin {
        display: inline-block;
        animation: spin 10s linear infinite;
        font-size: 2rem;
    }
    
    .main-header {
        font-size: 2.8rem;
        background: linear-gradient(135deg, #0984e3, #00b894);
        color: white;
        text-align: center;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(9, 132, 227, 0.15);
        font-family: 'Noto Naskh Arabic', sans-serif;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .case-card {
        background: #ffffff;
        padding: 1.8rem;
        border-radius: 12px;
        border-left: 6px solid #0984e3;
        margin: 1rem 0;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border-top: 1px solid #eee;
        border-right: 1px solid #eee;
        border-bottom: 1px solid #eee;
        animation: slideInLeft 0.5s ease-out;
        color: #2d3436;
        position: relative;
    }
    
    .case-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.08);
        border-left-color: #00b894;
    }
    
    .success-box {
        background: #e6fffa;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 6px solid #00b894;
        box-shadow: 0 4px 15px rgba(0, 184, 148, 0.1);
        color: #005247;
        border: 1px solid #b2f5ea;
    }
    
    .error-box {
        background: #fff5f5;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 6px solid #d63031;
        box-shadow: 0 4px 15px rgba(214, 48, 49, 0.1);
        color: #721c24;
        border: 1px solid #fed7d7;
    }
    
    .quiz-card {
        background: #ffffff;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin: 1.5rem 0;
        border: 1px solid #e9ecef;
        transition: all 0.3s ease;
        color: #2d3436;
        animation: slideInRight 0.5s ease-out;
    }
    
    .quiz-card:hover {
        box-shadow: 0 8px 25px rgba(0,0,0,0.08);
        border-color: #0984e3;
    }
    
    .progress-container {
        background: #e9ecef;
        border-radius: 20px;
        height: 18px;
        overflow: hidden;
        margin: 1rem 0;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #0984e3, #00b894);
        border-radius: 20px;
        transition: width 1s ease;
        position: relative;
    }
    
    .progress-fill::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
        animation: shimmer 2s infinite;
    }
    
    .stat-card {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        text-align: center;
        border-top: 5px solid #0984e3;
        transition: all 0.3s ease;
        color: #2d3436;
        border: 1px solid #eee;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        border-top-color: #00b894;
    }
    
    .stat-number {
        font-size: 2.8rem;
        font-weight: bold;
        color: #0984e3;
    }
    
    .badge-level {
        display: inline-block;
        padding: 0.5rem 1.5rem;
        border-radius: 25px;
        font-weight: bold;
        background: #dfe6e9;
        color: #2d3436;
        font-size: 1rem;
    }
    
    .footer-style {
        text-align: center;
        padding: 2rem;
        background: #ffffff;
        color: #636e72;
        border-radius: 12px;
        margin-top: 3rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: 1px solid #eee;
    }
    
    .drug-card {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #eee;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
        color: #2d3436;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }
    
    .drug-card:hover {
        transform: translateY(-3px);
        border-color: #00b894;
        box-shadow: 0 6px 15px rgba(0,0,0,0.07);
    }
    
    .symptom-tag {
        display: inline-block;
        background: #e3f2fd;
        padding: 0.3rem 1rem;
        border-radius: 15px;
        margin: 0.2rem;
        font-size: 0.85rem;
        color: #0984e3;
        border: 1px solid #bbdefb;
    }
    
    .symptom-tag:hover {
        background: #0984e3;
        color: white;
    }
    
    .risk-high { color: #d63031; font-weight: bold; }
    .risk-medium { color: #fdcb6e; font-weight: bold; }
    .risk-low { color: #00b894; font-weight: bold; }
    
    .achievement-badge {
        display: inline-flex;
        align-items: center;
        background: #fff9c4;
        padding: 0.5rem 1.2rem;
        border-radius: 20px;
        color: #f57f17;
        font-weight: bold;
        margin: 0.3rem;
        border: 1px solid #fff59d;
        box-shadow: 0 2px 5px rgba(245, 127, 23, 0.1);
    }
    
    .tab-container {
        background: #ffffff;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin: 1.5rem 0;
        border: 1px solid #eee;
        color: #2d3436;
    }
    
    .medication-card {
        background: #f8f9fa;
        padding: 1.2rem;
        border-radius: 10px;
        border: 1px solid #e9ecef;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
        color: #2d3436;
    }
    
    .medication-card:hover {
        background: #eef2f5;
        border-color: #0984e3;
    }
    
    .level-badge {
        display: inline-block;
        padding: 0.2rem 0.8rem;
        border-radius: 15px;
        font-weight: bold;
        font-size: 0.8rem;
        margin: 0.2rem;
    }
    
    .level-1 { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
    .level-2 { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
    .level-3 { background: #fff3cd; color: #856404; border: 1px solid #ffeeba; }
    .level-4 { background: #ffe2cc; color: #8a4b08; border: 1px solid #ffd6b3; }
    .level-5 { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    
    .lab-result-card {
        background: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #0984e3;
        box-shadow: 0 2px 5px rgba(0,0,0,0.03);
    }
    
    .lab-result-card:hover {
        background: #f8f9fa;
    }
    
    .lab-normal { border-left-color: #00b894; }
    .lab-high { border-left-color: #d63031; }
    .lab-low { border-left-color: #fdcb6e; }
    
    .notification-toast {
        position: fixed;
        top: 20px;
        right: 20px;
        background: #00b894;
        color: white;
        padding: 1rem 2rem;
        border-radius: 8px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        z-index: 1000;
    }
    
    .timeline-item {
        padding: 1rem 1.5rem;
        border-left: 3px solid #0984e3;
        margin: 0.5rem 0;
        background: #ffffff;
        border-radius: 0 8px 8px 0;
        color: #2d3436;
    }
    
    .timeline-item:hover {
        background: #f8f9fa;
    }
    
    .dr-icon {
        font-size: 3.5rem;
    }
    
    .login-container {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 80vh;
    }
    
    .login-box {
        background: #ffffff;
        padding: 3rem;
        border-radius: 15px;
        border: 1px solid #e2e8e0;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.05);
        text-align: center;
        max-width: 450px;
        width: 100%;
    }
    
    .login-input {
        background: #f8f9fa !important;
        border: 1px solid #dfe6e9 !important;
        border-radius: 8px !important;
        color: #2d3436 !important;
        padding: 12px 20px !important;
        margin: 10px 0 !important;
        width: 100% !important;
    }
    
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
            padding: 1.5rem;
        }
        .stat-number {
            font-size: 2rem;
        }
        .stat-card {
            padding: 1rem;
        }
        .logo-text {
            font-size: 1.8rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# ================================
# 3. سیستەمی ئاستەکان (Levels) - پڕتر
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
    "پەستانی خوێنی دووەمی": {
        "نیشانەکان": ["سەرئێشە", "سەرگێژخواردن", "فشاری پشت چاو", "خێرالێدانی دڵ", "ئاوسانی قاچ", "میلە"],
        "پشکنینەکان": {"BP": ">140/90 mmHg", "Creatinine": "بەرز", "Ultrasound": "نەخۆشی گورچیلە", "Aldosterone": "بەرز"},
        "چارەسەر": ["چارەسەری هۆکار", "دژە پەستانی خوێن", "کەمکردنەوەی نمەک", "پشکنینی بەردەوام"],
        "ئاستی مەترسی": "مەترسیدار",
        "تایبەتمەندی": "BP بەرز + هۆکاری دیکە وەک نەخۆشی گورچیلە",
        "ڕێپیشگیری": ["دۆزینەوەی هۆکار", "چارەسەری هۆکار"],
        "گروپی تەمەن": "هەموو تەمەنەکان",
        "ڕێژەی تووشبوون": "5%",
        "جۆری نەخۆشی": "دڵ و خوێن"
    },
    "نەخۆشی دڵی ئیسکیمیک": {
        "نیشانەکان": ["ئازاری سنگ", "کورتی هەناسە", "ئارەقەکردن", "سکچوون و ڕشانەوە", "ئازاری شان", "تنگەنەفەسی", "ئازاری پشت", "خێرالێدانی دڵ"],
        "پشکنینەکان": {"ECG": "ST depression", "Troponin": "بەرز >0.04", "CK-MB": "بەرز >5", "Echocardiogram": "کەمبوونی ئیشی دڵ", "CAG": "تەنگی کرۆنەری"},
        "چارەسەر": ["ئەسپیرین 300mg", "نایترۆگلیسیرین", "ئۆکسجین", "بێتا بلاکەر", "هێپارین"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندی": "ST changes + Troponin elevated",
        "ڕێپیشگیری": ["کۆنتڕۆڵی پەستانی خوێن", "وەرزش", "وەستانی جگەرە", "کۆنتڕۆڵی شەکرە"],
        "گروپی تەمەن": "تەمەن > 50 ساڵ",
        "ڕێژەی تووشبوون": "7%",
        "جۆری نەخۆشی": "دڵ و خوێن"
    },
    "نەخۆشی دڵی شکان (Heart Failure)": {
        "نیشانەکان": ["کورتی هەناسە", "ئاوسانی قاچ", "ماندوویی", "خێرالێدانی دڵ", "کۆخە", "ئارەقەکردنی شەو"],
        "پشکنینەکان": {"BNP": "بەرز", "Echocardiogram": "EF < 40%", "Chest X-ray": "Cardiomegaly", "ECG": "Abnormal"},
        "چارەسەر": ["Diuretics", "ACE inhibitor", "Beta blocker", "کەمکردنەوەی نمەک", "ئۆکسجین"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندی": "BNP بەرز + EF نزم",
        "ڕێپیشگیری": ["کۆنتڕۆڵی BP", "وەرزش", "شێوازی خواردن"],
        "گروپی تەمەن": "تەمەن > 60 ساڵ",
        "ڕێژەی تووشبوون": "2%",
        "جۆری نەخۆشی": "دڵ و خوێن"
    },
    "نەخۆشی دڵی ڕیتم (Arrhythmia)": {
        "نیشانەکان": ["لێدانی دڵ ناڕێک", "سەرگێژخواردن", "کورتی هەناسە", "ئازاری سنگ", "خێرالێدانی دڵ"],
        "پشکنینەکان": {"ECG": "Arrhythmia", "Holter": "Abnormal", "Echocardiogram": "نۆرماڵ"},
        "چارەسەر": ["Beta blocker", "Calcium channel blocker", "Anticoagulant", "Pacemaker"],
        "ئاستی مەترسی": "مەترسیدار",
        "تایبەتمەندی": "ECG ناڕێک",
        "ڕێپیشگیری": ["پارێزی لە کافئین", "وەرزش", "پشکنینی بەردەوام"],
        "گروپی تەمەن": "هەموو تەمەنەکان",
        "ڕێژەی تووشبوون": "1.5%",
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
    },
    "هەوکردنی سییە ڤایرۆسی": {
        "نیشانەکان": ["تا", "کۆخە وشک", "هەناسەدان بە زەحمەت", "ماندوویی", "ئازاری ماسوولکە", "سەرئێشە"],
        "پشکنینەکان": {"Chest X-ray": "Interstitial", "CRP": "نۆرماڵ", "WBC": "نزم", "PCR": "positive"},
        "چارەسەر": ["شلەمەنی", "ئۆکسجین", "دەرمانی دژە تا", "پشوو"],
        "ئاستی مەترسی": "مامناوەند",
        "تایبەتمەندی": "کۆخە وشک + CRP نۆرماڵ",
        "ڕێپیشگیری": ["دەستشۆردن", "ماسک", "دوورکەوتنەوە"],
        "گروپی تەمەن": "هەموو تەمەنەکان",
        "ڕێژەی تووشبوون": "2%",
        "جۆری نەخۆشی": "هەوکردن"
    },
    "ئەنیمیا": {
        "نیشانەکان": ["ماندوویی", "ڕەنگی پێست زەرد", "سەرگێژخواردن", "لێدانی دڵ خێرا", "سەرئێشە", "پڕۆشتن", "هەستی ساردی", "تەنگی هەناسە"],
        "پشکنینەکان": {"Hb": "<12 g/dL", "MCV": "<80 fL", "Ferritin": "نزم <15", "TIBC": "بەرز >450", "Iron": "نزم"},
        "چارەسەر": ["فێروس سولفەیت 325mg", "گۆڕینی خواردن", "دۆزینەوەی هۆکاری سەرەکی", "ڤیتامین C 500mg"],
        "ئاستی مەترسی": "مامناوەند",
        "تایبەتمەندی": "Hb نزم + MCV نزم + Ferritin نزم",
        "ڕێپیشگیری": ["خواردنی ئاسن", "خواردنی ڤیتامین C", "پشکنینی خوێنی بەردەوام"],
        "گروپی تەمەن": "هەموو تەمەنەکان",
        "ڕێژەی تووشبوون": "25%",
        "جۆری نەخۆشی": "خوێن"
    },
    "ئەنیمیای ماکرۆسایتیک": {
        "نیشانەکان": ["ماندوویی", "سەرگێژخواردن", "هەستی بێهێزی", "کورتی هەناسە", "خێرالێدانی دڵ"],
        "پشکنینەکان": {"Hb": "<12 g/dL", "MCV": ">100 fL", "B12": "نزم", "Folate": "نزم"},
        "چارەسەر": ["ڤیتامین B12 1000mcg", "فۆلیک ئەسید 1mg", "گۆڕینی خواردن"],
        "ئاستی مەترسی": "مامناوەند",
        "تایبەتمەندی": "MCV بەرز + B12 نزم",
        "ڕێپیشگیری": ["خواردنی ڤیتامین B12", "خواردنی فۆلیک ئەسید"],
        "گروپی تەمەن": "پیران",
        "ڕێژەی تووشبوون": "5%",
        "جۆری نەخۆشی": "خوێن"
    },
    "ئەنیمیای هیمۆلایتیک": {
        "نیشانەکان": ["ماندوویی", "زەردبوون", "میز تۆخ", "تا", "ئازاری سک", "خێرالێدانی دڵ"],
        "پشکنینەکان": {"Hb": "نزم", "Reticulocyte": "بەرز", "LDH": "بەرز", "Haptoglobin": "نزم", "Coomb's test": "positive"},
        "چارەسەر": ["دەرمانی ستیرۆید", "خوێن گواستنەوە", "دۆزینەوەی هۆکار"],
        "ئاستی مەترسی": "مەترسیدار",
        "تایبەتمەندی": "Hb نزم + Reticulocyte بەرز",
        "ڕێپیشگیری": ["دۆزینەوەی هۆکار", "پارێزی لە دەرمانەکان"],
        "گروپی تەمەن": "هەموو تەمەنەکان",
        "ڕێژەی تووشبوون": "1%",
        "جۆری نەخۆشی": "خوێن"
    },
    "ئەنیمیای شاخە (Sickle Cell)": {
        "نیشانەکان": ["ئازاری ماسوولکە", "ماندوویی", "زەردبوون", "تەنگی هەناسە", "خێرالێدانی دڵ"],
        "پشکنینەکان": {"Hb": "نزم", "HbS": "positive", "Peripheral smear": "Sickle cells"},
        "چارەسەر": ["هیدروکسی یوریا", "خوێن گواستنەوە", "ئۆکسجین", "دەرمانی ئازار"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندی": "HbS positive + شێوەی شاخە",
        "ڕێپیشگیری": ["پشکنینی بۆماوەیی", "پارێزی لە وشکبوونەوە"],
        "گروپی تەمەن": "منداڵان و گەنجان",
        "ڕێژەی تووشبوون": "0.5%",
        "جۆری نەخۆشی": "خوێن"
    },
    "لەوسیمیا (Leukemia)": {
        "نیشانەکان": ["ماندوویی", "خوێنبەربوون", "تا", "کێش کەمبوونەوە", "ئازاری ئێسک", "خوێن لە لووتدا"],
        "پشکنینەکان": {"WBC": "بەرز >20", "Hb": "نزم", "Platelets": "نزم", "Bone marrow": "Blast cells"},
        "چارەسەر": ["کیمۆتێراپی", "خوێن گواستنەوە", "ستیرۆید", "پشتیوانی"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندی": "WBC بەرز + Blast cells",
        "ڕێپیشگیری": ["پشکنینی بەردەوام"],
        "گروپی تەمەن": "هەموو تەمەنەکان",
        "ڕێژەی تووشبوون": "0.3%",
        "جۆری نەخۆشی": "خوێن"
    },
    "نەخۆشی گورچیلە": {
        "نیشانەکان": ["ئاوسانی ڕوو و قاچ", "میزی کەم", "ماندوویی", "سەرئێشە", "خوێن لە میزدا", "فشاری خوێن بەرز", "هەستی ساردی"],
        "پشکنینەکان": {"Creatinine": "بەرز >1.3", "BUN": "بەرز >20", "eGFR": "<60", "Urinalysis": "پڕۆتین + خوێن", "Potassium": "بەرز"},
        "چارەسەر": ["ACE inhibitor", "کەمکردنەوەی پڕۆتین", "کۆنتڕۆڵی BP", "دایەلیز (ئەگەر پێویست)"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندی": "Creatinine بەرز + eGFR نزم",
        "ڕێپیشگیری": ["کۆنتڕۆڵی شەکرە", "کۆنتڕۆڵی BP", "کەمکردنەوەی نمەک"],
        "گروپی تەمەن": "تەمەن > 50 ساڵ",
        "ڕێژەی تووشبوون": "10%",
        "جۆری نەخۆشی": "گورچیلە"
    },
    "نەخۆشی گورچیلەی شەکری": {
        "نیشانەکان": ["پڕۆتین لە میزدا", "ئاوسان", "فشاری خوێن بەرز", "میزی کەم"],
        "پشکنینەکان": {"Urine protein": ">300mg", "Creatinine": "بەرز", "eGFR": "کەم"},
        "چارەسەر": ["ACE inhibitor", "کۆنتڕۆڵی شەکرە", "کەمکردنەوەی پڕۆتین"],
        "ئاستی مەترسی": "مەترسیدار",
        "تایبەتمەندی": "شەکرە + پڕۆتین لە میزدا",
        "ڕێپیشگیری": ["کۆنتڕۆڵی شەکرە", "کۆنتڕۆڵی BP"],
        "گروپی تەمەن": "نەخۆشانی شەکرە",
        "ڕێژەی تووشبوون": "20% (لە نەخۆشانی شەکرە)",
        "جۆری نەخۆشی": "گورچیلە"
    },
    "نەخۆشی گورچیلە بەرد": {
        "نیشانەکان": ["ئازاری پشت", "خوێن لە میزدا", "سکچوون", "تا", "ئازاری میزکردن"],
        "پشکنینەکان": {"Ultrasound": "بەرد", "Urinalysis": "خوێن + بەلۆر", "CT": "بەرد"},
        "چارەسەر": ["شلەمەنی", "دەرمانی ئازار", "Lithotripsy", "نەشتەرگەری"],
        "ئاستی مەترسی": "مامناوەند",
        "تایبەتمەندی": "ئازاری پشت + خوێن لە میزدا",
        "ڕێپیشگیری": ["ئاوی زۆر", "کەمکردنەوەی نمەک"],
        "گروپی تەمەن": "هەموو تەمەنەکان",
        "ڕێژەی تووشبوون": "8%",
        "جۆری نەخۆشی": "گورچیلە"
    },
    "نەخۆشی جگەر (Hepatitis A)": {
        "نیشانەکان": ["ماندوویی", "زەردبوونی چاو", "سکچوون", "تا", "ئازاری سک", "میز تۆخ"],
        "پشکنینەکان": {"ALT": "بەرز >40", "AST": "بەرز >40", "Bilirubin": "بەرز >1.2", "Anti-HAV": "positive"},
        "چارەسەر": ["پشوو", "شلەمەنی", "شێوازی خواردن", "پارێزی لە جگەر"],
        "ئاستی مەترسی": "مامناوەند",
        "تایبەتمەندی": "Anti-HAV positive",
        "ڕێپیشگیری": ["کوتان", "دەستشۆردن", "خواردنی پاک"],
        "گروپی تەمەن": "هەموو تەمەنەکان",
        "ڕێژەی تووشبوون": "1.5%",
        "جۆری نەخۆشی": "جگەر"
    },
    "نەخۆشی جگەر (Hepatitis B)": {
        "نیشانەکان": ["ماندوویی", "زەردبوون", "میز تۆخ", "ئازاری سک", "سکچوون"],
        "پشکنینەکان": {"ALT": "بەرز", "HBsAg": "positive", "Anti-HBc": "positive"},
        "چارەسەر": ["Entecavir", "Tenofovir", "پشکنینی بەردەوام", "پارێزی لە جگەر"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندی": "HBsAg positive",
        "ڕێپیشگیری": ["کوتان", "پارێزی لە پەیوەندی خوێن"],
        "گروپی تەمەن": "هەموو تەمەنەکان",
        "ڕێژەی تووشبوون": "3%",
        "جۆری نەخۆشی": "جگەر"
    },
    "نەخۆشی جگەر (Hepatitis C)": {
        "نیشانەکان": ["ماندوویی", "کێش کەمبوونەوە", "ئازاری سک", "زەردبوون", "میلە"],
        "پشکنینەکان": {"Anti-HCV": "positive", "PCR": "positive", "ALT": "بەرز"},
        "چارەسەر": ["Sofosbuvir", "Daclatasvir", "پشکنینی بەردەوام"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندی": "Anti-HCV positive",
        "ڕێپیشگیری": ["پارێزی لە پەیوەندی خوێن"],
        "گروپی تەمەن": "هەموو تەمەنەکان",
        "ڕێژەی تووشبوون": "2%",
        "جۆری نەخۆشی": "جگەر"
    },
    "نەخۆشی جگەر (Cirrhosis)": {
        "نیشانەکان": ["ئاوسانی سک", "زەردبوون", "ماندوویی", "خوێنبەربوون", "کێش کەمبوونەوە"],
        "پشکنینەکان": {"ALT": "بەرز", "AST": "بەرز", "Albumin": "نزم", "Ultrasound": "Cirrhosis"},
        "چارەسەر": ["پارێزی لە کحول", "Diuretic", "شێوازی خواردن", "پشکنینی بەردەوام"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندی": "Ultrasound cirrhosis",
        "ڕێپیشگیری": ["پارێزی لە کحول", "پارێزی لە Hepatitis"],
        "گروپی تەمەن": "تەمەن > 50 ساڵ",
        "ڕێژەی تووشبوون": "0.5%",
        "جۆری نەخۆشی": "جگەر"
    },
    "نەخۆشی جگەر (Fatty Liver)": {
        "نیشانەکان": ["ماندوویی", "ئازاری سکی سەرەوە", "کێش زیادکردن", "میلە"],
        "پشکنینەکان": {"Ultrasound": "Fatty liver", "ALT": "نزم بەرز", "Cholesterol": "بەرز"},
        "چارەسەر": ["کەمکردنەوەی کێش", "وەرزش", "شێوازی خواردن", "پارێزی لە جگەر"],
        "ئاستی مەترسی": "کەم",
        "تایبەتمەندی": "Ultrasound fatty liver",
        "ڕێپیشگیری": ["شێوازی خواردن", "وەرزش"],
        "گروپی تەمەن": "تەمەن مامناوەند",
        "ڕێژەی تووشبوون": "25%",
        "جۆری نەخۆشی": "جگەر"
    },
    "نەخۆشی جگەر (Liver Cancer)": {
        "نیشانەکان": ["کێش کەمبوونەوە", "ئازاری سک", "زەردبوون", "ئاوسانی سک", "میلە"],
        "پشکنینەکان": {"AFP": "بەرز >400", "CT": "تومۆر", "Biopsy": "Malignant"},
        "چارەسەر": ["نەشتەرگەری", "کیمۆتێراپی", "ڕادیۆتێراپی", "پشتیوانی"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندی": "AFP بەرز + تومۆر",
        "ڕێپیشگیری": ["پارێزی لە Hepatitis", "پشکنینی بەردەوام"],
        "گروپی تەمەن": "تەمەن > 60 ساڵ",
        "ڕێژەی تووشبوون": "0.3%",
        "جۆری نەخۆشی": "جگەر"
    },
    "نەخۆشی کۆکە (Asthma)": {
        "نیشانەکان": ["هەناسەدان بە زەحمەت", "کۆخە", "تنگەنەفەسی", "فیشک (Wheezing)", "فشاری سنگ", "تەنگی هەناسە"],
        "پشکنینەکان": {"Pulmonary function": "FEV1 < 80%", "Peak flow": "کەم", "Chest X-ray": "نۆرماڵ", "IgE": "بەرز"},
        "چارەسەر": ["Bronchodilator", "Steroid inhaler", "پارێزی لە هۆکارەکان", "Leukotriene inhibitor"],
        "ئاستی مەترسی": "مامناوەند",
        "تایبەتمەندی": "FEV1 کەم + فیشک",
        "ڕێپیشگیری": ["پارێزی لە هۆکارەکان", "بەکارهێنانی inhaler", "وەرزش"],
        "گروپی تەمەن": "منداڵان و گەنجان",
        "ڕێژەی تووشبوون": "5%",
        "جۆری نەخۆشی": "هەناسە"
    },
    "نەخۆشی کۆکە (COPD)": {
        "نیشانەکان": ["کۆخەی درێژخایەن", "تنگەنەفەسی", "هەناسەدان بە زەحمەت", "کەمبوونی کێش", "ماندوویی"],
        "پشکنینەکان": {"Pulmonary function": "FEV1/FVC < 70%", "Chest X-ray": "Hyperinflation", "Blood gas": "نزم"},
        "چارەسەر": ["Bronchodilator", "Steroid", "ئۆکسجین", "وەستانی جگەرە"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندی": "FEV1/FVC < 70%",
        "ڕێپیشگیری": ["وەستانی جگەرە", "پارێزی لە پیسی"],
        "گروپی تەمەن": "تەمەن > 50 ساڵ",
        "ڕێژەی تووشبوون": "6%",
        "جۆری نەخۆشی": "هەناسە"
    },
    "نەخۆشی سیل (TB)": {
        "نیشانەکان": ["کۆخە (بە خوێن)", "تا", "ئارەقەکردنی شەو", "کێش کەمبوونەوە", "ماندوویی", "تەنگی هەناسە"],
        "پشکنینەکان": {"Chest X-ray": "تەوەرەکان", "Sputum AFB": "positive", "PPD": "positive", "GeneXpert": "positive"},
        "چارەسەر": ["Rifampicin", "Isoniazid", "Pyrazinamide", "Ethambutol"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندی": "کۆخەی خوێناوی + X-ray تایبەت",
        "ڕێپیشگیری": ["BCG vaccine", "پارێزی لە کەسانی تووشبوو", "پشکنین"],
        "گروپی تەمەن": "هەموو تەمەنەکان",
        "ڕێژەی تووشبوون": "0.5%",
        "جۆری نەخۆشی": "هەناسە"
    },
    "نەخۆشی تایفیید (Typhoid)": {
        "نیشانەکان": ["تای بەرز", "سەرئێشە", "سکچوون", "رشانەوە", "ئازاری سک", "میلە"],
        "پشکنینەکان": {"WBC": "نزم", "Blood culture": "Salmonella", "Widal": "positive", "CRP": "بەرز"},
        "چارەسەر": ["Azithromycin", "Ceftriaxone", "شلەمەنی", "پشوو"],
        "ئاستی مەترسی": "مەترسیدار",
        "تایبەتمەندی": "تای بەرز + سکچوون",
        "ڕێپیشگیری": ["خواردنی پاک", "دەستشۆردن", "کوتان"],
        "گروپی تەمەن": "هەموو تەمەنەکان",
        "ڕێژەی تووشبوون": "0.8%",
        "جۆری نەخۆشی": "هەوکردن"
    },
    "نەخۆشی کۆلێرا (Cholera)": {
        "نیشانەکان": ["سکچوونی زۆر (وەک ئاو)", "رشانەوە", "تینوویەتی زۆر", "کەمبوونەوەی میز"],
        "پشکنینەکان": {"Stool culture": "Vibrio cholera", "Rapid test": "positive", "Electrolytes": "نزم"},
        "چارەسەر": ["ORS", "شلەمەنی", "Doxycycline", "Azithromycin"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندی": "سکچوونی زۆر وەک ئاو",
        "ڕێپیشگیری": ["خواردنی پاک", "ئاوی پاک", "دەستشۆردن", "کوتان"],
        "گروپی تەمەن": "هەموو تەمەنەکان",
        "ڕێژەی تووشبوون": "0.1%",
        "جۆری نەخۆشی": "هەوکردن"
    },
    "نەخۆشی پەنکریاتیت": {
        "نیشانەکان": ["ئازاری سکی سەرەوە", "رشانەوە", "تا", "سکچوون", "ئازاری پشت", "تەنگی هەناسە"],
        "پشکنینەکان": {"Amylase": "بەرز >200", "Lipase": "بەرز >200", "CT scan": "پەنکریاتیت", "CRP": "بەرز"},
        "چارەسەر": ["پشووی خواردن", "شلەمەنی", "دەرمانی ئازار", "ئەنتیبایۆتیک"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندی": "Amylase + Lipase بەرز",
        "ڕێپیشگیری": ["پارێزی لە خواردنی چەور", "کەمکردنەوەی کحول"],
        "گروپی تەمەن": "تەمەن > 40 ساڵ",
        "ڕێژەی تووشبوون": "0.3%",
        "جۆری نەخۆشی": "پەنکریاس"
    },
    "نەخۆشی گەدە (Gastritis)": {
        "نیشانەکان": ["ئازاری گەدە", "سکچوون", "سووتانی گەدە", "ڕشانەوە", "هەستی پڕی"],
        "پشکنینەکان": {"Endoscopy": "هەوکردن", "H. pylori": "positive", "Urea breath test": "positive"},
        "چارەسەر": ["PPI (Omeprazole)", "Antibiotic (Amoxicillin)", "Antacid", "گۆڕینی خواردن"],
        "ئاستی مەترسی": "کەم",
        "تایبەتمەندی": "ئازاری گەدە + H. pylori positive",
        "ڕێپیشگیری": ["خواردنی کەم بەهارات", "پارێزی لە NSAIDs"],
        "گروپی تەمەن": "هەموو تەمەنەکان",
        "ڕێژەی تووشبوون": "20%",
        "جۆری نەخۆشی": "گەدە"
    },
    "نەخۆشی گەدە (Gastric Ulcer)": {
        "نیشانەکان": ["ئازاری گەدە", "سکچوون", "خوێن لە رشانەوە", "کێش کەمبوونەوە", "ئازاری شەو"],
        "پشکنینەکان": {"Endoscopy": "Ulcer", "H. pylori": "positive", "Barium swallow": "Ulcer"},
        "چارەسەر": ["PPI", "Antibiotic", "Sucralfate", "گۆڕینی خواردن"],
        "ئاستی مەترسی": "مەترسیدار",
        "تایبەتمەندی": "Ulcer لە Endoscopy",
        "ڕێپیشگیری": ["پارێزی لە NSAIDs", "پارێزی لە کحول"],
        "گروپی تەمەن": "تەمەن > 50 ساڵ",
        "ڕێژەی تووشبوون": "5%",
        "جۆری نەخۆشی": "گەدە"
    },
    "نەخۆشی Parkinson": {
        "نیشانەکان": ["لەرزین", "خاوکردنەوەی جوڵە", "سختی ماسوولکە", "کەمبوونی پێست", "مشکێتی ڕۆیشتن"],
        "پشکنینەکان": {"Clinical exam": "Parkinsonian", "DAT scan": "کەم", "MRI": "نۆرماڵ"},
        "چارەسەر": ["Levodopa", "Carbidopa", "Pramipexole", "Ropinirole"],
        "ئاستی مەترسی": "مەترسیدار",
        "تایبەتمەندی": "لەرزین + سختی ماسوولکە",
        "ڕێپیشگیری": ["وەرزش", "پارێزی لە پیسی"],
        "گروپی تەمەن": "تەمەن > 60 ساڵ",
        "ڕێژەی تووشبوون": "1%",
        "جۆری نەخۆشی": "دەمار"
    },
    "نەخۆشی Alzheimer": {
        "نیشانەکان": ["بیرچون", "کەمبوونی بیر", "گۆڕانی کەسایەتی", "مشکێتی ڕۆژانە", "بێئاگایی"],
        "پشکنینەکان": {"MRI": "Atrophy", "PET": "Abnormal", "Cognitive test": "کەم"},
        "چارەسەر": ["Donepezil", "Rivastigmine", "Memantine", "پشتیوانی"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندی": "بیرچون + MRI atrophy",
        "ڕێپیشگیری": ["مەشقی مێشک", "وەرزش", "شێوازی خواردن"],
        "گروپی تەمەن": "تەمەن > 65 ساڵ",
        "ڕێژەی تووشبوون": "5% (تەمەن > 65)",
        "جۆری نەخۆشی": "دەمار"
    },
    "نەخۆشی MS (Multiple Sclerosis)": {
        "نیشانەکان": ["کورتی بینین", "ماندوویی", "بێئاگایی", "مشکێتی جوڵە", "سەرگێژخواردن"],
        "پشکنینەکان": {"MRI": "Plagues", "CSF": "Oligoclonal bands", "VEP": "کەم"},
        "چارەسەر": ["Steroid", "Interferon", "Glatiramer", "Rituximab"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندی": "MRI plagues + Oligoclonal bands",
        "ڕێپیشگیری": ["پارێزی لە ڤایرۆس"],
        "گروپی تەمەن": "ژنانی گەنج",
        "ڕێژەی تووشبوون": "0.3%",
        "جۆری نەخۆشی": "دەمار"
    },
    "نەخۆشی Stroke": {
        "نیشانەکان": ["مشکێتی جوڵە", "مشکێتی قسەکردن", "بێئاگایی", "سەرگێژخواردن", "خوێنبەربوون"],
        "پشکنینەکان": {"CT": "Ischemia/Hemorrhage", "MRI": "Stroke", "Angiography": "تەنگی کرۆنەری"},
        "چارەسەر": ["Thrombolytic", "Antiplatelet", "Rehabilitation", "پشتیوانی"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندی": "مشکێتی جوڵە + CT stroke",
        "ڕێپیشگیری": ["کۆنتڕۆڵی BP", "کۆنتڕۆڵی شەکرە", "وەستانی جگەرە"],
        "گروپی تەمەن": "تەمەن > 60 ساڵ",
        "ڕێژەی تووشبوون": "2%",
        "جۆری نەخۆشی": "دەمار"
    },
    "نەخۆشی Migraine": {
        "نیشانەکان": ["سەرئێشەی توند", "سەرگێژخواردن", "هەستی بەمەزە", "بینینی تەڵخ", "ڕشانەوە"],
        "پشکنینەکان": {"MRI": "نۆرماڵ", "Clinical exam": "Migraine", "Response to triptan": "positive"},
        "چارەسەر": ["Triptan", "NSAIDs", "Propranolol", "Amitriptyline"],
        "ئاستی مەترسی": "کەم",
        "تایبەتمەندی": "سەرئێشەی توند + هەستی بەمەزە",
        "ڕێپیشگیری": ["پارێزی لە هۆکارەکان", "وەرزش", "پشوو"],
        "گروپی تەمەن": "ژنان",
        "ڕێژەی تووشبوون": "12%",
        "جۆری نەخۆشی": "دەمار"
    }
}

# ================================
# 5. داتابەسی پشکنینەکانی تاقیگە (٢٠٠ پشکنین) - بە ناوی ئامێر و تێبینی
# ================================
LAB_TESTS = {}

# 5.1 پشکنینەکانی خوێن (٥٠ پشکنین)
blood_tests = {
    "CBC": {"گروپ": "خوێن", "نۆرماڵ": (4.0, 11.0), "یەکە": "x10³/µL", "تەفسیر": "خڕۆکە سپیەکان", "ئامێر": "ئۆتۆماتیک سێل کاونتر (Sysmex XN-9000)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "Hemoglobin": {"گروپ": "خوێن", "نۆرماڵ": (12.0, 16.0), "یەکە": "g/dL", "تەفسیر": "هیمۆگلۆبین", "ئامێر": "هیمۆگلۆبینۆمیتەر (HemoCue 201+", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "Platelets": {"گروپ": "خوێن", "نۆرماڵ": (150, 450), "یەکە": "x10³/µL", "تەفسیر": "پلەیتلێت", "ئامێر": "ئۆتۆماتیک سێل کاونتر (Sysmex XN-9000)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "MCV": {"گروپ": "خوێن", "نۆرماڵ": (80, 100), "یەکە": "fL", "تەفسیر": "قەبارەی خڕۆکە سوورەکان", "ئامێر": "ئۆتۆماتیک سێل کاونتر (Sysmex XN-9000)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "MCH": {"گروپ": "خوێن", "نۆرماڵ": (27, 33), "یەکە": "pg", "تەفسیر": "کەمی هیمۆگلۆبین", "ئامێر": "ئۆتۆماتیک سێل کاونتر (Sysmex XN-9000)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "MCHC": {"گروپ": "خوێن", "نۆرماڵ": (32, 36), "یەکە": "g/dL", "تەفسیر": "چڕی هیمۆگلۆبین", "ئامێر": "ئۆتۆماتیک سێل کاونتر (Sysmex XN-9000)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "RDW": {"گروپ": "خوێن", "نۆرماڵ": (11.5, 14.5), "یەکە": "%", "تەفسیر": "جیاوازی قەبارە", "ئامێر": "ئۆتۆماتیک سێل کاونتر (Sysmex XN-9000)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "Reticulocyte": {"گروپ": "خوێن", "نۆرماڵ": (0.5, 2.5), "یەکە": "%", "تەفسیر": "خڕۆکە نوێکان", "ئامێر": "فلۆ سایتمیتەر (BD FACSCalibur)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "Ferritin": {"گروپ": "خوێن", "نۆرماڵ": (15, 300), "یەکە": "ng/mL", "تەفسیر": "ئاسن", "ئامێر": "کیمیایی ئیمینۆ (Roche Cobas e411)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "TIBC": {"گروپ": "خوێن", "نۆرماڵ": (250, 450), "یەکە": "mcg/dL", "تەفسیر": "ئاسن", "ئامێر": "کیمیایی ئیمینۆ (Roche Cobas c502)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "Iron": {"گروپ": "خوێن", "نۆرماڵ": (60, 170), "یەکە": "mcg/dL", "تەفسیر": "ئاسن", "ئامێر": "کیمیایی ئیمینۆ (Roche Cobas c502)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "Vitamin B12": {"گروپ": "خوێن", "نۆرماڵ": (200, 900), "یەکە": "pg/mL", "تەفسیر": "ڤیتامین B12", "ئامێر": "کیمیایی ئیمینۆ (Roche Cobas e411)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "Folate": {"گروپ": "خوێن", "نۆرماڵ": (3, 17), "یەکە": "ng/mL", "تەفسیر": "فۆلیک ئەسید", "ئامێر": "کیمیایی ئیمینۆ (Roche Cobas e411)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "LDH": {"گروپ": "خوێن", "نۆرماڵ": (100, 250), "یەکە": "U/L", "تەفسیر": "ئەنزیم", "ئامێر": "سپێکترۆفۆتۆمیتەر (Beckman Coulter AU480)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "Haptoglobin": {"گروپ": "خوێن", "نۆرماڵ": (50, 250), "یەکە": "mg/dL", "تەفسیر": "پروتێین", "ئامێر": "نێفێلۆمیتەر (Siemens BNII)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "ESR": {"گروپ": "خوێن", "نۆرماڵ": (0, 20), "یەکە": "mm/hr", "تەفسیر": "خێرایی تەنیشتن", "ئامێر": "ESR ئۆتۆماتیک (Ves-Matic 20)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "CRP": {"گروپ": "خوێن", "نۆرماڵ": (0, 5), "یەکە": "mg/L", "تەفسیر": "پروتێینی هەوکردن", "ئامێر": "توربیدیمیتەر (Roche Cobas c502)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "Procalcitonin": {"گروپ": "خوێن", "نۆرماڵ": (0, 0.5), "یەکە": "ng/mL", "تەفسیر": "هەوکردنی بەکتریایی", "ئامێر": "کیمیایی ئیمینۆ (Roche Cobas e411)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "Interleukin-6": {"گروپ": "خوێن", "نۆرماڵ": (0, 5), "یەکە": "pg/mL", "تەفسیر": "سایتۆکاینی هەوکردن", "ئامێر": "ELISA Reader (BioTek 800TS)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "TNF-alpha": {"گروپ": "خوێن", "نۆرماڵ": (0, 8), "یەکە": "pg/mL", "تەفسیر": "سایتۆکاینی هەوکردن", "ئامێر": "ELISA Reader (BioTek 800TS)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
}

# 5.2 پشکنینەکانی بایۆکیمیایی (٥٠ پشکنین)
biochem_tests = {
    "Glucose": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (70, 126), "یەکە": "mg/dL", "تەفسیر": "شەکری خوێن", "ئامێر": "گلوکۆمیتەر (Roche Cobas c502)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "HbA1c": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (4.0, 5.6), "یەکە": "%", "تەفسیر": "شەکری درێژخایەن", "ئامێر": "HPLC (Bio-Rad D-100)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "Creatinine": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (0.6, 1.3), "یەکە": "mg/dL", "تەفسیر": "کارایی گورچیلە", "ئامێر": "سپێکترۆفۆتۆمیتەر (Roche Cobas c502)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "BUN": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (7, 20), "یەکە": "mg/dL", "تەفسیر": "نایترۆجینی یوریا", "ئامێر": "سپێکترۆفۆتۆمیتەر (Roche Cobas c502)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "ALT": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (10, 40), "یەکە": "U/L", "تەفسیر": "ئەنزیمی جگەر", "ئامێر": "سپێکترۆفۆتۆمیتەر (Roche Cobas c502)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "AST": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (10, 40), "یەکە": "U/L", "تەفسیر": "ئەنزیمی جگەر", "ئامێر": "سپێکترۆفۆتۆمیتەر (Roche Cobas c502)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "Bilirubin": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (0.1, 1.2), "یەکە": "mg/dL", "تەفسیر": "زەرداوی", "ئامێر": "سپێکترۆفۆتۆمیتەر (Roche Cobas c502)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "Albumin": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (3.5, 5.0), "یەکە": "g/dL", "تەفسیر": "ئەلبومین", "ئامێر": "سپێکترۆفۆتۆمیتەر (Roche Cobas c502)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "Potassium": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (3.5, 5.0), "یەکە": "mmol/L", "تەفسیر": "پۆتاسیۆم", "ئامێر": "ئایۆن سەلێکت یوڤ ئەنالایزەر (Roche Cobas c502)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "Sodium": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (135, 145), "یەکە": "mmol/L", "تەفسیر": "سۆدیۆم", "ئامێر": "ئایۆن سەلێکت یوڤ ئەنالایزەر (Roche Cobas c502)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "Calcium": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (8.5, 10.5), "یەکە": "mg/dL", "تەفسیر": "کالسیۆم", "ئامێر": "سپێکترۆفۆتۆمیتەر (Roche Cobas c502)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "Phosphorus": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (2.5, 4.5), "یەکە": "mg/dL", "تەفسیر": "فۆسفۆر", "ئامێر": "سپێکترۆفۆتۆمیتەر (Roche Cobas c502)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "Magnesium": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (1.7, 2.5), "یەکە": "mg/dL", "تەفسیر": "مەگنیسیۆم", "ئامێر": "سپێکترۆفۆتۆمیتەر (Roche Cobas c502)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "Amylase": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (20, 200), "یەکە": "U/L", "تەفسیر": "ئەنزیمی پەنکریاس", "ئامێر": "سپێکترۆفۆتۆمیتەر (Roche Cobas c502)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "Lipase": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (20, 200), "یەکە": "U/L", "تەفسیر": "ئەنزیمی پەنکریاس", "ئامێر": "سپێکترۆفۆتۆمیتەر (Roche Cobas c502)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "Cholesterol": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (0, 200), "یەکە": "mg/dL", "تەفسیر": "کۆلسترۆل", "ئامێر": "سپێکترۆفۆتۆمیتەر (Roche Cobas c502)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "LDL": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (0, 100), "یەکە": "mg/dL", "تەفسیر": "کۆلسترۆلی خراپ", "ئامێر": "سپێکترۆفۆتۆمیتەر (Roche Cobas c502)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "HDL": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (40, 60), "یەکە": "mg/dL", "تەفسیر": "کۆلسترۆلی باش", "ئامێر": "سپێکترۆفۆتۆمیتەر (Roche Cobas c502)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "Triglycerides": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (0, 150), "یەکە": "mg/dL", "تەفسیر": "تریگلیسیرید", "ئامێر": "سپێکترۆفۆتۆمیتەر (Roche Cobas c502)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "Total Protein": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (6.0, 8.0), "یەکە": "g/dL", "تەفسیر": "پڕۆتینی گشتی", "ئامێر": "سپێکترۆفۆتۆمیتەر (Roche Cobas c502)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
}

# 5.3 پشکنینەکانی دڵ (٤٠ پشکنین)
cardiac_tests = {
    "Troponin I": {"گروپ": "دڵ", "نۆرماڵ": (0, 0.04), "یەکە": "ng/mL", "تەفسیر": "پروتێینی دڵ", "ئامێر": "کیمیایی ئیمینۆ (Roche Cobas e411)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "Troponin T": {"گروپ": "دڵ", "نۆرماڵ": (0, 0.014), "یەکە": "ng/mL", "تەفسیر": "پروتێینی دڵ", "ئامێر": "کیمیایی ئیمینۆ (Roche Cobas e411)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "CK-MB": {"گروپ": "دڵ", "نۆرماڵ": (0, 5), "یەکە": "ng/mL", "تەفسیر": "ئەنزیمی دڵ", "ئامێر": "کیمیایی ئیمینۆ (Roche Cobas e411)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "BNP": {"گروپ": "دڵ", "نۆرماڵ": (0, 100), "یەکە": "pg/mL", "تەفسیر": "پروتێینی دڵ", "ئامێر": "کیمیایی ئیمینۆ (Roche Cobas e411)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "Myoglobin": {"گروپ": "دڵ", "نۆرماڵ": (0, 80), "یەکە": "ng/mL", "تەفسیر": "پروتێین", "ئامێر": "کیمیایی ئیمینۆ (Roche Cobas e411)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "HS-CRP": {"گروپ": "دڵ", "نۆرماڵ": (0, 2), "یەکە": "mg/L", "تەفسیر": "هەوکردنی دڵ", "ئامێر": "توربیدیمیتەر (Roche Cobas c502)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "Homocysteine": {"گروپ": "دڵ", "نۆرماڵ": (5, 15), "یەکە": "μmol/L", "تەفسیر": "مەترسی دڵ", "ئامێر": "HPLC (Agilent 1200)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "ApoB": {"گروپ": "دڵ", "نۆرماڵ": (60, 120), "یەکە": "mg/dL", "تەفسیر": "پرۆتێین", "ئامێر": "نێفێلۆمیتەر (Siemens BNII)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "ApoA": {"گروپ": "دڵ", "نۆرماڵ": (90, 150), "یەکە": "mg/dL", "تەفسیر": "پرۆتێین", "ئامێر": "نێفێلۆمیتەر (Siemens BNII)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "Lipoprotein(a)": {"گروپ": "دڵ", "نۆرماڵ": (0, 30), "یەکە": "mg/dL", "تەفسیر": "مەترسی دڵ", "ئامێر": "نێفێلۆمیتەر (Siemens BNII)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
}

# 5.4 پشکنینەکانی هەوکردن (٣٠ پشکنین)
inflammation_tests = {
    "Procalcitonin": {"گروپ": "هەوکردن", "نۆرماڵ": (0, 0.5), "یەکە": "ng/mL", "تەفسیر": "هەوکردنی بەکتریایی", "ئامێر": "کیمیایی ئیمینۆ (Roche Cobas e411)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "IL-6": {"گروپ": "هەوکردن", "نۆرماڵ": (0, 5), "یەکە": "pg/mL", "تەفسیر": "سایتۆکاینی هەوکردن", "ئامێر": "ELISA Reader (BioTek 800TS)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "TNF-alpha": {"گروپ": "هەوکردن", "نۆرماڵ": (0, 8), "یەکە": "pg/mL", "تەفسیر": "سایتۆکاینی هەوکردن", "ئامێر": "ELISA Reader (BioTek 800TS)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "Ferritin": {"گروپ": "هەوکردن", "نۆرماڵ": (15, 300), "یەکە": "ng/mL", "تەفسیر": "ئاسن", "ئامێر": "کیمیایی ئیمینۆ (Roche Cobas e411)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "LDH": {"گروپ": "هەوکردن", "نۆرماڵ": (100, 250), "یەکە": "U/L", "تەفسیر": "ئەنزیم", "ئامێر": "سپێکترۆفۆتۆمیتەر (Beckman Coulter AU480)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "Haptoglobin": {"گروپ": "هەوکردن", "نۆرماڵ": (50, 250), "یەکە": "mg/dL", "تەفسیر": "پروتێین", "ئامێر": "نێفێلۆمیتەر (Siemens BNII)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
}

# 5.5 پشکنینەکانی هۆرمۆن (٣٠ پشکنین)
hormone_tests = {
    "TSH": {"گروپ": "هۆرمۆن", "نۆرماڵ": (0.4, 4.0), "یەکە": "mIU/L", "تەفسیر": "هۆرمۆنی دروان", "ئامێر": "کیمیایی ئیمینۆ (Roche Cobas e411)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "T4": {"گروپ": "هۆرمۆن", "نۆرماڵ": (5, 12), "یەکە": "μg/dL", "تەفسیر": "هۆرمۆنی دروان", "ئامێر": "کیمیایی ئیمینۆ (Roche Cobas e411)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "T3": {"گروپ": "هۆرمۆن", "نۆرماڵ": (80, 200), "یەکە": "ng/dL", "تەفسیر": "هۆرمۆنی دروان", "ئامێر": "کیمیایی ئیمینۆ (Roche Cobas e411)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "Cortisol": {"گروپ": "هۆرمۆن", "نۆرماڵ": (5, 25), "یەکە": "μg/dL", "تەفسیر": "هۆرمۆنی پەستانی خوێن", "ئامێر": "کیمیایی ئیمینۆ (Roche Cobas e411)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "Insulin": {"گروپ": "هۆرمۆن", "نۆرماڵ": (2, 25), "یەکە": "μIU/mL", "تەفسیر": "هۆرمۆنی شەکر", "ئامێر": "کیمیایی ئیمینۆ (Roche Cobas e411)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "C-peptide": {"گروپ": "هۆرمۆن", "نۆرماڵ": (0.5, 2.0), "یەکە": "ng/mL", "تەفسیر": "پێکهاتەی ئەنسولین", "ئامێر": "کیمیایی ئیمینۆ (Roche Cobas e411)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "ACTH": {"گروپ": "هۆرمۆن", "نۆرماڵ": (10, 60), "یەکە": "pg/mL", "تەفسیر": "هۆرمۆنی دروان", "ئامێر": "کیمیایی ئیمینۆ (Roche Cobas e411)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "Growth Hormone": {"گروپ": "هۆرمۆن", "نۆرماڵ": (0, 5), "یەکە": "ng/mL", "تەفسیر": "هۆرمۆنی گەشە", "ئامێر": "کیمیایی ئیمینۆ (Roche Cobas e411)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "Prolactin": {"گروپ": "هۆرمۆن", "نۆرماڵ": (2, 15), "یەکە": "ng/mL", "تەفسیر": "هۆرمۆنی شیر", "ئامێر": "کیمیایی ئیمینۆ (Roche Cobas e411)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "Testosterone": {"گروپ": "هۆرمۆن", "نۆرماڵ": (300, 1000), "یەکە": "ng/dL", "تەفسیر": "هۆرمۆنی نێر", "ئامێر": "کیمیایی ئیمینۆ (Roche Cobas e411)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "Estradiol": {"گروپ": "هۆرمۆن", "نۆرماڵ": (20, 400), "یەکە": "pg/mL", "تەفسیر": "هۆرمۆنی مێ", "ئامێر": "کیمیایی ئیمینۆ (Roche Cobas e411)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
}

# 5.6 پشکنینەکانی میز (٣٠ پشکنین)
urine_tests = {
    "Urine Protein": {"گروپ": "میز", "نۆرماڵ": (0, 0.3), "یەکە": "g/24h", "تەفسیر": "پڕۆتینی میز", "ئامێر": "سپێکترۆفۆتۆمیتەر (Roche Cobas c502)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "Urine Glucose": {"گروپ": "میز", "نۆرماڵ": (0, 0), "یەکە": "mg/dL", "تەفسیر": "شەکری میز", "ئامێر": "سپێکترۆفۆتۆمیتەر (Roche Cobas c502)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "Urine Ketones": {"گروپ": "میز", "نۆرماڵ": (0, 0), "یەکە": "mg/dL", "تەفسیر": "کیتۆنی میز", "ئامێر": "سپێکترۆفۆتۆمیتەر (Roche Cobas c502)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "Urine WBC": {"گروپ": "میز", "نۆرماڵ": (0, 5), "یەکە": "/HPF", "تەفسیر": "خڕۆکە سپیەکان", "ئامێر": "مایکرۆسکۆپی (Olympus CX23)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "Urine RBC": {"گروپ": "میز", "نۆرماڵ": (0, 3), "یەکە": "/HPF", "تەفسیر": "خڕۆکە سوورەکان", "ئامێر": "مایکرۆسکۆپی (Olympus CX23)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "Urine pH": {"گروپ": "میز", "نۆرماڵ": (5.0, 8.0), "یەکە": "", "تەفسیر": "pH میز", "ئامێر": "pH میتر (Hanna HI221)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "Urine Specific Gravity": {"گروپ": "میز", "نۆرماڵ": (1.005, 1.030), "یەکە": "", "تەفسیر": "چڕی میز", "ئامێر": "ریفڕاکتۆمیتەر (Atago PAL-10S)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
}

# 5.7 پشکنینەکانی ڤیتامین (٢٠ پشکنین)
vitamin_tests = {
    "Vitamin D": {"گروپ": "ڤیتامین", "نۆرماڵ": (30, 100), "یەکە": "ng/mL", "تەفسیر": "ڤیتامین D", "ئامێر": "کیمیایی ئیمینۆ (Roche Cobas e411)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "Vitamin A": {"گروپ": "ڤیتامین", "نۆرماڵ": (20, 80), "یەکە": "μg/dL", "تەفسیر": "ڤیتامین A", "ئامێر": "HPLC (Agilent 1200)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "Vitamin E": {"گروپ": "ڤیتامین", "نۆرماڵ": (5, 18), "یەکە": "mg/L", "تەفسیر": "ڤیتامین E", "ئامێر": "HPLC (Agilent 1200)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "Vitamin K": {"گروپ": "ڤیتامین", "نۆرماڵ": (0.2, 3.0), "یەکە": "ng/mL", "تەفسیر": "ڤیتامین K", "ئامێر": "HPLC (Agilent 1200)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "Vitamin C": {"گروپ": "ڤیتامین", "نۆرماڵ": (0.6, 2.0), "یەکە": "mg/dL", "تەفسیر": "ڤیتامین C", "ئامێر": "HPLC (Agilent 1200)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
}

# 5.8 پشکنینەکانی معدن (٢٠ پشکنین)
mineral_tests = {
    "Zinc": {"گروپ": "معدن", "نۆرماڵ": (70, 120), "یەکە": "μg/dL", "تەفسیر": "زینک", "ئامێر": "ICP-MS (Agilent 7800)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "Selenium": {"گروپ": "معدن", "نۆرماڵ": (70, 150), "یەکە": "μg/L", "تەفسیر": "سێلینیۆم", "ئامێر": "ICP-MS (Agilent 7800)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "Copper": {"گروپ": "معدن", "نۆرماڵ": (70, 140), "یەکە": "μg/dL", "تەفسیر": "کۆپر", "ئامێر": "ICP-MS (Agilent 7800)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "Manganese": {"گروپ": "معدن", "نۆرماڵ": (4, 15), "یەکە": "μg/L", "تەفسیر": "مەنگەنیز", "ئامێر": "ICP-MS (Agilent 7800)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
    "Chromium": {"گروپ": "معدن", "نۆرماڵ": (0.5, 2.0), "یەکە": "μg/L", "تەفسیر": "کرۆمیۆم", "ئامێر": "ICP-MS (Agilent 7800)", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
}

# یەکخستنی هەموو پشکنینەکان
for test_dict in [blood_tests, biochem_tests, cardiac_tests, inflammation_tests, hormone_tests, urine_tests, vitamin_tests, mineral_tests]:
    LAB_TESTS.update(test_dict)

# ================================
# 6. داتابەسی دەرمانەکان (١٢٠+ دەرمان) - بە وەسفی تەواو و تێبینی
# ================================
DRUG_DATABASE = {
    "دژە پەستانی خوێن": {
        "کاپتۆپریل": {"ڕێژە": "25-50mg", "میکانیزم": "ACE inhibitor", "کاریگەری لاوەکی": "کۆخە, سەرگێژخواردن", "پێچەوانە": "حەملی دووگانی", "وەسف": "دەرمانی ACE inhibitor کە پەستانی خوێن کەم دەکاتەوە بە فراوانکردنی خوێنبەرەکان", "بۆچی": "بۆ کەمکردنەوەی پەستانی خوێن و پاراستنی گورچیلە لە نەخۆشانی شەکرە", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "ئەملۆدیپین": {"ڕێژە": "5-10mg", "میکانیزم": "Calcium channel blocker", "کاریگەری لاوەکی": "ئاوسانی قاچ", "پێچەوانە": "هەستیاری", "وەسف": "بەربەستەری کالسیۆم کە خوێنبەرەکان فراوان دەکات", "بۆچی": "بۆ چارەسەری پەستانی خوێنی بەرز و ئازاری سنگ", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "لۆسارتان": {"ڕێژە": "50-100mg", "میکانیزم": "ARB", "کاریگەری لاوەکی": "سەرگێژخواردن", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "بەربەستەری گیرۆدەی ئەنجیۆتێنسین کە خوێنبەرەکان فراوان دەکات", "بۆچی": "بۆ چارەسەری پەستانی خوێن و پاراستنی گورچیلە", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "بایسۆپرۆلۆل": {"ڕێژە": "2.5-10mg", "میکانیزم": "Beta blocker", "کاریگەری لاوەکی": "خاوکردنەوەی دڵ", "پێچەوانە": "ئەستمی هەوە", "وەسف": "بەربەستەری بیتا کە لێدانی دڵ خاو دەکاتەوە", "بۆچی": "بۆ پەستانی خوێن و نەخۆشی دڵی ئیسکیمیک", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "هیدروکلۆرۆتایزید": {"ڕێژە": "12.5-25mg", "میکانیزم": "Thiazide diuretic", "کاریگەری لاوەکی": "نزمی پۆتاسیۆم", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "دەرمانی دەرکەری ئاو کە شلەمەنی زیاد لە جەستە دەر دەکات", "بۆچی": "بۆ کەمکردنەوەی پەستانی خوێن بە دەرکردنی نمەک و ئاو", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "فورۆسیماید": {"ڕێژە": "20-40mg", "میکانیزم": "Loop diuretic", "کاریگەری لاوەکی": "نزمی پۆتاسیۆم", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "دەرمانی دەرکەری بەهێز بۆ دەرکردنی ئاو و نمەک", "بۆچی": "بۆ چارەسەری پەستانی خوێن و ئاوسان لە نەخۆشی دڵ و گورچیلە", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "کارڤیدیلۆل": {"ڕێژە": "6.25-25mg", "میکانیزم": "Beta blocker", "کاریگەری لاوەکی": "سەرگێژخواردن", "پێچەوانە": "ئەستمی هەوە", "وەسف": "بەربەستەری بیتا کە خوێنبەرەکان فراوان دەکات", "بۆچی": "بۆ نەخۆشی دڵی شکان و پەستانی خوێن", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "نایترۆگلیسیرین": {"ڕێژە": "0.3-0.6mg", "میکانیزم": "Nitrate", "کاریگەری لاوەکی": "سەرئێشە", "پێچەوانە": "نزمی BP", "وەسف": "دەرمانی فراوانکەری خوێنبەرەکان", "بۆچی": "بۆ چارەسەری ئازاری سنگ و نەخۆشی دڵی ئیسکیمیک", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "ئیسۆسۆرباید": {"ڕێژە": "10-30mg", "میکانیزم": "Nitrate", "کاریگەری لاوەکی": "سەرئێشە", "پێچەوانە": "نزمی BP", "وەسف": "دەرمانی نایترات بۆ فراوانکردنی خوێنبەرەکان", "بۆچی": "بۆ پێشگیری لە ئازاری سنگ", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "دیلتیازەم": {"ڕێژە": "30-60mg", "میکانیزم": "Calcium blocker", "کاریگەری لاوەکی": "سەرگێژخواردن", "پێچەوانە": "نەخۆشی دڵ", "وەسف": "بەربەستەری کالسیۆم بۆ خوێنبەرەکان", "بۆچی": "بۆ پەستانی خوێن و ئازاری سنگ", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "ڤێراپامیل": {"ڕێژە": "40-80mg", "میکانیزم": "Calcium blocker", "کاریگەری لاوەکی": "خاوکردنەوەی دڵ", "پێچەوانە": "نەخۆشی دڵ", "وەسف": "بەربەستەری کالسیۆم کە دڵ خاو دەکاتەوە", "بۆچی": "بۆ چارەسەری ئازاری سنگ و پەستانی خوێن", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "آتنۆلۆل": {"ڕێژە": "25-50mg", "میکانیزم": "Beta blocker", "کاریگەری لاوەکی": "ماندوویی", "پێچەوانە": "ئەستمی هەوە", "وەسف": "بەربەستەری بیتا بۆ کەمکردنەوەی کاری دڵ", "بۆچی": "بۆ پەستانی خوێن و نەخۆشی دڵ", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "میتۆپرۆلۆل": {"ڕێژە": "25-50mg", "میکانیزم": "Beta blocker", "کاریگەری لاوەکی": "خاوکردنەوەی دڵ", "پێچەوانە": "ئەستمی هەوە", "وەسف": "بەربەستەری بیتا بۆ دڵ و خوێنبەرەکان", "بۆچی": "بۆ پەستانی خوێن و نەخۆشی دڵی شکان", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "پروپانۆلۆل": {"ڕێژە": "10-40mg", "میکانیزم": "Beta blocker", "کاریگەری لاوەکی": "سەرگێژخواردن", "پێچەوانە": "ئەستمی هەوە", "وەسف": "بەربەستەری بیتا بۆ کەمکردنەوەی دڵ", "بۆچی": "بۆ پەستانی خوێن، ئازاری سنگ، و خێرایی دڵ", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "رامبەریل": {"ڕێژە": "1.25-5mg", "میکانیزم": "ACE inhibitor", "کاریگەری لاوەکی": "کۆخە", "پێچەوانە": "حەمل", "وەسف": "ACE inhibitor بۆ کەمکردنەوەی پەستانی خوێن", "بۆچی": "بۆ پاراستنی گورچیلە و کەمکردنەوەی پەستانی خوێن", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "کینیاپریل": {"ڕێژە": "5-20mg", "میکانیزم": "ACE inhibitor", "کاریگەری لاوەکی": "کۆخە", "پێچەوانە": "حەمل", "وەسف": "ACE inhibitor بۆ خوێنبەرەکان", "بۆچی": "بۆ پەستانی خوێن و نەخۆشی دڵ", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "تێلمیسارتان": {"ڕێژە": "40-80mg", "میکانیزم": "ARB", "کاریگەری لاوەکی": "سەرگێژخواردن", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "بەربەستەری گیرۆدەی ئەنجیۆتێنسین", "بۆچی": "بۆ پەستانی خوێن و پاراستنی گورچیلە", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "ئیربێسارتان": {"ڕێژە": "150-300mg", "میکانیزم": "ARB", "کاریگەری لاوەکی": "سەرگێژخواردن", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "ARB بۆ کەمکردنەوەی پەستانی خوێن", "بۆچی": "بۆ پەستانی خوێن و نەخۆشی گورچیلە", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "فۆزینۆپریل": {"ڕێژە": "10-40mg", "میکانیزم": "ACE inhibitor", "کاریگەری لاوەکی": "کۆخە", "پێچەوانە": "حەمل", "وەسف": "ACE inhibitor بۆ خوێنبەرەکان", "بۆچی": "بۆ پەستانی خوێن", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "سپیرۆنۆلاکتۆن": {"ڕێژە": "25-50mg", "میکانیزم": "Aldosterone antagonist", "کاریگەری لاوەکی": "بەرزی پۆتاسیۆم", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "دژە ئەلدۆستێرۆن بۆ دەرکردنی ئاو و نمەک", "بۆچی": "بۆ پەستانی خوێن و نەخۆشی دڵی شکان", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."}
    },
    "دژە شەکرە": {
        "مێتفۆرمین": {"ڕێژە": "500-2000mg", "میکانیزم": "Biguanide", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "دەرمانی هێڵی یەکەم بۆ شەکرەی جۆری ٢ - کەمکردنی بەرهەمهێنانی شەکر لە جگەر و زیادکردنی هەستی ئەنسولین", "بۆچی": "بۆ کۆنتڕۆڵکردنی شەکری خوێن لە نەخۆشانی شەکرەی جۆری ٢", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "گلیپیزاید": {"ڕێژە": "5-20mg", "میکانیزم": "Sulfonylurea", "کاریگەری لاوەکی": "هایپۆگلایسیمیا", "پێچەوانە": "هەستیاری", "وەسف": "دەرمانی سەلفۆنیل یوریا کە پەنکریاس هان دەدات بۆ بەرهەمهێنانی زیاتری ئەنسولین", "بۆچی": "بۆ کەمکردنەوەی شەکری خوێن لە شەکرەی جۆری ٢", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "ئەنسولین Glargine": {"ڕێژە": "10-40 IU", "میکانیزم": "Insulin analog", "کاریگەری لاوەکی": "هایپۆگلایسیمیا", "پێچەوانە": "هایپۆگلایسیمیا", "وەسف": "ئەنسولینی درێژخایەن کە شەکر بە درێژایی ٢٤ کاتژمێر کۆنتڕۆڵ دەکات", "بۆچی": "بۆ کۆنتڕۆڵی شەکری خوێن لە شەکرەی جۆری ١ و جۆری ٢", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "سیتاگلیپتین": {"ڕێژە": "100mg", "میکانیزم": "DPP-4 inhibitor", "کاریگەری لاوەکی": "سەرئێشە", "پێچەوانە": "نەخۆشی پەنکریاس", "وەسف": "بەربەستەری DPP-4 کە ئاستی GLP-1 زیاد دەکات بۆ کەمکردنەوەی شەکر", "بۆچی": "بۆ کۆنتڕۆڵی شەکری خوێن لە شەکرەی جۆری ٢", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "ساکساگلیپتین": {"ڕێژە": "5mg", "میکانیزم": "DPP-4 inhibitor", "کاریگەری لاوەکی": "سەرئێشە", "پێچەوانە": "نەخۆشی پەنکریاس", "وەسف": "بەربەستەری DPP-4 بۆ کەمکردنەوەی شەکر", "بۆچی": "بۆ شەکرەی جۆری ٢", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "لیناگلیپتین": {"ڕێژە": "5mg", "میکانیزم": "DPP-4 inhibitor", "کاریگەری لاوەکی": "سەرئێشە", "پێچەوانە": "نەخۆشی پەنکریاس", "وەسف": "بەربەستەری DPP-4 بۆ شەکر", "بۆچی": "بۆ شەکرەی جۆری ٢", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "ئەلبیکوتاید": {"ڕێژە": "1-2mg", "میکانیزم": "GLP-1 agonist", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "نەخۆشی پەنکریاس", "وەسف": "هاندهری GLP-1 بۆ کەمکردنەوەی شەکر و کێش", "بۆچی": "بۆ شەکرەی جۆری ٢ و کەمکردنەوەی کێش", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "لیراگلوتاید": {"ڕێژە": "0.6-1.8mg", "میکانیزم": "GLP-1 agonist", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "نەخۆشی پەنکریاس", "وەسف": "هاندهری GLP-1 بۆ کۆنتڕۆڵی شەکر و کەمکردنەوەی کێش", "بۆچی": "بۆ شەکرەی جۆری ٢ و نەخۆشی دڵ", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "دولاگلوتاید": {"ڕێژە": "0.75-1.5mg", "میکانیزم": "GLP-1 agonist", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "نەخۆشی پەنکریاس", "وەسف": "هاندهری GLP-1 بۆ کۆنتڕۆڵی شەکر", "بۆچی": "بۆ شەکرەی جۆری ٢", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "ئەنسولین Aspart": {"ڕێژە": "2-10 IU", "میکانیزم": "Insulin analog", "کاریگەری لاوەکی": "هایپۆگلایسیمیا", "پێچەوانە": "هایپۆگلایسیمیا", "وەسف": "ئەنسولینی خێرا بۆ کۆنتڕۆڵی شەکری پاش خواردن", "بۆچی": "بۆ شەکرەی جۆری ١ و جۆری ٢", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "ئەنسولین Lispro": {"ڕێژە": "2-10 IU", "میکانیزم": "Insulin analog", "کاریگەری لاوەکی": "هایپۆگلایسیمیا", "پێچەوانە": "هایپۆگلایسیمیا", "وەسف": "ئەنسولینی خێرا بۆ کۆنتڕۆڵی شەکر", "بۆچی": "بۆ شەکرەی جۆری ١ و جۆری ٢", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "ئەنسولین Regular": {"ڕێژە": "2-10 IU", "میکانیزم": "Insulin", "کاریگەری لاوەکی": "هایپۆگلایسیمیا", "پێچەوانە": "هایپۆگلایسیمیا", "وەسف": "ئەنسولینی ستاندارد بۆ کۆنتڕۆڵی شەکر", "بۆچی": "بۆ شەکرەی جۆری ١ و جۆری ٢", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "گلیمێپیراید": {"ڕێژە": "1-4mg", "میکانیزم": "Sulfonylurea", "کاریگەری لاوەکی": "هایپۆگلایسیمیا", "پێچەوانە": "هەستیاری", "وەسف": "سەلفۆنیل یوریا بۆ زیادی ئەنسولین", "بۆچی": "بۆ شەکرەی جۆری ٢", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "پایۆگلیتازۆن": {"ڕێژە": "15-45mg", "میکانیزم": "Thiazolidinedione", "کاریگەری لاوەکی": "ئاوسان", "پێچەوانە": "نەخۆشی دڵ", "وەسف": "زیادکەری هەستی ئەنسولین لە شانەکاندا", "بۆچی": "بۆ شەکرەی جۆری ٢", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "ئەکاربۆس": {"ڕێژە": "25-50mg", "میکانیزم": "Alpha-glucosidase inhibitor", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "نەخۆشی گەدە", "وەسف": "بەربەستەری هەرسکردنی کاربۆهیدرات بۆ کەمکردنەوەی شەکر", "بۆچی": "بۆ شەکرەی جۆری ٢", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."}
    },
    "دژە کۆخە و هەوکردن": {
        "ئەمۆکسیسیلین": {"ڕێژە": "500mg", "میکانیزم": "Beta-lactam", "کاریگەری لاوەکی": "زکچوون", "پێچەوانە": "هەستیاری پێنیسیلین", "وەسف": "ئەنتیبایۆتیکی پێنیسیلین بۆ هەوکردنی بەکتریایی", "بۆچی": "بۆ هەوکردنی سییەکان، گەدە، میز", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "ئازیترۆمایسین": {"ڕێژە": "250-500mg", "میکانیزم": "Macrolide", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "نەخۆشی دڵ", "وەسف": "ئەنتیبایۆتیکی ماکرۆلید بۆ هەوکردنی هەناسە", "بۆچی": "بۆ هەوکردنی سییەکان و کۆکە", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "سیپرۆفلۆکساسین": {"ڕێژە": "500mg", "میکانیزم": "Fluoroquinolone", "کاریگەری لاوەکی": "ئازاری ماسوولکە", "پێچەوانە": "منداڵان", "وەسف": "ئەنتیبایۆتیکی فلۆرۆکینۆلۆن بۆ هەوکردنی بەکتریایی", "بۆچی": "بۆ هەوکردنی میز و سییەکان", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "سێفتریاکسۆن": {"ڕێژە": "1-2g", "میکانیزم": "Cephalosporin", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "هەستیاری", "وەسف": "ئەنتیبایۆتیکی سێفالۆسپۆرین بۆ هەوکردنی توند", "بۆچی": "بۆ هەوکردنی سییەکان، گورچیلە، و خوێن", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "دۆکسیسایکلین": {"ڕێژە": "100mg", "میکانیزم": "Tetracycline", "کاریگەری لاوەکی": "زکچوون", "پێچەوانە": "منداڵان", "وەسف": "ئەنتیبایۆتیکی تێتراسایکلین بۆ هەوکردنی جۆراوجۆر", "بۆچی": "بۆ هەوکردنی سییەکان، کۆلێرا، و سیل", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "تتراسایکلین": {"ڕێژە": "250-500mg", "میکانیزم": "Tetracycline", "کاریگەری لاوەکی": "زکچوون", "پێچەوانە": "منداڵان", "وەسف": "ئەنتیبایۆتیکی تێتراسایکلین", "بۆچی": "بۆ هەوکردنی پێست و سییەکان", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "کوتریمۆکسازۆل": {"ڕێژە": "400-800mg", "میکانیزم": "Sulfonamide", "کاریگەری لاوەکی": "زکچوون", "پێچەوانە": "هەستیاری", "وەسف": "ئەنتیبایۆتیکی سەلفۆنامید", "بۆچی": "بۆ هەوکردنی میز و سییەکان", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "مێترۆنیدازۆل": {"ڕێژە": "250-500mg", "میکانیزم": "Nitroimidazole", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "حەمل", "وەسف": "ئەنتیبایۆتیک بۆ بەکتریای ئانایروب", "بۆچی": "بۆ هەوکردنی گەدە و خوێن", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "فینوکسیمایسین": {"ڕێژە": "250mg", "میکانیزم": "Macrolide", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "نەخۆشی دڵ", "وەسف": "ئەنتیبایۆتیکی ماکرۆلید", "بۆچی": "بۆ هەوکردنی هەناسە", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "سێفیکسیم": {"ڕێژە": "400mg", "میکانیزم": "Cephalosporin", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "هەستیاری", "وەسف": "سێفالۆسپۆرین بۆ هەوکردنی میز و سییەکان", "بۆچی": "بۆ هەوکردنی میز و کۆکە", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "لیفلوکسایسین": {"ڕێژە": "500mg", "میکانیزم": "Fluoroquinolone", "کاریگەری لاوەکی": "ئازاری ماسوولکە", "پێچەوانە": "منداڵان", "وەسف": "فلۆرۆکینۆلۆن بۆ هەوکردن", "بۆچی": "بۆ هەوکردنی سییەکان و میز", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "مۆکسیفلۆکساسین": {"ڕێژە": "400mg", "میکانیزم": "Fluoroquinolone", "کاریگەری لاوەکی": "ئازاری ماسوولکە", "پێچەوانە": "منداڵان", "وەسف": "فلۆرۆکینۆلۆن", "بۆچی": "بۆ هەوکردنی سییەکان", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "ریفامپیسین": {"ڕێژە": "600mg", "میکانیزم": "Antibiotic", "کاریگەری لاوەکی": "زەردبوون", "پێچەوانە": "نەخۆشی جگەر", "وەسف": "ئەنتیبایۆتیک بۆ سیل", "بۆچی": "بۆ چارەسەری سیل", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "ئایسۆنیازید": {"ڕێژە": "300mg", "میکانیزم": "Antibiotic", "کاریگەری لاوەکی": "زیان بە جگەر", "پێچەوانە": "نەخۆشی جگەر", "وەسف": "ئەنتیبایۆتیک بۆ سیل", "بۆچی": "بۆ چارەسەری سیل", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "پیرازیناماید": {"ڕێژە": "1500mg", "میکانیزم": "Antibiotic", "کاریگەری لاوەکی": "ئازاری جومگە", "پێچەوانە": "نەخۆشی جگەر", "وەسف": "ئەنتیبایۆتیک بۆ سیل", "بۆچی": "بۆ چارەسەری سیل", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."}
    },
    "دژە ئەنیمیا": {
        "فێروس سولفەیت": {"ڕێژە": "300-600mg", "میکانیزم": "Iron supplement", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "هیمۆکروماتۆسیس", "وەسف": "پڕکەری ئاسن بۆ چارەسەری ئەنیمیای کەمخوێنی ئاسن", "بۆچی": "بۆ زیادی ئاسن لە جەستە و چارەسەری ئەنیمیا", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "فۆلیک ئەسید": {"ڕێژە": "1mg", "میکانیزم": "Folate supplement", "کاریگەری لاوەکی": "کەم", "پێچەوانە": "هەستیاری", "وەسف": "پڕکەری فۆلیک ئەسید بۆ ئەنیمیای ماکرۆسایتیک", "بۆچی": "بۆ زیادکردنی فۆلیک ئەسید و چارەسەری ئەنیمیا", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "ڤیتامین B12": {"ڕێژە": "1000mcg", "میکانیزم": "Cobalamin", "کاریگەری لاوەکی": "کەم", "پێچەوانە": "هەستیاری", "وەسف": "پڕکەری ڤیتامین B12 بۆ ئەنیمیای ماکرۆسایتیک", "بۆچی": "بۆ چارەسەری ئەنیمیای کەمخوێنی B12", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "ئەریترۆپۆیتین": {"ڕێژە": "50-100 IU/kg", "میکانیزم": "Erythropoietin", "کاریگەری لاوەکی": "BP بەرز", "پێچەوانە": "نەخۆشی دڵ", "وەسف": "هۆرمۆنی دروستکردنی خڕۆکە سوورەکان", "بۆچی": "بۆ زیادکردنی خڕۆکە سوورەکان لە نەخۆشی گورچیلە", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "سیانۆکۆبالامین": {"ڕێژە": "1000mcg", "میکانیزم": "Vitamin B12", "کاریگەری لاوەکی": "کەم", "پێچەوانە": "هەستیاری", "وەسف": "پڕکەری ڤیتامین B12", "بۆچی": "بۆ ئەنیمیای ماکرۆسایتیک", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "ئاسن دیکستران": {"ڕێژە": "100-200mg", "میکانیزم": "Iron supplement", "کاریگەری لاوەکی": "هەستیاری", "پێچەوانە": "هیمۆکروماتۆسیس", "وەسف": "پڕکەری ئاسن بۆ نەخۆشانی گورچیلە", "بۆچی": "بۆ چارەسەری ئەنیمیای کەمخوێنی ئاسن", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "دێسفێریۆکسامین": {"ڕێژە": "500-1000mg", "میکانیزم": "Iron chelator", "کاریگەری لاوەکی": "زیان بە گورچیلە", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "دەرمانی دەرکردنی ئاسنی زۆر لە جەستە", "بۆچی": "بۆ چارەسەری هیمۆکروماتۆسیس", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "فۆلیک اسید": {"ڕێژە": "1-5mg", "میکانیزم": "Folate", "کاریگەری لاوەکی": "کەم", "پێچەوانە": "هەستیاری", "وەسف": "پڕکەری فۆلیک ئەسید", "بۆچی": "بۆ ئەنیمیای ماکرۆسایتیک", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "دەیکسۆمیتازۆن": {"ڕێژە": "0.5-2mg", "میکانیزم": "Steroid", "کاریگەری لاوەکی": "کێش زیادکردن", "پێچەوانە": "هەوکردن", "وەسف": "ستیرۆید بۆ هەوکردن و ئەنیمیا", "بۆچی": "بۆ چارەسەری ئەنیمیای هیمۆلایتیک", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "پرەدنیسۆلۆن": {"ڕێژە": "5-20mg", "میکانیزم": "Steroid", "کاریگەری لاوەکی": "کێش زیادکردن", "پێچەوانە": "هەوکردن", "وەسف": "ستیرۆید بۆ هەوکردن و خۆئەگەری", "بۆچی": "بۆ ئەنیمیای هیمۆلایتیک", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."}
    },
    "دژە کۆکە": {
        "سالبوتامۆل": {"ڕێژە": "2 puffs", "میکانیزم": "Beta-2 agonist", "کاریگەری لاوەکی": "لەرزین", "پێچەوانە": "نەخۆشی دڵ", "وەسف": "فراوانکەری بۆڕی هەناسە بۆ کۆکە", "بۆچی": "بۆ چارەسەری کۆکە و COPD", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "بۆدیزۆناید": {"ڕێژە": "200-800mcg", "میکانیزم": "Steroid inhaler", "کاریگەری لاوەکی": "هەوکردنی دەم", "پێچەوانە": "هەستیاری", "وەسف": "ستیرۆیدی هەناسەدان بۆ کەمکردنەوەی هەوکردن", "بۆچی": "بۆ پێشگیری لە کۆکە", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "فۆرمۆتێرۆل": {"ڕێژە": "6-12mcg", "میکانیزم": "Beta-2 agonist", "کاریگەری لاوەکی": "لەرزین", "پێچەوانە": "نەخۆشی دڵ", "وەسف": "فراوانکەری بۆڕی هەناسە", "بۆچی": "بۆ کۆکە و COPD", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "فلوتیکاسۆن": {"ڕێژە": "250-500mcg", "میکانیزم": "Steroid inhaler", "کاریگەری لاوەکی": "هەوکردنی دەم", "پێچەوانە": "هەستیاری", "وەسف": "ستیرۆیدی هەناسەدان", "بۆچی": "بۆ کۆکە", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "مۆنتلۆکاست": {"ڕێژە": "10mg", "میکانیزم": "Leukotriene inhibitor", "کاریگەری لاوەکی": "سەرئێشە", "پێچەوانە": "هەستیاری", "وەسف": "بەربەستەری لیوکۆترین بۆ کەمکردنەوەی هەوکردن", "بۆچی": "بۆ کۆکە و هەستێکی هەوە", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "زافیرلوکاست": {"ڕێژە": "20mg", "میکانیزم": "Leukotriene inhibitor", "کاریگەری لاوەکی": "سەرئێشە", "پێچەوانە": "هەستیاری", "وەسف": "بەربەستەری لیوکۆترین", "بۆچی": "بۆ کۆکە", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "تیۆترۆپیۆم": {"ڕێژە": "18mcg", "میکانیزم": "Anticholinergic", "کاریگەری لاوەکی": "دەم وشک", "پێچەوانە": "نەخۆشی دڵ", "وەسف": "بەربەستەری ئەستیلکۆلین بۆ فراوانکردنی بۆڕی هەناسە", "بۆچی": "بۆ COPD و کۆکە", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "ئیپرەترۆپیۆم": {"ڕێژە": "20mcg", "میکانیزم": "Anticholinergic", "کاریگەری لاوەکی": "دەم وشک", "پێچەوانە": "نەخۆشی دڵ", "وەسف": "بەربەستەری ئەستیلکۆلین", "بۆچی": "بۆ COPD", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "تئۆفیلین": {"ڕێژە": "100-200mg", "میکانیزم": "Bronchodilator", "کاریگەری لاوەکی": "خێرالێدانی دڵ", "پێچەوانە": "نەخۆشی دڵ", "وەسف": "فراوانکەری بۆڕی هەناسە", "بۆچی": "بۆ کۆکە و COPD", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "ئامینۆفیلین": {"ڕێژە": "100-200mg", "میکانیزم": "Bronchodilator", "کاریگەری لاوەکی": "خێرالێدانی دڵ", "پێچەوانە": "نەخۆشی دڵ", "وەسف": "فراوانکەری بۆڕی هەناسە", "بۆچی": "بۆ کۆکە", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."}
    },
    "دژە سکچوون": {
        "ئومەپرازۆل": {"ڕێژە": "20-40mg", "میکانیزم": "PPI", "کاریگەری لاوەکی": "سەرئێشە", "پێچەوانە": "نەخۆشی جگەر", "وەسف": "بەربەستەری پمپەی پرۆتۆن بۆ کەمکردنەوەی ترشێتی گەدە", "بۆچی": "بۆ چارەسەری سکچوون و برینداری گەدە", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "لانسۆپرازۆل": {"ڕێژە": "30mg", "میکانیزم": "PPI", "کاریگەری لاوەکی": "سەرئێشە", "پێچەوانە": "نەخۆشی جگەر", "وەسف": "بەربەستەری پمپەی پرۆتۆن", "بۆچی": "بۆ سکچوون", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "پانتۆپرازۆل": {"ڕێژە": "40mg", "میکانیزم": "PPI", "کاریگەری لاوەکی": "سەرئێشە", "پێچەوانە": "نەخۆشی جگەر", "وەسف": "بەربەستەری پمپەی پرۆتۆن", "بۆچی": "بۆ گەدە و سکچوون", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "ڕابێپرازۆل": {"ڕێژە": "20mg", "میکانیزم": "PPI", "کاریگەری لاوەکی": "سەرئێشە", "پێچەوانە": "نەخۆشی جگەر", "وەسف": "PPI بۆ کەمکردنەوەی ترشێتی", "بۆچی": "بۆ سکچوون", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "ڕانیتیدین": {"ڕێژە": "150mg", "میکانیزم": "H2 blocker", "کاریگەری لاوەکی": "سەرگێژخواردن", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "بەربەستەری H2 بۆ کەمکردنەوەی ترشێتی", "بۆچی": "بۆ سکچوون", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "فامۆتیدین": {"ڕێژە": "20-40mg", "میکانیزم": "H2 blocker", "کاریگەری لاوەکی": "سەرگێژخواردن", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "بەربەستەری H2", "بۆچی": "بۆ سکچوون", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "سوکرالفەیت": {"ڕێژە": "1g", "میکانیزم": "Mucosal protectant", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "پارێزەری پەردەی گەدە", "بۆچی": "بۆ برینداری گەدە", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "بسمەت سابیسیلیت": {"ڕێژە": "262mg", "میکانیزم": "Antidiarrheal", "کاریگەری لاوەکی": "زکچوون", "پێچەوانە": "منداڵان", "وەسف": "دژە سکچوون بۆ کەمکردنەوەی سکچوون", "بۆچی": "بۆ سکچوون و گەدە", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "میزۆپرۆستۆل": {"ڕێژە": "100-200mcg", "میکانیزم": "Prostaglandin", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "حەمل", "وەسف": "پرۆستاگلاندین بۆ پاراستنی گەدە", "بۆچی": "بۆ پێشگیری لە برینداری گەدە لە NSAIDs", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "سوکرالفەیت": {"ڕێژە": "1g", "میکانیزم": "Mucosal protectant", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "پارێزەری گەدە", "بۆچی": "بۆ برینداری گەدە", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."}
    },
    "دژە ئازار": {
        "ئەسپیرین": {"ڕێژە": "75-300mg", "میکانیزم": "NSAID", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "خوێنبەربوون", "وەسف": "دژە ئازار و دژە تەمەن بۆ کەمکردنەوەی ئازار و تا", "بۆچی": "بۆ ئازاری کەم و ناوەند و پێشگیری لە خوێن مەبەست", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "ئیبۆپروفین": {"ڕێژە": "200-400mg", "میکانیزم": "NSAID", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "دژە ئازار و دژە هەوکردن", "بۆچی": "بۆ ئازاری ماسوولکە و سەرئێشە", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "نابومیتۆن": {"ڕێژە": "500mg", "میکانیزم": "NSAID", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "دژە هەوکردن بۆ ئازاری جومگەکان", "بۆچی": "بۆ ئازاری جومگە و ئارتریت", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "پاراستامۆل": {"ڕێژە": "500-1000mg", "میکانیزم": "Analgesic", "کاریگەری لاوەکی": "زیان بە جگەر", "پێچەوانە": "نەخۆشی جگەر", "وەسف": "دژە ئازار و دژە تەمەن بۆ هەموو ئازارەکان", "بۆچی": "بۆ ئازاری سەرئێشە و تا", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "مۆرفین": {"ڕێژە": "5-10mg", "میکانیزم": "Opioid", "کاریگەری لاوەکی": "خەوی", "پێچەوانە": "نەخۆشی هەناسە", "وەسف": "دژە ئازاری بەهێز بۆ ئازاری توند", "بۆچی": "بۆ ئازاری توند وەک ئازاری شێرپەنجە", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "کۆدەین": {"ڕێژە": "30mg", "میکانیزم": "Opioid", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "منداڵان", "وەسف": "دژە ئازاری مامناوەند", "بۆچی": "بۆ ئازاری مامناوەند", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "ترامادۆل": {"ڕێژە": "50mg", "میکانیزم": "Opioid", "کاریگەری لاوەکی": "سەرگێژخواردن", "پێچەوانە": "نەخۆشی دڵ", "وەسف": "دژە ئازاری نا ئۆپیۆیدی", "بۆچی": "بۆ ئازاری مامناوەند", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "پێتیدین": {"ڕێژە": "50mg", "میکانیزم": "Opioid", "کاریگەری لاوەکی": "سەرگێژخواردن", "پێچەوانە": "نەخۆشی دڵ", "وەسف": "دژە ئازاری بەهێز", "بۆچی": "بۆ ئازاری توند", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "ناکسۆکسان": {"ڕێژە": "5-10mg", "میکانیزم": "Opioid", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "نەخۆشی دڵ", "وەسف": "دژە ئازار", "بۆچی": "بۆ ئازاری ناوەند", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "فوێنتانیل": {"ڕێژە": "25mcg", "میکانیزم": "Opioid", "کاریگەری لاوەکی": "خەوی", "پێچەوانە": "نەخۆشی هەناسە", "وەسف": "دژە ئازاری زۆر بەهێز", "بۆچی": "بۆ ئازاری شێرپەنجە", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."}
    },
    "دژە خوێن": {
        "وارفارین": {"ڕێژە": "5mg", "میکانیزم": "Vitamin K antagonist", "کاریگەری لاوەکی": "خوێنبەربوون", "پێچەوانە": "حەمل", "وەسف": "دژە خوێن بۆ پێشگیری لە مەبەست", "بۆچی": "بۆ پێشگیری لە خوێن مەبەست", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "هێپارین": {"ڕێژە": "5000 IU", "میکانیزم": "Anticoagulant", "کاریگەری لاوەکی": "خوێنبەربوون", "پێچەوانە": "خوێنبەربوون", "وەسف": "دژە خوێنی خێرا بۆ نەخۆشخانە", "بۆچی": "بۆ پێشگیری لە مەبەست", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "ئەنۆکساپارین": {"ڕێژە": "40mg", "میکانیزم": "LMWH", "کاریگەری لاوەکی": "خوێنبەربوون", "پێچەوانە": "خوێنبەربوون", "وەسف": "دژە خوێنی کەم کێش", "بۆچی": "بۆ پێشگیری لە مەبەست", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "کلۆپیدۆگرێل": {"ڕێژە": "75mg", "میکانیزم": "Antiplatelet", "کاریگەری لاوەکی": "خوێنبەربوون", "پێچەوانە": "خوێنبەربوون", "وەسف": "دژە پلەیتلێت بۆ پێشگیری لە مەبەست", "بۆچی": "بۆ نەخۆشی دڵی ئیسکیمیک", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "پراسوگرێل": {"ڕێژە": "10mg", "میکانیزم": "Antiplatelet", "کاریگەری لاوەکی": "خوێنبەربوون", "پێچەوانە": "خوێنبەربوون", "وەسف": "دژە پلەیتلێت", "بۆچی": "بۆ ئازاری سنگ", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "تیکاگرێلۆر": {"ڕێژە": "90mg", "میکانیزم": "Antiplatelet", "کاریگەری لاوەکی": "خوێنبەربوون", "پێچەوانە": "خوێنبەربوون", "وەسف": "دژە پلەیتلێت", "بۆچی": "بۆ نەخۆشی دڵ", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "دابیگاتران": {"ڕێژە": "110mg", "میکانیزم": "Direct thrombin inhibitor", "کاریگەری لاوەکی": "خوێنبەربوون", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "بەربەستەری ترۆمبین", "بۆچی": "بۆ پێشگیری لە مەبەست", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "ریڤارۆکسابان": {"ڕێژە": "10mg", "میکانیزم": "Factor Xa inhibitor", "کاریگەری لاوەکی": "خوێنبەربوون", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "بەربەستەری فاکتۆر Xa", "بۆچی": "بۆ مەبەست", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "ئەپیکسابان": {"ڕێژە": "2.5-5mg", "میکانیزم": "Factor Xa inhibitor", "کاریگەری لاوەکی": "خوێنبەربوون", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "بەربەستەری فاکتۆر Xa", "بۆچی": "بۆ مەبەست", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."},
        "ئیدۆکسابان": {"ڕێژە": "30-60mg", "میکانیزم": "Factor Xa inhibitor", "کاریگەری لاوەکی": "خوێنبەربوون", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "بەربەستەری فاکتۆر Xa", "بۆچی": "بۆ مەبەست", "تێبینی": "تێبینی تایبەتی خۆت لێرە بنووسە..."}
    }
}

# ================================
# 7. دروستکردنی ١٠٠٠ کویز (بە ئاست)
# ================================
def generate_quizzes_by_level():
    quizzes = []
    
    level1_questions = [
        {"پرسیار": "نیشانەی سەرەکی شەکرەی جۆری ٢ چییە؟", "هەڵبژاردەکان": ["تینوویەتی زۆر", "سەرئێشە", "ئازاری سنگ", "کۆخە"], "وەڵامی ڕاست": 0},
        {"پرسیار": "پەستانی خوێنی نۆرماڵ چەندە؟", "هەڵبژاردەکان": ["120/80", "140/90", "160/100", "180/110"], "وەڵامی ڕاست": 0},
        {"پرسیار": "کام دەرمانە بۆ شەکرە بەکاردێت؟", "هەڵبژاردەکان": ["مێتفۆرمین", "ئەسپیرین", "کاپتۆپریل", "ئەمۆکسیسیلین"], "وەڵامی ڕاست": 0},
        {"پرسیار": "نیشانەی ئەنیمیا چییە؟", "هەڵبژاردەکان": ["ماندوویی", "سەرئێشە", "ئازاری سنگ", "کۆخە"], "وەڵامی ڕاست": 0},
        {"پرسیار": "کام پشکنینە بۆ دەستنیشانکردنی شەکرە؟", "هەڵبژاردەکان": ["FBS", "ECG", "Chest X-ray", "MRI"], "وەڵامی ڕاست": 0},
        {"پرسیار": "نیشانەی پەستانی خوێن چییە؟", "هەڵبژاردەکان": ["سەرئێشە", "کۆخە", "تا", "سکچوون"], "وەڵامی ڕاست": 0},
        {"پرسیار": "کام دەرمانە بۆ ئازار بەکاردێت؟", "هەڵبژاردەکان": ["ئەسپیرین", "مێتفۆرمین", "ئەنسولین", "کاپتۆپریل"], "وەڵامی ڕاست": 0},
        {"پرسیار": "نیشانەی هەوکردنی سی چییە؟", "هەڵبژاردەکان": ["تا و کۆخە", "سەرئێشە", "ئازاری سنگ", "ماندوویی"], "وەڵامی ڕاست": 0},
        {"پرسیار": "Hb نزم نیشانەی چییە؟", "هەڵبژاردەکان": ["ئەنیمیا", "شەکرە", "نەخۆشی دڵ", "هەوکردن"], "وەڵامی ڕاست": 0},
        {"پرسیار": "کام دەرمانە بۆ پەستانی خوێن؟", "هەڵبژاردەکان": ["کاپتۆپریل", "مێتفۆرمین", "ئەنسولین", "ئەمۆکسیسیلین"], "وەڵامی ڕاست": 0},
        {"پرسیار": "نیشانەی نەخۆشی گەدە چییە؟", "هەڵبژاردەکان": ["ئازاری گەدە", "سەرئێشە", "ئازاری سنگ", "کۆخە"], "وەڵامی ڕاست": 0},
        {"پرسیار": "کام پشکنینە بۆ پەستانی خوێن؟", "هەڵبژاردەکان": ["BP", "FBS", "HbA1c", "CBC"], "وەڵامی ڕاست": 0},
        {"پرسیار": "نیشانەی نەخۆشی دڵ چییە؟", "هەڵبژاردەکان": ["ئازاری سنگ", "تینوویەتی زۆر", "سکچوون", "کۆخە"], "وەڵامی ڕاست": 0},
        {"پرسیار": "کام دەرمانە بۆ ئەنیمیا؟", "هەڵبژاردەکان": ["فێروس سولفەیت", "ئەسپیرین", "کاپتۆپریل", "مێتفۆرمین"], "وەڵامی ڕاست": 0},
        {"پرسیار": "CRP بەرز نیشانەی چییە؟", "هەڵبژاردەکان": ["هەوکردن", "شەکرە", "ئەنیمیا", "نەخۆشی دڵ"], "وەڵامی ڕاست": 0},
        {"پرسیار": "کام دەرمانە بۆ کۆخە؟", "هەڵبژاردەکان": ["سالبوتامۆل", "مێتفۆرمین", "کاپتۆپریل", "ئەسپیرین"], "وەڵامی ڕاست": 0},
        {"پرسیار": "نیشانەی سیل چییە؟", "هەڵبژاردەکان": ["کۆخەی خوێناوی", "سەرئێشە", "ئازاری سنگ", "سکچوون"], "وەڵامی ڕاست": 0},
        {"پرسیار": "کام پشکنینە بۆ دڵ؟", "هەڵبژاردەکان": ["ECG", "FBS", "HbA1c", "CBC"], "وەڵامی ڕاست": 0},
        {"پرسیار": "نیشانەی شەکرە چییە؟", "هەڵبژاردەکان": ["تینوویەتی زۆر", "سەرئێشە", "ئازاری سنگ", "کۆخە"], "وەڵامی ڕاست": 0},
        {"پرسیار": "کام دەرمانە بۆ هەوکردن؟", "هەڵبژاردەکان": ["ئەمۆکسیسیلین", "مێتفۆرمین", "کاپتۆپریل", "ئەسپیرین"], "وەڵامی ڕاست": 0}
    ]
    
    level2_questions = [
        {"پرسیار": "HbA1c > 6.5% ئاماژەیە بۆ چی؟", "هەڵبژاردەکان": ["شەکرە", "ئەنیمیا", "نەخۆشی دڵ", "هەوکردن"], "وەڵامی ڕاست": 0},
        {"پرسیار": "BP > 140/90 نیشانەی چییە؟", "هەڵبژاردەکان": ["پەستانی خوێن", "نەخۆشی دڵ", "شەکرە", "هەوکردن"], "وەڵامی ڕاست": 0},
        {"پرسیار": "MCV < 80 fL نیشانەی چییە؟", "هەڵبژاردەکان": ["ئەنیمیای مایکرۆسایتیک", "ئەنیمیای ماکرۆسایتیک", "ئەنیمیای نۆرمۆسایتیک", "هیمۆلایتیک"], "وەڵامی ڕاست": 0},
        {"پرسیار": "Troponin بەرز نیشانەی چییە؟", "هەڵبژاردەکان": ["نەخۆشی دڵ", "شەکرە", "هەوکردن", "ئەنیمیا"], "وەڵامی ڕاست": 0},
        {"پرسیار": "Creatinine بەرز نیشانەی چییە؟", "هەڵبژاردەکان": ["نەخۆشی گورچیلە", "نەخۆشی جگەر", "نەخۆشی دڵ", "شەکرە"], "وەڵامی ڕاست": 0},
        {"پرسیار": "ALT بەرز نیشانەی چییە؟", "هەڵبژاردەکان": ["نەخۆشی جگەر", "نەخۆشی گورچیلە", "نەخۆشی دڵ", "شەکرە"], "وەڵامی ڕاست": 0},
        {"پرسیار": "Ferritin نزم نیشانەی چییە؟", "هەڵبژاردەکان": ["ئەنیمیای کەمخوێنی ئاسن", "ئەنیمیای ماکرۆسایتیک", "هیمۆلایتیک", "شەکرە"], "وەڵامی ڕاست": 0},
        {"پرسیار": "C-peptide نزم لە شەکرەی جۆری چی؟", "هەڵبژاردەکان": ["جۆری 1", "جۆری 2", "حەملی دووگانی", "پێش شەکرە"], "وەڵامی ڕاست": 0},
        {"پرسیار": "FEV1 < 80% نیشانەی چییە؟", "هەڵبژاردەکان": ["نەخۆشی کۆکە", "نەخۆشی دڵ", "شەکرە", "هەوکردن"], "وەڵامی ڕاست": 0},
        {"پرسیار": "BNP بەرز نیشانەی چییە؟", "هەڵبژاردەکان": ["نەخۆشی دڵی شکان", "نەخۆشی گورچیلە", "شەکرە", "هەوکردن"], "وەڵامی ڕاست": 0},
        {"پرسیار": "Anti-GAD positive نیشانەی چییە؟", "هەڵبژاردەکان": ["شەکرەی جۆری 1", "شەکرەی جۆری 2", "نەخۆشی دڵ", "هەوکردن"], "وەڵامی ڕاست": 0},
        {"پرسیار": "eGFR < 60 نیشانەی چییە؟", "هەڵبژاردەکان": ["نەخۆشی گورچیلە", "نەخۆشی جگەر", "نەخۆشی دڵ", "شەکرە"], "وەڵامی ڕاست": 0},
        {"پرسیار": "HBsAg positive نیشانەی چییە؟", "هەڵبژاردەکان": ["نەخۆشی جگەر B", "نەخۆشی جگەر C", "نەخۆشی جگەر A", "سیرۆسیس"], "وەڵامی ڕاست": 0},
        {"پرسیار": "Anti-HCV positive نیشانەی چییە؟", "هەڵبژاردەکان": ["نەخۆشی جگەر C", "نەخۆشی جگەر B", "نەخۆشی جگەر A", "سیرۆسیس"], "وەڵامی ڕاست": 0},
        {"پرسیار": "Amylase بەرز نیشانەی چییە؟", "هەڵبژاردەکان": ["پەنکریاتیت", "نەخۆشی جگەر", "نەخۆشی گورچیلە", "شەکرە"], "وەڵامی ڕاست": 0},
        {"پرسیار": "Lipase بەرز نیشانەی چییە؟", "هەڵبژاردەکان": ["پەنکریاتیت", "نەخۆشی جگەر", "نەخۆشی گورچیلە", "شەکرە"], "وەڵامی ڕاست": 0},
        {"پرسیار": "وەڵامی ڕاست بۆ کویزی ئاست ٢ چییە؟", "هەڵبژاردەکان": ["ئاست ٢", "ئاست ١", "ئاست ٣", "ئاست ٤"], "وەڵامی ڕاست": 0},
        {"پرسیار": "کام دەرمانە بۆ MS؟", "هەڵبژاردەکان": ["Interferon", "Levodopa", "Donepezil", "Warfarin"], "وەڵامی ڕاست": 0},
        {"پرسیار": "نیشانەی Stroke چییە؟", "هەڵبژاردەکان": ["مشکێتی جوڵە", "بیرچون", "لەرزین", "ئازاری سنگ"], "وەڵامی ڕاست": 0},
        {"پرسیار": "کام پشکنینە بۆ نەخۆشی جگەر؟", "هەڵبژاردەکان": ["ALT", "Troponin", "CBC", "ESR"], "وەڵامی ڕاست": 0}
    ]
    
    level3_questions = [
        {"پرسیار": "ST depression + Troponin elevated نیشانەی چییە؟", "هەڵبژاردەکان": ["نەخۆشی دڵی ئیسکیمیک", "شەکرە", "هەوکردن", "ئەنیمیا"], "وەڵامی ڕاست": 0},
        {"پرسیار": "Oligoclonal bands لە CSF نیشانەی چییە؟", "هەڵبژاردەکان": ["MS", "Alzheimer", "Parkinson", "Stroke"], "وەڵامی ڕاست": 0},
        {"پرسیار": "CAG تەنگی کرۆنەری نیشانەی چییە؟", "هەڵبژاردەکان": ["نەخۆشی دڵ", "شەکرە", "هەوکردن", "ئەنیمیا"], "وەڵامی ڕاست": 0},
        {"پرسیار": "AFP بەرز > 400 نیشانەی چییە؟", "هەڵبژاردەکان": ["نەخۆشی جگەر", "نەخۆشی گورچیلە", "شەکرە", "هەوکردن"], "وەڵامی ڕاست": 0},
        {"پرسیار": "DAT scan کەم نیشانەی چییە؟", "هەڵبژاردەکان": ["Parkinson", "Alzheimer", "MS", "Stroke"], "وەڵامی ڕاست": 0},
        {"پرسیار": "PET abnormal نیشانەی چییە؟", "هەڵبژاردەکان": ["Alzheimer", "Parkinson", "MS", "Stroke"], "وەڵامی ڕاست": 0},
        {"پرسیار": "VEP کەم نیشانەی چییە؟", "هەڵبژاردەکان": ["MS", "Alzheimer", "Parkinson", "Stroke"], "وەڵامی ڕاست": 0},
        {"پرسیار": "Sputum AFB positive نیشانەی چییە؟", "هەڵبژاردەکان": ["سیل", "هەوکردنی سی", "شەکرە", "نەخۆشی دڵ"], "وەڵامی ڕاست": 0},
        {"پرسیار": "Ultrasound fatty liver نیشانەی چییە؟", "هەڵبژاردەکان": ["نەخۆشی جگەری چەور", "سیرۆسیس", "نەخۆشی جگەر B", "نەخۆشی جگەر C"], "وەڵامی ڕاست": 0},
        {"پرسیار": "MRI atrophy نیشانەی چییە؟", "هەڵبژاردەکان": ["Alzheimer", "Parkinson", "MS", "Stroke"], "وەڵامی ڕاست": 0},
        {"پرسیار": "CT ischemia نیشانەی چییە؟", "هەڵبژاردەکان": ["Stroke", "MS", "Alzheimer", "Parkinson"], "وەڵامی ڕاست": 0},
        {"پرسیار": "Holter abnormal نیشانەی چییە؟", "هەڵبژاردەکان": ["Arrhythmia", "نەخۆشی دڵ", "شەکرە", "هەوکردن"], "وەڵامی ڕاست": 0},
        {"پرسیار": "Echocardiogram EF < 40% نیشانەی چییە؟", "هەڵبژاردەکان": ["نەخۆشی دڵی شکان", "نەخۆشی دڵی ئیسکیمیک", "شەکرە", "هەوکردن"], "وەڵامی ڕاست": 0},
        {"پرسیار": "Chest X-ray consolidation نیشانەی چییە؟", "هەڵبژاردەکان": ["هەوکردنی سی", "سیل", "نەخۆشی دڵ", "شەکرە"], "وەڵامی ڕاست": 0},
        {"پرسیار": "Widal positive نیشانەی چییە؟", "هەڵبژاردەکان": ["تایفیید", "کۆلێرا", "سیل", "هەوکردن"], "وەڵامی ڕاست": 0},
        {"پرسیار": "Stool culture Vibrio cholera نیشانەی چییە؟", "هەڵبژاردەکان": ["کۆلێرا", "تایفیید", "هەوکردن", "سکچوون"], "وەڵامی ڕاست": 0},
        {"پرسیار": "CT scan tumor نیشانەی چییە؟", "هەڵبژاردەکان": ["نەخۆشی جگەر", "نەخۆشی گورچیلە", "شەکرە", "هەوکردن"], "وەڵامی ڕاست": 0},
        {"پرسیار": "Biopsy malignant نیشانەی چییە؟", "هەڵبژاردەکان": ["نەخۆشی جگەر", "نەخۆشی گورچیلە", "شەکرە", "هەوکردن"], "وەڵامی ڕاست": 0},
        {"پرسیار": "Endoscopy ulcer نیشانەی چییە؟", "هەڵبژاردەکان": ["نەخۆشی گەدە", "هەوکردنی گەدە", "شەکرە", "نەخۆشی دڵ"], "وەڵامی ڕاست": 0},
        {"پرسیار": "H. pylori positive نیشانەی چییە؟", "هەڵبژاردەکان": ["نەخۆشی گەدە", "هەوکردنی گەدە", "شەکرە", "نەخۆشی دڵ"], "وەڵامی ڕاست": 0}
    ]
    
    level4_questions = [
        {"پرسیار": "CA19-9 بەرز نیشانەی چییە؟", "هەڵبژاردەکان": ["نەخۆشی پەنکریاس", "نەخۆشی جگەر", "نەخۆشی گورچیلە", "شەکرە"], "وەڵامی ڕاست": 0},
        {"پرسیار": "PSA بەرز نیشانەی چییە؟", "هەڵبژاردەکان": ["نەخۆشی پڕۆستات", "نەخۆشی گورچیلە", "شەکرە", "هەوکردن"], "وەڵامی ڕاست": 0},
        {"پرسیار": "CA125 بەرز نیشانەی چییە؟", "هەڵبژاردەکان": ["نەخۆشی هێلکەدان", "نەخۆشی جگەر", "نەخۆشی گورچیلە", "شەکرە"], "وەڵامی ڕاست": 0},
        {"پرسیار": "AFP بەرز نیشانەی چییە؟", "هەڵبژاردەکان": ["نەخۆشی جگەر", "نەخۆشی گورچیلە", "شەکرە", "هەوکردن"], "وەڵامی ڕاست": 0},
        {"پرسیار": "CEA بەرز نیشانەی چییە؟", "هەڵبژاردەکان": ["نەخۆشی کۆلۆن", "نەخۆشی جگەر", "نەخۆشی گورچیلە", "شەکرە"], "وەڵامی ڕاست": 0},
        {"پرسیار": "HCG بەرز نیشانەی چییە؟", "هەڵبژاردەکان": ["حەمل", "نەخۆشی جگەر", "نەخۆشی گورچیلە", "شەکرە"], "وەڵامی ڕاست": 0},
        {"پرسیار": "LDH بەرز نیشانەی چییە؟", "هەڵبژاردەکان": ["هیمۆلایسیس", "نەخۆشی جگەر", "نەخۆشی گورچیلە", "شەکرە"], "وەڵامی ڕاست": 0},
        {"پرسیار": "Haptoglobin نزم نیشانەی چییە؟", "هەڵبژاردەکان": ["هیمۆلایسیس", "نەخۆشی جگەر", "نەخۆشی گورچیلە", "شەکرە"], "وەڵامی ڕاست": 0},
        {"پرسیار": "Reticulocyte بەرز نیشانەی چییە؟", "هەڵبژاردەکان": ["هیمۆلایسیس", "نەخۆشی جگەر", "نەخۆشی گورچیلە", "شەکرە"], "وەڵامی ڕاست": 0},
        {"پرسیار": "Coomb's test positive نیشانەی چییە؟", "هەڵبژاردەکان": ["هیمۆلایسیس خۆئەگەر", "نەخۆشی جگەر", "نەخۆشی گورچیلە", "شەکرە"], "وەڵامی ڕاست": 0},
        {"پرسیار": "Bone marrow blast cells نیشانەی چییە؟", "هەڵبژاردەکان": ["لەوسیمیا", "نەخۆشی جگەر", "نەخۆشی گورچیلە", "شەکرە"], "وەڵامی ڕاست": 0},
        {"پرسیار": "Lymph node biopsy malignant نیشانەی چییە؟", "هەڵبژاردەکان": ["لەوسیمیا", "نەخۆشی جگەر", "نەخۆشی گورچیلە", "شەکرە"], "وەڵامی ڕاست": 0},
        {"پرسیار": "Platelets < 50 نیشانەی چییە؟", "هەڵبژاردەکان": ["ترۆمبۆسایتۆپینیا", "لەوسیمیا", "نەخۆشی جگەر", "شەکرە"], "وەڵامی ڕاست": 0},
        {"پرسیار": "PTT درێژ نیشانەی چییە؟", "هەڵبژاردەکان": ["هیمۆفیلیا", "نەخۆشی جگەر", "نەخۆشی گورچیلە", "شەکرە"], "وەڵامی ڕاست": 0},
        {"پرسیار": "Factor VIII نزم نیشانەی چییە؟", "هەڵبژاردەکان": ["هیمۆفیلیا A", "هیمۆفیلیا B", "نەخۆشی جگەر", "شەکرە"], "وەڵامی ڕاست": 0},
        {"پرسیار": "Factor IX نزم نیشانەی چییە؟", "هەڵبژاردەکان": ["هیمۆفیلیا B", "هیمۆفیلیا A", "نەخۆشی جگەر", "شەکرە"], "وەڵامی ڕاست": 0},
        {"پرسیار": "Urine protein > 3.5g نیشانەی چییە؟", "هەڵبژاردەکان": ["نەخۆشی گورچیلە", "نەخۆشی جگەر", "شەکرە", "هەوکردن"], "وەڵامی ڕاست": 0},
        {"پرسیار": "Urine casts نیشانەی چییە؟", "هەڵبژاردەکان": ["نەخۆشی گورچیلە", "نەخۆشی جگەر", "شەکرە", "هەوکردن"], "وەڵامی ڕاست": 0},
        {"پرسیار": "Complement نزم نیشانەی چییە؟", "هەڵبژاردەکان": ["نەخۆشی گورچیلە", "نەخۆشی جگەر", "شەکرە", "هەوکردن"], "وەڵامی ڕاست": 0},
        {"پرسیار": "Water deprivation test positive نیشانەی چییە؟", "هەڵبژاردەکان": ["نەخۆشی میزی شەکر", "شەکرە", "نەخۆشی گورچیلە", "هەوکردن"], "وەڵامی ڕاست": 0}
    ]
    
    level5_questions = [
        {"پرسیار": "CAG تەنگی کرۆنەری نیشانەی چییە؟", "هەڵبژاردەکان": ["نەخۆشی دڵی ئیسکیمیک", "شەکرە", "هەوکردن", "ئەنیمیا"], "وەڵامی ڕاست": 0},
        {"پرسیار": "Oligoclonal bands لە CSF نیشانەی چییە؟", "هەڵبژاردەکان": ["MS", "Alzheimer", "Parkinson", "Stroke"], "وەڵامی ڕاست": 0},
        {"پرسیار": "کام دەرمانە بۆ Hep C؟", "هەڵبژاردەکان": ["Sofosbuvir", "Rifampicin", "Levodopa", "Warfarin"], "وەڵامی ڕاست": 0},
        {"پرسیار": "نیشانەی نەخۆشی گەدە چییە؟", "هەڵبژاردەکان": ["ئازاری گەدە", "سەرئێشە", "ئازاری سنگ", "کۆخە"], "وەڵامی ڕاست": 0},
        {"پرسیار": "کام پشکنینە بۆ پەنکریاتیت؟", "هەڵبژاردەکان": ["Amylase", "ALT", "Troponin", "CRP"], "وەڵامی ڕاست": 0},
        {"پرسیار": "MRI plagues نیشانەی چییە؟", "هەڵبژاردەکان": ["MS", "Alzheimer", "Parkinson", "Stroke"], "وەڵامی ڕاست": 0},
        {"پرسیار": "DAT scan کەم نیشانەی چییە؟", "هەڵبژاردەکان": ["Parkinson", "Alzheimer", "MS", "Stroke"], "وەڵامی ڕاست": 0},
        {"پرسیار": "PET abnormal نیشانەی چییە؟", "هەڵبژاردەکان": ["Alzheimer", "Parkinson", "MS", "Stroke"], "وەڵامی ڕاست": 0},
        {"پرسیار": "VEP کەم نیشانەی چییە؟", "هەڵبژاردەکان": ["MS", "Alzheimer", "Parkinson", "Stroke"], "وەڵامی ڕاست": 0},
        {"پرسیار": "Sputum AFB positive نیشانەی چییە؟", "هەڵبژاردەکان": ["سیل", "هەوکردنی سی", "شەکرە", "نەخۆشی دڵ"], "وەڵامی ڕاست": 0},
        {"پرسیار": "Ultrasound cirrhosis نیشانەی چییە؟", "هەڵبژاردەکان": ["سیرۆسیس", "نەخۆشی جگەری چەور", "نەخۆشی جگەر B", "نەخۆشی جگەر C"], "وەڵامی ڕاست": 0},
        {"پرسیار": "MRI atrophy نیشانەی چییە؟", "هەڵبژاردەکان": ["Alzheimer", "Parkinson", "MS", "Stroke"], "وەڵامی ڕاست": 0},
        {"پرسیار": "CT stroke نیشانەی چییە؟", "هەڵبژاردەکان": ["Stroke", "MS", "Alzheimer", "Parkinson"], "وەڵامی ڕاست": 0},
        {"پرسیار": "Holter abnormal نیشانەی چییە؟", "هەڵبژاردەکان": ["Arrhythmia", "نەخۆشی دڵ", "شەکرە", "هەوکردن"], "وەڵامی ڕاست": 0},
        {"پرسیار": "Echocardiogram EF < 40% نیشانەی چییە؟", "هەڵبژاردەکان": ["نەخۆشی دڵی شکان", "نەخۆشی دڵی ئیسکیمیک", "شەکرە", "هەوکردن"], "وەڵامی ڕاست": 0},
        {"پرسیار": "Chest X-ray consolidation نیشانەی چییە؟", "هەڵبژاردەکان": ["هەوکردنی سی", "سیل", "نەخۆشی دڵ", "شەکرە"], "وەڵامی ڕاست": 0},
        {"پرسیار": "Widal positive نیشانەی چییە؟", "هەڵبژاردەکان": ["تایفیید", "کۆلێرا", "سیل", "هەوکردن"], "وەڵامی ڕاست": 0},
        {"پرسیار": "Stool culture Vibrio cholera نیشانەی چییە؟", "هەڵبژاردەکان": ["کۆلێرا", "تایفیید", "هەوکردن", "سکچوون"], "وەڵامی ڕاست": 0},
        {"پرسیار": "CT scan tumor نیشانەی چییە؟", "هەڵبژاردەکان": ["نەخۆشی جگەر", "نەخۆشی گورچیلە", "شەکرە", "هەوکردن"], "وەڵامی ڕاست": 0},
        {"پرسیار": "Biopsy malignant نیشانەی چییە؟", "هەڵبژاردەکان": ["نەخۆشی جگەر", "نەخۆشی گورچیلە", "شەکرە", "هەوکردن"], "وەڵامی ڕاست": 0}
    ]
    
    level_questions = {
        1: level1_questions,
        2: level2_questions,
        3: level3_questions,
        4: level4_questions,
        5: level5_questions
    }
    
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

def analyze_symptoms_advanced(symptoms: List[str], disease: str) -> Dict:
    disease_symptoms = set(DISEASE_DATABASE[disease]['نیشانەکان'])
    patient_symptoms = set(symptoms)
    match_count = len(patient_symptoms.intersection(disease_symptoms))
    total_disease_symptoms = len(disease_symptoms)
    total_patient_symptoms = len(patient_symptoms)
    match_percentage = (match_count / total_disease_symptoms) * 100 if total_disease_symptoms > 0 else 0
    coverage_percentage = (match_count / total_patient_symptoms) * 100 if total_patient_symptoms > 0 else 0
    return {
        "match_count": match_count,
        "total_disease_symptoms": total_disease_symptoms,
        "total_patient_symptoms": total_patient_symptoms,
        "match_percentage": round(match_percentage, 1),
        "coverage_percentage": round(coverage_percentage, 1),
        "match_quality": "باش" if match_percentage > 60 else "مامناوەند" if match_percentage > 30 else "کەم",
        "matched_symptoms": list(patient_symptoms.intersection(disease_symptoms)),
        "unmatched_disease_symptoms": list(disease_symptoms.difference(patient_symptoms)),
        "unmatched_patient_symptoms": list(patient_symptoms.difference(disease_symptoms))
    }

def get_student_level_score(level: str) -> int:
    levels = {"ساڵی یەکەم": 10, "ساڵی دووەم": 25, "ساڵی سێیەم": 40, "ساڵی چوارەم": 60, "ساڵی پێنجەم": 75, "ساڵی شەشەم": 90}
    return levels.get(level, 10)

def get_risk_color(risk_level: str) -> str:
    colors = {"زۆر مەترسیدار": "#ff6b6b", "مەترسیدار": "#ffd93d", "مامناوەند": "#ffc107", "کەم": "#6bcb77"}
    return colors.get(risk_level, "#6c757d")

def get_age_group(age: int) -> str:
    if age < 18: return "منداڵ"
    elif age < 40: return "گەنج"
    elif age < 60: return "تەمەن مامناوەند"
    else: return "پیر"

def generate_random_lab_results() -> Dict:
    results = {}
    for test, info in LAB_TESTS.items():
        low, high = info["نۆرماڵ"]
        if random.random() < 0.7:
            value = round(random.uniform(low, high), 2)
            status = "نۆرماڵ"
        else:
            if random.random() < 0.5:
                value = round(random.uniform(high, high * 1.5), 2)
                status = "بەرز"
            else:
                value = round(random.uniform(low * 0.5, low), 2)
                status = "نزم"
        results[test] = {"value": value, "status": status, "unit": info["یەکە"]}
    return results

def calculate_case_similarity(case1: Dict, case2: Dict) -> float:
    similarities = []
    if abs(case1.get('تەمەن', 0) - case2.get('تەمەن', 0)) < 10:
        similarities.append(1)
    else:
        similarities.append(0)
    if case1.get('ڕەگەز') == case2.get('ڕەگەز'):
        similarities.append(1)
    symptoms1 = set(case1.get('نیشانە سەرەکییەکان', []))
    symptoms2 = set(case2.get('نیشانە سەرەکییەکان', []))
    if symptoms1 and symptoms2:
        intersection = len(symptoms1.intersection(symptoms2))
        union = len(symptoms1.union(symptoms2))
        similarities.append(intersection / union if union > 0 else 0)
    return sum(similarities) / len(similarities) if similarities else 0

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

def get_quizzes_for_level(level: int) -> List:
    return [q for q in MEDICAL_QUIZZES if q.get("ئاست", 1) == level]

def get_quiz_progress(level: int) -> float:
    total = LEVELS[level]["quizzes"]
    done = st.session_state.get(f"level_{level}_done", 0)
    return (done / total) * 100 if total > 0 else 0

def get_next_quiz(level: int) -> Optional[Dict]:
    quizzes = get_quizzes_for_level(level)
    done = st.session_state.get(f"level_{level}_done", 0)
    if done < len(quizzes):
        return quizzes[done]
    return None

def analyze_lab_result(test_name: str, value: float) -> Dict:
    if test_name not in LAB_TESTS:
        return {"status": "نەزانراو", "color": "#6c757d", "interpretation": "پشکنین نەدۆزرایەوە"}
    low, high = LAB_TESTS[test_name]["نۆرماڵ"]
    if value < low:
        return {"status": "نزم", "color": "#ffc107", "interpretation": f"{LAB_TESTS[test_name]['تەفسیر']} نزمە (نزمتر لە نۆرماڵ)"}
    elif value > high:
        return {"status": "بەرز", "color": "#dc3545", "interpretation": f"{LAB_TESTS[test_name]['تەفسیر']} بەرزە (بەرزتر لە نۆرماڵ)"}
    else:
        return {"status": "نۆرماڵ", "color": "#28a745", "interpretation": f"{LAB_TESTS[test_name]['تەفسیر']} نۆرماڵە (لە مەودای نۆرماڵدایە)"}

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
            test_keys = list(info['پشکنینەکان'].keys())
            selected_tests = random.sample(test_keys, min(4, len(test_keys)))
            lab_results = generate_random_lab_results()
            case = {
                'case_id': f"CASE-{case_id_counter:04d}",
                'تەمەن': age,
                'ڕەگەز': gender,
                'نیشانە سەرەکییەکان': symptoms,
                'پشکنینە پێویستەکان': selected_tests,
                'ئەنجامی پشکنینەکان': lab_results,
                'دەستنیشانکردن': disease,
                'ئاستی مەترسی': info['ئاستی مەترسی'],
                'نمرەی مەترسی': calculate_risk_score(disease, age, gender, symptoms),
                'case_date': datetime.now() - timedelta(days=random.randint(0, 730)),
                'دەستنیشانکردنی دوایین': disease
            }
            cases.append(case)
            case_id_counter += 1
    return pd.DataFrame(cases)

training_data = generate_training_data()

# ================================
# 10. مۆدێلی AI پێشکەوتوو
# ================================
@st.cache_resource
def train_prediction_model_advanced():
    try:
        data = training_data.copy()
        data['گروپی تەمەن'] = data['تەمەن'].apply(get_age_group)
        features = pd.get_dummies(data[['تەمەن', 'ڕەگەز', 'گروپی تەمەن'] + ['نیشانە سەرەکییەکان']], drop_first=True)
        scaler = StandardScaler()
        numerical_cols = features.select_dtypes(include=[np.number]).columns
        features_scaled = scaler.fit_transform(features[numerical_cols])
        model = RandomForestClassifier(n_estimators=250, max_depth=15, min_samples_split=5, min_samples_leaf=2, random_state=42)
        model.fit(features_scaled, data['دەستنیشانکردن'])
        predictions = model.predict(features_scaled)
        accuracy = accuracy_score(data['دەستنیشانکردن'], predictions)
        pca = PCA(n_components=2)
        pca_result = pca.fit_transform(features_scaled)
        return model, scaler, accuracy, numerical_cols, pca, pca_result
    except Exception as e:
        return None, None, 0, None, None, None

model, scaler, model_accuracy, numerical_cols, pca_model, pca_result = train_prediction_model_advanced()

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
if 'favorite_diseases' not in st.session_state:
    st.session_state.favorite_diseases = []
if 'study_notes' not in st.session_state:
    st.session_state.study_notes = ""
if 'study_time' not in st.session_state:
    st.session_state.study_time = 0
if 'quiz_attempts' not in st.session_state:
    st.session_state.quiz_attempts = 0
if 'simulation_count' not in st.session_state:
    st.session_state.simulation_count = 0
if 'current_level' not in st.session_state:
    st.session_state.current_level = 1
if 'level_1_done' not in st.session_state:
    st.session_state.level_1_done = 0
if 'level_2_done' not in st.session_state:
    st.session_state.level_2_done = 0
if 'level_3_done' not in st.session_state:
    st.session_state.level_3_done = 0
if 'level_4_done' not in st.session_state:
    st.session_state.level_4_done = 0
if 'level_5_done' not in st.session_state:
    st.session_state.level_5_done = 0
if 'lab_history' not in st.session_state:
    st.session_state.lab_history = []
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
        <h2 style="color:#0984e3;margin-bottom:20px;">Dr.Danyal</h2>
        <p style="color:#636e72;">تکایە بچۆ ژوورەوە یان هەژمارێکی نوێ دروست بکە</p>
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
                        st.success("✅ هەژمارەکەت بە سەرکەوتوویی دروست کرا! ئێستا دەتوانیت بچیتە ژوورەوە")
                    else:
                        st.error("❌ ئەم ناوی بەکارهێنەرییە پێشتر بەکارهێنراوە")
    
    st.markdown('</div></div>', unsafe_allow_html=True)
    st.stop()

# ================================
# 12. سایدبار - لەگەڵ لۆگۆی Dr.Danyal و دوگمەی چوونە دەرەوە
# ================================
with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center;padding:10px 0;">
        <span class="dr-icon">🩺</span>
        <div style="font-size:2rem;font-weight:bold;color:#0984e3;">
            Dr.Danyal
        </div>
        <div style="color:#636e72;font-size:0.8rem;margin-top:-5px;">🎓 ڕاهێنەری پزیشکی Pro Max</div>
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
    
    time_diff = datetime.now() - st.session_state.last_activity
    minutes = int(time_diff.total_seconds() / 60)
    if minutes > 60:
        st.markdown(f"🕐 دوایین چالاکی: {minutes//60} کاتژمێر پێش")
    else:
        st.markdown(f"🕐 دوایین چالاکی: {minutes} خولەک پێش")
    
    st.markdown("---")
    if st.button("🚪 چوونە دەرەوە", type="primary"):
        save_user_data(st.session_state.username, {
            "custom_lab_tests": st.session_state.custom_lab_tests,
            "custom_drugs": st.session_state.custom_drugs
        })
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.custom_lab_tests = {}
        st.session_state.custom_drugs = {}
        st.rerun()

# ================================
# خەزنکردنی خۆکارانەی داتا لە کاتی گۆڕانکاریدا
# ================================
def auto_save():
    if st.session_state.logged_in:
        save_user_data(st.session_state.username, {
            "custom_lab_tests": st.session_state.custom_lab_tests,
            "custom_drugs": st.session_state.custom_drugs
        })

# ================================
# 13. پەڕەی داشبۆرد
# ================================
if page == "🏠 داشبۆرد":
    st.markdown("""
    <div class="main">
        <div class="logo-container">
            <span class="logo-icon">🩺</span>
            <span class="logo-text">Dr.Danyal</span>
        </div>
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
    
    st.markdown("---")
    
    st.markdown(f"""
    <div class="case-card">
        <h3>{get_level_icon(level)} ئاستی ئێستا: {level_info['name']}</h3>
        <p>نمرەی کویز: {st.session_state.quiz_score}</p>
        <div class="progress-container">
            <div class="progress-fill" style="width:{get_level_progress(st.session_state.quiz_score)}%"></div>
        </div>
        <p>پێشکەوتن: {get_level_progress(st.session_state.quiz_score):.1f}%</p>
        <p>کویزەکانی ئەم ئاستە: {st.session_state.get(f'level_{level}_done', 0)}/{LEVELS[level]['quizzes']}</p>
        <p style="font-size:0.9rem;color:#888;">{level_info['description']}</p>
    </div>
    """, unsafe_allow_html=True)

# ================================
# 14. پەڕەی کویز (ئاستی)
# ================================
elif page == "📝 کویز (ئاستی)":
    st.markdown("""
    <div class="main">
        <h2>📝 کویزی پزیشکی - بەپێی ئاست</h2>
    </div>
    """, unsafe_allow_html=True)
    
    level = get_user_level(st.session_state.quiz_score)
    level_info = get_level_info(level)
    
    st.markdown("### 🎯 پێشکەوتنی ئاستەکان")
    cols = st.columns(5)
    for i in range(1, 6):
        with cols[i-1]:
            info = get_level_info(i)
            done = st.session_state.get(f'level_{i}_done', 0)
            total = info['quizzes']
            pct = (done / total) * 100 if total > 0 else 0
            is_current = i == level
            st.markdown(f"""
            <div class="stat-card" style="border-top-color: {info['color']}; {'transform: scale(1.05); box-shadow: 0 10px 30px rgba(102,126,234,0.3);' if is_current else ''}">
                <h4>{get_level_icon(i)} ئاست {i}</h4>
                <p style="font-size:0.9rem;">{info['name']}</p>
                <p>{done}/{total}</p>
                <div class="progress-container">
                    <div class="progress-fill" style="width:{pct}%;background:{info['color']};"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    if not st.session_state.quiz_completed:
        next_quiz = get_next_quiz(level)
        
        if next_quiz:
            st.markdown(f"""
            <div class="quiz-card">
                <h3>{next_quiz['پرسیار']}</h3>
                <p style="color: #888;font-size:0.9rem;">ئاست: {get_level_icon(level)} {next_quiz.get('ئاستی ناو', level_info['name'])}</p>
                <p style="color: #666;font-size:0.8rem;">پێشکەوتن: {st.session_state.get(f'level_{level}_done', 0)}/{LEVELS[level]['quizzes']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            answer = st.radio("وەڵام:", next_quiz['هەڵبژاردەکان'], key=f"q_{st.session_state.quiz_index}")
            
            if st.button("✅ پشتڕاستکردنەوە", type="primary"):
                selected = next_quiz['هەڵبژاردەکان'].index(answer)
                st.session_state.quiz_attempts += 1
                
                if selected == next_quiz['وەڵامی ڕاست']:
                    st.session_state.quiz_score += 1
                    st.success("🎉 ڕاستە! نمرەی زیادیکرد")
                    st.balloons()
                else:
                    st.error(f"❌ هەڵەیە. ڕاست: {next_quiz['هەڵبژاردەکان'][next_quiz['وەڵامی ڕاست']]}")
                
                st.info(f"📚 {next_quiz['ڕوونکردنەوە']}")
                st.session_state.quiz_answers.append({
                    'پرسیار': next_quiz['پرسیار'],
                    'وەڵام': answer,
                    'ڕاستە': selected == next_quiz['وەڵامی ڕاست']
                })
                
                st.session_state[f'level_{level}_done'] = st.session_state.get(f'level_{level}_done', 0) + 1
                st.session_state.study_time += 2
                st.session_state.last_activity = datetime.now()
                
                if datetime.now().date() > st.session_state.last_study_date:
                    st.session_state.streak_days += 1
                    st.session_state.last_study_date = datetime.now().date()
                
                if st.session_state.get(f'level_{level}_done', 0) >= LEVELS[level]['quizzes']:
                    next_level = get_next_level(level)
                    st.success(f"🎊 پیرۆز! تۆ ئاستی {level_info['name']} تەواو کردیت!")
                    if next_level <= 5:
                        st.info(f"🚀 بچۆ بۆ ئاستی {LEVELS[next_level]['name']}")
                        st.session_state.current_level = next_level
                        if f"تەواوکردنی ئاست {level}" not in st.session_state.achievements:
                            st.session_state.achievements.append(f"تەواوکردنی ئاست {level}")
                
                st.rerun()
        else:
            st.info("هیچ کویزێکی تر نییە بۆ ئەم ئاستە!")
            if level < 5:
                if st.button(f"🚀 بچۆ بۆ ئاستی {LEVELS[level+1]['name']}"):
                    st.session_state.current_level = level + 1
                    st.rerun()
            else:
                st.success("🎊 پیرۆز! تۆ هەموو ئاستەکانت تەواو کردیت! تۆ پزیشکێکی لێهاتووی!")
    else:
        st.markdown(f"""
        <div class="success-box">
            <h2>🎊 کویز تەواو بوو!</h2>
            <h3>نمرە: {st.session_state.quiz_score}/100</h3>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔄 کویزی نوێ"):
            st.session_state.quiz_completed = False
            st.session_state.quiz_index = 0
            st.rerun()

# ================================
# 15. پەڕەی تاقیگە (٢٠٠ پشکنین) - پشکنینەکان بە ناوی ئامێر و تێبینی
# ================================
elif page == "🔬 تاقیگە (٢٠٠)":
    st.markdown("""
    <div class="main">
        <h2>🔬 تاقیگەی ڤێرچواڵ - Dr.Danyal</h2>
        <p style="color:#aaa;">200+ پشکنینی تاقیگە لەگەڵ ئامێرەکان و شوێنی تێبینی تایبەتی خۆت</p>
    </div>
    """, unsafe_allow_html=True)
    
    groups = ["هەموو"] + sorted(set(test["گروپ"] for test in LAB_TESTS.values()))
    selected_group = st.selectbox("📂 پۆلێن:", groups)
    
    search_lab = st.text_input("🔍 گەڕان:", placeholder="ناوی پشکنین...")
    
    all_lab_tests = {**LAB_TESTS, **st.session_state.custom_lab_tests}
    st.markdown(f"**📊 ژمارەی پشکنینەکان:** {len([t for t in all_lab_tests if (selected_group == 'هەموو' or all_lab_tests[t].get('گروپ', '') == selected_group) and (not search_lab or search_lab.lower() in t.lower())])}")
    
    cols = st.columns(2)
    idx = 0
    
    for test_name, test_info in all_lab_tests.items():
        if selected_group != "هەموو" and test_info.get("گروپ", "") != selected_group:
            continue
        if search_lab and search_lab.lower() not in test_name.lower():
            continue
        
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
    
    st.markdown("---")
    st.markdown("### 🧪 شیکاری پشکنین (نرخەکەت پێوەر بکە لەگەڵ نۆرماڵ)")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        test_to_analyze = st.selectbox("پشکنین هەڵبژێرە:", list(all_lab_tests.keys()))
        test_value = st.number_input("نرخ:", value=0.0, step=0.1)
    
    with col2:
        if test_to_analyze and test_value:
            result = analyze_lab_result(test_to_analyze, test_value)
            low, high = all_lab_tests[test_to_analyze].get("نۆرماڵ", (0, 0))
            note = all_lab_tests[test_to_analyze].get("تێبینی", "تێبینی تایبەتی خۆت لێرە بنووسە...")
            st.markdown(f"""
            <div class="lab-result-card lab-{result['status']}">
                <h4>{test_to_analyze}</h4>
                <p><strong>نرخ:</strong> {test_value} {all_lab_tests[test_to_analyze].get('یەکە', '')}</p>
                <p><strong>نۆرماڵ:</strong> {low} - {high}</p>
                <p><strong>دۆخ:</strong> <span style="color:{result['color']}">{result['status']}</span></p>
                <p><strong>تەفسیر:</strong> {result['interpretation']}</p>
                <p style="color:#aaa;font-size:0.8rem;"><strong>ئامێر:</strong> {all_lab_tests[test_to_analyze].get('ئامێر', 'نەزانراو')}</p>
                <p style="color:#aaa;font-size:0.8rem;background:rgba(255,255,255,0.
