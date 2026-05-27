import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import base64
import qrcode
from PIL import Image
import numpy as np
from fpdf import FPDF
import time
import json
import pickle
import warnings
import os
warnings.filterwarnings('ignore')

# Try importing scikit-learn (optional)
try:
    from sklearn.ensemble import RandomForestRegressor
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

# ================== PAGE CONFIGURATION ==================
st.set_page_config(
    page_title="سیستەمی بەڕێوەبردنی دوکانی مۆبایل",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================== CUSTOM CSS ==================
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        color: white;
        transition: transform 0.3s;
    }
    .metric-card:hover {transform: translateY(-5px);}
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 10px;
    }
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    .customer-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
    }
    .chat-admin {background-color: #e3f2fd; padding: 10px; border-radius: 10px; margin: 5px;}
    .chat-user {background-color: #f3e5f5; padding: 10px; border-radius: 10px; margin: 5px; text-align: right;}
    .footer {
        text-align: center; padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; border-radius: 15px; margin-top: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# ================== SESSION STATE ==================
def init_session():
    if 'sales' not in st.session_state:
        st.session_state.sales = pd.DataFrame(columns=['ناوی بەرهەم','نرخ','کاتی فرۆشتن','ناوی کڕیار','کۆدی داشکاندن','نرخی کۆتایی','کارمەند'])
    if 'inventory' not in st.session_state:
        st.session_state.inventory = pd.DataFrame(columns=['ناوی کەلوپەل','ژمارەی دانەکان','نرخی کڕین','بەرواری زیادکردن','کەمترین ژمارە'])
    if 'warranty' not in st.session_state:
        st.session_state.warranty = pd.DataFrame(columns=['ناوی کڕیار','ژمارەی IMEI','بەرواری کۆتایی گەرەنتی','جۆری مۆبایل'])
    if 'customers' not in st.session_state:
        st.session_state.customers = pd.DataFrame(columns=['ناوی کڕیار','ژمارەی مۆبایل','ئیمەیڵ','ناونیشان','بەرواری زیادکردن','ڕێکەوتی لەدایکبوون','کۆی کڕین','خاڵەکان','ئاست'])
    if 'discounts' not in st.session_state:
        st.session_state.discounts = pd.DataFrame(columns=['کۆدی داشکاندن','ڕێژە','بەرواری دەستپێک','بەرواری کۆتایی','کەمترین کڕین','ژمارەی بەکارهێنان'])
    if 'employees' not in st.session_state:
        st.session_state.employees = pd.DataFrame(columns=['ناوی کارمەند','پلە','مووچە','بەرواری دەستبەکاربوون','ژمارەی فرۆشتن','کۆی فرۆشتن','پاداشت'])
    if 'repairs' not in st.session_state:
        st.session_state.repairs = pd.DataFrame(columns=['ID','ناوی کڕیار','جۆری مۆبایل','کێشە','بەرواری وەرگرتن','بەرواری گەڕاندنەوە','نرخی چاککردنەوە','ڕەوش'])
    if 'loyalty_points' not in st.session_state:
        st.session_state.loyalty_points = {}
    if 'last_sale_invoice' not in st.session_state:
        st.session_state.last_sale_invoice = None
    if 'installments' not in st.session_state:
        st.session_state.installments = pd.DataFrame(columns=['ID','ناوی کڕیار','بەرهەم','کۆی نرخ','پارەی پێشەکی','مانگانە','ماوە (مانگ)','بەرواری دەستپێک','بەرواری کۆتایی','پارەی دراو','پارەی ماوە','ڕەوش','بەرواری داهاتووی قیست'])
    if 'messages' not in st.session_state:
        st.session_state.messages = pd.DataFrame(columns=['ID','ناوی کڕیار','ژمارە','پەیام','بەروار','ڕەوش'])
    if 'deliveries' not in st.session_state:
        st.session_state.deliveries = pd.DataFrame(columns=['ID','ناوی کڕیار','ژمارەی مۆبایل','ناونیشان','بەرهەم','بەرواری داواکاری','بەرواری گەیاندن','تێچووی گەیاندن','ڕەوش','تێبینی'])
    if 'tickets' not in st.session_state:
        st.session_state.tickets = pd.DataFrame(columns=['ID','ناوی کڕیار','بابەت','کێشە','لەولەوەپێشی','بەرواری کردنەوە','بەرواری داخستن','ڕەوش','وەڵام'])
    if 'events' not in st.session_state:
        st.session_state.events = pd.DataFrame(columns=['ناونیشان','جۆر','بەرواری دەستپێک','بەرواری کۆتایی','ڕێژەی داشکاندن','بەرهەمەکان','ڕەوش'])
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    if 'expenses' not in st.session_state:
        st.session_state.expenses = pd.DataFrame(columns=['بەروار','جۆر','بڕ','تێبینی'])
    if 'suppliers' not in st.session_state:
        st.session_state.suppliers = pd.DataFrame(columns=['ID','ناوی کۆمپانیا','بەرپرس','مۆبایل','ئیمەیڵ','ناونیشان','جۆری کەلوپەل'])
    if 'attendance' not in st.session_state:
        st.session_state.attendance = pd.DataFrame(columns=['کارمەند','بەروار','کاتی هاتن','کاتی ڕۆیشتن','کاتژمێر','ڕەوش'])
    if 'reviews' not in st.session_state:
        st.session_state.reviews = pd.DataFrame(columns=['کڕیار','بەرهەم','ئەستێرە','سەرنج','بەروار'])
    if 'tasks' not in st.session_state:
        st.session_state.tasks = pd.DataFrame(columns=['ناونیشان','وەسف','وادە','لەولەوەپێشی','کارمەند','ڕەوش'])
    if 'purchase_orders' not in st.session_state:
        st.session_state.purchase_orders = pd.DataFrame(columns=['ID','دابینکەر','کەلوپەل','دانە','نرخ','کۆی نرخ','ڕەوش'])

init_session()

# ================== HELPER FUNCTIONS ==================
def add_sale(product_name, price, customer_name, discount_code="", employee=""):
    final_price = apply_discount(price, discount_code)
    new_sale = pd.DataFrame({
        'ناوی بەرهەم': [product_name], 'نرخ': [float(price)],
        'کاتی فرۆشتن': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        'ناوی کڕیار': [customer_name], 'کۆدی داشکاندن': [discount_code],
        'نرخی کۆتایی': [final_price], 'کارمەند': [employee]
    })
    st.session_state.sales = pd.concat([st.session_state.sales, new_sale], ignore_index=True)
    add_loyalty_points(customer_name, final_price)
    if employee: update_employee_performance(employee, final_price)
    st.session_state.last_sale_invoice = generate_invoice({
        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'customer': customer_name, 'product': product_name,
        'price': price, 'final_price': final_price
    })
    return True

def apply_discount(price, code):
    if code and not st.session_state.discounts.empty:
        d = st.session_state.discounts[st.session_state.discounts['کۆدی داشکاندن'] == code]
        if not d.empty: return price * (1 - d['ڕێژە'].iloc[0] / 100)
    return price

def add_loyalty_points(customer, amount):
    points = int(amount / 10)
    st.session_state.loyalty_points[customer] = st.session_state.loyalty_points.get(customer, 0) + points
    total = st.session_state.loyalty_points[customer]
    level = "🏆 پلاتینیۆم" if total >= 1000 else ("🥇 زێڕین" if total >= 500 else ("🥈 زیوین" if total >= 200 else "🥉 ئاسایی"))
    if customer in st.session_state.customers['ناوی کڕیار'].values:
        idx = st.session_state.customers[st.session_state.customers['ناوی کڕیار'] == customer].index[0]
        st.session_state.customers.at[idx, 'خاڵەکان'] = total
        st.session_state.customers.at[idx, 'ئاست'] = level
        st.session_state.customers.at[idx, 'کۆی کڕین'] += amount

def update_employee_performance(emp, amount):
    if emp in st.session_state.employees['ناوی کارمەند'].values:
        idx = st.session_state.employees[st.session_state.employees['ناوی کارمەند'] == emp].index[0]
        st.session_state.employees.at[idx, 'ژمارەی فرۆشتن'] += 1
        st.session_state.employees.at[idx, 'کۆی فرۆشتن'] += amount
        st.session_state.employees.at[idx, 'پاداشت'] += amount * 0.02

def generate_invoice(data):
    try:
        pdf = FPDF(); pdf.add_page()
        pdf.set_font("Arial", "B", 20)
        pdf.cell(0, 10, "Mobile Shop Invoice", ln=True, align="C")
        pdf.line(10, pdf.get_y(), 200, pdf.get_y()); pdf.ln(10)
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"Date: {data.get('date', '')}", ln=True)
        pdf.cell(0, 10, f"Customer: {data.get('customer', '')}", ln=True)
        pdf.cell(0, 10, f"Product: {data.get('product', '')}", ln=True)
        pdf.cell(0, 10, f"Price: ${data.get('final_price', 0)}", ln=True)
        try:
            qr = qrcode.make(f"INV{datetime.now().strftime('%Y%m%d%H%M%S')}")
            qr.save("temp_qr.png")
            pdf.image("temp_qr.png", x=150, y=30, w=40)
        except: pass
        pdf.output("temp_invoice.pdf")
        with open("temp_invoice.pdf", "rb") as f: result = f.read()
        for f in ["temp_qr.png", "temp_invoice.pdf"]:
            if os.path.exists(f): os.remove(f)
        return result
    except: return None

def check_low_stock():
    if not st.session_state.inventory.empty:
        return st.session_state.inventory[st.session_state.inventory['ژمارەی دانەکان'] < st.session_state.inventory['کەمترین ژمارە']]
    return pd.DataFrame()

def check_expiring_warranty():
    if not st.session_state.warranty.empty:
        today = datetime.now().date()
        dates = pd.to_datetime(st.session_state.warranty['بەرواری کۆتایی گەرەنتی']).dt.date
        return st.session_state.warranty[((dates - today).dt.days <= 30) & ((dates - today).dt.days >= 0)]
    return pd.DataFrame()

def check_upcoming_installments():
    if not st.session_state.installments.empty:
        today = datetime.now().date()
        return st.session_state.installments[(pd.to_datetime(st.session_state.installments['بەرواری داهاتووی قیست']).dt.date - today).dt.days <= 7]
    return pd.DataFrame()

def check_birthdays():
    today = datetime.now()
    birthdays = []
    if not st.session_state.customers.empty:
        for _, c in st.session_state.customers.iterrows():
            if c['ڕێکەوتی لەدایکبوون']:
                bd = pd.to_datetime(c['ڕێکەوتی لەدایکبوون'])
                if bd.month == today.month and bd.day == today.day:
                    birthdays.append(c['ناوی کڕیار'])
    return birthdays

def export_to_excel(df, sheet="Data"):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as w: df.to_excel(w, sheet_name=sheet, index=False)
    return output.getvalue()

def get_download_link(data, filename):
    return f'<a href="data:application/octet-stream;base64,{base64.b64encode(data).decode()}" download="{filename}">📥 {filename}</a>'

def backup_data():
    all_data = {k: v.to_dict() if hasattr(v, 'to_dict') else v for k, v in st.session_state.items() if not k.startswith('_')}
    all_data['backup_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return json.dumps(all_data, default=str), pickle.dumps(all_data)

def restore_data(uploaded_file):
    try:
        data = json.loads(uploaded_file.read()) if uploaded_file.name.endswith('.json') else pickle.loads(uploaded_file.read())
        for key in data:
            if key != 'backup_date' and key in st.session_state:
                if isinstance(data[key], dict) and hasattr(st.session_state[key], 'empty'):
                    st.session_state[key] = pd.DataFrame(data[key])
                else:
                    st.session_state[key] = data[key]
        return True
    except: return False

# ================== SIDEBAR ==================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/shop.png", width=80)
    st.title("📱 مینوی سەرەکی")
    
    st.markdown("---")
    st.markdown("### 🔔 ئاگادارییەکان")
    
    low = check_low_stock()
    if not low.empty:
        with st.expander(f"⚠️ {len(low)} کەلوپەلی کەم!", expanded=True):
            for _, i in low.iterrows(): st.error(f"📦 {i['ناوی کەلوپەل']}: {i['ژمارەی دانەکان']} دانە")
    
    exp = check_expiring_warranty()
    if not exp.empty:
        with st.expander(f"⏰ {len(exp)} گەرەنتی نزیک!", expanded=False):
            for _, w in exp.iterrows(): st.warning(f"📱 {w['ناوی کڕیار']}")
    
    inst = check_upcoming_installments()
    if not inst.empty:
        with st.expander(f"💳 {len(inst)} قیستی نزیک!", expanded=False):
            for _, i in inst.iterrows(): st.warning(f"💰 {i['ناوی کڕیار']}: ${i['مانگانە']:,.2f}")
    
    bdays = check_birthdays()
    if bdays:
        for b in bdays: st.success(f"🎂 {b}")
    
    st.markdown("---")
    
    menu = {
        "💰 فرۆشتن": ["📝 فرۆشتنی نوێ", "📋 لیست", "🧾 فاکتوور", "📷 سکانی بارکۆد"],
        "📦 کۆگا": ["📝 زیادکردن", "📋 لیست", "🔄 بەڕێوەبردن", "🏭 دابینکەران", "📋 داواکاری کڕین"],
        "🛡️ گەرەنتی": ["📝 تۆمارکردن", "📋 لیست", "⚠️ ئاگاداری"],
        "📊 قازانج": ["💰 خەمڵاندن", "📈 هێڵکاری", "📋 ڕاپۆرت", "💸 خەرجی", "📄 ڕاپۆرتی PDF"],
        "👥 کڕیاران": ["📝 زیادکردن", "📋 لیست", "⭐ خاڵ", "🌟 هەڵسەنگاندن"],
        "💳 قیست": ["📝 نوێ", "📋 لیست", "📊 بەدواداچوون", "💵 پارەدان"],
        "🏷️ داشکاندن": ["📝 نوێ", "📋 لیست", "🎉 بۆنە", "📢 مارکێتینگ"],
        "👨‍💼 کارمەندان": ["📝 زیادکردن", "📋 لیست", "📊 ئاست", "🕐 ئامادەبوون", "💰 مووچە"],
        "🔧 چاککردنەوە": ["📝 تۆمارکردن", "📋 لیست", "🔄 بەڕێوەبردن"],
        "🚚 گەیاندن": ["📝 نوێ", "📋 لیست"],
        "📱 پەیام": ["📝 ناردن", "📋 مێژوو"],
        "🎫 پشتیوانی": ["📝 تیکت", "📋 تیکتەکان", "💬 چات"],
        "📅 ڕۆژمێر": ["📝 کاری نوێ", "📋 کارەکان", "📅 ڕۆژمێر"],
        "📊 داشبۆرد": ["🎯 سەرەکی", "🔮 پێشبینیکردن", "📊 بەراورد", "📈 شیکاری"],
        "⚙️ ڕێکخستن": ["💾 بەکاپ", "🎨 ڕووکار", "🔔 ئاگادارییەکان"]
    }
    
    main_choice = st.selectbox("بەشێک هەڵبژێرە:", list(menu.keys()))
    sub_choice = st.radio("ژێربەش:", menu[main_choice]) if main_choice in menu else None
    
    st.markdown("---")
    st.markdown("### 📊 کورتە")
    ts = st.session_state.sales['نرخی کۆتایی'].sum() if not st.session_state.sales.empty else 0
    tc = (st.session_state.inventory['نرخی کڕین'] * st.session_state.inventory['ژمارەی دانەکان']).sum() if not st.session_state.inventory.empty else 0
    te = st.session_state.expenses['بڕ'].sum() if not st.session_state.expenses.empty else 0
    c1, c2, c3 = st.columns(3)
    c1.metric("💰 فرۆشتن", f"${ts:,.0f}")
    c2.metric("👥 کڕیار", len(st.session_state.customers))
    c3.metric("💵 قازانج", f"${ts-tc-te:,.0f}")

# ================== MAIN CONTENT ==================
st.markdown('<p class="main-header">📱 سیستەمی بەڕێوەبردنی دوکانی مۆبایل</p>', unsafe_allow_html=True)

# ================== 1. SALES ==================
if main_choice == "💰 فرۆشتن" and sub_choice == "📝 فرۆشتنی نوێ":
    st.header("📝 فرۆشتنی نوێ")
    c1, c2 = st.columns([2, 1])
    with c1:
        with st.form("sale"):
            p = st.text_input("📱 بەرهەم", placeholder="iPhone 15 Pro")
            pr, cu = st.columns(2)
            price = pr.number_input("💵 نرخ ($)", min_value=0.0, step=10.0)
            cust = cu.text_input("👤 کڕیار")
            dc, em = st.columns(2)
            code = dc.text_input("🏷️ کۆدی داشکاندن")
            emp = em.selectbox("👨‍💼 کارمەند", [""] + list(st.session_state.employees['ناوی کارمەند'])) if not st.session_state.employees.empty else ""
            fp = apply_discount(price, code) if code else price
            if code and fp != price: st.success(f"💰 کۆتایی: ${fp:,.2f}")
            if st.form_submit_button("➕ تۆمارکردن"):
                if p and price > 0 and cust:
                    add_sale(p, price, cust, code, emp)
                    st.success(f"✅ فرۆشرا بە ${fp:,.2f}"); st.balloons()
                    if st.session_state.last_sale_invoice:
                        st.download_button("📄 فاکتوور", st.session_state.last_sale_invoice, "invoice.pdf", "application/pdf")
                else: st.error("هەموو خانەکان پڕ بکە!")
    with c2:
        if not st.session_state.sales.empty:
            st.subheader("📈 دوایین فرۆشتن")
            st.dataframe(st.session_state.sales.tail(5)[['ناوی بەرهەم','نرخی کۆتایی','ناوی کڕیار']])

elif main_choice == "💰 فرۆشتن" and sub_choice == "📋 لیست":
    st.header("📋 لیستی فرۆشتنەکان")
    if not st.session_state.sales.empty:
        f1, f2, f3 = st.columns(3)
        df = f1.date_input("📅 بەروار", value=None)
        pf = f2.multiselect("📱 بەرهەم", st.session_state.sales['ناوی بەرهەم'].unique())
        cf = f3.text_input("👤 گەڕان")
        flt = st.session_state.sales.copy()
        if df:
            flt['d'] = pd.to_datetime(flt['کاتی فرۆشتن']).dt.date
            flt = flt[flt['d'] == df]
        if pf: flt = flt[flt['ناوی بەرهەم'].isin(pf)]
        if cf: flt = flt[flt['ناوی کڕیار'].str.contains(cf, case=False)]
        st.dataframe(flt)
        c1, c2, c3 = st.columns(3)
        c1.metric("ژمارە", len(flt))
        c2.metric("کۆی داهات", f"${flt['نرخی کۆتایی'].sum():,.2f}")
        c3.metric("تێکڕا", f"${flt['نرخی کۆتایی'].mean():,.2f}" if not flt.empty else "$0")
        if st.button("📥 Excel"): st.markdown(get_download_link(export_to_excel(flt, 'Sales'), 'sales.xlsx'), unsafe_allow_html=True)
    else: st.info("هیچ فرۆشتنێک نییە")

elif main_choice == "💰 فرۆشتن" and sub_choice == "🧾 فاکتوور":
    st.header("🧾 فاکتوور")
    if not st.session_state.sales.empty:
        s = st.selectbox("فرۆشتن", range(len(st.session_state.sales)), format_func=lambda x: f"{st.session_state.sales.iloc[x]['ناوی بەرهەم']} - {st.session_state.sales.iloc[x]['ناوی کڕیار']}")
        if st.button("🧾 دروستکردن"):
            r = st.session_state.sales.iloc[s]
            inv = generate_invoice({'date': r['کاتی فرۆشتن'], 'customer': r['ناوی کڕیار'], 'product': r['ناوی بەرهەم'], 'final_price': r['نرخی کۆتایی']})
            if inv: st.download_button("📄 فاکتوور", inv, "invoice.pdf", "application/pdf")

elif main_choice == "💰 فرۆشتن" and sub_choice == "📷 سکانی بارکۆد":
    st.header("📷 سکانی بارکۆد")
    bc = st.text_input("🔢 بارکۆد", placeholder="سکان بکە یان بنووسە...")
    if bc:
        prod = None
        if not st.session_state.inventory.empty:
            for _, r in st.session_state.inventory.iterrows():
                if bc.lower() in r['ناوی کەلوپەل'].lower(): prod = r; break
        if prod is not None:
            st.success(f"✅ {prod['ناوی کەلوپەل']}")
            c1, c2 = st.columns(2)
            c1.metric("نرخ", f"${prod['نرخی کڕین']:,.2f}")
            c1.metric("دانە", prod['ژمارەی دانەکان'])
            pr = c2.number_input("نرخی فرۆشتن", value=float(prod['نرخی کڕین'])*1.3)
            cust = c2.text_input("کڕیار")
            if st.button("🛒 فرۆشتنی خێرا") and cust:
                add_sale(prod['ناوی کەلوپەل'], pr, cust)
                st.success("✅ فرۆشرا!"); st.balloons()
        else: st.error("❌ نەدۆزرایەوە!")

# ================== 2. INVENTORY ==================
elif main_choice == "📦 کۆگا" and sub_choice == "📝 زیادکردن":
    st.header("📝 زیادکردنی کەلوپەل")
    with st.form("inv"):
        n = st.text_input("🏷️ ناو")
        s, p = st.columns(2)
        stk = s.number_input("📦 دانە", min_value=1, step=1)
        prc = p.number_input("💰 نرخ ($)", min_value=0.0, step=1.0)
        mn = st.number_input("⚠️ ئاستی ئاگاداری", min_value=1, value=5)
        if st.form_submit_button("➕ زیادکردن"):
            if n and stk > 0:
                ni = pd.DataFrame({'ناوی کەلوپەل': [n], 'ژمارەی دانەکان': [stk], 'نرخی کڕین': [prc], 'بەرواری زیادکردن': [datetime.now().strftime("%Y-%m-%d")], 'کەمترین ژمارە': [mn]})
                st.session_state.inventory = pd.concat([st.session_state.inventory, ni], ignore_index=True)
                st.success(f"✅ {stk} دانە {n} زیاد کرا!")

elif main_choice == "📦 کۆگا" and sub_choice == "📋 لیست":
    st.header("📋 کۆگا")
    if not st.session_state.inventory.empty:
        d = st.session_state.inventory.copy()
        d['کۆی بەها'] = d['ژمارەی دانەکان'] * d['نرخی کڕین']
        d['ڕەوش'] = d.apply(lambda x: '🔴 کەم' if x['ژمارەی دانەکان'] < x['کەمترین ژمارە'] else '🟢 باش', axis=1)
        st.dataframe(d)
        c1, c2, c3 = st.columns(3)
        c1.metric("جۆر", len(d))
        c2.metric("دانە", d['ژمارەی دانەکان'].sum())
        c3.metric("بەها", f"${d['کۆی بەها'].sum():,.2f}")
        if st.button("📥 Excel"): st.markdown(get_download_link(export_to_excel(d, 'Inventory'), 'inventory.xlsx'), unsafe_allow_html=True)

elif main_choice == "📦 کۆگا" and sub_choice == "🔄 بەڕێوەبردن":
    st.header("🔄 بەڕێوەبردنی کۆگا")
    if not st.session_state.inventory.empty:
        it = st.selectbox("کەلوپەل", st.session_state.inventory['ناوی کەلوپەل'])
        ci = st.session_state.inventory[st.session_state.inventory['ناوی کەلوپەل'] == it].iloc[0]
        st.info(f"ئێستا: {ci['ژمارەی دانەکان']} | ${ci['نرخی کڕین']}")
        c1, c2 = st.columns(2)
        ch = c1.number_input("گۆڕانکاری (+/-)", value=0, step=1)
        np = c2.number_input("نرخی نوێ (0=بێ گۆڕان)", value=0.0)
        if st.button("🔄 نوێکردنەوە"):
            idx = st.session_state.inventory[st.session_state.inventory['ناوی کەلوپەل'] == it].index[0]
            if ch != 0:
                ns = ci['ژمارەی دانەکان'] + ch
                if ns >= 0: st.session_state.inventory.at[idx, 'ژمارەی دانەکان'] = ns
                else: st.error("ناتوانێت سالب بێت!"); st.stop()
            if np > 0: st.session_state.inventory.at[idx, 'نرخی کڕین'] = np
            st.success("✅ نوێ کرایەوە!"); st.rerun()

elif main_choice == "📦 کۆگا" and sub_choice == "🏭 دابینکەران":
    st.header("🏭 دابینکەران")
    with st.form("sup"):
        c = st.text_input("🏢 کۆمپانیا")
        ct = st.text_input("👤 بەرپرس")
        ph = st.text_input("📞 مۆبایل")
        em = st.text_input("📧 ئیمەیڵ")
        ad = st.text_input("📍 ناونیشان")
        pt = st.text_input("📦 جۆری کەلوپەل")
        if st.form_submit_button("➕ زیادکردن") and c:
            ns = pd.DataFrame({'ID': [f"SUP{datetime.now().strftime('%Y%m%d%H%M%S')}"], 'ناوی کۆمپانیا': [c], 'بەرپرس': [ct], 'مۆبایل': [ph], 'ئیمەیڵ': [em], 'ناونیشان': [ad], 'جۆری کەلوپەل': [pt]})
            st.session_state.suppliers = pd.concat([st.session_state.suppliers, ns], ignore_index=True)
            st.success("✅ زیاد کرا!")
    if not st.session_state.suppliers.empty: st.dataframe(st.session_state.suppliers)

elif main_choice == "📦 کۆگا" and sub_choice == "📋 داواکاری کڕین":
    st.header("📋 داواکاری کڕین")
    low = check_low_stock()
    if not low.empty: st.warning(f"⚠️ {len(low)} کەلوپەل کەمە!")
    with st.form("po"):
        sup = st.selectbox("دابینکەر", st.session_state.suppliers['ناوی کۆمپانیا']) if not st.session_state.suppliers.empty else st.text_input("دابینکەر")
        prod = st.selectbox("کەلوپەل", st.session_state.inventory['ناوی کەلوپەل']) if not st.session_state.inventory.empty else st.text_input("کەلوپەل")
        qty = st.number_input("دانە", min_value=1, value=10)
        prc = st.number_input("نرخ ($)", min_value=0.0)
        st.info(f"کۆی نرخ: ${qty*prc:,.2f}")
        if st.form_submit_button("📝 دروستکردن") and sup and prod:
            np = pd.DataFrame({'ID': [f"PO{datetime.now().strftime('%Y%m%d%H%M%S')}"], 'دابینکەر': [sup], 'کەلوپەل': [prod], 'دانە': [qty], 'نرخ': [prc], 'کۆی نرخ': [qty*prc], 'ڕەوش': ['چاوەڕوان']})
            st.session_state.purchase_orders = pd.concat([st.session_state.purchase_orders, np], ignore_index=True)
            st.success("✅ تۆمار کرا!")
    if not st.session_state.purchase_orders.empty: st.dataframe(st.session_state.purchase_orders)

# ================== 3. WARRANTY ==================
elif main_choice == "🛡️ گەرەنتی" and sub_choice == "📝 تۆمارکردن":
    st.header("📝 گەرەنتی نوێ")
    with st.form("war"):
        c = st.text_input("👤 کڕیار")
        i, d = st.columns(2)
        im = i.text_input("📱 IMEI (15)")
        dm = d.text_input("📱 جۆری مۆبایل")
        we = st.date_input("📅 کۆتایی گەرەنتی", min_value=datetime.now().date())
        if st.form_submit_button("➕ تۆمارکردن") and c and im and len(im)==15 and im.isdigit():
            nw = pd.DataFrame({'ناوی کڕیار': [c], 'ژمارەی IMEI': [im], 'بەرواری کۆتایی گەرەنتی': [we.strftime("%Y-%m-%d")], 'جۆری مۆبایل': [dm]})
            st.session_state.warranty = pd.concat([st.session_state.warranty, nw], ignore_index=True)
            st.success("✅ تۆمار کرا!")

elif main_choice == "🛡️ گەرەنتی" and sub_choice == "📋 لیست":
    st.header("📋 گەرەنتییەکان")
    if not st.session_state.warranty.empty:
        d = st.session_state.warranty.copy()
        d['کۆتایی'] = pd.to_datetime(d['بەرواری کۆتایی گەرەنتی'])
        d['ڕۆژ'] = (d['کۆتایی'] - datetime.now()).dt.days
        d['ڕەوش'] = d['ڕۆژ'].apply(lambda x: '🔴 بەسەرچوو' if x<0 else ('🔴 زۆر نزیک' if x<=7 else ('🟡 نزیک' if x<=30 else '🟢 چالاک')))
        st.dataframe(d)
        if st.button("📥 Excel"): st.markdown(get_download_link(export_to_excel(d, 'Warranty'), 'warranty.xlsx'), unsafe_allow_html=True)

elif main_choice == "🛡️ گەرەنتی" and sub_choice == "⚠️ ئاگاداری":
    st.header("⚠️ ئاگادارییەکان")
    exp = check_expiring_warranty()
    if not exp.empty:
        st.warning(f"⚠️ {len(exp)} گەرەنتی نزیکە!")
        for _, w in exp.iterrows(): st.markdown(f"<div class='customer-card'><h4>📱 {w['جۆری مۆبایل']}</h4><p>👤 {w['ناوی کڕیار']}</p><p>📅 {w['بەرواری کۆتایی گەرەنتی']}</p></div>", unsafe_allow_html=True)
    else: st.success("✅ هیچ گەرەنتییەکی نزیک نییە!")

# ================== 4. PROFIT ==================
elif main_choice == "📊 قازانج":
    ts = st.session_state.sales['نرخی کۆتایی'].sum() if not st.session_state.sales.empty else 0
    tc = (st.session_state.inventory['نرخی کڕین'] * st.session_state.inventory['ژمارەی دانەکان']).sum() if not st.session_state.inventory.empty else 0
    te = st.session_state.expenses['بڕ'].sum() if not st.session_state.expenses.empty else 0
    p = ts - tc - te
    pm = (p/ts*100) if ts > 0 else 0
    
    if sub_choice == "💰 خەمڵاندن":
        st.header("💰 قازانج")
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown('<div class="metric-card">', unsafe_allow_html=True); c1.metric("فرۆشتن", f"${ts:,.2f}"); c1.markdown('</div>', unsafe_allow_html=True)
        c2.markdown('<div class="metric-card">', unsafe_allow_html=True); c2.metric("تێچوو", f"${tc:,.2f}"); c2.markdown('</div>', unsafe_allow_html=True)
        c3.markdown('<div class="metric-card">', unsafe_allow_html=True); c3.metric("خەرجی", f"${te:,.2f}"); c3.markdown('</div>', unsafe_allow_html=True)
        c4.markdown('<div class="metric-card">', unsafe_allow_html=True); c4.metric("قازانج", f"${p:,.2f}", f"{pm:.1f}%"); c4.markdown('</div>', unsafe_allow_html=True)
        if pm > 30: st.success("🎉 زۆر باشە!")
        elif pm > 15: st.info("👍 باشە")
        elif pm > 0: st.warning("⚠️ کەمە")
        else: st.error("❌ زیانە!")
    
    elif sub_choice == "📈 هێڵکاری":
        st.header("📈 هێڵکاری")
        fig = go.Figure(data=[go.Bar(name='فرۆشتن', x=['دارایی'], y=[ts], marker_color='#2ecc71'), go.Bar(name='تێچوو', x=['دارایی'], y=[tc], marker_color='#e74c3c'), go.Bar(name='خەرجی', x=['دارایی'], y=[te], marker_color='#f39c12'), go.Bar(name='قازانج', x=['دارایی'], y=[p], marker_color='#3498db')])
        fig.update_layout(barmode='group', height=500); st.plotly_chart(fig)
    
    elif sub_choice == "📄 ڕاپۆرتی PDF":
        st.header("📄 ڕاپۆرتی PDF")
        rt = st.selectbox("جۆر", ["دارایی", "فرۆشتن", "کۆگا", "گشتی"])
        if st.button("📄 دروستکردن"):
            try:
                pdf = FPDF(); pdf.add_page()
                pdf.set_font("Arial", "B", 20); pdf.cell(0, 10, f"Mobile Shop - {rt}", ln=True, align="C")
                pdf.set_font("Arial", "", 12)
                pdf.cell(0, 10, f"Date: {datetime.now().strftime('%Y-%m-%d')}", ln=True)
                pdf.cell(0, 10, f"Total Sales: ${ts:,.2f}", ln=True)
                pdf.cell(0, 10, f"Net Profit: ${p:,.2f}", ln=True)
                rpt = pdf.output(dest='S').encode('latin-1')
                st.download_button("📥 داگرتن", rpt, f"report_{datetime.now().strftime('%Y%m%d')}.pdf", "application/pdf")
                st.success("✅ دروست کرا!")
            except: st.error("هەڵە!")

# ================== 5. CUSTOMERS ==================
elif main_choice == "👥 کڕیاران" and sub_choice == "🌟 هەڵسەنگاندن":
    st.header("🌟 هەڵسەنگاندن")
    if not st.session_state.customers.empty:
        c = st.selectbox("کڕیار", st.session_state.customers['ناوی کڕیار'])
        pr = st.session_state.sales[st.session_state.sales['ناوی کڕیار']==c]['ناوی بەرهەم'].unique()
        if len(pr)>0:
            p = st.selectbox("بەرهەم", pr)
            r = st.slider("ئەستێرە", 1, 5, 5)
            st.markdown(f"### {'⭐'*r}{'☆'*(5-r)}")
            cm = st.text_area("سەرنج")
            if st.button("📝 تۆمارکردن"):
                nr = pd.DataFrame({'کڕیار': [c], 'بەرهەم': [p], 'ئەستێرە': [r], 'سەرنج': [cm], 'بەروار': [datetime.now().strftime("%Y-%m-%d")]})
                st.session_state.reviews = pd.concat([st.session_state.reviews, nr], ignore_index=True)
                st.success("✅ تۆمار کرا!")
                if r <= 2: st.warning("⚠️ پێویستی بە پەیوەندییە!")
    if not st.session_state.reviews.empty:
        st.metric("تێکڕای ئەستێرە", f"{st.session_state.reviews['ئەستێرە'].mean():.1f} ⭐")
        st.dataframe(st.session_state.reviews)

# ================== 6. INSTALLMENTS ==================
elif main_choice == "💳 قیست" and sub_choice == "💵 پارەدان":
    st.header("💵 پارەدان")
    m = st.selectbox("شێواز", ["💵 کاش", "💳 کارت", "📱 مۆبایل"])
    a = st.number_input("بڕ ($)", min_value=0.0)
    if m == "💵 کاش":
        r = st.number_input("پارەی وەرگیراو", min_value=0.0)
        if r>0:
            ch = r-a
            if ch >= 0: st.success(f"💰 باقی: ${ch:,.2f}")
            else: st.error(f"کەمە! ${abs(ch):,.2f}")
    elif m == "💳 کارت":
        st.text_input("ژمارەی کارت", placeholder="**** **** **** ****")
        if st.button("💳 پارەدان"): st.success("✅ ئەنجامدرا!")
    elif m == "📱 مۆبایل":
        st.info("📱 ئەپی بانکی بەکاربهێنە")
        if st.button("✅ پشتڕاستکردنەوە"): st.success("✅ پشتڕاست کرا!")

# ================== 7. DISCOUNTS & MARKETING ==================
elif main_choice == "🏷️ داشکاندن" and sub_choice == "📢 مارکێتینگ":
    st.header("📢 هەڵمەتی مارکێتینگ")
    with st.form("camp"):
        n = st.text_input("ناوی هەڵمەت")
        t = st.selectbox("جۆر", ["📱 سۆشیال", "📧 ئیمەیڵ", "📩 SMS", "🎯 گووگڵ"])
        b = st.number_input("بودجە ($)", min_value=0.0)
        s, e = st.columns(2)
        stt = s.date_input("دەستپێک")
        end = e.date_input("کۆتایی")
        if st.form_submit_button("➕ دروستکردن") and n:
            st.success(f"✅ هەڵمەتی {n} دروست کرا!")

# ================== 8. EMPLOYEES ==================
elif main_choice == "👨‍💼 کارمەندان" and sub_choice == "🕐 ئامادەبوون":
    st.header("🕐 ئامادەبوون")
    if not st.session_state.employees.empty:
        e = st.selectbox("کارمەند", st.session_state.employees['ناوی کارمەند'])
        c1, c2, c3 = st.columns(3)
        if c1.button("🏃 هاتن"):
            na = pd.DataFrame({'کارمەند': [e], 'بەروار': [datetime.now().strftime("%Y-%m-%d")], 'کاتی هاتن': [datetime.now().strftime("%H:%M:%S")], 'کاتی ڕۆیشتن': [''], 'کاتژمێر': [0], 'ڕەوش': ['ئامادە']})
            st.session_state.attendance = pd.concat([st.session_state.attendance, na], ignore_index=True)
            st.success(f"✅ {e} هات")
        if c2.button("🚶 ڕۆیشتن"):
            idx = st.session_state.attendance[(st.session_state.attendance['کارمەند']==e)&(st.session_state.attendance['بەروار']==datetime.now().strftime("%Y-%m-%d"))].index
            if len(idx)>0:
                st.session_state.attendance.at[idx[-1], 'کاتی ڕۆیشتن'] = datetime.now().strftime("%H:%M:%S")
                st.success(f"✅ {e} ڕۆیشت")
            else: st.error("سەرەتا هاتن تۆمار بکە!")
        if c3.button("❌ عدم"):
            na = pd.DataFrame({'کارمەند': [e], 'بەروار': [datetime.now().strftime("%Y-%m-%d")], 'کاتی هاتن': [''], 'کاتی ڕۆیشتن': [''], 'کاتژمێر': [0], 'ڕەوش': ['عدم']})
            st.session_state.attendance = pd.concat([st.session_state.attendance, na], ignore_index=True)
            st.warning(f"⚠️ {e} عدم")
    if not st.session_state.attendance.empty: st.dataframe(st.session_state.attendance.tail(20))

elif main_choice == "👨‍💼 کارمەندان" and sub_choice == "💰 مووچە":
    st.header("💰 مووچە")
    if not st.session_state.employees.empty:
        e = st.selectbox("کارمەند", st.session_state.employees['ناوی کارمەند'])
        m = st.selectbox("مانگ", range(1,13), index=datetime.now().month-1)
        ed = st.session_state.employees[st.session_state.employees['ناوی کارمەند']==e]
        base = ed['مووچە'].iloc[0] if not ed.empty else 0
        bonus = ed['پاداشت'].iloc[0] if not ed.empty else 0
        absences = 0
        if not st.session_state.attendance.empty:
            ma = st.session_state.attendance[(st.session_state.attendance['کارمەند']==e)&(pd.to_datetime(st.session_state.attendance['بەروار']).dt.month==m)&(st.session_state.attendance['ڕەوش']=='عدم')]
            absences = len(ma)
        ded = (base/30)*absences
        total = base + bonus - ded
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("بنەڕەتی", f"${base:,.2f}")
        c2.metric("پاداشت", f"${bonus:,.2f}")
        c3.metric("کەمکردنەوە", f"${ded:,.2f}")
        c4.metric("💵 کۆی گشتی", f"${total:,.2f}")

# ================== 9. TASKS CALENDAR ==================
elif main_choice == "📅 ڕۆژمێر" and sub_choice == "📝 کاری نوێ":
    st.header("📝 کاری نوێ")
    with st.form("task"):
        t = st.text_input("ناونیشان")
        d = st.text_area("وەسف")
        dl = st.date_input("وادە", min_value=datetime.now().date())
        p = st.selectbox("لەولەوەپێشی", ["🔴 بەرز", "🟡 مامناوەند", "🟢 نزم"])
        a = st.selectbox("کارمەند", st.session_state.employees['ناوی کارمەند']) if not st.session_state.employees.empty else "خۆم"
        if st.form_submit_button("➕ زیادکردن") and t:
            nt = pd.DataFrame({'ناونیشان': [t], 'وەسف': [d], 'وادە': [dl.strftime("%Y-%m-%d")], 'لەولەوەپێشی': [p], 'کارمەند': [a], 'ڕەوش': ['چاوەڕوان']})
            st.session_state.tasks = pd.concat([st.session_state.tasks, nt], ignore_index=True)
            st.success("✅ زیاد کرا!")

elif main_choice == "📅 ڕۆژمێر" and sub_choice == "📅 ڕۆژمێر":
    st.header("📅 ڕۆژمێر")
    today = datetime.now()
    st.subheader(f"📌 {today.strftime('%A, %B %d, %Y')}")
    bdays = check_birthdays()
    if bdays:
        st.balloons()
        for b in bdays: st.success(f"🎂 {b}!")
    if not st.session_state.tasks.empty:
        tt = st.session_state.tasks[st.session_state.tasks['وادە']==today.strftime("%Y-%m-%d")]
        if not tt.empty:
            for _, t in tt.iterrows(): st.markdown(f"<div class='customer-card'><strong>{t['لەولەوەپێشی']}</strong> {t['ناونیشان']}<br><small>👤 {t['کارمەند']} | ⏰ {t['ڕەوش']}</small></div>", unsafe_allow_html=True)
        else: st.success("✅ هیچ کارێک بۆ ئەمڕۆ نییە!")

# ================== 10. ADVANCED ANALYTICS ==================
elif main_choice == "📊 داشبۆرد" and sub_choice == "📈 شیکاری":
    st.header("📈 شیکاری پێشکەوتوو")
    tab1, tab2 = st.tabs(["📊 گەیج", "📈 هێڵکاری"])
    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            sat = st.session_state.reviews['ئەستێرە'].mean()*20 if not st.session_state.reviews.empty else 85
            fig = go.Figure(go.Indicator(mode="gauge+number", value=sat, title={'text': "ڕەزامەندی %"}, gauge={'axis': {'range': [0,100]}, 'bar': {'color': "#667eea"}}))
            st.plotly_chart(fig)
        with c2:
            fig = go.Figure(go.Indicator(mode="gauge+number", value=ts if 'ts' in dir() else 0, title={'text': "فرۆشتن $"}, gauge={'axis': {'range': [0, max(ts*1.5 if 'ts' in dir() else 1000, 1000)]}, 'bar': {'color': "#667eea"}}))
            st.plotly_chart(fig)
    with tab2:
        if not st.session_state.sales.empty:
            sm = st.session_state.sales.copy()
            sm['m'] = pd.to_datetime(sm['کاتی فرۆشتن']).dt.month
            ms = sm.groupby('m')['نرخی کۆتایی'].sum()
            fig = px.line(x=ms.index, y=ms.values, labels={'x':'مانگ', 'y':'فرۆشتن'})
            st.plotly_chart(fig)

# ================== 11. SETTINGS ==================
elif main_choice == "⚙️ ڕێکخستن" and sub_choice == "💾 بەکاپ":
    st.header("💾 بەکاپ و گەڕاندنەوە")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📥 دروستکردنی بەکاپ"):
            jb, pb = backup_data()
            st.download_button("📥 JSON", jb, f"backup_{datetime.now().strftime('%Y%m%d')}.json", "application/json")
            st.download_button("📥 Pickle", pb, f"backup_{datetime.now().strftime('%Y%m%d')}.pkl", "application/octet-stream")
            st.success("✅ دروست کرا!")
    with c2:
        uf = st.file_uploader("فایلی بەکاپ", type=['json','pkl'])
        if uf and st.button("🔄 گەڕاندنەوە"):
            if restore_data(uf): st.success("✅ گەڕێندرایەوە!"); st.balloons()

elif main_choice == "⚙️ ڕێکخستن" and sub_choice == "🔔 ئاگادارییەکان":
    st.header("🔔 ئاگادارییە زیرەکەکان")
    nots = []
    for _, i in check_low_stock().iterrows(): nots.append(('error', f"📦 {i['ناوی کەلوپەل']}: {i['ژمارەی دانەکان']} دانە"))
    for _, w in check_expiring_warranty().iterrows():
        d = (pd.to_datetime(w['بەرواری کۆتایی گەرەنتی']).date()-datetime.now().date()).days
        nots.append(('warning' if d<=7 else 'info', f"⏰ {w['ناوی کڕیار']} {d} ڕۆژ"))
    for _, i in check_upcoming_installments().iterrows(): nots.append(('info', f"💳 {i['ناوی کڕیار']}: ${i['مانگانە']:,.2f}"))
    for b in check_birthdays(): nots.append(('success', f"🎂 {b}"))
    if nots:
        for t, m in nots:
            if t=='error': st.error(m)
            elif t=='warning': st.warning(m)
            elif t=='info': st.info(m)
            elif t=='success': st.success(m); st.balloons()
    else: st.success("✅ هیچ ئاگادارییەک نییە!")

# ================== DEFAULT DASHBOARD ==================
elif main_choice == "📊 داشبۆرد" and sub_choice == "🎯 سەرەکی":
    st.header("🎯 داشبۆردی سەرەکی")
    today = datetime.now().date()
    ts_today = 0
    if not st.session_state.sales.empty:
        stt = st.session_state.sales.copy()
        stt['d'] = pd.to_datetime(stt['کاتی فرۆشتن']).dt.date
        ts_today = stt[stt['d']==today]['نرخی کۆتایی'].sum()
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown('<div class="metric-card">', unsafe_allow_html=True); c1.metric("💰 ئەمڕۆ", f"${ts_today:,.2f}"); c1.markdown('</div>', unsafe_allow_html=True)
    c2.markdown('<div class="metric-card">', unsafe_allow_html=True); c2.metric("📦 کەم", len(check_low_stock())); c2.markdown('</div>', unsafe_allow_html=True)
    pr = len(st.session_state.repairs[st.session_state.repairs['ڕەوش'].isin(['چاوەڕوان','لەژێر کاردایە'])]) if not st.session_state.repairs.empty else 0
    c3.markdown('<div class="metric-card">', unsafe_allow_html=True); c3.metric("🔧 چاککردنەوە", pr); c3.markdown('</div>', unsafe_allow_html=True)
    at = len(st.session_state.tickets[st.session_state.tickets['ڕەوش']=='کراوە']) if not st.session_state.tickets.empty else 0
    c4.markdown('<div class="metric-card">', unsafe_allow_html=True); c4.metric("🎫 تیکت", at); c4.markdown('</div>', unsafe_allow_html=True)

# ================== FOOTER ==================
st.markdown("---")
st.markdown("""
    <div class="footer">
        <h3>📱 سیستەمی بەڕێوەبردنی دوکانی مۆبایل</h3>
        <p>© 2024 | 15 بەش | AI | پشتیوانی ڕاستەوخۆ</p>
    </div>
""", unsafe_allow_html=True)
