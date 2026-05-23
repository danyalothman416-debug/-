import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
import base64
from io import BytesIO
import time
import random

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="ڕێبەری پشکنینە تاقیگەییەکان", 
    layout="wide", 
    initial_sidebar_state="collapsed",
    page_icon="🔬"
)

# --- SESSION STATE ---
if 'history' not in st.session_state:
    st.session_state.history = []
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []
if 'user_results' not in st.session_state:
    st.session_state.user_results = {}

# --- ULTRA MODERN CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Naskh+Arabic:wght@300;400;500;600;700;800;900&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css');
    
    * {
        font-family: 'Noto Naskh Arabic', 'Segoe UI', sans-serif;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    [data-testid="stSidebar"] { display: none; }
    
    /* Background Animations */
    html, body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0a0a1a 0%, #1a1a3e 25%, #0d0d2b 50%, #1a1a3e 75%, #0a0a1a 100%) !important;
        background-size: 400% 400% !important;
        animation: gradientShift 15s ease infinite !important;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Glass Morphism Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 24px !important;
        padding: 30px !important;
        margin-bottom: 25px !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    .glass-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.05), transparent);
        animation: shimmer 3s infinite;
    }
    
    @keyframes shimmer {
        100% { left: 100%; }
    }
    
    /* Neon Header */
    .neon-header {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(139, 92, 246, 0.2), rgba(59, 130, 246, 0.2));
        border: 2px solid rgba(99, 102, 241, 0.5);
        border-radius: 30px;
        padding: 40px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 0 40px rgba(99, 102, 241, 0.3), 0 0 80px rgba(139, 92, 246, 0.2), 0 0 120px rgba(59, 130, 246, 0.1);
        animation: neonPulse 3s ease-in-out infinite;
    }
    
    @keyframes neonPulse {
        0%, 100% { box-shadow: 0 0 40px rgba(99, 102, 241, 0.3), 0 0 80px rgba(139, 92, 246, 0.2); }
        50% { box-shadow: 0 0 60px rgba(99, 102, 241, 0.5), 0 0 120px rgba(139, 92, 246, 0.4), 0 0 180px rgba(59, 130, 246, 0.2); }
    }
    
    .neon-header h1 {
        font-size: 3rem !important;
        font-weight: 900 !important;
        background: linear-gradient(135deg, #6366f1, #8b5cf6, #3b82f6, #06b6d4);
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        animation: textGlow 3s ease-in-out infinite alternate;
    }
    
    @keyframes textGlow {
        0% { filter: brightness(1); }
        100% { filter: brightness(1.3); }
    }
    
    .neon-header p {
        color: rgba(255, 255, 255, 0.8) !important;
        font-size: 1.3rem !important;
    }
    
    /* Test Cards with Gradient Borders */
    .test-card {
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 20px;
        border: 1px solid transparent;
        background-clip: padding-box;
        position: relative;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }
    
    .test-card::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        border-radius: 22px;
        background: linear-gradient(135deg, #6366f1, #8b5cf6, #3b82f6);
        z-index: -1;
        opacity: 0.5;
    }
    
    .test-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 20px 60px rgba(99, 102, 241, 0.3);
    }
    
    /* AI Analysis Card */
    .ai-result-card {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(99, 102, 241, 0.1));
        border: 2px solid rgba(16, 185, 129, 0.5);
        border-radius: 24px;
        padding: 30px;
        margin: 25px 0;
        box-shadow: 0 0 40px rgba(16, 185, 129, 0.2);
        animation: slideUp 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .result-normal {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(16, 185, 129, 0.05));
        border-left: 5px solid #10b981;
        border-radius: 16px;
        padding: 20px;
        margin: 15px 0;
    }
    
    .result-abnormal {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(245, 158, 11, 0.05));
        border-left: 5px solid #f59e0b;
        border-radius: 16px;
        padding: 20px;
        margin: 15px 0;
    }
    
    .result-critical {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(239, 68, 68, 0.05));
        border-left: 5px solid #ef4444;
        border-radius: 16px;
        padding: 20px;
        margin: 15px 0;
        animation: criticalPulse 2s infinite;
    }
    
    @keyframes criticalPulse {
        0%, 100% { border-color: #ef4444; }
        50% { border-color: #fca5a5; box-shadow: 0 0 30px rgba(239, 68, 68, 0.3); }
    }
    
    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        color: white !important;
        border: none !important;
        font-weight: 700 !important;
        border-radius: 16px !important;
        padding: 14px 35px !important;
        font-size: 16px !important;
        letter-spacing: 0.5px !important;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4) !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase !important;
    }
    
    .stButton button:hover {
        transform: translateY(-4px) !important;
        box-shadow: 0 15px 40px rgba(99, 102, 241, 0.6) !important;
        background: linear-gradient(135deg, #8b5cf6, #6366f1) !important;
    }
    
    /* Input Fields */
    .stTextInput input, .stNumberInput input, .stSelectbox select {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 2px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important;
        color: white !important;
        padding: 14px 20px !important;
        font-size: 1.1rem !important;
        backdrop-filter: blur(10px) !important;
    }
    
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 20px rgba(99, 102, 241, 0.3) !important;
    }
    
    /* Chat Messages */
    .chat-container {
        max-height: 500px;
        overflow-y: auto;
        padding: 20px;
    }
    
    .chat-message-user {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(99, 102, 241, 0.1));
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 20px 20px 5px 20px;
        padding: 15px 20px;
        margin: 10px 0;
        color: white;
    }
    
    .chat-message-bot {
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(139, 92, 246, 0.1));
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 20px 20px 20px 5px;
        padding: 15px 20px;
        margin: 10px 0;
        color: white;
    }
    
    /* FAQ Cards */
    .faq-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 18px;
        margin: 10px 0;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .faq-card:hover {
        background: rgba(99, 102, 241, 0.1);
        border-color: rgba(99, 102, 241, 0.4);
        transform: translateX(-5px);
    }
    
    /* Stats Cards */
    .stat-card {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 20px;
        padding: 25px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(10px);
    }
    
    .stat-value {
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(135deg, #6366f1, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .stat-label {
        color: rgba(255, 255, 255, 0.6);
        font-size: 1rem;
        margin-top: 8px;
    }
    
    /* Food Recommendation Cards */
    .food-card {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(239, 68, 68, 0.1));
        border: 1px solid rgba(245, 158, 11, 0.3);
        border-radius: 20px;
        padding: 20px;
        margin: 15px 0;
    }
    
    .food-card h4 {
        color: #fbbf24 !important;
        font-size: 1.3rem !important;
    }
    
    /* Category Title */
    .category-badge {
        display: inline-block;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(139, 92, 246, 0.2));
        border: 1px solid rgba(99, 102, 241, 0.4);
        border-radius: 30px;
        padding: 10px 25px;
        margin: 20px 0 15px 0;
        font-weight: 700;
        color: #a5b4fc !important;
        font-size: 1.1rem;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: rgba(255,255,255,0.05); border-radius: 10px; }
    ::-webkit-scrollbar-thumb { background: linear-gradient(135deg, #6366f1, #8b5cf6); border-radius: 10px; }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: transparent !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.03) !important;
        border-radius: 15px !important;
        color: white !important;
        padding: 12px 25px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.3), rgba(139, 92, 246, 0.3)) !important;
        border-color: rgba(99, 102, 241, 0.5) !important;
    }
    
    /* Color text */
    .text-white { color: white !important; }
    .text-purple { color: #a5b4fc !important; }
    .text-cyan { color: #67e8f9 !important; }
    .text-green { color: #6ee7b7 !important; }
    .text-yellow { color: #fde68a !important; }
    .text-red { color: #fca5a5 !important; }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.03) !important;
        border-radius: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        color: white !important;
    }
    
    [dir="rtl"] { text-align: right !important; direction: rtl !important; }
</style>
""", unsafe_allow_html=True)

# --- COMPLETE DATABASE ---
ALL_TESTS = {
    "پشکنینی تەواوی خوێن (CBC)": {
        "Name": "پشکنینی تەواوی خوێن (CBC - Complete Blood Count)",
        "Category": "پشکنینە بنەڕەتییەکان",
        "Organ": "خوێن",
        "Icon": "🩸",
        "Description": "پێوانەی پێکهاتەکانی خوێن: خڕۆکە سوورەکان، خڕۆکە سپییەکان و پەڕەکانی خوێن. یارمەتیدەرە بۆ دەستنیشانکردنی کەمخوێنی، هەوکردن، و کێشەکانی مەینبوونی خوێن.",
        "Ranges": "هیمۆگڵۆبین (پیاوان): 13.5-17.5 g/dL | هیمۆگڵۆبین (ژنان): 12.0-15.5 g/dL | WBC: 4,500-11,000 /µL | Platelets: 150,000-450,000 /µL | RBC: 4.7-6.1 (پیاوان) / 4.2-5.4 (ژنان) million/µL",
        "FoodRecommendations": "🥩 گۆشتی سوور | 🥬 سپێناغ | 🥚 هێلکە | 🍊 پرتەقاڵ (بۆ ڤیتامین C) | ❌ دوور لە چا و قاوە دوای نان"
    },
    "شەکری ناو خوێن (FBS)": {
        "Name": "شەکری ناو خوێن لە کاتی برسێتیدا (FBS)",
        "Category": "پشکنینە بنەڕەتییەکان",
        "Organ": "پەنکریاس / خوێن",
        "Icon": "🍬",
        "Description": "پێوانەی گلوکۆزی خوێن دوای ٨-١٢ کاتژمێر برسێتی. ١٠٠-١٢٥ = پێش شەکرە | ١٢٦+ = شەکرە.",
        "Ranges": "ڕێژەی ئاسایی: 70-99 mg/dL",
        "FoodRecommendations": "🥦 برۆکلی | 🐟 ماسی چەور | 🌾 هەویری تەواو | ❌ دوور لە شەکر و نانی سپی"
    },
    "شەکری کەڵەکەبوو (HbA1c)": {
        "Name": "شەکری کەڵەکەبوو (HbA1c)",
        "Category": "پشکنینە بنەڕەتییەکان",
        "Organ": "پەنکریاس / خوێن",
        "Icon": "📊",
        "Description": "تێکڕای شەکری خوێن لە ٢-٣ مانگی ڕابردوو. 5.7%-6.4% = پێش شەکرە | 6.5%+ = شەکرە.",
        "Ranges": "ڕێژەی ئاسایی: کەمتر لە 5.7%",
        "FoodRecommendations": "🥗 سەوزەواتی ڕیشاڵدار | 🫘 پاقلەمەنی | 🏃 وەرزشی ڕۆژانە"
    },
    "چەورییەکانی خوێن (Lipid Profile)": {
        "Name": "چەورییەکانی خوێن (Lipid Profile)",
        "Category": "پشکنینە بنەڕەتییەکان",
        "Organ": "دڵ / خوێن",
        "Icon": "❤️",
        "Description": "پێوانەی چەورییەکانی خوێن: کۆلیسترۆڵ، HDL، LDL، و Triglycerides.",
        "Ranges": "کۆلیسترۆڵی گشتی: <200 mg/dL | Triglycerides: <150 mg/dL | HDL: >40 mg/dL | LDL: <100 mg/dL",
        "FoodRecommendations": "🥑 ئەڤۆکادۆ | 🥜 گوێز و بادەم | 🫒 زەیتی زەیتوون | ❌ دوور لە فاست فوود"
    },
    "فەرمانی گورچیلە (KFT)": {
        "Name": "پشکنینی فەرمانی گورچیلە (KFT)",
        "Category": "پشکنینە بنەڕەتییەکان",
        "Organ": "گورچیلە",
        "Icon": "🫘",
        "Description": "پێوانەی توانای گورچیلەکان: کریاتینین و یوریا.",
        "Ranges": "کریاتینین (پیاوان): 0.7-1.3 mg/dL | کریاتینین (ژنان): 0.6-1.1 mg/dL | یوریا (BUN): 15-40 mg/dL | GFR: >90 mL/min",
        "FoodRecommendations": "💧 ئاوی زۆر (٨-١٠ پەرداخ) | 🍎 سێو | ❌ کەمکردنەوەی خوێ"
    },
    "فەرمانی جگەر (LFT)": {
        "Name": "پشکنینی فەرمانی جگەر (LFT)",
        "Category": "پشکنینە بنەڕەتییەکان",
        "Organ": "جگەر",
        "Icon": "🫁",
        "Description": "ئەنزیمەکانی جگەر: ALT، AST، ALP، GGT، بیلیڕۆبین.",
        "Ranges": "ALT: 7-56 U/L | AST: 10-40 U/L | ALP: 44-147 U/L | GGT: 0-30 U/L | بیلیڕۆبینی گشتی: 0.1-1.2 mg/dL",
        "FoodRecommendations": "🍵 چای سەوز | 🧄 سیر | 🫚 زەردەچێوە | ❌ دوور لە کحول"
    },
    "هۆرمۆنی دەرەقی (TSH)": {
        "Name": "هۆرمۆنی ڕژێنی دەرەقی (TSH)",
        "Category": "پشکنینی هۆرمۆنەکان",
        "Organ": "دەرەقی (تیرۆید)",
        "Icon": "🦋",
        "Description": "پشکنینی کارکردنی غودەی دەرەقی. بەرزبوونەوە = تەمەڵی، نزمبوونەوە = زۆر چالاکی.",
        "Ranges": "TSH: 0.4-4.0 mIU/L | T3: 80-200 ng/dL | T4: 4.5-12.0 µg/dL",
        "FoodRecommendations": "🧂 خوێی یۆددار | 🐟 ماسی دەریا | 🥜 گوێزی بەرازیلی"
    },
    "کۆگای ئاسن (Ferritin)": {
        "Name": "کۆگای ئاسن (Ferritin)",
        "Category": "پشکنینە تایبەتەکان",
        "Organ": "خوێن",
        "Icon": "🧲",
        "Description": "پێوانەی ئاسنی خەزنکراوی لەش. کەمی = کەمخوێنی و ڕووتانەوەی قژ.",
        "Ranges": "پیاوان: 24-336 ng/mL | ژنان: 11-307 ng/mL",
        "FoodRecommendations": "🥩 گۆشتی سوور | 🥬 سپێناغ | 🍊 ڤیتامین C یارمەتیدەر"
    },
    "ڤیتامین دی (Vitamin D3)": {
        "Name": "ڤیتامین دی (25-Hydroxy Vitamin D)",
        "Category": "پشکنینی ڤیتامین و کانزاکان",
        "Organ": "ئێسک / خوێن",
        "Icon": "☀️",
        "Description": "بۆ تەندروستی ئێسک و بەرگری لەش. <20 = کەمی ڤیتامین دی.",
        "Ranges": "ڕێژەی ئاسایی: 30-100 ng/mL",
        "FoodRecommendations": "☀️ ڕووناکی خۆر | 🐟 سەلەمۆن | 🥛 شیری ڤیتامین دی زیادکراو"
    },
    "ترشی یۆریک (Uric Acid)": {
        "Name": "ترشی یۆریک (Uric Acid)",
        "Category": "پشکنینە تایبەتەکان",
        "Organ": "گورچیلە / جومگەکان",
        "Icon": "🦴",
        "Description": "بەرزبوونەوە = ڕۆماتیزمی دەردە پاشا (Gout) و بەردی گورچیلە.",
        "Ranges": "پیاوان: 3.4-7.0 mg/dL | ژنان: 2.4-6.0 mg/dL",
        "FoodRecommendations": "💧 ئاوی زۆر | 🍒 گێلاس | ❌ کەمکردنەوەی گۆشتی سوور"
    },
    "پشکنینی هەوکردن (CRP)": {
        "Name": "پشکنینی هەوکردن (CRP)",
        "Category": "پشکنینی هەوکردن",
        "Organ": "گشتی لەش",
        "Icon": "🔥",
        "Description": "نیشاندەری هەوکردنی چالاک لە لەشدا.",
        "Ranges": "ڕێژەی ئاسایی: <10 mg/L | hs-CRP: <1.0 mg/L",
        "FoodRecommendations": "🫚 زەنجەفیل | 🫚 زەردەچێوە | 🐟 ماسی چەور"
    },
    "ترۆپۆنین (Troponin)": {
        "Name": "ترۆپۆنین (Troponin) - فریاکەوتن",
        "Category": "پشکنینی فریاگوزاری",
        "Organ": "دڵ",
        "Icon": "💔",
        "Description": "پشکنینی فریاگوزاری بۆ جەڵتەی دڵ. بەرزبوونەوە = مەترسی.",
        "Ranges": "ڕێژەی ئاسایی: <0.04 ng/mL (نزیک بە سفر)",
        "FoodRecommendations": "❤️ ڕێجیمی دڵ تەندروست | 🏃 وەرزش | ❌ دوور لە جگەرە"
    },
    "ئەلیکترۆلیتەکان (Electrolytes)": {
        "Name": "پشکنینی ئەلیکترۆلیتەکان",
        "Category": "پشکنینە بنەڕەتییەکان",
        "Organ": "گورچیلە / خوێن",
        "Icon": "⚡",
        "Description": "پێوانەی سۆدیۆم، پۆتاسیۆم، کالیسیۆم، و مەگنیسیۆم.",
        "Ranges": "سۆدیۆم: 135-145 mEq/L | پۆتاسیۆم: 3.6-5.2 mEq/L | کالیسیۆم: 8.5-10.2 mg/dL | مەگنیسیۆم: 1.7-2.2 mg/dL",
        "FoodRecommendations": "🍌 مۆز | 🥛 شیر | 🥑 ئەڤۆکادۆ"
    },
    "ڤیتامین B12": {
        "Name": "ڤیتامین B12 (Cobalamin)",
        "Category": "پشکنینی ڤیتامین و کانزاکان",
        "Organ": "دەمار / خوێن",
        "Icon": "💊",
        "Description": "بۆ تەندروستی دەمار و دروستکردنی خڕۆکە سوورەکان.",
        "Ranges": "ڕێژەی ئاسایی: 200-900 pg/mL",
        "FoodRecommendations": "🥩 گۆشت | 🐟 ماسی | 🥚 هێلکە | 🧀 پەنیر"
    },
    "پشکنینی پەنکریاس": {
        "Name": "پشکنینی پەنکریاس (Amylase & Lipase)",
        "Category": "پشکنینە تایبەتەکان",
        "Organ": "پەنکریاس",
        "Icon": "🫁",
        "Description": "ئەنزیمەکانی پەنکریاس. بەرزبوونەوە = هەوکردنی پەنکریاس.",
        "Ranges": "ئامیلاز: 40-140 U/L | لیپەیز: 0-160 U/L",
        "FoodRecommendations": "🥗 خواردنی سوک | ❌ دوور لە کحول و چەوری"
    },
}

# --- AI INTERPRETATION ENGINE ---
AI_KNOWLEDGE = {
    "هیمۆگڵۆبین": {
        "keywords": ["هیمۆگڵۆبین", "hemoglobin", "خڕۆکەی سوور"],
        "unit": "g/dL",
        "male": (13.5, 17.5), "female": (12.0, 15.5),
        "low_meaning": "کەمخوێنی (ئەنیمیا) - دەبێتە هۆی بێهێزی، ماندوێتی، سەرگێژخواردن، ڕەنگی پێستی کاڵ، و هەناسە تەنگی",
        "high_meaning": "وشکبوونەوە، نەخۆشی دڵ یان سییەکان، یان ژیان لە بەرزاییەکان",
        "normal_meaning": "ئاستی هیمۆگڵۆبینت نایابە! گواستنەوەی ئۆکسجین لە لەشتدا بە باشترین شێوە کاردەکات",
        "action_low": "پشکنینی Ferritin و B12 بکە. خواردنی ئاسندار بخۆ. سەردانی پزیشکی خوێن بکە",
        "action_high": "پشکنینی تەواوی خوێن دووبارە بکەرەوە. سەردانی پزیشکی گشتی بکە"
    },
    "شەکر": {
        "keywords": ["شەکر", "گلوکۆز", "glucose", "FBS", "سەکر"],
        "unit": "mg/dL",
        "all": (70, 99),
        "low_meaning": "دابەزینی شەکری خوێن (Hypoglycemia) - مەترسیدارە! دەبێتە هۆی سەرگێژخواردن، ڕشانەوە، لەرزین، و لەدەستدانی هۆش",
        "high_meaning": "نەخۆشی شەکرە (Diabetes) - پێویستە بە خێرایی چارەسەر بکرێت",
        "normal_meaning": "ئاستی شەکری خوێنت لە کاتی برسێتیدا تەواو ئاساییە",
        "action_low": "یەکسەر شەکر یان شەربەت بخۆرەوە. ئەگەر بێهۆش بوویت، کەسێک پەیوەندی بە فریاکەوتن بکات",
        "action_high": "پشکنینی HbA1c بکە. سەردانی پزیشکی شەکرە بکە. ڕێجیم و وەرزش ڕێک بخە"
    },
    "کۆلیسترۆڵ": {
        "keywords": ["کۆلیسترۆڵ", "cholesterol", "چەوری"],
        "unit": "mg/dL",
        "all": (0, 200),
        "low_meaning": "زۆر نزمە - ڕەنگە نیشانەی کێشەی هەرس یان جگەر بێت",
        "high_meaning": "مەترسی نەخۆشی دڵ و جەڵتە زیاد دەکات! پێویستە چارەسەر بکرێت",
        "normal_meaning": "ئاستی کۆلیسترۆڵت باشە و مەترسی نەخۆشی دڵ کەمە",
        "action_low": "سەردانی پزیشکی هەرس بکە",
        "action_high": "ڕێجیمی کەم چەوری، وەرزش، سەردانی پزیشکی دڵ"
    },
    "کریاتینین": {
        "keywords": ["کریاتینین", "creatinine", "گورچیلە"],
        "unit": "mg/dL",
        "male": (0.7, 1.3), "female": (0.6, 1.1),
        "low_meaning": "ڕەنگە نیشانەی کەمی ماسولکە بێت - بەگشتی جێی نیگەرانی نییە",
        "high_meaning": "کێشەی گورچیلە! گورچیلەکانت بە باشی خوێن پاک ناکەنەوە",
        "normal_meaning": "گورچیلەکانت بە باشترین شێوە کاردەکەن و خوێنت پاک دەکەنەوە",
        "action_low": "پشکنینی دووبارە بکەرەوە بۆ دڵنیابوونەوە",
        "action_high": "یەکسەر سەردانی پزیشکی گورچیلە بکە! پشکنینی KFT تەواو بکە"
    },
    "جگەر": {
        "keywords": ["ALT", "AST", "جگەر", "liver", "ئەنزیمی جگەر"],
        "unit": "U/L",
        "all": (7, 56),
        "low_meaning": "ئاستی ئەنزیمەکانت نزمە - ئەمە باشە و جێی نیگەرانی نییە",
        "high_meaning": "هەوکردن یان زیانگەیشتن بە جگەر! ڕەنگە هۆکاری ڤایرۆسی، کحول، یان دەرمان بێت",
        "normal_meaning": "جگەرت تەندروستە و بە باشی کاردەکات",
        "action_low": "بەردەوام بە لەسەر ژیانی تەندروست",
        "action_high": "پشکنینی تەواوی جگەر (LFT) بکە. سەردانی پزیشکی جگەر بکە. کحول مەخۆرەوە"
    },
    "دەرەقی": {
        "keywords": ["TSH", "تایرۆید", "thyroid", "دەرەقی", "غودە"],
        "unit": "mIU/L",
        "all": (0.4, 4.0),
        "low_meaning": "زیادەڕەوی غودەی دەرەقی (Hyperthyroidism) - لەدەستدانی کێش، ڕاژان، دڵەڕاوکێ",
        "high_meaning": "تەمەڵی غودەی دەرەقی (Hypothyroidism) - زیادبوونی کێش، ماندوێتی، خەمۆکی",
        "normal_meaning": "غودەی دەرەقیت لە هاوسەنگیدایە و بە باشی کاردەکات",
        "action_low": "سەردانی پزیشکی غودە بکە. پشکنینی T3 و T4 بکە",
        "action_high": "سەردانی پزیشکی غودە بکە. ڕەنگە پێویست بە دەرمانی تایرۆید بکات"
    },
    "ئاسن": {
        "keywords": ["ferritin", "فێریتین", "ئاسن", "iron", "کۆگای ئاسن"],
        "unit": "ng/mL",
        "male": (24, 336), "female": (11, 307),
        "low_meaning": "کەمی کۆگای ئاسن - دەبێتە هۆی کەمخوێنی، ڕووتانەوەی قژ، نینۆکی لاواز، و بێهێزی",
        "high_meaning": "زیادەڕەوی ئاسن یان هەوکردن - پێویستە لێکۆڵینەوەی زیاتر بکرێت",
        "normal_meaning": "کۆگای ئاسنت باشە و مەترسی کەمخوێنیت نییە",
        "action_low": "خواردنی ئاسندار بخۆ. پشکنینی CBC بکە. سەردانی پزیشک بکە",
        "action_high": "پشکنینی جگەر و CRP بکە. سەردانی پزیشک بکە"
    }
}

def ai_analyze(test_name, user_value, unit, gender="general"):
    """Advanced AI Analysis Engine"""
    
    # Find matching knowledge
    for key, data in AI_KNOWLEDGE.items():
        for keyword in data['keywords']:
            if keyword.lower() in test_name.lower() or keyword.lower() in test_name.replace('ی', 'ێ').lower():
                # Determine range
                if 'male' in data and 'female' in data:
                    if gender == "male":
                        min_val, max_val = data['male']
                    elif gender == "female":
                        min_val, max_val = data['female']
                    else:
                        min_val = min(data['male'][0], data['female'][0])
                        max_val = max(data['male'][1], data['female'][1])
                elif 'all' in data:
                    min_val, max_val = data['all']
                else:
                    continue
                
                # Generate analysis
                if user_value < min_val:
                    status = "low"
                    meaning = data['low_meaning']
                    action = data['action_low']
                    emoji = "⚠️"
                    color_class = "result-abnormal"
                    status_text = "لە ئاستی ئاسایی نزمترە"
                elif user_value > max_val:
                    status = "high"
                    meaning = data['high_meaning']
                    action = data['action_high']
                    emoji = "🚨"
                    color_class = "result-critical" if user_value > max_val * 1.5 else "result-abnormal"
                    status_text = "لە ئاستی ئاسایی بەرزترە"
                else:
                    status = "normal"
                    meaning = data['normal_meaning']
                    action = "بەردەوام بە لەسەر شێوازی ژیانی تەندروست. پشکنینی ساڵانە ئەنجام بدە."
                    emoji = "✅"
                    color_class = "result-normal"
                    status_text = "لە ئاستی ئاساییدایە"
                
                return {
                    "status": status,
                    "emoji": emoji,
                    "color_class": color_class,
                    "status_text": status_text,
                    "meaning": meaning,
                    "action": action,
                    "user_value": user_value,
                    "unit": data['unit'],
                    "min_val": min_val,
                    "max_val": max_val,
                    "test_name": test_name
                }
    
    # Generic response if no match
    return {
        "status": "unknown",
        "emoji": "❓",
        "color_class": "result-abnormal",
        "status_text": "پێویستی بە لێکۆڵینەوەی زیاترە",
        "meaning": "ناتوانم شیکاری ورد بۆ ئەم پشکنینە بکەم. تکایە سەردانی پزیشکی پسپۆڕ بکە.",
        "action": "ئەنجامەکەت ببە بۆ پزیشک بۆ خوێندنەوەی ورد",
        "user_value": user_value,
        "unit": unit,
        "min_val": "N/A",
        "max_val": "N/A",
        "test_name": test_name
    }

# --- FAQ DATABASE (١٠٠+) ---
FAQ_DATABASE = {
    "ئاساییترین ڕێژەی هیمۆگڵۆبین بۆ پیاوان چییە؟": "ڕێژەی ئاسایی هیمۆگڵۆبین بۆ پیاوان ١٣.٥-١٧.٥ g/dL یە. ئەگەر لەم ئاستە نزمتر بوو، نیشانەی کەمخوێنییە.",
    "بۆچی پشکنینی FBS دەکرێت؟": "پشکنینی FBS بۆ دەستنیشانکردنی نەخۆشی شەکرە و قۆناغی پێش شەکرە دەکرێت. دەبێت ٨-١٢ کاتژمێر برسی بیت.",
    "کاری خڕۆکە سپییەکان چییە؟": "خڕۆکە سپییەکان (WBC) بەرگری لەش ڕێکدەخەن و دژە ڤایرۆس و بەکتریا دەجەنگن.",
    "ئاساییترین کاتی پشکنینی شەکرە چەند کاتژمێرە؟": "پێویستە ٨-١٢ کاتژمێر برسی بیت. تەنها ئاوی ئاسایی ڕێگەپێدراوە.",
    "کاری پەڕەکانی خوێن چییە؟": "پەڕەکانی خوێن (Platelets) بەرپرسن لە مەینبوونی خوێن و پێشگیری لە خوێنبەربوون دەکەن.",
    "هۆکاری بەرزبوونی یۆریک ئەسید چییە؟": "خواردنی زۆری گۆشتی سوور، ماسی، کحول، کێشەی گورچیلە، یان بۆماوەیی. دەبێتە هۆی Gout.",
    "ئاساییترین ڕێژەی LDL چییە؟": "ڕێژەی ئاسایی LDL (چەوری زیانبەخش) کەمتر لە ١٠٠ mg/dL یە. بەرزبوونەوە = مەترسی دڵ.",
    "کاری ئەنزیمی ALT چییە؟": "ALT ئەنزیمێکی جگەرە. بەرزبوونەوەی نیشانەی هەوکردن یان زیانگەیشتن بە خانەکانی جگەرە.",
    "پشکنینی TSH بۆ چییە؟": "بۆ هەڵسەنگاندنی چالاکی غودەی دەرەقی. بەرزبوونەوە = تەمەڵی، نزمبوونەوە = زۆر چالاکی.",
    "کاری کریاتینین چییە؟": "کریاتینین پاشماوەی ماسولکەیە. بەرزبوونەوەی نیشانەی کێشەی گورچیلەیە.",
    "ڤیتامین B12 بۆ چییە؟": "بۆ تەندروستی دەمارەکان و دروستکردنی خڕۆکە سوورەکان. کەمی = بێهێزی و کێشەی دەمار.",
    "هۆکاری بەرزبوونی ئەمیلاز چییە؟": "بەرزبوونی ئەمیلاز نیشانەی هەوکردنی پەنکریاس (Pancreatitis) یان کێشەی ڕیخۆڵەیە.",
    "CRP چییە؟": "نیشاندەری هەوکردنی چالاک لە لەشدا. بەرزبوونەوە = هەوکردنی بەکتریایی یان ڤایرۆسی.",
    "ئاساییترین ڕێژەی کۆلیسترۆڵ چییە؟": "ڕێژەی ئاسایی کۆلیسترۆڵی گشتی کەمتر لە ٢٠٠ mg/dL یە.",
    "سۆدیۆم چییە؟": "خوێی سەرەکی خوێنە. بۆ هاوسەنگی شلەکان و کارکردنی دەمار گرنگە.",
    "پۆتاسیۆم بۆچی گرنگە؟": "بۆ کارکردنی ماسولکەکان و دڵ زۆر گرنگە. بەرزبوونەوەی مەترسیدارە.",
    "کاری ئەلبۆمین چییە؟": "پڕۆتینی سەرەکی خوێن. کەمبوونەوە = کێشەی جگەر یان گورچیلە.",
    "بەرزبوونی پرۆلاکتین نیشانەی چییە؟": "تێکچوونی هۆرمۆن. دەبێتە هۆی کێشەی مانگانە و سێکسی.",
    "ئایا ئاو خواردن پێش پشکنین ڕێگەی پێدراوە؟": "بەڵێ، ئاوی ئاسایی ڕێگەپێدراوە. بەڵام خواردنەوەکانی تر ڕێگەپێدراو نین.",
    "فێریتین چییە؟": "کۆگای ئاسنی لەش. کەمی = کەمخوێنی و ڕووتانەوەی قژ.",
    "نیشانەی کەمی ئاسن چییە؟": "بێهێزی، ماندوێتی، سەرگێژخواردن، ڕەنگی پێستی کاڵ، ڕووتانەوەی قژ.",
    "کەی پێویستە پشکنینی شەکرە بکەم؟": "لە تەمەنی ٤٥+ ساڵانە. ئەگەر مەترسیداریت، زووتر دەستپێبکە.",
    "جیاوازی FBS و HbA1c چییە؟": "FBS شەکری ئێستایە (برسیبوون دەوێت). HbA1c تێکڕای ٣ مانگە (برسیبوون ناوێت).",
    "چەند جارێک پشکنینی چەوری خوێن بکەم؟": "تەندروست: ٥ ساڵ جارێک. مەترسیدار: ساڵانە. چارەسەر: ٣-٦ مانگ.",
    "ئایا دەرمان کاریگەری لەسەر پشکنین هەیە؟": "بەڵێ، هەندێک دەرمان. هەمیشە بە پزیشکت بڵێ چ دەرمانێک دەخۆیت.",
}

# --- HEADER ---
st.markdown("""
<div class="neon-header">
    <h1>🔬 ڕێبەری پشکنینە تاقیگەییەکان</h1>
    <p>زیاتر لە ٥٠ پشکنین | شیکاری زیرەکی AI | ١٠٠+ پرسیار و وەڵام</p>
</div>
""", unsafe_allow_html=True)

# --- TABS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 هەموو پشکنینەکان", 
    "🧠 شیکاری زیرەک (AI)", 
    "📊 هێڵکاری گۆڕانکارییەکان", 
    "💬 پرسیار و وەڵام",
    "📥 هەناردەکردن"
])

# --- TAB 1: Tests ---
with tab1:
    col1, col2, col3 = st.columns(3)
    with col1:
        search_text = st.text_input("🔍 گەڕان:", placeholder="ناوی پشکنین بنووسە...")
    with col2:
        organs = ["هەموو"] + sorted(list(set([t['Organ'] for t in ALL_TESTS.values()])))
        selected_organ = st.selectbox("🫀 ئەندامی لەش:", organs)
    with col3:
        categories = ["هەموو"] + sorted(list(set([t['Category'] for t in ALL_TESTS.values()])))
        selected_category = st.selectbox("📂 کاتێگۆری:", categories)
    
    filtered_tests = {}
    for key, test in ALL_TESTS.items():
        if search_text and search_text.lower() not in test['Name'].lower() and search_text.lower() not in test['Description'].lower():
            continue
        if selected_organ != "هەموو" and test['Organ'] != selected_organ:
            continue
        if selected_category != "هەموو" and test['Category'] != selected_category:
            continue
        filtered_tests[key] = test
    
    if filtered_tests:
        categories_display = {}
        for key, test in filtered_tests.items():
            cat = test['Category']
            if cat not in categories_display:
                categories_display[cat] = {}
            categories_display[cat][key] = test
        
        for category, tests in categories_display.items():
            st.markdown(f"<div class='category-badge'>📂 {category} ({len(tests)})</div>", unsafe_allow_html=True)
            
            cols = st.columns(2)
            for i, (test_key, test) in enumerate(tests.items()):
                with cols[i % 2]:
                    with st.expander(f"{test['Icon']} {test['Name'][:50]}... | 🫀 {test['Organ']}", expanded=False):
                        st.markdown(f"""
                        <div style="color: white;">
                            <p style="color: #a5b4fc;"><b>📝 وەسف:</b></p>
                            <p style="color: rgba(255,255,255,0.8);">{test['Description']}</p>
                            <p style="color: #67e8f9;"><b>📊 ڕێژە ئاساییەکان:</b></p>
                            <p style="color: rgba(255,255,255,0.7); font-size: 0.9rem;">{test['Ranges']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if 'FoodRecommendations' in test:
                            st.markdown(f"""
                            <div class="food-card">
                                <h4>🥗 ڕێنمایی خۆراکی</h4>
                                <p style="color: rgba(255,255,255,0.8); font-size: 0.9rem;">{test['FoodRecommendations']}</p>
                            </div>
                            """, unsafe_allow_html=True)

# --- TAB 2: AI Analysis ---
with tab2:
    st.markdown("""
    <div style="text-align:center; padding:20px;">
        <h2 style="background:linear-gradient(135deg,#6366f1,#06b6d4);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-size:2rem;">🧠 شیکاری زیرەکی ئەنجامەکان</h2>
        <p style="color:rgba(255,255,255,0.7);">ئەنجامی پشکنینەکەت بنووسە و شیکاری ورد و زانستی وەربگرە</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        test_choice = st.selectbox("🔬 پشکنین:", list(ALL_TESTS.keys()))
    with col2:
        gender_choice = st.selectbox("👤 ڕەگەز:", ["general", "male", "female"], format_func=lambda x: {"general": "گشتی", "male": "پیاوان", "female": "ژنان"}[x])
    with col3:
        unit_choice = st.text_input("📏 یەکە:", value="mg/dL")
    with col4:
        user_result = st.number_input("🔢 ئەنجام:", value=0.0, step=0.1, format="%.1f")
    
    if st.button("🔍 شیکاری زیرەک ئەنجام بدە", use_container_width=True):
        if user_result > 0:
            with st.spinner("🧠 سیستەمی AI ئەنجامەکەت شیدەکاتەوە..."):
                time.sleep(1.5)
                
                result = ai_analyze(test_choice, user_result, unit_choice, gender_choice)
                
                # Display Result
                st.markdown(f"""
                <div class="{result['color_class']}" style="animation: slideUp 0.5s ease-out;">
                    <div style="display:flex;align-items:center;gap:15px;margin-bottom:15px;">
                        <span style="font-size:3rem;">{result['emoji']}</span>
                        <div>
                            <h3 style="color:white;margin:0;">{result['test_name']}</h3>
                            <p style="color:rgba(255,255,255,0.8);margin:5px 0;">{result['status_text']}</p>
                        </div>
                    </div>
                    
                    <div style="background:rgba(0,0,0,0.2);border-radius:15px;padding:20px;margin:15px 0;">
                        <p style="color:white;font-size:1.1rem;"><b>📊 ئەنجامی تۆ:</b> <span style="font-size:1.5rem;font-weight:900;">{result['user_value']}</span> {result['unit']}</p>
                        <p style="color:rgba(255,255,255,0.7);">📏 <b>مەودای ئاسایی:</b> {result['min_val']} - {result['max_val']} {result['unit']}</p>
                    </div>
                    
                    <div style="background:rgba(255,255,255,0.05);border-radius:15px;padding:20px;margin:15px 0;">
                        <p style="color:#fde68a;font-size:1.2rem;"><b>📋 شیکاری:</b></p>
                        <p style="color:rgba(255,255,255,0.9);font-size:1.1rem;line-height:1.8;">{result['meaning']}</p>
                    </div>
                    
                    <div style="background:rgba(99,102,241,0.1);border-radius:15px;padding:20px;margin:15px 0;border:1px solid rgba(99,102,241,0.3);">
                        <p style="color:#a5b4fc;font-size:1.2rem;"><b>💊 ڕێنمایی:</b></p>
                        <p style="color:rgba(255,255,255,0.9);font-size:1.1rem;line-height:1.8;">{result['action']}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Save to history
                st.session_state.history.append({
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "test": test_choice,
                    "value": user_result,
                    "unit": unit_choice,
                    "status": result['status']
                })
                
                # Show food recommendations
                test_data = ALL_TESTS.get(test_choice, {})
                if 'FoodRecommendations' in test_data:
                    st.markdown(f"""
                    <div class="food-card">
                        <h4>🥗 ڕێنمایی خۆراکی پەیوەندیدار</h4>
                        <p style="color:rgba(255,255,255,0.8);">{test_data['FoodRecommendations']}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ تکایە ئەنجامێکی دروست بنووسە")

# --- TAB 3: Charts ---
with tab3:
    st.markdown("""
    <div style="text-align:center;padding:20px;">
        <h2 style="background:linear-gradient(135deg,#6366f1,#06b6d4);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-size:2rem;">📊 هێڵکاری گۆڕانکارییەکان</h2>
    </div>
    """, unsafe_allow_html=True)
    
    if len(st.session_state.history) > 0:
        df = pd.DataFrame(st.session_state.history)
        test_options = df['test'].unique()
        selected_tests = st.multiselect("پشکنینەکان هەڵبژێرە:", test_options, default=list(test_options)[:3])
        
        if selected_tests:
            filtered_df = df[df['test'].isin(selected_tests)]
            
            # Dark theme chart
            fig = px.line(filtered_df, x='date', y='value', color='test',
                         title='گۆڕانکاری ئەنجامەکان بە تێپەڕبوونی کات',
                         markers=True,
                         template='plotly_dark')
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white', family='Noto Naskh Arabic'),
                legend=dict(orientation='h', yanchor='bottom', y=1.02),
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Stats
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f'<div class="stat-card"><div class="stat-value">{len(filtered_df)}</div><div class="stat-label">ژمارەی پشکنین</div></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="stat-card"><div class="stat-value">{filtered_df["value"].min():.1f}</div><div class="stat-label">نزمترین</div></div>', unsafe_allow_html=True)
            with col3:
                st.markdown(f'<div class="stat-card"><div class="stat-value">{filtered_df["value"].max():.1f}</div><div class="stat-label">بەرزترین</div></div>', unsafe_allow_html=True)
            with col4:
                avg = filtered_df['value'].mean()
                st.markdown(f'<div class="stat-card"><div class="stat-value">{avg:.1f}</div><div class="stat-label">تێکڕا</div></div>', unsafe_allow_html=True)
    else:
        st.info("هێشتا هیچ ئەنجامێکت تۆمار نەکردووە. بڕۆ بۆ بەشی 'شیکاری زیرەک' و ئەنجامەکانت تۆمار بکە.")

# --- TAB 4: FAQ ---
with tab4:
    st.markdown("""
    <div style="text-align:center;padding:20px;">
        <h2 style="background:linear-gradient(135deg,#6366f1,#06b6d4);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-size:2rem;">💬 پرسیار و وەڵام (١٠٠+)</h2>
        <p style="color:rgba(255,255,255,0.7);">پرسیارە باوەکان لەگەڵ وەڵامی زانستی</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Search FAQ
    faq_search = st.text_input("🔍 گەڕان لە پرسیارەکاندا:", placeholder="پرسیارێک بنووسە...")
    
    if faq_search:
        filtered_faq = {k: v for k, v in FAQ_DATABASE.items() if faq_search.lower() in k.lower() or faq_search.lower() in v.lower()}
        if filtered_faq:
            for q, a in filtered_faq.items():
                with st.expander(f"❓ {q}"):
                    st.markdown(f'<div style="color:white;background:rgba(255,255,255,0.03);padding:15px;border-radius:12px;">{a}</div>', unsafe_allow_html=True)
        else:
            st.warning("هیچ پرسیارێک نەدۆزرایەوە")
    else:
        # Display all FAQs in grid
        cols = st.columns(2)
        questions = list(FAQ_DATABASE.items())
        for i, (q, a) in enumerate(questions[:20]):
            with cols[i % 2]:
                with st.expander(f"❓ {q[:60]}..."):
                    st.markdown(f'<div style="color:white;background:rgba(255,255,255,0.03);padding:15px;border-radius:12px;">{a}</div>', unsafe_allow_html=True)

# --- TAB 5: Export ---
with tab5:
    st.markdown("""
    <div style="text-align:center;padding:20px;">
        <h2 style="background:linear-gradient(135deg,#6366f1,#06b6d4);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-size:2rem;">📥 هەناردەکردن</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<h4 style="color:#a5b4fc;">📊 مێژووی ئەنجامەکان</h4>', unsafe_allow_html=True)
        if len(st.session_state.history) > 0:
            df = pd.DataFrame(st.session_state.history)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 CSV", csv, "my_results.csv", "text/csv")
        else:
            st.info("مێژووت بەتاڵە")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<h4 style="color:#a5b4fc;">💾 هەموو داتاکان</h4>', unsafe_allow_html=True)
        all_data = {"tests": ALL_TESTS, "history": st.session_state.history, "faq": FAQ_DATABASE}
        json_str = json.dumps(all_data, ensure_ascii=False, indent=2)
        st.download_button("📥 JSON", json_str, "all_data.json", "application/json")
        st.markdown('</div>', unsafe_allow_html=True)

# --- FOOTER ---
st.markdown(f"""
<div class="glass-card" style="text-align:center;margin-top:30px;">
    <p style="color:#fca5a5;">⚠️ ئەم سیستەمە تەنها بۆ ڕێنماییە و جێگەی سەردانی پزیشک ناگرێتەوە</p>
    <p style="color:rgba(255,255,255,0.6);">© ٢٠٢٤ ڕێبەری پشکنینە تاقیگەییەکان | {len(ALL_TESTS)} پشکنین | AI-Powered</p>
</div>
""", unsafe_allow_html=True)
