import streamlit as st
import pandas as pd
import os
import urllib.parse
from streamlit_js_eval import streamlit_js_eval

# --- 1. ڕێکخستنی لاپەڕە و زمان ---
st.set_page_config(page_title="Golden Delivery", layout="wide")

languages = {
    "کوردی 🇭🇺": {
        "dir": "rtl", "align": "right",
        "title": "GOLDEN DELIVERY ✨",
        "subtitle": "خێراترین و باوەڕپێکراوترین خزمەتگوزاری گەیاندن لە کەرکوک",
        "get_gps_btn": "📍 دۆزینەوەی شوێنەکەم (GPS ئۆتۆماتیکی)",
        "gps_success": "✅ شوێنەکەت بە سەرکەوتوویی وەرگیرا",
        "customer_name": "👤 ناوی کڕیار",
        "shop_name": "🏪 ناوی دوکان",
        "shop_addr": "📍 ناونیشانی دوکان",
        "phone": "📞 ژمارەی مۆبایل",
        "area": "🏘 گەڕەکی کڕیار",
        "full_addr": "🏠 وردەکاری ناونیشان (نزیک کوێیە؟)",
        "price": "💰 نرخ (د.ع)",
        "submit": "تۆمارکردن و ناردنی وەسڵ ✅",
        "wa_btn": "ناردنی زانیاری بۆ ئۆفیس 💬",
        "error": "⚠️ تکایە خانەکان پڕ بکەرەوە",
        "success": "✅ بە سەرکەوتوویی تۆمارکرا",
        "admin_title": "🛠 پانێڵی بەڕێوەبەرایەتی",
        "admin_pass": "پاسۆرد داخڵ بکە",
        "msg_delivered": "سڵاو، داواکارییەکەت گەیشت ✅",
        "msg_onway": "سڵاو، داواکارییەکەت لە ڕێگەیە 🚚"
    }
}

if "selected_lang" not in st.session_state:
    st.session_state.selected_lang = "کوردی 🇭🇺"

col_ref, col_lang, col_space = st.columns([0.5, 1.5, 4])

with col_ref:
    if st.button("🔄"):
        st.rerun()

with col_lang:
    lang_choice = st.selectbox("🌐 Language", list(languages.keys()))
    st.session_state.selected_lang = lang_choice

L = languages[st.session_state.selected_lang]

# --- ٢. گەڕەکەکان ---
KIRKUK_AREAS = sorted([
"ڕەحیماوا","پەنجاعەلی","شۆراو","تەپە","ئیمام قاسم","ئازادی","شۆڕش",
"ڕێگای بەغداد","موسەڵا","تسعین","واسطی","دۆمیز","غرناطة","حوزەیران",
"شیمال","عرفە","کوردستان","دەروازە","ناوەندی شار","ڕووناكی","ئەحمەد ئاغا",
"ئیسکان","قۆریە","حەجیاوا","برایەتی","تەپەی مەلا عەبدوڵا","بێستوون",
"شۆراو نوێ","کۆمەڵگای نیشتەجێبوون","سەربازی","ئەڵماس","بەرلێمان","دەروازەی باکور",
"کەنیسە","حەی سەدام","حەی مەنصور","حەی ئەسرا و مەفقودین","حەی بەعس",
"حەی عەدەن","پەنجای نوێ","شۆراوی کۆن","قادسیە ١","قادسیە ٢","فەیلەق",
"بڵاوەکان","حەی حوسێن","حەی ئەفسەران","کۆمار","شاتیلو","تاریق","حەی خەزرا","ڕاپەڕین"
])

# --- ٣. داتا ---
DB_FILE="deliveries.csv"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE,dtype={"phone":str})
    return pd.DataFrame(columns=["customer","shop","phone","area","address","price","location"])

# --- ٤. ستایل ---
st.markdown(f"""
<style>
html, body, [data-testid="stAppViewContainer"] {{
direction:{L['dir']};
text-align:{L['align']};
}}

.brand-header {{
background: linear-gradient(135deg,#1a1a1a,#333333);
padding:20px;
border-radius:15px;
border-bottom:4px solid #D4AF37;
text-align:center;
margin-bottom:15px;
}}

.brand-title {{
color:#D4AF37;
font-size:28px;
font-weight:bold;
}}
</style>
""",unsafe_allow_html=True)

st.markdown(f"""
<div class="brand-header">
<div class="brand-title">{L["title"]}</div>
<div style="color:white;">{L["subtitle"]}</div>
</div>
""",unsafe_allow_html=True)

# --- ٥. فۆرم ---
with st.form("delivery_form",clear_on_submit=True):

    col1,col2=st.columns(2)

    with col1:
        customer=st.text_input(L['customer_name'])
        shop=st.text_input(L['shop_name'])
        shop_addr=st.text_input(L['shop_addr'])

    with col2:
        phone=st.text_input(L['phone'])
        selected_area=st.selectbox(L['area'],["هەڵبژێرە..."]+KIRKUK_AREAS)
        price=st.number_input(L['price'],min_value=0,step=250)

    full_addr=st.text_input(L['full_addr'])

    st.write("---")

    # --- GPS FIX ---
    gps_link=""

    if st.button(L['get_gps_btn']):
        loc_data = streamlit_js_eval(
            data_key='pos',
            func_name='getCurrentPosition'
        )

        if loc_data:
            lat = loc_data['coords']['latitude']
            lon = loc_data['coords']['longitude']
            gps_link=f"https://www.google.com/maps?q={lat},{lon}"
            st.success(L['gps_success'])

    submit=st.form_submit_button(L['submit'])

    if submit:

        if not customer or not phone or "هەڵبژێرە" in selected_area:
            st.error(L['error'])

        else:

            df=load_data()

            new_row=pd.DataFrame([{
            "customer":customer,
            "shop":shop,
            "phone":phone,
            "area":selected_area,
            "address":full_addr,
            "price":price,
            "location":gps_link
            }])

            pd.concat([df,new_row]).to_csv(DB_FILE,index=False)

            msg=f"""Golden Delivery ✨
📦 داواکاری نوێ
👤 کڕیار: {customer}
🏘 گەڕەک: {selected_area}
📍 نەخشە: {gps_link}
📞 مۆبایل: {phone}
💰 نرخ: {price:,} IQD
"""

            link=f"https://wa.me/9647801352003?text={urllib.parse.quote(msg)}"

            st.success(L['success'])

            st.markdown(
            f'<a href="{link}" target="_blank"><button style="width:100%;background:#25D366;color:white;border:none;padding:12px;border-radius:10px;font-weight:bold;">{L["wa_btn"]}</button></a>',
            unsafe_allow_html=True
            )

# --- ٦. Admin ---
if st.query_params.get("role")=="boss":

    st.divider()
    st.subheader(L['admin_title'])

    if st.text_input(L['admin_pass'],type="password")=="dr_danyal_2024":

        data=load_data()

        if not data.empty:

            st.dataframe(data,use_container_width=True)

            for i,row in data.iterrows():

                with st.expander(f"📦 {row['customer']} - {row['area']}"):

                    c1,c2=st.columns(2)

                    with c1:

                        m1=urllib.parse.quote(
                        f"سڵاو {row['customer']}\n{L['msg_delivered']}\nGolden Delivery ✨")

                        st.markdown(
                        f'<a href="https://wa.me/{row["phone"]}?text={m1}" target="_blank"><button style="width:100%;background:#4CAF50;color:white;border:none;padding:8px;border-radius:5px;">✅ گەیشت</button></a>',
                        unsafe_allow_html=True
                        )

                    with c2:

                        m2=urllib.parse.quote(
                        f"سڵاو {row['customer']}\n{L['msg_onway']}\nGolden Delivery ✨")

                        st.markdown(
                        f'<a href="https://wa.me/{row["phone"]}?text={m2}" target="_blank"><button style="width:100%;background:#FF9800;color:white;border:none;padding:8px;border-radius:5px;">🚚 لە ڕێگەیە</button></a>',
                        unsafe_allow_html=True
                        )

st.markdown("""
<div style="text-align:center;padding:10px;">
📞 0780 135 2003 | 0772 195 9922
</div>
""",unsafe_allow_html=True)
