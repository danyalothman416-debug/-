import streamlit as st

# --- 1. ڕێکخستنی لاپەڕە ---
st.set_page_config(page_title="ڕێبەری گشتگیری تاقیگە", layout="centered")

# --- 2. سیستەمی Dark Mode (Toggle) بە ئایکۆن لە Sidebar ---
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

with st.sidebar:
    # لێرەدا تەنیا ئایکۆنەکە ماوەتەوە بەبێ نووسینی Settings
    st.markdown('<h3 style="text-align:right;">⚙️</h3>', unsafe_allow_html=True)
    
    st.markdown("""
        <style>
        /* لابردنی نووسینی تەنیشت Toggle و بچووککردنەوەی جێگاکەی */
        div[data-testid="stCheckbox"] p { font-size: 0px !important; }
        div[data-testid="stCheckbox"] { width: fit-content !important; margin-left: auto !important; }
        </style>
    """, unsafe_allow_html=True)

    mode = st.toggle("🌙", value=st.session_state.dark_mode)
    st.session_state.dark_mode = mode

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
    .stTextInput input, .stNumberInput input, .stSelectbox [data-testid="stMarkdownContainer"] p {{ 
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

# --- 6. بنکەدراوەی پشکنینەکان (١ تا ٨) ---
full_lab_data = {
    "1. Hematology (خوێن زانی)": {
        "CBC": "پشکنینی گشتی خوێن بۆ Hb, WBC, RBC, Plt.",
        "ESR": "نیشاندەری هەوکردن.",
        "PT & PTT": "مەیینی خوێن.",
        "PCV": "چڕی خوێن.",
        "Reticulocyte": "بەرهەمهێنانی خوێن."
    },
    "2. Clinical Chemistry": {
        "Blood Sugar": "شەکری بەڕۆژوو و تێکڕای ٣ مانگ.",
        "ALT & AST": "ئەنزیمەکانی جگەر.",
        "Creatinine & Urea": "توانای گورچیلەکان.",
        "Lipids": "چەوری خوێن.",
        "S.Calcium": "کالسیۆم بۆ ئێسک.",
        "S.Uric Acid": "بۆ زانینی ئاستی ترشی یوریک."
    },
    "3. Microbiology": {"Culture": "چاندنی میز.", "Antibiogram": "دژەباکتریا."},
    "4. Urinalysis": {"GUE": "پشکنینی گشتی میز."},
    "5. Serology": {"CRP": "هەوکردن.", "Widal": "تیفۆید.", "Hormones": "ڤایرۆسەکان."},
    "6. Pathology": {"Tumors": "PSA, CA-125, AFP."},
    "7. Molecular": {"PCR": "ڤایرۆسەکان."},
    "8. Endocrinology & Hormones": {"Thyroid": "TSH, T3, T4.", "Vitamin D3": "ڤیتامین D."}
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

# --- 8. نیشاندانی لیستەکان (خاڵی 1 تا 8) ---
for category, tests in full_lab_data.items():
    with st.expander(category):
        for test_name, content in tests.items():
            st.markdown(f'<span class="test-title">🧪 {test_name}</span>', unsafe_allow_html=True)
            st.markdown(f'<div class="info-box">{content}</div>', unsafe_allow_html=True)

# --- 9. خاڵی نۆیەم: BMI Calculator ---
with st.expander("9. BMI Calculator (دیاریکردنی کێشی گونجاو)"):
    w = st.number_input("کێش (kg):", value=70.0)
    h = st.number_input("باڵا (cm):", value=170.0)
    if h > 0:
        bmi = w / ((h/100)**2)
        st.write(f"BMI: {bmi:.1f}")
        if bmi < 18.5: st.error("⚠️ کێشت کەمە")
        elif 18.5 <= bmi < 25: st.success("✅ کێشت گونجاوە")
        elif 25 <= bmi < 30: st.warning("🟠 کێشت زیادە")
        else: st.error("🔴 قەڵەوی")

# --- 10. خاڵی دەیەم: ڕێنماییەکان ---
with st.expander("10. ڕێنماییەکانی پێش پشکنین"):
    st.markdown('<div class="info-box">بەڕۆژووبوون، ئاگادارکردنەوە لە دەرمان، و کاتی گونجاوی پشکنین لێرەدا گرنگن.</div>', unsafe_allow_html=True)

# --- 11. خاڵی یازدەیەم: وەرگێڕی زیرەک ---
with st.expander("11. وەرگێڕی زیرەکی ئەنجامەکان (AI Interpreter)"):
    test_type = st.selectbox("پشکنین:", ["شەکری بەڕۆژوو (FBS)", "Hemoglobin (Hb)"])
    val = st.number_input("ئەنجامەکە بنووسە:", value=0.0)
    if val > 0:
        if test_type == "شەکری بەڕۆژوو (FBS)":
            if val < 70: st.error("📉 نزمە")
            elif val <= 100: st.success("✅ ئاساییە")
            else: st.error("📈 بەرزە")
        elif test_type == "Hemoglobin (Hb)":
            if val < 12: st.error("🩸 کەمخوێنی")
            else: st.success("✅ ئاساییە")
