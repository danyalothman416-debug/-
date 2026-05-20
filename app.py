import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import json
from typing import Dict, List, Optional
import plotly.express as px
import plotly.graph_objects as go

# ==================== Database Setup ====================
class LabDatabase:
    def __init__(self):
        self.conn = sqlite3.connect('medical_lab.db', check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
        self._insert_reference_data()
    
    def _create_tables(self):
        self.conn.executescript("""
            -- Disease Categories
            CREATE TABLE IF NOT EXISTS disease_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                icon TEXT
            );
            
            -- Specific Diseases
            CREATE TABLE IF NOT EXISTS diseases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER,
                name TEXT NOT NULL,
                description TEXT,
                symptoms TEXT,
                FOREIGN KEY (category_id) REFERENCES disease_categories(id)
            );
            
            -- Test Types
            CREATE TABLE IF NOT EXISTS test_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                category TEXT,
                unit TEXT,
                normal_range_low REAL,
                normal_range_high REAL,
                critical_low REAL,
                critical_high REAL,
                description TEXT
            );
            
            -- Disease-Specific Tests
            CREATE TABLE IF NOT EXISTS disease_tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                disease_id INTEGER,
                test_id INTEGER,
                is_diagnostic BOOLEAN DEFAULT 1,
                expected_result TEXT,
                notes TEXT,
                FOREIGN KEY (disease_id) REFERENCES diseases(id),
                FOREIGN KEY (test_id) REFERENCES test_types(id)
            );
            
            -- Test Results
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
            
            -- Practical Tests
            CREATE TABLE IF NOT EXISTS practical_tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                category TEXT,
                steps TEXT,
                materials TEXT,
                expected_results TEXT,
                interpretation TEXT,
                duration_minutes INTEGER,
                difficulty_level TEXT
            );
            
            -- Theory Questions
            CREATE TABLE IF NOT EXISTS theory_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                disease_id INTEGER,
                question TEXT NOT NULL,
                answer TEXT,
                category TEXT,
                difficulty TEXT,
                FOREIGN KEY (disease_id) REFERENCES diseases(id)
            );
            
            -- Study Notes
            CREATE TABLE IF NOT EXISTS study_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT,
                content TEXT,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        self.conn.commit()
    
    def _insert_reference_data(self):
        """Insert comprehensive medical test reference data"""
        
        # Disease Categories
        categories = [
            ("Hematology", "Blood disorders and diseases", "🩸"),
            ("Microbiology", "Bacterial, viral, fungal infections", "🦠"),
            ("Clinical Chemistry", "Chemical analysis of body fluids", "🧪"),
            ("Immunology", "Immune system disorders", "🛡️"),
            ("Parasitology", "Parasitic infections", "🐛"),
            ("Urinalysis", "Urine analysis", "💧"),
            ("Histopathology", "Tissue examination", "🔬"),
            ("Serology", "Blood serum analysis", "💉")
        ]
        
        for cat in categories:
            self.conn.execute(
                "INSERT OR IGNORE INTO disease_categories (name, description, icon) VALUES (?, ?, ?)",
                cat
            )
        
        # Test Types (Common lab tests)
        tests = [
            # Hematology
            ("CBC - Complete Blood Count", "Hematology", "cells/μL", 4.5, 11.0, 2.0, 15.0, "Complete blood cell count"),
            ("WBC Count", "Hematology", "×10³/μL", 4.0, 11.0, 2.0, 30.0, "White blood cell count"),
            ("RBC Count", "Hematology", "×10⁶/μL", 4.5, 5.5, 2.0, 7.0, "Red blood cell count"),
            ("Hemoglobin", "Hematology", "g/dL", 12.0, 16.0, 6.0, 20.0, "Hemoglobin level"),
            ("Platelet Count", "Hematology", "×10³/μL", 150, 400, 50, 1000, "Platelet count"),
            ("ESR", "Hematology", "mm/hr", 0, 20, 0, 100, "Erythrocyte sedimentation rate"),
            ("PT", "Hematology", "seconds", 11, 13.5, 9, 30, "Prothrombin time"),
            ("APTT", "Hematology", "seconds", 25, 35, 20, 60, "Activated partial thromboplastin time"),
            
            # Clinical Chemistry
            ("Blood Glucose Fasting", "Clinical Chemistry", "mg/dL", 70, 100, 40, 300, "Fasting blood sugar"),
            ("HbA1c", "Clinical Chemistry", "%", 4.0, 5.6, 3.0, 10.0, "Glycated hemoglobin"),
            ("Creatinine", "Clinical Chemistry", "mg/dL", 0.6, 1.2, 0.2, 5.0, "Kidney function marker"),
            ("BUN", "Clinical Chemistry", "mg/dL", 7, 20, 3, 50, "Blood urea nitrogen"),
            ("ALT", "Clinical Chemistry", "U/L", 7, 56, 5, 200, "Alanine aminotransferase"),
            ("AST", "Clinical Chemistry", "U/L", 10, 40, 5, 200, "Aspartate aminotransferase"),
            ("Total Bilirubin", "Clinical Chemistry", "mg/dL", 0.1, 1.2, 0.05, 5.0, "Bilirubin level"),
            ("Total Protein", "Clinical Chemistry", "g/dL", 6.0, 8.3, 4.0, 10.0, "Total protein"),
            ("Albumin", "Clinical Chemistry", "g/dL", 3.5, 5.0, 2.0, 7.0, "Albumin level"),
            ("Cholesterol Total", "Clinical Chemistry", "mg/dL", 125, 200, 100, 300, "Total cholesterol"),
            ("Triglycerides", "Clinical Chemistry", "mg/dL", 40, 150, 30, 300, "Triglycerides level"),
            ("HDL", "Clinical Chemistry", "mg/dL", 40, 60, 20, 80, "High-density lipoprotein"),
            ("LDL", "Clinical Chemistry", "mg/dL", 60, 130, 40, 190, "Low-density lipoprotein"),
            
            # Urinalysis
            ("Urine pH", "Urinalysis", "pH", 4.5, 8.0, 4.0, 9.0, "Urine acidity"),
            ("Urine Specific Gravity", "Urinalysis", "", 1.005, 1.030, 1.001, 1.040, "Urine concentration"),
            ("Urine Protein", "Urinalysis", "mg/dL", 0, 8, 0, 30, "Protein in urine"),
            ("Urine Glucose", "Urinalysis", "mg/dL", 0, 15, 0, 50, "Glucose in urine"),
            
            # Serology
            ("CRP", "Serology", "mg/L", 0, 3, 0, 10, "C-reactive protein"),
            ("RF", "Serology", "IU/mL", 0, 14, 0, 30, "Rheumatoid factor"),
            ("ASO Titer", "Serology", "IU/mL", 0, 200, 0, 400, "Anti-streptolysin O"),
            
            # Microbiology
            ("Blood Culture", "Microbiology", "colonies", 0, 0, 0, 1, "Blood culture"),
            ("Urine Culture", "Microbiology", "CFU/mL", 0, 10000, 10000, 100000, "Urine culture"),
            
            # Immunology
            ("IgG", "Immunology", "mg/dL", 700, 1600, 400, 2000, "Immunoglobulin G"),
            ("IgM", "Immunology", "mg/dL", 40, 230, 20, 300, "Immunoglobulin M"),
            ("IgA", "Immunology", "mg/dL", 70, 400, 50, 500, "Immunoglobulin A")
        ]
        
        for test in tests:
            self.conn.execute("""
                INSERT OR IGNORE INTO test_types 
                (name, category, unit, normal_range_low, normal_range_high, critical_low, critical_high, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, test)
        
        # Diseases
        diseases = [
            # Hematology
            (1, "Anemia", "Decreased red blood cells or hemoglobin", "Fatigue, weakness, pale skin, shortness of breath"),
            (1, "Leukemia", "Cancer of blood-forming tissues", "Fever, fatigue, frequent infections, weight loss"),
            (1, "Thrombocytopenia", "Low platelet count", "Easy bruising, prolonged bleeding, petechiae"),
            (1, "Hemophilia", "Blood clotting disorder", "Excessive bleeding, joint pain, easy bruising"),
            
            # Microbiology
            (2, "Urinary Tract Infection", "Bacterial infection of urinary system", "Burning urination, frequent urination, cloudy urine"),
            (2, "Pneumonia", "Lung infection", "Cough, fever, chest pain, difficulty breathing"),
            (2, "Tuberculosis", "Bacterial infection affecting lungs", "Chronic cough, night sweats, weight loss, fever"),
            (2, "Meningitis", "Inflammation of brain membranes", "Severe headache, fever, stiff neck, confusion"),
            
            # Clinical Chemistry
            (3, "Diabetes Mellitus", "High blood sugar levels", "Increased thirst, frequent urination, fatigue, blurred vision"),
            (3, "Kidney Disease", "Impaired kidney function", "Swelling, fatigue, changes in urination, nausea"),
            (3, "Liver Disease", "Liver dysfunction", "Jaundice, abdominal pain, fatigue, nausea"),
            (3, "Hyperlipidemia", "High blood fat levels", "Usually asymptomatic, detected by blood tests"),
            
            # Immunology
            (4, "Rheumatoid Arthritis", "Autoimmune joint disease", "Joint pain, swelling, stiffness, fatigue"),
            (4, "Lupus (SLE)", "Systemic autoimmune disease", "Joint pain, rash, fever, fatigue, organ involvement"),
            
            # Parasitology
            (5, "Malaria", "Parasitic infection transmitted by mosquitoes", "Fever, chills, headache, muscle pain"),
            (5, "Amebiasis", "Intestinal parasitic infection", "Diarrhea, abdominal pain, bloody stools"),
            
            # Urinalysis
            (6, "Nephrotic Syndrome", "Kidney disorder causing protein loss", "Swelling, foamy urine, weight gain, fatigue"),
        ]
        
        for disease in diseases:
            self.conn.execute(
                "INSERT OR IGNORE INTO diseases (category_id, name, description, symptoms) VALUES (?, ?, ?, ?)",
                disease
            )
        
        # Practical Tests
        practicals = [
            ("Blood Smear Preparation", "Learn to prepare and stain blood smears", "Hematology",
             "1. Clean slide with alcohol\n2. Place small drop of blood\n3. Use spreader slide at 30-45° angle\n4. Spread blood evenly\n5. Allow to air dry\n6. Fix with methanol\n7. Stain with Wright-Giemsa",
             "Glass slides, blood sample, Wright-Giemsa stain, methanol, microscope",
             "Well-spread monolayer of cells with feathered edge",
             "Check for cell morphology, parasites, abnormal cells", 45, "Basic"),
            
            ("Gram Staining", "Differentiate bacteria into Gram-positive and Gram-negative", "Microbiology",
             "1. Prepare bacterial smear\n2. Fix with heat\n3. Apply Crystal Violet (1 min)\n4. Apply Iodine (1 min)\n5. Decolorize with alcohol\n6. Counterstain with Safranin (30 sec)\n7. Wash and dry",
             "Bacterial culture, Crystal Violet, Iodine, Alcohol, Safranin, microscope slides",
             "Gram-positive: Purple/Blue\nGram-negative: Pink/Red",
             "Gram-positive bacteria have thick peptidoglycan layer", 60, "Basic"),
            
            ("Urinalysis - Dipstick Method", "Chemical analysis of urine using dipstick", "Urinalysis",
             "1. Collect fresh urine sample\n2. Dip test strip briefly\n3. Remove excess urine\n4. Read at specified times\n5. Compare with color chart",
             "Urine sample, dipstick test strips, timer, color chart",
             "Results compared to standard color chart for each parameter",
             "Multiple parameters: pH, protein, glucose, ketones, blood, etc.", 30, "Basic"),
            
            ("Blood Group Typing", "Determine ABO and Rh blood groups", "Hematology",
             "1. Prepare 3 drops of blood on slide\n2. Add Anti-A to first drop\n3. Add Anti-B to second drop\n4. Add Anti-D to third drop\n5. Mix gently\n6. Observe agglutination",
             "Blood sample, Anti-A, Anti-B, Anti-D sera, slides, mixing sticks",
             "Agglutination indicates presence of corresponding antigen",
             "Essential for blood transfusion compatibility", 30, "Basic"),
            
            ("ELISA Test", "Enzyme-Linked Immunosorbent Assay", "Immunology",
             "1. Coat plate with antigen\n2. Block non-specific binding\n3. Add patient sample\n4. Add detection antibody\n5. Add enzyme substrate\n6. Measure color change",
             "ELISA plate, antigens, antibodies, enzyme conjugate, substrate, microplate reader",
             "Color intensity proportional to antibody concentration",
             "Used for HIV, Hepatitis, and other infectious disease testing", 120, "Advanced"),
        ]
        
        for prac in practicals:
            self.conn.execute("""
                INSERT OR IGNORE INTO practical_tests 
                (title, description, category, steps, materials, expected_results, interpretation, duration_minutes, difficulty_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, prac)
        
        self.conn.commit()
    
    def get_categories(self) -> List[Dict]:
        return [dict(row) for row in self.conn.execute("SELECT * FROM disease_categories").fetchall()]
    
    def get_tests(self, category=None) -> List[Dict]:
        if category:
            return [dict(row) for row in self.conn.execute(
                "SELECT * FROM test_types WHERE category = ?", (category,)
            ).fetchall()]
        return [dict(row) for row in self.conn.execute("SELECT * FROM test_types").fetchall()]
    
    def get_diseases(self, category_id=None) -> List[Dict]:
        if category_id:
            return [dict(row) for row in self.conn.execute(
                "SELECT d.*, dc.name as category_name FROM diseases d JOIN disease_categories dc ON d.category_id = dc.id WHERE d.category_id = ?",
                (category_id,)
            ).fetchall()]
        return [dict(row) for row in self.conn.execute(
            "SELECT d.*, dc.name as category_name FROM diseases d JOIN disease_categories dc ON d.category_id = dc.id"
        ).fetchall()]
    
    def get_practical_tests(self, category=None) -> List[Dict]:
        if category:
            return [dict(row) for row in self.conn.execute(
                "SELECT * FROM practical_tests WHERE category = ?", (category,)
            ).fetchall()]
        return [dict(row) for row in self.conn.execute("SELECT * FROM practical_tests").fetchall()]

# ==================== Initialize Database ====================
@st.cache_resource
def get_db():
    return LabDatabase()

# ==================== Main Application ====================
def main():
    st.set_page_config(
        page_title="Medical Laboratory Analysis System",
        page_icon="🔬",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
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
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize database
    db = get_db()
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🔬 Navigation")
        
        page = st.radio(
            "Select Section",
            ["📊 Dashboard", "🦠 Disease Database", "🧪 Laboratory Tests", 
             "🔬 Practical Tests", "📚 Theory Questions", "📝 Test Results Entry",
             "📈 Reports & Analytics"]
        )
        
        st.markdown("---")
        st.markdown("### 📋 Quick Info")
        st.info("This system contains comprehensive medical laboratory test information for 4th stage students.")
    
    # Main content based on selected page
    if page == "📊 Dashboard":
        render_dashboard(db)
    elif page == "🦠 Disease Database":
        render_disease_database(db)
    elif page == "🧪 Laboratory Tests":
        render_lab_tests(db)
    elif page == "🔬 Practical Tests":
        render_practical_tests(db)
    elif page == "📚 Theory Questions":
        render_theory_questions(db)
    elif page == "📝 Test Results Entry":
        render_test_results(db)
    elif page == "📈 Reports & Analytics":
        render_reports(db)

def render_dashboard(db: LabDatabase):
    st.markdown("""
    <div class="main-header">
        <h1>🔬 Medical Laboratory Analysis System</h1>
        <h3>Fourth Stage - Disease Analysis</h3>
        <p>Comprehensive reference for all laboratory tests and disease analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    categories = db.get_categories()
    tests = db.get_tests()
    diseases = db.get_diseases()
    practicals = db.get_practical_tests()
    
    with col1:
        st.metric("Disease Categories", len(categories))
    with col2:
        st.metric("Laboratory Tests", len(tests))
    with col3:
        st.metric("Diseases", len(diseases))
    with col4:
        st.metric("Practical Tests", len(practicals))
    
    # Categories overview
    st.markdown("## 📂 Disease Categories")
    
    cols = st.columns(2)
    for i, cat in enumerate(categories):
        with cols[i % 2]:
            st.markdown(f"""
            <div class="category-card">
                <h3>{cat['icon']} {cat['name']}</h3>
                <p>{cat['description']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Recent tests overview
    st.markdown("## 🧪 Quick Reference - Common Tests")
    
    common_tests = tests[:6]  # Show first 6 tests
    cols = st.columns(3)
    for i, test in enumerate(common_tests):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="test-card">
                <h4>📊 {test['name']}</h4>
                <p><span class="normal-range">Normal: {test['normal_range_low']} - {test['normal_range_high']} {test['unit']}</span></p>
                <p><small>{test['description']}</small></p>
            </div>
            """, unsafe_allow_html=True)

def render_disease_database(db: LabDatabase):
    st.markdown("## 🦠 Disease Database")
    
    categories = db.get_categories()
    
    # Filter by category
    selected_category = st.selectbox(
        "Filter by Category",
        ["All Categories"] + [cat['name'] for cat in categories]
    )
    
    if selected_category != "All Categories":
        category_id = next(cat['id'] for cat in categories if cat['name'] == selected_category)
        diseases = db.get_diseases(category_id)
    else:
        diseases = db.get_diseases()
    
    # Search
    search = st.text_input("🔍 Search Diseases")
    if search:
        diseases = [d for d in diseases if search.lower() in d['name'].lower()]
    
    # Display diseases
    for disease in diseases:
        with st.expander(f"🦠 {disease['name']} - {disease['category_name']}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Description:** {disease['description']}")
                
                st.markdown("**Symptoms:**")
                if disease['symptoms']:
                    symptoms = disease['symptoms'].split(',')
                    symptom_html = ""
                    for symptom in symptoms:
                        symptom_html += f"<span class='symptom-tag'>{symptom.strip()}</span>"
                    st.markdown(symptom_html, unsafe_allow_html=True)
            
            with col2:
                st.markdown("**Category:**")
                st.info(disease['category_name'])
                
                # Show related tests
                st.markdown("**Related Tests:**")
                # Here you would query related tests

def render_lab_tests(db: LabDatabase):
    st.markdown("## 🧪 Laboratory Tests Reference")
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        categories = ["All"] + list(set(t['category'] for t in db.get_tests()))
        selected_category = st.selectbox("Test Category", categories)
    with col2:
        search = st.text_input("🔍 Search Tests")
    
    # Get tests
    if selected_category != "All":
        tests = db.get_tests(selected_category)
    else:
        tests = db.get_tests()
    
    if search:
        tests = [t for t in tests if search.lower() in t['name'].lower()]
    
    # Group tests by category
    from itertools import groupby
    tests_sorted = sorted(tests, key=lambda x: x['category'])
    
    for category, group in groupby(tests_sorted, key=lambda x: x['category']):
        st.markdown(f"### 📁 {category}")
        
        group_list = list(group)
        cols = st.columns(2)
        
        for i, test in enumerate(group_list):
            with cols[i % 2]:
                with st.container():
                    st.markdown(f"""
                    <div class="test-card">
                        <h4>📊 {test['name']}</h4>
                        <p><strong>Unit:</strong> {test['unit']}</p>
                        <p><span class="normal-range">Normal Range: {test['normal_range_low']} - {test['normal_range_high']}</span></p>
                        <p><strong>Description:</strong> {test['description']}</p>
                        <hr>
                        <p><strong>⚠️ Critical Values:</strong></p>
                        <p>Low: <span class="critical-range">< {test['critical_low']}</span> | 
                        High: <span class="critical-range">> {test['critical_high']}</span></p>
                    </div>
                    """, unsafe_allow_html=True)

def render_practical_tests(db: LabDatabase):
    st.markdown("## 🔬 Practical Laboratory Tests")
    
    # Filter
    col1, col2 = st.columns(2)
    with col1:
        categories = ["All"] + list(set(p['category'] for p in db.get_practical_tests()))
        selected = st.selectbox("Category", categories)
    with col2:
        difficulty = st.selectbox("Difficulty Level", ["All", "Basic", "Intermediate", "Advanced"])
    
    # Get tests
    if selected != "All":
        practicals = db.get_practical_tests(selected)
    else:
        practicals = db.get_practical_tests()
    
    if difficulty != "All":
        practicals = [p for p in practicals if p['difficulty_level'] == difficulty]
    
    # Display each practical test
    for i, test in enumerate(practicals):
        with st.expander(f"🔬 {test['title']} ({test['duration_minutes']} min - {test['difficulty_level']})"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Description:** {test['description']}")
                
                st.markdown("### 📝 Procedure Steps:")
                steps = test['steps'].split('\n')
                for j, step in enumerate(steps):
                    if step.strip():
                        st.markdown(f"<span class='step-number'>{j+1}</span> {step.strip()}", unsafe_allow_html=True)
                
                st.markdown("---")
                
                col_mat, col_exp = st.columns(2)
                with col_mat:
                    st.markdown("### 🧫 Materials Required:")
                    materials = test['materials'].split(',')
                    for mat in materials:
                        st.markdown(f"- {mat.strip()}")
                
                with col_exp:
                    st.markdown("### ✅ Expected Results:")
                    st.info(test['expected_results'])
            
            with col2:
                st.markdown(f"**Category:** {test['category']}")
                st.markdown(f"**Duration:** {test['duration_minutes']} minutes")
                st.markdown(f"**Difficulty:** {'⭐' * (['Basic','Intermediate','Advanced'].index(test['difficulty_level'])+1)}")
                
                st.markdown("---")
                st.markdown("### 🔍 Interpretation:")
                st.success(test['interpretation'])

def render_theory_questions(db: LabDatabase):
    st.markdown("## 📚 Theory Questions & Study Material")
    
    # Search
    search = st.text_input("Search questions or topics")
    
    # Add note-taking section
    with st.expander("📝 Add Study Notes"):
        col1, col2 = st.columns(2)
        with col1:
            topic = st.text_input("Topic")
            category = st.selectbox("Category", ["Hematology", "Microbiology", "Clinical Chemistry", 
                                                  "Immunology", "Parasitology", "Urinalysis"])
        with col2:
            content = st.text_area("Note Content", height=150)
        
        if st.button("Save Note"):
            db.conn.execute(
                "INSERT INTO study_notes (topic, content, category) VALUES (?, ?, ?)",
                (topic, content, category)
            )
            db.conn.commit()
            st.success("✅ Note saved!")
    
    # Display notes
    st.markdown("### 📖 Your Study Notes")
    notes = db.conn.execute("SELECT * FROM study_notes ORDER BY created_at DESC").fetchall()
    
    for note in notes:
        note_dict = dict(note)
        with st.expander(f"📝 {note_dict['topic']} - {note_dict['category']}"):
            st.markdown(note_dict['content'])
            st.caption(f"Created: {note_dict['created_at']}")
            if st.button("Delete", key=f"del_{note_dict['id']}"):
                db.conn.execute("DELETE FROM study_notes WHERE id = ?", (note_dict['id'],))
                db.conn.commit()
                st.rerun()

def render_test_results(db: LabDatabase):
    st.markdown("## 📝 Enter Test Results")
    
    with st.form("test_result_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            patient_name = st.text_input("Patient Name")
            patient_age = st.number_input("Patient Age", min_value=0, max_value=120)
        
        with col2:
            patient_gender = st.selectbox("Patient Gender", ["Male", "Female", "Other"])
            test_type = st.selectbox("Select Test", [t['name'] for t in db.get_tests()])
        
        with col3:
            result_value = st.number_input("Result Value", step=0.01)
            result_text = st.text_input("Result Text (optional)")
        
        notes = st.text_area("Additional Notes")
        
        if st.form_submit_button("Save Result"):
            # Find test ID
            test = db.conn.execute("SELECT * FROM test_types WHERE name = ?", (test_type,)).fetchone()
            if test:
                test_dict = dict(test)
                # Check if abnormal
                is_abnormal = False
                if result_value < test_dict['normal_range_low'] or result_value > test_dict['normal_range_high']:
                    is_abnormal = True
                
                db.conn.execute("""
                    INSERT INTO test_results (patient_name, patient_age, patient_gender, test_id, 
                                           result_value, result_text, is_abnormal, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (patient_name, patient_age, patient_gender, test_dict['id'], 
                     result_value, result_text, is_abnormal, notes))
                db.conn.commit()
                st.success("✅ Result saved successfully!")
                if is_abnormal:
                    st.warning("⚠️ Abnormal result detected!")

def render_reports(db: LabDatabase):
    st.markdown("## 📈 Reports & Analytics")
    
    # Get results data
    results = db.conn.execute("""
        SELECT tr.*, tt.name as test_name, tt.category
        FROM test_results tr 
        JOIN test_types tt ON tr.test_id = tt.id
        ORDER BY tr.date_performed DESC
    """).fetchall()
    
    if results:
        df = pd.DataFrame([dict(r) for r in results])
        
        # Statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Tests", len(df))
        with col2:
            abnormal = len(df[df['is_abnormal'] == True])
            st.metric("Abnormal Results", abnormal)
        with col3:
            normal_percentage = ((len(df) - abnormal) / len(df)) * 100 if len(df) > 0 else 0
            st.metric("Normal Rate", f"{normal_percentage:.1f}%")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Tests by category
            category_counts = df['category'].value_counts()
            fig = px.pie(values=category_counts.values, names=category_counts.index, 
                        title="Tests by Category")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Normal vs Abnormal
            status_counts = df['is_abnormal'].value_counts()
            fig = px.bar(x=['Normal', 'Abnormal'], y=status_counts.values,
                        title="Normal vs Abnormal Results",
                        color=['Normal', 'Abnormal'],
                        color_discrete_map={'Normal': '#2e7d32', 'Abnormal': '#c62828'})
            st.plotly_chart(fig, use_container_width=True)
        
        # Results table
        st.markdown("### 📋 Recent Results")
        st.dataframe(df[['patient_name', 'test_name', 'result_value', 'is_abnormal', 'date_performed']],
                    use_container_width=True)
    else:
        st.info("No test results recorded yet. Use the 'Test Results Entry' page to add results.")

if __name__ == "__main__":
    main()
