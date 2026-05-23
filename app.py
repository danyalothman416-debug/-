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
from fpdf import FPDF

# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="ڕێبەری پشکنینە تاقیگەییەکان - سیستەمی تەواو", 
    layout="wide", 
    initial_sidebar_state="collapsed",
    page_icon="🔬"
)

# ============================================
# SESSION STATE
# ============================================
if 'history' not in st.session_state:
    st.session_state.history = []
if 'reminders' not in st.session_state:
    st.session_state.reminders = []
if 'doctor_notes' not in st.session_state:
    st.session_state.doctor_notes = []

# ============================================
# MODERN PREMIUM CSS
# ============================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Naskh+Arabic:wght@300;400;500;600;700;800;900&display=swap');
    
    * { font-family: 'Noto Naskh Arabic', 'Segoe UI', sans-serif !important; }
    [data-testid="stSidebar"] { display: none; }
    
    /* Background */
    html, body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #f0f4ff 0%, #e8eeff 25%, #f5f7ff 50%, #eef2ff 75%, #f0f4ff 100%) !important;
        background-size: 400% 400% !important;
        animation: gradientShift 20s ease infinite !important;
    }
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Main Header */
    .main-header {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 40%, #2563eb 100%);
        border-radius: 24px;
        padding: 30px 25px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 15px 40px rgba(79, 70, 229, 0.25), 0 0 80px rgba(124, 58, 237, 0.1);
        position: relative;
        overflow: hidden;
    }
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%; left: -50%;
        width: 200%; height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 60%);
        animation: rotate 25s linear infinite;
    }
    @keyframes rotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
    .main-header h1 { color: white !important; font-size: 2rem !important; font-weight: 900 !important; margin: 0 0 8px 0 !important; position: relative; z-index: 1; }
    .main-header p { color: rgba(255,255,255,0.9) !important; font-size: 1rem !important; margin: 0 !important; position: relative; z-index: 1; }
    
    /* Cards */
    .glass-card {
        background: white !important;
        border-radius: 18px !important;
        padding: 20px !important;
        margin-bottom: 15px !important;
        box-shadow: 0 3px 15px rgba(0,0,0,0.05), 0 1px 3px rgba(0,0,0,0.03) !important;
        border: 1px solid rgba(0,0,0,0.04) !important;
        transition: all 0.3s ease !important;
    }
    .glass-card:hover { transform: translateY(-3px); box-shadow: 0 8px 25px rgba(0,0,0,0.08) !important; }
    
    /* Symptom Grid */
    .symptom-btn {
        background: white !important;
        border: 2px solid #e5e7eb !important;
        border-radius: 14px !important;
        padding: 12px 8px !important;
        text-align: center !important;
        cursor: pointer !important;
        transition: all 0.25s ease !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        color: #374151 !important;
        width: 100% !important;
        min-height: 50px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    .symptom-btn:hover {
        border-color: #4f46e5 !important;
        background: #eef2ff !important;
        color: #4f46e5 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(79,70,229,0.15) !important;
    }
    
    /* Result Boxes */
    .result-box { border-radius: 14px; padding: 16px; margin: 10px 0; font-size: 0.9rem; line-height: 1.7; }
    .result-normal { background: #f0fdf4; border-left: 5px solid #10b981; color: #065f46 !important; }
    .result-abnormal { background: #fffbeb; border-left: 5px solid #f59e0b; color: #92400e !important; }
    .result-critical { background: #fef2f2; border-left: 5px solid #ef4444; color: #991b1b !important; animation: pulse 2s infinite; }
    .result-info { background: #eff6ff; border-left: 5px solid #3b82f6; color: #1e40af !important; }
    @keyframes pulse { 0%,100% { opacity:1; } 50% { opacity:0.85; } }
    
    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
        color: white !important; border: none !important;
        font-weight: 700 !important; border-radius: 14px !important;
        padding: 12px 24px !important; font-size: 0.95rem !important;
        box-shadow: 0 4px 15px rgba(79,70,229,0.3) !important;
        transition: all 0.3s ease !important; width: 100% !important;
        letter-spacing: 0.3px !important;
    }
    .stButton button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(79,70,229,0.45) !important;
    }
    
    /* Inputs */
    .stTextInput input, .stNumberInput input, .stTextArea textarea {
        background: white !important; border: 2px solid #e5e7eb !important;
        border-radius: 12px !important; color: #1f2937 !important;
        padding: 10px 16px !important; font-size: 0.9rem !important;
        transition: all 0.3s ease !important;
    }
    .stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {
        border-color: #4f46e5 !important; box-shadow: 0 0 0 4px rgba(79,70,229,0.08) !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 6px; background: white !important; border-radius: 16px; padding: 6px; box-shadow: 0 2px 10px rgba(0,0,0,0.04); }
    .stTabs [data-baseweb="tab"] { background: transparent !important; border-radius: 12px !important; color: #374151 !important; padding: 8px 14px !important; font-weight: 600 !important; font-size: 0.85rem !important; transition: all 0.3s !important; }
    .stTabs [aria-selected="true"] { background: linear-gradient(135deg, #4f46e5, #7c3aed) !important; color: white !important; box-shadow: 0 4px 12px rgba(79,70,229,0.3) !important; }
    
    /* Expander */
    .streamlit-expanderHeader { background: #fafbfc !important; border-radius: 12px !important; border: 1px solid #e5e7eb !important; color: #1f2937 !important; font-weight: 700 !important; font-size: 0.9rem !important; padding: 10px 14px !important; transition: all 0.3s !important; }
    .streamlit-expanderHeader:hover { background: #f0f4ff !important; border-color: #c7d2fe !important; }
    
    /* Badges */
    .badge { display: inline-block; background: #eef2ff; border: 1px solid #c7d2fe; border-radius: 20px; padding: 6px 18px; margin: 12px 0 8px 0; font-weight: 700; color: #3730a3 !important; font-size: 0.85rem; }
    .badge-green { background: #f0fdf4; border-color: #86efac; color: #166534 !important; }
    .badge-yellow { background: #fffbeb; border-color: #fde68a; color: #92400e !important; }
    
    /* Food Card */
    .food-card { background: linear-gradient(135deg, #fffbeb, #fff7ed); border: 1px solid #fde68a; border-radius: 14px; padding: 14px; margin: 10px 0; font-size: 0.85rem; }
    .food-card h4 { color: #92400e !important; font-size: 1rem !important; margin: 0 0 8px 0 !important; }
    
    /* Stats */
    .stat-card { background: white; border-radius: 14px; padding: 18px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
    .stat-value { font-size: 1.8rem; font-weight: 900; color: #4f46e5 !important; }
    .stat-label { color: #6b7280 !important; font-size: 0.8rem; margin-top: 4px; }
    
    /* Reminder Card */
    .reminder-card { background: white; border-radius: 14px; padding: 14px; margin: 8px 0; border: 1px solid #e5e7eb; border-left: 4px solid #4f46e5; font-size: 0.85rem; transition: all 0.3s; }
    .reminder-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.06); }
    
    /* Abbreviation Card */
    .abbr-card { background: white; border-radius: 14px; padding: 16px; margin: 8px 0; border: 1px solid #e5e7eb; text-align: center; cursor: pointer; transition: all 0.3s; }
    .abbr-card:hover { border-color: #4f46e5; background: #eef2ff; transform: translateY(-2px); }
    .abbr-card h3 { color: #4f46e5 !important; margin: 0 0 5px 0 !important; }
    
    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #f1f5f9; border-radius: 10px; }
    ::-webkit-scrollbar-thumb { background: #c7d2fe; border-radius: 10px; }
    ::-webkit-scrollbar-thumb:hover { background: #4f46e5; }
    
    [dir="rtl"] { text-align: right !important; direction: rtl !important; }
    
    @media (max-width: 768px) {
        .main-header h1 { font-size: 1.3rem !important; }
        .main-header p { font-size: 0.8rem !important; }
        .stButton button { font-size: 0.8rem !important; padding: 8px 14px !important; }
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# COMPLETE DATABASE (50+ Tests)
# ============================================
ALL_TESTS = {
    # بنەڕەتییەکان
    "پشکنینی تەواوی خوێن (CBC)": {
        "Name": "پشکنینی تەواوی خوێن (CBC)", "Category": "پشکنینە بنەڕەتییەکان", "Organ": "خوێن", "Icon": "🩸",
        "Description": "پێوانەی پێکهاتەکانی خوێن: خڕۆکە سوورەکان، خڕۆکە سپییەکان و پەڕەکانی خوێن. یارمەتیدەرە بۆ دەستنیشانکردنی کەمخوێنی، هەوکردن، و کێشەکانی مەینبوونی خوێن.",
        "Ranges": "هیمۆگڵۆبین (پیاوان): 13.5-17.5 g/dL | (ژنان): 12.0-15.5 g/dL | WBC: 4,500-11,000 /µL | Platelets: 150,000-450,000 /µL | RBC: 4.7-6.1 / 4.2-5.4 million/µL",
        "FoodRecommendations": "🥩 گۆشتی سوور | 🥬 سپێناغ | 🍊 ڤیتامین C | ❌ دوور لە چا دوای نان"
    },
    "شەکری ناو خوێن (FBS)": {
        "Name": "شەکری ناو خوێن لە کاتی برسێتیدا (FBS)", "Category": "پشکنینە بنەڕەتییەکان", "Organ": "پەنکریاس", "Icon": "🍬",
        "Description": "پێوانەی گلوکۆزی خوێن دوای ٨-١٢ کاتژمێر برسێتی. ١٠٠-١٢٥ = پێش شەکرە | ١٢٦+ = شەکرە.",
        "Ranges": "ڕێژەی ئاسایی: 70-99 mg/dL",
        "FoodRecommendations": "🥦 برۆکلی | 🐟 ماسی | 🌾 هەویری تەواو | ❌ دوور لە شەکر و نانی سپی"
    },
    "شەکری کەڵەکەبوو (HbA1c)": {
        "Name": "شەکری کەڵەکەبوو (HbA1c)", "Category": "پشکنینە بنەڕەتییەکان", "Organ": "پەنکریاس", "Icon": "📊",
        "Description": "تێکڕای شەکری خوێن لە ٢-٣ مانگی ڕابردوو. 5.7%-6.4% = پێش شەکرە | 6.5%+ = شەکرە.",
        "Ranges": "ڕێژەی ئاسایی: <5.7%",
        "FoodRecommendations": "🥗 سەوزەواتی ڕیشاڵدار | 🏃 وەرزشی ڕۆژانە ٣٠ خولەک"
    },
    "چەورییەکانی خوێن (Lipid)": {
        "Name": "چەورییەکانی خوێن (Lipid Profile)", "Category": "پشکنینە بنەڕەتییەکان", "Organ": "دڵ", "Icon": "❤️",
        "Description": "پێوانەی چەورییەکانی خوێن: کۆلیسترۆڵ، HDL، LDL، و Triglycerides. گرنگە بۆ هەڵسەنگاندنی مەترسی نەخۆشی دڵ.",
        "Ranges": "کۆلیسترۆڵ: <200 mg/dL | Triglycerides: <150 mg/dL | HDL: >40 mg/dL | LDL: <100 mg/dL",
        "FoodRecommendations": "🥑 ئەڤۆکادۆ | 🥜 گوێز | 🫒 زەیتی زەیتوون | ❌ دوور لە فاست فوود"
    },
    "فەرمانی گورچیلە (KFT)": {
        "Name": "پشکنینی فەرمانی گورچیلە (KFT)", "Category": "پشکنینە بنەڕەتییەکان", "Organ": "گورچیلە", "Icon": "🫘",
        "Description": "پێوانەی کریاتینین و یوریا بۆ هەڵسەنگاندنی کارکردنی گورچیلەکان.",
        "Ranges": "کریاتینین (پیاوان): 0.7-1.3 mg/dL | (ژنان): 0.6-1.1 mg/dL | یوریا: 15-40 mg/dL | GFR: >90 mL/min",
        "FoodRecommendations": "💧 ئاوی زۆر (٨-١٠ پەرداخ) | 🍎 سێو | ❌ کەمکردنەوەی خوێ"
    },
    "فەرمانی جگەر (LFT)": {
        "Name": "پشکنینی فەرمانی جگەر (LFT)", "Category": "پشکنینە بنەڕەتییەکان", "Organ": "جگەر", "Icon": "🫁",
        "Description": "ئەنزیمەکانی جگەر: ALT، AST، ALP، GGT، بیلیڕۆبین. بەرزبوونەوە = هەوکردن یان تێکچوونی جگەر.",
        "Ranges": "ALT: 7-56 U/L | AST: 10-40 U/L | ALP: 44-147 U/L | GGT: 0-30 U/L | بیلیڕۆبین: 0.1-1.2 mg/dL",
        "FoodRecommendations": "🍵 چای سەوز | 🧄 سیر | 🫚 زەردەچێوە | ❌ دوور لە کحول"
    },
    "هۆرمۆنی دەرەقی (TSH)": {
        "Name": "هۆرمۆنی ڕژێنی دەرەقی (TSH)", "Category": "پشکنینی هۆرمۆنەکان", "Organ": "دەرەقی", "Icon": "🦋",
        "Description": "پشکنینی کارکردنی غودەی دەرەقی. بەرزبوونەوە = تەمەڵی، نزمبوونەوە = زۆر چالاکی.",
        "Ranges": "TSH: 0.4-4.0 mIU/L | T3: 80-200 ng/dL | T4: 4.5-12.0 µg/dL",
        "FoodRecommendations": "🧂 خوێی یۆددار | 🐟 ماسی دەریا | 🥜 گوێزی بەرازیلی"
    },
    "پرۆتینەکانی خوێن": {
        "Name": "پرۆتینەکانی خوێن (Albumin & Total Protein)", "Category": "پشکنینە بنەڕەتییەکان", "Organ": "جگەر / گورچیلە", "Icon": "🧪",
        "Description": "ئەلبومین پرۆتینی سەرەکی خوێنە. کەمبوونەوە = کێشەی جگەر یان گورچیلە.",
        "Ranges": "ئەلبومین: 3.4-5.4 g/dL | پرۆتینی گشتی: 6.0-8.3 g/dL",
        "FoodRecommendations": "🥚 هێلکە | 🥛 شیر | 🍗 مریشک"
    },
    "ئەلیکترۆلیتەکان": {
        "Name": "پشکنینی ئەلیکترۆلیتەکان (Electrolytes)", "Category": "پشکنینە بنەڕەتییەکان", "Organ": "گورچیلە / خوێن", "Icon": "⚡",
        "Description": "پێوانەی سۆدیۆم، پۆتاسیۆم، کالیسیۆم، کلۆراید، و مەگنیسیۆم.",
        "Ranges": "سۆدیۆم: 135-145 | پۆتاسیۆم: 3.6-5.2 | کالیسیۆم: 8.5-10.2 | مەگنیسیۆم: 1.7-2.2 | کلۆراید: 96-106",
        "FoodRecommendations": "🍌 مۆز | 🥛 شیر | 🥑 ئەڤۆکادۆ | 🧂 هاوسەنگی خوێ"
    },
    # ڤیتامینەکان
    "کۆگای ئاسن (Ferritin)": {
        "Name": "کۆگای ئاسن (Ferritin)", "Category": "پشکنینە تایبەتەکان", "Organ": "خوێن", "Icon": "🧲",
        "Description": "پێوانەی ئاسنی خەزنکراوی لەش. کەمی = کەمخوێنی، ڕووتانەوەی قژ، و بێهێزی.",
        "Ranges": "پیاوان: 24-336 ng/mL | ژنان: 11-307 ng/mL",
        "FoodRecommendations": "🥩 گۆشتی سوور | 🥬 سپێناغ | 🍊 ڤیتامین C بۆ هەڵمژینی باشتر"
    },
    "ئاسنی خوێن (Serum Iron)": {
        "Name": "ئاسنی خوێن (Serum Iron)", "Category": "پشکنینە تایبەتەکان", "Organ": "خوێن", "Icon": "🔩",
        "Description": "ئاستی ڕاستەوخۆی ئاسن لە خوێندا. پێویستە بۆ دروستبوونی خڕۆکە سوورەکان.",
        "Ranges": "ڕێژەی ئاسایی: 60-170 µg/dL | TIBC: 240-450 µg/dL",
        "FoodRecommendations": "🥩 گۆشت | 🥬 سەوزەواتی گەڵا سەوز | 🍊 پرتەقاڵ"
    },
    "ڤیتامین دی (Vitamin D)": {
        "Name": "ڤیتامین دی (25-Hydroxy Vitamin D)", "Category": "پشکنینی ڤیتامینەکان", "Organ": "ئێسک", "Icon": "☀️",
        "Description": "بۆ تەندروستی ئێسک، هەڵمژینی کالیسیۆم، و بەرگری لەش. <20 = کەمی ڤیتامین دی.",
        "Ranges": "ڕێژەی ئاسایی: 30-100 ng/mL",
        "FoodRecommendations": "☀️ ڕووناکی خۆر ١٥-٢٠ خولەک | 🐟 سەلەمۆن | 🥛 شیری ڤیتامین دی زیادکراو"
    },
    "ڤیتامین B12": {
        "Name": "ڤیتامین B12 (Cobalamin)", "Category": "پشکنینی ڤیتامینەکان", "Organ": "دەمار", "Icon": "💊",
        "Description": "بۆ تەندروستی دەمارەکان و دروستکردنی خڕۆکە سوورەکان. کەمی = بێهێزی و کێشەی دەمار.",
        "Ranges": "ڕێژەی ئاسایی: 200-900 pg/mL",
        "FoodRecommendations": "🥩 گۆشت | 🐟 ماسی | 🥚 هێلکە | 🧀 پەنیر"
    },
    "فۆلیک ئەسید (B9)": {
        "Name": "فۆلیک ئەسید (Vitamin B9 / Folic Acid)", "Category": "پشکنینی ڤیتامینەکان", "Organ": "خوێن", "Icon": "💚",
        "Description": "بۆ دروستبوونی خڕۆکە سوورەکان و پێشگیری لە کەموکوڕی کۆرپە لە دووگیانیدا.",
        "Ranges": "ڕێژەی ئاسایی: 5-20 ng/mL",
        "FoodRecommendations": "🥬 سەوزەواتی گەڵا سەوز | 🫘 پاقلەمەنی | 🥜 گوێز"
    },
    "مەگنیسیۆم (Magnesium)": {
        "Name": "مەگنیسیۆم (Magnesium)", "Category": "پشکنینی ڤیتامینەکان", "Organ": "دەمار / ماسولکە", "Icon": "🔋",
        "Description": "بۆ کارکردنی دەمار و ماسولکە، تەندروستی دڵ، و بەهێزبوونی ئێسک.",
        "Ranges": "ڕێژەی ئاسایی: 1.7-2.2 mg/dL",
        "FoodRecommendations": "🥜 بادەم | 🥑 ئەڤۆکادۆ | 🍌 مۆز | 🥬 سپێناغ"
    },
    "زینک (Zinc)": {
        "Name": "زینک (Zinc)", "Category": "پشکنینی ڤیتامینەکان", "Organ": "بەرگری / پێست", "Icon": "✨",
        "Description": "بۆ بەهێزکردنی بەرگری لەش، چاکبوونەوەی برین، و تەندروستی پێست و قژ.",
        "Ranges": "ڕێژەی ئاسایی: 70-120 µg/dL",
        "FoodRecommendations": "🥩 گۆشت | 🦪 ماسی | 🎃 تۆوی کولەکە | 🥜 گوێز"
    },
    # تایبەتەکان
    "ترشی یۆریک (Uric Acid)": {
        "Name": "ترشی یۆریک (Uric Acid)", "Category": "پشکنینە تایبەتەکان", "Organ": "جومگەکان / گورچیلە", "Icon": "🦴",
        "Description": "بەرزبوونەوە = ڕۆماتیزمی دەردە پاشا (Gout) و بەردی گورچیلە.",
        "Ranges": "پیاوان: 3.4-7.0 mg/dL | ژنان: 2.4-6.0 mg/dL",
        "FoodRecommendations": "💧 ئاوی زۆر | 🍒 گێلاس | ❌ کەمکردنەوەی گۆشتی سوور و ماسی"
    },
    "پەنکریاس (Amylase/Lipase)": {
        "Name": "پشکنینی پەنکریاس (Amylase & Lipase)", "Category": "پشکنینە تایبەتەکان", "Organ": "پەنکریاس", "Icon": "🫁",
        "Description": "ئەنزیمەکانی پەنکریاس. بەرزبوونەوە = هەوکردنی پەنکریاس (Pancreatitis).",
        "Ranges": "ئامیلاز: 40-140 U/L | لیپەیز: 0-160 U/L",
        "FoodRecommendations": "🥗 خواردنی سوک و کەم چەوری | ❌ دوور لە کحول"
    },
    "ماسولکە و دڵ (LDH/CPK)": {
        "Name": "پشکنینی ماسولکە و دڵ (LDH & CPK)", "Category": "پشکنینە تایبەتەکان", "Organ": "دڵ / ماسولکە", "Icon": "💪",
        "Description": "LDH و CPK نیشاندەری زیانگەیشتن بە شانەکانی دڵ و ماسولکەکانن.",
        "Ranges": "LDH: 140-280 U/L | CPK: 10-120 U/L | CK-MB: <5 ng/mL",
        "FoodRecommendations": "🏃 وەرزشی ئاستەم | 💧 ئاوی زۆر دوای وەرزش"
    },
    # هەوکردن
    "هەوکردن (CRP)": {
        "Name": "پشکنینی هەوکردن (CRP)", "Category": "پشکنینی هەوکردن", "Organ": "گشتی لەش", "Icon": "🔥",
        "Description": "نیشاندەری هەوکردنی چالاک لە لەشدا. بەرزبوونەوە = هەوکردنی بەکتریایی یان ڤایرۆسی.",
        "Ranges": "ڕێژەی ئاسایی: <10 mg/L | hs-CRP (مەترسی دڵ): <1.0 mg/L",
        "FoodRecommendations": "🫚 زەنجەفیل | 🫚 زەردەچێوە | 🐟 ماسی چەور | 🫒 زەیتی زەیتوون"
    },
    "نیشتنەوەی خڕۆکە سوورەکان (ESR)": {
        "Name": "ڕێژەی نیشتنەوەی خڕۆکە سوورەکان (ESR)", "Category": "پشکنینی هەوکردن", "Organ": "گشتی لەش", "Icon": "⏳",
        "Description": "نیشاندەری هەوکردنی درێژخایەن یان نەخۆشی جومگەکان. بەپێی تەمەن و ڕەگەز دەگۆڕێت.",
        "Ranges": "پیاوان: 0-22 mm/hr | ژنان: 0-29 mm/hr",
        "FoodRecommendations": "🥗 ڕێجیمی دژە هەوکردن | ❌ کەمکردنەوەی شەکر"
    },
    # فریاگوزاری
    "ترۆپۆنین (Troponin)": {
        "Name": "ترۆپۆنین (Troponin) - فریاکەوتن", "Category": "پشکنینی فریاگوزاری", "Organ": "دڵ", "Icon": "💔",
        "Description": "پشکنینی فریاگوزاری بۆ دەستنیشانکردنی جەڵتەی دڵ. بەرزبوونەوەی کەم = مەترسی.",
        "Ranges": "ڕێژەی ئاسایی: <0.04 ng/mL (نزیک بە سفر)",
        "FoodRecommendations": "❤️ ڕێجیمی دڵ تەندروست | 🏃 وەرزش | ❌ دوور لە جگەرە"
    },
    "مەینبوونی خوێن (PT/INR)": {
        "Name": "پشکنینی مەینبوونی خوێن (PT, PTT, INR)", "Category": "پشکنینی تایبەت", "Organ": "خوێن", "Icon": "🩹",
        "Description": "پێوانەی ماوەی مەینبوونی خوێن. بۆ کۆنترۆڵکردنی دەرمانی وارفارین و پێش نەشتەرگەری.",
        "Ranges": "PT: 11-13.5 sec | PTT: 25-35 sec | INR (ئاسایی): 0.8-1.2 | INR (وارفارین): 2.0-3.0",
        "FoodRecommendations": "🥬 ڕێکخستنی ڤیتامین K | 💊 دەرمان بە ڕێنمایی پزیشک"
    },
    # ڤایرۆسی و بەرگری
    "ڤایرۆسی جگەر (Hepatitis)": {
        "Name": "پشکنینی ڤایرۆسی جگەر (Hepatitis Panel)", "Category": "پشکنینی ڤایرۆسی", "Organ": "جگەر", "Icon": "🦠",
        "Description": "پشکنینی ڤایرۆسی جگەر: HAV, HBV, HCV. بۆ دەستنیشانکردنی هەوکردنی ڤایرۆسی جگەر.",
        "Ranges": "HBsAg: نەرێنی (Negative) | Anti-HCV: نەرێنی | Anti-HAV IgM: نەرێنی",
        "FoodRecommendations": "🧼 خۆپارێزی | 💉 ڤاکسین (بۆ A و B)"
    },
    "پشکنینی HIV": {
        "Name": "پشکنینی ڤایرۆسی بەرگری (HIV Test)", "Category": "پشکنینی ڤایرۆسی", "Organ": "بەرگری لەش", "Icon": "🏥",
        "Description": "پشکنینی ڤایرۆسی HIV کە هێرش دەکاتە سەر کۆئەندامی بەرگری لەش.",
        "Ranges": "Anti-HIV: نەرێنی (Negative)",
        "FoodRecommendations": "💊 چارەسەری پزیشکی | 🥗 بەهێزکردنی بەرگری"
    },
    # میز
    "پشکنینی میز (Urinalysis)": {
        "Name": "پشکنینی تەواوی میز (Urinalysis)", "Category": "پشکنینە بنەڕەتییەکان", "Organ": "گورچیلە / میزەڕۆ", "Icon": "🧪",
        "Description": "پشکنینی جەستەیی و کیمیایی میز بۆ دەستنیشانکردنی هەوکردن، کێشەی گورچیلە، یان شەکرە.",
        "Ranges": "ڕەنگ: زەردی کاڵ | pH: 4.5-8.0 | پرۆتین و گلوکۆز: نەبێت | WBC: 0-5 /HPF | RBC: 0-3 /HPF",
        "FoodRecommendations": "💧 ئاوی زۆر | 🫐 قەرەکەمەری | ❌ دوور لە خواردنی تیژ"
    },
}

# ============================================
# SYMPTOM TO TEST MAPPING
# ============================================
SYMPTOM_TESTS = {
    "بێهێزی": ["پشکنینی تەواوی خوێن (CBC)", "کۆگای ئاسن (Ferritin)", "ڤیتامین B12", "ڤیتامین دی (Vitamin D)", "شەکری ناو خوێن (FBS)"],
    "سەرئێشە": ["پشکنینی تەواوی خوێن (CBC)", "ڤیتامین دی (Vitamin D)", "هۆرمۆنی دەرەقی (TSH)", "ئەلیکترۆلیتەکان"],
    "ئازاری جومگە": ["ترشی یۆریک (Uric Acid)", "هەوکردن (CRP)", "پشکنینی تەواوی خوێن (CBC)", "ڤیتامین دی (Vitamin D)"],
    "ماندوێتی زۆر": ["پشکنینی تەواوی خوێن (CBC)", "کۆگای ئاسن (Ferritin)", "هۆرمۆنی دەرەقی (TSH)", "شەکری ناو خوێن (FBS)", "ڤیتامین B12"],
    "دڵەڕاوکێ و ڕاژان": ["هۆرمۆنی دەرەقی (TSH)", "ئەلیکترۆلیتەکان", "پشکنینی تەواوی خوێن (CBC)"],
    "کێش دابەزینی لەناکاو": ["هۆرمۆنی دەرەقی (TSH)", "شەکری ناو خوێن (FBS)", "شەکری کەڵەکەبوو (HbA1c)", "پشکنینی تەواوی خوێن (CBC)"],
    "کێش زیادبوون": ["هۆرمۆنی دەرەقی (TSH)", "شەکری ناو خوێن (FBS)", "چەورییەکانی خوێن (Lipid)"],
    "ڕووتانەوەی قژ": ["کۆگای ئاسن (Ferritin)", "هۆرمۆنی دەرەقی (TSH)", "ڤیتامین دی (Vitamin D)", "ڤیتامین B12", "زینک (Zinc)"],
    "ئازاری سک": ["پەنکریاس (Amylase/Lipase)", "فەرمانی جگەر (LFT)", "هەوکردن (CRP)", "پشکنینی تەواوی خوێن (CBC)"],
    "زۆر میزکردن و تینوێتی": ["شەکری ناو خوێن (FBS)", "شەکری کەڵەکەبوو (HbA1c)", "فەرمانی گورچیلە (KFT)"],
    "هەناسە تەنگی": ["پشکنینی تەواوی خوێن (CBC)", "کۆگای ئاسن (Ferritin)", "ترۆپۆنین (Troponin)"],
    "سووربوونەوەی پێست": ["هەوکردن (CRP)", "پشکنینی تەواوی خوێن (CBC)", "فەرمانی جگەر (LFT)"],
    "ورەوەری و خەمۆکی": ["هۆرمۆنی دەرەقی (TSH)", "پشکنینی تەواوی خوێن (CBC)", "کۆگای ئاسن (Ferritin)", "ڤیتامین دی (Vitamin D)"],
    "ئازاری سنگ": ["ترۆپۆنین (Troponin)", "چەورییەکانی خوێن (Lipid)", "پشکنینی تەواوی خوێن (CBC)"],
}

# ============================================
# ABBREVIATIONS DATABASE
# ============================================
LAB_ABBREVIATIONS = {
    "CBC": "Complete Blood Count - پشکنینی تەواوی خوێن (پێوانەی خڕۆکە سوورە و سپییەکان و پەڕەکانی خوێن)",
    "FBS": "Fasting Blood Sugar - شەکری ناو خوێن لە کاتی برسێتیدا (پێویستی بە ٨-١٢ کاتژمێر برسیبوونە)",
    "HbA1c": "Hemoglobin A1c - شەکری کەڵەکەبوو (تێکڕای شەکری خوێن لە ٢-٣ مانگی ڕابردوودا)",
    "TSH": "Thyroid Stimulating Hormone - هۆرمۆنی چالاککەری دەرەقی (بۆ پشکنینی کارکردنی غودەی تایرۆید)",
    "ALT": "Alanine Aminotransferase - ئەنزیمێکی جگەرە، بەرزبوونەوەی نیشانەی هەوکردن یان زیانگەیشتن بە جگەرە",
    "AST": "Aspartate Aminotransferase - ئەنزیمێکی جگەر و دڵ و ماسولکەیە، بەرزبوونەوە = تێکچوونی شانە",
    "ALP": "Alkaline Phosphatase - ئەنزیمێکی جگەر و ئێسکە، بەرزبوونەوە نیشانەی کێشەی جگەر یان ئێسکە",
    "GGT": "Gamma-Glutamyl Transferase - ئەنزیمێکی هەستیاری جگەر، بەرزبوونەوە = زیانی جگەر یان کحول",
    "HDL": "High-Density Lipoprotein - چەوری سوودبەخش (کۆلیسترۆڵی باش)، بەرزبوونەوەی باشە",
    "LDL": "Low-Density Lipoprotein - چەوری زیانبەخش (کۆلیسترۆڵی خراپ)، بەرزبوونەوە = مەترسی دڵ",
    "CRP": "C-Reactive Protein - پڕۆتینی کاردانەوەی هەوکردن، بەرزبوونەوە = هەوکردنی چالاک",
    "ESR": "Erythrocyte Sedimentation Rate - ڕێژەی نیشتنەوەی خڕۆکە سوورەکان، نیشاندەری هەوکردنە",
    "WBC": "White Blood Cells - خڕۆکە سپییەکانی خوێن (بەرگری لەش)، بەرزبوونەوە = هەوکردن",
    "RBC": "Red Blood Cells - خڕۆکە سوورەکانی خوێن (هەڵگری ئۆکسجین)، کەمبوونەوە = کەمخوێنی",
    "KFT": "Kidney Function Test - پشکنینی فەرمانی گورچیلە (کریاتینین و یوریا)",
    "LFT": "Liver Function Test - پشکنینی فەرمانی جگەر (ALT, AST, ALP, GGT, Bilirubin)",
    "PT": "Prothrombin Time - کاتی مەینبوونی خوێن (بۆ کۆنترۆڵکردنی دەرمانی وارفارین)",
    "INR": "International Normalized Ratio - ڕێژەی ستانداردی نێودەوڵەتی مەینبوونی خوێن",
    "BUN": "Blood Urea Nitrogen - نایترۆجینی یوریای خوێن (پاشماوەی گورچیلە)",
    "GFR": "Glomerular Filtration Rate - ڕێژەی فلتەرکردنی گورچیلە (پێوانەی کاری گورچیلە)",
}

# ============================================
# SAMPLE COLLECTION GUIDES
# ============================================
SAMPLE_GUIDES = {
    "پشکنینی تەواوی خوێن (CBC)": "💉 نموونەی خوێن لە خوێنهێنەر وەردەگیرێت. پێویست بە برسیبوون نییە. دەتوانیت ئاوی ئاسایی بخۆیتەوە. ٢٤ کاتژمێر پێش وەرزشی قورس مەکە.",
    "شەکری ناو خوێن (FBS)": "💉 **زۆر گرنگ:** پێویستە ٨-١٢ کاتژمێر برسی بیت (هیچ نەخۆیت). تەنها ئاوی ئاسایی ڕێگەپێدراوە. نموونە بەیانیان وەردەگیرێت.",
    "چەورییەکانی خوێن (Lipid)": "💉 پێویستە ١٢-١٤ کاتژمێر برسی بیت. ٢٤ کاتژمێر پێش وەرزشی قورس و ٤٨ کاتژمێر پێش کحول مەخۆ.",
    "فەرمانی گورچیلە (KFT)": "💉 پێویست بە برسیبوون نییە بەڵام باشترە ٨ کاتژمێر برسی بیت. ئاوی ئاسایی بخۆرەوە. وەرزشی قورس مەکە ٢٤ کاتژمێر پێش.",
    "فەرمانی جگەر (LFT)": "💉 پێویست بە برسیبوون نییە. بەڵام ئەگەر لەگەڵ پشکنینی تر بکرێت، ڕەنگە پێویست بە برسیبوون بکات. کحول مەخۆرەوە ٤٨ کاتژمێر پێش.",
    "هۆرمۆنی دەرەقی (TSH)": "💉 باشترین کات بەیانیانە. پێویست بە برسیبوون نییە. ئەگەر دەرمانی تایرۆید دەخۆیت، دوای وەرگرتنی نموونە بیخۆ.",
    "کۆگای ئاسن (Ferritin)": "💉 پێویست بە برسیبوون نییە. بەیانیان باشترە چونکە ئاستی ئاسن لە ڕۆژدا دەگۆڕێت.",
    "ترشی یۆریک (Uric Acid)": "💉 پێویست بە برسیبوون نییە. ٢٤ کاتژمێر پێش کحول و گۆشتی سوور کەم بکەرەوە.",
    "پشکنینی میز (Urinalysis)": "🧪 **نموونەی یەکەمی بەیانیان باشترە.** ناوچەکە بە ئاو و سابوون پاک بکەرەوە. یەکەم بەشی میز فڕێ بدە و ناوەڕاستی میزەکە لە دەفتەری تایبەت کۆبکەرەوە.",
    "چەورییەکانی خوێن (Lipid)": "💉 ١٢-١٤ کاتژمێر برسی بە. ٤٨ کاتژمێر پێش کحول مەخۆ. ئاوی ئاسایی ڕێگەپێدراوە.",
}

# ============================================
# UNIT CONVERSIONS
# ============================================
UNIT_CONVERSIONS = {
    "گلوکۆز (شەکر)": {"from": "mg/dL", "to": "mmol/L", "factor": 0.0555, "formula": "× 0.0555"},
    "کۆلیسترۆڵ": {"from": "mg/dL", "to": "mmol/L", "factor": 0.0259, "formula": "× 0.0259"},
    "Triglycerides": {"from": "mg/dL", "to": "mmol/L", "factor": 0.0113, "formula": "× 0.0113"},
    "کریاتینین": {"from": "mg/dL", "to": "µmol/L", "factor": 88.4, "formula": "× 88.4"},
    "بیلیڕۆبین": {"from": "mg/dL", "to": "µmol/L", "factor": 17.1, "formula": "× 17.1"},
    "کالیسیۆم": {"from": "mg/dL", "to": "mmol/L", "factor": 0.25, "formula": "× 0.25"},
    "هیمۆگڵۆبین": {"from": "g/dL", "to": "g/L", "factor": 10, "formula": "× 10"},
}

# ============================================
# FAQ DATABASE
# ============================================
FAQ_DATABASE = {
    "ئاساییترین ڕێژەی هیمۆگڵۆبین بۆ پیاوان چییە؟": "ڕێژەی ئاسایی هیمۆگڵۆبین بۆ پیاوان ١٣.٥-١٧.٥ g/dL یە. ئەگەر لەم ئاستە نزمتر بوو، نیشانەی کەمخوێنییە.",
    "بۆچی پشکنینی FBS دەکرێت؟": "بۆ دەستنیشانکردنی شەکرە. دەبێت ٨-١٢ کاتژمێر برسی بیت.",
    "کاری خڕۆکە سپییەکان چییە؟": "بەرگری لەش ڕێکدەخەن و دژە ڤایرۆس و بەکتریا دەجەنگن.",
    "هۆکاری بەرزبوونی یۆریک ئەسید چییە؟": "گۆشتی سوور، ماسی، کحول، یان کێشەی گورچیلە. دەبێتە هۆی Gout.",
    "پشکنینی TSH بۆ چییە؟": "بۆ چالاکی غودەی دەرەقی. بەرز = تەمەڵی، نزم = زۆر چالاکی.",
    "ڤیتامین B12 بۆ چییە؟": "بۆ تەندروستی دەمار و دروستکردنی خڕۆکە سوورەکان. کەمی = بێهێزی.",
    "CRP چییە؟": "نیشاندەری هەوکردنی چالاک لە لەشدا. بەرزبوونەوە = هەوکردن.",
    "ئاساییترین ڕێژەی کۆلیسترۆڵ چییە؟": "کەمتر لە ٢٠٠ mg/dL. بەرزتر = مەترسی نەخۆشی دڵ.",
    "فێریتین چییە؟": "کۆگای ئاسنی لەش. کەمی = کەمخوێنی و ڕووتانەوەی قژ.",
    "کەی پێویستە پشکنینی شەکرە بکەم؟": "لە تەمەنی ٤٥+ ساڵانە، یان زووتر ئەگەر مەترسیداریت (کێشی زیادە، مێژووی خێزان).",
    "جیاوازی FBS و HbA1c چییە؟": "FBS شەکری ئێستایە (برسیبوون دەوێت). HbA1c تێکڕای ٣ مانگە (برسیبوون ناوێت).",
    "چەند جارێک پشکنینی چەوری خوێن بکەم؟": "تەندروست: ٥ ساڵ جارێک. مەترسیدار: ساڵانە. لەژێر چارەسەری: ٣-٦ مانگ.",
    "نیشانەی کەمی ئاسن چییە؟": "بێهێزی، ماندوێتی، ڕووتانەوەی قژ، نینۆکی لاواز، و ڕەنگی پێستی کاڵ.",
    "ئایا ئاو خواردن پێش پشکنین ڕێگەی پێدراوە؟": "بەڵێ، ئاوی ئاسایی ڕێگەپێدراوە و تەنانەت پێشنیار دەکرێت.",
    "پۆتاسیۆم بۆچی گرنگە؟": "بۆ کارکردنی ماسولکە و دڵ. بەرزبوونەوە = مەترسی بۆ دڵ.",
}

# ============================================
# AI ANALYSIS ENGINE
# ============================================
def ai_analyze(test_name, user_value, gender="general"):
    matched_test = ALL_TESTS.get(test_name)
    
    if not matched_test:
        return create_result("unknown", user_value, "N/A", "N/A", "unit", test_name)
    
    ranges_text = matched_test['Ranges']
    range_matches = re.findall(r'(\d+\.?\d*)\s*-\s*(\d+\.?\d*)', ranges_text)
    
    if not range_matches:
        return create_result("unknown", user_value, "N/A", "N/A", "unit", matched_test['Name'])
    
    min_val = float(range_matches[0][0])
    max_val = float(range_matches[0][1])
    
    if gender == "male":
        for r, full_text in zip(range_matches, ranges_text.split('|')):
            if "پیاوان" in full_text:
                min_val, max_val = float(r[0]), float(r[1])
                break
    elif gender == "female":
        for r, full_text in zip(range_matches, ranges_text.split('|')):
            if "ژنان" in full_text:
                min_val, max_val = float(r[0]), float(r[1])
                break
    
    unit_match = re.search(r'([a-zA-Z/µ%]+)', ranges_text)
    unit = unit_match.group(1) if unit_match else "unit"
    
    if user_value < min_val:
        return create_result("low", user_value, min_val, max_val, unit, matched_test['Name'])
    elif user_value > max_val:
        critical = user_value > max_val * 1.5
        return create_result("critical" if critical else "high", user_value, min_val, max_val, unit, matched_test['Name'])
    else:
        return create_result("normal", user_value, min_val, max_val, unit, matched_test['Name'])

def create_result(status, user_value, min_val, max_val, unit, test_name):
    short_name = test_name.split('(')[0].strip() if '(' in test_name else test_name
    
    result = {
        "status": status, "user_value": user_value, "min_val": min_val,
        "max_val": max_val, "unit": unit, "test_name": short_name
    }
    
    if status == "normal":
        result.update({
            "emoji": "✅", "color_class": "result-normal",
            "status_text": "لە ئاستی ئاساییدایە 🎉",
            "meaning": f"ئەنجامی {short_name}ی تۆ ({user_value} {unit}) لە مەودای ئاسایی ({min_val}-{max_val} {unit}) دایە. ئەمە نیشانەیەکی زۆر باشە و ئەندامە پەیوەندیدارەکانت بە باشی کاردەکەن.",
            "action": "بەردەوام بە لەسەر شێوازی ژیانی تەندروست. پشکنینی ساڵانە ئەنجام بدە بۆ دڵنیابوونەوە."
        })
    elif status == "low":
        result.update({
            "emoji": "⚠️", "color_class": "result-abnormal",
            "status_text": "لە ئاستی ئاسایی نزمترە",
            "meaning": f"ئەنجامی {short_name}ی تۆ ({user_value} {unit}) لە مەودای ئاسایی ({min_val}-{max_val} {unit}) نزمترە. ئەمە ڕەنگە نیشانەی کێشەیەکی تەندروستی بێت.",
            "action": "پێشنیار دەکەم سەردانی پزیشکی پسپۆڕ بکەیت بۆ پشکنینی زیاتر و دەستنیشانکردنی هۆکاری سەرەکی."
        })
    elif status == "high":
        result.update({
            "emoji": "⚠️", "color_class": "result-abnormal",
            "status_text": "لە ئاستی ئاسایی بەرزترە",
            "meaning": f"ئەنجامی {short_name}ی تۆ ({user_value} {unit}) لە مەودای ئاسایی ({min_val}-{max_val} {unit}) بەرزترە. ئەمە پێویستی بە لێکۆڵینەوەی زیاترە.",
            "action": "پێشنیار دەکەم بە زووترین کات سەردانی پزیشکی پسپۆڕ بکەیت بۆ دەستنیشانکردنی ورد و چارەسەری گونجاو."
        })
    elif status == "critical":
        result.update({
            "emoji": "🚨", "color_class": "result-critical",
            "status_text": "زۆر بەرزە - مەترسیدارە!",
            "meaning": f"ئەنجامی {short_name}ی تۆ ({user_value} {unit}) زۆر لە مەودای ئاسایی ({min_val}-{max_val} {unit}) بەرزترە. ئەمە حاڵەتێکی مەترسیدارە و پێویستی بە چارەسەری خێرایە!",
            "action": "🚨 یەکسەر پەیوەندی بە پزیشکەوە بکە یان سەردانی نەخۆشخانە بکە! ئەم ئەنجامە مەترسیدارە."
        })
    else:
        result.update({
            "emoji": "❓", "color_class": "result-abnormal",
            "status_text": "پێویستی بە پشکنینی زیاترە",
            "meaning": f"ببورە، ناتوانم شیکاری ورد بۆ {short_name} بکەم. تکایە ئەنجامەکەت ببە بۆ پزیشکی پسپۆڕ.",
            "action": "تکایە ئەنجامەکەت ببە بۆ پزیشکی پسپۆڕ بۆ خوێندنەوەی ورد."
        })
    
    return result

# ============================================
# HEADER
# ============================================
st.markdown("""
<div class="main-header">
    <h1>🔬 ڕێبەری پشکنینە تاقیگەییەکان</h1>
    <p>شیکاری نیشانەکان | ڕوونکردنەوەی کورتکراوەکان | ڕێنمایی وەرگرتنی نموونە | گۆڕینی یەکەکان | یادخستنەوە</p>
</div>
""", unsafe_allow_html=True)

# ============================================
# MAIN TABS (7 Tabs)
# ============================================
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🔍 شیکاری نیشانەکان",
    "📋 پشکنینەکان", 
    "🧠 شیکاری ئەنجام",
    "📖 کورتکراوەکان",
    "🧪 ڕێنمایی وەرگرتن",
    "🔄 گۆڕینی یەکە",
    "⏰ یادخستنەوە"
])

# ============================================
# TAB 1: SYMPTOM CHECKER
# ============================================
with tab1:
    st.markdown("<h3 style='color:#4f46e5;text-align:center;'>🔍 شیکاری نیشانەکان - پێشنیاری پشکنین</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#6b7280;'>نیشانەکانت هەڵبژێرە بۆ ئەوەی پێشنیاری پشکنینی گونجاوت پێ بدرێت</p>", unsafe_allow_html=True)
    
    all_symptoms = list(SYMPTOM_TESTS.keys())
    selected_symptoms = []
    
    # Display symptoms in a nice grid
    for i in range(0, len(all_symptoms), 4):
        cols = st.columns(4)
        for j in range(4):
            idx = i + j
            if idx < len(all_symptoms):
                symptom = all_symptoms[idx]
                with cols[j]:
                    if st.button(symptom, key=f"symptom_{idx}", use_container_width=True):
                        if symptom not in selected_symptoms:
                            selected_symptoms.append(symptom)
    
    if selected_symptoms:
        st.markdown("<hr style='margin:20px 0;'>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:0.9rem;'><b>✅ نیشانە هەڵبژێردراوەکان:</b> {', '.join(selected_symptoms)}</p>", unsafe_allow_html=True)
        
        recommended_tests = set()
        for symptom in selected_symptoms:
            for test in SYMPTOM_TESTS.get(symptom, []):
                recommended_tests.add(test)
        
        st.markdown(f"<div class='badge'>🔬 پشکنینە پێشنیارکراوەکان ({len(recommended_tests)})</div>", unsafe_allow_html=True)
        
        for test in recommended_tests:
            st.markdown(f"""<div class="result-info result-box">🔬 <b>{test}</b></div>""", unsafe_allow_html=True)

# ============================================
# TAB 2: ALL TESTS
# ============================================
with tab2:
    st.markdown("<h3 style='color:#4f46e5;text-align:center;'>📋 هەموو پشکنینەکان</h3>", unsafe_allow_html=True)
    
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
            if cat not in categories_display: categories_display[cat] = {}
            categories_display[cat][key] = test
        
        for category, tests in categories_display.items():
            st.markdown(f"<div class='badge'>📂 {category}</div>", unsafe_allow_html=True)
            
            for test_key, test in tests.items():
                with st.expander(f"{test['Icon']} {test['Name'][:55]}... | 🫀 {test['Organ']}"):
                    st.markdown(f"""<div class="glass-card"><p><b>📝 وەسف:</b> {test['Description']}</p><p><b>📊 ڕێژە ئاساییەکان:</b></p><p style="background:#f3f4f6;padding:10px 14px;border-radius:8px;font-size:0.85rem;">{test['Ranges']}</p></div>""", unsafe_allow_html=True)
                    if 'FoodRecommendations' in test:
                        st.markdown(f"""<div class="food-card"><h4>🥗 ڕێنمایی خۆراکی</h4><p>{test['FoodRecommendations']}</p></div>""", unsafe_allow_html=True)

# ============================================
# TAB 3: AI ANALYSIS
# ============================================
with tab3:
    st.markdown("<h3 style='color:#4f46e5;text-align:center;'>🧠 شیکاری زیرەکی ئەنجامەکان</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        test_choice = st.selectbox("🔬 پشکنین:", list(ALL_TESTS.keys()), key="ai_test")
        gender_choice = st.selectbox("👤 ڕەگەز:", ["general", "male", "female"], format_func=lambda x: {"general":"گشتی","male":"پیاوان","female":"ژنان"}[x], key="ai_gender")
    with col2:
        unit_choice = st.text_input("📏 یەکە:", value="mg/dL", key="ai_unit")
        user_result = st.number_input("🔢 ئەنجام:", value=0.0, step=0.1, format="%.1f", key="ai_value")
    
    doctor_note = st.text_area("📝 تێبینی پزیشک (ئارەزوومەندانە):", placeholder="بۆ نموونە: ئەم پشکنینەم کرد کاتێک نەخۆش بووم...", key="doctor_note")
    
    if st.button("🔍 شیکاری بکە", key="ai_btn", use_container_width=True):
        if user_result > 0:
            with st.spinner("🧠 سیستەم ئەنجامەکەت شیدەکاتەوە..."):
                time.sleep(0.8)
                result = ai_analyze(test_choice, user_result, gender_choice)
                
                st.markdown(f"""
                <div class="glass-card">
                    <div class="{result['color_class']}">
                        <span style="font-size:1.8rem;">{result['emoji']}</span>
                        <b>{result['test_name']}</b> - {result['status_text']}
                    </div>
                    <p style="margin-top:12px;"><b>📊 ئەنجامی تۆ:</b> {result['user_value']} {result['unit']}</p>
                    <p><b>📏 مەودای ئاسایی:</b> {result['min_val']} - {result['max_val']} {result['unit']}</p>
                    <p><b>📋 شیکاری:</b> {result['meaning']}</p>
                    <p><b>💊 ڕێنمایی:</b> {result['action']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.session_state.history.append({
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "test": test_choice, "value": user_result,
                    "unit": unit_choice, "status": result['status'], "note": doctor_note
                })
                
                if doctor_note:
                    st.markdown(f"""<div class="result-info result-box"><b>📝 تێبینی تۆمارکراو:</b> {doctor_note}</div>""", unsafe_allow_html=True)
                
                test_data = ALL_TESTS.get(test_choice, {})
                if 'FoodRecommendations' in test_data:
                    st.markdown(f"""<div class="food-card"><h4>🥗 ڕێنمایی خۆراکی</h4><p>{test_data['FoodRecommendations']}</p></div>""", unsafe_allow_html=True)
        else:
            st.warning("تکایە ئەنجامێکی دروست بنووسە")

# ============================================
# TAB 4: ABBREVIATIONS
# ============================================
with tab4:
    st.markdown("<h3 style='color:#4f46e5;text-align:center;'>📖 ڕوونکردنەوەی کورتکراوە تاقیگەییەکان</h3>", unsafe_allow_html=True)
    
    abbr_search = st.text_input("🔍 کورتکراوە بنووسە:", placeholder="بۆ نموونە: ALT, CBC, TSH, HDL...", key="abbr_search")
    
    if abbr_search:
        abbr_upper = abbr_search.upper().strip()
        if abbr_upper in LAB_ABBREVIATIONS:
            st.markdown(f"""<div class="result-info result-box"><h4>🔤 {abbr_upper}</h4><p>{LAB_ABBREVIATIONS[abbr_upper]}</p></div>""", unsafe_allow_html=True)
        else:
            st.warning("کورتکراوەکە نەدۆزرایەوە")
    else:
        st.markdown("<p style='color:#6b7280;text-align:center;'>کورتکراوەیەک بنووسە یان لە خوارەوە هەڵبژێرە</p>", unsafe_allow_html=True)
        st.markdown("<div class='badge'>📌 باوترین کورتکراوەکان</div>", unsafe_allow_html=True)
        
        popular = ["CBC", "FBS", "HbA1c", "TSH", "ALT", "AST", "HDL", "LDL", "CRP", "KFT", "LFT", "WBC", "ESR", "PT", "INR", "GFR"]
        cols = st.columns(4)
        for i, abbr in enumerate(popular):
            with cols[i % 4]:
                if st.button(f"🔤 {abbr}", key=f"abbr_{abbr}", use_container_width=True):
                    st.info(f"**{abbr}**: {LAB_ABBREVIATIONS[abbr]}")

# ============================================
# TAB 5: SAMPLE COLLECTION
# ============================================
with tab5:
    st.markdown("<h3 style='color:#4f46e5;text-align:center;'>🧪 ڕێنمایی وەرگرتنی نموونە</h3>", unsafe_allow_html=True)
    
    sample_test = st.selectbox("پشکنین هەڵبژێرە:", list(SAMPLE_GUIDES.keys()), key="sample_test")
    
    if sample_test:
        st.markdown(f"""<div class="glass-card"><div class="result-info result-box"><h4>🧪 {sample_test}</h4><p style="font-size:1.05rem;line-height:1.9;">{SAMPLE_GUIDES[sample_test]}</p></div></div>""", unsafe_allow_html=True)
    
    st.markdown("<div class='badge'>💡 ڕێنمایی گشتی بۆ هەموو پشکنینەکان</div>", unsafe_allow_html=True)
    st.markdown("""<div class="glass-card">
        <p>✅ ئاوی ئاسایی بخۆرەوە پێش پشکنین</p>
        <p>✅ دەرمانەکانت بەردەوام بە بەڵام بە پزیشکت بڵێ</p>
        <p>✅ ٢٤ کاتژمێر پێش پشکنین وەرزشی قورس مەکە</p>
        <p>❌ ٤٨ کاتژمێر پێش پشکنین کحول مەخۆرەوە</p>
        <p>❌ ٢ کاتژمێر پێش پشکنین جگەرە مەکێشە</p>
    </div>""", unsafe_allow_html=True)

# ============================================
# TAB 6: UNIT CONVERTER
# ============================================
with tab6:
    st.markdown("<h3 style='color:#4f46e5;text-align:center;'>🔄 گۆڕینی یەکەکان</h3>", unsafe_allow_html=True)
    
    conversion_choice = st.selectbox("جۆری پشکنین:", list(UNIT_CONVERSIONS.keys()), key="conv_choice")
    
    if conversion_choice:
        conv = UNIT_CONVERSIONS[conversion_choice]
        
        col1, col2, col3 = st.columns([2, 1, 2])
        with col1:
            from_value = st.number_input(f"بڕ بە {conv['from']}:", value=100.0, step=0.1, key="conv_from")
        with col2:
            st.markdown("<div style='text-align:center;padding-top:35px;font-size:2rem;'>➡️</div>", unsafe_allow_html=True)
        with col3:
            to_value = from_value * conv['factor']
            st.metric(f"بڕ بە {conv['to']}:", f"{to_value:.2f}")
        
        st.markdown(f"""<div class="result-info result-box"><p><b>📐 هاوکۆلکە:</b> 1 {conv['from']} {conv['formula']} = {conv['to']}</p><p><b>📊 ئەنجام:</b> {from_value} {conv['from']} = {to_value:.2f} {conv['to']}</p></div>""", unsafe_allow_html=True)

# ============================================
# TAB 7: REMINDERS
# ============================================
with tab7:
    st.markdown("<h3 style='color:#4f46e5;text-align:center;'>⏰ یادخستنەوەی پشکنین</h3>", unsafe_allow_html=True)
    
    with st.expander("➕ زیادکردنی یادخستنەوەی نوێ", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            reminder_test = st.selectbox("جۆری پشکنین:", list(ALL_TESTS.keys()), key="reminder_test")
        with col2:
            reminder_freq = st.selectbox("دووبارەبوونەوە:", ["ڕۆژانە", "هەفتانە", "مانگانە", "سێ مانگ جارێک", "شەش مانگ جارێک", "ساڵانە"], key="reminder_freq")
        reminder_note = st.text_input("📝 تێبینی:", placeholder="بۆ نموونە: پشکنینی شەکری مانگانە...", key="reminder_note")
        
        if st.button("💾 تۆمارکردنی یادخستنەوە", key="save_reminder", use_container_width=True):
            st.session_state.reminders.append({
                "test": reminder_test, "frequency": reminder_freq,
                "note": reminder_note, "created": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            st.success("✅ یادخستنەوەکە بە سەرکەوتوویی تۆمارکرا!")
            st.rerun()
    
    if st.session_state.reminders:
        st.markdown(f"<div class='badge'>📅 یادخستنەوەکانت ({len(st.session_state.reminders)})</div>", unsafe_allow_html=True)
        for i, reminder in enumerate(st.session_state.reminders):
            st.markdown(f"""<div class="reminder-card"><b>🔬 {reminder['test']}</b><br>🔄 {reminder['frequency']} | 📝 {reminder['note']}<br><span style="color:#6b7280;font-size:0.8rem;">📅 تۆمارکراو: {reminder['created']}</span></div>""", unsafe_allow_html=True)
    else:
        st.info("هێشتا هیچ یادخستنەوەیەکت نییە")
    
    st.markdown("<div class='badge badge-yellow'>💡 یادخستنەوەی گشتی بۆ نەخۆشییە درێژخایەنەکان</div>", unsafe_allow_html=True)
    st.markdown("""<div class="glass-card">
        <p><b>🍬 شەکرە:</b> FBS مانگانە | HbA1c هەر ٣ مانگ</p>
        <p><b>❤️ پەستانی خوێن:</b> پێوانەکردن هەفتانە | Lipid Profile ساڵانە</p>
        <p><b>🦋 دەرەقی:</b> TSH هەر ٦-١٢ مانگ</p>
        <p><b>🫘 گورچیلە:</b> KFT هەر ٣-٦ مانگ</p>
    </div>""", unsafe_allow_html=True)

# ============================================
# HISTORY & EXPORT SECTION
# ============================================
with st.expander("📊 مێژووی ئەنجامەکانت و هەناردەکردن", expanded=False):
    if len(st.session_state.history) > 0:
        df = pd.DataFrame(st.session_state.history)
        st.dataframe(df, use_container_width=True)
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 دابەزاندنی مێژوو بە CSV", csv, "my_lab_results.csv", "text/csv")
    else:
        st.info("هێشتا هیچ ئەنجامێکت تۆمار نەکردووە")

# ============================================
# FOOTER
# ============================================
st.markdown("""<div class="glass-card" style="text-align:center;margin-top:20px;"><div class="result-critical" style="text-align:center;"><p style="margin:0;font-weight:700;">⚠️ ئەم سیستەمە تەنها بۆ ڕێنمایی سەرەتاییە و جێگەی سەردانی پزیشک ناگرێتەوە</p></div><p style="color:#6b7280;margin-top:10px;">© ٢٠٢٤ ڕێبەری پشکنینە تاقیگەییەکان | ٣٠+ پشکنین | ٧ بەشی تایبەت</p></div>""", unsafe_allow_html=True)
