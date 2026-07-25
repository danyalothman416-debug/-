import flet as ft
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import json
import time
import hashlib
import os
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')

# ================================
# 1. سیستەمی لۆگین و خەزنکردنی داتا
# ================================
DATA_DIR = "user_data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

USERS_FILE = os.path.join(DATA_DIR, "users.json")

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def load_users() -> Dict:
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_users(users: Dict):
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

def load_user_data(username: str) -> Dict:
    users = load_users()
    if username in users:
        return users[username]
    return {}

def save_user_data(username: str, data: Dict):
    users = load_users()
    if username in users:
        users[username].update(data)
        save_users(users)

# ================================
# 2. سیستەمی ئاستەکان (Levels)
# ================================
LEVELS = {
    1: {"name": "سەرەتایی", "min_score": 0, "max_score": 9, "color": "#28a745", "quizzes": 50, "icon": "🌱", "description": "دەستپێکی ڕێگای پزیشکی"},
    2: {"name": "فێرخواز", "min_score": 10, "max_score": 29, "color": "#17a2b8", "quizzes": 100, "icon": "📖", "description": "فێربوونی بنەماکان"},
    3: {"name": "پێشکەوتوو", "min_score": 30, "max_score": 59, "color": "#ffc107", "quizzes": 150, "icon": "🚀", "description": "پێشکەوتن لە زانست"},
    4: {"name": "شارەزا", "min_score": 60, "max_score": 89, "color": "#ff9f1c", "quizzes": 200, "icon": "🏆", "description": "شارەزایی"},
    5: {"name": "پزیشک", "min_score": 90, "max_score": 100, "color": "#dc3545", "quizzes": 500, "icon": "👨‍⚕️", "description": "پزیشکی لێهاتوو"}
}

def get_user_level(score: int) -> int:
    for level, info in LEVELS.items():
        if info["min_score"] <= score <= info["max_score"]:
            return level
    return 1

def get_level_info(level: int) -> Dict:
    return LEVELS.get(level, LEVELS[1])

def get_level_icon(level: int) -> str:
    return get_level_info(level).get("icon", "📚")

# ================================
# 3. داتابەسی نەخۆشییەکان
# ================================
DISEASE_DATABASE = {
    "شەکرەی جۆری 1": {
        "نیشانەکان": ["تینوویەتی زۆر", "میزی زۆر", "کێش کەمبوونەوە", "ماندوویی"],
        "پشکنینەکان": {"FBS": ">200", "HbA1c": ">8%", "C-peptide": "نزم"},
        "چارەسەر": ["ئەنسولین", "پێوانەکردنی شەکر"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندی": "تەمەن < 30 + C-peptide نزم"
    },
    "شەکرەی جۆری 2": {
        "نیشانەکان": ["تینوویەتی زۆر", "ماندوویی", "کێش کەمبوونەوە"],
        "پشکنینەکان": {"FBS": ">126", "HbA1c": ">6.5%"},
        "چارەسەر": ["مێتفۆرمین 500mg", "گۆڕینی شێوازی ژیان"],
        "ئاستی مەترسی": "مەترسیدار",
        "تایبەتمەندی": "FBS بەرز + تەمەن > 40"
    },
    "پەستانی خوێنی سەرەتایی": {
        "نیشانەکان": ["سەرئێشە", "سەرگێژخواردن", "خێرالێدانی دڵ"],
        "پشکنینەکان": {"BP": ">140/90 mmHg", "ECG": "نۆرماڵ"},
        "چارەسەر": ["کاپتۆپریل 25mg", "کەمکردنەوەی نمەک"],
        "ئاستی مەترسی": "مامناوەند",
        "تایبەتمەندی": "BP بەرز بەبێ هۆکاری دیکە"
    }
    # (بۆ کەمکردنەوەی قەبارەی کۆد لێرە تەنها چەند نەخۆشییەک دانراوە، بەڵام لە کۆدی ڕەسەنیدا هەمووی دێنرێت)
}

# ================================
# 4. داتابەسی پشکنینەکانی تاقیگە
# ================================
LAB_TESTS = {
    "CBC": {"گروپ": "خوێن", "نۆرماڵ": (4.0, 11.0), "یەکە": "x10³/µL", "تەفسیر": "خڕۆکە سپیەکان", "ئامێر": "Sysmex XN-9000", "تێبینی": ""},
    "Hemoglobin": {"گروپ": "خوێن", "نۆرماڵ": (12.0, 16.0), "یەکە": "g/dL", "تەفسیر": "هیمۆگلۆبین", "ئامێر": "HemoCue 201+", "تێبینی": ""},
    "Glucose": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (70, 126), "یەکە": "mg/dL", "تەفسیر": "شەکری خوێن", "ئامێر": "Roche Cobas c502", "تێبینی": ""},
    "Troponin I": {"گروپ": "دڵ", "نۆرماڵ": (0, 0.04), "یەکە": "ng/mL", "تەفسیر": "پروتێینی دڵ", "ئامێر": "Roche Cobas e411", "تێبینی": ""},
}

# ================================
# 5. داتابەسی دەرمانەکان
# ================================
DRUG_DATABASE = {
    "دژە پەستانی خوێن": {
        "کاپتۆپریل": {"ڕێژە": "25-50mg", "میکانیزم": "ACE inhibitor", "کاریگەری لاوەکی": "کۆخە", "پێچەوانە": "حەمل", "وەسف": "کەمکردنەوەی پەستانی خوێن", "بۆچی": "گورچیلە پارێزی", "تێبینی": ""},
        "ئەملۆدیپین": {"ڕێژە": "5-10mg", "میکانیزم": "CCB", "کاریگەری لاوەکی": "ئاوسانی قاچ", "پێچەوانە": "هەستیاری", "وەسف": "فراوانکەری خوێنبەر", "بۆچی": "پەستانی خوێن", "تێبینی": ""}
    },
    "دژە شەکرە": {
        "مێتفۆرمین": {"ڕێژە": "500-2000mg", "میکانیزم": "Biguanide", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "کەمکردنی شەکر", "بۆچی": "شەکرەی جۆری ٢", "تێبینی": ""}
    }
}

# ================================
# 6. سیستەمی کویز
# ================================
MEDICAL_QUIZZES = [
    {"پرسیار": "نیشانەی سەرەکی شەکرە چییە؟", "هەڵبژاردەکان": ["تینوویەتی زۆر", "سەرئێشە", "ئازاری سنگ"], "وەڵامی ڕاست": 0, "ئاست": 1},
    {"پرسیار": "پەستانی خوێنی نۆرماڵ چەندە؟", "هەڵبژاردەکان": ["120/80", "140/90", "160/100"], "وەڵامی ڕاست": 0, "ئاست": 1}
]

# ================================
# 7. فانکشنە یارمەتیدەرەکان
# ================================
def get_drug_count() -> int:
    return sum(len(v) for v in DRUG_DATABASE.values())

def analyze_lab_result(test_name: str, value: float, all_tests: Dict) -> Dict:
    if test_name not in all_tests:
        return {"status": "نەزانراو", "color": "#6c757d", "interpretation": "پشکنین نەدۆزرایەوە"}
    low, high = all_tests[test_name]["نۆرماڵ"]
    if value < low:
        return {"status": "نزم", "color": "#ffc107", "interpretation": "نزمە"}
    elif value > high:
        return {"status": "بەرز", "color": "#dc3545", "interpretation": "بەرزە"}
    else:
        return {"status": "نۆرماڵ", "color": "#28a745", "interpretation": "نۆرماڵە"}

# ================================
# 8. ستایلی جوانی پرۆگرامەر (Glassmorphism)
# ================================
def get_main_container_style():
    return {
        "bgcolor": "#0f0c29",
        "gradient": ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=["#0f0c29", "#302b63", "#24243e"]
        ),
        "padding": 0
    }

def card_style(border_color="#667eea"):
    return {
        "bgcolor": ft.colors.with_opacity(0.05, ft.colors.WHITE),
        "border_radius": 20,
        "padding": 25,
        "border": ft.border.all(1, ft.colors.with_opacity(0.1, ft.colors.WHITE)),
        "shadow": ft.BoxShadow(
            spread_radius=2,
            blur_radius=20,
            color=ft.colors.with_opacity(0.2, ft.colors.BLACK)
        )
    }

# ================================
# 9. دۆخی ئەپ (App State)
# ================================
class AppState:
    def __init__(self):
        self.logged_in = False
        self.username = ""
        self.custom_lab_tests = {}
        self.custom_drugs = {}
        self.quiz_score = 0
        self.current_page = "dashboard"
        
app_state = AppState()

# ================================
# 10. بەشەکانی UI
# ================================
def login_view(page: ft.Page):
    def do_login(e):
        if authenticate_user(username_input.value, password_input.value):
            app_state.logged_in = True
            app_state.username = username_input.value
            user_data = load_user_data(app_state.username)
            app_state.custom_lab_tests = user_data.get("custom_lab_tests", {})
            app_state.custom_drugs = user_data.get("custom_drugs", {})
            page.snack_bar = ft.SnackBar(ft.Text(f"بەخێربێیت {app_state.username}!"), bgcolor="#28a745")
            page.snack_bar.open = True
            build_main_ui(page)
        else:
            page.snack_bar = ft.SnackBar(ft.Text("❌ ناوی بەکارهێنەری یان وشەی نهێنی هەڵەیە"), bgcolor="#dc3545")
            page.snack_bar.open = True
        page.update()

    username_input = ft.TextField(label="👤 ناوی بەکارهێنەری", bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE), color=ft.colors.WHITE, border_radius=15)
    password_input = ft.TextField(label="🔒 وشەی نهێنی", password=True, can_reveal_password=True, bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE), color=ft.colors.WHITE, border_radius=15)

    return ft.Container(
        content=ft.Column(
            [
                ft.Text("🩺 Dr.Danyal", size=40, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE, text_align=ft.TextAlign.CENTER),
                ft.Text("ڕاهێنەری پزیشکی Pro Max", size=16, color=ft.colors.with_opacity(0.6, ft.colors.WHITE), text_align=ft.TextAlign.CENTER),
                ft.Container(height=20),
                username_input,
                password_input,
                ft.ElevatedButton("🚪 چوونەژوورەوە", on_click=do_login, bgcolor="#667eea", color=ft.colors.WHITE, width=ft.constants.INFINITY, height=50, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=15))),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        alignment=ft.alignment.center,
        expand=True,
        bgcolor="#0f0c29"
    )

def dashboard_view(page: ft.Page):
    level = get_user_level(app_state.quiz_score)
    level_info = get_level_info(level)
    
    return ft.Column(
        [
            ft.Text("🎓 داشبۆرد", size=32, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
            ft.Row(
                [
                    ft.Container(ft.Column([ft.Text("📚", size=30), ft.Text(f"{len(DISEASE_DATABASE)}", size=25, color="#667eea"), ft.Text("نەخۆشی")], horizontal_alignment=ft.CrossAxisAlignment.CENTER), **card_style()),
                    ft.Container(ft.Column([ft.Text("💊", size=30), ft.Text(f"{get_drug_count() + len(app_state.custom_drugs)}", size=25, color="#f093fb"), ft.Text("دەرمان")], horizontal_alignment=ft.CrossAxisAlignment.CENTER), **card_style()),
                    ft.Container(ft.Column([ft.Text("🔬", size=30), ft.Text(f"{len(LAB_TESTS) + len(app_state.custom_lab_tests)}", size=25, color="#4facfe"), ft.Text("پشکنین")], horizontal_alignment=ft.CrossAxisAlignment.CENTER), **card_style()),
                ],
                wrap=True
            ),
            ft.Container(
                ft.Column([
                    ft.Text(f"{get_level_icon(level)} ئاستی ئێستا: {level_info['name']}", size=20, color=ft.colors.WHITE),
                    ft.Text(f"نمرەی کویز: {app_state.quiz_score}/100", color=ft.colors.with_opacity(0.8, ft.colors.WHITE)),
                    ft.ProgressBar(value=app_state.quiz_score/100, color="#667eea", bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE), height=15, border_radius=10),
                ]),
                **card_style(),
                width=ft.constants.INFINITY,
                margin=ft.margin.only(top=20)
            )
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )

def lab_view(page: ft.Page):
    all_lab_tests = {**LAB_TESTS, **app_state.custom_lab_tests}
    
    def add_lab(e):
        name = new_name.value.strip()
        if not name:
            page.snack_bar = ft.SnackBar(ft.Text("❌ تکایە ناوی پشکنین بنووسە"), bgcolor="#dc3545")
            page.snack_bar.open = True
            page.update()
            return
        
        # جێگرەوەی ناوی هەڵە (ئەگەر هەڵە نووسرا بوو چاکی دەکەین)
        name = name.replace("  ", " ").strip()
        
        app_state.custom_lab_tests[name] = {
            "گروپ": new_group.value,
            "نۆرماڵ": (float(new_low.value), float(new_high.value)),
            "یەکە": new_unit.value,
            "تەفسیر": new_desc.value,
            "ئامێر": new_machine.value,
            "تێبینی": new_note.value
        }
        save_user_data(app_state.username, {"custom_lab_tests": app_state.custom_lab_tests})
        page.snack_bar = ft.SnackBar(ft.Text(f"✅ پشکنینی '{name}' زیاد کرا و خەزن کرا!"), bgcolor="#28a745")
        page.snack_bar.open = True
        build_main_ui(page)

    new_name = ft.TextField(label="ناوی پشکنین", bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE), color=ft.colors.WHITE)
    new_group = ft.Dropdown(options=[ft.dropdown.Option("گشتی"), ft.dropdown.Option("خوێن")], value="گشتی", bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE), color=ft.colors.WHITE)
    new_low = ft.TextField(label="نزمترین نۆرماڵ", value="0", bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE), color=ft.colors.WHITE)
    new_high = ft.TextField(label="بەرزترین نۆرماڵ", value="10", bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE), color=ft.colors.WHITE)
    new_unit = ft.TextField(label="یەکە", bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE), color=ft.colors.WHITE)
    new_machine = ft.TextField(label="ئامێر", bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE), color=ft.colors.WHITE)
    new_desc = ft.TextField(label="تەفسیر", bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE), color=ft.colors.WHITE)
    new_note = ft.TextField(label="📝 تێبینی تایبەتی خۆت", multiline=True, bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE), color=ft.colors.WHITE)

    lab_cards = []
    for tname, tinfo in all_lab_tests.items():
        lab_cards.append(
            ft.Container(
                ft.Column([
                    ft.Text(tname, size=18, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                    ft.Text(f"{tinfo.get('گروپ', '')} | ئامێر: {tinfo.get('ئامێر', 'نەزانراو')}", size=12, color=ft.colors.with_opacity(0.6, ft.colors.WHITE)),
                    ft.Text(f"نۆرماڵ: {tinfo['نۆرماڵ'][0]} - {tinfo['نۆرماڵ'][1]} {tinfo.get('یەکە', '')}", color=ft.colors.with_opacity(0.8, ft.colors.WHITE)),
                    ft.Text(f"📝 {tinfo.get('تێبینی', 'تێبینی نییە')}", size=12, color=ft.colors.with_opacity(0.5, ft.colors.WHITE))
                ]),
                **card_style(),
                width=300
            )
        )

    return ft.Column(
        [
            ft.Text("🔬 تاقیگەی ڤێرچواڵ", size=32, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
            ft.Row(lab_cards, wrap=True, scroll=ft.ScrollMode.AUTO),
            ft.Container(height=20),
            ft.Text("➕ پشکنینێکی نوێ زیاد بکە", size=20, color=ft.colors.WHITE),
            ft.Container(
                ft.Column([
                    ft.Row([new_name, new_group], wrap=True),
                    ft.Row([new_low, new_high, new_unit], wrap=True),
                    new_machine,
                    new_desc,
                    new_note,
                    ft.ElevatedButton("✅ زیادکردن و خەزنکردن", on_click=add_lab, bgcolor="#667eea", color=ft.colors.WHITE, width=ft.constants.INFINITY)
                ]),
                **card_style(),
                width=ft.constants.INFINITY
            )
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )

def drugs_view(page: ft.Page):
    all_drugs = {}
    for cat, drugs in DRUG_DATABASE.items():
        all_drugs[cat] = drugs
    
    # یەکخستنی دەرمانە کەسییەکان
    if app_state.custom_drugs:
        all_drugs["دەرمانە تایبەتییەکانی من"] = app_state.custom_drugs

    def add_drug(e):
        name = d_name.value.strip()
        if not name:
            page.snack_bar = ft.SnackBar(ft.Text("❌ تکایە ناوی دەرمان بنووسە"), bgcolor="#dc3545")
            page.snack_bar.open = True
            page.update()
            return
        
        name = name.replace("  ", " ").strip() # چاککردنی هەڵەی ناو
        
        app_state.custom_drugs[name] = {
            "ڕێژە": d_dose.value,
            "میکانیزم": d_mech.value,
            "کاریگەری لاوەکی": d_effect.value,
            "پێچەوانە": d_contra.value,
            "وەسف": d_desc.value,
            "بۆچی": d_why.value,
            "تێبینی": d_note.value
        }
        save_user_data(app_state.username, {"custom_drugs": app_state.custom_drugs})
        page.snack_bar = ft.SnackBar(ft.Text(f"✅ دەرمانی '{name}' زیاد کرا!"), bgcolor="#28a745")
        page.snack_bar.open = True
        build_main_ui(page)

    d_name = ft.TextField(label="ناوی دەرمان", bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE), color=ft.colors.WHITE)
    d_dose = ft.TextField(label="ڕێژە", bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE), color=ft.colors.WHITE)
    d_mech = ft.TextField(label="میکانیزم", bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE), color=ft.colors.WHITE)
    d_effect = ft.TextField(label="کاریگەری لاوەکی", bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE), color=ft.colors.WHITE)
    d_contra = ft.TextField(label="پێچەوانە", bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE), color=ft.colors.WHITE)
    d_desc = ft.TextField(label="وەسف", bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE), color=ft.colors.WHITE)
    d_why = ft.TextField(label="بۆچی", bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE), color=ft.colors.WHITE)
    d_note = ft.TextField(label="📝 تێبینی تایبەتی خۆت", multiline=True, bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE), color=ft.colors.WHITE)

    drug_ui = []
    for cat, drugs in all_drugs.items():
        drug_ui.append(ft.Text(f"📂 {cat}", size=22, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE))
        cards = []
        for dname, dinfo in drugs.items():
            cards.append(
                ft.Container(
                    ft.Column([
                        ft.Text(dname, size=16, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                        ft.Text(f"ڕێژە: {dinfo.get('ڕێژە', '')}", size=12, color=ft.colors.with_opacity(0.7, ft.colors.WHITE)),
                        ft.Text(f"بۆچی: {dinfo.get('بۆچی', '')}", size=12, color=ft.colors.with_opacity(0.7, ft.colors.WHITE)),
                        ft.Text(f"📝 {dinfo.get('تێبینی', '')}", size=12, color=ft.colors.with_opacity(0.5, ft.colors.WHITE))
                    ]),
                    **card_style(),
                    width=300
                )
            )
        drug_ui.append(ft.Row(cards, wrap=True))
        drug_ui.append(ft.Container(height=10))

    drug_ui.append(ft.Text("➕ دەرمانێکی نوێ زیاد بکە", size=20, color=ft.colors.WHITE))
    drug_ui.append(
        ft.Container(
            ft.Column([
                ft.Row([d_name, d_dose, d_mech], wrap=True),
                ft.Row([d_effect, d_contra], wrap=True),
                d_desc, d_why, d_note,
                ft.ElevatedButton("✅ زیادکردن و خەزنکردن", on_click=add_drug, bgcolor="#667eea", color=ft.colors.WHITE, width=ft.constants.INFINITY)
            ]),
            **card_style(),
            width=ft.constants.INFINITY
        )
    )

    return ft.Column(drug_ui, scroll=ft.ScrollMode.AUTO, expand=True)

# ================================
# 11. دروستکردنی ڕووکاری سەرەکی (Navigation)
# ================================
def build_main_ui(page: ft.Page):
    def navigate(e):
        index = page.navigation_bar.selected_index
        pages = ["dashboard", "diseases", "cases", "quiz", "lab", "drugs"]
        app_state.current_page = pages[index]
        render_page(page)

    def logout(e):
        save_user_data(app_state.username, {
            "custom_lab_tests": app_state.custom_lab_tests,
            "custom_drugs": app_state.custom_drugs
        })
        app_state.logged_in = False
        app_state.username = ""
        app_state.custom_lab_tests = {}
        app_state.custom_drugs = {}
        page.clean()
        page.add(login_view(page))
        page.update()

    def render_page(page: ft.Page):
        page.clean()
        
        # سایدبار / ڕووکاری سەرەوە
        appbar = ft.AppBar(
            title=ft.Text("🩺 Dr.Danyal", color=ft.colors.WHITE, weight=ft.FontWeight.BOLD),
            center_title=False,
            bgcolor="#0f0c29",
            actions=[
                ft.PopupMenuButton(
                    items=[
                        ft.PopupMenuItem(text=f"👤 {app_state.username}", disabled=True),
                        ft.PopupMenuItem(), # Divider
                        ft.PopupMenuItem(text="🚪 چوونەدەرەوە", on_click=logout),
                    ],
                    icon=ft.icons.ACCOUNT_CIRCLE,
                    icon_color=ft.colors.WHITE
                )
            ]
        )
        
        content = ft.Container(expand=True, padding=20, bgcolor="#0f0c29")
        
        if app_state.current_page == "dashboard":
            content.content = dashboard_view(page)
        elif app_state.current_page == "lab":
            content.content = lab_view(page)
        elif app_state.current_page == "drugs":
            content.content = drugs_view(page)
        else:
            content.content = ft.Column([ft.Text("بەشەکە بەم زووانە زیاد دەکرێت...", color=ft.colors.WHITE)], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            
        nav_bar = ft.NavigationBar(
            selected_index=["dashboard", "diseases", "cases", "quiz", "lab", "drugs"].index(app_state.current_page),
            on_change=navigate,
            destinations=[
                ft.NavigationBarDestination(icon=ft.icons.DASHBOARD, label="داشبۆرد"),
                ft.NavigationBarDestination(icon=ft.icons.MEDICAL_SERVICES, label="نەخۆشی"),
                ft.NavigationBarDestination(icon=ft.icons.ASSIGNMENT, label="کەیس"),
                ft.NavigationBarDestination(icon=ft.icons.QUIZ, label="کویز"),
                ft.NavigationBarDestination(icon=ft.icons.BIOTECH, label="تاقیگە"),
                ft.NavigationBarDestination(icon=ft.icons.MEDICATION, label="دەرمان"),
            ],
            bgcolor="#24243e"
        )
        
        page.add(appbar, content, nav_bar)
        page.update()

# ================================
# 12. دەستپێکردنی ئەپ
# ================================
def main(page: ft.Page):
    page.title = "Dr.Danyal - ڕاهێنەری پزیشکی Pro Max"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0f0c29"
    page.padding = 0
    
    if not app_state.logged_in:
        page.add(login_view(page))
    else:
        build_main_ui(page)

if __name__ == "__main__":
    ft.app(target=main)
