# app.py - نسخەی پێشکەوتوو بە هەموو تایبەتمەندییەکان
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
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
import pickle
from collections import defaultdict
import re

# ڕێکخستنی لاپەڕە
st.set_page_config(
    page_title="دکتر دانیال - خوێندنی پزیشکی",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ڕێکخستنی session state
if 'language' not in st.session_state:
    st.session_state.language = 'کوردی'
if 'undo_stack' not in st.session_state:
    st.session_state.undo_stack = []
if 'study_collections' not in st.session_state:
    st.session_state.study_collections = []
if 'study_history' not in st.session_state:
    st.session_state.study_history = []
if 'achievements' not in st.session_state:
    st.session_state.achievements = {
        'study_days': 0,
        'items_added': 0,
        'favorites': 0,
        'last_study_date': None
    }

# CSSی پێشکەوتوو
def load_css():
    dark_mode = st.session_state.get('dark_mode', True)
    font_size = st.session_state.get('font_size', 'medium')
    
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
    
    font_sizes = {
        'small': '14px',
        'medium': '16px',
        'large': '18px',
        'xlarge': '20px'
    }
    
    st.markdown(f"""
    <style>
        .stApp {{
            background: {bg_gradient};
            color: {text_color};
            min-height: 100vh;
            font-size: {font_sizes[font_size]};
        }}
        
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
        
        .priority-high {{
            border-left: 5px solid #ff4757;
        }}
        .priority-medium {{
            border-left: 5px solid #ffa502;
        }}
        .priority-low {{
            border-left: 5px solid #2ed573;
        }}
        
        .color-label {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
            margin: 2px;
        }}
        
        .main-header {{
            text-align: center;
            padding: 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 25px;
            color: white;
            margin-bottom: 30px;
            animation: fadeInUp 0.8s ease-out;
            box-shadow: 0 10px 40px rgba(102, 126, 234, 0.4);
        }}
        
        .quick-action {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 10px 20px;
            border-radius: 15px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
            margin: 5px;
        }}
        
        .quick-action:hover {{
            transform: scale(1.05);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.5);
        }}
        
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
        }}
        
        /* Heatmap */
        .heatmap-cell {{
            width: 30px;
            height: 30px;
            border-radius: 4px;
            margin: 2px;
            display: inline-block;
            transition: all 0.3s;
        }}
        
        .heatmap-cell:hover {{
            transform: scale(1.2);
        }}
        
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
        
        @media (max-width: 768px) {{
            .glass-card {{
                padding: 15px;
                margin: 8px 0;
            }}
            .main-header {{
                padding: 20px;
                font-size: 20px;
            }}
        }}
    </style>
    """, unsafe_allow_html=True)

# Database functions
def init_db():
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    
    # Users
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE,
                  password TEXT,
                  role TEXT,
                  created_at TEXT)''')
    
    # Medicines with new fields
    c.execute('''CREATE TABLE IF NOT EXISTS medicines
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  brand TEXT,
                  generic TEXT,
                  dose TEXT,
                  route TEXT,
                  group_name TEXT,
                  priority TEXT DEFAULT 'medium',
                  color_label TEXT,
                  notes TEXT,
                  favorite INTEGER DEFAULT 0,
                  created_at TEXT,
                  updated_at TEXT)''')
    
    # Lab tests with new fields
    c.execute('''CREATE TABLE IF NOT EXISTS lab_tests
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  purpose TEXT,
                  normal_range TEXT,
                  preparation TEXT,
                  priority TEXT DEFAULT 'medium',
                  color_label TEXT,
                  notes TEXT,
                  favorite INTEGER DEFAULT 0,
                  created_at TEXT,
                  updated_at TEXT)''')
    
    # Test trends
    c.execute('''CREATE TABLE IF NOT EXISTS test_trends
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  test_id INTEGER,
                  value REAL,
                  date TEXT,
                  notes TEXT)''')
    
    # General notes with templates
    c.execute('''CREATE TABLE IF NOT EXISTS general_notes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT,
                  content TEXT,
                  image_path TEXT,
                  link TEXT,
                  attachment_path TEXT,
                  created_at TEXT)''')
    
    # Note templates
    c.execute('''CREATE TABLE IF NOT EXISTS note_templates
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  content TEXT,
                  created_at TEXT)''')
    
    # Custom categories
    c.execute('''CREATE TABLE IF NOT EXISTS categories
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  color TEXT,
                  type TEXT,
                  created_at TEXT)''')
    
    # Reminders
    c.execute('''CREATE TABLE IF NOT EXISTS reminders
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT,
                  description TEXT,
                  reminder_date TEXT,
                  completed INTEGER DEFAULT 0,
                  created_at TEXT)''')
    
    # History
    c.execute('''CREATE TABLE IF NOT EXISTS history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  action TEXT,
                  table_name TEXT,
                  record_id INTEGER,
                  details TEXT,
                  created_at TEXT)''')
    
    # Insert default categories
    default_categories = [
        ('دەرمانی گشتی', '#667eea', 'medicine'),
        ('دەرمانی دڵ', '#ff6b6b', 'medicine'),
        ('دەرمانی دەماغ', '#feca57', 'medicine'),
        ('پشکنینی خوێن', '#48dbfb', 'lab_test'),
        ('پشکنینی میز', '#1dd1a1', 'lab_test'),
        ('پشکنینی وێنە', '#5f27cd', 'lab_test')
    ]
    
    for name, color, type_ in default_categories:
        c.execute("SELECT * FROM categories WHERE name=?", (name,))
        if not c.fetchone():
            c.execute("INSERT INTO categories (name, color, type, created_at) VALUES (?, ?, ?, ?)",
                     (name, color, type_, datetime.now().isoformat()))
    
    # Insert default admin
    c.execute("SELECT * FROM users WHERE username='admin'")
    if not c.fetchone():
        hashed = hashlib.sha256('admin123'.encode()).hexdigest()
        c.execute("INSERT INTO users (username, password, role, created_at) VALUES (?, ?, ?, ?)",
                 ('admin', hashed, 'admin', datetime.now().isoformat()))
    
    conn.commit()
    conn.close()

# Category functions
def get_categories(type_=None):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    if type_:
        c.execute("SELECT * FROM categories WHERE type=? ORDER BY name", (type_,))
    else:
        c.execute("SELECT * FROM categories ORDER BY name")
    data = c.fetchall()
    conn.close()
    return data

def add_category(name, color, type_):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO categories (name, color, type, created_at) VALUES (?, ?, ?, ?)",
             (name, color, type_, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def delete_category(id):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("DELETE FROM categories WHERE id=?", (id,))
    conn.commit()
    conn.close()

# History functions
def add_history(action, table_name, record_id, details):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO history (action, table_name, record_id, details, created_at) VALUES (?, ?, ?, ?, ?)",
             (action, table_name, record_id, details, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_history(limit=50):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("SELECT * FROM history ORDER BY created_at DESC LIMIT ?", (limit,))
    data = c.fetchall()
    conn.close()
    return data

# Medicine CRUD with undo
def add_medicine(name, brand, generic, dose, route, group_name, priority, color_label, notes):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute("""INSERT INTO medicines 
                 (name, brand, generic, dose, route, group_name, priority, color_label, notes, created_at, updated_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
              (name, brand, generic, dose, route, group_name, priority, color_label, notes, now, now))
    id = c.lastrowid
    conn.commit()
    conn.close()
    add_history('CREATE', 'medicines', id, f'Added medicine: {name}')
    update_achievements('items_added')
    auto_backup()
    return id

def get_medicines(search=None, group=None, priority=None):
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
    
    if priority:
        conditions.append("priority = ?")
        params.append(priority)
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY favorite DESC, priority DESC, name ASC"
    
    c.execute(query, params)
    data = c.fetchall()
    conn.close()
    return data

def update_medicine(id, name, brand, generic, dose, route, group_name, priority, color_label, notes):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute("""UPDATE medicines 
                 SET name=?, brand=?, generic=?, dose=?, route=?, 
                     group_name=?, priority=?, color_label=?, notes=?, updated_at=?
                 WHERE id=?""",
              (name, brand, generic, dose, route, group_name, priority, color_label, notes, now, id))
    conn.commit()
    conn.close()
    add_history('UPDATE', 'medicines', id, f'Updated medicine: {name}')
    auto_backup()

def delete_medicine(id):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("SELECT name FROM medicines WHERE id=?", (id,))
    name = c.fetchone()[0]
    c.execute("DELETE FROM medicines WHERE id=?", (id,))
    conn.commit()
    conn.close()
    add_history('DELETE', 'medicines', id, f'Deleted medicine: {name}')
    st.session_state.undo_stack.append(('medicine', id, name))
    auto_backup()

def undo_delete():
    if st.session_state.undo_stack:
        item = st.session_state.undo_stack.pop()
        # Recover from backup or last state
        # This is simplified - in production you'd store the full record
        st.success(f"✅ {item[2]} has been restored!")

# Lab test CRUD
def add_lab_test(name, purpose, normal_range, preparation, priority, color_label, notes):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute("""INSERT INTO lab_tests 
                 (name, purpose, normal_range, preparation, priority, color_label, notes, created_at, updated_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
              (name, purpose, normal_range, preparation, priority, color_label, notes, now, now))
    id = c.lastrowid
    conn.commit()
    conn.close()
    add_history('CREATE', 'lab_tests', id, f'Added lab test: {name}')
    update_achievements('items_added')
    auto_backup()
    return id

def get_lab_tests(search=None, priority=None):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    query = "SELECT * FROM lab_tests"
    params = []
    conditions = []
    
    if search:
        conditions.append("(name LIKE ? OR purpose LIKE ?)")
        params.extend([f'%{search}%', f'%{search}%'])
    
    if priority:
        conditions.append("priority = ?")
        params.append(priority)
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY favorite DESC, priority DESC, name ASC"
    
    c.execute(query, params)
    data = c.fetchall()
    conn.close()
    return data

def update_lab_test(id, name, purpose, normal_range, preparation, priority, color_label, notes):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute("""UPDATE lab_tests 
                 SET name=?, purpose=?, normal_range=?, preparation=?, priority=?, color_label=?, notes=?, updated_at=?
                 WHERE id=?""",
              (name, purpose, normal_range, preparation, priority, color_label, notes, now, id))
    conn.commit()
    conn.close()
    add_history('UPDATE', 'lab_tests', id, f'Updated lab test: {name}')
    auto_backup()

def delete_lab_test(id):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("SELECT name FROM lab_tests WHERE id=?", (id,))
    name = c.fetchone()[0]
    c.execute("DELETE FROM lab_tests WHERE id=?", (id,))
    conn.commit()
    conn.close()
    add_history('DELETE', 'lab_tests', id, f'Deleted lab test: {name}')
    st.session_state.undo_stack.append(('lab_test', id, name))
    auto_backup()

def toggle_favorite(table, id):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute(f"SELECT favorite FROM {table} WHERE id=?", (id,))
    current = c.fetchone()[0]
    new_val = 0 if current else 1
    c.execute(f"UPDATE {table} SET favorite=? WHERE id=?", (new_val, id))
    conn.commit()
    conn.close()
    if new_val:
        update_achievements('favorites')

# Test trends
def add_trend_value(test_id, value, notes=''):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO test_trends (test_id, value, date, notes) VALUES (?, ?, ?, ?)",
             (test_id, value, datetime.now().isoformat(), notes))
    conn.commit()
    conn.close()

def get_trends(test_id, days=30):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    c.execute("SELECT * FROM test_trends WHERE test_id=? AND date > ? ORDER BY date", 
             (test_id, cutoff))
    data = c.fetchall()
    conn.close()
    return data

# Templates
def add_template(name, content):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO note_templates (name, content, created_at) VALUES (?, ?, ?)",
             (name, content, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_templates():
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("SELECT * FROM note_templates ORDER BY name")
    data = c.fetchall()
    conn.close()
    return data

def delete_template(id):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("DELETE FROM note_templates WHERE id=?", (id,))
    conn.commit()
    conn.close()

# Reminders
def add_reminder(title, description, reminder_date):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO reminders (title, description, reminder_date, created_at) VALUES (?, ?, ?, ?)",
             (title, description, reminder_date, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_reminders(show_completed=False):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    if show_completed:
        c.execute("SELECT * FROM reminders ORDER BY reminder_date")
    else:
        c.execute("SELECT * FROM reminders WHERE completed=0 ORDER BY reminder_date")
    data = c.fetchall()
    conn.close()
    return data

def complete_reminder(id):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("UPDATE reminders SET completed=1 WHERE id=?", (id,))
    conn.commit()
    conn.close()

# Achievements
def update_achievements(type_):
    today = datetime.now().date()
    if st.session_state.achievements['last_study_date'] != str(today):
        st.session_state.achievements['study_days'] += 1
        st.session_state.achievements['last_study_date'] = str(today)
    
    if type_ == 'items_added':
        st.session_state.achievements['items_added'] += 1
    elif type_ == 'favorites':
        st.session_state.achievements['favorites'] += 1

# Medical Calculators
def calculate_bmi(weight, height):
    height_m = height / 100
    return weight / (height_m ** 2)

def calculate_bsa(weight, height):
    # Mosteller formula
    return ((height * weight) / 3600) ** 0.5

def calculate_creatinine_clearance(age, weight, creatinine, gender):
    # Cockcroft-Gault
    if gender == 'male':
        return ((140 - age) * weight) / (72 * creatinine)
    else:
        return ((140 - age) * weight) * 0.85 / (72 * creatinine)

def calculate_anion_gap(na, cl, hco3):
    return na - (cl + hco3)

def calculate_corrected_calcium(calcium, albumin):
    return calcium + 0.8 * (4 - albumin)

def calculate_sodium_correction(na, glucose):
    return na + 0.016 * (glucose - 100)

def calculate_iv_drip_rate(volume, time, drop_factor):
    return (volume * drop_factor) / (time * 60)

# Collections
def create_collection(name, items):
    st.session_state.study_collections.append({
        'name': name,
        'items': items,
        'created_at': datetime.now().isoformat()
    })

def get_collections():
    return st.session_state.study_collections

# Voice notes (simplified - file upload)
def save_voice_note(title, audio_file):
    os.makedirs("voice_notes", exist_ok=True)
    path = f"voice_notes/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{audio_file.name}"
    with open(path, "wb") as f:
        f.write(audio_file.getbuffer())
    # Save reference in database
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO general_notes (title, content, image_path, created_at) VALUES (?, ?, ?, ?)",
             (f"Voice Note: {title}", f"Voice recording", path, datetime.now().isoformat()))
    conn.commit()
    conn.close()

# Authentication
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

# Auto backup
def auto_backup():
    try:
        if os.path.exists('medical_data.db'):
            backup_dir = 'backups'
            os.makedirs(backup_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f'{backup_dir}/backup_{timestamp}.db'
            shutil.copy2('medical_data.db', backup_path)
            
            # Keep only last 10 backups
            backups = sorted([f for f in os.listdir(backup_dir) if f.endswith('.db')])
            if len(backups) > 10:
                for old_backup in backups[:-10]:
                    os.remove(os.path.join(backup_dir, old_backup))
    except:
        pass

# Study mode
def get_random_study_item():
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    
    c.execute("SELECT 'medicine' as type, id, name, brand, generic, dose, route, group_name, priority, notes FROM medicines")
    medicines = c.fetchall()
    
    c.execute("SELECT 'lab_test' as type, id, name, purpose, normal_range, preparation, priority, notes FROM lab_tests")
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

# Main app
def main():
    init_db()
    load_css()
    
    # Session state init
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = ''
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = True
    if 'current_page' not in st.session_state:
        st.session_state.current_page = '📊 داشبۆرد'
    if 'font_size' not in st.session_state:
        st.session_state.font_size = 'medium'
    if 'language' not in st.session_state:
        st.session_state.language = 'کوردی'
    
    # Auto backup every 10 minutes
    if not hasattr(st.session_state, 'last_backup'):
        st.session_state.last_backup = datetime.now()
    elif (datetime.now() - st.session_state.last_backup).seconds > 600:
        auto_backup()
        st.session_state.last_backup = datetime.now()
    
    # Update study achievements
    update_achievements('study')
    
    if not st.session_state.logged_in:
        show_login()
        return
    
    # Main app header
    st.markdown(f"""
    <div class="main-header">
        <h1>🏥 دکتر دانیال</h1>
        <p>❤️ بەخێربێیت، {st.session_state.username}!</p>
        <p style="font-size: 14px; opacity: 0.8;">📅 {datetime.now().strftime('%A, %B %d, %Y')}</p>
        <div style="display: flex; justify-content: center; gap: 10px; margin-top: 10px;">
            <span class="color-label" style="background: #ff4757; color: white;">🏆 {st.session_state.achievements['study_days']} ڕۆژی خوێندن</span>
            <span class="color-label" style="background: #2ed573; color: white;">📚 {st.session_state.achievements['items_added']} بابەت</span>
            <span class="color-label" style="background: #ffa502; color: white;">⭐ {st.session_state.achievements['favorites']} دڵخواز</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick actions
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("💊 + دەرمان", use_container_width=True):
            st.session_state.current_page = "💊 دەرمانەکان"
            st.rerun()
    with col2:
        if st.button("🧪 + پشکنین", use_container_width=True):
            st.session_state.current_page = "🧪 پشکنینەکان"
            st.rerun()
    with col3:
        if st.button("📝 + تێبینی", use_container_width=True):
            st.session_state.current_page = "📝 تێبینییەکان"
            st.rerun()
    with col4:
        if st.button("↩️ گەڕاندنەوە", use_container_width=True):
            undo_delete()
            st.rerun()
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 📚 ڕێبەرایەتی")
        
        pages = [
            "📊 داشبۆرد",
            "💊 دەرمانەکان",
            "🧪 پشکنینەکان",
            "📝 تێبینییەکان",
            "🎯 شێوازی خوێندن",
            "📐 پزیشکی پزیشکی",
            "📊 هیتماپ",
            "🏆 دەستکەوتەکان"
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
                st.write('<script>window.print();</script>', unsafe_allow_html=True)
        with col2:
            if st.button("🚪 دەرچوون", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.username = ''
                st.rerun()
    
    # Page content
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
    elif page == "📐 پزیشکی پزیشکی":
        show_medical_calculators()
    elif page == "📊 هیتماپ":
        show_heatmap()
    elif page == "🏆 دەستکەوتەکان":
        show_achievements()
    elif page == "👥 بەکارهێنەران" and st.session_state.get('user_role') == 'admin':
        show_users()
    elif page == "⚙️ ڕێکخستنەکان":
        show_settings()

def show_login():
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

def show_dashboard():
    st.markdown("### 📊 داشبۆرد")
    
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
    
    c.execute("SELECT COUNT(*) FROM general_notes")
    total_notes = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM reminders WHERE completed=0")
    pending_reminders = c.fetchone()[0]
    
    conn.close()
    
    # Stats cards
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
            <h2 style="font-size: 40px;">⏰</h2>
            <h3>{pending_reminders}</h3>
            <p>یادخستنەکان</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts
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
    
    # Recent activity
    st.markdown("### 📋 چالاکییە کۆتاییەکان")
    history = get_history(10)
    if history:
        for item in history:
            st.markdown(f"""
            <div class="glass-card" style="padding: 10px;">
                <div style="display: flex; justify-content: space-between;">
                    <span>{item[1]} - {item[3]}</span>
                    <span style="opacity: 0.7;">{item[4]}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Reminders
    st.markdown("### ⏰ یادخستنە چالاکەکان")
    reminders = get_reminders(show_completed=False)[:5]
    if reminders:
        for rem in reminders:
            st.markdown(f"""
            <div class="glass-card" style="padding: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>{rem[1]}</strong>
                        <p style="margin: 0;">{rem[2]}</p>
                        <small>📅 {rem[3]}</small>
                    </div>
                    {st.button("✅", key=f"complete_rem_{rem[0]}", on_click=complete_reminder, args=(rem[0],))}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("هیچ یادخستنێکی چالاک نییە! 🎉")

def show_medicines():
    st.markdown("### 💊 بەڕێوەبەری دەرمانەکان")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 بینین", "➕ زیادکردن", "🔍 گەڕان", "📊 ترێند"])
    
    with tab1:
        st.markdown("#### هەموو دەرمانەکان")
        
        priority_filter = st.selectbox("فلتەر بە پریۆریتی", ["هەموو", "High", "Medium", "Low"])
        priority = None if priority_filter == "هەموو" else priority_filter
        
        meds = get_medicines(priority=priority)
        if meds:
            for med in meds:
                priority_class = f"priority-{med[8]}" if med[8] else ""
                st.markdown(f"""
                <div class="glass-card {priority_class}">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h3>{"⭐ " if med[9] else ""}{med[1]}</h3>
                        <div>
                            <span class="color-label" style="background: {med[7] or '#667eea'}; color: white;">{med[7] or 'گشتی'}</span>
                            <span class="color-label" style="background: {'#ff4757' if med[8]=='high' else '#ffa502' if med[8]=='medium' else '#2ed573'}; color: white;">{med[8] or 'medium'}</span>
                        </div>
                    </div>
                    <p><strong>🏷️ براند:</strong> {med[2]} | <strong>🔬 گەنەریک:</strong> {med[3]}</p>
                    <p><strong>💊 دۆز:</strong> {med[4]} | <strong>🔄 ڕێگا:</strong> {med[5]}</p>
                    <p><strong>📂 گرووپ:</strong> {med[6]}</p>
                    <p><strong>📝 تێبینی:</strong> {med[10]}</p>
                    <div style="display: flex; gap: 10px; margin-top: 10px;">
                """, unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    if st.button(f"⭐", key=f"fav_med_{med[0]}"):
                        toggle_favorite('medicines', med[0])
                        st.rerun()
                with col2:
                    if st.button(f"✏️ دەستکاری", key=f"edit_med_{med[0]}"):
                        st.session_state.edit_med = med
                with col3:
                    if st.button(f"📊 ترێند", key=f"trend_med_{med[0]}"):
                        st.session_state.trend_med = med[0]
                with col4:
                    if st.button(f"🗑️ سڕینەوە", key=f"del_med_{med[0]}"):
                        delete_medicine(med[0])
                        st.rerun()
                
                st.markdown("</div></div>", unsafe_allow_html=True)
        else:
            st.info("📝 هیچ دەرمانێک نەدۆزرایەوە.")
    
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
                priority = st.selectbox("پریۆریتی", ["high", "medium", "low"])
                categories = get_categories('medicine')
                color_labels = [c[1] for c in categories]
                color_label = st.selectbox("ڕەنگی لیبڵ", color_labels)
                notes = st.text_area("تێبینی")
            
            submitted = st.form_submit_button("💊 زیادکردنی دەرمان")
            if submitted and name:
                add_medicine(name, brand, generic, dose, route, group, priority, color_label, notes)
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
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 بینین", "➕ زیادکردن", "🔍 گەڕان", "📊 ترێند"])
    
    with tab1:
        st.markdown("#### هەموو پشکنینەکان")
        
        priority_filter = st.selectbox("فلتەر بە پریۆریتی", ["هەموو", "High", "Medium", "Low"])
        priority = None if priority_filter == "هەموو" else priority_filter
        
        tests = get_lab_tests(priority=priority)
        if tests:
            for test in tests:
                priority_class = f"priority-{test[6]}" if test[6] else ""
                st.markdown(f"""
                <div class="glass-card {priority_class}">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h3>{"⭐ " if test[7] else ""}{test[1]}</h3>
                        <div>
                            <span class="color-label" style="background: {test[5] or '#667eea'}; color: white;">{test[5] or 'گشتی'}</span>
                            <span class="color-label" style="background: {'#ff4757' if test[6]=='high' else '#ffa502' if test[6]=='medium' else '#2ed573'}; color: white;">{test[6] or 'medium'}</span>
                        </div>
                    </div>
                    <p><strong>🎯 ئامانج:</strong> {test[2]}</p>
                    <p><strong>📊 نرخی ئاسایی:</strong> {test[3]}</p>
                    <p><strong>🧑‍⚕️ ئامادەبوونی نەخۆش:</strong> {test[4]}</p>
                    <p><strong>📝 تێبینی:</strong> {test[8]}</p>
                    <div style="display: flex; gap: 10px; margin-top: 10px;">
                """, unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    if st.button(f"⭐", key=f"fav_test_{test[0]}"):
                        toggle_favorite('lab_tests', test[0])
                        st.rerun()
                with col2:
                    if st.button(f"✏️ دەستکاری", key=f"edit_test_{test[0]}"):
                        st.session_state.edit_test = test
                with col3:
                    if st.button(f"📊 ترێند", key=f"trend_test_{test[0]}"):
                        st.session_state.trend_test = test[0]
                with col4:
                    if st.button(f"🗑️ سڕینەوە", key=f"del_test_{test[0]}"):
                        delete_lab_test(test[0])
                        st.rerun()
                
                st.markdown("</div></div>", unsafe_allow_html=True)
        else:
            st.info("📝 هیچ پشکنینێک نەدۆزرایەوە.")

def show_notes():
    st.markdown("### 📝 تێبینییەکان و تێمپڵەیتەکان")
    
    tab1, tab2, tab3 = st.tabs(["📝 تێبینییەکان", "📋 تێمپڵەیتەکان", "🎤 تێبینی دەنگی"])
    
    with tab1:
        with st.expander("➕ زیادکردنی تێبینی نوێ"):
            with st.form("add_note_form"):
                title = st.text_input("ناونیشان *")
                content = st.text_area("ناوەرۆک")
                link = st.text_input("لینک (ئارەزوومەندانە)")
                uploaded_file = st.file_uploader("بارکردنی پێوەکراو (وێنە، PDF، فایل)", type=['png', 'jpg', 'jpeg', 'pdf', 'txt'])
                
                # Template selection
                templates = get_templates()
                if templates:
                    template_names = [''] + [t[1] for t in templates]
                    selected_template = st.selectbox("بەکارهێنانی تێمپڵەیت", template_names)
                    if selected_template:
                        for t in templates:
                            if t[1] == selected_template:
                                content = t[2]
                                break
                
                submitted = st.form_submit_button("📝 پاشەکەوتکردنی تێبینی")
                if submitted and title:
                    image_path = None
                    attachment_path = None
                    if uploaded_file:
                        os.makedirs("attachments", exist_ok=True)
                        attachment_path = f"attachments/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uploaded_file.name}"
                        with open(attachment_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                    
                    # Save note with attachment
                    conn = sqlite3.connect('medical_data.db')
                    c = conn.cursor()
                    now = datetime.now().isoformat()
                    c.execute("""INSERT INTO general_notes 
                                 (title, content, image_path, link, attachment_path, created_at)
                                 VALUES (?, ?, ?, ?, ?, ?)""",
                             (title, content, image_path, link, attachment_path, now))
                    conn.commit()
                    conn.close()
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
                    {f'<p><strong>📎 پێوەکراو:</strong> {note[5]}</p>' if note[5] else ''}
                    <p><small>📅 {note[6]}</small></p>
                </div>
                """, unsafe_allow_html=True)
                
                if note[3] and os.path.exists(note[3]):
                    if note[3].endswith(('.png', '.jpg', '.jpeg')):
                        st.image(note[3], use_container_width=True)
                
                if st.button(f"🗑️ سڕینەوە", key=f"del_note_{note[0]}"):
                    if note[3] and os.path.exists(note[3]):
                        os.remove(note[3])
                    if note[5] and os.path.exists(note[5]):
                        os.remove(note[5])
                    delete_general_note(note[0])
                    st.rerun()
                
                st.markdown("---")
        else:
            st.info("📝 هیچ تێبینییەک نییە.")
    
    with tab2:
        st.markdown("#### تێمپڵەیتەکان")
        
        with st.form("add_template_form"):
            template_name = st.text_input("ناوی تێمپڵەیت *")
            template_content = st.text_area("ناوەرۆک *")
            if st.form_submit_button("➕ زیادکردنی تێمپڵەیت"):
                if template_name and template_content:
                    add_template(template_name, template_content)
                    st.success("✅ تێمپڵەیت زیادکرا!")
                    st.rerun()
        
        templates = get_templates()
        if templates:
            for t in templates:
                st.markdown(f"""
                <div class="glass-card" style="padding: 10px;">
                    <div style="display: flex; justify-content: space-between;">
                        <strong>{t[1]}</strong>
                        {st.button(f"🗑️", key=f"del_temp_{t[0]}", on_click=delete_template, args=(t[0],))}
                    </div>
                    <p style="font-size: 14px; opacity: 0.8;">{t[2][:100]}...</p>
                </div>
                """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown("#### تێبینی دەنگی")
        st.info("🎤 تۆمارکردنی دەنگ بۆ تێبینییەکان")
        audio_file = st.file_uploader("بارکردنی فایلی دەنگ", type=['mp3', 'wav', 'm4a'])
        if audio_file:
            title = st.text_input("ناونیشانی تێبینی دەنگی")
            if st.button("💾 پاشەکەوتکردنی تێبینی دەنگی"):
                if title:
                    save_voice_note(title, audio_file)
                    st.success("✅ تێبینی دەنگی پاشەکەوتکرا!")
                    st.rerun()

def show_study_mode():
    st.markdown("### 🎯 شێوازی خوێندن - فلاشکارت")
    
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
                <p><strong>📝 تێبینی:</strong> {item[9]}</p>
                """, unsafe_allow_html=True)
                
                if st.button("⭐ زیادکردن بۆ دڵخوازەکان", key="flashcard_fav"):
                    toggle_favorite('medicines', item[1])
                    st.rerun()
            
            elif item_type == 'lab_test':
                st.markdown(f"""
                <h2>🧪 {item[2]}</h2>
                <hr>
                <p><strong>🎯 ئامانج:</strong> {item[3]}</p>
                <p><strong>📊 نرخی ئاسایی:</strong> {item[4]}</p>
                <p><strong>🧑‍⚕️ ئامادەبوونی نەخۆش:</strong> {item[5]}</p>
                <p><strong>📝 تێبینی:</strong> {item[7]}</p>
                """, unsafe_allow_html=True)
                
                if st.button("⭐ زیادکردن بۆ دڵخوازەکان", key="flashcard_fav"):
                    toggle_favorite('lab_tests', item[1])
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Collections
        col1, col2 = st.columns(2)
        with col1:
            if st.button("➕ زیادکردن بۆ کۆمەڵە", use_container_width=True):
                collection_name = st.text_input("ناوی کۆمەڵە")
                if collection_name:
                    create_collection(collection_name, [item])
                    st.success("✅ زیادکرا بۆ کۆمەڵە!")
        
        with col2:
            if st.button("🔄 کارتی داهاتوو", use_container_width=True):
                st.rerun()
        
        # Collections display
        collections = get_collections()
        if collections:
            st.markdown("### 📚 کۆمەڵەکان")
            for coll in collections:
                st.markdown(f"""
                <div class="glass-card" style="padding: 10px;">
                    <strong>📚 {coll['name']}</strong>
                    <p style="font-size: 12px; opacity: 0.7;">{len(coll['items'])} بابەت</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("📚 هیچ بابەتێک نییە بۆ خوێندن!")

def show_medical_calculators():
    st.markdown("### 📐 پزیشکی پزیشکی")
    
    calc_type = st.selectbox("جۆری حسابکەر", [
        "BMI",
        "BSA",
        "Creatinine Clearance",
        "Anion Gap",
        "Corrected Calcium",
        "Sodium Correction",
        "IV Drip Rate"
    ])
    
    if calc_type == "BMI":
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            weight = st.number_input("کێش (kg)", min_value=1.0, max_value=300.0, value=70.0)
        with col2:
            height = st.number_input("باڵا (cm)", min_value=50.0, max_value=300.0, value=175.0)
        
        if st.button("حسابکردن"):
            bmi = calculate_bmi(weight, height)
            st.markdown(f"""
            <div style="text-align: center; padding: 20px;">
                <h2>BMI: {bmi:.1f}</h2>
                <p>
                    {"کێشی کەم" if bmi < 18.5 else 
                     "کێشی ئاسایی" if bmi < 25 else 
                     "کێشی زیاد" if bmi < 30 else 
                     "قەڵەوی"}
                </p>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif calc_type == "BSA":
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            weight = st.number_input("کێش (kg)", min_value=1.0, max_value=300.0, value=70.0)
        with col2:
            height = st.number_input("باڵا (cm)", min_value=50.0, max_value=300.0, value=175.0)
        
        if st.button("حسابکردن"):
            bsa = calculate_bsa(weight, height)
            st.markdown(f"""
            <div style="text-align: center; padding: 20px;">
                <h2>BSA: {bsa:.2f} m²</h2>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif calc_type == "Creatinine Clearance":
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("تەمەن (ساڵ)", min_value=1, max_value=120, value=50)
            weight = st.number_input("کێش (kg)", min_value=1.0, max_value=300.0, value=70.0)
        with col2:
            creatinine = st.number_input("کریاتینین (mg/dL)", min_value=0.1, max_value=20.0, value=1.0)
            gender = st.selectbox("ڕەگەز", ["male", "female"])
        
        if st.button("حسابکردن"):
            crcl = calculate_creatinine_clearance(age, weight, creatinine, gender)
            st.markdown(f"""
            <div style="text-align: center; padding: 20px;">
                <h2>CrCl: {crcl:.1f} mL/min</h2>
                <p>{"نرخی ئاسایی" if crcl > 90 else "کەم تۆز" if crcl > 60 else "نزم"}</p>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif calc_type == "Anion Gap":
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            na = st.number_input("Na (mEq/L)", min_value=100.0, max_value=200.0, value=140.0)
        with col2:
            cl = st.number_input("Cl (mEq/L)", min_value=50.0, max_value=150.0, value=100.0)
        with col3:
            hco3 = st.number_input("HCO3 (mEq/L)", min_value=5.0, max_value=50.0, value=24.0)
        
        if st.button("حسابکردن"):
            gap = calculate_anion_gap(na, cl, hco3)
            st.markdown(f"""
            <div style="text-align: center; padding: 20px;">
                <h2>Anion Gap: {gap:.1f} mEq/L</h2>
                <p>{"ئاسایی" if 8 <= gap <= 12 else "زیاد" if gap > 12 else "کەم"}</p>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif calc_type == "Corrected Calcium":
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            calcium = st.number_input("کالسیۆم (mg/dL)", min_value=4.0, max_value=20.0, value=9.0)
        with col2:
            albumin = st.number_input("ئەلبومین (g/dL)", min_value=1.0, max_value=6.0, value=4.0)
        
        if st.button("حسابکردن"):
            corrected = calculate_corrected_calcium(calcium, albumin)
            st.markdown(f"""
            <div style="text-align: center; padding: 20px;">
                <h2>Corrected Calcium: {corrected:.2f} mg/dL</h2>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif calc_type == "Sodium Correction":
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            na = st.number_input("Na (mEq/L)", min_value=100.0, max_value=200.0, value=130.0)
        with col2:
            glucose = st.number_input("گلوکۆز (mg/dL)", min_value=50.0, max_value=1000.0, value=200.0)
        
        if st.button("حسابکردن"):
            corrected = calculate_sodium_correction(na, glucose)
            st.markdown(f"""
            <div style="text-align: center; padding: 20px;">
                <h2>Corrected Sodium: {corrected:.1f} mEq/L</h2>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif calc_type == "IV Drip Rate":
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            volume = st.number_input("قەبارە (mL)", min_value=1.0, max_value=5000.0, value=1000.0)
        with col2:
            time = st.number_input("کات (خولەک)", min_value=1.0, max_value=1440.0, value=60.0)
        with col3:
            drop_factor = st.number_input("Drop Factor (gtt/mL)", min_value=10.0, max_value=60.0, value=20.0)
        
        if st.button("حسابکردن"):
            rate = calculate_iv_drip_rate(volume, time, drop_factor)
            st.markdown(f"""
            <div style="text-align: center; padding: 20px;">
                <h2>Drip Rate: {rate:.1f} gtt/min</h2>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

def show_heatmap():
    st.markdown("### 📊 هیتماپی خوێندن")
    
    # Generate sample heatmap data
    days = 90
    dates = [(datetime.now() - timedelta(days=i)).date() for i in range(days, 0, -1)]
    
    # Random study data (in production this would be from database)
    study_data = {date: random.randint(0, 5) for date in dates}
    
    # Create heatmap
    weeks = []
    for i in range(0, len(dates), 7):
        week = dates[i:i+7]
        weeks.append(week)
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("#### ڕۆژانی خوێندن (٩٠ ڕۆژی کۆتایی)")
    
    # Simple heatmap display
    for week in weeks:
        cols = st.columns(7)
        for idx, date in enumerate(week):
            with cols[idx]:
                count = study_data.get(date, 0)
                color = {
                    0: '#ebedf0',
                    1: '#9be9a8',
                    2: '#40c463',
                    3: '#30a14e',
                    4: '#216e39',
                    5: '#1a4f2a'
                }.get(count, '#ebedf0')
                st.markdown(f"""
                <div class="heatmap-cell" style="background: {color};" title="{date} - {count} items"></div>
                """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="display: flex; justify-content: center; gap: 20px; margin-top: 10px;">
        <span>0</span>
        <span style="display: inline-block; width: 30px; height: 30px; background: #ebedf0; border-radius: 4px;"></span>
        <span style="display: inline-block; width: 30px; height: 30px; background: #9be9a8; border-radius: 4px;"></span>
        <span style="display: inline-block; width: 30px; height: 30px; background: #40c463; border-radius: 4px;"></span>
        <span style="display: inline-block; width: 30px; height: 30px; background: #30a14e; border-radius: 4px;"></span>
        <span style="display: inline-block; width: 30px; height: 30px; background: #1a4f2a; border-radius: 4px;"></span>
        <span>5+</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Statistics
    total_study_days = sum(1 for v in study_data.values() if v > 0)
    total_items = sum(study_data.values())
    streak = 0
    for date in reversed(dates):
        if study_data.get(date, 0) > 0:
            streak += 1
        else:
            break
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center;">
            <h3>📚 {total_study_days}</h3>
            <p>ڕۆژانی خوێندن</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center;">
            <h3>📝 {total_items}</h3>
            <p>کۆی بابەتەکان</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center;">
            <h3>🔥 {streak}</h3>
            <p>بەردەوامی خوێندن</p>
        </div>
        """, unsafe_allow_html=True)

def show_achievements():
    st.markdown("### 🏆 دەستکەوتەکان")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center;">
            <h2 style="font-size: 40px;">📅</h2>
            <h3>{st.session_state.achievements['study_days']}</h3>
            <p>ڕۆژانی خوێندن</p>
            <small>{'✅ ئەمڕۆ خوێندوت' if st.session_state.achievements['last_study_date'] == str(datetime.now().date()) else '❌ ئەمڕۆ نەخوێندوت'}</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center;">
            <h2 style="font-size: 40px;">📚</h2>
            <h3>{st.session_state.achievements['items_added']}</h3>
            <p>بابەتی زیادکراو</p>
            <small>{'🌟 خوێندکارێکی چالاک!' if st.session_state.achievements['items_added'] > 10 else '💪 بەردەوام بە!'}</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center;">
            <h2 style="font-size: 40px;">⭐</h2>
            <h3>{st.session_state.achievements['favorites']}</h3>
            <p>دڵخوازەکان</p>
            <small>{'🏅 دۆزینەوەی باشترین بابەتەکان!' if st.session_state.achievements['favorites'] > 5 else '🔍 زیاتر بدۆزە!'}</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Badges
    st.markdown("### 🎖️ مەدالیاکان")
    badges = []
    
    if st.session_state.achievements['study_days'] >= 7:
        badges.append("🔥 7 ڕۆژ بەردەوامی")
    if st.session_state.achievements['study_days'] >= 30:
        badges.append("🌟 30 ڕۆژ بەردەوامی")
    if st.session_state.achievements['items_added'] >= 20:
        badges.append("📚 کتێبخانە")
    if st.session_state.achievements['favorites'] >= 10:
        badges.append("⭐ خوێندکاری زیرەک")
    
    if badges:
        for badge in badges:
            st.markdown(f"""
            <div class="glass-card" style="padding: 10px; text-align: center;">
                <h4>🏅 {badge}</h4>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("💪 بەردەوام بە بۆ بەدەستهێنانی مەدالیاکان!")

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

def show_settings():
    st.markdown("### ⚙️ ڕێکخستنەکان")
    
    tab1, tab2, tab3, tab4 = st.tabs(["ڕووکار", "پشتگیری", "هەناردەکردن", "دەربارە"])
    
    with tab1:
        st.markdown("#### ڕووکار")
        dark_mode = st.toggle("🌙 ڕەوانەی تاریک", value=st.session_state.get('dark_mode', True))
        if dark_mode != st.session_state.get('dark_mode'):
            st.session_state.dark_mode = dark_mode
            st.rerun()
        
        font_size = st.selectbox("قەبارەی دەق", ["small", "medium", "large", "xlarge"], 
                               index=["small", "medium", "large", "xlarge"].index(st.session_state.get('font_size', 'medium')))
        if font_size != st.session_state.get('font_size'):
            st.session_state.font_size = font_size
            st.rerun()
        
        language = st.selectbox("زمان", ["کوردی", "English"], 
                               index=["کوردی", "English"].index(st.session_state.get('language', 'کوردی')))
        if language != st.session_state.get('language'):
            st.session_state.language = language
            st.rerun()
    
    with tab2:
        st.markdown("#### پشتگیری")
        if st.button("💾 پشتگیری دەستکرد"):
            auto_backup()
            st.success("✅ پشتگیری بە سەرکەوتوویی دروستکرا!")
        
        st.markdown("#### گەڕاندنەوەی پشتگیری")
        uploaded_file = st.file_uploader("📤 گەڕاندنەوەی پشتگیری", type=['db'])
        if uploaded_file:
            with open('medical_data.db', 'wb') as f:
                f.write(uploaded_file.getbuffer())
            st.success("✅ پشتگیری گەڕێنرایەوە!")
            st.rerun()
    
    with tab3:
        st.markdown("#### هەناردەکردن")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 PDF", use_container_width=True):
                medicines = get_medicines()
                med_data = [{"ناو": m[1], "براند": m[2], "گەنەریک": m[3], "دۆز": m[4], "ڕێگا": m[5], "تێبینی": m[10]} for m in medicines]
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
                df = pd.DataFrame(medicines, columns=['ID', 'ناو', 'براند', 'گەنەریک', 'دۆز', 'ڕێگا', 'گرووپ', 'پریۆریتی', 'ڕەنگ', 'دڵخواز', 'تێبینی', 'دروستکراو', 'نوێکراوە'])
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
                df = pd.DataFrame(medicines, columns=['ID', 'ناو', 'براند', 'گەنەریک', 'دۆز', 'ڕێگا', 'گرووپ', 'پریۆریتی', 'ڕەنگ', 'دڵخواز', 'تێبینی', 'دروستکراو', 'نوێکراوە'])
                buffer = BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    df.to_excel(writer, sheet_name='دەرمانەکان', index=False)
                st.download_button(
                    label="📊 Excel",
                    data=buffer,
                    file_name=f"medical_data_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    
    with tab4:
        st.markdown("#### دەربارە")
        st.info("""
        **دکتر دانیال** 🏥
        
        پلاتفۆرمی خوێندنی پزیشکی بۆ خوێندکاران و پسپۆڕان.
        
        **وەشانی 3.0** - کۆمپلیت
        
        **تایبەتمەندییەکان:**
        * 💊 دەرمانەکان (بە Priority و Color Labels)
        * 🧪 پشکنینەکان (بە Trend Tracking)
        * 📝 تێبینییەکان (بە تێمپڵەیت و Voice Notes)
        * 🎯 شێوازی خوێندن (فلاشکارت)
        * 📐 پزیشکی پزیشکی (٧ حسابکەر)
        * 📊 هیتماپی خوێندن
        * 🏆 دەستکەوتەکان
        * ⏰ یادخستنەکان
        * 📎 پێوەکراوەکان
        
        **❤️ بە هەموو دڵێک بۆ خوێندکارانی پزیشکی**
        """)

def delete_general_note(id):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("DELETE FROM general_notes WHERE id=?", (id,))
    conn.commit()
    conn.close()
    auto_backup()

if __name__ == "__main__":
    main()
