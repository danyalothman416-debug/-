import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
from fpdf import FPDF
import base64
from io import BytesIO
import random

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="ڕێبەری پشکنینە تاقیگەییەکان - سیستەمی زیرەک", 
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

# --- CSS STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Naskh+Arabic:wght@400;700&display=swap');
    
    * { font-family: 'Noto Naskh Arabic', 'Segoe UI', sans-serif; }
    
    [data-testid="stSidebar"] { display: none; }
    
    html, body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #F5F7FA 0%, #E8EDF2 100%) !important;
    }
    
    .header-card {
        background: linear-gradient(135deg, #1a237e 0%, #283593 50%, #3949ab 100%);
        border-radius: 25px;
        padding: 35px;
        color: white !important;
        margin-bottom: 30px;
        text-align: center;
        box-shadow: 0 15px 40px rgba(26,35,126,0.3);
    }
    
    .header-card * { color: white !important; }
    
    .test-card {
        background: white;
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.08);
        border-right: 6px solid #3949ab;
        transition: all 0.3s ease;
    }
    
    .test-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    }
    
    .ai-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 25px;
        color: white !important;
        margin: 20px 0;
        box-shadow: 0 10px 30px rgba(102,126,234,0.3);
    }
    
    .ai-card * { color: white !important; }
    
    .recommendation-card {
        background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
        border-radius: 20px;
        padding: 20px;
        margin: 15px 0;
        border-right: 5px solid #4caf50;
    }
    
    .recommendation-card-food {
        background: linear-gradient(135deg, #fff3e0, #ffe0b2);
        border-radius: 20px;
        padding: 20px;
        margin: 15px 0;
        border-right: 5px solid #ff9800;
    }
    
    .chat-message {
        padding: 15px;
        border-radius: 15px;
        margin: 10px 0;
    }
    
    .chat-user {
        background: #e3f2fd;
        text-align: left;
    }
    
    .chat-bot {
        background: #f3e5f5;
        text-align: right;
    }
    
    .stButton button {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
        border-radius: 15px !important;
        padding: 12px 30px !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(102,126,234,0.5) !important;
    }
    
    .export-btn button {
        background: linear-gradient(135deg, #4caf50, #66bb6a) !important;
    }
    
    .filter-box {
        background: white;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.08);
        margin-bottom: 25px;
    }
    
    .warning-box {
        background: #ffebee;
        border-right: 5px solid #f44336;
        border-radius: 15px;
        padding: 20px;
        margin: 25px 0;
        text-align: center;
    }
    
    .result-normal {
        background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
        border-right: 5px solid #4caf50;
        border-radius: 12px;
        padding: 18px;
        margin: 10px 0;
    }
    
    .result-abnormal {
        background: linear-gradient(135deg, #fff3e0, #ffe0b2);
        border-right: 5px solid #ff9800;
        border-radius: 12px;
        padding: 18px;
        margin: 10px 0;
    }
    
    .result-critical {
        background: linear-gradient(135deg, #ffebee, #ffcdd2);
        border-right: 5px solid #f44336;
        border-radius: 12px;
        padding: 18px;
        margin: 10px 0;
    }
    
    .category-title {
        font-size: 1.3rem;
        font-weight: bold;
        color: #1a237e;
        margin: 25px 0 15px 0;
        padding: 10px 20px;
        background: linear-gradient(135deg, #e8eaf6, #c5cae9);
        border-radius: 15px;
        display: inline-block;
    }
    
    [dir="rtl"] { text-align: right !important; direction: rtl !important; }
</style>
""", unsafe_allow_html=True)

# --- هەموو پشکنینەکان ---
ALL_TESTS = {
    "پشکنینی تەواوی خوێن (CBC)": {
        "Name": "پشکنینی تەواوی خوێن (CBC - Complete Blood Count)",
        "Description": "یەکێکە لە باوترین پشکنینەکان کە پێوانەی پێکهاتەکانی خوێن دەکات، وەک خڕۆکە سوورەکان، خڕۆکە سپییەکان و پەڕەکانی خوێن. یارمەتیدەرە بۆ دەستنیشانکردنی کەمخوێنی (ئەنیمیا)، هەوکردن، و کێشەکانی مەینبوونی خوێن.",
        "Ranges": "هیمۆگڵۆبین (پیاوان): 13.5-17.5 g/dL | هیمۆگڵۆبین (ژنان): 12.0-15.5 g/dL | خڕۆکە سپییەکان (WBC): 4,500-11,000 /µL | پەڕەکانی خوێن (Platelets): 150,000-450,000 /µL",
        "Category": "پشکنینە بنەڕەتییەکان",
        "Organ": "خوێن",
        "FoodRecommendations": "بۆ بەرزکردنەوەی هیمۆگڵۆبین: گۆشتی سوور، سپێناغ، ڕەمەزانە، دەنکەڵان، جگەر. ڤیتامین C (پرتەقاڵ، لیمۆ) یارمەتی هەڵمژینی ئاسن دەدات. دوورکەوتنەوە لە چا و قاوە دوای نان خواردن."
    },
    "شەکری ناو خوێن (FBS)": {
        "Name": "شەکری ناو خوێن لە کاتی برسێتیدا (FBS - Fasting Blood Sugar)",
        "Description": "ئەم پشکنینە بڕی گلوکۆز (شەکر) لە خوێندا دەپێوێت. دەبێت کەسەکە ٨ بۆ ١٢ کاتژمێر پێش پشکنینەکە هیچ شتێکی نەخواردبێت. ١٠٠-١٢٥ = پێش شەکرە | ١٢٦+ = شەکرە.",
        "Ranges": "ڕێژەی ئاسایی: 70-99 mg/dL",
        "Category": "پشکنینە بنەڕەتییەکان",
        "Organ": "پەنکریاس / خوێن",
        "FoodRecommendations": "بۆ کۆنترۆڵکردنی شەکری خوێن: سەوزەواتی ڕیشاڵدار (برۆکلی، سپێناغ)، دەنکەڵان، ماسی چەور (سەلەمۆن)، هەویری تەواو (نان و برنجی قاوەیی). دوورکەوتنەوە لە شەکر، نان و برنجی سپی، خواردنەوە گازییەکان. وەرزشی ڕۆژانە ٣٠ خولەک."
    },
    "شەکری کەڵەکەبوو (HbA1c)": {
        "Name": "شەکری کەڵەکەبوو (HbA1c)",
        "Description": "ئەم پشکنینە تێکڕای ڕێژەی شەکری خوێنت نیشان دەدات لە ماوەی ٢ بۆ ٣ مانگی ڕابردوو. 5.7%-6.4% = پێش شەکرە | 6.5%+ = شەکرە.",
        "Ranges": "ڕێژەی ئاسایی: کەمتر لە 5.7%",
        "Category": "پشکنینە بنەڕەتییەکان",
        "Organ": "پەنکریاس / خوێن",
        "FoodRecommendations": "بۆ کەمکردنەوەی HbA1c: ڕێجیمی دژە هەوکردن (سەوزەوات، ماسی، زەیتی زەیتوون)، کەمکردنەوەی کاربۆهیدرات، وەرزشی بەردەوام. هەنگاو بە هەنگاو کەمکردنەوەی کێش ئەگەر زیادەت هەیە."
    },
    "چەورییەکانی خوێن (Lipid Profile)": {
        "Name": "چەورییەکانی خوێن (Lipid Profile)",
        "Description": "کۆمەڵە پشکنینێکە بۆ پێوانەکردنی جۆرە جیاوازەکانی چەوری لە خوێندا. گرنگە بۆ هەڵسەنگاندنی مەترسییەکانی نەخۆشییەکانی دڵ و جەڵتە.",
        "Ranges": "کۆلیسترۆڵی گشتی: کەمتر لە 200 mg/dL | چەوری سیانی (Triglycerides): کەمتر لە 150 mg/dL | HDL (چەوری سوودبەخش): زیاتر لە 40 mg/dL | LDL (چەوری زیانبەخش): کەمتر لە 100 mg/dL",
        "Category": "پشکنینە بنەڕەتییەکان",
        "Organ": "دڵ / خوێن",
        "FoodRecommendations": "بۆ کەمکردنەوەی چەوری خوێن: ماسی چەور (هەفتەی ٢ جار)، ئەڤۆکادۆ، گوێز و بادەم، زەیتی زەیتوون، پاقلەمەنییەکان. دوورکەوتنەوە لە کەرە، خواردنی سوورەکراو، گۆشتی چەور، فاست فوود. ڕۆژانە ٣٠-٤٥ خولەک ڕۆیشتن."
    },
    "فەرمانی گورچیلە (KFT)": {
        "Name": "پشکنینی فەرمانی گورچیلە (KFT)",
        "Description": "پێوانەی توانای گورچیلەکان دەکات بۆ فلتەرکردن و پاککردنەوەی خوێن لە پاشماوەکان. سەرەکیترین پشکنینەکان: کریاتینین و یوریا.",
        "Ranges": "کریاتینین (پیاوان): 0.7-1.3 mg/dL | کریاتینین (ژنان): 0.6-1.1 mg/dL | یوریا (Blood Urea): 15-40 mg/dL",
        "Category": "پشکنینە بنەڕەتییەکان",
        "Organ": "گورچیلە",
        "FoodRecommendations": "بۆ تەندروستی گورچیلە: ئاوی زۆر (ڕۆژانە ٨-١٠ پەرداخ)، سەوزەواتی تازە، میوەی کەم پۆتاسیۆم (سێو، هەنگوین). کەمکردنەوەی خوێ، پرۆتینی زیاد لە پێویست، و خواردنەوە گازییەکان."
    },
    "فەرمانی جگەر (LFT)": {
        "Name": "پشکنینی فەرمانی جگەر (LFT)",
        "Description": "ئەم پشکنینانە بڕی ئەو ئەنزیم و پرۆتینانە دەپێون کە جگەر دەریاندەدات. بەرزبوونەوەیان نیشانەی هەوکردن یان تێکچوونی جگەرە.",
        "Ranges": "ALT (SGPT): 7-56 U/L | AST (SGOT): 10-40 U/L",
        "Category": "پشکنینە بنەڕەتییەکان",
        "Organ": "جگەر",
        "FoodRecommendations": "بۆ پاککردنەوەی جگەر: چای سەوز، سیر، زەردەچێوە، لیمۆ، چەوەندەری سوور، گەنمەشامی. دوورکەوتنەوە لە کحول، خواردنی چەور و سوورەکراو، دەرمانی بێ ڕێنمایی پزیشک."
    },
    "کۆگای ئاسن (Ferritin)": {
        "Name": "کۆگای ئاسن (Ferritin)",
        "Description": "پێوانەی ئاسنی خەزنکراوی لەش کە بۆ دروستبوونی خڕۆکە سوورەکان و گواستنەوەی ئۆکسجین پێویستە. کەمی دەبێتە هۆی کەمخوێنی و بێهێزی.",
        "Ranges": "پیاوان: 24-336 ng/mL | ژنان: 11-307 ng/mL",
        "Category": "پشکنینە تایبەتەکان",
        "Organ": "خوێن",
        "FoodRecommendations": "بۆ بەرزکردنەوەی ئاسن: گۆشتی سوور، جگەر، سپێناغ، ڕەمەزانی کوڵاو، نۆک، پاقلە. خواردنی ڤیتامین C (لیمۆ، پرتەقاڵ) لەگەڵ خواردنی ئاسندار بۆ هەڵمژینی باشتر. دوورکەوتنەوە لە چا و شیر لەگەڵ ژەمە ئاسندارەکان."
    },
    "ڤیتامین دی (Vitamin D3)": {
        "Name": "ڤیتامین دی (Vitamin D3)",
        "Description": "گرنگە بۆ تەندروستی ئێسک، هەڵمژینی کالیسیۆم، و بەهێزکردنی کۆئەندامی بەرگری. کەمتر لە ٢٠ ng/mL = کەمی ڤیتامین دی.",
        "Ranges": "ڕێژەی ئاسایی: 30-100 ng/mL",
        "Category": "پشکنینی ڤیتامین و کانزاکان",
        "Organ": "ئێسک / خوێن",
        "FoodRecommendations": "بۆ بەرزکردنەوەی ڤیتامین دی: ڕووناکی ڕاستەوخۆی خۆر (ڕۆژانە ١٥-٢٠ خولەک)، ماسی چەور (سەلەمۆن، تونا)، هێلکە، شیر و پەنیری ڤیتامین دی زیادکراو. ڕەنگە پێویست بە دەرمانی ڤیتامین D3 بکات بە ڕێنمایی پزیشک."
    },
    "هۆرمۆنی دەرەقی (TSH)": {
        "Name": "هۆرمۆنی ڕژێنی دەرەقی (TSH)",
        "Description": "پشکنینی کارکردنی غودەی دەرەقی. بەرزبوونەوە = تەمەڵی غودە، نزمبوونەوە = زۆر چالاکی غودە.",
        "Ranges": "ڕێژەی ئاسایی TSH: 0.4-4.0 mIU/L",
        "Category": "پشکنینە بنەڕەتییەکان",
        "Organ": "دەرەقی (تیرۆید)",
        "FoodRecommendations": "بۆ تەندروستی دەرەقی: خواردنی یۆددار (خوێی یۆددار، ماسی دەریا)، گوێزی بەرازیلی (١-٢ دەنک ڕۆژانە)، سەوزەواتی ڕیشاڵدار. خۆپارێزی لە خواردنی زۆری سویا و کەلەرمی خاو ئەگەر کێشەی دەرەقیت هەیە."
    }
}

# --- AI INTERPRETATION ENGINE (شیکەرەوەی زیرەک) ---
def ai_interpret_result(test_name, user_value, unit, gender="general"):
    """
    شیکەرەوەی زیرەکی ئەنجامەکان بەبێ API دەرەکی
    """
    
    # بنکەدراوەی ئەنجامەکان
    knowledge_base = {
        "هیمۆگڵۆبین": {
            "unit": "g/dL",
            "male": (13.5, 17.5),
            "female": (12.0, 15.5),
            "low_interpretation": "ئەم ئەنجامە نزمە و ڕەنگە نیشانەی کەمخوێنی (ئەنیمیا) بێت. کەمخوێنی دەبێتە هۆی بێهێزی، ماندوێتی، سەرگێژخواردن، و ڕەنگی پێستی کاڵ. پێویستە پشکنینی کۆگای ئاسن (Ferritin) و ڤیتامین B12 ئەنجام بدەیت بۆ زانینی هۆکاری سەرەکی.",
            "high_interpretation": "ئەم ئەنجامە بەرزە. ڕەنگە نیشانەی وشکبوونەوە، نەخۆشی دڵ، یان کێشەی سییەکان بێت. پێویستە سەردانی پزیشکی خوێن بکەیت بۆ پشکنینی زیاتر.",
            "normal_interpretation": "ئەم ئەنجامە لە ئاستی ئاساییدایە. ئاستی هیمۆگڵۆبینت باشە و گواستنەوەی ئۆکسجین لە لەشتدا بە باشی کاردەکات."
        },
        "FBS": {
            "unit": "mg/dL",
            "all": (70, 99),
            "low_interpretation": "ئەم ئەنجامە نزمە و نیشانەی دابەزینی شەکری خوێنە (Hypoglycemia). دەبێتە هۆی سەرگێژخواردن، ڕشانەوە، لەرزین، و لەدەستدانی هۆش لە حاڵەتی تونددا. پێویستە یەکسەر شەکر یان خواردنێکی شیرین بخۆیت و سەردانی پزیشک بکەیت.",
            "high_interpretation": "ئەم ئەنجامە بەرزە و نیشانەی نەخۆشی شەکرەیە (Diabetes). پێویستە پشکنینی HbA1c ئەنجام بدەیت بۆ پشتڕاستکردنەوە. کۆنترۆڵکردنی شەکرە بە ڕێجیم، وەرزش، و دەرمان دەکرێت.",
            "normal_interpretation": "ئەم ئەنجامە لە ئاستی ئاساییدایە. ئاستی شەکری خوێنت لە کاتی برسێتیدا باشە."
        },
        "کۆلیسترۆڵ": {
            "unit": "mg/dL",
            "all": (0, 200),
            "low_interpretation": "ئەم ئەنجامە زۆر نزمە. ڕەنگە نیشانەی کێشەی هەرس یان جگەر بێت. پێویستە پشکنینی زیاتر بۆ جگەر و پرۆتینەکانی خوێن ئەنجام بدەیت.",
            "high_interpretation": "ئەم ئەنجامە بەرزە و مەترسی نەخۆشی دڵ و جەڵتە زیاد دەکات. پێویستە ڕێجیمی کەم چەوری و وەرزش ڕێک بخەیت. سەردانی پزیشکی دڵ بکە.",
            "normal_interpretation": "ئەم ئەنجامە لە ئاستی ئاساییدایە. ئاستی کۆلیسترۆڵت باشە و مەترسی نەخۆشی دڵ کەمە."
        },
        "کریاتینین": {
            "unit": "mg/dL",
            "male": (0.7, 1.3),
            "female": (0.6, 1.1),
            "low_interpretation": "ئەم ئەنجامە نزمە. ڕەنگە نیشانەی کەمی ماسولکە یان کێشەی جگەر بێت. بەگشتی ئەگەر نیشانەی تر نەبێت جێی نیگەرانی نییە.",
            "high_interpretation": "ئەم ئەنجامە بەرزە و نیشانەی کێشەی گورچیلەیە! گورچیلەکانت ڕەنگە بە باشی خوێن پاک نەکەنەوە. پێویستە یەکسەر سەردانی پزیشکی گورچیلە بکەیت و پشکنینی KFT تەواو ئەنجام بدەیت.",
            "normal_interpretation": "ئەم ئەنجامە لە ئاستی ئاساییدایە. گورچیلەکانت بە باشی کاردەکەن."
        },
        "ALT": {
            "unit": "U/L",
            "all": (7, 56),
            "low_interpretation": "ئەم ئەنجامە لە ئاستی ئاسایی کەمترە. بەگشتی جێی نیگەرانی نییە و نیشانەی باشی کارکردنی جگەرە.",
            "high_interpretation": "ئەم ئەنجامە بەرزە و نیشانەی هەوکردن یان زیانگەیشتن بە جگەرە! ڕەنگە هۆکاری ڤایرۆسی، کحول، یان دەرمان بێت. پێویستە پشکنینی تەواوی جگەر (LFT) ئەنجام بدەیت و سەردانی پزیشکی جگەر بکەیت.",
            "normal_interpretation": "ئەم ئەنجامە لە ئاستی ئاساییدایە. ئەنزیمەکانی جگەرت لە سنووری ئاساییدان."
        },
        "TSH": {
            "unit": "mIU/L",
            "all": (0.4, 4.0),
            "low_interpretation": "ئەم ئەنجامە نزمە و نیشانەی زیادەڕەوی غودەی دەرەقییە (Hyperthyroidism). نیشانەکانی: لەدەستدانی کێش، ڕاژان، خێرایی لێدانی دڵ، دڵەڕاوکێ. پێویستە سەردانی پزیشکی غودە بکەیت.",
            "high_interpretation": "ئەم ئەنجامە بەرزە و نیشانەی تەمەڵی غودەی دەرەقییە (Hypothyroidism). نیشانەکانی: زیادبوونی کێش، ماندوێتی، ساردی، ڕەشبینی. پێویستە سەردانی پزیشکی غودە بکەیت.",
            "normal_interpretation": "ئەم ئەنجامە لە ئاستی ئاساییدایە. غودەی دەرەقیت بە باشی کاردەکات."
        },
        "ڤیتامین دی": {
            "unit": "ng/mL",
            "all": (30, 100),
            "low_interpretation": "ئەم ئەنجامە نزمە و نیشانەی کەمی ڤیتامین دییە. دەبێتە هۆی ئازاری ئێسک، بێهێزی ماسولکە، و لاوازی بەرگری لەش. پێویستە دەرمانی ڤیتامین D3 وەربگریت و زیاتر بەر خۆر بکەویت.",
            "high_interpretation": "ئەم ئەنجامە بەرزە. ڕەنگە نیشانەی زیادەڕەوی لە وەرگرتنی دەرمانی ڤیتامین دی بێت. پێویستە ڕێژەی وەرگرتن کەم بکەیتەوە و سەردانی پزیشک بکەیت.",
            "normal_interpretation": "ئەم ئەنجامە لە ئاستی ئاساییدایە. ئاستی ڤیتامین دیت باشە و ئێسک و بەرگری لەشت بەهێزە."
        },
        "فێریتین": {
            "unit": "ng/mL",
            "male": (24, 336),
            "female": (11, 307),
            "low_interpretation": "ئەم ئەنجامە نزمە و نیشانەی کەمی کۆگای ئاسنە. دەبێتە هۆی کەمخوێنی، بێهێزی، ڕووتانەوەی قژ، و نینۆکی لاواز. پێویستە خواردنی ئاسندار بخۆیت و سەردانی پزیشک بکەیت.",
            "high_interpretation": "ئەم ئەنجامە بەرزە. ڕەنگە نیشانەی هەوکردن، نەخۆشی جگەر، یان زیادەڕەوی ئاسن بێت. پێویستە پشکنینی زیاتر ئەنجام بدەیت.",
            "normal_interpretation": "ئەم ئەنجامە لە ئاستی ئاساییدایە. کۆگای ئاسنت باشە و مەترسی کەمخوێنیت نییە."
        }
    }
    
    # دۆزینەوەی پشکنین لە بنکەدراوە
    for key, data in knowledge_base.items():
        if key.lower() in test_name.lower():
            # دیاریکردنی مەودا بەپێی ڕەگەز
            if "male" in data and "female" in data and gender != "general":
                min_val, max_val = data.get(gender, data.get("all", (0, 0)))
            elif "all" in data:
                min_val, max_val = data["all"]
            elif "male" in data:
                min_val, max_val = data["male"]
            else:
                min_val, max_val = (0, 0)
            
            if user_value < min_val:
                return f"""
                🔍 **شیکاری زیرەک بۆ: {test_name}**
                
                📊 ئەنجامی تۆ: **{user_value} {unit}**
                📏 مەودای ئاسایی: **{min_val} - {max_val} {unit}**
                
                ⚠️ **دۆخ:** ئەنجامەکەت **لە ئاستی ئاسایی نزمترە**
                
                📋 **شیکاری:**
                {data['low_interpretation']}
                
                💊 **ڕێنمایی گشتی:**
                - سەردانی پزیشکی پسپۆڕ بکە بۆ پشکنینی زیاتر
                - ڕێجیم و خۆراکی گونجاو ڕێک بخە
                - ئەگەر نیشانەکانی ترت هەیە تۆماریان بکە بۆ پزیشک
                """
            elif user_value > max_val:
                return f"""
                🔍 **شیکاری زیرەک بۆ: {test_name}**
                
                📊 ئەنجامی تۆ: **{user_value} {unit}**
                📏 مەودای ئاسایی: **{min_val} - {max_val} {unit}**
                
                ⚠️ **دۆخ:** ئەنجامەکەت **لە ئاستی ئاسایی بەرزترە**
                
                📋 **شیکاری:**
                {data['high_interpretation']}
                
                💊 **ڕێنمایی گشتی:**
                - سەردانی پزیشکی پسپۆڕ بکە بۆ پشکنینی زیاتر
                - ڕێجیم و خۆراکی گونجاو ڕێک بخە
                - ئەگەر نیشانەکانی ترت هەیە تۆماریان بکە بۆ پزیشک
                """
            else:
                return f"""
                🔍 **شیکاری زیرەک بۆ: {test_name}**
                
                📊 ئەنجامی تۆ: **{user_value} {unit}**
                📏 مەودای ئاسایی: **{min_val} - {max_val} {unit}**
                
                ✅ **دۆخ:** ئەنجامەکەت **لە ئاستی ئاساییدایە**
                
                📋 **شیکاری:**
                {data['normal_interpretation']}
                
                💊 **ڕێنمایی:**
                - بەردەوام بە لەسەر ڕێجیم و شێوازی ژیانی تەندروست
                - پشکنینی ساڵانە ئەنجام بدە بۆ دڵنیابوونەوە
                """
    
    # ئەگەر پشکنین نەدۆزرایەوە
    return f"""
    🔍 **شیکاری زیرەک بۆ: {test_name}**
    
    📊 ئەنجامی تۆ: **{user_value} {unit}**
    
    ❓ ببورە، ناتوانم شیکاری ورد بۆ ئەم پشکنینە بکەم.
    تکایە سەردانی پزیشکی پسپۆڕ بکە بۆ خوێندنەوەی ئەنجامەکەت.
    """

# --- PDF EXPORT FUNCTION ---
def create_pdf(tests_data):
    pdf = FPDF()
    pdf.add_page()
    
    # Add Arabic font (using DejaVu as fallback)
    pdf.add_font('Arabic', '', 'DejaVu.ttf', uni=True)
    pdf.set_font('Arabic', '', 14)
    
    # Title
    pdf.cell(0, 10, 'ڕێبەری پشکنینە تاقیگەییەکان', ln=True, align='C')
    pdf.ln(10)
    
    for test_name, test_data in tests_data.items():
        pdf.set_font('Arabic', '', 12)
        pdf.cell(0, 10, test_data['Name'], ln=True)
        pdf.set_font('Arabic', '', 10)
        pdf.multi_cell(0, 8, f"وەسف: {test_data['Description']}")
        pdf.multi_cell(0, 8, f"ڕێژە ئاساییەکان: {test_data['Ranges']}")
        pdf.ln(5)
    
    return pdf.output(dest='S').encode('latin-1')

def get_pdf_download_link(pdf_bytes, filename):
    b64 = base64.b64encode(pdf_bytes).decode()
    return f'<a href="data:application/pdf;base64,{b64}" download="{filename}" style="text-decoration:none;"><button style="background:linear-gradient(135deg,#4caf50,#66bb6a);color:white;border:none;padding:12px 30px;border-radius:15px;font-size:16px;cursor:pointer;font-weight:bold;">📥 دابەزاندنی PDF</button></a>'

# --- FAQ DATABASE ---
FAQ_DATABASE = {
    "کەی پێویستە پشکنینی شەکرە بکەم؟": "پێویستە هەموو کەسێک لە تەمەنی ٤٥ ساڵی بەرەو سەر، ساڵانە پشکنینی شەکرە ئەنجام بدات. ئەگەر کێشی زیادەت هەیە، مێژووی خێزانی شەکرەت هەیە، یان پەستانی خوێنت بەرزە، پێویستە زووتر (لە ٣٠ ساڵییەوە) دەست بکەیت بە پشکنین.",
    "ئایا شیر خواردن کاریگەری لەسەر ئەنجامی پشکنین هەیە؟": "بەڵێ، شیر خواردن دەتوانێت کاریگەری لەسەر هەندێک پشکنین هەبێت. بۆ پشکنینی شەکری ناو خوێن (FBS) پێویستە ٨-١٢ کاتژمێر هیچ شتێک نەخۆیت (تەنها ئاو). بۆ پشکنینی چەوری خوێن (Lipid) پێویستە ١٢ کاتژمێر برسی بیت. بەڵام بۆ زۆربەی پشکنینەکانی تر (وەک CBC، TSH) پێویست بە برسی بوون نییە.",
    "جیاوازی نێوان FBS و HbA1c چییە؟": "FBS شەکری خوێنت لەو ساتەدا دەپێوێت و پێویستی بە ٨-١٢ کاتژمێر برسی بوون هەیە. بەڵام HbA1c تێکڕای شەکری خوێنت لە ٢-٣ مانگی ڕابردوودا نیشان دەدات و پێویستی بە برسی بوون نییە. HbA1c وردترە بۆ کۆنترۆڵکردنی درێژخایەنی شەکرە.",
    "چەند جارێک پێویستە پشکنینی چەوری خوێن بکەم؟": "بۆ کەسانی تەندروست: هەر ٥ ساڵ جارێک. بۆ کەسانی مەترسیدار (پەستانی خوێنی بەرز، شەکرە، جگەرەکێشان): ساڵانە یان بەپێی ڕێنمایی پزیشک. ئەگەر چارەسەری کەمکردنەوەی چەوری وەردەگریت: هەر ٣-٦ مانگ جارێک.",
    "ئایا پشکنینی خوێن ئازاری هەیە؟": "پشکنینی خوێن تەنها چەند چرکەیەک ئازاری کەمی دەبێت لە کاتی کونکردنی پێست. زۆربەی کەسان بە ئاسانی بەرگەی دەگرن. ئەگەر ترسی لە دەرزیت هەیە، دەتوانیت لە پێشوەختە بە پەرستار یان تەکنیکاری تاقیگە بڵێیت."
}

# --- CHATBOT FUNCTION ---
def chatbot_response(question):
    for key, answer in FAQ_DATABASE.items():
        if key in question or question in key:
            return answer
    
    # وەڵامی گشتی
    if "شەکر" in question or "گلوکۆز" in question:
        return "بۆ هەر پرسیارێک سەبارەت بە شەکرە، پێشنیار دەکەم پشکنینی FBS (بە برسی بوون) و HbA1c (بۆ تێکڕای ٣ مانگ) ئەنجام بدەیت. ڕێژەی ئاسایی FBS: 70-99 mg/dL و HbA1c: کەمتر لە 5.7%."
    elif "دڵ" in question or "چەوری" in question or "کۆلیسترۆڵ" in question:
        return "بۆ تەندروستی دڵ، پشکنینی Lipid Profile گرنگە. ڕێژە ئاساییەکان: کۆلیسترۆڵی گشتی کەمتر لە 200، LDL کەمتر لە 100، HDL زیاتر لە 40، و Triglycerides کەمتر لە 150 mg/dL."
    elif "گورچیلە" in question or "کریاتینین" in question:
        return "بۆ پشکنینی گورچیلە، KFT ئەنجام بدە. گرنگترین نیشانەکان: کریاتینین (پیاوان: 0.7-1.3، ژنان: 0.6-1.1 mg/dL) و یوریا (15-40 mg/dL)."
    elif "جگەر" in question or "ALT" in question or "AST" in question:
        return "بۆ پشکنینی جگەر، LFT ئەنجام بدە. ئەنزیمە سەرەکییەکان: ALT (7-56 U/L) و AST (10-40 U/L). بەرزبوونەوەیان نیشانەی هەوکردنی جگەرە."
    else:
        return "ببورە، ناتوانم وەڵامی ئەم پرسیارە بدەم. تکایە بە شێوەیەکی تر پرسیارەکەت بکەوە یان سەردانی پزیشک بکە. دەتوانیت لەم بوارانە پرسیار بکەیت: شەکرە، دڵ، گورچیلە، جگەر، ڤیتامینەکان."

# --- HEADER ---
st.markdown("""
<div class="header-card">
    <h1 style="font-size:2.5rem; margin-bottom:15px;">🔬 ڕێبەری پشکنینە تاقیگەییەکان</h1>
    <p style="font-size:1.3rem; opacity:0.95;">سیستەمی زیرەکی شیکاری پشکنینەکان | ڕێنمایی خۆراکی | هاوڕێی تەندروستیت</p>
</div>
""", unsafe_allow_html=True)

# --- MAIN TABS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 پشکنینەکان", 
    "🧠 شیکاری زیرەک (AI)", 
    "📊 هێڵکاری گۆڕانکارییەکان", 
    "💬 پرسیار و وەڵام",
    "📥 هەناردەکردن"
])

# --- TAB 1: پشکنینەکان ---
with tab1:
    # فلتەری پێشکەوتوو
    with st.expander("🔍 فلتەری پێشکەوتوو", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            search_text = st.text_input("🔍 گەڕان بەناوی پشکنین:", placeholder="بۆ نموونە: شەکرە، هیمۆگڵۆبین...")
        with col2:
            organs = ["هەموو"] + list(set([test['Organ'] for test in ALL_TESTS.values()]))
            selected_organ = st.selectbox("🫀 فلتەر بەپێی ئەندامی لەش:", organs)
        with col3:
            categories = ["هەموو"] + list(set([test['Category'] for test in ALL_TESTS.values()]))
            selected_category = st.selectbox("📂 فلتەر بەپێی کاتێگۆری:", categories)
    
    # فلتەرکردن
    filtered_tests = {}
    for key, test in ALL_TESTS.items():
        if search_text and search_text.lower() not in test['Name'].lower() and search_text.lower() not in test['Description'].lower():
            continue
        if selected_organ != "هەموو" and test['Organ'] != selected_organ:
            continue
        if selected_category != "هەموو" and test['Category'] != selected_category:
            continue
        filtered_tests[key] = test
    
    # پیشاندانی پشکنینەکان
    if filtered_tests:
        st.success(f"🔍 {len(filtered_tests)} پشکنین دۆزرایەوە")
        
        for test_key, test in filtered_tests.items():
            with st.expander(f"🔬 {test['Name']} | 🫀 {test['Organ']}", expanded=False):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"""
                    <div style="background:#f8f9fa;padding:15px;border-radius:10px;margin-bottom:15px;">
                        📝 <b>وەسف:</b> {test['Description']}
                    </div>
                    <div style="background:#e8eaf6;padding:15px;border-radius:10px;">
                        📊 <b>ڕێژە ئاساییەکان:</b> {test['Ranges']}
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    # ئامۆژگاری خۆراکی
                    if 'FoodRecommendations' in test:
                        st.markdown(f"""
                        <div class="recommendation-card-food">
                            <h4>🥗 ئامۆژگاری خۆراکی:</h4>
                            <p style="font-size:0.95rem;">{test['FoodRecommendations']}</p>
                        </div>
                        """, unsafe_allow_html=True)
    else:
        st.warning("😔 هیچ پشکنینێک نەدۆزرایەوە. تکایە فلتەرەکانت بگۆڕە.")

# --- TAB 2: شیکاری زیرەک (AI) ---
with tab2:
    st.markdown("""
    <div class="ai-card">
        <h2>🧠 شیکاری زیرەکی ئەنجامەکان (AI-Powered)</h2>
        <p>ئەنجامی پشکنینەکەت بنووسە و شیکارییەکی زانستی ورد وەربگرە</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        test_choice = st.selectbox("پشکنین هەڵبژێرە:", list(ALL_TESTS.keys()))
    with col2:
        gender_choice = st.radio("ڕەگەز:", ["general", "male", "female"], format_func=lambda x: {"general": "گشتی", "male": "پیاوان", "female": "ژنان"}[x], horizontal=True)
    with col3:
        unit_choice = st.text_input("یەکە (Unit):", value="mg/dL", placeholder="بۆ نموونە: mg/dL, g/dL, U/L")
    
    user_result = st.number_input("ئەنجامی پشکنینەکەت بنووسە:", value=0.0, step=0.1, format="%.1f")
    
    if st.button("🔍 شیکاری زیرەک ئەنجام بدە", use_container_width=True):
        if user_result > 0:
            with st.spinner("🧠 سیستەمی زیرەک ئەنجامەکەت شیدەکاتەوە..."):
                import time
                time.sleep(1.5)  # سیمولەیشنی پرۆسێسکردن
                
                interpretation = ai_interpret_result(test_choice, user_result, unit_choice, gender_choice)
                
                st.markdown(f"""
                <div class="ai-card">
                    {interpretation.replace(chr(10), '<br>')}
                </div>
                """, unsafe_allow_html=True)
                
                # هەڵگرتنی لە هێڵکاری
                st.session_state.history.append({
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "test": test_choice,
                    "value": user_result,
                    "unit": unit_choice
                })
                
                # پیشاندانی ئامۆژگاری خۆراکی
                test_data = ALL_TESTS.get(test_choice, {})
                if 'FoodRecommendations' in test_data:
                    st.markdown(f"""
                    <div class="recommendation-card-food">
                        <h4>🥗 ئامۆژگاری خۆراکی پەیوەندیدار:</h4>
                        <p>{test_data['FoodRecommendations']}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("تکایە ئەنجامێکی دروست بنووسە (گەورەتر لە ٠)")

# --- TAB 3: هێڵکاری گۆڕانکارییەکان ---
with tab3:
    st.markdown("<h3>📊 هێڵکاری گۆڕانکارییەکانی ئەنجامەکانت</h3>", unsafe_allow_html=True)
    
    if len(st.session_state.history) > 0:
        df = pd.DataFrame(st.session_state.history)
        
        # هەڵبژاردنی پشکنین بۆ پیشاندان
        test_options = df['test'].unique()
        selected_tests = st.multiselect("پشکنینەکان هەڵبژێرە بۆ پیشاندان:", test_options, default=list(test_options)[:3])
        
        if selected_tests:
            filtered_df = df[df['test'].isin(selected_tests)]
            
            # Line Chart
            fig = px.line(filtered_df, x='date', y='value', color='test', 
                         title='گۆڕانکاری ئەنجامی پشکنینەکان بە تێپەڕبوونی کات',
                         markers=True,
                         labels={'date': 'ڕێکەوت', 'value': 'ئەنجام', 'test': 'پشکنین'})
            
            fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font_family='Noto Naskh Arabic',
                font_size=14,
                legend=dict(orientation='h', yanchor='bottom', y=1.02),
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # ئامار
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("ژمارەی پشکنینەکان", len(filtered_df))
            with col2:
                st.metric("نزمترین ئەنجام", f"{filtered_df['value'].min():.1f}")
            with col3:
                st.metric("بەرزترین ئەنجام", f"{filtered_df['value'].max():.1f}")
            
            # خشتەی داتاکان
            st.dataframe(filtered_df, use_container_width=True)
    else:
        st.info("📊 هێشتا هیچ ئەنجامێکی شیکاریکراوت نییە. بڕۆ بۆ بەشی 'شیکاری زیرەک' و ئەنجامی پشکنینەکانت تۆمار بکە.")
        
        # داتای نمونەیی
        if st.button("📊 داتای نمونەیی پیشان بدە"):
            sample_data = pd.DataFrame({
                'date': [(datetime.now() - timedelta(days=i*30)).strftime("%Y-%m-%d") for i in range(6)],
                'test': ['FBS']*6,
                'value': [95, 102, 110, 105, 98, 92],
                'unit': ['mg/dL']*6
            })
            fig = px.line(sample_data, x='date', y='value', title='نمونەی گۆڕانکاری شەکری خوێن', markers=True)
            fig.update_layout(plot_bgcolor='white', paper_bgcolor='white')
            st.plotly_chart(fig, use_container_width=True)

# --- TAB 4: پرسیار و وەڵام ---
with tab4:
    st.markdown("<h3>💬 پرسیار و وەڵام - یارمەتیدەری زیرەک</h3>", unsafe_allow_html=True)
    
    # پیشاندانی گفتوگۆ
    for msg in st.session_state.chat_messages:
        if msg['role'] == 'user':
            st.markdown(f"""
            <div class="chat-message chat-user">
                <b>👤 ئێوە:</b> {msg['content']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message chat-bot">
                <b>🤖 یارمەتیدەر:</b> {msg['content']}
            </div>
            """, unsafe_allow_html=True)
    
    # داخڵکردنی پرسیار
    user_question = st.text_input("پرسیارەکەت بنووسە:", placeholder="بۆ نموونە: کەی پێویستە پشکنینی شەکرە بکەم؟", key="chat_input")
    
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("📤 ناردن", use_container_width=True) and user_question:
            st.session_state.chat_messages.append({"role": "user", "content": user_question})
            response = chatbot_response(user_question)
            st.session_state.chat_messages.append({"role": "bot", "content": response})
            st.rerun()
    
    # پرسیارە باوەکان
    st.markdown("<br><h4>📌 پرسیارە باوەکان:</h4>", unsafe_allow_html=True)
    cols = st.columns(2)
    common_questions = list(FAQ_DATABASE.keys())
    for i, q in enumerate(common_questions):
        with cols[i % 2]:
            if st.button(f"❓ {q}", key=f"faq_{i}"):
                st.info(FAQ_DATABASE[q])

# --- TAB 5: هەناردەکردن ---
with tab5:
    st.markdown("<h3>📥 هەناردەکردنی زانیارییەکان</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h4>📄 هەناردەکردنی پشکنینەکان بە PDF</h4>", unsafe_allow_html=True)
        
        if st.button("📥 دابەزاندنی هەموو پشکنینەکان", use_container_width=True):
            pdf_bytes = create_pdf(ALL_TESTS)
            st.markdown(get_pdf_download_link(pdf_bytes, "all_tests.pdf"), unsafe_allow_html=True)
            st.success("✅ فایلی PDF ئامادەیە!")
    
    with col2:
        st.markdown("<h4>📊 هەناردەکردنی مێژووی ئەنجامەکان</h4>", unsafe_allow_html=True)
        
        if len(st.session_state.history) > 0:
            df = pd.DataFrame(st.session_state.history)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 دابەزاندنی مێژوو بە CSV",
                data=csv,
                file_name="my_results_history.csv",
                mime="text/csv"
            )
        else:
            st.info("هێشتا هیچ مێژوویەکت نییە. بڕۆ بۆ بەشی 'شیکاری زیرەک' و ئەنجامەکانت تۆمار بکە.")
    
    # هەناردەکردنی دیجیتاڵی
    st.markdown("<br><h4>💾 هەناردەکردنی هەموو زانیارییەکان بە JSON</h4>", unsafe_allow_html=True)
    all_data = {
        "tests": ALL_TESTS,
        "history": st.session_state.history,
        "export_date": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    json_str = json.dumps(all_data, ensure_ascii=False, indent=2)
    st.download_button(
        label="📥 دابەزاندنی هەموو زانیارییەکان بە JSON",
        data=json_str,
        file_name="all_medical_data.json",
        mime="application/json"
    )

# --- FOOTER ---
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(f"""
<div style="background:white;padding:25px;border-radius:15px;text-align:center;
            box-shadow:0 -5px 20px rgba(0,0,0,0.05);margin-top:30px;">
    <div class="warning-box" style="margin-bottom:15px;">
        <h3 style="color:#c62828;">⚠️ تێبینییەکی گرنگ</h3>
        <p style="color:#333;">
            ئەم سیستەمە تەنها بۆ ڕێنمایی سەرەتاییە و نابێت جێگەی سەردانی پزیشک بگرێتەوە.
        </p>
    </div>
    <p style="color:#666;">© ٢٠٢٤ ڕێبەری پشکنینە تاقیگەییەکان | وەشانی 4.0</p>
    <p style="color:#999; font-size:0.85rem;">{len(ALL_TESTS)} پشکنین | AI-Powered | هاوڕێی تەندروستیت</p>
</div>
""", unsafe_allow_html=True)
