import streamlit as st
import pandas as pd
import os
import urllib.parse
from streamlit_js_eval import streamlit_js_eval

# --- 1. ڕێکخستنی لاپەڕە ---
st.set_page_config(page_title="Golden Delivery", layout="wide")

# فەرهەنگی وەرگێڕان (English Added)
languages = {
    "کوردی 🇭🇺": {
        "dir": "rtl", "align": "right",
        "get_gps": "📍 دیاریکردنی شوێنی کڕیار (GPS)",
        "gps_info": "تکایە کلیک لە 'Allow' بکە بۆ وەرگرتنی شوێنەکە.",
        "location_label": "📍 لینکی نەخشە (خۆکار)",
        "title": "GOLDEN DELIVERY ✨",
        "customer_name": "👤 ناوی کڕیار", "phone": "📞 مۆبایل", "area": "🏘 گەڕەک",
        "full_addr": "🏠 ناونیشانی ورد", "price": "💰 نرخ",
        "submit": "تۆمارکردن ✅", "wa_btn": "ناردنی وەسڵ بۆ ئۆفیس 💬",
        "admin_tab": "🛠 بەشی بەڕێوەبەر", "status_sent": "داواکارییەکەت گەیشت ✅", "status_road": "داواکارییەکەت لە ڕێگەیە 🚚"
    },
    "العربية 🇮🇶": {
        "dir": "rtl", "align": "right",
        "get_gps": "📍 تحديد الموقع (GPS)",
        "gps_info": "يرجى الضغط على 'Allow' لتحديد موقعك.",
        "location_label": "📍 رابط الخريطة",
        "title": "گولدن دليفري ✨",
        "customer_name": "👤 اسم الزبون", "phone": "📞 الموبايل", "area": "🏘 المنطقة",
        "full_addr": "🏠 العنوان بالتفصيل", "price": "💰 السعر",
        "submit": "تسجيل ✅", "wa_btn": "إرسال للمكتب 💬",
        "admin_tab": "🛠 قسم الإدارة", "status_sent": "وصلت طلبيتك ✅", "status_road": "طلبيتك في الطريق 🚚"
    },
    "English 🇬🇧": {
        "dir": "ltr", "align": "left",
        "get_gps": "📍 Get Location (GPS)",
        "gps_info": "Please click 'Allow' to get your location.",
        "location_label": "📍 Map Link",
        "title": "GOLDEN DELIVERY ✨",
        "customer_name": "👤 Customer Name", "phone": "📞 Phone", "area": "🏘 Area",
        "full_addr": "🏠 Address Detail", "price": "💰 Price",
        "submit": "Register ✅", "wa_btn": "Send to Office 💬",
        "admin_tab": "🛠 Admin Panel", "status_sent": "Order Delivered ✅", "status_road": "Order is on the way 🚚"
    }
}

if "selected_lang" not in st.session_state:
    st.session_state.selected_lang = "کوردی 🇭🇺"

col_ref, col_lang, col_space = st.columns([0.5, 1.5, 4])
with col_ref:
    if st.button("🔄"): st.rerun()
with col_lang:
    lang_choice = st.selectbox("🌐 Language", list(languages.keys()), index=list(languages.keys()).index(st.session_state.selected_lang))
    st.session_state.selected_lang = lang_choice

L = languages[st.session_state.selected_lang]

# --- جی پی ئێس (GPS) ---
loc = streamlit_js_eval(data_key='pos', func_name='getCurrentPosition', component_value=None)
gps_link = ""
if loc:
    lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
    gps_link = f"https://www.google.com/maps?q={lat},{lon}"

# --- داتا ---
DB_FILE = "deliveries.csv"
def load_data():
    if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE, dtype={"phone": str})
    return pd.DataFrame(columns=["customer", "phone", "area", "address", "price", "location"])

# --- ستایل ---
st.markdown(f"<style>html, body, [data-testid='stAppViewContainer'] {{ direction: {L['dir']}; text-align: {L['align']}; }} .stForm {{ border: 1px solid #D4AF37 !important; border-radius: 15px; }}</style>", unsafe_allow_html=True)

# --- فۆرمی داواکاری ---
st.markdown(f'<h1 style="text-align:center; color:#D4AF37;">{L["title"]}</h1>', unsafe_allow_html=True)

with st.form("main_form"):
    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input(L['customer_name'])
        area = st.text_input(L['area'])
        addr = st.text_input(L['full_addr'])
    with c2:
        tel = st.text_input(L['phone'])
        price = st.number_input(L['price'], step=250)
        loc_input = st.text_input(L['location_label'], value=gps_link)
    
    if st.form_submit_button(L['submit']):
        df = load_data()
        new_data = pd.DataFrame([{"customer": name, "phone": tel, "area": area, "address": addr, "price": price, "location": loc_input}])
        pd.concat([df, new_data]).to_csv(DB_FILE, index=False)
        st.success("Saved!")
        
        # ناردن بۆ ئۆفیس
        wa_msg = f"Golden Delivery ✨\n👤 {name}\n📞 {tel}\n🏘 {area}\n🏠 {addr}\n📍 {loc_input}\n💰 {price:,} IQD"
        wa_link = f"https://wa.me/9647801352003?text={urllib.parse.quote(wa_msg)}"
        st.markdown(f'<a href="{wa_link}" target="_blank"><button style="width:100%; background:#25D366; color:white; border:none; padding:10px; border-radius:10px;">{L["wa_btn"]}</button></a>', unsafe_allow_html=True)

# --- 🛠 بەشی ئەدمین ---
st.divider()
query = st.query_params
if query.get("role") == "boss":
    st.header(L['admin_tab'])
    df_admin = load_data()
    if not df_admin.empty:
        for i, row in df_admin.iterrows():
            with st.expander(f"📦 {row['customer']} - {row['area']}"):
                st.write(f"📞 {row['phone']} | 💰 {row['price']}")
                
                # دوگمەکانی نامە ناردن بۆ کڕیار
                col_a, col_b = st.columns(2)
                with col_a:
                    m1 = urllib.parse.quote(f"سڵاو {row['customer']}\n{L['status_sent']}\nGolden Delivery ✨")
                    st.markdown(f'<a href="https://wa.me/{row["phone"]}?text={m1}" target="_blank"><button style="width:100%; background:#4CAF50; color:white; border:none; border-radius:5px;">✅ گەیشت</button></a>', unsafe_allow_html=True)
                with col_b:
                    m2 = urllib.parse.quote(f"سڵاو {row['customer']}\n{L['status_road']}\nGolden Delivery ✨")
                    st.markdown(f'<a href="https://wa.me/{row["phone"]}?text={m2}" target="_blank"><button style="width:100%; background:#FF9800; color:white; border:none; border-radius:5px;">🚚 لە ڕێگەیە</button></a>', unsafe_allow_html=True)
