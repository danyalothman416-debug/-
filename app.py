# ================== ADD THESE TO YOUR EXISTING CODE ==================

# === ADD TO SESSION STATE INITIALIZATION ===
if 'suppliers' not in st.session_state:
    st.session_state.suppliers = pd.DataFrame(columns=[
        'ID', 'ناوی کۆمپانیا', 'بەرپرس', 'مۆبایل', 'ئیمەیڵ', 'ناونیشان', 'جۆری کەلوپەل'
    ])
if 'attendance' not in st.session_state:
    st.session_state.attendance = pd.DataFrame(columns=[
        'کارمەند', 'بەروار', 'کاتی هاتن', 'کاتی ڕۆیشتن', 'کاتژمێر', 'ڕەوش'
    ])
if 'reviews' not in st.session_state:
    st.session_state.reviews = pd.DataFrame(columns=[
        'کڕیار', 'بەرهەم', 'ئەستێرە', 'سەرنج', 'بەروار'
    ])
if 'tasks' not in st.session_state:
    st.session_state.tasks = pd.DataFrame(columns=[
        'ناونیشان', 'وەسف', 'وادە', 'لەولەوەپێشی', 'کارمەند', 'ڕەوش'
    ])
if 'purchase_orders' not in st.session_state:
    st.session_state.purchase_orders = pd.DataFrame(columns=[
        'ID', 'دابینکەر', 'کەلوپەل', 'دانە', 'نرخ', 'کۆی نرخ', 'ڕەوش'
    ])

# === ADD TO MENU OPTIONS IN SIDEBAR ===
menu_options = {
    "💰 فرۆشتن": ["📝 فرۆشتنی نوێ", "📋 لیست", "🧾 فاکتوور", "📷 سکانی بارکۆد"],
    "📦 کۆگا": ["📝 زیادکردن", "📋 لیست", "🔄 بەڕێوەبردن", "🏭 دابینکەران", "📋 داواکاری کڕین"],
    "🛡️ گەرەنتی": ["📝 تۆمارکردن", "📋 لیست", "⚠️ ئاگاداری"],
    "📊 قازانج": ["💰 خەمڵاندن", "📈 هێڵکاری", "📋 ڕاپۆرت", "💸 خەرجی", "📄 ڕاپۆرتی PDF"],
    "👥 کڕیاران": ["📝 زیادکردن", "📋 لیست", "⭐ خاڵ", "🌟 هەڵسەنگاندن"],
    "💳 قیست": ["📝 نوێ", "📋 لیست", "📊 بەدواداچوون", "💵 پارەدان"],
    "🏷️ داشکاندن": ["📝 نوێ", "📋 لیست", "🎉 بۆنە", "📢 هەڵمەتی مارکێتینگ"],
    "👨‍💼 کارمەندان": ["📝 زیادکردن", "📋 لیست", "📊 ئاست", "🕐 ئامادەبوون", "💰 مووچە"],
    "🔧 چاککردنەوە": ["📝 تۆمارکردن", "📋 لیست", "🔄 بەڕێوەبردن"],
    "🚚 گەیاندن": ["📝 نوێ", "📋 لیست"],
    "📱 پەیام": ["📝 ناردن", "📋 مێژوو"],
    "🎫 پشتیوانی": ["📝 تیکت", "📋 تیکتەکان", "💬 چات"],
    "📅 ڕۆژمێر": ["📝 کاری نوێ", "📋 کارەکان", "📅 ڕۆژمێر"],
    "📊 داشبۆرد": ["🎯 سەرەکی", "🔮 پێشبینیکردن", "📊 بەراورد", "📈 شیکاری"],
    "⚙️ ڕێکخستن": ["💾 بەکاپ", "🎨 ڕووکار", "🔔 ئاگادارییەکان"]
}

# === ADD THESE HELPER FUNCTIONS ===
def scan_product_barcode(barcode_text):
    """Scan product by barcode"""
    if not st.session_state.inventory.empty:
        for idx, row in st.session_state.inventory.iterrows():
            if barcode_text.lower() in row['ناوی کەلوپەل'].lower():
                return row
    return None

def calculate_employee_salary(employee_name, month):
    """Calculate monthly salary with bonus and deductions"""
    emp_data = st.session_state.employees[st.session_state.employees['ناوی کارمەند'] == employee_name]
    if emp_data.empty:
        return 0, 0, 0, 0
    
    base_salary = emp_data['مووچە'].iloc[0]
    bonus = emp_data['پاداشت'].iloc[0]
    
    # Calculate absences
    absences = 0
    if not st.session_state.attendance.empty:
        month_attendance = st.session_state.attendance[
            (st.session_state.attendance['کارمەند'] == employee_name) &
            (pd.to_datetime(st.session_state.attendance['بەروار']).dt.month == month)
        ]
        absences = len(month_attendance[month_attendance['ڕەوش'] == 'عدم'])
    
    deduction = (base_salary / 30) * absences
    total = base_salary + bonus - deduction
    return base_salary, bonus, deduction, total

def check_birthdays():
    """Check today's birthdays"""
    today = datetime.now()
    birthdays = []
    if not st.session_state.customers.empty:
        for _, cust in st.session_state.customers.iterrows():
            if cust['ڕێکەوتی لەدایکبوون']:
                bday = pd.to_datetime(cust['ڕێکەوتی لەدایکبوون'])
                if bday.month == today.month and bday.day == today.day:
                    birthdays.append(cust['ناوی کڕیار'])
    return birthdays

# === ADD NEW SECTIONS TO MAIN CONTENT ===

# === BARCODE SCANNER ===
if main_choice == "💰 فرۆشتن" and sub_choice == "📷 سکانی بارکۆد":
    st.header("📷 سکانی بارکۆدی بەرهەم")
    
    barcode = st.text_input("🔢 بارکۆد بکە سکان یان بنووسە", placeholder="ژمارەی بارکۆد...")
    
    if barcode:
        product = scan_product_barcode(barcode)
        if product is not None:
            st.success(f"✅ بەرهەم دۆزرایەوە: {product['ناوی کەلوپەل']}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("نرخی کڕین", f"${product['نرخی کڕین']:,.2f}")
                st.metric("دانە", f"{product['ژمارەی دانەکان']}")
            with col2:
                price = st.number_input("نرخی فرۆشتن", value=float(product['نرخی کڕین']) * 1.3)
                customer = st.text_input("ناوی کڕیار")
            
            if st.button("🛒 فرۆشتنی خێرا") and customer:
                add_sale(product['ناوی کەلوپەل'], price, customer)
                st.success(f"✅ فرۆشرا بە {customer}!")
                st.balloons()
        else:
            st.error("❌ بەرهەم نەدۆزرایەوە!")

# === SUPPLIERS ===
elif main_choice == "📦 کۆگا" and sub_choice == "🏭 دابینکەران":
    st.header("🏭 بەڕێوەبردنی دابینکەران")
    
    with st.form("supplier_form"):
        company = st.text_input("🏢 کۆمپانیا")
        contact = st.text_input("👤 بەرپرس")
        phone = st.text_input("📞 مۆبایل")
        email = st.text_input("📧 ئیمەیڵ")
        address = st.text_input("📍 ناونیشان")
        product_type = st.text_input("📦 جۆری کەلوپەل")
        
        if st.form_submit_button("➕ زیادکردن"):
            if company:
                new_supplier = pd.DataFrame({
                    'ID': [f"SUP{datetime.now().strftime('%Y%m%d%H%M%S')}"],
                    'ناوی کۆمپانیا': [company],
                    'بەرپرس': [contact],
                    'مۆبایل': [phone],
                    'ئیمەیڵ': [email],
                    'ناونیشان': [address],
                    'جۆری کەلوپەل': [product_type]
                })
                st.session_state.suppliers = pd.concat([st.session_state.suppliers, new_supplier], ignore_index=True)
                st.success("✅ دابینکەر زیاد کرا!")
    
    if not st.session_state.suppliers.empty:
        st.subheader("📋 لیستی دابینکەران")
        st.dataframe(st.session_state.suppliers, use_container_width=True)

# === PURCHASE ORDERS ===
elif main_choice == "📦 کۆگا" and sub_choice == "📋 داواکاری کڕین":
    st.header("📋 داواکاری کڕین")
    
    # Auto-suggest low stock items
    low_stock = check_low_stock()
    if not low_stock.empty:
        st.warning(f"⚠️ {len(low_stock)} کەلوپەل کەمە! داواکاری کڕین دروست بکە.")
    
    with st.form("purchase_order"):
        if not st.session_state.suppliers.empty:
            supplier = st.selectbox("دابینکەر", st.session_state.suppliers['ناوی کۆمپانیا'])
        else:
            supplier = st.text_input("ناوی دابینکەر")
        
        if not st.session_state.inventory.empty:
            product = st.selectbox("کەلوپەل", st.session_state.inventory['ناوی کەلوپەل'])
        else:
            product = st.text_input("ناوی کەلوپەل")
        
        quantity = st.number_input("دانە", min_value=1, value=10)
        price = st.number_input("نرخی یەکە ($)", min_value=0.0)
        total = quantity * price
        
        st.info(f"کۆی نرخ: ${total:,.2f}")
        
        if st.form_submit_button("📝 دروستکردنی داواکاری"):
            if supplier and product:
                new_po = pd.DataFrame({
                    'ID': [f"PO{datetime.now().strftime('%Y%m%d%H%M%S')}"],
                    'دابینکەر': [supplier],
                    'کەلوپەل': [product],
                    'دانە': [quantity],
                    'نرخ': [price],
                    'کۆی نرخ': [total],
                    'ڕەوش': ['چاوەڕوان']
                })
                st.session_state.purchase_orders = pd.concat([st.session_state.purchase_orders, new_po], ignore_index=True)
                st.success("✅ داواکاری کڕین تۆمار کرا!")
    
    if not st.session_state.purchase_orders.empty:
        st.subheader("📋 داواکارییەکان")
        st.dataframe(st.session_state.purchase_orders, use_container_width=True)

# === EMPLOYEE ATTENDANCE ===
elif main_choice == "👨‍💼 کارمەندان" and sub_choice == "🕐 ئامادەبوون":
    st.header("🕐 سیستەمی ئامادەبوون")
    
    if not st.session_state.employees.empty:
        employee = st.selectbox("کارمەند", st.session_state.employees['ناوی کارمەند'])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🏃 هاتن", use_container_width=True):
                new_attendance = pd.DataFrame({
                    'کارمەند': [employee],
                    'بەروار': [datetime.now().strftime("%Y-%m-%d")],
                    'کاتی هاتن': [datetime.now().strftime("%H:%M:%S")],
                    'کاتی ڕۆیشتن': [''],
                    'کاتژمێر': [0],
                    'ڕەوش': ['ئامادە']
                })
                st.session_state.attendance = pd.concat([st.session_state.attendance, new_attendance], ignore_index=True)
                st.success(f"✅ هاتنی {employee} تۆمار کرا!")
        
        with col2:
            if st.button("🚶 ڕۆیشتن", use_container_width=True):
                idx = st.session_state.attendance[
                    (st.session_state.attendance['کارمەند'] == employee) &
                    (st.session_state.attendance['بەروار'] == datetime.now().strftime("%Y-%m-%d"))
                ].index
                if len(idx) > 0:
                    st.session_state.attendance.at[idx[-1], 'کاتی ڕۆیشتن'] = datetime.now().strftime("%H:%M:%S")
                    st.success(f"✅ ڕۆیشتنی {employee} تۆمار کرا!")
                else:
                    st.error("سەرەتا هاتن تۆمار بکە!")
        
        with col3:
            if st.button("❌ عدم", use_container_width=True):
                new_attendance = pd.DataFrame({
                    'کارمەند': [employee],
                    'بەروار': [datetime.now().strftime("%Y-%m-%d")],
                    'کاتی هاتن': [''],
                    'کاتی ڕۆیشتن': [''],
                    'کاتژمێر': [0],
                    'ڕەوش': ['عدم']
                })
                st.session_state.attendance = pd.concat([st.session_state.attendance, new_attendance], ignore_index=True)
                st.warning(f"⚠️ عدمی {employee} تۆمار کرا!")
    
    if not st.session_state.attendance.empty:
        st.subheader("📋 مێژووی ئامادەبوون")
        st.dataframe(st.session_state.attendance.tail(20), use_container_width=True)

# === SALARY CALCULATION ===
elif main_choice == "👨‍💼 کارمەندان" and sub_choice == "💰 مووچە":
    st.header("💰 ژمێریاری مووچە")
    
    if not st.session_state.employees.empty:
        employee = st.selectbox("کارمەند", st.session_state.employees['ناوی کارمەند'])
        month = st.selectbox("مانگ", range(1, 13), index=datetime.now().month - 1)
        
        base, bonus, deduction, total = calculate_employee_salary(employee, month)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("مووچەی بنەڕەتی", f"${base:,.2f}")
        with col2:
            st.metric("پاداشت", f"${bonus:,.2f}", delta=f"+{bonus:,.2f}")
        with col3:
            st.metric("کەمکردنەوە", f"${deduction:,.2f}", delta=f"-{deduction:,.2f}")
        with col4:
            st.metric("💵 کۆی گشتی", f"${total:,.2f}")
        
        if st.button("🖨️ پرینتی مووچە"):
            st.success("📄 فیشەی مووچە ئامادەیە!")

# === CUSTOMER REVIEWS ===
elif main_choice == "👥 کڕیاران" and sub_choice == "🌟 هەڵسەنگاندن":
    st.header("🌟 هەڵسەنگاندنی کڕیاران")
    
    if not st.session_state.customers.empty:
        customer = st.selectbox("کڕیار", st.session_state.customers['ناوی کڕیار'])
        
        # Get customer purchases
        purchases = st.session_state.sales[
            st.session_state.sales['ناوی کڕیار'] == customer
        ]['ناوی بەرهەم'].unique()
        
        if len(purchases) > 0:
            product = st.selectbox("بەرهەم", purchases)
            rating = st.slider("ڕێژە", 1, 5, 5)
            stars = "⭐" * rating + "☆" * (5 - rating)
            st.markdown(f"### {stars}")
            comment = st.text_area("سەرنج")
            
            if st.button("📝 تۆمارکردن"):
                new_review = pd.DataFrame({
                    'کڕیار': [customer],
                    'بەرهەم': [product],
                    'ئەستێرە': [rating],
                    'سەرنج': [comment],
                    'بەروار': [datetime.now().strftime("%Y-%m-%d")]
                })
                st.session_state.reviews = pd.concat([st.session_state.reviews, new_review], ignore_index=True)
                st.success("✅ هەڵسەنگاندن تۆمار کرا!")
                
                if rating <= 2:
                    st.warning("⚠️ ئەم کڕیارە پێویستی بە پەیوەندییە!")
    
    if not st.session_state.reviews.empty:
        st.subheader("📊 ئاماری هەڵسەنگاندنەکان")
        avg_rating = st.session_state.reviews['ئەستێرە'].mean()
        st.metric("تێکڕای ئەستێرە", f"{avg_rating:.1f} ⭐")
        st.dataframe(st.session_state.reviews, use_container_width=True)

# === PAYMENT GATEWAY ===
elif main_choice == "💳 قیست" and sub_choice == "💵 پارەدان":
    st.header("💵 پارەدان")
    
    methods = ["💵 کاش", "💳 کارت", "📱 مۆبایل"]
    method = st.selectbox("شێواز", methods)
    amount = st.number_input("بڕ ($)", min_value=0.0)
    
    if method == "💵 کاش":
        received = st.number_input("پارەی وەرگیراو", min_value=0.0)
        if received > 0:
            change = received - amount
            if change >= 0:
                st.success(f"💰 باقی: ${change:,.2f}")
            else:
                st.error(f"کەمە! ${abs(change):,.2f} ی تر پێویستە")
    
    elif method == "💳 کارت":
        st.text_input("ژمارەی کارت", placeholder="**** **** **** ****")
        st.text_input("CVV", placeholder="***")
        if st.button("💳 پارەدان"):
            st.success("✅ پارەدان ئەنجامدرا!")
    
    elif method == "📱 مۆبایل":
        st.info("📱 ئەپی بانکی بەکاربهێنە")
        if st.button("✅ پشتڕاستکردنەوە"):
            st.success("✅ پارەدان پشتڕاست کرایەوە!")

# === MARKETING CAMPAIGNS ===
elif main_choice == "🏷️ داشکاندن" and sub_choice == "📢 هەڵمەتی مارکێتینگ":
    st.header("📢 هەڵمەتی مارکێتینگ")
    
    campaign_types = ["📱 سۆشیال میدیا", "📧 ئیمەیڵ", "📩 SMS", "🎯 گووگڵ ئەدس"]
    
    with st.form("campaign"):
        name = st.text_input("ناوی هەڵمەت")
        campaign_type = st.selectbox("جۆر", campaign_types)
        budget = st.number_input("بودجە ($)", min_value=0.0)
        
        col1, col2 = st.columns(2)
        with col1:
            start = st.date_input("دەستپێک")
        with col2:
            end = st.date_input("کۆتایی")
        
        if st.form_submit_button("➕ دروستکردن"):
            st.success(f"✅ هەڵمەتی {name} دروست کرا!")
            st.info(f"💰 بودجە: ${budget:,.2f}")
            st.info(f"📅 ماوە: {start} تا {end}")

# === TASK CALENDAR ===
elif main_choice == "📅 ڕۆژمێر":
    if sub_choice == "📝 کاری نوێ":
        st.header("📝 کاری نوێ")
        
        with st.form("task_form"):
            title = st.text_input("ناونیشان")
            desc = st.text_area("وەسف")
            
            col1, col2 = st.columns(2)
            with col1:
                deadline = st.date_input("وادە", min_value=datetime.now().date())
            with col2:
                priority = st.selectbox("لەولەوەپێشی", ["🔴 بەرز", "🟡 مامناوەند", "🟢 نزم"])
            
            if not st.session_state.employees.empty:
                assignee = st.selectbox("کارمەند", st.session_state.employees['ناوی کارمەند'])
            else:
                assignee = "خۆم"
            
            if st.form_submit_button("➕ زیادکردن"):
                new_task = pd.DataFrame({
                    'ناونیشان': [title],
                    'وەسف': [desc],
                    'وادە': [deadline.strftime("%Y-%m-%d")],
                    'لەولەوەپێشی': [priority],
                    'کارمەند': [assignee],
                    'ڕەوش': ['چاوەڕوان']
                })
                st.session_state.tasks = pd.concat([st.session_state.tasks, new_task], ignore_index=True)
                st.success("✅ کار زیاد کرا!")
    
    elif sub_choice == "📋 کارەکان":
        st.header("📋 لیستی کارەکان")
        
        if not st.session_state.tasks.empty:
            # Filter
            status = st.multiselect("ڕەوش", ["چاوەڕوان", "لە ئەنجامدایە", "تەواو"])
            display_tasks = st.session_state.tasks.copy()
            if status:
                display_tasks = display_tasks[display_tasks['ڕەوش'].isin(status)]
            
            for _, task in display_tasks.iterrows():
                with st.expander(f"{task['لەولەوەپێشی']} {task['ناونیشان']} - {task['وادە']}"):
                    st.write(f"**وەسف:** {task['وەسف']}")
                    st.write(f"**کارمەند:** {task['کارمەند']}")
                    st.write(f"**ڕەوش:** {task['ڕەوش']}")
                    
                    new_status = st.selectbox("گۆڕینی ڕەوش", 
                                             ["چاوەڕوان", "لە ئەنجامدایە", "تەواو"],
                                             key=f"status_{task['ناونیشان']}")
                    if st.button("نوێکردنەوە", key=f"update_{task['ناونیشان']}"):
                        idx = st.session_state.tasks[st.session_state.tasks['ناونیشان'] == task['ناونیشان']].index[0]
                        st.session_state.tasks.at[idx, 'ڕەوش'] = new_status
                        st.success("✅ نوێ کرایەوە!")
                        st.rerun()
        else:
            st.info("هیچ کارێک نییە")
    
    elif sub_choice == "📅 ڕۆژمێر":
        st.header("📅 ڕۆژمێر")
        
        today = datetime.now()
        st.subheader(f"📌 ئەمڕۆ - {today.strftime('%A, %B %d, %Y')}")
        
        # Birthday check
        birthdays = check_birthdays()
        if birthdays:
            st.balloons()
            for bday_person in birthdays:
                st.success(f"🎂 ڕۆژی لەدایکبوونی {bday_person} پیرۆزە! 🎉")
        
        # Today's tasks
        if not st.session_state.tasks.empty:
            todays_tasks = st.session_state.tasks[
                st.session_state.tasks['وادە'] == today.strftime("%Y-%m-%d")
            ]
            if not todays_tasks.empty:
                st.markdown("#### کارەکانی ئەمڕۆ:")
                for _, task in todays_tasks.iterrows():
                    st.markdown(f"""
                    <div class="customer-card">
                        <strong>{task['لەولەوەپێشی']}</strong> {task['ناونیشان']}<br>
                        <small>👤 {task['کارمەند']} | ⏰ {task['ڕەوش']}</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("✅ هیچ کارێک بۆ ئەمڕۆ نییە!")

# === PDF REPORT ===
elif main_choice == "📊 قازانج" and sub_choice == "📄 ڕاپۆرتی PDF":
    st.header("📄 دروستکردنی ڕاپۆرتی PDF")
    
    report_type = st.selectbox("جۆری ڕاپۆرت", ["دارایی", "فرۆشتن", "کۆگا", "گشتی"])
    period = st.selectbox("ماوە", ["مانگانە", "سێ مانگە", "ساڵانە"])
    
    with st.expander("⚙️ ڕێکخستن"):
        include_charts = st.checkbox("هێڵکاری", True)
        include_tables = st.checkbox("خشتە", True)
        include_summary = st.checkbox("کورتە", True)
    
    if st.button("📄 دروستکردنی ڕاپۆرت"):
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 20)
            pdf.cell(0, 10, f"Mobile Shop - {report_type} Report", ln=True, align="C")
            pdf.set_font("Arial", "", 12)
            pdf.cell(0, 10, f"Date: {datetime.now().strftime('%Y-%m-%d')}", ln=True)
            pdf.cell(0, 10, f"Period: {period}", ln=True)
            
            if include_summary:
                pdf.ln(10)
                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, "Summary", ln=True)
                pdf.set_font("Arial", "", 12)
                total_sales = st.session_state.sales['نرخی کۆتایی'].sum() if not st.session_state.sales.empty else 0
                pdf.cell(0, 10, f"Total Sales: ${total_sales:,.2f}", ln=True)
            
            if include_tables and not st.session_state.sales.empty:
                pdf.add_page()
                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, "Sales Data", ln=True)
                pdf.set_font("Arial", "", 10)
                for _, row in st.session_state.sales.head(20).iterrows():
                    pdf.cell(0, 8, f"{row['ناوی بەرهەم']} - ${row['نرخی کۆتایی']} - {row['ناوی کڕیار']}", ln=True)
            
            report_data = pdf.output(dest='S').encode('latin-1')
            st.download_button(
                "📥 داگرتنی ڕاپۆرت",
                report_data,
                f"report_{datetime.now().strftime('%Y%m%d')}.pdf",
                "application/pdf"
            )
            st.success("✅ ڕاپۆرت دروست کرا!")
        except Exception as e:
            st.error(f"هەڵە: {e}")

# === ADVANCED ANALYTICS ===
elif main_choice == "📊 داشبۆرد" and sub_choice == "📈 شیکاری":
    st.header("📈 شیکاری پێشکەوتوو")
    
    tabs = st.tabs(["📊 گەیج", "📈 هێڵکاری", "🎯 KPIs"])
    
    with tabs[0]:
        col1, col2 = st.columns(2)
        
        with col1:
            satisfaction = st.session_state.reviews['ئەستێرە'].mean() * 20 if not st.session_state.reviews.empty else 85
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=satisfaction,
                title={'text': "ڕێژەی ڕەزامەندی"},
                gauge={'axis': {'range': [0, 100]},
                       'bar': {'color': "#667eea"},
                       'steps': [{'range': [0, 50], 'color': "#ff4757"},
                                {'range': [50, 75], 'color': "#ffa502"},
                                {'range': [75, 100], 'color': "#2ed573"}]}
            ))
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            total_sales = st.session_state.sales['نرخی کۆتایی'].sum() if not st.session_state.sales.empty else 0
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=total_sales,
                title={'text': "کۆی فرۆشتن"},
                delta={'reference': total_sales * 0.8},
                gauge={'axis': {'range': [0, total_sales * 1.5]},
                       'bar': {'color': "#667eea"}}
            ))
            st.plotly_chart(fig, use_container_width=True)
    
    with tabs[1]:
        if not st.session_state.sales.empty:
            sales_by_month = st.session_state.sales.copy()
            sales_by_month['مانگ'] = pd.to_datetime(sales_by_month['کاتی فرۆشتن']).dt.month
            monthly = sales_by_month.groupby('مانگ')['نرخی کۆتایی'].sum()
            
            fig = px.line(x=monthly.index, y=monthly.values, 
                         labels={'x': 'مانگ', 'y': 'فرۆشتن ($)'},
                         title="ڕەوتی فرۆشتنی مانگانە")
            st.plotly_chart(fig, use_container_width=True)
    
    with tabs[2]:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_customers = len(st.session_state.customers)
            st.metric("👥 کڕیاران", total_customers)
        
        with col2:
            total_products = len(st.session_state.inventory)
            st.metric("📦 بەرهەمەکان", total_products)
        
        with col3:
            total_sales = len(st.session_state.sales)
            st.metric("🛒 فرۆشتنەکان", total_sales)

# === SMART NOTIFICATIONS ===
elif main_choice == "⚙️ ڕێکخستن" and sub_choice == "🔔 ئاگادارییەکان":
    st.header("🔔 ئاگادارییە زیرەکەکان")
    
    notifications = []
    
    # Low stock
    low_stock = check_low_stock()
    for _, item in low_stock.iterrows():
        notifications.append({
            'type': 'error',
            'msg': f"📦 {item['ناوی کەلوپەل']}: {item['ژمارەی دانەکان']} دانە ماوە!"
        })
    
    # Expiring warranty
    expiring = check_expiring_warranty()
    for _, warranty in expiring.iterrows():
        days = (pd.to_datetime(warranty['بەرواری کۆتایی گەرەنتی']).date() - datetime.now().date()).days
        notifications.append({
            'type': 'warning' if days <= 7 else 'info',
            'msg': f"⏰ گەرەنتی {warranty['ناوی کڕیار']} {days} ڕۆژی ماوە"
        })
    
    # Upcoming installments
    upcoming = check_upcoming_installments()
    for _, inst in upcoming.iterrows():
        notifications.append({
            'type': 'info',
            'msg': f"💳 قیستی {inst['ناوی کڕیار']}: ${inst['مانگانە']:,.2f}"
        })
    
    # Birthdays
    birthdays = check_birthdays()
    for person in birthdays:
        notifications.append({
            'type': 'success',
            'msg': f"🎂 ئەمڕۆ ڕۆژی لەدایکبوونی {person}ە!"
        })
    
    if notifications:
        for notif in notifications:
            if notif['type'] == 'error':
                st.error(notif['msg'])
            elif notif['type'] == 'warning':
                st.warning(notif['msg'])
            elif notif['type'] == 'info':
                st.info(notif['msg'])
            elif notif['type'] == 'success':
                st.success(notif['msg'])
                st.balloons()
    else:
        st.success("✅ هیچ ئاگادارییەک نییە! هەموو شتێک باشە.")
