# -*- coding: utf-8 -*-
"""
📱 Smart Mobile Shop System - Daniel Phone
بەشی یەکەم: داشبۆرد و پێکهاتەی سەرەکی
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import streamlit.components.v1 as components

# ⚙️ ڕێکخستنی پەیج
st.set_page_config(
    page_title="Daniel Phone | داشبۆرد",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🎨 CSS بۆ دیزاینی سەردەم
st.markdown("""
<style>
    /* باگراوندی سەرەکی - شینی زۆر تۆخ */
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #141852 50%, #070b34 100%);
    }
    
    /* سایدباڕ */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1137 0%, #0a0e27 100%);
        border-left: 1px solid rgba(30, 144, 255, 0.2);
    }
    
    section[data-testid="stSidebar"] * {
        color: #e0e8ff !important;
    }
    
    /* سەردێڕی سایدباڕ */
    section[data-testid="stSidebar"] h1 {
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
        font-size: 1.8rem !important;
        letter-spacing: 1px;
    }
    
    /* کاردەکان */
    .glass-card {
        background: linear-gradient(135deg, rgba(20, 30, 80, 0.7) 0%, rgba(15, 23, 60, 0.8) 100%);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(30, 144, 255, 0.25);
        box-shadow: 0 8px 32px rgba(0, 20, 80, 0.3);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        margin-bottom: 20px;
    }
    
    .glass-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 15px 40px rgba(0, 100, 255, 0.25);
        border: 1px solid rgba(30, 144, 255, 0.5);
    }
    
    /* ناونیشانی کارد */
    .card-title {
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #6b8cce;
        font-weight: 600;
        margin-bottom: 8px;
    }
    
    .card-value {
        font-size: 36px;
        font-weight: 900;
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    .card-subtitle {
        font-size: 13px;
        color: #5a6fa0;
        margin-top: 5px;
    }
    
    /* هێدەری سەرەکی */
    .main-header {
        font-size: 2.5rem;
        font-weight: 900;
        background: linear-gradient(90deg, #ffffff 0%, #4facfe 50%, #00f2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }
    
    .sub-header {
        color: #6b8cce;
        font-size: 1rem;
        margin-bottom: 30px;
        font-weight: 400;
    }
    
    /* دوگمەکان */
    .stButton > button {
        background: linear-gradient(135deg, #1e90ff 0%, #4facfe 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 25px !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(30, 144, 255, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(30, 144, 255, 0.5) !important;
        background: linear-gradient(135deg, #4facfe 0%, #1e90ff 100%) !important;
    }
    
    /* خشتەکان */
    .dataframe {
        background: rgba(15, 23, 60, 0.6) !important;
        border-radius: 15px !important;
        border: 1px solid rgba(30, 144, 255, 0.2) !important;
    }
    
    /* دیڤایدەر */
    hr {
        border: 1px solid rgba(30, 144, 255, 0.15) !important;
    }
    
    /* هەموو تێکست لایت مۆد */
    .stMarkdown, .stText, p, span, label {
        color: #c5d0f0 !important;
    }
    
    /* مێتریکەکان */
    [data-testid="stMetric"] {
        background: rgba(20, 30, 80, 0.5);
        border-radius: 15px;
        padding: 15px;
        border: 1px solid rgba(30, 144, 255, 0.2);
    }
    
    [data-testid="stMetric"] label {
        color: #6b8cce !important;
    }
    
    [data-testid="stMetric"] div {
        color: #ffffff !important;
        font-weight: 800 !important;
    }
    
    /* ئایکۆنی مۆبایل لە سایدباڕ */
    .logo-emoji {
        font-size: 3rem;
        text-align: center;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# 📊 داتای هەڵبژێردراو (بۆ نموونە)
@st.cache_data
def load_sample_data():
    sales_data = pd.DataFrame({
        'مانگ': ['کانوونی دووەم', 'شوبات', 'ئازار', 'نیسان', 'ئایار', 'حوزەیران'],
        'iPhone': [12, 15, 10, 18, 22, 20],
        'Samsung': [8, 11, 14, 16, 13, 19],
        'Xiaomi': [20, 25, 18, 22, 28, 30]
    })
    
    recent_sales = pd.DataFrame({
        'کڕیار': ['ئارام عەلی', 'سارا محەمەد', 'دڵشاد ئیسماعیل', 'ڕێباز حەمە'],
        'مۆبایل': ['iPhone 15 Pro', 'Samsung S24 Ultra', 'Xiaomi 14 Pro', 'iPhone 14'],
        'نرخ': ['$1,200', '$1,100', '$650', '$580'],
        'ڕێکەوت': ['2026-05-20', '2026-05-19', '2026-05-18', '2026-05-17'],
        'دۆخ': ['تەواو', 'تەواو', 'چاوەڕوان', 'تەواو']
    })
    
    return sales_data, recent_sales

sales_data, recent_sales = load_sample_data()

# ================================
# 📌 سایدباڕ
# ================================
with st.sidebar:
    st.markdown('<div class="logo-emoji">📱</div>', unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center;'>Daniel Phone</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #6b8cce; margin-bottom: 30px;'>سیستەمی زیرەکی بەڕێوەبردن</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    # ناڤیگەیشن
    st.markdown("### 📌 ناڤیگەیشن")
    page = st.radio(
        "",
        ["🏠 داشبۆرد", "📱 مۆبایلەکان", "👥 کڕیاران", "🔧 تەعمیرات", "💰 فرۆشتن", "📦 کۆگا", "🤖 پێشنیاری AI", "📊 ڕاپۆرت"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # پرۆفایلی خێرا
    st.markdown("### 👤 بەڕێوەبەر")
    col1, col2 = st.columns([0.3, 0.7])
    with col1:
        st.markdown("🟢", help="ئۆنلاین")
    with col2:
        st.markdown("**دانیال**")
        st.caption("بەڕێوەبەری دووکان")
    
    st.markdown("---")
    st.caption("© 2026 Daniel Phone • وەشانی 1.0.0")

# ================================
# 📱 ناوەڕۆکی سەرەکی
# ================================
st.markdown(f'<h1 class="main-header">👋 سڵاو، دانیال!</h1>', unsafe_allow_html=True)
st.markdown(f'<p class="sub-header">ڕاپۆرتی ڕۆژانەی دووکان • {datetime.now().strftime("%Y-%m-%d")}</p>', unsafe_allow_html=True)

# --- کارتی ستاتستیکەکان ---
st.markdown("### 📊 پوختەی ئەمڕۆ")
col1, col2, col3, col4 = st.columns(4)

with col1:
    with st.container():
        st.markdown("""
        <div class="glass-card">
            <div class="card-title">💰 کۆی فرۆشتن</div>
            <div class="card-value">$4,850</div>
            <div class="card-subtitle">📈 +12.5% لە دوێنێوە</div>
        </div>
        """, unsafe_allow_html=True)

with col2:
    with st.container():
        st.markdown("""
        <div class="glass-card">
            <div class="card-title">📱 مۆبایلی فرۆشراو</div>
            <div class="card-value">8</div>
            <div class="card-subtitle">🎯 ٤ ئایفۆن • ٣ سامسونگ • ١ شیائۆمی</div>
        </div>
        """, unsafe_allow_html=True)

with col3:
    with st.container():
        st.markdown("""
        <div class="glass-card">
            <div class="card-title">👥 کڕیاری نوێ</div>
            <div class="card-value">12</div>
            <div class="card-subtitle">📋 ٣ کڕیاری تۆمارکراو</div>
        </div>
        """, unsafe_allow_html=True)

with col4:
    with st.container():
        st.markdown("""
        <div class="glass-card">
            <div class="card-title">🔧 تەعمیرات</div>
            <div class="card-value">5</div>
            <div class="card-subtitle">⏳ ٢ لە چاوەڕوانی • ٣ تەواو</div>
        </div>
        """, unsafe_allow_html=True)

# --- گرافی فرۆشتن ---
st.markdown("---")
col_left, col_right = st.columns([2, 1])

with col_left:
    st.markdown("### 📈 هێڵکاری فرۆشتنی ٦ مانگ")
    
    # ئامادەکردنی داتا بۆ پلۆتلی
    sales_melted = sales_data.melt(id_vars=['مانگ'], 
                                    value_vars=['iPhone', 'Samsung', 'Xiaomi'],
                                    var_name='براند', value_name='ژمارە')
    
    fig = px.line(sales_melted, x='مانگ', y='ژمارە', color='براند',
                  color_discrete_map={'iPhone': '#4facfe', 'Samsung': '#a78bfa', 'Xiaomi': '#f59e0b'},
                  markers=True, line_shape='spline')
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#c5d0f0',
        legend_title=None,
        margin=dict(l=20, r=20, t=30, b=20),
        height=350,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(30,144,255,0.1)')
    )
    fig.update_traces(line=dict(width=3), marker=dict(size=8))
    
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.markdown("### 🏆 پڕفرۆشترین ئەمڕۆ")
    
    best_sellers = pd.DataFrame({
        'مۆبایل': ['iPhone 15 Pro', 'Samsung S24', 'Xiaomi 14'],
        'ژمارە': [4, 3, 1]
    })
    
    fig2 = px.bar(best_sellers, x='مۆبایل', y='ژمارە',
                  color='مۆبایل',
                  color_discrete_map={'iPhone 15 Pro': '#4facfe', 'Samsung S24': '#a78bfa', 'Xiaomi 14': '#f59e0b'})
    fig2.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#c5d0f0',
        showlegend=False,
        margin=dict(l=20, r=20, t=30, b=20),
        height=350,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(30,144,255,0.1)')
    )
    fig2.update_traces(marker=dict(borderRadius=8))
    
    st.plotly_chart(fig2, use_container_width=True)

# --- خشتەی دوایین فرۆشتنەکان ---
st.markdown("---")
st.markdown("### 📋 دوایین فرۆشتنەکان")

# ستایلی بۆ خشتەکە
styled_df = recent_sales.style.applymap(lambda x: 'color: #4facfe' if x == 'تەواو' else 'color: #f59e0b', subset=['دۆخ'])
st.dataframe(recent_sales, use_container_width=True, hide_index=True)

# --- دیزاینی فووتەر ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px;">
    <p style="color: #6b8cce; margin: 0;">🚀 دروستکراوە بە ❤️ بۆ <span style="color: #4facfe; font-weight: 700;">Daniel Phone</span></p>
    <p style="color: #4a5a8a; font-size: 12px; margin-top: 5px;">Smart Mobile Shop System v1.0 • 2026</p>
</div>
""", unsafe_allow_html=True)
