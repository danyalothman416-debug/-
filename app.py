import flet as ft
from flet import *
import pandas as pd
import numpy as np
import random
import json
import os
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List
import warnings
warnings.filterwarnings('ignore')

# ================================
# داتابەیسەکان - پێویستە هەموویان لێرە زیاد بکەیت
# ================================

DISEASE_DATABASE = {
    "شەکرەی جۆری 1": {
        "نیشانەکان": ["تینوویەتی زۆر", "میزی زۆر", "کێش کەمبوونەوە", "ماندوویی"],
        "پشکنینەکان": {"FBS": ">200 mg/dL", "HbA1c": ">8%"},
        "چارەسەر": ["ئەنسولین", "پێوانەکردنی شەکر", "شێوازی خواردن"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندی": "تەمەن < 30 + C-peptide نزم",
        "گروپی تەمەن": "منداڵان و گەنجان",
        "ڕێژەی تووشبوون": "0.5%",
        "جۆری نەخۆشی": "خۆئەگەر"
    },
    "شەکرەی جۆری 2": {
        "نیشانەکان": ["تینوویەتی زۆر", "میزی زۆر", "ماندوویی", "کێش کەمبوونەوە"],
        "پشکنینەکان": {"FBS": ">126 mg/dL", "HbA1c": ">6.5%"},
        "چارەسەر": ["مێتفۆرمین 500mg", "گۆڕینی شێوازی ژیان", "وەرزش"],
        "ئاستی مەترسی": "مەترسیدار",
        "تایبەتمەندی": "FBS بەرز + تەمەن > 40",
        "گروپی تەمەن": "تەمەن مامناوەند",
        "ڕێژەی تووشبوون": "8.5%",
        "جۆری نەخۆشی": "مێتابۆلیک"
    },
    "پەستانی خوێنی سەرەتایی": {
        "نیشانەکان": ["سەرئێشە", "سەرگێژخواردن", "فشاری پشت چاو"],
        "پشکنینەکان": {"BP": ">140/90 mmHg"},
        "چارەسەر": ["کاپتۆپریل 25mg", "کەمکردنەوەی نمەک"],
        "ئاستی مەترسی": "مامناوەند",
        "تایبەتمەندی": "BP بەرز بەبێ هۆکاری دیکە",
        "گروپی تەمەن": "هەموو تەمەنەکان",
        "ڕێژەی تووشبوون": "25%",
        "جۆری نەخۆشی": "دڵ و خوێن"
    },
    "نەخۆشی دڵی ئیسکیمیک": {
        "نیشانەکان": ["ئازاری سنگ", "کورتی هەناسە", "ئارەقەکردن"],
        "پشکنینەکان": {"ECG": "ST depression", "Troponin": "بەرز"},
        "چارەسەر": ["ئەسپیرین 300mg", "نایترۆگلیسیرین"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندی": "ST changes + Troponin elevated",
        "گروپی تەمەن": "تەمەن > 50",
        "ڕێژەی تووشبوون": "7%",
        "جۆری نەخۆشی": "دڵ و خوێن"
    }
}

LAB_TESTS = {
    "FBS": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (70, 126), "یەکە": "mg/dL", "تەفسیر": "شەکری خوێن", "ئامێر": "گلوکۆمیتەر"},
    "HbA1c": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (4.0, 5.6), "یەکە": "%", "تەفسیر": "شەکری درێژخایەن", "ئامێر": "HPLC"},
    "Creatinine": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (0.6, 1.3), "یەکە": "mg/dL", "تەفسیر": "کارایی گورچیلە", "ئامێر": "سپێکترۆفۆتۆمیتەر"},
    "Hemoglobin": {"گروپ": "خوێن", "نۆرماڵ": (12.0, 16.0), "یەکە": "g/dL", "تەفسیر": "هیمۆگلۆبین", "ئامێر": "هیمۆگلۆبینۆمیتەر"},
    "Troponin I": {"گروپ": "دڵ", "نۆرماڵ": (0, 0.04), "یەکە": "ng/mL", "تەفسیر": "پروتێینی دڵ", "ئامێر": "کیمیایی ئیمینۆ"},
    "ALT": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (10, 40), "یەکە": "U/L", "تەفسیر": "ئەنزیمی جگەر", "ئامێر": "سپێکترۆفۆتۆمیتەر"},
    "CRP": {"گروپ": "خوێن", "نۆرماڵ": (0, 5), "یەکە": "mg/L", "تەفسیر": "پروتێینی هەوکردن", "ئامێر": "توربیدیمیتەر"},
    "TSH": {"گروپ": "هۆرمۆن", "نۆرماڵ": (0.4, 4.0), "یەکە": "mIU/L", "تەفسیر": "هۆرمۆنی دروان", "ئامێر": "کیمیایی ئیمینۆ"},
    "Vitamin D": {"گروپ": "ڤیتامین", "نۆرماڵ": (30, 100), "یەکە": "ng/mL", "تەفسیر": "ڤیتامین D", "ئامێر": "کیمیایی ئیمینۆ"},
    "Cholesterol": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": (0, 200), "یەکە": "mg/dL", "تەفسیر": "کۆلسترۆل", "ئامێر": "سپێکترۆفۆتۆمیتەر"}
}

DRUG_DATABASE = {
    "دژە پەستانی خوێن": {
        "کاپتۆپریل": {"ڕێژە": "25-50mg", "میکانیزم": "ACE inhibitor", "کاریگەری لاوەکی": "کۆخە, سەرگێژخواردن", "پێچەوانە": "حەملی دووگانی", "وەسف": "دەرمانی کەمکردنەوەی پەستانی خوێن"},
        "ئەملۆدیپین": {"ڕێژە": "5-10mg", "میکانیزم": "Calcium channel blocker", "کاریگەری لاوەکی": "ئاوسانی قاچ", "پێچەوانە": "هەستیاری", "وەسف": "فراوانکەری خوێنبەرەکان"}
    },
    "دژە شەکرە": {
        "مێتفۆرمین": {"ڕێژە": "500-2000mg", "میکانیزم": "Biguanide", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "نەخۆشی گورچیلە", "وەسف": "کەمکردنی بەرهەمهێنانی شەکر"},
        "ئەنسولین Glargine": {"ڕێژە": "10-40 IU", "میکانیزم": "Insulin analog", "کاریگەری لاوەکی": "هایپۆگلایسیمیا", "پێچەوانە": "هایپۆگلایسیمیا", "وەسف": "ئەنسولینی درێژخایەن"}
    },
    "دژە کۆخە و هەوکردن": {
        "ئەمۆکسیسیلین": {"ڕێژە": "500mg", "میکانیزم": "Beta-lactam", "کاریگەری لاوەکی": "زکچوون", "پێچەوانە": "هەستیاری پێنیسیلین", "وەسف": "ئەنتیبایۆتیکی پێنیسیلین"},
        "ئازیترۆمایسین": {"ڕێژە": "250-500mg", "میکانیزم": "Macrolide", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "نەخۆشی دڵ", "وەسف": "ئەنتیبایۆتیکی ماکرۆلید"}
    },
    "دژە ئەنیمیا": {
        "فێروس سولفەیت": {"ڕێژە": "300-600mg", "میکانیزم": "Iron supplement", "کاریگەری لاوەکی": "سکچوون", "پێچەوانە": "هیمۆکروماتۆسیس", "وەسف": "پڕکەری ئاسن"},
        "فۆلیک ئەسید": {"ڕێژە": "1mg", "میکانیزم": "Folate supplement", "کاریگەری لاوەکی": "کەم", "پێچەوانە": "هەستیاری", "وەسف": "پڕکەری فۆلیک ئەسید"}
    }
}

MEDICAL_QUIZZES = [
    {"پرسیار": "نیشانەی سەرەکی شەکرەی جۆری ٢ چییە؟", "هەڵبژاردەکان": ["تینوویەتی زۆر", "سەرئێشە", "ئازاری سنگ", "کۆخە"], "وەڵامی ڕاست": 0, "ئاست": 1, "ڕوونکردنەوە": "تینوویەتی زۆر یەکێکە لە نیشانە سەرەکییەکانی شەکرە"},
    {"پرسیار": "پەستانی خوێنی نۆرماڵ چەندە؟", "هەڵبژاردەکان": ["120/80", "140/90", "160/100", "180/110"], "وەڵامی ڕاست": 0, "ئاست": 1, "ڕوونکردنەوە": "پەستانی خوێنی نۆرماڵ 120/80 mmHg"},
    {"پرسیار": "کام دەرمانە بۆ شەکرە بەکاردێت؟", "هەڵبژاردەکان": ["مێتفۆرمین", "ئەسپیرین", "کاپتۆپریل", "ئەمۆکسیسیلین"], "وەڵامی ڕاست": 0, "ئاست": 1, "ڕوونکردنەوە": "مێتفۆرمین دەرمانی هێڵی یەکەمی شەکرەی جۆری ٢"},
    {"پرسیار": "نیشانەی ئەنیمیا چییە؟", "هەڵبژاردەکان": ["ماندوویی", "سەرئێشە", "ئازاری سنگ", "کۆخە"], "وەڵامی ڕاست": 0, "ئاست": 1, "ڕوونکردنەوە": "ماندوویی نیشانەی سەرەکی ئەنیمیایە"},
    {"پرسیار": "Troponin بەرز نیشانەی چییە؟", "هەڵبژاردەکان": ["نەخۆشی دڵ", "شەکرە", "هەوکردن", "ئەنیمیا"], "وەڵامی ڕاست": 0, "ئاست": 2, "ڕوونکردنەوە": "Troponin نیشاندەری نەخۆشی دڵە"},
    {"پرسیار": "Creatinine بەرز نیشانەی چییە؟", "هەڵبژاردەکان": ["نەخۆشی گورچیلە", "نەخۆشی جگەر", "نەخۆشی دڵ", "شەکرە"], "وەڵامی ڕاست": 0, "ئاست": 2, "ڕوونکردنەوە": "Creatinine بەرز ئاماژەیە بۆ کێشەی گورچیلە"}
]

LEVELS = {
    1: {"name": "سەرەتایی", "min_score": 0, "max_score": 9, "color": "#28a745", "quizzes": 4, "icon": "🌱"},
    2: {"name": "فێرخواز", "min_score": 10, "max_score": 29, "color": "#17a2b8", "quizzes": 2, "icon": "📖"},
    3: {"name": "پێشکەوتوو", "min_score": 30, "max_score": 59, "color": "#ffc107", "quizzes": 5, "icon": "🚀"},
    4: {"name": "شارەزا", "min_score": 60, "max_score": 89, "color": "#ff9f1c", "quizzes": 5, "icon": "🏆"},
    5: {"name": "پزیشک", "min_score": 90, "max_score": 100, "color": "#dc3545", "quizzes": 5, "icon": "👨‍⚕️"}
}

# ================================
# سیستەمی فایل و لۆگین
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
# فانکشنە یارمەتیدەرەکان
# ================================
def get_risk_color(risk_level: str) -> str:
    colors = {"زۆر مەترسیدار": "#ff6b6b", "مەترسیدار": "#ffd93d", "مامناوەند": "#ffc107", "کەم": "#6bcb77"}
    return colors.get(risk_level, "#6c757d")

def get_user_level(score: int) -> int:
    for level, info in LEVELS.items():
        if info["min_score"] <= score <= info["max_score"]:
            return level
    return 1

def get_level_info(level: int) -> Dict:
    return LEVELS.get(level, LEVELS[1])

def analyze_lab_result(test_name: str, value: float) -> Dict:
    if test_name not in LAB_TESTS:
        return {"status": "نەزانراو", "color": "#6c757d"}
    low, high = LAB_TESTS[test_name]["نۆرماڵ"]
    if value < low:
        return {"status": "نزم", "color": "#ffc107"}
    elif value > high:
        return {"status": "بەرز", "color": "#dc3545"}
    else:
        return {"status": "نۆرماڵ", "color": "#28a745"}

# ================================
# ئەپی سەرەکی Flet
# ================================
def main(page: ft.Page):
    page.title = "Dr.Danyal - ڕاهێنەری پزیشکی Pro Max"
    page.window_width = 1400
    page.window_height = 900
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.bgcolor = "#0f0c29"
    page.fonts = {"NotoNaskhArabic": "https://fonts.googleapis.com/css2?family=Noto+Naskh+Arabic"}

    # ستەیتی ئەپ
    logged_in = False
    username = ""
    current_page = "login"
    custom_lab_tests = {}
    custom_drugs = {}
    quiz_score = 0
    quiz_index = 0
    total_cases_solved = 0
    correct_diagnoses = 0
    streak_days = 0
    study_time = 0
    achievements = []
    student_level = "ساڵی یەکەم"
    current_case = None

    # ================================
    # پەڕەی لۆگین
    # ================================
    def create_login_page():
        login_username = ft.TextField(
            label="ناوی بەکارهێنەری",
            prefix_icon=ft.icons.PERSON,
            border_radius=15,
            bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE),
            color=ft.colors.WHITE,
            width=350
        )
        login_password = ft.TextField(
            label="وشەی نهێنی",
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.icons.LOCK,
            border_radius=15,
            bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE),
            color=ft.colors.WHITE,
            width=350
        )
        login_error = ft.Text(color=ft.colors.RED_400)
        
        reg_username = ft.TextField(
            label="ناوی بەکارهێنەری نوێ",
            prefix_icon=ft.icons.PERSON,
            border_radius=15,
            bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE),
            color=ft.colors.WHITE,
            width=350
        )
        reg_password = ft.TextField(
            label="وشەی نهێنی",
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.icons.LOCK,
            border_radius=15,
            bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE),
            color=ft.colors.WHITE,
            width=350
        )
        reg_confirm = ft.TextField(
            label="دووبارە وشەی نهێنی",
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.icons.LOCK,
            border_radius=15,
            bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE),
            color=ft.colors.WHITE,
            width=350
        )
        reg_error = ft.Text(color=ft.colors.RED_400)
        reg_success = ft.Text(color=ft.colors.GREEN_400)

        def handle_login(e):
            nonlocal logged_in, username, custom_lab_tests, custom_drugs
            if authenticate_user(login_username.value, login_password.value):
                logged_in = True
                username = login_username.value
                user_data = load_user_data(username)
                custom_lab_tests = user_data.get("custom_lab_tests", {})
                custom_drugs = user_data.get("custom_drugs", {})
                page.go("/dashboard")
            else:
                login_error.value = "❌ ناوی بەکارهێنەری یان وشەی نهێنی هەڵەیە"
                login_error.update()

        def handle_register(e):
            if not reg_username.value or not reg_password.value:
                reg_error.value = "تکایە هەموو خانەکان پڕ بکەرەوە"
            elif reg_password.value != reg_confirm.value:
                reg_error.value = "وشەی نهێنی یەک ناگرنەوە"
            elif len(reg_password.value) < 4:
                reg_error.value = "وشەی نهێنی پێویستە لانیکەم ٤ پیت بێت"
            else:
                if create_user(reg_username.value, reg_password.value):
                    reg_success.value = "✅ هەژمارەکەت بە سەرکەوتوویی دروست کرا!"
                    reg_error.value = ""
                else:
                    reg_error.value = "❌ ئەم ناوی بەکارهێنەرییە پێشتر بەکارهێنراوە"
                    reg_success.value = ""
            reg_error.update()
            reg_success.update()

        login_tab = ft.Tab(
            text="چوونە ژوورەوە",
            content=ft.Container(
                content=ft.Column([
                    login_username,
                    login_password,
                    login_error,
                    ft.ElevatedButton(
                        "🚪 چوونە ژوورەوە",
                        on_click=handle_login,
                        style=ft.ButtonStyle(
                            bgcolor=ft.colors.BLUE_600,
                            color=ft.colors.WHITE,
                            padding=20,
                            shape=ft.RoundedRectangleBorder(radius=15)
                        ),
                        width=350
                    )
                ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=30
            )
        )
        
        register_tab = ft.Tab(
            text="دروستکردنی هەژمار",
            content=ft.Container(
                content=ft.Column([
                    reg_username,
                    reg_password,
                    reg_confirm,
                    reg_error,
                    reg_success,
                    ft.ElevatedButton(
                        "📝 دروستکردنی هەژمار",
                        on_click=handle_register,
                        style=ft.ButtonStyle(
                            bgcolor=ft.colors.GREEN_600,
                            color=ft.colors.WHITE,
                            padding=20,
                            shape=ft.RoundedRectangleBorder(radius=15)
                        ),
                        width=350
                    )
                ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=30
            )
        )

        return ft.View(
            "/login",
            [
                ft.Container(
                    content=ft.Column([
                        ft.Text("🩺", size=80, text_align=ft.TextAlign.CENTER),
                        ft.Text("Dr.Danyal", size=40, weight=ft.FontWeight.BOLD, 
                               color=ft.colors.BLUE_400),
                        ft.Text("ڕاهێنەری پزیشکی Pro Max", color=ft.colors.GREY_400, size=16),
                        ft.Divider(height=30, color=ft.colors.TRANSPARENT),
                        ft.Tabs(
                            selected_index=0,
                            tabs=[login_tab, register_tab],
                            indicator_color=ft.colors.BLUE_400
                        )
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=40,
                    border_radius=30,
                    bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
                    blur=ft.Blur(20, 20),
                    border=ft.border.all(1, ft.colors.with_opacity(0.1, ft.colors.WHITE)),
                    width=500
                )
            ],
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            bgcolor="#0f0c29"
        )

    # ================================
    # پەڕەی داشبۆرد
    # ================================
    def create_dashboard_page():
        level = get_user_level(quiz_score)
        level_info = get_level_info(level)
        
        def logout(e):
            nonlocal logged_in, username
            if username:
                save_user_data(username, {
                    "custom_lab_tests": custom_lab_tests,
                    "custom_drugs": custom_drugs
                })
            logged_in = False
            username = ""
            page.go("/login")

        return ft.View(
            "/dashboard",
            [
                ft.AppBar(
                    title=ft.Text("Dr.Danyal", weight=ft.FontWeight.BOLD),
                    bgcolor=ft.colors.with_opacity(0.1, "#667eea"),
                    actions=[
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(ft.icons.PERSON, color=ft.colors.WHITE70),
                                ft.Text(username, color=ft.colors.WHITE),
                                ft.Text(" | ", color=ft.colors.WHITE24),
                                ft.Text(level_info["name"], color=ft.colors.BLUE_200),
                            ]),
                            margin=ft.margin.only(right=10)
                        ),
                        ft.TextButton(
                            "چوونە دەرەوە",
                            on_click=logout,
                            style=ft.ButtonStyle(color=ft.colors.RED_400)
                        )
                    ]
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text("🎓 ڕاهێنەری پزیشکی Pro Max", size=35, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                        ft.Text(f"ئاست: {level_info['icon']} {level_info['name']}", size=20, color=ft.colors.BLUE_200),
                        ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                        ft.Row([
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("📚", size=40),
                                    ft.Text(f"{len(DISEASE_DATABASE)}", size=30, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                                    ft.Text("نەخۆشی", color=ft.colors.GREY_400)
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                                padding=25,
                                border_radius=20,
                                bgcolor=ft.colors.with_opacity(0.1, ft.colors.BLUE),
                                width=200,
                                height=150
                            ),
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("💊", size=40),
                                    ft.Text(f"{sum(len(v) for v in DRUG_DATABASE.values()) + len(custom_drugs)}", size=30, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                                    ft.Text("دەرمان", color=ft.colors.GREY_400)
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                                padding=25,
                                border_radius=20,
                                bgcolor=ft.colors.with_opacity(0.1, ft.colors.PURPLE),
                                width=200,
                                height=150
                            ),
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("📝", size=40),
                                    ft.Text(f"{quiz_score}/100", size=30, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                                    ft.Text("کویز", color=ft.colors.GREY_400)
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                                padding=25,
                                border_radius=20,
                                bgcolor=ft.colors.with_opacity(0.1, ft.colors.GREEN),
                                width=200,
                                height=150
                            ),
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("🔬", size=40),
                                    ft.Text(f"{len(LAB_TESTS) + len(custom_lab_tests)}", size=30, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                                    ft.Text("پشکنین", color=ft.colors.GREY_400)
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                                padding=25,
                                border_radius=20,
                                bgcolor=ft.colors.with_opacity(0.1, ft.colors.ORANGE),
                                width=200,
                                height=150
                            )
                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
                        ft.Divider(height=30, color=ft.colors.TRANSPARENT),
                        ft.Container(
                            content=ft.Column([
                                ft.Text("🔥 چالاکییەکان", size=20, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                                ft.Text(f"کەیسەکان: {total_cases_solved}", color=ft.colors.GREY_400),
                                ft.Text(f"بەردەوامی: {streak_days} ڕۆژ", color=ft.colors.GREY_400),
                                ft.Text(f"کاتی خوێندن: {study_time} خولەک", color=ft.colors.GREY_400),
                            ]),
                            padding=20,
                            border_radius=15,
                            bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
                            border=ft.border.all(1, ft.colors.with_opacity(0.1, ft.colors.WHITE))
                        )
                    ], spacing=10),
                    padding=30,
                    border_radius=25,
                    bgcolor=ft.colors.with_opacity(0.03, ft.colors.WHITE),
                    blur=ft.Blur(20, 20),
                    border=ft.border.all(1, ft.colors.with_opacity(0.05, ft.colors.WHITE)),
                    expand=True
                )
            ],
            bgcolor="#0f0c29",
            padding=20
        )

    # ================================
    # پەڕەی نەخۆشییەکان
    # ================================
    def create_diseases_page():
        search_field = ft.TextField(
            label="🔍 گەڕان",
            border_radius=15,
            bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE),
            color=ft.colors.WHITE,
            on_change=lambda e: filter_diseases()
        )
        
        disease_container = ft.ListView(spacing=15, padding=10, expand=True)
        
        def filter_diseases():
            disease_container.controls.clear()
            search_text = search_field.value.lower() if search_field.value else ""
            
            for disease, info in DISEASE_DATABASE.items():
                if search_text and search_text not in disease.lower():
                    continue
                    
                disease_container.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text("🩺", size=25),
                                ft.Text(disease, size=20, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE)
                            ]),
                            ft.Row([
                                ft.Container(
                                    ft.Text(info.get('جۆری نەخۆشی', ''), size=12, color=ft.colors.WHITE),
                                    padding=ft.padding.symmetric(horizontal=10, vertical=5),
                                    border_radius=15,
                                    bgcolor=ft.colors.with_opacity(0.2, ft.colors.BLUE)
                                ),
                                ft.Container(
                                    ft.Text(info.get('ئاستی مەترسی', ''), size=12, color=get_risk_color(info.get('ئاستی مەترسی', ''))),
                                    padding=ft.padding.symmetric(horizontal=10, vertical=5),
                                    border_radius=15,
                                    bgcolor=ft.colors.with_opacity(0.2, ft.colors.RED)
                                )
                            ], spacing=10),
                            ft.Text("نیشانە سەرەکییەکان:", color=ft.colors.GREY_400, size=14),
                            ft.Text(", ".join(info.get('نیشانەکان', [])[:4]), color=ft.colors.GREY_300, size=14),
                            ft.Text("چارەسەر:", color=ft.colors.GREY_400, size=14),
                            ft.Text(" • ".join(info.get('چارەسەر', [])[:3]), color=ft.colors.GREY_300, size=14),
                        ], spacing=8),
                        padding=20,
                        border_radius=20,
                        bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
                        border=ft.border.only(left=ft.BorderSide(6, ft.colors.BLUE_600)),
                    )
                )
            disease_container.update()
        
        filter_diseases()
        
        return ft.View(
            "/diseases",
            [
                ft.AppBar(
                    title=ft.Text("📚 کتێبخانەی نەخۆشییەکان"),
                    bgcolor=ft.colors.with_opacity(0.1, "#667eea")
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text(f"کۆی گشتی: {len(DISEASE_DATABASE)} نەخۆشی", color=ft.colors.GREY_400, size=16),
                        search_field,
                        disease_container
                    ]),
                    padding=20,
                    expand=True
                )
            ],
            bgcolor="#0f0c29",
            padding=20
        )

    # ================================
    # پەڕەی شیکاری کەیس
    # ================================
    def create_cases_page():
        case_container = ft.Container(
            content=ft.Text("کلیک لەسەر دوگمەکە بکە بۆ دروستکردنی کەیسێکی نوێ", color=ft.colors.GREY_400),
            padding=25,
            border_radius=20,
            bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
            border=ft.border.only(left=ft.BorderSide(6, ft.colors.BLUE_600))
        )
        
        diagnosis_dropdown = ft.Dropdown(
            label="دەستنیشانکردن هەڵبژێرە",
            options=[ft.dropdown.Option(d) for d in DISEASE_DATABASE.keys()],
            border_radius=15,
            bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE),
            color=ft.colors.WHITE,
            visible=False
        )
        
        submit_btn = ft.ElevatedButton(
            "✅ پشتڕاستکردنەوە",
            visible=False,
            style=ft.ButtonStyle(bgcolor=ft.colors.BLUE_600, color=ft.colors.WHITE)
        )
        
        result_text = ft.Text("", size=18, color=ft.colors.WHITE)
        
        def generate_case(e):
            nonlocal current_case
            disease = random.choice(list(DISEASE_DATABASE.keys()))
            info = DISEASE_DATABASE[disease]
            age = random.randint(18, 80)
            gender = random.choice(['نێر', 'مێ'])
            symptoms = random.sample(info['نیشانەکان'], min(5, len(info['نیشانەکان'])))
            
            current_case = {
                "disease": disease,
                "info": info,
                "age": age,
                "gender": gender,
                "symptoms": symptoms
            }
            
            case_container.content = ft.Column([
                ft.Text("📋 کەیسی نوێ", size=22, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                ft.Text(f"تەمەن: {age} ساڵ", color=ft.colors.GREY_300),
                ft.Text(f"ڕەگەز: {gender}", color=ft.colors.GREY_300),
                ft.Text("نیشانەکان:", color=ft.colors.GREY_400, size=14),
                ft.Text(", ".join(symptoms), color=ft.colors.WHITE, size=16),
                ft.Text(f"ئاستی مەترسی: {info['ئاستی مەترسی']}", color=get_risk_color(info['ئاستی مەترسی']))
            ])
            
            diagnosis_dropdown.visible = True
            submit_btn.visible = True
            result_text.value = ""
            
            diagnosis_dropdown.update()
            submit_btn.update()
            result_text.update()
            case_container.update()
        
        def check_diagnosis(e):
            nonlocal total_cases_solved, correct_diagnoses, study_time
            if current_case and diagnosis_dropdown.value:
                total_cases_solved += 1
                study_time += 3
                
                if diagnosis_dropdown.value == current_case["disease"]:
                    correct_diagnoses += 1
                    result_text.value = "🎉 ڕاستە! دەستنیشانکردنەکەت ڕاستە!"
                    result_text.color = ft.colors.GREEN_400
                else:
                    result_text.value = f"❌ هەڵەیە. دەستنیشانکردنی ڕاست: {current_case['disease']}"
                    result_text.color = ft.colors.RED_400
                
                result_text.update()
        
        generate_btn = ft.ElevatedButton(
            "🔄 کەیسی نوێ",
            on_click=generate_case,
            style=ft.ButtonStyle(bgcolor=ft.colors.BLUE_600, color=ft.colors.WHITE)
        )
        
        submit_btn.on_click = check_diagnosis
        
        return ft.View(
            "/cases",
            [
                ft.AppBar(
                    title=ft.Text("🩺 شیکاری کەیس"),
                    bgcolor=ft.colors.with_opacity(0.1, "#667eea")
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Row([generate_btn], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                        case_container,
                        ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                        diagnosis_dropdown,
                        ft.Row([submit_btn], alignment=ft.MainAxisAlignment.CENTER),
                        result_text
                    ], spacing=15),
                    padding=20,
                    expand=True
                )
            ],
            bgcolor="#0f0c29",
            padding=20
        )

    # ================================
    # پەڕەی کویز
    # ================================
    def create_quiz_page():
        quiz_question = ft.Text("", size=22, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE)
        options_group = ft.RadioGroup(content=ft.Column([]))
        result_text = ft.Text("", size=16, color=ft.colors.WHITE)
        explanation_text = ft.Text("", size=14, color=ft.colors.GREY_400)
        progress_text = ft.Text("", color=ft.colors.GREY_400)
        
        def load_next_quiz():
            nonlocal quiz_index
            if quiz_index < len(MEDICAL_QUIZZES):
                q = MEDICAL_QUIZZES[quiz_index]
                quiz_question.value = q["پرسیار"]
                options_group.content = [
                    ft.Radio(value=str(i), label=opt) 
                    for i, opt in enumerate(q["هەڵبژاردەکان"])
                ]
                options_group.value = None
                result_text.value = ""
                explanation_text.value = ""
                progress_text.value = f"کویزی {quiz_index + 1} لە {len(MEDICAL_QUIZZES)}"
            else:
                quiz_question.value = "🎊 پیرۆزە! هەموو کویزەکانت تەواو کرد!"
                options_group.content = []
                progress_text.value = f"نمرەی کۆتایی: {quiz_score}/{len(MEDICAL_QUIZZES)}"
            
            quiz_question.update()
            options_group.update()
            result_text.update()
            explanation_text.update()
            progress_text.update()
        
        def check_answer(e):
            nonlocal quiz_score, quiz_index, study_time
            if quiz_index < len(MEDICAL_QUIZZES) and options_group.value is not None:
                q = MEDICAL_QUIZZES[quiz_index]
                selected = int(options_group.value)
                study_time += 2
                
                if selected == q["وەڵامی ڕاست"]:
                    quiz_score += 1
                    result_text.value = "🎉 ڕاستە!"
                    result_text.color = ft.colors.GREEN_400
                else:
                    result_text.value = f"❌ هەڵەیە"
                    result_text.color = ft.colors.RED_400
                
                explanation_text.value = f"📚 ڕوونکردنەوە: {q['ڕوونکردنەوە']}"
                quiz_index += 1
                
                result_text.update()
                explanation_text.update()
        
        load_quiz_btn = ft.ElevatedButton(
            "کویزی داهاتوو ➡️",
            on_click=lambda e: load_next_quiz(),
            style=ft.ButtonStyle(bgcolor=ft.colors.BLUE_600, color=ft.colors.WHITE)
        )
        
        check_btn = ft.ElevatedButton(
            "✅ پشتڕاستکردنەوە",
            on_click=check_answer,
            style=ft.ButtonStyle(bgcolor=ft.colors.GREEN_600, color=ft.colors.WHITE)
        )
        
        reset_btn = ft.ElevatedButton(
            "🔄 ڕیسێت",
            on_click=lambda e: [setattr(None, 'quiz_index', 0), setattr(None, 'quiz_score', 0), load_next_quiz()][-1] if False else (
                globals().update(quiz_index=0, quiz_score=0) or load_next_quiz()
            ),
            style=ft.ButtonStyle(bgcolor=ft.colors.ORANGE_600, color=ft.colors.WHITE)
        )
        
        load_next_quiz()
        
        return ft.View(
            "/quiz",
            [
                ft.AppBar(
                    title=ft.Text("📝 کویزی پزیشکی"),
                    bgcolor=ft.colors.with_opacity(0.1, "#667eea")
                ),
                ft.Container(
                    content=ft.Column([
                        progress_text,
                        ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                        ft.Container(
                            content=quiz_question,
                            padding=20,
                            border_radius=15,
                            bgcolor=ft.colors.with_opacity(0.08, ft.colors.WHITE)
                        ),
                        options_group,
                        ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                        ft.Row([check_btn, load_quiz_btn, reset_btn], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
                        result_text,
                        explanation_text
                    ], spacing=10),
                    padding=20,
                    expand=True
                )
            ],
            bgcolor="#0f0c29",
            padding=20
        )

    # ================================
    # پەڕەی تاقیگە
    # ================================
    def create_lab_page():
        all_tests = {**LAB_TESTS, **custom_lab_tests}
        
        search_field = ft.TextField(
            label="🔍 گەڕان",
            border_radius=15,
            bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE),
            color=ft.colors.WHITE
        )
        
        lab_list = ft.ListView(spacing=10, padding=10, expand=True)
        
        def filter_labs(e=None):
            lab_list.controls.clear()
            search = search_field.value.lower() if search_field.value else ""
            
            for test_name, test_info in all_tests.items():
                if search and search not in test_name.lower():
                    continue
                
                low, high = test_info["نۆرماڵ"]
                lab_list.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text(test_name, size=16, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                            ft.Text(f"گروپ: {test_info.get('گروپ', '')} | ئامێر: {test_info.get('ئامێر', '')}", size=12, color=ft.colors.GREY_400),
                            ft.Text(f"نۆرماڵ: {low} - {high} {test_info.get('یەکە', '')}", color=ft.colors.GREY_300),
                            ft.Text(test_info.get('تەفسیر', ''), size=14, color=ft.colors.GREY_400)
                        ], spacing=5),
                        padding=15,
                        border_radius=15,
                        bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
                        border=ft.border.only(left=ft.BorderSide(4, ft.colors.GREEN_600))
                    )
                )
            lab_list.update()
        
        search_field.on_change = filter_labs
        filter_labs()
        
        # فۆرمی زیادکردنی پشکنین
        new_test_name = ft.TextField(label="ناوی پشکنین", border_radius=10, bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE), color=ft.colors.WHITE)
        new_test_group = ft.Dropdown(label="گروپ", options=[ft.dropdown.Option(g) for g in ["گشتی", "خوێن", "بایۆکیمیایی", "دڵ", "هەوکردن", "هۆرمۆن"]], border_radius=10, bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE), color=ft.colors.WHITE)
        new_test_low = ft.TextField(label="نزمترین", border_radius=10, bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE), color=ft.colors.WHITE, width=100)
        new_test_high = ft.TextField(label="بەرزترین", border_radius=10, bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE), color=ft.colors.WHITE, width=100)
        new_test_unit = ft.TextField(label="یەکە", border_radius=10, bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE), color=ft.colors.WHITE)
        
        def add_test(e):
            if new_test_name.value:
                custom_lab_tests[new_test_name.value] = {
                    "گروپ": new_test_group.value or "گشتی",
                    "نۆرماڵ": (float(new_test_low.value or 0), float(new_test_high.value or 10)),
                    "یەکە": new_test_unit.value or "",
                    "تەفسیر": "",
                    "ئامێر": "",
                    "تێبینی": ""
                }
                save_user_data(username, {"custom_lab_tests": custom_lab_tests, "custom_drugs": custom_drugs})
                filter_labs()
                new_test_name.value = ""
                new_test_name.update()
        
        return ft.View(
            "/lab",
            [
                ft.AppBar(title=ft.Text("🔬 تاقیگە"), bgcolor=ft.colors.with_opacity(0.1, "#667eea")),
                ft.Container(
                    content=ft.Column([
                        ft.Text(f"کۆی پشکنینەکان: {len(all_tests)}", color=ft.colors.GREY_400),
                        search_field,
                        lab_list,
                        ft.Divider(height=20),
                        ft.Text("➕ زیادکردنی پشکنینی نوێ", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                        ft.Row([new_test_name, new_test_group]),
                        ft.Row([new_test_low, new_test_high, new_test_unit]),
                        ft.ElevatedButton("زیاد بکە", on_click=add_test)
                    ]),
                    padding=20,
                    expand=True
                )
            ],
            bgcolor="#0f0c29",
            padding=20
        )

    # ================================
    # پەڕەی فارماکۆلۆجی
    # ================================
    def create_pharmacy_page():
        all_drugs = {**{k: v for cat in DRUG_DATABASE.values() for k, v in cat.items()}, **custom_drugs}
        
        search_field = ft.TextField(
            label="🔍 گەڕان",
            border_radius=15,
            bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE),
            color=ft.colors.WHITE
        )
        
        drug_list = ft.ListView(spacing=10, padding=10, expand=True)
        
        def filter_drugs(e=None):
            drug_list.controls.clear()
            search = search_field.value.lower() if search_field.value else ""
            
            for drug_name, drug_info in all_drugs.items():
                if search and search not in drug_name.lower():
                    continue
                
                drug_list.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text(f"💊 {drug_name}", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                            ft.Text(f"ڕێژە: {drug_info.get('ڕێژە', '')}", color=ft.colors.GREY_300),
                            ft.Text(f"میکانیزم: {drug_info.get('میکانیزم', '')}", color=ft.colors.GREY_300),
                            ft.Text(f"کاریگەری لاوەکی: {drug_info.get('کاریگەری لاوەکی', '')}", color=ft.colors.RED_300),
                        ], spacing=5),
                        padding=15,
                        border_radius=15,
                        bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
                        border=ft.border.only(left=ft.BorderSide(4, ft.colors.PURPLE_600))
                    )
                )
            drug_list.update()
        
        search_field.on_change = filter_drugs
        filter_drugs()
        
        return ft.View(
            "/pharmacy",
            [
                ft.AppBar(title=ft.Text("💊 فارماکۆلۆجی"), bgcolor=ft.colors.with_opacity(0.1, "#667eea")),
                ft.Container(
                    content=ft.Column([
                        ft.Text(f"کۆی دەرمانەکان: {len(all_drugs)}", color=ft.colors.GREY_400),
                        search_field,
                        drug_list
                    ]),
                    padding=20,
                    expand=True
                )
            ],
            bgcolor="#0f0c29",
            padding=20
        )

    # ================================
    # پەڕەی AI
    # ================================
    def create_ai_page():
        symptoms_input = ft.TextField(
            label="🩺 نیشانەکان بنووسە (بە کۆما جیا بکەرەوە)",
            multiline=True,
            min_lines=4,
            border_radius=15,
            bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE),
            color=ft.colors.WHITE
        )
        
        ai_result = ft.ListView(spacing=10, expand=True)
        
        def analyze(e):
            ai_result.controls.clear()
            if symptoms_input.value:
                symptoms = [s.strip() for s in symptoms_input.value.split(',')]
                results = []
                
                for disease, info in DISEASE_DATABASE.items():
                    match = len(set(symptoms).intersection(set(info['نیشانەکان'])))
                    if match > 0:
                        pct = (match / len(info['نیشانەکان'])) * 100
                        results.append((disease, pct, info))
                
                results.sort(key=lambda x: x[1], reverse=True)
                
                for disease, pct, info in results[:5]:
                    ai_result.controls.append(
                        ft.Container(
                            content=ft.Column([
                                ft.Text(f"🩺 {disease}", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                                ft.Text(f"ڕێژەی گونجاندن: {pct:.1f}%", color=ft.colors.GREEN_400),
                                ft.Text(f"ئاستی مەترسی: {info.get('ئاستی مەترسی', '')}", color=get_risk_color(info.get('ئاستی مەترسی', ''))),
                                ft.Text(f"چارەسەر: {'، '.join(info.get('چارەسەر', [])[:3])}", color=ft.colors.GREY_300)
                            ]),
                            padding=15,
                            border_radius=15,
                            bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
                            border=ft.border.only(left=ft.BorderSide(4, ft.colors.BLUE_600))
                        )
                    )
            ai_result.update()
        
        return ft.View(
            "/ai",
            [
                ft.AppBar(title=ft.Text("🧠 AI یاریدەدەر"), bgcolor=ft.colors.with_opacity(0.1, "#667eea")),
                ft.Container(
                    content=ft.Column([
                        symptoms_input,
                        ft.ElevatedButton(
                            "🔍 شیکاری بکە",
                            on_click=analyze,
                            style=ft.ButtonStyle(bgcolor=ft.colors.BLUE_600, color=ft.colors.WHITE)
                        ),
                        ft.Divider(height=20),
                        ai_result
                    ]),
                    padding=20,
                    expand=True
                )
            ],
            bgcolor="#0f0c29",
            padding=20
        )

    # ================================
    # پەڕەی پێشکەوتن
    # ================================
    def create_progress_page():
        level = get_user_level(quiz_score)
        level_info = get_level_info(level)
        
        achievement_list = ft.ListView(spacing=10, expand=True)
        
        all_achievements = [
            ("⭐ دەستنیشانکەری شارەزا", correct_diagnoses >= 5),
            ("📚 ڕاهێنەری پزیشکی", total_cases_solved >= 20),
            ("📝 شارەزای کویز", quiz_score >= 30),
            ("🎓 پزیشکی گشتی", quiz_score >= 50),
            ("👨‍⚕️ پزیشکی لێهاتوو", quiz_score >= 80),
            ("🔥 بەردەوامی ٧ ڕۆژ", streak_days >= 7),
        ]
        
        for ach_name, achieved in all_achievements:
            if achieved:
                achievement_list.controls.append(
                    ft.Container(
                        content=ft.Text(f"{ach_name} ✅", color=ft.colors.WHITE),
                        padding=15,
                        border_radius=15,
                        bgcolor=ft.colors.with_opacity(0.2, ft.colors.GREEN)
                    )
                )
            else:
                achievement_list.controls.append(
                    ft.Container(
                        content=ft.Text(f"{ach_name} 🔒", color=ft.colors.GREY_600),
                        padding=15,
                        border_radius=15,
                        bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE)
                    )
                )
        
        return ft.View(
            "/progress",
            [
                ft.AppBar(title=ft.Text("📊 پێشکەوتن"), bgcolor=ft.colors.with_opacity(0.1, "#667eea")),
                ft.Container(
                    content=ft.Column([
                        ft.Text(f"🏅 ئاست: {level_info['icon']} {level_info['name']}", size=24, color=ft.colors.WHITE),
                        ft.Text(f"📝 نمرەی کویز: {quiz_score}/100", color=ft.colors.GREY_300),
                        ft.Text(f"🩺 کەیسەکان: {total_cases_solved}", color=ft.colors.GREY_300),
                        ft.Text(f"🎯 دەقی: {int((correct_diagnoses / max(total_cases_solved, 1)) * 100)}%", color=ft.colors.GREY_300),
                        ft.Text(f"🔥 بەردەوامی: {streak_days} ڕۆژ", color=ft.colors.GREY_300),
                        ft.Text(f"⏱️ کاتی خوێندن: {study_time} خولەک", color=ft.colors.GREY_300),
                        ft.Divider(height=20),
                        ft.Text("🏆 دەستکەوتەکان", size=20, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                        achievement_list
                    ]),
                    padding=20,
                    expand=True
                )
            ],
            bgcolor="#0f0c29",
            padding=20
        )

    # ================================
    # ناوبەری سەرەکی (Navigation Rail)
    # ================================
    def create_rail():
        return ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=80,
            min_extended_width=200,
            group_alignment=-0.9,
            destinations=[
                ft.NavigationRailDestination(icon=ft.icons.DASHBOARD, label="داشبۆرد"),
                ft.NavigationRailDestination(icon=ft.icons.MEDICAL_SERVICES, label="نەخۆشی"),
                ft.NavigationRailDestination(icon=ft.icons.HEALING, label="کەیس"),
                ft.NavigationRailDestination(icon=ft.icons.QUIZ, label="کویز"),
                ft.NavigationRailDestination(icon=ft.icons.SCIENCE, label="تاقیگە"),
                ft.NavigationRailDestination(icon=ft.icons.MEDICATION, label="دەرمان"),
                ft.NavigationRailDestination(icon=ft.icons.PSYCHOLOGY, label="AI"),
                ft.NavigationRailDestination(icon=ft.icons.TRENDING_UP, label="پێشکەوتن"),
            ],
            on_change=lambda e: navigate(e.control.selected_index)
        )
    
    def navigate(index):
        routes = ["/dashboard", "/diseases", "/cases", "/quiz", "/lab", "/pharmacy", "/ai", "/progress"]
        if 0 <= index < len(routes):
            page.go(routes[index])

    # ================================
    # ڕێڕەوەکان
    # ================================
    def route_change(route):
        page.views.clear()
        
        if not logged_in:
            page.views.append(create_login_page())
        else:
            # هەموو پەڕەکان ناوبەری سەرەکیان هەیە
            rail = create_rail()
            
            if route == "/login":
                page.views.append(create_login_page())
            elif route == "/dashboard":
                page.views.append(create_dashboard_page())
            elif route == "/diseases":
                page.views.append(create_diseases_page())
            elif route == "/cases":
                page.views.append(create_cases_page())
            elif route == "/quiz":
                page.views.append(create_quiz_page())
            elif route == "/lab":
                page.views.append(create_lab_page())
            elif route == "/pharmacy":
                page.views.append(create_pharmacy_page())
            elif route == "/ai":
                page.views.append(create_ai_page())
            elif route == "/progress":
                page.views.append(create_progress_page())
            else:
                page.views.append(create_dashboard_page())
            
            # زیادکردنی ناوبەر بۆ هەموو پەڕەکان (جگە لە لۆگین)
            if page.views:
                last_view = page.views[-1]
                last_view.navigation_bar = ft.NavigationBar(
                    destinations=[
                        ft.NavigationBarDestination(icon=ft.icons.DASHBOARD, label="داشبۆرد"),
                        ft.NavigationBarDestination(icon=ft.icons.MEDICAL_SERVICES, label="نەخۆشی"),
                        ft.NavigationBarDestination(icon=ft.icons.HEALING, label="کەیس"),
                        ft.NavigationBarDestination(icon=ft.icons.QUIZ, label="کویز"),
                        ft.NavigationBarDestination(icon=ft.icons.SCIENCE, label="تاقیگە"),
                        ft.NavigationBarDestination(icon=ft.icons.MEDICATION, label="دەرمان"),
                        ft.NavigationBarDestination(icon=ft.icons.PSYCHOLOGY, label="AI"),
                        ft.NavigationBarDestination(icon=ft.icons.TRENDING_UP, label="پێشکەوتن"),
                    ],
                    on_change=lambda e: navigate(e.control.selected_index)
                )
    
    page.on_route_change = route_change
    page.go("/login")

# ================================
# ڕاکردنی ئەپ
# ================================
if __name__ == "__main__":
    ft.app(target=main)
