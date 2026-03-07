import streamlit as st

# --- 1. ڕێکخستنی لاپەڕە ---
st.set_page_config(page_title="ڕێبەری گشتگیری تاقیگە", layout="centered")

# --- 2. سیستەمی Dark Mode (Toggle) ---
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# دروستکردنی دوگمەی گۆڕین لە لای چەپ (Sidebar)
with st.sidebar:
    st.title("⚙️ ڕێکخستن")
    mode = st.radio("شێوازی بینین هەڵبژێرە:", ["Light ☀️", "Dark 🌙"])
    st.session_state.dark_mode = (mode == "Dark 🌙")

# دیاریکردنی ڕەنگەکان بەپێی دۆخی هەڵبژێردراو
if st.session_state.dark_mode:
    bg_color = "#0e1117"
    text_color = "#ffffff"
    card_bg = "#1d2129"
    input_bg = "#262730"
    border_color = "#3e7e69"
else:
    bg_color = "#ffffff"
    text_color = "#000000"
    card_bg = "#f0f7f4"
    input_bg = "#ffffff"
    border_color = "#3e7e69"

# --- 3. دیزاینی CSS ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn&display=swap');
    
    html, body, .stApp {{ 
        direction: rtl; 
        text-align: right; 
        font-family: 'Vazirmatn', sans-serif;
        background-color: {bg_color};
        color: {text_color};
    }}
    
    .stTextInput input {{ 
        direction: rtl; 
        text-align: right; 
        font-size: 18px !important;
        background-color: {input_bg} !important;
        color: {text_color} !important;
        border: 1px solid {border_color} !important;
    }}
    
    .stButton>button {{
        width: 100%; border-radius: 12px; height: 3.5rem;
        background-color: #3e7e69; color: white; font-size: 18px; border: none; margin-bottom: 8px;
    }}
    
    .info-box {{ 
        padding: 15px; border-radius: 12px; 
        background-color: {card_bg}; 
        color: {text_color};
        border-right: 5px solid #3e7e69; 
        margin-top: 5px; line-height: 1.8;
    }}

    /* چاککردنی ستایلی لیستەکان (Expander) */
    .streamlit-expanderHeader {{
        background-color: {card_bg} !important;
        color: {text_color} !important;
        border-radius: 10px !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. بەشی سەرەوە ---
st.markdown('<p style="text-align:center; color:#888; margin-bottom:0;">Developed by: Dr. Danyal</p>', unsafe_allow_html=True)
st.markdown(f'<h1 style="text-align:center; margin-top:0; color:#3e7e69;">🏥 ڕێبەری گشتگیری تاقیگە</h1>', unsafe_allow_html=True)

# --- 5. بەشی گەڕانی خێرا ---
search_query = st.text_input("🔎 ناوی پشکنین بنووسە بۆ گەڕان...")

# --- 6. بنکەدراوەی پشکنینەکان (هەموو پشکنینەکان وەک خۆیان) ---
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
                st.markdown(f'<div class="info-box"><b>🧪 {t_name} ({cat})</b><br>{t_cont}</div>', unsafe_allow_html=True)
                found = True
    if not found:
        st.warning("ئەم پشکنینە نەدۆزرایەوە.")
    st.write("---")

# --- 8. نیشاندانی لیستەکان بە شێوەی دوگمە (Expander) ---
for category, tests in full_lab_data.items():
    with st.expander(category):
        for test_name, content in tests.items():
            st.markdown(f"**🧪 {test_name}**")
            st.markdown(f'<div class="info-box">{content}</div>', unsafe_allow_html=True)
            st.write("")
