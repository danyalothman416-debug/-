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

# ================== PAGE CONFIGURATION ==================
st.set_page_config(
    page_title="سیستەمی بەڕێوەبردنی دوکانی مۆبایل - پڕۆ",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================== CUSTOM CSS ==================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Raleway:wght@400;700&display=swap');
    
    * {
        font-family: 'Raleway', sans-serif;
    }
    
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
    
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 10px;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    .notification-badge {
        background-color: #ff4757;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 20px;
        font-size: 0.8rem;
    }
    
    .customer-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# ================== SESSION STATE INITIALIZATION ==================
if 'sales' not in st.session_state:
    st.session_state.sales = pd.DataFrame(columns=['ناوی بەرهەم', 'نرخ', 'کاتی فرۆشتن', 'ناوی کڕیار', 'کۆدی داشکاندن', 'نرخی کۆتایی', 'کارمەند'])
if 'inventory' not in st.session_state:
    st.session_state.inventory = pd.DataFrame(columns=['ناوی کەلوپەل', 'ژمارەی دانەکان', 'نرخی کڕین', 'بەرواری زیادکردن', 'کەمترین ژمارە'])
if 'warranty' not in st.session_state:
    st.session_state.warranty = pd.DataFrame(columns=['ناوی کڕیار', 'ژمارەی IMEI', 'بەرواری کۆتایی گەرەنتی', 'جۆری مۆبایل'])
if 'customers' not in st.session_state:
    st.session_state.customers = pd.DataFrame(columns=['ناوی کڕیار', 'ژمارەی مۆبایل', 'ئیمەیڵ', 'ناونیشان', 'بەرواری زیادکردن', 'کۆی کڕین', 'خاڵەکان', 'ئاست'])
if 'discounts' not in st.session_state:
    st.session_state.discounts = pd.DataFrame(columns=['کۆدی داشکاندن', 'ڕێژە', 'بەرواری دەستپێک', 'بەرواری کۆتایی', 'کەمترین کڕین', 'ژمارەی بەکارهێنان'])
if 'employees' not in st.session_state:
    st.session_state.employees = pd.DataFrame(columns=['ناوی کارمەند', 'پلە', 'مووچە', 'بەرواری دەستبەکاربوون', 'ژمارەی فرۆشتن', 'کۆی فرۆشتن', 'پاداشت'])
if 'repairs' not in st.session_state:
    st.session_state.repairs = pd.DataFrame(columns=['ID', 'ناوی کڕیار', 'جۆری مۆبایل', 'کێشە', 'بەرواری وەرگرتن', 'بەرواری گەڕاندنەوە', 'نرخی چاککردنەوە', 'ڕەوش'])
if 'loyalty_points' not in st.session_state:
    st.session_state.loyalty_points = {}
if 'last_sale_invoice' not in st.session_state:
    st.session_state.last_sale_invoice = None
if 'show_invoice' not in st.session_state:
    st.session_state.show_invoice = False

# ================== HELPER FUNCTIONS ==================
def add_sale(product_name, price, customer_name, discount_code="", employee=""):
    final_price = apply_discount(price, discount_code)
    
    new_sale = pd.DataFrame({
        'ناوی بەرهەم': [product_name],
        'نرخ': [float(price)],
        'کاتی فرۆشتن': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        'ناوی کڕیار': [customer_name],
        'کۆدی داشکاندن': [discount_code],
        'نرخی کۆتایی': [final_price],
        'کارمەند': [employee]
    })
    st.session_state.sales = pd.concat([st.session_state.sales, new_sale], ignore_index=True)
    
    # زیادکردنی خاڵەکان
    add_loyalty_points(customer_name, final_price)
    
    # نوێکردنەوەی ئاستی کارمەند
    if employee:
        update_employee_performance(employee, final_price)
    
    # دروستکردنی فاکتوور
    sale_data = {
        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'customer': customer_name,
        'product': product_name,
        'price': price,
        'final_price': final_price
    }
    st.session_state.last_sale_invoice = generate_invoice(sale_data)
    st.session_state.show_invoice = True
    
    return True

def apply_discount(price, discount_code):
    if discount_code and not st.session_state.discounts.empty:
        discount = st.session_state.discounts[st.session_state.discounts['کۆدی داشکاندن'] == discount_code]
        if not discount.empty:
            rate = discount['ڕێژە'].iloc[0]
            return price * (1 - rate / 100)
    return price

def add_loyalty_points(customer_name, sale_amount):
    points = int(sale_amount / 10)
    if customer_name in st.session_state.loyalty_points:
        st.session_state.loyalty_points[customer_name] += points
    else:
        st.session_state.loyalty_points[customer_name] = points
    
    # نوێکردنەوەی ئاستی کڕیار
    total_points = st.session_state.loyalty_points[customer_name]
    if total_points >= 1000:
        level = "🏆 پلاتینیۆم"
    elif total_points >= 500:
        level = "🥇 زێڕین"
    elif total_points >= 200:
        level = "🥈 زیوین"
    else:
        level = "🥉 ئاسایی"
    
    # نوێکردنەوەی داتای کڕیار
    if customer_name in st.session_state.customers['ناوی کڕیار'].values:
        idx = st.session_state.customers[st.session_state.customers['ناوی کڕیار'] == customer_name].index[0]
        st.session_state.customers.at[idx, 'خاڵەکان'] = total_points
        st.session_state.customers.at[idx, 'ئاست'] = level
        st.session_state.customers.at[idx, 'کۆی کڕین'] += sale_amount

def update_employee_performance(employee, sale_amount):
    if employee in st.session_state.employees['ناوی کارمەند'].values:
        idx = st.session_state.employees[st.session_state.employees['ناوی کارمەند'] == employee].index[0]
        st.session_state.employees.at[idx, 'ژمارەی فرۆشتن'] += 1
        st.session_state.employees.at[idx, 'کۆی فرۆشتن'] += sale_amount
        st.session_state.employees.at[idx, 'پاداشت'] += sale_amount * 0.02

def generate_invoice(sale_data):
    try:
        pdf = FPDF()
        pdf.add_page()
        
        # هێدەر
        pdf.set_font("Arial", "B", 20)
        pdf.cell(0, 10, "Mobile Shop Invoice", ln=True, align="C")
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(10)
        
        # زانیاری فرۆشتن
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"Date: {sale_data.get('date', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}", ln=True)
        pdf.cell(0, 10, f"Customer: {sale_data.get('customer', 'N/A')}", ln=True)
        pdf.cell(0, 10, f"Product: {sale_data.get('product', 'N/A')}", ln=True)
        pdf.cell(0, 10, f"Original Price: ${sale_data.get('price', 0)}", ln=True)
        pdf.cell(0, 10, f"Final Price: ${sale_data.get('final_price', 0)}", ln=True)
        
        # QR Code
        qr = qrcode.make(f"Invoice: {datetime.now().strftime('%Y%m%d%H%M%S')}")
        qr.save("temp_qr.png")
        pdf.image("temp_qr.png", x=150, y=30, w=40)
        
        pdf.output("temp_invoice.pdf")
        with open("temp_invoice.pdf", "rb") as f:
            return f.read()
    except Exception as e:
        st.error(f"کێشەیەک ڕوویدا لە دروستکردنی فاکتوور: {e}")
        return None

def check_low_stock():
    if not st.session_state.inventory.empty:
        return st.session_state.inventory[st.session_state.inventory['ژمارەی دانەکان'] < st.session_state.inventory['کەمترین ژمارە']]
    return pd.DataFrame()

def check_expiring_warranty():
    if not st.session_state.warranty.empty:
        today = datetime.now().date()
        warranty_dates = pd.to_datetime(st.session_state.warranty['بەرواری کۆتایی گەرەنتی']).dt.date
        days_remaining = (warranty_dates - today).dt.days
        return st.session_state.warranty[(days_remaining <= 30) & (days_remaining >= 0)]
    return pd.DataFrame()

def export_to_excel(df, sheet_name):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    return output.getvalue()

def get_download_link(data, filename):
    b64 = base64.b64encode(data).decode()
    return f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}" style="text-decoration: none; color: #667eea;">📥 داگرتنی {filename}</a>'

# ================== SIDEBAR ==================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/shop.png", width=80)
    st.title("📱 مینوی سەرەکی")
    
    # ئاگادارییەکان
    st.markdown("---")
    st.markdown("### 🔔 ئاگادارییەکان")
    
    low_stock_items = check_low_stock()
    if not low_stock_items.empty:
        with st.expander(f"⚠️ {len(low_stock_items)} کەلوپەلی کەم!", expanded=True):
            for _, item in low_stock_items.iterrows():
                st.error(f"📦 {item['ناوی کەلوپەل']}: {item['ژمارەی دانەکان']} دانە")
    
    expiring_warranties = check_expiring_warranty()
    if not expiring_warranties.empty:
        with st.expander(f"⏰ {len(expiring_warranties)} گەرەنتی نزیک!", expanded=True):
            for _, warranty in expiring_warranties.iterrows():
                st.warning(f"📱 {warranty['ناوی کڕیار']} - {warranty['جۆری مۆبایل']}")
    
    st.markdown("---")
    
    # مینوی سەرەکی
    menu_options = {
        "💰 تۆمارکردنی فرۆشتن": ["📝 فرۆشتنی نوێ", "📋 لیستی فرۆشتنەکان", "🧾 فاکتوور"],
        "📦 کۆگای کەلوپەل": ["📝 زیادکردنی کەلوپەل", "📋 لیستی کۆگا", "🔄 بەڕێوەبردنی کۆگا"],
        "🛡️ گەرەنتی": ["📝 تۆمارکردنی گەرەنتی", "📋 لیستی گەرەنتی", "⚠️ ئاگادارییەکان"],
        "📊 قازانج": ["💰 خەمڵاندنی قازانج", "📈 هێڵکاری", "📋 ڕاپۆرت"],
        "👥 کڕیاران": ["📝 زیادکردنی کڕیار", "📋 لیستی کڕیاران", "⭐ بەرنامەی خاڵ"],
        "🏷️ داشکاندن": ["📝 داشکاندنی نوێ", "📋 لیستی داشکاندنەکان"],
        "👨‍💼 کارمەندان": ["📝 زیادکردنی کارمەند", "📋 لیستی کارمەندان", "📊 ئاستی کارمەندان"],
        "🔧 چاککردنەوە": ["📝 تۆمارکردنی چاککردنەوە", "📋 لیستی چاککردنەوەکان"],
        "📊 داشبۆرد": ["🎯 داشبۆردی سەرەکی"]
    }
    
    main_choice = st.selectbox("بەشێک هەڵبژێرە:", list(menu_options.keys()))
    
    if main_choice in menu_options:
        sub_choice = st.radio("ژێربەش:", menu_options[main_choice])
    
    st.markdown("---")
    
    # کورتەی گشتی
    st.markdown("### 📊 کورتەی گشتی")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("کۆی فرۆشتنەکان", f"{len(st.session_state.sales)}")
    with col2:
        st.metric("کڕیارەکان", f"{len(st.session_state.customers)}")
    
    total_sales = st.session_state.sales['نرخی کۆتایی'].sum() if not st.session_state.sales.empty else 0
    total_cost = (st.session_state.inventory['نرخی کڕین'] * st.session_state.inventory['ژمارەی دانەکان']).sum() if not st.session_state.inventory.empty else 0
    profit = total_sales - total_cost
    
    st.metric("قازانجی پوخت", f"${profit:,.0f}", delta=f"{'+' if profit > 0 else ''}{profit:,.0f}")

# ================== MAIN CONTENT ==================
st.markdown('<p class="main-header">📱 سیستەمی بەڕێوەبردنی دوکانی مۆبایل</p>', unsafe_allow_html=True)

# ================== 1. SALES SECTION ==================
if main_choice == "💰 تۆمارکردنی فرۆشتن":
    if sub_choice == "📝 فرۆشتنی نوێ":
        st.header("📝 تۆمارکردنی فرۆشتنی نوێ")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # لێرەدا فۆرم بەکاردەهێنین بەڵام download_button لە دەرەوەی فۆرم دادەنێین
            with st.form("advanced_sale_form"):
                product_name = st.text_input("📱 ناوی بەرهەم", placeholder="بۆ نموونە: iPhone 15 Pro")
                
                col_price, col_customer = st.columns(2)
                with col_price:
                    original_price = st.number_input("💵 نرخی بنەڕەتی ($)", min_value=0.0, step=10.0)
                with col_customer:
                    customer_name = st.text_input("👤 ناوی کڕیار", placeholder="ناوی کڕیار")
                
                col_discount, col_employee = st.columns(2)
                with col_discount:
                    discount_code = st.text_input("🏷️ کۆدی داشکاندن (ئارەزوومەندانە)")
                    if discount_code:
                        final_price = apply_discount(original_price, discount_code)
                        if final_price != original_price:
                            st.success(f"💰 نرخی کۆتایی: ${final_price:,.2f}")
                        else:
                            st.warning("کۆدی داشکاندن دروست نییە")
                    else:
                        final_price = original_price
                
                with col_employee:
                    if not st.session_state.employees.empty:
                        employee = st.selectbox("👨‍💼 کارمەند", [""] + list(st.session_state.employees['ناوی کارمەند']))
                    else:
                        employee = ""
                        st.info("هیچ کارمەندێک تۆمار نەکراوە")
                
                submitted = st.form_submit_button("➕ تۆمارکردنی فرۆشتن", use_container_width=True)
            
            # لە دەرەوەی فۆرم، دوای پێشکەشکردن
            if submitted:
                if product_name and original_price > 0 and customer_name:
                    if add_sale(product_name, original_price, customer_name, discount_code, employee):
                        st.success(f"✅ فرۆشتنی {product_name} بە نرخی ${final_price:,.2f} بۆ {customer_name} تۆمار کرا!")
                        st.balloons()
                        
                        # پیشاندانی دوگمەی داگرتنی فاکتوور لە دەرەوەی فۆرم
                        if st.session_state.last_sale_invoice:
                            st.download_button(
                                label="📄 داگرتنی فاکتوور (PDF)",
                                data=st.session_state.last_sale_invoice,
                                file_name="invoice.pdf",
                                mime="application/pdf",
                                key="download_invoice_new"
                            )
                else:
                    st.error("⚠️ تکایە هەموو خانە پێویستەکان پڕ بکەرەوە!")
        
        with col2:
            st.subheader("📈 دوایین فرۆشتنەکان")
            if not st.session_state.sales.empty:
                recent_sales = st.session_state.sales.tail(5)[['ناوی بەرهەم', 'نرخی کۆتایی', 'ناوی کڕیار']]
                st.dataframe(recent_sales, use_container_width=True)
                
                # هێڵکاری
                fig = px.histogram(st.session_state.sales.tail(20), x='نرخی کۆتایی', 
                                 title="دابەشبوونی نرخی فرۆشتن")
                st.plotly_chart(fig, use_container_width=True)
    
    elif sub_choice == "📋 لیستی فرۆشتنەکان":
        st.header("📋 لیستی فرۆشتنەکان")
        
        if not st.session_state.sales.empty:
            # فلتەرەکان
            col_f1, col_f2, col_f3 = st.columns(3)
            with col_f1:
                date_filter = st.date_input("📅 فلتەر بەپێی بەروار", value=None)
            with col_f2:
                if not st.session_state.sales.empty:
                    product_filter = st.multiselect("📱 بەرهەم", st.session_state.sales['ناوی بەرهەم'].unique())
            with col_f3:
                customer_filter = st.text_input("👤 گەڕان بە ناوی کڕیار")
            
            filtered = st.session_state.sales.copy()
            if date_filter:
                filtered['date'] = pd.to_datetime(filtered['کاتی فرۆشتن']).dt.date
                filtered = filtered[filtered['date'] == date_filter]
            if product_filter:
                filtered = filtered[filtered['ناوی بەرهەم'].isin(product_filter)]
            if customer_filter:
                filtered = filtered[filtered['ناوی کڕیار'].str.contains(customer_filter, case=False)]
            
            st.dataframe(filtered, use_container_width=True)
            
            # ئامارەکان
            col_s1, col_s2, col_s3 = st.columns(3)
            with col_s1:
                st.metric("ژمارەی فرۆشتن", f"{len(filtered)}")
            with col_s2:
                st.metric("کۆی داهات", f"${filtered['نرخی کۆتایی'].sum():,.2f}")
            with col_s3:
                avg = filtered['نرخی کۆتایی'].mean() if not filtered.empty else 0
                st.metric("تێکڕای نرخ", f"${avg:,.2f}")
            
            if st.button("📥 هەناردەکردن بۆ Excel"):
                excel_data = export_to_excel(filtered, 'Sales')
                st.markdown(get_download_link(excel_data, 'sales_data.xlsx'), unsafe_allow_html=True)
        else:
            st.info("👈 تا ئێستا هیچ فرۆشتنێک تۆمار نەکراوە.")
    
    elif sub_choice == "🧾 فاکتوور":
        st.header("🧾 بەڕێوەبردنی فاکتوورەکان")
        
        if not st.session_state.sales.empty:
            sale_to_invoice = st.selectbox("فرۆشتن هەڵبژێرە بۆ فاکتوور", 
                                          range(len(st.session_state.sales)),
                                          format_func=lambda x: f"{st.session_state.sales.iloc[x]['ناوی بەرهەم']} - {st.session_state.sales.iloc[x]['ناوی کڕیار']}")
            
            if st.button("🧾 دروستکردنی فاکتوور"):
                sale = st.session_state.sales.iloc[sale_to_invoice]
                sale_data = {
                    'date': sale['کاتی فرۆشتن'],
                    'customer': sale['ناوی کڕیار'],
                    'product': sale['ناوی بەرهەم'],
                    'price': sale['نرخ'],
                    'final_price': sale['نرخی کۆتایی']
                }
                invoice_data = generate_invoice(sale_data)
                if invoice_data:
                    st.download_button(
                        label="📄 داگرتنی فاکتوور",
                        data=invoice_data,
                        file_name="invoice.pdf",
                        mime="application/pdf",
                        key="download_invoice_manual"
                    )
        else:
            st.info("هیچ فرۆشتنێک نییە بۆ دروستکردنی فاکتوور")

# ================== 2. INVENTORY SECTION ==================
elif main_choice == "📦 کۆگای کەلوپەل":
    if sub_choice == "📝 زیادکردنی کەلوپەل":
        st.header("📝 زیادکردنی کەلوپەلی نوێ")
        
        with st.form("advanced_inventory_form"):
            item_name = st.text_input("🏷️ ناوی کەلوپەل")
            
            col1, col2 = st.columns(2)
            with col1:
                stock = st.number_input("📦 ژمارەی دانەکان", min_value=1, step=1)
            with col2:
                purchase_price = st.number_input("💰 نرخی کڕین ($)", min_value=0.0, step=1.0)
            
            min_stock = st.number_input("⚠️ ئاستی ئاگادارکردنەوە", min_value=1, value=5,
                                       help="کاتێک ژمارەکە کەمتر بوو لەم ڕێژەیە، ئاگاداریت دەکەینەوە")
            
            if st.form_submit_button("➕ زیادکردنی کەلوپەل"):
                if item_name and stock > 0 and purchase_price > 0:
                    new_item = pd.DataFrame({
                        'ناوی کەلوپەل': [item_name],
                        'ژمارەی دانەکان': [int(stock)],
                        'نرخی کڕین': [float(purchase_price)],
                        'بەرواری زیادکردن': [datetime.now().strftime("%Y-%m-%d")],
                        'کەمترین ژمارە': [min_stock]
                    })
                    st.session_state.inventory = pd.concat([st.session_state.inventory, new_item], ignore_index=True)
                    st.success(f"✅ {stock} دانە {item_name} زیاد کرا!")
                else:
                    st.error("⚠️ تکایە هەموو خانەکان پڕ بکەرەوە!")
    
    elif sub_choice == "📋 لیستی کۆگا":
        st.header("📋 لیستی کەلوپەلەکان")
        
        if not st.session_state.inventory.empty:
            inventory_display = st.session_state.inventory.copy()
            inventory_display['کۆی بەها'] = inventory_display['ژمارەی دانەکان'] * inventory_display['نرخی کڕین']
            inventory_display['ڕەوش'] = inventory_display.apply(
                lambda x: '🔴 کەم' if x['ژمارەی دانەکان'] < x['کەمترین ژمارە'] else '🟢 باش', axis=1
            )
            
            # فلتەر
            status_filter = st.multiselect("فلتەر بەپێی ڕەوش", ['باش', 'کەم'])
            if status_filter:
                if 'کەم' in status_filter and 'باش' not in status_filter:
                    inventory_display = inventory_display[inventory_display['ڕەوش'] == '🔴 کەم']
                elif 'باش' in status_filter and 'کەم' not in status_filter:
                    inventory_display = inventory_display[inventory_display['ڕەوش'] == '🟢 باش']
            
            st.dataframe(inventory_display, use_container_width=True)
            
            col_s1, col_s2, col_s3 = st.columns(3)
            with col_s1:
                st.metric("کۆی جۆرەکان", f"{len(inventory_display)}")
            with col_s2:
                st.metric("کۆی دانەکان", f"{inventory_display['ژمارەی دانەکان'].sum():,}")
            with col_s3:
                st.metric("کۆی بەها", f"${inventory_display['کۆی بەها'].sum():,.2f}")
            
            # هێڵکاری
            fig = px.pie(inventory_display, values='کۆی بەها', names='ناوی کەلوپەل', 
                        title="دابەشبوونی بەهای کۆگا")
            st.plotly_chart(fig, use_container_width=True)
            
            if st.button("📥 هەناردەکردن بۆ Excel"):
                excel_data = export_to_excel(inventory_display, 'Inventory')
                st.markdown(get_download_link(excel_data, 'inventory.xlsx'), unsafe_allow_html=True)
        else:
            st.info("کۆگا بەتاڵە")
    
    elif sub_choice == "🔄 بەڕێوەبردنی کۆگا":
        st.header("🔄 بەڕێوەبردنی کۆگا")
        
        if not st.session_state.inventory.empty:
            item_to_update = st.selectbox("کەلوپەل هەڵبژێرە", 
                                         st.session_state.inventory['ناوی کەلوپەل'])
            
            current_item = st.session_state.inventory[st.session_state.inventory['ناوی کەلوپەل'] == item_to_update].iloc[0]
            
            st.info(f"ژمارەی ئێستا: {current_item['ژمارەی دانەکان']} | نرخی کڕین: ${current_item['نرخی کڕین']}")
            
            col1, col2 = st.columns(2)
            with col1:
                stock_change = st.number_input("گۆڕانکاری لە ژمارەدا (+/-)", value=0, step=1)
            with col2:
                new_price = st.number_input("نرخی نوێ (0 = بێ گۆڕانکاری)", value=0.0, step=1.0)
            
            if st.button("🔄 نوێکردنەوە"):
                idx = st.session_state.inventory[st.session_state.inventory['ناوی کەلوپەل'] == item_to_update].index[0]
                
                if stock_change != 0:
                    new_stock = current_item['ژمارەی دانەکان'] + stock_change
                    if new_stock >= 0:
                        st.session_state.inventory.at[idx, 'ژمارەی دانەکان'] = new_stock
                    else:
                        st.error("ژمارە ناتوانێت سالب بێت!")
                        st.stop()
                
                if new_price > 0:
                    st.session_state.inventory.at[idx, 'نرخی کڕین'] = new_price
                
                st.success("✅ کۆگا بە سەرکەوتوویی نوێ کرایەوە!")
                st.rerun()
        else:
            st.info("کۆگا بەتاڵە")

# ================== 3. WARRANTY SECTION ==================
elif main_choice == "🛡️ گەرەنتی":
    if sub_choice == "📝 تۆمارکردنی گەرەنتی":
        st.header("📝 تۆمارکردنی گەرەنتی نوێ")
        
        with st.form("advanced_warranty_form"):
            customer_name = st.text_input("👤 ناوی کڕیار")
            
            col1, col2 = st.columns(2)
            with col1:
                imei = st.text_input("📱 ژمارەی IMEI (15 ژمارە)")
            with col2:
                device_model = st.text_input("📱 جۆری مۆبایل")
            
            warranty_end = st.date_input("📅 بەرواری کۆتایی گەرەنتی", 
                                        min_value=datetime.now().date())
            
            if st.form_submit_button("➕ تۆمارکردن"):
                if customer_name and imei and len(imei) == 15 and imei.isdigit():
                    new_warranty = pd.DataFrame({
                        'ناوی کڕیار': [customer_name],
                        'ژمارەی IMEI': [imei],
                        'بەرواری کۆتایی گەرەنتی': [warranty_end.strftime("%Y-%m-%d")],
                        'جۆری مۆبایل': [device_model]
                    })
                    st.session_state.warranty = pd.concat([st.session_state.warranty, new_warranty], ignore_index=True)
                    st.success(f"✅ گەرەنتی بۆ {customer_name} تۆمار کرا!")
                else:
                    st.error("⚠️ تکایە زانیارییەکان بە دروستی پڕ بکەرەوە!")
    
    elif sub_choice == "📋 لیستی گەرەنتی":
        st.header("📋 لیستی گەرەنتییەکان")
        
        if not st.session_state.warranty.empty:
            warranty_display = st.session_state.warranty.copy()
            warranty_display['بەرواری کۆتایی'] = pd.to_datetime(warranty_display['بەرواری کۆتایی گەرەنتی'])
            today = datetime.now()
            warranty_display['ڕۆژی ماوە'] = (warranty_display['بەرواری کۆتایی'] - today).dt.days
            
            def get_status(days):
                if days < 0:
                    return '🔴 بەسەرچوو'
                elif days <= 7:
                    return '🔴 زۆر نزیک'
                elif days <= 30:
                    return '🟡 نزیک'
                else:
                    return '🟢 چالاک'
            
            warranty_display['ڕەوش'] = warranty_display['ڕۆژی ماوە'].apply(get_status)
            
            status_filter = st.multiselect("فلتەر بەپێی ڕەوش", 
                                          ['چالاک', 'نزیک', 'زۆر نزیک', 'بەسەرچوو'])
            if status_filter:
                warranty_display = warranty_display[warranty_display['ڕەوش'].str.contains('|'.join(status_filter))]
            
            st.dataframe(warranty_display, use_container_width=True)
            
            # ئامار
            active = len(warranty_display[warranty_display['ڕۆژی ماوە'] > 0])
            expired = len(warranty_display[warranty_display['ڕۆژی ماوە'] < 0])
            
            col_s1, col_s2, col_s3 = st.columns(3)
            with col_s1:
                st.metric("کۆی گشتی", f"{len(warranty_display)}")
            with col_s2:
                st.metric("چالاک", f"{active}")
            with col_s3:
                st.metric("بەسەرچوو", f"{expired}")
            
            if st.button("📥 هەناردەکردن بۆ Excel"):
                excel_data = export_to_excel(warranty_display, 'Warranty')
                st.markdown(get_download_link(excel_data, 'warranty.xlsx'), unsafe_allow_html=True)
        else:
            st.info("هیچ گەرەنتییەک تۆمار نەکراوە")
    
    elif sub_choice == "⚠️ ئاگادارییەکان":
        st.header("⚠️ ئاگادارییەکانی گەرەنتی")
        
        expiring = check_expiring_warranty()
        if not expiring.empty:
            st.warning(f"⚠️ {len(expiring)} گەرەنتی لە ماوەی 30 ڕۆژدا بەسەردەچێت!")
            
            for _, warranty in expiring.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class="customer-card">
                        <h4>📱 {warranty['جۆری مۆبایل']}</h4>
                        <p>👤 کڕیار: {warranty['ناوی کڕیار']}</p>
                        <p>📅 بەرواری کۆتایی: {warranty['بەرواری کۆتایی گەرەنتی']}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.success("✅ هیچ گەرەنتییەکی نزیک نییە!")

# ================== 4. PROFIT SECTION ==================
elif main_choice == "📊 قازانج":
    total_sales = st.session_state.sales['نرخی کۆتایی'].sum() if not st.session_state.sales.empty else 0
    total_cost = (st.session_state.inventory['نرخی کڕین'] * st.session_state.inventory['ژمارەی دانەکان']).sum() if not st.session_state.inventory.empty else 0
    profit = total_sales - total_cost
    profit_margin = (profit / total_sales * 100) if total_sales > 0 else 0
    
    if sub_choice == "💰 خەمڵاندنی قازانج":
        st.header("💰 خەمڵاندنی قازانج")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("کۆی فرۆشتن", f"${total_sales:,.2f}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("تێچووی کەلوپەل", f"${total_cost:,.2f}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("قازانجی پوخت", f"${profit:,.2f}", delta=f"{profit_margin:.1f}%")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            sales_count = len(st.session_state.sales)
            avg_sale = total_sales / sales_count if sales_count > 0 else 0
            st.metric("تێکڕای فرۆشتن", f"${avg_sale:,.2f}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # ڕێنمایی
        if profit_margin > 30:
            st.success("🎉 زۆر باشە! ڕێژەی قازانجت بەرزە.")
        elif profit_margin > 15:
            st.info("👍 باشە. بەردەوام بە!")
        elif profit_margin > 0:
            st.warning("⚠️ قازانجت کەمە. پێویستە تێچووەکان کەم بکەیتەوە.")
        else:
            st.error("❌ زیانە! پێویستە بە پەلە ڕێکار بگریت.")
    
    elif sub_choice == "📈 هێڵکاری":
        st.header("📈 هێڵکاری قازانج")
        
        if total_sales > 0 or total_cost > 0:
            fig = go.Figure(data=[
                go.Bar(name='کۆی فرۆشتن', x=['دارایی'], y=[total_sales], marker_color='#2ecc71'),
                go.Bar(name='تێچوو', x=['دارایی'], y=[total_cost], marker_color='#e74c3c'),
                go.Bar(name='قازانج', x=['دارایی'], y=[profit], marker_color='#3498db')
            ])
            fig.update_layout(barmode='group', height=500)
            st.plotly_chart(fig, use_container_width=True)
            
            # فرۆشتن بەپێی بەرهەم
            if not st.session_state.sales.empty:
                sales_by_product = st.session_state.sales.groupby('ناوی بەرهەم')['نرخی کۆتایی'].sum()
                fig2 = px.pie(values=sales_by_product.values, names=sales_by_product.index, 
                             title="فرۆشتن بەپێی بەرهەم")
                st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("داتا بەردەست نییە")
    
    elif sub_choice == "📋 ڕاپۆرت":
        st.header("📋 ڕاپۆرتی قازانج")
        
        # ڕاپۆرتی مانگانە
        if not st.session_state.sales.empty:
            sales_copy = st.session_state.sales.copy()
            sales_copy['مانگ'] = pd.to_datetime(sales_copy['کاتی فرۆشتن']).dt.to_period('M')
            monthly_sales = sales_copy.groupby('مانگ')['نرخی کۆتایی'].sum()
            
            st.subheader("📅 فرۆشتنی مانگانە")
            st.dataframe(monthly_sales)
            
            # باشترین بەرهەمەکان
            st.subheader("🏆 باشترین 5 بەرهەم")
            top_products = sales_copy.groupby('ناوی بەرهەم').agg({
                'نرخی کۆتایی': 'sum',
                'ناوی کڕیار': 'count'
            }).rename(columns={'ناوی کڕیار': 'ژمارەی فرۆشتن'}).nlargest(5, 'نرخی کۆتایی')
            st.dataframe(top_products)
            
            if st.button("📥 داگرتنی ڕاپۆرتی تەواو"):
                excel_data = export_to_excel(sales_copy, 'Full Report')
                st.markdown(get_download_link(excel_data, 'full_report.xlsx'), unsafe_allow_html=True)
        else:
            st.info("داتای فرۆشتن بەردەست نییە")

# ================== 5. CUSTOMERS SECTION ==================
elif main_choice == "👥 کڕیاران":
    if sub_choice == "📝 زیادکردنی کڕیار":
        st.header("📝 زیادکردنی کڕیاری نوێ")
        
        with st.form("customer_form"):
            name = st.text_input("👤 ناوی کڕیار")
            
            col1, col2 = st.columns(2)
            with col1:
                phone = st.text_input("📞 ژمارەی مۆبایل")
            with col2:
                email = st.text_input("📧 ئیمەیڵ")
            
            address = st.text_area("📍 ناونیشان")
            
            if st.form_submit_button("➕ زیادکردن"):
                if name:
                    new_customer = pd.DataFrame({
                        'ناوی کڕیار': [name],
                        'ژمارەی مۆبایل': [phone],
                        'ئیمەیڵ': [email],
                        'ناونیشان': [address],
                        'بەرواری زیادکردن': [datetime.now().strftime("%Y-%m-%d")],
                        'کۆی کڕین': [0],
                        'خاڵەکان': [0],
                        'ئاست': ['🥉 ئاسایی']
                    })
                    st.session_state.customers = pd.concat([st.session_state.customers, new_customer], ignore_index=True)
                    st.success(f"✅ کڕیاری {name} زیاد کرا!")
                else:
                    st.error("⚠️ ناوی کڕیار پێویستە!")
    
    elif sub_choice == "📋 لیستی کڕیاران":
        st.header("📋 لیستی کڕیاران")
        
        if not st.session_state.customers.empty:
            search = st.text_input("🔍 گەڕان بە ناو")
            
            display_customers = st.session_state.customers.copy()
            if search:
                display_customers = display_customers[display_customers['ناوی کڕیار'].str.contains(search, case=False)]
            
            st.dataframe(display_customers, use_container_width=True)
            
            # هێڵکاری ئاستی کڕیاران
            level_counts = display_customers['ئاست'].value_counts()
            fig = px.pie(values=level_counts.values, names=level_counts.index, 
                        title="ئاستی کڕیاران")
            st.plotly_chart(fig, use_container_width=True)
            
            if st.button("📥 هەناردەکردن بۆ Excel"):
                excel_data = export_to_excel(display_customers, 'Customers')
                st.markdown(get_download_link(excel_data, 'customers.xlsx'), unsafe_allow_html=True)
        else:
            st.info("هیچ کڕیارێک تۆمار نەکراوە")
    
    elif sub_choice == "⭐ بەرنامەی خاڵ":
        st.header("⭐ بەرنامەی خاڵ و ڕێوڕەسمی بەخشین")
        
        if st.session_state.loyalty_points:
            points_df = pd.DataFrame(list(st.session_state.loyalty_points.items()), 
                                    columns=['ناوی کڕیار', 'خاڵەکان'])
            points_df['ئاست'] = points_df['خاڵەکان'].apply(
                lambda x: '🏆 پلاتینیۆم' if x >= 1000 else ('🥇 زێڕین' if x >= 500 else ('🥈 زیوین' if x >= 200 else '🥉 ئاسایی'))
            )
            
            st.dataframe(points_df, use_container_width=True)
            
            # بەکارهێنانی خاڵەکان
            st.subheader("💱 بەکارهێنانی خاڵەکان")
            customer = st.selectbox("کڕیار هەڵبژێرە", points_df['ناوی کڕیار'])
            points_to_use = st.number_input("ژمارەی خاڵەکان", min_value=0, max_value=int(points_df[points_df['ناوی کڕیار'] == customer]['خاڵەکان'].iloc[0]))
            
            discount_value = points_to_use * 0.5
            st.info(f"💵 بەهای داشکاندن: ${discount_value:.2f}")
            
            if st.button("💱 بەکارهێنان"):
                st.success(f"✅ {points_to_use} خاڵ بەکارهات. داشکاندنی ${discount_value:.2f}!")
        else:
            st.info("هیچ خاڵێک تۆمار نەکراوە")

# ================== 6. DISCOUNTS SECTION ==================
elif main_choice == "🏷️ داشکاندن":
    if sub_choice == "📝 داشکاندنی نوێ":
        st.header("📝 دروستکردنی داشکاندنی نوێ")
        
        with st.form("discount_form"):
            code = st.text_input("🏷️ کۆدی داشکاندن")
            rate = st.slider("ڕێژەی داشکاندن (%)", 1, 50, 10)
            
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("بەرواری دەستپێک")
            with col2:
                end_date = st.date_input("بەرواری کۆتایی")
            
            min_purchase = st.number_input("کەمترین بڕی کڕین ($)", min_value=0.0, value=0.0)
            
            if st.form_submit_button("➕ دروستکردن"):
                if code:
                    new_discount = pd.DataFrame({
                        'کۆدی داشکاندن': [code],
                        'ڕێژە': [rate],
                        'بەرواری دەستپێک': [start_date.strftime("%Y-%m-%d")],
                        'بەرواری کۆتایی': [end_date.strftime("%Y-%m-%d")],
                        'کەمترین کڕین': [min_purchase],
                        'ژمارەی بەکارهێنان': [0]
                    })
                    st.session_state.discounts = pd.concat([st.session_state.discounts, new_discount], ignore_index=True)
                    st.success(f"✅ داشکاندنی {code} دروست کرا!")
                else:
                    st.error("کۆدی داشکاندن پێویستە!")
    
    elif sub_choice == "📋 لیستی داشکاندنەکان":
        st.header("📋 داشکاندنە چالاکەکان")
        
        if not st.session_state.discounts.empty:
            st.dataframe(st.session_state.discounts, use_container_width=True)
            
            # هێڵکاری
            fig = px.bar(st.session_state.discounts, x='کۆدی داشکاندن', y='ڕێژە',
                        title="ڕێژەی داشکاندنەکان")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("هیچ داشکاندنێک دروست نەکراوە")

# ================== 7. EMPLOYEES SECTION ==================
elif main_choice == "👨‍💼 کارمەندان":
    if sub_choice == "📝 زیادکردنی کارمەند":
        st.header("📝 زیادکردنی کارمەندی نوێ")
        
        with st.form("employee_form"):
            name = st.text_input("👨‍💼 ناوی کارمەند")
            
            col1, col2 = st.columns(2)
            with col1:
                position = st.text_input("💼 پلە")
            with col2:
                salary = st.number_input("💰 مووچە ($)", min_value=0.0, step=100.0)
            
            start_date = st.date_input("📅 بەرواری دەستبەکاربوون")
            
            if st.form_submit_button("➕ زیادکردن"):
                if name:
                    new_employee = pd.DataFrame({
                        'ناوی کارمەند': [name],
                        'پلە': [position],
                        'مووچە': [salary],
                        'بەرواری دەستبەکاربوون': [start_date.strftime("%Y-%m-%d")],
                        'ژمارەی فرۆشتن': [0],
                        'کۆی فرۆشتن': [0.0],
                        'پاداشت': [0.0]
                    })
                    st.session_state.employees = pd.concat([st.session_state.employees, new_employee], ignore_index=True)
                    st.success(f"✅ کارمەندی {name} زیاد کرا!")
                else:
                    st.error("ناوی کارمەند پێویستە!")
    
    elif sub_choice == "📋 لیستی کارمەندان":
        st.header("📋 لیستی کارمەندان")
        
        if not st.session_state.employees.empty:
            st.dataframe(st.session_state.employees, use_container_width=True)
            
            # هێڵکاری
            fig = px.bar(st.session_state.employees, x='ناوی کارمەند', y='کۆی فرۆشتن',
                        title="کۆی فرۆشتنی کارمەندان", color='پاداشت')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("هیچ کارمەندێک تۆمار نەکراوە")
    
    elif sub_choice == "📊 ئاستی کارمەندان":
        st.header("📊 هەڵسەنگاندنی ئاستی کارمەندان")
        
        if not st.session_state.employees.empty:
            best_employee = st.session_state.employees.nlargest(1, 'کۆی فرۆشتن').iloc[0]
            st.success(f"🏆 باشترین کارمەند: {best_employee['ناوی کارمەند']} - ${best_employee['کۆی فرۆشتن']:,.2f}")
            
            # پێشبینی پاداشت
            for _, emp in st.session_state.employees.iterrows():
                with st.expander(f"👨‍💼 {emp['ناوی کارمەند']} - {emp['پلە']}"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("فرۆشتن", f"{emp['ژمارەی فرۆشتن']}")
                    with col2:
                        st.metric("کۆی فرۆشتن", f"${emp['کۆی فرۆشتن']:,.2f}")
                    with col3:
                        st.metric("پاداشت", f"${emp['پاداشت']:,.2f}")
        else:
            st.info("هیچ کارمەندێک تۆمار نەکراوە")

# ================== 8. REPAIRS SECTION ==================
elif main_choice == "🔧 چاککردنەوە":
    if sub_choice == "📝 تۆمارکردنی چاککردنەوە":
        st.header("📝 تۆمارکردنی چاککردنەوەی نوێ")
        
        with st.form("repair_form"):
            customer = st.text_input("👤 ناوی کڕیار")
            device = st.text_input("📱 جۆری مۆبایل")
            issue = st.text_area("🔧 کێشەکە")
            
            col1, col2 = st.columns(2)
            with col1:
                received_date = st.date_input("📅 بەرواری وەرگرتن")
            with col2:
                price = st.number_input("💰 نرخی چاککردنەوە ($)", min_value=0.0)
            
            status = st.selectbox("📊 ڕەوش", ["چاوەڕوان", "لەژێر کاردایە", "ئامادەیە", "گەڕێندراوەتەوە"])
            
            if st.form_submit_button("➕ تۆمارکردن"):
                if customer and device:
                    repair_id = f"REP{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    new_repair = pd.DataFrame({
                        'ID': [repair_id],
                        'ناوی کڕیار': [customer],
                        'جۆری مۆبایل': [device],
                        'کێشە': [issue],
                        'بەرواری وەرگرتن': [received_date.strftime("%Y-%m-%d")],
                        'بەرواری گەڕاندنەوە': [''],
                        'نرخی چاککردنەوە': [price],
                        'ڕەوش': [status]
                    })
                    st.session_state.repairs = pd.concat([st.session_state.repairs, new_repair], ignore_index=True)
                    st.success(f"✅ چاککردنەوە بە ID: {repair_id} تۆمار کرا!")
                else:
                    st.error("تکایە زانیارییە پێویستەکان پڕ بکەرەوە!")
    
    elif sub_choice == "📋 لیستی چاککردنەوەکان":
        st.header("📋 لیستی چاککردنەوەکان")
        
        if not st.session_state.repairs.empty:
            status_filter = st.multiselect("فلتەر بەپێی ڕەوش", 
                                          ["چاوەڕوان", "لەژێر کاردایە", "ئامادەیە", "گەڕێندراوەتەوە"])
            
            display_repairs = st.session_state.repairs.copy()
            if status_filter:
                display_repairs = display_repairs[display_repairs['ڕەوش'].isin(status_filter)]
            
            st.dataframe(display_repairs, use_container_width=True)
            
            # نوێکردنەوەی ڕەوش
            st.subheader("🔄 نوێکردنەوەی ڕەوش")
            repair_to_update = st.selectbox("چاککردنەوە هەڵبژێرە", display_repairs['ID'])
            new_status = st.selectbox("ڕەوشی نوێ", ["چاوەڕوان", "لەژێر کاردایە", "ئامادەیە", "گەڕێندراوەتەوە"])
            
            if st.button("🔄 نوێکردنەوە"):
                idx = st.session_state.repairs[st.session_state.repairs['ID'] == repair_to_update].index[0]
                st.session_state.repairs.at[idx, 'ڕەوش'] = new_status
                if new_status == "گەڕێندراوەتەوە":
                    st.session_state.repairs.at[idx, 'بەرواری گەڕاندنەوە'] = datetime.now().strftime("%Y-%m-%d")
                st.success("✅ ڕەوش نوێ کرایەوە!")
                st.rerun()
        else:
            st.info("هیچ چاککردنەوەیەک تۆمار نەکراوە")

# ================== 9. DASHBOARD ==================
elif main_choice == "📊 داشبۆرد":
    st.header("🎯 داشبۆردی سەرەکی")
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    today = datetime.now().date()
    today_sales = 0
    if not st.session_state.sales.empty:
        sales_today = st.session_state.sales.copy()
        sales_today['date'] = pd.to_datetime(sales_today['کاتی فرۆشتن']).dt.date
        today_sales = sales_today[sales_today['date'] == today]['نرخی کۆتایی'].sum()
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("💰 فرۆشتنی ئەمڕۆ", f"${today_sales:,.2f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        low_stock_count = len(check_low_stock())
        st.metric("📦 کەلوپەلی کەم", f"{low_stock_count}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        new_customers_today = 0
        if not st.session_state.customers.empty:
            customers_copy = st.session_state.customers.copy()
            customers_copy['date'] = pd.to_datetime(customers_copy['بەرواری زیادکردن']).dt.date
            new_customers_today = len(customers_copy[customers_copy['date'] == today])
        st.metric("👥 کڕیاری نوێی ئەمڕۆ", f"{new_customers_today}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        pending_repairs = 0
        if not st.session_state.repairs.empty:
            pending_repairs = len(st.session_state.repairs[st.session_state.repairs['ڕەوش'].isin(['چاوەڕوان', 'لەژێر کاردایە'])])
        st.metric("🔧 چاککردنەوەی چاوەڕوان", f"{pending_repairs}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # هێڵکارییەکان
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📈 ڕەوتی فرۆشتن (30 ڕۆژی ڕابردوو)")
        if not st.session_state.sales.empty:
            sales_30 = st.session_state.sales.copy()
            sales_30['date'] = pd.to_datetime(sales_30['کاتی فرۆشتن']).dt.date
            sales_30 = sales_30[sales_30['date'] >= today - timedelta(days=30)]
            daily_sales = sales_30.groupby('date')['نرخی کۆتایی'].sum()
            
            fig = px.line(x=daily_sales.index, y=daily_sales.values, 
                         labels={'x': 'بەروار', 'y': 'فرۆشتن ($)'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("داتا بەردەست نییە")
    
    with col_right:
        st.subheader("🏆 باشترین بەرهەمەکان")
        if not st.session_state.sales.empty:
            top_products = st.session_state.sales.groupby('ناوی بەرهەم')['نرخی کۆتایی'].sum().nlargest(5)
            fig = px.bar(x=top_products.index, y=top_products.values,
                        labels={'x': 'بەرهەم', 'y': 'کۆی فرۆشتن ($)'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("داتا بەردەست نییە")
    
    st.markdown("---")
    
    # دوایین چالاکییەکان
    st.subheader("📋 دوایین چالاکییەکان")
    
    if not st.session_state.sales.empty:
        st.write("**🛒 دوایین فرۆشتنەکان:**")
        st.dataframe(st.session_state.sales.tail(5)[['ناوی بەرهەم', 'نرخی کۆتایی', 'ناوی کڕیار', 'کاتی فرۆشتن']], 
                    use_container_width=True)
    
    if not st.session_state.repairs.empty:
        st.write("**🔧 چاککردنەوە چاوەڕوانەکان:**")
        pending = st.session_state.repairs[st.session_state.repairs['ڕەوش'].isin(['چاوەڕوان', 'لەژێر کاردایە'])]
        if not pending.empty:
            st.dataframe(pending[['ID', 'ناوی کڕیار', 'جۆری مۆبایل', 'ڕەوش']], use_container_width=True)

# ================== FOOTER ==================
st.markdown("---")
st.markdown("""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 15px;">
        <h3>📱 سیستەمی بەڕێوەبردنی دوکانی مۆبایل - وەشانی پڕۆ</h3>
        <p>هەموو مافێک پارێزراوە © 2024</p>
        <p>دروستکراوە بە ❤️ بۆ بەڕێوەبردنی باشتری دوکانەکەت</p>
    </div>
""", unsafe_allow_html=True)
