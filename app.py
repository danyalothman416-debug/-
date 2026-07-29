# ================================
# MEDICAL TRAINING PLATFORM v12.0
# Dr.Danyal - Complete Edition
# Fixed get_user_count() and RTL Sidebar
# ================================

import streamlit as st
import hashlib
import os
import sqlite3
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import warnings
warnings.filterwarnings('ignore')

# ================================
# PAGE CONFIGURATION
# ================================
st.set_page_config(
    page_title="Dr.Danyal Medical Platform",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================================
# COMPLETE TRANSLATION SYSTEM
# ================================
TRANSLATIONS = {
    "en": {
        "app_name": "Dr.Danyal Medical Platform",
        "app_subtitle": "Advanced Medical Training Platform",
        "version": "v12.0",
        "copyright": "All rights reserved.",
        "login": "Login",
        "register": "Register",
        "username": "Username",
        "password": "Password",
        "confirm_password": "Confirm Password",
        "login_button": "Login",
        "register_button": "Create Account",
        "logout": "Logout",
        "enter_username": "Enter username",
        "enter_password": "Enter password",
        "confirm_password_placeholder": "Confirm password",
        "choose_username": "Choose Username",
        "choose_password": "Choose Password",
        "dashboard": "Dashboard",
        "diseases": "Diseases",
        "case_analysis": "Case Analysis",
        "quiz": "Quiz",
        "comprehensive_exam": "Comprehensive Exam",
        "spaced_repetition": "Spaced Repetition",
        "lab_tests": "Lab Tests",
        "pharmacology": "Pharmacology",
        "drug_interactions": "Drug Interactions",
        "leaderboard": "Leaderboard",
        "medical_news": "Medical News",
        "ai_assistant": "AI Assistant",
        "clinical_notes": "Clinical Notes",
        "achievements": "Achievements",
        "xp": "XP",
        "quiz_score": "Quiz Score",
        "streak": "Streak",
        "cases": "Cases",
        "level": "Level",
        "level_progress": "Level Progress",
        "diseases_count": "Diseases",
        "drugs_count": "Drugs",
        "tests_count": "Tests",
        "total_users": "Total Users",
        "your_progress": "Your Progress",
        "platform_stats": "Platform Stats",
        "accuracy": "Accuracy",
        "cases_solved": "Cases Solved",
        "disease_library": "Disease Library",
        "search": "Search",
        "search_placeholder": "Type disease name...",
        "risk_level": "Risk Level",
        "all": "All",
        "critical": "Critical",
        "high": "High",
        "moderate": "Moderate",
        "low": "Low",
        "symptoms": "Symptoms",
        "treatment": "Treatment",
        "risk": "Risk",
        "category": "Category",
        "clinical_case_analysis": "Clinical Case Analysis",
        "generate_new_case": "Generate New Case",
        "your_diagnosis": "Your Diagnosis",
        "submit": "Submit",
        "correct": "Correct!",
        "incorrect": "Incorrect.",
        "patient": "Patient",
        "case_id": "Case",
        "years_old": "years old",
        "medical_quiz": "Medical Quiz",
        "select_answer": "Select your answer",
        "submit_answer": "Submit Answer",
        "comprehensive_exam_title": "Comprehensive Exam",
        "start_exam": "Start Exam",
        "submit_exam": "Submit Exam",
        "score": "Score",
        "retake": "Retake",
        "spaced_repetition_title": "Spaced Repetition",
        "reveal_answer": "Reveal Answer",
        "knew_it": "Knew It",
        "review_again": "Review Again",
        "lab_tests_title": "Laboratory Tests",
        "normal_range": "Normal Range",
        "description": "Description",
        "no_tests_found": "No tests found",
        "pharmacology_title": "Pharmacology",
        "drug_class": "Class",
        "dose": "Dose",
        "indications": "Indications",
        "side_effects": "Side Effects",
        "drug_interactions_title": "Drug Interaction Checker",
        "select_drugs": "Select drugs to check",
        "select_minimum": "Select 2 or more drugs",
        "leaderboard_title": "Leaderboard",
        "no_data": "No data yet",
        "ai_assistant_title": "AI Symptom Checker",
        "enter_symptoms": "Enter symptoms (comma-separated):",
        "analyze": "Analyze",
        "match": "Match",
        "results": "Results",
        "clinical_notes_title": "Clinical Notes",
        "patient_info": "Patient Info",
        "clinical_note": "Clinical Note",
        "save_note": "Save Note",
        "note_saved": "Note saved!",
        "achievements_title": "Achievements",
        "earned": "Earned",
        "locked": "Locked",
        "online": "Online",
        "account_created": "Account created! Please login.",
        "invalid_credentials": "Invalid username or password",
        "username_exists": "Username already exists",
        "passwords_dont_match": "Passwords don't match",
        "what_are_symptoms_of": "What are the symptoms of",
        "is_characteristic_of": "is characteristic of",
        "answer_was": "Answer was",
        "drugs_selected": "drugs selected",
    },
    "ku": {
        "app_name": "پلاتفۆرمی پزیشکی Dr.Danyal",
        "app_subtitle": "پلاتفۆرمی ڕاهێنانی پزیشکی پێشکەوتوو",
        "version": "v12.0",
        "copyright": "هەموو مافێک پارێزراوە.",
        "login": "چوونەژوورەوە",
        "register": "خۆتۆمارکردن",
        "username": "ناوی بەکارهێنەر",
        "password": "وشەی نهێنی",
        "confirm_password": "دووپاتکردنەوەی وشەی نهێنی",
        "login_button": "چوونەژوورەوە",
        "register_button": "دروستکردنی هەژمار",
        "logout": "چوونەدەرەوە",
        "enter_username": "ناوی بەکارهێنەر بنووسە",
        "enter_password": "وشەی نهێنی بنووسە",
        "confirm_password_placeholder": "وشەی نهێنی دووپات بکەرەوە",
        "choose_username": "ناوی بەکارهێنەر هەڵبژێرە",
        "choose_password": "وشەی نهێنی هەڵبژێرە",
        "dashboard": "داشبۆرد",
        "diseases": "نەخۆشییەکان",
        "case_analysis": "شیکاری کەیس",
        "quiz": "کویز",
        "comprehensive_exam": "تاقیکردنەوەی گشتی",
        "spaced_repetition": "دووبارەکردنەوە",
        "lab_tests": "پشکنینەکان",
        "pharmacology": "دەرمانەکان",
        "drug_interactions": "کارلێکی دەرمانەکان",
        "leaderboard": "خشتەی ڕێزلێنان",
        "medical_news": "هەواڵی پزیشکی",
        "ai_assistant": "یاریدەدەری زیرەک",
        "clinical_notes": "تێبینی کلینیکی",
        "achievements": "دەستکەوتەکان",
        "xp": "خاڵ",
        "quiz_score": "کویز",
        "streak": "بەردەوامی",
        "cases": "کەیس",
        "level": "ئاست",
        "level_progress": "پێشکەوتنی ئاست",
        "diseases_count": "نەخۆشی",
        "drugs_count": "دەرمان",
        "tests_count": "پشکنین",
        "total_users": "کۆی بەکارهێنەران",
        "your_progress": "پێشکەوتنەکەت",
        "platform_stats": "ئاماری پلاتفۆرم",
        "accuracy": "ڕێژەی ڕاستی",
        "cases_solved": "کەیسەکانی شیکارکراو",
        "disease_library": "کتێبخانەی نەخۆشییەکان",
        "search": "گەڕان",
        "search_placeholder": "ناوی نەخۆشی بنووسە...",
        "risk_level": "ئاستی مەترسی",
        "all": "هەموو",
        "critical": "زۆر مەترسیدار",
        "high": "مەترسیدار",
        "moderate": "مامناوەند",
        "low": "کەم",
        "symptoms": "نیشانەکان",
        "treatment": "چارەسەر",
        "risk": "مەترسی",
        "category": "پۆلێن",
        "clinical_case_analysis": "شیکاری کەیسی کلینیکی",
        "generate_new_case": "دروستکردنی کەیسی نوێ",
        "your_diagnosis": "دەستنیشانکردنەکەت",
        "submit": "ناردن",
        "correct": "ڕاستە!",
        "incorrect": "هەڵەیە.",
        "patient": "نەخۆش",
        "case_id": "کەیس",
        "years_old": "ساڵ",
        "medical_quiz": "کویزی پزیشکی",
        "select_answer": "وەڵامەکەت هەڵبژێرە",
        "submit_answer": "ناردنی وەڵام",
        "comprehensive_exam_title": "تاقیکردنەوەی گشتی",
        "start_exam": "دەستپێکردنی تاقیکردنەوە",
        "submit_exam": "ناردنی تاقیکردنەوە",
        "score": "نمرە",
        "retake": "دووبارەکردنەوە",
        "spaced_repetition_title": "دووبارەکردنەوەی بۆشایی",
        "reveal_answer": "ئاشکراکردنی وەڵام",
        "knew_it": "زانیم",
        "review_again": "دووبارە خوێندنەوە",
        "lab_tests_title": "پشکنینەکانی تاقیگە",
        "normal_range": "مەودای ئاسایی",
        "description": "وەسف",
        "no_tests_found": "هیچ پشکنینێک نەدۆزرایەوە",
        "pharmacology_title": "فارماکۆلۆجی",
        "drug_class": "پۆلێن",
        "dose": "ڕێژە",
        "indications": "بەکارهێنانەکان",
        "side_effects": "کاریگەرییە لاوەکییەکان",
        "drug_interactions_title": "پشکنینی کارلێکی دەرمانەکان",
        "select_drugs": "دەرمانەکان هەڵبژێرە",
        "select_minimum": "لانیکەم ٢ دەرمان هەڵبژێرە",
        "leaderboard_title": "خشتەی ڕێزلێنان",
        "no_data": "هێشتا هیچ داتایەک نییە",
        "ai_assistant_title": "پشکنەری زیرەکی نیشانەکان",
        "enter_symptoms": "نیشانەکان بنووسە (بە بچووکەوە جیاکراوە):",
        "analyze": "شیکردنەوە",
        "match": "ڕێژەی گونجان",
        "results": "ئەنجامەکان",
        "clinical_notes_title": "تێبینییە کلینیکییەکان",
        "patient_info": "زانیاری نەخۆش",
        "clinical_note": "تێبینی کلینیکی",
        "save_note": "خەزنکردن",
        "note_saved": "تێبینییەکە خەزن کرا!",
        "achievements_title": "دەستکەوتەکان",
        "earned": "بەدەستهێنراوە",
        "locked": "داخراوە",
        "online": "ئۆنلاین",
        "account_created": "هەژمارەکەت دروست کرا! تکایە بچۆ ژوورەوە.",
        "invalid_credentials": "ناوی بەکارهێنەر یان وشەی نهێنی هەڵەیە",
        "username_exists": "ئەم ناوی بەکارهێنەریە پێشتر بەکارهێنراوە",
        "passwords_dont_match": "وشەی نهێنیەکان یەک ناگرنەوە",
        "what_are_symptoms_of": "نیشانەکانی چیین",
        "is_characteristic_of": "تایبەتە بە",
        "answer_was": "وەڵامەکە",
        "drugs_selected": "دەرمان هەڵبژێردرا",
    },
    "ar": {
        "app_name": "منصة الدكتور دانيال الطبية",
        "app_subtitle": "منصة التدريب الطبي المتقدمة",
        "version": "v12.0",
        "copyright": "جميع الحقوق محفوظة.",
        "login": "تسجيل الدخول",
        "register": "إنشاء حساب",
        "username": "اسم المستخدم",
        "password": "كلمة المرور",
        "confirm_password": "تأكيد كلمة المرور",
        "login_button": "تسجيل الدخول",
        "register_button": "إنشاء حساب",
        "logout": "تسجيل الخروج",
        "enter_username": "أدخل اسم المستخدم",
        "enter_password": "أدخل كلمة المرور",
        "confirm_password_placeholder": "أكد كلمة المرور",
        "choose_username": "اختر اسم المستخدم",
        "choose_password": "اختر كلمة المرور",
        "dashboard": "لوحة التحكم",
        "diseases": "الأمراض",
        "case_analysis": "تحليل الحالة",
        "quiz": "اختبار",
        "comprehensive_exam": "امتحان شامل",
        "spaced_repetition": "التكرار المتباعد",
        "lab_tests": "التحاليل المخبرية",
        "pharmacology": "علم الأدوية",
        "drug_interactions": "تداخلات الأدوية",
        "leaderboard": "لوحة المتصدرين",
        "medical_news": "أخبار طبية",
        "ai_assistant": "المساعد الذكي",
        "clinical_notes": "ملاحظات سريرية",
        "achievements": "الإنجازات",
        "xp": "الخبرة",
        "quiz_score": "الاختبار",
        "streak": "التوالي",
        "cases": "الحالات",
        "level": "المستوى",
        "level_progress": "تقدم المستوى",
        "diseases_count": "الأمراض",
        "drugs_count": "الأدوية",
        "tests_count": "التحاليل",
        "total_users": "إجمالي المستخدمين",
        "your_progress": "تقدمك",
        "platform_stats": "إحصائيات المنصة",
        "accuracy": "الدقة",
        "cases_solved": "الحالات المحلولة",
        "disease_library": "مكتبة الأمراض",
        "search": "بحث",
        "search_placeholder": "اكتب اسم المرض...",
        "risk_level": "مستوى الخطورة",
        "all": "الكل",
        "critical": "حرج",
        "high": "مرتفع",
        "moderate": "متوسط",
        "low": "منخفض",
        "symptoms": "الأعراض",
        "treatment": "العلاج",
        "risk": "الخطورة",
        "category": "الفئة",
        "clinical_case_analysis": "تحليل الحالة السريرية",
        "generate_new_case": "إنشاء حالة جديدة",
        "your_diagnosis": "تشخيصك",
        "submit": "إرسال",
        "correct": "صحيح!",
        "incorrect": "غير صحيح.",
        "patient": "المريض",
        "case_id": "الحالة",
        "years_old": "سنة",
        "medical_quiz": "اختبار طبي",
        "select_answer": "اختر إجابتك",
        "submit_answer": "إرسال الإجابة",
        "comprehensive_exam_title": "الامتحان الشامل",
        "start_exam": "بدء الامتحان",
        "submit_exam": "تسليم الامتحان",
        "score": "النتيجة",
        "retake": "إعادة",
        "spaced_repetition_title": "التكرار المتباعد",
        "reveal_answer": "كشف الإجابة",
        "knew_it": "كنت أعرفها",
        "review_again": "مراجعة مرة أخرى",
        "lab_tests_title": "التحاليل المخبرية",
        "normal_range": "المدى الطبيعي",
        "description": "الوصف",
        "no_tests_found": "لم يتم العثور على تحاليل",
        "pharmacology_title": "علم الأدوية",
        "drug_class": "الفئة",
        "dose": "الجرعة",
        "indications": "دواعي الاستعمال",
        "side_effects": "الآثار الجانبية",
        "drug_interactions_title": "مدقق تداخلات الأدوية",
        "select_drugs": "اختر الأدوية",
        "select_minimum": "اختر دواءين أو أكثر",
        "leaderboard_title": "لوحة المتصدرين",
        "no_data": "لا توجد بيانات بعد",
        "ai_assistant_title": "مدقق الأعراض الذكي",
        "enter_symptoms": "أدخل الأعراض (مفصولة بفواصل):",
        "analyze": "تحليل",
        "match": "نسبة التطابق",
        "results": "النتائج",
        "clinical_notes_title": "الملاحظات السريرية",
        "patient_info": "معلومات المريض",
        "clinical_note": "ملاحظة سريرية",
        "save_note": "حفظ الملاحظة",
        "note_saved": "تم حفظ الملاحظة!",
        "achievements_title": "الإنجازات",
        "earned": "تم الإنجاز",
        "locked": "مقفل",
        "online": "متصل",
        "account_created": "تم إنشاء الحساب! الرجاء تسجيل الدخول.",
        "invalid_credentials": "اسم المستخدم أو كلمة المرور غير صحيحة",
        "username_exists": "اسم المستخدم موجود مسبقاً",
        "passwords_dont_match": "كلمات المرور غير متطابقة",
        "what_are_symptoms_of": "ما هي أعراض",
        "is_characteristic_of": "مميز لـ",
        "answer_was": "الإجابة كانت",
        "drugs_selected": "أدوية مختارة",
    }
}

def t(key: str, lang: str = None) -> str:
    if lang is None:
        lang = st.session_state.get('language', 'en')
    return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, TRANSLATIONS['en'].get(key, key))

# ================================
# DATABASE SETUP
# ================================
DB_PATH = "medical_platform.db"
MAX_LOGIN_ATTEMPTS = 5
LOGIN_TIMEOUT_MINUTES = 15

@st.cache_resource
def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            login_attempts INTEGER DEFAULT 0,
            locked_until TIMESTAMP,
            xp_points INTEGER DEFAULT 0,
            quiz_score INTEGER DEFAULT 0,
            total_cases INTEGER DEFAULT 0,
            correct_diagnoses INTEGER DEFAULT 0,
            daily_streak INTEGER DEFAULT 0,
            last_active_date DATE,
            language_preference TEXT DEFAULT 'en',
            badges TEXT DEFAULT '[]',
            achievements TEXT DEFAULT '[]'
        );
        
        CREATE TABLE IF NOT EXISTS leaderboard (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            xp_points INTEGER DEFAULT 0,
            quiz_score INTEGER DEFAULT 0,
            cases_solved INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS clinical_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            patient_info TEXT,
            note TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS login_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            success BOOLEAN DEFAULT FALSE
        );
        
        CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
        CREATE INDEX IF NOT EXISTS idx_leaderboard_xp ON leaderboard(xp_points DESC);
        CREATE INDEX IF NOT EXISTS idx_login_attempts ON login_attempts(username, attempt_time);
    """)
    
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'language_preference' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN language_preference TEXT DEFAULT 'en'")
    
    conn.commit()

# ================================
# PASSWORD SECURITY
# ================================
def generate_salt(length: int = 32) -> str:
    return os.urandom(length).hex()

def hash_password_secure(password: str, salt: str = None) -> Tuple[str, str]:
    if salt is None:
        salt = generate_salt()
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 200000, dklen=64)
    return key.hex(), salt

def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    computed_hash, _ = hash_password_secure(password, salt)
    return computed_hash == stored_hash

def check_login_rate_limit(username: str) -> Tuple[bool, str]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT locked_until FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    if user and user['locked_until']:
        locked_until = datetime.fromisoformat(user['locked_until'])
        if locked_until > datetime.now():
            remaining = (locked_until - datetime.now()).seconds // 60
            return False, f"Account locked. Try again in {remaining} minutes."
    cutoff_time = datetime.now() - timedelta(minutes=LOGIN_TIMEOUT_MINUTES)
    cursor.execute("SELECT COUNT(*) as attempts FROM login_attempts WHERE username = ? AND attempt_time > ? AND success = FALSE", (username, cutoff_time))
    result = cursor.fetchone()
    recent_attempts = result['attempts'] if result else 0
    if recent_attempts >= MAX_LOGIN_ATTEMPTS:
        cursor.execute("UPDATE users SET locked_until = ? WHERE username = ?", ((datetime.now() + timedelta(minutes=LOGIN_TIMEOUT_MINUTES)).isoformat(), username))
        conn.commit()
        return False, f"Too many attempts. Account locked for {LOGIN_TIMEOUT_MINUTES} minutes."
    return True, ""

def record_login_attempt(username: str, success: bool):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO login_attempts (username, success) VALUES (?, ?)", (username, success))
    if success: cursor.execute("UPDATE users SET login_attempts = 0, locked_until = NULL WHERE username = ?", (username,))
    else: cursor.execute("UPDATE users SET login_attempts = login_attempts + 1 WHERE username = ?", (username,))
    conn.commit()

def create_user(username: str, password: str) -> Tuple[bool, str]:
    if len(username) < 3: return False, "Username must be at least 3 characters"
    if len(password) < 6: return False, "Password must be at least 6 characters"
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    if cursor.fetchone(): return False, "Username already exists"
    password_hash, salt = hash_password_secure(password)
    cursor.execute("INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)", (username, password_hash, salt))
    cursor.execute("INSERT INTO leaderboard (username, xp_points) VALUES (?, 0)", (username,))
    conn.commit()
    return True, "Account created successfully"

def authenticate_user(username: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
    can_attempt, message = check_login_rate_limit(username)
    if not can_attempt: return False, message, None
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    if not user:
        record_login_attempt(username, False)
        return False, "Invalid username or password", None
    if verify_password(password, user['password_hash'], user['salt']):
        record_login_attempt(username, True)
        cursor.execute("UPDATE users SET last_login = ? WHERE id = ?", (datetime.now().isoformat(), user['id']))
        conn.commit()
        return True, "Login successful", dict(user)
    else:
        record_login_attempt(username, False)
        return False, "Invalid username or password", None

def update_user_streak(username: str) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT daily_streak, last_active_date FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    if not user: return 0
    today = datetime.now().date()
    last_active = datetime.fromisoformat(user['last_active_date']).date() if user['last_active_date'] else None
    if last_active:
        yesterday = today - timedelta(days=1)
        if last_active == yesterday: new_streak = user['daily_streak'] + 1
        elif last_active == today: new_streak = user['daily_streak']
        else: new_streak = 1
    else: new_streak = 1
    cursor.execute("UPDATE users SET daily_streak = ?, last_active_date = ? WHERE username = ?", (new_streak, today.isoformat(), username))
    conn.commit()
    return new_streak

def add_xp(username: str, points: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET xp_points = xp_points + ? WHERE username = ?", (points, username))
    cursor.execute("UPDATE leaderboard SET xp_points = xp_points + ?, last_active = ? WHERE username = ?", (points, datetime.now().isoformat(), username))
    conn.commit()

# ================================
# LEVEL SYSTEM
# ================================
LEVELS = {
    1: {"name_en": "Medical Student", "name_ku": "خوێندکاری پزیشکی", "name_ar": "طالب طب", "icon": "🌱", "min_xp": 0},
    2: {"name_en": "Intern", "name_ku": "کارمەندی ڕاهێنان", "name_ar": "طبيب امتياز", "icon": "📖", "min_xp": 100},
    3: {"name_en": "Resident", "name_ku": "پزیشکی دانیشتوو", "name_ar": "طبيب مقيم", "icon": "🚀", "min_xp": 300},
    4: {"name_en": "Specialist", "name_ku": "پزیشکی پسپۆڕ", "name_ar": "أخصائي", "icon": "🏆", "min_xp": 600},
    5: {"name_en": "Consultant", "name_ku": "پزیشکی ڕاوێژکار", "name_ar": "استشاري", "icon": "👨‍⚕️", "min_xp": 1000},
    6: {"name_en": "Professor", "name_ku": "پڕۆفیسۆر", "name_ar": "أستاذ", "icon": "🎓", "min_xp": 2000},
    7: {"name_en": "Legend", "name_ku": "ئەفسانە", "name_ar": "أسطورة", "icon": "👑", "min_xp": 5000}
}

def get_level_name(level: int, lang: str = 'en') -> str:
    return LEVELS[level].get(f"name_{lang}", LEVELS[level]["name_en"])

def get_user_level(xp_points: int) -> int:
    for level in range(7, 0, -1):
        if xp_points >= LEVELS[level]["min_xp"]: return level
    return 1

def get_level_progress(xp_points: int) -> float:
    current_level = get_user_level(xp_points)
    if current_level >= 7: return 100.0
    current_min = LEVELS[current_level]["min_xp"]
    next_min = LEVELS[current_level + 1]["min_xp"]
    return min(((xp_points - current_min) / (next_min - current_min)) * 100, 100)

# ================================
# 200 LAB TESTS DATABASE
# ================================
LAB_TESTS = {}

hematology = {
    "Hemoglobin": "Oxygen-carrying capacity|12-16 g/dL",
    "WBC Count": "Infection/inflammation marker|4,000-11,000/µL",
    "RBC Count": "Oxygen transport|4.5-5.5 million/µL",
    "Hematocrit": "RBC volume percentage|37-47%",
    "MCV": "RBC size|80-100 fL",
    "MCH": "Hemoglobin per RBC|27-33 pg",
    "MCHC": "Hemoglobin concentration|32-36 g/dL",
    "RDW": "RBC size variation|11.5-14.5%",
    "Platelet Count": "Clotting ability|150,000-450,000/µL",
    "MPV": "Platelet size|7.5-11.5 fL",
    "Reticulocyte Count": "Bone marrow activity|0.5-2.5%",
    "ESR": "Inflammation marker|0-20 mm/hr",
    "Ferritin": "Iron stores|15-300 ng/mL",
    "Serum Iron": "Circulating iron|60-170 µg/dL",
    "TIBC": "Iron binding capacity|250-450 µg/dL",
    "Transferrin Saturation": "Iron saturation|20-50%",
    "Vitamin B12": "B12 deficiency marker|200-900 pg/mL",
    "Folate": "Folate deficiency marker|3-17 ng/mL",
    "PT": "Extrinsic pathway|11-13.5 sec",
    "PTT": "Intrinsic pathway|25-35 sec",
    "INR": "Coagulation status|0.9-1.1",
    "Fibrinogen": "Clotting factor|200-400 mg/dL",
    "D-Dimer": "Thrombosis marker|<0.5 mg/L",
    "Haptoglobin": "Hemolysis marker|50-250 mg/dL",
    "LDH": "Cell damage marker|100-250 U/L",
    "Reticulocyte Index": "Corrected reticulocyte count|1-2",
    "Peripheral Smear": "RBC morphology|Normal morphology",
    "Hemoglobin Electrophoresis": "Hemoglobin variants|HbA >95%",
    "G6PD": "Enzyme deficiency|5-15 U/g Hb",
    "Osmotic Fragility": "RBC membrane stability|0.45-0.35% NaCl",
    "Bone Marrow Biopsy": "Marrow cellularity|40-70%",
    "Serum Haptoglobin": "Intravascular hemolysis|30-200 mg/dL",
    "Plasma Free Hemoglobin": "Hemolysis|<5 mg/dL",
    "Methemoglobin": "Oxidized hemoglobin|<1.5%",
    "Carboxyhemoglobin": "Carbon monoxide exposure|<2% (non-smokers)",
    "Erythropoietin": "RBC production stimulus|4-26 mU/mL",
    "Soluble Transferrin Receptor": "Iron deficiency anemia|0.8-2.3 mg/L",
    "Hepcidin": "Iron regulation|<50 ng/mL",
    "Heinz Body Preparation": "Oxidative damage|Negative",
    "Hemoglobin A2": "Beta-thalassemia marker|2.2-3.5%",
}
for name, info in hematology.items():
    desc, normal = info.split("|")
    LAB_TESTS[name] = {"category": "Hematology", "normal": normal.strip(), "description_en": desc.strip(), "description_ku": desc.strip(), "description_ar": desc.strip()}

biochemistry = {
    "Fasting Glucose": "Diabetes screening|70-100 mg/dL",
    "HbA1c": "3-month glucose average|4.0-5.6%",
    "Creatinine": "Kidney function|0.6-1.3 mg/dL",
    "BUN": "Kidney function|7-20 mg/dL",
    "eGFR": "Kidney filtration rate|>90 mL/min",
    "Uric Acid": "Gout marker|3.5-7.2 mg/dL",
    "Total Protein": "Nutritional status|6.0-8.0 g/dL",
    "Albumin": "Liver function|3.5-5.0 g/dL",
    "Globulin": "Immune proteins|2.0-3.5 g/dL",
    "Total Bilirubin": "Jaundice marker|0.1-1.2 mg/dL",
    "Direct Bilirubin": "Conjugated bilirubin|0.0-0.3 mg/dL",
    "Indirect Bilirubin": "Unconjugated bilirubin|0.1-0.9 mg/dL",
    "ALT": "Liver enzyme|10-40 U/L",
    "AST": "Liver/muscle enzyme|10-40 U/L",
    "ALP": "Bone/liver enzyme|44-147 U/L",
    "GGT": "Liver/biliary enzyme|0-51 U/L",
    "Amylase": "Pancreatic enzyme|20-200 U/L",
    "Lipase": "Pancreatic enzyme|20-200 U/L",
    "CK": "Muscle enzyme|22-198 U/L",
    "CK-MB": "Cardiac enzyme|0-5 ng/mL",
    "Sodium": "Electrolyte|135-145 mmol/L",
    "Potassium": "Electrolyte|3.5-5.0 mmol/L",
    "Chloride": "Electrolyte|96-106 mmol/L",
    "Calcium": "Bone metabolism|8.5-10.5 mg/dL",
    "Ionized Calcium": "Active calcium|4.5-5.6 mg/dL",
    "Magnesium": "Neuromuscular function|1.7-2.2 mg/dL",
    "Phosphorus": "Bone metabolism|2.5-4.5 mg/dL",
    "Total Cholesterol": "Lipid profile|<200 mg/dL",
    "LDL Cholesterol": "Bad cholesterol|<100 mg/dL",
    "HDL Cholesterol": "Good cholesterol|>40 mg/dL",
    "Triglycerides": "Blood fats|<150 mg/dL",
    "VLDL": "Very low density lipoprotein|<30 mg/dL",
    "ApoA": "Cardioprotective|90-150 mg/dL",
    "ApoB": "Atherogenic|60-120 mg/dL",
    "Lipoprotein(a)": "Genetic cardiac risk|<30 mg/dL",
    "hs-CRP": "Cardiovascular risk|<2 mg/L",
    "Homocysteine": "Vascular risk|5-15 µmol/L",
    "Ammonia": "Liver function|15-45 µg/dL",
    "Lactate": "Tissue perfusion|0.5-2.2 mmol/L",
    "Pyruvate": "Metabolic status|0.3-0.9 mg/dL",
    "Osmolality": "Fluid balance|275-295 mOsm/kg",
    "Anion Gap": "Metabolic acidosis|8-16 mEq/L",
    "Serum Ketones": "Ketosis|<0.6 mmol/L",
    "Ceruloplasmin": "Wilson disease|20-60 mg/dL",
    "Alpha-1 Antitrypsin": "Emphysema/liver|100-200 mg/dL",
    "ACE Level": "Sarcoidosis|8-53 U/L",
    "Cystatin C": "Kidney function|0.6-1.0 mg/L",
    "C-reactive Protein": "Acute inflammation|<5 mg/L",
    "Prealbumin": "Nutritional status|15-35 mg/dL",
    "Beta-2 Microglobulin": "Tumor marker|1-2 mg/L",
}
for name, info in biochemistry.items():
    desc, normal = info.split("|")
    LAB_TESTS[name] = {"category": "Biochemistry", "normal": normal.strip(), "description_en": desc.strip(), "description_ku": desc.strip(), "description_ar": desc.strip()}

cardiac = {
    "Troponin I": "Myocardial injury|<0.04 ng/mL",
    "Troponin T": "High-sensitivity cardiac|<0.014 ng/mL",
    "BNP": "Heart failure|<100 pg/mL",
    "NT-proBNP": "Heart failure|<125 pg/mL",
    "Myoglobin": "Early cardiac marker|<80 ng/mL",
    "CK-MB Mass": "Cardiac-specific|0-5 ng/mL",
    "hs-CRP Cardiac": "Cardiovascular risk|<2 mg/L",
    "Homocysteine Cardiac": "Vascular risk|5-15 µmol/L",
    "Lipoprotein(a) Cardiac": "Genetic risk|<30 mg/dL",
    "ApoB Cardiac": "Atherogenic particles|60-120 mg/dL",
    "Ischemia Modified Albumin": "Early ischemia|<85 U/mL",
    "Heart-type FABP": "Early MI marker|<6 ng/mL",
    "ST2": "Cardiac remodeling|<35 ng/mL",
    "Galectin-3": "Cardiac fibrosis|<22 ng/mL",
    "Copeptin": "Stress response|<14 pmol/L",
}
for name, info in cardiac.items():
    desc, normal = info.split("|")
    LAB_TESTS[name] = {"category": "Cardiac", "normal": normal.strip(), "description_en": desc.strip(), "description_ku": desc.strip(), "description_ar": desc.strip()}

hormones = {
    "TSH": "Thyroid function|0.4-4.0 mIU/L",
    "Free T4": "Thyroid hormone|0.8-1.8 ng/dL",
    "Free T3": "Active thyroid hormone|2.3-4.2 pg/mL",
    "Total T4": "Total thyroxine|5-12 µg/dL",
    "Total T3": "Total triiodothyronine|80-200 ng/dL",
    "Reverse T3": "Inactive T3|10-24 ng/dL",
    "Thyroglobulin": "Thyroid tissue marker|<33 ng/mL",
    "Cortisol (AM)": "Adrenal function|6-23 µg/dL",
    "Cortisol (PM)": "Evening cortisol|3-15 µg/dL",
    "ACTH": "Pituitary function|10-60 pg/mL",
    "DHEA-S": "Adrenal androgen|35-430 µg/dL",
    "Testosterone (Male)": "Androgen|300-1000 ng/dL",
    "Testosterone (Female)": "Female androgen|15-70 ng/dL",
    "Free Testosterone": "Bioavailable testosterone|5-21 ng/dL",
    "Estradiol": "Estrogen|20-400 pg/mL",
    "Progesterone": "Ovulation marker|0.1-25 ng/mL",
    "Prolactin": "Pituitary function|4-23 ng/mL",
    "LH": "Reproductive hormone|1.5-9.3 IU/L",
    "FSH": "Reproductive hormone|1.4-18.1 IU/L",
    "SHBG": "Hormone binding|10-57 nmol/L",
    "Insulin (Fasting)": "Glucose metabolism|2-25 µIU/mL",
    "C-Peptide": "Insulin production|0.5-2.0 ng/mL",
    "IGF-1": "Growth factor|100-300 ng/mL",
    "PTH": "Calcium regulation|10-65 pg/mL",
    "Calcitonin": "Calcium regulation|<10 pg/mL",
    "Vitamin D (25-OH)": "Vitamin D status|30-100 ng/mL",
    "1,25-Dihydroxy Vitamin D": "Active vitamin D|20-60 pg/mL",
    "Aldosterone": "Mineralocorticoid|3-16 ng/dL",
    "Renin": "Blood pressure regulation|0.5-4.0 ng/mL/hr",
    "Catecholamines": "Stress hormones|Epinephrine <50 pg/mL",
}
for name, info in hormones.items():
    desc, normal = info.split("|")
    LAB_TESTS[name] = {"category": "Endocrine", "normal": normal.strip(), "description_en": desc.strip(), "description_ku": desc.strip(), "description_ar": desc.strip()}

urinalysis = {
    "Urine pH": "Acid-base balance|4.5-8.0",
    "Urine Specific Gravity": "Concentration|1.005-1.030",
    "Urine Protein": "Kidney damage|Negative",
    "Urine Glucose": "Diabetes|Negative",
    "Urine Ketones": "Starvation/DKA|Negative",
    "Urine Bilirubin": "Liver disease|Negative",
    "Urine Urobilinogen": "Hemolysis|0.1-1.0 mg/dL",
    "Urine Nitrite": "Bacteria indicator|Negative",
    "Urine Leukocyte Esterase": "WBC enzyme|Negative",
    "Urine WBC": "Infection|0-5/HPF",
    "Urine RBC": "Bleeding|0-3/HPF",
    "Urine Casts": "Cellular casts|None/LPF",
    "Urine Crystals": "Crystal formations|None",
    "Microalbumin": "Early nephropathy|<30 mg/24h",
    "24h Urine Protein": "Daily protein excretion|<150 mg/24h",
    "24h Urine Creatinine": "Creatinine clearance|15-25 mg/kg/24h",
    "Urine Calcium": "Calcium excretion|100-300 mg/24h",
    "Urine Uric Acid": "Uric acid excretion|250-750 mg/24h",
    "Urine Oxalate": "Kidney stone risk|<45 mg/24h",
    "Urine Citrate": "Stone inhibitor|>320 mg/24h",
}
for name, info in urinalysis.items():
    desc, normal = info.split("|")
    LAB_TESTS[name] = {"category": "Urinalysis", "normal": normal.strip(), "description_en": desc.strip(), "description_ku": desc.strip(), "description_ar": desc.strip()}

immunology = {
    "CRP": "Acute inflammation|<5 mg/L",
    "Rheumatoid Factor": "RA marker|<14 IU/mL",
    "ANA": "Autoimmune screening|Negative",
    "Anti-dsDNA": "SLE marker|<30 IU/mL",
    "C3 Complement": "Complement system|90-180 mg/dL",
    "C4 Complement": "Complement system|10-40 mg/dL",
    "IgG": "Humoral immunity|700-1600 mg/dL",
    "IgA": "Mucosal immunity|70-400 mg/dL",
    "IgM": "Acute infection|40-230 mg/dL",
    "IgE": "Allergy/parasites|0-100 IU/mL",
    "Anti-CCP": "RA specific|<20 U/mL",
    "ANCA": "Vasculitis|Negative",
    "Anti-Ro/SSA": "Sjogren syndrome|Negative",
    "Anti-La/SSB": "Sjogren syndrome|Negative",
    "Anti-Smith": "SLE specific|Negative",
    "Anti-RNP": "Mixed connective tissue disease|Negative",
    "Anti-Scl-70": "Scleroderma|Negative",
    "Anti-Jo-1": "Polymyositis|Negative",
    "Anti-Centromere": "CREST syndrome|Negative",
    "Anti-Histone": "Drug-induced lupus|Negative",
    "Cryoglobulins": "Vasculitis|Negative",
    "Procalcitonin": "Bacterial infection|<0.5 ng/mL",
    "IL-6": "Cytokine storm|<5 pg/mL",
    "TNF-alpha": "Inflammatory cytokine|<8 pg/mL",
    "Beta-2 Glycoprotein I": "Antiphospholipid syndrome|<20 U/mL",
}
for name, info in immunology.items():
    desc, normal = info.split("|")
    LAB_TESTS[name] = {"category": "Immunology", "normal": normal.strip(), "description_en": desc.strip(), "description_ku": desc.strip(), "description_ar": desc.strip()}

tumor_markers = {
    "CEA": "Colorectal cancer|<5 ng/mL",
    "CA 19-9": "Pancreatic cancer|<37 U/mL",
    "CA 125": "Ovarian cancer|<35 U/mL",
    "PSA": "Prostate cancer|<4 ng/mL",
    "AFP": "Liver cancer/Germ cell|<10 ng/mL",
    "Beta-hCG": "Germ cell tumors|<5 IU/L",
    "LDH Tumor": "Tumor burden|100-250 U/L",
    "CA 15-3": "Breast cancer|<30 U/mL",
    "Calcitonin Tumor": "Medullary thyroid cancer|<10 pg/mL",
    "NSE": "Neuroendocrine tumors|<15 ng/mL",
}
for name, info in tumor_markers.items():
    desc, normal = info.split("|")
    LAB_TESTS[name] = {"category": "Tumor Markers", "normal": normal.strip(), "description_en": desc.strip(), "description_ku": desc.strip(), "description_ar": desc.strip()}

microbiology = {
    "Blood Culture": "Bacteremia detection|No growth",
    "Urine Culture": "UTI diagnosis|<100,000 CFU/mL",
    "Sputum Culture": "Respiratory pathogens|Normal flora",
    "Stool Culture": "GI pathogens|No pathogens",
    "CSF Culture": "Meningitis diagnosis|No growth",
    "Throat Culture": "Strep detection|No Group A Strep",
    "Wound Culture": "Wound infection|No pathogens",
    "Gram Stain": "Bacterial classification|No organisms",
    "AFB Stain": "Tuberculosis screening|Negative",
    "Fungal Culture": "Fungal infection|No growth",
}
for name, info in microbiology.items():
    desc, normal = info.split("|")
    LAB_TESTS[name] = {"category": "Microbiology", "normal": normal.strip(), "description_en": desc.strip(), "description_ku": desc.strip(), "description_ar": desc.strip()}

# ================================
# 200 DRUG DATABASE
# ================================
DRUG_DATABASE = {
    "Cardiovascular": {}, "Endocrinology": {}, "Antibiotics": {},
    "Neurology & Psychiatry": {}, "Gastroenterology": {}, "Respiratory": {},
    "Analgesics & Anesthetics": {}, "Oncology": {}, "Dermatology": {}, "Ophthalmology": {},
}

cv_drugs = {
    "Lisinopril": "ACE Inhibitor|10-40mg daily|Hypertension, HF|Cough, angioedema",
    "Enalapril": "ACE Inhibitor|5-40mg daily|Hypertension, HF|Cough, hyperkalemia",
    "Captopril": "ACE Inhibitor|25-150mg TID|Hypertension, diabetic nephropathy|Cough, rash",
    "Ramipril": "ACE Inhibitor|2.5-20mg daily|Hypertension, post-MI|Cough, hypotension",
    "Losartan": "ARB|50-100mg daily|Hypertension, HF|Dizziness, hyperkalemia",
    "Valsartan": "ARB|80-320mg daily|Hypertension, HF|Headache, dizziness",
    "Telmisartan": "ARB|40-80mg daily|Hypertension|Back pain, sinusitis",
    "Irbesartan": "ARB|150-300mg daily|Hypertension, diabetic nephropathy|Diarrhea",
    "Candesartan": "ARB|8-32mg daily|Hypertension, HF|Dizziness, back pain",
    "Amlodipine": "CCB|5-10mg daily|Hypertension, angina|Edema, flushing",
    "Nifedipine": "CCB|30-90mg daily|Hypertension, angina|Headache, edema",
    "Diltiazem": "CCB|120-360mg daily|Hypertension, arrhythmia|Bradycardia, constipation",
    "Verapamil": "CCB|120-480mg daily|Hypertension, SVT|Constipation, dizziness",
    "Metoprolol": "Beta Blocker|25-200mg daily|Hypertension, angina, HF|Bradycardia, fatigue",
    "Atenolol": "Beta Blocker|25-100mg daily|Hypertension, angina|Bradycardia, fatigue",
    "Propranolol": "Beta Blocker|40-320mg daily|Hypertension, migraine, anxiety|Sleep disturbance",
    "Carvedilol": "Beta/Alpha Blocker|6.25-50mg BID|HF, hypertension|Dizziness, fatigue",
    "Bisoprolol": "Beta Blocker|2.5-10mg daily|Hypertension, HF|Bradycardia, cold extremities",
    "Hydrochlorothiazide": "Thiazide Diuretic|12.5-50mg daily|Hypertension, edema|Hypokalemia",
    "Furosemide": "Loop Diuretic|20-80mg daily|Edema, HF|Hypokalemia, dehydration",
    "Spironolactone": "Aldosterone Antagonist|25-100mg daily|HF, ascites|Hyperkalemia, gynecomastia",
    "Eplerenone": "Aldosterone Antagonist|25-50mg daily|HF post-MI|Hyperkalemia",
    "Atorvastatin": "Statin|10-80mg daily|Hyperlipidemia|Myalgia, elevated LFTs",
    "Rosuvastatin": "Statin|5-40mg daily|Hyperlipidemia|Myalgia, headache",
    "Simvastatin": "Statin|10-40mg daily|Hyperlipidemia|Myopathy, GI upset",
    "Clopidogrel": "Antiplatelet (P2Y12)|75mg daily|ACS, stroke prevention|Bleeding",
    "Aspirin": "Antiplatelet|75-325mg daily|CVD prevention|GI bleeding",
    "Warfarin": "Anticoagulant|2-10mg daily|DVT, PE, AF|Bleeding",
    "Rivaroxaban": "DOAC|10-20mg daily|DVT, PE, AF|Bleeding",
    "Apixaban": "DOAC|2.5-5mg BID|AF, DVT prevention|Bleeding",
}
for name, info in cv_drugs.items():
    parts = info.split("|")
    DRUG_DATABASE["Cardiovascular"][name] = {"class": parts[0], "dose": parts[1], "indications_en": parts[2], "indications_ku": parts[2], "indications_ar": parts[2], "side_effects_en": parts[3], "side_effects_ku": parts[3], "side_effects_ar": parts[3]}

endo_drugs = {
    "Metformin": "Biguanide|500-2000mg daily|Type 2 DM|GI upset, lactic acidosis",
    "Glipizide": "Sulfonylurea|5-20mg daily|Type 2 DM|Hypoglycemia, weight gain",
    "Glyburide": "Sulfonylurea|2.5-10mg daily|Type 2 DM|Hypoglycemia",
    "Pioglitazone": "TZD|15-45mg daily|Type 2 DM|Edema, fractures",
    "Sitagliptin": "DPP-4 Inhibitor|100mg daily|Type 2 DM|Headache, pancreatitis",
    "Empagliflozin": "SGLT2 Inhibitor|10-25mg daily|Type 2 DM, HF|UTI, DKA",
    "Dapagliflozin": "SGLT2 Inhibitor|5-10mg daily|Type 2 DM, CKD|Genital infections",
    "Insulin Glargine": "Long-acting Insulin|Individualized|Type 1 & 2 DM|Hypoglycemia",
    "Insulin Aspart": "Rapid-acting Insulin|Individualized|Type 1 & 2 DM|Hypoglycemia",
    "Insulin Lispro": "Rapid-acting Insulin|Individualized|Type 1 & 2 DM|Hypoglycemia",
    "Insulin Detemir": "Long-acting Insulin|Individualized|Type 1 & 2 DM|Hypoglycemia",
    "Levothyroxine": "Thyroid Hormone|25-200mcg daily|Hypothyroidism|Palpitations, insomnia",
    "Methimazole": "Antithyroid|5-30mg daily|Hyperthyroidism|Agranulocytosis",
    "Propylthiouracil": "Antithyroid|100-300mg daily|Hyperthyroidism|Hepatotoxicity",
    "Prednisone": "Corticosteroid|5-60mg daily|Inflammation, autoimmune|Weight gain, osteoporosis",
    "Hydrocortisone": "Corticosteroid|20-240mg daily|Adrenal insufficiency|Fluid retention",
    "Dexamethasone": "Corticosteroid|0.5-10mg daily|Inflammation, cerebral edema|Insomnia",
    "Alendronate": "Bisphosphonate|70mg weekly|Osteoporosis|Esophagitis",
    "Risedronate": "Bisphosphonate|35mg weekly|Osteoporosis|GI upset",
    "Teriparatide": "PTH Analog|20mcg daily|Osteoporosis|Hypercalcemia",
    "Denosumab": "RANKL Inhibitor|60mg q6months|Osteoporosis|Hypocalcemia",
    "Calcitriol": "Active Vitamin D|0.25-2mcg daily|Hypocalcemia, renal osteodystrophy|Hypercalcemia",
    "Desmopressin": "ADH Analog|0.1-0.4mg daily|Diabetes insipidus|Hyponatremia",
    "Octreotide": "Somatostatin Analog|50-200mcg TID|Acromegaly|Gallstones",
    "Bromocriptine": "Dopamine Agonist|2.5-15mg daily|Hyperprolactinemia|Nausea, orthostasis",
}
for name, info in endo_drugs.items():
    parts = info.split("|")
    DRUG_DATABASE["Endocrinology"][name] = {"class": parts[0], "dose": parts[1], "indications_en": parts[2], "indications_ku": parts[2], "indications_ar": parts[2], "side_effects_en": parts[3], "side_effects_ku": parts[3], "side_effects_ar": parts[3]}

abx_drugs = {
    "Amoxicillin": "Penicillin|500-875mg BID|Respiratory, UTI|Diarrhea, rash",
    "Amoxicillin-Clavulanate": "Penicillin+BLI|500/125mg TID|Broad spectrum|Diarrhea",
    "Ampicillin": "Penicillin|500mg QID|UTI, meningitis|Rash, diarrhea",
    "Cephalexin": "1st Gen Cephalosporin|250-500mg QID|Skin, UTI|GI upset",
    "Ceftriaxone": "3rd Gen Cephalosporin|1-2g IV daily|Serious infections|Diarrhea",
    "Cefuroxime": "2nd Gen Cephalosporin|250-500mg BID|Respiratory, skin|Diarrhea",
    "Cefixime": "3rd Gen Cephalosporin|400mg daily|Gonorrhea, UTI|Diarrhea",
    "Azithromycin": "Macrolide|250-500mg daily|Respiratory, STI|GI upset, QT prolongation",
    "Clarithromycin": "Macrolide|250-500mg BID|H. pylori, respiratory|GI upset, metallic taste",
    "Erythromycin": "Macrolide|250-500mg QID|Respiratory, skin|GI upset, QT prolongation",
    "Doxycycline": "Tetracycline|100mg BID|Acne, Lyme, malaria|Photosensitivity",
    "Minocycline": "Tetracycline|100mg BID|Acne, MRSA|Vertigo, hyperpigmentation",
    "Ciprofloxacin": "Fluoroquinolone|250-750mg BID|UTI, GI|Tendonitis, neuropathy",
    "Levofloxacin": "Fluoroquinolone|500-750mg daily|Respiratory, UTI|Tendon rupture",
    "Moxifloxacin": "Fluoroquinolone|400mg daily|Respiratory|QT prolongation",
    "Metronidazole": "Nitroimidazole|500mg TID|Anaerobic, C. diff|Metallic taste",
    "Clindamycin": "Lincosamide|150-450mg QID|Anaerobic, acne|C. diff colitis",
    "Vancomycin": "Glycopeptide|IV trough-guided|MRSA, C. diff (oral)|Red man syndrome",
    "TMP-SMX": "Sulfonamide|160/800mg BID|UTI, PCP|Rash, hyperkalemia",
    "Nitrofurantoin": "Nitrofuran|100mg BID|UTI prophylaxis|Pulmonary fibrosis",
    "Linezolid": "Oxazolidinone|600mg BID|VRE, MRSA|Myelosuppression",
    "Daptomycin": "Lipopeptide|4-6mg/kg IV|MRSA, VRE|Myopathy, CPK elevation",
    "Gentamicin": "Aminoglycoside|5-7mg/kg IV|Gram-negative|Nephrotoxicity, ototoxicity",
    "Tobramycin": "Aminoglycoside|5-7mg/kg IV|Pseudomonas|Nephrotoxicity",
    "Aztreonam": "Monobactam|1-2g IV q8h|Gram-negative (penicillin allergy)|Rash",
    "Meropenem": "Carbapenem|1g IV q8h|Broad spectrum, ESBL|Seizures",
    "Piperacillin-Tazobactam": "Penicillin+BLI|3.375-4.5g IV q6h|Pseudomonas, anaerobes|Diarrhea",
    "Colistin": "Polymyxin|IV weight-based|MDR gram-negative|Nephrotoxicity, neurotoxicity",
    "Tigecycline": "Glycylcycline|100mg IV loading|MDR infections|Nausea, pancreatitis",
    "Fidaxomicin": "Macrocyclic|200mg BID|C. difficile|GI upset",
}
for name, info in abx_drugs.items():
    parts = info.split("|")
    DRUG_DATABASE["Antibiotics"][name] = {"class": parts[0], "dose": parts[1], "indications_en": parts[2], "indications_ku": parts[2], "indications_ar": parts[2], "side_effects_en": parts[3], "side_effects_ku": parts[3], "side_effects_ar": parts[3]}

neuro_drugs = {
    "Sertraline": "SSRI|50-200mg daily|Depression, anxiety, PTSD|GI upset, sexual dysfunction",
    "Fluoxetine": "SSRI|20-80mg daily|Depression, OCD, bulimia|Insomnia, weight changes",
    "Escitalopram": "SSRI|10-20mg daily|Depression, GAD|Nausea, fatigue",
    "Paroxetine": "SSRI|20-50mg daily|Depression, anxiety|Sedation, weight gain",
    "Venlafaxine": "SNRI|75-375mg daily|Depression, anxiety|Hypertension, sweating",
    "Duloxetine": "SNRI|30-120mg daily|Depression, neuropathic pain|Nausea, dry mouth",
    "Amitriptyline": "TCA|25-150mg nightly|Depression, neuropathic pain|Sedation, anticholinergic",
    "Nortriptyline": "TCA|25-100mg daily|Neuropathic pain, depression|Sedation, dry mouth",
    "Quetiapine": "Atypical Antipsychotic|25-800mg daily|Schizophrenia, bipolar|Weight gain, metabolic syndrome",
    "Risperidone": "Atypical Antipsychotic|1-6mg daily|Schizophrenia, bipolar|Hyperprolactinemia, EPS",
    "Olanzapine": "Atypical Antipsychotic|5-20mg daily|Schizophrenia, bipolar|Weight gain, diabetes",
    "Aripiprazole": "Atypical Antipsychotic|10-30mg daily|Schizophrenia, bipolar|Akathisia, insomnia",
    "Lithium": "Mood Stabilizer|300-1800mg daily|Bipolar disorder|Tremor, nephrotoxicity",
    "Valproic Acid": "Mood Stabilizer/AED|250-3000mg daily|Bipolar, epilepsy|Weight gain, hepatotoxicity",
    "Carbamazepine": "AED|200-1600mg daily|Epilepsy, trigeminal neuralgia|Hyponatremia, SJS",
    "Gabapentin": "Gabapentinoid|300-3600mg daily|Neuropathic pain, epilepsy|Sedation, dizziness",
    "Pregabalin": "Gabapentinoid|75-600mg daily|Neuropathic pain, fibromyalgia|Dizziness, edema",
    "Levetiracetam": "AED|500-3000mg daily|Epilepsy|Behavioral changes, sedation",
    "Phenytoin": "AED|200-400mg daily|Epilepsy|Gingival hyperplasia, nystagmus",
    "Lamotrigine": "AED|25-400mg daily|Epilepsy, bipolar|Rash, SJS",
    "Topiramate": "AED|25-400mg daily|Epilepsy, migraine|Weight loss, cognitive impairment",
    "Donepezil": "Cholinesterase Inhibitor|5-10mg daily|Alzheimer's|GI upset, bradycardia",
    "Rivastigmine": "Cholinesterase Inhibitor|3-12mg daily|Alzheimer's, Parkinson dementia|Nausea, vomiting",
    "Memantine": "NMDA Antagonist|5-20mg daily|Alzheimer's|Dizziness, confusion",
    "Sumatriptan": "Triptan|50-100mg PRN|Acute migraine|Chest tightness, paresthesia",
    "Rizatriptan": "Triptan|5-10mg PRN|Acute migraine|Dizziness, fatigue",
    "Levodopa/Carbidopa": "Dopamine Precursor|100/25mg TID|Parkinson's|Dyskinesia, nausea",
    "Pramipexole": "Dopamine Agonist|0.125-1.5mg TID|Parkinson's, RLS|Impulse control disorder",
    "Ropinirole": "Dopamine Agonist|0.25-4mg TID|Parkinson's, RLS|Nausea, somnolence",
    "Entacapone": "COMT Inhibitor|200mg with levodopa|Parkinson's (wearing-off)|Diarrhea, urine discoloration",
}
for name, info in neuro_drugs.items():
    parts = info.split("|")
    DRUG_DATABASE["Neurology & Psychiatry"][name] = {"class": parts[0], "dose": parts[1], "indications_en": parts[2], "indications_ku": parts[2], "indications_ar": parts[2], "side_effects_en": parts[3], "side_effects_ku": parts[3], "side_effects_ar": parts[3]}

gi_drugs = {
    "Omeprazole": "PPI|20-40mg daily|GERD, PUD, H. pylori|Headache, B12 deficiency",
    "Pantoprazole": "PPI|40mg daily|GERD, erosive esophagitis|Headache, diarrhea",
    "Esomeprazole": "PPI|20-40mg daily|GERD, H. pylori|GI upset",
    "Famotidine": "H2 Antagonist|20-40mg BID|GERD, PUD|Constipation, diarrhea",
    "Ondansetron": "5-HT3 Antagonist|4-8mg PRN|Nausea, vomiting|Headache, constipation",
    "Metoclopramide": "Dopamine Antagonist|10mg TID|Gastroparesis, nausea|EPS, tardive dyskinesia",
    "Loperamide": "Opioid Agonist|2-4mg PRN|Acute diarrhea|Constipation",
    "Mesalamine": "5-ASA|2.4-4.8g daily|Ulcerative colitis|Headache, GI upset",
    "Lactulose": "Osmotic Laxative|15-30mL daily|Constipation, hepatic encephalopathy|Bloating",
    "Ursodeoxycholic Acid": "Bile Acid|10-15mg/kg daily|PBC, gallstones|Diarrhea",
    "Sucralfate": "Mucosal Protectant|1g QID|Peptic ulcer|Constipation",
    "Bismuth Subsalicylate": "Antisecretory|524mg QID|Diarrhea, H. pylori|Black stool, tinnitus",
    "Infliximab": "Anti-TNF|5mg/kg IV|Crohn's, UC|Infection, malignancy",
    "Adalimumab": "Anti-TNF|40mg SC q2weeks|Crohn's, UC|Injection site reaction",
    "Vedolizumab": "Anti-integrin|300mg IV|UC, Crohn's|Infection",
    "Polyethylene Glycol": "Osmotic Laxative|17g daily|Constipation|Bloating",
    "Dicyclomine": "Anticholinergic|20mg QID|IBS|Dry mouth, blurred vision",
    "Prochlorperazine": "Antiemetic|5-10mg TID|Nausea, vertigo|Sedation, EPS",
    "Lubiprostone": "Chloride Channel Activator|24mcg BID|Chronic constipation|Nausea",
    "Linaclotide": "Guanylate Cyclase-C Agonist|145-290mcg daily|IBS-C, chronic constipation|Diarrhea",
}
for name, info in gi_drugs.items():
    parts = info.split("|")
    DRUG_DATABASE["Gastroenterology"][name] = {"class": parts[0], "dose": parts[1], "indications_en": parts[2], "indications_ku": parts[2], "indications_ar": parts[2], "side_effects_en": parts[3], "side_effects_ku": parts[3], "side_effects_ar": parts[3]}

resp_drugs = {
    "Albuterol": "SABA|2 puffs Q4-6H PRN|Asthma, COPD|Tremor, tachycardia",
    "Salmeterol": "LABA|50mcg BID|Asthma, COPD maintenance|Tremor, palpitations",
    "Fluticasone": "ICS|100-500mcg BID|Asthma maintenance|Oral thrush, dysphonia",
    "Budesonide": "ICS|200-800mcg BID|Asthma, COPD|Cough, oral candidiasis",
    "Montelukast": "Leukotriene Antagonist|10mg daily|Asthma, allergic rhinitis|Headache",
    "Tiotropium": "LAMA|18mcg daily|COPD|Dry mouth, constipation",
    "Ipratropium": "SAMA|2-4 puffs QID|COPD, asthma|Dry mouth",
    "Theophylline": "Methylxanthine|200-600mg daily|Asthma, COPD|Nausea, seizures",
    "Roflumilast": "PDE-4 Inhibitor|500mcg daily|Severe COPD|Diarrhea, weight loss",
    "Formoterol": "LABA|12mcg BID|Asthma, COPD|Tremor",
    "Beclomethasone": "ICS|40-80mcg BID|Asthma|Oral thrush",
    "Zafirlukast": "Leukotriene Antagonist|20mg BID|Asthma|Headache, hepatotoxicity",
    "Omalizumab": "Anti-IgE|150-375mg SC|Severe allergic asthma|Anaphylaxis",
    "Mepolizumab": "Anti-IL5|100mg SC|Severe eosinophilic asthma|Headache",
    "Benralizumab": "Anti-IL5R|30mg SC|Severe eosinophilic asthma|Headache",
}
for name, info in resp_drugs.items():
    parts = info.split("|")
    DRUG_DATABASE["Respiratory"][name] = {"class": parts[0], "dose": parts[1], "indications_en": parts[2], "indications_ku": parts[2], "indications_ar": parts[2], "side_effects_en": parts[3], "side_effects_ku": parts[3], "side_effects_ar": parts[3]}

pain_drugs = {
    "Ibuprofen": "NSAID|200-800mg TID|Pain, inflammation|GI ulcer, renal impairment",
    "Naproxen": "NSAID|250-500mg BID|Pain, inflammation|GI upset",
    "Celecoxib": "COX-2 Inhibitor|100-200mg BID|Osteoarthritis, RA|Cardiovascular risk",
    "Acetaminophen": "Analgesic|500-1000mg Q6H|Pain, fever|Hepatotoxicity",
    "Tramadol": "Weak Opioid+SNRI|50-100mg Q6H|Moderate pain|Nausea, seizures",
    "Morphine": "Opioid Agonist|5-30mg Q4H|Severe pain|Respiratory depression",
    "Oxycodone": "Opioid Agonist|5-30mg Q4-6H|Severe pain|Respiratory depression",
    "Fentanyl": "Opioid Agonist|12-100mcg/hr patch|Chronic severe pain|Respiratory depression",
    "Hydromorphone": "Opioid Agonist|2-4mg Q4-6H|Severe pain|Respiratory depression",
    "Methadone": "Opioid Agonist|2.5-10mg Q8-12H|Chronic pain, addiction|QT prolongation",
    "Buprenorphine": "Partial Opioid Agonist|2-24mg SL|Chronic pain, addiction|Respiratory depression",
    "Lidocaine": "Local Anesthetic|1-2% solution|Local anesthesia|CNS toxicity",
    "Bupivacaine": "Local Anesthetic|0.25-0.5% solution|Regional anesthesia|Cardiotoxicity",
    "Ketamine": "NMDA Antagonist|0.5-2mg/kg IV|Anesthesia, pain|Hallucinations",
    "Propofol": "GABA Agonist|1-2mg/kg IV|Anesthesia induction|Respiratory depression",
    "Midazolam": "Benzodiazepine|1-5mg IV|Sedation, anxiolysis|Respiratory depression",
    "Gabapentin (Pain)": "Gabapentinoid|300-3600mg daily|Neuropathic pain|Sedation",
    "Pregabalin (Pain)": "Gabapentinoid|75-600mg daily|Neuropathic pain|Dizziness",
    "Diclofenac": "NSAID|50mg TID|Pain, inflammation|GI upset",
    "Meloxicam": "NSAID|7.5-15mg daily|Osteoarthritis|GI upset, edema",
}
for name, info in pain_drugs.items():
    parts = info.split("|")
    DRUG_DATABASE["Analgesics & Anesthetics"][name] = {"class": parts[0], "dose": parts[1], "indications_en": parts[2], "indications_ku": parts[2], "indications_ar": parts[2], "side_effects_en": parts[3], "side_effects_ku": parts[3], "side_effects_ar": parts[3]}

onco_drugs = {
    "Cyclophosphamide": "Alkylating Agent|500-1000mg/m2 IV|Lymphoma, leukemia, breast cancer|Myelosuppression, hemorrhagic cystitis",
    "Doxorubicin": "Anthracycline|60-75mg/m2 IV|Breast, lung, lymphoma|Cardiotoxicity, myelosuppression",
    "Cisplatin": "Platinum Analog|50-100mg/m2 IV|Testicular, ovarian, lung|Nephrotoxicity, ototoxicity",
    "Carboplatin": "Platinum Analog|AUC 5-6 IV|Ovarian, lung|Myelosuppression",
    "5-Fluorouracil": "Antimetabolite|400-600mg/m2 IV|Colorectal, breast|Mucositis, diarrhea",
    "Methotrexate": "Antimetabolite|Variable dosing|Leukemia, lymphoma, RA|Myelosuppression, hepatotoxicity",
    "Paclitaxel": "Taxane|175mg/m2 IV|Breast, ovarian, lung|Neuropathy, hypersensitivity",
    "Docetaxel": "Taxane|75-100mg/m2 IV|Breast, prostate, lung|Myelosuppression, fluid retention",
    "Tamoxifen": "SERM|20mg daily|Breast cancer (ER+)|Hot flashes, endometrial cancer",
    "Imatinib": "Tyrosine Kinase Inhibitor|400mg daily|CML, GIST|Edema, nausea",
    "Rituximab": "Anti-CD20|375mg/m2 IV|Lymphoma, CLL|Infusion reaction, infection",
    "Trastuzumab": "Anti-HER2|4-8mg/kg IV|Breast cancer (HER2+)|Cardiotoxicity",
    "Bevacizumab": "Anti-VEGF|5-15mg/kg IV|Colorectal, lung, renal|Hypertension, bleeding",
    "Pembrolizumab": "Anti-PD1|200mg IV q3weeks|Melanoma, lung, many cancers|Immune-related adverse events",
    "Lenalidomide": "Immunomodulator|10-25mg daily|Multiple myeloma|Myelosuppression, thrombosis",
}
for name, info in onco_drugs.items():
    parts = info.split("|")
    DRUG_DATABASE["Oncology"][name] = {"class": parts[0], "dose": parts[1], "indications_en": parts[2], "indications_ku": parts[2], "indications_ar": parts[2], "side_effects_en": parts[3], "side_effects_ku": parts[3], "side_effects_ar": parts[3]}

derm_drugs = {
    "Hydrocortisone Topical": "Topical Steroid|1% cream BID|Eczema, dermatitis|Skin atrophy",
    "Betamethasone": "Topical Steroid|0.1% cream BID|Psoriasis, eczema|Skin atrophy, striae",
    "Clotrimazole": "Topical Antifungal|1% cream BID|Tinea, candidiasis|Local irritation",
    "Mupirocin": "Topical Antibiotic|2% ointment TID|Impetigo, MRSA colonization|Burning",
    "Tretinoin": "Retinoid|0.025-0.1% nightly|Acne, photoaging|Irritation, photosensitivity",
    "Isotretinoin": "Oral Retinoid|0.5-1mg/kg daily|Severe acne|Teratogenicity, hyperlipidemia",
    "Adapalene": "Topical Retinoid|0.1% gel nightly|Acne|Dryness, irritation",
    "Tacrolimus Topical": "Calcineurin Inhibitor|0.1% ointment BID|Atopic dermatitis|Burning, pruritus",
    "Ustekinumab": "Anti-IL12/23|45-90mg SC|Psoriasis|Infection",
    "Secukinumab": "Anti-IL17A|300mg SC|Psoriasis|Infection, candidiasis",
}
for name, info in derm_drugs.items():
    parts = info.split("|")
    DRUG_DATABASE["Dermatology"][name] = {"class": parts[0], "dose": parts[1], "indications_en": parts[2], "indications_ku": parts[2], "indications_ar": parts[2], "side_effects_en": parts[3], "side_effects_ku": parts[3], "side_effects_ar": parts[3]}

ophth_drugs = {
    "Timolol": "Beta Blocker|0.5% drops BID|Glaucoma|Bradycardia, bronchospasm",
    "Latanoprost": "Prostaglandin Analog|0.005% nightly|Glaucoma|Iris pigmentation",
    "Brimonidine": "Alpha-2 Agonist|0.2% drops TID|Glaucoma|Allergic conjunctivitis",
    "Dorzolamide": "Carbonic Anhydrase Inhibitor|2% drops TID|Glaucoma|Bitter taste",
    "Cyclosporine Ophthalmic": "Immunomodulator|0.05% BID|Dry eye|Burning",
}
for name, info in ophth_drugs.items():
    parts = info.split("|")
    DRUG_DATABASE["Ophthalmology"][name] = {"class": parts[0], "dose": parts[1], "indications_en": parts[2], "indications_ku": parts[2], "indications_ar": parts[2], "side_effects_en": parts[3], "side_effects_ku": parts[3], "side_effects_ar": parts[3]}

# ================================
# DISEASE DATABASE
# ================================
DISEASE_DATABASE = {
    "Diabetes Mellitus Type 1": {"symptoms_en": ["Polyuria", "Polydipsia", "Weight loss", "Fatigue", "Blurred vision", "Ketoacidosis"], "symptoms_ku": ["میزی زۆر", "تینوویەتی زۆر", "کێش کەمبوونەوە", "ماندوویی", "بینی تەڵخ", "کیتۆئەسیدۆز"], "symptoms_ar": ["كثرة التبول", "العطش الشديد", "فقدان الوزن", "التعب", "عدم وضوح الرؤية", "الحماض الكيتوني"], "treatment_en": ["Insulin therapy", "Carbohydrate counting", "Regular exercise"], "treatment_ku": ["چارەسەری ئەنسولین", "ژمێریاری کاربۆهیدرات", "وەرزشی ڕێک"], "treatment_ar": ["العلاج بالأنسولين", "حساب الكربوهيدرات", "التمارين المنتظمة"], "risk_level": "High"},
    "Diabetes Mellitus Type 2": {"symptoms_en": ["Polyuria", "Polydipsia", "Fatigue", "Slow wound healing"], "symptoms_ku": ["میزی زۆر", "تینوویەتی زۆر", "ماندوویی", "خاوی چاکبوونەوەی برین"], "symptoms_ar": ["كثرة التبول", "العطش الشديد", "التعب", "بطء التئام الجروح"], "treatment_en": ["Metformin", "Lifestyle modification", "Regular exercise"], "treatment_ku": ["مێتفۆرمین", "گۆڕینی شێوازی ژیان", "وەرزشی ڕێک"], "treatment_ar": ["الميتفورمين", "تعديل نمط الحياة", "التمارين المنتظمة"], "risk_level": "Moderate"},
    "Essential Hypertension": {"symptoms_en": ["Often asymptomatic", "Headache", "Dizziness", "Blurred vision"], "symptoms_ku": ["زۆرجار بێ نیشانە", "سەرئێشە", "سەرگێژخواردن", "بینی تەڵخ"], "symptoms_ar": ["غالباً بدون أعراض", "صداع", "دوخة", "عدم وضوح الرؤية"], "treatment_en": ["ACE inhibitors", "Lifestyle changes", "Low sodium diet"], "treatment_ku": ["بەرگرەکانی ACE", "گۆڕینی شێوازی ژیان", "خواردنی کەم نمەک"], "treatment_ar": ["مثبطات ACE", "تغيير نمط الحياة", "نظام غذائي منخفض الصوديوم"], "risk_level": "Low"},
    "Acute Myocardial Infarction": {"symptoms_en": ["Severe chest pain", "Diaphoresis", "Dyspnea", "Nausea", "Anxiety"], "symptoms_ku": ["ئازاری توندی سنگ", "ئارەقەکردنی زۆر", "تەنگی هەناسە", "سکچوون", "دڵەڕاوکێ"], "symptoms_ar": ["ألم شديد في الصدر", "تعرق غزير", "ضيق التنفس", "غثيان", "قلق"], "treatment_en": ["Aspirin 300mg", "Nitroglycerin", "Morphine", "Oxygen"], "treatment_ku": ["ئەسپیرین ٣٠٠مگ", "نایترۆگلیسیرین", "مۆرفین", "ئۆکسجین"], "treatment_ar": ["أسبرين 300 ملغ", "نيتروجليسرين", "مورفين", "أكسجين"], "risk_level": "Critical"},
    "Community-Acquired Pneumonia": {"symptoms_en": ["Fever", "Productive cough", "Dyspnea", "Pleuritic chest pain"], "symptoms_ku": ["تا", "کۆخەی بەرھەمدار", "تەنگی هەناسە", "ئازاری سنگی پلوریتی"], "symptoms_ar": ["حمى", "سعال منتج", "ضيق التنفس", "ألم صدري جنبي"], "treatment_en": ["Amoxicillin-clavulanate", "Azithromycin", "Oxygen if needed"], "treatment_ku": ["ئەمۆکسیسیلین-کلاڤولانات", "ئازیترۆمایسین", "ئۆکسجین ئەگەر پێویست بوو"], "treatment_ar": ["أموكسيسيلين-كلافولانات", "أزيثروميسين", "أكسجين إذا لزم"], "risk_level": "Moderate"},
    "Bronchial Asthma": {"symptoms_en": ["Wheezing", "Dyspnea", "Chest tightness", "Cough"], "symptoms_ku": ["فیشک", "تەنگی هەناسە", "گرژبوونی سنگ", "کۆخە"], "symptoms_ar": ["صفير", "ضيق التنفس", "ضيق الصدر", "سعال"], "treatment_en": ["SABA (Albuterol)", "ICS (Budesonide)", "Avoid triggers"], "treatment_ku": ["SABA (ئەلبوتێرۆل)", "ICS (بودێسۆناید)", "خۆپاراستن لە هۆکارەکان"], "treatment_ar": ["SABA (ألبوتيرول)", "ICS (بوديزونيد)", "تجنب المحفزات"], "risk_level": "Low"},
    "Iron Deficiency Anemia": {"symptoms_en": ["Fatigue", "Pallor", "Dyspnea on exertion", "Palpitations"], "symptoms_ku": ["ماندوویی", "ڕەنگی پێست زەرد", "تەنگی هەناسە لە چالاکیدا", "لێدانی دڵ"], "symptoms_ar": ["التعب", "شحوب", "ضيق التنفس عند الجهد", "خفقان"], "treatment_en": ["Ferrous sulfate 325mg", "Vitamin C", "Iron-rich diet"], "treatment_ku": ["فێرۆس سەلفەیت ٣٢٥مگ", "ڤیتامین C", "خواردنی پڕ ئاسن"], "treatment_ar": ["كبريتات الحديدوز 325 ملغ", "فيتامين C", "نظام غذائي غني بالحديد"], "risk_level": "Low"},
    "Chronic Kidney Disease": {"symptoms_en": ["Edema", "Fatigue", "Decreased urine output", "Nausea"], "symptoms_ku": ["ئاوسان", "ماندوویی", "کەمبوونی میز", "سکچوون"], "symptoms_ar": ["وذمة", "التعب", "انخفاض إخراج البول", "غثيان"], "treatment_en": ["ACE inhibitors", "Dietary restriction", "Dialysis if ESRD"], "treatment_ku": ["بەرگرەکانی ACE", "سنووردارکردنی خواردن", "دیالیز ئەگەر ESRD"], "treatment_ar": ["مثبطات ACE", "تقييد غذائي", "غسيل الكلى إذا لزم"], "risk_level": "High"},
    "Hepatitis B": {"symptoms_en": ["Jaundice", "Fatigue", "Dark urine", "RUQ pain", "Nausea"], "symptoms_ku": ["زەردبوون", "ماندوویی", "میز تۆخ", "ئازاری سەرەوەی ڕاستی سک", "سکچوون"], "symptoms_ar": ["يرقان", "التعب", "بول داكن", "ألم الربع العلوي الأيمن", "غثيان"], "treatment_en": ["Entecavir", "Tenofovir", "Avoid alcohol"], "treatment_ku": ["ئەنتێکاڤیر", "تێنۆفۆڤیر", "خۆپاراستن لە کحول"], "treatment_ar": ["إنتيكافير", "تينوفوفير", "تجنب الكحول"], "risk_level": "High"},
    "Migraine": {"symptoms_en": ["Unilateral headache", "Photophobia", "Nausea", "Visual aura"], "symptoms_ku": ["سەرئێشەی لایەک", "ترسی ڕووناکی", "سکچوون", "ئۆرای بینین"], "symptoms_ar": ["صداع أحادي الجانب", "رهاب الضوء", "غثيان", "هالة بصرية"], "treatment_en": ["Sumatriptan", "NSAIDs", "Avoid triggers"], "treatment_ku": ["سوماتریپتان", "NSAIDs", "خۆپاراستن لە هۆکارەکان"], "treatment_ar": ["سوماتريبتان", "مضادات الالتهاب", "تجنب المحفزات"], "risk_level": "Low"},
}

# ================================
# 100 QUIZ QUESTIONS
# ================================
QUIZ_QUESTIONS = [
    {"question_en": "What is the first-line treatment for Type 2 Diabetes?", "question_ku": "چارەسەری هێڵی یەکەم بۆ شەکرەی جۆری ٢ چییە؟", "question_ar": "ما هو علاج الخط الأول لمرض السكري من النوع 2؟", "options_en": ["Metformin", "Insulin", "Glipizide", "Pioglitazone"], "options_ku": ["مێتفۆرمین", "ئەنسولین", "گلیپیزاید", "پیۆگلیتازۆن"], "options_ar": ["ميتفورمين", "أنسولين", "غليبيزيد", "بيوغليتازون"], "correct": 0},
    {"question_en": "Which test diagnoses Acute Myocardial Infarction?", "question_ku": "کام پشکنین بۆ دەستنیشانکردنی جەڵتەی دڵ بەکاردێت؟", "question_ar": "أي اختبار يستخدم لتشخيص احتشاء عضلة القلب الحاد؟", "options_en": ["Troponin I", "Glucose", "Hemoglobin", "Creatinine"], "options_ku": ["ترۆپۆنین I", "گلوکۆز", "هیمۆگلۆبین", "کریاتینین"], "options_ar": ["تروبونين I", "جلوكوز", "هيموغلوبين", "كرياتينين"], "correct": 0},
    {"question_en": "Normal Blood Pressure?", "question_ku": "پەستانی خوێنی ئاسایی؟", "question_ar": "ضغط الدم الطبيعي؟", "options_en": ["<120/80 mmHg", "<140/90 mmHg", "<160/100 mmHg", "<100/60 mmHg"], "options_ku": ["<120/80 mmHg", "<140/90 mmHg", "<160/100 mmHg", "<100/60 mmHg"], "options_ar": ["<120/80 مم زئبق", "<140/90 مم زئبق", "<160/100 مم زئبق", "<100/60 مم زئبق"], "correct": 0},
    {"question_en": "Vitamin deficiency causing megaloblastic anemia?", "question_ku": "کەمی کام ڤیتامین دەبێتە هۆی ئەنیمیای مێگالۆبلاستیک؟", "question_ar": "نقص أي فيتامين يسبب فقر الدم الضخم الأرومات؟", "options_en": ["Vitamin B12", "Vitamin C", "Vitamin D", "Vitamin A"], "options_ku": ["ڤیتامین B12", "ڤیتامین C", "ڤیتامین D", "ڤیتامین A"], "options_ar": ["فيتامين B12", "فيتامين C", "فيتامين D", "فيتامين A"], "correct": 0},
    {"question_en": "Metformin mechanism?", "question_ku": "میکانیزمی مێتفۆرمین؟", "question_ar": "آلية الميتفورمين؟", "options_en": ["Biguanide", "Sulfonylurea", "DPP-4 inhibitor", "SGLT2 inhibitor"], "options_ku": ["بیگواناید", "سەلفۆنیل یوریا", "بەرگری DPP-4", "بەرگری SGLT2"], "options_ar": ["بيغوانيد", "سلفونيل يوريا", "مثبط DPP-4", "مثبط SGLT2"], "correct": 0},
    {"question_en": "Antibiotic contraindicated in pregnancy?", "question_ku": "کام دژە زیندەیی لە دووگیانیدا قەدەغەیە؟", "question_ar": "أي مضاد حيوي ممنوع في الحمل؟", "options_en": ["Tetracycline", "Amoxicillin", "Azithromycin", "Cephalexin"], "options_ku": ["تێتراسایکلین", "ئەمۆکسیسیلین", "ئازیترۆمایسین", "سێفالێکسین"], "options_ar": ["تيتراسيكلين", "أموكسيسيلين", "أزيثروميسين", "سيفاليكسين"], "correct": 0},
    {"question_en": "Target HbA1c for diabetics?", "question_ku": "ئامانجی HbA1c بۆ نەخۆشانی شەکرە؟", "question_ar": "هدف HbA1c لمرضى السكري؟", "options_en": ["<7%", "<6%", "<8%", "<9%"], "options_ku": ["<7%", "<6%", "<8%", "<9%"], "options_ar": ["<7%", "<6%", "<8%", "<9%"], "correct": 0},
    {"question_en": "Lisinopril drug class?", "question_ku": "لیسینۆپریل سەر بە کام پۆلە؟", "question_ar": "فئة ليسينوبريل؟", "options_en": ["ACE Inhibitor", "Beta Blocker", "CCB", "Diuretic"], "options_ku": ["بەرگری ACE", "بێتا بلاکەر", "CCB", "میزەڕۆ"], "options_ar": ["مثبط ACE", "حاصر بيتا", "CCB", "مدر للبول"], "correct": 0},
    {"question_en": "Most common statin side effect?", "question_ku": "باوانترین کاریگەری لاوەکی ستاتینەکان؟", "question_ar": "أكثر الآثار الجانبية للستاتينات؟", "options_en": ["Myalgia", "Headache", "Diarrhea", "Cough"], "options_ku": ["ئازاری ماسوولکە", "سەرئێشە", "سکچوون", "کۆخە"], "options_ar": ["ألم عضلي", "صداع", "إسهال", "سعال"], "correct": 0},
    {"question_en": "Furosemide causes which electrolyte abnormality?", "question_ku": "فورۆسیماید دەبێتە هۆی کام ناڕێکی ئەلیکترۆلیتی؟", "question_ar": "فوروسيميد يسبب أي اضطراب كهرلي؟", "options_en": ["Hypokalemia", "Hyperkalemia", "Hyponatremia", "Hypercalcemia"], "options_ku": ["کەمی پۆتاسیۆم", "زۆری پۆتاسیۆم", "کەمی سۆدیۆم", "زۆری کالسیۆم"], "options_ar": ["نقص بوتاسيوم", "فرط بوتاسيوم", "نقص صوديوم", "فرط كالسيوم"], "correct": 0},
]

disease_list = list(DISEASE_DATABASE.keys())
drug_list = [drug for drugs in DRUG_DATABASE.values() for drug in drugs]
test_list = list(LAB_TESTS.keys())

for i in range(90):
    q_type = random.choice(["disease_symptom", "drug_class", "test_normal"])
    if q_type == "disease_symptom" and disease_list:
        disease = random.choice(disease_list)
        info = DISEASE_DATABASE[disease]
        correct_symptom = random.choice(info["symptoms_en"])
        wrong_symptoms = random.sample([s for d in disease_list for s in DISEASE_DATABASE[d]["symptoms_en"] if s != correct_symptom], 3)
        options = [correct_symptom] + wrong_symptoms[:3]
        random.shuffle(options)
        QUIZ_QUESTIONS.append({"question_en": f"Which symptom is characteristic of {disease}?", "question_ku": f"کام نیشانە تایبەتە بە {disease}؟", "question_ar": f"أي عرض مميز لـ {disease}؟", "options_en": options, "options_ku": options, "options_ar": options, "correct": options.index(correct_symptom)})
    elif q_type == "drug_class" and drug_list:
        drug = random.choice(drug_list)
        for cat, drugs in DRUG_DATABASE.items():
            if drug in drugs: correct_class = drugs[drug]["class"]; break
        wrong_classes = random.sample([d["class"] for cat in DRUG_DATABASE for d in DRUG_DATABASE[cat].values() if d["class"] != correct_class], 3)
        options = [correct_class] + wrong_classes[:3]
        random.shuffle(options)
        QUIZ_QUESTIONS.append({"question_en": f"What class does {drug} belong to?", "question_ku": f"{drug} سەر بە کام پۆلە؟", "question_ar": f"إلى أي فئة ينتمي {drug}؟", "options_en": options, "options_ku": options, "options_ar": options, "correct": options.index(correct_class)})
    elif q_type == "test_normal" and test_list:
        test = random.choice(test_list)
        correct_normal = LAB_TESTS[test]["normal"]
        wrong_normals = random.sample([t["normal"] for t in LAB_TESTS.values() if t["normal"] != correct_normal], 3)
        options = [correct_normal] + wrong_normals[:3]
        random.shuffle(options)
        QUIZ_QUESTIONS.append({"question_en": f"Normal range for {test}?", "question_ku": f"مەودای ئاسایی {test}؟", "question_ar": f"المعدل الطبيعي لـ {test}؟", "options_en": options, "options_ku": options, "options_ar": options, "correct": options.index(correct_normal)})

# ================================
# 100 MEDICAL NEWS ITEMS
# ================================
MEDICAL_NEWS = [
    {"title": "New Diabetes Treatment Shows Promise", "summary": "A novel GLP-1/GIP dual agonist demonstrates superior glycemic control.", "source": "NEJM", "date": "2024-01-20"},
    {"title": "AI Improves Cancer Detection", "summary": "Machine learning shows 95% accuracy in early lung cancer detection.", "source": "The Lancet", "date": "2024-01-19"},
    {"title": "mRNA Beyond COVID-19", "summary": "mRNA vaccines for malaria and tuberculosis show promising results.", "source": "Nature Medicine", "date": "2024-01-18"},
    {"title": "Alzheimer's Breakthrough", "summary": "New monoclonal antibody slows cognitive decline.", "source": "JAMA", "date": "2024-01-17"},
    {"title": "Antibiotic Resistance Crisis", "summary": "WHO reports alarming increase in multidrug-resistant infections.", "source": "WHO", "date": "2024-01-16"},
]
topics = [("Vaccine Development", "Universal flu vaccine progress"), ("Gene Therapy", "CRISPR treats genetic disorders"), ("Cardiovascular Health", "Mediterranean diet benefits"), ("Mental Health", "Psychedelic therapy for depression"), ("Oncology", "CAR-T cell therapy approved")]
for i in range(95):
    topic = topics[i % len(topics)]
    date = datetime(2024, 1, 1) + timedelta(days=i)
    MEDICAL_NEWS.append({"title": f"{topic[0]} ({date.strftime('%B %d, %Y')})", "summary": f"{topic[1]} based on latest research.", "source": random.choice(["NEJM", "The Lancet", "JAMA", "BMJ", "Nature Medicine", "WHO", "CDC"]), "date": date.strftime("%Y-%m-%d")})

# ================================
# HELPER FUNCTIONS
# ================================
def get_symptoms(info: Dict, lang: str) -> List[str]:
    return info.get(f"symptoms_{lang}", info.get("symptoms_en", []))

def get_treatment(info: Dict, lang: str) -> List[str]:
    return info.get(f"treatment_{lang}", info.get("treatment_en", []))

def get_description(lab_info: Dict, lang: str) -> str:
    return lab_info.get(f"description_{lang}", lab_info.get("description_en", ""))

def get_indications(drug_info: Dict, lang: str) -> str:
    return drug_info.get(f"indications_{lang}", drug_info.get("indications_en", ""))

def get_side_effects(drug_info: Dict, lang: str) -> str:
    return drug_info.get(f"side_effects_{lang}", drug_info.get("side_effects_en", ""))

def get_risk_level_translated(risk: str, lang: str) -> str:
    risk_map = {"en": {"Critical": "Critical", "High": "High", "Moderate": "Moderate", "Low": "Low"}, "ku": {"Critical": "زۆر مەترسیدار", "High": "مەترسیدار", "Moderate": "مامناوەند", "Low": "کەم"}, "ar": {"Critical": "حرج", "High": "مرتفع", "Moderate": "متوسط", "Low": "منخفض"}}
    return risk_map.get(lang, risk_map['en']).get(risk, risk)

@st.cache_data(ttl=300)
def get_leaderboard_data():
    import pandas as pd
    conn = get_db_connection()
    return pd.read_sql_query("SELECT username, xp_points, quiz_score, cases_solved, level, last_active FROM leaderboard ORDER BY xp_points DESC", conn)

@st.cache_data(ttl=60)
def get_user_count() -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM users")
    result = cursor.fetchone()
    return result['count'] if result else 0

# ================================
# CSS STYLING
# ================================
def load_css(lang: str = 'en'):
    rtl_css = ""
    if lang in ['ku', 'ar']:
        rtl_css = """
            html { direction: rtl; }
            body { direction: rtl; text-align: right; }
            .stApp { direction: rtl; }
            .stMarkdown, .stText, p, h1, h2, h3, h4 { text-align: right !important; }
            .stRadio label { text-align: right !important; }
            .stSelectbox { direction: rtl !important; }
            input, textarea { text-align: right !important; direction: rtl !important; }
        """
    
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        * {{ font-family: 'Inter', sans-serif; }}
        .stApp {{ background: linear-gradient(135deg, #0a0a1a, #1a1a3e, #0a0a1a); }}
        .glass-card {{ background: rgba(255,255,255,0.03); backdrop-filter: blur(20px); border-radius: 16px; padding: 1.5rem; border: 1px solid rgba(99,102,241,0.2); margin: 1rem 0; }}
        .stat-card {{ background: linear-gradient(135deg, rgba(99,102,241,0.1), rgba(139,92,246,0.05)); border-radius: 16px; padding: 1.2rem; text-align: center; border: 1px solid rgba(99,102,241,0.2); }}
        .stat-number {{ font-size: 2.5rem; font-weight: 800; background: linear-gradient(135deg, #6366f1, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .badge {{ display: inline-block; padding: 0.3rem 1rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; }}
        .badge-primary {{ background: rgba(99,102,241,0.2); color: #a78bfa; }}
        .badge-success {{ background: rgba(16,185,129,0.2); color: #10b981; }}
        .badge-danger {{ background: rgba(239,68,68,0.2); color: #ef4444; }}
        .badge-warning {{ background: rgba(251,191,36,0.2); color: #fbbf24; }}
        .stButton > button {{ background: linear-gradient(135deg, #6366f1, #8b5cf6) !important; color: white !important; border: none !important; border-radius: 12px !important; font-weight: 600 !important; }}
        .stButton > button:hover {{ background: linear-gradient(135deg, #8b5cf6, #a78bfa) !important; transform: translateY(-2px) !important; }}
        .stTextInput > div > div, .stTextArea > div > div {{ background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(99,102,241,0.2) !important; border-radius: 10px !important; color: white !important; }}
        [data-testid="stSidebar"] {{ background: linear-gradient(180deg, #0a0a1a, #1a1a3e, #0a0a1a) !important; }}
        [data-testid="stSidebar"] .stButton > button {{ background: rgba(99,102,241,0.1) !important; border: 1px solid rgba(99,102,241,0.2) !important; color: white !important; padding: 0.5rem 1rem !important; margin: 2px 0 !important; }}
        [data-testid="stSidebar"] .stButton > button:hover {{ background: rgba(99,102,241,0.2) !important; border-color: rgba(139,92,246,0.4) !important; }}
        h1 {{ background: linear-gradient(135deg, #6366f1, #8b5cf6, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800 !important; }}
        ::-webkit-scrollbar {{ width: 8px; }}
        ::-webkit-scrollbar-track {{ background: rgba(255,255,255,0.05); }}
        ::-webkit-scrollbar-thumb {{ background: linear-gradient(180deg, #6366f1, #8b5cf6); border-radius: 10px; }}
        @keyframes float {{ 0%, 100% {{ transform: translateY(0px); }} 50% {{ transform: translateY(-10px); }} }}
        .language-switcher {{ display: flex; gap: 0.5rem; justify-content: center; padding: 0.5rem; }}
        {rtl_css}
    </style>
    """, unsafe_allow_html=True)

# ================================
# SESSION STATE
# ================================
def init_session_state():
    defaults = {'logged_in': False, 'username': "", 'user_data': None, 'xp_points': 0, 'quiz_score': 0, 'total_cases': 0, 'correct_diagnoses': 0, 'streak': 0, 'current_page': "Dashboard", 'flashcard_flipped': False, 'comprehensive_exam': None, 'comprehensive_answers': {}, 'comprehensive_submitted': False, 'comprehensive_score': 0, 'current_case': None, 'achievements': [], 'language': 'en'}
    for key, value in defaults.items():
        if key not in st.session_state: st.session_state[key] = value

init_session_state()
load_css(st.session_state.language)
init_database()

# ================================
# LOGIN PAGE
# ================================
if not st.session_state.logged_in:
    col_lang1, col_lang2, col_lang3 = st.columns([3, 2, 3])
    with col_lang2:
        st.markdown('<div class="language-switcher">', unsafe_allow_html=True)
        cols = st.columns(3)
        for i, (code, name) in enumerate([('en', 'English'), ('ku', 'کوردی'), ('ar', 'العربية')]):
            with cols[i]:
                if st.button(name, key=f"lang_{code}", use_container_width=True): st.session_state.language = code; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    lang = st.session_state.language
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f'<div style="text-align: center; padding: 3rem 0;"><div style="font-size: 5rem; animation: float 3s ease-in-out infinite;">🩺</div><h1 style="font-size: 3rem;">Dr.Danyal</h1><p style="color: rgba(255,255,255,0.6);">{t("app_subtitle", lang)}</p></div>', unsafe_allow_html=True)
        tab1, tab2 = st.tabs([t('login', lang), t('register', lang)])
        with tab1:
            with st.form("login_form"):
                username = st.text_input(t('username', lang), placeholder=t('enter_username', lang))
                password = st.text_input(t('password', lang), type="password", placeholder=t('enter_password', lang))
                if st.form_submit_button(t('login_button', lang), type="primary", use_container_width=True):
                    success, message, user_data = authenticate_user(username, password)
                    if success:
                        st.session_state.logged_in = True; st.session_state.username = username; st.session_state.user_data = user_data
                        st.session_state.xp_points = user_data['xp_points']; st.session_state.quiz_score = user_data['quiz_score']
                        st.session_state.total_cases = user_data['total_cases']; st.session_state.correct_diagnoses = user_data['correct_diagnoses']
                        st.session_state.streak = update_user_streak(username)
                        if user_data.get('language_preference'): st.session_state.language = user_data['language_preference']
                        st.rerun()
                    else: st.error(f"❌ {message}")
        with tab2:
            with st.form("register_form"):
                new_username = st.text_input(t('choose_username', lang), placeholder=t('username', lang))
                new_password = st.text_input(t('choose_password', lang), type="password", placeholder=t('password', lang))
                confirm_password = st.text_input(t('confirm_password', lang), type="password")
                if st.form_submit_button(t('register_button', lang), type="primary", use_container_width=True):
                    if new_password != confirm_password: st.error(f"❌ {t('passwords_dont_match', lang)}")
                    else:
                        success, message = create_user(new_username, new_password)
                        if success: st.success(f"✅ {t('account_created', lang)}")
                        else: st.error(f"❌ {message}")
    st.stop()

# ================================
# MAIN APP WITH RTL SIDEBAR FIX
# ================================
lang = st.session_state.language

if lang in ['ku', 'ar']:
    # RTL Layout: Custom right sidebar using columns
    col_sidebar, col_main = st.columns([1, 4])
    
    with col_sidebar:
        # Language switcher
        st.markdown('<div class="language-switcher">', unsafe_allow_html=True)
        cols_inner = st.columns(3)
        for i, (code, name) in enumerate([('en', 'English'), ('ku', 'KU'), ('ar', 'AR')]):
            with cols_inner[i]:
                if st.button(name, key=f"rtl_sidebar_lang_{code}", use_container_width=True):
                    st.session_state.language = code
                    conn = get_db_connection()
                    conn.execute("UPDATE users SET language_preference = ? WHERE username = ?", (code, st.session_state.username))
                    conn.commit()
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        level = get_user_level(st.session_state.xp_points)
        level_info = LEVELS[level]
        progress = get_level_progress(st.session_state.xp_points)
        
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem 0;"><div style="font-size: 3rem;">{level_info['icon']}</div><div style="font-weight: 700; color: #a78bfa;">{st.session_state.username}</div><span class="badge badge-primary">{get_level_name(level, lang)}</span></div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin: 1rem 0;">
            <div style="background: rgba(99,102,241,0.1); padding: 0.5rem; border-radius: 10px; text-align: center;"><div style="font-weight: 700; color: #a78bfa;">⭐ {st.session_state.xp_points}</div><div style="font-size: 0.65rem; color: #888;">{t('xp', lang)}</div></div>
            <div style="background: rgba(99,102,241,0.1); padding: 0.5rem; border-radius: 10px; text-align: center;"><div style="font-weight: 700; color: #a78bfa;">📊 {st.session_state.quiz_score}</div><div style="font-size: 0.65rem; color: #888;">{t('quiz_score', lang)}</div></div>
            <div style="background: rgba(99,102,241,0.1); padding: 0.5rem; border-radius: 10px; text-align: center;"><div style="font-weight: 700; color: #a78bfa;">🔥 {st.session_state.streak}</div><div style="font-size: 0.65rem; color: #888;">{t('streak', lang)}</div></div>
            <div style="background: rgba(99,102,241,0.1); padding: 0.5rem; border-radius: 10px; text-align: center;"><div style="font-weight: 700; color: #a78bfa;">🩺 {st.session_state.total_cases}</div><div style="font-size: 0.65rem; color: #888;">{t('cases', lang)}</div></div>
        </div>
        <div style="width: 100%; height: 6px; background: rgba(255,255,255,0.1); border-radius: 10px; overflow: hidden; margin: 0.5rem 0;"><div style="width: {progress:.1f}%; height: 100%; background: linear-gradient(90deg, #6366f1, #8b5cf6); border-radius: 10px;"></div></div>
        <div style="font-size: 0.65rem; color: #888; text-align: right;">{t('level_progress', lang)} {progress:.0f}%</div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        pages = [("dashboard", "Dashboard"), ("diseases", "Diseases"), ("case_analysis", "Case Analysis"), ("quiz", "Quiz"), ("comprehensive_exam", "Comprehensive Exam"), ("spaced_repetition", "Spaced Repetition"), ("lab_tests", "Lab Tests"), ("pharmacology", "Pharmacology"), ("drug_interactions", "Drug Interactions"), ("leaderboard", "Leaderboard"), ("medical_news", "Medical News"), ("ai_assistant", "AI Assistant"), ("clinical_notes", "Clinical Notes"), ("achievements", "Achievements")]
        for key, page_name in pages:
            if st.button(t(key, lang), use_container_width=True, key=f"rtl_nav_{page_name}"):
                st.session_state.current_page = page_name
                st.rerun()
        st.markdown("---")
        if st.button(t('logout', lang), use_container_width=True, key="rtl_logout"): st.session_state.logged_in = False; st.rerun()
        st.markdown(f'<div style="text-align: center; padding: 0.5rem; font-size: 0.7rem; color: #666;"><span class="badge badge-primary">{t("version", lang)}</span><p>© 2024 Dr.Danyal</p></div>', unsafe_allow_html=True)
    
    with col_main:
        # Main content for RTL
        page = st.session_state.current_page
        
        if page == "Dashboard":
            st.markdown(f'<h1 style="text-align: center;">{t("dashboard", lang)}</h1>', unsafe_allow_html=True)
            cols = st.columns(5)
            metrics = [(t("diseases_count", lang), len(DISEASE_DATABASE)), (t("drugs_count", lang), sum(len(d) for d in DRUG_DATABASE.values())), (t("tests_count", lang), len(LAB_TESTS)), (t("xp", lang), st.session_state.xp_points), (t("streak", lang), st.session_state.streak)]
            for col, (label, value) in zip(cols, metrics):
                with col: st.markdown(f'<div class="stat-card"><h3>{label}</h3><div class="stat-number">{value}</div></div>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1: st.markdown(f"""<div class="glass-card"><h3>{t('your_progress', lang)}</h3><p>{t('level', lang)}: {level_info['icon']} {get_level_name(level, lang)}</p><p>{t('quiz_score', lang)}: {st.session_state.quiz_score}</p><p>{t('cases_solved', lang)}: {st.session_state.total_cases}</p><p>{t('accuracy', lang)}: {(st.session_state.correct_diagnoses / max(st.session_state.total_cases, 1) * 100):.1f}%</p></div>""", unsafe_allow_html=True)
            with col2: st.markdown(f"""<div class="glass-card"><h3>{t('platform_stats', lang)}</h3><p>{t('total_users', lang)}: {get_user_count()}</p><p>{t('diseases_count', lang)}: {len(DISEASE_DATABASE)}</p><p>{t('drugs_count', lang)}: {sum(len(d) for d in DRUG_DATABASE.values())}</p><p>{t('tests_count', lang)}: {len(LAB_TESTS)}</p></div>""", unsafe_allow_html=True)
        
        elif page == "Diseases":
            st.markdown(f'<h2>{t("disease_library", lang)}</h2>', unsafe_allow_html=True)
            search = st.text_input(t("search", lang), placeholder=t("search_placeholder", lang))
            risk_filter = st.selectbox(t("risk_level", lang), [t("all", lang), t("critical", lang), t("high", lang), t("moderate", lang), t("low", lang)])
            risk_map_reverse = {t("critical", lang): "Critical", t("high", lang): "High", t("moderate", lang): "Moderate", t("low", lang): "Low"}
            filtered = DISEASE_DATABASE.copy()
            if search: filtered = {k: v for k, v in filtered.items() if search.lower() in k.lower()}
            if risk_filter != t("all", lang): filtered = {k: v for k, v in filtered.items() if v.get("risk_level") == risk_map_reverse.get(risk_filter, risk_filter)}
            cols = st.columns(2)
            for i, (disease, info) in enumerate(filtered.items()):
                with cols[i % 2]:
                    with st.expander(f"🩺 {disease}"):
                        risk_color = {"Critical": "#ef4444", "High": "#f59e0b", "Moderate": "#06b6d4", "Low": "#10b981"}
                        st.markdown(f"**{t('risk', lang)}:** <span style='color:{risk_color.get(info.get('risk_level', 'Low'))}'>{get_risk_level_translated(info.get('risk_level', 'Low'), lang)}</span>", unsafe_allow_html=True)
                        st.markdown(f"**{t('symptoms', lang)}:** {', '.join(get_symptoms(info, lang)[:5])}")
                        st.markdown(f"**{t('treatment', lang)}:** {', '.join(get_treatment(info, lang)[:3])}")
        
        elif page == "Case Analysis":
            st.markdown(f'<h2>{t("clinical_case_analysis", lang)}</h2>', unsafe_allow_html=True)
            if st.button(t("generate_new_case", lang), type="primary", use_container_width=True):
                disease = random.choice(list(DISEASE_DATABASE.keys()))
                info = DISEASE_DATABASE[disease]
                gender_map = {"en": random.choice(["Male", "Female"]), "ku": random.choice(["نێر", "مێ"]), "ar": random.choice(["ذكر", "أنثى"])}
                st.session_state.current_case = {"id": f"CASE-{random.randint(1000,9999)}", "age": random.randint(18, 85), "gender": gender_map, "symptoms": random.sample(get_symptoms(info, lang), min(5, len(get_symptoms(info, lang)))), "diagnosis": disease, "risk": info["risk_level"]}
                st.rerun()
            if st.session_state.current_case:
                case = st.session_state.current_case
                gender = case["gender"].get(lang, case["gender"].get("en", ""))
                st.markdown(f"""<div class="glass-card"><h3>{t('case_id', lang)} #{case['id']}</h3><p><strong>{t('patient', lang)}:</strong> {case['age']} {t('years_old', lang)} {gender}</p><p><strong>{t('symptoms', lang)}:</strong> {', '.join(case['symptoms'])}</p></div>""", unsafe_allow_html=True)
                diagnosis = st.selectbox(t("your_diagnosis", lang), list(DISEASE_DATABASE.keys()))
                if st.button(t("submit", lang), type="primary"):
                    st.session_state.total_cases += 1
                    if diagnosis == case["diagnosis"]: st.session_state.correct_diagnoses += 1; add_xp(st.session_state.username, 20); st.success(f"🎉 {t('correct', lang)}!")
                    else: st.error(f"❌ {t('incorrect', lang)}.")
                    conn = get_db_connection(); conn.execute("UPDATE users SET total_cases = ?, correct_diagnoses = ? WHERE username = ?", (st.session_state.total_cases, st.session_state.correct_diagnoses, st.session_state.username)); conn.commit()
        
        elif page == "Quiz":
            st.markdown(f'<h2>{t("medical_quiz", lang)}</h2>', unsafe_allow_html=True)
            q = random.choice(QUIZ_QUESTIONS)
            question = q.get(f"question_{lang}", q["question_en"]); options = q.get(f"options_{lang}", q["options_en"])
            st.markdown(f'<div class="glass-card"><h3>{question}</h3></div>', unsafe_allow_html=True)
            answer = st.radio(t("select_answer", lang), options, key="rtl_quiz_ans")
            if st.button(t("submit_answer", lang), type="primary"):
                if options.index(answer) == q["correct"]: st.session_state.quiz_score += 1; add_xp(st.session_state.username, 10); st.success(f"🎉 {t('correct', lang)}!")
                else: st.error(f"❌ {t('incorrect', lang)}.")
                conn = get_db_connection(); conn.execute("UPDATE users SET quiz_score = ? WHERE username = ?", (st.session_state.quiz_score, st.session_state.username)); conn.commit(); st.rerun()
        
        elif page == "Comprehensive Exam":
            st.markdown(f'<h2>{t("comprehensive_exam_title", lang)}</h2>', unsafe_allow_html=True)
            if st.session_state.comprehensive_exam is None:
                if st.button(t("start_exam", lang), type="primary", use_container_width=True): st.session_state.comprehensive_exam = random.sample(QUIZ_QUESTIONS, min(50, len(QUIZ_QUESTIONS))); st.session_state.comprehensive_answers = {}; st.session_state.comprehensive_submitted = False; st.rerun()
            elif not st.session_state.comprehensive_submitted:
                for i, q in enumerate(st.session_state.comprehensive_exam):
                    question = q.get(f"question_{lang}", q["question_en"]); options = q.get(f"options_{lang}", q["options_en"])
                    st.markdown(f"**{i+1}. {question}**"); ans = st.radio(f"Q{i}", options, key=f"rtl_exam_{i}", label_visibility="collapsed")
                    st.session_state.comprehensive_answers[i] = options.index(ans) if ans else -1
                if st.button(t("submit_exam", lang), type="primary"):
                    score = sum(1 for i, q in enumerate(st.session_state.comprehensive_exam) if st.session_state.comprehensive_answers.get(i) == q["correct"])
                    st.session_state.comprehensive_score = score; st.session_state.comprehensive_submitted = True; add_xp(st.session_state.username, score * 2); st.rerun()
            else:
                score = st.session_state.comprehensive_score; total = len(st.session_state.comprehensive_exam)
                st.markdown(f'<div class="glass-card"><h2>🎉 {t("score", lang)}: {score}/{total} ({(score/total*100):.1f}%)</h2></div>', unsafe_allow_html=True)
                if st.button(t("retake", lang)): st.session_state.comprehensive_exam = None; st.rerun()
        
        elif page == "Spaced Repetition":
            st.markdown(f'<h2>{t("spaced_repetition_title", lang)}</h2>', unsafe_allow_html=True)
            disease = random.choice(list(DISEASE_DATABASE.keys())); info = DISEASE_DATABASE[disease]
            if st.session_state.flashcard_flipped:
                st.markdown(f"""<div class="glass-card" style="text-align: center; padding: 2rem;"><h3>{disease}</h3><p><strong>{t('symptoms', lang)}:</strong> {', '.join(get_symptoms(info, lang)[:4])}</p><p style="color: #a78bfa;"><strong>{t('treatment', lang)}:</strong> {', '.join(get_treatment(info, lang)[:3])}</p></div>""", unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(t("knew_it", lang), type="primary", use_container_width=True): st.session_state.flashcard_flipped = False; add_xp(st.session_state.username, 5); st.rerun()
                with col2:
                    if st.button(t("review_again", lang), use_container_width=True): st.session_state.flashcard_flipped = False; st.rerun()
            else:
                st.markdown(f"""<div class="glass-card" style="text-align: center; padding: 3rem;"><h3>{t('what_are_symptoms_of', lang)} {disease}?</h3></div>""", unsafe_allow_html=True)
                if st.button(t("reveal_answer", lang), use_container_width=True): st.session_state.flashcard_flipped = True; st.rerun()
        
        elif page == "Lab Tests":
            st.markdown(f'<h2>{t("lab_tests_title", lang)} ({len(LAB_TESTS)} {t("tests_count", lang)})</h2>', unsafe_allow_html=True)
            search = st.text_input(t("search", lang))
            category = st.selectbox(t("category", lang), [t("all", lang)] + sorted(set(v["category"] for v in LAB_TESTS.values())))
            filtered = {k: v for k, v in LAB_TESTS.items() if (not search or search.lower() in k.lower()) and (category == t("all", lang) or v["category"] == category)}
            if filtered:
                import pandas as pd
                df_data = [{"Test": k, "Category": v["category"], t("normal_range", lang): v["normal"], t("description", lang): get_description(v, lang)} for k, v in filtered.items()]
                st.dataframe(pd.DataFrame(df_data), use_container_width=True, height=400)
            else: st.info(t("no_tests_found", lang))
        
        elif page == "Pharmacology":
            st.markdown(f'<h2>{t("pharmacology_title", lang)} ({sum(len(d) for d in DRUG_DATABASE.values())} {t("drugs_count", lang)})</h2>', unsafe_allow_html=True)
            search = st.text_input(t("search", lang))
            for category, drugs in DRUG_DATABASE.items():
                cat_drugs = {k: v for k, v in drugs.items() if not search or search.lower() in k.lower()}
                if cat_drugs:
                    with st.expander(f"📂 {category} ({len(cat_drugs)} {t('drugs_count', lang)})"):
                        for drug, info in cat_drugs.items():
                            st.markdown(f"""<div class="glass-card"><h4>{drug}</h4><p><strong>{t('drug_class', lang)}:</strong> {info['class']} | <strong>{t('dose', lang)}:</strong> {info['dose']}</p><p><strong>{t('indications', lang)}:</strong> {get_indications(info, lang)}</p><p style="color: #ef4444;"><strong>{t('side_effects', lang)}:</strong> {get_side_effects(info, lang)}</p></div>""", unsafe_allow_html=True)
        
        elif page == "Drug Interactions":
            st.markdown(f'<h2>{t("drug_interactions_title", lang)}</h2>', unsafe_allow_html=True)
            all_drugs = [drug for drugs in DRUG_DATABASE.values() for drug in drugs]
            selected = st.multiselect(t("select_drugs", lang), all_drugs)
            if len(selected) >= 2: st.info(f"{len(selected)} {t('drugs_selected', lang)}")
            else: st.info(t("select_minimum", lang))
        
        elif page == "Leaderboard":
            st.markdown(f'<h2>{t("leaderboard_title", lang)}</h2>', unsafe_allow_html=True)
            df = get_leaderboard_data()
            if not df.empty:
                for i, (_, row) in enumerate(df.iterrows()):
                    medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"#{i+1}"
                    st.markdown(f"""<div class="glass-card"><h3>{medal} {row['username']}</h3><p>⭐ {row['xp_points']} {t('xp', lang)} | 📊 {row['quiz_score']} {t('quiz_score', lang)} | 🩺 {row['cases_solved']} {t('cases', lang)}</p></div>""", unsafe_allow_html=True)
            else: st.info(t("no_data", lang))
        
        elif page == "Medical News":
            st.markdown(f'<h2>{t("medical_news", lang)} ({len(MEDICAL_NEWS)} items)</h2>', unsafe_allow_html=True)
            for item in MEDICAL_NEWS[:20]: st.markdown(f"""<div class="glass-card"><h4>📰 {item['title']}</h4><p>{item['summary']}</p><p style="color: #888;">📅 {item['date']} | 📚 {item['source']}</p></div>""", unsafe_allow_html=True)
        
        elif page == "AI Assistant":
            st.markdown(f'<h2>{t("ai_assistant_title", lang)}</h2>', unsafe_allow_html=True)
            symptoms = st.text_area(t("enter_symptoms", lang), placeholder="e.g., fever, cough, fatigue", height=100)
            if st.button(t("analyze", lang), type="primary") and symptoms:
                symptom_list = [s.strip().lower() for s in symptoms.split(",") if s.strip()]
                results = []
                for disease, info in DISEASE_DATABASE.items():
                    disease_symptoms = [s.lower() for s in get_symptoms(info, 'en')]
                    matches = len(set(symptom_list) & set(disease_symptoms))
                    if matches > 0: results.append((disease, (matches / len(disease_symptoms)) * 100, info["risk_level"]))
                results.sort(key=lambda x: x[1], reverse=True)
                if results:
                    for disease, match, risk in results[:10]:
                        risk_color = {"Critical": "#ef4444", "High": "#f59e0b", "Moderate": "#06b6d4", "Low": "#10b981"}
                        st.markdown(f"""<div class="glass-card"><h4>{disease}</h4><p>{t('match', lang)}: {match:.0f}% | {t('risk', lang)}: <span style="color:{risk_color.get(risk, '#888')}">{get_risk_level_translated(risk, lang)}</span></p></div>""", unsafe_allow_html=True)
                else: st.info("No matching diseases found.")
        
        elif page == "Clinical Notes":
            st.markdown(f'<h2>{t("clinical_notes_title", lang)}</h2>', unsafe_allow_html=True)
            with st.form("rtl_add_note"):
                patient = st.text_input(t("patient_info", lang)); note = st.text_area(t("clinical_note", lang))
                if st.form_submit_button(t("save_note", lang), type="primary"):
                    conn = get_db_connection(); conn.execute("INSERT INTO clinical_notes (username, patient_info, note) VALUES (?, ?, ?)", (st.session_state.username, patient, note)); conn.commit()
                    st.success(f"✅ {t('note_saved', lang)}"); st.rerun()
            conn = get_db_connection(); notes = conn.execute("SELECT * FROM clinical_notes WHERE username = ? ORDER BY created_at DESC LIMIT 20", (st.session_state.username,)).fetchall()
            for note in notes: st.markdown(f"""<div class="glass-card"><p><strong>{t('patient_info', lang)}:</strong> {note['patient_info']}</p><p>{note['note']}</p><p style="color: #888;">{note['created_at'][:10]}</p></div>""", unsafe_allow_html=True)
        
        elif page == "Achievements":
            st.markdown(f'<h2>{t("achievements_title", lang)}</h2>', unsafe_allow_html=True)
            achievements = [("First Steps", "🩺", st.session_state.total_cases >= 1), ("Case Master", "🏆", st.session_state.total_cases >= 20), ("Quiz Beginner", "📝", st.session_state.quiz_score >= 10), ("Quiz Expert", "🎓", st.session_state.quiz_score >= 50), ("Streak Master", "🔥", st.session_state.streak >= 7), ("XP Hunter", "⭐", st.session_state.xp_points >= 100), ("XP Champion", "💎", st.session_state.xp_points >= 500)]
            cols = st.columns(3)
            for i, (name, icon, earned) in enumerate(achievements):
                with cols[i % 3]: st.markdown(f"""<div class="glass-card" style="text-align: center; opacity: {1 if earned else 0.5};"><div style="font-size: 3rem;">{icon}</div><h4>{name}</h4><span class="badge {'badge-success' if earned else 'badge-warning'}">{t('earned', lang) if earned else t('locked', lang)}</span></div>""", unsafe_allow_html=True)

else:
    # LTR Layout: Default Streamlit sidebar
    with st.sidebar:
        st.markdown('<div class="language-switcher">', unsafe_allow_html=True)
        cols = st.columns(3)
        for i, (code, name) in enumerate([('en', 'EN'), ('ku', 'KU'), ('ar', 'AR')]):
            with cols[i]:
                if st.button(name, key=f"ltr_sidebar_lang_{code}", use_container_width=True):
                    st.session_state.language = code
                    conn = get_db_connection()
                    conn.execute("UPDATE users SET language_preference = ? WHERE username = ?", (code, st.session_state.username))
                    conn.commit()
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        level = get_user_level(st.session_state.xp_points)
        level_info = LEVELS[level]
        progress = get_level_progress(st.session_state.xp_points)
        
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem 0;"><div style="font-size: 3rem;">{level_info['icon']}</div><div style="font-weight: 700; color: #a78bfa;">{st.session_state.username}</div><span class="badge badge-primary">{get_level_name(level, lang)}</span></div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin: 1rem 0;">
            <div style="background: rgba(99,102,241,0.1); padding: 0.5rem; border-radius: 10px; text-align: center;"><div style="font-weight: 700; color: #a78bfa;">⭐ {st.session_state.xp_points}</div><div style="font-size: 0.65rem; color: #888;">{t('xp', lang)}</div></div>
            <div style="background: rgba(99,102,241,0.1); padding: 0.5rem; border-radius: 10px; text-align: center;"><div style="font-weight: 700; color: #a78bfa;">📊 {st.session_state.quiz_score}</div><div style="font-size: 0.65rem; color: #888;">{t('quiz_score', lang)}</div></div>
            <div style="background: rgba(99,102,241,0.1); padding: 0.5rem; border-radius: 10px; text-align: center;"><div style="font-weight: 700; color: #a78bfa;">🔥 {st.session_state.streak}</div><div style="font-size: 0.65rem; color: #888;">{t('streak', lang)}</div></div>
            <div style="background: rgba(99,102,241,0.1); padding: 0.5rem; border-radius: 10px; text-align: center;"><div style="font-weight: 700; color: #a78bfa;">🩺 {st.session_state.total_cases}</div><div style="font-size: 0.65rem; color: #888;">{t('cases', lang)}</div></div>
        </div>
        <div style="width: 100%; height: 6px; background: rgba(255,255,255,0.1); border-radius: 10px; overflow: hidden; margin: 0.5rem 0;"><div style="width: {progress:.1f}%; height: 100%; background: linear-gradient(90deg, #6366f1, #8b5cf6); border-radius: 10px;"></div></div>
        <div style="font-size: 0.65rem; color: #888; text-align: right;">{t('level_progress', lang)} {progress:.0f}%</div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        pages = [("dashboard", "Dashboard"), ("diseases", "Diseases"), ("case_analysis", "Case Analysis"), ("quiz", "Quiz"), ("comprehensive_exam", "Comprehensive Exam"), ("spaced_repetition", "Spaced Repetition"), ("lab_tests", "Lab Tests"), ("pharmacology", "Pharmacology"), ("drug_interactions", "Drug Interactions"), ("leaderboard", "Leaderboard"), ("medical_news", "Medical News"), ("ai_assistant", "AI Assistant"), ("clinical_notes", "Clinical Notes"), ("achievements", "Achievements")]
        for key, page_name in pages:
            if st.button(t(key, lang), use_container_width=True, key=f"ltr_nav_{page_name}"):
                st.session_state.current_page = page_name
                st.rerun()
        st.markdown("---")
        if st.button(t('logout', lang), use_container_width=True, key="ltr_logout"): st.session_state.logged_in = False; st.rerun()
        st.markdown(f'<div style="text-align: center; padding: 0.5rem; font-size: 0.7rem; color: #666;"><span class="badge badge-primary">{t("version", lang)}</span><p>© 2024 Dr.Danyal</p></div>', unsafe_allow_html=True)
    
    # Main content for LTR
    page = st.session_state.current_page
    
    if page == "Dashboard":
        st.markdown(f'<h1 style="text-align: center;">{t("dashboard", lang)}</h1>', unsafe_allow_html=True)
        cols = st.columns(5)
        metrics = [(t("diseases_count", lang), len(DISEASE_DATABASE)), (t("drugs_count", lang), sum(len(d) for d in DRUG_DATABASE.values())), (t("tests_count", lang), len(LAB_TESTS)), (t("xp", lang), st.session_state.xp_points), (t("streak", lang), st.session_state.streak)]
        for col, (label, value) in zip(cols, metrics):
            with col: st.markdown(f'<div class="stat-card"><h3>{label}</h3><div class="stat-number">{value}</div></div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1: st.markdown(f"""<div class="glass-card"><h3>{t('your_progress', lang)}</h3><p>{t('level', lang)}: {level_info['icon']} {get_level_name(level, lang)}</p><p>{t('quiz_score', lang)}: {st.session_state.quiz_score}</p><p>{t('cases_solved', lang)}: {st.session_state.total_cases}</p><p>{t('accuracy', lang)}: {(st.session_state.correct_diagnoses / max(st.session_state.total_cases, 1) * 100):.1f}%</p></div>""", unsafe_allow_html=True)
        with col2: st.markdown(f"""<div class="glass-card"><h3>{t('platform_stats', lang)}</h3><p>{t('total_users', lang)}: {get_user_count()}</p><p>{t('diseases_count', lang)}: {len(DISEASE_DATABASE)}</p><p>{t('drugs_count', lang)}: {sum(len(d) for d in DRUG_DATABASE.values())}</p><p>{t('tests_count', lang)}: {len(LAB_TESTS)}</p></div>""", unsafe_allow_html=True)
    
    elif page == "Diseases":
        st.markdown(f'<h2>{t("disease_library", lang)}</h2>', unsafe_allow_html=True)
        search = st.text_input(t("search", lang), placeholder=t("search_placeholder", lang))
        risk_filter = st.selectbox(t("risk_level", lang), [t("all", lang), t("critical", lang), t("high", lang), t("moderate", lang), t("low", lang)])
        risk_map_reverse = {t("critical", lang): "Critical", t("high", lang): "High", t("moderate", lang): "Moderate", t("low", lang): "Low"}
        filtered = DISEASE_DATABASE.copy()
        if search: filtered = {k: v for k, v in filtered.items() if search.lower() in k.lower()}
        if risk_filter != t("all", lang): filtered = {k: v for k, v in filtered.items() if v.get("risk_level") == risk_map_reverse.get(risk_filter, risk_filter)}
        cols = st.columns(2)
        for i, (disease, info) in enumerate(filtered.items()):
            with cols[i % 2]:
                with st.expander(f"🩺 {disease}"):
                    risk_color = {"Critical": "#ef4444", "High": "#f59e0b", "Moderate": "#06b6d4", "Low": "#10b981"}
                    st.markdown(f"**{t('risk', lang)}:** <span style='color:{risk_color.get(info.get('risk_level', 'Low'))}'>{get_risk_level_translated(info.get('risk_level', 'Low'), lang)}</span>", unsafe_allow_html=True)
                    st.markdown(f"**{t('symptoms', lang)}:** {', '.join(get_symptoms(info, lang)[:5])}")
                    st.markdown(f"**{t('treatment', lang)}:** {', '.join(get_treatment(info, lang)[:3])}")
    
    elif page == "Case Analysis":
        st.markdown(f'<h2>{t("clinical_case_analysis", lang)}</h2>', unsafe_allow_html=True)
        if st.button(t("generate_new_case", lang), type="primary", use_container_width=True):
            disease = random.choice(list(DISEASE_DATABASE.keys()))
            info = DISEASE_DATABASE[disease]
            gender_map = {"en": random.choice(["Male", "Female"]), "ku": random.choice(["نێر", "مێ"]), "ar": random.choice(["ذكر", "أنثى"])}
            st.session_state.current_case = {"id": f"CASE-{random.randint(1000,9999)}", "age": random.randint(18, 85), "gender": gender_map, "symptoms": random.sample(get_symptoms(info, lang), min(5, len(get_symptoms(info, lang)))), "diagnosis": disease, "risk": info["risk_level"]}
            st.rerun()
        if st.session_state.current_case:
            case = st.session_state.current_case
            gender = case["gender"].get(lang, case["gender"].get("en", ""))
            st.markdown(f"""<div class="glass-card"><h3>{t('case_id', lang)} #{case['id']}</h3><p><strong>{t('patient', lang)}:</strong> {case['age']} {t('years_old', lang)} {gender}</p><p><strong>{t('symptoms', lang)}:</strong> {', '.join(case['symptoms'])}</p></div>""", unsafe_allow_html=True)
            diagnosis = st.selectbox(t("your_diagnosis", lang), list(DISEASE_DATABASE.keys()))
            if st.button(t("submit", lang), type="primary"):
                st.session_state.total_cases += 1
                if diagnosis == case["diagnosis"]: st.session_state.correct_diagnoses += 1; add_xp(st.session_state.username, 20); st.success(f"🎉 {t('correct', lang)}!")
                else: st.error(f"❌ {t('incorrect', lang)}.")
                conn = get_db_connection(); conn.execute("UPDATE users SET total_cases = ?, correct_diagnoses = ? WHERE username = ?", (st.session_state.total_cases, st.session_state.correct_diagnoses, st.session_state.username)); conn.commit()
    
    elif page == "Quiz":
        st.markdown(f'<h2>{t("medical_quiz", lang)}</h2>', unsafe_allow_html=True)
        q = random.choice(QUIZ_QUESTIONS)
        question = q.get(f"question_{lang}", q["question_en"]); options = q.get(f"options_{lang}", q["options_en"])
        st.markdown(f'<div class="glass-card"><h3>{question}</h3></div>', unsafe_allow_html=True)
        answer = st.radio(t("select_answer", lang), options, key="ltr_quiz_ans")
        if st.button(t("submit_answer", lang), type="primary"):
            if options.index(answer) == q["correct"]: st.session_state.quiz_score += 1; add_xp(st.session_state.username, 10); st.success(f"🎉 {t('correct', lang)}!")
            else: st.error(f"❌ {t('incorrect', lang)}.")
            conn = get_db_connection(); conn.execute("UPDATE users SET quiz_score = ? WHERE username = ?", (st.session_state.quiz_score, st.session_state.username)); conn.commit(); st.rerun()
    
    elif page == "Comprehensive Exam":
        st.markdown(f'<h2>{t("comprehensive_exam_title", lang)}</h2>', unsafe_allow_html=True)
        if st.session_state.comprehensive_exam is None:
            if st.button(t("start_exam", lang), type="primary", use_container_width=True): st.session_state.comprehensive_exam = random.sample(QUIZ_QUESTIONS, min(50, len(QUIZ_QUESTIONS))); st.session_state.comprehensive_answers = {}; st.session_state.comprehensive_submitted = False; st.rerun()
        elif not st.session_state.comprehensive_submitted:
            for i, q in enumerate(st.session_state.comprehensive_exam):
                question = q.get(f"question_{lang}", q["question_en"]); options = q.get(f"options_{lang}", q["options_en"])
                st.markdown(f"**{i+1}. {question}**"); ans = st.radio(f"Q{i}", options, key=f"ltr_exam_{i}", label_visibility="collapsed")
                st.session_state.comprehensive_answers[i] = options.index(ans) if ans else -1
            if st.button(t("submit_exam", lang), type="primary"):
                score = sum(1 for i, q in enumerate(st.session_state.comprehensive_exam) if st.session_state.comprehensive_answers.get(i) == q["correct"])
                st.session_state.comprehensive_score = score; st.session_state.comprehensive_submitted = True; add_xp(st.session_state.username, score * 2); st.rerun()
        else:
            score = st.session_state.comprehensive_score; total = len(st.session_state.comprehensive_exam)
            st.markdown(f'<div class="glass-card"><h2>🎉 {t("score", lang)}: {score}/{total} ({(score/total*100):.1f}%)</h2></div>', unsafe_allow_html=True)
            if st.button(t("retake", lang)): st.session_state.comprehensive_exam = None; st.rerun()
    
    elif page == "Spaced Repetition":
        st.markdown(f'<h2>{t("spaced_repetition_title", lang)}</h2>', unsafe_allow_html=True)
        disease = random.choice(list(DISEASE_DATABASE.keys())); info = DISEASE_DATABASE[disease]
        if st.session_state.flashcard_flipped:
            st.markdown(f"""<div class="glass-card" style="text-align: center; padding: 2rem;"><h3>{disease}</h3><p><strong>{t('symptoms', lang)}:</strong> {', '.join(get_symptoms(info, lang)[:4])}</p><p style="color: #a78bfa;"><strong>{t('treatment', lang)}:</strong> {', '.join(get_treatment(info, lang)[:3])}</p></div>""", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1: 
                if st.button(t("knew_it", lang), type="primary", use_container_width=True): st.session_state.flashcard_flipped = False; add_xp(st.session_state.username, 5); st.rerun()
            with col2:
                if st.button(t("review_again", lang), use_container_width=True): st.session_state.flashcard_flipped = False; st.rerun()
        else:
            st.markdown(f"""<div class="glass-card" style="text-align: center; padding: 3rem;"><h3>{t('what_are_symptoms_of', lang)} {disease}?</h3></div>""", unsafe_allow_html=True)
            if st.button(t("reveal_answer", lang), use_container_width=True): st.session_state.flashcard_flipped = True; st.rerun()
    
    elif page == "Lab Tests":
        st.markdown(f'<h2>{t("lab_tests_title", lang)} ({len(LAB_TESTS)} {t("tests_count", lang)})</h2>', unsafe_allow_html=True)
        search = st.text_input(t("search", lang))
        category = st.selectbox(t("category", lang), [t("all", lang)] + sorted(set(v["category"] for v in LAB_TESTS.values())))
        filtered = {k: v for k, v in LAB_TESTS.items() if (not search or search.lower() in k.lower()) and (category == t("all", lang) or v["category"] == category)}
        if filtered:
            import pandas as pd
            df_data = [{"Test": k, "Category": v["category"], t("normal_range", lang): v["normal"], t("description", lang): get_description(v, lang)} for k, v in filtered.items()]
            st.dataframe(pd.DataFrame(df_data), use_container_width=True, height=400)
        else: st.info(t("no_tests_found", lang))
    
    elif page == "Pharmacology":
        st.markdown(f'<h2>{t("pharmacology_title", lang)} ({sum(len(d) for d in DRUG_DATABASE.values())} {t("drugs_count", lang)})</h2>', unsafe_allow_html=True)
        search = st.text_input(t("search", lang))
        for category, drugs in DRUG_DATABASE.items():
            cat_drugs = {k: v for k, v in drugs.items() if not search or search.lower() in k.lower()}
            if cat_drugs:
                with st.expander(f"📂 {category} ({len(cat_drugs)} {t('drugs_count', lang)})"):
                    for drug, info in cat_drugs.items():
                        st.markdown(f"""<div class="glass-card"><h4>{drug}</h4><p><strong>{t('drug_class', lang)}:</strong> {info['class']} | <strong>{t('dose', lang)}:</strong> {info['dose']}</p><p><strong>{t('indications', lang)}:</strong> {get_indications(info, lang)}</p><p style="color: #ef4444;"><strong>{t('side_effects', lang)}:</strong> {get_side_effects(info, lang)}</p></div>""", unsafe_allow_html=True)
    
    elif page == "Drug Interactions":
        st.markdown(f'<h2>{t("drug_interactions_title", lang)}</h2>', unsafe_allow_html=True)
        all_drugs = [drug for drugs in DRUG_DATABASE.values() for drug in drugs]
        selected = st.multiselect(t("select_drugs", lang), all_drugs)
        if len(selected) >= 2: st.info(f"{len(selected)} {t('drugs_selected', lang)}")
        else: st.info(t("select_minimum", lang))
    
    elif page == "Leaderboard":
        st.markdown(f'<h2>{t("leaderboard_title", lang)}</h2>', unsafe_allow_html=True)
        df = get_leaderboard_data()
        if not df.empty:
            for i, (_, row) in enumerate(df.iterrows()):
                medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"#{i+1}"
                st.markdown(f"""<div class="glass-card"><h3>{medal} {row['username']}</h3><p>⭐ {row['xp_points']} {t('xp', lang)} | 📊 {row['quiz_score']} {t('quiz_score', lang)} | 🩺 {row['cases_solved']} {t('cases', lang)}</p></div>""", unsafe_allow_html=True)
        else: st.info(t("no_data", lang))
    
    elif page == "Medical News":
        st.markdown(f'<h2>{t("medical_news", lang)} ({len(MEDICAL_NEWS)} items)</h2>', unsafe_allow_html=True)
        for item in MEDICAL_NEWS[:20]: st.markdown(f"""<div class="glass-card"><h4>📰 {item['title']}</h4><p>{item['summary']}</p><p style="color: #888;">📅 {item['date']} | 📚 {item['source']}</p></div>""", unsafe_allow_html=True)
    
    elif page == "AI Assistant":
        st.markdown(f'<h2>{t("ai_assistant_title", lang)}</h2>', unsafe_allow_html=True)
        symptoms = st.text_area(t("enter_symptoms", lang), placeholder="e.g., fever, cough, fatigue", height=100)
        if st.button(t("analyze", lang), type="primary") and symptoms:
            symptom_list = [s.strip().lower() for s in symptoms.split(",") if s.strip()]
            results = []
            for disease, info in DISEASE_DATABASE.items():
                disease_symptoms = [s.lower() for s in get_symptoms(info, 'en')]
                matches = len(set(symptom_list) & set(disease_symptoms))
                if matches > 0: results.append((disease, (matches / len(disease_symptoms)) * 100, info["risk_level"]))
            results.sort(key=lambda x: x[1], reverse=True)
            if results:
                for disease, match, risk in results[:10]:
                    risk_color = {"Critical": "#ef4444", "High": "#f59e0b", "Moderate": "#06b6d4", "Low": "#10b981"}
                    st.markdown(f"""<div class="glass-card"><h4>{disease}</h4><p>{t('match', lang)}: {match:.0f}% | {t('risk', lang)}: <span style="color:{risk_color.get(risk, '#888')}">{get_risk_level_translated(risk, lang)}</span></p></div>""", unsafe_allow_html=True)
            else: st.info("No matching diseases found.")
    
    elif page == "Clinical Notes":
        st.markdown(f'<h2>{t("clinical_notes_title", lang)}</h2>', unsafe_allow_html=True)
        with st.form("ltr_add_note"):
            patient = st.text_input(t("patient_info", lang)); note = st.text_area(t("clinical_note", lang))
            if st.form_submit_button(t("save_note", lang), type="primary"):
                conn = get_db_connection(); conn.execute("INSERT INTO clinical_notes (username, patient_info, note) VALUES (?, ?, ?)", (st.session_state.username, patient, note)); conn.commit()
                st.success(f"✅ {t('note_saved', lang)}"); st.rerun()
        conn = get_db_connection(); notes = conn.execute("SELECT * FROM clinical_notes WHERE username = ? ORDER BY created_at DESC LIMIT 20", (st.session_state.username,)).fetchall()
        for note in notes: st.markdown(f"""<div class="glass-card"><p><strong>{t('patient_info', lang)}:</strong> {note['patient_info']}</p><p>{note['note']}</p><p style="color: #888;">{note['created_at'][:10]}</p></div>""", unsafe_allow_html=True)
    
    elif page == "Achievements":
        st.markdown(f'<h2>{t("achievements_title", lang)}</h2>', unsafe_allow_html=True)
        achievements = [("First Steps", "🩺", st.session_state.total_cases >= 1), ("Case Master", "🏆", st.session_state.total_cases >= 20), ("Quiz Beginner", "📝", st.session_state.quiz_score >= 10), ("Quiz Expert", "🎓", st.session_state.quiz_score >= 50), ("Streak Master", "🔥", st.session_state.streak >= 7), ("XP Hunter", "⭐", st.session_state.xp_points >= 100), ("XP Champion", "💎", st.session_state.xp_points >= 500)]
        cols = st.columns(3)
        for i, (name, icon, earned) in enumerate(achievements):
            with cols[i % 3]: st.markdown(f"""<div class="glass-card" style="text-align: center; opacity: {1 if earned else 0.5};"><div style="font-size: 3rem;">{icon}</div><h4>{name}</h4><span class="badge {'badge-success' if earned else 'badge-warning'}">{t('earned', lang) if earned else t('locked', lang)}</span></div>""", unsafe_allow_html=True)

# ================================
# FOOTER
# ================================
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; padding: 2rem; color: rgba(255,255,255,0.3);">
    <p>🩺 Dr.Danyal Medical Training Platform {t('version', lang)}</p>
    <p style="font-size: 0.8rem;">{len(DISEASE_DATABASE)} {t('diseases_count', lang)} | {sum(len(d) for d in DRUG_DATABASE.values())} {t('drugs_count', lang)} | {len(LAB_TESTS)} {t('tests_count', lang)} | {len(QUIZ_QUESTIONS)} Quizzes | {len(MEDICAL_NEWS)} News | {get_user_count()} {t('total_users', lang)}</p>
    <p style="font-size: 0.7rem;">© {datetime.now().year} {t('copyright', lang)}</p>
</div>
""", unsafe_allow_html=True)
