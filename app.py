# ================== MISSING SECTIONS ==================

# ================== DISCOUNTS SECTION ==================
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
            else:
                st.error("❌ تکایە کۆدێک بنووسە")

elif main_choice == "🏷️ داشکاندن" and sub_choice == "📋 لیستی کۆدەکان":
    st.header("📋 لیستی کۆدی داشکاندنەکان")
    if not st.session_state.discounts.empty:
        st.dataframe(st.session_state.discounts, use_container_width=True)
    else:
        st.info("📭 هیچ کۆدی داشکاندنێک نییە")

# ================== REPAIRS SECTION ==================
elif main_choice == "🔧 چاککردنەوە" and sub_choice == "📝 تۆماری چاککردنەوە":
    st.header("📝 تۆمارکردنی چاککردنەوەی نوێ")
    with st.form("repair_form"):
        col1, col2 = st.columns(2)
        with col1:
            customer_options = [""] + list(st.session_state.customers['ناوی کڕیار'].values) if not st.session_state.customers.empty else [""]
            customer = st.selectbox("👤 ناوی کڕیار", customer_options)
            phone_model = st.text_input("📱 جۆری مۆبایل")
            issue = st.text_area("🔧 کێشە")
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
            else:
                st.error("❌ تکایە هەموو خانەکان پڕ بکەرەوە")

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
        if not filtered.empty:
            repair_to_update = st.selectbox("چاککردنەوە هەڵبژێرە بۆ نوێکردنەوە", filtered['ID'].tolist())
            new_status = st.selectbox("ڕەوشی نوێ", ["چاوەڕوان", "لەژێرکارە", "تەواو بوو", "گەڕێندرایەوە"])
            if st.button("💾 نوێکردنەوەی ڕەوش"):
                idx = st
