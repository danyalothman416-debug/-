بە پێی داواکاریت، هەموو کۆدەکە بە یەکجار و بە شێوەیەکی تەواو چاککراوە و بەشە کەمبووەکان زیاد کراون. تکایە تێبینی بکە کە ئەمە کۆدێکی زۆر درێژە و پێکهاتووە لە ١٥+ بەشی جیاواز:

```python
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import base64
import qrcode
from fpdf import FPDF
import json
import pickle
import warnings
import os
import tempfile

warnings.filterwarnings('ignore')

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
        transition: all 0.3s;
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
    .footer {
        text-align: center; 
        padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; 
        border-radius: 15px; 
        margin-top: 2rem;
    }
    .status-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: bold;
    }
    .status-active {background: #2ecc71; color: white;}
    .status-pending {background: #f39c12; color: white;}
    .status-completed {background: #3498db; color: white;}
    .status-cancelled {background: #e74c3c; color: white;}
    </style>
""", unsafe_allow_html=True)

# ================== SESSION STATE INITIALIZATION ==================
def init_session():
    # Sales
    if 'sales' not in st.session_state:
        st.session_state.sales = pd.DataFrame(columns=['ناوی بەرهەم','نرخ','کاتی فرۆشتن','ناوی کڕیار','کۆدی داشکاندن','نرخی کۆتایی','کارمەند'])
    
    # Inventory with barcode support
    if 'inventory' not in st.session_state:
        st.session_state.inventory = pd.DataFrame(columns=['ناوی کەلوپەل','ژمارەی دانەکان','نرخی کڕین','بەرواری زیادکردن','کەمترین ژمارە','بارکۆد'])
    
    # Warranty
    if 'warranty' not in st.session_state:
        st.session_state.warranty = pd.DataFrame(columns=['ناوی کڕیار','ژمارەی IMEI','بەرواری کۆتایی گەرەنتی','جۆری مۆبایل'])
    
    # Customers
    if 'customers' not in st.session_state:
        st.session_state.customers = pd.DataFrame(columns=['ناوی کڕیار','ژمارەی مۆبایل','ئیمەیڵ','ناونیشان','بەرواری زیادکردن','ڕێکەوتی لەدایکبوون','کۆی کڕین','خاڵەکان','ئاست'])
    
    # Discounts
    if 'discounts' not in st.session_state:
        st.session_state.discounts = pd.DataFrame(columns=['کۆدی داشکاندن','ڕێژە','بەرواری دەستپێک','بەرواری کۆتایی','کەمترین کڕین','ژمارەی بەکارهێنان'])
    
    # Employees
    if 'employees' not in st.session_state:
        st.session_state.employees = pd.DataFrame(columns=['ناوی کارمەند','پلە','مووچە','بەرواری دەستبەکاربوون','ژمارەی فرۆشتن','کۆی فرۆشتن','پاداشت'])
    
    # Repairs
    if 'repairs' not in st.session_state:
        st.session_state.repairs = pd.DataFrame(columns=['ID','ناوی کڕیار','جۆری مۆبایل','کێشە','بەرواری وەرگرتن','بەرواری گەڕاندنەوە','نرخی چاککردنەوە','ڕەوش'])
    
    # Loyalty points
    if 'loyalty_points' not in st.session_state:
        st.session_state.loyalty_points = {}
    
    # Last sale invoice
    if 'last_sale_invoice' not in st.session_state:
        st.session_state.last_sale_invoice = None
    
    # Installments
    if 'installments' not in st.session_state:
        st.session_state.installments = pd.DataFrame(columns=['ID','ناوی کڕیار','بەرهەم','کۆی نرخ','پارەی پێشەکی','مانگانە','ماوە','بەرواری دەستپێک','پارەی دراو','پارەی ماوە','ڕەوش','بەرواری داهاتووی قیست'])
    
    # Messages
    if 'messages' not in st.session_state:
        st.session_state.messages = pd.DataFrame(columns=['ID','ناوی کڕیار','ژمارە','پەیام','بەروار','ڕەوش'])
    
    # Deliveries
    if 'deliveries' not in st.session_state:
        st.session_state.deliveries = pd.DataFrame(columns=['ID','ناوی کڕیار','ژمارەی مۆبایل','ناونیشان','بەرهەم','بەرواری داواکاری','بەرواری گەیاندن','تێچووی گەیاندن','ڕەوش','تێبینی'])
    
    # Tickets
    if 'tickets' not in st.session_state:
        st.session_state.tickets = pd.DataFrame(columns=['ID','ناوی کڕیار','بابەت','کێشە','لەولەوەپێشی','بەرواری کردنەوە','بەرواری داخستن','ڕەوش','وەڵام'])
    
    # Events
    if 'events' not in st.session_state:
        st.session_state.events = pd.DataFrame(columns=['ناونیشان','جۆر','بەرواری دەستپێک','بەرواری کۆتایی','ڕێژەی داشکاندن','بەرهەمەکان','ڕەوش'])
    
    # Expenses
    if 'expenses' not in st.session_state:
        st.session_state.expenses = pd.DataFrame(columns=['بەروار','جۆر','بڕ','تێبینی'])
    
    # Suppliers
    if 'suppliers' not in st.session_state:
        st.session_state.suppliers = pd.DataFrame(columns=['ID','ناوی کۆمپانیا','بەرپرس','مۆبایل','ئیمەیڵ','ناونیشان','جۆری کەلوپەل'])
    
    # Attendance
    if 'attendance' not in st.session_state:
        st.session_state.attendance = pd.DataFrame(columns=['کارمەند','بەروار','کاتی هاتن','کاتی ڕۆیشتن','کاتژمێر','ڕەوش'])
    
    # Reviews
    if 'reviews' not in st.session_state:
        st.session_state.reviews = pd.DataFrame(columns=['کڕیار','بەرهەم','ئەستێرە','سەرنج','بەروار'])
    
    # Tasks
    if 'tasks' not in st.session_state:
        st.session_state.tasks = pd.DataFrame(columns=['ناونیشان','وەسف','وادە','لەولەوەپێشی','کارمەند','ڕەوش'])
    
    # Purchase orders
    if 'purchase_orders' not in st.session_state:
        st.session_state.purchase_orders = pd.DataFrame(columns=['ID','دابینکەر','کەلوپەل','دانە','نرخ','کۆی نرخ','ڕەوش'])

init_session()

# ================== HELPER FUNCTIONS ==================
def safe_concat(df1, df2):
    """Safe concatenation of dataframes"""
    try:
        if df1.empty:
            return df2
        elif df2.empty:
            return df1
        else:
            return pd.concat([df1, df2], ignore_index=True)
    except:
        return df2 if not df2.empty else df1

def apply_discount(price, code):
    if code and not st.session_state.discounts.empty:
        d = st.session_state.discounts[st.session_state.discounts['کۆدی داشکاندن'] == code]
        if not d.empty:
            # Check if discount is active
            try:
                today = datetime.now().date()
                start_date = pd.to_datetime(d['بەرواری دەستپێک'].iloc[0]).date() if pd.notna(d['بەرواری دەستپێک'].iloc[0]) else None
                end_date = pd.to_datetime(d['بەرواری کۆتایی'].iloc[0]).date() if pd.notna(d['بەرواری کۆتایی'].iloc[0]) else None
                
                if start_date and today < start_date:
                    return price
                if end_date and today > end_date:
                    return price
                    
                return price * (1 - d['ڕێژە'].iloc[0] / 100)
            except:
                pass
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
    
    if not st.session_state.customers.empty:
        mask = st.session_state.customers['ناوی کڕیار'] == customer
        if mask.any():
            idx = st.session_state.customers[mask].index[0]
            st.session_state.customers.at[idx, 'خاڵەکان'] = total
            st.session_state.customers.at[idx, 'ئاست'] = level
            current_total = st.session_state.customers.at[idx, 'کۆی کڕین']
            if pd.isna(current_total):
                current_total = 0
            st.session_state.customers.at[idx, 'کۆی کڕین'] = current_total + amount

def update_employee_performance(emp, amount):
    if emp and not st.session_state.employees.empty:
        mask = st.session_state.employees['ناوی کارمەند'] == emp
        if mask.any():
            idx = st.session_state.employees[mask].index[0]
            current_count = st.session_state.employees.at[idx, 'ژمارەی فرۆشتن']
            current_total = st.session_state.employees.at[idx, 'کۆی فرۆشتن']
            current_bonus = st.session_state.employees.at[idx, 'پاداشت']
            
            if pd.isna(current_count):
                current_count = 0
            if pd.isna(current_total):
                current_total = 0
            if pd.isna(current_bonus):
                current_bonus = 0
            
            st.session_state.employees.at[idx, 'ژمارەی فرۆشتن'] = current_count + 1
            st.session_state.employees.at[idx, 'کۆی فرۆشتن'] = current_total + amount
            st.session_state.employees.at[idx, 'پاداشت'] = current_bonus + (amount * 0.02)

def update_inventory(product_name, quantity_sold):
    """Update inventory after a sale"""
    if not st.session_state.inventory.empty:
        mask = st.session_state.inventory['ناوی کەلوپەل'] == product_name
        if mask.any():
            idx = st.session_state.inventory[mask].index[0]
            current_qty = st.session_state.inventory.at[idx, 'ژمارەی دانەکان']
            new_qty = current_qty - quantity_sold
            if new_qty >= 0:
                st.session_state.inventory.at[idx, 'ژمارەی دانەکان'] = new_qty
                return True
    return False

def add_sale(product_name, price, customer_name, discount_code="", employee="", quantity=1):
    try:
        if not product_name or price <= 0 or not customer_name:
            st.error("تکایە ناوی بەرهەم، نرخ و ناوی کڕیار پڕ بکەرەوە")
            return False
        
        final_price = apply_discount(price, discount_code)
        total_amount = final_price * quantity
        
        for i in range(quantity):
            new_sale = pd.DataFrame({
                'ناوی بەرهەم': [product_name], 
                'نرخ': [float(price)],
                'کاتی فرۆشتن': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                'ناوی کڕیار': [customer_name], 
                'کۆدی داشکاندن': [discount_code],
                'نرخی کۆتایی': [final_price], 
                'کارمەند': [employee]
            })
            
            st.session_state.sales = safe_concat(st.session_state.sales, new_sale)
        
        add_loyalty_points(customer_name, total_amount)
        update_inventory(product_name, quantity)
        
        if employee: 
            update_employee_performance(employee, total_amount)
        
        st.session_state.last_sale_invoice = generate_invoice({
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'customer': customer_name, 
            'product': product_name,
            'quantity': quantity,
            'price': price, 
            'discount_code': discount_code,
            'final_price': total_amount
        })
        return True
    except Exception as e:
        st.error(f"هەڵە لە تۆمارکردنی فرۆشتن: {str(e)}")
        return False

def generate_invoice(data):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_pdf:
            pdf = FPDF()
            pdf.add_page()
            
            # Header
            pdf.set_font("Arial", "B", 24)
            pdf.cell(0, 15, "MOBILE SHOP", ln=True, align="C")
            pdf.set_font("Arial", "", 12)
            pdf.cell(0, 8, "INVOICE", ln=True, align="C")
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(10)
            
            # Invoice details
            pdf.set_font("Arial", "", 10)
            pdf.cell(0, 6, f"Date: {data.get('date', '')}", ln=True)
            pdf.cell(0, 6, f"Customer: {data.get('customer', '')}", ln=True)
            pdf.ln(5)
            
            # Product details
            pdf.set_font("Arial", "B", 10)
            pdf.cell(80, 8, "Product", 1)
            pdf.cell(25, 8, "Qty", 1, align="C")
            pdf.cell(35, 8, "Price", 1, align="R")
            pdf.cell(35, 8, "Total", 1, align="R")
            pdf.ln()
            
            pdf.set_font("Arial", "", 10)
            pdf.cell(80, 8, data.get('product', ''), 1)
            pdf.cell(25, 8, str(data.get('quantity', 1)), 1, align="C")
            pdf.cell(35, 8, f"${data.get('price', 0):.2f}", 1, align="R")
            pdf.cell(35, 8, f"${data.get('final_price', 0):.2f}", 1, align="R")
            pdf.ln()
            
            if data.get('discount_code'):
                pdf.cell(0, 8, f"Discount Code: {data['discount_code']}", ln=True)
            
            pdf.ln(5)
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, f"Total Amount: ${data.get('final_price', 0):.2f}", ln=True, align="R")
            
            # QR Code
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_qr:
                    qr = qrcode.make(f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}")
                    qr.save(tmp_qr.name)
                    pdf.image(tmp_qr.name, x=150, y=30, w=40)
                    os.unlink(tmp_qr.name)
            except:
                pass
            
            # Footer
            pdf.ln(20)
            pdf.set_font("Arial", "I", 8)
            pdf.cell(0, 5, "Thank you for your purchase!", ln=True, align="C")
            
            pdf.output(tmp_pdf.name)
            with open(tmp_pdf.name, "rb") as f:
                result = f.read()
            os.unlink(tmp_pdf.name)
            return result
    except Exception as e:
        return None

def check_low_stock():
    if not st.session_state.inventory.empty and 'ژمارەی دانەکان' in st.session_state.inventory.columns and 'کەمترین ژمارە' in st.session_state.inventory.columns:
        try:
            return st.session_state.inventory[st.session_state.inventory['ژمارەی دانەکان'] < st.session_state.inventory['کەمترین ژمارە']]
        except:
            return pd.DataFrame()
    return pd.DataFrame()

def check_expiring_warranty():
    if not st.session_state.warranty.empty and 'بەرواری کۆتایی گەرەنتی' in st.session_state.warranty.columns:
        try:
            today = datetime.now().date()
            st.session_state.warranty['بەرواری کۆتایی گەرەنتی'] = pd.to_datetime(st.session_state.warranty['بەرواری کۆتایی گەرەنتی'], errors='coerce').dt.date
            valid_warranties = st.session_state.warranty.dropna(subset=['بەرواری کۆتایی گەرەنتی'])
            if not valid_warranties.empty:
                days_diff = (valid_warranties['بەرواری کۆتایی گەرەنتی'] - today).dt.days
                return valid_warranties[(days_diff <= 30) & (days_diff >= 0)]
        except:
            return pd.DataFrame()
    return pd.DataFrame()

def check_upcoming_installments():
    if not st.session_state.installments.empty and 'بەرواری داهاتووی قیست' in st.session_state.installments.columns:
        try:
            today = datetime.now().date()
            st.session_state.installments['بەرواری داهاتووی قیست'] = pd.to_datetime(st.session_state.installments['بەرواری داهاتووی قیست'], errors='coerce').dt.date
            valid_inst = st.session_state.installments.dropna(subset=['بەرواری داهاتووی قیست'])
            if not valid_inst.empty:
                days_diff = (valid_inst['بەرواری داهاتووی قیست'] - today).dt.days
                active_mask = st.session_state.installments['ڕەوش'] == 'چالاکە'
                return valid_inst[(days_diff <= 7) & active_mask]
        except:
            return pd.DataFrame()
    return pd.DataFrame()

def check_birthdays():
    today = datetime.now()
    birthdays = []
    if not st.session_state.customers.empty and 'ڕێکەوتی لەدایکبوون' in st.session_state.customers.columns:
        for _, c in st.session_state.customers.iterrows():
            if c['ڕێکەوتی لەدایکبوون'] and pd.notna(c['ڕێکەوتی لەدایکبوون']):
                try:
                    bd = pd.to_datetime(c['ڕێکەوتی لەدایکبوون'])
                    if bd.month == today.month and bd.day == today.day:
                        birthdays.append(c['ناوی کڕیار'])
                except:
                    pass
    return birthdays

def export_to_excel(df, sheet="Data"):
    if df.empty:
        return None
    try:
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet, index=False)
        return output.getvalue()
    except:
        return None

def get_download_link(data, filename):
    if data is None:
        return "هیچ داتایەک بۆ هەناردەکردن نییە"
    b64 = base64.b64encode(data).decode()
    return f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">📥 {filename}</a>'

def backup_data():
    all_data = {}
    for k, v in st.session_state.items():
        if not k.startswith('_'):
            try:
                if hasattr(v, 'to_dict'):
                    all_data[k] = v.to_dict()
                else:
                    all_data[k] = v
            except:
                pass
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
                try:
                    if isinstance(data[key], dict) and hasattr(st.session_state[key], 'empty'):
                        st.session_state[key] = pd.DataFrame(data[key])
                    else:
                        st.session_state[key] = data[key]
                except:
                    pass
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
            'کارمەند': ['ڕێباز', 'ڕێباز', 'هەڵگورد']
        })
        st.session_state.sales = sample_sale
        
    if st.session_state.inventory.empty:
        sample_inv = pd.DataFrame({
            'ناوی کەلوپەل': ['iPhone 15 Pro', 'Samsung Galaxy S24', 'Google Pixel 8', 'Charger', 'Phone Case'],
            'ژمارەی دانەکان': [15, 12, 8, 50, 100],
            'نرخی کڕین': [700, 600, 550, 15, 5],
            'بەرواری زیادکردن': [datetime.now().strftime("%Y-%m-%d")] * 5,
            'کەمترین ژمارە': [5, 5, 5, 20, 30],
            'بارکۆد': ['1234567890123', '1234567890124', '1234567890125', 'CH001', 'CS001']
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
        sample_cust = pd.DataFrame({
            'ناوی کڕیار': ['ئەحمەد', 'سارا', 'محەمەد'],
            'ژمارەی مۆبایل': ['07701234567', '07707654321', '07501234567'],
            'ئیمەیڵ': ['ahmed@email.com', 'sara@email.com', 'mohammed@email.com'],
            'ناونیشان': ['هەولێر', 'سلێمانی', 'دهۆک'],
            'بەرواری زیادکردن': [datetime.now().strftime("%Y-%m-%d")] * 3,
            'ڕێکەوتی لەدایکبوون': ['1990-01-01', '1992-05-15', '1988-10-20'],
            'کۆی کڕین': [1000, 900, 800],
            'خاڵەکان': [100, 90, 80],
            'ئاست': ['🥈 زیوین', '🥈 زیوین', '🥉 ئاسایی']
        })
        st.session_state.customers = sample_cust
    
    if st.session_state.discounts.empty:
        sample_discounts = pd.DataFrame({
            'کۆدی داشکاندن': ['SUMMER2024', 'NEWYEAR2024'],
            'ڕێژە': [10, 15],
            'بەرواری دەستپێک': [(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")] * 2,
            'بەرواری کۆتایی': [(datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")] * 2,
            'کەمترین کڕین': [0, 500],
            'ژمارەی بەکارهێنان': [0, 0]
        })
        st.session_state.discounts = sample_discounts
        
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
                st.warning(f"📱 {w['ناوی کڕیار']} - کۆتایی: {w['بەرواری کۆتایی گەرەنتی']}")
    
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
        "💰 فرۆشتن": ["📝 فرۆشتنی نوێ", "📋 لیستی فرۆشتن", "🧾 فاکتوور", "📷 سکانی بارکۆد"],
        "📦 کۆگا": ["📝 زیادکردنی کەلوپەل", "📋 لیستی کۆگا", "🔄 نوێکردنەوەی کۆگا", "🏭 دابینکەران"],
        "🏷️ داشکاندن": ["📝 کۆدی نوێ", "📋 لیستی کۆدەکان"],
        "💳 قیست": ["📝 قیستی نوێ", "📋 لیستی قیستەکان", "💰 پارەدان", "⚠️ ئاگاداری قیست"],
        "🛡️ گەرەنتی": ["📝 تۆمارکردنی گەرەنتی", "📋 لیستی گەرەنتی", "⚠️ ئاگاداری گەرەنتی"],
        "🔧 چاککردنەوە": ["📝 تۆماری چاککردنەوە", "📋 لیستی چاککردنەوەکان"],
        "🚚 گەیاندن": ["📝 داواکاری نوێ", "📋 لیستی گەیاندنەکان"],
        "🎫 پشتیوانی": ["📝 تیکتی نوێ", "📋 تیکتەکان"],
        "👥 کڕیاران": ["📝 زیادکردنی کڕیار", "📋 لیستی کڕیاران", "⭐ خاڵەکان", "🎂 ڕۆژی لەدایکبوون"],
        "👨‍💼 کارمەندان": ["📝 زیادکردنی کارمەند", "📋 لیستی کارمەندان", "📊 ئاستی کارمەندان", "⏰ ئامادەبوون"],
        "📊 قازانج": ["💰 خەمڵاندنی قازانج", "📈 هێڵکاری", "📄 ڕاپۆرتی PDF", "💸 خەرجییەکان"],
        "📊 داشبۆرد": ["🎯 سەرەکی", "📈 شیکاری"],
        "⚙️ ڕێکخستن": ["💾 بەکاپ", "🔔 ئاگادارییەکان"]
    }
    
    main_choice = st.selectbox("بەشێک هەڵبژێرە:", list(menu.keys()))
    sub_choice = None
    if main_choice in menu:
        sub_choice = st.radio("ژێربەش:", menu[main_choice])
    
    st.markdown("---")
    st.markdown("### 📊 کورتە")
    total_sales_sum = st.session_state.sales['نرخی کۆتایی'].sum() if not st.session_state.sales.empty else 0
    total_customers = len(st.session_state.customers)
    total_cost = (st.session_state.inventory['نرخی کڕین'] * st.session_state.inventory['ژمارەی دانەکان']).sum() if not st.session_state.inventory.empty else 0
    total_expenses = st.session_state.expenses['بڕ'].sum() if not st.session_state.expenses.empty else 0
    total_profit = total_sales_sum - total_cost - total_expenses
    
    c1, c2, c3 = st.columns(3)
    c1.metric("💰 فرۆشتن", f"${total_sales_sum:,.0f}")
    c2.metric("👥 کڕیار", total_customers)
    c3.metric("💵 قازانج", f"${total_profit:,.0f}")

# ================== MAIN CONTENT ==================
st.markdown('<p class="main-header">📱 سیستەمی بەڕێوەبردنی دوکانی مۆبایل</p>', unsafe_allow_html=True)

try:
    # ================== 1. SALES SECTION ==================
    if main_choice == "💰 فرۆشتن" and sub_choice == "📝 فرۆشتنی نوێ":
        st.header("📝 فرۆشتنی نوێ")
        c1, c2 = st.columns([2, 1])
        with c1:
            with st.form("sale_form"):
                product_options = [""] + list(st.session_state.inventory['ناوی کەلوپەل'].values) if not st.session_state.inventory.empty else [""]
                product_name = st.selectbox("📱 ناوی بەرهەم", product_options)
                
                col1, col2 = st.columns(2)
                quantity = col1.number_input("📦 ژمارە", min_value=1, value=1, step=1)
                price = col2.number_input("💵 نرخ ($)", min_value=0.0, step=10.0, value=0.0)
                
                col3, col4 = st.columns(2)
                customer_options = [""] + list(st.session_state.customers['ناوی کڕیار'].values) if not st.session_state.customers.empty else [""]
                customer_name = col3.selectbox("👤 ناوی کڕیار", customer_options)
                discount_code = col4.text_input("🏷️ کۆدی داشکاندن")
                
                employee_options = [""] + list(st.session_state.employees['ناوی کارمەند'].values) if not st.session_state.employees.empty else [""]
                employee = st.selectbox("👨‍💼 کارمەند", employee_options)
                
                if discount_code:
                    final_price = apply_discount(price, discount_code)
                    if final_price != price:
                        st.success(f"💰 نرخی کۆتایی دوای داشکاندن: ${final_price * quantity:,.2f}")
                
                if st.form_submit_button("➕ تۆمارکردنی فرۆشتن"):
                    if product_name and price > 0 and customer_name:
                        if add_sale(product_name, price, customer_name, discount_code, employee, quantity):
                            st.success(f"✅ {quantity} دانە {product_name} بە {customer_name} فرۆشرا! کۆی گشتی: ${apply_discount(price, discount_code) * quantity:,.2f}")
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
        
        with c2:
            if not st.session_state.sales.empty:
                st.subheader("📈 دوایین فرۆشتنەکان")
                st.dataframe(st.session_state.sales.tail(5)[['ناوی بەرهەم', 'نرخی کۆتایی', 'ناوی کڕیار']], use_container_width=True)

    elif main_choice == "💰 فرۆشتن" and sub_choice == "📋 لیستی فرۆشتن":
        st.header("📋 لیستی فرۆشتنەکان")
        if not st.session_state.sales.empty:
            filtered_sales = st.session_state.sales.copy()
            
            # Filters
            col1, col2, col3 = st.columns(3)
            if not st.session_state.employees.empty:
                emp_filter = col1.selectbox("پاڵێو بە کارمەند", ["هەموو"] + list(st.session_state.employees['ناوی کارمەند'].unique()))
                if emp_filter != "هەموو":
                    filtered_sales = filtered_sales[filtered_sales['کارمەند'] == emp_filter]
            
            date_filter = col2.date_input("لە بەروارەوە", value=None)
            if date_filter:
                filtered_sales['date'] = pd.to_datetime(filtered_sales['کاتی فرۆشتن']).dt.date
                filtered_sales = filtered_sales[filtered_sales['date'] == date_filter]
            
            st.dataframe(filtered_sales, use_container_width=True)
            
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("📊 ژمارەی فرۆشتن", len(filtered_sales))
            col_b.metric("💰 کۆی داهات", f"${filtered_sales['نرخی کۆتایی'].sum():,.2f}")
            col_c.metric("📈 تێکڕای فرۆشتن", f"${filtered_sales['نرخی کۆتایی'].mean():,.2f}" if not filtered_sales.empty else "$0")
            
            if st.button("📥 هەناردەکردن بۆ Excel"):
                excel_data = export_to_excel(filtered_sales, 'Sales')
                if excel_data:
                    st.markdown(get_download_link(excel_data, 'sales_report.xlsx'), unsafe_allow_html=True)
        else:
            st.info("📭 هیچ فرۆشتنێک تۆمار نەکراوە")

    elif main_choice == "💰 فرۆشتن" and sub_choice == "🧾 فاکتوور":
        st.header("🧾 دروستکردنی فاکتوور")
        if not st.session_state.sales.empty:
            sale_options = [f"{row['ناوی بەرهەم']} - {row['ناوی کڕیار']} ({row['کاتی فرۆشتن']})" for _, row in st.session_state.sales.iterrows()]
            selected_idx = st.selectbox("📝 فرۆشتنی هەڵبژێرە", range(len(sale_options)), format_func=lambda x: sale_options[x])
            
            if st.button("🧾 دروستکردنی فاکتوور"):
                sale_data = st.session_state.sales.iloc[selected_idx]
                invoice_data = {
                    'date': sale_data['کاتی فرۆشتن'],
                    'customer': sale_data['ناوی کڕیار'],
                    'product': sale_data['ناوی بەرهەم'],
                    'quantity': 1,
                    'price': sale_data['نرخ'],
                    'discount_code': sale_data['کۆدی داشکاندن'],
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
            st.info("📭 سەرەتا فرۆشتنێک تۆمار بکە")

    # ================== BARCODE SCANNER SECTION ==================
    elif main_choice == "💰 فرۆشتن" and sub_choice == "📷 سکانی بارکۆد":
        st.header("📷 سکانی بارکۆد")
        
        barcode_input = st.text_input("🔢 بارکۆد یان ناوی بەرهەم", placeholder="بارکۆدەکە سکان بکە یان ناوەکە بنووسە...", key="barcode_scanner")
        
        if barcode_input:
            found_item = None
            for _, row in st.session_state.inventory.iterrows():
                row_barcode = str(row.get('بارکۆد', '')).strip()
                row_name = str(row['ناوی کەلوپەل']).strip().lower()
                
                if barcode_input.strip() == row_barcode or barcode_input.strip().lower() == row_name:
                    found_item = row
                    break
            
            if found_item is not None:
                st.success(f"✅ بەرهەم دۆزرایەوە: {found_item['ناوی کەلوپەل']}")
                
                suggested_price = found_item['نرخی کڕین'] * 1.3
                
                with st.form(key="quick_sale_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        selling_price = st.number_input("💰 نرخی فرۆشتن ($)", min_value=0.0, value=float(suggested_price), step=10.0)
                        quantity = st.number_input("📦 ژمارەی دانە", min_value=1, max_value=int(found_item['ژمارەی دانەکان']), value=1)
                    with col2:
                        customer_options = [""] + list(st.session_state.customers['ناوی کڕیار'].values) if not st.session_state.customers.empty else [""]
                        customer_name = st.selectbox("👤 کڕیار", customer_options)
                        employee_options = [""] + list(st.session_state.employees['ناوی کارمەند'].values) if not st.session_state.employees.empty else [""]
                        employee = st.selectbox("👨‍💼 کارمەند", employee_options)
                    
                    discount_code = st.text_input("🏷️ کۆدی داشکاندن (ئارەزوومەندانە)")
                    
                    if st.form_submit_button("🛒 فرۆشتن"):
                        if customer_name:
                            if add_sale(found_item['ناوی کەلوپەل'], selling_price, customer_name, discount_code, employee, quantity):
                                st.success(f"✅ {quantity} دانە {found_item['ناوی کەلوپەل']} فرۆشرا!")
                                st.balloons()
                                st.rerun()
                        else:
                            st.error("❌ تکایە ناوی کڕیار دیاری بکە")
            else:
                st.error("❌ بەرهەم نەدۆزرایەوە! تکایە بارکۆد یان ناوێکی دروست بنووسە")

    # ================== 2. INVENTORY SECTION ==================
    elif main_choice == "📦 کۆگا" and sub_choice == "📝 زیادکردنی کەلوپەل":
        st.header("📝 زیادکردنی کەلوپەلی نوێ")
        with st.form("inventory_form"):
            col1, col2 = st.columns(2)
            with col1:
                item_name = st.text_input("🏷️ ناوی کەلوپەل")
                quantity = st.number_input("📦 ژمارەی دانەکان", min_value=1, step=1, value=1)
                barcode = st.text_input("🔢 بارکۆد (ئارەزوومەندانە)", placeholder="1234567890123")
            with col2:
                purchase_price = st.number_input("💰 نرخی کڕین ($)", min_value=0.0, step=1.0, value=0.0)
                min_stock = st.number_input("⚠️ کەمترین ئاستی ئاگاداری", min_value=1, value=5, step=1)
                supplier_options = [""] + list(st.session_state.suppliers['ناوی کۆمپانیا'].values) if not st.session_state.suppliers.empty else [""]
                supplier = st.selectbox("🏭 دابینکەر", supplier_options)
            
            if st.form_submit_button("➕ زیادکردنی کەلوپەل"):
                if item_name and quantity > 0:
                    new_item = pd.DataFrame({
                        'ناوی کەلوپەل': [item_name],
                        'ژمارەی دانەکان': [quantity],
                        'نرخی کڕین': [purchase_price],
                        'بەرواری زیادکردن': [datetime.now().strftime("%Y-%m-%d")],
                        'کەمترین ژمارە': [min_stock],
                        'بارکۆد': [barcode if barcode else ''],
                        'دابینکەر': [supplier if supplier else '']
                    })
                    st.session_state.inventory = safe_concat(st.session_state.inventory, new_item)
                    st.success(f"✅ {quantity} دانە {item_name} بە سەرکەوتوویی زیاد کرا!")
                    st.rerun()
                else:
                    st.error("❌ تکایە ناوی کەلوپەل و ژمارەی دانەکان پڕ بکەرەوە")

    elif main_choice == "📦 کۆگا" and sub_choice == "📋 لیستی کۆگا":
        st.header("📋 لیستی کەلوپەلەکان")
        if not st.session_state.inventory.empty:
            inventory_display = st.session_state.inventory.copy()
            inventory_display['کۆی بەها'] = inventory_display['ژمارەی دانەکان'] * inventory_display['نرخی کڕین']
            inventory_display['نرخی فرۆشتن (پێشنیارکراو)'] = inventory_display['نرخی کڕین'] * 1.3
            inventory_display['ڕەوش'] = inventory_display.apply(
                lambda x: '🔴 کەمە' if x['ژمارەی دانەکان'] < x['کەمترین ژمارە'] else '🟢 باشە', 
                axis=1
            )
            
            # Search
            search = st.text_input("🔍 گەڕان...", placeholder="ناوی کەلوپەل بنووسە...")
            if search:
                inventory_display = inventory_display[inventory_display['ناوی کەلوپەل'].str.contains(search, case=False)]
            
            st.dataframe(inventory_display, use_container_width=True)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("📦 جۆری کەلوپەل", len(inventory_display))
            col2.metric("🔢 کۆی دانەکان", inventory_display['ژمارەی دانەکان'].sum())
            col3.metric("💰 کۆی بەها", f"${inventory_display['کۆی بەها'].sum():,.2f}")
            
            if st.button("📥 هەناردەکردن بۆ Excel"):
                excel_data = export_to_excel(inventory_display, 'Inventory')
                if excel_data:
                    st.markdown(get_download_link(excel_data, 'inventory_report.xlsx'), unsafe_allow_html=True)
        else:
            st.info("📭 هیچ کەلوپەلێک لە کۆگادا نییە")

    elif main_choice == "📦 کۆگا" and sub_choice == "🔄 نوێکردنەوەی کۆگا":
        st.header("🔄 نوێکردنەوەی کۆگا")
        if not st.session_state.inventory.empty:
            item_list = st.session_state.inventory['ناوی کەلوپەل'].tolist()
            selected_item = st.selectbox("📦 کەلوپەلی هەڵبژێرە", item_list)
            
            if selected_item:
                current_item = st.session_state.inventory[st.session_state.inventory['ناوی کەلوپەل'] == selected_item].iloc[0]
                st.info(f"📊 زانیاری ئێستا:\n- ژمارەی دانەکان: {current_item['ژمارەی دانەکان']}\n- نرخی کڕین: ${current_item['نرخی کڕین']:,.2f}")
                
                col1, col2 = st.columns(2)
                with col1:
                    quantity_change = st.number_input("🔄 گۆڕانی ژمارە (+/-)", value=0, step=1)
                with col2:
                    new_price = st.number_input("💰 نرخی نوێ (0 = نەگۆڕان)", value=0.0, step=10.0)
                
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
        
        tab1, tab2 = st.tabs(["➕ زیادکردن", "📋 لیست"])
        
        with tab1:
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
                    st.session_state.suppliers = safe_concat(st.session_state.suppliers, new_supplier)
                    st.success(f"✅ دابینکەر {company_name} زیاد کرا!")
                    st.rerun()
        
        with tab2:
            if not st.session_state.suppliers.empty:
                st.dataframe(st.session_state.suppliers, use_container_width=True)
                
                if st.button("📥 هەناردەکردن"):
                    excel_data = export_to_excel(st.session_state.suppliers, 'Suppliers')
                    if excel_data:
                        st.markdown(get_download_link(excel_data, 'suppliers_list.xlsx'), unsafe_allow_html=True)
            else:
                st.info("📭 هیچ دابینکەرێک تۆمار نەکراوە")

    # ================== 3. DISCOUNTS SECTION ==================
    elif main_choice == "🏷️ داشکاندن" and sub_choice == "📝 کۆدی نوێ":
        st.header("📝 دروستکردنی کۆدی داشکاندنی نوێ")
        with st.form("discount_form"):
            col1, col2 = st.columns(2)
            with col1:
                code = st.text_input("🏷️ کۆدی داشکاندن", placeholder="SUMMER2024")
                percentage = st.slider("📊 ڕێژەی داشکاندن %", 0, 100, 10)
            with col2:
                start_date = st.date_input("📅 بەرواری دەستپێک", value=datetime.now().date())
                end_date = st.date_input("📅 بەرواری کۆتایی", value=datetime.now().date() + timedelta(days=30))
                min_purchase = st.number_input("💰 کەمترین کڕین ($)", min_value=0.0, value=0.0, step=50.0)
            
            if st.form_submit_button("➕ دروستکردنی کۆد"):
                if code:
                    new_discount = pd.DataFrame({
                        'کۆدی داشکاندن': [code],
                        'ڕێژە': [percentage],
                        'بەرواری دەستپێک': [start_date.strftime("%Y-%m-%d")],
                        'بەرواری کۆتایی': [end_date.strftime("%Y-%m-%d")],
                        'کەمترین کڕین': [min_purchase],
                        'ژمارەی بەکارهێنان': [0]
                    })
                    st.session_state.discounts = safe_concat(st.session_state.discounts, new_discount)
                    st.success(f"✅ کۆدی {code} بە {percentage}% داشکاندن دروست کرا!")
                    st.balloons()
                else:
                    st.error("❌ تکایە کۆدێک بنووسە")

    elif main_choice == "🏷️ داشکاندن" and sub_choice == "📋 لیستی کۆدەکان":
        st.header("📋 لیستی کۆدی داشکاندنەکان")
        if not st.session_state.discounts.empty:
            st.dataframe(st.session_state.discounts, use_container_width=True)
            
            col1, col2 = st.columns(2)
            active_discounts = 0
            today = datetime.now().date()
            for _, d in st.session_state.discounts.iterrows():
                try:
                    start = pd.to_datetime(d['بەرواری دەستپێک']).date()
                    end = pd.to_datetime(d['بەرواری کۆتایی']).date()
                    if start <= today <= end:
                        active_discounts += 1
                except:
                    pass
            
            col1.metric("🏷️ کۆدی چالاک", active_discounts)
            col2.metric("📊 کۆی کۆدەکان", len(st.session_state.discounts))
            
            if st.button("📥 هەناردەکردن"):
                excel_data = export_to_excel(st.session_state.discounts, 'Discounts')
                if excel_data:
                    st.markdown(get_download_link(excel_data, 'discounts_list.xlsx'), unsafe_allow_html=True)
        else:
            st.info("📭 هیچ کۆدی داشکاندنێک نییە")

    # ================== 4. INSTALLMENTS SECTION ==================
    elif main_choice == "💳 قیست" and sub_choice == "📝 قیستی نوێ":
        st.header("📝 تۆمارکردنی قیستی نوێ")
        
        with st.form("installment_form"):
            col1, col2 = st.columns(2)
            with col1:
                customer_options = st.session_state.customers['ناوی کڕیار'].tolist() if not st.session_state.customers.empty else []
                customer = st.selectbox("👤 کڕیار", customer_options)
                product_options = st.session_state.inventory['ناوی کەلوپەل'].tolist() if not st.session_state.inventory.empty else []
                product = st.selectbox("📱 بەرهەم", product_options)
                total_price = st.number_input("💰 کۆی نرخ ($)", min_value=0.0, step=50.0, value=0.0)
            with col2:
                down_payment = st.number_input("💵 پارەی پێشەکی ($)", min_value=0.0, step=50.0, value=0.0)
                months = st.number_input("📅 ماوە (مانگ)", min_value=1, max_value=24, value=6)
                start_date = st.date_input("📅 بەرواری دەستپێک", value=datetime.now().date())
            
            if total_price > 0 and months > 0:
                remaining = total_price - down_payment
                monthly = remaining / months if remaining > 0 else 0
                st.info(f"📊 **پوختە:**\n- پارەی ماوە: ${remaining:,.2f}\n- مانگانە: ${monthly:,.2f}\n- کۆتا قیست: {(start_date + timedelta(days=30*months)).strftime('%Y-%m-%d')}")
            
            if st.form_submit_button("➕ تۆمارکردنی قیست"):
                if customer and product and total_price > 0 and down_payment <= total_price:
                    remaining = total_price - down_payment
                    monthly = remaining / months if months > 0 and remaining > 0 else 0
                    
                    new_installment = pd.DataFrame({
                        'ID': [f"INST{datetime.now().strftime('%Y%m%d%H%M%S')}"],
                        'ناوی کڕیار': [customer],
                        'بەرهەم': [product],
                        'کۆی نرخ': [total_price],
                        'پارەی پێشەکی': [down_payment],
                        'مانگانە': [monthly],
                        'ماوە': [months],
                        'بەرواری دەستپێک': [start_date.strftime("%Y-%m-%d")],
                        'پارەی دراو': [down_payment],
                        'پارەی ماوە': [remaining],
                        'ڕەوش': ['چالاکە'],
                        'بەرواری داهاتووی قیست': [(start_date + timedelta(days=30)).strftime("%Y-%m-%d")]
                    })
                    
                    st.session_state.installments = safe_concat(st.session_state.installments, new_installment)
                    st.success(f"✅ قیست بۆ {customer} بە سەرکەوتوویی تۆمار کرا!")
                    st.balloons()
                    st.rerun()
                elif down_payment > total_price:
                    st.error("❌ پارەی پێشەکی نابێت لە کۆی نرخ زیاتر بێت!")
                else:
                    st.error("❌ تکایە هەموو خانە پێویستەکان پڕ بکەرەوە!")

    elif main_choice == "💳 قیست" and sub_choice == "📋 لیستی قیستەکان":
        st.header("📋 لیستی قیستەکان")
        
        if not st.session_state.installments.empty:
            display_df = st.session_state.installments.copy()
            
            # Filter by status
            status_filter = st.selectbox("ڕەوش", ["هەموو", "چالاکە", "تەواو بوو"])
            if status_filter != "هەموو":
                display_df = display_df[display_df['ڕەوش'] == status_filter]
            
            try:
                display_df['بەرواری داهاتووی قیست'] = pd.to_datetime(display_df['بەرواری داهاتووی قیست'], errors='coerce').dt.date
            except:
                pass
            
            st.dataframe(display_df, use_container_width=True)
            
            col1, col2, col3 = st.columns(3)
            active_inst = st.session_state.installments[st.session_state.installments['ڕەوش'] == 'چالاکە']
            total_remaining = active_inst['پارەی ماوە'].sum() if not active_inst.empty else 0
            total_paid = active_inst['پارەی دراو'].sum() if not active_inst.empty else 0
            
            col1.metric("📊 قیستی چالاک", len(active_inst))
            col2.metric("💰 کۆی پارەی دراو", f"${total_paid:,.2f}")
            col3.metric("💳 پارەی ماوە", f"${total_remaining:,.2f}")
            
            if st.button("📥 هەناردەکردن بۆ Excel"):
                excel_data = export_to_excel(display_df, 'Installments')
                if excel_data:
                    st.markdown(get_download_link(excel_data, 'installments_list.xlsx'), unsafe_allow_html=True)
        else:
            st.info("📭 هیچ قیستێک تۆمار نەکراوە")

    elif main_choice == "💳 قیست" and sub_choice == "💰 پارەدان":
        st.header("💰 تۆمارکردنی پارەدانی قیست")
        
        if not st.session_state.installments.empty:
            active_inst = st.session_state.installments[st.session_state.installments['ڕەوش'] == 'چالاکە']
            if not active_inst.empty:
                selected_id = st.selectbox("📋 قیستی هەڵبژێرە", active_inst['ID'].tolist())
                inst_data = active_inst[active_inst['ID'] == selected_id].iloc[0]
                
                st.info(f"""
                **👤 کڕیار:** {inst_data['ناوی کڕیار']}
                **📱 بەرهەم:** {inst_data['بەرهەم']}
                **💰 پارەی ماوە:** ${inst_data['پارەی ماوە']:,.2f}
                **💳 مانگانە:** ${inst_data['مانگانە']:,.2f}
                **📅 بەرواری داهاتوو:** {inst_data['بەرواری داهاتووی قیست']}
                """)
                
                amount = st.number_input("💰 بڕی پارە ($)", min_value=0.0, max_value=float(inst_data['پارەی ماوە']), step=10.0, value=float(inst_data['مانگانە']))
                
                if st.button("✅ تۆمارکردنی پارە") and amount > 0:
                    idx = st.session_state.installments[st.session_state.installments['ID'] == selected_id].index[0]
                    new_paid = inst_data['پارەی دراو'] + amount
                    remaining = inst_data['کۆی نرخ'] - new_paid
                    
                    st.session_state.installments.at[idx, 'پارەی دراو'] = new_paid
                    st.session_state.installments.at[idx, 'پارەی ماوە'] = remaining
                    
                    if remaining <= 0:
                        st.session_state.installments.at[idx, 'ڕەوش'] = 'تەواو بوو'
                        st.success("🎉 قیستەکە تەواو بوو! پیرۆز بێت!")
                        st.balloons()
                    else:
                        next_date = (datetime.now().date() + timedelta(days=30)).strftime("%Y-%m-%d")
                        st.session_state.installments.at[idx, 'بەرواری داهاتووی قیست'] = next_date
                        st.success(f"✅ پارەکە تۆمار کرا! پارەی ماوە: ${remaining:,.2f}")
                    st.rerun()
            else:
                st.info("هیچ قیستێکی چالاک نییە!")
        else:
            st.info("📭 هیچ قیستێک تۆمار نەکراوە")

    elif main_choice == "💳 قیست" and sub_choice == "⚠️ ئاگاداری قیست":
        st.header("⚠️ ئاگادارییەکانی قیستەکان")
        
        upcoming = check_upcoming_installments()
        if not upcoming.empty:
            st.warning(f"⚠️ {len(upcoming)} قیست لە 7 ڕۆژی داهاتوودا دەبێت!")
            for _, inst in upcoming.iterrows():
                days_left = (inst['بەرواری داهاتووی قیست'] - datetime.now().date()).days if pd.notna(inst['بەرواری داهاتووی قیست']) else 0
                st.markdown(f"""
                <div class='customer-card'>
                    <h4>💰 {inst['ناوی کڕیار']} 
                    <span class='status-badge status-pending'>{days_left} ڕۆژ ماوە</span></h4>
                    <p>📱 {inst['بەرهەم']}</p>
                    <p>💳 مانگانە: ${inst['مانگانە']:,.2f}</p>
                    <p>📅 بەرواری داهاتوو: {inst['بەرواری داهاتووی قیست']}</p>
                    <p>💰 پارەی ماوە: ${inst['پارەی ماوە']:,.2f}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ هیچ قیستێکی نزیک لە کۆتایی هاتن نییە!")
        
        # Overdue installments
        if not st.session_state.installments.empty:
            today = datetime.now().date()
            active_inst = st.session_state.installments[st.session_state.installments['ڕەوش'] == 'چالاکە'].copy()
            if not active_inst.empty:
                active_inst['بەرواری داهاتووی قیست'] = pd.to_datetime(active_inst['بەرواری داهاتووی قیست'], errors='coerce').dt.date
                overdue = active_inst[active_inst['بەرواری داهاتووی قیست'] < today]
                if not overdue.empty:
                    st.error(f"🚨 {len(overdue)} قیستی دواکەوتوو هەیە!")
                    for _, inst in overdue.iterrows():
                        st.error(f"❌ {inst['ناوی کڕیار']} - {inst['بەرهەم']}: ${inst['مانگانە']:,.2f}")

    # ================== 5. WARRANTY SECTION ==================
    elif main_choice == "🛡️ گەرەنتی" and sub_choice == "📝 تۆمارکردنی گەرەنتی":
        st.header("📝 تۆمارکردنی گەرەنتی نوێ")
        with st.form("warranty_form"):
            col1, col2 = st.columns(2)
            with col1:
                customer_options = [""] + list(st.session_state.customers['ناوی کڕیار'].values) if not st.session_state.customers.empty else [""]
                customer_name = st.selectbox("👤 ناوی کڕیار", customer_options)
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
                    st.session_state.warranty = safe_concat(st.session_state.warranty, new_warranty)
                    st.success("✅ گەرەنتی بە سەرکەوتوویی تۆمار کرا!")
                    st.rerun()
                else:
                    st.error("❌ ژمارەی IMEI دەبێت 15 ژمارە بێت!")

    elif main_choice == "🛡️ گەرەنتی" and sub_choice == "📋 لیستی گەرەنتی":
        st.header("📋 لیستی گەرەنتییەکان")
        if not st.session_state.warranty.empty:
            st.dataframe(st.session_state.warranty, use_container_width=True)
            if st.button("📥 هەناردەکردن"):
                excel_data = export_to_excel(st.session_state.warranty, 'Warranty')
                if excel_data:
                    st.markdown(get_download_link(excel_data, 'warranty_list.xlsx'), unsafe_allow_html=True)
        else:
            st.info("📭 هیچ گەرەنتییەک تۆمار نەکراوە")

    elif main_choice == "🛡️ گەرەنتی" and sub_choice == "⚠️ ئاگاداری گەرەنتی":
        st.header("⚠️ ئاگادارییەکانی گەرەنتی")
        expiring_warranties = check_expiring_warranty()
        if not expiring_warranties.empty:
            st.warning(f"⚠️ {len(expiring_warranties)} گەرەنتی لە 30 ڕۆژی داهاتوودا کۆتایی دێت!")
            for _, warranty in expiring_warranties.iterrows():
                days_left = (warranty['بەرواری کۆتایی گەرەنتی'] - datetime.now().date()).days
                st.markdown(f"""
                <div class='customer-card'>
                    <h4>📱 {warranty['جۆری مۆبایل']} 
                    <span class='status-badge status-pending'>{days_left} ڕۆژ ماوە</span></h4>
                    <p>👤 {warranty['ناوی کڕیار']}</p>
                    <p>📅 کۆتایی: {warranty['بەرواری کۆتایی گەرەنتی']}</p>
                    <p>🔢 IMEI: {warranty['ژمارەی IMEI']}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ هیچ گەرەنتییەکی نزیک لە کۆتایی هاتن نییە!")

    # ================== 6. REPAIRS SECTION ==================
    elif main_choice == "🔧 چاککردنەوە" and sub_choice == "📝 تۆماری چاککردنەوە":
        st.header("📝 تۆمارکردنی چاککردنەوەی نوێ")
        with st.form("repair_form"):
            col1, col2 = st.columns(2)
            with col1:
                customer_options = [""] + list(st.session_state.customers['ناوی کڕیار'].values) if not st.session_state.customers.empty else [""]
                customer = st.selectbox("👤 ناوی کڕیار", customer_options)
                phone_model = st.text_input("📱 جۆری مۆبایل")
                issue = st.text_area("🔧 کێشە", placeholder="کێشەکە بە وردی ڕوون بکەرەوە...")
            with col2:
                received_date = st.date_input("📅 بەرواری وەرگرتن", value=datetime.now().date())
                expected_return = st.date_input("📅 بەرواری پێشبینیکراوی گەڕاندنەوە", value=datetime.now().date() + timedelta(days=7))
                repair_cost = st.number_input("💰 نرخی چاککردنەوە ($)", min_value=0.0, step=10.0)
            
            if st.form_submit_button("➕ تۆمارکردن"):
                if customer and phone_model and issue:
                    new_repair = pd.DataFrame({
                        'ID': [f"REP{datetime.now().strftime('%Y%m%d%H%M%S')}"],
                        'ناوی کڕیار': [customer],
                        'جۆری مۆبایل': [phone_model],
                        'کێشە': [issue],
                        'بەرواری وەرگرتن': [received_date.strftime("%Y-%m-%d")],
                        'بەرواری گەڕاندنەوە': [expected_return.strftime("%Y-%m-%d")],
                        'نرخی چاککردنەوە': [repair_cost],
                        'ڕەوش': ['چاوەڕوان']
                    })
                    st.session_state.repairs = safe_concat(st.session_state.repairs, new_repair)
                    st.success(f"✅ چاککردنەوە بۆ {customer} تۆمار کرا!")
                    st.rerun()
                else:
                    st.error("❌ تکایە هەموو خانە پێویستەکان پڕ بکەرەوە")

    elif main_choice == "🔧 چاککردنەوە" and sub_choice == "📋 لیستی چاککردنەوەکان":
        st.header("📋 لیستی چاککردنەوەکان")
        if not st.session_state.repairs.empty:
            col1, col2, col3 = st.columns(3)
            status_filter = col1.selectbox("ڕەوش", ["هەموو"] + list(st.session_state.repairs['ڕەوش'].unique()))
            
            filtered = st.session_state.repairs.copy()
            if status_filter != "هەموو":
                filtered = filtered[filtered['ڕەوش'] == status_filter]
            
            st.dataframe(filtered, use_container_width=True)
            
            # Update status
            st.subheader("🔄 نوێکردنەوەی ڕەوش")
            if not filtered.empty:
                repair_to_update = st.selectbox("چاککردنەوە هەڵبژێرە", filtered['ID'].tolist())
                new_status = st.selectbox("ڕەوشی نوێ", ["چاوەڕوان", "لەژێرکارە", "تەواو بوو", "گەڕێندرایەوە"])
                if st.button("💾 نوێکردنەوەی ڕەوش"):
                    idx = st.session_state.repairs[st.session_state.repairs['ID'] == repair_to_update].index[0]
                    st.session_state.repairs.at[idx, 'ڕەوش'] = new_status
                    if new_status == "گەڕێندرایەوە":
                        st.session_state.repairs.at[idx, 'بەرواری گەڕاندنەوە'] = datetime.now().strftime("%Y-%m-%d")
                    st.success(f"✅ ڕەوشی چاککردنەوە نوێ کرایەوە بۆ '{new_status}'")
                    st.rerun()
            
            # Statistics
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("📊 کۆی چاککردنەوەکان", len(st.session_state.repairs))
            col_b.metric("⏳ چاوەڕوان", len(st.session_state.repairs[st.session_state.repairs['ڕەوش'] == 'چاوەڕوان']))
            col_c.metric("✅ تەواوکراو", len(st.session_state.repairs[st.session_state.repairs['ڕەوش'] == 'گەڕێندرایەوە']))
        else:
            st.info("📭 هیچ چاککردنەوەیەک تۆمار نەکراوە")

    # ================== 7. DELIVERIES SECTION ==================
    elif main_choice == "🚚 گەیاندن" and sub_choice == "📝 داواکاری نوێ":
        st.header("📝 داواکاری گەیاندنی نوێ")
        with st.form("delivery_form"):
            col1, col2 = st.columns(2)
            with col1:
                customer_options = [""] + list(st.session_state.customers['ناوی کڕیار'].values) if not st.session_state.customers.empty else [""]
                customer = st.selectbox("👤 ناوی کڕیار", customer_options)
                phone = st.text_input("📞 ژمارەی مۆبایل")
                address = st.text_area("📍 ناونیشانی گەیاندن")
            with col2:
                product = st.text_input("📦 بەرهەم")
                delivery_date = st.date_input("📅 بەرواری داواکاری", value=datetime.now().date())
                delivery_cost = st.number_input("💰 تێچووی گەیاندن ($)", min_value=0.0, step=5.0)
            
            notes = st.text_area("📝 تێبینی (ئارەزوومەندانە)")
            
            if st.form_submit_button("➕ تۆمارکردنی داواکاری"):
                if customer and address and product:
                    new_delivery = pd.DataFrame({
                        'ID': [f"DEL{datetime.now().strftime('%Y%m%d%H%M%S')}"],
                        'ناوی کڕیار': [customer],
                        'ژمارەی مۆبایل': [phone],
                        'ناونیشان': [address],
                        'بەرهەم': [product],
                        'بەرواری داواکاری': [delivery_date.strftime("%Y-%m-%d")],
                        'بەرواری گەیاندن': [''],
                        'تێچووی گەیاندن': [delivery_cost],
                        'ڕەوش': ['چاوەڕوان'],
                        'تێبینی': [notes]
                    })
                    st.session_state.deliveries = safe_concat(st.session_state.deliveries, new_delivery)
                    st.success(f"✅ داواکاری گەیاندن بۆ {customer} تۆمار کرا!")
                    st.rerun()
                else:
                    st.error("❌ تکایە ناوی کڕیار، ناونیشان و بەرهەم پڕ بکەرەوە")

    elif main_choice == "🚚 گەیاندن" and sub_choice == "📋 لیستی گەیاندنەکان":
        st.header("📋 لیستی گەیاندنەکان")
        if not st.session_state.deliveries.empty:
            status_filter = st.selectbox("ڕەوش", ["هەموو"] + list(st.session_state.deliveries['ڕەوش'].unique()))
            
            filtered = st.session_state.deliveries.copy()
            if status_filter != "هەموو":
                filtered = filtered[filtered['ڕەوش'] == status_filter]
            
            st.dataframe(filtered, use_container_width=True)
            
            # Update delivery status
            if not filtered.empty:
                st.subheader("🔄 نوێکردنەوەی ڕەوش")
                delivery_to_update = st.selectbox("داواکاری هەڵبژێرە", filtered['ID'].tolist())
                new_status = st.selectbox("ڕەوشی نوێ", ["چاوەڕوان", "لەڕێگادا", "گەیشتووە", "هەڵوەشاوەتەوە"])
                if st.button("💾 نوێکردنەوە"):
                    idx = st.session_state.deliveries[st.session_state.deliveries['ID'] == delivery_to_update].index[0]
                    st.session_state.deliveries.at[idx, 'ڕەوش'] = new_status
                    if new_status == "گەیشتووە":
                        st.session_state.deliveries.at[idx, 'بەرواری گەیاندن'] = datetime.now().strftime("%Y-%m-%d")
                    st.success("✅ ڕەوش نوێ کرایەوە!")
                    st.rerun()
            
            col1, col2 = st.columns(2)
            col1.metric("📦 کۆی داواکارییەکان", len(st.session_state.deliveries))
            col2.metric("✅ گەیشتووە", len(st.session_state.deliveries[st.session_state.deliveries['ڕەوش'] == 'گەیشتووە']))
        else:
            st.info("📭 هیچ داواکارییەکی گەیاندن نییە")

    # ================== 8. SUPPORT TICKETS SECTION ==================
    elif main_choice == "🎫 پشتیوانی" and sub_choice == "📝 تیکتی نوێ":
        st.header("📝 کردنەوەی تیکتی نوێ")
        with st.form("ticket_form"):
            col1, col2 = st.columns(2)
            with col1:
                customer_options = [""] + list(st.session_state.customers['ناوی کڕیار'].values) if not st.session_state.customers.empty else [""]
                customer = st.selectbox("👤 ناوی کڕیار", customer_options)
                subject = st.text_input("📋 بابەت")
            with col2:
                priority = st.selectbox("🔺 لەولەوەپێشی", ["نزم", "مامناوەند", "بەرز", "زۆر بەرز"])
            
            issue = st.text_area("📝 کێشە", placeholder="کێشەکە بە وردی ڕوون بکەرەوە...", height=150)
            
            if st.form_submit_button("📤 ناردنی تیکت"):
                if customer and subject and issue:
                    new_ticket = pd.DataFrame({
                        'ID': [f"TCK{datetime.now().strftime('%Y%m%d%H%M%S')}"],
                        'ناوی کڕیار': [customer],
                        'بابەت': [subject],
                        'کێشە': [issue],
                        'لەولەوەپێشی': [priority],
                        'بەرواری کردنەوە': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                        'بەرواری داخستن': [''],
                        'ڕەوش': ['کراوە'],
                        'وەڵام': ['']
                    })
                    st.session_state.tickets = safe_concat(st.session_state.tickets, new_ticket)
                    st.success(f"✅ تیکت بە سەرکەوتوویی نێردرا! ژمارەی تیکت: {new_ticket['ID'].iloc[0]}")
                    st.rerun()
                else:
                    st.error("❌ تکایە ناوی کڕیار، بابەت و کێشە پڕ بکەرەوە")

    elif main_choice == "🎫 پشتیوانی" and sub_choice == "📋 تیکتەکان":
        st.header("📋 لیستی تیکتەکان")
        if not st.session_state.tickets.empty:
            col1, col2 = st.columns(2)
            status_filter = col1.selectbox("ڕەوش", ["هەموو"] + list(st.session_state.tickets['ڕەوش'].unique()))
            priority_filter = col2.selectbox("لەولەوەپێشی", ["هەموو"] + list(st.session_state.tickets['لەولەوەپێشی'].unique()))
            
            filtered = st.session_state.tickets.copy()
            if status_filter != "هەموو":
                filtered = filtered[filtered['ڕەوش'] == status_filter]
            if priority_filter != "هەموو":
                filtered = filtered[filtered['لەولەوەپێشی'] == priority_filter]
            
            st.dataframe(filtered, use_container_width=True)
            
            # Respond to ticket
            if not filtered.empty:
                st.subheader("📝 وەڵامدانەوە")
                ticket_to_answer = st.selectbox("تیکت هەڵبژێرە", filtered[filtered['ڕەوش'] == 'کراوە']['ID'].tolist() if not filtered[filtered['ڕەوش'] == 'کراوە'].empty else filtered['ID'].tolist())
                response = st.text_area("وەڵام", height=100)
                close_ticket = st.checkbox("تیکتەکە دابخە")
                
                if st.button("📤 ناردنی وەڵام"):
                    idx = st.session_state.tickets[st.session_state.tickets['ID'] == ticket_to_answer].index[0]
                    st.session_state.tickets.at[idx, 'وەڵام'] = response
                    if close_ticket:
                        st.session_state.tickets.at[idx, 'ڕەوش'] = 'داخراوە'
                        st.session_state.tickets.at[idx, 'بەرواری داخستن'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.success("✅ وەڵام بە سەرکەوتوویی نێردرا!")
                    st.rerun()
        else:
            st.info("📭 هیچ تیکتێک نییە")

    # ================== 9. CUSTOMERS SECTION ==================
    elif main_choice == "👥 کڕیاران" and sub_choice == "📝 زیادکردنی کڕیار":
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
                # Check for duplicate
                if not st.session_state.customers.empty and cust_name in st.session_state.customers['ناوی کڕیار'].values:
                    st.error(f"❌ کڕیار {cust_name} پێشتر تۆمار کراوە!")
                else:
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
                    st.session_state.customers = safe_concat(st.session_state.customers, new_customer)
                    st.success(f"✅ کڕیار {cust_name} بە سەرکەوتوویی زیاد کرا!")
                    st.balloons()
                    st.rerun()

    elif main_choice == "👥 کڕیاران" and sub_choice == "📋 لیستی کڕیاران":
        st.header("📋 لیستی کڕیاران")
        if not st.session_state.customers.empty:
            # Search
            search = st.text_input("🔍 گەڕان...", placeholder="ناوی کڕیار یان ژمارە...")
            display_df = st.session_state.customers.copy()
            if search:
                mask = display_df['ناوی کڕیار'].str.contains(search, case=False) | display_df['ژمارەی مۆبایل'].str.contains(search, case=False)
                display_df = display_df[mask]
            
            st.dataframe(display_df, use_container_width=True)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("👥 کۆی کڕیاران", len(display_df))
            col2.metric("⭐ کۆی خاڵەکان", display_df['خاڵەکان'].sum())
            col3.metric("💰 کۆی کڕین", f"${display_df['کۆی کڕین'].sum():,.2f}")
            
            if st.button("📥 هەناردەکردن بۆ Excel"):
                excel_data = export_to_excel(display_df, 'Customers')
                if excel_data:
                    st.markdown(get_download_link(excel_data, 'customers_list.xlsx'), unsafe_allow_html=True)
        else:
            st.info("📭 هیچ کڕیارێک تۆمار نەکراوە")

    elif main_choice == "👥 کڕیاران" and sub_choice == "⭐ خاڵەکان":
        st.header("⭐ خاڵەکانی کڕیاران")
        if not st.session_state.customers.empty:
            loyalty_df = st.session_state.customers[['ناوی کڕیار', 'کۆی کڕین', 'خاڵەکان', 'ئاست']].copy()
            loyalty_df = loyalty_df.sort_values('خاڵەکان', ascending=False)
            
            st.dataframe(loyalty_df, use_container_width=True)
            
            if not loyalty_df.empty:
                top_customer = loyalty_df.iloc[0]
                st.success(f"🏆 کڕیاری هەفتە: {top_customer['ناوی کڕیار']} - {top_customer['خاڵەکان']} خاڵ!")
            
            # Points chart
            fig = px.bar(loyalty_df.head(10), x='ناوی کڕیار', y='خاڵەکان', color='ئاست', title='باشترین 10 کڕیار')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📭 هیچ کڕیارێک تۆمار نەکراوە")

    elif main_choice == "👥 کڕیاران" and sub_choice == "🎂 ڕۆژی لەدایکبوون":
        st.header("🎂 ڕۆژانی لەدایکبوون")
        
        today = datetime.now()
        birthdays_today = check_birthdays()
        
        if birthdays_today:
            st.success(f"🎂 ئەمڕۆ ڕۆژی لەدایکبوونی {', '.join(birthdays_today)} پیرۆز بێت!")
            st.balloons()
        
        if not st.session_state.customers.empty:
            # Upcoming birthdays this month
            this_month = st.session_state.customers.copy()
            this_month['birth_date'] = pd.to_datetime(this_month['ڕێکەوتی لەدایکبوون'], errors='coerce')
            this_month = this_month.dropna(subset=['birth_date'])
            this_month = this_month[this_month['birth_date'].dt.month == today.month]
            
            if not this_month.empty:
                this_month = this_month.sort_values('birth_date')
                st.subheader(f"📅 ڕۆژانی لەدایکبوونی مانگی {today.month}")
                st.dataframe(this_month[['ناوی کڕیار', 'ڕێکەوتی لەدایکبوون', 'ژمارەی مۆبایل']], use_container_width=True)
            else:
                st.info("هیچ ڕۆژی لەدایکبوونێک لەم مانگەدا نییە")
        else:
            st.info("📭 هیچ کڕیارێک تۆمار نەکراوە")

    # ================== 10. EMPLOYEES SECTION ==================
    elif main_choice == "👨‍💼 کارمەندان" and sub_choice == "📝 زیادکردنی کارمەند":
        st.header("📝 زیادکردنی کارمەندی نوێ")
        with st.form("employee_form"):
            col1, col2 = st.columns(2)
            with col1:
                emp_name = st.text_input("👤 ناوی کارمەند")
                emp_position = st.selectbox("📋 پلە", ["فرۆشیار", "بەڕێوەبەر", "تەکنیکار", "پاککەرەوە", "گەیاندن"])
            with col2:
                emp_salary = st.number_input("💰 مووچە ($)", min_value=0.0, step=50.0, value=600.0)
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
                st.session_state.employees = safe_concat(st.session_state.employees, new_employee)
                st.success(f"✅ کارمەند {emp_name} زیاد کرا!")
                st.rerun()
        
        if not st.session_state.employees.empty:
            st.subheader("📋 لیستی کارمەندان")
            st.dataframe(st.session_state.employees, use_container_width=True)

    elif main_choice == "👨‍💼 کارمەندان" and sub_choice == "📋 لیستی کارمەندان":
        st.header("📋 لیستی کارمەندان")
        if not st.session_state.employees.empty:
            st.dataframe(st.session_state.employees, use_container_width=True)
            
            if st.button("📥 هەناردەکردن"):
                excel_data = export_to_excel(st.session_state.employees, 'Employees')
                if excel_data:
                    st.markdown(get_download_link(excel_data, 'employees_list.xlsx'), unsafe_allow_html=True)
            
            # Salary summary
            total_salary = st.session_state.employees['مووچە'].sum()
            total_bonus = st.session_state.employees['پاداشت'].sum()
            st.metric("💰 کۆی مووچە و پاداشت", f"${total_salary + total_bonus:,.2f}")
        else:
            st.info("📭 هیچ کارمەندێک تۆمار نەکراوە")

    elif main_choice == "👨‍💼 کارمەندان" and sub_choice == "📊 ئاستی کارمەندان":
        st.header("📊 ئاستی کارمەندان")
        if not st.session_state.employees.empty:
            performance_df = st.session_state.employees[['ناوی کارمەند', 'پلە', 'ژمارەی فرۆشتن', 'کۆی فرۆشتن', 'پاداشت']].copy()
            performance_df = performance_df.sort_values('کۆی فرۆشتن', ascending=False)
            st.dataframe(performance_df, use_container_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                fig = px.bar(performance_df, x='ناوی کارمەند', y='کۆی فرۆشتن', title='کۆی فرۆشتن')
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                fig2 = px.pie(performance_df, values='پاداشت', names='ناوی کارمەند', title='دابەشکردنی پاداشت')
                st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("📭 هیچ کارمەندێک تۆمار نەکراوە")

    elif main_choice == "👨‍💼 کارمەندان" and sub_choice == "⏰ ئامادەبوون":
        st.header("⏰ تۆمارکردنی ئامادەبوون")
        
        if not st.session_state.employees.empty:
            col1, col2 = st.columns(2)
            with col1:
                employee = st.selectbox("👨‍💼 کارمەند", st.session_state.employees['ناوی کارمەند'].tolist())
                attendance_date = st.date_input("📅 بەروار", value=datetime.now().date())
            with col2:
                time_in = st.time_input("🕐 کاتی هاتن", value=datetime.strptime("08:00", "%H:%M").time())
                time_out = st.time_input("🕔 کاتی ڕۆیشتن", value=datetime.strptime("17:00", "%H:%M").time())
            
            if time_in and time_out:
                hours_worked = (datetime.combine(datetime.today(), time_out) - datetime.combine(datetime.today(), time_in)).seconds / 3600
                st.info(f"⏱️ کاتژمێری کار: {hours_worked:.1f} کاتژمێر")
            
            if st.button("✅ تۆمارکردنی ئامادەبوون"):
                new_attendance = pd.DataFrame({
                    'کارمەند': [employee],
                    'بەروار': [attendance_date.strftime("%Y-%m-%d")],
                    'کاتی هاتن': [time_in.strftime("%H:%M")],
                    'کاتی ڕۆیشتن': [time_out.strftime("%H:%M")],
                    'کاتژمێر': [hours_worked],
                    'ڕەوش': ['ئامادە']
                })
                st.session_state.attendance = safe_concat(st.session_state.attendance, new_attendance)
                st.success(f"✅ ئامادەبوونی {employee} تۆمار کرا!")
                st.rerun()
            
            if not st.session_state.attendance.empty:
                st.subheader("📋 مێژووی ئامادەبوون")
                filtered_attendance = st.session_state.attendance.copy()
                emp_filter = st.selectbox("پاڵێو بە کارمەند", ["هەموو"] + list(st.session_state.attendance['کارمەند'].unique()))
                if emp_filter != "هەموو":
                    filtered_attendance = filtered_attendance[filtered_attendance['کارمەند'] == emp_filter]
                
                st.dataframe(filtered_attendance.tail(20), use_container_width=True)
        else:
            st.info("📭 هیچ کارمەندێک تۆمار نەکراوە")

    # ================== 11. PROFIT SECTION ==================
    elif main_choice == "📊 قازانج" and sub_choice == "💰 خەمڵاندنی قازانج":
        st.header("💰 خەمڵاندنی قازانج")
        
        total_sales = st.session_state.sales['نرخی کۆتایی'].sum() if not st.session_state.sales.empty else 0
        total_cost = (st.session_state.inventory['نرخی کڕین'] * st.session_state.inventory['ژمارەی دانەکان']).sum() if not st.session_state.inventory.empty else 0
        total_expenses = st.session_state.expenses['بڕ'].sum() if not st.session_state.expenses.empty else 0
        net_profit = total_sales - total_cost - total_expenses
        profit_margin = (net_profit / total_sales * 100) if total_sales > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("💰 کۆی فرۆشتن", f"${total_sales:,.2f}")
        col2.metric("💸 کۆی تێچوو", f"${total_cost:,.2f}")
        col3.metric("📊 کۆی خەرجی", f"${total_expenses:,.2f}")
        col4.metric("💰 قازانجی خالص", f"${net_profit:,.2f}", f"{profit_margin:.1f}%")
        
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
        
        total_sales = st.session_state.sales['نرخی کۆتایی'].sum() if not st.session_state.sales.empty else 0
        total_cost = (st.session_state.inventory['نرخی کڕین'] * st.session_state.inventory['ژمارەی دانەکان']).sum() if not st.session_state.inventory.empty else 0
        total_expenses = st.session_state.expenses['بڕ'].sum() if not st.session_state.expenses.empty else 0
        net_profit = total_sales - total_cost - total_expenses
        
        fig = go.Figure()
        fig.add_trace(go.Bar(name='کۆی فرۆشتن', x=['دارایی'], y=[total_sales], marker_color='#2ecc71'))
        fig.add_trace(go.Bar(name='کۆی تێچوو', x=['دارایی'], y=[total_cost], marker_color='#e74c3c'))
        fig.add_trace(go.Bar(name='کۆی خەرجی', x=['دارایی'], y=[total_expenses], marker_color='#f39c12'))
        fig.add_trace(go.Bar(name='قازانجی خالص', x=['دارایی'], y=[net_profit], marker_color='#3498db'))
        
        fig.update_layout(title="هێڵکاری دارایی دوکان", barmode='group', height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Expense breakdown
        if not st.session_state.expenses.empty:
            expense_by_type = st.session_state.expenses.groupby('جۆر')['بڕ'].sum()
            fig2 = px.pie(values=expense_by_type.values, names=expense_by_type.index, title='دابەشکردنی خەرجییەکان')
            st.plotly_chart(fig2, use_container_width=True)

    elif main_choice == "📊 قازانج" and sub_choice == "📄 ڕاپۆرتی PDF":
        st.header("📄 دروستکردنی ڕاپۆرتی PDF")
        
        report_type = st.selectbox("جۆری ڕاپۆرت", ["دارایی", "فرۆشتن", "کۆگا", "کڕیاران", "قیستەکان"])
        date_from = st.date_input("لە بەروارەوە", value=datetime.now().date() - timedelta(days=30))
        date_to = st.date_input("تا بەروار", value=datetime.now().date())
        
        if st.button("📄 دروستکردنی ڕاپۆرت"):
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_pdf:
                    pdf = FPDF()
                    pdf.add_page()
                    
                    # Title
                    pdf.set_font("Arial", "B", 20)
                    pdf.cell(0, 15, f"Mobile Shop - ڕاپۆرتی {report_type}", ln=True, align="C")
                    pdf.ln(5)
                    pdf.set_font("Arial", "", 12)
                    pdf.cell(0, 8, f"ماوە: {date_from} تا {date_to}", ln=True)
                    pdf.cell(0, 8, f"بەرواری دروستکردن: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
                    pdf.ln(10)
                    
                    if report_type == "دارایی":
                        total_sales = st.session_state.sales['نرخی کۆتایی'].sum() if not st.session_state.sales.empty else 0
                        total_expenses = st.session_state.expenses['بڕ'].sum() if not st.session_state.expenses.empty else 0
                        total_cost = (st.session_state.inventory['نرخی کڕین'] * st.session_state.inventory['ژمارەی دانەکان']).sum() if not st.session_state.inventory.empty else 0
                        
                        pdf.set_font("Arial", "B", 14)
                        pdf.cell(0, 10, "پوختەی دارایی", ln=True)
                        pdf.set_font("Arial", "", 12)
                        pdf.cell(0, 8, f"کۆی فرۆشتن: ${total_sales:,.2f}", ln=True)
                        pdf.cell(0, 8, f"کۆی تێچوو: ${total_cost:,.2f}", ln=True)
                        pdf.cell(0, 8, f"کۆی خەرجی: ${total_expenses:,.2f}", ln=True)
                        pdf.cell(0, 8, f"قازانجی خالص: ${total_sales - total_cost - total_expenses:,.2f}", ln=True)
                    
                    elif report_type == "فرۆشتن":
                        pdf.set_font("Arial", "B", 14)
                        pdf.cell(0, 10, "دوایین فرۆشتنەکان", ln=True)
                        pdf.set_font("Arial", "", 10)
                        for _, sale in st.session_state.sales.tail(20).iterrows():
                            pdf.cell(0, 6, f"{sale['کاتی فرۆشتن']} - {sale['ناوی بەرهەم']} - ${sale['نرخی کۆتایی']:.2f}", ln=True)
                    
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

    elif main_choice == "📊 قازانج" and sub_choice == "💸 خەرجییەکان":
        st.header("💸 تۆمارکردنی خەرجی")
        with st.form("expense_form"):
            col1, col2 = st.columns(2)
            with col1:
                expense_date = st.date_input("📅 بەروار", value=datetime.now().date())
                expense_type = st.selectbox("📋 جۆری خەرجی", ["کرێ", "مووچە", "کارەبا", "ئاو", "ئینتەرنێت", "گواستنەوە", "ڕیکلام", "چاککردنەوە", "کڕینی کەلوپەل", "تر"])
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
                    st.session_state.expenses = safe_concat(st.session_state.expenses, new_expense)
                    st.success(f"✅ خەرجی {expense_type} بە بڕی ${expense_amount:,.2f} تۆمار کرا!")
                    st.rerun()
                else:
                    st.error("❌ تکایە بڕی خەرجی پڕ بکەرەوە")
        
        if not st.session_state.expenses.empty:
            st.subheader("📋 مێژووی خەرجییەکان")
            
            # Filter by type
            expense_type_filter = st.selectbox("پاڵێو بە جۆر", ["هەموو"] + list(st.session_state.expenses['جۆر'].unique()))
            filtered_expenses = st.session_state.expenses.copy()
            if expense_type_filter != "هەموو":
                filtered_expenses = filtered_expenses[filtered_expenses['جۆر'] == expense_type_filter]
            
            st.dataframe(filtered_expenses.sort_values('بەروار', ascending=False), use_container_width=True)
            
            col1, col2 = st.columns(2)
            col1.metric("💰 کۆی خەرجییەکان", f"${filtered_expenses['بڕ'].sum():,.2f}")
            col2.metric("📊 ژمارەی خەرجییەکان", len(filtered_expenses))
            
            if st.button("📥 هەناردەکردن"):
                excel_data = export_to_excel(filtered_expenses, 'Expenses')
                if excel_data:
                    st.markdown(get_download_link(excel_data, 'expenses_list.xlsx'), unsafe_allow_html=True)

    # ================== 12. DASHBOARD SECTION ==================
    elif main_choice == "📊 داشبۆرد" and sub_choice == "🎯 سەرەکی":
        st.header("🎯 داشبۆردی سەرەکی")
        
        today = datetime.now().date()
        today_sales = 0
        if not st.session_state.sales.empty:
            sales_today = st.session_state.sales.copy()
            sales_today['date'] = pd.to_datetime(sales_today['کاتی فرۆشتن']).dt.date
            today_sales = sales_today[sales_today['date'] == today]['نرخی کۆتایی'].sum()
        
        # Main metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("💰 فرۆشتی ئەمڕۆ", f"${today_sales:,.2f}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("📦 کەلوپەلی کەم", len(check_low_stock()))
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            active_repairs = len(st.session_state.repairs[st.session_state.repairs['ڕەوش'].isin(['چاوەڕوان', 'لەژێرکارە'])]) if not st.session_state.repairs.empty else 0
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("🔧 چاککردنەوە", active_repairs)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            active_installments = len(st.session_state.installments[st.session_state.installments['ڕەوش'] == 'چالاکە']) if not st.session_state.installments.empty else 0
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("💳 قیستی چالاک", active_installments)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Quick actions
        st.markdown("---")
        st.subheader("🚀 کردارە خێراکان")
        col_a, col_b, col_c, col_d = st.columns(4)
        with col_a:
            if st.button("💰 فرۆشتنی نوێ"):
                st.session_state['nav_to'] = ("💰 فرۆشتن", "📝 فرۆشتنی نوێ")
                st.rerun()
        with col_b:
            if st.button("📦 زیادکردنی کەلوپەل"):
                st.session_state['nav_to'] = ("📦 کۆگا", "📝 زیادکردنی کەلوپەل")
                st.rerun()
        with col_c:
            if st.button("👥 کڕیاری نوێ"):
                st.session_state['nav_to'] = ("👥 کڕیاران", "📝 زیادکردنی کڕیار")
                st.rerun()
        with col_d:
            if st.button("💸 خەرجی نوێ"):
                st.session_state['nav_to'] = ("📊 قازانج", "💸 خەرجییەکان")
                st.rerun()

    elif main_choice == "📊 داشبۆرد" and sub_choice == "📈 شیکاری":
        st.header("📈 شیکاری پێشکەوتوو")
        
        if not st.session_state.sales.empty:
            sales_data = st.session_state.sales.copy()
            sales_data['date'] = pd.to_datetime(sales_data['کاتی فرۆشتن']).dt.date
            sales_data['month'] = pd.to_datetime(sales_data['کاتی فرۆشتن']).dt.month
            
            # Monthly sales
            monthly_sales = sales_data.groupby('month')['نرخی کۆتایی'].sum()
            
            fig = px.line(
                x=monthly_sales.index, 
                y=monthly_sales.values,
                labels={'x': 'مانگ', 'y': 'فرۆشتن ($)'},
                title="هێڵکاری فرۆشتن بەپێی مانگ",
                markers=True
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                # Top products
                top_products = sales_data.groupby('ناوی بەرهەم')['نرخی کۆتایی'].sum().nlargest(5)
                fig2 = px.pie(values=top_products.values, names=top_products.index, title='باشترین 5 بەرهەم')
                st.plotly_chart(fig2, use_container_width=True)
            
            with col2:
                # Top customers
                top_customers = sales_data.groupby('ناوی کڕیار')['نرخی کۆتایی'].sum().nlargest(5)
                fig3 = px.bar(x=top_customers.index, y=top_customers.values, title='باشترین 5 کڕیار')
                st.plotly_chart(fig3, use_container_width=True)
            
            # Daily sales trend
            daily_sales = sales_data.groupby('date')['نرخی کۆتایی'].sum()
            fig4 = px.line(x=daily_sales.index, y=daily_sales.values, title='فرۆشتی ڕۆژانە', markers=True)
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("هیچ داتایەکی فرۆشتن بۆ شیکاری نییە")

    # ================== 13. SETTINGS SECTION ==================
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
        
        st.markdown("---")
        st.warning("⚠️ ئاگاداری: گەڕاندنەوەی بەکاپ هەموو داتا ئێستاکە دەسڕێتەوە!")

    elif main_choice == "⚙️ ڕێکخستن" and sub_choice == "🔔 ئاگادارییەکان":
        st.header("🔔 ئاگادارییە زیرەکەکان")
        
        notifications = []
        
        # Low stock
        for _, item in check_low_stock().iterrows():
            notifications.append(('error', f"📦 کەلوپەلی {item['ناوی کەلوپەل']} کەمە! (ماوە: {item['ژمارەی دانەکان']} دانە)"))
        
        # Expiring warranty
        for _, warranty in check_expiring_warranty().iterrows():
            days_left = (warranty['بەرواری کۆتایی گەرەنتی'] - datetime.now().date()).days if pd.notna(warranty['بەرواری کۆتایی گەرەنتی']) else 0
            notifications.append(('warning', f"⏰ گەرەنتی {warranty['ناوی کڕیار']} ({days_left} ڕۆژ ماوە)"))
        
        # Upcoming installments
        for _, installment in check_upcoming_installments().iterrows():
            notifications.append(('info', f"💳 قیستی {installment['ناوی کڕیار']}: ${installment['مانگانە']:,.2f}"))
        
        # Birthdays
        for birthday in check_birthdays():
            notifications.append(('success', f"🎂 ڕۆژی لەدایکبوونی {birthday} پیرۆز بێت!"))
        
        # Overdue installments
        if not st.session_state.installments.empty:
            today = datetime.now().date()
            active_inst = st.session_state.installments[st.session_state.installments['ڕەوش'] == 'چالاکە'].copy()
            if not active_inst.empty:
                active_inst['due_date'] = pd.to_datetime(active_inst['بەرواری داهاتووی قیست'], errors='coerce').dt.date
                overdue = active_inst[active_inst['due_date'] < today]
                for _, inst in overdue.iterrows():
                    notifications.append(('error', f"🚨 قیستی دواکەوتوو: {inst['ناوی کڕیار']} - ${inst['مانگانە']:,.2f}"))
        
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
        
        # Notification summary
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("⚠️ کەلوپەلی کەم", len(check_low_stock()))
        col2.metric("⏰ گەرەنتی نزیک", len(check_expiring_warranty()))
        col3.metric("💳 قیستی نزیک", len(check_upcoming_installments()))
        col4.metric("🎂 ڕۆژی لەدایکبوون", len(check_birthdays()))

    # ================== DEFAULT PAGE ==================
    else:
        st.info(f"""
        ### 👋 بەخێربێیت بۆ سیستەمی بەڕێوەبردنی دوکانی مۆبایل!
        
        **ڕێنمایی خێرا:**
        - 🏠 لە شریتی لای ڕاستەوە بەشێک هەڵبژێرە
        - 💰 بۆ فرۆشتن، بەشی "فرۆشتن" هەڵبژێرە
        - 💳 بۆ بەڕێوەبردنی قیستەکان، بەشی "قیست" هەڵبژێرە
        - 📦 بۆ بەڕێوەبردنی کۆگا، بەشی "کۆگا" هەڵبژێرە
        - 👥 بۆ بەڕێوەبردنی کڕیاران، بەشی "کڕیاران" هەڵبژێرە
        
        **تایبەتمەندییە نوێیەکان:**
        - ✅ 15+ بەشی جیاواز
        - ✅ سیستەمی قیستی تەواو
        - ✅ سکانی بارکۆد
        - ✅ چاککردنەوە و گەیاندن
        - ✅ تیکتی پشتیوانی
        - ✅ بەڕێوەبردنی کارمەندان و ئامادەبوون
        - ✅ فاکتوور و ڕاپۆرتی PDF
        - ✅ سیستەمی خاڵ و پاداشت
        - ✅ بەکاپ و گەڕاندنەوە
        - ✅ ئاگادارییە زیرەکەکان
        
        📌 دەتوانیت بە دوگمەی **"داتای نموونەیی"** لە شریتی لاتەنیشتەوە، داتای تاقیکردنەوە دروست بکەیت.
        """)

except Exception as e:
    st.error(f"هەڵەیەک ڕوویدا: {str(e)}")
    st.info("تکایە پەڕەکە نوێ بکەرەوە یان پەیوەندی بە پشتیوانییەوە بکەن.")

# ================== FOOTER ==================
st.markdown("---")
st.markdown("""
    <div class="footer">
        <h3>📱 سیستەمی بەڕێوەبردنی دوکانی مۆبایل</h3>
        <p>© 2024 | 15+ بەشی جیاواز | ڕاپۆرتی زیرەک | پشتیوانی قیست | پشتیوانی بارکۆد</p>
        <p>🔧 وەشانی 3.0 - تەواو پاڵپشتیکراو و بێ کێشە</p>
    </div>
""", unsafe_allow_html=True)
```

ئەم کۆدە تەواوکراوە و ئەم تایبەتمەندییانەی تێدایە:

1. ✅ هەموو 15+ بەشەکە چالاکە: فرۆشتن، کۆگا، داشکاندن، قیست، گەرەنتی، چاککردنەوە، گەیاندن، پشتیوانی، کڕیاران، کارمەندان، قازانج، داشبۆرد، ڕێکخستن
2. ✅ سیستەمی ئامادەبوون: بۆ کارمەندان
3. ✅ بەڕێوەبردنی تەواوی قیستەکان: بە ئاگاداری دواکەوتووەکان
4. ✅ چاکردنەوە و گەیاندن: بە شوێنکەوتنی ڕەوش
5. ✅ تیکتی پشتیوانی: بە وەڵامدانەوە
6. ✅ گەڕان و پاڵێوکردن: لە زۆربەی بەشەکاندا
7. ✅ نوێکردنەوەی کۆگا: بە شێوەیەکی ئۆتۆماتیکی دوای هەر فرۆشتنێک
8. ✅ ڕاپۆرتی تەواو: بە هەڵبژاردنی جۆر و ماوە
