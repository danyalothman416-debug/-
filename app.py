import flet as ft
import hashlib
import json
import os
from datetime import datetime

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

def authenticate_user(username: str, password: str) -> bool:
    users = load_users()
    return username in users and users[username]["password"] == hash_password(password)

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

def load_user_data(username: str) -> dict:
    users = load_users()
    return users.get(username, {"custom_lab_tests": {}, "custom_drugs": {}})

def save_user_data(username: str, data: dict):
    users = load_users()
    if username in users:
        users[username].update(data)
        save_users(users)

# ================================
# 2. داتابەسی بنەڕەتی (هەموو داتاکانت لێرەدانەوە بە کورتی بۆ جێگیربوون)
# ================================
DISEASE_DATABASE = {
    "شەکرەی جۆری 1": {"نیشانەکان": ["تینوویەتی زۆر", "میزی زۆر", "کێش کەمبوونەوە"], "ئاستی مەترسی": "زۆر مەترسیدار", "چارەسەر": ["ئەنسولین"]},
    "شەکرەی جۆری 2": {"نیشانەکان": ["تینوویەتی زۆر", "ماندوویی", "بینی تەڵخ"], "ئاستی مەترسی": "مەترسیدار", "چارەسەر": ["مێتفۆرمین"]},
    "پەستانی خوێنی سەرەتایی": {"نیشانەکان": ["سەرئێشە", "سەرگێژخواردن"], "ئاستی مەترسی": "مامناوەند", "چارەسەر": ["کاپتۆپریل"]},
    "هەوکردنی سییەکان": {"نیشانەکان": ["تا", "کۆخە"], "ئاستی مەترسی": "مامناوەند", "چارەسەر": ["ئەمۆکسیسیلین"]},
    "نەخۆشی دڵی ئیسکیمیک": {"نیشانەکان": ["ئازاری سنگ", "کورتی هەناسە"], "ئاستی مەترسی": "زۆر مەترسیدار", "چارەسەر": ["ئەسپیرین", "نایترۆگلیسیرین"]},
    "نەخۆشی گەدە": {"نیشانەکان": ["ئازاری گەدە", "سکچوون"], "ئاستی مەترسی": "کەم", "چارەسەر": ["ئومەپرازۆل"]},
    # ... (دەتوانیت باقی نەخۆشییەکانی خۆت لێرە زیاد بکەیت بە هەمان فۆرمات)
}

DEFAULT_LABS = {
    "CBC": {"گروپ": "خوێن", "نۆرماڵ": "4.0-11.0", "یەکە": "x10³/µL", "ئامێر": "سێل کاونتر"},
    "Glucose": {"گروپ": "بایۆکیمیایی", "نۆرماڵ": "70-126", "یەکە": "mg/dL", "ئامێر": "گلوکۆمیتەر"},
    "Troponin": {"گروپ": "دڵ", "نۆرماڵ": "0-0.04", "یەکە": "ng/mL", "ئامێر": "کیمیایی ئیمینۆ"},
    "ALT": {"گروپ": "جگەر", "نۆرماڵ": "10-40", "یەکە": "U/L", "ئامێر": "سپێکترۆفۆتۆمیتەر"},
    # ... (باقی پشکنینەکانت لێرە زیاد بکە)
}

DEFAULT_DRUGS = {
    "کاپتۆپریل": {"ڕێژە": "25mg", "میکانیزم": "ACE inhibitor", "بۆچی": "پەستانی خوێن"},
    "مێتفۆرمین": {"ڕێژە": "500mg", "میکانیزم": "Biguanide", "بۆچی": "شەکرەی جۆری 2"},
    "ئەمۆکسیسیلین": {"ڕێژە": "500mg", "میکانیزم": "Beta-lactam", "بۆچی": "هەوکردن"},
    "ئومەپرازۆل": {"ڕێژە": "20mg", "میکانیزم": "PPI", "بۆچی": "گەدە"},
    # ... (باقی دەرمانەکانت لێرە زیاد بکە)
}

def get_drug_count(user_data):
    return len(DEFAULT_DRUGS) + len(user_data.get("custom_drugs", {}))

# ================================
# 3. دروستکردنی ئەپلیکەیشنەکە (Flet)
# ================================
def main(page: ft.Page):
    page.title = "Dr.Danyal - ڕاهێنەری پزیشکی Pro Max"
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(color_scheme_seed=ft.colors.BLUE_GREY)
    page.window_width = 400
    page.window_height = 800
    page.padding = 0
    
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

    # ================================
    # 4. پەڕەی لۆگین
    # ================================
    def show_login_view(e=None):
        page.controls.clear()
        
        def do_login(e):
            if authenticate_user(username_input.value, password_input.value):
                app_state["logged_in"] = True
                app_state["username"] = username_input.value
                app_state["user_data"] = load_user_data(username_input.value)
                show_dashboard_view()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("ناوی بەکارهێنەری یان وشەی نهێنی هەڵەیە!", color=ft.colors.WHITE), bgcolor=ft.colors.RED_800)
                page.snack_bar.open = True
                page.update()

        def do_register(e):
            if username_input.value and password_input.value:
                if create_user(username_input.value, password_input.value):
                    page.snack_bar = ft.SnackBar(ft.Text("هەژمارەکەت دروست کرا! بچۆ ژوورەوە."), bgcolor=ft.colors.GREEN_800)
                    page.snack_bar.open = True
                    page.update()
                else:
                    page.snack_bar = ft.SnackBar(ft.Text("ئەم ناوە پێشتر بەکارهاتووە!"), bgcolor=ft.colors.RED_800)
                    page.snack_bar.open = True
                    page.update()

        username_input = ft.TextField(label="ناوی بەکارهێنەری", prefix_icon=ft.icons.PERSON, width=300, text_align=ft.TextAlign.RIGHT)
        password_input = ft.TextField(label="وشەی نهێنی", prefix_icon=ft.icons.LOCK, password=True, can_reveal_password=True, width=300, text_align=ft.TextAlign.RIGHT)

        page.add(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.MEDICAL_SERVICES, size=80, color=ft.colors.BLUE_400),
                    ft.Text("Dr.Danyal", size=32, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_400),
                    ft.Text("ڕاهێنەری پزیشکی پڕۆ مەکس", size=16, color=ft.colors.GREY_400),
                    ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                    username_input, password_input,
                    ft.Row([
                        ft.ElevatedButton("چوونە ژوورەوە", on_click=do_login, width=140, bgcolor=ft.colors.BLUE_400, color=ft.colors.WHITE),
                        ft.OutlinedButton("دروستکردنی هەژمار", on_click=do_register, width=140),
                    ], alignment=ft.MainAxisAlignment.CENTER),
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.alignment.center, expand=True,
                gradient=ft.LinearGradient(begin=ft.alignment.top_center, end=ft.alignment.bottom_center, colors=[ft.colors.BLUE_900, ft.colors.GREY_900])
            )
        )
        page.update()

    # ================================
    # 5. پەڕەی داشبۆرد
    # ================================
    def show_dashboard_view(e=None):
        page.controls.clear()
        
        def logout(e):
            auto_save()
            app_state["logged_in"] = False
            app_state["username"] = ""
            show_login_view()

        stats = [
            ft.Card(content=ft.Container(content=ft.Column([ft.Icon(ft.icons.DISEASE, size=40, color=ft.colors.RED_400), ft.Text(f"{len(DISEASE_DATABASE)}", size=24, weight=ft.BOLD), ft.Text("نەخۆشی")], horizontal_alignment=ft.CrossAxisAlignment.CENTER), padding=10), expand=True),
            ft.Card(content=ft.Container(content=ft.Column([ft.Icon(ft.icons.MEDICATION, size=40, color=ft.colors.GREEN_400), ft.Text(f"{get_drug_count(app_state['user_data'])}", size=24, weight=ft.BOLD), ft.Text("دەرمان")], horizontal_alignment=ft.CrossAxisAlignment.CENTER), padding=10), expand=True),
            ft.Card(content=ft.Container(content=ft.Column([ft.Icon(ft.icons.SCIENCE, size=40, color=ft.colors.PURPLE_400), ft.Text(f"{len(DEFAULT_LABS) + len(app_state['user_data'].get('custom_lab_tests', {}))}", size=24, weight=ft.BOLD), ft.Text("پشکنین")], horizontal_alignment=ft.CrossAxisAlignment.CENTER), padding=10), expand=True),
        ]

        page.add(
            ft.Column([
                ft.Container(
                    content=ft.Row([ft.Text(f"بەخێربێیت {app_state['username']}", size=18, weight=ft.BOLD), ft.IconButton(ft.icons.LOGOUT, on_click=logout, icon_color=ft.colors.RED_400)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=15, bgcolor=ft.colors.SURFACE_VARIANT
                ),
                ft.Row(stats, alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(),
                ft.Text("بەشەکان:", size=18, weight=ft.BOLD),
                ft.ListTile(leading=ft.Icon(ft.icons.SCIENCE, color=ft.colors.PURPLE_400), title=ft.Text("تاقیگە و پشکنین"), on_click=show_labs_view, trailing=ft.Icon(ft.icons.CHEVRON_RIGHT)),
                ft.ListTile(leading=ft.Icon(ft.icons.MEDICATION, color=ft.colors.GREEN_400), title=ft.Text("فارماکۆلۆجی"), on_click=show_drugs_view, trailing=ft.Icon(ft.icons.CHEVRON_RIGHT)),
                ft.ListTile(leading=ft.Icon(ft.icons.MEDICAL_INFORMATION, color=ft.colors.RED_400), title=ft.Text("نەخۆشییەکان"), on_click=show_diseases_view, trailing=ft.Icon(ft.icons.CHEVRON_RIGHT)),
            ], scroll=ft.ScrollMode.AUTO, expand=True)
        )
        page.update()

    # ================================
    # 6. پەڕەی تاقیگە (زیادکردن، سڕینەوە)
    # ================================
    def show_labs_view(e=None):
        page.controls.clear()
        all_labs = {**DEFAULT_LABS, **app_state["user_data"].get("custom_lab_tests", {})}
        
        def go_back(e): show_dashboard_view()
        
        def open_add_lab_dialog(e):
            name_field = ft.TextField(label="ناوی پشکنین", text_align=ft.TextAlign.RIGHT)
            normal_field = ft.TextField(label="نۆرماڵ (وەک: 70-126)", text_align=ft.TextAlign.RIGHT)
            machine_field = ft.TextField(label="ئامێر", text_align=ft.TextAlign.RIGHT)
            note_field = ft.TextField(label="تێبینی", multiline=True, text_align=ft.TextAlign.RIGHT)

            def save_new_lab(e):
                if name_field.value:
                    app_state["user_data"].setdefault("custom_lab_tests", {})[name_field.value] = {
                        "نۆرماڵ": normal_field.value or "نەزانراو",
                        "ئامێر": machine_field.value or "",
                        "تێبینی": note_field.value or ""
                    }
                    auto_save()
                    dialog.open = False
                    page.update()
                    show_labs_view()

            dialog = ft.AlertDialog(
                title=ft.Text("زیادکردنی پشکنینی نوێ"),
                content=ft.Column([name_field, normal_field, machine_field, note_field], tight=True, scroll=ft.ScrollMode.AUTO),
                actions=[ft.TextButton("هەڵوەشاندنەوە", on_click=lambda _: close_dialog(dialog)), ft.ElevatedButton("خەزنکردن", on_click=save_new_lab, bgcolor=ft.colors.BLUE_400, color=ft.colors.WHITE)],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            page.dialog = dialog
            dialog.open = True
            page.update()

        def delete_lab(lab_name):
            if lab_name in app_state["user_data"].get("custom_lab_tests", {}):
                del app_state["user_data"]["custom_lab_tests"][lab_name]
                auto_save()
                show_labs_view()

        lab_list_controls = []
        for name, info in all_labs.items():
            is_custom = name in app_state["user_data"].get("custom_lab_tests", {})
            lab_list_controls.append(
                ft.Card(content=ft.Container(content=ft.Column([
                    ft.Row([ft.Text(name, size=16, weight=ft.BOLD, color=ft.colors.BLUE_200), ft.Container(content=ft.Text("تایبەت بە من", size=10, color=ft.colors.WHITE), bgcolor=ft.colors.GREEN_700, padding=5, border_radius=5, visible=is_custom)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Text(f"نۆرماڵ: {info.get('نۆرماڵ', '')} | ئامێر: {info.get('ئامێر', '')}", size=12, color=ft.colors.GREY_400),
                    ft.Text(f"📝 {info.get('تێبینی', 'بێ تێبینی')}", size=12, color=ft.colors.GREY_300, italic=True),
                    ft.Row([ft.IconButton(ft.icons.DELETE, icon_color=ft.colors.RED_400, on_click=lambda e, n=name: delete_lab(n), visible=is_custom)], alignment=ft.MainAxisAlignment.END)
                ]), padding=15))
            )

        page.add(
            ft.Column([
                ft.Row([ft.IconButton(ft.icons.ARROW_BACK, on_click=go_back), ft.Text("تاقیگەی پشکنین", size=22, weight=ft.BOLD)], alignment=ft.MainAxisAlignment.START),
                ft.ElevatedButton("➕ زیادکردنی پشکنینی نوێ", on_click=open_add_lab_dialog, width=page.width, bgcolor=ft.colors.PURPLE_400, color=ft.colors.WHITE),
                ft.Divider(),
                ft.Column(lab_list_controls, scroll=ft.ScrollMode.AUTO, expand=True)
            ], expand=True)
        )
        page.update()

    # ================================
    # 7. پەڕەی دەرمانەکان (زیادکردن، سڕینەوە)
    # ================================
    def show_drugs_view(e=None):
        page.controls.clear()
        all_drugs = {**DEFAULT_DRUGS, **app_state["user_data"].get("custom_drugs", {})}
        
        def go_back(e): show_dashboard_view()
        
        def open_add_drug_dialog(e):
            name_field = ft.TextField(label="ناوی دەرمان", text_align=ft.TextAlign.RIGHT)
            dose_field = ft.TextField(label="ڕێژە", text_align=ft.TextAlign.RIGHT)
            mech_field = ft.TextField(label="میکانیزم", text_align=ft.TextAlign.RIGHT)
            why_field = ft.TextField(label="بۆچی بەکاردێت", text_align=ft.TextAlign.RIGHT)
            note_field = ft.TextField(label="تێبینی", multiline=True, text_align=ft.TextAlign.RIGHT)

            def save_new_drug(e):
                if name_field.value:
                    app_state["user_data"].setdefault("custom_drugs", {})[name_field.value] = {
                        "ڕێژە": dose_field.value or "",
                        "میکانیزم": mech_field.value or "",
                        "بۆچی": why_field.value or "",
                        "تێبینی": note_field.value or ""
                    }
                    auto_save()
                    dialog.open = False
                    page.update()
                    show_drugs_view()

            dialog = ft.AlertDialog(
                title=ft.Text("زیادکردنی دەرمانی نوێ"),
                content=ft.Column([name_field, dose_field, mech_field, why_field, note_field], tight=True, scroll=ft.ScrollMode.AUTO),
                actions=[ft.TextButton("هەڵوەشاندنەوە", on_click=lambda _: close_dialog(dialog)), ft.ElevatedButton("خەزنکردن", on_click=save_new_drug, bgcolor=ft.colors.GREEN_400, color=ft.colors.WHITE)],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            page.dialog = dialog
            dialog.open = True
            page.update()

        def delete_drug(drug_name):
            if drug_name in app_state["user_data"].get("custom_drugs", {}):
                del app_state["user_data"]["custom_drugs"][drug_name]
                auto_save()
                show_drugs_view()

        drug_list_controls = []
        for name, info in all_drugs.items():
            is_custom = name in app_state["user_data"].get("custom_drugs", {})
            drug_list_controls.append(
                ft.Card(content=ft.Container(content=ft.Column([
                    ft.Row([ft.Icon(ft.icons.MEDICATION, color=ft.colors.GREEN_400), ft.Text(name, size=16, weight=ft.BOLD, expand=True), ft.Container(content=ft.Text("تایبەت بە من", size=10, color=ft.colors.WHITE), bgcolor=ft.colors.GREEN_700, padding=5, border_radius=5, visible=is_custom)]),
                    ft.Text(f"ڕێژە: {info.get('ڕێژە', '')} | میکانیزم: {info.get('میکانیزم', '')}", size=12, color=ft.colors.GREY_400),
                    ft.Text(f"بەکارهێنان: {info.get('بۆچی', '')}", size=14, color=ft.colors.WHITE),
                    ft.Text(f"📝 {info.get('تێبینی', 'بێ تێبینی')}", size=12, color=ft.colors.GREY_300, italic=True),
                    ft.Row([ft.IconButton(ft.icons.DELETE, icon_color=ft.colors.RED_400, on_click=lambda e, n=name: delete_drug(n), visible=is_custom)], alignment=ft.MainAxisAlignment.END)
                ]), padding=15))
            )

        page.add(
            ft.Column([
                ft.Row([ft.IconButton(ft.icons.ARROW_BACK, on_click=go_back), ft.Text("فارماکۆلۆجی و دەرمان", size=22, weight=ft.BOLD)], alignment=ft.MainAxisAlignment.START),
                ft.ElevatedButton("➕ زیادکردنی دەرمانی نوێ", on_click=open_add_drug_dialog, width=page.width, bgcolor=ft.colors.GREEN_400, color=ft.colors.WHITE),
                ft.Divider(),
                ft.Column(drug_list_controls, scroll=ft.ScrollMode.AUTO, expand=True)
            ], expand=True)
        )
        page.update()

    # ================================
    # 8. پەڕەی نەخۆشییەکان
    # ================================
    def show_diseases_view(e=None):
        page.controls.clear()
        def go_back(e): show_dashboard_view()
        
        disease_controls = []
        for name, info in DISEASE_DATABASE.items():
            disease_controls.append(
                ft.Card(content=ft.Container(content=ft.ExpansionTile(
                    title=ft.Text(name, size=16, weight=ft.BOLD, color=ft.colors.RED_200),
                    subtitle=ft.Text(f"ئاستی مەترسی: {info['ئاستی مەترسی']}"),
                    controls=[ft.Container(content=ft.Column([
                        ft.Text("نیشانەکان:", weight=ft.BOLD, color=ft.colors.BLUE_200), ft.Text("، ".join(info['نیشانەکان'])),
                        ft.Text("چارەسەر:", weight=ft.BOLD, color=ft.colors.GREEN_200), ft.Text("، ".join(info['چارەسەر'])),
                    ]), padding=ft.padding.only(left=10, right=10, bottom=10))]
                )))
            )

        page.add(
            ft.Column([
                ft.Row([ft.IconButton(ft.icons.ARROW_BACK, on_click=go_back), ft.Text("کتیبخانەی نەخۆشییەکان", size=22, weight=ft.BOLD)], alignment=ft.MainAxisAlignment.START),
                ft.Divider(),
                ft.Column(disease_controls, scroll=ft.ScrollMode.AUTO, expand=True)
            ], expand=True)
        )
        page.update()

    def close_dialog(dialog):
        dialog.open = False
        page.update()

    # دەستپێکردنی ئەپلیکەیشنەکە
    show_login_view()

if __name__ == "__main__":
    ft.app(target=main)
