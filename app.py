import streamlit as st

# ========== ڕێکخستنی پەڕە ==========
st.set_page_config(
    page_title="ئەپەکەم",
    page_icon="🏠",
    layout="wide"
)

# ========== HTML Tag ی گۆگڵ ==========
st.markdown('<meta name="google-site-verification" content="K6kVkF7ESS0d8787HSnrSVWrBjcUD5VdDycTdMa_3HE" />', unsafe_allow_html=True)

# ========== PWA Manifest ==========
st.markdown("""
<link rel="manifest" href="data:application/json;base64,ewogICJuYW1lIjogItin24zYp9mG2YbZhSIsCiAgInNob3J0X25hbWUiOiAi2KfYudio2YrZhdmHIiwKICAic3RhcnRfdXJsIjogIi8iLAogICJkaXNwbGF5IjogInN0YW5kYWxvbmUiLAogICJiYWNrZ3JvdW5kX2NvbG9yIjogIiM2NjdlZWEiLAogICJ0aGVtZV9jb2xvciI6ICIjNzY0YmEyIiwKICAiaWNvbnMiOiBbCiAgICB7CiAgICAgICJzcmMiOiAi8J+agCIsCiAgICAgICJzaXplcyI6ICIxOTJ4MTkyIiwKICAgICAgInR5cGUiOiAiaW1hZ2UvcG5nIgogICAgfQogIF0KfQ==">
<meta name="theme-color" content="#667eea">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="ئەپەکەم">
""", unsafe_allow_html=True)

# ========== CSS بۆ بەکگراوند ==========
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    h1 {
        color: white !important;
        text-align: center !important;
        font-size: 3rem !important;
    }
    
    p, label {
        color: white !important;
    }
    
    .stButton > button {
        background: #4CAF50 !important;
        color: white !important;
        border-radius: 10px !important;
        padding: 10px 30px !important;
        font-size: 1.2rem !important;
    }
    
    [data-testid="stSidebar"] {
        background: #1a1a2e !important;
    }
</style>
""", unsafe_allow_html=True)

# ========== ناوەڕۆکی ئەپەکە ==========
st.title("🏠 بەخێربێیت بۆ ئەپەکەم!")
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("👥 بەکارهێنەران", "1,234", "+12%")
with col2:
    st.metric("💰 فرۆشتن", "$5,678", "+8%")
with col3:
    st.metric("⭐ ڕەزامەندی", "98%", "+2%")

st.markdown("---")

with st.form("form"):
    name = st.text_input("👤 ناوت:")
    email = st.text_input("📧 ئیمەیڵت:")
    send = st.form_submit_button("📩 ناردن")
    
    if send:
        st.success(f"✅ سڵاو {name}! بە سەرکەوتوویی نێردرا!")
        st.balloons()
