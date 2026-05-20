import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import json
from typing import Dict, List, Optional
import plotly.express as px
import plotly.graph_objects as go
from itertools import groupby

# ==================== Translations ====================
TRANSLATIONS = {
    "English 🇬🇧": {
        "app_title": "🔬 Medical Laboratory Analysis System",
        "app_subtitle": "Fourth Stage - Disease Analysis",
        "app_description": "Comprehensive reference for all laboratory tests and disease analysis",
        "dashboard": "📊 Dashboard",
        "disease_db": "🦠 Disease Database",
        "lab_tests": "🧪 Laboratory Tests",
        "practical": "🔬 Practical Tests",
        "theory": "📚 Theory Questions",
        "results_entry": "📝 Test Results Entry",
        "reports": "📈 Reports & Analytics",
        "nav_title": "🔬 Navigation",
        "select_section": "Select Section",
        "quick_info": "📋 Quick Info",
        "quick_info_text": "This system contains comprehensive medical laboratory test information for 4th stage students.",
        "disease_categories": "Disease Categories",
        "laboratory_tests": "Laboratory Tests",
        "diseases": "Diseases",
        "practical_tests": "Practical Tests",
        "categories_overview": "📂 Disease Categories",
        "quick_reference": "🧪 Quick Reference - Common Tests",
        "filter_category": "Filter by Category",
        "all_categories": "All Categories",
        "search": "🔍 Search",
        "search_diseases": "Search Diseases",
        "description": "Description",
        "symptoms": "Symptoms",
        "category": "Category",
        "related_tests": "Related Tests",
        "test_category": "Test Category",
        "search_tests": "Search Tests",
        "unit": "Unit",
        "normal_range": "Normal Range",
        "critical_values": "⚠️ Critical Values",
        "low": "Low",
        "high": "High",
        "procedure": "📝 Procedure Steps",
        "materials": "🧫 Materials Required",
        "expected_results": "✅ Expected Results",
        "interpretation": "🔍 Interpretation",
        "duration": "Duration",
        "difficulty": "Difficulty",
        "add_notes": "📝 Add Study Notes",
        "topic": "Topic",
        "content": "Note Content",
        "save_note": "Save Note",
        "your_notes": "📖 Your Study Notes",
        "delete": "Delete",
        "patient_name": "Patient Name",
        "patient_age": "Patient Age",
        "patient_gender": "Patient Gender",
        "select_test": "Select Test",
        "result_value": "Result Value",
        "result_text": "Result Text (optional)",
        "additional_notes": "Additional Notes",
        "save_result": "Save Result",
        "total_tests": "Total Tests",
        "abnormal_results": "Abnormal Results",
        "normal_rate": "Normal Rate",
        "tests_by_category": "Tests by Category",
        "normal_vs_abnormal": "Normal vs Abnormal Results",
        "recent_results": "📋 Recent Results",
        "no_results": "No test results recorded yet.",
        "abnormal_warning": "⚠️ Abnormal result detected!",
        "saved_success": "✅ Saved successfully!",
        "note_saved": "✅ Note saved!",
        "please_wait": "Please wait...",
        "minutes": "minutes",
        "basic": "Basic",
        "intermediate": "Intermediate", 
        "advanced": "Advanced",
        "gender_male": "Male",
        "gender_female": "Female",
        "gender_other": "Other",
        "created": "Created",
        "hematology": "Hematology",
        "microbiology": "Microbiology",
        "clinical_chemistry": "Clinical Chemistry",
        "immunology": "Immunology",
        "parasitology": "Parasitology",
        "urinalysis": "Urinalysis",
        "histopathology": "Histopathology",
        "serology": "Serology",
    },
    "کوردی 🇮🇶": {
        "app_title": "🔬 سیستەمی شیکردنەوەی تاقیگەی پزیشکی",
        "app_subtitle": "قۆناغی چوارەم - شیکردنەوەی نەخۆشییەکان",
        "app_description": "سەرچاوەیەکی گشتگیر بۆ هەموو پشکنینە تاقیگەییەکان و شیکردنەوەی نەخۆشییەکان",
        "dashboard": "📊 داشبۆرد",
        "disease_db": "🦠 بنکەدراوەی نەخۆشییەکان",
        "lab_tests": "🧪 پشکنینە تاقیگەییەکان",
        "practical": "🔬 پشکنینی پراکتیکی",
        "theory": "📚 پرسیاری تیۆری",
        "results_entry": "📝 تۆمارکردنی ئەنجامەکان",
        "reports": "📈 ڕاپۆرت و ئامارەکان",
        "nav_title": "🔬 ڕێنیشاندەر",
        "select_section": "بەش هەڵبژێرە",
        "quick_info": "📋 زانیاری خێرا",
        "quick_info_text": "ئەم سیستەمە زانیاری گشتگیری پشکنینە تاقیگەییەکانی پزیشکی بۆ قوتابیانی قۆناغی چوارەم لەخۆدەگرێت.",
        "disease_categories": "بەشەکانی نەخۆشی",
        "laboratory_tests": "پشکنینە تاقیگەییەکان",
        "diseases": "نەخۆشییەکان",
        "practical_tests": "پشکنینە پراکتیکییەکان",
        "categories_overview": "📂 بەشەکانی نەخۆشییەکان",
        "quick_reference": "🧪 سەرچاوەی خێرا - پشکنینە باوەکان",
        "filter_category": "پاڵێوکردن بەپێی بەش",
        "all_categories": "هەموو بەشەکان",
        "search": "🔍 گەڕان",
        "search_diseases": "گەڕان بەدوای نەخۆشییەکان",
        "description": "ڕوونکردنەوە",
        "symptoms": "نیشانەکان",
        "category": "بەش",
        "related_tests": "پشکنینە پەیوەندیدارەکان",
        "test_category": "بەشی پشکنین",
        "search_tests": "گەڕان بەدوای پشکنینەکان",
        "unit": "یەکە",
        "normal_range": "مەودای ئاسایی",
        "critical_values": "⚠️ بەهای مەترسیدار",
        "low": "نزم",
        "high": "بەرز",
        "procedure": "📝 هەنگاوەکانی پڕۆسێجەر",
        "materials": "🧫 کەرەستە پێویستەکان",
        "expected_results": "✅ ئەنجامی چاوەڕوانکراو",
        "interpretation": "🔍 لێکدانەوە",
        "duration": "ماوە",
        "difficulty": "ئاستی قورسی",
        "add_notes": "📝 زیادکردنی تێبینی خوێندن",
        "topic": "بابەت",
        "content": "ناوەڕۆکی تێبینی",
        "save_note": "تۆمارکردنی تێبینی",
        "your_notes": "📖 تێبینییەکانی خوێندنت",
        "delete": "سڕینەوە",
        "patient_name": "ناوی نەخۆش",
        "patient_age": "تەمەنی نەخۆش",
        "patient_gender": "ڕەگەزی نەخۆش",
        "select_test": "پشکنین هەڵبژێرە",
        "result_value": "بەهای ئەنجام",
        "result_text": "دەقی ئەنجام (ئارەزوومەندانە)",
        "additional_notes": "تێبینی زیادە",
        "save_result": "تۆمارکردنی ئەنجام",
        "total_tests": "کۆی گشتی پشکنینەکان",
        "abnormal_results": "ئەنجامە نائاساییەکان",
        "normal_rate": "ڕێژەی ئاسایی",
        "tests_by_category": "پشکنینەکان بەپێی بەش",
        "normal_vs_abnormal": "ئاسایی بەرامبەر نائاسایی",
        "recent_results": "📋 دوایین ئەنجامەکان",
        "no_results": "هێشتا هیچ ئەنجامێکی پشکنین تۆمار نەکراوە.",
        "abnormal_warning": "⚠️ ئەنجامی نائاسایی دۆزرایەوە!",
        "saved_success": "✅ بە سەرکەوتوویی تۆمارکرا!",
        "note_saved": "✅ تێبینییەکە تۆمارکرا!",
        "please_wait": "تکایە چاوەڕێ بکە...",
        "minutes": "خولەک",
        "basic": "سەرەتایی",
        "intermediate": "ناوەندی", 
        "advanced": "پێشکەوتوو",
        "gender_male": "نێر",
        "gender_female": "مێ",
        "gender_other": "هی تر",
        "created": "دروستکراوە",
        "hematology": "خوێنناسی",
        "microbiology": "مایکرۆبایۆلۆجی",
        "clinical_chemistry": "کیمیای کلینیکی",
        "immunology": "ئیمیونۆلۆجی",
        "parasitology": "مشقوڕخوێناسی",
        "urinalysis": "شیکردنەوەی میز",
        "histopathology": "هیستۆپاتۆلۆجی",
        "serology": "سیرۆلۆجی",
    },
    "العربية 🇮🇶": {
        "app_title": "🔬 نظام تحليل المختبرات الطبية",
        "app_subtitle": "المرحلة الرابعة - تحليل الأمراض",
        "app_description": "مرجع شامل لجميع الفحوصات المخبرية وتحليل الأمراض",
        "dashboard": "📊 لوحة القيادة",
        "disease_db": "🦠 قاعدة بيانات الأمراض",
        "lab_tests": "🧪 الفحوصات المخبرية",
        "practical": "🔬 الفحوصات العملية",
        "theory": "📚 الأسئلة النظرية",
        "results_entry": "📝 إدخال النتائج",
        "reports": "📈 التقارير والتحليلات",
        "nav_title": "🔬 التنقل",
        "select_section": "اختر القسم",
        "quick_info": "📋 معلومات سريعة",
        "quick_info_text": "يحتوي هذا النظام على معلومات شاملة عن الفحوصات المخبرية الطبية لطلاب المرحلة الرابعة.",
        "disease_categories": "فئات الأمراض",
        "laboratory_tests": "الفحوصات المخبرية",
        "diseases": "الأمراض",
        "practical_tests": "الفحوصات العملية",
        "categories_overview": "📂 فئات الأمراض",
        "quick_reference": "🧪 مرجع سريع - الفحوصات الشائعة",
        "filter_category": "تصفية حسب الفئة",
        "all_categories": "جميع الفئات",
        "search": "🔍 بحث",
        "search_diseases": "بحث عن الأمراض",
        "description": "الوصف",
        "symptoms": "الأعراض",
        "category": "الفئة",
        "related_tests": "الفحوصات ذات الصلة",
        "test_category": "فئة الفحص",
        "search_tests": "بحث عن الفحوصات",
        "unit": "الوحدة",
        "normal_range": "المدى الطبيعي",
        "critical_values": "⚠️ القيم الحرجة",
        "low": "منخفض",
        "high": "مرتفع",
        "procedure": "📝 خطوات الإجراء",
        "materials": "🧫 المواد المطلوبة",
        "expected_results": "✅ النتائج المتوقعة",
        "interpretation": "🔍 التفسير",
        "duration": "المدة",
        "difficulty": "مستوى الصعوبة",
        "add_notes": "📝 إضافة ملاحظات دراسية",
        "topic": "الموضوع",
        "content": "محتوى الملاحظة",
        "save_note": "حفظ الملاحظة",
        "your_notes": "📖 ملاحظاتك الدراسية",
        "delete": "حذف",
        "patient_name": "اسم المريض",
        "patient_age": "عمر المريض",
        "patient_gender": "جنس المريض",
        "select_test": "اختر الفحص",
        "result_value": "قيمة النتيجة",
        "result_text": "نص النتيجة (اختياري)",
        "additional_notes": "ملاحظات إضافية",
        "save_result": "حفظ النتيجة",
        "total_tests": "إجمالي الفحوصات",
        "abnormal_results": "نتائج غير طبيعية",
        "normal_rate": "معدل الطبيعي",
        "tests_by_category": "الفحوصات حسب الفئة",
        "normal_vs_abnormal": "طبيعي مقابل غير طبيعي",
        "recent_results": "📋 النتائج الحديثة",
        "no_results": "لم يتم تسجيل أي نتائج بعد.",
        "abnormal_warning": "⚠️ تم اكتشاف نتيجة غير طبيعية!",
        "saved_success": "✅ تم الحفظ بنجاح!",
        "note_saved": "✅ تم حفظ الملاحظة!",
        "please_wait": "يرجى الانتظار...",
        "minutes": "دقيقة",
        "basic": "أساسي",
        "intermediate": "متوسط", 
        "advanced": "متقدم",
        "gender_male": "ذكر",
        "gender_female": "أنثى",
        "gender_other": "آخر",
        "created": "تم الإنشاء",
        "hematology": "أمراض الدم",
        "microbiology": "الأحياء الدقيقة",
        "clinical_chemistry": "الكيمياء السريرية",
        "immunology": "المناعة",
        "parasitology": "الطفيليات",
        "urinalysis": "تحليل البول",
        "histopathology": "هيستوباثولوجي",
        "serology": "الأمصال",
    }
}

# ==================== Database Setup ====================
class LabDatabase:
    def __init__(self):
        self.conn = sqlite3.connect('medical_lab.db', check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
        self._insert_reference_data()
    
    def _create_tables(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS disease_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name_en TEXT NOT NULL,
                name_ku TEXT NOT NULL,
                name_ar TEXT NOT NULL,
                description_en TEXT,
                description_ku TEXT,
                description_ar TEXT,
                icon TEXT
            );
            
            CREATE TABLE IF NOT EXISTS diseases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER,
                name_en TEXT NOT NULL,
                name_ku TEXT NOT NULL,
                name_ar TEXT NOT NULL,
                description_en TEXT,
                description_ku TEXT,
                description_ar TEXT,
                symptoms_en TEXT,
                symptoms_ku TEXT,
                symptoms_ar TEXT,
                FOREIGN KEY (category_id) REFERENCES disease_categories(id)
            );
            
            CREATE TABLE IF NOT EXISTS test_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name_en TEXT NOT NULL,
                name_ku TEXT NOT NULL,
                name_ar TEXT NOT NULL,
                category TEXT,
                unit TEXT,
                normal_range_low REAL,
                normal_range_high REAL,
                critical_low REAL,
                critical_high REAL,
                description_en TEXT,
                description_ku TEXT,
                description_ar TEXT
            );
            
            CREATE TABLE IF NOT EXISTS practical_tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title_en TEXT NOT NULL,
                title_ku TEXT NOT NULL,
                title_ar TEXT NOT NULL,
                description_en TEXT,
                description_ku TEXT,
                description_ar TEXT,
                category TEXT,
                steps_en TEXT,
                steps_ku TEXT,
                steps_ar TEXT,
                materials_en TEXT,
                materials_ku TEXT,
                materials_ar TEXT,
                expected_results_en TEXT,
                expected_results_ku TEXT,
                expected_results_ar TEXT,
                interpretation_en TEXT,
                interpretation_ku TEXT,
                interpretation_ar TEXT,
                duration_minutes INTEGER,
                difficulty_level TEXT
            );
            
            CREATE TABLE IF NOT EXISTS study_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT,
                content TEXT,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_name TEXT,
                patient_age INTEGER,
                patient_gender TEXT,
                test_id INTEGER,
                result_value REAL,
                result_text TEXT,
                is_abnormal BOOLEAN,
                notes TEXT,
                date_performed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (test_id) REFERENCES test_types(id)
            );
        """)
        self.conn.commit()
    
    def _insert_reference_data(self):
        # Disease Categories with trilingual names
        categories = [
            ("Hematology", "خوێنناسی", "أمراض الدم", 
             "Blood disorders and diseases", "نەخۆشی و تێکچوونەکانی خوێن", "اضطرابات وأمراض الدم", "🩸"),
            ("Microbiology", "مایکرۆبایۆلۆجی", "الأحياء الدقيقة",
             "Bacterial, viral, fungal infections", "هەوکردنی بەکتریایی، ڤایرۆسی، کەڕوویی", "الالتهابات البكتيرية والفيروسية والفطرية", "🦠"),
            ("Clinical Chemistry", "کیمیای کلینیکی", "الكيمياء السريرية",
             "Chemical analysis of body fluids", "شیکردنەوەی کیمیایی شلەکانی لەش", "التحليل الكيميائي لسوائل الجسم", "🧪"),
            ("Immunology", "ئیمیونۆلۆجی", "المناعة",
             "Immune system disorders", "تێکچوونەکانی سیستەمی بەرگری", "اضطرابات الجهاز المناعي", "🛡️"),
            ("Parasitology", "مشقوڕخوێناسی", "الطفيليات",
             "Parasitic infections", "هەوکردنی مشقوڕخوەکان", "الالتهابات الطفيلية", "🐛"),
            ("Urinalysis", "شیکردنەوەی میز", "تحليل البول",
             "Urine analysis", "شیکردنەوەی میز", "تحليل البول", "💧"),
            ("Serology", "سیرۆلۆجی", "الأمصال",
             "Blood serum analysis", "شیکردنەوەی شلەی خوێن", "تحليل مصل الدم", "💉"),
            ("Histopathology", "هیستۆپاتۆلۆجی", "هيستوباثولوجي",
             "Tissue examination", "پشکنینی شانەکان", "فحص الأنسجة", "🔬")
        ]
        
        for cat in categories:
            self.conn.execute("""
                INSERT OR IGNORE INTO disease_categories 
                (name_en, name_ku, name_ar, description_en, description_ku, description_ar, icon) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, cat)
        
        # Laboratory Tests with trilingual names
        tests = [
            # Hematology
            ("CBC - Complete Blood Count", "CBC - ژماردنی تەواوی خوێن", "CBC - تعداد الدم الكامل",
             "Hematology", "cells/μL", 4.5, 11.0, 2.0, 15.0,
             "Complete blood cell count", "ژماردنی تەواوی خانەکانی خوێن", "تعداد خلايا الدم الكامل"),
            
            ("WBC Count", "ژماردنی WBC", "تعداد كريات الدم البيضاء",
             "Hematology", "×10³/μL", 4.0, 11.0, 2.0, 30.0,
             "White blood cell count", "ژماردنی خانە سپییەکانی خوێن", "تعداد خلايا الدم البيضاء"),
            
            ("Hemoglobin", "هیمۆگلۆبین", "الهيموجلوبين",
             "Hematology", "g/dL", 12.0, 16.0, 6.0, 20.0,
             "Hemoglobin level", "ئاستی هیمۆگلۆبین", "مستوى الهيموجلوبين"),
            
            # Clinical Chemistry
            ("Blood Glucose Fasting", "گلوکۆزی خوێن بە بەڕۆژوویی", "سكر الدم صائم",
             "Clinical Chemistry", "mg/dL", 70, 100, 40, 300,
             "Fasting blood sugar", "شەکری خوێن بە بەڕۆژوویی", "سكر الدم أثناء الصيام"),
            
            ("HbA1c", "HbA1c", "السكر التراكمي",
             "Clinical Chemistry", "%", 4.0, 5.6, 3.0, 10.0,
             "Glycated hemoglobin", "هیمۆگلۆبینی گڵایکەیتکراو", "الهيموجلوبين السكري"),
            
            ("Creatinine", "کریاتینین", "الكرياتينين",
             "Clinical Chemistry", "mg/dL", 0.6, 1.2, 0.2, 5.0,
             "Kidney function marker", "نیشاندەری کاری گورچیلە", "مؤشر وظائف الكلى"),
            
            ("ALT", "ALT", "إنزيم ALT",
             "Clinical Chemistry", "U/L", 7, 56, 5, 200,
             "Alanine aminotransferase", "ئالانین ئەمینۆترانسفێرەیس", "ناقلة أمين الألانين"),
            
            ("AST", "AST", "إنزيم AST",
             "Clinical Chemistry", "U/L", 10, 40, 5, 200,
             "Aspartate aminotransferase", "ئەسپارتەیت ئەمینۆترانسفێرەیس", "ناقلة أمين الأسبارتات"),
            
            ("Total Cholesterol", "کۆلیستڕۆڵی گشتی", "الكوليسترول الكلي",
             "Clinical Chemistry", "mg/dL", 125, 200, 100, 300,
             "Total cholesterol", "کۆلیستڕۆڵی گشتی", "الكوليسترول الكلي"),
            
            # Urinalysis
            ("Urine pH", "pH ی میز", "درجة حموضة البول",
             "Urinalysis", "pH", 4.5, 8.0, 4.0, 9.0,
             "Urine acidity", "ترشێتی میز", "حموضة البول"),
            
            ("Urine Protein", "پڕۆتینی میز", "بروتين البول",
             "Urinalysis", "mg/dL", 0, 8, 0, 30,
             "Protein in urine", "پڕۆتین لە میزدا", "البروتين في البول"),
            
            # Serology
            ("CRP", "CRP", "بروتين سي التفاعلي",
             "Serology", "mg/L", 0, 3, 0, 10,
             "C-reactive protein", "پڕۆتینی C- کاردانەوەیی", "بروتين سي التفاعلي"),
        ]
        
        for test in tests:
            self.conn.execute("""
                INSERT OR IGNORE INTO test_types 
                (name_en, name_ku, name_ar, category, unit, normal_range_low, normal_range_high, 
                 critical_low, critical_high, description_en, description_ku, description_ar)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, test)
        
        # Diseases with trilingual names
        diseases = [
            (1, 
             "Anemia", "کەمخوێنی", "فقر الدم",
             "Decreased red blood cells or hemoglobin", "کەمبوونەوەی خانە سوورەکانی خوێن یان هیمۆگلۆبین", "انخفاض خلايا الدم الحمراء أو الهيموجلوبين",
             "Fatigue, weakness, pale skin, shortness of breath", "ماندوویی، لاوازی، ڕەنگی پێستی کاڵ، تەنگی هەناسە", "التعب، الضعف، شحوب الجلد، ضيق التنفس"),
            
            (1,
             "Leukemia", "لۆکیمیا", "سرطان الدم",
             "Cancer of blood-forming tissues", "شێرپەنجەی شانەکانی دروستکەری خوێن", "سرطان الأنسجة المكونة للدم",
             "Fever, fatigue, frequent infections, weight loss", "تا، ماندوویی، هەوکردنی دووبارە، دابەزینی کێش", "حمى، تعب، التهابات متكررة، فقدان الوزن"),
            
            (2,
             "Urinary Tract Infection", "هەوکردنی میزەڕۆ", "التهاب المسالك البولية",
             "Bacterial infection of urinary system", "هەوکردنی بەکتریایی سیستەمی میز", "عدوى بكتيرية في الجهاز البولي",
             "Burning urination, frequent urination, cloudy urine", "سووتان لە کاتی میزکردندا، میزکردنی زۆر، میزی شێواو", "حرقة عند التبول، كثرة التبول، بول عكر"),
            
            (3,
             "Diabetes Mellitus", "شەکرە", "مرض السكري",
             "High blood sugar levels", "ئاستی بەرزی شەکری خوێن", "ارتفاع مستويات السكر في الدم",
             "Increased thirst, frequent urination, fatigue, blurred vision", "تینوێتی زۆر، میزکردنی زۆر، ماندوویی، بینینی شێواو", "زيادة العطش، كثرة التبول، التعب، عدم وضوح الرؤية"),
            
            (3,
             "Kidney Disease", "نەخۆشی گورچیلە", "مرض الكلى",
             "Impaired kidney function", "تێکچوونی کاری گورچیلە", "ضعف وظائف الكلى",
             "Swelling, fatigue, changes in urination, nausea", "ئاوسان، ماندوویی، گۆڕانکاری لە میزکردندا، هێڵنج", "تورم، تعب، تغيرات في التبول، غثيان"),
            
            (5,
             "Malaria", "مەلاریا", "الملاريا",
             "Parasitic infection transmitted by mosquitoes", "هەوکردنی مشقوڕخوەیی کە بە مێشوولە دەگوازرێتەوە", "عدوى طفيلية تنتقل عن طريق البعوض",
             "Fever, chills, headache, muscle pain", "تا، لەرز، سەرئێشە، ئازاری ماسولکە", "حمى، قشعريرة، صداع، آلام في العضلات"),
        ]
        
        for disease in diseases:
            self.conn.execute("""
                INSERT OR IGNORE INTO diseases 
                (category_id, name_en, name_ku, name_ar, description_en, description_ku, 
                 description_ar, symptoms_en, symptoms_ku, symptoms_ar)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, disease)
        
        # Practical Tests with trilingual names
        practicals = [
            ("Blood Smear Preparation", "ئامادەکردنی سمێری خوێن", "تحضير لطاخة الدم",
             "Learn to prepare and stain blood smears", "فێربوونی ئامادەکردن و ڕەنگکردنی سمێری خوێن", "تعلم تحضير وتلوين لطاخات الدم",
             "Hematology",
             "1. Clean slide with alcohol\n2. Place small drop of blood\n3. Use spreader slide at 30-45° angle\n4. Spread blood evenly\n5. Allow to air dry\n6. Fix with methanol\n7. Stain with Wright-Giemsa",
             "١. پاککردنەوەی سلاید بە ئەلکحول\n٢. دانانی دڵۆپێکی بچووکی خوێن\n٣. بەکارهێنانی سلایدی بڵاوکەرەوە بە گۆشەی ٣٠-٤٥ پلە\n٤. بڵاوکردنەوەی خوێن بە یەکسانی\n٥. ڕێگەدان بە وشکبوونەوە\n٦. جێگیرکردن بە میسانۆل\n٧. ڕەنگکردن بە رایت-گیمسا",
             "١. تنظيف الشريحة بالكحول\n٢. وضع قطرة صغيرة من الدم\n٣. استخدام شريحة فارشة بزاوية ٣٠-٤٥ درجة\n٤. نشر الدم بالتساوي\n٥. تركها لتجف في الهواء\n٦. تثبيتها بالميثانول\n٧. تلوينها برايت-جيمسا",
             "Glass slides, blood sample, Wright-Giemsa stain, methanol, microscope",
             "سلایدی شووشەیی، نموونەی خوێن، ڕەنگی رایت-گیمسا، میسانۆل، مایکرۆسکۆپ",
             "شرائح زجاجية، عينة دم، صبغة رايت-جيمسا، ميثانول، مجهر",
             "Well-spread monolayer of cells with feathered edge", "توێژاڵێکی یەک خانەیی بە باشی بڵاوکراوە لەگەڵ لێواری پەڕیشی", "طبقة أحادية منتشرة جيداً من الخلايا مع حافة ريشية",
             "Check for cell morphology, parasites, abnormal cells", "پشکنین بۆ شێوەزانی خانەکان، مشقوڕخوەکان، خانە نائاساییەکان", "فحص مورفولوجيا الخلايا، الطفيليات، الخلايا غير الطبيعية",
             45, "Basic"),
            
            ("Gram Staining", "ڕەنگکردنی گرام", "تلوين غرام",
             "Differentiate bacteria into Gram-positive and Gram-negative", "جیاکردنەوەی بەکتریا بۆ گرام-پۆزەتیڤ و گرام-نیگەتیڤ", "تمييز البكتيريا إلى غرام موجبة وغرام سالبة",
             "Microbiology",
             "1. Prepare bacterial smear\n2. Fix with heat\n3. Apply Crystal Violet (1 min)\n4. Apply Iodine (1 min)\n5. Decolorize with alcohol\n6. Counterstain with Safranin (30 sec)\n7. Wash and dry",
             "١. ئامادەکردنی سمێری بەکتریایی\n٢. جێگیرکردن بە گەرمی\n٣. بەکارهێنانی کریستاڵ ڤایۆلێت (١ خولەک)\n٤. بەکارهێنانی ئایۆدین (١ خولەک)\n٥. ڕەنگ لابردن بە ئەلکحول\n٦. ڕەنگی پێچەوانە بە سەفرانین (٣٠ چرکە)\n٧. شۆردن و وشککردن",
             "١. تحضير لطاخة بكتيرية\n٢. تثبيت بالحرارة\n٣. وضع الكريستال البنفسجي (١ دقيقة)\n٤. وضع اليود (١ دقيقة)\n٥. إزالة اللون بالكحول\n٦. تلوين مضاد بالصفرانين (٣٠ ثانية)\n٧. غسل وتجفيف",
             "Bacterial culture, Crystal Violet, Iodine, Alcohol, Safranin, microscope slides",
             "کشتوکاڵی بەکتریایی، کریستاڵ ڤایۆلێت، ئایۆدین، ئەلکحول، سەفرانین، سلایدی مایکرۆسکۆپ",
             "مزرعة بكتيرية، كريستال بنفسجي، يود، كحول، صفرانين، شرائح مجهرية",
             "Gram-positive: Purple/Blue\nGram-negative: Pink/Red", "گرام-پۆزەتیڤ: وەنەوشەیی/شین\nگرام-نیگەتیڤ: پەمەیی/سوور", "غرام موجب: أرجواني/أزرق\nغرام سالب: وردي/أحمر",
             "Gram-positive bacteria have thick peptidoglycan layer", "بەکتریای گرام-پۆزەتیڤ توێژاڵێکی ئەستووری پێپتیدۆگلایکانیان هەیە", "البكتيريا غرام الموجبة لديها طبقة ببتيدوغليكان سميكة",
             60, "Basic"),
            
            ("Urinalysis - Dipstick Method", "شیکردنەوەی میز - شێوازی دیپستیک", "تحليل البول - طريقة الشريط",
             "Chemical analysis of urine using dipstick", "شیکردنەوەی کیمیایی میز بە بەکارهێنانی دیپستیک", "التحليل الكيميائي للبول باستخدام الشريط",
             "Urinalysis",
             "1. Collect fresh urine sample\n2. Dip test strip briefly\n3. Remove excess urine\n4. Read at specified times\n5. Compare with color chart",
             "١. کۆکردنەوەی نموونەی میزی تازە\n٢. نوقمکردنی شریتی پشکنین بە کورتی\n٣. لابردنی میزی زیادە\n٤. خوێندنەوە لە کاتی دیاریکراودا\n٥. بەراوردکردن لەگەڵ هێڵکاری ڕەنگ",
             "١. جمع عينة بول طازجة\n٢. غمس شريط الاختبار لفترة وجيزة\n٣. إزالة البول الزائد\n٤. القراءة في الأوقات المحددة\n٥. المقارنة مع مخطط الألوان",
             "Urine sample, dipstick test strips, timer, color chart",
             "نموونەی میز، شریتی پشکنینی دیپستیک، کاتژمێر، هێڵکاری ڕەنگ",
             "عينة بول، شرائط اختبار، مؤقت، مخطط ألوان",
             "Results compared to standard color chart", "ئەنجامەکان بەراورد دەکرێن لەگەڵ هێڵکاری ڕەنگی ستاندارد", "تتم مقارنة النتائج مع مخطط الألوان القياسي",
             "Multiple parameters: pH, protein, glucose, ketones, blood, etc.", "پارامێتەری فرە: pH، پڕۆتین، گلوکۆز، کیتۆن، خوێن، هتد.", "معلمات متعددة: درجة الحموضة، البروتين، الجلوكوز، الكيتونات، الدم، إلخ.",
             30, "Basic"),
        ]
        
        for prac in practicals:
            self.conn.execute("""
                INSERT OR IGNORE INTO practical_tests 
                (title_en, title_ku, title_ar, description_en, description_ku, description_ar,
                 category, steps_en, steps_ku, steps_ar, materials_en, materials_ku, materials_ar,
                 expected_results_en, expected_results_ku, expected_results_ar,
                 interpretation_en, interpretation_ku, interpretation_ar,
                 duration_minutes, difficulty_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, prac)
        
        self.conn.commit()
    
    def get_localized(self, table: str, lang: str) -> List[Dict]:
        """Get data with localized names based on language"""
        rows = self.conn.execute(f"SELECT * FROM {table}").fetchall()
        results = []
        for row in dict_rows(rows):
            localized = dict(row)
            # Map localized fields
            name_field = f"name_{lang}" if f"name_{lang}" in localized else "name_en"
            desc_field = f"description_{lang}" if f"description_{lang}" in localized else "description_en"
            
            if name_field in localized:
                localized['display_name'] = localized[name_field]
            if desc_field in localized:
                localized['display_description'] = localized[desc_field]
            
            results.append(localized)
        return results

def dict_rows(rows):
    return [dict(row) for row in rows]

# ==================== Initialize Database ====================
@st.cache_resource
def get_db():
    return LabDatabase()

# ==================== Helper Functions ====================
def get_translation(key: str) -> str:
    """Get translation for current language"""
    lang = st.session_state.get('language', 'English 🇬🇧')
    return TRANSLATIONS.get(lang, TRANSLATIONS['English 🇬🇧']).get(key, key)

def get_name(row: Dict, prefix: str = "name") -> str:
    """Get localized name from database row"""
    lang_map = {
        "English 🇬🇧": "en",
        "کوردی 🇮🇶": "ku",
        "العربية 🇮🇶": "ar"
    }
    lang = lang_map.get(st.session_state.get('language', 'English 🇬🇧'), 'en')
    field = f"{prefix}_{lang}"
    return row.get(field, row.get(f"{prefix}_en", ""))

def get_description(row: Dict, prefix: str = "description") -> str:
    """Get localized description from database row"""
    return get_name(row, prefix)

# ==================== Main Application ====================
def main():
    st.set_page_config(
        page_title=get_translation('app_title'),
        page_icon="🔬",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize language
    if 'language' not in st.session_state:
        st.session_state.language = 'English 🇬🇧'
    
    # Custom CSS
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
        
        * {
            font-family: 'Cairo', sans-serif;
        }
        
        .main-header {
            background: linear-gradient(135deg, #1a237e 0%, #0d47a1 50%, #01579b 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 30px;
        }
        
        .category-card {
            background: linear-gradient(135deg, #e3f2fd, #bbdefb);
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
            cursor: pointer;
            transition: transform 0.3s;
            border-left: 5px solid #1565c0;
        }
        
        .category-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        }
        
        .test-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            border: 1px solid #e0e0e0;
        }
        
        .practical-card {
            background: linear-gradient(135deg, #f3e5f5, #e1bee7);
            padding: 20px;
            border-radius: 10px;
            margin: 15px 0;
            border-left: 5px solid #7b1fa2;
        }
        
        .stButton > button {
            background: linear-gradient(135deg, #1a237e, #0d47a1);
            color: white;
            border: none;
            padding: 10px 25px;
            border-radius: 25px;
            font-weight: bold;
        }
        
        .normal-range {
            color: #2e7d32;
            font-weight: bold;
        }
        
        .critical-range {
            color: #c62828;
            font-weight: bold;
        }
        
        .disease-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin: 15px 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border-top: 4px solid #1565c0;
        }
        
        .symptom-tag {
            display: inline-block;
            background: #ffebee;
            color: #c62828;
            padding: 3px 10px;
            border-radius: 15px;
            margin: 3px;
            font-size: 0.9em;
        }
        
        .step-number {
            display: inline-block;
            background: #1a237e;
            color: white;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            text-align: center;
            line-height: 30px;
            margin-right: 10px;
        }
        
        [dir="rtl"] {
            direction: rtl;
            text-align: right;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize database
    db = get_db()
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"## {get_translation('nav_title')}")
        
        # Language selector
        language = st.selectbox(
            "🌐 Language / زمان / اللغة",
            ["English 🇬🇧", "کوردی 🇮🇶", "العربية 🇮🇶"],
            key="language_selector"
        )
        if language != st.session_state.language:
            st.session_state.language = language
            st.rerun()
        
        st.markdown("---")
        
        page = st.radio(
            get_translation('select_section'),
            [get_translation('dashboard'), get_translation('disease_db'), 
             get_translation('lab_tests'), get_translation('practical'),
             get_translation('theory'), get_translation('results_entry'),
             get_translation('reports')]
        )
        
        st.markdown("---")
        st.markdown(f"### {get_translation('quick_info')}")
        st.info(get_translation('quick_info_text'))
    
    # Route to appropriate page
    if page == get_translation('dashboard'):
        render_dashboard(db)
    elif page == get_translation('disease_db'):
        render_disease_database(db)
    elif page == get_translation('lab_tests'):
        render_lab_tests(db)
    elif page == get_translation('practical'):
        render_practical_tests(db)
    elif page == get_translation('theory'):
        render_theory_questions(db)
    elif page == get_translation('results_entry'):
        render_test_results(db)
    elif page == get_translation('reports'):
        render_reports(db)

def render_dashboard(db: LabDatabase):
    T = get_translation
    
    st.markdown(f"""
    <div class="main-header">
        <h1>{T('app_title')}</h1>
        <h3>{T('app_subtitle')}</h3>
        <p>{T('app_description')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    categories = db.conn.execute("SELECT COUNT(*) as c FROM disease_categories").fetchone()
    tests = db.conn.execute("SELECT COUNT(*) as c FROM test_types").fetchone()
    diseases = db.conn.execute("SELECT COUNT(*) as c FROM diseases").fetchone()
    practicals = db.conn.execute("SELECT COUNT(*) as c FROM practical_tests").fetchone()
    
    with col1:
        st.metric(T('disease_categories'), categories['c'])
    with col2:
        st.metric(T('laboratory_tests'), tests['c'])
    with col3:
        st.metric(T('diseases'), diseases['c'])
    with col4:
        st.metric(T('practical_tests'), practicals['c'])
    
    # Categories overview
    st.markdown(f"## {T('categories_overview')}")
    
    all_categories = db.conn.execute("SELECT * FROM disease_categories").fetchall()
    
    cols = st.columns(2)
    for i, cat in enumerate(all_categories):
        cat_dict = dict(cat)
        with cols[i % 2]:
            st.markdown(f"""
            <div class="category-card">
                <h3>{cat_dict['icon']} {get_name(cat_dict)}</h3>
                <p>{get_description(cat_dict)}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Quick reference tests
    st.markdown(f"## {T('quick_reference')}")
    
    common_tests = db.conn.execute("SELECT * FROM test_types LIMIT 6").fetchall()
    cols = st.columns(3)
    for i, test in enumerate(common_tests):
        test_dict = dict(test)
        with cols[i % 3]:
            st.markdown(f"""
            <div class="test-card">
                <h4>📊 {get_name(test_dict)}</h4>
                <p><span class="normal-range">{T('normal_range')}: {test_dict['normal_range_low']} - {test_dict['normal_range_high']} {test_dict['unit']}</span></p>
                <p><small>{get_description(test_dict)}</small></p>
            </div>
            """, unsafe_allow_html=True)

def render_disease_database(db: LabDatabase):
    T = get_translation
    
    st.markdown(f"## {T('disease_db')}")
    
    categories = db.conn.execute("SELECT * FROM disease_categories").fetchall()
    
    # Filter
    selected_category = st.selectbox(
        T('filter_category'),
        [T('all_categories')] + [get_name(dict(cat)) for cat in categories]
    )
    
    diseases = db.conn.execute("""
        SELECT d.*, dc.name_en as cat_en, dc.name_ku as cat_ku, dc.name_ar as cat_ar 
        FROM diseases d 
        JOIN disease_categories dc ON d.category_id = dc.id
    """).fetchall()
    
    # Filter by category
    if selected_category != T('all_categories'):
        diseases = [d for d in diseases if get_name(dict(d), 'cat') == selected_category]
    
    # Search
    search = st.text_input(T('search_diseases'))
    if search:
        diseases = [d for d in diseases if search.lower() in get_name(dict(d)).lower()]
    
    # Display diseases
    for disease in diseases:
        disease_dict = dict(disease)
        with st.expander(f"🦠 {get_name(disease_dict)} - {get_name(disease_dict, 'cat')}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**{T('description')}:** {get_description(disease_dict)}")
                
                st.markdown(f"**{T('symptoms')}:**")
                symptoms_field = f"symptoms_{st.session_state.language.split()[-1][:2].lower()}"
                symptoms_text = disease_dict.get('symptoms_en', '')
                if symptoms_text:
                    symptoms = symptoms_text.split(',')
                    symptom_html = ""
                    for symptom in symptoms:
                        symptom_html += f"<span class='symptom-tag'>{symptom.strip()}</span>"
                    st.markdown(symptom_html, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"**{T('category')}:**")
                st.info(get_name(disease_dict, 'cat'))

def render_lab_tests(db: LabDatabase):
    T = get_translation
    
    st.markdown(f"## {T('lab_tests')}")
    
    col1, col2 = st.columns(2)
    with col1:
        categories = [T('all_categories')] + list(set(
            t['category'] for t in db.conn.execute("SELECT category FROM test_types").fetchall()
        ))
        selected_category = st.selectbox(T('test_category'), categories)
    with col2:
        search = st.text_input(T('search_tests'))
    
    # Get tests
    tests = db.conn.execute("SELECT * FROM test_types").fetchall()
    
    if selected_category != T('all_categories'):
        tests = [t for t in tests if t['category'] == selected_category]
    
    if search:
        tests = [t for t in tests if search.lower() in get_name(dict(t)).lower()]
    
    # Group by category
    tests_sorted = sorted(tests, key=lambda x: x['category'])
    
    for category, group in groupby(tests_sorted, key=lambda x: x['category']):
        st.markdown(f"### 📁 {category}")
        
        group_list = list(group)
        cols = st.columns(2)
        
        for i, test in enumerate(group_list):
            test_dict = dict(test)
            with cols[i % 2]:
                st.markdown(f"""
                <div class="test-card">
                    <h4>📊 {get_name(test_dict)}</h4>
                    <p><strong>{T('unit')}:</strong> {test_dict['unit']}</p>
                    <p><span class="normal-range">{T('normal_range')}: {test_dict['normal_range_low']} - {test_dict['normal_range_high']}</span></p>
                    <p><strong>{T('description')}:</strong> {get_description(test_dict)}</p>
                    <hr>
                    <p><strong>{T('critical_values')}:</strong></p>
                    <p>{T('low')}: <span class="critical-range">< {test_dict['critical_low']}</span> | 
                    {T('high')}: <span class="critical-range">> {test_dict['critical_high']}</span></p>
                </div>
                """, unsafe_allow_html=True)

def render_practical_tests(db: LabDatabase):
    T = get_translation
    
    st.markdown(f"## {T('practical')}")
    
    col1, col2 = st.columns(2)
    with col1:
        categories = [T('all_categories')] + list(set(
            p['category'] for p in db.conn.execute("SELECT category FROM practical_tests").fetchall()
        ))
        selected = st.selectbox(T('filter_category'), categories)
    with col2:
        difficulty = st.selectbox(T('difficulty'), 
            [T('all_categories'), T('basic'), T('intermediate'), T('advanced')])
    
    # Get tests
    practicals = db.conn.execute("SELECT * FROM practical_tests").fetchall()
    
    if selected != T('all_categories'):
        practicals = [p for p in practicals if p['category'] == selected]
    
    if difficulty != T('all_categories'):
        diff_map = {T('basic'): 'Basic', T('intermediate'): 'Intermediate', T('advanced'): 'Advanced'}
        practicals = [p for p in practicals if p['difficulty_level'] == diff_map.get(difficulty, difficulty)]
    
    for test in practicals:
        test_dict = dict(test)
        with st.expander(f"🔬 {get_name(test_dict, 'title')} ({test_dict['duration_minutes']} {T('minutes')} - {get_name(test_dict, 'difficulty_level')})"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**{T('description')}:** {get_description(test_dict, 'description')}")
                
                st.markdown(f"### {T('procedure')}")
                steps_field = f"steps_{st.session_state.language.split()[-1][:2].lower()}"
                steps = test_dict.get('steps_en', '').split('\n')
                for j, step in enumerate(steps):
                    if step.strip():
                        st.markdown(f"<span class='step-number'>{j+1}</span> {step.strip()}", unsafe_allow_html=True)
                
                st.markdown("---")
                
                col_mat, col_exp = st.columns(2)
                with col_mat:
                    st.markdown(f"### {T('materials')}")
                    materials = test_dict.get('materials_en', '').split(',')
                    for mat in materials:
                        st.markdown(f"- {mat.strip()}")
                
                with col_exp:
                    st.markdown(f"### {T('expected_results')}")
                    st.info(test_dict.get('expected_results_en', ''))
            
            with col2:
                st.markdown(f"**{T('category')}:** {test_dict['category']}")
                st.markdown(f"**{T('duration')}:** {test_dict['duration_minutes']} {T('minutes')}")
                diff_level = test_dict['difficulty_level']
                stars = {'Basic': 1, 'Intermediate': 2, 'Advanced': 3}
                st.markdown(f"**{T('difficulty')}:** {'⭐' * stars.get(diff_level, 1)}")
                
                st.markdown("---")
                st.markdown(f"### {T('interpretation')}")
                st.success(test_dict.get('interpretation_en', ''))

def render_theory_questions(db: LabDatabase):
    T = get_translation
    
    st.markdown(f"## {T('theory')}")
    
    search = st.text_input(T('search'))
    
    with st.expander(T('add_notes')):
        col1, col2 = st.columns(2)
        with col1:
            topic = st.text_input(T('topic'))
            category = st.selectbox(T('category'), 
                ["Hematology", "Microbiology", "Clinical Chemistry", "Immunology", "Parasitology", "Urinalysis"])
        with col2:
            content = st.text_area(T('content'), height=150)
        
        if st.button(T('save_note')):
            db.conn.execute(
                "INSERT INTO study_notes (topic, content, category) VALUES (?, ?, ?)",
                (topic, content, category)
            )
            db.conn.commit()
            st.success(T('note_saved'))
    
    st.markdown(f"### {T('your_notes')}")
    notes = db.conn.execute("SELECT * FROM study_notes ORDER BY created_at DESC").fetchall()
    
    for note in notes:
        note_dict = dict(note)
        with st.expander(f"📝 {note_dict['topic']} - {note_dict['category']}"):
            st.markdown(note_dict['content'])
            st.caption(f"{T('created')}: {note_dict['created_at']}")
            if st.button(T('delete'), key=f"del_{note_dict['id']}"):
                db.conn.execute("DELETE FROM study_notes WHERE id = ?", (note_dict['id'],))
                db.conn.commit()
                st.rerun()

def render_test_results(db: LabDatabase):
    T = get_translation
    
    st.markdown(f"## {T('results_entry')}")
    
    with st.form("test_result_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            patient_name = st.text_input(T('patient_name'))
            patient_age = st.number_input(T('patient_age'), min_value=0, max_value=120)
        
        with col2:
            patient_gender = st.selectbox(T('patient_gender'), 
                [T('gender_male'), T('gender_female'), T('gender_other')])
            tests = db.conn.execute("SELECT * FROM test_types").fetchall()
            test_options = {get_name(dict(t)): t['id'] for t in tests}
            selected_test = st.selectbox(T('select_test'), list(test_options.keys()))
        
        with col3:
            result_value = st.number_input(T('result_value'), step=0.01)
            result_text = st.text_input(T('result_text'))
        
        notes = st.text_area(T('additional_notes'))
        
        if st.form_submit_button(T('save_result')):
            test_id = test_options[selected_test]
            test = db.conn.execute("SELECT * FROM test_types WHERE id = ?", (test_id,)).fetchone()
            test_dict = dict(test)
            
            is_abnormal = False
            if result_value < test_dict['normal_range_low'] or result_value > test_dict['normal_range_high']:
                is_abnormal = True
            
            db.conn.execute("""
                INSERT INTO test_results (patient_name, patient_age, patient_gender, test_id, 
                                       result_value, result_text, is_abnormal, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (patient_name, patient_age, patient_gender, test_id, 
                 result_value, result_text, is_abnormal, notes))
            db.conn.commit()
            st.success(T('saved_success'))
            if is_abnormal:
                st.warning(T('abnormal_warning'))

def render_reports(db: LabDatabase):
    T = get_translation
    
    st.markdown(f"## {T('reports')}")
    
    results = db.conn.execute("""
        SELECT tr.*, tt.name_en as test_name, tt.category
        FROM test_results tr 
        JOIN test_types tt ON tr.test_id = tt.id
        ORDER BY tr.date_performed DESC
    """).fetchall()
    
    if results:
        df = pd.DataFrame([dict(r) for r in results])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(T('total_tests'), len(df))
        with col2:
            abnormal = len(df[df['is_abnormal'] == True])
            st.metric(T('abnormal_results'), abnormal)
        with col3:
            normal_percentage = ((len(df) - abnormal) / len(df)) * 100 if len(df) > 0 else 0
            st.metric(T('normal_rate'), f"{normal_percentage:.1f}%")
        
        col1, col2 = st.columns(2)
        
        with col1:
            category_counts = df['category'].value_counts()
            fig = px.pie(values=category_counts.values, names=category_counts.index, 
                        title=T('tests_by_category'))
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            status_counts = df['is_abnormal'].value_counts()
            fig = px.bar(x=['Normal', 'Abnormal'], y=status_counts.values,
                        title=T('normal_vs_abnormal'),
                        color=['Normal', 'Abnormal'],
                        color_discrete_map={'Normal': '#2e7d32', 'Abnormal': '#c62828'})
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown(f"### {T('recent_results')}")
        st.dataframe(df[['patient_name', 'test_name', 'result_value', 'is_abnormal', 'date_performed']],
                    use_container_width=True)
    else:
        st.info(T('no_results'))

if __name__ == "__main__":
    main()
