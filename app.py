from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
DB_NAME = "debts.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# دروستکردنی خشتەکانی بنکەدراوە لە یەکەم داگیرساندندا
def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                address TEXT,
                created_at TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                type TEXT NOT NULL, -- 'debt' (قەرز) یان 'payment' (دانەوە)
                amount REAL NOT NULL,
                note TEXT,
                date TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers (id)
            )
        """)
        conn.commit()

init_db()

@app.route("/")
def index():
    conn = get_db()
    
    # هێنانی لیستی کڕیارەکان و باڵانسی ماوەیان
    query = """
        SELECT 
            c.id, c.name, c.phone, c.address,
            COALESCE(SUM(CASE WHEN t.type = 'debt' THEN t.amount ELSE 0 END), 0) as total_debt,
            COALESCE(SUM(CASE WHEN t.type = 'payment' THEN t.amount ELSE 0 END), 0) as total_paid
        FROM customers c
        LEFT JOIN transactions t ON c.id = t.customer_id
        GROUP BY c.id
        ORDER BY c.id DESC
    """
    customers_raw = conn.execute(query).fetchall()
    
    customers = []
    total_market_debt = 0.0
    total_market_paid = 0.0

    for c in customers_raw:
        balance = c["total_debt"] - c["total_paid"]
        total_market_debt += balance
        total_market_paid += c["total_paid"]
        customers.append({
            "id": c["id"],
            "name": c["name"],
            "phone": c["phone"] or "نییە",
            "address": c["address"] or "نییە",
            "balance": balance,
            "total_debt": c["total_debt"],
            "total_paid": c["total_paid"]
        })

    conn.close()
    return render_template("index.html", 
                           customers=customers, 
                           total_debt=total_market_debt, 
                           total_paid=total_market_paid,
                           total_customers=len(customers))

# زیادکردنی کڕیاری نوێ
@app.route("/api/customer/add", methods=["POST"])
def add_customer():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    phone = data.get("phone", "").strip()
    address = data.get("address", "").strip()

    if not name:
        return jsonify({"status": "error", "message": "ناوی کڕیار مەرجە بنووسرێت"}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO customers (name, phone, address, created_at)
        VALUES (?, ?, ?, ?)
    """, (name, phone, address, datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    conn.close()

    return jsonify({"status": "success", "message": "کڕیار بە سەرکەوتوویی زیادکرا"}), 201

# زیادکردنی مامەڵەی نوێ (قەرز یان دانەوە)
@app.route("/api/transaction/add", methods=["POST"])
def add_transaction():
    data = request.get_json() or {}
    customer_id = data.get("customer_id")
    tx_type = data.get("type") # 'debt' or 'payment'
    amount = data.get("amount")
    note = data.get("note", "").strip()

    if not customer_id or tx_type not in ['debt', 'payment']:
        return jsonify({"status": "error", "message": "زانیارییەکان تەواو نین"}), 400

    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError()
    except (TypeError, ValueError):
        return jsonify({"status": "error", "message": "بڕی پارە دەبێت ژمارەیەکی دروست بێت"}), 400

    conn = get_db()
    conn.execute("""
        INSERT INTO transactions (customer_id, type, amount, note, date)
        VALUES (?, ?, ?, ?, ?)
    """, (customer_id, tx_type, amount, note, datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    conn.close()

    return jsonify({"status": "success", "message": "مامەڵەکە تۆمارکرا"}), 200

# هێنانی مێژووی مامەڵەکانی کڕیارێک
@app.route("/api/customer/<int:customer_id>/statement")
def get_statement(customer_id):
    conn = get_db()
    customer = conn.execute("SELECT * FROM customers WHERE id = ?", (customer_id,)).fetchone()
    if not customer:
        conn.close()
        return jsonify({"status": "error", "message": "کڕیار نەدۆزرایەوە"}), 404

    txs = conn.execute("""
        SELECT * FROM transactions WHERE customer_id = ? ORDER BY id DESC
    """, (customer_id,)).fetchall()
    conn.close()

    history = [{
        "id": t["id"],
        "type": t["type"],
        "amount": t["amount"],
        "note": t["note"] or "بێ تێبینی",
        "date": t["date"]
    } for t in txs]

    return jsonify({
        "status": "success",
        "customer": dict(customer),
        "history": history
    })

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
