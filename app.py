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
SPACED_REPETITION_FILE = os.path.join(DATA_DIR, "spaced_repetition.json")
CLINICAL_NOTES_FILE = os.path.join(DATA_DIR, "clinical_notes.json")

def hash_password(password: str) -> str:
    """هێشکردنی وشەی نهێنی بە شێوازی SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_json_file(filepath: str, default: any) -> any:
    """بارکردنی هەر فایلێکی JSON"""
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return default
    return default

def save_json_file(filepath: str, data: any):
    """خەزنکردنی داتا لە فایلی JSON"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_users() -> Dict:
    """بارکردنی زانیاری بەکارهێنەران"""
    return load_json_file(USERS_FILE, {})

def save_users(users: Dict):
    """خەزنکردنی زانیاری بەکارهێنەران"""
    save_json_file(USERS_FILE, users)

def load_leaderboard() -> List:
    """بارکردنی خشتەی ڕێزلێنان"""
    return load_json_file(LEADERBOARD_FILE, [])

def save_leaderboard(data: List):
    """خەزنکردنی خشتەی ڕێزلێنان"""
    save_json_file(LEADERBOARD_FILE, data)

def load_study_rooms() -> Dict:
    """بارکردنی ژوورەکانی خوێندن"""
    return load_json_file(STUDY_ROOMS_FILE, {})

def save_study_rooms(data: Dict):
    """خەزنکردنی ژوورەکانی خوێندن"""
    save_json_file(STUDY_ROOMS_FILE, data)

def load_spaced_repetition() -> Dict:
    """بارکردنی داتای دووبارەکردنەوەی بۆشایی"""
    return load_json_file(SPACED_REPETITION_FILE, {})

def save_spaced_repetition(data: Dict):
    """خەزنکردنی داتای دووبارەکردنەوەی بۆشایی"""
    save_json_file(SPACED_REPETITION_FILE, data)

def load_clinical_notes() -> Dict:
    """بارکردنی یاداشتە کلینیکییەکان"""
    return load_json_file(CLINICAL_NOTES_FILE, {})

def save_clinical_notes(data: Dict):
    """خەزنکردنی یاداشتە کلینیکییەکان"""
    save_json_file(CLINICAL_NOTES_FILE, data)

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
        "total_study_time": 0,
        "level": 1,
        "xp_points": 0,
        "badges": [],
        "daily_streak": 0,
        "last_login": datetime.now().isoformat(),
        "comprehensive_exams": [],
        "quiz_history": []
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
        "badges": [],
        "last_active": datetime.now().isoformat()
    })
    save_leaderboard(leaderboard)
    
    # دروستکردنی داتای دووبارەکردنەوەی بۆشایی
    sr_data = load_spaced_repetition()
    sr_data[username] = {}
    save_spaced_repetition(sr_data)
    
    # دروستکردنی یاداشتە کلینیکییەکان
    clinical_notes = load_clinical_notes()
    clinical_notes[username] = []
    save_clinical_notes(clinical_notes)
    
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
    """زیادکردنی XP بۆ بەکارهێنەر"""
    update_leaderboard(username, xp=points)
    users = load_users()
    if username in users:
        users[username]["xp_points"] = users[username].get("xp_points", 0) + points
        save_users(users)

def update_user_streak(username: str):
    """نوێکردنەوەی بەردەوامی بەکارهێنەر"""
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
    
    .stSelectbox > div > div,
    .stTextInput > div > div,
    .stTextArea > div > div,
    .stNumberInput > div > div {
        background: rgba(255, 255, 255, 0.06) !important;
        border: 1px solid rgba(79, 172, 254, 0.2) !important;
        border-radius: 14px !important;
        transition: all 0.3s ease !important;
    }
    
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
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 15px 35px rgba(67, 233, 123, 0.45) !important;
        color: #0a1929 !important;
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%) !important;
        box-shadow: 0 8px 25px rgba(67, 233, 123, 0.35) !important;
        color: #0a1929 !important;
    }
    
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
        50% { transform: scale(1.05); text-shadow: 0 0 40px rgba(102,126,234,0.6); }
        100% { transform: scale(1); text-shadow: 0 0 20px rgba(102,126,234,0.3); }
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
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
        border: 1px solid rgba(255, 255, 255, 0.15);
        text-shadow: 0 4px 20px rgba(0,0,0,0.3);
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
        border-left: 8px solid #667eea;
        margin: 1.2rem 0;
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        border: 1px solid rgba(255, 255, 255, 0.06);
        animation: slideInLeft 0.6s ease-out;
        color: #fff;
    }
    
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-50px); }
        to { opacity: 1; transform: translateX(0); }
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
        background: linear-gradient(90deg, #667eea, #764ba2, #f093fb, #4facfe, #667eea);
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
        border-top: 6px solid #667eea;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        color: #fff;
        border: 1px solid rgba(255, 255, 255, 0.04);
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
        background: linear-gradient(135deg, #667eea, #f093fb);
        color: white;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        animation: pulse 3s infinite;
        font-size: 1.2rem;
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
        border-color: #764ba2;
        box-shadow: 0 15px 50px rgba(102, 126, 234, 0.2);
        background: rgba(255, 255, 255, 0.1);
    }
    
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
        border-left: 4px solid #667eea;
        transition: all 0.3s ease;
    }
    
    .lab-result-card:hover {
        background: rgba(0, 0, 0, 0.3);
        transform: translateX(5px);
    }
    
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
    
    .leaderboard-card {
        background: rgba(255, 215, 0, 0.08);
        backdrop-filter: blur(15px);
        padding: 1.5rem;
        border-radius: 20px;
        border: 2px solid rgba(255, 215, 0, 0.2);
        margin: 0.8rem 0;
        animation: leaderboardSlide 0.5s ease-out;
    }
    
    @keyframes leaderboardSlide {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .leaderboard-card:hover {
        transform: scale(1.02);
        box-shadow: 0 10px 40px rgba(255, 215, 0, 0.2);
    }
    
    .leaderboard-top1 { border-color: #ffd700 !important; background: rgba(255, 215, 0, 0.15) !important; }
    .leaderboard-top2 { border-color: #c0c0c0 !important; background: rgba(192, 192, 192, 0.1) !important; }
    .leaderboard-top3 { border-color: #cd7f32 !important; background: rgba(205, 127, 50, 0.1) !important; }
    
    .xp-bar {
        background: linear-gradient(90deg, #ffd700, #ffb900, #ff9500);
        height: 15px;
        border-radius: 10px;
        transition: width 0.5s ease;
    }
    
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
    }
    
    .flashcard:hover {
        transform: rotateY(5deg);
        box-shadow: 0 15px 50px rgba(102, 126, 234, 0.3);
    }
    
    .flashcard.flipped {
        transform: rotateY(180deg);
        background: rgba(102, 126, 234, 0.15);
    }
    
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
    
    .timer-display {
        font-size: 3rem;
        font-weight: bold;
        color: #ff6b6b;
        text-align: center;
        animation: pulse 1s infinite;
    }
    
    .risk-high { color: #ff6b6b; font-weight: bold; }
    .risk-medium { color: #ffd93d; font-weight: bold; }
    .risk-low { color: #6bcb77; font-weight: bold; }
    
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
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    @media (max-width: 768px) {
        .main-header { font-size: 2.2rem; padding: 1.2rem; }
        .stat-number { font-size: 2.8rem; }
        .stat-card { padding: 1rem; }
        .logo-text { font-size: 1.5rem; }
        .logo-icon { font-size: 2.5rem; }
        .dr-icon { font-size: 2.5rem; }
    }
</style>
""", unsafe_allow_html=True)

# ================================
# 3. سیستەمی ئاستەکان (Levels)
# ================================
LEVELS = {
    1: {"name": "سەرەتایی (Beginner)", "min_score": 0, "max_score": 9, "color": "#28a745", "quizzes": 50, "icon": "🌱", "description": "دەستپێکی ڕێگای پزیشکی", "requirements": "هیچ", "xp_required": 0},
    2: {"name": "فێرخواز (Learner)", "min_score": 10, "max_score": 29, "color": "#17a2b8", "quizzes": 100, "icon": "📖", "description": "فێربوونی بنەماکانی پزیشکی", "requirements": "تەواوکردنی ئاست ١", "xp_required": 100},
    3: {"name": "پێشکەوتوو (Advanced)", "min_score": 30, "max_score": 59, "color": "#ffc107", "quizzes": 150, "icon": "🚀", "description": "پێشکەوتن لە زانستە پزیشکییەکان", "requirements": "تەواوکردنی ئاست ٢", "xp_required": 300},
    4: {"name": "شارەزا (Expert)", "min_score": 60, "max_score": 89, "color": "#ff9f1c", "quizzes": 200, "icon": "🏆", "description": "شارەزایی لە نەخۆشییەکان", "requirements": "تەواوکردنی ئاست ٣", "xp_required": 600},
    5: {"name": "پزیشک (Master)", "min_score": 90, "max_score": 100, "color": "#dc3545", "quizzes": 500, "icon": "👨‍⚕️", "description": "پزیشکی لێهاتوو و شارەزا", "requirements": "تەواوکردنی ئاست ٤", "xp_required": 1000},
    6: {"name": "پڕۆفیسۆر (Professor)", "min_score": 100, "max_score": 150, "color": "#9b59b6", "quizzes": 750, "icon": "🎓", "description": "ئاستی پڕۆفیسۆری پزیشکی", "requirements": "تەواوکردنی ئاست ٥ + ٢٠٠٠ XP", "xp_required": 2000},
    7: {"name": "ئەفسانە (Legend)", "min_score": 150, "max_score": 999, "color": "#e74c3c", "quizzes": 1000, "icon": "👑", "description": "ئاستی ئەفسانەیی - گەیشتوویتە لوتکە!", "requirements": "تەواوکردنی ئاست ٦ + ٥٠٠٠ XP", "xp_required": 5000}
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
    if level >= 7: return 100.0
    current = LEVELS[level]
    next_level = get_next_level(level)
    total = LEVELS[next_level]["min_score"] - current["min_score"]
    achieved = score - current["min_score"]
    return min((achieved / total) * 100, 100) if total > 0 else 100

def get_level_icon(level: int) -> str:
    return LEVELS.get(level, LEVELS[1])["icon"]

def get_xp_for_level(level: int) -> int:
    return LEVELS.get(level, LEVELS[1]).get("xp_required", 0)

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
    "شەکرەی حەملی دووگانی": {
        "نیشانەکان": ["تینوویەتی زۆر", "میزی زۆر", "ماندوویی", "هەستی بەمەزە", "هەستی بێهێزی"],
        "پشکنینەکان": {"FBS": ">126 mg/dL", "OGTT": ">200 mg/dL", "HbA1c": ">6.5%"},
        "چارەسەر": ["گۆڕینی شێوازی ژیان", "ئەنسولین (ئەگەر پێویست)", "پێوانەکردنی شەکر", "شێوازی خواردن"],
        "ئاستی مەترسی": "مەترسیدار",
        "تایبەتمەندی": "حەمل + شەکر",
        "ڕێپیشگیری": ["پێشکەشکردنی شەکر لە حەملی پێشوو", "پێوانەکردنی شەکر"],
        "گروپی تەمەن": "ژنانی حەملی",
        "ڕێژەی تووشبوون": "7%",
        "جۆری نەخۆشی": "مێتابۆلیک",
        "دەگمەن": False
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
        "جۆری نەخۆشی": "دڵ و خوێن",
        "دەگمەن": False
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
        "جۆری نەخۆشی": "هەوکردن",
        "دەگمەن": False
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
        "جۆری نەخۆشی": "هەوکردن",
        "دەگمەن": False
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
        "جۆری نەخۆشی": "خوێن",
        "دەگمەن": False
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
        "جۆری نەخۆشی": "خوێن",
        "دەگمەن": False
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
        "جۆری نەخۆشی": "خوێن",
        "دەگمەن": False
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
        "جۆری نەخۆشی": "خوێن",
        "دەگمەن": False
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
        "جۆری نەخۆشی": "خوێن",
        "دەگمەن": False
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
        "جۆری نەخۆشی": "گورچیلە",
        "دەگمەن": False
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
        "جۆری نەخۆشی": "گورچیلە",
        "دەگمەن": False
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
        "جۆری نەخۆشی": "گورچیلە",
        "دەگمەن": False
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
        "جۆری نەخۆشی": "جگەر",
        "دەگمەن": False
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
        "جۆری نەخۆشی": "جگەر",
        "دەگمەن": False
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
        "جۆری نەخۆشی": "جگەر",
        "دەگمەن": False
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
        "جۆری نەخۆشی": "جگەر",
        "دەگمەن": False
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
        "جۆری نەخۆشی": "جگەر",
        "دەگمەن": False
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
        "جۆری نەخۆشی": "جگەر",
        "دەگمەن": False
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
        "جۆری نەخۆشی": "هەناسە",
        "دەگمەن": False
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
        "جۆری نەخۆشی": "هەناسە",
        "دەگمەن": False
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
        "جۆری نەخۆشی": "هەناسە",
        "دەگمەن": False
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
        "جۆری نەخۆشی": "هەوکردن",
        "دەگمەن": False
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
        "جۆری نەخۆشی": "هەوکردن",
        "دەگمەن": False
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
        "جۆری نەخۆشی": "پەنکریاس",
        "دەگمەن": False
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
        "جۆری نەخۆشی": "گەدە",
        "دەگمەن": False
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
        "جۆری نەخۆشی": "گەدە",
        "دەگمەن": False
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
        "جۆری نەخۆشی": "دەمار",
        "دەگمەن": False
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
        "جۆری نەخۆشی": "دەمار",
        "دەگمەن": False
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
        "جۆری نەخۆشی": "دەمار",
        "دەگمەن": False
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
        "جۆری نەخۆشی": "دەمار",
        "دەگمەن": False
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
        "جۆری نەخۆشی": "دەمار",
        "دەگمەن": False
    },
    "نەخۆشی فابری (Fabry Disease)": {
        "نیشانەکان": ["ئازاری دەست و پێ", "کەمبوونی ئارەقە", "پێستی سوور", "کێشەکانی گورچیلە", "کێشەکانی دڵ"],
        "پشکنینەکان": {"Alpha-Gal A": "نزم", "Genetic test": "GLA mutation", "Urine GL-3": "بەرز"},
        "چارەسەر": ["Enzyme replacement", "Agalsidase beta", "دەرمانی ئازار"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندی": "Alpha-Gal A نزم + GLA mutation",
        "ڕێپیشگیری": ["پشکنینی بۆماوەیی", "چارەسەری زوو"],
        "گروپی تەمەن": "گەنجان",
        "ڕێژەی تووشبوون": "0.001%",
        "جۆری نەخۆشی": "دەگمەن",
        "دەگمەن": True
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
    "MCH": {"گروپ": "خوێن", "نۆرماڵ": (27, 33), "یەکە": "pg", "تەفسیر": "کەمی هیمۆگلۆبین", "ئامێر": "ئۆتۆماتیک سێل کاونتر (Sysmex XN-9000)", "تێبینی": ""},
    "MCHC": {"گروپ": "خوێن", "نۆرماڵ": (32, 36), "یەکە": "g/dL", "تەفسیر": "چڕی هیمۆگلۆبین", "ئامێر": "ئۆتۆماتیک سێل کاونتر (Sysmex XN-9000)", "تێبینی": ""},
    "RDW": {"گروپ": "خوێن", "نۆرماڵ": (11.5, 14.5), "یەکە": "%", "تەفسیر": "جیاوازی قەبارە", "ئامێر": "ئۆتۆماتیک سێل کاونتر (Sysmex XN-9000)", "تێبینی": ""},
    "Reticulocyte": {"گروپ": "خوێن", "نۆرماڵ": (0.5, 2.5), "یەکە": "%", "تەفسیر": "خڕۆکە نوێکان", "ئامێر": "فلۆ سایتمیتەر (BD FACSCalibur)", "تێبینی": ""},
    "Ferritin": {"گروپ": "خوێن", "نۆرماڵ": (15, 300), "یەکە": "ng/mL", "تەفسیر": "ئاسن", "ئامێر": "کیمیایی ئیمینۆ (Roche Cobas e411)", "تێبینی": ""},
    "TIBC": {"گروپ": "خوێن", "نۆرماڵ": (250, 450), "یەکە": "mcg/dL", "تەفسیر": "ئاسن", "ئامێر": "کیمیایی ئیمینۆ (Roche Cobas c502)", "تێبینی": ""},
    "Iron": {"گروپ": "خوێن", "نۆرماڵ": (60, 170), "یەکە": "mcg/dL", "تەفسیر": "ئاسن", "ئامێر": "کیمیایی ئیمینۆ (Roche Cobas c502)", "تێبینی": ""},
    "Vitamin B12": {"گروپ": "خوێن", "نۆرماڵ": (200, 900), "یەکە": "pg/mL", "تەفسیر": "ڤیتامین B12", "ئامێر": "کیمیایی ئیمینۆ (Roche Cobas e411)", "تێبینی": ""},
    "Folate": {"گروپ": "خوێن", "نۆرماڵ": (3, 17), "یەکە": "ng/mL", "تەفسیر": "فۆلیک ئەسید", "ئامێر": "کیمیایی ئیمینۆ (Roche Cobas e411)", "تێبینی": ""},
    "LDH": {"گروپ": "خوێن", "نۆرماڵ": (100, 250), "یەکە": "U/L", "تەفسیر": "ئەنزیم", "ئامێر": "سپێکترۆفۆتۆمیتەر (Beckman Coulter AU480)", "تێبینی": ""},
    "Haptoglobin": {"گروپ": "خوێن", "نۆرماڵ": (50, 250), "یەکە": "mg/dL", "تەفسیر": "پروتێین", "ئامێر": "نێفێلۆمیتەر (Siemens BNII)", "تێبینی": ""},
    "ESR": {"گروپ": "خوێن", "نۆرماڵ": (0, 20), "یەکە": "mm/hr", "تەفسیر": "خێرایی تەنیشتن", "ئامێر": "ESR ئۆتۆماتیک (Ves-Matic 20)", "تێبینی": ""},
    "CRP": {"گروپ": "خوێن", "نۆرماڵ": (0, 5), "یەکە": "mg/L", "تەفسیر": "پروتێینی هەوکردن", "ئامێر": "توربیدیمیتەر (Roche Cobas c502)", "تێبینی": ""},
    "Procalcitonin": {"گروپ": "خوێن", "نۆرماڵ": (0, 0.5), "یەکە": "ng/mL", "تەفسیر": "هەوکردنی بەکتریایی", "ئامێر": "کیمیایی ئیمینۆ (Roche Cobas e411)", "تێبینی": ""},
    "Interleukin-6": {"گروپ": "خوێن", "نۆرماڵ": (0, 5), "یەکە": "pg/mL", "تەفسیر": "سایتۆکاینی هەوکردن", "ئامێر": "ELISA Reader (BioTek 800TS)", "تێبینی": ""},
    "TNF-alpha": {"گروپ": "خوێن", "نۆرماڵ": (0, 8), "یەکە": "pg/mL", "تەفسیر": "سایتۆکاینی هەوکردن", "ئامێر": "ELISA Reader (BioTek 800TS)", "تێبینی": ""}
}

biochem_tests = {
    "Glucose": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (70, 126), "یەکە": "mg/dL", "تەفسیر": "شەکری خوێن", "ئامێر": "گلوکۆمیتەر (Roche Cobas c502)", "تێبینی": ""},
    "HbA1c": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (4.0, 5.6), "یەکە": "%", "تەفسیر": "شەکری درێژخایەن", "ئامێر": "HPLC (Bio-Rad D-100)", "تێبینی": ""},
    "Creatinine": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (0.6, 1.3), "یەکە": "mg/dL", "تەفسیر": "کارایی گورچیلە", "ئامێر": "سپێکترۆفۆتۆمیتەر (Roche Cobas c502)", "تێبینی": ""},
    "BUN": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (7, 20), "یەکە": "mg/dL", "تەفسیر": "نایترۆجینی یوریا", "ئامێر": "سپێکترۆفۆتۆمیتەر (Roche Cobas c502)", "تێبینی": ""},
    "ALT": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (10, 40), "یەکە": "U/L", "تەفسیر": "ئەنزیمی جگەر", "ئامێر": "سپێکترۆفۆتۆمیتەر (Roche Cobas c502)", "تێبینی": ""},
    "AST": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (10, 40), "یەکە": "U/L", "تەفسیر": "ئەنزیمی جگەر", "ئامێر": "سپێکترۆفۆتۆمیتەر (Roche Cobas c502)", "تێبینی": ""},
    "Bilirubin": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (0.1, 1.2), "یەکە": "mg/dL", "تەفسیر": "زەرداوی", "ئامێر": "سپێکترۆفۆتۆمیتەر (Roche Cobas c502)", "تێبینی": ""},
    "Albumin": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (3.5, 5.0), "یەکە": "g/dL", "تەفسیر": "ئەلبومین", "ئامێر": "سپێکترۆفۆتۆمیتەر (Roche Cobas c502)", "تێبینی": ""},
    "Potassium": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (3.5, 5.0), "یەکە": "mmol/L", "تەفسیر": "پۆتاسیۆم", "ئامێر": "ئایۆن سەلێکت یوڤ ئەنالایزەر (Roche Cobas c502)", "تێبینی": ""},
    "Sodium": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (135, 145), "یەکە": "mmol/L", "تەفسیر": "سۆدیۆم", "ئامێر": "ئایۆن سەلێکت یوڤ ئەنالایزەر (Roche Cobas c502)", "تێبینی": ""},
    "Calcium": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (8.5, 10.5), "یەکە": "mg/dL", "تەفسیر": "کالسیۆم", "ئامێر": "سپێکترۆفۆتۆمیتەر (Roche Cobas c502)", "تێبینی": ""},
    "Phosphorus": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (2.5, 4.5), "یەکە": "mg/dL", "تەفسیر": "فۆسفۆر", "ئامێر": "سپێکترۆفۆتۆمیتەر (Roche Cobas c502)", "تێبینی": ""},
    "Magnesium": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (1.7, 2.5), "یەکە": "mg/dL", "تەفسیر": "مەگنیسیۆم", "ئامێر": "سپێکترۆفۆتۆمیتەر (Roche Cobas c502)", "تێبینی": ""},
    "Amylase": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (20, 200), "یەکە": "U/L", "تەفسیر": "ئەنزیمی پەنکریاس", "ئامێر": "سپێکترۆفۆتۆمیتەر (Roche Cobas c502)", "تێبینی": ""},
    "Lipase": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (20, 200), "یەکە": "U/L", "تەفسیر": "ئەنزیمی پەنکریاس", "ئامێر": "سپێکترۆفۆتۆمیتەر (Roche Cobas c502)", "تێبینی": ""},
    "Cholesterol": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (0, 200), "یەکە": "mg/dL", "تەفسیر": "کۆلسترۆل", "ئامێر": "سپێکترۆفۆتۆمیتەر (Roche Cobas c502)", "تێبینی": ""},
    "LDL": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (0, 100), "یەکە": "mg/dL", "تەفسیر": "کۆلسترۆلی خراپ", "ئامێر": "سپێکترۆفۆتۆمیتەر (Roche Cobas c502)", "تێبینی": ""},
    "HDL": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (40, 60), "یەکە": "mg/dL", "تەفسیر": "کۆلسترۆلی باش", "ئامێر": "سپێکترۆفۆتۆمیتەر (Roche Cobas c502)", "تێبینی": ""},
    "Triglycerides": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (0, 150), "یەکە": "mg/dL", "تەفسیر": "تریگلیسیرید", "ئامێر": "سپێکترۆفۆتۆمیتەر (Roche Cobas c502)", "تێبینی": ""},
    "Total Protein": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (6.0, 8.0), "یەکە": "g/dL", "تەفسیر": "پڕۆتینی گشتی", "ئامێر": "سپێکترۆفۆتۆمیتەر (Roche Cobas c502)", "تێبینی": ""}
}

cardiac_tests = {
    "Troponin I": {"گروپ": "دڵ", "نۆرماڵ": (0, 0.04), "یەکە": "ng/mL", "تەفسیر": "پروتێینی دڵ", "ئامێر": "کیمیایی ئیمینۆ (Roche Cobas e411)", "تێبینی": ""},
    "Troponin T": {"گروپ": "دڵ", "نۆرماڵ": (0, 0.014), "یەکە": "ng/mL", "تەفسیر": "پروتێینی دڵ", "ئامێر": "کیمیایی ئیمینۆ (Roche Cobas e411)", "تێبینی": ""},
    "CK-MB": {"گروپ": "دڵ", "نۆرماڵ": (0, 5), "یەکە": "ng/mL", "تەفسیر": "ئەنزیمی دڵ", "ئامێر": "کیمیایی ئیمینۆ (Roche Cobas e411)", "تێبینی": ""},
    "BNP": {"گروپ": "دڵ", "نۆرماڵ": (0, 100), "یەکە": "pg/mL", "تەفسیر": "پروتێینی دڵ", "ئامێر": "کیمیایی ئیمینۆ (Roche Cobas e411)", "تێبینی": ""},
    "Myoglobin": {"گروپ": "دڵ", "نۆرماڵ": (0, 80), "یەکە": "ng/mL", "تەفسیر": "پروتێین", "ئامێر": "کیمیایی ئیمینۆ (Roche Cobas e411)", "تێبینی": ""},
    "HS-CRP": {"گروپ": "دڵ", "نۆرماڵ": (0, 2), "یەکە": "mg/L", "تەفسیر": "هەوکردنی دڵ", "ئامێر": "توربیدیمیتەر (Roche Cobas c502)", "تێبینی": ""},
    "Homocysteine": {"گروپ": "دڵ", "نۆرماڵ": (5, 15), "یەکە": "μmol/L", "تەفسیر": "مەترسی دڵ", "ئامێر": "HPLC (Agilent 1200)", "تێبینی": ""},
    "ApoB": {"گروپ": "دڵ", "نۆرماڵ": (60, 120), "یەکە": "mg/dL", "تەفسیر": "پرۆتێین", "ئامێر": "نێفێلۆمیتەر (Siemens BNII)", "تێبینی": ""},
    "ApoA": {"گروپ": "دڵ", "نۆرماڵ": (90, 150), "یەکە": "mg/dL", "تەفسیر": "پرۆتێین", "ئامێر": "نێفێلۆمیتەر (Siemens BNII)", "تێبینی": ""},
    "Lipoprotein(a)": {"گروپ": "دڵ", "نۆرماڵ": (0, 30), "یەکە": "mg/dL", "تەفسیر": "مەترسی دڵ", "ئامێر": "نێفێلۆمیتەر (Siemens BNII)", "تێبینی": ""}
}

hormone_tests = {
    "TSH": {"گروپ": "هۆرمۆن", "نۆرماڵ": (0.4, 4.0), "یەکە": "mIU/L", "تەفسیر": "هۆرمۆنی دروان", "ئامێر": "کیمیایی ئیمینۆ (Roche Cobas e411)", "تێبینی": ""},
    "T4": {"گروپ": "هۆرمۆن", "نۆرماڵ": (5, 12), "یەکە": "μg/dL", "تەفسیر": "هۆرمۆنی دروان", "ئامێر": "کیمیایی ئیمینۆ (Roche Cobas e411)", "تێبینی": ""},
    "T3": {"گروپ": "هۆرمۆن", "نۆرماڵ": (80, 200), "یەکە": "ng/dL", "تەفسیر": "هۆرمۆنی دروان", "ئامێر": "کیمیایی ئیمینۆ (Roche Cobas e411)", "تێبینی": ""},
    "Cortisol": {"گروپ": "هۆرمۆن", "نۆرماڵ": (5, 25), "یەکە": "μg/dL", "تەفسیر": "هۆرمۆنی پەستانی خوێن", "ئامێر": "کیمیایی ئیمینۆ (Roche Cobas e411)", "تێبینی": ""},
    "Insulin": {"گروپ": "هۆرمۆن", "نۆرماڵ": (2, 25), "یەکە": "μIU/mL", "تەفسیر": "هۆرمۆنی شەکر", "ئامێر": "کیمیایی ئیمینۆ (Roche Cobas e411)", "تێبینی": ""},
    "C-peptide": {"گروپ": "هۆرمۆن", "نۆرماڵ": (0.5, 2.0), "یەکە": "ng/mL", "تەفسیر": "پێکهاتەی ئەنسولین", "ئامێر": "کیمیایی ئیمینۆ (Roche Cobas e411)", "تێبینی": ""},
    "Testosterone": {"گروپ": "هۆرمۆن", "نۆرماڵ": (300, 1000), "یەکە": "ng/dL", "تەفسیر": "هۆرمۆنی نێر", "ئامێر": "کیمیایی ئیمینۆ (Roche Cobas e411)", "تێبینی": ""},
    "Estradiol": {"گروپ": "هۆرمۆن", "نۆرماڵ": (20, 400), "یەکە": "pg/mL", "تەفسیر": "هۆرمۆنی مێ", "ئامێر": "کیمیایی ئیمینۆ (Roche Cobas e411)", "تێبینی": ""}
}

urine_tests = {
    "Urine Protein": {"گروپ": "میز", "نۆرماڵ": (0, 0.3), "یەکە": "g/24h", "تەفسیر": "پڕۆتینی میز", "ئامێر": "سپێکترۆفۆتۆمیتەر (Roche Cobas c502)", "تێبینی": ""},
    "Urine Glucose": {"گروپ": "میز", "نۆرماڵ": (0, 0), "یەکە": "mg/dL", "تەفسیر": "شەکری میز", "ئامێر": "سپێکترۆفۆتۆمیتەر (Roche Cobas c502)", "تێبینی": ""},
    "Urine WBC": {"گروپ": "میز", "نۆرماڵ": (0, 5), "یەکە": "/HPF", "تەفسیر": "خڕۆکە سپیەکان", "ئامێر": "مایکرۆسکۆپی (Olympus CX23)", "تێبینی": ""},
    "Urine RBC": {"گروپ": "میز", "نۆرماڵ": (0, 3), "یەکە": "/HPF", "تەفسیر": "خڕۆکە سوورەکان", "ئامێر": "مایکرۆسکۆپی (Olympus CX23)", "تێبینی": ""}
}

vitamin_tests = {
    "Vitamin D": {"گروپ": "ڤیتامین", "نۆرماڵ": (30, 100), "یەکە": "ng/mL", "تەفسیر": "ڤیتامین D", "ئامێر": "کیمیایی ئیمینۆ (Roche Cobas e411)", "تێبینی": ""},
    "Vitamin A": {"گروپ": "ڤیتامین", "نۆرماڵ": (20, 80), "یەکە": "μg/dL", "تەفسیر": "ڤیتامین A", "ئامێر": "HPLC (Agilent 1200)", "تێبینی": ""},
    "Vitamin E": {"گروپ": "ڤیتامین", "نۆرماڵ": (5, 18), "یەکە": "mg/L", "تەفسیر": "ڤیتامین E", "ئامێر": "HPLC (Agilent 1200)", "تێبینی": ""}
}

for test_dict in [blood_tests, biochem_tests, cardiac_tests, hormone_tests, urine_tests, vitamin_tests]:
    LAB_TESTS.update(test_dict)

# ================================
# 6. داتابەسی دەرمانەکان (١٢٠+ دەرمان)
# ================================
DRUG_DATABASE = {
    "دژە پەستانی خوێن": {
        "کاپتۆپریل": {"ڕێژە": "25-50mg", "میکانیزم": "ACE inhibitor", "کاریگەری لاوەکی": "کۆخە, سەرگێژخواردن", "پێچەوانە": "حەملی دووگانی", "وەسف": "دەرمانی ACE inhibitor کە پەستانی خوێن کەم دەکاتەوە بە فراوانکردنی خوێنبەرەکان", "بۆچی": "بۆ کەمکردنەوەی پەستانی خوێن و پاراستنی گورچیلە لە نەخۆشانی شەکرە", "تێبینی": ""},
        "ئەملۆدیپین": {"ڕێژە": "5-10mg", "میکانیزم": "Calcium channel blocker", "کاریگەری لاوەکی": "ئاوسانی قاچ", "پێچەوانە": "هەستیاری", "وەسف": "بەربەستەری کالسیۆم کە خوێنبەرەکان فراوان دەکات", "بۆچی": "بۆ چارەسەری پەستانی خوێنی بەرز و ئازاری سنگ", "تێبینی": ""},
        "لۆسارتان": {"ڕێژە": "50-100mg", "میکانیزم": "ARB", "کاریگەری لاوەکی": "سەرگێژخواردن", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "بەربەستەری گیرۆدەی ئەنجیۆتێنسین", "بۆچی": "بۆ چارەسەری پەستانی خوێن و پاراستنی گورچیلە", "تێبینی": ""},
        "بایسۆپرۆلۆل": {"ڕێژە": "2.5-10mg", "میکانیزم": "Beta blocker", "کاریگەری لاوەکی": "خاوکردنەوەی دڵ", "پێچەوانە": "ئەستمی هەوە", "وەسف": "بەربەستەری بیتا کە لێدانی دڵ خاو دەکاتەوە", "بۆچی": "بۆ پەستانی خوێن و نەخۆشی دڵی ئیسکیمیک", "تێبینی": ""},
        "هیدروکلۆرۆتایزید": {"ڕێژە": "12.5-25mg", "میکانیزم": "Thiazide diuretic", "کاریگەری لاوەکی": "نزمی پۆتاسیۆم", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "دەرمانی دەرکەری ئاو", "بۆچی": "بۆ کەمکردنەوەی پەستانی خوێن", "تێبینی": ""},
        "فورۆسیماید": {"ڕێژە": "20-40mg", "میکانیزم": "Loop diuretic", "کاریگەری لاوەکی": "نزمی پۆتاسیۆم", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "دەرمانی دەرکەری بەهێز", "بۆچی": "بۆ چارەسەری پەستانی خوێن و ئاوسان", "تێبینی": ""},
        "کارڤیدیلۆل": {"ڕێژە": "6.25-25mg", "میکانیزم": "Beta blocker", "کاریگەری لاوەکی": "سەرگێژخواردن", "پێچەوانە": "ئەستمی هەوە", "وەسف": "بەربەستەری بیتا", "بۆچی": "بۆ نەخۆشی دڵی شکان و پەستانی خوێن", "تێبینی": ""},
        "نایترۆگلیسیرین": {"ڕێژە": "0.3-0.6mg", "میکانیزم": "Nitrate", "کاریگەری لاوەکی": "سەرئێشە", "پێچەوانە": "نزمی BP", "وەسف": "فراوانکەری خوێنبەرەکان", "بۆچی": "بۆ چارەسەری ئازاری سنگ", "تێبینی": ""}
    },
    "دژە شەکرە": {
        "مێتفۆرمین": {"ڕێژە": "500-2000mg", "میکانیزم": "Biguanide", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "دەرمانی هێڵی یەکەم بۆ شەکرەی جۆری ٢", "بۆچی": "بۆ کۆنتڕۆڵکردنی شەکری خوێن", "تێبینی": ""},
        "گلیپیزاید": {"ڕێژە": "5-20mg", "میکانیزم": "Sulfonylurea", "کاریگەری لاوەکی": "هایپۆگلایسیمیا", "پێچەوانە": "هەستیاری", "وەسف": "دەرمانی سەلفۆنیل یوریا", "بۆچی": "بۆ کەمکردنەوەی شەکری خوێن", "تێبینی": ""},
        "ئەنسولین Glargine": {"ڕێژە": "10-40 IU", "میکانیزم": "Insulin analog", "کاریگەری لاوەکی": "هایپۆگلایسیمیا", "پێچەوانە": "هایپۆگلایسیمیا", "وەسف": "ئەنسولینی درێژخایەن", "بۆچی": "بۆ کۆنتڕۆڵی شەکری خوێن", "تێبینی": ""},
        "سیتاگلیپتین": {"ڕێژە": "100mg", "میکانیزم": "DPP-4 inhibitor", "کاریگەری لاوەکی": "سەرئێشە", "پێچەوانە": "نەخۆشی پەنکریاس", "وەسف": "بەربەستەری DPP-4", "بۆچی": "بۆ شەکرەی جۆری ٢", "تێبینی": ""}
    },
    "دژە کۆخە و هەوکردن": {
        "ئەمۆکسیسیلین": {"ڕێژە": "500mg", "میکانیزم": "Beta-lactam", "کاریگەری لاوەکی": "زکچوون", "پێچەوانە": "هەستیاری پێنیسیلین", "وەسف": "ئەنتیبایۆتیکی پێنیسیلین", "بۆچی": "بۆ هەوکردنی بەکتریایی", "تێبینی": ""},
        "ئازیترۆمایسین": {"ڕێژە": "250-500mg", "میکانیزم": "Macrolide", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "نەخۆشی دڵ", "وەسف": "ئەنتیبایۆتیکی ماکرۆلید", "بۆچی": "بۆ هەوکردنی هەناسە", "تێبینی": ""},
        "سیپرۆفلۆکساسین": {"ڕێژە": "500mg", "میکانیزم": "Fluoroquinolone", "کاریگەری لاوەکی": "ئازاری ماسوولکە", "پێچەوانە": "منداڵان", "وەسف": "ئەنتیبایۆتیکی فلۆرۆکینۆلۆن", "بۆچی": "بۆ هەوکردنی میز و سییەکان", "تێبینی": ""},
        "سێفتریاکسۆن": {"ڕێژە": "1-2g", "میکانیزم": "Cephalosporin", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "هەستیاری", "وەسف": "ئەنتیبایۆتیکی سێفالۆسپۆرین", "بۆچی": "بۆ هەوکردنی توند", "تێبینی": ""}
    },
    "دژە ئەنیمیا": {
        "فێروس سولفەیت": {"ڕێژە": "300-600mg", "میکانیزم": "Iron supplement", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "هیمۆکروماتۆسیس", "وەسف": "پڕکەری ئاسن", "بۆچی": "بۆ چارەسەری ئەنیمیا", "تێبینی": ""},
        "فۆلیک ئەسید": {"ڕێژە": "1mg", "میکانیزم": "Folate supplement", "کاریگەری لاوەکی": "کەم", "پێچەوانە": "هەستیاری", "وەسف": "پڕکەری فۆلیک ئەسید", "بۆچی": "بۆ ئەنیمیای ماکرۆسایتیک", "تێبینی": ""},
        "ڤیتامین B12": {"ڕێژە": "1000mcg", "میکانیزم": "Cobalamin", "کاریگەری لاوەکی": "کەم", "پێچەوانە": "هەستیاری", "وەسف": "پڕکەری ڤیتامین B12", "بۆچی": "بۆ ئەنیمیای ماکرۆسایتیک", "تێبینی": ""}
    },
    "دژە ئازار": {
        "ئەسپیرین": {"ڕێژە": "75-300mg", "میکانیزم": "NSAID", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "خوێنبەربوون", "وەسف": "دژە ئازار و دژە تەمەن", "بۆچی": "بۆ ئازار و پێشگیری لە خوێن مەبەست", "تێبینی": ""},
        "ئیبۆپروفین": {"ڕێژە": "200-400mg", "میکانیزم": "NSAID", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "دژە ئازار و دژە هەوکردن", "بۆچی": "بۆ ئازاری ماسوولکە و سەرئێشە", "تێبینی": ""},
        "پاراستامۆل": {"ڕێژە": "500-1000mg", "میکانیزم": "Analgesic", "کاریگەری لاوەکی": "زیان بە جگەر", "پێچەوانە": "نەخۆشی جگەر", "وەسف": "دژە ئازار و دژە تەمەن", "بۆچی": "بۆ ئازاری سەرئێشە و تا", "تێبینی": ""},
        "مۆرفین": {"ڕێژە": "5-10mg", "میکانیزم": "Opioid", "کاریگەری لاوەکی": "خەوی", "پێچەوانە": "نەخۆشی هەناسە", "وەسف": "دژە ئازاری بەهێز", "بۆچی": "بۆ ئازاری توند", "تێبینی": ""}
    },
    "دژە خوێن": {
        "وارفارین": {"ڕێژە": "5mg", "میکانیزم": "Vitamin K antagonist", "کاریگەری لاوەکی": "خوێنبەربوون", "پێچەوانە": "حەمل", "وەسف": "دژە خوێن", "بۆچی": "بۆ پێشگیری لە مەبەست", "تێبینی": ""},
        "هێپارین": {"ڕێژە": "5000 IU", "میکانیزم": "Anticoagulant", "کاریگەری لاوەکی": "خوێنبەربوون", "پێچەوانە": "خوێنبەربوون", "وەسف": "دژە خوێنی خێرا", "بۆچی": "بۆ پێشگیری لە مەبەست", "تێبینی": ""},
        "کلۆپیدۆگرێل": {"ڕێژە": "75mg", "میکانیزم": "Antiplatelet", "کاریگەری لاوەکی": "خوێنبەربوون", "پێچەوانە": "خوێنبەربوون", "وەسف": "دژە پلەیتلێت", "بۆچی": "بۆ نەخۆشی دڵی ئیسکیمیک", "تێبینی": ""}
    },
    "دژە سکچوون": {
        "ئومەپرازۆل": {"ڕێژە": "20-40mg", "میکانیزم": "PPI", "کاریگەری لاوەکی": "سەرئێشە", "پێچەوانە": "نەخۆشی جگەر", "وەسف": "بەربەستەری پمپەی پرۆتۆن", "بۆچی": "بۆ چارەسەری سکچوون و برینداری گەدە", "تێبینی": ""},
        "ڕانیتیدین": {"ڕێژە": "150mg", "میکانیزم": "H2 blocker", "کاریگەری لاوەکی": "سەرگێژخواردن", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "بەربەستەری H2", "بۆچی": "بۆ سکچوون", "تێبینی": ""}
    },
    "دژە کۆکە": {
        "سالبوتامۆل": {"ڕێژە": "2 puffs", "میکانیزم": "Beta-2 agonist", "کاریگەری لاوەکی": "لەرزین", "پێچەوانە": "نەخۆشی دڵ", "وەسف": "فراوانکەری بۆڕی هەناسە", "بۆچی": "بۆ چارەسەری کۆکە", "تێبینی": ""},
        "بۆدیزۆناید": {"ڕێژە": "200-800mcg", "میکانیزم": "Steroid inhaler", "کاریگەری لاوەکی": "هەوکردنی دەم", "پێچەوانە": "هەستیاری", "وەسف": "ستیرۆیدی هەناسەدان", "بۆچی": "بۆ پێشگیری لە کۆکە", "تێبینی": ""}
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
    ("وارفارین", "ئەسپیرین"): {"severity": "مەترسیدار", "effect": "زیادبوونی زۆری مەترسی خوێنبەربوون", "color": "danger"},
    ("هێپارین", "وارفارین"): {"severity": "مامناوەند", "effect": "پێویستی بە چاودێری وردی INR", "color": "warning"},
    ("ئیبۆپروفین", "پاراستامۆل"): {"severity": "کەم", "effect": "بە گشتی سەلامەتە", "color": "safe"},
    ("مۆرفین", "سالبوتامۆل"): {"severity": "مامناوەند", "effect": "کەمبوونی کاریگەری هەناسەدان", "color": "warning"}
}

# ================================
# 7. فانکشنەکانی تایبەتمەندییە نوێیەکان
# ================================

# 7.1 سیستەمی دووبارەکردنەوەی بۆشایی (Spaced Repetition)
def update_spaced_repetition(username: str, item: str, item_type: str, correct: bool):
    """نوێکردنەوەی سیستەمی دووبارەکردنەوەی بۆشایی"""
    sr_data = load_spaced_repetition()
    if username not in sr_data:
        sr_data[username] = {}
    
    key = f"{item_type}_{item}"
    
    if key not in sr_data[username]:
        sr_data[username][key] = {
            "interval": 1,
            "repetitions": 0,
            "ease_factor": 2.5,
            "next_review": datetime.now().isoformat(),
            "correct_count": 0,
            "wrong_count": 0
        }
    
    item_data = sr_data[username][key]
    
    if correct:
        item_data["repetitions"] += 1
        item_data["correct_count"] += 1
        if item_data["repetitions"] == 1:
            item_data["interval"] = 1
        elif item_data["repetitions"] == 2:
            item_data["interval"] = 6
        else:
            item_data["interval"] = int(item_data["interval"] * item_data["ease_factor"])
        item_data["ease_factor"] = max(1.3, item_data["ease_factor"] + 0.1)
    else:
        item_data["repetitions"] = 0
        item_data["wrong_count"] += 1
        item_data["interval"] = 1
        item_data["ease_factor"] = max(1.3, item_data["ease_factor"] - 0.2)
    
    item_data["next_review"] = (datetime.now() + timedelta(days=item_data["interval"])).isoformat()
    
    save_spaced_repetition(sr_data)
    return item_data

def get_due_reviews(username: str) -> List:
    """دۆزینەوەی ئەو بابەتانەی کە پێویستە دووبارە بکرێنەوە"""
    sr_data = load_spaced_repetition()
    if username in sr_data:
        due_items = []
        now = datetime.now()
        for key, data in sr_data[username].items():
            next_review = datetime.fromisoformat(data["next_review"])
            if now >= next_review:
                parts = key.split("_", 1)
                if len(parts) == 2:
                    item_type, item = parts
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
    """وەرگرتنی هەواڵی پزیشکی"""
    return [
        {"title": "دۆزینەوەی دەرمانێکی نوێ بۆ شەکرە", "summary": "توێژینەوەیەکی نوێ دەرمانێکی کاریگەر بۆ چارەسەری شەکرەی جۆری ٢ دەدۆزێتەوە", "source": "PubMed", "date": "2024-01-15"},
        {"title": "پێشکەوتن لە چارەسەری نەخۆشی دڵ", "summary": "ڕێگەیەکی نوێ بۆ چارەسەری نەخۆشی دڵی ئیسکیمیک پەرەی پێدراوە", "source": "The Lancet", "date": "2024-01-10"},
        {"title": "کوتانی نوێ بۆ نەخۆشی سیل", "summary": "کوتانێکی نوێ بۆ نەخۆشی سیل لە تاقیکردنەوەکاندا ئەنجامی باشی نیشان داوە", "source": "WHO", "date": "2024-01-05"},
        {"title": "پەیوەندی نێوان شێوازی خواردن و نەخۆشی جگەر", "summary": "توێژینەوە نوێیەکان پەیوەندی نێوان شێوازی خواردنی چەور و نەخۆشی جگەری چەور دەردەخەن", "source": "NEJM", "date": "2024-01-01"}
    ]

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
                interactions.append({"drug1": drugs[i], "drug2": drugs[j], "severity": interaction["severity"], "effect": interaction["effect"], "color": interaction["color"]})
            elif reverse_pair in DRUG_INTERACTIONS:
                interaction = DRUG_INTERACTIONS[reverse_pair]
                interactions.append({"drug1": drugs[j], "drug2": drugs[i], "severity": interaction["severity"], "effect": interaction["effect"], "color": interaction["color"]})
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
        "created_at": datetime.now().isoformat()
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
    clinical_notes = load_clinical_notes()
    if username not in clinical_notes:
        clinical_notes[username] = []
    note["timestamp"] = datetime.now().isoformat()
    clinical_notes[username].append(note)
    save_clinical_notes(clinical_notes)

def get_clinical_notes(username: str) -> List:
    """وەرگرتنی یاداشتە کلینیکییەکان"""
    clinical_notes = load_clinical_notes()
    return clinical_notes.get(username, [])

# 7.7 سیستەمی تاقیکردنەوەی گشتی
def generate_comprehensive_exam(num_questions: int = 100) -> List[Dict]:
    """دروستکردنی تاقیکردنەوەی گشتی"""
    all_questions = []
    for disease, info in DISEASE_DATABASE.items():
        symptoms = info.get("نیشانەکان", [])
        if symptoms:
            correct = random.choice(symptoms)
            wrong_options = []
            for d in DISEASE_DATABASE.values():
                for s in d.get("نیشانەکان", []):
                    if s != correct and s not in wrong_options:
                        wrong_options.append(s)
                        if len(wrong_options) >= 3:
                            break
                if len(wrong_options) >= 3:
                    break
            options = [correct] + wrong_options[:3]
            random.shuffle(options)
            all_questions.append({
                "پرسیار": f"کام نیشانە تایبەتە بە {disease}؟",
                "هەڵبژاردەکان": options,
                "وەڵامی ڕاست": options.index(correct),
                "ڕوونکردنەوە": f"{disease}: {', '.join(symptoms[:3])}",
                "category": "نەخۆشی"
            })
    
    return random.sample(all_questions, min(num_questions, len(all_questions)))

# 7.8 شێوەکاری میکرۆسکۆپ
def generate_microscope_view(cell_type: str) -> None:
    """دروستکردنی شێوەکاری میکرۆسکۆپی"""
    fig, ax = plt.subplots(figsize=(4, 4), facecolor='black')
    ax.set_facecolor('black')
    
    if cell_type == "RBC":
        for _ in range(30):
            x, y = random.uniform(0, 1), random.uniform(0, 1)
            circle = plt.Circle((x, y), random.uniform(0.03, 0.06), color='red', alpha=0.7, ec='darkred')
            ax.add_patch(circle)
        ax.set_title("خڕۆکە سوورەکان (RBC)", color='white')
    elif cell_type == "WBC":
        for _ in range(10):
            x, y = random.uniform(0, 1), random.uniform(0, 1)
            circle = plt.Circle((x, y), random.uniform(0.05, 0.1), color=random.choice(['purple', 'blue']), alpha=0.6)
            ax.add_patch(circle)
            inner = plt.Circle((x, y), random.uniform(0.02, 0.04), color='darkblue', alpha=0.8)
            ax.add_patch(inner)
        ax.set_title("خڕۆکە سپییەکان (WBC)", color='white')
    elif cell_type == "Platelets":
        for _ in range(50):
            x, y = random.uniform(0, 1), random.uniform(0, 1)
            circle = plt.Circle((x, y), random.uniform(0.01, 0.03), color='lightblue', alpha=0.5)
            ax.add_patch(circle)
        ax.set_title("پلەیتلێتەکان (Platelets)", color='white')
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    st.pyplot(fig)
    plt.close()

# ================================
# 8. دروستکردنی کویز
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
        {"پرسیار": "کام دەرمانە بۆ پەستانی خوێن؟", "هەڵبژاردەکان": ["کاپتۆپریل", "مێتفۆرمین", "ئەنسولین", "ئەمۆکسیسیلین"], "وەڵامی ڕاست": 0}
    ]
    
    level2_questions = [
        {"پرسیار": "HbA1c > 6.5% ئاماژەیە بۆ چی؟", "هەڵبژاردەکان": ["شەکرە", "ئەنیمیا", "نەخۆشی دڵ", "هەوکردن"], "وەڵامی ڕاست": 0},
        {"پرسیار": "BP > 140/90 نیشانەی چییە؟", "هەڵبژاردەکان": ["پەستانی خوێن", "نەخۆشی دڵ", "شەکرە", "هەوکردن"], "وەڵامی ڕاست": 0},
        {"پرسیار": "MCV < 80 fL نیشانەی چییە؟", "هەڵبژاردەکان": ["ئەنیمیای مایکرۆسایتیک", "ئەنیمیای ماکرۆسایتیک", "ئەنیمیای نۆرمۆسایتیک", "هیمۆلایتیک"], "وەڵامی ڕاست": 0},
        {"پرسیار": "Troponin بەرز نیشانەی چییە؟", "هەڵبژاردەکان": ["نەخۆشی دڵ", "شەکرە", "هەوکردن", "ئەنیمیا"], "وەڵامی ڕاست": 0},
        {"پرسیار": "Creatinine بەرز نیشانەی چییە؟", "هەڵبژاردەکان": ["نەخۆشی گورچیلە", "نەخۆشی جگەر", "نەخۆشی دڵ", "شەکرە"], "وەڵامی ڕاست": 0}
    ]
    
    level_questions = {1: level1_questions, 2: level2_questions}
    
    for level, questions in level_questions.items():
        for i in range(LEVELS[level]["quizzes"]):
            q = random.choice(questions)
            quizzes.append({
                "پرسیار": q["پرسیار"],
                "هەڵبژاردەکان": q["هەڵبژاردەکان"],
                "وەڵامی ڕاست": q["وەڵامی ڕاست"],
                "ئاست": level,
                "ئاستی ناو": LEVELS[level]["name"],
                "ڕوونکردنەوە": f"ئاستی {LEVELS[level]['name']} - کویز ژمارە {i+1}"
            })
    
    return quizzes

MEDICAL_QUIZZES = generate_quizzes_by_level()

# ================================
# 9. فانکشنە یارمەتیدەرەکان
# ================================
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

def get_risk_color(risk_level: str) -> str:
    colors = {"زۆر مەترسیدار": "#ff6b6b", "مەترسیدار": "#ffd93d", "مامناوەند": "#ffc107", "کەم": "#6bcb77"}
    return colors.get(risk_level, "#6c757d")

def get_age_group(age: int) -> str:
    if age < 18: return "منداڵ"
    elif age < 40: return "گەنج"
    elif age < 60: return "تەمەن مامناوەند"
    else: return "پیر"

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

def auto_save():
    if st.session_state.logged_in:
        save_user_data(st.session_state.username, {
            "custom_lab_tests": st.session_state.custom_lab_tests,
            "custom_drugs": st.session_state.custom_drugs,
            "lab_notes": st.session_state.lab_notes,
            "drug_notes": st.session_state.drug_notes,
            "xp_points": st.session_state.xp_points,
            "badges": st.session_state.badges
        })

# ================================
# 10. ستەیتەکانی ئەپ
# ================================
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
if 'xp_points' not in st.session_state:
    st.session_state.xp_points = 0
if 'badges' not in st.session_state:
    st.session_state.badges = []
if 'quiz_score' not in st.session_state:
    st.session_state.quiz_score = 0
if 'quiz_completed' not in st.session_state:
    st.session_state.quiz_completed = False
if 'total_cases_solved' not in st.session_state:
    st.session_state.total_cases_solved = 0
if 'correct_diagnoses' not in st.session_state:
    st.session_state.correct_diagnoses = 0
if 'streak_days' not in st.session_state:
    st.session_state.streak_days = 0
if 'last_activity' not in st.session_state:
    st.session_state.last_activity = datetime.now()
if 'current_case' not in st.session_state:
    st.session_state.current_case = None
if 'student_level' not in st.session_state:
    st.session_state.student_level = "ساڵی یەکەم"
if 'achievements' not in st.session_state:
    st.session_state.achievements = []
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
if 'study_time' not in st.session_state:
    st.session_state.study_time = 0
if 'quiz_attempts' not in st.session_state:
    st.session_state.quiz_attempts = 0

# ================================
# 11. پەڕەی لۆگین
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
                    st.session_state.xp_points = user_data.get("xp_points", 0)
                    st.session_state.badges = user_data.get("badges", [])
                    st.session_state.streak_days = update_user_streak(login_username)
                    add_xp(login_username, 1)
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
# 12. سایدبار
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
        st.rerun()

# ================================
# 13. پەڕەکان
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
    
    due_reviews = get_due_reviews(st.session_state.username)
    if due_reviews:
        st.warning(f"📚 **{len(due_reviews)}** بابەت پێویستیان بە دووبارەکردنەوەیە! بچۆ بەشی دووبارەکردنەوە")

elif page == "📋 تاقیکردنەوەی گشتی":
    st.markdown("<h2>📋 تاقیکردنەوەی گشتی پزیشکی</h2>", unsafe_allow_html=True)
    
    if st.session_state.comprehensive_exam_questions is None:
        st.markdown("### تاقیکردنەوەیەکی ١٠٠ پرسیاری لە هەموو بابەتەکان")
        if st.button("🚀 دەستپێکردنی تاقیکردنەوە", type="primary"):
            st.session_state.comprehensive_exam_questions = generate_comprehensive_exam(100)
            st.session_state.comprehensive_exam_answers = {}
            st.session_state.comprehensive_exam_submitted = False
            st.rerun()
    
    elif not st.session_state.comprehensive_exam_submitted:
        questions = st.session_state.comprehensive_exam_questions
        for i, q in enumerate(questions):
            st.markdown(f"**{i+1}. {q['پرسیار']}**")
            answer = st.radio(f"وەڵام {i+1}:", q["هەڵبژاردەکان"], key=f"comp_q_{i}")
            st.session_state.comprehensive_exam_answers[i] = q["هەڵبژاردەکان"].index(answer) if answer else -1
        
        if st.button("📤 پێشکەشکردن", type="primary"):
            score = sum(1 for i, q in enumerate(questions) if st.session_state.comprehensive_exam_answers.get(i, -1) == q["وەڵامی ڕاست"])
            st.session_state.comprehensive_exam_score = score
            st.session_state.comprehensive_exam_submitted = True
            add_xp(st.session_state.username, score * 2)
            st.rerun()
    
    elif st.session_state.comprehensive_exam_submitted:
        score = st.session_state.comprehensive_exam_score
        total = len(st.session_state.comprehensive_exam_questions)
        percentage = (score / total) * 100 if total > 0 else 0
        st.markdown(f'<div class="success-box"><h2>🎉 ئەنجام: {score}/{total} ({percentage:.1f}%)</h2></div>', unsafe_allow_html=True)
        if st.button("🔄 تاقیکردنەوەی نوێ"):
            st.session_state.comprehensive_exam_questions = None
            st.rerun()

elif page == "🔄 دووبارەکردنەوە":
    st.markdown("<h2>🔄 دووبارەکردنەوەی بۆشایی (Spaced Repetition)</h2>", unsafe_allow_html=True)
    
    due_reviews = get_due_reviews(st.session_state.username)
    
    if due_reviews:
        st.markdown(f"### 📚 {len(due_reviews)} بابەت پێویستیان بە دووبارەکردنەوەیە")
        
        if st.session_state.flashcard_index >= len(due_reviews):
            st.session_state.flashcard_index = 0
        
        current_review = due_reviews[st.session_state.flashcard_index]
        
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
        st.success("🎉 هیچ بابەتێک پێویستی بە دووبارەکردنەوە نییە!")

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
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("هێشتا هیچ داتایەک نییە")

elif page == "👥 هاوڕێی خوێندن":
    st.markdown("<h2>👥 هاوڕێی خوێندن</h2>", unsafe_allow_html=True)
    
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
        </div>
        """, unsafe_allow_html=True)

elif page == "⚠️ کارلێکی دەرمانەکان":
    st.markdown("<h2>⚠️ پشکنینی کارلێکی نێوان دەرمانەکان</h2>", unsafe_allow_html=True)
    
    all_drugs = []
    for category, drugs in DRUG_DATABASE.items():
        all_drugs.extend(list(drugs.keys()))
    
    selected_drugs = st.multiselect("دەرمانەکان هەڵبژێرە:", all_drugs)
    
    if len(selected_drugs) >= 2:
        interactions = check_drug_interactions(selected_drugs)
        if interactions:
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
        st.info("تکایە لانیکەم ٢ دەرمان هەڵبژێرە")

elif page == "🔬 میکرۆسکۆپ":
    st.markdown("<h2>🔬 شێوەکاری میکرۆسکۆپ</h2>", unsafe_allow_html=True)
    cell_type = st.selectbox("جۆری خانە:", ["RBC", "WBC", "Platelets"])
    if st.button("🔬 نیشاندان"):
        generate_microscope_view(cell_type)

elif page == "📝 یاداشتی کلینیکی":
    st.markdown("<h2>📝 یاداشتی کلینیکی</h2>", unsafe_allow_html=True)
    
    with st.form("clinical_note"):
        patient_name = st.text_input("ناوی نەخۆش:")
        note_text = st.text_area("یاداشت:")
        if st.form_submit_button("💾 خەزنکردن"):
            add_clinical_note(st.session_state.username, {"patient": patient_name, "note": note_text})
            st.success("یاداشت خەزن کرا!")
            st.rerun()
    
    notes = get_clinical_notes(st.session_state.username)
    for note in notes[-10:]:
        st.markdown(f"""
        <div class="case-card">
            <p><strong>نەخۆش:</strong> {note.get('patient', 'نەزانراو')}</p>
            <p>{note.get('note', '')}</p>
            <p style="color:#888;">📅 {note.get('timestamp', '')[:10]}</p>
        </div>
        """, unsafe_allow_html=True)

elif page == "🧠 AI یاریدەدەر":
    st.markdown("<h2>🧠 یاریدەدەری هۆشمەند</h2>", unsafe_allow_html=True)
    symptoms_input = st.text_area("🩺 نیشانەکان:", placeholder="سەرئێشە, تا, کۆخە, ...")
    if st.button("🔍 شیکاری", type="primary") and symptoms_input:
        symptoms_list = [s.strip() for s in symptoms_input.split(',') if s.strip()]
        results = []
        for disease, info in DISEASE_DATABASE.items():
            match = len(set(symptoms_list).intersection(set(info['نیشانەکان'])))
            if match > 0:
                pct = (match / len(info['نیشانەکان'])) * 100
                results.append({'disease': disease, 'pct': round(pct, 1), 'risk': info['ئاستی مەترسی']})
        results.sort(key=lambda x: x['pct'], reverse=True)
        for r in results[:5]:
            st.markdown(f"""
            <div class="case-card">
                <h4>{r['disease']}</h4>
                <p>ڕێژەی گونجاندن: {r['pct']}% | ئاستی مەترسی: <span style="color:{get_risk_color(r['risk'])}">{r['risk']}</span></p>
            </div>
            """, unsafe_allow_html=True)

elif page == "📚 نەخۆشییەکان":
    st.markdown(f"<h2>📚 کتێبخانەی نەخۆشییەکان - {get_disease_count()} نەخۆشی</h2>", unsafe_allow_html=True)
    
    search = st.text_input("🔍 گەڕان:")
    filter_risk = st.selectbox("فلتر:", ["هەموو", "زۆر مەترسیدار", "مەترسیدار", "مامناوەند", "کەم"])
    show_rare = st.checkbox("نیشاندانی نەخۆشییە دەگمەنەکان")
    
    filtered = {k: v for k, v in DISEASE_DATABASE.items() if (not search or search in k)}
    if filter_risk != "هەموو":
        filtered = {k: v for k, v in filtered.items() if v.get('ئاستی مەترسی') == filter_risk}
    if not show_rare:
        filtered = {k: v for k, v in filtered.items() if not v.get('دەگمەن', False)}
    
    cols = st.columns(2)
    idx = 0
    for disease, info in filtered.items():
        with cols[idx % 2]:
            with st.expander(f"🩺 {disease} {'🔴 دەگمەن' if info.get('دەگمەن') else ''}"):
                st.markdown(f"**ئاستی مەترسی:** <span style='color:{get_risk_color(info.get('ئاستی مەترسی', 'کەم'))}'>{info.get('ئاستی مەترسی')}</span>", unsafe_allow_html=True)
                st.markdown("**نیشانەکان:** " + ", ".join(info.get('نیشانەکان', [])[:6]))
                st.markdown("**چارەسەر:** " + ", ".join(info.get('چارەسەر', [])[:3]))
        idx += 1

elif page == "🩺 شیکاری کەیس":
    st.markdown("<h2>🩺 شیکاری کەیسی پزیشکی</h2>", unsafe_allow_html=True)
    
    if st.button("🔄 کەیسی نوێ", type="primary"):
        disease = random.choice(list(DISEASE_DATABASE.keys()))
        info = DISEASE_DATABASE[disease]
        st.session_state.current_case = {
            'case_id': f"CASE-{random.randint(1000,9999)}",
            'تەمەن': random.randint(18, 80),
            'ڕەگەز': random.choice(['نێر', 'مێ']),
            'نیشانەکان': random.sample(info['نیشانەکان'], min(5, len(info['نیشانەکان']))),
            'دەستنیشانکردن': disease,
            'ئاستی مەترسی': info['ئاستی مەترسی']
        }
        st.rerun()
    
    if st.session_state.current_case:
        case = st.session_state.current_case
        st.markdown(f"""
        <div class="case-card">
            <h3>📋 کەیسی {case['case_id']}</h3>
            <p>تەمەن: {case['تەمەن']} | ڕەگەز: {case['ڕەگەز']}</p>
            <p>نیشانەکان: {', '.join(case['نیشانەکان'])}</p>
            <p>ئاستی مەترسی: <span style="color:{get_risk_color(case['ئاستی مەترسی'])}">{case['ئاستی مەترسی']}</span></p>
        </div>
        """, unsafe_allow_html=True)
        
        user_diagnosis = st.selectbox("دەستنیشانکردن:", list(DISEASE_DATABASE.keys()))
        if st.button("✅ پشتڕاستکردنەوە", type="primary"):
            correct = case['دەستنیشانکردن']
            st.session_state.total_cases_solved += 1
            if user_diagnosis == correct:
                st.session_state.correct_diagnoses += 1
                add_xp(st.session_state.username, 20)
                st.markdown(f'<div class="success-box"><h3>🎉 ڕاستە!</h3><p>{correct}</p></div>', unsafe_allow_html=True)
                st.balloons()
            else:
                st.markdown(f'<div class="error-box"><h3>❌ هەڵەیە</h3><p>ڕاست: {correct}</p></div>', unsafe_allow_html=True)

elif page == "📝 کویز (ئاستی)":
    st.markdown("<h2>📝 کویزی پزیشکی - بەپێی ئاست</h2>", unsafe_allow_html=True)
    
    level = get_user_level(st.session_state.quiz_score)
    level_info = get_level_info(level)
    
    if not st.session_state.quiz_completed:
        next_quiz = get_next_quiz(level)
        if next_quiz:
            st.markdown(f"""
            <div class="quiz-card">
                <h3>{next_quiz['پرسیار']}</h3>
                <p style="color: #888;">ئاست: {get_level_icon(level)} {next_quiz.get('ئاستی ناو', level_info['name'])}</p>
            </div>
            """, unsafe_allow_html=True)
            
            answer = st.radio("وەڵام:", next_quiz['هەڵبژاردەکان'], key=f"q_{st.session_state.quiz_attempts}")
            
            if st.button("✅ پشتڕاستکردنەوە", type="primary"):
                selected = next_quiz['هەڵبژاردەکان'].index(answer)
                st.session_state.quiz_attempts += 1
                
                if selected == next_quiz['وەڵامی ڕاست']:
                    st.session_state.quiz_score += 1
                    add_xp(st.session_state.username, 10)
                    st.success("🎉 ڕاستە!")
                    update_spaced_repetition(st.session_state.username, next_quiz['پرسیار'], "quiz", True)
                else:
                    st.error(f"❌ هەڵەیە. ڕاست: {next_quiz['هەڵبژاردەکان'][next_quiz['وەڵامی ڕاست']]}")
                    update_spaced_repetition(st.session_state.username, next_quiz['پرسیار'], "quiz", False)
                
                st.session_state[f'level_{level}_done'] = st.session_state.get(f'level_{level}_done', 0) + 1
                st.rerun()

elif page == "🔬 تاقیگە":
    st.markdown("<h2>🔬 تاقیگەی ڤێرچواڵ</h2>", unsafe_allow_html=True)
    
    all_lab_tests = {**LAB_TESTS, **st.session_state.custom_lab_tests}
    
    search_lab = st.text_input("🔍 گەڕان:")
    
    for test_name, test_info in all_lab_tests.items():
        if search_lab and search_lab.lower() not in test_name.lower():
            continue
        
        low, high = test_info.get("نۆرماڵ", (0, 0))
        is_custom = test_name in st.session_state.custom_lab_tests
        current_note = test_info.get("تێبینی", "") if is_custom else st.session_state.lab_notes.get(test_name, test_info.get("تێبینی", ""))
        note_key = f"note_lab_{test_name}"
        
        st.markdown(f"""
        <div class="lab-result-card">
            <strong>{test_name}</strong>
            <p style="color:#aaa;">{test_info.get('گروپ', '')} | نۆرماڵ: {low}-{high} {test_info.get('یەکە', '')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        new_note = st.text_area("📝 تێبینی:", value=current_note, key=note_key, height=68, label_visibility="collapsed")
        if new_note != current_note:
            if is_custom:
                st.session_state.custom_lab_tests[test_name]["تێبینی"] = new_note
            else:
                st.session_state.lab_notes[test_name] = new_note
            auto_save()

elif page == "💊 فارماکۆلۆجی":
    st.markdown("<h2>💊 فارماکۆلۆجی</h2>", unsafe_allow_html=True)
    
    for category, drugs in DRUG_DATABASE.items():
        with st.expander(f"📂 {category} ({len(drugs)} دەرمان)"):
            for drug, info in drugs.items():
                note_key = f"note_drug_{category}_{drug}"
                current_note = st.session_state.drug_notes.get(note_key, info.get("تێبینی", ""))
                
                st.markdown(f"""
                <div class="drug-card">
                    <h4>{drug}</h4>
                    <p>ڕێژە: {info.get('ڕێژە', '')} | میکانیزم: {info.get('میکانیزم', '')}</p>
                    <p>بۆچی: {info.get('بۆچی', '')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                new_note = st.text_area("📝 تێبینی:", value=current_note, key=note_key, height=68, label_visibility="collapsed")
                if new_note != current_note:
                    st.session_state.drug_notes[note_key] = new_note
                    auto_save()

elif page == "🏆 دەستکەوتەکان":
    st.markdown("<h2>🏆 دەستکەوتەکان</h2>", unsafe_allow_html=True)
    
    all_achievements = [
        {"name": "دەستنیشانکەری شارەزا", "condition": st.session_state.correct_diagnoses >= 5, "icon": "⭐"},
        {"name": "ڕاهێنەری پزیشکی", "condition": st.session_state.total_cases_solved >= 20, "icon": "📚"},
        {"name": "شارەزای کویز", "condition": st.session_state.quiz_score >= 30, "icon": "📝"},
        {"name": "پزیشکی گشتی", "condition": st.session_state.quiz_score >= 50, "icon": "🎓"},
        {"name": "بەردەوامی ٧ ڕۆژ", "condition": st.session_state.streak_days >= 7, "icon": "🔥"}
    ]
    
    for ach in all_achievements:
        if ach["condition"] and ach["name"] not in st.session_state.achievements:
            st.session_state.achievements.append(ach["name"])
    
    for ach in st.session_state.achievements:
        st.markdown(f'<span class="achievement-badge">{ach} ✅</span>', unsafe_allow_html=True)

# ================================
# 14. فووەتەر
# ================================
st.markdown("---")
st.markdown(f"""
<div class="footer-style">
    <h3>🩺 Dr.Danyal - ڕاهێنەری پزیشکی Pro Max Ultra v7.0</h3>
    <p>{get_disease_count()} نەخۆشی | {get_drug_count()} دەرمان | {get_quiz_count()} کویز | {get_lab_count()} پشکنین</p>
    <p style="font-size:0.8rem;opacity:0.8;">© 2024 Dr.Danyal | Ultra Edition</p>
</div>
""", unsafe_allow_html=True)
