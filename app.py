import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from itertools import groupby
import hashlib

# ==================== Config & Constants ====================
st.set_page_config(
    page_title="سیستەمی شیکردنەوەی تاقیگەی پزیشکی - وەشانی ٢.٠",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== Custom CSS with better Kurdish support ====================
def load_custom_css():
    st.markdown("""
    <style>
        /* Import Kurdish-friendly fonts */
        @import url('https://fonts.googleapis.com/css2?family=Noto+Naskh+Arabic:wght@400;500;600;700&family=Noto+Sans:ital,wght@0,400;0,600;0,700;1,400&display=swap');
        
        /* RTL Support */
        * {
            font-family: 'Noto Naskh Arabic', 'Segoe UI', 'Noto Sans', sans-serif;
        }
        
        [dir="rtl"] {
            direction: rtl;
            text-align: right;
        }
        
        /* Modern header design */
        .modern-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem 2rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .modern-header h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            font-weight: 700;
        }
        
        .modern-header p {
            font-size: 1.1rem;
            opacity: 0.95;
        }
        
        /* Card design */
        .card {
            background: white;
            border-radius: 15px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            border: 1px solid #e0e0e0;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        }
        
        /* Metric cards */
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 15px;
            padding: 1.2rem;
            text-align: center;
            margin: 0.5rem 0;
        }
        
        .metric-card h3 {
            font-size: 2rem;
            margin: 0.5rem 0;
            font-weight: bold;
        }
        
        .metric-card p {
            margin: 0;
            opacity: 0.9;
            font-size: 0.9rem;
        }
        
        /* Status badges */
        .badge-normal {
            background: #4caf50;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
        }
        
        .badge-abnormal {
            background: #f44336;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
        }
        
        .badge-warning {
            background: #ff9800;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
        }
        
        /* Test cards */
        .test-card {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 12px;
            padding: 1rem;
            margin: 0.5rem 0;
            border-left: 4px solid #667eea;
        }
        
        /* Search bar */
        .search-box {
            background: white;
            border-radius: 50px;
            padding: 0.5rem 1rem;
            border: 2px solid #e0e0e0;
            transition: all 0.3s ease;
        }
        
        .search-box:focus-within {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102,126,234,0.1);
        }
        
        /* Button styling */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 0.6rem 1.5rem;
            border-radius: 50px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        /* Animation */
        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .fade-in {
            animation: fadeIn 0.5s ease-out;
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .modern-header h1 {
                font-size: 1.5rem;
            }
            
            .metric-card h3 {
                font-size: 1.2rem;
            }
        }
        
        /* RTL specific styles */
        .rtl-margin {
            margin-right: 0.5rem;
            margin-left: 0;
        }
    </style>
    """, unsafe_allow_html=True)

# ==================== Translations ====================
TRANSLATIONS = {
    "English": {
        "app_title": "🔬 Medical Laboratory Analysis System v2.0",
        "app_subtitle": "Advanced Disease Analysis Platform",
        "dashboard": "📊 Dashboard",
        "disease_db": "🦠 Disease Database",
        "lab_tests": "🧪 Lab Tests",
        "practical": "🔬 Practical Tests",
        "theory": "📚 Theory & Notes",
        "results_entry": "📝 Results Entry",
        "reports": "📈 Analytics",
        "total_categories": "Categories",
        "total_tests": "Lab Tests",
        "total_diseases": "Diseases",
        "total_practical": "Practical Tests",
        "normal_range": "Normal Range",
        "critical": "Critical Values",
        "search": "🔍 Search",
        "filter": "Filter",
        "all": "All",
        "save": "Save",
        "delete": "Delete",
        "edit": "Edit",
        "close": "Close",
        "confirm": "Confirm",
        "cancel": "Cancel",
        "yes": "Yes",
        "no": "No",
        "success": "Success!",
        "error": "Error!",
        "warning": "Warning!",
        "info": "Information",
        "loading": "Loading...",
        "no_data": "No data available",
        "abnormal": "Abnormal",
        "normal": "Normal",
        "patient_name": "Patient Name",
        "patient_age": "Age",
        "patient_gender": "Gender",
        "male": "Male",
        "female": "Female",
        "other": "Other"
    },
    "کوردی": {
        "app_title": "🔬 سیستەمی شیکردنەوەی تاقیگەی پزیشکی وەشانی ٢.٠",
        "app_subtitle": "پلاتفۆرمی پێشکەوتووی شیکردنەوەی نەخۆشییەکان",
        "dashboard": "📊 داشبۆرد",
        "disease_db": "🦠 بنکەدراوەی نەخۆشییەکان",
        "lab_tests": "🧪 پشکنینەکان",
        "practical": "🔬 پشکنینی پراکتیکی",
        "theory": "📚 تیۆری و تێبینی",
        "results_entry": "📝 تۆمارکردنی ئەنجام",
        "reports": "📈 شیکردنەوەکان",
        "total_categories": "پۆلەکان",
        "total_tests": "پشکنینەکان",
        "total_diseases": "نەخۆشییەکان",
        "total_practical": "پشکنینی پراکتیکی",
        "normal_range": "مەودای ئاسایی",
        "critical": "نرخی مەترسیدار",
        "search": "🔍 گەڕان",
        "filter": "پاڵێوکردن",
        "all": "هەموو",
        "save": "تۆمارکردن",
        "delete": "سڕینەوە",
        "edit": "دەستکاری",
        "close": "داخستن",
        "confirm": "پشتڕاستکردنەوە",
        "cancel": "پەشیمانبوون",
        "yes": "بەڵێ",
        "no": "نەخێر",
        "success": "سەرکەوتوو بوو!",
        "error": "هەڵە!",
        "warning": "ئاگاداری!",
        "info": "زانیاری",
        "loading": "چاوەڕوان بە...",
        "no_data": "هیچ زانیاریەک نییە",
        "abnormal": "نائاسایی",
        "normal": "ئاسایی",
        "patient_name": "ناوی نەخۆش",
        "patient_age": "تەمەن",
        "patient_gender": "ڕەگەز",
        "male": "نێر",
        "female": "مێ",
        "other": "هی تر"
    }
}

# ==================== Database Class ====================
class MedicalLabDatabase:
    def __init__(self):
        self.conn = sqlite3.connect('medical_lab_v2.db', check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.init_database()
    
    def init_database(self):
        """Initialize database with proper schema and indexes"""
        self.conn.executescript("""
            -- Enable foreign keys
            PRAGMA foreign_keys = ON;
            
            -- Disease Categories table
            CREATE TABLE IF NOT EXISTS disease_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name_en TEXT NOT NULL,
                name_ku TEXT NOT NULL,
                description_en TEXT,
                description_ku TEXT,
                icon TEXT,
                color TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- Diseases table
            CREATE TABLE IF NOT EXISTS diseases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER,
                name_en TEXT NOT NULL,
                name_ku TEXT NOT NULL,
                description_en TEXT,
                description_ku TEXT,
                symptoms_en TEXT,
                symptoms_ku TEXT,
                treatment_en TEXT,
                treatment_ku TEXT,
                prevention_en TEXT,
                prevention_ku TEXT,
                FOREIGN KEY (category_id) REFERENCES disease_categories(id) ON DELETE CASCADE
            );
            
            -- Test Types table
            CREATE TABLE IF NOT EXISTS test_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name_en TEXT NOT NULL,
                name_ku TEXT NOT NULL,
                category TEXT,
                subcategory TEXT,
                unit TEXT,
                normal_range_low REAL,
                normal_range_high REAL,
                critical_low REAL,
                critical_high REAL,
                description_en TEXT,
                description_ku TEXT,
                preparation_en TEXT,
                preparation_ku TEXT
            );
            
            -- Practical Tests table
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
                difficulty_level TEXT,
                video_url TEXT,
                image_url TEXT
            );
            
            -- Study Notes table
            CREATE TABLE IF NOT EXISTS study_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                topic TEXT,
                content TEXT,
                category TEXT,
                tags TEXT,
                is_favorite BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- Test Results table
            CREATE TABLE IF NOT EXISTS test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT,
                patient_name TEXT,
                patient_age INTEGER,
                patient_gender TEXT,
                test_id INTEGER,
                result_value REAL,
                result_text TEXT,
                is_abnormal BOOLEAN,
                severity TEXT,
                notes TEXT,
                doctor_name TEXT,
                date_performed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (test_id) REFERENCES test_types(id)
            );
            
            -- Create indexes for better performance
            CREATE INDEX IF NOT EXISTS idx_diseases_category ON diseases(category_id);
            CREATE INDEX IF NOT EXISTS idx_test_results_patient ON test_results(patient_id);
            CREATE INDEX IF NOT EXISTS idx_test_results_date ON test_results(date_performed);
            CREATE INDEX IF NOT EXISTS idx_study_notes_user ON study_notes(user_id);
        """)
        self.conn.commit()
        
        # Insert reference data if empty
        if not self.conn.execute("SELECT COUNT(*) FROM disease_categories").fetchone()[0]:
            self.insert_reference_data()
    
    def insert_reference_data(self):
        """Insert initial reference data"""
        categories = [
            ("Hematology", "خوێنناسی", "Blood disorders and analysis", "نەخۆشی و شیکردنەوەی خوێن", "🩸", "#e53935"),
            ("Microbiology", "مایکرۆبایۆلۆجی", "Bacterial, viral, and fungal infections", "هەوکردنە بەکتریایی، ڤایرۆسی و کەڕووییەکان", "🦠", "#43a047"),
            ("Clinical Chemistry", "کیمیای کلینیکی", "Chemical analysis of body fluids", "شیکردنەوەی کیمیایی شلەکانی لەش", "🧪", "#1e88e5"),
            ("Immunology", "ئیمیونۆلۆجی", "Immune system disorders and testing", "تێکچوون و پشکنینی سیستەمی بەرگری", "🛡️", "#fb8c00"),
            ("Parasitology", "مشقوڕخوێناسی", "Parasitic infections and diagnosis", "هەوکردن و دەستنیشانکردنی مشقوڕخوەکان", "🐛", "#8e24aa"),
            ("Urinalysis", "شیکردنەوەی میز", "Urine analysis and diagnostics", "شیکردنەوە و دەستنیشانکردنی میز", "💧", "#00acc1"),
            ("Serology", "سیرۆلۆجی", "Blood serum analysis", "شیکردنەوەی شلەی خوێن", "💉", "#fdd835"),
            ("Histopathology", "هیستۆپاتۆلۆجی", "Tissue examination and biopsy", "پشکنینی شانەکان و بایۆپسی", "🔬", "#546e7a")
        ]
        
        for cat in categories:
            self.conn.execute("""
                INSERT INTO disease_categories 
                (name_en, name_ku, description_en, description_ku, icon, color) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, cat)
        
        # Insert more comprehensive test data
        tests = [
            ("CBC", "CBC - ژماردنی تەواوی خوێن", "Hematology", "Complete Blood Count",
             "cells/uL", 4.5, 11.0, 2.0, 15.0,
             "Complete blood cell count for diagnosing anemia, infections, and blood disorders",
             "ژماردنی تەواوی خانەکانی خوێن بۆ دەستنیشانکردنی کەمخوێنی، هەوکردن و نەخۆشییەکانی خوێن",
             "Fasting not required", "پێویست بە بەڕۆژوویی نییە"),
             
            ("WBC", "ژماردنی WBC", "Hematology", "White Blood Cells",
             "x10³/uL", 4.0, 11.0, 2.0, 30.0,
             "White blood cell count for detecting infections and immune disorders",
             "ژماردنی خانە سپییەکانی خوێن بۆ دۆزینەوەی هەوکردن و نەخۆشییەکانی بەرگری",
             "Fasting not required", "پێویست بە بەڕۆژوویی نییە"),
             
            ("Hb", "هیمۆگلۆبین", "Hematology", "Hemoglobin",
             "g/dL", 12.0, 16.0, 6.0, 20.0,
             "Hemoglobin level for diagnosing anemia and polycythemia",
             "ئاستی هیمۆگلۆبین بۆ دەستنیشانکردنی کەمخوێنی و زۆری خانە سوورەکانی خوێن",
             "No special preparation", "ئامادەکاری تایبەت پێویست نییە"),
             
            ("Glucose", "گلوکۆز", "Clinical Chemistry", "Blood Sugar",
             "mg/dL", 70, 100, 40, 300,
             "Blood glucose level for diabetes diagnosis and monitoring",
             "ئاستی گلوکۆزی خوێن بۆ دەستنیشانکردن و چاودێریکردنی شەکرە",
             "Fasting for 8-12 hours required", "بەڕۆژوویی ٨-١٢ کاتژمێر پێویستە"),
        ]
        
        for test in tests:
            self.conn.execute("""
                INSERT INTO test_types 
                (name_en, name_ku, category, subcategory, unit, normal_range_low, 
                 normal_range_high, critical_low, critical_high, description_en, 
                 description_ku, preparation_en, preparation_ku)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, test)
        
        self.conn.commit()

# ==================== Session State Management ====================
def init_session_state():
    """Initialize session state variables"""
    defaults = {
        'language': 'کوردی',
        'user_id': hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8],
        'theme': 'light',
        'sidebar_state': 'expanded',
        'notifications': [],
        'favorites': set()
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# ==================== Helper Functions ====================
def t(key):
    """Get translation for current language"""
    lang = st.session_state.get('language', 'کوردی')
    return TRANSLATIONS[lang].get(key, key)

def get_localized(row, field, default=""):
    """Get localized value from database row"""
    lang = st.session_state.get('language', 'کوردی')
    suffix = 'ku' if lang == 'کوردی' else 'en'
    
    value = row.get(f"{field}_{suffix}")
    if value is None:
        value = row.get(f"{field}_en", default)
    return value

def show_notification(message, type="info"):
    """Show a notification message"""
    icons = {"success": "✅", "error": "❌", "warning": "⚠️", "info": "ℹ️"}
    st.toast(f"{icons.get(type, 'ℹ️')} {message}")

# ==================== UI Components ====================
def render_sidebar():
    """Render modern sidebar navigation"""
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <div style="font-size: 3rem;">🔬</div>
            <h3 style="margin: 0; color: #667eea;">MedLab</h3>
            <p style="margin: 0; font-size: 0.8rem; opacity: 0.7;">v2.0</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Language selector
        lang = st.selectbox(
            "🌐 " + ("Language" if st.session_state.language == "English" else "زمان"),
            ["English", "کوردی"],
            key="lang_select"
        )
        if lang != st.session_state.language:
            st.session_state.language = lang
            st.rerun()
        
        st.markdown("---")
        
        # Navigation
        pages = {
            t('dashboard'): "📊",
            t('disease_db'): "🦠",
            t('lab_tests'): "🧪",
            t('practical'): "🔬",
            t('theory'): "📚",
            t('results_entry'): "📝",
            t('reports'): "📈"
        }
        
        selected = st.radio(
            "", 
            list(pages.keys()),
            format_func=lambda x: f"{pages[x]} {x}"
        )
        
        st.markdown("---")
        
        # User info
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%); 
                    border-radius: 10px; padding: 1rem; margin-top: 1rem;">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div style="font-size: 2rem;">👤</div>
                <div>
                    <div style="font-weight: bold;">{t('user') if 'user' in t('user') else 'کاربەر'}</div>
                    <div style="font-size: 0.8rem; opacity: 0.7;">ID: {st.session_state.user_id[:6]}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        return selected

# ==================== Main Pages ====================
def render_dashboard(db):
    """Enhanced dashboard with real metrics"""
    st.markdown(f"""
    <div class="modern-header fade-in">
        <h1>{t('app_title')}</h1>
        <p>{t('app_subtitle')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get real-time statistics
    categories_count = db.conn.execute("SELECT COUNT(*) FROM disease_categories").fetchone()[0]
    tests_count = db.conn.execute("SELECT COUNT(*) FROM test_types").fetchone()[0]
    diseases_count = db.conn.execute("SELECT COUNT(*) FROM diseases").fetchone()[0]
    practicals_count = db.conn.execute("SELECT COUNT(*) FROM practical_tests").fetchone()[0]
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 2rem;">📂</div>
            <h3>{categories_count}</h3>
            <p>{t('total_categories')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 2rem;">🧪</div>
            <h3>{tests_count}</h3>
            <p>{t('total_tests')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 2rem;">🦠</div>
            <h3>{diseases_count}</h3>
            <p>{t('total_diseases')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 2rem;">🔬</div>
            <h3>{practicals_count}</h3>
            <p>{t('total_practical')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Categories overview
    st.markdown("### 📂 " + t('total_categories'))
    categories = db.conn.execute("SELECT * FROM disease_categories").fetchall()
    
    cols = st.columns(3)
    for idx, cat in enumerate(categories):
        with cols[idx % 3]:
            st.markdown(f"""
            <div class="card fade-in" style="border-left: 4px solid {cat['color']};">
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <div style="font-size: 3rem;">{cat['icon']}</div>
                    <div>
                        <h4 style="margin: 0;">{get_localized(cat, 'name')}</h4>
                        <p style="margin: 0.5rem 0 0 0; font-size: 0.85rem; opacity: 0.7;">
                            {get_localized(cat, 'description')[:100]}...
                        </p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

def render_lab_tests(db):
    """Modern lab tests interface"""
    st.markdown(f"## 🧪 {t('lab_tests')}")
    
    # Search and filter
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search = st.text_input(t('search'), placeholder=f"{t('search')}...")
    
    with col2:
        categories = [t('all')] + [c['category'] for c in db.conn.execute("SELECT DISTINCT category FROM test_types").fetchall()]
        selected_cat = st.selectbox(t('filter'), categories)
    
    # Query tests
    query = "SELECT * FROM test_types"
    params = []
    if selected_cat != t('all'):
        query += " WHERE category = ?"
        params.append(selected_cat)
    
    tests = db.conn.execute(query, params).fetchall()
    
    if search:
        tests = [t for t in tests if search.lower() in get_localized(t, 'name').lower()]
    
    if not tests:
        st.info(t('no_data'))
        return
    
    # Display tests in grid
    for test in tests:
        with st.expander(f"🧪 {get_localized(test, 'name')}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**📝 {t('description')}:** {get_localized(test, 'description')}")
                st.markdown(f"**📊 {t('normal_range')}:** {test['normal_range_low']} - {test['normal_range_high']} {test['unit']}")
                
                if test['preparation_ku'] or test['preparation_en']:
                    st.markdown(f"**📋 {t('preparation') if 'preparation' in t('preparation') else 'ئامادەکاری'}:** {get_localized(test, 'preparation')}")
            
            with col2:
                st.markdown(f"**⚠️ {t('critical')}:**")
                st.markdown(f"- 🔻 {t('low')}: {test['critical_low']}")
                st.markdown(f"- 🔺 {t('high')}: {test['critical_high']}")
                st.markdown(f"**📁 {t('category')}:** {test['category']}")

# ==================== Main App ====================
def main():
    # Initialize
    load_custom_css()
    init_session_state()
    db = MedicalLabDatabase()
    
    # Render sidebar and get selected page
    selected_page = render_sidebar()
    
    # Page routing
    pages = {
        t('dashboard'): render_dashboard,
        t('lab_tests'): render_lab_tests,
        # Add other pages as needed
    }
    
    # Render selected page
    if selected_page in pages:
        pages[selected_page](db)
    else:
        render_dashboard(db)

if __name__ == "__main__":
    main()
