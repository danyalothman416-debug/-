import streamlit as st

# ١. دیزاینی گشتی
st.set_page_config(page_title="My App", page_icon="📱", layout="centered")

# ٢. بەکارهێنانی CSS بۆ ئەوەی وەک ئەپ دەربکەوێت (شێوەی کارت)
st.markdown("""
    <style>
    .stApp { background-color: #f0f2f6; }
    .css-1r6slp0 { padding: 1rem; }
    </style>
""", unsafe_allow_html=True)

# ٣. ناوەڕۆکی لاپەڕە
st.title("📱 ئەپی من")

# بەکارهێنانی کۆنتەینەر بۆ ئەوەی وەک "کارت" دەربکەوێت
with st.container(border=True):
    st.subheader("چوونە ژوورەوە")
    st.write("تکایە وشەی نهێنی بنووسە")
    
    password = st.text_input("وشەی نهێنی", type="password", label_visibility="collapsed")
    
    if st.button("چوونە ژوورەوە", use_container_width=True):
        if password == "123": # وشەی نهێنیەکەت لێرە دابنێ
            st.success("سەرکەوتوو بوو!")
            st.balloons()
        else:
            st.error("وشەی نهێنی هەڵەیە")

# ٤. فووتەری سادە
st.markdown("<center>وەشانی ١.٠</center>", unsafe_allow_html=True)
