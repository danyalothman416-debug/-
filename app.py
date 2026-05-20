import streamlit as st
import time

# --- ١. ڕێکخستنی سەرەتایی پەیج ---
st.set_page_config(page_title="Danyal Health", page_icon="💙", layout="centered")

# --- ٢. پێناسەکردنی زمانەکان (Multi-Language Dictionary) ---
LANG_DATA = {
    "Kurdish": {
        "dir": "rtl", "font": "Noto Sans Arabic",
        "welcome": "سڵاو دانیال 👋", "sub_welcome": "بەخێرهاتی بۆ Danyal Health",
        "search": "🔍 گەڕان بۆ نەخۆشی، دکتۆر، دەرمان...", "search_placeholder": "لێرە بنووسە...",
        "categories": "بەشەکان",
        "cat1": "🦠 نەخۆشییە باوەکان", "cat2": "💊 دەرمان دۆزەرەوە", "cat3": "👨‍⚕️ ڕاوێژی دکتۆر", "cat4": "📋 مێژووی شیکاری",
        "chat_title": "🤖 پزیشکی زیرەک (Gemini AI)", "chat_ask": "چی هەست دەکەیت؟ نیشانەکانت لێرە بنووسە...",
        "voice_btn": "🎤 تۆمارکردنی دەنگ (Voice Input)", "cam_title": "📷 پشکنین بە کامێرا (Skin/Eye Scan)",
        "cam_upload": "وێنەی پێست، چاوی سوور، یان برین دابنێ...", "analyze_btn": "شیکاری بکە",
        "history_title": "📋 مێژووی شیکارییەکان", "profile_title": "👤 پرۆفایلی بەکارهێنەر", "age": "تەمەن", "gender": "ڕەگەز", "male": "نێر"
    },
    "English": {
        "dir": "ltr", "font": "Poppins",
        "welcome": "Hello Danyal 👋", "sub_welcome": "Welcome to Danyal Health",
        "search": "🔍 Search for diseases, doctors, medicines...", "search_placeholder": "Type here...",
        "categories": "Categories",
        "cat1": "🦠 Common Diseases", "cat2": "💊 Pill Finder", "cat3": "👨‍⚕️ Doctor Consult", "cat4": "📋 Medical History",
        "chat_title": "🤖 AI Doctor (Gemini)", "chat_ask": "What do you feel? Describe your symptoms...",
        "voice_btn": "🎤 Voice Input (Record)", "cam_title": "📷 Camera Scan (Skin/Eye)",
        "cam_upload": "Upload image of skin, red eye, or wound...", "analyze_btn": "Analyze Now",
        "history_title": "📋 Analysis History", "profile_title": "👤 User Profile", "age": "Age", "gender": "Gender", "male": "Male"
    },
    "Arabic": {
        "dir": "rtl", "font": "Noto Sans Arabic",
        "welcome": "مرحباً دانيال 👋", "sub_welcome": "مرحباً بك في Danyal Health",
        "search": "🔍 ابحث عن الأمراض، الأطباء، الأدوية...", "search_placeholder": "اكتب هنا...",
        "categories": "الأقسام",
        "cat1": "🦠 الأمراض الشائعة", "cat2": "💊 دليل الأدوية", "cat3": "👨‍⚕️ استشارة طبيب", "cat4": "📋 سجل التحاليل",
        "chat_title": "🤖 طبيب الذكاء الاصطناعي (Gemini)", "chat_ask": "بماذا تشعر؟ اكتب أعراضك هنا...",
        "voice_btn": "🎤 إدخال صوتي", "cam_title": "📷 الفحص بالكاميرا (الجلد/العين)",
        "cam_upload": "ارفع صورة للجلد، احمرار العين، أو الجرح...", "analyze_btn": "ابدأ التحليل",
        "history_title": "📋 سجل التحليلات", "profile_title": "👤 ملف المستخدم", "age": "العمر", "gender": "الجنس", "male": "ذكر"
    }
}

# --- ٣. بەڕێوەبردنی سێشەنەکان (Session States) ---
if 'current_page' not in st.session_state: st.session_state.current_page = '🏠 Home'
if 'dark_mode' not in st.session_state: st.session_state.dark_mode = False
if 'lang' not in st.session_state: st.session_state.lang = 'Kurdish'

L = LANG_DATA[st.session_state.lang]

# --- ٤. دینامیکیەتی Dark Mode و ڕووناکی لەگەڵ فۆنتەکان ---
bg_color = "#111827" if st.session_state.dark_mode else "#F8FAFC"
card_color = "#1F2937" if st.session_state.dark_mode else "#FFFFFF"
text_color = "#F9FAFB" if st.session_state.dark_mode else "#1E3A8A"
sub_text = "#9CA3AF" if st.session_state.dark_mode else "#64748B"
border_color = "#374151" if st.session_state.dark_mode else "#E2E8F0"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@300;400;700&family=Poppins:wght@300;400;600&display=swap');
    
    * {{
        font-family: '{L["font"]}', 'sans-serif' !important;
        direction: {L["dir"]};
    }}
    .stApp {{ background-color: {bg_color}; }}
    h1, h2, h3, h4, p, span, label {{ color: {text_color} !important; }}
    .custom-card {{
        background: {card_color}; padding: 25px; border-radius: 16px;
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.08);
        border: 1px solid {border_color}; margin-bottom: 15px;
        text-align: center;
    }}
    div.stButton > button {{
        background: linear-gradient(135deg, #3B82F6, #8B5CF6) !important;
        color: white !important; border-radius: 12px !important; border: none !important;
        padding: 14px 24px !important; font-size: 16px !important; font-weight: bold !important; width: 100%;
        box-shadow: 0 4px 10px rgba(59, 130, 246, 0.2);
    }}
    div.stButton > button:hover {{
        transform: translateY(-1px);
        box-shadow: 0 6px 15px rgba(59, 130, 246, 0.3);
    }}
    .category-box {{
        background: {card_color}; color: {text_color}; padding: 18px; border-radius: 14px; 
        text-align: center; font-weight: bold; margin-bottom: 12px; border: 1px solid {border_color};
        box-shadow: 0 2px 6px rgba(0,0,0,0.02);
    }}
</style>
""", unsafe_allow_html=True)

# --- ٥. بەشی سەرەوەی سابت: کۆنتڕۆڵی ڕووناکی و زمان ---
col_mode, col_lang = st.columns([1, 2])
with col_mode:
    if st.button("🌙" if not st.session_state.dark_mode else "☀️", key="mode_toggle"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()
with col_lang:
    languages_list = ["Kurdish", "English", "Arabic"]
    selected_lang = st.selectbox(
        "", 
        options=languages_list, 
        index=languages_list.index(st.session_state.lang), 
        label_visibility="collapsed",
        key="lang_select"
    )
    if selected_lang != st.session_state.lang:
        st.session_state.lang = selected_lang
        st.rerun()

st.write("---")

# ==========================================
# 🏠 HOME PAGE
# ==========================================
if st.session_state.current_page == '🏠 Home':
    st.markdown(f"<h2 style='margin-bottom: 0;'>{L['welcome']}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: {sub_text}; margin-top: 4px;'>{L['sub_welcome']}</p>", unsafe_allow_html=True)
    
    st.text_input(L["search"], placeholder=L["search_placeholder"], key="home_search")
    st.write("")
    
    st.markdown(f"<h3 style='margin-bottom: 15px;'>{L['categories']}</h3>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<div class='category-box'>{L['cat1']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='category-box'>{L['cat2']}</div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='category-box'>{L['cat3']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='category-box'>{L['cat4']}</div>", unsafe_allow_html=True)

# ==========================================
# 🩺 ANALYZE / AI CHAT & CAMERA
# ==========================================
elif st.session_state.current_page == '🩺 Analyze':
    st.markdown(f"<h2>{L['chat_title']}</h2>", unsafe_allow_html=True)
    
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    st.chat_input(L["chat_ask"], key="gemini_chat_input")
    if st.button(L["voice_btn"], key="voice_input_btn"):
        st.toast("🎙️ گوێ دەگرم... دەنگەکەت تۆمار دەکرێت...", icon="🎤")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown(f"<h3>{L['cam_title']}</h3>", unsafe_allow_html=True)
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader(L["cam_upload"], type=["png", "jpg", "jpeg"], key="camera_uploader")
    if uploaded_file is not None:
        st.image(uploaded_file, width=250, caption="وێنەی بارکراو")
    
    if st.button(L["analyze_btn"], key="run_ai_analysis"):
        with st.spinner('Gemini AI 🤖 خەریکی لێکدانەوەی زانیاری و وێنەکانە...'):
            time.sleep(2)
        st.success("✅ ئەنجامی شیکاری ئامادەیە: 78% نیشانەکانی سەرماخۆری سەرەتایی.")
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 📋 HISTORY PAGE
# ==========================================
elif st.session_state.current_page == '📋 History':
    st.markdown(f"<h2>{L['history_title']}</h2>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class='custom-card'>
        <span style='color: #8B5CF6; font-weight: bold;'>2026-05-20</span>
        <h4>سکانی کامێرا - سووربوونی چاو</h4>
        <p style='color: #EF4444;'>حاڵەت: هەستیاری کاتی</p>
    </div>
    <div class='custom-card'>
        <span style='color: #8B5CF6; font-weight: bold;'>2026-04-12</span>
        <h4>چاتی پزیشکی لەگەڵ جێمینی</h4>
        <p style='color: #64748B;'>چارەسەر: نووسرانی دەرمانی پاراسیتامۆڵ</p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 👤 PROFILE PAGE
# ==========================================
elif st.session_state.current_page == '👤 Profile':
    st.markdown(f"<h2>{L['profile_title']}</h2>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class='custom-card' style='text-align: center; margin: 0 auto;'>
        <div style='background: #E0E7FF; width: 80px; height: 80px; border-radius: 50%; margin: 0 auto 10px auto; display: flex; align-items: center; justify-content: center; font-size: 32px;'>👤</div>
        <h3>دانیال</h3>
        <p style='color: {sub_text};'>Danyal Health ID: #9921</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"<div class='custom-card'>", unsafe_allow_html=True)
    st.write(f"**🔢 {L['age']}:** ٢٢ ساڵ")
    st.write(f"**🚹 {L['gender']}:** {L['male']}")
    st.markdown("</div>", unsafe_allow_html=True)

# --- ٦. دروستکردنی باڕی خوارەوە (Bottom Navigation) ---
st.write("---")
nav_options = ['🏠 Home', '🩺 Analyze', '📋 History', '👤 Profile']
selected_nav = st.radio(
    "", 
    options=nav_options, 
    index=nav_options.index(st.session_state.current_page) if st.session_state.current_page in nav_options else 0, 
    horizontal=True, 
    label_visibility="collapsed",
    key="bottom_nav"
)

if selected_nav != st.session_state.current_page:
    st.session_state.current_page = selected_nav
    st.rerun()
