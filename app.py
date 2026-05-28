import streamlit as st
import sqlite3
from datetime import datetime

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Muhammad Mobile",
    page_icon="📱",
    layout="wide"
)

# ---------------- DATABASE ----------------
conn = sqlite3.connect("mobile_store.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS products(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
category TEXT,
price REAL
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS orders(
id INTEGER PRIMARY KEY AUTOINCREMENT,
customer TEXT,
product TEXT,
price REAL,
date TEXT
)
""")

conn.commit()

# ---------------- LANGUAGE ----------------
lang = st.sidebar.selectbox(
    "Language / زمان / زمان",
    ["Kurdish","Arabic","English"]
)

txt = {
"Kurdish":{
"title":"دووکانی Muhammad Mobile",
"products":"کاڵاکان",
"admin":"ئەدمین",
"orders":"داواکاریەکان",
"search":"گەڕان",
"cart":"سەبەتە",
"buy":"کڕین"
},

"Arabic":{
"title":"متجر Muhammad Mobile",
"products":"المنتجات",
"admin":"الادمن",
"orders":"الطلبات",
"search":"بحث",
"cart":"السلة",
"buy":"شراء"
},

"English":{
"title":"Muhammad Mobile Store",
"products":"Products",
"admin":"Admin",
"orders":"Orders",
"search":"Search",
"cart":"Cart",
"buy":"Buy"
}
}

t = txt[lang]

# ---------------- DEFAULT PRODUCTS ----------------
default_products = [
("iPhone Cover","Cover",10),
("Mobile Shield","Protection",5),
("PUBG UC","Gaming",20),
("iTunes Card","Digital",25),
("FastPay","Finance",50),
("FIB Service","Finance",30),
("Asiacell Card","Cards",10),
("Korek Card","Cards",10),
("Zain Card","Cards",10)
]

if c.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
    c.executemany(
        "INSERT INTO products(name,category,price) VALUES(?,?,?)",
        default_products
    )
    conn.commit()

# ---------------- HEADER ----------------
st.title(t["title"])
st.caption("Developed by Danyal")

menu = st.sidebar.radio(
    "Menu",
    [t["products"], t["orders"], t["admin"]]
)

# ---------------- PRODUCTS ----------------
if menu == t["products"]:

    search = st.text_input(t["search"])

    query = """
    SELECT * FROM products
    WHERE name LIKE ?
    """

    rows = c.execute(
        query,
        (f"%{search}%",)
    ).fetchall()

    col1, col2 = st.columns(2)

    if "cart" not in st.session_state:
        st.session_state.cart = []

    for i,row in enumerate(rows):

        with (col1 if i % 2 == 0 else col2):

            st.subheader(row[1])
            st.write("Category:", row[2])
            st.write("Price:", row[3], "$")

            if st.button(
                f"{t['buy']} {row[0]}",
                key=row[0]
            ):
                st.session_state.cart.append(row)

    st.divider()
    st.subheader(t["cart"])

    total = 0

    for item in st.session_state.cart:
        st.write(item[1], "-", item[3], "$")
        total += item[3]

    st.write("Total:", total)

# ---------------- ORDERS ----------------
elif menu == t["orders"]:

    customer = st.text_input("Customer Name")

    if st.button("Create Order"):

        for item in st.session_state.cart:

            c.execute("""
            INSERT INTO orders(
            customer,
            product,
            price,
            date
            )
            VALUES(?,?,?,?)
            """,
            (
            customer,
            item[1],
            item[3],
            datetime.now().strftime(
            "%Y-%m-%d %H:%M"
            )
            ))

        conn.commit()

        st.success("Saved")

        st.session_state.cart = []

    rows = c.execute(
    "SELECT * FROM orders ORDER BY id DESC"
    ).fetchall()

    for row in rows:
        st.write(
        row[1],
        "|",
        row[2],
        "|",
        row[3],
        "$"
        )

# ---------------- ADMIN ----------------
elif menu == t["admin"]:

    st.subheader("Admin Panel")

    name = st.text_input("Product")

    category = st.selectbox(
    "Category",
    [
    "Cover",
    "Protection",
    "Gaming",
    "Digital",
    "Finance",
    "Cards"
    ])

    price = st.number_input(
    "Price",
    0.0
    )

    if st.button("Add Product"):

        c.execute("""
        INSERT INTO products(
        name,
        category,
        price
        )
        VALUES(?,?,?)
        """,
        (
        name,
        category,
        price
        ))

        conn.commit()

        st.success("Added")
