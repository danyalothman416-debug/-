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
import re

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

# --- MODERN LIGHT THEME CSS (MOBILE FRIENDLY) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Naskh+Arabic:wght@400;500;600;700;800;900&display=swap');
    
    * {
        font-family: 'Noto Naskh Arabic', 'Segoe UI', sans-serif;
    }
    
    [data-testid="stSidebar"] { display: none; }
    
    html, body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%) !important;
    }
    
    .main-header {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #2563eb 100%);
        border-radius: 20px;
        padding: 25px 20px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(79, 70, 229, 0.2);
    }
    
    .main-header h1 {
        color: white !important;
        font-size: 1.8rem !important;
        font-weight: 800 !important;
        margin: 0 0 8px 0 !important;
    }
    
    .main-header p {
        color: rgba(255,255,255,0.9) !important;
        font-size: 0.95rem !important;
        margin: 0 !important;
    }
    
    .glass-card {
        background: white !important;
        border-radius: 16px !important;
        padding: 20px !important;
        margin-bottom: 15px !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.04) !important;
        border: 1px solid #e5e7eb !important;
    }
    
    .test-card {
        background: white;
        border-radius: 14px;
        padding: 15px;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        border-right: 4px solid #4f46e5;
    }
    
    .test-card p {
        font-size: 0.9rem !important;
        line-height: 1.6 !important;
    }
    
    .ai-result-card {
        background: white;
        border-radius: 20px;
        padding: 20px;
        margin: 20px 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        animation: slideUp 0.4s ease-out;
    }
    
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .result-normal {
        background: #f0fdf4;
        border-left: 5px solid #10b981;
        border-radius: 12px;
        padding: 15px;
        margin: 12px 0;
    }
    
    .result-normal p, .result-normal h3 { color: #065f46 !important; }
    
    .result-abnormal {
        background: #fffbeb;
        border-left: 5px solid #f59e0b;
        border-radius: 12px;
        padding: 15px;
        margin: 12px 0;
    }
    
    .result-abnormal p, .result-abnormal h3 { color: #92400e !important; }
    
    .result-critical {
        background: #fef2f2;
        border-left: 5px solid #ef4444;
        border-radius: 12px;
        padding: 15px;
        margin: 12px 0;
    }
    
    .result-critical p, .result-critical h3 { color: #991b1b !important; }
    
    /* Smaller buttons */
    .stButton button {
        background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
        border-radius: 12px !important;
        padding: 10px 20px !important;
        font-size: 0.9rem !important;
        box-shadow: 0 2px 8px rgba(79, 70, 229, 0.2) !important;
        width: 100% !important;
    }
    
    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 15px rgba(79, 70, 229, 0.3) !important;
    }
    
    /* Smaller inputs */
    .stTextInput input, .stNumberInput input {
        background: white !important;
        border: 2px solid #e5e7eb !important;
        border-radius: 10px !important;
        color: #1f2937 !important;
        padding: 8px 14px !important;
        font-size: 0.9rem !important;
    }
    
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #4f46e5 !important;
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.08) !important;
    }
    
    .stSelectbox div {
        font-size: 0.9rem !important;
    }
    
    .food-card {
        background: #fffbeb;
        border: 1px solid #fde68a;
        border-radius: 12px;
        padding: 12px;
        margin: 10px 0;
        font-size: 0.85rem !important;
    }
    
    .food-card h4 {
        color: #92400e !important;
        font-size: 1rem !important;
        margin: 0 0 8px 0 !important;
    }
    
    .food-card p {
        color: #78350f !important;
        margin: 0 !important;
    }
    
    .category-badge {
        display: inline-block;
        background: #eef2ff;
        border: 1px solid #c7d2fe;
        border-radius: 20px;
        padding: 6px 16px;
        margin: 15px 0 10px 0;
        font-weight: 600;
        color: #3730a3 !important;
        font-size: 0.9rem;
    }
    
    .stat-card {
        background: white;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    }
    
    .stat-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #4f46e5 !important;
    }
    
    .stat-label {
        color: #6b7280 !important;
        font-size: 0.8rem;
        margin-top: 3px;
    }
    
    .faq-item {
        background: #f9fafb;
        border-radius: 10px;
        padding: 12px;
        margin: 6px 0;
        border: 1px solid #e5e7eb;
        font-size: 0.9rem;
    }
    
    /* Smaller expander */
    .streamlit-expanderHeader {
        background: #f9fafb !important;
        border-radius: 10px !important;
        border: 1px solid #e5e7eb !important;
        color: #1f2937 !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        padding: 8px 12px !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 5px;
        background: white !important;
        border-radius: 12px;
        padding: 4px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.03);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border-radius: 10px !important;
        color: #374151 !important;
        padding: 6px 12px !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
        color: white !important;
    }
    
    /* Smaller icons in result */
    .result-emoji {
        font-size: 2rem !important;
    }
    
    /* Info/warning boxes */
    .info-box {
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        border-radius: 10px;
        padding: 12px;
        font-size: 0.9rem;
    }
    
    .warning-box {
        background: #fef3c7;
        border: 1px solid #fde68a;
        border-radius: 10px;
        padding: 12px;
        font-size: 0.9rem;
    }
    
    /* Mobile responsive */
    @media (max-width: 768px) {
        .main-header h1 { font-size: 1.4rem !important; }
        .main-header p { font-size: 0.8rem !important; }
        .stButton button { font-size: 0.85rem !important; padding: 8px 16px !important; }
    }
    
    [dir="rtl"] { text-align: right !important; direction: rtl !important; }
</style>
""", unsafe_allow_html=True)

# --- ALL TESTS DATABASE ---
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

# --- FIXED AI ANALYSIS ENGINE ---
def ai_analyze(test_name, user_value, gender="general"):
    """Works for ALL tests by parsing ranges from database"""
    
    # Find matching test
    matched_test = None
    for key, test in ALL_TESTS.items():
        if key == test_name:
            matched_test = test
            break
    
    if not matched_test:
        # Create a safe result
        return create_result("unknown", user_value, "N/A", "N/A", "unit", test_name)
    
    # Parse ranges from text
    ranges_text = matched_test['Ranges']
    
    # Find number patterns
    range_matches = re.findall(r'(\d+\.?\d*)\s*-\s*(\d+\.?\d*)', ranges_text)
    
    if not range_matches:
        return create_result("unknown", user_value, "N/A", "N/A", "unit", matched_test['Name'])
    
    # Get first range as default
    min_val = float(range_matches[0][0])
    max_val = float(range_matches[0][1])
    
    # Try gender-specific
    if gender == "male":
        for i, (r, full_text) in enumerate(zip(range_matches, ranges_text.split('|'))):
            if "پیاوان" in full_text:
                min_val = float(r[0])
                max_val = float(r[1])
                break
    elif gender == "female":
        for i, (r, full_text) in enumerate(zip(range_matches, ranges_text.split('|'))):
            if "ژنان" in full_text:
                min_val = float(r[0])
                max_val = float(r[1])
                break
    
    # Extract unit
    unit_match = re.search(r'([a-zA-Z/µ]+)', ranges_text)
    unit = unit_match.group(1) if unit_match else "unit"
    
    # Determine status
    if user_value < min_val:
        return create_result("low", user_value, min_val, max_val, unit, matched_test['Name'])
    elif user_value > max_val:
        critical = user_value > max_val * 1.5
        return create_result("high" if not critical else "critical", user_value, min_val, max_val, unit, matched_test['Name'])
    else:
        return create_result("normal", user_value, min_val, max_val, unit, matched_test['Name'])

def create_result(status, user_value, min_val, max_val, unit, test_name):
    """Create consistent result dictionary with safe key access"""
    
    # Get short name
    short_name = test_name.split('(')[0].strip() if '(' in test_name else test_name
    
    result = {
        "status": status,
        "user_value": user_value,
        "min_val": min_val,
        "max_val": max_val,
        "unit": unit,
        "test_name": short_name,
        "test_name_full": test_name
    }
    
    if status == "normal":
        result.update({
            "emoji": "✅",
            "color_class": "result-normal",
            "status_text": "لە ئاستی ئاساییدایە",
            "meaning": f"ئەنجامی {short_name}ی تۆ ({user_value} {unit}) لە مەودای ئاسایی ({min_val}-{max_val} {unit}) دایە. ئەمە نیشانەیەکی باشە!",
            "action": "بەردەوام بە لەسەر شێوازی ژیانی تەندروست. پشکنینی ساڵانە ئەنجام بدە."
        })
    elif status == "low":
        result.update({
            "emoji": "⚠️",
            "color_class": "result-abnormal",
            "status_text": "لە ئاستی ئاسایی نزمترە",
            "meaning": f"ئەنجامی {short_name}ی تۆ ({user_value} {unit}) لە مەودای ئاسایی ({min_val}-{max_val} {unit}) نزمترە. ڕەنگە نیشانەی کێشەیەک بێت.",
            "action": "پێشنیار دەکەم سەردانی پزیشکی پسپۆڕ بکەیت بۆ پشکنینی زیاتر."
        })
    elif status == "high":
        result.update({
            "emoji": "⚠️",
            "color_class": "result-abnormal",
            "status_text": "لە ئاستی ئاسایی بەرزترە",
            "meaning": f"ئەنجامی {short_name}ی تۆ ({user_value} {unit}) لە مەودای ئاسایی ({min_val}-{max_val} {unit}) بەرزترە.",
            "action": "پێشنیار دەکەم بە زووترین کات سەردانی پزیشکی پسپۆڕ بکەیت."
        })
    elif status == "critical":
        result.update({
            "emoji": "🚨",
            "color_class": "result-critical",
            "status_text": "زۆر بەرزە - مەترسیدار!",
            "meaning": f"ئەنجامی {short_name}ی تۆ ({user_value} {unit}) زۆر لە مەودای ئاسایی ({min_val}-{max_val} {unit}) بەرزترە. ئەمە حاڵەتێکی مەترسیدارە!",
            "action": "یەکسەر پەیوەندی بە پزیشکەوە بکە یان سەردانی نەخۆشخانە بکە!"
        })
    else:
        result.update({
            "emoji": "❓",
            "color_class": "result-abnormal",
            "status_text": "پێویستی بە پشکنینی زیاترە",
            "meaning": f"ببورە، ناتوانم شیکاری ورد بۆ {short_name} بکەم.",
            "action": "تکایە ئەنجامەکەت ببە بۆ پزیشکی پسپۆڕ."
        })
    
    return result

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
    <p>شیکاری زیرەک | پرسیار و وەڵام</p>
</div>
""", unsafe_allow_html=True)

# --- TABS ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📋 پشکنینەکان", 
    "🧠 شیکاری", 
    "📊 هێڵکاری",
    "💬 پرسیار"
])

# --- TAB 1 ---
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        search_text = st.text_input("🔍 گەڕان:", placeholder="ناوی پشکنین...", key="search_tests")
    with col2:
        organs = ["هەموو"] + sorted(list(set([t['Organ'] for t in ALL_TESTS.values()])))
        selected_organ = st.selectbox("🫀 ئەندامی لەش:", organs, key="organ_filter")
    
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
                with st.expander(f"{test['Icon']} {test['Name'][:50]}... | {test['Organ']}"):
                    st.markdown(f"""
                    <div class="test-card">
                        <p><b>📝 وەسف:</b> {test['Description']}</p>
                        <p><b>📊 ڕێژە ئاساییەکان:</b></p>
                        <p style="background:#f3f4f6;padding:8px 12px;border-radius:8px;font-size:0.85rem;">{test['Ranges']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if 'FoodRecommendations' in test:
                        st.markdown(f"""
                        <div class="food-card">
                            <h4>🥗 خۆراکی</h4>
                            <p>{test['FoodRecommendations']}</p>
                        </div>
                        """, unsafe_allow_html=True)

# --- TAB 2 ---
with tab2:
    st.markdown("<h3 style='color:#4f46e5;text-align:center;margin-bottom:15px;'>🧠 شیکاری زیرەکی ئەنجامەکان</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        test_choice = st.selectbox("🔬 پشکنین:", list(ALL_TESTS.keys()), key="ai_test")
        gender_choice = st.selectbox("👤 ڕەگەز:", ["general", "male", "female"], 
                                     format_func=lambda x: {"general": "گشتی", "male": "پیاوان", "female": "ژنان"}[x], key="ai_gender")
    with col2:
        unit_choice = st.text_input("📏 یەکە:", value="mg/dL", key="ai_unit")
        user_result = st.number_input("🔢 ئەنجام:", value=0.0, step=0.1, format="%.1f", key="ai_value")
    
    if st.button("🔍 شیکاری بکە", key="ai_button", use_container_width=True):
        if user_result > 0:
            with st.spinner("🧠 شیکاری دەکرێت..."):
                time.sleep(0.8)
                
                result = ai_analyze(test_choice, user_result, gender_choice)
                
                st.markdown(f"""
                <div class="ai-result-card">
                    <div class="{result['color_class']}">
                        <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">
                            <span style="font-size:1.8rem;">{result['emoji']}</span>
                            <div>
                                <h4 style="margin:0;font-size:1rem;">{result['test_name']}</h4>
                                <p style="margin:3px 0;font-size:0.85rem;font-weight:600;">{result['status_text']}</p>
                            </div>
                        </div>
                        
                        <div style="background:#f9fafb;border-radius:8px;padding:10px;margin:10px 0;font-size:0.9rem;">
                            <b>📊 ئەنجام:</b> {result['user_value']} {result['unit']}<br>
                            <b>📏 مەودای ئاسایی:</b> {result['min_val']} - {result['max_val']} {result['unit']}
                        </div>
                        
                        <div style="margin:10px 0;font-size:0.9rem;">
                            <b>📋 شیکاری:</b> {result['meaning']}
                        </div>
                        
                        <div style="background:#eef2ff;border-radius:8px;padding:10px;margin:10px 0;font-size:0.9rem;">
                            <b>💊 ڕێنمایی:</b> {result['action']}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.session_state.history.append({
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "test": test_choice,
                    "value": user_result,
                    "unit": unit_choice,
                    "status": result['status']
                })
                
                test_data = ALL_TESTS.get(test_choice, {})
                if 'FoodRecommendations' in test_data:
                    st.markdown(f"""
                    <div class="food-card">
                        <h4>🥗 خۆراکی</h4>
                        <p>{test_data['FoodRecommendations']}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("تکایە ئەنجامێک بنووسە")

# --- TAB 3 ---
with tab3:
    st.markdown("<h3 style='color:#4f46e5;text-align:center;'>📊 گۆڕانکارییەکان</h3>", unsafe_allow_html=True)
    
    if len(st.session_state.history) > 0:
        df = pd.DataFrame(st.session_state.history)
        test_options = df['test'].unique()
        selected_tests = st.multiselect("پشکنین:", test_options, default=list(test_options)[:3], key="chart_tests")
        
        if selected_tests:
            filtered_df = df[df['test'].isin(selected_tests)]
            fig = px.line(filtered_df, x='date', y='value', color='test', markers=True)
            fig.update_layout(plot_bgcolor='white', paper_bgcolor='white', height=350)
            st.plotly_chart(fig, use_container_width=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f'<div class="stat-card"><div class="stat-value">{len(filtered_df)}</div><div class="stat-label">ژمارە</div></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="stat-card"><div class="stat-value">{filtered_df["value"].min():.1f}</div><div class="stat-label">نزمترین</div></div>', unsafe_allow_html=True)
            with col3:
                st.markdown(f'<div class="stat-card"><div class="stat-value">{filtered_df["value"].max():.1f}</div><div class="stat-label">بەرزترین</div></div>', unsafe_allow_html=True)
    else:
        st.info("هێشتا ئەنجامێکت تۆمار نەکردووە")

# --- TAB 4 ---
with tab4:
    st.markdown("<h3 style='color:#4f46e5;text-align:center;'>💬 پرسیار و وەڵام</h3>", unsafe_allow_html=True)
    
    faq_search = st.text_input("🔍 گەڕان:", placeholder="پرسیار بنووسە...", key="faq_search")
    
    if faq_search:
        filtered_faq = {k: v for k, v in FAQ_DATABASE.items() if faq_search.lower() in k.lower()}
        if filtered_faq:
            for q, a in filtered_faq.items():
                with st.expander(f"❓ {q}"):
                    st.markdown(f'<div class="faq-item"><p style="margin:0;">{a}</p></div>', unsafe_allow_html=True)
        else:
            st.info("نەدۆزرایەوە")
    else:
        questions = list(FAQ_DATABASE.items())
        for i, (q, a) in enumerate(questions[:12]):
            with st.expander(f"❓ {q}"):
                st.markdown(f'<div class="faq-item"><p style="margin:0;">{a}</p></div>', unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("""
<div class="glass-card" style="text-align:center;margin-top:20px;">
    <div class="warning-box">
        <p style="margin:0;">⚠️ ئەم سیستەمە تەنها بۆ ڕێنماییە و جێگەی سەردانی پزیشک ناگرێتەوە</p>
    </div>
</div>
""", unsafe_allow_html=True)
