import streamlit as st
import pandas as pd

# --- 1. ڕێکخستنی لاپەڕە ---
st.set_page_config(page_title="ڕێبەری گشتگیری تاقیگە", layout="centered")

# --- 2. سیستەمی Dark Mode لە Sidebar ---
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

# --- 3. دیزاینی CSS ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;700&display=swap');
    html, body, .stApp {{ 
        direction: rtl; text-align: right; font-family: 'Vazirmatn', sans-serif;
        background-color: {bg_color}; color: {text_color} !important;
    }}
    .info-box {{ 
        padding: 15px; border-radius: 12px; background-color: {card_bg}; 
        color: {text_color} !important; border-right: 6px solid #3e7e69; 
        margin-top: 5px; line-height: 1.8;
    }}
    .test-title {{ color: {label_color} !important; font-weight: bold; font-size: 19px; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. شاشەی سەرەکی ---
st.markdown('<p style="text-align:center; color:#888; font-size: 14px; margin-bottom:5px;">Developed by: Dr. Danyal</p>', unsafe_allow_html=True)
st.markdown(f'<h1 style="text-align:center; margin-top:0; color:#3e7e69;">🏥 ڕێبەری گشتگیری تاقیگە</h1>', unsafe_allow_html=True)

# --- 5. بەشی گەڕان ---
search_query = st.text_input("🔎 گەڕان بۆ پشکنین، نیشانەکان یان کۆدەکان...")

# --- 6-8. پشکنینەکان ---
full_lab_data = {
    "1. Hematology": {"CBC": "Hb, WBC, RBC, Plt.", "ESR": "هەوکردن."},
    "2. Clinical Chemistry": {"Blood Sugar": "شەکرە.", "Creatinine": "گورچیلە."},
    "3. Microbiology": {"Culture": "چاندن."},
    "4. Urinalysis": {"GUE": "میز."},
    "5. Serology": {"CRP": "هەوکردن."},
    "6. Pathology": {"PSA": "پڕۆستات."},
    "7. Molecular": {"PCR": "ڤایرۆس."},
    "8. Hormones": {"TSH": "غودە.", "Vit D3": "ڤیتامین."}
}

for cat, tests in full_lab_data.items():
    with st.expander(cat):
        for t_name, t_cont in tests.items():
            st.markdown(f'<span class="test-title">🧪 {t_name}</span><div class="info-box">{t_cont}</div>', unsafe_allow_html=True)

# --- 9-12. تایبەتمەندییە زیرەکەکان ---
with st.expander("9. BMI Calculator"):
    st.write("دیاریکردنی کێشی گونجاو.")

with st.expander("10. ڕێنماییەکانی پێش پشکنین"):
    st.write("بەڕۆژووبوون و دەرمان.")

with st.expander("11. وەرگێڕی زیرەک"):
    st.write("تێگەیشتن لە ئەنجامەکان.")

with st.expander("12. Results Tracker"):
    st.write("گرافی گۆڕانکارییەکان.")

# --- 13. پشکنین بەپێی نیشانەکان (Professional Symptom Guide) ---

with st.expander("13. پشکنینەکان بەپێی نیشانەکان (Symptom Guide)"):
    symptom = st.selectbox("هەست بە چ نیشانەیەک دەکەیت؟", ["ماندوێتی زۆر", "کێشەی هەرسی گەدە", "جومگە ئێشە"])
    if symptom == "ماندوێتی زۆر":
        st.info("Pشکنینە پێشنیارکراوەکان: CBC, Ferritin, TSH, Vitamin D3")
    elif symptom == "کێشەی هەرسی گەدە":
        st.info("Pشکنینە پێشنیارکراوەکان: GUE, GSE, H. Pylori Ag")
    elif symptom == "جومگە ئێشە":
        st.info("Pشکنینە پێشنیارکراوەکان: RF, Anti-CCP, S. Uric Acid, CRP")

# --- 14. فەرهەنگی کورتکراوە پزیشکییەکان ---
with st.expander("14. فەرهەنگی کورتکراوە پزیشکییەکان (Medical Glossary)"):
    st.markdown("""
    - **NPO:** بەڕۆژووبوون (هیچ نەخواردن لەدوای نیوەشەو).
    - **Stat:** بەپەلە (پێویستە پشکنینەکە یەکسەر بکرێت).
    - **Reference Range:** مەودای ئاسایی پشکنینەکە.
    - **Hemolysis:** تێکچوونی خانەکانی خوێن لەناو نموونەکەدا.
    """)
