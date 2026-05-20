# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime
import plotly.express as px
import google.generativeai as genai

# ================= PAGE CONFIG =================

st.set_page_config(
    page_title="MediLab Pro",
    page_icon="🔬",
    layout="wide"
)

# ================= CSS =================

st.markdown("""
<style>

.main-header{
    background:linear-gradient(135deg,#1565c0,#0d47a1);
    padding:20px;
    border-radius:15px;
    color:white;
    text-align:center;
    margin-bottom:20px;
}

.card{
    background:#f5f7fa;
    padding:15px;
    border-radius:12px;
    margin-bottom:10px;
    border-right:5px solid #1565c0;
}

.result-card{
    background:#e8f5e9;
    padding:12px;
    border-radius:10px;
    margin-bottom:10px;
}

</style>
""", unsafe_allow_html=True)

# ================= DATABASE =================

DB_NAME = "medical_lab.db"

@st.cache_resource
def init_db():

    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row

    conn.executescript("""

    CREATE TABLE IF NOT EXISTS disease_categories(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name_en TEXT,
        name_ku TEXT,
        icon TEXT
    );

    CREATE TABLE IF NOT EXISTS diseases(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER,
        name_en TEXT,
        name_ku TEXT,
        description_en TEXT,
        description_ku TEXT,
        symptoms_en TEXT,
        symptoms_ku TEXT,
        treatment_en TEXT,
        treatment_ku TEXT,
        severity TEXT
    );

    CREATE TABLE IF NOT EXISTS test_types(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name_en TEXT,
        name_ku TEXT,
        category TEXT,
        unit TEXT,
        normal_low REAL,
        normal_high REAL,
        price REAL
    );

    CREATE TABLE IF NOT EXISTS practical_tests(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title_en TEXT,
        title_ku TEXT,
        category TEXT,
        steps_en TEXT,
        steps_ku TEXT,
        duration INTEGER
    );

    CREATE TABLE IF NOT EXISTS study_notes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT,
        content TEXT,
        category TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS test_results(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT,
        patient_age INTEGER,
        patient_gender TEXT,
        test_id INTEGER,
        result_value REAL,
        notes TEXT,
        date_performed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    """)

    conn.commit()

    return conn

conn = init_db()

# ================= INSERT DATA =================

def insert_data():

    count = conn.execute(
        "SELECT COUNT(*) as c FROM test_types"
    ).fetchone()["c"]

    if count > 0:
        return

    categories = [
        ("Hematology","خوێنناسی","🩸"),
        ("Clinical Chemistry","کیمیای کلینیکی","🧪"),
        ("Microbiology","مایکرۆبایۆلۆجی","🔬")
    ]

    conn.executemany(
        "INSERT INTO disease_categories(name_en,name_ku,icon) VALUES(?,?,?)",
        categories
    )

    diseases = [
        (
            1,
            "Iron Deficiency Anemia",
            "کەمخوێنی",
            "Low iron anemia",
            "کەمبوونی ئاسن",
            "Fatigue",
            "ماندووبوون",
            "Iron supplements",
            "ئاسن",
            "Moderate"
        ),

        (
            2,
            "Diabetes",
            "شەکرە",
            "High blood sugar",
            "بەرزی شەکر",
            "Thirst",
            "تینوێتی",
            "Insulin",
            "ئینسولین",
            "Severe"
        )
    ]

    conn.executemany("""

    INSERT INTO diseases(
        category_id,
        name_en,
        name_ku,
        description_en,
        description_ku,
        symptoms_en,
        symptoms_ku,
        treatment_en,
        treatment_ku,
        severity
    )

    VALUES(?,?,?,?,?,?,?,?,?,?)

    """, diseases)

    tests = [

        (
            "CBC",
            "CBC",
            "Hematology",
            "cells/uL",
            4.5,
            11.0,
            25
        ),

        (
            "Glucose",
            "شەکری خوێن",
            "Chemistry",
            "mg/dL",
            70,
            100,
            20
        ),

        (
            "Cholesterol",
            "کۆلێسترۆڵ",
            "Chemistry",
            "mg/dL",
            120,
            200,
            30
        )
    ]

    conn.executemany("""

    INSERT INTO test_types(
        name_en,
        name_ku,
        category,
        unit,
        normal_low,
        normal_high,
        price
    )

    VALUES(?,?,?,?,?,?,?)

    """, tests)

    practicals = [

        (
            "Blood Smear",
            "سمێری خوێن",
            "Hematology",
            "1.Clean slide\n2.Add blood\n3.Spread",
            "١.سلاید پاک بکە\n٢.خوێن زیاد بکە",
            30
        )
    ]

    conn.executemany("""

    INSERT INTO practical_tests(
        title_en,
        title_ku,
        category,
        steps_en,
        steps_ku,
        duration
    )

    VALUES(?,?,?,?,?,?)

    """, practicals)

    conn.commit()

insert_data()

# ================= LANGUAGE =================

if "lang" not in st.session_state:
    st.session_state.lang = "ku"

def get_text(en, ku):

    if st.session_state.lang == "ku":
        return ku

    return en

# ================= SIDEBAR =================

with st.sidebar:

    st.title("🔬 MediLab Pro")

    lang = st.selectbox(
        "Language",
        ["کوردی","English"]
    )

    if lang == "کوردی":
        st.session_state.lang = "ku"
    else:
        st.session_state.lang = "en"

    page = st.radio(

        "Menu",

        [
            "Dashboard",
            "Diseases",
            "Tests",
            "Practical",
            "Notes",
            "Results",
            "Reports",
            "AI Chat"
        ]
    )

# ================= DASHBOARD =================

def dashboard():

    st.markdown(
        "<div class='main-header'><h1>Dashboard</h1></div>",
        unsafe_allow_html=True
    )

    c1,c2,c3,c4 = st.columns(4)

    disease_count = conn.execute(
        "SELECT COUNT(*) as c FROM diseases"
    ).fetchone()["c"]

    test_count = conn.execute(
        "SELECT COUNT(*) as c FROM test_types"
    ).fetchone()["c"]

    practical_count = conn.execute(
        "SELECT COUNT(*) as c FROM practical_tests"
    ).fetchone()["c"]

    result_count = conn.execute(
        "SELECT COUNT(*) as c FROM test_results"
    ).fetchone()["c"]

    c1.metric("Diseases", disease_count)
    c2.metric("Tests", test_count)
    c3.metric("Practical", practical_count)
    c4.metric("Results", result_count)

# ================= DISEASES =================

def diseases_page():

    st.markdown(
        "<div class='main-header'><h1>Diseases</h1></div>",
        unsafe_allow_html=True
    )

    search = st.text_input("Search")

    if search:

        rows = conn.execute("""

        SELECT d.*,dc.name_en as cat_en,
        dc.name_ku as cat_ku,
        dc.icon

        FROM diseases d

        JOIN disease_categories dc
        ON d.category_id = dc.id

        WHERE d.name_en LIKE ?
        OR d.name_ku LIKE ?

        """,(f"%{search}%",f"%{search}%")).fetchall()

    else:

        rows = conn.execute("""

        SELECT d.*,dc.name_en as cat_en,
        dc.name_ku as cat_ku,
        dc.icon

        FROM diseases d

        JOIN disease_categories dc
        ON d.category_id = dc.id

        """).fetchall()

    for row in rows:

        d = dict(row)

        disease_name = get_text(
            d["name_en"],
            d["name_ku"]
        )

        category_name = get_text(
            d["cat_en"],
            d["cat_ku"]
        )

        st.markdown(f"""

        <div class='card'>

        <h3>{d['icon']} {disease_name}</h3>

        <p><b>Category:</b> {category_name}</p>

        <p><b>Severity:</b> {d['severity']}</p>

        </div>

        """, unsafe_allow_html=True)

        with st.expander("Details"):

            st.write(get_text(
                d["description_en"],
                d["description_ku"]
            ))

            st.write("Symptoms:")

            st.write(get_text(
                d["symptoms_en"],
                d["symptoms_ku"]
            ))

            st.write("Treatment:")

            st.write(get_text(
                d["treatment_en"],
                d["treatment_ku"]
            ))

# ================= TESTS =================

def tests_page():

    st.markdown(
        "<div class='main-header'><h1>Lab Tests</h1></div>",
        unsafe_allow_html=True
    )

    rows = conn.execute(
        "SELECT * FROM test_types"
    ).fetchall()

    for row in rows:

        t = dict(row)

        test_name = get_text(
            t["name_en"],
            t["name_ku"]
        )

        st.markdown(f"""

        <div class='card'>

        <h3>🧪 {test_name}</h3>

        <p><b>Category:</b> {t['category']}</p>

        <p><b>Normal:</b> {t['normal_low']} - {t['normal_high']} {t['unit']}</p>

        <p><b>Price:</b> ${t['price']}</p>

        </div>

        """, unsafe_allow_html=True)

# ================= PRACTICAL =================

def practical_page():

    st.markdown(
        "<div class='main-header'><h1>Practical</h1></div>",
        unsafe_allow_html=True
    )

    rows = conn.execute(
        "SELECT * FROM practical_tests"
    ).fetchall()

    for row in rows:

        p = dict(row)

        title = get_text(
            p["title_en"],
            p["title_ku"]
        )

        steps = get_text(
            p["steps_en"],
            p["steps_ku"]
        )

        st.markdown(f"""

        <div class='card'>

        <h3>🔬 {title}</h3>

        <p><b>Category:</b> {p['category']}</p>

        <p><b>Duration:</b> {p['duration']} min</p>

        </div>

        """, unsafe_allow_html=True)

        with st.expander("Steps"):

            st.text(steps)

# ================= NOTES =================

def notes_page():

    st.markdown(
        "<div class='main-header'><h1>Notes</h1></div>",
        unsafe_allow_html=True
    )

    with st.form("note_form"):

        topic = st.text_input("Topic")

        content = st.text_area("Content")

        category = st.text_input("Category")

        submit = st.form_submit_button("Save")

        if submit:

            conn.execute("""

            INSERT INTO study_notes(
                topic,
                content,
                category
            )

            VALUES(?,?,?)

            """,(topic,content,category))

            conn.commit()

            st.success("Saved")

    notes = conn.execute(
        "SELECT * FROM study_notes ORDER BY id DESC"
    ).fetchall()

    for note in notes:

        n = dict(note)

        st.markdown(f"""

        <div class='card'>

        <h3>📚 {n['topic']}</h3>

        <p>{n['category']}</p>

        </div>

        """, unsafe_allow_html=True)

        with st.expander("Open"):

            st.write(n["content"])

# ================= RESULTS =================

def results_page():

    st.markdown(
        "<div class='main-header'><h1>Results</h1></div>",
        unsafe_allow_html=True
    )

    c1,c2 = st.columns(2)

    with c1:

        with st.form("result_form"):

            patient = st.text_input("Patient Name")

            age = st.number_input("Age",0,120,25)

            gender = st.selectbox(
                "Gender",
                ["Male","Female"]
            )

            tests = conn.execute(
                "SELECT * FROM test_types"
            ).fetchall()

            options = {}

            for t in tests:

                name = get_text(
                    t["name_en"],
                    t["name_ku"]
                )

                options[name] = t["id"]

            selected = st.selectbox(
                "Test",
                list(options.keys())
            )

            value = st.number_input(
                "Result",
                step=0.1
            )

            notes = st.text_area("Notes")

            submit = st.form_submit_button(
                "Save"
            )

            if submit:

                conn.execute("""

                INSERT INTO test_results(
                    patient_name,
                    patient_age,
                    patient_gender,
                    test_id,
                    result_value,
                    notes
                )

                VALUES(?,?,?,?,?,?)

                """,(

                    patient,
                    age,
                    gender,
                    options[selected],
                    value,
                    notes

                ))

                conn.commit()

                st.success("Saved")

    with c2:

        rows = conn.execute("""

        SELECT tr.*,
        tt.name_en,
        tt.name_ku,
        tt.unit

        FROM test_results tr

        JOIN test_types tt
        ON tr.test_id = tt.id

        ORDER BY tr.id DESC

        LIMIT 10

        """).fetchall()

        for row in rows:

            r = dict(row)

            test_name = get_text(
                r["name_en"],
                r["name_ku"]
            )

            st.markdown(f"""

            <div class='result-card'>

            <b>{r['patient_name']}</b>

            <br>

            {test_name}

            <br>

            {r['result_value']} {r['unit']}

            </div>

            """, unsafe_allow_html=True)

# ================= REPORTS =================

def reports_page():

    st.markdown(
        "<div class='main-header'><h1>Reports</h1></div>",
        unsafe_allow_html=True
    )

    rows = conn.execute("""

    SELECT tr.*,
    tt.name_en,
    tt.name_ku,
    tt.category

    FROM test_results tr

    JOIN test_types tt
    ON tr.test_id = tt.id

    """).fetchall()

    if not rows:

        st.warning("No data")

        return

    df = pd.DataFrame([dict(r) for r in rows])

    if st.session_state.lang == "ku":
        df["test_name"] = df["name_ku"]
    else:
        df["test_name"] = df["name_en"]

    st.dataframe(df)

    fig = px.bar(
        df["test_name"].value_counts(),
        title="Top Tests"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ================= AI =================

def ai_page():

    st.markdown(
        "<div class='main-header'><h1>AI Chat</h1></div>",
        unsafe_allow_html=True
    )

    q = st.chat_input("Ask")

    if q:

        st.chat_message("user").write(q)

        answer = "I can help you with medical laboratory information."

        if "cbc" in q.lower():
            answer = "CBC checks RBC, WBC and platelets."

        if "glucose" in q.lower():
            answer = "Normal glucose is 70-100 mg/dL."

        st.chat_message("assistant").write(answer)

# ================= ROUTER =================

if page == "Dashboard":
    dashboard()

elif page == "Diseases":
    diseases_page()

elif page == "Tests":
    tests_page()

elif page == "Practical":
    practical_page()

elif page == "Notes":
    notes_page()

elif page == "Results":
    results_page()

elif page == "Reports":
    reports_page()

elif page == "AI Chat":
    ai_page()
