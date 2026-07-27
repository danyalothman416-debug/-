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
        "custom_drugs": {},
        "quiz_history": [],
        "case_history": []
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
# 2. CSS و ستایلە پێشکەوتووەکان (وەک خۆی پارێزراوە)
# ================================
st.markdown("""
<style>
    /* CSS Code from the original prompt - kept exactly the same for style consistency */
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
    
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown span,
    [data-testid="stSidebar"] label {
        color: rgba(255, 255, 255, 0.85) !important;
        font-weight: 400 !important;
    }
    
    [data-testid="stSidebar"] hr {
        border-color: rgba(79, 172, 254, 0.2) !important;
    }
    
    [data-testid="stSidebar"] .stRadio > div {
        background: rgba(255, 255, 255, 0.03) !important;
        border-radius: 16px !important;
        padding: 8px !important;
        border: 1px solid rgba(79, 172, 254, 0.15) !important;
        transition: all 0.3s ease !important;
    }
    
    [data-testid="stSidebar"] .stRadio > div:hover {
        background: rgba(79, 172, 254, 0.08) !important;
        border-color: rgba(79, 172, 254, 0.3) !important;
    }
    
    [data-testid="stSidebar"] .stRadio [role="radiogroup"] label {
        transition: all 0.3s ease !important;
        padding: 6px 12px !important;
        border-radius: 12px !important;
    }
    
    [data-testid="stSidebar"] .stRadio [role="radiogroup"] label:hover {
        background: rgba(79, 172, 254, 0.1) !important;
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
    .logo-sub {
        font-size: 0.9rem;
        color: rgba(255,255,255,0.6);
        -webkit-text-fill-color: rgba(255,255,255,0.6);
        text-align: center;
        margin-top: -5px;
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
    
    @keyframes glow {
        0% { box-shadow: 0 0 20px rgba(102, 126, 234, 0.3); }
        50% { box-shadow: 0 0 60px rgba(102, 126, 234, 0.6), 0 0 100px rgba(118, 75, 162, 0.3); }
        100% { box-shadow: 0 0 20px rgba(102, 126, 234, 0.3); }
    }
    
    @keyframes shimmer {
        0% { background-position: 400% 0; }
        100% { background-position: -400% 0; }
    }
    
    @keyframes iconFloat {
        0% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-15px) rotate(5deg); }
        100% { transform: translateY(0px) rotate(0deg); }
    }
    
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
    
    @keyframes shine {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
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
    
    .tab-container {
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(20px);
        padding: 2.8rem;
        border-radius: 28px;
        box-shadow: 0 10px 45px rgba(0,0,0,0.1);
        margin: 1.5rem 0;
        border: 1px solid rgba(255, 255, 255, 0.04);
        color: #fff;
        animation: fadeIn 0.8s ease-out;
    }
    
    .button-primary {
        background: linear-gradient(135deg, #667eea, #764ba2, #f093fb);
        color: white;
        border: none;
        padding: 1.1rem 3rem;
        border-radius: 20px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        font-size: 1.1rem;
        letter-spacing: 0.5px;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .button-primary::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 60%);
        transform: rotate(45deg);
        transition: all 0.6s ease;
    }
    
    .button-primary:hover {
        transform: scale(1.06);
        box-shadow: 0 20px 50px rgba(102, 126, 234, 0.5);
    }
    
    .button-primary:hover::before {
        transform: rotate(45deg) scale(1.5);
    }
    
    .medication-card {
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin: 0.8rem 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        color: #fff;
        position: relative;
        padding-left: 20px;
    }
    
    .medication-card::before {
        content: '💊';
        position: absolute;
        left: -5px;
        top: 50%;
        transform: translateY(-50%);
        font-size: 2rem;
        opacity: 0.15;
    }
    
    .medication-card:hover {
        background: rgba(255, 255, 255, 0.08);
        border-color: #667eea;
        transform: translateX(10px);
    }
    
    .level-badge {
        display: inline-block;
        padding: 0.3rem 1.2rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.8rem;
        margin: 0.2rem;
        transition: all 0.3s ease;
    }
    
    .level-1 { background: rgba(40, 167, 69, 0.3); color: #6bcb77; border: 1px solid rgba(40, 167, 69, 0.2); }
    .level-2 { background: rgba(23, 162, 184, 0.3); color: #5bc0de; border: 1px solid rgba(23, 162, 184, 0.2); }
    .level-3 { background: rgba(255, 193, 7, 0.3); color: #ffd93d; border: 1px solid rgba(255, 193, 7, 0.2); }
    .level-4 { background: rgba(255, 153, 0, 0.3); color: #ff9f1c; border: 1px solid rgba(255, 153, 0, 0.2); }
    .level-5 { background: rgba(220, 53, 69, 0.3); color: #ff6b6b; border: 1px solid rgba(220, 53, 69, 0.2); }
    
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
    
    .quiz-level-progress {
        background: rgba(255, 255, 255, 0.04);
        padding: 1rem 2rem;
        border-radius: 18px;
        margin: 0.5rem 0;
        border: 1px solid rgba(255, 255, 255, 0.05);
        transition: all 0.3s ease;
    }
    
    .quiz-level-progress:hover {
        background: rgba(255, 255, 255, 0.08);
        transform: scale(1.01);
    }
    
    .notification-toast {
        position: fixed;
        top: 20px;
        right: 20px;
        background: linear-gradient(135deg, #28a745, #20c997);
        color: white;
        padding: 1.2rem 2.5rem;
        border-radius: 15px;
        box-shadow: 0 10px 35px rgba(0,0,0,0.3);
        z-index: 1000;
        animation: slideInRight 0.5s ease;
        font-weight: bold;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(100px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    .timeline-item {
        padding: 1rem 1.8rem;
        border-left: 4px solid #667eea;
        margin: 0.8rem 0;
        background: rgba(255, 255, 255, 0.04);
        border-radius: 0 16px 16px 0;
        transition: all 0.3s ease;
        color: #ddd;
    }
    
    .timeline-item:hover {
        background: rgba(255, 255, 255, 0.08);
        transform: translateX(8px);
    }
    
    .timeline-item .time {
        font-size: 0.8rem;
        color: #888;
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
# 3. سیستەمی ئاستەکان (Levels) - وەک خۆی پارێزراوە
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
# 4. داتابەسی نەخۆشییەکان (١٠٠+ نەخۆشی) - بە شێوەیەکی بەرچاو فراوان کراوە
# ================================
DISEASE_DATABASE = {
    # === نەخۆشییەکانی کۆئەندامی هەرس و مێتابۆلیک (Metabolic & Endocrine) ===
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
    "کەمکاریی دەرقی (Hypothyroidism)": {
        "نیشانەکان": ["ماندوویی", "کێش زیادکردن", "هەستی ساردی", "ڕەقبوونی پێست", "قژ ڕژان", "خەمۆکی", "بیرچوونەوە"],
        "پشکنینەکان": {"TSH": "بەرز", "Free T4": "نزم", "Anti-TPO": "positive (ئەگەر هاشیمۆتۆ)"},
        "چارەسەر": ["لیڤۆتایرۆکسین (Levothyroxine)", "پشکنینی TSH بەردەوام"],
        "ئاستی مەترسی": "کەم",
        "تایبەتمەندی": "TSH بەرز + T4 نزم",
        "ڕێپیشگیری": ["پشکنینی ڕۆتینی TSH لە کەسانی مەترسیدار"],
        "گروپی تەمەن": "تەمەن > 60 ساڵ، ژنان",
        "ڕێژەی تووشبوون": "5%",
        "جۆری نەخۆشی": "هۆرمۆنی"
    },
    "زیادکاریی دەرقی (Hyperthyroidism)": {
        "نیشانەکان": ["کێش کەمبوونەوە", "خێرالێدانی دڵ", "لەرزین", "ئارەقەکردن", "بێتاقەتی", "چاو هەڵهاتن (Graves)"],
        "پشکنینەکان": {"TSH": "نزم", "Free T4": "بەرز", "Free T3": "بەرز", "TSI": "positive (Graves)"},
        "چارەسەر": ["مێتیمازۆل (Methimazole)", "پڕۆپیل تیۆراسیل (PTU)", "یۆدی ڕادیۆئەکتیڤ", "نەشتەرگەری"],
        "ئاستی مەترسی": "مامناوەند",
        "تایبەتمەندی": "TSH نزم + T4 بەرز + T3 بەرز",
        "ڕێپیشگیری": ["پشکنینی ڕۆتین"],
        "گروپی تەمەن": "ژنانی گەنج و تەمەن مامناوەند",
        "ڕێژەی تووشبوون": "1.2%",
        "جۆری نەخۆشی": "هۆرمۆنی"
    },
    "نەخۆشی کۆن (Gout)": {
        "نیشانەکان": ["ئازاری چەقڵی گەورەی پێ", "ئاوسان", "سووربوونەوە", "سختی جومگە"],
        "پشکنینەکان": {"Uric Acid": "بەرز (>7 mg/dL)", "Synovial fluid analysis": "Monosodium urate crystals"},
        "چارەسەر": ["NSAIDs", "کۆلشیسین", "Allopurinol (بۆ دڕێژخایەن)"],
        "ئاستی مەترسی": "کەم",
        "تایبەتمەندی": "ئازاری لەناکاوی شەوانە لە جومگەکان + Uric acid بەرز",
        "ڕێپیشگیری": ["کەمکردنەوەی پورین (گۆشت، ئەندامەکان)"],
        "گروپی تەمەن": "پیاوانی تەمەن مامناوەند و پیر",
        "ڕێژەی تووشبوون": "4%",
        "جۆری نەخۆشی": "مێتابۆلیک"
    },
    "ئۆستێپۆرۆسیس (Osteoporosis)": {
        "نیشانەکان": ["ئازاری پشت", "کەمبوونەوەی باڵا", "شکان بە ئاسانی"],
        "پشکنینەکان": {"DEXA Scan": "T-score < -2.5", "Calcium": "نۆرماڵ یان کەم", "Vitamin D": "نزم"},
        "چارەسەر": ["کالسیۆم", "ڤیتامین D", "Bisphosphonates (Alendronate)"],
        "ئاستی مەترسی": "مامناوەند",
        "تایبەتمەندی": "شکانێکی نزم تروما + T-score < -2.5",
        "ڕێپیشگیری": ["وەرزشی هەڵگری کێش", "خواردنی پڕ کالسیۆم"],
        "گروپی تەمەن": "ژنانی پاش وەستانی سووڕی مانگانە",
        "ڕێژەی تووشبوون": "10% (ژنانی >50)",
        "جۆری نەخۆشی": "ئێسک"
    },
    "گەشکە (Rickets/Osteomalacia)": {
        "نیشانەکان": ["ئازاری ئێسک", "لەرزی ماسوولکە", "شێوانی ئێسک (لە منداڵان)"],
        "پشکنینەکان": {"Vitamin D": "نزم (<20 ng/mL)", "Calcium": "نزم", "Phosphorus": "نزم", "ALP": "بەرز"},
        "چارەسەر": ["ڤیتامین D", "کالسیۆم"],
        "ئاستی مەترسی": "کەم",
        "تایبەتمەندی": "Vitamin D نزم + کێشەی ئێسک",
        "ڕێپیشگیری": ["پڕکەری ڤیتامین D", "بەرکەوتنی خۆر"],
        "گروپی تەمەن": "منداڵان و پیران",
        "ڕێژەی تووشبوون": "کەمتر لە 1%",
        "جۆری نەخۆشی": "مێتابۆلیک/ئێسک"
    },

    # === نەخۆشییەکانی دڵ و خوێنبەرەکان (Cardiovascular) ===
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
    "نەخۆشی دڵی ڕیتم (Arrhythmia - AFib)": {
        "نیشانەکان": ["لێدانی دڵ ناڕێک", "سەرگێژخواردن", "کورتی هەناسە", "ئازاری سنگ", "خێرالێدانی دڵ"],
        "پشکنینەکان": {"ECG": "Absent P waves, irregularly irregular", "Holter": "Paroxysmal AFib", "Echocardiogram": "LA enlargement"},
        "چارەسەر": ["Beta blocker", "Calcium channel blocker", "Anticoagulant (Warfarin/DOAC)", "Cardioversion"],
        "ئاستی مەترسی": "مەترسیدار",
        "تایبەتمەندی": "ECG ناڕێک بێ P waves",
        "ڕێپیشگیری": ["پارێزی لە کافئین", "وەرزش", "پشکنینی بەردەوام"],
        "گروپی تەمەن": "تەمەن > 65 ساڵ",
        "ڕێژەی تووشبوون": "1.5%",
        "جۆری نەخۆشی": "دڵ و خوێن"
    },
    "هەوکردنی پەردەی دڵ (Pericarditis)": {
        "نیشانەکان": ["ئازاری تیژی سنگ (باشتر دەبێت بە دانیشتن)", "تا", "کورتی هەناسە"],
        "پشکنینەکان": {"ECG": "Diffuse ST elevation", "Echocardiogram": "Pericardial effusion", "CRP": "بەرز"},
        "چارەسەر": ["NSAIDs (Ibuprofen)", "Colchicine", "چارەسەری هۆکار"],
        "ئاستی مەترسی": "مامناوەند",
        "تایبەتمەندی": "ئازاری سنگ کە باشتر دەبێت بە دانیشتن + ST elevation گشتی",
        "ڕێپیشگیری": ["چارەسەری هەوکردنەکان"],
        "گروپی تەمەن": "گەنجان و تەمەن مامناوەند",
        "ڕێژەی تووشبوون": "0.1%",
        "جۆری نەخۆشی": "دڵ و خوێن"
    },
    "نەخۆشی خوێنبەری چواردەور (PAD)": {
        "نیشانەکان": ["ئازاری قاچ لە کاتی ڕۆیشتن (Claudication)", "ساردی قاچ", "برینی قاچ کە زوو چاک نابێت"],
        "پشکنینەکان": {"ABI": "<0.9", "Doppler Ultrasound": "تەنگی خوێنبەرەکان", "Angiography": " stenosis"},
        "چارەسەر": ["وەرزش", "Cilostazol", "Antiplatelet (Aspirin)", "Angioplasty"],
        "ئاستی مەترسی": "مەترسیدار",
        "تایبەتمەندی": "ABI < 0.9 + ئازاری قاچ لە کاتی ڕۆیشتن",
        "ڕێپیشگیری": ["وەستانی جگەرە", "کۆنتڕۆڵی شەکرە و چەوری"],
        "گروپی تەمەن": "تەمەن > 60 ساڵ، جگەرەکێشان",
        "ڕێژەی تووشبوون": "5% لە پیاوانی >60",
        "جۆری نەخۆشی": "دڵ و خوێن"
    },

    # === نەخۆشییەکانی هەناسەدان (Respiratory) ===
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
    "نەخۆشی کۆکە (Asthma)": {
        "نیشانەکان": ["هەناسەدان بە زەحمەت", "کۆخە", "تنگەنەفەسی", "فیشک (Wheezing)", "فشاری سنگ", "تەنگی هەناسە"],
        "پشکنینەکان": {"Pulmonary function": "FEV1 < 80%", "Peak flow": "کەم", "Chest X-ray": "نۆرماڵ", "IgE": "بەرز"},
        "چارەسەر": ["Bronchodilator (SABA)", "Steroid inhaler (ICS)", "پارێزی لە هۆکارەکان", "Leukotriene inhibitor"],
        "ئاستی مەترسی": "مامناوەند",
        "تایبەتمەندی": "FEV1 کەم + فیشک + Reversible",
        "ڕێپیشگیری": ["پارێزی لە هۆکارەکان", "بەکارهێنانی inhaler", "وەرزش"],
        "گروپی تەمەن": "منداڵان و گەنجان",
        "ڕێژەی تووشبوون": "5%",
        "جۆری نەخۆشی": "هەناسە"
    },
    "نەخۆشی کۆکە (COPD)": {
        "نیشانەکان": ["کۆخەی درێژخایەن", "تنگەنەفەسی", "هەناسەدان بە زەحمەت", "کەمبوونی کێش", "ماندوویی"],
        "پشکنینەکان": {"Pulmonary function": "FEV1/FVC < 70% (Not reversible)", "Chest X-ray": "Hyperinflation", "Blood gas": "نزم"},
        "چارەسەر": ["Bronchodilator (LAMA/LABA)", "Steroid (ICS)", "ئۆکسجین", "وەستانی جگەرە"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندی": "FEV1/FVC < 70% + مێژووی جگەرەکێشان",
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
        "تایبەتمەندی": "کۆخەی خوێناوی + X-ray تایبەت + AFB+",
        "ڕێپیشگیری": ["BCG vaccine", "پارێزی لە کەسانی تووشبوو", "پشکنین"],
        "گروپی تەمەن": "هەموو تەمەنەکان",
        "ڕێژەی تووشبوون": "0.5%",
        "جۆری نەخۆشی": "هەناسە"
    },
    "هەوکردنی کۆکی درێژخایەن (Bronchiectasis)": {
        "نیشانەکان": ["کۆخەی ڕۆژانە بە ڕژان", "هەناسەدان بە زەحمەت", "هەوکردنی دووبارە", "کەمبوونی کێش"],
        "پشکنینەکان": {"High-Resolution CT": "Tram-track opacities", "Sputum culture": "Pseudomonas/H. influenzae", "PFT": "Obstructive pattern"},
        "چارەسەر": ["Chest physiotherapy", "Antibiotics", "Bronchodilators", "Mucoactive agents"],
        "ئاستی مەترسی": "مەترسیدار",
        "تایبەتمەندی": "کۆخەی ڕۆژانەی بەرهەمدار + HRCT دۆزینەوەکان",
        "ڕێپیشگیری": ["چارەسەری هەوکردنەکان بە خێرایی", "کوتانی ئەنفلۆنزا و پنێومۆنیا"],
        "گروپی تەمەن": "تەمەن مامناوەند و پیر",
        "ڕێژەی تووشبوون": "0.1%",
        "جۆری نەخۆشی": "هەناسە"
    },
    "خەوی هەناسە بڕان (Sleep Apnea)": {
        "نیشانەکان": ["خەراپی خەو", "ماندوویی ڕۆژانە", "پڕۆشتن", "سەرئێشەی بەیانیان", "کێش زیادکردن"],
        "پشکنینەکان": {"Polysomnography": "AHI > 5", "O2 sat": "Desaturation لە شەودا"},
        "چارەسەر": ["CPAP", "کەمکردنەوەی کێش", "پارێزی لە خەو بە پشتدا"],
        "ئاستی مەترسی": "مامناوەند",
        "تایبەتمەندی": "پڕۆشتنی بەرز + ماندوویی ڕۆژانە + AHI > 5",
        "ڕێپیشگیری": ["پاراستنی کێشی تەندروست"],
        "گروپی تەمەن": "پیاوانی تەمەن مامناوەند بە کێشی زیاد",
        "ڕێژەی تووشبوون": "4%",
        "جۆری نەخۆشی": "هەناسە/دەماری"
    },

    # === نەخۆشییەکانی گورچیلە و میزەڕۆ (Renal & Urology) ===
    "نەخۆشی گورچیلەی درێژخایەن (CKD)": {
        "نیشانەکان": ["ئاوسانی ڕوو و قاچ", "میزی کەم", "ماندوویی", "سەرئێشە", "خوێن لە میزدا", "فشاری خوێن بەرز", "هەستی ساردی"],
        "پشکنینەکان": {"Creatinine": "بەرز >1.3", "BUN": "بەرز >20", "eGFR": "<60 (>3 مانگ)", "Urinalysis": "پڕۆتین + خوێن", "Potassium": "بەرز"},
        "چارەسەر": ["ACE inhibitor", "کەمکردنەوەی پڕۆتین", "کۆنتڕۆڵی BP", "دایەلیز (ئەگەر پێویست)"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندی": "eGFR <60 بۆ >3 مانگ",
        "ڕێپیشگیری": ["کۆنتڕۆڵی شەکرە", "کۆنتڕۆڵی BP", "کەمکردنەوەی نمەک"],
        "گروپی تەمەن": "تەمەن > 50 ساڵ",
        "ڕێژەی تووشبوون": "10%",
        "جۆری نەخۆشی": "گورچیلە"
    },
    "هەوکردنی میزەڕۆ (UTI)": {
        "نیشانەکان": ["ئازاری میزکردن", "میزی زۆر و بەردەوام", "هەستی پەلە بۆ میز", "ئازاری سکی خوارەوە", "میز بە خوێن", "میز تەڵخ"],
        "پشکنینەکان": {"Urinalysis": "Leukocyte esterase+, Nitrites+, WBCs", "Urine culture": "E. coli (>100k CFU)"},
        "چارەسەر": ["Nitrofurantoin", "Trimethoprim/Sulfamethoxazole", "Ciprofloxacin", "ئاوی زۆر"],
        "ئاستی مەترسی": "کەم",
        "تایبەتمەندی": "ئازاری میزکردن + Leukocyte esterase+",
        "ڕێپیشگیری": ["ئاوی زۆر", "پاکژی", "دەرچوونی میز پاش جووتبوون"],
        "گروپی تەمەن": "ژنان (تەمەنی منداڵبوون)",
        "ڕێژەی تووشبوون": "50% ی ژنان بە درێژایی ژیان",
        "جۆری نەخۆشی": "گورچیلە/میزەڕۆ"
    },
    "نەخۆشی گورچیلە بەرد (Kidney Stones)": {
        "نیشانەکان": ["ئازاری پشت (flank pain)", "خوێن لە میزدا", "سکچوون و ڕشانەوە", "تا", "ئازاری میزکردن"],
        "پشکنینەکان": {"CT Scan (non-contrast)": "بەرد", "Ultrasound": "Hydronephrosis", "Urinalysis": "خوێن + بەلۆر"},
        "چارەسەر": ["شلەمەنی", "دەرمانی ئازار (NSAIDs)", "Tamsulosin (بۆ دەرکردن)", "Lithotripsy"],
        "ئاستی مەترسی": "مامناوەند",
        "تایبەتمەندی": "ئازاری لەناکاوی flank + خوێن لە میزدا",
        "ڕێپیشگیری": ["ئاوی زۆر", "کەمکردنەوەی نمەک و پڕۆتینی ئاژەڵی"],
        "گروپی تەمەن": "تەمەن 30-50 ساڵ",
        "ڕێژەی تووشبوون": "8%",
        "جۆری نەخۆشی": "گورچیلە"
    },

    # === نەخۆشییەکانی کۆئەندامی هەرس (Gastroenterology) ===
    "نەخۆشی گەدە (Gastritis)": {
        "نیشانەکان": ["ئازاری گەدە", "سکچوون", "سووتانی گەدە", "ڕشانەوە", "هەستی پڕی"],
        "پشکنینەکان": {"Endoscopy": "هەوکردن", "H. pylori": "positive (Urea breath test)", "CBC": "نۆرماڵ"},
        "چارەسەر": ["PPI (Omeprazole)", "Antibiotic (Amoxicillin + Clarithromycin)", "Antacid", "گۆڕینی خواردن"],
        "ئاستی مەترسی": "کەم",
        "تایبەتمەندی": "ئازاری گەدە + H. pylori positive",
        "ڕێپیشگیری": ["خواردنی کەم بەهارات", "پارێزی لە NSAIDs"],
        "گروپی تەمەن": "هەموو تەمەنەکان",
        "ڕێژەی تووشبوون": "20%",
        "جۆری نەخۆشی": "گەدە"
    },
    "نەخۆشی گەدە (Peptic Ulcer Disease)": {
        "نیشانەکان": ["ئازاری گەدە", "سکچوون", "خوێن لە رشانەوە یان پیساییدا", "کێش کەمبوونەوە", "ئازاری شەو"],
        "پشکنینەکان": {"Endoscopy": "Ulcer", "H. pylori": "positive", "Barium swallow": "Ulcer crater"},
        "چارەسەر": ["PPI", "Antibiotic (ئەگەر H. pylori+)", "Sucralfate", "گۆڕینی خواردن"],
        "ئاستی مەترسی": "مەترسیدار",
        "تایبەتمەندی": "Ulcer لە Endoscopy",
        "ڕێپیشگیری": ["پارێزی لە NSAIDs", "پارێزی لە کحول و جگەرە"],
        "گروپی تەمەن": "تەمەن > 50 ساڵ",
        "ڕێژەی تووشبوون": "5%",
        "جۆری نەخۆشی": "گەدە"
    },
    "نەخۆشی گەدەی ڕیفلۆکس (GERD)": {
        "نیشانەکان": ["سووتانی گەدە (heartburn)", "گەڕانەوەی ترش", "ئازاری سنگ (جیاواز لە دڵ)", "کۆخەی وشک", "بەد تام لە دەمدا"],
        "پشکنینەکان": {"Endoscopy": "Esophagitis", "pH monitoring": "Acid reflux", "Clinical diagnosis": "بە وەڵامدانەوە بۆ PPI"},
        "چارەسەر": ["PPI (Omeprazole)", "Antacids", "گۆڕینی شێوازی ژیان (سەربەرز خەوتن)", "پارێزی لە خواردنی چەور"],
        "ئاستی مەترسی": "کەم",
        "تایبەتمەندی": "سووتانی گەدە + گەڕانەوەی ترش",
        "ڕێپیشگیری": ["پارێزی لە خواردنی چەور و کافئین", "کێشی تەندروست"],
        "گروپی تەمەن": "هەموو تەمەنەکان، بەتایبەت دووگیان و قەڵەو",
        "ڕێژەی تووشبوون": "20%",
        "جۆری نەخۆشی": "گەدە"
    },
    "نەخۆشی هەوکردنی ڕیخۆڵەکان (IBD - Crohn's/Ulcerative Colitis)": {
        "نیشانەکان": ["سکچوونی بەردەوام", "ئازاری سک", "خوێن لە پیساییدا", "کێش کەمبوونەوە", "تا", "ماندوویی"],
        "پشکنینەکان": {"Colonoscopy": "Ulcers/Inflammation", "Biopsy": "Granulomas (Crohn's)", "Fecal Calprotectin": "بەرز", "CRP": "بەرز"},
        "چارەسەر": ["5-ASA (Mesalamine)", "Steroids", "Immunomodulators (Azathioprine)", "Biologics (Infliximab)"],
        "ئاستی مەترسی": "مەترسیدار",
        "تایبەتمەندی": "سکچوونی خوێناوی + ئەنجامی کۆڵۆنۆسکۆپی",
        "ڕێپیشگیری": ["پارێزی لە جگەرە (بۆ Crohn's)", "پارێزی لە NSAIDs"],
        "گروپی تەمەن": "گەنجان (15-35 ساڵ)",
        "ڕێژەی تووشبوون": "0.3%",
        "جۆری نەخۆشی": "گەدە / خۆئەگەر"
    },
    "نەخۆشی پەنکریاتیت (Pancreatitis)": {
        "نیشانەکان": ["ئازاری سکی سەرەوە", "رشانەوە", "تا", "سکچوون", "ئازاری پشت", "تەنگی هەناسە"],
        "پشکنینەکان": {"Amylase": "بەرز >200 (3x نۆرماڵ)", "Lipase": "بەرز >200 (3x نۆرماڵ)", "CT scan": "پەنکریاتیت", "CRP": "بەرز"},
        "چارەسەر": ["پشووی خواردن (NPO)", "شلەمەنی (IV)", "دەرمانی ئازار (Opioids)", "ئەنتیبایۆتیک (ئەگەر پیس بوو)"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندی": "ئازاری سەرەوەی سک + Lipase > 3x نۆرماڵ",
        "ڕێپیشگیری": ["پارێزی لە خواردنی چەور", "کەمکردنەوەی کحول"],
        "گروپی تەمەن": "تەمەن > 40 ساڵ",
        "ڕێژەی تووشبوون": "0.3%",
        "جۆری نەخۆشی": "پەنکریاس"
    },
    "نەخۆشی جگەر (Hepatitis B)": {
        "نیشانەکان": ["ماندوویی", "زەردبوون", "میز تۆخ", "ئازاری سک", "سکچوون"],
        "پشکنینەکان": {"ALT": "بەرز", "HBsAg": "positive", "Anti-HBc": "positive", "HBV DNA": "بەرز"},
        "چارەسەر": ["Entecavir", "Tenofovir", "پشکنینی بەردەوام", "پارێزی لە جگەر"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندی": "HBsAg positive",
        "ڕێپیشگیری": ["کوتان", "پارێزی لە پەیوەندی خوێن و سێکس"],
        "گروپی تەمەن": "هەموو تەمەنەکان",
        "ڕێژەی تووشبوون": "3%",
        "جۆری نەخۆشی": "جگەر"
    },
    "نەخۆشی جگەر (Hepatitis C)": {
        "نیشانەکان": ["ماندوویی", "کێش کەمبوونەوە", "ئازاری سک", "زەردبوون", "میلە"],
        "پشکنینەکان": {"Anti-HCV": "positive", "PCR": "positive", "ALT": "بەرز", "Genotype": "دیاریکراو"},
        "چارەسەر": ["Sofosbuvir/Velpatasvir", "Daclatasvir", "پشکنینی بەردەوام"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندی": "Anti-HCV positive + PCR detectable",
        "ڕێپیشگیری": ["پارێزی لە پەیوەندی خوێن"],
        "گروپی تەمەن": "هەموو تەمەنەکان",
        "ڕێژەی تووشبوون": "2%",
        "جۆری نەخۆشی": "جگەر"
    },
    "نەخۆشی جگەر (Cirrhosis)": {
        "نیشانەکان": ["ئاوسانی سک (Ascites)", "زەردبوون", "ماندوویی", "خوێنبەربوون", "کێش کەمبوونەوە", "گیان لێ قەپات بوون"],
        "پشکنینەکان": {"ALT": "بەرز", "AST": "بەرز", "Albumin": "نزم", "INR": "بەرز", "Ultrasound": "Cirrhosis", "FibroScan": "F4"},
        "چارەسەر": ["پارێزی لە کحول", "Diuretic (Spironolactone)", "Lactulose (بۆ HE)", "پشکنینی HCC"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندی": "Ascites + نزمی ئەلبومین + INR بەرز + Ultrasound cirrhosis",
        "ڕێپیشگیری": ["پارێزی لە کحول", "کوتانی Hepatitis B", "پارێزی لە Hepatitis C"],
        "گروپی تەمەن": "تەمەن > 50 ساڵ",
        "ڕێژەی تووشبوون": "0.5%",
        "جۆری نەخۆشی": "جگەر"
    },
    "نەخۆشی جگەری چەور (NAFLD/NASH)": {
        "نیشانەکان": ["ماندوویی", "ئازاری سکی سەرەوە", "کێش زیادکردن", "میلە"],
        "پشکنینەکان": {"Ultrasound": "Fatty liver", "ALT": "بەرز", "Cholesterol": "بەرز", "FibroScan": "Steatosis"},
        "چارەسەر": ["کەمکردنەوەی کێش", "وەرزش", "شێوازی خواردنی کەم کارب", "Vitamin E (بۆ NASH)"],
        "ئاستی مەترسی": "کەم",
        "تایبەتمەندی": "Ultrasound fatty liver + ALT بەرز",
        "ڕێپیشگیری": ["شێوازی خواردنی تەندروست", "وەرزش"],
        "گروپی تەمەن": "تەمەن مامناوەند",
        "ڕێژەی تووشبوون": "25%",
        "جۆری نەخۆشی": "جگەر"
    },

    # === نەخۆشییەکانی دەمار (Neurology) ===
    "نەخۆشی Parkinson": {
        "نیشانەکان": ["لەرزین (Tremor at rest)", "خاوکردنەوەی جوڵە (Bradykinesia)", "سختی ماسوولکە (Rigidity)", "کەمبوونی پێست (Postural instability)", "مشکێتی ڕۆیشتن (Shuffling gait)"],
        "پشکنینەکان": {"Clinical exam": "Parkinsonian features", "DAT scan": "کەم", "MRI": "نۆرماڵ"},
        "چارەسەر": ["Levodopa/Carbidopa", "Pramipexole", "Ropinirole", "Deep Brain Stimulation"],
        "ئاستی مەترسی": "مەترسیدار",
        "تایبەتمەندی": "Tremor + Rigidity + Bradykinesia",
        "ڕێپیشگیری": ["وەرزش", "پارێزی لە ژەهراوی بوون"],
        "گروپی تەمەن": "تەمەن > 60 ساڵ",
        "ڕێژەی تووشبوون": "1%",
        "جۆری نەخۆشی": "دەمار"
    },
    "نەخۆشی Alzheimer": {
        "نیشانەکان": ["بیرچون (Memory loss)", "کەمبوونی بیر (Cognitive decline)", "گۆڕانی کەسایەتی", "مشکێتی ڕۆژانە", "بێئاگایی"],
        "پشکنینەکان": {"MRI": "Atrophy (Hippocampus)", "PET": "Amyloid plaques", "Cognitive test": "MMSE < 24"},
        "چارەسەر": ["Donepezil", "Rivastigmine", "Memantine", "پشتیوانی"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندی": "بیرچون + MRI atrophy + MMSE نزم",
        "ڕێپیشگیری": ["مەشقی مێشک", "وەرزش", "شێوازی خواردن"],
        "گروپی تەمەن": "تەمەن > 65 ساڵ",
        "ڕێژەی تووشبوون": "5% (تەمەن > 65)",
        "جۆری نەخۆشی": "دەمار"
    },
    "نەخۆشی MS (Multiple Sclerosis)": {
        "نیشانەکان": ["کورتی بینین (Optic neuritis)", "ماندوویی", "بێئاگایی (Numbness)", "مشکێتی جوڵە", "سەرگێژخواردن", "Lhermitte's sign"],
        "پشکنینەکان": {"MRI": "Demyelinating plaques", "CSF": "Oligoclonal bands", "VEP": "Delayed"},
        "چارەسەر": ["Steroid (بۆ ڕیلابس)", "Interferon", "Glatiramer", "Rituximab/Ocrelizumab"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندی": "MRI plaques + Oligoclonal bands + Clinical relapses",
        "ڕێپیشگیری": ["پارێزی لە ڤایرۆس (EBV)", "Vitamin D"],
        "گروپی تەمەن": "ژنانی گەنج (20-40)",
        "ڕێژەی تووشبوون": "0.3%",
        "جۆری نەخۆشی": "دەمار/خۆئەگەر"
    },
    "نەخۆشی Stroke (Ischemic)": {
        "نیشانەکان": ["مشکێتی جوڵە (یەکلایەنە)", "مشکێتی قسەکردن (Aphasia)", "بێئاگایی (یەکلایەنە)", "سەرگێژخواردن", "خوێنبەربوون"],
        "پشکنینەکان": {"CT (non-contrast)": "Ischemia/Hemorrhage", "MRI (DWI)": "Acute infarct", "Angiography": "تەنگی کرۆنەری", "Carotid Doppler": "Stenosis"},
        "چارەسەر": ["Thrombolytic (tPA) <4.5hrs", "Antiplatelet (Aspirin)", "Rehabilitation", "پشتیوانی"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندی": "مشکێتی جوڵە + CT stroke",
        "ڕێپیشگیری": ["کۆنتڕۆڵی BP", "کۆنتڕۆڵی شەکرە", "وەستانی جگەرە", "Anticoagulation بۆ AFib"],
        "گروپی تەمەن": "تەمەن > 60 ساڵ",
        "ڕێژەی تووشبوون": "2%",
        "جۆری نەخۆشی": "دەمار"
    },
    "نەخۆشی Migraine": {
        "نیشانەکان": ["سەرئێشەی توند (یەکلایەنە)", "سەرگێژخواردن", "هەستی بەمەزە", "بینینی تەڵخ (Aura)", "ڕشانەوە"],
        "پشکنینەکان": {"MRI": "نۆرماڵ", "Clinical exam": "Migraine criteria", "Response to triptan": "positive"},
        "چارەسەر": ["Triptan (Sumatriptan)", "NSAIDs", "Propranolol (پێشگیری)", "Amitriptyline"],
        "ئاستی مەترسی": "کەم",
        "تایبەتمەندی": "سەرئێشەی یەکلایەنە + هەستی بەمەزە + ڕشانەوە",
        "ڕێپیشگیری": ["پارێزی لە هۆکارەکان", "وەرزش", "پشوو"],
        "گروپی تەمەن": "ژنان (تەمەنی منداڵبوون)",
        "ڕێژەی تووشبوون": "12%",
        "جۆری نەخۆشی": "دەمار"
    },

    # === نەخۆشییەکانی خوێن (Hematology) ===
    "ئەنیمیای کەمخوێنی ئاسن (IDA)": {
        "نیشانەکان": ["ماندوویی", "ڕەنگی پێست زەرد", "سەرگێژخواردن", "لێدانی دڵ خێرا", "سەرئێشە", "پڕۆشتن", "هەستی ساردی", "تەنگی هەناسە"],
        "پشکنینەکان": {"Hb": "<12 g/dL (ژنان)/<13 (پیاوان)", "MCV": "<80 fL", "Ferritin": "نزم <15", "TIBC": "بەرز", "Iron": "نزم"},
        "چارەسەر": ["فێروس سولفەیت 325mg", "گۆڕینی خواردن", "دۆزینەوەی هۆکاری سەرەکی (خوێنبەربوون)", "ڤیتامین C 500mg"],
        "ئاستی مەترسی": "مامناوەند",
        "تایبەتمەندی": "MCV <80 + Ferritin نزم + TIBC بەرز",
        "ڕێپیشگیری": ["خواردنی پڕ ئاسن", "خواردنی ڤیتامین C", "پشکنینی خوێنی بەردەوام"],
        "گروپی تەمەن": "هەموو تەمەنەکان، بەتایبەت ژنانی دووگیان",
        "ڕێژەی تووشبوون": "25%",
        "جۆری نەخۆشی": "خوێن"
    },
    "ئەنیمیای ماکرۆسایتیک (B12/Folate Def)": {
        "نیشانەکان": ["ماندوویی", "سەرگێژخواردن", "هەستی بێهێزی و دەمارگیران", "کورتی هەناسە", "خێرالێدانی دڵ"],
        "پشکنینەکان": {"Hb": "<12 g/dL", "MCV": ">100 fL", "B12": "نزم (<200)", "Folate": "نزم (<3)", "Homocysteine/MMA": "بەرز"},
        "چارەسەر": ["ڤیتامین B12 1000mcg", "فۆلیک ئەسید 1mg", "گۆڕینی خواردن"],
        "ئاستی مەترسی": "مامناوەند",
        "تایبەتمەندی": "MCV >100 + B12/Folate نزم",
        "ڕێپیشگیری": ["خواردنی ڤیتامین B12", "خواردنی فۆلیک ئەسید"],
        "گروپی تەمەن": "پیران، ڤیگنەکان",
        "ڕێژەی تووشبوون": "5%",
        "جۆری نەخۆشی": "خوێن"
    },
    "لەوسیمیا (AML)": {
        "نیشانەکان": ["ماندوویی", "خوێنبەربوون", "تا", "کێش کەمبوونەوە", "ئازاری ئێسک", "خوێن لە لووتدا", "هەوکردنی دووبارە"],
        "پشکنینەکان": {"CBC": "Anemia, Thrombocytopenia, Leukocytosis", "Peripheral smear": "Blast cells", "Bone marrow biopsy": ">20% blasts"},
        "چارەسەر": ["کیمۆتێراپی (7+3)", "خوێن گواستنەوە", "ستیرۆید", "Stem cell transplant"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندی": "Blast cells >20% لە مۆخی ئێسکدا",
        "ڕێپیشگیری": ["نییە"],
        "گروپی تەمەن": "هەموو تەمەنەکان، بەتایبەت پیران",
        "ڕێژەی تووشبوون": "0.03%",
        "جۆری نەخۆشی": "خوێن/شێرپەنجە"
    },
    "هیمۆفیلیا A": {
        "نیشانەکان": ["خوێنبەربوونی زۆر", "خوێنبەربوونی ناو جومگەکان (Hemarthrosis)", "شین بوونەوە بە ئاسانی"],
        "پشکنینەکان": {"PTT": "درێژ", "Factor VIII": "نزم", "PT/INR": "نۆرماڵ", "Platelets": "نۆرماڵ"},
        "چارەسەر": ["Desmopressin (DDAVP)", "Factor VIII concentrate"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندی": "PTT درێژ + Factor VIII نزم",
        "ڕێپیشگیری": ["ڕاوێژکاری بۆماوەیی"],
        "گروپی تەمەن": "پیاوان (X-linked)",
        "ڕێژەی تووشبوون": "1/5000 پیاوان",
        "جۆری نەخۆشی": "خوێن/بۆماوەیی"
    },
    "لەیمفۆما (Non-Hodgkin's)": {
        "نیشانەکان": ["ئاوسانی لیمفە گرێکان", "تا", "ئارەقەکردنی شەو", "کێش کەمبوونەوە", "ماندوویی"],
        "پشکنینەکان": {"Lymph node biopsy": "Malignant lymphocytes", "LDH": "بەرز", "PET-CT": "Avid lymph nodes"},
        "چارەسەر": ["R-CHOP کیمۆتێراپی", "ڕادیۆتێراپی", "Immunotherapy (Rituximab)"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندی": "ئاوسانی لیمفە گرێ بێ ئازار + بیۆپسی",
        "ڕێپیشگیری": ["پارێزی لە ڤایرۆسەکان (EBV, HIV)"],
        "گروپی تەمەن": "تەمەن > 60 ساڵ",
        "ڕێژەی تووشبوون": "0.1%",
        "جۆری نەخۆشی": "خوێن/شێرپەنجە"
    },

    # === نەخۆشییە هەرە گرنگەکانی دیکە (Other Key Diseases) ===
    "HIV/AIDS": {
        "نیشانەکان": ["تا", "ئاوسانی لیمفە گرێکان", "کێش کەمبوونەوە", "ئارەقەکردنی شەو", "سکچوونی درێژخایەن", "هەوکردنی هەلپەرست (PCP, TB)"],
        "پشکنینەکان": {"HIV Antibody/Antigen": "positive", "CD4 count": "کەم (<200 = AIDS)", "Viral load": "بەرز"},
        "چارەسەر": ["ART (Tenofovir/Emtricitabine/Dolutegravir)"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندی": "HIV+ + CD4 < 200",
        "ڕێپیشگیری": ["PrEP", "پارێزی لە سێکسی پارێزراو", "دەرزی پاک"],
        "گروپی تەمەن": "گەنجان و تەمەن مامناوەند",
        "ڕێژەی تووشبوون": "0.3%",
        "جۆری نەخۆشی": "ڤایرۆسی/خۆئەگەر"
    },
    "سوورێژە (Measles)": {
        "نیشانەکان": ["تا", "کۆخە", "ڕژانی لووت", "چاوی سوور (Conjunctivitis)", "Koplik spots", "ڕەشان (Rash)"],
        "پشکنینەکان": {"IgM Antibody": "positive", "PCR": "Measles RNA"},
        "چارەسەر": ["پشتیوانی", "Vitamin A", "ئەنتیبایۆتیک بۆ هەوکردنی دووەمی"],
        "ئاستی مەترسی": "مامناوەند",
        "تایبەتمەندی": "3 C's (Cough, Coryza, Conjunctivitis) + Rash + Koplik spots",
        "ڕێپیشگیری": ["MMR vaccine"],
        "گروپی تەمەن": "منداڵان",
        "ڕێژەی تووشبوون": "بە پێی کوتان",
        "جۆری نەخۆشی": "ڤایرۆسی"
    },
    "ئەنفلۆنزا (Influenza)": {
        "نیشانەکان": ["تای بەرز", "کۆخەی وشک", "ئازاری ماسوولکە", "سەرئێشە", "ماندوویی", "گەروو ئازار"],
        "پشکنینەکان": {"Rapid Antigen Test": "positive", "PCR": "Influenza RNA"},
        "چارەسەر": ["Oseltamivir (Tamiflu)", "شلەمەنی", "دەرمانی دژە تا"],
        "ئاستی مەترسی": "مامناوەند",
        "تایبەتمەندی": "تای لەناکاو + ئازاری ماسوولکە + سەرئێشە",
        "ڕێپیشگیری": ["کوتانی ساڵانەی ئەنفلۆنزا"],
        "گروپی تەمەن": "هەموو تەمەنەکان",
        "ڕێژەی تووشبوون": "5-20% ساڵانە",
        "جۆری نەخۆشی": "ڤایرۆسی"
    },
    "شێرپەنجەی مەمک (Breast Cancer)": {
        "نیشانەکان": ["گرێ لە مەمکدا", "گۆڕانی پێستی مەمک", "دەرچوون لە گۆی مەمک", "ئاوسانی مەمک"],
        "پشکنینەکان": {"Mammogram": "Mass/Microcalcifications", "Biopsy": "Malignant cells", "ER/PR/HER2": "status"},
        "چارەسەر": ["نەشتەرگەری", "کیمۆتێراپی", "ڕادیۆتێراپی", "Hormonal therapy (Tamoxifen)"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندی": "گرێی سەرەتایی + بیۆپسی",
        "ڕێپیشگیری": ["Mammogram", "خۆپشکنینی مەمک", "کەمکردنەوەی مەترسی (بۆماوەیی)"],
        "گروپی تەمەن": "ژنانی >40 ساڵ",
        "ڕێژەی تووشبوون": "12% ی ژنان",
        "جۆری نەخۆشی": "شێرپەنجە"
    },
    "شێرپەنجەی پرۆستات (Prostate Cancer)": {
        "نیشانەکان": ["مشکێتی میزکردن", "خوێن لە میزدا", "ئازاری پشت/لەگەنە"],
        "پشکنینەکان": {"PSA": "بەرز", "DRE": "Nodule", "Biopsy": "Adenocarcinoma", "MRI": "PI-RADS score"},
        "چارەسەر": ["Active surveillance", "نەشتەرگەری", "ڕادیۆتێراپی", "Hormonal therapy"],
        "ئاستی مەترسی": "مەترسیدار",
        "تایبەتمەندی": "PSA بەرز + بیۆپسی",
        "ڕێپیشگیری": ["پشکنینی PSA و DRE"],
        "گروپی تەمەن": "پیاوانی >50 ساڵ",
        "ڕێژەی تووشبوون": "12% ی پیاوان",
        "جۆری نەخۆشی": "شێرپەنجە"
    },
    "نەخۆشی خۆئەگەری سیستێمیک (SLE/Lupus)": {
        "نیشانەکان": ["ئازاری جومگە", "ڕەش (Malar rash)", "تا", "ماندوویی", "ئاوسانی لیمفە گرێکان", "هەستیاری بە خۆر"],
        "پشکنینەکان": {"ANA": "positive", "ds-DNA": "بەرز", "C3/C4": "نزم", "Urinalysis": "پڕۆتین/خوێن"},
        "چارەسەر": ["NSAIDs", "Hydroxychloroquine", "Prednisone", "Mycophenolate mofetil"],
        "ئاستی مەترسی": "مەترسیدار",
        "تایبەتمەندی": "Malar rash + ANA+ + جومگە ئازار + پڕۆتین لە میزدا",
        "ڕێپیشگیری": ["پارێزی لە خۆر"],
        "گروپی تەمەن": "ژنانی گەنج (15-40)",
        "ڕێژەی تووشبوون": "0.1%",
        "جۆری نەخۆشی": "خۆئەگەر"
    }
}

# ================================
# 5. داتابەسی پشکنینەکانی تاقیگە (بەرەو ٢٠٠ پشکنین)
# ================================
LAB_TESTS = {}

# === پشکنینەکانی خوێن (Hematology) ===
blood_tests = {
    "CBC": {"گروپ": "خوێن", "نۆرماڵ": (4.0, 11.0), "یەکە": "x10³/µL", "تەفسیر": "خڕۆکە سپیەکان (WBC)", "ئامێر": "Sysmex XN-9000"},
    "Hemoglobin": {"گروپ": "خوێن", "نۆرماڵ": (12.0, 16.0), "یەکە": "g/dL", "تەفسیر": "هیمۆگلۆبین", "ئامێر": "HemoCue 201+"},
    "Platelets": {"گروپ": "خوێن", "نۆرماڵ": (150, 450), "یەکە": "x10³/µL", "تەفسیر": "پلەیتلێت", "ئامێر": "Sysmex XN-9000"},
    "MCV": {"گروپ": "خوێن", "نۆرماڵ": (80, 100), "یەکە": "fL", "تەفسیر": "قەبارەی خڕۆکە سوورەکان", "ئامێر": "Sysmex XN-9000"},
    "RDW": {"گروپ": "خوێن", "نۆرماڵ": (11.5, 14.5), "یەکە": "%", "تەفسیر": "جیاوازی قەبارەی RBC", "ئامێر": "Sysmex XN-9000"},
    "Reticulocyte": {"گروپ": "خوێن", "نۆرماڵ": (0.5, 2.5), "یەکە": "%", "تەفسیر": "خڕۆکە سوورە گەنجەکان", "ئامێر": "BD FACSCalibur"},
    "ESR": {"گروپ": "خوێن", "نۆرماڵ": (0, 20), "یەکە": "mm/hr", "تەفسیر": "خێرایی تەنیشتنی خڕۆکە سوورەکان", "ئامێر": "Ves-Matic 20"},
    "PT": {"گروپ": "خوێن", "نۆرماڵ": (11, 13.5), "یەکە": "seconds", "تەفسیر": "کاتی پڕۆترۆمبین", "ئامێر": "Stago Compact Max"},
    "PTT": {"گروپ": "خوێن", "نۆرماڵ": (25, 35), "یەکە": "seconds", "تەفسیر": "کاتی ترۆمبۆپلاستینی بەشەکی", "ئامێر": "Stago Compact Max"},
    "INR": {"گروپ": "خوێن", "نۆرماڵ": (0.9, 1.2), "یەکە": "", "تەفسیر": "ڕێژەی نێودەوڵەتی نۆرماڵ", "ئامێر": "Stago Compact Max"},
    "D-Dimer": {"گروپ": "خوێن", "نۆرماڵ": (0, 500), "یەکە": "ng/mL", "تەفسیر": "بەرهەمی هەڵوەشاندنەوەی مەبەست", "ئامێر": "Roche Cobas e411"},
}

# === پشکنینەکانی بایۆکیمیایی (Biochemistry) ===
biochem_tests = {
    "Glucose": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (70, 126), "یەکە": "mg/dL", "تەفسیر": "شەکری خوێن", "ئامێر": "Roche Cobas c502"},
    "HbA1c": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (4.0, 5.6), "یەکە": "%", "تەفسیر": "شەکری درێژخایەن", "ئامێر": "Bio-Rad D-100"},
    "Creatinine": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (0.6, 1.3), "یەکە": "mg/dL", "تەفسیر": "کارایی گورچیلە", "ئامێر": "Roche Cobas c502"},
    "BUN": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (7, 20), "یەکە": "mg/dL", "تەفسیر": "نایترۆجینی یوریا", "ئامێر": "Roche Cobas c502"},
    "eGFR": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (90, 120), "یەکە": "mL/min/1.73m²", "تەفسیر": "خێرایی فلتەرکردنی گورچیلە", "ئامێر": "Calculated"},
    "ALT": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (10, 40), "یەکە": "U/L", "تەفسیر": "ئەنزیمی جگەر", "ئامێر": "Roche Cobas c502"},
    "AST": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (10, 40), "یەکە": "U/L", "تەفسیر": "ئەنزیمی جگەر و دڵ", "ئامێر": "Roche Cobas c502"},
    "Bilirubin Total": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (0.1, 1.2), "یەکە": "mg/dL", "تەفسیر": "زەرداوی", "ئامێر": "Roche Cobas c502"},
    "Albumin": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (3.5, 5.0), "یەکە": "g/dL", "تەفسیر": "ئەلبومین", "ئامێر": "Roche Cobas c502"},
    "Sodium": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (135, 145), "یەکە": "mmol/L", "تەفسیر": "سۆدیۆم", "ئامێر": "Roche Cobas c502 (ISE)"},
    "Potassium": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (3.5, 5.0), "یەکە": "mmol/L", "تەفسیر": "پۆتاسیۆم", "ئامێر": "Roche Cobas c502 (ISE)"},
    "Calcium": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (8.5, 10.5), "یەکە": "mg/dL", "تەفسیر": "کالسیۆم", "ئامێر": "Roche Cobas c502"},
    "Uric Acid": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (3.5, 7.2), "یەکە": "mg/dL", "تەفسیر": "یۆریک ئەسید", "ئامێر": "Roche Cobas c502"},
    "Lipase": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (20, 200), "یەکە": "U/L", "تەفسیر": "ئەنزیمی پەنکریاس", "ئامێر": "Roche Cobas c502"},
    "Amylase": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (30, 110), "یەکە": "U/L", "تەفسیر": "ئەنزیمی پەنکریاس", "ئامێر": "Roche Cobas c502"},
    "Cholesterol": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (0, 200), "یەکە": "mg/dL", "تەفسیر": "کۆلسترۆلی گشتی", "ئامێر": "Roche Cobas c502"},
    "LDL": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (0, 100), "یەکە": "mg/dL", "تەفسیر": "کۆلسترۆلی خراپ", "ئامێر": "Roche Cobas c502"},
    "HDL": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (40, 60), "یەکە": "mg/dL", "تەفسیر": "کۆلسترۆلی باش", "ئامێر": "Roche Cobas c502"},
    "Triglycerides": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (0, 150), "یەکە": "mg/dL", "تەفسیر": "تریگلیسیرید", "ئامێر": "Roche Cobas c502"},
    "CRP": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (0, 5), "یەکە": "mg/L", "تەفسیر": "پروتێینی هەوکردن", "ئامێر": "Roche Cobas c502"},
}

# === پشکنینەکانی دڵ (Cardiac Markers) ===
cardiac_tests = {
    "Troponin I": {"گروپ": "دڵ", "نۆرماڵ": (0, 0.04), "یەکە": "ng/mL", "تەفسیر": "پروتێینی دڵ (برینداری)", "ئامێر": "Roche Cobas e411"},
    "CK-MB": {"گروپ": "دڵ", "نۆرماڵ": (0, 5), "یەکە": "ng/mL", "تەفسیر": "ئەنزیمی دڵ", "ئامێر": "Roche Cobas e411"},
    "BNP": {"گروپ": "دڵ", "نۆرماڵ": (0, 100), "یەکە": "pg/mL", "تەفسیر": "پروتێینی دڵ (Heart Failure)", "ئامێر": "Roche Cobas e411"},
    "NT-proBNP": {"گروپ": "دڵ", "نۆرماڵ": (0, 125), "یەکە": "pg/mL", "تەفسیر": "نیشانەی پێشکەوتووی HF", "ئامێر": "Roche Cobas e411"},
}

# === پشکنینەکانی تایرۆید و هۆرمۆن (Endocrinology) ===
hormone_tests = {
    "TSH": {"گروپ": "هۆرمۆن", "نۆرماڵ": (0.4, 4.0), "یەکە": "mIU/L", "تەفسیر": "هۆرمۆنی هاندەری دەرقی", "ئامێر": "Roche Cobas e411"},
    "Free T4": {"گروپ": "هۆرمۆن", "نۆرماڵ": (0.8, 1.8), "یەکە": "ng/dL", "تەفسیر": "تایرۆکسینی ئازاد", "ئامێر": "Roche Cobas e411"},
    "Free T3": {"گروپ": "هۆرمۆن", "نۆرماڵ": (2.3, 4.2), "یەکە": "pg/mL", "تەفسیر": "ترییۆدۆتایرۆنینی ئازاد", "ئامێر": "Roche Cobas e411"},
    "Anti-TPO": {"گروپ": "هۆرمۆن", "نۆرماڵ": (0, 34), "یەکە": "IU/mL", "تەفسیر": "دژەتەنی تایرۆید", "ئامێر": "Roche Cobas e411"},
    "Cortisol": {"گروپ": "هۆرمۆن", "نۆرماڵ": (5, 25), "یەکە": "μg/dL", "تەفسیر": "هۆرمۆنی فشار", "ئامێر": "Roche Cobas e411"},
    "Prolactin": {"گروپ": "هۆرمۆن", "نۆرماڵ": (2, 15), "یەکە": "ng/mL", "تەفسیر": "هۆرمۆنی شیر", "ئامێر": "Roche Cobas e411"},
    "Testosterone (Total)": {"گروپ": "هۆرمۆن", "نۆرماڵ": (300, 1000), "یەکە": "ng/dL", "تەفسیر": "هۆرمۆنی نێرینە", "ئامێر": "Roche Cobas e411"},
    "Vitamin D (25-OH)": {"گروپ": "هۆرمۆن", "نۆرماڵ": (30, 100), "یەکە": "ng/mL", "تەفسیر": "ڕەوشی ڤیتامین D", "ئامێر": "Roche Cobas e411"},
    "Insulin": {"گروپ": "هۆرمۆن", "نۆرماڵ": (2, 25), "یەکە": "μIU/mL", "تەفسیر": "هۆرمۆنی شەکر", "ئامێر": "Roche Cobas e411"},
    "C-peptide": {"گروپ": "هۆرمۆن", "نۆرماڵ": (0.5, 2.0), "یەکە": "ng/mL", "تەفسیر": "پێکهاتەی ئەنسولین", "ئامێر": "Roche Cobas e411"},
    "IGF-1": {"گروپ": "هۆرمۆن", "نۆرماڵ": (50, 300), "یەکە": "ng/mL", "تەفسیر": "فاکتەری گەشەی هاوشێوەی ئەنسولین", "ئامێر": "Roche Cobas e411"},
    "ACTH": {"گروپ": "هۆرمۆن", "نۆرماڵ": (10, 60), "یەکە": "pg/mL", "تەفسیر": "هۆرمۆنی هاندەری ئەدریناڵ", "ئامێر": "Roche Cobas e411"},
}

# === پشکنینەکانی شێرپەنجە (Tumor Markers) ===
tumor_markers = {
    "PSA": {"گروپ": "شێرپەنجە", "نۆرماڵ": (0, 4), "یەکە": "ng/mL", "تەفسیر": "پڕۆستات سپێسیفیک ئەنتیجین", "ئامێر": "Roche Cobas e411"},
    "CA-125": {"گروپ": "شێرپەنجە", "نۆرماڵ": (0, 35), "یەکە": "U/mL", "تەفسیر": "شێرپەنجەی هێلکەدان", "ئامێر": "Roche Cobas e411"},
    "CA 19-9": {"گروپ": "شێرپەنجە", "نۆرماڵ": (0, 37), "یەکە": "U/mL", "تەفسیر": "شێرپەنجەی پەنکریاس/گەدە", "ئامێر": "Roche Cobas e411"},
    "AFP": {"گروپ": "شێرپەنجە", "نۆرماڵ": (0, 10), "یەکە": "ng/mL", "تەفسیر": "شێرپەنجەی جگەر/هێلکە", "ئامێر": "Roche Cobas e411"},
    "CEA": {"گروپ": "شێرپەنجە", "نۆرماڵ": (0, 3), "یەکە": "ng/mL", "تەفسیر": "شێرپەنجەی کۆلۆن/ڕیخۆڵە", "ئامێر": "Roche Cobas e411"},
    "HCG": {"گروپ": "شێرپەنجە", "نۆرماڵ": (0, 5), "یەکە": "mIU/mL", "تەفسیر": "حەمل یان شێرپەنجەی تێستیکولار", "ئامێر": "Roche Cobas e411"},
    "LDH": {"گروپ": "شێرپەنجە", "نۆرماڵ": (100, 250), "یەکە": "U/L", "تەفسیر": "ئەنزیمی گشتی (لەیمفۆما)", "ئامێر": "Roche Cobas c502"},
}

# یەکخستنی هەموو پشکنینەکان
for test_dict in [blood_tests, biochem_tests, cardiac_tests, hormone_tests, tumor_markers]:
    LAB_TESTS.update(test_dict)

# ================================
# 6. داتابەسی دەرمانەکان (بەرەو 150+ دەرمان) - بە وەسفی تەواو
# ================================
DRUG_DATABASE = {
    # 6.1 دژە پەستانی خوێن و دڵ (Cardiovascular)
    "دژە پەستانی خوێن و دڵ": {
        "کاپتۆپریل": {"ڕێژە": "25-50mg", "میکانیزم": "ACE inhibitor", "کاریگەری لاوەکی": "کۆخە, سەرگێژخواردن", "پێچەوانە": "حەملی دووگانی, Angioedema", "وەسف": "دەرمانی ACE inhibitor کە پەستانی خوێن کەم دەکاتەوە.", "بۆچی": "بۆ کەمکردنەوەی پەستانی خوێن و پاراستنی گورچیلە لە نەخۆشانی شەکرە."},
        "ئەملۆدیپین": {"ڕێژە": "5-10mg", "میکانیزم": "Calcium channel blocker", "کاریگەری لاوەکی": "ئاوسانی قاچ", "پێچەوانە": "هەستیاری", "وەسف": "بەربەستەری کالسیۆم کە خوێنبەرەکان فراوان دەکات.", "بۆچی": "بۆ چارەسەری پەستانی خوێنی بەرز و ئازاری سنگ."},
        "ئەسپیرین (دژە پلەیتلێت)": {"ڕێژە": "75-100mg", "میکانیزم": "COX inhibitor", "کاریگەری لاوەکی": "خوێنبەربوونی گەدە", "پێچەوانە": "Ulcer, خوێنبەربوون", "وەسف": "دژە پلەیتلێت بۆ پێشگیری لە مەبەست.", "بۆچی": "پێشگیری لە جەڵتە و نەخۆشی دڵ."},
        "وارفارین": {"ڕێژە": "5mg (بەپێی INR)", "میکانیزم": "Vitamin K antagonist", "کاریگەری لاوەکی": "خوێنبەربوون", "پێچەوانە": "حەملی دووگانی", "وەسف": "دژە خوێن (Anticoagulant) بۆ پێشگیری لە مەبەست.", "بۆچی": "بۆ AFib, DVT, PE."},
    },
    # 6.2 دژە شەکرە (Endocrine)
    "دژە شەکرە": {
        "مێتفۆرمین": {"ڕێژە": "500-2000mg", "میکانیزم": "Biguanide", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "eGFR <30, Acidosis", "وەسف": "هێڵی یەکەمی چارەسەری شەکرەی جۆری ٢.", "بۆچی": "بۆ کۆنتڕۆڵکردنی شەکری خوێن."},
        "گلیپیزاید": {"ڕێژە": "5-20mg", "میکانیزم": "Sulfonylurea", "کاریگەری لاوەکی": "هایپۆگلایسیمیا", "پێچەوانە": "هەستیاری, CKD", "وەسف": "هاندەری پەنکریاس بۆ دەردانی زیاتری ئەنسولین.", "بۆچی": "بۆ کەمکردنەوەی شەکری خوێن."},
        "ئەنسولین Glargine": {"ڕێژە": "10-40 IU", "میکانیزم": "Insulin analog (Basal)", "کاریگەری لاوەکی": "هایپۆگلایسیمیا", "پێچەوانە": "هایپۆگلایسیمیا", "وەسف": "ئەنسولینی درێژخایەن (24 کاتژمێر).", "بۆچی": "بۆ کۆنتڕۆڵی شەکری بنەڕەتی."},
        "سیتاگلیپتین": {"ڕێژە": "100mg", "میکانیزم": "DPP-4 inhibitor", "کاریگەری لاوەکی": "سەرئێشە", "پێچەوانە": "پەنکریاتیت", "وەسف": "بەرزکردنەوەی ئاستی GLP-1.", "بۆچی": "یارمەتیدەر بۆ کۆنتڕۆڵی شەکر."},
        "ئەمپاگلیفلۆزین": {"ڕێژە": "10-25mg", "میکانیزم": "SGLT2 inhibitor", "کاریگەری لاوەکی": "UTI, کێش کەمبوونەوە", "پێچەوانە": "eGFR <30", "وەسف": "دەرکردنی شەکر لە ڕێگەی میزەوە و پارێزگاری لە دڵ و گورچیلە.", "بۆچی": "بۆ شەکرەی جۆری ٢ و نەخۆشی دڵ و گورچیلە."},
    },
    # 6.3 دژە میکرۆب (Antibiotics)
    "دژە میکرۆب (Antibiotics)": {
        "ئەمۆکسیسیلین": {"ڕێژە": "500mg", "میکانیزم": "Beta-lactam", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "هەستیاری پێنیسیلین", "وەسف": "ئەنتیبایۆتیکی پێنیسیلین.", "بۆچی": "بۆ هەوکردنی سییەکان، گوێ، و سینوس."},
        "ئازیترۆمایسین": {"ڕێژە": "250-500mg", "میکانیزم": "Macrolide", "کاریگەری لاوەکی": "سکچوون, QT درێژ", "پێچەوانە": "نەخۆشی دڵ (QT)", "وەسف": "ئەنتیبایۆتیکی ماکرۆلید.", "بۆچی": "بۆ هەوکردنی هەناسە و سینوس."},
        "سیپرۆفلۆکساسین": {"ڕێژە": "500mg", "میکانیزم": "Fluoroquinolone", "کاریگەری لاوەکی": "ئازاری ماسوولکە, QT درێژ", "پێچەوانە": "منداڵان, حەمل", "وەسف": "ئەنتیبایۆتیکی فلۆرۆکینۆلۆن.", "بۆچی": "بۆ UTI، هەوکردنی پرۆستات."},
        "مێترۆنیدازۆل": {"ڕێژە": "500mg", "میکانیزم": "Nitroimidazole", "کاریگەری لاوەکی": "تامی کانزایی, سکچوون", "پێچەوانە": "حەمل (سێ مانگی یەکەم)", "وەسف": "ئەنتیبایۆتیک بۆ بەکتریای بێ ئۆکسجین و پرۆتۆزۆوا.", "بۆچی": "بۆ هەوکردنی گەدە، C. diff، ڤاجاینایس."},
        "سێفتریاکسۆن": {"ڕێژە": "1-2g IV", "میکانیزم": "Cephalosporin (3rd gen)", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "هەستیاری بێتا-لاکتام", "وەسف": "ئەنتیبایۆتیکی بەهێز.", "بۆچی": "بۆ مێنەنجایت، پنێومۆنیا، گۆنۆریا."},
    },
    # 6.4 دەرمانی هەناسە (Respiratory)
    "دەرمانی هەناسە": {
        "سالبوتامۆل": {"ڕێژە": "2 puffs PRN", "میکانیزم": "Beta-2 agonist (SABA)", "کاریگەری لاوەکی": "لەرزین, خێرایی دڵ", "پێچەوانە": "Tachyarrhythmia", "وەسف": "فراوانکەری بۆڕی هەناسە.", "بۆچی": "بۆ هێورکردنەوەی کۆکە (Asthma)."},
        "فلوتیکاسۆن": {"ڕێژە": "250-500mcg", "میکانیزم": "Corticosteroid (ICS)", "کاریگەری لاوەکی": "هەوکردنی دەم", "پێچەوانە": "هەستیاری", "وەسف": "ستیرۆیدی هەڵمژراوی دژە هەوکردن.", "بۆچی": "بۆ پێشگیری لە کۆکە."},
        "مۆنتلۆکاست": {"ڕێژە": "10mg", "میکانیزم": "Leukotriene receptor antagonist", "کاریگەری لاوەکی": "سەرئێشە", "پێچەوانە": "هەستیاری", "وەسف": "بەربەستەری لیوکۆترین.", "بۆچی": "بۆ کۆکە و ڕینایتیس."},
        "تیۆترۆپیۆم": {"ڕێژە": "18mcg", "میکانیزم": "Anticholinergic (LAMA)", "کاریگەری لاوەکی": "دەم وشک", "پێچەوانە": "Glaucoma", "وەسف": "فراوانکەری درێژخایەن بۆ COPD.", "بۆچی": "بۆ چارەسەری ڕاگرتنی COPD."},
    },
    # 6.5 دەرمانی گەدە (GI)
    "دەرمانی گەدە": {
        "ئومەپرازۆل": {"ڕێژە": "20-40mg", "میکانیزم": "PPI", "کاریگەری لاوەکی": "سەرئێشە, نزمی Mg", "پێچەوانە": "هەستیاری", "وەسف": "بەربەستەری پمپەی پرۆتۆن.", "بۆچی": "بۆ GERD, Gastritis, Ulcer."},
        "ئۆنداسێترۆن": {"ڕێژە": "4-8mg", "میکانیزم": "5-HT3 antagonist", "کاریگەری لاوەکی": "سەرئێشە, سکچوون", "پێچەوانە": "QT درێژ", "وەسف": "دژە ڕشانەوەی بەهێز.", "بۆچی": "بۆ ڕشانەوەی پاش کیمۆتێراپی و نەشتەرگەری."},
    }
}

# ================================
# 7. فانکشنە یارمەتیدەرەکان
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

def get_disease_count() -> int:
    return len(DISEASE_DATABASE)

def get_drug_count() -> int:
    total = 0
    for category in DRUG_DATABASE.values():
        total += len(category)
    return total

def get_lab_count() -> int:
    return len(LAB_TESTS)

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
# 8. دروستکردنی ١٠٠٠+ کویز (بە ئاست)
# ================================
def generate_quizzes_by_level():
    quizzes = []
    level_questions = {
        1: [
            {"پرسیار": "نیشانەی سەرەکی شەکرە چییە؟", "هەڵبژاردەکان": ["تینوویەتی زۆر", "سەرئێشە", "ئازاری سنگ", "کۆخە"], "وەڵامی ڕاست": 0},
            {"پرسیار": "دەرمانی یەکەم بۆ شەکرەی جۆری ٢ چییە؟", "هەڵبژاردەکان": ["مێتفۆرمین", "ئەنسولین", "گلیپیزاید", "سیتاگلیپتین"], "وەڵامی ڕاست": 0},
            {"پرسیار": "پەستانی خوێنی نۆرماڵ چەندە؟", "هەڵبژاردەکان": ["120/80", "140/90", "160/100", "130/85"], "وەڵامی ڕاست": 0},
            {"پرسیار": "کام دەرمان دژە پلەیتلێتە؟", "هەڵبژاردەکان": ["ئەسپیرین", "وارفارین", "هێپارین", "ئەنۆکساپارین"], "وەڵامی ڕاست": 0},
            {"پرسیار": "نیشانەی ئەنیمیا چییە؟", "هەڵبژاردەکان": ["ماندوویی و ڕەنگی پێست زەرد", "ئازاری سنگ", "تینوویەتی زۆر", "کۆخە"], "وەڵامی ڕاست": 0},
            {"پرسیار": "کام پشکنینە بۆ دەستنیشانکردنی شەکرە؟", "هەڵبژاردەکان": ["HbA1c", "ECG", "Chest X-ray", "MRI"], "وەڵامی ڕاست": 0},
            {"پرسیار": "کام لەم نیشانانە بۆ کۆکە (Asthma) نییە؟", "هەڵبژاردەکان": ["Wheezing", "تەنگی هەناسە", "کۆخە", "ئاوسانی قاچ"], "وەڵامی ڕاست": 3},
            {"پرسیار": "کام دەرمانە بۆ هەوکردنی سییەکان (Pneumonia)؟", "هەڵبژاردەکان": ["ئەمۆکسیسیلین", "مێتفۆرمین", "ئەسپیرین", "سالبوتامۆل"], "وەڵامی ڕاست": 0},
            {"پرسیار": "MCV < 80 fL نیشانەی چییە؟", "هەڵبژاردەکان": ["ئەنیمیای مایکرۆسایتیک", "ئەنیمیای ماکرۆسایتیک", "نۆرمۆسایتیک", "هیمۆلایتیک"], "وەڵامی ڕاست": 0},
            {"پرسیار": "CRP بەرز نیشانەی چییە؟", "هەڵبژاردەکان": ["هەوکردن", "شەکرە", "ئەنیمیا", "نەخۆشی دڵ"], "وەڵامی ڕاست": 0},
        ],
        2: [
            {"پرسیار": "HbA1c > 6.5% ئاماژەیە بۆ چی؟", "هەڵبژاردەکان": ["شەکرە", "ئەنیمیا", "نەخۆشی دڵ", "هەوکردن"], "وەڵامی ڕاست": 0},
            {"پرسیار": "تایفیید بە کام دەرمان چارەسەر دەکرێت؟", "هەڵبژاردەکان": ["Ceftriaxone", "Metformin", "Salbutamol", "Aspirin"], "وەڵامی ڕاست": 0},
            {"پرسیار": "Ferritin نزم + TIBC بەرز نیشانەی چییە؟", "هەڵبژاردەکان": ["IDA", "B12 Def", "Thalassemia", "ACD"], "وەڵامی ڕاست": 0},
            {"پرسیار": "هۆکاری سەرەکی COPD چییە؟", "هەڵبژاردەکان": ["جگەرەکێشان", "هەوکردن", "بۆماوەیی", "هەستیاری"], "وەڵامی ڕاست": 0},
            {"پرسیار": "Anti-GAD positive نیشانەی کام شەکرەیە؟", "هەڵبژاردەکان": ["جۆری 1", "جۆری 2", "حەملی", "MODY"], "وەڵامی ڕاست": 0},
            {"پرسیار": "کام دەرمان دژە ڕشانەوەی بەهێزە و لە کیمۆدا بەکاردێت؟", "هەڵبژاردەکان": ["ئۆنداسێترۆن", "مێتۆکلۆپرامید", "دۆمپێریدۆن", "پرۆکلۆرپێرازین"], "وەڵامی ڕاست": 0},
            {"پرسیار": "eGFR < 60 بۆ زیاتر لە 3 مانگ چی دەستنیشان دەکات؟", "هەڵبژاردەکان": ["CKD", "AKI", "UTI", "Stones"], "وەڵامی ڕاست": 0},
            {"پرسیار": "کام دەرمان SGLT2 inhibitorە؟", "هەڵبژاردەکان": ["ئەمپاگلیفلۆزین", "مێتفۆرمین", "گلیپیزاید", "سیتاگلیپتین"], "وەڵامی ڕاست": 0},
            {"پرسیار": "Amylase/Lipase بەرز نیشانەی چییە؟", "هەڵبژاردەکان": ["پەنکریاتیت", "هەپاتایت", "کۆلێسیستایت", "گاستریت"], "وەڵامی ڕاست": 0},
            {"پرسیار": "وارفارین چ پشکنینێک پێوانە دەکات؟", "هەڵبژاردەکان": ["INR", "PTT", "CBC", "Platelets"], "وەڵامی ڕاست": 0},
        ],
        3: [
            {"پرسیار": "نەخۆشی کۆن (Gout) بە کام دەرمان چارەسەر دەکرێت (حەملەی توند)؟", "هەڵبژاردەکان": ["NSAIDs یان کۆلشیسین", "Allopurinol", "Probenecid", "Febuxostat"], "وەڵامی ڕاست": 0},
            {"پرسیار": "Oligoclonal bands لە CSF نیشانەی چییە؟", "هەڵبژاردەکان": ["MS", "Alzheimer", "Parkinson", "GBS"], "وەڵامی ڕاست": 0},
            {"پرسیار": "FEV1/FVC < 70% (پاش برۆنکۆدایلەیتەر) نیشانەی چییە؟", "هەڵبژاردەکان": ["COPD", "Asthma", "Bronchitis", "Fibrosis"], "وەڵامی ڕاست": 0},
            {"پرسیار": "کام دەرمانە بۆ پێشگیری لە مێگرەین بەکاردێت؟", "هەڵبژاردەکان": ["پڕۆپانۆلۆل", "سوماتریپتان", "ئیبۆپروفین", "پاراستامۆل"], "وەڵامی ڕاست": 0},
            {"پرسیار": "Malar rash + ANA+ + پڕۆتین لە میزدا نیشانەی چییە؟", "هەڵبژاردەکان": ["SLE (Lupus)", "RA", "Scleroderma", "Dermatomyositis"], "وەڵامی ڕاست": 0},
            {"پرسیار": "کام دەرمان بۆ چارەسەری Hepatitis C بەکاردێت؟", "هەڵبژاردەکان": ["Sofosbuvir/Velpatasvir", "Entecavir", "Acyclovir", "Oseltamivir"], "وەڵامی ڕاست": 0},
            {"پرسیار": "DAT scan کەمبوونەوە نیشانەی چییە؟", "هەڵبژاردەکان": ["Parkinson", "Alzheimer", "MS", "Stroke"], "وەڵامی ڕاست": 0},
            {"پرسیار": "PTT درێژ + Factor VIII نزم نیشانەی چییە؟", "هەڵبژاردەکان": ["هیمۆفیلیا A", "هیمۆفیلیا B", "vWD", "DIC"], "وەڵامی ڕاست": 0},
            {"پرسیار": "CA-125 بەرز بۆ کام شێرپەنجە دەگەڕێتەوە؟", "هەڵبژاردەکان": ["هێلکەدان", "مەمک", "کۆلۆن", "پەنکریاس"], "وەڵامی ڕاست": 0},
            {"پرسیار": "HIV+ + CD4 < 200 نیشانەی چییە؟", "هەڵبژاردەکان": ["AIDS", "HIV Infection", "Seroconversion", "Remission"], "وەڵامی ڕاست": 0},
        ],
        4: [
            {"پرسیار": "کام دەرمان بۆ ڕشانەوەی پاش کیمۆتێراپی هەڵدەبژێردرێت؟", "هەڵبژاردەکان": ["ئۆنداسێترۆن", "مێتۆکلۆپرامید", "دۆمپێریدۆن", "پرۆکلۆرپێرازین"], "وەڵامی ڕاست": 0},
            {"پرسیار": "Troponin I بەرز + ST depression نیشانەی چییە؟", "هەڵبژاردەکان": ["NSTEMI", "STEMI", "Unstable Angina", "Pericarditis"], "وەڵامی ڕاست": 0},
            {"پرسیار": "کۆڵۆنۆسکۆپی + بیۆپسی بۆ چی پێویستە؟", "هەڵبژاردەکان": ["IBD vs CRC", "GERD", "Ulcer", "Gastritis"], "وەڵامی ڕاست": 0},
            {"پرسیار": "پارێزگاری لە دڵ و گورچیلە کام کاریگەریی SGLT2 inhibitorsە؟", "هەڵبژاردەکان": ["ڕاستە", "هەڵەیە"], "وەڵامی ڕاست": 0},
            {"پرسیار": "AFP > 400 لەگەڵ CT mass نیشانەی چییە؟", "هەڵبژاردەکان": ["Hepatocellular Carcinoma", "Metastasis", "Hemangioma", "Abscess"], "وەڵامی ڕاست": 0},
            {"پرسیار": "ACTH بەرز + کۆرتیزۆڵ بەرز نیشانەی چییە؟", "هەڵبژاردەکان": ["Cushing's Disease", "Cushing's Syndrome", "Addison's", "Conn's"], "وەڵامی ڕاست": 0},
            {"پرسیار": "Blast cells >20% لە مۆخی ئێسکدا نیشانەی چییە؟", "هەڵبژاردەکان": ["AML", "ALL", "CML", "MDS"], "وەڵامی ڕاست": 0},
            {"پرسیار": "کام لەم دەرمانانە بۆ SLE بەکاردێت؟", "هەڵبژاردەکان": ["Hydroxychloroquine", "Methotrexate", "Sulfasalazine", "Allopurinol"], "وەڵامی ڕاست": 0},
            {"پرسیار": "ABI < 0.9 نیشانەی چییە؟", "هەڵبژاردەکان": ["PAD", "DVT", "Venous Insufficiency", "Lymphedema"], "وەڵامی ڕاست": 0},
            {"پرسیار": "DEXA Scan T-score < -2.5 چییە؟", "هەڵبژاردەکان": ["Osteoporosis", "Osteopenia", "Osteomalacia", "Paget's"], "وەڵامی ڕاست": 0},
        ],
        5: [
            {"پرسیار": "کام دەرمان بۆ تایفیید لە حەملی دووگانیدا بەکاردێت؟", "هەڵبژاردەکان": ["Ceftriaxone", "Ciprofloxacin", "Doxycycline", "Azithromycin"], "وەڵامی ڕاست": 0},
            {"پرسیار": "Pulsus paradoxus + Beck's triad نیشانەی چییە؟", "هەڵبژاردەکان": ["Cardiac Tamponade", "Pericarditis", "CHF", "COPD"], "وەڵامی ڕاست": 0},
            {"پرسیار": "C-ANCA positive بۆ کام نەخۆشی گرنگە؟", "هەڵبژاردەکان": ["Granulomatosis with Polyangiitis", "Microscopic Polyangiitis", "Eosinophilic GPA", "SLE"], "وەڵامی ڕاست": 0},
            {"پرسیار": "Lithium toxicity چ نیشانەیەکی هەیە؟", "هەڵبژاردەکان": ["Tremor, Ataxia, Nephrogenic DI", "Jaundice, Ascites", "Cough, Fever", "Rash, Arthralgia"], "وەڵامی ڕاست": 0},
            {"پرسیار": "کام دەرمان بۆ Status Epilepticus یەکەم هەڵبژاردەیە؟", "هەڵبژاردەکان": ["Lorazepam IV", "Phenytoin", "Levetiracetam", "Propofol"], "وەڵامی ڕاست": 0},
            {"پرسیار": "Rituximab بۆ کام نەخۆشی بەکاردێت؟", "هەڵبژاردەکان": ["Non-Hodgkin's Lymphoma & RA", "AML", "CML", "Multiple Myeloma"], "وەڵامی ڕاست": 0},
            {"پرسیار": "CK-MB > CK Total (Macro CK) چی دەگەیەنێت؟", "هەڵبژاردەکان": ["Hypothyroidism یان Malignancy", "Acute MI", "Rhabdomyolysis", "Myocarditis"], "وەڵامی ڕاست": 0},
            {"پرسیار": "Water deprivation test بۆ کام نەخۆشییە؟", "هەڵبژاردەکان": ["Diabetes Insipidus", "SIADH", "DM", "Psychogenic Polydipsia"], "وەڵامی ڕاست": 0},
            {"پرسیار": "Kayser-Fleischer rings نیشانەی چییە؟", "هەڵبژاردەکان": ["Wilson's Disease", "Hemochromatosis", "Alpha-1 Antitrypsin Def.", "Gilbert's"], "وەڵامی ڕاست": 0},
            {"پرسیار": "Thiazide diuretic چ کاردەکات لەسەر کالسیۆم؟", "هەڵبژاردەکان": ["ڕیابسۆرپشنی کالسیۆم زیاد دەکات (Hypercalcemia)", "دەری دەکات (Hypocalcemia)", "کاریگەری نییە", "کالسیۆم لەناو دەبات"], "وەڵامی ڕاست": 0},
        ]
    }
    
    for level, questions in level_questions.items():
        base_quizzes = []
        for q in questions:
            base_quizzes.append({
                "پرسیار": q["پرسیار"],
                "هەڵبژاردەکان": q["هەڵبژاردەکان"],
                "وەڵامی ڕاست": q["وەڵامی ڕاست"],
                "ئاست": level,
                "ئاستی ناو": LEVELS[level]["name"],
                "ڕوونکردنەوە": f"ئاستی {LEVELS[level]['name']}"
            })
        # پڕکردنەوەی کویزەکان تا ژمارەی پێویست
        needed = LEVELS[level]["quizzes"]
        while len(base_quizzes) < needed:
            q = random.choice(questions)
            base_quizzes.append({
                "پرسیار": q["پرسیار"],
                "هەڵبژاردەکان": q["هەڵبژاردەکان"],
                "وەڵامی ڕاست": q["وەڵامی ڕاست"],
                "ئاست": level,
                "ئاستی ناو": LEVELS[level]["name"],
                "ڕوونکردنەوە": f"ئاستی {LEVELS[level]['name']} - کویز ژمارە {len(base_quizzes)+1}"
            })
        quizzes.extend(base_quizzes[:needed])
    return quizzes

MEDICAL_QUIZZES = generate_quizzes_by_level()

def get_quizzes_for_level(level: int) -> List:
    return [q for q in MEDICAL_QUIZZES if q.get("ئاست", 1) == level]

def get_next_quiz(level: int) -> Optional[Dict]:
    quizzes = get_quizzes_for_level(level)
    done = st.session_state.get(f"level_{level}_done", 0)
    if done < len(quizzes):
        return quizzes[done]
    return None

# ================================
# 9. ستەیتەکانی ئەپ
# ================================
if 'current_case' not in st.session_state: st.session_state.current_case = None
if 'diagnosis_submitted' not in st.session_state: st.session_state.diagnosis_submitted = False
if 'quiz_score' not in st.session_state: st.session_state.quiz_score = 0
if 'quiz_completed' not in st.session_state: st.session_state.quiz_completed = False
if 'total_cases_solved' not in st.session_state: st.session_state.total_cases_solved = 0
if 'correct_diagnoses' not in st.session_state: st.session_state.correct_diagnoses = 0
if 'last_activity' not in st.session_state: st.session_state.last_activity = datetime.now()
if 'student_level' not in st.session_state: st.session_state.student_level = "ساڵی یەکەم"
if 'quiz_answers' not in st.session_state: st.session_state.quiz_answers = []
if 'streak_days' not in st.session_state: st.session_state.streak_days = 0
if 'last_study_date' not in st.session_state: st.session_state.last_study_date = datetime.now().date()
if 'achievements' not in st.session_state: st.session_state.achievements = []
if 'favorite_diseases' not in st.session_state: st.session_state.favorite_diseases = []
if 'study_notes' not in st.session_state: st.session_state.study_notes = ""
if 'study_time' not in st.session_state: st.session_state.study_time = 0
if 'quiz_attempts' not in st.session_state: st.session_state.quiz_attempts = 0
if 'simulation_count' not in st.session_state: st.session_state.simulation_count = 0
if 'current_level' not in st.session_state: st.session_state.current_level = 1
if 'level_1_done' not in st.session_state: st.session_state.level_1_done = 0
if 'level_2_done' not in st.session_state: st.session_state.level_2_done = 0
if 'level_3_done' not in st.session_state: st.session_state.level_3_done = 0
if 'level_4_done' not in st.session_state: st.session_state.level_4_done = 0
if 'level_5_done' not in st.session_state: st.session_state.level_5_done = 0
if 'lab_history' not in st.session_state: st.session_state.lab_history = []
if 'custom_lab_tests' not in st.session_state: st.session_state.custom_lab_tests = {}
if 'custom_drugs' not in st.session_state: st.session_state.custom_drugs = {}
if 'current_tab' not in st.session_state: st.session_state.current_tab = "🏠 داشبۆرد"

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
                        st.success("✅ هەژمارەکەت بە سەرکەوتوویی دروست کرا! ئێستا دەتوانیت بچیتە ژوورەوە")
                    else:
                        st.error("❌ ئەم ناوی بەکارهێنەرییە پێشتر بەکارهێنراوە")
    st.markdown('</div></div>', unsafe_allow_html=True)
    st.stop()

# ================================
# سایدبار - Dr.Danyal
# ================================
with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center;padding:10px 0;">
        <span class="dr-icon">🩺</span>
        <div style="font-size:2rem;font-weight:bold;background:linear-gradient(135deg,#4facfe,#43e97b);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
            Dr.Danyal
        </div>
        <div style="color:rgba(255,255,255,0.5);font-size:0.8rem;margin-top:-5px;">🎓 ڕاهێنەری پزیشکی Pro Max</div>
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
        ["🏠 داشبۆرد", "📚 نەخۆشییەکان", "🩺 شیکاری کەیس", "📝 کویز (ئاستی)", "🔬 تاقیگە (٢٠٠)", "📊 پێشکەوتن", "💊 فارماکۆلۆجی", "🧠 AI یاریدەدەر", "🏆 دەستکەوتەکان"],
        index=["🏠 داشبۆرد", "📚 نەخۆشییەکان", "🩺 شیکاری کەیس", "📝 کویز (ئاستی)", "🔬 تاقیگە (٢٠٠)", "📊 پێشکەوتن", "💊 فارماکۆلۆجی", "🧠 AI یاریدەدەر", "🏆 دەستکەوتەکان"].index(st.session_state.current_tab)
    )
    st.session_state.current_tab = page
    st.markdown("---")
    st.markdown(f"🔥 بەردەوامی: {st.session_state.streak_days} ڕۆژ")
    st.markdown(f"⏱️ خوێندن: {st.session_state.study_time} خولەک")
    if st.button("🚪 چوونە دەرەوە", type="primary"):
        save_user_data(st.session_state.username, {"custom_lab_tests": st.session_state.custom_lab_tests, "custom_drugs": st.session_state.custom_drugs})
        st.session_state.logged_in = False
        st.rerun()

# ================================
# Auto-save function
# ================================
def auto_save():
    if st.session_state.logged_in:
        save_user_data(st.session_state.username, {"custom_lab_tests": st.session_state.custom_lab_tests, "custom_drugs": st.session_state.custom_drugs})

# ================================
# پەڕەکان (Pages)
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
    st.markdown(f"""
    <div class="case-card">
        <h3>{get_level_icon(level)} ئاستی ئێستا: {level_info['name']}</h3>
        <div class="progress-container"><div class="progress-fill" style="width:{get_level_progress(st.session_state.quiz_score)}%"></div></div>
        <p>پێشکەوتن: {get_level_progress(st.session_state.quiz_score):.1f}%</p>
    </div>
    """, unsafe_allow_html=True)

elif page == "📝 کویز (ئاستی)":
    st.markdown("### 📝 کویزی پزیشکی - بەپێی ئاست")
    level = get_user_level(st.session_state.quiz_score)
    level_info = get_level_info(level)
    cols = st.columns(5)
    for i in range(1, 6):
        with cols[i-1]:
            info = get_level_info(i)
            done = st.session_state.get(f'level_{i}_done', 0)
            total = info['quizzes']
            pct = (done / total) * 100 if total > 0 else 0
            st.markdown(f"""
            <div class="stat-card" style="border-top-color: {info['color']};">
                <h4>{get_level_icon(i)} ئاست {i}</h4>
                <p>{done}/{total}</p>
                <div class="progress-container"><div class="progress-fill" style="width:{pct}%;"></div></div>
            </div>
            """, unsafe_allow_html=True)
    
    next_quiz = get_next_quiz(level)
    if next_quiz:
        st.markdown(f"""
        <div class="quiz-card">
            <h3>{next_quiz['پرسیار']}</h3>
            <p>ئاست: {get_level_icon(level)} {next_quiz.get('ئاستی ناو', level_info['name'])}</p>
        </div>
        """, unsafe_allow_html=True)
        answer = st.radio("وەڵام:", next_quiz['هەڵبژاردەکان'], key=f"q_{st.session_state.get(f'level_{level}_done', 0)}")
        if st.button("✅ پشتڕاستکردنەوە", type="primary"):
            selected = next_quiz['هەڵبژاردەکان'].index(answer)
            if selected == next_quiz['وەڵامی ڕاست']:
                st.session_state.quiz_score += 1
                st.success("🎉 ڕاستە!")
                st.balloons()
            else:
                st.error(f"❌ هەڵەیە. ڕاست: {next_quiz['هەڵبژاردەکان'][next_quiz['وەڵامی ڕاست']]}")
            st.session_state[f'level_{level}_done'] = st.session_state.get(f'level_{level}_done', 0) + 1
            st.session_state.study_time += 2
            st.rerun()
    else:
        st.success("ئەم ئاستەت تەواو کرد! بچۆ بۆ ئاستی داهاتوو.")
        if level < 5 and st.button(f"🚀 بچۆ بۆ ئاستی {LEVELS[level+1]['name']}"):
            st.session_state.current_level = level + 1
            st.rerun()

elif page == "🔬 تاقیگە (٢٠٠)":
    st.markdown("### 🔬 تاقیگەی ڤێرچواڵ - Dr.Danyal")
    search_lab = st.text_input("🔍 گەڕان:", placeholder="ناوی پشکنین...")
    all_lab_tests = {**LAB_TESTS, **st.session_state.custom_lab_tests}
    cols = st.columns(2)
    idx = 0
    for test_name, test_info in all_lab_tests.items():
        if search_lab and search_lab.lower() not in test_name.lower(): continue
        with cols[idx % 2]:
            low, high = test_info.get("نۆرماڵ", (0, 0))
            st.markdown(f"""
            <div class="lab-result-card lab-normal">
                <strong>{test_name}</strong>
                <p>گروپ: {test_info.get('گروپ', 'گشتی')} | ئامێر: {test_info.get('ئامێر', 'نەزانراو')}</p>
                <p>نۆرماڵ: {low} - {high} {test_info.get('یەکە', '')}</p>
            </div>
            """, unsafe_allow_html=True)
        idx += 1

elif page == "🩺 شیکاری کەیس":
    st.markdown("### 🩺 شیکاری کەیسی پزیشکی")
    if st.button("🔄 کەیسی نوێ", type="primary"):
        disease = random.choice(list(DISEASE_DATABASE.keys()))
        info = DISEASE_DATABASE[disease]
        st.session_state.current_case = {
            "تەمەن": random.randint(18, 80),
            "ڕەگەز": random.choice(['نێر', 'مێ']),
            "نیشانە سەرەکییەکان": random.sample(info['نیشانەکان'], min(5, len(info['نیشانەکان']))),
            "دەستنیشانکردن": disease,
            "ئاستی مەترسی": info['ئاستی مەترسی']
        }
        st.rerun()
    if st.session_state.current_case:
        case = st.session_state.current_case
        st.markdown(f"""
        <div class="case-card">
            <h3>📋 کەیس</h3>
            <p>تەمەن: {case['تەمەن']} | ڕەگەز: {case['ڕەگەز']}</p>
            <p>نیشانەکان: {', '.join(case['نیشانە سەرەکییەکان'])}</p>
            <p>ئاستی مەترسی: <span style="color:{get_risk_color(case['ئاستی مەترسی'])}">{case['ئاستی مەترسی']}</span></p>
        </div>
        """, unsafe_allow_html=True)
        user_diagnosis = st.selectbox("دەستنیشانکردن:", list(DISEASE_DATABASE.keys()))
        if st.button("✅ پشتڕاستکردنەوە", type="primary"):
            st.session_state.total_cases_solved += 1
            if user_diagnosis == case['دەستنیشانکردن']:
                st.session_state.correct_diagnoses += 1
                st.success("🎉 ڕاستە!")
            else:
                st.error(f"❌ هەڵە. ڕاست: {case['دەستنیشانکردن']}")

elif page == "💊 فارماکۆلۆجی":
    st.markdown("### 💊 فارماکۆلۆجی - Dr.Danyal")
    for category, drugs in DRUG_DATABASE.items():
        with st.expander(f"📂 {category} ({len(drugs)} دەرمان)"):
            for drug, info in drugs.items():
                st.markdown(f"""
                <div class="drug-card">
                    <h4>{drug}</h4>
                    <p><strong>ڕێژە:</strong> {info.get('ڕێژە', '')} | <strong>میکانیزم:</strong> {info.get('میکانیزم', '')}</p>
                    <p><strong>وەسف:</strong> {info.get('وەسف', '')}</p>
                    <p><strong>بۆچی:</strong> {info.get('بۆچی', '')}</p>
                </div>
                """, unsafe_allow_html=True)

elif page == "🧠 AI یاریدەدەر":
    st.markdown("### 🧠 یاریدەدەری هۆشمەند - Dr.Danyal")
    symptoms_input = st.text_area("🩺 نیشانەکان بنووسە:", placeholder="وەک: سەرئێشە, تا, کۆخە, ...")
    if st.button("🔍 شیکاری بکە", type="primary"):
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
                <p>ڕێژەی گونجاندن: {r['pct']}% | مەترسی: <span style="color:{get_risk_color(r['risk'])}">{r['risk']}</span></p>
            </div>
            """, unsafe_allow_html=True)

elif page == "🏆 دەستکەوتەکان" or page == "📊 پێشکەوتن":
    st.markdown("### 📊 پێشکەوتن و دەستکەوتەکان")
    cols = st.columns(4)
    with cols[0]: st.metric("📝 کویز", f"{st.session_state.quiz_score}/100")
    with cols[1]: st.metric("🩺 کەیس", st.session_state.total_cases_solved)
    with cols[2]: st.metric("🎯 دەقی", f"{int((st.session_state.correct_diagnoses / max(st.session_state.total_cases_solved, 1)) * 100)}%")
    with cols[3]: st.metric("🔥 بەردەوامی", f"{st.session_state.streak_days} ڕۆژ")

elif page == "📚 نەخۆشییەکان":
    st.markdown(f"### 📚 کتێبخانەی نەخۆشییەکان - Dr.Danyal ({len(DISEASE_DATABASE)}+)")
    search = st.text_input("🔍 گەڕان:", placeholder="ناوی نەخۆشی...")
    for disease, info in DISEASE_DATABASE.items():
        if search and search.lower() not in disease.lower(): continue
        with st.expander(f"🩺 {disease}"):
            st.markdown(f"**⚠️ ئاستی مەترسی:** <span style='color:{get_risk_color(info.get('ئاستی مەترسی', 'کەم'))}'>{info.get('ئاستی مەترسی', 'نەزانراو')}</span>", unsafe_allow_html=True)
            st.markdown(f"**🔑 تایبەتمەندی:** {info.get('تایبەتمەندی', 'نییە')}")

# ================================
# فووەتەر
# ================================
st.markdown("---")
st.markdown(f"""
<div class="footer-style">
    <h3>🩺 Dr.Danyal - ڕاهێنەری پزیشکی Pro Max v6.0</h3>
    <p>{get_disease_count()}+ نەخۆشی | {get_drug_count()}+ دەرمان | {len(MEDICAL_QUIZZES)} کویز | {len(LAB_TESTS)}+ پشکنین</p>
    <p style="font-size:0.7rem;opacity:0.5;">© 2024 Dr.Danyal | داتاکانت بە پارێزراوی هەڵدەگیرێن</p>
</div>
""", unsafe_allow_html=True)
