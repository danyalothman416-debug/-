import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import uuid
import json
import plotly.express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
import random
import time

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="سیستەمی شیکاری نەخۆشییەکان - کەرکوک", 
    layout="wide", 
    initial_sidebar_state="collapsed",
    page_icon="🏥"
)

# --- 2. INITIALIZE SESSION STATES ---
def init_session_states():
    defaults = {
        'page': "home",
        'user_email': None,
        'user_role': "patient",
        'user_name': None,
        'user_phone': None,
        'user_id': None,
        'admin_authenticated': False,
        'lang_choice': "کوردی 🇭🇺",
        'doctor_id': None,
        'current_patient_id': None,
        'notifications': [],
        'test_history': [],
        'current_test_id': None,
        'currency': 'IQD',
        'notification_preferences': {'sms': True, 'email': True, 'whatsapp': True},
        'online': True
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_states()

# --- 3. HOSPITAL INFO ---
HOSPITAL_PHONES = ["07801352003", "07721959922"]
HOSPITAL_EMAIL = "hospital@kirkuk-medical.iq"
HOSPITAL_ADDRESS = "کەرکوک، شەقامی سەرەکی، نەخۆشخانەی ناوەندی"
HOSPITAL_WHATSAPP = "https://wa.me/9647801352003"
EMERGENCY_POLICE = "104"
EMERGENCY_AMBULANCE = "122"

# --- 4. MEDICAL DATA ---
BLOOD_TYPES = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
GENDERS = ["نێر", "مێ", "هی تر"]

TEST_TYPES = [
    "پشکنینی خوێن (CBC)",
    "پشکنینی شەکری خوێن (FBS)",
    "پشکنینی چەوری خوێن (Lipid Profile)",
    "پشکنینی جگەر (LFT)",
    "پشکنینی گورچیلە (KFT)",
    "پشکنینی تیرۆید (TSH/T3/T4)",
    "پشکنینی ڤیتامین D",
    "پشکنینی هۆرمۆنەکان",
    "پشکنینی ڤایرۆسی (HCV/HBV/HIV)",
    "پشکنینی میز (Urinalysis)",
    "پشکنینی کۆڤید-١٩",
    "وێنەگرتن (X-Ray)",
    "سونۆگرافی (Ultrasound)",
    "سیتی سکان (CT Scan)",
    "MRI",
    "نەخۆشییە هەناویەکان"
]

SPECIALTIES = [
    "پزیشکی گشتی",
    "پزیشکی ناوخۆیی",
    "پزیشکی دڵ",
    "پزیشکی شەکرە",
    "پزیشکی جگەر",
    "پزیشکی گورچیلە",
    "پزیشکی هەرس",
    "پزیشکی مێز و زاوزێ",
    "پزیشکی منداڵان",
    "پزیشکی دەمار",
    "پزیشکی دەروونی",
    "پزیشکی پێست",
    "پزیشکی چاو",
    "پزیشکی گوێ و لوت و قورگ",
    "پزیشکی شێرپەنجە",
    "پزیشکی ڕێنمایی وێنەگرتن"
]

URGENCY_LEVELS = ["ئاسایی", "پەلە", "فریاکەوتن"]
TEST_STATUS = ["چاوەڕوان", "لەژێر ئەنجامدان", "ئەنجام ئامادەیە", "نێردرا"]

# --- 5. MULTI-LANGUAGE UI STRINGS ---
languages = {
    "English 🇬🇧": {
        "dir": "ltr", "align": "left",
        "title": "MEDICAL ANALYSIS SYSTEM",
        "desc": "Advanced medical analysis and diagnostics center in Kirkuk.",
        "nav_home": "Dashboard", "nav_patients": "Patients", "nav_tests": "Tests",
        "nav_results": "Results", "nav_doctors": "Doctors", "nav_reports": "Reports",
        "nav_support": "Support", "nav_emergency": "Emergency",
        "patient_name": "Patient Name", "patient_age": "Age",
        "patient_gender": "Gender", "phone": "Phone Number",
        "blood_type": "Blood Type", "allergies": "Allergies",
        "chronic_diseases": "Chronic Diseases", "test_type": "Test Type",
        "urgency": "Urgency Level", "doctor": "Doctor",
        "notes": "Notes", "submit": "Register",
        "patient_id": "Patient ID", "test_id": "Test ID",
        "result": "Result", "normal_range": "Normal Range",
        "status": "Status", "date_ordered": "Date Ordered",
        "estimated_completion": "Estimated Completion",
        "critical_alert": "⚠️ Critical Alert",
        "abnormal_result": "⚠️ Abnormal Result",
        "normal_result": "✅ Normal Result",
        "emergency_call": "🚨 Emergency",
        "police": "Police", "ambulance": "Ambulance",
        "fast_title": "⚡ Fast Results", "fast_desc": "Results within 2-4 hours",
        "secure_title": "🔒 Secure", "secure_desc": "Your medical data is protected",
        "accurate_title": "🎯 Accurate", "accurate_desc": "99.9% accuracy rate"
    },
    "کوردی 🇭🇺": {
        "dir": "rtl", "align": "right",
        "title": "سیستەمی شیکاری نەخۆشییەکان",
        "desc": "سەنتەری پێشکەوتووی شیکاری و دەستنیشانکردنی پزیشکی لە کەرکوک.",
        "nav_home": "داشبۆرد", "nav_patients": "نەخۆشەکان", "nav_tests": "پشکنینەکان",
        "nav_results": "ئەنجامەکان", "nav_doctors": "پزیشکان", "nav_reports": "ڕاپۆرتەکان",
        "nav_support": "پاڵپشتی", "nav_emergency": "فریاکەوتن",
        "patient_name": "ناوی نەخۆش", "patient_age": "تەمەن",
        "patient_gender": "ڕەگەز", "phone": "ژمارەی مۆبایل",
        "blood_type": "گروپی خوێن", "allergies": "حەساسیەت",
        "chronic_diseases": "نەخۆشییە درێژخایەنەکان", "test_type": "جۆری پشکنین",
        "urgency": "ئاستی پەلەکردن", "doctor": "پزیشک",
        "notes": "تێبینییەکان", "submit": "تۆمارکردن",
        "patient_id": "ناسنامەی نەخۆش", "test_id": "ناسنامەی پشکنین",
        "result": "ئەنجام", "normal_range": "مەودای ئاسایی",
        "status": "دۆخ", "date_ordered": "ڕێکەوتی داواکردن",
        "estimated_completion": "کاتی چاوەڕوانکراو",
        "critical_alert": "⚠️ هۆشداری پەلە",
        "abnormal_result": "⚠️ ئەنجامی نائاسایی",
        "normal_result": "✅ ئەنجامی ئاسایی",
        "emergency_call": "🚨 فریاکەوتن",
        "police": "پۆلیس", "ambulance": "فریاکەوتن",
        "fast_title": "⚡ ئەنجامی خێرا", "fast_desc": "ئەنجام لە ماوەی ٢-٤ کاتژمێردا",
        "secure_title": "🔒 پارێزراو", "secure_desc": "زانیاری پزیشکیەکەت پارێزراوە",
        "accurate_title": "🎯 ورد", "accurate_desc": "ڕێژەی دروستی ٩٩.٩٪",
        "total_patients": "کۆی نەخۆشەکان",
        "today_tests": "پشکنینی ئەمڕۆ",
        "completed": "تەواوکراو",
        "pending": "چاوەڕوان",
        "abnormal_cases": "حاڵەتی نائاسایی",
        "access_account": "بچۆ ژوورەوە بۆ سیستەمەکە",
        "signed_in_as": "چوویتە ژوورەوە وەک",
        "logout": "چوونەدەرەوە",
        "settings": "ڕێکخستنەکان"
    },
    "العربية 🇮🇶": {
        "dir": "rtl", "align": "right",
        "title": "نظام التحاليل الطبية",
        "desc": "مركز متقدم للتحاليل الطبية والتشخيص في كركوك.",
        "nav_home": "لوحة التحكم", "nav_patients": "المرضى", "nav_tests": "الفحوصات",
        "nav_results": "النتائج", "nav_doctors": "الأطباء", "nav_reports": "التقارير",
        "nav_support": "الدعم", "nav_emergency": "طوارئ",
        "patient_name": "اسم المريض", "patient_age": "العمر",
        "patient_gender": "الجنس", "phone": "رقم الهاتف",
        "blood_type": "فصيلة الدم", "allergies": "الحساسية",
        "chronic_diseases": "الأمراض المزمنة", "test_type": "نوع الفحص",
        "urgency": "مستوى الاستعجال", "doctor": "الطبيب",
        "notes": "ملاحظات", "submit": "تسجيل",
        "patient_id": "رقم المريض", "test_id": "رقم الفحص",
        "result": "النتيجة", "normal_range": "المجال الطبيعي",
        "status": "الحالة", "date_ordered": "تاريخ الطلب",
        "estimated_completion": "الوقت المتوقع",
        "critical_alert": "⚠️ تنبيه عاجل",
        "abnormal_result": "⚠️ نتيجة غير طبيعية",
        "normal_result": "✅ نتيجة طبيعية",
        "emergency_call": "🚨 طوارئ",
        "police": "شرطة", "ambulance": "إسعاف",
        "fast_title": "⚡ نتائج سريعة", "fast_desc": "النتائج خلال ٢-٤ ساعات",
        "secure_title": "🔒 آمن", "secure_desc": "بياناتك الطبية محمية",
        "accurate_title": "🎯 دقيق", "accurate_desc": "نسبة دقة ٩٩.٩٪",
        "total_patients": "إجمالي المرضى",
        "today_tests": "فحوصات اليوم",
        "completed": "مكتمل",
        "pending": "قيد الانتظار",
        "abnormal_cases": "حالات غير طبيعية",
        "access_account": "سجل الدخول للنظام",
        "signed_in_as": "تم تسجيل الدخول باسم",
        "logout": "خروج",
        "settings": "الإعدادات"
    }
}

# --- 6. DATA FILES ---
PATIENTS_FILE = "patients.csv"
TESTS_FILE = "tests.csv"
DOCTORS_FILE = "doctors.csv"
FEEDBACK_FILE = "feedback.csv"

# --- 7. DATA FUNCTIONS ---
def load_patients():
    if os.path.exists(PATIENTS_FILE):
        return pd.read_csv(PATIENTS_FILE, dtype={"phone": str, "patient_id": str})
    return pd.DataFrame(columns=[
        "patient_id", "name", "age", "gender", "phone", "blood_type",
        "allergies", "chronic_diseases", "registration_date", "total_tests"
    ])

def save_patients(df):
    df.to_csv(PATIENTS_FILE, index=False)

def load_tests():
    if os.path.exists(TESTS_FILE):
        return pd.read_csv(TESTS_FILE, dtype={"patient_id": str, "test_id": str})
    return pd.DataFrame(columns=[
        "test_id", "patient_id", "test_type", "date_ordered", 
        "doctor", "status", "urgency", "result", "normal_range", 
        "notes", "price", "payment_status", "estimated_completion"
    ])

def save_tests(df):
    df.to_csv(TESTS_FILE, index=False)

def load_doctors():
    if os.path.exists(DOCTORS_FILE):
        return pd.read_csv(DOCTORS_FILE, dtype={"phone": str, "doctor_id": str})
    return pd.DataFrame(columns=[
        "doctor_id", "name", "specialty", "phone", "available", "total_patients"
    ])

def save_doctors(df):
    df.to_csv(DOCTORS_FILE, index=False)

def generate_patient_id():
    return f"PT-{datetime.now().strftime('%Y%m')}-{str(uuid.uuid4())[:8].upper()}"

def generate_test_id():
    return f"TST-{datetime.now().strftime('%Y%m')}-{str(uuid.uuid4())[:8].upper()}"

def generate_doctor_id():
    return f"DR-{str(uuid.uuid4())[:8].upper()}"

def calculate_estimated_completion(urgency):
    now = datetime.now()
    if urgency == "فریاکەوتن":
        return (now + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
    elif urgency == "پەلە":
        return (now + timedelta(hours=3)).strftime("%Y-%m-%d %H:%M")
    else:
        return (now + timedelta(hours=6)).strftime("%Y-%m-%d %H:%M")

def check_abnormal_result(test_type, result_value):
    """بۆ دیاریکردنی ئەنجامی نائاسایی"""
    try:
        value = float(result_value)
        abnormal_ranges = {
            "پشکنینی شەکری خوێن (FBS)": (70, 110),
            "پشکنینی چەوری خوێن (Lipid Profile)": (0, 200),
            "پشکنینی ڤیتامین D": (30, 100),
            "پشکنینی تیرۆید (TSH/T3/T4)": (0.5, 4.5)
        }
        
        if test_type in abnormal_ranges:
            min_val, max_val = abnormal_ranges[test_type]
            return value < min_val or value > max_val
        return False
    except:
        return False

# --- 8. INITIALIZE SAMPLE DATA ---
def initialize_sample_data():
    doctors_df = load_doctors()
    if doctors_df.empty:
        sample_doctors = pd.DataFrame([
            {"doctor_id": generate_doctor_id(), "name": "د. ئازاد محەمەد", "specialty": "پزیشکی گشتی", "phone": "07701234567", "available": True, "total_patients": 0},
            {"doctor_id": generate_doctor_id(), "name": "د. سارا ئەحمەد", "specialty": "پزیشکی ناوخۆیی", "phone": "07702345678", "available": True, "total_patients": 0},
            {"doctor_id": generate_doctor_id(), "name": "د. هێمن عوسمان", "specialty": "پزیشکی دڵ", "phone": "07703456789", "available": True, "total_patients": 0},
            {"doctor_id": generate_doctor_id(), "name": "د. لەیلا حەسەن", "specialty": "پزیشکی منداڵان", "phone": "07704567890", "available": True, "total_patients": 0},
            {"doctor_id": generate_doctor_id(), "name": "د. کاروان ڕەسوڵ", "specialty": "پزیشکی شەکرە", "phone": "07705678901", "available": True, "total_patients": 0}
        ])
        save_doctors(sample_doctors)

initialize_sample_data()

# --- 9. TOP BAR ---
L = languages[st.session_state.lang_choice]

top_col1, top_col2, top_col3 = st.columns([2, 1, 1])
with top_col1:
    st.markdown(f"<h2 style='color:#0077B6; margin:0;'>{L['title']} 🏥</h2>", unsafe_allow_html=True)
with top_col2:
    lang_options = list(languages.keys())
    current_lang_index = lang_options.index(st.session_state.lang_choice)
    selected_lang = st.selectbox("🌐", lang_options, index=current_lang_index, label_visibility="collapsed", key="lang_select")
    if selected_lang != st.session_state.lang_choice:
        st.session_state.lang_choice = selected_lang
        st.rerun()

L = languages[st.session_state.lang_choice]

# --- 10. CSS STYLING (Medical Theme) ---
main_bg = "#F0F8FF"  # Alice Blue
card_bg = "#FFFFFF"
text_color = "#1a1a2e"
accent = "#0077B6"  # Medical Blue
accent_light = "#00B4D8"
critical_color = "#FF4444"
warning_color = "#FFA500"
success_color = "#00C851"

st.markdown(f"""
<style>
    [data-testid="stSidebar"] {{ display: none; }}
    html, body, [data-testid="stAppViewContainer"] {{ background-color: {main_bg} !important; color: {text_color} !important; }}
    h1, h2, h3, h4, h5, h6, p, span, div, label {{ color: {text_color} !important; }}
    input, textarea, .stTextInput input, .stTextArea textarea {{ background-color: {card_bg} !important; color: {text_color} !important; border: 1px solid #e0e0e0 !important; }}
    .stSelectbox div[data-baseweb="select"] {{ background-color: {card_bg} !important; border-color: #e0e0e0 !important; }}
    div[data-baseweb="menu"] {{ background-color: {card_bg} !important; }}
    .stForm {{ background-color: {card_bg} !important; border: 1px solid {accent}40 !important; border-radius: 20px !important; padding: 30px !important; }}
    .medical-card {{ background: linear-gradient(135deg, {accent} 0%, {accent_light} 100%); border-radius: 20px; padding: 25px; color: white !important; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
    .medical-card * {{ color: white !important; }}
    .glass-card {{ background-color: {card_bg} !important; border-radius: 20px !important; padding: 25px !important; border: 1px solid {accent}30 !important; margin-bottom: 20px !important; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
    .stButton button {{ background-color: {accent} !important; color: white !important; border: none !important; font-weight: bold !important; border-radius: 10px !important; padding: 10px 20px !important; transition: all 0.3s !important; }}
    .stButton button:hover {{ background-color: {accent_light} !important; transform: translateY(-2px) !important; box-shadow: 0 4px 8px rgba(0, 119, 182, 0.3); }}
    .card-title {{ color: {accent} !important; font-size: 1.5rem !important; }}
    .metric-card {{ background-color: {card_bg}; padding: 20px; border-radius: 15px; text-align: center; border: 1px solid {accent}20; margin: 10px 0; }}
    .metric-value {{ font-size: 2.5rem; font-weight: bold; color: {accent}; }}
    .metric-label {{ font-size: 1rem; color: {text_color}; opacity: 0.8; }}
    .alert-critical {{ background-color: {critical_color}20; border-left: 5px solid {critical_color}; padding: 15px; border-radius: 5px; margin: 10px 0; }}
    .alert-warning {{ background-color: {warning_color}20; border-left: 5px solid {warning_color}; padding: 15px; border-radius: 5px; margin: 10px 0; }}
    .alert-success {{ background-color: {success_color}20; border-left: 5px solid {success_color}; padding: 15px; border-radius: 5px; margin: 10px 0; }}
    [dir="{L['dir']}"] {{ text-align: {L['align']} !important; }}
    .emergency-button {{ background-color: {critical_color} !important; color: white !important; }}
    .whatsapp-button {{ background-color: #25D366 !important; color: white !important; }}
</style>
""", unsafe_allow_html=True)

# --- 11. NAVIGATION MENU ---
selected = option_menu(
    menu_title=None,
    options=[L['nav_home'], L['nav_patients'], L['nav_tests'], L['nav_results'], 
             L['nav_doctors'], L['nav_reports'], L['nav_support'], L['nav_emergency']],
    icons=['speedometer2', 'people', 'clipboard2-pulse', 'file-medical', 
           'person-badge', 'graph-up', 'headset', 'exclamation-triangle'],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "transparent", "max-width": "1200px", "margin": "0 auto", "display": "flex", "justify-content": "center", "gap": "5px"},
        "icon": {"color": accent, "font-size": "16px"},
        "nav-link": {"font-size": "14px", "text-align": "center", "margin": "0px 2px", "padding": "8px 12px", "border-radius": "30px", "color": text_color, "background-color": card_bg},
        "nav-link:hover": {"background-color": f"{accent}20", "transform": "translateY(-2px)"},
        "nav-link-selected": {"background-color": accent, "color": "white", "font-weight": "bold"},
    }
)

page_mapping = {
    L['nav_home']: "home", L['nav_patients']: "patients", 
    L['nav_tests']: "tests", L['nav_results']: "results",
    L['nav_doctors']: "doctors", L['nav_reports']: "reports",
    L['nav_support']: "support", L['nav_emergency']: "emergency"
}
st.session_state.page = page_mapping.get(selected, "home")

# --- 12. HOME PAGE (Dashboard) ---
if st.session_state.page == "home":
    st.markdown(f'<div class="medical-card"><h1>🏥 {L["title"]}</h1><p>{L["desc"]}</p></div>', unsafe_allow_html=True)
    
    patients_df = load_patients()
    tests_df = load_tests()
    doctors_df = load_doctors()
    
    today = datetime.now().strftime("%Y-%m-%d")
    today_tests = tests_df[tests_df['date_ordered'].str.contains(today, na=False)]
    completed_tests = tests_df[tests_df['status'].isin(['ئەنجام ئامادەیە', 'نێردرا'])]
    pending_tests = tests_df[tests_df['status'] == 'چاوەڕوان']
    
    # ئاماری سەرەکی
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(patients_df)}</div>
            <div class="metric-label">👥 {L['total_patients']}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(today_tests)}</div>
            <div class="metric-label">🔬 {L['today_tests']}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(completed_tests)}</div>
            <div class="metric-label">✅ {L['completed']}</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(pending_tests)}</div>
            <div class="metric-label">⏳ {L['pending']}</div>
        </div>
        """, unsafe_allow_html=True)
    with col5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(doctors_df[doctors_df['available'] == True])}</div>
            <div class="metric-label">👨‍⚕️ پزیشکی چالاک</div>
        </div>
        """, unsafe_allow_html=True)
    
    # چارتەکان
    col1, col2 = st.columns(2)
    with col1:
        if not tests_df.empty:
            test_counts = tests_df['test_type'].value_counts().head(10)
            fig = px.bar(x=test_counts.index, y=test_counts.values, 
                        title='پشکنینەکان بەپێی جۆر',
                        labels={'x': 'جۆری پشکنین', 'y': 'ژمارە'},
                        color_discrete_sequence=[accent])
            fig.update_layout(plot_bgcolor=card_bg, paper_bgcolor=card_bg)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if not tests_df.empty:
            status_counts = tests_df['status'].value_counts()
            fig = px.pie(values=status_counts.values, names=status_counts.index, 
                        title='دۆخی پشکنینەکان',
                        color_discrete_sequence=[success_color, warning_color, accent, critical_color])
            fig.update_layout(plot_bgcolor=card_bg, paper_bgcolor=card_bg)
            st.plotly_chart(fig, use_container_width=True)
    
    # دواین نەخۆشەکان
    st.markdown(f"<h3 style='color:{accent};'>📋 دواین نەخۆشە تۆمارکراوەکان</h3>", unsafe_allow_html=True)
    if not patients_df.empty:
        st.dataframe(patients_df.tail(10)[['patient_id', 'name', 'age', 'gender', 'blood_type', 'registration_date']], 
                    use_container_width=True)
    
    # تایبەتمەندییەکان
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="glass-card"><h3 class="card-title">{L["fast_title"]}</h3><p>{L["fast_desc"]}</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="glass-card"><h3 class="card-title">{L["secure_title"]}</h3><p>{L["secure_desc"]}</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="glass-card"><h3 class="card-title">{L["accurate_title"]}</h3><p>{L["accurate_desc"]}</p></div>', unsafe_allow_html=True)

# --- 13. PATIENTS PAGE ---
elif st.session_state.page == "patients":
    st.markdown(f"<h2 style='color:{accent}; text-align:center;'>👥 {L['nav_patients']}</h2>", unsafe_allow_html=True)
    
    patients_df = load_patients()
    
    tab1, tab2 = st.tabs(["➕ نەخۆشی نوێ", "📋 لیستی نەخۆشەکان"])
    
    with tab1:
        with st.form("new_patient_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input(L['patient_name'])
                age = st.number_input(L['patient_age'], min_value=0, max_value=150, value=30)
                gender = st.selectbox(L['patient_gender'], GENDERS)
                phone = st.text_input(L['phone'], placeholder="07xx xxx xxxx")
            with col2:
                blood_type = st.selectbox(L['blood_type'], ["-- هەڵبژاردن --"] + BLOOD_TYPES)
                allergies = st.text_area(L['allergies'], placeholder="دەرمان، خۆراک، هتد...")
                chronic = st.text_area(L['chronic_diseases'], placeholder="شەکرە، پەستانی خوێن، هتد...")
            
            if st.form_submit_button(L['submit']):
                if name and phone and blood_type != "-- هەڵبژاردن --":
                    patient_id = generate_patient_id()
                    new_patient = pd.DataFrame([{
                        "patient_id": patient_id,
                        "name": name,
                        "age": age,
                        "gender": gender,
                        "phone": phone,
                        "blood_type": blood_type,
                        "allergies": allergies,
                        "chronic_diseases": chronic,
                        "registration_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "total_tests": 0
                    }])
                    patients_df = pd.concat([patients_df, new_patient], ignore_index=True)
                    save_patients(patients_df)
                    st.success(f"✅ نەخۆش بە سەرکەوتوویی تۆمارکرا! ناسنامە: {patient_id}")
                    st.balloons()
                else:
                    st.error("تکایە ناو، ژمارە مۆبایل، و گروپی خوێن پڕ بکەرەوە")
    
    with tab2:
        if not patients_df.empty:
            search = st.text_input("🔍 گەڕان بەپێی ناو یان ژمارە")
            if search:
                filtered = patients_df[patients_df['name'].str.contains(search, na=False) | 
                                      patients_df['phone'].str.contains(search, na=False)]
                st.dataframe(filtered, use_container_width=True)
            else:
                st.dataframe(patients_df, use_container_width=True)
            
            # بینینی وردەکاری نەخۆش
            selected_patient = st.selectbox("هەڵبژاردنی نەخۆش بۆ بینینی وردەکاری", 
                                           patients_df['patient_id'].tolist())
            if selected_patient:
                patient = patients_df[patients_df['patient_id'] == selected_patient].iloc[0]
                st.markdown(f"""
                <div class="glass-card">
                    <h4 style="color:{accent};">📋 وردەکاری نەخۆش</h4>
                    <p><b>ناو:</b> {patient['name']}</p>
                    <p><b>تەمەن:</b> {patient['age']} ساڵ</p>
                    <p><b>ڕەگەز:</b> {patient['gender']}</p>
                    <p><b>گروپی خوێن:</b> {patient['blood_type']}</p>
                    <p><b>ژمارە:</b> {patient['phone']}</p>
                    <p><b>حەساسیەت:</b> {patient['allergies']}</p>
                    <p><b>نەخۆشییە درێژخایەنەکان:</b> {patient['chronic_diseases']}</p>
                    <p><b>ڕێکەوتی تۆمارکردن:</b> {patient['registration_date']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # پشکنینەکانی نەخۆش
                tests_df = load_tests()
                patient_tests = tests_df[tests_df['patient_id'] == selected_patient]
                if not patient_tests.empty:
                    st.markdown(f"<h4 style='color:{accent};\">🔬 پشکنینەکانی نەخۆش</h4>", unsafe_allow_html=True)
                    st.dataframe(patient_tests[['test_id', 'test_type', 'date_ordered', 'status', 'result']], 
                                use_container_width=True)
        else:
            st.info("هیچ نەخۆشێک تۆمار نەکراوە")

# --- 14. TESTS PAGE ---
elif st.session_state.page == "tests":
    st.markdown(f"<h2 style='color:{accent}; text-align:center;'>🔬 {L['nav_tests']}</h2>", unsafe_allow_html=True)
    
    patients_df = load_patients()
    doctors_df = load_doctors()
    tests_df = load_tests()
    
    if patients_df.empty:
        st.warning("تکایە یەکەم جار نەخۆش تۆمار بکە لە بەشی نەخۆشەکان")
    else:
        with st.form("new_test_form"):
            st.markdown(f"<h4 style='color:{accent};\">➕ پشکنینی نوێ</h4>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                patient = st.selectbox(L['patient_name'], 
                                      [f"{p['name']} - {p['patient_id']}" for _, p in patients_df.iterrows()])
                test_type = st.selectbox(L['test_type'], TEST_TYPES)
                urgency = st.selectbox(L['urgency'], URGENCY_LEVELS)
            with col2:
                available_doctors = doctors_df[doctors_df['available'] == True]
                if not available_doctors.empty:
                    doctor = st.selectbox(L['doctor'], 
                                         [f"{d['name']} - {d['specialty']}" for _, d in available_doctors.iterrows()])
                else:
                    doctor = "No doctor available"
                
                price = st.number_input("نرخ (د.ع)", min_value=0, value=15000, step=1000)
                notes = st.text_area(L['notes'])
            
            if st.form_submit_button(L['submit']):
                patient_id = patient.split(" - ")[1]
                doctor_name = doctor.split(" - ")[0] if " - " in doctor else doctor
                
                test_id = generate_test_id()
                estimated = calculate_estimated_completion(urgency)
                
                new_test = pd.DataFrame([{
                    "test_id": test_id,
                    "patient_id": patient_id,
                    "test_type": test_type,
                    "date_ordered": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "doctor": doctor_name,
                    "status": "چاوەڕوان",
                    "urgency": urgency,
                    "result": None,
                    "normal_range": None,
                    "notes": notes,
                    "price": price,
                    "payment_status": "نەدراوە",
                    "estimated_completion": estimated
                }])
                
                tests_df = pd.concat([tests_df, new_test], ignore_index=True)
                save_tests(tests_df)
                
                # زیادکردنی ژمارەی پشکنینی نەخۆش
                patients_df.loc[patients_df['patient_id'] == patient_id, 'total_tests'] += 1
                save_patients(patients_df)
                
                st.success(f"✅ پشکنین تۆمارکرا! ناسنامەی پشکنین: {test_id}")
                st.balloons()
        
        # پیشاندانی لیستی پشکنینەکان
        st.markdown(f"<h4 style='color:{accent}; margin-top:30px;'>📋 لیستی پشکنینەکان</h4>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_status = st.multiselect("پاڵاوتن بەپێی دۆخ", TEST_STATUS, default=TEST_STATUS)
        with col2:
            filter_urgency = st.multiselect("پاڵاوتن بەپێی پەلە", URGENCY_LEVELS, default=URGENCY_LEVELS)
        
        filtered_tests = tests_df[tests_df['status'].isin(filter_status) & 
                                  tests_df['urgency'].isin(filter_urgency)]
        
        if not filtered_tests.empty:
            for _, test in filtered_tests.iterrows():
                patient = patients_df[patients_df['patient_id'] == test['patient_id']]
                patient_name = patient.iloc[0]['name'] if not patient.empty else "نەناسراو"
                
                status_emoji = {
                    "چاوەڕوان": "⏳",
                    "لەژێر ئەنجامدان": "🔄",
                    "ئەنجام ئامادەیە": "✅",
                    "نێردرا": "📤"
                }
                
                urgency_color = {
                    "ئاسایی": "info",
                    "پەلە": "warning",
                    "فریاکەوتن": "error"
                }
                
                with st.expander(f"{status_emoji.get(test['status'], '📋')} {test['test_id']} - {patient_name} - {test['test_type']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**نەخۆش:** {patient_name}")
                        st.write(f"**پزیشک:** {test['doctor']}")
                        st.write(f"**پەلەکردن:** {test['urgency']}")
                    with col2:
                        st.write(f"**دۆخ:** {test['status']}")
                        st.write(f"**کاتی چاوەڕوانکراو:** {test['estimated_completion']}")
                        st.write(f"**نرخ:** {test['price']:,} د.ع")
                    
                    if test['status'] == 'لەژێر ئەنجامدان' and st.session_state.user_role in ['doctor', 'admin']:
                        with st.form(f"result_{test['test_id']}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                result_value = st.text_input(L['result'])
                            with col2:
                                normal_range = st.text_input(L['normal_range'])
                            
                            if st.form_submit_button("تۆمارکردنی ئەنجام"):
                                is_abnormal = check_abnormal_result(test['test_type'], result_value)
                                tests_df.loc[tests_df['test_id'] == test['test_id'], 'result'] = result_value
                                tests_df.loc[tests_df['test_id'] == test['test_id'], 'normal_range'] = normal_range
                                tests_df.loc[tests_df['test_id'] == test['test_id'], 'status'] = 'ئەنجام ئامادەیە'
                                save_tests(tests_df)
                                
                                if is_abnormal:
                                    st.error(f"⚠️ {L['abnormal_result']}")
                                else:
                                    st.success(f"✅ {L['normal_result']}")
                                st.rerun()

# --- 15. RESULTS PAGE ---
elif st.session_state.page == "results":
    st.markdown(f"<h2 style='color:{accent}; text-align:center;'>📊 {L['nav_results']}</h2>", unsafe_allow_html=True)
    
    tests_df = load_tests()
    patients_df = load_patients()
    
    completed_tests = tests_df[tests_df['status'].isin(['ئەنجام ئامادەیە', 'نێردرا'])]
    
    if not completed_tests.empty:
        for _, test in completed_tests.iterrows():
            patient = patients_df[patients_df['patient_id'] == test['patient_id']]
            patient_name = patient.iloc[0]['name'] if not patient.empty else "نەناسراو"
            
            is_abnormal = check_abnormal_result(test['test_type'], test['result']) if test['result'] else False
            
            alert_class = "alert-critical" if is_abnormal else "alert-success"
            alert_text = L['abnormal_result'] if is_abnormal else L['normal_result']
            
            with st.expander(f"{'⚠️' if is_abnormal else '✅'} {patient_name} - {test['test_type']} - {test['date_ordered']}"):
                st.markdown(f"""
                <div class="{alert_class}">
                    <h4>{alert_text}</h4>
                    <p><b>نەخۆش:</b> {patient_name}</p>
                    <p><b>جۆری پشکنین:</b> {test['test_type']}</p>
                    <p><b>ئەنجام:</b> {test['result']}</p>
                    <p><b>مەودای ئاسایی:</b> {test['normal_range']}</p>
                    <p><b>ڕێکەوت:</b> {test['date_ordered']}</p>
                    <p><b>پزیشک:</b> {test['doctor']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if test['status'] == 'ئەنجام ئامادەیە':
                    if st.button(f"📤 ناردنی ئەنجام بۆ نەخۆش", key=f"send_{test['test_id']}"):
                        tests_df.loc[tests_df['test_id'] == test['test_id'], 'status'] = 'نێردرا'
                        save_tests(tests_df)
                        st.success("ئەنجام نێردرا!")
                        st.rerun()
    else:
        st.info("هیچ ئەنجامێکی ئامادە نییە")

# --- 16. DOCTORS PAGE ---
elif st.session_state.page == "doctors":
    st.markdown(f"<h2 style='color:{accent}; text-align:center;'>👨‍⚕️ {L['nav_doctors']}</h2>", unsafe_allow_html=True)
    
    doctors_df = load_doctors()
    
    tab1, tab2 = st.tabs(["➕ پزیشکی نوێ", "📋 لیستی پزیشکان"])
    
    with tab1:
        with st.form("new_doctor_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("ناوی پزیشک")
                specialty = st.selectbox("شارەزایی", SPECIALTIES)
            with col2:
                phone = st.text_input("ژمارەی مۆبایل")
                available = st.checkbox("بەردەستە", value=True)
            
            if st.form_submit_button("تۆمارکردن"):
                if name and phone:
                    doctor_id = generate_doctor_id()
                    new_doctor = pd.DataFrame([{
                        "doctor_id": doctor_id,
                        "name": name,
                        "specialty": specialty,
                        "phone": phone,
                        "available": available,
                        "total_patients": 0
                    }])
                    doctors_df = pd.concat([doctors_df, new_doctor], ignore_index=True)
                    save_doctors(doctors_df)
                    st.success("پزیشک تۆمارکرا!")
                    st.rerun()
    
    with tab2:
        if not doctors_df.empty:
            st.dataframe(doctors_df, use_container_width=True)
            
            # بەڕێوەبردنی پزیشکان
            selected_doctor = st.selectbox("هەڵبژاردنی پزیشک بۆ بەڕێوەبردن", 
                                          doctors_df['doctor_id'].tolist())
            if selected_doctor:
                doctor = doctors_df[doctors_df['doctor_id'] == selected_doctor].iloc[0]
                st.markdown(f"""
                <div class="glass-card">
                    <h4 style="color:{accent};">👨‍⚕️ {doctor['name']}</h4>
                    <p><b>شارەزایی:</b> {doctor['specialty']}</p>
                    <p><b>بەردەست:</b> {'✅ بەڵێ' if doctor['available'] else '❌ نەخێر'}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # گۆڕینی بەردەستبوون
                new_status = st.checkbox("بەردەستە", value=doctor['available'])
                if new_status != doctor['available']:
                    doctors_df.loc[doctors_df['doctor_id'] == selected_doctor, 'available'] = new_status
                    save_doctors(doctors_df)
                    st.success("دۆخی پزیشک نوێ کرایەوە")
                    st.rerun()

# --- 17. REPORTS PAGE ---
elif st.session_state.page == "reports":
    st.markdown(f"<h2 style='color:{accent}; text-align:center;'>📈 {L['nav_reports']}</h2>", unsafe_allow_html=True)
    
    tests_df = load_tests()
    patients_df = load_patients()
    doctors_df = load_doctors()
    
    # ڕاپۆرتی ڕۆژانە
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="glass-card"><h4 style="color:{accent};">📊 ڕاپۆرتی ڕۆژانە</h4></div>', unsafe_allow_html=True)
        today = datetime.now().strftime("%Y-%m-%d")
        today_tests = tests_df[tests_df['date_ordered'].str.contains(today, na=False)]
        st.metric("پشکنینی ئەمڕۆ", len(today_tests))
    
    with col2:
        st.markdown(f'<div class="glass-card"><h4 style="color:{accent};">💰 ڕاپۆرتی دارایی</h4></div>', unsafe_allow_html=True)
        total_revenue = tests_df['price'].sum()
        st.metric("کۆی داهات", f"{total_revenue:,} د.ع")
    
    # چارتی پشکنینەکان بەپێی پزیشک
    if not tests_df.empty:
        doctor_tests = tests_df.groupby('doctor').size().reset_index(name='count')
        fig = px.bar(doctor_tests, x='doctor', y='count', 
                    title='پشکنینەکان بەپێی پزیشک',
                    color_discrete_sequence=[accent])
        st.plotly_chart(fig, use_container_width=True)
    
    # ڕاپۆرتی پشکنینە نائاساییەکان
    abnormal_count = 0
    for _, test in tests_df.iterrows():
        if test['result'] and check_abnormal_result(test['test_type'], test['result']):
            abnormal_count += 1
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{abnormal_count}</div>
        <div class="metric-label">⚠️ حاڵەتی نائاسایی</div>
    </div>
    """, unsafe_allow_html=True)

# --- 18. SUPPORT PAGE ---
elif st.session_state.page == "support":
    st.markdown(f"<h2 style='color:{accent}; text-align:center;'>💬 {L['nav_support']}</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="glass-card">
            <h4 style="color:{accent};">📞 پەیوەندیمان پێوە بکە</h4>
            <p><b>ژمارە:</b> {HOSPITAL_PHONES[0]}</p>
            <p><b>ژمارە:</b> {HOSPITAL_PHONES[1]}</p>
            <p><b>واتسئاپ:</b> <a href="{HOSPITAL_WHATSAPP}" target="_blank">پەیوەندی</a></p>
            <p><b>ئیمەیڵ:</b> {HOSPITAL_EMAIL}</p>
            <p><b>ناونیشان:</b> {HOSPITAL_ADDRESS}</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="glass-card">
            <h4 style="color:{accent};">🕒 کاتی کار</h4>
            <p>شەممە - پێنجشەممە: ٨:٠٠ - ٢٢:٠٠</p>
            <p>هەینی: ١٤:٠٠ - ٢٠:٠٠</p>
            <p>٢٤/٧ بۆ حاڵەتی فریاکەوتن</p>
        </div>
        """, unsafe_allow_html=True)
    
    with st.form("support_form"):
        st.markdown(f"<h4 style='color:{accent};\">📝 فۆڕمی پەیوەندی</h4>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("ناو")
            email = st.text_input("ئیمەیڵ")
        with col2:
            phone = st.text_input("ژمارە مۆبایل")
            subject = st.selectbox("بابەت", ["پرسیار", "کێشە", "پێشنیار", "سکاڵا"])
        message = st.text_area("پەیام")
        if st.form_submit_button("ناردن"):
            st.success("پەیامەکەت نێردرا! وەڵامت دەدەینەوە")

# --- 19. EMERGENCY PAGE ---
elif st.session_state.page == "emergency":
    st.markdown(f"<h2 style='color:{critical_color}; text-align:center;'>🚨 {L['emergency_call']}</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button(f"🚓 {L['police']} {EMERGENCY_POLICE}", use_container_width=True, key="police_btn"):
            st.markdown(f'<meta http-equiv="refresh" content="0;url=tel:{EMERGENCY_POLICE}">', unsafe_allow_html=True)
    with col2:
        if st.button(f"🚑 {L['ambulance']} {EMERGENCY_AMBULANCE}", use_container_width=True, key="ambulance_btn"):
            st.markdown(f'<meta http-equiv="refresh" content="0;url=tel:{EMERGENCY_AMBULANCE}">', unsafe_allow_html=True)
    with col3:
        if st.button(f"🏥 نەخۆشخانە", use_container_width=True):
            st.markdown(f'<meta http-equiv="refresh" content="0;url=tel:{HOSPITAL_PHONES[0]}">', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="glass-card" style="margin-top:20px;">
        <h4 style="color:{critical_color};">🚨 ڕێنمایی فریاکەوتن</h4>
        <div class="alert-critical">
            <p>١. ئارام بە و یەکسەر پەیوەندی بکە بە ١٢٢</p>
            <p>٢. ناونیشان و نیشانەکانی نەخۆش بڵێ</p>
            <p>٣. نەخۆشەکە لە شوێنێکی سەلامەت دابنێ</p>
            <p>٤. تا هاتنی یارمەتی لە نەخۆشەکە جیا مەبەوە</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 20. PROFILE/AUTH SECTION ---
if st.session_state.user_email is None:
    st.sidebar.markdown(f"### 🔑 {L['access_account']}")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("👤 نەخۆش"):
            st.session_state.user_email = "patient@hospital.iq"
            st.session_state.user_role = "patient"
            st.session_state.user_name = "نەخۆش"
            st.rerun()
    with col2:
        if st.button("👨‍⚕️ پزیشک"):
            st.session_state.user_email = "doctor@hospital.iq"
            st.session_state.user_role = "doctor"
            st.session_state.user_name = "پزیشک"
            st.rerun()
    
    if st.sidebar.button("🔑 ئەدمین"):
        st.session_state.user_email = "admin@hospital.iq"
        st.session_state.user_role = "admin"
        st.session_state.user_name = "Admin"
        st.rerun()
else:
    with st.sidebar:
        st.markdown(f"### {L['signed_in_as']}")
        st.write(f"**{st.session_state.user_name}** ({st.session_state.user_role})")
        if st.button(L['logout']):
            for key in ['user_email', 'user_role', 'user_name', 'user_id']:
                st.session_state[key] = None
            st.rerun()

# --- 21. FOOTER ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(f"""
<div style="background-color:{card_bg}; padding:15px; border-radius:10px; text-align:center; border: 1px solid {accent}20;">
    <p>📞 <span style="color:{accent};">{HOSPITAL_PHONES[0]}</span> | <span style="color:{accent};">{HOSPITAL_PHONES[1]}</span></p>
    <p>✉️ {HOSPITAL_EMAIL} | 📍 {HOSPITAL_ADDRESS}</p>
    <p style="font-size:0.9rem;">© ٢٠٢٤ سیستەمی شیکاری نەخۆشییەکان - کەرکوک</p>
</div>
""", unsafe_allow_html=True)
