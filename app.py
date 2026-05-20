import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from itertools import groupby

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
    @import url('https://fonts.googleapis.com/css2?family=Noto+Naskh+Arabic:wght@400;600;700&display=swap');
    
    * {
        font-family: 'Noto Naskh Arabic', 'Segoe UI', sans-serif;
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
        color: white;
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
    }
    
    .warning-box {
        background: #fff3e0;
        padding: 15px;
        border-radius: 10px;
        border-right: 4px solid #ff9800;
        margin: 10px 0;
    }
    
    .success-box {
        background: #e8f5e9;
        padding: 15px;
        border-radius: 10px;
        border-right: 4px solid #4caf50;
        margin: 10px 0;
    }
    
    [dir="rtl"] {
        direction: rtl;
        text-align: right;
    }
</style>
""", unsafe_allow_html=True)

# ==================== Database ====================
def init_database():
    """Initialize database with all tables"""
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
            is_abnormal BOOLEAN,
            notes TEXT,
            date_performed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (test_id) REFERENCES test_types(id)
        );
    """)
    
    conn.commit()
    return conn

@st.cache_resource
def get_connection():
    return init_database()

# ==================== Data Insertion ====================
def insert_initial_data(conn):
    """Insert initial data if not exists"""
    
    # Check if data already exists
    check = conn.execute("SELECT COUNT(*) as c FROM disease_categories").fetchone()
    if check['c'] > 0:
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
    
    # Test Types with full details
    tests = [
        ("CBC - Complete Blood Count", "CBC - ژماردنی تەواوی خوێن",
         "Hematology", "cells/μL", 4.5, 11.0, 2.0, 15.0,
         "Complete blood cell count - measures red blood cells, white blood cells, hemoglobin, hematocrit, and platelets",
         "ژماردنی تەواوی خانەکانی خوێن - خانە سوورەکان، خانە سپییەکان، هیمۆگلۆبین، هیماتۆکریت و پلەیکلتەکان دەپێورێت"),
        
        ("WBC Count", "ژماردنی خانە سپییەکانی خوێن",
         "Hematology", "×10³/μL", 4.0, 11.0, 2.0, 30.0,
         "White blood cell count - indicates infection, inflammation, or immune system disorders",
         "ژماردنی خانە سپییەکانی خوێن - نیشاندەری هەوکردن، هەوکردنی ناوەکی، یان تێکچوونی سیستەمی بەرگری"),
        
        ("RBC Count", "ژماردنی خانە سوورەکانی خوێن",
         "Hematology", "×10⁶/μL", 4.5, 5.5, 2.0, 7.0,
         "Red blood cell count - carries oxygen throughout the body",
         "ژماردنی خانە سوورەکانی خوێن - ئۆکسجین بە هەموو لەشدا دەگوازێتەوە"),
        
        ("Hemoglobin", "هیمۆگلۆبین",
         "Hematology", "g/dL", 12.0, 16.0, 6.0, 20.0,
         "Hemoglobin level - protein in red blood cells that carries oxygen",
         "ئاستی هیمۆگلۆبین - پڕۆتینێکە لە خانە سوورەکانی خوێندا کە ئۆکسجین هەڵدەگرێت"),
        
        ("Platelet Count", "ژماردنی پلەیکلت",
         "Hematology", "×10³/μL", 150, 400, 50, 1000,
         "Platelet count - essential for blood clotting",
         "ژماردنی پلەیکلتەکان - پێویستە بۆ مەیینەوەی خوێن"),
        
        ("Blood Glucose Fasting", "گلوکۆزی خوێن بە بەڕۆژوویی",
         "Clinical Chemistry", "mg/dL", 70, 100, 40, 300,
         "Fasting blood sugar - screens for diabetes",
         "شەکری خوێن بە بەڕۆژوویی - بۆ پشکنینی شەکرە"),
        
        ("HbA1c", "هیمۆگلۆبینی گڵایکەیتکراو",
         "Clinical Chemistry", "%", 4.0, 5.6, 3.0, 10.0,
         "Glycated hemoglobin - average blood sugar over 2-3 months",
         "هیمۆگلۆبینی گڵایکەیتکراو - تێکڕای شەکری خوێن بۆ ماوەی ٢-٣ مانگ"),
        
        ("Creatinine", "کریاتینین",
         "Clinical Chemistry", "mg/dL", 0.6, 1.2, 0.2, 5.0,
         "Kidney function marker - waste product filtered by kidneys",
         "نیشاندەری کاری گورچیلە - ماددەیەکی بەفیڕۆدراوە کە گورچیلە پاڵێوی دەکات"),
        
        ("ALT", "ئەنزیمی ALT",
         "Clinical Chemistry", "U/L", 7, 56, 5, 200,
         "Alanine aminotransferase - liver enzyme, elevated in liver damage",
         "ئالانین ئەمینۆترانسفێرەیس - ئەنزیمی جگەر، لە تێکچوونی جگەردا بەرز دەبێتەوە"),
        
        ("AST", "ئەنزیمی AST",
         "Clinical Chemistry", "U/L", 10, 40, 5, 200,
         "Aspartate aminotransferase - liver and heart enzyme",
         "ئەسپارتەیت ئەمینۆترانسفێرەیس - ئەنزیمی جگەر و دڵ"),
        
        ("Total Cholesterol", "کۆلیستڕۆڵی گشتی",
         "Clinical Chemistry", "mg/dL", 125, 200, 100, 300,
         "Total cholesterol - risk factor for heart disease",
         "کۆلیستڕۆڵی گشتی - هۆکاری مەترسی بۆ نەخۆشی دڵ"),
        
        ("Urine pH", "pH ی میز",
         "Urinalysis", "pH", 4.5, 8.0, 4.0, 9.0,
         "Urine acidity - indicates metabolic or kidney disorders",
         "ترشێتی میز - نیشاندەری تێکچوونی میتابۆلیکی یان گورچیلەیی"),
        
        ("Urine Protein", "پڕۆتینی میز",
         "Urinalysis", "mg/dL", 0, 8, 0, 30,
         "Protein in urine - sign of kidney disease",
         "پڕۆتین لە میزدا - نیشانەی نەخۆشی گورچیلە"),
        
        ("CRP", "پڕۆتینی C-C-reactive",
         "Serology", "mg/L", 0, 3, 0, 10,
         "C-reactive protein - marker of inflammation",
         "پڕۆتینی C-کاردانەوەیی - نیشاندەری هەوکردن"),
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
         "Decreased red blood cells or hemoglobin - can be caused by iron deficiency, vitamin B12 deficiency, or chronic disease",
         "کەمبوونەوەی خانە سوورەکانی خوێن یان هیمۆگلۆبین - دەکرێت بەهۆی کەمی ئاسن، کەمی ڤیتامین B12، یان نەخۆشی درێژخایەنەوە بێت",
         "Fatigue, weakness, pale skin, shortness of breath, dizziness, cold hands and feet",
         "ماندوویی، لاوازی، ڕەنگی پێستی کاڵ، تەنگی هەناسە، سەرگێژخواردن، دەست و قاچی سارد"),
        
        (1, "Leukemia", "لۆکیمیا",
         "Cancer of blood-forming tissues - abnormal white blood cells multiply uncontrollably",
         "شێرپەنجەی شانەکانی دروستکەری خوێن - خانە سپییە نائاساییەکان بە شێوەیەکی کۆنترۆڵنەکراو زیاد دەبن",
         "Fever, fatigue, frequent infections, weight loss, swollen lymph nodes, easy bleeding",
         "تا، ماندوویی، هەوکردنی دووبارە، دابەزینی کێش، ئاوسانی لووەکان، خوێنبەربوونی ئاسان"),
        
        (2, "Urinary Tract Infection", "هەوکردنی میزەڕۆ",
         "Bacterial infection of urinary system - most commonly caused by E. coli",
         "هەوکردنی بەکتریایی سیستەمی میز - زۆربەی کات بەهۆی E. coli دروست دەبێت",
         "Burning urination, frequent urination, cloudy urine, pelvic pain, strong-smelling urine",
         "سووتان لە کاتی میزکردندا، میزکردنی زۆر، میزی شێواو، ئازاری لەگەنە، میزی بۆن بەهێز"),
        
        (3, "Diabetes Mellitus", "شەکرە",
         "High blood sugar levels - body cannot properly use insulin",
         "ئاستی بەرزی شەکری خوێن - لەش ناتوانێت بە باشی ئینسولین بەکاربهێنێت",
         "Increased thirst, frequent urination, fatigue, blurred vision, slow healing wounds",
         "تینوێتی زۆر، میزکردنی زۆر، ماندوویی، بینینی شێواو، برینی درەنگ چاکبووەوە"),
        
        (3, "Kidney Disease", "نەخۆشی گورچیلە",
         "Impaired kidney function - kidneys cannot filter waste properly",
         "تێکچوونی کاری گورچیلە - گورچیلەکان ناتوانن بە باشی ماددە بەفیڕۆدراوەکان پاڵێو بکەن",
         "Swelling, fatigue, changes in urination, nausea, shortness of breath, high blood pressure",
         "ئاوسان، ماندوویی، گۆڕانکاری لە میزکردندا، هێڵنج، تەنگی هەناسە، پەستانی خوێنی بەرز"),
        
        (5, "Malaria", "مەلاریا",
         "Parasitic infection transmitted by mosquitoes - caused by Plasmodium parasites",
         "هەوکردنی مشقوڕخوەیی کە بە مێشوولە دەگوازرێتەوە - بەهۆی مشقوڕخوەکانی پلاسمۆدیەم دروست دەبێت",
         "Fever, chills, headache, muscle pain, fatigue, nausea, sweating",
         "تا، لەرز، سەرئێشە، ئازاری ماسولکە، ماندوویی، هێڵنج، ئارەقەکردن"),
    ]
    
    conn.executemany("""
        INSERT INTO diseases 
        (category_id, name_en, name_ku, description_en, description_ku, symptoms_en, symptoms_ku)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, diseases)
    
    # Practical Tests with complete details
    practicals = [
        ("Blood Smear Preparation and Staining", "ئامادەکردن و ڕەنگکردنی سمێری خوێن",
         "Learn to prepare, fix, and stain peripheral blood smears for microscopic examination",
         "فێربوونی ئامادەکردن، جێگیرکردن و ڕەنگکردنی سمێری خوێنی چواردەوری بۆ پشکنینی مایکرۆسکۆپی",
         "Hematology",
         "1. Clean glass slide with alcohol and let dry\n2. Place a small drop of blood (about 2-3mm) near one end of the slide\n3. Hold spreader slide at 30-45 degree angle in front of the blood drop\n4. Pull spreader back into the blood drop and let it spread along the edge\n5. Push spreader forward with a smooth, rapid motion to create a feathered edge\n6. Allow the smear to air dry completely (about 5-10 minutes)\n7. Fix the smear by dipping in absolute methanol for 2-3 minutes\n8. Allow methanol to evaporate\n9. Stain with Wright-Giemsa stain for 3-5 minutes\n10. Add buffer solution and wait 10-15 minutes\n11. Rinse gently with distilled water\n12. Allow to dry and examine under microscope",
         "١. پاکردنەوەی سلایدی شووشەیی بە ئەلکحول و ڕێگەدان بە وشکبوونەوە\n٢. دانانی دڵۆپێکی بچووکی خوێن (نزیکەی ٢-٣ملم) لە نزیک لێواری سلایدەکە\n٣. ڕاگرتنی سلایدی بڵاوکەرەوە بە گۆشەی ٣٠-٤٥ پلە لە بەردەم دڵۆپەکە\n٤. ڕاکێشانی بڵاوکەرەوەکە بۆ ناو دڵۆپەکە و ڕێگەدان بە بڵاوبوونەوە بە درێژایی لێوارەکە\n٥. پاڵنانی بڵاوکەرەوەکە بە جوڵەیەکی خێرا و نەرم بۆ دروستکردنی لێوارێکی پەڕیشی\n٦. ڕێگەدان بە سمێرەکە بۆ وشکبوونەوەی تەواو (نزیکەی ٥-١٠ خولەک)\n٧. جێگیرکردنی سمێرەکە بە نوقمکردن لە میسانۆلی پەتی بۆ ماوەی ٢-٣ خولەک\n٨. ڕێگەدان بە میسانۆل بۆ بەهەڵم بوون\n٩. ڕەنگکردن بە ڕەنگی رایت-گیمسا بۆ ٣-٥ خولەک\n١٠. زیادکردنی گیراوەی بەفەر و چاوەڕوانی ١٠-١٥ خولەک\n١١. شۆردن بە ئاوی مونەققە بە نەرمی\n١٢. ڕێگەدان بە وشکبوونەوە و پشکنین لەژێر مایکرۆسکۆپ",
         "Clean glass slides, sterile lancet, blood sample, Wright-Giemsa stain, absolute methanol, buffer solution, distilled water, microscope, gloves",
         "سلایدی شووشەیی پاک، لانسێتی ستێرایل، نموونەی خوێن، ڕەنگی رایت-گیمسا، میسانۆلی پەتی، گیراوەی بەفەر، ئاوی مونەققە، مایکرۆسکۆپ، دەستکێش",
         "A well-prepared smear shows a monolayer of cells with a smooth feathered edge. Red cells appear pink-red, white cells show purple nuclei with visible cytoplasmic granules, and platelets appear as small purple fragments",
         "سمێرێکی باش ئامادەکراو توێژاڵێکی یەک خانەیی پیشان دەدات لەگەڵ لێوارێکی پەڕیشی نەرم. خانە سوورەکان پەمەیی-سوور دەردەکەون، خانە سپییەکان ناوکی وەنەوشەیی پیشان دەدەن لەگەڵ دەنکۆڵەکانی ناوەخۆیی دیار، و پلەیکلتەکان وەک پارچەی وەنەوشەیی بچووک دەردەکەون",
         "Examine for RBC morphology (size, shape, color), WBC differential count, platelet estimate, and presence of parasites or abnormal cells. Abnormal findings may indicate anemia, infection, leukemia, or parasitic diseases",
         "پشکنین بۆ شێوەزانی خانە سوورەکان (قەبارە، شێوە، ڕەنگ)، ژماردنی جیاکاری خانە سپییەکان، خەمڵاندنی پلەیکلت، و بوونی مشقوڕخوەکان یان خانە نائاساییەکان. دۆزینەوە نائاساییەکان ڕەنگە نیشاندەری کەمخوێنی، هەوکردن، لۆکیمیا، یان نەخۆشی مشقوڕخوەیی بن",
         45, "Basic"),
        
        ("Gram Staining Technique", "تەکنیکی ڕەنگکردنی گرام",
         "Differential staining method to classify bacteria into Gram-positive and Gram-negative",
         "شێوازی ڕەنگکردنی جیاکارانە بۆ پۆلێنکردنی بەکتریا بۆ گرام-پۆزەتیڤ و گرام-نیگەتیڤ",
         "Microbiology",
         "1. Prepare a thin bacterial smear on a clean glass slide\n2. Allow to air dry completely\n3. Heat fix by passing slide through flame 3-4 times\n4. Cover smear with Crystal Violet for 1 minute\n5. Wash gently with water\n6. Cover with Gram's Iodine for 1 minute\n7. Wash gently with water\n8. Decolorize with 95% alcohol or acetone drop by drop until no more color runs off (about 10-15 seconds)\n9. Wash immediately with water\n10. Counterstain with Safranin for 30-45 seconds\n11. Wash gently with water\n12. Blot dry with filter paper and examine under oil immersion (100x)",
         "١. ئامادەکردنی سمێرێکی باریکی بەکتریایی لەسەر سلایدێکی شووشەیی پاک\n٢. ڕێگەدان بە وشکبوونەوەی تەواو\n٣. جێگیرکردنی گەرمی بە تێپەڕاندنی سلایدەکە بەسەر بڵێسەدا ٣-٤ جار\n٤. داپۆشینی سمێرەکە بە کریستاڵ ڤایۆلێت بۆ ١ خولەک\n٥. شۆردن بە ئاو بە نەرمی\n٦. داپۆشین بە ئایۆدینی گرام بۆ ١ خولەک\n٧. شۆردن بە ئاو بە نەرمی\n٨. ڕەنگ لابردن بە ئەلکحولی ٩٥٪ یان ئەسیتۆن دڵۆپە بە دڵۆپە تا چیتر ڕەنگ دانەپەڕێت (نزیکەی ١٠-١٥ چرکە)\n٩. دەستبەجێ شۆردن بە ئاو\n١٠. ڕەنگکردنی پێچەوانە بە سەفرانین بۆ ٣٠-٤٥ چرکە\n١١. شۆردن بە ئاو بە نەرمی\n١٢. وشککردن بە کاغەزی پاڵێوەر و پشکنین لەژێر زەیتی ئیمێرژن (١٠٠x)",
         "Bacterial culture, clean slides, Crystal Violet, Gram's Iodine, 95% alcohol or acetone, Safranin, water, filter paper, microscope with oil immersion",
         "کشتوکاڵی بەکتریایی، سلایدی پاک، کریستاڵ ڤایۆلێت، ئایۆدینی گرام، ئەلکحولی ٩٥٪ یان ئەسیتۆن، سەفرانین، ئاو، کاغەزی پاڵێوەر، مایکرۆسکۆپ لەگەڵ زەیتی ئیمێرژن",
         "Gram-positive bacteria appear purple/blue due to thick peptidoglycan layer retaining crystal violet. Gram-negative bacteria appear pink/red because they lose the primary stain and take up safranin counterstain",
         "بەکتریای گرام-پۆزەتیڤ وەنەوشەیی/شین دەردەکەوێت بەهۆی توێژاڵی ئەستووری پێپتیدۆگلایکان کە کریستاڵ ڤایۆلێت دەپارێزێت. بەکتریای گرام-نیگەتیڤ پەمەیی/سوور دەردەکەوێت چونکە ڕەنگی سەرەکی لەدەست دەدات و ڕەنگی پێچەوانەی سەفرانین وەردەگرێت",
         "Gram-positive (purple) indicates bacteria with thick peptidoglycan cell wall (e.g., Staphylococcus, Streptococcus). Gram-negative (pink) indicates bacteria with thin peptidoglycan and outer membrane (e.g., E. coli, Pseudomonas). This helps guide antibiotic therapy selection",
         "گرام-پۆزەتیڤ (وەنەوشەیی) نیشاندەری بەکتریایە لەگەڵ دیواری خانەیی پێپتیدۆگلایکانی ئەستوور (بۆ نموونە، ستافیلۆکۆکۆس، سترێپتۆکۆکۆس). گرام-نیگەتیڤ (پەمەیی) نیشاندەری بەکتریایە لەگەڵ پێپتیدۆگلایکانی باریک و پەردەی دەرەکی (بۆ نموونە، E. coli، سیودۆمۆناس). ئەمە یارمەتی هەڵبژاردنی چارەسەری ئانتی بایۆتیک دەدات",
         60, "Basic"),
        
        ("Urinalysis Using Dipstick Method", "شیکردنەوەی میز بە شێوازی دیپستیک",
         "Chemical analysis of urine using reagent strip to detect multiple parameters",
         "شیکردنەوەی کیمیایی میز بە بەکارهێنانی شریتی کاردانەوە بۆ دۆزینەوەی چەندین پارامێتەر",
         "Urinalysis",
         "1. Collect fresh midstream urine sample in a clean container\n2. Label the container with patient information\n3. Remove one dipstick from container and close immediately\n4. Dip the strip completely into urine for 1-2 seconds\n5. Remove excess urine by running the edge against container rim\n6. Hold strip horizontally to prevent mixing of reagents\n7. Read glucose and bilirubin at 30 seconds\n8. Read ketones at 40 seconds\n9. Read specific gravity at 45 seconds\n10. Read pH, protein, urobilinogen, blood, and nitrite at 60 seconds\n11. Read leukocytes at 2 minutes\n12. Compare each pad color to the color chart on container\n13. Record all results immediately",
         "١. کۆکردنەوەی نموونەی میزی ناوەڕاستی تازە لە دەفرێکی پاکدا\n٢. ناونیشانکردنی دەفرەکە بە زانیاری نەخۆش\n٣. دەرهێنانی یەک دیپستیک لە دەفرەکە و داخستنی دەستبەجێ\n٤. نوقمکردنی شریتەکە بە تەواوی لە میزدا بۆ ١-٢ چرکە\n٥. لابردنی میزی زیادە بە ڕاکێشانی لێوارەکە بەسەر لێواری دەفرەکەدا\n٦. ڕاگرتنی شریتەکە بە شێوەی ئاسۆیی بۆ ڕێگریکردن لە تێکەڵبوونی کاردانەوەکان\n٧. خوێندنەوەی گلوکۆز و بیلیروبین لە ٣٠ چرکەدا\n٨. خوێندنەوەی کیتۆنەکان لە ٤٠ چرکەدا\n٩. خوێندنەوەی چڕی تایبەت لە ٤٥ چرکەدا\n١٠. خوێندنەوەی pH، پڕۆتین، یورۆبیلینۆجین، خوێن، و نایترایت لە ٦٠ چرکەدا\n١١. خوێندنەوەی لۆکۆسایتەکان لە ٢ خولەکدا\n١٢. بەراوردکردنی ڕەنگی هەر پەدێک لەگەڵ هێڵکاری ڕەنگی سەر دەفرەکە\n١٣. تۆمارکردنی هەموو ئەنجامەکان دەستبەجێ",
         "Fresh urine sample, dipstick test strips, timer or watch, paper towels, gloves, color chart",
         "نموونەی میزی تازە، شریتی پشکنینی دیپستیک، کاتژمێر، کلنسی کاغەزی، دەستکێش، هێڵکاری ڕەنگ",
         "Normal urine: pH 5-7, specific gravity 1.005-1.030, negative for glucose, protein, blood, ketones, bilirubin, urobilinogen, nitrite, leukocytes. Abnormal findings require further investigation",
         "میزی ئاسایی: pH ٥-٧، چڕی تایبەت ١.٠٠٥-١.٠٣٠، نەرێنی بۆ گلوکۆز، پڕۆتین، خوێن، کیتۆنەکان، بیلیروبین، یورۆبیلینۆجین، نایترایت، لۆکۆسایتەکان. دۆزینەوە نائاساییەکان پێویستیان بە لێکۆڵینەوەی زیاترە",
         "Positive glucose may indicate diabetes. Positive protein suggests kidney disease. Positive blood may indicate infection, stones, or tumor. Positive nitrite and leukocytes suggest UTI. Positive ketones may indicate diabetic ketoacidosis or starvation. Positive bilirubin suggests liver disease",
         "گلوکۆزی پۆزەتیڤ ڕەنگە نیشاندەری شەکرە بێت. پڕۆتینی پۆزەتیڤ ئاماژە بە نەخۆشی گورچیلە دەکات. خوێنی پۆزەتیڤ ڕەنگە نیشاندەری هەوکردن، بەرد، یان وەرەم بێت. نایترایت و لۆکۆسایتی پۆزەتیڤ ئاماژە بە هەوکردنی میزەڕۆ دەکات. کیتۆنی پۆزەتیڤ ڕەنگە نیشاندەری کیتۆئەسیدۆزی شەکرەیی یان برسیێتی بێت. بیلیروبینی پۆزەتیڤ ئاماژە بە نەخۆشی جگەر دەکات",
         30, "Basic"),
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

# Initialize database and insert data
conn = get_connection()
insert_initial_data(conn)

# ==================== Helper Functions ====================
def t(key):
    """Get translation"""
    translations = {
        "English 🇬🇧": {
            "app_title": "Medical Laboratory Analysis System",
            "app_subtitle": "Fourth Stage - Disease Analysis",
            "student_name": "Danyal Ismail",
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
            "quick_info": "Quick Info",
            "quick_info_text": "Comprehensive medical laboratory reference for 4th stage students",
            "disease_categories": "Disease Categories",
            "laboratory_tests": "Laboratory Tests",
            "diseases": "Diseases",
            "practical_tests": "Practical Tests",
            "categories_overview": "Disease Categories",
            "filter_category": "Filter by Category",
            "all_categories": "All Categories",
            "search": "Search",
            "search_diseases": "Search Diseases",
            "description": "Description",
            "symptoms": "Symptoms",
            "category": "Category",
            "test_category": "Test Category",
            "search_tests": "Search Tests",
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
            "difficulty": "Difficulty",
            "add_notes": "Add Study Notes",
            "topic": "Topic",
            "content": "Note Content",
            "save_note": "Save Note",
            "your_notes": "Your Study Notes",
            "delete": "Delete",
            "patient_name": "Patient Name",
            "patient_age": "Patient Age",
            "patient_gender": "Patient Gender",
            "select_test": "Select Test",
            "result_value": "Result Value",
            "result_text": "Result Text",
            "additional_notes": "Additional Notes",
            "save_result": "Save Result",
            "total_tests": "Total Tests",
            "abnormal_results": "Abnormal Results",
            "normal_rate": "Normal Rate",
            "tests_by_category": "Tests by Category",
            "normal_vs_abnormal": "Normal vs Abnormal",
            "recent_results": "Recent Results",
            "no_results": "No test results recorded yet",
            "abnormal_warning": "Abnormal result detected",
            "saved_success": "Saved successfully",
            "note_saved": "Note saved",
            "minutes": "minutes",
            "basic": "Basic",
            "intermediate": "Intermediate",
            "advanced": "Advanced",
            "gender_male": "Male",
            "gender_female": "Female",
            "created": "Created",
            "no_diseases_found": "No diseases found",
            "no_notes_yet": "No notes yet",
            "write_topic_content": "Please write topic and content",
            "write_patient_name": "Please write patient name",
            "ask_question": "Ask me anything about laboratory tests...",
            "ai_response": "AI Response",
            "type_question": "Type your question here...",
        },
        "کوردی 🇹🇯": {
            "app_title": "سیستەمی شیکردنەوەی تاقیگەی پزیشکی",
            "app_subtitle": "قۆناغی چوارەم - شیکردنەوەی نەخۆشییەکان",
            "student_name": "دانیال ئیسماعیل",
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
            "quick_info": "زانیاری",
            "quick_info_text": "سەرچاوەیەکی تەواوی تاقیگەیی بۆ قوتابیانی قۆناغی چوارەم",
            "disease_categories": "بەشەکانی نەخۆشی",
            "laboratory_tests": "پشکنینە تاقیگەییەکان",
            "diseases": "نەخۆشییەکان",
            "practical_tests": "پشکنینی پراکتیکی",
            "categories_overview": "بەشەکانی نەخۆشییەکان",
            "filter_category": "پاڵێوکردن بەپێی بەش",
            "all_categories": "هەموو بەشەکان",
            "search": "گەڕان",
            "search_diseases": "گەڕان بەدوای نەخۆشییەکان",
            "description": "ڕوونکردنەوە",
            "symptoms": "نیشانەکان",
            "category": "بەش",
            "test_category": "بەشی پشکنین",
            "search_tests": "گەڕان بەدوای پشکنینەکان",
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
            "difficulty": "ئاستی قورسی",
            "add_notes": "زیادکردنی تێبینی",
            "topic": "بابەت",
            "content": "ناوەڕۆکی تێبینی",
            "save_note": "تۆمارکردنی تێبینی",
            "your_notes": "تێبینییەکانت",
            "delete": "سڕینەوە",
            "patient_name": "ناوی نەخۆش",
            "patient_age": "تەمەنی نەخۆش",
            "patient_gender": "ڕەگەزی نەخۆش",
            "select_test": "پشکنین هەڵبژێرە",
            "result_value": "بەهای ئەنجام",
            "result_text": "دەقی ئەنجام",
            "additional_notes": "تێبینی زیادە",
            "save_result": "تۆمارکردنی ئەنجام",
            "total_tests": "کۆی گشتی",
            "abnormal_results": "نائاسایی",
            "normal_rate": "ڕێژەی ئاسایی",
            "tests_by_category": "پشکنینەکان بەپێی بەش",
            "normal_vs_abnormal": "ئاسایی بەرامبەر نائاسایی",
            "recent_results": "دوایین ئەنجامەکان",
            "no_results": "هێشتا هیچ ئەنجامێک تۆمار نەکراوە",
            "abnormal_warning": "ئەنجامی نائاسایی دۆزرایەوە",
            "saved_success": "بە سەرکەوتوویی تۆمارکرا",
            "note_saved": "تێبینییەکە تۆمارکرا",
            "minutes": "خولەک",
            "basic": "سەرەتایی",
            "intermediate": "ناوەندی",
            "advanced": "پێشکەوتوو",
            "gender_male": "نێر",
            "gender_female": "مێ",
            "created": "دروستکراوە",
            "no_diseases_found": "هیچ نەخۆشییەک نەدۆزرایەوە",
            "no_notes_yet": "هێشتا هیچ تێبینییەکت نییە",
            "write_topic_content": "تکایە بابەت و ناوەڕۆک بنووسە",
            "write_patient_name": "تکایە ناوی نەخۆش بنووسە",
            "ask_question": "هەر پرسیارێکی تاقیگەییت هەیە لێم بپرسە...",
            "ai_response": "وەڵامی زیرەک",
            "type_question": "پرسیارەکەت لێرە بنووسە...",
        }
    }
    
    lang = st.session_state.get('language', 'کوردی 🇹🇯')
    return translations.get(lang, translations['کوردی 🇹🇯']).get(key, key)

def get_name(row, prefix="name"):
    """Get localized name"""
    lang_map = {"English 🇬🇧": "en", "کوردی 🇹🇯": "ku"}
    lang = lang_map.get(st.session_state.get('language', 'کوردی 🇹🇯'), 'ku')
    field = f"{prefix}_{lang}"
    result = dict(row) if not isinstance(row, dict) else row
    return result.get(field, result.get(f"{prefix}_en", ""))

def get_desc(row):
    """Get localized description"""
    return get_name(row, "description")

# ==================== Main App ====================
def main():
    # Initialize language
    if 'language' not in st.session_state:
        st.session_state.language = 'کوردی 🇹🇯'
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"## 🔬 {t('nav_title')}")
        
        # Language selector with Kurdistan flag
        language = st.selectbox(
            t('language'),
            ["کوردی 🇹🇯", "English 🇬🇧"],
            key="lang_sel"
        )
        if language != st.session_state.language:
            st.session_state.language = language
            st.rerun()
        
        st.markdown("---")
        
        page = st.radio(
            t('select_section'),
            [t('dashboard'), t('disease_db'), t('lab_tests'), 
             t('practical'), t('theory'), t('results_entry'),
             t('reports'), t('ai_chat')],
            key="page_sel"
        )
        
        st.markdown("---")
        st.markdown(f"### 📋 {t('quick_info')}")
        st.info(t('quick_info_text'))
    
    # Student info header
    st.markdown(f"""
    <div class="student-info">
        <h2>🎓 {t('welcome')}، {t('student_name')}</h2>
        <p>{t('app_subtitle')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Route pages
    if page == t('dashboard'):
        render_dashboard()
    elif page == t('disease_db'):
        render_diseases()
    elif page == t('lab_tests'):
        render_tests()
    elif page == t('practical'):
        render_practical()
    elif page == t('theory'):
        render_notes()
    elif page == t('results_entry'):
        render_results()
    elif page == t('reports'):
        render_reports()
    elif page == t('ai_chat'):
        render_ai_chat()

def render_dashboard():
    """Dashboard page"""
    st.markdown(f"## {t('dashboard')}")
    
    # Stats
    cats = conn.execute("SELECT COUNT(*) as c FROM disease_categories").fetchone()['c']
    tests = conn.execute("SELECT COUNT(*) as c FROM test_types").fetchone()['c']
    diseases = conn.execute("SELECT COUNT(*) as c FROM diseases").fetchone()['c']
    practicals = conn.execute("SELECT COUNT(*) as c FROM practical_tests").fetchone()['c']
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(t('disease_categories'), cats)
    c2.metric(t('laboratory_tests'), tests)
    c3.metric(t('diseases'), diseases)
    c4.metric(t('practical_tests'), practicals)
    
    st.markdown(f"## {t('categories_overview')}")
    categories = conn.execute("SELECT * FROM disease_categories").fetchall()
    
    cols = st.columns(2)
    for i, cat in enumerate(categories):
        with cols[i % 2]:
            st.markdown(f"""
            <div class="category-card">
                <h3>{cat['icon']} {get_name(cat)}</h3>
                <p>{get_desc(cat)}</p>
            </div>
            """, unsafe_allow_html=True)

def render_diseases():
    """Disease database"""
    st.markdown(f"## {t('disease_db')}")
    
    # Categories filter
    categories = conn.execute("SELECT * FROM disease_categories").fetchall()
    cat_options = {t('all_categories'): None}
    for cat in categories:
        cat_options[get_name(cat)] = cat['id']
    
    selected = st.selectbox(t('filter_category'), list(cat_options.keys()))
    cat_id = cat_options[selected]
    
    # Get diseases
    if cat_id:
        diseases = conn.execute("""
            SELECT d.*, dc.name_en as cat_en, dc.name_ku as cat_ku
            FROM diseases d 
            JOIN disease_categories dc ON d.category_id = dc.id
            WHERE d.category_id = ?
        """, (cat_id,)).fetchall()
    else:
        diseases = conn.execute("""
            SELECT d.*, dc.name_en as cat_en, dc.name_ku as cat_ku
            FROM diseases d 
            JOIN disease_categories dc ON d.category_id = dc.id
        """).fetchall()
    
    # Search
    search = st.text_input(t('search_diseases'))
    if search:
        diseases = [d for d in diseases if search.lower() in get_name(d).lower()]
    
    if not diseases:
        st.info(t('no_diseases_found'))
        return
    
    # Display diseases
    for disease in diseases:
        with st.expander(f"🦠 {get_name(disease)} - {get_name(disease, 'cat')}"):
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"### {t('description')}")
                st.write(get_desc(disease))
                
                st.markdown(f"### {t('symptoms')}")
                symptoms = get_name(disease, 'symptoms').split(',')
                for s in symptoms:
                    if s.strip():
                        st.markdown(f"<span class='symptom-tag'>{s.strip()}</span>", unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"**{t('category')}:** {get_name(disease, 'cat')}")

def render_tests():
    """Laboratory tests"""
    st.markdown(f"## {t('lab_tests')}")
    
    col1, col2 = st.columns(2)
    with col1:
        cats = conn.execute("SELECT DISTINCT category FROM test_types").fetchall()
        cat_list = [t('all_categories')] + [c['category'] for c in cats]
        selected = st.selectbox(t('test_category'), cat_list)
    with col2:
        search = st.text_input(t('search_tests'))
    
    tests = conn.execute("SELECT * FROM test_types").fetchall()
    
    if selected != t('all_categories'):
        tests = [t for t in tests if t['category'] == selected]
    
    if search:
        tests = [t for t in tests if search.lower() in get_name(t).lower()]
    
    # Group tests
    sorted_tests = sorted(tests, key=lambda x: x['category'])
    
    for category, group in groupby(sorted_tests, key=lambda x: x['category']):
        st.markdown(f"### 📁 {category}")
        
        for test in group:
            with st.expander(f"📊 {get_name(test)}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                    <div class="info-box">
                        <p><strong>{t('unit')}:</strong> {test['unit']}</p>
                        <p><strong class="normal-range">{t('normal_range')}: {test['normal_range_low']} - {test['normal_range_high']}</strong></p>
                        <p><strong>{t('description')}:</strong> {get_desc(test)}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="warning-box">
                        <h4>{t('critical_values')}</h4>
                        <p>{t('low')}: <span class="critical-range">< {test['critical_low']}</span></p>
                        <p>{t('high')}: <span class="critical-range">> {test['critical_high']}</span></p>
                    </div>
                    """, unsafe_allow_html=True)

def render_practical():
    """Practical tests"""
    st.markdown(f"## {t('practical')}")
    
    col1, col2 = st.columns(2)
    with col1:
        cats = conn.execute("SELECT DISTINCT category FROM practical_tests").fetchall()
        cat_list = [t('all_categories')] + [c['category'] for c in cats]
        selected = st.selectbox(t('filter_category'), cat_list)
    with col2:
        difficulty = st.selectbox(t('difficulty'), [t('all_categories'), t('basic'), t('intermediate'), t('advanced')])
    
    practicals = conn.execute("SELECT * FROM practical_tests").fetchall()
    
    if selected != t('all_categories'):
        practicals = [p for p in practicals if p['category'] == selected]
    
    if difficulty != t('all_categories'):
        diff_map = {t('basic'): 'Basic', t('intermediate'): 'Intermediate', t('advanced'): 'Advanced'}
        practicals = [p for p in practicals if p['difficulty_level'] == diff_map.get(difficulty)]
    
    for test in practicals:
        with st.expander(f"🔬 {get_name(test, 'title')} ({test['duration_minutes']} {t('minutes')})"):
            st.markdown(f"### {t('description')}")
            st.write(get_desc(test))
            
            st.markdown(f"### {t('procedure')}")
            steps = get_name(test, 'steps').split('\n')
            for i, step in enumerate(steps):
                if step.strip():
                    st.markdown(f"<p><span class='step-number'>{i+1}</span> {step.strip()}</p>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"### {t('materials')}")
                for m in get_name(test, 'materials').split(','):
                    if m.strip():
                        st.markdown(f"- {m.strip()}")
            with col2:
                st.markdown(f"### {t('expected_results')}")
                st.info(get_name(test, 'expected_results'))
            
            st.markdown(f"### {t('interpretation')}")
            st.success(get_name(test, 'interpretation'))

def render_notes():
    """Study notes"""
    st.markdown(f"## {t('theory')}")
    
    with st.expander(t('add_notes'), expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            topic = st.text_input(t('topic'))
            category = st.selectbox(t('category'), ["Hematology", "Microbiology", "Clinical Chemistry", "Immunology", "Parasitology", "Urinalysis"])
        with col2:
            content = st.text_area(t('content'), height=150)
        
        if st.button(t('save_note'), use_container_width=True):
            if topic and content:
                conn.execute("INSERT INTO study_notes (topic, content, category) VALUES (?, ?, ?)", (topic, content, category))
                conn.commit()
                st.success(t('note_saved'))
                st.rerun()
            else:
                st.warning(t('write_topic_content'))
    
    st.markdown(f"### {t('your_notes')}")
    notes = conn.execute("SELECT * FROM study_notes ORDER BY created_at DESC").fetchall()
    
    if not notes:
        st.info(t('no_notes_yet'))
    else:
        for note in notes:
            with st.expander(f"📝 {note['topic']} - {note['category']}"):
                st.write(note['content'])
                st.caption(f"{t('created')}: {note['created_at']}")
                if st.button(t('delete'), key=f"del_{note['id']}"):
                    conn.execute("DELETE FROM study_notes WHERE id = ?", (note['id'],))
                    conn.commit()
                    st.rerun()

def render_results():
    """Test results entry"""
    st.markdown(f"## {t('results_entry')}")
    
    with st.form("results_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            name = st.text_input(t('patient_name'))
            age = st.number_input(t('patient_age'), 0, 120, 30)
        with c2:
            gender = st.selectbox(t('patient_gender'), [t('gender_male'), t('gender_female')])
            all_tests = conn.execute("SELECT * FROM test_types").fetchall()
            test_opts = {get_name(t): t['id'] for t in all_tests}
            selected_test = st.selectbox(t('select_test'), list(test_opts.keys()))
        with c3:
            value = st.number_input(t('result_value'), step=0.01)
            text = st.text_input(t('result_text'))
        
        notes = st.text_area(t('additional_notes'))
        
        if st.form_submit_button(t('save_result'), use_container_width=True):
            if not name:
                st.error(t('write_patient_name'))
            else:
                tid = test_opts[selected_test]
                test = conn.execute("SELECT * FROM test_types WHERE id = ?", (tid,)).fetchone()
                abnormal = value < test['normal_range_low'] or value > test['normal_range_high']
                
                conn.execute("""
                    INSERT INTO test_results (patient_name, patient_age, patient_gender, test_id, result_value, result_text, is_abnormal, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (name, age, gender, tid, value, text, abnormal, notes))
                conn.commit()
                
                st.success(t('saved_success'))
                if abnormal:
                    st.warning(t('abnormal_warning'))

def render_reports():
    """Reports"""
    st.markdown(f"## {t('reports')}")
    
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
    df['test_name'] = df.apply(lambda r: get_name(r, 't'), axis=1)
    
    c1, c2, c3 = st.columns(3)
    c1.metric(t('total_tests'), len(df))
    abnormal = len(df[df['is_abnormal'] == True])
    c2.metric(t('abnormal_results'), abnormal)
    c3.metric(t('normal_rate'), f"{((len(df) - abnormal) / len(df)) * 100:.1f}%")
    
    col1, col2 = st.columns(2)
    with col1:
        cat_counts = df['category'].value_counts()
        if len(cat_counts) > 0:
            fig = px.pie(values=cat_counts.values, names=cat_counts.index, title=t('tests_by_category'))
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if len(df) > 0:
            status_df = pd.DataFrame({'حاڵەت': ['ئاسایی', 'نائاسایی'], 'ژمارە': [len(df[df['is_abnormal'] == False]), len(df[df['is_abnormal'] == True])]})
            fig = px.bar(status_df, x='حاڵەت', y='ژمارە', title=t('normal_vs_abnormal'), color='حاڵەت', color_discrete_map={'ئاسایی': '#2e7d32', 'نائاسایی': '#c62828'})
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown(f"### {t('recent_results')}")
    st.dataframe(df[['patient_name', 'test_name', 'result_value', 'is_abnormal', 'date_performed']], use_container_width=True)

def render_ai_chat():
    """AI Chat Assistant"""
    st.markdown(f"## 🤖 {t('ai_chat')}")
    st.markdown(f"### {t('ask_question')}")
    
    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    for chat in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(chat['question'])
        with st.chat_message("assistant"):
            st.write(chat['answer'])
    
    # Question input
    question = st.chat_input(t('type_question'))
    
    if question:
        # Add to history
        st.session_state.chat_history.append({"question": question, "answer": ""})
        
        # Generate response based on database knowledge
        answer = generate_ai_response(question)
        st.session_state.chat_history[-1]['answer'] = answer
        st.rerun()

def generate_ai_response(question):
    """Generate AI response based on database"""
    q = question.lower()
    
    # Search tests
    tests = conn.execute("SELECT * FROM test_types").fetchall()
    for test in tests:
        if get_name(test).lower() in q or any(word in q for word in get_desc(test).lower().split()):
            return f"""
**{get_name(test)}**
- **{t('normal_range')}:** {test['normal_range_low']} - {test['normal_range_high']} {test['unit']}
- **{t('description')}:** {get_desc(test)}
- **{t('critical_values')}:** < {test['critical_low']} یا > {test['critical_high']}
            """
    
    # Search diseases
    diseases = conn.execute("SELECT d.*, dc.name_ku as cname FROM diseases d JOIN disease_categories dc ON d.category_id = dc.id").fetchall()
    for disease in diseases:
        if get_name(disease).lower() in q:
            return f"""
**{get_name(disease)}** - {disease['cname']}
- **{t('description')}:** {get_desc(disease)}
- **{t('symptoms')}:** {get_name(disease, 'symptoms')}
            """
    
    # Search practical tests
    practicals = conn.execute("SELECT * FROM practical_tests").fetchall()
    for prac in practicals:
        if get_name(prac, 'title').lower() in q or any(word in q for word in get_desc(prac).lower().split()[:5]):
            return f"""
**{get_name(prac, 'title')}**
- **{t('description')}:** {get_desc(prac)}
- **{t('procedure')}:** {get_name(prac, 'steps')[:200]}...
            """
    
    # Default response
    return f"""
**ببورە، نەمتوانی وەڵامی ڕاستەوخۆ بدۆزمەوە.**

تکایە پرسیار لەسەر:
- پشکنینە تاقیگەییەکان (وەک CBC، هیمۆگلۆبین، گلوکۆز)
- نەخۆشییەکان (وەک کەمخوێنی، شەکرە، هەوکردنی میزەڕۆ)
- پشکنینە پراکتیکییەکان (وەک ڕەنگکردنی گرام، شیکردنەوەی میز)

**یان دەتوانیت لە بەشەکانی تر بگەڕێیت!**
"""

if __name__ == "__main__":
    main()
