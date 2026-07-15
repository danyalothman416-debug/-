import streamlit as st
from PIL import Image
import base64
from io import BytesIO

# Page configuration
st.set_page_config(
    page_title="بەڕێوەبەرایەتی پرۆژە",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Kurdish fonts and beautiful design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Naskh+Arabic:wght@400;700&display=swap');
    
    /* Main background gradient */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: 'Noto Naskh Arabic', serif;
    }
    
    /* Custom card styling */
    .custom-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 30px;
        margin: 20px 0;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .custom-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 50px rgba(0, 0, 0, 0.3);
    }
    
    /* Title styling */
    .main-title {
        color: white;
        text-align: center;
        font-size: 3rem;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
        direction: rtl;
    }
    
    .subtitle {
        color: rgba(255, 255, 255, 0.9);
        text-align: center;
        font-size: 1.5rem;
        margin-bottom: 40px;
        direction: rtl;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 50px;
        padding: 15px 40px;
        font-size: 1.2rem;
        font-weight: 700;
        font-family: 'Noto Naskh Arabic', serif;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #667eea;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #667eea;
    }
    
    .metric-label {
        font-size: 1.1rem;
        color: #666;
        direction: rtl;
    }
    
    /* RTL support */
    .rtl {
        direction: rtl;
        text-align: right;
        font-family: 'Noto Naskh Arabic', serif;
    }
    
    /* Success message styling */
    .success-message {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        padding: 20px;
        border-radius: 15px;
        color: #1a1a2e;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# Background image function
def add_bg_from_url():
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%), 
                        url('https://images.unsplash.com/photo-1557683316-973673baf926?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80');
            background-size: cover;
            background-position: center;
            background-blend-mode: overlay;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Icon generator function
def create_icon_svg():
    svg_icon = '''
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
        <defs>
            <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
            </linearGradient>
        </defs>
        <circle cx="50" cy="50" r="45" fill="url(#grad)"/>
        <text x="50" y="55" font-size="40" text-anchor="middle" fill="white" font-family="Arial">✦</text>
    </svg>
    '''
    return svg_icon

# Main app
def main():
    # Add background
    add_bg_from_url()
    
    # Header section
    st.markdown('<h1 class="main-title">🌟 بەڕێوەبەرایەتی پرۆژەی کوردی</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">سیستەمی بەڕێوەبردنی ئەرک و پرۆژەکان بە زمانی کوردی</p>', unsafe_allow_html=True)
    
    # Sidebar with profile
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 20px;">
            <img src="https://ui-avatars.com/api/?name=User&background=667eea&color=fff&size=100" 
                 style="border-radius: 50%; margin-bottom: 15px;"/>
            <h3 style="color: white; direction: rtl;">بەخێربێیت بەکارهێنەر</h3>
            <hr style="border-color: rgba(255,255,255,0.2);"/>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation
        st.markdown('<h4 style="color: white; direction: rtl;">📋 ناوەڕۆکی پەیج</h4>', unsafe_allow_html=True)
        
        if st.button("🏠 سەرەکی"):
            st.session_state.page = "home"
        if st.button("📊 ئامارەکان"):
            st.session_state.page = "stats"
        if st.button("⚙️ ڕێکخستنەکان"):
            st.session_state.page = "settings"
        if st.button("📝 تێبینیەکان"):
            st.session_state.page = "notes"
    
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = "home"
    
    # Main content area
    if st.session_state.page == "home":
        home_page()
    elif st.session_state.page == "stats":
        stats_page()
    elif st.session_state.page == "settings":
        settings_page()
    elif st.session_state.page == "notes":
        notes_page()

def home_page():
    # Welcome card
    st.markdown("""
    <div class="custom-card">
        <h2 class="rtl" style="color: #333; margin-bottom: 15px;">👋 بەخێربێیت بۆ سیستەمی بەڕێوەبەرایەتی</h2>
        <p class="rtl" style="color: #666; font-size: 1.1rem; line-height: 1.8;">
            ئەم سیستەمە بۆ یارمەتیدانت لە ڕێکخستنی کارووباری ڕۆژانە و پرۆژەکانت دروست کراوە.
            دەتوانیت ئەرکەکانت زیاد بکەیت، دۆخیان ببینیت، و ڕێکخستنەکانت بەپێی پێویست بگۆڕیت.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Metrics row
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">12</div>
            <div class="metric-label">پرۆژەی چالاک</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">85%</div>
            <div class="metric-label">ڕێژەی تەواوبوون</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">5</div>
            <div class="metric-label">ئەرکی ڕۆژانە</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Task input section
    st.markdown("""
    <div class="custom-card">
        <h3 class="rtl" style="color: #333;">📝 زیادکردنی ئەرکی نوێ</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        new_task = st.text_input("", placeholder="ناوی ئەرکەکەت لێرە بنووسە...", key="task_input")
    
    with col2:
        if st.button("➕ زیاد بکە"):
            if new_task:
                if 'tasks' not in st.session_state:
                    st.session_state.tasks = []
                st.session_state.tasks.append({"task": new_task, "done": False})
                st.success("ئەرکەکەت بە سەرکەوتوویی زیاد کرا!")
    
    # Display tasks
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown('<h3 class="rtl" style="color: #333;">📋 لیستی ئەرکەکان</h3>', unsafe_allow_html=True)
    
    if 'tasks' in st.session_state and st.session_state.tasks:
        for idx, task in enumerate(st.session_state.tasks):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f'<p class="rtl" style="font-size: 1.1rem;">{task["task"]}</p>', unsafe_allow_html=True)
            with col2:
                if st.button("✅ تەواو", key=f"done_{idx}"):
                    st.session_state.tasks[idx]["done"] = True
                    st.success("ئەرکەکە تەواو بوو!")
            with col3:
                if st.button("🗑️ سڕینەوە", key=f"del_{idx}"):
                    del st.session_state.tasks[idx]
                    st.rerun()
    else:
        st.info("هیچ ئەرکێک تۆمار نەکراوە. ئەرکێکی نوێ زیاد بکە!")
    
    st.markdown('</div>', unsafe_allow_html=True)

def stats_page():
    st.markdown("""
    <div class="custom-card">
        <h2 class="rtl" style="color: #333;">📊 ئامارەکانی سیستەم</h2>
        <p class="rtl" style="color: #666;">ڕاپۆرتی وردەکاری ئامارەکانی بەڕێوەبەرایەتی پرۆژەکان</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sample chart
    chart_data = {
        "تەواوکراو": 65,
        "لەکاردا": 25,
        "دواکەوتوو": 10
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown('<h4 class="rtl">📈 دۆخی پرۆژەکان</h4>', unsafe_allow_html=True)
        st.bar_chart(chart_data)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown('<h4 class="rtl">📊 ڕێژەی تەواوبوون</h4>', unsafe_allow_html=True)
        st.progress(0.65)
        st.markdown('<p class="rtl" style="color: #667eea; font-size: 2rem; font-weight: 700;">65%</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

def settings_page():
    st.markdown("""
    <div class="custom-card">
        <h2 class="rtl" style="color: #333;">⚙️ ڕێکخستنەکان</h2>
        <p class="rtl" style="color: #666;">ڕێکخستنەکانی سیستەمەکەت بەپێی پێویست دەستکاری بکە</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    
    # Settings options
    st.markdown('<h4 class="rtl">🌍 زمان</h4>', unsafe_allow_html=True)
    language = st.selectbox("", ["کوردی", "عەرەبی", "ئینگلیزی"], key="lang")
    
    st.markdown('<h4 class="rtl">🔔 ئاگادارکردنەوە</h4>', unsafe_allow_html=True)
    notifications = st.toggle("چالاککردنی ئاگادارکردنەوەکان", value=True)
    
    st.markdown('<h4 class="rtl">🎨 ڕەنگی بابەت</h4>', unsafe_allow_html=True)
    theme = st.select_slider("", options=["ڕووناک", "تاریک", "شین", "سەوز"])
    
    st.markdown('<h4 class="rtl">📊 ڕێکخستنی پرۆژەکان</h4>', unsafe_allow_html=True)
    project_limit = st.slider("ژمارەی زۆرترین پرۆژە", 1, 50, 20)
    
    if st.button("💾 پاشەکەوتکردنی ڕێکخستنەکان"):
        st.success("ڕێکخستنەکانت بە سەرکەوتوویی پاشەکەوت کرا!")
    
    st.markdown('</div>', unsafe_allow_html=True)

def notes_page():
    st.markdown("""
    <div class="custom-card">
        <h2 class="rtl" style="color: #333;">📝 تێبینیەکان</h2>
        <p class="rtl" style="color: #666;">تێبینی و سەرنجەکانت لێرە تۆمار بکە</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    
    note_title = st.text_input("", placeholder="ناونیشانی تێبینی...", key="note_title")
    note_content = st.text_area("", placeholder="ناوەرۆکی تێبینیەکەت لێرە بنووسە...", height=150, key="note_content")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("💾 پاشەکەوتکردن"):
            if note_title and note_content:
                if 'notes' not in st.session_state:
                    st.session_state.notes = []
                st.session_state.notes.append({"title": note_title, "content": note_content})
                st.success("تێبینیەکەت پاشەکەوت کرا!")
    
    with col2:
        if st.button("🗑️ پاککردنەوە"):
            if 'notes' in st.session_state:
                st.session_state.notes = []
                st.success("هەموو تێبینیەکان پاککرانەوە!")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Show saved notes
    if 'notes' in st.session_state and st.session_state.notes:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown('<h4 class="rtl">📌 تێبینیە پاشەکەوتکراوەکان</h4>', unsafe_allow_html=True)
        for idx, note in enumerate(st.session_state.notes):
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); 
                        padding: 15px; border-radius: 10px; margin: 10px 0;">
                <h5 class="rtl" style="color: #333;">📌 {note['title']}</h5>
                <p class="rtl" style="color: #666;">{note['content']}</p>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
