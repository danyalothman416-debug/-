# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from itertools import groupby
import os
import google.generativeai as genai
import random
from typing import List, Dict, Any
import plotly.figure_factory as ff
import json

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
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    .student-info {
        background: linear-gradient(135deg, #1a237e, #283593);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    .category-card {
        background: linear-gradient(135deg, #e8eaf6, #c5cae9);
        padding: 20px;
        border-radius: 12px;
        margin: 10px 0;
        border-right: 5px solid #1565c0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: transform 0.3s, box-shadow 0.3s;
    }
    
    .category-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.1);
    }

    .info-box {
        background: #e3f2fd;
        padding: 15px;
        border-radius: 10px;
        border-right: 4px solid #1565c0;
        margin: 10px 0;
        color: #1a1a1a;
    }

    .warning-box {
        background: #fff3e0;
        padding: 15px;
        border-radius: 10px;
        border-right: 4px solid #ff9800;
        margin: 10px 0;
        color: #1a1a1a;
    }
    
    .critical-box {
        background: #ffebee;
        padding: 15px;
        border-radius: 10px;
        border-right: 4px solid #f44336;
        margin: 10px 0;
        color: #1a1a1a;
    }

    .symptom-tag {
        display: inline-block;
        background: linear-gradient(135deg, #ffebee, #ffcdd2);
        color: #c62828;
        padding: 5px 12px;
        border-radius: 20px;
        margin: 3px;
        font-size: 0.9em;
        border: 1px solid #ef9a9a;
    }

    .step-number {
        display: inline-block;
        background: linear-gradient(135deg, #0d47a1, #1565c0);
        color: white;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        text-align: center;
        line-height: 32px;
        margin-left: 8px;
        font-weight: bold;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }

    .normal-range {
        color: #2e7d32;
        font-weight: bold;
        background-color: #e8f5e9;
        padding: 2px 6px;
        border-radius: 4px;
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
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        text-align: center;
        transition: transform 0.2s;
    }
    
    .stat-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .test-result-normal {
        background-color: #e8f5e9;
        padding: 10px;
        border-radius: 8px;
        border-right: 4px solid #4caf50;
        margin: 5px 0;
    }
    
    .test-result-abnormal {
        background-color: #fff3e0;
        padding: 10px;
        border-radius: 8px;
        border-right: 4px solid #ff9800;
        margin: 5px 0;
    }
    
    .test-result-critical {
        background-color: #ffebee;
        padding: 10px;
        border-radius: 8px;
        border-right: 4px solid #f44336;
        margin: 5px 0;
    }

    .stMarkdown, .stMarkdown p, .stMarkdown h1,
    .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
        color: #1a1a1a !important;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    
    .glass-effect {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 10px;
        padding: 20px;
    }
    
    .practical-step {
        background: #f5f5f5;
        padding: 10px;
        margin: 5px 0;
        border-radius: 5px;
        border-left: 3px solid #1565c0;
    }
    
    .note-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-top: 3px solid #1565c0;
    }

</style>
""", unsafe_allow_html=True)

# ==================== Database ====================

@st.cache_resource
def init_db():
    """Initialize database with better error handling and performance"""
    try:
        # Remove existing database if corrupted
        if os.path.exists('medical_lab.db'):
            try:
                # Test connection
                test_conn = sqlite3.connect('medical_lab.db')
                test_conn.execute("SELECT 1")
                test_conn.close()
            except:
                os.remove('medical_lab.db')
        
        conn = sqlite3.connect(
            'medical_lab.db',
            check_same_thread=False,
            timeout=30
        )
        
        # Enable WAL mode for better performance
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
        
        CREATE TABLE IF NOT EXISTS reference_ranges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_id INTEGER NOT NULL,
            age_min INTEGER,
            age_max INTEGER,
            gender TEXT,
            range_low REAL,
            range_high REAL,
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

# ==================== Insert Comprehensive Data ====================

def insert_comprehensive_data(conn):
    """Insert comprehensive medical data into database"""
    if conn is None:
        return
        
    try:
        # Check if data already exists
        count = conn.execute("SELECT COUNT(*) as c FROM test_types").fetchone()
        if count['c'] > 5:  # If we have more than basic data, skip
            return
            
        # Clear existing data for fresh insert
        conn.execute("DELETE FROM reference_ranges")
        conn.execute("DELETE FROM test_results")
        conn.execute("DELETE FROM practical_tests")
        conn.execute("DELETE FROM study_notes")
        conn.execute("DELETE FROM diseases")
        conn.execute("DELETE FROM test_types")
        conn.execute("DELETE FROM disease_categories")
        
        # Disease Categories with more details
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
             
            ("Parasitology", "مشەخۆرناسی",
             "Study of parasites and parasitic diseases",
             "لێکۆڵینەوە لە مشەخۆرەکان و نەخۆشییە مشەخۆرییەکان",
             "🪱", "#8B4513"),
             
            ("Serology", "سیرۆلۆجی",
             "Study of blood serum and antibodies",
             "لێکۆڵینەوە لە سیرۆمی خوێن و دژەتەنەکان",
             "💉", "#FF69B4")
        ]
        
        for cat in categories:
            try:
                conn.execute("""
                INSERT INTO disease_categories (name_en, name_ku, description_en, description_ku, icon, color)
                VALUES (?, ?, ?, ?, ?, ?)
                """, cat)
            except sqlite3.IntegrityError:
                pass  # Skip duplicates
        
        # Comprehensive Test Types
        tests = [
            # Hematology Tests
            ("CBC", "ژمارەی تەواوی خوێن (CBC)", "Hematology", "cells/μL", 
             4.5, 11.0, 2.0, 15.0,
             "Complete Blood Count - measures red blood cells, white blood cells, and platelets",
             "ژمارەی تەواوی خوێن - خانە سوورەکان، سپییەکان و پەڕەکانی خوێن دەپێورێت",
             "No special preparation needed", "پێویستی بە ئامادەکاری تایبەت نییە", "2 hours", 25.0),
             
            ("Hemoglobin", "هیمۆگلۆبین (Hb)", "Hematology", "g/dL",
             12.0, 16.0, 7.0, 20.0,
             "Measures the amount of hemoglobin in blood",
             "بڕی هیمۆگلۆبین لە خوێندا دەپێورێت",
             "Fasting not required", "پێویستی بە بەڕۆژووبوون نییە", "1 hour", 15.0),
             
            ("WBC Count", "ژمارەی خانە سپییەکان (WBC)", "Hematology", "cells/μL",
             4000, 11000, 2000, 30000,
             "White Blood Cell count - indicates infection or inflammation",
             "ژمارەی خانە سپییەکانی خوێن - هەوکردن یان هەوکردن نیشان دەدات",
             "No special preparation", "پێویستی بە ئامادەکاری نییە", "1 hour", 20.0),
             
            ("Platelet Count", "ژمارەی پەڕەکانی خوێن (PLT)", "Hematology", "cells/μL",
             150000, 450000, 50000, 1000000,
             "Measures blood clotting ability",
             "توانستی مەیاندنی خوێن دەپێورێت",
             "Avoid aspirin 48 hours before", "٤٨ کاتژمێر پێش ئەسپرین بەکارمەهێنە", "2 hours", 30.0),
             
            ("RBC Count", "ژمارەی خانە سوورەکان (RBC)", "Hematology", "million/μL",
             4.5, 5.5, 3.0, 7.0,
             "Red Blood Cell count - oxygen carrying capacity",
             "ژمارەی خانە سوورەکانی خوێن - توانای هەڵگرتنی ئۆکسجین",
             "No special preparation", "پێویستی بە ئامادەکاری نییە", "1 hour", 20.0),
            
            # Clinical Chemistry Tests
            ("Blood Glucose", "شەکری خوێن (FBS)", "Clinical Chemistry", "mg/dL",
             70, 100, 40, 300,
             "Measures blood sugar levels - important for diabetes diagnosis",
             "ئاستی شەکری خوێن دەپێورێت - گرنگە بۆ دەستنیشانکردنی شەکرە",
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
             "Kidney function and protein metabolism test",
             "پشکنینی کاری گورچیلە و میتابۆلیسمی پرۆتین",
             "No special preparation", "پێویستی بە ئامادەکاری نییە", "2 hours", 20.0),
             
            ("Cholesterol Total", "کۆلیستڕۆڵی گشتی", "Clinical Chemistry", "mg/dL",
             125, 200, 100, 300,
             "Total blood cholesterol - heart disease risk",
             "کۆی کۆلیستڕۆڵی خوێن - مەترسی نەخۆشی دڵ",
             "Fast for 9-12 hours", "٩-١٢ کاتژمێر بەڕۆژوو بە", "3 hours", 35.0),
             
            ("HDL Cholesterol", "کۆلیستڕۆڵی باش (HDL)", "Clinical Chemistry", "mg/dL",
             40, 60, 20, 100,
             "Good cholesterol - protective for heart",
             "کۆلیستڕۆڵی باش - پارێزەری دڵ",
             "Fast for 9-12 hours", "٩-١٢ کاتژمێر بەڕۆژوو بە", "3 hours", 35.0),
             
            ("LDL Cholesterol", "کۆلیستڕۆڵی خراپ (LDL)", "Clinical Chemistry", "mg/dL",
             0, 100, 0, 200,
             "Bad cholesterol - heart disease risk",
             "کۆلیستڕۆڵی خراپ - مەترسی نەخۆشی دڵ",
             "Fast for 9-12 hours", "٩-١٢ کاتژمێر بەڕۆژوو بە", "3 hours", 35.0),
             
            ("Triglycerides", "ترایگلیسیرید (TG)", "Clinical Chemistry", "mg/dL",
             35, 150, 20, 500,
             "Fat levels in blood",
             "ئاستی چەوری لە خوێندا",
             "Fast for 12 hours", "١٢ کاتژمێر بەڕۆژوو بە", "3 hours", 35.0),
             
            ("ALT", "ئەلانین ئەمینۆترانسفێراز (ALT)", "Clinical Chemistry", "U/L",
             7, 56, 3, 200,
             "Liver enzyme - liver function test",
             "ئەنزیمی جگەر - پشکنینی کاری جگەر",
             "No special preparation", "پێویستی بە ئامادەکاری نییە", "2 hours", 25.0),
             
            ("AST", "ئەسپارتەیت ئەمینۆترانسفێراز (AST)", "Clinical Chemistry", "U/L",
             10, 40, 5, 200,
             "Liver and muscle enzyme test",
             "پشکنینی ئەنزیمی جگەر و ماسولکە",
             "No special preparation", "پێویستی بە ئامادەکاری نییە", "2 hours", 25.0),
            
            # Immunology Tests
            ("CRP", "پڕۆتینی کاردەر لە هەوکردن (CRP)", "Immunology", "mg/L",
             0, 5, 0, 100,
             "C-Reactive Protein - inflammation marker",
             "پڕۆتینی کاردەر لە هەوکردن - نیشانەکەری هەوکردن",
             "No special preparation", "پێویستی بە ئامادەکاری نییە", "2 hours", 40.0),
             
            ("ESR", "خێرایی ڕوونیشتنەوەی خوێن (ESR)", "Immunology", "mm/hr",
             0, 20, 0, 100,
             "Erythrocyte Sedimentation Rate - inflammation indicator",
             "خێرایی ڕوونیشتنەوەی خڕۆکە سوورەکان - نیشانەکەری هەوکردن",
             "No special preparation", "پێویستی بە ئامادەکاری نییە", "1 hour", 15.0),
             
            ("RF", "فاکتەری ڕۆماتیزمی (RF)", "Immunology", "IU/mL",
             0, 14, 0, 100,
             "Rheumatoid Factor - autoimmune disease marker",
             "فاکتەری ڕۆماتیزمی - نیشانەکەری نەخۆشی خۆبەرگری",
             "No special preparation", "پێویستی بە ئامادەکاری نییە", "2 hours", 45.0),
            
            # Microbiology Tests  
            ("Urine Culture", "کەلتووری میز", "Microbiology", "CFU/mL",
             0, 10000, 0, 100000,
             "Detects bacterial infection in urine",
             "هەوکردنی بەکتریایی لە میزدا دەدۆزێتەوە",
             "Clean catch midstream sample", "نموونەی ناوەڕاستی میز بە پاکی کۆبکەرەوە", "48-72 hours", 75.0),
             
            ("Blood Culture", "کەلتووری خوێن", "Microbiology", "CFU/mL",
             0, 0, 0, 10,
             "Detects bacteria in blood - sepsis",
             "بەکتریا لە خوێندا دەدۆزێتەوە - خوێن ژەهراویبوون",
             "Strict aseptic technique", "تەکنیکی وردی پاکژی", "24-72 hours", 100.0),
             
            ("Stool Culture", "کەلتووری پیسایی", "Microbiology", "CFU/mL",
             0, 0, 0, 1000,
             "Detects pathogenic bacteria in stool",
             "بەکتریای نەخۆشیخواز لە پیساییدا دەدۆزێتەوە",
             "Fresh stool sample", "نموونەی پیسایی تازە", "48-72 hours", 80.0),
             
            # Endocrinology Tests
            ("TSH", "هۆرمۆنی چالاککەری تایرۆید (TSH)", "Endocrinology", "mIU/L",
             0.4, 4.0, 0.1, 50.0,
             "Thyroid Stimulating Hormone - thyroid function",
             "هۆرمۆنی چالاککەری تایرۆید - کاری تایرۆید",
             "Morning sample preferred", "نموونەی بەیانی باشترە", "3 hours", 60.0),
             
            ("T3", "ترای ئایۆدۆ تایرۆنین (T3)", "Endocrinology", "ng/dL",
             80, 200, 50, 500,
             "Triiodothyronine - thyroid hormone",
             "هۆرمۆنی تایرۆیدی T3",
             "Morning sample preferred", "نموونەی بەیانی باشترە", "3 hours", 55.0),
             
            ("T4", "تایرۆکسین (T4)", "Endocrinology", "μg/dL",
             4.5, 12.0, 2.0, 25.0,
             "Thyroxine - main thyroid hormone",
             "هۆرمۆنی سەرەکی تایرۆید",
             "Morning sample preferred", "نموونەی بەیانی باشترە", "3 hours", 55.0),
             
            ("Vitamin D", "ڤیتامین D", "Endocrinology", "ng/mL",
             30, 100, 10, 150,
             "Vitamin D levels - bone health",
             "ئاستی ڤیتامین D - تەندروستی ئێسک",
             "No special preparation", "پێویستی بە ئامادەکاری نییە", "4 hours", 80.0),
            
            # Urinalysis Tests
            ("Urine pH", "ترشێتی میز (pH)", "Urinalysis", "pH",
             4.5, 8.0, 4.0, 9.0,
             "Measures acidity of urine",
             "ترشێتی میز دەپێورێت",
             "Fresh sample required", "نموونەی تازە پێویستە", "30 minutes", 10.0),
             
            ("Urine Protein", "پرۆتینی میز", "Urinalysis", "mg/24h",
             0, 150, 0, 3000,
             "Protein in urine - kidney function",
             "پرۆتین لە میزدا - کاری گورچیلە",
             "24-hour collection", "کۆکردنەوەی ٢٤ کاتژمێر", "24 hours", 30.0),
             
            ("Urine Glucose", "شەکری میز", "Urinalysis", "mg/dL",
             0, 0, 0, 100,
             "Glucose in urine - diabetes indicator",
             "شەکر لە میزدا - نیشانەکەری شەکرە",
             "Random urine sample", "نموونەی میزی هەڕەمەکی", "30 minutes", 10.0),
             
            # Coagulation Tests
            ("PT", "کاتی پڕۆترۆمبین (PT)", "Coagulation", "seconds",
             11, 13.5, 9, 30,
             "Prothrombin Time - clotting pathway",
             "کاتی پڕۆترۆمبین - ڕێڕەوی مەیاندن",
             "Avoid anticoagulants if possible", "دژە مەیاندنەکان بەکارمەهێنە ئەگەر دەکرێت", "2 hours", 35.0),
             
            ("PTT", "کاتی ترۆمبۆپلاستینی بەشەکی (PTT)", "Coagulation", "seconds",
             25, 35, 20, 60,
             "Partial Thromboplastin Time - clotting factors",
             "کاتی ترۆمبۆپلاستینی بەشەکی - فاکتەرەکانی مەیاندن",
             "Avoid heparin therapy", "چارەسەری هیپارین بەکارمەهێنە", "2 hours", 35.0),
            
            # Serology Tests
            ("HBsAg", "دژەپەیداکەری ڤایرۆسی هەوکردنی جگەر B", "Serology", "qualitative",
             0, 0, 0, 1,
             "Hepatitis B surface antigen test",
             "پشکنینی دژەپەیداکەری ڤایرۆسی هەوکردنی جگەری جۆری B",
             "No special preparation", "پێویستی بە ئامادەکاری نییە", "4 hours", 50.0),
             
            ("HIV Test", "پشکنینی ڤایرۆسی نەمانی بەرگری (HIV)", "Serology", "qualitative",
             0, 0, 0, 1,
             "HIV antibody screening test",
             "پشکنینی پشکنینی دژەتەنی ڤایرۆسی HIV",
             "Counseling recommended", "ڕاوێژکاری پێشنیار دەکرێت", "24 hours", 60.0)
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
                pass  # Skip duplicates
        
        # Comprehensive Diseases
        diseases_data = [
            # Hematology Diseases
            (1, "Iron Deficiency Anemia", "کەمخوێنی بەهۆی کەمی ئاسن",
             "Most common type of anemia caused by insufficient iron",
             "باوباپترین جۆری کەمخوێنی بەهۆی کەمی ئاسنەوە",
             "Fatigue, Weakness, Pale skin, Shortness of breath, Dizziness",
             "ماندووبوون، لاوازی، پێستی کاڵ، هەناسە توندی، سەرگێژە",
             "Poor diet, Blood loss, Pregnancy, Malabsorption",
             "خواردنی خراپ، لەدەستدانی خوێن، دووگیانی، هەڵنەمژینی خواردن",
             "Iron supplements, Iron-rich diet, Treat underlying cause",
             "تەواوکەری ئاسن، خواردنی دەوڵەمەند بە ئاسن، چارەسەری هۆکاری سەرەکی",
             "Mild to Severe"),
             
            (1, "Thalassemia", "تالاسیمیا",
             "Genetic blood disorder affecting hemoglobin production",
             "نەخۆشی خوێنی بۆماوەیی کاردەکاتە سەر بەرهەمهێنانی هیمۆگلۆبین",
             "Fatigue, Weakness, Bone deformities, Dark urine, Slow growth",
             "ماندووبوون، لاوازی، شێواوی ئێسک، میزی تاریک، گەشەی هێواش",
             "Genetic inheritance from parents",
             "بۆماوەیی لە دایک و باوکەوە",
             "Blood transfusions, Folic acid, Bone marrow transplant",
             "گواستنەوەی خوێن، ترشی فۆلیک، چاندنی مۆخی ئێسک",
             "Moderate to Severe"),
             
            (1, "Leukemia", "شێرپەنجەی خوێن (لیوکیمیا)",
             "Cancer of blood-forming tissues",
             "شێرپەنجەی شانەکانی دروستکردنی خوێن",
             "Frequent infections, Weight loss, Bruising, Bone pain, Fatigue",
             "هەوکردنی زۆر، دابەزینی کێش، شینبوونەوە، ئازاری ئێسک، ماندووبوون",
             "Genetic mutations, Radiation exposure, Chemical exposure",
             "گۆڕانی بۆماوەیی، بەرکەوتنی تیشکدان، بەرکەوتنی کیمیایی",
             "Chemotherapy, Radiation, Bone marrow transplant",
             "کیمۆتراپی، تیشکدان، چاندنی مۆخی ئێسک",
             "Severe"),
            
            # Clinical Chemistry Diseases
            (2, "Diabetes Mellitus Type 1", "شەکرەی جۆری ١",
             "Autoimmune destruction of insulin-producing cells",
             "تێکدانی خۆبەرگری خانەکانی بەرهەمهێنەری ئینسولین",
             "Frequent urination, Excessive thirst, Weight loss, Fatigue",
             "میزی زۆر، تینویەتی زۆر، دابەزینی کێش، ماندووبوون",
             "Autoimmune reaction, Genetic factors",
             "کارلێکی خۆبەرگری، هۆکارە بۆماوەییەکان",
             "Insulin therapy, Diet control, Blood sugar monitoring",
             "چارەسەری ئینسولین، کۆنتڕۆڵی خواردن، چاودێری شەکری خوێن",
             "Moderate to Severe"),
             
            (2, "Diabetes Mellitus Type 2", "شەکرەی جۆری ٢",
             "Insulin resistance and relative insulin deficiency",
             "بەرگری ئینسولین و کەمی ڕێژەیی ئینسولین",
             "Slow-healing wounds, Numbness, Blurred vision, Fatigue",
             "برینەکانی بە هێواشی چاکدەبنەوە، کڕێتی، تەمومژی بینین، ماندووبوون",
             "Obesity, Sedentary lifestyle, Genetic factors",
             "قەڵەوی، ژیانی بێ جوڵە، هۆکارە بۆماوەییەکان",
             "Oral medications, Diet, Exercise, Insulin if needed",
             "دەرمانی دەم، ڕێجیم، وەرزش، ئینسولین ئەگەر پێویست بوو",
             "Moderate"),
             
            (2, "Liver Cirrhosis", "ڕەقبوونی جگەر",
             "Late stage of scarring of the liver",
             "قۆناغی دوایی برینداربوونی جگەر",
             "Jaundice, Ascites, Easy bleeding, Confusion, Spider veins",
             "زەردوویی، کۆبوونەوەی ئاو لە سک، خوێنبەربوونی ئاسان، سەرلێشێواوی، خوێنهێنەرەکانی جاڵجاڵۆکە",
             "Chronic alcoholism, Hepatitis, Fatty liver disease",
             "ئەلکحولیزمی درێژخایەن، هەوکردنی جگەر، نەخۆشی چەوری جگەر",
             "Treat underlying cause, Liver transplant, Symptom management",
             "چارەسەری هۆکاری سەرەکی، چاندنی جگەر، بەڕێوەبردنی نیشانەکان",
             "Severe"),
            
            # Microbiology Diseases  
            (3, "Urinary Tract Infection", "هەوکردنی ڕێڕەوی میز",
             "Bacterial infection of urinary system",
             "هەوکردنی بەکتریایی سیستەمی میز",
             "Burning urination, Frequent urination, Cloudy urine, Pelvic pain",
             "میزکردنی سووتێنەر، میزکردنی زۆر، میزی تەمومژاوی، ئازاری لەگەنە",
             "E. coli bacteria, Poor hygiene, Catheter use",
             "بەکتریای ئیکۆلای، پاکژی خراپ، بەکارهێنانی کەتێتەر",
             "Antibiotics, Increased fluids, Cranberry products",
             "دژەبەکتریاکان، شلەی زیاتر، بەرهەمەکانی کرانبێری",
             "Mild to Moderate"),
             
            (3, "Tuberculosis", "سڵ",
             "Bacterial infection primarily affecting lungs",
             "هەوکردنی بەکتریایی بە شێوەیەکی سەرەکی کاریگەری لەسەر سییەکان",
             "Persistent cough, Blood in sputum, Night sweats, Weight loss, Fever",
             "کۆکەی بەردەوام، خوێن لە قڵێسک، ئارەقەی شەوانە، دابەزینی کێش، تا",
             "Mycobacterium tuberculosis bacteria, Airborne transmission",
             "بەکتریای مایکۆباکتریۆم تیوبێرکلۆزیس، گواستنەوەی هەوایی",
             "Long-term antibiotics, Isolation, Direct Observed Therapy",
             "دژەبەکتریای درێژخایەن، جیاکردنەوە، چارەسەری چاودێریکراوی ڕاستەوخۆ",
             "Moderate to Severe"),
             
            # Immunology Diseases
            (4, "Rheumatoid Arthritis", "هەوکردنی جومگەکانی ڕۆماتیزمی",
             "Autoimmune disease causing joint inflammation",
             "نەخۆشی خۆبەرگری دەبێتە هۆی هەوکردنی جومگەکان",
             "Joint pain, Morning stiffness, Fatigue, Fever, Weight loss",
             "ئازاری جومگەکان، ڕەقبوونی بەیانیان، ماندووبوون، تا، دابەزینی کێش",
             "Autoimmune reaction, Genetic factors, Environmental triggers",
             "کارلێکی خۆبەرگری، هۆکارە بۆماوەییەکان، هاندەرە ژینگەییەکان",
             "NSAIDs, Steroids, DMARDs, Physical therapy",
             "دژەهەوکردنەکان، سترۆیدەکان، دەرمانە دژە ڕۆماتیزمییەکان، چارەسەری جوڵەیی",
             "Moderate to Severe"),
             
            (4, "Systemic Lupus Erythematosus", "نەخۆشی لوپوسی سیستمیکی",
             "Autoimmune disease affecting multiple organs",
             "نەخۆشی خۆبەرگری کاریگەری لەسەر چەندین ئەندام",
             "Butterfly rash, Joint pain, Kidney problems, Fatigue, Fever",
             "دەرپەڕینی پەپولەیی، ئازاری جومگەکان، کێشەی گورچیلە، ماندووبوون، تا",
             "Autoimmune reaction, Genetic factors, UV light exposure",
             "کارلێکی خۆبەرگری، هۆکارە بۆماوەییەکان، بەرکەوتنی تیشکی سەرووی وەنەوشەیی",
             "Immunosuppressants, Anti-inflammatory drugs, Lifestyle changes",
             "دەرمانەکانی سەرکوتکەری بەرگری، دژەهەوکردنەکان، گۆڕانی شێوازی ژیان",
             "Moderate to Severe"),
             
            # Endocrinology Diseases
            (5, "Hypothyroidism", "کەمکاری تایرۆید",
             "Underactive thyroid gland",
             "کەمکاری ڕژێنی تایرۆید",
             "Weight gain, Cold intolerance, Fatigue, Depression, Dry skin",
             "زیادبوونی کێش، نەتوانینی بەرگەی سەرما، ماندووبوون، خەمۆکی، پێستی وشک",
             "Autoimmune disease, Iodine deficiency, Thyroid surgery",
             "نەخۆشی خۆبەرگری، کەمی یۆد، نەشتەرگەری تایرۆید",
             "Levothyroxine replacement therapy",
             "چارەسەری جێگرەوەی لیڤۆتایرۆکسین",
             "Moderate"),
             
            (5, "Hyperthyroidism", "زۆرکاری تایرۆید",
             "Overactive thyroid gland",
             "زۆرکاری ڕژێنی تایرۆید",
             "Weight loss, Heat intolerance, Anxiety, Tremors, Rapid heartbeat",
             "دابەزینی کێش، نەتوانینی بەرگەی گەرمی، دڵەڕاوکێ، لەرزین، لێدانی خێرای دڵ",
             "Graves' disease, Thyroid nodules, Excessive iodine",
             "نەخۆشی گرەیڤز، گرێی تایرۆید، یۆدی زۆر",
             "Anti-thyroid drugs, Radioactive iodine, Surgery",
             "دەرمانە دژە تایرۆیدییەکان، یۆدی تیشکدەر، نەشتەرگەری",
             "Moderate")
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
                pass  # Skip duplicates
        
        # Comprehensive Practical Tests
        practicals = [
            ("Blood Smear Preparation", "ئامادەکردنی سمێری خوێن",
             "Preparation and staining of blood smear for microscopic examination",
             "ئامادەکردن و ڕەنگکردنی سمێری خوێن بۆ پشکنینی مایکرۆسکۆپی",
             "Hematology",
             "1. Clean slide with alcohol\n2. Place small drop of blood\n3. Use spreader slide at 30-45° angle\n4. Quick smooth motion to spread\n5. Air dry completely\n6. Fix with methanol\n7. Stain with Wright's stain\n8. Wash and dry\n9. Examine under microscope",
             "١. سلاید بە ئەلکحول پاک بکەرەوە\n٢. دڵۆپێکی بچووکی خوێن دابنێ\n٣. سلایدی بڵاوکەرەوە بە گۆشەی ٣٠-٤٥ پلە بەکاربهێنە\n٤. بە جوڵەیەکی خێرا و نەرم بیبڵاوە\n٥. بە تەواوی وشک بکەرەوە\n٦. بە میسانۆل جێگیر بکە\n٧. بە ڕەنگی رایت ڕەنگی بکە\n٨. بیشۆ و وشکی بکەرەوە\n٩. لە ژێر مایکرۆسکۆپ پشکنین بکە",
             "Glass slides, Blood sample, Spreader slide, Methanol, Wright's stain, Microscope",
             "سلایدی شووشەیی، نموونەی خوێن، سلایدی بڵاوکەرەوە، میسانۆل، ڕەنگی رایت، مایکرۆسکۆپ",
             "Evenly distributed blood cells with proper staining",
             "خانەکانی خوێن بە یەکسانی بڵاوکراونەتەوە و بە باشی ڕەنگکراون",
             "Check RBC morphology, WBC differential, Platelet estimation",
             "شێوەی خڕۆکە سوورەکان، جیاکاری خانە سپییەکان، خەمڵاندنی پەڕەکانی خوێن",
             "Avoid air bubbles, Use fresh blood, Proper angle technique",
             "دوورکەوتنەوە لە بڵقەکانی هەوا، بەکارهێنانی خوێنی تازە، تەکنیکی گۆشەی گونجاو",
             30, "Basic"),
             
            ("Gram Staining", "ڕەنگکردنی گرام",
             "Differential staining technique for bacteria classification",
             "تەکنیکی ڕەنگکردنی جیاکار بۆ پۆلێنکردنی بەکتریا",
             "Microbiology",
             "1. Prepare bacterial smear\n2. Heat fix\n3. Crystal violet - 1 minute\n4. Wash with water\n5. Gram's iodine - 1 minute\n6. Wash with water\n7. Decolorize with alcohol\n8. Wash immediately\n9. Safranin counterstain - 30 sec\n10. Wash, dry, examine",
             "١. سمێری بەکتریا ئامادە بکە\n٢. بە گەرمی جێگیر بکە\n٣. کریستاڵ ڤایۆلێت - ١ خولەک\n٤. بە ئاو بیشۆ\n٥. یۆدی گرام - ١ خولەک\n٦. بە ئاو بیشۆ\n٧. بە ئەلکحول ڕەنگ لێ بەرەوە\n٨. یەکسەر بیشۆ\n٩. سەفرانین - ٣٠ چرکە\n١٠. بیشۆ، وشک بکەرەوە، پشکنین بکە",
             "Bacterial culture, Crystal violet, Iodine, Alcohol, Safranin, Microscope",
             "کەلتووری بەکتریا، کریستاڵ ڤایۆلێت، یۆد، ئەلکحول، سەفرانین، مایکرۆسکۆپ",
             "Gram-positive: Purple, Gram-negative: Pink/Red",
             "گرام پۆزەتیڤ: وەنەوشەیی، گرام نێگەتیڤ: پەمەیی/سوور",
             "Bacterial classification, Antibiotic selection guidance",
             "پۆلێنکردنی بەکتریا، ڕێنمایی هەڵبژاردنی دژەبەکتریا",
             "Don't over-decolorize, Use fresh cultures, Check controls",
             "زۆر ڕەنگ لێ مەبەرەوە، کەلتووری تازە بەکاربهێنە، کۆنترۆڵەکان بپشکنە",
             45, "Intermediate"),
             
            ("Urine Dipstick Analysis", "شیکردنەوەی دیپستیکی میز",
             "Rapid screening test for urine components",
             "پشکنینی خێرای پشکنین بۆ پێکهاتەکانی میز",
             "Urinalysis",
             "1. Collect fresh urine sample\n2. Dip test strip briefly\n3. Remove excess urine\n4. Compare to color chart at specified times\n5. Record results for each parameter",
             "١. نموونەی میزی تازە کۆبکەرەوە\n٢. شریتی پشکنین بە کورتی نوقم بکە\n٣. میزی زیادە لابەرە\n٤. بەراورد بە هێڵکاری ڕەنگەکان لە کاتە دیاریکراوەکان\n٥. ئەنجامەکان بۆ هەر پارامێتەرێک تۆمار بکە",
             "Urine sample, Dipstick strips, Color chart, Timer",
             "نموونەی میز، شریتەکانی دیپستیک، هێڵکاری ڕەنگ، کاتژمێر",
             "Color changes indicating various urine components",
             "گۆڕانی ڕەنگەکان پێکهاتە جیاوازەکانی میز نیشان دەدات",
             "pH, Protein, Glucose, Ketones, Blood, Nitrite, Leukocytes",
             "ترشێتی، پرۆتین، شەکر، کیتۆنەکان، خوێن، نایترایت، خانە سپییەکان",
             "Check expiration date, Proper timing, Good lighting",
             "بەرواری بەسەرچوون بپشکنە، کاتی گونجاو، ڕووناکی باش",
             15, "Basic"),
             
            ("Blood Group Testing", "پشکنینی گروپی خوێن",
             "ABO and Rh blood group determination",
             "دیاریکردنی گروپی خوێنی ABO و Rh",
             "Blood Bank",
             "1. Prepare clean slide with 3 sections\n2. Add anti-A, anti-B, anti-D reagents\n3. Add blood drop to each section\n4. Mix with clean stick\n5. Rock slide gently\n6. Observe agglutination within 2 minutes",
             "١. سلایدی پاک بە ٣ بەش ئامادە بکە\n٢. کارلێککەرەکانی دژە-A، دژە-B، دژە-D زیاد بکە\n٣. دڵۆپەی خوێن بۆ هەر بەشێک زیاد بکە\n٤. بە داری پاک تێکەڵ بکە\n٥. سلایدەکە بە نەرمی بجوڵێنە\n٦. چڕبوونەوە لە ماوەی ٢ خولەکدا چاودێری بکە",
             "Clean slide, Anti-A reagent, Anti-B reagent, Anti-D reagent, Blood sample, Mixing sticks",
             "سلایدی پاک، کارلێککەری دژە-A، کارلێککەری دژە-B، کارلێککەری دژە-D، نموونەی خوێن، داری تێکەڵکردن",
             "Agglutination pattern determines blood group",
             "شێوازی چڕبوونەوە گروپی خوێن دیاری دەکات",
             "A, B, AB, O groups with Rh positive/negative",
             "گروپەکانی A، B، AB، O لەگەڵ Rh پۆزەتیڤ/نێگەتیڤ",
             "Use fresh blood, Check reagent expiry, Proper lighting",
             "خوێنی تازە بەکاربهێنە، بەرواری بەسەرچوونی کارلێککەر بپشکنە، ڕووناکی گونجاو",
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
                pass  # Skip duplicates
        
        # Add sample study notes
        notes = [
            ("Hematology Basics", "Complete blood count interpretation:\n\nRBC: 4.5-5.5 million/μL\nWBC: 4,000-11,000/μL\nPlatelets: 150,000-450,000/μL\nHemoglobin: 12-16 g/dL\nHematocrit: 37-47%", "Hematology", "CBC, blood, basic"),
            ("Diabetes Diagnosis", "Diagnostic criteria:\n\nFBS ≥ 126 mg/dL\nHbA1c ≥ 6.5%\nOGTT 2-hour ≥ 200 mg/dL\nRandom glucose ≥ 200 mg/dL with symptoms", "Clinical Chemistry", "diabetes, glucose, diagnosis"),
            ("Gram Staining Principle", "Gram-positive bacteria: Thick peptidoglycan layer retains crystal violet\n\nGram-negative bacteria: Thin peptidoglycan, outer membrane, lose crystal violet", "Microbiology", "gram stain, bacteria, microbiology")
        ]
        
        for note in notes:
            conn.execute("""
            INSERT INTO study_notes (topic, content, category, tags)
            VALUES (?, ?, ?, ?)
            """, note)
        
        conn.commit()
        st.success("✅ Comprehensive medical data loaded successfully!")
        
    except Exception as e:
        st.error(f"Data Insert Error: {str(e)}")
        conn.rollback()

# Insert comprehensive data
insert_comprehensive_data(conn)

# ==================== Translation System ====================

def t(key):
    """Enhanced translation system with more comprehensive coverage"""
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
            "history": "مێژوو",
            "statistics": "ئامار",
            "trends": "ڕەوتەکان",
            "comparison": "بەراورد",
            "alerts": "ئاگادارییەکان",
            "settings": "ڕێکخستنەکان",
            "help": "یارمەتی",
            "about": "دەربارە",
            "language": "زمان",
            "theme": "ڕووکار",
            "difficulty": "ئاستی قورسی",
            "duration": "ماوە",
            "category": "بەش"
        },
        
        "English 🇬🇧": {
            "dashboard": "📊 Dashboard",
            "disease_db": "🦠 Disease Database",
            "lab_tests": "🧪 Laboratory Tests",
            "practical": "🔬 Practical Tests",
            "theory": "📚 Study Notes",
            "results_entry": "📝 Results Entry",
            "reports": "📈 Reports & Analytics",
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
            "history": "History",
            "statistics": "Statistics",
            "trends": "Trends",
            "comparison": "Comparison",
            "alerts": "Alerts",
            "settings": "Settings",
            "help": "Help",
            "about": "About",
            "language": "Language",
            "theme": "Theme",
            "difficulty": "Difficulty Level",
            "duration": "Duration",
            "category": "Category"
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
            # Try to access by key or index
            return row[field]
        except:
            try:
                return row[f"{prefix}_en"]
            except:
                return str(row)

def get_desc(row):
    """Get localized description"""
    return get_name(row, "description")

# ==================== AI Integration ====================

def get_gemini_response(question):
    """Enhanced AI response with medical context"""
    try:
        api_key = os.environ.get("GEMINI_API_KEY", "")
        
        if api_key:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-pro")
            
            # Add medical context
            context = """
            You are a medical laboratory expert assistant. Provide accurate, 
            educational information about medical tests, diseases, and procedures.
            Always include disclaimers about consulting healthcare professionals.
            Keep responses concise but informative.
            """
            
            full_prompt = f"{context}\n\nQuestion: {question}"
            response = model.generate_content(full_prompt)
            return response.text
            
    except Exception as e:
        st.warning(f"AI service unavailable: {str(e)}")
    
    # Fallback responses with medical accuracy
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
        - Diabetes: 6.5% or higher
        
        Important for diagnosing and monitoring diabetes. Requires proper fasting for accurate results."""
    
    elif "anemia" in q or "hemoglobin" in q:
        return """**Anemia** is a condition where you lack enough healthy red blood cells:
        
        Common types:
        - **Iron Deficiency Anemia**: Most common, caused by insufficient iron
        - **Vitamin B12 Deficiency**: Pernicious anemia
        - **Thalassemia**: Genetic disorder affecting hemoglobin
        
        Symptoms: Fatigue, weakness, pale skin, shortness of breath
        
        Diagnosis: CBC, Iron studies, Vitamin B12, Folate levels"""
    
    return "Please ask a medical laboratory related question. I can help with test interpretation, disease information, and lab procedures."

# ==================== Enhanced Dashboard ====================

def render_dashboard():
    """Enhanced dashboard with comprehensive statistics and visualizations"""
    if conn is None:
        st.error("❌ Database connection failed")
        return
        
    st.markdown(f"""
    <div class="main-header">
        <h1>{t('dashboard')}</h1>
        <p>Medical Laboratory Management System Overview</p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        # Key Statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            cat_count = conn.execute("SELECT COUNT(*) as c FROM disease_categories").fetchone()['c']
            st.markdown(f"""
            <div class="stat-card">
                <h2 style="color: #FF6B6B;">{cat_count}</h2>
                <p>📂 Disease Categories</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            test_count = conn.execute("SELECT COUNT(*) as c FROM test_types").fetchone()['c']
            st.markdown(f"""
            <div class="stat-card">
                <h2 style="color: #4ECDC4;">{test_count}</h2>
                <p>🧪 Laboratory Tests</p>
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
        
        # Charts and Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Test Distribution by Category")
            
            # Get test distribution data
            test_dist = conn.execute("""
                SELECT category, COUNT(*) as count 
                FROM test_types 
                GROUP BY category
                ORDER BY count DESC
            """).fetchall()
            
            if test_dist:
                df_dist = pd.DataFrame([dict(r) for r in test_dist])
                fig = px.pie(df_dist, values='count', names='category', 
                           title="Tests by Category",
                           color_discrete_sequence=px.colors.qualitative.Set3)
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No test data available")
        
        with col2:
            st.markdown("### 🦠 Disease Severity Distribution")
            
            # Disease severity data
            severity_data = conn.execute("""
                SELECT severity, COUNT(*) as count 
                FROM diseases 
                GROUP BY severity
            """).fetchall()
            
            if severity_data:
                df_severity = pd.DataFrame([dict(r) for r in severity_data])
                fig = px.bar(df_severity, x='severity', y='count',
                           title="Diseases by Severity",
                           color='severity',
                           color_discrete_sequence=px.colors.qualitative.Set2)
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No disease data available")
        
        # Recent Results Section
        st.markdown("### 📝 Recent Test Results")
        
        recent_results = conn.execute("""
            SELECT tr.*, tt.name_en, tt.name_ku
            FROM test_results tr
            JOIN test_types tt ON tr.test_id = tt.id
            ORDER BY tr.date_performed DESC
            LIMIT 5
        """).fetchall()
        
        if recent_results:
            results_data = []
            for r in recent_results:
                rd = dict(r)
                results_data.append({
                    "Patient": rd['patient_name'],
                    "Test": get_name(rd),
                    "Result": f"{rd['result_value']}",
                    "Date": rd['date_performed'],
                    "Status": "⚠️ Abnormal" if rd['is_abnormal'] else "✅ Normal"
                })
            
            df_results = pd.DataFrame(results_data)
            st.dataframe(df_results, use_container_width=True, hide_index=True)
        else:
            st.info("No test results recorded yet")
            
        # Quick Actions
        st.markdown("### ⚡ Quick Actions")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🧪 Order New Test", use_container_width=True, type="primary"):
                st.session_state['nav_page'] = 'results'
                st.rerun()
                
        with col2:
            if st.button("🔍 Search Diseases", use_container_width=True):
                st.session_state['nav_page'] = 'diseases'
                st.rerun()
                
        with col3:
            if st.button("📊 View Reports", use_container_width=True):
                st.session_state['nav_page'] = 'reports'
                st.rerun()
                
        with col4:
            if st.button("🤖 Ask AI Assistant", use_container_width=True):
                st.session_state['nav_page'] = 'ai'
                st.rerun()
                
    except Exception as e:
        st.error(f"Dashboard Error: {str(e)}")

# ==================== Enhanced Diseases Module ====================

def render_diseases():
    """Enhanced disease database with search and filter capabilities"""
    if conn is None:
        return
        
    st.markdown(f"""
    <div class="main-header">
        <h1>{t('disease_db')}</h1>
        <p>Comprehensive Medical Disease Database</p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        # Search and Filter
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
        
        # Build query with filters
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
        
        # Display diseases in cards
        for i in range(0, len(diseases), 2):
            cols = st.columns(2)
            
            for j in range(2):
                if i + j < len(diseases):
                    disease = dict(diseases[i + j])
                    
                    with cols[j]:
                        with st.container():
                            st.markdown(f"""
                            <div class="category-card" style="border-right-color: {disease.get('color', '#1565c0')};">
                                <h3>{disease.get('icon', '🦠')} {get_name(disease)}</h3>
                                <p><strong>{t('category')}:</strong> {get_name(disease, 'cat')}</p>
                                <p><strong>{t('severity')}:</strong> {disease['severity']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            with st.expander(f"{t('details')} - {get_name(disease)}"):
                                # Description
                                st.markdown(f"#### {t('description')}")
                                st.write(get_desc(disease))
                                
                                # Symptoms
                                st.markdown(f"#### {t('symptoms')}")
                                symptoms = get_name(disease, 'symptoms')
                                if symptoms:
                                    symptom_list = [s.strip() for s in symptoms.split(',') if s.strip()]
                                    for s in symptom_list:
                                        st.markdown(f"<span class='symptom-tag'>{s}</span>", 
                                                  unsafe_allow_html=True)
                                
                                # Causes
                                if disease.get('causes_en') or disease.get('causes_ku'):
                                    st.markdown(f"#### {t('causes')}")
                                    st.write(get_name(disease, 'causes'))
                                
                                # Treatment
                                if disease.get('treatment_en') or disease.get('treatment_ku'):
                                    st.markdown(f"#### {t('treatment')}")
                                    st.write(get_name(disease, 'treatment'))
                                
                                # Related Tests
                                st.markdown("#### Related Laboratory Tests")
                                related_tests = conn.execute("""
                                    SELECT name_en, name_ku FROM test_types 
                                    WHERE category = (
                                        SELECT name_en FROM disease_categories WHERE id = ?
                                    )
                                    LIMIT 5
                                """, (disease['category_id'],)).fetchall()
                                
                                if related_tests:
                                    for test in related_tests:
                                        st.markdown(f"- {get_name(dict(test))}")
                                else:
                                    st.write("No related tests found")
                                
    except Exception as e:
        st.error(f"Disease Database Error: {str(e)}")

# ==================== Enhanced Tests Module ====================

def render_tests():
    """Enhanced laboratory tests display with detailed information"""
    if conn is None:
        return
        
    st.markdown(f"""
    <div class="main-header">
        <h1>{t('lab_tests')}</h1>
        <p>Complete Laboratory Test Reference Guide</p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        # Search and filter
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            search_test = st.text_input(t('search'), placeholder="Search by name or category...")
        
        with col2:
            categories = conn.execute("SELECT DISTINCT category FROM test_types ORDER BY category").fetchall()
            category_list = ["All"] + [c['category'] for c in categories]
            selected_cat = st.selectbox(t('category'), category_list)
        
        with col3:
            sort_by = st.selectbox("Sort by", ["Name", "Category", "Price"])
        
        # Get tests
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
        
        # Group and display
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
                        <table style="width:100%; border-collapse: collapse;">
                            <tr>
                                <td style="padding: 8px;"><strong>{t('unit')}:</strong> {test['unit']}</td>
                                <td style="padding: 8px;"><strong>Price:</strong> ${test.get('price', 'N/A')}</td>
                                <td style="padding: 8px;"><strong>Turnaround:</strong> {test.get('turnaround_time', 'N/A')}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px;" colspan="3">
                                    <strong class="normal-range">{t('normal_range')}: {test['normal_range_low']} - {test['normal_range_high']} {test['unit']}</strong>
                                </td>
                            </tr>
                        </table>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    with st.expander(f"More details for {get_name(test)}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"#### {t('description')}")
                            st.write(get_desc(test))
                            
                            if test.get('preparation_en') or test.get('preparation_ku'):
                                st.markdown(f"#### Patient Preparation")
                                st.info(get_name(test, 'preparation'))
                        
                        with col2:
                            st.markdown(f"#### {t('critical_values')}")
                            
                            crit_low = test['critical_low']
                            crit_high = test['critical_high']
                            
                            st.markdown(f"""
                            <div class="critical-box">
                                <p>🔴 <strong>{t('low')}:</strong> < {crit_low} {test['unit']}</p>
                                <p>🔴 <strong>{t('high')}:</strong> > {crit_high} {test['unit']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Visual range indicator
                            try:
                                fig = go.Figure()
                                
                                # Normal range
                                fig.add_trace(go.Bar(
                                    x=[test['normal_range_high'] - test['normal_range_low']],
                                    y=['Test Range'],
                                    base=test['normal_range_low'],
                                    orientation='h',
                                    marker_color='green',
                                    name='Normal Range',
                                    text=[f"{test['normal_range_low']}-{test['normal_range_high']}"],
                                    textposition='inside'
                                ))
                                
                                # Critical ranges
                                fig.add_vline(x=crit_low, line_dash="dash", line_color="red", 
                                            annotation_text=f"Critical Low: {crit_low}")
                                fig.add_vline(x=crit_high, line_dash="dash", line_color="red", 
                                            annotation_text=f"Critical High: {crit_high}")
                                
                                fig.update_layout(
                                    title=f"Reference Ranges for {get_name(test)}",
                                    xaxis_title=f"Value ({test['unit']})",
                                    showlegend=False,
                                    height=200
                                )
                                
                                st.plotly_chart(fig, use_container_width=True)
                            except:
                                pass  # Skip chart if data is not numeric
                        
    except Exception as e:
        st.error(f"Tests Display Error: {str(e)}")

# ==================== Practical Tests Module ====================

def render_practical():
    """Practical tests module with step-by-step instructions"""
    if conn is None:
        return
        
    st.markdown(f"""
    <div class="main-header">
        <h1>{t('practical')}</h1>
        <p>Laboratory Practical Tests & Procedures</p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        # Filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            categories = conn.execute("SELECT DISTINCT category FROM practical_tests ORDER BY category").fetchall()
            cat_list = ["All"] + [c['category'] for c in categories]
            selected_cat = st.selectbox(t('category'), cat_list)
        
        with col2:
            difficulty = st.selectbox(t('difficulty'), ["All", "Basic", "Intermediate", "Advanced"])
        
        with col3:
            search_practical = st.text_input(t('search'), placeholder="Search practical tests...")
        
        # Build query
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
                <h3>🔬 {get_name(p, 'title')}</h3>
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
                # Description
                st.markdown(f"#### {t('description')}")
                st.write(get_desc(p))
                
                # Procedure Steps
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
                    # Materials
                    st.markdown(f"#### {t('materials')}")
                    materials = get_name(p, 'materials')
                    if materials:
                        mat_list = [m.strip() for m in materials.split(',')]
                        for mat in mat_list:
                            if mat:
                                st.markdown(f"- {mat}")
                    
                    # Expected Results
                    st.markdown(f"#### {t('expected_results')}")
                    st.write(get_name(p, 'expected_results'))
                
                with col2:
                    # Interpretation
                    st.markdown(f"#### {t('interpretation')}")
                    st.write(get_name(p, 'interpretation'))
                    
                    # Precautions
                    st.markdown(f"#### {t('precautions')}")
                    precautions = get_name(p, 'precautions')
                    if precautions:
                        st.warning(precautions)
                
    except Exception as e:
        st.error(f"Practical Tests Error: {str(e)}")

# ==================== Study Notes Module ====================

def render_notes():
    """Study notes module for laboratory theory"""
    if conn is None:
        return
        
    st.markdown(f"""
    <div class="main-header">
        <h1>{t('theory')}</h1>
        <p>Laboratory Theory & Study Notes</p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        # Add new note form
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
        
        # Search notes
        search_note = st.text_input(t('search'), placeholder="Search notes...")
        
        # Get notes
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
                
                # Delete button
                if st.button(f"🗑️ {t('delete')}", key=f"del_{n['id']}"):
                    conn.execute("DELETE FROM study_notes WHERE id = ?", (n['id'],))
                    conn.commit()
                    st.rerun()
                
    except Exception as e:
        st.error(f"Study Notes Error: {str(e)}")

# ==================== Enhanced Results Entry ====================

def render_results():
    """Enhanced results entry with validation and alerts"""
    if conn is None:
        return
        
    st.markdown(f"""
    <div class="main-header">
        <h1>{t('results_entry')}</h1>
        <p>Enter and Validate Laboratory Test Results</p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        # Split into two columns
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
                
                # Organized test selection
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
                            <p><strong>Price:</strong> ${selected_test.get('price', 'N/A')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        result_value = st.number_input(
                            f"{t('result_value')} ({selected_test['unit']})",
                            step=0.01,
                            format="%.2f"
                        )
                        
                        notes = st.text_area("Additional Notes", placeholder="Any observations or comments...")
                        
                        submitted = st.form_submit_button(t('save_result'), use_container_width=True)
                        
                        if submitted:
                            if not name:
                                st.error("Please enter patient name")
                            elif selected_category == "Select Category...":
                                st.error("Please select a test category")
                            else:
                                # Determine status
                                is_abnormal = 0
                                is_critical = 0
                                
                                if result_value < selected_test['normal_range_low'] or result_value > selected_test['normal_range_high']:
                                    is_abnormal = 1
                                    
                                if result_value < selected_test['critical_low'] or result_value > selected_test['critical_high']:
                                    is_critical = 1
                                
                                # Save result
                                conn.execute("""
                                    INSERT INTO test_results 
                                    (patient_name, patient_age, patient_gender, test_id, 
                                     result_value, is_abnormal, is_critical, notes)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                """, (name, age, gender, selected_test['id'], 
                                     result_value, is_abnormal, is_critical, notes))
                                
                                conn.commit()
                                
                                st.success(t('saved_success'))
                                
                                # Show alert if critical
                                if is_critical:
                                    st.error("🚨 CRITICAL VALUE ALERT! Immediate action required!")
                                    st.markdown(f"""
                                    <div class="critical-box">
                                        <h4>⚠️ Critical Result for {get_name(selected_test)}</h4>
                                        <p>Patient: {name}</p>
                                        <p>Result: {result_value} {selected_test['unit']}</p>
                                        <p>Critical Range: < {selected_test['critical_low']} or > {selected_test['critical_high']}</p>
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

# ==================== Enhanced Reports ====================

def render_reports():
    """Enhanced reports with analytics and visualizations"""
    if conn is None:
        return
        
    st.markdown(f"""
    <div class="main-header">
        <h1>{t('reports')}</h1>
        <p>Laboratory Analytics and Reporting Dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        # Date range filter
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            date_from = st.date_input("From Date", datetime.now() - timedelta(days=30))
        with col2:
            date_to = st.date_input("To Date", datetime.now())
        
        # Get filtered results
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
        
        # Add localized name
        df['test_name'] = df.apply(lambda row: get_name(row), axis=1)
        
        # Summary Statistics
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
            st.metric("Critical Values", critical_count, 
                     delta_color="inverse" if critical_count > 0 else "normal")
        
        # Charts
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Test Distribution")
            
            test_counts = df['test_name'].value_counts().head(10)
            if len(test_counts) > 0:
                fig = px.bar(x=test_counts.index, y=test_counts.values,
                            title="Top 10 Most Ordered Tests",
                            labels={'x': 'Test Name', 'y': 'Count'},
                            color=test_counts.values,
                            color_continuous_scale='Viridis')
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Abnormal Results by Category")
            
            category_abnormal = df.groupby('category')['is_abnormal'].agg(['sum', 'count'])
            if len(category_abnormal) > 0:
                category_abnormal['rate'] = (category_abnormal['sum'] / category_abnormal['count'] * 100)
                
                fig = px.bar(category_abnormal, y=category_abnormal.index, x='rate',
                            title="Abnormal Rate by Test Category (%)",
                            orientation='h',
                            color='rate',
                            color_continuous_scale='RdYlGn_r')
                st.plotly_chart(fig, use_container_width=True)
        
        # Detailed Results Table
        st.markdown("### 📋 Detailed Results")
        
        display_cols = ['patient_name', 'patient_age', 'patient_gender', 
                       'test_name', 'result_value', 'unit', 'date_performed']
        display_cols = [c for c in display_cols if c in df.columns]
        
        # Add status column
        df['Status'] = df.apply(lambda row: 
                               '🚨 CRITICAL' if row['is_critical'] else 
                               '⚠️ ABNORMAL' if row['is_abnormal'] else 
                               '✅ NORMAL', axis=1)
        
        st.dataframe(df[display_cols + ['Status']], use_container_width=True, hide_index=True)
        
        # Export options
        col1, col2 = st.columns(2)
        
        with col1:
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Export to CSV",
                data=csv,
                file_name=f"lab_results_{date_from}_{date_to}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            if st.button("🖨️ Print Report", use_container_width=True):
                st.info("Print functionality - Use browser print (Ctrl+P)")
                
    except Exception as e:
        st.error(f"Reports Error: {str(e)}")

# ==================== Enhanced AI Chat ====================

def render_ai_chat():
    """Enhanced AI chat with medical context and history"""
    st.markdown(f"""
    <div class="main-header">
        <h1>{t('ai_chat')}</h1>
        <p>Medical Laboratory AI Assistant - Ask any lab-related questions</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Suggested questions
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
    
    # Create rows of 4 buttons each
    for i in range(0, len(suggestions), 4):
        cols = st.columns(4)
        for j in range(4):
            if i + j < len(suggestions):
                with cols[j]:
                    if st.button(suggestions[i + j], key=f"sug_{i+j}", use_container_width=True):
                        st.session_state.chat_input = suggestions[i + j]
    
    # Chat interface
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    chat_container = st.container()
    
    with chat_container:
        for i, chat in enumerate(st.session_state.chat_history):
            with st.chat_message("user"):
                st.write(chat['question'])
            
            with st.chat_message("assistant"):
                st.markdown(chat['answer'])
                
                # Add feedback buttons
                col1, col2, col3 = st.columns([1, 1, 8])
                with col1:
                    if st.button("👍", key=f"like_{i}"):
                        st.success("Thanks for your feedback!")
                with col2:
                    if st.button("👎", key=f"dislike_{i}"):
                        st.error("We'll improve our responses")
    
    # Chat input
    if 'chat_input' not in st.session_state:
        st.session_state.chat_input = ""
    
    question = st.chat_input(t('type_question'))
    
    if question:
        # Add user message
        st.session_state.chat_history.append({
            "question": question,
            "answer": ""
        })
        
        # Display user message
        with st.chat_message("user"):
            st.write(question)
        
        # Generate and display response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Analyzing your question..."):
                # Add relevant context from database
                context = ""
                
                # Check if question relates to any disease in database
                try:
                    diseases = conn.execute("SELECT name_en, name_ku, description_en FROM diseases").fetchall()
                    for disease in diseases:
                        d = dict(disease)
                        if d['name_en'].lower() in question.lower() or d['name_ku'].lower() in question.lower():
                            context += f"\nRelevant disease: {d['name_en']} - {d['description_en']}"
                except:
                    pass
                
                answer = get_gemini_response(context + "\n" + question if context else question)
                
                st.markdown(answer)
                
                # Save answer to history
                st.session_state.chat_history[-1]['answer'] = answer
    
    # Clear chat button
    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

# ==================== Main Application ====================

def main():
    """Main application with enhanced navigation and features"""
    
    # Initialize session state
    if 'language' not in st.session_state:
        st.session_state.language = "کوردی 🇹🇯"
    
    if 'nav_page' not in st.session_state:
        st.session_state.nav_page = "dashboard"
    
    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 20px 0;">
            <h2 style="color: #1565c0;">🔬 MediLab Pro</h2>
            <p style="color: #666;">Advanced Medical Laboratory System</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Language selection
        language = st.selectbox(
            "🌐 Language / زمان",
            ["کوردی 🇹🇯", "English 🇬🇧"],
            key="lang_selector"
        )
        
        if language != st.session_state.language:
            st.session_state.language = language
            st.rerun()
        
        st.markdown("---")
        
        # Navigation
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
        
        # System info
        st.markdown("### ℹ️ System Info")
        
        try:
            db_size = os.path.getsize('medical_lab.db') / (1024 * 1024)
            st.caption(f"Database Size: {db_size:.2f} MB")
        except:
            st.caption("Database: Connected")
        
        st.caption(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        # Test counts
        try:
            total_results = conn.execute("SELECT COUNT(*) as c FROM test_results").fetchone()['c']
            st.caption(f"Total Test Results: {total_results}")
        except:
            pass
        
        st.markdown("---")
        
        # Credits
        st.markdown("""
        <div style="text-align: center; padding: 10px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 10px; color: white;">
            <p style="margin: 5px 0;"><strong>🎓 دانیال ئیسماعیل</strong></p>
            <p style="margin: 5px 0; font-size: 0.9em;">قۆناغی چوارەم - تاقیگەی پزیشکی</p>
            <p style="margin: 5px 0; font-size: 0.8em;">© 2024 All Rights Reserved</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Student Info Header
    st.markdown("""
    <div class="student-info">
        <h2>🎓 دانیال ئیسماعیل</h2>
        <p>قۆناغی چوارەم - بەشی تاقیگەی پزیشکی</p>
        <p style="font-size: 0.9em; opacity: 0.9;">سیستەمی بەڕێوەبردنی تاقیگەی پزیشکی</p>
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
        st.info("Please try refreshing the page or contact support.")
    
    # Footer
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; padding: 10px; color: #666;">
        <p>🔬 Medical Laboratory Management System | Version 2.0</p>
        <p style="font-size: 0.8em;">Developed for educational purposes | Always consult healthcare professionals</p>
    </div>
    """, unsafe_allow_html=True)

# ==================== Run Application ====================

if __name__ == "__main__":
    if conn:
        main()
    else:
        st.error("❌ Failed to connect to database. Please check your configuration.")
        st.info("Make sure SQLite is installed and the application has write permissions.")
