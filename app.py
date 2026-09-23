"""
Commercial Debt & Financial System (POS & Management)
Author: Danyal App Architecture
"""

import os
import sqlite3
import csv
import io
import json
import base64
from datetime import datetime, date, timedelta
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, Response, send_file
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.urandom(32)
app.permanent_session_lifetime = timedelta(days=7)

DB_NAME = "debt_pro.db"
UPLOAD_FOLDER = os.path.join("static", "avatars")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def log_audit(conn, username, action, details):
    conn.execute("""
        INSERT INTO audit_logs (username, action, details, created_at)
        VALUES (?, ?, ?, ?)
    """, (username, action, details, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))


def init_db():
    with get_db() as conn:
        cursor = conn.cursor()

        # ١. خشتەی بەکارهێنەران
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT,
                full_name TEXT NOT NULL,
                email TEXT,
                role TEXT NOT NULL DEFAULT 'admin',
                avatar TEXT DEFAULT 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150',
                bio TEXT DEFAULT 'بەڕێوەبەری سیستەمی دارایی',
                created_at TEXT NOT NULL
            )
        """)

        # ٢. خشتەی قەرزەکان
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS debts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                phone TEXT,
                total_amount REAL NOT NULL,
                currency TEXT NOT NULL DEFAULT 'IQD',
                debt_date TEXT NOT NULL,
                due_date TEXT NOT NULL,
                note TEXT,
                is_installment INTEGER DEFAULT 0,
                installment_count INTEGER DEFAULT 1,
                status TEXT NOT NULL DEFAULT 'pending',
                created_by TEXT,
                created_at TEXT NOT NULL
            )
        """)

        # ٣. خشتەی قیستەکان
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS installments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                debt_id INTEGER NOT NULL,
                installment_no INTEGER NOT NULL,
                amount REAL NOT NULL,
                due_date TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                paid_date TEXT,
                FOREIGN KEY (debt_id) REFERENCES debts (id) ON DELETE CASCADE
            )
        """)

        # ٤. خشتەی وەسڵ و واسڵکردن
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                debt_id INTEGER NOT NULL,
                receipt_no TEXT UNIQUE NOT NULL,
                amount_paid REAL NOT NULL,
                payment_date TEXT NOT NULL,
                note TEXT,
                received_by TEXT,
                FOREIGN KEY (debt_id) REFERENCES debts (id) ON DELETE CASCADE
            )
        """)

        # ٥. خشتەی لۆگی چاودێری
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT,
                created_at TEXT NOT NULL
            )
        """)

        # دروستکردنی هەژماری سەرەکی
        admin = cursor.execute("SELECT * FROM users WHERE username = 'admin'").fetchone()
        if not admin:
            cursor.execute("""
                INSERT INTO users (username, password_hash, full_name, email, role, avatar, bio, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "admin",
                generate_password_hash("admin123"),
                "دانیال ئیسماعیل",
                "admin@danyal.app",
                "admin",
                "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150",
                "بەڕێوەبەری سەرەکی سیستەم",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
        conn.commit()

init_db()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return jsonify({"status": "error", "message": "تکایە سەرەتا بچۆ ژوورەوە"}), 401
        return f(*args, **kwargs)
    return decorated_function


def update_debt_status(conn, debt_id):
    debt = conn.execute("SELECT total_amount, due_date FROM debts WHERE id = ?", (debt_id,)).fetchone()
    if not debt:
        return

    paid_sum = conn.execute(
        "SELECT COALESCE(SUM(amount_paid), 0) as total FROM payments WHERE debt_id = ?", (debt_id,)
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

    conn.execute("UPDATE debts SET status = ? WHERE id = ?", (status, debt_id))
    conn.commit()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/auth/login", methods=["POST"])
def api_login():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    with get_db() as conn:
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if not user or not user["password_hash"] or not check_password_hash(user["password_hash"], password):
            return jsonify({"status": "error", "message": "ناوی بەکارهێنەر یان وشەی نهێنی هەڵەیە!"}), 401

        session["user"] = {
            "id": user["id"],
            "username": user["username"],
            "full_name": user["full_name"],
            "role": user["role"],
            "avatar": user["avatar"],
            "bio": user["bio"]
        }
        log_audit(conn, user["username"], "LOGIN", "چوونەژوورەوەی ئاسایی بە سەرکەوتوویی")
        conn.commit()

    return jsonify({"status": "success", "user": session["user"]})


@app.route("/api/auth/google", methods=["POST"])
def google_auth():
    data = request.get_json() or {}
    credential = data.get("credential")
    if not credential:
        return jsonify({"status": "error", "message": "بڕوانامەی گووگڵ نەدۆزرایەوە"}), 400

    try:
        parts = credential.split(".")
        payload_b64 = parts[1] + "=" * ((4 - len(parts[1]) % 4) % 4)
        google_data = json.loads(base64.urlsafe_b64decode(payload_b64).decode("utf-8"))

        email = google_data.get("email")
        full_name = google_data.get("name", "بەکارهێنەری گووگڵ")
        avatar = google_data.get("picture", "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150")
        username = email.split("@")[0]
    except Exception:
        return jsonify({"status": "error", "message": "هەڵە لە وەرگرتنی زانیاری گووگڵ"}), 400

    with get_db() as conn:
        user = conn.execute("SELECT * FROM users WHERE email = ? OR username = ?", (email, username)).fetchone()
        if not user:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (username, full_name, email, role, avatar, bio, created_at)
                VALUES (?, ?, ?, 'staff', ?, 'هەژماری گووگڵ', ?)
            """, (username, full_name, email, avatar, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            user_id = cursor.lastrowid
            role, bio = "staff", "هەژماری گووگڵ"
        else:
            user_id, role, bio = user["id"], user["role"], user["bio"]
            conn.execute("UPDATE users SET avatar = ? WHERE id = ?", (avatar, user_id))

        session["user"] = {
            "id": user_id,
            "username": username,
            "full_name": full_name,
            "email": email,
            "role": role,
            "avatar": avatar,
            "bio": bio
        }
        log_audit(conn, username, "GOOGLE_LOGIN", f"چوونەژوورەوە لە ڕێگەی {email}")
        conn.commit()

    return jsonify({"status": "success", "user": session["user"]})


@app.route("/api/auth/logout", methods=["POST"])
def api_logout():
    if "user" in session:
        with get_db() as conn:
            log_audit(conn, session["user"]["username"], "LOGOUT", "دەرچوون لە سیستەم")
            conn.commit()
    session.clear()
    return jsonify({"status": "success"})


@app.route("/api/auth/me", methods=["GET"])
def api_me():
    if "user" in session:
        with get_db() as conn:
            user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user"]["id"],)).fetchone()
            if user:
                session["user"] = {
                    "id": user["id"],
                    "username": user["username"],
                    "full_name": user["full_name"],
                    "role": user["role"],
                    "avatar": user["avatar"],
                    "bio": user["bio"]
                }
        return jsonify({"logged_in": True, "user": session["user"]})
    return jsonify({"logged_in": False})


@app.route("/api/profile/update", methods=["POST"])
@login_required
def update_profile():
    full_name = request.form.get("full_name", "").strip()
    bio = request.form.get("bio", "").strip()
    file = request.files.get("avatar")

    if not full_name:
        return jsonify({"status": "error", "message": "ناو پێویستە بنووسرێت"}), 400

    avatar_url = session["user"].get("avatar")
    if file and file.filename != '':
        filename = f"avatar_{session['user']['id']}_{int(datetime.now().timestamp())}.{file.filename.rsplit('.', 1)[1].lower()}"
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)
        avatar_url = f"/static/avatars/{filename}"

    with get_db() as conn:
        conn.execute("UPDATE users SET full_name = ?, bio = ?, avatar = ? WHERE id = ?", (full_name, bio, avatar_url, session["user"]["id"]))
        log_audit(conn, session["user"]["username"], "UPDATE_PROFILE", "نوێکردنەوەی پرۆفایل و وێنە")
        conn.commit()

    session["user"]["full_name"] = full_name
    session["user"]["bio"] = bio
    session["user"]["avatar"] = avatar_url

    return jsonify({"status": "success", "user": session["user"]})


@app.route("/api/dashboard/analytics", methods=["GET"])
@login_required
def dashboard_analytics():
    today = date.today().isoformat()
    with get_db() as conn:
        for d in conn.execute("SELECT id FROM debts").fetchall():
            update_debt_status(conn, d["id"])

        iqd_debt = conn.execute("SELECT COALESCE(SUM(total_amount), 0) as s FROM debts WHERE currency = 'IQD'").fetchone()["s"]
        iqd_paid = conn.execute("""
            SELECT COALESCE(SUM(p.amount_paid), 0) as s 
            FROM payments p JOIN debts d ON p.debt_id = d.id WHERE d.currency = 'IQD'
        """).fetchone()["s"]

        usd_debt = conn.execute("SELECT COALESCE(SUM(total_amount), 0) as s FROM debts WHERE currency = 'USD'").fetchone()["s"]
        usd_paid = conn.execute("""
            SELECT COALESCE(SUM(p.amount_paid), 0) as s 
            FROM payments p JOIN debts d ON p.debt_id = d.id WHERE d.currency = 'USD'
        """).fetchone()["s"]

        overdue_count = conn.execute("SELECT COUNT(*) as c FROM debts WHERE status = 'overdue'").fetchone()["c"]
        due_today_count = conn.execute("SELECT COUNT(*) as c FROM debts WHERE due_date = ? AND status != 'paid'", (today,)).fetchone()["c"]

        top_debtors_raw = conn.execute("""
            SELECT d.customer_name, (d.total_amount - COALESCE(SUM(p.amount_paid), 0)) as remaining
            FROM debts d LEFT JOIN payments p ON d.id = p.debt_id
            GROUP BY d.id HAVING remaining > 0 ORDER BY remaining DESC LIMIT 5
        """).fetchall()

        monthly_payments = conn.execute("""
            SELECT strftime('%Y-%m', payment_date) as month, SUM(amount_paid) as total
            FROM payments GROUP BY month ORDER BY month DESC LIMIT 6
        """).fetchall()

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
    search = request.args.get("search", "").strip()
    query = """
        SELECT d.id, d.customer_name, d.phone, d.total_amount, d.currency,
               d.debt_date, d.due_date, d.status, d.is_installment, d.installment_count, d.note,
               COALESCE(SUM(p.amount_paid), 0) as paid_amount,
               (d.total_amount - COALESCE(SUM(p.amount_paid), 0)) as remaining_amount
        FROM debts d
        LEFT JOIN payments p ON d.id = p.debt_id
        WHERE 1=1
    """
    params = []
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
    data = request.get_json() or {}
    name = data.get("customer_name", "").strip()
    phone = data.get("phone", "").strip()
    amount = data.get("total_amount")
    currency = data.get("currency", "IQD")
    debt_date = data.get("debt_date") or date.today().isoformat()
    due_date = data.get("due_date")
    note = data.get("note", "").strip()
    is_installment = 1 if data.get("is_installment") else 0
    installments_count = int(data.get("installment_count", 1))

    if not name or not amount or not due_date:
        return jsonify({"status": "error", "message": "تکایە خانە مەرجدارەکان پڕبکەرەوە"}), 400

    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError()
    except ValueError:
        return jsonify({"status": "error", "message": "بڕی پارە نادروستە"}), 400

    status = "overdue" if due_date < date.today().isoformat() else "pending"

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO debts (customer_name, phone, total_amount, currency, debt_date, due_date, note, is_installment, installment_count, status, created_by, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, phone, amount, currency, debt_date, due_date, note, is_installment, installments_count, status, session["user"]["username"], datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        debt_id = cursor.lastrowid

        if is_installment and installments_count > 1:
            part_amount = round(amount / installments_count, 2)
            base_date = datetime.strptime(debt_date, "%Y-%m-%d")
            for i in range(1, installments_count + 1):
                inst_due = (base_date + timedelta(days=30 * i)).strftime("%Y-%m-%d")
                cursor.execute("""
                    INSERT INTO installments (debt_id, installment_no, amount, due_date, status)
                    VALUES (?, ?, ?, ?, 'pending')
                """, (debt_id, i, part_amount, inst_due))

        log_audit(conn, session["user"]["username"], "ADD_DEBT", f"قەرزی نوێ بۆ {name} بە بڕی {amount} {currency}")
        conn.commit()

    return jsonify({"status": "success", "message": "قەرزەکە بە سەرکەوتوویی تۆمارکرا"})


@app.route("/api/debts/<int:debt_id>/payments", methods=["POST"])
@login_required
def make_payment(debt_id):
    data = request.get_json() or {}
    amount = float(data.get("amount", 0))
    note = data.get("note", "").strip()

    if amount <= 0:
        return jsonify({"status": "error", "message": "بڕی واسڵکراو دەبێت لە سفر زیاتر بێت"}), 400

    with get_db() as conn:
        debt = conn.execute("SELECT * FROM debts WHERE id = ?", (debt_id,)).fetchone()
        if not debt:
            return jsonify({"status": "error", "message": "قەرزەکە نەدۆزرایەوە"}), 404

        current_paid = conn.execute(
            "SELECT COALESCE(SUM(amount_paid), 0) as s FROM payments WHERE debt_id = ?", (debt_id,)
        ).fetchone()["s"]

        remaining_before = debt["total_amount"] - current_paid
        if amount > remaining_before:
            return jsonify({"status": "error", "message": f"بڕی دراو زۆرترە لە ماوە! ({remaining_before:,.0f} {debt['currency']})"}), 400

        receipt_no = f"REC-{datetime.now().strftime('%y%m%d')}-{debt_id}-{int(datetime.now().timestamp()) % 1000}"

        conn.execute("""
            INSERT INTO payments (debt_id, receipt_no, amount_paid, payment_date, note, received_by)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (debt_id, receipt_no, amount, datetime.now().strftime("%Y-%m-%d %H:%M"), note, session["user"]["username"]))

        update_debt_status(conn, debt_id)
        log_audit(conn, session["user"]["username"], "PAYMENT", f"وەرگرتنی {amount} {debt['currency']} بۆ وەسڵی #{receipt_no}")
        conn.commit()

        remaining_after = remaining_before - amount

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
    with get_db() as conn:
        debt = conn.execute("SELECT customer_name FROM debts WHERE id = ?", (debt_id,)).fetchone()
        conn.execute("DELETE FROM installments WHERE debt_id = ?", (debt_id,))
        conn.execute("DELETE FROM payments WHERE debt_id = ?", (debt_id,))
        conn.execute("DELETE FROM debts WHERE id = ?", (debt_id,))
        if debt:
            log_audit(conn, session["user"]["username"], "DELETE_DEBT", f"سڕینەوەی قەرزی {debt['customer_name']}")
        conn.commit()
    return jsonify({"status": "success"})


@app.route("/api/customers/suggestions", methods=["GET"])
@login_required
def get_customer_suggestions():
    with get_db() as conn:
        rows = conn.execute("SELECT DISTINCT customer_name, phone FROM debts ORDER BY customer_name ASC").fetchall()
    return jsonify([{"name": r["customer_name"], "phone": r["phone"] or ""} for r in rows])


@app.route("/api/audit-logs", methods=["GET"])
@login_required
def get_audit_logs():
    with get_db() as conn:
        logs = conn.execute("SELECT * FROM audit_logs ORDER BY id DESC LIMIT 40").fetchall()
    return jsonify([dict(l) for l in logs])


@app.route("/api/admin/backup", methods=["GET"])
@login_required
def download_backup():
    if os.path.exists(DB_NAME):
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return send_file(DB_NAME, as_attachment=True, download_name=f"debt_backup_{stamp}.db")
    return jsonify({"status": "error"}), 404


@app.route("/api/reports/export-excel", methods=["GET"])
@login_required
def export_excel():
    with get_db() as conn:
        rows = conn.execute("""
            SELECT d.id, d.customer_name, d.phone, d.total_amount, d.currency,
                   COALESCE(SUM(p.amount_paid), 0) as paid_amount,
                   (d.total_amount - COALESCE(SUM(p.amount_paid), 0)) as remaining,
                   d.due_date, d.status
            FROM debts d LEFT JOIN payments p ON d.id = p.debt_id
            GROUP BY d.id ORDER BY d.id DESC
        """).fetchall()

    output = io.StringIO()
    output.write('\ufeff')
    writer = csv.writer(output)
    writer.writerow(["کۆد", "ناوی کڕیار", "مۆبایل", "کۆی قەرز", "دراو", "ماوە", "دراو", "بەرواری دانەوە", "دۆخ"])
    for r in rows:
        writer.writerow([r["id"], r["customer_name"], r["phone"] or "-", f"{r['total_amount']:,.0f}", f"{r['paid_amount']:,.0f}", f"{r['remaining']:,.0f}", r["currency"], r["due_date"], r["status"]])

    response = Response(output.getvalue(), mimetype="text/csv; charset=utf-8")
    response.headers["Content-Disposition"] = f"attachment; filename=debts_{date.today().isoformat()}.csv"
    return response


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
