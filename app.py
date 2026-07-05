import streamlit as st
import json
import os
from datetime import datetime
from fpdf import FPDF
import tempfile
import subprocess
import platform
import webbrowser
import base64
from io import BytesIO
import sys

# ================================
# ڕێکخستنی ڕووکاری پەڕە
# ================================
st.set_page_config(
    page_title="محمد فۆن - سیستەمی قەرزی مۆبایل",
    page_icon="📱",
    layout="wide"
)

# ================================
# CSS
# ================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }
    
    h1, h2, h3 {
        color: white !important;
        font-weight: 700 !important;
    }
    
    p, label {
        color: #e2e8f0 !important;
    }
    
    .custom-card {
        background: linear-gradient(135deg, #16213e 0%, #1a1a2e 100%);
        border: 1px solid #0f3460;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        margin-bottom: 1rem;
    }
    
    .stat-card {
        background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
        border: 1px solid #e94560;
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        color: white;
    }
    
    .stat-card h2 {
        color: #e94560 !important;
        font-size: 2rem;
        margin: 0.5rem 0;
    }
    
    .stButton > button {
        border-radius: 12px !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        border: none !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 20px rgba(233, 69, 96, 0.3) !important;
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #e94560 0%, #c23152 100%) !important;
        color: white !important;
    }
    
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        border-radius: 12px !important;
        border: 2px solid #0f3460 !important;
        padding: 0.75rem !important;
        background: #16213e !important;
        color: white !important;
    }
    
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #0f3460 0%, #16213e 100%) !important;
        color: white !important;
        border-radius: 12px !important;
        border: 1px solid #e94560 !important;
    }
    
    .paid-badge {
        background: #48bb78;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.9rem;
        display: inline-block;
    }
    
    .unpaid-badge {
        background: #e94560;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.9rem;
        display: inline-block;
    }
    
    .footer {
        text-align: center;
        padding: 20px;
        color: #718096;
        margin-top: 2rem;
    }
    
    .info-box {
        background: #16213e;
        border: 1px solid #e94560;
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        color: #e2e8f0;
    }
    
    .info-box ul {
        margin: 0.5rem 0;
        padding-right: 1.5rem;
    }
    
    .info-box li {
        margin: 0.3rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ================================
# سیستەمی خەزنکردنی داتا
# ================================
DATA_FILE = "mohammed_phone_loans.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"customers": []}
    return {"customers": []}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ================================
# PDF بە عەرەبی - بەبێ فۆنتی دەرەکی
# ================================
def create_customer_pdf_arabic(customer):
    pdf = FPDF()
    pdf.add_page()
    
    # هێدەر
    pdf.set_font('Arial', 'B', 24)
    pdf.set_text_color(233, 69, 96)
    pdf.cell(0, 15, 'Mohammed Phone', ln=True, align='C')
    pdf.set_font('Arial', '', 14)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, 'تقرير قرض العميل', ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_draw_color(233, 69, 96)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)
    
    # زانیاری کڕیار
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(33, 37, 41)
    pdf.cell(0, 10, 'معلومات العميل', ln=True, align='R')
    pdf.ln(5)
    
    info_items = [
        ('الاسم', customer['name']),
        ('نوع الموبايل', customer['phone_model']),
        ('رقم الهاتف', customer['phone_number']),
        ('تاريخ الاضافة', customer['date_added']),
    ]
    
    pdf.set_font('Arial', '', 12)
    pdf.set_text_color(60, 60, 60)
    for label, value in info_items:
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(60, 8, f'{label}:', ln=False, align='R')
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 8, str(value), ln=True, align='R')
    
    pdf.ln(5)
    
    # زانیاری قەرز
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(33, 37, 41)
    pdf.cell(0, 10, 'معلومات القرض', ln=True, align='R')
    pdf.ln(5)
    
    status_text = 'تم التسديد' if customer['status'] == 'paid' else 'لم يكتمل'
    
    loan_items = [
        ('السعر الكلي', f"{customer['total_amount']:,} د.ع"),
        ('الدفعة المقدمة', f"{customer['down_payment']:,} د.ع"),
        ('القسط الشهري', f"{customer['monthly_payment']:,} د.ع"),
        ('المبلغ المدفوع', f"{customer['paid_amount']:,} د.ع"),
        ('المبلغ المتبقي', f"{customer['remaining']:,} د.ع"),
        ('الحالة', status_text),
    ]
    
    for label, value in loan_items:
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(60, 8, f'{label}:', ln=False, align='R')
        pdf.set_font('Arial', '', 12)
        
        if label == 'الحالة':
            if 'تم' in value:
                pdf.set_text_color(72, 187, 120)
            else:
                pdf.set_text_color(233, 69, 96)
        
        pdf.cell(0, 8, str(value), ln=True, align='R')
        pdf.set_text_color(60, 60, 60)
    
    pdf.ln(5)
    
    # مێژووی پارەدان
    if customer['payments']:
        pdf.set_font('Arial', 'B', 16)
        pdf.set_text_color(33, 37, 41)
        pdf.cell(0, 10, 'سجل المدفوعات', ln=True, align='R')
        pdf.ln(5)
        
        pdf.set_font('Arial', 'B', 11)
        pdf.set_fill_color(233, 69, 96)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(15, 8, 'م', border=1, fill=True, align='C')
        pdf.cell(50, 8, 'التاريخ', border=1, fill=True, align='C')
        pdf.cell(50, 8, 'المبلغ', border=1, fill=True, align='C')
        pdf.cell(0, 8, 'ملاحظات', border=1, fill=True, align='C')
        pdf.ln()
        
        pdf.set_text_color(60, 60, 60)
        for i, payment in enumerate(customer['payments'], 1):
            pdf.set_font('Arial', '', 11)
            if i % 2 == 0:
                pdf.set_fill_color(240, 240, 240)
            else:
                pdf.set_fill_color(255, 255, 255)
            
            pdf.cell(15, 7, str(i), border=1, fill=True, align='C')
            pdf.cell(50, 7, payment['date'], border=1, fill=True, align='C')
            pdf.cell(50, 7, f"{payment['amount']:,} د.ع", border=1, fill=True, align='C')
            pdf.cell(0, 7, payment.get('notes', ''), border=1, fill=True, align='C')
            pdf.ln()
    
    pdf.ln(10)
    pdf.set_font('Arial', 'I', 10)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 10, f'تم الاصدار: {datetime.now().strftime("%Y-%m-%d %H:%M")} | محمد فون', ln=True, align='C')
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        pdf.output(tmp.name)
        return tmp.name

def create_all_customers_pdf_arabic(data):
    pdf = FPDF()
    pdf.add_page('L')
    
    pdf.set_font('Arial', 'B', 24)
    pdf.set_text_color(233, 69, 96)
    pdf.cell(0, 15, 'Mohammed Phone', ln=True, align='C')
    pdf.set_font('Arial', '', 14)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, 'تقرير جميع العملاء', ln=True, align='C')
    pdf.ln(5)
    
    total_loan = sum(c['total_amount'] for c in data['customers'])
    total_paid = sum(c['paid_amount'] for c in data['customers'])
    remaining = total_loan - total_paid
    
    pdf.set_font('Arial', 'B', 14)
    pdf.set_text_color(33, 37, 41)
    pdf.cell(0, 10, 'الملخص', ln=True, align='R')
    pdf.set_font('Arial', '', 12)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 8, f'عدد العملاء: {len(data["customers"])}', ln=True, align='R')
    pdf.cell(0, 8, f'مجموع القروض: {total_loan:,} د.ع', ln=True, align='R')
    pdf.cell(0, 8, f'المبلغ المدفوع: {total_paid:,} د.ع', ln=True, align='R')
    pdf.cell(0, 8, f'المبلغ المتبقي: {remaining:,} د.ع', ln=True, align='R')
    pdf.ln(10)
    
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(33, 37, 41)
    pdf.cell(0, 10, 'قائمة العملاء', ln=True, align='R')
    pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 10)
    pdf.set_fill_color(233, 69, 96)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(10, 8, 'م', border=1, fill=True, align='C')
    pdf.cell(60, 8, 'الاسم', border=1, fill=True, align='C')
    pdf.cell(50, 8, 'نوع الموبايل', border=1, fill=True, align='C')
    pdf.cell(35, 8, 'السعر', border=1, fill=True, align='C')
    pdf.cell(35, 8, 'المدفوع', border=1, fill=True, align='C')
    pdf.cell(35, 8, 'المتبقي', border=1, fill=True, align='C')
    pdf.cell(0, 8, 'الحالة', border=1, fill=True, align='C')
    pdf.ln()
    
    pdf.set_font('Arial', '', 10)
    pdf.set_text_color(60, 60, 60)
    for i, customer in enumerate(data['customers'], 1):
        if i % 2 == 0:
            pdf.set_fill_color(240, 240, 240)
        else:
            pdf.set_fill_color(255, 255, 255)
        
        pdf.cell(10, 7, str(i), border=1, fill=True, align='C')
        pdf.cell(60, 7, customer['name'][:25], border=1, fill=True)
        pdf.cell(50, 7, customer['phone_model'][:22], border=1, fill=True)
        pdf.cell(35, 7, f"{customer['total_amount']:,}", border=1, fill=True, align='R')
        pdf.cell(35, 7, f"{customer['paid_amount']:,}", border=1, fill=True, align='R')
        pdf.cell(35, 7, f"{customer['remaining']:,}", border=1, fill=True, align='R')
        
        status = 'تم' if customer['status'] == 'paid' else 'متبقي'
        if status == 'تم':
            pdf.set_text_color(72, 187, 120)
        else:
            pdf.set_text_color(233, 69, 96)
        pdf.cell(0, 7, status, border=1, fill=True, align='C')
        pdf.set_text_color(60, 60, 60)
        pdf.ln()
    
    pdf.ln(10)
    pdf.set_font('Arial', 'I', 10)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 10, f'تم الاصدار: {datetime.now().strftime("%Y-%m-%d %H:%M")} | محمد فون', ln=True, align='C')
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        pdf.output(tmp.name)
        return tmp.name

# ================================
# فەنکشنی پرینت
# ================================
def open_pdf_for_printing(pdf_path):
    """کردنەوەی PDF بۆ پرینت"""
    try:
        if platform.system() == 'Windows':
            os.startfile(pdf_path, 'print')
        elif platform.system() == 'Darwin':  # Mac
            subprocess.run(['open', pdf_path])
        else:  # Linux
            subprocess.run(['xdg-open', pdf_path])
        return True
    except Exception as e:
        return False

# ================================
# دەستپێکردن
# ================================
if 'data' not in st.session_state:
    st.session_state.data = load_data()
if 'editing_customer' not in st.session_state:
    st.session_state.editing_customer = None
if 'saved_pdf_path' not in st.session_state:
    st.session_state.saved_pdf_path = None

data = st.session_state.data

# ================================
# هێدەر
# ================================
st.markdown("""
<div style='text-align: center; padding: 2rem 1rem;'>
    <div style='font-size: 4rem;'>📱</div>
    <h1 style='font-size: 3rem; margin: 0.5rem 0;'>محمد فۆن</h1>
    <p style='font-size: 1.2rem; color: #e94560;'>سیستەمی بەڕێوەبردنی قەرزی مۆبایل</p>
</div>
""", unsafe_allow_html=True)

# ================================
# ئاماری گشتی
# ================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class='stat-card'>
        <p>👥 کڕیاران</p>
        <h2>{len(data['customers'])}</h2>
    </div>
    """, unsafe_allow_html=True)

with col2:
    total_loan = sum(c['total_amount'] for c in data['customers'])
    st.markdown(f"""
    <div class='stat-card'>
        <p>💰 کۆی قەرز</p>
        <h2>{total_loan:,.0f} د.ع</h2>
    </div>
    """, unsafe_allow_html=True)

with col3:
    total_paid = sum(c['paid_amount'] for c in data['customers'])
    st.markdown(f"""
    <div class='stat-card'>
        <p>✅ پارەی وەرگیراو</p>
        <h2>{total_paid:,.0f} د.ع</h2>
    </div>
    """, unsafe_allow_html=True)

with col4:
    remaining = total_loan - total_paid
    st.markdown(f"""
    <div class='stat-card'>
        <p>⏳ پارەی ماوە</p>
        <h2>{remaining:,.0f} د.ع</h2>
    </div>
    """, unsafe_allow_html=True)

# ================================
# تابەکان
# ================================
tab1, tab2, tab3, tab4 = st.tabs([
    "➕ زیادکردنی کڕیار", 
    "📋 لیستی کڕیاران", 
    "💵 تۆمارکردنی پارە", 
    "📤 هەناردەکردن و پرینت"
])

# ================================
# تاب ١: زیادکردنی کڕیار
# ================================
with tab1:
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    st.markdown("<h3>➕ کڕیاری نوێ</h3>", unsafe_allow_html=True)
    
    with st.form("add_customer", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("👤 ناوی کڕیار:", placeholder="ناوی کڕیار")
            phone_model = st.text_input("📱 مۆدێلی مۆبایل:", placeholder="وەک: iPhone 15 Pro")
            phone_number = st.text_input("📞 ژمارەی مۆبایل:", placeholder="07xx xxx xxxx")
        
        with col2:
            total_price = st.number_input("💰 نرخی گشتی (دینار):", min_value=0, step=1000)
            down_payment = st.number_input("💵 پێشەکی (دینار):", min_value=0, step=1000)
            monthly_payment = st.number_input("📅 قیستی مانگانە (دینار):", min_value=0, step=1000)
        
        notes = st.text_area("📝 تێبینی:", placeholder="هەر تێبینییەک...")
        
        if st.form_submit_button("✅ زیادکردنی کڕیار", use_container_width=True):
            if not name:
                st.error("❌ ناوی کڕیار پێویستە")
            elif total_price <= 0:
                st.error("❌ نرخی گشتی پێویستە")
            else:
                new_customer = {
                    "id": len(data['customers']) + 1,
                    "name": name,
                    "phone_model": phone_model,
                    "phone_number": phone_number,
                    "total_amount": total_price,
                    "down_payment": down_payment,
                    "monthly_payment": monthly_payment,
                    "paid_amount": down_payment,
                    "remaining": total_price - down_payment,
                    "payments": [],
                    "date_added": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "notes": notes,
                    "status": "unpaid"
                }
                
                data['customers'].append(new_customer)
                save_data(data)
                st.success(f"✅ کڕیار {name} زیاد کرا!")
                st.balloons()
                st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# ================================
# تاب ٢: لیستی کڕیاران
# ================================
with tab2:
    st.markdown("<h3>📋 لیستی کڕیاران</h3>", unsafe_allow_html=True)
    
    if not data['customers']:
        st.info("هیچ کڕیارێک تۆمار نەکراوە.")
    else:
        search = st.text_input("🔍 گەڕان...", placeholder="گەڕان بەناوی کڕیار...")
        
        filtered_customers = data['customers']
        if search:
            filtered_customers = [c for c in data['customers'] if search.lower() in c['name'].lower()]
        
        for customer in filtered_customers:
            status_badge = '<span class="paid-badge">✅ پڕکراوە</span>' if customer['status'] == 'paid' else '<span class="unpaid-badge">⏳ ماوە</span>'
            
            with st.expander(f"📱 {customer['name']} - {customer['phone_model']} | ماوە: {customer['remaining']:,} د.ع {status_badge}", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    **👤 ناو:** {customer['name']}
                    **📱 مۆبایل:** {customer['phone_model']}
                    **📞 ژمارە:** {customer['phone_number']}
                    **📅 بەروار:** {customer['date_added']}
                    **📝 تێبینی:** {customer['notes']}
                    """)
                
                with col2:
                    st.markdown(f"""
                    **💰 نرخی گشتی:** {customer['total_amount']:,} د.ع
                    **💵 پێشەکی:** {customer['down_payment']:,} د.ع
                    **📅 قیست:** {customer['monthly_payment']:,} د.ع
                    **✅ وەرگیراو:** {customer['paid_amount']:,} د.ع
                    **⏳ ماوە:** {customer['remaining']:,} د.ع
                    """)
                
                if customer['total_amount'] > 0:
                    progress = customer['paid_amount'] / customer['total_amount']
                    st.progress(min(progress, 1.0))
                    st.caption(f"{progress * 100:.1f}% پارەکەی وەرگیراوە")
                
                if customer['payments']:
                    st.markdown("**📋 مێژووی پارەدان:**")
                    for payment in customer['payments'][-5:]:
                        st.markdown(f"- {payment['date']}: {payment['amount']:,} د.ع | {payment.get('notes', '')}")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    if st.button("💵 تۆمارکردنی پارە", key=f"pay_{customer['id']}"):
                        st.session_state.selected_customer = customer['id']
                        st.rerun()
                with col2:
                    if st.button("✏️ دەستکاری", key=f"edit_{customer['id']}"):
                        st.session_state.editing_customer = customer['id']
                        st.rerun()
                with col3:
                    if st.button("🗑️ سڕینەوە", key=f"delete_{customer['id']}"):
                        data['customers'].remove(customer)
                        save_data(data)
                        st.success(f"کڕیار {customer['name']} سڕایەوە")
                        st.rerun()
                with col4:
                    # پرینتی ڕاستەوخۆ بۆ هەر کڕیارێک
                    if st.button("🖨️ پرینت", key=f"print_{customer['id']}", use_container_width=True):
                        try:
                            pdf_path = create_customer_pdf_arabic(customer)
                            if open_pdf_for_printing(pdf_path):
                                st.success("✅ PDF بۆ پرینت نێردرا!")
                            else:
                                st.error("❌ نەتوانرا بکرێتەوە. تکایە دابەزێنە و پرینتی بکە")
                        except Exception as e:
                            st.error(f"هەڵە: {e}")
                
                # دوگمەی PDF بۆ دابەزاندن
                if st.button("📄 دابەزاندنی PDF", key=f"pdf_{customer['id']}", use_container_width=True):
                    try:
                        pdf_path = create_customer_pdf_arabic(customer)
                        with open(pdf_path, 'rb') as f:
                            pdf_bytes = f.read()
                        
                        st.download_button(
                            label="📥 دابەزاندن",
                            data=pdf_bytes,
                            file_name=f"{customer['name']}_تقرير.pdf",
                            mime="application/pdf",
                            key=f"download_{customer['id']}",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"هەڵە: {e}")
                
                # دەستکاری
                if st.session_state.editing_customer == customer['id']:
                    st.markdown("---")
                    st.markdown("### ✏️ دەستکاری کڕیار")
                    
                    with st.form(key=f"edit_form_{customer['id']}"):
                        c1, c2 = st.columns(2)
                        with c1:
                            new_name = st.text_input("ناو:", value=customer['name'])
                            new_model = st.text_input("مۆبایل:", value=customer['phone_model'])
                            new_phone = st.text_input("ژمارە:", value=customer['phone_number'])
                        with c2:
                            new_total = st.number_input("نرخی گشتی:", value=customer['total_amount'], step=1000)
                            new_down = st.number_input("پێشەکی:", value=customer['down_payment'], step=1000)
                            new_monthly = st.number_input("قیست:", value=customer['monthly_payment'], step=1000)
                        
                        new_notes = st.text_area("تێبینی:", value=customer['notes'])
                        
                        if st.form_submit_button("💾 خەزنکردن", use_container_width=True):
                            customer['name'] = new_name
                            customer['phone_model'] = new_model
                            customer['phone_number'] = new_phone
                            customer['total_amount'] = new_total
                            customer['down_payment'] = new_down
                            customer['monthly_payment'] = new_monthly
                            customer['remaining'] = new_total - customer['paid_amount']
                            customer['notes'] = new_notes
                            save_data(data)
                            st.session_state.editing_customer = None
                            st.success("✅ زانیارییەکان نوێ کرانەوە")
                            st.rerun()

# ================================
# تاب ٣: تۆمارکردنی پارە
# ================================
with tab3:
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    st.markdown("<h3>💵 تۆمارکردنی پارەی وەرگیراو</h3>", unsafe_allow_html=True)
    
    if not data['customers']:
        st.info("هیچ کڕیارێک نییە.")
    else:
        customer_names = [f"{c['name']} - {c['phone_model']} (ماوە: {c['remaining']:,} د.ع)" for c in data['customers']]
        selected = st.selectbox("👤 کڕیار هەڵبژێرە:", customer_names)
        
        if selected:
            customer_index = customer_names.index(selected)
            customer = data['customers'][customer_index]
            
            st.markdown(f"""
            <div style='background: #16213e; padding: 1rem; border-radius: 12px; margin: 1rem 0;'>
                <p><b>👤 ناو:</b> {customer['name']}</p>
                <p><b>📱 مۆبایل:</b> {customer['phone_model']}</p>
                <p><b>💰 نرخی گشتی:</b> {customer['total_amount']:,} د.ع</p>
                <p><b>✅ وەرگیراو:</b> {customer['paid_amount']:,} د.ع</p>
                <p><b>⏳ ماوە:</b> {customer['remaining']:,} د.ع</p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.form("add_payment", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    amount = st.number_input("💰 بڕی پارە (دینار):", min_value=0, max_value=customer['remaining'], step=1000)
                with col2:
                    payment_date = st.date_input("📅 بەروار:", value=datetime.now())
                
                notes = st.text_input("📝 تێبینی:", placeholder="قیستی مانگی ...")
                
                if st.form_submit_button("✅ تۆمارکردنی پارە", use_container_width=True):
                    if amount <= 0:
                        st.error("❌ بڕی پارە پێویستە")
                    elif amount > customer['remaining']:
                        st.error("❌ بڕی پارە زیاترە لە پارەی ماوە")
                    else:
                        payment = {
                            "amount": amount,
                            "date": payment_date.strftime("%Y-%m-%d"),
                            "notes": notes
                        }
                        
                        customer['payments'].append(payment)
                        customer['paid_amount'] += amount
                        customer['remaining'] = customer['total_amount'] - customer['paid_amount']
                        
                        if customer['remaining'] <= 0:
                            customer['status'] = 'paid'
                        
                        save_data(data)
                        st.success(f"✅ {amount:,} د.ع تۆمار کرا")
                        st.balloons()
                        st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# ================================
# تاب ٤: هەناردەکردن و پرینت
# ================================
with tab4:
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    st.markdown("<h3>📤 هەناردەکردن و پرینت</h3>", unsafe_allow_html=True)
    
    if not data['customers']:
        st.info("هیچ کڕیارێک نییە.")
    else:
        # PDF بۆ هەمووان
        st.markdown("#### 📄 ڕاپۆرتی هەموو کڕیاران")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📄 دروستکردنی PDF بۆ هەمووان", use_container_width=True):
                try:
                    pdf_path = create_all_customers_pdf_arabic(data)
                    st.session_state.saved_pdf_path = pdf_path
                    with open(pdf_path, 'rb') as f:
                        pdf_bytes = f.read()
                    
                    st.download_button(
                        label="📥 دابەزاندنی PDF",
                        data=pdf_bytes,
                        file_name=f"تقرير_جميع_العملاء_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf",
                        key="download_all",
                        use_container_width=True
                    )
                    st.success("✅ PDF دروست کرا! دابەزێنە یان پرینتی بکە")
                except Exception as e:
                    st.error(f"هەڵە: {e}")
        
        with col2:
            if st.button("🖨️ پرینتی هەموو کڕیاران", use_container_width=True):
                try:
                    pdf_path = create_all_customers_pdf_arabic(data)
                    if open_pdf_for_printing(pdf_path):
                        st.success("✅ PDF بۆ پرینت نێردرا! لە دیالۆگی پرینت OK بکە")
                    else:
                        st.error("❌ نەتوانرا بکرێتەوە. تکایە PDF دابەزێنە و پرینتی بکە")
                except Exception as e:
                    st.error(f"هەڵە: {e}")
        
        # ئامار
        st.markdown("---")
        st.markdown("#### 📊 ئاماری گشتی")
        
        paid_count = len([c for c in data['customers'] if c['status'] == 'paid'])
        unpaid_count = len(data['customers']) - paid_count
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class='stat-card'>
                <p>👥 کڕیار</p>
                <h2>{len(data['customers'])}</h2>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class='stat-card'>
                <p>✅ پڕکراوە</p>
                <h2>{paid_count}</h2>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class='stat-card'>
                <p>⏳ ماوە</p>
                <h2>{unpaid_count}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        # ڕێنمایی پرینت
        st.markdown("---")
        st.markdown("""
        <div class='info-box'>
            <h4>💡 ڕێنمایی پرینت:</h4>
            <ul>
                <li>PDF دروست بکە</li>
                <li>دابەزێنە یان ڕاستەوخۆ پرینتی بکە</li>
                <li>ئەگەر پرینتەرەکەت بلوتوزە، دڵنیا بە کە بەستراوە</li>
                <li>لە دیالۆگی پرینت، پرینتەری بلوتوز هەڵبژێرە</li>
                <li>بۆ پرینت، دوگمەی پرینت لە سەرەوە یان لە ناو کڕیارەکەدا کلیک بکە</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # ڕێگایەکی تر بۆ پرینت
        st.markdown("---")
        st.markdown("#### 🖨️ پرینتی ڕاستەوخۆ بە بەکارهێنانی JavaScript")
        
        if st.button("🖨️ پرینتی پەڕە", use_container_width=True):
            st.markdown("""
            <script>
                window.print();
            </script>
            """, unsafe_allow_html=True)
            st.info("لە دیالۆگی پرینت، 'Save as PDF' یان پرینتەرەکەت هەڵبژێرە")
    
    st.markdown("</div>", unsafe_allow_html=True)

# ================================
# فووەتەر
# ================================
st.markdown("---")
st.markdown(f"""
<div class='footer'>
    <p>📱 <b>محمد فۆن</b> - سیستەمی قەرزی مۆبایل</p>
    <p style='font-size:0.8rem;'>دوایین نوێکردنەوە: {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>
</div>
""", unsafe_allow_html=True)
