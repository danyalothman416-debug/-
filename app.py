import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os

# --- 1. ڕێکخستنی لاپەڕە ---
st.set_page_config(page_title="سیستەمی گەیاندنی کەرکوک", layout="wide")

st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        direction: rtl;
        text-align: right;
    }
    .stButton>button {
        width: 100%;
        font-size: 18px !important;
    }
    .phone-footer {
        text-align: center;
        padding: 20px;
        background-color: #f0f2f6;
        border-radius: 10px;
        margin-top: 20px;
        font-weight: bold;
        color: #1f77b4;
    }
    </style>
    """, unsafe_allow_html=True)

ADMIN_PASSWORD = "dr_danyal_2024" 
DB_FILE = "global_deliveries.csv"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["کڕیار", "دوکان", "مۆبایل", "نرخ", "ناونیشان"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

# --- 2. لۆژیکی گەڕانەوە ---
if "back_to_home" in st.session_state and st.session_state.back_to_home:
    st.session_state.clear()
    st.rerun()

# --- 3. شریتی لای ڕاست ---
with st.sidebar:
    password = st.text_input("", type="password", placeholder="...", key="admin_pwd_final")

# --- 4. لاپەڕەی سەرەکی ---
if password == ADMIN_PASSWORD:
    st.header("👨‍⚕️ بەشی بەڕێوەبەر")
    df_to_show = load_data()
    
    if not df_to_show.empty:
        map_center = [35.4676, 44.3921]
        m = folium.Map(location=map_center, zoom_start=12)
        for _, row in df_to_show.iterrows():
            folium.Marker(location=map_center, popup=f"کڕیار: {row['کڕیار']}").add_to(m)
        st_folium(m, height=400, width=None)

        st.write("### 📋 لیستی وەسڵەکان")
        st.table(df_to_show) 
        
        if st.button("🗑 سڕینەوەی هەموو وەسڵەکان"):
            save_data(pd.DataFrame(columns=["کڕیار", "دوکان", "مۆبایل", "نرخ", "ناونیشان"]))
            st.rerun()
        
        if st.button("⬅️ گەڕانەوە بۆ لاپەڕەی سەرەکی"):
            st.session_state.back_to_home = True
            st.rerun()
    else:
        st.warning("⚠️ هیچ وەسڵێک لە لیستدا نەماوە.")
        if st.button("⬅️ گەڕانەوە بۆ لاپەڕەی سەرەکی"):
            st.session_state.back_to_home = True
            st.rerun()

else:
    st.title("📦 فۆرمی تۆمارکردنی وەسڵ")
    with st.form("delivery_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            customer = st.text_input("ناوی کڕیار / اسم الزبون")
            shop = st.text_input("ناوی دوکان / اسم المحل")
            price = st.number_input("نرخی کاڵا / سعر البضاعة", min_value=0, step=250)
        with col2:
            phone = st.text_input("ژمارەی مۆبایل / رقم الهاتف")
            address = st.text_input("ناونیشانی ورد / العنوان بالتفصيل")
        
        submit = st.form_submit_button("ناردنی وەسڵ ✅")
        
        if submit:
            if not customer or not shop or not phone or not address:
                st.error("⚠️ تکایە هەموو خانەکان پڕ بکەرەوە!")
            else:
                current_df = load_data()
                new_row = pd.DataFrame([{"کڕیار": customer, "دوکان": shop, "مۆبایل": phone, "نرخ": price, "ناونیشان": address}])
                updated_df = pd.concat([current_df, new_row], ignore_index=True)
                save_data(updated_df)
                st.success("✅ وەسڵەکەت بە سەرکەوتوویی نێردرا.")

    # --- زیادکردنی ژمارە تەلەفۆنەکان لە خوارەوەی فۆرمەکە ---
    st.markdown(f"""
        <div class="phone-footer">
            📞 بۆ پەیوەندی و زانیاری زیاتر:<br>
            <span style="font-size: 20px;">0772 195 9922</span><br>
            <span style="font-size: 20px;">0780 135 2003</span>
        </div>
    """, unsafe_allow_html=True)
