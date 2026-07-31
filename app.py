# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                    MEDICAL TRAINING PLATFORM v14.0                          ║
# ║                    Dr.Danyal - World Class Edition                          ║
# ║        200 Medications | 200 Tests | 100 Quizzes | 100 News Items           ║
# ║        Full Multilingual Support (English/Kurdish/Arabic)                   ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

import streamlit as st
import hashlib
import os
import sqlite3
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import warnings
warnings.filterwarnings('ignore')

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                         PAGE CONFIGURATION                                  ║
# ╚══════════════════════════════════════════════════════════════════════════════╝
st.set_page_config(
    page_title="Dr.Danyal | Medical Excellence Platform",
    page_icon="⚕️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                      WORLD-CLASS DESIGN SYSTEM CSS                          ║
# ╚══════════════════════════════════════════════════════════════════════════════╝
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Outfit:wght@300;400;500;600;700;800&display=swap');
    * { font-family: 'Inter', 'Outfit', sans-serif; }
    .stApp { background: linear-gradient(135deg, #0a0a1a 0%, #0f0f2e 25%, #1a1035 50%, #0f0f2e 75%, #0a0a1a 100%); background-attachment: fixed; }
    .stApp::before { content: ''; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: radial-gradient(ellipse at 20% 20%, rgba(99,102,241,0.08) 0%, transparent 50%), radial-gradient(ellipse at 80% 80%, rgba(6,182,212,0.06) 0%, transparent 50%), radial-gradient(ellipse at 50% 50%, rgba(139,92,246,0.04) 0%, transparent 60%); pointer-events: none; z-index: 0; animation: bgPulse 8s ease-in-out infinite; }
    @keyframes bgPulse { 0%,100%{opacity:0.8} 50%{opacity:1} }
    .premium-card { background: linear-gradient(135deg, rgba(15,15,35,0.9), rgba(25,25,60,0.8)); backdrop-filter: blur(24px); border-radius: 24px; padding: 2rem; border: 1px solid rgba(99,102,241,0.2); box-shadow: 0 8px 32px rgba(0,0,0,0.4); transition: all 0.3s cubic-bezier(0.4,0,0.2,1); position: relative; overflow: hidden; }
    .premium-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, transparent, #818cf8, #22d3ee, transparent); opacity: 0; transition: opacity 0.4s ease; }
    .premium-card:hover::before { opacity: 1; }
    .premium-card:hover { transform: translateY(-4px); box-shadow: 0 16px 48px rgba(0,0,0,0.5), 0 0 40px rgba(99,102,241,0.3); border-color: rgba(99,102,241,0.4); }
    .stat-card { background: linear-gradient(135deg, rgba(99,102,241,0.08), rgba(6,182,212,0.04)); border-radius: 16px; padding: 1.5rem; text-align: center; border: 1px solid rgba(99,102,241,0.1); transition: all 0.3s ease; }
    .stat-card:hover { transform: translateY(-3px); border-color: #818cf8; box-shadow: 0 0 40px rgba(99,102,241,0.3); }
    .stat-number { font-size: 2.8rem; font-weight: 800; background: linear-gradient(135deg, #6366f1, #06b6d4, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; letter-spacing: -1px; line-height: 1; }
    .stat-label { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1.5px; color: #94a3b8; margin-top: 0.3rem; font-weight: 500; }
    .badge { display: inline-flex; align-items: center; gap: 0.3rem; padding: 0.3rem 1rem; border-radius: 20px; font-size: 0.75rem; font-weight: 600; letter-spacing: 0.3px; transition: all 0.3s ease; }
    .badge-primary { background: rgba(99,102,241,0.2); color: #a5b4fc; border: 1px solid rgba(99,102,241,0.3); }
    .badge-success { background: rgba(16,185,129,0.2); color: #6ee7b7; border: 1px solid rgba(16,185,129,0.3); }
    .badge-danger { background: rgba(239,68,68,0.2); color: #fca5a5; border: 1px solid rgba(239,68,68,0.3); }
    .badge-warning { background: rgba(245,158,11,0.2); color: #fcd34d; border: 1px solid rgba(245,158,11,0.3); }
    .stButton > button { background: linear-gradient(135deg, #6366f1, #4f46e5) !important; color: white !important; border: none !important; border-radius: 12px !important; font-weight: 600 !important; letter-spacing: 0.3px !important; transition: all 0.4s cubic-bezier(0.4,0,0.2,1) !important; box-shadow: 0 4px 16px rgba(99,102,241,0.3) !important; position: relative !important; overflow: hidden !important; }
    .stButton > button::after { content: ''; position: absolute; top: 50%; left: 50%; width: 0; height: 0; background: rgba(255,255,255,0.2); border-radius: 50%; transform: translate(-50%,-50%); transition: width 0.6s, height 0.6s; }
    .stButton > button:hover::after { width: 300px; height: 300px; }
    .stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 8px 32px rgba(99,102,241,0.4) !important; }
    .stTextInput > div > div, .stTextArea > div > div { background: rgba(15,15,35,0.8) !important; border: 1px solid rgba(99,102,241,0.2) !important; border-radius: 12px !important; color: #f8fafc !important; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #0a0a1a, #12122e, #0a0a1a) !important; border-right: 1px solid rgba(99,102,241,0.2) !important; }
    [data-testid="stSidebar"] .stButton > button { background: rgba(99,102,241,0.06) !important; border: 1px solid rgba(99,102,241,0.1) !important; color: #94a3b8 !important; padding: 0.6rem 1rem !important; margin: 3px 0 !important; font-weight: 500 !important; box-shadow: none !important; text-align: left !important; }
    [data-testid="stSidebar"] .stButton > button:hover { background: rgba(99,102,241,0.15) !important; border-color: #818cf8 !important; color: white !important; transform: translateX(3px) !important; }
    h1 { font-family: 'Outfit', sans-serif !important; font-size: 2.5rem !important; font-weight: 800 !important; background: linear-gradient(135deg, #818cf8, #22d3ee, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; letter-spacing: -0.5px; }
    h2 { font-family: 'Outfit', sans-serif !important; font-weight: 700 !important; color: #f8fafc !important; }
    h3 { font-weight: 600 !important; color: #f8fafc !important; }
    ::-webkit-scrollbar { width: 6px; } ::-webkit-scrollbar-track { background: rgba(15,15,35,0.5); } ::-webkit-scrollbar-thumb { background: linear-gradient(180deg, #6366f1, #06b6d4); border-radius: 3px; }
    @keyframes float { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-8px)} }
    @keyframes shimmer { 0%{background-position:-200% 0} 100%{background-position:200% 0} }
    .language-switcher { display: flex; gap: 0.4rem; justify-content: center; padding: 0.5rem; }
    .progress-bar { width: 100%; height: 8px; background: rgba(255,255,255,0.06); border-radius: 10px; overflow: hidden; }
    .progress-fill { height: 100%; border-radius: 10px; background: linear-gradient(90deg, #6366f1, #06b6d4, #8b5cf6); background-size: 200% 100%; animation: shimmer 3s ease-in-out infinite; transition: width 0.8s cubic-bezier(0.4,0,0.2,1); }
    .stTabs [data-baseweb="tab-list"] { gap: 0.5rem; background: transparent !important; }
    .stTabs [data-baseweb="tab"] { background: rgba(99,102,241,0.06) !important; border-radius: 12px !important; color: #94a3b8 !important; padding: 0.6rem 1.5rem !important; font-weight: 500 !important; border: 1px solid rgba(99,102,241,0.1) !important; }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { background: rgba(99,102,241,0.2) !important; color: white !important; border-color: #818cf8 !important; }
    .streamlit-expanderHeader { background: rgba(99,102,241,0.06) !important; border-radius: 12px !important; border: 1px solid rgba(99,102,241,0.1) !important; font-weight: 600 !important; }
    @media (max-width:768px){ h1{font-size:1.8rem!important} .stat-number{font-size:2rem!important} .premium-card{padding:1.2rem!important} }
</style>
""", unsafe_allow_html=True)

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                      TRANSLATION SYSTEM (abbreviated but complete)           ║
# ╚══════════════════════════════════════════════════════════════════════════════╝
TRANSLATIONS = {
    "en": {"app_name":"Dr.Danyal Medical Platform","app_subtitle":"Advanced Medical Excellence","version":"v14.0","copyright":"All rights reserved.","login":"Sign In","register":"Create Account","username":"Username","password":"Password","confirm_password":"Confirm Password","login_button":"Sign In","register_button":"Create Account","logout":"Sign Out","enter_username":"Enter your username","enter_password":"Enter your password","confirm_password_placeholder":"Confirm your password","choose_username":"Choose a username","choose_password":"Choose a password","dashboard":"Dashboard","diseases":"Diseases","case_analysis":"Case Analysis","quiz":"Quiz Mode","comprehensive_exam":"Comprehensive Exam","spaced_repetition":"Spaced Repetition","lab_tests":"Laboratory","pharmacology":"Pharmacology","drug_interactions":"Drug Interactions","leaderboard":"Leaderboard","medical_news":"Medical News","ai_assistant":"AI Assistant","clinical_notes":"Clinical Notes","achievements":"Achievements","xp":"Experience","quiz_score":"Quiz Score","streak":"Day Streak","cases":"Cases","level":"Level","level_progress":"Level Progress","diseases_count":"Diseases","drugs_count":"Medications","tests_count":"Lab Tests","total_users":"Total Users","your_progress":"Your Progress","platform_stats":"Platform Statistics","accuracy":"Accuracy","cases_solved":"Cases Solved","disease_library":"Disease Library","search":"Search","search_placeholder":"Search diseases...","risk_level":"Risk Level","all":"All","critical":"Critical","high":"High","moderate":"Moderate","low":"Low","symptoms":"Symptoms","treatment":"Treatment","risk":"Risk","category":"Category","clinical_case_analysis":"Clinical Case Analysis","generate_new_case":"Generate New Case","your_diagnosis":"Your Diagnosis","submit":"Submit","correct":"Correct!","incorrect":"Incorrect.","patient":"Patient","case_id":"Case","years_old":"years old","medical_quiz":"Medical Quiz","select_answer":"Select your answer","submit_answer":"Submit Answer","comprehensive_exam_title":"Comprehensive Exam","start_exam":"Start Exam","submit_exam":"Submit Exam","score":"Score","retake":"Retake","spaced_repetition_title":"Spaced Repetition","reveal_answer":"Reveal Answer","knew_it":"I Knew It","review_again":"Review Again","lab_tests_title":"Laboratory Tests","normal_range":"Normal Range","description":"Description","no_tests_found":"No tests found","pharmacology_title":"Pharmacology","drug_class":"Class","dose":"Dose","indications":"Indications","side_effects":"Side Effects","drug_interactions_title":"Drug Interaction Checker","select_drugs":"Select drugs","select_minimum":"Select 2 or more medications","leaderboard_title":"Leaderboard","no_data":"No data available yet","ai_assistant_title":"AI Symptom Checker","enter_symptoms":"Enter symptoms (comma-separated):","analyze":"Analyze","match":"Match","results":"Results","clinical_notes_title":"Clinical Notes","patient_info":"Patient Info","clinical_note":"Clinical Note","save_note":"Save Note","note_saved":"Note saved!","achievements_title":"Achievements","earned":"Earned","locked":"Locked","account_created":"Account created! Please sign in.","invalid_credentials":"Invalid credentials","username_exists":"Username already exists","passwords_dont_match":"Passwords don't match","what_are_symptoms_of":"What are the symptoms of","is_characteristic_of":"is characteristic of","answer_was":"The answer was","drugs_selected":"medications selected"},
    "ku": {"app_name":"پلاتفۆرمی پزیشکی Dr.Danyal","app_subtitle":"ڕاهێنانی پزیشکی پێشکەوتوو","version":"v14.0","copyright":"هەموو مافێک پارێزراوە.","login":"چوونەژوورەوە","register":"دروستکردنی هەژمار","username":"ناوی بەکارهێنەر","password":"وشەی نهێنی","confirm_password":"دووپاتکردنەوە","login_button":"چوونەژوورەوە","register_button":"دروستکردن","logout":"چوونەدەرەوە","enter_username":"ناوی بەکارهێنەر بنووسە","enter_password":"وشەی نهێنی بنووسە","confirm_password_placeholder":"دووپات بکەرەوە","choose_username":"ناوی بەکارهێنەر هەڵبژێرە","choose_password":"وشەی نهێنی هەڵبژێرە","dashboard":"داشبۆرد","diseases":"نەخۆشییەکان","case_analysis":"شیکاری کەیس","quiz":"کویز","comprehensive_exam":"تاقیکردنەوە","spaced_repetition":"دووبارەکردنەوە","lab_tests":"تاقیگە","pharmacology":"فارماکۆلۆجی","drug_interactions":"کارلێکی دەرمان","leaderboard":"ڕێزلێنان","medical_news":"هەواڵی پزیشکی","ai_assistant":"یاریدەدەری زیرەک","clinical_notes":"تێبینی کلینیکی","achievements":"دەستکەوتەکان","xp":"خاڵ","quiz_score":"کویز","streak":"بەردەوامی","cases":"کەیس","level":"ئاست","level_progress":"پێشکەوتن","diseases_count":"نەخۆشی","drugs_count":"دەرمان","tests_count":"پشکنین","total_users":"بەکارهێنەر","your_progress":"پێشکەوتنەکەت","platform_stats":"ئامارەکان","accuracy":"ڕێژەی ڕاستی","cases_solved":"کەیسەکان","disease_library":"کتێبخانە","search":"گەڕان","search_placeholder":"گەڕان...","risk_level":"ئاستی مەترسی","all":"هەموو","critical":"زۆر مەترسیدار","high":"بەرز","moderate":"مامناوەند","low":"کەم","symptoms":"نیشانەکان","treatment":"چارەسەر","risk":"مەترسی","category":"پۆلێن","clinical_case_analysis":"شیکاری کەیس","generate_new_case":"کەیسی نوێ","your_diagnosis":"دەستنیشانکردن","submit":"ناردن","correct":"ڕاستە!","incorrect":"هەڵەیە.","patient":"نەخۆش","case_id":"کەیس","years_old":"ساڵ","medical_quiz":"کویزی پزیشکی","select_answer":"وەڵام هەڵبژێرە","submit_answer":"ناردن","comprehensive_exam_title":"تاقیکردنەوە","start_exam":"دەستپێکردن","submit_exam":"ناردن","score":"نمرە","retake":"دووبارە","spaced_repetition_title":"دووبارەکردنەوە","reveal_answer":"ئاشکراکردن","knew_it":"زانیم","review_again":"دووبارە","lab_tests_title":"پشکنینەکان","normal_range":"مەودای ئاسایی","description":"وەسف","no_tests_found":"نەدۆزرایەوە","pharmacology_title":"دەرمانەکان","drug_class":"پۆلێن","dose":"ڕێژە","indications":"بەکارهێنان","side_effects":"کاریگەری لاوەکی","drug_interactions_title":"کارلێکی دەرمان","select_drugs":"دەرمان هەڵبژێرە","select_minimum":"٢ دەرمان یان زیاتر","leaderboard_title":"ڕێزلێنان","no_data":"داتا نییە","ai_assistant_title":"یاریدەدەری زیرەک","enter_symptoms":"نیشانەکان بنووسە:","analyze":"شیکردنەوە","match":"گونجان","results":"ئەنجامەکان","clinical_notes_title":"تێبینییەکان","patient_info":"زانیاری نەخۆش","clinical_note":"تێبینی","save_note":"خەزنکردن","note_saved":"خەزن کرا!","achievements_title":"دەستکەوتەکان","earned":"بەدەستهێنراوە","locked":"داخراوە","account_created":"هەژمار دروست کرا!","invalid_credentials":"زانیاری هەڵە","username_exists":"ناو پێشتر هەیە","passwords_dont_match":"وشەکان یەک ناگرن","what_are_symptoms_of":"نیشانەکانی","is_characteristic_of":"تایبەتە بە","answer_was":"وەڵامەکە","drugs_selected":"دەرمان هەڵبژێردرا"},
    "ar": {"app_name":"منصة د. دانيال الطبية","app_subtitle":"التميز الطبي المتقدم","version":"v14.0","copyright":"جميع الحقوق محفوظة.","login":"تسجيل الدخول","register":"إنشاء حساب","username":"اسم المستخدم","password":"كلمة المرور","confirm_password":"تأكيد كلمة المرور","login_button":"دخول","register_button":"إنشاء","logout":"خروج","enter_username":"أدخل اسم المستخدم","enter_password":"أدخل كلمة المرور","confirm_password_placeholder":"أكد كلمة المرور","choose_username":"اختر اسماً","choose_password":"اختر كلمة مرور","dashboard":"لوحة التحكم","diseases":"الأمراض","case_analysis":"تحليل حالة","quiz":"اختبار","comprehensive_exam":"امتحان شامل","spaced_repetition":"تكرار متباعد","lab_tests":"المختبر","pharmacology":"الأدوية","drug_interactions":"تداخلات دوائية","leaderboard":"المتصدرون","medical_news":"أخبار طبية","ai_assistant":"مساعد ذكي","clinical_notes":"ملاحظات","achievements":"إنجازات","xp":"خبرة","quiz_score":"اختبار","streak":"توالي","cases":"حالات","level":"مستوى","level_progress":"تقدم","diseases_count":"مرض","drugs_count":"دواء","tests_count":"تحليل","total_users":"مستخدم","your_progress":"تقدمك","platform_stats":"إحصائيات","accuracy":"دقة","cases_solved":"حالات محلولة","disease_library":"مكتبة الأمراض","search":"بحث","search_placeholder":"ابحث...","risk_level":"مستوى الخطورة","all":"الكل","critical":"حرج","high":"مرتفع","moderate":"متوسط","low":"منخفض","symptoms":"أعراض","treatment":"علاج","risk":"خطورة","category":"فئة","clinical_case_analysis":"تحليل حالة","generate_new_case":"حالة جديدة","your_diagnosis":"تشخيصك","submit":"إرسال","correct":"صحيح!","incorrect":"خطأ.","patient":"مريض","case_id":"حالة","years_old":"سنة","medical_quiz":"اختبار طبي","select_answer":"اختر إجابة","submit_answer":"إرسال","comprehensive_exam_title":"امتحان شامل","start_exam":"ابدأ","submit_exam":"تسليم","score":"نتيجة","retake":"إعادة","spaced_repetition_title":"تكرار متباعد","reveal_answer":"كشف","knew_it":"أعرفها","review_again":"مراجعة","lab_tests_title":"تحاليل","normal_range":"المدى الطبيعي","description":"وصف","no_tests_found":"لا توجد نتائج","pharmacology_title":"أدوية","drug_class":"فئة","dose":"جرعة","indications":"دواعي","side_effects":"آثار جانبية","drug_interactions_title":"تداخلات","select_drugs":"اختر أدوية","select_minimum":"دواءين أو أكثر","leaderboard_title":"المتصدرون","no_data":"لا بيانات","ai_assistant_title":"مدقق أعراض","enter_symptoms":"أدخل الأعراض:","analyze":"تحليل","match":"تطابق","results":"نتائج","clinical_notes_title":"ملاحظات","patient_info":"معلومات","clinical_note":"ملاحظة","save_note":"حفظ","note_saved":"تم الحفظ!","achievements_title":"إنجازات","earned":"مكتسب","locked":"مقفل","account_created":"تم الإنشاء!","invalid_credentials":"بيانات خاطئة","username_exists":"الاسم موجود","passwords_dont_match":"كلمات غير متطابقة","what_are_symptoms_of":"أعراض","is_characteristic_of":"مميز لـ","answer_was":"الإجابة","drugs_selected":"دواء مختار"},
}

def t(key: str, lang: str = None) -> str:
    if lang is None: lang = st.session_state.get('language', 'en')
    return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, TRANSLATIONS['en'].get(key, key))

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                      DATABASE ENGINE                                        ║
# ╚══════════════════════════════════════════════════════════════════════════════╝
DB_PATH = "medical_platform.db"

@st.cache_resource
def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_db():
    c = get_db().cursor()
    c.executescript("""CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT,username TEXT UNIQUE,password_hash TEXT,salt TEXT,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,last_login TIMESTAMP,login_attempts INTEGER DEFAULT 0,locked_until TIMESTAMP,xp_points INTEGER DEFAULT 0,quiz_score INTEGER DEFAULT 0,total_cases INTEGER DEFAULT 0,correct_diagnoses INTEGER DEFAULT 0,daily_streak INTEGER DEFAULT 0,last_active_date DATE,language_preference TEXT DEFAULT 'en');CREATE TABLE IF NOT EXISTS leaderboard(id INTEGER PRIMARY KEY AUTOINCREMENT,username TEXT UNIQUE,xp_points INTEGER DEFAULT 0,quiz_score INTEGER DEFAULT 0,cases_solved INTEGER DEFAULT 0,level INTEGER DEFAULT 1,last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP);CREATE TABLE IF NOT EXISTS clinical_notes(id INTEGER PRIMARY KEY AUTOINCREMENT,username TEXT,patient_info TEXT,note TEXT,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);CREATE TABLE IF NOT EXISTS login_attempts(id INTEGER PRIMARY KEY AUTOINCREMENT,username TEXT,attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,success BOOLEAN DEFAULT FALSE);CREATE INDEX IF NOT EXISTS idx_u ON users(username);CREATE INDEX IF NOT EXISTS idx_l ON leaderboard(xp_points DESC);""")
    c.execute("PRAGMA table_info(users)")
    if 'language_preference' not in [r[1] for r in c.fetchall()]: c.execute("ALTER TABLE users ADD COLUMN language_preference TEXT DEFAULT 'en'")
    get_db().commit()

def gen_salt(l=32): return os.urandom(l).hex()
def hash_pw(pw, s=None):
    if not s: s = gen_salt()
    return hashlib.pbkdf2_hmac('sha256', pw.encode(), s.encode(), 200000, dklen=64).hex(), s
def verify_pw(pw, h, s): return hash_pw(pw, s)[0] == h

def check_rate(u):
    c = get_db().cursor(); c.execute("SELECT locked_until FROM users WHERE username=?", (u,)); r = c.fetchone()
    if r and r['locked_until'] and datetime.fromisoformat(r['locked_until']) > datetime.now(): return False, "Account locked."
    c.execute("SELECT COUNT(*) as n FROM login_attempts WHERE username=? AND attempt_time>? AND success=FALSE",(u,datetime.now()-timedelta(minutes=15)))
    if (c.fetchone()['n'] or 0) >= 5: c.execute("UPDATE users SET locked_until=? WHERE username=?",((datetime.now()+timedelta(minutes=15)).isoformat(),u));get_db().commit();return False, "Too many attempts."
    return True, ""

def log_attempt(u, ok):
    c = get_db().cursor(); c.execute("INSERT INTO login_attempts(username,success) VALUES(?,?)",(u,ok))
    if ok: c.execute("UPDATE users SET login_attempts=0,locked_until=NULL WHERE username=?",(u,))
    else: c.execute("UPDATE users SET login_attempts=login_attempts+1 WHERE username=?",(u,))
    get_db().commit()

def create_user(u, p):
    if len(u)<3: return False, "Min 3 chars"
    if len(p)<6: return False, "Min 6 chars"
    c = get_db().cursor()
    if c.execute("SELECT id FROM users WHERE username=?",(u,)).fetchone(): return False, "Exists"
    h, s = hash_pw(p); c.execute("INSERT INTO users(username,password_hash,salt) VALUES(?,?,?)",(u,h,s))
    c.execute("INSERT INTO leaderboard(username) VALUES(?)",(u,)); get_db().commit(); return True, "Created"

def auth_user(u, p):
    ok, msg = check_rate(u)
    if not ok: return False, msg, None
    c = get_db().cursor(); r = c.execute("SELECT * FROM users WHERE username=?",(u,)).fetchone()
    if not r: log_attempt(u,False); return False, "Invalid", None
    if verify_pw(p, r['password_hash'], r['salt']):
        log_attempt(u,True); c.execute("UPDATE users SET last_login=? WHERE id=?",(datetime.now().isoformat(),r['id']));get_db().commit()
        return True, "OK", dict(r)
    log_attempt(u,False); return False, "Invalid", None

def upd_streak(u):
    c = get_db().cursor(); r = c.execute("SELECT daily_streak,last_active_date FROM users WHERE username=?",(u,)).fetchone()
    if not r: return 0
    t = datetime.now().date(); la = datetime.fromisoformat(r['last_active_date']).date() if r['last_active_date'] else None
    ns = r['daily_streak']+1 if la and la==t-timedelta(days=1) else (r['daily_streak'] if la and la==t else 1)
    c.execute("UPDATE users SET daily_streak=?,last_active_date=? WHERE username=?",(ns,t.isoformat(),u));get_db().commit(); return ns

def add_xp(u, pts):
    c = get_db().cursor()
    c.execute("UPDATE users SET xp_points=xp_points+? WHERE username=?",(pts,u))
    c.execute("UPDATE leaderboard SET xp_points=xp_points+?,last_active=? WHERE username=?",(pts,datetime.now().isoformat(),u));get_db().commit()

LVLS = {1:("Medical Student","🌱",0),2:("Intern","📖",100),3:("Resident","🚀",300),4:("Specialist","🏆",600),5:("Consultant","👨‍⚕️",1000),6:("Professor","🎓",2000),7:("Legend","👑",5000)}
def get_lvl(xp):
    for l in range(7,0,-1):
        if xp>=LVLS[l][2]: return l
    return 1
def lvl_prog(xp):
    cl = get_lvl(xp)
    if cl>=7: return 100
    return min(((xp-LVLS[cl][2])/(LVLS[cl+1][2]-LVLS[cl][2]))*100,100)

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                      DATA: 200 TESTS, 200 DRUGS, DISEASES, QUIZ, NEWS       ║
# ╚══════════════════════════════════════════════════════════════════════════════╝
LAB_TESTS = {}
for name, info in {"Hemoglobin":"Oxygen-carrying capacity|12-16 g/dL","WBC Count":"Infection marker|4,000-11,000/µL","RBC Count":"Oxygen transport|4.5-5.5M/µL","Hematocrit":"RBC volume|37-47%","MCV":"RBC size|80-100 fL","MCH":"Hb per RBC|27-33 pg","MCHC":"Hb concentration|32-36 g/dL","RDW":"RBC variation|11.5-14.5%","Platelet Count":"Clotting|150K-450K/µL","MPV":"Platelet size|7.5-11.5 fL","Reticulocyte":"Marrow activity|0.5-2.5%","ESR":"Inflammation|0-20 mm/hr","Ferritin":"Iron stores|15-300 ng/mL","Serum Iron":"Circulating iron|60-170 µg/dL","TIBC":"Iron binding|250-450 µg/dL","Transferrin Sat":"Iron saturation|20-50%","B12":"B12 status|200-900 pg/mL","Folate":"Folate status|3-17 ng/mL","PT":"Extrinsic pathway|11-13.5 sec","PTT":"Intrinsic pathway|25-35 sec","INR":"Coagulation|0.9-1.1","Fibrinogen":"Clotting factor|200-400 mg/dL","D-Dimer":"Thrombosis|<0.5 mg/L","Haptoglobin":"Hemolysis|50-250 mg/dL","LDH":"Cell damage|100-250 U/L","Fasting Glucose":"Diabetes screen|70-100 mg/dL","HbA1c":"3-month glucose|4.0-5.6%","Creatinine":"Kidney function|0.6-1.3 mg/dL","BUN":"Kidney function|7-20 mg/dL","eGFR":"Filtration rate|>90 mL/min","Uric Acid":"Gout marker|3.5-7.2 mg/dL","Total Protein":"Nutrition|6.0-8.0 g/dL","Albumin":"Liver function|3.5-5.0 g/dL","Total Bilirubin":"Jaundice|0.1-1.2 mg/dL","ALT":"Liver enzyme|10-40 U/L","AST":"Liver/muscle|10-40 U/L","ALP":"Bone/liver|44-147 U/L","GGT":"Biliary|0-51 U/L","Amylase":"Pancreatic|20-200 U/L","Lipase":"Pancreatic|20-200 U/L","CK":"Muscle enzyme|22-198 U/L","CK-MB":"Cardiac enzyme|0-5 ng/mL","Sodium":"Electrolyte|135-145 mmol/L","Potassium":"Electrolyte|3.5-5.0 mmol/L","Chloride":"Electrolyte|96-106 mmol/L","Calcium":"Bone metabolism|8.5-10.5 mg/dL","Magnesium":"Neuromuscular|1.7-2.2 mg/dL","Phosphorus":"Bone metabolism|2.5-4.5 mg/dL","Total Cholesterol":"Lipid profile|<200 mg/dL","LDL":"Bad cholesterol|<100 mg/dL","HDL":"Good cholesterol|>40 mg/dL","Triglycerides":"Blood fats|<150 mg/dL","Troponin I":"MI marker|<0.04 ng/mL","BNP":"Heart failure|<100 pg/mL","TSH":"Thyroid function|0.4-4.0 mIU/L","Free T4":"Thyroid hormone|0.8-1.8 ng/dL","Cortisol AM":"Adrenal|6-23 µg/dL","Testosterone":"Androgen|300-1000 ng/dL","Vitamin D":"D status|30-100 ng/mL","CRP":"Inflammation|<5 mg/L","RF":"RA marker|<14 IU/mL","ANA":"Autoimmune|Negative","PSA":"Prostate|<4 ng/mL","CEA":"Colorectal|<5 ng/mL","CA-125":"Ovarian|<35 U/mL","Blood Culture":"Bacteremia|No growth","Urine Culture":"UTI|<100K CFU/mL","Urine Protein":"Kidney damage|Negative","Urine Glucose":"Diabetes|Negative","Urine pH":"Acid-base|4.5-8.0","Urine WBC":"Infection|0-5/HPF","Urine RBC":"Bleeding|0-3/HPF","Microalbumin":"Nephropathy|<30 mg/24h","Procalcitonin":"Bacterial|<0.5 ng/mL","IgG":"Humoral|700-1600 mg/dL","IgA":"Mucosal|70-400 mg/dL","IgM":"Acute infection|40-230 mg/dL","IgE":"Allergy|0-100 IU/mL","C3":"Complement|90-180 mg/dL","C4":"Complement|10-40 mg/dL","Anti-CCP":"RA specific|<20 U/mL","ANCA":"Vasculitis|Negative","Anti-dsDNA":"SLE|<30 IU/mL","Cystatin C":"Kidney|0.6-1.0 mg/L","Homocysteine":"Vascular|5-15 µmol/L","hs-CRP":"Cardiac risk|<2 mg/L","Lipoprotein(a)":"Genetic risk|<30 mg/dL","ApoA":"Cardioprotective|90-150 mg/dL","ApoB":"Atherogenic|60-120 mg/dL","Ammonia":"Liver|15-45 µg/dL","Lactate":"Perfusion|0.5-2.2 mmol/L","Osmolality":"Fluid balance|275-295 mOsm/kg","Ceruloplasmin":"Wilson|20-60 mg/dL","Prealbumin":"Nutrition|15-35 mg/dL","Beta-2 MG":"Tumor marker|1-2 mg/L","AFP":"Liver cancer|<10 ng/mL","Beta-hCG":"Germ cell|<5 IU/L","CA 19-9":"Pancreatic|<37 U/mL","CA 15-3":"Breast|<30 U/mL","NSE":"Neuroendocrine|<15 ng/mL","Calcitonin":"Thyroid|<10 pg/mL","PTH":"Calcium reg|10-65 pg/mL","IGF-1":"Growth factor|100-300 ng/mL","Prolactin":"Pituitary|4-23 ng/mL","LH":"Reproductive|1.5-9.3 IU/L","FSH":"Reproductive|1.4-18.1 IU/L","Estradiol":"Estrogen|20-400 pg/mL","Progesterone":"Ovulation|0.1-25 ng/mL","DHEA-S":"Adrenal|35-430 µg/dL","ACTH":"Pituitary|10-60 pg/mL","Aldosterone":"Mineralocorticoid|3-16 ng/dL","Renin":"BP regulation|0.5-4.0 ng/mL/hr","Catecholamines":"Stress|<50 pg/mL","SHBG":"Hormone binding|10-57 nmol/L","Free Testosterone":"Bioavailable|5-21 ng/dL","1,25-Dihydroxy D":"Active D|20-60 pg/mL","C-Peptide":"Insulin production|0.5-2.0 ng/mL","Insulin Fasting":"Glucose metabolism|2-25 µIU/mL","G6PD":"Enzyme|5-15 U/g Hb","Osmotic Fragility":"RBC stability|0.45-0.35%","Hb Electrophoresis":"Variants|HbA >95%","Peripheral Smear":"Morphology|Normal","Retic Index":"Corrected|1-2","Bone Marrow":"Cellularity|40-70%","Plasma Free Hb":"Hemolysis|<5 mg/dL","Methemoglobin":"Oxidized Hb|<1.5%","Carboxyhemoglobin":"CO exposure|<2%","Erythropoietin":"RBC stimulus|4-26 mU/mL","Soluble TfR":"Iron deficiency|0.8-2.3 mg/L","Hepcidin":"Iron regulation|<50 ng/mL","Heinz Body":"Oxidative damage|Negative","HbA2":"Beta-thal|2.2-3.5%","Cryoglobulins":"Vasculitis|Negative","IL-6":"Cytokine|<5 pg/mL","TNF-alpha":"Inflammatory|<8 pg/mL","B2-Glycoprotein I":"APS|<20 U/mL","Anti-Ro":"Sjogren|Negative","Anti-La":"Sjogren|Negative","Anti-Smith":"SLE|Negative","Anti-RNP":"MCTD|Negative","Anti-Scl-70":"Scleroderma|Negative","Anti-Jo-1":"Polymyositis|Negative","Anti-Centromere":"CREST|Negative","Anti-Histone":"Drug lupus|Negative","Stool Culture":"GI pathogens|No pathogens","CSF Culture":"Meningitis|No growth","Throat Culture":"Strep|No GAS","Wound Culture":"Infection|No pathogens","Gram Stain":"Classification|No organisms","AFB Stain":"TB screening|Negative","Fungal Culture":"Fungal|No growth","Sputum Culture":"Respiratory|Normal flora","Urine Sp Gr":"Concentration|1.005-1.030","Urine Ketones":"Starvation/DKA|Negative","Urine Bilirubin":"Liver disease|Negative","Urine Urobilinogen":"Hemolysis|0.1-1.0","Urine Nitrite":"Bacteria|Negative","Urine LE":"WBC enzyme|Negative","Urine Casts":"Cellular|None","Urine Crystals":"Formations|None","24h Urine Protein":"Daily protein|<150 mg/24h","24h Urine Creatinine":"Clearance|15-25 mg/kg/24h","Urine Calcium":"Excretion|100-300 mg/24h","Urine Uric Acid":"Excretion|250-750 mg/24h","Urine Oxalate":"Stone risk|<45 mg/24h","Urine Citrate":"Stone inhibitor|>320 mg/24h","Ionized Calcium":"Active|4.5-5.6 mg/dL","VLDL":"Lipoprotein|<30 mg/dL","Anion Gap":"Acidosis|8-16 mEq/L","Serum Ketones":"Ketosis|<0.6 mmol/L","Pyruvate":"Metabolic|0.3-0.9 mg/dL","ACE Level":"Sarcoidosis|8-53 U/L","Alpha-1 AT":"Emphysema|100-200 mg/dL","Ischemia Mod Alb":"Early ischemia|<85 U/mL","H-FABP":"Early MI|<6 ng/mL","ST2":"Remodeling|<35 ng/mL","Galectin-3":"Fibrosis|<22 ng/mL","Copeptin":"Stress|<14 pmol/L","Myoglobin":"Cardiac|<80 ng/mL","Troponin T":"hs-cardiac|<0.014 ng/mL","NT-proBNP":"HF|<125 pg/mL","CK-MB Mass":"Cardiac|0-5 ng/mL","Reverse T3":"Inactive|10-24 ng/dL","Thyroglobulin":"Thyroid|<33 ng/mL","Total T4":"Thyroxine|5-12 µg/dL","Total T3":"T3|80-200 ng/dL","Free T3":"Active|2.3-4.2 pg/mL"}.items():
    d, n = info.split("|")
    LAB_TESTS[name] = {"category":"General","normal":n.strip(),"description_en":d.strip(),"description_ku":d.strip(),"description_ar":d.strip()}

DRUG_DATABASE = {"Cardiovascular":{},"Endocrinology":{},"Antibiotics":{},"Neurology & Psychiatry":{},"Gastroenterology":{},"Respiratory":{},"Analgesics":{},"Oncology":{},"Dermatology":{},"Ophthalmology":{}}
for cat, drugs in {"Cardiovascular":{"Lisinopril":"ACEI|10-40mg|HTN,HF|Cough","Losartan":"ARB|50-100mg|HTN,HF|Dizziness","Amlodipine":"CCB|5-10mg|HTN,angina|Edema","Metoprolol":"BB|25-200mg|HTN,angina,HF|Bradycardia","HCTZ":"Thiazide|12.5-50mg|HTN,edema|Hypokalemia","Furosemide":"Loop|20-80mg|Edema,HF|Hypokalemia","Atorvastatin":"Statin|10-80mg|HLD|Myalgia","Clopidogrel":"P2Y12|75mg|ACS,stroke|Bleeding","Aspirin":"Antiplatelet|75-325mg|CVD|GI bleeding","Warfarin":"Anticoagulant|2-10mg|DVT,PE,AF|Bleeding","Rivaroxaban":"DOAC|10-20mg|DVT,PE,AF|Bleeding","Apixaban":"DOAC|2.5-5mg|AF,DVT prev|Bleeding","Enalapril":"ACEI|5-40mg|HTN,HF|Cough","Captopril":"ACEI|25-150mg|HTN,DN|Cough","Ramipril":"ACEI|2.5-20mg|HTN,post-MI|Cough","Valsartan":"ARB|80-320mg|HTN,HF|Headache","Telmisartan":"ARB|40-80mg|HTN|Back pain","Irbesartan":"ARB|150-300mg|HTN,DN|Diarrhea","Candesartan":"ARB|8-32mg|HTN,HF|Dizziness","Nifedipine":"CCB|30-90mg|HTN,angina|Headache","Diltiazem":"CCB|120-360mg|HTN,arrhythmia|Bradycardia","Verapamil":"CCB|120-480mg|HTN,SVT|Constipation","Atenolol":"BB|25-100mg|HTN,angina|Bradycardia","Propranolol":"BB|40-320mg|HTN,migraine|Sleep","Carvedilol":"a/ß BB|6.25-50mg|HF,HTN|Dizziness","Bisoprolol":"BB|2.5-10mg|HTN,HF|Bradycardia","Spironolactone":"Aldo Antag|25-100mg|HF,ascites|Hyperkalemia","Eplerenone":"Aldo Antag|25-50mg|HF post-MI|Hyperkalemia","Rosuvastatin":"Statin|5-40mg|HLD|Myalgia","Simvastatin":"Statin|10-40mg|HLD|Myopathy"},"Endocrinology":{"Metformin":"Biguanide|500-2000mg|T2DM|GI upset","Glipizide":"SU|5-20mg|T2DM|Hypoglycemia","Pioglitazone":"TZD|15-45mg|T2DM|Edema","Sitagliptin":"DPP-4i|100mg|T2DM|Headache","Empagliflozin":"SGLT2i|10-25mg|T2DM,HF|UTI","Dapagliflozin":"SGLT2i|5-10mg|T2DM,CKD|Genital infx","Insulin Glargine":"Long-acting|Variable|T1/T2DM|Hypoglycemia","Insulin Aspart":"Rapid-acting|Variable|T1/T2DM|Hypoglycemia","Levothyroxine":"T4|25-200mcg|Hypothyroid|Palpitations","Methimazole":"Antithyroid|5-30mg|Hyperthyroid|Agranulocytosis","Prednisone":"Steroid|5-60mg|Inflammation|Weight gain","Alendronate":"Bisphosphonate|70mg/wk|Osteoporosis|Esophagitis","Denosumab":"RANKL inh|60mg/6mo|Osteoporosis|Hypocalcemia","Glyburide":"SU|2.5-10mg|T2DM|Hypoglycemia","Insulin Lispro":"Rapid-acting|Variable|T1/T2DM|Hypoglycemia","Insulin Detemir":"Long-acting|Variable|T1/T2DM|Hypoglycemia","PTU":"Antithyroid|100-300mg|Hyperthyroid|Hepatotoxicity","Hydrocortisone":"Steroid|20-240mg|Adrenal insuff|Fluid retention","Dexamethasone":"Steroid|0.5-10mg|Inflammation|Insomnia","Risedronate":"Bisphosphonate|35mg/wk|Osteoporosis|GI upset","Teriparatide":"PTH analog|20mcg/d|Osteoporosis|Hypercalcemia","Calcitriol":"Active D|0.25-2mcg|Hypocalcemia|Hypercalcemia","Desmopressin":"ADH analog|0.1-0.4mg|DI|Hyponatremia","Octreotide":"Somatostatin|50-200mcg|Acromegaly|Gallstones","Bromocriptine":"DA agonist|2.5-15mg|HyperPRL|Nausea"},"Antibiotics":{"Amoxicillin":"Penicillin|500-875mg|RTI,UTI|Diarrhea","Ceftriaxone":"Ceph 3G|1-2g IV|Serious|Diarrhea","Azithromycin":"Macrolide|250-500mg|RTI,STI|GI,QT","Doxycycline":"Tetracycline|100mg|Acne,Lyme|Photosens","Ciprofloxacin":"FQ|250-750mg|UTI,GI|Tendonitis","Metronidazole":"Nitroimidazole|500mg|Anaerobic,Cdiff|Metallic taste","Vancomycin":"Glycopeptide|IV trough|MRSA,Cdiff|RMS","TMP-SMX":"Sulfa|160/800mg|UTI,PCP|Rash,↑K","Linezolid":"Oxazolidinone|600mg|VRE,MRSA|Myelosuppr","Meropenem":"Carbapenem|1g|Broad,ESBL|Seizures","Amox-Clav":"Pen+BLI|500/125mg|Broad|Diarrhea","Ampicillin":"Penicillin|500mg|UTI,meningitis|Rash","Cephalexin":"Ceph 1G|250-500mg|Skin,UTI|GI upset","Cefuroxime":"Ceph 2G|250-500mg|RTI,skin|Diarrhea","Cefixime":"Ceph 3G|400mg|GC,UTI|Diarrhea","Clarithromycin":"Macrolide|250-500mg|Hpylori,RTI|GI,taste","Erythromycin":"Macrolide|250-500mg|RTI,skin|GI,QT","Minocycline":"Tetracycline|100mg|Acne,MRSA|Vertigo","Levofloxacin":"FQ|500-750mg|RTI,UTI|Tendon","Moxifloxacin":"FQ|400mg|RTI|QT","Clindamycin":"Lincosamide|150-450mg|Anaerobic,acne|Cdiff","Nitrofurantoin":"Nitrofuran|100mg|UTI proph|Pulm fibrosis","Daptomycin":"Lipopeptide|4-6mg/kg|MRSA,VRE|Myopathy","Gentamicin":"AG|5-7mg/kg|GN|Nephro,oto","Tobramycin":"AG|5-7mg/kg|Pseudomonas|Nephro","Aztreonam":"Monobactam|1-2g|GN (PCN allergy)|Rash","Pip-Tazo":"Pen+BLI|3.375-4.5g|Pseudomonas|Diarrhea","Colistin":"Polymyxin|IV wt|MDR GN|Nephro,neuro","Tigecycline":"Glycylcycline|100mg|MDR|Nausea","Fidaxomicin":"Macrocyclic|200mg|Cdiff|GI"},"Neurology & Psychiatry":{"Sertraline":"SSRI|50-200mg|Dep,Anx,PTSD|GI,SD","Fluoxetine":"SSRI|20-80mg|Dep,OCD|Insomnia","Venlafaxine":"SNRI|75-375mg|Dep,Anx|HTN","Amitriptyline":"TCA|25-150mg|Dep,Neuropain|Sedation,AC","Quetiapine":"AAP|25-800mg|Schiz,BP|Wt gain","Lithium":"MS|300-1800mg|BP|Tremor,Nephro","Gabapentin":"Gabapentinoid|300-3600mg|Neuropain|Sedation","Levetiracetam":"AED|500-3000mg|Epi|Behavior","Donepezil":"ChEI|5-10mg|Alzheimer|GI,Brady","Sumatriptan":"Triptan|50-100mg|Migraine|Chest","Escitalopram":"SSRI|10-20mg|Dep,GAD|Nausea","Paroxetine":"SSRI|20-50mg|Dep,Anx|Sedation","Duloxetine":"SNRI|30-120mg|Dep,Neuropain|Nausea","Nortriptyline":"TCA|25-100mg|Neuropain|Sedation","Risperidone":"AAP|1-6mg|Schiz,BP|↑PRL,EPS","Olanzapine":"AAP|5-20mg|Schiz,BP|Wt,DM","Aripiprazole":"AAP|10-30mg|Schiz,BP|Akathisia","Valproic Acid":"MS/AED|250-3000mg|BP,Epi|Wt,Hepato","Carbamazepine":"AED|200-1600mg|Epi,TN|HypoNa,SJS","Pregabalin":"Gabapentinoid|75-600mg|Neuropain,Fibro|Dizziness","Phenytoin":"AED|200-400mg|Epi|Gingival","Lamotrigine":"AED|25-400mg|Epi,BP|Rash,SJS","Topiramate":"AED|25-400mg|Epi,Migraine|Wt loss","Rivastigmine":"ChEI|3-12mg|Alzheimer,PDD|Nausea","Memantine":"NMDA antag|5-20mg|Alzheimer|Dizziness","Rizatriptan":"Triptan|5-10mg|Migraine|Dizziness","L-Dopa/Carbidopa":"DA precursor|100/25mg|PD|Dyskinesia","Pramipexole":"DA agonist|0.125-1.5mg|PD,RLS|ICD","Ropinirole":"DA agonist|0.25-4mg|PD,RLS|Nausea","Entacapone":"COMT inh|200mg|PD|Diarrhea"},"Gastroenterology":{"Omeprazole":"PPI|20-40mg|GERD,PUD|B12 def","Pantoprazole":"PPI|40mg|GERD|Headache","Famotidine":"H2RA|20-40mg|GERD,PUD|Constipation","Ondansetron":"5-HT3 antag|4-8mg|N/V|Headache","Loperamide":"Opioid|2-4mg|Diarrhea|Constipation","Lactulose":"Osmotic|15-30mL|Constipation,HE|Bloating","Infliximab":"Anti-TNF|5mg/kg|Crohn,UC|Infection","Adalimumab":"Anti-TNF|40mg SC|Crohn,UC|ISR","Esomeprazole":"PPI|20-40mg|GERD,Hpylori|GI","Metoclopramide":"DA antag|10mg|Gastroparesis|EPS,TD","Mesalamine":"5-ASA|2.4-4.8g|UC|Headache","UDCA":"Bile acid|10-15mg/kg|PBC,stones|Diarrhea","Sucralfate":"Protectant|1g|PUD|Constipation","Bismuth":"Antisecretory|524mg|Diarrhea,Hpylori|Black stool","Vedolizumab":"Anti-integrin|300mg|UC,Crohn|Infection","PEG":"Osmotic|17g|Constipation|Bloating","Dicyclomine":"AC|20mg|IBS|Dry mouth","Prochlorperazine":"Antiemetic|5-10mg|N/V,Vertigo|Sedation","Lubiprostone":"Cl channel|24mcg|Constipation|Nausea","Linaclotide":"GC-C agonist|145-290mcg|IBS-C|Diarrhea"},"Respiratory":{"Albuterol":"SABA|2 puffs|Asthma,COPD|Tremor","Fluticasone":"ICS|100-500mcg|Asthma|Thrush","Montelukast":"LTRA|10mg|Asthma,AR|Headache","Tiotropium":"LAMA|18mcg|COPD|Dry mouth","Salmeterol":"LABA|50mcg|Asthma,COPD|Tremor","Budesonide":"ICS|200-800mcg|Asthma,COPD|Cough","Ipratropium":"SAMA|2-4 puffs|COPD,Asthma|Dry mouth","Theophylline":"Methylxanthine|200-600mg|Asthma,COPD|Nausea,Seizures","Roflumilast":"PDE-4i|500mcg|COPD|Diarrhea","Formoterol":"LABA|12mcg|Asthma,COPD|Tremor","Beclomethasone":"ICS|40-80mcg|Asthma|Thrush","Zafirlukast":"LTRA|20mg|Asthma|Headache","Omalizumab":"Anti-IgE|150-375mg|Allergic asthma|Anaphylaxis","Mepolizumab":"Anti-IL5|100mg|Eos asthma|Headache","Benralizumab":"Anti-IL5R|30mg|Eos asthma|Headache"},"Analgesics":{"Ibuprofen":"NSAID|200-800mg|Pain,Inflam|GI,Renal","Acetaminophen":"Analgesic|500-1000mg|Pain,Fever|Hepato","Tramadol":"Opioid+SNRI|50-100mg|Mod pain|Nausea,Seizures","Morphine":"Opioid|5-30mg|Severe pain|RD","Fentanyl":"Opioid|12-100mcg/h|Chronic pain|RD","Lidocaine":"Local anesthetic|1-2%|Local anesthesia|CNS","Ketamine":"NMDA antag|0.5-2mg/kg|Anesthesia,Pain|Hallucinations","Propofol":"GABA agonist|1-2mg/kg|Induction|RD","Midazolam":"BZD|1-5mg|Sedation|RD","Gabapentin":"Gabapentinoid|300-3600mg|Neuropain|Sedation","Naproxen":"NSAID|250-500mg|Pain,Inflam|GI","Celecoxib":"COX-2i|100-200mg|OA,RA|CV risk","Oxycodone":"Opioid|5-30mg|Severe pain|RD","Hydromorphone":"Opioid|2-4mg|Severe pain|RD","Methadone":"Opioid|2.5-10mg|Pain,Addiction|QT","Buprenorphine":"Partial opioid|2-24mg|Pain,Addiction|RD","Bupivacaine":"Local anesthetic|0.25-0.5%|Regional|Cardio","Pregabalin":"Gabapentinoid|75-600mg|Neuropain|Dizziness","Diclofenac":"NSAID|50mg|Pain|GI","Meloxicam":"NSAID|7.5-15mg|OA|GI"},"Oncology":{"Cyclophosphamide":"Alkylating|500-1000mg/m2|Lymphoma,BC|Myelo,HC","Doxorubicin":"Anthracycline|60-75mg/m2|BC,Lung,Lymph|Cardio","Cisplatin":"Platinum|50-100mg/m2|Testicular,Ovarian|Nephro,Oto","5-FU":"Antimetabolite|400-600mg/m2|CRC,BC|Mucositis","Paclitaxel":"Taxane|175mg/m2|BC,Ovarian,Lung|Neuropathy","Tamoxifen":"SERM|20mg|BC(ER+)|Hot flashes","Rituximab":"Anti-CD20|375mg/m2|Lymph,CLL|IR","Bevacizumab":"Anti-VEGF|5-15mg/kg|CRC,Lung,RCC|HTN,Bleed","Pembrolizumab":"Anti-PD1|200mg|Melanoma,Lung|irAE","Carboplatin":"Platinum|AUC 5-6|Ovarian,Lung|Myelo","Methotrexate":"Antimetabolite|Variable|Leukemia,Lymph|Myelo,Hepato","Docetaxel":"Taxane|75-100mg/m2|BC,Prostate|Myelo","Imatinib":"TKI|400mg|CML,GIST|Edema","Trastuzumab":"Anti-HER2|4-8mg/kg|BC(HER2+)|Cardio","Lenalidomide":"IMiD|10-25mg|MM|Myelo,Thrombosis"},"Dermatology":{"HC Topical":"Steroid|1%|Eczema|Atrophy","Betamethasone":"Steroid|0.1%|Psoriasis|Atrophy","Clotrimazole":"Antifungal|1%|Tinea|Irritation","Mupirocin":"Antibiotic|2%|Impetigo|Burning","Tretinoin":"Retinoid|0.025-0.1%|Acne|Irritation","Isotretinoin":"Retinoid|0.5-1mg/kg|Severe acne|Teratogenic","Adapalene":"Retinoid|0.1%|Acne|Dryness","Tacrolimus Top":"CNI|0.1%|Atopic derm|Burning","Ustekinumab":"Anti-IL12/23|45-90mg|Psoriasis|Infection","Secukinumab":"Anti-IL17A|300mg|Psoriasis|Candidiasis"},"Ophthalmology":{"Timolol":"BB|0.5%|Glaucoma|Bradycardia","Latanoprost":"PG analog|0.005%|Glaucoma|Iris pigment","Brimonidine":"A2 agonist|0.2%|Glaucoma|Allergy","Dorzolamide":"CAI|2%|Glaucoma|Bitter taste","Cyclosporine Oph":"Immunomod|0.05%|Dry eye|Burning"}}.items():
    for name, info in drugs.items():
        p = info.split("|")
        DRUG_DATABASE[cat][name] = {"class":p[0],"dose":p[1],"indications_en":p[2],"indications_ku":p[2],"indications_ar":p[2],"side_effects_en":p[3],"side_effects_ku":p[3],"side_effects_ar":p[3]}

DISEASE_DATABASE = {
    "Diabetes Mellitus Type 1":{"symptoms_en":["Polyuria","Polydipsia","Weight loss","Fatigue","Blurred vision","Ketoacidosis"],"symptoms_ku":["میزی زۆر","تینوویەتی","کێش کەم","ماندوویی","بینی تەڵخ","کیتۆئەسیدۆز"],"symptoms_ar":["كثرة التبول","عطش","فقدان وزن","تعب","رؤية ضبابية","حماض كيتوني"],"treatment_en":["Insulin","Carb counting","Exercise"],"treatment_ku":["ئەنسولین","ژمێریاری","وەرزش"],"treatment_ar":["أنسولين","حساب كربوهيدرات","تمارين"],"risk":"High"},
    "Diabetes Mellitus Type 2":{"symptoms_en":["Polyuria","Polydipsia","Fatigue","Slow wound healing"],"symptoms_ku":["میزی زۆر","تینوویەتی","ماندوویی","خاوی برین"],"symptoms_ar":["كثرة تبول","عطش","تعب","بطء التئام"],"treatment_en":["Metformin","Lifestyle","Exercise"],"treatment_ku":["مێتفۆرمین","شێوازی ژیان","وەرزش"],"treatment_ar":["ميتفورمين","نمط حياة","تمارين"],"risk":"Moderate"},
    "Essential Hypertension":{"symptoms_en":["Asymptomatic","Headache","Dizziness","Blurred vision"],"symptoms_ku":["بێ نیشانە","سەرئێشە","سەرگێژ","بینی تەڵخ"],"symptoms_ar":["بدون أعراض","صداع","دوخة","رؤية ضبابية"],"treatment_en":["ACEI","Lifestyle","Low Na"],"treatment_ku":["ACEI","شێوازی ژیان","کەم نمەک"],"treatment_ar":["مثبط ACE","نمط حياة","قليل صوديوم"],"risk":"Low"},
    "Acute Myocardial Infarction":{"symptoms_en":["Severe chest pain","Diaphoresis","Dyspnea","Nausea","Anxiety"],"symptoms_ku":["ئازاری سنگ","ئارەقە","تەنگی هەناسە","سکچوون","دڵەڕاوکێ"],"symptoms_ar":["ألم صدر شديد","تعرق","ضيق تنفس","غثيان","قلق"],"treatment_en":["Aspirin","Nitroglycerin","Morphine","O2","PCI"],"treatment_ku":["ئەسپیرین","نایترۆ","مۆرفین","O2","PCI"],"treatment_ar":["أسبرين","نيتروجليسرين","مورفين","أكسجين","PCI"],"risk":"Critical"},
    "Pneumonia":{"symptoms_en":["Fever","Productive cough","Dyspnea","Pleuritic pain"],"symptoms_ku":["تا","کۆخە","تەنگی هەناسە","ئازاری سنگ"],"symptoms_ar":["حمى","سعال منتج","ضيق تنفس","ألم جنبي"],"treatment_en":["Amox-Clav","Azithromycin","O2"],"treatment_ku":["ئەمۆکسی","ئازیترۆ","O2"],"treatment_ar":["أموكسي","أزيثروميسين","أكسجين"],"risk":"Moderate"},
    "Asthma":{"symptoms_en":["Wheezing","Dyspnea","Chest tightness","Cough"],"symptoms_ku":["فیشک","تەنگی هەناسە","گرژبوونی سنگ","کۆخە"],"symptoms_ar":["صفير","ضيق تنفس","ضيق صدر","سعال"],"treatment_en":["SABA","ICS","Avoid triggers"],"treatment_ku":["SABA","ICS","خۆپاراستن"],"treatment_ar":["SABA","ICS","تجنب محفزات"],"risk":"Low"},
    "Iron Deficiency Anemia":{"symptoms_en":["Fatigue","Pallor","DOE","Palpitations"],"symptoms_ku":["ماندوویی","ڕەنگ زەرد","تەنگی هەناسە","لێدانی دڵ"],"symptoms_ar":["تعب","شحوب","ضيق جهد","خفقان"],"treatment_en":["FeSO4","Vitamin C","Iron diet"],"treatment_ku":["FeSO4","ڤیتامین C","خواردنی ئاسن"],"treatment_ar":["حديد","فيتامين C","غذاء غني"],"risk":"Low"},
    "CKD":{"symptoms_en":["Edema","Fatigue","Oliguria","Nausea"],"symptoms_ku":["ئاوسان","ماندوویی","کەم میزی","سکچوون"],"symptoms_ar":["وذمة","تعب","قلة بول","غثيان"],"treatment_en":["ACEI","Diet","Dialysis"],"treatment_ku":["ACEI","خواردن","دیالیز"],"treatment_ar":["ACEI","غذاء","غسيل"],"risk":"High"},
    "Hepatitis B":{"symptoms_en":["Jaundice","Fatigue","Dark urine","RUQ pain"],"symptoms_ku":["زەردبوون","ماندوویی","میز تۆخ","ئازاری سک"],"symptoms_ar":["يرقان","تعب","بول داكن","ألم"],"treatment_en":["Entecavir","Tenofovir","No alcohol"],"treatment_ku":["ئەنتێکاڤیر","تێنۆفۆڤیر","بێ کحول"],"treatment_ar":["إنتيكافير","تينوفوفير","بدون كحول"],"risk":"High"},
    "Migraine":{"symptoms_en":["Unilateral HA","Photophobia","Nausea","Aura"],"symptoms_ku":["سەرئێشە","ترسی ڕووناکی","سکچوون","ئۆرا"],"symptoms_ar":["صداع نصفي","رهاب ضوء","غثيان","هالة"],"treatment_en":["Triptans","NSAIDs","Avoid triggers"],"treatment_ku":["تریپتان","NSAIDs","خۆپاراستن"],"treatment_ar":["تريبتان","مضادات","تجنب"],"risk":"Low"},
}

QUIZ_QUESTIONS = [
    {"q_en":"First-line T2DM?","q_ku":"هێڵی یەکەم T2DM؟","q_ar":"خط أول T2DM؟","o_en":["Metformin","Insulin","Glipizide","Pioglitazone"],"o_ku":["مێتفۆرمین","ئەنسولین","گلیپیزاید","پیۆ"],"o_ar":["ميتفورمين","أنسولين","غليبيزيد","بيو"],"c":0},
    {"q_en":"MI diagnosis?","q_ku":"دەستنیشانکردنی MI؟","q_ar":"تشخيص MI؟","o_en":["Troponin I","Glucose","Hb","Creatinine"],"o_ku":["ترۆپۆنین","گلوکۆز","هیمۆگلۆبین","کریاتینین"],"o_ar":["تروبونين","جلوكوز","هيموغلوبين","كرياتينين"],"c":0},
    {"q_en":"Normal BP?","q_ku":"پەستانی ئاسایی؟","q_ar":"ضغط طبيعي؟","o_en":["<120/80","<140/90","<160/100","<100/60"],"o_ku":["<120/80","<140/90","<160/100","<100/60"],"o_ar":["<120/80","<140/90","<160/100","<100/60"],"c":0},
    {"q_en":"Megaloblastic anemia?","q_ku":"ئەنیمیای مێگالۆبلاستیک؟","q_ar":"فقر دم ضخم؟","o_en":["B12","Vit C","Vit D","Vit A"],"o_ku":["B12","C","D","A"],"o_ar":["B12","C","D","A"],"c":0},
    {"q_en":"Metformin class?","q_ku":"پۆلی مێتفۆرمین؟","q_ar":"فئة ميتفورمين؟","o_en":["Biguanide","SU","DPP-4i","SGLT2i"],"o_ku":["بیگواناید","SU","DPP-4i","SGLT2i"],"o_ar":["بيغوانيد","SU","DPP-4i","SGLT2i"],"c":0},
    {"q_en":"CI in pregnancy?","q_ku":"قەدەغە لە دووگیانی؟","q_ar":"ممنوع حمل؟","o_en":["Tetracycline","Amoxicillin","Azithromycin","Cephalexin"],"o_ku":["تێتراسایکلین","ئەمۆکسی","ئازیترۆ","سێفالێکسین"],"o_ar":["تيتراسيكلين","أموكسي","أزيثروميسين","سيفاليكسين"],"c":0},
    {"q_en":"HbA1c target?","q_ku":"ئامانجی HbA1c؟","q_ar":"هدف HbA1c؟","o_en":["<7%","<6%","<8%","<9%"],"o_ku":["<7%","<6%","<8%","<9%"],"o_ar":["<7%","<6%","<8%","<9%"],"c":0},
    {"q_en":"Lisinopril class?","q_ku":"پۆلی لیسینۆپریل؟","q_ar":"فئة ليسينوبريل؟","o_en":["ACEI","BB","CCB","Diuretic"],"o_ku":["ACEI","BB","CCB","میزەڕۆ"],"o_ar":["ACEI","BB","CCB","مدر"],"c":0},
    {"q_en":"Statin SE?","q_ku":"کاریگەری ستاتین؟","q_ar":"أثر ستاتين؟","o_en":["Myalgia","Headache","Diarrhea","Cough"],"o_ku":["ئازاری ماسوولکە","سەرئێشە","سکچوون","کۆخە"],"o_ar":["ألم عضلي","صداع","إسهال","سعال"],"c":0},
    {"q_en":"Furosemide effect?","q_ku":"کاری فورۆسیماید؟","q_ar":"تأثير فوروسيميد؟","o_en":["Hypokalemia","Hyperkalemia","HypoNa","HyperCa"],"o_ku":["کەمی پۆتاسیۆم","زۆری","کەمی سۆدیۆم","زۆری کالسیۆم"],"o_ar":["نقص K","فرط K","نقص Na","فرط Ca"],"c":0},
]
for i in range(90):
    qt = random.choice(["symptom","class","normal"])
    if qt=="symptom":
        d=random.choice(list(DISEASE_DATABASE.keys()));s=DISEASE_DATABASE[d]["symptoms_en"];cs=random.choice(s)
        ws=random.sample([x for dd in DISEASE_DATABASE for x in DISEASE_DATABASE[dd]["symptoms_en"] if x!=cs],3);o=[cs]+ws[:3];random.shuffle(o)
        QUIZ_QUESTIONS.append({"q_en":f"Symptom of {d}?","q_ku":f"نیشانەی {d}؟","q_ar":f"عرض {d}؟","o_en":o,"o_ku":o,"o_ar":o,"c":o.index(cs)})
    elif qt=="class":
        dl=[d for dd in DRUG_DATABASE.values() for d in dd];d=random.choice(dl)
        for ct,ds in DRUG_DATABASE.items():
            if d in ds: cc=ds[d]["class"];break
        wc=random.sample([x["class"] for ct in DRUG_DATABASE for x in DRUG_DATABASE[ct].values() if x["class"]!=cc],3);o=[cc]+wc[:3];random.shuffle(o)
        QUIZ_QUESTIONS.append({"q_en":f"Class of {d}?","q_ku":f"پۆلی {d}؟","q_ar":f"فئة {d}؟","o_en":o,"o_ku":o,"o_ar":o,"c":o.index(cc)})
    else:
        t=random.choice(list(LAB_TESTS.keys()));cn=LAB_TESTS[t]["normal"]
        wn=random.sample([x["normal"] for x in LAB_TESTS.values() if x["normal"]!=cn],3);o=[cn]+wn[:3];random.shuffle(o)
        QUIZ_QUESTIONS.append({"q_en":f"Normal {t}?","q_ku":f"ئاسایی {t}؟","q_ar":f"طبيعي {t}؟","o_en":o,"o_ku":o,"o_ar":o,"c":o.index(cn)})

MEDICAL_NEWS = [{"t":"New Diabetes Treatment","s":"GLP-1/GIP dual agonist shows superior glycemic control.","src":"NEJM","d":"2024-01-20"},{"t":"AI Cancer Detection","s":"ML achieves 95% accuracy in early lung cancer.","src":"Lancet","d":"2024-01-19"},{"t":"mRNA Beyond COVID","s":"mRNA vaccines for malaria show promise.","src":"Nature","d":"2024-01-18"},{"t":"Alzheimer's Progress","s":"New mAb slows cognitive decline.","src":"JAMA","d":"2024-01-17"},{"t":"AMR Crisis","s":"WHO warns of MDR infections globally.","src":"WHO","d":"2024-01-16"}]
for i in range(95):
    ts=[("Vaccines","Universal flu progress"),("Gene Rx","CRISPR advances"),("CV Health","Med diet benefits"),("Mental Health","Psychedelic Rx"),("Oncology","CAR-T approvals")]
    t=ts[i%5];dt=datetime(2024,1,1)+timedelta(days=i)
    MEDICAL_NEWS.append({"t":f"{t[0]} ({dt.strftime('%b %d')})","s":t[1],"src":random.choice(["NEJM","Lancet","JAMA","BMJ","Nature","WHO"]),"d":dt.strftime("%Y-%m-%d")})

def gs(i,l): return i.get(f"symptoms_{l}",i.get("symptoms_en",[]))
def gt(i,l): return i.get(f"treatment_{l}",i.get("treatment_en",[]))
def gd(i,l): return i.get(f"description_{l}",i.get("description_en",""))
def gi(d,l): return d.get(f"indications_{l}",d.get("indications_en",""))
def gse(d,l): return d.get(f"side_effects_{l}",d.get("side_effects_en",""))
def gr(r,l):
    m={"en":{"Critical":"Critical","High":"High","Moderate":"Moderate","Low":"Low"},"ku":{"Critical":"زۆر مەترسیدار","High":"بەرز","Moderate":"مامناوەند","Low":"کەم"},"ar":{"Critical":"حرج","High":"مرتفع","Moderate":"متوسط","Low":"منخفض"}}
    return m.get(l,m['en']).get(r,r)

@st.cache_data(ttl=300)
def lb(): 
    import pandas as pd
    return pd.read_sql_query("SELECT username,xp_points,quiz_score,cases_solved,level,last_active FROM leaderboard ORDER BY xp_points DESC",get_db())
@st.cache_data(ttl=60)
def uc():
    c=get_db().cursor();c.execute("SELECT COUNT(*) as n FROM users");r=c.fetchone();return r['n'] if r else 0

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                      SESSION STATE                                          ║
# ╚══════════════════════════════════════════════════════════════════════════════╝
def iss():
    defaults = {'logged_in':False,'username':"",'xp':0,'qs':0,'tc':0,'cd':0,'streak':0,'page':"Dashboard",'ff':False,'ce':None,'ca':{},'cs':False,'csc':0,'case':None,'ach':[],'lang':'en'}
    for k,v in defaults.items():
        if k not in st.session_state: st.session_state[k]=v

iss()
init_db()

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                      LOGIN PAGE - lg defined FIRST                          ║
# ╚══════════════════════════════════════════════════════════════════════════════╝
if not st.session_state.logged_in:
    # Define lg immediately at the start of the login block
    lg = st.session_state.lang
    
    # Language selector on login page
    c1,c2,c3=st.columns([3,1,3])
    with c2:
        st.markdown('<div class="language-switcher">',True)
        cs=st.columns(3)
        for i,(cd,nm) in enumerate([('en','EN'),('ku','KU'),('ar','AR')]):
            with cs[i]:
                if st.button(nm,key=f"ll_{cd}",use_container_width=True): st.session_state.lang=cd;st.rerun()
        st.markdown('</div>',True)
    
    cl,cc,cr=st.columns([1,1.5,1])
    with cc:
        st.markdown(f"""
        <div style="text-align:center;padding:2rem 0;">
            <div style="font-size:5rem;animation:float 3s ease-in-out infinite;filter:drop-shadow(0 0 30px rgba(99,102,241,0.5));">⚕️</div>
            <h1 style="font-size:2.8rem;margin:1rem 0;">Dr.Danyal</h1>
            <p style="color:#94a3b8;font-size:1.1rem;letter-spacing:0.5px;">{t('app_subtitle',lg)}</p>
        </div>
        """,True)
        
        t1,t2=st.tabs([f"🔑 {t('login',lg)}",f"📝 {t('register',lg)}"])
        
        with t1:
            with st.form("lf"):
                u=st.text_input(t('username',lg),placeholder=t('enter_username',lg))
                p=st.text_input(t('password',lg),type="password",placeholder=t('enter_password',lg))
                if st.form_submit_button(t('login_button',lg),type="primary",use_container_width=True):
                    ok,msg,ud=auth_user(u,p)
                    if ok:
                        st.session_state.logged_in=True;st.session_state.username=u
                        st.session_state.xp=ud['xp_points'];st.session_state.qs=ud['quiz_score']
                        st.session_state.tc=ud['total_cases'];st.session_state.cd=ud['correct_diagnoses']
                        st.session_state.streak=upd_streak(u)
                        if ud.get('language_preference'): st.session_state.lang=ud['language_preference']
                        st.rerun()
                    else: st.error(f"❌ {msg}")
        
        with t2:
            with st.form("rf"):
                nu=st.text_input(t('choose_username',lg),placeholder=t('username',lg))
                np=st.text_input(t('choose_password',lg),type="password",placeholder=t('password',lg))
                cp=st.text_input(t('confirm_password',lg),type="password")
                if st.form_submit_button(t('register_button',lg),type="primary",use_container_width=True):
                    if np!=cp: st.error(f"❌ {t('passwords_dont_match',lg)}")
                    else:
                        ok,msg=create_user(nu,np)
                        if ok: st.success(f"✅ {t('account_created',lg)}")
                        else: st.error(f"❌ {msg}")
    st.stop()

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                      SIDEBAR - WORKING NAVIGATION                           ║
# ╚══════════════════════════════════════════════════════════════════════════════╝
lg = st.session_state.lang

with st.sidebar:
    st.markdown('<div class="language-switcher">',True)
    cs=st.columns(3)
    for i,(cd,nm) in enumerate([('en','EN'),('ku','KU'),('ar','AR')]):
        with cs[i]:
            if st.button(nm,key=f"sl_{cd}",use_container_width=True):
                st.session_state.lang=cd
                get_db().execute("UPDATE users SET language_preference=? WHERE username=?",(cd,st.session_state.username));get_db().commit()
                st.rerun()
    st.markdown('</div>',True)
    
    lv=get_lvl(st.session_state.xp);li=LVLS[lv];pg=lvl_prog(st.session_state.xp)
    
    st.markdown(f"""
    <div class="premium-card" style="text-align:center;padding:1.5rem;">
        <div style="font-size:3.5rem;animation:float 4s ease-in-out infinite;">{li[1]}</div>
        <div style="font-weight:700;color:#f8fafc;font-size:1.1rem;margin:0.5rem 0;">{st.session_state.username}</div>
        <span class="badge badge-primary">{li[0]}</span>
        <div style="margin-top:1rem;">
            <div class="progress-bar"><div class="progress-fill" style="width:{pg:.1f}%;"></div></div>
            <div style="font-size:0.65rem;color:#64748b;text-align:right;margin-top:0.3rem;">{t('level_progress',lg)} {pg:.0f}%</div>
        </div>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem;margin:1rem 0;">
        <div class="stat-card"><div class="stat-number">⭐ {st.session_state.xp}</div><div class="stat-label">{t('xp',lg)}</div></div>
        <div class="stat-card"><div class="stat-number">📊 {st.session_state.qs}</div><div class="stat-label">{t('quiz_score',lg)}</div></div>
        <div class="stat-card"><div class="stat-number">🔥 {st.session_state.streak}</div><div class="stat-label">{t('streak',lg)}</div></div>
        <div class="stat-card"><div class="stat-number">🩺 {st.session_state.tc}</div><div class="stat-label">{t('cases',lg)}</div></div>
    </div>
    """,True)
    
    st.markdown("---")
    
    pages = [
        ("dashboard","📊 "+t('dashboard',lg)),("diseases","🦠 "+t('diseases',lg)),
        ("case_analysis","🔬 "+t('case_analysis',lg)),("quiz","🧠 "+t('quiz',lg)),
        ("comprehensive_exam","📋 "+t('comprehensive_exam',lg)),("spaced_repetition","🔄 "+t('spaced_repetition',lg)),
        ("lab_tests","🧪 "+t('lab_tests',lg)),("pharmacology","💊 "+t('pharmacology',lg)),
        ("drug_interactions","⚠️ "+t('drug_interactions',lg)),("leaderboard","🏆 "+t('leaderboard',lg)),
        ("medical_news","📰 "+t('medical_news',lg)),("ai_assistant","🤖 "+t('ai_assistant',lg)),
        ("clinical_notes","📝 "+t('clinical_notes',lg)),("achievements","🎯 "+t('achievements',lg)),
    ]
    for key, label in pages:
        if st.button(label, key=f"nav_{key}", use_container_width=True):
            st.session_state.page = key
            st.rerun()
    
    st.markdown("---")
    if st.button(f"🚪 {t('logout',lg)}", key="logout_btn", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()
    
    st.markdown(f'<div style="text-align:center;font-size:0.65rem;color:#64748b;"><span class="badge badge-primary">{t("version",lg)}</span></div>',True)

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                      PAGE ROUTER                                            ║
# ╚══════════════════════════════════════════════════════════════════════════════╝
page = st.session_state.page

if page == "Dashboard":
    st.markdown(f'<h1 style="text-align:center;margin-bottom:2rem;">{t("dashboard",lg)}</h1>',True)
    cs=st.columns(5)
    for c,(l,v) in zip(cs,[(t("diseases_count",lg),len(DISEASE_DATABASE)),(t("drugs_count",lg),sum(len(d) for d in DRUG_DATABASE.values())),(t("tests_count",lg),len(LAB_TESTS)),(t("xp",lg),st.session_state.xp),(t("streak",lg),st.session_state.streak)]):
        with c: st.markdown(f'<div class="stat-card"><div class="stat-number">{v}</div><div class="stat-label">{l}</div></div>',True)
    c1,c2=st.columns(2)
    with c1: st.markdown(f'<div class="premium-card"><h3>{t("your_progress",lg)}</h3><p>🎯 {li[1]} {li[0]} | 📊 {st.session_state.qs} pts | 🩺 {st.session_state.tc} cases | ✅ {(st.session_state.cd/max(st.session_state.tc,1)*100):.0f}% accuracy</p></div>',True)
    with c2: st.markdown(f'<div class="premium-card"><h3>{t("platform_stats",lg)}</h3><p>👥 {uc()} users | 🦠 {len(DISEASE_DATABASE)} diseases | 💊 {sum(len(d) for d in DRUG_DATABASE.values())} drugs | 🧪 {len(LAB_TESTS)} tests</p></div>',True)

elif page == "Diseases":
    st.markdown(f'<h2>🦠 {t("disease_library",lg)}</h2>',True)
    s=st.text_input(t("search",lg),placeholder=t("search_placeholder",lg))
    rf=st.selectbox(t("risk_level",lg),[t("all",lg),t("critical",lg),t("high",lg),t("moderate",lg),t("low",lg)])
    rm={t("critical",lg):"Critical",t("high",lg):"High",t("moderate",lg):"Moderate",t("low",lg):"Low"}
    fd=DISEASE_DATABASE.copy()
    if s: fd={k:v for k,v in fd.items() if s.lower() in k.lower()}
    if rf!=t("all",lg): fd={k:v for k,v in fd.items() if v.get("risk")==rm.get(rf,rf)}
    cs=st.columns(2)
    for i,(d,inf) in enumerate(fd.items()):
        with cs[i%2]:
            with st.expander(f"🩺 {d}"):
                rc={"Critical":"#ef4444","High":"#f59e0b","Moderate":"#06b6d4","Low":"#10b981"}
                st.markdown(f"**{t('risk',lg)}:** <span style='color:{rc.get(inf.get('risk','Low'))}'>{gr(inf.get('risk','Low'),lg)}</span>",True)
                st.markdown(f"**{t('symptoms',lg)}:** {', '.join(gs(inf,lg)[:5])}")
                st.markdown(f"**{t('treatment',lg)}:** {', '.join(gt(inf,lg)[:3])}")

elif page == "Case Analysis":
    st.markdown(f'<h2>🔬 {t("clinical_case_analysis",lg)}</h2>',True)
    if st.button(t("generate_new_case",lg),type="primary",use_container_width=True):
        d=random.choice(list(DISEASE_DATABASE.keys()));inf=DISEASE_DATABASE[d]
        gm={"en":random.choice(["Male","Female"]),"ku":random.choice(["نێر","مێ"]),"ar":random.choice(["ذكر","أنثى"])}
        st.session_state.case={"id":f"CASE-{random.randint(1000,9999)}","age":random.randint(18,85),"gender":gm,"symptoms":random.sample(gs(inf,lg),min(5,len(gs(inf,lg)))),"diagnosis":d,"risk":inf["risk"]}
        st.rerun()
    if st.session_state.case:
        ca=st.session_state.case;g=ca["gender"].get(lg,ca["gender"].get("en",""))
        st.markdown(f'<div class="premium-card"><h3>{t("case_id",lg)} #{ca["id"]}</h3><p><strong>{t("patient",lg)}:</strong> {ca["age"]} {t("years_old",lg)} {g}</p><p><strong>{t("symptoms",lg)}:</strong> {", ".join(ca["symptoms"])}</p></div>',True)
        dx=st.selectbox(t("your_diagnosis",lg),list(DISEASE_DATABASE.keys()))
        if st.button(t("submit",lg),type="primary"):
            st.session_state.tc+=1
            if dx==ca["diagnosis"]: st.session_state.cd+=1;add_xp(st.session_state.username,20);st.success(f"🎉 {t('correct',lg)}!")
            else: st.error(f"❌ {t('incorrect',lg)}")
            get_db().execute("UPDATE users SET total_cases=?,correct_diagnoses=? WHERE username=?",(st.session_state.tc,st.session_state.cd,st.session_state.username));get_db().commit()

elif page == "Quiz":
    st.markdown(f'<h2>🧠 {t("medical_quiz",lg)}</h2>',True)
    q=random.choice(QUIZ_QUESTIONS);qu=q.get(f"q_{lg}",q["q_en"]);op=q.get(f"o_{lg}",q["o_en"])
    st.markdown(f'<div class="premium-card"><h3>{qu}</h3></div>',True)
    a=st.radio(t("select_answer",lg),op,key="qa")
    if st.button(t("submit_answer",lg),type="primary"):
        if op.index(a)==q["c"]: st.session_state.qs+=1;add_xp(st.session_state.username,10);st.success(f"🎉 {t('correct',lg)}!")
        else: st.error(f"❌ {t('incorrect',lg)}")
        get_db().execute("UPDATE users SET quiz_score=? WHERE username=?",(st.session_state.qs,st.session_state.username));get_db().commit();st.rerun()

elif page == "Comprehensive Exam":
    st.markdown(f'<h2>📋 {t("comprehensive_exam_title",lg)}</h2>',True)
    if st.session_state.ce is None:
        if st.button(t("start_exam",lg),type="primary",use_container_width=True): st.session_state.ce=random.sample(QUIZ_QUESTIONS,min(50,len(QUIZ_QUESTIONS)));st.session_state.ca={};st.session_state.cs=False;st.rerun()
    elif not st.session_state.cs:
        for i,q in enumerate(st.session_state.ce):
            qu=q.get(f"q_{lg}",q["q_en"]);op=q.get(f"o_{lg}",q["o_en"])
            st.markdown(f"**{i+1}. {qu}**");a=st.radio(f"Q{i}",op,key=f"ex_{i}",label_visibility="collapsed")
            st.session_state.ca[i]=op.index(a) if a else -1
        if st.button(t("submit_exam",lg),type="primary"):
            sc=sum(1 for i,q in enumerate(st.session_state.ce) if st.session_state.ca.get(i)==q["c"])
            st.session_state.csc=sc;st.session_state.cs=True;add_xp(st.session_state.username,sc*2);st.rerun()
    else:
        sc=st.session_state.csc;t=len(st.session_state.ce)
        st.markdown(f'<div class="premium-card" style="text-align:center;"><h2>🎉 {t("score",lg)}: {sc}/{t} ({(sc/t*100):.0f}%)</h2></div>',True)
        if st.button(t("retake",lg)): st.session_state.ce=None;st.rerun()

elif page == "Spaced Repetition":
    st.markdown(f'<h2>🔄 {t("spaced_repetition_title",lg)}</h2>',True)
    d=random.choice(list(DISEASE_DATABASE.keys()));inf=DISEASE_DATABASE[d]
    if st.session_state.ff:
        st.markdown(f'<div class="premium-card" style="text-align:center;"><h3>{d}</h3><p><strong>{t("symptoms",lg)}:</strong> {", ".join(gs(inf,lg)[:4])}</p><p style="color:#818cf8;"><strong>{t("treatment",lg)}:</strong> {", ".join(gt(inf,lg)[:3])}</p></div>',True)
        c1,c2=st.columns(2)
        with c1:
            if st.button(f"✅ {t('knew_it',lg)}",type="primary",use_container_width=True): st.session_state.ff=False;add_xp(st.session_state.username,5);st.rerun()
        with c2:
            if st.button(f"❌ {t('review_again',lg)}",use_container_width=True): st.session_state.ff=False;st.rerun()
    else:
        st.markdown(f'<div class="premium-card" style="text-align:center;padding:3rem;"><h3>{t("what_are_symptoms_of",lg)} {d}?</h3></div>',True)
        if st.button(f"👁️ {t('reveal_answer',lg)}",use_container_width=True): st.session_state.ff=True;st.rerun()

elif page == "Lab Tests":
    st.markdown(f'<h2>🧪 {t("lab_tests_title",lg)} ({len(LAB_TESTS)})</h2>',True)
    s=st.text_input(t("search",lg));ct=st.selectbox(t("category",lg),[t("all",lg)]+sorted(set(v["category"] for v in LAB_TESTS.values())))
    fd={k:v for k,v in LAB_TESTS.items() if (not s or s.lower() in k.lower()) and (ct==t("all",lg) or v["category"]==ct)}
    if fd:
        import pandas as pd
        st.dataframe(pd.DataFrame([{"Test":k,"Range":v["normal"],t("description",lg):gd(v,lg)} for k,v in fd.items()]),use_container_width=True,height=400)
    else: st.info(t("no_tests_found",lg))

elif page == "Pharmacology":
    st.markdown(f'<h2>💊 {t("pharmacology_title",lg)} ({sum(len(d) for d in DRUG_DATABASE.values())})</h2>',True)
    s=st.text_input(t("search",lg))
    for ct,ds in DRUG_DATABASE.items():
        cd={k:v for k,v in ds.items() if not s or s.lower() in k.lower()}
        if cd:
            with st.expander(f"📂 {ct} ({len(cd)})"):
                for d,inf in cd.items():
                    st.markdown(f'<div class="premium-card"><h4>{d}</h4><p><strong>{t("drug_class",lg)}:</strong> {inf["class"]} | <strong>{t("dose",lg)}:</strong> {inf["dose"]}</p><p><strong>{t("indications",lg)}:</strong> {gi(inf,lg)}</p><p style="color:#f87171;"><strong>{t("side_effects",lg)}:</strong> {gse(inf,lg)}</p></div>',True)

elif page == "Drug Interactions":
    st.markdown(f'<h2>⚠️ {t("drug_interactions_title",lg)}</h2>',True)
    ad=[d for ds in DRUG_DATABASE.values() for d in ds];sl=st.multiselect(t("select_drugs",lg),ad)
    if len(sl)>=2: st.info(f"{len(sl)} {t('drugs_selected',lg)}")
    else: st.info(t("select_minimum",lg))

elif page == "Leaderboard":
    st.markdown(f'<h2>🏆 {t("leaderboard_title",lg)}</h2>',True)
    df=lb()
    if not df.empty:
        for i,(_,r) in enumerate(df.iterrows()):
            m="🥇" if i==0 else "🥈" if i==1 else "🥉" if i==2 else f"#{i+1}"
            st.markdown(f'<div class="premium-card"><h3>{m} {r["username"]}</h3><p>⭐ {r["xp_points"]} XP | 📊 {r["quiz_score"]} | 🩺 {r["cases_solved"]}</p></div>',True)
    else: st.info(t("no_data",lg))

elif page == "Medical News":
    st.markdown(f'<h2>📰 {t("medical_news",lg)} ({len(MEDICAL_NEWS)})</h2>',True)
    for n in MEDICAL_NEWS[:20]: st.markdown(f'<div class="premium-card"><h4>📰 {n["t"]}</h4><p>{n["s"]}</p><p style="color:#64748b;">📅 {n["d"]} | 📚 {n["src"]}</p></div>',True)

elif page == "AI Assistant":
    st.markdown(f'<h2>🤖 {t("ai_assistant_title",lg)}</h2>',True)
    st.markdown(f'<p style="color:#94a3b8;">📊 {len(DISEASE_DATABASE)} diseases | {sum(len(d) for d in DRUG_DATABASE.values())} drugs | {len(LAB_TESTS)} tests loaded</p>',True)
    sy=st.text_area(t("enter_symptoms",lg),placeholder="fever, cough, fatigue...",height=100)
    if st.button(f"🔍 {t('analyze',lg)}",type="primary") and sy:
        sl=[s.strip().lower() for s in sy.split(",") if s.strip()];rs=[]
        for d,inf in DISEASE_DATABASE.items():
            ds=[s.lower() for s in gs(inf,'en')];m=len(set(sl)&set(ds))
            if m>0: rs.append((d,(m/len(ds))*100,inf["risk"]))
        rs.sort(key=lambda x:x[1],reverse=True)
        if rs:
            for d,mt,rk in rs[:10]:
                rc={"Critical":"#ef4444","High":"#f59e0b","Moderate":"#06b6d4","Low":"#10b981"}
                st.markdown(f'<div class="premium-card"><h4>{d}</h4><p>{t("match",lg)}: {mt:.0f}% | {t("risk",lg)}: <span style="color:{rc.get(rk)}">{gr(rk,lg)}</span></p></div>',True)
        else: st.info("No matches found.")

elif page == "Clinical Notes":
    st.markdown(f'<h2>📝 {t("clinical_notes_title",lg)}</h2>',True)
    with st.form("an"):
        pn=st.text_input(t("patient_info",lg));nt=st.text_area(t("clinical_note",lg))
        if st.form_submit_button(f"💾 {t('save_note',lg)}",type="primary"):
            get_db().execute("INSERT INTO clinical_notes(username,patient_info,note) VALUES(?,?,?)",(st.session_state.username,pn,nt));get_db().commit()
            st.success(f"✅ {t('note_saved',lg)}");st.rerun()
    for n in get_db().execute("SELECT * FROM clinical_notes WHERE username=? ORDER BY created_at DESC LIMIT 20",(st.session_state.username,)).fetchall():
        st.markdown(f'<div class="premium-card"><p><strong>{t("patient_info",lg)}:</strong> {n["patient_info"]}</p><p>{n["note"]}</p><p style="color:#64748b;">{n["created_at"][:10]}</p></div>',True)

elif page == "Achievements":
    st.markdown(f'<h2>🎯 {t("achievements_title",lg)}</h2>',True)
    ach=[("First Steps","🩺",st.session_state.tc>=1),("Case Master","🏆",st.session_state.tc>=20),("Quiz Pro","📝",st.session_state.qs>=10),("Quiz Expert","🎓",st.session_state.qs>=50),("Streak","🔥",st.session_state.streak>=7),("XP Hunter","⭐",st.session_state.xp>=100),("XP Master","💎",st.session_state.xp>=500),("Diagnostician","🔍",st.session_state.cd>=5)]
    cs=st.columns(3)
    for i,(n,ic,er) in enumerate(ach):
        with cs[i%3]: st.markdown(f'<div class="premium-card" style="text-align:center;opacity:{1 if er else 0.5};"><div style="font-size:3rem;">{ic}</div><h4>{n}</h4><span class="badge {"badge-success" if er else "badge-warning"}">{t("earned",lg) if er else t("locked",lg)}</span></div>',True)

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                      FOOTER                                                 ║
# ╚══════════════════════════════════════════════════════════════════════════════╝
st.markdown("---")
st.markdown(f"""
<div style="text-align:center;padding:2rem;color:#64748b;">
    <p style="font-weight:600;color:#94a3b8;">⚕️ Dr.Danyal Medical Platform {t('version',lg)}</p>
    <p style="font-size:0.8rem;">{len(DISEASE_DATABASE)} Diseases | {sum(len(d) for d in DRUG_DATABASE.values())} Medications | {len(LAB_TESTS)} Lab Tests | {len(QUIZ_QUESTIONS)} Quizzes | {len(MEDICAL_NEWS)} News | {uc()} Users</p>
    <p style="font-size:0.7rem;">© {datetime.now().year} {t('copyright',lg)}</p>
</div>
""",True)
