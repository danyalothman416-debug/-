import streamlit as st
import pandas as pd

# ڕێکخستنی لاپەڕە
st.set_page_config(page_title="ڕێبەری تاقیگە", layout="wide")

# ستایلی کوردی
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn&display=swap');
    html, body, [class*="css"] { direction: rtl; text-align: right; font-family: 'Vazirmatn', sans-serif; }
    .stTextInput input { font-size: 22px !important; }
    .result-card { border: 2px solid #e6e6e6; padding: 20px; border-radius: 15px; margin-bottom: 15px; background-color: #ffffff; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("🔬 بنکەدراوەی پشکنینەکان - د. دانیال")

# خوێندنەوەی داتاکان (ئەگەر فایلەکە نەبوو، لیستێکی کاتی دروست دەکات)
try:
    df = pd.read_csv('tests.csv')
except:
    # داتای نموونەیی ئەگەر فایلەکەت هێشتا ئامادە نەبێت
    data = {
        'Test Name': ['CBC', 'ESR', 'HbA1c', 'Creatinine'],
        'Information': ['پشکنینی خوێن', 'هەوکردنی گشتی', 'تێکڕای شەکرە', 'فرمانی گورچیلە']
    }
    df = pd.DataFrame(data)

# بەشی گەڕان
search = st.text_input("🔎 ناوی پشکنینەکە بنووسە (بۆ نموونە: CBC)")

if search:
    # گەڕان لەناو ناوەکاندا
    results = df[df['Test Name'].str.contains(search, case=False, na=False)]
    
    if not results.empty:
        for index, row in results.iterrows():
            st.markdown(f"""
                <div class="result-card">
                    <h2 style="color: #007bff;">🧪 {row['Test Name']}</h2>
                    <p style="font-size: 18px;">{row['Information']}</p>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.error("❌ ببورە، ئەم پشکنینە لە بنکەدراوەکەدا نییە.")
else:
    st.info("تکایە ناوی پشکنینەکە بنووسە بۆ نیشاندانی زانیارییەکان.")

st.sidebar.write(f"کۆی پشکنینە بەردەستەکان: {len(df)}")
