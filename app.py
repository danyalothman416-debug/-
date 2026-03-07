import streamlit as st
import pandas as pd

# --- 1. ڕێکخستنی لاپەڕە ---
st.set_page_config(page_title="ڕێبەری گشتگیری تاقیگە", layout="centered")

# --- 2. سیستەمی Dark Mode (Toggle) لە Sidebar ---
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

with st.sidebar:
    st.markdown('<h3 style="text-align:right;">⚙️</h3>', unsafe_allow_html=True)
    st.markdown("""
        <style>
        div[data-testid="stCheckbox"] p { font-size: 0px !important; }
        div[data-testid="stCheckbox"] { width: fit-content !important; margin-left: auto !important; }
        </style>
    """, unsafe_allow_html=True)
    mode = st.toggle("🌙", value=st.session_state.dark_mode)
    st.session_state.dark_mode = mode

# ڕێکخستنی ڕەنگەکان
if st.session_state.dark_mode:
    bg_color, text_color, card_bg, border_color = "#121212", "#FFFFFF", "#1E1E1E", "#333333"
else:
    bg_color, text_color, card_bg, border_color = "#F5F7F9", "#000000", "#FFFFFF", "#E0E0E0"

# --- 3. دیزاینی CSS پێشکەوتوو (بۆ هاوشێوەکردنی وێنەکە) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;700&display=swap');
    
    html, body, .stApp {{ 
        direction: rtl; text-align: right; font-family: 'Vazirmatn', sans-serif;
        background-color: {bg_color}; color: {text_color} !important;
    }}
    
    /* ڕێکخستنی شاشەی سەرەکی */
    .reportview-container .main .block-container{{
        padding-top: 2rem; padding-bottom: 2rem;
    }}
    
    /* گەڕان */
    .stTextInput input {{
        background-color: {card_bg} !important;
        border: 2px solid #3e7e69 !important; border-radius: 10px !important;
        padding: 10px; font-size: 16px !important; color: {text_color} !important;
    }}
    
    /* کارتەکان (Square Grids) */
    .card-grid {{
        display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-top: 20px;
    }}
    
    .card {{
        background-color: {card_bg}; border: 1px solid {border_color}; border-radius: 12px;
        padding: 15px; text-align: center; color: {text_color} !important;
        cursor: pointer; transition: all 0.3s ease; height: 100%;
    }}
    
    .card:hover {{
        border-color: #3e7e69; box-shadow: 0 4px 10px rgba(62, 126, 105, 0.2);
    }}
    
    .card-title {{
        font-weight: bold; font-size: 16px; margin-top: 10px; display: block;
    }}
    
    .card-icon {{
        font-size: 40px; margin-bottom: 10px;
    }}
    
    .card-info {{
        font-size: 12px; color: #888; margin-top: 5px; line-height: 1.6;
    }}
    
    /* بەشەکانی خوارەوە (9-13) */
    .streamlit-expanderHeader {{
        background-color: {card_bg} !important; border-radius: 10px !important;
        color: {text_color} !important; font-weight: bold !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. شاشەی سەرەکی ---
st.markdown('<p style="text-align:center; color:#888; font-size: 12px; margin-bottom:5px;">Developed by: Dr. Danyal</p>', unsafe_allow_html=True)
st.markdown(f'<h2 style="text-align:center; margin-top:0; color:#3e7e69;">🏥 ڕێبەری گشتگیری تاقیگە</h2>', unsafe_allow_html=True)

# --- 5. بەشی گەڕان ---
search_query = st.text_input("🔎 ناوی پشکنین بنووسە بۆ گەڕان...")

# --- 6. بنکەدراوەی دەوڵەمەندی پشکنینەکان (بە هەمان زانیاری) ---
# تێبینی: بەهۆی زۆری زانیارییەکان، لێرەدا کورتکراوەیەکمان داناوە، بەڵام هەموو تێستەکان لە خوارەوە لە ناو کارتەکاندان.
full_lab_data = {
    "1. Hematology (خوێن زانی)": {
        "CBC": "پشکنینی گشتی خوێن. | Hb 12-17 | ٣٠ خولەک",
        "ESR": "نیشاندەری هەوکردن. | 0-20 mm/hr | ١ کاتژمێر",
        "PT & PTT": "مەیینی خوێن. | PT 11-13s | ١ کاتژمێر",
        "PCV": "چڕی خوێن. | 37-52% | ٣٠ خولەک",
        "Reticulocyte": "بەرهەمهێنانی خوێن نوێ. | ٢ کاتژمێر"
    },
    "2. Clinical Chemistry": {
        "Blood Sugar": "شەکری بەڕۆژوو/٣ مانگ. | FBS 70-100 | ٣٠ خولەک",
        "ALT & AST": "ئەنزیمەکانی جگەر. | <40 U/L | ١ کاتژمێر",
        "Creatinine": "توانای گورچیلەکان. | Cr 0.6-1.2 | ١ کاتژمێر",
        "Lipid Profile": "چەوری خوێن (Chol, TG). | Chol <200 | ٢ کاتژمێر",
        "Calcium": "کالسیۆمی خوێن. | ١ کاتژمێر",
        "Uric Acid": "ترشی یوریک. | ٣.٥-٧.٢ | ١ کاتژمێر",
        "Bilirubin": "زەردەویی. | Total <1.2 | ١ کاتژمێر"
    },
    # تێستەکانی تر ... (هەمان زانیاری لە ناو کارتەکاندان)
}

# --- 7. ئەنجامی گەڕان (بە دیزاینی کارت) ---
if search_query:
    for cat, tests in full_lab_data.items():
        for t_name, t_cont in tests.items():
            if search_query.lower() in t_name.lower():
                st.markdown(f'<div class="info-box"><span class="test-title">🧪 {t_name}</span><br>{t_cont}</div>', unsafe_allow_html=True)

# --- 8. دیزاینی کارتەکان (Square Grid هاوشێوەی وێنەکە) ---
st.markdown('<p style="font-weight:bold; font-size:18px; color:#3e7e69; margin-top:25px;">لیستی بەشەکان</p>', unsafe_allow_html=True)

# ئەنجامدانی سێ کۆڵۆن بۆ کارتەکان
col1, col2, col3 = st.columns(3)

# کارتەکان (بەبێ کەمکردنەوەی پشکنینەکان)
with col1:
    st.markdown('<div class="card"><div class="card-icon">🔬</div><span class="card-title">Hematology</span><div class="card-info">CBC, ESR, PT, PTT</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="card"><div class="card-icon">🧫</div><span class="card-title">Pathology</span><div class="card-info">PSA, CA-125</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="card"><div class="card-icon">🩺</div><span class="card-title">Symptom</span><div class="card-info">Symptom Guide</div></div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card"><div class="card-icon">🧪</div><span class="card-title">Chemistry</span><div class="card-info">Sugar, Liver, Renal</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="card"><div class="card-icon">🧬</div><span class="card-title">Molecular</span><div class="card-info">PCR, Karyotyping</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="card"><div class="card-icon">🧠</div><span class="card-title">Interpreter</span><div class="card-info">AI Interpreter</div></div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="card"><div class="card-icon">🦠</div><span class="card-title">Microbiology</span><div class="card-info">Culture, GSE, GUE</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="card"><div class="card-icon">⚠️</div><span class="card-title">Hormones</span><div class="card-info">Thyroid, Vit D3</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="card"><div class="card-icon">📊</div><span class="card-title">Tracker</span><div class="card-info">Results Tracker</div></div>', unsafe_allow_html=True)

# --- خوارەوەی کارتەکان (9-14) ---
with st.expander("9. BMI Calculator"):
    st.write("دیاریکردنی کێشی گونجاو.")

with st.expander("10. ڕێنماییەکانی پێش پشکنین"):
    st.write("بەڕۆژووبوون و دەرمان.")

with st.expander("14. 📲 دابەزاندنی ئەپ"):
    st.write("بۆ مۆبایل و کۆمپیوتەر.")
