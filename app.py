import streamlit as st
from transformers import pipeline

# ڕێکخستنی ڕووکاری پەڕە
st.set_page_config(
    page_title="شیکاری هەست و سۆز",
    page_icon="🧠",
    layout="centered"
)

# ناونیشانی سەرەکی
st.title("🧠 شیکاری هەست و سۆز بە AI")
st.markdown("---")

# ناساندنی بەرنامە
st.markdown("""
### بەخێربێیت! 👋
ئەم بەرنامەیە دەتوانێت هەست و سۆزی دەقەکەت شیکار بکات.
تەنها دەقێک بنووسە و کلیک لەسەر دوگمەکە بکە!
""")

# بارکردنی مۆدێل (cache دەکرێت بۆ خێرایی زیاتر)
@st.cache_resource
def load_model():
    with st.spinner("چاوەڕێ بە... مۆدێلەکە باردەکرێت"):
        return pipeline("sentiment-analysis", 
                       model="distilbert-base-uncased-finetuned-sst-2-english")

# بارکردنی مۆدێل لە کاتی دەستپێکردندا
try:
    classifier = load_model()
    model_loaded = True
except Exception as e:
    st.error(f"هەڵەیەک ڕوویدا لە بارکردنی مۆدێل: {e}")
    model_loaded = False

st.markdown("---")

# وەرگرتنی دەق لە بەکارهێنەر
text_input = st.text_area(
    "✍️ دەقێک لێرە بنووسە:",
    height=150,
    placeholder="بۆ نموونە: I really enjoyed this movie, it was fantastic!",
    max_chars=500
)

# دوگمەی شیکاری
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    analyze_button = st.button("🔍 شیکاری بکە", type="primary", use_container_width=True)

# شیکاری دەق
if analyze_button and text_input and model_loaded:
    with st.spinner("شیکاری دەکرێت..."):
        try:
            # ئەنجامدانی شیکاری
            result = classifier(text_input)
            
            st.markdown("---")
            st.subheader("📊 ئەنجامەکان:")
            
            # نمایشکردنی ئەنجامەکان بە شێوەیەکی جوان
            col1, col2 = st.columns(2)
            
            with col1:
                label = result[0]['label']
                if label == 'POSITIVE':
                    st.success(f"✅ هەست: **ئەرێنی** (Positive)")
                else:
                    st.error(f"❌ هەست: **نەرێنی** (Negative)")
            
            with col2:
                confidence = result[0]['score']
                st.info(f"🎯 ڕێژەی دڵنیایی: **{confidence:.2%}**")
            
            # پیشاندانی پێوەری پێشکەوتن بۆ ڕێژەی دڵنیایی
            st.progress(confidence)
            
        except Exception as e:
            st.error(f"هەڵەیەک ڕوویدا لە کاتی شیکاری: {e}")

elif analyze_button and not text_input:
    st.warning("⚠️ تکایە دەقێک بنووسە پێش ئەوەی کلیک بکەیت!")

# زانیاری زیاتر
st.markdown("---")
with st.expander("ℹ️ دەربارەی ئەم بەرنامەیە"):
    st.write("""
    ئەم بەرنامەیە بەرنامەیەکی سادەی شیکاری هەست و سۆزە کە:
    - **Streamlit**: بۆ دروستکردنی ڕووکاری وێب
    - **Hugging Face Transformers**: بۆ مۆدێلی AI
    - **DistilBERT**: وەک مۆدێلی زیرەکی دەستکرد
    
    مۆدێلەکە دەتوانێت هەستی ئەرێنی یان نەرێنی دەقەکەت دیاری بکات.
    """)

# پەراوێز
st.markdown("---")
st.caption("دروستکراوە بە Streamlit و Hugging Face 🤗")
