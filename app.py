import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os

# --- 1. ڕێکخستنی سەرەکی ---
st.set_page_config(page_title="سیستەمی گەیاندنی کەرکوک", layout="wide")

ADMIN_PASSWORD = "dr_danyal_2024" 
DB_FILE = "global_deliveries.csv"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["کڕیار", "دوکان", "مۆبایل", "نرخ", "ناونیشان"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

# --- 2. فۆرمی وەسڵ (بۆ هەمووان) ---
st.title("📦 فۆرمی تۆمارکردنی وەسڵ")

with st.form("delivery_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        customer = st.text_input("ناوی کڕیار")
        shop = st.text_input("ناوی دوکان")
        price = st.number_input("نرخی کاڵا (دینار)", min_value=0, step=250)
    with col2:
        phone = st.text_input("ژمارەی مۆبایل")
        address = st.text_input("ناونیشان")
    
    submit = st.form_submit_button("ناردنی وەسڵ ✅")
    
    if submit and customer:
        current_df = load_data()
        new_row = pd.DataFrame([{"کڕیار": customer, "دوکان": shop, "مۆبایل": phone, "نرخ": price, "ناونیشان": address}])
        updated_df = pd.concat([current_df, new_row], ignore_index=True)
        save_data(updated_df)
        st.success("وەسڵەکەت بە سەرکەوتوویی نێردرا. سوپاس!")

# --- 3. بەشی بەڕێوەبەر (بێ دەنگ و شاردراوە) ---
with st.sidebar:
    # لێرەدا ناوەکەمان گۆڕیوە بۆ شتێکی ئاسایی وەک 'تایبەتمەندی'
    password = st.text_input("کۆد:", type="password", help="بۆ بەکارهێنانی تایبەت")

if password == ADMIN_PASSWORD:
    st.markdown("---")
    st.header("👨‍⚕️ داتاکانی دکتۆر دانیال")
    
    df_to_show = load_data()
    
    if not df_to_show.empty:
        # نەخشە
        map_center = [35.4676, 44.3921]
        m = folium.Map(location=map_center, zoom_start=12)
        for _, row in df_to_show.iterrows():
            folium.Marker(
                location=map_center,
                popup=f"کڕیار: {row['کڕیار']}<br>بڕ: {row['نرخ']}",
                icon=folium.Icon(color="red")
            ).add_to(m)
        st_folium(m, height=400, width=None)

        # خشتە
        st.dataframe(df_to_show, use_container_width=True)
        
        if st.button("🗑 سڕینەوەی هەموو وەسڵەکان"):
            save_data(pd.DataFrame(columns=["کڕیار", "دوکان", "مۆبایل", "نرخ", "ناونیشان"]))
            st.rerun()
    else:
        st.write("لیستەکە خاڵییە.")

# لێرەدا بەشە 'else'ەکەمان سڕیوەتەوە، کەواتە ئەگەر کۆدەکە هەڵە بێت یان بەتاڵ بێت، هیچی زیادە پیشان نادات
