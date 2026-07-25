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
        "نیشانەکان": ["تینوویەتی زۆر", "میزی زۆر", "کێش کەمبوونەوە", "ماندوویی"],
        "چارەسەر": ["ئەنسولین", "پێوانەکردنی شەکر"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
    },
    "شەکرەی جۆری 2": {
        "نیشانەکان": ["تینوویەتی زۆر", "میزی زۆر", "ماندوویی"],
        "چارەسەر": ["مێتفۆرمین", "وەرزش"],
        "ئاستی مەترسی": "مەترسیدار",
    },
    "پەستانی خوێن": {
        "نیشانەکان": ["سەرئێشە", "سەرگێژخواردن"],
        "چارەسەر": ["کاپتۆپریل", "کەمکردنەوەی نمەک"],
        "ئاستی مەترسی": "مامناوەند",
    },
    "نەخۆشی دڵ": {
        "نیشانەکان": ["ئازاری سنگ", "کورتی هەناسە"],
        "چارەسەر": ["ئەسپیرین", "نایترۆگلیسیرین"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
    },
    "هەوکردنی سییەکان": {
        "نیشانەکان": ["تا", "کۆخە", "هەناسەدان بە زەحمەت"],
        "چارەسەر": ["ئەمۆکسیسیلین", "ئۆکسجین"],
        "ئاستی مەترسی": "مامناوەند",
    }
}

LAB_TESTS = {
    "FBS": {"نۆرماڵ": "70-126", "یەکە": "mg/dL", "تەفسیر": "شەکری خوێن"},
    "HbA1c": {"نۆرماڵ": "4.0-5.6", "یەکە": "%", "تەفسیر": "شەکری درێژخایەن"},
    "Creatinine": {"نۆرماڵ": "0.6-1.3", "یەکە": "mg/dL", "تەفسیر": "کارایی گورچیلە"},
    "Hemoglobin": {"نۆرماڵ": "12-16", "یەکە": "g/dL", "تەفسیر": "هیمۆگلۆبین"},
}

DRUG_DATABASE = {
    "دژە پەستانی خوێن": {
        "کاپتۆپریل": {"ڕێژە": "25-50mg", "کاریگەری": "کۆخە"},
        "ئەملۆدیپین": {"ڕێژە": "5-10mg", "کاریگەری": "ئاوسان"}
    },
    "دژە شەکرە": {
        "مێتفۆرمین": {"ڕێژە": "500-2000mg", "کاریگەری": "سکچوون"},
    }
}

MEDICAL_QUIZZES = [
    {"پرسیار": "نیشانەی سەرەکی شەکرە چییە؟", "هەڵبژاردەکان": ["تینوویەتی زۆر", "سەرئێشە", "ئازاری سنگ", "کۆخە"], "وەڵامی ڕاست": 0},
    {"پرسیار": "پەستانی خوێنی نۆرماڵ چەندە؟", "هەڵبژاردەکان": ["120/80", "140/90", "160/100", "180/110"], "وەڵامی ڕاست": 0},
    {"پرسیار": "کام دەرمانە بۆ شەکرە؟", "هەڵبژاردەکان": ["مێتفۆرمین", "ئەسپیرین", "کاپتۆپریل", "ئەمۆکسیسیلین"], "وەڵامی ڕاست": 0},
    {"پرسیار": "نیشانەی ئەنیمیا چییە؟", "هەڵبژاردەکان": ["ماندوویی", "سەرئێشە", "ئازاری سنگ", "کۆخە"], "وەڵامی ڕاست": 0},
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
# ئەپی سەرەکی
# ================================
def main(page: ft.Page):
    page.title = "Dr.Danyal"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.bgcolor = "#0f0c29"
    
    # ستەیت
    current_username = ""
    quiz_score = 0
    quiz_index = 0
    total_cases = 0
    correct_cases = 0
    
    # ================================
    # دروستکردنی پەڕەی لۆگین
    # ================================
    def build_login_page():
        username_field = ft.TextField(
            label="ناوی بەکارهێنەری",
            border_radius=10,
            bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE),
            color=ft.colors.WHITE,
            width=350
        )
        password_field = ft.TextField(
            label="وشەی نهێنی",
            password=True,
            can_reveal_password=True,
            border_radius=10,
            bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE),
            color=ft.colors.WHITE,
            width=350
        )
        login_msg = ft.Text("", color=ft.colors.RED_400)
        
        reg_username = ft.TextField(
            label="ناوی بەکارهێنەری نوێ",
            border_radius=10,
            bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE),
            color=ft.colors.WHITE,
            width=350
        )
        reg_password = ft.TextField(
            label="وشەی نهێنی",
            password=True,
            can_reveal_password=True,
            border_radius=10,
            bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE),
            color=ft.colors.WHITE,
            width=350
        )
        reg_confirm = ft.TextField(
            label="دووبارە وشەی نهێنی",
            password=True,
            can_reveal_password=True,
            border_radius=10,
            bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE),
            color=ft.colors.WHITE,
            width=350
        )
        reg_msg = ft.Text("", color=ft.colors.RED_400)
        reg_success = ft.Text("", color=ft.colors.GREEN_400)
        
        def do_login(e):
            nonlocal current_username
            if authenticate_user(username_field.value, password_field.value):
                current_username = username_field.value
                build_main_app()
            else:
                login_msg.value = "❌ هەڵە"
                page.update()
        
        def do_register(e):
            if not reg_username.value or not reg_password.value:
                reg_msg.value = "هەموو خانەکان پڕ بکەرەوە"
            elif reg_password.value != reg_confirm.value:
                reg_msg.value = "وشەی نهێنی یەک ناگرنەوە"
            elif len(reg_password.value) < 4:
                reg_msg.value = "وشەی نهێنی کورتە"
            else:
                if create_user(reg_username.value, reg_password.value):
                    reg_success.value = "✅ دروست کرا!"
                    reg_msg.value = ""
                else:
                    reg_msg.value = "❌ پێشتر هەیە"
                    reg_success.value = ""
            page.update()
        
        login_tab = ft.Tab(
            text="چوونە ژوورەوە",
            content=ft.Container(
                content=ft.Column([
                    username_field,
                    password_field,
                    login_msg,
                    ft.ElevatedButton(
                        "🚪 چوونە ژوورەوە",
                        on_click=do_login,
                        style=ft.ButtonStyle(bgcolor=ft.colors.BLUE_600, color=ft.colors.WHITE, padding=15)
                    )
                ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=20
            )
        )
        
        register_tab = ft.Tab(
            text="دروستکردنی هەژمار",
            content=ft.Container(
                content=ft.Column([
                    reg_username,
                    reg_password,
                    reg_confirm,
                    reg_msg,
                    reg_success,
                    ft.ElevatedButton(
                        "📝 دروستکردن",
                        on_click=do_register,
                        style=ft.ButtonStyle(bgcolor=ft.colors.GREEN_600, color=ft.colors.WHITE, padding=15)
                    )
                ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=20
            )
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text("🩺", size=60, text_align=ft.TextAlign.CENTER),
                ft.Text("Dr.Danyal", size=40, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_400),
                ft.Text("ڕاهێنەری پزیشکی", color=ft.colors.GREY_400),
                ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                ft.Tabs(
                    selected_index=0,
                    tabs=[login_tab, register_tab],
                    indicator_color=ft.colors.BLUE_400
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=30,
            border_radius=25,
            bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
            border=ft.border.all(1, ft.colors.with_opacity(0.1, ft.colors.WHITE)),
            width=450,
            alignment=ft.alignment.center
        )
    
    # ================================
    # دروستکردنی ئەپی سەرەکی
    # ================================
    def build_main_app():
        page.clean()
        
        # کۆنتێنەری ناوەڕۆک
        content_area = ft.Container(
            expand=True,
            padding=25,
            border_radius=20,
            bgcolor=ft.colors.with_opacity(0.03, ft.colors.WHITE)
        )
        
        # فەنکشنی گۆڕینی پەڕە
        def switch_page(page_name):
            if page_name == "dashboard":
                content_area.content = build_dashboard()
            elif page_name == "diseases":
                content_area.content = build_diseases()
            elif page_name == "cases":
                content_area.content = build_cases()
            elif page_name == "quiz":
                content_area.content = build_quiz()
            elif page_name == "lab":
                content_area.content = build_lab()
            elif page_name == "drugs":
                content_area.content = build_drugs()
            elif page_name == "ai":
                content_area.content = build_ai()
            elif page_name == "progress":
                content_area.content = build_progress()
            page.update()
        
        # ================================
        # پەڕەکان
        # ================================
        def build_dashboard():
            return ft.Column([
                ft.Text("🎓 داشبۆرد", size=30, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                ft.Text(f"بەخێربێیت {current_username}!", color=ft.colors.GREY_400, size=18),
                ft.Divider(height=20),
                ft.Row([
                    ft.Container(
                        content=ft.Column([
                            ft.Text("📚", size=40),
                            ft.Text(str(len(DISEASE_DATABASE)), size=25, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                            ft.Text("نەخۆشی", color=ft.colors.GREY_400)
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=20,
                        border_radius=15,
                        bgcolor=ft.colors.with_opacity(0.1, ft.colors.BLUE),
                        width=180,
                        height=130
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("💊", size=40),
                            ft.Text(str(sum(len(v) for v in DRUG_DATABASE.values())), size=25, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                            ft.Text("دەرمان", color=ft.colors.GREY_400)
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=20,
                        border_radius=15,
                        bgcolor=ft.colors.with_opacity(0.1, ft.colors.PURPLE),
                        width=180,
                        height=130
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("📝", size=40),
                            ft.Text(f"{quiz_score}/{len(MEDICAL_QUIZZES)}", size=25, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                            ft.Text("کویز", color=ft.colors.GREY_400)
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=20,
                        border_radius=15,
                        bgcolor=ft.colors.with_opacity(0.1, ft.colors.GREEN),
                        width=180,
                        height=130
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("🔬", size=40),
                            ft.Text(str(len(LAB_TESTS)), size=25, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                            ft.Text("پشکنین", color=ft.colors.GREY_400)
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=20,
                        border_radius=15,
                        bgcolor=ft.colors.with_opacity(0.1, ft.colors.ORANGE),
                        width=180,
                        height=130
                    )
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=15, wrap=True),
                ft.Divider(height=20),
                ft.Text(f"کەیسەکان: {total_cases} | ڕاستی: {correct_cases}", color=ft.colors.GREY_400)
            ], scroll=ft.ScrollMode.AUTO)
        
        def build_diseases():
            search = ft.TextField(
                label="🔍 گەڕان",
                border_radius=10,
                bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE),
                color=ft.colors.WHITE,
                on_change=lambda e: filter_list()
            )
            d_list = ft.ListView(spacing=10, expand=True)
            
            def filter_list():
                d_list.controls.clear()
                s = search.value.lower() if search.value else ""
                for disease, info in DISEASE_DATABASE.items():
                    if s and s not in disease.lower():
                        continue
                    d_list.controls.append(
                        ft.Container(
                            content=ft.Column([
                                ft.Text(f"🩺 {disease}", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                                ft.Text(f"نیشانەکان: {', '.join(info.get('نیشانەکان', [])[:3])}", color=ft.colors.GREY_300, size=13),
                                ft.Text(f"چارەسەر: {', '.join(info.get('چارەسەر', [])[:2])}", color=ft.colors.GREY_400, size=13)
                            ], spacing=5),
                            padding=15,
                            border_radius=10,
                            bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
                            border=ft.border.only(left=ft.BorderSide(4, ft.colors.BLUE_400))
                        )
                    )
                page.update()
            
            filter_list()
            return ft.Column([
                ft.Text("📚 نەخۆشییەکان", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                search,
                d_list
            ], expand=True)
        
        def build_cases():
            case_text = ft.Text("کلیک بکە بۆ دروستکردنی کەیس", color=ft.colors.GREY_400)
            dd = ft.Dropdown(
                label="دەستنیشانکردن",
                options=[ft.dropdown.Option(d) for d in DISEASE_DATABASE.keys()],
                border_radius=10,
                bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE),
                color=ft.colors.WHITE,
                visible=False,
                width=350
            )
            result = ft.Text("", size=16)
            submit = ft.ElevatedButton("✅ پشتڕاستکردنەوە", visible=False)
            case_data = {"disease": ""}
            
            def gen(e):
                d = random.choice(list(DISEASE_DATABASE.keys()))
                info = DISEASE_DATABASE[d]
                age = random.randint(18, 80)
                gender = random.choice(['نێر', 'مێ'])
                symps = random.sample(info['نیشانەکان'], min(3, len(info['نیشانەکان'])))
                case_data["disease"] = d
                case_text.value = f"تەمەن: {age} | ڕەگەز: {gender}\n\nنیشانەکان:\n• {'\n• '.join(symps)}"
                dd.visible = True
                submit.visible = True
                result.value = ""
                page.update()
            
            def check(e):
                nonlocal total_cases, correct_cases
                total_cases += 1
                if dd.value == case_data["disease"]:
                    correct_cases += 1
                    result.value = "✅ ڕاستە!"
                    result.color = ft.colors.GREEN_400
                else:
                    result.value = f"❌ ڕاست: {case_data['disease']}"
                    result.color = ft.colors.RED_400
                page.update()
            
            submit.on_click = check
            
            return ft.Column([
                ft.Text("🩺 شیکاری کەیس", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                ft.ElevatedButton("🔄 کەیسی نوێ", on_click=gen, style=ft.ButtonStyle(bgcolor=ft.colors.BLUE_600, color=ft.colors.WHITE)),
                ft.Divider(height=10, color=ft.colors.TRANSPARENT),
                ft.Container(case_text, padding=15, border_radius=10, bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE)),
                dd,
                submit,
                result
            ])
        
        def build_quiz():
            q_text = ft.Text("", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE)
            opts = ft.RadioGroup(content=ft.Column([]))
            res = ft.Text("", size=16)
            
            def load():
                nonlocal quiz_index
                if quiz_index < len(MEDICAL_QUIZZES):
                    q = MEDICAL_QUIZZES[quiz_index]
                    q_text.value = q["پرسیار"]
                    opts.content = [ft.Radio(value=str(i), label=opt) for i, opt in enumerate(q["هەڵبژاردەکان"])]
                    opts.value = None
                    res.value = ""
                else:
                    q_text.value = "🎊 تەواو!"
                    res.value = f"نمرە: {quiz_score}/{len(MEDICAL_QUIZZES)}"
                    opts.content = []
                page.update()
            
            def check(e):
                nonlocal quiz_score, quiz_index
                if quiz_index < len(MEDICAL_QUIZZES) and opts.value:
                    if int(opts.value) == MEDICAL_QUIZZES[quiz_index]["وەڵامی ڕاست"]:
                        quiz_score += 1
                        res.value = "🎉 ڕاستە!"
                        res.color = ft.colors.GREEN_400
                    else:
                        res.value = "❌ هەڵەیە"
                        res.color = ft.colors.RED_400
                    quiz_index += 1
                page.update()
            
            load()
            
            return ft.Column([
                ft.Text("📝 کویز", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                ft.Container(q_text, padding=15, border_radius=10, bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE)),
                opts,
                ft.Row([
                    ft.ElevatedButton("✅ پشتڕاستکردنەوە", on_click=check),
                    ft.ElevatedButton("➡️ داهاتوو", on_click=lambda e: load())
                ]),
                res
            ])
        
        def build_lab():
            l_list = ft.ListView(spacing=10, expand=True)
            for name, info in LAB_TESTS.items():
                l_list.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text(f"🧪 {name}", size=14, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                            ft.Text(f"نۆرماڵ: {info['نۆرماڵ']} {info['یەکە']}", color=ft.colors.GREY_300, size=12)
                        ], spacing=3),
                        padding=12,
                        border_radius=10,
                        bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE)
                    )
                )
            return ft.Column([
                ft.Text("🔬 تاقیگە", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                l_list
            ], expand=True)
        
        def build_drugs():
            d_list = ft.ListView(spacing=10, expand=True)
            for cat, drugs in DRUG_DATABASE.items():
                d_list.controls.append(ft.Text(f"📂 {cat}", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE))
                for name, info in drugs.items():
                    d_list.controls.append(
                        ft.Container(
                            content=ft.Text(f"💊 {name} | {info['ڕێژە']}", color=ft.colors.GREY_300, size=13),
                            padding=8, margin=ft.margin.only(left=20)
                        )
                    )
            return ft.Column([
                ft.Text("💊 دەرمانەکان", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                d_list
            ], expand=True)
        
        def build_ai():
            symptoms = ft.TextField(
                label="🩺 نیشانەکان (بە کۆما جیا بکەرەوە)",
                multiline=True, min_lines=3,
                border_radius=10,
                bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE),
                color=ft.colors.WHITE
            )
            result_list = ft.ListView(spacing=10, expand=True)
            
            def analyze(e):
                result_list.controls.clear()
                if symptoms.value:
                    symps = [s.strip() for s in symptoms.value.split(',')]
                    results = []
                    for disease, info in DISEASE_DATABASE.items():
                        match = len(set(symps).intersection(set(info['نیشانەکان'])))
                        if match > 0:
                            results.append((disease, match / len(info['نیشانەکان']) * 100, info))
                    results.sort(key=lambda x: x[1], reverse=True)
                    
                    for d, p, info in results[:5]:
                        result_list.controls.append(
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(f"🩺 {d} - {p:.1f}%", size=14, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                                    ft.Text(f"چارەسەر: {', '.join(info['چارەسەر'][:2])}", color=ft.colors.GREY_300, size=12)
                                ]),
                                padding=12, border_radius=10,
                                bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE)
                            )
                        )
                page.update()
            
            return ft.Column([
                ft.Text("🧠 AI یاریدەدەر", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                symptoms,
                ft.ElevatedButton("🔍 شیکاری", on_click=analyze),
                result_list
            ], expand=True)
        
        def build_progress():
            return ft.Column([
                ft.Text("📊 پێشکەوتن", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                ft.Text(f"کویز: {quiz_score}/{len(MEDICAL_QUIZZES)}", color=ft.colors.GREY_300, size=16),
                ft.Text(f"کەیس: {total_cases}", color=ft.colors.GREY_300, size=16),
                ft.Text(f"ڕاستی: {correct_cases}", color=ft.colors.GREY_300, size=16)
            ])
        
        # ================================
        # سایدبار
        # ================================
        sidebar = ft.Container(
            content=ft.Column([
                ft.Text("🩺", size=40, text_align=ft.TextAlign.CENTER),
                ft.Text("Dr.Danyal", size=20, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_400, text_align=ft.TextAlign.CENTER),
                ft.Text(current_username, color=ft.colors.GREY_400, size=12, text_align=ft.TextAlign.CENTER),
                ft.Divider(height=15, color=ft.colors.TRANSPARENT),
                
                ft.TextButton("🏠 داشبۆرد", on_click=lambda e: switch_page("dashboard"), style=ft.ButtonStyle(color=ft.colors.WHITE)),
                ft.TextButton("📚 نەخۆشییەکان", on_click=lambda e: switch_page("diseases"), style=ft.ButtonStyle(color=ft.colors.WHITE)),
                ft.TextButton("🩺 کەیس", on_click=lambda e: switch_page("cases"), style=ft.ButtonStyle(color=ft.colors.WHITE)),
                ft.TextButton("📝 کویز", on_click=lambda e: switch_page("quiz"), style=ft.ButtonStyle(color=ft.colors.WHITE)),
                ft.TextButton("🔬 تاقیگە", on_click=lambda e: switch_page("lab"), style=ft.ButtonStyle(color=ft.colors.WHITE)),
                ft.TextButton("💊 دەرمان", on_click=lambda e: switch_page("drugs"), style=ft.ButtonStyle(color=ft.colors.WHITE)),
                ft.TextButton("🧠 AI", on_click=lambda e: switch_page("ai"), style=ft.ButtonStyle(color=ft.colors.WHITE)),
                ft.TextButton("📊 پێشکەوتن", on_click=lambda e: switch_page("progress"), style=ft.ButtonStyle(color=ft.colors.WHITE)),
                
                ft.Divider(height=15, color=ft.colors.TRANSPARENT),
                ft.TextButton("🚪 چوونە دەرەوە", on_click=lambda e: build_login_screen(), style=ft.ButtonStyle(color=ft.colors.RED_400))
            ], spacing=3, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            width=220,
            padding=15,
            bgcolor="#16213e",
            border_radius=15
        )
        
        # دانانی پەڕەی سەرەکی
        switch_page("dashboard")
        
        # زیادکردنی هەموو شتێک
        page.add(
            ft.Row([
                sidebar,
                ft.VerticalDivider(width=8, color=ft.colors.TRANSPARENT),
                content_area
            ], expand=True)
        )
        page.update()
    
    # ================================
    # دروستکردنی شاشەی لۆگین
    # ================================
    def build_login_screen():
        page.clean()
        login_page = build_login_page()
        page.add(
            ft.Container(
                content=login_page,
                alignment=ft.alignment.center,
                expand=True
            )
        )
        page.update()
    
    # دەستپێکردن
    build_login_screen()

# ڕاکردن
ft.app(target=main)
