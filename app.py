import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from itertools import groupby

# ==================== Translations (Kurdish & English Only) ====================
TRANSLATIONS = {
    "English 🇬🇧": {
        "app_title": "🔬 Medical Laboratory Analysis System",
        "app_subtitle": "Fourth Stage - Disease Analysis",
        "app_description": "Comprehensive reference for all laboratory tests and disease analysis",
        "dashboard": "📊 Dashboard",
        "disease_db": "🦠 Disease Database",
        "lab_tests": "🧪 Laboratory Tests",
        "practical": "🔬 Practical Tests",
        "theory": "📚 Theory & Notes",
        "results_entry": "📝 Test Results Entry",
        "reports": "📈 Reports & Analytics",
        "nav_title": "🔬 Navigation",
        "select_section": "Select Section",
        "language": "🌐 Language",
        "quick_info": "📋 Quick Info",
        "quick_info_text": "Comprehensive medical laboratory test information for 4th stage students.",
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
        "minutes": "minutes",
        "basic": "Basic",
        "intermediate": "Intermediate",
        "advanced": "Advanced",
        "gender_male": "Male",
        "gender_female": "Female",
        "gender_other": "Other",
        "created": "Created",
        "no_diseases_found": "No diseases found",
        "no_notes_yet": "No notes written yet",
        "write_topic_content": "Please write topic and content",
        "write_patient_name": "Please write patient name",
    },
    "کوردی 🇮🇶": {
        "app_title": "🔬 سیستەمی شیکردنەوەی تاقیگەی پزیشکی",
        "app_subtitle": "قۆناغی چوارەم - شیکردنەوەی نەخۆشییەکان",
        "app_description": "سەرچاوەیەکی گشتگیر بۆ هەموو پشکنینە تاقیگەییەکان و شیکردنەوەی نەخۆشییەکان",
        "dashboard": "📊 داشبۆرد",
        "disease_db": "🦠 بنکەدراوەی نەخۆشییەکان",
        "lab_tests": "🧪 پشکنینە تاقیگەییەکان",
        "practical": "🔬 پشکنینی پراکتیکی",
        "theory": "📚 تیۆری و تێبینییەکان",
        "results_entry": "📝 تۆمارکردنی ئەنجامەکان",
        "reports": "📈 ڕاپۆرت و ئامارەکان",
        "nav_title": "🔬 ڕێنیشاندەر",
        "select_section": "بەش هەڵبژێرە",
        "language": "🌐 زمان",
        "quick_info": "📋 زانیاری خێرا",
        "quick_info_text": "زانیاری گشتگیری پشکنینە تاقیگەییەکانی پزیشکی بۆ قوتابیانی قۆناغی چوارەم.",
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
        "minutes": "خولەک",
        "basic": "سەرەتایی",
        "intermediate": "ناوەندی",
        "advanced": "پێشکەوتوو",
        "gender_male": "نێر",
        "gender_female": "مێ",
        "gender_other": "هی تر",
        "created": "دروستکراوە",
        "no_diseases_found": "هیچ نەخۆشییەک نەدۆزرایەوە",
        "no_notes_yet": "هێشتا هیچ تێبینییەکت نەنووسیوە",
        "write_topic_content": "تکایە بابەت و ناوەڕۆک بنووسە",
        "write_patient_name": "تکایە ناوی نەخۆش بنووسە",
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
                description_en TEXT,
                description_ku TEXT,
                icon TEXT
            );
            
            CREATE TABLE IF NOT EXISTS diseases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER,
                name_en TEXT NOT NULL,
                name_ku TEXT NOT NULL,
                description_en TEXT,
                description_ku TEXT,
                symptoms_en TEXT,
                symptoms_ku TEXT,
                FOREIGN KEY (category_id) REFERENCES disease_categories(id)
            );
            
            CREATE TABLE IF NOT EXISTS test_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name_en TEXT NOT NULL,
                name_ku TEXT NOT NULL,
                category TEXT,
                unit TEXT,
                normal_range_low REAL,
                normal_range_high REAL,
                critical_low REAL,
                critical_high REAL,
                description_en TEXT,
                description_ku TEXT
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
        """Insert reference data - only English and Kurdish"""
        
        # Disease Categories
        categories = [
            ("Hematology", "خوێنناسی",
             "Blood disorders and diseases",
             "نەخۆشی و تێکچوونەکانی خوێن", "🩸"),
            ("Microbiology", "مایکرۆبایۆلۆجی",
             "Bacterial, viral, fungal infections",
             "هەوکردنی بەکتریایی، ڤایرۆسی، کەڕوویی", "🦠"),
            ("Clinical Chemistry", "کیمیای کلینیکی",
             "Chemical analysis of body fluids",
             "شیکردنەوەی کیمیایی شلەکانی لەش", "🧪"),
            ("Immunology", "ئیمیونۆلۆجی",
             "Immune system disorders",
             "تێکچوونەکانی سیستەمی بەرگری", "🛡️"),
            ("Parasitology", "مشقوڕخوێناسی",
             "Parasitic infections",
             "هەوکردنی مشقوڕخوەکان", "🐛"),
            ("Urinalysis", "شیکردنەوەی میز",
             "Urine analysis",
             "شیکردنەوەی میز", "💧"),
            ("Serology", "سیرۆلۆجی",
             "Blood serum analysis",
             "شیکردنەوەی شلەی خوێن", "💉"),
            ("Histopathology", "هیستۆپاتۆلۆجی",
             "Tissue examination",
             "پشکنینی شانەکان", "🔬")
        ]
        
        for cat in categories:
            self.conn.execute("""
                INSERT OR IGNORE INTO disease_categories 
                (name_en, name_ku, description_en, description_ku, icon) 
                VALUES (?, ?, ?, ?, ?)
            """, cat)
        
        # Laboratory Tests
        tests = [
            ("CBC - Complete Blood Count", "CBC - ژماردنی تەواوی خوێن",
             "Hematology", "cells/μL", 4.5, 11.0, 2.0, 15.0,
             "Complete blood cell count",
             "ژماردنی تەواوی خانەکانی خوێن"),
            
            ("WBC Count", "ژماردنی WBC",
             "Hematology", "×10³/μL", 4.0, 11.0, 2.0, 30.0,
             "White blood cell count",
             "ژماردنی خانە سپییەکانی خوێن"),
            
            ("Hemoglobin", "هیمۆگلۆبین",
             "Hematology", "g/dL", 12.0, 16.0, 6.0, 20.0,
             "Hemoglobin level",
             "ئاستی هیمۆگلۆبین"),
            
            ("Platelet Count", "ژماردنی پلەیکلت",
             "Hematology", "×10³/μL", 150, 400, 50, 1000,
             "Platelet count",
             "ژماردنی پلەیکلتەکان"),
            
            ("Blood Glucose Fasting", "گلوکۆزی خوێن بە بەڕۆژوویی",
             "Clinical Chemistry", "mg/dL", 70, 100, 40, 300,
             "Fasting blood sugar",
             "شەکری خوێن بە بەڕۆژوویی"),
            
            ("HbA1c", "HbA1c",
             "Clinical Chemistry", "%", 4.0, 5.6, 3.0, 10.0,
             "Glycated hemoglobin",
             "هیمۆگلۆبینی گڵایکەیتکراو"),
            
            ("Creatinine", "کریاتینین",
             "Clinical Chemistry", "mg/dL", 0.6, 1.2, 0.2, 5.0,
             "Kidney function marker",
             "نیشاندەری کاری گورچیلە"),
            
            ("ALT", "ALT",
             "Clinical Chemistry", "U/L", 7, 56, 5, 200,
             "Alanine aminotransferase",
             "ئالانین ئەمینۆترانسفێرەیس"),
            
            ("AST", "AST",
             "Clinical Chemistry", "U/L", 10, 40, 5, 200,
             "Aspartate aminotransferase",
             "ئەسپارتەیت ئەمینۆترانسفێرەیس"),
            
            ("Total Cholesterol", "کۆلیستڕۆڵی گشتی",
             "Clinical Chemistry", "mg/dL", 125, 200, 100, 300,
             "Total cholesterol",
             "کۆلیستڕۆڵی گشتی"),
            
            ("Urine pH", "pH ی میز",
             "Urinalysis", "pH", 4.5, 8.0, 4.0, 9.0,
             "Urine acidity",
             "ترشێتی میز"),
            
            ("Urine Protein", "پڕۆتینی میز",
             "Urinalysis", "mg/dL", 0, 8, 0, 30,
             "Protein in urine",
             "پڕۆتین لە میزدا"),
            
            ("CRP", "CRP",
             "Serology", "mg/L", 0, 3, 0, 10,
             "C-reactive protein",
             "پڕۆتینی C- کاردانەوەیی"),
        ]
        
        for test in tests:
            self.conn.execute("""
                INSERT OR IGNORE INTO test_types 
                (name_en, name_ku, category, unit, normal_range_low, normal_range_high, 
                 critical_low, critical_high, description_en, description_ku)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, test)
        
        # Diseases
        diseases = [
            (1, "Anemia", "کەمخوێنی",
             "Decreased red blood cells or hemoglobin",
             "کەمبوونەوەی خانە سوورەکانی خوێن یان هیمۆگلۆبین",
             "Fatigue, weakness, pale skin, shortness of breath",
             "ماندوویی، لاوازی، ڕەنگی پێستی کاڵ، تەنگی هەناسە"),
            
            (1, "Leukemia", "لۆکیمیا",
             "Cancer of blood-forming tissues",
             "شێرپەنجەی شانەکانی دروستکەری خوێن",
             "Fever, fatigue, frequent infections, weight loss",
             "تا، ماندوویی، هەوکردنی دووبارە، دابەزینی کێش"),
            
            (2, "Urinary Tract Infection", "هەوکردنی میزەڕۆ",
             "Bacterial infection of urinary system",
             "هەوکردنی بەکتریایی سیستەمی میز",
             "Burning urination, frequent urination, cloudy urine",
             "سووتان لە کاتی میزکردندا، میزکردنی زۆر، میزی شێواو"),
            
            (3, "Diabetes Mellitus", "شەکرە",
             "High blood sugar levels",
             "ئاستی بەرزی شەکری خوێن",
             "Increased thirst, frequent urination, fatigue, blurred vision",
             "تینوێتی زۆر، میزکردنی زۆر، ماندوویی، بینینی شێواو"),
            
            (3, "Kidney Disease", "نەخۆشی گورچیلە",
             "Impaired kidney function",
             "تێکچوونی کاری گورچیلە",
             "Swelling, fatigue, changes in urination, nausea",
             "ئاوسان، ماندوویی، گۆڕانکاری لە میزکردندا، هێڵنج"),
            
            (5, "Malaria", "مەلاریا",
             "Parasitic infection transmitted by mosquitoes",
             "هەوکردنی مشقوڕخوەیی کە بە مێشوولە دەگوازرێتەوە",
             "Fever, chills, headache, muscle pain",
             "تا، لەرز، سەرئێشە، ئازاری ماسولکە"),
        ]
        
        for disease in diseases:
            self.conn.execute("""
                INSERT OR IGNORE INTO diseases 
                (category_id, name_en, name_ku, description_en, description_ku, 
                 symptoms_en, symptoms_ku)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, disease)
        
        # Practical Tests
        practicals = [
            ("Blood Smear Preparation", "ئامادەکردنی سمێری خوێن",
             "Learn to prepare and stain blood smears",
             "فێربوونی ئامادەکردن و ڕەنگکردنی سمێری خوێن",
             "Hematology",
             "1. Clean slide with alcohol\n2. Place small drop of blood\n3. Use spreader slide at 30-45° angle\n4. Spread blood evenly\n5. Allow to air dry\n6. Fix with methanol\n7. Stain with Wright-Giemsa",
             "١. پاککردنەوەی سلاید بە ئەلکحول\n٢. دانانی دڵۆپێکی بچووکی خوێن\n٣. بەکارهێنانی سلایدی بڵاوکەرەوە بە گۆشەی ٣٠-٤٥ پلە\n٤. بڵاوکردنەوەی خوێن بە یەکسانی\n٥. ڕێگەدان بە وشکبوونەوە\n٦. جێگیرکردن بە میسانۆل\n٧. ڕەنگکردن بە رایت-گیمسا",
             "Glass slides, blood sample, Wright-Giemsa stain, methanol, microscope",
             "سلایدی شووشەیی، نموونەی خوێن، ڕەنگی رایت-گیمسا، میسانۆل، مایکرۆسکۆپ",
             "Well-spread monolayer of cells with feathered edge",
             "توێژاڵێکی یەک خانەیی بە باشی بڵاوکراوە لەگەڵ لێواری پەڕیشی",
             "Check for cell morphology, parasites, abnormal cells",
             "پشکنین بۆ شێوەزانی خانەکان، مشقوڕخوەکان، خانە نائاساییەکان",
             45, "Basic"),
            
            ("Gram Staining", "ڕەنگکردنی گرام",
             "Differentiate bacteria into Gram-positive and Gram-negative",
             "جیاکردنەوەی بەکتریا بۆ گرام-پۆزەتیڤ و گرام-نیگەتیڤ",
             "Microbiology",
             "1. Prepare bacterial smear\n2. Fix with heat\n3. Apply Crystal Violet (1 min)\n4. Apply Iodine (1 min)\n5. Decolorize with alcohol\n6. Counterstain with Safranin (30 sec)\n7. Wash and dry",
             "١. ئامادەکردنی سمێری بەکتریایی\n٢. جێگیرکردن بە گەرمی\n٣. بەکارهێنانی کریستاڵ ڤایۆلێت (١ خولەک)\n٤. بەکارهێنانی ئایۆدین (١ خولەک)\n٥. ڕەنگ لابردن بە ئەلکحول\n٦. ڕەنگی پێچەوانە بە سەفرانین (٣٠ چرکە)\n٧. شۆردن و وشککردن",
             "Bacterial culture, Crystal Violet, Iodine, Alcohol, Safranin, microscope slides",
             "کشتوکاڵی بەکتریایی، کریستاڵ ڤایۆلێت، ئایۆدین، ئەلکحول، سەفرانین، سلایدی مایکرۆسکۆپ",
             "Gram-positive: Purple/Blue\nGram-negative: Pink/Red",
             "گرام-پۆزەتیڤ: وەنەوشەیی/شین\nگرام-نیگەتیڤ: پەمەیی/سوور",
             "Gram-positive bacteria have thick peptidoglycan layer",
             "بەکتریای گرام-پۆزەتیڤ توێژاڵێکی ئەستووری پێپتیدۆگلایکانیان هەیە",
             60, "Basic"),
        ]
        
        for prac in practicals:
            self.conn.execute("""
                INSERT OR IGNORE INTO practical_tests 
                (title_en, title_ku, description_en, description_ku,
                 category, steps_en, steps_ku, materials_en, materials_ku,
                 expected_results_en, expected_results_ku,
                 interpretation_en, interpretation_ku,
                 duration_minutes, difficulty_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, prac)
        
        self.conn.commit()

# ==================== Initialize Database ====================
@st.cache_resource
def get_db():
    return LabDatabase()

# ==================== Helper Functions ====================
def get_translation(key: str) -> str:
    """Get translation for current language"""
    lang = st.session_state.get('language', 'کوردی 🇮🇶')
    return TRANSLATIONS.get(lang, TRANSLATIONS['کوردی 🇮🇶']).get(key, key)

def get_name(row: dict, prefix: str = "name") -> str:
    """Get localized name from database row"""
    lang_map = {"English 🇬🇧": "en", "کوردی 🇮🇶": "ku"}
    lang = lang_map.get(st.session_state.get('language', 'کوردی 🇮🇶'), 'ku')
    field = f"{prefix}_{lang}"
    return row.get(field, row.get(f"{prefix}_en", ""))

def get_description(row: dict) -> str:
    """Get localized description"""
    return get_name(row, "description")

# ==================== Main Application ====================
def main():
    st.set_page_config(
        page_title="سیستەمی شیکردنەوەی تاقیگەی پزیشکی",
        page_icon="🔬",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize language - Default to Kurdish
    if 'language' not in st.session_state:
        st.session_state.language = 'کوردی 🇮🇶'
    
    # Custom CSS with proper Kurdish font
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Naskh+Arabic:wght@400;600;700&family=Noto+Sans:wght@400;600;700&display=swap');
        
        * {
            font-family: 'Noto Naskh Arabic', 'Noto Sans', 'Segoe UI', sans-serif;
        }
        
        [dir="rtl"] {
            direction: rtl;
            text-align: right;
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
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize database
    db = get_db()
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"## {get_translation('nav_title')}")
        
        # Language selector
        language = st.selectbox(
            get_translation('language'),
            ["کوردی 🇮🇶", "English 🇬🇧"],
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
    
    result = db.conn.execute("SELECT COUNT(*) as c FROM disease_categories").fetchone()
    categories_count = result['c'] if result else 0
    
    result = db.conn.execute("SELECT COUNT(*) as c FROM test_types").fetchone()
    tests_count = result['c'] if result else 0
    
    result = db.conn.execute("SELECT COUNT(*) as c FROM diseases").fetchone()
    diseases_count = result['c'] if result else 0
    
    result = db.conn.execute("SELECT COUNT(*) as c FROM practical_tests").fetchone()
    practicals_count = result['c'] if result else 0
    
    with col1:
        st.metric(T('disease_categories'), categories_count)
    with col2:
        st.metric(T('laboratory_tests'), tests_count)
    with col3:
        st.metric(T('diseases'), diseases_count)
    with col4:
        st.metric(T('practical_tests'), practicals_count)
    
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
    
    # Get categories from database
    categories = db.conn.execute("SELECT * FROM disease_categories").fetchall()
    
    # Create category options
    category_options = [T('all_categories')]
    category_map = {}
    for cat in categories:
        cat_dict = dict(cat)
        display_name = get_name(cat_dict)
        category_options.append(display_name)
        category_map[display_name] = cat_dict['id']
    
    # Filter
    selected_category = st.selectbox(T('filter_category'), category_options)
    
    # Get all diseases with category info
    diseases = db.conn.execute("""
        SELECT d.*, dc.name_en as cat_name_en, dc.name_ku as cat_name_ku 
        FROM diseases d 
        JOIN disease_categories dc ON d.category_id = dc.id
    """).fetchall()
    
    # Filter by category
    if selected_category != T('all_categories'):
        cat_id = category_map[selected_category]
        diseases = [d for d in diseases if d['category_id'] == cat_id]
    
    # Search
    search = st.text_input(T('search_diseases'))
    if search:
        diseases = [d for d in diseases if search.lower() in get_name(dict(d)).lower()]
    
    if not diseases:
        st.info(T('no_diseases_found'))
        return
    
    # Display diseases
    for disease in diseases:
        disease_dict = dict(disease)
        cat_name = get_name(disease_dict, "cat_name")
        with st.expander(f"🦠 {get_name(disease_dict)} - {cat_name}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**{T('description')}:** {get_description(disease_dict)}")
                
                st.markdown(f"**{T('symptoms')}:**")
                symptoms_text = get_name(disease_dict, "symptoms")
                if symptoms_text:
                    symptoms = symptoms_text.split(',')
                    symptom_html = ""
                    for symptom in symptoms:
                        symptom_html += f"<span class='symptom-tag'>{symptom.strip()}</span>"
                    st.markdown(symptom_html, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"**{T('category')}:**")
                st.info(cat_name)

def render_lab_tests(db: LabDatabase):
    T = get_translation
    
    st.markdown(f"## {T('lab_tests')}")
    
    col1, col2 = st.columns(2)
    with col1:
        # Get unique categories
        all_tests = db.conn.execute("SELECT DISTINCT category FROM test_types").fetchall()
        categories = [T('all_categories')] + [t['category'] for t in all_tests]
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
        all_prac = db.conn.execute("SELECT DISTINCT category FROM practical_tests").fetchall()
        categories = [T('all_categories')] + [p['category'] for p in all_prac]
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
        with st.expander(f"🔬 {get_name(test_dict, 'title')} ({test_dict['duration_minutes']} {T('minutes')})"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**{T('description')}:** {get_description(test_dict)}")
                
                st.markdown(f"### {T('procedure')}")
                steps = get_name(test_dict, 'steps').split('\n')
                for j, step in enumerate(steps):
                    if step.strip():
                        st.markdown(f"<span class='step-number'>{j+1}</span> {step.strip()}", unsafe_allow_html=True)
                
                st.markdown("---")
                
                col_mat, col_exp = st.columns(2)
                with col_mat:
                    st.markdown(f"### {T('materials')}")
                    materials = get_name(test_dict, 'materials').split(',')
                    for mat in materials:
                        st.markdown(f"- {mat.strip()}")
                
                with col_exp:
                    st.markdown(f"### {T('expected_results')}")
                    st.info(get_name(test_dict, 'expected_results'))
            
            with col2:
                st.markdown(f"**{T('category')}:** {test_dict['category']}")
                st.markdown(f"**{T('duration')}:** {test_dict['duration_minutes']} {T('minutes')}")
                
                st.markdown("---")
                st.markdown(f"### {T('interpretation')}")
                st.success(get_name(test_dict, 'interpretation'))

def render_theory_questions(db: LabDatabase):
    T = get_translation
    
    st.markdown(f"## {T('theory')}")
    
    with st.expander(T('add_notes')):
        col1, col2 = st.columns(2)
        with col1:
            topic = st.text_input(T('topic'))
            category = st.selectbox(T('category'), 
                ["Hematology", "Microbiology", "Clinical Chemistry", "Immunology", "Parasitology", "Urinalysis"])
        with col2:
            content = st.text_area(T('content'), height=150)
        
        if st.button(T('save_note')):
            if topic and content:
                db.conn.execute(
                    "INSERT INTO study_notes (topic, content, category) VALUES (?, ?, ?)",
                    (topic, content, category)
                )
                db.conn.commit()
                st.success(T('note_saved'))
            else:
                st.warning(T('write_topic_content'))
    
    st.markdown(f"### {T('your_notes')}")
    notes = db.conn.execute("SELECT * FROM study_notes ORDER BY created_at DESC").fetchall()
    
    if not notes:
        st.info(T('no_notes_yet'))
    else:
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
            patient_age = st.number_input(T('patient_age'), min_value=0, max_value=120, value=30)
        
        with col2:
            patient_gender = st.selectbox(T('patient_gender'), 
                [T('gender_male'), T('gender_female'), T('gender_other')])
            tests = db.conn.execute("SELECT * FROM test_types").fetchall()
            test_options = {get_name(dict(t)): t['id'] for t in tests}
            selected_test = st.selectbox(T('select_test'), list(test_options.keys()))
        
        with col3:
            result_value = st.number_input(T('result_value'), step=0.01, value=0.0)
            result_text = st.text_input(T('result_text'))
        
        notes = st.text_area(T('additional_notes'))
        
        if st.form_submit_button(T('save_result')):
            if not patient_name:
                st.error(T('write_patient_name'))
            else:
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
        SELECT tr.*, tt.name_en as test_name_en, tt.name_ku as test_name_ku, tt.category
        FROM test_results tr 
        JOIN test_types tt ON tr.test_id = tt.id
        ORDER BY tr.date_performed DESC
    """).fetchall()
    
    if results:
        df = pd.DataFrame([dict(r) for r in results])
        
        # Add display name
        df['test_name'] = df.apply(lambda row: get_name(row, 'test_name'), axis=1)
        
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
            if len(category_counts) > 0:
                fig = px.pie(values=category_counts.values, names=category_counts.index, 
                            title=T('tests_by_category'))
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if len(df) > 0:
                normal_count = len(df[df['is_abnormal'] == False])
                abnormal_count = len(df[df['is_abnormal'] == True])
                status_data = pd.DataFrame({
                    'حاڵەت': ['ئاسایی', 'نائاسایی'],
                    'ژمارە': [normal_count, abnormal_count]
                })
                fig = px.bar(status_data, x='حاڵەت', y='ژمارە',
                            title=T('normal_vs_abnormal'),
                            color='حاڵەت',
                            color_discrete_map={'ئاسایی': '#2e7d32', 'نائاسایی': '#c62828'})
                st.plotly_chart(fig, use_container_width=True)
        
        st.markdown(f"### {T('recent_results')}")
        st.dataframe(df[['patient_name', 'test_name', 'result_value', 'is_abnormal', 'date_performed']],
                    use_container_width=True)
    else:
        st.info(T('no_results'))

if __name__ == "__main__":
    main()
