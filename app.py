import streamlit as st

# --- ڕێکخستنی لاپەڕە ---
st.set_page_config(page_title="ڕێبەری گشتگیری تاقیگە", layout="centered")

# --- دیزاینی CSS بۆ Dark Mode و فۆنت ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn&display=swap');
    
    /* ڕێکخستنی گشتی و فۆنت */
    html, body, [class*="css"] { 
        direction: rtl; text-align: right; font-family: 'Vazirmatn', sans-serif; 
    }

    /* پشتێنەی تاریک بۆ هەموو ئەپەکە */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }

    /* چاککردنی خانەی گەڕان */
    .stTextInput input { 
        direction: rtl; 
        text-align: right; 
        background-color: #262730 !important;
        color: white !important;
        border: 1px solid #3e7e69 !important;
        border-radius: 10px;
    }

    /* دوگمە سەوزەکان بە ستایلی تاریک */
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3.5rem;
        background-color: #3e7e69; color: white; font-size: 18px; 
        border: none; margin-bottom: 8px; transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #4ea88d;
        box-shadow: 0px 4px 15px rgba(62, 126, 105, 0.4);
    }

    /* سندوقی زانیارییەکان (Dark Info Box) */
    .info-box { 
        padding: 15px; border-radius: 12px; 
        background-color: #1d2129; 
        color: #e0e0e0;
        border-right: 5px solid #3e7e69; 
        margin-top: 5px; line-height: 1.8;
    }

    /* ڕێکخستنی Expander (لیستەکان) */
    .streamlit-expanderHeader {
        background-color: #1d2129 !important;
        color: white !important;
        border-radius: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- بەشی سەرەوە ---
st.markdown('<p style="text-align:center; color:#aaa; margin-bottom:0;">Developed by: Dr. Danyal</p>', unsafe_allow_html=True)
st.markdown('<h1 style="text-align:center; color:#3e7e69; margin-top:0;">🏥 ڕێبەری گشتگیری تاقیگە (Dark Edition)</h1>', unsafe_allow_html=True)

# --- بەشی گەڕان ---
search_query = st.text_input("🔎 گەڕان بۆ پشکنین...")

# --- داتاکان (هەمان لیستە گەورەکە) ---
full_lab_data = {
    "1. Hematology (خوێن زانی)": {
        "CBC": "پشکنینی گشتی خوێن (Hb, WBC, RBC, Plt).",
        "ESR": "نیشاندەری هەوکردن و ڕۆماتیزم.",
        "PT & PTT": "بۆ پێوانەی کاتی مەیینی خوێن."
    },
    "2. Clinical Chemistry": {
        "Blood Sugar": "FBS و HbA1c بۆ چاودێری شەکرە.",
        "LFT (جگەر)": "ALT, AST, ALP بۆ جگەر.",
        "KFT (گورچیلە)": "Creatinine و Urea بۆ گورچیلە."
    },
    "3. Microbiology": {
        "Urine Culture": "چاندنی میز بۆ دۆزینەوەی باکتریای زیانبەخش.",
        "GSE": "پشکنینی پیسایی بۆ پاراسایت و کرم."
    }
    # دەتوانیت هەموو لیستەکانی تر لێرە دابنێیتەوە
}

# --- ئەنجامی گەڕان ---
if search_query:
    found = False
    for cat, tests in full_lab_data.items():
        for t_name, t_cont in tests.items():
            if search_query.lower() in t_name.lower():
                st.markdown(f'<div class="info-box"><b style="color:#4ea88d;">🧪 {t_name}</b><br>{t_cont}</div>', unsafe_allow_html=True)
                found = True
    if not found:
        st.warning("نەدۆزرایەوە.")
    st.write("---")

# --- نیشاندانی لیستەکان ---
for category, tests in full_lab_data.items():
    with st.expander(category):
        for test_name, content in tests.items():
            st.markdown(f"<b style='color:#4ea88d;'>🧪 {test_name}</b>", unsafe_allow_html=True)
            st.markdown(f'<div class="info-box">{content}</div>', unsafe_allow_html=True)
            st.write("")
