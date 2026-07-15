import streamlit as st

# ١. ڕێکخستنی شاشە و شاردنەوەی سایدبار
st.set_page_config(page_title="ئەپی من", layout="centered", initial_sidebar_state="collapsed")

# ٢. کۆدی جوانکاری (CSS) بۆ گۆڕینی شێوەی ئەپەکە
st.markdown("""
    <style>
    /* پاشبنەمای ئەپەکە بە ڕەنگێکی قەشەنگ (شین و مۆر) */
    .stApp {
        background: linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%);
    }
    
    /* شاردنەوەی هێڵی سەرەوەی Streamlit بۆ ئەوەی وەک ئەپی ڕاستەقینە بێت */
    header {visibility: hidden;}
    
    /* جوانکردنی دوگمەی چوونەژوورەوە */
    div.stButton > button {
        width: 100%;
        border-radius: 30px;
        height: 50px;
        background-color: #ffffff;
        color: #4facfe;
        font-size: 18px;
        font-weight: bold;
        border: none;
        box-shadow: 0 8px 15px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    /* جوڵەی دوگمەکە کاتێک پەنجەی دەچێتە سەر */
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        color: #8ec5fc;
    }
    
    /* دیزاینی بۆکسەکانی نووسین */
    div.stTextInput input {
        border-radius: 15px;
        border: 1px solid transparent;
        padding: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    /* ڕەنگی تێکستەکانی سەرەوە */
    .title-text {
        text-align: center;
        color: white;
        font-family: sans-serif;
        margin-top: 40px;
    }
    </style>
""", unsafe_allow_html=True)

# ٣. بەشی سەرەوەی ئەپەکە
st.markdown("<h1 class='title-text'>✨ بەخێربێیت</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: white; font-size: 18px;'>تکایە زانیارییەکانت بنووسە</p>", unsafe_allow_html=True)

st.write("")
st.write("")

# ٤. بۆکسەکانی چوونەژوورەوە
with st.container():
    st.text_input("ئیمەیڵ", placeholder="name@example.com")
    password = st.text_input("وشەی نهێنی", type="password", placeholder="••••••••")
    
    st.write("")
    
    if st.button("🚀 چوونەژوورەوە"):
        if password == "123":
            st.success("سەرکەوتوو بوویت! 🎉")
            st.balloons()
        else:
            st.error("وشەی نهێنی هەڵەیە! ❌")
