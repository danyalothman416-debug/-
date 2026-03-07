import streamlit as st
import pandas as pd

# --- 1. ڕێکخستنی لاپەڕە ---
st.set_page_config(page_title="تەندروستی زیرەک", layout="centered")

# --- 2. دیزاینی CSS بۆ هاوشێوەکردنی وێنەکە ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #1a1a1a !important;
        direction: rtl; text-align: right;
        font-family: 'Vazirmatn', sans-serif;
    }
    header {visibility: hidden;}
    
    /* ستایلی دوگمەکان وەک کارت */
    .stButton>button {
        background-color: #262626 !important;
        color: white !important;
        border: 1px solid #333 !important;
        border-radius: 15px !important;
        padding: 25px 10px !important;
        font-size: 15px !important;
        font-weight: bold !important;
        width: 100% !important;
        transition: 0.3s !important;
        line-height: 1.5 !important;
    }
    .stButton>button:hover {
        border-color: #4ea88d !important;
        background-color: #333 !important;
    }
    
    .info-box {
        background-color: #262626; padding: 15px; border-radius: 12px;
        border-right: 5px solid #4ea88d; margin-bottom: 10px; color: white;
    }
    h2, h3, p, label { color: white !important; }
    .test-title { color: #4ea88d; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. سەردێڕ ---
st.markdown('<h2 style="text-align:right;">🏥 دکتۆر دانیال - تاقیگە</h2>', unsafe_allow_html=True)

# --- 4. دروستکردنی کارتەکان (3x3 Grid) ---
col1, col2, col3 = st.columns(3)

with col1:
    btn_lab = st.button("🔬\nتاقیگە\n(پشکنینەکان)")
    btn_bmi = st.button("⚖️\nکێشی گونجاو\n(BMI)")
    btn_new_meds = st.button("💊\nدەرمانە\nنوێیەکان")

with col2:
    btn_ai = st.button("🧠\nوەرگێڕی\nزیرەک")
    btn_vit = st.button("🍎\nڤیتامینەکان\n(بەردەستە)")
    btn_tracker = st.button("📊\nچاودێری\nئەنجامەکان")

with col3:
    btn_guide = st.button("📋\nڕێنمایی\nپێش پشکنین")
    btn_symp = st.button("🩺\nنیشانە و\nپشکنین")
    btn_app = st.button("📲\nدابەزاندنی\nئەپ")

st.divider()

# --- 5. بنکەدراوەی پشکنینەکان (١٢ خاڵەکە لێرەدا کۆکراوەتەوە) ---
full_lab_data = {
    "1. Hematology": {
        "CBC": "Hb, WBC, RBC, Plt. | ئاسایی: Hb 12-17 | کات: ٣٠ خولەک",
        "ESR": "نیشاندەری هەوکردن. | ئاسایی: 0-20 | کات: ١ کاتژمێر",
        "PT & PTT": "مەیینی خوێن. | ئاسایی: PT 11-13s | کات: ١ کاتژمێر",
        "PCV": "چڕی خوێن. | ئاسایی: 37-52% | کات: ٣٠ خولەک"
    },
    "2. Clinical Chemistry": {
        "Blood Sugar (FBS)": "شەکری بەڕۆژوو. | ئاسایی: 70-100 | کات: ٣٠ خولەک",
        "Creatinine": "فرمانی گورچیلە. | ئاسایی: 0.6-1.2 | کات: ١ کاتژمێر",
        "ALT & AST": "ئەنزیمەکانی جگەر. | ئاسایی: <40 | کات: ١ کاتژمێر",
        "Lipid Profile": "چەوری خوێن. | ئاسایی: Chol <200 | کات: ٢ کاتژمێر"
    },
    "3. Microbiology": {"Urine Culture": "کات: ٣ ڕۆژ", "GSE": "پیسایی گشتی. | ٣٠ خولەک"},
    "4. Urinalysis": {"GUE": "میزی گشتی. | کات: ٣٠ خولەک"},
    "5. Serology": {"CRP": "هەوکردن. | ئاسایی: <6", "Widal": "تیفۆید. | <1/80"},
    "6. Tumor Markers": {"PSA": "پڕۆستات. | <4 ng/ml", "CA-125": "هێلکەدان. | <35"},
    "7. Molecular": {"PCR": "ڤایرۆسەکان. | کات: ٢ ڕۆژ"},
    "8. Hormones": {"TSH": "غودە. | 0.4-4.5", "Vit D3": "ڤیتامین. | 30-100"}
}

# --- 6. لۆژیکی کارکردنی کارتەکان ---

# ئەگەر کلیکی لەسەر تاقیگە کرد (هەموو پشکنینەکان)
if btn_lab:
    st.subheader("🔬 هەموو بەشەکانی تاقیگە")
    search = st.text_input("🔎 گەڕان لە ناو پشکنینەکان...")
    for cat, tests in full_lab_data.items():
        with st.expander(cat):
            for t_name, t_cont in tests.items():
                st.markdown(f'<div class="info-box"><span class="test-title">🧪 {t_name}</span><br>{t_cont}</div>', unsafe_allow_html=True)

# ئەگەر کلیکی لەسەر BMI کرد
elif btn_bmi:
    st.subheader("⚖️ BMI Calculator")
    w = st.number_input("کێش (kg):", value=70.0)
    h = st.number_input("باڵا (cm):", value=170.0)
    if h > 0:
        bmi = w / ((h/100)**2)
        st.success(f"دەرەنجام: {bmi:.1f}")
        if bmi < 18.5: st.warning("کێشت کەمە")
        elif bmi < 25: st.info("کێشت ئاساییە")
        else: st.error("کێشت زیادەیە")

# ئەگەر کلیکی لەسەر وەرگێڕی زیرەک کرد
elif btn_ai:
    st.subheader("🧠 وەرگێڕی زیرەکی ئەنجامەکان")
    test_type = st.selectbox("پشکنین:", ["شەکری بەڕۆژوو (FBS)", "S. Creatinine", "Hemoglobin (Hb)"])
    val = st.number_input("ئەنجامەکە بنووسە:", value=0.0)
    if val > 0:
        if test_type == "شەکری بەڕۆژوو (FBS)":
            if val <= 100: st.success("ئاساییە")
            else: st.error("بەرزە")

# ئەگەر کلیکی لەسەر ڕێنماییەکان کرد
elif btn_guide:
    st.subheader("📋 ڕێنماییەکانی پێش پشکنین")
    st.markdown('<div class="info-box">١. بەڕۆژووبوون بۆ شەکرە و چەوری.<br>٢. ئاگادارکردنەوە لە دەرمانەکان.</div>', unsafe_allow_html=True)

# ئەگەر کلیکی لەسەر نیشانەکان کرد
elif btn_symp:
    st.subheader("🩺 پشکنین بەپێی نیشانەکان")
    sym = st.selectbox("نیشانە:", ["ماندوێتی زۆر", "کێشەی هەرس"])
    if sym == "ماندوێتی زۆر": st.info("پێشنیار: CBC, TSH, Vit D3")

# ئەگەر کلیکی لەسەر دابەزاندن کرد
elif btn_app:
    st.subheader("📲 دابەزاندنی ئەپ")
    st.write("لە وێبگەڕەکەتدا Add to Home Screen دابگرە.")

# --- بەشی خوارەوە ---
st.markdown('<p style="text-align:center; font-size:12px; color:#666;">هەموو مافێکی پارێزراوە بۆ دکتۆر دانیال</p>', unsafe_allow_html=True)
