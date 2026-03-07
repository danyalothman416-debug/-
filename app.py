import streamlit as st

# --- ڕێکخستنی سەرەتایی ---
st.set_page_config(page_title="ڕێبەری گشتگیری تاقیگە", layout="centered")

# --- دیزاینی CSS بۆ ڕەنگەکان و فۆنت ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn&display=swap');
    html, body, [class*="css"] { 
        direction: rtl; text-align: right; font-family: 'Vazirmatn', sans-serif; 
    }
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3.5rem;
        background-color: #3e7e69; color: white; font-size: 18px;
        border: none; margin-bottom: 8px; transition: 0.3s;
    }
    .stButton>button:hover { background-color: #2d5d4d; color: #fff; }
    .info-box { 
        padding: 20px; border-radius: 15px; background-color: #f0f7f4; 
        border-right: 5px solid #3e7e69; line-height: 1.8;
    }
    .dev-label { text-align: center; color: #888; font-size: 14px; }
    </style>
    """, unsafe_allow_html=True)

# --- سەرپەڕەی ئەپەکە ---
st.markdown('<p class="dev-label">Developed by: Dr. Danyal</p>', unsafe_allow_html=True)
st.markdown('<h1 style="text-align: center;">🏥 ڕێبەری گشتگیری تاقیگە</h1>', unsafe_allow_html=True)

# --- بنکەدراوەی پشکنینەکان ---
full_lab_data = {
    "1. Hematology (خوێن زانی)": {
        "CBC": "• ڕێگای کردن: وەرگرتنی 2-5ml خوێن.\n\n• پێکهاتەکان:\n- RBC: خڕۆکە سوورەکان.\n- Hb: هیمۆگلۆبین.\n- WBC: خڕۆکە سپییەکان.\n- Plt: پلاکلێتەکان.",
        "ESR": "نیشاندەرێکی هەستیار بۆ هەوکردن، ڕۆماتیزم، یان شێرپەنجە.",
        "PT & PTT": "بۆ پێوانەی کاتی مەیینی خوێن، گرنگ بۆ پێش نەشتەرگەری."
    },
    "2. Clinical Chemistry": {
        "Blood Sugar": "FBS (بەڕۆژوو) و HbA1c (تێکڕای ٣ مانگ) بۆ چاودێری شەکرە.",
        "LFT (جگەر)": "ALT, AST, ALP و Bilirubin بۆ زانیاری لەسەر تەندروستی جگەر.",
        "KFT (گورچیلە)": "Creatinine و Urea بۆ زانینی توانای کارکردنی گورچیلە.",
        "Lipid Profile": "Cholesterol, TG, HDL, LDL بۆ چەوری خوێن."
    },
    "3. Microbiology": {
        "Urine Culture": "چاندنی میز بۆ دۆزینەوەی باکتریا لە سەروو 100,000.",
        "Antibiogram": "دیاریکردنی کاریگەرترین دژەباکتیریا بۆ نەخۆشەکە."
    },
    "4. Urinalysis": {
        "General Urine (U/A)": "پشکنینی بینراو، کیمیایی، و وردبینی بۆ بینینی کریستاڵ و پڕۆتین."
    },
    "5. Serology (ئیمۆنۆلۆجی)": {
        "CRP Test": "لە کاتی هەوکردنی تیژدا بەرز دەبێتەوە.",
        "Widal Test": "دۆزینەوەی دژەتەنەکانی تایبەت بە تایفۆید."
    },
    "6. Pathology (Tumor Markers)": {
        "PSA": "بۆ پڕۆستاتی پیاوان.",
        "CA-125": "بۆ شێرپەنجەی هێلکەدانی ئافرەتان."
    },
    "7. Molecular & Viral": {
        "Karyotype": "بۆ تێبینی کرۆمۆسۆمەکان (وەک داون سایندرۆم).",
        "Hepatitis": "پشکنینی ڤایرۆسی جگەر (HBV, HCV).",
        "Autoimmune": "پشکنینەکانی وەک ANA و Anti-CCP."
    }
}

# --- دروستکردنی دوگمەکان ---
for category, tests in full_lab_data.items():
    with st.expander(category):
        for test_name, content in tests.items():
            st.markdown(f"### 🧪 {test_name}")
            st.markdown(f'<div class="info-box">{content}</div>', unsafe_allow_html=True)
            st.write("") # بۆشایی

# --- بەشی گەڕانی گشتی ---
st.sidebar.title("🔍 گەڕانی خێرا")
search_query = st.sidebar.text_input("ناوی پشکنین بنووسە...")
if search_query:
    st.sidebar.write("ئەنجامەکان:")
    for cat, tests in full_lab_data.items():
        for t_name in tests:
            if search_query.lower() in t_name.lower():
                st.sidebar.info(f"{t_name} لە بەشی {cat}")
