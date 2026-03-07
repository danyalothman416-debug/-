import streamlit as st
import pandas as pd

# --- 1. ڕێکخستنی لاپەڕە ---
st.set_page_config(page_title="ڕێبەری گشتگیری تاقیگە", layout="centered")

# --- زیادکردنی تایبەتمەندی Add to Home Screen (PWA Meta Tags) ---
st.markdown("""
    <head>
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black">
    <meta name="apple-mobile-web-app-title" content="Lab Guide">
    <link rel="apple-touch-icon" href="https://cdn-icons-png.flaticon.com/512/3063/3063176.png">
    </head>
    <script>
    // پەیامێک بۆ بەکارهێنەرانی ئایفۆن و ئەندرۆید
    if (window.navigator.standalone === false) {
        console.log("Add to Home Screen prompt");
    }
    </script>
""", unsafe_allow_html=True)

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

    st.divider()
    st.markdown("📲 **دابەزاندنی بەرنامە:**")
    st.info("بۆ دابەزاندنی ئەم ئەپە، لە وێبگەڕەکەتدا (Chrome یان Safari) کلیک لە سێ خاڵەکە یان دوگمەی Share بکە و 'Add to Home Screen' هەڵبژێرە.")

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

# --- 6. بنکەدراوەی دەوڵەمەندی پشکنینەکان ---
full_lab_data = {
    "1. Hematology (خوێن زانی)": {
        "CBC": "پشکنینی گشتی خوێن بۆ Hb, WBC, RBC, Plt. بۆ دەستنیشانکردنی ئەنیمیا و هەوکردن. | ئاسایی: Hb 12-17 | کات: ٣٠ خولەک",
        "ESR": "ڕێژەی نیشتنی خڕۆکە سوورەکان، نیشاندەرە بۆ بوونی هەوکردن. | ئاسایی: 0-20 mm/hr | کات: ١ کاتژمێر",
        "PT & PTT": "بۆ کاتی مەیینی خوێن، گرنگ بۆ پێش نەشتەرگەری. | ئاسایی: PT 11-13s | کات: ١ کاتژمێر",
        "PCV": "ڕێژەی قەبارەی خڕۆکە سوورەکان، بۆ زانینی چڕی خوێن. | ئاسایی: 37-52% | کات: ٣٠ خولەک",
        "Reticulocyte Count": "بۆ زانینی ڕێژەی بەرهەمهێنانی خڕۆکە سوورە نوێیەکان. | ئاسایی: 0.5-1.5% | کات: ٢ کاتژمێر"
    },
    "2. Clinical Chemistry": {
        "Blood Sugar (FBS/HbA1c)": "شەکری بەڕۆژوو و تێکڕای ٣ مانگ. | ئاسایی: FBS 70-100 mg/dL | کات: ٣٠ خولەک",
        "ALT & AST": "ئەنزیمەکانی جگەر، نیشانەی زیانی خانەکانی جگەرە. | ئاسایی: <40 U/L | کات: ١ کاتژمێر",
        "Creatinine & Urea": "پشکنینی سەرەکی بۆ توانای گورچیلەکان. | ئاسایی: Cr 0.6-1.2 | کات: ١ کاتژمێر",
        "Lipid Profile": "Cholesterol, TG, HDL, LDL بۆ چەوری خوێن. | ئاسایی: Chol <200 | کات: ٢ کاتژمێر",
        "S.Calcium": "پشکنینی کالسیۆم بۆ تەندروستی ئێسک. | ئاسایی: 8.5-10.5 mg/dL | کات: ١ کاتژمێر",
        "S.Uric Acid": "بۆ زانینی ئاستی ترشی یوریک و نەخۆشی جومگە. | ئاسایی: 3.5-7.2 | کات: ١ کاتژمێر",
        "Bilirubin (T/D)": "پشکنینی زەردەویی. | ئاسایی: Total <1.2 mg/dL | کات: ١ کاتژمێر"
    },
    "3. Microbiology": {
        "Urine Culture": "چاندنی میز بۆ دۆزینەوەی باکتریای زیانبەخش. | کات: ٣ ڕۆژ",
        "Antibiogram": "دیاریکردنی دژەباکتریای گونجاو. | کات: ٣ ڕۆژ",
        "GSE (Stool Exam)": "پشکنینی گشتی پیسایی بۆ پاراسایت. | کات: ٣٠ خولەک"
    },
    "4. Urinalysis": {
        "General Urine (U/A)": "پشکنینی گشتی میز بۆ بینینی شەکر و پڕۆتین. | کات: ٣٠ خولەک"
    },
    "5. Serology & Immunology": {
        "CRP Test": "لە کاتی هەوکردنی توند یان بەکتریاییدا بەرز دەبێتەوە. | ئاسایی: <6 mg/L | کات: ٣٠ خولەک",
        "Widal Test": "بۆ دەستنیشانکردنی تای تیفۆید. | ئاسایی: <1/80 | کات: ١ کاتژمێر",
        "HBsAg & HCV": "پشکنینی ڤایرۆسی جگەری جۆری B و C. | ئاسایی: Non-reactive | کات: ١ کاتژمێر",
        "Toxoplasmosis": "نەخۆشی پشیلە، گرنگ بۆ ئافرەتی دووگیان. | کات: ٢ کاتژمێر",
        "RF & Anti-CCP": "بۆ دەستنیشانکردنی ڕۆماتیزمی جومگەکان. | کات: ٢ کاتژمێر"
    },
    "6. Pathology (Tumor Markers)": {
        "PSA": "بۆ پڕۆستاتی پیاوان. | ئاسایی: <4 ng/mL | کات: ٤ کاتژمێر",
        "CA-125": "بۆ شێرپەنجەی هێلکەدان. | ئاسایی: <35 U/mL | کات: ٤ کاتژمێر",
        "AFP": "نیشاندەر بۆ شێرپەنجەی جگەر. | کات: ٤ کاتژمێر",
        "CEA": "نیشاندەر بۆ شێرپەنجەی کۆڵۆن. | کات: ٤ کاتژمێر"
    },
    "7. Molecular & Viral": {
        "PCR Test": "بۆ دەستنیشانکردنی وردی ڤایرۆسەکان. | کات: ٢ ڕۆژ",
        "Karyotyping": "پشکنینی کرۆمۆسۆمەکان. | کات: ١٠ ڕۆژ",
        "ANA": "بۆ نەخۆشییەکانی بەرگری جەستە. | کات: ٢٤ کاتژمێر"
    },
    "8. Endocrinology & Hormones": {
        "Thyroid Profile (TSH, T3, T4)": "بۆ فرمانی ڕژێنە دەرەقییەکان. | ئاسایی: TSH 0.4-4.5 | کات: ٤ کاتژمێر",
        "Vitamin D3": "پشکنینی ئاستی ڤیتامین D. | ئاسایی: 30-100 ng/mL | کات: ٢٤ کاتژمێر",
        "Prolactin": "هۆرمۆنی شیر. | کات: ٤ کاتژمێر",
        "Testosterone": "هۆرمۆنی نێرینە. | کات: ٤ کاتژمێر",
        "Insulin Test": "بۆ زانینی بڕی هۆرمۆنی ئەنسۆلین. | کات: ٤ کاتژمێر",
        "Cortisol": "هۆرمۆنی سترێس. | کات: ٤ کاتژمێر"
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
    if not found: st.warning("نەدۆزرایەوە.")

# --- 8. نیشاندانی لیستەکان (1-8) ---
for category, tests in full_lab_data.items():
    with st.expander(category):
        for test_name, content in tests.items():
            st.markdown(f'<span class="test-title">🧪 {test_name}</span>', unsafe_allow_html=True)
            st.markdown(f'<div class="info-box">{content}</div>', unsafe_allow_html=True)

# --- 9. BMI Calculator ---
with st.expander("9. BMI Calculator (دیاریکردنی کێشی گونجاو)"):
    st.markdown('<div class="info-box">ئەم بەشە بەکاردێت بۆ زانینی ئەوەی ئایا کێشت گونجاوە لەگەڵ باڵات یان نا.</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1: weight = st.number_input("کێش (kg):", min_value=1.0, value=70.0, step=0.1, key="w9")
    with col2: height = st.number_input("باڵا (cm):", min_value=50.0, value=170.0, step=0.1, key="h9")
    if height > 0:
        bmi = weight / ((height/100) ** 2)
        st.markdown(f"### **BMI دەرەنجام: {bmi:.1f}**")
        if bmi < 18.5: st.error("⚠️ کێشت کەمە (Underweight)")
        elif 18.5 <= bmi < 25: st.success("✅ کێشت زۆر گونجاوە (Normal Weight)")
        elif 25 <= bmi < 30: st.warning("🟠 کێشت کەمێک زیادە (Overweight)")
        else: st.error("🔴 قەڵەوی (Obesity)")

# --- 10. ڕێنماییەکانی پێش پشکنین ---
with st.expander("10. ڕێنماییەکانی پێش پشکنین (Pre-test Instructions)"):
    st.markdown("""
    <div class="info-box">
    - <b>بەڕۆژوو بوون (Fasting):</b> بۆ پشکنینەکانی شەکرە (8-10 کاتژمێر) و چەوری خوێن (12-14 کاتژمێر) پێویستە.<br>
    - <b>دەرمان:</b> ئاگادارکردنەوەی پزیشک یان تاقیگە لەو دەرمانانەی کە بەکاری دەهێنیت.<br>
    - <b>کات:</b> هەندێک پشکنینی هۆرمۆن پێویستە لە کاتژمێرەکانی سەرەتای بەیانی ئەنجام بدرێن.<br>
    - <b>وەرزش:</b> پێش پشکنینی پڕۆستات (PSA) پێویستە بۆ ماوەی 24 کاتژمێر وەرزشی قورس نەکرێت.
    </div>
    """, unsafe_allow_html=True)

# --- 11. وەرگێڕی زیرەکی ئەنجامەکان ---
with st.expander("11. وەرگێڕی زیرەکی ئەنجامەکان (AI Interpreter)"):
    st.markdown('<div class="info-box">جۆری پشکنینەکە هەڵبژێرە و ژمارەی ئەنجامەکە بنووسە:</div>', unsafe_allow_html=True)
    test_type = st.selectbox("پشکنین:", ["شەکری بەڕۆژوو (FBS)", "S. Creatinine", "Hemoglobin (Hb)"], key="test11")
    val = st.number_input("ئەنجامەکە بنووسە:", value=0.0, key="val11")
    if val > 0:
        if test_type == "شەکری بەڕۆژوو (FBS)":
            if val < 70: st.error("📉 نزمە (Hypoglycemia)")
            elif val <= 100: st.success("✅ ئاساییە")
            elif val <= 125: st.warning("🟠 قۆناغی پێش شەکرە (Prediabetes)")
            else: st.error("📈 بەرزە (Diabetes)")
        elif test_type == "S. Creatinine":
            if val <= 1.3: st.success("✅ فرمانی گورچیلە ئاساییە")
            else: st.error("⚠️ ئەنجامەکە بەرزە")
        elif test_type == "Hemoglobin (Hb)":
            if val < 12: st.error("🩸 کەمخوێنی (Anemia)")
            elif val <= 17: st.success("✅ ئاستی خوێن ئاساییە")
            else: st.warning("⚠️ ئاستی خوێن بەرزە")

# --- 12. چاودێری گەشەی پشکنینەکان (Results Tracker) ---
with st.expander("12. چاودێری گەشەی پشکنینەکان (Results Tracker)"):
    if 'history' not in st.session_state: st.session_state.history = pd.DataFrame(columns=["Month", "Value"])
    m_in = st.selectbox("مانگ:", ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], key="m12")
    v_in = st.number_input("ئەنجام:", value=0.0, key="v12")
    if st.button("تۆمارکردنی ئەنجام"):
        st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame({"Month": [m_in], "Value": [v_in]})], ignore_index=True)
    if not st.session_state.history.empty: st.line_chart(st.session_state.history.set_index("Month"))

# --- 13. پشکنینەکان بەپێی نیشانەکان (Symptom Guide) ---
with st.expander("13. پشکنینەکان بەپێی نیشانەکان (Symptom Guide)"):
    symp = st.selectbox("نیشانە:", ["ماندوێتی زۆر", "کێشەی هەرس", "ئازاری جومگە"], key="s13")
    if symp == "ماندوێتی زۆر": st.info("🧪 پشکنینە پێشنیارکراوەکان: CBC, Ferritin, TSH, Vitamin D3")
    elif symp == "کێشەی هەرس": st.info("🧪 پشکنینە پێشنیارکراوەکان: GUE, GSE, H. Pylori Ag, Liver Profile")
    elif symp == "ئازاری جومگە": st.info("🧪 پشکنینە پێشنیارکراوەکان: RF, Anti-CCP, CRP, S. Uric Acid")
