import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import base64
import numpy as np
import warnings
import os
warnings.filterwarnings('ignore')

# Page config
st.set_page_config(page_title="سیستەمی دوکانی مۆبایل", page_icon="📱", layout="wide")

# Initialize session state
if 'sales' not in st.session_state:
    st.session_state.sales = pd.DataFrame(columns=['بەرهەم', 'نرخ', 'کاتی فرۆشتن', 'کڕیار'])
if 'inventory' not in st.session_state:
    st.session_state.inventory = pd.DataFrame(columns=['کەلوپەل', 'دانە', 'نرخی کڕین'])
if 'warranty' not in st.session_state:
    st.session_state.warranty = pd.DataFrame(columns=['کڕیار', 'IMEI', 'کۆتایی گەرەنتی', 'مۆبایل'])
if 'customers' not in st.session_state:
    st.session_state.customers = pd.DataFrame(columns=['ناو', 'مۆبایل', 'ئیمەیڵ', 'ناونیشان'])
if 'expenses' not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=['بەروار', 'جۆر', 'بڕ'])
if 'tasks' not in st.session_state:
    st.session_state.tasks = pd.DataFrame(columns=['ناونیشان', 'وادە', 'ڕەوش'])
if 'reviews' not in st.session_state:
    st.session_state.reviews = pd.DataFrame(columns=['کڕیار', 'بەرهەم', 'ئەستێرە', 'سەرنج'])

# Helper functions
def add_sale(product, price, customer):
    new = pd.DataFrame({'بەرهەم': [product], 'نرخ': [price], 'کاتی فرۆشتن': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")], 'کڕیار': [customer]})
    st.session_state.sales = pd.concat([st.session_state.sales, new], ignore_index=True)
    return True

def add_inventory(item, stock, price):
    new = pd.DataFrame({'کەلوپەل': [item], 'دانە': [stock], 'نرخی کڕین': [price]})
    st.session_state.inventory = pd.concat([st.session_state.inventory, new], ignore_index=True)
    return True

def add_expense(date, expense_type, amount):
    new = pd.DataFrame({'بەروار': [date], 'جۆر': [expense_type], 'بڕ': [amount]})
    st.session_state.expenses = pd.concat([st.session_state.expenses, new], ignore_index=True)
    return True

def check_low_stock():
    if not st.session_state.inventory.empty:
        return st.session_state.inventory[st.session_state.inventory['دانە'] < 5]
    return pd.DataFrame()

def check_birthdays():
    today = datetime.now()
    birthdays = []
    if not st.session_state.customers.empty and 'ڕێکەوتی لەدایکبوون' in st.session_state.customers.columns:
        for _, c in st.session_state.customers.iterrows():
            if pd.notna(c.get('ڕێکەوتی لەدایکبوون')):
                try:
                    bd = pd.to_datetime(c['ڕێکەوتی لەدایکبوون'])
                    if bd.month == today.month and bd.day == today.day:
                        birthdays.append(c['ناو'])
                except:
                    pass
    return birthdays

# Sidebar
with st.sidebar:
    st.title("📱 مینو")
    
    # Alerts
    st.markdown("### 🔔 ئاگاداری")
    low = check_low_stock()
    if not low.empty:
        for _, i in low.iterrows():
            st.error(f"📦 {i['کەلوپەل']}: {i['دانە']} دانە")
    
    bdays = check_birthdays()
    if bdays:
        for b in bdays:
            st.success(f"🎂 {b}")
    
    st.markdown("---")
    
    # Menu
    menu = st.selectbox("بەش", [
        "💰 فرۆشتن", "📦 کۆگا", "🛡️ گەرەنتی", "📊 قازانج",
        "👥 کڕیاران", "💸 خەرجی", "⭐ هەڵسەنگاندن", "📅 کارەکان",
        "🎯 داشبۆرد"
    ])
    
    st.markdown("---")
    st.markdown("### 📊 کورتە")
    ts = st.session_state.sales['نرخ'].sum() if not st.session_state.sales.empty else 0
    tc = (st.session_state.inventory['نرخی کڕین'] * st.session_state.inventory['دانە']).sum() if not st.session_state.inventory.empty else 0
    te = st.session_state.expenses['بڕ'].sum() if not st.session_state.expenses.empty else 0
    st.metric("💰 فرۆشتن", f"${ts:,.0f}")
    st.metric("👥 کڕیار", len(st.session_state.customers))
    st.metric("💵 قازانج", f"${ts-tc-te:,.0f}")

# Main content
st.title("📱 سیستەمی بەڕێوەبردنی دوکانی مۆبایل")

if menu == "💰 فرۆشتن":
    st.header("💰 تۆمارکردنی فرۆشتن")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        product = st.text_input("📱 ناوی بەرهەم")
        price = st.number_input("💵 نرخ ($)", min_value=0.0, step=10.0)
        customer = st.text_input("👤 ناوی کڕیار")
        
        if st.button("➕ تۆمارکردنی فرۆشتن", use_container_width=True):
            if product and price > 0 and customer:
                add_sale(product, price, customer)
                st.success(f"✅ فرۆشتنی {product} بە {customer} تۆمار کرا!")
                st.balloons()
            else:
                st.error("هەموو خانەکان پڕ بکە!")
    
    with col2:
        if not st.session_state.sales.empty:
            st.subheader("دوایین فرۆشتنەکان")
            st.dataframe(st.session_state.sales.tail(5))

elif menu == "📦 کۆگا":
    st.header("📦 بەڕێوەبردنی کۆگا")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("زیادکردنی کەلوپەل")
        item = st.text_input("🏷️ ناوی کەلوپەل")
        stock = st.number_input("📦 ژمارە", min_value=1, value=1)
        price = st.number_input("💰 نرخی کڕین ($)", min_value=0.0)
        
        if st.button("➕ زیادکردن"):
            if item and stock > 0:
                add_inventory(item, stock, price)
                st.success(f"✅ {stock} دانە {item} زیاد کرا!")
    
    with col2:
        if not st.session_state.inventory.empty:
            st.subheader("کۆگا")
            d = st.session_state.inventory.copy()
            d['کۆی بەها'] = d['دانە'] * d['نرخی کڕین']
            st.dataframe(d)

elif menu == "🛡️ گەرەنتی":
    st.header("🛡️ گەرەنتی")
    
    customer = st.text_input("👤 کڕیار")
    imei = st.text_input("📱 IMEI (15 ژمارە)")
    device = st.text_input("📱 جۆری مۆبایل")
    end_date = st.date_input("📅 کۆتایی گەرەنتی")
    
    if st.button("➕ تۆمارکردن"):
        if customer and imei and len(imei) == 15:
            new = pd.DataFrame({
                'کڕیار': [customer], 'IMEI': [imei],
                'کۆتایی گەرەنتی': [end_date.strftime("%Y-%m-%d")],
                'مۆبایل': [device]
            })
            st.session_state.warranty = pd.concat([st.session_state.warranty, new], ignore_index=True)
            st.success("✅ تۆمار کرا!")
    
    if not st.session_state.warranty.empty:
        st.dataframe(st.session_state.warranty)

elif menu == "📊 قازانج":
    st.header("📊 قازانج")
    
    ts = st.session_state.sales['نرخ'].sum() if not st.session_state.sales.empty else 0
    tc = (st.session_state.inventory['نرخی کڕین'] * st.session_state.inventory['دانە']).sum() if not st.session_state.inventory.empty else 0
    te = st.session_state.expenses['بڕ'].sum() if not st.session_state.expenses.empty else 0
    profit = ts - tc - te
    
    col1, col2, col3 = st.columns(3)
    col1.metric("کۆی فرۆشتن", f"${ts:,.2f}")
    col2.metric("تێچوو", f"${tc:,.2f}")
    col3.metric("قازانج", f"${profit:,.2f}")
    
    if ts > 0:
        fig = go.Figure(data=[
            go.Bar(name='فرۆشتن', x=['دارایی'], y=[ts]),
            go.Bar(name='تێچوو', x=['دارایی'], y=[tc]),
            go.Bar(name='قازانج', x=['دارایی'], y=[profit])
        ])
        st.plotly_chart(fig)

elif menu == "👥 کڕیاران":
    st.header("👥 کڕیاران")
    
    name = st.text_input("👤 ناوی کڕیار")
    phone = st.text_input("📞 مۆبایل")
    email = st.text_input("📧 ئیمەیڵ")
    address = st.text_area("📍 ناونیشان")
    birthday = st.date_input("🎂 ڕێکەوتی لەدایکبوون")
    
    if st.button("➕ زیادکردن"):
        if name:
            new = pd.DataFrame({
                'ناو': [name], 'مۆبایل': [phone], 'ئیمەیڵ': [email],
                'ناونیشان': [address], 'ڕێکەوتی لەدایکبوون': [birthday.strftime("%Y-%m-%d")]
            })
            st.session_state.customers = pd.concat([st.session_state.customers, new], ignore_index=True)
            st.success("✅ زیاد کرا!")
    
    if not st.session_state.customers.empty:
        st.dataframe(st.session_state.customers)

elif menu == "💸 خەرجی":
    st.header("💸 خەرجییەکان")
    
    expense_type = st.selectbox("جۆر", ["کرێ", "مووچە", "کارەبا", "ئینتەرنێت", "ی تر"])
    amount = st.number_input("بڕ ($)", min_value=0.0)
    date = st.date_input("بەروار")
    
    if st.button("➕ زیادکردن"):
        add_expense(date.strftime("%Y-%m-%d"), expense_type, amount)
        st.success("✅ تۆمار کرا!")
    
    if not st.session_state.expenses.empty:
        st.dataframe(st.session_state.expenses)

elif menu == "⭐ هەڵسەنگاندن":
    st.header("⭐ هەڵسەنگاندنی کڕیاران")
    
    if not st.session_state.customers.empty:
        customer = st.selectbox("کڕیار", st.session_state.customers['ناو'])
        product = st.text_input("بەرهەم")
        rating = st.slider("ئەستێرە", 1, 5, 5)
        st.markdown(f"### {'⭐'*rating}{'☆'*(5-rating)}")
        comment = st.text_area("سەرنج")
        
        if st.button("📝 تۆمارکردن"):
            new = pd.DataFrame({'کڕیار': [customer], 'بەرهەم': [product], 'ئەستێرە': [rating], 'سەرنج': [comment]})
            st.session_state.reviews = pd.concat([st.session_state.reviews, new], ignore_index=True)
            st.success("✅ تۆمار کرا!")
    
    if not st.session_state.reviews.empty:
        st.metric("تێکڕا", f"{st.session_state.reviews['ئەستێرە'].mean():.1f} ⭐")
        st.dataframe(st.session_state.reviews)

elif menu == "📅 کارەکان":
    st.header("📅 بەڕێوەبردنی کارەکان")
    
    title = st.text_input("ناونیشانی کار")
    deadline = st.date_input("وادە")
    status = st.selectbox("ڕەوش", ["چاوەڕوان", "لە ئەنجامدایە", "تەواو"])
    
    if st.button("➕ زیادکردن"):
        if title:
            new = pd.DataFrame({'ناونیشان': [title], 'وادە': [deadline.strftime("%Y-%m-%d")], 'ڕەوش': [status]})
            st.session_state.tasks = pd.concat([st.session_state.tasks, new], ignore_index=True)
            st.success("✅ زیاد کرا!")
    
    if not st.session_state.tasks.empty:
        today = datetime.now().strftime("%Y-%m-%d")
        st.subheader("کارەکانی ئەمڕۆ")
        today_tasks = st.session_state.tasks[st.session_state.tasks['وادە'] == today]
        if not today_tasks.empty:
            for _, t in today_tasks.iterrows():
                st.markdown(f"- **{t['ناونیشان']}** - {t['ڕەوش']}")
        else:
            st.success("✅ هیچ کارێک بۆ ئەمڕۆ نییە")

elif menu == "🎯 داشبۆرد":
    st.header("🎯 داشبۆردی سەرەکی")
    
    col1, col2, col3 = st.columns(3)
    
    ts_today = 0
    if not st.session_state.sales.empty:
        today = datetime.now().strftime("%Y-%m-%d")
        sales_today = st.session_state.sales[st.session_state.sales['کاتی فرۆشتن'].str.startswith(today)]
        ts_today = sales_today['نرخ'].sum()
    
    col1.metric("💰 فرۆشتنی ئەمڕۆ", f"${ts_today:,.2f}")
    col2.metric("📦 کەلوپەلی کەم", len(check_low_stock()))
    col3.metric("👥 کڕیاران", len(st.session_state.customers))
    
    # Recent sales
    if not st.session_state.sales.empty:
        st.subheader("📈 دوایین فرۆشتنەکان")
        st.dataframe(st.session_state.sales.tail(10))
    
    # Today's birthdays
    bdays = check_birthdays()
    if bdays:
        st.subheader("🎂 ڕۆژی لەدایکبوونی ئەمڕۆ")
        for b in bdays:
            st.success(f"🎉 {b}")

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: gray;'>📱 سیستەمی بەڕێوەبردنی دوکانی مۆبایل © 2024</div>", unsafe_allow_html=True)
