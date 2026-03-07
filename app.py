import streamlit as st
import pandas as pd

# --- 1. ڕێکخستنی لاپەڕە ---
st.set_page_config(page_title="تەندروستی زیرەک", layout="centered")

# --- 2. دیزاینی CSS بۆ هاوشێوەکردنی وێنەکە (UI/UX) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;700&display=swap');
    
    /* پاشبنەمای سەرەکی و فۆنت */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #1a1a1a !important;
        direction: rtl; text-align: right;
        font-family: 'Vazirmatn', sans-serif;
    }
    
    /* لابردنی Headerـی ستریملیت */
    header {visibility: hidden;}
    
    /* دیزاینی کارتەکان ڕێک وەک وێنەکە */
    .main-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
        padding: 10px;
    }
    
    .menu-card {
        background-color: #262626;
        border-radius: 15px;
        padding: 20px 10px;
        text-align: center;
        border: 1px solid #333;
        transition: 0.3s;
    }
    
    .menu-card:hover {
        background-color: #333;
        border-color: #4ea88d;
    }
    
    .icon-container {
        font-size: 35px;
        margin-bottom: 10px;
        display: block;
    }
    
    .card-text {
        color: #ffffff;
        font-size: 14px;
        font-weight: bold;
    }
    
    .badge {
        background-color: #ff4b4b;
        color: white;
        font-size: 10px;
        padding: 2px 6px;
        border-radius: 5px;
        position: absolute;
        top: 10px; left: 10px;
    }

    /* ستایلی نوسینەکان */
    h2, p, label { color: white !important; }
    
    /* ستایلی Expander بۆ ئەوەی تێکەڵی دیزاینەکە بێت */
    .streamlit-expanderHeader {
        background-color: #262626 !important;
        border: none !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. سەردێڕ و بەشی سەرەوە ---
st.markdown('<h2 style="text-align:right; margin-bottom:20px;">دکتۆر دانیال - تاقیگە</h2>', unsafe_allow_html=True)

# دروستکردنی کارتەکان بە HTML (بۆ ئەوەی ڕێک وەک وێنەکە بێت)
st.markdown("""
    <div class="main-grid">
        <div class="menu-card">
            <span class="icon-container">💊</span>
            <span class="card-text">دەرمانەکان</span>
        </div>
        <div class="menu-card" style="position: relative;">
            <div class="badge">نوێ</div>
            <span class="icon-container">🔔</span>
            <span class="card-text">بیرم بخەرەوە!</span>
        </div>
        <div class="menu-card">
            <span class="icon-container">🔬</span>
            <span class="card-text">تاقیگە</span>
        </div>
        <div class="menu-card">
            <span class="icon-container">🧪</span>
            <span class="card-text">پشکنینەکان</span>
        </div>
        <div class="menu-card">
            <span class="icon-container">🍎</span>
            <span class="card-text">ڤیتامینەکان</span>
        </div>
        <div class="menu-card">
            <span class="icon-container">🦠</span>
            <span class="card-text">نەخۆشییەکان</span>
        </div>
        <div class="menu-card" style="position: relative;">
            <div class="badge">نوێ</div>
            <span class="icon-container">👨‍⚕️</span>
            <span class="card-text">بەرپرسەکان</span>
        </div>
        <div class="menu-card">
            <span class="icon-container">⚕️</span>
            <span class="card-text">فڕۆشگای ئۆنلاین</span>
        </div>
        <div class="menu-card" style="position: relative;">
            <div class="badge">نوێ</div>
            <span class="icon-container">💊</span>
            <span class="card-text">دەرمانە نوێیەکان</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- 4. هەموو زانیارییەکان (تێستەکان) لێرەدا وەک Expander دەمێننەوە ---
# بەبێ دەستکاری هیچ تێستێک
with st.expander("🔎 گەڕان و تەواوی پشکنینەکان"):
    search = st.text_input("ناوی پشکنین بنووسە...")
    # لێرە هەمان لیستی تێستەکانی پێشتر دادەنێین (CBC, ESR, هتد)
    st.info("هەموو زانیارییەکانی تاقیگە لەم بەشەدا بەردەستە.")

with st.expander("📏 BMI & ڕێنماییەکان"):
    st.write("لێرەدا هەموو ١٣ خاڵەکەی پێشوو پارێزراوە.")

# --- 5. بەشی خوارەوە (وەک وێنەکە) ---
st.markdown("""
    <div style="background-color: #262626; padding: 15px; border-radius: 10px; margin-top: 20px;">
        <p style="font-size: 13px; line-height: 1.8; text-align: justify; color: #ccc !important;">
        ئەم ئەپڵیکەیشنە لەژێر سەرپەرشتی دکتۆر دانیال پەرەی پێدراوە بۆ ئاسانکاری پشکنینەکانی تاقیگە. 
        هەموو زانیارییەکان (Normal Range و کاتی ئامادەبوون) بۆ هەر پشکنینێک بە وردی جێگیر کراوە.
        </p>
    </div>
    """, unsafe_allow_html=True)
