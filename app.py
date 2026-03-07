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
