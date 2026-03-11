import streamlit as st
import pandas as pd
import os
import urllib.parse
from datetime import datetime

# --- 1. ڕێکخستنی لاپەڕە و زمان ---
st.set_page_config(page_title="Golden Delivery Pro", layout="wide")

languages = {
    "کوردی 🇭🇺": {
        "dir": "rtl", "align": "right",
        "title": "GOLDEN DELIVERY ✨",
        "subtitle": "سیستەمی پێشکەوتووی گەیاندن لە کەرکوک",
        "customer_name": "👤 ناوی کڕیار", 
        "shop_name": "🏪 ناوی دوکان", 
        "shop_addr": "📍 ناونیشانی دوکان",
        "phone": "📞 ژمارەی مۆبایل", 
        "area": "🏘 گەڕەکی کڕیار", 
        "full_addr": "🏠 وردەکاری ناونیشان",
        "item_price": "💰 نرخی کاڵا (د.ع)",
        "delivery_fee": "🚚 کرێی گەیاندن",
        "submit": "تۆمارکردنی داواکاری ✅", 
        "wa_btn": "ناردنی وەسڵ بۆ ئۆفیس 💬",
        "error": "⚠️ تکایە هەموو خانەکان پڕ بکەرەوە", 
        "success": "✅ بە سەرکەوتوویی تۆمارکرا",
        "admin_title": "🛠 پانێڵی کۆنتڕۆڵ", 
        "admin_pass": "پاسۆرد داخڵ بکە",
        "status_pending": "⏳ چاوەڕوان",
        "status_onway": "🚚 لەڕێگەیە",
        "status_delivered": "✅ گەیشت",
        "status_canceled": "❌ گەڕایەوە",
        "stats_total": "کۆی داواکارییەکان",
        "stats_profit": "کۆی قازانجی گەیاندن"
    },
    "العربية 🇮🇶": {
        "dir": "rtl", "align": "right",
        "title": "گولدن دليفري ✨",
        "subtitle": "النظام المتطور للتوصيل في كركوك",
        "customer_name": "👤 اسم الزبون", 
        "shop_name": "🏪 اسم المحل", 
        "shop_addr": "📍 عنوان المحل",
        "phone": "📞 رقم الموبايل", 
        "area": "🏘 منطقة الزبون", 
        "full_addr": "🏠 تفاصيل العنوان",
        "item_price": "💰 سعر البضاعة (د.ع)",
        "delivery_fee": "🚚 أجرة التوصيل",
        "submit": "تسجيل الطلبية ✅", 
        "wa_btn": "إرسال الوصل للمكتب 💬",
        "error": "⚠️ يرجى ملء جميع الحقول", 
        "success": "✅ تم التسجيل بنجاح",
        "admin_title": "🛠 لوحة التحكم", 
        "admin_pass": "أدخل كلمة المرور",
        "status_pending": "⏳ قيد الانتظار",
        "status_onway": "🚚 في الطريق",
        "status_delivered": "✅ تم التوصيل",
        "status_canceled": "❌ ملغي/مرجع",
        "stats_total": "إجمالي الطلبات",
        "stats_profit": "إجمالي أرباح التوصيل"
    },
    "English 🇬🇧": {
        "dir": "ltr", "align": "left",
        "title": "GOLDEN DELIVERY ✨",
        "subtitle": "Advanced Delivery System in Kirkuk",
        "customer_name": "👤 Customer Name", 
        "shop_name": "🏪 Shop Name", 
        "shop_addr": "📍 Shop Address",
        "phone": "📞 Phone Number", 
        "area": "🏘 Customer Area", 
        "full_addr": "🏠 Address Details",
        "item_price": "💰 Item Price (IQD)",
        "delivery_fee": "🚚 Delivery Fee",
        "submit": "Register Order ✅", 
        "wa_btn": "Send to Office 💬",
        "error": "⚠️ Please fill all fields", 
        "success": "✅ Registered Successfully",
        "admin_title": "🛠 Admin Panel", 
        "admin_pass": "Password",
        "status_pending": "⏳ Pending",
        "status_onway": "🚚 On Way",
        "status_delivered": "✅ Delivered",
        "status_canceled": "❌ Canceled",
        "stats_total": "Total Orders",
        "stats_profit": "Total Profit"
    }
}

if "selected_lang" not in st.session_state:
    st.session_state.selected_lang = "کوردی 🇭🇺"

L = languages[st.session_state.selected_lang]

# --- ٢. لیستی گەڕەکەکان (بێ گۆڕانکاری) ---
KIRKUK_AREAS = sorted([
    "ڕەحیماوا", "پەنجاعەلی", "شۆراو", "تەپە", "ئیمام قاسم", "ئازادی", "شۆڕش", 
    "ڕێگای بەغداد", "موسەڵا", "تسعین", "واسطی", "دۆمیز", "غرناطة", "حوزەیران", 
    "شیمال", "عرفە", "کوردستان", "دەروازە", "ناوەندی شار", "ڕووناكی", "ئەحمەد ئاغا",
    "ئیسکان", "قۆریە", "حەجیاوا", "برایەتی", "تەپەی مەلا عەبدوڵا", "بێستوون", 
    "شۆراو نوێ", "کۆمەڵگای نیشتەجێبوون", "سەربازی", "ئەڵماس", "بەرلێمان", "دەروازەی باکور",
    "کەنیسە", "حەی سەدام", "حەی مەنصور", "حەی ئەسرا و مەفقودین", "حەی بەعس",
    "حەی عەدەن", "پەنجای نوێ", "شۆراوی کۆن", "قادسیە ١", "قادسیە ٢", "فەیلەق", 
    "بڵاوەکان", "حەی حوسێن", "حەی ئەفسەران", "کۆمار", "شاتیلو", "تاریق", "حەی خەزرا", "ڕاپەڕین"
])

# --- ٣. بەڕێوەبردنی داتا ---
DB_FILE = "orders_v2.csv"
def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["id", "date", "customer", "shop", "phone", "area", "address", "price", "fee", "status"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

# --- ٤. دیزاین ---
st.markdown(f"""
    <style>
    html, body, [data-testid="stAppViewContainer"] {{ direction: {L['dir']}; text-align: {L['align']}; }}
    .main-card {{ background: #1e1e1e; color: #D4AF37; padding: 20px; border-radius: 15px; border-bottom: 5px solid #D4AF37; text-align: center; margin-bottom: 20px; }}
    .stButton>button {{ width: 100%; border-radius: 10px; font-weight: bold; }}
    .num-fix {{ direction: ltr !important; display: inline-block; }}
    [data-testid="stMetricValue"] {{ color: #D4AF37 !important; }}
    </style>
    """, unsafe_allow_html=True)

st.markdown(f'<div class="main-card"><h1>{L["title"]}</h1><p>{L["subtitle"]}</p></div>', unsafe_allow_html=True)

# --- ٥. بەشەکانی ئەپڵیکەیشن (Tabs) ---
tab1, tab2, tab3 = st.tabs(["📝 فۆرمی داواکاری", "🚚 پانێڵی شۆفێر", "📊 بەڕێوەبەر"])

# --- TAB 1: Merchant (فۆرمی دوکان) ---
with tab1:
    with st.form("merchant_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            customer = st.text_input(L['customer_name'])
            shop = st.text_input(L['shop_name'])
            phone = st.text_input(L['phone'])
        with col2:
            selected_area = st.selectbox(L['area'], ["هەڵبژێرە..."] + KIRKUK_AREAS)
            item_p = st.number_input(L['item_price'], min_value=0, step=1000)
            del_f = st.number_input(L['delivery_fee'], min_value=0, step=500, value=3000)
        
        addr = st.text_input(L['full_addr'])
        submit = st.form_submit_button(L['submit'])

        if submit:
            if not customer or not phone or "هەڵبژێرە" in selected_area:
                st.error(L['error'])
            else:
                df = load_data()
                order_id = len(df) + 1001
                new_data = {
                    "id": order_id, "date": datetime.now().strftime("%Y-%m-%d"),
                    "customer": customer, "shop": shop, "phone": phone,
                    "area": selected_area, "address": addr,
                    "price": item_p, "fee": del_f, "status": L['status_pending']
                }
                df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
                save_data(df)
                st.success(f"{L['success']} - ID: {order_id}")
                
                # وەسڵ بۆ واتسئەپ
                msg = f"Golden Delivery ✨\n📦 وەسڵی ژمارە: {order_id}\n👤 کڕیار: {customer}\n🏪 دوکان: {shop}\n🏘 گەڕەک: {selected_area}\n💰 کۆی گشتی: {item_p + del_f:,} IQD"
                wa_link = f"https://wa.me/9647801352003?text={urllib.parse.quote(msg)}"
                st.markdown(f'<a href="{wa_link}" target="_blank"><button style="width:100%; background:#25D366; color:white; padding:10px; border:none; border-radius:10px;">{L["wa_btn"]}</button></a>', unsafe_allow_html=True)

# --- TAB 2: Driver (پانێڵی شۆفێر) ---
with tab2:
    df_driver = load_data()
    if not df_driver.empty:
        pending_orders = df_driver[df_driver['status'].isin([L['status_pending'], L['status_onway']])]
        for i, row in pending_orders.iterrows():
            with st.expander(f"📦 {row['customer']} - {row['area']} ({row['status']})"):
                st.write(f"📞 {row['phone']} | 📍 {row['address']}")
                st.write(f"💵 وەرگرتن لە کڕیار: **{row['price'] + row['fee']:,}** IQD")
                
                c1, c2, c3 = st.columns(3)
                if c1.button(f"🚚 لەڕێگەیە", key=f"onway_{row['id']}"):
                    df_driver.at[i, 'status'] = L['status_onway']
                    save_data(df_driver)
                    st.rerun()
                if c2.button(f"✅ گەیشت", key=f"del_{row['id']}"):
                    df_driver.at[i, 'status'] = L['status_delivered']
                    save_data(df_driver)
                    st.rerun()
                if c3.button(f"❌ گەڕایەوە", key=f"can_{row['id']}"):
                    df_driver.at[i, 'status'] = L['status_canceled']
                    save_data(df_driver)
                    st.rerun()

# --- TAB 3: Admin (پانێڵی بەڕێوەبەر) ---
with tab3:
    if st.text_input(L['admin_pass'], type="password") == "dr_danyal_2024":
        df_admin = load_data()
        if not df_admin.empty:
            # Stats
            col_s1, col_s2, col_s3 = st.columns(3)
            col_s1.metric(L['stats_total'], len(df_admin))
            delivered_df = df_admin[df_admin['status'] == L['status_delivered']]
            col_s2.metric(L['stats_profit'], f"{delivered_df['fee'].sum():,} IQD")
            col_s3.metric("داواکاری سەرکەوتوو", len(delivered_df))
            
            st.divider()
            st.dataframe(df_admin, use_container_width=True)
            
            if st.button("پاککردنەوەی هەموو داتاکان (Reset)"):
                if os.path.exists(DB_FILE): os.remove(DB_FILE)
                st.rerun()

# گۆڕینی زمان لە خوارەوە
st.sidebar.title("🌐 Settings")
lang = st.sidebar.selectbox("Language", list(languages.keys()), index=list(languages.keys()).index(st.session_state.selected_lang))
if lang != st.session_state.selected_lang:
    st.session_state.selected_lang = lang
    st.rerun()

st.markdown(f'<div style="text-align:center; padding:20px; color:#888;">📞 <span class="num-fix">0780 135 2003</span> | <span class="num-fix">0772 195 9922</span></div>', unsafe_allow_html=True)
