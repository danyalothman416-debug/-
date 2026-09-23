"""
Danyal Financial OS - Production Server
Clean Username & Password Authentication (Zero Email Bugs)
"""

import os
import sqlite3
import csv
import io
from datetime import datetime, date, timedelta
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, Response, send_file
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "danyal_secure_vault_key_2026_clean"
app.permanent_session_lifetime = timedelta(days=30)

# بنکەدراوەیەکی خاوێن بۆ ئەوەی هیچ کێشەیەکی داتابەیسی کۆن ڕوونەدات
DB_NAME = "danyal_system.db"
UPLOAD_FOLDER = os.path.join("static", "avatars")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def init_db():
    with get_db() as conn:
        cursor = conn.cursor()

        # ١. خشتەی بەکارهێنەران و دوکانەکان
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                shop_name TEXT NOT NULL,
                full_name TEXT NOT NULL,
                avatar TEXT DEFAULT 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150',
                bio TEXT DEFAULT 'بەڕێوەبەری سیستەم',
                created_at TEXT NOT NULL
            )
        """)

        # ٢. خشتەی قەرزەکان (دابڕاو بەپێی بەکارهێنەر)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS debts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                customer_name TEXT NOT NULL,
                phone TEXT,
                total_amount REAL NOT NULL,
                currency TEXT NOT NULL DEFAULT 'IQD',
                debt_date TEXT NOT NULL,
                due_date TEXT NOT NULL,
                note TEXT,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)

        # ٣. خشتەی وەسڵ و واسڵکردن
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                debt_id INTEGER NOT NULL,
                receipt_no TEXT NOT NULL,
                amount_paid REAL NOT NULL,
                payment_date TEXT NOT NULL,
                note TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (debt_id) REFERENCES debts (id) ON DELETE CASCADE
            )
        """)

        conn.commit()

init_db()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return jsonify({"status": "error", "message": "تکایە سەرەتا بچۆ ژوورەوە"}), 401
        return f(*args, **kwargs)
    return decorated_function


def update_debt_status(conn, user_id, debt_id):
    debt = conn.execute("SELECT total_amount, due_date FROM debts WHERE id = ? AND user_id = ?", (debt_id, user_id)).fetchone()
    if not debt:
        return

    paid_sum = conn.execute(
        "SELECT COALESCE(SUM(amount_paid), 0) as total FROM payments WHERE debt_id = ? AND user_id = ?", (debt_id, user_id)
    ).fetchone()["total"]

    remaining = debt["total_amount"] - paid_sum
    today = date.today().isoformat()

    if remaining <= 0:
        status = "paid"
    elif debt["due_date"] and debt["due_date"] < today:
        status = "overdue"
    elif paid_sum > 0:
        status = "partial"
    else:
        status = "pending"

    conn.execute("UPDATE debts SET status = ? WHERE id = ? AND user_id = ?", (status, debt_id, user_id))
    conn.commit()


@app.route("/")
def index():
    return render_template("index.html")


# چوونەژوورەوە یان دروستکردنی ئەکاونت تەنها بە ناوی بەکارهێنەر و وشەی نهێنی
@app.route("/api/auth/login", methods=["POST"])
def auth_login():
    data = request.get_json(force=True, silent=True) or {}
    username = data.get("username", "").strip().lower()
    password = data.get("password", "").strip()

    if not username:
        return jsonify({"status": "error", "message": "تکایە ناوی بەکارهێنەر بنووسە"}), 400

    if not password:
        return jsonify({"status": "error", "message": "تکایە وشەی نهێنی بنووسە"}), 400

    with get_db() as conn:
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

        # ئەگەر بەکارهێنەرەکە پێشتر نەبوو، دەستبەجێ بەم وشە نهێنییە تۆماری دەکات و ئەپەکە دەکاتەوە
        if not user:
            cursor = conn.cursor()
            clean_name = username.capitalize()
            cursor.execute("""
                INSERT INTO users (username, password_hash, shop_name, full_name, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (username, generate_password_hash(password), f"فرۆشگای {clean_name}", clean_name, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            user_id = cursor.lastrowid
            conn.commit()

            user_data = {
                "id": user_id,
                "username": username,
                "shop_name": f"فرۆشگای {clean_name}",
                "full_name": clean_name,
                "avatar": "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150",
                "bio": "بەڕێوەبەری سیستەم"
            }
        else:
            # ئەگەر هەژمارەکە هەبوو، پشکنین بۆ وشەی نهێنی دەکات
            if not check_password_hash(user["password_hash"], password):
                return jsonify({"status": "error", "message": "وشەی نهێنی هەڵەیە!"}), 401

            user_data = {
                "id": user["id"],
                "username": user["username"],
                "shop_name": user["shop_name"],
                "full_name": user["full_name"],
                "avatar": user["avatar"],
                "bio": user["bio"]
            }

    session.permanent = True
    session["user"] = user_data

    return jsonify({"status": "success", "user": user_data})


@app.route("/api/auth/me", methods=["GET"])
def auth_me():
    if "user" in session:
        return jsonify({"logged_in": True, "user": session["user"]})
    return jsonify({"logged_in": False})


@app.route("/api/auth/logout", methods=["POST"])
def auth_logout():
    session.clear()
    return jsonify({"status": "success"})


@app.route("/api/profile/update", methods=["POST"])
@login_required
def update_profile():
    full_name = request.form.get("full_name", "").strip()
    shop_name = request.form.get("shop_name", "").strip()
    bio = request.form.get("bio", "").strip()
    file = request.files.get("avatar")

    if not full_name:
        return jsonify({"status": "error", "message": "ناو پێویستە"}), 400

    avatar_url = session["user"].get("avatar")
    if file and file.filename != '':
        filename = f"avatar_{session['user']['id']}_{int(datetime.now().timestamp())}.{file.filename.rsplit('.', 1)[1].lower()}"
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)
        avatar_url = f"/static/avatars/{filename}"

    with get_db() as conn:
        conn.execute("""
            UPDATE users SET full_name = ?, shop_name = ?, bio = ?, avatar = ? WHERE id = ?
        """, (full_name, shop_name or session["user"]["shop_name"], bio, avatar_url, session["user"]["id"]))
        conn.commit()

    session["user"]["full_name"] = full_name
    if shop_name:
        session["user"]["shop_name"] = shop_name
    session["user"]["bio"] = bio
    session["user"]["avatar"] = avatar_url

    return jsonify({"status": "success", "user": session["user"]})


@app.route("/api/dashboard/analytics", methods=["GET"])
@login_required
def dashboard_analytics():
    user_id = session["user"]["id"]
    today = date.today().isoformat()

    with get_db() as conn:
        for d in conn.execute("SELECT id FROM debts WHERE user_id = ?", (user_id,)).fetchall():
            update_debt_status(conn, user_id, d["id"])

        iqd_debt = conn.execute("SELECT COALESCE(SUM(total_amount), 0) as s FROM debts WHERE user_id = ? AND currency = 'IQD'", (user_id,)).fetchone()["s"]
        iqd_paid = conn.execute("""
            SELECT COALESCE(SUM(p.amount_paid), 0) as s 
            FROM payments p JOIN debts d ON p.debt_id = d.id 
            WHERE p.user_id = ? AND d.currency = 'IQD'
        """, (user_id,)).fetchone()["s"]

        usd_debt = conn.execute("SELECT COALESCE(SUM(total_amount), 0) as s FROM debts WHERE user_id = ? AND currency = 'USD'", (user_id,)).fetchone()["s"]
        usd_paid = conn.execute("""
            SELECT COALESCE(SUM(p.amount_paid), 0) as s 
            FROM payments p JOIN debts d ON p.debt_id = d.id 
            WHERE p.user_id = ? AND d.currency = 'USD'
        """, (user_id,)).fetchone()["s"]

        overdue_count = conn.execute("SELECT COUNT(*) as c FROM debts WHERE user_id = ? AND status = 'overdue'", (user_id,)).fetchone()["c"]
        due_today_count = conn.execute("SELECT COUNT(*) as c FROM debts WHERE user_id = ? AND due_date = ? AND status != 'paid'", (user_id, today)).fetchone()["c"]

        top_debtors_raw = conn.execute("""
            SELECT d.customer_name, (d.total_amount - COALESCE(SUM(p.amount_paid), 0)) as remaining
            FROM debts d LEFT JOIN payments p ON d.id = p.debt_id
            WHERE d.user_id = ?
            GROUP BY d.id HAVING remaining > 0 ORDER BY remaining DESC LIMIT 5
        """, (user_id,)).fetchall()

        monthly_payments = conn.execute("""
            SELECT strftime('%Y-%m', payment_date) as month, SUM(amount_paid) as total
            FROM payments WHERE user_id = ?
            GROUP BY month ORDER BY month DESC LIMIT 6
        """, (user_id,)).fetchall()

    return jsonify({
        "iqd": {"debt": iqd_debt, "paid": iqd_paid, "remaining": max(0.0, iqd_debt - iqd_paid)},
        "usd": {"debt": usd_debt, "paid": usd_paid, "remaining": max(0.0, usd_debt - usd_paid)},
        "overdue_count": overdue_count,
        "due_today_count": due_today_count,
        "top_debtors": [dict(r) for r in top_debtors_raw],
        "monthly_chart": [dict(m) for m in reversed(monthly_payments)]
    })


@app.route("/api/debts", methods=["GET"])
@login_required
def get_debts():
    user_id = session["user"]["id"]
    search = request.args.get("search", "").strip()

    query = """
        SELECT d.*, 
               COALESCE(SUM(p.amount_paid), 0) as paid_amount,
               (d.total_amount - COALESCE(SUM(p.amount_paid), 0)) as remaining_amount
        FROM debts d
        LEFT JOIN payments p ON d.id = p.debt_id
        WHERE d.user_id = ?
    """
    params = [user_id]
    if search:
        query += " AND (d.customer_name LIKE ? OR d.phone LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])

    query += " GROUP BY d.id ORDER BY d.id DESC"

    with get_db() as conn:
        rows = conn.execute(query, params).fetchall()

    return jsonify([dict(r) for r in rows])


@app.route("/api/debts", methods=["POST"])
@login_required
def create_debt():
    user_id = session["user"]["id"]
    data = request.get_json(force=True, silent=True) or {}
    name = data.get("customer_name", "").strip()
    phone = data.get("phone", "").strip()
    amount = data.get("total_amount")
    currency = data.get("currency", "IQD")
    due_date = data.get("due_date")
    debt_date = data.get("debt_date") or date.today().isoformat()
    note = data.get("note", "").strip()

    if not name or not amount or not due_date:
        return jsonify({"status": "error", "message": "تکایە ناو، بڕی پارە و بەرواری دانەوە بنووسە"}), 400

    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError()
    except (TypeError, ValueError):
        return jsonify({"status": "error", "message": "بڕی پارە نادروستە"}), 400

    status = "overdue" if due_date < date.today().isoformat() else "pending"

    with get_db() as conn:
        conn.execute("""
            INSERT INTO debts (user_id, customer_name, phone, total_amount, currency, debt_date, due_date, note, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, name, phone, amount, currency, debt_date, due_date, note, status, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()

    return jsonify({"status": "success", "message": "قەرزەکە پاشەکەوت کرا"})


@app.route("/api/debts/<int:debt_id>/payments", methods=["POST"])
@login_required
def make_payment(debt_id):
    user_id = session["user"]["id"]
    data = request.get_json(force=True, silent=True) or {}
    try:
        amount = float(data.get("amount", 0))
    except (TypeError, ValueError):
        amount = 0.0

    if amount <= 0:
        return jsonify({"status": "error", "message": "بڕی واسڵکراو دەبێت لە ٠ زیاتر بێت"}), 400

    with get_db() as conn:
        debt = conn.execute("SELECT * FROM debts WHERE id = ? AND user_id = ?", (debt_id, user_id)).fetchone()
        if not debt:
            return jsonify({"status": "error", "message": "قەرزەکە نەدۆزرایەوە"}), 404

        current_paid = conn.execute(
            "SELECT COALESCE(SUM(amount_paid), 0) as s FROM payments WHERE debt_id = ? AND user_id = ?", (debt_id, user_id)
        ).fetchone()["s"]

        remaining = debt["total_amount"] - current_paid
        if amount > remaining:
            return jsonify({"status": "error", "message": f"بڕی دراو لە ماوە زیاترە! ({remaining:,.0f} {debt['currency']})"}), 400

        receipt_no = f"REC-{user_id}-{int(datetime.now().timestamp()) % 100000}"

        conn.execute("""
            INSERT INTO payments (user_id, debt_id, receipt_no, amount_paid, payment_date, note)
            VALUES (?, ?, ?, ?, ?, '')
        """, (user_id, debt_id, receipt_no, amount, datetime.now().strftime("%Y-%m-%d %H:%M")))

        update_debt_status(conn, user_id, debt_id)
        conn.commit()

        remaining_after = remaining - amount

    return jsonify({
        "status": "success",
        "receipt": {
            "receipt_no": receipt_no,
            "customer_name": debt["customer_name"],
            "phone": debt["phone"],
            "amount_paid": amount,
            "currency": debt["currency"],
            "remaining": remaining_after,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "received_by": session["user"]["full_name"]
        }
    })


@app.route("/api/debts/<int:debt_id>", methods=["DELETE"])
@login_required
def delete_debt(debt_id):
    user_id = session["user"]["id"]
    with get_db() as conn:
        conn.execute("DELETE FROM payments WHERE debt_id = ? AND user_id = ?", (debt_id, user_id))
        conn.execute("DELETE FROM debts WHERE id = ? AND user_id = ?", (debt_id, user_id))
        conn.commit()
    return jsonify({"status": "success"})


@app.route("/api/customers/suggestions", methods=["GET"])
@login_required
def get_customer_suggestions():
    user_id = session["user"]["id"]
    with get_db() as conn:
        rows = conn.execute("SELECT DISTINCT customer_name, phone FROM debts WHERE user_id = ? ORDER BY customer_name ASC", (user_id,)).fetchall()
    return jsonify([{"name": r["customer_name"], "phone": r["phone"] or ""} for r in rows])


@app.route("/api/reports/export-excel", methods=["GET"])
@login_required
def export_excel():
    user_id = session["user"]["id"]
    with get_db() as conn:
        rows = conn.execute("""
            SELECT d.id, d.customer_name, d.phone, d.total_amount, d.currency,
                   COALESCE(SUM(p.amount_paid), 0) as paid_amount,
                   (d.total_amount - COALESCE(SUM(p.amount_paid), 0)) as remaining,
                   d.due_date, d.status
            FROM debts d LEFT JOIN payments p ON d.id = p.debt_id
            WHERE d.user_id = ?
            GROUP BY d.id ORDER BY d.id DESC
        """, (user_id,)).fetchall()

    output = io.StringIO()
    output.write('\ufeff')
    writer = csv.writer(output)
    writer.writerow(["کۆد", "ناوی کڕیار", "مۆبایل", "کۆی قەرز", "دراو", "ماوە", "دراو", "بەرواری دانەوە", "دۆخ"])
    for r in rows:
        writer.writerow([r["id"], r["customer_name"], r["phone"] or "-", f"{r['total_amount']:,.0f}", f"{r['paid_amount']:,.0f}", f"{r['remaining']:,.0f}", r["currency"], r["due_date"], r["status"]])

    response = Response(output.getvalue(), mimetype="text/csv; charset=utf-8")
    response.headers["Content-Disposition"] = f"attachment; filename=debts_{session['user']['username']}_{date.today().isoformat()}.csv"
    return response


@app.route("/api/admin/backup", methods=["GET"])
@login_required
def download_backup():
    if os.path.exists(DB_NAME):
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return send_file(DB_NAME, as_attachment=True, download_name=f"danyal_backup_{stamp}.db")
    return jsonify({"status": "error"}), 404


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
