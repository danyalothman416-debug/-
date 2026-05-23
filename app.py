import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
import base64
from io import BytesIO
import time
import re
from fpdf import FPDF

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="ڕێبەری پشکنینە تاقیگەییەکان", 
    layout="wide", 
    initial_sidebar_state="collapsed",
    page_icon="🔬"
)

# --- SESSION STATE ---
if 'history' not in st.session_state:
    st.session_state.history = []
if 'reminders' not in st.session_state:
    st.session_state.reminders = []
if 'doctor_notes' not in st.session_state:
    st.session_state.doctor_notes = []

# --- CSS STYLING (Light & Mobile Friendly) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Naskh+Arabic:wght@400;500;600;700;800&display=swap');
    
    * { font-family: 'Noto Naskh Arabic', 'Segoe UI', sans-serif; }
    [data-testid="stSidebar"] { display: none; }
    
    html, body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%) !important;
    }
    
    .main-header {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #2563eb 100%);
        border-radius: 20px; padding: 20px; text-align: center; margin-bottom: 15px;
        box-shadow: 0 8px 25px rgba(79, 70, 229, 0.2);
    }
    .main-header h1 { color: white !important; font-size: 1.6rem !important; font-weight: 800 !important; margin: 0 !important; }
    .main-header p { color: rgba(255,255,255,0.9) !important; font-size: 0.85rem !important; margin: 5px 0 0 0 !important; }
    
    .glass-card { background: white !important; border-radius: 16px !important; padding: 18px !important; margin-bottom: 15px !important; box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important; border: 1px solid #e5e7eb !important; }
    
    .stButton button { background: linear-gradient(135deg, #4f46e5, #7c3aed) !important; color: white !important; border: none !important; font-weight: 600 !important; border-radius: 12px !important; padding: 10px 20px !important; font-size: 0.9rem !important; width: 100% !important; box-shadow: 0 2px 8px rgba(79, 70, 229, 0.2) !important; }
    .stButton button:hover { transform: translateY(-2px) !important; }
    
    .stTextInput input, .stNumberInput input { background: white !important; border: 2px solid #e5e7eb !important; border-radius: 10px !important; padding: 8px 14px !important; font-size: 0.9rem !important; }
    .stTextInput input:focus, .stNumberInput input:focus { border-color: #4f46e5 !important; }
    
    .category-badge { display: inline-block; background: #eef2ff; border: 1px solid #c7d2fe; border-radius: 20px; padding: 6px 16px; margin: 15px 0 10px 0; font-weight: 600; color: #3730a3 !important; font-size: 0.85rem; }
    
    .symptom-card { background: white; border-radius: 12px; padding: 12px; margin: 6px; text-align: center; border: 2px solid #e5e7eb; cursor: pointer; transition: all 0.2s; font-size: 0.85rem; }
    .symptom-card:hover { border-color: #4f46e5; background: #eef2ff; }
    .symptom-selected { border-color: #4f46e5 !important; background: #eef2ff !important; font-weight: 700; }
    
    .result-box { border-radius: 12px; padding: 15px; margin: 10px 0; font-size: 0.9rem; }
    .result-normal { background: #f0fdf4; border-left: 4px solid #10b981; }
    .result-warning { background: #fffbeb; border-left: 4px solid #f59e0b; }
    .result-info { background: #eff6ff; border-left: 4px solid #3b82f6; }
    
    .reminder-card { background: white; border-radius: 12px; padding: 12px; margin: 8px 0; border: 1px solid #e5e7eb; font-size: 0.85rem; }
    
    .food-card { background: #fffbeb; border: 1px solid #fde68a; border-radius: 10px; padding: 10px; margin: 8px 0; font-size: 0.85rem; }
    
    .stat-card { background: white; border-radius: 12px; padding: 15px; text-align: center; box-shadow: 0 2px 6px rgba(0,0,0,0.03); }
    .stat-value { font-size: 1.5rem; font-weight: 800; color: #4f46e5 !important; }
    .stat-label { color: #6b7280 !important; font-size: 0.78rem; }
    
    .streamlit-expanderHeader { background: #f9fafb !important; border-radius: 10px !important; font-size: 0.85rem !important; padding: 8px 12px !important; }
    
    .stTabs [data-baseweb="tab-list"] { gap: 4px; background: white !important; border-radius: 12px; padding: 4px; }
    .stTabs [data-baseweb="tab"] { border-radius: 10px !important; padding: 6px 10px !important; font-size: 0.8rem !important; }
    .stTabs [aria-selected="true"] { background: linear-gradient(135deg, #4f46e5, #7c3aed) !important; color: white !important; }
    
    [dir="rtl"] { text-align: right !important; direction: rtl !important; }
</style>
""", unsafe_allow_html=True)

# --- DATABASES ---

# Symptom to Test Mapping
SYMPTOM_TESTS = {
    "بێهێزی": ["پشکنینی تەواوی خوێن (CBC)", "کۆگای ئاسن (Ferritin)", "ڤیتامین B12", "ڤیتامین دی (Vitamin D)", "شەکری ناو خوێن (FBS)"],
    "سەرئێشە": ["پشکنینی تەواوی خوێن (CBC)", "پەستانی خوێن", "ڤیتامین دی (Vitamin D)", "هۆرمۆنی دەرەقی (TSH)"],
    "ئازاری جومگە": ["ترشی یۆریک (Uric Acid)", "هەوکردن (CRP)", "پشکنینی تەواوی خوێن (CBC)", "ڤیتامین دی (Vitamin D)"],
    "ماندوێتی": ["پشکنینی تەواوی خوێن (CBC)", "کۆگای ئاسن (Ferritin)", "هۆرمۆنی دەرەقی (TSH)", "شەکری ناو خوێن (FBS)", "ڤیتامین B12"],
    "دڵەڕاوکێ": ["هۆرمۆنی دەرەقی (TSH)", "ئەلیکترۆلیتەکان", "پشکنینی تەواوی خوێن (CBC)"],
    "کێش دابەزین": ["هۆرمۆنی دەرەقی (TSH)", "شەکری ناو خوێن (FBS)", "شەکری کەڵەکەبوو (HbA1c)", "پشکنینی تەواوی خوێن (CBC)"],
    "کێش زیادبوون": ["هۆرمۆنی دەرەقی (TSH)", "شەکری ناو خوێن (FBS)", "چەورییەکانی خوێن (Lipid)"],
    "ڕووتانەوەی قژ": ["کۆگای ئاسن (Ferritin)", "هۆرمۆنی دەرەقی (TSH)", "ڤیتامین دی (Vitamin D)", "ڤیتامین B12"],
    "ئازاری سک": ["پەنکریاس (Amylase/Lipase)", "فەرمانی جگەر (LFT)", "پشکنینی هەوکردن (CRP)"],
    "زۆر میزکردن": ["شەکری ناو خوێن (FBS)", "شەکری کەڵەکەبوو (HbA1c)", "فەرمانی گورچیلە (KFT)"],
    "هەناسە تەنگی": ["پشکنینی تەواوی خوێن (CBC)", "کۆگای ئاسن (Ferritin)", "ترۆپۆنین (Troponin)"],
    "سووربوونەوەی پێست": ["هەوکردن (CRP)", "پشکنینی تەواوی خوێن (CBC)", "فەرمانی جگەر (LFT)"],
    "ئازاری دڵ": ["ترۆپۆنین (Troponin)", "چەورییەکانی خوێن (Lipid)", "پشکنینی تەواوی خوێن (CBC)"],
    "ورەوەری و بێتاقەتی": ["هۆرمۆنی دەرەقی (TSH)", "پشکنینی تەواوی خوێن (CBC)", "کۆگای ئاسن (Ferritin)"],
}

# Lab Abbreviations
LAB_ABBREVIATIONS = {
    "CBC": "Complete Blood Count - پشکنینی تەواوی خوێن",
    "FBS": "Fasting Blood Sugar - شەکری ناو خوێن لە کاتی برسێتیدا",
    "HbA1c": "Hemoglobin A1c - شەکری کەڵەکەبوو (تێکڕای ٣ مانگ)",
    "TSH": "Thyroid Stimulating Hormone - هۆرمۆنی چالاککەری دەرەقی",
    "ALT": "Alanine Aminotransferase - ئەنزیمێکی جگەرە، بەرزبوونەوەی نیشانەی زیانگەیشتن بە جگەرە",
    "AST": "Aspartate Aminotransferase - ئەنزیمێکی جگەر و دڵ و ماسولکەیە",
    "ALP": "Alkaline Phosphatase - ئەنزیمێکی جگەر و ئێسکە",
    "GGT": "Gamma-Glutamyl Transferase - ئەنزیمێکی هەستیاری جگەر و ڕێڕەوی زەرداوە",
    "HDL": "High-Density Lipoprotein - چەوری سوودبەخش (کۆلیسترۆڵی باش)",
    "LDL": "Low-Density Lipoprotein - چەوری زیانبەخش (کۆلیسترۆڵی خراپ)",
    "CRP": "C-Reactive Protein - پڕۆتینی کاردانەوەی هەوکردن",
    "ESR": "Erythrocyte Sedimentation Rate - ڕێژەی نیشتنەوەی خڕۆکە سوورەکان",
    "WBC": "White Blood Cells - خڕۆکە سپییەکانی خوێن (بەرگری لەش)",
    "RBC": "Red Blood Cells - خڕۆکە سوورەکانی خوێن (هەڵگری ئۆکسجین)",
    "KFT": "Kidney Function Test - پشکنینی فەرمانی گورچیلە",
    "LFT": "Liver Function Test - پشکنینی فەرمانی جگەر",
    "PT": "Prothrombin Time - کاتی مەینبوونی خوێن",
    "INR": "International Normalized Ratio - ڕێژەی نێودەوڵەتی مەینبوون",
    "BUN": "Blood Urea Nitrogen - نایترۆجینی یوریای خوێن",
    "GFR": "Glomerular Filtration Rate - ڕێژەی فلتەرکردنی گورچیلە",
    "PSA": "Prostate Specific Antigen - دژە پەیکەری تایبەتی پرۆستات",
    "ANA": "Antinuclear Antibody - دژە تەنی ناوەکی (بۆ نەخۆشییە خۆییەکان)",
    "HCV": "Hepatitis C Virus - ڤایرۆسی جگەری جۆری C",
    "HBsAg": "Hepatitis B Surface Antigen - دژە پەیکەری ڕووکەشی ڤایرۆسی جگەری B",
    "HIV": "Human Immunodeficiency Virus - ڤایرۆسی کەمبوونەوەی بەرگری مرۆڤ",
}

# Sample Collection Guide
SAMPLE_GUIDES = {
    "پشکنینی تەواوی خوێن (CBC)": "💉 نموونەی خوێن لە خوێنهێنەر وەردەگیرێت. پێویست بە برسیبوون نییە. دەتوانیت ئاوی ئاسایی بخۆیتەوە.",
    "شەکری ناو خوێن (FBS)": "💉 پێویستە ٨-١٢ کاتژمێر برسی بیت. تەنها ئاوی ئاسایی ڕێگەپێدراوە. نموونە بەیانیان وەردەگیرێت.",
    "چەورییەکانی خوێن (Lipid)": "💉 پێویستە ١٢-١٤ کاتژمێر برسی بیت. ٢٤ کاتژمێر پێش وەرزشی قورس و کحول مەخۆ.",
    "فەرمانی گورچیلە (KFT)": "💉 پێویست بە برسیبوون نییە بەڵام باشترە ٨ کاتژمێر برسی بیت. ئاوی ئاسایی بخۆرەوە.",
    "فەرمانی جگەر (LFT)": "💉 پێویست بە برسیبوون نییە. بەڵام ئەگەر لەگەڵ پشکنینی تر بکرێت، ڕەنگە پێویست بە برسیبوون بکات.",
    "هۆرمۆنی دەرەقی (TSH)": "💉 باشترین کات بەیانیانە. پێویست بە برسیبوون نییە. ئەگەر دەرمانی تایرۆید دەخۆیت، دوای پشکنین بیخۆ.",
    "کۆگای ئاسن (Ferritin)": "💉 پێویست بە برسیبوون نییە. بەیانیان باشترە چونکە ئاستی ئاسن لە ڕۆژدا دەگۆڕێت.",
    "ترشی یۆریک (Uric Acid)": "💉 پێویست بە برسیبوون نییە. ٢٤ کاتژمێر پێش کحول و گۆشتی سوور کەم بکەرەوە.",
    "ڤیتامین دی (Vitamin D)": "💉 پێویست بە برسیبوون نییە. هەر کاتێکی ڕۆژ دەتوانیت پشکنینەکە بکەیت.",
    "پشکنینی میز": "🧪 نموونەی یەکەمی بەیانیان باشترە. ناوچەکە پاک بکەرەوە. یەکەم بەشی میز فڕێ بدە و ناوەڕاستی میزەکە کۆبکەرەوە.",
}

# Unit Conversions
UNIT_CONVERSIONS = {
    "گلوکۆز (شەکر)": {"from": "mg/dL", "to": "mmol/L", "factor": 0.0555},
    "کۆلیسترۆڵ": {"from": "mg/dL", "to": "mmol/L", "factor": 0.0259},
    "Triglycerides": {"from": "mg/dL", "to": "mmol/L", "factor": 0.0113},
    "کریاتینین": {"from": "mg/dL", "to": "µmol/L", "factor": 88.4},
    "بیلیڕۆبین": {"from": "mg/dL", "to": "µmol/L", "factor": 17.1},
    "کالیسیۆم": {"from": "mg/dL", "to": "mmol/L", "factor": 0.25},
}

# --- HEADER ---
st.markdown("""
<div class="main-header">
    <h1>🔬 ڕێبەری پشکنینە تاقیگەییەکان</h1>
    <p>شیکاری نیشانەکان | ڕێنمایی وەرگرتنی نموونە | گۆڕینی یەکە | تێبینی پزیشک</p>
</div>
""", unsafe_allow_html=True)

# --- MAIN TABS ---
main_tab1, main_tab2, main_tab3, main_tab4, main_tab5, main_tab6, main_tab7 = st.tabs([
    "🔍 شیکاری نیشانەکان",
    "📋 پشکنینەکان", 
    "🧠 شیکاری ئەنجام",
    "📖 کورتکراوەکان",
    "🧪 ڕێنمایی وەرگرتن",
    "🔄 گۆڕینی یەکە",
    "⏰ یادخستنەوە"
])

# --- TAB 1: Symptom Checker ---
with main_tab1:
    st.markdown("<h3 style='color:#4f46e5;text-align:center;'>🔍 شیکاری نیشانەکان</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#6b7280;font-size:0.9rem;'>نیشانەکانت هەڵبژێرە بۆ پێشنیاری پشکنینی گونجاو</p>", unsafe_allow_html=True)
    
    # Display symptoms as clickable cards
    all_symptoms = list(SYMPTOM_TESTS.keys())
    
    # Use columns for grid layout
    cols_per_row = 4
    selected_symptoms = []
    
    for i in range(0, len(all_symptoms), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            idx = i + j
            if idx < len(all_symptoms):
                symptom = all_symptoms[idx]
                with col:
                    if st.button(symptom, key=f"symptom_{idx}", use_container_width=True):
                        if symptom not in selected_symptoms:
                            selected_symptoms.append(symptom)
    
    # Show selected symptoms and recommended tests
    if selected_symptoms:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(f"<p><b>✅ نیشانە هەڵبژێردراوەکان:</b> {', '.join(selected_symptoms)}</p>", unsafe_allow_html=True)
        
        # Collect unique recommended tests
        recommended_tests = set()
        for symptom in selected_symptoms:
            for test in SYMPTOM_TESTS.get(symptom, []):
                recommended_tests.add(test)
        
        st.markdown(f"<div class='category-badge'>🔬 پشکنینە پێشنیارکراوەکان ({len(recommended_tests)})</div>", unsafe_allow_html=True)
        
        for test in recommended_tests:
            st.markdown(f"""
            <div class="result-info result-box">
                <b>🔬 {test}</b>
            </div>
            """, unsafe_allow_html=True)
        
        # Button to go to tests tab
        if st.button("📋 بینینی وردەکاری پشکنینەکان", use_container_width=True):
            st.info("بڕۆ بۆ تابی 'پشکنینەکان' بۆ بینینی ڕێژە ئاساییەکان و ڕێنمایی خۆراکی")

# --- TAB 2: Tests List ---
with main_tab2:
    st.markdown("<h3 style='color:#4f46e5;text-align:center;'>📋 پشکنینەکان</h3>", unsafe_allow_html=True)
    
    search_text = st.text_input("🔍 گەڕان:", placeholder="ناوی پشکنین...", key="test_search")
    
    filtered_tests = {}
    for key, test in ALL_TESTS.items():
        if search_text and search_text.lower() not in key.lower():
            continue
        filtered_tests[key] = test
    
    if filtered_tests:
        for test_key, test in filtered_tests.items():
            with st.expander(f"{test.get('Icon', '🔬')} {test['Name'][:50]}... | {test['Organ']}"):
                st.markdown(f"""
                <div class="glass-card">
                    <p><b>📝 وەسف:</b> {test['Description']}</p>
                    <p><b>📊 ڕێژە ئاساییەکان:</b></p>
                    <p style="background:#f3f4f6;padding:8px 12px;border-radius:8px;font-size:0.85rem;">{test['Ranges']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if 'FoodRecommendations' in test:
                    st.markdown(f"""
                    <div class="food-card">
                        <h4>🥗 خۆراکی</h4>
                        <p>{test['FoodRecommendations']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Sample collection guide
                if test_key in SAMPLE_GUIDES:
                    st.markdown(f"""
                    <div class="result-info result-box">
                        <b>🧪 ڕێنمایی وەرگرتن:</b> {SAMPLE_GUIDES[test_key]}
                    </div>
                    """, unsafe_allow_html=True)

# --- TAB 3: AI Analysis ---
with main_tab3:
    st.markdown("<h3 style='color:#4f46e5;text-align:center;'>🧠 شیکاری ئەنجام</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        test_choice = st.selectbox("🔬 پشکنین:", list(ALL_TESTS.keys()), key="ai_test_select")
        gender_choice = st.selectbox("👤 ڕەگەز:", ["general", "male", "female"], format_func=lambda x: {"general": "گشتی", "male": "پیاوان", "female": "ژنان"}[x], key="ai_gender_select")
    with col2:
        unit_choice = st.text_input("📏 یەکە:", value="mg/dL", key="ai_unit_input")
        user_result = st.number_input("🔢 ئەنجام:", value=0.0, step=0.1, format="%.1f", key="ai_value_input")
    
    # Doctor's note
    doctor_note = st.text_area("📝 تێبینی پزیشک (ئارەزوومەندانە):", placeholder="بۆ نموونە: ئەم پشکنینەم کرد کاتێک نەخۆش بووم...", key="doctor_note")
    
    if st.button("🔍 شیکاری بکە", key="ai_analyze_btn", use_container_width=True):
        if user_result > 0:
            with st.spinner("🧠 شیکاری دەکرێت..."):
                time.sleep(0.8)
                result = ai_analyze(test_choice, user_result, gender_choice)
                
                st.markdown(f"""
                <div class="glass-card">
                    <div class="result-box {result['color_class']}">
                        <span style="font-size:1.5rem;">{result['emoji']}</span>
                        <b>{result['test_name']}</b> - {result['status_text']}
                    </div>
                    <p><b>📊 ئەنجام:</b> {result['user_value']} {result['unit']}</p>
                    <p><b>📏 مەودای ئاسایی:</b> {result['min_val']} - {result['max_val']} {result['unit']}</p>
                    <p><b>📋 شیکاری:</b> {result['meaning']}</p>
                    <p><b>💊 ڕێنمایی:</b> {result['action']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Save to history with doctor's note
                st.session_state.history.append({
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "test": test_choice,
                    "value": user_result,
                    "unit": unit_choice,
                    "status": result['status'],
                    "note": doctor_note
                })
                
                if doctor_note:
                    st.markdown(f"""
                    <div class="result-info result-box">
                        <b>📝 تێبینی تۆمارکراو:</b> {doctor_note}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("تکایە ئەنجامێک بنووسە")

# --- TAB 4: Abbreviations ---
with main_tab4:
    st.markdown("<h3 style='color:#4f46e5;text-align:center;'>📖 ڕوونکردنەوەی کورتکراوە تاقیگەییەکان</h3>", unsafe_allow_html=True)
    
    abbr_search = st.text_input("🔍 کورتکراوە بنووسە:", placeholder="بۆ نموونە: ALT, CBC, TSH...", key="abbr_search")
    
    if abbr_search:
        abbr_upper = abbr_search.upper().strip()
        if abbr_upper in LAB_ABBREVIATIONS:
            st.markdown(f"""
            <div class="result-info result-box">
                <h4>🔤 {abbr_upper}</h4>
                <p>{LAB_ABBREVIATIONS[abbr_upper]}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("کورتکراوەکە نەدۆزرایەوە. تکایە کورتکراوەیەکی تر تاقی بکەرەوە.")
    else:
        st.markdown("<p style='color:#6b7280;'>کورتکراوەیەک بنووسە بۆ زانینی ماناکەی</p>", unsafe_allow_html=True)
        
        # Show popular abbreviations
        st.markdown("<div class='category-badge'>📌 باوترین کورتکراوەکان</div>", unsafe_allow_html=True)
        popular = ["CBC", "FBS", "HbA1c", "TSH", "ALT", "AST", "HDL", "LDL", "CRP", "KFT", "LFT", "WBC"]
        cols = st.columns(3)
        for i, abbr in enumerate(popular):
            with cols[i % 3]:
                if st.button(f"🔤 {abbr}", key=f"abbr_{abbr}", use_container_width=True):
                    st.info(f"**{abbr}**: {LAB_ABBREVIATIONS[abbr]}")

# --- TAB 5: Sample Collection ---
with main_tab5:
    st.markdown("<h3 style='color:#4f46e5;text-align:center;'>🧪 ڕێنمایی وەرگرتنی نموونە</h3>", unsafe_allow_html=True)
    
    sample_test = st.selectbox("پشکنین هەڵبژێرە:", list(SAMPLE_GUIDES.keys()), key="sample_test")
    
    if sample_test:
        st.markdown(f"""
        <div class="glass-card">
            <div class="result-info result-box">
                <h4>🧪 {sample_test}</h4>
                <p style="font-size:1.1rem;">{SAMPLE_GUIDES[sample_test]}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # General tips
    st.markdown("<div class='category-badge'>💡 ڕێنمایی گشتی</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="glass-card">
        <p>✅ هەمیشە ئاوی ئاسایی بخۆرەوە پێش پشکنین</p>
        <p>✅ دەرمانەکانت بەردەوام بە بەڵام بە پزیشکت بڵێ</p>
        <p>✅ ٢٤ کاتژمێر پێش پشکنین وەرزشی قورس مەکە</p>
        <p>❌ کحول مەخۆرەوە ٤٨ کاتژمێر پێش پشکنین</p>
        <p>❌ جگەرە مەکێشە ٢ کاتژمێر پێش پشکنین</p>
    </div>
    """, unsafe_allow_html=True)

# --- TAB 6: Unit Converter ---
with main_tab6:
    st.markdown("<h3 style='color:#4f46e5;text-align:center;'>🔄 گۆڕینی یەکەکان</h3>", unsafe_allow_html=True)
    
    conversion_choice = st.selectbox("جۆری پشکنین:", list(UNIT_CONVERSIONS.keys()), key="conv_choice")
    
    if conversion_choice:
        conv = UNIT_CONVERSIONS[conversion_choice]
        
        col1, col2, col3 = st.columns([2, 1, 2])
        with col1:
            from_value = st.number_input(f"بڕ بە {conv['from']}:", value=100.0, step=0.1, key="conv_from")
        with col2:
            st.markdown("<div style='text-align:center;padding-top:30px;font-size:2rem;'>➡️</div>", unsafe_allow_html=True)
        with col3:
            to_value = from_value * conv['factor']
            st.metric(f"بڕ بە {conv['to']}:", f"{to_value:.2f}")
        
        st.markdown(f"""
        <div class="result-info result-box">
            <p><b>📐 هاوکۆلکە:</b> 1 {conv['from']} = {conv['factor']} {conv['to']}</p>
            <p><b>📊 ئەنجام:</b> {from_value} {conv['from']} = {to_value:.2f} {conv['to']}</p>
        </div>
        """, unsafe_allow_html=True)

# --- TAB 7: Reminders ---
with main_tab7:
    st.markdown("<h3 style='color:#4f46e5;text-align:center;'>⏰ یادخستنەوەی پشکنین</h3>", unsafe_allow_html=True)
    
    # Add reminder
    with st.expander("➕ زیادکردنی یادخستنەوە"):
        reminder_test = st.selectbox("جۆری پشکنین:", list(ALL_TESTS.keys()), key="reminder_test")
        reminder_freq = st.selectbox("دووبارەبوونەوە:", ["ڕۆژانە", "هەفتانە", "مانگانە", "سێ مانگ جارێک", "ساڵانە"], key="reminder_freq")
        reminder_note = st.text_input("تێبینی:", placeholder="بۆ نموونە: پشکنینی شەکری مانگانە", key="reminder_note")
        
        if st.button("💾 تۆمارکردن", key="save_reminder"):
            st.session_state.reminders.append({
                "test": reminder_test,
                "frequency": reminder_freq,
                "note": reminder_note,
                "created": datetime.now().strftime("%Y-%m-%d")
            })
            st.success("✅ یادخستنەوەکە تۆمارکرا!")
            st.rerun()
    
    # Display reminders
    if st.session_state.reminders:
        st.markdown("<div class='category-badge'>📅 یادخستنەوەکانت</div>", unsafe_allow_html=True)
        for i, reminder in enumerate(st.session_state.reminders):
            st.markdown(f"""
            <div class="reminder-card">
                <b>🔬 {reminder['test']}</b><br>
                <span>🔄 {reminder['frequency']}</span> | 
                <span>📝 {reminder['note']}</span><br>
                <span style="color:#6b7280;font-size:0.8rem;">📅 تۆمارکراو: {reminder['created']}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("هێشتا هیچ یادخستنەوەیەکت نییە")
    
    # General reminders for chronic conditions
    st.markdown("<div class='category-badge'>💡 یادخستنەوەی گشتی بۆ نەخۆشییە درێژخایەنەکان</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="glass-card">
        <p><b>🍬 شەکرە:</b> پشکنینی FBS مانگانە | HbA1c هەر ٣ مانگ</p>
        <p><b>❤️ پەستانی خوێن:</b> پێوانەکردن هەفتانە | پشکنینی چەوری ساڵانە</p>
        <p><b>🦋 دەرەقی:</b> پشکنینی TSH هەر ٦-١٢ مانگ</p>
        <p><b>🫘 گورچیلە:</b> پشکنینی KFT هەر ٣-٦ مانگ</p>
    </div>
    """, unsafe_allow_html=True)

# --- HISTORY SECTION (Collapsible) ---
with st.expander("📊 مێژووی ئەنجامەکانت", expanded=False):
    if len(st.session_state.history) > 0:
        df = pd.DataFrame(st.session_state.history)
        st.dataframe(df, use_container_width=True)
        
        # Export
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 دابەزاندنی مێژوو (CSV)", csv, "my_results.csv", "text/csv")
    else:
        st.info("هێشتا هیچ ئەنجامێکت تۆمار نەکردووە")

# --- FOOTER ---
st.markdown("""
<div class="glass-card" style="text-align:center;margin-top:15px;">
    <p style="color:#ef4444;font-weight:600;margin:0;">⚠️ ئەم سیستەمە تەنها بۆ ڕێنمایی سەرەتاییە و جێگەی سەردانی پزیشک ناگرێتەوە</p>
</div>
""", unsafe_allow_html=True)
