import streamlit as st

# --- 1. ڕێکخستنی لاپەڕە ---
st.set_page_config(page_title="ڕێبەری گشتگیری تاقیگە", layout="centered")

# --- 2. سیستەمی Dark Mode (Toggle) ---
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

with st.sidebar:
    st.title("⚙️ ڕێکخستن")
    mode = st.sidebar.radio("شێوازی بینین هەڵبژێرە:", ["Light ☀️", "Dark 🌙"])
    st.session_state.dark_mode = (mode == "Dark 🌙")

# ڕێکخستنی ڕەنگەکان بە وردی بۆ دیاربوونی فۆنت
if st.session_state.dark_mode:
    bg_color = "#0e1117"
    text_color = "#FFFFFF"  # سپی تەواو بۆ فۆنت
    card_bg = "#1d2129"
    input_bg = "#262730"
    label_color = "#4ea88d" # سەوزێکی ڕووناکتر بۆ ناوی پشکنینەکان
else:
    bg_color = "#ffffff"
    text_color = "#000000"
    card_bg = "#f0f7f4"
    input_bg = "#ffffff"
    label_color = "#3e7e69"

# --- 3. دیزاینی CSS نوێکراوە بۆ ڕوونی فۆنت ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;700&display=swap');
    
    html, body, .stApp {{ 
        direction: rtl; 
        text-align: right; 
        font-family: 'Vazirmatn', sans-serif;
        background-color: {bg_color};
        color: {text_color} !important;
    }}
    
    /* چاککردنی ڕەنگی هەموو نووسینەکان */
    p, span, label, div {{
        color: {text_color} !important;
    }}

    .stTextInput input {{ 
        direction: rtl; 
        text-align: right; 
        font-size: 18px !important;
        background-color: {input_bg} !important;
        color: {text_color} !important;
        border: 2px solid #3e7e69 !important;
    }}
    
    .info-box {{ 
        padding: 15px; 
        border-radius: 12px; 
        background-color: {card_bg}; 
        color: {text_color} !important;
        border-right: 6px solid #3e7e69; 
        margin-top: 5px; 
        line-height: 1.8;
        font-weight: 500; /* فۆنتەکە کەمێک تۆختر بێت */
    }}

    /* ستایلی ناوی پشکنینەکان */
    .test-title {{
        color: {label_color} !important;
        font-weight: bold;
        font-size: 19px;
    }}

    .streamlit-expanderHeader {{
        background-color: {card_bg} !important;
        color: {text_color} !important;
        border-radius: 10px !important;
        font-weight: bold !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. بەشی سەرەوە ---
st.markdown('<p style="text-align:center; color:#888; margin-bottom:0;">Developed by: Dr. Danyal</p>', unsafe_allow_html=True)
st.markdown(f'<h1 style="text-align:center; margin-top:0; color:#3e7e69;">🏥 ڕێبەری گشتگیری تاقیگە</h1>', unsafe_allow_html=True)

# --- 5. بەشی گەڕان ---
search_query = st.text_input("🔎 ناوی پشکنین بنووسە بۆ گەڕان...")

# --- 6. بنکەدراوەی پشکنینەکان ---
full_lab_data = {
    "1. Hematology (خوێن زانی)": {
        "CBC": "پشکنینی گشتی خوێن بۆ زانینی ئاستی Hb, WBC, RBC, و Plt. بۆ دەستنیشانکردنی ئەنیمیا و هەوکردن.",
        "ESR": "ڕێژەی نیشتنی خڕۆکە سوورەکان، نیشاندەرە بۆ بوونی هەوکردن یان ڕۆماتیزم.",
        "PT & PTT": "بۆ پێوانەی کاتی مەیینی خوێن، گرنگ بۆ پێش نەشتەرگەری.",
        "PCV": "ڕێژەی قەبارەی خڕۆکە سوورەکان لە خوێندا.",
        "Reticulocyte Count": "بۆ زانینی ڕێژەی بەرهەمهێنانی خڕۆکە سوورە نوێیەکان."
    },
    "2. Clinical Chemistry": {
        "Blood Sugar (FBS/HbA1c)": "شەکری بەڕۆژوو و تێکڕای ٣ مانگ. باشترینە بۆ چاودێری نەخۆشی شەکرە.",
        "ALT & AST": "ئەنزیمەکانی جگەر، بەرزبوونیان نیشانەی زیانی خانەکانی جگەرە.",
        "Creatinine & Urea": "پشکنینی سەرەکی بۆ توانای گورچیلەکان.",
        "Lipid Profile": "Cholesterol, TG, HDL, LDL بۆ زانینی ئاستی چەورییەکان.",
        "S.Calcium": "پشکنینی کالسیۆم بۆ تەندروستی ئێسک.",
        "S.Uric Acid": "بۆ دەستنیشانکردنی نەخۆشی پادشا (Gout).",
        "Bilirubin (T/D)": "پشکنینی زەردەویی (Jaundice)."
    },
    "3. Microbiology": {
        "Urine Culture": "چاندنی میز بۆ دۆزینەوەی باکتریای زیانبەخش.",
        "Antibiogram": "دیاریکردنی کاریگەرترین دەرمانی دژەباکتریا.",
        "GSE (Stool Exam)": "پشکنینی گشتی پیسایی."
    },
    "4. Urinalysis": {
        "General Urine (U/A)": "پشکنینی گشتی میز بۆ بینینی شەکر، پڕۆتین، کێم و کریستاڵەکان."
    },
    "5. Serology & Immunology": {
        "CRP Test": "لە کاتی هەوکردنی تونددا بەرز دەبێتەوە.",
        "Widal Test": "بۆ دەستنیشانکردنی تای تیفۆید.",
        "HBsAg & HCV": "پشکنینی ڤایرۆسی جگەری جۆری B و C.",
        "Toxoplasmosis": "نەخۆشی پشیلە، گرنگ بۆ ئافرەتی دووگیان.",
        "RF & Anti-CCP": "بۆ دەستنیشانکردنی ڕۆماتیزمی جومگەکان."
    },
    "6. Pathology (Tumor Markers)": {
        "PSA": "بۆ پڕۆستاتی پیاوان.",
        "CA-125": "بۆ شێرپەنجەی هێلکەدان لە ئافرەتان.",
        "AFP": "نیشاندەر بۆ شێرپەنجەی جگەر.",
        "CEA": "نیشاندەر بۆ شێرپەنجەی کۆڵۆن."
    },
    "7. Molecular & Viral": {
        "PCR Test": "بۆ دەستنیشانکردنی وردی ڤایرۆسەکان.",
        "Karyotyping": "پشکنینی کرۆمۆسۆمەکان بۆ کێشە بۆماوەییەکان.",
        "ANA": "بۆ گومانی نەخۆشییەکانی بەرگری جەستە."
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
    st.write("---")

# --- 8. نیشاندانی لیستەکان ---
for category, tests in full_lab_data.items():
    with st.expander(category):
        for test_name, content in tests.items():
            st.markdown(f'<span class="test-title">🧪 {test_name}</span>', unsafe_allow_html=True)
            st.markdown(f'<div class="info-box">{content}</div>', unsafe_allow_html=True)
            st.write("")
