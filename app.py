# ================================
# MEDICAL TRAINING PLATFORM v11.0
# Dr.Danyal - Multilingual Edition
# Supports: English, Kurdish (کوردی), Arabic (العربية)
# ================================

import streamlit as st
import hashlib
import json
import os
import sqlite3
import time
import uuid
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
# MULTILINGUAL TRANSLATION SYSTEM
# ================================
TRANSLATIONS = {
    "en": {
        # General
        "app_name": "Dr.Danyal Medical Platform",
        "app_subtitle": "Advanced Medical Training Platform",
        "version": "v11.0",
        "copyright": "All rights reserved. Secure Platform.",
        
        # Login/Register
        "login": "Login",
        "register": "Register",
        "username": "Username",
        "password": "Password",
        "confirm_password": "Confirm Password",
        "login_button": "🚀 Login",
        "register_button": "✨ Create Account",
        "logout": "🚪 Logout",
        "welcome_back": "Welcome back",
        "account_created": "Account created successfully. Please login.",
        "invalid_credentials": "Invalid username or password",
        "username_exists": "Username already exists",
        "passwords_dont_match": "Passwords don't match",
        "username_min_length": "Username must be at least 3 characters",
        "password_min_length": "Password must be at least 6 characters",
        "account_locked": "Account locked. Try again in",
        "minutes": "minutes",
        "too_many_attempts": "Too many attempts. Account locked for",
        "enter_username": "Enter username",
        "enter_password": "Enter password",
        "confirm_password_placeholder": "Confirm password",
        "choose_username": "Choose Username",
        "choose_password": "Choose Password",
        
        # Navigation
        "dashboard": "📊 Dashboard",
        "diseases": "📚 Diseases",
        "case_analysis": "🩺 Case Analysis",
        "quiz": "📝 Quiz",
        "comprehensive_exam": "📋 Comprehensive Exam",
        "spaced_repetition": "🔄 Spaced Repetition",
        "lab_tests": "🔬 Lab Tests",
        "pharmacology": "💊 Pharmacology",
        "drug_interactions": "⚠️ Drug Interactions",
        "leaderboard": "🏆 Leaderboard",
        "medical_news": "📰 Medical News",
        "ai_assistant": "🧠 AI Assistant",
        "clinical_notes": "📝 Clinical Notes",
        "achievements": "🏆 Achievements",
        
        # Stats
        "xp": "XP",
        "quiz_score": "Quiz",
        "streak": "Streak",
        "cases": "Cases",
        "level": "Level",
        "level_progress": "Level Progress",
        "diseases_count": "Diseases",
        "drugs_count": "Drugs",
        "tests_count": "Tests",
        "total_users": "Total Users",
        
        # Dashboard
        "your_progress": "Your Progress",
        "platform_stats": "Platform Stats",
        "accuracy": "Accuracy",
        "cases_solved": "Cases Solved",
        
        # Diseases
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
        
        # Case Analysis
        "clinical_case_analysis": "Clinical Case Analysis",
        "generate_new_case": "🔄 Generate New Case",
        "your_diagnosis": "Your Diagnosis",
        "submit": "✅ Submit",
        "correct": "Correct",
        "incorrect": "Incorrect",
        "patient": "Patient",
        "case_id": "Case",
        "years_old": "years old",
        
        # Quiz
        "medical_quiz": "Medical Quiz",
        "select_answer": "Select your answer",
        "submit_answer": "✅ Submit Answer",
        "is_characteristic_of": "is characteristic of",
        "answer_was": "Answer was",
        
        # Comprehensive Exam
        "comprehensive_exam_title": "Comprehensive Exam",
        "start_exam": "🚀 Start Exam",
        "submit_exam": "📤 Submit Exam",
        "score": "Score",
        "retake": "🔄 Retake",
        
        # Spaced Repetition
        "spaced_repetition_title": "Spaced Repetition",
        "reveal_answer": "🔄 Reveal Answer",
        "knew_it": "✅ Knew It",
        "review_again": "❌ Review Again",
        "what_are_symptoms_of": "What are the symptoms of",
        
        # Lab Tests
        "lab_tests_title": "Laboratory Tests",
        "normal_range": "Normal Range",
        "description": "Description",
        "no_tests_found": "No tests found",
        
        # Pharmacology
        "pharmacology_title": "Pharmacology",
        "drug_class": "Class",
        "dose": "Dose",
        "indications": "Indications",
        "side_effects": "Side Effects",
        "drugs_selected": "drugs selected",
        
        # Drug Interactions
        "drug_interactions_title": "Drug Interaction Checker",
        "select_drugs": "Select drugs to check",
        "select_minimum": "Select 2 or more drugs",
        
        # Leaderboard
        "leaderboard_title": "Leaderboard",
        "no_data": "No data yet",
        
        # AI Assistant
        "ai_assistant_title": "AI Symptom Checker",
        "enter_symptoms": "Enter symptoms (comma-separated)",
        "analyze": "🔍 Analyze",
        "match": "Match",
        
        # Clinical Notes
        "clinical_notes_title": "Clinical Notes",
        "patient_info": "Patient Info",
        "clinical_note": "Clinical Note",
        "save_note": "💾 Save Note",
        "note_saved": "Note saved successfully",
        
        # Achievements
        "achievements_title": "Achievements",
        "earned": "Earned",
        "locked": "Locked",
    },
    "ku": {
        # General
        "app_name": "پلاتفۆرمی پزیشکی Dr.Danyal",
        "app_subtitle": "پلاتفۆرمی ڕاهێنانی پزیشکی پێشکەوتوو",
        "version": "v11.0",
        "copyright": "هەموو مافێک پارێزراوە. پلاتفۆرمی پارێزراو.",
        
        # Login/Register
        "login": "چوونەژوورەوە",
        "register": "خۆتۆمارکردن",
        "username": "ناوی بەکارهێنەر",
        "password": "وشەی نهێنی",
        "confirm_password": "دووپاتکردنەوەی وشەی نهێنی",
        "login_button": "🚀 چوونەژوورەوە",
        "register_button": "✨ دروستکردنی هەژمار",
        "logout": "🚪 چوونەدەرەوە",
        "welcome_back": "بەخێربێیتەوە",
        "account_created": "هەژمارەکەت بە سەرکەوتوویی دروست کرا. تکایە بچۆ ژوورەوە.",
        "invalid_credentials": "ناوی بەکارهێنەر یان وشەی نهێنی هەڵەیە",
        "username_exists": "ئەم ناوی بەکارهێنەریە پێشتر بەکارهێنراوە",
        "passwords_dont_match": "وشەی نهێنیەکان یەک ناگرنەوە",
        "username_min_length": "ناوی بەکارهێنەر دەبێت لانیکەم ٣ پیت بێت",
        "password_min_length": "وشەی نهێنی دەبێت لانیکەم ٦ پیت بێت",
        "account_locked": "هەژمارەکەت داخراوە. دووبارە هەوڵبدەرەوە دوای",
        "minutes": "خولەک",
        "too_many_attempts": "هەوڵی زۆر. هەژمارەکەت بۆ ماوەی",
        "enter_username": "ناوی بەکارهێنەر بنووسە",
        "enter_password": "وشەی نهێنی بنووسە",
        "confirm_password_placeholder": "وشەی نهێنی دووپات بکەرەوە",
        "choose_username": "ناوی بەکارهێنەر هەڵبژێرە",
        "choose_password": "وشەی نهێنی هەڵبژێرە",
        
        # Navigation
        "dashboard": "📊 داشبۆرد",
        "diseases": "📚 نەخۆشییەکان",
        "case_analysis": "🩺 شیکاری کەیس",
        "quiz": "📝 کویز",
        "comprehensive_exam": "📋 تاقیکردنەوەی گشتی",
        "spaced_repetition": "🔄 دووبارەکردنەوە",
        "lab_tests": "🔬 پشکنینەکان",
        "pharmacology": "💊 دەرمانەکان",
        "drug_interactions": "⚠️ کارلێکی دەرمانەکان",
        "leaderboard": "🏆 خشتەی ڕێزلێنان",
        "medical_news": "📰 هەواڵی پزیشکی",
        "ai_assistant": "🧠 یاریدەدەری زیرەک",
        "clinical_notes": "📝 تێبینی کلینیکی",
        "achievements": "🏆 دەستکەوتەکان",
        
        # Stats
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
        
        # Dashboard
        "your_progress": "پێشکەوتنەکەت",
        "platform_stats": "ئاماری پلاتفۆرم",
        "accuracy": "ڕێژەی ڕاستی",
        "cases_solved": "کەیسەکانی شیکارکراو",
        
        # Diseases
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
        
        # Case Analysis
        "clinical_case_analysis": "شیکاری کەیسی کلینیکی",
        "generate_new_case": "🔄 دروستکردنی کەیسی نوێ",
        "your_diagnosis": "دەستنیشانکردنەکەت",
        "submit": "✅ ناردن",
        "correct": "ڕاست",
        "incorrect": "هەڵە",
        "patient": "نەخۆش",
        "case_id": "کەیس",
        "years_old": "ساڵ",
        
        # Quiz
        "medical_quiz": "کویزی پزیشکی",
        "select_answer": "وەڵامەکەت هەڵبژێرە",
        "submit_answer": "✅ ناردنی وەڵام",
        "is_characteristic_of": "تایبەتە بە",
        "answer_was": "وەڵامەکە",
        
        # Comprehensive Exam
        "comprehensive_exam_title": "تاقیکردنەوەی گشتی",
        "start_exam": "🚀 دەستپێکردنی تاقیکردنەوە",
        "submit_exam": "📤 ناردنی تاقیکردنەوە",
        "score": "نمرە",
        "retake": "🔄 دووبارەکردنەوە",
        
        # Spaced Repetition
        "spaced_repetition_title": "دووبارەکردنەوەی بۆشایی",
        "reveal_answer": "🔄 ئاشکراکردنی وەڵام",
        "knew_it": "✅ زانیم",
        "review_again": "❌ دووبارە خوێندنەوە",
        "what_are_symptoms_of": "نیشانەکانی چیین",
        
        # Lab Tests
        "lab_tests_title": "پشکنینەکانی تاقیگە",
        "normal_range": "مەودای ئاسایی",
        "description": "وەسف",
        "no_tests_found": "هیچ پشکنینێک نەدۆزرایەوە",
        
        # Pharmacology
        "pharmacology_title": "فارماکۆلۆجی",
        "drug_class": "پۆلێن",
        "dose": "ڕێژە",
        "indications": "بەکارهێنانەکان",
        "side_effects": "کاریگەرییە لاوەکییەکان",
        "drugs_selected": "دەرمان هەڵبژێردرا",
        
        # Drug Interactions
        "drug_interactions_title": "پشکنینی کارلێکی دەرمانەکان",
        "select_drugs": "دەرمانەکان هەڵبژێرە",
        "select_minimum": "لانیکەم ٢ دەرمان هەڵبژێرە",
        
        # Leaderboard
        "leaderboard_title": "خشتەی ڕێزلێنان",
        "no_data": "هێشتا هیچ داتایەک نییە",
        
        # AI Assistant
        "ai_assistant_title": "پشکنەری زیرەکی نیشانەکان",
        "enter_symptoms": "نیشانەکان بنووسە (بە بچووکەوە جیاکراوە)",
        "analyze": "🔍 شیکردنەوە",
        "match": "ڕێژەی گونجان",
        
        # Clinical Notes
        "clinical_notes_title": "تێبینییە کلینیکییەکان",
        "patient_info": "زانیاری نەخۆش",
        "clinical_note": "تێبینی کلینیکی",
        "save_note": "💾 خەزنکردن",
        "note_saved": "تێبینییەکە بە سەرکەوتوویی خەزن کرا",
        
        # Achievements
        "achievements_title": "دەستکەوتەکان",
        "earned": "بەدەستهێنراوە",
        "locked": "داخراوە",
    },
    "ar": {
        # General
        "app_name": "منصة الدكتور دانيال الطبية",
        "app_subtitle": "منصة التدريب الطبي المتقدمة",
        "version": "v11.0",
        "copyright": "جميع الحقوق محفوظة. منصة آمنة.",
        
        # Login/Register
        "login": "تسجيل الدخول",
        "register": "إنشاء حساب",
        "username": "اسم المستخدم",
        "password": "كلمة المرور",
        "confirm_password": "تأكيد كلمة المرور",
        "login_button": "🚀 تسجيل الدخول",
        "register_button": "✨ إنشاء حساب",
        "logout": "🚪 تسجيل الخروج",
        "welcome_back": "مرحباً بعودتك",
        "account_created": "تم إنشاء الحساب بنجاح. الرجاء تسجيل الدخول.",
        "invalid_credentials": "اسم المستخدم أو كلمة المرور غير صحيحة",
        "username_exists": "اسم المستخدم موجود مسبقاً",
        "passwords_dont_match": "كلمات المرور غير متطابقة",
        "username_min_length": "يجب أن يكون اسم المستخدم 3 أحرف على الأقل",
        "password_min_length": "يجب أن تكون كلمة المرور 6 أحرف على الأقل",
        "account_locked": "تم قفل الحساب. حاول مرة أخرى بعد",
        "minutes": "دقائق",
        "too_many_attempts": "محاولات كثيرة جداً. تم قفل الحساب لمدة",
        "enter_username": "أدخل اسم المستخدم",
        "enter_password": "أدخل كلمة المرور",
        "confirm_password_placeholder": "أكد كلمة المرور",
        "choose_username": "اختر اسم المستخدم",
        "choose_password": "اختر كلمة المرور",
        
        # Navigation
        "dashboard": "📊 لوحة التحكم",
        "diseases": "📚 الأمراض",
        "case_analysis": "🩺 تحليل الحالة",
        "quiz": "📝 اختبار",
        "comprehensive_exam": "📋 امتحان شامل",
        "spaced_repetition": "🔄 التكرار المتباعد",
        "lab_tests": "🔬 التحاليل المخبرية",
        "pharmacology": "💊 علم الأدوية",
        "drug_interactions": "⚠️ تداخلات الأدوية",
        "leaderboard": "🏆 لوحة المتصدرين",
        "medical_news": "📰 أخبار طبية",
        "ai_assistant": "🧠 المساعد الذكي",
        "clinical_notes": "📝 ملاحظات سريرية",
        "achievements": "🏆 الإنجازات",
        
        # Stats
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
        
        # Dashboard
        "your_progress": "تقدمك",
        "platform_stats": "إحصائيات المنصة",
        "accuracy": "الدقة",
        "cases_solved": "الحالات المحلولة",
        
        # Diseases
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
        
        # Case Analysis
        "clinical_case_analysis": "تحليل الحالة السريرية",
        "generate_new_case": "🔄 إنشاء حالة جديدة",
        "your_diagnosis": "تشخيصك",
        "submit": "✅ إرسال",
        "correct": "صحيح",
        "incorrect": "غير صحيح",
        "patient": "المريض",
        "case_id": "الحالة",
        "years_old": "سنة",
        
        # Quiz
        "medical_quiz": "اختبار طبي",
        "select_answer": "اختر إجابتك",
        "submit_answer": "✅ إرسال الإجابة",
        "is_characteristic_of": "مميز لـ",
        "answer_was": "الإجابة كانت",
        
        # Comprehensive Exam
        "comprehensive_exam_title": "الامتحان الشامل",
        "start_exam": "🚀 بدء الامتحان",
        "submit_exam": "📤 تسليم الامتحان",
        "score": "النتيجة",
        "retake": "🔄 إعادة",
        
        # Spaced Repetition
        "spaced_repetition_title": "التكرار المتباعد",
        "reveal_answer": "🔄 كشف الإجابة",
        "knew_it": "✅ كنت أعرفها",
        "review_again": "❌ مراجعة مرة أخرى",
        "what_are_symptoms_of": "ما هي أعراض",
        
        # Lab Tests
        "lab_tests_title": "التحاليل المخبرية",
        "normal_range": "المدى الطبيعي",
        "description": "الوصف",
        "no_tests_found": "لم يتم العثور على تحاليل",
        
        # Pharmacology
        "pharmacology_title": "علم الأدوية",
        "drug_class": "الفئة",
        "dose": "الجرعة",
        "indications": "دواعي الاستعمال",
        "side_effects": "الآثار الجانبية",
        "drugs_selected": "أدوية مختارة",
        
        # Drug Interactions
        "drug_interactions_title": "مدقق تداخلات الأدوية",
        "select_drugs": "اختر الأدوية",
        "select_minimum": "اختر دواءين أو أكثر",
        
        # Leaderboard
        "leaderboard_title": "لوحة المتصدرين",
        "no_data": "لا توجد بيانات بعد",
        
        # AI Assistant
        "ai_assistant_title": "مدقق الأعراض الذكي",
        "enter_symptoms": "أدخل الأعراض (مفصولة بفواصل)",
        "analyze": "🔍 تحليل",
        "match": "نسبة التطابق",
        
        # Clinical Notes
        "clinical_notes_title": "الملاحظات السريرية",
        "patient_info": "معلومات المريض",
        "clinical_note": "ملاحظة سريرية",
        "save_note": "💾 حفظ الملاحظة",
        "note_saved": "تم حفظ الملاحظة بنجاح",
        
        # Achievements
        "achievements_title": "الإنجازات",
        "earned": "تم الإنجاز",
        "locked": "مقفل",
    }
}

# ================================
# TRANSLATION HELPER FUNCTION
# ================================
def t(key: str, lang: str = None) -> str:
    """Get translation for a key in the current language"""
    if lang is None:
        lang = st.session_state.get('language', 'en')
    return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, TRANSLATIONS['en'].get(key, key))

# ================================
# CONSTANTS & CONFIGURATION
# ================================
DB_PATH = "medical_platform.db"
MAX_LOGIN_ATTEMPTS = 5
LOGIN_TIMEOUT_MINUTES = 15

# ================================
# DATABASE SETUP
# ================================
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
    
    # Create tables
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
    
    # Check if language_preference column exists, add if not (for existing databases)
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
    
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        200000,
        dklen=64
    )
    
    return key.hex(), salt

def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    computed_hash, _ = hash_password_secure(password, salt)
    return computed_hash == stored_hash

# ================================
# RATE LIMITING
# ================================
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
    cursor.execute("""
        SELECT COUNT(*) as attempts FROM login_attempts 
        WHERE username = ? AND attempt_time > ? AND success = FALSE
    """, (username, cutoff_time))
    
    result = cursor.fetchone()
    recent_attempts = result['attempts'] if result else 0
    
    if recent_attempts >= MAX_LOGIN_ATTEMPTS:
        cursor.execute("UPDATE users SET locked_until = ? WHERE username = ?",
                      ((datetime.now() + timedelta(minutes=LOGIN_TIMEOUT_MINUTES)).isoformat(), username))
        conn.commit()
        return False, f"Too many attempts. Account locked for {LOGIN_TIMEOUT_MINUTES} minutes."
    
    return True, ""

def record_login_attempt(username: str, success: bool):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO login_attempts (username, success) VALUES (?, ?)", (username, success))
    
    if success:
        cursor.execute("UPDATE users SET login_attempts = 0, locked_until = NULL WHERE username = ?", (username,))
    else:
        cursor.execute("UPDATE users SET login_attempts = login_attempts + 1 WHERE username = ?", (username,))
    
    conn.commit()

# ================================
# CACHED DATA FUNCTIONS
# ================================
@st.cache_data(ttl=300)
def get_leaderboard_data():
    import pandas as pd
    conn = get_db_connection()
    df = pd.read_sql_query("""
        SELECT username, xp_points, quiz_score, cases_solved, level, last_active
        FROM leaderboard ORDER BY xp_points DESC
    """, conn)
    return df

@st.cache_data(ttl=60)
def get_user_count() -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM users")
    result = cursor.fetchone()
    return result['count'] if result else 0

# ================================
# USER MANAGEMENT
# ================================
def create_user(username: str, password: str) -> Tuple[bool, str]:
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        return False, "Username already exists"
    
    password_hash, salt = hash_password_secure(password)
    
    cursor.execute("INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
                  (username, password_hash, salt))
    cursor.execute("INSERT INTO leaderboard (username, xp_points) VALUES (?, 0)", (username,))
    
    conn.commit()
    return True, "Account created successfully"

def authenticate_user(username: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
    can_attempt, message = check_login_rate_limit(username)
    if not can_attempt:
        return False, message, None
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    
    if not user:
        record_login_attempt(username, False)
        return False, "Invalid username or password", None
    
    if verify_password(password, user['password_hash'], user['salt']):
        record_login_attempt(username, True)
        cursor.execute("UPDATE users SET last_login = ? WHERE id = ?",
                      (datetime.now().isoformat(), user['id']))
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
    
    if not user:
        return 0
    
    today = datetime.now().date()
    last_active = datetime.fromisoformat(user['last_active_date']).date() if user['last_active_date'] else None
    
    if last_active:
        yesterday = today - timedelta(days=1)
        if last_active == yesterday:
            new_streak = user['daily_streak'] + 1
        elif last_active == today:
            new_streak = user['daily_streak']
        else:
            new_streak = 1
    else:
        new_streak = 1
    
    cursor.execute("UPDATE users SET daily_streak = ?, last_active_date = ? WHERE username = ?",
                  (new_streak, today.isoformat(), username))
    conn.commit()
    return new_streak

def add_xp(username: str, points: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("UPDATE users SET xp_points = xp_points + ? WHERE username = ?", (points, username))
    cursor.execute("UPDATE leaderboard SET xp_points = xp_points + ?, last_active = ? WHERE username = ?",
                  (points, datetime.now().isoformat(), username))
    conn.commit()

# ================================
# LEVEL SYSTEM
# ================================
LEVELS = {
    1: {"name_en": "Medical Student", "name_ku": "خوێندکاری پزیشکی", "name_ar": "طالب طب", "icon": "🌱", "min_xp": 0, "max_xp": 99},
    2: {"name_en": "Intern", "name_ku": "کارمەندی ڕاهێنان", "name_ar": "طبيب امتياز", "icon": "📖", "min_xp": 100, "max_xp": 299},
    3: {"name_en": "Resident", "name_ku": "پزیشکی دانیشتوو", "name_ar": "طبيب مقيم", "icon": "🚀", "min_xp": 300, "max_xp": 599},
    4: {"name_en": "Specialist", "name_ku": "پزیشکی پسپۆڕ", "name_ar": "أخصائي", "icon": "🏆", "min_xp": 600, "max_xp": 999},
    5: {"name_en": "Consultant", "name_ku": "پزیشکی ڕاوێژکار", "name_ar": "استشاري", "icon": "👨‍⚕️", "min_xp": 1000, "max_xp": 1999},
    6: {"name_en": "Professor", "name_ku": "پڕۆفیسۆر", "name_ar": "أستاذ", "icon": "🎓", "min_xp": 2000, "max_xp": 4999},
    7: {"name_en": "Legend", "name_ku": "ئەفسانە", "name_ar": "أسطورة", "icon": "👑", "min_xp": 5000, "max_xp": float('inf')}
}

def get_level_name(level: int, lang: str = 'en') -> str:
    return LEVELS[level].get(f"name_{lang}", LEVELS[level]["name_en"])

def get_user_level(xp_points: int) -> int:
    for level in range(7, 0, -1):
        if xp_points >= LEVELS[level]["min_xp"]:
            return level
    return 1

def get_level_progress(xp_points: int) -> float:
    current_level = get_user_level(xp_points)
    if current_level >= 7:
        return 100.0
    
    current_min = LEVELS[current_level]["min_xp"]
    next_min = LEVELS[current_level + 1]["min_xp"]
    
    progress = ((xp_points - current_min) / (next_min - current_min)) * 100
    return min(progress, 100)

# ================================
# DISEASE DATABASE
# ================================
DISEASE_DATABASE = {
    "Diabetes Mellitus Type 1": {
        "symptoms_en": ["Polyuria", "Polydipsia", "Weight loss", "Fatigue", "Blurred vision"],
        "symptoms_ku": ["میزی زۆر", "تینوویەتی زۆر", "کێش کەمبوونەوە", "ماندوویی", "بینی تەڵخ"],
        "symptoms_ar": ["كثرة التبول", "العطش الشديد", "فقدان الوزن", "التعب", "عدم وضوح الرؤية"],
        "treatment_en": ["Insulin therapy", "Carbohydrate counting", "Regular exercise"],
        "treatment_ku": ["چارەسەری ئەنسولین", "ژمێریاری کاربۆهیدرات", "وەرزشی ڕێک"],
        "treatment_ar": ["العلاج بالأنسولين", "حساب الكربوهيدرات", "التمارين المنتظمة"],
        "risk_level": "High",
    },
    "Diabetes Mellitus Type 2": {
        "symptoms_en": ["Polyuria", "Polydipsia", "Fatigue", "Slow wound healing"],
        "symptoms_ku": ["میزی زۆر", "تینوویەتی زۆر", "ماندوویی", "خاوی چاکبوونەوەی برین"],
        "symptoms_ar": ["كثرة التبول", "العطش الشديد", "التعب", "بطء التئام الجروح"],
        "treatment_en": ["Metformin", "Lifestyle modification", "Regular exercise"],
        "treatment_ku": ["مێتفۆرمین", "گۆڕینی شێوازی ژیان", "وەرزشی ڕێک"],
        "treatment_ar": ["الميتفورمين", "تعديل نمط الحياة", "التمارين المنتظمة"],
        "risk_level": "Moderate",
    },
    "Essential Hypertension": {
        "symptoms_en": ["Often asymptomatic", "Headache", "Dizziness", "Blurred vision"],
        "symptoms_ku": ["زۆرجار بێ نیشانە", "سەرئێشە", "سەرگێژخواردن", "بینی تەڵخ"],
        "symptoms_ar": ["غالباً بدون أعراض", "صداع", "دوخة", "عدم وضوح الرؤية"],
        "treatment_en": ["ACE inhibitors", "Lifestyle changes", "Low sodium diet"],
        "treatment_ku": ["بەرگرەکانی ACE", "گۆڕینی شێوازی ژیان", "خواردنی کەم نمەک"],
        "treatment_ar": ["مثبطات ACE", "تغيير نمط الحياة", "نظام غذائي منخفض الصوديوم"],
        "risk_level": "Low",
    },
    "Acute Myocardial Infarction": {
        "symptoms_en": ["Severe chest pain", "Diaphoresis", "Dyspnea", "Nausea", "Anxiety"],
        "symptoms_ku": ["ئازاری توندی سنگ", "ئارەقەکردنی زۆر", "تەنگی هەناسە", "سکچوون", "دڵەڕاوکێ"],
        "symptoms_ar": ["ألم شديد في الصدر", "تعرق غزير", "ضيق التنفس", "غثيان", "قلق"],
        "treatment_en": ["Aspirin 300mg", "Nitroglycerin", "Morphine", "Oxygen"],
        "treatment_ku": ["ئەسپیرین ٣٠٠مگ", "نایترۆگلیسیرین", "مۆرفین", "ئۆکسجین"],
        "treatment_ar": ["أسبرين 300 ملغ", "نيتروجليسرين", "مورفين", "أكسجين"],
        "risk_level": "Critical",
    },
    "Community-Acquired Pneumonia": {
        "symptoms_en": ["Fever", "Productive cough", "Dyspnea", "Pleuritic chest pain"],
        "symptoms_ku": ["تا", "کۆخەی بەرھەمدار", "تەنگی هەناسە", "ئازاری سنگی پلوریتی"],
        "symptoms_ar": ["حمى", "سعال منتج", "ضيق التنفس", "ألم صدري جنبي"],
        "treatment_en": ["Amoxicillin-clavulanate", "Azithromycin", "Oxygen if needed"],
        "treatment_ku": ["ئەمۆکسیسیلین-کلاڤولانات", "ئازیترۆمایسین", "ئۆکسجین ئەگەر پێویست بوو"],
        "treatment_ar": ["أموكسيسيلين-كلافولانات", "أزيثروميسين", "أكسجين إذا لزم"],
        "risk_level": "Moderate",
    }
}

# ================================
# LAB TESTS DATABASE
# ================================
LAB_TESTS = {
    "Hemoglobin": {"category": "Hematology", "normal": "12-16 g/dL", "description_en": "Oxygen-carrying capacity", "description_ku": "توانای هەڵگرتنی ئۆکسجین", "description_ar": "القدرة على حمل الأكسجين"},
    "WBC Count": {"category": "Hematology", "normal": "4,000-11,000/µL", "description_en": "Infection/inflammation marker", "description_ku": "نیشانەی هەوکردن", "description_ar": "علامة العدوى/الالتهاب"},
    "RBC Count": {"category": "Hematology", "normal": "4.5-5.5 million/µL", "description_en": "Oxygen transport", "description_ku": "گواستنەوەی ئۆکسجین", "description_ar": "نقل الأكسجين"},
    "Platelet Count": {"category": "Hematology", "normal": "150,000-450,000/µL", "description_en": "Clotting ability", "description_ku": "توانای مەیین", "description_ar": "القدرة على التخثر"},
    "Fasting Glucose": {"category": "Biochemistry", "normal": "70-100 mg/dL", "description_en": "Diabetes screening", "description_ku": "پشکنینی شەکرە", "description_ar": "فحص السكري"},
    "HbA1c": {"category": "Biochemistry", "normal": "4.0-5.6%", "description_en": "3-month glucose average", "description_ku": "تێکڕای شەکری ٣ مانگ", "description_ar": "متوسط السكر لـ 3 أشهر"},
    "Creatinine": {"category": "Biochemistry", "normal": "0.6-1.3 mg/dL", "description_en": "Kidney function", "description_ku": "کاری گورچیلە", "description_ar": "وظيفة الكلى"},
    "ALT": {"category": "Biochemistry", "normal": "10-40 U/L", "description_en": "Liver enzyme", "description_ku": "ئەنزیمی جگەر", "description_ar": "إنزيم الكبد"},
    "Sodium": {"category": "Biochemistry", "normal": "135-145 mmol/L", "description_en": "Electrolyte", "description_ku": "ئەلیکترۆلیت", "description_ar": "كهرل"},
    "Potassium": {"category": "Biochemistry", "normal": "3.5-5.0 mmol/L", "description_en": "Electrolyte", "description_ku": "ئەلیکترۆلیت", "description_ar": "كهرل"},
    "Total Cholesterol": {"category": "Lipids", "normal": "<200 mg/dL", "description_en": "Lipid profile", "description_ku": "پرۆفایلی چەوری", "description_ar": "ملف الدهون"},
    "Troponin I": {"category": "Cardiac", "normal": "<0.04 ng/mL", "description_en": "Myocardial injury", "description_ku": "برینداربوونی ماسوولکەی دڵ", "description_ar": "إصابة عضلة القلب"},
    "TSH": {"category": "Endocrine", "normal": "0.4-4.0 mIU/L", "description_en": "Thyroid function", "description_ku": "کاری ڕژێنی دەرەقی", "description_ar": "وظيفة الغدة الدرقية"},
}

# ================================
# DRUG DATABASE
# ================================
DRUG_DATABASE = {
    "Cardiovascular": {
        "Lisinopril": {
            "class": "ACE Inhibitor", "dose": "10-40mg daily",
            "indications_en": "Hypertension, HF", "indications_ku": "پەستانی خوێن, شکستی دڵ", "indications_ar": "ارتفاع ضغط الدم, فشل القلب",
            "side_effects_en": "Cough, angioedema", "side_effects_ku": "کۆخە, ئاوسانی ڕوو", "side_effects_ar": "سعال, وذمة وعائية"
        },
        "Losartan": {
            "class": "ARB", "dose": "50-100mg daily",
            "indications_en": "Hypertension, HF", "indications_ku": "پەستانی خوێن, شکستی دڵ", "indications_ar": "ارتفاع ضغط الدم, فشل القلب",
            "side_effects_en": "Dizziness, hyperkalemia", "side_effects_ku": "سەرگێژخواردن, پۆتاسیۆمی بەرز", "side_effects_ar": "دوخة, فرط بوتاسيوم الدم"
        },
        "Amlodipine": {
            "class": "CCB", "dose": "5-10mg daily",
            "indications_en": "Hypertension, angina", "indications_ku": "پەستانی خوێن, ئازاری سنگ", "indications_ar": "ارتفاع ضغط الدم, ذبحة صدرية",
            "side_effects_en": "Edema, flushing", "side_effects_ku": "ئاوسان, سووربوونەوە", "side_effects_ar": "وذمة, احمرار"
        },
        "Metoprolol": {
            "class": "Beta Blocker", "dose": "25-200mg daily",
            "indications_en": "Hypertension, angina", "indications_ku": "پەستانی خوێن, ئازاری سنگ", "indications_ar": "ارتفاع ضغط الدم, ذبحة صدرية",
            "side_effects_en": "Bradycardia, fatigue", "side_effects_ku": "خاوی لێدانی دڵ, ماندوویی", "side_effects_ar": "بطء القلب, إرهاق"
        },
    },
    "Endocrinology": {
        "Metformin": {
            "class": "Biguanide", "dose": "500-2000mg daily",
            "indications_en": "Type 2 DM", "indications_ku": "شەکرەی جۆری ٢", "indications_ar": "السكري النوع 2",
            "side_effects_en": "GI upset, lactic acidosis", "side_effects_ku": "ناخۆشی گەدە, ترشێتی لاکتیک", "side_effects_ar": "اضطراب معدي, حماض لاكتيكي"
        },
        "Insulin Glargine": {
            "class": "Long-acting Insulin", "dose": "Individualized",
            "indications_en": "Type 1 & 2 DM", "indications_ku": "شەکرەی جۆری ١ و ٢", "indications_ar": "السكري النوع 1 و 2",
            "side_effects_en": "Hypoglycemia", "side_effects_ku": "شەکری نزم", "side_effects_ar": "نقص سكر الدم"
        },
    },
    "Antibiotics": {
        "Amoxicillin": {
            "class": "Penicillin", "dose": "500-875mg BID",
            "indications_en": "Respiratory, UTI", "indications_ku": "هەناسە, میزەڕۆ", "indications_ar": "الجهاز التنفسي, المسالك البولية",
            "side_effects_en": "Diarrhea, rash", "side_effects_ku": "سکچوون, پەڵە", "side_effects_ar": "إسهال, طفح جلدي"
        },
        "Azithromycin": {
            "class": "Macrolide", "dose": "250-500mg daily",
            "indications_en": "Respiratory infections", "indications_ku": "هەوکردنی هەناسە", "indications_ar": "التهابات الجهاز التنفسي",
            "side_effects_en": "GI upset", "side_effects_ku": "ناخۆشی گەدە", "side_effects_ar": "اضطراب معدي"
        },
    },
    "Analgesics": {
        "Ibuprofen": {
            "class": "NSAID", "dose": "200-800mg TID",
            "indications_en": "Pain, inflammation", "indications_ku": "ئازار, هەوکردن", "indications_ar": "ألم, التهاب",
            "side_effects_en": "GI ulcer", "side_effects_ku": "برینی گەدە", "side_effects_ar": "قرحة معدية"
        },
        "Acetaminophen": {
            "class": "Analgesic", "dose": "500-1000mg Q6H",
            "indications_en": "Pain, fever", "indications_ku": "ئازار, تا", "indications_ar": "ألم, حمى",
            "side_effects_en": "Hepatotoxicity", "side_effects_ku": "ژەهراویی جگەر", "side_effects_ar": "سمية كبدية"
        },
    }
}

# ================================
# HELPER FUNCTIONS FOR MULTILINGUAL DATA
# ================================
def get_symptoms(disease_info: Dict, lang: str) -> List[str]:
    return disease_info.get(f"symptoms_{lang}", disease_info.get("symptoms_en", []))

def get_treatment(disease_info: Dict, lang: str) -> List[str]:
    return disease_info.get(f"treatment_{lang}", disease_info.get("treatment_en", []))

def get_description(lab_info: Dict, lang: str) -> str:
    return lab_info.get(f"description_{lang}", lab_info.get("description_en", ""))

def get_indications(drug_info: Dict, lang: str) -> str:
    return drug_info.get(f"indications_{lang}", drug_info.get("indications_en", ""))

def get_side_effects(drug_info: Dict, lang: str) -> str:
    return drug_info.get(f"side_effects_{lang}", drug_info.get("side_effects_en", ""))

def get_risk_level_translated(risk: str, lang: str) -> str:
    risk_map = {
        "en": {"Critical": "Critical", "High": "High", "Moderate": "Moderate", "Low": "Low"},
        "ku": {"Critical": "زۆر مەترسیدار", "High": "مەترسیدار", "Moderate": "مامناوەند", "Low": "کەم"},
        "ar": {"Critical": "حرج", "High": "مرتفع", "Moderate": "متوسط", "Low": "منخفض"}
    }
    return risk_map.get(lang, risk_map['en']).get(risk, risk)

# ================================
# CSS STYLING WITH RTL SUPPORT
# ================================
def load_css(lang: str = 'en'):
    rtl_styles = ""
    if lang in ['ku', 'ar']:
        rtl_styles = """
            body { direction: rtl; text-align: right; }
            .stApp { direction: rtl; }
            [data-testid="stSidebar"] { direction: rtl; text-align: right; }
            [data-testid="stSidebar"] .stButton > button { text-align: right !important; }
            .stMarkdown, .stText, p, h1, h2, h3, h4 { text-align: right; }
            .stRadio label { text-align: right; }
            .stSelectbox { direction: rtl; }
            input { text-align: right; }
        """
    
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        * {{ font-family: 'Inter', sans-serif; }}
        
        .stApp {{
            background: linear-gradient(135deg, #0a0a1a, #1a1a3e, #0a0a1a);
        }}
        
        .glass-card {{
            background: rgba(255,255,255,0.03);
            backdrop-filter: blur(20px);
            border-radius: 16px;
            padding: 1.5rem;
            border: 1px solid rgba(99,102,241,0.2);
            margin: 1rem 0;
            transition: all 0.3s ease;
        }}
        
        .glass-card:hover {{
            border-color: rgba(139,92,246,0.4);
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(99,102,241,0.1);
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, rgba(99,102,241,0.1), rgba(139,92,246,0.05));
            border-radius: 16px;
            padding: 1.2rem;
            text-align: center;
            border: 1px solid rgba(99,102,241,0.2);
        }}
        
        .stat-number {{
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #6366f1, #a78bfa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .badge {{
            display: inline-block;
            padding: 0.3rem 1rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }}
        
        .badge-primary {{ background: rgba(99,102,241,0.2); color: #a78bfa; }}
        .badge-success {{ background: rgba(16,185,129,0.2); color: #10b981; }}
        .badge-danger {{ background: rgba(239,68,68,0.2); color: #ef4444; }}
        .badge-warning {{ background: rgba(251,191,36,0.2); color: #fbbf24; }}
        
        .stButton > button {{
            background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }}
        
        .stButton > button:hover {{
            background: linear-gradient(135deg, #8b5cf6, #a78bfa) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px rgba(99,102,241,0.3) !important;
        }}
        
        .stTextInput > div > div, .stTextArea > div > div {{
            background: rgba(255,255,255,0.05) !important;
            border: 1px solid rgba(99,102,241,0.2) !important;
            border-radius: 10px !important;
            color: white !important;
        }}
        
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #0a0a1a, #1a1a3e, #0a0a1a) !important;
            border-right: 2px solid rgba(99,102,241,0.2) !important;
        }}
        
        [data-testid="stSidebar"] .stButton > button {{
            background: rgba(99,102,241,0.1) !important;
            border: 1px solid rgba(99,102,241,0.2) !important;
            color: white !important;
            padding: 0.5rem 1rem !important;
            margin: 2px 0 !important;
        }}
        
        [data-testid="stSidebar"] .stButton > button:hover {{
            background: rgba(99,102,241,0.2) !important;
            border-color: rgba(139,92,246,0.4) !important;
            transform: translateX(5px) !important;
        }}
        
        h1 {{
            background: linear-gradient(135deg, #6366f1, #8b5cf6, #a78bfa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800 !important;
        }}
        
        ::-webkit-scrollbar {{ width: 8px; }}
        ::-webkit-scrollbar-track {{ background: rgba(255,255,255,0.05); }}
        ::-webkit-scrollbar-thumb {{ background: linear-gradient(180deg, #6366f1, #8b5cf6); border-radius: 10px; }}
        
        @keyframes float {{
            0%, 100% {{ transform: translateY(0px); }}
            50% {{ transform: translateY(-10px); }}
        }}
        
        .language-switcher {{
            display: flex;
            gap: 0.5rem;
            justify-content: center;
            padding: 0.5rem;
        }}
        
        {rtl_styles}
    </style>
    """, unsafe_allow_html=True)

# ================================
# SESSION STATE INITIALIZATION
# ================================
def init_session_state():
    defaults = {
        'logged_in': False,
        'username': "",
        'user_data': None,
        'xp_points': 0,
        'quiz_score': 0,
        'total_cases': 0,
        'correct_diagnoses': 0,
        'streak': 0,
        'current_page': "Dashboard",
        'flashcard_flipped': False,
        'comprehensive_exam': None,
        'comprehensive_answers': {},
        'comprehensive_submitted': False,
        'comprehensive_score': 0,
        'current_room_id': None,
        'editing_drug': None,
        'editing_lab': None,
        'current_case': None,
        'achievements': [],
        'language': 'en',
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# ================================
# LOAD CSS WITH CURRENT LANGUAGE
# ================================
load_css(st.session_state.language)

# ================================
# INITIALIZE DATABASE
# ================================
init_database()

# ================================
# LOGIN PAGE
# ================================
if not st.session_state.logged_in:
    # Language switcher for login page
    col_lang1, col_lang2, col_lang3 = st.columns([3, 2, 3])
    with col_lang2:
        st.markdown('<div class="language-switcher">', unsafe_allow_html=True)
        cols = st.columns(3)
        for i, (code, name) in enumerate([('en', 'English'), ('ku', 'کوردی'), ('ar', 'العربية')]):
            with cols[i]:
                if st.button(name, key=f"lang_{code}", use_container_width=True):
                    st.session_state.language = code
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    lang = st.session_state.language
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div style="text-align: center; padding: 3rem 0;">
            <div style="font-size: 5rem; animation: float 3s ease-in-out infinite;">🩺</div>
            <h1 style="font-size: 3rem;">Dr.Danyal</h1>
            <p style="color: rgba(255,255,255,0.6); font-size: 1.1rem;">{t('app_subtitle', lang)}</p>
        </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs([t('login', lang), t('register', lang)])
        
        with tab1:
            with st.form("login_form"):
                username = st.text_input(t('username', lang), placeholder=t('enter_username', lang))
                password = st.text_input(t('password', lang), type="password", placeholder=t('enter_password', lang))
                
                if st.form_submit_button(t('login_button', lang), type="primary", use_container_width=True):
                    success, message, user_data = authenticate_user(username, password)
                    
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.user_data = user_data
                        st.session_state.xp_points = user_data['xp_points']
                        st.session_state.quiz_score = user_data['quiz_score']
                        st.session_state.total_cases = user_data['total_cases']
                        st.session_state.correct_diagnoses = user_data['correct_diagnoses']
                        st.session_state.streak = update_user_streak(username)
                        
                        # Load language preference
                        if user_data.get('language_preference'):
                            st.session_state.language = user_data['language_preference']
                        
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
        
        with tab2:
            with st.form("register_form"):
                new_username = st.text_input(t('choose_username', lang), placeholder=t('username', lang))
                new_password = st.text_input(t('choose_password', lang), type="password", placeholder=t('password', lang))
                confirm_password = st.text_input(t('confirm_password', lang), type="password", placeholder=t('confirm_password_placeholder', lang))
                
                if st.form_submit_button(t('register_button', lang), type="primary", use_container_width=True):
                    if new_password != confirm_password:
                        st.error(f"❌ {t('passwords_dont_match', lang)}")
                    else:
                        success, message = create_user(new_username, new_password)
                        if success:
                            st.success(f"✅ {t('account_created', lang)}")
                        else:
                            st.error(f"❌ {message}")
    
    st.stop()

# ================================
# SIDEBAR
# ================================
lang = st.session_state.language

with st.sidebar:
    # Language Switcher
    st.markdown('<div class="language-switcher">', unsafe_allow_html=True)
    cols = st.columns(3)
    languages = [('en', 'EN'), ('ku', 'KU'), ('ar', 'AR')]
    for i, (code, name) in enumerate(languages):
        with cols[i]:
            if st.button(name, key=f"sidebar_lang_{code}", use_container_width=True):
                st.session_state.language = code
                # Save preference
                conn = get_db_connection()
                conn.execute("UPDATE users SET language_preference = ? WHERE username = ?",
                           (code, st.session_state.username))
                conn.commit()
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    level = get_user_level(st.session_state.xp_points)
    level_info = LEVELS[level]
    progress = get_level_progress(st.session_state.xp_points)
    
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem 0;">
        <div style="font-size: 3rem;">{level_info['icon']}</div>
        <div style="font-weight: 700; color: #a78bfa;">{st.session_state.username}</div>
        <span class="badge badge-primary">{get_level_name(level, lang)}</span>
    </div>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin: 1rem 0;">
        <div style="background: rgba(99,102,241,0.1); padding: 0.5rem; border-radius: 10px; text-align: center;">
            <div style="font-weight: 700; color: #a78bfa;">⭐ {st.session_state.xp_points}</div>
            <div style="font-size: 0.65rem; color: #888;">{t('xp', lang)}</div>
        </div>
        <div style="background: rgba(99,102,241,0.1); padding: 0.5rem; border-radius: 10px; text-align: center;">
            <div style="font-weight: 700; color: #a78bfa;">📊 {st.session_state.quiz_score}</div>
            <div style="font-size: 0.65rem; color: #888;">{t('quiz_score', lang)}</div>
        </div>
        <div style="background: rgba(99,102,241,0.1); padding: 0.5rem; border-radius: 10px; text-align: center;">
            <div style="font-weight: 700; color: #a78bfa;">🔥 {st.session_state.streak}</div>
            <div style="font-size: 0.65rem; color: #888;">{t('streak', lang)}</div>
        </div>
        <div style="background: rgba(99,102,241,0.1); padding: 0.5rem; border-radius: 10px; text-align: center;">
            <div style="font-weight: 700; color: #a78bfa;">🩺 {st.session_state.total_cases}</div>
            <div style="font-size: 0.65rem; color: #888;">{t('cases', lang)}</div>
        </div>
    </div>
    
    <div style="width: 100%; height: 6px; background: rgba(255,255,255,0.1); border-radius: 10px; overflow: hidden; margin: 0.5rem 0;">
        <div style="width: {progress:.1f}%; height: 100%; background: linear-gradient(90deg, #6366f1, #8b5cf6); border-radius: 10px;"></div>
    </div>
    <div style="font-size: 0.65rem; color: #888; text-align: right;">{t('level_progress', lang)} {progress:.0f}%</div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation
    pages = [
        ("dashboard", "Dashboard"),
        ("diseases", "Diseases"),
        ("case_analysis", "Case Analysis"),
        ("quiz", "Quiz"),
        ("comprehensive_exam", "Comprehensive Exam"),
        ("spaced_repetition", "Spaced Repetition"),
        ("lab_tests", "Lab Tests"),
        ("pharmacology", "Pharmacology"),
        ("drug_interactions", "Drug Interactions"),
        ("leaderboard", "Leaderboard"),
        ("medical_news", "Medical News"),
        ("ai_assistant", "AI Assistant"),
        ("clinical_notes", "Clinical Notes"),
        ("achievements", "Achievements"),
    ]
    
    for key, page_name in pages:
        if st.button(t(key, lang), use_container_width=True, key=f"nav_{page_name}"):
            st.session_state.current_page = page_name
            st.rerun()
    
    st.markdown("---")
    
    if st.button(t('logout', lang), use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()
    
    st.markdown(f"""
    <div style="text-align: center; padding: 0.5rem; font-size: 0.7rem; color: #666;">
        <span class="badge badge-primary">{t('version', lang)}</span>
        <p>© 2024 Dr.Danyal</p>
    </div>
    """, unsafe_allow_html=True)

# ================================
# PAGE ROUTING
# ================================
page = st.session_state.current_page

if page == "Dashboard":
    st.markdown(f'<h1 style="text-align: center;">{t("dashboard", lang)}</h1>', unsafe_allow_html=True)
    
    cols = st.columns(5)
    metrics = [
        (t("diseases_count", lang), len(DISEASE_DATABASE)),
        (t("drugs_count", lang), sum(len(d) for d in DRUG_DATABASE.values())),
        (t("tests_count", lang), len(LAB_TESTS)),
        (t("xp", lang), st.session_state.xp_points),
        (t("streak", lang), st.session_state.streak)
    ]
    
    for col, (label, value) in zip(cols, metrics):
        with col:
            st.markdown(f'<div class="stat-card"><h3>{label}</h3><div class="stat-number">{value}</div></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="glass-card">
            <h3>{t('your_progress', lang)}</h3>
            <p>{t('level', lang)}: {level_info['icon']} {get_level_name(level, lang)}</p>
            <p>{t('quiz_score', lang)}: {st.session_state.quiz_score}</p>
            <p>{t('cases_solved', lang)}: {st.session_state.total_cases}</p>
            <p>{t('accuracy', lang)}: {(st.session_state.correct_diagnoses / max(st.session_state.total_cases, 1) * 100):.1f}%</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="glass-card">
            <h3>{t('platform_stats', lang)}</h3>
            <p>{t('total_users', lang)}: {get_user_count()}</p>
            <p>{t('diseases_count', lang)}: {len(DISEASE_DATABASE)}</p>
            <p>{t('drugs_count', lang)}: {sum(len(d) for d in DRUG_DATABASE.values())}</p>
            <p>{t('tests_count', lang)}: {len(LAB_TESTS)}</p>
        </div>
        """, unsafe_allow_html=True)

elif page == "Diseases":
    st.markdown(f'<h2>{t("disease_library", lang)}</h2>', unsafe_allow_html=True)
    
    search = st.text_input(t("search", lang), placeholder=t("search_placeholder", lang))
    risk_filter = st.selectbox(t("risk_level", lang), [t("all", lang), t("critical", lang), t("high", lang), t("moderate", lang), t("low", lang)])
    
    risk_map_reverse = {
        t("critical", lang): "Critical", t("high", lang): "High", 
        t("moderate", lang): "Moderate", t("low", lang): "Low"
    }
    
    filtered = DISEASE_DATABASE.copy()
    if search:
        filtered = {k: v for k, v in filtered.items() if search.lower() in k.lower()}
    if risk_filter != t("all", lang):
        english_risk = risk_map_reverse.get(risk_filter, risk_filter)
        filtered = {k: v for k, v in filtered.items() if v.get("risk_level") == english_risk}
    
    cols = st.columns(2)
    for i, (disease, info) in enumerate(filtered.items()):
        with cols[i % 2]:
            with st.expander(f"🩺 {disease}"):
                risk_color = {"Critical": "#ef4444", "High": "#f59e0b", "Moderate": "#06b6d4", "Low": "#10b981"}
                translated_risk = get_risk_level_translated(info.get('risk_level', 'Low'), lang)
                st.markdown(f"**{t('risk', lang)}:** <span style='color:{risk_color.get(info.get('risk_level', 'Low'))}'>{translated_risk}</span>", unsafe_allow_html=True)
                st.markdown(f"**{t('symptoms', lang)}:** {', '.join(get_symptoms(info, lang)[:5])}")
                st.markdown(f"**{t('treatment', lang)}:** {', '.join(get_treatment(info, lang)[:3])}")

elif page == "Case Analysis":
    st.markdown(f'<h2>{t("clinical_case_analysis", lang)}</h2>', unsafe_allow_html=True)
    
    if st.button(t("generate_new_case", lang), type="primary", use_container_width=True):
        disease = random.choice(list(DISEASE_DATABASE.keys()))
        info = DISEASE_DATABASE[disease]
        gender_map = {"en": random.choice(["Male", "Female"]), "ku": random.choice(["نێر", "مێ"]), "ar": random.choice(["ذكر", "أنثى"])}
        st.session_state.current_case = {
            "id": f"CASE-{random.randint(1000,9999)}",
            "age": random.randint(18, 85),
            "gender": gender_map,
            "symptoms": random.sample(get_symptoms(info, lang), min(5, len(get_symptoms(info, lang)))),
            "diagnosis": disease,
            "risk": info["risk_level"]
        }
        st.rerun()
    
    if st.session_state.current_case:
        case = st.session_state.current_case
        gender = case["gender"].get(lang, case["gender"].get("en", ""))
        st.markdown(f"""
        <div class="glass-card">
            <h3>{t('case_id', lang)} #{case['id']}</h3>
            <p><strong>{t('patient', lang)}:</strong> {case['age']} {t('years_old', lang)} {gender}</p>
            <p><strong>{t('symptoms', lang)}:</strong> {', '.join(case['symptoms'])}</p>
        </div>
        """, unsafe_allow_html=True)
        
        diagnosis = st.selectbox(t("your_diagnosis", lang), list(DISEASE_DATABASE.keys()))
        
        if st.button(t("submit", lang), type="primary"):
            st.session_state.total_cases += 1
            if diagnosis == case["diagnosis"]:
                st.session_state.correct_diagnoses += 1
                add_xp(st.session_state.username, 20)
                st.success(f"🎉 {t('correct', lang)}! {case['diagnosis']}")
            else:
                st.error(f"❌ {t('incorrect', lang)}. {case['diagnosis']}")
            
            conn = get_db_connection()
            conn.execute("UPDATE users SET total_cases = ?, correct_diagnoses = ? WHERE username = ?",
                        (st.session_state.total_cases, st.session_state.correct_diagnoses, st.session_state.username))
            conn.commit()

elif page == "Quiz":
    st.markdown(f'<h2>{t("medical_quiz", lang)}</h2>', unsafe_allow_html=True)
    
    diseases = list(DISEASE_DATABASE.keys())
    if diseases:
        disease = random.choice(diseases)
        info = DISEASE_DATABASE[disease]
        correct = get_symptoms(info, lang)[0]
        wrong = [s for d in diseases if d != disease for s in get_symptoms(DISEASE_DATABASE[d], lang)[:1] if s != correct][:3]
        options = [correct] + wrong
        random.shuffle(options)
        
        st.markdown(f'<div class="glass-card"><h3>{correct} {t("is_characteristic_of", lang)} <strong>{disease}</strong>?</h3></div>', unsafe_allow_html=True)
        
        answer = st.radio(t("select_answer", lang), options, key="quiz_ans")
        
        if st.button(t("submit_answer", lang), type="primary"):
            if answer == correct:
                st.session_state.quiz_score += 1
                add_xp(st.session_state.username, 10)
                st.success(f"🎉 {t('correct', lang)}!")
            else:
                st.error(f"❌ {t('incorrect', lang)}. {t('answer_was', lang)}: {correct}")
            
            conn = get_db_connection()
            conn.execute("UPDATE users SET quiz_score = ? WHERE username = ?",
                        (st.session_state.quiz_score, st.session_state.username))
            conn.commit()
            st.rerun()

elif page == "Comprehensive Exam":
    st.markdown(f'<h2>{t("comprehensive_exam_title", lang)}</h2>', unsafe_allow_html=True)
    
    if st.session_state.comprehensive_exam is None:
        if st.button(t("start_exam", lang), type="primary", use_container_width=True):
            questions = []
            for disease, info in DISEASE_DATABASE.items():
                symptoms = get_symptoms(info, lang)
                if symptoms:
                    correct = random.choice(symptoms)
                    all_symptoms = [s for d in DISEASE_DATABASE for s in get_symptoms(DISEASE_DATABASE[d], lang) if s != correct]
                    wrong_opts = random.sample(all_symptoms, min(3, len(all_symptoms)))
                    opts = [correct] + wrong_opts[:3]
                    random.shuffle(opts)
                    questions.append({
                        "question": f"{disease}?",
                        "options": opts,
                        "correct": opts.index(correct)
                    })
            
            st.session_state.comprehensive_exam = random.sample(questions, min(len(DISEASE_DATABASE), len(questions)))
            st.session_state.comprehensive_answers = {}
            st.session_state.comprehensive_submitted = False
            st.rerun()
    
    elif not st.session_state.comprehensive_submitted:
        for i, q in enumerate(st.session_state.comprehensive_exam):
            st.markdown(f"**{i+1}. {q['question']}**")
            ans = st.radio(f"Q{i}", q["options"], key=f"exam_{i}", label_visibility="collapsed")
            st.session_state.comprehensive_answers[i] = q["options"].index(ans) if ans else -1
        
        if st.button(t("submit_exam", lang), type="primary"):
            score = sum(1 for i, q in enumerate(st.session_state.comprehensive_exam) 
                       if st.session_state.comprehensive_answers.get(i) == q["correct"])
            st.session_state.comprehensive_score = score
            st.session_state.comprehensive_submitted = True
            add_xp(st.session_state.username, score * 2)
            st.rerun()
    
    else:
        score = st.session_state.comprehensive_score
        total = len(st.session_state.comprehensive_exam)
        st.markdown(f'<div class="glass-card"><h2>🎉 {t("score", lang)}: {score}/{total} ({(score/total*100):.1f}%)</h2></div>', unsafe_allow_html=True)
        if st.button(t("retake", lang)):
            st.session_state.comprehensive_exam = None
            st.rerun()

elif page == "Spaced Repetition":
    st.markdown(f'<h2>{t("spaced_repetition_title", lang)}</h2>', unsafe_allow_html=True)
    
    disease = random.choice(list(DISEASE_DATABASE.keys()))
    info = DISEASE_DATABASE[disease]
    
    if st.session_state.flashcard_flipped:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center; padding: 2rem;">
            <h3>{disease}</h3>
            <p><strong>{t('symptoms', lang)}:</strong> {', '.join(get_symptoms(info, lang)[:4])}</p>
            <p style="color: #a78bfa;"><strong>{t('treatment', lang)}:</strong> {', '.join(get_treatment(info, lang)[:3])}</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(t("knew_it", lang), type="primary", use_container_width=True):
                st.session_state.flashcard_flipped = False
                add_xp(st.session_state.username, 5)
                st.rerun()
        with col2:
            if st.button(t("review_again", lang), use_container_width=True):
                st.session_state.flashcard_flipped = False
                st.rerun()
    else:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center; padding: 3rem;">
            <h3>{t('what_are_symptoms_of', lang)} {disease}?</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button(t("reveal_answer", lang), use_container_width=True):
            st.session_state.flashcard_flipped = True
            st.rerun()

elif page == "Lab Tests":
    st.markdown(f'<h2>{t("lab_tests_title", lang)} ({len(LAB_TESTS)} {t("tests_count", lang)})</h2>', unsafe_allow_html=True)
    
    search = st.text_input(t("search", lang))
    category = st.selectbox(t("category", lang), [t("all", lang)] + sorted(set(v["category"] for v in LAB_TESTS.values())))
    
    filtered = {k: v for k, v in LAB_TESTS.items() 
               if (not search or search.lower() in k.lower()) 
               and (category == t("all", lang) or v["category"] == category)}
    
    if filtered:
        import pandas as pd
        df_data = [{"Test": k, "Category": v["category"], t("normal_range", lang): v["normal"], t("description", lang): get_description(v, lang)} 
                  for k, v in filtered.items()]
        st.dataframe(pd.DataFrame(df_data), use_container_width=True, height=400)
    else:
        st.info(t("no_tests_found", lang))

elif page == "Pharmacology":
    st.markdown(f'<h2>{t("pharmacology_title", lang)} ({sum(len(d) for d in DRUG_DATABASE.values())} {t("drugs_count", lang)})</h2>', unsafe_allow_html=True)
    
    search = st.text_input(t("search", lang))
    
    for category, drugs in DRUG_DATABASE.items():
        cat_drugs = {k: v for k, v in drugs.items() if not search or search.lower() in k.lower()}
        if cat_drugs:
            with st.expander(f"📂 {category} ({len(cat_drugs)} {t('drugs_count', lang)})"):
                for drug, info in cat_drugs.items():
                    st.markdown(f"""
                    <div class="glass-card">
                        <h4>{drug}</h4>
                        <p><strong>{t('drug_class', lang)}:</strong> {info['class']} | <strong>{t('dose', lang)}:</strong> {info['dose']}</p>
                        <p><strong>{t('indications', lang)}:</strong> {get_indications(info, lang)}</p>
                        <p style="color: #ef4444;"><strong>{t('side_effects', lang)}:</strong> {get_side_effects(info, lang)}</p>
                    </div>
                    """, unsafe_allow_html=True)

elif page == "Drug Interactions":
    st.markdown(f'<h2>{t("drug_interactions_title", lang)}</h2>', unsafe_allow_html=True)
    
    all_drugs = [drug for drugs in DRUG_DATABASE.values() for drug in drugs]
    selected = st.multiselect(t("select_drugs", lang), all_drugs)
    
    if len(selected) >= 2:
        st.info(f"{len(selected)} {t('drugs_selected', lang)}")
    else:
        st.info(t("select_minimum", lang))

elif page == "Leaderboard":
    st.markdown(f'<h2>{t("leaderboard_title", lang)}</h2>', unsafe_allow_html=True)
    
    df = get_leaderboard_data()
    if not df.empty:
        for i, (_, row) in enumerate(df.iterrows()):
            medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"#{i+1}"
            st.markdown(f"""
            <div class="glass-card">
                <h3>{medal} {row['username']}</h3>
                <p>⭐ {row['xp_points']} {t('xp', lang)} | 📊 {row['quiz_score']} {t('quiz_score', lang)} | 🩺 {row['cases_solved']} {t('cases', lang)}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info(t("no_data", lang))

elif page == "Medical News":
    st.markdown(f'<h2>{t("medical_news", lang)}</h2>', unsafe_allow_html=True)
    
    news_items = [
        ("New Diabetes Treatment", "GLP-1/GIP dual agonist shows superior glycemic control", "NEJM"),
        ("AI in Radiology", "Machine learning improves cancer detection by 30%", "The Lancet"),
        ("mRNA Vaccines", "Beyond COVID - New applications in cancer therapy", "Nature Medicine"),
        ("Antibiotic Resistance", "WHO warns of critical antimicrobial resistance crisis", "WHO Bulletin"),
        ("Alzheimer's Breakthrough", "New monoclonal antibody slows cognitive decline", "JAMA")
    ]
    
    for title, summary, source in news_items:
        st.markdown(f"""
        <div class="glass-card">
            <h4>📰 {title}</h4>
            <p>{summary}</p>
            <p style="color: #888;">Source: {source}</p>
        </div>
        """, unsafe_allow_html=True)

elif page == "AI Assistant":
    st.markdown(f'<h2>{t("ai_assistant_title", lang)}</h2>', unsafe_allow_html=True)
    
    symptoms = st.text_area(t("enter_symptoms", lang), placeholder="e.g., fever, cough, fatigue")
    
    if st.button(t("analyze", lang), type="primary") and symptoms:
        symptom_list = [s.strip().lower() for s in symptoms.split(",")]
        results = []
        
        for disease, info in DISEASE_DATABASE.items():
            disease_symptoms_lower = [s.lower() for s in get_symptoms(info, lang)]
            matches = len(set(symptom_list) & set(disease_symptoms_lower))
            if matches > 0:
                results.append((disease, (matches / len(disease_symptoms_lower)) * 100, info["risk_level"]))
        
        results.sort(key=lambda x: x[1], reverse=True)
        
        for disease, match, risk in results[:5]:
            risk_color = {"Critical": "#ef4444", "High": "#f59e0b", "Moderate": "#06b6d4", "Low": "#10b981"}
            translated_risk = get_risk_level_translated(risk, lang)
            st.markdown(f"""
            <div class="glass-card">
                <h4>{disease}</h4>
                <p>{t('match', lang)}: {match:.0f}% | {t('risk', lang)}: <span style="color:{risk_color.get(risk, '#888')}">{translated_risk}</span></p>
            </div>
            """, unsafe_allow_html=True)

elif page == "Clinical Notes":
    st.markdown(f'<h2>{t("clinical_notes_title", lang)}</h2>', unsafe_allow_html=True)
    
    with st.form("add_note"):
        patient = st.text_input(t("patient_info", lang))
        note = st.text_area(t("clinical_note", lang))
        if st.form_submit_button(t("save_note", lang), type="primary"):
            conn = get_db_connection()
            conn.execute("INSERT INTO clinical_notes (username, patient_info, note) VALUES (?, ?, ?)",
                        (st.session_state.username, patient, note))
            conn.commit()
            st.success(f"✅ {t('note_saved', lang)}")
            st.rerun()
    
    conn = get_db_connection()
    notes = conn.execute("SELECT * FROM clinical_notes WHERE username = ? ORDER BY created_at DESC LIMIT 20",
                        (st.session_state.username,)).fetchall()
    
    for note in notes:
        st.markdown(f"""
        <div class="glass-card">
            <p><strong>{t('patient_info', lang)}:</strong> {note['patient_info']}</p>
            <p>{note['note']}</p>
            <p style="color: #888;">{note['created_at'][:10]}</p>
        </div>
        """, unsafe_allow_html=True)

elif page == "Achievements":
    st.markdown(f'<h2>{t("achievements_title", lang)}</h2>', unsafe_allow_html=True)
    
    achievements = [
        ("First Steps", "🩺", st.session_state.total_cases >= 1),
        ("Case Master", "🏆", st.session_state.total_cases >= 20),
        ("Quiz Beginner", "📝", st.session_state.quiz_score >= 10),
        ("Quiz Expert", "🎓", st.session_state.quiz_score >= 50),
        ("Streak Master", "🔥", st.session_state.streak >= 7),
        ("XP Hunter", "⭐", st.session_state.xp_points >= 100),
        ("XP Champion", "💎", st.session_state.xp_points >= 500),
        ("Diagnostician", "🔍", st.session_state.correct_diagnoses >= 5),
    ]
    
    cols = st.columns(3)
    for i, (name, icon, earned) in enumerate(achievements):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="glass-card" style="text-align: center; opacity: {1 if earned else 0.5};">
                <div style="font-size: 3rem;">{icon}</div>
                <h4>{name}</h4>
                <span class="badge {'badge-success' if earned else 'badge-warning'}">{t('earned', lang) if earned else t('locked', lang)}</span>
            </div>
            """, unsafe_allow_html=True)

# ================================
# FOOTER
# ================================
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; padding: 2rem; color: rgba(255,255,255,0.3);">
    <p>🩺 Dr.Danyal Medical Training Platform {t('version', lang)}</p>
    <p style="font-size: 0.8rem;">{len(DISEASE_DATABASE)} {t('diseases_count', lang)} | {sum(len(d) for d in DRUG_DATABASE.values())} {t('drugs_count', lang)} | {len(LAB_TESTS)} {t('tests_count', lang)} | {get_user_count()} {t('total_users', lang)}</p>
    <p style="font-size: 0.7rem;">© {datetime.now().year} {t('copyright', lang)}</p>
</div>
""", unsafe_allow_html=True)
