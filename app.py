import streamlit as st
import time

# --- ١. ڕێکخستنی لاپەڕە و فۆنت و ستایل (UI/UX) ---
st.set_page_config(page_title="Danyal Health", page_icon="💙", layout="centered")

# داتای سێشەن بۆ گۆڕینی شاشەکان
if 'current_page' not in st.session_state:
    st.session_state.current_page = '🏠 Home'

# بەکارهێنانی CSS بۆ جێبەجێکردنی فۆنتی ڕەسەنی کوردی و ستایلی Modern Minimal
st.markdown("""
<style>
    /* هێنانی فۆنتی فەرمی و جوانی کوردی لە گووگڵ */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@300;400;700&family=Poppins:wght@300;400;600&display=swap');
    
    * {
        font-family: 'Noto Sans Arabic', 'Poppins', sans-serif !important;
        direction: rtl;
    }
    
    /* پاککردنەوەی پاشبنەمای ستریمکێت و دانانی ڕەنگی سپی و مۆری زۆر کاڵ */
    .stApp {
        background-color: #F8FAFC;
    }
    
    /* ستایلی کارتەکان (Rounded Cards & Soft Shadow) */
    .custom-card {
        background: white;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(147, 51, 234, 0.06); /* سێبەری مۆری زۆر کاڵ */
        border: 1px solid #E2E8F0;
        margin-bottom: 15px;
    }
    
    /* دوگمەی سەرەکی (شین و مۆدێرن) */
    div.stButton > button {
        background: linear-gradient(135deg, #3B82F6, #8B5CF6) !important; /* تێکەڵەی شین و مۆری کەم */
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 12px 24px !important;
        font-size: 16px !important;
        font-weight: bold !important;
        width: 100%;
        transition: all 0.3s ease;
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.3);
    }
    
    /* دوگمە بچووکەکانی بەشەکان */
    .category-box {
        background: #F3E8FF; /* مۆری کەم */
        color: #6B21A8;
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    /* ڕێکخستنی فۆنتی ڕادیۆ بتنەکان لە خوارەوە */
    div.stRadio > div {
        gap: 10px;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# ٢. شاشەی سەرەکی (🏠 Home)
# ==========================================
if st.session_state.current_page == '🏠 Home':
    st.markdown("<h2 style='color: #1E3A8A; margin-bottom: 0;'>سڵاو دانیال 👋</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B;'>بەخێرهاتی بۆ Danyal Health</p>", unsafe_allow_html=True)
    
    st.text_input("🔍 گەڕان بۆ نەخۆشی، دکتۆر، دەرمان...", placeholder="لێرە بنووسە...")
    
    st.write("")
    
    st.markdown("<div class='custom-card' style='text-align: center;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #3B82F6;'>سیستەمی زیرەکی پشکنین</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B;'>نیشانەکانت دەستنیشان بکە بۆ وەرگرتنی ڕاپۆرتی سەرەتایی</p>", unsafe_allow_html=True)
    if st.button("📊 شیکاری نیشانەکان"):
        st.session_state.current_page = '🩺 Analyze'
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='color: #1E3A8A;'>بەشەکان</h3>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='category-box'>🦠 نەخۆشییە باوەکان</div>", unsafe_allow_html=True)
        st.markdown("<div class='category-box'>💊 دەرمان دۆزەرەوە</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='category-box'>👨‍⚕️ ڕاوێژی دکتۆر</div>", unsafe_allow_html=True)
        st.markdown("<div class='category-box'>📋 مێژووی شیکاری</div>", unsafe_allow_html=True)


# ==========================================
# ٣. شاشەی نیشانەکان (🩺 Analyze)
# ==========================================
elif st.session_state.current_page == '🩺 Analyze':
    st.markdown("<h2 style='color: #1E3A8A;'>🩺 هەڵبژاردنی نیشانەکان</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B;'>تکایە ئەو نیشانانەی هەستی پێدەکەیت دیاری بکە:</p>", unsafe_allow_html=True)
    
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    s1 = st.checkbox("☑️ سەرئێشە")
    s2 = st.checkbox("☑️ گەرمی (تا)")
    s3 = st.checkbox("☑️ کۆخە")
    s4 = st.checkbox("☑️ ماندووبوون و بێهێزی")
    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.button("پڕۆسەی شیکاری بکە ➔"):
        if s1 or s2 or s3 or s4:
            st.session_state.current_page = 'Result_Page'
            st.rerun()
        else:
            st.warning("تکایە لانی کەم یەک نیشانە هەڵبژێرە.")


# ==========================================
# ٤. شاشەی ئەنجام (Result Page)
# ==========================================
elif st.session_state.current_page == 'Result_Page':
    st.markdown("<h2 style='color: #1E3A8A;'>📊 ئەنجامی شیکاری زیرەک</h2>", unsafe_allow_html=True)
    
    with st.spinner('خەریکی لێکدانەوەی نیشانەکانین...'):
        time.sleep(1)
        
    st.markdown("""
    <div class='custom-card' style='border-right: 5px solid #3B82F6;'>
        <h2 style='color: #3B82F6; margin-bottom:0;'>78% گومان بە سەرماخۆری</h2>
        <p style='color: #64748B;'>ئەم ئەنجامە بەپێی ئەو نیشانانەیە کە دیاریت کردوون.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    st.markdown("<h4>💡 ڕاوێژ و ڕێنمایی:</h4>", unsafe_allow_html=True)
    st.write("• خواردنەوەی شلەمەنی گەرم و پشوودانی تەواو لە ماڵەوە.")
    st.write("• وەرگرتنی ڤیتامین C و بەکارهێنانی حەپی دژە تا لە کاتی پێویستدا.")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    st.markdown("<h4>👨‍⚕️ پێشنیاری دکتۆر:</h4>", unsafe_allow_html=True)
    st.write("ئەگەر نیشانەکان و تا کەیەت بۆ زیاتر لە ٣ ڕۆژ بەردەوام بوو، پێشنیار دەکەین سەردانی دکتۆری پسپۆڕی گشتی بکەیت.")
    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.button("گەڕانەوە بۆ شاشەی سەرەکی"):
        st.session_state.current_page = '🏠 Home'
        st.rerun()


# ==========================================
# ٥. شاشەی مێژوو (📋 History)
# ==========================================
elif st.session_state.current_page == '📋 History':
    st.markdown("<h2 style='color: #1E3A8A;'>📋 مێژووی شیکارییەکان</h2>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='custom-card'>
        <span style='color: #8B5CF6; font-weight: bold;'>2026-05-20</span>
        <h4>شیکاری سەرماخۆری</h4>
        <p style='color: #10B981;'>دۆخ: چاکبووەتەوە</p>
    </div>
    <div class='custom-card'>
        <span style='color: #8B5CF6; font-weight: bold;'>2026-04-12</span>
        <h4>پشکنینی گشتی تاقیگە</h4>
        <p style='color: #64748B;'>دۆخ: ئەرشیف کراوە</p>
    </div>
    """, unsafe_allow_html=True)


# ==========================================
# ٦. شاشەی پرۆفایل (👤 Profile)
# ==========================================
elif st.session_state.current_page == '👤 Profile':
    st.markdown("<h2 style='color: #1E3A8A;'>👤 پرۆفایلی بەکارهێنەر</h2>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='custom-card' style='text-align: center;'>
        <div style='background: #E0E7FF; width: 80px; height: 80px; border-radius: 50%; margin: 0 auto 10px auto; display: flex; align-items: center; justify-content: center; font-size: 32px;'>👤</div>
        <h3>دانیال</h3>
        <p style='color: #64748B;'>نەخۆشخانەی تایبەتی Danyal Health</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    st.write("**🔢 تەمەن:** ٢٢ ساڵ")
    st.write("**🚹 ڕەگەز:** نێر")
    st.write("**🩸 مێژووی نەخۆشی:** هۆکاری هەستیاری وەرزی")
    st.markdown("</div>", unsafe_allow_html=True)


# ==========================================
# ٧. دروستکردنی باشترین Bottom Navigation
# ==========================================
st.write("---")
nav_options = ['🏠 Home', '🩺 Analyze', '📋 History', '👤 Profile']

selected_nav = st.radio(
    "", 
    options=nav_options, 
    index=nav_options.index(st.session_state.current_page) if st.session_state.current_page in nav_options else 0,
    horizontal=True
)

if selected_nav != st.session_state.current_page:
    st.session_state.current_page = selected_nav
    st.rerun()
