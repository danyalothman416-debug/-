# app.py
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

# Page config
st.set_page_config(
    page_title="Dr Danyal - Medical Study",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark mode and glassmorphism
def load_css():
    dark_mode = st.session_state.get('dark_mode', True)
    
    if dark_mode:
        bg_color = "#0f0f1a"
        card_bg = "rgba(255,255,255,0.05)"
        text_color = "#ffffff"
        border_color = "rgba(255,255,255,0.1)"
    else:
        bg_color = "#f5f5f5"
        card_bg = "rgba(255,255,255,0.8)"
        text_color = "#000000"
        border_color = "rgba(0,0,0,0.1)"
    
    st.markdown(f"""
    <style>
        /* Main container */
        .stApp {{
            background: {bg_color};
            color: {text_color};
        }}
        
        /* Glassmorphism cards */
        .glass-card {{
            background: {card_bg};
            backdrop-filter: blur(10px);
            border-radius: 20px;
            border: 1px solid {border_color};
            padding: 20px;
            margin: 10px 0;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            transition: all 0.3s ease;
        }}
        
        .glass-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.5);
        }}
        
        /* Headers */
        .main-header {{
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            color: white;
            margin-bottom: 30px;
        }}
        
        /* Flashcard animation */
        .flashcard {{
            background: linear-gradient(145deg, #667eea, #764ba2);
            border-radius: 30px;
            padding: 40px;
            margin: 20px 0;
            color: white;
            text-align: center;
            animation: pulse 2s infinite;
            cursor: pointer;
        }}
        
        @keyframes pulse {{
            0% {{ transform: scale(1); }}
            50% {{ transform: scale(1.02); }}
            100% {{ transform: scale(1); }}
        }}
        
        /* Favorite star */
        .favorite {{
            color: #FFD700;
            font-size: 24px;
            cursor: pointer;
        }}
        
        /* Sidebar */
        .css-1d391kg {{
            background: {card_bg};
            backdrop-filter: blur(10px);
        }}
    </style>
    """, unsafe_allow_html=True)

# Database functions
def init_db():
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE,
                  password TEXT,
                  role TEXT,
                  created_at TEXT)''')
    
    # Medicines table
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
    
    # Lab tests table
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
    
    # General notes table
    c.execute('''CREATE TABLE IF NOT EXISTS general_notes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT,
                  content TEXT,
                  image_path TEXT,
                  link TEXT,
                  created_at TEXT)''')
    
    # Insert default admin if not exists
    c.execute("SELECT * FROM users WHERE username='admin'")
    if not c.fetchone():
        hashed = hashlib.sha256('admin123'.encode()).hexdigest()
        c.execute("INSERT INTO users (username, password, role, created_at) VALUES (?, ?, ?, ?)",
                 ('admin', hashed, 'admin', datetime.now().isoformat()))
    
    conn.commit()
    conn.close()

# Authentication functions
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

# CRUD for medicines
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

def delete_medicine(id):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("DELETE FROM medicines WHERE id=?", (id,))
    conn.commit()
    conn.close()

def toggle_favorite_medicine(id):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("SELECT favorite FROM medicines WHERE id=?", (id,))
    current = c.fetchone()[0]
    new_val = 0 if current else 1
    c.execute("UPDATE medicines SET favorite=? WHERE id=?", (new_val, id))
    conn.commit()
    conn.close()

# CRUD for lab tests
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

def delete_lab_test(id):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("DELETE FROM lab_tests WHERE id=?", (id,))
    conn.commit()
    conn.close()

def toggle_favorite_lab_test(id):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("SELECT favorite FROM lab_tests WHERE id=?", (id,))
    current = c.fetchone()[0]
    new_val = 0 if current else 1
    c.execute("UPDATE lab_tests SET favorite=? WHERE id=?", (new_val, id))
    conn.commit()
    conn.close()

# General notes
def add_general_note(title, content, image_path=None, link=None):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute("""INSERT INTO general_notes (title, content, image_path, link, created_at)
                 VALUES (?, ?, ?, ?, ?)""",
              (title, content, image_path, link, now))
    conn.commit()
    conn.close()

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

# Study mode - get random item for flashcard
def get_random_study_item():
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    
    # Get random medicine
    c.execute("SELECT 'medicine' as type, id, name, brand, generic, dose, route, group_name, notes FROM medicines")
    medicines = c.fetchall()
    
    # Get random lab test
    c.execute("SELECT 'lab_test' as type, id, name, purpose, normal_range, preparation, notes FROM lab_tests")
    lab_tests = c.fetchall()
    
    conn.close()
    
    all_items = list(medicines) + list(lab_tests)
    if all_items:
        return random.choice(all_items)
    return None

# Export functions
def export_to_pdf(data, title):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#667eea'),
        alignment=1
    )
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 20))
    
    # Table
    if data:
        headers = list(data[0].keys())
        table_data = [headers]
        for row in data:
            table_data.append([str(row.get(h, '')) for h in headers])
        
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
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

# Main app
def main():
    # Initialize database
    init_db()
    
    # Load CSS
    load_css()
    
    # Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = ''
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = True
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'Dashboard'
    
    # Login page
    if not st.session_state.logged_in:
        st.markdown("""
        <div class="main-header">
            <h1>🏥 Dr Danyal</h1>
            <p>Medical Study & Reference Platform</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.container():
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.subheader("🔐 Login")
                
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                
                if st.button("Login", use_container_width=True):
                    user = check_login(username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.user_id = user[0]
                        st.session_state.user_role = user[3]
                        st.rerun()
                    else:
                        st.error("Invalid username or password!")
                
                st.markdown("---")
                st.caption("Default admin: admin / admin123")
                st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Main app
    st.markdown(f"""
    <div class="main-header">
        <h1>🏥 Dr Danyal</h1>
        <p>Welcome, {st.session_state.username}! 👋</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("### 📚 Navigation")
        
        pages = ["📊 Dashboard", "💊 Medicines", "🧪 Lab Tests", "📝 Notes", "🎯 Study Mode"]
        if st.session_state.get('user_role') == 'admin':
            pages.append("👥 Users")
        pages.append("⚙️ Settings")
        
        for page in pages:
            if st.button(page, use_container_width=True):
                st.session_state.current_page = page
                st.rerun()
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ''
            st.rerun()
    
    # Page content
    page = st.session_state.current_page
    
    if page == "📊 Dashboard":
        show_dashboard()
    elif page == "💊 Medicines":
        show_medicines()
    elif page == "🧪 Lab Tests":
        show_lab_tests()
    elif page == "📝 Notes":
        show_notes()
    elif page == "🎯 Study Mode":
        show_study_mode()
    elif page == "👥 Users" and st.session_state.get('user_role') == 'admin':
        show_users()
    elif page == "⚙️ Settings":
        show_settings()

def show_dashboard():
    st.markdown("### 📊 Dashboard")
    
    # Statistics
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
    
    conn.close()
    
    # Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center;">
            <h2>💊</h2>
            <h3>{total_meds}</h3>
            <p>Medicines</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center;">
            <h2>🧪</h2>
            <h3>{total_tests}</h3>
            <p>Lab Tests</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center;">
            <h2>⭐</h2>
            <h3>{fav_meds + fav_tests}</h3>
            <p>Favorites</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center;">
            <h2>📚</h2>
            <h3>{total_meds + total_tests}</h3>
            <p>Total Items</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📈 Distribution")
        fig = go.Figure(data=[go.Pie(labels=['Medicines', 'Lab Tests'], 
                                     values=[total_meds, total_tests],
                                     marker=dict(colors=['#667eea', '#764ba2']))])
        fig.update_layout(showlegend=True, height=300)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("⭐ Favorites")
        fig = go.Figure(data=[go.Bar(x=['Medicines', 'Lab Tests'], 
                                     y=[fav_meds, fav_tests],
                                     marker_color=['#667eea', '#764ba2'])])
        fig.update_layout(showlegend=False, height=300)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Recent items
    st.markdown("### 📋 Recent Activity")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("💊 Recent Medicines")
        meds = get_medicines()[:5]
        for med in meds:
            st.write(f"• {med[1]} ({med[2]})")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("🧪 Recent Lab Tests")
        tests = get_lab_tests()[:5]
        for test in tests:
            st.write(f"• {test[1]}")
        st.markdown('</div>', unsafe_allow_html=True)

def show_medicines():
    st.markdown("### 💊 Medicines Management")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📋 View", "➕ Add", "🔍 Search"])
    
    with tab1:
        st.markdown("#### All Medicines")
        
        meds = get_medicines()
        if meds:
            for med in meds:
                with st.container():
                    st.markdown(f"""
                    <div class="glass-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <h3>{"⭐ " if med[8] else ""}{med[1]}</h3>
                            <div>
                                <span style="background: #667eea; padding: 5px 10px; border-radius: 10px; color: white;">{med[6]}</span>
                            </div>
                        </div>
                        <p><strong>Brand:</strong> {med[2]} | <strong>Generic:</strong> {med[3]}</p>
                        <p><strong>Dose:</strong> {med[4]} | <strong>Route:</strong> {med[5]}</p>
                        <p><strong>Notes:</strong> {med[7]}</p>
                        <div style="display: flex; gap: 10px; margin-top: 10px;">
                    """, unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col1:
                        if st.button(f"⭐", key=f"fav_med_{med[0]}"):
                            toggle_favorite_medicine(med[0])
                            st.rerun()
                    with col2:
                        if st.button(f"✏️ Edit", key=f"edit_med_{med[0]}"):
                            st.session_state.edit_med = med
                    with col3:
                        if st.button(f"🗑️ Delete", key=f"del_med_{med[0]}"):
                            delete_medicine(med[0])
                            st.rerun()
                    
                    st.markdown("</div></div>", unsafe_allow_html=True)
        else:
            st.info("No medicines found. Add some! 📝")
    
    with tab2:
        st.markdown("#### Add New Medicine")
        with st.form("add_medicine_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Medicine Name *")
                brand = st.text_input("Brand Name")
                generic = st.text_input("Generic Name")
                dose = st.text_input("Dose")
            with col2:
                route = st.selectbox("Route", ["Oral", "IV", "IM", "SC", "Topical", "Inhalation", "Other"])
                group = st.selectbox("Group", ["Analgesics", "Antibiotics", "Antidepressants", "Antihypertensives", 
                                              "Antidiabetics", "Antihistamines", "Antacids", "Vitamins", "Other"])
                notes = st.text_area("Notes")
            
            submitted = st.form_submit_button("💊 Add Medicine")
            if submitted and name:
                add_medicine(name, brand, generic, dose, route, group, notes)
                st.success("✅ Medicine added successfully!")
                st.rerun()
    
    with tab3:
        st.markdown("#### Search Medicines")
        search_term = st.text_input("Search by name, brand, or generic")
        if search_term:
            results = get_medicines(search=search_term)
            if results:
                for med in results:
                    st.markdown(f"""
                    <div class="glass-card">
                        <h4>{med[1]}</h4>
                        <p><strong>Brand:</strong> {med[2]} | <strong>Generic:</strong> {med[3]}</p>
                        <p><strong>Dose:</strong> {med[4]} | <strong>Route:</strong> {med[5]}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("No results found!")

def show_lab_tests():
    st.markdown("### 🧪 Lab Tests Management")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📋 View", "➕ Add", "🔍 Search"])
    
    with tab1:
        st.markdown("#### All Lab Tests")
        
        tests = get_lab_tests()
        if tests:
            for test in tests:
                with st.container():
                    st.markdown(f"""
                    <div class="glass-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <h3>{"⭐ " if test[6] else ""}{test[1]}</h3>
                        </div>
                        <p><strong>Purpose:</strong> {test[2]}</p>
                        <p><strong>Normal Range:</strong> {test[3]}</p>
                        <p><strong>Preparation:</strong> {test[4]}</p>
                        <p><strong>Notes:</strong> {test[5]}</p>
                        <div style="display: flex; gap: 10px; margin-top: 10px;">
                    """, unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col1:
                        if st.button(f"⭐", key=f"fav_test_{test[0]}"):
                            toggle_favorite_lab_test(test[0])
                            st.rerun()
                    with col2:
                        if st.button(f"✏️ Edit", key=f"edit_test_{test[0]}"):
                            st.session_state.edit_test = test
                    with col3:
                        if st.button(f"🗑️ Delete", key=f"del_test_{test[0]}"):
                            delete_lab_test(test[0])
                            st.rerun()
                    
                    st.markdown("</div></div>", unsafe_allow_html=True)
        else:
            st.info("No lab tests found. Add some! 📝")
    
    with tab2:
        st.markdown("#### Add New Lab Test")
        with st.form("add_test_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Test Name *")
                purpose = st.text_area("Purpose")
                normal_range = st.text_input("Normal Range")
            with col2:
                preparation = st.text_area("Patient Preparation")
                notes = st.text_area("Additional Notes")
            
            submitted = st.form_submit_button("🧪 Add Lab Test")
            if submitted and name:
                add_lab_test(name, purpose, normal_range, preparation, notes)
                st.success("✅ Lab test added successfully!")
                st.rerun()
    
    with tab3:
        st.markdown("#### Search Lab Tests")
        search_term = st.text_input("Search by name or purpose")
        if search_term:
            results = get_lab_tests(search=search_term)
            if results:
                for test in results:
                    st.markdown(f"""
                    <div class="glass-card">
                        <h4>{test[1]}</h4>
                        <p><strong>Purpose:</strong> {test[2]}</p>
                        <p><strong>Normal Range:</strong> {test[3]}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("No results found!")

def show_notes():
    st.markdown("### 📝 General Notes")
    
    # Add note
    with st.expander("➕ Add New Note"):
        with st.form("add_note_form"):
            title = st.text_input("Title *")
            content = st.text_area("Content")
            link = st.text_input("Link (optional)")
            uploaded_file = st.file_uploader("Upload Image (optional)", type=['png', 'jpg', 'jpeg'])
            
            submitted = st.form_submit_button("📝 Save Note")
            if submitted and title:
                # Save image if uploaded
                image_path = None
                if uploaded_file:
                    # Save to images folder
                    os.makedirs("images", exist_ok=True)
                    image_path = f"images/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uploaded_file.name}"
                    with open(image_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                
                add_general_note(title, content, image_path, link)
                st.success("✅ Note added successfully!")
                st.rerun()
    
    # Display notes
    notes = get_general_notes()
    if notes:
        for note in notes:
            st.markdown(f"""
            <div class="glass-card">
                <h4>{note[1]}</h4>
                <p>{note[2]}</p>
                {f'<p><strong>🔗 Link:</strong> <a href="{note[4]}" target="_blank">{note[4]}</a></p>' if note[4] else ''}
                <p><small>📅 {note[5]}</small></p>
            </div>
            """, unsafe_allow_html=True)
            
            # Show image if exists
            if note[3] and os.path.exists(note[3]):
                st.image(note[3], use_container_width=True)
            
            if st.button(f"🗑️ Delete", key=f"del_note_{note[0]}"):
                if note[3] and os.path.exists(note[3]):
                    os.remove(note[3])
                delete_general_note(note[0])
                st.rerun()
            
            st.markdown("---")
    else:
        st.info("No notes yet. Start writing! 📝")

def show_study_mode():
    st.markdown("### 🎯 Study Mode - Flashcard Review")
    
    # Get random item for flashcard
    item = get_random_study_item()
    
    if item:
        item_type = item[0]
        
        st.markdown("""
        <div style="text-align: center; margin: 20px 0;">
            <p style="font-size: 18px; opacity: 0.7;">Tap the card to flip</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Flashcard
        with st.container():
            st.markdown('<div class="flashcard">', unsafe_allow_html=True)
            
            if item_type == 'medicine':
                st.markdown(f"""
                <h2>💊 {item[2]}</h2>
                <hr>
                <p><strong>Brand:</strong> {item[3]}</p>
                <p><strong>Generic:</strong> {item[4]}</p>
                <p><strong>Dose:</strong> {item[5]}</p>
                <p><strong>Route:</strong> {item[6]}</p>
                <p><strong>Group:</strong> {item[7]}</p>
                <p><strong>Notes:</strong> {item[8]}</p>
                """, unsafe_allow_html=True)
                
                # Favorite button
                if st.button("⭐ Add to Favorites", key="flashcard_fav"):
                    toggle_favorite_medicine(item[1])
                    st.rerun()
            
            elif item_type == 'lab_test':
                st.markdown(f"""
                <h2>🧪 {item[2]}</h2>
                <hr>
                <p><strong>Purpose:</strong> {item[3]}</p>
                <p><strong>Normal Range:</strong> {item[4]}</p>
                <p><strong>Preparation:</strong> {item[5]}</p>
                <p><strong>Notes:</strong> {item[6]}</p>
                """, unsafe_allow_html=True)
                
                # Favorite button
                if st.button("⭐ Add to Favorites", key="flashcard_fav"):
                    toggle_favorite_lab_test(item[1])
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Next button
        if st.button("🔄 Next Card", use_container_width=True):
            st.rerun()
        
        # Progress
        st.markdown("""
        <div style="text-align: center; margin-top: 20px;">
            <p style="opacity: 0.7;">💡 Study one card at a time for better retention</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("📚 No items to study! Add some medicines or lab tests first.")

def show_users():
    if st.session_state.get('user_role') != 'admin':
        st.error("⛔ Access denied. Admin only.")
        return
    
    st.markdown("### 👥 User Management")
    
    # Add user
    with st.expander("➕ Add New User"):
        with st.form("add_user_form"):
            new_username = st.text_input("Username *")
            new_password = st.text_input("Password *", type="password")
            role = st.selectbox("Role", ["user", "admin"])
            
            submitted = st.form_submit_button("👤 Add User")
            if submitted and new_username and new_password:
                if add_user(new_username, new_password, role):
                    st.success("✅ User added successfully!")
                    st.rerun()
                else:
                    st.error("❌ Username already exists!")
    
    # Display users
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("SELECT id, username, role, created_at FROM users")
    users = c.fetchall()
    conn.close()
    
    st.markdown("#### Existing Users")
    if users:
        for user in users:
            st.markdown(f"""
            <div class="glass-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4>👤 {user[1]}</h4>
                        <p><strong>Role:</strong> {user[2]} | <strong>Joined:</strong> {user[3]}</p>
                    </div>
                    {f'<span style="background: #667eea; padding: 5px 10px; border-radius: 10px; color: white;">Active</span>' if user[0] != 1 else '<span style="background: #FFD700; padding: 5px 10px; border-radius: 10px;">Admin</span>'}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No users found.")

def show_settings():
    st.markdown("### ⚙️ Settings")
    
    # Dark mode toggle
    st.markdown("#### Appearance")
    dark_mode = st.toggle("🌙 Dark Mode", value=st.session_state.get('dark_mode', True))
    if dark_mode != st.session_state.get('dark_mode'):
        st.session_state.dark_mode = dark_mode
        st.rerun()
    
    # Export
    st.markdown("#### Export Data")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Export PDF", use_container_width=True):
            # Get data
            medicines = get_medicines()
            med_data = [{"Name": m[1], "Brand": m[2], "Generic": m[3], "Dose": m[4], "Route": m[5], "Notes": m[7]} for m in medicines]
            pdf_buffer = export_to_pdf(med_data, "Dr Danyal - Medical Data")
            st.download_button(
                label="📥 Download PDF",
                data=pdf_buffer,
                file_name=f"medical_data_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf"
            )
    
    with col2:
        # CSV export
        medicines = get_medicines()
        if medicines:
            df = pd.DataFrame(medicines, columns=['ID', 'Name', 'Brand', 'Generic', 'Dose', 'Route', 'Group', 'Notes', 'Favorite', 'Created', 'Updated'])
            csv = df.to_csv(index=False)
            st.download_button(
                label="📊 Export CSV",
                data=csv,
                file_name=f"medical_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with col3:
        # Excel export
        medicines = get_medicines()
        if medicines:
            df = pd.DataFrame(medicines, columns=['ID', 'Name', 'Brand', 'Generic', 'Dose', 'Route', 'Group', 'Notes', 'Favorite', 'Created', 'Updated'])
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Medicines', index=False)
            st.download_button(
                label="📊 Export Excel",
                data=buffer,
                file_name=f"medical_data_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    # Backup and Restore
    st.markdown("#### Backup & Restore")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Create Backup", use_container_width=True):
            if os.path.exists('medical_data.db'):
                with open('medical_data.db', 'rb') as f:
                    backup_data = f.read()
                st.download_button(
                    label="📥 Download Backup",
                    data=backup_data,
                    file_name=f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db",
                    mime="application/octet-stream"
                )
    
    with col2:
        uploaded_file = st.file_uploader("📤 Restore Backup", type=['db'])
        if uploaded_file:
            with open('medical_data.db', 'wb') as f:
                f.write(uploaded_file.getbuffer())
            st.success("✅ Backup restored! Please restart the app.")
            st.rerun()

if __name__ == "__main__":
    main()
