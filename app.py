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
        font-family: sans-serif;
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
# 5. داتابەسی پشکنینەکانی تاقیگە - بەتاڵ (تەنها زیادکردنی کەسی)
# ================================
LAB_TESTS = {}

# ================================
# 6. داتابەسی دەرمانەکان - بەتاڵ (تەنها زیادکردنی کەسی)
# ================================
DRUG_DATABASE = {}

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
    all_tests = {**LAB_TESTS, **st.session_state.custom_lab_tests}
    for test, info in all_tests.items():
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
    all_tests = {**LAB_TESTS, **st.session_state.custom_lab_tests}
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
# 12. سایدبار
# ================================
with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center;padding:10px 0;">
        <span class="dr-icon">🩺</span>
        <div style="font-size:2rem;font-weight:bold;background:linear-gradient(135deg,#667eea,#f093fb,#4facfe);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
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
    st.markdown(f"**🔬 پشکنین:** {len(st.session_state.custom_lab_tests)}")
    st.markdown(f"**💊 دەرمان:** {len(st.session_state.custom_drugs)}")
    
    st.markdown("---")
    
    page = st.radio(
        "📋 بەشەکان:",
        [
            "🏠 داشبۆرد",
            "📚 نەخۆشییەکان",
            "🩺 شیکاری کەیس",
            "📝 کویز (ئاستی)",
            "🔬 تاقیگە",
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
# خەزنکردنی خۆکارانەی داتا
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
        st.markdown(f'<div class="stat-card"><h3>💊</h3><div class="stat-number">{len(st.session_state.custom_drugs)}</div><p>دەرمان</p></div>', unsafe_allow_html=True)
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
# 15. پەڕەی تاقیگە - تەنها زیادکردنی پشکنینی نوێ
# ================================
elif page == "🔬 تاقیگە":
    st.markdown("""
    <div class="main">
        <h2>🔬 تاقیگەی ڤێرچواڵ - Dr.Danyal</h2>
        <p style="color:#aaa;">پشکنینە تایبەتییەکانی خۆت زیاد بکە</p>
    </div>
    """, unsafe_allow_html=True)
    
    all_lab_tests = {**LAB_TESTS, **st.session_state.custom_lab_tests}
    st.markdown(f"**📊 ژمارەی پشکنینەکان:** {len(all_lab_tests)}")
    
    if st.session_state.custom_lab_tests:
        st.markdown("### 📋 پشکنینە تایبەتییەکانت")
        cols = st.columns(2)
        idx = 0
        
        for test_name, test_info in st.session_state.custom_lab_tests.items():
            with cols[idx % 2]:
                low, high = test_info.get("نۆرماڵ", (0, 0))
                note = test_info.get("تێبینی", "")
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
    else:
        st.info("ℹ️ هێشتا هیچ پشکنینێکی تایبەتیت زیاد نەکردووە. لە خوارەوە پشکنینی نوێ زیاد بکە.")
    
    if st.session_state.custom_lab_tests:
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
                note = all_lab_tests[test_to_analyze].get("تێبینی", "")
                st.markdown(f"""
                <div class="lab-result-card lab-{result['status']}">
                    <h4>{test_to_analyze}</h4>
                    <p><strong>نرخ:</strong> {test_value} {all_lab_tests[test_to_analyze].get('یەکە', '')}</p>
                    <p><strong>نۆرماڵ:</strong> {low} - {high}</p>
                    <p><strong>دۆخ:</strong> <span style="color:{result['color']}">{result['status']}</span></p>
                    <p><strong>تەفسیر:</strong> {result['interpretation']}</p>
                    <p style="color:#aaa;font-size:0.8rem;"><strong>ئامێر:</strong> {all_lab_tests[test_to_analyze].get('ئامێر', 'نەزانراو')}</p>
                    <p style="color:#aaa;font-size:0.8rem;background:rgba(255,255,255,0.05);padding:8px;border-radius:8px;margin-top:5px;">📝 {note}</p>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### ➕ پشکنینێکی نوێ زیاد بکە (لەگەڵ تێبینی خۆت) - بۆ هەمیشە خەزن دەکرێت")
    with st.form("add_lab_test_form", clear_on_submit=True):
        col_new_lab1, col_new_lab2 = st.columns(2)
        with col_new_lab1:
            new_lab_name = st.text_input("ناوی پشکنین:")
            new_lab_group = st.selectbox("گروپ:", ["گشتی", "خوێن", "بایۆکیمیایی", "دڵ", "هەوکردن", "هۆرمۆن", "میز", "ڤیتامین", "معدن"])
            new_lab_low = st.number_input("نزمترین ڕێژەی نۆرماڵ:", value=0.0)
            new_lab_high = st.number_input("بەرزترین ڕێژەی نۆرماڵ:", value=10.0)
        with col_new_lab2:
            new_lab_unit = st.text_input("یەکە:", placeholder="mg/dL")
            new_lab_machine = st.text_input("ئامێر:", placeholder="ئامێری پێوانەکردن")
            new_lab_desc = st.text_area("تەفسیر:", placeholder="ڕوونکردنەوەی ئەم پشکنینە...")
            new_lab_note = st.text_area("📝 تێبینی:", placeholder="تێبینی تایبەتی خۆت لێرە بنووسە...")
            
        submitted = st.form_submit_button("✅ پشکنینەکە زیاد بکە و بۆ هەمیشە خەزن بکە")
        if submitted and new_lab_name:
            st.session_state.custom_lab_tests[new_lab_name] = {
                "گروپ": new_lab_group,
                "نۆرماڵ": (new_lab_low, new_lab_high),
                "یەکە": new_lab_unit,
                "تەفسیر": new_lab_desc,
                "ئامێر": new_lab_machine,
                "تێبینی": new_lab_note
            }
            auto_save()
            st.success(f"پشکنینی '{new_lab_name}' بە سەرکەوتوویی زیاد کرا و بۆ هەمیشە خەزن کرا!")
            st.rerun()

# ================================
# 16. پەڕەی شیکاری کەیس
# ================================
elif page == "🩺 شیکاری کەیس":
    st.markdown("""
    <div class="main">
        <h2>🩺 شیکاری کەیسی پزیشکی</h2>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔄 کەیسی نوێ", type="primary"):
        random_case = training_data.sample(1).iloc[0]
        st.session_state.current_case = random_case
        st.session_state.diagnosis_submitted = False
        st.rerun()
    
    if st.session_state.current_case is not None:
        case = st.session_state.current_case
        st.markdown(f"""
        <div class="case-card">
            <h3>📋 کەیسی {case.get('case_id', 'N/A')}</h3>
            <p><strong>تەمەن:</strong> {case.get('تەمەن', 'N/A')} ساڵ ({get_age_group(case.get('تەمەن', 40))})</p>
            <p><strong>ڕەگەز:</strong> {case.get('ڕەگەز', 'N/A')}</p>
            <p><strong>نیشانەکان:</strong> {', '.join(case.get('نیشانە سەرەکییەکان', []))}</p>
            <p><strong>ئاستی مەترسی:</strong> <span style="color:{get_risk_color(case.get('ئاستی مەترسی', 'کەم'))}">{case.get('ئاستی مەترسی', 'نەزانراو')}</span></p>
            <p><strong>نمرەی مەترسی:</strong> {case.get('نمرەی مەترسی', 0)}%</p>
        </div>
        """, unsafe_allow_html=True)
        
        user_diagnosis = st.selectbox("دەستنیشانکردن:", list(DISEASE_DATABASE.keys()))
        
        if st.button("✅ پشتڕاستکردنەوە", type="primary"):
            correct = case.get('دەستنیشانکردن', '')
            st.session_state.total_cases_solved += 1
            st.session_state.study_time += 3
            
            if user_diagnosis == correct:
                st.session_state.correct_diagnoses += 1
                st.markdown(f'<div class="success-box"><h3>🎉 ڕاستە!</h3><p>{correct}</p></div>', unsafe_allow_html=True)
                st.balloons()
                if st.session_state.correct_diagnoses >= 5:
                    if "دەستنیشانکەری شارەزا" not in st.session_state.achievements:
                        st.session_state.achievements.append("دەستنیشانکەری شارەزا")
            else:
                st.markdown(f'<div class="error-box"><h3>❌ هەڵەیە</h3><p>ڕاست: {correct}</p></div>', unsafe_allow_html=True)
                disease_info = DISEASE_DATABASE.get(correct, {})
                if disease_info:
                    st.info(f"**🔑 خاڵی جیاکەرەوە:** {disease_info.get('تایبەتمەندی', 'نییە')}")
                    st.info(f"**🩺 نیشانە سەرەکییەکان:** {', '.join(disease_info.get('نیشانەکان', [])[:4])}")

# ================================
# 17. پەڕەی فارماکۆلۆجی - تەنها زیادکردنی دەرمانی نوێ
# ================================
elif page == "💊 فارماکۆلۆجی":
    st.markdown("""
    <div class="main">
        <h2>💊 فارماکۆلۆجی و دەرمانناسی - Dr.Danyal</h2>
        <p style="color:#aaa;">دەرمانە تایبەتییەکانی خۆت زیاد بکە</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.custom_drugs:
        st.markdown(f"### 📋 دەرمانە تایبەتییەکانت ({len(st.session_state.custom_drugs)} دەرمان)")
        cols = st.columns(2)
        idx = 0
        for drug, info in st.session_state.custom_drugs.items():
            with cols[idx % 2]:
                note = info.get("تێبینی", "")
                st.markdown(f"""
                <div class="drug-card">
                    <div class="drug-icon">💊</div>
                    <h4>{drug}</h4>
                    <p><strong>ڕێژە:</strong> {info.get('ڕێژە', '')}</p>
                    <p><strong>میکانیزم:</strong> {info.get('میکانیزم', '')}</p>
                    <p><strong>وەسف:</strong> {info.get('وەسف', '')}</p>
                    <p><strong>بۆچی بەکاردێت:</strong> {info.get('بۆچی', '')}</p>
                    <p><strong>کاریگەری لاوەکی:</strong> {info.get('کاریگەری لاوەکی', '')}</p>
                    <p><strong>پێچەوانە:</strong> {info.get('پێچەوانە', '')}</p>
                    <p style="color:#aaa;font-size:0.8rem;background:rgba(255,255,255,0.05);padding:8px;border-radius:8px;margin-top:5px;">📝 {note}</p>
                </div>
                """, unsafe_allow_html=True)
            idx += 1
    else:
        st.info("ℹ️ هێشتا هیچ دەرمانێکی تایبەتیت زیاد نەکردووە. لە خوارەوە دەرمانی نوێ زیاد بکە.")
    
    st.markdown("---")
    st.markdown("### ➕ دەرمانێکی نوێ زیاد بکە (لەگەڵ تێبینی خۆت) - بۆ هەمیشە خەزن دەکرێت")
    with st.form("add_drug_form", clear_on_submit=True):
        col_new_drug1, col_new_drug2 = st.columns(2)
        with col_new_drug1:
            new_drug_name = st.text_input("ناوی دەرمان:")
            new_drug_dose = st.text_input("ڕێژە:", placeholder="500mg")
            new_drug_mech = st.text_input("میکانیزم:", placeholder="چۆن کار دەکات")
            new_drug_effect = st.text_input("کاریگەری لاوەکی:", placeholder="سەرگێژخواردن")
        with col_new_drug2:
            new_drug_contra = st.text_input("پێچەوانە:", placeholder="نەخۆشی گورچیلە")
            new_drug_desc = st.text_area("وەسف:", placeholder="ڕوونکردنەوەی دەرمانەکە...")
            new_drug_why = st.text_area("بۆچی:", placeholder="بۆ چارەسەری چی بەکاردێت...")
            new_drug_note = st.text_area("📝 تێبینی:", placeholder="تێبینی تایبەتی خۆت لێرە بنووسە...")
            
        submitted = st.form_submit_button("✅ دەرمانەکە زیاد بکە و بۆ هەمیشە خەزن بکە")
        if submitted and new_drug_name:
            st.session_state.custom_drugs[new_drug_name] = {
                "ڕێژە": new_drug_dose,
                "میکانیزم": new_drug_mech,
                "کاریگەری لاوەکی": new_drug_effect,
                "پێچەوانە": new_drug_contra,
                "وەسف": new_drug_desc,
                "بۆچی": new_drug_why,
                "تێبینی": new_drug_note
            }
            auto_save()
            st.success(f"دەرمانی '{new_drug_name}' بە سەرکەوتوویی زیاد کرا و بۆ هەمیشە خەزن کرا!")
            st.rerun()

# ================================
# 18. پەڕەی AI یاریدەدەر
# ================================
elif page == "🧠 AI یاریدەدەر":
    st.markdown("""
    <div class="main">
        <h2>🧠 یاریدەدەری هۆشمەند - Dr.Danyal</h2>
        <p style="color:#aaa;">شیکاری نیشانەکان بە یارمەتی AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    symptoms_input = st.text_area("🩺 نیشانەکان بنووسە:", placeholder="وەک: سەرئێشە, تا, کۆخە, ...", height=120)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        age_ai = st.number_input("تەمەن:", 1, 120, 40)
        gender_ai = st.selectbox("ڕەگەز:", ["نێر", "مێ"])
    
    with col2:
        if st.button("🔍 شیکاری AI بکە", type="primary"):
            if symptoms_input.strip():
                symptoms_list = [s.strip() for s in symptoms_input.split(',') if s.strip()]
                if symptoms_list:
                    results = []
                    for disease, info in DISEASE_DATABASE.items():
                        match = len(set(symptoms_list).intersection(set(info['نیشانەکان'])))
                        if match > 0:
                            pct = (match / len(info['نیشانەکان'])) * 100
                            risk_score = calculate_risk_score(disease, age_ai, gender_ai, symptoms_list)
                            results.append({
                                'disease': disease,
                                'pct': round(pct, 1),
                                'risk': info['ئاستی مەترسی'],
                                'risk_score': risk_score,
                                'symptoms': list(set(symptoms_list).intersection(set(info['نیشانەکان']))),
                                'treatment': info['چارەسەر'][:2]
                            })
                    results.sort(key=lambda x: x['pct'], reverse=True)
                    
                    if results:
                        st.markdown("### 📊 ئەنجامی شیکاری")
                        for r in results[:5]:
                            st.markdown(f"""
                            <div class="case-card">
                                <h4>{r['disease']}</h4>
                                <p><strong>ڕێژەی گونجاندن:</strong> {r['pct']}%</p>
                                <p><strong>نیشانە هاوبەشەکان:</strong> {', '.join(r['symptoms'])}</p>
                                <p><strong>ئاستی مەترسی:</strong> <span style="color:{get_risk_color(r['risk'])}">{r['risk']}</span></p>
                                <p><strong>نمرەی مەترسی:</strong> {r['risk_score']}%</p>
                                <p><strong>چارەسەر:</strong> {', '.join(r['treatment'])}</p>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.warning("هیچ نەخۆشییەک نەدۆزرایەوە کە نیشانەکانت بگونجێت.")
                else:
                    st.error("تکایە نیشانەکان بنووسە.")
            else:
                st.error("تکایە نیشانەکان بنووسە.")

# ================================
# 19. پەڕەی پێشکەوتن و دەستکەوتەکان
# ================================
elif page == "🏆 دەستکەوتەکان" or page == "📊 پێشکەوتن":
    st.markdown("""
    <div class="main">
        <h2>📊 پێشکەوتن و دەستکەوتەکان - Dr.Danyal</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🎯 ئاستەکان")
    cols = st.columns(5)
    for i in range(1, 6):
        with cols[i-1]:
            info = get_level_info(i)
            done = st.session_state.get(f'level_{i}_done', 0)
            total = info['quizzes']
            pct = (done / total) * 100 if total > 0 else 0
            is_current = i == get_user_level(st.session_state.quiz_score)
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
    
    st.markdown("### 🏆 دەستکەوتەکان")
    
    all_achievements = [
        {"icon": "⭐", "name": "دەستنیشانکەری شارەزا", "condition": st.session_state.correct_diagnoses >= 5},
        {"icon": "📚", "name": "ڕاهێنەری پزیشکی", "condition": st.session_state.total_cases_solved >= 20},
        {"icon": "📝", "name": "شارەزای کویز", "condition": st.session_state.quiz_score >= 30},
        {"icon": "🎓", "name": "پزیشکی گشتی", "condition": st.session_state.quiz_score >= 50},
        {"icon": "👨‍⚕️", "name": "پزیشکی لێهاتوو", "condition": st.session_state.quiz_score >= 80},
        {"icon": "🔥", "name": "بەردەوامی ٧ ڕۆژ", "condition": st.session_state.streak_days >= 7},
        {"icon": "💪", "name": "بەردەوامی ٣٠ ڕۆژ", "condition": st.session_state.streak_days >= 30},
        {"icon": "🔬", "name": "شارەزای تاقیگە", "condition": len(st.session_state.lab_history) >= 50},
        {"icon": "💊", "name": "فارماکۆلۆجیست", "condition": len(st.session_state.favorite_diseases) >= 10}
    ]
    
    for ach in all_achievements:
        if ach["condition"] and ach["name"] not in st.session_state.achievements:
            st.session_state.achievements.append(ach["name"])
    
    if st.session_state.achievements:
        cols = st.columns(3)
        for i, ach in enumerate(st.session_state.achievements):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="achievement-badge">
                    {ach} ✅
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("💪 بەردەوام بە! دەستکەوتەکان لە ڕێگادان...")
    
    st.markdown("---")
    st.markdown("### 📊 ئاماری گشتی")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📝 کویز", f"{st.session_state.quiz_score}/100")
    with col2:
        st.metric("🩺 کەیس", st.session_state.total_cases_solved)
    with col3:
        accuracy = int((st.session_state.correct_diagnoses / max(st.session_state.total_cases_solved, 1)) * 100)
        st.metric("🎯 دەقی", f"{accuracy}%")
    with col4:
        st.metric("🔥 بەردەوامی", f"{st.session_state.streak_days} ڕۆژ")

# ================================
# 20. پەڕەی نەخۆشییەکان
# ================================
elif page == "📚 نەخۆشییەکان":
    st.markdown(f"""
    <div class="main">
        <h2>📚 کتێبخانەی نەخۆشییەکان - Dr.Danyal</h2>
        <p style="color:#aaa;">{get_disease_count()} نەخۆشی لەگەڵ پشکنین و چارەسەر</p>
    </div>
    """, unsafe_allow_html=True)
    
    search = st.text_input("🔍 گەڕان:", placeholder="ناوی نەخۆشی...")
    filter_risk = st.selectbox("فلتر:", ["هەموو", "زۆر مەترسیدار", "مەترسیدار", "مامناوەند", "کەم"])
    filter_age = st.selectbox("گروپی تەمەن:", ["هەموو", "منداڵان", "گەنجان", "تەمەن مامناوەند", "پیران"])
    
    filtered = {k: v for k, v in DISEASE_DATABASE.items() if (not search or search in k)}
    if filter_risk != "هەموو":
        filtered = {k: v for k, v in filtered.items() if v.get('ئاستی مەترسی', '') == filter_risk}
    if filter_age != "هەموو":
        filtered = {k: v for k, v in filtered.items() if filter_age in v.get('گروپی تەمەن', '')}
    
    st.markdown(f"**📊 ژمارە:** {len(filtered)} نەخۆشی")
    
    cols = st.columns(2)
    idx = 0
    for disease, info in filtered.items():
        with cols[idx % 2]:
            with st.expander(f"🩺 {disease}"):
                st.markdown(f"**⚠️ ئاستی مەترسی:** <span style='color:{get_risk_color(info.get('ئاستی مەترسی', 'کەم'))}'>{info.get('ئاستی مەترسی', 'نەزانراو')}</span>", unsafe_allow_html=True)
                st.markdown(f"**👤 گروپی تەمەن:** {info.get('گروپی تەمەن', 'هەموو')}")
                st.markdown(f"**📊 ڕێژەی تووشبوون:** {info.get('ڕێژەی تووشبوون', 'نەزانراو')}")
                st.markdown(f"**🏥 جۆری نەخۆشی:** {info.get('جۆری نەخۆشی', 'نەزانراو')}")
                
                st.markdown("**🔍 نیشانەکان:**")
                for s in info.get('نیشانەکان', [])[:6]:
                    st.markdown(f"- {s}")
                
                st.markdown("**🧪 پشکنینەکان (لەگەڵ نۆرماڵ):**")
                for test, value in list(info.get('پشکنینەکان', {}).items())[:4]:
                    st.markdown(f"- {test}: {value}")
                
                st.markdown("**💊 چارەسەر:**")
                for t in info.get('چارەسەر', [])[:4]:
                    st.markdown(f"- {t}")
                
                st.info(f"**🔑 تایبەتمەندی:** {info.get('تایبەتمەندی', 'نییە')}")
                
                if info.get('ڕێپیشگیری'):
                    st.markdown("**🛡️ ڕێپیشگیری:**")
                    for p in info['ڕێپیشگیری'][:3]:
                        st.markdown(f"- {p}")
        idx += 1

# ================================
# 21. فووەتەر
# ================================
st.markdown("---")
st.markdown(f"""
<div class="footer-style">
    <h3>🩺 Dr.Danyal - ڕاهێنەری پزیشکی Pro Max v5.0</h3>
    <p>{get_disease_count()} نەخۆشی | {len(st.session_state.custom_drugs)} دەرمان | {get_quiz_count()} کویز | {len(st.session_state.custom_lab_tests)} پشکنین</p>
    <p style="font-size:0.8rem;opacity:0.8;">© 2024 Dr.Danyal | بەکارهێنەر: {st.session_state.username} | داتاکانت بۆ هەمیشە خەزن دەکرێن</p>
    <p style="font-size:0.7rem;opacity:0.5;">پشکنین و دەرمانە زیادکراوەکانت بە پارێزراوی لە فایلی JSON دا هەڵدەگیرێن</p>
</div>
""", unsafe_allow_html=True)

# ================================
# 22. کۆتایی
# ================================
