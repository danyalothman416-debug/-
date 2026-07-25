import flet as ft
import hashlib
import json
import os

# ================================
# 1. سیستەمی خەزنکردنی داتا و لۆگین
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
        "custom_lab_tests": {},
        "custom_drugs": {}
    }
    save_users(users)
    return True

def authenticate_user(username: str, password: str) -> bool:
    users = load_users()
    return username in users and users[username]["password"] == hash_password(password)

def load_user_data(username: str) -> dict:
    users = load_users()
    return users.get(username, {"custom_lab_tests": {}, "custom_drugs": {}})

def save_user_data(username: str, data: dict):
    users = load_users()
    if username in users:
        users[username].update(data)
        save_users(users)

# ================================
# 2. داتابەسی بنەڕەتی (نموونە)
# ================================
DISEASE_DATABASE = {
    "شەکرەی جۆری 2": {"نیشانەکان": ["تینوویەتی زۆر", "ماندوویی"], "ئاستی مەترسی": "مەترسیدار", "چارەسەر": ["مێتفۆرمین"]},
    "پەستانی خوێنی بەرز": {"نیشانەکان": ["سەرئێشە"], "ئاستی مەترسی": "مامناوەند", "چارەسەر": ["کاپتۆپریل"]},
}

DEFAULT_LABS = {
    "CBC": {"نۆرماڵ": "4.0-11.0", "یەکە": "x10³/µL", "ئامێر": "سێل کاونتر"},
    "Glucose": {"نۆرماڵ": "70-126", "یەکە": "mg/dL", "ئامێر": "گلوکۆمیتەر"},
}

DEFAULT_DRUGS = {
    "مێتفۆرمین": {"ڕێژە": "500mg", "میکانیزم": "Biguanide", "بۆچی": "شەکرە"},
    "کاپتۆپریل": {"ڕێژە": "25mg", "میکانیزم": "ACE inhibitor", "بۆچی": "پەستانی خوێن"},
}

def get_drug_count(user_data):
    return len(DEFAULT_DRUGS) + len(user_data.get("custom_drugs", {}))

# ================================
# 3. دروستکردنی ئەپلیکەیشنەکە (بە دیزاینی پڕۆفیشناڵ)
# ================================
def main(page: ft.Page):
    page.title = "Dr.Danyal Pro Max"
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.colors.BLUE_400,
            secondary=ft.colors.PURPLE_400,
            background=ft.colors.BLACK,
            surface=ft.colors.with_opacity(0.05, ft.colors.WHITE)
        ),
        font_family="Segoe UI"
    )
    page.bgcolor = ft.colors.BLACK
    page.padding = 0
    page.window_width = 420
    page.window_height = 850
    page.window_resizable = False
    
    app_state = {
        "logged_in": False,
        "username": "",
        "user_data": {"custom_lab_tests": {}, "custom_drugs": {}}
    }

    def auto_save():
        if app_state["logged_in"]:
            save_user_data(app_state["username"], {
                "custom_lab_tests": app_state["user_data"]["custom_lab_tests"],
                "custom_drugs": app_state["user_data"]["custom_drugs"]
            })

    def route_to(view_func):
        page.controls.clear()
        view_func()
        page.update()

    # ================================
    # 4. پەڕەی لۆگین و دروستکردنی هەژمار (بە شێوازی مۆدێرن)
    # ================================
    def login_view():
        def do_login(e):
            if authenticate_user(username_input.value, password_input.value):
                app_state["logged_in"] = True
                app_state["username"] = username_input.value
                app_state["user_data"] = load_user_data(username_input.value)
                route_to(dashboard_view)
            else:
                page.snack_bar = ft.SnackBar(ft.Text("هەڵە لە ناو یان وشەی نهێنی!", text_align=ft.TextAlign.CENTER), bgcolor=ft.colors.RED_800)
                page.snack_bar.open = True
                page.update()

        def do_register(e):
            if not username_input.value or not password_input.value:
                page.snack_bar = ft.SnackBar(ft.Text("تکایە هەموو خانەکان پڕبکەرەوە"), bgcolor=ft.colors.RED_800)
                page.snack_bar.open = True
                page.update()
                return
            
            if create_user(username_input.value, password_input.value):
                page.snack_bar = ft.SnackBar(ft.Text("هەژمارەکەت دروست بوو! ئێستا بچۆ ژوورەوە"), bgcolor=ft.colors.GREEN_800)
                page.snack_bar.open = True
                page.update()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("ئەم ناوە پێشتر بەکارهاتووە!"), bgcolor=ft.colors.RED_800)
                page.snack_bar.open = True
                page.update()

        username_input = ft.TextField(label="ناوی بەکارهێنەری", prefix_icon=ft.icons.PERSON_OUTLINED, border_radius=15, filled=True)
        password_input = ft.TextField(label="وشەی نهێنی", prefix_icon=ft.icons.LOCK_OUTLINE, password=True, can_reveal_password=True, border_radius=15, filled=True)

        page.add(
            ft.Container(
                content=ft.Column([
                    ft.Container(height=60),
                    ft.Icon(ft.icons.MEDICAL_SERVICES_OUTLINED, size=80, color=ft.colors.BLUE_400),
                    ft.Text("Dr.Danyal", size=36, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                    ft.Text("ڕاهێنەری پزیشکی پڕۆ مەکس", size=14, color=ft.colors.GREY_500),
                    ft.Container(height=40),
                    username_input,
                    password_input,
                    ft.Container(height=20),
                    ft.ElevatedButton("چوونە ژوورەوە", on_click=do_login, width=double.infinity, height=50, bgcolor=ft.colors.BLUE_400, color=ft.colors.BLACK, border_radius=15, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=15))),
                    ft.OutlinedButton("دروستکردنی هەژماری نوێ", on_click=do_register, width=double.infinity, height=50, border_radius=15),
                ], alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.alignment.center,
                expand=True,
                padding=30
            )
        )

    # ================================
    # 5. پەڕەی داشبۆرد
    # ================================
    def dashboard_view():
        def logout(e):
            auto_save()
            app_state["logged_in"] = False
            app_state["username"] = ""
            route_to(login_view)

        stats = [
            ft.Card(content=ft.Container(content=ft.Column([ft.Icon(ft.icons.DISEASE, size=30, color=ft.colors.RED_400), ft.Text(f"{len(DISEASE_DATABASE)}", size=22, weight=ft.BOLD), ft.Text("نەخۆشی", size=12, color=ft.colors.GREY_400)]), padding=15, alignment=ft.alignment.center), expand=True, color=ft.colors.with_opacity(0.05, ft.colors.WHITE)),
            ft.Card(content=ft.Container(content=ft.Column([ft.Icon(ft.icons.MEDICATION, size=30, color=ft.colors.GREEN_400), ft.Text(f"{get_drug_count(app_state['user_data'])}", size=22, weight=ft.BOLD), ft.Text("دەرمان", size=12, color=ft.colors.GREY_400)]), padding=15, alignment=ft.alignment.center), expand=True, color=ft.colors.with_opacity(0.05, ft.colors.WHITE)),
            ft.Card(content=ft.Container(content=ft.Column([ft.Icon(ft.icons.SCIENCE, size=30, color=ft.colors.PURPLE_400), ft.Text(f"{len(DEFAULT_LABS) + len(app_state['user_data'].get('custom_lab_tests', {}))}", size=22, weight=ft.BOLD), ft.Text("پشکنین", size=12, color=ft.colors.GREY_400)]), padding=15, alignment=ft.alignment.center), expand=True, color=ft.colors.with_opacity(0.05, ft.colors.WHITE)),
        ]

        page.add(
            ft.Column([
                # هێدەر
                ft.Container(
                    content=ft.Row([ft.Column([ft.Text(f"بەخێربێیت", size=12, color=ft.colors.GREY_400), ft.Text(app_state['username'], size=18, weight=ft.BOLD)]), ft.IconButton(ft.icons.LOGOUT, on_click=logout, icon_color=ft.colors.RED_400)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=20, bgcolor=ft.colors.with_opacity(0.03, ft.colors.WHITE)
                ),
                # ئامار
                ft.Row(stats, alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(height=10),
                ft.Text("  بەشەکان", size=16, weight=ft.BOLD, color=ft.colors.GREY_400),
                ft.Container(height=10),
                # مێنیو
                ft.Card(content=ft.Column([
                    ft.ListTile(leading=ft.Icon(ft.icons.SCIENCE_OUTLINED, color=ft.colors.PURPLE_400), title=ft.Text("تاقیگە و پشکنین"), on_click=lambda e: route_to(labs_view), trailing=ft.Icon(ft.icons.CHEVRON_RIGHT_OUTLINED, color=ft.colors.GREY_500)),
                    ft.Divider(height=1, color=ft.colors.with_opacity(0.1, ft.colors.WHITE)),
                    ft.ListTile(leading=ft.Icon(ft.icons.MEDICATION_OUTLINED, color=ft.colors.GREEN_400), title=ft.Text("فارماکۆلۆجی"), on_click=lambda e: route_to(drugs_view), trailing=ft.Icon(ft.icons.CHEVRON_RIGHT_OUTLINED, color=ft.colors.GREY_500)),
                    ft.Divider(height=1, color=ft.colors.with_opacity(0.1, ft.colors.WHITE)),
                    ft.ListTile(leading=ft.Icon(ft.icons.MEDICAL_INFORMATION_OUTLINED, color=ft.colors.RED_400), title=ft.Text("نەخۆشییەکان"), on_click=lambda e: route_to(diseases_view), trailing=ft.Icon(ft.icons.CHEVRON_RIGHT_OUTLINED, color=ft.colors.GREY_500)),
                ]), color=ft.colors.with_opacity(0.03, ft.colors.WHITE), elevation=0),
            ], scroll=ft.ScrollMode.AUTO, expand=True)
        )

    # ================================
    # 6. پەڕەی تاقیگە (زیادکردن و سڕینەوە)
    # ================================
    def labs_view():
        all_labs = {**DEFAULT_LABS, **app_state["user_data"].get("custom_lab_tests", {})}
        
        def open_add_dialog(e):
            name_f = ft.TextField(label="ناوی پشکنین", border_radius=10, filled=True)
            normal_f = ft.TextField(label="نۆرماڵ (وەک: 70-126)", border_radius=10, filled=True)
            machine_f = ft.TextField(label="ئامێر", border_radius=10, filled=True)
            note_f = ft.TextField(label="تێبینی", multiline=True, border_radius=10, filled=True)

            def save(e):
                if name_f.value:
                    app_state["user_data"].setdefault("custom_lab_tests", {})[name_f.value] = {
                        "نۆرماڵ": normal_f.value or "", "ئامێر": machine_f.value or "", "تێبینی": note_f.value or ""}
                    auto_save()
                    dialog.open = False
                    route_to(labs_view)

            dialog = ft.AlertDialog(
                title=ft.Text("زیادکردنی پشکنین"),
                content=ft.Column([name_f, normal_f, machine_f, note_f], tight=True, scroll=ft.ScrollMode.AUTO),
                actions=[ft.TextButton("هەڵوەشاندنەوە", on_click=lambda _: setattr(dialog, 'open', False) or page.update()), ft.ElevatedButton("خەزنکردن", on_click=save, bgcolor=ft.colors.BLUE_400, color=ft.colors.BLACK)]
            )
            page.dialog = dialog
            dialog.open = True
            page.update()

        def delete_lab(name):
            del app_state["user_data"]["custom_lab_tests"][name]
            auto_save()
            route_to(labs_view)

        lab_list = []
        for name, info in all_labs.items():
            is_custom = name in app_state["user_data"].get("custom_lab_tests", {})
            lab_list.append(
                ft.Card(content=ft.Container(content=ft.Column([
                    ft.Row([ft.Text(name, size=16, weight=ft.BOLD, color=ft.colors.BLUE_200), ft.Container(content=ft.Text("تایبەت بە من", size=10), bgcolor=ft.colors.GREEN_700, padding=3, border_radius=5, visible=is_custom)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Text(f"نۆرماڵ: {info.get('نۆرماڵ', '')} | ئامێر: {info.get('ئامێر', '')}", size=12, color=ft.colors.GREY_400),
                    ft.Text(f"📝 {info.get('تێبینی', '')}", size=12, color=ft.colors.GREY_300, italic=True),
                    ft.Row([ft.TextButton("سڕینەوە", icon=ft.icons.DELETE, on_click=lambda e, n=name: delete_lab(n), style=ft.ButtonStyle(color=ft.colors.RED_400))], alignment=ft.MainAxisAlignment.END) if is_custom else ft.Container()
                ]), padding=15), color=ft.colors.with_opacity(0.03, ft.colors.WHITE), elevation=0)
            )

        page.add(
            ft.Column([
                ft.Row([ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda e: route_to(dashboard_view)), ft.Text("تاقیگەی پشکنین", size=20, weight=ft.BOLD)], alignment=ft.MainAxisAlignment.START),
                ft.ElevatedButton("➕ زیادکردنی پشکنینی نوێ", on_click=open_add_dialog, width=double.infinity, height=45, bgcolor=ft.colors.PURPLE_400, color=ft.colors.BLACK, border_radius=10),
                ft.Container(height=10),
                ft.Column(lab_list, scroll=ft.ScrollMode.AUTO, expand=True)
            ], expand=True)
        )

    # ================================
    # 7. پەڕەی دەرمانەکان
    # ================================
    def drugs_view():
        all_drugs = {**DEFAULT_DRUGS, **app_state["user_data"].get("custom_drugs", {})}
        
        def open_add_dialog(e):
            name_f = ft.TextField(label="ناوی دەرمان", border_radius=10, filled=True)
            dose_f = ft.TextField(label="ڕێژە", border_radius=10, filled=True)
            mech_f = ft.TextField(label="میکانیزم", border_radius=10, filled=True)
            why_f = ft.TextField(label="بۆچی", border_radius=10, filled=True)

            def save(e):
                if name_f.value:
                    app_state["user_data"].setdefault("custom_drugs", {})[name_f.value] = {
                        "ڕێژە": dose_f.value or "", "میکانیزم": mech_f.value or "", "بۆچی": why_f.value or ""}
                    auto_save()
                    dialog.open = False
                    route_to(drugs_view)

            dialog = ft.AlertDialog(
                title=ft.Text("زیادکردنی دەرمان"),
                content=ft.Column([name_f, dose_f, mech_f, why_f], tight=True, scroll=ft.ScrollMode.AUTO),
                actions=[ft.TextButton("هەڵوەشاندنەوە", on_click=lambda _: setattr(dialog, 'open', False) or page.update()), ft.ElevatedButton("خەزنکردن", on_click=save, bgcolor=ft.colors.GREEN_400, color=ft.colors.BLACK)]
            )
            page.dialog = dialog
            dialog.open = True
            page.update()

        def delete_drug(name):
            del app_state["user_data"]["custom_drugs"][name]
            auto_save()
            route_to(drugs_view)

        drug_list = []
        for name, info in all_drugs.items():
            is_custom = name in app_state["user_data"].get("custom_drugs", {})
            drug_list.append(
                ft.Card(content=ft.Container(content=ft.Column([
                    ft.Row([ft.Icon(ft.icons.PILL, color=ft.colors.GREEN_400), ft.Text(name, size=16, weight=ft.BOLD, expand=True), ft.Container(content=ft.Text("تایبەت بە من", size=10), bgcolor=ft.colors.GREEN_700, padding=3, border_radius=5, visible=is_custom)]),
                    ft.Text(f"ڕێژە: {info.get('ڕێژە', '')} | {info.get('بۆچی', '')}", size=12, color=ft.colors.GREY_400),
                    ft.Row([ft.TextButton("سڕینەوە", icon=ft.icons.DELETE, on_click=lambda e, n=name: delete_drug(n), style=ft.ButtonStyle(color=ft.colors.RED_400))], alignment=ft.MainAxisAlignment.END) if is_custom else ft.Container()
                ]), padding=15), color=ft.colors.with_opacity(0.03, ft.colors.WHITE), elevation=0)
            )

        page.add(
            ft.Column([
                ft.Row([ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda e: route_to(dashboard_view)), ft.Text("فارماکۆلۆجی", size=20, weight=ft.BOLD)], alignment=ft.MainAxisAlignment.START),
                ft.ElevatedButton("➕ زیادکردنی دەرمانی نوێ", on_click=open_add_dialog, width=double.infinity, height=45, bgcolor=ft.colors.GREEN_400, color=ft.colors.BLACK, border_radius=10),
                ft.Container(height=10),
                ft.Column(drug_list, scroll=ft.ScrollMode.AUTO, expand=True)
            ], expand=True)
        )

    # ================================
    # 8. پەڕەی نەخۆشییەکان
    # ================================
    def diseases_view():
        dis_list = []
        for name, info in DISEASE_DATABASE.items():
            dis_list.append(
                ft.Card(content=ft.Container(content=ft.ExpansionTile(
                    title=ft.Text(name, size=16, weight=ft.BOLD, color=ft.colors.RED_200),
                    subtitle=ft.Text(f"ئاستی مەترسی: {info['ئاستی مەترسی']}", size=12, color=ft.colors.GREY_400),
                    controls=[ft.Container(content=ft.Column([
                        ft.Text("نیشانەکان:", weight=ft.BOLD, color=ft.colors.BLUE_200), ft.Text("، ".join(info['نیشانەکان'])),
                        ft.Text("چارەسەر:", weight=ft.BOLD, color=ft.colors.GREEN_200), ft.Text("، ".join(info['چارەسەر'])),
                    ]), padding=10)]
                )), color=ft.colors.with_opacity(0.03, ft.colors.WHITE), elevation=0)
            )

        page.add(
            ft.Column([
                ft.Row([ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda e: route_to(dashboard_view)), ft.Text("نەخۆشییەکان", size=20, weight=ft.BOLD)], alignment=ft.MainAxisAlignment.START),
                ft.Container(height=10),
                ft.Column(dis_list, scroll=ft.ScrollMode.AUTO, expand=True)
            ], expand=True)
        )

    # دەستپێکردن
    route_to(login_view)

if __name__ == "__main__":
    ft.app(target=main)
