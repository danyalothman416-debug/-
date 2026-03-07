import streamlit as st

# ڕێکخستنی سەرەکی بۆ مۆبایل
st.set_page_config(page_title="ڕێبەری تاقیگە - د. دانیال", layout="centered")

# CSS بۆ ڕێکخستنی زمان و دوگمەکان کە لە مۆبایلدا تێک نەچن
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn&display=swap');
    html, body, [class*="css"] {
        direction: rtl;
        text-align: right;
        font-family: 'Vazirmatn', sans-serif;
    }
    /* چاککردنی دوگمەکان بۆ ئەوەی کلیک بکرێن */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        background-color: #007bff;
        color: white;
        height: 3em;
        margin-top: 5px;
        border: none;
    }
    /* ڕێگری لە تێکەڵبوونی نووسینەکان */
    .stExpander {
        border: 1px solid #ddd;
        border-radius: 8px;
        margin-bottom: 10px;
        background-color: white;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏥 ڕێبەری پشکنینەکان")
st.subheader("پەرەپێدراوە لەلایەن: دکتۆر دانیال")

# داتاکان بە شێوازێکی سادەتر بۆ ئەوەی "کلیک" ئاسان بێت
data = {
    "🩸 پشکنینەکانی خوێن (Hematology)": {
        "CBC": "🔬 CBC: پشکنینی گشتی خوێن بۆ ئەنیمیا و هەوکردن.",
        "ESR": "🔬 ESR: نیشاندەری گشتی بۆ هەوکردن لە جەستەدا."
    },
    "🧪 کیمیای کلینیکی (Chemistry)": {
        "Sugar": "🍬 Blood Sugar: بۆ دۆزینەوەی شەکرە.",
        "LFT": "🧪 LFT: پشکنینی فرمانەکانی جگەر.",
        "KFT": "🧪 KFT: پشکنینی فرمانەکانی گورچیلە.",
        "Lipid": "🍔 Lipid Profile: پشکنینی چەوری خوێن."
    }
}

# دروستکردنی لیستەکە
for cat, tests in data.items():
    with st.expander(cat):
        for t_name, t_info in tests.items():
            # بەکارهێنانی columns بۆ ئەوەی دوگمەکە و نووسینەکە جیا ببنەوە
            if st.button(f"بینینی زانیاری: {t_name}"):
                st.info(t_info)

st.divider()
st.caption("ئەم ئەپە بۆ مەبەستی فێربوونە.")
