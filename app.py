# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import os
import google.generativeai as genai

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
    @import url('https://fonts.googleapis.com/css2?family=Noto+Kurdish:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Noto Kurdish', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
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
    }
    
    .info-box {
        background: #e3f2fd;
        padding: 15px;
        border-radius: 10px;
        border-right: 4px solid #1565c0;
        margin: 10px 0;
    }
    
    .stat-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .test-result-normal {
        background-color: #e8f5e9;
        padding: 10px;
        border-radius: 8px;
        border-right: 4px solid #4caf50;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# ==================== Database ====================

@st.cache_resource
def init_db():
    """Initialize database with correct schema"""
    try:
        conn = sqlite3.connect('medical_lab.db', check_same_thread=False, timeout=30)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.row_factory = sqlite3.Row
        
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS disease_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name_en TEXT NOT NULL UNIQUE,
            name_ku TEXT NOT NULL UNIQUE,
            description_en TEXT,
            description_ku TEXT,
            icon TEXT,
            color TEXT
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
            severity TEXT DEFAULT 'Moderate'
        );
        
        CREATE TABLE IF NOT EXISTS test_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name_en TEXT NOT NULL,
            name_ku TEXT NOT NULL,
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
            turnaround_time TEXT,
            price REAL
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
            difficulty_level TEXT
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
            patient_gender TEXT,
            test_id INTEGER NOT NULL,
            result_value REAL,
            is_abnormal INTEGER DEFAULT 0,
            is_critical INTEGER DEFAULT 0,
            notes TEXT,
            date_performed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        conn.commit()
        return conn
    except Exception as e:
        st.error(f"Database Error: {str(e)}")
        return None

conn = init_db()

# ==================== Insert Data ====================

def insert_all_data(conn):
    if conn is None:
        return
    
    try:
        cursor = conn.execute("SELECT COUNT(*) as cnt FROM test_types")
        if cursor.fetchone()['cnt'] > 0:
            return
        
        categories = [
            ("Hematology", "خوێنناسی", "Study of blood", "لێکۆڵینەوەی خوێن", "🩸", "#FF6B6B"),
            ("Clinical Chemistry", "کیمیای کلینیکی", "Chemical analysis", "شیکردنەوەی کیمیایی", "🧪", "#4ECDC4"),
            ("Microbiology", "مایکرۆبایۆلۆجی", "Study of microorganisms", "لێکۆڵینەوەی میکرۆب", "🔬", "#45B7D1"),
            ("Immunology", "بەرگری ناسی", "Immune system", "سیستەمی بەرگری", "🛡️", "#96CEB4"),
            ("Endocrinology", "هۆرمۆن ناسی", "Hormones study", "لێکۆڵینەوەی هۆرمۆنەکان", "⚡", "#FFEAA7"),
            ("Urinalysis", "شیکردنەوەی میز", "Urine analysis", "شیکردنەوەی میز", "💧", "#DDA0DD")
        ]
        conn.executemany("INSERT INTO disease_categories (name_en, name_ku, description_en, description_ku, icon, color) VALUES (?,?,?,?,?,?)", categories)
        
        diseases = [
            (1, "Iron Deficiency Anemia", "کەمخوێنی کەمی ئاسن", "Most common anemia", "باوباپترین کەمخوێنی", "Fatigue, Weakness, Pale skin", "ماندوویی، لاوازی، پێستی کاڵ", "Poor diet, Blood loss", "خواردنی خراپ، لەدەستدانی خوێن", "Iron supplements", "تەواوکەری ئاسن", "Moderate"),
            (1, "Thalassemia", "تالاسیمیا", "Genetic blood disorder", "نەخۆشی خوێنی بۆماوەیی", "Fatigue, Bone deformities", "ماندوویی، شێواوی ئێسک", "Genetic", "بۆماوەیی", "Blood transfusion", "گواستنەوەی خوێن", "Severe"),
            (2, "Diabetes Mellitus", "شەکرە", "High blood sugar", "شەکری بەرزی خوێن", "Frequent urination, Thirst", "میزی زۆر، تینوێتی", "Insulin resistance", "بەرگری ئینسولین", "Insulin, Diet", "ئینسولین، خواردن", "Severe")
        ]
        conn.executemany("INSERT INTO diseases (category_id, name_en, name_ku, description_en, description_ku, symptoms_en, symptoms_ku, causes_en, causes_ku, treatment_en, treatment_ku, severity) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", diseases)
        
        tests = [
            ("CBC", "ژمارەی تەواوی خوێن", "Hematology", "cells/μL", 4.5, 11.0, 2.0, 15.0, "Complete Blood Count", "ژمارەی تەواوی خوێن", "No preparation", "پێویستی نییە", "2 hours", 25.0),
            ("Hemoglobin", "هیمۆگلۆبین", "Hematology", "g/dL", 12.0, 16.0, 7.0, 20.0, "Measures hemoglobin", "پێوانی هیمۆگلۆبین", "No preparation", "پێویستی نییە", "1 hour", 15.0),
            ("Blood Glucose", "شەکری خوێن", "Clinical Chemistry", "mg/dL", 70, 100, 40, 300, "Blood sugar test", "پشکنینی شەکری خوێن", "Fast 8 hours", "بەڕۆژووبوونی ٨ کاتژمێر", "2 hours", 20.0),
            ("Cholesterol", "کۆلیستڕۆڵ", "Clinical Chemistry", "mg/dL", 125, 200, 100, 300, "Cholesterol test", "پشکنینی کۆلیستڕۆڵ", "Fast 12 hours", "بەڕۆژووبوونی ١٢ کاتژمێر", "3 hours", 35.0),
            ("CRP", "پڕۆتینی کاردەر", "Immunology", "mg/L", 0, 5, 0, 100, "Inflammation marker", "نیشانەکەری هەوکردن", "No preparation", "پێویستی نییە", "2 hours", 40.0),
            ("TSH", "هۆرمۆنی تایرۆید", "Endocrinology", "mIU/L", 0.4, 4.0, 0.1, 50.0, "Thyroid function", "کاری تایرۆید", "Morning sample", "نموونەی بەیانی", "3 hours", 60.0),
            ("Urine pH", "ترشێتی میز", "Urinalysis", "pH", 4.5, 8.0, 4.0, 9.0, "Urine acidity", "ترشێتی میز", "Fresh sample", "نموونەی تازە", "30 min", 10.0)
        ]
        conn.executemany("INSERT INTO test_types (name_en, name_ku, category, unit, normal_range_low, normal_range_high, critical_low, critical_high, description_en, description_ku, preparation_en, preparation_ku, turnaround_time, price) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", tests)
        
        practicals = [
            ("Blood Smear Preparation", "ئامادەکردنی سمێری خوێن", "Prepare blood smear", "ئامادەکردنی سمێری خوێن", "Hematology", 
             "1. Clean slide\n2. Place blood drop\n3. Spread blood\n4. Air dry\n5. Stain", 
             "١. سلاید پاک بکە\n٢. دڵۆپی خوێن دابنێ\n٣. خوێن بڵاو بکە\n٤. وشک بکە\n٥. ڕەنگ بکە",
             "Slide, Blood, Stain", "سلاید، خوێن، ڕەنگ", "Well spread blood cells", "خانەکانی خوێن بڵاون", "Check RBC morphology", "شێوەی خڕۆکە سوورەکان", "Avoid bubbles", "دووربە لە بڵق", 30, "Basic"),
            ("Gram Staining", "ڕەنگکردنی گرام", "Bacteria staining", "ڕەنگکردنی بەکتریا", "Microbiology",
             "1. Heat fix\n2. Crystal violet\n3. Iodine\n4. Decolorize\n5. Safranin",
             "١. جێگیر بکە بە گەرمی\n٢. کریستاڵ ڤایۆلێت\n٣. یۆد\n٤. ڕەنگ لێبەرە\n٥. سەفرانین",
             "Culture, Stains", "کەلتوور، ڕەنگەکان", "Purple = Gram+, Pink = Gram-", "وەنەوشەیی = پۆزەتیڤ، پەمەیی = نێگەتیڤ", "Bacteria ID", "ناسینەوەی بەکتریا", "Don't over-decolorize", "زۆر ڕەنگ لێمەبەرە", 45, "Intermediate"),
            ("Urine Dipstick", "دیپستیکی میز", "Urine analysis", "شیکردنەوەی میز", "Urinalysis",
             "1. Dip strip\n2. Wait\n3. Compare to chart", "١. شریت نقوم بکە\n٢. چاوەڕێ بکە\n٣. بەراورد بکە",
             "Strip, Urine, Chart", "شریت، میز، چارت", "Normal ranges", "مەودای ئاسایی", "Check for UTI", "پشکنینی هەوکردنی میز", "Use fresh sample", "نموونەی تازە بەکاربهێنە", 15, "Basic")
        ]
        conn.executemany("INSERT INTO practical_tests (title_en, title_ku, description_en, description_ku, category, steps_en, steps_ku, materials_en, materials_ku, expected_results_en, expected_results_ku, interpretation_en, interpretation_ku, precautions_en, precautions_ku, duration_minutes, difficulty_level) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", practicals)
        
        conn.commit()
    except Exception as e:
        st.error(f"Insert Error: {str(e)}")
        conn.rollback()

if conn:
    insert_all_data(conn)

# ==================== Translation ====================

def t(key):
    translations = {
        "کوردی 🇹🇯": {
            "dashboard": "📊 داشبۆرد", "disease_db": "🦠 نەخۆشییەکان", "lab_tests": "🧪 پشکنینەکان",
            "practical": "🔬 پراکتیکی", "theory": "📚 تێبینییەکان", "results_entry": "📝 ئەنجامەکان",
            "reports": "📈 ڕاپۆرت", "ai_chat": "🤖 زیرەکی دەستکرد", "search": "گەڕان...",
            "save": "تۆمارکردن", "delete": "سڕینەوە", "edit": "دەستکاری"
        },
        "English 🇬🇧": {
            "dashboard": "📊 Dashboard", "disease_db": "🦠 Disease Database", "lab_tests": "🧪 Lab Tests",
            "practical": "🔬 Practical", "theory": "📚 Study Notes", "results_entry": "📝 Results",
            "reports": "📈 Reports", "ai_chat": "🤖 AI Assistant", "search": "Search...",
            "save": "Save", "delete": "Delete", "edit": "Edit"
        }
    }
    lang = st.session_state.get("language", "کوردی 🇹🇯")
    return translations.get(lang, {}).get(key, key)

def get_name(row, prefix="name"):
    lang = st.session_state.get("language", "کوردی 🇹🇯")
    suffix = "ku" if lang == "کوردی 🇹🇯" else "en"
    field = f"{prefix}_{suffix}"
    
    if isinstance(row, dict):
        return row.get(field, row.get(f"{prefix}_en", "N/A"))
    try:
        return row[field]
    except:
        return "N/A"

def get_desc(row):
    return get_name(row, "description")

# ==================== AI ====================

def get_ai_response(question):
    try:
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if api_key:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-pro")
            response = model.generate_content(f"You are a medical lab expert. Answer: {question}")
            return response.text
    except:
        pass
    
    q = question.lower()
    if "cbc" in q:
        return "CBC measures red/white blood cells and platelets. Normal ranges vary by age/gender."
    elif "glucose" in q:
        return "Normal fasting glucose: 70-100 mg/dL. Above 126 indicates diabetes."
    else:
        return "I can help with medical lab questions about CBC, glucose, cholesterol, diseases, and test procedures."

# ==================== Dashboard ====================

def render_dashboard():
    st.markdown(f"<div class='main-header'><h1>{t('dashboard')}</h1></div>", unsafe_allow_html=True)
    
    if conn is None:
        st.error("Database not connected")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        cursor = conn.execute("SELECT COUNT(*) as c FROM disease_categories")
        cat_count = cursor.fetchone()['c']
        st.markdown(f"<div class='stat-card'><h2>{cat_count}</h2><p>📂 Categories</p></div>", unsafe_allow_html=True)
    with col2:
        cursor = conn.execute("SELECT COUNT(*) as c FROM test_types")
        test_count = cursor.fetchone()['c']
        st.markdown(f"<div class='stat-card'><h2>{test_count}</h2><p>🧪 Tests</p></div>", unsafe_allow_html=True)
    with col3:
        cursor = conn.execute("SELECT COUNT(*) as c FROM diseases")
        disease_count = cursor.fetchone()['c']
        st.markdown(f"<div class='stat-card'><h2>{disease_count}</h2><p>🦠 Diseases</p></div>", unsafe_allow_html=True)
    with col4:
        cursor = conn.execute("SELECT COUNT(*) as c FROM practical_tests")
        practical_count = cursor.fetchone()['c']
        st.markdown(f"<div class='stat-card'><h2>{practical_count}</h2><p>🔬 Practical</p></div>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.info("👈 Select a page from the sidebar to get started")

# ==================== Diseases ====================

def render_diseases():
    st.markdown(f"<div class='main-header'><h1>{t('disease_db')}</h1></div>", unsafe_allow_html=True)
    
    if conn is None:
        return
    
    search = st.text_input(t('search'), placeholder="Search diseases...")
    
    if search:
        diseases = conn.execute("""
            SELECT d.*, dc.name_en as cat_en, dc.name_ku as cat_ku, dc.icon 
            FROM diseases d 
            JOIN disease_categories dc ON d.category_id = dc.id
            WHERE d.name_en LIKE ? OR d.name_ku LIKE ?
        """, (f"%{search}%", f"%{search}%")).fetchall()
    else:
        diseases = conn.execute("""
            SELECT d.*, dc.name_en as cat_en, dc.name_ku as cat_ku, dc.icon 
            FROM diseases d 
            JOIN disease_categories dc ON d.category_id = dc.id
        """).fetchall()
    
    st.markdown(f"### Found: {len(diseases)} diseases")
    
    for disease in diseases:
        d = dict(disease)
        with st.container():
            st.markdown(f"<div class='category-card'><h3>{d.get('icon', '🦠')} {get_name(d)}</h3><p><strong>Category:</strong> {get_name(d, 'cat')}</p><p><strong>Severity:</strong> {d.get('severity', 'Unknown')}</p></div>", unsafe_allow_html=True)
            with st.expander("View Details"):
                st.markdown(f"**Description:** {get_desc(d) or d.get('description_en', 'N/A')}")
                st.markdown(f"**Symptoms:** {get_name(d, 'symptoms') or d.get('symptoms_en', 'N/A')}")
                st.markdown(f"**Causes:** {get_name(d, 'causes') or d.get('causes_en', 'N/A')}")
                st.markdown(f"**Treatment:** {get_name(d, 'treatment') or d.get('treatment_en', 'N/A')}")

# ==================== Tests ====================

def render_tests():
    st.markdown(f"<div class='main-header'><h1>{t('lab_tests')}</h1></div>", unsafe_allow_html=True)
    
    if conn is None:
        return
    
    search = st.text_input("Search tests...")
    
    if search:
        tests = conn.execute("SELECT * FROM test_types WHERE name_en LIKE ? OR name_ku LIKE ?", (f"%{search}%", f"%{search}%")).fetchall()
    else:
        tests = conn.execute("SELECT * FROM test_types").fetchall()
    
    st.markdown(f"### Found: {len(tests)} tests")
    
    for test in tests:
        tst = dict(test)
        st.markdown(f"<div class='info-box'><h4>📊 {get_name(tst)}</h4><p><strong>Unit:</strong> {tst['unit']}</p><p><strong>Normal Range:</strong> {tst['normal_range_low']} - {tst['normal_range_high']} {tst['unit']}</p><p><strong>Price:</strong> ${tst.get('price', 'N/A')}</p></div>", unsafe_allow_html=True)

# ==================== Practical ====================

def render_practical():
    st.markdown(f"<div class='main-header'><h1>{t('practical')}</h1></div>", unsafe_allow_html=True)
    
    if conn is None:
        return
    
    practicals = conn.execute("SELECT * FROM practical_tests").fetchall()
    st.markdown(f"### Found: {len(practicals)} practical tests")
    
    for practical in practicals:
        p = dict(practical)
        st.markdown(f"<div class='category-card'><h3>🔬 {get_name(p, 'title')}</h3><p><strong>Category:</strong> {p.get('category', 'General')}</p><p><strong>Duration:</strong> {p.get('duration_minutes', 'N/A')} minutes</p><p><strong>Difficulty:</strong> {p.get('difficulty_level', 'Basic')}</p></div>", unsafe_allow_html=True)
        with st.expander("View Procedure"):
            st.markdown(f"**Description:** {get_desc(p) or p.get('description_en', 'N/A')}")
            st.markdown(f"**Materials:** {get_name(p, 'materials') or p.get('materials_en', 'N/A')}")
            st.markdown(f"**Steps:**\n{get_name(p, 'steps') or p.get('steps_en', 'N/A')}")

# ==================== Notes ====================

def render_notes():
    st.markdown(f"<div class='main-header'><h1>{t('theory')}</h1></div>", unsafe_allow_html=True)
    
    if conn is None:
        return
    
    with st.expander("➕ Add New Note", expanded=False):
        with st.form("note_form"):
            topic = st.text_input("Topic")
            content = st.text_area("Content", height=150)
            category = st.selectbox("Category", ["Hematology", "Clinical Chemistry", "Microbiology", "Immunology", "General"])
            tags = st.text_input("Tags (comma separated)")
            if st.form_submit_button("Save"):
                if topic and content:
                    conn.execute("INSERT INTO study_notes (topic, content, category, tags) VALUES (?,?,?,?)", (topic, content, category, tags))
                    conn.commit()
                    st.success("Note saved!")
                    st.rerun()
    
    notes = conn.execute("SELECT * FROM study_notes ORDER BY created_at DESC").fetchall()
    st.markdown(f"### Found: {len(notes)} notes")
    
    for note in notes:
        n = dict(note)
        st.markdown(f"<div class='info-box'><h4>📚 {n['topic']}</h4><p><strong>Category:</strong> {n.get('category', 'General')}</p><p><small>Created: {n['created_at']}</small></p></div>", unsafe_allow_html=True)
        with st.expander("View Content"):
            st.markdown(n['content'])
            if n.get('tags'):
                st.markdown(f"**Tags:** {n['tags']}")

# ==================== Results ====================

def render_results():
    st.markdown(f"<div class='main-header'><h1>{t('results_entry')}</h1></div>", unsafe_allow_html=True)
    
    if conn is None:
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.form("result_form"):
            name = st.text_input("Patient Name")
            age = st.number_input("Age", 0, 120, 30)
            gender = st.selectbox("Gender", ["Male", "Female"])
            
            tests = conn.execute("SELECT id, name_en, name_ku, unit FROM test_types").fetchall()
            test_options = {f"{get_name(dict(t))} ({t['unit']})": t['id'] for t in tests}
            selected_test = st.selectbox("Test", list(test_options.keys()))
            
            result = st.number_input("Result Value", step=0.01)
            notes = st.text_area("Notes")
            
            if st.form_submit_button("Save Result"):
                test_id = test_options[selected_test]
                conn.execute("INSERT INTO test_results (patient_name, patient_age, patient_gender, test_id, result_value, notes) VALUES (?,?,?,?,?,?)", (name, age, gender, test_id, result, notes))
                conn.commit()
                st.success("Result saved!")
                st.rerun()
    
    with col2:
        st.markdown("### Recent Results")
        results = conn.execute("""
            SELECT tr.*, tt.name_en, tt.name_ku, tt.unit 
            FROM test_results tr 
            JOIN test_types tt ON tr.test_id = tt.id 
            ORDER BY tr.date_performed DESC 
            LIMIT 10
        """).fetchall()
        for r in results:
            rd = dict(r)
            st.markdown(f"<div class='test-result-normal'><strong>{rd['patient_name']}</strong> - {get_name(rd)}<br>Result: {rd['result_value']} {rd['unit']}<br><small>{rd['date_performed']}</small></div>", unsafe_allow_html=True)

# ==================== Reports ====================

def render_reports():
    st.markdown(f"<div class='main-header'><h1>{t('reports')}</h1></div>", unsafe_allow_html=True)
    
    if conn is None:
        return
    
    results = conn.execute("""
        SELECT tr.*, tt.name_en, tt.name_ku, tt.category 
        FROM test_results tr 
        JOIN test_types tt ON tr.test_id = tt.id
    """).fetchall()
    
    if not results:
        st.info("No results yet")
        return
    
    df = pd.DataFrame([dict(r) for r in results])
    lang = st.session_state.get("language", "کوردی 🇹🇯")
    df['test_name'] = df['name_ku'] if lang == "کوردی 🇹🇯" else df['name_en']
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Tests", len(df))
    with col2:
        st.metric("Abnormal Results", df['is_abnormal'].sum())
    
    fig = px.bar(df['test_name'].value_counts().head(10), title="Top Tests")
    st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(df[['patient_name', 'test_name', 'result_value', 'date_performed']], use_container_width=True)
    
    csv = df.to_csv(index=False)
    st.download_button("📥 Download CSV", csv, "report.csv", "text/csv")

# ==================== AI Chat ====================

def render_ai_chat():
    st.markdown(f"<div class='main-header'><h1>{t('ai_chat')}</h1></div>", unsafe_allow_html=True)
    
    suggestions = ["What does CBC measure?", "Normal glucose levels?", "What causes anemia?"]
    cols = st.columns(len(suggestions))
    for i, sug in enumerate(suggestions):
        with cols[i]:
            if st.button(sug):
                st.session_state.chat_input = sug
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    for chat in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(chat['q'])
        with st.chat_message("assistant"):
            st.write(chat['a'])
    
    question = st.chat_input("Ask me anything about medical lab...")
    if question:
        with st.chat_message("user"):
            st.write(question)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = get_ai_response(question)
                st.write(answer)
                st.session_state.chat_history.append({'q': question, 'a': answer})

# ==================== Main ====================

def main():
    if 'language' not in st.session_state:
        st.session_state.language = "کوردی 🇹🇯"
    if 'nav_page' not in st.session_state:
        st.session_state.nav_page = "dashboard"
    
    with st.sidebar:
        st.markdown("<h2 style='text-align:center;color:#1565c0;'>🔬 MediLab Pro</h2>", unsafe_allow_html=True)
        
        lang = st.selectbox("🌐 Language / زمان", ["کوردی 🇹🇯", "English 🇬🇧"])
        if lang != st.session_state.language:
            st.session_state.language = lang
            st.rerun()
        
        st.markdown("---")
        
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
        
        for key, name in pages.items():
            if st.button(name, key=key, use_container_width=True):
                st.session_state.nav_page = key
                st.rerun()
        
        st.markdown("---")
        st.markdown("<div style='text-align:center;background:linear-gradient(135deg,#667eea,#764ba2);border-radius:10px;padding:10px;color:white;'><strong>🎓 دانیال ئیسماعیل</strong><br>قۆناغی چوارەم<br>© 2024</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='student-info'><h2>🎓 دانیال ئیسماعیل</h2><p>قۆناغی چوارەم - بەشی تاقیگەی پزیشکی</p></div>", unsafe_allow_html=True)
    
    page = st.session_state.nav_page
    if page == "dashboard":
        render_dashboard()
    elif page == "diseases":
        render_diseases()
    elif page == "tests":
        render_tests()
    elif page == "practical":
        render_practical()
    elif page == "notes":
        render_notes()
    elif page == "results":
        render_results()
    elif page == "reports":
        render_reports()
    elif page == "ai":
        render_ai_chat()
    else:
        render_dashboard()
    
    st.markdown("---")
    st.caption("🔬 Medical Laboratory System | For educational purposes only")

if __name__ == "__main__":
    if conn:
        main()
    else:
        st.error("❌ Database connection failed. Please restart the app.")
