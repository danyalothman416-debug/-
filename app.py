import streamlit as st
import json
import os
from datetime import datetime
import hashlib
import base64
from PIL import Image
import io
from fpdf import FPDF
import tempfile
import shutil

# ================================
# 1. ڕێکخستنی ڕووکاری پەڕە
# ================================
st.set_page_config(
    page_title="Dr.Danyal - زیادکردنی پشکنین و دەرمان",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================================
# CSSی تایبەت بۆ دیزاینی جوان
# ================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    h1, h2, h3 {
        color: #2d3748 !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px !important;
    }
    
    .custom-card {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .custom-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 50px rgba(0,0,0,0.15);
    }
    
    .stButton > button {
        border-radius: 12px !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        border: none !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 20px rgba(0,0,0,0.2) !important;
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    }
    
    .stButton > button[kind="secondary"] {
        background: #fc8181 !important;
        color: white !important;
    }
    
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        border-radius: 12px !important;
        border: 2px solid #e2e8f0 !important;
        padding: 0.75rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 1rem !important;
    }
    
    .streamlit-expanderContent {
        background: white !important;
        border-radius: 0 0 12px 12px !important;
        padding: 1.5rem !important;
    }
    
    .metric-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        text-align: center;
    }
    
    .icon-large {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    .stAlert {
        border-radius: 12px !important;
        border: none !important;
    }
    
    .css-1d391kg {
        background: linear-gradient(180deg, #2d3748 0%, #1a202c 100%) !important;
    }
    
    .css-1d391kg .stRadio > div {
        background: rgba(255,255,255,0.1) !important;
        border-radius: 12px !important;
        padding: 0.5rem !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background: rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    
    .edit-form {
        background: #f7fafc;
        border-radius: 12px;
        padding: 1.5rem;
        border: 2px solid #667eea;
        margin: 1rem 0;
    }
    
    .image-container {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    .search-highlight {
        background: #fefcbf;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
    }
    
    .export-button {
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%) !important;
    }
</style>
""", unsafe_allow_html=True)

# ================================
# 2. سیستەمی خەزنکردنی داتا
# ================================
DATA_DIR = "user_data"
IMAGES_DIR = "user_images"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
if not os.path.exists(IMAGES_DIR):
    os.makedirs(IMAGES_DIR)

USERS_FILE = os.path.join(DATA_DIR, "users.json")

def get_user_images_dir(username: str) -> str:
    """مسیری پوشەی وێنەکانی بەکارهێنەر"""
    user_img_dir = os.path.join(IMAGES_DIR, username)
    if not os.path.exists(user_img_dir):
        os.makedirs(user_img_dir)
    return user_img_dir

def save_image(username: str, image_file, item_type: str, item_name: str) -> str:
    """خەزنکردنی وێنە و گەڕاندنەوەی مسیرەکەی"""
    user_img_dir = get_user_images_dir(username)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(c for c in item_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    filename = f"{item_type}_{safe_name}_{timestamp}.png"
    filepath = os.path.join(user_img_dir, filename)
    
    image = Image.open(image_file)
    image.save(filepath, "PNG")
    return filepath

def get_images(username: str, item_type: str, item_name: str) -> list:
    """گەڕاندنەوەی هەموو وێنەکانی پەیوەست بە یەک تۆمار"""
    user_img_dir = get_user_images_dir(username)
    if not os.path.exists(user_img_dir):
        return []
    
    images = []
    safe_name = "".join(c for c in item_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    for filename in os.listdir(user_img_dir):
        if filename.startswith(f"{item_type}_{safe_name}_"):
            filepath = os.path.join(user_img_dir, filename)
            images.append(filepath)
    return images

def delete_image(filepath: str):
    """سڕینەوەی وێنە"""
    if os.path.exists(filepath):
        os.remove(filepath)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def load_users() -> dict:
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_users(users: dict):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

def create_user(username: str, password: str) -> tuple:
    users = load_users()
    
    if username in users:
        return False, "ئەم ناوی بەکارهێنەرییە پێشتر بەکارهێنراوە"
    
    if len(password) < 4:
        return False, "وشەی نهێنی پێویستە لانیکەم ٤ پیت بێت"
    
    users[username] = {
        "password": hash_password(password),
        "created_at": datetime.now().isoformat(),
        "custom_lab_tests": {},
        "custom_drugs": {}
    }
    save_users(users)
    return True, "هەژمارەکەت بە سەرکەوتوویی دروست کرا! 🎉"

def authenticate_user(username: str, password: str) -> bool:
    users = load_users()
    if username in users:
        return users[username]["password"] == hash_password(password)
    return False

def load_user_data(username: str) -> dict:
    users = load_users()
    return users.get(username, {})

def save_user_data(username: str, data: dict):
    users = load_users()
    if username in users:
        users[username].update(data)
        save_users(users)

def auto_save():
    if st.session_state.logged_in:
        save_user_data(st.session_state.username, {
            "custom_lab_tests": st.session_state.custom_lab_tests,
            "custom_drugs": st.session_state.custom_drugs
        })

# ================================
# 3. فەنکشنی گەڕان
# ================================
def search_items(search_term: str, data_dict: dict) -> dict:
    """گەڕان لە نێو داتاکاندا"""
    if not search_term:
        return data_dict
    
    search_term = search_term.lower()
    results = {}
    
    for name, info in data_dict.items():
        # گەڕان لە ناو و بەهاکاندا
        if search_term in name.lower():
            results[name] = info
        else:
            for key, value in info.items():
                if isinstance(value, str) and search_term in value.lower():
                    results[name] = info
                    break
                elif isinstance(value, tuple):
                    for v in value:
                        if isinstance(v, (int, float)) and search_term in str(v).lower():
                            results[name] = info
                            break
    
    return results

def highlight_text(text: str, search_term: str) -> str:
    """هایلایتکردنی تێکستی گەڕان"""
    if not search_term:
        return text
    
    import re
    pattern = re.compile(re.escape(search_term), re.IGNORECASE)
    highlighted = pattern.sub(f'<span class="search-highlight">{search_term}</span>', str(text))
    return highlighted

# ================================
# 4. فەنکشنی هەناردەکردن
# ================================
def create_pdf_report(username: str, lab_tests: dict, drugs: dict):
    """دروستکردنی ڕاپۆرتی PDF"""
    pdf = FPDF()
    pdf.add_page()
    
    # پشتگیری فۆنتی عەرەبی/کوردی
    # تێبینی: بۆ پشتگیری ڕاستەوخۆی فۆنتی کوردی، پێویستە فایلێکی .ttf زیاد بکەیت
    # pdf.add_font('Kurdish', '', 'path/to/font.ttf', uni=True)
    
    # هێدەر
    pdf.set_font('Arial', 'B', 20)
    pdf.cell(0, 15, 'Dr.Danyal - Report', ln=True, align='C')
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'User: {username}', ln=True, align='C')
    pdf.cell(0, 10, f'Date: {datetime.now().strftime("%Y-%m-%d %H:%M")}', ln=True, align='C')
    pdf.ln(10)
    
    # بەشی پشکنینەکان
    if lab_tests:
        pdf.set_font('Arial', 'B', 16)
        pdf.set_fill_color(102, 126, 234)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 12, '  Lab Tests', ln=True, fill=True)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(5)
        
        for name, info in lab_tests.items():
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, f'Test: {name}', ln=True)
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 6, f'  Group: {info.get("group", "N/A")}', ln=True)
            pdf.cell(0, 6, f'  Unit: {info.get("unit", "N/A")}', ln=True)
            normal_range = info.get('normal_range', (0, 0))
            pdf.cell(0, 6, f'  Normal Range: {normal_range[0]} - {normal_range[1]}', ln=True)
            pdf.cell(0, 6, f'  Machine: {info.get("machine", "N/A")}', ln=True)
            pdf.ln(3)
    
    # بەشی دەرمانەکان
    if drugs:
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 16)
        pdf.set_fill_color(102, 126, 234)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 12, '  Drugs', ln=True, fill=True)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(5)
        
        for name, info in drugs.items():
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, f'Drug: {name}', ln=True)
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 6, f'  Dose: {info.get("dose", "N/A")}', ln=True)
            pdf.cell(0, 6, f'  Mechanism: {info.get("mechanism", "N/A")}', ln=True)
            pdf.cell(0, 6, f'  Side Effects: {info.get("side_effects", "N/A")}', ln=True)
            pdf.ln(3)
    
    # پێگە
    pdf.ln(10)
    pdf.set_font('Arial', 'I', 8)
    pdf.cell(0, 10, f'Generated by Dr.Danyal App - {datetime.now().strftime("%Y-%m-%d %H:%M")}', ln=True, align='C')
    
    # خەزنکردنی PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        pdf.output(tmp.name)
        return tmp.name

def create_excel_report(username: str, lab_tests: dict, drugs: dict) -> str:
    """دروستکردنی ڕاپۆرتی CSV (Excel compatible)"""
    import csv
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='w', encoding='utf-8') as tmp:
        writer = csv.writer(tmp)
        
        writer.writerow(['Dr.Danyal - Report'])
        writer.writerow([f'User: {username}'])
        writer.writerow([f'Date: {datetime.now().strftime("%Y-%m-%d %H:%M")}'])
        writer.writerow([])
        
        if lab_tests:
            writer.writerow(['LAB TESTS'])
            writer.writerow(['Name', 'Group', 'Unit', 'Normal Low', 'Normal High', 'Machine', 'Description'])
            for name, info in lab_tests.items():
                normal_range = info.get('normal_range', (0, 0))
                writer.writerow([
                    name,
                    info.get('group', ''),
                    info.get('unit', ''),
                    normal_range[0],
                    normal_range[1],
                    info.get('machine', ''),
                    info.get('description', '')
                ])
        
        writer.writerow([])
        
        if drugs:
            writer.writerow(['DRUGS'])
            writer.writerow(['Name', 'Dose', 'Mechanism', 'Side Effects', 'Contraindications', 'Description'])
            for name, info in drugs.items():
                writer.writerow([
                    name,
                    info.get('dose', ''),
                    info.get('mechanism', ''),
                    info.get('side_effects', ''),
                    info.get('contraindications', ''),
                    info.get('description', '')
                ])
        
        return tmp.name

# ================================
# 5. دەستپێکردنی ستەیتەکان
# ================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'custom_lab_tests' not in st.session_state:
    st.session_state.custom_lab_tests = {}
if 'custom_drugs' not in st.session_state:
    st.session_state.custom_drugs = {}
if 'editing_lab' not in st.session_state:
    st.session_state.editing_lab = None
if 'editing_drug' not in st.session_state:
    st.session_state.editing_drug = None
if 'search_term' not in st.session_state:
    st.session_state.search_term = ""
if 'show_search' not in st.session_state:
    st.session_state.show_search = False

# ================================
# 6. پەڕەی لۆگین
# ================================
if not st.session_state.logged_in:
    st.markdown("<div style='text-align: center; padding: 2rem;'>", unsafe_allow_html=True)
    st.markdown("<h1 style='color: white; font-size: 3rem;'>🩺 Dr.Danyal</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: rgba(255,255,255,0.8); font-size: 1.2rem;'>سیستەمی بەڕێوەبردنی پشکنین و دەرمان</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["🚪 چوونە ژوورەوە", "📝 دروستکردنی هەژمار"])
        
        with tab1:
            with st.form("login_form"):
                login_username = st.text_input("👤 ناوی بەکارهێنەری", placeholder="ناوی بەکارهێنەری خۆت بنووسە")
                login_password = st.text_input("🔒 وشەی نهێنی", type="password", placeholder="وشەی نهێنی خۆت بنووسە")
                login_submit = st.form_submit_button("🚪 چوونە ژوورەوە", use_container_width=True)
                
                if login_submit:
                    if authenticate_user(login_username, login_password):
                        st.session_state.logged_in = True
                        st.session_state.username = login_username
                        user_data = load_user_data(login_username)
                        st.session_state.custom_lab_tests = user_data.get("custom_lab_tests", {})
                        st.session_state.custom_drugs = user_data.get("custom_drugs", {})
                        st.success(f"بەخێربێیت {login_username}! 🎉")
                        st.rerun()
                    else:
                        st.error("❌ ناوی بەکارهێنەری یان وشەی نهێنی هەڵەیە")
        
        with tab2:
            with st.form("register_form"):
                new_username = st.text_input("👤 ناوی بەکارهێنەری نوێ", placeholder="ناوی بەکارهێنەری نوێ بنووسە")
                new_password = st.text_input("🔒 وشەی نهێنی", type="password", placeholder="وشەی نهێنی (لانیکەم ٤ پیت)")
                new_password_confirm = st.text_input("🔒 دووبارە وشەی نهێنی", type="password", placeholder="وشەی نهێنی دووبارە بنووسە")
                register_submit = st.form_submit_button("📝 دروستکردنی هەژمار", use_container_width=True)
                
                if register_submit:
                    if not new_username or not new_password:
                        st.error("❌ تکایە هەموو خانەکان پڕ بکەرەوە")
                    elif new_password != new_password_confirm:
                        st.error("❌ وشەی نهێنی یەک ناگرنەوە")
                    else:
                        success, message = create_user(new_username, new_password)
                        if success:
                            st.success(f"✅ {message}")
                            st.balloons()
                        else:
                            st.error(f"❌ {message}")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.stop()

# ================================
# 7. سایدبار
# ================================
with st.sidebar:
    st.markdown(f"""
    <div style='text-align: center; padding: 1rem;'>
        <div style='font-size: 3rem; margin-bottom: 0.5rem;'>🩺</div>
        <h3 style='color: white; margin: 0;'>Dr.Danyal</h3>
        <p style='color: rgba(255,255,255,0.6); font-size: 0.9rem;'>سیستەمی تەندروستی</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown(f"""
    <div style='background: rgba(255,255,255,0.1); border-radius: 12px; padding: 1rem; margin-bottom: 1rem;'>
        <div style='display: flex; align-items: center; gap: 0.5rem;'>
            <div style='background: #667eea; border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center;'>
                <span style='color: white; font-weight: bold;'>👤</span>
            </div>
            <div>
                <p style='color: white; margin: 0; font-weight: 600;'>{st.session_state.username}</p>
                <p style='color: rgba(255,255,255,0.6); margin: 0; font-size: 0.8rem;'>بەکارهێنەر</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    page = st.radio(
        "📋 بەشەکان:",
        [
            "🏠 داشبۆرد",
            "🔬 زیادکردنی پشکنین",
            "💊 زیادکردنی دەرمان",
            "📤 هەناردەکردن"
        ],
        index=0,
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    if st.button("🚪 چوونە دەرەوە", use_container_width=True):
        auto_save()
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.custom_lab_tests = {}
        st.session_state.custom_drugs = {}
        st.rerun()

# ================================
# 8. کۆمپۆنێنتی گەڕان
# ================================
def render_search_bar(search_key: str):
    """ڕێندەرکردنی باری گەڕان"""
    col1, col2 = st.columns([4, 1])
    with col1:
        search_term = st.text_input(
            "🔍 گەڕان...",
            placeholder="ناو، گروپ، یەکە، یان هەر زانیارییەک...",
            key=f"search_{search_key}",
            value=st.session_state.search_term,
            label_visibility="collapsed"
        )
    with col2:
        if st.button("❌ ڕیسێت", key=f"reset_search_{search_key}"):
            st.session_state.search_term = ""
            st.rerun()
    
    if search_term:
        st.session_state.search_term = search_term
    
    return st.session_state.search_term

# ================================
# 9. بەشی داشبۆرد
# ================================
if page == "🏠 داشبۆرد":
    st.markdown("<h2 style='color: white;'>🏠 داشبۆرد</h2>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class='custom-card' style='text-align: center;'>
        <div class='icon-large'>👋</div>
        <h3>بەخێربێیت {st.session_state.username}!</h3>
        <p style='color: #718096;'>ئەمە داشبۆردی تایبەتی تۆیە. دەتوانیت پشکنین و دەرمانەکانت لێرە بەڕێوەببەیت.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class='metric-card'>
            <div class='icon-large'>📊</div>
            <h2 style='color: #667eea;'>{}</h2>
            <p style='color: #718096;'>پشکنینی کەسی</p>
        </div>
        """.format(len(st.session_state.custom_lab_tests)), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='metric-card'>
            <div class='icon-large'>💊</div>
            <h2 style='color: #667eea;'>{}</h2>
            <p style='color: #718096;'>دەرمانی کەسی</p>
        </div>
        """.format(len(st.session_state.custom_drugs)), unsafe_allow_html=True)
    
    with col3:
        total_images = 0
        user_img_dir = get_user_images_dir(st.session_state.username)
        if os.path.exists(user_img_dir):
            total_images = len([f for f in os.listdir(user_img_dir) if f.endswith('.png')])
        st.markdown("""
        <div class='metric-card'>
            <div class='icon-large'>📸</div>
            <h2 style='color: #667eea;'>{}</h2>
            <p style='color: #718096;'>وێنە</p>
        </div>
        """.format(total_images), unsafe_allow_html=True)
    
    if len(st.session_state.custom_lab_tests) == 0 and len(st.session_state.custom_drugs) == 0:
        st.info("💡 بچۆ بۆ بەشی 'زیادکردنی پشکنین' یان 'زیادکردنی دەرمان' بۆ زیادکردنی تۆمارە تایبەتییەکانی خۆت.")

# ================================
# 10. بەشی پشکنین
# ================================
elif page == "🔬 زیادکردنی پشکنین":
    st.markdown("<h2 style='color: white;'>🔬 زیادکردنی پشکنینی تایبەت</h2>", unsafe_allow_html=True)
    
    # گەڕان
    search_term = render_search_bar("lab")
    
    # فلتەرکردنی داتاکان بەپێی گەڕان
    filtered_labs = search_items(search_term, st.session_state.custom_lab_tests)
    
    if search_term:
        st.markdown(f"<p style='color: rgba(255,255,255,0.8);'>🔍 ئەنجامی گەڕان بۆ: <b>{search_term}</b> - {len(filtered_labs)} ئەنجام</p>", unsafe_allow_html=True)
    
    # نمایشی پشکنینەکان
    if filtered_labs:
        st.markdown("<h3 style='color: white;'>📋 پشکنینەکان</h3>", unsafe_allow_html=True)
        for name, info in filtered_labs.items():
            # دۆخی دەستکاری
            if st.session_state.editing_lab == name:
                with st.expander(f"✏️ دەستکاری: {name}", expanded=True):
                    st.markdown("<div class='edit-form'>", unsafe_allow_html=True)
                    
                    with st.form(key=f"edit_lab_form_{name}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            edit_lab_group = st.selectbox(
                                "📂 گروپ:",
                                ["گشتی", "خوێن", "بایۆکیمیایی", "دڵ", "هەوکردن", "هۆرمۆن", "میز", "ڤیتامین", "معدن"],
                                index=["گشتی", "خوێن", "بایۆکیمیایی", "دڵ", "هەوکردن", "هۆرمۆن", "میز", "ڤیتامین", "معدن"].index(info.get('group', 'گشتی'))
                            )
                            edit_lab_low = st.number_input("⬇️ نزمترین:", value=float(info.get('normal_range', (0,0))[0]), step=0.1)
                            edit_lab_high = st.number_input("⬆️ بەرزترین:", value=float(info.get('normal_range', (0,0))[1]), step=0.1)
                        
                        with col2:
                            edit_lab_unit = st.text_input("📏 یەکە:", value=info.get('unit', ''))
                            edit_lab_machine = st.text_input("🔬 ئامێر:", value=info.get('machine', ''))
                            edit_lab_desc = st.text_area("📖 تەفسیر:", value=info.get('description', ''), height=100)
                            edit_lab_note = st.text_area("📝 تێبینی:", value=info.get('note', ''), height=100)
                        
                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            save_edit = st.form_submit_button("💾 خەزنکردن", use_container_width=True)
                        with col_cancel:
                            cancel_edit = st.form_submit_button("❌ ڕەتکردنەوە", use_container_width=True)
                        
                        if save_edit:
                            # پاراستنی وێنەکانی پێشوو
                            old_images = info.get('images', [])
                            st.session_state.custom_lab_tests[name] = {
                                "group": edit_lab_group,
                                "normal_range": (edit_lab_low, edit_lab_high),
                                "unit": edit_lab_unit,
                                "description": edit_lab_desc,
                                "machine": edit_lab_machine,
                                "note": edit_lab_note,
                                "images": old_images
                            }
                            auto_save()
                            st.session_state.editing_lab = None
                            st.success("✅ پشکنینەکە نوێ کرایەوە!")
                            st.rerun()
                        
                        if cancel_edit:
                            st.session_state.editing_lab = None
                            st.rerun()
                    
                    st.markdown("</div>", unsafe_allow_html=True)
            else:
                # دۆخی ئاسایی
                with st.expander(f"🔬 {name}"):
                    col1, col2, col3 = st.columns([2.5, 0.5, 1])
                    with col1:
                        st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.markdown(f"**📂 گروپ:** {info.get('group', 'نادیار')}")
                            st.markdown(f"**📏 یەکە:** {info.get('unit', 'نادیار')}")
                            normal_range = info.get('normal_range', (0,0))
                            st.markdown(f"**⬇️ نزمترین:** {normal_range[0]}")
                            st.markdown(f"**⬆️ بەرزترین:** {normal_range[1]}")
                        with col_b:
                            st.markdown(f"**🔬 ئامێر:** {info.get('machine', 'نادیار')}")
                            st.markdown(f"**📖 تەفسیر:** {info.get('description', 'نییە')}")
                            st.markdown(f"**📝 تێبینی:** {info.get('note', 'نییە')}")
                        
                        # نمایشی وێنەکان
                        images = get_images(st.session_state.username, "lab", name)
                        if images:
                            st.markdown("**📸 وێنەکان:**")
                            img_cols = st.columns(min(3, len(images)))
                            for idx, img_path in enumerate(images[:3]):  # تەنها ٣ وێنە پیشان بدە
                                with img_cols[idx % 3]:
                                    try:
                                        st.image(img_path, caption=f"وێنەی {idx+1}", use_column_width=True)
                                        if st.button(f"🗑️ سڕینەوەی وێنە {idx+1}", key=f"del_img_lab_{name}_{idx}"):
                                            delete_image(img_path)
                                            st.rerun()
                                    except:
                                        st.error("وێنەکە نەدۆزرایەوە")
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    with col2:
                        st.write("")
                        if st.button("✏️", key=f"edit_lab_{name}", help="دەستکاری"):
                            st.session_state.editing_lab = name
                            st.rerun()
                        if st.button("📸", key=f"upload_lab_{name}", help="زیادکردنی وێنە"):
                            st.session_state[f"upload_lab_{name}"] = True
                    
                    with col3:
                        st.write("")
                        if st.button("🗑️", key=f"del_lab_{name}", help="سڕینەوە"):
                            # سڕینەوەی وێنەکانیش
                            images = get_images(st.session_state.username, "lab", name)
                            for img in images:
                                delete_image(img)
                            del st.session_state.custom_lab_tests[name]
                            auto_save()
                            st.rerun()
                    
                    # فۆرمی بارکردنی وێنە
                    if st.session_state.get(f"upload_lab_{name}", False):
                        st.markdown("<div class='edit-form'>", unsafe_allow_html=True)
                        st.markdown("### 📸 بارکردنی وێنە")
                        uploaded_file = st.file_uploader(
                            "وێنەی پشکنینەکە هەڵبژێرە",
                            type=['png', 'jpg', 'jpeg'],
                            key=f"file_lab_{name}"
                        )
                        col_up, col_close = st.columns(2)
                        with col_up:
                            if uploaded_file and st.button("📤 بارکردن", key=f"upload_btn_lab_{name}"):
                                save_image(st.session_state.username, uploaded_file, "lab", name)
                                st.session_state[f"upload_lab_{name}"] = False
                                st.success("✅ وێنەکە زیاد کرا!")
                                st.rerun()
                        with col_close:
                            if st.button("❌ داخستن", key=f"close_upload_lab_{name}"):
                                st.session_state[f"upload_lab_{name}"] = False
                                st.rerun()
                        st.markdown("</div>", unsafe_allow_html=True)
    
    # فۆرمی زیادکردنی پشکنینی نوێ
    st.markdown("---")
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    st.markdown("<h3>➕ پشکنینێکی نوێ زیاد بکە</h3>", unsafe_allow_html=True)
    
    with st.form("add_lab_test_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            new_lab_name = st.text_input("📝 ناوی پشکنین:", placeholder="وەک: Vitamin D")
            new_lab_group = st.selectbox("📂 گروپ:", ["گشتی", "خوێن", "بایۆکیمیایی", "دڵ", "هەوکردن", "هۆرمۆن", "میز", "ڤیتامین", "معدن"])
            new_lab_low = st.number_input("⬇️ نزمترین:", value=0.0, step=0.1)
            new_lab_high = st.number_input("⬆️ بەرزترین:", value=10.0, step=0.1)
        
        with col2:
            new_lab_unit = st.text_input("📏 یەکە:", placeholder="mg/dL")
            new_lab_machine = st.text_input("🔬 ئامێر:", placeholder="Roche Cobas c502")
            new_lab_desc = st.text_area("📖 تەفسیر:", height=100)
            new_lab_note = st.text_area("📝 تێبینی:", height=100)
        
        submitted = st.form_submit_button("✅ زیاد بکە", use_container_width=True)
        
        if submitted:
            if not new_lab_name:
                st.error("❌ تکایە ناوی پشکنین بنووسە")
            elif new_lab_name in st.session_state.custom_lab_tests:
                st.error(f"❌ پشکنینی '{new_lab_name}' پێشتر زیاد کراوە")
            else:
                st.session_state.custom_lab_tests[new_lab_name] = {
                    "group": new_lab_group,
                    "normal_range": (new_lab_low, new_lab_high),
                    "unit": new_lab_unit,
                    "description": new_lab_desc,
                    "machine": new_lab_machine,
                    "note": new_lab_note,
                    "images": []
                }
                auto_save()
                st.success(f"✅ پشکنینی '{new_lab_name}' زیاد کرا!")
                st.balloons()
                st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# ================================
# 11. بەشی دەرمان
# ================================
elif page == "💊 زیادکردنی دەرمان":
    st.markdown("<h2 style='color: white;'>💊 زیادکردنی دەرمانی تایبەت</h2>", unsafe_allow_html=True)
    
    # گەڕان
    search_term = render_search_bar("drug")
    filtered_drugs = search_items(search_term, st.session_state.custom_drugs)
    
    if search_term:
        st.markdown(f"<p style='color: rgba(255,255,255,0.8);'>🔍 ئەنجامی گەڕان بۆ: <b>{search_term}</b> - {len(filtered_drugs)} ئەنجام</p>", unsafe_allow_html=True)
    
    if filtered_drugs:
        st.markdown("<h3 style='color: white;'>📋 دەرمانەکان</h3>", unsafe_allow_html=True)
        for name, info in filtered_drugs.items():
            if st.session_state.editing_drug == name:
                with st.expander(f"✏️ دەستکاری: {name}", expanded=True):
                    st.markdown("<div class='edit-form'>", unsafe_allow_html=True)
                    
                    with st.form(key=f"edit_drug_form_{name}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            edit_drug_dose = st.text_input("💊 ڕێژە:", value=info.get('dose', ''))
                            edit_drug_mech = st.text_input("⚙️ میکانیزم:", value=info.get('mechanism', ''))
                            edit_drug_effect = st.text_input("⚠️ کاریگەری لاوەکی:", value=info.get('side_effects', ''))
                        
                        with col2:
                            edit_drug_contra = st.text_input("🚫 پێچەوانە:", value=info.get('contraindications', ''))
                            edit_drug_desc = st.text_area("📖 وەسف:", value=info.get('description', ''), height=100)
                            edit_drug_why = st.text_area("🎯 بۆچی:", value=info.get('purpose', ''), height=100)
                            edit_drug_note = st.text_area("📝 تێبینی:", value=info.get('note', ''), height=100)
                        
                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            save_edit = st.form_submit_button("💾 خەزنکردن", use_container_width=True)
                        with col_cancel:
                            cancel_edit = st.form_submit_button("❌ ڕەتکردنەوە", use_container_width=True)
                        
                        if save_edit:
                            old_images = info.get('images', [])
                            st.session_state.custom_drugs[name] = {
                                "dose": edit_drug_dose,
                                "mechanism": edit_drug_mech,
                                "side_effects": edit_drug_effect,
                                "contraindications": edit_drug_contra,
                                "description": edit_drug_desc,
                                "purpose": edit_drug_why,
                                "note": edit_drug_note,
                                "images": old_images
                            }
                            auto_save()
                            st.session_state.editing_drug = None
                            st.success("✅ دەرمانەکە نوێ کرایەوە!")
                            st.rerun()
                        
                        if cancel_edit:
                            st.session_state.editing_drug = None
                            st.rerun()
                    
                    st.markdown("</div>", unsafe_allow_html=True)
            else:
                with st.expander(f"💊 {name}"):
                    col1, col2, col3 = st.columns([2.5, 0.5, 1])
                    with col1:
                        st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.markdown(f"**💊 ڕێژە:** {info.get('dose', 'نادیار')}")
                            st.markdown(f"**⚙️ میکانیزم:** {info.get('mechanism', 'نادیار')}")
                            st.markdown(f"**⚠️ کاریگەری لاوەکی:** {info.get('side_effects', 'نییە')}")
                        with col_b:
                            st.markdown(f"**🚫 پێچەوانە:** {info.get('contraindications', 'نییە')}")
                            st.markdown(f"**🎯 بۆچی:** {info.get('purpose', 'نادیار')}")
                            st.markdown(f"**📝 تێبینی:** {info.get('note', 'نییە')}")
                        
                        images = get_images(st.session_state.username, "drug", name)
                        if images:
                            st.markdown("**📸 وێنەکان:**")
                            img_cols = st.columns(min(3, len(images)))
                            for idx, img_path in enumerate(images[:3]):
                                with img_cols[idx % 3]:
                                    try:
                                        st.image(img_path, caption=f"وێنەی {idx+1}", use_column_width=True)
                                        if st.button(f"🗑️ سڕینەوەی وێنە {idx+1}", key=f"del_img_drug_{name}_{idx}"):
                                            delete_image(img_path)
                                            st.rerun()
                                    except:
                                        st.error("وێنەکە نەدۆزرایەوە")
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    with col2:
                        st.write("")
                        if st.button("✏️", key=f"edit_drug_{name}", help="دەستکاری"):
                            st.session_state.editing_drug = name
                            st.rerun()
                        if st.button("📸", key=f"upload_drug_{name}", help="زیادکردنی وێنە"):
                            st.session_state[f"upload_drug_{name}"] = True
                    
                    with col3:
                        st.write("")
                        if st.button("🗑️", key=f"del_drug_{name}", help="سڕینەوە"):
                            images = get_images(st.session_state.username, "drug", name)
                            for img in images:
                                delete_image(img)
                            del st.session_state.custom_drugs[name]
                            auto_save()
                            st.rerun()
                    
                    if st.session_state.get(f"upload_drug_{name}", False):
                        st.markdown("<div class='edit-form'>", unsafe_allow_html=True)
                        st.markdown("### 📸 بارکردنی وێنە")
                        uploaded_file = st.file_uploader(
                            "وێنەی دەرمانەکە هەڵبژێرە",
                            type=['png', 'jpg', 'jpeg'],
                            key=f"file_drug_{name}"
                        )
                        col_up, col_close = st.columns(2)
                        with col_up:
                            if uploaded_file and st.button("📤 بارکردن", key=f"upload_btn_drug_{name}"):
                                save_image(st.session_state.username, uploaded_file, "drug", name)
                                st.session_state[f"upload_drug_{name}"] = False
                                st.success("✅ وێنەکە زیاد کرا!")
                                st.rerun()
                        with col_close:
                            if st.button("❌ داخستن", key=f"close_upload_drug_{name}"):
                                st.session_state[f"upload_drug_{name}"] = False
                                st.rerun()
                        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    st.markdown("<h3>➕ دەرمانێکی نوێ زیاد بکە</h3>", unsafe_allow_html=True)
    
    with st.form("add_drug_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            new_drug_name = st.text_input("📝 ناوی دەرمان:", placeholder="وەک: Atorvastatin")
            new_drug_dose = st.text_input("💊 ڕێژە:", placeholder="20mg")
            new_drug_mech = st.text_input("⚙️ میکانیزم:", placeholder="HMG-CoA reductase inhibitor")
            new_drug_effect = st.text_input("⚠️ کاریگەری لاوەکی:", placeholder="ئازاری ماسوولکە")
        
        with col2:
            new_drug_contra = st.text_input("🚫 پێچەوانە:", placeholder="نەخۆشی جگەر")
            new_drug_desc = st.text_area("📖 وەسف:", height=100)
            new_drug_why = st.text_area("🎯 بۆچی:", height=100)
            new_drug_note = st.text_area("📝 تێبینی:", height=100)
        
        submitted = st.form_submit_button("✅ زیاد بکە", use_container_width=True)
        
        if submitted:
            if not new_drug_name:
                st.error("❌ تکایە ناوی دەرمان بنووسە")
            elif new_drug_name in st.session_state.custom_drugs:
                st.error(f"❌ دەرمانی '{new_drug_name}' پێشتر زیاد کراوە")
            else:
                st.session_state.custom_drugs[new_drug_name] = {
                    "dose": new_drug_dose,
                    "mechanism": new_drug_mech,
                    "side_effects": new_drug_effect,
                    "contraindications": new_drug_contra,
                    "description": new_drug_desc,
                    "purpose": new_drug_why,
                    "note": new_drug_note,
                    "images": []
                }
                auto_save()
                st.success(f"✅ دەرمانی '{new_drug_name}' زیاد کرا!")
                st.balloons()
                st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# ================================
# 12. بەشی هەناردەکردن
# ================================
elif page == "📤 هەناردەکردن":
    st.markdown("<h2 style='color: white;'>📤 هەناردەکردنی داتا</h2>", unsafe_allow_html=True)
    
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    st.markdown("### 📋 هەناردەکردنی ڕاپۆرت")
    st.markdown("داتاکانت بە شێوازی PDF یان Excel هەناردە بکە بۆ چاپکردن یان ناردن بۆ پزیشک.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📄 هەناردە بە PDF")
        if st.button("🖨️ دروستکردنی PDF", use_container_width=True):
            try:
                # گۆڕینی کلیلەکان بۆ ئینگلیزی بۆ PDF
                lab_tests_eng = {}
                for name, info in st.session_state.custom_lab_tests.items():
                    lab_tests_eng[name] = {
                        "group": info.get("group", ""),
                        "normal_range": info.get("normal_range", (0,0)),
                        "unit": info.get("unit", ""),
                        "machine": info.get("machine", ""),
                        "description": info.get("description", "")
                    }
                
                drugs_eng = {}
                for name, info in st.session_state.custom_drugs.items():
                    drugs_eng[name] = {
                        "dose": info.get("dose", ""),
                        "mechanism": info.get("mechanism", ""),
                        "side_effects": info.get("side_effects", ""),
                        "contraindications": info.get("contraindications", ""),
                        "description": info.get("description", "")
                    }
                
                pdf_path = create_pdf_report(st.session_state.username, lab_tests_eng, drugs_eng)
                
                with open(pdf_path, 'rb') as f:
                    pdf_bytes = f.read()
                
                st.download_button(
                    label="📥 دابەزاندنی PDF",
                    data=pdf_bytes,
                    file_name=f"DrDanyal_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                
                os.unlink(pdf_path)
            except Exception as e:
                st.warning("⚠️ بۆ دروستکردنی PDF پێویستت بە کتێبخانەی fpdf هەیە. تکایە ئەم کۆدە جێبەجێ بکە: pip install fpdf")
                st.info("💡 یان دەتوانیت Excel بەکاربهێنیت لە خوارەوە")
    
    with col2:
        st.markdown("#### 📊 هەناردە بە Excel (CSV)")
        if st.button("📈 دروستکردنی Excel", use_container_width=True):
            try:
                lab_tests_eng = {}
                for name, info in st.session_state.custom_lab_tests.items():
                    lab_tests_eng[name] = {
                        "group": info.get("group", ""),
                        "normal_range": info.get("normal_range", (0,0)),
                        "unit": info.get("unit", ""),
                        "machine": info.get("machine", ""),
                        "description": info.get("description", "")
                    }
                
                drugs_eng = {}
                for name, info in st.session_state.custom_drugs.items():
                    drugs_eng[name] = {
                        "dose": info.get("dose", ""),
                        "mechanism": info.get("mechanism", ""),
                        "side_effects": info.get("side_effects", ""),
                        "contraindications": info.get("contraindications", ""),
                        "description": info.get("description", "")
                    }
                
                csv_path = create_excel_report(st.session_state.username, lab_tests_eng, drugs_eng)
                
                with open(csv_path, 'r', encoding='utf-8') as f:
                    csv_bytes = f.read()
                
                st.download_button(
                    label="📥 دابەزاندنی Excel (CSV)",
                    data=csv_bytes,
                    file_name=f"DrDanyal_Report_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                
                os.unlink(csv_path)
            except Exception as e:
                st.error(f"❌ هەڵەیەک ڕوویدا: {e}")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # پیشاندانی ئاماری هەناردەکردن
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    st.markdown("### 📊 ئاماری داتاکانت")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📊 پشکنین", len(st.session_state.custom_lab_tests))
    with col2:
        st.metric("💊 دەرمان", len(st.session_state.custom_drugs))
    with col3:
        total_images = len([f for f in os.listdir(get_user_images_dir(st.session_state.username)) if f.endswith('.png')]) if os.path.exists(get_user_images_dir(st.session_state.username)) else 0
        st.metric("📸 وێنە", total_images)
    
    st.markdown("</div>", unsafe_allow_html=True)

# ================================
# 13. فووەتەر
# ================================
st.markdown("---")
st.markdown(f"""
<div style='text-align:center;padding:20px;background:rgba(255,255,255,0.1);border-radius:15px;color:white;margin-top:2rem;'>
    <p style='font-size:1.1rem;font-weight:600;'>🩺 Dr.Danyal - زیادکردنی پشکنین و دەرمان</p>
    <p style='font-size:0.9rem;opacity:0.8;'>بەکارهێنەر: {st.session_state.username} | داتاکانت بۆ هەمیشە خەزن دەکرێن</p>
</div>
""", unsafe_allow_html=True)
