import streamlit as st

# --- 1. ڕێکخستنی لاپەڕە ---
st.set_page_config(page_title="ڕێبەری گشتگیری تاقیگە", layout="centered")

# --- 2. سیستەمی Dark Mode (Toggle) لە Sidebar ---
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

with st.sidebar:
    st.markdown('<h3 style="text-align:right;">⚙️ Settings</h3>', unsafe_allow_html=True)
    
    st.markdown("""
        <style>
        div[data-testid="stCheckbox"] p { font-size: 0px !important; }
        div[data-testid="stCheckbox"] { width: fit-content !important; margin-left: auto !important; }
        .stButton>button { border-radius: 8px; height: 2.5rem; font-size: 14px; }
        </style>
    """, unsafe_allow_html=True)

    mode = st.toggle("🌙", value=st.session_state.dark_mode)
    st.session_state.dark_mode = mode

    st.markdown("---")
    st.markdown('<p style="text-align:right; font-size: 14px;">📞 پەیوەندی خێرا:</p>', unsafe_allow_html=True)
    st.button("💬 WhatsApp")
    st.button("✈️ Telegram")

# ڕێکخستنی ڕەنگەکان
if st.session_state.dark_mode:
    bg_color, text_color, card_bg, input_bg, label_color = "#0e1117", "#FFFFFF", "#1d2129", "#262730", "#4ea88d"
else:
    bg_color, text_color, card_bg, input_bg, label_color = "#ffffff", "#000000", "#f0f7f4", "#ffffff", "#3e7e69"

# --- 3. دیزاینی CSS ---
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
        margin-top: 5px; line-height: 1.8;
    }}
    .test-title {{ color: {label_color} !important; font-weight: bold; font-size: 19px; }}
    .normal-range {{
        width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 14px;
    }}
    .normal-range td, .normal-range th {{
        border: 1px solid #3e7e69; padding: 8px; text-align: center;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. شاشەی سەرەکی ---
st.markdown('<p style="text-align:center; color:#888; font-size: 14px; margin-bottom:5px;">Developed by: Dr. Danyal</p>', unsafe_allow_html=True)
st.markdown(f'<h1 style="text-align:center; margin-top:0; color:#3e7e69;">🏥 ڕێبەری گشتگیری تاقیگە</h1>', unsafe_allow_html=True)

# --- 5. بەشی گەڕان ---
search_query = st.text_input("🔎 گەڕان بۆ پشکنین یان ڕێژەی ئاسایی...")

# --- 6. بنکەدراوەی پشکنینەکان (بە خشتەی ڕێژەی ئاساییەوە) ---
full_lab_data = {
    "1. Hematology (خوێن زانی)": {
        "CBC": """پشکنینی گشتی خوێن بۆ Hb, WBC, RBC, Plt.
        <table class="normal-range">
            <tr><th>Component</th><th>Normal Range</th><th>Unit</th></tr>
            <tr><td>Hemoglobin (M)</td><td>13.5 - 17.5</td><td>g/dL</td></tr>
            <tr><td>Hemoglobin (F)</td><td>12.0 - 15.5</td><td>g/dL</td></tr>
            <tr><td>WBC Count</td><td>4,500 - 11,000</td><td>cells/mcL</td></tr>
        </table>""",
        "ESR": "ڕێژەی نیشتنی خڕۆکە سوورەکان. (Normal: 0-15 mm/hr for males, 0-20 for females).",
        "PT & PTT": "بۆ کاتی مەیینی خوێن. (PT Normal: 11-13.5 seconds).",
        "PCV": "ڕێژەی قەبارەی خڕۆکە سوورەکان. (Normal: 37% - 52%).",
        "Reticulocyte Count": "بۆ زانینی ڕێژەی بەرهەمهێنانی خڕۆکە سوورە نوێیەکان."
    },
    "2. Clinical Chemistry": {
        "Blood Sugar (FBS/HbA1c)": """چاودێری شەکرە.
        <table class="normal-range">
            <tr><th>Test</th><th>Normal</th><th>Prediabetes</th></tr>
            <tr><td>FBS</td><td>70-99</td><td>100-125</td></tr>
            <tr><td>HbA1c</td><td>< 5.7%</td><td>5.7% - 6.4%</td></tr>
        </table>""",
        "ALT & AST": "ئەنزیمەکانی جگەر. (Normal ALT: 7-55 U/L).",
        "Creatinine & Urea": "توانای گورچیلەکان. (Normal Creatinine: 0.7-1.3 mg/dL).",
        "Lipid Profile": "Cholesterol, TG, HDL, LDL. (Cholesterol Normal: < 200 mg/dL).",
        "S.Calcium": "پشکنینی کالسیۆم بۆ تەندروستی ئێسک.",
        "S.Uric Acid": "بۆ نەخۆشی پادشا (Gout). (Normal: 3.5-7.2 mg/dL).",
        "Bilirubin (T/D)": "پشکنینی زەردەویی."
    },
    "3. Microbiology": {
        "Urine Culture": "چاندنی میز بۆ دۆزینەوەی باکتریا.",
        "Antibiogram": "دیاریکردنی کاریگەرترین دژەباکتریا.",
        "GSE (Stool Exam)": "پشکنینی گشتی پیسایی."
    },
    "4. Urinalysis": {
        "General Urine (U/A)": "پشکنینی گشتی میز بۆ بینینی شەکر، پڕۆتین، کێم."
    },
    "5. Serology & Immunology": {
        "CRP Test": "نیشاندەری هەوکردنی توند. (Normal: < 10 mg/L).",
        "Widal Test": "بۆ دەستنیشانکردنی تای تیفۆید.",
        "HBsAg & HCV": "پشکنینی ڤایرۆسی جگەر.",
        "Toxoplasmosis": "نەخۆشی پشیلە.",
        "RF & Anti-CCP": "بۆ ڕۆماتیزمی جومگەکان."
    },
    "6. Pathology (Tumor Markers)": {
        "PSA": "بۆ پڕۆستات. (Normal: < 4.0 ng/mL).",
        "CA-125": "بۆ شێرپەنجەی هێلکەدان.",
        "AFP": "بۆ شێرپەنجەی جگەر.",
        "CEA": "بۆ شێرپەنجەی کۆڵۆن."
    },
    "7. Molecular & Viral": {
        "PCR Test": "بۆ دەستنیشانکردنی وردی ڤایرۆسەکان.",
        "Karyotyping": "پشکنینی کرۆمۆسۆمەکان.",
        "ANA": "بۆ نەخۆشییەکانی بەرگری جەستە."
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
        st.warning("نەدۆزرایەوە.")

# --- 8. نیشاندانی لیستەکان ---
for category, tests in full_lab_data.items():
    with st.expander(category):
        for test_name, content in tests.items():
            st.markdown(f'<span class="test-title">🧪 {test_name}</span>', unsafe_allow_html=True)
            st.markdown(f'<div class="info-box">{content}</div>', unsafe_allow_html=True)
