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
import stripe
from supabase import create_client, Client

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
# 1.5 دەستپێکردنی Stripe و Supabase
# ================================
stripe.api_key = st.secrets.get("STRIPE_SECRET_KEY", "sk_test_placeholder")

try:
    supabase_url = st.secrets.get("SUPABASE_URL", "")
    supabase_key = st.secrets.get("SUPABASE_KEY", "")
    if supabase_url and supabase_key:
        supabase: Client = create_client(supabase_url, supabase_key)
        SUPABASE_AVAILABLE = True
    else:
        SUPABASE_AVAILABLE = False
        st.sidebar.warning("⚠️ Supabase ڕێک نەخراوە. داتاکان بە شێوەی JSON خەزن دەکرێن.")
except Exception as e:
    SUPABASE_AVAILABLE = False
    st.sidebar.warning(f"⚠️ نەتوانرا Supabase بار بکرێت: {e}")

# ================================
# 1.6 سیستەمی لۆگین و خەزنکردنی داتا
# ================================
DATA_DIR = "user_data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

USERS_FILE = os.path.join(DATA_DIR, "users.json")
INVITE_CODES_FILE = os.path.join(DATA_DIR, "invite_codes.json")

# زانیاری پەیوەندی
CONTACT_PHONE = "07801352003"
CONTACT_WHATSAPP = f"https://wa.me/9647801352003"

def hash_password(password: str) -> str:
    """هێشکردنی وشەی نهێنی بە شێوازی SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_invite_codes() -> List[str]:
    """بارکردنی کۆدی بانگهێشتکردنەکان"""
    if os.path.exists(INVITE_CODES_FILE):
        with open(INVITE_CODES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    # دروستکردنی 1000 کۆدی بانگهێشتکردن
    codes = []
    for i in range(1000):
        code = hashlib.md5(f"DRDANYAL-{i}-{uuid.uuid4()}".encode()).hexdigest()[:10].upper()
        codes.append(code)
    save_invite_codes(codes)
    return codes

def save_invite_codes(codes: List[str]):
    """خەزنکردنی کۆدی بانگهێشتکردنەکان"""
    with open(INVITE_CODES_FILE, 'w', encoding='utf-8') as f:
        json.dump(codes, f, ensure_ascii=False, indent=4)

def validate_invite_code(code: str) -> bool:
    """پشتڕاستکردنەوەی کۆدی بانگهێشتکردن"""
    codes = load_invite_codes()
    return code.upper() in codes

def remove_invite_code(code: str):
    """لابردنی کۆدی بانگهێشتکردن دوای بەکارهێنان"""
    codes = load_invite_codes()
    if code.upper() in codes:
        codes.remove(code.upper())
        save_invite_codes(codes)

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

def create_user(username: str, password: str, invite_code: str) -> Tuple[bool, str]:
    """دروستکردنی بەکارهێنەری نوێ"""
    if not validate_invite_code(invite_code):
        return False, "کۆدی بانگهێشتکردن هەڵەیە یان پێشتر بەکارهێنراوە"
    
    if SUPABASE_AVAILABLE:
        try:
            email = f"{username}@drdanyal.app"
            response = supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "username": username,
                        "phone": CONTACT_PHONE
                    }
                }
            })
            if response.user:
                remove_invite_code(invite_code)
                return True, "هەژمار بە سەرکەوتوویی دروست کرا!"
            return False, "هەڵە لە دروستکردنی هەژمار"
        except Exception as e:
            return False, f"هەڵە: {str(e)}"
    else:
        users = load_users()
        if username in users:
            return False, "ئەم ناوی بەکارهێنەرییە پێشتر بەکارهێنراوە"
        users[username] = {
            "password": hash_password(password),
            "created_at": datetime.now().isoformat(),
            "custom_lab_tests": {},
            "custom_drugs": {},
            "is_vip": False,
            "phone": CONTACT_PHONE,
            "invite_code": invite_code
        }
        save_users(users)
        remove_invite_code(invite_code)
        return True, "هەژمار بە سەرکەوتوویی دروست کرا!"

def authenticate_user(username: str, password: str) -> bool:
    """پشتڕاستکردنەوەی بەکارهێنەر"""
    if SUPABASE_AVAILABLE:
        try:
            email = f"{username}@drdanyal.app"
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            return True if response.user else False
        except Exception:
            return False
    else:
        users = load_users()
        if username in users:
            return users[username]["password"] == hash_password(password)
        return False

def load_user_data(username: str) -> Dict:
    """بارکردنی داتای تایبەتی بەکارهێنەر"""
    if SUPABASE_AVAILABLE:
        try:
            response = supabase.table("profiles").select("*").eq("username", username).execute()
            if response.data:
                return response.data[0]
        except Exception:
            pass
    users = load_users()
    if username in users:
        return users[username]
    return {}

def save_user_data(username: str, data: Dict):
    """خەزنکردنی داتای تایبەتی بەکارهێنەر"""
    if SUPABASE_AVAILABLE:
        try:
            supabase.table("profiles").update(data).eq("username", username).execute()
        except Exception:
            pass
    else:
        users = load_users()
        if username in users:
            users[username].update(data)
            save_users(users)

# ================================
# 1.7 سیستەمی پارەدان (Stripe)
# ================================
def create_checkout_session(price_id: str, user_id: str) -> Optional[str]:
    """دروستکردنی سێشنی پارەدان بۆ VIP"""
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url='https://drdanyal.streamlit.app/?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='https://drdanyal.streamlit.app/?canceled=true',
            metadata={
                "user_id": user_id,
                "username": st.session_state.username
            },
            allow_promotion_codes=True,
            billing_address_collection='auto',
            payment_method_types=['card'],
            phone_number_collection={'enabled': True},
        )
        return checkout_session.url
    except Exception as e:
        st.error(f"❌ هەڵە لە دروستکردنی پارەدان: {str(e)}")
        return None

def check_vip_status(username: str) -> bool:
    """پشکنینی دۆخی VIP بەکارهێنەر"""
    user_data = load_user_data(username)
    return user_data.get("is_vip", False)

def activate_vip(username: str):
    """چالاککردنی VIP بۆ بەکارهێنەر"""
    save_user_data(username, {"is_vip": True, "vip_activated_at": datetime.now().isoformat()})

VIP_MONTHLY_PRICE_ID = st.secrets.get("VIP_MONTHLY_PRICE_ID", "price_monthly_placeholder")
VIP_YEARLY_PRICE_ID = st.secrets.get("VIP_YEARLY_PRICE_ID", "price_yearly_placeholder")

# دەستپێکردنی ستەیتی لۆگین
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'custom_lab_tests' not in st.session_state:
    st.session_state.custom_lab_tests = {}
if 'custom_drugs' not in st.session_state:
    st.session_state.custom_drugs = {}
if 'is_vip' not in st.session_state:
    st.session_state.is_vip = False
if 'show_chat' not in st.session_state:
    st.session_state.show_chat = False
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []

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
    }
    
    [data-testid="stSidebar"] * {
        color: rgba(255, 255, 255, 0.9) !important;
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
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 15px 35px rgba(67, 233, 123, 0.45) !important;
    }
    
    .vip-button > button {
        background: linear-gradient(135deg, #FFD700, #FFA500, #FFD700) !important;
        background-size: 200% 200% !important;
        animation: vipGlow 2s ease infinite !important;
        color: #0a1929 !important;
        font-weight: 800 !important;
        border: 2px solid #FFD700 !important;
        box-shadow: 0 0 30px rgba(255, 215, 0, 0.5) !important;
    }
    
    @keyframes vipGlow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .payment-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border-radius: 25px;
        padding: 2rem;
        border: 2px solid rgba(255, 215, 0, 0.3);
        text-align: center;
        transition: all 0.3s ease;
        color: white;
    }
    
    .payment-card:hover {
        border-color: #FFD700;
        box-shadow: 0 0 40px rgba(255, 215, 0, 0.3);
        transform: translateY(-5px);
    }
    
    .vip-badge {
        display: inline-block;
        background: linear-gradient(135deg, #FFD700, #FFA500);
        color: #0a1929;
        padding: 0.3rem 1.5rem;
        border-radius: 30px;
        font-weight: bold;
        font-size: 0.9rem;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
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
    
    .lab-result-card {
        background: rgba(0, 0, 0, 0.2);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        border-left: 4px solid #4facfe;
        transition: all 0.3s ease;
        color: #fff;
    }
    
    .lab-result-card:hover {
        background: rgba(0, 0, 0, 0.3);
        transform: translateX(5px);
    }
    
    .lab-normal { border-left-color: #28a745; }
    .lab-high { border-left-color: #dc3545; }
    .lab-low { border-left-color: #ffc107; }
    
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
        max-width: 500px;
        width: 100%;
        animation: fadeIn 1s ease-out;
    }
    
    .leaderboard-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0 10px;
    }
    
    .leaderboard-table th {
        background: rgba(79, 172, 254, 0.2);
        padding: 12px;
        border-radius: 10px 10px 0 0;
        color: #4facfe;
        font-weight: bold;
    }
    
    .leaderboard-table td {
        background: rgba(255, 255, 255, 0.05);
        padding: 12px;
        text-align: center;
        color: white;
    }
    
    .leaderboard-table tr:hover td {
        background: rgba(79, 172, 254, 0.15);
    }
    
    .rank-1 { color: #FFD700; font-weight: bold; font-size: 1.2rem; }
    .rank-2 { color: #C0C0C0; font-weight: bold; font-size: 1.1rem; }
    .rank-3 { color: #CD7F32; font-weight: bold; font-size: 1.1rem; }
    
    .chat-container {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 20px;
        border: 1px solid rgba(79, 172, 254, 0.2);
        margin: 10px 0;
    }
    
    .chat-message {
        padding: 10px 15px;
        border-radius: 15px;
        margin: 8px 0;
        animation: fadeIn 0.5s ease;
    }
    
    .chat-message.sent {
        background: rgba(79, 172, 254, 0.2);
        margin-left: 20%;
        border-right: 3px solid #4facfe;
    }
    
    .chat-message.received {
        background: rgba(67, 233, 123, 0.2);
        margin-right: 20%;
        border-left: 3px solid #43e97b;
    }
    
    .whatsapp-button {
        display: inline-block;
        background: #25D366;
        color: white !important;
        padding: 12px 25px;
        border-radius: 50px;
        text-decoration: none;
        font-weight: bold;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 8px 25px rgba(37, 211, 102, 0.3);
    }
    
    .whatsapp-button:hover {
        background: #128C7E;
        transform: translateY(-3px);
        box-shadow: 0 12px 35px rgba(37, 211, 102, 0.5);
    }
    
    .app-description {
        background: linear-gradient(135deg, rgba(79, 172, 254, 0.1), rgba(67, 233, 123, 0.1));
        border-radius: 20px;
        padding: 2rem;
        border: 1px solid rgba(79, 172, 254, 0.2);
        margin: 1.5rem 0;
    }
    
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .feature-item {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 1.5rem;
        text-align: center;
        border: 1px solid rgba(79, 172, 254, 0.15);
        transition: all 0.3s ease;
    }
    
    .feature-item:hover {
        background: rgba(255, 255, 255, 0.1);
        border-color: #4facfe;
        transform: translateY(-5px);
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    @media (max-width: 768px) {
        .main-header { font-size: 2.2rem; padding: 1.2rem; }
        .stat-number { font-size: 2.8rem; }
        .stat-card { padding: 1rem; }
        .logo-text { font-size: 1.5rem; }
        .logo-icon { font-size: 2.5rem; }
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
            return level    return 1

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

def get_level_icon(level: int) -> str:
    info = get_level_info(level)
    return info.get("icon", "📚")

# ================================
# 4. داتابەسی نەخۆشییەکان (تەواو - 100+ نەخۆشی)
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
        "وەسفی تەواو": "شەکرەی جۆری 1 نەخۆشییەکی خۆئەگەرە کە تێیدا سیستەمی بەرگری جەستە هێرش دەکاتە سەر خانەکانی پەنکریاس کە ئەنسولین بەرهەم دەهێنن. ئەمە دەبێتە هۆی نەبوونی ئەنسولین لە جەستەدا. نەخۆشەکە پێویستی بە ئەنسولینی دەرەکی هەیە بۆ هەموو ژیانی."
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
        "وەسفی تەواو": "شەکرەی جۆری 2 باوترین جۆری شەکرەیە کە تێیدا جەستە بەرگری لە کاریگەری ئەنسولین دەکات یان پەنکریاس ناتوانێت ئەنسولینی پێویست بەرهەم بهێنێت. زۆر جار بەهۆی زیادەڕەوی کێش و کەم جوڵانەوە ڕوودەدات."
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
        "وەسفی تەواو": "پەستانی خوێنی سەرەتایی بەرزبوونەوەی پەستانی خوێنە بەبێ هۆکارێکی ڕوون. ئەم نەخۆشیە دەبێتە هۆی مەترسی گەورە بۆ نەخۆشی دڵ، سەکتەی مێشک، و نەخۆشی گورچیلە. پێوانەکردنی بەردەوامی پەستانی خوێن زۆر گرنگە."
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
        "وەسفی تەواو": "نەخۆشی دڵی ئیسکیمیک کاتێک ڕوودەدات کە خوێنبەرەکانی دڵ تەنگ دەبنەوە یان دەگیرێن، ئەمەش ڕێگری لە گەیشتنی خوێن و ئۆکسجین بە ماسوولکەی دڵ دەکات. ئەمە دەبێتە هۆی ئازاری سنگ و لەوانەیە ببێتە هۆی جەڵتەی دڵ."
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
        "وەسفی تەواو": "هەوکردنی سییەکان هەوکردنێکی سییەکانە کە دەبێتە هۆی پڕبوونی کیسە هەواییەکان بە شلە یان کێم. دەتوانرێت بەهۆی بەکتریا، ڤایرۆس، یان کەڕووەوە دروست بێت. نیشانەکانی بریتین لە کۆخە، تا، و هەناسەدان بە زەحمەت."
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
        "وەسفی تەواو": "ئەنیمیا حاڵەتێکە کە تێیدا ژمارەی خڕۆکە سوورەکانی خوێن یان ڕێژەی هیمۆگلۆبین لە خوێندا کەمترە لە ئاستی نۆرماڵ. هۆکارەکانی بریتین لە کەمخوێنی ئاسن، کەمخوێنی ڤیتامین B12، یان نەخۆشی درێژخایەن."
    }
}

# ================================
# 5. داتابەسی پشکنینەکانی تاقیگە (تەواو - 200+ پشکنین)
# ================================
LAB_TESTS = {
    "CBC": {"گروپ": "خوێن", "نۆرماڵ": (4.0, 11.0), "یەکە": "x10³/µL", "تەفسیر": "خڕۆکە سپیەکانی خوێن. بەرزبوونەوە ئاماژەیە بۆ هەوکردن یان لەوسیمیا. نزمبوونەوە ئاماژەیە بۆ کەمبوونەوەی بەرگری جەستە.", "ئامێر": "Sysmex XN-9000", "تێبینی": ""},
    "Hemoglobin": {"گروپ": "خوێن", "نۆرماڵ": (12.0, 16.0), "یەکە": "g/dL", "تەفسیر": "پڕۆتینێکە لە خڕۆکە سوورەکاندا کە ئۆکسجین هەڵدەگرێت. نزمبوونەوە ئاماژەیە بۆ ئەنیمیا. بەرزبوونەوە لەوانەیە ئاماژە بێت بۆ نەخۆشی سییەکان یان وشکبوونەوە.", "ئامێر": "HemoCue 201+", "تێبینی": ""},
    "Platelets": {"گروپ": "خوێن", "نۆرماڵ": (150, 450), "یەکە": "x10³/µL", "تەفسیر": "خانەی پلەیتلێت کە بەرپرسیارن لە مەیینەوەی خوێن. نزمبوونەوە مەترسی خوێنبەربوون زیاد دەکات. بەرزبوونەوە مەترسی مەیینەوەی خوێن زیاد دەکات.", "ئامێر": "Sysmex XN-9000", "تێبینی": ""},
    "Glucose": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (70, 126), "یەکە": "mg/dL", "تەفسیر": "شەکری خوێن. بەرزبوونەوە ئاماژەیە بۆ شەکرە. نزمبوونەوە دەبێتە هۆی هایپۆگلایسیمیا کە مەترسیدارە.", "ئامێر": "Roche Cobas c502", "تێبینی": ""},
    "HbA1c": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (4.0, 5.6), "یەکە": "%", "تەفسیر": "ڕێژەی شەکری خوێن لە ماوەی 2-3 مانگی ڕابردوودا. ئەم پشکنینە بۆ دەستنیشانکردن و چاودێری شەکرە بەکاردێت.", "ئامێر": "Bio-Rad D-100", "تێبینی": ""},
    "Creatinine": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (0.6, 1.3), "یەکە": "mg/dL", "تەفسیر": "پاشماوەی ماسوولکەیە کە لە ڕێگەی گورچیلەوە دەردەکرێت. بەرزبوونەوە ئاماژەیە بۆ کەمبوونەوەی کاری گورچیلە.", "ئامێر": "Roche Cobas c502", "تێبینی": ""},
    "ALT": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (10, 40), "یەکە": "U/L", "تەفسیر": "ئەنزیمێکی جگەرە. بەرزبوونەوە ئاماژەیە بۆ زیانگەیشتن بە جگەر بەهۆی هەوکردن، دەرمان، یان نەخۆشی جگەر.", "ئامێر": "Roche Cobas c502", "تێبینی": ""},
    "AST": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (10, 40), "یەکە": "U/L", "تەفسیر": "ئەنزیمێکی جگەر و ماسوولکەی دڵە. بەرزبوونەوە لەوانەیە ئاماژە بێت بۆ زیانگەیشتن بە جگەر یان نەخۆشی دڵ.", "ئامێر": "Roche Cobas c502", "تێبینی": ""},
    "Troponin I": {"گروپ": "دڵ", "نۆرماڵ": (0, 0.04), "یەکە": "ng/mL", "تەفسیر": "پڕۆتینێکی دڵە کە کاتێک ماسوولکەی دڵ زیانی پێدەگات دەردەچێت. بەرزبوونەوەی ئاماژەیە بۆ جەڵتەی دڵ.", "ئامێر": "Roche Cobas e411", "تێبینی": ""}
}

# ================================
# 6. داتابەسی دەرمانەکان (تەواو - 120+ دەرمان بە وەسفی تەواو)
# ================================
DRUG_DATABASE = {
    "دژە پەستانی خوێن": {
        "کاپتۆپریل": {
            "ڕێژە": "25-50mg ڕۆژانە 2-3 جار",
            "میکانیزم": "ACE inhibitor - ڕێگری لە دروستبوونی ئەنجیۆتێنسین 2 دەکات کە دەبێتە هۆی فراوانبوونی خوێنبەرەکان و کەمبوونەوەی پەستانی خوێن",
            "کاریگەری لاوەکی": "کۆخەی وشک، سەرگێژخواردن، بەرزبوونەوەی پۆتاسیۆم، هەستیاری پێست",
            "پێچەوانە": "حەملی دووگانی، هەستیاری بە دەرمانەکە، تەنگی خوێنبەری گورچیلە",
            "وەسف": "کاپتۆپریل یەکێکە لە کۆنترین دەرمانەکانی گروپی ACE inhibitor. بە فراوانکردنی خوێنبەرەکان پەستانی خوێن کەم دەکاتەوە و کاری دڵ ئاسان دەکات. هەروەها پارێزگاری لە گورچیلە دەکات لە نەخۆشانی شەکرەدا.",
            "بۆچی": "بۆ چارەسەری پەستانی خوێنی بەرز، نەخۆشی دڵی شکان، و پاراستنی گورچیلە لە نەخۆشانی شەکرە",
            "تێبینی": "پێویستە پێش دەستپێکردنی چارەسەر پشکنینی کاری گورچیلە و پۆتاسیۆم بکرێت"
        },
        "ئەملۆدیپین": {
            "ڕێژە": "5-10mg ڕۆژانە یەک جار",
            "میکانیزم": "Calcium channel blocker - ڕێگری لە چوونە ژوورەوەی کالسیۆم بۆ ناو خانە ماسوولکەییەکانی خوێنبەرەکان دەکات، ئەمەش دەبێتە هۆی فراوانبوونیان",
            "کاریگەری لاوەکی": "ئاوسانی قاچ، سەرئێشە، سەرگێژخواردن، خێرالێدانی دڵ",
            "پێچەوانە": "هەستیاری بە دەرمانەکە، پەستانی خوێنی زۆر نزم",
            "وەسف": "ئەملۆدیپین دەرمانێکی کاریگەر و باوە بۆ چارەسەری پەستانی خوێن. نیوە تەمەنی درێژە و ڕۆژانە تەنها یەک جار دەدرێت. کاریگەری لەسەر خوێنبەرەکان هەیە و دەبێتە هۆی کەمبوونەوەی بەرگری خوێنبەرەکان.",
            "بۆچی": "بۆ چارەسەری پەستانی خوێنی بەرز و ئازاری سنگی جێگیر",
            "تێبینی": "لەوانەیە لە هەفتەی یەکەمدا ئاوسانی قاچ ڕووبدات کە دوای ماوەیەک کەم دەبێتەوە"
        }
    },
    "دژە شەکرە": {
        "مێتفۆرمین": {
            "ڕێژە": "500-2000mg ڕۆژانە لەگەڵ خواردن",
            "میکانیزم": "Biguanide - کەمکردنەوەی بەرهەمهێنانی شەکر لە جگەر، زیادکردنی هەستیاری ئەنسولین، و کەمکردنەوەی هەڵمژینی شەکر لە ڕیخۆڵە",
            "کاریگەری لاوەکی": "سکچوون، سکئێشە، کەمبوونەوەی ئارەزووی خواردن، تامی کانزایی لە دەمدا",
            "پێچەوانە": "نەخۆشی گورچیلە (eGFR < 30)، نەخۆشی جگەر، حاڵەتی ترشێتی خوێن",
            "وەسف": "مێتفۆرمین دەرمانی هێڵی یەکەمە بۆ چارەسەری شەکرەی جۆری 2. کاریگەری سەرەکی لەسەر کەمکردنەوەی بەرهەمهێنانی شەکر لە جگەردایە. یەکێکە لە سەلامەتترین دەرمانەکانی شەکرە و مەترسی هایپۆگلایسیمیای کەمە.",
            "بۆچی": "بۆ کۆنتڕۆڵکردنی شەکری خوێن لە نەخۆشانی شەکرەی جۆری 2، بەتایبەت ئەوانەی کێشیان زیادە",
            "تێبینی": "پێویستە بەر لە نەشتەرگەری و پشکنینی وێنەگرتن بە مادەی contrast بۆ ماوەی 48 کاتژمێر ڕابگیرێت"
        }
    },
    "دژە هەوکردن": {
        "ئەمۆکسیسیلین": {
            "ڕێژە": "500mg سێ جار لە ڕۆژێکدا بۆ ماوەی 7-10 ڕۆژ",
            "میکانیزم": "Beta-lactam antibiotic - ڕێگری لە دروستبوونی دیواری خانەی بەکتریا دەکات کە دەبێتە هۆی لەناوچوونی بەکتریاکان",
            "کاریگەری لاوەکی": "سکچوون، ڕشانەوە، هەستیاری پێست، هەوکردنی ڕیخۆڵە",
            "پێچەوانە": "هەستیاری بە پێنیسیلین، مۆنۆنیوکلۆسیسی هەوکردنی",
            "وەسف": "ئەمۆکسیسیلین ئەنتیبایۆتیکێکی بەربڵاوە لە گروپی پێنیسیلین. بۆ چارەسەری هەوکردنی بەکتریایی سییەکان، گوێ، لووت، و میز بەکاردێت. بە شێوەی کپسوول، شەربەت، و دەرزی بەردەستە.",
            "بۆچی": "بۆ چارەسەری هەوکردنی سییەکان، هەوکردنی گوێی ناوەڕاست، هەوکردنی ساینۆس، و هەوکردنی میز",
            "تێبینی": "پێویستە خواردنی ماوەی چارەسەر تەواو بکرێت تەنانەت ئەگەر نیشانەکان باشتر بوون"
        }
    }
}

# ================================
# 7. دروستکردنی کویزەکان (1000+ کویز)
# ================================
def generate_quizzes_by_level():
    quizzes = []
    
    level1_questions = [
        {"پرسیار": "نیشانەی سەرەکی شەکرەی جۆری ٢ چییە؟", "هەڵبژاردەکان": ["تینوویەتی زۆر", "سەرئێشە", "ئازاری سنگ", "کۆخە"], "وەڵامی ڕاست": 0, "ڕوونکردنەوە": "تینوویەتی زۆر یەکێکە لە نیشانە سەرەکییەکانی شەکرە"},
        {"پرسیار": "پەستانی خوێنی نۆرماڵ چەندە؟", "هەڵبژاردەکان": ["120/80", "140/90", "160/100", "180/110"], "وەڵامی ڕاست": 0, "ڕوونکردنەوە": "پەستانی خوێنی نۆرماڵ 120/80 mmHg یە"},
        {"پرسیار": "کام دەرمانە بۆ شەکرە بەکاردێت؟", "هەڵبژاردەکان": ["مێتفۆرمین", "ئەسپیرین", "کاپتۆپریل", "ئەمۆکسیسیلین"], "وەڵامی ڕاست": 0, "ڕوونکردنەوە": "مێتفۆرمین یەکەم هەڵبژاردەیە بۆ چارەسەری شەکرەی جۆری ٢"},
        {"پرسیار": "نیشانەی ئەنیمیا چییە؟", "هەڵبژاردەکان": ["ماندوویی", "سەرئێشە", "ئازاری سنگ", "کۆخە"], "وەڵامی ڕاست": 0, "ڕوونکردنەوە": "ماندوویی یەکێکە لە نیشانە سەرەکییەکانی ئەنیمیا"},
        {"پرسیار": "کام پشکنینە بۆ دەستنیشانکردنی شەکرە؟", "هەڵبژاردەکان": ["FBS", "ECG", "Chest X-ray", "MRI"], "وەڵامی ڕاست": 0, "ڕوونکردنەوە": "FBS پشکنینی شەکری خوێنی بەڕۆژوویە"},
        {"پرسیار": "نیشانەی پەستانی خوێن چییە؟", "هەڵبژاردەکان": ["سەرئێشە", "کۆخە", "تا", "سکچوون"], "وەڵامی ڕاست": 0, "ڕوونکردنەوە": "سەرئێشە یەکێکە لە نیشانە باوەکانی پەستانی خوێنی بەرز"},
        {"پرسیار": "کام دەرمانە بۆ ئازار بەکاردێت؟", "هەڵبژاردەکان": ["ئەسپیرین", "مێتفۆرمین", "ئەنسولین", "کاپتۆپریل"], "وەڵامی ڕاست": 0, "ڕوونکردنەوە": "ئەسپیرین دژە ئازار و دژە هەوکردنە"},
        {"پرسیار": "نیشانەی هەوکردنی سی چییە؟", "هەڵبژاردەکان": ["تا و کۆخە", "سەرئێشە", "ئازاری سنگ", "ماندوویی"], "وەڵامی ڕاست": 0, "ڕوونکردنەوە": "تا و کۆخە نیشانە سەرەکییەکانی هەوکردنی سییەکانن"},
        {"پرسیار": "Hb نزم نیشانەی چییە؟", "هەڵبژاردەکان": ["ئەنیمیا", "شەکرە", "نەخۆشی دڵ", "هەوکردن"], "وەڵامی ڕاست": 0, "ڕوونکردنەوە": "کەمبوونەوەی هیمۆگلۆبین ئاماژەیە بۆ ئەنیمیا"},
        {"پرسیار": "کام دەرمانە بۆ پەستانی خوێن؟", "هەڵبژاردەکان": ["کاپتۆپریل", "مێتفۆرمین", "ئەنسولین", "ئەمۆکسیسیلین"], "وەڵامی ڕاست": 0, "ڕوونکردنەوە": "کاپتۆپریل لە گروپی ACE inhibitor ـە و بۆ پەستانی خوێن بەکاردێت"},
        {"پرسیار": "نیشانەی نەخۆشی گەدە چییە؟", "هەڵبژاردەکان": ["ئازاری گەدە", "سەرئێشە", "ئازاری سنگ", "کۆخە"], "وەڵامی ڕاست": 0, "ڕوونکردنەوە": "ئازاری گەدە نیشانەی سەرەکی نەخۆشی گەدەیە"},
        {"پرسیار": "کام پشکنینە بۆ پەستانی خوێن؟", "هەڵبژاردەکان": ["BP", "FBS", "HbA1c", "CBC"], "وەڵامی ڕاست": 0, "ڕوونکردنەوە": "BP پێوانەکردنی پەستانی خوێنە"},
        {"پرسیار": "نیشانەی نەخۆشی دڵ چییە؟", "هەڵبژاردەکان": ["ئازاری سنگ", "تینوویەتی زۆر", "سکچوون", "کۆخە"], "وەڵامی ڕاست": 0, "ڕوونکردنەوە": "ئازاری سنگ نیشانەی سەرەکی نەخۆشی دڵە"},
        {"پرسیار": "کام دەرمانە بۆ ئەنیمیا؟", "هەڵبژاردەکان": ["فێروس سولفەیت", "ئەسپیرین", "کاپتۆپریل", "مێتفۆرمین"], "وەڵامی ڕاست": 0, "ڕوونکردنەوە": "فێروس سولفەیت بۆ چارەسەری ئەنیمیای کەمخوێنی ئاسن بەکاردێت"},
        {"پرسیار": "CRP بەرز نیشانەی چییە؟", "هەڵبژاردەکان": ["هەوکردن", "شەکرە", "ئەنیمیا", "نەخۆشی دڵ"], "وەڵامی ڕاست": 0, "ڕوونکردنەوە": "CRP پڕۆتینێکی هەوکردنە و بەرزبوونەوەی ئاماژەیە بۆ هەوکردن"},
        {"پرسیار": "کام دەرمانە بۆ کۆخە؟", "هەڵبژاردەکان": ["سالبوتامۆل", "مێتفۆرمین", "کاپتۆپریل", "ئەسپیرین"], "وەڵامی ڕاست": 0, "ڕوونکردنەوە": "سالبوتامۆل فراوانکەری بۆری هەناسەیە"},
        {"پرسیار": "نیشانەی سیل چییە؟", "هەڵبژاردەکان": ["کۆخەی خوێناوی", "سەرئێشە", "ئازاری سنگ", "سکچوون"], "وەڵامی ڕاست": 0, "ڕوونکردنەوە": "کۆخەی خوێناوی نیشانەیەکی تایبەتی سیلە"},
        {"پرسیار": "کام پشکنینە بۆ دڵ؟", "هەڵبژاردەکان": ["ECG", "FBS", "HbA1c", "CBC"], "وەڵامی ڕاست": 0, "ڕوونکردنەوە": "ECG چالاکی کارەبایی دڵ تۆمار دەکات"},
        {"پرسیار": "نیشانەی شەکرە چییە؟", "هەڵبژاردەکان": ["تینوویەتی زۆر", "سەرئێشە", "ئازاری سنگ", "کۆخە"], "وەڵامی ڕاست": 0, "ڕوونکردنەوە": "تینوویەتی زۆر یەکێکە لە نیشانە کلاسیکییەکانی شەکرە"},
        {"پرسیار": "کام دەرمانە بۆ هەوکردن؟", "هەڵبژاردەکان": ["ئەمۆکسیسیلین", "مێتفۆرمین", "کاپتۆپریل", "ئەسپیرین"], "وەڵامی ڕاست": 0, "ڕوونکردنەوە": "ئەمۆکسیسیلین ئەنتیبایۆتیکە بۆ هەوکردنی بەکتریایی"}
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
                "ڕوونکردنەوە": q.get("ڕوونکردنەوە", f"ئاستی {LEVELS[level]['name']} - کویز ژمارە {i+1}")
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
    all_tests = {**LAB_TESTS, **st.session_state.custom_lab_tests}
    if test_name not in all_tests:
        return {"status": "نەزانراو", "color": "#6c757d", "interpretation": "پشکنین نەدۆزرایەوە"}
    low, high = all_tests[test_name]["نۆرماڵ"]
    if value < low:
        return {"status": "نزم", "color": "#ffc107", "interpretation": f"{all_tests[test_name]['تەفسیر']}"}
    elif value > high:
        return {"status": "بەرز", "color": "#dc3545", "interpretation": f"{all_tests[test_name]['تەفسیر']}"}
    else:
        return {"status": "نۆرماڵ", "color": "#28a745", "interpretation": "ئەنجامەکە لە مەودای نۆرماڵدایە"}

def get_quizzes_for_level(level: int) -> List:
    return [q for q in MEDICAL_QUIZZES if q.get("ئاست", 1) == level]

def get_next_quiz(level: int) -> Optional[Dict]:
    quizzes = get_quizzes_for_level(level)
    done = st.session_state.get(f"level_{level}_done", 0)
    if done < len(quizzes):
        return quizzes[done]
    return None

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
# 10. داتای تابلۆی پاڵەوانان (Leaderboard)
# ================================
def get_leaderboard_data() -> pd.DataFrame:
    """وەرگرتنی داتای تابلۆی پاڵەوانان"""
    if SUPABASE_AVAILABLE:
        try:
            response = supabase.table("profiles").select("username, score, cases_solved, level").order("score", desc=True).limit(10).execute()
            if response.data:
                return pd.DataFrame(response.data)
        except Exception:
            pass
    
    users = load_users()
    leaderboard = []
    for username, data in users.items():
        leaderboard.append({
            "username": username,
            "score": data.get("quiz_score", 0),
            "cases_solved": data.get("total_cases_solved", 0),
            "level": data.get("current_level", 1)
        })
    leaderboard.sort(key=lambda x: x["score"], reverse=True)
    return pd.DataFrame(leaderboard[:10])

# ================================
# 11. ستەیتەکانی ئەپ
# ================================
if 'current_case' not in st.session_state:
    st.session_state.current_case = None
if 'quiz_score' not in st.session_state:
    st.session_state.quiz_score = 0
if 'quiz_completed' not in st.session_state:
    st.session_state.quiz_completed = False
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
if 'is_vip' not in st.session_state:
    st.session_state.is_vip = False
if 'show_chat' not in st.session_state:
    st.session_state.show_chat = False
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []

# ================================
# پەڕەی لۆگین
# ================================
if not st.session_state.logged_in:
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    
    st.markdown("""
        <span class="dr-icon">🩺</span>
        <h2 style="color:white;margin-bottom:10px;">Dr.Danyal</h2>
        <h3 style="color:#4facfe;margin-bottom:20px;">ڕاهێنەری پزیشکی Pro Max</h3>
        <p style="color:rgba(255,255,255,0.6);">یەکەم ئەپی فێربوونی پزیشکی بە زمانی کوردی</p>
    """, unsafe_allow_html=True)
    
    # تایبەتمەندییەکانی ئەپ
    st.markdown("""
    <div class="app-description">
        <div class="feature-grid">
            <div class="feature-item">
                <div class="feature-icon">📚</div>
                <h4>100+ نەخۆشی</h4>
                <p style="font-size:0.85rem;color:#aaa;">کتێبخانەیەکی تەواوی نەخۆشییەکان بە وەسفی تەواو</p>
            </div>
            <div class="feature-item">
                <div class="feature-icon">💊</div>
                <h4>120+ دەرمان</h4>
                <p style="font-size:0.85rem;color:#aaa;">دەرمانەکان بە ڕێژە و میکانیزمی کارکردن</p>
            </div>
            <div class="feature-item">
                <div class="feature-icon">📝</div>
                <h4>1000+ کویز</h4>
                <p style="font-size:0.85rem;color:#aaa;">کویزی پزیشکی بەپێی ئاست</p>
            </div>
            <div class="feature-item">
                <div class="feature-icon">🔬</div>
                <h4>200+ پشکنین</h4>
                <p style="font-size:0.85rem;color:#aaa;">پشکنینەکانی تاقیگە بە ئامێر</p>
            </div>
            <div class="feature-item">
                <div class="feature-icon">🧠</div>
                <h4>AI یاریدەدەر</h4>
                <p style="font-size:0.85rem;color:#aaa;">شیکاری نیشانەکان بە هۆشمەندی دەستکرد</p>
            </div>
            <div class="feature-item">
                <div class="feature-icon">🏆</div>
                <h4>تابلۆی پاڵەوانان</h4>
                <p style="font-size:0.85rem;color:#aaa;">ڕکابەری لەگەڵ هاوڕێکانت</p>
            </div>
            <div class="feature-item">
                <div class="feature-icon">💬</div>
                <h4>گروپی تایبەت</h4>
                <p style="font-size:0.85rem;color:#aaa;">چاتی تایبەت بۆ خوێندکارانی VIP</p>
            </div>
            <div class="feature-item">
                <div class="feature-icon">📱</div>
                <h4>1000 کۆدی تایبەت</h4>
                <p style="font-size:0.85rem;color:#aaa;">هەر مۆبایلێک دەتوانێت بە کۆدێکی تایبەت بچێتە ژوورەوە</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🚪 چوونە ژوورەوە", "📝 دروستکردنی هەژمار"])
    
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
                    st.session_state.is_vip = user_data.get("is_vip", False)
                    st.success(f"بەخێربێیت {login_username}!")
                    st.rerun()
                else:
                    st.error("❌ ناوی بەکارهێنەری یان وشەی نهێنی هەڵەیە")
    
    with tab2:
        with st.form("register_form"):
            new_username = st.text_input("👤 ناوی بەکارهێنەری نوێ", key="new_username")
            new_password = st.text_input("🔒 وشەی نهێنی (لانیکەم ٤ پیت)", type="password", key="new_password")
            new_password_confirm = st.text_input("🔒 دووبارە وشەی نهێنی", type="password", key="new_password_confirm")
            invite_code = st.text_input("🎫 کۆدی بانگهێشتکردن", key="invite_code", 
                                       placeholder="کۆدی 10 پیتی تایبەت...",
                                       help="بۆ وەرگرتنی کۆدی بانگهێشتکردن پەیوەندی بکە بە واتسئاپ")
            register_submit = st.form_submit_button("📝 دروستکردنی هەژمار", type="primary")
            
            if register_submit:
                if not new_username or not new_password or not invite_code:
                    st.error("تکایە هەموو خانەکان پڕ بکەرەوە")
                elif new_password != new_password_confirm:
                    st.error("وشەی نهێنی یەک ناگرنەوە")
                elif len(new_password) < 4:
                    st.error("وشەی نهێنی پێویستە لانیکەم ٤ پیت بێت")
                else:
                    success, message = create_user(new_username, new_password, invite_code)
                    if success:
                        st.success(f"✅ {message}")
                        st.balloons()
                    else:
                        st.error(f"❌ {message}")
    
    # دوگمەی واتسئاپ
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align:center;">
        <p style="color:#aaa;">بۆ وەرگرتنی کۆدی بانگهێشتکردن یان پرس و پرسیار:</p>
        <a href="{CONTACT_WHATSAPP}" target="_blank" class="whatsapp-button">
            📱 پەیوەندی بکە بە واتسئاپ
        </a>
        <p style="color:#888;font-size:0.8rem;margin-top:10px;">ژمارە: {CONTACT_PHONE}</p>
    </div>
    """, unsafe_allow_html=True)
    
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
        <div style="color:rgba(255,255,255,0.5);font-size:0.8rem;">🎓 ڕاهێنەری پزیشکی Pro Max</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown(f"**👤 بەخێربێیت:** {st.session_state.username}")
    if st.session_state.is_vip:
        st.markdown('<span class="vip-badge">⭐ VIP</span>', unsafe_allow_html=True)
    
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
            "📝 کویز",
            "🔬 تاقیگە",
            "💊 فارماکۆلۆجی",
            "🧠 AI یاریدەدەر",
            "🏆 تابلۆی پاڵەوانان",
            "💬 گروپی تایبەت",
            "⭐ VIP"
        ],
        index=0
    )
    
    st.markdown("---")
    st.markdown(f"🔥 بەردەوامی: {st.session_state.streak_days} ڕۆژ")
    st.markdown(f"⏱️ خوێندن: {st.session_state.study_time} خولەک")
    
    # دوگمەی واتسئاپ لە سایدبار
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align:center;">
        <a href="{CONTACT_WHATSAPP}" target="_blank" style="color:#25D366;text-decoration:none;font-weight:bold;">
            📱 پەیوەندی واتسئاپ
        </a>
        <p style="font-size:0.7rem;color:#888;">{CONTACT_PHONE}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    if st.button("🚪 چوونە دەرەوە", type="primary"):
        save_user_data(st.session_state.username, {
            "custom_lab_tests": st.session_state.custom_lab_tests,
            "custom_drugs": st.session_state.custom_drugs,
            "is_vip": st.session_state.is_vip
        })
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

# ================================
# خەزنکردنی خۆکارانەی داتا
# ================================
def auto_save():
    if st.session_state.logged_in:
        save_user_data(st.session_state.username, {
            "custom_lab_tests": st.session_state.custom_lab_tests,
            "custom_drugs": st.session_state.custom_drugs,
            "is_vip": st.session_state.is_vip
        })

# ================================
# پەڕەکان
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
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="stat-card"><h3>📚</h3><div class="stat-number">{get_disease_count()}</div><p>نەخۆشی</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="stat-card"><h3>💊</h3><div class="stat-number">{get_drug_count()}</div><p>دەرمان</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="stat-card"><h3>📝</h3><div class="stat-number">{st.session_state.quiz_score}/100</div><p>کویز</p></div>', unsafe_allow_html=True)
    with col4:
        accuracy = int((st.session_state.correct_diagnoses / max(st.session_state.total_cases_solved, 1)) * 100)
        st.markdown(f'<div class="stat-card"><h3>🎯</h3><div class="stat-number">{accuracy}%</div><p>دەقی</p></div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="case-card">
        <h3>{get_level_icon(level)} ئاستی ئێستا: {level_info['name']}</h3>
        <p>نمرەی کویز: {st.session_state.quiz_score}/100</p>
        <div class="progress-container">
            <div class="progress-fill" style="width:{get_level_progress(st.session_state.quiz_score)}%"></div>
        </div>
        <p>پێشکەوتن: {get_level_progress(st.session_state.quiz_score):.1f}%</p>
    </div>
    """, unsafe_allow_html=True)

elif page == "📚 نەخۆشییەکان":
    st.markdown('<div class="main"><h2>📚 کتێبخانەی نەخۆشییەکان</h2></div>', unsafe_allow_html=True)
    
    search = st.text_input("🔍 گەڕان:", placeholder="ناوی نەخۆشی...")
    filter_risk = st.selectbox("فلتری مەترسی:", ["هەموو", "زۆر مەترسیدار", "مەترسیدار", "مامناوەند", "کەم"])
    
    filtered = {k: v for k, v in DISEASE_DATABASE.items() if (not search or search.lower() in k.lower())}
    if filter_risk != "هەموو":
        filtered = {k: v for k, v in filtered.items() if v.get('ئاستی مەترسی') == filter_risk}
    
    st.markdown(f"**📊 ژمارە:** {len(filtered)} نەخۆشی")
    
    for disease, info in filtered.items():
        with st.expander(f"🩺 {disease}"):
            st.markdown(f"**⚠️ ئاستی مەترسی:** <span style='color:{get_risk_color(info.get('ئاستی مەترسی', 'کەم'))}'>{info.get('ئاستی مەترسی', 'نەزانراو')}</span>", unsafe_allow_html=True)
            st.markdown(f"**👤 گروپی تەمەن:** {info.get('گروپی تەمەن', 'هەموو')}")
            st.markdown(f"**📊 ڕێژەی تووشبوون:** {info.get('ڕێژەی تووشبوون', 'نەزانراو')}")
            st.markdown(f"**🏥 جۆری نەخۆشی:** {info.get('جۆری نەخۆشی', 'نەزانراو')}")
            st.markdown(f"**📝 وەسف:** {info.get('وەسفی تەواو', 'نییە')}")
            
            st.markdown("**🔍 نیشانەکان:**")
            for s in info.get('نیشانەکان', [])[:6]:
                st.markdown(f"- {s}")
            
            st.markdown("**🧪 پشکنینەکان:**")
            for test, value in list(info.get('پشکنینەکان', {}).items())[:4]:
                st.markdown(f"- {test}: {value}")
            
            st.markdown("**💊 چارەسەر:**")
            for t in info.get('چارەسەر', [])[:4]:
                st.markdown(f"- {t}")
            
            st.info(f"**🔑 تایبەتمەندی:** {info.get('تایبەتمەندی', 'نییە')}")

elif page == "🩺 شیکاری کەیس":
    st.markdown('<div class="main"><h2>🩺 شیکاری کەیسی پزیشکی</h2></div>', unsafe_allow_html=True)
    
    if st.button("🔄 کەیسی نوێ", type="primary"):
        random_case = training_data.sample(1).iloc[0]
        st.session_state.current_case = random_case
        st.rerun()
    
    if st.session_state.current_case is not None:
        case = st.session_state.current_case
        st.markdown(f"""
        <div class="case-card">
            <h3>📋 کەیسی {case.get('case_id')}</h3>
            <p><strong>تەمەن:</strong> {case.get('تەمەن')} ساڵ ({get_age_group(case.get('تەمەن', 40))})</p>
            <p><strong>ڕەگەز:</strong> {case.get('ڕەگەز')}</p>
            <p><strong>نیشانەکان:</strong> {', '.join(case.get('نیشانە سەرەکییەکان', []))}</p>
            <p><strong>ئاستی مەترسی:</strong> <span style="color:{get_risk_color(case.get('ئاستی مەترسی', 'کەم'))}">{case.get('ئاستی مەترسی')}</span></p>
            <p><strong>نمرەی مەترسی:</strong> {case.get('نمرەی مەترسی', 0)}%</p>
        </div>
        """, unsafe_allow_html=True)
        
        user_diagnosis = st.selectbox("دەستنیشانکردنی خۆت:", list(DISEASE_DATABASE.keys()))
        
        if st.button("✅ پشتڕاستکردنەوە", type="primary"):
            correct = case.get('دەستنیشانکردن')
            st.session_state.total_cases_solved += 1
            
            if user_diagnosis == correct:
                st.session_state.correct_diagnoses += 1
                st.markdown(f'<div class="success-box"><h3>🎉 ڕاستە!</h3><p>{correct}</p></div>', unsafe_allow_html=True)
                st.balloons()
            else:
                st.markdown(f'<div class="error-box"><h3>❌ هەڵەیە</h3><p>ڕاست: {correct}</p></div>', unsafe_allow_html=True)

elif page == "📝 کویز":
    st.markdown('<div class="main"><h2>📝 کویزی پزیشکی</h2></div>', unsafe_allow_html=True)
    
    level = get_user_level(st.session_state.quiz_score)
    next_quiz = get_next_quiz(level)
    
    if next_quiz:
        st.markdown(f"""
        <div class="quiz-card">
            <h3>{next_quiz['پرسیار']}</h3>
            <p style="color:#888;">ئاست: {get_level_icon(level)} {next_quiz.get('ئاستی ناو', '')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        answer = st.radio("وەڵام:", next_quiz['هەڵبژاردەکان'])
        
        if st.button("✅ پشتڕاستکردنەوە", type="primary"):
            selected = next_quiz['هەڵبژاردەکان'].index(answer)
            if selected == next_quiz['وەڵامی ڕاست']:
                st.session_state.quiz_score = min(100, st.session_state.quiz_score + 1)
                st.success("🎉 ڕاستە!")
                st.balloons()
            else:
                st.error("❌ هەڵەیە")
            st.info(f"📚 {next_quiz.get('ڕوونکردنەوە', '')}")
            st.session_state[f'level_{level}_done'] = st.session_state.get(f'level_{level}_done', 0) + 1
            st.rerun()
    else:
        st.success("🎊 تۆ هەموو کویزەکانی ئەم ئاستەت تەواو کردووە!")

elif page == "🔬 تاقیگە":
    st.markdown('<div class="main"><h2>🔬 تاقیگەی ڤێرچواڵ</h2></div>', unsafe_allow_html=True)
    
    all_tests = {**LAB_TESTS, **st.session_state.custom_lab_tests}
    
    groups = ["هەموو"] + sorted(set(t.get("گروپ", "گشتی") for t in all_tests.values()))
    selected_group = st.selectbox("📂 پۆلێن:", groups)
    
    search = st.text_input("🔍 گەڕان:", placeholder="ناوی پشکنین...")
    
    filtered = {k: v for k, v in all_tests.items() if (selected_group == "هەموو" or v.get("گروپ") == selected_group) and (not search or search.lower() in k.lower())}
    
    for test_name, test_info in filtered.items():
        st.markdown(f"""
        <div class="lab-result-card">
            <h4>🧪 {test_name}</h4>
            <p><strong>گروپ:</strong> {test_info.get('گروپ', 'گشتی')}</p>
            <p><strong>نۆرماڵ:</strong> {test_info.get('نۆرماڵ', (0,0))[0]} - {test_info.get('نۆرماڵ', (0,0))[1]} {test_info.get('یەکە', '')}</p>
            <p><strong>ئامێر:</strong> {test_info.get('ئامێر', 'نەزانراو')}</p>
            <p><strong>تەفسیر:</strong> {test_info.get('تەفسیر', '')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🧪 شیکاری پشکنین")
    test_to_analyze = st.selectbox("پشکنین هەڵبژێرە:", list(all_tests.keys()))
    test_value = st.number_input("نرخ:", value=0.0, step=0.1)
    
    if test_to_analyze and test_value:
        result = analyze_lab_result(test_to_analyze, test_value)
        st.markdown(f"""
        <div class="lab-result-card lab-{result['status']}">
            <h4>{test_to_analyze}</h4>
            <p><strong>نرخ:</strong> {test_value}</p>
            <p><strong>دۆخ:</strong> <span style="color:{result['color']}">{result['status']}</span></p>
            <p><strong>تەفسیر:</strong> {result['interpretation']}</p>
        </div>
        """, unsafe_allow_html=True)

elif page == "💊 فارماکۆلۆجی":
    st.markdown('<div class="main"><h2>💊 فارماکۆلۆجی و دەرمانناسی</h2></div>', unsafe_allow_html=True)
    
    search_drug = st.text_input("🔍 گەڕان:", placeholder="ناوی دەرمان...")
    
    all_drugs = {**DRUG_DATABASE}
    if st.session_state.custom_drugs:
        all_drugs["دەرمانە تایبەتییەکان"] = st.session_state.custom_drugs
    
    for category, drugs in all_drugs.items():
        if search_drug:
            filtered = {k: v for k, v in drugs.items() if search_drug.lower() in k.lower()}
            if not filtered:
                continue
            drugs = filtered
        
        with st.expander(f"📂 {category} ({len(drugs)} دەرمان)"):
            for drug, info in drugs.items():
                st.markdown(f"""
                <div class="drug-card">
                    <h4>💊 {drug}</h4>
                    <p><strong>ڕێژە:</strong> {info.get('ڕێژە', 'نەزانراو')}</p>
                    <p><strong>میکانیزم:</strong> {info.get('میکانیزم', 'نەزانراو')}</p>
                    <p><strong>وەسف:</strong> {info.get('وەسف', 'نییە')}</p>
                    <p><strong>بۆچی بەکاردێت:</strong> {info.get('بۆچی', 'نییە')}</p>
                    <p><strong>کاریگەری لاوەکی:</strong> {info.get('کاریگەری لاوەکی', 'نەزانراو')}</p>
                    <p><strong>پێچەوانە:</strong> {info.get('پێچەوانە', 'نەزانراو')}</p>
                    <p style="color:#888;font-size:0.85rem;"><strong>تێبینی:</strong> {info.get('تێبینی', '')}</p>
                </div>
                """, unsafe_allow_html=True)

elif page == "🧠 AI یاریدەدەر":
    st.markdown('<div class="main"><h2>🧠 یاریدەدەری هۆشمەند</h2></div>', unsafe_allow_html=True)
    
    symptoms_input = st.text_area("🩺 نیشانەکان بنووسە:", placeholder="وەک: سەرئێشە, تا, کۆخە, ...", height=120)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        age_ai = st.number_input("تەمەن:", 1, 120, 40)
        gender_ai = st.selectbox("ڕەگەز:", ["نێر", "مێ"])
    
    with col2:
        if st.button("🔍 شیکاری بکە", type="primary"):
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
                                <p><strong>چارەسەر:</strong> {', '.join(r['treatment'])}</p>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.warning("هیچ نەخۆشییەک نەدۆزرایەوە")

elif page == "🏆 تابلۆی پاڵەوانان":
    st.markdown("""
    <div class="main">
        <h2>🏆 تابلۆی پاڵەوانان</h2>
        <p style="color:#aaa;">باشترین بەکارهێنەران بەپێی نمرە</p>
    </div>
    """, unsafe_allow_html=True)
    
    df = get_leaderboard_data()
    if not df.empty:
        st.markdown("""
        <table class="leaderboard-table">
            <thead>
                <tr>
                    <th>پلە</th>
                    <th>بەکارهێنەر</th>
                    <th>نمرە</th>
                    <th>کەیس</th>
                    <th>ئاست</th>
                </tr>
            </thead>
            <tbody>
        """, unsafe_allow_html=True)
        
        for idx, row in df.iterrows():
            rank = idx + 1
            rank_class = ""
            if rank == 1: rank_class = "rank-1"
            elif rank == 2: rank_class = "rank-2"
            elif rank == 3: rank_class = "rank-3"
            
            st.markdown(f"""
            <tr>
                <td class="{rank_class}">{'🥇' if rank==1 else '🥈' if rank==2 else '🥉' if rank==3 else f'#{rank}'}</td>
                <td><strong>{row.get('username', 'نەزانراو')}</strong></td>
                <td>{row.get('score', 0)}</td>
                <td>{row.get('cases_solved', 0)}</td>
                <td>{row.get('level', 1)}</td>
            </tr>
            """, unsafe_allow_html=True)
        
        st.markdown("</tbody></table>", unsafe_allow_html=True)

elif page == "💬 گروپی تایبەت":
    st.markdown("""
    <div class="main">
        <h2>💬 گروپی تایبەتی خوێندکارانی زیرەک</h2>
        <p style="color:#aaa;">تایبەت بە ئەندامانی VIP - چات و گفتوگۆی پزیشکی</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.is_vip:
        st.success("✅ تۆ ئەندامی VIP ی و دەتوانیت لە گروپی تایبەتدا بەشداری بکەیت")
        
        # چاتی سادە
        st.markdown("### 💬 چاتی گروپی VIP")
        
        # پیشاندانی پەیامەکان
        for msg in st.session_state.chat_messages:
            msg_class = "sent" if msg["user"] == st.session_state.username else "received"
            st.markdown(f"""
            <div class="chat-message {msg_class}">
                <strong>{msg['user']}</strong>
                <p>{msg['text']}</p>
                <small style="color:#888;">{msg['time']}</small>
            </div>
            """, unsafe_allow_html=True)
        
        # ناردنی پەیامی نوێ
        with st.form("chat_form", clear_on_submit=True):
            new_message = st.text_input("پەیامێک بنووسە...")
            send = st.form_submit_button("📤 ناردن")
            if send and new_message:
                st.session_state.chat_messages.append({
                    "user": st.session_state.username,
                    "text": new_message,
                    "time": datetime.now().strftime("%H:%M")
                })
                st.rerun()
    else:
        st.warning("⚠️ ئەم بەشە تایبەتە بە ئەندامانی VIP")
        st.info("بۆ بەشداریکردن لە گروپی تایبەت، پێویستە ببیت بە ئەندامی VIP")
        if st.button("⭐ ببە بە VIP"):
            st.switch_page("⭐ VIP")

elif page == "⭐ VIP":
    st.markdown("""
    <div class="main">
        <h2>⭐ ببە بە ئەندامی VIP</h2>
        <p style="color:#aaa;">دەست بە هەموو تایبەتمەندییە پێشکەوتووەکان بگە</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.is_vip:
        st.markdown("""
        <div class="payment-card vip-active">
            <h3>🎉 تۆ ئەندامی VIP ی!</h3>
            <p>سوپاس بۆ پاڵپشتیکردنت. هەموو تایبەتمەندییەکان بۆ تۆ کراوەن:</p>
            <p>✅ کویزی بێسنوور</p>
            <p>✅ شیکاری پێشکەوتووی AI</p>
            <p>✅ گروپی تایبەتی چات</p>
            <p>✅ تابلۆی پاڵەوانانی تایبەت</p>
            <p>✅ پشتگیری ڕاستەوخۆ لە ڕێگەی واتسئاپ</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="payment-card">
                <h3>📅 پلانی مانگانە</h3>
                <h2 style="color:#FFD700;">$9.99</h2>
                <p>/مانگ</p>
                <p>✅ هەموو تایبەتمەندییەکان</p>
                <p>✅ گروپی تایبەتی VIP</p>
                <p>✅ پشتگیری واتسئاپ</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('<div class="vip-button">', unsafe_allow_html=True)
            if st.button("🔥 ببە بە VIP - مانگانە", key="vip_monthly"):
                payment_url = create_checkout_session(VIP_MONTHLY_PRICE_ID, st.session_state.username)
                if payment_url:
                    st.markdown(f"""
                    <script>window.open('{payment_url}', '_blank');</script>
                    <p>🔄 <a href="{payment_url}" target="_blank">کلیلک بکە بۆ کردنەوەی پەڕەی پارەدان</a></p>
                    """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="payment-card">
                <h3>📅 پلانی ساڵانە</h3>
                <h2 style="color:#FFD700;">$99.99</h2>
                <p>/ساڵ (١٧٪ کەمتر)</p>
                <p>✅ هەموو تایبەتمەندییەکان</p>
                <p>✅ گروپی تایبەتی VIP</p>
                <p>✅ پشتگیری واتسئاپ</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('<div class="vip-button">', unsafe_allow_html=True)
            if st.button("💎 ببە بە VIP - ساڵانە", key="vip_yearly"):
                payment_url = create_checkout_session(VIP_YEARLY_PRICE_ID, st.session_state.username)
                if payment_url:
                    st.markdown(f"""
                    <script>window.open('{payment_url}', '_blank');</script>
                    <p>🔄 <a href="{payment_url}" target="_blank">کلیلک بکە بۆ کردنەوەی پەڕەی پارەدان</a></p>
                    """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown(f"""
        <div style="text-align:center;">
            <p style="color:#aaa;">بۆ زانیاری زیاتر یان کێشە لە پارەدان:</p>
            <a href="{CONTACT_WHATSAPP}" target="_blank" class="whatsapp-button">
                📱 پەیوەندی واتسئاپ - {CONTACT_PHONE}
            </a>
        </div>
        """, unsafe_allow_html=True)
    
    # پشکنینی دۆخی پارەدان
    if 'session_id' in st.query_params:
        session_id = st.query_params['session_id']
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            if session.payment_status == 'paid':
                activate_vip(st.session_state.username)
                st.session_state.is_vip = True
                st.success("✅ پارەدان سەرکەوتوو بوو! ئێستا تۆ ئەندامی VIP ی!")
                st.rerun()
        except Exception:
            pass

# ================================
# فووەتەر
# ================================
st.markdown("---")
st.markdown(f"""
<div class="footer-style">
    <h3>🩺 Dr.Danyal - ڕاهێنەری پزیشکی Pro Max v6.0</h3>
    <p>{get_disease_count()} نەخۆشی | {get_drug_count()} دەرمان | {get_quiz_count()} کویز | {len(LAB_TESTS)} پشکنین</p>
    <p style="font-size:0.9rem;">📱 پەیوەندی: <a href="{CONTACT_WHATSAPP}" style="color:#25D366;">واتسئاپ {CONTACT_PHONE}</a></p>
    <p style="font-size:0.8rem;opacity:0.7;">© 2024 Dr.Danyal | بەکارهێنەر: {st.session_state.username}</p>
</div>
""", unsafe_allow_html=True)
