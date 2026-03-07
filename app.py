import streamlit as st

# --- 1. ڕێکخستنی لاپەڕە ---
st.set_page_config(page_title="تاقیگەی زیرەک", layout="centered")

# --- 2. دیزاینی CSS بۆ دروستکردنی کارتەکان ڕێک وەک وێنەکە ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #1a1a1a !important;
        direction: rtl; text-align: right;
        font-family: 'Vazirmatn', sans-serif;
    }
    header {visibility: hidden;}

    /* ستایلی گشتی کارتەکان لە ناو گرید */
    .stButton > button {
        background-color: #262626 !important;
        color: white !important;
        border: 1px solid #333 !important;
        border-radius: 12px !important;
        padding: 20px 0px !important;
        height: 120px !important;
        width: 100% !important;
        font-weight: bold !important;
        font-size: 15px !important;
        display: block !important;
        transition: 0.3s !important;
    }

    .stButton > button:hover {
        border-color: #4ea88d !important;
        background-color: #2d2d2d !important;
    }

    /* ستایلی نوسینەکانی ناوەوە */
    .info-box {
        background-color: #262626; padding: 15px; border-radius: 12px;
        border-right: 5px solid #4ea88d; margin-bottom: 10px; color: white;
        font-size: 14px; line-height: 1.6;
    }
    
    .section-title {
        color: #888; font-size: 14px; margin-bottom: 15px; margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. بەڕێوەبردنی لاپەڕەکان ---
if 'active_page' not in st.session_state:
    st.session_state.active_page = "main"

# --- 4. لاپەڕەی سەرەکی (ڕێک وەک وێنەکە) ---
if st.session_state.active_page == "main":
    st.markdown('<h2 style="text-align:right; color:white;">دکتۆر دانیال - تاقیگە</h2>', unsafe_allow_html=True)
    
    # بەشی سەرەکی (Grid 3x3)
    st.markdown('<p class="section-title">سەرەکی</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔬\nتاقیگە"): 
            st.session_state.active_page = "lab_list"
            st.rerun()
        if st.button("🦠\nنەخۆشییەکان"): pass
        if st.button("💊\nدەرمانە نوێ"): pass

    with col2:
        if st.button("🔔\nبیرم بخەرەوە"): pass
        if st.button("🍎\nڤیتامینەکان"): pass
        if st.button("⚖️\nBMI"): 
            st.session_state.active_page = "bmi_calc"
            st.rerun()

    with col3:
        if st.button("🧪\nپشکنینەکان"): pass
        if st.button("🧠\nوەرگێڕی زیرەک"): 
            st.session_state.active_page = "ai_interpreter"
            st.rerun()
        if st.button("👨‍⚕️\nبابەتەکان"): pass

    # بەشی نوسینی خوارەوە (وەک ناو وێنەکە)
    st.markdown("""
    <div style="background-color: #262626; padding: 15px; border-radius: 10px; margin-top: 25px; border: 1px solid #333;">
        <p style="color: #bbb; font-size: 13px; line-height: 1.8; text-align: justify;">
        لە ئەپڵیکەیشنی دکتۆر دانیالدا، زانیاری زیاتر لە ١٠٠٠ جۆری پشکنین و دەرمان جێگیر کراوە. هەموو زانیارییەکان بە وردی و لەژێر چاودێری پزیشکی پسپۆر ئامادە کراون بۆ ئاسانکاری ئێوەی خۆشەویست.
        </p>
    </div>
    """, unsafe_allow_html=True)

# --- 5. لاپەڕەی پشکنینەکان (١٢ خاڵەکە) ---
elif st.session_state.active_page == "lab_list":
    if st.button("🔙 گەڕانەوە"):
        st.session_state.active_page = "main"
        st.rerun()
    
    st.header("🔬 لیستی پشکنینەکان")
    # لێرە هەموو ١٢ خاڵەکە بە Expanders دادەنێین بۆ ئەوەی ڕێک و پێك بێت
    with st.expander("1. Hematology (خوێن زانی)"):
        st.markdown('<div class="info-box"><b>CBC:</b> Hb 12-17 | ٣٠ خولەک<br><b>ESR:</b> 0-20 mm/hr</div>', unsafe_allow_html=True)
    with st.expander("2. Chemistry (کیمیای کلینیکی)"):
        st.markdown('<div class="info-box"><b>FBS:</b> 70-100 mg/dL<br><b>Creatinine:</b> 0.6-1.2 mg/dL</div>', unsafe_allow_html=True)
    # دەتوانیت باقی خاڵەکان لێرە زیاد بکەیت...

# --- 6. لاپەڕەی BMI ---
elif st.session_state.active_page == "bmi_calc":
    if st.button("🔙 گەڕانەوە"):
        st.session_state.active_page = "main"
        st.rerun()
    st.header("⚖️ حیسابکردنی BMI")
    weight = st.number_input("کێش (kg):", value=75.0)
    height = st.number_input("باڵا (cm):", value=175.0)
    if height > 0:
        bmi = weight / ((height/100)**2)
        st.success(f"BMI Score: {bmi:.1f}")

# --- 7. لاپەڕەی وەرگێڕی زیرەک ---
elif st.session_state.active_page == "ai_interpreter":
    if st.button("🔙 گەڕانەوە"):
        st.session_state.active_page = "main"
        st.rerun()
    st.header("🧠 وەرگێڕی زیرەک")
    st.info("ئەنجامی پشکنینەکانت لێرە بنووسە بۆ شیکردنەوە...")
