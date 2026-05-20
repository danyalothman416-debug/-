import streamlit as st
import time

# --- ڕێکخستنی سەرەتایی پەڕەکە ---
st.set_page_config(page_title="Danyal Medical Lab", page_icon="🩺", layout="centered")

# --- دیزاینی CSS بۆ ڕاست-بۆ-چەپ (RTL) و ڕەنگەکان ---
st.markdown("""
<style>
    /* گۆڕینی ئاڕاستەی پەیجەکە بۆ کوردی */
    * {
        direction: rtl;
    }
    .st-emotion-cache-1y4p8pa {
        padding-top: 2rem;
    }
    /* دیزاینی کارتەکان و دوگمەکان */
    div.stButton > button:first-child {
        background-color: #3B82F6;
        color: white;
        border-radius: 10px;
        width: 100%;
        padding: 10px;
        font-size: 18px;
        font-weight: bold;
        border: none;
    }
    div.stButton > button:first-child:hover {
        background-color: #2563EB;
        color: white;
    }
    .main-title {
        text-align: center;
        color: #1E3A8A;
        font-size: 40px;
        font-weight: bold;
        margin-bottom: -10px;
    }
    .sub-title {
        text-align: center;
        color: #64748B;
        font-size: 18px;
        margin-bottom: 30px;
    }
    .info-box {
        background: linear-gradient(135deg, #60A5FA, #3B82F6);
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# --- کۆنتڕۆڵکردنی پەڕەکان (Navigation) ---
if 'page' not in st.session_state:
    st.session_state.page = 'home'

def change_page(page_name):
    st.session_state.page = page_name

# ==========================================
# پەڕەی سەرەکی (Home)
# ==========================================
if st.session_state.page == 'home':
    st.markdown("<div class='main-title'>💙 Danyal Medical Lab</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>یارمەتی شیکاری نەخۆشییەکان و پشکنینەکان</div>", unsafe_allow_html=True)
    
    st.write("---")
    
    st.markdown("""
    <div class='info-box'>
        <h3>شیکاری نیشانەکان 🔍</h3>
        <p>نیشانەکانت بنووسە و بە شێوەی زیرەک شیکارییان بۆ دەکرێت.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("دەست پێبکە ➔"):
        change_page('symptoms')
        st.rerun()

    st.write("### خزمەتگوزارییەکان")
    col1, col2 = st.columns(2)
    with col1:
        st.info("🦠 نەخۆشییە باوەکان")
        st.info("📊 پشکنینی تاقیگە")
    with col2:
        st.success("❤️ شیکاری نیشانەکان")
        st.warning("📋 پەڕاوی تەندروستی")

# ==========================================
# پەڕەی هەڵبژاردنی نیشانەکان (Symptoms)
# ==========================================
elif st.session_state.page == 'symptoms':
    st.button("🔙 گەڕانەوە", on_click=change_page, args=('home',))
    
    st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>کام نیشانەت هەیە؟</h2>", unsafe_allow_html=True)
    st.write("هەموو ئەو نیشانانە دیاریبکە کە تێتدایە بۆ ئەوەی باشترین شیکاریت پێبدەین.")
    
    # لیستی نیشانەکان
    col1, col2 = st.columns(2)
    with col1:
        s1 = st.checkbox("🤕 سەر ئێشە")
        s2 = st.checkbox("🤧 کۆکە")
        s3 = st.checkbox("🤒 تا (گەرما)")
    with col2:
        s4 = st.checkbox(" خرووی پێست")
        s5 = st.checkbox("🥱 بێهێزی")
        s6 = st.checkbox("🦴 ئازاری ماسولکە")
        
    other_symptom = st.text_input("نیشانەی تر...", placeholder="نیشانەکەی لێرە بنووسە...")
    
    st.write("---")
    if st.button("بەردەوام بە"):
        if s1 or s2 or s3 or s4 or s5 or s6 or other_symptom:
            change_page('analyzing')
            st.rerun()
        else:
            st.warning("تکایە لانی کەم یەک نیشانە هەڵبژێرە!")

# ==========================================
# پەڕەی پرۆسەی شیکاری و ئەنجام (Results)
# ==========================================
elif st.session_state.page == 'analyzing':
    st.markdown("<h2 style='text-align: center;'>خەریکی شیکارین... ⚙️</h2>", unsafe_allow_html=True)
    
    # دروستکردنی جوڵەیەک بۆ کاتی چاوەڕوانی (Progress Bar)
    progress_text = "تکایە چاوەڕێبە، زانیارییەکانت شیکار دەکرێن..."
    my_bar = st.progress(0, text=progress_text)
    for percent_complete in range(100):
        time.sleep(0.02)
        my_bar.progress(percent_complete + 1, text=progress_text)
    
    time.sleep(0.5)
    change_page('result')
    st.rerun()

elif st.session_state.page == 'result':
    st.button("🔙 گەڕانەوە بۆ سەرەتا", on_click=change_page, args=('home',))
    
    st.success("✅ شیکاری تەواو بوو")
    st.markdown("<h3 style='text-align: center;'>ئەنجامی پێشبینیکراو:</h3>", unsafe_allow_html=True)
    
    # ئەنجامێکی نموونەیی (پێویستە لێرەدا لۆجیکی پزیشکی بنووسرێت لە داهاتوودا)
    st.markdown("""
    <div style='background-color: #DCFCE7; padding: 20px; border-radius: 10px; text-align: center; border: 2px solid #22C55E;'>
        <h2 style='color: #166534;'>سەرماخۆری و ئەنفلۆنزا (Cold & Flu)</h2>
        <p style='color: #15803D;'>ڕێژەی ئەگەر: <b>%85</b></p>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("### 💊 چۆنیەتی چارەسەر و ئامۆژگاری:")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("🛏️ پشوو بدە")
    with col2:
        st.info("💧 شلەمەنی زۆر بخۆرەوە")
    with col3:
        st.info("💊 دەرمانی دژە تا (وەک پاراسیتامۆڵ)")
        
    st.warning("⚠️ تێبینی: ئەمە تەنها شیکارییەکی سەرەتاییە بۆ یارمەتیدانت. بۆ ئەنجامی دروست و پشکنینی تاقیگەیی سەردانی سەنتەرەکەمان بکە یان پزیشک.")
