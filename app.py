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
    .main-grid {
        display: grid; grid-template-columns: repeat(3, 1fr);
        gap: 12px; padding: 10px;
    }
    .menu-card {
        background-color: #262626; border-radius: 15px;
        padding: 20px 10px; text-align: center;
        border: 1px solid #333; transition: 0.3s; color: white;
    }
    .icon-container { font-size: 30px; margin-bottom: 8px; display: block; }
    .card-text { font-size: 13px; font-weight: bold; }
    h2, p, label, .stMarkdown { color: white !important; }
    .stButton>button { width: 100%; background-color: #262626; color: white; border: 1px solid #4ea88d; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. بنکەدراوەی تەواوەتی پشکنینەکان ---
full_data = {
    "Hematology": {
        "CBC": "پشکنینی گشتی خوێن. | ئاسایی: Hb 12-17 | کات: ٣٠ خولەک",
        "ESR": "هەوکردنی گشتی. | ئاسایی: 0-20 | کات: ١ کاتژمێر",
        "PT/PTT": "مەیینی خوێن. | کات: ١ کاتژمێر",
        "PCV": "چڕی خوێن. | ئاسایی: 37-52%"
    },
    "Chemistry": {
        "FBS": "شەکری بەڕۆژوو. | ئاسایی: 70-100 | کات: ٣٠ خولەک",
        "Creatinine": "گورچیلە. | ئاسایی: 0.6-1.2 | کات: ١ کاتژمێر",
        "ALT/AST": "جگەر. | ئاسایی: <40 | کات: ١ کاتژمێر",
        "Lipids": "چەورییەکان. | ئاسایی: Chol <200"
    }
}

# --- 4. سەردێڕ ---
st.markdown('<h2 style="text-align:right;">🏥 دکتۆر دانیال - تاقیگە</h2>', unsafe_allow_html=True)

# --- 5. دروستکردنی گریدەکە (کارتەکان) ---
# بەکارهێنانی دوگمە بۆ ئەوەی هەر کارتێک کار بکات
col1, col2, col3 = st.columns(3)
with col1:
    btn_hem = st.button("🔬\nHematology")
    btn_path = st.button("🧫\nPathology")
    btn_bmi = st.button("⚖️\nBMI Calc")
with col2:
    btn_chem = st.button("🧪\nChemistry")
    btn_horm = st.button("⚠️\nHormones")
    btn_ai = st.button("🧠\nAI Interpreter")
with col3:
    btn_micro = st.button("🦠\nMicrobiology")
    btn_symp = st.button("🩺\nSymptom")
    btn_guide = st.button("📲\nDownload App")

st.divider()

# --- 6. لۆژیکی کارکردنی کارتەکان (بێ کەمکردنەوەی زانیاری) ---

if btn_hem:
    st.subheader("🔬 بەشی Hematology")
    for t, v in full_data["Hematology"].items():
        st.markdown(f"**{t}**: {v}")

elif btn_chem:
    st.subheader("🧪 بەشی Clinical Chemistry")
    for t, v in full_data["Chemistry"].items():
        st.markdown(f"**{t}**: {v}")

elif btn_bmi:
    st.subheader("⚖️ BMI Calculator")
    w = st.number_input("کێش (kg):", value=70.0)
    h = st.number_input("باڵا (cm):", value=170.0)
    if h > 0:
        bmi = w / ((h/100)**2)
        st.success(f"BMI Score: {bmi:.1f}")
        if bmi < 18.5: st.warning("کێشت کەمە")
        elif bmi < 25: st.info("کێشت ئاساییە")
        else: st.error("کێشت زیادەیە")

elif btn_ai:
    st.subheader("🧠 وەرگێڕی زیرەک")
    test_sel = st.selectbox("پشکنین:", ["FBS", "Hb"])
    val = st.number_input("ئەنجامەکە:")
    if val > 0:
        if test_sel == "FBS" and val > 100: st.error("بەرزە")
        elif test_sel == "Hb" and val < 12: st.error("کەمخوێنی")
        else: st.success("ئاساییە")

elif btn_symp:
    st.subheader("🩺 ڕێبەری نیشانەکان")
    sym = st.selectbox("نیشانە:", ["ماندوێتی", "ئازاری جومگە"])
    if sym == "ماندوێتی": st.info("پشکنین: CBC, Ferritin, Vit D3, TSH")

elif btn_guide:
    st.subheader("📲 دابەزاندنی ئەپ")
    st.write("لەسەر ئایفۆن Share و پاشان Add to Home Screen دابگرە.")

# ئەگەر هیچیان کلیک نەکرابوو، بەشی گەڕانەکە نیشان بدە
if not (btn_hem or btn_chem or btn_bmi or btn_ai or btn_symp or btn_guide):
    search = st.text_input("🔎 گەڕانی خێرا لە پشکنینەکان...")
    if search:
        st.write(f"ئەنجامی گەڕان بۆ: {search}")
