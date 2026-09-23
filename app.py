"""
Danyal Mobile POS & Luxury Store OS
Engineered for Mobile Store Management with Product Images
Author: Danyal App Architecture
"""

import os
import sqlite3
import json
from datetime import datetime, date, timedelta
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "danyal_luxury_pos_ultra_vault_2026")
app.permanent_session_lifetime = timedelta(days=30)

DB_NAME = "danyal_luxury_store.db"

# بوخچەی پاشەکەوتکردنی وێنەی کاڵاکان
UPLOAD_FOLDER = os.path.join("static", "uploads", "products")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def init_db():
    with get_db() as conn:
        cursor = conn.cursor()

        # خشتەی بەکارهێنەران
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                shop_name TEXT NOT NULL DEFAULT 'دانیال مۆبایل',
                created_at TEXT NOT NULL
            )
        """)

        # خشتەی کاڵاکان (لەگەڵ وێنەی image_url)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                barcode TEXT UNIQUE,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                buy_price REAL NOT NULL DEFAULT 0,
                sell_price REAL NOT NULL,
                stock_qty INTEGER NOT NULL DEFAULT 0,
                min_stock_alert INTEGER NOT NULL DEFAULT 2,
                image_url TEXT,
                specs TEXT,
                created_at TEXT NOT NULL
            )
        """)

        # خشتەی کڕیاران
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

        # خشتەی فرۆشتن و پسوڵە
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_no TEXT UNIQUE NOT NULL,
                customer_id INTEGER,
                customer_name TEXT NOT NULL DEFAULT 'کڕیاری ئاسایی',
                subtotal REAL NOT NULL,
                discount REAL NOT NULL DEFAULT 0,
                grand_total REAL NOT NULL,
                paid REAL NOT NULL,
                remaining REAL NOT NULL DEFAULT 0,
                payment_method TEXT NOT NULL DEFAULT 'Cash',
                cashier_name TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (customer_id) REFERENCES customers (id) ON DELETE SET NULL
            )
        """)

        # خشتەی بڕگەکانی ناو پسوڵە
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

        # خشتەی قەرزەکان
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

        # خشتەی دانەوەی قەرز
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

        # دروستکردنی ئەکاونتی سەرەکی ئەگەر نەبێت
        admin = cursor.execute("SELECT * FROM users WHERE username = 'admin'").fetchone()
        if not admin:
            cursor.execute("""
                INSERT INTO users (username, password_hash, full_name, shop_name, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, ("admin", generate_password_hash("admin123"), "دانیال بەڕێوەبەر", "دانیال مۆبایل", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        # کاڵای دەستپێکی لوکس ئەگەر داتابەیس نوێ بێت
        if cursor.execute("SELECT COUNT(*) as c FROM products").fetchone()["c"] == 0:
            sample_items = [
                ("101", "iPhone 15 Pro Max", "موبایل", 1090, 1180, 6, 2, "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=500", json.dumps({"storage": "256GB", "color": "تایتانیۆم"})),
                ("102", "Samsung Galaxy S24 Ultra", "موبایل", 970, 1050, 4, 2, "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=500", json.dumps({"storage": "512GB", "color": "ڕەشی مات"})),
                ("201", "سیمکارت ئاسیاسێڵ 4G زێڕین", "سیمکارت", 5, 15, 25, 5, "https://images.unsplash.com/photo-1563770660941-20978e870e26?w=500", json.dumps({"operator": "ئاسیاسێڵ", "phone_no": "0770 123 4567"})),
                ("301", "سەری شەحن Apple 20W ئەسڵی", "شەحنکەر", 9, 18, 30, 4, "https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=500", json.dumps({"watt": "20W Type-C"})),
                ("401", "کەڤەری ماگسەیفی ئەسڵی", "کاڤەر", 3, 12, 45, 5, "https://images.unsplash.com/photo-1601784551446-20c9e07cdbdb?w=500", json.dumps({"model": "iPhone 15 Series"})),
                ("501", "AirPods Pro 2 (USB-C)", "ئەکسسوار", 145, 179, 8, 2, "https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=500", json.dumps({"type": "بێوایەر ئەسڵی"}))
            ]
            for bar, nm, cat, bp, sp, st, mn, img, spc in sample_items:
                cursor.execute("""
                    INSERT INTO products (barcode, name, category, buy_price, sell_price, stock_qty, min_stock_alert, image_url, specs, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (bar, nm, cat, bp, sp, st, mn, img, spc, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

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


@app.route("/static/uploads/products/<filename>")
def serve_product_image(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# --- Auth API ---
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

    return jsonify({
        "today_sales": today_sales["s"],
        "today_profit": profit_row["profit"],
        "total_debt": total_debt,
        "total_products": total_products
    })


# --- Products / Stock API ---
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


# زیادکردنی کاڵا بە وێنەوە (Multipart Form-Data)
@app.route("/api/products", methods=["POST"])
@login_required
def add_product():
    name = request.form.get("name", "").strip()
    category = request.form.get("category", "موبایل")
    buy_price = float(request.form.get("buy_price") or 0)
    sell_price = float(request.form.get("sell_price") or 0)
    stock_qty = int(request.form.get("stock_qty") or 1)
    min_stock = int(request.form.get("min_stock_alert") or 2)
    barcode = request.form.get("barcode", "").strip() or None
    specs = request.form.get("specs", "{}")

    if not name or sell_price <= 0:
        return jsonify({"status": "error", "message": "ناو و نرخی فرۆشتن بە دروستی داواکراون"}), 400

    # وەرگرتنی وێنە لە کڕیار / کامێرا
    image_url = None
    if "image" in request.files:
        file = request.files["image"]
        if file and file.filename != "" and allowed_file(file.filename):
            ext = file.filename.rsplit(".", 1)[1].lower()
            fname = f"item_{int(datetime.now().timestamp())}_{secure_filename(file.filename)}"
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], fname)
            file.save(file_path)
            image_url = f"/static/uploads/products/{fname}"

    # ئەگەر وێنەی دانەنا، وێنەیەکی کوالێتی بەرزی ئۆتۆماتیکی دابنێ بەپێی بەشەکە
    if not image_url:
        default_images = {
            "موبایل": "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=500",
            "سیمکارت": "https://images.unsplash.com/photo-1563770660941-20978e870e26?w=500",
            "شەحنکەر": "https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=500",
            "کاڤەر": "https://images.unsplash.com/photo-1601784551446-20c9e07cdbdb?w=500",
            "ئەکسسوار": "https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=500"
        }
        image_url = default_images.get(category, default_images["موبایل"])

    with get_db() as conn:
        try:
            conn.execute("""
                INSERT INTO products (barcode, name, category, buy_price, sell_price, stock_qty, min_stock_alert, image_url, specs, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (barcode, name, category, buy_price, sell_price, stock_qty, min_stock, image_url, specs, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
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


# --- POS Checkout Engine ---
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
        return jsonify({"status": "error", "message": "بڕی پارە هەڵەیە"}), 400

    with get_db() as conn:
        debt = conn.execute("SELECT * FROM debts WHERE id = ?", (debt_id,)).fetchone()
        if not debt or amount > debt["remaining_amount"]:
            return jsonify({"status": "error", "message": "بڕی پارە لە قەرزەکە زیاترە!"}), 400

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
