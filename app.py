import streamlit as st

# --- 1. ڕێکخستنی لاپەڕە ---
st.set_page_config(page_title="ڕێبەری گشتگیری تاقیگە", layout="centered")

# --- 2. سیستەمی Dark Mode (Toggle) بە ئایکۆن لە Sidebar ---
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
    bg_color, text_color, card_bg, input_bg, label_color = "#0e1117", "#FFFFFF", "#1d2129", "#262730", "#4ea88d"
else:
    bg_color, text_color, card_bg, input_bg, label_color = "#ffffff", "#000000", "#f0f7f4", "#ffffff", "#3e7e69"

# --- 3. دیزاینی CSS گشتی ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;700&display=swap');
    html, body, .stApp {{ 
        direction: rtl; text-align: right; font-family: 'Vazirmatn', sans-serif;
        background-color: {bg_color}; color: {text_color} !important;
    }}
    p, span, label, div {{ color: {text_color} !important; }}
    .stTextInput input, .stNumberInput input {{ 
        direction: rtl; text-align: right; font-size: 18px !important;
        background-color: {input_bg} !important; color: {text_color} !important;
        border: 2px solid #3e7e69 !important;
    }}
    .info-box {{ 
        padding: 15px; border-radius: 12px; background-color: {card_bg}; 
        color: {text_color} !important; border-right: 6px solid #3e7e69; 
        margin-top: 5px; line-height: 1.8;
    }}
    .test-title {{ color: {label_color} !important; font-weight: bold; font-size: 19px; }}
    .streamlit-expanderHeader {{
        background-color: {card_bg} !important; color: {text_color} !important;
        border-radius: 10px !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. شاشەی سەرەکی ---
st.markdown('<p style="text-align:center; color:#888; font-size: 14px; margin-bottom:5px;">Developed by: Dr. Danyal</p>', unsafe_allow_html=True)
st.markdown(f'<h1 style="text-align:center; margin-top:0; color:#3e7e69;">🏥 ڕێبەری گشتگیری تاقیگە</h1>', unsafe_allow_html=True)

# --- 5. بەشی گەڕان ---
search_query = st.text_input("🔎 ناوی پشکنین بنووسە بۆ گەڕان...")

# --- 6. بنکەدراوەی پشکنینەکان (1 تا 8 وەک خۆیان) ---
full_lab_data = {
    "1. Hematology (خوێن زانی)": {
        "CBC": "پشکنینی گشتی خوێن بۆ Hb, WBC, RBC, Plt.",
        "ESR": "ڕێژەی نیشتنی خڕۆکە سوورەکان بۆ زانینی هەوکردن.",
        "PT & PTT": "بۆ کاتی مەیینی خوێن.",
        "PCV": "ڕێژەی قەبارەی خڕۆکە سوورەکان.",
        "Reticulocyte Count": "بۆ زانینی ڕێژەی بەرهەمهێنانی خڕۆکە سوورە نوێیەکان."
    },
    "2. Clinical Chemistry": {
        "Blood Sugar (FBS/HbA1c)": "شەکری بەڕۆژوو و تێکڕای ٣ مانگ.",
        "ALT & AST": "ئەنزیمەکانی جگەر.",
        "Creatinine & Urea": "پشکنینی سەرەکی بۆ توانای گورچیلەکان.",
        "Lipid Profile": "Cholesterol, TG, HDL, LDL بۆ چەوری خوێن.",
        "S.Calcium": "پشکنینی کالسیۆم بۆ تەندروستی ئێسک.",
        "S.Uric Acid": "بۆ زانینی ئاستی یوریک ئەسید و نەخۆشی جومگە.",
        "Bilirubin (T/D)": "پشکنینی زەردەویی."
    },
    "3. Microbiology": {
        "Urine Culture": "چاندنی میز بۆ دۆزینەوەی باکتریای زیانبەخش.",
        "Antibiogram": "دیاریکردنی دژەباکتریای گونجاو.",
        "GSE (Stool Exam)": "پشکنینی گشتی پیسایی."
    },
    "4. Urinalysis": {
        "General Urine (U/A)": "پشکنینی گشتی میز بۆ بینینی شەکر، پڕۆتین، کێم."
    },
    "5. Serology & Immunology": {
        "CRP Test": "لە کاتی هەوکردندا بەرز دەبێتەوە.",
        "Widal Test": "بۆ تای تیفۆید.",
        "HBsAg & HCV": "ڤایرۆسی جگەری B و C.",
        "Toxoplasmosis": "نەخۆشی پشیلە.",
        "RF & Anti-CCP": "بۆ ڕۆماتیزمی جومگەکان."
    },
    "6. Pathology (Tumor Markers)": {
        "PSA": "بۆ پڕۆستات.",
        "CA-125": "بۆ هێلکەدان.",
        "AFP": "بۆ شێرپەنجەی جگەر.",
        "CEA": "بۆ شێرپەنجەی کۆڵۆن."
    },
    "7. Molecular & Viral": {
        "PCR Test": "بۆ دەستنیشانکردنی وردی ڤایرۆسەکان.",
        "Karyotyping": "پشکنینی کرۆمۆسۆمەکان.",
        "ANA": "بۆ نەخۆشییەکانی بەرگری جەستە."
    },
    "8. Endocrinology & Hormones (هۆرمۆنەکان)": {
        "Thyroid Profile (TSH, T3, T4)": "بۆ فرمانی ڕژێنە دەرەقییەکان.",
        "Vitamin D3": "ڤیتامین D بۆ ئێسک و بەرگری.",
        "Prolactin": "هۆرمۆنی شیر.",
        "Testosterone": "هۆرمۆنی نێرینە.",
        "Insulin Test": "بۆ بەرگری ئەنسۆلین.",
        "Cortisol": "هۆرمۆنی سترێس."
    }
}

# --- 7. ئەنجامی گەڕان ---
if search_query:
    found = False
    for cat, tests in full_lab_data.items():
        for t_name, t_cont in tests.items():
            if search_query.lower() in t_name.lower():
                st.markdown(f'<div class="info-box"><span class="test-title">🧪 {t_name} ({cat})</span><br>{t_cont}</div>', unsafe_allow_html=True)
                found = True
    if not found:
        st.warning("ئەم پشکنینە نەدۆزرایەوە.")

# --- 8. نیشاندانی لیستەکان (خاڵی 1 تا 8) ---
for category, tests in full_lab_data.items():
    with st.expander(category):
        for test_name, content in tests.items():
            st.markdown(f'<span class="test-title">🧪 {test_name}</span>', unsafe_allow_html=True)
            st.markdown(f'<div class="info-box">{content}</div>', unsafe_allow_html=True)

# --- 9. خاڵی نۆیەم: BMI Calculator ---

with st.expander("9. BMI Calculator (دیاریکردنی کێشی گونجاو)"):
    st.markdown('<div class="info-box">ئەم بەشە بەکاردێت بۆ زانینی ئەوەی ئایا کێشت گونجاوە لەگەڵ باڵات یان نا.</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        weight = st.number_input("کێش (kg):", min_value=1.0, value=70.0, step=0.1)
    with col2:
        height = st.number_input("باڵا (cm):", min_value=50.0, value=170.0, step=0.1)
    
    if height > 0:
        bmi = weight / ((height/100) ** 2)
        st.markdown(f"### **BMI دەرەنجام: {bmi:.1f}**")
        
        if bmi < 18.5:
            st.error("⚠️ کێشت کەمە (Underweight)")
        elif 18.5 <= bmi < 25:
            st.success("✅ کێشت زۆر گونجاوە (Normal Weight)")
        elif 25 <= bmi < 30:
            st.warning("🟠 کێشت کەمێک زیادە (Overweight)")
        else:
            st.error("🔴 قەڵەوی (Obesity)")
