import streamlit as st
from groq import Groq

st.set_page_config(page_title="یاریدەدەری AI", page_icon="🤖")

st.title("🤖 یاریدەدەری زیرەکی دەستکرد")
st.write("وەک ئەم وتووێژەی ئێمە، پرسیار بکە و وەڵام وەربگرە!")

# وەرگرتنی کلیلی API لە بەکارهێنەر (لە سایدبار)
with st.sidebar:
    st.header("⚙️ ڕێکخستنەکان")
    api_key = st.text_input("کلیلی Groq بنووسە:", type="password")
    st.markdown("---")
    st.markdown("[کلیلی خۆرایی بەدەست بهێنە](https://console.groq.com)")
    
    if st.button("پاککردنەوەی گفتوگۆ"):
        st.session_state.messages = []
        st.rerun()

# ئەگەر کلیلی API نەنووسراوە
if not api_key:
    st.warning("👈 تکایە لە لای چەپ کلیلی Groq -ەکەت بنووسە بۆ دەستپێکردن")
    st.stop()

# دروستکردنی client
client = Groq(api_key=api_key)

# مێژووی گفتوگۆ
if "messages" not in st.session_state:
    st.session_state.messages = []

# نمایشی مێژوو
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# وەرگرتنی پرسیار
prompt = st.chat_input("پرسیارەکەت لێرە بنووسە...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant"):
        with st.spinner("بیردەکەمەوە..."):
            try:
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": "تۆ یاریدەدەرێکی زیرەکی، هەمیشە بە زمانی کوردی وەڵام بدەوە."},
                        *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                    ],
                    temperature=0.7,
                    max_tokens=1000
                )
                reply = response.choices[0].message.content
                st.write(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"هەڵەیەک ڕوویدا: {e}")
