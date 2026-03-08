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
    /* ئەم بەشە ناوی ناو خشتەکە گەورە و ڕوون دەکاتەوە */
    .stDataFrame div {
        font-size: 16px !important;
        font-weight: bold !important;
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

# --- 2. شریتی لای ڕاست ---
with st.sidebar:
    password = st.text_input("", type="password", placeholder="...")

# --- 3. لاپەڕەی سەرەکی ---
if password == ADMIN_PASSWORD:
    st.header("👨‍⚕️ بەشی بەڕێوەبەر")
    df_to_show = load_data()
    
    if not df_to_show.empty:
        # نەخشە
        map_center = [35.4676, 44.3921]
        m = folium.Map(location=map_center, zoom_start=12)
        for _, row in df_to_show.iterrows():
            folium.Marker(
                location=map_center,
                popup=f"کڕیار: {row['کڕیار']}",
                icon=folium.Icon(color="red")
            ).add_to(m)
        st_folium(m, height=400, width=None)

        st.write("### 📋 لیستی وەسڵەکان")
        
        # --- لێرەدا ناوەکانمان بە گەورەیی ڕێکخستووە ---
        st.table(df_to_show) # بەکارهێنانی st.table لە جیاتی dataframe بۆ ئەوەی ناوەکان جێگیر و ڕوون بن
        
        if st.button("🗑 سڕینەوەی هەموو وەسڵەکان"):
            save_data(pd.DataFrame(columns=["کڕیار", "دوکان", "مۆبایل", "نرخ", "ناونیشان"]))
            st.rerun()
    else:
        st.info("هیچ وەسڵێک نییە.")

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
                save_data(pd.concat([current_df, new_row], ignore_index=True))
                st.success("✅ وەسڵەکەت بە سەرکەوتوویی نێردرا.")
