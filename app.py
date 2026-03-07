import streamlit as st
import pandas as pd

# --- 1. ڕێکخستنی سەرەکی لاپەڕە ---
st.set_page_config(page_title="تاقیگەی زیرەک", layout="centered")

# --- 2. دیزاینی CSS بۆ هاوشێوەکردنی وێنە ئەسڵییەکە ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #1a1a1a !important;
        direction: rtl; text-align: right;
        font-family: 'Vazirmatn', sans-serif;
    }
    header {visibility: hidden;}
    .stButton>button {
        background-color: #262626 !important;
        color: white !important;
        border: 1px solid #333 !important;
        border-radius: 12px !important;
        padding: 20px 5px !important;
        font-size: 14px !important;
        font-weight: bold !important;
        width: 100% !important;
        height: 100px !important;
        transition: 0.3s !important;
    }
    .stButton>button:hover { border-color: #4ea88d !important; background-color: #333 !important; }
    .info-box {
        background-color: #262626; padding: 15px; border-radius: 12px;
        border-right: 5px solid #4ea88d; margin-bottom: 10px; color: white;
    }
    .test-title { color: #4ea88d; font-weight: bold; font-size: 17px; }
    h2, h3, p, label, .stMarkdown { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. سیستەمی گۆڕینی لاپەڕە ---
if 'page' not in st.session_state:
    st.session_state.page = "main"

# --- 4. شاشەی سەرەکی (Grid 3x3) ---
if st.session_state.page == "main":
    st.markdown('<h2 style="text-align:center;">دکتۆر دانیال - تاقیگەی زیرەک</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔬\nتاقیگە\n(پشکنینەکان)"): st.session_state.page = "lab"
        if st.button("🦠\nنەخۆشییەکان"): pass
        if st.button("💊\nدەرمانە نوێیەکان"): pass
    with col2:
        if st.button("⚖️\nBMI\nحیسابکردن"): st.session_state.page = "bmi"
        if st.button("🍎\nڤیتامینەکان"): pass
        if st.button("⚕️\nفڕۆشگا"): pass
    with col3:
        if st.button("🧠\nوەرگێڕی\nزیرەک"): st.session_state.page = "interpreter"
        if st.button("📋\nڕێنمایی\nپێش پشکنین"): st.session_state.page = "guidelines"
        if st.button("👨‍⚕️\nنیشانە و\nپشکنین"): st.session_state.page = "symptoms"

    st.markdown('<div class="info-box" style="margin-top:20px; font-size:13px;">ئەم بەرنامەیە هەموو زانیارییەکانی تاقیگە لەخۆ دەگرێت بە وردی.</div>', unsafe_allow_html=True)

# --- 5. بەشی تاقیگە (هەموو پشکنینەکان لێرەیە) ---
elif st.session_state.page == "lab":
    if st.button("🔙 گەڕانەوە"): st.session_state.page = "main"; st.rerun()
    st.header("🔬 هەموو پشکنینەکانی تاقیگە")
    
    lab_sections = {
        "1. Hematology": {
            "CBC": "پشکنینی گشتی خوێن (Hb, WBC, Plt). | ئاسایی: Hb 12-17 | کات: ٣٠ خولەک",
            "ESR": "نیشاندەری هەوکردن. | ئاسایی: 0-20 mm/hr | کات: ١ کاتژمێر",
            "PT/PTT": "مەیینی خوێن. | ئاسایی: PT 11-13s | کات: ١ کاتژمێر",
            "PCV": "چڕی خوێن. | ئاسایی: 37-52% | کات: ٣٠ خولەک"
        },
        "2. Clinical Chemistry": {
            "Blood Sugar (FBS)": "شەکری بەڕۆژوو. | ئاسایی: 70-100 mg/dL | کات: ٣٠ خولەک",
            "Creatinine": "فرمانی گورچیلە. | ئاسایی: 0.6-1.2 mg/dL | کات: ١ کاتژمێر",
            "Urea": "پاشماوەی نایترۆجینی. | ئاسایی: 15-45 mg/dL | کات: ١ کاتژمێر",
            "ALT/AST": "ئەنزیمی جگەر. | ئاسایی: <40 U/L | کات: ١ کاتژمێر",
            "Lipid Profile": "چەوری خوێن (Chol, TG, HDL, LDL). | ئاسایی: Chol <200 | کات: ٢ کاتژمێر"
        },
        "3. Microbiology": {"Urine Culture": "کات: ٣ ڕۆژ", "GSE": "پیسایی گشتی. | ٣٠ خولەک"},
        "4. Urinalysis": {"GUE": "میزی گشتی. | ٣٠ خولەک"},
        "5. Serology": {"CRP": "هەوکردنی تیژ. | ئاسایی: <6", "Widal": "تیفۆید. | <1/80"},
        "6. Tumor Markers": {"PSA": "پڕۆستات. | <4 ng/ml", "CA-125": "هێلکەدان. | <35"},
        "7. Molecular": {"PCR (Viral Load)": "دەستنیشانکردنی وردی ڤایرۆس. | کات: ٢-٣ ڕۆژ"},
        "8. Hormones": {"TSH": "غودە. | 0.4-4.5", "Vit D3": "ڤیتامین D. | 30-100", "Prolactin": "٤ کاتژمێر"}
    }
    
    search = st.text_input("🔎 گەڕان بۆ پشکنین...")
    for cat, tests in lab_sections.items():
        with st.expander(cat):
            for t_name, t_cont in tests.items():
                if search.lower() in t_name.lower():
                    st.markdown(f'<div class="info-box"><span class="test-title">🧪 {t_name}</span><br>{t_cont}</div>', unsafe_allow_html=True)

# --- 6. بەشی BMI ---
elif st.session_state.page == "bmi":
    if st.button("🔙 گەڕانەوە"): st.session_state.page = "main"; st.rerun()
    st.header("⚖️ حیسابکردنی BMI")
    w = st.number_input("کێش (kg):", value=70.0)
    h = st.number_input("باڵا (cm):", value=170.0)
    if h > 0:
        bmi = w / ((h/100)**2)
        st.markdown(f'<div class="info-box">دەرەنجامی تۆ: {bmi:.1f}</div>', unsafe_allow_html=True)
        if bmi < 18.5: st.warning("کێشت کەمە")
        elif bmi < 25: st.success("کێشت ئاساییە")
        else: st.error("قەڵەوی یان کێشی زیادە")

# --- 7. بەشی وەرگێڕی زیرەک ---
elif st.session_state.page == "interpreter":
    if st.button("🔙 گەڕانەوە"): st.session_state.page = "main"; st.rerun()
    st.header("🧠 وەرگێڕی زیرەکی ئەنجامەکان")
    test_type = st.selectbox("پشکنین هەڵبژێرە:", ["FBS (Sugar)", "Hb (Blood)", "Creatinine"])
    val = st.number_input("ئەنجامەکە بنووسە:", value=0.0)
    if val > 0:
        if test_type == "FBS (Sugar)":
            if val <= 100: st.success("ئاساییە")
            elif val <= 125: st.warning("پێش شەکرە")
            else: st.error("بەرزە")
        elif test_type == "Hb (Blood)":
            if val < 12: st.error("کەمخوێنی")
            else: st.success("ئاساییە")

# --- 8. ڕێنمایی و نیشانەکان ---
elif st.session_state.page == "guidelines":
    if st.button("🔙 گەڕانەوە"): st.session_state.page = "main"; st.rerun()
    st.header("📋 ڕێنماییەکان")
    st.markdown('<div class="info-box">١. بەڕۆژووبوون (٨-١٢ کاتژمێر) بۆ شەکرە و چەوری.<br>٢. نەکردنی وەرزشی قورس پێش پشکنین.</div>', unsafe_allow_html=True)

elif st.session_state.page == "symptoms":
    if st.button("🔙 گەڕانەوە"): st.session_state.page = "main"; st.rerun()
    st.header("🩺 پشکنین بەپێی نیشانەکان")
    sym = st.selectbox("نیشانەکان:", ["ماندوێتی زۆر", "ئازاری جومگە", "کێشەی میزکردن"])
    if sym == "ماندوێتی زۆر": st.info("پێشنیار: CBC, TSH, Vit D3, Ferritin")
