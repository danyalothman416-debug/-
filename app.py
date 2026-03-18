import streamlit as st
import pandas as pd
import os
import urllib.parse
from datetime import datetime
import plotly.express as px
import folium
from streamlit_folium import st_folium
import uuid
import requests

# ---------------- APP CONFIG ----------------
st.set_page_config(page_title="Golden Delivery", layout="wide", initial_sidebar_state="collapsed")

DB_FILE = "deliveries.csv"

# ---------------- GLOBAL STATE ----------------
if "app_state" not in st.session_state:
    st.session_state.app_state = {
        "language": "English 🇬🇧",
        "theme": "Dark",
        "page": "home"
    }

def set_language(lang): st.session_state.app_state["language"] = lang
def set_theme(theme): st.session_state.app_state["theme"] = theme
def set_page(p): st.session_state.app_state["page"] = p

def get_lang(): return st.session_state.app_state["language"]
def get_theme(): return st.session_state.app_state["theme"]
def get_page(): return st.session_state.app_state["page"]

# ---------------- LANGUAGE SYSTEM ----------------
languages = {
    "English 🇬🇧": {
        "dir":"ltr","align":"left","theme_label":"Theme","light":"Light","dark":"Dark",
        "title":"Golden Delivery","subtitle":"Fastest delivery in Kirkuk",
        "name":"Customer Name","phone":"Phone","area":"Area","address":"Address",
        "submit":"Submit Order","track":"Track Order","status":"Status",
        "home":"Home","offers":"Offers","profile":"Profile"
    },
    "العربية 🇮🇶": {
        "dir":"rtl","align":"right","theme_label":"المظهر","light":"فاتح","dark":"داكن",
        "title":"جولدن دليفري","subtitle":"أسرع توصيل في كركوك",
        "name":"اسم الزبون","phone":"رقم الهاتف","area":"المنطقة","address":"العنوان",
        "submit":"إرسال الطلب","track":"تتبع الطلب","status":"الحالة",
        "home":"الرئيسية","offers":"العروض","profile":"الحساب"
    },
    "کوردی 🇭🇺": {
        "dir":"rtl","align":"right","theme_label":"ڕووکار","light":"ڕوون","dark":"تاریک",
        "title":"گۆڵدن دلیڤەری","subtitle":"خێراترین گەیاندن لە کەرکوک",
        "name":"ناوی کڕیار","phone":"ژمارە","area":"گەڕەک","address":"ناونیشان",
        "submit":"ناردن","track":"شوێنکەوتن","status":"دۆخ",
        "home":"سەرەکی","offers":"داشکاندن","profile":"هەژمار"
    }
}

L = languages[get_lang()]

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("⚙️ Settings")

    lang = st.selectbox("🌐 Language", list(languages.keys()),
                        index=list(languages.keys()).index(get_lang()))
    set_language(lang)

    theme = st.radio(L['theme_label'], [L['light'], L['dark']],
                     index=1 if get_theme()=="Dark" else 0)
    set_theme("Dark" if theme==L['dark'] else "Light")

    st.divider()
    st.subheader("📄 About")
    st.write("Golden Delivery System - Kirkuk")

    st.subheader("⚖️ Policy")
    st.write("All deliveries are validated within Kirkuk zones.")

# ---------------- THEME ----------------
is_dark = get_theme()=="Dark"

bg = "#0e1117" if is_dark else "#ffffff"
text = "#ffffff" if is_dark else "#000000"

st.markdown(f"""
<style>
html, body {{
    background-color:{bg};
    color:{text};
}}
.nav {{
    position:fixed; bottom:10px; width:100%;
    display:flex; justify-content:space-around;
}}
button {{
    border-radius:15px;
}}
</style>
""", unsafe_allow_html=True)

# ---------------- DATA ----------------
def load():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE, dtype={"phone":str})
    return pd.DataFrame(columns=[
        "id","date","name","phone","area","address","status"
    ])

def save(df): df.to_csv(DB_FILE,index=False)

# ---------------- KIRKUK FULL DATABASE ----------------
KIRKUK_DB = {
    "Rahimawa":[35.4950,44.3910],
    "Iskan":[35.4820,44.3980],
    "Azadi":[35.4750,44.4050],
    "Baghdad Road":[35.4520,44.3680],
    "Taseen":[35.4510,44.3750],
    "Wasit":[35.4180,44.3620],
    "Kurdistan":[35.5050,44.4010],
    "Musalla":[35.4650,44.3950],
    "Arafa":[35.4880,44.3550],
    "Domiz":[35.4250,44.3850],
    "Huzairan":[35.4150,44.3750],
    "Panja Ali":[35.4650,44.4350],
    "Shoraw":[35.4700,44.3600],
    "Laylan":[35.4100,44.4200],
    "Yaychi":[35.4300,44.3000],
    "Askari":[35.4600,44.3900],
    "Qadisiyah":[35.4500,44.4000],
    "1 Haziran":[35.4200,44.3700],
    "2 Haziran":[35.4180,44.3720]
}

# ---------------- TELEGRAM ----------------
def send_telegram(msg):
    TOKEN = "PUT_TOKEN"
    CHAT_ID = "PUT_CHAT_ID"
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                      data={"chat_id":CHAT_ID,"text":msg})
    except:
        pass

# ---------------- HOME ----------------
if get_page()=="home":

    st.title(L["title"])
    st.caption(L["subtitle"])

    with st.form("order"):
        name = st.text_input(L["name"])
        phone = st.text_input(L["phone"])
        area = st.selectbox(L["area"], list(KIRKUK_DB.keys()))
        address = st.text_input(L["address"])

        if st.form_submit_button(L["submit"]):

            if area not in KIRKUK_DB:
                st.error("Invalid Area")
                st.stop()

            df = load()

            order_id = str(uuid.uuid4())[:8]

            new = pd.DataFrame([{
                "id":order_id,
                "date":datetime.now(),
                "name":name,
                "phone":phone,
                "area":area,
                "address":address,
                "status":"Pending"
            }])

            df = pd.concat([df,new])
            save(df)

            msg = f"Order {order_id} - {name} - {area}"

            wa = f"https://wa.me/?text={urllib.parse.quote(msg)}"

            st.success(f"Saved ✅ {order_id}")
            st.markdown(f"[WhatsApp]({wa})")

            send_telegram(msg)

# ---------------- TRACK ----------------
elif get_page()=="track":
    st.subheader(L["track"])
    oid = st.text_input("ID")

    if oid:
        df = load()
        res = df[df["id"]==oid]
        if not res.empty:
            st.success(res.iloc[0]["status"])

# ---------------- PROFILE ----------------
elif get_page()=="profile":
    st.subheader(L["profile"])
    phone = st.text_input(L["phone"])
    if phone:
        df = load()
        st.dataframe(df[df["phone"]==phone])

# ---------------- ADMIN ----------------
if st.query_params.get("role")=="boss":
    if st.text_input("Password",type="password")=="admin123":
        data = load()
        st.dataframe(data)

        st.subheader("Analytics")
        st.bar_chart(data["status"].value_counts())

# ---------------- MAP ----------------
st.divider()
m = folium.Map(location=[35.47,44.39],zoom_start=12)

for k,v in KIRKUK_DB.items():
    folium.Marker(v,popup=k).add_to(m)

st_folium(m,use_container_width=True)

# ---------------- NAV ----------------
st.markdown("<br><br><br>",unsafe_allow_html=True)

c1,c2,c3 = st.columns(3)
with c1:
    if st.button("🏠"): set_page("home"); st.rerun()
with c2:
    if st.button("🔍"): set_page("track"); st.rerun()
with c3:
    if st.button("👤"): set_page("profile"); st.rerun()
