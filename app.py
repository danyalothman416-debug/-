import streamlit as st

# --- ڕێکخستنی سەرەتایی ---
st.set_page_config(page_title="ڕێبەری گشتگیری تاقیگە", layout="centered")

# --- دیزاینی CSS بۆ چاککردنی فۆنت و لابردنی تێکەڵبوونی پیتەکان ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn&display=swap');
    
    html, body, [class*="css"] { 
        direction: rtl; 
        text-align: right; 
        font-family: 'Vazirmatn', sans-serif; 
    }
    
    /* چاککردنی خانەی گەڕان بۆ ئەوەی پیتەکان تێکەڵ نەبن */
    .stTextInput input {
        direction: rtl;
        text-align: right;
        font-size: 18px !important;
        padding: 10px !important;
    }

    /* ستایلی دوگمە سەوزەکان */
    .stButton>button {
        width: 100%; 
        border-radius: 12px; 
        height: 3.8rem;
        background-color: #3e7e69; 
        color: white; 
        font-size: 18px;
        border: none; 
        margin-bottom: 10px;
    }
    
    .info-box { 
        padding: 15px; 
        border-radius: 12px; 
        background-color: #f0f7f4; 
        border-right: 5px solid #3e7e69; 
        margin-top: 10px;
        font-size: 17px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- بەشی سەرەوە ---
st.markdown('<p style="text-align:center; color:#888;">Developed by: Dr. Danyal</p>', unsafe_allow_html=True)
st.markdown('<h1 style="text-align:center;">🏥 ڕێبەری گشتگیری تاقیگە</h1>', unsafe_allow_html=True)

# --- بەشی گەڕان (لێرە دامناوە بۆ ئەوەی پیتەکان تێکەڵ نەبن) ---
search_query = st.text_input("🔎 ناوی پشکنین بنووسە بۆ گەڕانی خێرا...")

# --- داتاکان ---
full_lab_data = {
    "1. Hematology (خوێن زانی)": {
        "CBC": "• ڕێگای کردن: وەرگرتنی 2-5ml خوێن.\n\n• پێکهاتەکان: خڕۆکە سوورەکان، سپییەکان و پلاکلێت.",
        "ESR": "نیشاندەر بۆ هەوکردن و ڕۆماتیزم.",
        "PT & PTT": "بۆ پێوانەی کاتی مەیینی خوێن."
    },
    "2. Clinical Chemistry": {
        "Blood Sugar": "شەکری بەڕۆژوو و تێکڕای ٣ مانگی.",
        "LFT (جگەر)": "ALT, AST, ALP بۆ تەندروستی جگەر.",
        "KFT (گورچیلە)": "Creatinine و Urea بۆ گورچیلە."
    }
    # دەتوانیت بەشەکانی تر لێرە زیاد بکەیتەوە بە هەمان شێوە
}

# --- نیشاندانی ئەنجامی گەڕان ---
if search_query:
    found = False
    for cat, tests in full_lab_data.items():
        for t_name, t_cont in tests.items():
            if search_query.lower() in t_name.lower():
                st.success(f"دۆزرایەوە لە بەشی: {cat}")
                st.markdown(f'<div class="info-box"><b>{t_name}:</b><br>{t_cont}</div>', unsafe_allow_html=True)
                found = True
    if not found:
        st.warning("ئەم پشکنینە نەدۆزرایەوە.")

st.write("---")

# --- لیستە سەرەکییەکە (Expander) ---
for category, tests in full_lab_data.items():
    with st.expander(category):
        for test_name, content in tests.items():
            st.markdown(f"**🧪 {test_name}**")
            st.markdown(f'<div class="info-box">{content}</div>', unsafe_allow_html=True)
            st.write("")
import streamlit as st

# --- ڕێکخستنی لاپەڕە ---
st.set_page_config(page_title="ڕێبەری گشتگیری تاقیگە", layout="centered")

# --- دیزاینی CSS بۆ ڕێککردنەوەی پیتەکان و ستایلی ئەپەکە ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn&display=swap');
    html, body, [class*="css"] { 
        direction: rtl; text-align: right; font-family: 'Vazirmatn', sans-serif; 
    }
    .stTextInput input { direction: rtl; text-align: right; font-size: 18px !important; }
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3.5rem;
        background-color: #3e7e69; color: white; font-size: 18px; border: none; margin-bottom: 8px;
    }
    .info-box { 
        padding: 15px; border-radius: 12px; background-color: #f0f7f4; 
        border-right: 5px solid #3e7e69; margin-top: 5px; line-height: 1.8;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p style="text-align:center; color:#888; margin-bottom:0;">Developed by: Dr. Danyal</p>', unsafe_allow_html=True)
st.markdown('<h1 style="text-align:center; margin-top:0;">🏥 ڕێبەری گشتگیری تاقیگە</h1>', unsafe_allow_html=True)

# --- بەشی گەڕانی خێرا ---
search_query = st.text_input("🔎 ناوی پشکنین بنووسە بۆ گەڕان...")

# --- بنکەدراوەی گەورەی پشکنینەکان ---
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

# --- ئەنجامی گەڕان ---
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

# --- نیشاندانی لیستەکان بە شێوەی دوگمە (Expander) ---
for category, tests in full_lab_data.items():
    with st.expander(category):
        for test_name, content in tests.items():
            st.markdown(f"**🧪 {test_name}**")
            st.markdown(f'<div class="info-box">{content}</div>', unsafe_allow_html=True)
            st.write("")
