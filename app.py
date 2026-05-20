import streamlit as st

# --- ١. ڕێکخستنی سەرەتایی پەیج ---
st.set_page_config(page_title="سالم - سالم", page_icon="💙", layout="centered")

# --- ٢. سێشەن ستەیت بۆ پاراستنی باری دوگمەکان ---
if 'dark_mode' not in st.session_state: st.session_state.dark_mode = False

# --- ٣. ڕێکخستنی شێواز و دیزاینی مۆدێرن (CSS) ---
bg_color = "#111827" if st.session_state.dark_mode else "#F8FAFC"
card_color = "#1F2937" if st.session_state.dark_mode else "#FFFFFF"
text_color = "#F9FAFB" if st.session_state.dark_mode else "#1E3A8A"
sub_text = "#9CA3AF" if st.session_state.dark_mode else "#64748B"
border_color = "#374151" if st.session_state.dark_mode else "#E2E8F0"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@300;400;600;700&display=swap');
    
    * {{
        font-family: 'Noto Sans Arabic', sans-serif !important;
        direction: rtl;
    }}
    .stApp {{ background-color: {bg_color}; }}
    h1, h2, h3, h4, p, span, label {{ color: {text_color} !important; }}
    
    /* کارتەکان */
    .custom-card {{
        background: {card_color}; padding: 22px; border-radius: 20px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
        border: 1px solid {border_color}; margin-bottom: 15px;
        text-align: center;
    }}
    
    /* کارتی سەرەکی شیکاری */
    .main-gradient-card {{
        background: linear-gradient(135deg, #3B82F6, #8B5CF6);
        padding: 25px; border-radius: 24px; text-align: center; color: white !important;
        box-shadow: 0 8px 20px rgba(59, 130, 246, 0.15); margin-bottom: 20px;
    }}
    
    /* بەشەکانی خزمەتگوزاری (Grid) */
    .category-box {{
        background: {card_color}; color: {text_color}; padding: 20px; border-radius: 18px; 
        text-align: center; font-weight: bold; margin-bottom: 12px; border: 1px solid {border_color};
        box-shadow: 0 2px 8px rgba(0,0,0,0.02); font-size: 15px;
    }}

    /* ==========================================
       ✨ دیزاینی مۆدێرنی باڕی خوارەوە (Bottom Tab Bar) بە کوردی
       ========================================== */
    div[data-testid="stRadio"] {{
        background-color: {card_color} !important;
        border: 1px solid {border_color} !important;
        border-radius: 24px !important;
        padding: 10px !important;
        box-shadow: 0 -10px 30px rgba(0, 0, 0, 0.04) !important;
        position: relative;
        margin-top: 30px;
    }}
    /* وونکردنی تایتڵی سەرەکی و نەخوازراوی ڕادیۆ */
    div[data-testid="stRadio"] [data-testid="stWidgetLabel"] {{
        display: none !important;
    }}
    /* ڕێکخستنی ئاسۆیی تابەکان */
    div[data-testid="stRadio"] > div[role="radiogroup"] {{
        display: flex !important;
        flex-direction: row !important;
        justify-content: space-between !important;
        width: 100% !important;
        gap: 6px !important;
    }}
    /* شێوازی گشتی هەر تابێک */
    div[data-testid="stRadio"] label {{
        flex: 1 !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        background-color: transparent !important;
        padding: 10px 4px !important;
        border-radius: 18px !important;
        cursor: pointer !important;
        transition: all 0.25s ease-in-out !important;
        border: none !important;
    }}
    /* لادانی بازنە سەرەتاییەکەی سێلێکتەر */
    div[data-testid="stRadio"] label > div:first-child {{
        display: none !important;
    }}
    /* 🛠️ ڕێگریکردن لە دابەشبوون یان شکانی دەقی کوردی (No Wrap) */
    div[data-testid="stRadio"] label p {{
        color: {text_color} !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        margin: 0 !important;
        white-space: nowrap !important;  /* ڕێگری لە دابەشبوونی وشەکان دەکات */
        overflow: visible !important;
    }}
    /* کاتێک ماوس دەبرێتە سەر تابەکان */
    div[data-testid="stRadio"] label:hover {{
        background-color: {bg_color} !important;
    }}
    /* 🔥 شێوازی تابی دیاریکراو و چالاک (Active Selected Tab) */
    div[data-testid="stRadio"] label:has(input:checked) {{
        background: linear-gradient(135deg, #3B82F6, #8B5CF6) !important;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.25) !important;
    }}
    div[data-testid="stRadio"] label:has(input:checked) p {{
        color: #FFFFFF !important;
    }}
</style>
""", unsafe_allow_html=True)

# --- ٤. هێدەر و گۆڕینی مۆد (ڕووناکی / تاریکی) ---
col_logo, col_mode = st.columns([5, 1])
with col_logo:
    st.markdown("<h3 style='margin:0;'>سالم 💙</h3>", unsafe_allow_html=True)
with col_mode:
    if st.button("🌙" if not st.session_state.dark_mode else "☀️", key="mode_toggle"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

st.write("---")

# ==========================================
# 🏠 نیشاندانی دیزاینی شاشەی سەرەکی (تەنها وەک ڕووکار)
# ==========================================
st.markdown("<p style='margin-bottom: 5px; font-size: 18px; font-weight: bold;'>سڵاو دانیال 👋</p>", unsafe_allow_html=True)
st.markdown(f"<p style='color: {sub_text}; margin-top: 0px; margin-bottom: 20px;'>چۆن هەست دەکەیت؟</p>", unsafe_allow_html=True)

# سندوقی گەڕان وەک ناو شاشەکە
st.text_input("", placeholder="🔍 گەڕان بۆ نیشانە یان نەخۆشی...", label_visibility="collapsed", key="search_bar")

st.write("")

# کارتی گڕادێنتی گەورەی شیکاری (وەک نێو وێنەی یەکەم)
st.markdown(f"""
<div class="main-gradient-card">
    <h3 style="color: white !important; margin-top: 0;">شیکاری نیشانەکان</h3>
    <p style="color: rgba(255,255,255,0.9) !important; font-size: 14px;">نیشانەکانت بنووسە و بە شێوەیەکى زیرەک شیکاریان بۆ دەکەین.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<p style='font-weight: bold; margin-bottom: 12px;'>خزمەتگوزارییەکان</p>", unsafe_allow_html=True)

# گریدی بەشەکان (٢ بە ٢)
col1, col2 = st.columns(2)
with col1:
    st.markdown("<div class='category-box'>🦠 نەخۆشییە باوەکان</div>", unsafe_allow_html=True)
    st.markdown("<div class='category-box'>🩺 شیکاری نیشانەکان</div>", unsafe_allow_html=True)
with col2:
    st.markdown("<div class='category-box'>📋 پەیڕەوی تەندروستی</div>", unsafe_allow_html=True)
    st.markdown("<div class='category-box'>🤖 دکتۆرێکی زیرەک</div>", unsafe_allow_html=True)

# ==========================================
# 🗺️ باڕی خوارەوەی مۆدێرن و ڕێکخراو (Bottom Navigation)
# ==========================================
st.write("---")

# لیستەکە بە کوردی ڕێکخراوە و بەهۆی CSSـەوە کاتێک کلیکی لێدەکەیت تەنها ڕەنگی دەگۆڕێت و هیچ نابێت
nav_options = ['👤 پرۆفایل', '📋 مێژوو', '🩺 شیکاری', '🏠 سەرەکی']

selected_nav = st.radio(
    "", 
    options=nav_options, 
    index=3, # بە شێوازی دیفۆڵت لەسەر "سەرەکی" دەبێت
    horizontal=True, 
    label_visibility="collapsed",
    key="decorative_bottom_nav"
)
