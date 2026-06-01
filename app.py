import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os

# ==================== DATA MANAGEMENT ====================
DATA_FILE = "debts_data.json"

def load_data():
    """بارکردنی داتا لە فایلی JSON"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(data):
    """پاشەکەوتکردنی داتا لە فایلی JSON"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ==================== INITIALIZE SESSION ====================
if "customers" not in st.session_state:
    st.session_state.customers = load_data()

# ==================== SIDEBAR ====================
st.sidebar.title("📱 دوکانی مۆبایل")
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "📋 هەڵبژاردن:",
    ["🏠 سەرەکی", "➕ زیادکردنی قەرز", "📊 لیستی قەرزەکان", "🔍 گەڕان", "ℹ️ دەربارە"]
)

# ==================== FUNCTIONS ====================
def add_customer(name, phone, amount, phone_model):
    """زیادکردنی کڕیاری نوێ"""
    customer = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S"),
        "name": name,
        "phone": phone,
        "phone_model": phone_model,
        "amount": amount,
        "paid": 0,
        "remaining": amount,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "transactions": [{
            "date": datetime.now().strftime("%Y-%m-%d"),
            "type": "قەرز",
            "amount": amount,
            "balance": amount
        }]
    }
    st.session_state.customers.append(customer)
    save_data(st.session_state.customers)

def add_payment(customer_id, amount):
    """زیادکردنی پارەدان"""
    for customer in st.session_state.customers:
        if customer["id"] == customer_id:
            customer["paid"] += amount
            customer["remaining"] = customer["amount"] - customer["paid"]
            customer["transactions"].append({
                "date": datetime.now().strftime("%Y-%m-%d"),
                "type": "پارەدان",
                "amount": amount,
                "balance": customer["remaining"]
            })
            break
    save_data(st.session_state.customers)

def calculate_totals():
    """ژماردنی کۆی گشتی"""
    total_debt = sum(c["amount"] for c in st.session_state.customers)
    total_paid = sum(c["paid"] for c in st.session_state.customers)
    total_remaining = sum(c["remaining"] for c in st.session_state.customers)
    return total_debt, total_paid, total_remaining

# ==================== MAIN PAGE ====================
if menu == "🏠 سەرەکی":
    st.title("📱 سیستەمی بەڕێوەبردنی قەرزەکانی دوکانی مۆبایل")
    st.markdown("---")
    
    # Statistics
    total_debt, total_paid, total_remaining = calculate_totals()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💰 کۆی قەرزەکان", f"${total_debt:,.0f}")
    with col2:
        st.metric("✅ پارە دراوەکان", f"${total_paid:,.0f}")
    with col3:
        st.metric("⏳ ماوە", f"${total_remaining:,.0f}", delta="-$"+str(total_remaining) if total_remaining > 0 else "تەواو")
    
    st.markdown("---")
    
    # Recent customers
    st.subheader("🕐 دوایین کڕیارەکان")
    if st.session_state.customers:
        recent = sorted(st.session_state.customers, key=lambda x: x["date"], reverse=True)[:5]
        for customer in recent:
            with st.expander(f"👤 {customer['name']} - {customer['phone_model']}"):
                st.write(f"📞 **ژمارە:** {customer['phone']}")
                st.write(f"💰 **کۆی قەرز:** ${customer['amount']:,.0f}")
                st.write(f"✅ **پارە دراوە:** ${customer['paid']:,.0f}")
                st.write(f"⏳ **ماوە:** ${customer['remaining']:,.0f}")
                progress = customer['paid'] / customer['amount'] if customer['amount'] > 0 else 0
                st.progress(progress)
                st.caption(f"📅 بەروار: {customer['date']}")
    else:
        st.info("👈 هیچ کڕیارێک تۆمار نەکراوە")

# ==================== ADD DEBT ====================
elif menu == "➕ زیادکردنی قەرز":
    st.title("➕ زیادکردنی قەرزی نوێ")
    
    with st.form("add_debt_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("👤 ناوی کڕیار*")
            phone = st.text_input("📞 ژمارەی مۆبایل")
        with col2:
            phone_model = st.text_input("📱 مۆدێلی مۆبایل*")
            amount = st.number_input("💰 بڕی قەرز*", min_value=0.0, step=100.0)
        
        note = st.text_area("📝 تێبینی (ئارەزوومەندانە)")
        
        submitted = st.form_submit_button("💾 تۆمارکردن", use_container_width=True)
        
        if submitted:
            if name and phone_model and amount > 0:
                add_customer(name, phone, amount, phone_model)
                st.success("✅ قەرزەکە بە سەرکەوتویی تۆمار کرا!")
                st.balloons()
            else:
                st.error("❌ تکایە ناو و مۆدێلی مۆبایل و بڕی قەرز پڕ بکەرەوە")

# ==================== DEBT LIST ====================
elif menu == "📊 لیستی قەرزەکان":
    st.title("📊 لیستی هەموو قەرزەکان")
    
    if st.session_state.customers:
        # Filters
        filter_option = st.selectbox(
            "🔍 ڕیزکردن:",
            ["هەمووی", "💸 پارە ماو", "✅ پارە دراو", "⏰ بەپێی بەروار"]
        )
        
        df = pd.DataFrame(st.session_state.customers)
        
        if filter_option == "💸 پارە ماو":
            df = df[df["remaining"] > 0]
        elif filter_option == "✅ پارە دراو":
            df = df[df["remaining"] == 0]
        elif filter_option == "⏰ بەپێی بەروار":
            df = df.sort_values("date", ascending=False)
        
        st.markdown(f"**ژمارەی کڕیارەکان:** {len(df)}")
        
        # Display table
        display_df = df[["name", "phone_model", "amount", "paid", "remaining", "date"]].copy()
        display_df.columns = ["ناو", "مۆبایل", "کۆی قەرز", "دراوە", "ماوە", "بەروار"]
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "کۆی قەرز": st.column_config.NumberColumn(format="$%d"),
                "دراوە": st.column_config.NumberColumn(format="$%d"),
                "ماوە": st.column_config.NumberColumn(format="$%d")
            }
        )
        
        # Manage payments
        st.markdown("---")
        st.subheader("💳 پارەدان")
        
        customer_names = [f"{c['name']} ({c['phone_model']}) - ${c['remaining']:,.0f}" for c in st.session_state.customers if c["remaining"] > 0]
        
        if customer_names:
            selected = st.selectbox("کڕیار هەڵبژێرە:", customer_names)
            payment_amount = st.number_input("💰 بڕی پارەدان:", min_value=0.0, step=50.0)
            
            if st.button("💳 پارەدان", type="primary", use_container_width=True):
                selected_customer = st.session_state.customers[customer_names.index(selected)]
                if payment_amount > 0 and payment_amount <= selected_customer["remaining"]:
                    add_payment(selected_customer["id"], payment_amount)
                    st.success("✅ پارەدان تۆمار کرا!")
                    st.rerun()
                else:
                    st.error("❌ بڕی پارەدان دەبێت لە ماوە کەمتر یان یەکسان بێت")
        else:
            st.success("🎉 هیچ قەرزێکی ماو نییە!")
    else:
        st.info("👈 هیچ کڕیارێک تۆمار نەکراوە")

# ==================== SEARCH ====================
elif menu == "🔍 گەڕان":
    st.title("🔍 گەڕان بەدوای کڕیاردا")
    
    search = st.text_input("🔍 ناوی کڕیار یان مۆدێلی مۆبایل:")
    
    if search:
        results = [c for c in st.session_state.customers if search.lower() in c["name"].lower() or search.lower() in c["phone_model"].lower()]
        
        if results:
            st.success(f"📊 {len(results)} کڕیار دۆزرایەوە")
            for customer in results:
                with st.container():
                    st.markdown(f"### 👤 {customer['name']}")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"📱 **مۆبایل:** {customer['phone_model']}")
                        st.write(f"📞 **ژمارە:** {customer['phone']}")
                    with col2:
                        st.write(f"💰 **قەرز:** ${customer['amount']:,.0f}")
                        st.write(f"✅ **دراوە:** ${customer['paid']:,.0f}")
                    with col3:
                        st.write(f"⏳ **ماوە:** ${customer['remaining']:,.0f}")
                        progress = customer['paid'] / customer['amount'] if customer['amount'] > 0 else 0
                        st.progress(progress)
                    
                    # Transaction history
                    with st.expander("📜 مێژووی وەصڵەکان"):
                        if customer.get("transactions"):
                            trans_df = pd.DataFrame(customer["transactions"])
                            trans_df.columns = ["بەروار", "جۆر", "بڕ", "باڵانس"]
                            st.dataframe(trans_df, use_container_width=True, hide_index=True)
                    
                    st.markdown("---")
        else:
            st.warning("👈 هیچ کڕیارێک نەدۆزرایەوە")

# ==================== ABOUT ====================
elif menu == "ℹ️ دەربارە":
    st.title("ℹ️ دەربارەی سیستەمەکە")
    st.markdown("""
    ### 📱 سیستەمی بەڕێوەبردنی قەرزەکانی دوکانی مۆبایل
    
    **وەشانی 1.0**
    
    **تایبەتمەندییەکان:**
    - ➕ تۆمارکردنی قەرزی کڕیاران
    - 💰 بەڕێوەبردنی پارەدانەکان
    - 📊 بینینی لیستی قەرزەکان
    - 🔍 گەڕان بەدوای کڕیاردا
    - 📜 مێژووی وەصڵەکان
    - 💾 پاشەکەوتکردنی داتاکان
    
    **چۆنیەتی بەکارهێنان:**
    1. لە **زیادکردنی قەرز** قەرزی نوێ تۆمار دەکەیت
    2. لە **لیستی قەرزەکان** دەتوانیت پارەدان تۆمار بکەیت
    3. لە **گەڕان** بەدوای کڕیارێکی دیاریکراو دا بگەڕێیت
    """)

# ==================== FOOTER ====================
st.sidebar.markdown("---")
st.sidebar.caption(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
st.sidebar.caption("© 2024 دوکانی مۆبایل - هەموو مافێک پارێزراوە")
