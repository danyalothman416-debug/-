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
import os
import uuid
from io import BytesIO
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

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
DATA_DIR = "user_data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

USERS_FILE = os.path.join(DATA_DIR, "users.json")
LEADERBOARD_FILE = os.path.join(DATA_DIR, "leaderboard.json")
STUDY_ROOMS_FILE = os.path.join(DATA_DIR, "study_rooms.json")
SPACED_REPETITION_FILE = os.path.join(DATA_DIR, "spaced_repetition.json")
CLINICAL_NOTES_FILE = os.path.join(DATA_DIR, "clinical_notes.json")

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
# 2. CSS و ستایلە پێشکەوتووەکان
# ================================
st.markdown("""
<style>
    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #0a0a1a 0%, #1a1a3e 50%, #0a0a1a 100%);
        min-height: 100vh;
    }
    
    .main {
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 2rem;
        margin: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Custom Sidebar Styles */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0f2e 0%, #1a1a4e 50%, #0f0f2e 100%) !important;
        border-right: 2px solid rgba(99, 102, 241, 0.2) !important;
        box-shadow: 8px 0 40px rgba(0, 0, 0, 0.6) !important;
    }
    
    [data-testid="stSidebar"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: 
            radial-gradient(circle at 20% 20%, rgba(99, 102, 241, 0.08) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(139, 92, 246, 0.08) 0%, transparent 50%);
        pointer-events: none;
    }
    
    [data-testid="stSidebar"] * {
        color: rgba(255, 255, 255, 0.95) !important;
        font-family: 'Segoe UI', system-ui, -apple-system, sans-serif !important;
    }
    
    [data-testid="stSidebar"] hr {
        border-color: rgba(99, 102, 241, 0.15) !important;
        margin: 1rem 0 !important;
    }
    
    /* Sidebar User Profile Section */
    .sidebar-profile {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(139, 92, 246, 0.1));
        border-radius: 20px;
        padding: 1.5rem;
        margin: 0.5rem 0 1.5rem 0;
        border: 1px solid rgba(99, 102, 241, 0.2);
        text-align: center;
        backdrop-filter: blur(10px);
        position: relative;
        overflow: hidden;
    }
    
    .sidebar-profile::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: conic-gradient(from 0deg, transparent, rgba(99, 102, 241, 0.1), transparent, rgba(139, 92, 246, 0.1), transparent);
        animation: rotate 8s linear infinite;
    }
    
    .sidebar-avatar {
        width: 70px;
        height: 70px;
        border-radius: 50%;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 0.8rem;
        font-size: 2rem;
        border: 3px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4);
        position: relative;
        z-index: 1;
    }
    
    .sidebar-username {
        font-size: 1.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #6366f1, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        position: relative;
        z-index: 1;
    }
    
    .sidebar-level-badge {
        display: inline-block;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.3), rgba(139, 92, 246, 0.3));
        padding: 0.3rem 1rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        color: #a78bfa !important;
        border: 1px solid rgba(139, 92, 246, 0.3);
        margin-top: 0.5rem;
        position: relative;
        z-index: 1;
    }
    
    /* Sidebar Stats Grid */
    .sidebar-stats {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.5rem;
        margin: 1.2rem 0;
        position: relative;
        z-index: 1;
    }
    
    .sidebar-stat-item {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 12px;
        padding: 0.7rem;
        text-align: center;
        border: 1px solid rgba(99, 102, 241, 0.1);
        transition: all 0.3s ease;
    }
    
    .sidebar-stat-item:hover {
        background: rgba(99, 102, 241, 0.1);
        transform: translateY(-2px);
        border-color: rgba(99, 102, 241, 0.3);
    }
    
    .sidebar-stat-value {
        font-size: 1.3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #6366f1, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .sidebar-stat-label {
        font-size: 0.65rem;
        color: rgba(255, 255, 255, 0.5) !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* XP Progress Bar */
    .sidebar-xp-container {
        margin: 0.8rem 0;
        position: relative;
        z-index: 1;
    }
    
    .sidebar-xp-bar {
        width: 100%;
        height: 6px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        overflow: hidden;
        margin: 0.5rem 0;
    }
    
    .sidebar-xp-fill {
        height: 100%;
        background: linear-gradient(90deg, #6366f1, #8b5cf6, #a78bfa);
        border-radius: 10px;
        transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
    }
    
    .sidebar-xp-fill::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
        animation: shimmer 2s infinite;
    }
    
    .sidebar-xp-text {
        font-size: 0.7rem;
        color: rgba(255, 255, 255, 0.5) !important;
        text-align: right;
    }
    
    /* Navigation Menu */
    .sidebar-nav {
        margin: 1.5rem 0;
    }
    
    .sidebar-nav-section {
        font-size: 0.65rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: rgba(99, 102, 241, 0.6) !important;
        font-weight: 700;
        margin: 1rem 0 0.5rem 0;
        padding-left: 0.5rem;
    }
    
    /* Radio Button Styling */
    [data-testid="stSidebar"] .stRadio > div {
        display: flex;
        flex-direction: column;
        gap: 2px;
    }
    
    [data-testid="stSidebar"] .stRadio label {
        padding: 0.7rem 1rem !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
        font-size: 0.9rem !important;
        border: 1px solid transparent !important;
        margin: 0 !important;
    }
    
    [data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(99, 102, 241, 0.08) !important;
        border-color: rgba(99, 102, 241, 0.2) !important;
        transform: translateX(3px);
    }
    
    [data-testid="stSidebar"] .stRadio label[data-selected="true"] {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(139, 92, 246, 0.15)) !important;
        border-color: rgba(99, 102, 241, 0.4) !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.2) !important;
    }
    
    /* Logout Button */
    [data-testid="stSidebar"] .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(239, 68, 68, 0.05)) !important;
        border: 1px solid rgba(239, 68, 68, 0.3) !important;
        color: #ef4444 !important;
        padding: 0.7rem !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(239, 68, 68, 0.1)) !important;
        border-color: rgba(239, 68, 68, 0.5) !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(239, 68, 68, 0.2) !important;
    }
    
    /* Sidebar Footer */
    .sidebar-footer {
        text-align: center;
        padding: 1rem 0;
        border-top: 1px solid rgba(99, 102, 241, 0.1);
        margin-top: 1rem;
    }
    
    .sidebar-footer-text {
        font-size: 0.7rem;
        color: rgba(255, 255, 255, 0.3) !important;
    }
    
    .sidebar-version {
        background: rgba(99, 102, 241, 0.2);
        padding: 0.2rem 0.8rem;
        border-radius: 10px;
        font-size: 0.65rem;
        color: #a78bfa !important;
        display: inline-block;
        margin-top: 0.3rem;
    }
    
    /* Active indicator dot */
    .active-dot {
        width: 8px;
        height: 8px;
        background: #10b981;
        border-radius: 50%;
        display: inline-block;
        margin-right: 0.5rem;
        box-shadow: 0 0 10px rgba(16, 185, 129, 0.5);
        animation: pulse-dot 2s infinite;
    }
    
    @keyframes pulse-dot {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(200%); }
    }
    
    @keyframes rotate {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Main Content Styles */
    .stat-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(15px);
        padding: 1.5rem;
        border-radius: 20px;
        border: 1px solid rgba(99, 102, 241, 0.15);
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
        border-color: rgba(99, 102, 241, 0.4);
        box-shadow: 0 15px 40px rgba(99, 102, 241, 0.2);
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #6366f1, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .main-header {
        font-size: 2.5rem;
        background: linear-gradient(135deg, #6366f1, #8b5cf6, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        padding: 2rem;
        margin-bottom: 1.5rem;
    }
    
    .case-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid rgba(99, 102, 241, 0.15);
        margin: 1rem 0;
        transition: all 0.3s ease;
        color: #fff;
    }
    
    .case-card:hover {
        border-color: rgba(99, 102, 241, 0.4);
        transform: translateY(-2px);
    }
    
    .success-box {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(16, 185, 129, 0.05));
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid rgba(16, 185, 129, 0.3);
        color: #fff;
    }
    
    .error-box {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(239, 68, 68, 0.05));
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid rgba(239, 68, 68, 0.3);
        color: #fff;
    }
    
    .quiz-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(15px);
        padding: 2rem;
        border-radius: 20px;
        border: 1px solid rgba(99, 102, 241, 0.2);
        margin: 1rem 0;
        color: #fff;
    }
    
    .leaderboard-card {
        background: rgba(255, 255, 255, 0.03);
        padding: 1rem;
        border-radius: 14px;
        border: 1px solid rgba(99, 102, 241, 0.15);
        margin: 0.5rem 0;
        transition: all 0.3s ease;
        color: #fff;
    }
    
    .leaderboard-card:hover {
        transform: translateX(5px);
        border-color: rgba(99, 102, 241, 0.4);
    }
    
    .leaderboard-top1 { border-color: #fbbf24 !important; background: rgba(251, 191, 36, 0.05) !important; }
    .leaderboard-top2 { border-color: #94a3b8 !important; background: rgba(148, 163, 184, 0.05) !important; }
    .leaderboard-top3 { border-color: #d97706 !important; background: rgba(217, 119, 6, 0.05) !important; }
    
    .badge-level {
        display: inline-block;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.3), rgba(139, 92, 246, 0.3));
        padding: 0.4rem 1.2rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        border: 1px solid rgba(139, 92, 246, 0.3);
        color: #fff;
    }
    
    .drug-card {
        background: rgba(255, 255, 255, 0.03);
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid rgba(99, 102, 241, 0.1);
        margin: 0.5rem 0;
        color: #fff;
    }
    
    .news-card {
        background: rgba(255, 255, 255, 0.03);
        padding: 1rem;
        border-radius: 12px;
        border-left: 4px solid #6366f1;
        margin: 0.8rem 0;
        color: #fff;
    }
    
    .interaction-safe {
        background: rgba(16, 185, 129, 0.1);
        border-left: 4px solid #10b981;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        color: #fff;
    }
    
    .interaction-warning {
        background: rgba(251, 191, 36, 0.1);
        border-left: 4px solid #fbbf24;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        color: #fff;
    }
    
    .interaction-danger {
        background: rgba(239, 68, 68, 0.1);
        border-left: 4px solid #ef4444;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        color: #fff;
    }
    
    .achievement-badge {
        display: inline-block;
        background: linear-gradient(135deg, rgba(251, 191, 36, 0.2), rgba(245, 158, 11, 0.1));
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        margin: 0.3rem;
        border: 1px solid rgba(251, 191, 36, 0.3);
        color: #fbbf24;
    }
    
    .flashcard {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        padding: 2rem;
        border-radius: 20px;
        border: 2px solid rgba(99, 102, 241, 0.2);
        text-align: center;
        min-height: 200px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.5s ease;
        color: #fff;
    }
    
    .flashcard:hover {
        border-color: rgba(99, 102, 241, 0.5);
        box-shadow: 0 15px 40px rgba(99, 102, 241, 0.2);
    }
    
    .flashcard.flipped {
        background: rgba(99, 102, 241, 0.1);
        border-color: rgba(139, 92, 246, 0.5);
    }
    
    .study-room {
        background: rgba(255, 255, 255, 0.03);
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid rgba(99, 102, 241, 0.15);
        margin: 1rem 0;
        color: #fff;
    }
    
    .chat-message {
        background: rgba(255, 255, 255, 0.03);
        padding: 0.8rem;
        border-radius: 12px;
        margin: 0.3rem 0;
        color: #fff;
    }
    
    .chat-message.own {
        background: rgba(99, 102, 241, 0.1);
    }
    
    .lab-result-card {
        background: rgba(255, 255, 255, 0.02);
        padding: 0.8rem;
        border-radius: 10px;
        margin: 0.3rem 0;
        border-left: 3px solid rgba(99, 102, 241, 0.3);
        color: #fff;
    }
    
    .footer-style {
        text-align: center;
        padding: 2rem;
        background: rgba(255, 255, 255, 0.02);
        border-radius: 16px;
        margin-top: 2rem;
        border: 1px solid rgba(99, 102, 241, 0.1);
        color: #fff;
    }
    
    .login-container {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 80vh;
    }
    
    .login-box {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        padding: 3rem;
        border-radius: 24px;
        border: 1px solid rgba(99, 102, 241, 0.2);
        text-align: center;
        max-width: 450px;
        width: 100%;
        box-shadow: 0 30px 60px rgba(0, 0, 0, 0.3);
    }
    
    .dr-icon {
        font-size: 4rem;
        display: inline-block;
        filter: drop-shadow(0 0 20px rgba(99, 102, 241, 0.4));
    }
    
    /* Selectbox and Input Styles */
    .stSelectbox > div > div,
    .stTextInput > div > div,
    .stTextArea > div > div,
    .stNumberInput > div > div {
        background: rgba(255, 255, 255, 0.06) !important;
        border: 1px solid rgba(99, 102, 241, 0.2) !important;
        border-radius: 12px !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        border: none !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 0.7rem 2rem !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 30px rgba(99, 102, 241, 0.3) !important;
    }
    
    @media (max-width: 768px) {
        .main-header { font-size: 1.8rem; padding: 1rem; }
        .stat-number { font-size: 1.8rem; }
    }
</style>
""", unsafe_allow_html=True)

# ================================
# 3. سیستەمی ئاستەکان (Levels)
# ================================
LEVELS = {
    1: {"name": "سەرەتایی (Beginner)", "min_score": 0, "max_score": 9, "color": "#10b981", "quizzes": 50, "icon": "🌱", "description": "دەستپێکی ڕێگای پزیشکی", "requirements": "هیچ", "xp_required": 0},
    2: {"name": "فێرخواز (Learner)", "min_score": 10, "max_score": 29, "color": "#06b6d4", "quizzes": 100, "icon": "📖", "description": "فێربوونی بنەماکانی پزیشکی", "requirements": "تەواوکردنی ئاست ١", "xp_required": 100},
    3: {"name": "پێشکەوتوو (Advanced)", "min_score": 30, "max_score": 59, "color": "#f59e0b", "quizzes": 150, "icon": "🚀", "description": "پێشکەوتن لە زانستە پزیشکییەکان", "requirements": "تەواوکردنی ئاست ٢", "xp_required": 300},
    4: {"name": "شارەزا (Expert)", "min_score": 60, "max_score": 89, "color": "#f97316", "quizzes": 200, "icon": "🏆", "description": "شارەزایی لە نەخۆشییەکان", "requirements": "تەواوکردنی ئاست ٣", "xp_required": 600},
    5: {"name": "پزیشک (Master)", "min_score": 90, "max_score": 100, "color": "#ef4444", "quizzes": 500, "icon": "👨‍⚕️", "description": "پزیشکی لێهاتوو و شارەزا", "requirements": "تەواوکردنی ئاست ٤", "xp_required": 1000},
    6: {"name": "پڕۆفیسۆر (Professor)", "min_score": 100, "max_score": 150, "color": "#8b5cf6", "quizzes": 750, "icon": "🎓", "description": "ئاستی پڕۆفیسۆری پزیشکی", "requirements": "تەواوکردنی ئاست ٥ + ٢٠٠٠ XP", "xp_required": 2000},
    7: {"name": "ئەفسانە (Legend)", "min_score": 150, "max_score": 999, "color": "#ec4899", "quizzes": 1000, "icon": "👑", "description": "ئاستی ئەفسانەیی - گەیشتوویتە لوتکە!", "requirements": "تەواوکردنی ئاست ٦ + ٥٠٠٠ XP", "xp_required": 5000}
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
    "پەستانی خوێنی سەرەتایی": {
        "نیشانەکان": ["سەرئێشە", "سەرگێژخواردن", "فشاری پشت چاو", "خێرالێدانی دڵ", "ئەرەقەکردن", "مەلە", "خوێن لە لووتدا"],
        "پشکنینەکان": {"BP": ">140/90 mmHg", "ECG": "Left ventricular hypertrophy", "Creatinine": "نۆرماڵ", "Potassium": "نۆرماڵ"},
        "چارەسەر": ["کاپتۆپریل 25mg", "کەمکردنەوەی نمەک", "وەرزشی ئیروبیک", "کەمکردنەوەی کێش", "پێوانەکردنی BP"],
        "ئاستی مەترسی": "مامناوەند",
        "تایبەتمەندی": "BP بەرز بەبێ هۆکاری دیکە",
        "ڕێپیشگیری": ["پێوانەکردنی BP بەردەوام", "شێوازی خواردنی کەم نمەک", "ڕاهێنانی ڕۆژانە"],
        "گروپی تەمەن": "هەموو تەمەنەکان",
        "ڕێژەی تووشبوون": "25%",
        "جۆری نەخۆشی": "دڵ و خوێن",
        "دەگمەن": False
    },
    "نەخۆشی دڵی ئیسکیمیک": {
        "نیشانەکان": ["ئازاری سنگ", "کورتی هەناسە", "ئارەقەکردن", "سکچوون و ڕشانەوە", "ئازاری شان", "تنگەنەفەسی", "ئازاری پشت", "خێرالێدانی دڵ"],
        "پشکنینەکان": {"ECG": "ST depression", "Troponin": "بەرز >0.04", "CK-MB": "بەرز >5", "Echocardiogram": "کەمبوونی ئیشی دڵ"},
        "چارەسەر": ["ئەسپیرین 300mg", "نایترۆگلیسیرین", "ئۆکسجین", "بێتا بلاکەر", "هێپارین"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندی": "ST changes + Troponin elevated",
        "ڕێپیشگیری": ["کۆنتڕۆڵی پەستانی خوێن", "وەرزش", "وەستانی جگەرە", "کۆنتڕۆڵی شەکرە"],
        "گروپی تەمەن": "تەمەن > 50 ساڵ",
        "ڕێژەی تووشبوون": "7%",
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
    }
}

# ================================
# 5. داتابەسی پشکنینەکانی تاقیگە
# ================================
LAB_TESTS = {
    "CBC": {"گروپ": "خوێن", "نۆرماڵ": (4.0, 11.0), "یەکە": "x10³/µL", "تەفسیر": "خڕۆکە سپیەکان", "ئامێر": "ئۆتۆماتیک سێل کاونتر", "تێبینی": ""},
    "Hemoglobin": {"گروپ": "خوێن", "نۆرماڵ": (12.0, 16.0), "یەکە": "g/dL", "تەفسیر": "هیمۆگلۆبین", "ئامێر": "هیمۆگلۆبینۆمیتەر", "تێبینی": ""},
    "Platelets": {"گروپ": "خوێن", "نۆرماڵ": (150, 450), "یەکە": "x10³/µL", "تەفسیر": "پلەیتلێت", "ئامێر": "ئۆتۆماتیک سێل کاونتر", "تێبینی": ""},
    "MCV": {"گروپ": "خوێن", "نۆرماڵ": (80, 100), "یەکە": "fL", "تەفسیر": "قەبارەی خڕۆکە سوورەکان", "ئامێر": "ئۆتۆماتیک سێل کاونتر", "تێبینی": ""},
    "Ferritin": {"گروپ": "خوێن", "نۆرماڵ": (15, 300), "یەکە": "ng/mL", "تەفسیر": "ئاسن", "ئامێر": "کیمیایی ئیمینۆ", "تێبینی": ""},
    "Vitamin B12": {"گروپ": "خوێن", "نۆرماڵ": (200, 900), "یەکە": "pg/mL", "تەفسیر": "ڤیتامین B12", "ئامێر": "کیمیایی ئیمینۆ", "تێبینی": ""},
    "Folate": {"گروپ": "خوێن", "نۆرماڵ": (3, 17), "یەکە": "ng/mL", "تەفسیر": "فۆلیک ئەسید", "ئامێر": "کیمیایی ئیمینۆ", "تێبینی": ""},
    "ESR": {"گروپ": "خوێن", "نۆرماڵ": (0, 20), "یەکە": "mm/hr", "تەفسیر": "خێرایی تەنیشتن", "ئامێر": "ESR ئۆتۆماتیک", "تێبینی": ""},
    "CRP": {"گروپ": "خوێن", "نۆرماڵ": (0, 5), "یەکە": "mg/L", "تەفسیر": "پروتێینی هەوکردن", "ئامێر": "توربیدیمیتەر", "تێبینی": ""},
    "Glucose": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (70, 126), "یەکە": "mg/dL", "تەفسیر": "شەکری خوێن", "ئامێر": "گلوکۆمیتەر", "تێبینی": ""},
    "HbA1c": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (4.0, 5.6), "یەکە": "%", "تەفسیر": "شەکری درێژخایەن", "ئامێر": "HPLC", "تێبینی": ""},
    "Creatinine": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (0.6, 1.3), "یەکە": "mg/dL", "تەفسیر": "کارایی گورچیلە", "ئامێر": "سپێکترۆفۆتۆمیتەر", "تێبینی": ""},
    "BUN": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (7, 20), "یەکە": "mg/dL", "تەفسیر": "نایترۆجینی یوریا", "ئامێر": "سپێکترۆفۆتۆمیتەر", "تێبینی": ""},
    "ALT": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (10, 40), "یەکە": "U/L", "تەفسیر": "ئەنزیمی جگەر", "ئامێر": "سپێکترۆفۆتۆمیتەر", "تێبینی": ""},
    "AST": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (10, 40), "یەکە": "U/L", "تەفسیر": "ئەنزیمی جگەر", "ئامێر": "سپێکترۆفۆتۆمیتەر", "تێبینی": ""},
    "Bilirubin": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (0.1, 1.2), "یەکە": "mg/dL", "تەفسیر": "زەرداوی", "ئامێر": "سپێکترۆفۆتۆمیتەر", "تێبینی": ""},
    "Albumin": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (3.5, 5.0), "یەکە": "g/dL", "تەفسیر": "ئەلبومین", "ئامێر": "سپێکترۆفۆتۆمیتەر", "تێبینی": ""},
    "Potassium": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (3.5, 5.0), "یەکە": "mmol/L", "تەفسیر": "پۆتاسیۆم", "ئامێر": "ئایۆن سەلێکت یوڤ", "تێبینی": ""},
    "Sodium": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (135, 145), "یەکە": "mmol/L", "تەفسیر": "سۆدیۆم", "ئامێر": "ئایۆن سەلێکت یوڤ", "تێبینی": ""},
    "Calcium": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (8.5, 10.5), "یەکە": "mg/dL", "تەفسیر": "کالسیۆم", "ئامێر": "سپێکترۆفۆتۆمیتەر", "تێبینی": ""},
    "Cholesterol": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (0, 200), "یەکە": "mg/dL", "تەفسیر": "کۆلسترۆل", "ئامێر": "سپێکترۆفۆتۆمیتەر", "تێبینی": ""},
    "LDL": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (0, 100), "یەکە": "mg/dL", "تەفسیر": "کۆلسترۆلی خراپ", "ئامێر": "سپێکترۆفۆتۆمیتەر", "تێبینی": ""},
    "HDL": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (40, 60), "یەکە": "mg/dL", "تەفسیر": "کۆلسترۆلی باش", "ئامێر": "سپێکترۆفۆتۆمیتەر", "تێبینی": ""},
    "Triglycerides": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (0, 150), "یەکە": "mg/dL", "تەفسیر": "تریگلیسیرید", "ئامێر": "سپێکترۆفۆتۆمیتەر", "تێبینی": ""},
    "Troponin I": {"گروپ": "دڵ", "نۆرماڵ": (0, 0.04), "یەکە": "ng/mL", "تەفسیر": "پروتێینی دڵ", "ئامێر": "کیمیایی ئیمینۆ", "تێبینی": ""},
    "CK-MB": {"گروپ": "دڵ", "نۆرماڵ": (0, 5), "یەکە": "ng/mL", "تەفسیر": "ئەنزیمی دڵ", "ئامێر": "کیمیایی ئیمینۆ", "تێبینی": ""},
    "BNP": {"گروپ": "دڵ", "نۆرماڵ": (0, 100), "یەکە": "pg/mL", "تەفسیر": "پروتێینی دڵ", "ئامێر": "کیمیایی ئیمینۆ", "تێبینی": ""},
    "TSH": {"گروپ": "هۆرمۆن", "نۆرماڵ": (0.4, 4.0), "یەکە": "mIU/L", "تەفسیر": "هۆرمۆنی دروان", "ئامێر": "کیمیایی ئیمینۆ", "تێبینی": ""},
    "T4": {"گروپ": "هۆرمۆن", "نۆرماڵ": (5, 12), "یەکە": "μg/dL", "تەفسیر": "هۆرمۆنی دروان", "ئامێر": "کیمیایی ئیمینۆ", "تێبینی": ""},
    "Cortisol": {"گروپ": "هۆرمۆن", "نۆرماڵ": (5, 25), "یەکە": "μg/dL", "تەفسیر": "هۆرمۆنی پەستانی خوێن", "ئامێر": "کیمیایی ئیمینۆ", "تێبینی": ""},
    "Insulin": {"گروپ": "هۆرمۆن", "نۆرماڵ": (2, 25), "یەکە": "μIU/mL", "تەفسیر": "هۆرمۆنی شەکر", "ئامێر": "کیمیایی ئیمینۆ", "تێبینی": ""},
    "Testosterone": {"گروپ": "هۆرمۆن", "نۆرماڵ": (300, 1000), "یەکە": "ng/dL", "تەفسیر": "هۆرمۆنی نێر", "ئامێر": "کیمیایی ئیمینۆ", "تێبینی": ""},
    "Vitamin D": {"گروپ": "ڤیتامین", "نۆرماڵ": (30, 100), "یەکە": "ng/mL", "تەفسیر": "ڤیتامین D", "ئامێر": "کیمیایی ئیمینۆ", "تێبینی": ""},
    "Urine Protein": {"گروپ": "میز", "نۆرماڵ": (0, 0.3), "یەکە": "g/24h", "تەفسیر": "پڕۆتینی میز", "ئامێر": "سپێکترۆفۆتۆمیتەر", "تێبینی": ""},
    "Urine Glucose": {"گروپ": "میز", "نۆرماڵ": (0, 0), "یەکە": "mg/dL", "تەفسیر": "شەکری میز", "ئامێر": "سپێکترۆفۆتۆمیتەر", "تێبینی": ""}
}

# ================================
# 6. داتابەسی دەرمانەکان
# ================================
DRUG_DATABASE = {
    "دژە پەستانی خوێن": {
        "کاپتۆپریل": {"ڕێژە": "25-50mg", "میکانیزم": "ACE inhibitor", "کاریگەری لاوەکی": "کۆخە, سەرگێژخواردن", "پێچەوانە": "حەملی دووگانی", "وەسف": "دەرمانی ACE inhibitor", "بۆچی": "بۆ کەمکردنەوەی پەستانی خوێن و پاراستنی گورچیلە", "تێبینی": ""},
        "ئەملۆدیپین": {"ڕێژە": "5-10mg", "میکانیزم": "Calcium channel blocker", "کاریگەری لاوەکی": "ئاوسانی قاچ", "پێچەوانە": "هەستیاری", "وەسف": "بەربەستەری کالسیۆم", "بۆچی": "بۆ چارەسەری پەستانی خوێن و ئازاری سنگ", "تێبینی": ""},
        "لۆسارتان": {"ڕێژە": "50-100mg", "میکانیزم": "ARB", "کاریگەری لاوەکی": "سەرگێژخواردن", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "بەربەستەری گیرۆدەی ئەنجیۆتێنسین", "بۆچی": "بۆ چارەسەری پەستانی خوێن", "تێبینی": ""},
        "فورۆسیماید": {"ڕێژە": "20-40mg", "میکانیزم": "Loop diuretic", "کاریگەری لاوەکی": "نزمی پۆتاسیۆم", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "دەرمانی دەرکەری بەهێز", "بۆچی": "بۆ چارەسەری پەستانی خوێن و ئاوسان", "تێبینی": ""}
    },
    "دژە شەکرە": {
        "مێتفۆرمین": {"ڕێژە": "500-2000mg", "میکانیزم": "Biguanide", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "دەرمانی هێڵی یەکەم بۆ شەکرە", "بۆچی": "بۆ کۆنتڕۆڵکردنی شەکری خوێن", "تێبینی": ""},
        "گلیپیزاید": {"ڕێژە": "5-20mg", "میکانیزم": "Sulfonylurea", "کاریگەری لاوەکی": "هایپۆگلایسیمیا", "پێچەوانە": "هەستیاری", "وەسف": "دەرمانی سەلفۆنیل یوریا", "بۆچی": "بۆ کەمکردنەوەی شەکری خوێن", "تێبینی": ""},
        "ئەنسولین Glargine": {"ڕێژە": "10-40 IU", "میکانیزم": "Insulin analog", "کاریگەری لاوەکی": "هایپۆگلایسیمیا", "پێچەوانە": "هایپۆگلایسیمیا", "وەسف": "ئەنسولینی درێژخایەن", "بۆچی": "بۆ کۆنتڕۆڵی شەکری خوێن", "تێبینی": ""}
    },
    "دژە کۆخە و هەوکردن": {
        "ئەمۆکسیسیلین": {"ڕێژە": "500mg", "میکانیزم": "Beta-lactam", "کاریگەری لاوەکی": "زکچوون", "پێچەوانە": "هەستیاری پێنیسیلین", "وەسف": "ئەنتیبایۆتیکی پێنیسیلین", "بۆچی": "بۆ هەوکردنی بەکتریایی", "تێبینی": ""},
        "ئازیترۆمایسین": {"ڕێژە": "250-500mg", "میکانیزم": "Macrolide", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "نەخۆشی دڵ", "وەسف": "ئەنتیبایۆتیکی ماکرۆلید", "بۆچی": "بۆ هەوکردنی هەناسە", "تێبینی": ""},
        "سیپرۆفلۆکساسین": {"ڕێژە": "500mg", "میکانیزم": "Fluoroquinolone", "کاریگەری لاوەکی": "ئازاری ماسوولکە", "پێچەوانە": "منداڵان", "وەسف": "ئەنتیبایۆتیکی فلۆرۆکینۆلۆن", "بۆچی": "بۆ هەوکردنی میز و سییەکان", "تێبینی": ""}
    },
    "دژە ئازار": {
        "ئەسپیرین": {"ڕێژە": "75-300mg", "میکانیزم": "NSAID", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "خوێنبەربوون", "وەسف": "دژە ئازار و دژە تەمەن", "بۆچی": "بۆ ئازار و پێشگیری لە خوێن مەبەست", "تێبینی": ""},
        "ئیبۆپروفین": {"ڕێژە": "200-400mg", "میکانیزم": "NSAID", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "دژە ئازار و دژە هەوکردن", "بۆچی": "بۆ ئازاری ماسوولکە و سەرئێشە", "تێبینی": ""},
        "پاراستامۆل": {"ڕێژە": "500-1000mg", "میکانیزم": "Analgesic", "کاریگەری لاوەکی": "زیان بە جگەر", "پێچەوانە": "نەخۆشی جگەر", "وەسف": "دژە ئازار و دژە تەمەن", "بۆچی": "بۆ ئازاری سەرئێشە و تا", "تێبینی": ""},
        "مۆرفین": {"ڕێژە": "5-10mg", "میکانیزم": "Opioid", "کاریگەری لاوەکی": "خەوی", "پێچەوانە": "نەخۆشی هەناسە", "وەسف": "دژە ئازاری بەهێز", "بۆچی": "بۆ ئازاری توند", "تێبینی": ""}
    },
    "دژە خوێن": {
        "وارفارین": {"ڕێژە": "5mg", "میکانیزم": "Vitamin K antagonist", "کاریگەری لاوەکی": "خوێنبەربوون", "پێچەوانە": "حەمل", "وەسف": "دژە خوێن", "بۆچی": "بۆ پێشگیری لە مەبەست", "تێبینی": ""},
        "هێپارین": {"ڕێژە": "5000 IU", "میکانیزم": "Anticoagulant", "کاریگەری لاوەکی": "خوێنبەربوون", "پێچەوانە": "خوێنبەربوون", "وەسف": "دژە خوێنی خێرا", "بۆچی": "بۆ پێشگیری لە مەبەست", "تێبینی": ""}
    },
    "دژە سکچوون": {
        "ئومەپرازۆل": {"ڕێژە": "20-40mg", "میکانیزم": "PPI", "کاریگەری لاوەکی": "سەرئێشە", "پێچەوانە": "نەخۆشی جگەر", "وەسف": "بەربەستەری پمپەی پرۆتۆن", "بۆچی": "بۆ چارەسەری سکچوون و برینداری گەدە", "تێبینی": ""}
    },
    "دژە کۆکە": {
        "سالبوتامۆل": {"ڕێژە": "2 puffs", "میکانیزم": "Beta-2 agonist", "کاریگەری لاوەکی": "لەرزین", "پێچەوانە": "نەخۆشی دڵ", "وەسف": "فراوانکەری بۆڕی هەناسە", "بۆچی": "بۆ چارەسەری کۆکە", "تێبینی": ""}
    }
}

# Drug Interactions Database
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
# 7. فانکشنە یارمەتیدەرەکان
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

def get_risk_color(risk_level: str) -> str:
    colors = {"زۆر مەترسیدار": "#ff6b6b", "مەترسیدار": "#ffd93d", "مامناوەند": "#ffc107", "کەم": "#6bcb77"}
    return colors.get(risk_level, "#6c757d")

def check_drug_interactions(drugs: List[str]) -> List[Dict]:
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

def get_leaderboard_data() -> pd.DataFrame:
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
    clinical_notes = load_clinical_notes()
    if username not in clinical_notes:
        clinical_notes[username] = []
    note["timestamp"] = datetime.now().isoformat()
    clinical_notes[username].append(note)
    save_clinical_notes(clinical_notes)

def get_clinical_notes(username: str) -> List:
    clinical_notes = load_clinical_notes()
    return clinical_notes.get(username, [])

def fetch_medical_news() -> List:
    return [
        {"title": "دۆزینەوەی دەرمانێکی نوێ بۆ شەکرە", "summary": "توێژینەوەیەکی نوێ دەرمانێکی کاریگەر بۆ چارەسەری شەکرەی جۆری ٢ دەدۆزێتەوە", "source": "PubMed", "date": "2024-01-15"},
        {"title": "پێشکەوتن لە چارەسەری نەخۆشی دڵ", "summary": "ڕێگەیەکی نوێ بۆ چارەسەری نەخۆشی دڵی ئیسکیمیک پەرەی پێدراوە", "source": "The Lancet", "date": "2024-01-10"},
        {"title": "کوتانی نوێ بۆ نەخۆشی سیل", "summary": "کوتانێکی نوێ بۆ نەخۆشی سیل لە تاقیکردنەوەکاندا ئەنجامی باشی نیشان داوە", "source": "WHO", "date": "2024-01-05"},
        {"title": "پەیوەندی نێوان شێوازی خواردن و نەخۆشی جگەر", "summary": "توێژینەوە نوێیەکان پەیوەندی نێوان شێوازی خواردنی چەور و نەخۆشی جگەری چەور دەردەخەن", "source": "NEJM", "date": "2024-01-01"}
    ]

def update_spaced_repetition(username: str, item: str, item_type: str, correct: bool):
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

def generate_comprehensive_exam(num_questions: int = 100) -> List[Dict]:
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

def generate_microscope_view(cell_type: str) -> None:
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
# 8. ستەیتەکانی ئەپ
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

# ================================
# 9. پەڕەی لۆگین
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
# 10. سایدبار - ڕێدیزاینی تەواو
# ================================
with st.sidebar:
    # Calculate user stats
    level = get_user_level(st.session_state.quiz_score)
    level_info = get_level_info(level)
    xp_progress = get_level_progress(st.session_state.quiz_score)
    xp_points = st.session_state.xp_points
    quiz_score = st.session_state.quiz_score
    streak_days = st.session_state.streak_days
    total_cases = st.session_state.total_cases_solved
    username = st.session_state.username
    level_icon = get_level_icon(level)
    level_name = level_info['name']
    
    # Logo and Brand
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <div style="font-size: 3rem; margin-bottom: 0.5rem; filter: drop-shadow(0 0 20px rgba(99, 102, 241, 0.4));">🩺</div>
        <div style="font-size: 1.8rem; font-weight: 800; background: linear-gradient(135deg, #6366f1, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
            Dr.Danyal
        </div>
        <div style="font-size: 0.7rem; color: rgba(255,255,255,0.4); letter-spacing: 2px; text-transform: uppercase;">
            Medical Trainer
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # User Profile Section
    st.markdown(f"""
    <div class="sidebar-profile">
        <div class="sidebar-avatar">
            {level_icon}
        </div>
        <div class="sidebar-username">{username}</div>
        <div class="sidebar-level-badge">
            {level_icon} {level_name}
        </div>
        
        <!-- Stats Grid -->
        <div class="sidebar-stats">
            <div class="sidebar-stat-item">
                <div class="sidebar-stat-value">⭐ {xp_points}</div>
                <div class="sidebar-stat-label">XP</div>
            </div>
            <div class="sidebar-stat-item">
                <div class="sidebar-stat-value">📊 {quiz_score}</div>
                <div class="sidebar-stat-label">Quiz</div>
            </div>
            <div class="sidebar-stat-item">
                <div class="sidebar-stat-value">🔥 {streak_days}</div>
                <div class="sidebar-stat-label">Streak</div>
            </div>
            <div class="sidebar-stat-item">
                <div class="sidebar-stat-value">🩺 {total_cases}</div>
                <div class="sidebar-stat-label">Cases</div>
            </div>
        </div>
        
        <!-- XP Progress -->
        <div class="sidebar-xp-container">
            <div class="sidebar-xp-bar">
                <div class="sidebar-xp-fill" style="width: {xp_progress:.1f}%;"></div>
            </div>
            <div class="sidebar-xp-text">Level Progress: {xp_progress:.0f}%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Online Status
    st.markdown(f"""
    <div style="display: flex; align-items: center; padding: 0.3rem 0.5rem; font-size: 0.8rem; margin-bottom: 0.5rem;">
        <span class="active-dot"></span>
        <span style="color: rgba(255,255,255,0.6); margin-left: 0.5rem;">Online Now</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation Menu
    st.markdown('<div class="sidebar-nav">', unsafe_allow_html=True)
    
    # Main Navigation
    st.markdown('<div class="sidebar-nav-section">📋 MAIN</div>', unsafe_allow_html=True)
    main_page = st.radio(
        "",
        [
            "🏠 داشبۆرد",
            "📚 نەخۆشییەکان",
            "🩺 شیکاری کەیس",
            "📝 کویز (ئاستی)",
            "📋 تاقیکردنەوەی گشتی",
        ],
        key="main_nav",
        label_visibility="collapsed"
    )
    
    # Learning Tools
    st.markdown('<div class="sidebar-nav-section">📖 LEARNING</div>', unsafe_allow_html=True)
    learning_page = st.radio(
        "",
        [
            "🔄 دووبارەکردنەوە",
            "🔬 تاقیگە",
            "💊 فارماکۆلۆجی",
            "⚠️ کارلێکی دەرمانەکان",
        ],
        key="learning_nav",
        label_visibility="collapsed"
    )
    
    # Community
    st.markdown('<div class="sidebar-nav-section">👥 COMMUNITY</div>', unsafe_allow_html=True)
    community_page = st.radio(
        "",
        [
            "🏆 خشتەی ڕێزلێنان",
            "👥 هاوڕێی خوێندن",
            "📰 هەواڵی پزیشکی",
        ],
        key="community_nav",
        label_visibility="collapsed"
    )
    
    # Advanced
    st.markdown('<div class="sidebar-nav-section">🔬 ADVANCED</div>', unsafe_allow_html=True)
    advanced_page = st.radio(
        "",
        [
            "🔬 میکرۆسکۆپ",
            "📝 یاداشتی کلینیکی",
            "🧠 AI یاریدەدەر",
            "🏆 دەستکەوتەکان",
        ],
        key="advanced_nav",
        label_visibility="collapsed"
    )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Determine which page is selected (use the last changed radio)
    # We need to track which radio was changed last
    page = main_page
    
    st.markdown("---")
    
    # Version and Footer
    st.markdown("""
    <div class="sidebar-footer">
        <span class="sidebar-version">v8.0 Ultra</span>
        <div class="sidebar-footer-text">
            © 2024 Dr.Danyal<br>
            All rights reserved
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Logout Button
    if st.button("🚪 چوونە دەرەوە", key="logout_btn", use_container_width=True):
        auto_save()
        st.session_state.logged_in = False
        st.rerun()

# ================================
# 11. پەڕەکان
# ================================

if page == "🏠 داشبۆرد":
    st.markdown("""
    <div class="main">
        <div style="text-align: center; padding: 2rem 0;">
            <span class="dr-icon">🩺</span>
            <h1 class="main-header">🎓 ڕاهێنەری پزیشکی Pro Max Ultra</h1>
        </div>
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
    
    # Recent activity section
    st.markdown("### 📊 چالاکییەکانی ئەم دواییە")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="case-card">
            <h4>📝 کویزەکان</h4>
            <p>نمرەی گشتی: {st.session_state.quiz_score}/100</p>
            <p>ئاست: {get_level_icon(level)} {level_info['name']}</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="case-card">
            <h4>🩺 کەیسەکان</h4>
            <p>کەیسەکانی شیکارکراو: {st.session_state.total_cases_solved}</p>
            <p>دەستنیشانکردنی ڕاست: {st.session_state.correct_diagnoses}</p>
        </div>
        """, unsafe_allow_html=True)

elif page == "📚 نەخۆشییەکان":
    st.markdown(f"<h2>📚 کتێبخانەی نەخۆشییەکان - {get_disease_count()} نەخۆشی</h2>", unsafe_allow_html=True)
    
    search = st.text_input("🔍 گەڕان:")
    filter_risk = st.selectbox("فلتر:", ["هەموو", "زۆر مەترسیدار", "مەترسیدار", "مامناوەند", "کەم"])
    
    filtered = {k: v for k, v in DISEASE_DATABASE.items() if (not search or search in k)}
    if filter_risk != "هەموو":
        filtered = {k: v for k, v in filtered.items() if v.get('ئاستی مەترسی') == filter_risk}
    
    cols = st.columns(2)
    idx = 0
    for disease, info in filtered.items():
        with cols[idx % 2]:
            with st.expander(f"🩺 {disease}"):
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
    st.markdown("<h2>📝 کویزی پزیشکی</h2>", unsafe_allow_html=True)
    
    level = get_user_level(st.session_state.quiz_score)
    level_info = get_level_info(level)
    
    # Simple quiz generation
    diseases = list(DISEASE_DATABASE.keys())
    if diseases:
        disease = random.choice(diseases)
        info = DISEASE_DATABASE[disease]
        correct_answer = info['نیشانەکان'][0] if info['نیشانەکان'] else "نەزانراو"
        
        wrong_answers = []
        for d in diseases:
            if d != disease:
                other_info = DISEASE_DATABASE[d]
                if other_info['نیشانەکان']:
                    wrong = other_info['نیشانەکان'][0]
                    if wrong != correct_answer and wrong not in wrong_answers:
                        wrong_answers.append(wrong)
                    if len(wrong_answers) >= 3:
                        break
        
        options = [correct_answer] + wrong_answers[:3]
        random.shuffle(options)
        
        st.markdown(f"""
        <div class="quiz-card">
            <h3>کام نیشانە تایبەتە بە {disease}؟</h3>
            <p style="color: #888;">ئاست: {get_level_icon(level)} {level_info['name']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        answer = st.radio("وەڵام:", options, key="quiz_answer")
        
        if st.button("✅ پشتڕاستکردنەوە", type="primary"):
            if answer == correct_answer:
                st.session_state.quiz_score += 1
                add_xp(st.session_state.username, 10)
                st.success("🎉 ڕاستە!")
            else:
                st.error(f"❌ هەڵەیە. ڕاست: {correct_answer}")
            st.rerun()

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

elif page == "🔬 تاقیگە":
    st.markdown("<h2>🔬 تاقیگەی ڤێرچواڵ</h2>", unsafe_allow_html=True)
    
    search_lab = st.text_input("🔍 گەڕان:")
    
    all_lab_tests = {**LAB_TESTS, **st.session_state.custom_lab_tests}
    
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
    
    # Show locked achievements
    st.markdown("### 🔒 دەستکەوتە داخراوەکان")
    for ach in all_achievements:
        if ach["name"] not in st.session_state.achievements:
            st.markdown(f'<span class="achievement-badge" style="opacity:0.5;">{ach["icon"]} {ach["name"]} 🔒</span>', unsafe_allow_html=True)

# ================================
# 12. فووەتەر
# ================================
st.markdown("---")
st.markdown(f"""
<div class="footer-style">
    <h3>🩺 Dr.Danyal - ڕاهێنەری پزیشکی Pro Max Ultra v8.0</h3>
    <p>© {datetime.now().year} - هەموو مافێک پارێزراوە</p>
    <p style="font-size:0.8rem; color: rgba(255,255,255,0.4);">
        {get_disease_count()} نەخۆشی | {get_drug_count()} دەرمان | {get_lab_count()} پشکنینی تاقیگە
    </p>
</div>
""", unsafe_allow_html=True)
