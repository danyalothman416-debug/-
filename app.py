import streamlit as st
import pandas as pd
import os
import urllib.parse

# --- 1. ڕێکخستنی لاپەڕە و دیزاین ---
st.set_page_config(page_title="Golden Delivery", layout="wide")

st.markdown("""
    <style>
    section[data-testid="stSidebar"] { display: none !important; }
    html, body, [data-testid="stAppViewContainer"] { direction: rtl; text-align: right; }
    .brand-header {
        background: linear-gradient(135deg, #1a1a1a 0%, #333333 100%);
        padding: 25px; border-radius: 15px; border-bottom: 4px solid #D4AF37;
        text-align: center; margin-bottom: 20px;
    }
    .brand-title { color: #D4AF37; font-size: 32px; font-weight: bold; }
    .num-fix { direction: ltr !important; display: inline-block !important; color: #D4AF37; font-weight: bold; }
    .install-bar {
        position: fixed; bottom: 0; left: 0; width: 100%;
        background-color: #1a1a1a; color: white; padding: 12px;
        text-align: center; border-top: 3px solid #D4AF37; z-index: 9999;
    }
    .stForm { border: 1px solid #D4AF37 !important; border-radius: 15px !important; padding: 20px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- ٢. لۆژیکی داتا ---
ADMIN_PASSWORD = "dr_danyal_2024" 
DB_FILE = "global_deliveries.csv"
MY_WHATSAPP = "9647801352003" 

# لیستی گەڕەکەکانی کەرکوک
KIRKUK_AREAS = [
    "هەڵبژاردنی گەڕەک...", "ڕەحیماوا", "پەنجاعەلی", "شۆراو", "تەپە", "ئیمام قاسم", 
    "ئازادی", "شۆڕش", "ڕێگای بەغداد", "موسەڵا", "تسعین", "واسطی", "دۆمیز", 
    "غرناطة", "حوزەیران", "شیمال", "عرفە", "کوردستان", "دەروازە", "ناوەندی شار"
]

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE, dtype={"مۆبایل": str})
        # دڵنیابوونەوە لە هەبوونی ستونە پێویستەکان
        columns = ["کڕیار", "ناوی دوکان", "ناونیشانی دوکان", "مۆبایل", "نرخ", "گەڕەک", "ناونیشانی ورد", "دۆخی داواکاری"]
        for col in columns:
            if col not in df.columns:
                df[col] = ""
        return df
    return pd.DataFrame(columns=["کڕیار", "ناوی دوکان", "ناونیشانی دوکان", "مۆبایل", "نرخ", "گەڕەک", "ناونیشانی ورد", "دۆخی داواکاری"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

# --- ٣. ڕووکاری سەرەکی ---

col_title, col_ref = st.columns([5, 1])
with col_ref:
    if st.button("🔄 Refresh"):
        st.rerun()

st.markdown("""
    <div class="brand-header">
        <div class="brand-title">GOLDEN DELIVERY ✨</div>
        <div style="color:white; font-size:14px;">خێراترین و باوەڕپێکراوترین خزمەتگوزاری گەیاندن لە کەرکوک</div>
    </div>
""", unsafe_allow_html=True)

with st.form("delivery_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        customer = st.text_input("👤 ناوی کڕیار")
        shop_name = st.text_input("🏪 ناوی دوکان")
        shop_address = st.text_input("📍 ناونیشانی دوکان")
    with col2:
        phone = st.text_input("📞 ژمارەی مۆبایل")
        selected_area = st.selectbox("🏘 گەڕەکی کڕیار", KIRKUK_AREAS)
        full_address = st.text_input("🏠 وردەکاری ناونیشان (نزیک کوێیە؟)")
        price = st.number_input("💰 نرخ (د.ع)", min_value=0, step=250)
    
    submit = st.form_submit_button("تۆمارکردن و ناردنی وەسڵ ✅")
    
    if submit:
        if not customer or not phone or selected_area == "هەڵبژاردنی گەڕەک...":
            st.error("⚠️ تکایە ناوی کڕیار، مۆبایل و گەڕەک بە دروستی پڕ بکەرەوە")
        else:
            df = load_data()
            new_row = pd.DataFrame([{
                "کڕیار": customer, "ناوی دوکان": shop_name, "ناونیشانی دوکان": shop_address, 
                "مۆبایل": str(phone), "نرخ": price, "گەڕەک": selected_area, 
                "ناونیشانی ورد": full_address, "دۆخی داواکاری": "وەرگیرا 📥"
            }])
            save_data(pd.concat([df, new_row], ignore_index=True))
            
            msg = (f"Golden Delivery ✨\n📦 وەسڵێکی نوێ\n👤 کڕیار: {customer}\n"
                   f"🏘 گەڕەک: {selected_area}\n🏠 ناونیشان: {full_address}\n"
                   f"📞 مۆبایل: {phone}\n💰 نرخ: {price:,} د.ع")
            
            link = f"https://wa.me/{MY_WHATSAPP}?text={urllib.parse.quote(msg)}"
            st.success("✅ بە سەرکەوتوویی تۆمارکرا")
            st.markdown(f'<a href="{link}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:12px; border-radius:10px; font-weight:bold; cursor:pointer;">ناردنی زانیاری بۆ ئۆفیس 💬</button></a>', unsafe_allow_html=True)

st.markdown(f'<div style="text-align:center; padding:15px;">📞 <span class="num-fix">0772 195 9922</span> | <span class="num-fix">0780 135 2003</span></div>', unsafe_allow_html=True)

with st.expander("📲 چۆن ئەپەکە دابەزێنم؟"):
    st.write("لە سەفاری نیشانەی Share دابگرە و Add to Home Screen هەڵبژێرە.")

# --- ٤. بەشی ئەدمینی نهێنی ---
query_params = st.query_params
if query_params.get("role") == "boss":
    st.write("---")
    with st.expander("🛠 بەشی کارگێڕی و کۆنتڕۆڵی داواکارییەکان"):
        if st.text_input("کۆدی نهێنی", type="password", key="admin_final") == ADMIN_PASSWORD:
            df_admin = load_data()
            
            if not df_admin.empty:
                st.metric("💰 کۆی گشتی نرخەکان", f"{df_admin['نرخ'].sum():,} د.ع")
                
                st.subheader("📦 نوێکردنەوەی دۆخی داواکارییەکان")
                for index, row in df_admin.iterrows():
                    col_info, col_status, col_wa = st.columns([2, 1, 1])
                    with col_info:
                        st.write(f"**{row['کڕیار']}** ({row['گەڕەک']})")
                    with col_status:
                        current_status = row["دۆخی داواکاری"] if row["دۆخی داواکاری"] in ["وەرگیرا 📥", "ئامادەیە 📦", "لە ڕێگایە 🚚", "گەیشت ✅"] else "وەرگیرا 📥"
                        new_status = st.selectbox(f"دۆخ", ["وەرگیرا 📥", "ئامادەیە 📦", "لە ڕێگایە 🚚", "گەیشت ✅"], index=["وەرگیرا 📥", "ئامادەیە 📦", "لە ڕێگایە 🚚", "گەیشت ✅"].index(current_status), key=f"sel_{index}")
                        if new_status != row["دۆخی داواکاری"]:
                            df_admin.at[index, "دۆخی داواکاری"] = new_status
                            save_data(df_admin)
                            st.rerun()
                    with col_wa:
                        cust_msg = f"سڵاو {row['کڕیار']} بەڕێز\nداواکارییەکەت لە Golden Delivery ✨\nئێستا لە دۆخی: {new_status} دایە."
                        clean_phone = str(row['مۆبایل']).strip().replace(" ", "")
                        if not clean_phone.startswith("964"):
                            if clean_phone.startswith("0"): clean_phone = "964" + clean_phone[1:]
                            else: clean_phone = "964" + clean_phone
                        
                        wa_link = f"https://wa.me/{clean_phone}?text={urllib.parse.quote(cust_msg)}"
                        st.markdown(f'<a href="{wa_link}" target="_blank">📲 نامە بۆ کڕیار</a>', unsafe_allow_html=True)
                
                st.write("---")
                st.dataframe(df_admin, use_container_width=True)
            
            if st.button("🗑 سڕینەوەی گشت داتاکان"):
                if st.checkbox("دڵنیام"):
                    save_data(pd.DataFrame(columns=["کڕیار", "ناوی دوکان", "ناونیشانی دوکان", "مۆبایل", "نرخ", "گەڕەک", "ناونیشانی ورد", "دۆخی داواکاری"]))
                    st.rerun()
else:
    st.markdown('<div style="text-align:center; opacity:0.2; font-size:10px; padding-bottom:60px;">Golden Delivery v1.4</div>', unsafe_allow_html=True)

st.markdown("""<div class="install-bar">بۆ دابەزاندنی ئەپ: کلیک لە ⎙ یان ⋮ بکە و <b>Add to Home Screen</b> هەڵبژێرە</div>""", unsafe_allow_html=True)
