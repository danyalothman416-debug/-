import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import warnings
warnings.filterwarnings('ignore')
import json
import time
import hashlib
import re
from typing import Dict, List, Tuple, Optional

# ================================
# ڕێکخستنی ڕووکاری پەڕە
# ================================
st.set_page_config(
    page_title="ڕاهێنەری پزیشکی - Medical Training Simulator",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================================
# CSS و ستایلەکان
# ================================
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        text-align: center;
        padding: 1.8rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        animation: fadeIn 1s ease-in;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .case-card {
        background: linear-gradient(145deg, #f0f4ff, #e8edff);
        padding: 1.8rem;
        border-radius: 18px;
        border-left: 6px solid #667eea;
        margin: 1rem 0;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    }
    .case-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);
    }
    .success-box {
        background: linear-gradient(135deg, #d4edda, #b8e0c8);
        padding: 1.8rem;
        border-radius: 15px;
        border-left: 6px solid #28a745;
        box-shadow: 0 4px 15px rgba(40, 167, 69, 0.2);
    }
    .error-box {
        background: linear-gradient(135deg, #f8d7da, #f5c6cb);
        padding: 1.8rem;
        border-radius: 15px;
        border-left: 6px solid #dc3545;
        box-shadow: 0 4px 15px rgba(220, 53, 69, 0.2);
    }
    .quiz-card {
        background: linear-gradient(135deg, #ffffff, #f8f9ff);
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
        margin: 1.5rem 0;
        border: 1px solid rgba(102, 126, 234, 0.1);
    }
    .progress-container {
        background: #e9ecef;
        border-radius: 12px;
        height: 14px;
        overflow: hidden;
        margin: 0.8rem 0;
    }
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #667eea, #764ba2);
        border-radius: 12px;
        transition: width 0.8s ease;
    }
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        text-align: center;
        border-top: 4px solid #667eea;
        transition: transform 0.3s ease;
    }
    .stat-card:hover {
        transform: scale(1.03);
    }
    .badge-level {
        display: inline-block;
        padding: 0.3rem 1.2rem;
        border-radius: 20px;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
    }
    .footer-style {
        text-align: center;
        padding: 2.5rem;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border-radius: 20px;
        margin-top: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    .tab-container {
        background: white;
        padding: 2rem;
        border-radius: 18px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        margin: 1rem 0;
    }
    .button-primary {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        padding: 0.8rem 2rem;
        border-radius: 12px;
        font-weight: bold;
        cursor: pointer;
        transition: transform 0.2s;
    }
    .button-primary:hover {
        transform: scale(1.05);
    }
    .medication-card {
        background: #f8f9ff;
        padding: 1.2rem;
        border-radius: 12px;
        border: 1px solid #e8edff;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ================================
# داتابەیسی پڕ و تەواوی نەخۆشییەکان
# ================================
DISEASE_DATABASE = {
    "شەکرەی جۆری 2": {
        "نیشانەکان": ["تینوویەتی زۆر", "میزی زۆر", "ماندوویی", "کێش کەمبوونەوە", "بینی تەڵخ", "برسێتی زۆر", "پێست وشک"],
        "پشکنینەکان": {
            "FBS": ">126 mg/dL",
            "HbA1c": ">6.5%",
            "OGTT": ">200 mg/dL",
            "C-peptide": "نۆرماڵ یان بەرز"
        },
        "چارەسەر": ["مێتفۆرمین 500mg", "گۆڕینی شێوازی ژیان", "وەرزشی ڕۆژانە 30 خولەک", "شێوازی خواردن کەم کاربۆهیدرات"],
        "ئاستی مەترسی": "مەترسیدار",
        "تایبەتمەندییە جیاکەرەوەکان": "FBS بەرز + HbA1c بەرز + تەمەن > 40 ساڵ",
        "ڕێپیشگیری": ["شێوازی خواردنی تەندروست", "چالاکی جەستەیی", "پێوانەکردنی شەکر بەردەوام"]
    },
    "پەستانی خوێنی سەرەتایی": {
        "نیشانەکان": ["سەرئێشە", "سەرگێژخواردن", "فشاری پشت چاو", "خێرالێدانی دڵ", "ئەرەقەکردن", "مەلە"],
        "پشکنینەکان": {
            "BP": ">140/90 mmHg",
            "ECG": "Left ventricular hypertrophy",
            "Creatinine": "نۆرماڵ",
            "Potassium": "نۆرماڵ"
        },
        "چارەسەر": ["کاپتۆپریل 25mg", "کەمکردنەوەی نمەک", "وەرزشی ئیروبیک", "کەمکردنەوەی کێش"],
        "ئاستی مەترسی": "مامناوەند",
        "تایبەتمەندییە جیاکەرەوەکان": "BP بەرز بەبێ هۆکاری دیکە",
        "ڕێپیشگیری": ["پێوانەکردنی BP بەردەوام", "شێوازی خواردنی کەم نمەک", "ڕاهێنانی ڕۆژانە"]
    },
    "نەخۆشی دڵی ئیسکیمیک": {
        "نیشانەکان": ["ئازاری سنگ", "کورتی هەناسە", "ئارەقەکردن", "سکچوون و ڕشانەوە", "ئازاری شان", "تنگەنەفەسی"],
        "پشکنینەکان": {
            "ECG": "ST depression",
            "Troponin": "بەرز",
            "CK-MB": "بەرز",
            "Echocardiogram": "کەمبوونی ئیشی دڵ"
        },
        "چارەسەر": ["ئەسپیرین 300mg", "نایترۆگلیسیرین", "ئۆکسجین", "بێتا بلاکەر"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندییە جیاکەرەوەکان": "ST changes + Troponin elevated",
        "ڕێپیشگیری": ["کۆنتڕۆڵی پەستانی خوێن", "وەرزش", "وەستانی جگەرە"]
    },
    "هەوکردنی سییەکان": {
        "نیشانەکان": ["تا", "کۆخە", "هەناسەدان بە زەحمەت", "ئازاری سنگ", "ڕژانی لووت", "ماندوویی"],
        "پشکنینەکان": {
            "Chest X-ray": "Consolidation",
            "CRP": "بەرز",
            "WBC": "بەرز",
            "Sputum culture": "بەکتریا"
        },
        "چارەسەر": ["ئەنتیبایۆتیک (Amoxicillin)", "ئۆکسجین", "شلەمەنی", "دەرمانی دژە تا"],
        "ئاستی مەترسی": "مامناوەند",
        "تایبەتمەندییە جیاکەرەوەکان": "Consolidation لە X-ray + CRP بەرز",
        "ڕێپیشگیری": ["کوتان (Vaccination)", "دەستشۆردن", "دوورکەوتنەوە لە کەسانی تووشبوو"]
    },
    "ئەنیمیا": {
        "نیشانەکان": ["ماندوویی", "ڕەنگی پێست زەرد", "سەرگێژخواردن", "لێدانی دڵ خێرا", "سەرئێشە", "پڕۆشتن"],
        "پشکنینەکان": {
            "Hb": "<12 g/dL",
            "MCV": "<80 fL (microcytic)",
            "Ferritin": "نزم",
            "TIBC": "بەرز"
        },
        "چارەسەر": ["سوپلیمێنتی ئاسن (Ferrous sulfate)", "گۆڕینی خواردن", "دۆزینەوەی هۆکاری سەرەکی", "ڤیتامین C"],
        "ئاستی مەترسی": "مامناوەند",
        "تایبەتمەندییە جیاکەرەوەکان": "Hb نزم + MCV نزم + Ferritin نزم",
        "ڕێپیشگیری": ["خواردنی ئاسن", "خواردنی ڤیتامین C", "پشکنینی خوێنی بەردەوام"]
    },
    "نەخۆشی گورچیلە": {
        "نیشانەکان": ["ئاوسانی ڕوو و قاچ", "میزی کەم", "ماندوویی", "سەرئێشە", "خوێن لە میزدا", "فشاری خوێن بەرز"],
        "پشکنینەکان": {
            "Creatinine": "بەرز",
            "BUN": "بەرز",
            "eGFR": "<60",
            "Urinalysis": "پڕۆتین + خوێن"
        },
        "چارەسەر": ["ACE inhibitor", "کەمکردنەوەی پڕۆتین", "کۆنتڕۆڵی BP", "دایەلیز"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندییە جیاکەرەوەکان": "Creatinine بەرز + eGFR نزم",
        "ڕێپیشگیری": ["کۆنتڕۆڵی شەکرە", "کۆنتڕۆڵی BP", "کەمکردنەوەی نمەک"]
    }
}

# ================================
# کویزەکانی پزیشکی (١٠ کویز)
# ================================
MEDICAL_QUIZZES = [
    {
        "پرسیار": "نەخۆشێکی ٤٥ ساڵان، سەرئێشە و سەرگێژخواردنی هەیە، BP=١٦٠/٩٥. باشترین هەنگاوی داهاتوو چییە؟",
        "هەڵبژاردەکان": [
            "دەستبەجێ دەرمانی دژە پەستانی خوێن",
            "پێوانەکردنی BP دوای ٢ هەفتە و گۆڕینی شێوازی ژیان",
            "CT سەر",
            "پشکنینی خوێنی تەواو"
        ],
        "وەڵامی ڕاست": 1,
        "ڕوونکردنەوە": "بەپێی ڕێنماییەکان، بۆ پەستانی خوێنی قۆناغی ١، دەبێت دووبارە BP پێوانە بکرێت و گۆڕانی شێوازی ژیان پێشنیار بکرێت"
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
        "ڕوونکردنەوە": "FBS>١٢٦ و HbA1c>٦.٥% دوو پێوەری سەرەکی بۆ دەستنیشانکردنی شەکرەن"
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
        "ڕوونکردنەوە": "MCV<٨٠ fL ئاماژەیە بۆ ئەنیمیای مایکرۆسایتیک (Microcytic Anemia)"
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
        "ڕوونکردنەوە": "Troponin بەرز ئاماژەیە بۆ نەخۆشی دڵی ئیسکیمیک، پێویستە ECG و پشکنینی زیاتر بکرێت"
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
        "ڕوونکردنەوە": "Consolidation لە X-ray ئاماژەیە بۆ هەوکردنی سییەکان"
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
        "ڕوونکردنەوە": "ڕێژەی دەستپێکی مێتفۆرمین ٥٠٠mg دووجارە لەگەڵ خواردن"
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
        "ڕوونکردنەوە": "Creatinine بەرز ئاماژەیە بۆ نەخۆشی گورچیلە، پێویستە ڕەوانە بکرێت بۆ پسپۆڕی گورچیلە"
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
        "ڕوونکردنەوە": "Hb نزم + Ferritin نزم ئاماژەیە بۆ ئەنیمیای کەمخوێنی ئاسن"
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
        "ڕوونکردنەوە": "مێتفۆرمین کار لە جگەر دەکات بۆ کەمکردنەوەی بەرهەمهێنانی گلوکۆز"
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
        "ڕوونکردنەوە": "بۆ BP قۆناغی ١، گۆڕینی شێوازی ژیان و کەمکردنەوەی کێش پێشنیار دەکرێت"
    }
]

# ================================
# داتای تاقیگەی ڤێرچواڵ
# ================================
LAB_DATA = {
    "CBC": {
        "WBC": {"نۆرماڵ": (4.0, 11.0), "یەکە": "x10³/µL"},
        "Hb": {"نۆرماڵ": (12.0, 16.0), "یەکە": "g/dL"},
        "Platelets": {"نۆرماڵ": (150, 450), "یەکە": "x10³/µL"},
        "MCV": {"نۆرماڵ": (80, 100), "یەکە": "fL"},
        "MCH": {"نۆرماڵ": (27, 33), "یەکە": "pg"}
    },
    "بایۆکیمیایی": {
        "Glucose": {"نۆرماڵ": (70, 126), "یەکە": "mg/dL"},
        "Creatinine": {"نۆرماڵ": (0.6, 1.3), "یەکە": "mg/dL"},
        "ALT": {"نۆرماڵ": (10, 40), "یەکە": "U/L"},
        "AST": {"نۆرماڵ": (10, 40), "یەکە": "U/L"},
        "Potassium": {"نۆرماڵ": (3.5, 5.0), "یەکە": "mmol/L"},
        "Sodium": {"نۆرماڵ": (135, 145), "یەکە": "mmol/L"}
    },
    "دڵ": {
        "Troponin": {"نۆرماڵ": (0, 0.04), "یەکە": "ng/mL"},
        "CK-MB": {"نۆرماڵ": (0, 5), "یەکە": "ng/mL"}
    }
}

# ================================
# فانکشنە یارمەتیدەرەکان
# ================================

def generate_case_id() -> str:
    """دروستکردنی ناسنامەی بێهاوتا بۆ کەیس"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_num = random.randint(1000, 9999)
    return f"CASE-{timestamp}-{random_num}"

def calculate_risk_score(disease: str, age: int, gender: str) -> int:
    """حسابکردنی نمرەی مەترسی بۆ نەخۆشی"""
    base_risk = {
        "زۆر مەترسیدار": 80,
        "مەترسیدار": 60,
        "مامناوەند": 40,
        "کەم": 20
    }
    risk = base_risk.get(DISEASE_DATABASE[disease]['ئاستی مەترسی'], 40)
    
    # زیادکردنی مەترسی بەپێی تەمەن
    if age > 60:
        risk += 15
    elif age > 50:
        risk += 10
    elif age > 40:
        risk += 5
    
    return min(risk, 100)

def analyze_symptoms(symptoms: List[str], disease: str) -> Dict:
    """شیکاری نیشانەکان بۆ نەخۆشی"""
    disease_symptoms = set(DISEASE_DATABASE[disease]['نیشانەکان'])
    patient_symptoms = set(symptoms)
    
    match_count = len(patient_symptoms.intersection(disease_symptoms))
    total_disease_symptoms = len(disease_symptoms)
    
    percentage = (match_count / total_disease_symptoms) * 100 if total_disease_symptoms > 0 else 0
    
    return {
        "match_count": match_count,
        "total_symptoms": total_disease_symptoms,
        "percentage": percentage,
        "match_quality": "باش" if percentage > 60 else "مامناوەند" if percentage > 30 else "کەم"
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

# ================================
# دروستکردنی داتای ڕاهێنان (زیاتر)
# ================================
@st.cache_data
def generate_training_cases():
    cases = []
    case_id_counter = 1
    
    for disease, info in DISEASE_DATABASE.items():
        # ٨ کەیس بۆ هەر نەخۆشییەک
        for i in range(8):
            age = random.randint(18, 80)
            gender = random.choice(['نێر', 'مێ'])
            symptoms = random.sample(info['نیشانەکان'], min(4, len(info['نیشانەکان'])))
            
            # دروستکردنی پشکنینەکان بە شێوەیەکی ڕاستەقینە
            test_keys = list(info['پشکنینەکان'].keys())
            selected_tests = random.sample(test_keys, min(3, len(test_keys)))
            
            case = {
                'case_id': f"CASE-{case_id_counter:04d}",
                'تەمەن': age,
                'ڕەگەز': gender,
                'نیشانە سەرەکییەکان': symptoms,
                'پشکنینە پێویستەکان': selected_tests,
                'دەستنیشانکردن': disease,
                'ئاستی مەترسی': info['ئاستی مەترسی'],
                'نمرەی مەترسی': calculate_risk_score(disease, age, gender),
                'case_date': datetime.now() - timedelta(days=random.randint(0, 365))
            }
            cases.append(case)
            case_id_counter += 1
    
    return pd.DataFrame(cases)

training_data = generate_training_cases()

# ================================
# مۆدێلی AI بۆ پێشبینی
# ================================
@st.cache_resource
def train_prediction_model():
    """ڕاهێنانی مۆدێلی پێشبینی نەخۆشی"""
    try:
        # داتا ئامادەکردن
        data = training_data.copy()
        data['تەمەن_پلە'] = pd.cut(data['تەمەن'], bins=[0, 30, 50, 70, 100], labels=['جوان', 'نێوەند', 'پیر', 'زۆر پیر'])
        
        # داتای تایبەتمەندی
        features = pd.get_dummies(data[['تەمەن', 'ڕەگەز'] + ['نیشانە سەرەکییەکان']], drop_first=True)
        
        # هەر نەخۆشییەک بە تایبەتمەندی خۆی
        X = features
        y = data['دەستنیشانکردن']
        
        # دابەشکردنی داتا
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # ستانداردکردن
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train.select_dtypes(include=[np.number]))
        X_test_scaled = scaler.transform(X_test.select_dtypes(include=[np.number]))
        
        # ڕاهێنانی مۆدێل
        model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
        model.fit(X_train_scaled, y_train)
        
        # هەڵسەنگاندن
        y_pred = model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        return model, scaler, accuracy, X_train.columns.tolist()
    except Exception as e:
        return None, None, 0, []

model, scaler, model_accuracy, feature_columns = train_prediction_model()

# ================================
# ستەیتەکانی ئەپ
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

# ================================
# سایدبار
# ================================
with st.sidebar:
    # لۆگۆ و ناو
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image("https://img.icons8.com/color/96/000000/medical-doctor.png", width=70)
    with col2:
        st.markdown("## 🎓 ڕاهێنەری پزیشکی")
    
    st.markdown("---")
    
    # ئاستی خوێندکار
    student_level = st.selectbox(
        "📚 ئاستی خوێندنت:",
        ["ساڵی یەکەم", "ساڵی دووەم", "ساڵی سێیەم", "ساڵی چوارەم", "ساڵی پێنجەم", "ساڵی شەشەم"],
        index=["ساڵی یەکەم", "ساڵی دووەم", "ساڵی سێیەم", "ساڵی چوارەم", "ساڵی پێنجەم", "ساڵی شەشەم"].index(st.session_state.student_level) if st.session_state.student_level in ["ساڵی یەکەم", "ساڵی دووەم", "ساڵی سێیەم", "ساڵی چوارەم", "ساڵی پێنجەم", "ساڵی شەشەم"] else 0
    )
    st.session_state.student_level = student_level
    
    level_score = get_student_level_score(student_level)
    
    st.markdown("---")
    
    # ناوەڕۆک
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
            "🧠 AI یاریدەدەر"
        ],
        index=0
    )
    
    st.markdown("---")
    
    # ئاماری خێرا
    st.markdown("### 📊 ئاماری تۆ")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📝 کویز", f"{st.session_state.quiz_score}/10")
    with col2:
        st.metric("🩺 کەیس", st.session_state.total_cases_solved)
    
    # پێشکەوتنی گشتی
    total_progress = min(65 + (st.session_state.total_cases_solved * 2) + (st.session_state.quiz_score * 3), 100)
    st.progress(total_progress/100, text=f"پێشکەوتنی گشتی: {total_progress}%")
    
    # وەرزی خوێندن
    st.markdown("---")
    st.markdown(f"### 👨‍🎓 {student_level}")
    st.markdown(f"🏅 نمرەی ئاست: {level_score}%")
    
    # دوایین چالاکی
    time_diff = datetime.now() - st.session_state.last_activity
    minutes = int(time_diff.total_seconds() / 60)
    st.markdown(f"🕐 دوایین چالاکی: {minutes} خولەک پێش")

# ================================
# پەڕەی داشبۆردی فێربوون
# ================================
if page == "🏠 داشبۆردی فێربوون":
    st.markdown('<h1 class="main-header">🎓 ڕاهێنەری پزیشکی - ببە پزیشکێکی لێهاتوو</h1>', unsafe_allow_html=True)
    
    # کارتەکانی ئامار
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="stat-card">
            <h3>📚</h3>
            <h2>{}</h2>
            <p>کەیسی فێربوون</p>
        </div>
        """.format(len(training_data)), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-card">
            <h3>🩺</h3>
            <h2>{}</h2>
            <p>نەخۆشی جیاواز</p>
        </div>
        """.format(len(DISEASE_DATABASE)), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stat-card">
            <h3>📝</h3>
            <h2>{}/10</h2>
            <p>کویزی ئەنجامدراو</p>
        </div>
        """.format(st.session_state.quiz_score), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="stat-card">
            <h3>🎯</h3>
            <h2>{}%</h2>
            <p>دەقی ڕاست</p>
        </div>
        """.format(int((st.session_state.correct_diagnoses / max(st.session_state.total_cases_solved, 1)) * 100)), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # وانەی ڕۆژانە
    st.markdown("### 📖 وانەی ڕۆژانە")
    
    daily_topic = random.choice(list(DISEASE_DATABASE.keys()))
    daily_info = DISEASE_DATABASE[daily_topic]
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"""
        <div class="case-card">
            <h3>🎯 وانەی ئەمڕۆ: {daily_topic}</h3>
            <p><strong>نیشانە سەرەکییەکان:</strong> {', '.join(daily_info['نیشانەکان'][:4])}</p>
            <p><strong>تایبەتمەندی جیاکەرەوە:</strong> {daily_info['تایبەتمەندییە جیاکەرەوەکان']}</p>
            <p><strong>ئاستی مەترسی:</strong> <span style='color: red; font-weight: bold;'>{daily_info['ئاستی مەترسی']}</span></p>
            <p><strong>ڕێپیشگیری:</strong> {daily_info['ڕێپیشگیری'][0] if daily_info['ڕێپیشگیری'] else 'نییە'}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 🎯 ئامانجەکانی فێربوون")
        
        # ئامانجەکانی ئەمڕۆ
        today_goals = [
            "ناسینەوەی نیشانەکانی نەخۆشی",
            "فێربوونی پشکنینەکان",
            "دەستنیشانکردنی جیاکار",
            "پلانی چارەسەر"
        ]
        
        for i, goal in enumerate(today_goals):
            checked = i < 2
            st.checkbox(goal, checked, key=f"goal_{i}")
    
    # گرافی پێشکەوتن
    st.markdown("---")
    st.markdown("### 📈 پێشکەوتنی فێربوون بەپێی بوار")
    
    progress_data = pd.DataFrame({
        'بوار': ['نیشانەناسی', 'دەستنیشانکردن', 'چارەسەر', 'فارماکۆلۆجی', 'پشکنینەکان', 'ڕێپیشگیری'],
        'پێشکەوتن': [
            min(75 + st.session_state.total_cases_solved, 100),
            min(60 + st.session_state.total_cases_solved * 1.5, 100),
            min(55 + st.session_state.quiz_score * 3, 100),
            min(70 + st.session_state.quiz_score * 2, 100),
            min(80 + st.session_state.total_cases_solved, 100),
            min(50 + st.session_state.total_cases_solved, 100)
        ]
    })
    
    fig = px.bar(progress_data, x='بوار', y='پێشکەوتن',
                 title='ڕێژەی لێهاتوویی بەپێی بوار (%)',
                 color='پێشکەوتن',
                 color_continuous_scale='Viridis',
                 text_auto=True)
    fig.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    # کەیسەکانی دوایین
    st.markdown("---")
    st.markdown("### 🩺 کەیسەکانی دوایین")
    
    if len(st.session_state.case_history) > 0:
        recent_cases = st.session_state.case_history[-3:]
        for case in recent_cases:
            st.markdown(f"""
            <div class="case-card">
                <strong>{case['case_id']}</strong> - 
                {case['دەستنیشانکردن']} 
                <span style="color: {'green' if case['result'] else 'red'}">
                    {'✅ ڕاست' if case['result'] else '❌ هەڵە'}
                </span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("هێشتا هیچ کەیسیەکت شیکار نەکردووە. بچۆ بۆ بەشی 'شیکاری کەیس' دەستپێبکە!")

# ================================
# پەڕەی کتێبخانەی نەخۆشییەکان
# ================================
elif page == "📚 کتێبخانەی نەخۆشییەکان":
    st.markdown("## 📚 کتێبخانەی نەخۆشییەکان")
    
    # گەڕان
    search = st.text_input("🔍 گەڕان بەدوای نەخۆشیدا:", placeholder="ناوی نەخۆشی بنووسە...")
    
    # فلتر
    filter_risk = st.selectbox("فلتر بەپێی ئاستی مەترسی:", ["هەموو", "زۆر مەترسیدار", "مەترسیدار", "مامناوەند", "کەم"])
    
    if search:
        filtered = {k: v for k, v in DISEASE_DATABASE.items() if search in k}
    else:
        filtered = DISEASE_DATABASE
    
    if filter_risk != "هەموو":
        filtered = {k: v for k, v in filtered.items() if v['ئاستی مەترسی'] == filter_risk}
    
    # پیشاندان
    cols = st.columns(2)
    col_idx = 0
    
    for disease, info in filtered.items():
        with cols[col_idx % 2]:
            risk_color = {
                "زۆر مەترسیدار": "red",
                "مەترسیدار": "orange",
                "مامناوەند": "blue",
                "کەم": "green"
            }.get(info['ئاستی مەترسی'], "black")
            
            with st.expander(f"🩺 {disease}", expanded=False):
                st.markdown(f"**⚠️ ئاستی مەترسی:** <span style='color:{risk_color};font-weight:bold;'>{info['ئاستی مەترسی']}</span>", unsafe_allow_html=True)
                
                st.markdown("#### 🔍 نیشانەکان")
                for symptom in info['نیشانەکان']:
                    st.markdown(f"- {symptom}")
                
                st.markdown("#### 🧪 پشکنینە دەستنیشانکردنەکان")
                for test, value in info['پشکنینەکان'].items():
                    st.markdown(f"- **{test}**: {value}")
                
                st.markdown("#### 💊 چارەسەر")
                for treatment in info['چارەسەر']:
                    st.markdown(f"- {treatment}")
                
                st.markdown("#### 🛡️ ڕێپیشگیری")
                for prevention in info.get('ڕێپیشگیری', []):
                    st.markdown(f"- {prevention}")
                
                st.info(f"**🔑 تایبەتمەندی جیاکەرەوە:** {info['تایبەتمەندییە جیاکەرەوەکان']}")
        col_idx += 1
    
    if len(filtered) == 0:
        st.warning("هیچ نەخۆشییەک نەدۆزرایەوە. تکایە بە شێوەیەکی تر بگەڕێ.")

# ================================
# پەڕەی شیکاری کەیس
# ================================
elif page == "🩺 شیکاری کەیس":
    st.markdown("## 🩺 شیکاری کەیسی پزیشکی")
    
    st.markdown("### 📋 کەیسێکی نوێ بخوێنەرەوە و دەستنیشانی بکە")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 کەیسی نوێ", use_container_width=True, type="primary"):
            random_case = training_data.sample(1).iloc[0]
            st.session_state.current_case = random_case
            st.session_state.diagnosis_submitted = False
            st.rerun()
    
    if st.session_state.current_case is None:
        random_case = training_data.sample(1).iloc[0]
        st.session_state.current_case = random_case
    
    case = st.session_state.current_case
    
    # نیشاندانی کەیس
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"""
        <div class="case-card">
            <h3>📋 کەیسی ژمارە: {case['case_id']}</h3>
            <table style="width:100%">
                <tr><td><strong>تەمەن:</strong></td><td>{case['تەمەن']} ساڵ</td></tr>
                <tr><td><strong>ڕەگەز:</strong></td><td>{case['ڕەگەز']}</td></tr>
                <tr><td><strong>نیشانەکان:</strong></td><td>{', '.join(case['نیشانە سەرەکییەکان'])}</td></tr>
                <tr><td><strong>پشکنینی پێشنیارکراو:</strong></td><td>{', '.join(case['پشکنینە پێویستەکان'])}</td></tr>
                <tr><td><strong>ئاستی مەترسی:</strong></td><td><span style='color:red;'>{case['ئاستی مەترسی']}</span></td></tr>
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
            default=case['پشکنینە پێویستەکان'][:3] if isinstance(case['پشکنینە پێویستەکان'], list) else []
        )
    
    st.markdown("### 🎯 دەستنیشانکردنەکەت چییە؟")
    
    diagnosis_options = list(DISEASE_DATABASE.keys()) + ["نەخۆشی تر", "پێویستی بە پشکنینی زیاترە"]
    
    user_diagnosis = st.selectbox("دەستنیشانکردن هەڵبژێرە:", diagnosis_options, key="diagnosis_select")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("✅ پشتڕاستکردنەوە", type="primary", use_container_width=True):
            correct_diagnosis = case['دەستنیشانکردن']
            st.session_state.diagnosis_submitted = True
            
            if user_diagnosis == correct_diagnosis:
                st.markdown(f"""
                <div class="success-box">
                    <h3>🎉 زۆر باشە! دەستنیشانکردنەکەت ڕاستە!</h3>
                    <p>دەستنیشانکردنی ڕاست: <strong>{correct_diagnosis}</strong></p>
                    <p>تۆ نیشانەکانت بە باشی خوێندەوە و گەیشتیتە دەستنیشانکردنی ڕاست!</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.session_state.correct_diagnoses += 1
                st.session_state.total_cases_solved += 1
                st.session_state.case_history.append({
                    'case_id': case['case_id'],
                    'دەستنیشانکردن': correct_diagnosis,
                    'result': True
                })
                st.balloons()
                
            else:
                st.markdown(f"""
                <div class="error-box">
                    <h3>❌ ببورە، دەستنیشانکردنەکەت هەڵەیە</h3>
                    <p>دەستنیشانکردنی ڕاست: <strong>{correct_diagnosis}</strong></p>
                    <p>دەستنیشانکردنی تۆ: {user_diagnosis}</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.session_state.total_cases_solved += 1
                st.session_state.case_history.append({
                    'case_id': case['case_id'],
                    'دەستنیشانکردن': correct_diagnosis,
                    'result': False
                })
                
                st.markdown("### 💡 ڕێنمایی فێربوون:")
                disease_info = DISEASE_DATABASE[correct_diagnosis]
                st.info(f"**🔑 خاڵی جیاکەرەوە:** {disease_info['تایبەتمەندییە جیاکەرەوەکان']}")
                st.info(f"**🩺 نیشانە سەرەکییەکان:** {', '.join(disease_info['نیشانەکان'][:3])}")
    
    with col2:
        if st.button("💡 ڕاهێنەر", use_container_width=True):
            correct_diagnosis = case['دەستنیشانکردن']
            disease_info = DISEASE_DATABASE[correct_diagnosis]
            
            st.markdown("### 💡 ڕێنمایی")
            st.markdown(f"**نەخۆشی ڕاستەقینە:** {correct_diagnosis}")
            st.markdown(f"**نیشانە جیاکەرەوەکان:** {disease_info['تایبەتمەندییە جیاکەرەوەکان']}")
            st.markdown(f"**چارەسەری سەرەکی:** {disease_info['چارەسەر'][0]}")
    
    # ئاماری کەیسەکان
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
# پەڕەی کویزی پزیشکی
# ================================
elif page == "📝 کویزی پزیشکی":
    st.markdown("## 📝 تاقیکردنەوەی پزیشکی")
    
    if not st.session_state.quiz_completed:
        quiz = MEDICAL_QUIZZES[st.session_state.quiz_index]
        
        st.markdown(f"### ❓ پرسیاری {st.session_state.quiz_index + 1} لە {len(MEDICAL_QUIZZES)}")
        
        # پڕۆگرێس
        progress = (st.session_state.quiz_index) / len(MEDICAL_QUIZZES) * 100
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
                
                if selected_index == quiz['وەڵامی ڕاست']:
                    st.session_state.quiz_score += 1
                    st.success("🎉 وەڵامەکەت ڕاستە! نمرەی زیادیکرد")
                else:
                    st.error(f"❌ وەڵامەکەت هەڵەیە. وەڵامی ڕاست: {quiz['هەڵبژاردەکان'][quiz['وەڵامی ڕاست']]}")
                
                st.info(f"📚 ڕوونکردنەوە: {quiz['ڕوونکردنەوە']}")
        
        with col2:
            if st.button("➡️ پرسیاری داهاتوو", use_container_width=True):
                if st.session_state.quiz_index < len(MEDICAL_QUIZZES) - 1:
                    st.session_state.quiz_index += 1
                else:
                    st.session_state.quiz_completed = True
                st.rerun()
        
        # نمرە
        st.markdown(f"🏆 نمرە: {st.session_state.quiz_score}/{len(MEDICAL_QUIZZES)}")
    
    else:
        # تەواوکردنی کویز
        percentage = (st.session_state.quiz_score / len(MEDICAL_QUIZZES)) * 100
        
        st.markdown(f"""
        <div class="success-box">
            <h2>🎊 تاقیکردنەوە تەواو بوو!</h2>
            <h3>نمرەی تۆ: {st.session_state.quiz_score}/{len(MEDICAL_QUIZZES)}</h3>
            <h4>ڕێژە: {percentage:.1f}%</h4>
            <p>{'🌟 زۆر باش! تۆ پزیشکێکی لێهاتووی!' if percentage >= 80 else '📚 باشە، بەردەوام بە لە فێربوون!' if percentage >= 50 else '💪 بەردەوام بە، دەتوانی باشتر بکەیت!'}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # گریف
        if percentage >= 80:
            fig = go.Figure(data=[go.Pie(labels=['ڕاست', 'هەڵە'], 
                                         values=[st.session_state.quiz_score, len(MEDICAL_QUIZZES)-st.session_state.quiz_score],
                                         marker_colors=['#28a745', '#dc3545'])])
            fig.update_layout(title='ئەنجامی کویز')
            st.plotly_chart(fig, use_container_width=True)
        
        if st.button("🔄 تاقیکردنەوەی نوێ", use_container_width=True):
            st.session_state.quiz_index = 0
            st.session_state.quiz_score = 0
            st.session_state.quiz_completed = False
            st.rerun()

# ================================
# پەڕەی تاقیگەی ڤێرچواڵ
# ================================
elif page == "🔬 تاقیگەی ڤێرچواڵ":
    st.markdown("## 🔬 تاقیگەی پزیشکی ڤێرچواڵ")
    
    st.markdown("### 🧪 شیکاری پشکنینە تاقیگەییەکان")
    
    tab1, tab2, tab3 = st.tabs(["🩸 CBC", "🧪 بایۆکیمیایی", "❤️ دڵ"])
    
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
        
        if st.button("🔍 شیکاری CBC بکە", use_container_width=True, key="cbc_analyze"):
            st.markdown("---")
            st.markdown("#### 📈 ئەنجامی شیکاری:")
            
            results = []
            # WBC
            if wbc > 11:
                results.append(("WBC بەرزە", "⚠️ ئەگەری هەوکردن یان لیکۆسایتۆسیس", "error"))
            elif wbc < 4:
                results.append(("WBC نزمە", "⚠️ لیکۆپینیا", "warning"))
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
                results.append(("MCV نزمە", "⚠️ ئەنیمیای مایکرۆسایتیک", "warning"))
            elif mcv > 100:
                results.append(("MCV بەرزە", "⚠️ ئەنیمیای ماکرۆسایتیک", "warning"))
            else:
                results.append(("MCV نۆرماڵە", "✅ نۆرماڵ", "success"))
            
            for title, detail, status in results:
                if status == "error":
                    st.error(f"**{title}** - {detail}")
                elif status == "warning":
                    st.warning(f"**{title}** - {detail}")
                else:
                    st.success(f"**{title}** - {detail}")
    
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
        
        if st.button("🔍 شیکاری بایۆکیمیایی بکە", use_container_width=True, key="bio_analyze"):
            st.markdown("---")
            st.markdown("#### 📈 ئەنجامی شیکاری:")
            
            if glucose > 126:
                st.error(f"⚠️ Glucose={glucose} بەرزە - پێویستە پشکنینی شەکرە بکرێت")
            elif glucose < 70:
                st.warning(f"⚠️ Glucose={glucose} نزمە - هایپۆگلایسیمیا")
            else:
                st.success("✅ Glucose نۆرماڵە")
            
            if creatinine > 1.3:
                st.error(f"⚠️ Creatinine={creatinine} بەرزە - ئەگەری کێشەی گورچیلە")
            else:
                st.success("✅ Creatinine نۆرماڵە")
            
            if alt > 40:
                st.warning(f"⚠️ ALT={alt} بەرزە - ئەگەری کێشەی جگەر")
            else:
                st.success("✅ ALT نۆرماڵە")
            
            if ast > 40:
                st.warning(f"⚠️ AST={ast} بەرزە - ئەگەری کێشەی جگەر")
            else:
                st.success("✅ AST نۆرماڵە")
            
            if potassium < 3.5:
                st.warning(f"⚠️ Potassium={potassium} نزمە - هایپۆکالیمیا")
            elif potassium > 5.0:
                st.warning(f"⚠️ Potassium={potassium} بەرزە - هایپەرکالیمیا")
            else:
                st.success("✅ Potassium نۆرماڵە")
    
    with tab3:
        st.markdown("#### ❤️ پشکنینەکانی دڵ")
        
        col1, col2 = st.columns(2)
        with col1:
            troponin = st.number_input("Troponin (ng/mL):", 0.0, 10.0, 0.01, 0.01, key="troponin")
            ck_mb = st.number_input("CK-MB (ng/mL):", 0.0, 50.0, 2.0, 0.1, key="ck_mb")
        
        if st.button("🔍 شیکاری دڵ بکە", use_container_width=True, key="cardiac_analyze"):
            st.markdown("---")
            st.markdown("#### 📈 ئەنجامی شیکاری:")
            
            if troponin > 0.04:
                st.error(f"⚠️ Troponin={troponin} بەرزە - ئەگەری نەخۆشی دڵی ئیسکیمیک")
                st.warning("پێویستە ECG و شیکاری زیاتر بکرێت")
            else:
                st.success("✅ Troponin نۆرماڵە")
            
            if ck_mb > 5:
                st.warning(f"⚠️ CK-MB={ck_mb} بەرزە - ئەگەری زیانی ماسوولکەی دڵ")
            else:
                st.success("✅ CK-MB نۆرماڵە")

# ================================
# پەڕەی پێشکەوتنی فێربوون
# ================================
elif page == "📊 پێشکەوتنی فێربوون":
    st.markdown("## 📊 دۆشیەی فێربوون")
    
    # خاڵەکانی لێهاتوویی
    st.markdown("### 🎯 خاڵەکانی لێهاتوویی")
    
    skills = {
        'نیشانەناسی': min(85 + st.session_state.total_cases_solved, 100),
        'دەستنیشانکردن': min(70 + st.session_state.total_cases_solved * 1.5, 100),
        'پشکنینەکان': min(90 + st.session_state.total_cases_solved, 100),
        'چارەسەر': min(65 + st.session_state.quiz_score * 3, 100),
        'ڕێپیشگیری': min(75 + st.session_state.total_cases_solved * 0.5, 100),
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
        if st.session_state.quiz_score >= 8:
            achievements.append("🎓 نمرەی بەرز لە کویز")
        if st.session_state.correct_diagnoses >= 5:
            achievements.append("💯 دەستنیشانکردنی ٥ کەیسی ڕاست")
        if st.session_state.total_cases_solved >= 20:
            achievements.append("🔬 شیکاری ٢٠ کەیسی پزیشکی")
        
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
        scores = [min(100, s + st.session_state.total_cases_solved * 0.5) for s in base_scores]
        
        fig = px.line(x=months, y=scores, title='پێشکەوتنی فێربوون',
                     labels={'x': 'مانگ', 'y': 'نمرە'})
        fig.update_traces(line_color='#667eea', line_width=3)
        st.plotly_chart(fig, use_container_width=True)
    
    # پێشکەوتنی بوارەکان
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

# ================================
# پەڕەی فارماکۆلۆجی
# ================================
elif page == "💊 فارماکۆلۆجی":
    st.markdown("## 💊 فارماکۆلۆجی و دەرمانناسی")
    
    drug_categories = {
        "دژە پەستانی خوێن": {
            "دەرمانەکان": {
                "کاپتۆپریل": {
                    "ڕێژە": "25-50mg",
                    "میکانیزم": "ACE inhibitor",
                    "کاریگەری لاوەکی": "کۆخە",
                    "پێچەوانە": "حەملی دووگیانی"
                },
                "ئەملۆدیپین": {
                    "ڕێژە": "5-10mg",
                    "میکانیزم": "Calcium channel blocker",
                    "کاریگەری لاوەکی": "ئاوسانی قاچ",
                    "پێچەوانە": "هەستیاری"
                },
                "لۆسارتان": {
                    "ڕێژە": "50-100mg",
                    "میکانیزم": "ARB",
                    "کاریگەری لاوەکی": "سەرگێژخواردن",
                    "پێچەوانە": "نەخۆشی گورچیلە"
                }
            }
        },
        "دژە شەکرە": {
            "دەرمانەکان": {
                "مێتفۆرمین": {
                    "ڕێژە": "500-2000mg",
                    "میکانیزم": "Biguanide",
                    "کاریگەری لاوەکی": "سکچوون",
                    "پێچەوانە": "نەخۆشی گورچیلە"
                },
                "گلیپیزاید": {
                    "ڕێژە": "5-20mg",
                    "میکانیزم": "Sulfonylurea",
                    "کاریگەری لاوەکی": "هایپۆگلایسیمیا",
                    "پێچەوانە": "هەستیاری"
                }
            }
        },
        "دژە کۆخە و هەوکردن": {
            "دەرمانەکان": {
                "ئەمۆکسیسیلین": {
                    "ڕێژە": "500mg",
                    "میکانیزم": "Beta-lactam",
                    "کاریگەری لاوەکی": "زکچوون",
                    "پێچەوانە": "هەستیاری پێنیسیلین"
                },
                "ئازیترۆمایسین": {
                    "ڕێژە": "250-500mg",
                    "میکانیزم": "Macrolide",
                    "کاریگەری لاوەکی": "سکچوون",
                    "پێچەوانە": "نەخۆشی دڵ"
                }
            }
        },
        "دژە ئەنیمیا": {
            "دەرمانەکان": {
                "فێروس سولفەیت": {
                    "ڕێژە": "300-600mg",
                    "میکانیزم": "Iron supplement",
                    "کاریگەری لاوەکی": "سکچوون",
                    "پێچەوانە": "هیمۆکروماتۆسیس"
                },
                "فۆلیک ئەسید": {
                    "ڕێژە": "1mg",
                    "میکانیزم": "Folate supplement",
                    "کاریگەری لاوەکی": "کەم",
                    "پێچەوانە": "هەستیاری"
                }
            }
        }
    }
    
    selected_category = st.selectbox("پۆلێنی دەرمان:", list(drug_categories.keys()))
    
    if selected_category:
        st.markdown(f"### 📋 دەرمانەکانی {selected_category}")
        
        for drug, info in drug_categories[selected_category]["دەرمانەکان"].items():
            with st.expander(f"💊 {drug}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**📏 ڕێژە:** {info['ڕێژە']}")
                    st.markdown(f"**⚙️ میکانیزم:** {info['میکانیزم']}")
                with col2:
                    st.markdown(f"**⚠️ کاریگەری لاوەکی:** {info['کاریگەری لاوەکی']}")
                    st.markdown(f"**🚫 پێچەوانە:** {info['پێچەوانە']}")
    
    # دەرمانەکانی نەخۆشییەکان
    st.markdown("---")
    st.markdown("### 🩺 دەرمانەکانی نەخۆشییەکان")
    
    disease_for_drugs = st.selectbox("نەخۆشی هەڵبژێرە:", list(DISEASE_DATABASE.keys()))
    
    if disease_for_drugs:
        disease_info = DISEASE_DATABASE[disease_for_drugs]
        st.markdown(f"**💊 چارەسەری {disease_for_drugs}:**")
        for treatment in disease_info['چارەسەر']:
            st.markdown(f"- {treatment}")

# ================================
# پەڕەی AI یاریدەدەر
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
        
        age_input = st.number_input("تەمەن:", 1, 120, 40)
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
                                'ئاستی مەترسی': info['ئاستی مەترسی']
                            })
                    
                    results.sort(key=lambda x: x['ڕێژەی گونجاندن'], reverse=True)
                    
                    if results:
                        top_results = results[:3]
                        
                        for i, result in enumerate(top_results):
                            risk_color = {
                                "زۆر مەترسیدار": "red",
                                "مەترسیدار": "orange",
                                "مامناوەند": "blue",
                                "کەم": "green"
                            }.get(result['ئاستی مەترسی'], "black")
                            
                            st.markdown(f"""
                            <div class="case-card">
                                <h4>#{i+1} {result['نەخۆشی']}</h4>
                                <p><strong>ڕێژەی گونجاندن:</strong> {result['ڕێژەی گونجاندن']}%</p>
                                <p><strong>نیشانە هاوبەشەکان:</strong> {', '.join(result['نیشانە هاوبەشەکان'])}</p>
                                <p><strong>ئاستی مەترسی:</strong> <span style='color:{risk_color};'>{result['ئاستی مەترسی']}</span></p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # پیشنهادی چارەسەر بۆ باشترین دەرەنجام
                        best_match = results[0]
                        disease_info = DISEASE_DATABASE[best_match['نەخۆشی']]
                        st.markdown(f"""
                        <div class="success-box">
                            <h4>💡 پێشنیاری چارەسەر بۆ {best_match['نەخۆشی']}:</h4>
                            <p><strong>چارەسەر:</strong> {', '.join(disease_info['چارەسەر'][:2])}</p>
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
        
        common_symptoms = list(set(common_symptoms))[:15]
        
        for symptom in common_symptoms:
            st.markdown(f"- {symptom}")
        
        st.markdown("---")
        st.markdown("### 💡 ڕێنمایی")
        st.info("نیشانەکان بە وردی بنووسە و ئەگەر نیشانەی زیاتر هەیە زیاد بکە بۆ شیکاری باشتر.")

# ================================
# فووەتەر
# ================================
st.markdown("---")
st.markdown("""
<div class="footer-style">
    <h3>🎓 ڕاهێنەری پزیشکی - Medical Training Simulator</h3>
    <p>بۆ خوێندکارانی پزیشکی - ببە پزیشکێکی لێهاتوو</p>
    <p>© 2024 | وەشانی 2.0.0 | کەم و کورتییەکان چاککران</p>
</div>
""", unsafe_allow_html=True)
