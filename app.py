import streamlit as st

# --- 1. ڕێکخستنی لاپەڕە ---
st.set_page_config(page_title="ڕێبەری گشتگیری تاقیگە", layout="centered")

# --- 2. سیستەمی Dark Mode (Toggle) ---
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

with st.sidebar:
    st.markdown('<h3 style="text-align:right;">⚙️ ڕێکخستن</h3>', unsafe_allow_html=True)
    
    # CSS بۆ بچووککردنەوەی دوگمەی Toggle و ڕێگریکردن لە درێژبوونەوەی
    st.markdown("""
        <style>
        div[data-testid="stCheckbox"] {
            width: fit-content !important;
            margin-right: 0 !important;
            margin-left: auto !important;
        }
        .dev-footer {
            font-size: 11px;
            color: #888;
            border-top: 1px solid #444;
            padding-top: 10px;
            margin-top: 20px;
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)

    mode = st.toggle("Dark Mode 🌙", value=st.session_state.dark_mode)
    st.session_state.dark_mode = mode
    
    st.markdown('<p class="dev-footer">Developed by: Dr. Danyal</p>', unsafe_allow_html=True)

# ڕێکخستنی ڕەنگەکان بەپێی دۆخی هەڵبژێردراو
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

    .stTextInput input {{ 
        direction: rtl; text-align: right; font-size: 18px !important;
        background-color: {input_bg} !important; color: {text_color} !important;
        border: 2px solid #3e7e69 !important;
    }}
    
    .info-box {{ 
        padding: 15px; border-radius: 12px; background-color: {card_bg}; 
        color: {text_color} !important; border-right: 6px solid #3e7e69; 
        margin-top: 5px; line-height: 1.8; font-weight: 500;
    }}

    .test-title {{ color: {label_color} !important; font-weight: bold; font-size: 19px; }}

    .streamlit-expanderHeader {{
        background-color: {card_bg} !important; color: {text_color} !important;
        border-radius: 10px !important; font-weight: bold !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. شاشەی سەرەکی ---
st.markdown(f'<h1 style="text-align:center; margin-top:0; color:#3e7e69;">🏥 ڕێبەری گشتگیری تاقیگە</h1>', unsafe_allow_html=True)

# --- 5. بەشی گەڕان ---
search_query = st.text_input("🔎 ناوی پشکنین بنووسە بۆ گەڕان...")

# --- 6. بنکەدراوەی پشکنینەکان (تەواوی پشکنینەکان) ---
full_lab_data = {
    "1. Hematology (خوێن زانی)": {
        "CBC": "پشکنینی گشتی خوێن بۆ زانینی ئاستی Hb, WBC, RBC, و Plt. بۆ دەستنیشانکردنی ئەنیمیا و هەوکردن.",
        "ESR": "ڕێژەی نیشتنی خڕۆکە سوورەکان، نیشاندەرە بۆ بوونی هەوکردن یان ڕۆماتیزم.",
        "PT & PTT": "بۆ پێوانەی کاتی مەیینی خوێن، گرنگ بۆ پێش نەشتەرگەری یان بەکارهێنانی وارفارین.",
        "PCV": "ڕێژەی قەبارەی خڕۆکە سوورەکان لە خوێندا، بۆ زانینی چڕی خوێن بەکاردێت.",
        "Reticulocyte Count": "بۆ زانینی ڕێژەی بەرهەمهێنانی خڕۆکە سوورە نوێیەکان لە مۆخی ئێسکدا."
    },
    "2. Clinical Chemistry": {
        "Blood Sugar (FBS/HbA1c)": "شەکری بەڕۆژوو و تێکڕای ٣ مانگ. باشترینە بۆ چاودێری نەخۆشی شەکرە.",
        "ALT & AST": "ئەنزیمەکانی جگەر، بەرزبوونیان نیشانەی زیانی خانەکانی جگەرە.",
        "Creatinine & Urea": "پشکنینی سەرەکی بۆ توانای گورچیلەکان. بەرزبوونیان نیشانەی تەمەڵی گورچیلەیە.",
        "Lipid Profile": "Cholesterol, TG, HDL, LDL بۆ زانینی ئاستی چەورییەکان و پاراستنی دڵ.",
        "S.Calcium": "پشکنینی کالسیۆم بۆ تەندروستی ئێسک و فرمانەکانی دەمار.",
        "S.Uric Acid": "بۆ دەستنیشانکردنی نەخۆشی پادشا (Gout) و بەردی گورچیلە.",
        "Bilirubin (T/D)": "پشکنینی زەردەویی (Jaundice). نیشانەی کێشەی جگەر یان تێکشکانی خوێنە."
    },
    "3. Microbiology": {
        "Urine Culture": "چاندنی میز بۆ دۆزینەوەی باکتریای زیانبەخش.",
        "Antibiogram": "دیاریکردنی کاریگەرترین دەرمانی دژەباکتریا (Antibiotic) بۆ نەخۆشەکە.",
        "GSE (Stool Exam)": "پشکنینی گشتی پیسایی بۆ دۆزینەوەی پاراسایت و کرم."
    },
    "4. Urinalysis": {
        "General Urine (U/A)": "پشکنینی گشتی میز بۆ بینینی شەکر، پڕۆتین، کێم و کریستاڵەکان."
    },
    "5. Serology & Immunology": {
        "CRP Test": "لە کاتی هەوکردنی توند یان بەکتریاییدا بەرز دەبێتەوە.",
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
        "PCR Test": "بۆ دەستنیشانکردنی وردی ڤایرۆسەکان و بڕەکەیان لە خوێندا.",
        "Karyotyping": "پشکنینی کرۆمۆسۆمەکان بۆ کێشە بۆماوەییەکان.",
        "ANA": "بۆ گومانی نەخۆشییەکانی بەرگری جەستە (وەک لوپس)."
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
