import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import base64

# ================== PAGE CONFIGURATION ==================
st.set_page_config(
    page_title="سیستەمی بەڕێوەبردنی دوکانی مۆبایل",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================== STYLING ==================
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stButton > button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# ================== SESSION STATE INITIALIZATION ==================
if 'sales' not in st.session_state:
    st.session_state.sales = pd.DataFrame(columns=['ناوی بەرهەم', 'نرخ', 'کاتی فرۆشتن', 'ناوی کڕیار'])
if 'inventory' not in st.session_state:
    st.session_state.inventory = pd.DataFrame(columns=['ناوی کەلوپەل', 'ژمارەی دانەکان', 'نرخی کڕین'])
if 'warranty' not in st.session_state:
    st.session_state.warranty = pd.DataFrame(columns=['ناوی کڕیار', 'ژمارەی IMEI', 'بەرواری کۆتایی گەرەنتی'])

# ================== HELPER FUNCTIONS ==================
def add_sale(product_name, price, customer_name):
    new_sale = pd.DataFrame({
        'ناوی بەرهەم': [product_name],
        'نرخ': [float(price)],
        'کاتی فرۆشتن': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        'ناوی کڕیار': [customer_name]
    })
    st.session_state.sales = pd.concat([st.session_state.sales, new_sale], ignore_index=True)
    return True

def add_inventory_item(item_name, stock, purchase_price):
    new_item = pd.DataFrame({
        'ناوی کەلوپەل': [item_name],
        'ژمارەی دانەکان': [int(stock)],
        'نرخی کڕین': [float(purchase_price)]
    })
    st.session_state.inventory = pd.concat([st.session_state.inventory, new_item], ignore_index=True)
    return True

def add_warranty(customer_name, imei, warranty_end_date):
    new_warranty = pd.DataFrame({
        'ناوی کڕیار': [customer_name],
        'ژمارەی IMEI': [imei],
        'بەرواری کۆتایی گەرەنتی': [warranty_end_date]
    })
    st.session_state.warranty = pd.concat([st.session_state.warranty, new_warranty], ignore_index=True)
    return True

def calculate_profit():
    total_sales = st.session_state.sales['نرخ'].sum() if not st.session_state.sales.empty else 0
    total_cost = (st.session_state.inventory['نرخی کڕین'] * st.session_state.inventory['ژمارەی دانەکان']).sum() if not st.session_state.inventory.empty else 0
    profit = total_sales - total_cost
    return total_sales, total_cost, profit

def export_to_excel(df, sheet_name):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    return output.getvalue()

def get_download_link(data, filename):
    b64 = base64.b64encode(data).decode()
    return f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">داگرتنی فایلی Excel</a>'

# ================== SIDEBAR ==================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/shop.png", width=80)
    st.title("📱 مینوی سەرەکی")
    
    menu_options = {
        "تۆمارکردنی فرۆشتن": "💰",
        "کۆگای کەلوپەل": "📦",
        "گەرەنتی": "🛡️",
        "خەمڵاندنی قازانج": "📊"
    }
    
    choice = st.radio(
        "بەشێک هەڵبژێرە:",
        list(menu_options.keys()),
        format_func=lambda x: f"{menu_options[x]} {x}"
    )
    
    st.markdown("---")
    st.markdown("### 📊 کورتەی گشتی")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("کۆی فرۆشتنەکان", f"{len(st.session_state.sales)}")
    with col2:
        st.metric("کەلوپەلەکان", f"{len(st.session_state.inventory)}")
    
    total_sales, total_cost, profit = calculate_profit()
    st.metric("قازانجی پوخت", f"${profit:,.0f}", delta=f"{'+' if profit > 0 else ''}{profit:,.0f}")
    
    st.markdown("---")
    st.markdown("### 💾 پاشەکەوتکردن")
    if st.button("پاشەکەوتکردنی هەموو داتاکان"):
        st.success("داتاکان بە سەرکەوتوویی پاشەکەوت کران!")

# ================== MAIN CONTENT ==================
st.markdown('<p class="main-header">📱 سیستەمی بەڕێوەبردنی دوکانی مۆبایل</p>', unsafe_allow_html=True)

# ================== SALES SECTION ==================
if choice == "تۆمارکردنی فرۆشتن":
    st.header("💰 تۆمارکردنی فرۆشتن")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📝 تۆمارکردنی فرۆشتنی نوێ")
        
        with st.form("sale_form"):
            product_name = st.text_input("📱 ناوی بەرهەم", placeholder="بۆ نموونە: iPhone 15 Pro")
            col_price, col_customer = st.columns(2)
            with col_price:
                price = st.number_input("💵 نرخ ($)", min_value=0.0, step=10.0)
            with col_customer:
                customer_name = st.text_input("👤 ناوی کڕیار", placeholder="ناوی کڕیار")
            
            submit_button = st.form_submit_button("➕ تۆمارکردنی فرۆشتن", use_container_width=True)
            
            if submit_button:
                if product_name and price > 0 and customer_name:
                    if add_sale(product_name, price, customer_name):
                        st.success(f"✅ فرۆشتنی {product_name} بە نرخی ${price:,.2f} بۆ {customer_name} تۆمار کرا!")
                        st.balloons()
                else:
                    st.error("⚠️ تکایە هەموو خانەکان پڕ بکەرەوە!")
    
    with col2:
        st.subheader("📈 نرخەکانی فرۆشتن")
        if not st.session_state.sales.empty:
            fig = px.histogram(st.session_state.sales, x='نرخ', nbins=20, title="دابەشبوونی نرخەکان")
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.subheader("📋 لیستی فرۆشتنەکان")
    
    if not st.session_state.sales.empty:
        # Filters
        col_filter1, col_filter2, col_filter3 = st.columns(3)
        with col_filter1:
            filter_product = st.multiselect("فلتەر بەپێی بەرهەم", st.session_state.sales['ناوی بەرهەم'].unique())
        with col_filter2:
            filter_date = st.date_input("فلتەر بەپێی بەروار", value=None)
        
        # Apply filters
        filtered_sales = st.session_state.sales.copy()
        if filter_product:
            filtered_sales = filtered_sales[filtered_sales['ناوی بەرهەم'].isin(filter_product)]
        
        st.dataframe(filtered_sales, use_container_width=True)
        
        # Summary statistics
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        with col_stat1:
            st.metric("کۆی فرۆشتن", f"{len(filtered_sales)}")
        with col_stat2:
            st.metric("کۆی داهات", f"${filtered_sales['نرخ'].sum():,.2f}")
        with col_stat3:
            st.metric("نرخی مامناوەند", f"${filtered_sales['نرخ'].mean():,.2f}" if not filtered_sales.empty else "$0")
        
        # Export button
        if st.button("📥 هەناردەکردنی فرۆشتنەکان بۆ Excel"):
            excel_data = export_to_excel(filtered_sales, 'Sales')
            st.markdown(get_download_link(excel_data, 'sales_data.xlsx'), unsafe_allow_html=True)
    else:
        st.info("👈 تا ئێستا هیچ فرۆشتنێک تۆمار نەکراوە.")

# ================== INVENTORY SECTION ==================
elif choice == "کۆگای کەلوپەل":
    st.header("📦 کۆگای کەلوپەل")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📝 زیادکردنی کەلوپەلی نوێ")
        
        with st.form("inventory_form"):
            item_name = st.text_input("🏷️ ناوی کەلوپەل", placeholder="بۆ نموونە: شاشەی iPhone 12")
            col_stock, col_price = st.columns(2)
            with col_stock:
                stock = st.number_input("📦 ژمارەی دانەکان", min_value=1, step=1)
            with col_price:
                purchase_price = st.number_input("💰 نرخی کڕین ($)", min_value=0.0, step=1.0)
            
            submit_button = st.form_submit_button("➕ زیادکردنی کەلوپەل", use_container_width=True)
            
            if submit_button:
                if item_name and stock > 0 and purchase_price > 0:
                    if add_inventory_item(item_name, stock, purchase_price):
                        st.success(f"✅ {stock} دانە {item_name} بە نرخی ${purchase_price:,.2f} زیاد کرا!")
                else:
                    st.error("⚠️ تکایە هەموو خانەکان پڕ بکەرەوە!")
    
    with col2:
        st.subheader("📊 کۆگا بەپێی بەها")
        if not st.session_state.inventory.empty:
            inventory_value = st.session_state.inventory.copy()
            inventory_value['کۆی بەها'] = inventory_value['ژمارەی دانەکان'] * inventory_value['نرخی کڕین']
            fig = px.pie(inventory_value, values='کۆی بەها', names='ناوی کەلوپەل', title="دابەشبوونی بەهای کۆگا")
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.subheader("📋 لیستی کەلوپەلەکان")
    
    if not st.session_state.inventory.empty:
        # Add total value column
        inventory_display = st.session_state.inventory.copy()
        inventory_display['کۆی بەها'] = inventory_display['ژمارەی دانەکان'] * inventory_display['نرخی کڕین']
        
        # Low stock alert
        low_stock_items = inventory_display[inventory_display['ژمارەی دانەکان'] < 5]
        if not low_stock_items.empty:
            st.warning(f"⚠️ ئاگاداری: {len(low_stock_items)} کەلوپەل کەمتر لە 5 دانەیان ماوە!")
        
        st.dataframe(inventory_display, use_container_width=True)
        
        # Summary
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        with col_stat1:
            st.metric("کۆی جۆرەکان", f"{len(inventory_display)}")
        with col_stat2:
            st.metric("کۆی دانەکان", f"{inventory_display['ژمارەی دانەکان'].sum():,}")
        with col_stat3:
            st.metric("کۆی بەهای کۆگا", f"${inventory_display['کۆی بەها'].sum():,.2f}")
        
        # Stock management
        st.subheader("🔄 بەڕێوەبردنی کۆگا")
        col_update1, col_update2 = st.columns(2)
        
        with col_update1:
            item_to_update = st.selectbox("کەلوپەل هەڵبژێرە", st.session_state.inventory['ناوی کەلوپەل'])
            if item_to_update:
                current_stock = st.session_state.inventory[st.session_state.inventory['ناوی کەلوپەل'] == item_to_update]['ژمارەی دانەکان'].iloc[0]
                st.info(f"ژمارەی ئێستا: {current_stock}")
        
        with col_update2:
            stock_change = st.number_input("ڕێژەی گۆڕانکاری (+/-)", value=0, step=1)
            if st.button("🔄 نوێکردنەوەی کۆگا") and stock_change != 0:
                idx = st.session_state.inventory[st.session_state.inventory['ناوی کەلوپەل'] == item_to_update].index[0]
                new_stock = current_stock + stock_change
                if new_stock >= 0:
                    st.session_state.inventory.at[idx, 'ژمارەی دانەکان'] = new_stock
                    st.success(f"✅ کۆگا نوێ کرایەوە بۆ {new_stock}")
                    st.rerun()
                else:
                    st.error("❌ ژمارەی دانەکان ناتوانێت سالب بێت!")
        
        if st.button("📥 هەناردەکردنی کۆگا بۆ Excel"):
            excel_data = export_to_excel(inventory_display, 'Inventory')
            st.markdown(get_download_link(excel_data, 'inventory_data.xlsx'), unsafe_allow_html=True)
    else:
        st.info("👈 تا ئێستا هیچ کەلوپەلێک تۆمار نەکراوە.")

# ================== WARRANTY SECTION ==================
elif choice == "گەرەنتی":
    st.header("🛡️ بەدواداچوونی گەرەنتی")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📝 تۆمارکردنی گەرەنتی نوێ")
        
        with st.form("warranty_form"):
            customer_name = st.text_input("👤 ناوی کڕیار", placeholder="ناوی کڕیار")
            col_imei, col_date = st.columns(2)
            with col_imei:
                imei = st.text_input("📱 ژمارەی IMEI", placeholder="15 ژمارە")
            with col_date:
                warranty_end = st.date_input("📅 بەرواری کۆتایی گەرەنتی", 
                                           min_value=datetime.now().date())
            
            submit_button = st.form_submit_button("➕ تۆمارکردنی گەرەنتی", use_container_width=True)
            
            if submit_button:
                if customer_name and imei:
                    if len(imei) == 15 and imei.isdigit():
                        if add_warranty(customer_name, imei, warranty_end.strftime("%Y-%m-%d")):
                            st.success(f"✅ گەرەنتی بۆ {customer_name} تۆمار کرا!")
                    else:
                        st.error("⚠️ ژمارەی IMEI دەبێت 15 ژمارە بێت!")
                else:
                    st.error("⚠️ تکایە هەموو خانەکان پڕ بکەرەوە!")
    
    with col2:
        st.subheader("⚠️ گەرەنتییە نزیکەکان")
        if not st.session_state.warranty.empty:
            today = datetime.now().date()
            warranty_df = st.session_state.warranty.copy()
            warranty_df['بەرواری کۆتایی گەرەنتی'] = pd.to_datetime(warranty_df['بەرواری کۆتایی گەرەنتی']).dt.date
            
            expiring_soon = warranty_df[
                warranty_df['بەرواری کۆتایی گەرەنتی'].apply(lambda x: (x - today).days <= 30)
            ]
            
            if not expiring_soon.empty:
                for _, row in expiring_soon.iterrows():
                    days_left = (row['بەرواری کۆتایی گەرەنتی'] - today).days
                    color = "🔴" if days_left <= 7 else "🟡"
                    st.warning(f"{color} {row['ناوی کڕیار']} - {days_left} ڕۆژ ماوە")
            else:
                st.success("✅ هیچ گەرەنتییەکی نزیک نییە!")
    
    st.markdown("---")
    st.subheader("📋 لیستی گەرەنتییەکان")
    
    if not st.session_state.warranty.empty:
        # Calculate days remaining
        warranty_display = st.session_state.warranty.copy()
        warranty_display['بەرواری کۆتایی گەرەنتی'] = pd.to_datetime(warranty_display['بەرواری کۆتایی گەرەنتی'])
        today = datetime.now()
        warranty_display['ڕۆژەکانی ماوە'] = (warranty_display['بەرواری کۆتایی گەرەنتی'] - today).dt.days
        
        # Color coding
        def color_days(days):
            if days < 0:
                return '🔴 بەسەرچوو'
            elif days <= 7:
                return '🔴 نزیک'
            elif days <= 30:
                return '🟡 ئاگاداری'
            else:
                return '🟢 چالاک'
        
        warranty_display['ڕەوش'] = warranty_display['ڕۆژەکانی ماوە'].apply(color_days)
        
        # Filters
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            status_filter = st.multiselect("فلتەر بەپێی ڕەوش", ['چالاک', 'نزیک', 'ئاگاداری', 'بەسەرچوو'])
        with col_f2:
            customer_filter = st.text_input("گەڕان بەپێی ناوی کڕیار")
        
        filtered_warranty = warranty_display.copy()
        if status_filter:
            filtered_warranty = filtered_warranty[filtered_warranty['ڕەوش'].str.contains('|'.join(status_filter))]
        if customer_filter:
            filtered_warranty = filtered_warranty[filtered_warranty['ناوی کڕیار'].str.contains(customer_filter, case=False)]
        
        st.dataframe(filtered_warranty, use_container_width=True)
        
        # Statistics
        total_active = len(warranty_display[warranty_display['ڕۆژەکانی ماوە'] > 0])
        total_expired = len(warranty_display[warranty_display['ڕۆژەکانی ماوە'] < 0])
        
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        with col_stat1:
            st.metric("کۆی گەرەنتییەکان", f"{len(warranty_display)}")
        with col_stat2:
            st.metric("گەرەنتی چالاک", f"{total_active}")
        with col_stat3:
            st.metric("گەرەنتی بەسەرچوو", f"{total_expired}")
        
        if st.button("📥 هەناردەکردنی گەرەنتییەکان بۆ Excel"):
            excel_data = export_to_excel(filtered_warranty, 'Warranty')
            st.markdown(get_download_link(excel_data, 'warranty_data.xlsx'), unsafe_allow_html=True)
    else:
        st.info("👈 تا ئێستا هیچ گەرەنتییەک تۆمار نەکراوە.")

# ================== PROFIT CALCULATOR SECTION ==================
elif choice == "خەمڵاندنی قازانج":
    st.header("📊 خەمڵاندنی قازانج")
    
    # Calculate profit
    total_sales, total_cost, profit = calculate_profit()
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("کۆی فرۆشتن", f"${total_sales:,.2f}")
        st.caption(f"ژمارەی فرۆشتنەکان: {len(st.session_state.sales)}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("تێچووی کەلوپەل", f"${total_cost:,.2f}")
        st.caption(f"ژمارەی کەلوپەلەکان: {len(st.session_state.inventory)}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        profit_margin = (profit / total_sales * 100) if total_sales > 0 else 0
        st.metric("قازانجی پوخت", f"${profit:,.2f}", delta=f"{profit_margin:.1f}%")
        st.caption("قازانج = کۆی فرۆشتن - تێچووی کەلوپەل")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        sales_count = len(st.session_state.sales)
        avg_sale = total_sales / sales_count if sales_count > 0 else 0
        st.metric("تێکڕای فرۆشتن", f"${avg_sale:,.2f}")
        st.caption(f"تێکڕا بۆ {sales_count} فرۆشتن")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Visualization section
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📈 هێڵکاری قازانج")
        if total_sales > 0 or total_cost > 0:
            fig = go.Figure(data=[
                go.Bar(name='کۆی فرۆشتن', x=['دارایی'], y=[total_sales], marker_color='green'),
                go.Bar(name='تێچووی کەلوپەل', x=['دارایی'], y=[total_cost], marker_color='red'),
                go.Bar(name='قازانجی پوخت', x=['دارایی'], y=[profit], marker_color='blue')
            ])
            fig.update_layout(
                barmode='group',
                height=400,
                title="پوختەی دارایی"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("داتا بەردەست نییە بۆ دروستکردنی هێڵکاری")
    
    with col_right:
        st.subheader("📊 شیکاری فرۆشتنەکان")
        if not st.session_state.sales.empty:
            sales_by_product = st.session_state.sales.groupby('ناوی بەرهەم')['نرخ'].sum().reset_index()
            fig = px.pie(sales_by_product, values='نرخ', names='ناوی بەرهەم', 
                        title="دابەشبوونی فرۆشتن بەپێی بەرهەم")
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("داتای فرۆشتن بەردەست نییە")
    
    st.markdown("---")
    
    # Detailed breakdown
    st.subheader("📋 شیکاری وردەکاری")
    
    tab1, tab2 = st.tabs(["📈 ڕێژەی قازانج", "💰 باشترین فرۆشتنەکان"])
    
    with tab1:
        if total_sales > 0:
            profit_percentage = (profit / total_sales) * 100
            st.write(f"**ڕێژەی قازانج:** {profit_percentage:.2f}%")
            
            # Recommendations
            if profit_percentage > 30:
                st.success("🎉 زۆر باشە! ڕێژەی قازانجت زۆر بەرزە.")
            elif profit_percentage > 15:
                st.info("👍 باشە. ڕێژەی قازانجت لە ئاستێکی باشدایە.")
            else:
                st.warning("⚠️ پێویستە ڕێژەی قازانجت باشتر بکەیت.")
        else:
            st.info("داتا بەردەست نییە")
    
    with tab2:
        if not st.session_state.sales.empty:
            top_sales = st.session_state.sales.nlargest(10, 'نرخ')[['ناوی بەرهەم', 'نرخ', 'ناوی کڕیار']]
            st.dataframe(top_sales, use_container_width=True)
        else:
            st.info("هیچ فرۆشتنێک تۆمار نەکراوە")
    
    # Export
    st.markdown("---")
    if st.button("📥 هەناردەکردنی ڕاپۆرتی قازانج"):
        profit_data = pd.DataFrame({
            'بەش': ['کۆی فرۆشتن', 'تێچووی کەلوپەل', 'قازانجی پوخت', 'ڕێژەی قازانج'],
            'بڕ': [total_sales, total_cost, profit, f"{profit_margin:.2f}%"]
        })
        excel_data = export_to_excel(profit_data, 'Profit Report')
        st.markdown(get_download_link(excel_data, 'profit_report.xlsx'), unsafe_allow_html=True)

# ================== FOOTER ==================
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #666;">
        <p>📱 سیستەمی بەڕێوەبردنی دوکانی مۆبایل | وەشانی ١.٠</p>
        <p>دروستکراوە بۆ بەڕێوەبردنی دوکانی مۆبایل و کەرەستەکان</p>
    </div>
""", unsafe_allow_html=True)
