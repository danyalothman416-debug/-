import streamlit as st
import json
import os
from datetime import datetime
import hashlib
from PIL import Image
from fpdf import FPDF
import tempfile

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
# CSS
# ================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    .stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    
    h1, h2, h3 { color: #2d3748 !important; font-weight: 700 !important; }
    
    .custom-card {
        background: white; border-radius: 20px; padding: 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1); margin-bottom: 1rem;
    }
    
    .stButton > button {
        border-radius: 12px !important; padding: 0.5rem 1.5rem !important;
        font-weight: 600 !important; transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 20px rgba(0,0,0,0.2) !important;
    }
    
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        border-radius: 12px !important; border: 2px solid #e2e8f0 !important;
        padding: 0.75rem !important;
    }
    
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important; border-radius: 12px !important;
        font-weight: 600 !important; padding: 1rem !important;
    }
    
    .streamlit-expanderContent {
        background: white !important; border-radius: 0 0 12px 12px !important;
        padding: 1.5rem !important;
    }
    
    .metric-card {
        background: white; border-radius: 16px; padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08); text-align: center;
    }
    
    .edit-form {
        background: #f7fafc; border-radius: 12px; padding: 1.5rem;
        border: 2px solid #667eea; margin: 1rem 0;
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
    user_img_dir = os.path.join(IMAGES_DIR, username)
    if not os.path.exists(user_img_dir):
        os.makedirs(user_img_dir)
    return user_img_dir

def save_image(username: str, image_file, item_type: str, item_name: str) -> str:
    user_img_dir = get_user_images_dir(username)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(c for c in item_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    filename = f"{item_type}_{safe_name}_{timestamp}.png"
    filepath = os.path.join(user_img_dir, filename)
    image = Image.open(image_file)
    image.save(filepath, "PNG")
    return filepath

def get_images(username: str, item_type: str, item_name: str) -> list:
    user_img_dir = get_user_images_dir(username)
    if not os.path.exists(user_img_dir):
        return []
    images = []
    safe_name = "".join(c for c in item_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    for filename in os.listdir(user_img_dir):
        if filename.startswith(f"{item_type}_{safe_name}_"):
            images.append(os.path.join(user_img_dir, filename))
    return sorted(images, reverse=True)

def delete_image(filepath: str):
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
    return True, "هەژمارەکەت بە سەرکەوتوویی دروست کرا!"

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
    if not search_term:
        return data_dict
    search_term = search_term.lower()
    results = {}
    for name, info in data_dict.items():
        if search_term in name.lower():
            results[name] = info
            continue
        for value in info.values():
            if isinstance(value, str) and search_term in value.lower():
                results[name] = info
                break
            elif isinstance(value, tuple):
                for v in value:
                    if search_term in str(v).lower():
                        results[name] = info
                        break
    return results

# ================================
# 4. فەنکشنی هەناردەکردن
# ================================
def export_to_pdf(username, lab_tests, drugs):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 20)
    pdf.cell(0, 15, 'Dr.Danyal - Report', ln=True, align='C')
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'User: {username}', ln=True, align='C')
    pdf.cell(0, 10, f'Date: {datetime.now().strftime("%Y-%m-%d %H:%M")}', ln=True, align='C')
    pdf.ln(10)
    
    if lab_tests:
        pdf.set_font('Arial', 'B', 16)
        pdf.set_fill_color(102, 126, 234)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 12, '  Lab Tests', ln=True, fill=True)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(5)
        for name, info in lab_tests.items():
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, name, ln=True)
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 6, f'  Group: {info.get("گروپ", "")}', ln=True)
            pdf.cell(0, 6, f'  Unit: {info.get("یەکە", "")}', ln=True)
            normal = info.get('نۆرماڵ', (0, 0))
            pdf.cell(0, 6, f'  Normal Range: {normal[0]} - {normal[1]}', ln=True)
            pdf.cell(0, 6, f'  Machine: {info.get("ئامێر", "")}', ln=True)
            pdf.ln(3)
    
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
            pdf.cell(0, 8, name, ln=True)
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 6, f'  Dose: {info.get("ڕێژە", "")}', ln=True)
            pdf.cell(0, 6, f'  Mechanism: {info.get("میکانیزم", "")}', ln=True)
            pdf.ln(3)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        pdf.output(tmp.name)
        return tmp.name

def export_to_csv(username, lab_tests, drugs):
    import csv
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='w', encoding='utf-8-sig') as tmp:
        writer = csv.writer(tmp)
        writer.writerow(['Dr.Danyal - Report'])
        writer.writerow([f'User: {username}'])
        writer.writerow([f'Date: {datetime.now().strftime("%Y-%m-%d %H:%M")}'])
        writer.writerow([])
        
        if lab_tests:
            writer.writerow(['LAB TESTS'])
            writer.writerow(['Name', 'Group', 'Unit', 'Normal Low', 'Normal High', 'Machine', 'Description', 'Note'])
            for name, info in lab_tests.items():
                normal = info.get('نۆرماڵ', (0, 0))
                writer.writerow([name, info.get('گروپ', ''), info.get('یەکە', ''), normal[0], normal[1], info.get('ئامێر', ''), info.get('تەفسیر', ''), info.get('تێبینی', '')])
            writer.writerow([])
        
        if drugs:
            writer.writerow(['DRUGS'])
            writer.writerow(['Name', 'Dose', 'Mechanism', 'Side Effects', 'Contraindications', 'Description', 'Purpose', 'Note'])
            for name, info in drugs.items():
                writer.writerow([name, info.get('ڕێژە', ''), info.get('میکانیزم', ''), info.get('کاریگەری لاوەکی', ''), info.get('پێچەوانە', ''), info.get('وەسف', ''), info.get('بۆچی', ''), info.get('تێبینی', '')])
        
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
if 'search_lab' not in st.session_state:
    st.session_state.search_lab = ""
if 'search_drug' not in st.session_state:
    st.session_state.search_drug = ""

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
                            st.success(message)
                        else:
                            st.error(message)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.stop()

# ================================
# 7. سایدبار
# ================================
with st.sidebar:
    st.markdown(f"""
    <div style='text-align: center; padding: 1rem;'>
        <div style='font-size: 3rem;'>🩺</div>
        <h3 style='color: white;'>Dr.Danyal</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown(f"""
    <div style='background: rgba(255,255,255,0.1); border-radius: 12px; padding: 1rem;'>
        <p style='color: white; margin: 0;'>👤 {st.session_state.username}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    page = st.radio("📋 بەشەکان:", ["🏠 داشبۆرد", "🔬 پشکنینەکان", "💊 دەرمانەکان", "📤 هەناردەکردن"], index=0, label_visibility="collapsed")
    
    st.markdown("---")
    
    if st.button("🚪 چوونە دەرەوە", use_container_width=True):
        auto_save()
        st.session_state.logged_in = False
        st.rerun()

# ================================
# 8. داشبۆرد
# ================================
if page == "🏠 داشبۆرد":
    st.markdown("<h2 style='color: white;'>🏠 داشبۆرد</h2>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class='custom-card' style='text-align: center;'>
        <h3>بەخێربێیت {st.session_state.username}!</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class='metric-card'>
            <h2 style='color: #667eea;'>{len(st.session_state.custom_lab_tests)}</h2>
            <p>پشکنین</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class='metric-card'>
            <h2 style='color: #667eea;'>{len(st.session_state.custom_drugs)}</h2>
            <p>دەرمان</p>
        </div>
        """, unsafe_allow_html=True)

# ================================
# 9. بەشی پشکنینەکان
# ================================
elif page == "🔬 پشکنینەکان":
    st.markdown("<h2 style='color: white;'>🔬 پشکنینەکان</h2>", unsafe_allow_html=True)
    
    # باری گەڕان
    col_search, col_reset = st.columns([4, 1])
    with col_search:
        search_lab = st.text_input("🔍 گەڕان...", placeholder="گەڕان بەناو پشکنینەکان...", key="search_lab_input", label_visibility="collapsed")
    with col_reset:
        if st.button("❌", key="reset_lab_search", use_container_width=True):
            st.session_state.search_lab = ""
            st.rerun()
    
    if search_lab:
        st.session_state.search_lab = search_lab
    
    filtered_labs = search_items(st.session_state.search_lab, st.session_state.custom_lab_tests)
    
    if st.session_state.search_lab:
        st.info(f"🔍 {len(filtered_labs)} ئەنجام بۆ '{st.session_state.search_lab}'")
    
    # نمایشی پشکنینەکان
    if filtered_labs:
        for name, info in filtered_labs.items():
            if st.session_state.editing_lab == name:
                # دۆخی دەستکاری
                with st.expander(f"✏️ دەستکاری: {name}", expanded=True):
                    st.markdown("<div class='edit-form'>", unsafe_allow_html=True)
                    with st.form(key=f"edit_lab_{name}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            e_group = st.selectbox("گروپ:", ["گشتی", "خوێن", "بایۆکیمیایی", "دڵ", "هەوکردن", "هۆرمۆن", "میز", "ڤیتامین", "معدن"], index=["گشتی", "خوێن", "بایۆکیمیایی", "دڵ", "هەوکردن", "هۆرمۆن", "میز", "ڤیتامین", "معدن"].index(info.get('گروپ', 'گشتی')))
                            e_low = st.number_input("نزمترین:", value=float(info.get('نۆرماڵ', (0,0))[0]), step=0.1)
                            e_high = st.number_input("بەرزترین:", value=float(info.get('نۆرماڵ', (0,0))[1]), step=0.1)
                        with col2:
                            e_unit = st.text_input("یەکە:", value=info.get('یەکە', ''))
                            e_machine = st.text_input("ئامێر:", value=info.get('ئامێر', ''))
                            e_desc = st.text_area("تەفسیر:", value=info.get('تەفسیر', ''))
                            e_note = st.text_area("تێبینی:", value=info.get('تێبینی', ''))
                        
                        c1, c2 = st.columns(2)
                        with c1:
                            if st.form_submit_button("💾 خەزنکردن", use_container_width=True):
                                st.session_state.custom_lab_tests[name] = {"گروپ": e_group, "نۆرماڵ": (e_low, e_high), "یەکە": e_unit, "تەفسیر": e_desc, "ئامێر": e_machine, "تێبینی": e_note}
                                auto_save()
                                st.session_state.editing_lab = None
                                st.rerun()
                        with c2:
                            if st.form_submit_button("❌ ڕەتکردنەوە", use_container_width=True):
                                st.session_state.editing_lab = None
                                st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
            else:
                # دۆخی ئاسایی
                with st.expander(f"🔬 {name}"):
                    c1, c2, c3 = st.columns([2.5, 0.5, 1])
                    with c1:
                        st.markdown(f"**گروپ:** {info.get('گروپ', '')} | **یەکە:** {info.get('یەکە', '')} | **ئامێر:** {info.get('ئامێر', '')}")
                        normal = info.get('نۆرماڵ', (0,0))
                        st.markdown(f"**نۆرماڵ:** {normal[0]} - {normal[1]}")
                        if info.get('تەفسیر'):
                            st.markdown(f"**تەفسیر:** {info['تەفسیر']}")
                        
                        # وێنەکان
                        images = get_images(st.session_state.username, "lab", name)
                        if images:
                            cols = st.columns(min(3, len(images)))
                            for i, img_path in enumerate(images[:3]):
                                with cols[i % 3]:
                                    st.image(img_path, use_column_width=True)
                                    if st.button("🗑️", key=f"del_lab_img_{name}_{i}"):
                                        delete_image(img_path)
                                        st.rerun()
                        
                        # زیادکردنی وێنە
                        uploaded = st.file_uploader("وێنە زیاد بکە", type=['png', 'jpg', 'jpeg'], key=f"upload_lab_{name}", label_visibility="collapsed")
                        if uploaded:
                            save_image(st.session_state.username, uploaded, "lab", name)
                            st.rerun()
                    
                    with c2:
                        if st.button("✏️", key=f"edit_btn_lab_{name}"):
                            st.session_state.editing_lab = name
                            st.rerun()
                    
                    with c3:
                        if st.button("🗑️", key=f"del_btn_lab_{name}"):
                            for img in get_images(st.session_state.username, "lab", name):
                                delete_image(img)
                            del st.session_state.custom_lab_tests[name]
                            auto_save()
                            st.rerun()
    
    # فۆرمی زیادکردن
    st.markdown("---")
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    st.markdown("<h3>➕ پشکنینی نوێ</h3>", unsafe_allow_html=True)
    
    with st.form("add_lab", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("ناوی پشکنین:")
            group = st.selectbox("گروپ:", ["گشتی", "خوێن", "بایۆکیمیایی", "دڵ", "هەوکردن", "هۆرمۆن", "میز", "ڤیتامین", "معدن"])
            low = st.number_input("نزمترین:", value=0.0, step=0.1)
            high = st.number_input("بەرزترین:", value=10.0, step=0.1)
        with c2:
            unit = st.text_input("یەکە:")
            machine = st.text_input("ئامێر:")
            desc = st.text_area("تەفسیر:")
            note = st.text_area("تێبینی:")
        
        if st.form_submit_button("✅ زیاد بکە", use_container_width=True):
            if name and name not in st.session_state.custom_lab_tests:
                st.session_state.custom_lab_tests[name] = {"گروپ": group, "نۆرماڵ": (low, high), "یەکە": unit, "تەفسیر": desc, "ئامێر": machine, "تێبینی": note}
                auto_save()
                st.success(f"✅ '{name}' زیاد کرا!")
                st.rerun()
            else:
                st.error("ناو پێویستە و نابێت دووبارە بێت")
    st.markdown("</div>", unsafe_allow_html=True)

# ================================
# 10. بەشی دەرمانەکان
# ================================
elif page == "💊 دەرمانەکان":
    st.markdown("<h2 style='color: white;'>💊 دەرمانەکان</h2>", unsafe_allow_html=True)
    
    col_search, col_reset = st.columns([4, 1])
    with col_search:
        search_drug = st.text_input("🔍 گەڕان...", placeholder="گەڕان بەناو دەرمانەکان...", key="search_drug_input", label_visibility="collapsed")
    with col_reset:
        if st.button("❌", key="reset_drug_search", use_container_width=True):
            st.session_state.search_drug = ""
            st.rerun()
    
    if search_drug:
        st.session_state.search_drug = search_drug
    
    filtered_drugs = search_items(st.session_state.search_drug, st.session_state.custom_drugs)
    
    if st.session_state.search_drug:
        st.info(f"🔍 {len(filtered_drugs)} ئەنجام بۆ '{st.session_state.search_drug}'")
    
    if filtered_drugs:
        for name, info in filtered_drugs.items():
            if st.session_state.editing_drug == name:
                with st.expander(f"✏️ دەستکاری: {name}", expanded=True):
                    st.markdown("<div class='edit-form'>", unsafe_allow_html=True)
                    with st.form(key=f"edit_drug_{name}"):
                        c1, c2 = st.columns(2)
                        with c1:
                            e_dose = st.text_input("ڕێژە:", value=info.get('ڕێژە', ''))
                            e_mech = st.text_input("میکانیزم:", value=info.get('میکانیزم', ''))
                            e_effect = st.text_input("کاریگەری لاوەکی:", value=info.get('کاریگەری لاوەکی', ''))
                        with c2:
                            e_contra = st.text_input("پێچەوانە:", value=info.get('پێچەوانە', ''))
                            e_desc = st.text_area("وەسف:", value=info.get('وەسف', ''))
                            e_why = st.text_area("بۆچی:", value=info.get('بۆچی', ''))
                            e_note = st.text_area("تێبینی:", value=info.get('تێبینی', ''))
                        
                        c1, c2 = st.columns(2)
                        with c1:
                            if st.form_submit_button("💾 خەزنکردن", use_container_width=True):
                                st.session_state.custom_drugs[name] = {"ڕێژە": e_dose, "میکانیزم": e_mech, "کاریگەری لاوەکی": e_effect, "پێچەوانە": e_contra, "وەسف": e_desc, "بۆچی": e_why, "تێبینی": e_note}
                                auto_save()
                                st.session_state.editing_drug = None
                                st.rerun()
                        with c2:
                            if st.form_submit_button("❌ ڕەتکردنەوە", use_container_width=True):
                                st.session_state.editing_drug = None
                                st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
            else:
                with st.expander(f"💊 {name}"):
                    c1, c2, c3 = st.columns([2.5, 0.5, 1])
                    with c1:
                        st.markdown(f"**ڕێژە:** {info.get('ڕێژە', '')} | **میکانیزم:** {info.get('میکانیزم', '')}")
                        st.markdown(f"**کاریگەری لاوەکی:** {info.get('کاریگەری لاوەکی', '')}")
                        st.markdown(f"**پێچەوانە:** {info.get('پێچەوانە', '')}")
                        
                        images = get_images(st.session_state.username, "drug", name)
                        if images:
                            cols = st.columns(min(3, len(images)))
                            for i, img_path in enumerate(images[:3]):
                                with cols[i % 3]:
                                    st.image(img_path, use_column_width=True)
                                    if st.button("🗑️", key=f"del_drug_img_{name}_{i}"):
                                        delete_image(img_path)
                                        st.rerun()
                        
                        uploaded = st.file_uploader("وێنە زیاد بکە", type=['png', 'jpg', 'jpeg'], key=f"upload_drug_{name}", label_visibility="collapsed")
                        if uploaded:
                            save_image(st.session_state.username, uploaded, "drug", name)
                            st.rerun()
                    
                    with c2:
                        if st.button("✏️", key=f"edit_btn_drug_{name}"):
                            st.session_state.editing_drug = name
                            st.rerun()
                    
                    with c3:
                        if st.button("🗑️", key=f"del_btn_drug_{name}"):
                            for img in get_images(st.session_state.username, "drug", name):
                                delete_image(img)
                            del st.session_state.custom_drugs[name]
                            auto_save()
                            st.rerun()
    
    st.markdown("---")
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    st.markdown("<h3>➕ دەرمانی نوێ</h3>", unsafe_allow_html=True)
    
    with st.form("add_drug", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("ناوی دەرمان:")
            dose = st.text_input("ڕێژە:")
            mech = st.text_input("میکانیزم:")
            effect = st.text_input("کاریگەری لاوەکی:")
        with c2:
            contra = st.text_input("پێچەوانە:")
            desc = st.text_area("وەسف:")
            why = st.text_area("بۆچی:")
            note = st.text_area("تێبینی:")
        
        if st.form_submit_button("✅ زیاد بکە", use_container_width=True):
            if name and name not in st.session_state.custom_drugs:
                st.session_state.custom_drugs[name] = {"ڕێژە": dose, "میکانیزم": mech, "کاریگەری لاوەکی": effect, "پێچەوانە": contra, "وەسف": desc, "بۆچی": why, "تێبینی": note}
                auto_save()
                st.success(f"✅ '{name}' زیاد کرا!")
                st.rerun()
            else:
                st.error("ناو پێویستە و نابێت دووبارە بێت")
    st.markdown("</div>", unsafe_allow_html=True)

# ================================
# 11. بەشی هەناردەکردن
# ================================
elif page == "📤 هەناردەکردن":
    st.markdown("<h2 style='color: white;'>📤 هەناردەکردن</h2>", unsafe_allow_html=True)
    
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 📄 PDF")
        if st.button("دروستکردنی PDF", use_container_width=True):
            try:
                pdf_path = export_to_pdf(st.session_state.username, st.session_state.custom_lab_tests, st.session_state.custom_drugs)
                with open(pdf_path, 'rb') as f:
                    st.download_button("📥 دابەزاندن", f.read(), f"report_{datetime.now().strftime('%Y%m%d')}.pdf", "application/pdf", use_container_width=True)
                os.unlink(pdf_path)
            except Exception as e:
                st.error(f"هەڵە: {e}")
    
    with c2:
        st.markdown("#### 📊 Excel (CSV)")
        if st.button("دروستکردنی Excel", use_container_width=True):
            try:
                csv_path = export_to_csv(st.session_state.username, st.session_state.custom_lab_tests, st.session_state.custom_drugs)
                with open(csv_path, 'r', encoding='utf-8-sig') as f:
                    st.download_button("📥 دابەزاندن", f.read(), f"report_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv", use_container_width=True)
                os.unlink(csv_path)
            except Exception as e:
                st.error(f"هەڵە: {e}")
    
    st.markdown("</div>", unsafe_allow_html=True)

# ================================
# 12. فووەتەر
# ================================
st.markdown("---")
st.markdown(f"""
<div style='text-align:center;padding:20px;background:rgba(255,255,255,0.1);border-radius:15px;color:white;'>
    <p>🩺 Dr.Danyal</p>
    <p style='font-size:0.8rem;opacity:0.7;'> {st.session_state.username}</p>
</div>
""", unsafe_allow_html=True)
