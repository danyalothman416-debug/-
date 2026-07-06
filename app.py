# app.py - نسخەی کوردی و دیزاینی پێشکەوتوو
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import hashlib
import json
import base64
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import os
import random
from PIL import Image
import time
import shutil

# ڕێکخستنی لاپەڕە
st.set_page_config(
    page_title="دکتر دانیال - خوێندنی پزیشکی",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSSی پێشکەوتوو بۆ دیزاینی شووشەیی و ئەنیمەیشن
def load_css():
    dark_mode = st.session_state.get('dark_mode', True)
    
    if dark_mode:
        bg_gradient = "linear-gradient(135deg, #0f0c29, #302b63, #24243e)"
        card_bg = "rgba(255,255,255,0.08)"
        text_color = "#ffffff"
        border_color = "rgba(255,255,255,0.15)"
        shadow_color = "rgba(31, 38, 135, 0.5)"
    else:
        bg_gradient = "linear-gradient(135deg, #f5f7fa, #c3cfe2)"
        card_bg = "rgba(255,255,255,0.75)"
        text_color = "#1a1a2e"
        border_color = "rgba(0,0,0,0.1)"
        shadow_color = "rgba(31, 38, 135, 0.2)"
    
    st.markdown(f"""
    <style>
        /* ڕاستەوخۆی بنەڕەت */
        .stApp {{
            background: {bg_gradient};
            color: {text_color};
            min-height: 100vh;
        }}
        
        /* ئەنیمەیشنی بارکردن */
        @keyframes shimmer {{
            0% {{ background-position: -200% 0; }}
            100% {{ background-position: 200% 0; }}
        }}
        
        .skeleton {{
            background: linear-gradient(90deg, {card_bg} 25%, rgba(255,255,255,0.2) 50%, {card_bg} 75%);
            background-size: 200% 100%;
            animation: shimmer 1.5s infinite;
            border-radius: 10px;
            height: 100px;
            margin: 10px 0;
        }}
        
        /* کارتەکانی شووشەیی */
        .glass-card {{
            background: {card_bg};
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-radius: 25px;
            border: 1px solid {border_color};
            padding: 25px;
            margin: 12px 0;
            box-shadow: 0 8px 32px 0 {shadow_color};
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            animation: fadeInUp 0.6s ease-out;
            position: relative;
            overflow: hidden;
        }}
        
        .glass-card::before {{
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            opacity: 0;
            transition: opacity 0.4s;
        }}
        
        .glass-card:hover::before {{
            opacity: 1;
        }}
        
        .glass-card:hover {{
            transform: translateY(-8px) scale(1.01);
            box-shadow: 0 15px 45px 0 {shadow_color};
            border-color: rgba(102, 126, 234, 0.5);
        }}
        
        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        @keyframes float {{
            0%, 100% {{ transform: translateY(0px); }}
            50% {{ transform: translateY(-10px); }}
        }}
        
        /* سایدباری ئەنیمەیشن */
        .css-1d391kg {{
            background: {card_bg};
            backdrop-filter: blur(20px);
            border-right: 1px solid {border_color};
            animation: slideInLeft 0.5s ease-out;
        }}
        
        @keyframes slideInLeft {{
            from {{
                opacity: 0;
                transform: translateX(-50px);
            }}
            to {{
                opacity: 1;
                transform: translateX(0);
            }}
        }}
        
        /* سەرنووسە سەرەکی */
        .main-header {{
            text-align: center;
            padding: 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 25px;
            color: white;
            margin-bottom: 30px;
            animation: fadeInUp 0.8s ease-out;
            box-shadow: 0 10px 40px rgba(102, 126, 234, 0.4);
            position: relative;
            overflow: hidden;
        }}
        
        .main-header::after {{
            content: '❤️‍🩹';
            position: absolute;
            right: 20px;
            top: 20px;
            font-size: 40px;
            opacity: 0.3;
            animation: float 3s ease-in-out infinite;
        }}
        
        /* فلاشکارت */
        .flashcard {{
            background: linear-gradient(145deg, #667eea, #764ba2);
            border-radius: 30px;
            padding: 50px;
            margin: 20px 0;
            color: white;
            text-align: center;
            animation: float 3s ease-in-out infinite;
            cursor: pointer;
            box-shadow: 0 20px 60px rgba(102, 126, 234, 0.5);
            transition: all 0.3s;
            position: relative;
            overflow: hidden;
        }}
        
        .flashcard::before {{
            content: '📚';
            position: absolute;
            right: 30px;
            top: 30px;
            font-size: 60px;
            opacity: 0.2;
        }}
        
        .flashcard:hover {{
            transform: scale(1.02);
            box-shadow: 0 25px 70px rgba(102, 126, 234, 0.7);
        }}
        
        /* دکمەکان */
        .stButton > button {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 15px;
            padding: 12px 24px;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            width: 100%;
        }}
        
        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
            background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        }}
        
        /* ئایکۆنی دڵخواز */
        .favorite {{
            color: #FFD700;
            font-size: 28px;
            cursor: pointer;
            transition: all 0.3s;
            filter: drop-shadow(0 0 10px rgba(255, 215, 0, 0.3));
        }}
        
        .favorite:hover {{
            transform: scale(1.2) rotate(10deg);
        }}
        
        /* ئینپوتەکان */
        .stTextInput > div > div > input, 
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div {{
            background: {card_bg};
            border: 2px solid {border_color};
            border-radius: 15px;
            padding: 12px;
            color: {text_color};
            backdrop-filter: blur(10px);
        }}
        
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {{
            border-color: #667eea;
            box-shadow: 0 0 20px rgba(102, 126, 234, 0.3);
        }}
        
        /* تابیستەکان */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
            background: {card_bg};
            border-radius: 20px;
            padding: 8px;
            backdrop-filter: blur(10px);
        }}
        
        .stTabs [data-baseweb="tab"] {{
            border-radius: 15px;
            padding: 10px 20px;
            transition: all 0.3s;
        }}
        
        .stTabs [data-baseweb="tab"]:hover {{
            background: rgba(102, 126, 234, 0.2);
        }}
        
        .stTabs [aria-selected="true"] {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white !important;
        }}
        
        /* Loading animation */
        .loading-container {{
            display: flex;
            justify-content: center;
            align-items: center;
            height: 200px;
        }}
        
        .loader {{
            width: 60px;
            height: 60px;
            border: 5px solid {card_bg};
            border-top: 5px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        
        /* چاپ */
        @media print {{
            .stApp {{
                background: white !important;
            }}
            .glass-card {{
                background: white !important;
                border: 1px solid #ddd !important;
                box-shadow: none !important;
            }}
            .stButton, .stDownloadButton {{
                display: none !important;
            }}
        }}
        
        /* Responsive */
        @media (max-width: 768px) {{
            .glass-card {{
                padding: 15px;
                margin: 8px 0;
            }}
            .main-header {{
                padding: 20px;
                font-size: 20px;
            }}
            .flashcard {{
                padding: 30px;
            }}
        }}
        
        /* Scrollbar */
        ::-webkit-scrollbar {{
            width: 8px;
            background: {card_bg};
        }}
        ::-webkit-scrollbar-thumb {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            border-radius: 10px;
        }}
    </style>
    """, unsafe_allow_html=True)

# فەنکشنەکانی داتابەیس
def init_db():
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE,
                  password TEXT,
                  role TEXT,
                  created_at TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS medicines
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  brand TEXT,
                  generic TEXT,
                  dose TEXT,
                  route TEXT,
                  group_name TEXT,
                  notes TEXT,
                  favorite INTEGER DEFAULT 0,
                  created_at TEXT,
                  updated_at TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS lab_tests
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  purpose TEXT,
                  normal_range TEXT,
                  preparation TEXT,
                  notes TEXT,
                  favorite INTEGER DEFAULT 0,
                  created_at TEXT,
                  updated_at TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS general_notes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT,
                  content TEXT,
                  image_path TEXT,
                  link TEXT,
                  created_at TEXT)''')
    
    # زیادکردنی بەکارهێنەری بنەڕەت
    c.execute("SELECT * FROM users WHERE username='admin'")
    if not c.fetchone():
        hashed = hashlib.sha256('admin123'.encode()).hexdigest()
        c.execute("INSERT INTO users (username, password, role, created_at) VALUES (?, ?, ?, ?)",
                 ('admin', hashed, 'admin', datetime.now().isoformat()))
    
    conn.commit()
    conn.close()

# فەنکشنەکانی پشتگیریکردن
def auto_backup():
    """پشتگیری خۆکاری داتابەیس"""
    try:
        if os.path.exists('medical_data.db'):
            backup_dir = 'backups'
            os.makedirs(backup_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f'{backup_dir}/backup_{timestamp}.db'
            shutil.copy2('medical_data.db', backup_path)
            
            # تەنها ٥ پشتگیری دوایی بهێڵە
            backups = sorted([f for f in os.listdir(backup_dir) if f.endswith('.db')])
            if len(backups) > 5:
                for old_backup in backups[:-5]:
                    os.remove(os.path.join(backup_dir, old_backup))
    except:
        pass

# چاودێریکردن
def check_login(username, password):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    hashed = hashlib.sha256(password.encode()).hexdigest()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed))
    user = c.fetchone()
    conn.close()
    return user

def add_user(username, password, role='user'):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    hashed = hashlib.sha256(password.encode()).hexdigest()
    try:
        c.execute("INSERT INTO users (username, password, role, created_at) VALUES (?, ?, ?, ?)",
                 (username, hashed, role, datetime.now().isoformat()))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

# فەنکشنەکانی دەرمان
def add_medicine(name, brand, generic, dose, route, group_name, notes):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute("""INSERT INTO medicines 
                 (name, brand, generic, dose, route, group_name, notes, created_at, updated_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
              (name, brand, generic, dose, route, group_name, notes, now, now))
    conn.commit()
    conn.close()
    auto_backup()

def get_medicines(search=None, group=None):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    query = "SELECT * FROM medicines"
    params = []
    conditions = []
    
    if search:
        conditions.append("(name LIKE ? OR brand LIKE ? OR generic LIKE ?)")
        params.extend([f'%{search}%', f'%{search}%', f'%{search}%'])
    
    if group:
        conditions.append("group_name = ?")
        params.append(group)
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY favorite DESC, name ASC"
    
    c.execute(query, params)
    data = c.fetchall()
    conn.close()
    return data

def update_medicine(id, name, brand, generic, dose, route, group_name, notes):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute("""UPDATE medicines 
                 SET name=?, brand=?, generic=?, dose=?, route=?, 
                     group_name=?, notes=?, updated_at=?
                 WHERE id=?""",
              (name, brand, generic, dose, route, group_name, notes, now, id))
    conn.commit()
    conn.close()
    auto_backup()

def delete_medicine(id):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("DELETE FROM medicines WHERE id=?", (id,))
    conn.commit()
    conn.close()
    auto_backup()

def toggle_favorite_medicine(id):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("SELECT favorite FROM medicines WHERE id=?", (id,))
    current = c.fetchone()[0]
    new_val = 0 if current else 1
    c.execute("UPDATE medicines SET favorite=? WHERE id=?", (new_val, id))
    conn.commit()
    conn.close()

# فەنکشنەکانی پشکنین
def add_lab_test(name, purpose, normal_range, preparation, notes):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute("""INSERT INTO lab_tests 
                 (name, purpose, normal_range, preparation, notes, created_at, updated_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?)""",
              (name, purpose, normal_range, preparation, notes, now, now))
    conn.commit()
    conn.close()
    auto_backup()

def get_lab_tests(search=None):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    query = "SELECT * FROM lab_tests"
    params = []
    
    if search:
        query += " WHERE name LIKE ? OR purpose LIKE ?"
        params.extend([f'%{search}%', f'%{search}%'])
    
    query += " ORDER BY favorite DESC, name ASC"
    
    c.execute(query, params)
    data = c.fetchall()
    conn.close()
    return data

def update_lab_test(id, name, purpose, normal_range, preparation, notes):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute("""UPDATE lab_tests 
                 SET name=?, purpose=?, normal_range=?, preparation=?, notes=?, updated_at=?
                 WHERE id=?""",
              (name, purpose, normal_range, preparation, notes, now, id))
    conn.commit()
    conn.close()
    auto_backup()

def delete_lab_test(id):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("DELETE FROM lab_tests WHERE id=?", (id,))
    conn.commit()
    conn.close()
    auto_backup()

def toggle_favorite_lab_test(id):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("SELECT favorite FROM lab_tests WHERE id=?", (id,))
    current = c.fetchone()[0]
    new_val = 0 if current else 1
    c.execute("UPDATE lab_tests SET favorite=? WHERE id=?", (new_val, id))
    conn.commit()
    conn.close()

# تێبینییە گشتییەکان
def add_general_note(title, content, image_path=None, link=None):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute("""INSERT INTO general_notes (title, content, image_path, link, created_at)
                 VALUES (?, ?, ?, ?, ?)""",
              (title, content, image_path, link, now))
    conn.commit()
    conn.close()
    auto_backup()

def get_general_notes():
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("SELECT * FROM general_notes ORDER BY created_at DESC")
    data = c.fetchall()
    conn.close()
    return data

def delete_general_note(id):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("DELETE FROM general_notes WHERE id=?", (id,))
    conn.commit()
    conn.close()
    auto_backup()

# خوێندن - فلاشکارت
def get_random_study_item():
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    
    c.execute("SELECT 'medicine' as type, id, name, brand, generic, dose, route, group_name, notes FROM medicines")
    medicines = c.fetchall()
    
    c.execute("SELECT 'lab_test' as type, id, name, purpose, normal_range, preparation, notes FROM lab_tests")
    lab_tests = c.fetchall()
    
    conn.close()
    
    all_items = list(medicines) + list(lab_tests)
    if all_items:
        return random.choice(all_items)
    return None

# هەناردەکردن
def export_to_pdf(data, title):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#667eea'),
        alignment=1
    )
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 20))
    
    if data:
        headers = list(data[0].keys())
        table_data = [headers]
        for row in data:
            table_data.append([str(row.get(h, '')) for h in headers])
        
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# لاپەڕەی سەرەکی
def main():
    init_db()
    load_css()
    
    # ڕێکخستنی session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = ''
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = True
    if 'current_page' not in st.session_state:
        st.session_state.current_page = '📊 داشبۆرد'
    if 'loading' not in st.session_state:
        st.session_state.loading = False
    
    # پشتگیری خۆکار
    auto_backup()
    
    # لاپەڕەی چوونەژوورەوە
    if not st.session_state.logged_in:
        st.markdown("""
        <div class="main-header">
            <h1>🏥 دکتر دانیال</h1>
            <p>پلاتفۆرمی خوێندن و سەرچاوەی پزیشکی</p>
            <p style="font-size: 14px; opacity: 0.8;">❤️ بۆ خوێندکارانی پزیشکی و تەندروستی</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.container():
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.subheader("🔐 چوونەژوورەوە")
                
                username = st.text_input("ناوی بەکارهێنەر", placeholder="ناوی بەکارهێنەرێت بنووسە")
                password = st.text_input("ووشەی نهێنی", type="password", placeholder="ووشەی نهێنی بنووسە")
                
                if st.button("🔓 چوونەژوورەوە", use_container_width=True):
                    with st.spinner('تکایە چاوەڕوان بە...'):
                        time.sleep(0.5)
                        user = check_login(username, password)
                        if user:
                            st.session_state.logged_in = True
                            st.session_state.username = username
                            st.session_state.user_id = user[0]
                            st.session_state.user_role = user[3]
                            st.rerun()
                        else:
                            st.error("❌ ناوی بەکارهێنەر یان ووشەی نهێنی هەڵەیە!")
                
                st.markdown("---")
                st.caption("👤 بەکارهێنەری بنەڕەت: admin / admin123")
                st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # ئەپە سەرەکی
    st.markdown(f"""
    <div class="main-header">
        <h1>🏥 دکتر دانیال</h1>
        <p>❤️ بەخێربێیت، {st.session_state.username}!</p>
        <p style="font-size: 14px; opacity: 0.8;">📅 {datetime.now().strftime('%A, %B %d, %Y')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # سایدبار
    with st.sidebar:
        st.markdown("### 📚 ڕێبەرایەتی")
        
        pages = [
            "📊 داشبۆرد",
            "💊 دەرمانەکان",
            "🧪 پشکنینەکان",
            "📝 تێبینییەکان",
            "🎯 شێوازی خوێندن"
        ]
        
        if st.session_state.get('user_role') == 'admin':
            pages.append("👥 بەکارهێنەران")
        pages.append("⚙️ ڕێکخستنەکان")
        
        for page in pages:
            if st.button(page, use_container_width=True):
                st.session_state.current_page = page
                st.rerun()
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🖨️ چاپ", use_container_width=True):
                st.write("""
                <script>
                window.print();
                </script>
                """, unsafe_allow_html=True)
        with col2:
            if st.button("🚪 دەرچوون", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.username = ''
                st.rerun()
    
    # ناوەرۆکی لاپەڕە
    page = st.session_state.current_page
    
    if page == "📊 داشبۆرد":
        show_dashboard()
    elif page == "💊 دەرمانەکان":
        show_medicines()
    elif page == "🧪 پشکنینەکان":
        show_lab_tests()
    elif page == "📝 تێبینییەکان":
        show_notes()
    elif page == "🎯 شێوازی خوێندن":
        show_study_mode()
    elif page == "👥 بەکارهێنەران" and st.session_state.get('user_role') == 'admin':
        show_users()
    elif page == "⚙️ ڕێکخستنەکان":
        show_settings()

def show_dashboard():
    st.markdown("### 📊 داشبۆرد")
    
    # ئامارەکان
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM medicines")
    total_meds = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM lab_tests")
    total_tests = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM medicines WHERE favorite=1")
    fav_meds = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM lab_tests WHERE favorite=1")
    fav_tests = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM general_notes")
    total_notes = c.fetchone()[0]
    
    conn.close()
    
    # کارتەکانی ئامار
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center;">
            <h2 style="font-size: 40px;">💊</h2>
            <h3>{total_meds}</h3>
            <p>دەرمانەکان</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center;">
            <h2 style="font-size: 40px;">🧪</h2>
            <h3>{total_tests}</h3>
            <p>پشکنینەکان</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center;">
            <h2 style="font-size: 40px;">⭐</h2>
            <h3>{fav_meds + fav_tests}</h3>
            <p>دڵخوازەکان</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center;">
            <h2 style="font-size: 40px;">📝</h2>
            <h3>{total_notes}</h3>
            <p>تێبینییەکان</p>
        </div>
        """, unsafe_allow_html=True)
    
    # چارتەکان
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📈 دابەشکردن")
        fig = go.Figure(data=[go.Pie(
            labels=['دەرمانەکان', 'پشکنینەکان'],
            values=[total_meds, total_tests],
            marker=dict(colors=['#667eea', '#764ba2']),
            hole=0.3
        )])
        fig.update_layout(showlegend=True, height=300, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("⭐ دڵخوازەکان")
        fig = go.Figure(data=[go.Bar(
            x=['دەرمانەکان', 'پشکنینەکان'],
            y=[fav_meds, fav_tests],
            marker_color=['#667eea', '#764ba2'],
            text=[fav_meds, fav_tests],
            textposition='auto'
        )])
        fig.update_layout(showlegend=False, height=300, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # بەشەکانی کۆتایی
    st.markdown("### 📋 چالاکییە کۆتاییەکان")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("💊 دەرمانە کۆتاییەکان")
        meds = get_medicines()[:5]
        for med in meds:
            st.write(f"• {med[1]} ({med[2]})")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("🧪 پشکنینە کۆتاییەکان")
        tests = get_lab_tests()[:5]
        for test in tests:
            st.write(f"• {test[1]}")
        st.markdown('</div>', unsafe_allow_html=True)

def show_medicines():
    st.markdown("### 💊 بەڕێوەبەری دەرمانەکان")
    
    tab1, tab2, tab3 = st.tabs(["📋 بینین", "➕ زیادکردن", "🔍 گەڕان"])
    
    with tab1:
        st.markdown("#### هەموو دەرمانەکان")
        
        meds = get_medicines()
        if meds:
            for med in meds:
                with st.container():
                    st.markdown(f"""
                    <div class="glass-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <h3>{"⭐ " if med[8] else ""}{med[1]}</h3>
                            <div>
                                <span style="background: linear-gradient(135deg, #667eea, #764ba2); padding: 5px 15px; border-radius: 20px; color: white; font-size: 12px;">{med[6]}</span>
                            </div>
                        </div>
                        <p><strong>🏷️ براند:</strong> {med[2]} | <strong>🔬 گەنەریک:</strong> {med[3]}</p>
                        <p><strong>💊 دۆز:</strong> {med[4]} | <strong>🔄 ڕێگا:</strong> {med[5]}</p>
                        <p><strong>📝 تێبینی:</strong> {med[7]}</p>
                        <div style="display: flex; gap: 10px; margin-top: 10px;">
                    """, unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col1:
                        if st.button(f"⭐", key=f"fav_med_{med[0]}"):
                            toggle_favorite_medicine(med[0])
                            st.rerun()
                    with col2:
                        if st.button(f"✏️ دەستکاری", key=f"edit_med_{med[0]}"):
                            st.session_state.edit_med = med
                    with col3:
                        if st.button(f"🗑️ سڕینەوە", key=f"del_med_{med[0]}"):
                            delete_medicine(med[0])
                            st.rerun()
                    
                    st.markdown("</div></div>", unsafe_allow_html=True)
        else:
            st.info("📝 هیچ دەرمانێک نەدۆزرایەوە. دەرمانێک زیاد بکە!")
    
    with tab2:
        st.markdown("#### زیادکردنی دەرمانی نوێ")
        with st.form("add_medicine_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("ناوی دەرمان *")
                brand = st.text_input("براند")
                generic = st.text_input("گەنەریک")
                dose = st.text_input("دۆز")
            with col2:
                route = st.selectbox("ڕێگا", ["خواردنەوە", "IV", "IM", "ژێر پێست", "سەرپێست", "هەڵمکردن", "تر"])
                group = st.selectbox("گرووپ", ["دەردشکێن", "ئانتیبایۆتیک", "دەرمانی خەمۆکی", "دەرمانی فشاری خوێن", 
                                              "دەرمانی شەکەری خوێن", "دەرمانی هەستەوەری", "دەرمانی ترشەمێر", "ڤیتامینەکان", "تر"])
                notes = st.text_area("تێبینی")
            
            submitted = st.form_submit_button("💊 زیادکردنی دەرمان")
            if submitted and name:
                add_medicine(name, brand, generic, dose, route, group, notes)
                st.success("✅ دەرمان بە سەرکەوتوویی زیادکرا!")
                st.rerun()
    
    with tab3:
        st.markdown("#### گەڕانی دەرمانەکان")
        search_term = st.text_input("گەڕان بە ناو، براند، یان گەنەریک")
        if search_term:
            results = get_medicines(search=search_term)
            if results:
                for med in results:
                    st.markdown(f"""
                    <div class="glass-card">
                        <h4>{med[1]}</h4>
                        <p><strong>براند:</strong> {med[2]} | <strong>گەنەریک:</strong> {med[3]}</p>
                        <p><strong>دۆز:</strong> {med[4]} | <strong>ڕێگا:</strong> {med[5]}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("هیچ ئەنجامێک نەدۆزرایەوە!")

def show_lab_tests():
    st.markdown("### 🧪 بەڕێوەبەری پشکنینەکان")
    
    tab1, tab2, tab3 = st.tabs(["📋 بینین", "➕ زیادکردن", "🔍 گەڕان"])
    
    with tab1:
        st.markdown("#### هەموو پشکنینەکان")
        
        tests = get_lab_tests()
        if tests:
            for test in tests:
                with st.container():
                    st.markdown(f"""
                    <div class="glass-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <h3>{"⭐ " if test[6] else ""}{test[1]}</h3>
                        </div>
                        <p><strong>🎯 ئامانج:</strong> {test[2]}</p>
                        <p><strong>📊 نرخی ئاسایی:</strong> {test[3]}</p>
                        <p><strong>🧑‍⚕️ ئامادەبوونی نەخۆش:</strong> {test[4]}</p>
                        <p><strong>📝 تێبینی:</strong> {test[5]}</p>
                        <div style="display: flex; gap: 10px; margin-top: 10px;">
                    """, unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col1:
                        if st.button(f"⭐", key=f"fav_test_{test[0]}"):
                            toggle_favorite_lab_test(test[0])
                            st.rerun()
                    with col2:
                        if st.button(f"✏️ دەستکاری", key=f"edit_test_{test[0]}"):
                            st.session_state.edit_test = test
                    with col3:
                        if st.button(f"🗑️ سڕینەوە", key=f"del_test_{test[0]}"):
                            delete_lab_test(test[0])
                            st.rerun()
                    
                    st.markdown("</div></div>", unsafe_allow_html=True)
        else:
            st.info("📝 هیچ پشکنینێک نەدۆزرایەوە. پشکنینێک زیاد بکە!")
    
    with tab2:
        st.markdown("#### زیادکردنی پشکنینی نوێ")
        with st.form("add_test_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("ناوی پشکنین *")
                purpose = st.text_area("ئامانج")
                normal_range = st.text_input("نرخی ئاسایی")
            with col2:
                preparation = st.text_area("ئامادەبوونی نەخۆش")
                notes = st.text_area("تێبینی زیادە")
            
            submitted = st.form_submit_button("🧪 زیادکردنی پشکنین")
            if submitted and name:
                add_lab_test(name, purpose, normal_range, preparation, notes)
                st.success("✅ پشکنین بە سەرکەوتوویی زیادکرا!")
                st.rerun()
    
    with tab3:
        st.markdown("#### گەڕانی پشکنینەکان")
        search_term = st.text_input("گەڕان بە ناو یان ئامانج")
        if search_term:
            results = get_lab_tests(search=search_term)
            if results:
                for test in results:
                    st.markdown(f"""
                    <div class="glass-card">
                        <h4>{test[1]}</h4>
                        <p><strong>ئامانج:</strong> {test[2]}</p>
                        <p><strong>نرخی ئاسایی:</strong> {test[3]}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("هیچ ئەنجامێک نەدۆزرایەوە!")

def show_notes():
    st.markdown("### 📝 تێبینییە گشتییەکان")
    
    with st.expander("➕ زیادکردنی تێبینی نوێ"):
        with st.form("add_note_form"):
            title = st.text_input("ناونیشان *")
            content = st.text_area("ناوەرۆک")
            link = st.text_input("لینک (ئارەزوومەندانە)")
            uploaded_file = st.file_uploader("بارکردنی وێنە (ئارەزوومەندانە)", type=['png', 'jpg', 'jpeg'])
            
            submitted = st.form_submit_button("📝 پاشەکەوتکردنی تێبینی")
            if submitted and title:
                image_path = None
                if uploaded_file:
                    os.makedirs("images", exist_ok=True)
                    image_path = f"images/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uploaded_file.name}"
                    with open(image_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                
                add_general_note(title, content, image_path, link)
                st.success("✅ تێبینی بە سەرکەوتوویی زیادکرا!")
                st.rerun()
    
    notes = get_general_notes()
    if notes:
        for note in notes:
            st.markdown(f"""
            <div class="glass-card">
                <h4>{note[1]}</h4>
                <p>{note[2]}</p>
                {f'<p><strong>🔗 لینک:</strong> <a href="{note[4]}" target="_blank">{note[4]}</a></p>' if note[4] else ''}
                <p><small>📅 {note[5]}</small></p>
            </div>
            """, unsafe_allow_html=True)
            
            if note[3] and os.path.exists(note[3]):
                st.image(note[3], use_container_width=True)
            
            if st.button(f"🗑️ سڕینەوە", key=f"del_note_{note[0]}"):
                if note[3] and os.path.exists(note[3]):
                    os.remove(note[3])
                delete_general_note(note[0])
                st.rerun()
            
            st.markdown("---")
    else:
        st.info("📝 هیچ تێبینییەک نییە. تێبینییەک بنووسە!")

def show_study_mode():
    st.markdown("### 🎯 شێوازی خوێندن - پێداچوونەوەی فلاشکارت")
    
    item = get_random_study_item()
    
    if item:
        item_type = item[0]
        
        st.markdown("""
        <div style="text-align: center; margin: 20px 0;">
            <p style="font-size: 18px; opacity: 0.7;">👆 کرتە لەسەر کارت بکە بۆ گۆڕینی</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="flashcard">', unsafe_allow_html=True)
            
            if item_type == 'medicine':
                st.markdown(f"""
                <h2>💊 {item[2]}</h2>
                <hr>
                <p><strong>🏷️ براند:</strong> {item[3]}</p>
                <p><strong>🔬 گەنەریک:</strong> {item[4]}</p>
                <p><strong>💊 دۆز:</strong> {item[5]}</p>
                <p><strong>🔄 ڕێگا:</strong> {item[6]}</p>
                <p><strong>📂 گرووپ:</strong> {item[7]}</p>
                <p><strong>📝 تێبینی:</strong> {item[8]}</p>
                """, unsafe_allow_html=True)
                
                if st.button("⭐ زیادکردن بۆ دڵخوازەکان", key="flashcard_fav"):
                    toggle_favorite_medicine(item[1])
                    st.rerun()
            
            elif item_type == 'lab_test':
                st.markdown(f"""
                <h2>🧪 {item[2]}</h2>
                <hr>
                <p><strong>🎯 ئامانج:</strong> {item[3]}</p>
                <p><strong>📊 نرخی ئاسایی:</strong> {item[4]}</p>
                <p><strong>🧑‍⚕️ ئامادەبوونی نەخۆش:</strong> {item[5]}</p>
                <p><strong>📝 تێبینی:</strong> {item[6]}</p>
                """, unsafe_allow_html=True)
                
                if st.button("⭐ زیادکردن بۆ دڵخوازەکان", key="flashcard_fav"):
                    toggle_favorite_lab_test(item[1])
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("🔄 کارتی داهاتوو", use_container_width=True):
            st.rerun()
        
        st.markdown("""
        <div style="text-align: center; margin-top: 20px;">
            <p style="opacity: 0.7;">💡 هەر کارتێک بە جیا بخوێنە بۆ باشتری بیرهێنانەوە</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("📚 هیچ بابەتێک نییە بۆ خوێندن! یەکەم جار دەرمان یان پشکنین زیاد بکە.")

def show_users():
    if st.session_state.get('user_role') != 'admin':
        st.error("⛔ ڕێگەپێدراو نییە. تەنها بۆ بەڕێوەبەر.")
        return
    
    st.markdown("### 👥 بەڕێوەبەری بەکارهێنەران")
    
    with st.expander("➕ زیادکردنی بەکارهێنەری نوێ"):
        with st.form("add_user_form"):
            new_username = st.text_input("ناوی بەکارهێنەر *")
            new_password = st.text_input("ووشەی نهێنی *", type="password")
            role = st.selectbox("ڕۆڵ", ["user", "admin"])
            
            submitted = st.form_submit_button("👤 زیادکردنی بەکارهێنەر")
            if submitted and new_username and new_password:
                if add_user(new_username, new_password, role):
                    st.success("✅ بەکارهێنەر بە سەرکەوتوویی زیادکرا!")
                    st.rerun()
                else:
                    st.error("❌ ناوی بەکارهێنەر هەیە!")
    
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("SELECT id, username, role, created_at FROM users")
    users = c.fetchall()
    conn.close()
    
    st.markdown("#### بەکارهێنەرەکان")
    if users:
        for user in users:
            st.markdown(f"""
            <div class="glass-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4>👤 {user[1]}</h4>
                        <p><strong>ڕۆڵ:</strong> {user[2]} | <strong>بەستوو:</strong> {user[3]}</p>
                    </div>
                    {f'<span style="background: linear-gradient(135deg, #667eea, #764ba2); padding: 5px 15px; border-radius: 20px; color: white;">چالاک</span>' if user[0] != 1 else '<span style="background: #FFD700; padding: 5px 15px; border-radius: 20px; color: #1a1a2e;">بەڕێوەبەر</span>'}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("هیچ بەکارهێنەرێک نەدۆزرایەوە.")

def show_settings():
    st.markdown("### ⚙️ ڕێکخستنەکان")
    
    # ڕووکار
    st.markdown("#### ڕووکار")
    dark_mode = st.toggle("🌙 ڕەوانەی تاریک", value=st.session_state.get('dark_mode', True))
    if dark_mode != st.session_state.get('dark_mode'):
        st.session_state.dark_mode = dark_mode
        st.rerun()
    
    # پشتگیری
    st.markdown("#### پشتگیری")
    if st.button("💾 پشتگیری دەستکرد"):
        auto_backup()
        st.success("✅ پشتگیری بە سەرکەوتوویی دروستکرا!")
    
    # هەناردەکردن
    st.markdown("#### هەناردەکردن")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 PDF", use_container_width=True):
            medicines = get_medicines()
            med_data = [{"ناو": m[1], "براند": m[2], "گەنەریک": m[3], "دۆز": m[4], "ڕێگا": m[5], "تێبینی": m[7]} for m in medicines]
            pdf_buffer = export_to_pdf(med_data, "دکتر دانیال - داتاکان")
            st.download_button(
                label="📥 داگرتنی PDF",
                data=pdf_buffer,
                file_name=f"medical_data_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf"
            )
    
    with col2:
        medicines = get_medicines()
        if medicines:
            df = pd.DataFrame(medicines, columns=['ID', 'ناو', 'براند', 'گەنەریک', 'دۆز', 'ڕێگا', 'گرووپ', 'تێبینی', 'دڵخواز', 'دروستکراو', 'نوێکراوە'])
            csv = df.to_csv(index=False)
            st.download_button(
                label="📊 CSV",
                data=csv,
                file_name=f"medical_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with col3:
        medicines = get_medicines()
        if medicines:
            df = pd.DataFrame(medicines, columns=['ID', 'ناو', 'براند', 'گەنەریک', 'دۆز', 'ڕێگا', 'گرووپ', 'تێبینی', 'دڵخواز', 'دروستکراو', 'نوێکراوە'])
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='دەرمانەکان', index=False)
            st.download_button(
                label="📊 Excel",
                data=buffer,
                file_name=f"medical_data_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    # گەڕاندنەوەی پشتگیری
    st.markdown("#### گەڕاندنەوەی پشتگیری")
    uploaded_file = st.file_uploader("📤 گەڕاندنەوەی پشتگیری", type=['db'])
    if uploaded_file:
        with open('medical_data.db', 'wb') as f:
            f.write(uploaded_file.getbuffer())
        st.success("✅ پشتگیری گەڕێنرایەوە! تکایە ئەپەکە دووبارە بکەرەوە.")
        st.rerun()
    
    # دەربارە
    st.markdown("#### دەربارە")
    st.info("""
    **دکتر دانیال** 🏥
    
    پلاتفۆرمی خوێندنی پزیشکی بۆ خوێندکاران و پسپۆڕان.
    
    * 💊 دەرمانەکان
    * 🧪 پشکنینەکان
    * 📝 تێبینییەکان
    * 🎯 فلاشکارت
    
    **وەشانی 2.0** 
    **❤️ بە هەموو دڵێک بۆ خوێندکارانی پزیشکی**
    """)

if __name__ == "__main__":
    main()
