import streamlit as st
import json
import os
from datetime import datetime

# ================================
# 1. ڕێکخستنی ڕووکاری پەڕە (بەشێکی کورتی CSS بۆ باشترکردنی دیمەن)
# ================================
st.set_page_config(
    page_title="Dr.Danyal - زیادکردنی پشکنین و دەرمان",
    page_icon="🩺",
    layout="wide"
)

# ================================
# 2. سیستەمی خەزنکردنی داتا لە JSON
# ================================
DATA_DIR = "user_data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

USERS_FILE = os.path.join(DATA_DIR, "users.json")

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def load_users() -> dict:
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_users(users: dict):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

def create_user(username: str, password: str) -> bool:
    users = load_users()
    if username in users:
        return False
    users[username] = {
        "password": hash_password(password),
        "created_at": datetime.now().isoformat(),
        "custom_lab_tests": {},
        "custom_drugs": {}
    }
    save_users(users)
    return True

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
    """خەزنکردنی خۆکارانەی داتای بەکارهێنەر"""
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
    st.markdown("## 🔐 چوونە ژوورەوە یان دروستکردنی هەژمار")
    
    tab1, tab2 = st.tabs(["چوونە ژوورەوە", "دروستکردنی هەژمار"])
    
    with tab1:
        with st.form("login_form"):
            login_username = st.text_input("👤 ناوی بەکارهێنەری")
            login_password = st.text_input("🔒 وشەی نهێنی", type="password")
            login_submit = st.form_submit_button("🚪 چوونە ژوورەوە")
            
            if login_submit:
                if authenticate_user(login_username, login_password):
                    st.session_state.logged_in = True
                    st.session_state.username = login_username
                    user_data = load_user_data(login_username)
                    st.session_state.custom_lab_tests = user_data.get("custom_lab_tests", {})
                    st.session_state.custom_drugs = user_data.get("custom_drugs", {})
                    st.success(f"بەخێربێیت {login_username}!")
                    st.rerun()
                else:
                    st.error("❌ ناوی بەکارهێنەری یان وشەی نهێنی هەڵەیە")
    
    with tab2:
        with st.form("register_form"):
            new_username = st.text_input("👤 ناوی بەکارهێنەری نوێ")
            new_password = st.text_input("🔒 وشەی نهێنی", type="password")
            new_password_confirm = st.text_input("🔒 دووبارە وشەی نهێنی", type="password")
            register_submit = st.form_submit_button("📝 دروستکردنی هەژمار")
            
            if register_submit:
                if not new_username or not new_password:
                    st.error("تکایە هەموو خانەکان پڕ بکەرەوە")
                elif new_password != new_password_confirm:
                    st.error("وشەی نهێنی یەک ناگرنەوە")
                elif len(new_password) < 4:
                    st.error("وشەی نهێنی پێویستە لانیکەم ٤ پیت بێت")
                else:
                    if create_user(new_username, new_password):
                        st.success("✅ هەژمارەکەت بە سەرکەوتوویی دروست کرا!")
                    else:
                        st.error("❌ ئەم ناوی بەکارهێنەرییە پێشتر بەکارهێنراوە")
    st.stop()

# ================================
# 5. سایدبار بۆ گەیشتن بە بەشەکان
# ================================
with st.sidebar:
    st.markdown(f"**👤 بەکارهێنەر:** {st.session_state.username}")
    st.markdown("---")
    
    page = st.radio(
        "📋 بەشەکان:",
        [
            "🏠 داشبۆرد",
            "🔬 زیادکردنی پشکنین",
            "💊 زیادکردنی دەرمان"
        ],
        index=0
    )
    
    if st.button("🚪 چوونە دەرەوە"):
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
    st.markdown("## 🏠 داشبۆرد")
    st.markdown(f"**بەخێربێیت {st.session_state.username}!**")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📊 پشکنینە کەسییەکان", len(st.session_state.custom_lab_tests))
    with col2:
        st.metric("💊 دەرمانە کەسییەکان", len(st.session_state.custom_drugs))
    
    st.info("بچۆ بۆ بەشی 'زیادکردنی پشکنین' یان 'زیادکردنی دەرمان' بۆ زیادکردنی تۆمارە تایبەتییەکانی خۆت.")

# ================================
# 7. بەشی زیادکردنی پشکنین
# ================================
elif page == "🔬 زیادکردنی پشکنین":
    st.markdown("## 🔬 زیادکردنی پشکنینی تایبەت")
    st.markdown("پشکنینێک زیاد بکە کە بۆ هەمیشە بۆ ئەم بەکارهێنەرە خەزن دەکرێت.")
    
    # نمایشی پشکنینە کەسییەکان
    if st.session_state.custom_lab_tests:
        st.markdown("### 📋 پشکنینە کەسییەکان")
        for name, info in st.session_state.custom_lab_tests.items():
            with st.expander(f"🔬 {name}"):
                st.json(info)
                if st.button(f"🗑️ سڕینەوەی {name}", key=f"del_lab_{name}"):
                    del st.session_state.custom_lab_tests[name]
                    auto_save()
                    st.rerun()
    
    st.markdown("---")
    st.markdown("### ➕ پشکنینێکی نوێ زیاد بکە")
    
    with st.form("add_lab_test_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            new_lab_name = st.text_input("📝 ناوی پشکنین:", placeholder="وەک: Vitamin D")
            new_lab_group = st.selectbox("📂 گروپ:", ["گشتی", "خوێن", "بایۆکیمیایی", "دڵ", "هەوکردن", "هۆرمۆن", "میز", "ڤیتامین", "معدن"])
            new_lab_low = st.number_input("⬇️ نزمترین ڕێژەی نۆرماڵ:", value=0.0)
            new_lab_high = st.number_input("⬆️ بەرزترین ڕێژەی نۆرماڵ:", value=10.0)
        
        with col2:
            new_lab_unit = st.text_input("📏 یەکە:", placeholder="mg/dL")
            new_lab_machine = st.text_input("🔬 ئامێر:", placeholder="Roche Cobas c502")
            new_lab_desc = st.text_area("📖 تەفسیر:", placeholder="ڕوونکردنەوەی پشکنینەکە...")
            new_lab_note = st.text_area("📝 تێبینی:", placeholder="تێبینی تایبەتی خۆت...")
        
        submitted = st.form_submit_button("✅ پشکنینەکە زیاد بکە")
        
        if submitted and new_lab_name:
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
            st.rerun()

# ================================
# 8. بەشی زیادکردنی دەرمان
# ================================
elif page == "💊 زیادکردنی دەرمان":
    st.markdown("## 💊 زیادکردنی دەرمانی تایبەت")
    st.markdown("دەرمانێک زیاد بکە کە بۆ هەمیشە بۆ ئەم بەکارهێنەرە خەزن دەکرێت.")
    
    # نمایشی دەرمانە کەسییەکان
    if st.session_state.custom_drugs:
        st.markdown("### 📋 دەرمانە کەسییەکان")
        for name, info in st.session_state.custom_drugs.items():
            with st.expander(f"💊 {name}"):
                st.json(info)
                if st.button(f"🗑️ سڕینەوەی {name}", key=f"del_drug_{name}"):
                    del st.session_state.custom_drugs[name]
                    auto_save()
                    st.rerun()
    
    st.markdown("---")
    st.markdown("### ➕ دەرمانێکی نوێ زیاد بکە")
    
    with st.form("add_drug_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            new_drug_name = st.text_input("📝 ناوی دەرمان:", placeholder="وەک: Atorvastatin")
            new_drug_dose = st.text_input("💊 ڕێژە:", placeholder="20mg")
            new_drug_mech = st.text_input("⚙️ میکانیزم:", placeholder="HMG-CoA reductase inhibitor")
            new_drug_effect = st.text_input("⚠️ کاریگەری لاوەکی:", placeholder="ئازاری ماسوولکە")
        
        with col2:
            new_drug_contra = st.text_input("🚫 پێچەوانە:", placeholder="نەخۆشی جگەر")
            new_drug_desc = st.text_area("📖 وەسف:", placeholder="ڕوونکردنەوەی دەرمانەکە...")
            new_drug_why = st.text_area("🎯 بۆچی:", placeholder="بۆ چارەسەری چی بەکاردێت...")
            new_drug_note = st.text_area("📝 تێبینی:", placeholder="تێبینی تایبەتی خۆت...")
        
        submitted = st.form_submit_button("✅ دەرمانەکە زیاد بکە")
        
        if submitted and new_drug_name:
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
            st.rerun()

# ================================
# 9. فووەتەر
# ================================
st.markdown("---")
st.markdown(f"""
<div style="text-align:center;padding:20px;background:rgba(255,255,255,0.05);border-radius:15px;color:#aaa;">
    <p>🩺 Dr.Danyal - زیادکردنی پشکنین و دەرمان</p>
    <p style="font-size:0.8rem;opacity:0.7;">بەکارهێنەر: {st.session_state.username} | داتاکانت بۆ هەمیشە خەزن دەکرێن</p>
</div>
""", unsafe_allow_html=True)
