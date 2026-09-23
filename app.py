"""
Advanced Debt Management System with Video Splash & Google Auth
"""

import os
import sqlite3
import csv
import io
import json
import base64
from datetime import datetime, date, timedelta
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, send_file, Response
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


def init_db():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT,
                full_name TEXT NOT NULL,
                email TEXT,
                role TEXT NOT NULL DEFAULT 'staff',
                avatar TEXT DEFAULT 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150',
                bio TEXT DEFAULT 'بەکارهێنەری سیستەم',
                created_at TEXT NOT NULL
            )
        """)

        # پشکنینی زیادکردنی ستوونەکان
        for col, col_type in [("email", "TEXT"), ("avatar", "TEXT"), ("bio", "TEXT")]:
            try:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col} {col_type}")
            except sqlite3.OperationalError:
                pass

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS debts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                phone TEXT,
                total_amount REAL NOT NULL,
                debt_date TEXT NOT NULL,
                due_date TEXT NOT NULL,
                note TEXT,
                status TEXT NOT NULL DEFAULT 'pending',
                created_by TEXT,
                created_at TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                debt_id INTEGER NOT NULL,
                amount_paid REAL NOT NULL,
                payment_date TEXT NOT NULL,
                note TEXT,
                received_by TEXT,
                FOREIGN KEY (debt_id) REFERENCES debts (id) ON DELETE CASCADE
            )
        """)

        # دروستکردنی ئەدمینی سەرەکی
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
                "بەڕێوەبەری سەرەکی پڕۆژە",
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


# چوونەژوورەوە لە ڕێگەی گووگڵ (Google OAuth Handler)
@app.route("/api/auth/google", methods=["POST"])
def google_auth():
    data = request.get_json() or {}
    credential = data.get("credential")

    if not credential:
        return jsonify({"status": "error", "message": "ناسنامەی گووگڵ بەردەست نییە"}), 400

    try:
        # پەڕاندنی زانیارییەکان لە تۆکنی JWT ی گووگڵ بەبێ کتێبخانەی دەرەکی
        parts = credential.split(".")
        if len(parts) < 2:
            raise ValueError()
        
        # پڕکردنەوەی باڵانسی Base64
        payload_b64 = parts[1]
        payload_b64 += "=" * ((4 - len(payload_b64) % 4) % 4)
        decoded_bytes = base64.urlsafe_b64decode(payload_b64)
        google_data = json.loads(decoded_bytes.decode("utf-8"))

        email = google_data.get("email")
        full_name = google_data.get("name", "بەکارهێنەری گووگڵ")
        avatar = google_data.get("picture", "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150")
        username = email.split("@")[0]

    except Exception:
        return jsonify({"status": "error", "message": "نەتوانرا زانیارییەکانی گووگڵ بخوێندرێتەوە"}), 400

    with get_db() as conn:
        user = conn.execute("SELECT * FROM users WHERE email = ? OR username = ?", (email, username)).fetchone()
        
        if not user:
            # تۆمارکردنی ئۆتۆماتیکی ئەگەر هەژمارەکە نوێ بێت
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (username, full_name, email, role, avatar, bio, created_at)
                VALUES (?, ?, ?, 'staff', ?, 'چوونەژوورەوە لە ڕێگەی Google', ?)
            """, (username, full_name, email, avatar, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            user_id = cursor.lastrowid
            role = "staff"
            bio = "چوونەژوورەوە لە ڕێگەی Google"
        else:
            user_id = user["id"]
            role = user["role"]
            bio = user["bio"]
            # نوێکردنەوەی وێنەکەی ئەگەر هەبێت
            conn.execute("UPDATE users SET avatar = ? WHERE id = ?", (avatar, user_id))
            conn.commit()

    session["user"] = {
        "id": user_id,
        "username": username,
        "full_name": full_name,
        "email": email,
        "role": role,
        "avatar": avatar,
        "bio": bio
    }

    return jsonify({"status": "success", "user": session["user"]})


# چوونەژوورەوەی ئاسایی بە ئەدمین
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
    return jsonify({"status": "success", "user": session["user"]})


@app.route("/api/auth/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify({"status": "success"})


@app.route("/api/auth/me", methods=["GET"])
def api_me():
    if "user" in session:
        return jsonify({"logged_in": True, "user": session["user"]})
    return jsonify({"logged_in": False})


@app.route("/api/profile/update", methods=["POST"])
@login_required
def update_profile():
    full_name = request.form.get("full_name", "").strip()
    bio = request.form.get("bio", "").strip()
    file = request.files.get("avatar")

    if not full_name:
        return jsonify({"status": "error", "message": "ناو مەرجە"}), 400

    avatar_url = session["user"].get("avatar")
    if file and file.filename != '':
        filename = f"avatar_{session['user']['id']}_{int(datetime.now().timestamp())}.{file.filename.rsplit('.', 1)[1].lower()}"
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)
        avatar_url = f"/static/avatars/{filename}"

    with get_db() as conn:
        conn.execute("UPDATE users SET full_name = ?, bio = ?, avatar = ? WHERE id = ?", (full_name, bio, avatar_url, session["user"]["id"]))
        conn.commit()

    session["user"]["full_name"] = full_name
    session["user"]["bio"] = bio
    session["user"]["avatar"] = avatar_url

    return jsonify({"status": "success", "user": session["user"]})


@app.route("/api/customers/suggestions", methods=["GET"])
@login_required
def get_customer_suggestions():
    with get_db() as conn:
        rows = conn.execute("SELECT DISTINCT customer_name, phone FROM debts ORDER BY customer_name ASC").fetchall()
    return jsonify([{"name": r["customer_name"], "phone": r["phone"] or ""} for r in rows])


@app.route("/api/dashboard/stats", methods=["GET"])
@login_required
def api_dashboard_stats():
    today = date.today().isoformat()
    with get_db() as conn:
        for d in conn.execute("SELECT id FROM debts").fetchall():
            update_debt_status(conn, d["id"])

        total_debt = conn.execute("SELECT COALESCE(SUM(total_amount), 0) as s FROM debts").fetchone()["s"]
        total_paid = conn.execute("SELECT COALESCE(SUM(amount_paid), 0) as s FROM payments").fetchone()["s"]
        overdue_count = conn.execute("SELECT COUNT(*) as c FROM debts WHERE status = 'overdue'").fetchone()["c"]

    return jsonify({
        "total_debt": total_debt,
        "total_paid": total_paid,
        "total_remaining": max(0.0, total_debt - total_paid),
        "overdue_count": overdue_count
    })


@app.route("/api/debts", methods=["GET"])
@login_required
def get_debts():
    search = request.args.get("search", "").strip()
    query = """
        SELECT d.id, d.customer_name, d.phone, d.total_amount, d.debt_date, d.due_date, d.status,
               COALESCE(SUM(p.amount_paid), 0) as paid_amount,
               (d.total_amount - COALESCE(SUM(p.amount_paid), 0)) as remaining_amount
        FROM debts d LEFT JOIN payments p ON d.id = p.debt_id
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
    due_date = data.get("due_date")
    debt_date = data.get("debt_date") or date.today().isoformat()
    note = data.get("note", "").strip()

    if not name or not amount or not due_date:
        return jsonify({"status": "error", "message": "تکایە هەموو خانە سەرەکییەکان پڕبکەرەوە"}), 400

    try:
        amount = float(amount)
    except ValueError:
        return jsonify({"status": "error", "message": "بڕی قەرز دەبێت ژمارە بێت"}), 400

    status = "overdue" if due_date < date.today().isoformat() else "pending"

    with get_db() as conn:
        conn.execute("""
            INSERT INTO debts (customer_name, phone, total_amount, debt_date, due_date, note, status, created_by, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, phone, amount, debt_date, due_date, note, status, session["user"]["username"], datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()

    return jsonify({"status": "success", "message": "قەرزەکە بە سەرکەوتوویی تۆمارکرا"})


@app.route("/api/debts/<int:debt_id>", methods=["DELETE"])
@login_required
def delete_debt(debt_id):
    with get_db() as conn:
        conn.execute("DELETE FROM payments WHERE debt_id = ?", (debt_id,))
        conn.execute("DELETE FROM debts WHERE id = ?", (debt_id,))
        conn.commit()
    return jsonify({"status": "success"})


@app.route("/api/debts/<int:debt_id>/payments", methods=["POST"])
@login_required
def make_payment(debt_id):
    data = request.get_json() or {}
    amount = float(data.get("amount", 0))
    note = data.get("note", "").strip()

    with get_db() as conn:
        debt = conn.execute("SELECT total_amount FROM debts WHERE id = ?", (debt_id,)).fetchone()
        if not debt:
            return jsonify({"status": "error", "message": "قەرز نەدۆزرایەوە"}), 404

        conn.execute("""
            INSERT INTO payments (debt_id, amount_paid, payment_date, note, received_by)
            VALUES (?, ?, ?, ?, ?)
        """, (debt_id, amount, date.today().isoformat(), note, session["user"]["username"]))
        conn.commit()
        update_debt_status(conn, debt_id)

    return jsonify({"status": "success"})


@app.route("/api/reports/export-excel", methods=["GET"])
@login_required
def export_excel():
    with get_db() as conn:
        rows = conn.execute("""
            SELECT d.id, d.customer_name, d.phone, d.total_amount,
                   COALESCE(SUM(p.amount_paid), 0) as paid_amount,
                   (d.total_amount - COALESCE(SUM(p.amount_paid), 0)) as remaining,
                   d.due_date, d.status
            FROM debts d LEFT JOIN payments p ON d.id = p.debt_id
            GROUP BY d.id ORDER BY d.id DESC
        """).fetchall()

    output = io.StringIO()
    output.write('\ufeff')
    writer = csv.writer(output)
    writer.writerow(["کۆد", "ناوی کڕیار", "مۆبایل", "کۆی قەرز", "دراو", "ماوە", "بەرواری دانەوە", "دۆخ"])
    for r in rows:
        writer.writerow([r["id"], r["customer_name"], r["phone"] or "-", f"{r['total_amount']:,.0f}", f"{r['paid_amount']:,.0f}", f"{r['remaining']:,.0f}", r["due_date"], r["status"]])

    response = Response(output.getvalue(), mimetype="text/csv; charset=utf-8")
    response.headers["Content-Disposition"] = f"attachment; filename=debts_{date.today().isoformat()}.csv"
    return response


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
