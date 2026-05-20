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
    
    lang = st.session_state.get("lang
