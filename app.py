import streamlit as st
import pandas as pd

# --- 1. ڕێکخستنی لاپەڕە ---
st.set_page_config(page_title="تاقیگەی زیرەک", layout="centered")

# --- 2. دیزاینی CSS بۆ هاوشێوەکردنی وێنە ئەسڵییەکە ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #1a1a1a !important;
        direction: rtl; text-align: right;
        font-family: 'Vazirmatn', sans-serif;
    }
    header {visibility: hidden;}

    /* دروستکردنی گرید وەک وێنەکە */
    .main-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 10px;
        margin-top: 20px;
    }

    /* ستایلی کارتەکان */
    .card {
        background-color: #262626;
        border-radius: 12px;
        padding: 20px 5px;
        text-align: center;
        border: 1px solid #333;
        cursor: pointer;
        display: flex;
        flex-direction: column;
        align-items: center;
        text-decoration: none;
        color: white !important;
    }

    .card:hover { border-color: #4ea88d; background-color: #2d2d2d; }
    .icon { font-size: 32px; margin-bottom: 10px; }
    .title { font-size: 13px; font-weight: bold; }
    
    .badge {
        background-color: #ff4b4b; color: white; font-size: 9px;
        padding: 2px 5px; border-radius: 4px; margin-bottom: 5px;
    }

    .stExpander { background-color: #262626 !important; border: none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. لۆژیکی سێشن بۆ گۆڕینی لاپەڕەکان ---
if 'page' not in st.session_state:
    st.session_state.page = "main"

# --- 4. شاشەی سەرەکی (ڕێک وەک وێنەکە) ---
if st.session_state.page == "main":
    st.markdown('<h2 style="text-align:center; color:white;">دکتۆر دانیال - تاقیگە</h2>', unsafe_allow_html=True)
    
    # دروستکردنی کارتەکان بە دوگمەی ستریملیت بەڵام لەناو گرید
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔬\nتاقیگە", use_container_width=True): st.session_state.page = "lab"
        if st.button("🦠\nنەخۆشییەکان", use_container_width=True): pass
        if st.button("💊\nدەرمانە نوێیەکان", use_container_width=True): pass

    with col2:
        if st.button("🔔\nبیرم بخەرەوە", use_container_width=True): pass
        if st.button("🍎\nڤیتامینەکان", use_container_width=True): pass
        if st.button("⚕️\nفڕۆشگا", use_container_width=True): pass

    with col3:
        if st.button("💊\nدەرمانەکان", use_container_width=True): pass
        if st.button("🧪\nپشکنینەکان", use_container_width=True): pass
        if st.button("👨‍⚕️\nبابەتەکان", use_container_width=True): pass

    st.markdown("""
    <div style="background-color: #262626; padding: 15px; border-radius: 10px; margin-top: 20px; font-size: 13px; color: #bbb;">
    لە ئەپڵیکەیشنی تاقیگەی زیرەکدا، هەموو زانیارییەکان بە وردی جێگیر کراون لەژێر سەرپەرشتی دکتۆر دانیال.
    </div>
    """, unsafe_allow_html=True)

# --- 5. لاپەڕەی تاقیگە (١٢ خاڵەکە) ---
elif st.session_state.page == "lab":
    if st.button("🔙 گەڕانەوە بۆ سەرەکی"):
        st.session_state.page = "main"
        st.rerun()

    st.header("🔬 هەموو پشکنینەکانی تاقیگە")
    
    tabs = st.tabs(["پشکنینەکان", "BMI", "وەرگێڕ"])
    
    with tabs[0]:
        # لێرە هەموو ١٢ خاڵەکە دادەنێیت
        exp1 = st.expander("1. Hematology")
        exp1.write("CBC: Hb 12-17 | کات: ٣٠ خولەک")
        
        exp2 = st.expander("2. Clinical Chemistry")
        exp2.write("FBS: 70-100 | کات: ٣٠ خولەک")
        # ... باقی ١٢ خاڵەکە لێرە بەردەوام دەبێت

    with tabs[1]:
        st.subheader("حیسابکردنی BMI")
        w = st.number_input("کێش", value=70.0)
        h = st.number_input("باڵا", value=170.0)
        if h > 0:
            st.write(f"BMI: {w/((h/100)**2):.1f}")

    with tabs[2]:
        st.subheader("وەرگێڕی زیرەک")
        st.write("ئەنجامەکان لێرە لێک بدەرەوە.")
