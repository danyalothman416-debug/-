import streamlit as st
import time

# --- ڕێکخستنی سەرەتایی پەڕەکە ---
st.set_page_config(page_title="Danyal Medical Lab", page_icon="🔬", layout="centered")

# --- دیزاینی CSS بۆ ڕاست-بۆ-چەپ (RTL) و ڕەنگەکان ---
st.markdown("""
<style>
    * {
        direction: rtl;
    }
    .st-emotion-cache-1y4p8pa {
        padding-top: 2rem;
    }
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

# --- کۆنتڕۆڵکردنی پەڕەکان ---
if 'page' not in st.session_state:
    st.session_state.page = 'home'

def change_page(page_name):
    st.session_state.page = page_name

# ==========================================
# پەڕەی سەرەکی (Home)
# ==========================================
if st.session_state.page == 'home':
    st.markdown("<div class='main-title'>🔬 Danyal Medical Lab</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>سیستەمی زیرەک بۆ شیکاری پشکنینە تاقیگەییەکان</div>", unsafe_allow_html=True)
    
    st.write("---")
    
    st.markdown("""
    <div class='info-box'>
        <h3>شیکاری ئەنجامی پشکنین 📊</h3>
        <p>ئەنجامی پشکنینەکانت لێرە داخڵ بکە بۆ خوێندنەوە و شیکاری تەواوەتی.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("داخڵکردنی پشکنین ➔"):
        change_page('tests')
        st.rerun()

# ==========================================
# پەڕەی داخڵکردنی پشکنینەکان (Tests Input)
# ==========================================
elif st.session_state.page == 'tests':
    st.button("🔙 گەڕانەوە", on_click=change_page, args=('home',))
    
    st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>ئەنجامی پشکنینەکان</h2>", unsafe_allow_html=True)
    st.write("تکایە ژمارەی ئەنجامی پشکنینەکان لەم بۆکسانەی خوارەوە داخڵ بکە:")
    
    # فۆڕمی پشکنینە کیمیاییەکان
    col1, col2 = st.columns(2)
    with col1:
        fbs = st.number_input("شەکرەی خوێن (FBS) - mg/dL", min_value=0, value=90)
        chol = st.number_input("کۆلیسترۆڵ (Cholesterol) - mg/dL", min_value=0, value=180)
    with col2:
        hb = st.number_input("هیمۆگلۆبین (Hb) - g/dL", min_value=0.0, value=14.0, format="%.1f")
        alt = st.number_input("ئەنزیمی جگەر (ALT) - U/L", min_value=0, value=25)
        
    st.write("---")
    if st.button("شیکاری بکە"):
        # هەڵگرتنی داتاکان بۆ پەڕەی ئەنجام
        st.session_state.fbs = fbs
        change_page('analyzing')
        st.rerun()

# ==========================================
# پەڕەی پرۆسەی شیکاری (Analyzing)
# ==========================================
elif st.session_state.page == 'analyzing':
    st.markdown("<h2 style='text-align: center;'>خەریکی شیکارین... ⚙️</h2>", unsafe_allow_html=True)
    
    my_bar = st.progress(0)
    for percent_complete in range(100):
        time.sleep(0.01)
        my_bar.progress(percent_complete + 1)
    
    time.sleep(0.3)
    change_page('result')
    st.rerun()

# ==========================================
# پەڕەی ئەنجام (Results)
# ==========================================
elif st.session_state.page == 'result':
    st.button("🔙 گەڕانەوە بۆ سەرەتا", on_click=change_page, args=('home',))
    
    st.success("✅ شیکاری تەواو بوو")
    st.markdown("<h3 style='text-align: center;'>ڕاپۆرتی تاقیگە:</h3>", unsafe_allow_html=True)
    
    # لۆجیکی پزیشکی بۆ دیاریکردنی دۆخی شەکرە
    fbs_val = st.session_state.fbs
    if fbs_val > 125:
        status = "بەرزە (پێویستی بە سەردانی پزیشکە)"
        color = "#DC2626" # سوور
        bg_color = "#FEE2E2"
    elif fbs_val > 100:
        status = "قۆناغی پێش شەکرە (Pre-diabetes)"
        color = "#D97706" # پرتەقاڵی
        bg_color = "#FEF3C7"
    else:
        status = "ئاساییە (Normal)"
        color = "#166534" # سەوز
        bg_color = "#DCFCE7"

    # پیشاندانی ئەنجامەکە بە شێوەیەکی دیزاینکراو
    st.markdown(f"""
    <div style='background-color: {bg_color}; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px;'>
        <h3 style='color: {color};'>ئەنجامی شەکرەی خوێن (FBS): {fbs_val}</h3>
        <p style='font-size: 20px; color: {color};'>دۆخەکە: <b>{status}</b></p>
    </div>
    """, unsafe_allow_html=True)
