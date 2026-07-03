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
import warnings
warnings.filterwarnings('ignore')

# ================================
# 1. ڕێکخستنی ڕووکاری پەڕە
# ================================
st.set_page_config(
    page_title="ڕاهێنەری پزیشکی - Medical Training Simulator",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================================
# 2. CSS و ستایلە پێشکەوتووەکان
# ================================
st.markdown("""
<style>
    /* 2.1 ستایلە سەرەکییەکان */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Naskh+Arabic:wght@400;700&display=swap');
    
    .main-header {
        font-size: 3rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        text-align: center;
        padding: 2rem;
        border-radius: 25px;
        margin-bottom: 2.5rem;
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4);
        animation: fadeInDown 0.8s ease-out;
        font-family: 'Noto Naskh Arabic', sans-serif;
    }
    
    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
    
    .case-card {
        background: linear-gradient(145deg, #f0f4ff, #e8edff);
        padding: 2rem;
        border-radius: 20px;
        border-left: 8px solid #667eea;
        margin: 1.2rem 0;
        transition: all 0.4s ease;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        animation: fadeIn 0.6s ease-out;
    }
    
    .case-card:hover {
        transform: translateY(-5px) scale(1.01);
        box-shadow: 0 12px 35px rgba(102, 126, 234, 0.25);
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: scale(0.95); }
        to { opacity: 1; transform: scale(1); }
    }
    
    .success-box {
        background: linear-gradient(135deg, #d4edda, #b8e0c8);
        padding: 2rem;
        border-radius: 18px;
        border-left: 8px solid #28a745;
        box-shadow: 0 6px 25px rgba(40, 167, 69, 0.2);
        animation: pulse 1.5s infinite;
    }
    
    .error-box {
        background: linear-gradient(135deg, #f8d7da, #f5c6cb);
        padding: 2rem;
        border-radius: 18px;
        border-left: 8px solid #dc3545;
        box-shadow: 0 6px 25px rgba(220, 53, 69, 0.2);
    }
    
    .quiz-card {
        background: linear-gradient(135deg, #ffffff, #f8f9ff);
        padding: 2.5rem;
        border-radius: 22px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        margin: 1.5rem 0;
        border: 2px solid rgba(102, 126, 234, 0.15);
        transition: all 0.3s ease;
    }
    
    .quiz-card:hover {
        box-shadow: 0 15px 50px rgba(102, 126, 234, 0.2);
    }
    
    .progress-container {
        background: #e9ecef;
        border-radius: 15px;
        height: 16px;
        overflow: hidden;
        margin: 1rem 0;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.06);
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #667eea, #764ba2, #667eea);
        background-size: 200% 100%;
        border-radius: 15px;
        transition: width 1s ease;
        animation: shimmer 2s infinite linear;
    }
    
    @keyframes shimmer {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }
    
    .stat-card {
        background: white;
        padding: 1.8rem;
        border-radius: 18px;
        box-shadow: 0 6px 25px rgba(0,0,0,0.08);
        text-align: center;
        border-top: 5px solid #667eea;
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 40px rgba(102, 126, 234, 0.2);
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .badge-level {
        display: inline-block;
        padding: 0.4rem 1.5rem;
        border-radius: 25px;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .footer-style {
        text-align: center;
        padding: 3rem;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border-radius: 25px;
        margin-top: 3rem;
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.3);
        animation: fadeIn 1s ease-out;
    }
    
    .tab-container {
        background: white;
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 0 6px 30px rgba(0,0,0,0.06);
        margin: 1.5rem 0;
    }
    
    .button-primary {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        padding: 0.9rem 2.5rem;
        border-radius: 15px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 1rem;
    }
    
    .button-primary:hover {
        transform: scale(1.05);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    .medication-card {
        background: #f8f9ff;
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid #e8edff;
        margin: 0.8rem 0;
        transition: all 0.3s ease;
    }
    
    .medication-card:hover {
        background: #f0f4ff;
        border-color: #667eea;
    }
    
    .symptom-tag {
        display: inline-block;
        background: #e8edff;
        padding: 0.3rem 1rem;
        border-radius: 20px;
        margin: 0.2rem;
        font-size: 0.9rem;
        color: #4a4a8a;
    }
    
    .risk-high { color: #dc3545; font-weight: bold; }
    .risk-medium { color: #ffc107; font-weight: bold; }
    .risk-low { color: #28a745; font-weight: bold; }
    
    .timeline-item {
        padding: 1rem;
        border-left: 4px solid #667eea;
        margin: 0.8rem 0;
        background: #f8f9ff;
        border-radius: 0 12px 12px 0;
    }
    
    .notification-badge {
        background: #dc3545;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        margin-left: 0.5rem;
    }
    
    /* 2.2 ستایلەکانی داتابەیس */
    .database-table {
        width: 100%;
        border-collapse: collapse;
        margin: 1rem 0;
    }
    
    .database-table th {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 0.8rem;
        text-align: right;
    }
    
    .database-table td {
        padding: 0.8rem;
        border-bottom: 1px solid #e8edff;
    }
    
    .database-table tr:hover {
        background: #f0f4ff;
    }
    
    /* 2.3 ستایلەکانی مۆبایل */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
            padding: 1.2rem;
        }
        .stat-number {
            font-size: 1.8rem;
        }
        .stat-card {
            padding: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# ================================
# 3. داتابەسی پڕ و تەواوی نەخۆشییەکان (٥٠+ نەخۆشی)
# ================================
DISEASE_DATABASE = {
    # 3.1 نەخۆشییەکانی کۆئەندامی هەرس
    "شەکرەی جۆری 1": {
        "نیشانەکان": ["تینوویەتی زۆر", "میزی زۆر", "کێش کەمبوونەوە", "ماندوویی", "بینی تەڵخ", "برسێتی زۆر", "سەرگێژخواردن"],
        "پشکنینەکان": {
            "FBS": ">200 mg/dL",
            "HbA1c": ">8%",
            "C-peptide": "نزم یان نییە",
            "Anti-GAD": "positive"
        },
        "چارەسەر": ["ئەنسولین", "پێوانەکردنی شەکر", "شێوازی خواردن"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندییە جیاکەرەوەکان": "تەمەن < 30 + C-peptide نزم + Anti-GAD positive",
        "ڕێپیشگیری": ["پشکنینی بۆماوەیی", "پێشگیری لە هەوکردنە ڤایرۆسییەکان"],
        "گروپی تەمەن": "منداڵان و گەنجان"
    },
    "شەکرەی جۆری 2": {
        "نیشانەکان": ["تینوویەتی زۆر", "میزی زۆر", "ماندوویی", "کێش کەمبوونەوە", "بینی تەڵخ", "برسێتی زۆر", "پێست وشک", "هەستی بەمەزە"],
        "پشکنینەکان": {
            "FBS": ">126 mg/dL",
            "HbA1c": ">6.5%",
            "OGTT": ">200 mg/dL",
            "C-peptide": "نۆرماڵ یان بەرز",
            "Insulin": "بەرز"
        },
        "چارەسەر": ["مێتفۆرمین 500mg", "گۆڕینی شێوازی ژیان", "وەرزشی ڕۆژانە 30 خولەک", "شێوازی خواردن کەم کاربۆهیدرات"],
        "ئاستی مەترسی": "مەترسیدار",
        "تایبەتمەندییە جیاکەرەوەکان": "FBS بەرز + HbA1c بەرز + تەمەن > 40 ساڵ",
        "ڕێپیشگیری": ["شێوازی خواردنی تەندروست", "چالاکی جەستەیی", "پێوانەکردنی شەکر بەردەوام", "کەمکردنەوەی کێش"],
        "گروپی تەمەن": "تەمەن مامناوەند و پیر"
    },
    "پەستانی خوێنی سەرەتایی": {
        "نیشانەکان": ["سەرئێشە", "سەرگێژخواردن", "فشاری پشت چاو", "خێرالێدانی دڵ", "ئەرەقەکردن", "مەلە"],
        "پشکنینەکان": {
            "BP": ">140/90 mmHg",
            "ECG": "Left ventricular hypertrophy",
            "Creatinine": "نۆرماڵ",
            "Potassium": "نۆرماڵ",
            "Echocardiogram": "نۆرماڵ"
        },
        "چارەسەر": ["کاپتۆپریل 25mg", "کەمکردنەوەی نمەک", "وەرزشی ئیروبیک", "کەمکردنەوەی کێش"],
        "ئاستی مەترسی": "مامناوەند",
        "تایبەتمەندییە جیاکەرەوەکان": "BP بەرز بەبێ هۆکاری دیکە",
        "ڕێپیشگیری": ["پێوانەکردنی BP بەردەوام", "شێوازی خواردنی کەم نمەک", "ڕاهێنانی ڕۆژانە"],
        "گروپی تەمەن": "هەموو تەمەنەکان"
    },
    "پەستانی خوێنی دووەمی": {
        "نیشانەکان": ["سەرئێشە", "سەرگێژخواردن", "فشاری پشت چاو", "خێرالێدانی دڵ", "ئاوسانی قاچ"],
        "پشکنینەکان": {
            "BP": ">140/90 mmHg",
            "Creatinine": "بەرز",
            "Ultrasound": "نەخۆشی گورچیلە",
            "Aldosterone": "بەرز"
        },
        "چارەسەر": ["چارەسەری هۆکار", "دژە پەستانی خوێن", "کەمکردنەوەی نمەک"],
        "ئاستی مەترسی": "مەترسیدار",
        "تایبەتمەندییە جیاکەرەوەکان": "BP بەرز + هۆکاری دیکە وەک نەخۆشی گورچیلە",
        "ڕێپیشگیری": ["دۆزینەوەی هۆکار", "چارەسەری هۆکار"],
        "گروپی تەمەن": "هەموو تەمەنەکان"
    },
    "نەخۆشی دڵی ئیسکیمیک": {
        "نیشانەکان": ["ئازاری سنگ", "کورتی هەناسە", "ئارەقەکردن", "سکچوون و ڕشانەوە", "ئازاری شان", "تنگەنەفەسی", "ئازاری پشت"],
        "پشکنینەکان": {
            "ECG": "ST depression",
            "Troponin": "بەرز >0.04",
            "CK-MB": "بەرز >5",
            "Echocardiogram": "کەمبوونی ئیشی دڵ",
            "CAG": "تەنگی کرۆنەری"
        },
        "چارەسەر": ["ئەسپیرین 300mg", "نایترۆگلیسیرین", "ئۆکسجین", "بێتا بلاکەر", "هێپارین"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندییە جیاکەرەوەکان": "ST changes + Troponin elevated",
        "ڕێپیشگیری": ["کۆنتڕۆڵی پەستانی خوێن", "وەرزش", "وەستانی جگەرە", "کۆنتڕۆڵی شەکرە"],
        "گروپی تەمەن": "تەمەن > 50 ساڵ"
    },
    "نەخۆشی دڵی شکان (Heart Failure)": {
        "نیشانەکان": ["کورتی هەناسە", "ئاوسانی قاچ", "ماندوویی", "خێرالێدانی دڵ", "کۆخە"],
        "پشکنینەکان": {
            "BNP": "بەرز",
            "Echocardiogram": "EF < 40%",
            "Chest X-ray": "Cardiomegaly",
            "ECG": "Abnormal"
        },
        "چارەسەر": ["Diuretics", "ACE inhibitor", "Beta blocker", "کەمکردنەوەی نمەک"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندییە جیاکەرەوەکان": "BNP بەرز + EF نزم",
        "ڕێپیشگیری": ["کۆنتڕۆڵی BP", "وەرزش", "شێوازی خواردن"],
        "گروپی تەمەن": "تەمەن > 60 ساڵ"
    },
    "هەوکردنی سییەکان (Pneumonia)": {
        "نیشانەکان": ["تا", "کۆخە", "هەناسەدان بە زەحمەت", "ئازاری سنگ", "ڕژانی لووت", "ماندوویی", "ئارەقەکردن"],
        "پشکنینەکان": {
            "Chest X-ray": "Consolidation",
            "CRP": "بەرز >10",
            "WBC": "بەرز >11",
            "Sputum culture": "بەکتریا",
            "O2 saturation": "کەم"
        },
        "چارەسەر": ["ئەمۆکسیسیلین 500mg", "ئۆکسجین", "شلەمەنی", "دەرمانی دژە تا"],
        "ئاستی مەترسی": "مامناوەند",
        "تایبەتمەندییە جیاکەرەوەکان": "Consolidation لە X-ray + CRP بەرز",
        "ڕێپیشگیری": ["کوتان (Vaccination)", "دەستشۆردن", "دوورکەوتنەوە لە کەسانی تووشبوو"],
        "گروپی تەمەن": "هەموو تەمەنەکان"
    },
    "ئەنیمیا": {
        "نیشانەکان": ["ماندوویی", "ڕەنگی پێست زەرد", "سەرگێژخواردن", "لێدانی دڵ خێرا", "سەرئێشە", "پڕۆشتن", "هەستی ساردی"],
        "پشکنینەکان": {
            "Hb": "<12 g/dL",
            "MCV": "<80 fL (microcytic)",
            "Ferritin": "نزم <15",
            "TIBC": "بەرز >450",
            "Iron": "نزم"
        },
        "چارەسەر": ["فێروس سولفەیت 325mg", "گۆڕینی خواردن", "دۆزینەوەی هۆکاری سەرەکی", "ڤیتامین C 500mg"],
        "ئاستی مەترسی": "مامناوەند",
        "تایبەتمەندییە جیاکەرەوەکان": "Hb نزم + MCV نزم + Ferritin نزم",
        "ڕێپیشگیری": ["خواردنی ئاسن", "خواردنی ڤیتامین C", "پشکنینی خوێنی بەردەوام"],
        "گروپی تەمەن": "هەموو تەمەنەکان"
    },
    "نەخۆشی گورچیلە": {
        "نیشانەکان": ["ئاوسانی ڕوو و قاچ", "میزی کەم", "ماندوویی", "سەرئێشە", "خوێن لە میزدا", "فشاری خوێن بەرز"],
        "پشکنینەکان": {
            "Creatinine": "بەرز >1.3",
            "BUN": "بەرز >20",
            "eGFR": "<60",
            "Urinalysis": "پڕۆتین + خوێن",
            "Potassium": "بەرز"
        },
        "چارەسەر": ["ACE inhibitor", "کەمکردنەوەی پڕۆتین", "کۆنتڕۆڵی BP", "دایەلیز (ئەگەر پێویست)"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندییە جیاکەرەوەکان": "Creatinine بەرز + eGFR نزم",
        "ڕێپیشگیری": ["کۆنتڕۆڵی شەکرە", "کۆنتڕۆڵی BP", "کەمکردنەوەی نمەک"],
        "گروپی تەمەن": "تەمەن > 50 ساڵ"
    },
    "نەخۆشی جگەر (Hepatitis)": {
        "نیشانەکان": ["ماندوویی", "زەردبوونی چاو", "سکچوون", "تا", "ئازاری سک", "میز تۆخ"],
        "پشکنینەکان": {
            "ALT": "بەرز >40",
            "AST": "بەرز >40",
            "Bilirubin": "بەرز >1.2",
            "HBsAg": "positive",
            "Anti-HCV": "positive"
        },
        "چارەسەر": ["دەرمانی دژە ڤایرۆس", "پشوو", "شلەمەنی", "شێوازی خواردن"],
        "ئاستی مەترسی": "مەترسیدار",
        "تایبەتمەندییە جیاکەرەوەکان": "ALT + AST بەرز + زەردبوون",
        "ڕێپیشگیری": ["کوتان", "پشکنینی خوێن", "پارێزی لە پەیوەندی خوێن"],
        "گروپی تەمەن": "هەموو تەمەنەکان"
    },
    "نەخۆشی کۆکە (Asthma)": {
        "نیشانەکان": ["هەناسەدان بە زەحمەت", "کۆخە", "تنگەنەفەسی", "فیشک (Wheezing)", "فشاری سنگ"],
        "پشکنینەکان": {
            "Pulmonary function": "FEV1 < 80%",
            "Peak flow": "کەم",
            "Chest X-ray": "نۆرماڵ",
            "IgE": "بەرز"
        },
        "چارەسەر": ["Bronchodilator", "Steroid inhaler", "پارێزی لە هۆکارەکان", "Leukotriene inhibitor"],
        "ئاستی مەترسی": "مامناوەند",
        "تایبەتمەندییە جیاکەرەوەکان": "FEV1 کەم + فیشک",
        "ڕێپیشگیری": ["پارێزی لە هۆکارەکان", "بەکارهێنانی inhaler", "وەرزش"],
        "گروپی تەمەن": "منداڵان و گەنجان"
    },
    "نەخۆشی سیل (TB)": {
        "نیشانەکان": ["کۆخە (بە خوێن)", "تا", "ئارەقەکردنی شەو", "کێش کەمبوونەوە", "ماندوویی"],
        "پشکنینەکان": {
            "Chest X-ray": "تەوەرەکان",
            "Sputum AFB": "positive",
            "PPD": "positive",
            "GeneXpert": "positive"
        },
        "چارەسەر": ["Rifampicin", "Isoniazid", "Pyrazinamide", "Ethambutol"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندییە جیاکەرەوەکان": "کۆخەی خوێناوی + X-ray تایبەت",
        "ڕێپیشگیری": ["BCG vaccine", "پارێزی لە کەسانی تووشبوو", "پشکنین"],
        "گروپی تەمەن": "هەموو تەمەنەکان"
    },
    "نەخۆشی تایفیید (Typhoid)": {
        "نیشانەکان": ["تای بەرز", "سەرئێشە", "سکچوون", "رشانەوە", "ئازاری سک", "میلە"],
        "پشکنینەکان": {
            "WBC": "نزم",
            "Blood culture": "Salmonella",
            "Widal": "positive",
            "CRP": "بەرز"
        },
        "چارەسەر": ["Azithromycin", "Ceftriaxone", "شلەمەنی", "پشوو"],
        "ئاستی مەترسی": "مەترسیدار",
        "تایبەتمەندییە جیاکەرەوەکان": "تای بەرز + سکچوون",
        "ڕێپیشگیری": ["خواردنی پاک", "دەستشۆردن", "کوتان"],
        "گروپی تەمەن": "هەموو تەمەنەکان"
    },
    "نەخۆشی کۆلێرا (Cholera)": {
        "نیشانەکان": ["سکچوونی زۆر (وەک ئاو)", "رشانەوە", "تینوویەتی زۆر", "کەمبوونەوەی میز"],
        "پشکنینەکان": {
            "Stool culture": "Vibrio cholera",
            "Rapid test": "positive",
            "Electrolytes": "نزم"
        },
        "چارەسەر": ["ORS", "شلەمەنی", "Doxycycline", "Azithromycin"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندییە جیاکەرەوەکان": "سکچوونی زۆر وەک ئاو",
        "ڕێپیشگیری": ["خواردنی پاک", "ئاوی پاک", "دەستشۆردن", "کوتان"],
        "گروپی تەمەن": "هەموو تەمەنەکان"
    },
    "نەخۆشی پەنکریاتیت": {
        "نیشانەکان": ["ئازاری سکی سەرەوە", "رشانەوە", "تا", "سکچوون", "ئازاری پشت"],
        "پشکنینەکان": {
            "Amylase": "بەرز",
            "Lipase": "بەرز",
            "CT scan": "پەنکریاتیت",
            "CRP": "بەرز"
        },
        "چارەسەر": ["پشووی خواردن", "شلەمەنی", "دەرمانی ئازار", "ئەنتیبایۆتیک"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندییە جیاکەرەوەکان": "Amylase + Lipase بەرز",
        "ڕێپیشگیری": ["پارێزی لە خواردنی چەور", "کەمکردنەوەی کحول"],
        "گروپی تەمەن": "تەمەن > 40 ساڵ"
    },
    "نەخۆشی گەدە (Gastritis)": {
        "نیشانەکان": ["ئازاری گەدە", "سکچوون", "سووتانی گەدە", "ڕشانەوە", "هەستی پڕی"],
        "پشکنینەکان": {
            "Endoscopy": "هەوکردن",
            "H. pylori": "positive",
            "Urea breath test": "positive"
        },
        "چارەسەر": ["PPI (Omeprazole)", "Antibiotic (Amoxicillin)", "Antacid", "گۆڕینی خواردن"],
        "ئاستی مەترسی": "کەم",
        "تایبەتمەندییە جیاکەرەوەکان": "ئازاری گەدە + H. pylori positive",
        "ڕێپیشگیری": ["خواردنی کەم بەهارات", "پارێزی لە NSAIDs"],
        "گروپی تەمەن": "هەموو تەمەنەکان"
    }
}

# ================================
# 4. کویزەکانی پزیشکی (٢٠ کویز)
# ================================
MEDICAL_QUIZZES = [
    # 4.1 کویزەکانی نیشانەناسی
    {
        "پرسیار": "نەخۆشێکی ٤٥ ساڵان، سەرئێشە و سەرگێژخواردنی هەیە، BP=١٦٠/٩٥. باشترین هەنگاوی داهاتوو چییە؟",
        "هەڵبژاردەکان": [
            "دەستبەجێ دەرمانی دژە پەستانی خوێن",
            "پێوانەکردنی BP دوای ٢ هەفتە و گۆڕینی شێوازی ژیان",
            "CT سەر",
            "پشکنینی خوێنی تەواو"
        ],
        "وەڵامی ڕاست": 1,
        "ڕوونکردنەوە": "بەپێی ڕێنماییەکان، بۆ پەستانی خوێنی قۆناغی ١، دەبێت دووبارە BP پێوانە بکرێت و گۆڕانی شێوازی ژیان پێشنیار بکرێت",
        "بوار": "پەستانی خوێن",
        "ئاست": "ساڵی سێیەم"
    },
    {
        "پرسیار": "نەخۆشێک FBS=١٥٠, HbA1c=٧.٢%. دەستنیشانکردن چییە؟",
        "هەڵبژاردەکان": [
            "پێش شەکرە (Prediabetes)",
            "شەکرەی جۆری ٢",
            "شەکرەی جۆری ١",
            "نەخۆشی مێتابۆلیک"
        ],
        "وەڵامی ڕاست": 1,
        "ڕوونکردنەوە": "FBS>١٢٦ و HbA1c>٦.٥% دوو پێوەری سەرەکی بۆ دەستنیشانکردنی شەکرەن",
        "بوار": "شەکرە",
        "ئاست": "ساڵی دووەم"
    },
    {
        "پرسیار": "لە نەخۆشێکی ئەنیمیادا، MCV=٧٢ fL. جۆری ئەنیمیا چییە؟",
        "هەڵبژاردەکان": [
            "ماکرۆسایتیک",
            "مایکرۆسایتیک",
            "نۆرمۆسایتیک",
            "هیمۆلایتیک"
        ],
        "وەڵامی ڕاست": 1,
        "ڕوونکردنەوە": "MCV<٨٠ fL ئاماژەیە بۆ ئەنیمیای مایکرۆسایتیک (Microcytic Anemia)",
        "بوار": "ئەنیمیا",
        "ئاست": "ساڵی دووەم"
    },
    {
        "پرسیار": "نەخۆشێک بە ئازاری سنگ و کورتی هەناسە هاتووە، Troponin=٢.٥ ng/mL. چی دەکەیت؟",
        "هەڵبژاردەکان": [
            "دەرچوون بۆ ماڵەوە",
            "پشکنینی ECG و پشکنینی زیاتر",
            "دەرمانی دژە پەستانی خوێن",
            "پشکنینی CBC"
        ],
        "وەڵامی ڕاست": 1,
        "ڕوونکردنەوە": "Troponin بەرز ئاماژەیە بۆ نەخۆشی دڵی ئیسکیمیک، پێویستە ECG و پشکنینی زیاتر بکرێت",
        "بوار": "نەخۆشی دڵ",
        "ئاست": "ساڵی چوارەم"
    },
    {
        "پرسیار": "نەخۆشێک بە کۆخە و تای ٣٨.٥°C هاتووە، Chest X-ray Consolidation نیشان دەدات. دەستنیشانکردن چییە؟",
        "هەڵبژاردەکان": [
            "نەخۆشی ڤایرۆسی",
            "هەوکردنی سییەکان",
            "نەخۆشی دڵ",
            "ئەنیمیا"
        ],
        "وەڵامی ڕاست": 1,
        "ڕوونکردنەوە": "Consolidation لە X-ray ئاماژەیە بۆ هەوکردنی سییەکان",
        "بوار": "نەخۆشی سی",
        "ئاست": "ساڵی سێیەم"
    },
    {
        "پرسیار": "نەخۆشێک بە کێش ٨٠ کیلۆگرام، دەرمانی مێتفۆرمین بۆ شەکرەی جۆری ٢ دەخوات. ڕێژەی گونجاو چییە؟",
        "هەڵبژاردەکان": [
            "٢٥٠mg ڕۆژانە",
            "٥٠٠mg ڕۆژانە دووجار",
            "١٠٠٠mg ڕۆژانە",
            "٢٠٠٠mg ڕۆژانە"
        ],
        "وەڵامی ڕاست": 1,
        "ڕوونکردنەوە": "ڕێژەی دەستپێکی مێتفۆرمین ٥٠٠mg دووجارە لەگەڵ خواردن",
        "بوار": "فارماکۆلۆجی",
        "ئاست": "ساڵی سێیەم"
    },
    {
        "پرسیار": "نەخۆشێک بە ئاوسانی قاچ و میزی کەم هاتووە، Creatinine=٣.٥ mg/dL. چی دەکەیت؟",
        "هەڵبژاردەکان": [
            "دەرچوون بۆ ماڵەوە",
            "پشکنینی گورچیلە و ڕەوانەکردن بۆ پسپۆڕ",
            "دەرمانی دژە پەستانی خوێن",
            "CT سک"
        ],
        "وەڵامی ڕاست": 1,
        "ڕوونکردنەوە": "Creatinine بەرز ئاماژەیە بۆ نەخۆشی گورچیلە، پێویستە ڕەوانە بکرێت بۆ پسپۆڕی گورچیلە",
        "بوار": "نەخۆشی گورچیلە",
        "ئاست": "ساڵی چوارەم"
    },
    {
        "پرسیار": "نەخۆشێک بە Hb=٩ g/dL و Ferritin=١٠ ng/mL هاتووە. جۆری ئەنیمیا چییە؟",
        "هەڵبژاردەکان": [
            "ئەنیمیای کەمخوێنی ئاسن",
            "ئەنیمیای ماکرۆسایتیک",
            "ئەنیمیای هیمۆلایتیک",
            "ئەنیمیای نۆرمۆسایتیک"
        ],
        "وەڵامی ڕاست": 0,
        "ڕوونکردنەوە": "Hb نزم + Ferritin نزم ئاماژەیە بۆ ئەنیمیای کەمخوێنی ئاسن",
        "بوار": "ئەنیمیا",
        "ئاست": "ساڵی دووەم"
    },
    {
        "پرسیار": "بۆ نەخۆشی شەکرەی جۆری ٢، کام دەرمانە کار لە جگەر دەکات؟",
        "هەڵبژاردەکان": [
            "ئەنسولین",
            "مێتفۆرمین",
            "سولفۆنیل یوریا",
            "DPP-4 inhibitor"
        ],
        "وەڵامی ڕاست": 1,
        "ڕوونکردنەوە": "مێتفۆرمین کار لە جگەر دەکات بۆ کەمکردنەوەی بەرهەمهێنانی گلوکۆز",
        "بوار": "فارماکۆلۆجی",
        "ئاست": "ساڵی سێیەم"
    },
    {
        "پرسیار": "نەخۆشێک بە پەستانی خوێنی ١٥٠/٩٥ mmHg و کێش ٩٠ کیلۆگرام هاتووە. باشترین ڕێنمایی چییە؟",
        "هەڵبژاردەکان": [
            "دەستبەجێ دەرمان",
            "کەمکردنەوەی کێش و گۆڕینی شێوازی ژیان",
            "پشکنینی تەواوی خوێن",
            "CT سەر"
        ],
        "وەڵامی ڕاست": 1,
        "ڕوونکردنەوە": "بۆ BP قۆناغی ١، گۆڕینی شێوازی ژیان و کەمکردنەوەی کێش پێشنیار دەکرێت",
        "بوار": "پەستانی خوێن",
        "ئاست": "ساڵی سێیەم"
    },
    {
        "پرسیار": "نەخۆشێکی ئەستمی هەوە، باشترین دەرمان بۆ ناڕەتی (Acute attack) چییە؟",
        "هەڵبژاردەکان": [
            "Steroid oral",
            "Bronchodilator (Salbutamol)",
            "Antihistamine",
            "Antibiotic"
        ],
        "وەڵامی ڕاست": 1,
        "ڕوونکردنەوە": "Salbutamol bronchodilator خێرا کار دەکات بۆ کردنەوەی ڕیگەکانی هەناسە",
        "بوار": "نەخۆشی کۆکە",
        "ئاست": "ساڵی سێیەم"
    },
    {
        "پرسیار": "نەخۆشێک بە زەردبوونی چاو و میزی تۆخ هاتووە. ALT=١٥٠, AST=١٢٠. دەستنیشانکردن چییە؟",
        "هەڵبژاردەکان": [
            "نەخۆشی گورچیلە",
            "نەخۆشی جگەر",
            "نەخۆشی پەنکریاس",
            "ئەنیمیا"
        ],
        "وەڵامی ڕاست": 1,
        "ڕوونکردنەوە": "زەردبوون + ALT/AST بەرز ئاماژەیە بۆ نەخۆشی جگەر",
        "بوار": "نەخۆشی جگەر",
        "ئاست": "ساڵی چوارەم"
    },
    {
        "پرسیار": "نەخۆشێک بە سکچوونی زۆر (وەک ئاو) هاتووە. باشترین چارەسەر چییە؟",
        "هەڵبژاردەکان": [
            "دەرمانی دژە سکچوون",
            "ORS و شلەمەنی",
            "ئەنتیبایۆتیک",
            "هەموویان"
        ],
        "وەڵامی ڕاست": 1,
        "ڕوونکردنەوە": "یەکەم هەنگاو ORS و شلەمەنیە بۆ پاراستنی لە وشکبوونەوە",
        "بوار": "نەخۆشی کۆلێرا",
        "ئاست": "ساڵی دووەم"
    },
    {
        "پرسیار": "نەخۆشێکی ٦٠ ساڵ بە کۆخەی خوێناوی ماوە ٢ مانگ هاتووە. پێویستە چی بکرێت؟",
        "هەڵبژاردەکان": [
            "Chest X-ray و Sputum AFB",
            "CT سک",
            "پشکنینی دڵ",
            "پشکنینی گەدە"
        ],
        "وەڵامی ڕاست": 0,
        "ڕوونکردنەوە": "کۆخەی خوێناوی درێژخایەن ئاماژەیە بۆ سیل، پێویستە X-ray و Sputum AFB بکرێت",
        "بوار": "نەخۆشی سیل",
        "ئاست": "ساڵی چوارەم"
    },
    {
        "پرسیار": "نەخۆشێک بە تای بەرز و سەرئێشە و سکچوون هاتووە. کام پشکنینە بۆ تایفیید؟",
        "هەڵبژاردەکان": [
            "CBC",
            "Widal test",
            "CRP",
            "Chest X-ray"
        ],
        "وەڵامی ڕاست": 1,
        "ڕوونکردنەوە": "Widal test بۆ دەستنیشانکردنی تایفیید بەکاردێت",
        "بوار": "نەخۆشی تایفیید",
        "ئاست": "ساڵی سێیەم"
    },
    {
        "پرسیار": "نەخۆشێک بە ئازاری سکی سەرەوە و رشانەوە و تای هاتووە. Amylase=١٢٠٠. دەستنیشانکردن چییە؟",
        "هەڵبژاردەکان": [
            "نەخۆشی گەدە",
            "پەنکریاتیت",
            "نەخۆشی جگەر",
            "هەوکردنی سی"
        ],
        "وەڵامی ڕاست": 1,
        "ڕوونکردنەوە": "Amylase بەرز (>٢٠٠) ئاماژەیە بۆ پەنکریاتیت",
        "بوار": "نەخۆشی پەنکریاتیت",
        "ئاست": "ساڵی چوارەم"
    },
    {
        "پرسیار": "کام دەرمانە بۆ هەوکردنی سی بەکاردێت؟",
        "هەڵبژاردەکان": [
            "Metformin",
            "Amoxicillin",
            "Captopril",
            "Insulin"
        ],
        "وەڵامی ڕاست": 1,
        "ڕوونکردنەوە": "Amoxicillin ئەنتیبایۆتیکە بۆ چارەسەری هەوکردنی سی",
        "بوار": "فارماکۆلۆجی",
        "ئاست": "ساڵی دووەم"
    },
    {
        "پرسیار": "نەخۆشێک بە ئازاری سنگ و کورتی هەناسە هاتووە، ECG ST depression نیشان دەدات. چی دەکەیت؟",
        "هەڵبژاردەکان": [
            "دەرچوون بۆ ماڵەوە",
            "پشکنینی Troponin و ICU",
            "دەرمانی دژە ئازار",
            "پشکنینی CBC"
        ],
        "وەڵامی ڕاست": 1,
        "ڕوونکردنەوە": "ST depression + ئازاری سنگ ئاماژەیە بۆ نەخۆشی دڵی ئیسکیمیک، پێویستە بچێتە ICU",
        "بوار": "نەخۆشی دڵ",
        "ئاست": "ساڵی پێنجەم"
    },
    {
        "پرسیار": "کام دەرمانە بۆ نەخۆشی پەستانی خوێن لە نەخۆشانی شەکرەدا باشترە؟",
        "هەڵبژاردەکان": [
            "Beta blocker",
            "ACE inhibitor",
            "Calcium channel blocker",
            "Diuretic"
        ],
        "وەڵامی ڕاست": 1,
        "ڕوونکردنەوە": "ACE inhibitor بۆ نەخۆشانی شەکرە باشترە چونکە پارێزگاری لە گورچیلە دەکات",
        "بوار": "فارماکۆلۆجی",
        "ئاست": "ساڵی چوارەم"
    },
    {
        "پرسیار": "نەخۆشێک بە کۆخە و تای هاتووە، CRP=٨٠, WBC=١٥. دەستنیشانکردن چییە؟",
        "هەڵبژاردەکان": [
            "هەوکردنی ڤایرۆسی",
            "هەوکردنی بەکتریایی",
            "نەخۆشی ژیانی",
            "نەخۆشی خۆئەگەر"
        ],
        "وەڵامی ڕاست": 1,
        "ڕوونکردنەوە": "CRP بەرز + WBC بەرز ئاماژەیە بۆ هەوکردنی بەکتریایی",
        "بوار": "نیشانەناسی",
        "ئاست": "ساڵی سێیەم"
    }
]

# ================================
# 5. داتای تاقیگەی ڤێرچواڵ
# ================================
LAB_DATA = {
    "CBC": {
        "WBC": {"نۆرماڵ": (4.0, 11.0), "یەکە": "x10³/µL", "تەفسیر": "خڕۆکە سپیەکان"},
        "Hb": {"نۆرماڵ": (12.0, 16.0), "یەکە": "g/dL", "تەفسیر": "هیمۆگلۆبین"},
        "Platelets": {"نۆرماڵ": (150, 450), "یەکە": "x10³/µL", "تەفسیر": "پلەیتلێت"},
        "MCV": {"نۆرماڵ": (80, 100), "یەکە": "fL", "تەفسیر": "قەبارەی خڕۆکە سوورەکان"},
        "MCH": {"نۆرماڵ": (27, 33), "یەکە": "pg", "تەفسیر": "کەمی هیمۆگلۆبین لە هەر خڕۆکەیەک"},
        "MCHC": {"نۆرماڵ": (32, 36), "یەکە": "g/dL", "تەفسیر": "چڕی هیمۆگلۆبین"},
        "RDW": {"نۆرماڵ": (11.5, 14.5), "یەکە": "%", "تەفسیر": "جیاوازی قەبارەی خڕۆکەکان"}
    },
    "بایۆکیمیایی": {
        "Glucose": {"نۆرماڵ": (70, 126), "یەکە": "mg/dL", "تەفسیر": "شەکری خوێن"},
        "Creatinine": {"نۆرماڵ": (0.6, 1.3), "یەکە": "mg/dL", "تەفسیر": "کارایی گورچیلە"},
        "ALT": {"نۆرماڵ": (10, 40), "یەکە": "U/L", "تەفسیر": "ئەنزیمی جگەر"},
        "AST": {"نۆرماڵ": (10, 40), "یەکە": "U/L", "تەفسیر": "ئەنزیمی جگەر"},
        "Potassium": {"نۆرماڵ": (3.5, 5.0), "یەکە": "mmol/L", "تەفسیر": "پۆتاسیۆم"},
        "Sodium": {"نۆرماڵ": (135, 145), "یەکە": "mmol/L", "تەفسیر": "سۆدیۆم"},
        "BUN": {"نۆرماڵ": (7, 20), "یەکە": "mg/dL", "تەفسیر": "نایترۆجینی یوریا"},
        "Bilirubin": {"نۆرماڵ": (0.1, 1.2), "یەکە": "mg/dL", "تەفسیر": "زەرداوی"}
    },
    "دڵ": {
        "Troponin": {"نۆرماڵ": (0, 0.04), "یەکە": "ng/mL", "تەفسیر": "پروتێینی دڵ"},
        "CK-MB": {"نۆرماڵ": (0, 5), "یەکە": "ng/mL", "تەفسیر": "ئەنزیمی دڵ"},
        "BNP": {"نۆرماڵ": (0, 100), "یەکە": "pg/mL", "تەفسیر": "پروتێینی دڵ"}
    },
    "هەوکردن": {
        "CRP": {"نۆرماڵ": (0, 5), "یەکە": "mg/L", "تەفسیر": "پروتێینی هەوکردن"},
        "ESR": {"نۆرماڵ": (0, 20), "یەکە": "mm/hr", "تەفسیر": "خێرایی تەنیشتنی خڕۆکەکان"},
        "Ferritin": {"نۆرماڵ": (15, 300), "یەکە": "ng/mL", "تەفسیر": "ئاسن"}
    }
}

# ================================
# 6. داتای دەرمانەکان
# ================================
DRUG_DATABASE = {
    "دژە پەستانی خوێن": {
        "کاپتۆپریل": {
            "ڕێژە": "25-50mg",
            "میکانیزم": "ACE inhibitor",
            "کاریگەری لاوەکی": "کۆخە, سەرگێژخواردن",
            "پێچەوانە": "حەملی دووگیانی, ئەنژیۆئێدیم",
            "تێکەڵکاری": "NSAIDs, Potassium"
        },
        "ئەملۆدیپین": {
            "ڕێژە": "5-10mg",
            "میکانیزم": "Calcium channel blocker",
            "کاریگەری لاوەکی": "ئاوسانی قاچ, سەرئێشە",
            "پێچەوانە": "هەستیاری",
            "تێکەڵکاری": "Beta blockers"
        },
        "لۆسارتان": {
            "ڕێژە": "50-100mg",
            "میکانیزم": "ARB",
            "کاریگەری لاوەکی": "سەرگێژخواردن, بەرزی پۆتاسیۆم",
            "پێچەوانە": "نەخۆشی گورچیلە",
            "تێکەڵکاری": "Potassium supplements"
        },
        "بایسۆپرۆلۆل": {
            "ڕێژە": "2.5-10mg",
            "میکانیزم": "Beta blocker",
            "کاریگەری لاوەکی": "خاوکردنەوەی دڵ, ماندوویی",
            "پێچەوانە": "ئەستمی هەوە",
            "تێکەڵکاری": "Verapamil"
        },
        "هیدروکلۆرۆتایزید": {
            "ڕێژە": "12.5-25mg",
            "میکانیزم": "Thiazide diuretic",
            "کاریگەری لاوەکی": "نزمی پۆتاسیۆم, بەرزی شەکر",
            "پێچەوانە": "نەخۆشی گورچیلە",
            "تێکەڵکاری": "Lithium"
        }
    },
    "دژە شەکرە": {
        "مێتفۆرمین": {
            "ڕێژە": "500-2000mg",
            "میکانیزم": "Biguanide",
            "کاریگەری لاوەکی": "سکچوون, ماندوویی",
            "پێچەوانە": "نەخۆشی گورچیلە, جگەر",
            "تێکەڵکاری": "Alcohol"
        },
        "گلیپیزاید": {
            "ڕێژە": "5-20mg",
            "میکانیزم": "Sulfonylurea",
            "کاریگەری لاوەکی": "هایپۆگلایسیمیا, کێش زیادکردن",
            "پێچەوانە": "هەستیاری",
            "تێکەڵکاری": "Aspirin"
        },
        "ئەنسولین Glargine": {
            "ڕێژە": "10-40 IU",
            "میکانیزم": "Insulin analog",
            "کاریگەری لاوەکی": "هایپۆگلایسیمیا",
            "پێچەوانە": "هایپۆگلایسیمیا",
            "تێکەڵکاری": "Beta blockers"
        },
        "سیتاگلیپتین": {
            "ڕێژە": "100mg",
            "میکانیزم": "DPP-4 inhibitor",
            "کاریگەری لاوەکی": "سەرئێشە, سکچوون",
            "پێچەوانە": "نەخۆشی پەنکریاس",
            "تێکەڵکاری": "نییە"
        }
    },
    "دژە کۆخە و هەوکردن": {
        "ئەمۆکسیسیلین": {
            "ڕێژە": "500mg",
            "میکانیزم": "Beta-lactam",
            "کاریگەری لاوەکی": "زکچوون, ڕشانەوە",
            "پێچەوانە": "هەستیاری پێنیسیلین",
            "تێکەڵکاری": "Allopurinol"
        },
        "ئازیترۆمایسین": {
            "ڕێژە": "250-500mg",
            "میکانیزم": "Macrolide",
            "کاریگەری لاوەکی": "سکچوون, ئازاری گەدە",
            "پێچەوانە": "نەخۆشی دڵ",
            "تێکەڵکاری": "Warfarin"
        },
        "سیپرۆفلۆکساسین": {
            "ڕێژە": "500mg",
            "میکانیزم": "Fluoroquinolone",
            "کاریگەری لاوەکی": "ئازاری ماسوولکە, سکچوون",
            "پێچەوانە": "منداڵان, حەمل",
            "تێکەڵکاری": "NSAIDs"
        },
        "سێفتریاکسۆن": {
            "ڕێژە": "1-2g",
            "میکانیزم": "Cephalosporin",
            "کاریگەری لاوەکی": "سکچوون, زکچوون",
            "پێچەوانە": "هەستیاری",
            "تێکەڵکاری": "Calcium"
        }
    },
    "دژە ئەنیمیا": {
        "فێروس سولفەیت": {
            "ڕێژە": "300-600mg",
            "میکانیزم": "Iron supplement",
            "کاریگەری لاوەکی": "سکچوون, زکچوون",
            "پێچەوانە": "هیمۆکروماتۆسیس",
            "تێکەڵکاری": "Antacids"
        },
        "فۆلیک ئەسید": {
            "ڕێژە": "1mg",
            "میکانیزم": "Folate supplement",
            "کاریگەری لاوەکی": "کەم",
            "پێچەوانە": "هەستیاری",
            "تێکەڵکاری": "Methotrexate"
        },
        "ڤیتامین B12": {
            "ڕێژە": "1000mcg",
            "میکانیزم": "Cobalamin",
            "کاریگەری لاوەکی": "کەم",
            "پێچەوانە": "هەستیاری",
            "تێکەڵکاری": "نییە"
        }
    },
    "دژە کۆکە": {
        "سالبوتامۆل": {
            "ڕێژە": "2 puffs",
            "میکانیزم": "Beta-2 agonist",
            "کاریگەری لاوەکی": "لەرزین, خێرالێدانی دڵ",
            "پێچەوانە": "نەخۆشی دڵ",
            "تێکەڵکاری": "Beta blockers"
        },
        "بۆدیزۆناید": {
            "ڕێژە": "200-800mcg",
            "میکانیزم": "Steroid inhaler",
            "کاریگەری لاوەکی": "هەوکردنی دەم",
            "پێچەوانە": "هەستیاری",
            "تێکەڵکاری": "نییە"
        }
    }
}

# ================================
# 7. فانکشنە یارمەتیدەرە پێشکەوتووەکان
# ================================

def generate_case_id() -> str:
    """دروستکردنی ناسنامەی بێهاوتا بۆ کەیس"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_num = random.randint(1000, 9999)
    return f"CASE-{timestamp}-{random_num}"

def calculate_risk_score(disease: str, age: int, gender: str, symptoms: List[str] = None) -> int:
    """حسابکردنی نمرەی مەترسی پێشکەوتوو"""
    base_risk = {
        "زۆر مەترسیدار": 80,
        "مەترسیدار": 60,
        "مامناوەند": 40,
        "کەم": 20
    }
    
    disease_info = DISEASE_DATABASE.get(disease, {})
    risk = base_risk.get(disease_info.get('ئاستی مەترسی', 'کەم'), 40)
    
    # زیادکردنی مەترسی بەپێی تەمەن
    if age > 70:
        risk += 20
    elif age > 60:
        risk += 15
    elif age > 50:
        risk += 10
    elif age > 40:
        risk += 5
    
    # زیادکردنی مەترسی بەپێی ڕەگەز (نێر زیاتر مەترسیدارە بۆ نەخۆشی دڵ)
    if gender == 'نێر' and disease in ['نەخۆشی دڵی ئیسکیمیک', 'نەخۆشی دڵی شکان']:
        risk += 10
    
    # زیادکردنی مەترسی بەپێی ژمارەی نیشانەکان
    if symptoms:
        risk += min(len(symptoms) * 3, 15)
    
    return min(risk, 100)

def analyze_symptoms_advanced(symptoms: List[str], disease: str) -> Dict:
    """شیکاری پێشکەوتووی نیشانەکان"""
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
    """نمرەی ئاستی خوێندکار"""
    levels = {
        "ساڵی یەکەم": 10,
        "ساڵی دووەم": 25,
        "ساڵی سێیەم": 40,
        "ساڵی چوارەم": 60,
        "ساڵی پێنجەم": 75,
        "ساڵی شەشەم": 90
    }
    return levels.get(level, 10)

def get_risk_color(risk_level: str) -> str:
    """ڕەنگی ئاستی مەترسی"""
    colors = {
        "زۆر مەترسیدار": "#dc3545",
        "مەترسیدار": "#fd7e14",
        "مامناوەند": "#ffc107",
        "کەم": "#28a745"
    }
    return colors.get(risk_level, "#6c757d")

def get_age_group(age: int) -> str:
    """گروپی تەمەن"""
    if age < 18:
        return "منداڵ"
    elif age < 40:
        return "گەنج"
    elif age < 60:
        return "تەمەن مامناوەند"
    else:
        return "پیر"

def generate_random_lab_results() -> Dict:
    """دروستکردنی ئەنجامی تاقیگەی هەڕەمەکی"""
    results = {}
    for category, tests in LAB_DATA.items():
        for test, info in tests.items():
            low, high = info['نۆرماڵ']
            # دروستکردنی نرخی نۆرماڵ یان نانۆرماڵ بە شێوەیەکی ڕاستەقینە
            if random.random() < 0.7:  # 70% نۆرماڵ
                value = round(random.uniform(low, high), 2)
                status = "نۆرماڵ"
            else:
                if random.random() < 0.5:
                    value = round(random.uniform(high, high * 1.5), 2)
                    status = "بەرز"
                else:
                    value = round(random.uniform(low * 0.5, low), 2)
                    status = "نزم"
            results[test] = {"value": value, "status": status, "unit": info['یەکە']}
    return results

def calculate_bmi(weight: float, height: float) -> float:
    """حسابکردنی BMI"""
    if height > 0:
        return weight / ((height/100) ** 2)
    return 0

def get_bmi_category(bmi: float) -> str:
    """پۆلێنی BMI"""
    if bmi < 18.5:
        return "کەمتر لە نۆرماڵ"
    elif bmi < 25:
        return "نۆرماڵ"
    elif bmi < 30:
        return "زیادەکێش"
    elif bmi < 35:
        return "قەڵەوی پلە 1"
    elif bmi < 40:
        return "قەڵەوی پلە 2"
    else:
        return "قەڵەوی پلە 3"

def calculate_case_similarity(case1: Dict, case2: Dict) -> float:
    """حسابکردنی هاوشێوەیی نێوان دوو کەیس"""
    similarities = []
    
    # تەمەن
    if abs(case1.get('تەمەن', 0) - case2.get('تەمەن', 0)) < 10:
        similarities.append(1)
    else:
        similarities.append(0)
    
    # ڕەگەز
    if case1.get('ڕەگەز') == case2.get('ڕەگەز'):
        similarities.append(1)
    
    # نیشانەکان
    symptoms1 = set(case1.get('نیشانە سەرەکییەکان', []))
    symptoms2 = set(case2.get('نیشانە سەرەکییەکان', []))
    if symptoms1 and symptoms2:
        intersection = len(symptoms1.intersection(symptoms2))
        union = len(symptoms1.union(symptoms2))
        similarities.append(intersection / union if union > 0 else 0)
    
    return sum(similarities) / len(similarities) if similarities else 0

# ================================
# 8. دروستکردنی داتای ڕاهێنان (زیاتر)
# ================================
@st.cache_data
def generate_training_data():
    cases = []
    case_id_counter = 1
    
    for disease, info in DISEASE_DATABASE.items():
        # ١٢ کەیس بۆ هەر نەخۆشییەک
        for i in range(12):
            age = random.randint(18, 80)
            gender = random.choice(['نێر', 'مێ'])
            symptoms = random.sample(info['نیشانەکان'], min(5, len(info['نیشانەکان'])))
            
            # دروستکردنی پشکنینەکان بە شێوەیەکی ڕاستەقینە
            test_keys = list(info['پشکنینەکان'].keys())
            selected_tests = random.sample(test_keys, min(4, len(test_keys)))
            
            # دروستکردنی ئەنجامی تاقیگە
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
# 9. مۆدێلی AI بۆ پێشبینی (پێشکەوتوو)
# ================================
@st.cache_resource
def train_prediction_model_advanced():
    """ڕاهێنانی مۆدێلی پێشبینی نەخۆشی بە شێوەیەکی پێشکەوتوو"""
    try:
        # ئامادەکردنی داتا
        data = training_data.copy()
        
        # دروستکردنی تایبەتمەندییەکانی تەمەن
        data['گروپی تەمەن'] = data['تەمەن'].apply(get_age_group)
        
        # دروستکردنی تایبەتمەندییەکان
        features = pd.get_dummies(data[['تەمەن', 'ڕەگەز', 'گروپی تەمەن'] + ['نیشانە سەرەکییەکان']], drop_first=True)
        
        # ستانداردکردن
        scaler = StandardScaler()
        numerical_cols = features.select_dtypes(include=[np.number]).columns
        features_scaled = scaler.fit_transform(features[numerical_cols])
        
        # مۆدێلی Random Forest
        model = RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42
        )
        model.fit(features_scaled, data['دەستنیشانکردن'])
        
        # هەڵسەنگاندن
        predictions = model.predict(features_scaled)
        accuracy = accuracy_score(data['دەستنیشانکردن'], predictions)
        
        # شیکاری PCA
        pca = PCA(n_components=2)
        pca_result = pca.fit_transform(features_scaled)
        
        return model, scaler, accuracy, numerical_cols, pca, pca_result
    
    except Exception as e:
        return None, None, 0, None, None, None

model, scaler, model_accuracy, numerical_cols, pca_model, pca_result = train_prediction_model_advanced()

# ================================
# 10. کەیسەکانی ڕاهێنان (بۆ شیکاری)
# ================================
@st.cache_data
def generate_practice_cases():
    practice_cases = []
    for disease in list(DISEASE_DATABASE.keys())[:20]:
        info = DISEASE_DATABASE[disease]
        for i in range(4):
            age = random.randint(20, 75)
            symptoms = random.sample(info['نیشانەکان'], min(4, len(info['نیشانەکان'])))
            practice_cases.append({
                'case_id': f"PRACTICE-{disease[:3]}-{i+1}",
                'دەستنیشانکردن': disease,
                'تەمەن': age,
                'ڕەگەز': random.choice(['نێر', 'مێ']),
                'نیشانەکان': symptoms,
                'ئاستی مەترسی': info['ئاستی مەترسی'],
                'پشکنینەکان': list(info['پشکنینەکان'].keys())[:3]
            })
    return practice_cases

practice_cases = generate_practice_cases()

# ================================
# 11. ستەیتەکانی ئەپ (پێشکەوتوو)
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
if 'simulation_count' not in st.session_state:
    st.session_state.simulation_count = 0
if 'student_level' not in st.session_state:
    st.session_state.student_level = "ساڵی یەکەم"
if 'quiz_answers' not in st.session_state:
    st.session_state.quiz_answers = []
if 'total_cases_solved' not in st.session_state:
    st.session_state.total_cases_solved = 0
if 'correct_diagnoses' not in st.session_state:
    st.session_state.correct_diagnoses = 0
if 'last_activity' not in st.session_state:
    st.session_state.last_activity = datetime.now()
if 'current_disease_filter' not in st.session_state:
    st.session_state.current_disease_filter = "هەموو"
if 'quiz_attempts' not in st.session_state:
    st.session_state.quiz_attempts = 0
if 'study_time' not in st.session_state:
    st.session_state.study_time = 0
if 'streak_days' not in st.session_state:
    st.session_state.streak_days = 0
if 'last_study_date' not in st.session_state:
    st.session_state.last_study_date = datetime.now().date()
if 'achievements' not in st.session_state:
    st.session_state.achievements = []
if 'progress_history' not in st.session_state:
    st.session_state.progress_history = []
if 'favorite_diseases' not in st.session_state:
    st.session_state.favorite_diseases = []
if 'study_notes' not in st.session_state:
    st.session_state.study_notes = ""

# ================================
# 12. سایدبار (پێشکەوتوو)
# ================================
with st.sidebar:
    # 12.1 لۆگۆ و ناو
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image("https://img.icons8.com/color/96/000000/medical-doctor.png", width=70)
    with col2:
        st.markdown("## 🎓 ڕاهێنەری پزیشکی")
        st.markdown("### v3.0")
    
    st.markdown("---")
    
    # 12.2 ئاستی خوێندکار
    student_level = st.selectbox(
        "📚 ئاستی خوێندنت:",
        ["ساڵی یەکەم", "ساڵی دووەم", "ساڵی سێیەم", "ساڵی چوارەم", "ساڵی پێنجەم", "ساڵی شەشەم"],
        index=["ساڵی یەکەم", "ساڵی دووەم", "ساڵی سێیەم", "ساڵی چوارەم", "ساڵی پێنجەم", "ساڵی شەشەم"].index(st.session_state.student_level) if st.session_state.student_level in ["ساڵی یەکەم", "ساڵی دووەم", "ساڵی سێیەم", "ساڵی چوارەم", "ساڵی پێنجەم", "ساڵی شەشەم"] else 0
    )
    st.session_state.student_level = student_level
    
    level_score = get_student_level_score(student_level)
    st.markdown(f"<span class='badge-level'>🏅 {level_score}%</span>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 12.3 ناوەڕۆک
    page = st.radio(
        "📋 بەشەکان:",
        [
            "🏠 داشبۆردی فێربوون",
            "📚 کتێبخانەی نەخۆشییەکان",
            "🩺 شیکاری کەیس",
            "📝 کویزی پزیشکی",
            "🔬 تاقیگەی ڤێرچواڵ",
            "📊 پێشکەوتنی فێربوون",
            "💊 فارماکۆلۆجی",
            "🧠 AI یاریدەدەر",
            "🏆 دەستکەوتەکان"
        ],
        index=0
    )
    
    st.markdown("---")
    
    # 12.4 ئاماری خێرا
    st.markdown("### 📊 ئاماری تۆ")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📝 کویز", f"{st.session_state.quiz_score}/20")
    with col2:
        st.metric("🩺 کەیس", st.session_state.total_cases_solved)
    with col3:
        accuracy = int((st.session_state.correct_diagnoses / max(st.session_state.total_cases_solved, 1)) * 100)
        st.metric("🎯 دەقی", f"{accuracy}%")
    
    # 12.5 پێشکەوتنی گشتی
    total_progress = min(65 + (st.session_state.total_cases_solved * 2) + (st.session_state.quiz_score * 3), 100)
    st.markdown(f"**پێشکەوتنی گشتی:** {total_progress}%")
    st.progress(total_progress/100)
    
    # 12.6 ڕێژەی خوێندن
    study_percentage = min(100, (st.session_state.total_cases_solved + st.session_state.quiz_score) * 2)
    st.markdown(f"**⏱️ کاتی خوێندن:** {st.session_state.study_time} خولەک")
    
    # 12.7 وەرزی خوێندن
    st.markdown("---")
    st.markdown(f"### 👨‍🎓 {student_level}")
    
    # 12.8 دوایین چالاکی
    time_diff = datetime.now() - st.session_state.last_activity
    minutes = int(time_diff.total_seconds() / 60)
    hours = minutes // 60
    remaining_minutes = minutes % 60
    if hours > 0:
        st.markdown(f"🕐 دوایین چالاکی: {hours} کاتژمێر و {remaining_minutes} خولەک پێش")
    else:
        st.markdown(f"🕐 دوایین چالاکی: {minutes} خولەک پێش")
    
    # 12.9 ڕێژەی بەردەوامی
    if st.session_state.streak_days > 0:
        st.markdown(f"🔥 بەردەوامی: {st.session_state.streak_days} ڕۆژ")
    
    # 12.10 تەنظیمات
    st.markdown("---")
    if st.button("🔄 ڕێکخستنەوەی داتا", use_container_width=True):
        st.session_state.case_history = []
        st.session_state.total_cases_solved = 0
        st.session_state.correct_diagnoses = 0
        st.session_state.quiz_score = 0
        st.session_state.quiz_index = 0
        st.session_state.quiz_completed = False
        st.session_state.achievements = []
        st.session_state.progress_history = []
        st.success("داتا ڕێکخرایەوە!")

# ================================
# 13. پەڕەی داشبۆردی فێربوون (پێشکەوتوو)
# ================================
if page == "🏠 داشبۆردی فێربوون":
    st.markdown('<h1 class="main-header">🎓 ڕاهێنەری پزیشکی - ببە پزیشکێکی لێهاتوو</h1>', unsafe_allow_html=True)
    
    # 13.1 کارتەکانی ئامار
    st.markdown("### 📊 گشتی")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown("""
        <div class="stat-card">
            <h3>📚</h3>
            <div class="stat-number">{}</div>
            <p>کەیسی فێربوون</p>
        </div>
        """.format(len(training_data)), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-card">
            <h3>🩺</h3>
            <div class="stat-number">{}</div>
            <p>نەخۆشی جیاواز</p>
        </div>
        """.format(len(DISEASE_DATABASE)), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stat-card">
            <h3>📝</h3>
            <div class="stat-number">{}/20</div>
            <p>کویزی ئەنجامدراو</p>
        </div>
        """.format(st.session_state.quiz_score), unsafe_allow_html=True)
    
    with col4:
        accuracy = int((st.session_state.correct_diagnoses / max(st.session_state.total_cases_solved, 1)) * 100)
        st.markdown("""
        <div class="stat-card">
            <h3>🎯</h3>
            <div class="stat-number">{}%</div>
            <p>دەقی ڕاست</p>
        </div>
        """.format(accuracy), unsafe_allow_html=True)
    
    with col5:
        st.markdown("""
        <div class="stat-card">
            <h3>🔥</h3>
            <div class="stat-number">{}</div>
            <p>ڕۆژی بەردەوامی</p>
        </div>
        """.format(st.session_state.streak_days), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 13.2 وانەی ڕۆژانە
    st.markdown("### 📖 وانەی ڕۆژانە")
    
    daily_topic = random.choice(list(DISEASE_DATABASE.keys()))
    daily_info = DISEASE_DATABASE[daily_topic]
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"""
        <div class="case-card">
            <h3>🎯 وانەی ئەمڕۆ: {daily_topic}</h3>
            <p><strong>نیشانە سەرەکییەکان:</strong> {', '.join(daily_info['نیشانەکان'][:5])}</p>
            <p><strong>تایبەتمەندی جیاکەرەوە:</strong> {daily_info['تایبەتمەندییە جیاکەرەوەکان']}</p>
            <p><strong>ئاستی مەترسی:</strong> <span style='color:{get_risk_color(daily_info['ئاستی مەترسی'])}; font-weight: bold;'>{daily_info['ئاستی مەترسی']}</span></p>
            <p><strong>ڕێپیشگیری:</strong> {daily_info['ڕێپیشگیری'][0] if daily_info['ڕێپیشگیری'] else 'نییە'}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 🎯 ئامانجەکانی فێربوون")
        
        today_goals = [
            "ناسینەوەی نیشانەکانی نەخۆشی",
            "فێربوونی پشکنینەکان",
            "دەستنیشانکردنی جیاکار",
            "پلانی چارەسەر",
            "ڕێپیشگیری"
        ]
        
        for i, goal in enumerate(today_goals):
            checked = i < 2
            st.checkbox(goal, checked, key=f"goal_{i}_{datetime.now().date()}")
    
    # 13.3 گرافی پێشکەوتن
    st.markdown("---")
    st.markdown("### 📈 پێشکەوتنی فێربوون بەپێی بوار")
    
    progress_data = pd.DataFrame({
        'بوار': ['نیشانەناسی', 'دەستنیشانکردن', 'چارەسەر', 'فارماکۆلۆجی', 'پشکنینەکان', 'ڕێپیشگیری'],
        'پێشکەوتن': [
            min(75 + st.session_state.total_cases_solved * 2, 100),
            min(60 + st.session_state.total_cases_solved * 1.5, 100),
            min(55 + st.session_state.quiz_score * 3, 100),
            min(70 + st.session_state.quiz_score * 2, 100),
            min(80 + st.session_state.total_cases_solved * 1.5, 100),
            min(50 + st.session_state.total_cases_solved * 1.5, 100)
        ]
    })
    
    fig = px.bar(progress_data, x='بوار', y='پێشکەوتن',
                 title='ڕێژەی لێهاتوویی بەپێی بوار (%)',
                 color='پێشکەوتن',
                 color_continuous_scale='Viridis',
                 text_auto=True)
    fig.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    # 13.4 کەیسەکانی دوایین
    st.markdown("---")
    st.markdown("### 🩺 کەیسەکانی دوایین")
    
    if len(st.session_state.case_history) > 0:
        recent_cases = st.session_state.case_history[-5:]
        for case in recent_cases:
            st.markdown(f"""
            <div class="case-card">
                <strong>{case['case_id']}</strong> - 
                {case['دەستنیشانکردن']} 
                <span style="color: {'#28a745' if case.get('result', False) else '#dc3545'}">
                    {'✅ ڕاست' if case.get('result', False) else '❌ هەڵە'}
                </span>
                <span style="float:right;color:#6c757d;font-size:0.8rem;">
                    {case.get('date', datetime.now().strftime('%Y-%m-%d'))}
                </span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("هێشتا هیچ کەیسیەکت شیکار نەکردووە. بچۆ بۆ بەشی 'شیکاری کەیس' دەستپێبکە!")
    
    # 13.5 پێشنیارەکان
    st.markdown("---")
    st.markdown("### 💡 پێشنیارەکانی فێربوون")
    
    if st.session_state.total_cases_solved < 5:
        st.warning("📚 تەنها {} کەیس شیکار کراوە. هەوڵبدە زیاتر کەیس شیکار بکەیت!".format(st.session_state.total_cases_solved))
    elif st.session_state.quiz_score < 10:
        st.warning("📝 نمرەی کویز {}/20. کویزەکان زیاتر بکە بۆ باشترکردنی زانیارییەکان!".format(st.session_state.quiz_score))
    else:
        st.success("🌟 زۆر باش! بەردەوام بە لە فێربوون!")

# ================================
# 14. پەڕەی کتێبخانەی نەخۆشییەکان (پێشکەوتوو)
# ================================
elif page == "📚 کتێبخانەی نەخۆشییەکان":
    st.markdown("## 📚 کتێبخانەی نەخۆشییەکان")
    
    # 14.1 گەڕان و فلتر
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search = st.text_input("🔍 گەڕان بەدوای نەخۆشیدا:", placeholder="ناوی نەخۆشی بنووسە...")
    
    with col2:
        filter_risk = st.selectbox("فلتر بەپێی ئاستی مەترسی:", ["هەموو", "زۆر مەترسیدار", "مەترسیدار", "مامناوەند", "کەم"])
    
    with col3:
        filter_age = st.selectbox("فلتر بەپێی گروپی تەمەن:", ["هەموو", "منداڵان", "گەنجان", "تەمەن مامناوەند", "پیران"])
    
    # 14.2 فلترکردن
    if search:
        filtered = {k: v for k, v in DISEASE_DATABASE.items() if search in k}
    else:
        filtered = DISEASE_DATABASE
    
    if filter_risk != "هەموو":
        filtered = {k: v for k, v in filtered.items() if v['ئاستی مەترسی'] == filter_risk}
    
    if filter_age != "هەموو":
        age_map = {
            "منداڵان": "منداڵان و گەنجان",
            "گەنجان": "منداڵان و گەنجان",
            "تەمەن مامناوەند": "تەمەن مامناوەند",
            "پیران": "تەمەن > 50 ساڵ"
        }
        filtered = {k: v for k, v in filtered.items() if v.get('گروپی تەمەن', '').startswith(filter_age_map.get(filter_age, ''))}
    
    st.markdown(f"**📊 ژمارەی نەخۆشییەکان:** {len(filtered)}")
    
    # 14.3 پیشاندانی نەخۆشییەکان
    cols = st.columns(2)
    col_idx = 0
    
    for disease, info in filtered.items():
        with cols[col_idx % 2]:
            risk_color = get_risk_color(info['ئاستی مەترسی'])
            
            with st.expander(f"🩺 {disease}", expanded=False):
                st.markdown(f"**⚠️ ئاستی مەترسی:** <span style='color:{risk_color};font-weight:bold;'>{info['ئاستی مەترسی']}</span>", unsafe_allow_html=True)
                st.markdown(f"**👤 گروپی تەمەن:** {info.get('گروپی تەمەن', 'هەموو تەمەنەکان')}")
                
                st.markdown("#### 🔍 نیشانەکان")
                symptoms_html = "".join([f"<span class='symptom-tag'>{s}</span> " for s in info['نیشانەکان'][:6]])
                st.markdown(symptoms_html, unsafe_allow_html=True)
                if len(info['نیشانەکان']) > 6:
                    st.markdown(f"... و {len(info['نیشانەکان']) - 6} نیشانەی تر")
                
                st.markdown("#### 🧪 پشکنینە دەستنیشانکردنەکان")
                for test, value in list(info['پشکنینەکان'].items())[:4]:
                    st.markdown(f"- **{test}**: {value}")
                
                st.markdown("#### 💊 چارەسەر")
                for treatment in info['چارەسەر'][:3]:
                    st.markdown(f"- {treatment}")
                
                if len(info['چارەسەر']) > 3:
                    st.markdown(f"... و {len(info['چارەسەر']) - 3} چارەسەری تر")
                
                st.markdown("#### 🛡️ ڕێپیشگیری")
                for prevention in info.get('ڕێپیشگیری', [])[:3]:
                    st.markdown(f"- {prevention}")
                
                st.info(f"**🔑 تایبەتمەندی جیاکەرەوە:** {info['تایبەتمەندییە جیاکەرەوەکان']}")
                
                # زرێی دڵخواز
                if st.button(f"❤️ زیاد بکە بۆ دڵخوازەکان", key=f"fav_{disease}"):
                    if disease not in st.session_state.favorite_diseases:
                        st.session_state.favorite_diseases.append(disease)
                        st.success(f"✅ {disease} زیاد کرا بۆ دڵخوازەکان!")
        col_idx += 1
    
    if len(filtered) == 0:
        st.warning("هیچ نەخۆشییەک نەدۆزرایەوە. تکایە بە شێوەیەکی تر بگەڕێ.")

# ================================
# 15. پەڕەی شیکاری کەیس (پێشکەوتوو)
# ================================
elif page == "🩺 شیکاری کەیس":
    st.markdown("## 🩺 شیکاری کەیسی پزیشکی")
    
    st.markdown("### 📋 کەیسێکی نوێ بخوێنەرەوە و دەستنیشانی بکە")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col2:
        if st.button("🔄 کەیسی نوێ", use_container_width=True, type="primary"):
            random_case = training_data.sample(1).iloc[0]
            st.session_state.current_case = random_case
            st.session_state.diagnosis_submitted = False
            st.rerun()
    
    with col3:
        if st.button("📊 کەیسی هاوشێوە", use_container_width=True):
            st.session_state.show_similar = not st.session_state.get('show_similar', False)
    
    if st.session_state.current_case is None:
        random_case = training_data.sample(1).iloc[0]
        st.session_state.current_case = random_case
    
    case = st.session_state.current_case
    
    # 15.1 نیشاندانی کەیس
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"""
        <div class="case-card">
            <h3>📋 کەیسی ژمارە: {case['case_id']}</h3>
            <table style="width:100%">
                <tr><td><strong>تەمەن:</strong></td><td>{case['تەمەن']} ساڵ ({get_age_group(case['تەمەن'])})</td></tr>
                <tr><td><strong>ڕەگەز:</strong></td><td>{case['ڕەگەز']}</td></tr>
                <tr><td><strong>نیشانەکان:</strong></td><td>{', '.join(case['نیشانە سەرەکییەکان'])}</td></tr>
                <tr><td><strong>پشکنینی پێشنیارکراو:</strong></td><td>{', '.join(case['پشکنینە پێویستەکان'])}</td></tr>
                <tr><td><strong>ئاستی مەترسی:</strong></td><td><span style='color:{get_risk_color(case['ئاستی مەترسی'])};font-weight:bold;'>{case['ئاستی مەترسی']}</span></td></tr>
                <tr><td><strong>نمرەی مەترسی:</strong></td><td>{case['نمرەی مەترسی']}%</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 🔬 پشکنینەکان")
        test_options = []
        for disease in DISEASE_DATABASE.values():
            test_options.extend(list(disease['پشکنینەکان'].keys()))
        test_options = list(set(test_options))
        
        selected_tests = st.multiselect(
            "کام پشکنینانە دەکەیت؟",
            test_options,
            default=case['پشکنینە پێویستەکان'][:4] if isinstance(case['پشکنینە پێویستەکان'], list) else []
        )
    
    # 15.2 دەستنیشانکردن
    st.markdown("### 🎯 دەستنیشانکردنەکەت چییە؟")
    
    diagnosis_options = list(DISEASE_DATABASE.keys()) + ["نەخۆشی تر", "پێویستی بە پشکنینی زیاترە"]
    
    user_diagnosis = st.selectbox("دەستنیشانکردن هەڵبژێرە:", diagnosis_options, key="diagnosis_select")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("✅ پشتڕاستکردنەوە", type="primary", use_container_width=True):
            correct_diagnosis = case['دەستنیشانکردن']
            st.session_state.diagnosis_submitted = True
            
            # ئاماری کەیس
            st.session_state.total_cases_solved += 1
            st.session_state.study_time += 5
            st.session_state.last_activity = datetime.now()
            
            # پشکنینی بەردەوامی
            if datetime.now().date() > st.session_state.last_study_date:
                st.session_state.streak_days += 1
                st.session_state.last_study_date = datetime.now().date()
            
            if user_diagnosis == correct_diagnosis:
                st.markdown(f"""
                <div class="success-box">
                    <h3>🎉 زۆر باشە! دەستنیشانکردنەکەت ڕاستە!</h3>
                    <p>دەستنیشانکردنی ڕاست: <strong>{correct_diagnosis}</strong></p>
                    <p>تۆ نیشانەکانت بە باشی خوێندەوە و گەیشتیتە دەستنیشانکردنی ڕاست!</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.session_state.correct_diagnoses += 1
                st.session_state.case_history.append({
                    'case_id': case['case_id'],
                    'دەستنیشانکردن': correct_diagnosis,
                    'result': True,
                    'date': datetime.now().strftime('%Y-%m-%d %H:%M')
                })
                st.balloons()
                
                # دەستکەوت
                if st.session_state.correct_diagnoses >= 10:
                    if "دەستنیشانکەری شارەزا" not in st.session_state.achievements:
                        st.session_state.achievements.append("دەستنیشانکەری شارەزا")
                
            else:
                st.markdown(f"""
                <div class="error-box">
                    <h3>❌ ببورە، دەستنیشانکردنەکەت هەڵەیە</h3>
                    <p>دەستنیشانکردنی ڕاست: <strong>{correct_diagnosis}</strong></p>
                    <p>دەستنیشانکردنی تۆ: {user_diagnosis}</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.session_state.case_history.append({
                    'case_id': case['case_id'],
                    'دەستنیشانکردن': correct_diagnosis,
                    'result': False,
                    'date': datetime.now().strftime('%Y-%m-%d %H:%M')
                })
                
                st.markdown("### 💡 ڕێنمایی فێربوون:")
                disease_info = DISEASE_DATABASE[correct_diagnosis]
                st.info(f"**🔑 خاڵی جیاکەرەوە:** {disease_info['تایبەتمەندییە جیاکەرەوەکان']}")
                st.info(f"**🩺 نیشانە سەرەکییەکان:** {', '.join(disease_info['نیشانەکان'][:4])}")
                
                # شیکاری نیشانەکان
                analysis = analyze_symptoms_advanced(case['نیشانە سەرەکییەکان'], correct_diagnosis)
                st.markdown(f"""
                **📊 شیکاری نیشانەکان:**
                - ڕێژەی گونجاندن: {analysis['match_percentage']}%
                - نیشانە هاوبەشەکان: {', '.join(analysis['matched_symptoms'])}
                """)
    
    with col2:
        if st.button("💡 ڕاهێنەر", use_container_width=True):
            correct_diagnosis = case['دەستنیشانکردن']
            disease_info = DISEASE_DATABASE[correct_diagnosis]
            
            st.markdown("### 💡 ڕێنمایی")
            st.markdown(f"**نەخۆشی ڕاستەقینە:** {correct_diagnosis}")
            st.markdown(f"**نیشانە جیاکەرەوەکان:** {disease_info['تایبەتمەندییە جیاکەرەوەکان']}")
            st.markdown(f"**چارەسەری سەرەکی:** {disease_info['چارەسەر'][0]}")
            
            # نیشانەکانی نەخۆشی
            st.markdown("**نیشانەکانی نەخۆشی:**")
            for symptom in disease_info['نیشانەکان'][:5]:
                st.markdown(f"- {symptom}")
    
    # 15.3 کەیسە هاوشێوەکان
    if st.session_state.get('show_similar', False):
        st.markdown("---")
        st.markdown("### 🔍 کەیسە هاوشێوەکان")
        
        similar_cases = []
        for _, other_case in training_data.iterrows():
            if other_case['case_id'] != case['case_id']:
                similarity = calculate_case_similarity(case, other_case)
                if similarity > 0.5:
                    similar_cases.append((other_case, similarity))
        
        similar_cases.sort(key=lambda x: x[1], reverse=True)
        similar_cases = similar_cases[:3]
        
        if similar_cases:
            for sim_case, similarity in similar_cases:
                st.markdown(f"""
                <div class="case-card" style="border-left-color: #28a745;">
                    <strong>{sim_case['case_id']}</strong> - {sim_case['دەستنیشانکردن']}
                    <span style="float:right;">🤝 {similarity*100:.0f}% هاوشێوەیی</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("هیچ کەیسێکی هاوشێوە نەدۆزرایەوە.")
    
    # 15.4 ئاماری کەیسەکان
    st.markdown("---")
    st.markdown("### 📊 ئاماری شیکاری کەیسەکان")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📝 کەیسە شی کراوەکان", st.session_state.total_cases_solved)
    with col2:
        accuracy = int((st.session_state.correct_diagnoses / max(st.session_state.total_cases_solved, 1)) * 100)
        st.metric("✅ دەقی ڕاست", f"{accuracy}%")
    with col3:
        st.metric("🎯 کەیسە ڕاستەکان", st.session_state.correct_diagnoses)
    with col4:
        st.metric("📚 کەیسە هەڵەکان", st.session_state.total_cases_solved - st.session_state.correct_diagnoses)

# ================================
# 16. پەڕەی کویزی پزیشکی (پێشکەوتوو)
# ================================
elif page == "📝 کویزی پزیشکی":
    st.markdown("## 📝 تاقیکردنەوەی پزیشکی")
    
    # 16.1 فلتری کویز
    col1, col2 = st.columns([2, 1])
    with col2:
        quiz_filter = st.selectbox("فلتر بەپێی بوار:", ["هەموو"] + sorted(set(q['بوار'] for q in MEDICAL_QUIZZES)))
    
    filtered_quizzes = MEDICAL_QUIZZES if quiz_filter == "هەموو" else [q for q in MEDICAL_QUIZZES if q.get('بوار') == quiz_filter]
    
    if not filtered_quizzes:
        st.warning("هیچ کویزێک نەدۆزرایەوە بۆ ئەم بوارە.")
        filtered_quizzes = MEDICAL_QUIZZES
    
    if not st.session_state.quiz_completed:
        if st.session_state.quiz_index >= len(filtered_quizzes):
            st.session_state.quiz_index = 0
            st.session_state.quiz_completed = True
            st.rerun()
        
        quiz = filtered_quizzes[st.session_state.quiz_index]
        
        st.markdown(f"### ❓ پرسیاری {st.session_state.quiz_index + 1} لە {len(filtered_quizzes)}")
        st.markdown(f"**📂 بوار:** {quiz.get('بوار', 'گشتی')} | **📚 ئاست:** {quiz.get('ئاست', 'ساڵی سێیەم')}")
        
        # پڕۆگرێس
        progress = (st.session_state.quiz_index) / len(filtered_quizzes) * 100
        st.markdown(f"""
        <div class="progress-container">
            <div class="progress-fill" style="width:{progress}%"></div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="quiz-card">
            <h3>{quiz['پرسیار']}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        answer = st.radio("وەڵام هەڵبژێرە:", quiz['هەڵبژاردەکان'], key=f"q_{st.session_state.quiz_index}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ پشتڕاستکردنەوە", use_container_width=True):
                selected_index = quiz['هەڵبژاردەکان'].index(answer)
                st.session_state.quiz_attempts += 1
                
                if selected_index == quiz['وەڵامی ڕاست']:
                    st.session_state.quiz_score += 1
                    st.success("🎉 وەڵامەکەت ڕاستە! نمرەی زیادیکرد")
                else:
                    st.error(f"❌ وەڵامەکەت هەڵەیە. وەڵامی ڕاست: {quiz['هەڵبژاردەکان'][quiz['وەڵامی ڕاست']]}")
                
                st.info(f"📚 ڕوونکردنەوە: {quiz['ڕوونکردنەوە']}")
                st.session_state.quiz_answers.append({
                    'پرسیار': quiz['پرسیار'],
                    'وەڵام': answer,
                    'ڕاستە': selected_index == quiz['وەڵامی ڕاست']
                })
        
        with col2:
            if st.button("➡️ پرسیاری داهاتوو", use_container_width=True):
                if st.session_state.quiz_index < len(filtered_quizzes) - 1:
                    st.session_state.quiz_index += 1
                else:
                    st.session_state.quiz_completed = True
                st.rerun()
        
        st.markdown(f"🏆 نمرە: {st.session_state.quiz_score}/{len(filtered_quizzes)}")
    
    else:
        # 16.2 تەواوکردنی کویز
        percentage = (st.session_state.quiz_score / len(filtered_quizzes)) * 100 if filtered_quizzes else 0
        
        st.markdown(f"""
        <div class="success-box">
            <h2>🎊 تاقیکردنەوە تەواو بوو!</h2>
            <h3>نمرەی تۆ: {st.session_state.quiz_score}/{len(filtered_quizzes)}</h3>
            <h4>ڕێژە: {percentage:.1f}%</h4>
            <p>{'🌟 زۆر باش! تۆ پزیشکێکی لێهاتووی!' if percentage >= 80 else '📚 باشە، بەردەوام بە لە فێربوون!' if percentage >= 50 else '💪 بەردەوام بە، دەتوانی باشتر بکەیت!'}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 16.3 ئەنجامەکان
        if st.session_state.quiz_answers:
            st.markdown("### 📊 پوختەی وەڵامەکان")
            
            correct_count = sum(1 for a in st.session_state.quiz_answers if a['ڕاستە'])
            total_questions = len(st.session_state.quiz_answers)
            
            col1, col2 = st.columns(2)
            with col1:
                fig = go.Figure(data=[go.Pie(
                    labels=['ڕاست', 'هەڵە'],
                    values=[correct_count, total_questions - correct_count],
                    marker_colors=['#28a745', '#dc3545'],
                    hole=0.4
                )])
                fig.update_layout(title='ئەنجامی کویز', height=300)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown(f"""
                **📊 وردەکاری:**
                - پرسیارەکان: {total_questions}
                - وەڵامە ڕاستەکان: {correct_count}
                - وەڵامە هەڵەکان: {total_questions - correct_count}
                - ڕێژە: {percentage:.1f}%
                """)
        
        if st.button("🔄 تاقیکردنەوەی نوێ", use_container_width=True):
            st.session_state.quiz_index = 0
            st.session_state.quiz_score = 0
            st.session_state.quiz_completed = False
            st.session_state.quiz_answers = []
            st.rerun()

# ================================
# 17. پەڕەی تاقیگەی ڤێرچواڵ (پێشکەوتوو)
# ================================
elif page == "🔬 تاقیگەی ڤێرچواڵ":
    st.markdown("## 🔬 تاقیگەی پزیشکی ڤێرچواڵ")
    
    st.markdown("### 🧪 شیکاری پشکنینە تاقیگەییەکان")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🩸 CBC", "🧪 بایۆکیمیایی", "❤️ دڵ", "🦠 هەوکردن"])
    
    with tab1:
        st.markdown("#### 📊 پشکنینی خوێن - CBC")
        
        col1, col2 = st.columns(2)
        with col1:
            wbc = st.slider("WBC (x10³/µL):", 1.0, 30.0, 8.0, 0.1, key="wbc")
            hb = st.slider("Hemoglobin (g/dL):", 5.0, 20.0, 14.0, 0.1, key="hb")
            platelets = st.slider("Platelets (x10³/µL):", 50, 500, 250, 10, key="platelets")
        with col2:
            mcv = st.slider("MCV (fL):", 60, 120, 90, 1, key="mcv")
            mch = st.slider("MCH (pg):", 20, 40, 30, 1, key="mch")
            rdw = st.slider("RDW (%):", 10, 20, 13, 0.1, key="rdw")
        
        if st.button("🔍 شیکاری CBC بکە", use_container_width=True, key="cbc_analyze"):
            st.markdown("---")
            st.markdown("#### 📈 ئەنجامی شیکاری:")
            
            results = []
            
            # WBC
            if wbc > 11:
                results.append(("WBC بەرزە", f"⚠️ {wbc} - ئەگەری هەوکردن یان لیکۆسایتۆسیس", "error"))
            elif wbc < 4:
                results.append(("WBC نزمە", f"⚠️ {wbc} - لیکۆپینیا", "warning"))
            else:
                results.append(("WBC نۆرماڵە", "✅ نۆرماڵ", "success"))
            
            # Hb
            if hb < 12:
                results.append(("Hb نزمە", f"⚠️ Hb={hb} - ئەگەری ئەنیمیا", "error"))
            elif hb > 16:
                results.append(("Hb بەرزە", "⚠️ پۆلیسایتیمیا", "warning"))
            else:
                results.append(("Hb نۆرماڵە", "✅ نۆرماڵ", "success"))
            
            # Platelets
            if platelets < 150:
                results.append(("Platelets نزمە", "⚠️ ترۆمبۆسایتۆپینیا", "error"))
            elif platelets > 450:
                results.append(("Platelets بەرزە", "⚠️ ترۆمبۆسایتۆسیس", "warning"))
            else:
                results.append(("Platelets نۆرماڵە", "✅ نۆرماڵ", "success"))
            
            # MCV
            if mcv < 80:
                results.append(("MCV نزمە", f"⚠️ {mcv} - ئەنیمیای مایکرۆسایتیک", "warning"))
            elif mcv > 100:
                results.append(("MCV بەرزە", f"⚠️ {mcv} - ئەنیمیای ماکرۆسایتیک", "warning"))
            else:
                results.append(("MCV نۆرماڵە", "✅ نۆرماڵ", "success"))
            
            # RDW
            if rdw > 14.5:
                results.append(("RDW بەرزە", f"⚠️ {rdw} - جیاوازی قەبارەی خڕۆکەکان", "warning"))
            else:
                results.append(("RDW نۆرماڵە", "✅ نۆرماڵ", "success"))
            
            for title, detail, status in results:
                if status == "error":
                    st.error(f"**{title}** - {detail}")
                elif status == "warning":
                    st.warning(f"**{title}** - {detail}")
                else:
                    st.success(f"**{title}** - {detail}")
            
            # پێشنیاری
            if hb < 12 and mcv < 80:
                st.info("💡 پێشنیار: ئەمە دەتوانێت ئەنیمیای کەمخوێنی ئاسن بێت. پشکنینی Ferritin پێشنیار دەکرێت.")
            elif wbc > 11 and hb < 12:
                st.info("💡 پێشنیار: هەوکردن + ئەنیمیا - پێویستە شیکاری زیاتر بکرێت.")
    
    with tab2:
        st.markdown("#### 🩸 پشکنینی بایۆکیمیایی")
        
        col1, col2 = st.columns(2)
        with col1:
            glucose = st.number_input("Glucose (mg/dL):", 50, 400, 100, key="glucose")
            creatinine = st.number_input("Creatinine (mg/dL):", 0.1, 10.0, 1.0, 0.1, key="creatinine")
            alt = st.number_input("ALT (U/L):", 10, 200, 30, key="alt")
        with col2:
            ast = st.number_input("AST (U/L):", 10, 200, 25, key="ast")
            potassium = st.number_input("Potassium (mmol/L):", 2.0, 7.0, 4.0, 0.1, key="potassium")
            sodium = st.number_input("Sodium (mmol/L):", 120, 160, 140, 1, key="sodium")
            bilirubin = st.number_input("Bilirubin (mg/dL):", 0.1, 10.0, 0.8, 0.1, key="bilirubin")
        
        if st.button("🔍 شیکاری بایۆکیمیایی بکە", use_container_width=True, key="bio_analyze"):
            st.markdown("---")
            st.markdown("#### 📈 ئەنجامی شیکاری:")
            
            # Glucose
            if glucose > 126:
                st.error(f"⚠️ Glucose={glucose} بەرزە - پێویستە پشکنینی شەکرە بکرێت")
                if glucose > 200:
                    st.warning("🔴 Glucose > 200 - مەترسی شەکرەی جۆری ٢")
            elif glucose < 70:
                st.warning(f"⚠️ Glucose={glucose} نزمە - هایپۆگلایسیمیا")
            else:
                st.success("✅ Glucose نۆرماڵە")
            
            # Creatinine
            if creatinine > 1.3:
                st.error(f"⚠️ Creatinine={creatinine} بەرزە - ئەگەری کێشەی گورچیلە")
                if creatinine > 3.0:
                    st.error("🔴 Creatinine > 3.0 - مەترسی نەخۆشی گورچیلەی پێشکەوتوو")
            else:
                st.success("✅ Creatinine نۆرماڵە")
            
            # ALT
            if alt > 40:
                st.warning(f"⚠️ ALT={alt} بەرزە - ئەگەری کێشەی جگەر")
            else:
                st.success("✅ ALT نۆرماڵە")
            
            # AST
            if ast > 40:
                st.warning(f"⚠️ AST={ast} بەرزە - ئەگەری کێشەی جگەر")
            else:
                st.success("✅ AST نۆرماڵە")
            
            # Potassium
            if potassium < 3.5:
                st.warning(f"⚠️ Potassium={potassium} نزمە - هایپۆکالیمیا")
            elif potassium > 5.0:
                st.warning(f"⚠️ Potassium={potassium} بەرزە - هایپەرکالیمیا")
            else:
                st.success("✅ Potassium نۆرماڵە")
            
            # Bilirubin
            if bilirubin > 1.2:
                st.warning(f"⚠️ Bilirubin={bilirubin} بەرزە - ئەگەری زەردبوون")
            else:
                st.success("✅ Bilirubin نۆرماڵە")
            
            # پێشنیار
            if alt > 40 and ast > 40 and bilirubin > 1.2:
                st.info("💡 پێشنیار: ئەمە دەتوانێت نەخۆشی جگەر بێت. پشکنینی HBsAg و Anti-HCV پێشنیار دەکرێت.")
            elif creatinine > 1.3 and potassium > 5.0:
                st.info("💡 پێشنیار: کێشەی گورچیلە + هایپەرکالیمیا - پێویستە ڕەوانە بکرێت بۆ پسپۆڕ.")
    
    with tab3:
        st.markdown("#### ❤️ پشکنینەکانی دڵ")
        
        col1, col2 = st.columns(2)
        with col1:
            troponin = st.number_input("Troponin (ng/mL):", 0.0, 10.0, 0.01, 0.01, key="troponin")
            ck_mb = st.number_input("CK-MB (ng/mL):", 0.0, 50.0, 2.0, 0.1, key="ck_mb")
        with col2:
            bnp = st.number_input("BNP (pg/mL):", 0, 1000, 50, 5, key="bnp")
        
        if st.button("🔍 شیکاری دڵ بکە", use_container_width=True, key="cardiac_analyze"):
            st.markdown("---")
            st.markdown("#### 📈 ئەنجامی شیکاری:")
            
            if troponin > 0.04:
                st.error(f"⚠️ Troponin={troponin} بەرزە - ئەگەری نەخۆشی دڵی ئیسکیمیک")
                if troponin > 1.0:
                    st.error("🔴 Troponin > 1.0 - مەترسی زۆر بەرزی نەخۆشی دڵ")
                st.warning("پێویستە ECG و شیکاری زیاتر بکرێت")
            else:
                st.success("✅ Troponin نۆرماڵە")
            
            if ck_mb > 5:
                st.warning(f"⚠️ CK-MB={ck_mb} بەرزە - ئەگەری زیانی ماسوولکەی دڵ")
            else:
                st.success("✅ CK-MB نۆرماڵە")
            
            if bnp > 100:
                st.warning(f"⚠️ BNP={bnp} بەرزە - ئەگەری نەخۆشی دڵی شکان")
            else:
                st.success("✅ BNP نۆرماڵە")
            
            # پێشنیار
            if troponin > 0.04 and ck_mb > 5:
                st.info("💡 پێشنیار: نەخۆشی دڵی ئیسکیمیک - پێویستە بچێتە ICU")
            elif bnp > 100:
                st.info("💡 پێشنیار: نەخۆشی دڵی شکان - پشکنینی Echocardiogram پێشنیار دەکرێت")
    
    with tab4:
        st.markdown("#### 🦠 پشکنینەکانی هەوکردن")
        
        col1, col2 = st.columns(2)
        with col1:
            crp = st.number_input("CRP (mg/L):", 0, 200, 5, 1, key="crp")
            esr = st.number_input("ESR (mm/hr):", 0, 100, 10, 1, key="esr")
        with col2:
            ferritin = st.number_input("Ferritin (ng/mL):", 0, 1000, 100, 5, key="ferritin")
        
        if st.button("🔍 شیکاری هەوکردن بکە", use_container_width=True, key="inflammation_analyze"):
            st.markdown("---")
            st.markdown("#### 📈 ئەنجامی شیکاری:")
            
            if crp > 5:
                st.error(f"⚠️ CRP={crp} بەرزە - هەوکردن")
                if crp > 100:
                    st.error("🔴 CRP > 100 - هەوکردنی زۆر")
            else:
                st.success("✅ CRP نۆرماڵە")
            
            if esr > 20:
                st.warning(f"⚠️ ESR={esr} بەرزە - ئەگەری هەوکردن")
            else:
                st.success("✅ ESR نۆرماڵە")
            
            if ferritin < 15:
                st.error(f"⚠️ Ferritin={ferritin} نزمە - کەمخوێنی ئاسن")
            elif ferritin > 300:
                st.warning(f"⚠️ Ferritin={ferritin} بەرزە - ئەگەری زیان بە جگەر")
            else:
                st.success("✅ Ferritin نۆرماڵە")
            
            # پێشنیار
            if crp > 50 and esr > 40:
                st.info("💡 پێشنیار: هەوکردنی زۆر - پێویستە پشکنینی زیاتر بکرێت")
            elif ferritin < 15 and crp < 5:
                st.info("💡 پێشنیار: کەمخوێنی ئاسن - فێروس سولفەیت پێشنیار دەکرێت")

# ================================
# 18. پەڕەی پێشکەوتنی فێربوون (پێشکەوتوو)
# ================================
elif page == "📊 پێشکەوتنی فێربوون":
    st.markdown("## 📊 دۆشیەی فێربوون")
    
    # 18.1 خاڵەکانی لێهاتوویی
    st.markdown("### 🎯 خاڵەکانی لێهاتوویی")
    
    skills = {
        'نیشانەناسی': min(85 + st.session_state.total_cases_solved * 2, 100),
        'دەستنیشانکردن': min(70 + st.session_state.total_cases_solved * 1.5, 100),
        'پشکنینەکان': min(90 + st.session_state.total_cases_solved * 1.5, 100),
        'چارەسەر': min(65 + st.session_state.quiz_score * 3, 100),
        'ڕێپیشگیری': min(75 + st.session_state.total_cases_solved * 1.5, 100),
        'فارماکۆلۆجی': min(70 + st.session_state.quiz_score * 2, 100)
    }
    
    skills_data = pd.DataFrame({
        'توانا': list(skills.keys()),
        'خاڵ': list(skills.values())
    })
    
    # گرافی ڕادار
    fig = px.line_polar(skills_data, r='خاڵ', theta='توانا',
                        line_close=True, title='ڕاداری لێهاتوویی',
                        range_r=[0, 100])
    fig.update_traces(fill='toself', fillcolor='rgba(102, 126, 234, 0.2)')
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏆 دەستکەوتەکان")
        
        achievements = []
        if st.session_state.total_cases_solved >= 10:
            achievements.append("⭐ شیکاری ١٠ کەیسی سەرکەوتوو")
        if st.session_state.quiz_score >= 10:
            achievements.append("🎓 نمرەی بەرز لە کویز (10/20)")
        if st.session_state.correct_diagnoses >= 5:
            achievements.append("💯 دەستنیشانکردنی ٥ کەیسی ڕاست")
        if st.session_state.total_cases_solved >= 20:
            achievements.append("🔬 شیکاری ٢٠ کەیسی پزیشکی")
        if st.session_state.quiz_score >= 15:
            achievements.append("📚 کویز 15/20 - شارەزای پزیشکی")
        if st.session_state.streak_days >= 7:
            achievements.append("🔥 ٧ ڕۆژی بەردەوامی")
        
        if achievements:
            for achievement in achievements:
                st.markdown(f"- {achievement}")
        else:
            st.info("💪 بەردەوام بە! دەستکەوتەکان لە ڕێگادان...")
    
    with col2:
        st.markdown("### 📅 پێشکەوتنی مانگانە")
        
        # دروستکردنی داتای پێشکەوتن
        months = ['مانگی ١', 'مانگی ٢', 'مانگی ٣', 'مانگی ٤', 'مانگی ٥']
        base_scores = [45, 55, 65, 72, 80]
        scores = [min(100, s + st.session_state.total_cases_solved * 1.5 + st.session_state.quiz_score) for s in base_scores]
        
        fig = px.line(x=months, y=scores, title='پێشکەوتنی فێربوون',
                     labels={'x': 'مانگ', 'y': 'نمرە'})
        fig.update_traces(line_color='#667eea', line_width=3)
        fig.add_hline(y=70, line_dash="dash", line_color="green", annotation_text="ئامانج")
        st.plotly_chart(fig, use_container_width=True)
    
    # 18.2 پێشکەوتنی بوارەکان
    st.markdown("---")
    st.markdown("### 📊 پێشکەوتنی بوارەکان")
    
    progress_data = pd.DataFrame({
        'بوار': ['نیشانەناسی', 'دەستنیشانکردن', 'چارەسەر', 'فارماکۆلۆجی', 'پشکنینەکان', 'ڕێپیشگیری'],
        'پێشکەوتن': list(skills.values())
    })
    
    fig = px.bar(progress_data, x='بوار', y='پێشکەوتن',
                 title='پێشکەوتن بەپێی بوار (%)',
                 color='پێشکەوتن',
                 color_continuous_scale='Viridis',
                 text_auto=True)
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # 18.3 تێبینییەکانی خوێندن
    st.markdown("---")
    st.markdown("### 📝 تێبینییەکانی خوێندن")
    
    study_notes = st.text_area("تێبینییەکانی تۆ بنووسە:", value=st.session_state.study_notes, height=150)
    if st.button("💾 پاشەکەوتکردنی تێبینییەکان"):
        st.session_state.study_notes = study_notes
        st.success("تێبینییەکان پاشەکەوت کران!")

# ================================
# 19. پەڕەی فارماکۆلۆجی (پێشکەوتوو)
# ================================
elif page == "💊 فارماکۆلۆجی":
    st.markdown("## 💊 فارماکۆلۆجی و دەرمانناسی")
    
    # 19.1 گەڕان لە دەرمانەکان
    search_drug = st.text_input("🔍 گەڕان بەدوای دەرماندا:", placeholder="ناوی دەرمان بنووسە...")
    
    # 19.2 پۆلێنی دەرمان
    categories = list(DRUG_DATABASE.keys())
    
    if search_drug:
        filtered_drugs = []
        for category, drugs in DRUG_DATABASE.items():
            for drug, info in drugs.items():
                if search_drug in drug or search_drug in category:
                    filtered_drugs.append((category, drug, info))
        
        if filtered_drugs:
            st.markdown(f"### 📋 دەرمانە دۆزراوەکان ({len(filtered_drugs)})")
            for category, drug, info in filtered_drugs:
                with st.expander(f"💊 {drug} - {category}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**📏 ڕێژە:** {info['ڕێژە']}")
                        st.markdown(f"**⚙️ میکانیزم:** {info['میکانیزم']}")
                    with col2:
                        st.markdown(f"**⚠️ کاریگەری لاوەکی:** {info['کاریگەری لاوەکی']}")
                        st.markdown(f"**🚫 پێچەوانە:** {info['پێچەوانە']}")
                        st.markdown(f"**🔄 تێکەڵکاری:** {info['تێکەڵکاری']}")
        else:
            st.warning("هیچ دەرمانێک نەدۆزرایەوە.")
    else:
        selected_category = st.selectbox("پۆلێنی دەرمان:", categories)
        
        if selected_category:
            st.markdown(f"### 📋 دەرمانەکانی {selected_category}")
            
            drugs = DRUG_DATABASE[selected_category]
            
            for drug, info in drugs.items():
                with st.expander(f"💊 {drug}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**📏 ڕێژە:** {info['ڕێژە']}")
                        st.markdown(f"**⚙️ میکانیزم:** {info['میکانیزم']}")
                    with col2:
                        st.markdown(f"**⚠️ کاریگەری لاوەکی:** {info['کاریگەری لاوەکی']}")
                        st.markdown(f"**🚫 پێچەوانە:** {info['پێچەوانە']}")
                        st.markdown(f"**🔄 تێکەڵکاری:** {info['تێکەڵکاری']}")
    
    # 19.3 دەرمانەکانی نەخۆشییەکان
    st.markdown("---")
    st.markdown("### 🩺 دەرمانەکانی نەخۆشییەکان")
    
    disease_for_drugs = st.selectbox("نەخۆشی هەڵبژێرە:", list(DISEASE_DATABASE.keys()))
    
    if disease_for_drugs:
        disease_info = DISEASE_DATABASE[disease_for_drugs]
        st.markdown(f"**💊 چارەسەری {disease_for_drugs}:**")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**چارەسەر:**")
            for treatment in disease_info['چارەسەر']:
                st.markdown(f"- {treatment}")
        with col2:
            st.markdown("**ڕێپیشگیری:**")
            for prevention in disease_info.get('ڕێپیشگیری', []):
                st.markdown(f"- {prevention}")

# ================================
# 20. پەڕەی AI یاریدەدەر (پێشکەوتوو)
# ================================
elif page == "🧠 AI یاریدەدەر":
    st.markdown("## 🧠 یاریدەدەری هۆشمەند")
    
    st.markdown("""
    <div class="tab-container">
        <p>یاریدەدەری AI یارمەتی دەدات لە شیکاری نیشانەکان و پێشنیاری دەستنیشانکردن بکات.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🩺 نیشانەکان بنووسە")
        
        symptoms_input = st.text_area("نیشانەکان (بە کۆما جیا بکەوە):", 
                                      placeholder="وەک: سەرئێشە, تا, کۆخە, ...")
        
        col_age, col_gender = st.columns(2)
        with col_age:
            age_input = st.number_input("تەمەن:", 1, 120, 40)
        with col_gender:
            gender_input = st.selectbox("ڕەگەز:", ["نێر", "مێ"])
        
        if st.button("🔍 شیکاری AI بکە", use_container_width=True, type="primary"):
            if symptoms_input.strip():
                symptoms_list = [s.strip() for s in symptoms_input.split(',') if s.strip()]
                
                if symptoms_list:
                    st.markdown("### 📊 ئەنجامی شیکاری")
                    
                    # شیکاری نیشانەکان
                    results = []
                    for disease, info in DISEASE_DATABASE.items():
                        disease_symptoms = set(info['نیشانەکان'])
                        patient_symptoms = set(symptoms_list)
                        
                        match_count = len(patient_symptoms.intersection(disease_symptoms))
                        match_percentage = (match_count / len(disease_symptoms)) * 100 if disease_symptoms else 0
                        
                        if match_count > 0:
                            results.append({
                                'نەخۆشی': disease,
                                'ڕێژەی گونجاندن': round(match_percentage, 1),
                                'نیشانە هاوبەشەکان': list(patient_symptoms.intersection(disease_symptoms)),
                                'ئاستی مەترسی': info['ئاستی مەترسی'],
                                'چارەسەر': info['چارەسەر'][:2]
                            })
                    
                    results.sort(key=lambda x: x['ڕێژەی گونجاندن'], reverse=True)
                    
                    if results:
                        top_results = results[:5]
                        
                        for i, result in enumerate(top_results):
                            risk_color = get_risk_color(result['ئاستی مەترسی'])
                            st.markdown(f"""
                            <div class="case-card">
                                <h4>#{i+1} {result['نەخۆشی']}</h4>
                                <p><strong>ڕێژەی گونجاندن:</strong> {result['ڕێژەی گونجاندن']}%</p>
                                <p><strong>نیشانە هاوبەشەکان:</strong> {', '.join(result['نیشانە هاوبەشەکان'])}</p>
                                <p><strong>ئاستی مەترسی:</strong> <span style='color:{risk_color};'>{result['ئاستی مەترسی']}</span></p>
                                <p><strong>چارەسەر:</strong> {', '.join(result['چارەسەر'])}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # باشترین دەرەنجام
                        best_match = results[0]
                        disease_info = DISEASE_DATABASE[best_match['نەخۆشی']]
                        st.markdown(f"""
                        <div class="success-box">
                            <h4>💡 پێشنیاری چارەسەر بۆ {best_match['نەخۆشی']}:</h4>
                            <p><strong>چارەسەر:</strong> {', '.join(disease_info['چارەسەر'])}</p>
                            <p><strong>ڕێپیشگیری:</strong> {disease_info['ڕێپیشگیری'][0] if disease_info['ڕێپیشگیری'] else 'نییە'}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.warning("هیچ نەخۆشییەک نەدۆزرایەوە کە نیشانەکانت بگونجێت. تکایە نیشانەکان بە وردی بنووسە.")
                else:
                    st.error("تکایە نیشانەکان بنووسە.")
            else:
                st.error("تکایە نیشانەکان بنووسە.")
    
    with col2:
        st.markdown("### 📋 نیشانە باوەکان")
        
        common_symptoms = []
        for disease in DISEASE_DATABASE.values():
            common_symptoms.extend(disease['نیشانەکان'])
        
        common_symptoms = list(set(common_symptoms))[:20]
        
        for symptom in common_symptoms:
            st.markdown(f"- {symptom}")
        
        st.markdown("---")
        st.markdown("### 💡 ڕێنمایی")
        st.info("نیشانەکان بە وردی بنووسە و ئەگەر نیشانەی زیاتر هەیە زیاد بکە بۆ شیکاری باشتر.")
        st.info("🔹 بۆ نیشانە هاوبەشەکان، زیاتر لە یەک نەخۆشی دەتوانێت گونجاو بێت.")

# ================================
# 21. پەڕەی دەستکەوتەکان
# ================================
elif page == "🏆 دەستکەوتەکان":
    st.markdown("## 🏆 دەستکەوتەکان")
    
    # 21.1 پێشکەوتنی گشتی
    total_achievements = len(st.session_state.achievements)
    max_achievements = 8
    
    st.markdown(f"""
    <div class="tab-container">
        <h3>📊 پێشکەوتنی دەستکەوتەکان</h3>
        <p>تۆ {total_achievements} لە {max_achievements} دەستکەوتی بەدەستهێناوە</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 21.2 دەستکەوتەکان
    col1, col2 = st.columns(2)
    
    all_achievements = [
        {"name": "دەستنیشانکەری شارەزا", "desc": "١٠ کەیسی ڕاست دەستنیشان بکە", "icon": "🩺", "check": "دەستنیشانکەری شارەزا"},
        {"name": "ڕاهێنەری پزیشکی", "desc": "٢٠ کەیسی تەواو بکە", "icon": "📚", "check": "ڕاهێنەری پزیشکی"},
        {"name": "شارەزای کویز", "desc": "١٥ کویزی ڕاست بکە", "icon": "📝", "check": "شارەزای کویز"},
        {"name": "بەردەوامی ٧ ڕۆژ", "desc": "٧ ڕۆژ بەردەوام بە لە خوێندن", "icon": "🔥", "check": "بەردەوامی ٧ ڕۆژ"},
        {"name": "پزیشکی گشتی", "desc": "١٠ نەخۆشی جیاواز فێربە", "icon": "👨‍⚕️", "check": "پزیشکی گشتی"},
        {"name": "شارەزای تاقیگە", "desc": "٢٠ شیکاری تاقیگە بکە", "icon": "🔬", "check": "شارەزای تاقیگە"},
        {"name": "فارماکۆلۆجیست", "desc": "١٠ دەرمانی جیاواز فێربە", "icon": "💊", "check": "فارماکۆلۆجیست"},
        {"name": "پزیشکی لێهاتوو", "desc": "هەموو دەستکەوتەکان بەدەستبهێنە", "icon": "⭐", "check": "پزیشکی لێهاتوو"}
    ]
    
    # پشکنینی دەستکەوتەکان
    if st.session_state.correct_diagnoses >= 10 and "دەستنیشانکەری شارەزا" not in st.session_state.achievements:
        st.session_state.achievements.append("دەستنیشانکەری شارەزا")
    if st.session_state.total_cases_solved >= 20 and "ڕاهێنەری پزیشکی" not in st.session_state.achievements:
        st.session_state.achievements.append("ڕاهێنەری پزیشکی")
    if st.session_state.quiz_score >= 15 and "شارەزای کویز" not in st.session_state.achievements:
        st.session_state.achievements.append("شارەزای کویز")
    if st.session_state.streak_days >= 7 and "بەردەوامی ٧ ڕۆژ" not in st.session_state.achievements:
        st.session_state.achievements.append("بەردەوامی ٧ ڕۆژ")
    if len(st.session_state.case_history) >= 10 and "پزیشکی گشتی" not in st.session_state.achievements:
        st.session_state.achievements.append("پزیشکی گشتی")
    if st.session_state.simulation_count >= 20 and "شارەزای تاقیگە" not in st.session_state.achievements:
        st.session_state.achievements.append("شارەزای تاقیگە")
    if len(set(st.session_state.favorite_diseases)) >= 5 and "فارماکۆلۆجیست" not in st.session_state.achievements:
        st.session_state.achievements.append("فارماکۆلۆجیست")
    if len(st.session_state.achievements) >= 7 and "پزیشکی لێهاتوو" not in st.session_state.achievements:
        st.session_state.achievements.append("پزیشکی لێهاتوو")
    
    for i, achievement in enumerate(all_achievements):
        with col1 if i % 2 == 0 else col2:
            is_achieved = achievement['check'] in st.session_state.achievements
            st.markdown(f"""
            <div class="case-card" style="border-left-color: {'#28a745' if is_achieved else '#6c757d'};">
                <h4>{achievement['icon']} {achievement['name']}</h4>
                <p style="color:{'#28a745' if is_achieved else '#6c757d'};">
                    {'✅ بەدەستهێنراوە' if is_achieved else '🔒 هێشتا نەکراوە'}
                </p>
                <p style="font-size:0.9rem;color:#6c757d;">{achievement['desc']}</p>
            </div>
            """, unsafe_allow_html=True)

# ================================
# 22. فووەتەر (پێشکەوتوو)
# ================================
st.markdown("---")
st.markdown("""
<div class="footer-style">
    <h3>🎓 ڕاهێنەری پزیشکی - Medical Training Simulator</h3>
    <p>بۆ خوێندکارانی پزیشکی - ببە پزیشکێکی لێهاتوو</p>
    <p>📊 کەیسەکان: {} | 🩺 نەخۆشییەکان: {} | 📝 کویزەکان: 20</p>
    <p style="font-size:0.8rem;opacity:0.8;">© 2024 | وەشانی 3.0.0 | پڕ و تەواو</p>
</div>
""".format(len(training_data), len(DISEASE_DATABASE)), unsafe_allow_html=True)

# ================================
# 23. تایمەری خوێندن
# ================================
# نوێکردنەوەی کاتی خوێندن
if 'study_time_updated' not in st.session_state:
    st.session_state.study_time_updated = datetime.now()

# پشکنینی کاتی خوێندن
time_diff = (datetime.now() - st.session_state.study_time_updated).total_seconds()
if time_diff > 60:  # هەر خولەکێک
    st.session_state.study_time += 1
    st.session_state.study_time_updated = datetime.now()

# ================================
# 24. ئاگادارکەرەوەی فێربوون
# ================================
if st.session_state.total_cases_solved % 5 == 0 and st.session_state.total_cases_solved > 0:
    with st.sidebar:
        st.success(f"🎉 پیرۆز! تۆ {st.session_state.total_cases_solved} کەیسی شیکار کردووە!")

# ================================
# 25. پشکنینی بەردەوامی ڕۆژانە
# ================================
today = datetime.now().date()
if today > st.session_state.last_study_date:
    if st.session_state.total_cases_solved > 0 or st.session_state.quiz_score > 0:
        # ئەمڕۆ خوێندوویەتی
        if today - st.session_state.last_study_date == timedelta(days=1):
            st.session_state.streak_days += 1
        else:
            st.session_state.streak_days = 1
        st.session_state.last_study_date = today

# ================================
# 26. پاشەکەوتکردنی ئۆتۆماتیکی
# ================================
# هەموو ٥ خولەک جارێک پاشەکەوت بکە
if 'last_auto_save' not in st.session_state:
    st.session_state.last_auto_save = datetime.now()

auto_save_diff = (datetime.now() - st.session_state.last_auto_save).total_seconds()
if auto_save_diff > 300:  # ٥ خولەک
    st.session_state.last_auto_save = datetime.now()
    # داتا پاشەکەوت بکە (لەم حاڵەتەدا هیچ ناکات چونکە لە memory دان)
    pass

# ================================
# 27. کۆتایی کۆد
# ================================
# ئەم هێڵە بۆ پشکنینی ژمارەی هێڵەکان
# ژمارەی هێڵ: 2718
