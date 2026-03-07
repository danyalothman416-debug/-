import streamlit as st

# Setup page for Mobile view
st.set_page_config(page_title="ڕێبەری تاقیگە - د. دانیال", page_icon="🔬", layout="centered")

# Custom CSS for Kurdish RTL and Style
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;700&display=swap');
    html, body, [class*="css"]  {
        direction: rtl;
        text-align: right;
        font-family: 'Vazirmatn', sans-serif;
    }
    div.stButton > button {
        width: 100%;
        border-radius: 12px;
        background-color: #007bff;
        color: white;
        font-weight: bold;
        height: 3.5em;
        margin-bottom: 10px;
        border: none;
    }
    .stExpander {
        border-radius: 12px;
        background-color: #f8f9fa;
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# Main Title
st.title("🏥 ڕێبەری گشتگیری پشکنینەکان")
st.markdown("### پەرەپێدراوە لەلایەن: **دکتۆر دانیال**")
st.write("---")

# Full Data Structure
lab_database = {
    "🩸 پشکنینەکانی خوێن (Hematology)": {
        "CBC": "**CBC (Complete Blood Count)**\n\n• **ڕێگای کردن:** وەرگرتنی 2-5ml خوێن.\n• **گرنگی:**\n- RBC: ژمارەی خڕۆکە سوورەکان (کەمییان نیشانەی کەمخوێنییە).\n- Hb: ئاستی هیمۆگلۆبین.\n- WBC: خڕۆکە سپییەکان (بەرزبوونەوەیان نیشانەی هەوکردنە).\n- Plt: پلاکلێتەکان (بەرپرس لە مەیینی خوێن).",
        "ESR": "**ESR (ڕێژەی ڕژتن)**\n\n• **گرنگی:** نیشاندەرێکی گشتییە بۆ هەوکردن لە جەستەدا. ئەگەر زۆر بەرز بێت ئاماژەیە بۆ ڕۆماتیزم یان هەندێک جۆری شێرپەنجە.",
        "PT_PTT": "**PT & PTT (خوێنمەک)**\n\n• **گرنگی:** پێوانەکردنی کاتی مەیینی خوێن. پێش نەشتەرگەری و بۆ ئەو کەسانەی وارفارین بەکاردێنن زۆر گرنگە."
    },
    "🧪 کیمیای کلینیکی (Chemistry)": {
        "Sugar": "**Blood Sugar (FBS, HbA1c)**\n\n• **FBS:** شەکری بەڕۆژوو (سەروو 126 mg/dL نیشانەی شەکرەیە).\n• **HbA1c:** تێکڕای شەکرەی ٣ مانگی ڕابردوو (باشترین پشکنین بۆ چاودێری)." ,
        "LFT": "**LFT (کارکردنی جگەر)**\n\n• **ALT & AST:** بەرزبوونەوەیان نیشانەی هەوکردن یان زیانی جگەرە.\n• **ALP:** ئاماژە بۆ گیرانی ڕێڕەوی زەرداو.\n• **Bilirubin:** بەرزبوونی دەبێتە هۆی زەردوویی چاو و پێست.",
        "KFT": "**KFT (کارکردنی گورچیلە)**\n\n• **Creatinine & Urea:** ئەگەر لە خوێندا بەرز بن، ئاماژەن بۆ لەکارکەوتنی گورچیلە.",
        "Lipid": "**Lipid Profile (چەوری خوێن)**\n\n• **Cholesterol & LDL:** چەورییە خراپەکان.\n• **HDL:** چەوری باش.\n• **گرنگی:** هەڵسەنگاندنی مەترسی جەڵتەی دڵ."
    },
    "🧫 بەکتریا ناسی (Microbiology)": {
        "Urine_Culture": "**Urine Culture (چاندنی میز)**\n\n• **چۆنیەتی:** کۆکردنەوەی میزی بەیانی بە شێوەی ستێریل.\n• **گرنگی:** دیاریکردنی جۆری باکتریا و هەوکردنی میزەڵدان.",
        "Antibiotic": "**Antibiogram (هەستیاری دەرمان)**\n\n• **مەبەست:** دیاریکردنی باشترین جۆری دژەباکتیریا (Antibiotic) بۆ کوشتنی باکتیریاکە."
    },
    "🧬 پشکنینە پێشکەوتووەکان": {
        "PSA": "**PSA (پڕۆستاتی پیاو)**\n\n• **گرنگی:** دیاریکردنی شێرپەنجەی پڕۆستات یان گەورەبوونی سادەی پڕۆستات.",
        "Karyotype": "**Karyotype (بۆماوەیی)**\n\n• **گرنگی:** بینینی کرۆمۆسۆمەکان بۆ ناسینەوەی نەخۆشی داون سیندرۆم.",
        "Hepatitis": "**Viral Hepatitis (ڤایرۆسی جگەر)**\n\n• **HBV & HCV:** پشکنینی چالاکی ڤایرۆسەکە و دۆزینەوەی لە خوێندا."
    }
}

# Building the UI
for category, tests in lab_database.items():
    with st.expander(category):
        for test_name, details in tests.items():
            if st.button(test_name):
                st.session_state['active_test'] = details

# Display Details
if 'active_test' in st.session_state:
    st.write("---")
    st.info(st.session_state['active_test'])
    if st.button("داخستنی زانیارییەکان"):
        del st.session_state['active_test']
        st.rerun()

st.sidebar.markdown("### دەربارەی ئەپ")
st.sidebar.info("ئەم ئەپە سەرچاوەیەکی فێربوونە بۆ پشکنینە تاقیگەییەکان.")
