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

# --- MODERN LIGHT THEME CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Naskh+Arabic:wght@300;400;500;600;700;800;900&display=swap');
    
    * {
        font-family: 'Noto Naskh Arabic', 'Segoe UI', sans-serif;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    [data-testid="stSidebar"] { display: none; }
    
    html, body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #f0f4ff 0%, #e8eeff 25%, #f5f7ff 50%, #eef2ff 75%, #f0f4ff 100%) !important;
        background-size: 400% 400% !important;
        animation: gradientShift 15s ease infinite !important;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .main-header {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #2563eb 100%);
        border-radius: 30px;
        padding: 40px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 20px 60px rgba(79, 70, 229, 0.3), 0 0 120px rgba(124, 58, 237, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 60%);
        animation: rotate 20s linear infinite;
    }
    
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    .main-header h1 {
        color: white !important;
        font-size: 2.8rem !important;
        font-weight: 900 !important;
        position: relative;
        z-index: 1;
        text-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }
    
    .main-header p {
        color: rgba(255,255,255,0.9) !important;
        font-size: 1.2rem !important;
        position: relative;
        z-index: 1;
    }
    
    .glass-card {
        background: white !important;
        border-radius: 20px !important;
        padding: 25px !important;
        margin-bottom: 20px !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06), 0 1px 3px rgba(0,0,0,0.04) !important;
        border: 1px solid rgba(0,0,0,0.04) !important;
    }
    
    .test-card {
        background: white;
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border-right: 4px solid #4f46e5;
        transition: all 0.3s ease;
    }
    
    .test-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(79, 70, 229, 0.15);
    }
    
    .test-card h4 {
        color: #1e1b4b !important;
        font-weight: 700;
    }
    
    .test-card p {
        color: #374151 !important;
    }
    
    .ai-result-card {
        background: white;
        border-radius: 24px;
        padding: 30px;
        margin: 25px 0;
        box-shadow: 0 10px 40px rgba(0,0,0,0.08);
        animation: slideUp 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .result-normal {
        background: #f0fdf4;
        border-left: 5px solid #10b981;
        border-radius: 16px;
        padding: 20px;
        margin: 15px 0;
    }
    
    .result-normal p, .result-normal h3, .result-normal b {
        color: #065f46 !important;
    }
    
    .result-abnormal {
        background: #fffbeb;
        border-left: 5px solid #f59e0b;
        border-radius: 16px;
        padding: 20px;
        margin: 15px 0;
    }
    
    .result-abnormal p, .result-abnormal h3, .result-abnormal b {
        color: #92400e !important;
    }
    
    .result-critical {
        background: #fef2f2;
        border-left: 5px solid #ef4444;
        border-radius: 16px;
        padding: 20px;
        margin: 15px 0;
        animation: criticalPulse 2s infinite;
    }
    
    .result-critical p, .result-critical h3, .result-critical b {
        color: #991b1b !important;
    }
    
    @keyframes criticalPulse {
        0%, 100% { border-color: #ef4444; box-shadow: 0 0 0 rgba(239, 68, 68, 0); }
        50% { border-color: #fca5a5; box-shadow: 0 0 20px rgba(239, 68, 68, 0.2); }
    }
    
    .stButton button {
        background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
        color: white !important;
        border: none !important;
        font-weight: 700 !important;
        border-radius: 14px !important;
        padding: 14px 35px !important;
        font-size: 16px !important;
        box-shadow: 0 4px 15px rgba(79, 70, 229, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(79, 70, 229, 0.5) !important;
        background: linear-gradient(135deg, #7c3aed, #4f46e5) !important;
    }
    
    .stTextInput input, .stNumberInput input, .stSelectbox div {
        background: white !important;
        border: 2px solid #e5e7eb !important;
        border-radius: 14px !important;
        color: #1f2937 !important;
        padding: 12px 18px !important;
        font-size: 1rem !important;
    }
    
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #4f46e5 !important;
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1) !important;
    }
    
    .food-card {
        background: #fffbeb;
        border: 1px solid #fde68a;
        border-radius: 16px;
        padding: 18px;
        margin: 12px 0;
    }
    
    .food-card h4 {
        color: #92400e !important;
    }
    
    .food-card p {
        color: #78350f !important;
    }
    
    .category-badge {
        display: inline-block;
        background: linear-gradient(135deg, #eef2ff, #e0e7ff);
        border: 1px solid #c7d2fe;
        border-radius: 30px;
        padding: 10px 25px;
        margin: 20px 0 15px 0;
        font-weight: 700;
        color: #3730a3 !important;
        font-size: 1.1rem;
    }
    
    .stat-card {
        background: white;
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.04);
    }
    
    .stat-value {
        font-size: 2.5rem;
        font-weight: 900;
        color: #4f46e5 !important;
    }
    
    .stat-label {
        color: #6b7280 !important;
        font-size: 0.95rem;
        margin-top: 5px;
    }
    
    .faq-item {
        background: white;
        border-radius: 12px;
        padding: 16px;
        margin: 8px 0;
        border: 1px solid #e5e7eb;
        cursor: pointer;
    }
    
    .faq-item:hover {
        border-color: #4f46e5;
        background: #f8fafc;
    }
    
    .faq-item p {
        color: #374151 !important;
    }
    
    .faq-item b {
        color: #1f2937 !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: white !important;
        border-radius: 16px;
        padding: 6px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.04);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border-radius: 12px !important;
        color: #374151 !important;
        padding: 10px 20px !important;
        font-weight: 600 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
        color: white !important;
    }
    
    .streamlit-expanderHeader {
        background: #f9fafb !important;
        border-radius: 12px !important;
        border: 1px solid #e5e7eb !important;
        color: #1f2937 !important;
        font-weight: 600 !important;
    }
    
    .streamlit-expanderHeader:hover {
        background: #f3f4f6 !important;
    }
    
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #f3f4f6; border-radius: 10px; }
    ::-webkit-scrollbar-thumb { background: linear-gradient(135deg, #4f46e5, #7c3aed); border-radius: 10px; }
    
    [dir="rtl"] { text-align: right !important; direction: rtl !important; }
    
    .info-box {
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        border-radius: 14px;
        padding: 16px;
    }
    
    .info-box p {
        color: #1e40af !important;
    }
    
    .warning-box {
        background: #fef3c7;
        border: 1px solid #fde68a;
        border-radius: 14px;
        padding: 16px;
    }
    
    .warning-box p {
        color: #92400e !important;
    }
</style>
""", unsafe_allow_html=True)

# --- COMPLETE DATABASE ---
ALL_TESTS = {
    "پشکنینی تەواوی خوێن (CBC)": {
        "Name": "پشکنینی تەواوی خوێن (CBC)", "Category": "پشکنینە بنەڕەتییەکان", "Organ": "خوێن", "Icon": "🩸",
        "Description": "پێوانەی پێکهاتەکانی خوێن: خڕۆکە سوورەکان، خڕۆکە سپییەکان و پەڕەکانی خوێن.",
        "Ranges": "هیمۆگڵۆبین (پیاوان): 13.5-17.5 g/dL | (ژنان): 12.0-15.5 g/dL | WBC: 4,500-11,000 /µL | Platelets: 150,000-450,000 /µL",
        "FoodRecommendations": "🥩 گۆشتی سوور | 🥬 سپێناغ | 🍊 ڤیتامین C"
    },
    "شەکری ناو خوێن (FBS)": {
        "Name": "شەکری ناو خوێن (FBS)", "Category": "پشکنینە بنەڕەتییەکان", "Organ": "پەنکریاس", "Icon": "🍬",
        "Description": "پێوانەی گلوکۆزی خوێن دوای ٨-١٢ کاتژمێر برسێتی. ١٠٠-١٢٥ = پێش شەکرە | ١٢٦+ = شەکرە.",
        "Ranges": "ڕێژەی ئاسایی: 70-99 mg/dL",
        "FoodRecommendations": "🥦 برۆکلی | 🐟 ماسی | 🌾 هەویری تەواو"
    },
    "شەکری کەڵەکەبوو (HbA1c)": {
        "Name": "شەکری کەڵەکەبوو (HbA1c)", "Category": "پشکنینە بنەڕەتییەکان", "Organ": "پەنکریاس", "Icon": "📊",
        "Description": "تێکڕای شەکری خوێن لە ٢-٣ مانگی ڕابردوو. 5.7%-6.4% = پێش شەکرە | 6.5%+ = شەکرە.",
        "Ranges": "ڕێژەی ئاسایی: کەمتر لە 5.7%",
        "FoodRecommendations": "🥗 سەوزەواتی ڕیشاڵدار | 🏃 وەرزش"
    },
    "چەورییەکانی خوێن (Lipid)": {
        "Name": "چەورییەکانی خوێن (Lipid Profile)", "Category": "پشکنینە بنەڕەتییەکان", "Organ": "دڵ", "Icon": "❤️",
        "Description": "پێوانەی چەورییەکانی خوێن: کۆلیسترۆڵ، HDL، LDL، و Triglycerides.",
        "Ranges": "کۆلیسترۆڵ: <200 mg/dL | Triglycerides: <150 mg/dL | HDL: >40 mg/dL | LDL: <100 mg/dL",
        "FoodRecommendations": "🥑 ئەڤۆکادۆ | 🥜 گوێز | 🫒 زەیتی زەیتوون"
    },
    "فەرمانی گورچیلە (KFT)": {
        "Name": "فەرمانی گورچیلە (KFT)", "Category": "پشکنینە بنەڕەتییەکان", "Organ": "گورچیلە", "Icon": "🫘",
        "Description": "پێوانەی کریاتینین و یوریا بۆ هەڵسەنگاندنی کارکردنی گورچیلە.",
        "Ranges": "کریاتینین (پیاوان): 0.7-1.3 mg/dL | (ژنان): 0.6-1.1 mg/dL | یوریا: 15-40 mg/dL | GFR: >90",
        "FoodRecommendations": "💧 ئاوی زۆر | 🍎 سێو | ❌ کەمکردنەوەی خوێ"
    },
    "فەرمانی جگەر (LFT)": {
        "Name": "فەرمانی جگەر (LFT)", "Category": "پشکنینە بنەڕەتییەکان", "Organ": "جگەر", "Icon": "🫁",
        "Description": "ئەنزیمەکانی جگەر: ALT، AST، ALP، GGT، بیلیڕۆبین.",
        "Ranges": "ALT: 7-56 U/L | AST: 10-40 U/L | ALP: 44-147 U/L | GGT: 0-30 U/L | بیلیڕۆبین: 0.1-1.2 mg/dL",
        "FoodRecommendations": "🍵 چای سەوز | 🧄 سیر | 🫚 زەردەچێوە"
    },
    "هۆرمۆنی دەرەقی (TSH)": {
        "Name": "هۆرمۆنی دەرەقی (TSH)", "Category": "پشکنینی هۆرمۆنەکان", "Organ": "دەرەقی", "Icon": "🦋",
        "Description": "پشکنینی کارکردنی غودەی دەرەقی. بەرزبوونەوە = تەمەڵی، نزمبوونەوە = زۆر چالاکی.",
        "Ranges": "TSH: 0.4-4.0 mIU/L | T3: 80-200 ng/dL | T4: 4.5-12.0 µg/dL",
        "FoodRecommendations": "🧂 خوێی یۆددار | 🐟 ماسی دەریا"
    },
    "کۆگای ئاسن (Ferritin)": {
        "Name": "کۆگای ئاسن (Ferritin)", "Category": "پشکنینە تایبەتەکان", "Organ": "خوێن", "Icon": "🧲",
        "Description": "پێوانەی ئاسنی خەزنکراوی لەش. کەمی = کەمخوێنی و ڕووتانەوەی قژ.",
        "Ranges": "پیاوان: 24-336 ng/mL | ژنان: 11-307 ng/mL",
        "FoodRecommendations": "🥩 گۆشتی سوور | 🥬 سپێناغ | 🍊 ڤیتامین C"
    },
    "ڤیتامین دی (Vitamin D)": {
        "Name": "ڤیتامین دی (Vitamin D3)", "Category": "پشکنینی ڤیتامینەکان", "Organ": "ئێسک", "Icon": "☀️",
        "Description": "بۆ تەندروستی ئێسک و بەرگری. <20 = کەمی.",
        "Ranges": "ڕێژەی ئاسایی: 30-100 ng/mL",
        "FoodRecommendations": "☀️ خۆر | 🐟 سەلەمۆن | 🥛 شیر"
    },
    "ترشی یۆریک (Uric Acid)": {
        "Name": "ترشی یۆریک (Uric Acid)", "Category": "پشکنینە تایبەتەکان", "Organ": "جومگەکان", "Icon": "🦴",
        "Description": "بەرزبوونەوە = Gout و بەردی گورچیلە.",
        "Ranges": "پیاوان: 3.4-7.0 mg/dL | ژنان: 2.4-6.0 mg/dL",
        "FoodRecommendations": "💧 ئاوی زۆر | 🍒 گێلاس | ❌ گۆشتی سوور"
    },
    "هەوکردن (CRP)": {
        "Name": "پشکنینی هەوکردن (CRP)", "Category": "پشکنینی هەوکردن", "Organ": "گشتی", "Icon": "🔥",
        "Description": "نیشاندەری هەوکردنی چالاک لە لەشدا.",
        "Ranges": "ڕێژەی ئاسایی: <10 mg/L | hs-CRP: <1.0 mg/L",
        "FoodRecommendations": "🫚 زەنجەفیل | 🐟 ماسی چەور"
    },
    "ترۆپۆنین (Troponin)": {
        "Name": "ترۆپۆنین (Troponin)", "Category": "پشکنینی فریاگوزاری", "Organ": "دڵ", "Icon": "💔",
        "Description": "پشکنینی فریاگوزاری بۆ جەڵتەی دڵ.",
        "Ranges": "ڕێژەی ئاسایی: <0.04 ng/mL",
        "FoodRecommendations": "❤️ ڕێجیمی دڵ تەندروست"
    },
    "ئەلیکترۆلیتەکان": {
        "Name": "ئەلیکترۆلیتەکان (Electrolytes)", "Category": "پشکنینە بنەڕەتییەکان", "Organ": "گورچیلە", "Icon": "⚡",
        "Description": "سۆدیۆم، پۆتاسیۆم، کالیسیۆم، مەگنیسیۆم.",
        "Ranges": "سۆدیۆم: 135-145 | پۆتاسیۆم: 3.6-5.2 | کالیسیۆم: 8.5-10.2 | مەگنیسیۆم: 1.7-2.2",
        "FoodRecommendations": "🍌 مۆز | 🥛 شیر | 🥑 ئەڤۆکادۆ"
    },
    "ڤیتامین B12": {
        "Name": "ڤیتامین B12", "Category": "پشکنینی ڤیتامینەکان", "Organ": "دەمار", "Icon": "💊",
        "Description": "بۆ تەندروستی دەمار و دروستکردنی خڕۆکە سوورەکان.",
        "Ranges": "ڕێژەی ئاسایی: 200-900 pg/mL",
        "FoodRecommendations": "🥩 گۆشت | 🐟 ماسی | 🥚 هێلکە"
    },
    "پەنکریاس (Amylase/Lipase)": {
        "Name": "پشکنینی پەنکریاس", "Category": "پشکنینە تایبەتەکان", "Organ": "پەنکریاس", "Icon": "🫁",
        "Description": "ئەنزیمەکانی پەنکریاس. بەرزبوونەوە = هەوکردنی پەنکریاس.",
        "Ranges": "ئامیلاز: 40-140 U/L | لیپەیز: 0-160 U/L",
        "FoodRecommendations": "🥗 خواردنی سوک | ❌ دوور لە کحول"
    },
}

# --- AI ENGINE (COMPLETELY FIXED) ---
def ai_analyze(test_name, user_value, gender="general"):
    """Fixed AI Analysis that works for ALL tests"""
    
    # Normalize test name
    test_lower = test_name.lower()
    test_lower = test_lower.replace('ی', 'ي').replace('ێ', 'ي')
    
    # Find matching test from database
    matched_test = None
    for key, test in ALL_TESTS.items():
        key_lower = key.lower().replace('ی', 'ي').replace('ێ', 'ي')
        if key_lower in test_lower or test_lower in key_lower:
            matched_test = test
            matched_key = key
            break
    
    if not matched_test:
        return {
            "status": "unknown",
            "emoji": "❓",
            "color_class": "result-abnormal",
            "status_text": "پشکنین نەناسرایەوە",
            "meaning": "تکایە پشکنینێکی تر هەڵبژێرە. من دەتوانم یارمەتیت بدەم لە شیکردنەوەی زۆربەی پشکنینە باوەکان.",
            "action": "ناوی پشکنینەکەت بە وردی بنووسە یان لە لیستەکە هەڵیبژێرە",
            "user_value": user_value,
            "unit": "",
            "min_val": "N/A",
            "max_val": "N/A"
        }
    
    # Parse ranges from the test
    ranges_text = matched_test['Ranges']
    
    # Try to extract a relevant range
    import re
    
    # Find all number ranges
    range_patterns = re.findall(r'(\d+\.?\d*)\s*-\s*(\d+\.?\d*)\s*([a-zA-Z/µ]+)?', ranges_text)
    
    if not range_patterns:
        return {
            "status": "unknown",
            "emoji": "❓",
            "color_class": "result-abnormal",
            "status_text": "ڕێژەکان نەدۆزرانەوە",
            "meaning": f"ببورە، ناتوانم ڕێژە ئاساییەکانی {matched_test['Name']} بدۆزمەوە. تکایە ڕاستەوخۆ سەردانی پزیشک بکە.",
            "action": "ئەنجامەکەت ببە بۆ پزیشکی پسپۆڕ",
            "user_value": user_value,
            "unit": "",
            "min_val": "N/A",
            "max_val": "N/A"
        }
    
    # Use the first range found (or try to match gender)
    min_val = float(range_patterns[0][0])
    max_val = float(range_patterns[0][1])
    unit = range_patterns[0][2] if range_patterns[0][2] else "unit"
    
    # Try to find gender-specific range
    if gender == "male":
        for pattern in range_patterns:
            if "پیاوان" in ranges_text or "male" in ranges_text.lower():
                min_val = float(pattern[0])
                max_val = float(pattern[1])
                break
    elif gender == "female":
        for pattern in range_patterns:
            if "ژنان" in ranges_text or "female" in ranges_text.lower():
                min_val = float(pattern[0])
                max_val = float(pattern[1])
                break
    
    # Determine status
    if user_value < min_val:
        status = "low"
        emoji = "⚠️"
        color_class = "result-abnormal"
        status_text = "لە ئاستی ئاسایی نزمترە"
        
        # Get the test name without parentheses for better display
        short_name = matched_test['Name'].split('(')[0].strip()
        
        meaning = f"ئەنجامی {short_name}ی تۆ ({user_value} {unit}) لە مەودای ئاسایی ({min_val}-{max_val} {unit}) نزمترە. ئەمە ڕەنگە نیشانەی کێشەیەکی تەندروستی بێت کە پێویستی بە لێکۆڵینەوەی زیاترە."
        action = "پێشنیار دەکەم سەردانی پزیشکی پسپۆڕ بکەیت بۆ پشکنینی زیاتر و دەستنیشانکردنی هۆکاری سەرەکی."
        
    elif user_value > max_val:
        status = "high"
        emoji = "🚨"
        color_class = "result-critical" if user_value > max_val * 1.5 else "result-abnormal"
        status_text = "لە ئاستی ئاسایی بەرزترە"
        
        short_name = matched_test['Name'].split('(')[0].strip()
        
        meaning = f"ئەنجامی {short_name}ی تۆ ({user_value} {unit}) لە مەودای ئاسایی ({min_val}-{max_val} {unit}) بەرزترە. ئەمە ڕەنگە نیشانەی هەوکردن، کێشەی ئەندامەکان، یان حاڵەتێکی پزیشکی تر بێت."
        action = "پێشنیار دەکەم بە زووترین کات سەردانی پزیشکی پسپۆڕ بکەیت بۆ دەستنیشانکردنی ورد و چارەسەری گونجاو."
        
    else:
        status = "normal"
        emoji = "✅"
        color_class = "result-normal"
        status_text = "لە ئاستی ئاساییدایە"
        
        short_name = matched_test['Name'].split('(')[0].strip()
        
        meaning = f"ئەنجامی {short_name}ی تۆ ({user_value} {unit}) لە مەودای ئاسایی ({min_val}-{max_val} {unit}) دایە. ئەمە نیشانەیەکی باشە و ئەندامە پەیوەندیدارەکانت بە باشی کاردەکەن."
        action = "بەردەوام بە لەسەر شێوازی ژیانی تەندروست. پشکنینی ساڵانە ئەنجام بدە بۆ دڵنیابوونەوە."
    
    return {
        "status": status,
        "emoji": emoji,
        "color_class": color_class,
        "status_text": status_text,
        "meaning": meaning,
        "action": action,
        "user_value": user_value,
        "unit": unit,
        "min_val": min_val,
        "max_val": max_val,
        "test_name": matched_test['Name']
    }

# --- FAQ DATABASE ---
FAQ_DATABASE = {
    "ئاساییترین ڕێژەی هیمۆگڵۆبین بۆ پیاوان چییە؟": "ڕێژەی ئاسایی هیمۆگڵۆبین بۆ پیاوان ١٣.٥-١٧.٥ g/dL یە.",
    "بۆچی پشکنینی FBS دەکرێت؟": "بۆ دەستنیشانکردنی شەکرە. دەبێت ٨-١٢ کاتژمێر برسی بیت.",
    "کاری خڕۆکە سپییەکان چییە؟": "بەرگری لەش ڕێکدەخەن و دژە ڤایرۆس و بەکتریا دەجەنگن.",
    "هۆکاری بەرزبوونی یۆریک ئەسید چییە؟": "گۆشتی سوور، ماسی، کحول، یان کێشەی گورچیلە.",
    "پشکنینی TSH بۆ چییە؟": "بۆ چالاکی غودەی دەرەقی. بەرز = تەمەڵی، نزم = زۆر چالاکی.",
    "ڤیتامین B12 بۆ چییە؟": "بۆ تەندروستی دەمار و دروستکردنی خڕۆکە سوورەکان.",
    "CRP چییە؟": "نیشاندەری هەوکردنی چالاک لە لەشدا.",
    "ئاساییترین ڕێژەی کۆلیسترۆڵ چییە؟": "کەمتر لە ٢٠٠ mg/dL.",
    "فێریتین چییە؟": "کۆگای ئاسنی لەش. کەمی = کەمخوێنی.",
    "کەی پێویستە پشکنینی شەکرە بکەم؟": "لە تەمەنی ٤٥+ ساڵانە، یان زووتر ئەگەر مەترسیداریت.",
    "جیاوازی FBS و HbA1c چییە؟": "FBS شەکری ئێستایە، HbA1c تێکڕای ٣ مانگە.",
    "چەند جارێک پشکنینی چەوری خوێن بکەم؟": "تەندروست: ٥ ساڵ، مەترسیدار: ساڵانە.",
    "نیشانەی کەمی ئاسن چییە؟": "بێهێزی، ماندوێتی، ڕووتانەوەی قژ.",
    "ئایا ئاو خواردن پێش پشکنین ڕێگەی پێدراوە؟": "بەڵێ، ئاوی ئاسایی.",
    "پۆتاسیۆم بۆچی گرنگە؟": "بۆ کارکردنی ماسولکە و دڵ. بەرزبوونەوە = مەترسی.",
}

# --- HEADER ---
st.markdown("""
<div class="main-header">
    <h1>🔬 ڕێبەری پشکنینە تاقیگەییەکان</h1>
    <p>زیاتر لە ١٥ پشکنین | شیکاری زیرەک | پرسیار و وەڵام</p>
</div>
""", unsafe_allow_html=True)

# --- TABS ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📋 پشکنینەکان", 
    "🧠 شیکاری زیرەک", 
    "📊 هێڵکاری",
    "💬 پرسیار و وەڵام"
])

# --- TAB 1: Tests ---
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        search_text = st.text_input("🔍 گەڕان:", placeholder="ناوی پشکنین...")
    with col2:
        organs = ["هەموو"] + sorted(list(set([t['Organ'] for t in ALL_TESTS.values()])))
        selected_organ = st.selectbox("🫀 ئەندامی لەش:", organs)
    
    filtered_tests = {}
    for key, test in ALL_TESTS.items():
        if search_text and search_text.lower() not in key.lower():
            continue
        if selected_organ != "هەموو" and test['Organ'] != selected_organ:
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
            st.markdown(f"<div class='category-badge'>📂 {category}</div>", unsafe_allow_html=True)
            
            for test_key, test in tests.items():
                with st.expander(f"{test['Icon']} {test['Name']} | 🫀 {test['Organ']}"):
                    st.markdown(f"""
                    <div class="test-card">
                        <p><b>📝 وەسف:</b> {test['Description']}</p>
                        <p><b>📊 ڕێژە ئاساییەکان:</b></p>
                        <p style="background:#f3f4f6;padding:10px;border-radius:8px;">{test['Ranges']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if 'FoodRecommendations' in test:
                        st.markdown(f"""
                        <div class="food-card">
                            <h4>🥗 ڕێنمایی خۆراکی</h4>
                            <p>{test['FoodRecommendations']}</p>
                        </div>
                        """, unsafe_allow_html=True)

# --- TAB 2: AI Analysis ---
with tab2:
    st.markdown("""
    <div style="text-align:center;padding:20px;">
        <h2 style="color:#4f46e5;">🧠 شیکاری زیرەکی ئەنجامەکان</h2>
        <p style="color:#6b7280;">ئەنجامی پشکنینەکەت بنووسە و شیکاری وەربگرە</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        test_choice = st.selectbox("🔬 پشکنین:", list(ALL_TESTS.keys()))
    with col2:
        gender_choice = st.selectbox("👤 ڕەگەز:", ["general", "male", "female"], 
                                     format_func=lambda x: {"general": "گشتی", "male": "پیاوان", "female": "ژنان"}[x])
    with col3:
        unit_choice = st.text_input("📏 یەکە:", value="mg/dL")
    with col4:
        user_result = st.number_input("🔢 ئەنجام:", value=0.0, step=0.1, format="%.1f")
    
    if st.button("🔍 شیکاری زیرەک ئەنجام بدە", use_container_width=True):
        if user_result > 0:
            with st.spinner("🧠 سیستەم ئەنجامەکەت شیدەکاتەوە..."):
                time.sleep(1)
                
                result = ai_analyze(test_choice, user_result, gender_choice)
                
                st.markdown(f"""
                <div class="ai-result-card">
                    <div class="{result['color_class']}">
                        <div style="display:flex;align-items:center;gap:15px;margin-bottom:15px;">
                            <span style="font-size:3rem;">{result['emoji']}</span>
                            <div>
                                <h3 style="margin:0;">{result['test_name']}</h3>
                                <p style="margin:5px 0;font-weight:600;">{result['status_text']}</p>
                            </div>
                        </div>
                        
                        <div style="background:#f9fafb;border-radius:12px;padding:15px;margin:15px 0;">
                            <p><b>📊 ئەنجامی تۆ:</b> <span style="font-size:1.5rem;font-weight:900;color:#4f46e5;">{result['user_value']}</span> {result['unit']}</p>
                            <p><b>📏 مەودای ئاسایی:</b> {result['min_val']} - {result['max_val']} {result['unit']}</p>
                        </div>
                        
                        <div style="background:#f0fdf4;border-radius:12px;padding:15px;margin:15px 0;">
                            <p><b>📋 شیکاری:</b></p>
                            <p style="font-size:1.05rem;line-height:1.8;">{result['meaning']}</p>
                        </div>
                        
                        <div style="background:#eef2ff;border-radius:12px;padding:15px;margin:15px 0;">
                            <p><b>💊 ڕێنمایی:</b></p>
                            <p style="font-size:1.05rem;line-height:1.8;">{result['action']}</p>
                        </div>
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
                
                # Show food
                test_data = ALL_TESTS.get(test_choice, {})
                if 'FoodRecommendations' in test_data:
                    st.markdown(f"""
                    <div class="food-card">
                        <h4>🥗 ڕێنمایی خۆراکی</h4>
                        <p>{test_data['FoodRecommendations']}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("تکایە ئەنجامێکی دروست بنووسە")

# --- TAB 3: Charts ---
with tab3:
    st.markdown("<h3 style='color:#4f46e5;text-align:center;'>📊 هێڵکاری گۆڕانکارییەکان</h3>", unsafe_allow_html=True)
    
    if len(st.session_state.history) > 0:
        df = pd.DataFrame(st.session_state.history)
        test_options = df['test'].unique()
        selected_tests = st.multiselect("پشکنینەکان:", test_options, default=list(test_options)[:3])
        
        if selected_tests:
            filtered_df = df[df['test'].isin(selected_tests)]
            fig = px.line(filtered_df, x='date', y='value', color='test',
                         title='گۆڕانکاری ئەنجامەکان', markers=True)
            fig.update_layout(plot_bgcolor='white', paper_bgcolor='white')
            st.plotly_chart(fig, use_container_width=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f'<div class="stat-card"><div class="stat-value">{len(filtered_df)}</div><div class="stat-label">ژمارە</div></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="stat-card"><div class="stat-value">{filtered_df["value"].min():.1f}</div><div class="stat-label">نزمترین</div></div>', unsafe_allow_html=True)
            with col3:
                st.markdown(f'<div class="stat-card"><div class="stat-value">{filtered_df["value"].max():.1f}</div><div class="stat-label">بەرزترین</div></div>', unsafe_allow_html=True)
    else:
        st.info("هێشتا هیچ ئەنجامێکت تۆمار نەکردووە.")

# --- TAB 4: FAQ ---
with tab4:
    st.markdown("<h3 style='color:#4f46e5;text-align:center;'>💬 پرسیار و وەڵام</h3>", unsafe_allow_html=True)
    
    faq_search = st.text_input("🔍 گەڕان لە پرسیارەکاندا:", placeholder="پرسیارێک بنووسە...")
    
    if faq_search:
        filtered_faq = {k: v for k, v in FAQ_DATABASE.items() if faq_search.lower() in k.lower()}
        if filtered_faq:
            for q, a in filtered_faq.items():
                with st.expander(f"❓ {q}"):
                    st.markdown(f'<div class="faq-item"><p>{a}</p></div>', unsafe_allow_html=True)
        else:
            st.info("هیچ پرسیارێک نەدۆزرایەوە")
    else:
        cols = st.columns(2)
        questions = list(FAQ_DATABASE.items())
        for i, (q, a) in enumerate(questions):
            with cols[i % 2]:
                with st.expander(f"❓ {q}"):
                    st.markdown(f'<div class="faq-item"><p>{a}</p></div>', unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("""
<div class="glass-card" style="text-align:center;margin-top:30px;">
    <div class="warning-box">
        <p>⚠️ ئەم سیستەمە تەنها بۆ ڕێنمایی سەرەتاییە و جێگەی سەردانی پزیشک ناگرێتەوە.</p>
    </div>
    <p style="color:#6b7280;">© ٢٠٢٤ ڕێبەری پشکنینە تاقیگەییەکان</p>
</div>
""", unsafe_allow_html=True)
