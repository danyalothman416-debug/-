# -*- coding: utf-8 -*-
🔬
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import os
import random
from typing import List, Dict, Any
# ==================== Page Config ====================
st.set
_page_config(
page_
ﺳ "=title
لﺎ#ٮ.ٮاد -
ە ﮕ # ٮ % ڡ
ﺎ % ٮ
یەوە.ٮدﺮﮑ#ٮﺷ
ﻣ ە % ٮ
," ﻞ#ٮﻋﺎﻤﺴ#ٮﺋ
ﯽ
ﺴ # ٮ
page_
icon="
,"
layout="wide",
initial
sidebar
_
_state="expanded"
)
# ==================== Custom CSS ====================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?
family=Noto+Kurdish:wght@400;500;600;700&family=Noto+Sans+Arabic:wght@400;500;600;7
00&display=swap');
{ *
font-family: 'Noto Sans Arabic', 'Noto Kurdish', sans-serif !important;
}
body {
direction: rtl;
}
.main-header {
color: white;
background: linear-gradient(135deg, #0d47a1 0%, #1565c0 50%, #1976d2 100%);
padding: 20px;
border-radius: 12px;
text-align: center;
margin-bottom: 20px;
box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
.main-header h1 {
font-size: 1.5rem !important;
margin: 0 0 5px 0 !important;
color: white !important;
}
.main-header p {
font-size: 0.9rem !important;
margin: 0 !important;
color: rgba(255,255,255,0.9) !important;
}
.student-info {
background: linear-gradient(135deg, #1a237e, #283593);
color: white;
padding: 12px 15px;
border-radius: 10px;
text-align: center;
margin-bottom: 15px;
box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.student-info h2 {
font-size: 1.1rem !important;
margin: 0 0 3px 0 !important;
color: white !important;
}
.student-info p {
font-size: 0.8rem !important;
margin: 0 !important;
color: rgba(255,255,255,0.9) !important;
}
.category-card {
background: linear-gradient(135deg, #e8eaf6, #c5cae9);
padding: 15px;
border-radius: 10px;
margin: 8px 0;
border-right: 4px solid #1565c0;
box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
.info-box {
background: #e3f2fd;
padding: 12px;
border-radius: 8px;
border-right: 3px solid #1565c0;
margin: 8px 0;
}
.info-box h4 {
font-size: 1rem !important;
margin: 0 0 8px 0 !important;
}
.warning-box {
background: #fff3e0;
padding: 12px;
border-radius: 8px;
border-right: 3px solid #ff9800;
margin: 8px 0;
}
.critical-box {
background: #ffebee;
padding: 12px;
border-radius: 8px;
border-right: 3px solid #f44336;
border-right: 3px solid #f44336;
margin: 8px 0;
}
.symptom-tag {
display: inline-block;
background: linear-gradient(135deg, #ffebee, #ffcdd2);
color: #c62828;
padding: 4px 10px;
border-radius: 15px;
margin: 2px;
font-size: 0.85em;
border: 1px solid #ef9a9a;
}
.step-number {
display: inline-block;
background: linear-gradient(135deg, #0d47a1, #1565c0);
color: white;
width: 28px;
height: 28px;
border-radius: 50%;
text-align: center;
line-height: 28px;
margin-left: 6px;
font-weight: bold;
font-size: 0.85em;
}
.normal-range {
color: #2e7d32;
font-weight: bold;
background-color: #e8f5e9;
padding: 2px 6px;
border-radius: 4px;
font-size: 0.9em;
}
.critical-range {
color: #c62828;
color: #c62828;
font-weight: bold;
background-color: #ffebee;
padding: 2px 6px;
border-radius: 4px;
}
.stat-card {
background: white;
padding: 15px;
border-radius: 10px;
box-shadow: 0 2px 6px rgba(0,0,0,0.1);
text-align: center;
}
.test-result-normal {
background-color: #e8f5e9;
padding: 8px;
border-radius: 6px;
border-right: 3px solid #4caf50;
margin: 4px 0;
font-size: 0.9em;
}
.test-result-abnormal {
background-color: #fff3e0;
padding: 8px;
border-radius: 6px;
border-right: 3px solid #ff9800;
margin: 4px 0;
font-size: 0.9em;
}
.test-result-critical {
background-color: #ffebee;
padding: 8px;
border-radius: 6px;
border-right: 3px solid #f44336;
margin: 4px 0;
margin: 4px 0;
font-size: 0.9em;
}
.practical-step {
background: #f5f5f5;
padding: 8px;
margin: 4px 0;
border-radius: 5px;
border-left: 3px solid #1565c0;
font-size: 0.9em;
}
.note-card {
background: white;
padding: 12px;
border-radius: 8px;
margin: 8px 0;
box-shadow: 0 2px 4px rgba(0,0,0,0.1);
border-top: 3px solid #1565c0;
}
/* Fix sidebar button text */
.stButton > button {
font-size: 0.85rem !important;
white-space: normal !important;
word-wrap: break-word !important;
text-align: right !important;
direction: rtl !important;
}
/* Fix sidebar heading */
.sidebar .stMarkdown h2 {
font-size: 1.2rem !important;
}
/* Reduce MediLab Pro size */
[data-testid="stSidebar"] h2 {
font-size: 1.3rem !important;
}
/* Fix text colors */
.stMarkdown, .stMarkdown p, .stMarkdown h1,
.stMarkdown h2, .stMarkdown h3, .stMarkdown h4,
.stMarkdown h5, .stMarkdown h6 {
color: #1a1a1a !important;
}
/* Dark mode fixes */
@media (prefers-color-scheme: dark) {
.stMarkdown, .stMarkdown p, .stMarkdown h3, .stMarkdown h4 {
color: #e0e0e0 !important;
}
}
</style>
""", unsafe_
allow
_html=True)
# ==================== Database ====================
@st.cache_
resource
def init
_db():
"""Initialize database"""
try:
if os.path.exists('medical_lab.db'):
try:
test
_conn = sqlite3.connect('medical_lab.db')
test
_conn.execute("SELECT 1")
test
_conn.close()
except:
os.remove('medical_lab.db')
conn = sqlite3.connect('medical_lab.db', check_
same
_thread=False, timeout=30)
conn.execute("PRAGMA journal_mode=WAL")
conn.execute("PRAGMA foreign_keys=ON")
conn.row
_factory = sqlite3.Row
conn.executescript("""
CREATE TABLE IF NOT EXISTS disease
_categories (
id INTEGER PRIMARY KEY AUTOINCREMENT,
name
_en TEXT NOT NULL UNIQUE,
name
_ku TEXT NOT NULL UNIQUE,
description_en TEXT,
description_ku TEXT,
icon TEXT,
color TEXT,
created
at TIMESTAMP DEFAULT CURRENT
TIMESTAMP
_
_
);
CREATE TABLE IF NOT EXISTS diseases (
id INTEGER PRIMARY KEY AUTOINCREMENT,
category_id INTEGER NOT NULL,
name
_en TEXT NOT NULL,
name
_ku TEXT NOT NULL,
description_en TEXT,
description_ku TEXT,
symptoms_en TEXT,
symptoms_ku TEXT,
causes
_en TEXT,
causes
_ku TEXT,
treatment
_en TEXT,
treatment
_ku TEXT,
severity TEXT DEFAULT 'Moderate',
FOREIGN KEY (category_id) REFERENCES disease_categories(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS test
_types (
id INTEGER PRIMARY KEY AUTOINCREMENT,
name
_en TEXT NOT NULL UNIQUE,
name
_ku TEXT NOT NULL UNIQUE,
category TEXT NOT NULL,
unit TEXT,
normal
_range_low REAL,
normal
_range_high REAL,
critical
_low REAL,
critical
_high REAL,
description_en TEXT,
description_ku TEXT,
preparation_en TEXT,
preparation_ku TEXT,
turnaround
_time TEXT DEFAULT '24 hours',
price REAL DEFAULT 0.0
);
CREATE TABLE IF NOT EXISTS practical_tests (
id INTEGER PRIMARY KEY AUTOINCREMENT,
title
_en TEXT NOT NULL,
title
_ku TEXT NOT NULL,
description_en TEXT,
description_ku TEXT,
category TEXT,
steps_en TEXT,
steps_ku TEXT,
materials
_en TEXT,
materials
_ku TEXT,
expected_
results
_en TEXT,
expected_
results
_ku TEXT,
interpretation_en TEXT,
interpretation_ku TEXT,
precautions_en TEXT,
precautions_ku TEXT,
duration
_minutes INTEGER,
difficulty_level TEXT CHECK(difficulty_level IN ('Basic', 'Intermediate', 'Advanced')),
created
at TIMESTAMP DEFAULT CURRENT
TIMESTAMP
_
_
);
CREATE TABLE IF NOT EXISTS study_notes (
id INTEGER PRIMARY KEY AUTOINCREMENT,
topic TEXT NOT NULL,
content TEXT NOT NULL,
category TEXT,
tags TEXT,
created
_
at TIMESTAMP DEFAULT CURRENT
_TIMESTAMP,
updated_
at TIMESTAMP DEFAULT CURRENT
_
TIMESTAMP
);
CREATE TABLE IF NOT EXISTS test
_results (
id INTEGER PRIMARY KEY AUTOINCREMENT,
patient_name TEXT NOT NULL,
patient_age INTEGER,
patient_gender TEXT CHECK(patient_gender IN ('Male', 'Female', 'Other')),
test
_id INTEGER NOT NULL,
result
_value REAL,
result
_text TEXT,
is
_abnormal INTEGER DEFAULT 0,
is
_critical INTEGER DEFAULT 0,
notes TEXT,
date
_performed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
FOREIGN KEY (test_id) REFERENCES test_types(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx
test
results
_
_
_patient ON test_results(patient_name);
CREATE INDEX IF NOT EXISTS idx
test
results
date ON test
_
_
_
_results(date_performed);
CREATE INDEX IF NOT EXISTS idx
diseases
_
_category ON diseases(category_id);
""")
conn.commit()
return conn
except Exception as e:
st.error(f"Database Connection Error: {str(e)}")
return None
conn = init
_db()
# ==================== Insert Data ====================
def insert
_comprehensive_data(conn):
"""Insert medical data into database"""
if conn is None:
return
try:
count = conn.execute("SELECT COUNT(*) as c FROM test_types").fetchone()
if count['c'] > 5:
return
# Clear existing data
conn.execute("DELETE FROM test_results")
conn.execute("DELETE FROM practical_tests")
conn.execute("DELETE FROM study_notes")
conn.execute("DELETE FROM diseases")
conn.execute("DELETE FROM test_types")
conn.execute("DELETE FROM disease_categories")
# Disease Categories
categories = [
ﺳ ﺎ . ٮ . ٮ #ٚ ٮ
و . ﺣ " ,"Hematology"(
," ﯽ
"Study of blood and blood disorders",
," ﻦ #ٚ ٮ
و . ﺣ
ﺎ
ﯽ . ٮ
ک
ە # ٮ # ٮ
ﺷ ﯚ . ﺣ
ە . ٮ
و
ﻦ #ٚ ٮ
و . ﺣ
ەﻟ
ە و
ە . ٮ # ٮ ٚ ل ﯚ ﮑ #ٚ ٮ
ﻟ "
" ", "#FF6B6B"),
ک # ٮ . ٮ # ٮ
ﻠ
ک
یﺎ#ٮﻤ#ٮﮐ " ,"Clinical Chemistry"(
," ﯽ
"Chemical analysis of bodily fluids",
," شەﻟ
ﯽ.ٮﺎکەﻠﺷ
ﯽ#ٮﺎ#ٮﻤ#ٮﮐ
یەوە.ٮدﺮﮑ#ٮﺷ "
" ", "#4ECDC4"),
ﯚ ﻟ ﯚ # ٮ
ﺎ I ٮ
ﺎ
ۆ ر ﮑ # ٮ
ﻣ" ,"Microbiology"(
," ﯽ I ﺣ
"Study of microorganisms",
," نﺎکەﻣﺰ#ٮ.ٮﺎگرﯚﺋۆرﮑ#ٮﺎﻣ
ەﻟ
ە و
ە . ٮ # ٮ ٚ ل ﯚ ﮑ #ٚ ٮ
ﻟ "
" ", "#45B7D1"),
یرﮔرەIٮ " ,"Immunology"(
," ﯽﺳﺎ.ٮ
"Study of immune system",
," یرﮔرەIٮ
ﻣ ە % ٮ
ﯽ
ﺴ # ٮ
ﺳ
ەﻟ
ە و
ە . ٮ # ٮ ٚ ل ﯚ ﮑ #ٚ ٮ
ﻟ "
" ", "#96CEB4"),
نﯚﻣرﯚﻫ " ,"Endocrinology"(
," ﯽﺳﺎ.ٮ
"Study of hormones",
," نﺎکە.ٮﯚﻣرﯚﻫ
ەﻟ
ە و
ە . ٮ # ٮ ٚ ل ﯚ ﮑ #ٚ ٮ
ﻟ "
" ", "#FFEAA7"),
یەوە.ٮدﺮﮑ#ٮﺷ " ,"Urinalysis"(
," ﺰ#ٮﻣ
"Analysis of urine samples",
," ﺰ#ٮﻣ
یە.ٮووﻤ.ٮ
یەوە.ٮدﺮﮑ#ٮﺷ "
" ", "#DDA0DD"),
," نﺪ.ٮﺎ#ٮەﻣ " ,"Coagulation"(
"Blood clotting studies",
," ﻦ #ٚ ٮ
و . ﺣ
ﯽ.ٮﺪ.ٮﺎ#ٮەﻣ
ەﻟ
ە و
ە . ٮ # ٮ ٚ ل ﯚ ﮑ #ٚ ٮ
ﻟ "
" ", "#98D8C8"),
ﯽک.ٮﺎIٮ " ,"Blood Bank"(
," ﻦ #ٚ ٮ
و . ﺣ
"Blood transfusion services",
," ﻦ #ٚ ٮ
و . ﺣ
ی
ە و
ە . ٮ % ٮ
ﺳ ا و ﮔ
ﺎ
ﯽ . ٮ
ک
ە ي
ي ر ا ز و ﮕ % ٮ
ە ﻣ ﺰ . ﺣ "
" ", "#F7DC6F"),
]
for cat in categories:
try:
icon, color)
VALUES (?, ?, ?, ?, ?, ?)
""", cat)
except sqlite3.IntegrityError:
pass
conn.execute("""
INSERT INTO disease
_categories (name_en, name_ku, description_en, description_ku,
# Test Types
tests = [
یەرﺎﻣژ " ,"CBC"(
,"CBC)ﺣ
یواوە%ٮ
, "Hematolo", "cells/µL(,15.0 ,2.0 ,11.0 ,4.5
"Complete Blood Count",
," ﻦ #ٚ ٮ
و . ﺣ
یواوە%ٮ
یەرﺎﻣژ "
ي  #ٚ ٮ W ٮ " ,"No special preparaیرﺎکەدﺎﻣ,)25.0 ,"hours 2" ," ە#ٮ#ٮ.ٮ
ەIٮ
ﯽ % ٮ
ﺴ
("Hemoglobin", " ٮﯚﻠگﯚﻤ#ٮﻫIﻦي (Hb)", "Hematology", "g/dL",
,20.0 ,7.0 ,16.0 ,12.0
"Measures hemoglobin in blood",
," ﺖ #ٚ ٮ
ر و #ٚ ٮ W ٮ
ە د
ا
ﺪ . ٮ #ٚ ٮ
و . ﺣ
ەﻟ
ﻦيIٮﯚﻠگﯚﻤ#ٮﻫ
یڕIٮ "
ي و #ٚ ٮ W ٮ " ,"Fasting n,)15.0 ,"hour 1نووIٮوژۆڕەIٮ
ەIٮ
ﯽ % ٮ
ﺴ
ە . ٮ
ﺎ . ﺣ
یەرﺎﻣژ " ,"WBC Count"(
,"WBC)", "Hematology", "cells/µL( نﺎکە#ٮ#ٮWٮﺳ
,30000 ,2000 ,11000 ,4000
"White Blood Cell count",
," ﻦ #ٚ ٮو . ﺣ
ﯽ.ٮﺎکە#ٮ#ٮWٮﺳ
ە . ٮ
ﺎ . ﺣ
یەرﺎﻣژ "
," ﻦ #ٚ ٮ
و . ﺣ
ﯽ.ٮﺎکە#ٮ#ٮWٮﺳ
ە . ٮ
ﺎ . ﺣ
یەرﺎﻣژ "
يو #ٚ ٮ W ٮ " ,"No special ,)20.0 ,"hour 1" ," ە#ٮ#ٮ.ەIٮ
ﯽ % ٮ
ﺴ
یرﮐەﺷ " ,"Blood Glucose"(
,"FBS)ﺣ
, "Clinical Chemistry", g/dL(ٮ
,300 ,40 ,100 ,70
"Measures blood sugar levels",
," ﺖ #ٚ ٮ
ر و #ٚ ٮ W ٮ
ە د
ﻦ #ٚ ٮ
و . ﺣ
یرﮐەﺷ
ﯽ % ٮ
ﺳ ﺎ
ﺋ "
"Fast for 8-12 hours", " ووژۆڕەIٮ
ﺮ #ٚ ٮ
ﺎ
ﻣ ﮋ % ٮ
ک
١٢
٨-
,)20.0 ,"hours 2" ," ەIٮ
ﻫ " ,"HbA1c"(
,"%" ,"HbA1c)", "Clinical Chemistry( رادەﺮﮐەﺷ
ﯽ . ٮ
ي I ٮ
ﯚ ﻠ
گ ﯚ ﻤ # ٮ
,12.0 ,3.0 ,5.6 ,4.0
"Average blood sugar over 3 months",
," ﮓ.ٮﺎﻣ
٣
یەوﺎﻣ
ﯚIٮ
ﻦ #ٚ ٮ
و . ﺣ
یرﮐەﺷ
ی
ا ڕ
ﮑ #ٚ ٮ % ٮ "
ي و #ٚ ٮ W ٮ " ,"No fasti,)50.0 ,"hours 4نووIٮوژۆڕەIٮ
ەIٮ
ﯽ % ٮ
ﺴ
ي ر ﮐ " ,"Creatinine"(
,"r)", "Clinical ﺎ
Chemistry", "mg/ # ٮ . ٮ # ٮ % ٮ
,5.0 ,0.2 ,1.2 ,0.6
"Kidney function test",
," ە ﻠ # ٮ W ﺣ ر و ﮔ
یرﺎک
ﯽ . ٮ # ٮ . ٮ
ﮑ ﺸ W ٮ "
"Avoid heavy exercise 24h before", " س ر و % ڡ
ﺎ
ک
,)25.0 ,"hours 2" ," ەﮐەﻣ
ﯽﺷزرەو
ﺶ #ٚ ٮ W ٮ
ﺮ #ٚ ٮ
ﻣ ﮋ % ٮ
٢٤
یﺎيرو#ٮ " ,"Blood Urea"(
,"BUN)ﺣ
, "Clinical Chemistry", g/dL(ٮ
,50 ,3 ,20 ,7
"Kidney function test",
," ە ﻠ # ٮ W ﺣ ر و ﮔ
یرﺎک
ﯽ . ٮ # ٮ . ٮ
ﮑ ﺸ W ٮ "
يو #ٚ ٮ W ٮ " ,"No special ,)20.0 ,"hours 2" ," ە#ٮ#ٮ.ەIٮ
ﯽ % ٮ
ﺴ
ﻟ ﯚ ﮐ " ,"Cholesterol To,"Clinﺸ
ﮔ
ﯽ ٚ ل ۆ ڕﺴ # ٮ
ical Chemistry", "mg/dL""ﯽ % ٮ
,300 ,100 ,200 ,125
"Total blood cholesterol",
," ﻦ #ٚ ٮ
و . ﺣ
ﯽ ٚ ل ۆ ڕ % ٮ
ﺴ # ٮ
ﻟ ﯚ ﮐ
یﯚﮐ "
"Fast for 9-12 hours", " ﻦ#ٮ.ٮﻻەﺋ " ,"ALT"(
,"ALT), "Clinٮ
ﯚ . ٮ # ٮ
ﻣ ە ﺋ
ووڕەIٮ
ﺮ #ٚ ٮ
ﺎ
ﻣ ﮋ % ٮ
ک
١٢
٩-
,)35.0 ,"hours 3" ," ەIٮ
cal Chemistry", "U/L(,200 ,3 ,56 ,7
"Liver enzyme test",
," ر ە ﮕ I ﺣ
ﯽﻤيز.ٮەﺋ "
يو #ٚ ٮ W ٮ " ,"No special ,)25.0 ,"hours 2" ," ە#ٮ#ٮ.ەIٮ
ﯽ % ٮ
ﺴ
,"AST), "Clinٮ
ﺖە%ٮرﺎWٮﺳەﺋ " ,"AST"(
ﯚ . ٮ # ٮ
ﻣ ە ﺋ
cal Chemistry", "U/L(,200 ,5 ,40 ,10
"Liver and muscle enzyme test",
," ەﮑﻟﻮﺳﺎﻣ
ر ە ﮕ I ﺣ
و
ﯽﻤيز.ٮەﺋ
ﯽ . ٮ # ٮ . ٮ
ﮑ ﺸ W ٮ "
يو #ٚ ٮ W ٮ " ,"No special ,)25.0 ,"hours 2" ," ە#ٮ#ٮ.ەIٮ
ﯽ % ٮ
ﺴ
ۆ ڕ  ٮ " رە,"CRP)", "Immunology", "mg/L( ندﺮﮐوەﻫﯽ . ٮ # ٮ % ٮ
,100 ,0 ,5 ,0
"C-Reactive Protein",
," ندﺮﮐوەﻫ
ەﻟ
رەدرﺎک
ﯽ . ٮ # ٮ % ٮ
ۆ ڕ W ٮ "
يو #ٚ ٮ W ٮ " ,"No special ,)40.0 ,"hours 2" ," ە#ٮ#ٮ.ەIٮ
ﯽ % ٮ
ﺴ
ر ە ﯽ.ٮﯚﻣرﯚﻫ " ,"(
,"TSH)", "Endocrinology", "mIU/L( ﺪيۆر#ٮﺎ%ٮ
ی
ﮑﺎ W ﺣ
,50.0 ,0.1 ,4.0 ,0.4
"Thyroid Stimulating Hormone",
," ﺪيۆر#ٮﺎ%ٮ
ر ەی
 ﻻ
ﺎ W ﺣ
ﯽ.ٮﯚﻣرﯚﻫ "
یە.ٮووﻤ.ٮ " ,"Morning sample preferred"
,)60.0,"hoursﯽ.ٮﺷ ﺮ % ٮ " ,"Uri,"H)", "Urinalysis", "pHﯽ % ٮ #ٚ ٮ
,9.0 ,4.0 ,8.0 ,4.5
"Measures acidity of urine",
," ﺖ #ٚ ٮ
ر و #ٚ ٮ W ٮ
ە د
ﺰ#ٮﻣ
ﯽ % ٮ #ٚ ٮ
ﺷ ﺮ % ٮ "
,)10.0 ,"minuیە.ٮووﻤ.ٮ " ,"sh quiredﺴ
ي و #ٚ ٮ W ٮ
ەزﺎ%ٮ
tesﯽ%ٮﺎک " ,"PT"(
,"PT)", "Coagulation", "seconds( ﻦ#ٮIٮﻣۆر%ٮۆڕWٮ
,30 ,9 ,13.5 ,11
"Prothrombin Time",
," ﻦ#ٮIٮﻣۆر%ٮۆڕWٮ
ﯽ%ٮﺎک
"
ەژد " ,"Avoid anticoagulants if possib,)35.0 ,"hous 2"le,"B", "Serﯽﺎ o ف
یرەﮐاﺪ#ٮەWٮە " ,"HBsAg"(
ﺳ ۆ ر # ٮ
ﯽ
ﻫ ە ﻣ ر ﺎ
ک
ە I ٮ
نﺎکە.ٮﺪ.ٮﺎ#ٮەﻣ
ology", "qualitative,1 ,0 ,0 ,0
"Hepatitis B surface antigen test",
B",
ر ﯚ I ﺣ
ی
ر ە ﮕ I ﺣ
ی
ﯽ.ٮدﺮﮐوەﻫ
ﺳ ۆ ر # ٮ
ﯽ
ﺎ o ف
یرەﮐاﺪ#ٮەWٮەژد
ﯽ . ٮ # ٮ . ٮ
ﮑ ﺸ W ٮ "
يو #ٚ ٮ W ٮ " ,"No special ,)50.0 ,"hours 4" ," ە#ٮ#ٮ.ەIٮ
ﯽ % ٮ
ﺴ
]
for test in tests:
try:
conn.execute("""
INSERT INTO test
_types
(name_en, name_ku, category, unit, normal_range_low, normal_range_high,
critical
_low, critical_high, description_en, description_ku,
preparation_en, preparation_ku, turnaround_time, price)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", test)
except sqlite3.IntegrityError:
pass
# Diseases
diseases
_data = [
و . ﺤ  ە ﮐ " ,"Iron Deficiency ,یﯚﻫەIٮ
ﯽ . ٮ #ٚ ٮ
"Most common type of anemia caused by insufficient iron",
," ە و
ە . ٮ
ﺳ ﺎ
ﺋ
ﯽﻣەﮐ
یﯚﻫەIٮ
ﯽ . ٮ #ٚ ٮ
و . ﺤ ﻣ ە ﮐ
ر ﯚ I ﺣ
ی
ﻦ ي ر % ٮ W ٮ
ﺎ I ٮ
و
ﺎ I ٮ "
"Fatigue, Weakness, Pale skin, Shortness of breath, Dizziness",
," ە ﮋ #ٚ ٮ
ﮔ ر ە ﺳ
،یﺪ.ٮﻮ%ٮ
ەﺳﺎ.ٮەﻫ
،ڵﺎک
ﯽ % ٮ
ﺴ #ٚ ٮ W ٮ
،یزاوﻻ
،نووIٮوﺪ.ٮﺎﻣ "
"Poor diet, Blood loss, Pregnancy",
," ﯽ.ٮﺎ#ٮﮔوود
ﻦ #ٚ ٮ
،
و . ﺣ
ا
ﯽ . ٮ
ﺪ % ٮ
ﺳ ە د ە ﻟ
پ ا ر . ﺣ
،
ﯽ . ٮ
د ر ا و . ﺣ "
"Iron supplements, Iron-rich diet",
," ﻦﺳﺎﺋ
ەIٮ
ﺪ . ٮ
ە ﻣە د
ﯽ . ٮ
د ر ا و . ﺣ
،ﻦﺳﺎﺋ
یرەﮐواوە%ٮ "
"Mild to Severe"),
یﺮﮐەﺷ " ,"1 Diabetes Mellitus Typر ﯚ I ی
"Autoimmune destruction of insulin-producing cells",
," ﻦ # ٮ
ﺋ
ﻟ ﻮ ﺴ . ٮ # ٮ
ی
ر ە . ٮ #ٚ ٮ
ﻬ ﻣ ە ﻫ ر ە I ٮ
ﺎ
ﯽ . ٮ
ە . ٮ
ک
ﺎ . ﺣ
ر ﮔ ی
ە ٮ
ﯚ . ﺣ
ا
ﯽ . ٮ
ﮑ #ٚ ٮ % ٮ "
ﺪ
"Frequent urination, Excessive thirst, Weight loss, Fatigue",
," نووIٮوﺪ.ٮﺎﻣ
ﺶ #ٚ ٮ
،
ﮐ
ﯽ . ٮ
ا
ي ز ە I ٮ
د
،رۆز
ﯽ % ٮ
ە ي و . ٮ # ٮ % ٮ
،رۆز
یز#ٮﻣ "
"Autoimmune reaction, Genetic factors",
," نﺎکەي#ٮەوﺎﻣﯚIٮ
ەرﺎکﯚﻫ
،
ر ﮔ ی
ە ٮ
ﯚ . ﺣ
ﯽ
ک #ٚ ٮ
ﻟ ر ﺎ
ک
"
"Insulin therapy, Diet control",
," ن د ر ا و . ﺣ
ﯽ ٚ ل ۆ ڕ % ٮ . ٮ
ﯚ ﮐ
،
ﻦ # ٮ
ﺋ
ﻟ ﻮ ﺴ . ٮ # ٮ
ر ە ﺳ ە ر ﺎ W ﺣ "
ی
"Moderate to Severe"),
یﺮﮐەﺷ " ,"2 Diabetes Mellitus Typر ﯚ I ی
"Insulin resistance and relative insulin deficiency",
," ﻦ # ٮ
ﺋ
ﻟ ﻮ ﺴ . ٮ # ٮ
ﯽ#ٮەﮋ#ٚٮڕ
ﯽﻣەﮐ
و
ﻦ # ٮ
ﺋ
ﻟ ﻮ ﺴ . ٮ # ٮ
یرﮔرەIٮ "
"Slow-healing wounds, Numbness, Blurred vision, Fatigue",
," نووIٮوﺪ.ٮﺎﻣ
ﻦ # ٮ . ٮ
،
ي I ٮ
یژﻣﻮﻣە%ٮ
ﯽ% ٮ #ٮ
ﮐ
ڕ
،
ە و
ە . ٮ I ٮ
ە ﺪ
ﮐ ﺎ W ﺣ
ﺷ ا و #ٚ ٮ
ﯽ
ﻫ
ەIٮ
ﺎ
ﯽ . ٮ
ە . ٮ
ک
ي ر I ٮ "
"Obesity, Sedentary lifestyle, Genetic factors",
," نﺎکەي#ٮەوﺎﻣﯚIٮ
ەرﺎکﯚﻫ
ە ٚ ل ﻮ I ﺣ
،
ێIٮ
ﯽ.ٮﺎيژ
،
ی
ە ٚ ل ە % ڡ "
و
"Oral medications, Diet, Exercise",
," شزرەو
ﻢ # ٮ I ﺤ #ٚ ٮ
،
ڕ
،مەد
ﯽ.ٮﺎﻣرەد "
"Moderate"),
ﯽٮدﺮﮐوەﻫ " ,"Urinary Tract Infecیوەڕ#ٚٮ"Bacterial infection of urinary system",
," ﺰ#ٮﻣ
ﻣ ە % ٮ
ﯽ
ﺴ # ٮ
ﺳ
ﺎ
ﯽ # ٮ
ي ر % ٮ
ﮐ ە I ٮ
ﯽ.ٮدﺮﮐوەﻫ "
"Burning urination, Frequent urination, Cloudy urine, Pelvic pain",
," ە.ٮەﮔەﻟ
یرازﺎﺋ
،یواژﻣﻮﻣە%ٮ
یز#ٮﻣ
،رۆز
ﯽ.ٮدﺮﮐﺰ#ٮﻣ
ر ە . ٮ #ٚ ٮ % ٮ
،
و و ﺳ
ﯽ.ٮدﺮﮐﺰ#ٮﻣ "
"E. coli bacteria, Poor hygiene",
," پ ا ر . ﺣیژﮐﺎWٮ
،یﻻﯚﮑ#ٮﺋ
ی
ﺎ
ي ر % ٮ
ﮐ ە I ٮ "
," پ ا ر . ﺣ
یژﮐﺎWٮ
،یﻻﯚﮑ#ٮﺋ
ی
ﺎ
ي ر % ٮ
ﮐ ە I ٮ "
"Antibiotics, Increased fluids",
," ﺮ%ٮﺎيز
یەﻠﺷ
ن ﺎ
،
ک ﺎ
ي ر % ٮ
ﮐ ە I ٮ
ە ژ د "
"Mild to Moderate"),
ﺎ
ﯽ.ٮدﺮﮐوەﻫ " ,"Rheumatoid Arthritis" ,4(
ﯽ . ٮ
ک
ە ﮕ ﻣ ﻮ I ﺣ
," ﯽﻣﺰ#ٮ%ٮﺎﻣۆڕ
"Autoimmune disease causing joint inflammation",
ک
," ن ﺎ
ە ﮕ ﻣ ﻮ I ﺣ
ﯽ.ٮدﺮﮐوەﻫ
یﯚﻫ
ە % ٮ #ٚ ٮ I ٮ
ە د
ر ﮔ ی
ە ٮ
ﯚ . ﺣ
ﺷ ﯚ . ﺣ
ﯽ
ە . ٮ "
"Joint pain, Morning stiffness, Fatigue, Fever",
," ﺎ%ٮ
،نووIٮوﺪ.ٮﺎﻣ
،نﺎ#ٮ.ٮﺎ#ٮەIٮ
ﯽ . ٮ
و و I ٮ % ڡ
ە ڕ
ن ﺎ
،
ک
ە ﮕ ﻣ ﻮ I ﺣ
یرازﺎﺋ "
"Autoimmune reaction, Genetic factors",
," نﺎکەي#ٮەوﺎﻣﯚIٮ
ەرﺎکﯚﻫ
،
ر ﮔ ی
ە ٮ
ﯚ . ﺣ
ﯽ
ک #ٚ ٮ
ﻟ ر ﺎ
ک
"
"NSAIDs, Steroids, DMARDs",
," نﺎکە#ٮ#ٮﻣﺰ#ٮ%ٮﺎﻣۆڕ
ەژد
ە.ٮﺎﻣرەد
ن ﺎ
،
ک
ە ﺪ
ي ۆ ر % ٮ
ﺳ
،نﺎکە.ٮدﺮﮐوەﻫەژد "
"Moderate to Severe"),
یرﺎکﻣەﮐ " ,"Hypothyroidism" ,5(
," ﺪيۆر#ٮﺎ%ٮ
"Underactive thyroid gland",
," ﺪيۆر#ٮﺎ%ٮ
ﯽ . ٮ #ٚ ٮ
ژ ڕ
یرﺎکﻣەﮐ "
"Weight gain, Cold intolerance, Fatigue, Depression, Dry skin",
," ﮏﺷو
ﯽ % ٮ
ﺴ #ٚ ٮ W ٮ
،
ک ﯚ ﯽ
ە ﺣ
،نووIٮوﺪ.ٮﺎﻣ
،ﺎﻣرەﺳ
یەﮔرەIٮ
ﯽ . ٮ # ٮ . ٮ
ا و % ٮ
ە . ٮ
ﺶ #ٚ ٮ
،
ﮐ
ﯽ.ٮووIٮدﺎيز "
"Autoimmune disease, Iodine deficiency",
," دﯚ#ٮ
ﯽﻣەﮐ
،
ر ﮔ ی
ە ٮ
ﯚ . ﺣ
ﺷ ﯚ . ﺣ
ﯽ
ە . ٮ "
"Levothyroxine replacement therapy",
," ﻦ # ٮ
ﺴ
ﮐ ۆ ر # ٮ
ﺎ % ٮ
ﻟ
ﯚ z ڡ # ٮ
ی
ە و
ە ﺮ
ﮕ #ٚ ٮ I ﺣ
ر ە ﺳ ە ر ﺎ W ﺣ "
ی
"Moderate"),
]
for disease in diseases
_
data:
try:
conn.execute("""
INSERT INTO diseases
(category_id, name_en, name_ku, description_en, description_ku,
symptoms_en, symptoms_ku, causes_en, causes_ku, treatment_en, treatment_ku,
severity)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", disease)
except sqlite3.IntegrityError:
pass
# Practical Tests
practicals = [
ﯽ.ٮدﺮﮐەدﺎﻣﺎﺋ " ,"Blood Smear Preparation"(
," ﻦ #ٚ ٮ
و . ﺣ
ی
ر #ٚ ٮ
ﻤ ﺳ
"Preparation and staining of blood smear",
," ﻦ #ٚ ٮ
و . ﺣ
ی
ر #ٚ ٮ
ﻤ ﺳ
ﯽ.ٮدﺮﮑگ.ٮەڕ
و
ندﺮﮐەدﺎﻣﺎﺋ "
"Hematology",
"1. Clean slide with alcohol\n2. Place small drop of blood\n3. Use spreader slide at
30-45° angle\n4. Quick smooth motion to spread\n5. Air dry completely\n6. Fix with methanol\n7.
Stain with Wright's stain\n8. Wash and dry\n9. Examine under microscope",
٤٥ -٣٠
یەﺷﯚﮔ
ەIٮ
ەوەرەﮐوﺎڵIٮ
یﺪ#ٮﻼﺳ .
ا
n٣\ ێ . ٮ I ٮ
د
ﻦ #ٚ ٮ
و . ﺣ
ک و و W ﺤ I ٮ
ﯽ
ﯽ
ک #ٚ ٮ
پ ﯚ ٚ ل د .
\n٢
ەوەرەﮑIٮ
کﺎWٮ
لوﺤﮑﻟەﺋ
ەIٮ
ﺪ#ٮﻼﺳ . ١ "
ەIٮ
.
n٧\ ەﮑIٮ
ﺮ # ٮ
ﮕ #ٚ ٮ I ﺣ
لﯚ.ٮﺎﺴ#ٮﻣ
ەIٮ
.
\n٦
ەوەرەﮑIٮ
ﮏﺷو
یواوە%ٮ
ەIٮ
.
\n٥
ەوﺎڵIٮيIٮ
مرە.ٮ
و
ا ر #ٚ ٮ . ﺣ
ﯽ
ک
ە # ٮ
ە ٚ ل ﻮ I ﺣ
ەIٮ
.
n٤\ ە . ٮ #ٚ ٮ
ﻬ I ٮ
ر ﺎ
ک
ە I ٮ
ەﻠWٮ
," ەﮑIٮ
ﻦ # ٮ . ٮ
ﮑ ﺸ W ٮ
پﯚﮑﺳۆرﮑ#ٮﺎﻣ
ﺮ#ٚٮژ
ەﻟ .
\n٩
ەوەرەﮑIٮ
ﯽکﺷو
و
ﯚﺸيIٮ
.
n٨\ ەﮑIٮ
ﯽگ.ٮەڕ
ﺖ#ٮار
ﯽگ.ٮەڕ
"Glass slides, Blood sample, Spreader slide, Methanol, Wright's stain, Microscope",
," پﯚﮑﺳۆرﮑ#ٮﺎﻣ
،ﺖ#ٮار
ﯽگ.ٮەڕ
،لﯚ.ٮﺎﺴ#ٮﻣ
،ەوەرەﮐوﺎڵIٮ
یﺪ#ٮﻼﺳ
ﻦ #ٚ ٮ
،
و . ﺣ
یە.ٮووﻤ.ٮ
،ﯽ#ٮەﺷووﺷ
یﺪ#ٮﻼﺳ "
"Evenly distributed blood cells",
," ەوە%ٮە.ٮوارﮐوﺎڵIٮ
ﯽ.ٮﺎﺴﮐە#ٮ
ەIٮ
ﻦ #ٚ ٮ
و . ﺣ
ﺎ
ﯽ . ٮ
ە . ٮ
ک
ﺎ . ﺣ "
"Check RBC morphology, WBC differential",
," نﺎکە#ٮ#ٮWٮﺳ
ە . ٮ
ﺎ . ﺣ
ی
ر ﺎ
ک ﺎ # ٮ I ﺣ
،نﺎکەرووﺳ
ە ﮐ ۆ ڕ . ﺣ
ی
ە ﻮ #ٚ ٮ
ﺷ "
"Avoid air bubbles, Use fresh blood",
," ەزﺎ%ٮ
ﯽ . ٮ #ٚ ٮ
و . ﺣ
ﯽ . ٮ
ﺎ . ٮ #ٚ ٮ
ﻫ ر ﺎ
ک
ە I ٮ
،اوەﻫ
ﺎ
ﯽ . ٮ
ە % ڡ
ک
ڵ I ٮ
ەﻟ
ە و
ە . ٮ % ٮ
ە ﮐو
ر30, "Basic"),
ﯽ.ٮدﺮﮑگ.ٮەڕ " ,"Gram Staining"(
," مارﮔ
"Differential staining technique for bacteria",
," ﺎ
ي ر % ٮ
ﮐ ە I ٮ
ﯽ . ٮ
د ﺮ
ﮑ . ٮ #ٚ ٮ
ﻟ ﯚ W ٮ
ﯚIٮ
ر ﺎ
ک ﺎ # ٮ I ﺣ
ﯽ.ٮدﺮﮑگ.ٮەڕ
ﯽ
ک # ٮ . ٮ
ﮐ ە % ٮ "
"Microbiology",
"1. Prepare bacterial smear\n2. Heat fix\n3. Crystal violet - 1 minute\n4. Wash with
water\n5. Gram's iodine - 1 minute\n6. Wash with water\n7. Decolorize with alcohol\n8. Wash
immediately\n9. Safranin counterstain - 30 sec\n10. Wash, dry, examine",
.
\n٥
ﯚﺸيIٮ
وﺎﺋ
ەIٮ
.
n٤\ ک ە ﻟ ﻮ . ﺣ
١ -
ﺖ #ٚ ٮ
ﻟ ﯚ # ٮ
ﺎ o ف
ڵ ﺎ % ٮ
ﺴ
ي ر ﮐ .
n٣\ ەﮑIٮ
ﺮ # ٮ
ﮕ #ٚ ٮ I ﺣ
ﯽﻣرەﮔ
ەIٮ
.
n٢\ ەﮑIٮ
ەدﺎﻣﺎﺋ
ﺎ
ي ر % ٮ
ﮐ ە I ٮ
ی
ر #ٚ ٮ
ﻤ ﺳ . ١ "
.
n١٠\ ە ﮐ ﺮ W ﺣ
٣٠ -
ﻦ # ٮ . ٮ
ا ر . ڡ
ە ﺳ .
\n٩
ﯚﺸيIٮ
رەﺴﮐە#ٮ
.
\n٨
ەوەرەIٮ
ێﻟ
ﮓ.ٮەڕ
لوﺤﮑﻟەﺋ
ەIٮ
.
\n٧
ﯚﺸيIٮ
وﺎﺋ
ەIٮ
.
n٦\ ک ە ﻟ ﻮ . ﺣ
١ - مارﮔ
یدﯚ#ٮ
," ەﮑIٮ
ﻦ # ٮ . ٮ
ﮑ ﺸ W ٮ
،ەوەرەﮑIٮ
ﮏﺷو
،ﯚﺸيIٮ
"Bacterial culture, Crystal violet, Iodine, Alcohol, Safranin, Microscope",
," پﯚﮑﺳۆرﮑ#ٮﺎﻣ
ﻦ # ٮ . ٮ
،
ا ر . ڡ
ە ﺳ
،لوﺤﮑﻟەﺋ
،دﯚ#ٮ
ﺖ #ٚ ٮ
،
ﻟ ﯚ # ٮ
ﺎ o ف
ڵ ﺎ % ٮ
ﺴ
ي ر ﮐ
ي ر % ٮ
،
ﺎ
ﮐ ە I ٮ
ی
ر و و % ٮ
ﻟ ە ﮐ "
"Gram-positive: Purple, Gram-negative: Pink/Red",
," رووﺳ / ﯽ#ٮەﻣەWٮ
: ﭫ # ٮ % ٮ
ە ﮕ #ٚ ٮ . ٮ
مارﮔ
،ﯽ#ٮەﺷوە.ٮەو
: ﭫ#ٮ%ٮەزﯚWٮ
مارﮔ "
"Bacterial classification",
," ﺎ
ي ر % ٮ
ﮐ ە I ٮ
ﯽ . ٮ
د ﺮ
ﮑ . ٮ #ٚ ٮ
ﻟ ﯚ W ٮ "
"Don't over-decolorize, Use fresh cultures",
," ە . ٮ #ٚ ٮﻬ I ٮ
ر ﺎ
ک
ە I ٮ
ەزﺎ%ٮ
ی
ر و و % ٮ
ﻟ ە ﮐ
،ەوەرەIٮەﻣ
ێﻟ
ﮓ.ٮەڕ
رۆز "
," ە . ٮ #ٚ ٮ
ﻬ I ٮ
ر ﺎ
ک
ە I ٮ
ەزﺎ%ٮ
ی
ر و و % ٮ
ﻟ ە ﮐ
،ەوەرەIٮەﻣ
ێﻟ
ﮓ.ٮەڕ
رۆز "
45, "Intermediate"),
یەوە.ٮدﺮﮑ#ٮﺷ " ,"Urine Dipstick Analysis"(
," ﺰ#ٮﻣ
ﯽ
ک # ٮ % ٮ
ﺴ
پ # ٮ
د
"Rapid screening test for urine",
," ﺰ#ٮﻣ
ﺎ
ﯽ . ٮ
ە % ٮ
ک
ﺎ
ﻬ ﮑ #ٚ ٮ W ٮ
ﯚIٮ
ﻦ # ٮ . ٮ
ﮑ ﺸ W ٮ
ی
ا ر #ٚ ٮ . ﺣ
ﯽ . ٮ # ٮ . ٮ
ﮑ ﺸ W ٮ "
"Urinalysis",
"1. Collect fresh urine sample\n2. Dip test strip briefly\n3. Remove excess urine\n4.
Compare to color chart\n5. Record results",
ەIٮ
دروارەIٮ
.
n٤\ ەرەIٮﻻ
ەدﺎيز
یز#ٮﻣ .
n٣\ ەﮑIٮ
ﻢ % ڡ ﻮ . ٮ
ﯽ%ٮروﮐ
ەIٮ
ﻦ # ٮ . ٮ
ﮑ ﺸ W ٮ
ﯽ % ٮ
ي ر ﺷ .
\n٢
ەوەرەﮑIٮﯚﮐ
ەزﺎ%ٮ
یز#ٮﻣ
یە.ٮووﻤ.ٮ
. ١ "
," ەﮑIٮ
رﺎﻣﯚ%ٮ
ک
ن ﺎ
ە ﻣ ﺎ I ﺤ . ٮ
ە ﺋ
.
n٥\ نﺎکەﮕ.ٮەڕ
ی
ر ﺎ
ک ڵ #ٚ ٮ
ﻫ
"Urine sample, Dipstick strips, Color chart, Timer",
," ﺮ #ٚ ٮ
ﺎ
ﻣ ﮋ % ٮ
ک
،ﮓ.ٮەڕ
ی
ر ﺎ
ک ڵ #ٚ ٮ
ﻫ
ﮏ # ٮ % ٮ
،
ﺴ
پ # ٮ
د
ﺎ
ﯽ . ٮ
ە % ٮ
ک
ي ر ﺷ
،ﺰ#ٮﻣ
یە.ٮووﻤ.ٮ "
"Color changes indicating urine components",
," تادەد
نﺎﺸ#ٮ.ٮ
ﺰ#ٮﻣ
ﺎ
ﯽ . ٮ
ک
ە ز ا و
ﺎ # ٮ I ﺣ
ە % ٮ
ﺎ
ﻬ ﮑ #ٚ ٮ W ٮ
نﺎکەﮕ.ٮەڕ
ﯽ.ٮاڕﯚﮔ "
"pH, Protein, Glucose, Ketones, Blood",
," ﻦ #ٚ ٮ
و . ﺣ
ن ﺎ
،
ە . ٮ
ک
ﯚ % ٮ # ٮ
ﮐ
،ﺮﮐەﺷ
،ﻦ#ٮ%ٮۆرWٮ
ﯽ % ٮ #ٚ ٮ
،
ﺷ ﺮ % ٮ "
"Check expiration date, Proper timing",
," و
ﺎ I ﺤ . ٮ
ﻮ ﮔ
ﯽ%ٮﺎک
ە . ٮ
ﮑ ﺸ
،
پ I ٮ
ن و و W ﺣ ر ە ﺳ ە I ٮ
یراورەIٮ "
15, "Basic"),
ﮑ ﺸ W ٮ " ,"Blood Group Te,"و . ﺣ
ﯽپورﮔ
ﯽ . ٮ # ٮ . ٮ
"ABO and Rh blood group determination",
Rh",
و ABO
ﯽ . ٮ #ٚ ٮ
و . ﺣ
ﯽپورﮔ
ﯽ.ٮدﺮﮑيرﺎ#ٮد "
"Blood Bank",
"1. Prepare clean slide with 3 sections\n2. Add anti-A, anti-B, anti-D reagents\n3. Add
blood drop to each section\n4. Mix with clean stick\n5. Rock slide gently\n6. Observe
agglutination within 2 minutes",
ﯚIٮ
ﻦ #ٚ ٮ
و . ﺣ
ی
ە پ ﯚ ٚ ل د .
n٣\ ەﮑIٮ
دﺎيز D- ەژد
،B- ەژد
،A- ەژد
ﺎ
ﯽ . ٮ
ک
ە ر ە ﮑ ک #ٚ ٮ
ﻟ ر ﺎ
ک
.
n٢\ ەﮑIٮ
ەدﺎﻣﺎﺋ
شەIٮ
٣
ەIٮ
کﺎWٮ
یﺪ#ٮﻼﺳ . ١ "
ا
ﮐ ەﻟ . ﺣ
٢
یەوﺎﻣ
ەﻟ
ە و
ە . ٮ
و و I ٮ
ڕ W ﺣ .
n٦\ ە . ٮ #ٚ ٮ ٚ ل ﻮ I ﺤ I ٮ
ﯽﻣرە.ٮ
ەIٮ
ەﮐەﺪ#ٮﻼﺳ .
n٥\ ەﮑIٮ
ڵ ە ﮑ #ٚ ٮ % ٮ
کﺎWٮ
یراد
ەIٮ
.
n٤\ ەﮑIٮ
دﺎيز
ﮏ #ٚ ٮ
ﺷ ە I ٮ
رەﻫ
," ەﮑIٮ
ی
ر #ٚ ٮ
د و
ﺎ W ﺣ
"Clean slide, Anti-A, Anti-B, Anti-D reagents, Blood sample, Mixing sticks",
," ن د ﺮ
ﮑ ٚ ل ە ﮑ #ٚ ٮ % ٮ
یراد
ﻦ #ٚ ٮ
،
و . ﺣ
یە.ٮووﻤ.ٮ
،D- ەژد
،B- ەژد
،A- ەژد
ر ە ﮑ ک #ٚ ٮ
ی
ﻟ ر ﺎ
ک
،کﺎWٮ
یﺪ#ٮﻼﺳ "
"Agglutination pattern determines blood group",
," تﺎکەد
یرﺎ#ٮد
ﻦ #ٚ ٮ
و . ﺣ
ﯽپورﮔ
ە و
ە . ٮ
و و I ٮ
ڕ W ﺣ
ی
ز ا و #ٚ ٮ
ﺷ "
"A, B, AB, O groups with Rh positive/negative",
," ﭫ # ٮ % ٮ
ە ﮕ #ٚ ٮ . ٮ
/ ﭫ#ٮ%ٮەزﯚWٮ Rh
ڵەﮔەﻟ A، B، AB، O
ﯽ.ٮﺎکەپورﮔ "
"Use fresh blood, Check reagent expiry",
," ە . ٮ
ﮑ ﺸ
پ I ٮ
ر ە ﮑ ک #ٚ ٮ
ﻟ ر ﺎ
ک
ﯽ . ٮ
و و W ﺣ ر ە ﺳ ە I ٮ
یراورەIٮ
ە . ٮ #ٚ ٮ
،
ﻬ I ٮ
ر ﺎ
ک
ە I ٮ
ەزﺎ%ٮ
ﯽ . ٮ #ٚ ٮ
و . ﺣ "
20, "Basic")
]
for practical in practicals:
try:
conn.execute("""
INSERT INTO practical_
tests
(title_en, title_ku, description_en, description_ku, category,
steps_en, steps_ku, materials_en, materials_ku,
expected_
results
_en, expected_
results
_ku,
interpretation_en, interpretation_ku,
precautions_en, precautions_ku,
duration
_minutes, difficulty_level)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", practical)
except sqlite3.IntegrityError:
pass
# Study Notes
notes = [
("Hematology Basics", "CBC Interpretation:\n\nRBC: 4.5-5.5 million/µL\nWBC:
4,000-11,000/µL\nPlatelets: 150,000-450,000/µL\nHemoglobin: 12-16 g/dL\nHematocrit:
37-47%", "Hematology", "CBC, blood, basic"),
("Diabetes Diagnosis", "Diagnostic criteria:\n\nFBS ≥ 126 mg/dL\nHbA1c ≥ 6.5%\nOGTT
2-hour ≥ 200 mg/dL\nRandom glucose ≥ 200 mg/dL with symptoms", "Clinical Chemistry",
"diabetes, glucose, diagnosis"),
("Gram Staining Principle", "Gram-positive bacteria: Thick peptidoglycan layer retains
crystal violet\n\nGram-negative bacteria: Thin peptidoglycan, outer membrane, lose crystal
violet", "Microbiology", "gram stain, bacteria"),
]
for note in notes:
conn.execute("""
INSERT INTO study_notes (topic, content, category, tags)
VALUES (?, ?, ?, ?)
""", note)
conn.commit()
except Exception as e:
conn.rollback()
# Insert data
insert
_comprehensive_data(conn)
# ==================== Translation System ====================
def t(key):
"""Translation system"""
translations = {
} :"
یدروﮐ "
," درﯚIٮﺷاد " :"dashboard"
"disease
ک
ە . ٮ " :"db
_
," ن ﺎ
ە # ٮ # ٮ
ﺷ ﯚ . ﺣ
"lab
_
ﮑ ﺸ Wٮ " ,ە . ٮ # ٮ . ٮ
ﮐ ا ر W ٮ " :"p," ﯽ
ە # ٮ # ٮ ک
ٮ # ٮ I ٮ #ٚ ٮ % ٮ ""theory"
," ن ﺎ
"results
ک
ە ﻣ ﺎ I ﺤ . ٮ
ە ﺋ " :"entry_
," ن ﺎ
," ترﯚWٮاڕ " :"reports"
"ai
ﮑ % ٮ
_
ﯽکەﺮيز " :"chat
ﺳ ە د
," د ﺮ
," ەوە.ٮدﺮﮑ.ٮووڕ " :"description"
," نﺎکە.ٮﺎﺸ#ٮ.ٮ " :"symptoms"
," نﺎکەرﺎکﯚﻫ " :"causes"
," ر ە ﺳ ە ر ﺎ W ﺣ " :"treatment"
," یﺪ.ٮﻮ%ٮ " :"severity"
"normal
یادوەﻣ " :"range_
," ﯽ#ٮﺎﺳﺎﺋ
"critical
_
یﺎﻫەIٮ " :"values
," راﺪ#ٮﺳﺮ%ٮەﻣ
," مﺰ.ٮ " :"low"
," زرەIٮ " :"high"
," ەﮐە#ٮ " :"unit"
," ک ە ﻟ ﻮ . ﺣ " :"minutes"
," نﺎکەوﺎگ.ٮەﻫ " :"procedure"
ﺳەر ە ﮐ " :"m"
," ن ﺎ
"expected_
ە ﺋ " :"results
ا ر ﮑ . ٮ
," و
ا و ﺣ
ڕﻣ ﺎ I ﺤ . ٮ
ﯽ
ە . ٮ
ا
ﻟ " :"interpretation"
," ە و
ﮑ #ٚ ٮ
ﺪ
ﮕ ﺸ ٚٮ W ٮ " :","د ﺮ
ﮑ ي ر # ٮ
"save
_
," ندﺮﮐرﺎﻣﯚ%ٮ " :"note
"saved
_
ﯽيوو%ٮوەﮐرەﺳەIٮ " :"success
," ! ارﮐرﺎﻣﯚ%ٮ
"patient_
ە . ٮ
یوﺎ.ٮ " :"name
," ش ﯚ . ﺣ
"patient_
ە . ٮ
یوﺎ.ٮ " :"name
," ش ﯚ . ﺣ
," نەﻣە%ٮ " :"patient_age"
," زەﮔەڕ " :"patient_gender"
"select
_
ﮑ ﺸ W ٮ "ژ I ٮ ," ە ﺮ #ٚ ٮ
ﻦ # ٮ . ٮ
"result
ە ﺋ " :"value
_
," م ﺎ I ﺤ . ٮ
"save
_
ﯽ.ٮدﺮﮐرﺎﻣﯚ%ٮ " :"result
," م ﺎ I ﺤ .ە"ask
_
رﺎ#ٮﺳﺮWٮ " :"ai
," ەﮑIٮ
,"... ە ﺳ و و . تەﮐەرﺎ#ٮﺳﺮWٮ " :"_question,"... ناڕەﮔ " :"search"
ﻠ . ڡ " :"filter"
," ر ە % ٮ
," ووﻣەﻫ " :"all"
," ندﺮﮐەدرﺎ.ٮەﻫ " :"export"
ﺎ W ﺣ " :"print"
," ن د ﺮ
ﮑ W ٮ
ﺳ " :"delete"
ە . ٮ
," ە و
ي ڕ
ﺳ ە د " :"edit"
ر ﺎ
ک % ٮ
," ی
ي I ٮ " :"view"
," ﻦ # ٮ . ٮ
," نﺎکەييرﺎکەدرو " :"details"
," شەIٮ " :"category"
ﺳ ر و % ڡ
ﺋ " :"difficulty"
," ﯽ
ﯽ % ٮ
ﺳ ﺎ
," ەوﺎﻣ " :"duration"
,}
"English ": {
"dashboard": " Dashboard",
"disease
_
db": " Disease Database",
"lab
_
tests": " Laboratory Tests",
"practical": " Practical Tests",
"theory": " Study Notes",
"results
_entry": " Results Entry",
"reports": " Reports",
"ai
_
chat": " AI Assistant",
"description": "Description",
"symptoms": "Symptoms",
"causes": "Causes",
"treatment": "Treatment",
"severity": "Severity",
"normal
_range": "Normal Range",
"critical
_values": "Critical Values",
"low": "Low",
"high": "High",
"unit": "Unit",
"minutes": "minutes",
"procedure": "Procedure Steps",
"materials": "Required Materials",
"expected_results": "Expected Results",
"interpretation": "Interpretation",
"precautions": "Precautions",
"save
_note": "Save Note",
"saved
_success": "Saved successfully! ",
"patient_name": "Patient Name",
"patient_age": "Age",
"patient_gender": "Gender",
"select
_test": "Select Test",
"result
_value": "Result Value",
"save
_result": "Save Result",
"ask
_ai": "Ask AI",
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
"category": "Category",
"difficulty": "Difficulty Level",
"duration": "Duration",
}
}
)" یدروﮐ " ,"lang = st.session_state.get("language
return translations.get(lang, {}).get(key, key)
def get_name(row, prefix="name"):
"""Get localized name from database row"""
lang_map = {
"English ": "en",
": "ku"
یدروﮐ "
}
lang = lang_map.get(st.session_state.get("language", " یدروﮐ "), "ku")
field = f"{prefix}_{lang}"
if isinstance(row, dict):
return row.get(field, row.get(f"{prefix}_en", ""))
else:
try:
return row[field]
except:
try:
return row[f"{prefix}_en"]
except:
return str(row)
def get_desc(row):
"""Get localized description"""
return get_name(row, "description")
# ==================== AI Responses ====================
def get_
ai
_response(question):
"""Get AI response for medical questions"""
q = question.lower()
if "cbc" in q or "complete blood count" in q:
return """**CBC (Complete Blood Count)** is a comprehensive blood test that measures:
- **Red Blood Cells (RBC)**: Oxygen carriers (4.5-5.5 million/µL)
- **White Blood Cells (WBC)**: Immune system cells (4,000-11,000/µL)
- **Hemoglobin**: Oxygen-carrying protein (12-16 g/dL)
- **Hematocrit**: Percentage of red blood cells (37-47%)
- **Platelets**: Blood clotting cells (150,000-450,000/µL)
Normal ranges vary by age and gender. Always consult your healthcare provider for
interpretation."""
elif "glucose" in q or "sugar" in q or "diabetes" in q:
return """**Blood Glucose Test** measures blood sugar levels:
- **Fasting**: 70-100 mg/dL (normal)
- **Pre-diabetes**: 100-125 mg/dL
- **Diabetes**: 126 mg/dL or higher
**HbA1c** provides 3-month average:
- Normal: Below 5.7%
- Pre-diabetes: 5.7-6.4%
- Diabetes: 6.5% or higher"""
elif "anemia" in q or "hemoglobin" in q:
return """**Anemia** is a condition where you lack enough healthy red blood cells:
Common types:
- **Iron Deficiency Anemia**: Most common, caused by insufficient iron
- **Vitamin B12 Deficiency**: Pernicious anemia
- **Thalassemia**: Genetic disorder affecting hemoglobin
Symptoms: Fatigue, weakness, pale skin, shortness of breath"""
return "Please ask a medical laboratory related question. I can help with test interpretation,
disease information, and lab procedures."
# ==================== Dashboard ====================
def render
_dashboard():
"""Dashboard page"""
if conn is None:
st.error(" Database connection failed")
return
st.markdown("""
<div class="main-header">
<h1> ٮﺷادIدرﯚ </h1>
<p>Overview of Medical Laboratory System</p>
</div>
""", unsafe_
allow
_html=True)
try:
col1, col2, col3, col4 = st.columns(4)
with col1:
cat
_count = conn.execute("SELECT COUNT(*) as c FROM
disease
_categories").fetchone()['c']
st.markdown(f"""
<div class="stat-card">
<h2 style="color: #FF6B6B;">{cat_count}</h2>
<p> Categories</p>
</div>
""", unsafe_
allow
_html=True)
with col2:
test
_count = conn.execute("SELECT COUNT(*) as c FROM test_types").fetchone()['c']
st.markdown(f"""
<div class="stat-card">
<h2 style="color: #4ECDC4;">{test_count}</h2>
<p> Lab Tests</p>
</div>
""", unsafe_
allow
_html=True)
with col3:
disease
_count = conn.execute("SELECT COUNT(*) as c FROM diseases").fetchone()['c']
st.markdown(f"""
<div class="stat-card">
<h2 style="color: #45B7D1;">{disease_count}</h2>
<p> Diseases</p>
</div>
""", unsafe_
allow
_html=True)
with col4:
practical_count = conn.execute("SELECT COUNT(*) as c FROM
practical_tests").fetchone()['c']
st.markdown(f"""
<div class="stat-card">
<h2 style="color: #96CEB4;">{practical_count}</h2>
<p> Practical Tests</p>
</div>
""", unsafe_
allow
_html=True)
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
st.markdown("### Tests by Category")
test
_dist = conn.execute("""
SELECT category, COUNT(*) as count
FROM test
_types
GROUP BY category
ORDER BY count DESC
""").fetchall()
if test
dist:
_
df
_dist = pd.DataFrame([dict(r) for r in test_dist])
fig = px.pie(df_dist, values='count', names='category',
color
discrete
_
_sequence=px.colors.qualitative.Set3)
fig.update_traces(textposition='inside', textinfo='percent+label')
fig.update_layout(height=350)
st.plotly_chart(fig, use_
container
_width=True)
with col2:
st.markdown("### Disease Severity")
severity_data = conn.execute("""
SELECT severity, COUNT(*) as count
FROM diseases
GROUP BY severity
""").fetchall()
if severity_
data:
df
_severity = pd.DataFrame([dict(r) for r in severity_data])
fig = px.bar(df_severity, x='severity', y='count',
color='severity',
color
discrete
_
_sequence=px.colors.qualitative.Set2)
fig.update_layout(height=350)
st.plotly_chart(fig, use_
container
_width=True)
except Exception as e:
st.error(f"Dashboard Error: {str(e)}")
# ==================== Diseases Module ====================
def render
_diseases():
"""Disease database page"""
if conn is None:
return
st.markdown("""
<div class="main-header">
ک
ە . ٮ >h1<
>h1/< ن ﺎ
ە # ٮ # ٮ
ﺷ ﯚ . ﺣ
<p>Medical Disease Database</p>
</div>
""", unsafe_
allow
_html=True)
try:
col1, col2 = st.columns([2, 1])
with col1:
search
_query = st.text_input(t('search'), placeholder="Search diseases...")
with col2:
categories = conn.execute("SELECT id, name_en, name_
ku FROM
disease
_categories").fetchall()
category_options = {"All": None}
for cat in categories:
name = get_name(dict(cat))
category_options[name] = cat['id']
selected
_category = st.selectbox(t('filter'), list(category_options.keys()))
query = """
SELECT d.*, dc.name_
en as cat
_en, dc.name_
ku as cat
_ku, dc.icon, dc.color
FROM diseases d
JOIN disease
_categories dc ON d.category_
id = dc.id
WHERE 1=1
"""
params = []
if search
_query:
query += " AND (d.name_
en LIKE ? OR d.name
_
ku LIKE ? OR d.symptoms_
en LIKE ? OR
d.symptoms_
ku LIKE ?)"
search
_term = f"%{search_query}%"
params.extend([search_term, search_term, search_term, search_term])
if category_options[selected_category]:
query += " AND d.category_
id = ?"
params.append(category_options[selected_category])
query += " ORDER BY d.severity DESC, d.name_
en"
diseases = conn.execute(query, params).fetchall()
st.markdown(f"### Found: {len(diseases)} diseases")
for i in range(0, len(diseases), 2):
cols = st.columns(2)
for j in range(2):
if i + j < len(diseases):
disease = dict(diseases[i + j])
with cols[j]:
with st.container():
st.markdown(f"""
<div class="category-card" style="border-right-color: {disease.get('color',
'#1565c0')};">
<h4>{disease.get('icon', ' ')} {get_name(disease)}</h4>
<p><strong>{t('category')}:</strong> {get_name(disease, 'cat')}</p>
<p><strong>{t('severity')}:</strong> {disease['severity']}</p>
</div>
""", unsafe_
allow
_html=True)
with st.expander(f"{t('details')} - {get_name(disease)}"):
st.markdown(f"#### {t('description')}")
st.write(get_desc(disease))
st.markdown(f"#### {t('symptoms')}")
symptoms = get_name(disease, 'symptoms')
if symptoms:
symptom_list = [s.strip() for s in symptoms.split(',') if s.strip()]
for s in symptom_
list:
st.markdown(f"<span class='symptom-tag'>{s}</span>",
unsafe
allow
_
_html=True)
if disease.get('causes_en') or disease.get('causes_ku'):
st.markdown(f"#### {t('causes')}")
st.write(get_name(disease, 'causes'))
if disease.get('treatment_en') or disease.get('treatment_ku'):
st.markdown(f"#### {t('treatment')}")
st.write(get_name(disease, 'treatment'))
except Exception as e:
st.error(f"Disease Database Error: {str(e)}")
# ==================== Tests Module ====================
def render
_tests():
"""Laboratory tests page"""
if conn is None:
return
st.markdown("""
<div class="main-header">
ک
ﮑ ﺸ W ٮ >h1<
>h1/< ن ﺎە . ٮ # ٮ . ٮ
<p>Laboratory Test Reference Guide</p>
</div>
""", unsafe_
allow
_html=True)
try:
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
search
test = st.text
_
_input(t('search'), placeholder="Search by name or category...")
with col2:
categories = conn.execute("SELECT DISTINCT category FROM test_types ORDER BY
category").fetchall()
category_list = ["All"] + [c['category'] for c in categories]
selected
_cat = st.selectbox(t('category'), category_list)
with col3:
sort
_by = st.selectbox("Sort by", ["Name", "Category", "Price"])
query = "SELECT * FROM test_types WHERE 1=1"
params = []
if search
test:
_
query += " AND (name_
en LIKE ? OR name
_
ku LIKE ? OR category LIKE ?)"
search
_term = f"%{search_test}%"
params.extend([search_term, search_term, search_term])
if selected
cat != "All":
_
query += " AND category = ?"
params.append(selected_cat)
if sort
_by == "Name":
query += " ORDER BY name_
en"
elif sort
_by == "Category":
query += " ORDER BY category, name_
en"
elif sort
_by == "Price":
query += " ORDER BY price"
tests = conn.execute(query, params).fetchall()
st.markdown(f"### Found: {len(tests)} tests")
tests
_by_category = {}
for test in tests:
cat = test['category']
if cat not in tests
_by_category:
tests
_by_category[cat] = []
tests
_by_category[cat].append(dict(test))
for category, category_
tests in tests
_by_category.items():
with st.expander(f" {category} ({len(category_tests)} tests)", expanded=True):
for test in category_
tests:
st.markdown(f"""
<div class="info-box">
<h4> {get_name(test)}</h4>
<p><strong>{t('unit')}:</strong> {test['unit']} |
<strong>Price:</strong> ${test.get('price', 'N/A')} |
<strong>Turnaround:</strong> {test.get('turnaround_time', 'N/A')}</p>
<p><strong class="normal-range">{t('normal_range')}:
{test['normal_range_low']} - {test['normal_range_high']} {test['unit']}</strong></p>
</div>
""", unsafe_
allow
_html=True)
with st.expander(f"More details for {get_name(test)}"):
st.markdown(f"#### {t('description')}")
st.write(get_desc(test))
if test.get('preparation_en') or test.get('preparation_ku'):
st.markdown(f"#### Patient Preparation")
st.info(get_name(test, 'preparation'))
st.markdown(f"#### {t('critical_values')}")
st.markdown(f"""
<div class="critical-box">
<p> <strong>{t('low')}:</strong> < {test['critical_low']} {test['unit']}</p>
<p> <strong>{t('high')}:</strong> > {test['critical_high']} {test['unit']}</p>
</div>
""", unsafe_
allow
_html=True)
except Exception as e:
st.error(f"Tests Display Error: {str(e)}")
# ==================== Practical Tests Module ====================
def render
_practical():
"""Practical tests page"""
if conn is None:
return
st.markdown("""
<div class="main-header">
ﮐ ا ر % ٮ
>h1/< ﯽ
 W ٮ<p>Laboratory Practical Tests & Procedures</p>
</div>
""", unsafe_
allow
_html=True)
try:
col1, col2, col3 = st.columns(3)
with col1:
categories = conn.execute("SELECT DISTINCT category FROM practical_
tests ORDER BY
category").fetchall()
cat
_list = ["All"] + [c['category'] for c in categories]
selected
_cat = st.selectbox(t('category'), cat_list)
with col2:
difficulty = st.selectbox(t('difficulty'), ["All", "Basic", "Intermediate", "Advanced"])
with col3:
search
_practical = st.text_input(t('search'), placeholder="Search practical tests...")
query = "SELECT * FROM practical_
tests WHERE 1=1"
params = []
if selected
cat != "All":
_
query += " AND category = ?"
params.append(selected_cat)
if difficulty != "All":
query += " AND difficulty_
level = ?"
params.append(difficulty)
if search
_practical:
query += " AND (title_
en LIKE ? OR title
_
ku LIKE ?)"
search
_term = f"%{search_practical}%"
params.extend([search_term, search_term])
query += " ORDER BY difficulty_level, title_
en"
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
<h4> {get_name(p, 'title')}</h4>
<p>
<span style="background: {difficulty_color}; color: white; padding: 2px 10px; border-
radius: 10px; font-size: 0.8em;">
{p['difficulty_level']}
</span>
<span style="margin-left: 10px;"> {p['duration_minutes']} {t('minutes')}</span>
<span style="margin-left: 10px;"> {p['category']}</span>
</p>
</div>
""", unsafe_
allow
_html=True)
with st.expander(f"{t('details')} - {get_name(p, 'title')}"):
st.markdown(f"#### {t('description')}")
st.write(get_desc(p))
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
""", unsafe_
allow
_html=True)
col1, col2 = st.columns(2)
with col1:
st.markdown(f"#### {t('materials')}")
materials = get_name(p, 'materials')
if materials:
mat
_list = [m.strip() for m in materials.split(',')]
for mat in mat
list:
_
if mat:
st.markdown(f"- {mat}")
st.markdown(f"#### {t('expected_results')}")
st.write(get_name(p, 'expected_results'))
with col2:
st.markdown(f"#### {t('interpretation')}")
st.write(get_name(p, 'interpretation'))
st.markdown(f"#### {t('precautions')}")
precautions = get_name(p, 'precautions')
if precautions:
st.warning(precautions)
except Exception as e:
st.error(f"Practical Tests Error: {str(e)}")
# ==================== Study Notes Module ====================
def render
_notes():
"""Study notes page"""
if conn is None:
return
st.markdown("""
<div class="main-header">
ە # ٮک
>h1/< ن ﺎ
 # ٮ .  I ٮ #ٚ ٮ % ٮ<p>Laboratory Theory & Study Notes</p>
</div>
""", unsafe_
allow
_html=True)
try:
with st.expander(" Add New Note"):
with st.form("add_
note
_form"):
topic = st.text_input("Topic")
content = st.text
_area("Content", height=150)
category = st.selectbox("Category", ["Hematology", "Clinical Chemistry",
"Microbiology",
"Immunology", "Endocrinology", "Urinalysis",
"Coagulation", "Blood Bank", "General"])
tags = st.text_input("Tags (comma separated)")
if st.form
submit
_
_button(t('save_note')):
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
search
note = st.text
_
_input(t('search'), placeholder="Search notes...")
query = "SELECT * FROM study_
notes WHERE 1=1"
params = []
if search
note:
_
query += " AND (topic LIKE ? OR content LIKE ? OR tags LIKE ?)"
search
_term = f"%{search_note}%"
params.extend([search_term, search_term, search_term])
query += " ORDER BY updated_
at DESC"
notes = conn.execute(query, params).fetchall()
st.markdown(f"### Found: {len(notes)} notes")
for note in notes:
n = dict(note)
with st.expander(f" {n['topic']} ({n['category']})"):
st.markdown(f"""
<div class="note-card">
<p><strong>Category:</strong> {n['category']}</p>
<p><strong>Created:</strong> {n['created_at']}</p>
<p><strong>Tags:</strong> {n['tags']}</p>
</div>
""", unsafe_
allow
_html=True)
st.markdown("### Content")
st.markdown(n['content'])
if st.button(f" {t('delete')}", key=f"del_{n['id']}"):
conn.execute("DELETE FROM study_
notes WHERE id = ?", (n['id'],))
conn.commit()
st.rerun()
except Exception as e:
st.error(f"Study Notes Error: {str(e)}")
# ==================== Results Entry ====================
def render
_results():
"""Results entry page"""
if conn is None:
return
st.markdown("""
<div class="main-header">
ک
ە ﺋ >h1<
ە ﻣ ﺎ I ﺤ . ٮ
>h1/< ن ﺎ
<p>Enter Laboratory Test Results</p>
</div>
""", unsafe_
allow
_html=True)
try:
col1, col2 = st.columns([1, 1])
with col1:
st.markdown("### Patient Information")
with st.form("result_form"):
name = st.text
_input(t('patient_name'), placeholder="Enter patient full name")
col
_age, col_gender = st.columns(2)
with col
_age:
with col
_gender:
age = st.number_input(t('patient_age'), min_value=0, max_value=120, value=30)
gender = st.selectbox(t('patient_gender'), ["Male", "Female", "Other"])
st.markdown("### Test Selection")
test
_categories = conn.execute("SELECT DISTINCT category FROM test_types ORDER
BY category").fetchall()
selected
_category = st.selectbox("Test Category",
["Select Category..."] + [c['category'] for c in test_categories])
if selected
_category != "Select Category...":
tests
in
_
_category = conn.execute("""
SELECT id, name_en, name_ku, unit, normal_range_low, normal_range_high,
critical
_low, critical_high, price
FROM test
_types
WHERE category = ?
ORDER BY name
en
_
""", (selected_category,)).fetchall()
test
_options = {}
for t in tests
in
_
_category:
td = dict(t)
test
_options[f"{get_name(td)} ({td['unit']})"] = td
selected
test
_
_name = st.selectbox(t('select_test'), list(test_options.keys()))
if selected
test
name:
_
_
selected
test = test
_
_options[selected_
test
_name]
st.markdown(f"""
<div class="info-box">
<p><strong>Normal Range:</strong> {selected_test['normal_range_low']} -
{selected_test['normal_range_high']} {selected_test['unit']}</p>
</div>
""", unsafe_
allow
_html=True)
result
value = st.number
_
_input(
f"{t('result_value')} ({selected_test['unit']})",
step=0.01,
format="%.2f"
)
notes = st.text
_area("Additional Notes", placeholder="Any observations...")
submitted = st.form
submit
_
_button(t('save_result'), use_
container
_width=True)
if submitted:
if not name:
st.error("Please enter patient name")
elif selected
_category == "Select Category...":
st.error("Please select a test category")
else:
is
abnormal = 0
_
is
critical = 0
_
if result
value < selected
_
_test['normal_range_low'] or result_
value >
selected
_test['normal_range_high']:
is
abnormal = 1
_
if result
value < selected
_
_test['critical_low'] or result_
value >
selected
_test['critical_high']:
is
critical = 1
_
conn.execute("""
INSERT INTO test
results
_
(patient_name, patient_age, patient_gender, test_id,
result
_value, is_abnormal, is_critical, notes)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", (name, age, gender, selected_test['id'],
result
_value, is_abnormal, is_critical, notes))
conn.commit()
st.success(t('saved_success'))
if is
critical:
_
st.error(" CRITICAL VALUE ALERT!")
st.markdown(f"""
<div class="critical-box">
<h4> Critical Result for {get_name(selected_test)}</h4>
<p>Patient: {name}</p>
<p>Result: {result_value} {selected_test['unit']}</p>
</div>
""", unsafe_
allow
_html=True)
st.rerun()
else:
st.info("Please select a test category to continue")
st.form
submit
_
_button(t('save_result'), disabled=True, use_
container
_width=True)
with col2:
st.markdown("### Recent Results")
recent
_results = conn.execute("""
SELECT tr.*, tt.name_en, tt.name_ku, tt.unit
FROM test
results tr
_
JOIN test
_types tt ON tr.test_
id = tt.id
ORDER BY tr.date
_performed DESC
LIMIT 10
""").fetchall()
if recent
results:
_
for result in recent
_
rd = dict(result)
results:
if rd['is_critical']:
box
class = "test-result-critical"
_
emoji = " "
elif rd['is_abnormal']:
box
class = "test-result-abnormal"
_
emoji = " "
else:
box
class = "test-result-normal"
_
emoji = " "
st.markdown(f"""
<div class="{box_class}">
<p><strong>{emoji} {rd['patient_name']}</strong> - {get_name(rd)}</p>
<p>Result: {rd['result_value']} {rd['unit']}</p>
<p><small>{rd['date_performed']}</small></p>
</div>
""", unsafe_
allow
_html=True)
else:
st.info("No recent results to display")
except Exception as e:
st.error(f"Results Entry Error: {str(e)}")
# ==================== Reports ====================
def render
_reports():
"""Reports page"""
if conn is None:
return
st.markdown("""
<div class="main-header">
<h1> ٮاڕWترﯚ </h1>
<p>Laboratory Analytics</p>
</div>
""", unsafe_
allow
_html=True)
try:
col1, col2, col3 = st.columns([1, 1, 2])
with col1:
date
_
from = st.date
_input("From Date", datetime×now() - timedelta(days=30))
with col2:
date
to = st.date
_
_input("To Date", datetime.now())
results = conn.execute("""
SELECT tr.*, tt.name_en, tt.name_ku, tt.category, tt.unit
FROM test
results tr
_
JOIN test
_types tt ON tr.test_
id = tt.id
WHERE date(tr.date_performed) BETWEEN ? AND ?
ORDER BY tr.date
_performed DESC
""", (date_from, date_to)).fetchall()
if not results:
st.info("No results found for selected period")
return
df = pd×DataFrame([dict(r) for r in results])
df['test_name'] = df.apply(lambda row: get_name(row), axis=1)
st.markdown("### Summary Statistics")
col1, col2, col3, col4 = st.columns(4)
with col1:
total
_tests = len(df)
st.metric("Total Tests", total_tests)
with col2:
total
_patients = df['patient_name'].nunique()
st.metric("Unique Patients", total_patients)
with col3:
abnormal
_count = df['is_abnormal'].sum()
abnormal
_rate = (abnormal_count / total_tests * 100) if total_
tests > 0 else 0
st.metric("Abnormal Results", f"{abnormal_count} ({abnormal_rate:.1f}%)")
with col4:
critical
_count = df['is_critical'].sum()
st.metric("Critical Values", critical_count)
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
st.markdown("### Test Distribution")
test
_counts = df['test_name'].value_counts().head(10)
if len(test_counts) > 0:
fig = px×bar(x=test_counts.index, y=test_counts.values,
title="Top 10 Tests",
labels={'x': 'Test', 'y': 'Count'},
color=test
_counts.values,
color
continuous
_
_scale='Viridis')
fig.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig, use_
container
_width=True)
with col2:
st.markdown("### Abnormal by Category")
category_
abnormal = df×groupby('category')['is_abnormal'].agg(['sum', 'count'])
if len(category_abnormal) > 0:
category_abnormal['rate'] = (category_abnormal['sum'] / category_abnormal['count'] *
100)
fig = px.bar(category_abnormal, y=category_abnormal.index, x='rate',
title="Abnormal Rate (%)",
orientation='h',
color='rate',
color
continuous
scale='RdYlGn
_
_
_r')
st.plotly_chart(fig, use_
container
_width=True)
st.markdown("### Detailed Results")
display_cols = ['patient_name', 'patient_age', 'patient_gender',
'test
_name', 'result_value', 'unit', 'date_performed']
display_cols = [c for c in display_cols if c in df.columns]
df['Status'] = df.apply(lambda row:
' CRITICAL' if row['is_critical'] else
' ABNORMAL' if row['is_abnormal'] else
' NORMAL', axis=1)
st.dataframe(df[display_cols + ['Status']], use_
container
_width=True, hide_index=True)
csv = df×to
_csv(index=False)
st.download
_button(
label=" Export to CSV",
data=csv,
file
name=f"lab
results
_
_
_{date_from}_{date_to}.csv",
mime="text/csv",
use
container
width=True
_
_
)
except Exception as e:
st.error(f"Reports Error: {str(e)}")
# ==================== AI Chat ====================
def render
ai
_
_chat():
"""AI Chat page"""
st.markdown("""
<div class="main-header">
ﮑ % ٮ
ﯽکەﺮيز >h1<
>h1/< د ﺮ
ﺳ ە د
<p>Medical Laboratory AI Assistant</p>
</div>
""", unsafe_
allow
_html=True)
st.markdown("### Suggested Questions")
suggestions = [
"What does a CBC test measure?",
"Explain normal blood glucose levels",
"What causes anemia?",
"How to prepare for a cholesterol test?",
"Interpret high WBC count",
"What is HbA1c?",
"Explain Gram staining procedure"
]
for i in range(0, len(suggestions), 4):
cols = st.columns(4)
for j in range(4):
if i + j < len(suggestions):
with cols[j]:
if st.button(suggestions[i + j], key=f"sug_{i+j}", use_
container
_width=True):
st.session
state.chat
_
_input = suggestions[i + j]
if 'chat
_history' not in st.session_
state:
st.session
state.chat
_
_history = []
chat
_container = st.container()
with chat
container:
_
for i, chat in enumerate(st.session_
state.chat
_history):
with st.chat
_message("user"):
st.write(chat['question'])
with st.chat
_message("assistant"):
st.markdown(chat['answer'])
if 'chat
_input' not in st.session_
state:
st.session
state.chat
_
_input = ""
question = st.chat_input(t('type_question'))
if question:
st.session
state.chat
_
_history.append({
"question": question,
"answer": ""
})
with st.chat
_message("user"):
st.write(question)
with st.chat
_message("assistant"):
with st.spinner(" Analyzing your question..."):
answer = get_
ai
_response(question)
st.markdown(answer)
st.session
state.chat
_
_history[-1]['answer'] = answer
if st.session
state.chat
_
_history:
if st.button(" Clear Chat History", use_
container
_width=True):
st.session
state.chat
_
_history = []
st.rerun()
# ==================== Main Application ====================
def main():
"""Main application"""
if 'language' not in st.session_
state:
st.session
" یدروﮐ " = state.language_
if 'nav
_page' not in st.session_
state:
st.session
state.nav
_
_page = "dashboard"
# Sidebar
with st.sidebar:
st.markdown("""
<div style="text-align: center; padding: 15px 0;">
<h3 style="color: #1565c0; margin: 0;"> MediLab Pro</h3>
<p style="color: #666; font-size: 0.8rem; margin: 5px 0;">Medical Laboratory System</
p>
</div>
""", unsafe_
allow
_html=True)
,["
language = st.selectbox(
," نﺎﻣز / Language "
", "English
یدروﮐ "]
key="lang_
selector"
)
if language != st.session
_state.language:
st.session
_state.language = language
st.rerun()
st.markdown("---")
st.markdown("### Navigation")
pages = {
"dashboard": " " + t('dashboard'),
"diseases": " " + t('disease_db'),
"tests": " " + t('lab_tests'),
"practical": " " + t('practical'),
"notes": " " + t('theory'),
"results": " " + t('results_entry'),
"reports": " " + t('reports'),
"ai": " " + t('ai_chat')
}
for page_key, page_name in pages.items():
button
_type = "primary" if st.session_
state.nav
_page == page_key else "secondary"
if st.button(page_name, key=f"nav_{page_key}",
use
container
_
_width=True,
type=button_type):
st.session
state.nav
_
_page = page_key
st.rerun()
st.markdown("---")
try:
db
_size = os.path.getsize('medical_lab.db') / (1024 * 1024)
st.caption(f"Database Size: {db_size:.2f} MB")
except:
st.caption("Database: Connected")
st.caption(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 10px; background: linear-gradient(135deg, #667eea
0%, #764ba2 100%);
border-radius: 10px; color: white;">
لﺎ#ٮ.ٮاد >p style="margin: 3px 0; font-size: 0.9rem;">>strong></p/< ﻞ#
لﺎ#ٮ.ٮاد >p style="margin: 3px 0; font-size: 0.9rem;">ﯚ % ڡ >";="margin: 3px 0; font-size: 0.yle="margin: 3px 0; font-size: 0.7rem;">© 2024</p>
>strong></p/< ﻞ#ٮﻋﺎﻤﺴ#ٮﺋ
ە ﮕ # ٮ % ڡ
>p/< ﯽکﺸيزWٮ
ی
ﺎ % ٮ -
م ە ر ا و W ﺣ
ﯽ . ﻋ ﺎ . ٮ
</div>
""", unsafe_
allow
_html=True)
# Student Info Header - smaller version
st.markdown("""
<div class="student-info">
لﺎ#ٮ.ٮاد >h2<
>h2/< ﻞ#ٮﻋﺎﻤﺴ#ٮﺋ
ە ﮕ # ٮ % ڡ
ﯚ % ڡ >p<
>p/< ﯽکﺸيزWٮ
ی
ﺎ % ٮ
ﯽﺷەIٮ -
م ە ر ا و W ﺣ
ﯽ . ﻋ ﺎ . ٮ
</div>
""", unsafe_
allow
_html=True)
# Render selected page
current
_page = st.session_
state.nav
_page
try:
if current
_page == "dashboard":
render
_dashboard()
elif current
_page == "diseases":
render
_diseases()
elif current
_page == "tests":
render
_tests()
elif current
_page == "practical":
render
_practical()
elif current
_page == "notes":
render
_notes()
elif current
_page == "results":
render
_results()
elif current
_page == "reports":
render
_reports()
elif current
_page == "ai":
render
ai
_
_chat()
else:
render
_dashboard()
except Exception as e:
st.error(f"Error loading page: {str(e)}")
st.info("Please try refreshing the page.")
# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 8px; color: #666; font-size: 0.8rem;">
<p> Medical Laboratory Management System | Version 2.0</p>
<p>Developed for educational purposes | Always consult healthcare professionals</p>
</div>
""", unsafe_
allow
_html=True)
# ==================== Run Application ====================
if
name
" ==
main
:"
__
__
__
__
if conn:
main()
else:
st.error(" Failed to connect to database. Please check your configuration.")
st.info("Make sure SQLite is installed and the application has write permissions.")
