import streamlit as st

# --- ١. ڕێکخستنی سەرەتایی پەیج ---
st.set_page_config(page_title="سالم", page_icon="💙", layout="centered")

# --- ٢. سێشەن ستەیت ---
if 'dark_mode' not in st.session_state: st.session_state.dark_mode = False
if 'current_page' not in st.session_state: st.session_state.current_page = '🏠 سەرەکی'

# --- ٣. ڕێکخستنی دیزاینی مۆدێرن (CSS) ---
bg_color = "#111827" if st.session_state.dark_mode else "#F8FAFC"
card_color = "#1F2937" if st.session_state.dark_mode else "#FFFFFF"
text_color = "#F9FAFB" if st.session_state.dark_mode else "#1E3A8A"
border_color = "#374151" if st.session_state.dark_mode else "#E2E8F0"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@300;400;600;700&display=swap');
    * {{ font-family: 'Noto Sans Arabic', sans-serif !important; direction: rtl; }}
    .stApp {{ background-color: {bg_color}; }}
    .category-box {{ background: {card_color}; color: {text_color}; padding: 20px; border-radius: 18px; text-align: center; font-weight: bold; margin-bottom: 12px; border: 1px solid {border_color}; cursor: pointer; }}
    .test-card {{ background: {card_color}; padding: 20px; border-radius: 20px; border: 1px solid {border_color}; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
    div[data-testid="stRadio"] {{ background-color: {card_color}; border: 1px solid {border_color}; border-radius: 24px; padding: 10px; }}
    div[data-testid="stRadio"] [data-testid="stWidgetLabel"] {{ display: none; }}
    div[data-testid="stRadio"] label:has(input:checked) {{ background: linear-gradient(135deg, #3B82F6, #8B5CF6); border-radius: 14px; }}
    div[data-testid="stRadio"] label:has(input:checked) p {{ color: white !important; }}
</style>
""", unsafe_allow_html=True)

# --- ٤. لۆجیکی لاپەڕەکان ---
if st.session_state.current_page == '🏠 سەرەکی':
    col_logo, col_mode = st.columns([5, 1])
    with col_mode:
        if st.button("🌙" if not st.session_state.dark_mode else "☀️"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()
    
    st.markdown("### سڵاو 👋")
    st.text_input("", placeholder="🔍 گەڕان...", label_visibility="collapsed")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧪 تێستەکان"): st.session_state.current_page = '🧪 تێستەکان'; st.rerun()
        if st.button("📚 ثیۆری"): pass
    with col2:
        if st.button("🔬 پراکتیکەڵ"): pass
        if st.button("ℹ️ دەربارەی ئێمە"): pass

elif st.session_state.current_page == '🧪 تێستەکان':
    st.markdown("## 🧪 تێستە باوەکان")
    tests = {
        "CBC (شیکاری خوێن)": "پشکنینی گشتی خوێن و ڕێژەی خڕۆکەکان.",
        "FBS (شەکرەی بەڕۆژوو)": "پشکنینی شەکر کاتێک کەسەکە بەڕۆژووە.",
        "TSH (ڕژێنی دەرەقی)": "پشکنینی چالاکی هۆرمۆنەکانی ڕژێنی دەرەقی.",
        "HbA1c (شەکری کەڵەکەبوو)": "مامناوەندی شەکر لە ماوەی ٣ مانگی ڕابردوودا.",
        "Lipid Profile (چەوری)": "پشکنینی کۆلیسترۆڵ و چەورییە زیانبەخشەکان."
    }
    for title, desc in tests.items():
        with st.expander(f"🔹 {title}"):
            st.markdown(f"<div class='test-card'><b>{title}</b><br>{desc}</div>", unsafe_allow_html=True)
    if st.button("⬅️ گەڕانەوە"): st.session_state.current_page = '🏠 سەرەکی'; st.rerun()

# --- ٥. باڕی خوارەوە ---
st.write("---")
nav_options = ['👤 پرۆفایل', '📋 مێژوو', '🩺 شیکاری', '🏠 سەرەکی']
selected_nav = st.radio("", options=nav_options, index=3, horizontal=True, label_visibility="collapsed")

if selected_nav != st.session_state.current_page:
    if selected_nav == '🏠 سەرەکی': st.session_state.current_page = '🏠 سەرەکی'; st.rerun()
