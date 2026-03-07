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

# --- 6. بنکەدراوەی پشکنینەکان ---
full_lab_data = {
    "1. Hematology (خوێن زانی)": {
        "CBC": "پشکنینی گشتی خوێن بۆ Hb, WBC, RBC, Plt. | ئاسایی: Hb 12-17 | کات: ٣٠ خولەک",
        "ESR": "ڕێژەی نیشتنی خڕۆکە سوورەکان. | ئاسایی: 0-20 mm/hr | کات: ١ کاتژمێر",
        "PT & PTT": "بۆ کاتی مەیینی خوێن. | ئاسایی: PT 11-13s | کات: ١ کاتژمێر",
        "PCV": "ڕێژەی قەبارەی خڕۆکە سوورەکان. | ئاسایی: 37-52% | کات: ٣٠ خولەک",
        "Reticulocyte Count": "ڕێژەی بەرهەمهێنانی خڕۆکە سوورە نوێیەکان. | ئاسایی: 0.5-1.5% | کات: ٢ کاتژمێر"
    },
    "2. Clinical Chemistry": {
        "Blood Sugar (FBS/HbA1c)": "شەکری بەڕۆژوو و تێکڕای ٣ مانگ. | ئاسایی: FBS 70-100 | کات: ٣٠ خولەک",
        "ALT & AST": "ئەنزیمەکانی جگەر. | ئاسایی: <40 U/L | کات: ١ کاتژمێر",
        "Creatinine & Urea": "پشکنینی توانای گورچیلەکان. | ئاسایی: Cr 0.6-1.2 | کات: ١ کاتژمێر",
        "Lipid Profile": "چەوری خوێن (Cholesterol, TG). | ئاسایی: Chol <200 | کات: ٢ کاتژمێر",
        "S.Calcium": "کالسیۆمی خوێن. | ئاسایی: 8.5-10.5 | کات: ١ کاتژمێر",
        "S.Uric Acid": "بۆ زانی ئاستی ترشی یوریک. | ئاسایی: 3.5-7.2 | کات: ١ کاتژمێر",
        "Bilirubin (T/D)": "پشکنینی زەردەویی. | ئاسایی: Total <1.2 | کات: ١ کاتژمێر"
    },
    "3. Microbiology": {
        "Urine Culture": "چاندنی میز. | کات: ٣ ڕۆژ",
        "Antibiogram": "دیاریکردنی دژەباکتریای گونجاو. | کات: ٣ ڕۆژ",
        "GSE (Stool Exam)": "پشکنینی گشتی پیسایی. | کات: ٣٠ خولەک"
    },
    "4. Urinalysis": {
        "General Urine (U/A)": "پشکنینی گشتی میز. | کات: ٣٠ خولەک"
    },
    "5. Serology & Immunology": {
        "CRP Test": "نیشاندەری هەوکردن. | ئاسایی: <6 mg/L | کات: ٣٠ خولەک",
        "Widal Test": "بۆ تای تیفۆید. | ئاسایی: <1/80 | کات: ١ کاتژمێر",
        "HBsAg & HCV": "ڤایرۆسی جگەری B و C. | کات: ١ کاتژمێر",
        "Toxoplasmosis": "نەخۆشی پشیلە. | کات: ٢ کاتژمێر",
        "RF & Anti-CCP": "بۆ ڕۆماتیزمی جومگەکان. | کات: ٢ کاتژمێر"
    },
    "6. Pathology (Tumor Markers)": {
        "PSA": "پڕۆستات. | ئاسایی: <4 ng/mL | کات: ٤ کاتژمێر",
        "CA-125": "هێلکەدان. | ئاسایی: <35 U/mL | کات: ٤ کاتژمێر",
        "AFP": "شێرپەنجەی جگەر. | کات: ٤ کاتژمێر",
        "CEA": "شێرپەنجەی کۆڵۆن. | کات: ٤ کاتژمێر"
    },
    "7. Molecular & Viral": {
        "PCR Test": "دەستنیشانکردنی وردی ڤایرۆسەکان. | کات: ٢ ڕۆژ",
        "Karyotyping": "پشکنینی کرۆمۆسۆمەکان. | کات: ١٠ ڕۆژ",
        "ANA": "بۆ نەخۆشییەکانی بەرگری جەستە. | کات: ٢٤ کاتژمێر"
    },
    "8. Endocrinology & Hormones": {
        "Thyroid Profile (TSH, T3, T4)": "بۆ فرمانی ڕژێنە دەرەقییەکان. | کات: ٤ کاتژمێر",
        "Vitamin D3": "ئاستی ڤیتامین D. | ئاسایی: 30-100 | کات: ٢٤ کاتژمێر",
        "Prolactin": "هۆرمۆنی شیر. | کات: ٤ کاتژمێر",
        "Testosterone": "هۆرمۆنی نێرینە. | کات: ٤ کاتژمێر",
        "Insulin Test": "بۆ بڕی هۆرمۆنی ئەنسۆلین. | کات: ٤ کاتژمێر",
        "Cortisol": "هۆرمۆنی سترێس. | کات: ٤ کاتژمێر"
    }
}

# --- 7. ئەنجامی گەڕان ---
if search_query:
    for cat, tests in full_lab_data.items():
        for t_name, t_cont in tests.items():
            if search_query.lower() in t_name.lower():
                st.markdown(f'<div class="info-box"><span class="test-title">🧪 {t_name}</span><br>{t_cont}</div>', unsafe_allow_html=True)

# --- 8-13. نیشاندانی لیستەکان ---
for category, tests in full_lab_data.items():
    with st.expander(category):
        for test_name, content in tests.items():
            st.markdown(f'<span class="test-title">🧪 {test_name}</span><div class="info-box">{content}</div>', unsafe_allow_html=True)

with st.expander("9. BMI Calculator"):
    w = st.number_input("کێش (kg):", value=70.0, key="w9")
    h = st.number_input("باڵا (cm):", value=170.0, key="h9")
    if h > 0: st.info(f"BMI Score: {w/((h/100)**2):.1f}")

with st.expander("10. ڕێنماییەکانی پێش پشکنین"):
    st.markdown('<div class="info-box">- بەڕۆژووبوون بۆ شەکرە و چەوری.<br>- ئاگادارکردنەوە لە دەرمان.</div>', unsafe_allow_html=True)

with st.expander("11. وەرگێڕی زیرەکی ئەنجامەکان"):
    test11 = st.selectbox("پشکنین:", ["شەکری بەڕۆژوو (FBS)", "Hemoglobin (Hb)"])
    val11 = st.number_input("ئەنجام:", value=0.0, key="v11")
    if val11 > 100: st.error("📈 بەرزە")

with st.expander("12. چاودێری گەشەی پشکنینەکان"):
    st.markdown('<div class="info-box">تۆمارکردنی ئەنجامەکان بۆ بینینی گراف.</div>', unsafe_allow_html=True)

with st.expander("13. پشکنینەکان بەپێی نیشانەکان"):
    st.selectbox("نیشانە:", ["ماندوێتی زۆر", "کێشەی هەرس"], key="s13")

# --- 14. خاڵی نوێ: دابەزاندنی ئەپ (Add to Screen) ---
with st.expander("14. 📲 دابەزاندنی ئەپ بۆ ناو مۆبایل"):
    st.markdown("""
    <div class="info-box" style="text-align:center;">
    بۆ ئەوەی وەک بەرنامە بەکاریبهێنیت:<br>
    <b>لەسەر iPhone:</b> کلیک لە Share بکە و پاشان <b>Add to Home Screen</b>.<br>
    <b>لەسەر Android:</b> کلیک لە سێ خاڵەکە بکە و پاشان <b>Install App</b>.
    </div>
    """, unsafe_allow_html=True)
