import streamlit as st
import json
import os
from datetime import datetime
import hashlib

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
    /* ستایلی گشتی */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* باگراوندی پەڕە */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* هێدەرەکان */
    h1, h2, h3 {
        color: #2d3748 !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px !important;
    }
    
    /* کارتەکان */
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
    
    /* دوگمەکان */
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
    
    /* دوگمەی سەرەکی */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    }
    
    /* دوگمەی مەترسیدار */
    .stButton > button[kind="secondary"] {
        background: #fc8181 !important;
        color: white !important;
    }
    
    /* فۆڕمەکان */
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
    
    /* ئێکسپاندەرەکان */
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
    
    /* مێتریک کارت */
    .metric-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        text-align: center;
    }
    
    /* لۆگین فۆرم */
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        background: white;
        border-radius: 20px;
        padding: 3rem;
        box-shadow: 0 20px 60px rgba(0,0,0,0.15);
    }
    
    /* ئایکۆنەکان */
    .icon-large {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    /* هۆشداری و پەیامەکان */
    .stAlert {
        border-radius: 12px !important;
        border: none !important;
    }
    
    /* سایدبار */
    .css-1d391kg {
        background: linear-gradient(180deg, #2d3748 0%, #1a202c 100%) !important;
    }
    
    .css-1d391kg .stRadio > div {
        background: rgba(255,255,255,0.1) !important;
        border-radius: 12px !important;
        padding: 0.5rem !important;
    }
    
    /* تابەکان */
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
</style>
""", unsafe_allow_html=True)

# ================================
# 2. سیستەمی خەزنکردنی داتا لە JSON
# ================================
DATA_DIR = "user_data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

USERS_FILE = os.path.join(DATA_DIR, "users.json")

def hash_password(password: str) -> str:
    """هێشکردنی وشەی نهێنی بە شێوازی SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users() -> dict:
    """بارکردنی زانیاری بەکارهێنەران لە فایلی JSON"""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_users(users: dict):
    """خەزنکردنی زانیاری بەکارهێنەران لە فایلی JSON"""
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
# 3. دەستپێکردنی ستەیتەکان
# ================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'custom_lab_tests' not in st.session_state:
    st.session_state.custom_lab_tests = {}
if 'custom_drugs' not in st.session_state:
    st.session_state.custom_drugs = {}

# ================================
# 4. پەڕەی لۆگین
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
                col_l1, col_l2 = st.columns([2, 1])
                with col_l1:
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
# 5. سایدبار بۆ گەیشتن بە بەشەکان
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
    
    # پڕۆفایلی بەکارهێنەر
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
    
    # ناڤیگەیشن
    page = st.radio(
        "📋 بەشەکان:",
        [
            "🏠 داشبۆرد",
            "🔬 زیادکردنی پشکنین",
            "💊 زیادکردنی دەرمان"
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
# 6. بەشی داشبۆرد
# ================================
if page == "🏠 داشبۆرد":
    st.markdown("<h2 style='color: white;'>🏠 داشبۆرد</h2>", unsafe_allow_html=True)
    
    # کارتی بەخێربێیت
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
        st.markdown("""
        <div class='metric-card'>
            <div class='icon-large'>📁</div>
            <h2 style='color: #667eea;'>{}</h2>
            <p style='color: #718096;'>کۆی گشتی تۆمارەکان</p>
        </div>
        """.format(len(st.session_state.custom_lab_tests) + len(st.session_state.custom_drugs)), unsafe_allow_html=True)
    
    if len(st.session_state.custom_lab_tests) == 0 and len(st.session_state.custom_drugs) == 0:
        st.info("💡 بچۆ بۆ بەشی 'زیادکردنی پشکنین' یان 'زیادکردنی دەرمان' بۆ زیادکردنی تۆمارە تایبەتییەکانی خۆت.")
    else:
        st.success(f"📊 تۆ {len(st.session_state.custom_lab_tests) + len(st.session_state.custom_drugs)} تۆماری تایبەتیت هەیە!")

# ================================
# 7. بەشی زیادکردنی پشکنین
# ================================
elif page == "🔬 زیادکردنی پشکنین":
    st.markdown("<h2 style='color: white;'>🔬 زیادکردنی پشکنینی تایبەت</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: rgba(255,255,255,0.8);'>پشکنینێک زیاد بکە کە بۆ هەمیشە بۆ ئەم بەکارهێنەرە خەزن دەکرێت.</p>", unsafe_allow_html=True)
    
    # نمایشی پشکنینە کەسییەکان
    if st.session_state.custom_lab_tests:
        st.markdown("<h3 style='color: white;'>📋 پشکنینە کەسییەکان</h3>", unsafe_allow_html=True)
        for name, info in st.session_state.custom_lab_tests.items():
            with st.expander(f"🔬 {name}"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown(f"**📂 گروپ:** {info.get('گروپ', 'نادیار')}")
                        st.markdown(f"**📏 یەکە:** {info.get('یەکە', 'نادیار')}")
                        st.markdown(f"**⬇️ نزمترین:** {info.get('نۆرماڵ', (0,0))[0]}")
                        st.markdown(f"**⬆️ بەرزترین:** {info.get('نۆرماڵ', (0,0))[1]}")
                    with col_b:
                        st.markdown(f"**🔬 ئامێر:** {info.get('ئامێر', 'نادیار')}")
                        st.markdown(f"**📖 تەفسیر:** {info.get('تەفسیر', 'نییە')}")
                        st.markdown(f"**📝 تێبینی:** {info.get('تێبینی', 'نییە')}")
                    st.markdown("</div>", unsafe_allow_html=True)
                with col2:
                    if st.button(f"🗑️ سڕینەوەی {name}", key=f"del_lab_{name}"):
                        del st.session_state.custom_lab_tests[name]
                        auto_save()
                        st.rerun()
    
    st.markdown("---")
    
    # فۆرمی زیادکردن
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    st.markdown("<h3>➕ پشکنینێکی نوێ زیاد بکە</h3>", unsafe_allow_html=True)
    
    with st.form("add_lab_test_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            new_lab_name = st.text_input("📝 ناوی پشکنین:", placeholder="وەک: Vitamin D")
            new_lab_group = st.selectbox("📂 گروپ:", ["گشتی", "خوێن", "بایۆکیمیایی", "دڵ", "هەوکردن", "هۆرمۆن", "میز", "ڤیتامین", "معدن"])
            new_lab_low = st.number_input("⬇️ نزمترین ڕێژەی نۆرماڵ:", value=0.0, step=0.1)
            new_lab_high = st.number_input("⬆️ بەرزترین ڕێژەی نۆرماڵ:", value=10.0, step=0.1)
        
        with col2:
            new_lab_unit = st.text_input("📏 یەکە:", placeholder="mg/dL")
            new_lab_machine = st.text_input("🔬 ئامێر:", placeholder="Roche Cobas c502")
            new_lab_desc = st.text_area("📖 تەفسیر:", placeholder="ڕوونکردنەوەی پشکنینەکە...", height=100)
            new_lab_note = st.text_area("📝 تێبینی:", placeholder="تێبینی تایبەتی خۆت...", height=100)
        
        submitted = st.form_submit_button("✅ پشکنینەکە زیاد بکە", use_container_width=True)
        
        if submitted:
            if not new_lab_name:
                st.error("❌ تکایە ناوی پشکنین بنووسە")
            elif new_lab_name in st.session_state.custom_lab_tests:
                st.error(f"❌ پشکنینی '{new_lab_name}' پێشتر زیاد کراوە")
            else:
                st.session_state.custom_lab_tests[new_lab_name] = {
                    "گروپ": new_lab_group,
                    "نۆرماڵ": (new_lab_low, new_lab_high),
                    "یەکە": new_lab_unit,
                    "تەفسیر": new_lab_desc,
                    "ئامێر": new_lab_machine,
                    "تێبینی": new_lab_note
                }
                auto_save()
                st.success(f"✅ پشکنینی '{new_lab_name}' بە سەرکەوتوویی زیاد کرا!")
                st.balloons()
                st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# ================================
# 8. بەشی زیادکردنی دەرمان
# ================================
elif page == "💊 زیادکردنی دەرمان":
    st.markdown("<h2 style='color: white;'>💊 زیادکردنی دەرمانی تایبەت</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: rgba(255,255,255,0.8);'>دەرمانێک زیاد بکە کە بۆ هەمیشە بۆ ئەم بەکارهێنەرە خەزن دەکرێت.</p>", unsafe_allow_html=True)
    
    # نمایشی دەرمانە کەسییەکان
    if st.session_state.custom_drugs:
        st.markdown("<h3 style='color: white;'>📋 دەرمانە کەسییەکان</h3>", unsafe_allow_html=True)
        for name, info in st.session_state.custom_drugs.items():
            with st.expander(f"💊 {name}"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown(f"**💊 ڕێژە:** {info.get('ڕێژە', 'نادیار')}")
                        st.markdown(f"**⚙️ میکانیزم:** {info.get('میکانیزم', 'نادیار')}")
                        st.markdown(f"**⚠️ کاریگەری لاوەکی:** {info.get('کاریگەری لاوەکی', 'نییە')}")
                    with col_b:
                        st.markdown(f"**🚫 پێچەوانە:** {info.get('پێچەوانە', 'نییە')}")
                        st.markdown(f"**🎯 بۆچی:** {info.get('بۆچی', 'نادیار')}")
                        st.markdown(f"**📝 تێبینی:** {info.get('تێبینی', 'نییە')}")
                    st.markdown("</div>", unsafe_allow_html=True)
                with col2:
                    if st.button(f"🗑️ سڕینەوەی {name}", key=f"del_drug_{name}"):
                        del st.session_state.custom_drugs[name]
                        auto_save()
                        st.rerun()
    
    st.markdown("---")
    
    # فۆرمی زیادکردن
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
            new_drug_desc = st.text_area("📖 وەسف:", placeholder="ڕوونکردنەوەی دەرمانەکە...", height=100)
            new_drug_why = st.text_area("🎯 بۆچی:", placeholder="بۆ چارەسەری چی بەکاردێت...", height=100)
            new_drug_note = st.text_area("📝 تێبینی:", placeholder="تێبینی تایبەتی خۆت...", height=100)
        
        submitted = st.form_submit_button("✅ دەرمانەکە زیاد بکە", use_container_width=True)
        
        if submitted:
            if not new_drug_name:
                st.error("❌ تکایە ناوی دەرمان بنووسە")
            elif new_drug_name in st.session_state.custom_drugs:
                st.error(f"❌ دەرمانی '{new_drug_name}' پێشتر زیاد کراوە")
            else:
                st.session_state.custom_drugs[new_drug_name] = {
                    "ڕێژە": new_drug_dose,
                    "میکانیزم": new_drug_mech,
                    "کاریگەری لاوەکی": new_drug_effect,
                    "پێچەوانە": new_drug_contra,
                    "وەسف": new_drug_desc,
                    "بۆچی": new_drug_why,
                    "تێبینی": new_drug_note
                }
                auto_save()
                st.success(f"✅ دەرمانی '{new_drug_name}' بە سەرکەوتوویی زیاد کرا!")
                st.balloons()
                st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# ================================
# 9. فووەتەر
# ================================
st.markdown("---")
st.markdown(f"""
<div style='text-align:center;padding:20px;background:rgba(255,255,255,0.1);border-radius:15px;color:white;margin-top:2rem;'>
    <p style='font-size:1.1rem;font-weight:600;'>🩺 Dr.Danyal - زیادکردنی پشکنین و دەرمان</p>
    <p style='font-size:0.9rem;opacity:0.8;'>بەکارهێنەر: {st.session_state.username} | داتاکانت بۆ هەمیشە خەزن دەکرێن</p>
</div>
""", unsafe_allow_html=True)
