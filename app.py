"""
Danyal POS & Store Management System
Tailored for Mobile & Electronics Shops
Features: POS, Stock Control, Debts, Barcode Scanner, Multi-language API, Expenses & Backup
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
app.secret_key = os.environ.get("SECRET_KEY", "danyal_pos_secure_vault_2026")
app.permanent_session_lifetime = timedelta(days=30)

DB_NAME = "danyal_pos.db"
UPLOAD_FOLDER = os.path.join("static", "avatars")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def init_db():
    with get_db() as conn:
        cursor = conn.cursor()

        # ١. خشتەی بەکارهێنەران (Cashiers & Admins)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'admin', -- 'admin', 'cashier'
                created_at TEXT NOT NULL
            )
        """)

        # ٢. خشتەی کاڵاکان / کۆگا (Products & Stock)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                barcode TEXT UNIQUE,
                name TEXT NOT NULL,
                category TEXT NOT NULL, -- موبایل, کاڤەر, شەحنکەر, سیمکارت, ئەکسسوار
                buy_price REAL NOT NULL DEFAULT 0,
                sell_price REAL NOT NULL,
                stock_qty INTEGER NOT NULL DEFAULT 0,
                min_stock_alert INTEGER NOT NULL DEFAULT 3,
                created_at TEXT NOT NULL
            )
        """)

        # ٣. خشتەی کڕیارەکان (Customers)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT UNIQUE,
                total_debt REAL NOT NULL DEFAULT 0,
                total_purchases REAL NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            )
        """)

        # ٤. خشتەی فرۆشتن و پسوڵەکان (Sales & Invoices)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_no TEXT UNIQUE NOT NULL,
                customer_id INTEGER,
                customer_name TEXT NOT NULL DEFAULT 'کڕیاری نەناسراو',
                subtotal REAL NOT NULL,
                discount REAL NOT NULL DEFAULT 0,
                grand_total REAL NOT NULL,
                paid REAL NOT NULL,
                remaining REAL NOT NULL DEFAULT 0,
                payment_method TEXT NOT NULL DEFAULT 'Cash', -- Cash, FIB, FastPay
                cashier_name TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (customer_id) REFERENCES customers (id) ON DELETE SET NULL
            )
        """)

        # ٥. خشتەی بڕگەکانی ناو پسوڵە (Sale Items)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sale_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER NOT NULL,
                product_id INTEGER,
                product_name TEXT NOT NULL,
                buy_price REAL NOT NULL DEFAULT 0,
                sell_price REAL NOT NULL,
                qty INTEGER NOT NULL,
                total REAL NOT NULL,
                FOREIGN KEY (sale_id) REFERENCES sales (id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE SET NULL
            )
        """)

        # ٦. خشتەی قەرزەکان (Debts & Payments)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS debts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                sale_id INTEGER,
                total_amount REAL NOT NULL,
                paid_amount REAL NOT NULL DEFAULT 0,
                remaining_amount REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending', -- pending, partial, paid
                due_date TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (customer_id) REFERENCES customers (id) ON DELETE CASCADE,
                FOREIGN KEY (sale_id) REFERENCES sales (id) ON DELETE SET NULL
            )
        """)

        # ٧. خشتەی مێژووی دانەوەی قەرز (Debt Payments)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS debt_payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                debt_id INTEGER NOT NULL,
                customer_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                payment_method TEXT NOT NULL DEFAULT 'Cash',
                note TEXT,
                received_by TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (debt_id) REFERENCES debts (id) ON DELETE CASCADE,
                FOREIGN KEY (customer_id) REFERENCES customers (id) ON DELETE CASCADE
            )
        """)

        # ٨. خشتەی مەسرەف و خەرجییەکان (Expenses)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL DEFAULT 'گشتی',
                note TEXT,
                created_at TEXT NOT NULL
            )
        """)

        # دروستکردنی ئەدمینی بنەڕەتی ئەگەر نەبێت
        admin = cursor.execute("SELECT * FROM users WHERE username = 'admin'").fetchone()
        if not admin:
            cursor.execute("""
                INSERT INTO users (username, password_hash, full_name, role, created_at)
                VALUES (?, ?, ?, 'admin', ?)
            """, ("admin", generate_password_hash("admin123"), "دانیال بەڕێوەبەر", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        # زیادکردنی چەند نموونەی کاڵا ئەگەر کۆگا بەتاڵ بێت
        prod_count = cursor.execute("SELECT COUNT(*) as c FROM products").fetchone()["c"]
        if prod_count == 0:
            sample_items = [
                ("1001", "iPhone 15 Pro Max 256GB", "موبایل", 1080, 1170, 8, 2),
                ("1002", "Samsung Galaxy S24 Ultra", "موبایل", 950, 1040, 5, 2),
                ("2001", "کەڤەری ماگسەیف ئایفۆن 15", "کاڤەر", 3, 10, 25, 5),
                ("2002", "کەڤەری سیلیکۆن ئەندرۆید", "کاڤەر", 2, 7, 30, 5),
                ("3001", "سەری شەحنکەرەوە 20W ئەسڵی", "شەحنکەر", 8, 18, 15, 4),
                ("3002", "کێبڵی Type-C بۆ Lightning پەت", "شەحنکەر", 2.5, 8, 40, 5),
                ("4001", "سیمکارت کۆڕەک باڵانس دار", "سیمکارت", 3, 5, 50, 10),
                ("4002", "سیمکارت ئاسیاسێڵ 4G", "سیمکارت", 3, 5, 45, 10),
                ("5001", "لەزگەی شووشەیی دژە شکاندن 9H", "ئەکسسوار", 1, 4, 60, 10),
                ("5002", "پاوەربانک Anker 10000mAh", "ئەکسسوار", 15, 28, 12, 3)
            ]
            for bar, nm, cat, bp, sp, st, mn in sample_items:
                cursor.execute("""
                    INSERT INTO products (barcode, name, category, buy_price, sell_price, stock_qty, min_stock_alert, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (bar, nm, cat, bp, sp, st, mn, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        conn.commit()

init_db()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return jsonify({"status": "error", "message": "تکایە سەرەتا بچۆ ژوورەوە"}), 401
        return f(*args, **kwargs)
    return decorated_function


@app.route("/")
def index():
    return render_template("index.html")


# --- Auth API ---
@app.route("/api/auth/login", methods=["POST"])
def api_login():
    data = request.get_json(force=True, silent=True) or {}
    username = data.get("username", "").strip().lower()
    password = data.get("password", "").strip()

    with get_db() as conn:
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if not user or not check_password_hash(user["password_hash"], password):
            return jsonify({"status": "error", "message": "ناوی بەکارهێنەر یان وشەی نهێنی هەڵەیە!"}), 401

        session.permanent = True
        session["user"] = {
            "id": user["id"],
            "username": user["username"],
            "full_name": user["full_name"],
            "role": user["role"]
        }
    return jsonify({"status": "success", "user": session["user"]})


@app.route("/api/auth/me", methods=["GET"])
def api_me():
    if "user" in session:
        return jsonify({"logged_in": True, "user": session["user"]})
    return jsonify({"logged_in": False})


@app.route("/api/auth/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify({"status": "success"})


# --- Dashboard API ---
@app.route("/api/dashboard/stats", methods=["GET"])
@login_required
def dashboard_stats():
    today = date.today().isoformat()
    with get_db() as conn:
        # فرۆشتنی ئەمڕۆ
        today_sales_row = conn.execute("""
            SELECT COALESCE(SUM(grand_total), 0) as total_sales,
                   COALESCE(SUM(paid), 0) as total_collected,
                   COALESCE(SUM(remaining), 0) as total_new_debts,
                   COUNT(id) as invoices_count
            FROM sales WHERE date(created_at) = ?
        """, (today,)).fetchone()

        # قازانجی ئەمڕۆ (Total Selling - Total Buying of sold items)
        today_profit_row = conn.execute("""
            SELECT COALESCE(SUM((si.sell_price - si.buy_price) * si.qty), 0) as gross_profit
            FROM sale_items si JOIN sales s ON si.sale_id = s.id
            WHERE date(s.created_at) = ?
        """, (today,)).fetchone()

        # مەسرەفی ئەمڕۆ
        today_exp = conn.execute("SELECT COALESCE(SUM(amount), 0) as exp FROM expenses WHERE date(created_at) = ?", (today,)).fetchone()["exp"]
        net_profit = today_profit_row["gross_profit"] - today_exp

        # ئامارە گشتییەکان
        total_products = conn.execute("SELECT COUNT(*) as c FROM products").fetchone()["c"]
        total_customers = conn.execute("SELECT COUNT(*) as c FROM customers").fetchone()["c"]
        total_debt = conn.execute("SELECT COALESCE(SUM(remaining_amount), 0) as d FROM debts WHERE status != 'paid'").fetchone()["d"]
        
        # کاڵای کەمبووەوە (Low Stock Items)
        low_stock_items = conn.execute("""
            SELECT id, name, category, stock_qty, min_stock_alert, sell_price 
            FROM products WHERE stock_qty <= min_stock_alert ORDER BY stock_qty ASC LIMIT 10
        """).fetchall()

        # جوڵەی ٧ ڕۆژی ڕابردوو بۆ هێڵکاری
        last_7_days = conn.execute("""
            SELECT date(created_at) as sale_date, COALESCE(SUM(grand_total), 0) as daily_total
            FROM sales 
            WHERE date(created_at) >= date('now', '-6 days')
            GROUP BY sale_date ORDER BY sale_date ASC
        """).fetchall()

    return jsonify({
        "today_sales": today_sales_row["total_sales"],
        "today_collected": today_sales_row["total_collected"],
        "today_profit": max(0.0, net_profit),
        "today_invoices": today_sales_row["invoices_count"],
        "total_products": total_products,
        "total_customers": total_customers,
        "total_debt": total_debt,
        "low_stock_count": len(low_stock_items),
        "low_stock_items": [dict(r) for r in low_stock_items],
        "chart_data": [dict(r) for r in last_7_days]
    })


# --- Products / Stock API ---
@app.route("/api/products", methods=["GET"])
@login_required
def get_products():
    search = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()

    query = "SELECT * FROM products WHERE 1=1"
    params = []
    if search:
        query += " AND (name LIKE ? OR barcode LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    if category and category != "all":
        query += " AND category = ?"
        params.append(category)

    query += " ORDER BY id DESC"
    with get_db() as conn:
        rows = conn.execute(query, params).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/products/scan/<barcode>", methods=["GET"])
@login_required
def scan_barcode(barcode):
    barcode = barcode.strip()
    with get_db() as conn:
        p = conn.execute("SELECT * FROM products WHERE barcode = ?", (barcode,)).fetchone()
    if p:
        return jsonify({"status": "success", "product": dict(p)})
    return jsonify({"status": "error", "message": "کاڵاکە نەدۆزرایەوە"}), 404


@app.route("/api/products", methods=["POST"])
@login_required
def add_product():
    data = request.get_json(force=True, silent=True) or {}
    name = data.get("name", "").strip()
    barcode = data.get("barcode", "").strip() or None
    category = data.get("category", "ئەکسسوار")
    buy_price = float(data.get("buy_price") or 0)
    sell_price = float(data.get("sell_price") or 0)
    stock_qty = int(data.get("stock_qty") or 0)
    min_stock = int(data.get("min_stock_alert") or 3)

    if not name or sell_price <= 0:
        return jsonify({"status": "error", "message": "ناو و نرخی فرۆشتن بە دروستی داواکراوە"}), 400

    with get_db() as conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO products (barcode, name, category, buy_price, sell_price, stock_qty, min_stock_alert, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (barcode, name, category, buy_price, sell_price, stock_qty, min_stock, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            return jsonify({"status": "success", "id": cursor.lastrowid})
        except sqlite3.IntegrityError:
            return jsonify({"status": "error", "message": "ئەم بارکۆدە پێشتر بۆ کاڵایەکی تر تۆمارکراوە!"}), 409


@app.route("/api/products/<int:prod_id>", methods=["DELETE"])
@login_required
def delete_product(prod_id):
    with get_db() as conn:
        conn.execute("DELETE FROM products WHERE id = ?", (prod_id,))
        conn.commit()
    return jsonify({"status": "success"})


# --- POS Checkout Engine ---
@app.route("/api/pos/checkout", methods=["POST"])
@login_required
def pos_checkout():
    data = request.get_json(force=True, silent=True) or {}
    cart = data.get("cart", [])
    if not cart:
        return jsonify({"status": "error", "message": "سەبەتەی کڕین بەتاڵە!"}), 400

    customer_name = data.get("customer_name", "").strip() or "کڕیاری نەناسراو"
    customer_phone = data.get("customer_phone", "").strip()
    discount = float(data.get("discount") or 0)
    paid = float(data.get("paid") or 0)
    payment_method = data.get("payment_method", "Cash") # Cash, FIB, FastPay
    cashier = session["user"]["full_name"]

    with get_db() as conn:
        cursor = conn.cursor()

        # پشکنینی کڕیار یان دروستکردنی ئەگەر ژمارەکەی هەبێت
        customer_id = None
        if customer_phone:
            c_row = conn.execute("SELECT id FROM customers WHERE phone = ?", (customer_phone,)).fetchone()
            if c_row:
                customer_id = c_row["id"]
            else:
                cursor.execute("""
                    INSERT INTO customers (name, phone, created_at) VALUES (?, ?, ?)
                """, (customer_name, customer_phone, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                customer_id = cursor.lastrowid

        subtotal = 0
        sale_items_data = []

        # پشکنین و کەمکردنەوە لە کۆگا (Stock reduction)
        for item in cart:
            p_id = item.get("id")
            qty = int(item.get("qty", 1))
            prod = conn.execute("SELECT * FROM products WHERE id = ?", (p_id,)).fetchone()
            if not prod:
                return jsonify({"status": "error", "message": f"کاڵای #{p_id} نەدۆزرایەوە"}), 400
            
            if prod["stock_qty"] < qty:
                return jsonify({"status": "error", "message": f"بڕی ماوەی ({prod['name']}) تەنها {prod['stock_qty']} دانەیە!"}), 400

            item_total = prod["sell_price"] * qty
            subtotal += item_total
            sale_items_data.append((prod["id"], prod["name"], prod["buy_price"], prod["sell_price"], qty, item_total))

            # کەمکردنەوەی ژمارەی کاڵا
            cursor.execute("UPDATE products SET stock_qty = stock_qty - ? WHERE id = ?", (qty, p_id))

        grand_total = max(0.0, subtotal - discount)
        remaining = max(0.0, grand_total - paid)

        # دروستکردنی ژمارەی پسوڵە
        inv_no = f"INV-{datetime.now().strftime('%y%m%d%H%M')}-{int(datetime.now().timestamp()) % 1000}"

        cursor.execute("""
            INSERT INTO sales (invoice_no, customer_id, customer_name, subtotal, discount, grand_total, paid, remaining, payment_method, cashier_name, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (inv_no, customer_id, customer_name, subtotal, discount, grand_total, paid, remaining, payment_method, cashier, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        sale_id = cursor.lastrowid

        # زیادکردنی کاڵاکانی پسوڵە
        for p_id, p_name, b_price, s_price, qty, it_total in sale_items_data:
            cursor.execute("""
                INSERT INTO sale_items (sale_id, product_id, product_name, buy_price, sell_price, qty, total)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (sale_id, p_id, p_name, b_price, s_price, qty, it_total))

        # ئەگەر قەرز مابێتەوە، تۆمارکردنی لە خشتەی قەرز
        if remaining > 0:
            if not customer_id:
                # کڕیارێکی تایبەت دروست دەکات بۆ قەرزەکە
                cursor.execute("INSERT INTO customers (name, phone, created_at) VALUES (?, ?, ?)",
                               (customer_name, customer_phone or 'بێ ژمارە', datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                customer_id = cursor.lastrowid

            cursor.execute("""
                INSERT INTO debts (customer_id, sale_id, total_amount, paid_amount, remaining_amount, status, created_at)
                VALUES (?, ?, ?, ?, ?, 'pending', ?)
            """, (customer_id, sale_id, grand_total, paid, remaining, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

            cursor.execute("UPDATE customers SET total_debt = total_debt + ? WHERE id = ?", (remaining, customer_id))

        if customer_id:
            cursor.execute("UPDATE customers SET total_purchases = total_purchases + ? WHERE id = ?", (grand_total, customer_id))

        conn.commit()

    return jsonify({
        "status": "success",
        "invoice": {
            "invoice_no": inv_no,
            "customer_name": customer_name,
            "items": cart,
            "subtotal": subtotal,
            "discount": discount,
            "grand_total": grand_total,
            "paid": paid,
            "remaining": remaining,
            "payment_method": payment_method,
            "cashier": cashier,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
    })


# --- Debts & Customers API ---
@app.route("/api/debts", methods=["GET"])
@login_required
def get_debts():
    with get_db() as conn:
        rows = conn.execute("""
            SELECT d.id, d.total_amount, d.paid_amount, d.remaining_amount, d.status, d.created_at,
                   c.name as customer_name, c.phone as customer_phone, s.invoice_no
            FROM debts d
            JOIN customers c ON d.customer_id = c.id
            LEFT JOIN sales s ON d.sale_id = s.id
            WHERE d.status != 'paid'
            ORDER BY d.id DESC
        """).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/debts/<int:debt_id>/pay", methods=["POST"])
@login_required
def pay_debt(debt_id):
    data = request.get_json(force=True, silent=True) or {}
    amount = float(data.get("amount") or 0)
    method = data.get("payment_method", "Cash")
    note = data.get("note", "").strip()

    if amount <= 0:
        return jsonify({"status": "error", "message": "بڕی پارە نادروستە"}), 400

    with get_db() as conn:
        debt = conn.execute("SELECT * FROM debts WHERE id = ?", (debt_id,)).fetchone()
        if not debt:
            return jsonify({"status": "error", "message": "قەرزەکە نەدۆزرایەوە"}), 404

        if amount > debt["remaining_amount"]:
            return jsonify({"status": "error", "message": f"بڕی پارە لە قەرزەکە زیاترە! ماوە: {debt['remaining_amount']}"}), 400

        cursor = conn.cursor()
        new_paid = debt["paid_amount"] + amount
        new_rem = debt["remaining_amount"] - amount
        new_status = "paid" if new_rem == 0 else "partial"

        cursor.execute("""
            UPDATE debts SET paid_amount = ?, remaining_amount = ?, status = ? WHERE id = ?
        """, (new_paid, new_rem, new_status, debt_id))

        cursor.execute("UPDATE customers SET total_debt = total_debt - ? WHERE id = ?", (amount, debt["customer_id"]))

        cursor.execute("""
            INSERT INTO debt_payments (debt_id, customer_id, amount, payment_method, note, received_by, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (debt_id, debt["customer_id"], amount, method, note, session["user"]["full_name"], datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        conn.commit()

    return jsonify({"status": "success", "remaining": new_rem})


@app.route("/api/customers", methods=["GET"])
@login_required
def get_customers():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM customers ORDER BY total_debt DESC").fetchall()
    return jsonify([dict(r) for r in rows])


# --- Expenses API ---
@app.route("/api/expenses", methods=["GET", "POST"])
@login_required
def handle_expenses():
    if request.method == "POST":
        data = request.get_json(force=True, silent=True) or {}
        title = data.get("title", "").strip()
        amount = float(data.get("amount") or 0)
        category = data.get("category", "گشتی")
        note = data.get("note", "").strip()

        if not title or amount <= 0:
            return jsonify({"status": "error", "message": "زانیارییەکان تەواو نین"}), 400

        with get_db() as conn:
            conn.execute("""
                INSERT INTO expenses (title, amount, category, note, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (title, amount, category, note, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
        return jsonify({"status": "success"})

    with get_db() as conn:
        rows = conn.execute("SELECT * FROM expenses ORDER BY id DESC LIMIT 50").fetchall()
    return jsonify([dict(r) for r in rows])


# --- Backup API ---
@app.route("/api/backup", methods=["GET"])
@login_required
def download_backup():
    if os.path.exists(DB_NAME):
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return send_file(DB_NAME, as_attachment=True, download_name=f"danyal_pos_backup_{stamp}.db")
    return jsonify({"status": "error"}), 404


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
