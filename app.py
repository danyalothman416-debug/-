import streamlit as st
from streamlit_google_auth import Authenticate

# ئەم زانیاریانە لە Google Cloud Console وەرتگرتووە
client_id = "YOUR_CLIENT_ID.apps.googleusercontent.com"
client_secret = "YOUR_CLIENT_SECRET"
redirect_uri = "https://your-app-name.streamlit.app/" # لینکەکەی ئەپەکەت

authenticator = Authenticate(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    cookie_name="my_cookie",
    cookie_key="secret_key",
    cookie_expiry_days=30
)

# پشکنینی چوونەژوورەوە
if st.session_state.get('connected'):
    st.write("بەخێربێیت! تۆ ئێستا چوویتە ژوورەوە.")
    st.write(f"ناو: {st.session_state['user_info']['name']}")
else:
    authenticator.login()
