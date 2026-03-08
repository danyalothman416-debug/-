import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os

# --- 1. ڕێکخستنی لاپەڕە و ناونیشان ---
st.set_page_config(page_title="سیستەمی گەیاندنی کەرکوک", layout="wide")

st.markdown("""
<div style='text-align:center; font-size:18px; color:gray;'>
Developed by Dr. Danyal & Eng. Ali
</div>
""", unsafe_allow_html=True)

# --- 2. بەڕێوەبردنی داتابەیس (فایلی هاوبەش) ---
# ئەم فایلە هەموو وەسڵەکان لەخۆ دەگرێت بۆ ئەوەی هەمووان بیبینن
DB_FILE = "global_deliveries.csv"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["کڕیار", "دوکان", "مۆبایل", "نرخ", "ناونیشان"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

# بارکردنی داتاکان لە فایلەکەوە بۆ ناو بەرنامەکە
if "df_deliveries" not in st.session_state:
    st.session_state.df_deliveries = load_data()

# --- 3. Sidebar (لای تەنیشت) ---
with st.sidebar:
    st.title("📦 Delivery System - Kirkuk")
    st.info("GPS + Map + Delivery System")
    st.markdown("---")
    # دوگمەی سڕینەوە تەنها لای تۆ بێت باشترە
    if st.button("🗑 پاککردنەوەی هەموو وەسڵەکان"):
        st.session_state.df_deliveries = pd.DataFrame(columns=["کڕیار", "دوکان", "مۆبایل", "نرخ", "ناونیشان"])
        save_data(st.session_state.df_deliveries)
        st.success("هەموو وەسڵەکان سڕانەوە")
        st.rerun()

st.title("📍 Delivery Map & Tracking")

# --- 4. زیادکردنی وەسڵ (Add Delivery) ---
with st.expander("➕ زیادکردنی وەسڵ"):
    with st.form("delivery_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            customer = st.text_input("ناوی کڕیار")
            shop = st.text_input("ناوی دوکان")
            price = st.number_input("نرخی کاڵا (دینار)", min_value=0, step=250)
        with col2:
            phone = st.text_input("ژمارەی مۆبایل")
            address = st.text_input("ناونیشانی کڕیار (بۆ نموونە: ڕەحیماوا)")
        
        submit = st.form_submit_button("ناردنی وەسڵ")
        
        if submit and customer:
            # دروستکردنی داتای نوێ
            new_data = {
                "کڕیار": customer,
                "دوکان": shop,
                "مۆبایل": phone,
                "نرخ": price,
                "ناونیشان": address
            }
            # زیادکردنی بۆ DataFrame و پاشەکەوتکردنی لە فایلەکەدا
            current_df = load_data()
            new_row = pd.DataFrame([new_data])
            updated_df = pd.concat([current_df, new_row], ignore_index=True)
            save_data(updated_df)
            
            st.session_state.df_deliveries = updated_df
            st.success(f"وەسڵی {customer} بە سەرکەوتوویی بۆ هەمووان نێردرا ✅")
            st.rerun()

# --- 5. نەخشە (Map) ---
st.subheader("🗺 نەخشەی گەیاندن")

# چەقی نەخشەکە (کەرکوک)
map_center = [35.4676, 44.3921]
m = folium.Map(location=map_center, zoom_start=12)

# نوێکردنەوەی داتاکان پێش پیشاندان
df_to_show = load_data()

# زیادکردنی نیشانەکان (Markers) بۆ سەر نەخشەکە
for index, row in df_to_show.iterrows():
    folium.Marker(
        location=map_center, # لێرەدا دەتوانیت Lat/Lon دابنێیت ئەگەر هەبێت
        popup=f"کڕیار: {row['کڕیار']}<br>نرخ: {row['نرخ']}<br>ناونیشان: {row['ناونیشان']}",
        tooltip=row['کڕیار'],
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(m)

st_folium(m, height=400, width=None)

# --- 6. لیستی وەسڵەکان (Table) ---
st.subheader("📋 لیستی هەموو وەسڵەکان")
if not df_to_show.empty:
    st.dataframe(df_to_show, use_container_width=True)
    
    # حیسابکردنی کۆی گشتی نرخەکان
    total_price = df_to_show["نرخ"].sum()
    st.metric("کۆی گشتی پارەی وەسڵەکان", f"{total_price:,} دینار")
else:
    st.info("هێشتا هیچ کەسێک وەسڵی تۆمار نەکردووە.")
