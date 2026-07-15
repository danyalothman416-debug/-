import streamlit as st

# ١. وشەی نهێنی دابنێ
PASSWORD = "123"

def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        # پەڕەی چوونەژوورەوە
        user_input = st.text_input("وشەی نهێنی بنووسە:", type="password")
        if st.button("چوونەژوورەوە"):
            if user_input == PASSWORD:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("وشەی نهێنی هەڵەیە!")
    else:
        # ئەگەر چوویتە ژوورەوە، ئەمە نیشان بدە
        st.write("بەخێربێیت! تۆ سەرکەوتووانە چوویتە ژوورەوە.")
        if st.button("دەرچوون"):
            st.session_state.logged_in = False
            st.rerun()

main()
