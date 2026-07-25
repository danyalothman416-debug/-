import flet as ft
import random
import json
import os
import hashlib
from datetime import datetime
from typing import Dict

# ================================
# داتابەیس
# ================================
DISEASE_DATABASE = {
    "شەکرەی جۆری 1": {
        "نیشانەکان": ["تینوویەتی زۆر", "میزی زۆر", "کێش کەمبوونەوە", "ماندوویی", "بینی تەڵخ"],
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
        "تایبەتمەندی": "FBS بەرز + HbA1c بەرز + تەمەن > 40 ساڵ",
        "گروپی تەمەن": "تەمەن مامناوەند و پیر",
        "ڕێژەی تووشبوون": "8.5%",
        "جۆری نەخۆشی": "مێتابۆلیک"
    },
    "پەستانی خوێنی سەرەتایی": {
        "نیشانەکان": ["سەرئێشە", "سەرگێژخواردن", "فشاری پشت چاو", "خێرالێدانی دڵ"],
        "پشکنینەکان": {"BP": ">140/90 mmHg"},
        "چارەسەر": ["کاپتۆپریل 25mg", "کەمکردنەوەی نمەک", "وەرزش"],
        "ئاستی مەترسی": "مامناوەند",
        "تایبەتمەندی": "BP بەرز بەبێ هۆکاری دیکە",
        "گروپی تەمەن": "هەموو تەمەنەکان",
        "ڕێژەی تووشبوون": "25%",
        "جۆری نەخۆشی": "دڵ و خوێن"
    },
    "نەخۆشی دڵی ئیسکیمیک": {
        "نیشانەکان": ["ئازاری سنگ", "کورتی هەناسە", "ئارەقەکردن", "سکچوون"],
        "پشکنینەکان": {"ECG": "ST depression", "Troponin": "بەرز >0.04"},
        "چارەسەر": ["ئەسپیرین 300mg", "نایترۆگلیسیرین", "ئۆکسجین"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندی": "ST changes + Troponin elevated",
        "گروپی تەمەن": "تەمەن > 50 ساڵ",
        "ڕێژەی تووشبوون": "7%",
        "جۆری نەخۆشی": "دڵ و خوێن"
    },
    "هەوکردنی سییەکان": {
        "نیشانەکان": ["تا", "کۆخە", "هەناسەدان بە زەحمەت", "ئازاری سنگ", "ماندوویی"],
        "پشکنینەکان": {"Chest X-ray": "Consolidation", "CRP": "بەرز >10"},
        "چارەسەر": ["ئەمۆکسیسیلین 500mg", "ئۆکسجین", "شلەمەنی"],
        "ئاستی مەترسی": "مامناوەند",
        "تایبەتمەندی": "Consolidation لە X-ray + CRP بەرز",
        "گروپی تەمەن": "هەموو تەمەنەکان",
        "ڕێژەی تووشبوون": "3%",
        "جۆری نەخۆشی": "هەوکردن"
    },
    "ئەنیمیا": {
        "نیشانەکان": ["ماندوویی", "ڕەنگی پێست زەرد", "سەرگێژخواردن", "لێدانی دڵ خێرا"],
        "پشکنینەکان": {"Hb": "<12 g/dL", "MCV": "<80 fL", "Ferritin": "نزم <15"},
        "چارەسەر": ["فێروس سولفەیت 325mg", "گۆڕینی خواردن", "ڤیتامین C"],
        "ئاستی مەترسی": "مامناوەند",
        "تایبەتمەندی": "Hb نزم + MCV نزم + Ferritin نزم",
        "گروپی تەمەن": "هەموو تەمەنەکان",
        "ڕێژەی تووشبوون": "25%",
        "جۆری نەخۆشی": "خوێن"
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
}

DRUG_DATABASE = {
    "دژە پەستانی خوێن": {
        "کاپتۆپریل": {"ڕێژە": "25-50mg", "میکانیزم": "ACE inhibitor", "کاریگەری لاوەکی": "کۆخە, سەرگێژخواردن"},
        "ئەملۆدیپین": {"ڕێژە": "5-10mg", "میکانیزم": "Calcium channel blocker", "کاریگەری لاوەکی": "ئاوسانی قاچ"}
    },
    "دژە شەکرە": {
        "مێتفۆرمین": {"ڕێژە": "500-2000mg", "میکانیزم": "Biguanide", "کاریگەری لاوەکی": "سکچوون"},
    },
    "دژە هەوکردن": {
        "ئەمۆکسیسیلین": {"ڕێژە": "500mg", "میکانیزم": "Beta-lactam", "کاریگەری لاوەکی": "زکچوون"},
    },
    "دژە ئەنیمیا": {
        "فێروس سولفەیت": {"ڕێژە": "300-600mg", "میکانیزم": "Iron", "کاریگەری لاوەکی": "سکچوون"},
    }
}

MEDICAL_QUIZZES = [
    {"پرسیار": "نیشانەی سەرەکی شەکرەی جۆری ٢ چییە؟", "هەڵبژاردەکان": ["تینوویەتی زۆر", "سەرئێشە", "ئازاری سنگ", "کۆخە"], "وەڵامی ڕاست": 0},
    {"پرسیار": "پەستانی خوێنی نۆرماڵ چەندە؟", "هەڵبژاردەکان": ["120/80", "140/90", "160/100", "180/110"], "وەڵامی ڕاست": 0},
    {"پرسیار": "کام دەرمانە بۆ شەکرە بەکاردێت؟", "هەڵبژاردەکان": ["مێتفۆرمین", "ئەسپیرین", "کاپتۆپریل", "ئەمۆکسیسیلین"], "وەڵامی ڕاست": 0},
    {"پرسیار": "نیشانەی ئەنیمیا چییە؟", "هەڵبژاردەکان": ["ماندوویی", "سەرئێشە", "ئازاری سنگ", "کۆخە"], "وەڵامی ڕاست": 0},
    {"پرسیار": "Troponin بەرز نیشانەی چییە؟", "هەڵبژاردەکان": ["نەخۆشی دڵ", "شەکرە", "هەوکردن", "ئەنیمیا"], "وەڵامی ڕاست": 0},
]

# ================================
# سیستەمی لۆگین
# ================================
DATA_DIR = "user_data"
os.makedirs(DATA_DIR, exist_ok=True)
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
        "created_at": datetime.now().isoformat()
    }
    save_users(users)
    return True

def authenticate_user(username: str, password: str) -> bool:
    users = load_users()
    if username in users:
        return users[username]["password"] == hash_password(password)
    return False

# ================================
# فانکشنە یارمەتیدەرەکان
# ================================
def get_risk_color(risk_level: str) -> str:
    colors = {
        "زۆر مەترسیدار": ft.colors.RED_400,
        "مەترسیدار": ft.colors.ORANGE_400,
        "مامناوەند": ft.colors.YELLOW_400,
        "کەم": ft.colors.GREEN_400
    }
    return colors.get(risk_level, ft.colors.GREY_400)

# ================================
# ئەپی سەرەکی
# ================================
def main(page: ft.Page):
    # ڕێکخستنی پەڕە
    page.title = "Dr.Danyal - ڕاهێنەری پزیشکی"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 1300
    page.window.height = 850
    page.window.min_width = 1000
    page.window.min_height = 700
    page.padding = 0
    
    # باکگراوندی گرادینت
    page.bgcolor = "#0f0c29"
    
    # ڤاریبڵەکانی ستەیت
    current_username = ""
    quiz_score = 0
    quiz_index = 0
    total_cases = 0
    correct_cases = 0
    
    # ================================
    # پەڕەی لۆگین
    # ================================
    def show_login():
        page.clean()
        
        username_field = ft.TextField(
            label="ناوی بەکارهێنەری",
            border_radius=15,
            bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE),
            color=ft.colors.WHITE,
            width=350
        )
        password_field = ft.TextField(
            label="وشەی نهێنی",
            password=True,
            can_reveal_password=True,
            border_radius=15,
            bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE),
            color=ft.colors.WHITE,
            width=350
        )
        login_error = ft.Text(color=ft.colors.RED_400)
        
        reg_username = ft.TextField(
            label="ناوی بەکارهێنەری نوێ",
            border_radius=15,
            bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE),
            color=ft.colors.WHITE,
            width=350
        )
        reg_password = ft.TextField(
            label="وشەی نهێنی",
            password=True,
            can_reveal_password=True,
            border_radius=15,
            bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE),
            color=ft.colors.WHITE,
            width=350
        )
        reg_confirm = ft.TextField(
            label="دووبارە وشەی نهێنی",
            password=True,
            can_reveal_password=True,
            border_radius=15,
            bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE),
            color=ft.colors.WHITE,
            width=350
        )
        reg_error = ft.Text(color=ft.colors.RED_400)
        reg_success = ft.Text(color=ft.colors.GREEN_400)
        
        def handle_login(e):
            nonlocal current_username
            if authenticate_user(username_field.value, password_field.value):
                current_username = username_field.value
                show_main_app()
            else:
                login_error.value = "❌ ناوی بەکارهێنەری یان وشەی نهێنی هەڵەیە"
                page.update()
        
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
            page.update()
        
        login_tab = ft.Tab(
            text="چوونە ژوورەوە",
            content=ft.Container(
                content=ft.Column([
                    username_field,
                    password_field,
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
        
        page.add(
            ft.Container(
                content=ft.Column([
                    ft.Text("🩺", size=80, text_align=ft.TextAlign.CENTER),
                    ft.Text("Dr.Danyal", size=45, weight=ft.FontWeight.BOLD, 
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
                width=500,
                alignment=ft.alignment.center
            ),
            ft.Container(expand=True, alignment=ft.alignment.center)
        )
        page.update()
    
    # ================================
    # ئەپی سەرەکی
    # ================================
    def show_main_app():
        page.clean()
        
        # کۆنتێنەری ناوەڕۆک
        content_container = ft.Container(
            expand=True,
            padding=25,
            border_radius=25,
            bgcolor=ft.colors.with_opacity(0.03, ft.colors.WHITE),
            blur=ft.Blur(20, 20),
            border=ft.border.all(1, ft.colors.with_opacity(0.05, ft.colors.WHITE))
        )
        
        # فەنکشنی گۆڕینی پەڕە
        def switch_page(page_name):
            if page_name == "dashboard":
                content_container.content = create_dashboard()
            elif page_name == "diseases":
                content_container.content = create_diseases_page()
            elif page_name == "cases":
                content_container.content = create_cases_page()
            elif page_name == "quiz":
                content_container.content = create_quiz_page()
            elif page_name == "lab":
                content_container.content = create_lab_page()
            elif page_name == "pharmacy":
                content_container.content = create_pharmacy_page()
            elif page_name == "ai":
                content_container.content = create_ai_page()
            elif page_name == "progress":
                content_container.content = create_progress_page()
            page.update()
        
        # ================================
        # پەڕەی داشبۆرد
        # ================================
        def create_dashboard():
            return ft.Column([
                ft.Text("🎓 ڕاهێنەری پزیشکی Pro Max", size=35, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                ft.Text(f"بەخێربێیت {current_username}!", size=20, color=ft.colors.GREY_400),
                ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                ft.Row([
                    create_stat_card("📚", str(len(DISEASE_DATABASE)), "نەخۆشی", ft.colors.BLUE),
                    create_stat_card("💊", str(sum(len(v) for v in DRUG_DATABASE.values())), "دەرمان", ft.colors.PURPLE),
                    create_stat_card("📝", f"{quiz_score}/100", "کویز", ft.colors.GREEN),
                    create_stat_card("🔬", str(len(LAB_TESTS)), "پشکنین", ft.colors.ORANGE)
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=20, wrap=True),
                ft.Divider(height=30, color=ft.colors.TRANSPARENT),
                ft.Container(
                    content=ft.Column([
                        ft.Text("🔥 چالاکییەکان", size=20, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                        ft.Text(f"کەیسەکان: {total_cases}", color=ft.colors.GREY_400),
                        ft.Text(f"ڕاستی: {correct_cases}", color=ft.colors.GREY_400),
                    ]),
                    padding=20,
                    border_radius=15,
                    bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE)
                )
            ], scroll=ft.ScrollMode.AUTO)
        
        def create_stat_card(icon, number, label, color):
            return ft.Container(
                content=ft.Column([
                    ft.Text(icon, size=40),
                    ft.Text(number, size=30, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                    ft.Text(label, color=ft.colors.GREY_400)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                padding=25,
                border_radius=20,
                bgcolor=ft.colors.with_opacity(0.1, color),
                width=200,
                height=150
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
            
            diseases_list = ft.ListView(spacing=10, expand=True)
            
            def filter_diseases():
                diseases_list.controls.clear()
                search = search_field.value.lower() if search_field.value else ""
                
                for disease, info in DISEASE_DATABASE.items():
                    if search and search not in disease.lower():
                        continue
                    
                    diseases_list.controls.append(
                        ft.Container(
                            content=ft.Column([
                                ft.Text(f"🩺 {disease}", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                                ft.Text(f"جۆر: {info.get('جۆری نەخۆشی', '')}", color=ft.colors.GREY_400, size=12),
                                ft.Text(f"مەترسی: {info.get('ئاستی مەترسی', '')}", color=get_risk_color(info.get('ئاستی مەترسی', '')), size=14),
                                ft.Text(f"نیشانەکان: {', '.join(info.get('نیشانەکان', [])[:3])}", color=ft.colors.GREY_300),
                                ft.Text(f"چارەسەر: {'، '.join(info.get('چارەسەر', [])[:2])}", color=ft.colors.GREY_300)
                            ], spacing=5),
                            padding=15,
                            border_radius=15,
                            bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
                            border=ft.border.only(left=ft.BorderSide(5, ft.colors.BLUE_600))
                        )
                    )
                page.update()
            
            filter_diseases()
            
            return ft.Column([
                ft.Text(f"📚 کتێبخانەی نەخۆشییەکان ({len(DISEASE_DATABASE)})", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                search_field,
                diseases_list
            ], expand=True)
        
        # ================================
        # پەڕەی کەیس
        # ================================
        def create_cases_page():
            case_text = ft.Text("کلیک بکە بۆ دروستکردنی کەیس", color=ft.colors.GREY_400, size=16)
            diagnosis_dd = ft.Dropdown(
                label="دەستنیشانکردن",
                options=[ft.dropdown.Option(d) for d in DISEASE_DATABASE.keys()],
                border_radius=15,
                bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE),
                color=ft.colors.WHITE,
                visible=False,
                width=400
            )
            result_text = ft.Text("", size=16)
            submit_btn = ft.ElevatedButton(
                "✅ پشتڕاستکردنەوە",
                visible=False,
                style=ft.ButtonStyle(bgcolor=ft.colors.GREEN_600, color=ft.colors.WHITE)
            )
            current_case_data = {"disease": ""}
            
            def generate_case(e):
                disease = random.choice(list(DISEASE_DATABASE.keys()))
                info = DISEASE_DATABASE[disease]
                age = random.randint(18, 80)
                gender = random.choice(['نێر', 'مێ'])
                symptoms = random.sample(info['نیشانەکان'], min(4, len(info['نیشانەکان'])))
                
                current_case_data["disease"] = disease
                case_text.value = f"تەمەن: {age} | ڕەگەز: {gender}\n\nنیشانەکان:\n• {'\n• '.join(symptoms)}\n\nمەترسی: {info['ئاستی مەترسی']}"
                diagnosis_dd.visible = True
                submit_btn.visible = True
                result_text.value = ""
                page.update()
            
            def check_diagnosis(e):
                nonlocal total_cases, correct_cases
                total_cases += 1
                if diagnosis_dd.value == current_case_data["disease"]:
                    correct_cases += 1
                    result_text.value = "✅ ڕاستە!"
                    result_text.color = ft.colors.GREEN_400
                else:
                    result_text.value = f"❌ هەڵە! ڕاست: {current_case_data['disease']}"
                    result_text.color = ft.colors.RED_400
                page.update()
            
            submit_btn.on_click = check_diagnosis
            
            return ft.Column([
                ft.Text("🩺 شیکاری کەیس", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                ft.ElevatedButton("🔄 کەیسی نوێ", on_click=generate_case, 
                                 style=ft.ButtonStyle(bgcolor=ft.colors.BLUE_600, color=ft.colors.WHITE)),
                ft.Divider(height=10, color=ft.colors.TRANSPARENT),
                ft.Container(
                    content=case_text,
                    padding=20,
                    border_radius=15,
                    bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
                    border=ft.border.only(left=ft.BorderSide(5, ft.colors.BLUE_600))
                ),
                diagnosis_dd,
                submit_btn,
                result_text
            ])
        
        # ================================
        # پەڕەی کویز
        # ================================
        def create_quiz_page():
            question_text = ft.Text("", size=20, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE)
            options_radio = ft.RadioGroup(content=ft.Column([]))
            result = ft.Text("", size=16)
            
            def load_quiz():
                nonlocal quiz_index
                if quiz_index < len(MEDICAL_QUIZZES):
                    q = MEDICAL_QUIZZES[quiz_index]
                    question_text.value = q["پرسیار"]
                    options_radio.content = [
                        ft.Radio(value=str(i), label=opt, fill_color=ft.colors.BLUE_400)
                        for i, opt in enumerate(q["هەڵبژاردەکان"])
                    ]
                    options_radio.value = None
                    result.value = ""
                else:
                    question_text.value = "🎊 پیرۆزە! هەموو کویزەکانت تەواو کرد!"
                    result.value = f"نمرەی کۆتایی: {quiz_score}/{len(MEDICAL_QUIZZES)}"
                    options_radio.content = []
                page.update()
            
            def check_answer(e):
                nonlocal quiz_score, quiz_index
                if quiz_index < len(MEDICAL_QUIZZES) and options_radio.value:
                    if int(options_radio.value) == MEDICAL_QUIZZES[quiz_index]["وەڵامی ڕاست"]:
                        quiz_score += 1
                        result.value = "🎉 ڕاستە!"
                        result.color = ft.colors.GREEN_400
                    else:
                        result.value = "❌ هەڵەیە"
                        result.color = ft.colors.RED_400
                    quiz_index += 1
                page.update()
            
            def next_quiz(e):
                load_quiz()
            
            load_quiz()
            
            return ft.Column([
                ft.Text("📝 کویزی پزیشکی", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                ft.Container(
                    content=question_text,
                    padding=20,
                    border_radius=15,
                    bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE)
                ),
                options_radio,
                ft.Row([
                    ft.ElevatedButton("✅ پشتڕاستکردنەوە", on_click=check_answer,
                                     style=ft.ButtonStyle(bgcolor=ft.colors.BLUE_600, color=ft.colors.WHITE)),
                    ft.ElevatedButton("➡️ داهاتوو", on_click=next_quiz,
                                     style=ft.ButtonStyle(bgcolor=ft.colors.GREEN_600, color=ft.colors.WHITE))
                ], spacing=20),
                result
            ])
        
        # ================================
        # پەڕەی تاقیگە
        # ================================
        def create_lab_page():
            labs_list = ft.ListView(spacing=10, expand=True)
            
            for test_name, test_info in LAB_TESTS.items():
                low, high = test_info["نۆرماڵ"]
                labs_list.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text(f"🧪 {test_name}", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                            ft.Text(f"گروپ: {test_info.get('گروپ', '')} | ئامێر: {test_info.get('ئامێر', '')}", 
                                   size=12, color=ft.colors.GREY_400),
                            ft.Text(f"نۆرماڵ: {low} - {high} {test_info.get('یەکە', '')}", 
                                   color=ft.colors.GREY_300),
                            ft.Text(f"تەفسیر: {test_info.get('تەفسیر', '')}", 
                                   color=ft.colors.GREY_400, size=14)
                        ], spacing=5),
                        padding=15,
                        border_radius=15,
                        bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
                        border=ft.border.only(left=ft.BorderSide(4, ft.colors.GREEN_600))
                    )
                )
            
            return ft.Column([
                ft.Text("🔬 تاقیگە", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                ft.Text(f"ژمارەی پشکنینەکان: {len(LAB_TESTS)}", color=ft.colors.GREY_400),
                labs_list
            ], expand=True)
        
        # ================================
        # پەڕەی فارماکۆلۆجی
        # ================================
        def create_pharmacy_page():
            drugs_list = ft.ListView(spacing=10, expand=True)
            
            for category, drugs in DRUG_DATABASE.items():
                drugs_list.controls.append(
                    ft.Text(f"📂 {category}", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE)
                )
                for drug_name, drug_info in drugs.items():
                    drugs_list.controls.append(
                        ft.Container(
                            content=ft.Column([
                                ft.Text(f"💊 {drug_name}", size=14, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                                ft.Text(f"ڕێژە: {drug_info.get('ڕێژە', '')}", color=ft.colors.GREY_300, size=12),
                                ft.Text(f"میکانیزم: {drug_info.get('میکانیزم', '')}", color=ft.colors.GREY_300, size=12),
                                ft.Text(f"کاریگەری لاوەکی: {drug_info.get('کاریگەری لاوەکی', '')}", 
                                       color=ft.colors.RED_300, size=12)
                            ], spacing=3),
                            padding=12,
                            border_radius=12,
                            bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
                            margin=ft.margin.only(left=20)
                        )
                    )
            
            return ft.Column([
                ft.Text("💊 فارماکۆلۆجی", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                drugs_list
            ], expand=True)
        
        # ================================
        # پەڕەی AI
        # ================================
        def create_ai_page():
            symptoms_field = ft.TextField(
                label="🩺 نیشانەکان بنووسە (بە کۆما جیا بکەرەوە)",
                multiline=True,
                min_lines=4,
                border_radius=15,
                bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE),
                color=ft.colors.WHITE
            )
            ai_results = ft.ListView(spacing=10, expand=True)
            
            def analyze(e):
                ai_results.controls.clear()
                if symptoms_field.value:
                    symptoms = [s.strip() for s in symptoms_field.value.split(',')]
                    results = []
                    
                    for disease, info in DISEASE_DATABASE.items():
                        match = len(set(symptoms).intersection(set(info['نیشانەکان'])))
                        if match > 0:
                            pct = (match / len(info['نیشانەکان'])) * 100
                            results.append((disease, pct, info))
                    
                    results.sort(key=lambda x: x[1], reverse=True)
                    
                    for disease, pct, info in results[:5]:
                        ai_results.controls.append(
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(f"🩺 {disease} - {pct:.1f}%", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                                    ft.Text(f"مەترسی: {info.get('ئاستی مەترسی', '')}", color=get_risk_color(info.get('ئاستی مەترسی', ''))),
                                    ft.Text(f"چارەسەر: {'، '.join(info.get('چارەسەر', [])[:3])}", color=ft.colors.GREY_300)
                                ]),
                                padding=15,
                                border_radius=15,
                                bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
                                border=ft.border.only(left=ft.BorderSide(4, ft.colors.BLUE_600))
                            )
                        )
                page.update()
            
            return ft.Column([
                ft.Text("🧠 AI یاریدەدەر", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                symptoms_field,
                ft.ElevatedButton("🔍 شیکاری", on_click=analyze,
                                 style=ft.ButtonStyle(bgcolor=ft.colors.BLUE_600, color=ft.colors.WHITE)),
                ft.Divider(height=10, color=ft.colors.TRANSPARENT),
                ai_results
            ], expand=True)
        
        # ================================
        # پەڕەی پێشکەوتن
        # ================================
        def create_progress_page():
            return ft.Column([
                ft.Text("📊 پێشکەوتن", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                ft.Text(f"نمرەی کویز: {quiz_score}/100", color=ft.colors.GREY_300, size=18),
                ft.Text(f"کەیسەکان: {total_cases}", color=ft.colors.GREY_300, size=18),
                ft.Text(f"ڕاستی: {correct_cases}", color=ft.colors.GREY_300, size=18),
                ft.Text(f"ڕێژەی ڕاستی: {int((correct_cases / max(total_cases, 1)) * 100)}%", color=ft.colors.GREY_300, size=18)
            ])
        
        # ================================
        # دروستکردنی سایدبار
        # ================================
        def create_sidebar():
            return ft.Container(
                content=ft.Column([
                    ft.Text("🩺", size=45, text_align=ft.TextAlign.CENTER),
                    ft.Text("Dr.Danyal", size=22, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_400, text_align=ft.TextAlign.CENTER),
                    ft.Text(f"👤 {current_username}", color=ft.colors.GREY_400, size=12, text_align=ft.TextAlign.CENTER),
                    ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                    
                    create_nav_button("🏠 داشبۆرد", "dashboard"),
                    create_nav_button("📚 نەخۆشییەکان", "diseases"),
                    create_nav_button("🩺 کەیس", "cases"),
                    create_nav_button("📝 کویز", "quiz"),
                    create_nav_button("🔬 تاقیگە", "lab"),
                    create_nav_button("💊 فارماکۆلۆجی", "pharmacy"),
                    create_nav_button("🧠 AI", "ai"),
                    create_nav_button("📊 پێشکەوتن", "progress"),
                    
                    ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                    ft.TextButton(
                        "🚪 چوونە دەرەوە",
                        on_click=lambda e: show_login(),
                        style=ft.ButtonStyle(color=ft.colors.RED_400)
                    )
                ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                width=250,
                padding=20,
                bgcolor="#16213e",
                border_radius=20
            )
        
        def create_nav_button(text, page_name):
            return ft.TextButton(
                text,
                on_click=lambda e, p=page_name: switch_page(p),
                style=ft.ButtonStyle(color=ft.colors.WHITE)
            )
        
        # دانانی پەڕەی سەرەکی
        switch_page("dashboard")
        
        # زیادکردنی هەموو شتێک
        page.add(
            ft.Row([
                create_sidebar(),
                ft.VerticalDivider(width=10, color=ft.colors.TRANSPARENT),
                content_container
            ], expand=True)
        )
        
        page.update()
    
    # دەستپێکردن بە پەڕەی لۆگین
    show_login()

# ڕاکردنی ئەپ
ft.app(target=main)
