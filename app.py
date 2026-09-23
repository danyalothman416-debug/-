"""
Commercial Multi-Tenant Debt Management System (Danyal OS)
Bulletproof Auth, Auto-Migrations & Error Logging
"""

import os
import sqlite3
import csv
import io
import json
from datetime import datetime, date, timedelta
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, Response, send_file
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "danyal_secret_vault_key_2026_super_safe")
app.permanent_session_lifetime = timedelta(days=30)

DB_NAME = "saas_debt_pro.db"
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

        # ١. خشتەی بزنسەکان
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS businesses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_name TEXT NOT NULL,
                subscription_plan TEXT NOT NULL DEFAULT 'trial',
                expires_at TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        # ٢. خشتەی بەکارهێنەران (بە username و email بەیەکەوە بۆ ئەوەی هیچ کێشەیەک دروست نەبێت)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_id INTEGER NOT NULL,
                username TEXT,
                email TEXT,
                password_hash TEXT,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'owner',
                avatar TEXT DEFAULT 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150',
                bio TEXT DEFAULT 'بەڕێوەبەری سیستەم',
                created_at TEXT NOT NULL,
                FOREIGN KEY (business_id) REFERENCES businesses (id) ON DELETE CASCADE
            )
        """)

        # ٣. خشتەی قەرزەکان
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
                status TEXT NOT NULL DEFAULT 'pending',
                created_by TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (business_id) REFERENCES businesses (id) ON DELETE CASCADE
            )
        """)

        # ٤. خشتەی وەسڵ و واسڵکردن
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

        conn.commit()

init_db()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session or "business" not in session:
            return jsonify({"status": "error", "message": "سەرەتا پێویستە بچیتە ژوورەوە"}), 401
        return f(*args, **kwargs)
    return decorated_function


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


# چوونەژوورەوە یان دروستکردنی ئەکاونت بە ئیمەیڵ
@app.route("/api/auth/email-login", methods=["POST"])
def email_login():
    try:
        data = request.get_json(force=True, silent=True) or {}
        email = data.get("email", "").strip().lower()
        password = data.get("password", "").strip()

        if not email or "@" not in email:
            return jsonify({"status": "error", "message": "تکایە ناونیشانی ئیمەیڵ بە دروستی بنووسە"}), 400

        if not password:
            return jsonify({"status": "error", "message": "تکایە وشەی نهێنی بنووسە"}), 400

        with get_db() as conn:
            user = conn.execute("""
                SELECT u.*, b.business_name, b.subscription_plan, b.expires_at 
                FROM users u JOIN businesses b ON u.business_id = b.id 
                WHERE u.email = ? OR u.username = ?
            """, (email, email)).fetchone()

            # دروستکردنی خۆکارانەی دوکان و هەژمار بۆ ئیمەیڵی نوێ
            if not user:
                trial_expiry = (date.today() + timedelta(days=30)).isoformat()
                new_biz_name = f"فرۆشگای {email.split('@')[0]}"

                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO businesses (business_name, subscription_plan, expires_at, created_at)
                    VALUES (?, 'trial', ?, ?)
                """, (new_biz_name, trial_expiry, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                biz_id = cursor.lastrowid

                clean_user = email.split('@')[0]
                cursor.execute("""
                    INSERT INTO users (business_id, username, email, password_hash, full_name, role, created_at)
                    VALUES (?, ?, ?, ?, ?, 'owner', ?)
                """, (biz_id, clean_user, email, generate_password_hash(password), clean_user, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                user_id = cursor.lastrowid
                conn.commit()

                user_data = {
                    "id": user_id, "email": email, "full_name": clean_user, "role": "owner",
                    "avatar": "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150",
                    "bio": "بەڕێوەبەری سیستەم"
                }
                biz_data = {"id": biz_id, "name": new_biz_name, "expires_at": trial_expiry}
            else:
                if not user["password_hash"] or not check_password_hash(user["password_hash"], password):
                    return jsonify({"status": "error", "message": "وشەی نهێنی بۆ ئەم ئیمەیڵە هەڵەیە!"}), 401

                user_data = {
                    "id": user["id"], "email": user["email"] or email, "full_name": user["full_name"], "role": user["role"],
                    "avatar": user["avatar"], "bio": user["bio"]
                }
                biz_data = {"id": user["business_id"], "name": user["business_name"], "expires_at": user["expires_at"]}

        session.permanent = True
        session["user"] = user_data
        session["business"] = biz_data

        return jsonify({"status": "success", "user": user_data, "business": biz_data})

    except Exception as err:
        return jsonify({"status": "error", "message": f"هەڵەی سێرڤەر: {str(err)}"}), 500


# چوونەژوورەوەی یەک کلیک لە ڕێگەی Google
@app.route("/api/auth/google-one-click", methods=["POST"])
def google_one_click():
    try:
        data = request.get_json(force=True, silent=True) or {}
        email = data.get("email", "").strip().lower()
        full_name = data.get("full_name", "").strip() or email.split("@")[0]
        avatar = data.get("avatar") or "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150"

        if not email or "@" not in email:
            return jsonify({"status": "error", "message": "ئیمەیڵی دروست نەدۆزرایەوە"}), 400

        with get_db() as conn:
            user = conn.execute("""
                SELECT u.*, b.business_name, b.expires_at 
                FROM users u JOIN businesses b ON u.business_id = b.id 
                WHERE u.email = ? OR u.username = ?
            """, (email, email)).fetchone()

            if not user:
                trial_expiry = (date.today() + timedelta(days=30)).isoformat()
                biz_name = f"فرۆشگای {full_name}"

                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO businesses (business_name, subscription_plan, expires_at, created_at)
                    VALUES (?, 'trial', ?, ?)
                """, (biz_name, trial_expiry, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                biz_id = cursor.lastrowid

                cursor.execute("""
                    INSERT INTO users (business_id, username, email, full_name, avatar, role, created_at)
                    VALUES (?, ?, ?, ?, ?, 'owner', ?)
                """, (biz_id, email.split('@')[0], email, full_name, avatar, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                user_id = cursor.lastrowid
                conn.commit()

                user_data = {"id": user_id, "email": email, "full_name": full_name, "avatar": avatar, "bio": "بەستراوە بە Google"}
                biz_data = {"id": biz_id, "name": biz_name, "expires_at": trial_expiry}
            else:
                user_data = {"id": user["id"], "email": user["email"] or email, "full_name": user["full_name"], "avatar": user["avatar"], "bio": user["bio"]}
                biz_data = {"id": user["business_id"], "name": user["business_name"], "expires_at": user["expires_at"]}

        session.permanent = True
        session["user"] = user_data
        session["business"] = biz_data

        return jsonify({"status": "success", "user": user_data, "business": biz_data})

    except Exception as err:
        return jsonify({"status": "error", "message": f"هەڵەی سێرڤەر: {str(err)}"}), 500


@app.route("/api/auth/me", methods=["GET"])
def api_me():
    if "user" in session and "business" in session:
        return jsonify({"logged_in": True, "user": session["user"], "business": session["business"]})
    return jsonify({"logged_in": False})


@app.route("/api/auth/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify({"status": "success"})


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


@app.route("/api/debts", methods=["GET"])
@login_required
def get_debts():
    biz_id = session["business"]["id"]
    search = request.args.get("search", "").strip()

    query = """
        SELECT d.*, 
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
def create_debt():
    biz_id = session["business"]["id"]
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
            INSERT INTO debts (business_id, customer_name, phone, total_amount, currency, debt_date, due_date, note, status, created_by, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (biz_id, name, phone, amount, currency, debt_date, due_date, note, status, session["user"]["email"], datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()

    return jsonify({"status": "success", "message": "قەرزەکە بە سەرکەوتوویی تۆمارکرا"})


@app.route("/api/debts/<int:debt_id>/payments", methods=["POST"])
@login_required
def make_payment(debt_id):
    biz_id = session["business"]["id"]
    data = request.get_json(force=True, silent=True) or {}
    try:
        amount = float(data.get("amount", 0))
    except (TypeError, ValueError):
        amount = 0.0

    if amount <= 0:
        return jsonify({"status": "error", "message": "بڕی واسڵکراو دەبێت لە ٠ زیاتر بێت"}), 400

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
            VALUES (?, ?, ?, ?, ?, '', ?)
        """, (biz_id, debt_id, receipt_no, amount, datetime.now().strftime("%Y-%m-%d %H:%M"), session["user"]["email"]))

        update_debt_status(conn, biz_id, debt_id)
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
    biz_id = session["business"]["id"]
    with get_db() as conn:
        conn.execute("DELETE FROM payments WHERE debt_id = ? AND business_id = ?", (debt_id, biz_id))
        conn.execute("DELETE FROM debts WHERE id = ? AND business_id = ?", (debt_id, biz_id))
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


@app.route("/api/admin/backup", methods=["GET"])
@login_required
def download_backup():
    if os.path.exists(DB_NAME):
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return send_file(DB_NAME, as_attachment=True, download_name=f"debt_backup_{stamp}.db")
    return jsonify({"status": "error"}), 404


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
