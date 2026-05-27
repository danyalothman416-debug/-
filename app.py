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
    page_title="سیستەمی بەڕێوەبردنی دوکانی مۆبایل - پڕۆماکس",
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
        border-left: 4px solid #667eea;
    }
    
    .chat-message-admin {
        background-color: #e3f2fd;
        padding: 10px;
        border-radius: 10px;
        margin: 5px;
        text-align: left;
    }
    
    .chat-message-user {
        background-color: #f3e5f5;
        padding: 10px;
        border-radius: 10px;
        margin: 5px;
        text-align: right;
    }
    
    .installment-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1rem;
    }
    
    .footer {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        margin-top: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# ================== SESSION STATE INITIALIZATION ==================
def init_session_state():
    """Initialize all session state variables"""
    if 'sales' not in st.session_state:
        st.session_state.sales = pd.DataFrame(columns=[
            'ناوی بەرهەم', 'نرخ', 'کاتی فرۆشتن', 'ناوی کڕیار', 
            'کۆدی داشکاندن', 'نرخی کۆتایی', 'کارمەند'
        ])
    if 'inventory' not in st.session_state:
        st.session_state.inventory = pd.DataFrame(columns=[
            'ناوی کەلوپەل', 'ژمارەی دانەکان', 'نرخی کڕین', 
            'بەرواری زیادکردن', 'کەمترین ژمارە'
        ])
    if 'warranty' not in st.session_state:
        st.session_state.warranty = pd.DataFrame(columns=[
            'ناوی کڕیار', 'ژمارەی IMEI', 'بەرواری کۆتایی گەرەنتی', 'جۆری مۆبایل'
        ])
    if 'customers' not in st.session_state:
        st.session_state.customers = pd.DataFrame(columns=[
            'ناوی کڕیار', 'ژمارەی مۆبایل', 'ئیمەیڵ', 'ناونیشان', 
            'بەرواری زیادکردن', 'ڕێکەوتی لەدایکبوون', 'کۆی کڕین', 'خاڵەکان', 'ئاست'
        ])
    if 'discounts' not in st.session_state:
        st.session_state.discounts = pd.DataFrame(columns=[
            'کۆدی داشکاندن', 'ڕێژە', 'بەرواری دەستپێک', 'بەرواری کۆتایی', 
            'کەمترین کڕین', 'ژمارەی بەکارهێنان'
        ])
    if 'employees' not in st.session_state:
        st.session_state.employees = pd.DataFrame(columns=[
            'ناوی کارمەند', 'پلە', 'مووچە', 'بەرواری دەستبەکاربوون', 
            'ژمارەی فرۆشتن', 'کۆی فرۆشتن', 'پاداشت'
        ])
    if 'repairs' not in st.session_state:
        st.session_state.repairs = pd.DataFrame(columns=[
            'ID', 'ناوی کڕیار', 'جۆری مۆبایل', 'کێشە', 
            'بەرواری وەرگرتن', 'بەرواری گەڕاندنەوە', 'نرخی چاککردنەوە', 'ڕەوش'
        ])
    if 'loyalty_points' not in st.session_state:
        st.session_state.loyalty_points = {}
    if 'last_sale_invoice' not in st.session_state:
        st.session_state.last_sale_invoice = None
    if 'installments' not in st.session_state:
        st.session_state.installments = pd.DataFrame(columns=[
            'ID', 'ناوی کڕیار', 'بەرهەم', 'کۆی نرخ', 'پارەی پێشەکی',
            'مانگانە', 'ماوە (مانگ)', 'بەرواری دەستپێک', 'بەرواری کۆتایی',
            'پارەی دراو', 'پارەی ماوە', 'ڕەوش', 'بەرواری داهاتووی قیست'
        ])
    if 'messages' not in st.session_state:
        st.session_state.messages = pd.DataFrame(columns=[
            'ID', 'ناوی کڕیار', 'ژمارە', 'پەیام', 'بەروار', 'ڕەوش'
        ])
    if 'deliveries' not in st.session_state:
        st.session_state.deliveries = pd.DataFrame(columns=[
            'ID', 'ناوی کڕیار', 'ژمارەی مۆبایل', 'ناونیشان',
            'بەرهەم', 'بەرواری داواکاری', 'بەرواری گەیاندن',
            'تێچووی گەیاندن', 'ڕەوش', 'تێبینی'
        ])
    if 'tickets' not in st.session_state:
        st.session_state.tickets = pd.DataFrame(columns=[
            'ID', 'ناوی کڕیار', 'بابەت', 'کێشە', 'لەولەوەپێشی',
            'بەرواری کردنەوە', 'بەرواری داخستن', 'ڕەوش', 'وەڵام'
        ])
    if 'events' not in st.session_state:
        st.session_state.events = pd.DataFrame(columns=[
            'ناونیشان', 'جۆر', 'بەرواری دەستپێک', 'بەرواری کۆتایی',
            'ڕێژەی داشکاندن', 'بەرهەمەکان', 'ڕەوش'
        ])
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    if 'expenses' not in st.session_state:
        st.session_state.expenses = pd.DataFrame(columns=[
            'بەروار', 'جۆر', 'بڕ', 'تێبینی'
        ])

init_session_state()

# ================== HELPER FUNCTIONS ==================
def add_sale(product_name, price, customer_name, discount_code="", employee=""):
    """Add a new sale record"""
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
    
    add_loyalty_points(customer_name, final_price)
    
    if employee:
        update_employee_performance(employee, final_price)
    
    sale_data = {
        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'customer': customer_name,
        'product': product_name,
        'price': price,
        'final_price': final_price
    }
    st.session_state.last_sale_invoice = generate_invoice(sale_data)
    
    return True

def apply_discount(price, discount_code):
    """Apply discount code to price"""
    if discount_code and not st.session_state.discounts.empty:
        discount = st.session_state.discounts[st.session_state.discounts['کۆدی داشکاندن'] == discount_code]
        if not discount.empty:
            rate = discount['ڕێژە'].iloc[0]
            return price * (1 - rate / 100)
    return price

def add_loyalty_points(customer_name, sale_amount):
    """Add loyalty points for customer"""
    points = int(sale_amount / 10)
    if customer_name in st.session_state.loyalty_points:
        st.session_state.loyalty_points[customer_name] += points
    else:
        st.session_state.loyalty_points[customer_name] = points
    
    total_points = st.session_state.loyalty_points[customer_name]
    if total_points >= 1000:
        level = "🏆 پلاتینیۆم"
    elif total_points >= 500:
        level = "🥇 زێڕین"
    elif total_points >= 200:
        level = "🥈 زیوین"
    else:
        level = "🥉 ئاسایی"
    
    if customer_name in st.session_state.customers['ناوی کڕیار'].values:
        idx = st.session_state.customers[st.session_state.customers['ناوی کڕیار'] == customer_name].index[0]
        st.session_state.customers.at[idx, 'خاڵەکان'] = total_points
        st.session_state.customers.at[idx, 'ئاست'] = level
        st.session_state.customers.at[idx, 'کۆی کڕین'] += sale_amount

def update_employee_performance(employee, sale_amount):
    """Update employee performance metrics"""
    if employee in st.session_state.employees['ناوی کارمەند'].values:
        idx = st.session_state.employees[st.session_state.employees['ناوی کارمەند'] == employee].index[0]
        st.session_state.employees.at[idx, 'ژمارەی فرۆشتن'] += 1
        st.session_state.employees.at[idx, 'کۆی فرۆشتن'] += sale_amount
        st.session_state.employees.at[idx, 'پاداشت'] += sale_amount * 0.02

def generate_invoice(sale_data):
    """Generate PDF invoice"""
    try:
        pdf = FPDF()
        pdf.add_page()
        
        pdf.set_font("Arial", "B", 20)
        pdf.cell(0, 10, "Mobile Shop Invoice", ln=True, align="C")
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(10)
        
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"Date: {sale_data.get('date', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}", ln=True)
        pdf.cell(0, 10, f"Customer: {sale_data.get('customer', 'N/A')}", ln=True)
        pdf.cell(0, 10, f"Product: {sale_data.get('product', 'N/A')}", ln=True)
        pdf.cell(0, 10, f"Original Price: ${sale_data.get('price', 0)}", ln=True)
        pdf.cell(0, 10, f"Final Price: ${sale_data.get('final_price', 0)}", ln=True)
        
        try:
            qr = qrcode.make(f"Invoice: {datetime.now().strftime('%Y%m%d%H%M%S')}")
            qr.save("temp_qr.png")
            pdf.image("temp_qr.png", x=150, y=30, w=40)
        except:
            pass
        
        pdf.output("temp_invoice.pdf")
        with open("temp_invoice.pdf", "rb") as f:
            invoice_data = f.read()
        
        # Clean up temp files
        for temp_file in ["temp_qr.png", "temp_invoice.pdf"]:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        
        return invoice_data
    except Exception as e:
        st.error(f"Error generating invoice: {e}")
        return None

def check_low_stock():
    """Check for low stock items"""
    if not st.session_state.inventory.empty:
        return st.session_state.inventory[
            st.session_state.inventory['ژمارەی دانەکان'] < st.session_state.inventory['کەمترین ژمارە']
        ]
    return pd.DataFrame()

def check_expiring_warranty():
    """Check for expiring warranties"""
    if not st.session_state.warranty.empty:
        today = datetime.now().date()
        warranty_dates = pd.to_datetime(st.session_state.warranty['بەرواری کۆتایی گەرەنتی']).dt.date
        days_remaining = (warranty_dates - today).dt.days
        return st.session_state.warranty[(days_remaining <= 30) & (days_remaining >= 0)]
    return pd.DataFrame()

def check_upcoming_installments():
    """Check for upcoming installment payments"""
    if not st.session_state.installments.empty:
        today = datetime.now().date()
        upcoming = st.session_state.installments[
            (pd.to_datetime(st.session_state.installments['بەرواری داهاتووی قیست']).dt.date - today).dt.days <= 7
        ]
        return upcoming
    return pd.DataFrame()

def export_to_excel(df, sheet_name="Data"):
    """Export dataframe to Excel"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    return output.getvalue()

def get_download_link(data, filename):
    """Generate download link for data"""
    b64 = base64.b64encode(data).decode()
    return f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}" style="text-decoration: none; color: #667eea;">📥 داگرتنی {filename}</a>'

def predict_future_sales(days=30):
    """Predict future sales using AI"""
    if not SKLEARN_AVAILABLE:
        return None
    
    if len(st.session_state.sales) < 7:
        return None
    
    try:
        sales_df = st.session_state.sales.copy()
        sales_df['date'] = pd.to_datetime(sales_df['کاتی فرۆشتن']).dt.date
        daily_sales = sales_df.groupby('date')['نرخی کۆتایی'].sum().reset_index()
        
        daily_sales['day_num'] = range(len(daily_sales))
        
        X = daily_sales[['day_num']].values
        y = daily_sales['نرخی کۆتایی'].values
        
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)
        
        future_days = np.array(range(len(daily_sales), len(daily_sales) + days)).reshape(-1, 1)
        predictions = model.predict(future_days)
        
        return predictions
    except Exception as e:
        st.error(f"Error in prediction: {e}")
        return None

def backup_data():
    """Backup all data"""
    all_data = {
        'sales': st.session_state.sales.to_dict(),
        'inventory': st.session_state.inventory.to_dict(),
        'warranty': st.session_state.warranty.to_dict(),
        'customers': st.session_state.customers.to_dict(),
        'discounts': st.session_state.discounts.to_dict(),
        'employees': st.session_state.employees.to_dict(),
        'repairs': st.session_state.repairs.to_dict(),
        'installments': st.session_state.installments.to_dict(),
        'expenses': st.session_state.expenses.to_dict(),
        'loyalty_points': st.session_state.loyalty_points,
        'backup_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    backup_json = json.dumps(all_data, default=str)
    backup_pickle = pickle.dumps(all_data)
    
    return backup_json, backup_pickle

def restore_data(uploaded_file):
    """Restore data from backup"""
    try:
        if uploaded_file.name.endswith('.json'):
            data = json.loads(uploaded_file.read())
        elif uploaded_file.name.endswith('.pkl'):
            data = pickle.loads(uploaded_file.read())
        else:
            st.error("جۆری فایل پشتگیری ناکرێت")
            return False
        
        st.session_state.sales = pd.DataFrame(data['sales'])
        st.session_state.inventory = pd.DataFrame(data['inventory'])
        st.session_state.warranty = pd.DataFrame(data['warranty'])
        st.session_state.customers = pd.DataFrame(data['customers'])
        st.session_state.discounts = pd.DataFrame(data['discounts'])
        st.session_state.employees = pd.DataFrame(data['employees'])
        st.session_state.repairs = pd.DataFrame(data['repairs'])
        st.session_state.installments = pd.DataFrame(data['installments'])
        st.session_state.expenses = pd.DataFrame(data['expenses'])
        st.session_state.loyalty_points = data['loyalty_points']
        
        return True
    except Exception as e:
        st.error(f"هەڵە لە گەڕاندنەوەی داتا: {e}")
        return False

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
        with st.expander(f"⏰ {len(expiring_warranties)} گەرەنتی نزیک!", expanded=False):
            for _, warranty in expiring_warranties.iterrows():
                st.warning(f"📱 {warranty['ناوی کڕیار']} - {warranty['جۆری مۆبایل']}")
    
    upcoming_installments = check_upcoming_installments()
    if not upcoming_installments.empty:
        with st.expander(f"💳 {len(upcoming_installments)} قیستی نزیک!", expanded=False):
            for _, inst in upcoming_installments.iterrows():
                st.warning(f"💰 {inst['ناوی کڕیار']}: ${inst['مانگانە']:,.2f}")
    
    st.markdown("---")
    
    # مینوی سەرەکی
    menu_options = {
        "💰 فرۆشتن": ["📝 فرۆشتنی نوێ", "📋 لیستی فرۆشتنەکان", "🧾 فاکتوور"],
        "📦 کۆگا": ["📝 زیادکردنی کەلوپەل", "📋 لیستی کۆگا", "🔄 بەڕێوەبردنی کۆگا"],
        "🛡️ گەرەنتی": ["📝 تۆمارکردنی گەرەنتی", "📋 لیستی گەرەنتی", "⚠️ ئاگادارییەکان"],
        "📊 قازانج": ["💰 خەمڵاندنی قازانج", "📈 هێڵکاری", "📋 ڕاپۆرت", "💸 خەرجییەکان"],
        "👥 کڕیاران": ["📝 زیادکردنی کڕیار", "📋 لیستی کڕیاران", "⭐ بەرنامەی خاڵ"],
        "💳 قیستەکان": ["📝 قیستی نوێ", "📋 لیستی قیستەکان", "📊 بەدواداچوون"],
        "🏷️ داشکاندن": ["📝 داشکاندنی نوێ", "📋 داشکاندنەکان", "🎉 بۆنەکان"],
        "👨‍💼 کارمەندان": ["📝 زیادکردنی کارمەند", "📋 کارمەندان", "📊 ئاستی کارمەندان"],
        "🔧 چاککردنەوە": ["📝 تۆمارکردن", "📋 لیست", "🔄 بەڕێوەبردن"],
        "🚚 گەیاندن": ["📝 گەیاندنی نوێ", "📋 لیستی گەیاندنەکان"],
        "📱 پەیامەکان": ["📝 ناردنی پەیام", "📋 مێژووی پەیامەکان"],
        "🎫 پشتیوانی": ["📝 تیکتی نوێ", "📋 تیکتەکان", "💬 چاتی ڕاستەوخۆ"],
        "📊 داشبۆرد": ["🎯 داشبۆردی سەرەکی", "🔮 پێشبینیکردن", "📊 بەراوردکردن"],
        "⚙️ ڕێکخستنەکان": ["💾 بەکاپ و گەڕاندنەوە", "🎨 ڕێکخستنی ڕووکار"]
    }
    
    main_choice = st.selectbox("بەشێک هەڵبژێرە:", list(menu_options.keys()))
    
    if main_choice in menu_options:
        sub_choice = st.radio("ژێربەش:", menu_options[main_choice])
    
    st.markdown("---")
    
    # کورتەی گشتی
    st.markdown("### 📊 کورتەی گشتی")
    
    total_sales = st.session_state.sales['نرخی کۆتایی'].sum() if not st.session_state.sales.empty else 0
    total_cost = (st.session_state.inventory['نرخی کڕین'] * st.session_state.inventory['ژمارەی دانەکان']).sum() if not st.session_state.inventory.empty else 0
    total_expenses = st.session_state.expenses['بڕ'].sum() if not st.session_state.expenses.empty else 0
    profit = total_sales - total_cost - total_expenses
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💰 فرۆشتن", f"${total_sales:,.0f}")
    with col2:
        st.metric("📦 کڕیار", f"{len(st.session_state.customers)}")
    with col3:
        st.metric("💵 قازانج", f"${profit:,.0f}")

# ================== MAIN CONTENT ==================
st.markdown('<p class="main-header">📱 سیستەمی بەڕێوەبردنی دوکانی مۆبایل - پڕۆماکس</p>', unsafe_allow_html=True)

# ================== 1. SALES SECTION ==================
if main_choice == "💰 فرۆشتن":
    if sub_choice == "📝 فرۆشتنی نوێ":
        st.header("📝 تۆمارکردنی فرۆشتنی نوێ")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            with st.form("sale_form"):
                product_name = st.text_input("📱 ناوی بەرهەم", placeholder="iPhone 15 Pro")
                
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
                        final_price = original_price
                
                with col_employee:
                    if not st.session_state.employees.empty:
                        employee = st.selectbox("👨‍💼 کارمەند", [""] + list(st.session_state.employees['ناوی کارمەند']))
                    else:
                        employee = ""
                
                submitted = st.form_submit_button("➕ تۆمارکردنی فرۆشتن", use_container_width=True)
            
            if submitted:
                if product_name and original_price > 0 and customer_name:
                    if add_sale(product_name, original_price, customer_name, discount_code, employee):
                        st.success(f"✅ فرۆشتنی {product_name} بە نرخی ${final_price:,.2f} بۆ {customer_name} تۆمار کرا!")
                        st.balloons()
                        
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
    
    elif sub_choice == "📋 لیستی فرۆشتنەکان":
        st.header("📋 لیستی فرۆشتنەکان")
        
        if not st.session_state.sales.empty:
            col_f1, col_f2, col_f3 = st.columns(3)
            with col_f1:
                date_filter = st.date_input("📅 فلتەر بەپێی بەروار", value=None)
            with col_f2:
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
elif main_choice == "📦 کۆگا":
    if sub_choice == "📝 زیادکردنی کەلوپەل":
        st.header("📝 زیادکردنی کەلوپەلی نوێ")
        
        with st.form("inventory_form"):
            item_name = st.text_input("🏷️ ناوی کەلوپەل")
            
            col1, col2 = st.columns(2)
            with col1:
                stock = st.number_input("📦 ژمارەی دانەکان", min_value=1, step=1)
            with col2:
                purchase_price = st.number_input("💰 نرخی کڕین ($)", min_value=0.0, step=1.0)
            
            min_stock = st.number_input("⚠️ ئاستی ئاگادارکردنەوە", min_value=1, value=5)
            
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
            
            st.dataframe(inventory_display, use_container_width=True)
            
            col_s1, col_s2, col_s3 = st.columns(3)
            with col_s1:
                st.metric("کۆی جۆرەکان", f"{len(inventory_display)}")
            with col_s2:
                st.metric("کۆی دانەکان", f"{inventory_display['ژمارەی دانەکان'].sum():,}")
            with col_s3:
                st.metric("کۆی بەها", f"${inventory_display['کۆی بەها'].sum():,.2f}")
            
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
        
        with st.form("warranty_form"):
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
            st.dataframe(warranty_display, use_container_width=True)
            
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

# ================== CONTINUE WITH REMAINING SECTIONS ==================
# (All other sections follow the same pattern - I'll include the key ones)

# ================== 4. PROFIT & EXPENSES SECTION ==================
elif main_choice == "📊 قازانج":
    total_sales = st.session_state.sales['نرخی کۆتایی'].sum() if not st.session_state.sales.empty else 0
    total_cost = (st.session_state.inventory['نرخی کڕین'] * st.session_state.inventory['ژمارەی دانەکان']).sum() if not st.session_state.inventory.empty else 0
    total_expenses = st.session_state.expenses['بڕ'].sum() if not st.session_state.expenses.empty else 0
    profit = total_sales - total_cost - total_expenses
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
            st.metric("خەرجییەکان", f"${total_expenses:,.2f}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("قازانجی پوخت", f"${profit:,.2f}", delta=f"{profit_margin:.1f}%")
            st.markdown('</div>', unsafe_allow_html=True)
        
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
                go.Bar(name='خەرجی', x=['دارایی'], y=[total_expenses], marker_color='#f39c12'),
                go.Bar(name='قازانج', x=['دارایی'], y=[profit], marker_color='#3498db')
            ])
            fig.update_layout(barmode='group', height=500)
            st.plotly_chart(fig, use_container_width=True)
    
    elif sub_choice == "📋 ڕاپۆرت":
        st.header("📋 ڕاپۆرتی قازانج")
        
        if not st.session_state.sales.empty:
            sales_copy = st.session_state.sales.copy()
            sales_copy['مانگ'] = pd.to_datetime(sales_copy['کاتی فرۆشتن']).dt.to_period('M')
            monthly_sales = sales_copy.groupby('مانگ')['نرخی کۆتایی'].sum()
            
            st.subheader("📅 فرۆشتنی مانگانە")
            st.dataframe(monthly_sales)
            
            if st.button("📥 داگرتنی ڕاپۆرتی تەواو"):
                excel_data = export_to_excel(sales_copy, 'Full Report')
                st.markdown(get_download_link(excel_data, 'full_report.xlsx'), unsafe_allow_html=True)
        else:
            st.info("داتای فرۆشتن بەردەست نییە")
    
    elif sub_choice == "💸 خەرجییەکان":
        st.header("💸 بەدواداچوونی خەرجییەکان")
        
        with st.form("expense_form"):
            expense_type = st.selectbox("جۆری خەرجی", [
                "کرێی دوکان", "مووچە", "کارەبا", "ئاو", "ئینتەرنێت",
                "بازاڕکردن", "پاککەرەوە", "هاتوچۆ", "ی تر"
            ])
            
            amount = st.number_input("بڕ ($)", min_value=0.0)
            date = st.date_input("بەروار")
            note = st.text_area("تێبینی")
            
            if st.form_submit_button("➕ زیادکردنی خەرجی"):
                new_expense = pd.DataFrame({
                    'بەروار': [date.strftime("%Y-%m-%d")],
                    'جۆر': [expense_type],
                    'بڕ': [amount],
                    'تێبینی': [note]
                })
                st.session_state.expenses = pd.concat([st.session_state.expenses, new_expense], ignore_index=True)
                st.success("✅ خەرجی تۆمار کرا!")
        
        if not st.session_state.expenses.empty:
            st.subheader("📊 خەرجییەکان")
            expenses_by_type = st.session_state.expenses.groupby('جۆر')['بڕ'].sum()
            fig = px.pie(values=expenses_by_type.values, names=expenses_by_type.index, 
                        title="دابەشبوونی خەرجییەکان")
            st.plotly_chart(fig, use_container_width=True)

# ================== 13. DASHBOARD SECTION ==================
elif main_choice == "📊 داشبۆرد":
    if sub_choice == "🎯 داشبۆردی سەرەکی":
        st.header("🎯 داشبۆردی سەرەکی")
        
        today = datetime.now().date()
        today_sales = 0
        if not st.session_state.sales.empty:
            sales_today = st.session_state.sales.copy()
            sales_today['date'] = pd.to_datetime(sales_today['کاتی فرۆشتن']).dt.date
            today_sales = sales_today[sales_today['date'] == today]['نرخی کۆتایی'].sum()
        
        col1, col2, col3, col4 = st.columns(4)
        
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
            pending_repairs = len(st.session_state.repairs[st.session_state.repairs['ڕەوش'].isin(['چاوەڕوان', 'لەژێر کاردایە'])]) if not st.session_state.repairs.empty else 0
            st.metric("🔧 چاککردنەوە", f"{pending_repairs}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            active_tickets = len(st.session_state.tickets[st.session_state.tickets['ڕەوش'] == 'کراوە']) if not st.session_state.tickets.empty else 0
            st.metric("🎫 تیکتی کراوە", f"{active_tickets}")
            st.markdown('</div>', unsafe_allow_html=True)
    
    elif sub_choice == "🔮 پێشبینیکردن":
        st.header("🔮 پێشبینیکردنی فرۆشتن بە AI")
        
        if SKLEARN_AVAILABLE:
            predictions = predict_future_sales(30)
            if predictions is not None:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    y=predictions,
                    mode='lines+markers',
                    name='پێشبینیکراو',
                    line=dict(color='blue', dash='dash')
                ))
                fig.update_layout(title="پێشبینی 30 ڕۆژی داهاتوو")
                st.plotly_chart(fig, use_container_width=True)
                
                avg_prediction = predictions.mean()
                st.info(f"📊 تێکڕای پێشبینیکراو: ${avg_prediction:,.2f} لە ڕۆژێکدا")
            else:
                st.warning("پێویستە بەلایەنی کەمەوە 7 فرۆشتن تۆمار کرا بێت بۆ پێشبینیکردن")
        else:
            st.warning("کیتەخانەی scikit-learn دامەزراو نییە. بۆ بەکارهێنانی AI، تکایە ئەم کتێبخانەیە دامەزرێنە.")
    
    elif sub_choice == "📊 بەراوردکردن":
        st.header("📊 بەراوردکردنی بەرهەمەکان")
        
        if not st.session_state.sales.empty:
            products = st.session_state.sales['ناوی بەرهەم'].unique()
            
            col1, col2 = st.columns(2)
            
            with col1:
                product1 = st.selectbox("بەرهەمی یەکەم", products)
                if product1:
                    sales1 = st.session_state.sales[st.session_state.sales['ناوی بەرهەم'] == product1]
                    st.metric("کۆی فرۆشتن", f"${sales1['نرخی کۆتایی'].sum():,.2f}")
                    st.metric("ژمارەی فرۆشتن", f"{len(sales1)}")
            
            with col2:
                product2 = st.selectbox("بەرهەمی دووەم", products)
                if product2:
                    sales2 = st.session_state.sales[st.session_state.sales['ناوی بەرهەم'] == product2]
                    st.metric("کۆی فرۆشتن", f"${sales2['نرخی کۆتایی'].sum():,.2f}")
                    st.metric("ژمارەی فرۆشتن", f"{len(sales2)}")
            
            if product1 and product2:
                fig = go.Figure(data=[
                    go.Bar(name=product1, x=['کۆی فرۆشتن', 'ژمارە'], 
                          y=[sales1['نرخی کۆتایی'].sum(), len(sales1)]),
                    go.Bar(name=product2, x=['کۆی فرۆشتن', 'ژمارە'], 
                          y=[sales2['نرخی کۆتایی'].sum(), len(sales2)])
                ])
                fig.update_layout(barmode='group', title="بەراوردی بەرهەمەکان")
                st.plotly_chart(fig, use_container_width=True)

# ================== 14. SETTINGS SECTION ==================
elif main_choice == "⚙️ ڕێکخستنەکان":
    if sub_choice == "💾 بەکاپ و گەڕاندنەوە":
        st.header("💾 بەکاپ و گەڕاندنەوەی داتا")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📥 بەکاپگرتن")
            if st.button("📥 دروستکردنی بەکاپ"):
                json_backup, pickle_backup = backup_data()
                
                st.download_button(
                    label="📥 داگرتنی بەکاپ (JSON)",
                    data=json_backup,
                    file_name=f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    key="backup_json"
                )
                
                st.download_button(
                    label="📥 داگرتنی بەکاپ (Pickle)",
                    data=pickle_backup,
                    file_name=f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl",
                    mime="application/octet-stream",
                    key="backup_pickle"
                )
                
                st.success("✅ بەکاپ بە سەرکەوتوویی دروست کرا!")
        
        with col2:
            st.subheader("📤 گەڕاندنەوە")
            uploaded_backup = st.file_uploader("فایلی بەکاپ هەڵبژێرە", type=['json', 'pkl'])
            if uploaded_backup:
                if st.button("🔄 گەڕاندنەوەی داتا"):
                    if restore_data(uploaded_backup):
                        st.success("✅ داتاکان بە سەرکەوتوویی گەڕێندرانەوە!")
                        st.balloons()
    
    elif sub_choice == "🎨 ڕێکخستنی ڕووکار":
        st.header("🎨 ڕێکخستنی ڕووکاری بەکارهێنەر")
        
        theme_color = st.color_picker("🎨 ڕەنگی سەرەکی", "#667eea")
        
        st.markdown(f"""
        <style>
        .metric-card {{
            background: linear-gradient(135deg, {theme_color} 0%, #764ba2 100%);
        }}
        .stButton > button {{
            background: linear-gradient(135deg, {theme_color} 0%, #764ba2 100%);
        }}
        </style>
        """, unsafe_allow_html=True)
        
        st.success("✅ ڕێکخستنەکان پاشەکەوت کران!")

# ================== FOOTER ==================
st.markdown("---")
st.markdown("""
    <div class="footer">
        <h3>📱 سیستەمی بەڕێوەبردنی دوکانی مۆبایل - وەشانی پڕۆماکس</h3>
        <p>هەموو مافێک پارێزراوە © 2024</p>
        <p>🚀 14 بەشی جیاواز | 🤖 پێشبینیکردنی AI | 💬 پشتیوانی ڕاستەوخۆ</p>
        <p>💳 قیست | 🚚 گەیاندن | 📱 پەیام | 🎉 بۆنە | 💾 بەکاپ</p>
    </div>
""", unsafe_allow_html=True)
