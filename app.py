# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import os
import random
from typing import List, Dict, Any

# ==================== Page Config ====================
st.set_page_config(
    page_title="سیستەمی شیکردنەوەی تاقیگە - دانیال ئیسماعیل",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== Custom CSS ====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Kurdish:wght@400;500;600;700&family=Noto+Sans+Arabic:wght@400;500;600;700&display=swap');

    * {
        font-family: 'Noto Sans Arabic', 'Noto Kurdish', sans-serif !important;
    }
    
    body {
        direction: rtl;
    }

    .main-header {
        background: linear-gradient(135deg, #0d47a1 0%, #1565c0 50%, #1976d2 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        font-size: 1.5rem !important;
        margin: 0 0 5px 0 !important;
        color: white !important;
    }
    
    .main-header p {
        font-size: 0.9rem !important;
        margin: 0 !important;
        color: rgba(255,255,255,0.9) !important;
    }

    .student-info {
        background: linear-gradient(135deg, #1a237e, #283593);
        color: white;
        padding: 12px 15px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .student-info h2 {
        font-size: 1.1rem !important;
        margin: 0 0 3px 0 !important;
        color: white !important;
    }
    
    .student-info p {
        font-size: 0.8rem !important;
        margin: 0 !important;
        color: rgba(255,255,255,0.9) !important;
    }

    .category-card {
        background: linear-gradient(135deg, #e8eaf6, #c5cae9);
        padding: 15px;
        border-radius: 10px;
        margin: 8px 0;
        border-right: 4px solid #1565c0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    .info-box {
        background: #e3f2fd;
        padding: 12px;
        border-radius: 8px;
        border-right: 3px solid #1565c0;
        margin: 8px 0;
    }
    
    .info-box h4 {
        font-size: 1rem !important;
        margin: 0 0 8px 0 !important;
    }

    .warning-box {
        background: #fff3e0;
        padding: 12px;
        border-radius: 8px;
        border-right: 3px solid #ff9800;
        margin: 8px 0;
    }
    
    .critical-box {
        background: #ffebee;
        padding: 12px;
        border-radius: 8px;
        border-right: 3px solid #f44336;
        margin: 8px 0;
    }

    .symptom-tag {
        display: inline-block;
        background: linear-gradient(135deg, #ffebee, #ffcdd2);
        color: #c62828;
        padding: 4px 10px;
        border-radius: 15px;
        margin: 2px;
        font-size: 0.85em;
        border: 1px solid #ef9a9a;
    }

    .step-number {
        display: inline-block;
        background: linear-gradient(135deg, #0d47a1, #1565c0);
        color: white;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        text-align: center;
        line-height: 28px;
        margin-left: 6px;
        font-weight: bold;
        font-size: 0.85em;
    }

    .normal-range {
        color: #2e7d32;
        font-weight: bold;
        background-color: #e8f5e9;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 0.9em;
    }

    .critical-range {
        color: #c62828;
        font-weight: bold;
        background-color: #ffebee;
        padding: 2px 6px;
        border-radius: 4px;
    }
    
    .stat-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .test-result-normal {
        background-color: #e8f5e9;
        padding: 8px;
        border-radius: 6px;
        border-right: 3px solid #4caf50;
        margin: 4px 0;
        font-size: 0.9em;
    }
    
    .test-result-abnormal {
        background-color: #fff3e0;
        padding: 8px;
        border-radius: 6px;
        border-right: 3px solid #ff9800;
        margin: 4px 0;
        font-size: 0.9em;
    }
    
    .test-result-critical {
        background-color: #ffebee;
        padding: 8px;
        border-radius: 6px;
        border-right: 3px solid #f44336;
        margin: 4px 0;
        font-size: 0.9em;
    }
    
    .practical-step {
        background: #f5f5f5;
        padding: 8px;
        margin: 4px 0;
        border-radius: 5px;
        border-left: 3px solid #1565c0;
        font-size: 0.9em;
    }
    
    .note-card {
        background: white;
        padding: 12px;
        border-radius: 8px;
        margin: 8px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-top: 3px solid #1565c0;
    }

    .stButton > button {
        font-size: 0.85rem !important;
        white-space: normal !important;
        word-wrap: break-word !important;
        text-align: right !important;
        direction: rtl !important;
    }
    
    .sidebar .stMarkdown h2 {
        font-size: 1.2rem !important;
    }
    
    [data-testid="stSidebar"] h2 {
        font-size: 1.3rem !important;
    }
    
    .stMarkdown, .stMarkdown p, .stMarkdown h1,
    .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, 
    .stMarkdown h5, .stMarkdown h6 {
        color: #1a1a1a !important;
    }
    
    @media (prefers-color-scheme: dark) {
        .stMarkdown, .stMarkdown p, .stMarkdown h3, .stMarkdown h4 {
            color: #e0e0e0 !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# ==================== Database ====================
@st.cache_resource
def init_db():
    """Initialize database"""
    try:
        if os.path.exists('medical_lab.db'):
            try:
                test_conn = sqlite3.connect('medical_lab.db')
                test_conn.execute("SELECT 1")
                test_conn.close()
            except:
                os.remove('medical_lab.db')
        
        conn = sqlite3.connect('medical_lab.db', check_same_thread=False, timeout=30)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.row_factory = sqlite3.Row
        
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS disease_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name_en TEXT NOT NULL UNIQUE,
            name_ku TEXT NOT NULL UNIQUE,
            description_en TEXT,
            description_ku TEXT,
            icon TEXT,
            color TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS diseases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            name_en TEXT NOT NULL,
            name_ku TEXT NOT NULL,
            description_en TEXT,
            description_ku TEXT,
            symptoms_en TEXT,
            symptoms_ku TEXT,
            causes_en TEXT,
            causes_ku TEXT,
            treatment_en TEXT,
            treatment_ku TEXT,
            severity TEXT DEFAULT 'Moderate',
            FOREIGN KEY (category_id) REFERENCES disease_categories(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS test_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name_en TEXT NOT NULL UNIQUE,
            name_ku TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL,
            unit TEXT,
            normal_range_low REAL,
            normal_range_high REAL,
            critical_low REAL,
            critical_high REAL,
            description_en TEXT,
            description_ku TEXT,
            preparation_en TEXT,
            preparation_ku TEXT,
            turnaround_time TEXT DEFAULT '24 hours',
            price REAL DEFAULT 0.0
        );

        CREATE TABLE IF NOT EXISTS practical_tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title_en TEXT NOT NULL,
            title_ku TEXT NOT NULL,
            description_en TEXT,
            description_ku TEXT,
            category TEXT,
            steps_en TEXT,
            steps_ku TEXT,
            materials_en TEXT,
            materials_ku TEXT,
            expected_results_en TEXT,
            expected_results_ku TEXT,
            interpretation_en TEXT,
            interpretation_ku TEXT,
            precautions_en TEXT,
            precautions_ku TEXT,
            duration_minutes INTEGER,
            difficulty_level TEXT CHECK(difficulty_level IN ('Basic', 'Intermediate', 'Advanced')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS study_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT,
            tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS test_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            patient_age INTEGER,
            patient_gender TEXT CHECK(patient_gender IN ('Male', 'Female', 'Other')),
            test_id INTEGER NOT NULL,
            result_value REAL,
            result_text TEXT,
            is_abnormal INTEGER DEFAULT 0,
            is_critical INTEGER DEFAULT 0,
            notes TEXT,
            date_performed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (test_id) REFERENCES test_types(id) ON DELETE CASCADE
        );
        
        CREATE INDEX IF NOT EXISTS idx_test_results_patient ON test_results(patient_name);
        CREATE INDEX IF NOT EXISTS idx_test_results_date ON test_results(date_performed);
        CREATE INDEX IF NOT EXISTS idx_diseases_category ON diseases(category_id);
        """)
        conn.commit()
        return conn
    except Exception as e:
        st.error(f"Database Connection Error: {str(e)}")
        return None

conn = init_db()

# ==================== Insert Data ====================
def insert_comprehensive_data(conn):
    if conn is None:
        return
    try:
        count = conn.execute("SELECT COUNT(*) as c FROM test_types").fetchone()
        if count['c'] > 5:
            return
            
        conn.execute("DELETE FROM test_results")
        conn.execute("DELETE FROM practical_tests")
        conn.execute("DELETE FROM study_notes")
        conn.execute("DELETE FROM diseases")
        conn.execute("DELETE FROM test_types")
        conn.execute("DELETE FROM disease_categories")
        
        categories = [
            ("Hematology", "خوێنناسی", "Study of blood and blood disorders", "لێکۆڵینەوە لە خوێن و نەخۆشییەکانی خوێن", "🩸", "#FF6B6B"),
            ("Clinical Chemistry", "کیمیای کلینیکی", "Chemical analysis of bodily fluids", "شیکردنەوەی کیمیایی شلەکانی لەش", "🧪", "#4ECDC4"),
            ("Microbiology", "مایکرۆبایۆلۆجی", "Study of microorganisms", "لێکۆڵینەوە لە مایکرۆئۆرگانیزمەکان", "🔬", "#45B7D1"),
            ("Immunology", "بەرگری ناسی", "Study of immune system", "لێکۆڵینەوە لە سیستەمی بەرگری", "🛡️", "#96CEB4"),
            ("Endocrinology", "هۆرمۆن ناسی", "Study of hormones", "لێکۆڵینەوە لە هۆرمۆنەکان", "⚡", "#FFEAA7"),
            ("Urinalysis", "شیکردنەوەی میز", "Analysis of urine samples", "شیکردنەوەی نموونەی میز", "💧", "#DDA0DD"),
            ("Coagulation", "مەیاندن", "Blood clotting studies", "لێکۆڵینەوە لە مەیاندنی خوێن", "🩹", "#98D8C8"),
            ("Blood Bank", "بانکی خوێن", "Blood transfusion services", "خزمەتگوزارییەکانی گواستنەوەی خوێن", "🏥", "#F7DC6F"),
        ]
        
        for cat in categories:
            conn.execute("""
            INSERT INTO disease_categories (name_en, name_ku, description_en, description_ku, icon, color)
            VALUES (?, ?, ?, ?, ?, ?)
            """, cat)
        
        tests = [
            ("CBC", "ژمارەی تەواوی خوێن (CBC)", "Hematology", "cells/μL", 4.5, 11.0, 2.0, 15.0, "Complete Blood Count", "ژمارەی تەواوی خوێن", "No special preparation needed", "پێویستی بە ئامادەکاری تایبەت نییە", "2 hours", 25.0),
            ("Hemoglobin", "هیمۆگلۆبین (Hb)", "Hematology", "g/dL", 12.0, 16.0, 7.0, 20.0, "Measures hemoglobin in blood", "بڕی هیمۆگلۆبین لە خوێندا دەپێورێت", "Fasting not required", "پێویستی بە بەڕۆژووبوون نییە", "1 hour", 15.0),
            ("WBC Count", "ژمارەی خانە سپییەکان (WBC)", "Hematology", "cells/μL", 4000, 11000, 2000, 30000, "White Blood Cell count", "ژمارەی خانە سپییەکانی خوێن", "No special preparation", "پێویستی بە ئامادەکاری نییە", "1 hour", 20.0),
            ("Blood Glucose", "شەکری خوێن (FBS)", "Clinical Chemistry", "mg/dL", 70, 100, 40, 300, "Measures blood sugar levels", "ئاستی شەکری خوێن دەپێورێت", "Fast for 8-12 hours", "٨-١٢ کاتژمێر بەڕۆژوو بە", "2 hours", 20.0),
            ("HbA1c", "هیمۆگلۆبینی شەکرەدار (HbA1c)", "Clinical Chemistry", "%", 4.0, 5.6, 3.0, 12.0, "Average blood sugar over 3 months", "تێکڕای شەکری خوێن بۆ ماوەی ٣ مانگ", "No fasting required", "پێویستی بە بەڕۆژووبوون نییە", "4 hours", 50.0),
            ("Creatinine", "کریاتینین (Cr)", "Clinical Chemistry", "mg/dL", 0.6, 1.2, 0.2, 5.0, "Kidney function test", "پشکنینی کاری گورچیلە", "Avoid heavy exercise 24h before", "٢٤ کاتژمێر پێش وەرزشی قورس مەکە", "2 hours", 25.0),
            ("Blood Urea", "یوریای خوێن (BUN)", "Clinical Chemistry", "mg/dL", 7, 20, 3, 50, "Kidney function test", "پشکنینی کاری گورچیلە", "No special preparation", "پێویستی بە ئامادەکاری نییە", "2 hours", 20.0),
            ("Cholesterol Total", "کۆلیستڕۆڵی گشتی", "Clinical Chemistry", "mg/dL", 125, 200, 100, 300, "Total blood cholesterol", "کۆی کۆلیستڕۆڵی خوێن", "Fast for 9-12 hours", "٩-١٢ کاتژمێر بەڕۆژوو بە", "3 hours", 35.0),
            ("ALT", "ئەلانین ئەمینۆترانسفێراز (ALT)", "Clinical Chemistry", "U/L", 7, 56, 3, 200, "Liver enzyme test", "ئەنزیمی جگەر", "No special preparation", "پێویستی بە ئامادەکاری نییە", "2 hours", 25.0),
            ("AST", "ئەسپارتەیت ئەمینۆترانسفێراز (AST)", "Clinical Chemistry", "U/L", 10, 40, 5, 200, "Liver and muscle enzyme test", "پشکنینی ئەنزیمی جگەر و ماسولکە", "No special preparation", "پێویستی بە ئامادەکاری نییە", "2 hours", 25.0),
            ("CRP", "پڕۆتینی کاردەر لە هەوکردن (CRP)", "Immunology", "mg/L", 0, 5, 0, 100, "C-Reactive Protein", "پڕۆتینی کاردەر لە هەوکردن", "No special preparation", "پێویستی بە ئامادەکاری نییە", "2 hours", 40.0),
            ("TSH", "هۆرمۆنی چالاککەری تایرۆید (TSH)", "Endocrinology", "mIU/L", 0.4, 4.0, 0.1, 50.0, "Thyroid Stimulating Hormone", "هۆرمۆنی چالاککەری تایرۆید", "Morning sample preferred", "نموونەی بەیانی باشترە", "3 hours", 60.0),
            ("Urine pH", "ترشێتی میز (pH)", "Urinalysis", "pH", 4.5, 8.0, 4.0, 9.0, "Measures acidity of urine", "ترشێتی میز دەپێورێت", "Fresh sample required", "نموونەی تازە پێویستە", "30 minutes", 10.0),
            ("PT", "کاتی پڕۆترۆمبین (PT)", "Coagulation", "seconds", 11, 13.5, 9, 30, "Prothrombin Time", "کاتی پڕۆترۆمبین", "Avoid anticoagulants if possible", "دژە مەیاندنەکان بەکارمەهێنە", "2 hours", 35.0),
        ]
        
        for test in tests:
            conn.execute("""
            INSERT INTO test_types 
            (name_en, name_ku, category, unit, normal_range_low, normal_range_high, critical_low, critical_high, description_en, description_ku, preparation_en, preparation_ku, turnaround_time, price)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, test)
        
        diseases_data = [
            (1, "Iron Deficiency Anemia", "کەمخوێنی بەهۆی کەمی ئاسن", "Most common type of anemia caused by insufficient iron", "باوباپترین جۆری کەمخوێنی بەهۆی کەمی ئاسنەوە", "Fatigue, Weakness, Pale skin, Shortness of breath, Dizziness", "ماندووبوون، لاوازی، پێستی کاڵ، هەناسە توندی، سەرگێژە", "Poor diet, Blood loss, Pregnancy", "خوارنی خراپ، لەدەستدانی خوێن، دووگیانی", "Iron supplements, Iron-rich diet", "تەواوکەری ئاسن، خواردنی دەوڵەمەند بە ئاسن", "Mild to Severe"),
            (2, "Diabetes Mellitus Type 1", "شەکرەی جۆری ١", "Autoimmune destruction of insulin-producing cells", "تێکدانی خۆبەرگری خانەکانی بەرهەمهێنەری ئینسولین", "Frequent urination, Excessive thirst, Weight loss, Fatigue", "میزی زۆر، تینویەتی زۆر، دابەزینی کێش، ماندووبوون", "Autoimmune reaction, Genetic factors", "کارلێکی خۆبەرگری، هۆکارە بۆماوەییەکان", "Insulin therapy, Diet control", "چارەسەری ئینسولین، کۆنتڕۆڵی خواردن", "Moderate to Severe"),
            (2, "Diabetes Mellitus Type 2", "شەکرەی جۆری ٢", "Insulin resistance and relative insulin deficiency", "بەرگری ئینسولین و کەمی ڕێژەیی ئینسولین", "Slow-healing wounds, Numbness, Blurred vision, Fatigue", "برینەکانی بە هێواشی چاکدەبنەوە، کڕێتی، تەمومژی بینین، ماندووبوون", "Obesity, Sedentary lifestyle, Genetic factors", "قەڵەوی، ژیانی بێ جوڵە، هۆکارە بۆماوەییەکان", "Oral medications, Diet, Exercise", "دەرمانی دەم، ڕێجیم، وەرزش", "Moderate"),
            (6, "Urinary Tract Infection", "هەوکردنی ڕێڕەوی میز", "Bacterial infection of urinary system", "هەوکردنی بەکتریایی سیستەمی میز", "Burning urination, Frequent urination, Cloudy urine, Pelvic pain", "میزکردنی سووتێنەر، میزکردنی زۆر، میزی تەمومژاوی، ئازاری لەگەنە", "E. coli bacteria, Poor hygiene", "بەکتریای ئیکۆلای، پاکژی خراپ", "Antibiotics, Increased fluids", "دژەبەکتریاکان، شلەی زیاتر", "Mild to Moderate")
        ]
        
        for disease in diseases_data:
            conn.execute("""
            INSERT INTO diseases (category_id, name_en, name_ku, description_en, description_ku, symptoms_en, symptoms_ku, causes_en, causes_ku, treatment_en, treatment_ku, severity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, disease)

        practicals = [
            ("Blood Smear Preparation", "ئامادەکردنی سمێری خوێن", "Preparation and staining of blood smear", "ئامادەکردن و ڕەنگکردنی سمێری خوێن", "Hematology",
             "1. Clean slide with alcohol\n2. Place small drop of blood\n3. Use spreader slide at 30-45° angle\n4. Quick smooth motion to spread\n5. Air dry completely\n6. Fix with methanol\n7. Stain with Wright's stain\n8. Wash and dry\n9. Examine under microscope",
             "١. سلاید بە ئەلکحول پاک بکەرەوە\n٢. دڵۆپێکی بچووکی خوێن دابنێ\n٣. سلایدی بڵاوکەرەوە بە گۆشەی ٣٠-٤٥ پلە بەکاربهێنە\n٤. بە جوڵەیەکی خێرا و نەرم بیبڵاوە\n٥. بە تەواوی وشک بکەرەوە\n٦. بە میسانۆل جێگیر بکە\n٧. بە ڕەنگی رایت ڕەنگی بکە\n٨. بیشۆ و وشکی بکەرەوە\n٩. لە ژێر مایکرۆسکۆپ پشکنین بکە",
             "Glass slides, Blood sample, Spreader slide, Methanol, Wright's stain, Microscope", "سلایدی شووشەیی، نموونەی خوێن، سلایدی بڵاوکەرەوە، میسانۆل، ڕەنگی رایت، مایکرۆسکۆپ",
             "Evenly distributed blood cells", "خانەکانی خوێن بە یەکسانی بڵاوکراونەتەوە", "Check RBC morphology", "شێوەی خڕۆکە سوورەکان", "Avoid air bubbles", "دوورکەوتنەوە لە بڵقەکانی هەوا", 30, "Basic")
        ]
        
        for pr in practicals:
            conn.execute("""
            INSERT INTO practical_tests (title_en, title_ku, description_en, description_ku, category, steps_en, steps_ku, materials_en, materials_ku, expected_results_en, expected_results_ku, interpretation_en, interpretation_ku, precautions_en, precautions_ku, duration_minutes, difficulty_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, pr)

        conn.commit()
    except Exception as e:
        st.error(f"Error seeding database: {str(e)}")

insert_comprehensive_data(conn)

# ==================== Translation System ====================
translations = {
    "کوردی 🇹🇯": {
        "dashboard": "📊 داشبۆرد", "disease_db": "🦠 نەخۆشییەکان", "lab_tests": "🧪 پشکنینەکان", 
        "practical": "🔬 پراکتیکی", "theory": "📚 تێبینییەکان", "results_entry": "📝 ئەنجامەکان",
        "reports": "📈 ڕاپۆرت", "ai_chat": "🤖 زیرەکی دەستکرد", "description": "ڕوونکردنەوە",
        "symptoms": "نیشانەکان", "causes": "هۆکارەکان", "treatment": "چارەسەر", "severity": "توندی",
        "normal_range": "مەودای ئاسایی", "critical_values": "بەهای مەترسیدار", "low": "نزم", "high": "بەرز", 
        "unit": "یەکە", "minutes": "خولەک", "procedure": "هەنگاوەکان", "materials": "کەرەستەکان",
        "expected_results": "ئەنجامی چاوەڕوانکراو", "interpretation": "لێکدانەوە", "precautions": "ڕێوشوێنی خۆپارێزی",
        "save_note": "تۆمارکردن", "saved_success": "بەسەرکەوتوویی تۆمارکرا! ✅", "patient_name": "ناوی نەخۆش",
        "patient_age": "تەمەن", "patient_gender": "ڕەگەز", "select_test": "پشکنین هەڵبژێرە",
        "result_value": "ئەنجام", "save_result": "تۆمارکردنی ئەنجام", "ask_ai": "پرسیار بکە",
        "type_question": "پرسیارەکەت بنووسە...", "search": "گەڕان...", "filter": "فلتەر",
        "all": "هەموو", "category": "بەش", "difficulty": "ئاستی قورسی", "duration": "ماوە"
    },
    "English 🇬🇧": {
        "dashboard": "📊 Dashboard", "disease_db": "🦠 Disease Database", "lab_tests": "🧪 Laboratory Tests",
        "practical": "🔬 Practical Tests", "theory": "📚 Study Notes", "results_entry": "📝 Results Entry",
        "reports": "📈 Reports", "ai_chat": "🤖 AI Assistant", "description": "Description",
        "symptoms": "Symptoms", "causes": "Causes", "treatment": "Treatment", "severity": "Severity",
        "normal_range": "Normal Range", "critical_values": "Critical Values", "low": "Low", "high": "High",
        "unit": "Unit", "minutes": "minutes", "procedure": "Procedure Steps", "materials": "Required Materials",
        "expected_results": "Expected Results", "interpretation": "Interpretation", "precautions": "Precautions",
        "save_note": "Save Note", "saved_success": "Saved successfully! ✅", "patient_name": "Patient Name",
        "patient_age": "Age", "patient_gender": "Gender", "select_test": "Select Test",
        "result_value": "Result Value", "save_result": "Save Result", "ask_ai": "Ask AI",
        "type_question": "Type your question...", "search": "Search...", "filter": "Filter",
        "all": "All", "category": "Category", "difficulty": "Difficulty Level", "duration": "Duration"
    }
}

def t(key):
    lang = st.session_state.get("lang", "کوردی 🇹🇯")
    return translations.get(lang, translations["کوردی 🇹🇯"]).get(key, key)

# ==================== Sidebar Navigation ====================
st.sidebar.markdown("""
<div class="student-info">
    <h2>سیستەمی تاقیگەی پزیشکی</h2>
    <p>دانیال ئیسماعیل | وەشانی 2.0</p>
</div>
""", unsafe_allow_html=True)

lang_choice = st.sidebar.selectbox("Language / زمان", ["کوردی 🇹🇯", "English 🇬🇧"], key="lang")
is_ku = lang_choice == "کوردی 🇹🇯"

st.sidebar.markdown("---")
pages = {
    "dashboard": t("dashboard"),
    "diseases": t("disease_db"),
    "tests": t("lab_tests"),
    "practical": t("practical"),
    "notes": t("theory"),
    "results": t("results_entry"),
    "reports": t("reports"),
    "ai": t("ai_chat")
}

if "current_page" not in st.session_state:
    st.session_state.current_page = "dashboard"

for page_id, page_name in pages.items():
    if st.sidebar.button(page_name, key=f"btn_{page_id}", use_container_width=True):
        st.session_state.current_page = page_id

current_page = st.session_state.current_page

st.markdown(f"""
<div class="main-header">
    <h1>سیستەمی پێشکەوتووی بەڕێوەبردن و شیکردنەوەی تاقیگە</h1>
    <p>{pages[current_page]}</p>
</div>
""", unsafe_allow_html=True)

# ==================== Page Renderers ====================
def render_dashboard():
    col1, col2, col3, col4 = st.columns(4)
    
    total_tests = conn.execute("SELECT COUNT(*) as count FROM test_types").fetchone()['count']
    total_results = conn.execute("SELECT COUNT(*) as count FROM test_results").fetchone()['count']
    abnormal_results = conn.execute("SELECT COUNT(*) as count FROM test_results WHERE is_abnormal=1").fetchone()['count']
    critical_results = conn.execute("SELECT COUNT(*) as count FROM test_results WHERE is_critical=1").fetchone()['count']
        
    with col1:
        st.markdown(f'<div class="stat-card"><h3>{total_tests}</h3><p>{t("lab_tests")}</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="stat-card"><h3>{total_results}</h3><p>{t("results_entry")}</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="stat-card" style="border-right: 4px solid #ff9800;"><h3>{abnormal_results}</h3><p>ئەنجامی نائاسایی</p></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="stat-card" style="border-right: 4px solid #f44336;"><h3>{critical_results}</h3><p>مەترسی توند</p></div>', unsafe_allow_html=True)

    st.markdown("### 📈 ئاماری گشتی پشکنینەکان")
    df = pd.read_sql_query("SELECT date_performed as Date, COUNT(*) as Count FROM test_results GROUP BY date_performed", conn)
    if not df.empty:
        fig = px.line(df, x="Date", y="Count", title="تێکڕای پشکنینەکان بەپێی کات")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("هیچ داتایەک تۆمار نەکراوە بۆ پیشاندانی گرافیک.")

def render_diseases():
    search_query = st.text_input(t("search"), "")
    query = "SELECT d.*, c.name_ku as cat_ku, c.name_en as cat_en, c.icon FROM diseases d JOIN disease_categories c ON d.category_id = c.id"
    df = pd.read_sql_query(query, conn)
    
    if search_query:
        df = df[df['name_ku'].str.contains(search_query, case=False) | df['name_en'].str.contains(search_query, case=False)]
        
    for _, row in df.iterrows():
        name = row['name_ku'] if is_ku else row['name_en']
        desc = row['description_ku'] if is_ku else row['description_en']
        symptoms = row['symptoms_ku'] if is_ku else row['symptoms_en']
        treatment = row['treatment_ku'] if is_ku else row['treatment_en']
        
        st.markdown(f"""
        <div class="category-card">
            <h3>{row['icon']} {name} <span style="font-size:0.8rem; color:#666;">({row['cat_ku'] if is_ku else row['cat_en']})</span></h3>
            <p><b>{t("description")}:</b> {desc}</p>
            <p><b>{t("symptoms")}:</b> {symptoms}</p>
            <p style="color: #1565c0;"><b>{t("treatment")}:</b> {treatment}</p>
            <span class="symptom-tag">{t("severity")}: {row['severity']}</span>
        </div>
        """, unsafe_allow_html=True)

def render_tests():
    categories_query = pd.read_sql_query("SELECT DISTINCT category FROM test_types", conn)
    selected_cat = st.selectbox(t("category"), [t("all")] + list(categories_query['category'].tolist()))
    
    if selected_cat == t("all"):
        df = pd.read_sql_query("SELECT * FROM test_types", conn)
    else:
        df = pd.read_sql_query("SELECT * FROM test_types WHERE category = ?", conn, params=(selected_cat,))
        
    for _, row in df.iterrows():
        name = row['name_ku'] if is_ku else row['name_en']
        desc = row['description_ku'] if is_ku else row['description_en']
        prep = row['preparation_ku'] if is_ku else row['preparation_en']
        
        st.markdown(f"""
        <div class="info-box">
            <h4>{name} ({row['category']})</h4>
            <p><b>{t("description")}:</b> {desc}</p>
            <p><b>{t("normal_range")}:</b> <span class="normal-range">{row['normal_range_low']} - {row['normal_range_high']} {row['unit']}</span></p>
            <p><b>{t("critical_values")}:</b> <span class="critical-range">< {row['critical_low']} یان > {row['critical_high']} {row['unit']}</span></p>
            <p style="font-size:0.85rem; color:#d35400;">⚠️ <b>ئامادەکاری پێش پشکنین:</b> {prep}</p>
            <p style="font-size:0.8rem; color:#7f8c8d;">⏱️ کاتی دەرچوون: {row['turnaround_time']} | 💵 نرخ: {row['price']} $</p>
        </div>
        """, unsafe_allow_html=True)

def render_practical():
    df = pd.read_sql_query("SELECT * FROM practical_tests", conn)
    for _, row in df.iterrows():
        title = row['title_ku'] if is_ku else row['title_en']
        desc = row['description_ku'] if is_ku else row['description_en']
        steps = row['steps_ku'] if is_ku else row['steps_en']
        materials = row['materials_ku'] if is_ku else row['materials_en']
        interpretation = row['interpretation_ku'] if is_ku else row['interpretation_en']
        precautions = row['precautions_ku'] if is_ku else row['precautions_en']
        
        with st.expander(f"🔬 {title} ({row['difficulty_level']})"):
            st.markdown(f"**{t('description')}:** {desc}")
            st.markdown(f"**{t('materials')}:** {materials}")
            st.markdown(f"**{t('procedure')}:**")
            for step in steps.split('\n'):
                st.markdown(f'<div class="practical-step">{step}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="info-box"><b>{t("interpretation")}:</b> {interpretation}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="warning-box"><b>{t("precautions")}:</b> {precautions}</div>', unsafe_allow_html=True)

def render_notes():
    st.markdown("### 📝 زیادکردنی تێبینی خوێندن")
    with st.form("new_note_form"):
        topic = st.text_input("بابەت / Topic")
        category = st.text_input("بەش / Category")
        tags = st.text_input("تاگەکان / Tags")
        content = st.text_area("ناوەرۆک / Content")
        
        if st.form_submit_button(t("save_note")):
            if topic and content:
                conn.execute("INSERT INTO study_notes (topic, content, category, tags) VALUES (?, ?, ?, ?)", (topic, content, category, tags))
                conn.commit()
                st.success(t("saved_success"))
            else:
                st.error("تکایە خانەکان بە دروستی پڕ بکەرەوە.")
                
    st.markdown("---")
    notes_df = pd.read_sql_query("SELECT * FROM study_notes ORDER BY created_at DESC", conn)
    for _, row in notes_df.iterrows():
        st.markdown(f"""
        <div class="note-card">
            <h4>📌 {row['topic']} <span style="font-size:0.75rem; color:#666;">({row['category']})</span></h4>
            <p style="white-space: pre-line;">{row['content']}</p>
            <p style="font-size:0.7rem; color:#999;">📅 {row['created_at']} | 🏷️ {row['tags']}</p>
        </div>
        """, unsafe_allow_html=True)

def render_results():
    st.markdown("### 📥 تۆمارکردنی ئەنجامی پشکنین")
    tests_df = pd.read_sql_query("SELECT id, name_en, name_ku FROM test_types", conn)
    test_options = {row['id']: (row['name_ku'] if is_ku else row['name_en']) for _, row in tests_df.iterrows()}
    
    with st.form("result_form"):
        p_name = st.text_input(t("patient_name"))
        p_age = st.number_input(t("patient_age"), min_value=0, max_value=120, value=25)
        p_gender = st.selectbox(t("patient_gender"), ["Male", "Female", "Other"])
        selected_test_id = st.selectbox(t("select_test"), list(test_options.keys()), format_func=lambda x: test_options[x])
        res_value = st.number_input(t("result_value"), value=0.0, format="%.2f")
        notes = st.text_area("تێبینی")
        
        if st.form_submit_button(t("save_result")):
            test_info = conn.execute("SELECT * FROM test_types WHERE id=?", (selected_test_id,)).fetchone()
            is_abnormal = 0
            is_critical = 0
            
            if test_info['normal_range_low'] and (res_value < test_info['normal_range_low'] or res_value > test_info['normal_range_high']):
                is_abnormal = 1
            if test_info['critical_low'] and (res_value <= test_info['critical_low'] or res_value >= test_info['critical_high']):
                is_critical = 1
                
            conn.execute("""
                INSERT INTO test_results (patient_name, patient_age, patient_gender, test_id, result_value, is_abnormal, is_critical, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (p_name, p_age, p_gender, selected_test_id, res_value, is_abnormal, is_critical, notes))
            conn.commit()
            st.success(t("saved_success"))

def render_reports():
    st.markdown("### 📋 ڕاپۆرتی گشتی نەخۆشەکان")
    search_patient = st.text_input("ناوی نەخۆش بنووسە بۆ گەڕان:")
    
    if search_patient:
        df = pd.read_sql_query("""
            SELECT r.*, t.name_ku as test_ku, t.name_en as test_en, t.unit 
            FROM test_results r JOIN test_types t ON r.test_id = t.id 
            WHERE r.patient_name LIKE ?
        """, conn, params=(f"%{search_patient}%",))
    else:
        df = pd.read_sql_query("""
            SELECT r.*, t.name_ku as test_ku, t.name_en as test_en, t.unit 
            FROM test_results r JOIN test_types t ON r.test_id = t.id
        """, conn)
    
    if not df.empty:
        st.dataframe(df[['patient_name', 'patient_age', 'patient_gender', 'test_ku', 'result_value', 'unit', 'date_performed']], use_container_width=True)
    else:
        st.warning("هیچ ئەنجامێک نەدۆزرایەوە.")

def render_ai_chat():
    st.markdown(f"### {t('ai_chat')}")
    user_q = st.text_input(t("type_question"))
    if st.button(t("ask_ai")):
        if user_q:
            st.markdown(f"**🤖 وەڵام:** سەبارەت بە `{user_q}`، پێویستە هەمیشە بەهاکانی تاقیگە لەگەڵ مەودای نۆرمال (Normal Range) بەراورد بکرێن. ئەگەر بەهاکە نائاسایی بوو، ڕاوێژ بە پزیشکی پسپۆڕ بکە.")

# ==================== Application Router ====================
if conn:
    try:
        if current_page == "dashboard": render_dashboard()
        elif current_page == "diseases": render_diseases()
        elif current_page == "tests": render_tests()
        elif current_page == "practical": render_practical()
        elif current_page == "notes": render_notes()
        elif current_page == "results": render_results()
        elif current_page == "reports": render_reports()
        elif current_page == "ai": render_ai_chat()
    except Exception as e:
        st.error(f"Error executing page layout: {str(e)}")
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 8px; color: #666; font-size: 0.8rem;">
        <p>🔬 Medical Laboratory Management System | Developed by Danyal Esmael © 2026</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.error("❌ کێشە لە پەیوەستبوونی بنکەی زانیاری هەیە.")
