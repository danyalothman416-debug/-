import streamlit as st

# ١. ڕێکخستنی سەرەتایی ئەپەکە
st.set_page_config(page_title="Future Doctor", page_icon="🩺", layout="centered", initial_sidebar_state="collapsed")

# ٢. دیزاینی مۆدێرن بۆ ئەپەکە
st.markdown("""
    <style>
    .stApp { background-color: #f4f6f9; }
    .card {
        background-color: white; padding: 20px; border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px;
    }
    div.stButton > button {
        width: 100%; border-radius: 15px; background-color: #007AFF;
        color: white; font-weight: bold; border: none; height: 45px;
    }
    </style>
""", unsafe_allow_html=True)

# ٣. داتابەیسی کاتی بۆ گەیمیفیکەیشن (XP و ئاستەکان)
if 'xp' not in st.session_state:
    st.session_state.xp = 0
if 'level' not in st.session_state:
    st.session_state.level = "Student"
if 'page' not in st.session_state:
    st.session_state.page = "Roadmap"

# دیاریکردنی ئاست بەپێی XP
if st.session_state.xp >= 1000: st.session_state.level = "Specialist 🏆"
elif st.session_state.xp >= 500: st.session_state.level = "Resident 🩺"
elif st.session_state.xp >= 100: st.session_state.level = "Intern 🏥"

# ٤. دروستکردنی مینیوی گەڕان (Navigation)
st.sidebar.title("🩺 Future Doctor")
st.sidebar.write(f"**ئاست:** {st.session_state.level} | **XP:** {st.session_state.xp}")
menu = st.sidebar.radio("بەشەکان", ["🗺️ Career Roadmap", "🚑 AI Case Simulator", "🏆 پرۆفایل و دەستکەوتەکان"])

st.session_state.page = menu

# ==========================================
# بەشی یەکەم: Doctor Career Roadmap
# ==========================================
if st.session_state.page == "🗺️ Career Roadmap":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.title("🗺️ نەخشەی ڕێگای پزیشکی")
    st.write("با AI تایبەت بە خۆت پلانێکت بۆ دروست بکات.")
    
    col1, col2 = st.columns(2)
    with col1:
        year = st.selectbox("لە چ قۆناغێکیت؟", ["قۆناغی ١", "قۆناغی ٢", "قۆناغی ٣", "قۆناغی ٤", "قۆناغی ٥", "قۆناغی ٦"])
    with col2:
        interest = st.selectbox("حەزت لە چ بوارێکە؟", ["نەزانراوە", "نەشتەرگەری (Surgery)", "دڵ (Cardiology)", "منداڵان (Pediatrics)", "هەناوی (Internal Med)"])
    
    if st.button("پلانم بۆ دروست بکە بە AI 🤖"):
        # لێرەدا لە داهاتوودا پەیوەندی بە OpenAI API دەکەین
        st.success(f"پلانەکە ئامادەیە بۆ فێرخوازی {year} کە ئارەزووی {interest} دەکات!")
        st.info("📅 **پلانی ئەم هەفتەیە:**\n\n* خوێندنەوەی Anatomy بەشی دڵ.\n* چارەسەرکردنی ٣ Clinical Cases.\n* سەیرکردنی ڤیدیۆی فێرکاری ECG.")
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# بەشی دووەم: AI Case Simulator
# ==========================================
elif st.session_state.page == "🚑 AI Case Simulator":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.title("🚑 نەخۆشخانەی خەیاڵی")
    st.write("تۆ ئێستا پزیشکی ئێشکگریت. نەخۆشێک هاتووەتە ژوورەوە.")
    
    st.warning("**نەخۆش:** پیاوێکی تەمەن ٤٥ ساڵ، سینگ ئێشەیەکی زۆری هەیە و ئارەقەی کردووە.")
    
    action = st.radio("چی دەکەیت وەکو پزیشک؟", ["پرسیاری مێژووی نەخۆشییەکەی دەکەم", "ڕاستەوخۆ ECG ی بۆ دەکەم", "حەبی ئازارشکێنی دەدەمێ"])
    
    if st.button("ئەنجامدانی بڕیار 🩺"):
        if action == "ڕاستەوخۆ ECG ی بۆ دەکەم":
            st.success("بڕیارێکی زۆر دروستە! لەم جۆرە حاڵەتانەدا کات زێڕە. (+50 XP) 🎉")
            st.session_state.xp += 50
        else:
            st.error("پێویستە خێراتر بیت بۆ حاڵەتی دڵ! باشترین بژاردە پێش هەر شتێک ECG یە.")
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# بەشی سێیەم: پرۆفایل و XP
# ==========================================
elif st.session_state.page == "🏆 پرۆفایل و دەستکەوتەکان":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.title("🏆 پرۆفایلی پزیشک")
    
    st.header(f"ئاستی ئێستا: {st.session_state.level}")
    st.progress(min(st.session_state.xp / 1000, 1.0))
    st.write(f"**کۆی گشتی خاڵەکان (XP):** {st.session_state.xp}")
    
    st.subheader("مەدالیاکان (Badges)")
    if st.session_state.xp >= 50:
        st.write("🥇 **First Life Saved** (ڕزگارکەری یەکەم ژیان)")
    else:
        st.write("هێشتا هیچ مەدالیایەکت بەدەست نەهێناوە. بڕۆ نەخۆشەکان چارەسەر بکە!")
    st.markdown("</div>", unsafe_allow_html=True)
