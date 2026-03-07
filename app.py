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
    .stTextInput input, .stNumberInput input, .stSelectbox [data-testid="stMarkdownContainer"] p {{ 
        direction: rtl; text-align: right; font-size: 18px !important;
        background-color: {input_bg} !important; color: {text_color} !important;
        border: 2px solid #3e7e69 !important;
    }}
    .info-box {{ 
        padding: 15px; border-radius: 12px; background-color: {card_bg}; 
        color: {text_color} !important; border-right: 6px solid #3e7e69; 
        margin-top: 5px; line-height: 1.8; margin-bottom: 10px;
    }}
    .test-title {{ color: {label_color} !important; font-weight: bold; font-size: 19px; }}
    .range-text {{ color: #e67e22 !important; font-weight: bold; font-size: 14px; }}
    .time-text {{ color: #3498db !important; font-weight: bold; font-size: 14px; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. شاشەی سەرەکی ---
st.markdown('<p style="text-align:center; color:#888; font-size: 14px; margin-bottom:5px;">Developed by: Dr. Danyal</p>', unsafe_allow_html=True)
st.markdown(f'<h1 style="text-align:center; margin-top:0; color:#3e7e69;">🏥 ڕێبەری گشتگیری تاقیگە</h1>', unsafe_allow_html=True)

# --- 5. بەشی گەڕان ---
search_query = st.text_input("🔎 ناوی پشکنین بنووسە بۆ گەڕان...")

# --- 6. بنکەدراوەی گشتگیر (بە زیادکردنی مەودای ئاسایی و کات) ---
full_lab_data = {
    "1. Hematology (خوێن زانی)": {
        "CBC (Hb, WBC, Plt)": "پشکنینی گشتی خوێن. | ئاسایی: Hb 12-16 | کات: ٣٠ خولەک",
        "ESR": "نیشاندەری هەوکردن. | ئاسایی: 0-20 mm/hr | کات: ١ کاتژمێر",
        "PT & PTT": "مەیینی خوێن. | ئاسایی: PT 11-13s | کات: ١ کاتژمێر",
        "PCV": "چڕی خوێن. | ئاسایی: 37-47% | کات: ٣٠ خولەک"
    },
    "2. Clinical Chemistry": {
        "Blood Sugar (FBS)": "شەکری بەڕۆژوو. | ئاسایی: 70-100 mg/dL | کات: ٣٠ خولەک",
        "S. Creatinine": "فرمانی گورچیلە. | ئاسایی: 0.6-1.2 mg/dL | کات: ١ کاتژمێر",
        "ALT (SGPT)": "ئەنزیمی جگەر. | ئاسایی: 7-55 U/L | کات: ١ کاتژمێر",
        "Lipid Profile": "چەوری خوێن. | ئاسایی: Chol <200 | کات: ٢ کاتژمێر",
        "S. Calcium": "کالسیۆمی خوێن. | ئاسایی: 8.5-10.5 mg/dL | کات: ١ کاتژمێر",
        "S. Uric Acid": "ترشی یوریک. | ئاسایی: 3.5-7.2 mg/dL | کات: ١ کاتژمێر"
    },
    "3. Microbiology": {
        "Urine Culture": "چاندنی میز. | ئاسایی: No Growth | کات: ٣ ڕۆژ",
        "Stool Exam (GSE)": "پیسایی گشتی. | ئاسایی: No parasite | کات: ٣٠ خولەک"
    },
    "4. Urinalysis": {
        "General Urine (GUE)": "میزی گشتی. | ئاسایی: Negative | کات: ٣٠ خولەک"
    },
    "5. Serology & Immunology": {
        "CRP Test": "هەوکردنی جەستە. | ئاسایی: <6 mg/L | کات: ٣٠ خولەک",
        "Widal Test": "تیفۆید. | ئاسایی: <1/80 | کات: ١ کاتژمێر",
        "RF (Rheumatoid Factor)": "ڕۆماتیزم. | ئاسایی: <14 IU/mL | کات: ١ کاتژمێر"
    },
    "6. Pathology (Tumor Markers)": {
        "PSA (Prostate)": "پڕۆستات. | ئاسایی: <4 ng/mL | کات: ٤ کاتژمێر",
        "CA-125": "هێلکەدان. | ئاسایی: <35 U/mL | کات: ٤ کاتژمێر"
    },
    "7. Molecular & Viral": {
        "PCR (HCV/HBV)": "ڤایرۆسی جگەر. | ئاسایی: Not Detected | کات: ٢ ڕۆژ"
    },
    "8. Endocrinology & Hormones": {
        "TSH (Thyroid)": "غودە. | ئاسایی: 0.4-4.0 mIU/L | کات: ٤ کاتژمێر",
        "Vitamin D3": "ڤیتامین D. | ئاسایی: 30-100 ng/mL | کات: ٢٤ کاتژمێر"
    }
}

# --- 7. ئەنجامی گەڕان ---
if search_query:
    for cat, tests in full_lab_data.items():
        for t_name, t_cont in tests.items():
            if search_query.lower() in t_name.lower():
                st.markdown(f'<div class="info-box"><span class="test-title">🧪 {t_name}</span><br>{t_cont}</div>', unsafe_allow_html=True)

# --- 8. نیشاندانی لیستەکان (1-8) ---
for category, tests in full_lab_data.items():
    with st.expander(category):
        for t_name, content in tests.items():
            st.markdown(f'<span class="test-title">🧪 {t_name}</span><div class="info-box">{content}</div>', unsafe_allow_html=True)

# --- 9. BMI ---
with st.expander("9. BMI Calculator"):
    col1, col2 = st.columns(2)
    w = col1.number_input("کێش (kg):", value=70.0, key="w9")
    h = col2.number_input("باڵا (cm):", value=170.0, key="h9")
    if h > 0: st.info(f"BMI Score: {w/((h/100)**2):.1f}")

# --- 10. ڕێنماییەکان ---
with st.expander("10. ڕێنماییەکانی پێش پشکنین"):
    st.write("بەڕۆژووبوون بۆ پشکنینەکان زۆر گرنگە.")

# --- 11. وەرگێڕی زیرەک ---
with st.expander("11. وەرگێڕی زیرەکی ئەنجامەکان"):
    v11 = st.number_input("ئەنجامەکە بنووسە:", value=0.0, key="v11")
    if v11 > 100: st.error("📈 ئەنجامەکە بەرزە")

# --- 12. Tracker ---
with st.expander("12. چاودێری گەشەی پشکنینەکان"):
    st.write("لێرەدا دەتوانیت گراف دروست بکەیت بۆ ئەنجامەکانت.")

# --- 13. Symptom Guide ---
with st.expander("13. پشکنینەکان بەپێی نیشانەکان"):
    symp = st.selectbox("نیشانە:", ["ماندوێتی زۆر", "کێشەی هەرس"])
    if symp == "ماندوێتی زۆر": st.warning("پێشنیار: CBC, Ferritin, TSH")
