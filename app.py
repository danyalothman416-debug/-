import streamlit as st
import pandas as pd
import os

# --- 1. ڕێکخستنی لاپەڕە و ستایل ---
st.set_page_config(page_title="بەڕێوەبەری قەرزەکان", layout="centered")

st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #1a1a1a !important;
        direction: rtl; text-align: right;
        color: white;
    }
    .stButton > button {
        width: 100%;
        background-color: #4ea88d !important;
        color: white !important;
        border-radius: 8px;
    }
    .debt-card {
        background-color: #262626;
        padding: 15px;
        border-radius: 10px;
        border-right: 5px solid #4ea88d;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. بەڕێوەبردنی داتا (CSV) ---
FILE_NAME = "my_debts.csv"

def load_data():
    if os.path.exists(FILE_NAME):
        return pd.read_csv(FILE_NAME)
    return pd.DataFrame(columns=["ناو", "بڕی قەرز", "بەروار"])

def save_data(df):
    df.to_csv(FILE_NAME, index=False)

# --- 3. ڕووکاری بەرنامەکە ---
st.title("💸 سیستەمی قەرزەکان")

# بەشی زیادکردنی قەرز
with st.expander("➕ زیادکردنی قەرزی نوێ"):
    with st.form("debt_form", clear_on_submit=True):
        name = st.text_input("ناوی کەسەکە")
        amount = st.number_input("بڕی قەرز (دینار)", min_value=0, step=250)
        date = st.date_input("بەروار")
        submit = st.form_submit_button("تۆمارکردن")
        
        if submit and name:
            df = load_data()
            new_row = pd.DataFrame([[name, amount, str(date)]], columns=["ناو", "بڕی قەرز", "بەروار"])
            df = pd.concat([df, new_row], ignore_index=True)
            save_data(df)
            st.success(f"قەرزی {name} تۆمارکرا")
            st.rerun()

# پیشاندانی داتاکان
st.subheader("📊 لیستی قەرزەکان")
df = load_data()

if not df.empty:
    # حیسابکردنی کۆی گشتی
    total = df["بڕی قەرز"].sum()
    st.metric("کۆی گشتی قەرزەکان", f"{total:,} دینار")
    
    # پیشاندانی هەر قەرزێک وەک کارتێک
    for index, row in df.iterrows():
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"""
            <div class="debt-card">
                <b>ناو:</b> {row['ناو']}<br>
                <b>بڕ:</b> {row['بڕی قەرز']:,} دینار | <b>بەروار:</b> {row['بەروار']}
            </div>
            """, unsafe_allow_html=True)
        with col2:
            # دوگمەی سڕینەوە بۆ هەر یەکێک
            if st.button("🗑️", key=f"del_{index}"):
                df = df.drop(index)
                save_data(df)
                st.rerun()
else:
    st.info("هیچ قەرزێک تۆمار نەکراوە.")

st.markdown("---")
st.caption("دروستکراوە لەلایەن دکتۆر دانیال")
