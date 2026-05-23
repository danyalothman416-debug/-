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

# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="ڕێبەری پشکنینە تاقیگەییەکان - Danyal Ismail", 
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
if 'selected_symptoms' not in st.session_state:
    st.session_state.selected_symptoms = []

# ============================================
# CSS - NO ARROW GLITCHES, CLEAR SELECTS, COMPACT TEXT
# ============================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Naskh+Arabic:wght@400;500;600;700;800;900&display=swap');
    
    * { font-family: 'Noto Naskh Arabic', 'Segoe UI', sans-serif !important; }
    [data-testid="stSidebar"] { display: none; }
    
    /* Hide ALL SVG icons including Streamlit arrows */
    svg { display: none !important; }
    [data-testid="stExpanderToggle"] { display: none !important; }
    .streamlit-expanderHeader svg { display: none !important; }
    
    /* Custom expander arrow */
    .streamlit-expanderHeader::before { content: '▼ '; font-size: 9px; color: #6b7280; margin-left: 6px; font-family: Arial; }
    
    html, body, [data-testid="stAppViewContainer"] { background: #f8fafc !important; }
    
    /* Logo */
    .logo-badge { display: inline-flex; align-items: center; gap: 6px; background: linear-gradient(135deg, #4f46e5, #7c3aed); color: white; padding: 5px 12px; border-radius: 20px; font-size: 0.7rem; font-weight: 700; box-shadow: 0 3px 10px rgba(79,70,229,0.25); margin-bottom: 8px; }
    .logo-icon { width: 18px; height: 18px; background: white; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-size: 0.6rem; color: #4f46e5; font-weight: 900; }
    
    /* Header */
    .main-header { background: linear-gradient(135deg, #1e1b4b 0%, #4f46e5 50%, #7c3aed 100%); border-radius: 18px; padding: 18px; text-align: center; margin-bottom: 12px; box-shadow: 0 8px 25px rgba(79,70,229,0.2); }
    .main-header h1 { color: white !important; font-size: 1.4rem !important; font-weight: 900 !important; margin: 0 0 3px 0 !important; }
    .main-header p { color: rgba(255,255,255,0.85) !important; font-size: 0.72rem !important; margin: 0 !important; }
    .dev-credit { text-align: center; font-size: 0.68rem; color: #6b7280; margin-bottom: 10px; }
    .dev-credit span { color: #4f46e5; font-weight: 700; }
    
    /* Cards */
    .glass-card { background: white !important; border-radius: 12px !important; padding: 12px !important; margin-bottom: 10px !important; box-shadow: 0 2px 6px rgba(0,0,0,0.03) !important; border: 1px solid #e5e7eb !important; font-size: 0.78rem !important; }
    
    /* CLEAR SELECT BOXES */
    .stSelectbox label { color: #374151 !important; font-size: 0.75rem !important; font-weight: 600 !important; }
    .stSelectbox > div > div { background: white !important; border: 2px solid #d1d5db !important; border-radius: 8px !important; font-size: 0.78rem !important; color: #1f2937 !important; min-height: 35px !important; }
    .stSelectbox > div > div:hover { border-color: #4f46e5 !important; }
    
    /* CLEAR INPUTS */
    .stTextInput label, .stNumberInput label, .stTextArea label { color: #374151 !important; font-size: 0.75rem !important; font-weight: 600 !important; }
    .stTextInput input, .stNumberInput input, .stTextArea textarea { background: white !important; border: 2px solid #d1d5db !important; border-radius: 8px !important; color: #1f2937 !important; padding: 7px 10px !important; font-size: 0.78rem !important; }
    .stTextInput input:focus, .stNumberInput input:focus { border-color: #4f46e5 !important; box-shadow: 0 0 0 3px rgba(79,70,229,0.06) !important; }
    
    /* Buttons */
    .stButton button { background: linear-gradient(135deg, #4f46e5, #7c3aed) !important; color: white !important; border: none !important; font-weight: 600 !important; border-radius: 10px !important; padding: 7px 16px !important; font-size: 0.78rem !important; box-shadow: 0 3px 10px rgba(79,70,229,0.2) !important; }
    .stButton button:hover { transform: translateY(-2px) !important; box-shadow: 0 5px 15px rgba(79,70,229,0.35) !important; }
    
    /* Results */
    .result-box { border-radius: 8px; padding: 10px; margin: 6px 0; font-size: 0.78rem; line-height: 1.6; }
    .result-normal { background: #f0fdf4; border-left: 4px solid #10b981; }
    .result-abnormal { background: #fffbeb; border-left: 4px solid #f59e0b; }
    .result-critical { background: #fef2f2; border-left: 4px solid #ef4444; }
    .result-info { background: #eff6ff; border-left: 4px solid #3b82f6; }
    
    .food-card { background: #fffbeb; border: 1px solid #fde68a; border-radius: 10px; padding: 10px; margin: 6px 0; font-size: 0.76rem; }
    
    .badge { display: inline-block; background: #eef2ff; border: 1px solid #c7d2fe; border-radius: 15px; padding: 4px 12px; margin: 6px 0 5px 0; font-weight: 700; color: #3730a3 !important; font-size: 0.73rem; }
    
    .reminder-card { background: white; border-radius: 10px; padding: 10px; margin: 5px 0; border: 1px solid #e5e7eb; border-left: 3px solid #4f46e5; font-size: 0.76rem; }
    
    /* Expander */
    .streamlit-expanderHeader { background: #f9fafb !important; border-radius: 8px !important; border: 1px solid #e5e7eb !important; color: #1f2937 !important; font-weight: 600 !important; font-size: 0.78rem !important; padding: 7px 10px !important; }
    .streamlit-expanderHeader:hover { background: #f0f4ff !important; }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 3px; background: white !important; border-radius: 10px; padding: 3px; box-shadow: 0 1px 3px rgba(0,0,0,0.02); flex-wrap: wrap; }
    .stTabs [data-baseweb="tab"] { background: transparent !important; border-radius: 8px !important; color: #374151 !important; padding: 5px 7px !important; font-weight: 600 !important; font-size: 0.7rem !important; }
    .stTabs [aria-selected="true"] { background: linear-gradient(135deg, #4f46e5, #7c3aed) !important; color: white !important; }
    
    h3 { font-size: 1rem !important; margin-bottom: 6px !important; }
    h4 { font-size: 0.88rem !important; }
    p { font-size: 0.76rem !important; }
    
    [dir="rtl"] { text-align: right !important; direction: rtl !important; }
</style>
""", unsafe_allow_html=True)

# ============================================
# LOGO + HEADER
# ============================================
st.markdown("""
<div style="text-align:center;">
    <div class="logo-badge">
        <span class="logo-icon">DI</span>
        Danyal Ismail
    </div>
</div>
<div class="main-header">
    <h1>🔬 ڕێبەری پشکنینە تاقیگەییەکان</h1>
    <p>شیکاری نیشانەکان | کورتکراوەکان | ڕێنمایی وەرگرتن | گۆڕینی یەکە | یادخستنەوە</p>
</div>
<div class="dev-credit">
    پەرەپێدراو لەلایەن <span>Danyal Ismail</span>
</div>
""", unsafe_allow_html=True)

# ============================================
# COMPLETE DATABASE - ALL 25+ TESTS
# ============================================
ALL_TESTS = {
    "پشکنینی تەواوی خوێن (CBC)": {
        "Name": "پشکنینی تەواوی خوێن (CBC)", "Category": "پشکنینە بنەڕەتییەکان", "Organ": "خوێن", "Icon": "🩸",
        "Description": "پێوانەی پێکهاتەکانی خوێن: خڕۆکە سوورەکان، خڕۆکە سپییەکان و پەڕەکانی خوێن. یارمەتیدەرە بۆ دەستنیشانکردنی کەمخوێنی (ئەنیمیا)، هەوکردن، و کێشەکانی مەینبوونی خوێن.",
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
    "پشکنینی میز (Urinalysis)": {
        "Name": "پشکنینی تەواوی میز (Urinalysis)", "Category": "پشکنینە بنەڕەتییەکان", "Organ": "گورچیلە / میزەڕۆ", "Icon": "🧪",
        "Description": "پشکنینی جەستەیی و کیمیایی میز بۆ دەستنیشانکردنی هەوکردن، کێشەی گورچیلە، یان شەکرە.",
        "Ranges": "ڕەنگ: زەردی کاڵ | pH: 4.5-8.0 | پرۆتین و گلوکۆز: نەبێت | WBC: 0-5 /HPF | RBC: 0-3 /HPF",
        "FoodRecommendations": "💧 ئاوی زۆر | 🫐 قەرەکەمەری | ❌ دوور لە خواردنی تیژ"
    },
}

# ============================================
# SYMPTOM MAPPING
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
# ABBREVIATIONS
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
# SAMPLE GUIDES
# ============================================
SAMPLE_GUIDES = {
    "پشکنینی تەواوی خوێن (CBC)": "💉 نموونەی خوێن لە خوێنهێنەر وەردەگیرێت. پێویست بە برسیبوون نییە. دەتوانیت ئاوی ئاسایی بخۆیتەوە.",
    "شەکری ناو خوێن (FBS)": "💉 پێویستە ٨-١٢ کاتژمێر برسی بیت. تەنها ئاوی ئاسایی ڕێگەپێدراوە. نموونە بەیانیان وەردەگیرێت.",
    "چەورییەکانی خوێن (Lipid)": "💉 پێویستە ١٢-١٤ کاتژمێر برسی بیت. ٤٨ کاتژمێر پێش کحول مەخۆ.",
    "فەرمانی گورچیلە (KFT)": "💉 باشترە ٨ کاتژمێر برسی بیت. ئاوی ئاسایی بخۆرەوە.",
    "فەرمانی جگەر (LFT)": "💉 پێویست بە برسیبوون نییە. کحول مەخۆرەوە ٤٨ کاتژمێر پێش.",
    "هۆرمۆنی دەرەقی (TSH)": "💉 باشترین کات بەیانیانە. ئەگەر دەرمانی تایرۆید دەخۆیت، دوای پشکنین بیخۆ.",
    "کۆگای ئاسن (Ferritin)": "💉 پێویست بە برسیبوون نییە. بەیانیان باشترە.",
    "ترشی یۆریک (Uric Acid)": "💉 پێویست بە برسیبوون نییە. ٢٤ کاتژمێر پێش گۆشتی سوور کەم بکەرەوە.",
    "پشکنینی میز (Urinalysis)": "🧪 نموونەی یەکەمی بەیانیان باشترە. ناوچەکە پاک بکەرەوە و ناوەڕاستی میزەکە کۆبکەرەوە.",
}

# ============================================
# UNIT CONVERSIONS
# ============================================
UNIT_CONVERSIONS = {
    "گلوکۆز (شەکر)": {"from": "mg/dL", "to": "mmol/L", "factor": 0.0555},
    "کۆلیسترۆڵ": {"from": "mg/dL", "to": "mmol/L", "factor": 0.0259},
    "Triglycerides": {"from": "mg/dL", "to": "mmol/L", "factor": 0.0113},
    "کریاتینین": {"from": "mg/dL", "to": "µmol/L", "factor": 88.4},
    "بیلیڕۆبین": {"from": "mg/dL", "to": "µmol/L", "factor": 17.1},
    "کالیسیۆم": {"from": "mg/dL", "to": "mmol/L", "factor": 0.25},
    "هیمۆگڵۆبین": {"from": "g/dL", "to": "g/L", "factor": 10},
}

# ============================================
# AI ANALYSIS
# ============================================
def ai_analyze(test_name, user_value, gender="general"):
    matched_test = ALL_TESTS.get(test_name)
    if not matched_test:
        return {"emoji":"❓","color_class":"result-abnormal","status_text":"نەناسراو","meaning":"ناتوانم شیکاری بکەم","action":"سەردانی پزیشک بکە","user_value":user_value,"unit":"","min_val":"N/A","max_val":"N/A","test_name":test_name}
    
    ranges_text = matched_test['Ranges']
    range_matches = re.findall(r'(\d+\.?\d*)\s*-\s*(\d+\.?\d*)', ranges_text)
    if not range_matches:
        return {"emoji":"❓","color_class":"result-abnormal","status_text":"نەدۆزرایەوە","meaning":"ڕێژەکان نەدۆزرانەوە","action":"سەردانی پزیشک بکە","user_value":user_value,"unit":"","min_val":"N/A","max_val":"N/A","test_name":matched_test['Name']}
    
    min_val = float(range_matches[0][0]); max_val = float(range_matches[0][1])
    
    if gender == "male":
        for r, ft in zip(range_matches, ranges_text.split('|')):
            if "پیاوان" in ft: min_val, max_val = float(r[0]), float(r[1]); break
    elif gender == "female":
        for r, ft in zip(range_matches, ranges_text.split('|')):
            if "ژنان" in ft: min_val, max_val = float(r[0]), float(r[1]); break
    
    unit_match = re.search(r'([a-zA-Z/µ%]+)', ranges_text)
    unit = unit_match.group(1) if unit_match else "unit"
    short_name = matched_test['Name'].split('(')[0].strip()
    
    if user_value < min_val:
        return {"emoji":"⚠️","color_class":"result-abnormal","status_text":"لە ئاستی ئاسایی نزمترە","meaning":f"ئەنجامی {short_name}ی تۆ ({user_value} {unit}) لە مەودای ئاسایی ({min_val}-{max_val} {unit}) نزمترە. پێویستە لێکۆڵینەوەی زیاتر بکرێت.","action":"پێشنیار دەکەم سەردانی پزیشکی پسپۆڕ بکەیت.","user_value":user_value,"unit":unit,"min_val":min_val,"max_val":max_val,"test_name":short_name}
    elif user_value > max_val:
        critical = user_value > max_val * 1.5
        return {"emoji":"🚨","color_class":"result-critical" if critical else "result-abnormal","status_text":"زۆر بەرزە - مەترسیدار!" if critical else "لە ئاستی ئاسایی بەرزترە","meaning":f"ئەنجامی {short_name}ی تۆ ({user_value} {unit}) لە مەودای ئاسایی ({min_val}-{max_val} {unit}) بەرزترە.","action":"یەکسەر پەیوەندی بە پزیشکەوە بکە!" if critical else "پێشنیار دەکەم بە زووترین کات سەردانی پزیشک بکەیت.","user_value":user_value,"unit":unit,"min_val":min_val,"max_val":max_val,"test_name":short_name}
    else:
        return {"emoji":"✅","color_class":"result-normal","status_text":"لە ئاستی ئاساییدایە 🎉","meaning":f"ئەنجامی {short_name}ی تۆ ({user_value} {unit}) لە مەودای ئاسایی ({min_val}-{max_val} {unit}) دایە. ئەمە نیشانەیەکی زۆر باشە!","action":"بەردەوام بە لەسەر شێوازی ژیانی تەندروست.","user_value":user_value,"unit":unit,"min_val":min_val,"max_val":max_val,"test_name":short_name}

# ============================================
# TABS (7 Tabs)
# ============================================
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🔍 نیشانەکان", "📋 پشکنینەکان", "🧠 شیکاری", 
    "📖 کورتکراوە", "🧪 وەرگرتن", "🔄 یەکە", "⏰ یادخستنەوە"
])

# ============================================
# TAB 1: SYMPTOM CHECKER
# ============================================
with tab1:
    st.markdown("<h3 style='color:#4f46e5;text-align:center;'>🔍 شیکاری نیشانەکان</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#6b7280;font-size:0.78rem;'>نیشانەکانت هەڵبژێرە بۆ پێشنیاری پشکنینی گونجاو</p>", unsafe_allow_html=True)
    
    all_symptoms = list(SYMPTOM_TESTS.keys())
    
    for i in range(0, len(all_symptoms), 4):
        cols = st.columns(4)
        for j in range(4):
            idx = i + j
            if idx < len(all_symptoms):
                symptom = all_symptoms[idx]
                with cols[j]:
                    if st.button(symptom, key=f"s_{idx}", use_container_width=True):
                        if symptom not in st.session_state.selected_symptoms:
                            st.session_state.selected_symptoms.append(symptom)
                        else:
                            st.session_state.selected_symptoms.remove(symptom)
                        st.rerun()
    
    if st.session_state.selected_symptoms:
        st.markdown(f"<p style='font-size:0.78rem;margin-top:10px;'><b>✅ نیشانەکان:</b> {', '.join(st.session_state.selected_symptoms)}</p>", unsafe_allow_html=True)
        recommended = set()
        for s in st.session_state.selected_symptoms:
            for t in SYMPTOM_TESTS.get(s, []): recommended.add(t)
        st.markdown(f"<div class='badge'>🔬 پێشنیارکراوە ({len(recommended)})</div>", unsafe_allow_html=True)
        for t in recommended:
            st.markdown(f"""<div class="result-info result-box">🔬 <b>{t}</b></div>""", unsafe_allow_html=True)

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
        if search_text and search_text.lower() not in key.lower(): continue
        if selected_organ != "هەموو" and test['Organ'] != selected_organ: continue
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
                with st.expander(f"{test['Icon']} {test['Name'][:55]}... | {test['Organ']}"):
                    st.markdown(f"""<div class="glass-card"><p><b>📝 وەسف:</b> {test['Description']}</p><p><b>📊 ڕێژە ئاساییەکان:</b></p><p style="background:#f3f4f6;padding:8px 10px;border-radius:6px;font-size:0.75rem;">{test['Ranges']}</p></div>""", unsafe_allow_html=True)
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
    
    doctor_note = st.text_area("📝 تێبینی پزیشک:", placeholder="بۆ نموونە: ئەم پشکنینەم کرد کاتێک نەخۆش بووم...", key="doctor_note")
    
    if st.button("🔍 شیکاری بکە", key="ai_btn", use_container_width=True):
        if user_result > 0:
            with st.spinner("🧠 سیستەم ئەنجامەکەت شیدەکاتەوە..."):
                time.sleep(0.8)
                result = ai_analyze(test_choice, user_result, gender_choice)
                
                st.markdown(f"""<div class="glass-card"><div class="{result['color_class']}"><span style="font-size:1.5rem;">{result['emoji']}</span> <b>{result['test_name']}</b> - {result['status_text']}</div><p style="margin-top:8px;"><b>📊 ئەنجامی تۆ:</b> {result['user_value']} {result['unit']}</p><p><b>📏 مەودای ئاسایی:</b> {result['min_val']} - {result['max_val']} {result['unit']}</p><p><b>📋 شیکاری:</b> {result['meaning']}</p><p><b>💊 ڕێنمایی:</b> {result['action']}</p></div>""", unsafe_allow_html=True)
                
                st.session_state.history.append({"date":datetime.now().strftime("%Y-%m-%d %H:%M"),"test":test_choice,"value":user_result,"unit":unit_choice,"status":result['status'],"note":doctor_note})
                
                if doctor_note:
                    st.markdown(f"""<div class="result-info result-box"><b>📝 تێبینی:</b> {doctor_note}</div>""", unsafe_allow_html=True)
                
                test_data = ALL_TESTS.get(test_choice, {})
                if 'FoodRecommendations' in test_data:
                    st.markdown(f"""<div class="food-card"><h4>🥗 ڕێنمایی خۆراکی</h4><p>{test_data['FoodRecommendations']}</p></div>""", unsafe_allow_html=True)
        else:
            st.warning("تکایە ئەنجامێکی دروست بنووسە")

# ============================================
# TAB 4: ABBREVIATIONS
# ============================================
with tab4:
    st.markdown("<h3 style='color:#4f46e5;text-align:center;'>📖 ڕوونکردنەوەی کورتکراوەکان</h3>", unsafe_allow_html=True)
    
    abbr_search = st.text_input("🔍 کورتکراوە بنووسە:", placeholder="بۆ نموونە: ALT, CBC, TSH...", key="abbr_search")
    
    if abbr_search:
        abbr_upper = abbr_search.upper().strip()
        if abbr_upper in LAB_ABBREVIATIONS:
            st.markdown(f"""<div class="result-info result-box"><h4>🔤 {abbr_upper}</h4><p>{LAB_ABBREVIATIONS[abbr_upper]}</p></div>""", unsafe_allow_html=True)
        else:
            st.warning("کورتکراوەکە نەدۆزرایەوە")
    else:
        st.markdown("<div class='badge'>📌 باوترین کورتکراوەکان</div>", unsafe_allow_html=True)
        popular = ["CBC","FBS","HbA1c","TSH","ALT","AST","HDL","LDL","CRP","KFT","LFT","WBC","ESR","PT","INR","GFR"]
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
        st.markdown(f"""<div class="glass-card"><div class="result-info result-box"><h4>🧪 {sample_test}</h4><p style="font-size:0.85rem;line-height:1.8;">{SAMPLE_GUIDES[sample_test]}</p></div></div>""", unsafe_allow_html=True)
    
    st.markdown("<div class='badge'>💡 ڕێنمایی گشتی</div>", unsafe_allow_html=True)
    st.markdown("""<div class="glass-card"><p>✅ ئاوی ئاسایی بخۆرەوە | ✅ دەرمانەکانت بەردەوام بە | ❌ ٤٨ کاتژمێر پێش کحول مەخۆ | ❌ جگەرە مەکێشە ٢ کاتژمێر پێش</p></div>""", unsafe_allow_html=True)

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
            st.markdown("<div style='text-align:center;padding-top:30px;font-size:1.5rem;'>→</div>", unsafe_allow_html=True)
        with col3:
            to_value = from_value * conv['factor']
            st.metric(f"بڕ بە {conv['to']}:", f"{to_value:.2f}")
        st.markdown(f"""<div class="result-info result-box"><p><b>📐</b> 1 {conv['from']} = {conv['factor']} {conv['to']}</p></div>""", unsafe_allow_html=True)

# ============================================
# TAB 7: REMINDERS
# ============================================
with tab7:
    st.markdown("<h3 style='color:#4f46e5;text-align:center;'>⏰ یادخستنەوەی پشکنین</h3>", unsafe_allow_html=True)
    
    with st.expander("➕ زیادکردنی یادخستنەوە", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            reminder_test = st.selectbox("جۆری پشکنین:", list(ALL_TESTS.keys()), key="reminder_test")
        with col2:
            reminder_freq = st.selectbox("دووبارەبوونەوە:", ["مانگانە","سێ مانگ جارێک","شەش مانگ جارێک","ساڵانە"], key="reminder_freq")
        reminder_note = st.text_input("📝 تێبینی:", placeholder="بۆ نموونە: پشکنینی شەکری مانگانە...", key="reminder_note")
        
        if st.button("💾 تۆمارکردن", key="save_reminder", use_container_width=True):
            st.session_state.reminders.append({"test":reminder_test,"frequency":reminder_freq,"note":reminder_note,"created":datetime.now().strftime("%Y-%m-%d %H:%M")})
            st.success("✅ تۆمارکرا!")
            st.rerun()
    
    if st.session_state.reminders:
        st.markdown(f"<div class='badge'>📅 یادخستنەوەکانت ({len(st.session_state.reminders)})</div>", unsafe_allow_html=True)
        for reminder in st.session_state.reminders:
            st.markdown(f"""<div class="reminder-card"><b>🔬 {reminder['test']}</b><br>🔄 {reminder['frequency']} | 📝 {reminder['note']}<br><span style="color:#6b7280;font-size:0.7rem;">📅 {reminder['created']}</span></div>""", unsafe_allow_html=True)
    
    st.markdown("<div class='badge'>💡 گشتی</div>", unsafe_allow_html=True)
    st.markdown("""<div class="glass-card"><p>🍬 شەکرە: FBS مانگانە | HbA1c هەر ٣ مانگ</p><p>❤️ دڵ: Lipid ساڵانە</p><p>🦋 دەرەقی: TSH هەر ٦-١٢ مانگ</p></div>""", unsafe_allow_html=True)

# ============================================
# HISTORY SECTION
# ============================================
with st.expander("📊 مێژووی ئەنجامەکانت", expanded=False):
    if len(st.session_state.history) > 0:
        df = pd.DataFrame(st.session_state.history)
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 CSV", csv, "results.csv", "text/csv")
    else:
        st.info("هێشتا هیچ ئەنجامێکت تۆمار نەکردووە")

# ============================================
# FOOTER
# ============================================
st.markdown(f"""<div class="glass-card" style="text-align:center;margin-top:15px;"><p style="color:#ef4444;font-weight:600;font-size:0.75rem;">⚠️ بۆ ڕێنمایی سەرەتاییە - جێگەی سەردانی پزیشک ناگرێتەوە</p><p style="color:#6b7280;font-size:0.7rem;">© 2024 <b>Danyal Ismail</b> | {len(ALL_TESTS)} پشکنین | ٧ بەش</p></div>""", unsafe_allow_html=True)
