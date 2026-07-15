import streamlit as st
from streamlit_option_menu import option_menu
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="بەڕێوەبەرایەتی پرۆژە",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide sidebar completely
st.markdown("""
<style>
    [data-testid="stSidebar"][aria-expanded="true"] {
        display: none;
    }
    [data-testid="stSidebar"][aria-expanded="false"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Naskh+Arabic:wght@400;500;700;800&display=swap');
    
    * {
        font-family: 'Noto Naskh Arabic', serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        background-attachment: fixed;
    }
    
    /* Header styles */
    .main-header {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 25px;
        padding: 25px;
        margin-bottom: 25px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        text-align: center;
    }
    
    .app-title {
        color: white;
        font-size: 2.8rem;
        font-weight: 800;
        margin: 0;
        direction: rtl;
        text-shadow: 0 0 20px rgba(102, 126, 234, 0.5);
    }
    
    .app-subtitle {
        color: rgba(255, 255, 255, 0.8);
        font-size: 1.2rem;
        direction: rtl;
        margin-top: 10px;
    }
    
    /* Navigation menu */
    .nav-menu {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 10px;
        margin-bottom: 30px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Custom card */
    .custom-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.3);
        transition: all 0.3s ease;
    }
    
    .custom-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 50px rgba(102, 126, 234, 0.4);
    }
    
    .card-title {
        color: #302b63;
        font-weight: 700;
        font
