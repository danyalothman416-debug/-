# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from itertools import groupby
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
    @import url('https://fonts.googleapis.com/css2?family=Noto+Naskh+Arabic:wght@400;500;600;700&family=Noto+Sans:wght@400;500;600;700&display=swap');

    * {
        font-family: 'Noto Naskh Arabic', 'Noto Sans', sans-serif !important;
    }

    [dir="rtl"] {
        direction: rtl;
        text-align: right;
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

    .normal-range {
        color: #2e7d32;
        font-weight: bold;
    }

    .critical-range {
        color: #c62828;
        font-weight: bold;
    }

    .stMarkdown, .stMarkdown p, .stMarkdown h1,
    .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
        color: #1a1a1a !important;
    }

</style>
""", unsafe_allow_html=True)

# ==================== Database ====================

@st.cache_resource
def init_db():
    try:
        conn = sqlite3.connect(
            'medical_lab.db',
            check_same_thread=False,
            timeout=30
        )

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
            symptoms_ku TEXT
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
            date_performed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        conn.commit()
        return conn

    except Exception as e:
        st.error(f"Database Error: {e}")
        return None


conn = init_db()

# ==================== Insert Data ====================

def insert_data(conn):
    if conn is None:
        return

    try:
        count = conn.execute(
            "SELECT COUNT(*) as c FROM test_types"
        ).fetchone()

        if count['c'] > 0:
            return

        categories = [
            ("Hematology", "خوێنناسی",
             "Blood disorders",
             "نەخۆشییەکانی خوێن",
             "🩸"),

            ("Clinical Chemistry", "کیمیای کلینیکی",
             "Chemical tests",
             "پشکنینی کیمیایی",
             "🧪"),
        ]

        conn.executemany("""
        INSERT INTO disease_categories
        (name_en,name_ku,description_en,description_ku,icon)
        VALUES (?,?,?,?,?)
        """, categories)

        tests = [
            (
                "CBC",
                "CBC",
                "Hematology",
                "cells/μL",
                4.5,
                11.0,
                2.0,
                15.0,
                "Complete Blood Count",
                "پشکنینی تەواوی خوێن"
            ),

            (
                "Blood Glucose",
                "شەکری خوێن",
                "Clinical Chemistry",
                "mg/dL",
                70,
                100,
                40,
                300,
                "Blood Sugar Test",
                "پشکنینی شەکری خوێن"
            )
        ]

        conn.executemany("""
        INSERT INTO test_types
        (name_en,name_ku,category,unit,
        normal_range_low,normal_range_high,
        critical_low,critical_high,
        description_en,description_ku)

        VALUES (?,?,?,?,?,?,?,?,?,?)
        """, tests)

        diseases = [
            (
                1,
                "Anemia",
                "کەمخوێنی",
                "Low hemoglobin",
                "کەمی هیمۆگلۆبین",
                "Fatigue, Weakness",
                "ماندووبوون، لاوازی"
            )
        ]

        conn.executemany("""
        INSERT INTO diseases
        (category_id,name_en,name_ku,
        description_en,description_ku,
        symptoms_en,symptoms_ku)

        VALUES (?,?,?,?,?,?,?)
        """, diseases)

        practicals = [
            (
                "Blood Smear",
                "سمێری خوێن",
                "Blood smear preparation",
                "ئامادەکردنی سمێری خوێن",
                "Hematology",

                "1. Clean slide\n2. Add blood\n3. Spread blood",

                "١. پاککردنەوەی سلاید\n٢. دانانی خوێن\n٣. بڵاوکردنەوەی خوێن",

                "Slide, Blood, Stain",

                "سلاید، خوێن، ڕەنگ",

                "Normal cells visible",

                "خانە ئاساییەکان دەردەکەون",

                "Check RBC and WBC",

                "پشکنینی RBC و WBC",

                30,

                "Basic"
            )
        ]

        conn.executemany("""
        INSERT INTO practical_tests
        (
        title_en,title_ku,
        description_en,description_ku,
        category,
        steps_en,steps_ku,
        materials_en,materials_ku,
        expected_results_en,expected_results_ku,
        interpretation_en,interpretation_ku,
        duration_minutes,difficulty_level
        )

        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, practicals)

        conn.commit()

    except Exception as e:
        st.error(f"Insert Error: {e}")


insert_data(conn)

# ==================== Translation ====================

def t(key):

    translations = {
        "کوردی 🇹🇯": {
            "dashboard": "📊 داشبۆرد",
            "disease_db": "🦠 نەخۆشییەکان",
            "lab_tests": "🧪 پشکنینەکان",
            "practical": "🔬 پراکتیکی",
            "theory": "📚 تێبینییەکان",
            "results_entry": "📝 ئەنجامەکان",
            "reports": "📈 ڕاپۆرت",
            "ai_chat": "🤖 AI",
            "description": "ڕوونکردنەوە",
            "symptoms": "نیشانەکان",
            "normal_range": "مەودای ئاسایی",
            "critical_values": "مەترسی",
            "low": "نزم",
            "high": "بەرز",
            "unit": "یەکە",
            "minutes": "خولەک",
            "procedure": "هەنگاوەکان",
            "materials": "کەرەستەکان",
            "expected_results": "ئەنجامی چاوەڕوانکراو",
            "interpretation": "لێکدانەوە",
            "save_note": "تۆمارکردن",
            "saved_success": "بەسەرکەوتوویی تۆمارکرا",
            "patient_name": "ناوی نەخۆش",
            "patient_age": "تەمەن",
            "patient_gender": "ڕەگەز",
            "select_test": "پشکنین",
            "result_value": "ئەنجام",
            "save_result": "تۆمارکردن",
            "ask_ai": "پرسیار بکە",
            "type_question": "پرسیار..."
        },

        "English 🇬🇧": {
            "dashboard": "Dashboard",
            "disease_db": "Diseases",
            "lab_tests": "Lab Tests",
            "practical": "Practical",
            "theory": "Notes",
            "results_entry": "Results",
            "reports": "Reports",
            "ai_chat": "AI Chat"
        }
    }

    lang = st.session_state.get("language", "کوردی 🇹🇯")

    return translations.get(lang, {}).get(key, key)

# ==================== Helper ====================

def get_name(row, prefix="name"):

    lang_map = {
        "English 🇬🇧": "en",
        "کوردی 🇹🇯": "ku"
    }

    lang = lang_map.get(
        st.session_state.get("language", "کوردی 🇹🇯"),
        "ku"
    )

    field = f"{prefix}_{lang}"

    if isinstance(row, dict):
        return row.get(field, "")
    else:
        return row[field]


def get_desc(row):
    return get_name(row, "description")

# ==================== AI ====================

def get_gemini_response(question):

    try:
        api_key = os.environ.get("GEMINI_API_KEY", "")

        if api_key:

            genai.configure(api_key=api_key)

            model = genai.GenerativeModel("gemini-pro")

            response = model.generate_content(question)

            return response.text

    except Exception as e:
        return f"Gemini Error: {e}"

    q = question.lower()

    if "cbc" in q:
        return "CBC پشکنینی تەواوی خوێنە."

    if "glucose" in q:
        return "Glucose بۆ پشکنینی شەکرە."

    return "تکایە پرسیارێکی پەیوەندیدار بنووسە."

# ==================== Dashboard ====================

def render_dashboard():

    if conn is None:
        st.error("Database not connected")
        return

    st.markdown(f"## {t('dashboard')}")

    try:

        cats = conn.execute(
            "SELECT COUNT(*) as c FROM disease_categories"
        ).fetchone()['c']

        tests = conn.execute(
            "SELECT COUNT(*) as c FROM test_types"
        ).fetchone()['c']

        diseases = conn.execute(
            "SELECT COUNT(*) as c FROM diseases"
        ).fetchone()['c']

        practicals = conn.execute(
            "SELECT COUNT(*) as c FROM practical_tests"
        ).fetchone()['c']

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("📂 بەشەکان", cats)
        c2.metric("🧪 پشکنینەکان", tests)
        c3.metric("🦠 نەخۆشییەکان", diseases)
        c4.metric("🔬 پراکتیکی", practicals)

    except Exception as e:
        st.error(e)

# ==================== Diseases ====================

def render_diseases():

    if conn is None:
        return

    st.markdown(f"## {t('disease_db')}")

    try:

        diseases = conn.execute("""
        SELECT d.*, dc.name_en as ce, dc.name_ku as ck
        FROM diseases d
        JOIN disease_categories dc
        ON d.category_id = dc.id
        """).fetchall()

        for disease in diseases:

            d = dict(disease)

            lang = st.session_state.get(
                'language',
                'کوردی 🇹🇯'
            )

            if lang == "English 🇬🇧":
                cat_name = d.get("ce", "")
            else:
                cat_name = d.get("ck", "")

            with st.expander(
                f"🦠 {get_name(d)} - {cat_name}"
            ):

                st.markdown(
                    f"### {t('description')}"
                )

                st.write(get_desc(d))

                st.markdown(
                    f"### {t('symptoms')}"
                )

                symptoms = get_name(
                    d,
                    "symptoms"
                )

                if symptoms:

                    for s in symptoms.split(","):

                        st.markdown(
                            f"<span class='symptom-tag'>{s.strip()}</span>",
                            unsafe_allow_html=True
                        )

    except Exception as e:
        st.error(e)

# ==================== Tests ====================

def render_tests():

    if conn is None:
        return

    st.markdown(f"## {t('lab_tests')}")

    try:

        tests = conn.execute(
            "SELECT * FROM test_types"
        ).fetchall()

        sorted_tests = sorted(
            tests,
            key=lambda x: x['category']
        )

        for category, group in groupby(
            sorted_tests,
            key=lambda x: x['category']
        ):

            st.markdown(f"### 📁 {category}")

            for test in group:

                td = dict(test)

                with st.expander(
                    f"📊 {get_name(td)}"
                ):

                    st.markdown(f"""
                    <div class="info-box">

                    <p><strong>{t('unit')}:</strong>
                    {td['unit']}</p>

                    <p>
                    <strong class="normal-range">
                    {t('normal_range')}:
                    {td['normal_range_low']}
                    -
                    {td['normal_range_high']}
                    </strong>
                    </p>

                    <p>
                    <strong>{t('description')}:</strong>
                    {get_desc(td)}
                    </p>

                    </div>

                    <div class="warning-box">

                    <h4>{t('critical_values')}</h4>

                    <p>
                    {t('low')}:
                    <span class="critical-range">
                    &lt; {td['critical_low']}
                    </span>
                    </p>

                    <p>
                    {t('high')}:
                    <span class="critical-range">
                    &gt; {td['critical_high']}
                    </span>
                    </p>

                    </div>
                    """, unsafe_allow_html=True)

    except Exception as e:
        st.error(e)

# ==================== Practical ====================

def render_practical():

    if conn is None:
        return

    st.markdown(f"## {t('practical')}")

    try:

        practicals = conn.execute(
            "SELECT * FROM practical_tests"
        ).fetchall()

        for test in practicals:

            td = dict(test)

            with st.expander(
                f"🔬 {get_name(td,'title')}"
            ):

                st.markdown(
                    f"### {t('description')}"
                )

                st.write(get_desc(td))

                st.markdown(
                    f"### {t('procedure')}"
                )

                steps_text = get_name(td, 'steps') or ""

                steps = steps_text.split('\n')

                for i, step in enumerate(steps):

                    if step.strip():

                        st.markdown(
                            f"<p><span class='step-number'>{i+1}</span> {step}</p>",
                            unsafe_allow_html=True
                        )

                col1, col2 = st.columns(2)

                with col1:

                    st.markdown(
                        f"### {t('materials')}"
                    )

                    materials_text = get_name(
                        td,
                        'materials'
                    ) or ""

                    for m in materials_text.split(','):
                        st.markdown(f"- {m.strip()}")

                with col2:

                    st.markdown(
                        f"### {t('expected_results')}"
                    )

                    st.info(
                        get_name(
                            td,
                            'expected_results'
                        ) or ""
                    )

                st.markdown(
                    f"### {t('interpretation')}"
                )

                st.success(
                    get_name(
                        td,
                        'interpretation'
                    ) or ""
                )

    except Exception as e:
        st.error(e)

# ==================== Notes ====================

def render_notes():

    if conn is None:
        return

    st.markdown(f"## {t('theory')}")

    topic = st.text_input("Topic")

    content = st.text_area("Content")

    if st.button(t('save_note')):

        if topic and content:

            conn.execute("""
            INSERT INTO study_notes
            (topic,content)
            VALUES (?,?)
            """, (topic, content))

            conn.commit()

            st.success(t('saved_success'))

            st.rerun()

# ==================== Results ====================

def render_results():

    if conn is None:
        return

    st.markdown(f"## {t('results_entry')}")

    try:

        with st.form("result_form"):

            name = st.text_input(
                t('patient_name')
            ).strip()

            age = st.number_input(
                t('patient_age'),
                0,
                120,
                20
            )

            gender = st.selectbox(
                t('patient_gender'),
                ["نێر", "مێ"]
            )

            all_tests = conn.execute(
                "SELECT * FROM test_types"
            ).fetchall()

            test_opts = {
                get_name(dict(t)): t['id']
                for t in all_tests
            }

            selected_test = st.selectbox(
                t('select_test'),
                list(test_opts.keys())
            )

            value = st.number_input(
                t('result_value'),
                step=0.01
            )

            submitted = st.form_submit_button(
                t('save_result')
            )

            if submitted:

                tid = test_opts[selected_test]

                test = conn.execute("""
                SELECT * FROM test_types
                WHERE id = ?
                """, (tid,)).fetchone()

                abnormal = 0

                if (
                    value < test['normal_range_low']
                    or
                    value > test['normal_range_high']
                ):
                    abnormal = 1

                conn.execute("""
                INSERT INTO test_results
                (
                patient_name,
                patient_age,
                patient_gender,
                test_id,
                result_value,
                is_abnormal
                )

                VALUES (?,?,?,?,?,?)
                """, (
                    name,
                    age,
                    gender,
                    tid,
                    value,
                    abnormal
                ))

                conn.commit()

                st.success(
                    t('saved_success')
                )

    except Exception as e:
        st.error(e)

# ==================== Reports ====================

def render_reports():

    if conn is None:
        return

    st.markdown(f"## {t('reports')}")

    try:

        results = conn.execute("""
        SELECT tr.*,
        tt.name_en as ten,
        tt.name_ku as tku

        FROM test_results tr

        JOIN test_types tt
        ON tr.test_id = tt.id
        """).fetchall()

        if not results:
            st.info("No Results")
            return

        df = pd.DataFrame(
            [dict(r) for r in results]
        )

        lang = st.session_state.get(
            "language",
            "کوردی 🇹🇯"
        )

        if lang == "English 🇬🇧":
            df['test_name'] = df['ten']
        else:
            df['test_name'] = df['tku']

        required_cols = [
            'patient_name',
            'test_name',
            'result_value',
            'is_abnormal',
            'date_performed'
        ]

        existing_cols = [
            c for c in required_cols
            if c in df.columns
        ]

        st.dataframe(
            df[existing_cols],
            use_container_width=True
        )

    except Exception as e:
        st.error(e)

# ==================== AI CHAT ====================

def render_ai_chat():

    st.markdown(f"## {t('ai_chat')}")

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    for chat in st.session_state.chat_history:

        with st.chat_message("user"):
            st.write(chat['question'])

        with st.chat_message("assistant"):
            st.markdown(chat['answer'])

    question = st.chat_input(
        t('type_question')
    )

    if question:

        with st.chat_message("user"):
            st.write(question)

        with st.chat_message("assistant"):

            with st.spinner("..."):

                answer = get_gemini_response(
                    question
                )

                st.markdown(answer)

        st.session_state.chat_history.append({
            "question": question,
            "answer": answer
        })

# ==================== MAIN ====================

def main():

    if 'language' not in st.session_state:
        st.session_state.language = "کوردی 🇹🇯"

    with st.sidebar:

        st.markdown("## 🔬 Navigation")

        language = st.selectbox(
            "🌐 Language",
            ["کوردی 🇹🇯", "English 🇬🇧"]
        )

        st.session_state.language = language

        pages = {
            t('dashboard'): "dashboard",
            t('disease_db'): "diseases",
            t('lab_tests'): "tests",
            t('practical'): "practical",
            t('theory'): "notes",
            t('results_entry'): "results",
            t('reports'): "reports",
            t('ai_chat'): "ai"
        }

        page = st.radio(
            "Pages",
            list(pages.keys())
        )

        current_page = pages[page]

    st.markdown("""
    <div class="student-info">
        <h2>🎓 دانیال ئیسماعیل</h2>
        <p>قۆناغی چوارەم</p>
    </div>
    """, unsafe_allow_html=True)

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

# ==================== RUN ====================

if __name__ == "__main__":

    if conn:
        main()

    else:
        st.error(
            "Database connection failed"
        )
