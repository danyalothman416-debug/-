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

    /* Fix sidebar button text */
    .stButton > button {
        font-size: 0.85rem !important;
        white-space: normal !important;
        word-wrap: break-word !important;
        text-align: right !important;
        direction: rtl !important;
    }
    
    /* Fix sidebar heading */
    .sidebar .stMarkdown h2 {
        font-size: 1.2rem !important;
    }
    
    /* Reduce MediLab Pro size */
    [data-testid="stSidebar"] h2 {
        font-size: 1.3rem !important;
    }
    
    /* Fix text colors */
    .stMarkdown, .stMarkdown p, .stMarkdown h1,
    .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, 
    .stMarkdown h5, .stMarkdown h6 {
        color: #1a1a1a !important;
    }
    
    /* Dark mode fixes */
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
    """Insert medical data into database"""
    if conn is None:
        return
        
    try:
        count = conn.execute("SELECT COUNT(*) as c FROM test_types").fetchone()
        if count['c'] > 5:
            return
            
        # Clear existing data
        conn.execute("DELETE FROM test_results")
        conn.execute("DELETE FROM practical_tests")
        conn.execute("DELETE FROM study_notes")
        conn.execute("DELETE FROM diseases")
        conn.execute("DELETE FROM test_types")
        conn.execute("DELETE FROM disease_categories")
        
        # Disease Categories
        categories = [
            ("Hematology", "خوێنناسی", 
             "Study of blood and blood disorders", 
             "لێکۆڵینەوە لە خوێن و نەخۆشییەکانی خوێن",
             "🩸", "#FF6B6B"),
            ("Clinical Chemistry", "کیمیای کلینیکی",
             "Chemical analysis of bodily fluids",
             "شیکردنەوەی کیمیایی شلەکانی لەش",
             "🧪", "#4ECDC4"),
            ("Microbiology", "مایکرۆبایۆلۆجی",
             "Study of microorganisms",
             "لێکۆڵینەوە لە مایکرۆئۆرگانیزمەکان",
             "🔬", "#45B7D1"),
            ("Immunology", "بەرگری ناسی",
             "Study of immune system",
             "لێکۆڵینەوە لە سیستەمی بەرگری",
             "🛡️", "#96CEB4"),
            ("Endocrinology", "هۆرمۆن ناسی",
             "Study of hormones",
             "لێکۆڵینەوە لە هۆرمۆنەکان",
             "⚡", "#FFEAA7"),
            ("Urinalysis", "شیکردنەوەی میز",
             "Analysis of urine samples",
             "شیکردنەوەی نموونەی میز",
             "💧", "#DDA0DD"),
            ("Coagulation", "مەیاندن",
             "Blood clotting studies",
             "لێکۆڵینەوە لە مەیاندنی خوێن",
             "🩹", "#98D8C8"),
            ("Blood Bank", "بانکی خوێن",
             "Blood transfusion services",
             "خزمەتگوزارییەکانی گواستنەوەی خوێن",
             "🏥", "#F7DC6F"),
        ]
        
        for cat in categories:
            try:
                conn.execute("""
                INSERT INTO disease_categories (name_en, name_ku, description_en, description_ku, icon, color)
                VALUES (?, ?, ?, ?, ?, ?)
                """, cat)
            except sqlite3.IntegrityError:
                pass
        
        # Test Types
        tests = [
            ("CBC", "ژمارەی تەواوی خوێن (CBC)", "Hematology", "cells/μL", 
             4.5, 11.0, 2.0, 15.0,
             "Complete Blood Count",
             "ژمارەی تەواوی خوێن",
             "No special preparation needed", "پێویستی بە ئامادەکاری تایبەت نییە", "2 hours", 25.0),
            ("Hemoglobin", "هیمۆگلۆبین (Hb)", "Hematology", "g/dL",
             12.0, 16.0, 7.0, 20.0,
             "Measures hemoglobin in blood",
             "بڕی هیمۆگلۆبین لە خوێندا دەپێورێت",
             "Fasting not required", "پێویستی بە بەڕۆژووبوون نییە", "1 hour", 15.0),
            ("WBC Count", "ژمارەی خانە سپییەکان (WBC)", "Hematology", "cells/μL",
             4000, 11000, 2000, 30000,
             "White Blood Cell count",
             "ژمارەی خانە سپییەکانی خوێن",
             "No special preparation", "پێویستی بە ئامادەکاری نییە", "1 hour", 20.0),
            ("Blood Glucose", "شەکری خوێن (FBS)", "Clinical Chemistry", "mg/dL",
             70, 100, 40, 300,
             "Measures blood sugar levels",
             "ئاستی شەکری خوێن دەپێورێت",
             "Fast for 8-12 hours", "٨-١٢ کاتژمێر بەڕۆژوو بە", "2 hours", 20.0),
            ("HbA1c", "هیمۆگلۆبینی شەکرەدار (HbA1c)", "Clinical Chemistry", "%",
             4.0, 5.6, 3.0, 12.0,
             "Average blood sugar over 3 months",
             "تێکڕای شەکری خوێن بۆ ماوەی ٣ مانگ",
             "No fasting required", "پێویستی بە بەڕۆژووبوون نییە", "4 hours", 50.0),
            ("Creatinine", "کریاتینین (Cr)", "Clinical Chemistry", "mg/dL",
             0.6, 1.2, 0.2, 5.0,
             "Kidney function test",
             "پشکنینی کاری گورچیلە",
             "Avoid heavy exercise 24h before", "٢٤ کاتژمێر پێش وەرزشی قورس مەکە", "2 hours", 25.0),
            ("Blood Urea", "یوریای خوێن (BUN)", "Clinical Chemistry", "mg/dL",
             7, 20, 3, 50,
             "Kidney function test",
             "پشکنینی کاری گورچیلە",
             "No special preparation", "پێویستی بە ئامادەکاری نییە", "2 hours", 20.0),
            ("Cholesterol Total", "کۆلیستڕۆڵی گشتی", "Clinical Chemistry", "mg/dL",
             125, 200, 100, 300,
             "Total blood cholesterol",
             "کۆی کۆلیستڕۆڵی خوێن",
             "Fast for 9-12 hours", "٩-١٢ کاتژمێر بەڕۆژوو بە", "3 hours", 35.0),
            ("ALT", "ئەلانین ئەمینۆترانسفێراز (ALT)", "Clinical Chemistry", "U/L",
             7, 56, 3, 200,
             "Liver enzyme test",
             "ئەنزیمی جگەر",
             "No special preparation", "پێویستی بە ئامادەکاری نییە", "2 hours", 25.0),
            ("AST", "ئەسپارتەیت ئەمینۆترانسفێراز (AST)", "Clinical Chemistry", "U/L",
             10, 40, 5, 200,
             "Liver and muscle enzyme test",
             "پشکنینی ئەنزیمی جگەر و ماسولکە",
             "No special preparation", "پێویستی بە ئامادەکاری نییە", "2 hours", 25.0),
            ("CRP", "پڕۆتینی کاردەر لە هەوکردن (CRP)", "Immunology", "mg/L",
             0, 5, 0, 100,
             "C-Reactive Protein",
             "پڕۆتینی کاردەر لە هەوکردن",
             "No special preparation", "پێویستی بە ئامادەکاری نییە", "2 hours", 40.0),
            ("TSH", "هۆرمۆنی چالاککەری تایرۆید (TSH)", "Endocrinology", "mIU/L",
             0.4, 4.0, 0.1, 50.0,
             "Thyroid Stimulating Hormone",
             "هۆرمۆنی چالاککەری تایرۆید",
             "Morning sample preferred", "نموونەی بەیانی باشترە", "3 hours", 60.0),
            ("Urine pH", "ترشێتی میز (pH)", "Urinalysis", "pH",
             4.5, 8.0, 4.0, 9.0,
             "Measures acidity of urine",
             "ترشێتی میز دەپێورێت",
             "Fresh sample required", "نموونەی تازە پێویستە", "30 minutes", 10.0),
            ("PT", "کاتی پڕۆترۆمبین (PT)", "Coagulation", "seconds",
             11, 13.5, 9, 30,
             "Prothrombin Time",
             "کاتی پڕۆترۆمبین",
             "Avoid anticoagulants if possible", "دژە مەیاندنەکان بەکارمەهێنە", "2 hours", 35.0),
            ("HBsAg", "دژەپەیداکەری ڤایرۆسی هەوکردنی جگەر B", "Serology", "qualitative",
             0, 0, 0, 1,
             "Hepatitis B surface antigen test",
             "پشکنینی دژەپەیداکەری ڤایرۆسی هەوکردنی جگەری جۆری B",
             "No special preparation", "پێویستی بە ئامادەکاری نییە", "4 hours", 50.0),
        ]
        
        for test in tests:
            try:
                conn.execute("""
                INSERT INTO test_types 
                (name_en, name_ku, category, unit, normal_range_low, normal_range_high, 
                 critical_low, critical_high, description_en, description_ku,
                 preparation_en, preparation_ku, turnaround_time, price)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, test)
            except sqlite3.IntegrityError:
                pass
        
        # Diseases
        diseases_data = [
            (1, "Iron Deficiency Anemia", "کەمخوێنی بەهۆی کەمی ئاسن",
             "Most common type of anemia caused by insufficient iron",
             "باوباپترین جۆری کەمخوێنی بەهۆی کەمی ئاسنەوە",
             "Fatigue, Weakness, Pale skin, Shortness of breath, Dizziness",
             "ماندووبوون، لاوازی، پێستی کاڵ، هەناسە توندی، سەرگێژە",
             "Poor diet, Blood loss, Pregnancy",
             "خواردنی خراپ، لەدەستدانی خوێن، دووگیانی",
             "Iron supplements, Iron-rich diet",
             "تەواوکەری ئاسن، خواردنی دەوڵەمەند بە ئاسن",
             "Mild to Severe"),
            (2, "Diabetes Mellitus Type 1", "شەکرەی جۆری ١",
             "Autoimmune destruction of insulin-producing cells",
             "تێکدانی خۆبەرگری خانەکانی بەرهەمهێنەری ئینسولین",
             "Frequent urination, Excessive thirst, Weight loss, Fatigue",
             "میزی زۆر، تینویەتی زۆر، دابەزینی کێش، ماندووبوون",
             "Autoimmune reaction, Genetic factors",
             "کارلێکی خۆبەرگری، هۆکارە بۆماوەییەکان",
             "Insulin therapy, Diet control",
             "چارەسەری ئینسولین، کۆنتڕۆڵی خواردن",
             "Moderate to Severe"),
            (2, "Diabetes Mellitus Type 2", "شەکرەی جۆری ٢",
             "Insulin resistance and relative insulin deficiency",
             "بەرگری ئینسولین و کەمی ڕێژەیی ئینسولین",
             "Slow-healing wounds, Numbness, Blurred vision, Fatigue",
             "برینەکانی بە هێواشی چاکدەبنەوە، کڕێتی، تەمومژی بینین، ماندووبوون",
             "Obesity, Sedentary lifestyle, Genetic factors",
             "قەڵەوی، ژیانی بێ جوڵە، هۆکارە بۆماوەییەکان",
             "Oral medications, Diet, Exercise",
             "دەرمانی دەم، ڕێجیم، وەرزش",
             "Moderate"),
            (3, "Urinary Tract Infection", "هەوکردنی ڕێڕەوی میز",
             "Bacterial infection of urinary system",
             "هەوکردنی بەکتریایی سیستەمی میز",
             "Burning urination, Frequent urination, Cloudy urine, Pelvic pain",
             "میزکردنی سووتێنەر، میزکردنی زۆر، میزی تەمومژاوی، ئازاری لەگەنە",
             "E. coli bacteria, Poor hygiene",
             "بەکتریای ئیکۆلای، پاکژی خراپ",
             "Antibiotics, Increased fluids",
             "دژەبەکتریاکان، شلەی زیاتر",
             "Mild to Moderate"),
            (4, "Rheumatoid Arthritis", "هەوکردنی جومگەکانی ڕۆماتیزمی",
             "Autoimmune disease causing joint inflammation",
             "نەخۆشی خۆبەرگری دەبێتە هۆی هەوکردنی جومگەکان",
             "Joint pain, Morning stiffness, Fatigue, Fever",
             "ئازاری جومگەکان، ڕەقبوونی بەیانیان، ماندووبوون، تا",
             "Autoimmune reaction, Genetic factors",
             "کارلێکی خۆبەرگری، هۆکارە بۆماوەییەکان",
             "NSAIDs, Steroids, DMARDs",
             "دژەهەوکردنەکان، سترۆیدەکان، دەرمانە دژە ڕۆماتیزمییەکان",
             "Moderate to Severe"),
            (5, "Hypothyroidism", "کەمکاری تایرۆید",
             "Underactive thyroid gland",
             "کەمکاری ڕژێنی تایرۆید",
             "Weight gain, Cold intolerance, Fatigue, Depression, Dry skin",
             "زیادبوونی کێش، نەتوانینی بەرگەی سەرما، ماندووبوون، خەمۆکی، پێستی وشک",
             "Autoimmune disease, Iodine deficiency",
             "نەخۆشی خۆبەرگری، کەمی یۆد",
             "Levothyroxine replacement therapy",
             "چارەسەری جێگرەوەی لیڤۆتایرۆکسین",
             "Moderate"),
        ]
        
        for disease in diseases_data:
            try:
                conn.execute("""
                INSERT INTO diseases 
                (category_id, name_en, name_ku, description_en, description_ku,
                 symptoms_en, symptoms_ku, causes_en, causes_ku, treatment_en, treatment_ku, severity)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, disease)
            except sqlite3.IntegrityError:
                pass
        
        # Practical Tests
        practicals = [
            ("Blood Smear Preparation", "ئامادەکردنی سمێری خوێن",
             "Preparation and staining of blood smear",
             "ئامادەکردن و ڕەنگکردنی سمێری خوێن",
             "Hematology",
             "1. Clean slide with alcohol\n2. Place small drop of blood\n3. Use spreader slide at 30-45° angle\n4. Quick smooth motion to spread\n5. Air dry completely\n6. Fix with methanol\n7. Stain with Wright's stain\n8. Wash and dry\n9. Examine under microscope",
             "١. سلاید بە ئەلکحول پاک بکەرەوە\n٢. دڵۆپێکی بچووکی خوێن دابنێ\n٣. سلایدی بڵاوکەرەوە بە گۆشەی ٣٠-٤٥ پلە بەکاربهێنە\n٤. بە جوڵەیەکی خێرا و نەرم بیبڵاوە\n٥. بە تەواوی وشک بکەرەوە\n٦. بە میسانۆل جێگیر بکە\n٧. بە ڕەنگی رایت ڕەنگی بکە\n٨. بیشۆ و وشکی بکەرەوە\n٩. لە ژێر مایکرۆسکۆپ پشکنین بکە",
             "Glass slides, Blood sample, Spreader slide, Methanol, Wright's stain, Microscope",
             "سلایدی شووشەیی، نموونەی خوێن، سلایدی بڵاوکەرەوە، میسانۆل، ڕەنگی رایت، مایکرۆسکۆپ",
             "Evenly distributed blood cells",
             "خانەکانی خوێن بە یەکسانی بڵاوکراونەتەوە",
             "Check RBC morphology, WBC differential",
             "شێوەی خڕۆکە سوورەکان، جیاکاری خانە سپییەکان",
             "Avoid air bubbles, Use fresh blood",
             "دوورکەوتنەوە لە بڵقەکانی هەوا، بەکارهێنانی خوێنی تازە",
             30, "Basic"),
            ("Gram Staining", "ڕەنگکردنی گرام",
             "Differential staining technique for bacteria",
             "تەکنیکی ڕەنگکردنی جیاکار بۆ پۆلێنکردنی بەکتریا",
             "Microbiology",
             "1. Prepare bacterial smear\n2. Heat fix\n3. Crystal violet - 1 minute\n4. Wash with water\n5. Gram's iodine - 1 minute\n6. Wash with water\n7. Decolorize with alcohol\n8. Wash immediately\n9. Safranin counterstain - 30 sec\n10. Wash, dry, examine",
             "١. سمێری بەکتریا ئامادە بکە\n٢. بە گەرمی جێگیر بکە\n٣. کریستاڵ ڤایۆلێت - ١ خولەک\n٤. بە ئاو بیشۆ\n٥. یۆدی گرام - ١ خولەک\n٦. بە ئاو بیشۆ\n٧. بە ئەلکحول ڕەنگ لێ بەرەوە\n٨. یەکسەر بیشۆ\n٩. سەفرانین - ٣٠ چرکە\n١٠. بیشۆ، وشک بکەرەوە، پشکنین بکە",
             "Bacterial culture, Crystal violet, Iodine, Alcohol, Safranin, Microscope",
             "کەلتووری بەکتریا، کریستاڵ ڤایۆلێت، یۆد، ئەلکحول، سەفرانین، مایکرۆسکۆپ",
             "Gram-positive: Purple, Gram-negative: Pink/Red",
             "گرام پۆزەتیڤ: وەنەوشەیی، گرام نێگەتیڤ: پەمەیی/سوور",
             "Bacterial classification",
             "پۆلێنکردنی بەکتریا",
             "Don't over-decolorize, Use fresh cultures",
             "زۆر ڕەنگ لێ مەبەرەوە، کەلتووری تازە بەکاربهێنە",
             45, "Intermediate"),
            ("Urine Dipstick Analysis", "شیکردنەوەی دیپستیکی میز",
             "Rapid screening test for urine",
             "پشکنینی خێرای پشکنین بۆ پێکهاتەکانی میز",
             "Urinalysis",
             "1. Collect fresh urine sample\n2. Dip test strip briefly\n3. Remove excess urine\n4. Compare to color chart\n5. Record results",
             "١. نموونەی میزی تازە کۆبکەرەوە\n٢. شریتی پشکنین بە کورتی نوقم بکە\n٣. میزی زیادە لابەرە\n٤. بەراورد بە هێڵکاری ڕەنگەکان\n٥. ئەنجامەکان تۆمار بکە",
             "Urine sample, Dipstick strips, Color chart, Timer",
             "نموونەی میز، شریتەکانی دیپستیک، هێڵکاری ڕەنگ، کاتژمێر",
             "Color changes indicating urine components",
             "گۆڕانی ڕەنگەکان پێکهاتە جیاوازەکانی میز نیشان دەدات",
             "pH, Protein, Glucose, Ketones, Blood",
             "ترشێتی، پرۆتین، شەکر، کیتۆنەکان، خوێن",
             "Check expiration date, Proper timing",
             "بەرواری بەسەرچوون بپشکنە، کاتی گونجاو",
             15, "Basic"),
            ("Blood Group Testing", "پشکنینی گروپی خوێن",
             "ABO and Rh blood group determination",
             "دیاریکردنی گروپی خوێنی ABO و Rh",
             "Blood Bank",
             "1. Prepare clean slide with 3 sections\n2. Add anti-A, anti-B, anti-D reagents\n3. Add blood drop to each section\n4. Mix with clean stick\n5. Rock slide gently\n6. Observe agglutination within 2 minutes",
             "١. سلایدی پاک بە ٣ بەش ئامادە بکە\n٢. کارلێککەرەکانی دژە-A، دژە-B، دژە-D زیاد بکە\n٣. دڵۆپەی خوێن بۆ هەر بەشێک زیاد بکە\n٤. بە داری پاک تێکەڵ بکە\n٥. سلایدەکە بە نەرمی بجوڵێنە\n٦. چڕبوونەوە لە ماوەی ٢ خولەکدا چاودێری بکە",
             "Clean slide, Anti-A, Anti-B, Anti-D reagents, Blood sample, Mixing sticks",
             "سلایدی پاک، کارلێککەری دژە-A، دژە-B، دژە-D، نموونەی خوێن، داری تێکەڵکردن",
             "Agglutination pattern determines blood group",
             "شێوازی چڕبوونەوە گروپی خوێن دیاری دەکات",
             "A, B, AB, O groups with Rh positive/negative",
             "گروپەکانی A، B، AB، O لەگەڵ Rh پۆزەتیڤ/نێگەتیڤ",
             "Use fresh blood, Check reagent expiry",
             "خوێنی تازە بەکاربهێنە، بەرواری بەسەرچوونی کارلێککەر بپشکنە",
             20, "Basic")
        ]
        
        for practical in practicals:
            try:
                conn.execute("""
                INSERT INTO practical_tests 
                (title_en, title_ku, description_en, description_ku, category,
                 steps_en, steps_ku, materials_en, materials_ku,
                 expected_results_en, expected_results_ku,
                 interpretation_en, interpretation_ku,
                 precautions_en, precautions_ku,
                 duration_minutes, difficulty_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, practical)
            except sqlite3.IntegrityError:
                pass
        
        # Study Notes
        notes = [
            ("Hematology Basics", "CBC Interpretation:\n\nRBC: 4.5-5.5 million/μL\nWBC: 4,000-11,000/μL\nPlatelets: 150,000-450,000/μL\nHemoglobin: 12-16 g/dL\nHematocrit: 37-47%", "Hematology", "CBC, blood, basic"),
            ("Diabetes Diagnosis", "Diagnostic criteria:\n\nFBS ≥ 126 mg/dL\nHbA1c ≥ 6.5%\nOGTT 2-hour ≥ 200 mg/dL\nRandom glucose ≥ 200 mg/dL with symptoms", "Clinical Chemistry", "diabetes, glucose, diagnosis"),
            ("Gram Staining Principle", "Gram-positive bacteria: Thick peptidoglycan layer retains crystal violet\n\nGram-negative bacteria: Thin peptidoglycan, outer membrane, lose crystal violet", "Microbiology", "gram stain, bacteria"),
        ]
        
        for note in notes:
            conn.execute("""
            INSERT INTO study_notes (topic, content, category, tags)
            VALUES (?, ?, ?, ?)
            """, note)
        
        conn.commit()
        
    except Exception as e:
        conn.rollback()

# Insert data
insert_comprehensive_data(conn)

# ==================== Translation System ====================

def t(key):
    """Translation system"""
    translations = {
        "کوردی 🇹🇯": {
            "dashboard": "📊 داشبۆرد",
            "disease_db": "🦠 نەخۆشییەکان",
            "lab_tests": "🧪 پشکنینەکان", 
            "practical": "🔬 پراکتیکی",
            "theory": "📚 تێبینییەکان",
            "results_entry": "📝 ئەنجامەکان",
            "reports": "📈 ڕاپۆرت",
            "ai_chat": "🤖 زیرەکی دەستکرد",
            "description": "ڕوونکردنەوە",
            "symptoms": "نیشانەکان",
            "causes": "هۆکارەکان",
            "treatment": "چارەسەر",
            "severity": "توندی",
            "normal_range": "مەودای ئاسایی",
            "critical_values": "بەهای مەترسیدار",
            "low": "نزم",
            "high": "بەرز", 
            "unit": "یەکە",
            "minutes": "خولەک",
            "procedure": "هەنگاوەکان",
            "materials": "کەرەستەکان",
            "expected_results": "ئەنجامی چاوەڕوانکراو",
            "interpretation": "لێکدانەوە",
            "precautions": "پێشگیریکردنەکان",
            "save_note": "تۆمارکردن",
            "saved_success": "بەسەرکەوتوویی تۆمارکرا! ✅",
            "patient_name": "ناوی نەخۆش",
            "patient_age": "تەمەن",
            "patient_gender": "ڕەگەز",
            "select_test": "پشکنین هەڵبژێرە",
            "result_value": "ئەنجام",
            "save_result": "تۆمارکردنی ئەنجام",
            "ask_ai": "پرسیار بکە",
            "type_question": "پرسیارەکەت بنووسە...",
            "search": "گەڕان...",
            "filter": "فلتەر",
            "all": "هەموو",
            "export": "هەناردەکردن",
            "print": "چاپکردن",
            "delete": "سڕینەوە",
            "edit": "دەستکاری",
            "view": "بینین",
            "details": "وردەکارییەکان",
            "category": "بەش",
            "difficulty": "ئاستی قورسی",
            "duration": "ماوە",
        },
        "English 🇬🇧": {
            "dashboard": "📊 Dashboard",
            "disease_db": "🦠 Disease Database",
            "lab_tests": "🧪 Laboratory Tests",
            "practical": "🔬 Practical Tests",
            "theory": "📚 Study Notes",
            "results_entry": "📝 Results Entry",
            "reports": "📈 Reports",
            "ai_chat": "🤖 AI Assistant",
            "description": "Description",
            "symptoms": "Symptoms",
            "causes": "Causes",
            "treatment": "Treatment",
            "severity": "Severity",
            "normal_range": "Normal Range",
            "critical_values": "Critical Values",
            "low": "Low",
            "high": "High",
            "unit": "Unit",
            "minutes": "minutes",
            "procedure": "Procedure Steps",
            "materials": "Required Materials",
            "expected_results": "Expected Results",
            "interpretation": "Interpretation",
            "precautions": "Precautions",
            "save_note": "Save Note",
            "saved_success": "Saved successfully! ✅",
            "patient_name": "Patient Name",
            "patient_age": "Age",
            "patient_gender": "Gender",
            "select_test": "Select Test",
            "result_value": "Result Value",
            "save_result": "Save Result",
            "ask_ai": "Ask AI",
            "type_question": "Type your question...",
            "search": "Search...",
            "filter": "Filter",
            "all": "All",
            "export": "Export",
            "print": "Print",
            "delete": "Delete",
            "edit": "Edit",
            "view": "View",
            "details": "Details",
            "category": "Category",
            "difficulty": "Difficulty Level",
            "duration": "Duration",
        }
    }
    
    lang = st.session_state.get("language", "کوردی 🇹🇯")
    return translations.get(lang, {}).get(key, key)

def get_name(row, prefix="name"):
    """Get localized name from database row"""
    lang_map = {
        "English 🇬🇧": "en",
        "کوردی 🇹🇯": "ku"
    }
    lang = lang_map.get(st.session_state.get("language", "کوردی 🇹🇯"), "ku")
    field = f"{prefix}_{lang}"
    
    if isinstance(row, dict):
        return row.get(field, row.get(f"{prefix}_en", ""))
    else:
        try:
            return row[field]
        except:
            try:
                return row[f"{prefix}_en"]
            except:
                return str(row)

def get_desc(row):
    """Get localized description"""
    return get_name(row, "description")

# ==================== AI Responses ====================

def get_ai_response(question):
    """Get AI response for medical questions"""
    q = question.lower()
    
    if "cbc" in q or "complete blood count" in q:
        return """**CBC (Complete Blood Count)** is a comprehensive blood test that measures:
        - **Red Blood Cells (RBC)**: Oxygen carriers (4.5-5.5 million/μL)
        - **White Blood Cells (WBC)**: Immune system cells (4,000-11,000/μL)
        - **Hemoglobin**: Oxygen-carrying protein (12-16 g/dL)
        - **Hematocrit**: Percentage of red blood cells (37-47%)
        - **Platelets**: Blood clotting cells (150,000-450,000/μL)
        
        Normal ranges vary by age and gender. Always consult your healthcare provider for interpretation."""
    
    elif "glucose" in q or "sugar" in q or "diabetes" in q:
        return """**Blood Glucose Test** measures blood sugar levels:
        - **Fasting**: 70-100 mg/dL (normal)
        - **Pre-diabetes**: 100-125 mg/dL
        - **Diabetes**: 126 mg/dL or higher
        
        **HbA1c** provides 3-month average:
        - Normal: Below 5.7%
        - Pre-diabetes: 5.7-6.4%
        - Diabetes: 6.5% or higher"""
    
    elif "anemia" in q or "hemoglobin" in q:
        return """**Anemia** is a condition where you lack enough healthy red blood cells:
        
        Common types:
        - **Iron Deficiency Anemia**: Most common, caused by insufficient iron
        - **Vitamin B12 Deficiency**: Pernicious anemia
        - **Thalassemia**: Genetic disorder affecting hemoglobin
        
        Symptoms: Fatigue, weakness, pale skin, shortness of breath"""
    
    return "Please ask a medical laboratory related question. I can help with test interpretation, disease information, and lab procedures."

# ==================== Dashboard ====================

def render_dashboard():
    """Dashboard page"""
    if conn is None:
        st.error("❌ Database connection failed")
        return
        
    st.markdown("""
    <div class="main-header">
        <h1>📊 داشبۆرد</h1>
        <p>Overview of Medical Laboratory System</p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            cat_count = conn.execute("SELECT COUNT(*) as c FROM disease_categories").fetchone()['c']
            st.markdown(f"""
            <div class="stat-card">
                <h2 style="color: #FF6B6B;">{cat_count}</h2>
                <p>📂 Categories</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            test_count = conn.execute("SELECT COUNT(*) as c FROM test_types").fetchone()['c']
            st.markdown(f"""
            <div class="stat-card">
                <h2 style="color: #4ECDC4;">{test_count}</h2>
                <p>🧪 Lab Tests</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col3:
            disease_count = conn.execute("SELECT COUNT(*) as c FROM diseases").fetchone()['c']
            st.markdown(f"""
            <div class="stat-card">
                <h2 style="color: #45B7D1;">{disease_count}</h2>
                <p>🦠 Diseases</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col4:
            practical_count = conn.execute("SELECT COUNT(*) as c FROM practical_tests").fetchone()['c']
            st.markdown(f"""
            <div class="stat-card">
                <h2 style="color: #96CEB4;">{practical_count}</h2>
                <p>🔬 Practical Tests</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Tests by Category")
            
            test_dist = conn.execute("""
                SELECT category, COUNT(*) as count 
                FROM test_types 
                GROUP BY category
                ORDER BY count DESC
            """).fetchall()
            
            if test_dist:
                df_dist = pd.DataFrame([dict(r) for r in test_dist])
                fig = px.pie(df_dist, values='count', names='category',
                           color_discrete_sequence=px.colors.qualitative.Set3)
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(height=350)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 🦠 Disease Severity")
            
            severity_data = conn.execute("""
                SELECT severity, COUNT(*) as count 
                FROM diseases 
                GROUP BY severity
            """).fetchall()
            
            if severity_data:
                df_severity = pd.DataFrame([dict(r) for r in severity_data])
                fig = px.bar(df_severity, x='severity', y='count',
                           color='severity',
                           color_discrete_sequence=px.colors.qualitative.Set2)
                fig.update_layout(height=350)
                st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Dashboard Error: {str(e)}")

# ==================== Diseases Module ====================

def render_diseases():
    """Disease database page"""
    if conn is None:
        return
        
    st.markdown("""
    <div class="main-header">
        <h1>🦠 نەخۆشییەکان</h1>
        <p>Medical Disease Database</p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            search_query = st.text_input(t('search'), placeholder="Search diseases...")
        
        with col2:
            categories = conn.execute("SELECT id, name_en, name_ku FROM disease_categories").fetchall()
            category_options = {"All": None}
            for cat in categories:
                name = get_name(dict(cat))
                category_options[name] = cat['id']
            
            selected_category = st.selectbox(t('filter'), list(category_options.keys()))
        
        query = """
            SELECT d.*, dc.name_en as cat_en, dc.name_ku as cat_ku, dc.icon, dc.color
            FROM diseases d
            JOIN disease_categories dc ON d.category_id = dc.id
            WHERE 1=1
        """
        params = []
        
        if search_query:
            query += " AND (d.name_en LIKE ? OR d.name_ku LIKE ? OR d.symptoms_en LIKE ? OR d.symptoms_ku LIKE ?)"
            search_term = f"%{search_query}%"
            params.extend([search_term, search_term, search_term, search_term])
        
        if category_options[selected_category]:
            query += " AND d.category_id = ?"
            params.append(category_options[selected_category])
        
        query += " ORDER BY d.severity DESC, d.name_en"
        
        diseases = conn.execute(query, params).fetchall()
        
        st.markdown(f"### Found: {len(diseases)} diseases")
        
        for i in range(0, len(diseases), 2):
            cols = st.columns(2)
            
            for j in range(2):
                if i + j < len(diseases):
                    disease = dict(diseases[i + j])
                    
                    with cols[j]:
                        with st.container():
                            st.markdown(f"""
                            <div class="category-card" style="border-right-color: {disease.get('color', '#1565c0')};">
                                <h4>{disease.get('icon', '🦠')} {get_name(disease)}</h4>
                                <p><strong>{t('category')}:</strong> {get_name(disease, 'cat')}</p>
                                <p><strong>{t('severity')}:</strong> {disease['severity']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            with st.expander(f"{t('details')} - {get_name(disease)}"):
                                st.markdown(f"#### {t('description')}")
                                st.write(get_desc(disease))
                                
                                st.markdown(f"#### {t('symptoms')}")
                                symptoms = get_name(disease, 'symptoms')
                                if symptoms:
                                    symptom_list = [s.strip() for s in symptoms.split(',') if s.strip()]
                                    for s in symptom_list:
                                        st.markdown(f"<span class='symptom-tag'>{s}</span>", 
                                                  unsafe_allow_html=True)
                                
                                if disease.get('causes_en') or disease.get('causes_ku'):
                                    st.markdown(f"#### {t('causes')}")
                                    st.write(get_name(disease, 'causes'))
                                
                                if disease.get('treatment_en') or disease.get('treatment_ku'):
                                    st.markdown(f"#### {t('treatment')}")
                                    st.write(get_name(disease, 'treatment'))
                                
    except Exception as e:
        st.error(f"Disease Database Error: {str(e)}")

# ==================== Tests Module ====================

def render_tests():
    """Laboratory tests page"""
    if conn is None:
        return
        
    st.markdown("""
    <div class="main-header">
        <h1>🧪 پشکنینەکان</h1>
        <p>Laboratory Test Reference Guide</p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            search_test = st.text_input(t('search'), placeholder="Search by name or category...")
        
        with col2:
            categories = conn.execute("SELECT DISTINCT category FROM test_types ORDER BY category").fetchall()
            category_list = ["All"] + [c['category'] for c in categories]
            selected_cat = st.selectbox(t('category'), category_list)
        
        with col3:
            sort_by = st.selectbox("Sort by", ["Name", "Category", "Price"])
        
        query = "SELECT * FROM test_types WHERE 1=1"
        params = []
        
        if search_test:
            query += " AND (name_en LIKE ? OR name_ku LIKE ? OR category LIKE ?)"
            search_term = f"%{search_test}%"
            params.extend([search_term, search_term, search_term])
        
        if selected_cat != "All":
            query += " AND category = ?"
            params.append(selected_cat)
        
        if sort_by == "Name":
            query += " ORDER BY name_en"
        elif sort_by == "Category":
            query += " ORDER BY category, name_en"
        elif sort_by == "Price":
            query += " ORDER BY price"
        
        tests = conn.execute(query, params).fetchall()
        
        st.markdown(f"### Found: {len(tests)} tests")
        
        tests_by_category = {}
        for test in tests:
            cat = test['category']
            if cat not in tests_by_category:
                tests_by_category[cat] = []
            tests_by_category[cat].append(dict(test))
        
        for category, category_tests in tests_by_category.items():
            with st.expander(f"📁 {category} ({len(category_tests)} tests)", expanded=True):
                for test in category_tests:
                    st.markdown(f"""
                    <div class="info-box">
                        <h4>📊 {get_name(test)}</h4>
                        <p><strong>{t('unit')}:</strong> {test['unit']} | 
                        <strong>Price:</strong> ${test.get('price', 'N/A')} | 
                        <strong>Turnaround:</strong> {test.get('turnaround_time', 'N/A')}</p>
                        <p><strong class="normal-range">{t('normal_range')}: {test['normal_range_low']} - {test['normal_range_high']} {test['unit']}</strong></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    with st.expander(f"More details for {get_name(test)}"):
                        st.markdown(f"#### {t('description')}")
                        st.write(get_desc(test))
                        
                        if test.get('preparation_en') or test.get('preparation_ku'):
                            st.markdown(f"#### Patient Preparation")
                            st.info(get_name(test, 'preparation'))
                        
                        st.markdown(f"#### {t('critical_values')}")
                        
                        st.markdown(f"""
                        <div class="critical-box">
                            <p>🔴 <strong>{t('low')}:</strong> < {test['critical_low']} {test['unit']}</p>
                            <p>🔴 <strong>{t('high')}:</strong> > {test['critical_high']} {test['unit']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
    except Exception as e:
        st.error(f"Tests Display Error: {str(e)}")

# ==================== Practical Tests Module ====================

def render_practical():
    """Practical tests page"""
    if conn is None:
        return
        
    st.markdown("""
    <div class="main-header">
        <h1>🔬 پراکتیکی</h1>
        <p>Laboratory Practical Tests & Procedures</p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            categories = conn.execute("SELECT DISTINCT category FROM practical_tests ORDER BY category").fetchall()
            cat_list = ["All"] + [c['category'] for c in categories]
            selected_cat = st.selectbox(t('category'), cat_list)
        
        with col2:
            difficulty = st.selectbox(t('difficulty'), ["All", "Basic", "Intermediate", "Advanced"])
        
        with col3:
            search_practical = st.text_input(t('search'), placeholder="Search practical tests...")
        
        query = "SELECT * FROM practical_tests WHERE 1=1"
        params = []
        
        if selected_cat != "All":
            query += " AND category = ?"
            params.append(selected_cat)
        
        if difficulty != "All":
            query += " AND difficulty_level = ?"
            params.append(difficulty)
        
        if search_practical:
            query += " AND (title_en LIKE ? OR title_ku LIKE ?)"
            search_term = f"%{search_practical}%"
            params.extend([search_term, search_term])
        
        query += " ORDER BY difficulty_level, title_en"
        
        practicals = conn.execute(query, params).fetchall()
        
        st.markdown(f"### Found: {len(practicals)} practical tests")
        
        for i, practical in enumerate(practicals):
            p = dict(practical)
            
            difficulty_color = {
                "Basic": "green",
                "Intermediate": "orange",
                "Advanced": "red"
            }.get(p['difficulty_level'], "blue")
            
            st.markdown(f"""
            <div class="category-card">
                <h4>🔬 {get_name(p, 'title')}</h4>
                <p>
                    <span style="background: {difficulty_color}; color: white; padding: 2px 10px; border-radius: 10px; font-size: 0.8em;">
                        {p['difficulty_level']}
                    </span>
                    <span style="margin-left: 10px;">⏱️ {p['duration_minutes']} {t('minutes')}</span>
                    <span style="margin-left: 10px;">📁 {p['category']}</span>
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander(f"{t('details')} - {get_name(p, 'title')}"):
                st.markdown(f"#### {t('description')}")
                st.write(get_desc(p))
                
                st.markdown(f"#### {t('procedure')}")
                steps = get_name(p, 'steps')
                if steps:
                    step_list = steps.split('\n')
                    for j, step in enumerate(step_list, 1):
                        if step.strip():
                            st.markdown(f"""
                            <div class="practical-step">
                                <span class="step-number">{j}</span> {step.strip()}
                            </div>
                            """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"#### {t('materials')}")
                    materials = get_name(p, 'materials')
                    if materials:
                        mat_list = [m.strip() for m in materials.split(',')]
                        for mat in mat_list:
                            if mat:
                                st.markdown(f"- {mat}")
                    
                    st.markdown(f"#### {t('expected_results')}")
                    st.write(get_name(p, 'expected_results'))
                
                with col2:
                    st.markdown(f"#### {t('interpretation')}")
                    st.write(get_name(p, 'interpretation'))
                    
                    st.markdown(f"#### {t('precautions')}")
                    precautions = get_name(p, 'precautions')
                    if precautions:
                        st.warning(precautions)
                
    except Exception as e:
        st.error(f"Practical Tests Error: {str(e)}")

# ==================== Study Notes Module ====================

def render_notes():
    """Study notes page"""
    if conn is None:
        return
        
    st.markdown("""
    <div class="main-header">
        <h1>📚 تێبینییەکان</h1>
        <p>Laboratory Theory & Study Notes</p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        with st.expander("➕ Add New Note"):
            with st.form("add_note_form"):
                topic = st.text_input("Topic")
                content = st.text_area("Content", height=150)
                category = st.selectbox("Category", ["Hematology", "Clinical Chemistry", "Microbiology", 
                                                     "Immunology", "Endocrinology", "Urinalysis", 
                                                     "Coagulation", "Blood Bank", "General"])
                tags = st.text_input("Tags (comma separated)")
                
                if st.form_submit_button(t('save_note')):
                    if topic and content:
                        conn.execute("""
                        INSERT INTO study_notes (topic, content, category, tags)
                        VALUES (?, ?, ?, ?)
                        """, (topic, content, category, tags))
                        conn.commit()
                        st.success(t('saved_success'))
                        st.rerun()
                    else:
                        st.error("Please fill in topic and content")
        
        search_note = st.text_input(t('search'), placeholder="Search notes...")
        
        query = "SELECT * FROM study_notes WHERE 1=1"
        params = []
        
        if search_note:
            query += " AND (topic LIKE ? OR content LIKE ? OR tags LIKE ?)"
            search_term = f"%{search_note}%"
            params.extend([search_term, search_term, search_term])
        
        query += " ORDER BY updated_at DESC"
        
        notes = conn.execute(query, params).fetchall()
        
        st.markdown(f"### Found: {len(notes)} notes")
        
        for note in notes:
            n = dict(note)
            
            with st.expander(f"📝 {n['topic']} ({n['category']})"):
                st.markdown(f"""
                <div class="note-card">
                    <p><strong>Category:</strong> {n['category']}</p>
                    <p><strong>Created:</strong> {n['created_at']}</p>
                    <p><strong>Tags:</strong> {n['tags']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("### Content")
                st.markdown(n['content'])
                
                if st.button(f"🗑️ {t('delete')}", key=f"del_{n['id']}"):
                    conn.execute("DELETE FROM study_notes WHERE id = ?", (n['id'],))
                    conn.commit()
                    st.rerun()
                
    except Exception as e:
        st.error(f"Study Notes Error: {str(e)}")

# ==================== Results Entry ====================

def render_results():
    """Results entry page"""
    if conn is None:
        return
        
    st.markdown("""
    <div class="main-header">
        <h1>📝 ئەنجامەکان</h1>
        <p>Enter Laboratory Test Results</p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### Patient Information")
            
            with st.form("result_form"):
                name = st.text_input(t('patient_name'), placeholder="Enter patient full name")
                
                col_age, col_gender = st.columns(2)
                with col_age:
                    age = st.number_input(t('patient_age'), min_value=0, max_value=120, value=30)
                with col_gender:
                    gender = st.selectbox(t('patient_gender'), ["Male", "Female", "Other"])
                
                st.markdown("### Test Selection")
                
                test_categories = conn.execute("SELECT DISTINCT category FROM test_types ORDER BY category").fetchall()
                
                selected_category = st.selectbox("Test Category", 
                                               ["Select Category..."] + [c['category'] for c in test_categories])
                
                if selected_category != "Select Category...":
                    tests_in_category = conn.execute("""
                        SELECT id, name_en, name_ku, unit, normal_range_low, normal_range_high, 
                               critical_low, critical_high, price
                        FROM test_types 
                        WHERE category = ?
                        ORDER BY name_en
                    """, (selected_category,)).fetchall()
                    
                    test_options = {}
                    for t in tests_in_category:
                        td = dict(t)
                        test_options[f"{get_name(td)} ({td['unit']})"] = td
                    
                    selected_test_name = st.selectbox(t('select_test'), list(test_options.keys()))
                    
                    if selected_test_name:
                        selected_test = test_options[selected_test_name]
                        
                        st.markdown(f"""
                        <div class="info-box">
                            <p><strong>Normal Range:</strong> {selected_test['normal_range_low']} - {selected_test['normal_range_high']} {selected_test['unit']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        result_value = st.number_input(
                            f"{t('result_value')} ({selected_test['unit']})",
                            step=0.01,
                            format="%.2f"
                        )
                        
                        notes = st.text_area("Additional Notes", placeholder="Any observations...")
                        
                        submitted = st.form_submit_button(t('save_result'), use_container_width=True)
                        
                        if submitted:
                            if not name:
                                st.error("Please enter patient name")
                            elif selected_category == "Select Category...":
                                st.error("Please select a test category")
                            else:
                                is_abnormal = 0
                                is_critical = 0
                                
                                if result_value < selected_test['normal_range_low'] or result_value > selected_test['normal_range_high']:
                                    is_abnormal = 1
                                    
                                if result_value < selected_test['critical_low'] or result_value > selected_test['critical_high']:
                                    is_critical = 1
                                
                                conn.execute("""
                                    INSERT INTO test_results 
                                    (patient_name, patient_age, patient_gender, test_id, 
                                     result_value, is_abnormal, is_critical, notes)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                """, (name, age, gender, selected_test['id'], 
                                     result_value, is_abnormal, is_critical, notes))
                                
                                conn.commit()
                                
                                st.success(t('saved_success'))
                                
                                if is_critical:
                                    st.error("🚨 CRITICAL VALUE ALERT!")
                                    st.markdown(f"""
                                    <div class="critical-box">
                                        <h4>⚠️ Critical Result for {get_name(selected_test)}</h4>
                                        <p>Patient: {name}</p>
                                        <p>Result: {result_value} {selected_test['unit']}</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                
                                st.rerun()
                else:
                    st.info("Please select a test category to continue")
                    st.form_submit_button(t('save_result'), disabled=True, use_container_width=True)
        
        with col2:
            st.markdown("### Recent Results")
            
            recent_results = conn.execute("""
                SELECT tr.*, tt.name_en, tt.name_ku, tt.unit
                FROM test_results tr
                JOIN test_types tt ON tr.test_id = tt.id
                ORDER BY tr.date_performed DESC
                LIMIT 10
            """).fetchall()
            
            if recent_results:
                for result in recent_results:
                    rd = dict(result)
                    
                    if rd['is_critical']:
                        box_class = "test-result-critical"
                        emoji = "🚨"
                    elif rd['is_abnormal']:
                        box_class = "test-result-abnormal"
                        emoji = "⚠️"
                    else:
                        box_class = "test-result-normal"
                        emoji = "✅"
                    
                    st.markdown(f"""
                    <div class="{box_class}">
                        <p><strong>{emoji} {rd['patient_name']}</strong> - {get_name(rd)}</p>
                        <p>Result: {rd['result_value']} {rd['unit']}</p>
                        <p><small>{rd['date_performed']}</small></p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No recent results to display")
                
    except Exception as e:
        st.error(f"Results Entry Error: {str(e)}")

# ==================== Reports ====================

def render_reports():
    """Reports page"""
    if conn is None:
        return
        
    st.markdown("""
    <div class="main-header">
        <h1>📈 ڕاپۆرت</h1>
        <p>Laboratory Analytics</p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            date_from = st.date_input("From Date", datetime.now() - timedelta(days=30))
        with col2:
            date_to = st.date_input("To Date", datetime.now())
        
        results = conn.execute("""
            SELECT tr.*, tt.name_en, tt.name_ku, tt.category, tt.unit
            FROM test_results tr
            JOIN test_types tt ON tr.test_id = tt.id
            WHERE date(tr.date_performed) BETWEEN ? AND ?
            ORDER BY tr.date_performed DESC
        """, (date_from, date_to)).fetchall()
        
        if not results:
            st.info("No results found for selected period")
            return
        
        df = pd.DataFrame([dict(r) for r in results])
        df['test_name'] = df.apply(lambda row: get_name(row), axis=1)
        
        st.markdown("### 📊 Summary Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_tests = len(df)
            st.metric("Total Tests", total_tests)
        
        with col2:
            total_patients = df['patient_name'].nunique()
            st.metric("Unique Patients", total_patients)
        
        with col3:
            abnormal_count = df['is_abnormal'].sum()
            abnormal_rate = (abnormal_count / total_tests * 100) if total_tests > 0 else 0
            st.metric("Abnormal Results", f"{abnormal_count} ({abnormal_rate:.1f}%)")
        
        with col4:
            critical_count = df['is_critical'].sum()
            st.metric("Critical Values", critical_count)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Test Distribution")
            
            test_counts = df['test_name'].value_counts().head(10)
            if len(test_counts) > 0:
                fig = px.bar(x=test_counts.index, y=test_counts.values,
                            title="Top 10 Tests",
                            labels={'x': 'Test', 'y': 'Count'},
                            color=test_counts.values,
                            color_continuous_scale='Viridis')
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Abnormal by Category")
            
            category_abnormal = df.groupby('category')['is_abnormal'].agg(['sum', 'count'])
            if len(category_abnormal) > 0:
                category_abnormal['rate'] = (category_abnormal['sum'] / category_abnormal['count'] * 100)
                
                fig = px.bar(category_abnormal, y=category_abnormal.index, x='rate',
                            title="Abnormal Rate (%)",
                            orientation='h',
                            color='rate',
                            color_continuous_scale='RdYlGn_r')
                st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### 📋 Detailed Results")
        
        display_cols = ['patient_name', 'patient_age', 'patient_gender', 
                       'test_name', 'result_value', 'unit', 'date_performed']
        display_cols = [c for c in display_cols if c in df.columns]
        
        df['Status'] = df.apply(lambda row: 
                               '🚨 CRITICAL' if row['is_critical'] else 
                               '⚠️ ABNORMAL' if row['is_abnormal'] else 
                               '✅ NORMAL', axis=1)
        
        st.dataframe(df[display_cols + ['Status']], use_container_width=True, hide_index=True)
        
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Export to CSV",
            data=csv,
            file_name=f"lab_results_{date_from}_{date_to}.csv",
            mime="text/csv",
            use_container_width=True
        )
                
    except Exception as e:
        st.error(f"Reports Error: {str(e)}")

# ==================== AI Chat ====================

def render_ai_chat():
    """AI Chat page"""
    st.markdown("""
    <div class="main-header">
        <h1>🤖 زیرەکی دەستکرد</h1>
        <p>Medical Laboratory AI Assistant</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 💡 Suggested Questions")
    
    suggestions = [
        "What does a CBC test measure?",
        "Explain normal blood glucose levels",
        "What causes anemia?",
        "How to prepare for a cholesterol test?",
        "Interpret high WBC count",
        "What is HbA1c?",
        "Explain Gram staining procedure"
    ]
    
    for i in range(0, len(suggestions), 4):
        cols = st.columns(4)
        for j in range(4):
            if i + j < len(suggestions):
                with cols[j]:
                    if st.button(suggestions[i + j], key=f"sug_{i+j}", use_container_width=True):
                        st.session_state.chat_input = suggestions[i + j]
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    chat_container = st.container()
    
    with chat_container:
        for i, chat in enumerate(st.session_state.chat_history):
            with st.chat_message("user"):
                st.write(chat['question'])
            
            with st.chat_message("assistant"):
                st.markdown(chat['answer'])
    
    if 'chat_input' not in st.session_state:
        st.session_state.chat_input = ""
    
    question = st.chat_input(t('type_question'))
    
    if question:
        st.session_state.chat_history.append({
            "question": question,
            "answer": ""
        })
        
        with st.chat_message("user"):
            st.write(question)
        
        with st.chat_message("assistant"):
            with st.spinner("🤔 Analyzing your question..."):
                answer = get_ai_response(question)
                st.markdown(answer)
                st.session_state.chat_history[-1]['answer'] = answer
    
    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

# ==================== Main Application ====================

def main():
    """Main application"""
    
    if 'language' not in st.session_state:
        st.session_state.language = "کوردی 🇹🇯"
    
    if 'nav_page' not in st.session_state:
        st.session_state.nav_page = "dashboard"
    
    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 15px 0;">
            <h3 style="color: #1565c0; margin: 0;">🔬 MediLab Pro</h3>
            <p style="color: #666; font-size: 0.8rem; margin: 5px 0;">Medical Laboratory System</p>
        </div>
        """, unsafe_allow_html=True)
        
        language = st.selectbox(
            "🌐 Language / زمان",
            ["کوردی 🇹🇯", "English 🇬🇧"],
            key="lang_selector"
        )
        
        if language != st.session_state.language:
            st.session_state.language = language
            st.rerun()
        
        st.markdown("---")
        
        st.markdown("### 📱 Navigation")
        
        pages = {
            "dashboard": "📊 " + t('dashboard'),
            "diseases": "🦠 " + t('disease_db'),
            "tests": "🧪 " + t('lab_tests'),
            "practical": "🔬 " + t('practical'),
            "notes": "📚 " + t('theory'),
            "results": "📝 " + t('results_entry'),
            "reports": "📈 " + t('reports'),
            "ai": "🤖 " + t('ai_chat')
        }
        
        for page_key, page_name in pages.items():
            button_type = "primary" if st.session_state.nav_page == page_key else "secondary"
            if st.button(page_name, key=f"nav_{page_key}", 
                        use_container_width=True,
                        type=button_type):
                st.session_state.nav_page = page_key
                st.rerun()
        
        st.markdown("---")
        
        try:
            db_size = os.path.getsize('medical_lab.db') / (1024 * 1024)
            st.caption(f"Database Size: {db_size:.2f} MB")
        except:
            st.caption("Database: Connected")
        
        st.caption(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        st.markdown("---")
        
        st.markdown("""
        <div style="text-align: center; padding: 10px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 10px; color: white;">
            <p style="margin: 3px 0; font-size: 0.9rem;"><strong>🎓 دانیال ئیسماعیل</strong></p>
            <p style="margin: 3px 0; font-size: 0.8rem;">قۆناغی چوارەم - تاقیگەی پزیشکی</p>
            <p style="margin: 3px 0; font-size: 0.7rem;">© 2024</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Student Info Header - smaller version
    st.markdown("""
    <div class="student-info">
        <h2>🎓 دانیال ئیسماعیل</h2>
        <p>قۆناغی چوارەم - بەشی تاقیگەی پزیشکی</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Render selected page
    current_page = st.session_state.nav_page
    
    try:
        if current_page == "dashboard":
            render_dashboard()
        elif current_page == "diseases":
            render_diseases()
        elif current_page == "tests":
            render_tests()
        elif current_page == "practical":
            render_practical()
        elif current_page == "notes":
            render_notes()
        elif current_page == "results":
            render_results()
        elif current_page == "reports":
            render_reports()
        elif current_page == "ai":
            render_ai_chat()
        else:
            render_dashboard()
    except Exception as e:
        st.error(f"Error loading page: {str(e)}")
        st.info("Please try refreshing the page.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 8px; color: #666; font-size: 0.8rem;">
        <p>🔬 Medical Laboratory Management System | Version 2.0</p>
        <p>Developed for educational purposes | Always consult healthcare professionals</p>
    </div>
    """, unsafe_allow_html=True)

# ==================== Run Application ====================

if __name__ == "__main__":
    if conn:
        main()
    else:
        st.error("❌ Failed to connect to database. Please check your configuration.")
        st.info("Make sure SQLite is installed and the application has write permissions.")
