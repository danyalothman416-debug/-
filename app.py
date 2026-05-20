import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from itertools import groupby
import os

# ==================== Page Config ====================
st.set_page_config(
    page_title="سیستەمی شیکردنەوەی تاقیگە - دانیال ئیسماعیل",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== Custom CSS with Better Kurdish Font ====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Naskh+Arabic:wght@400;500;600;700&family=Noto+Sans:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Noto Naskh Arabic', 'Noto Sans', 'Segoe UI', Tahoma, sans-serif !important;
    }
    
    .main-header {
        background: linear-gradient(135deg, #0d47a1 0%, #1565c0 50%, #1976d2 100%);
        color: white;
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 25px;
    }
    
    .student-info {
        background: linear-gradient(135deg, #1a237e, #283593);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 25px;
    }
    
    .category-card {
        background: linear-gradient(135deg, #e8eaf6, #c5cae9);
        padding: 20px;
        border-radius: 12px;
        margin: 10px 0;
        border-right: 5px solid #1565c0;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .category-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .test-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        margin: 12px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #e0e0e0;
    }
    
    .practical-card {
        background: linear-gradient(135deg, #f3e5f5, #e1bee7);
        padding: 20px;
        border-radius: 12px;
        margin: 15px 0;
        border-right: 5px solid #7b1fa2;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #0d47a1, #1565c0);
        color: white !important;
        border: none;
        padding: 12px 28px;
        border-radius: 25px;
        font-weight: bold;
        font-size: 16px;
        width: 100%;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #1565c0, #1976d2);
        transform: translateY(-2px);
    }
    
    .normal-range {
        color: #2e7d32;
        font-weight: bold;
        font-size: 1.1em;
    }
    
    .critical-range {
        color: #c62828;
        font-weight: bold;
    }
    
    .symptom-tag {
        display: inline-block;
        background: #ffebee;
        color: #c62828;
        padding: 5px 12px;
        border-radius: 20px;
        margin: 3px;
        font-size: 0.9em;
    }
    
    .step-number {
        display: inline-block;
        background: #0d47a1;
        color: white;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        text-align: center;
        line-height: 32px;
        margin-left: 8px;
        font-weight: bold;
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
    
    .success-box {
        background: #e8f5e9;
        padding: 15px;
        border-radius: 10px;
        border-right: 4px solid #4caf50;
        margin: 10px 0;
        color: #1a1a1a;
    }
    
    /* Fix white text issue */
    .stMarkdown, .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
        color: #1a1a1a !important;
    }
    
    .stSelectbox label, .stTextInput label, .stTextArea label, .stNumberInput label {
        color: #1a1a1a !important;
        font-weight: 600 !important;
    }
    
    [dir="rtl"] {
        direction: rtl;
        text-align: right;
    }
</style>
""", unsafe_allow_html=True)

# ==================== Database Setup ====================
@st.cache_resource
def init_db():
    """Initialize database with proper error handling"""
    try:
        conn = sqlite3.connect('medical_lab.db', check_same_thread=False)
        conn.row_factory = sqlite3.Row
        
        conn.executescript("""
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
                is_abnormal INTEGER DEFAULT 0,
                notes TEXT,
                date_performed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (test_id) REFERENCES test_types(id)
            );
        """)
        
        conn.commit()
        return conn
    except Exception as e:
        st.error(f"Database error: {e}")
        return None

# ==================== Insert Initial Data ====================
def insert_data(conn):
    """Insert initial data if tables are empty"""
    try:
        # Check if data exists
        count = conn.execute("SELECT COUNT(*) as c FROM test_types").fetchone()
        if count and count['c'] > 0:
            return
        
        # Disease Categories
        categories = [
            ("Hematology", "خوێنناسی", "Blood disorders and diseases", "نەخۆشی و تێکچوونەکانی خوێن", "🩸"),
            ("Microbiology", "مایکرۆبایۆلۆجی", "Bacterial, viral, fungal infections", "هەوکردنی بەکتریایی، ڤایرۆسی، کەڕوویی", "🦠"),
            ("Clinical Chemistry", "کیمیای کلینیکی", "Chemical analysis of body fluids", "شیکردنەوەی کیمیایی شلەکانی لەش", "🧪"),
            ("Immunology", "ئیمیونۆلۆجی", "Immune system disorders", "تێکچوونەکانی سیستەمی بەرگری", "🛡️"),
            ("Parasitology", "مشقوڕخوێناسی", "Parasitic infections", "هەوکردنی مشقوڕخوەکان", "🐛"),
            ("Urinalysis", "شیکردنەوەی میز", "Urine analysis", "شیکردنەوەی میز", "💧"),
            ("Serology", "سیرۆلۆجی", "Blood serum analysis", "شیکردنەوەی شلەی خوێن", "💉"),
        ]
        
        conn.executemany(
            "INSERT INTO disease_categories (name_en, name_ku, description_en, description_ku, icon) VALUES (?, ?, ?, ?, ?)",
            categories
        )
        
        # Test Types with complete details
        tests = [
            ("CBC - Complete Blood Count", "CBC - ژماردنی تەواوی خوێن",
             "Hematology", "cells/μL", 4.5, 11.0, 2.0, 15.0,
             "Complete blood cell count - measures RBC, WBC, hemoglobin, hematocrit, and platelets. Essential for diagnosing anemia, infection, and blood disorders.",
             "ژماردنی تەواوی خانەکانی خوێن - خانە سوورەکان، خانە سپییەکان، هیمۆگلۆبین، هیماتۆکریت و پلەیکلتەکان دەپێورێت. پێویستە بۆ دەستنیشانکردنی کەمخوێنی، هەوکردن و نەخۆشییەکانی خوێن."),
            
            ("WBC Count", "ژماردنی خانە سپییەکانی خوێن (WBC)",
             "Hematology", "×10³/μL", 4.0, 11.0, 2.0, 30.0,
             "White blood cell count - indicates infection, inflammation, or immune system disorders. Elevated in bacterial infections, decreased in viral infections.",
             "ژماردنی خانە سپییەکانی خوێن - نیشاندەری هەوکردن، هەوکردنی ناوەکی، یان تێکچوونی سیستەمی بەرگری. لە هەوکردنی بەکتریاییدا بەرز دەبێتەوە، لە هەوکردنی ڤایرۆسیدا کەم دەبێتەوە."),
            
            ("Hemoglobin (Hb)", "هیمۆگلۆبین (Hb)",
             "Hematology", "g/dL", 12.0, 16.0, 6.0, 20.0,
             "Hemoglobin level - protein in red blood cells that carries oxygen. Low levels indicate anemia, high levels may indicate polycythemia.",
             "ئاستی هیمۆگلۆبین - پڕۆتینێکە لە خانە سوورەکانی خوێندا کە ئۆکسجین هەڵدەگرێت. ئاستی نزم نیشاندەری کەمخوێنییە، ئاستی بەرز ڕەنگە نیشاندەری پۆلیسایتمیا بێت."),
            
            ("Blood Glucose Fasting", "گلوکۆزی خوێن بە بەڕۆژوویی",
             "Clinical Chemistry", "mg/dL", 70, 100, 40, 300,
             "Fasting blood sugar - screens for diabetes mellitus. Patient must fast for 8-12 hours before test.",
             "شەکری خوێن بە بەڕۆژوویی - بۆ پشکنینی نەخۆشی شەکرە. نەخۆش دەبێت ٨-١٢ کاتژمێر بەڕۆژوو بێت پێش پشکنینەکە."),
            
            ("Creatinine", "کریاتینین",
             "Clinical Chemistry", "mg/dL", 0.6, 1.2, 0.2, 5.0,
             "Kidney function marker - waste product from muscle metabolism filtered by kidneys. Elevated levels indicate impaired kidney function.",
             "نیشاندەری کاری گورچیلە - ماددەیەکی بەفیڕۆدراوی میتابۆلیزیمی ماسولکەیە کە گورچیلە پاڵێوی دەکات. ئاستی بەرز نیشاندەری تێکچوونی کاری گورچیلەیە."),
            
            ("ALT (SGPT)", "ئەنزیمی ALT (SGPT)",
             "Clinical Chemistry", "U/L", 7, 56, 5, 200,
             "Alanine aminotransferase - liver enzyme. Elevated in hepatitis, liver damage, or liver disease.",
             "ئالانین ئەمینۆترانسفێرەیس - ئەنزیمی جگەر. لە هەوکردنی جگەر، تێکچوونی جگەر، یان نەخۆشی جگەردا بەرز دەبێتەوە."),
        ]
        
        conn.executemany("""
            INSERT INTO test_types 
            (name_en, name_ku, category, unit, normal_range_low, normal_range_high, 
             critical_low, critical_high, description_en, description_ku)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, tests)
        
        # Diseases
        diseases = [
            (1, "Anemia", "کەمخوێنی",
             "Decreased red blood cells or hemoglobin. Types include iron deficiency, B12 deficiency, and hemolytic anemia.",
             "کەمبوونەوەی خانە سوورەکانی خوێن یان هیمۆگلۆبین. جۆرەکانی بریتین لە کەمخوێنی بەهۆی کەمی ئاسن، کەمی ڤیتامین B12، و کەمخوێنی هیمۆلیتیک.",
             "Fatigue, weakness, pale skin, shortness of breath, dizziness, cold hands/feet, brittle nails",
             "ماندوویی، لاوازی، ڕەنگی پێستی کاڵ، تەنگی هەناسە، سەرگێژخواردن، دەست و قاچی سارد، نینۆکی ناسک"),
            
            (3, "Diabetes Mellitus", "نەخۆشی شەکرە",
             "Chronic high blood sugar due to insulin deficiency or resistance. Type 1 is autoimmune, Type 2 is metabolic.",
             "شەکری بەرزی خوێنی درێژخایەن بەهۆی کەمی ئینسولین یان بەرگری بەرامبەر ئینسولین. جۆری ١ خۆبەرگرییە، جۆری ٢ میتابۆلیکییە.",
             "Increased thirst, frequent urination, fatigue, blurred vision, slow healing wounds, tingling in hands/feet",
             "تینوێتی زۆر، میزکردنی زۆر، ماندوویی، بینینی شێواو، برینی درەنگ چاکبووەوە، کزوزە لە دەست و قاچدا"),
        ]
        
        conn.executemany("""
            INSERT INTO diseases 
            (category_id, name_en, name_ku, description_en, description_ku, symptoms_en, symptoms_ku)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, diseases)
        
        # Practical Tests
        practicals = [
            ("Blood Smear Preparation", "ئامادەکردنی سمێری خوێن",
             "Learn to prepare and stain peripheral blood smears for microscopic examination of blood cells",
             "فێربوونی ئامادەکردن و ڕەنگکردنی سمێری خوێنی چواردەوری بۆ پشکنینی مایکرۆسکۆپی خانەکانی خوێن",
             "Hematology",
             "1. Clean glass slide with alcohol\n2. Place small blood drop near slide end\n3. Hold spreader at 30-45° angle\n4. Pull spreader back into blood drop\n5. Push forward smoothly to create feathered edge\n6. Air dry completely (5-10 min)\n7. Fix in absolute methanol (2-3 min)\n8. Stain with Wright-Giemsa (3-5 min)\n9. Add buffer, wait 10-15 min\n10. Rinse gently with distilled water\n11. Dry and examine under microscope",
             "١. پاککردنەوەی سلاید بە ئەلکحول\n٢. دانانی دڵۆپێکی بچووکی خوێن لە نزیک لێواری سلاید\n٣. ڕاگرتنی بڵاوکەرەوە بە گۆشەی ٣٠-٤٥ پلە\n٤. ڕاکێشانی بڵاوکەرەوە بۆ ناو دڵۆپەکە\n٥. پاڵنانی بەرەو پێشەوە بۆ دروستکردنی لێواری پەڕیشی\n٦. وشکبوونەوەی تەواو (٥-١٠ خولەک)\n٧. جێگیرکردن لە میسانۆلی پەتدا (٢-٣ خولەک)\n٨. ڕەنگکردن بە رایت-گیمسا (٣-٥ خولەک)\n٩. زیادکردنی بەفەر، چاوەڕوانی ١٠-١٥ خولەک\n١٠. شۆردنی نەرم بە ئاوی مونەققە\n١١. وشککردن و پشکنین لەژێر مایکرۆسکۆپ",
             "Glass slides, sterile lancet, blood sample, Wright-Giemsa stain, absolute methanol, buffer solution, distilled water, microscope",
             "سلایدی شووشەیی، لانسێتی ستێرایل، نموونەی خوێن، ڕەنگی رایت-گیمسا، میسانۆلی پەت، گیراوەی بەفەر، ئاوی مونەققە، مایکرۆسکۆپ",
             "Well-spread monolayer of cells with feathered edge. RBCs appear pink-red, WBCs show purple nuclei, platelets appear as small purple fragments",
             "توێژاڵێکی یەک خانەیی بە باشی بڵاوکراوە لەگەڵ لێواری پەڕیشی. خانە سوورەکان پەمەیی-سوور، خانە سپییەکان ناوکی وەنەوشەیی، پلەیکلتەکان وەک پارچەی وەنەوشەیی بچووک دەردەکەون",
             "Examine for RBC morphology (size, shape, color), WBC differential count, platelet estimate, and parasites. Abnormal findings may indicate anemia, infection, or leukemia",
             "پشکنین بۆ شێوەزانی خانە سوورەکان، ژماردنی جیاکاری خانە سپییەکان، خەمڵاندنی پلەیکلت، و مشقوڕخوەکان. دۆزینەوە نائاساییەکان نیشاندەری کەمخوێنی، هەوکردن، یان لۆکیمیان",
             45, "Basic"),
        ]
        
        conn.executemany("""
            INSERT INTO practical_tests 
            (title_en, title_ku, description_en, description_ku,
             category, steps_en, steps_ku, materials_en, materials_ku,
             expected_results_en, expected_results_ku,
             interpretation_en, interpretation_ku,
             duration_minutes, difficulty_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, practicals)
        
        conn.commit()
    except Exception as e:
        st.error(f"Error inserting data: {e}")

# Initialize database
conn = init_db()
if conn:
    insert_data(conn)

# ==================== Translation Helper ====================
def t(key):
    """Get translation for current language"""
    translations = {
        "English 🇬🇧": {
            "app_title": "Medical Laboratory Analysis System",
            "student_name": "Danyal Ismail",
            "stage": "Fourth Stage - Disease Analysis",
            "welcome": "Welcome",
            "dashboard": "📊 Dashboard",
            "disease_db": "🦠 Disease Database",
            "lab_tests": "🧪 Laboratory Tests",
            "practical": "🔬 Practical Tests",
            "theory": "📚 Study Notes",
            "results_entry": "📝 Test Results",
            "reports": "📈 Reports",
            "ai_chat": "🤖 AI Assistant",
            "nav_title": "Navigation",
            "select_section": "Select Section",
            "language": "Language",
            "filter_category": "Filter by Category",
            "all_categories": "All Categories",
            "search": "Search",
            "description": "Description",
            "symptoms": "Symptoms",
            "category": "Category",
            "unit": "Unit",
            "normal_range": "Normal Range",
            "critical_values": "Critical Values",
            "low": "Low",
            "high": "High",
            "procedure": "Procedure Steps",
            "materials": "Materials Required",
            "expected_results": "Expected Results",
            "interpretation": "Interpretation",
            "duration": "Duration",
            "minutes": "minutes",
            "patient_name": "Patient Name",
            "patient_age": "Patient Age",
            "patient_gender": "Patient Gender",
            "select_test": "Select Test",
            "result_value": "Result Value",
            "save_result": "Save Result",
            "total_tests": "Total Tests",
            "abnormal_results": "Abnormal Results",
            "normal_rate": "Normal Rate",
            "recent_results": "Recent Results",
            "no_results": "No results yet",
            "saved_success": "Saved successfully!",
            "abnormal_warning": "Abnormal result detected!",
            "add_notes": "Add Study Notes",
            "topic": "Topic",
            "content": "Content",
            "save_note": "Save Note",
            "your_notes": "Your Notes",
            "delete": "Delete",
            "ask_ai": "Ask me anything about laboratory tests...",
            "type_question": "Type your question here...",
        },
        "کوردی 🇹🇯": {
            "app_title": "سیستەمی شیکردنەوەی تاقیگەی پزیشکی",
            "student_name": "دانیال ئیسماعیل",
            "stage": "قۆناغی چوارەم - شیکردنەوەی نەخۆشییەکان",
            "welcome": "بەخێربێیت",
            "dashboard": "📊 داشبۆرد",
            "disease_db": "🦠 بنکەدراوەی نەخۆشییەکان",
            "lab_tests": "🧪 پشکنینە تاقیگەییەکان",
            "practical": "🔬 پشکنینی پراکتیکی",
            "theory": "📚 تێبینییەکان",
            "results_entry": "📝 تۆمارکردنی ئەنجام",
            "reports": "📈 ڕاپۆرتەکان",
            "ai_chat": "🤖 یارمەتی زیرەک",
            "nav_title": "ڕێنیشاندەر",
            "select_section": "بەش هەڵبژێرە",
            "language": "زمان",
            "filter_category": "پاڵێوکردن بەپێی بەش",
            "all_categories": "هەموو بەشەکان",
            "search": "گەڕان",
            "description": "ڕوونکردنەوە",
            "symptoms": "نیشانەکان",
            "category": "بەش",
            "unit": "یەکە",
            "normal_range": "مەودای ئاسایی",
            "critical_values": "بەهای مەترسیدار",
            "low": "نزم",
            "high": "بەرز",
            "procedure": "هەنگاوەکانی پڕۆسێجەر",
            "materials": "کەرەستە پێویستەکان",
            "expected_results": "ئەنجامی چاوەڕوانکراو",
            "interpretation": "لێکدانەوە",
            "duration": "ماوە",
            "minutes": "خولەک",
            "patient_name": "ناوی نەخۆش",
            "patient_age": "تەمەنی نەخۆش",
            "patient_gender": "ڕەگەزی نەخۆش",
            "select_test": "پشکنین هەڵبژێرە",
            "result_value": "بەهای ئەنجام",
            "save_result": "تۆمارکردنی ئەنجام",
            "total_tests": "کۆی گشتی",
            "abnormal_results": "نائاسایی",
            "normal_rate": "ڕێژەی ئاسایی",
            "recent_results": "دوایین ئەنجامەکان",
            "no_results": "هێشتا هیچ ئەنجامێک نییە",
            "saved_success": "بە سەرکەوتوویی تۆمارکرا!",
            "abnormal_warning": "ئەنجامی نائاسایی دۆزرایەوە!",
            "add_notes": "زیادکردنی تێبینی",
            "topic": "بابەت",
            "content": "ناوەڕۆک",
            "save_note": "تۆمارکردن",
            "your_notes": "تێبینییەکانت",
            "delete": "سڕینەوە",
            "ask_ai": "هەر پرسیارێکی تاقیگەییت هەیە لێم بپرسە...",
            "type_question": "پرسیارەکەت لێرە بنووسە...",
        }
    }
    
    lang = st.session_state.get('language', 'کوردی 🇹🇯')
    return translations.get(lang, translations['کوردی 🇹🇯']).get(key, key)

def get_name(row, prefix="name"):
    """Get localized name from database row"""
    lang_map = {"English 🇬🇧": "en", "کوردی 🇹🇯": "ku"}
    lang = lang_map.get(st.session_state.get('language', 'کوردی 🇹🇯'), 'ku')
    field = f"{prefix}_{lang}"
    if isinstance(row, dict):
        return row.get(field, row.get(f"{prefix}_en", ""))
    else:
        return row[field] if field in row.keys() else row[f"{prefix}_en"]

def get_desc(row):
    """Get localized description"""
    return get_name(row, "description")

# ==================== AI Chat Function ====================
def get_gemini_response(question):
    """Get response from Gemini AI or fallback to local knowledge"""
    try:
        # Try to use Gemini API if available
        api_key = os.environ.get('GEMINI_API_KEY', '')
        if api_key:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')
            
            prompt = f"""
            تۆ یارمەتیدەری زیرەکی بۆ قوتابیانی شیکاری نەخۆشی کوردی.
            تکایە بە زمانی کوردی وەڵامی ئەم پرسیارە بدەوە:
            
            پرسیار: {question}
            
            ئەگەر پرسیارەکە پەیوەندی بە پشکنینە تاقیگەییەکان، نەخۆشییەکان، یان پڕۆسێجەری تاقیگەوە هەیە، 
            ڕوونکردنەوەیەکی زانستی و تەواو بدە.
            ئەگەر نەخێر، بە ڕێزەوە ڕێنمایی بکە بۆ پرسیاری پەیوەندیدار.
            """
            
            response = model.generate_content(prompt)
            return response.text
    except:
        pass
    
    # Fallback to local knowledge
    q = question.lower()
    
    # Search in database
    try:
        tests = conn.execute("SELECT * FROM test_types").fetchall()
        for test in tests:
            test_name_ku = get_name(dict(test))
            test_name_en = get_name(dict(test), "name")
            if test_name_ku.lower() in q or test_name_en.lower() in q:
                return f"""
**🎯 {test_name_ku}**

**📊 {t('unit')}:** {test['unit']}
**✅ {t('normal_range')}:** {test['normal_range_low']} - {test['normal_range_high']}
**⚠️ {t('critical_values')}:** < {test['critical_low']} یان > {test['critical_high']}

**📝 {t('description')}:**
{get_desc(dict(test))}
                """
        
        diseases = conn.execute("""
            SELECT d.*, dc.name_ku as cat_name 
            FROM diseases d 
            JOIN disease_categories dc ON d.category_id = dc.id
        """).fetchall()
        
        for disease in diseases:
            disease_name = get_name(dict(disease))
            if disease_name.lower() in q:
                return f"""
**🦠 {disease_name}**
**📂 {t('category')}:** {dict(disease)['cat_name']}

**📝 {t('description')}:**
{get_desc(dict(disease))}

**🔴 {t('symptoms')}:**
{get_name(dict(disease), 'symptoms')}
                """
    except:
        pass
    
    return f"""
**ببورە، نەمتوانی وەڵامی ڕاستەوخۆ بدۆزمەوە. 😔**

**تکایە پرسیار لەسەر ئەم بابەتانە بکە:**
- 🔬 پشکنینەکانی خوێن (CBC، هیمۆگلۆبین، WBC)
- 🧪 پشکنینە کیمیاییەکان (گلوکۆز، کریاتینین، ئەنزیمەکانی جگەر)
- 🦠 نەخۆشییەکان (کەمخوێنی، شەکرە، هەوکردنی میزەڕۆ)
- 🔬 پڕۆسێجەری تاقیگە (ڕەنگکردنی گرام، ئامادەکردنی سمێری خوێن)

**یان دەتوانیت لە بەشەکانی تر بگەڕێیت! 📚**
"""

# ==================== Main App ====================
def main():
    # Initialize language
    if 'language' not in st.session_state:
        st.session_state.language = 'کوردی 🇹🇯'
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🔬 ڕێنیشاندەر")
        
        language = st.selectbox(
            "🌐 زمان",
            ["کوردی 🇹🇯", "English 🇬🇧"],
            key="lang_sel"
        )
        if language != st.session_state.language:
            st.session_state.language = language
            st.rerun()
        
        st.markdown("---")
        
        pages = {
            t('dashboard'): 'dashboard',
            t('disease_db'): 'disease_db',
            t('lab_tests'): 'lab_tests',
            t('practical'): 'practical',
            t('theory'): 'theory',
            t('results_entry'): 'results_entry',
            t('reports'): 'reports',
            t('ai_chat'): 'ai_chat'
        }
        
        page = st.radio(t('select_section'), list(pages.keys()), key="page_sel")
        current_page = pages[page]
    
    # Header
    st.markdown(f"""
    <div class="student-info">
        <h2>🎓 {t('welcome')}، {t('student_name')}</h2>
        <p>{t('stage')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Route
    if current_page == 'dashboard':
        render_dashboard()
    elif current_page == 'disease_db':
        render_diseases()
    elif current_page == 'lab_tests':
        render_tests()
    elif current_page == 'practical':
        render_practical()
    elif current_page == 'theory':
        render_notes()
    elif current_page == 'results_entry':
        render_results()
    elif current_page == 'reports':
        render_reports()
    elif current_page == 'ai_chat':
        render_ai_chat()

def render_dashboard():
    st.markdown(f"## {t('dashboard')}")
    
    try:
        cats = conn.execute("SELECT COUNT(*) as c FROM disease_categories").fetchone()['c']
        tests = conn.execute("SELECT COUNT(*) as c FROM test_types").fetchone()['c']
        diseases = conn.execute("SELECT COUNT(*) as c FROM diseases").fetchone()['c']
        practicals = conn.execute("SELECT COUNT(*) as c FROM practical_tests").fetchone()['c']
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("📂 بەشەکان", cats)
        c2.metric("🧪 پشکنینەکان", tests)
        c3.metric("🦠 نەخۆشییەکان", diseases)
        c4.metric("🔬 پراکتیکی", practicals)
    except:
        st.warning("هێشتا زانیاری نییە")
    
    st.markdown("## 📂 بەشەکانی نەخۆشییەکان")
    
    try:
        categories = conn.execute("SELECT * FROM disease_categories").fetchall()
        cols = st.columns(2)
        for i, cat in enumerate(categories):
            with cols[i % 2]:
                st.markdown(f"""
                <div class="category-card">
                    <h3>{cat['icon']} {get_name(dict(cat))}</h3>
                    <p>{get_desc(dict(cat))}</p>
                </div>
                """, unsafe_allow_html=True)
    except:
        pass

def render_diseases():
    st.markdown(f"## 🦠 {t('disease_db')}")
    
    try:
        categories = conn.execute("SELECT * FROM disease_categories").fetchall()
        cat_opts = {t('all_categories'): None}
        for cat in categories:
            cat_opts[get_name(dict(cat))] = cat['id']
        
        selected = st.selectbox(t('filter_category'), list(cat_opts.keys()))
        cat_id = cat_opts[selected]
        
        if cat_id:
            diseases = conn.execute("""
                SELECT d.*, dc.name_en as ce, dc.name_ku as ck
                FROM diseases d 
                JOIN disease_categories dc ON d.category_id = dc.id
                WHERE d.category_id = ?
            """, (cat_id,)).fetchall()
        else:
            diseases = conn.execute("""
                SELECT d.*, dc.name_en as ce, dc.name_ku as ck
                FROM diseases d 
                JOIN disease_categories dc ON d.category_id = dc.id
            """).fetchall()
        
        for disease in diseases:
            d = dict(disease)
            cat_name = get_name(d, "c")
            with st.expander(f"🦠 {get_name(d)} - {cat_name}"):
                st.markdown(f"### {t('description')}")
                st.write(get_desc(d))
                
                st.markdown(f"### {t('symptoms')}")
                symptoms = get_name(d, 'symptoms')
                if symptoms:
                    for s in symptoms.split(','):
                        st.markdown(f"<span class='symptom-tag'>{s.strip()}</span>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"هەڵە: {e}")

def render_tests():
    st.markdown(f"## 🧪 {t('lab_tests')}")
    
    try:
        tests = conn.execute("SELECT * FROM test_types").fetchall()
        
        # Group by category
        sorted_tests = sorted(tests, key=lambda x: x['category'])
        
        for category, group in groupby(sorted_tests, key=lambda x: x['category']):
            st.markdown(f"### 📁 {category}")
            
            for test in group:
                td = dict(test)
                with st.expander(f"📊 {get_name(td)}"):
                    st.markdown(f"""
                    <div class="info-box">
                        <p><strong>{t('unit')}:</strong> {td['unit']}</p>
                        <p><strong class="normal-range">{t('normal_range')}: {td['normal_range_low']} - {td['normal_range_high']}</strong></p>
                        <p><strong>{t('description')}:</strong> {get_desc(td)}</p>
                    </div>
                    
                    <div class="warning-box">
                        <h4>{t('critical_values')}</h4>
                        <p>{t('low')}: <span class="critical-range">< {td['critical_low']}</span></p>
                        <p>{t('high')}: <span class="critical-range">> {td['critical_high']}</span></p>
                    </div>
                    """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"هەڵە: {e}")

def render_practical():
    st.markdown(f"## 🔬 {t('practical')}")
    
    try:
        practicals = conn.execute("SELECT * FROM practical_tests").fetchall()
        
        for test in practicals:
            td = dict(test)
            with st.expander(f"🔬 {get_name(td, 'title')} ({td['duration_minutes']} {t('minutes')})"):
                st.markdown(f"### {t('description')}")
                st.write(get_desc(td))
                
                st.markdown(f"### {t('procedure')}")
                steps = get_name(td, 'steps').split('\n')
                for i, step in enumerate(steps):
                    if step.strip():
                        st.markdown(f"<p><span class='step-number'>{i+1}</span> {step.strip()}</p>", unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"### {t('materials')}")
                    for m in get_name(td, 'materials').split(','):
                        st.markdown(f"- {m.strip()}")
                with col2:
                    st.markdown(f"### {t('expected_results')}")
                    st.info(get_name(td, 'expected_results'))
                
                st.markdown(f"### {t('interpretation')}")
                st.success(get_name(td, 'interpretation'))
    except Exception as e:
        st.error(f"هەڵە: {e}")

def render_notes():
    st.markdown(f"## 📚 {t('theory')}")
    
    with st.expander(t('add_notes'), expanded=True):
        topic = st.text_input(t('topic'))
        content = st.text_area(t('content'), height=150)
        if st.button(t('save_note'), use_container_width=True):
            if topic and content:
                conn.execute("INSERT INTO study_notes (topic, content) VALUES (?, ?)", (topic, content))
                conn.commit()
                st.success(t('saved_success'))
                st.rerun()
    
    notes = conn.execute("SELECT * FROM study_notes ORDER BY created_at DESC").fetchall()
    if notes:
        for note in notes:
            with st.expander(f"📝 {note['topic']}"):
                st.write(note['content'])
                if st.button(t('delete'), key=f"d_{note['id']}"):
                    conn.execute("DELETE FROM study_notes WHERE id = ?", (note['id'],))
                    conn.commit()
                    st.rerun()
    else:
        st.info("هێشتا هیچ تێبینییەکت نییە")

def render_results():
    st.markdown(f"## 📝 {t('results_entry')}")
    
    try:
        with st.form("results_form"):
            name = st.text_input(t('patient_name'))
            age = st.number_input(t('patient_age'), 0, 120, 30)
            gender = st.selectbox(t('patient_gender'), ["نێر", "مێ"])
            
            all_tests = conn.execute("SELECT * FROM test_types").fetchall()
            test_opts = {get_name(dict(t)): t['id'] for t in all_tests}
            selected_test = st.selectbox(t('select_test'), list(test_opts.keys()))
            
            value = st.number_input(t('result_value'), step=0.01)
            
            if st.form_submit_button(t('save_result'), use_container_width=True):
                if name:
                    tid = test_opts[selected_test]
                    test = conn.execute("SELECT * FROM test_types WHERE id = ?", (tid,)).fetchone()
                    abnormal = 1 if (value < test['normal_range_low'] or value > test['normal_range_high']) else 0
                    
                    conn.execute("""
                        INSERT INTO test_results (patient_name, patient_age, patient_gender, test_id, result_value, is_abnormal)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (name, age, gender, tid, value, abnormal))
                    conn.commit()
                    
                    st.success(t('saved_success'))
                    if abnormal:
                        st.warning(t('abnormal_warning'))
                else:
                    st.error("تکایە ناوی نەخۆش بنووسە")
    except Exception as e:
        st.error(f"هەڵە: {e}")

def render_reports():
    st.markdown(f"## 📈 {t('reports')}")
    
    try:
        results = conn.execute("""
            SELECT tr.*, tt.name_en as ten, tt.name_ku as tku, tt.category
            FROM test_results tr
            JOIN test_types tt ON tr.test_id = tt.id
            ORDER BY tr.date_performed DESC
        """).fetchall()
        
        if not results:
            st.info(t('no_results'))
            return
        
        df = pd.DataFrame([dict(r) for r in results])
        
        # Add display names
        def get_test_name(row):
            lang_map = {"English 🇬🇧": "en", "کوردی 🇹🇯": "ku"}
            lang = lang_map.get(st.session_state.get('language', 'کوردی 🇹🇯'), 'ku')
            field = f"t{lang}"
            return row.get(field, row.get('ten', ''))
        
        df['test_name'] = df.apply(get_test_name, axis=1)
        
        c1, c2, c3 = st.columns(3)
        c1.metric(t('total_tests'), len(df))
        abnormal = len(df[df['is_abnormal'] == 1])
        c2.metric(t('abnormal_results'), abnormal)
        normal_pct = ((len(df) - abnormal) / len(df) * 100) if len(df) > 0 else 0
        c3.metric(t('normal_rate'), f"{normal_pct:.1f}%")
        
        st.markdown(f"### {t('recent_results')}")
        st.dataframe(df[['patient_name', 'test_name', 'result_value', 'is_abnormal', 'date_performed']], use_container_width=True)
    except Exception as e:
        st.error(f"هەڵە لە ڕاپۆرتەکان: {e}")

def render_ai_chat():
    st.markdown(f"## 🤖 {t('ai_chat')}")
    st.markdown(f"### {t('ask_ai')}")
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat
    for chat in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(chat['question'])
        with st.chat_message("assistant"):
            st.markdown(chat['answer'])
    
    # Input
    question = st.chat_input(t('type_question'))
    
    if question:
        with st.chat_message("user"):
            st.write(question)
        
        with st.chat_message("assistant"):
            with st.spinner("بیردەکەمەوە..."):
                answer = get_gemini_response(question)
                st.markdown(answer)
        
        st.session_state.chat_history.append({"question": question, "answer": answer})

# ==================== Run App ====================
if __name__ == "__main__":
    if conn:
        main()
    else:
        st.error("نەتوانرا داتابەیس بکرێتەوە. تکایە دووبارە هەوڵ بدەوە.")
