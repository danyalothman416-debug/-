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
import tempfile

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
        st.session_state.sales = pd.DataFrame(columns=['ناوی بەرهەم','نرخ','کاتی فرۆشتن','ناوی کڕیار','کۆدی داشکاندن','نرخی کۆتایی','کارمەند','نرخی کڕینی بەرهەم'])
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
def apply_discount(price, code):
    if code and not st.session_state.discounts.empty:
        d = st.session_state.discounts[st.session_state.discounts['کۆدی داشکاندن'] == code]
        if not d.empty:
            today = datetime.now().date()
            start = pd.to_datetime(d['بەرواری دەستپێک'].iloc[0]).date() if pd.notna(d['بەرواری دەستپێک'].iloc[0]) else None
            end = pd.to_datetime(d['بەرواری کۆتایی'].iloc[0]).date() if pd.notna(d['بەرواری کۆتایی'].iloc[0]) else None
            if start and end and start <= today <= end:
                return price * (1 - d['ڕێژە'].iloc[0] / 100)
    return price

def add_loyalty_points(customer, amount):
    points = int(amount / 10)
    st.session_state.loyalty_points[customer] = st.session_state.loyalty_points.get(customer, 0) + points
    total = st.session_state.loyalty_points[customer]
    
    if total >= 1000:
        level = "🏆 پلاتینیۆم"
    elif total >= 500:
        level = "🥇 زێڕین"
    elif total >= 200:
        level = "🥈 زیوین"
    else:
        level = "🥉 ئاسایی"
    
    # Update customer in dataframe if exists
    if not st.session_state.customers.empty and customer in st.session_state.customers['ناوی کڕیار'].values:
        idx = st.session_state.customers[st.session_state.customers['ناوی کڕیار'] == customer].index
        if len(idx) > 0:
            idx = idx[0]
            current_total = st.session_state.customers.at[idx, 'کۆی کڕین'] if pd.notna(st.session_state.customers.at[idx, 'کۆی کڕین']) else 0
            st.session_state.customers.at[idx, 'کۆی کڕین'] = current_total + amount
            st.session_state.customers.at[idx, 'خاڵەکان'] = total
            st.session_state.customers.at[idx, 'ئاست'] = level

def update_employee_performance(emp, amount):
    if emp and not st.session_state.employees.empty and emp in st.session_state.employees['ناوی کارمەند'].values:
        idx = st.session_state.employees[st.session_state.employees['ناوی کارمەند'] == emp].index
        if len(idx) > 0:
            idx = idx[0]
            current_count = st.session_state.employees.at[idx, 'ژمارەی فرۆشتن'] if pd.notna(st.session_state.employees.at[idx, 'ژمارەی فرۆشتن']) else 0
            current_total = st.session_state.employees.at[idx, 'کۆی فرۆشتن'] if pd.notna(st.session_state.employees.at[idx, 'کۆی فرۆشتن']) else 0
            current_bonus = st.session_state.employees.at[idx, 'پاداشت'] if pd.notna(st.session_state.employees.at[idx, 'پاداشت']) else 0
            
            st.session_state.employees.at[idx, 'ژمارەی فرۆشتن'] = current_count + 1
            st.session_state.employees.at[idx, 'کۆی فرۆشتن'] = current_total + amount
            st.session_state.employees.at[idx, 'پاداشت'] = current_bonus + (amount * 0.02)

def update_inventory_after_sale(product_name, quantity=1):
    """کەمکردنەوەی ژمارەی کەلوپەل دوای فرۆشتن"""
    if not st.session_state.inventory.empty:
        idx = st.session_state.inventory[st.session_state.inventory['ناوی کەلوپەل'] == product_name].index
        if len(idx) > 0:
            idx = idx[0]
            current_qty = st.session_state.inventory.at[idx, 'ژمارەی دانەکان']
            if current_qty >= quantity:
                st.session_state.inventory.at[idx, 'ژمارەی دانەکان'] = current_qty - quantity
                return True
    return False

def get_product_cost(product_name):
    """وەرگرتنی نرخی کڕینی بەرهەم"""
    if not st.session_state.inventory.empty:
        idx = st.session_state.inventory[st.session_state.inventory['ناوی کەلوپەل'] == product_name].index
        if len(idx) > 0:
            return st.session_state.inventory.at[idx[0], 'نرخی کڕین']
    return 0

def add_sale(product_name, price, customer_name, discount_code="", employee=""):
    try:
        if not product_name or price <= 0 or not customer_name:
            st.error("تکایە ناوی بەرهەم، نرخ و ناوی کڕیار پڕ بکەرەوە")
            return False
        
        # Get product cost
        product_cost = get_product_cost(product_name)
        
        # Update inventory
        update_inventory_after_sale(product_name, 1)
        
        final_price = apply_discount(price, discount_code)
        new_sale = pd.DataFrame({
            'ناوی بەرهەم': [product_name], 
            'نرخ': [float(price)],
            'کاتی فرۆشتن': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            'ناوی کڕیار': [customer_name], 
            'کۆدی داشکاندن': [discount_code],
            'نرخی کۆتایی': [final_price], 
            'کارمەند': [employee],
            'نرخی کڕینی بەرهەم': [product_cost]
        })
        st.session_state.sales = pd.concat([st.session_state.sales, new_sale], ignore_index=True)
        add_loyalty_points(customer_name, final_price)
        if employee: 
            update_employee_performance(employee, final_price)
        
        # Create invoice
        st.session_state.last_sale_invoice = generate_invoice({
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'customer': customer_name, 
            'product': product_name,
            'price': price, 
            'final_price': final_price
        })
        return True
    except Exception as e:
        st.error(f"هەڵە لە تۆمارکردنی فرۆشتن: {str(e)}")
        return False

def add_installment(customer_name, product, total_price, down_payment, months):
    """زیادکردنی قیستی نوێ"""
    try:
        remaining = total_price - down_payment
        monthly = remaining / months if months > 0 else 0
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=30 * months)
        next_payment = start_date + timedelta(days=30)
        
        new_installment = pd.DataFrame({
            'ID': [f"INS{datetime.now().strftime('%Y%m%d%H%M%S')}"],
            'ناوی کڕیار': [customer_name],
            'بەرهەم': [product],
            'کۆی نرخ': [total_price],
            'پارەی پێشەکی': [down_payment],
            'مانگانە': [monthly],
            'ماوە (مانگ)': [months],
            'بەرواری دەستپێک': [start_date.strftime("%Y-%m-%d")],
            'بەرواری کۆتایی': [end_date.strftime("%Y-%m-%d")],
            'پارەی دراو': [down_payment],
            'پارەی ماوە': [remaining],
            'ڕەوش': ['چالاکە'],
            'بەرواری داهاتووی قیست': [next_payment.strftime("%Y-%m-%d")]
        })
        st.session_state.installments = pd.concat([st.session_state.installments, new_installment], ignore_index=True)
        return True
    except Exception as e:
        st.error(f"هەڵە لە زیادکردنی قیست: {str(e)}")
        return False

def add_installment_payment(installment_id, amount):
    """پارەدان بۆ قیستێک"""
    try:
        if not st.session_state.installments.empty:
            idx = st.session_state.installments[st.session_state.installments['ID'] == installment_id].index
            if len(idx) > 0:
                idx = idx[0]
                current_paid = st.session_state.installments.at[idx, 'پارەی دراو'] if pd.notna(st.session_state.installments.at[idx, 'پارەی دراو']) else 0
                total = st.session_state.installments.at[idx, 'کۆی نرخ']
                new_paid = current_paid + amount
                
                st.session_state.installments.at[idx, 'پارەی دراو'] = new_paid
                st.session_state.installments.at[idx, 'پارەی ماوە'] = total - new_paid
                
                if new_paid >= total:
                    st.session_state.installments.at[idx, 'ڕەوش'] = 'تەواو'
                else:
                    next_date = datetime.now().date() + timedelta(days=30)
                    st.session_state.installments.at[idx, 'بەرواری داهاتووی قیست'] = next_date.strftime("%Y-%m-%d")
                
                return True
        return False
    except Exception as e:
        st.error(f"هەڵە لە پارەدانی قیست: {str(e)}")
        return False

def generate_invoice(data):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_pdf:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 20)
            pdf.cell(0, 10, "Mobile Shop Invoice", ln=True, align="C")
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(10)
            pdf.set_font("Arial", "", 12)
            pdf.cell(0, 10, f"Date: {data.get('date', '')}", ln=True)
            pdf.cell(0, 10, f"Customer: {data.get('customer', '')}", ln=True)
            pdf.cell(0, 10, f"Product: {data.get('product', '')}", ln=True)
            pdf.cell(0, 10, f"Original Price: ${data.get('price', 0):.2f}", ln=True)
            pdf.cell(0, 10, f"Final Price: ${data.get('final_price', 0):.2f}", ln=True)
            
            # Add QR code
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_qr:
                    qr = qrcode.make(f"INV{datetime.now().strftime('%Y%m%d%H%M%S')}")
                    qr.save(tmp_qr.name)
                    pdf.image(tmp_qr.name, x=150, y=30, w=40)
                    os.unlink(tmp_qr.name)
            except Exception:
                pass
            
            pdf.output(tmp_pdf.name)
            with open(tmp_pdf.name, "rb") as f:
                result = f.read()
            os.unlink(tmp_pdf.name)
            return result
    except Exception as e:
        return None

def check_low_stock():
    if not st.session_state.inventory.empty and 'ژمارەی دانەکان' in st.session_state.inventory.columns and 'کەمترین ژمارە' in st.session_state.inventory.columns:
        return st.session_state.inventory[st.session_state.inventory['ژمارەی دانەکان'] < st.session_state.inventory['کەمترین ژمارە']]
    return pd.DataFrame()

def check_expiring_warranty():
    if not st.session_state.warranty.empty and 'بەرواری کۆتایی گەرەنتی' in st.session_state.warranty.columns:
        try:
            today = datetime.now().date()
            st.session_state.warranty['بەرواری کۆتایی گەرەنتی'] = pd.to_datetime(st.session_state.warranty['بەرواری کۆتایی گەرەنتی']).dt.date
            dates = st.session_state.warranty['بەرواری کۆتایی گەرەنتی']
            return st.session_state.warranty[((dates - today).dt.days <= 30) & ((dates - today).dt.days >= 0)]
        except:
            return pd.DataFrame()
    return pd.DataFrame()

def check_upcoming_installments():
    """پێدانی قیستە نزیکەکان"""
    if not st.session_state.installments.empty and 'بەرواری داهاتووی قیست' in st.session_state.installments.columns:
        try:
            today = datetime.now().date()
            st.session_state.installments['بەرواری داهاتووی قیست'] = pd.to_datetime(st.session_state.installments['بەرواری داهاتووی قیست']).dt.date
            upcoming = st.session_state.installments[
                (st.session_state.installments['ڕەوش'] == 'چالاکە') &
                ((st.session_state.installments['بەرواری داهاتووی قیست'] - today).dt.days <= 7)
            ]
            return upcoming
        except:
            return pd.DataFrame()
    return pd.DataFrame()

def check_birthdays():
    today = datetime.now()
    birthdays = []
    if not st.session_state.customers.empty and 'ڕێکەوتی لەدایکبوون' in st.session_state.customers.columns:
        for _, c in st.session_state.customers.iterrows():
            if c['ڕێکەوتی لەدایکبوون'] and pd.notna(c['ڕێکەوتی لەدایکبوون']) and c['ڕێکەوتی لەدایکبوون'] != '':
                try:
                    bd = pd.to_datetime(c['ڕێکەوتی لەدایکبوون'])
                    if bd.month == today.month and bd.day == today.day:
                        birthdays.append(c['ناوی کڕیار'])
                except:
                    pass
    return birthdays

def calculate_actual_profit():
    """هەژمارکردنی قازانجی ڕاستەقینە"""
    if st.session_state.sales.empty:
        return 0, 0, 0, 0
    
    total_sales = st.session_state.sales['نرخی کۆتایی'].sum()
    total_cost_of_sold = 0
    
    for _, sale in st.session_state.sales.iterrows():
        if 'نرخی کڕینی بەرهەم' in sale and pd.notna(sale['نرخی کڕینی بەرهەم']):
            total_cost_of_sold += sale['نرخی کڕینی بەرهەم']
        else:
            # If cost not stored, try to get from inventory
            cost = get_product_cost(sale['ناوی بەرهەم'])
            total_cost_of_sold += cost
    
    total_expenses = st.session_state.expenses['بڕ'].sum() if not st.session_state.expenses.empty else 0
    net_profit = total_sales - total_cost_of_sold - total_expenses
    profit_margin = (net_profit / total_sales * 100) if total_sales > 0 else 0
    
    return total_sales, total_cost_of_sold, total_expenses, net_profit, profit_margin

def export_to_excel(df, sheet="Data"):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=sheet, index=False)
    return output.getvalue()

def get_download_link(data, filename):
    b64 = base64.b64encode(data).decode()
    return f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">📥 {filename}</a>'

def backup_data():
    all_data = {}
    for k, v in st.session_state.items():
        if not k.startswith('_'):
            if hasattr(v, 'to_dict'):
                all_data[k] = v.to_dict()
            else:
                all_data[k] = v
    all_data['backup_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return json.dumps(all_data, default=str), pickle.dumps(all_data)

def restore_data(uploaded_file):
    try:
        if uploaded_file.name.endswith('.json'):
            data = json.loads(uploaded_file.read().decode('utf-8'))
        else:
            data = pickle.loads(uploaded_file.read())
        
        for key in data:
            if key != 'backup_date' and key in st.session_state:
                if isinstance(data[key], dict) and hasattr(st.session_state[key], 'empty'):
                    st.session_state[key] = pd.DataFrame(data[key])
                else:
                    st.session_state[key] = data[key]
        return True
    except Exception as e:
        st.error(f"هەڵە لە گەڕاندنەوەی بەکاپ: {str(e)}")
        return False

def create_sample_data():
    """Create sample data for testing"""
    if st.session_state.sales.empty:
        sample_sale = pd.DataFrame({
            'ناوی بەرهەم': ['iPhone 15 Pro', 'Samsung Galaxy S24', 'Google Pixel 8'],
            'نرخ': [1000, 900, 800],
            'کاتی فرۆشتن': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")] * 3,
            'ناوی کڕیار': ['ئەحمەد', 'سارا', 'محەمەد'],
            'کۆدی داشکاندن': ['', '', ''],
            'نرخی کۆتایی': [1000, 900, 800],
            'کارمەند': ['ڕێباز', 'ڕێباز', 'هەڵگورد'],
            'نرخی کڕینی بەرهەم': [700, 600, 550]
        })
        st.session_state.sales = sample_sale
        
    if st.session_state.inventory.empty:
        sample_inv = pd.DataFrame({
            'ناوی کەلوپەل': ['iPhone 15 Pro', 'Samsung Galaxy S24', 'Google Pixel 8', 'Charger', 'Phone Case'],
            'ژمارەی دانەکان': [15, 12, 8, 50, 100],
            'نرخی کڕین': [700, 600, 550, 15, 5],
            'بەرواری زیادکردن': [datetime.now().strftime("%Y-%m-%d")] * 5,
            'کەمترین ژمارە': [5, 5, 5, 20, 30]
        })
        st.session_state.inventory = sample_inv
    
    if st.session_state.employees.empty:
        sample_emp = pd.DataFrame({
            'ناوی کارمەند': ['ڕێباز', 'هەڵگورد', 'دڵشاد'],
            'پلە': ['بەڕێوەبەر', 'فرۆشیار', 'فرۆشیار'],
            'مووچە': [1000, 600, 600],
            'بەرواری دەستبەکاربوون': [datetime.now().strftime("%Y-%m-%d")] * 3,
            'ژمارەی فرۆشتن': [0, 0, 0],
            'کۆی فرۆشتن': [0, 0, 0],
            'پاداشت': [0, 0, 0]
        })
        st.session_state.employees = sample_emp
    
    if st.session_state.customers.empty:
        sample_customers = pd.DataFrame({
            'ناوی کڕیار': ['ئەحمەد', 'سارا', 'محەمەد'],
            'ژمارەی مۆبایل': ['07701234567', '07707654321', '07501234567'],
            'ئیمەیڵ': ['ahmed@email.com', 'sara@email.com', 'mohammed@email.com'],
            'ناونیشان': ['سلێمانی', 'هەولێر', 'دهۆک'],
            'بەرواری زیادکردن': [datetime.now().strftime("%Y-%m-%d")] * 3,
            'ڕێکەوتی لەدایکبوون': ['1990-01-01', '1995-05-15', '1988-10-20'],
            'کۆی کڕین': [1000, 900, 800],
            'خاڵەکان': [100, 90, 80],
            'ئاست': ['🥈 زیوین', '🥈 زیوین', '🥉 ئاسایی']
        })
        st.session_state.customers = sample_customers
        
    st.success("✅ داتای نموونەیی دروست کرا!")

# ================== SIDEBAR ==================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/shop.png", width=80)
    st.title("📱 مینوی سەرەکی")
    
    # Sample data button
    if st.button("📊 داتای نموونەیی دروست بکە"):
        create_sample_data()
    
    st.markdown("---")
    st.markdown("### 🔔 ئاگادارییەکان")
    
    low = check_low_stock()
    if not low.empty:
        with st.expander(f"⚠️ {len(low)} کەلوپەلی کەم!", expanded=True):
            for _, i in low.iterrows(): 
                st.error(f"📦 {i['ناوی کەلوپەل']}: {i['ژمارەی دانەکان']} دانە")
    
    exp = check_expiring_warranty()
    if not exp.empty:
        with st.expander(f"⏰ {len(exp)} گەرەنتی نزیک!", expanded=False):
            for _, w in exp.iterrows(): 
                st.warning(f"📱 {w['ناوی کڕیار']} - {w['جۆری مۆبایل']}")
    
    inst = check_upcoming_installments()
    if not inst.empty:
        with st.expander(f"💳 {len(inst)} قیستی نزیک!", expanded=False):
            for _, i in inst.iterrows(): 
                st.warning(f"💰 {i['ناوی کڕیار']}: ${i['مانگانە']:,.2f} - {i['بەرواری داهاتووی قیست']}")
    
    bdays = check_birthdays()
    if bdays:
        for b in bdays: 
            st.success(f"🎂 ڕۆژی لەدایکبوونی {b} پیرۆز بێت!")
    
    st.markdown("---")
    
    menu = {
        "💰 فرۆشتن": ["📝 فرۆشتنی نوێ", "📋 لیست", "🧾 فاکتوور", "📷 سکانی بارکۆد"],
        "📦 کۆگا": ["📝 زیادکردن", "📋 لیست", "🔄 بەڕێوەبردن", "🏭 دابینکەران", "📋 داواکاری کڕین"],
        "🛡️ گەرەنتی": ["📝 تۆمارکردن", "📋 لیست", "⚠️ ئاگاداری"],
        "📊 قازانج": ["💰 خەمڵاندن", "📈 هێڵکاری", "📄 ڕاپۆرتی PDF", "💸 خەرجی"],
        "👥 کڕیاران": ["📝 زیادکردن", "📋 لیست", "⭐ خاڵ", "🌟 هەڵسەنگاندن"],
        "💳 قیست": ["📝 نوێ", "📋 لیست", "💵 پارەدان"],
        "🏷️ داشکاندن": ["📝 نوێ", "📋 لیست", "🎉 بۆنە", "📢 مارکێتینگ"],
        "👨‍💼 کارمەندان": ["📝 زیادکردن", "📋 لیست", "📊 ئاست", "🕐 ئامادەبوون", "💰 مووچە"],
        "🔧 چاککردنەوە": ["📝 تۆمارکردن", "📋 لیست"],
        "🚚 گەیاندن": ["📝 نوێ", "📋 لیست"],
        "📱 پەیام": ["📝 ناردن", "📋 مێژوو"],
        "🎫 پشتیوانی": ["📝 تیکت", "📋 تیکتەکان", "💬 چات"],
        "📅 ڕۆژمێر": ["📝 کاری نوێ", "📋 کارەکان", "📅 ڕۆژمێر"],
        "📊 داشبۆرد": ["🎯 سەرەکی", "📈 شیکاری"],
        "⚙️ ڕێکخستن": ["💾 بەکاپ", "🔔 ئاگادارییەکان"]
    
    main_choice = st.selectbox("بەشێک هەڵبژێرە:", list(menu.keys()))
    sub_choice = None
    if main_choice in menu:
        sub_choice = st.radio("ژێربەش:", menu[main_choice])
    
    st.markdown("---")
    st.markdown("### 📊 کورتە")
    
    total_sales, total_cost, total_expenses, net_profit, profit_margin = calculate_actual_profit()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("💰 فرۆشتن", f"${total_sales:,.0f}")
    c2.metric("👥 کڕیار", len(st.session_state.customers))
    c3.metric("💵 قازانج", f"${net_profit:,.0f}")

# ================== MAIN CONTENT ==================
st.markdown('<p class="main-header">📱 سیستەمی بەڕێوەبردنی دوکانی مۆبایل</p>', unsafe_allow_html=True)

try:
    # ================== 1. SALES ==================
    if main_choice == "💰 فرۆشتن" and sub_choice == "📝 فرۆشتنی نوێ":
        st.header("📝 فرۆشتنی نوێ")
        c1, c2 = st.columns([2, 1])
        with c1:
            with st.form("sale_form"):
                # Get product list from inventory
                product_list = st.session_state.inventory['ناوی کەلوپەل'].tolist() if not st.session_state.inventory.empty else []
                
                if product_list:
                    product_name = st.selectbox("📱 بەرهەم", product_list)
                    # Get product price suggestion
                    product_price = 0
                    if not st.session_state.inventory.empty:
                        product_row = st.session_state.inventory[st.session_state.inventory['ناوی کەلوپەل'] == product_name]
                        if not product_row.empty:
                            product_price = float(product_row['نرخی کڕین'].iloc[0]) * 1.3
                    
                    col1, col2 = st.columns(2)
                    price = col1.number_input("💵 نرخ ($)", min_value=0.0, step=10.0, value=product_price)
                    customer_name = col2.text_input("👤 ناوی کڕیار")
                    col3, col4 = st.columns(2)
                    discount_code = col3.text_input("🏷️ کۆدی داشکاندن")
                    employee = col4.selectbox("👨‍💼 کارمەند", [""] + list(st.session_state.employees['ناوی کارمەند'].values)) if not st.session_state.employees.empty else ""
                    
                    if discount_code:
                        final_price = apply_discount(price, discount_code)
                        if final_price != price:
                            st.success(f"💰 نرخی کۆتایی دوای داشکاندن: ${final_price:,.2f}")
                    
                    if st.form_submit_button("➕ تۆمارکردنی فرۆشتن"):
                        if product_name and price > 0 and customer_name:
                            if add_sale(product_name, price, customer_name, discount_code, employee):
                                st.success(f"✅ فرۆشتن بە سەرکەوتوویی تۆمار کرا! نرخی کۆتایی: ${apply_discount(price, discount_code):,.2f}")
                                st.balloons()
                                if st.session_state.last_sale_invoice:
                                    st.download_button(
                                        label="📄 داگرتنی فاکتوور",
                                        data=st.session_state.last_sale_invoice,
                                        file_name=f"invoice_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                        mime="application/pdf"
                                    )
                        else:
                            st.error("❌ تکایە ناوی بەرهەم، نرخ و ناوی کڕیار پڕ بکەرەوە!")
                else:
                    st.warning("⚠️ تکایە یەکەمجار کەلوپەلێک بۆ کۆگا زیاد بکە!")
        
        with c2:
            if not st.session_state.sales.empty:
                st.subheader("📈 دوایین فرۆشتنەکان")
                st.dataframe(st.session_state.sales.tail(5)[['ناوی بەرهەم', 'نرخی کۆتایی', 'ناوی کڕیار']], use_container_width=True)

    elif main_choice == "💰 فرۆشتن" and sub_choice == "📋 لیست":
        st.header("📋 لیستی فرۆشتنەکان")
        if not st.session_state.sales.empty:
            col1, col2, col3 = st.columns(3)
            with col1:
                filter_date = st.date_input("📅 بەروار", value=None)
            with col2:
                products = st.session_state.sales['ناوی بەرهەم'].unique().tolist() if 'ناوی بەرهەم' in st.session_state.sales.columns else []
                product_filter = st.multiselect("📱 بەرهەم", products)
            with col3:
                search_customer = st.text_input("👤 گەڕان بە ناوی کڕیار")
            
            filtered_sales = st.session_state.sales.copy()
            if filter_date:
                filtered_sales['date'] = pd.to_datetime(filtered_sales['کاتی فرۆشتن']).dt.date
                filtered_sales = filtered_sales[filtered_sales['date'] == filter_date]
            if product_filter:
                filtered_sales = filtered_sales[filtered_sales['ناوی بەرهەم'].isin(product_filter)]
            if search_customer:
                filtered_sales = filtered_sales[filtered_sales['ناوی کڕیار'].str.contains(search_customer, case=False, na=False)]
            
            st.dataframe(filtered_sales, use_container_width=True)
            
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("📊 ژمارەی فرۆشتن", len(filtered_sales))
            col_b.metric("💰 کۆی داهات", f"${filtered_sales['نرخی کۆتایی'].sum():,.2f}")
            col_c.metric("📈 تێکڕای فرۆشتن", f"${filtered_sales['نرخی کۆتایی'].mean():,.2f}" if not filtered_sales.empty else "$0")
            
            if st.button("📥 هەناردەکردن بۆ Excel"):
                excel_data = export_to_excel(filtered_sales, 'Sales')
                st.markdown(get_download_link(excel_data, 'sales_report.xlsx'), unsafe_allow_html=True)
        else:
            st.info("📭 هیچ فرۆشتنێک تۆمار نەکراوە")

    elif main_choice == "💰 فرۆشتن" and sub_choice == "🧾 فاکتوور":
        st.header("🧾 دروستکردنی فاکتوور")
        if not st.session_state.sales.empty:
            sale_options = [f"{row['ناوی بەرهەم']} - {row['ناوی کڕیار']} - {row['کاتی فرۆشتن']}" for _, row in st.session_state.sales.iterrows()]
            selected_sale = st.selectbox("📝 فرۆشتنی هەڵبژێرە", range(len(sale_options)), format_func=lambda x: sale_options[x])
            
            if st.button("🧾 دروستکردنی فاکتوور"):
                sale_data = st.session_state.sales.iloc[selected_sale]
                invoice_data = {
                    'date': sale_data['کاتی فرۆشتن'],
                    'customer': sale_data['ناوی کڕیار'],
                    'product': sale_data['ناوی بەرهەم'],
                    'price': sale_data['نرخ'],
                    'final_price': sale_data['نرخی کۆتایی']
                }
                invoice_pdf = generate_invoice(invoice_data)
                if invoice_pdf:
                    st.download_button(
                        label="📄 داگرتنی فاکتوور",
                        data=invoice_pdf,
                        file_name=f"invoice_{sale_data['ناوی کڕیار']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf"
                    )
                    st.success("✅ فاکتوور بە سەرکەوتوویی دروست کرا!")
                else:
                    st.error("❌ هەڵە لە دروستکردنی فاکتووردا")
        else:
            st.info("📭 سەرەتا فرۆشتنێک تۆمار بکە")

    elif main_choice == "💰 فرۆشتن" and sub_choice == "📷 سکانی بارکۆد":
        st.header("📷 سکانی بارکۆد")
        barcode = st.text_input("🔢 بارکۆد یان ناوی بەرهەم", placeholder="سکان یان بنووسە...")
        
        if barcode:
            found_product = None
            if not st.session_state.inventory.empty:
                for _, row in st.session_state.inventory.iterrows():
                    if barcode.lower() in row['ناوی کەلوپەل'].lower():
                        found_product = row
                        break
            
            if found_product is not None:
                st.success(f"✅ بەرهەم دۆزرایەوە: {found_product['ناوی کەلوپەل']}")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("📦 ژمارەی دانەکان", found_product['ژمارەی دانەکان'])
                    st.metric("💰 نرخی کڕین", f"${found_product['نرخی کڕین']:,.2f}")
                with col2:
                    suggested_price = float(found_product['نرخی کڕین']) * 1.3
                    selling_price = st.number_input("💰 نرخی فرۆشتن", min_value=0.0, value=suggested_price, step=10.0)
                    customer_name = st.text_input("👤 ناوی کڕیار")
                
                if st.button("🛒 فرۆشتنی خێرا") and customer_name:
                    if add_sale(found_product['ناوی کەلوپەل'], selling_price, customer_name):
                        st.success("✅ فرۆشتن تۆمار کرا!")
                        st.balloons()
            else:
                st.error("❌ بەرهەم نەدۆزرایەوە!")

    # ================== 2. INVENTORY ==================
    elif main_choice == "📦 کۆگا" and sub_choice == "📝 زیادکردن":
        st.header("📝 زیادکردنی کەلوپەلی نوێ")
        with st.form("inventory_form"):
            col1, col2 = st.columns(2)
            with col1:
                item_name = st.text_input("🏷️ ناوی کەلوپەل")
                quantity = st.number_input("📦 ژمارەی دانەکان", min_value=1, step=1, value=1)
            with col2:
                purchase_price = st.number_input("💰 نرخی کڕین ($)", min_value=0.0, step=1.0, value=0.0)
                min_stock = st.number_input("⚠️ کەمترین ئاستی ئاگاداری", min_value=1, value=5, step=1)
            
            if st.form_submit_button("➕ زیادکردنی کەلوپەل"):
                if item_name and quantity > 0:
                    # Check if item already exists
                    if not st.session_state.inventory.empty and item_name in st.session_state.inventory['ناوی کەلوپەل'].values:
                        idx = st.session_state.inventory[st.session_state.inventory['ناوی کەلوپەل'] == item_name].index[0]
                        new_qty = st.session_state.inventory.at[idx, 'ژمارەی دانەکان'] + quantity
                        st.session_state.inventory.at[idx, 'ژمارەی دانەکان'] = new_qty
                        st.success(f"✅ {quantity} دانە بۆ {item_name} زیاد کرا! کۆی گشتی: {new_qty}")
                    else:
                        new_item = pd.DataFrame({
                            'ناوی کەلوپەل': [item_name],
                            'ژمارەی دانەکان': [quantity],
                            'نرخی کڕین': [purchase_price],
                            'بەرواری زیادکردن': [datetime.now().strftime("%Y-%m-%d")],
                            'کەمترین ژمارە': [min_stock]
                        })
                        st.session_state.inventory = pd.concat([st.session_state.inventory, new_item], ignore_index=True)
                        st.success(f"✅ {quantity} دانە {item_name} بە سەرکەوتوویی زیاد کرا!")
                else:
                    st.error("❌ تکایە ناوی کەلوپەل و ژمارەی دانەکان پڕ بکەرەوە")

    elif main_choice == "📦 کۆگا" and sub_choice == "📋 لیست":
        st.header("📋 لیستی کەلوپەلەکان")
        if not st.session_state.inventory.empty:
            inventory_display = st.session_state.inventory.copy()
            inventory_display['کۆی بەها'] = inventory_display['ژمارەی دانەکان'] * inventory_display['نرخی کڕین']
            inventory_display['ڕەوش'] = inventory_display.apply(
                lambda x: '🔴 کەمە' if x['ژمارەی دانەکان'] < x['کەمترین ژمارە'] else '🟢 باشە', 
                axis=1
            )
            st.dataframe(inventory_display, use_container_width=True)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("📦 جۆری کەلوپەل", len(inventory_display))
            col2.metric("🔢 کۆی دانەکان", inventory_display['ژمارەی دانەکان'].sum())
            col3.metric("💰 کۆی بەها", f"${inventory_display['کۆی بەها'].sum():,.2f}")
            
            if st.button("📥 هەناردەکردن بۆ Excel"):
                excel_data = export_to_excel(inventory_display, 'Inventory')
                st.markdown(get_download_link(excel_data, 'inventory_report.xlsx'), unsafe_allow_html=True)
        else:
            st.info("📭 هیچ کەلوپەلێک لە کۆگادا نییە")

    elif main_choice == "📦 کۆگا" and sub_choice == "🔄 بەڕێوەبردن":
        st.header("🔄 بەڕێوەبردنی کۆگا")
        if not st.session_state.inventory.empty:
            item_list = st.session_state.inventory['ناوی کەلوپەل'].tolist()
            selected_item = st.selectbox("📦 کەلوپەلی هەڵبژێرە", item_list)
            
            current_item = st.session_state.inventory[st.session_state.inventory['ناوی کەلوپەل'] == selected_item].iloc[0]
            st.info(f"📊 زانیاری ئێستا:\n- ژمارەی دانەکان: {current_item['ژمارەی دانەکان']}\n- نرخی کڕین: ${current_item['نرخی کڕین']:,.2f}")
            
            col1, col2 = st.columns(2)
            with col1:
                quantity_change = st.number_input("🔄 گۆڕانی ژمارە (+/-)", value=0, step=1)
            with col2:
                new_price = st.number_input("💰 نرخی نوێ (بەجێهێشتنی 0 بۆ نەگۆڕان)", value=0.0, step=10.0)
            
            if st.button("💾 نوێکردنەوە"):
                idx = st.session_state.inventory[st.session_state.inventory['ناوی کەلوپەل'] == selected_item].index[0]
                
                if quantity_change != 0:
                    new_quantity = current_item['ژمارەی دانەکان'] + quantity_change
                    if new_quantity >= 0:
                        st.session_state.inventory.at[idx, 'ژمارەی دانەکان'] = new_quantity
                    else:
                        st.error("❌ ناتوانیت ژمارەی دانەکان بکەیت بە سالب!")
                        st.stop()
                
                if new_price > 0:
                    st.session_state.inventory.at[idx, 'نرخی کڕین'] = new_price
                
                st.success("✅ کۆگا بە سەرکەوتوویی نوێ کرایەوە!")
                st.rerun()
        else:
            st.info("📭 هیچ کەلوپەلێک لە کۆگادا نییە")

    elif main_choice == "📦 کۆگا" and sub_choice == "🏭 دابینکەران":
        st.header("🏭 بەڕێوەبردنی دابینکەران")
        
        with st.form("supplier_form"):
            col1, col2 = st.columns(2)
            with col1:
                company_name = st.text_input("🏢 ناوی کۆمپانیا")
                contact_person = st.text_input("👤 ناوی بەرپرس")
                phone = st.text_input("📞 ژمارەی مۆبایل")
            with col2:
                email = st.text_input("📧 ئیمەیڵ")
                address = st.text_area("📍 ناونیشان")
                product_type = st.text_input("📦 جۆری کەلوپەل")
            
            if st.form_submit_button("➕ زیادکردنی دابینکەر") and company_name:
                new_supplier = pd.DataFrame({
                    'ID': [f"SUP{datetime.now().strftime('%Y%m%d%H%M%S')}"],
                    'ناوی کۆمپانیا': [company_name],
                    'بەرپرس': [contact_person],
                    'مۆبایل': [phone],
                    'ئیمەیڵ': [email],
                    'ناونیشان': [address],
                    'جۆری کەلوپەل': [product_type]
                })
                st.session_state.suppliers = pd.concat([st.session_state.suppliers, new_supplier], ignore_index=True)
                st.success(f"✅ دابینکەر {company_name} زیاد کرا!")
        
        if not st.session_state.suppliers.empty:
            st.subheader("📋 لیستی دابینکەران")
            st.dataframe(st.session_state.suppliers, use_container_width=True)

    # ================== 3. WARRANTY ==================
    elif main_choice == "🛡️ گەرەنتی" and sub_choice == "📝 تۆمارکردن":
        st.header("📝 تۆمارکردنی گەرەنتی نوێ")
        with st.form("warranty_form"):
            col1, col2 = st.columns(2)
            with col1:
                customer_name = st.text_input("👤 ناوی کڕیار")
                imei = st.text_input("📱 ژمارەی IMEI (15 ژمارە)")
            with col2:
                phone_model = st.text_input("📱 جۆری مۆبایل")
                warranty_end = st.date_input("📅 بەرواری کۆتایی گەرەنتی", min_value=datetime.now().date())
            
            if st.form_submit_button("➕ تۆمارکردن") and customer_name and imei:
                if len(imei) == 15 and imei.isdigit():
                    new_warranty = pd.DataFrame({
                        'ناوی کڕیار': [customer_name],
                        'ژمارەی IMEI': [imei],
                        'بەرواری کۆتایی گەرەنتی': [warranty_end.strftime("%Y-%m-%d")],
                        'جۆری مۆبایل': [phone_model]
                    })
                    st.session_state.warranty = pd.concat([st.session_state.warranty, new_warranty], ignore_index=True)
                    st.success("✅ گەرەنتی بە سەرکەوتوویی تۆمار کرا!")
                else:
                    st.error("❌ ژمارەی IMEI دەبێت 15 ژمارە بێت!")

    elif main_choice == "🛡️ گەرەنتی" and sub_choice == "📋 لیست":
        st.header("📋 لیستی گەرەنتییەکان")
        if not st.session_state.warranty.empty:
            warranty_display = st.session_state.warranty.copy()
            warranty_display['بەرواری کۆتایی'] = pd.to_datetime(warranty_display['بەرواری کۆتایی گەرەنتی'])
            warranty_display['ڕۆژی ماوە'] = (warranty_display['بەرواری کۆتایی'] - datetime.now()).dt.days
            warranty_display['ڕەوش'] = warranty_display['ڕۆژی ماوە'].apply(
                lambda x: '🔴 بەسەرچووە' if x < 0 else ('🟠 نزیکە' if x <= 7 else ('🟡 30 ڕۆژ' if x <= 30 else '🟢 چالاکە'))
            )
            st.dataframe(warranty_display[['ناوی کڕیار', 'جۆری مۆبایل', 'ژمارەی IMEI', 'بەرواری کۆتایی گەرەنتی', 'ڕۆژی ماوە', 'ڕەوش']], use_container_width=True)
            
            if st.button("📥 هەناردەکردن"):
                excel_data = export_to_excel(warranty_display, 'Warranty')
                st.markdown(get_download_link(excel_data, 'warranty_list.xlsx'), unsafe_allow_html=True)
        else:
            st.info("📭 هیچ گەرەنتییەک تۆمار نەکراوە")

    elif main_choice == "🛡️ گەرەنتی" and sub_choice == "⚠️ ئاگاداری":
        st.header("⚠️ ئاگادارییەکانی گەرەنتی")
        expiring_warranties = check_expiring_warranty()
        if not expiring_warranties.empty:
            st.warning(f"⚠️ {len(expiring_warranties)} گەرەنتی لە 30 ڕۆژی داهاتوودا کۆتایی دێت!")
            for _, warranty in expiring_warranties.iterrows():
                days_left = (pd.to_datetime(warranty['بەرواری کۆتایی گەرەنتی']).date() - datetime.now().date()).days
                st.markdown(f"""
                <div class='customer-card'>
                    <h4>📱 {warranty['جۆری مۆبایل']}</h4>
                    <p>👤 {warranty['ناوی کڕیار']}</p>
                    <p>📅 کۆتایی: {warranty['بەرواری کۆتایی گەرەنتی']} ({days_left} ڕۆژ ماوە)</p>
                    <p>🔢 IMEI: {warranty['ژمارەی IMEI']}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ هیچ گەرەنتییەکی نزیک لە کۆتایی هاتن نییە!")

    # ================== 4. PROFIT ==================
    elif main_choice == "📊 قازانج" and sub_choice == "💰 خەمڵاندن":
        st.header("💰 خەمڵاندنی قازانج")
        
        total_sales, total_cost_sold, total_expenses, net_profit, profit_margin = calculate_actual_profit()
        
        col1, col2, col3, col4 = st.columns(4)
        col1.markdown('<div class="metric-card">', unsafe_allow_html=True)
        col1.metric("💰 کۆی فرۆشتن", f"${total_sales:,.2f}")
        col1.markdown('</div>', unsafe_allow_html=True)
        
        col2.markdown('<div class="metric-card">', unsafe_allow_html=True)
        col2.metric("💸 نرخی فرۆشراوەکان", f"${total_cost_sold:,.2f}")
        col2.markdown('</div>', unsafe_allow_html=True)
        
        col3.markdown('<div class="metric-card">', unsafe_allow_html=True)
        col3.metric("📊 کۆی خەرجی", f"${total_expenses:,.2f}")
        col3.markdown('</div>', unsafe_allow_html=True)
        
        col4.markdown('<div class="metric-card">', unsafe_allow_html=True)
        col4.metric("💰 قازانجی خالص", f"${net_profit:,.2f}", f"{profit_margin:.1f}%")
        col4.markdown('</div>', unsafe_allow_html=True)
        
        if profit_margin > 30:
            st.success("🎉 ئاستی قازانج زۆر باشە! بەردەوام بە!")
        elif profit_margin > 15:
            st.info("👍 ئاستی قازانج باشە، بەڵام دەتوانی باشتر بکەیت")
        elif profit_margin > 0:
            st.warning("⚠️ ئاستی قازانج کەمە، پێویستی بە باشترکردنە")
        else:
            st.error("❌ دوکانەکە لە زیاندا! پێویستی بە ڕێکخستنەوە")

    elif main_choice == "📊 قازانج" and sub_choice == "📈 هێڵکاری":
        st.header("📈 هێڵکاری قازانج")
        
        total_sales, total_cost_sold, total_expenses, net_profit, profit_margin = calculate_actual_profit()
        
        fig = go.Figure()
        fig.add_trace(go.Bar(name='کۆی فرۆشتن', x=['دارایی'], y=[total_sales], marker_color='#2ecc71'))
        fig.add_trace(go.Bar(name='نرخی فرۆشراوەکان', x=['دارایی'], y=[total_cost_sold], marker_color='#e74c3c'))
        fig.add_trace(go.Bar(name='کۆی خەرجی', x=['دارایی'], y=[total_expenses], marker_color='#f39c12'))
        fig.add_trace(go.Bar(name='قازانجی خالص', x=['دارایی'], y=[net_profit], marker_color='#3498db'))
        
        fig.update_layout(
            title="هێڵکاری دارایی دوکان",
            barmode='group',
            height=500,
            showlegend=True,
            font=dict(size=12)
        )
        st.plotly_chart(fig, use_container_width=True)

    elif main_choice == "📊 قازانج" and sub_choice == "📄 ڕاپۆرتی PDF":
        st.header("📄 دروستکردنی ڕاپۆرتی PDF")
        
        report_type = st.selectbox("جۆری ڕاپۆرت", ["دارایی", "فرۆشتن", "کۆگا", "گشتی"])
        
        if st.button("📄 دروستکردنی ڕاپۆرت"):
            try:
                total_sales, total_cost_sold, total_expenses, net_profit, profit_margin = calculate_actual_profit()
                
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_pdf:
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
                    pdf.set_font("Arial", "B", 20)
                    pdf.cell(0, 10, f"Mobile Shop - ڕاپۆرتی {report_type}", ln=True, align="C")
                    pdf.ln(10)
                    pdf.set_font("Arial", "", 12)
                    pdf.cell(0, 10, f"بەروار: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
                    pdf.cell(0, 10, f"کۆی فرۆشتن: ${total_sales:,.2f}", ln=True)
                    pdf.cell(0, 10, f"نرخی فرۆشراوەکان: ${total_cost_sold:,.2f}", ln=True)
                    pdf.cell(0, 10, f"کۆی خەرجی: ${total_expenses:,.2f}", ln=True)
                    pdf.cell(0, 10, f"قازانجی خالص: ${net_profit:,.2f}", ln=True)
                    pdf.cell(0, 10, f"ڕێژەی قازانج: {profit_margin:.1f}%", ln=True)
                    
                    if report_type == "فرۆشتن" and not st.session_state.sales.empty:
                        pdf.ln(5)
                        pdf.set_font("Arial", "B", 14)
                        pdf.cell(0, 10, "وردەکاری فرۆشتنەکان:", ln=True)
                        pdf.set_font("Arial", "", 10)
                        for _, sale in st.session_state.sales.tail(10).iterrows():
                            pdf.cell(0, 8, f"{sale['ناوی بەرهەم']} - ${sale['نرخی کۆتایی']:,.2f} - {sale['ناوی کڕیار']}", ln=True)
                    
                    pdf.output(tmp_pdf.name)
                    with open(tmp_pdf.name, "rb") as f:
                        pdf_data = f.read()
                    os.unlink(tmp_pdf.name)
                    
                    st.download_button(
                        label="📥 داگرتنی ڕاپۆرت",
                        data=pdf_data,
                        file_name=f"report_{report_type}_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf"
                    )
                    st.success("✅ ڕاپۆرت بە سەرکەوتوویی دروست کرا!")
            except Exception as e:
                st.error(f"هەڵە لە دروستکردنی ڕاپۆرت: {str(e)}")

    elif main_choice == "📊 قازانج" and sub_choice == "💸 خەرجی":
        st.header("💸 تۆمارکردنی خەرجی")
        with st.form("expense_form"):
            col1, col2 = st.columns(2)
            with col1:
                expense_date = st.date_input("📅 بەروار", value=datetime.now().date())
                expense_type = st.selectbox("📋 جۆری خەرجی", ["کرێ", "مووچە", "کارەبا", "ئاو", "ئینتەرنێت", "گواستنەوە", "ڕیکلام", "چاککردنەوە", "تر"])
            with col2:
                expense_amount = st.number_input("💰 بڕی خەرجی ($)", min_value=0.0, step=10.0)
                expense_note = st.text_area("📝 تێبینی")
            
            if st.form_submit_button("➕ تۆمارکردنی خەرجی"):
                if expense_amount > 0:
                    new_expense = pd.DataFrame({
                        'بەروار': [expense_date.strftime("%Y-%m-%d")],
                        'جۆر': [expense_type],
                        'بڕ': [expense_amount],
                        'تێبینی': [expense_note]
                    })
                    st.session_state.expenses = pd.concat([st.session_state.expenses, new_expense], ignore_index=True)
                    st.success(f"✅ خەرجی {expense_type} بە بڕی ${expense_amount:,.2f} تۆمار کرا!")
                else:
                    st.error("❌ تکایە بڕی خەرجی پڕ بکەرەوە")
        
        if not st.session_state.expenses.empty:
            st.subheader("📋 مێژووی خەرجییەکان")
            st.dataframe(st.session_state.expenses, use_container_width=True)
            st.metric("💰 کۆی خەرجییەکان", f"${st.session_state.expenses['بڕ'].sum():,.2f}")

    # ================== 5. CUSTOMERS ==================
    elif main_choice == "👥 کڕیاران" and sub_choice == "📝 زیادکردن":
        st.header("📝 زیادکردنی کڕیاری نوێ")
        with st.form("customer_form"):
            col1, col2 = st.columns(2)
            with col1:
                cust_name = st.text_input("👤 ناوی کڕیار")
                cust_phone = st.text_input("📞 ژمارەی مۆبایل")
                cust_email = st.text_input("📧 ئیمەیڵ")
            with col2:
                cust_address = st.text_area("📍 ناونیشان")
                cust_birthday = st.date_input("🎂 ڕێکەوتی لەدایکبوون", value=None)
            
            if st.form_submit_button("➕ زیادکردنی کڕیار") and cust_name:
                new_customer = pd.DataFrame({
                    'ناوی کڕیار': [cust_name],
                    'ژمارەی مۆبایل': [cust_phone],
                    'ئیمەیڵ': [cust_email],
                    'ناونیشان': [cust_address],
                    'بەرواری زیادکردن': [datetime.now().strftime("%Y-%m-%d")],
                    'ڕێکەوتی لەدایکبوون': [cust_birthday.strftime("%Y-%m-%d") if cust_birthday else ''],
                    'کۆی کڕین': [0],
                    'خاڵەکان': [0],
                    'ئاست': ['🥉 ئاسایی']
                })
                st.session_state.customers = pd.concat([st.session_state.customers, new_customer], ignore_index=True)
                st.success(f"✅ کڕیار {cust_name} بە سەرکەوتوویی زیاد کرا!")
                st.balloons()

    elif main_choice == "👥 کڕیاران" and sub_choice == "📋 لیست":
        st.header("📋 لیستی کڕیاران")
        if not st.session_state.customers.empty:
            st.dataframe(st.session_state.customers, use_container_width=True)
            if st.button("📥 هەناردەکردن"):
                excel_data = export_to_excel(st.session_state.customers, 'Customers')
                st.markdown(get_download_link(excel_data, 'customers_list.xlsx'), unsafe_allow_html=True)
        else:
            st.info("📭 هیچ کڕیارێک تۆمار نەکراوە")

    elif main_choice == "👥 کڕیاران" and sub_choice == "⭐ خاڵ":
        st.header("⭐ خاڵەکانی کڕیاران")
        if not st.session_state.customers.empty:
            loyalty_df = st.session_state.customers[['ناوی کڕیار', 'کۆی کڕین', 'خاڵەکان', 'ئاست']].copy()
            loyalty_df = loyalty_df.sort_values('خاڵەکان', ascending=False)
            st.dataframe(loyalty_df, use_container_width=True)
            
            top_customer = loyalty_df.iloc[0] if not loyalty_df.empty else None
            if top_customer is not None:
                st.success(f"🏆 کڕیاری هەفتە: {top_customer['ناوی کڕیار']} - {top_customer['خاڵەکان']} خاڵ!")
            
            # Redeem points
            st.subheader("💎 گۆڕینی خاڵ بە دیاری")
            selected_customer = st.selectbox("کڕیاری هەڵبژێرە", loyalty_df['ناوی کڕیار'].tolist())
            points = loyalty_df[loyalty_df['ناوی کڕیار'] == selected_customer]['خاڵەکان'].iloc[0]
            st.info(f"خاڵەکانی {selected_customer}: {points}")
            
            if points >= 100:
                if st.button("🎁 گۆڕینی 100 خاڵ بە $10 تخفیف"):
                    idx = st.session_state.customers[st.session_state.customers['ناوی کڕیار'] == selected_customer].index[0]
                    st.session_state.customers.at[idx, 'خاڵەکان'] = points - 100
                    st.success("✅ 100 خاڵ گۆڕدرا بە $10 تخفیف!")
                    st.rerun()
        else:
            st.info("📭 هیچ کڕیارێک تۆمار نەکراوە")

    elif main_choice == "👥 کڕیاران" and sub_choice == "🌟 هەڵسەنگاندن":
        st.header("🌟 هەڵسەنگاندنی بەرهەم")
        
        if not st.session_state.sales.empty:
            col1, col2 = st.columns(2)
            with col1:
                products = st.session_state.sales['ناوی بەرهەم'].unique().tolist()
                selected_product = st.selectbox("📱 بەرهەمی هەڵبژێرە", products)
            with col2:
                rating = st.slider("⭐ ئەستێرە", 1, 5, 5)
                review_text = st.text_area("📝 سەرنج")
            
            if st.button("💾 تۆمارکردنی هەڵسەنگاندن"):
                new_review = pd.DataFrame({
                    'کڕیار': ['میوان'],
                    'بەرهەم': [selected_product],
                    'ئەستێرە': [rating],
                    'سەرنج': [review_text],
                    'بەروار': [datetime.now().strftime("%Y-%m-%d")]
                })
                st.session_state.reviews = pd.concat([st.session_state.reviews, new_review], ignore_index=True)
                st.success("✅ سوپاس بۆ هەڵسەنگاندن!")
        
        if not st.session_state.reviews.empty:
            st.subheader("📋 هەڵسەنگاندنەکان")
            st.dataframe(st.session_state.reviews, use_container_width=True)
            
            avg_rating = st.session_state.reviews['ئەستێرە'].mean()
            st.metric("📊 تێکڕای هەڵسەنگاندن", f"{avg_rating:.1f}/5")

    # ================== 6. INSTALLMENTS ==================
    elif main_choice == "💳 قیست" and sub_choice == "📝 نوێ":
        st.header("📝 قیستی نوێ")
        with st.form("installment_form"):
            col1, col2 = st.columns(2)
            with col1:
                customer_name = st.text_input("👤 ناوی کڕیار")
                product = st.text_input("📱 بەرهەم")
                total_price = st.number_input("💰 کۆی نرخ ($)", min_value=0.0, step=50.0)
            with col2:
                down_payment = st.number_input("💵 پارەی پێشەکی ($)", min_value=0.0, step=50.0)
                months = st.number_input("📅 ماوە (مانگ)", min_value=1, max_value=24, value=6)
            
            if st.form_submit_button("➕ تۆمارکردنی قیست"):
                if customer_name and product and total_price > 0:
                    if add_installment(customer_name, product, total_price, down_payment, months):
                        st.success(f"✅ قیست بۆ {customer_name} تۆمار کرا!")
                        remaining = total_price - down_payment
                        monthly = remaining / months
                        st.info(f"💳 مانگانە: ${monthly:,.2f} بۆ {months} مانگ")
                    else:
                        st.error("❌ هەڵە لە تۆمارکردنی قیست")
                else:
                    st.error("❌ تکایە هەموو خانەکان پڕ بکەرەوە")

    elif main_choice == "💳 قیست" and sub_choice == "📋 لیست":
        st.header("📋 لیستی قیستەکان")
        if not st.session_state.installments.empty:
            installments_display = st.session_state.installments.copy()
            st.dataframe(installments_display, use_container_width=True)
            
            active = len(installments_display[installments_display['ڕەوش'] == 'چالاکە'])
            completed = len(installments_display[installments_display['ڕەوش'] == 'تەواو'])
            total_remaining = installments_display['پارەی ماوە'].sum() if 'پارەی ماوە' in installments_display.columns else 0
            
            col1, col2, col3 = st.columns(3)
            col1.metric("🟢 قیستی چالاک", active)
            col2.metric("✅ قیستی تەواو", completed)
            col3.metric("💰 پارەی ماوە", f"${total_remaining:,.2f}")
        else:
            st.info("📭 هیچ قیستێک تۆمار نەکراوە")

    elif main_choice == "💳 قیست" and sub_choice == "💵 پارەدان":
        st.header("💵 پارەدانی قیست")
        if not st.session_state.installments.empty:
            active_installments = st.session_state.installments[st.session_state.installments['ڕەوش'] == 'چالاکە']
            if not active_installments.empty:
                installment_options = [f"{row['ID']} - {row['ناوی کڕیار']} - {row['بەرهەم']} - ماوە: ${row['پارەی ماوە']:,.2f}" for _, row in active_installments.iterrows()]
                selected = st.selectbox("قیستی هەڵبژێرە", range(len(installment_options)), format_func=lambda x: installment_options[x])
                
                selected_row = active_installments.iloc[selected]
                st.info(f"💰 پارەی ماوە: ${selected_row['پارەی ماوە']:,.2f}")
                st.info(f"📅 مانگانە: ${selected_row['مانگانە']:,.2f}")
                
                payment_amount = st.number_input("💵 بڕی پارەدان ($)", min_value=0.0, max_value=float(selected_row['پارەی ماوە']), step=10.0)
                
                if st.button("✅ تۆمارکردنی پارەدان") and payment_amount > 0:
                    if add_installment_payment(selected_row['ID'], payment_amount):
                        st.success(f"✅ ${payment_amount:,.2f} وەرگیرا!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ هەڵە لە تۆمارکردنی پارەدان")
            else:
                st.info("📭 هیچ قیستێکی چالاک نییە")
        else:
            st.info("📭 هیچ قیستێک تۆمار نەکراوە")

    # ================== 7. EMPLOYEES ==================
    elif main_choice == "👨‍💼 کارمەندان" and sub_choice == "📝 زیادکردن":
        st.header("📝 زیادکردنی کارمەندی نوێ")
        with st.form("employee_form"):
            col1, col2 = st.columns(2)
            with col1:
                emp_name = st.text_input("👤 ناوی کارمەند")
                emp_position = st.selectbox("📋 پلە", ["فرۆشیار", "بەڕێوەبەر", "تەکنیکار", "پاککەرەوە"])
            with col2:
                emp_salary = st.number_input("💰 مووچە ($)", min_value=0.0, step=50.0)
                emp_start_date = st.date_input("📅 بەرواری دەستبەکاربوون", value=datetime.now().date())
            
            if st.form_submit_button("➕ زیادکردنی کارمەند") and emp_name:
                new_employee = pd.DataFrame({
                    'ناوی کارمەند': [emp_name],
                    'پلە': [emp_position],
                    'مووچە': [emp_salary],
                    'بەرواری دەستبەکاربوون': [emp_start_date.strftime("%Y-%m-%d")],
                    'ژمارەی فرۆشتن': [0],
                    'کۆی فرۆشتن': [0],
                    'پاداشت': [0]
                })
                st.session_state.employees = pd.concat([st.session_state.employees, new_employee], ignore_index=True)
                st.success(f"✅ کارمەند {emp_name} زیاد کرا!")
        
        if not st.session_state.employees.empty:
            st.subheader("📋 لیستی کارمەندان")
            st.dataframe(st.session_state.employees, use_container_width=True)

    elif main_choice == "👨‍💼 کارمەندان" and sub_choice == "📊 ئاست":
        st.header("📊 ئاستی کارمەندان")
        if not st.session_state.employees.empty:
            employees_display = st.session_state.employees.copy()
            employees_display['پاداشت (کۆمسیۆن)'] = employees_display['کۆی فرۆشتن'] * 0.02
            employees_display = employees_display.sort_values('کۆی فرۆشتن', ascending=False)
            
            fig = px.bar(employees_display, x='ناوی کارمەند', y='کۆی فرۆشتن', title="فرۆشتن بەپێی کارمەند", color='کۆی فرۆشتن', text_auto=True)
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(employees_display[['ناوی کارمەند', 'پلە', 'ژمارەی فرۆشتن', 'کۆی فرۆشتن', 'پاداشت (کۆمسیۆن)']], use_container_width=True)
        else:
            st.info("📭 هیچ کارمەندێک تۆمار نەکراوە")

    # ================== 8. DASHBOARD ==================
    elif main_choice == "📊 داشبۆرد" and sub_choice == "🎯 سەرەکی":
        st.header("🎯 داشبۆردی سەرەکی")
        
        today = datetime.now().date()
        today_sales = 0
        if not st.session_state.sales.empty:
            sales_today = st.session_state.sales.copy()
            sales_today['date'] = pd.to_datetime(sales_today['کاتی فرۆشتن']).dt.date
            today_sales = sales_today[sales_today['date'] == today]['نرخی کۆتایی'].sum()
        
        total_sales, total_cost_sold, total_expenses, net_profit, profit_margin = calculate_actual_profit()
        
        col1, col2, col3, col4 = st.columns(4)
        col1.markdown('<div class="metric-card">', unsafe_allow_html=True)
        col1.metric("💰 فرۆشتی ئەمڕۆ", f"${today_sales:,.2f}")
        col1.markdown('</div>', unsafe_allow_html=True)
        
        col2.markdown('<div class="metric-card">', unsafe_allow_html=True)
        col2.metric("📦 کەلوپەلی کەم", len(check_low_stock()))
        col2.markdown('</div>', unsafe_allow_html=True)
        
        active_repairs = len(st.session_state.repairs[st.session_state.repairs['ڕەوش'] == 'چاوەڕوان']) if not st.session_state.repairs.empty else 0
        col3.markdown('<div class="metric-card">', unsafe_allow_html=True)
        col3.metric("🔧 چاککردنەوە", active_repairs)
        col3.markdown('</div>', unsafe_allow_html=True)
        
        open_tickets = len(st.session_state.tickets[st.session_state.tickets['ڕەوش'] == 'کراوە']) if not st.session_state.tickets.empty else 0
        col4.markdown('<div class="metric-card">', unsafe_allow_html=True)
        col4.metric("🎫 تیکتی کراوە", open_tickets)
        col4.markdown('</div>', unsafe_allow_html=True)

    elif main_choice == "📊 داشبۆرد" and sub_choice == "📈 شیکاری":
        st.header("📈 شیکاری پێشکەوتوو")
        
        tab1, tab2 = st.tabs(["📊 ئامارەکان", "📈 هێڵکاری"])
        
        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                satisfaction = st.session_state.reviews['ئەستێرە'].mean() * 20 if not st.session_state.reviews.empty else 85
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=satisfaction,
                    title={'text': "ڕەزامەندی کڕیاران (%)"},
                    gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#667eea"}}
                ))
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                total_sales, _, _, _, _ = calculate_actual_profit()
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=total_sales,
                    title={'text': "کۆی فرۆشتن ($)"},
                    gauge={'axis': {'range': [0, max(total_sales * 1.5, 10000)]}, 'bar': {'color': "#667eea"}}
                ))
                st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            if not st.session_state.sales.empty:
                sales_monthly = st.session_state.sales.copy()
                sales_monthly['month'] = pd.to_datetime(sales_monthly['کاتی فرۆشتن']).dt.month
                monthly_sales = sales_monthly.groupby('month')['نرخی کۆتایی'].sum()
                
                fig = px.line(
                    x=monthly_sales.index, 
                    y=monthly_sales.values,
                    labels={'x': 'مانگ', 'y': 'فرۆشتن ($)'},
                    title="هێڵکاری فرۆشتن بەپێی مانگ"
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            if not st.session_state.employees.empty:
                emp_sales = st.session_state.employees[st.session_state.employees['کۆی فرۆشتن'] > 0]
                if not emp_sales.empty:
                    fig = px.pie(emp_sales, values='کۆی فرۆشتن', names='ناوی کارمەند', title="بەشی فرۆشتن بەپێی کارمەند")
                    st.plotly_chart(fig, use_container_width=True)

    # ================== 9. SETTINGS ==================
    elif main_choice == "⚙️ ڕێکخستن" and sub_choice == "💾 بەکاپ":
        st.header("💾 بەکاپ و گەڕاندنەوە")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📤 دروستکردنی بەکاپ")
            if st.button("📥 دروستکردنی بەکاپ"):
                json_backup, pickle_backup = backup_data()
                st.download_button(
                    label="📥 داگرتنی بەکاپ (JSON)",
                    data=json_backup,
                    file_name=f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
                st.download_button(
                    label="📥 داگرتنی بەکاپ (Pickle)",
                    data=pickle_backup,
                    file_name=f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl",
                    mime="application/octet-stream"
                )
                st.success("✅ بەکاپ بە سەرکەوتوویی دروست کرا!")
        
        with col2:
            st.subheader("🔄 گەڕاندنەوەی بەکاپ")
            uploaded_file = st.file_uploader("فایلی بەکاپ هەڵبژێرە", type=['json', 'pkl'])
            if uploaded_file and st.button("🔄 گەڕاندنەوە"):
                if restore_data(uploaded_file):
                    st.success("✅ داتا بە سەرکەوتوویی گەڕێندرایەوە!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ هەڵە لە گەڕاندنەوەی بەکاپدا")

    elif main_choice == "⚙️ ڕێکخستن" and sub_choice == "🔔 ئاگادارییەکان":
        st.header("🔔 ئاگادارییە زیرەکەکان")
        
        notifications = []
        
        for _, item in check_low_stock().iterrows():
            notifications.append(('error', f"📦 کەلوپەلی {item['ناوی کەلوپەل']} کەمە! (ماوە: {item['ژمارەی دانەکان']} دانە)"))
        
        for _, warranty in check_expiring_warranty().iterrows():
            days_left = (pd.to_datetime(warranty['بەرواری کۆتایی گەرەنتی']).date() - datetime.now().date()).days
            notifications.append(('warning', f"⏰ گەرەنتی {warranty['ناوی کڕیار']} لە {days_left} ڕۆژی دیکەدا کۆتایی دێت!"))
        
        for _, installment in check_upcoming_installments().iterrows():
            notifications.append(('info', f"💳 قیستی {installment['ناوی کڕیار']} نزیکە! بڕ: ${installment['مانگانە']:,.2f}"))
        
        for birthday in check_birthdays():
            notifications.append(('success', f"🎂 ڕۆژی لەدایکبوونی {birthday} پیرۆز بێت!"))
        
        if notifications:
            for notif_type, message in notifications:
                if notif_type == 'error':
                    st.error(message)
                elif notif_type == 'warning':
                    st.warning(message)
                elif notif_type == 'info':
                    st.info(message)
                elif notif_type == 'success':
                    st.success(message)
        else:
            st.success("✅ هیچ ئاگادارییەک نییە! هەموو شتێک لە ڕێگای خۆیدایە.")

    # ================== OTHER SECTIONS (Quick Info) ==================
    else:
        st.info(f"""
        ### 👋 بەخێربێیت بۆ سیستەمی بەڕێوەبردنی دوکانی مۆبایل!
        
        **ڕێنمایی خێرا:**
        - 🏠 لە شریتی لای ڕاستەوە بەشێک هەڵبژێرە
        - 💰 بۆ فرۆشتن، بەشی "فرۆشتن" هەڵبژێرە
        - 📦 بۆ بەڕێوەبردنی کۆگا، بەشی "کۆگا" هەڵبژێرە
        - 👥 بۆ بەڕێوەبردنی کڕیاران، بەشی "کڕیاران" هەڵبژێرە
        
        **تایبەتمەندییەکان:**
        - ✅ 15+ بەشی جیاواز
        - ✅ پشتیوانی فاکتوور و ڕاپۆرت
        - ✅ سیستەمی خاڵ و پاداشت
        - ✅ سیستەمی قیست (قسط)
        - ✅ بەکاپ و گەڕاندنەوە
        - ✅ ڕاپۆرتەکانی PDF و Excel
        
        📌 دەتوانیت بە دوگمەی "داتای نموونەیی" لە شریتی لاتەنیشتەوە، داتای تاقیکردنەوە دروست بکەیت.
        """)

except Exception as e:
    st.error(f"هەڵەیەک ڕوویدا: {str(e)}")
    st.info("تکایە پەڕەکە نوێ بکەرەوە یان پەیوەندی بە پشتیوانییەوە بکەن.")

# ================== FOOTER ==================
st.markdown("---")
st.markdown("""
    <div class="footer">
        <h3>📱 سیستەمی بەڕێوەبردنی دوکانی مۆبایل</h3>
        <p>© 2024 | 15+ بەشی جیاواز | ڕاپۆرتی زیرەک | پشتیوانی ڕاستەوخۆ</p>
        <p>🔧 وەشانی 2.0 - تەواو پاڵپشتیکراو بۆ Streamlit</p>
    </div>
""", unsafe_allow_html=True)
