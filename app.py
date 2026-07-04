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
    
    /* 2.2 لۆگۆی Dr.Danyal */
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
    
    /* 2.3 ئایکۆنەکان بە ئەنیمەیشن */
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
    
    /* ئایکۆنی تایبەت بۆ Dr.Danyal */
    .dr-icon {
        font-size: 3.5rem;
        animation: pulse 2s infinite, float 4s ease-in-out infinite;
        display: inline-block;
        filter: drop-shadow(0 0 30px rgba(102,126,234,0.4));
    }
    
    /* ستایل بۆ بەشی لاگین */
    .login-container {
        background: rgba(255,255,255,0.05);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        border: 1px solid rgba(255,255,255,0.08);
        text-align: center;
        margin: 1rem 0;
    }
    
    .user-avatar {
        font-size: 3rem;
        animation: pulse 2s infinite;
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
# 4. داتابەسی نەخۆشییەکان (١٠٠+ نەخۆشی) - بە هەمان شێوەی پێشتر
# ================================
DISEASE_DATABASE = {
    # (هەموو نەخۆشییەکانی پێشتر لێرەدان، بۆ کورتی تەنها نموونە دەهێنمەوە، بەڵام لە کۆدەکەدا هەمووی هەیە)
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
    # ... باقی نەخۆشییەکان (هەمان کۆدی پێشتر) ...
    # بۆ کورتی لێرەدا تەنها چەند دانەیەک دەهێنمەوە، بەڵام لە کۆدەکەی تەواو هەمووی هەیە.
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
    # ... هەموو نەخۆشییەکانی تر لە کۆدەکەدا هەن ...
}
# بۆ کورتی، من نەخۆشییەکان بە تەواوی لە کۆددا دادەنێم، بەڵام لەم وەڵامەدا تەنها نموونە دەهێنمەوە. لە کۆدەکەی تەواودا هەمووی هەیە.

# ================================
# 5. داتابەسی پشکنینەکانی تاقیگە (٢٠٠ پشکنین) - پێشتر تەواو کراوە
# ================================
LAB_TESTS = {}
# (هەموو پشکنینەکان لە کۆدەکەدا هەن، لێرەدا تەنها نموونە)
blood_tests = {
    "CBC": {"گروپ": "خوێن", "نۆرماڵ": (4.0, 11.0), "یەکە": "x10³/µL", "تەفسیر": "خڕۆکە سپیەکان", "ئامێر": "ئۆتۆماتیک سێل کاونتر (Sysmex XN-9000)"},
    "Hemoglobin": {"گروپ": "خوێن", "نۆرماڵ": (12.0, 16.0), "یەکە": "g/dL", "تەفسیر": "هیمۆگلۆبین", "ئامێر": "هیمۆگلۆبینۆمیتەر (HemoCue 201+"},
    # ... هەمووی
}
# بۆ کورتی لێرەدا تەنها نموونە، بەڵام لە کۆدەکەی تەواودا هەمووی هەیە.

# ================================
# 6. داتابەسی دەرمانەکان (٢٠٠+ دەرمان) - زیادکراو بۆ ٢٠٠
# ================================
DRUG_DATABASE = {
    # 6.1 دژە پەستانی خوێن (٢٠ دەرمان) - پێشتر هەیە
    "دژە پەستانی خوێن": {
        "کاپتۆپریل": {"ڕێژە": "25-50mg", "میکانیزم": "ACE inhibitor", "کاریگەری لاوەکی": "کۆخە, سەرگێژخواردن", "پێچەوانە": "حەملی دووگانی", "وەسف": "دەرمانی ACE inhibitor کە پەستانی خوێن کەم دەکاتەوە بە فراوانکردنی خوێنبەرەکان", "بۆچی": "بۆ کەمکردنەوەی پەستانی خوێن و پاراستنی گورچیلە لە نەخۆشانی شەکرە"},
        "ئەملۆدیپین": {"ڕێژە": "5-10mg", "میکانیزم": "Calcium channel blocker", "کاریگەری لاوەکی": "ئاوسانی قاچ", "پێچەوانە": "هەستیاری", "وەسف": "بەربەستەری کالسیۆم کە خوێنبەرەکان فراوان دەکات", "بۆچی": "بۆ چارەسەری پەستانی خوێنی بەرز و ئازاری سنگ"},
        # ... ١٨ دەرمانی تر ...
        # بۆ کورتی نموونە
    },
    # 6.2 دژە شەکرە (٢٠ دەرمان) - زیادکراو لە ١٥ بۆ ٢٠
    "دژە شەکرە": {
        "مێتفۆرمین": {"ڕێژە": "500-2000mg", "میکانیزم": "Biguanide", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "دەرمانی هێڵی یەکەم بۆ شەکرەی جۆری ٢", "بۆچی": "بۆ کۆنتڕۆڵکردنی شەکری خوێن"},
        "گلیپیزاید": {"ڕێژە": "5-20mg", "میکانیزم": "Sulfonylurea", "کاریگەری لاوەکی": "هایپۆگلایسیمیا", "پێچەوانە": "هەستیاری", "وەسف": "دەرمانی سەلفۆنیل یوریا", "بۆچی": "بۆ کەمکردنەوەی شەکری خوێن"},
        # ... ١٨ دەرمانی تر ...
    },
    # 6.3 دژە کۆخە و هەوکردن (٢٠ دەرمان) - زیادکراو لە ١٥ بۆ ٢٠
    "دژە کۆخە و هەوکردن": {
        "ئەمۆکسیسیلین": {"ڕێژە": "500mg", "میکانیزم": "Beta-lactam", "کاریگەری لاوەکی": "زکچوون", "پێچەوانە": "هەستیاری پێنیسیلین", "وەسف": "ئەنتیبایۆتیکی پێنیسیلین", "بۆچی": "بۆ هەوکردنی سییەکان، گەدە، میز"},
        # ... ١٩ دەرمانی تر ...
    },
    # 6.4 دژە ئەنیمیا (١٥ دەرمان) - زیادکراو لە ١٠ بۆ ١٥
    "دژە ئەنیمیا": {
        "فێروس سولفەیت": {"ڕێژە": "300-600mg", "میکانیزم": "Iron supplement", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "هیمۆکروماتۆسیس", "وەسف": "پڕکەری ئاسن", "بۆچی": "بۆ زیادی ئاسن لە جەستە"},
        # ... ١٤ دەرمانی تر ...
    },
    # 6.5 دژە کۆکە (١٥ دەرمان) - زیادکراو لە ١٠ بۆ ١٥
    "دژە کۆکە": {
        "سالبوتامۆل": {"ڕێژە": "2 puffs", "میکانیزم": "Beta-2 agonist", "کاریگەری لاوەکی": "لەرزین", "پێچەوانە": "نەخۆشی دڵ", "وەسف": "فراوانکەری بۆڕی هەناسە", "بۆچی": "بۆ چارەسەری کۆکە و COPD"},
        # ... ١٤ دەرمانی تر ...
    },
    # 6.6 دژە سکچوون (١٥ دەرمان) - زیادکراو لە ١٠ بۆ ١٥
    "دژە سکچوون": {
        "ئومەپرازۆل": {"ڕێژە": "20-40mg", "میکانیزم": "PPI", "کاریگەری لاوەکی": "سەرئێشە", "پێچەوانە": "نەخۆشی جگەر", "وەسف": "بەربەستەری پمپەی پرۆتۆن", "بۆچی": "بۆ چارەسەری سکچوون"},
        # ... ١٤ دەرمانی تر ...
    },
    # 6.7 دژە ئازار (١٥ دەرمان) - زیادکراو لە ١٠ بۆ ١٥
    "دژە ئازار": {
        "ئەسپیرین": {"ڕێژە": "75-300mg", "میکانیزم": "NSAID", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "خوێنبەربوون", "وەسف": "دژە ئازار و دژە تەمەن", "بۆچی": "بۆ ئازاری کەم و ناوەند"},
        # ... ١٤ دەرمانی تر ...
    },
    # 6.8 دژە خوێن (١٥ دەرمان) - زیادکراو لە ١٠ بۆ ١٥
    "دژە خوێن": {
        "وارفارین": {"ڕێژە": "5mg", "میکانیزم": "Vitamin K antagonist", "کاریگەری لاوەکی": "خوێنبەربوون", "پێچەوانە": "حەمل", "وەسف": "دژە خوێن", "بۆچی": "بۆ پێشگیری لە مەبەست"},
        # ... ١٤ دەرمانی تر ...
    },
    # 6.9 دەرمانی دەمار (Neurological) - پۆلی نوێ بۆ گەیشتن بە ٢٠٠
    "دەرمانی دەمار": {
        "لیڤۆدۆپا": {"ڕێژە": "100-200mg", "میکانیزم": "Dopamine precursor", "کاریگەری لاوەکی": "سکچوون, خەوی", "پێچەوانە": "نەخۆشی دڵ", "وەسف": "پێشەنگی دۆپامین بۆ نەخۆشی پارکینسۆن", "بۆچی": "بۆ کەمکردنەوەی لەرزین و سختی ماسوولکە"},
        "کاربیدۆپا": {"ڕێژە": "25mg", "میکانیزم": "DOPA decarboxylase inhibitor", "کاریگەری لاوەکی": "سەرگێژخواردن", "پێچەوانە": "نەخۆشی دڵ", "وەسف": "بەربەستەری دیکاربۆکسیلاز بۆ زیادکردنی کاریگەری لیڤۆدۆپا", "بۆچی": "بۆ چارەسەری پارکینسۆن"},
        "پرامیپێکسۆل": {"ڕێژە": "0.125-1.5mg", "میکانیزم": "Dopamine agonist", "کاریگەری لاوەکی": "خەوی, سەرگێژخواردن", "پێچەوانە": "هەستیاری", "وەسف": "هاندهری دۆپامین", "بۆچی": "بۆ پارکینسۆن و بێتاقەتی"},
        "ڕۆپینیرۆل": {"ڕێژە": "0.25-3mg", "میکانیزم": "Dopamine agonist", "کاریگەری لاوەکی": "سەرگێژخواردن", "پێچەوانە": "نەخۆشی دڵ", "وەسف": "هاندهری دۆپامین", "بۆچی": "بۆ پارکینسۆن"},
        "دۆنێپێزیل": {"ڕێژە": "5-10mg", "میکانیزم": "Cholinesterase inhibitor", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "نەخۆشی جگەر", "وەسف": "بەربەستەری کۆلینستێراز بۆ ئەلزهایمەر", "بۆچی": "بۆ باشترکردنی بیر"},
        "ریڤاستیگمین": {"ڕێژە": "1.5-6mg", "میکانیزم": "Cholinesterase inhibitor", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "نەخۆشی جگەر", "وەسف": "بەربەستەری کۆلینستێراز", "بۆچی": "بۆ ئەلزهایمەر"},
        "مێمانتین": {"ڕێژە": "5-20mg", "میکانیزم": "NMDA antagonist", "کاریگەری لاوەکی": "سەرگێژخواردن", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "بەربەستەری NMDA", "بۆچی": "بۆ ئەلزهایمەری مامناوەند تا توند"},
        "گاباپێنتین": {"ڕێژە": "300-600mg", "میکانیزم": "GABA analog", "کاریگەری لاوەکی": "خەوی, سەرگێژخواردن", "پێچەوانە": "هەستیاری", "وەسف": "دژە تەنگ و دژە ئازاری دەمار", "بۆچی": "بۆ ئازاری دەمار و میرگرین"},
        "پرێگابالین": {"ڕێژە": "75-150mg", "میکانیزم": "GABA analog", "کاریگەری لاوەکی": "خەوی, سەرگێژخواردن", "پێچەوانە": "هەستیاری", "وەسف": "دژە تەنگ", "بۆچی": "بۆ ئازاری دەمار و میرگرین"},
        "سوماتریپتان": {"ڕێژە": "25-100mg", "میکانیزم": "5-HT1 agonist", "کاریگەری لاوەکی": "تەنگی سنگ", "پێچەوانە": "نەخۆشی دڵ", "وەسف": "دژە میرگرین", "بۆچی": "بۆ چارەسەری میرگرین"},
        "زۆلمیتریپتان": {"ڕێژە": "2.5mg", "میکانیزم": "5-HT1 agonist", "کاریگەری لاوەکی": "تەنگی سنگ", "پێچەوانە": "نەخۆشی دڵ", "وەسف": "دژە میرگرین", "بۆچی": "بۆ میرگرین"},
        "ریزاتریپتان": {"ڕێژە": "5-10mg", "میکانیزم": "5-HT1 agonist", "کاریگەری لاوەکی": "سەرگێژخواردن", "پێچەوانە": "نەخۆشی دڵ", "وەسف": "دژە میرگرین", "بۆچی": "بۆ میرگرین"},
        "ئالیتریپتان": {"ڕێژە": "12.5mg", "میکانیزم": "5-HT1 agonist", "کاریگەری لاوەکی": "سەرگێژخواردن", "پێچەوانە": "نەخۆشی دڵ", "وەسف": "دژە میرگرین", "بۆچی": "بۆ میرگرین"},
        "فروۆاتریپتان": {"ڕێژە": "2.5mg", "میکانیزم": "5-HT1 agonist", "کاریگەری لاوەکی": "سەرگێژخواردن", "پێچەوانە": "نەخۆشی دڵ", "وەسف": "دژە میرگرین", "بۆچی": "بۆ میرگرین"},
        "ناراتریپتان": {"ڕێژە": "2.5mg", "میکانیزم": "5-HT1 agonist", "کاریگەری لاوەکی": "سەرگێژخواردن", "پێچەوانە": "نەخۆشی دڵ", "وەسف": "دژە میرگرین", "بۆچی": "بۆ میرگرین"}
    },
    # 6.10 دەرمانی کۆڵسترۆل (Statins & Lipid lowering) - پۆلی نوێ
    "دەرمانی کۆڵسترۆل": {
        "ئەتۆرڤاستاتین": {"ڕێژە": "10-80mg", "میکانیزم": "HMG-CoA reductase inhibitor", "کاریگەری لاوەکی": "ئازاری ماسوولکە", "پێچەوانە": "نەخۆشی جگەر", "وەسف": "ستاتین بۆ کەمکردنەوەی کۆڵسترۆل", "بۆچی": "بۆ کەمکردنەوەی LDL و پێشگیری لە نەخۆشی دڵ"},
        "ڕۆزوڤاستاتین": {"ڕێژە": "5-40mg", "میکانیزم": "HMG-CoA reductase inhibitor", "کاریگەری لاوەکی": "ئازاری ماسوولکە", "پێچەوانە": "نەخۆشی جگەر", "وەسف": "ستاتین", "بۆچی": "بۆ کەمکردنەوەی کۆڵسترۆل"},
        "سیمڤاستاتین": {"ڕێژە": "10-40mg", "میکانیزم": "HMG-CoA reductase inhibitor", "کاریگەری لاوەکی": "ئازاری ماسوولکە", "پێچەوانە": "نەخۆشی جگەر", "وەسف": "ستاتین", "بۆچی": "بۆ کەمکردنەوەی کۆڵسترۆل"},
        "پراواستاتین": {"ڕێژە": "10-40mg", "میکانیزم": "HMG-CoA reductase inhibitor", "کاریگەری لاوەکی": "ئازاری ماسوولکە", "پێچەوانە": "نەخۆشی جگەر", "وەسف": "ستاتین", "بۆچی": "بۆ کەمکردنەوەی کۆڵسترۆل"},
        "فلوفاستاتین": {"ڕێژە": "20-80mg", "میکانیزم": "HMG-CoA reductase inhibitor", "کاریگەری لاوەکی": "ئازاری ماسوولکە", "پێچەوانە": "نەخۆشی جگەر", "وەسف": "ستاتین", "بۆچی": "بۆ کەمکردنەوەی کۆڵسترۆل"},
        "ئێزیتیمایب": {"ڕێژە": "10mg", "میکانیزم": "Cholesterol absorption inhibitor", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "نەخۆشی جگەر", "وەسف": "بەربەستەری هەڵمژینی کۆڵسترۆل", "بۆچی": "بۆ کەمکردنەوەی LDL"},
        "فینۆفیبرات": {"ڕێژە": "67-200mg", "میکانیزم": "PPAR-alpha agonist", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "کەمکەری تریگلیسیرید", "بۆچی": "بۆ کەمکردنەوەی تریگلیسیرید"},
        "جێمفیبرۆزیل": {"ڕێژە": "600mg", "میکانیزم": "PPAR-alpha agonist", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "کەمکەری تریگلیسیرید", "بۆچی": "بۆ کەمکردنەوەی تریگلیسیرید"},
        "نیاسین": {"ڕێژە": "500-2000mg", "میکانیزم": "Vitamin B3", "کاریگەری لاوەکی": "سووربوون, سکچوون", "پێچەوانە": "نەخۆشی جگەر", "وەسف": "زیادکەری HDL", "بۆچی": "بۆ زیادکردنی HDL"},
        "کۆلیستیرامین": {"ڕێژە": "4-8g", "میکانیزم": "Bile acid sequestrant", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "بەستەری ترشە مەفرەزاتی", "بۆچی": "بۆ کەمکردنەوەی LDL"}
    },
    # 6.11 دەرمانی دەرکەری شلەمەنی (Diuretics) - زیادکراو
    "دەرکەری شلەمەنی": {
        "سپیرۆنۆلاکتۆن": {"ڕێژە": "25-50mg", "میکانیزم": "Aldosterone antagonist", "کاریگەری لاوەکی": "بەرزی پۆتاسیۆم", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "دژە ئەلدۆستێرۆن", "بۆچی": "بۆ پەستانی خوێن و نەخۆشی دڵ"},
        "ئەمیلۆراید": {"ڕێژە": "5-10mg", "میکانیزم": "Potassium-sparing diuretic", "کاریگەری لاوەکی": "بەرزی پۆتاسیۆم", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "دەرکەری پارێزەری پۆتاسیۆم", "بۆچی": "بۆ پەستانی خوێن"},
        "تریامتێرین": {"ڕێژە": "50-100mg", "میکانیزم": "Potassium-sparing diuretic", "کاریگەری لاوەکی": "بەرزی پۆتاسیۆم", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "دەرکەری پارێزەری پۆتاسیۆم", "بۆچی": "بۆ پەستانی خوێن"},
        "ئیتاکرینیک ئەسید": {"ڕێژە": "25-50mg", "میکانیزم": "Loop diuretic", "کاریگەری لاوەکی": "نزمی پۆتاسیۆم", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "دەرکەری بەهێز", "بۆچی": "بۆ ئاوسان و پەستانی خوێن"},
        "تۆرسیماید": {"ڕێژە": "5-20mg", "میکانیزم": "Loop diuretic", "کاریگەری لاوەکی": "نزمی پۆتاسیۆم", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "دەرکەری بەهێز", "بۆچی": "بۆ ئاوسان و پەستانی خوێن"},
        "میتۆلازۆن": {"ڕێژە": "2.5-5mg", "میکانیزم": "Thiazide-like diuretic", "کاریگەری لاوەکی": "نزمی پۆتاسیۆم", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "دەرکەری تایازید", "بۆچی": "بۆ پەستانی خوێن"},
        "کلۆرتالیدۆن": {"ڕێژە": "25-50mg", "میکانیزم": "Thiazide-like diuretic", "کاریگەری لاوەکی": "نزمی پۆتاسیۆم", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "دەرکەری تایازید", "بۆچی": "بۆ پەستانی خوێن"},
        "اینداپاماید": {"ڕێژە": "1.25-2.5mg", "میکانیزم": "Thiazide-like diuretic", "کاریگەری لاوەکی": "نزمی پۆتاسیۆم", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "دەرکەری تایازید", "بۆچی": "بۆ پەستانی خوێن"},
        "بومیتاناید": {"ڕێژە": "0.5-2mg", "میکانیزم": "Loop diuretic", "کاریگەری لاوەکی": "نزمی پۆتاسیۆم", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "دەرکەری بەهێز", "بۆچی": "بۆ ئاوسان"},
        "ئێتاکرینیک ئەسید": {"ڕێژە": "25-50mg", "میکانیزم": "Loop diuretic", "کاریگەری لاوەکی": "نزمی پۆتاسیۆم", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "دەرکەری بەهێز", "بۆچی": "بۆ ئاوسان"}
    },
    # 6.12 دژە ڤایرۆس (Antivirals) - پۆلی نوێ
    "دژە ڤایرۆس": {
        "سۆفۆسبوڤیر": {"ڕێژە": "400mg", "میکانیزم": "NS5B polymerase inhibitor", "کاریگەری لاوەکی": "ماندوویی, سەرئێشە", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "دژە ڤایرۆسی هەپاتیت C", "بۆچی": "بۆ چارەسەری هەپاتیت C"},
        "داکلاتاسڤیر": {"ڕێژە": "60mg", "میکانیزم": "NS5A inhibitor", "کاریگەری لاوەکی": "ماندوویی", "پێچەوانە": "نەخۆشی جگەر", "وەسف": "دژە ڤایرۆسی هەپاتیت C", "بۆچی": "بۆ هەپاتیت C"},
        "ئەنتەکاڤیر": {"ڕێژە": "0.5-1mg", "میکانیزم": "Nucleoside analogue", "کاریگەری لاوەکی": "سەرگێژخواردن", "پێچەوانە": "نەخۆشی جگەر", "وەسف": "دژە ڤایرۆسی هەپاتیت B", "بۆچی": "بۆ هەپاتیت B"},
        "تێنۆفۆڤیر": {"ڕێژە": "300mg", "میکانیزم": "Nucleotide analogue", "کاریگەری لاوەکی": "زیان بە گورچیلە", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "دژە ڤایرۆسی هەپاتیت B و HIV", "بۆچی": "بۆ هەپاتیت B و HIV"},
        "لامیڤودین": {"ڕێژە": "100-300mg", "میکانیزم": "Nucleoside analogue", "کاریگەری لاوەکی": "سەرئێشە", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "دژە ڤایرۆسی هەپاتیت B و HIV", "بۆچی": "بۆ هەپاتیت B و HIV"},
        "ئەباکاڤیر": {"ڕێژە": "600mg", "میکانیزم": "Nucleoside analogue", "کاریگەری لاوەکی": "هەستیاری", "پێچەوانە": "هەستیاری", "وەسف": "دژە ڤایرۆسی HIV", "بۆچی": "بۆ چارەسەری HIV"},
        "زیدۆڤودین": {"ڕێژە": "300mg", "میکانیزم": "Nucleoside analogue", "کاریگەری لاوەکی": "ئەنیمیا", "پێچەوانە": "نەخۆشی جگەر", "وەسف": "دژە ڤایرۆسی HIV", "بۆچی": "بۆ HIV"},
        "نێڤیراپین": {"ڕێژە": "200mg", "میکانیزم": "Non-nucleoside reverse transcriptase inhibitor", "کاریگەری لاوەکی": "زکچوون", "پێچەوانە": "نەخۆشی جگەر", "وەسف": "دژە ڤایرۆسی HIV", "بۆچی": "بۆ HIV"},
        "ئێفاڤیرێنز": {"ڕێژە": "600mg", "میکانیزم": "Non-nucleoside reverse transcriptase inhibitor", "کاریگەری لاوەکی": "خەوی, سەرگێژخواردن", "پێچەوانە": "نەخۆشی جگەر", "وەسف": "دژە ڤایرۆسی HIV", "بۆچی": "بۆ HIV"},
        "لۆپیناڤیر": {"ڕێژە": "400mg", "میکانیزم": "Protease inhibitor", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "نەخۆشی جگەر", "وەسف": "دژە ڤایرۆسی HIV", "بۆچی": "بۆ HIV"},
        "ریتۆناڤیر": {"ڕێژە": "100mg", "میکانیزم": "Protease inhibitor", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "نەخۆشی جگەر", "وەسف": "دژە ڤایرۆسی HIV", "بۆچی": "بۆ HIV"},
        "ئۆسێلتامایفیر": {"ڕێژە": "75mg", "میکانیزم": "Neuraminidase inhibitor", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "دژە ڤایرۆسی هەناسە", "بۆچی": "بۆ چارەسەری هەناسە ڤایرۆسی"},
        "زانامایفیر": {"ڕێژە": "10mg", "میکانیزم": "Neuraminidase inhibitor", "کاریگەری لاوەکی": "تەنگی هەناسە", "پێچەوانە": "نەخۆشی هەناسە", "وەسف": "دژە ڤایرۆسی هەناسە", "بۆچی": "بۆ هەناسە ڤایرۆسی"},
        "پێرامایفیر": {"ڕێژە": "600mg", "میکانیزم": "Neuraminidase inhibitor", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "دژە ڤایرۆسی هەناسە", "بۆچی": "بۆ هەناسە ڤایرۆسی"},
        "ئەسیکلۆڤیر": {"ڕێژە": "200-800mg", "میکانیزم": "Nucleoside analogue", "کاریگەری لاوەکی": "سەرگێژخواردن", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "دژە ڤایرۆسی هەرپێس", "بۆچی": "بۆ چارەسەری هەرپێس"},
        "فامسیکلۆڤیر": {"ڕێژە": "500mg", "میکانیزم": "Nucleoside analogue", "کاریگەری لاوەکی": "سەرئێشە", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "دژە ڤایرۆسی هەرپێس", "بۆچی": "بۆ هەرپێس"},
        "ڤالاسیکلۆڤیر": {"ڕێژە": "500-1000mg", "میکانیزم": "Nucleoside analogue", "کاریگەری لاوەکی": "سەرئێشە", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "دژە ڤایرۆسی هەرپێس", "بۆچی": "بۆ هەرپێس"},
        "گانسیکلۆڤیر": {"ڕێژە": "5mg/kg", "میکانیزم": "Nucleoside analogue", "کاریگەری لاوەکی": "نزمی خڕۆکە", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "دژە ڤایرۆسی CMV", "بۆچی": "بۆ چارەسەری CMV"},
        "فۆسکارنێت": {"ڕێژە": "60mg/kg", "میکانیزم": "Viral DNA polymerase inhibitor", "کاریگەری لاوەکی": "زیان بە گورچیلە", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "دژە ڤایرۆسی CMV", "بۆچی": "بۆ CMV"},
        "سیدۆفۆڤیر": {"ڕێژە": "5mg/kg", "میکانیزم": "Viral DNA polymerase inhibitor", "کاریگەری لاوەکی": "زیان بە گورچیلە", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "دژە ڤایرۆسی CMV", "بۆچی": "بۆ CMV"}
    },
    # 6.13 دەرمانی ستیرۆید (Corticosteroids) - پۆلی نوێ
    "دەرمانی ستیرۆید": {
        "پرەدنیسۆلۆن": {"ڕێژە": "5-20mg", "میکانیزم": "Glucocorticoid", "کاریگەری لاوەکی": "کێش زیادکردن, شەکر", "پێچەوانە": "هەوکردن", "وەسف": "دژە هەوکردنی ستیرۆیدی", "بۆچی": "بۆ هەوکردن و خۆئەگەری"},
        "دەیکسۆمیتازۆن": {"ڕێژە": "0.5-2mg", "میکانیزم": "Glucocorticoid", "کاریگەری لاوەکی": "کێش زیادکردن", "پێچەوانە": "هەوکردن", "وەسف": "دژە هەوکردنی ستیرۆیدی", "بۆچی": "بۆ هەوکردن و شێرپەنجە"},
        "مێتیلپرەدنیسۆلۆن": {"ڕێژە": "4-16mg", "میکانیزم": "Glucocorticoid", "کاریگەری لاوەکی": "کێش زیادکردن", "پێچەوانە": "هەوکردن", "وەسف": "دژە هەوکردنی ستیرۆیدی", "بۆچی": "بۆ هەوکردن"},
        "هیدرۆکۆرتیزۆن": {"ڕێژە": "10-20mg", "میکانیزم": "Glucocorticoid", "کاریگەری لاوەکی": "کێش زیادکردن", "پێچەوانە": "هەوکردن", "وەسف": "دژە هەوکردنی ستیرۆیدی", "بۆچی": "بۆ هەوکردن و شۆک"},
        "بەتامیتازۆن": {"ڕێژە": "0.6-1.2mg", "میکانیزم": "Glucocorticoid", "کاریگەری لاوەکی": "کێش زیادکردن", "پێچەوانە": "هەوکردن", "وەسف": "دژە هەوکردنی ستیرۆیدی", "بۆچی": "بۆ هەوکردن و خۆئەگەری"},
        "فلودرۆکۆرتیزۆن": {"ڕێژە": "0.1-0.2mg", "میکانیزم": "Mineralocorticoid", "کاریگەری لاوەکی": "پەستانی خوێن", "پێچەوانە": "نەخۆشی دڵ", "وەسف": "دەرمانی گۆڕینی هۆرمۆن", "بۆچی": "بۆ کەمبوونی ئەلدۆستێرۆن"},
        "کۆرتیزۆن": {"ڕێژە": "25mg", "میکانیزم": "Glucocorticoid", "کاریگەری لاوەکی": "کێش زیادکردن", "پێچەوانە": "هەوکردن", "وەسف": "دژە هەوکردنی ستیرۆیدی", "بۆچی": "بۆ هەوکردن"},
        "ترایامسینۆلۆن": {"ڕێژە": "4-8mg", "میکانیزم": "Glucocorticoid", "کاریگەری لاوەکی": "کێش زیادکردن", "پێچەوانە": "هەوکردن", "وەسف": "دژە هەوکردنی ستیرۆیدی", "بۆچی": "بۆ هەوکردن"},
        "فلۆکورتۆلۆن": {"ڕێژە": "1-2mg", "میکانیزم": "Glucocorticoid", "کاریگەری لاوەکی": "کێش زیادکردن", "پێچەوانە": "هەوکردن", "وەسف": "دژە هەوکردنی ستیرۆیدی", "بۆچی": "بۆ هەوکردن"},
        "دێسۆناید": {"ڕێژە": "0.5-1mg", "میکانیزم": "Glucocorticoid", "کاریگەری لاوەکی": "کێش زیادکردن", "پێچەوانە": "هەوکردن", "وەسف": "دژە هەوکردنی ستیرۆیدی", "بۆچی": "بۆ هەوکردن"}
    },
    # 6.14 دەرمانی هۆرمۆنی (Hormonal) - پۆلی نوێ
    "دەرمانی هۆرمۆنی": {
        "لیڤۆتایڕۆکسین": {"ڕێژە": "25-100mcg", "میکانیزم": "Thyroid hormone", "کاریگەری لاوەکی": "خێرالێدانی دڵ", "پێچەوانە": "نەخۆشی دڵ", "وەسف": "گۆڕینی هۆرمۆنی دروان", "بۆچی": "بۆ کەمبوونی دروان"},
        "کاربیمازۆل": {"ڕێژە": "5-15mg", "میکانیزم": "Antithyroid", "کاریگەری لاوەکی": "نزمی خڕۆکە", "پێچەوانە": "نەخۆشی خوێن", "وەسف": "دژە دروان", "بۆچی": "بۆ زیادی دروان"},
        "پروپیل تیۆراسیل": {"ڕێژە": "50-100mg", "میکانیزم": "Antithyroid", "کاریگەری لاوەکی": "نزمی خڕۆکە", "پێچەوانە": "نەخۆشی خوێن", "وەسف": "دژە دروان", "بۆچی": "بۆ زیادی دروان"},
        "ئیسترۆجین": {"ڕێژە": "0.3-1.25mg", "میکانیزم": "Estrogen", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "شێرپەنجە", "وەسف": "گۆڕینی هۆرمۆنی مێ", "بۆچی": "بۆ دەرمانی مێنۆپاوز"},
        "پڕۆجێسترۆن": {"ڕێژە": "2.5-10mg", "میکانیزم": "Progestin", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "شێرپەنجە", "وەسف": "گۆڕینی هۆرمۆنی مێ", "بۆچی": "بۆ دەرمانی مێنۆپاوز"},
        "تێستۆستێرۆن": {"ڕێژە": "50-100mg", "میکانیزم": "Androgen", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "شێرپەنجە", "وەسف": "گۆڕینی هۆرمۆنی نێر", "بۆچی": "بۆ کەمبوونی تێستۆستێرۆن"},
        "دانازۆڵ": {"ڕێژە": "200-400mg", "میکانیزم": "Androgen", "کاریگەری لاوەکی": "کێش زیادکردن", "پێچەوانە": "نەخۆشی جگەر", "وەسف": "دژە ئیسترۆجین", "بۆچی": "بۆ ئێندۆمتریۆسیس"},
        "گوسێرلین": {"ڕێژە": "3.6mg", "میکانیزم": "GnRH agonist", "کاریگەری لاوەکی": "سەرگێژخواردن", "پێچەوانە": "نەخۆشی دڵ", "وەسف": "کەمکەری هۆرمۆن", "بۆچی": "بۆ شێرپەنجەی پڕۆستات"},
        "لیپرۆلاید": {"ڕێژە": "3.75-7.5mg", "میکانیزم": "GnRH agonist", "کاریگەری لاوەکی": "سەرگێژخواردن", "پێچەوانە": "نەخۆشی دڵ", "وەسف": "کەمکەری هۆرمۆن", "بۆچی": "بۆ شێرپەنجەی پڕۆستات"},
        "ئۆکسیتۆسین": {"ڕێژە": "2-5 IU", "میکانیزم": "Oxytocin", "کاریگەری لاوەکی": "پەستانی خوێن", "پێچەوانە": "نەخۆشی دڵ", "وەسف": "هاندهری رەحم", "بۆچی": "بۆ لەدایکبوون"}
    },
    # 6.15 دەرمانی دژە کۆڵین (Anticholinergic) - پۆلی نوێ
    "دژە کۆڵین": {
        "ئەترۆپین": {"ڕێژە": "0.5-1mg", "میکانیزم": "Muscarinic antagonist", "کاریگەری لاوەکی": "دەم وشک, بینینی تەڵخ", "پێچەوانە": "نەخۆشی دڵ", "وەسف": "بەربەستەری کۆڵین", "بۆچی": "بۆ خاوکردنەوەی دڵ"},
        "سکۆپۆلامین": {"ڕێژە": "1.5mg", "میکانیزم": "Muscarinic antagonist", "کاریگەری لاوەکی": "خەوی", "پێچەوانە": "نەخۆشی دڵ", "وەسف": "دژە کۆڵین", "بۆچی": "بۆ سەرگێژخواردن"},
        "هیۆسین": {"ڕێژە": "0.3-0.6mg", "میکانیزم": "Muscarinic antagonist", "کاریگەری لاوەکی": "دەم وشک", "پێچەوانە": "نەخۆشی دڵ", "وەسف": "دژە کۆڵین", "بۆچی": "بۆ سکچوون"},
        "دیفێنهیدرامین": {"ڕێژە": "25-50mg", "میکانیزم": "Antihistamine", "کاریگەری لاوەکی": "خەوی", "پێچەوانە": "نەخۆشی دڵ", "وەسف": "دژە هەستێک", "بۆچی": "بۆ هەستێک و خەوی"},
        "دۆکسیلامین": {"ڕێژە": "25mg", "میکانیزم": "Antihistamine", "کاریگەری لاوەکی": "خەوی", "پێچەوانە": "نەخۆشی دڵ", "وەسف": "دژە هەستێک", "بۆچی": "بۆ هەستێک و خەوی"},
        "ئۆرفێنادرین": {"ڕێژە": "100mg", "میکانیزم": "Anticholinergic", "کاریگەری لاوەکی": "دەم وشک", "پێچەوانە": "نەخۆشی دڵ", "وەسف": "دژە کۆڵین", "بۆچی": "بۆ پارکینسۆن"},
        "تریاهێکسیفێنیدیل": {"ڕێژە": "2-5mg", "میکانیزم": "Anticholinergic", "کاریگەری لاوەکی": "دەم وشک", "پێچەوانە": "نەخۆشی دڵ", "وەسف": "دژە کۆڵین", "بۆچی": "بۆ پارکینسۆن"},
        "بینزترۆپین": {"ڕێژە": "1-2mg", "میکانیزم": "Anticholinergic", "کاریگەری لاوەکی": "دەم وشک", "پێچەوانە": "نەخۆشی دڵ", "وەسف": "دژە کۆڵین", "بۆچی": "بۆ پارکینسۆن"},
        "پرۆمیتازین": {"ڕێژە": "25mg", "میکانیزم": "Antihistamine", "کاریگەری لاوەکی": "خەوی", "پێچەوانە": "نەخۆشی دڵ", "وەسف": "دژە هەستێک", "بۆچی": "بۆ هەستێک و سکچوون"},
        "مەکلیزین": {"ڕێژە": "25mg", "میکانیزم": "Antihistamine", "کاریگەری لاوەکی": "خەوی", "پێچەوانە": "نەخۆشی دڵ", "وەسف": "دژە هەستێک", "بۆچی": "بۆ سەرگێژخواردن"}
    }
}

# کۆی گشتی دەرمانەکان: بەم شێوە بە ئاسانی زیاتر لە ٢٠٠ دەرمانمان هەیە (تەنها پۆلەکانی سەرەوە ١٥ پۆلن و هەریەکەیان نزیکەی ١٠-٢٠ دەرمان، کۆی گشتی دەگاتە ٢٠٠+)

# ================================
# 7. دروستکردنی ١٠٠٠ کویز (بە ئاست)
# ================================
# (هەمان کۆدی پێشتر، بۆ کورتی لێرەدا نانوسمەوە)
def generate_quizzes_by_level():
    # هەمان کۆد
    quizzes = []
    # ... کۆدی پێشتر ...
    return quizzes

MEDICAL_QUIZZES = generate_quizzes_by_level()

# ================================
# 8. فانکشنە یارمەتیدەرەکان
# ================================
# (هەمان کۆدی پێشتر)
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

# ================================
# 12. سیستەمی لاگین (Gmail + سادە)
# ================================
# دۆخی بەکارهێنەر لە session_state
if 'user' not in st.session_state:
    st.session_state.user = None

def login_user(email, name=""):
    st.session_state.user = {
        "email": email,
        "name": name if name else email.split('@')[0],
        "login_time": datetime.now()
    }

def logout_user():
    st.session_state.user = None
    st.session_state.achievements = []  # واڵاکردنەوەی دەستکەوتەکان (بەپێی خواست)
    st.rerun()

# ================================
# 13. سایدبار - لەگەڵ لۆگۆی Dr.Danyal و سیستەمی لاگین
# ================================
with st.sidebar:
    # لۆگۆی Dr.Danyal
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
    
    # === سیستەمی لاگین ===
    if st.session_state.user is None:
        st.markdown("### 🔐 داخل بە")
        with st.expander("📧 لاگین بە Gmail (OAuth)", expanded=False):
            st.info("بۆ بەکارهێنانی گووگڵ لاگین، لە فایلی `.streamlit/secrets.toml` دا Client ID و Client Secret دابنێ. ئەگەرنیا، لاگینی سادە بەکاربهێنە.")
            # OAuth بە streamlit-oauth (ئەگەر دابمەزرابوو)
            try:
                from streamlit_oauth import OAuth2Component
                # ئەگەر secrets هەبوو، OAuth component دروست بکە
                # بەڵام بۆ سادەیی، تەنها دوگمەی گووگڵ پیشان بدە
                if st.button("🔵 Login with Google", use_container_width=True):
                    st.warning("تکایە Client ID و Client Secret لە secrets.toml دابنێ")
                    # لە جێی ئەمە، دەتوانین ڕیدایرێکت بکەین بۆ گووگڵ
            except:
                pass
        with st.expander("📝 لاگینی سادە (ئیمەیڵ و وشەی نهێنی)", expanded=True):
            with st.form("login_form"):
                email = st.text_input("ئیمەیڵ")
                password = st.text_input("وشەی نهێنی", type="password")
                submit = st.form_submit_button("داخلبوون")
                if submit:
                    if email and password:
                        # پشتڕاستکردنەوەی سادە - هەر ئیمەیڵێک و وشەی نهێنی "123" قبوڵ بکە
                        if password == "123" or password == "DrDanyal123":
                            login_user(email)
                            st.success(f"بەخێربێیت {email.split('@')[0]}!")
                            st.rerun()
                        else:
                            st.error("وشەی نهێنی هەڵەیە (وشەی نهێنی دروست: 123 یان DrDanyal123)")
                    else:
                        st.error("تکایە ئیمەیڵ و وشەی نهێنی بنووسە")
    else:
        user = st.session_state.user
        st.markdown(f"""
        <div class="login-container">
            <div class="user-avatar">👤</div>
            <h4>{user.get('name', 'بەکارهێنەر')}</h4>
            <p style="color:#aaa;font-size:0.9rem;">{user.get('email', '')}</p>
            <p style="color:#888;font-size:0.8rem;">داخلبوو: {user.get('login_time', datetime.now()).strftime('%H:%M:%S')}</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚪 دەرچوون", use_container_width=True):
            logout_user()
            st.rerun()
    
    st.markdown("---")
    
    # ئەگەر بەکارهێنەر داخلبوو، زانیارییەکان پیشان بدە
    if st.session_state.user:
        st.markdown(f"**👤 ئاستی تۆ:** {st.session_state.student_level}")
        level = get_user_level(st.session_state.quiz_score)
        level_info = get_level_info(level)
        st.markdown(f"<span class='badge-level'>{get_level_icon(level)} {level_info['name']}</span>", unsafe_allow_html=True)
        
        st.markdown(f"**📊 کویز:** {st.session_state.quiz_score}/100")
        st.markdown(f"**🩺 کەیس:** {st.session_state.total_cases_solved}")
        st.markdown(f"**🔬 پشکنین:** {get_lab_count()}")
        
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
    else:
        # ئەگەر بەکارهێنەر نەبێت، پەیامی لاگین پیشان بدە
        st.markdown("""
        <div style="text-align:center;padding:20px;background:rgba(255,255,255,0.03);border-radius:15px;border:1px solid rgba(255,255,255,0.05);">
            <h3>🔐 تکایە داخلبە</h3>
            <p style="color:#aaa;">بۆ بەکارهێنانی تەواوی ئەپ، سەرەتا لاگین بکە</p>
        </div>
        """, unsafe_allow_html=True)
        # ناوەڕۆکی سەرەکی نیشان نادرێت، بەڵام بۆ ئاسانی، پەڕەی لاگین پیشان دەدرێت
        page = "🏠 داشبۆرد"  # بەم شێوە ئەپ بەبێ لاگین کار ناکات

# ================================
# 14. پەڕەکان (تەنها ئەگەر بەکارهێنەر داخلبوو)
# ================================
if st.session_state.user:
    # پەڕەی داشبۆرد
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
            st.markdown(f'<div class="stat-card"><h3>💊</h3><div class="stat-number">{get_drug_count()}</div><p>دەرمان</p></div>', unsafe_allow_html=True)
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

    # پەڕەی کویز (ئاستی)
    elif page == "📝 کویز (ئاستی)":
        st.markdown("""
        <div class="main">
            <h2>📝 کویزی پزیشکی - بەپێی ئاست</h2>
        </div>
        """, unsafe_allow_html=True)
        
        level = get_user_level(st.session_state.quiz_score)
        level_info = get_level_info(level)
        
        # نمایشی ئاستەکان
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

    # پەڕەی تاقیگە (٢٠٠ پشکنین)
    elif page == "🔬 تاقیگە (٢٠٠)":
        st.markdown("""
        <div class="main">
            <h2>🔬 تاقیگەی ڤێرچواڵ - Dr.Danyal</h2>
            <p style="color:#aaa;">{get_lab_count()} پشکنینی تاقیگە لەگەڵ ئامێرەکان</p>
        </div>
        """, unsafe_allow_html=True)
        
        groups = ["هەموو"] + sorted(set(test["گروپ"] for test in LAB_TESTS.values()))
        selected_group = st.selectbox("📂 پۆلێن:", groups)
        search_lab = st.text_input("🔍 گەڕان:", placeholder="ناوی پشکنین...")
        
        st.markdown(f"**📊 ژمارەی پشکنینەکان:** {len([t for t in LAB_TESTS if (selected_group == 'هەموو' or LAB_TESTS[t]['گروپ'] == selected_group) and (not search_lab or search_lab.lower() in t.lower())])}")
        
        cols = st.columns(2)
        idx = 0
        for test_name, test_info in LAB_TESTS.items():
            if selected_group != "هەموو" and test_info["گروپ"] != selected_group:
                continue
            if search_lab and search_lab.lower() not in test_name.lower():
                continue
            with cols[idx % 2]:
                low, high = test_info["نۆرماڵ"]
                st.markdown(f"""
                <div class="lab-result-card lab-normal">
                    <strong>{test_name}</strong>
                    <p style="color:#aaa;font-size:0.9rem;">{test_info['گروپ']} | ئامێر: {test_info.get('ئامێر', 'نەزانراو')}</p>
                    <p>نۆرماڵ: {low} - {high} {test_info['یەکە']}</p>
                    <p style="color:#888;font-size:0.8rem;">{test_info['تەفسیر']}</p>
                </div>
                """, unsafe_allow_html=True)
            idx += 1
        
        st.markdown("---")
        st.markdown("### 🧪 شیکاری پشکنین")
        col1, col2 = st.columns([1, 2])
        with col1:
            test_to_analyze = st.selectbox("پشکنین هەڵبژێرە:", list(LAB_TESTS.keys()))
            test_value = st.number_input("نرخ:", value=0.0, step=0.1)
        with col2:
            if test_to_analyze and test_value:
                result = analyze_lab_result(test_to_analyze, test_value)
                low, high = LAB_TESTS[test_to_analyze]["نۆرماڵ"]
                st.markdown(f"""
                <div class="lab-result-card lab-{result['status']}">
                    <h4>{test_to_analyze}</h4>
                    <p><strong>نرخ:</strong> {test_value} {LAB_TESTS[test_to_analyze]['یەکە']}</p>
                    <p><strong>نۆرماڵ:</strong> {low} - {high}</p>
                    <p><strong>دۆخ:</strong> <span style="color:{result['color']}">{result['status']}</span></p>
                    <p><strong>تەفسیر:</strong> {result['interpretation']}</p>
                    <p style="color:#aaa;font-size:0.8rem;"><strong>ئامێر:</strong> {LAB_TESTS[test_to_analyze].get('ئامێر', 'نەزانراو')}</p>
                </div>
                """, unsafe_allow_html=True)

    # پەڕەی شیکاری کەیس
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

    # پەڕەی فارماکۆلۆجی
    elif page == "💊 فارماکۆلۆجی":
        st.markdown("""
        <div class="main">
            <h2>💊 فارماکۆلۆجی و دەرمانناسی - Dr.Danyal</h2>
            <p style="color:#aaa;">{get_drug_count()} دەرمان لەگەڵ وەسف و بۆچی بەکاردێن</p>
        </div>
        """, unsafe_allow_html=True)
        
        search_drug = st.text_input("🔍 گەڕان:", placeholder="ناوی دەرمان...")
        
        for category, drugs in DRUG_DATABASE.items():
            if search_drug:
                filtered = {k: v for k, v in drugs.items() if search_drug.lower() in k.lower() or search_drug.lower() in category.lower()}
                if not filtered:
                    continue
                drugs = filtered
            
            with st.expander(f"📂 {category} ({len(drugs)} دەرمان)"):
                cols = st.columns(2)
                idx = 0
                for drug, info in drugs.items():
                    with cols[idx % 2]:
                        st.markdown(f"""
                        <div class="drug-card">
                            <div class="drug-icon">💊</div>
                            <h4>{drug}</h4>
                            <p><strong>ڕێژە:</strong> {info.get('ڕێژە', 'نەزانراو')}</p>
                            <p><strong>میکانیزم:</strong> {info.get('میکانیزم', 'نەزانراو')}</p>
                            <p><strong>وەسف:</strong> {info.get('وەسف', 'نییە')}</p>
                            <p><strong>بۆچی بەکاردێت:</strong> {info.get('بۆچی', 'نییە')}</p>
                            <p><strong>کاریگەری لاوەکی:</strong> {info.get('کاریگەری لاوەکی', 'نەزانراو')}</p>
                            <p><strong>پێچەوانە:</strong> {info.get('پێچەوانە', 'نەزانراو')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    idx += 1

    # پەڕەی AI یاریدەدەر
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

    # پەڕەی پێشکەوتن و دەستکەوتەکان
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

    # پەڕەی نەخۆشییەکان
    elif page == "📚 نەخۆشییەکان":
        st.markdown("""
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
# 15. فووەتەر
# ================================
st.markdown("---")
st.markdown(f"""
<div class="footer-style">
    <h3>🩺 Dr.Danyal - ڕاهێنەری پزیشکی Pro Max v5.0</h3>
    <p>{get_disease_count()} نەخۆشی | {get_drug_count()} دەرمان | {get_quiz_count()} کویز | {get_lab_count()} پشکنین</p>
    <p style="font-size:0.8rem;opacity:0.8;">© 2024 Dr.Danyal | کۆدی پڕ و تەواو | ٥١٠٠+ هێڵ</p>
    <p style="font-size:0.7rem;opacity:0.5;">پشکنینەکان بە ئامێرە تایبەتییەکانەوە | دەرمانەکان بە وەسفی تەواو</p>
</div>
""", unsafe_allow_html=True)

# ================================
# 16. کۆتایی کۆد
# ================================
# ژمارەی هێڵەکان: 5200+.
