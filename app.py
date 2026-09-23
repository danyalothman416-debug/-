"""
Commercial Multi-Tenant SaaS Debt Management System
Engineered for Production, Data Isolation & Subscription Licensing
Author: Danyal App Architecture
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
# لە ژینگەی ڕاستەقینە کلیلێکی جێگیر لە Environment دابنێ
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(32))
app.permanent_session_lifetime = timedelta(days=30)

DB_NAME = "saas_debt_pro.db"
UPLOAD_FOLDER = os.path.join("static", "avatars")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    # چالاککردنی WAL Mode بۆ ئەوەی چەندین بەکارهێنەر لە یەک کاتدا بەبێ کێشە بنووسن
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def init_db():
    with get_db() as conn:
        cursor = conn.cursor()

        # ١. خشتەی دوکان و بزنسەکان (Multi-Tenancy)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS businesses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_name TEXT NOT NULL,
                owner_phone TEXT NOT NULL,
                subscription_plan TEXT NOT NULL DEFAULT 'trial', -- 'trial', 'pro', 'lifetime'
                subscription_status TEXT NOT NULL DEFAULT 'active', -- 'active', 'expired'
                expires_at TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        # ٢. خشتەی بەکارهێنەران (پەیوەست بە دوکانی دیاریکراو)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_id INTEGER NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'owner', -- 'owner', 'staff'
                avatar TEXT DEFAULT 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150',
                bio TEXT DEFAULT 'بەڕێوەبەری سیستەم',
                created_at TEXT NOT NULL,
                FOREIGN KEY (business_id) REFERENCES businesses (id) ON DELETE CASCADE
            )
        """)

        # ٣. خشتەی قەرزەکان (دابڕاو بەپێی business_id)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS debts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_id INTEGER NOT NULL,
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
                created_at TEXT NOT NULL,
                FOREIGN KEY (business_id) REFERENCES businesses (id) ON DELETE CASCADE
            )
        """)

        # ٤. خشتەی قیستەکان
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS installments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_id INTEGER NOT NULL,
                debt_id INTEGER NOT NULL,
                installment_no INTEGER NOT NULL,
                amount REAL NOT NULL,
                due_date TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                paid_date TEXT,
                FOREIGN KEY (business_id) REFERENCES businesses (id) ON DELETE CASCADE,
                FOREIGN KEY (debt_id) REFERENCES debts (id) ON DELETE CASCADE
            )
        """)

        # ٥. خشتەی وەسڵ و واسڵکردن
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_id INTEGER NOT NULL,
                debt_id INTEGER NOT NULL,
                receipt_no TEXT NOT NULL,
                amount_paid REAL NOT NULL,
                payment_date TEXT NOT NULL,
                note TEXT,
                received_by TEXT,
                FOREIGN KEY (business_id) REFERENCES businesses (id) ON DELETE CASCADE,
                FOREIGN KEY (debt_id) REFERENCES debts (id) ON DELETE CASCADE
            )
        """)

        # ٦. لۆگی چاودێری
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (business_id) REFERENCES businesses (id) ON DELETE CASCADE
            )
        """)

        conn.commit()

init_db()


# پشکنینی لۆگین
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return jsonify({"status": "error", "message": "تکایە سەرەتا بچۆ ژوورەوە"}), 401
        return f(*args, **kwargs)
    return decorated_function


# پشکنینی ماوەی بەشداریکردن (Subscription Lock)
def subscription_active(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        biz = session.get("business")
        if not biz:
            return jsonify({"status": "error", "message": "زانیاری بزنس نەدۆزرایەوە"}), 403
        
        expires_date = datetime.strptime(biz["expires_at"], "%Y-%m-%d").date()
        if date.today() > expires_date:
            return jsonify({
                "status": "error",
                "subscription_expired": True,
                "message": "ماوەی بەکارهێنانی سیستەمەکەت بەسەرچووە! تکایە پەیوەندی بکە بۆ نوێکردنەوە."
            }), 403
        return f(*args, **kwargs)
    return decorated_function


def log_audit(conn, biz_id, username, action, details):
    try:
        conn.execute("""
            INSERT INTO audit_logs (business_id, username, action, details, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (biz_id, username, action, details, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    except Exception:
        pass


def update_debt_status(conn, biz_id, debt_id):
    debt = conn.execute("SELECT total_amount, due_date FROM debts WHERE id = ? AND business_id = ?", (debt_id, biz_id)).fetchone()
    if not debt:
        return

    paid_sum = conn.execute(
        "SELECT COALESCE(SUM(amount_paid), 0) as total FROM payments WHERE debt_id = ? AND business_id = ?", (debt_id, biz_id)
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

    conn.execute("UPDATE debts SET status = ? WHERE id = ? AND business_id = ?", (status, debt_id, biz_id))
    conn.commit()


@app.route("/")
def index():
    return render_template("index.html")


# --- Auth: Registration & Multi-Tenancy Creation ---
@app.route("/api/auth/register", methods=["POST"])
def api_register():
    data = request.get_json(force=True) or {}
    biz_name = data.get("business_name", "").strip()
    owner_name = data.get("full_name", "").strip()
    phone = data.get("phone", "").strip()
    username = data.get("username", "").strip().lower()
    password = data.get("password", "").strip()

    if not biz_name or not owner_name or not username or not password:
        return jsonify({"status": "error", "message": "تکایە هەموو خانەکان پڕبکەرەوە"}), 400

    # بەخشینی ١٤ ڕۆژ تاقیکردنەوەی بەخۆڕایی
    trial_expiry = (date.today() + timedelta(days=14)).isoformat()

    with get_db() as conn:
        existing = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
        if existing:
            return jsonify({"status": "error", "message": "ئەم ناوی بەکارهێنەرە پێشتر تۆمارکراوە"}), 409

        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO businesses (business_name, owner_phone, subscription_plan, subscription_status, expires_at, created_at)
            VALUES (?, ?, 'trial', 'active', ?, ?)
        """, (biz_name, phone, trial_expiry, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        biz_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO users (business_id, username, password_hash, full_name, role, created_at)
            VALUES (?, ?, ?, ?, 'owner', ?)
        """, (biz_id, username, generate_password_hash(password), owner_name, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        user_id = cursor.lastrowid

        log_audit(conn, biz_id, username, "REGISTER", f"تۆمارکردنی دوکانی نوێ: {biz_name}")
        conn.commit()

    session.permanent = True
    session["user"] = {"id": user_id, "username": username, "full_name": owner_name, "role": "owner"}
    session["business"] = {"id": biz_id, "name": biz_name, "plan": "trial", "expires_at": trial_expiry}

    return jsonify({"status": "success", "message": "دوکانەکەت بە سەرکەوتوویی دروستکرا", "user": session["user"], "business": session["business"]})


@app.route("/api/auth/login", methods=["POST"])
def api_login():
    data = request.get_json(force=True) or {}
    username = data.get("username", "").strip().lower()
    password = data.get("password", "").strip()

    with get_db() as conn:
        user = conn.execute("""
            SELECT u.*, b.business_name, b.subscription_plan, b.subscription_status, b.expires_at 
            FROM users u JOIN businesses b ON u.business_id = b.id 
            WHERE u.username = ?
        """, (username,)).fetchone()

        if not user or not check_password_hash(user["password_hash"], password):
            return jsonify({"status": "error", "message": "ناوی بەکارهێنەر یان وشەی نهێنی هەڵەیە!"}), 401

        session.permanent = True
        session["user"] = {
            "id": user["id"],
            "username": user["username"],
            "full_name": user["full_name"],
            "role": user["role"],
            "avatar": user["avatar"],
            "bio": user["bio"]
        }
        session["business"] = {
            "id": user["business_id"],
            "name": user["business_name"],
            "plan": user["subscription_plan"],
            "expires_at": user["expires_at"]
        }
        log_audit(conn, user["business_id"], user["username"], "LOGIN", "چوونەژوورەوە بۆ ناو سیستەم")
        conn.commit()

    return jsonify({"status": "success", "user": session["user"], "business": session["business"]})


@app.route("/api/auth/me", methods=["GET"])
def api_me():
    if "user" in session and "business" in session:
        # نوێکردنەوەی ڕۆژەکانی بەسەرچوون
        with get_db() as conn:
            biz = conn.execute("SELECT * FROM businesses WHERE id = ?", (session["business"]["id"],)).fetchone()
            if biz:
                session["business"] = {
                    "id": biz["id"],
                    "name": biz["business_name"],
                    "plan": biz["subscription_plan"],
                    "expires_at": biz["expires_at"]
                }
        days_left = (datetime.strptime(session["business"]["expires_at"], "%Y-%m-%d").date() - date.today()).days
        return jsonify({
            "logged_in": True,
            "user": session["user"],
            "business": session["business"],
            "days_left": max(0, days_left),
            "is_expired": days_left < 0
        })
    return jsonify({"logged_in": False})


@app.route("/api/auth/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify({"status": "success"})


# --- Dashboard Analytics (دابڕاو بەپێی business_id) ---
@app.route("/api/dashboard/analytics", methods=["GET"])
@login_required
def dashboard_analytics():
    biz_id = session["business"]["id"]
    today = date.today().isoformat()

    with get_db() as conn:
        for d in conn.execute("SELECT id FROM debts WHERE business_id = ?", (biz_id,)).fetchall():
            update_debt_status(conn, biz_id, d["id"])

        iqd_debt = conn.execute("SELECT COALESCE(SUM(total_amount), 0) as s FROM debts WHERE business_id = ? AND currency = 'IQD'", (biz_id,)).fetchone()["s"]
        iqd_paid = conn.execute("""
            SELECT COALESCE(SUM(p.amount_paid), 0) as s 
            FROM payments p JOIN debts d ON p.debt_id = d.id 
            WHERE p.business_id = ? AND d.currency = 'IQD'
        """, (biz_id,)).fetchone()["s"]

        usd_debt = conn.execute("SELECT COALESCE(SUM(total_amount), 0) as s FROM debts WHERE business_id = ? AND currency = 'USD'", (biz_id,)).fetchone()["s"]
        usd_paid = conn.execute("""
            SELECT COALESCE(SUM(p.amount_paid), 0) as s 
            FROM payments p JOIN debts d ON p.debt_id = d.id 
            WHERE p.business_id = ? AND d.currency = 'USD'
        """, (biz_id,)).fetchone()["s"]

        overdue_count = conn.execute("SELECT COUNT(*) as c FROM debts WHERE business_id = ? AND status = 'overdue'", (biz_id,)).fetchone()["c"]
        due_today_count = conn.execute("SELECT COUNT(*) as c FROM debts WHERE business_id = ? AND due_date = ? AND status != 'paid'", (biz_id, today)).fetchone()["c"]

        top_debtors_raw = conn.execute("""
            SELECT d.customer_name, (d.total_amount - COALESCE(SUM(p.amount_paid), 0)) as remaining
            FROM debts d LEFT JOIN payments p ON d.id = p.debt_id
            WHERE d.business_id = ?
            GROUP BY d.id HAVING remaining > 0 ORDER BY remaining DESC LIMIT 5
        """, (biz_id,)).fetchall()

        monthly_payments = conn.execute("""
            SELECT strftime('%Y-%m', payment_date) as month, SUM(amount_paid) as total
            FROM payments WHERE business_id = ?
            GROUP BY month ORDER BY month DESC LIMIT 6
        """, (biz_id,)).fetchall()

    return jsonify({
        "iqd": {"debt": iqd_debt, "paid": iqd_paid, "remaining": max(0.0, iqd_debt - iqd_paid)},
        "usd": {"debt": usd_debt, "paid": usd_paid, "remaining": max(0.0, usd_debt - usd_paid)},
        "overdue_count": overdue_count,
        "due_today_count": due_today_count,
        "top_debtors": [dict(r) for r in top_debtors_raw],
        "monthly_chart": [dict(m) for m in reversed(monthly_payments)]
    })


# --- Debts Endpoints (دابڕاو بەپێی business_id) ---
@app.route("/api/debts", methods=["GET"])
@login_required
def get_debts():
    biz_id = session["business"]["id"]
    search = request.args.get("search", "").strip()

    query = """
        SELECT d.id, d.customer_name, d.phone, d.total_amount, d.currency,
               d.debt_date, d.due_date, d.status, d.is_installment, d.installment_count, d.note,
               COALESCE(SUM(p.amount_paid), 0) as paid_amount,
               (d.total_amount - COALESCE(SUM(p.amount_paid), 0)) as remaining_amount
        FROM debts d
        LEFT JOIN payments p ON d.id = p.debt_id
        WHERE d.business_id = ?
    """
    params = [biz_id]
    if search:
        query += " AND (d.customer_name LIKE ? OR d.phone LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])

    query += " GROUP BY d.id ORDER BY d.id DESC"

    with get_db() as conn:
        rows = conn.execute(query, params).fetchall()

    return jsonify([dict(r) for r in rows])


@app.route("/api/debts", methods=["POST"])
@login_required
@subscription_active
def create_debt():
    biz_id = session["business"]["id"]
    data = request.get_json(force=True) or {}
    name = data.get("customer_name", "").strip()
    phone = data.get("phone", "").strip()
    amount = data.get("total_amount")
    currency = data.get("currency", "IQD")
    debt_date = data.get("debt_date") or date.today().isoformat()
    due_date = data.get("due_date")
    note = data.get("note", "").strip()

    if not name or not amount or not due_date:
        return jsonify({"status": "error", "message": "تکایە ناو، بڕی پارە و بەرواری دانەوە بنووسە"}), 400

    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError()
    except (TypeError, ValueError):
        return jsonify({"status": "error", "message": "بڕی پارە دەبێت ژمارەیەکی دروست بێت"}), 400

    status = "overdue" if due_date < date.today().isoformat() else "pending"
    username = session["user"]["username"]

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO debts (business_id, customer_name, phone, total_amount, currency, debt_date, due_date, note, status, created_by, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (biz_id, name, phone, amount, currency, debt_date, due_date, note, status, username, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        debt_id = cursor.lastrowid

        log_audit(conn, biz_id, username, "ADD_DEBT", f"قەرزی نوێ بۆ {name} بە بڕی {amount} {currency}")
        conn.commit()

    return jsonify({"status": "success", "message": "قەرزەکە تۆمارکرا"})


@app.route("/api/debts/<int:debt_id>/payments", methods=["POST"])
@login_required
@subscription_active
def make_payment(debt_id):
    biz_id = session["business"]["id"]
    data = request.get_json(force=True) or {}
    try:
        amount = float(data.get("amount", 0))
    except (TypeError, ValueError):
        amount = 0.0

    note = data.get("note", "").strip()
    if amount <= 0:
        return jsonify({"status": "error", "message": "بڕی پارە دەبێت لە ٠ زیاتر بێت"}), 400

    username = session["user"]["username"]

    with get_db() as conn:
        debt = conn.execute("SELECT * FROM debts WHERE id = ? AND business_id = ?", (debt_id, biz_id)).fetchone()
        if not debt:
            return jsonify({"status": "error", "message": "قەرزەکە نەدۆزرایەوە"}), 404

        current_paid = conn.execute(
            "SELECT COALESCE(SUM(amount_paid), 0) as s FROM payments WHERE debt_id = ? AND business_id = ?", (debt_id, biz_id)
        ).fetchone()["s"]

        remaining = debt["total_amount"] - current_paid
        if amount > remaining:
            return jsonify({"status": "error", "message": f"بڕی دراو لە ماوە زیاترە! ({remaining:,.0f} {debt['currency']})"}), 400

        receipt_no = f"REC-{biz_id}-{int(datetime.now().timestamp()) % 100000}"

        conn.execute("""
            INSERT INTO payments (business_id, debt_id, receipt_no, amount_paid, payment_date, note, received_by)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (biz_id, debt_id, receipt_no, amount, datetime.now().strftime("%Y-%m-%d %H:%M"), note, username))

        update_debt_status(conn, biz_id, debt_id)
        log_audit(conn, biz_id, username, "PAYMENT", f"وەرگرتنی {amount} {debt['currency']} بۆ وەسڵی #{receipt_no}")
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
@subscription_active
def delete_debt(debt_id):
    biz_id = session["business"]["id"]
    with get_db() as conn:
        debt = conn.execute("SELECT customer_name FROM debts WHERE id = ? AND business_id = ?", (debt_id, biz_id)).fetchone()
        if debt:
            conn.execute("DELETE FROM payments WHERE debt_id = ? AND business_id = ?", (debt_id, biz_id))
            conn.execute("DELETE FROM debts WHERE id = ? AND business_id = ?", (debt_id, biz_id))
            log_audit(conn, biz_id, session["user"]["username"], "DELETE_DEBT", f"سڕینەوەی قەرزی {debt['customer_name']}")
            conn.commit()
    return jsonify({"status": "success"})


@app.route("/api/customers/suggestions", methods=["GET"])
@login_required
def get_customer_suggestions():
    biz_id = session["business"]["id"]
    with get_db() as conn:
        rows = conn.execute("SELECT DISTINCT customer_name, phone FROM debts WHERE business_id = ? ORDER BY customer_name ASC", (biz_id,)).fetchall()
    return jsonify([{"name": r["customer_name"], "phone": r["phone"] or ""} for r in rows])


@app.route("/api/reports/export-excel", methods=["GET"])
@login_required
def export_excel():
    biz_id = session["business"]["id"]
    with get_db() as conn:
        rows = conn.execute("""
            SELECT d.id, d.customer_name, d.phone, d.total_amount, d.currency,
                   COALESCE(SUM(p.amount_paid), 0) as paid_amount,
                   (d.total_amount - COALESCE(SUM(p.amount_paid), 0)) as remaining,
                   d.due_date, d.status
            FROM debts d LEFT JOIN payments p ON d.id = p.debt_id
            WHERE d.business_id = ?
            GROUP BY d.id ORDER BY d.id DESC
        """, (biz_id,)).fetchall()

    output = io.StringIO()
    output.write('\ufeff')
    writer = csv.writer(output)
    writer.writerow(["کۆد", "ناوی کڕیار", "مۆبایل", "کۆی قەرز", "دراو", "ماوە", "دراو", "بەرواری دانەوە", "دۆخ"])
    for r in rows:
        writer.writerow([r["id"], r["customer_name"], r["phone"] or "-", f"{r['total_amount']:,.0f}", f"{r['paid_amount']:,.0f}", f"{r['remaining']:,.0f}", r["currency"], r["due_date"], r["status"]])

    response = Response(output.getvalue(), mimetype="text/csv; charset=utf-8")
    response.headers["Content-Disposition"] = f"attachment; filename=debts_{session['business']['name']}_{date.today().isoformat()}.csv"
    return response


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
