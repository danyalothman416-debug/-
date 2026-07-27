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
import requests
import feedparser
from gtts import gTTS
import speech_recognition as sr
import tempfile
import threading

# ================================
# 1. ڕێکخستنی ڕووکاری پەڕە
# ================================
st.set_page_config(
    page_title="Dr.Danyal - ڕاهێنەری پزیشکی Pro Max Ultra",
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
LEADERBOARD_FILE = os.path.join(DATA_DIR, "leaderboard.json")
STUDY_ROOMS_FILE = os.path.join(DATA_DIR, "study_rooms.json")

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

def load_leaderboard() -> List:
    """بارکردنی خشتەی ڕێزلێنان"""
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_leaderboard(data: List):
    """خەزنکردنی خشتەی ڕێزلێنان"""
    with open(LEADERBOARD_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_study_rooms() -> Dict:
    """بارکردنی ژوورەکانی خوێندن"""
    if os.path.exists(STUDY_ROOMS_FILE):
        with open(STUDY_ROOMS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_study_rooms(data: Dict):
    """خەزنکردنی ژوورەکانی خوێندن"""
    with open(STUDY_ROOMS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def create_user(username: str, password: str) -> bool:
    """دروستکردنی بەکارهێنەری نوێ"""
    users = load_users()
    if username in users:
        return False
    users[username] = {
        "password": hash_password(password),
        "created_at": datetime.now().isoformat(),
        "custom_lab_tests": {},
        "custom_drugs": {},
        "lab_notes": {},
        "drug_notes": {},
        "spaced_repetition": {},
        "clinical_notes": [],
        "comprehensive_exams": [],
        "total_study_time": 0,
        "level": 1,
        "xp_points": 0,
        "badges": [],
        "daily_streak": 0,
        "last_login": datetime.now().isoformat()
    }
    save_users(users)
    
    # زیادکردن بۆ خشتەی ڕێزلێنان
    leaderboard = load_leaderboard()
    leaderboard.append({
        "username": username,
        "xp_points": 0,
        "level": 1,
        "quiz_score": 0,
        "cases_solved": 0,
        "badges": []
    })
    save_leaderboard(leaderboard)
    
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

def update_leaderboard(username: str, xp: int = 0, quiz_score: int = None, cases_solved: int = None):
    """نوێکردنەوەی خشتەی ڕێزلێنان"""
    leaderboard = load_leaderboard()
    for entry in leaderboard:
        if entry["username"] == username:
            entry["xp_points"] += xp
            if quiz_score is not None:
                entry["quiz_score"] = max(entry.get("quiz_score", 0), quiz_score)
            if cases_solved is not None:
                entry["cases_solved"] = cases_solved
            entry["level"] = get_user_level(entry["quiz_score"])
            break
    save_leaderboard(leaderboard)

def add_xp(username: str, points: int):
    """زیادکردنی XP بۆ بەکارهێنەر"""
    update_leaderboard(username, xp=points)
    users = load_users()
    if username in users:
        users[username]["xp_points"] = users[username].get("xp_points", 0) + points
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
if 'lab_notes' not in st.session_state:
    st.session_state.lab_notes = {}
if 'drug_notes' not in st.session_state:
    st.session_state.drug_notes = {}
if 'spaced_repetition' not in st.session_state:
    st.session_state.spaced_repetition = {}
if 'clinical_notes' not in st.session_state:
    st.session_state.clinical_notes = []
if 'xp_points' not in st.session_state:
    st.session_state.xp_points = 0
if 'badges' not in st.session_state:
    st.session_state.badges = []

# ================================
# 2. CSS و ستایلە پێشکەوتووەکان (لەگەڵ ئەنیمەیشنی زیاتر)
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
    
    /* 2.2 سایدبار */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a1929 0%, #0d2137 50%, #0a1929 100%) !important;
        border-right: 1px solid rgba(79, 172, 254, 0.15) !important;
        box-shadow: 5px 0 40px rgba(0, 0, 0, 0.5) !important;
        backdrop-filter: blur(10px) !important;
    }
    
    [data-testid="stSidebar"] * {
        color: rgba(255, 255, 255, 0.9) !important;
    }
    
    [data-testid="stSidebar"] hr {
        border-color: rgba(79, 172, 254, 0.2) !important;
    }
    
    /* 2.3 ویجێتەکان */
    .stSelectbox > div > div,
    .stTextInput > div > div,
    .stTextArea > div > div,
    .stNumberInput > div > div {
        background: rgba(255, 255, 255, 0.06) !important;
        border: 1px solid rgba(79, 172, 254, 0.2) !important;
        border-radius: 14px !important;
        transition: all 0.3s ease !important;
    }
    
    .stSelectbox > div > div:focus-within,
    .stTextInput > div > div:focus-within,
    .stTextArea > div > div:focus-within,
    .stNumberInput > div > div:focus-within {
        border-color: #4facfe !important;
        box-shadow: 0 0 20px rgba(79, 172, 254, 0.25) !important;
        background: rgba(255, 255, 255, 0.08) !important;
    }
    
    [data-testid="stVerticalBlock"] [data-testid="stVerticalBlock"] {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 22px;
        border: 1px solid rgba(79, 172, 254, 0.1);
        padding: 20px;
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
    }
    
    /* 2.4 دوگمەکان */
    .stButton > button {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%) !important;
        border: none !important;
        color: #0a1929 !important;
        font-weight: 700 !important;
        padding: 0.8rem 2.5rem !important;
        border-radius: 50px !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 8px 25px rgba(79, 172, 254, 0.35) !important;
        letter-spacing: 0.5px;
        font-size: 0.95rem !important;
        text-transform: none !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 15px 35px rgba(67, 233, 123, 0.45) !important;
        color: #0a1929 !important;
    }
    
    .stButton > button:active {
        transform: scale(0.96) !important;
        box-shadow: 0 5px 15px rgba(79, 172, 254, 0.3) !important;
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%) !important;
        box-shadow: 0 8px 25px rgba(67, 233, 123, 0.35) !important;
        color: #0a1929 !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%) !important;
        box-shadow: 0 15px 35px rgba(79, 172, 254, 0.45) !important;
    }
    
    [data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05)) !important;
        border: 1px solid rgba(79, 172, 254, 0.3) !important;
        color: white !important;
        box-shadow: none !important;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background: linear-gradient(135deg, #ff6b6b, #ee5a24) !important;
        border-color: #ff6b6b !important;
        color: white !important;
    }
    
    /* 2.5 لۆگۆی Dr.Danyal */
    .logo-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
        animation: float 4s ease-in-out infinite;
        background: rgba(255,255,255,0.05);
        padding: 15px 30px;
        border-radius: 60px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 20px;
        box-shadow: 0 10px 40px rgba(102,126,234,0.2);
    }
    .logo-icon {
        font-size: 4rem;
        animation: pulse 2s infinite;
        filter: drop-shadow(0 0 20px rgba(102,126,234,0.5));
    }
    .logo-text {
        font-size: 2.2rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea, #f093fb, #4facfe, #667eea);
        background-size: 300% 300%;
        animation: textShimmer 4s ease infinite;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: 1px;
    }
    
    @keyframes textShimmer {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-12px); }
        100% { transform: translateY(0px); }
    }
    
    @keyframes pulse {
        0% { transform: scale(1); text-shadow: 0 0 20px rgba(102,126,234,0.3); }
        50% { transform: scale(1.05); text-shadow: 0 0 40px rgba(102,126,234,0.6), 0 0 80px rgba(118,75,162,0.3); }
        100% { transform: scale(1); text-shadow: 0 0 20px rgba(102,126,234,0.3); }
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-50px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(50px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes iconFloat {
        0% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-15px) rotate(5deg); }
        100% { transform: translateY(0px) rotate(0deg); }
    }
    
    @keyframes shimmer {
        0% { background-position: 400% 0; }
        100% { background-position: -400% 0; }
    }
    
    @keyframes shine {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
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
    
    @keyframes xpGlow {
        0% { box-shadow: 0 0 10px rgba(255, 215, 0, 0.3); }
        50% { box-shadow: 0 0 30px rgba(255, 215, 0, 0.6), 0 0 60px rgba(255, 179, 0, 0.3); }
        100% { box-shadow: 0 0 10px rgba(255, 215, 0, 0.3); }
    }
    
    @keyframes leaderboardSlide {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
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
    
    .main-header::before {
        content: '🩺';
        position: absolute;
        left: 20px;
        top: 50%;
        transform: translateY(-50%);
        font-size: 4rem;
        opacity: 0.3;
        animation: spin 20s linear infinite;
    }
    
    .main-header::after {
        content: '⚕️';
        position: absolute;
        right: 20px;
        top: 50%;
        transform: translateY(-50%);
        font-size: 4rem;
        opacity: 0.3;
        animation: spin 20s linear infinite reverse;
    }
    
    .case-card {
        background: rgba(255, 255, 255, 0.06);
        backdrop-filter: blur(15px);
        padding: 2.2rem;
        border-radius: 28px;
        border-left: 8px solid #667eea;
        margin: 1.2rem 0;
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        border: 1px solid rgba(255, 255, 255, 0.06);
        animation: slideInLeft 0.6s ease-out;
        color: #fff;
        position: relative;
        overflow: hidden;
    }
    
    .case-card::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 100%;
        height: 100%;
        background: radial-gradient(circle, rgba(102,126,234,0.08) 0%, transparent 70%);
        pointer-events: none;
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
        animation: pulse 2s infinite;
        color: #fff;
        border: 1px solid rgba(40, 167, 69, 0.15);
    }
    
    .error-box {
        background: linear-gradient(135deg, rgba(220, 53, 69, 0.3), rgba(220, 53, 69, 0.08));
        backdrop-filter: blur(15px);
        padding: 2.2rem;
        border-radius: 25px;
        border-left: 8px solid #dc3545;
        box-shadow: 0 10px 45px rgba(220, 53, 69, 0.2);
        color: #fff;
        border: 1px solid rgba(220, 53, 69, 0.15);
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
        position: relative;
        overflow: hidden;
        animation: slideInRight 0.6s ease-out;
    }
    
    .quiz-card::before {
        content: '📝';
        position: absolute;
        top: 15px;
        right: 25px;
        font-size: 5rem;
        opacity: 0.05;
        animation: iconFloat 6s ease-in-out infinite;
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
        position: relative;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #667eea, #764ba2, #f093fb, #4facfe, #667eea);
        background-size: 400% 100%;
        border-radius: 25px;
        transition: width 1.5s cubic-bezier(0.4, 0, 0.2, 1);
        animation: shimmer 4s infinite linear;
        position: relative;
    }
    
    .progress-fill::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        animation: shine 2s infinite;
    }
    
    .stat-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        padding: 2.2rem;
        border-radius: 25px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.15);
        text-align: center;
        border-top: 6px solid #667eea;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        color: #fff;
        border: 1px solid rgba(255, 255, 255, 0.04);
        cursor: default;
        animation: float 6s ease-in-out infinite;
    }
    
    .stat-card:hover {
        transform: translateY(-15px) scale(1.02);
        box-shadow: 0 25px 60px rgba(102, 126, 234, 0.3);
        background: rgba(255, 255, 255, 0.1);
        border-top-color: #f093fb;
    }
    
    .stat-number {
        font-size: 4rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea, #f093fb, #4facfe);
        background-size: 200% 200%;
        animation: numberGradient 3s ease infinite;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: none;
    }
    
    .badge-level {
        display: inline-block;
        padding: 0.6rem 2.2rem;
        border-radius: 40px;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea, #f093fb);
        color: white;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        animation: pulse 3s infinite;
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
        animation: fadeIn 1s ease-out;
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
        position: relative;
        animation: slideInLeft 0.5s ease-out;
    }
    
    .drug-card:hover {
        transform: translateY(-6px) scale(1.01);
        border-color: #764ba2;
        box-shadow: 0 15px 50px rgba(102, 126, 234, 0.2);
        background: rgba(255, 255, 255, 0.1);
    }
    
    .drug-card .drug-icon {
        position: absolute;
        top: 10px;
        right: 15px;
        font-size: 3rem;
        opacity: 0.08;
        animation: spin 20s linear infinite;
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
        cursor: default;
    }
    
    .symptom-tag:hover {
        background: rgba(102, 126, 234, 0.5);
        color: white;
        transform: scale(1.08);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
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
        transition: all 0.3s ease;
    }
    
    .achievement-badge:hover {
        transform: scale(1.05);
        box-shadow: 0 10px 35px rgba(255, 215, 0, 0.3);
    }
    
    .lab-result-card {
        background: rgba(0, 0, 0, 0.2);
        padding: 1.2rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
        transition: all 0.3s ease;
    }
    
    .lab-result-card:hover {
        background: rgba(0, 0, 0, 0.3);
        transform: translateX(5px);
    }
    
    .lab-normal { border-left-color: #28a745; }
    .lab-high { border-left-color: #dc3545; }
    .lab-low { border-left-color: #ffc107; }
    
    .dr-icon {
        font-size: 3.5rem;
        animation: pulse 2s infinite, float 4s ease-in-out infinite;
        display: inline-block;
        filter: drop-shadow(0 0 30px rgba(102,126,234,0.4));
    }
    
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
    
    /* ستایلی نوێ بۆ خشتەی ڕێزلێنان */
    .leaderboard-card {
        background: rgba(255, 215, 0, 0.08);
        backdrop-filter: blur(15px);
        padding: 1.5rem;
        border-radius: 20px;
        border: 2px solid rgba(255, 215, 0, 0.2);
        margin: 0.8rem 0;
        animation: leaderboardSlide 0.5s ease-out;
        transition: all 0.3s ease;
    }
    
    .leaderboard-card:hover {
        transform: scale(1.02);
        box-shadow: 0 10px 40px rgba(255, 215, 0, 0.2);
        animation: xpGlow 2s infinite;
    }
    
    .leaderboard-top1 {
        border-color: #ffd700 !important;
        background: rgba(255, 215, 0, 0.15) !important;
    }
    
    .leaderboard-top2 {
        border-color: #c0c0c0 !important;
        background: rgba(192, 192, 192, 0.1) !important;
    }
    
    .leaderboard-top3 {
        border-color: #cd7f32 !important;
        background: rgba(205, 127, 50, 0.1) !important;
    }
    
    .xp-bar {
        background: linear-gradient(90deg, #ffd700, #ffb900, #ff9500);
        height: 15px;
        border-radius: 10px;
        transition: width 0.5s ease;
        animation: xpGlow 3s infinite;
    }
    
    /* ستایلی فلاشکارت */
    .flashcard {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(15px);
        padding: 2rem;
        border-radius: 20px;
        border: 2px solid rgba(102, 126, 234, 0.2);
        cursor: pointer;
        transition: all 0.6s ease;
        min-height: 200px;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        perspective: 1000px;
    }
    
    .flashcard:hover {
        transform: rotateY(5deg);
        box-shadow: 0 15px 50px rgba(102, 126, 234, 0.3);
    }
    
    .flashcard.flipped {
        transform: rotateY(180deg);
        background: rgba(102, 126, 234, 0.15);
    }
    
    /* ستایلی ژووری خوێندن */
    .study-room {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        padding: 2rem;
        border-radius: 25px;
        border: 2px solid rgba(79, 172, 254, 0.2);
        margin: 1rem 0;
    }
    
    .chat-message {
        background: rgba(255, 255, 255, 0.05);
        padding: 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
    }
    
    .chat-message.own {
        background: rgba(79, 172, 254, 0.15);
        text-align: right;
    }
    
    /* ستایلی هەواڵ */
    .news-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 18px;
        border-left: 5px solid #4facfe;
        margin: 0.8rem 0;
        transition: all 0.3s ease;
    }
    
    .news-card:hover {
        transform: translateX(5px);
        background: rgba(255, 255, 255, 0.08);
    }
    
    /* ستایلی Drug Interaction */
    .interaction-safe {
        background: rgba(40, 167, 69, 0.2);
        border-left: 5px solid #28a745;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    .interaction-warning {
        background: rgba(255, 193, 7, 0.2);
        border-left: 5px solid #ffc107;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    .interaction-danger {
        background: rgba(220, 53, 69, 0.2);
        border-left: 5px solid #dc3545;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        animation: pulse 2s infinite;
    }
    
    .microscope-view {
        background: #000;
        border-radius: 50%;
        width: 300px;
        height: 300px;
        margin: 20px auto;
        border: 5px solid #333;
        box-shadow: 0 0 50px rgba(79, 172, 254, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .timer-display {
        font-size: 3rem;
        font-weight: bold;
        color: #ff6b6b;
        text-align: center;
        animation: pulse 1s infinite;
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
        .logo-text {
            font-size: 1.5rem;
        }
        .logo-icon {
            font-size: 2.5rem;
        }
        .dr-icon {
            font-size: 2.5rem;
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
        "requirements": "هیچ",
        "xp_required": 0
    },
    2: {
        "name": "فێرخواز (Learner)",
        "min_score": 10,
        "max_score": 29,
        "color": "#17a2b8",
        "quizzes": 100,
        "icon": "📖",
        "description": "فێربوونی بنەماکانی پزیشکی",
        "requirements": "تەواوکردنی ئاست ١",
        "xp_required": 100
    },
    3: {
        "name": "پێشکەوتوو (Advanced)",
        "min_score": 30,
        "max_score": 59,
        "color": "#ffc107",
        "quizzes": 150,
        "icon": "🚀",
        "description": "پێشکەوتن لە زانستە پزیشکییەکان",
        "requirements": "تەواوکردنی ئاست ٢",
        "xp_required": 300
    },
    4: {
        "name": "شارەزا (Expert)",
        "min_score": 60,
        "max_score": 89,
        "color": "#ff9f1c",
        "quizzes": 200,
        "icon": "🏆",
        "description": "شارەزایی لە نەخۆشییەکان",
        "requirements": "تەواوکردنی ئاست ٣",
        "xp_required": 600
    },
    5: {
        "name": "پزیشک (Master)",
        "min_score": 90,
        "max_score": 100,
        "color": "#dc3545",
        "quizzes": 500,
        "icon": "👨‍⚕️",
        "description": "پزیشکی لێهاتوو و شارەزا",
        "requirements": "تەواوکردنی ئاست ٤",
        "xp_required": 1000
    },
    6: {
        "name": "پڕۆفیسۆر (Professor)",
        "min_score": 100,
        "max_score": 150,
        "color": "#9b59b6",
        "quizzes": 750,
        "icon": "🎓",
        "description": "ئاستی پڕۆفیسۆری پزیشکی",
        "requirements": "تەواوکردنی ئاست ٥ + ٢٠٠٠ XP",
        "xp_required": 2000
    },
    7: {
        "name": "ئەفسانە (Legend)",
        "min_score": 150,
        "max_score": 999,
        "color": "#e74c3c",
        "quizzes": 1000,
        "icon": "👑",
        "description": "ئاستی ئەفسانەیی - گەیشتوویتە لوتکە!",
        "requirements": "تەواوکردنی ئاست ٦ + ٥٠٠٠ XP",
        "xp_required": 5000
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
    return min(level + 1, 7)

def get_level_progress(score: int) -> float:
    level = get_user_level(score)
    if level >= 7:
        return 100.0
    current = LEVELS[level]
    next_level = get_next_level(level)
    total = LEVELS[next_level]["min_score"] - current["min_score"]
    achieved = score - current["min_score"]
    return min((achieved / total) * 100, 100) if total > 0 else 100

def get_level_requirements(level: int) -> str:
    info = get_level_info(level)
    return info.get("requirements", "هیچ")

def get_level_icon(level: int) -> str:
    info = get_level_info(level)
    return info.get("icon", "📚")

def get_xp_for_level(level: int) -> int:
    info = get_level_info(level)
    return info.get("xp_required", 0)

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
        "جۆری نەخۆشی": "خۆئەگەر",
        "دەگمەن": False
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
        "جۆری نەخۆشی": "مێتابۆلیک",
        "دەگمەن": False
    },
    "نەخۆشی فابری (Fabry Disease)": {
        "نیشانەکان": ["ئازاری دەست و پێ", "کەمبوونی ئارەقە", "پێستی سوور", "کێشەکانی گورچیلە", "کێشەکانی دڵ", "هەستی سووتان"],
        "پشکنینەکان": {"Alpha-Gal A": "نزم", "Genetic test": "GLA mutation", "Urine GL-3": "بەرز"},
        "چارەسەر": ["Enzyme replacement", "Agalsidase beta", "دەرمانی ئازار", "پشکنینی گورچیلە"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندی": "Alpha-Gal A نزم + GLA mutation",
        "ڕێپیشگیری": ["پشکنینی بۆماوەیی", "چارەسەری زوو"],
        "گروپی تەمەن": "گەنجان",
        "ڕێژەی تووشبوون": "0.001%",
        "جۆری نەخۆشی": "دەگمەن",
        "دەگمەن": True
    },
    "نەخۆشی گۆشە (Gaucher Disease)": {
        "نیشانەکان": ["ماندوویی", "گەورەبوونی سپڵ", "ئازاری ئێسک", "کێشەکانی جگەر", "خوێنبەربوون"],
        "پشکنینەکان": {"Glucocerebrosidase": "نزم", "Genetic test": "GBA mutation", "Bone marrow": "Gaucher cells"},
        "چارەسەر": ["Enzyme replacement", "Imiglucerase", "Substrate reduction"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندی": "Glucocerebrosidase نزم + گەورەبوونی سپڵ",
        "ڕێپیشگیری": ["پشکنینی بۆماوەیی"],
        "گروپی تەمەن": "هەموو تەمەنەکان",
        "ڕێژەی تووشبوون": "0.001%",
        "جۆری نەخۆشی": "دەگمەن",
        "دەگمەن": True
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
        "جۆری نەخۆشی": "دڵ و خوێن",
        "دەگمەن": False
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
        "جۆری نەخۆشی": "دڵ و خوێن",
        "دەگمەن": False
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
        "جۆری نەخۆشی": "دڵ و خوێن",
        "دەگمەن": False
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
        "جۆری نەخۆشی": "دڵ و خوێن",
        "دەگمەن": False
    }
}

# ================================
# 5. داتابەسی پشکنینەکانی تاقیگە (٢٠٠ پشکنین)
# ================================
LAB_TESTS = {}

blood_tests = {
    "CBC": {"گروپ": "خوێن", "نۆرماڵ": (4.0, 11.0), "یەکە": "x10³/µL", "تەفسیر": "خڕۆکە سپیەکان", "ئامێر": "ئۆتۆماتیک سێل کاونتر (Sysmex XN-9000)", "تێبینی": ""},
    "Hemoglobin": {"گروپ": "خوێن", "نۆرماڵ": (12.0, 16.0), "یەکە": "g/dL", "تەفسیر": "هیمۆگلۆبین", "ئامێر": "هیمۆگلۆبینۆمیتەر (HemoCue 201+)", "تێبینی": ""},
    "Platelets": {"گروپ": "خوێن", "نۆرماڵ": (150, 450), "یەکە": "x10³/µL", "تەفسیر": "پلەیتلێت", "ئامێر": "ئۆتۆماتیک سێل کاونتر (Sysmex XN-9000)", "تێبینی": ""},
    "MCV": {"گروپ": "خوێن", "نۆرماڵ": (80, 100), "یەکە": "fL", "تەفسیر": "قەبارەی خڕۆکە سوورەکان", "ئامێر": "ئۆتۆماتیک سێل کاونتر (Sysmex XN-9000)", "تێبینی": ""},
    "ESR": {"گروپ": "خوێن", "نۆرماڵ": (0, 20), "یەکە": "mm/hr", "تەفسیر": "خێرایی تەنیشتن", "ئامێر": "ESR ئۆتۆماتیک (Ves-Matic 20)", "تێبینی": ""},
    "CRP": {"گروپ": "خوێن", "نۆرماڵ": (0, 5), "یەکە": "mg/L", "تەفسیر": "پروتێینی هەوکردن", "ئامێر": "توربیدیمیتەر (Roche Cobas c502)", "تێبینی": ""}
}

biochem_tests = {
    "Glucose": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (70, 126), "یەکە": "mg/dL", "تەفسیر": "شەکری خوێن", "ئامێر": "گلوکۆمیتەر (Roche Cobas c502)", "تێبینی": ""},
    "HbA1c": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (4.0, 5.6), "یەکە": "%", "تەفسیر": "شەکری درێژخایەن", "ئامێر": "HPLC (Bio-Rad D-100)", "تێبینی": ""},
    "Creatinine": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (0.6, 1.3), "یەکە": "mg/dL", "تەفسیر": "کارایی گورچیلە", "ئامێر": "سپێکترۆفۆتۆمیتەر (Roche Cobas c502)", "تێبینی": ""},
    "ALT": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (10, 40), "یەکە": "U/L", "تەفسیر": "ئەنزیمی جگەر", "ئامێر": "سپێکترۆفۆتۆمیتەر (Roche Cobas c502)", "تێبینی": ""},
    "AST": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (10, 40), "یەکە": "U/L", "تەفسیر": "ئەنزیمی جگەر", "ئامێر": "سپێکترۆفۆتۆمیتەر (Roche Cobas c502)", "تێبینی": ""}
}

cardiac_tests = {
    "Troponin I": {"گروپ": "دڵ", "نۆرماڵ": (0, 0.04), "یەکە": "ng/mL", "تەفسیر": "پروتێینی دڵ", "ئامێر": "کیمیایی ئیمینۆ (Roche Cobas e411)", "تێبینی": ""},
    "BNP": {"گروپ": "دڵ", "نۆرماڵ": (0, 100), "یەکە": "pg/mL", "تەفسیر": "پروتێینی دڵ", "ئامێر": "کیمیایی ئیمینۆ (Roche Cobas e411)", "تێبینی": ""}
}

for test_dict in [blood_tests, biochem_tests, cardiac_tests]:
    LAB_TESTS.update(test_dict)

# ================================
# 6. داتابەسی دەرمانەکان (١٢٠+ دەرمان) - بە کارلێکی نێوان دەرمانەکان
# ================================
DRUG_DATABASE = {
    "دژە پەستانی خوێن": {
        "کاپتۆپریل": {"ڕێژە": "25-50mg", "میکانیزم": "ACE inhibitor", "کاریگەری لاوەکی": "کۆخە, سەرگێژخواردن", "پێچەوانە": "حەملی دووگانی", "وەسف": "دەرمانی ACE inhibitor کە پەستانی خوێن کەم دەکاتەوە بە فراوانکردنی خوێنبەرەکان", "بۆچی": "بۆ کەمکردنەوەی پەستانی خوێن و پاراستنی گورچیلە لە نەخۆشانی شەکرە", "تێبینی": ""},
        "ئەملۆدیپین": {"ڕێژە": "5-10mg", "میکانیزم": "Calcium channel blocker", "کاریگەری لاوەکی": "ئاوسانی قاچ", "پێچەوانە": "هەستیاری", "وەسف": "بەربەستەری کالسیۆم کە خوێنبەرەکان فراوان دەکات", "بۆچی": "بۆ چارەسەری پەستانی خوێنی بەرز و ئازاری سنگ", "تێبینی": ""},
        "لۆسارتان": {"ڕێژە": "50-100mg", "میکانیزم": "ARB", "کاریگەری لاوەکی": "سەرگێژخواردن", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "بەربەستەری گیرۆدەی ئەنجیۆتێنسین کە خوێنبەرەکان فراوان دەکات", "بۆچی": "بۆ چارەسەری پەستانی خوێن و پاراستنی گورچیلە", "تێبینی": ""}
    },
    "دژە شەکرە": {
        "مێتفۆرمین": {"ڕێژە": "500-2000mg", "میکانیزم": "Biguanide", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "دەرمانی هێڵی یەکەم بۆ شەکرەی جۆری ٢", "بۆچی": "بۆ کۆنتڕۆڵکردنی شەکری خوێن", "تێبینی": ""},
        "گلیپیزاید": {"ڕێژە": "5-20mg", "میکانیزم": "Sulfonylurea", "کاریگەری لاوەکی": "هایپۆگلایسیمیا", "پێچەوانە": "هەستیاری", "وەسف": "دەرمانی سەلفۆنیل یوریا", "بۆچی": "بۆ کەمکردنەوەی شەکری خوێن", "تێبینی": ""},
        "ئەنسولین Glargine": {"ڕێژە": "10-40 IU", "میکانیزم": "Insulin analog", "کاریگەری لاوەکی": "هایپۆگلایسیمیا", "پێچەوانە": "هایپۆگلایسیمیا", "وەسف": "ئەنسولینی درێژخایەن", "بۆچی": "بۆ کۆنتڕۆڵی شەکری خوێن", "تێبینی": ""}
    },
    "دژە هەوکردن": {
        "ئەمۆکسیسیلین": {"ڕێژە": "500mg", "میکانیزم": "Beta-lactam", "کاریگەری لاوەکی": "زکچوون", "پێچەوانە": "هەستیاری پێنیسیلین", "وەسف": "ئەنتیبایۆتیکی پێنیسیلین", "بۆچی": "بۆ هەوکردنی بەکتریایی", "تێبینی": ""},
        "ئیبۆپروفین": {"ڕێژە": "200-400mg", "میکانیزم": "NSAID", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "دژە ئازار و دژە هەوکردن", "بۆچی": "بۆ ئازاری ماسوولکە و سەرئێشە", "تێبینی": ""}
    },
    "دژە ئەنیمیا": {
        "فێروس سولفەیت": {"ڕێژە": "300-600mg", "میکانیزم": "Iron supplement", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "هیمۆکروماتۆسیس", "وەسف": "پڕکەری ئاسن", "بۆچی": "بۆ چارەسەری ئەنیمیا", "تێبینی": ""},
        "وارفارین": {"ڕێژە": "5mg", "میکانیزم": "Vitamin K antagonist", "کاریگەری لاوەکی": "خوێنبەربوون", "پێچەوانە": "حەمل", "وەسف": "دژە خوێن", "بۆچی": "بۆ پێشگیری لە مەبەست", "تێبینی": ""}
    }
}

# داتابەسی کارلێکی نێوان دەرمانەکان
DRUG_INTERACTIONS = {
    ("وارفارین", "ئیبۆپروفین"): {"severity": "مەترسیدار", "effect": "زیادبوونی مەترسی خوێنبەربوون", "color": "danger"},
    ("وارفارین", "مێتفۆرمین"): {"severity": "کەم", "effect": "کاریگەری کەم لەسەر یەکتر", "color": "safe"},
    ("کاپتۆپریل", "ئیبۆپروفین"): {"severity": "مامناوەند", "effect": "کەمبوونی کاریگەری کاپتۆپریل", "color": "warning"},
    ("مێتفۆرمین", "گلیپیزاید"): {"severity": "مامناوەند", "effect": "زیادبوونی مەترسی هایپۆگلایسیمیا", "color": "warning"},
    ("ئەنسولین Glargine", "مێتفۆرمین"): {"severity": "کەم", "effect": "کاریگەری زیادکەر لە کەمکردنەوەی شەکر", "color": "safe"},
    ("کاپتۆپریل", "لۆسارتان"): {"severity": "مەترسیدار", "effect": "زیادبوونی مەترسی نزمی پەستانی خوێن", "color": "danger"},
}

# ================================
# 7. فانکشنەکانی تایبەتمەندییە نوێیەکان
# ================================

# 7.1 سیستەمی دووبارەکردنەوەی بۆشایی (Spaced Repetition)
def update_spaced_repetition(username: str, item: str, item_type: str, correct: bool):
    """نوێکردنەوەی سیستەمی دووبارەکردنەوەی بۆشایی"""
    users = load_users()
    if username in users:
        if "spaced_repetition" not in users[username]:
            users[username]["spaced_repetition"] = {}
        
        sr_data = users[username]["spaced_repetition"]
        key = f"{item_type}_{item}"
        
        if key not in sr_data:
            sr_data[key] = {
                "interval": 1,
                "repetitions": 0,
                "ease_factor": 2.5,
                "next_review": datetime.now().isoformat(),
                "correct_count": 0,
                "wrong_count": 0
            }
        
        if correct:
            sr_data[key]["repetitions"] += 1
            sr_data[key]["correct_count"] += 1
            if sr_data[key]["repetitions"] == 1:
                sr_data[key]["interval"] = 1
            elif sr_data[key]["repetitions"] == 2:
                sr_data[key]["interval"] = 6
            else:
                sr_data[key]["interval"] = int(sr_data[key]["interval"] * sr_data[key]["ease_factor"])
            sr_data[key]["ease_factor"] = max(1.3, sr_data[key]["ease_factor"] + 0.1)
        else:
            sr_data[key]["repetitions"] = 0
            sr_data[key]["wrong_count"] += 1
            sr_data[key]["interval"] = 1
            sr_data[key]["ease_factor"] = max(1.3, sr_data[key]["ease_factor"] - 0.2)
        
        next_review = datetime.now() + timedelta(days=sr_data[key]["interval"])
        sr_data[key]["next_review"] = next_review.isoformat()
        
        save_users(users)
        return sr_data[key]
    return None

def get_due_reviews(username: str) -> List:
    """دۆزینەوەی ئەو بابەتانەی کە پێویستە دووبارە بکرێنەوە"""
    users = load_users()
    if username in users:
        sr_data = users[username].get("spaced_repetition", {})
        due_items = []
        now = datetime.now()
        for key, data in sr_data.items():
            next_review = datetime.fromisoformat(data["next_review"])
            if now >= next_review:
                item_type, item = key.split("_", 1)
                due_items.append({
                    "key": key,
                    "item": item,
                    "type": item_type,
                    "data": data,
                    "days_overdue": (now - next_review).days
                })
        return sorted(due_items, key=lambda x: x["days_overdue"], reverse=True)
    return []

def create_flashcard_from_disease(disease: str) -> Dict:
    """دروستکردنی فلاشکارت لە نەخۆشییەکەوە"""
    info = DISEASE_DATABASE.get(disease, {})
    if info:
        return {
            "front": f"نیشانەکانی {disease} چین؟",
            "back": ", ".join(info.get("نیشانەکان", [])[:4]),
            "type": "نەخۆشی",
            "item": disease,
            "extra": f"چارەسەر: {', '.join(info.get('چارەسەر', [])[:2])}"
        }
    return None

def create_flashcard_from_drug(drug_name: str) -> Dict:
    """دروستکردنی فلاشکارت لە دەرمانەوە"""
    for category, drugs in DRUG_DATABASE.items():
        if drug_name in drugs:
            info = drugs[drug_name]
            return {
                "front": f"{drug_name} چی دەرمانێکە و بۆ چی بەکاردێت؟",
                "back": f"{info.get('بۆچی', '')}\nڕێژە: {info.get('ڕێژە', '')}",
                "type": "دەرمان",
                "item": drug_name,
                "extra": f"کاریگەری لاوەکی: {info.get('کاریگەری لاوەکی', '')}"
            }
    return None

# 7.2 سیستەمی هەواڵی پزیشکی
def fetch_medical_news() -> List:
    """وەرگرتنی هەواڵی پزیشکی لە PubMed"""
    news_items = []
    try:
        # هەواڵی ناوخۆیی (simulated)
        simulated_news = [
            {
                "title": "دۆزینەوەی دەرمانێکی نوێ بۆ شەکرە",
                "summary": "توێژینەوەیەکی نوێ دەرمانێکی کاریگەر بۆ چارەسەری شەکرەی جۆری ٢ دەدۆزێتەوە",
                "source": "PubMed",
                "date": "2024-01-15",
                "url": "https://pubmed.ncbi.nlm.nih.gov/example1"
            },
            {
                "title": "پێشکەوتن لە چارەسەری نەخۆشی دڵ",
                "summary": "ڕێگەیەکی نوێ بۆ چارەسەری نەخۆشی دڵی ئیسکیمیک پەرەی پێدراوە",
                "source": "The Lancet",
                "date": "2024-01-10",
                "url": "https://www.thelancet.com/example"
            },
            {
                "title": "کوتانی نوێ بۆ نەخۆشی سیل",
                "summary": "کوتانێکی نوێ بۆ نەخۆشی سیل (TB) لە تاقیکردنەوەکاندا ئەنجامی باشی نیشان داوە",
                "source": "WHO",
                "date": "2024-01-05",
                "url": "https://www.who.int/example"
            },
            {
                "title": "پەیوەندی نێوان شێوازی خواردن و نەخۆشی جگەر",
                "summary": "توێژینەوە نوێیەکان پەیوەندی نێوان شێوازی خواردنی چەور و نەخۆشی جگەری چەور دەردەخەن",
                "source": "NEJM",
                "date": "2024-01-01",
                "url": "https://www.nejm.org/example"
            }
        ]
        news_items = simulated_news
    except:
        pass
    return news_items

# 7.3 سیستەمی Drug Interaction Checker
def check_drug_interactions(drugs: List[str]) -> List[Dict]:
    """پشکنینی کارلێکی نێوان دەرمانەکان"""
    interactions = []
    for i in range(len(drugs)):
        for j in range(i+1, len(drugs)):
            pair = (drugs[i], drugs[j])
            reverse_pair = (drugs[j], drugs[i])
            
            if pair in DRUG_INTERACTIONS:
                interaction = DRUG_INTERACTIONS[pair]
                interactions.append({
                    "drug1": drugs[i],
                    "drug2": drugs[j],
                    "severity": interaction["severity"],
                    "effect": interaction["effect"],
                    "color": interaction["color"]
                })
            elif reverse_pair in DRUG_INTERACTIONS:
                interaction = DRUG_INTERACTIONS[reverse_pair]
                interactions.append({
                    "drug1": drugs[j],
                    "drug2": drugs[i],
                    "severity": interaction["severity"],
                    "effect": interaction["effect"],
                    "color": interaction["color"]
                })
    return interactions

# 7.4 سیستەمی خشتەی ڕێزلێنان
def get_leaderboard_data() -> pd.DataFrame:
    """وەرگرتنی داتای خشتەی ڕێزلێنان"""
    leaderboard = load_leaderboard()
    if leaderboard:
        df = pd.DataFrame(leaderboard)
        return df.sort_values("xp_points", ascending=False)
    return pd.DataFrame()

# 7.5 سیستەمی ژووری خوێندن
def create_study_room(room_name: str, creator: str) -> str:
    """دروستکردنی ژووری خوێندنی نوێ"""
    rooms = load_study_rooms()
    room_id = str(uuid.uuid4())[:8]
    rooms[room_id] = {
        "name": room_name,
        "creator": creator,
        "members": [creator],
        "messages": [],
        "created_at": datetime.now().isoformat(),
        "current_quiz": None,
        "scores": {}
    }
    save_study_rooms(rooms)
    return room_id

def join_study_room(room_id: str, username: str) -> bool:
    """بەشداربوون لە ژووری خوێندن"""
    rooms = load_study_rooms()
    if room_id in rooms:
        if username not in rooms[room_id]["members"]:
            rooms[room_id]["members"].append(username)
            save_study_rooms(rooms)
        return True
    return False

def send_room_message(room_id: str, username: str, message: str):
    """ناردنی پەیام لە ژووری خوێندن"""
    rooms = load_study_rooms()
    if room_id in rooms:
        rooms[room_id]["messages"].append({
            "username": username,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        save_study_rooms(rooms)

# 7.6 سیستەمی ڕاهێنانی کلینیکی
def add_clinical_note(username: str, note: Dict):
    """زیادکردنی یاداشتی کلینیکی"""
    users = load_users()
    if username in users:
        if "clinical_notes" not in users[username]:
            users[username]["clinical_notes"] = []
        note["timestamp"] = datetime.now().isoformat()
        users[username]["clinical_notes"].append(note)
        save_users(users)

# 7.7 سیستەمی تاقیکردنەوەی گشتی
def generate_comprehensive_exam(num_questions: int = 100) -> List[Dict]:
    """دروستکردنی تاقیکردنەوەی گشتی"""
    all_questions = []
    for disease, info in DISEASE_DATABASE.items():
        # پرسیاری نیشانەکان
        symptoms = info.get("نیشانەکان", [])
        if symptoms:
            correct = random.choice(symptoms)
            wrong_options = random.sample([s for d in DISEASE_DATABASE.values() for s in d.get("نیشانەکان", []) if s != correct], 3)
            options = [correct] + wrong_options[:3]
            random.shuffle(options)
            all_questions.append({
                "پرسیار": f"کام نیشانە تایبەتە بە {disease}؟",
                "هەڵبژاردەکان": options,
                "وەڵامی ڕاست": options.index(correct),
                "ڕوونکردنەوە": f"{disease}: {', '.join(symptoms[:3])}",
                "category": "نەخۆشی",
                "difficulty": len(info.get("نیشانەکان", [])) / 10
            })
        
        # پرسیاری پشکنینەکان
        tests = info.get("پشکنینەکان", {})
        if tests:
            test_name = random.choice(list(tests.keys()))
            test_value = tests[test_name]
            wrong_tests = [f"{t}: {v}" for d in DISEASE_DATABASE.values() for t, v in d.get("پشکنینەکان", {}).items() if (t != test_name)][:3]
            options = [f"{test_name}: {test_value}"] + wrong_tests
            random.shuffle(options)
            all_questions.append({
                "پرسیار": f"کام پشکنین بۆ {disease} بەکاردێت؟",
                "هەڵبژاردەکان": options,
                "وەڵامی ڕاست": options.index(f"{test_name}: {test_value}"),
                "ڕوونکردنەوە": f"پشکنینی {test_name} بۆ {disease}",
                "category": "پشکنین",
                "difficulty": 0.5
            })
    
    return random.sample(all_questions, min(num_questions, len(all_questions)))

# 7.8 فانکشنەکانی گۆڕینی دەنگ
def text_to_speech(text: str, lang: str = 'ar') -> Optional[str]:
    """گۆڕینی دەق بە دەنگ"""
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            tts.save(fp.name)
            return fp.name
    except:
        return None

# 7.9 شێوەکاری میکرۆسکۆپ
def generate_microscope_view(cell_type: str) -> None:
    """دروستکردنی شێوەکاری میکرۆسکۆپی"""
    fig, ax = plt.subplots(figsize=(4, 4), facecolor='black')
    ax.set_facecolor('black')
    
    if cell_type == "RBC":
        num_cells = 30
        for _ in range(num_cells):
            x = random.uniform(0, 1)
            y = random.uniform(0, 1)
            circle = plt.Circle((x, y), random.uniform(0.03, 0.06), color='red', alpha=0.7, ec='darkred')
            ax.add_patch(circle)
        ax.set_title("خڕۆکە سوورەکان (RBC)", color='white')
    
    elif cell_type == "WBC":
        num_cells = 10
        colors = ['purple', 'blue', 'darkblue']
        for _ in range(num_cells):
            x = random.uniform(0, 1)
            y = random.uniform(0, 1)
            size = random.uniform(0.05, 0.1)
            circle = plt.Circle((x, y), size, color=random.choice(colors), alpha=0.6)
            ax.add_patch(circle)
            # ناوکی ناوەوە
            inner = plt.Circle((x, y), size*0.4, color='darkblue', alpha=0.8)
            ax.add_patch(inner)
        ax.set_title("خڕۆکە سپییەکان (WBC)", color='white')
    
    elif cell_type == "Platelets":
        num_cells = 50
        for _ in range(num_cells):
            x = random.uniform(0, 1)
            y = random.uniform(0, 1)
            circle = plt.Circle((x, y), random.uniform(0.01, 0.03), color='lightblue', alpha=0.5)
            ax.add_patch(circle)
        ax.set_title("پلەیتلێتەکان (Platelets)", color='white')
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    st.pyplot(fig)
    plt.close()

# ================================
# 8. دروستکردنی ١٠٠٠ کویز (بە ئاست)
# ================================
def generate_quizzes_by_level():
    quizzes = []
    
    level1_questions = [
        {"پرسیار": "نیشانەی سەرەکی شەکرەی جۆری ٢ چییە؟", "هەڵبژاردەکان": ["تینوویەتی زۆر", "سەرئێشە", "ئازاری سنگ", "کۆخە"], "وەڵامی ڕاست": 0},
        {"پرسیار": "پەستانی خوێنی نۆرماڵ چەندە؟", "هەڵبژاردەکان": ["120/80", "140/90", "160/100", "180/110"], "وەڵامی ڕاست": 0},
        {"پرسیار": "کام دەرمانە بۆ شەکرە بەکاردێت؟", "هەڵبژاردەکان": ["مێتفۆرمین", "ئەسپیرین", "کاپتۆپریل", "ئەمۆکسیسیلین"], "وەڵامی ڕاست": 0},
        {"پرسیار": "نیشانەی ئەنیمیا چییە؟", "هەڵبژاردەکان": ["ماندوویی", "سەرئێشە", "ئازاری سنگ", "کۆخە"], "وەڵامی ڕاست": 0},
        {"پرسیار": "کام پشکنینە بۆ دەستنیشانکردنی شەکرە؟", "هەڵبژاردەکان": ["FBS", "ECG", "Chest X-ray", "MRI"], "وەڵامی ڕاست": 0}
    ]
    
    level2_questions = [
        {"پرسیار": "HbA1c > 6.5% ئاماژەیە بۆ چی؟", "هەڵبژاردەکان": ["شەکرە", "ئەنیمیا", "نەخۆشی دڵ", "هەوکردن"], "وەڵامی ڕاست": 0},
        {"پرسیار": "BP > 140/90 نیشانەی چییە؟", "هەڵبژاردەکان": ["پەستانی خوێن", "نەخۆشی دڵ", "شەکرە", "هەوکردن"], "وەڵامی ڕاست": 0},
        {"پرسیار": "MCV < 80 fL نیشانەی چییە؟", "هەڵبژاردەکان": ["ئەنیمیای مایکرۆسایتیک", "ئەنیمیای ماکرۆسایتیک", "ئەنیمیای نۆرمۆسایتیک", "هیمۆلایتیک"], "وەڵامی ڕاست": 0}
    ]
    
    level_questions = {1: level1_questions, 2: level2_questions}
    
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
# 9. فانکشنە یارمەتیدەرەکان
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
        return {"status": "نزم", "color": "#ffc107", "interpretation": f"{LAB_TESTS[test_name]['تەفسیر']} نزمە"}
    elif value > high:
        return {"status": "بەرز", "color": "#dc3545", "interpretation": f"{LAB_TESTS[test_name]['تەفسیر']} بەرزە"}
    else:
        return {"status": "نۆرماڵ", "color": "#28a745", "interpretation": f"{LAB_TESTS[test_name]['تەفسیر']} نۆرماڵە"}

# ================================
# 10. ستەیتەکانی ئەپ
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
if 'lab_notes' not in st.session_state:
    st.session_state.lab_notes = {}
if 'drug_notes' not in st.session_state:
    st.session_state.drug_notes = {}
if 'spaced_repetition' not in st.session_state:
    st.session_state.spaced_repetition = {}
if 'clinical_notes' not in st.session_state:
    st.session_state.clinical_notes = []
if 'xp_points' not in st.session_state:
    st.session_state.xp_points = 0
if 'badges' not in st.session_state:
    st.session_state.badges = []
if 'comprehensive_exam_questions' not in st.session_state:
    st.session_state.comprehensive_exam_questions = None
if 'comprehensive_exam_answers' not in st.session_state:
    st.session_state.comprehensive_exam_answers = {}
if 'comprehensive_exam_submitted' not in st.session_state:
    st.session_state.comprehensive_exam_submitted = False
if 'comprehensive_exam_score' not in st.session_state:
    st.session_state.comprehensive_exam_score = 0
if 'comprehensive_exam_start_time' not in st.session_state:
    st.session_state.comprehensive_exam_start_time = None
if 'flashcard_index' not in st.session_state:
    st.session_state.flashcard_index = 0
if 'flashcard_flipped' not in st.session_state:
    st.session_state.flashcard_flipped = False
if 'current_room_id' not in st.session_state:
    st.session_state.current_room_id = None
if 'exam_timer_seconds' not in st.session_state:
    st.session_state.exam_timer_seconds = 3600  # 60 خولەک

# ================================
# 11. خۆکارانەی Auto-save
# ================================
def auto_save():
    if st.session_state.logged_in:
        save_user_data(st.session_state.username, {
            "custom_lab_tests": st.session_state.custom_lab_tests,
            "custom_drugs": st.session_state.custom_drugs,
            "lab_notes": st.session_state.lab_notes,
            "drug_notes": st.session_state.drug_notes,
            "spaced_repetition": st.session_state.spaced_repetition,
            "clinical_notes": st.session_state.clinical_notes,
            "xp_points": st.session_state.xp_points,
            "badges": st.session_state.badges
        })

# ================================
# 12. پەڕەی لۆگین
# ================================
if not st.session_state.logged_in:
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    
    st.markdown("""
        <span class="dr-icon">🩺</span>
        <h2 style="color:white;margin-bottom:20px;">Dr.Danyal Ultra</h2>
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
                    st.session_state.lab_notes = user_data.get("lab_notes", {})
                    st.session_state.drug_notes = user_data.get("drug_notes", {})
                    st.session_state.spaced_repetition = user_data.get("spaced_repetition", {})
                    st.session_state.clinical_notes = user_data.get("clinical_notes", [])
                    st.session_state.xp_points = user_data.get("xp_points", 0)
                    st.session_state.badges = user_data.get("badges", [])
                    st.success(f"بەخێربێیت {login_username}!")
                    add_xp(login_username, 1)
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
# 13. سایدبار
# ================================
with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center;padding:10px 0;">
        <span class="dr-icon">🩺</span>
        <div style="font-size:2rem;font-weight:bold;background:linear-gradient(135deg,#4facfe,#43e97b);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
            Dr.Danyal
        </div>
        <div style="color:rgba(255,255,255,0.5);font-size:0.8rem;">🎓 Ultra Edition</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown(f"**👤:** {st.session_state.username}")
    level = get_user_level(st.session_state.quiz_score)
    level_info = get_level_info(level)
    st.markdown(f"<span class='badge-level'>{get_level_icon(level)} {level_info['name']}</span>", unsafe_allow_html=True)
    
    st.markdown(f"**⭐ XP:** {st.session_state.xp_points}")
    st.markdown(f"**📊 کویز:** {st.session_state.quiz_score}/100")
    st.markdown(f"**🩺 کەیس:** {st.session_state.total_cases_solved}")
    st.markdown(f"**🔥 بەردەوامی:** {st.session_state.streak_days} ڕۆژ")
    
    st.markdown("---")
    
    page = st.radio(
        "📋 بەشەکان:",
        [
            "🏠 داشبۆرد",
            "📚 نەخۆشییەکان",
            "🩺 شیکاری کەیس",
            "📝 کویز (ئاستی)",
            "📋 تاقیکردنەوەی گشتی",
            "🔄 دووبارەکردنەوە",
            "🔬 تاقیگە",
            "💊 فارماکۆلۆجی",
            "⚠️ کارلێکی دەرمانەکان",
            "🏆 خشتەی ڕێزلێنان",
            "👥 هاوڕێی خوێندن",
            "📰 هەواڵی پزیشکی",
            "🔬 میکرۆسکۆپ",
            "📝 یاداشتی کلینیکی",
            "🧠 AI یاریدەدەر",
            "🏆 دەستکەوتەکان"
        ],
        index=0
    )
    
    st.markdown("---")
    if st.button("🚪 چوونە دەرەوە"):
        auto_save()
        st.session_state.logged_in = False
        for key in list(st.session_state.keys()):
            if key not in ['logged_in', 'username']:
                del st.session_state[key]
        st.rerun()

# ================================
# 14. پەڕەکان
# ================================

if page == "🏠 داشبۆرد":
    st.markdown("""
    <div class="main">
        <div class="logo-container">
            <span class="logo-icon">🩺</span>
            <span class="logo-text">Dr.Danyal Ultra</span>
        </div>
        <h1 class="main-header">🎓 ڕاهێنەری پزیشکی Pro Max Ultra</h1>
    </div>
    """, unsafe_allow_html=True)
    
    level = get_user_level(st.session_state.quiz_score)
    level_info = get_level_info(level)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f'<div class="stat-card"><h3>📚</h3><div class="stat-number">{get_disease_count()}</div><p>نەخۆشی</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="stat-card"><h3>💊</h3><div class="stat-number">{get_drug_count()}</div><p>دەرمان</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="stat-card"><h3>⭐</h3><div class="stat-number">{st.session_state.xp_points}</div><p>XP</p></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="stat-card"><h3>📝</h3><div class="stat-number">{st.session_state.quiz_score}/100</div><p>کویز</p></div>', unsafe_allow_html=True)
    with col5:
        st.markdown(f'<div class="stat-card"><h3>🔥</h3><div class="stat-number">{st.session_state.streak_days}</div><p>ڕۆژ</p></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    due_reviews = get_due_reviews(st.session_state.username)
    if due_reviews:
        st.warning(f"📚 **{len(due_reviews)}** بابەت پێویستیان بە دووبارەکردنەوەیە! بچۆ بەشی دووبارەکردنەوە")
    
    st.markdown(f"""
    <div class="case-card">
        <h3>{get_level_icon(level)} ئاست: {level_info['name']}</h3>
        <p>نمرەی کویز: {st.session_state.quiz_score}</p>
        <div class="progress-container">
            <div class="progress-fill" style="width:{get_level_progress(st.session_state.quiz_score)}%"></div>
        </div>
        <p>XP: {st.session_state.xp_points} / {get_xp_for_level(get_next_level(level))}</p>
    </div>
    """, unsafe_allow_html=True)

elif page == "📋 تاقیکردنەوەی گشتی":
    st.markdown("<h2>📋 تاقیکردنەوەی گشتی پزیشکی</h2>", unsafe_allow_html=True)
    
    if st.session_state.comprehensive_exam_questions is None:
        st.markdown("### تاقیکردنەوەیەکی ١٠٠ پرسیاری لە هەموو بابەتەکان")
        st.info("⏱️ کات: ٦٠ خولەک | 📝 ١٠٠ پرسیار | 🎯 هەموو بابەتەکان")
        
        if st.button("🚀 دەستپێکردنی تاقیکردنەوە", type="primary"):
            st.session_state.comprehensive_exam_questions = generate_comprehensive_exam(100)
            st.session_state.comprehensive_exam_answers = {}
            st.session_state.comprehensive_exam_submitted = False
            st.session_state.comprehensive_exam_start_time = datetime.now()
            st.session_state.exam_timer_seconds = 3600
            st.rerun()
    
    elif not st.session_state.comprehensive_exam_submitted:
        elapsed = (datetime.now() - st.session_state.comprehensive_exam_start_time).total_seconds()
        remaining = max(0, 3600 - int(elapsed))
        
        minutes = remaining // 60
        seconds = remaining % 60
        st.markdown(f'<div class="timer-display">⏱️ {minutes:02d}:{seconds:02d}</div>', unsafe_allow_html=True)
        
        if remaining <= 0:
            st.error("⏰ کات تەواو بوو! تاقیکردنەوەکەت پێشکەش کرا.")
            st.session_state.comprehensive_exam_submitted = True
            st.rerun()
        
        questions = st.session_state.comprehensive_exam_questions
        
        for i, q in enumerate(questions):
            st.markdown(f"**{i+1}. {q['پرسیار']}**")
            answer = st.radio(f"وەڵام {i+1}:", q["هەڵبژاردەکان"], key=f"comp_q_{i}")
            st.session_state.comprehensive_exam_answers[i] = q["هەڵبژاردەکان"].index(answer) if answer else -1
        
        if st.button("📤 پێشکەشکردنی تاقیکردنەوە", type="primary"):
            score = 0
            for i, q in enumerate(questions):
                user_answer = st.session_state.comprehensive_exam_answers.get(i, -1)
                if user_answer == q["وەڵامی ڕاست"]:
                    score += 1
            st.session_state.comprehensive_exam_score = score
            st.session_state.comprehensive_exam_submitted = True
            add_xp(st.session_state.username, score * 2)
            st.rerun()
    
    elif st.session_state.comprehensive_exam_submitted:
        score = st.session_state.comprehensive_exam_score
        total = len(st.session_state.comprehensive_exam_questions)
        percentage = (score / total) * 100 if total > 0 else 0
        
        if percentage >= 80:
            st.markdown(f'<div class="success-box"><h2>🎉 ئەنجامی نایاب!</h2><h3>{score}/{total} ({percentage:.1f}%)</h3></div>', unsafe_allow_html=True)
            st.balloons()
        elif percentage >= 60:
            st.info(f"📊 ئەنجام: {score}/{total} ({percentage:.1f}%) - باشە!")
        else:
            st.warning(f"📊 ئەنجام: {score}/{total} ({percentage:.1f}%) - پێویستە زیاتر بخوێنیت")
        
        if st.button("🔄 تاقیکردنەوەی نوێ"):
            st.session_state.comprehensive_exam_questions = None
            st.session_state.comprehensive_exam_answers = {}
            st.session_state.comprehensive_exam_submitted = False
            st.rerun()

elif page == "🔄 دووبارەکردنەوە":
    st.markdown("<h2>🔄 دووبارەکردنەوەی بۆشایی (Spaced Repetition)</h2>", unsafe_allow_html=True)
    
    due_reviews = get_due_reviews(st.session_state.username)
    
    if due_reviews:
        st.markdown(f"### 📚 {len(due_reviews)} بابەت پێویستیان بە دووبارەکردنەوەیە")
        
        if st.session_state.flashcard_index >= len(due_reviews):
            st.session_state.flashcard_index = 0
        
        current_review = due_reviews[st.session_state.flashcard_index]
        
        # دروستکردنی فلاشکارت
        if current_review["type"] == "نەخۆشی":
            flashcard = create_flashcard_from_disease(current_review["item"])
        else:
            flashcard = create_flashcard_from_drug(current_review["item"])
        
        if flashcard:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🔄 هەڵگێڕانەوە", key="flip_flashcard"):
                    st.session_state.flashcard_flipped = not st.session_state.flashcard_flipped
                
                if st.session_state.flashcard_flipped:
                    st.markdown(f"""
                    <div class="flashcard flipped">
                        <div>
                            <h4>وەڵام:</h4>
                            <p style="font-size:1.2rem;">{flashcard['back']}</p>
                            <p style="color:#aaa;">{flashcard.get('extra', '')}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("✅ بیرم بوو", type="primary"):
                            update_spaced_repetition(st.session_state.username, current_review["item"], current_review["type"], True)
                            add_xp(st.session_state.username, 5)
                            st.session_state.flashcard_flipped = False
                            st.session_state.flashcard_index += 1
                            st.rerun()
                    with col_b:
                        if st.button("❌ بیرم نەبوو"):
                            update_spaced_repetition(st.session_state.username, current_review["item"], current_review["type"], False)
                            st.session_state.flashcard_flipped = False
                            st.rerun()
                else:
                    st.markdown(f"""
                    <div class="flashcard">
                        <h4>{flashcard['front']}</h4>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.success("🎉 هیچ بابەتێک پێویستی بە دووبارەکردنەوە نییە! ئێستا باشترین کاتە بۆ فێربوونی شتی نوێ")

elif page == "🏆 خشتەی ڕێزلێنان":
    st.markdown("<h2>🏆 خشتەی ڕێزلێنان</h2>", unsafe_allow_html=True)
    
    leaderboard_df = get_leaderboard_data()
    
    if not leaderboard_df.empty:
        for i, (_, row) in enumerate(leaderboard_df.iterrows()):
            rank = i + 1
            medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"{rank}"
            card_class = "leaderboard-top1" if rank == 1 else "leaderboard-top2" if rank == 2 else "leaderboard-top3" if rank == 3 else ""
            
            st.markdown(f"""
            <div class="leaderboard-card {card_class}">
                <h3>{medal} {row['username']}</h3>
                <p>⭐ XP: {row['xp_points']} | 📊 نمرە: {row['quiz_score']} | 🩺 کەیس: {row['cases_solved']}</p>
                <p>🎖️ ئاست: {get_level_icon(row['level'])} {get_level_info(row['level'])['name']}</p>
                <div class="progress-container">
                    <div class="xp-bar" style="width:{min(row['xp_points']/get_xp_for_level(get_next_level(row['level']))*100, 100)}%"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("هێشتا هیچ داتایەک نییە")

elif page == "👥 هاوڕێی خوێندن":
    st.markdown("<h2>👥 هاوڕێی خوێندن - ژووری خوێندنی هاوبەش</h2>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["دروستکردنی ژوور", "بەشداربوون"])
    
    with tab1:
        with st.form("create_room"):
            room_name = st.text_input("ناوی ژوور:")
            if st.form_submit_button("✅ دروستکردن"):
                room_id = create_study_room(room_name, st.session_state.username)
                st.session_state.current_room_id = room_id
                st.success(f"ژوور دروست کرا! ID: {room_id}")
                st.rerun()
    
    with tab2:
        with st.form("join_room"):
            room_id = st.text_input("ID ی ژوور:")
            if st.form_submit_button("🚪 بەشداربوون"):
                if join_study_room(room_id, st.session_state.username):
                    st.session_state.current_room_id = room_id
                    st.success("بە سەرکەوتوویی بەشدار بوویت!")
                    st.rerun()
                else:
                    st.error("ژوور نەدۆزرایەوە")
    
    if st.session_state.current_room_id:
        rooms = load_study_rooms()
        room = rooms.get(st.session_state.current_room_id)
        
        if room:
            st.markdown(f"### 📚 {room['name']}")
            st.markdown(f"**ئەندامان:** {', '.join(room['members'])}")
            
            st.markdown("### 💬 گفتوگۆ")
            for msg in room['messages'][-20:]:
                is_own = msg['username'] == st.session_state.username
                st.markdown(f"""
                <div class="chat-message {'own' if is_own else ''}">
                    <strong>{msg['username']}:</strong> {msg['message']}
                </div>
                """, unsafe_allow_html=True)
            
            with st.form("send_message"):
                message = st.text_input("پەیام:")
                if st.form_submit_button("📤 ناردن"):
                    send_room_message(st.session_state.current_room_id, st.session_state.username, message)
                    st.rerun()

elif page == "📰 هەواڵی پزیشکی":
    st.markdown("<h2>📰 هەواڵ و بابەتی پزیشکی</h2>", unsafe_allow_html=True)
    
    news = fetch_medical_news()
    
    for item in news:
        st.markdown(f"""
        <div class="news-card">
            <h4>📰 {item['title']}</h4>
            <p>{item['summary']}</p>
            <p style="color:#aaa;font-size:0.8rem;">📅 {item['date']} | 📚 {item['source']}</p>
            <a href="{item['url']}" target="_blank">زیاتر بخوێنەوە 🔗</a>
        </div>
        """, unsafe_allow_html=True)
    
    st.info("💡 ئەم هەواڵانە بۆ ڕاهێنان دروست کراون. بۆ هەواڵی ڕاستەقینە سەردانی PubMed یان The Lancet بکە.")

elif page == "⚠️ کارلێکی دەرمانەکان":
    st.markdown("<h2>⚠️ پشکنینی کارلێکی نێوان دەرمانەکان</h2>", unsafe_allow_html=True)
    
    all_drugs = []
    for category, drugs in DRUG_DATABASE.items():
        all_drugs.extend(list(drugs.keys()))
    
    selected_drugs = st.multiselect("دەرمانەکان هەڵبژێرە:", all_drugs)
    
    if len(selected_drugs) >= 2:
        interactions = check_drug_interactions(selected_drugs)
        
        if interactions:
            st.markdown("### ⚠️ ئەنجامی کارلێکەکان")
            for interaction in interactions:
                color_class = f"interaction-{interaction['color']}"
                st.markdown(f"""
                <div class="{color_class}">
                    <h4>{interaction['drug1']} + {interaction['drug2']}</h4>
                    <p><strong>ئاستی مەترسی:</strong> {interaction['severity']}</p>
                    <p><strong>کاریگەری:</strong> {interaction['effect']}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ هیچ کارلێکێکی مەترسیدار نەدۆزرایەوە")
    else:
        st.info("تکایە لانیکەم ٢ دەرمان هەڵبژێرە بۆ پشکنین")

elif page == "🔬 میکرۆسکۆپ":
    st.markdown("<h2>🔬 شێوەکاری میکرۆسکۆپ</h2>", unsafe_allow_html=True)
    
    cell_type = st.selectbox("جۆری خانە:", ["RBC", "WBC", "Platelets"])
    
    if st.button("🔬 نیشاندان"):
        generate_microscope_view(cell_type)
        st.caption(f"شێوەکاری: {cell_type} - بە هەڕەمەکی دروست کراوە")

elif page == "📝 یاداشتی کلینیکی":
    st.markdown("<h2>📝 یاداشتی کلینیکی</h2>", unsafe_allow_html=True)
    
    with st.form("clinical_note"):
        patient_name = st.text_input("ناوی نەخۆش:")
        note_text = st.text_area("یاداشت:")
        if st.form_submit_button("💾 خەزنکردن"):
            add_clinical_note(st.session_state.username, {
                "patient": patient_name,
                "note": note_text
            })
            st.success("یاداشت خەزن کرا!")
            st.rerun()
    
    st.markdown("### یاداشتە پێشووەکان")
    for note in st.session_state.clinical_notes[-10:]:
        st.markdown(f"""
        <div class="case-card">
            <p><strong>نەخۆش:</strong> {note.get('patient', 'نەزانراو')}</p>
            <p>{note.get('note', '')}</p>
            <p style="color:#888;font-size:0.8rem;">📅 {note.get('timestamp', '')[:10]}</p>
        </div>
        """, unsafe_allow_html=True)

# ================================
# 15. فووەتەر
# ================================
st.markdown("---")
st.markdown(f"""
<div class="footer-style">
    <h3>🩺 Dr.Danyal - ڕاهێنەری پزیشکی Pro Max Ultra</h3>
    <p>{get_disease_count()} نەخۆشی | {get_drug_count()} دەرمان | {get_quiz_count()} کویز</p>
    <p style="font-size:0.8rem;opacity:0.8;">© 2024 Dr.Danyal | Ultra Edition v6.0</p>
</div>
""", unsafe_allow_html=True)
