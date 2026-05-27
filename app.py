import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from io import BytesIO
import base64
import warnings
warnings.filterwarnings('ignore')

# ================== ڕێکخستنی پەڕە ==================
st.set_page_config(
    page_title="سیستەمی دوکانی مۆبایل",
    page_icon="📱",
    layout="wide"
)

# ================== دۆخی سێشن ==================
if 'sales' not in st.session_state:
    st.session_state.sales = pd.DataFrame(columns=['بەرهەم', 'نرخ', 'کات', 'کڕیار', 'نرخی کۆتایی'])

if 'inventory' not in st.session_state:
    st.session_state.inventory = pd.DataFrame(columns=['کەلوپەل', 'دانە', 'نرخی کڕین'])

if 'customers' not in st.session_state:
    st.session_state.customers = pd.DataFrame(columns=['ناو', 'مۆبایل', 'کۆی کڕین'])

# ================== فانکشنی یارمەتیدەر ==================
def add_sale(product, price, customer):
    new_sale = pd.DataFrame({
        'بەرهەم': [product],
        'نرخ': [price],
        'کات': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        'کڕیار': [customer],
        'نرخی کۆتایی': [price]
    })
    st.session_state.sales = pd.concat([st.session_state.sales, new_sale], ignore_index=True)
    return True

def export_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

# ================== شریتی لاتەنیشت ==================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/shop.png", width=80)
    st.title("📱 مێنیو")
    
    menu = st.selectbox("بەش هەڵبژێرە:", [
        "🏠 داشبۆرد",
        "💰 فرۆشتن",
        "📦 کۆگا",
        "👥 کڕیاران",
        "📊 ڕاپۆرت"
    ])

# ================== ناوەڕۆکی سەرەکی ==================
st.title("📱 سیستەمی بەڕێوەبردنی دوکانی مۆبایل")

# ================== داشبۆرد ==================
if menu == "🏠 داشبۆرد":
    st.header("🏠 داشبۆرد")
    
    col1, col2, col3 = st.columns(3)
    
    total_sales = st.session_state.sales['نرخی کۆتایی'].sum() if not st.session_state.sales.empty else 0
    col1.metric("💰 کۆی فرۆشتن", f"${total_sales:,.2f}")
    
    total_customers = len(st.session_state.customers)
    col2.metric("👥 کڕیاران", total_customers)
    
    total_products = len(st.session_state.inventory)
    col3.metric("📦 بەرهەمەکان", total_products)
    
    # گراف
    if not st.session_state.sales.empty:
        st.subheader("📈 فرۆشتنەکان")
        fig = px.bar(st.session_state.sales, x='بەرهەم', y='نرخ', title='فرۆشتن بەپێی بەرهەم')
        st.plotly_chart(fig, use_container_width=True)

# ================== فرۆشتن ==================
elif menu == "💰 فرۆشتن":
    st.header("💰 فرۆشتنی نوێ")
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.form("sale_form"):
            product = st.text_input("📱 ناوی بەرهەم")
            price = st.number_input("💵 نرخ ($)", min_value=0.0, step=10.0)
            customer = st.text_input("👤 ناوی کڕیار")
            
            if st.form_submit_button("✅ تۆمارکردن"):
                if product and price > 0 and customer:
                    add_sale(product, price, customer)
                    st.success(f"✅ فرۆشرا بە ${price:,.2f}")
                    st.balloons()
                else:
                    st.error("❌ هەموو خانەکان پڕ بکەرەوە")
    
    with col2:
        st.subheader("📋 دوایین فرۆشتنەکان")
        if not st.session_state.sales.empty:
            st.dataframe(st.session_state.sales.tail(5), use_container_width=True)
        else:
            st.info("هیچ فرۆشتنێک نییە")

# ================== کۆگا ==================
elif menu == "📦 کۆگا":
    st.header("📦 بەڕێوەبردنی کۆگا")
    
    tab1, tab2 = st.tabs(["➕ زیادکردن", "📋 لیست"])
    
    with tab1:
        with st.form("inventory_form"):
            col1, col2 = st.columns(2)
            with col1:
                item = st.text_input("🏷️ ناوی کەلوپەل")
                qty = st.number_input("📦 ژمارە", min_value=1, step=1)
            with col2:
                price = st.number_input("💰 نرخی کڕین", min_value=0.0, step=10.0)
            
            if st.form_submit_button("➕ زیادکردن"):
                if item and qty > 0:
                    new_item = pd.DataFrame({
                        'کەلوپەل': [item],
                        'دانە': [qty],
                        'نرخی کڕین': [price]
                    })
                    st.session_state.inventory = pd.concat([st.session_state.inventory, new_item], ignore_index=True)
                    st.success(f"✅ {qty} دانە {item} زیاد کرا!")
    
    with tab2:
        if not st.session_state.inventory.empty:
            st.dataframe(st.session_state.inventory, use_container_width=True)
            
            # هەناردەکردن
            if st.button("📥 هەناردەکردن بۆ Excel"):
                excel_data = export_excel(st.session_state.inventory)
                b64 = base64.b64encode(excel_data).decode()
                href = f'<a href="data:application/octet-stream;base64,{b64}" download="inventory.xlsx">📥 کلیک بکە بۆ داگرتن</a>'
                st.markdown(href, unsafe_allow_html=True)
        else:
            st.info("کۆگا بەتاڵە")

# ================== کڕیاران ==================
elif menu == "👥 کڕیاران":
    st.header("👥 بەڕێوەبردنی کڕیاران")
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.form("customer_form"):
            name = st.text_input("👤 ناوی کڕیار")
            phone = st.text_input("📞 ژمارەی مۆبایل")
            
            if st.form_submit_button("➕ زیادکردن"):
                if name:
                    new_customer = pd.DataFrame({
                        'ناو': [name],
                        'مۆبایل': [phone],
                        'کۆی کڕین': [0]
                    })
                    st.session_state.customers = pd.concat([st.session_state.customers, new_customer], ignore_index=True)
                    st.success(f"✅ کڕیار {name} زیاد کرا!")
    
    with col2:
        st.subheader("📋 لیستی کڕیاران")
        if not st.session_state.customers.empty:
            st.dataframe(st.session_state.customers, use_container_width=True)
        else:
            st.info("هیچ کڕیارێک نییە")

# ================== ڕاپۆرت ==================
elif menu == "📊 ڕاپۆرت":
    st.header("📊 ڕاپۆرتەکان")
    
    total_sales = st.session_state.sales['نرخی کۆتایی'].sum() if not st.session_state.sales.empty else 0
    total_inventory_value = st.session_state.inventory['نرخی کڕین'].sum() if not st.session_state.inventory.empty else 0
    
    col1, col2 = st.columns(2)
    col1.metric("💰 کۆی فرۆشتن", f"${total_sales:,.2f}")
    col2.metric("💎 کۆی کۆگا", f"${total_inventory_value:,.2f}")
    
    st.subheader("📋 هەموو فرۆشتنەکان")
    if not st.session_state.sales.empty:
        st.dataframe(st.session_state.sales, use_container_width=True)
        
        if st.button("📥 هەناردەکردنی ڕاپۆرت"):
            excel_data = export_excel(st.session_state.sales)
            b64 = base64.b64encode(excel_data).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="sales_report.xlsx">📥 کلیک بکە بۆ داگرتن</a>'
            st.markdown(href, unsafe_allow_html=True)
    else:
        st.info("هیچ فرۆشتنێک نییە")

# ================== پێوە ==================
st.markdown("---")
st.markdown("""
    <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px;">
        <p>📱 سیستەمی بەڕێوەبردنی دوکانی مۆبایل | وەشانی سادەکراو</p>
    </div>
""", unsafe_allow_html=True)
