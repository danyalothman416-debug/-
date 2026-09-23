"""
Danyal Mobile POS & Inventory OS
Tailored for Phone & Accessories Shops
Features: Category-Specific Stock, Mobile POS, Barcode, Multi-currency, Debts & Backups
Author: Danyal App Architecture
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
app.secret_key = os.environ.get("SECRET_KEY", "danyal_luxury_mobile_pos_2026")
app.permanent_session_lifetime = timedelta(days=30)

DB_NAME = "danyal_mobile_store.db"


def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def init_db():
    with get_db() as conn:
        cursor = conn.cursor()

        # ١. خشتەی بەکارهێنەران
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                shop_name TEXT NOT NULL DEFAULT 'دانیال مۆبایل',
                role TEXT NOT NULL DEFAULT 'admin',
                created_at TEXT NOT NULL
            )
        """)

        # ٢. خشتەی کاڵاکان بە تایبەتمەندی جیاواز بۆ هەر بەشێک
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                barcode TEXT UNIQUE,
                name TEXT NOT NULL,
                category TEXT NOT NULL, -- موبایل, سیمکارت, کاڤەر, شەحنکەر, ئەکسسوار
                buy_price REAL NOT NULL DEFAULT 0,
                sell_price REAL NOT NULL,
                stock_qty INTEGER NOT NULL DEFAULT 0,
                min_stock_alert INTEGER NOT NULL DEFAULT 2,
                specs TEXT, -- داتای ورد: بیرگە، ڕەنگ، کۆمپانیای سیمکارت، وات، هتد بە JSON
                created_at TEXT NOT NULL
            )
        """)

        # ٣. خشتەی کڕیارەکان
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

        # ٤. خشتەی پسوڵە و فرۆشتنەکان
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

        # ٥. بڕگەکانی ناو پسوڵە
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

        # ٦. خشتەی قەرزەکان
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS debts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                sale_id INTEGER,
                total_amount REAL NOT NULL,
                paid_amount REAL NOT NULL DEFAULT 0,
                remaining_amount REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL,
                FOREIGN KEY (customer_id) REFERENCES customers (id) ON DELETE CASCADE,
                FOREIGN KEY (sale_id) REFERENCES sales (id) ON DELETE SET NULL
            )
        """)

        # ٧. خشتەی دانەوەی قەرز
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS debt_payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                debt_id INTEGER NOT NULL,
                customer_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                payment_method TEXT NOT NULL DEFAULT 'Cash',
                received_by TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (debt_id) REFERENCES debts (id) ON DELETE CASCADE,
                FOREIGN KEY (customer_id) REFERENCES customers (id) ON DELETE CASCADE
            )
        """)

        # دروستکردنی ئەدمین
        admin = cursor.execute("SELECT * FROM users WHERE username = 'admin'").fetchone()
        if not admin:
            cursor.execute("""
                INSERT INTO users (username, password_hash, full_name, shop_name, role, created_at)
                VALUES (?, ?, ?, ?, 'admin', ?)
            """, ("admin", generate_password_hash("admin123"), "دانیال", "دانیال مۆبایل", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        # زیادکردنی کاڵای نموونەیی گەنجانە ئەگەر داتابەیس نوێ بێت
        if cursor.execute("SELECT COUNT(*) as c FROM products").fetchone()["c"] == 0:
            samples = [
                ("101", "iPhone 15 Pro Max", "موبایل", 1090, 1180, 5, 2, json.dumps({"storage": "256GB", "color": "Natural Titanium"})),
                ("102", "Samsung S24 Ultra", "موبایل", 960, 1050, 4, 2, json.dumps({"storage": "512GB", "color": "Titanium Black"})),
                ("201", "سیمکارت ئاسیاسێڵ زێڕین", "سیمکارت", 5, 12, 20, 5, json.dumps({"operator": "ئاسیاسێڵ", "phone_no": "0770 123 4567"})),
                ("202", "سیمکارت کۆڕەک 4G بێ سنوور", "سیمکارت", 4, 8, 30, 5, json.dumps({"operator": "کۆڕەک", "phone_no": "0750 987 6543"})),
                ("301", "سەری شەحن Apple 20W ئەسڵی", "شەحنکەر", 9, 18, 25, 4, json.dumps({"watt": "20W", "type": "Type-C"})),
                ("401", "کەڤەری ماگسەیف ڕوون بۆ ئایفۆن", "کاڤەر", 3, 10, 40, 5, json.dumps({"model": "iPhone 15 Series"})),
                ("501", "AirPods Pro 2 گەرەنتی", "ئەکسسوار", 140, 175, 6, 2, json.dumps({"type": "بێوایەر"}))
            ]
            for bar, nm, cat, bp, sp, st, mn, spc in samples:
                cursor.execute("""
                    INSERT INTO products (barcode, name, category, buy_price, sell_price, stock_qty, min_stock_alert, specs, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (bar, nm, cat, bp, sp, st, mn, spc, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

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


@app.route("/api/auth/login", methods=["POST"])
def auth_login():
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
            "shop_name": user["shop_name"]
        }
    return jsonify({"status": "success", "user": session["user"]})


@app.route("/api/auth/me", methods=["GET"])
def auth_me():
    if "user" in session:
        return jsonify({"logged_in": True, "user": session["user"]})
    return jsonify({"logged_in": False})


@app.route("/api/auth/logout", methods=["POST"])
def auth_logout():
    session.clear()
    return jsonify({"status": "success"})


# --- Dashboard Stats ---
@app.route("/api/dashboard/stats", methods=["GET"])
@login_required
def dashboard_stats():
    today = date.today().isoformat()
    with get_db() as conn:
        today_sales = conn.execute("SELECT COALESCE(SUM(grand_total), 0) as s, COALESCE(SUM(paid), 0) as p FROM sales WHERE date(created_at) = ?", (today,)).fetchone()
        
        profit_row = conn.execute("""
            SELECT COALESCE(SUM((si.sell_price - si.buy_price) * si.qty), 0) as profit
            FROM sale_items si JOIN sales s ON si.sale_id = s.id
            WHERE date(s.created_at) = ?
        """, (today,)).fetchone()

        total_debt = conn.execute("SELECT COALESCE(SUM(remaining_amount), 0) as d FROM debts WHERE status != 'paid'").fetchone()["d"]
        total_products = conn.execute("SELECT COUNT(*) as c FROM products").fetchone()["c"]
        low_stock = conn.execute("SELECT * FROM products WHERE stock_qty <= min_stock_alert ORDER BY stock_qty ASC").fetchall()

    return jsonify({
        "today_sales": today_sales["s"],
        "today_profit": profit_row["profit"],
        "total_debt": total_debt,
        "total_products": total_products,
        "low_stock_count": len(low_stock),
        "low_stock_items": [dict(r) for r in low_stock]
    })


# --- Products / Stock ---
@app.route("/api/products", methods=["GET"])
@login_required
def get_products():
    category = request.args.get("category", "").strip()
    search = request.args.get("search", "").strip()

    query = "SELECT * FROM products WHERE 1=1"
    params = []
    if category and category != "all":
        query += " AND category = ?"
        params.append(category)
    if search:
        query += " AND (name LIKE ? OR barcode LIKE ? OR specs LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

    query += " ORDER BY id DESC"
    with get_db() as conn:
        rows = conn.execute(query, params).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/products", methods=["POST"])
@login_required
def add_product():
    data = request.get_json(force=True, silent=True) or {}
    name = data.get("name", "").strip()
    category = data.get("category", "موبایل")
    buy_price = float(data.get("buy_price") or 0)
    sell_price = float(data.get("sell_price") or 0)
    stock_qty = int(data.get("stock_qty") or 1)
    min_stock = int(data.get("min_stock_alert") or 2)
    barcode = data.get("barcode", "").strip() or None
    specs = json.dumps(data.get("specs") or {})

    if not name or sell_price <= 0:
        return jsonify({"status": "error", "message": "ناو و نرخی فرۆشتن مەرجە"}), 400

    with get_db() as conn:
        try:
            conn.execute("""
                INSERT INTO products (barcode, name, category, buy_price, sell_price, stock_qty, min_stock_alert, specs, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (barcode, name, category, buy_price, sell_price, stock_qty, min_stock, specs, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            return jsonify({"status": "success"})
        except sqlite3.IntegrityError:
            return jsonify({"status": "error", "message": "ئەم بارکۆدە پێشتر تۆمارکراوە!"}), 409


@app.route("/api/products/<int:prod_id>", methods=["DELETE"])
@login_required
def delete_product(prod_id):
    with get_db() as conn:
        conn.execute("DELETE FROM products WHERE id = ?", (prod_id,))
        conn.commit()
    return jsonify({"status": "success"})


# --- POS Checkout ---
@app.route("/api/pos/checkout", methods=["POST"])
@login_required
def pos_checkout():
    data = request.get_json(force=True, silent=True) or {}
    cart = data.get("cart", [])
    if not cart:
        return jsonify({"status": "error", "message": "سەبەتەی کڕین بەتاڵە!"}), 400

    cust_name = data.get("customer_name", "").strip() or "کڕیاری ئاسایی"
    cust_phone = data.get("customer_phone", "").strip()
    discount = float(data.get("discount") or 0)
    paid = float(data.get("paid") or 0)
    method = data.get("payment_method", "Cash")
    cashier = session["user"]["full_name"]

    with get_db() as conn:
        cursor = conn.cursor()

        customer_id = None
        if cust_phone:
            c_row = conn.execute("SELECT id FROM customers WHERE phone = ?", (cust_phone,)).fetchone()
            if c_row:
                customer_id = c_row["id"]
            else:
                cursor.execute("INSERT INTO customers (name, phone, created_at) VALUES (?, ?, ?)",
                               (cust_name, cust_phone, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                customer_id = cursor.lastrowid

        subtotal = 0
        items_data = []

        for item in cart:
            p_id = item["id"]
            qty = int(item["qty"])
            prod = conn.execute("SELECT * FROM products WHERE id = ?", (p_id,)).fetchone()
            if not prod or prod["stock_qty"] < qty:
                return jsonify({"status": "error", "message": f"بڕی ماوەی ({prod['name'] if prod else ''}) لە کۆگا بەش ناکات!"}), 400

            total_item = prod["sell_price"] * qty
            subtotal += total_item
            items_data.append((prod["id"], prod["name"], prod["buy_price"], prod["sell_price"], qty, total_item))
            cursor.execute("UPDATE products SET stock_qty = stock_qty - ? WHERE id = ?", (qty, p_id))

        grand_total = max(0.0, subtotal - discount)
        remaining = max(0.0, grand_total - paid)

        inv_no = f"INV-{datetime.now().strftime('%y%m%d%H%M')}-{int(datetime.now().timestamp()) % 1000}"

        cursor.execute("""
            INSERT INTO sales (invoice_no, customer_id, customer_name, subtotal, discount, grand_total, paid, remaining, payment_method, cashier_name, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (inv_no, customer_id, cust_name, subtotal, discount, grand_total, paid, remaining, method, cashier, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        sale_id = cursor.lastrowid

        for pid, pname, bp, sp, q, t in items_data:
            cursor.execute("""
                INSERT INTO sale_items (sale_id, product_id, product_name, buy_price, sell_price, qty, total)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (sale_id, pid, pname, bp, sp, q, t))

        if remaining > 0:
            if not customer_id:
                cursor.execute("INSERT INTO customers (name, phone, created_at) VALUES (?, ?, ?)",
                               (cust_name, cust_phone or 'بێ ژمارە', datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
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
            "customer_name": cust_name,
            "items": cart,
            "subtotal": subtotal,
            "discount": discount,
            "grand_total": grand_total,
            "paid": paid,
            "remaining": remaining,
            "payment_method": method,
            "cashier": cashier,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
    })


# --- Debts ---
@app.route("/api/debts", methods=["GET"])
@login_required
def get_debts():
    with get_db() as conn:
        rows = conn.execute("""
            SELECT d.*, c.name as customer_name, c.phone as customer_phone, s.invoice_no
            FROM debts d JOIN customers c ON d.customer_id = c.id
            LEFT JOIN sales s ON d.sale_id = s.id
            WHERE d.status != 'paid' ORDER BY d.id DESC
        """).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/debts/<int:debt_id>/pay", methods=["POST"])
@login_required
def pay_debt(debt_id):
    data = request.get_json(force=True, silent=True) or {}
    amount = float(data.get("amount") or 0)
    method = data.get("payment_method", "Cash")

    if amount <= 0:
        return jsonify({"status": "error", "message": "بڕی پارە نادروستە"}), 400

    with get_db() as conn:
        debt = conn.execute("SELECT * FROM debts WHERE id = ?", (debt_id,)).fetchone()
        if not debt or amount > debt["remaining_amount"]:
            return jsonify({"status": "error", "message": "بڕی دراو زیاترە لە قەرزەکە"}), 400

        new_paid = debt["paid_amount"] + amount
        new_rem = debt["remaining_amount"] - amount
        new_status = "paid" if new_rem == 0 else "partial"

        conn.execute("UPDATE debts SET paid_amount = ?, remaining_amount = ?, status = ? WHERE id = ?",
                     (new_paid, new_rem, new_status, debt_id))
        conn.execute("UPDATE customers SET total_debt = total_debt - ? WHERE id = ?", (amount, debt["customer_id"]))
        conn.execute("""
            INSERT INTO debt_payments (debt_id, customer_id, amount, payment_method, received_by, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (debt_id, debt["customer_id"], amount, method, session["user"]["full_name"], datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()

    return jsonify({"status": "success"})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
