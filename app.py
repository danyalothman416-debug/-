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

    /* ڕێکخستنی گرید (Grid) ڕێک وەک وێنەکە */
    .main-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
        margin: 20px 0;
    }

    /* ستایلی کارتە چوارگۆشەییەکان */
    .menu-card {
        background-color: #262626;
        border-radius: 15px;
        padding: 20px 10px;
        text-align: center;
        border: 1px solid #333;
        transition: 0.3s;
        cursor: pointer;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 120px;
    }
    
    .menu-card:hover {
        border-color: #4ea88d;
        background-color: #2d2d2d;
    }

    .icon-img {
        width: 45px;
        height: 45px;
        margin-bottom: 10px;
    }

    .card-text {
        color: #ffffff;
        font-size: 13px;
        font-weight: bold;
    }

    .badge {
        background-color: #ff4b4b;
        color: white;
        font-size: 10px;
        padding: 2px 6px;
        border-radius: 5px;
        margin-bottom: 5px;
    }
    
    /* ستایلی بەشەکانی ناوەوە */
    .info-box {
        background-color: #262626; padding: 15px; border-radius: 12px;
        border-right: 5px solid #4ea88d; margin-bottom: 10px; color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. لۆژیکی سێشن بۆ گۆڕینی لاپەڕەکان ---
if 'page' not in st.session_state:
    st.session_state.page = "main"

# --- 4. شاشەی سەرەکی (ڕێک وەک وێنە ئەسڵییەکە) ---
if st.session_state.page == "main":
    st.markdown('<h2 style="text-align:center; color:white;">دکتۆر دانیال - تاقیگەی زیرەک</h2>', unsafe_allow_html=True)
    
    # دروستکردنی کارتەکان بە HTML و دوگمەی شاراوە بۆ کلیک کردن
    cols = st.columns(3)
    
    # ڕیزبەندی کارتەکان وەک وێنەکە
    with cols[0]:
        if st.button("💊\nدەرمانەکان", key="btn1"): pass
        if st.button("🧪\nپشکنینەکان", key="btn2"): pass
        if st.button("👨‍⚕️\nبابەتەکان", key="btn3"): pass

    with cols[1]:
        if st.button("🔔\nبیرم بخەرەوە", key="btn4"): pass
        if st.button("🍎\nڤیتامینەکان", key="btn5"): pass
        if st.button("⚕️\nفڕۆشگا", key="btn6"): pass

    with cols[2]:
        # ئەمەیان کارتی سەرەکی تاقیگەیە
        if st.button("🔬\nتاقیگە", key="lab_main"):
            st.session_state.page = "lab_details"
            st.rerun()
        if st.button("🦠\nنەخۆشییەکان", key="btn8"): pass
        if st.button("💊\nدەرمانە نوێ", key="btn9"): pass

    st.markdown("""
    <div style="background-color: #262626; padding: 20px; border-radius: 10px; margin-top: 20px; border: 1px solid #333;">
        <p style="font-size: 14px; line-height: 1.8; color: #ccc; text-align: justify;">
        ئەم ئەپڵیکەیشنە تایبەتە بە تاقیگەی دکتۆر دانیال. هەموو زانیارییەکانی تێدایە کە پێویستت دەبێت بۆ زانینی جۆری پشکنین، مەودای ئاسایی (Normal Range) و کاتی ئامادەبوون.
        </p>
    </div>
    """, unsafe_allow_html=True)

# --- 5. بەشی تاقیگە (کاتێک کلیک دەکرێت هەموو زانیارییەکان دەردەکەون) ---
elif st.session_state.page == "lab_details":
    if st.button("🔙 گەڕانەوە بۆ لاپەڕەی سەرەکی"):
        st.session_state.page = "main"
        st.rerun()
    
    st.markdown("<h2 style='color:#4ea88d;'>🔬 هەموو پشکنینەکانی تاقیگە</h2>", unsafe_allow_html=True)
    
    # لێرە هەموو ١٢ خاڵەکە جێگیر کراوە
    tab1, tab2, tab3 = st.tabs(["لیستی پشکنینەکان", "BMI", "وەرگێڕی زیرەک"])
    
    with tab1:
        search = st.text_input("🔎 گەڕان لە پشکنینەکان...")
        
        sections = {
            "1. Hematology (خوێن زانی)": {
                "CBC": "ئاسایی: Hb 12-17 | کات: ٣٠ خولەک",
                "ESR": "ئاسایی: 0-20 | کات: ١ کاتژمێر",
                "PT/PTT": "بۆ کاتی مەیینی خوێن."
            },
            "2. Clinical Chemistry": {
                "FBS (شەکر)": "ئاسایی: 70-100 | کات: ٣٠ خولەک",
                "Creatinine": "گورچیلە: 0.6-1.2",
                "ALT/AST": "جگەر: <40"
            },
            "8. Hormones": {
                "TSH": "غودە: 0.4-4.5",
                "Vitamin D3": "ئاسایی: 30-100"
            }
        }
        
        for cat, tests in sections.items():
            with st.expander(cat):
                for t, v in tests.items():
                    st.markdown(f"<div class='info-box'><b>{t}:</b><br>{v}</div>", unsafe_allow_html=True)

    with tab2:
        st.subheader("⚖️ BMI Calculator")
        w = st.number_input("کێش (kg):", value=70.0)
        h = st.number_input("باڵا (cm):", value=170.0)
        if h > 0:
            bmi = w / ((h/100)**2)
            st.metric("BMI دەرەنجام", f"{bmi:.1f}")

    with tab3:
        st.subheader("🧠 وەرگێڕی زیرەکی ئەنجامەکان")
        st.write("ئەنجامەکانت لێرە بنووسە بۆ شیکردنەوەی خێرا.")
