import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import pandas as pd

# Page configuration - Hide default sidebar
st.set_page_config(
    page_title="بەڕێوەبەرایەتی پرۆژە",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide default Streamlit sidebar and header
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        display: none;
    }
    header[data-testid="stHeader"] {
        display: none;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Custom CSS with Kurdish font
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Naskh+Arabic:wght@400;500;700;800&display=swap');
    
    * {
        font-family: 'Noto Naskh Arabic', serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }
    
    /* Main container */
    .main-container {
        display: flex;
        gap: 20px;
        padding: 20px;
        height: 100vh;
    }
    
    /* Custom sidebar */
    .custom-sidebar {
        width: 280px;
        min-width: 280px;
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border-radius: 25px;
        padding: 25px 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        height: fit-content;
        position: sticky;
        top: 20px;
    }
    
    .sidebar-logo {
        text-align: center;
        margin-bottom: 30px;
    }
    
    .sidebar-logo img {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        margin-bottom: 15px;
        border: 3px solid #667eea;
    }
    
    .sidebar-logo h3 {
        color: white;
        font-size: 1.3rem;
        font-weight: 700;
        direction: rtl;
    }
    
    .sidebar-logo p {
        color: rgba(255, 255, 255, 0.6);
        font-size: 0.8rem;
        direction: rtl;
    }
    
    /* Sidebar menu items */
    .menu-item {
        display: flex;
        align-items: center;
        padding: 12px 15px;
        margin: 5px 0;
        border-radius: 15px;
        cursor: pointer;
        transition: all 0.3s ease;
        direction: rtl;
        color: rgba(255, 255, 255, 0.7);
        text-decoration: none;
    }
    
    .menu-item:hover {
        background: rgba(102, 126, 234, 0.2);
        color: white;
        transform: translateX(-5px);
    }
    
    .menu-item.active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.3);
    }
    
    .menu-icon {
        font-size: 1.5rem;
        margin-left: 12px;
    }
    
    .menu-text {
        font-size: 1rem;
        font-weight: 500;
    }
    
    .menu-badge {
        background: #ff4757;
        color: white;
        padding: 2px 8px;
        border-radius: 20px;
        font-size: 0.75rem;
        margin-right: auto;
    }
    
    .sidebar-divider {
        border: none;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        margin: 20px 0;
    }
    
    .sidebar-footer {
        margin-top: auto;
        direction: rtl;
        color: rgba(255, 255, 255, 0.4);
        font-size: 0.7rem;
        text-align: center;
    }
    
    /* Content area */
    .content-area {
        flex: 1;
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border-radius: 25px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        overflow-y: auto;
    }
    
    /* Cards */
    .custom-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    .card-title {
        color: #302b63;
        font-weight: 700;
        font-size: 1.3rem;
        direction: rtl;
        margin-bottom: 15px;
    }
    
    /* Stats cards */
    .stat-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
        border-right: 4px solid #667eea;
        direction: rtl;
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: 800;
        color: #667eea;
    }
    
    .stat-label {
        color: #666;
        font-size: 0.9rem;
        margin-top: 5px;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 50px;
        padding: 12px 30px;
        font-size: 1rem;
        font-weight: 600;
        font-family: 'Noto Naskh Arabic', serif;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
    }
    
    /* Input fields */
    .stTextInput > div > div > input {
        border-radius: 15px;
        border: 2px solid #e0e0e0;
        padding: 12px 15px;
        font-family: 'Noto Naskh Arabic', serif;
        direction: rtl;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* RTL text */
    .rtl {
        direction: rtl;
        text-align: right;
    }
    
    /* Task list */
    .task-item {
        background: #f8f9fa;
        padding: 15px 20px;
        border-radius: 12px;
        margin: 10px 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
        direction: rtl;
        transition: all 0.3s ease;
    }
    
    .task-item:hover {
        background: #e9ecef;
        transform: translateX(-5px);
    }
    
    .task-done {
        background: #d4edda;
        text-decoration: line-through;
        opacity: 0.7;
    }
    
    /* Progress bar */
    .progress-container {
        background: #e9ecef;
        border-radius: 20px;
        height: 10px;
        margin: 15px 0;
    }
    
    .progress-fill {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        height: 100%;
        transition: width 0.5s ease;
    }
    
    /* Chart container */
    .chart-container {
        background: white;
        border-radius: 20px;
        padding: 20px;
        margin: 20px 0;
    }
    
    /* Notification dot */
    .notification-dot {
        width: 10px;
        height: 10px;
        background: #ff4757;
        border-radius: 50%;
        display: inline-block;
        margin-left: 5px;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.5); opacity: 0.7; }
        100% { transform: scale(1); }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = "home"
if 'tasks' not in st.session_state:
    st.session_state.tasks = []
if 'notes' not in st.session_state:
    st.session_state.notes = []

# Custom Sidebar HTML
def render_sidebar():
    sidebar_html = f"""
    <div class="custom-sidebar">
        <div class="sidebar-logo">
            <img src="https://ui-avatars.com/api/?name=Admin&background=667eea&color=fff&size=100" 
                 alt="پڕۆفایلی بەکارهێنەر"/>
            <h3>بەڕێوەبەرایەتی پرۆژە</h3>
            <p>سیستەمی بەڕێوەبردنی کارەکان</p>
        </div>
        
        <hr class="sidebar-divider">
        
        <div class="menu-item {'active' if st.session_state.current_page == 'home' else ''}" 
             onclick="handleMenuClick('home')">
            <span class="menu-icon">🏠</span>
            <span class="menu-text">سەرەکی</span>
        </div>
        
        <div class="menu-item {'active' if st.session_state.current_page == 'tasks' else ''}" 
             onclick="handleMenuClick('tasks')">
            <span class="menu-icon">📋</span>
            <span class="menu-text">ئەرکەکان</span>
            <span class="menu-badge">3</span>
        </div>
        
        <div class="menu-item {'active' if st.session_state.current_page == 'calendar' else ''}" 
             onclick="handleMenuClick('calendar')">
            <span class="menu-icon">📅</span>
            <span class="menu-text">ڕۆژمێر</span>
        </div>
        
        <div class="menu-item {'active' if st.session_state.current_page == 'stats' else ''}" 
             onclick="handleMenuClick('stats')">
            <span class="menu-icon">📊</span>
            <span class="menu-text">ئامارەکان</span>
        </div>
        
        <div class="menu-item {'active' if st.session_state.current_page == 'notes' else ''}" 
             onclick="handleMenuClick('notes')">
            <span class="menu-icon">📝</span>
            <span class="menu-text">تێبینیەکان</span>
        </div>
        
        <div class="menu-item {'active' if st.session_state.current_page == 'settings' else ''}" 
             onclick="handleMenuClick('settings')">
            <span class="menu-icon">⚙️</span>
            <span class="menu-text">ڕێکخستنەکان</span>
        </div>
        
        <hr class="sidebar-divider">
        
        <div class="sidebar-footer">
            <p>© 2024 بەڕێوەبەرایەتی پرۆژە</p>
            <p>وەشانی 1.0.0</p>
        </div>
    </div>
    """
    return sidebar_html

# Main app layout
def main():
    # Main container with two columns
    col1, col2 = st.columns([1, 3.5])
    
    # Left column - Custom Sidebar
    with col1:
        st.markdown(render_sidebar(), unsafe_allow_html=True)
        
        # Hidden buttons for navigation
        if st.button("🏠 سەرەکی", key="btn_home", help="بڕۆ بۆ پەیجی سەرەکی"):
            st.session_state.current_page = "home"
            st.rerun()
        if st.button("📋 ئەرکەکان", key="btn_tasks", help="بەڕێوەبردنی ئەرکەکان"):
            st.session_state.current_page = "tasks"
            st.rerun()
        if st.button("📅 ڕۆژمێر", key="btn_calendar", help="ڕۆژمێری پرۆژەکان"):
            st.session_state.current_page = "calendar"
            st.rerun()
        if st.button("📊 ئامارەکان", key="btn_stats", help="ئامارەکانی سیستەم"):
            st.session_state.current_page = "stats"
            st.rerun()
        if st.button("📝 تێبینیەکان", key="btn_notes", help="تێبینیەکانی من"):
            st.session_state.current_page = "notes"
            st.rerun()
        if st.button("⚙️ ڕێکخستنەکان", key="btn_settings", help="ڕێکخستنەکانی سیستەم"):
            st.session_state.current_page = "settings"
            st.rerun()
    
    # Right column - Content Area
    with col2:
        st.markdown('<div class="content-area">', unsafe_allow_html=True)
        
        if st.session_state.current_page == "home":
            home_page()
        elif st.session_state.current_page == "tasks":
            tasks_page()
        elif st.session_state.current_page == "calendar":
            calendar_page()
        elif st.session_state.current_page == "stats":
            stats_page()
        elif st.session_state.current_page == "notes":
            notes_page()
        elif st.session_state.current_page == "settings":
            settings_page()
        
        st.markdown('</div>', unsafe_allow_html=True)

# Pages
def home_page():
    st.markdown("""
    <div class="custom-card">
        <h2 class="card-title">👋 بەخێربێیت بۆ سیستەمی بەڕێوەبەرایەتی</h2>
        <p class="rtl" style="color: #666; line-height: 2;">
            ئەم سیستەمە بۆ یارمەتیدانت لە ڕێکخستنی کارووباری ڕۆژانە و پرۆژەکانت دروست کراوە.
            دەتوانیت ئەرکەکانت زیاد بکەیت، دۆخیان ببینیت، و ڕێکخستنەکانت بەپێی پێویست بگۆڕیت.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Stats row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-value">12</div>
            <div class="stat-label">پرۆژەی چالاک</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-value">85%</div>
            <div class="stat-label">ڕێژەی تەواوبوون</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-value">5</div>
            <div class="stat-label">ئەرکی ڕۆژانە</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-value">48</div>
            <div class="stat-label">کاتژمێری کار</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Recent activity
    st.markdown("""
    <div class="custom-card">
        <h3 class="card-title">🕐 دوایین چالاکییەکان</h3>
        <div class="task-item">
            <span>✅ پرۆژەی دیزاینی نوێ تەواو بوو</span>
            <small style="color: #999;">5 خولەک پێش ئێستا</small>
        </div>
        <div class="task-item">
            <span>📝 تێبینی نوێ زیاد کرا</span>
            <small style="color: #999;">30 خولەک پێش ئێستا</small>
        </div>
        <div class="task-item">
            <span>👥 ئەندامی نوێ زیاد بوو بۆ تیم</span>
            <small style="color: #999;">2 کاتژمێر پێش ئێستا</small>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick actions
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown('<h3 class="card-title">⚡ کردارە خێراکان</h3>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("➕ ئەرکی نوێ", key="quick_task"):
            st.session_state.current_page = "tasks"
            st.rerun()
    with col2:
        if st.button("📝 تێبینی نوێ", key="quick_note"):
            st.session_state.current_page = "notes"
            st.rerun()
    with col3:
        if st.button("📊 بینینی ئامار", key="quick_stats"):
            st.session_state.current_page = "stats"
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def tasks_page():
    st.markdown("""
    <div class="custom-card">
        <h2 class="card-title">📋 بەڕێوەبردنی ئەرکەکان</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Add task section
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        task_title = st.text_input("ناونیشانی ئەرک", placeholder="ناوی ئەرکەکەت بنووسە...", key="task_title")
    with col2:
        task_priority = st.selectbox("ئاستی گرنگی", ["بەرز", "مامناوەند", "نزم"], key="task_priority")
    with col3:
        st.write("")
        st.write("")
        if st.button("➕ زیادکردن", key="add_task"):
            if task_title:
                st.session_state.tasks.append({
                    "title": task_title,
                    "priority": task_priority,
                    "done": False,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                st.success("ئەرکەکەت بە سەرکەوتوویی زیاد کرا!")
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display tasks
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown('<h3 class="card-title">📌 ئەرکەکان</h3>', unsafe_allow_html=True)
    
    if st.session_state.tasks:
        for idx, task in enumerate(st.session_state.tasks):
            task_class = "task-item task-done" if task["done"] else "task-item"
            priority_emoji = "🔴" if task["priority"] == "بەرز" else "🟡" if task["priority"] == "مامناوەند" else "🟢"
            
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col1:
                st.markdown(f'<div class="{task_class}"><span>{priority_emoji} {task["title"]}</span></div>', unsafe_allow_html=True)
            with col2:
                if st.button("✅" if not task["done"] else "🔄", key=f"toggle_{idx}"):
                    st.session_state.tasks[idx]["done"] = not st.session_state.tasks[idx]["done"]
                    st.rerun()
            with col3:
                st.write(f"<small>{task['date']}</small>", unsafe_allow_html=True)
            with col4:
                if st.button("🗑️", key=f"delete_{idx}"):
                    del st.session_state.tasks[idx]
                    st.rerun()
    else:
        st.info("هیچ ئەرکێک تۆمار نەکراوە")
    
    st.markdown('</div>', unsafe_allow_html=True)

def calendar_page():
    st.markdown("""
    <div class="custom-card">
        <h2 class="card-title">📅 ڕۆژمێری پرۆژەکان</h2>
        <p class="rtl" style="color: #666;">ڕووداوەکان و دیدارەکانی ئەم مانگە</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Calendar display
    current_date = datetime.now()
    st.markdown(f"""
    <div class="custom-card" style="text-align: center;">
        <h3 class="rtl" style="color: #302b63;">{current_date.strftime('%B %Y')}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Sample events
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="custom-card">
            <h4 class="card-title">📌 ڕووداوەکانی ئەم هەفتەیە</h4>
            <div class="task-item">
                <span>📅 دیداری تیم - دووشەممە</span>
                <small>10:00 AM</small>
            </div>
            <div class="task-item">
                <span>🎯 وادەی کۆتایی پرۆژە - چوارشەممە</span>
                <small>5:00 PM</small>
            </div>
            <div class="task-item">
                <span>👥 کۆبوونەوەی گشتی - پێنجشەممە</span>
                <small>2:00 PM</small>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="custom-card">
            <h4 class="card-title">🔔 یادخستنەوەکان</h4>
            <div class="task-item" style="border-right: 4px solid #ff4757;">
                <span>⏰ ناردنی ڕاپۆرت - سبەینێ</span>
            </div>
            <div class="task-item" style="border-right: 4px solid #ffa502;">
                <span>📞 پەیوەندی بە کڕیار - ٢ ڕۆژی تر</span>
            </div>
            <div class="task-item" style="border-right: 4px solid #2ed573;">
                <span>🎉 یادی دامەزراندنی کۆمپانیا - ٥ ڕۆژی تر</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

def stats_page():
    st.markdown("""
    <div class="custom-card">
        <h2 class="card-title">📊 ئامارەکان و ڕاپۆرتەکان</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Progress overview
    st.markdown("""
    <div class="custom-card">
        <h4 class="card-title">📈 پێشکەوتنی گشتی</h4>
        <div class="progress-container">
            <div class="progress-fill" style="width: 75%;"></div>
        </div>
        <p class="rtl" style="color: #666;">٧٥٪ ی پرۆژەکان لە کاتی خۆیدا پێشکەوتوون</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Sample bar chart
        fig = go.Figure(data=[
            go.Bar(name='تەواوکراو', x=['هەفتەی ١', 'هەفتەی ٢', 'هەفتەی ٣', 'هەفتەی ٤'], 
                   y=[10, 15, 13, 17], marker_color='#667eea'),
            go.Bar(name='لەکاردا', x=['هەفتەی ١', 'هەفتەی ٢', 'هەفتەی ٣', 'هەفتەی ٤'], 
                   y=[5, 8, 6, 4], marker_color='#764ba2')
        ])
        fig.update_layout(
            title="ڕاپۆرتی هەفتانە",
            barmode='group',
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family='Noto Naskh Arabic')
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Sample pie chart
        labels = ['تەواوکراو', 'لەکاردا', 'دواکەوتوو', 'هەڵوەشاوە']
        values = [45, 30, 15, 10]
        colors = ['#2ed573', '#ffa502', '#ff4757', '#747d8c']
        
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, marker=dict(colors=colors))])
        fig.update_layout(
            title="دۆخی پرۆژەکان",
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family='Noto Naskh Arabic')
        )
        st.plotly_chart(fig, use_container_width=True)

def notes_page():
    st.markdown("""
    <div class="custom-card">
        <h2 class="card-title">📝 تێبینیەکان</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Add note
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    
    note_title = st.text_input("ناونیشانی تێبینی", placeholder="ناونیشانی تێبینیەکەت...", key="note_title")
    note_content = st.text_area("ناوەرۆک", placeholder="ناوەرۆکی تێبینیەکەت لێرە بنووسە...", height=150, key="note_content")
    
    if st.button("💾 پاشەکەوتکردنی تێبینی"):
        if note_title and note_content:
            st.session_state.notes.append({
                "title": note_title,
                "content": note_content,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            st.success("تێبینیەکەت پاشەکەوت کرا!")
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Show notes
    if st.session_state.notes:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown('<h3 class="card-title">📌 تێبینیە پاشەکەوتکراوەکان</h3>', unsafe_allow_html=True)
        
        for idx, note in enumerate(st.session_state.notes):
            st.markdown(f"""
            <div class="task-item" style="flex-direction: column; align-items: flex-start;">
                <h4 style="color: #302b63;">📌 {note['title']}</h4>
                <p style="color: #666;">{note['content']}</p>
                <small style="color: #999;">{note['date']}</small>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("🗑️ پاککردنەوەی هەموو تێبینیەکان"):
            st.session_state.notes = []
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

def settings_page():
    st.markdown("""
    <div class="custom-card">
        <h2 class="card-title">⚙️ ڕێکخستنەکان</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    
    # Profile settings
    st.markdown('<h4 class="card-title">👤 ڕێکخستنەکانی پڕۆفایل</h4>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("ناو", value="بەکارهێنەر", key="name")
        st.text_input("ئیمەیڵ", value="user@example.com", key="email")
    with col2:
        st.selectbox("زمان", ["کوردی", "عەرەبی", "ئینگلیزی"], key="language")
        st.selectbox("ناوچەی کاتی", ["Asia/Baghdad", "Asia/Tehran", "Europe/London"], key="timezone")
    
    st.markdown('<hr>', unsafe_allow_html=True)
    
    # Notification settings
    st.markdown('<h4 class="card-title">🔔 ڕێکخستنەکانی ئاگادارکردنەوە</h4>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.toggle("ئاگادارکردنەوەی ئیمەیڵ", value=True, key="email_notif")
    with col2:
        st.toggle("ئاگادارکردنەوەی پۆش", value=False, key="push_notif")
    with col3:
        st.toggle("دەنگی ئاگادارکردنەوە", value=True, key="sound_notif")
    
    st.markdown('<hr>', unsafe_allow_html=True)
    
    # Display settings
    st.markdown('<h4 class="card-title">🎨 ڕێکخستنەکانی ڕووکار</h4>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.select_slider("قەبارەی فۆنت", options=["بچووک", "مامناوەند", "گەورە", "زۆر گەورە"], key="font_size")
    with col2:
        st.color_picker("ڕەنگی سەرەکی", "#667eea", key="primary_color")
    
    st.markdown('<hr>', unsafe_allow_html=True)
    
    if st.button("💾 پاشەکەوتکردنی هەموو ڕێکخستنەکان"):
        st.success("ڕێکخستنەکانت بە سەرکەوتوویی پاشەکەوت کرا! 🎉")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Run the app
if __name__ == "__main__":
    main()
