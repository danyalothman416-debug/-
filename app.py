import streamlit as st
from groq import Groq

# ڕێکخستنی پەڕە
st.set_page_config(
    page_title="یاریدەدەری AI",
    page_icon="🤖",
    layout="wide"
)

# CSS بۆ ڕووکاری جوان
st.markdown("""
<style>
    .stChatMessage { border-radius: 15px !important; }
    .stButton button { 
        background: linear-gradient(45deg, #4CAF50, #45a049) !important;
        color: white !important;
        font-weight: bold !important;
    }
    .stDownloadButton button {
        background: linear-gradient(45deg, #2196F3, #1976D2) !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🤖 یاریدەدەری زیرەکی دەستکرد")
st.write("پرسیار بکە و وەڵام وەربگرە - وەک یاریدەدەرێکی زیرەک!")

# ═══════════ سایدبار ═══════════
with st.sidebar:
    st.header("⚙️ ڕێکخستنەکان")
    
    # کلیلی API
    api_key = st.text_input("🔑 کلیلی Groq بنووسە:", type="password")
    st.markdown("[کلیلی خۆرایی بەدەست بهێنە](https://console.groq.com)")
    
    st.markdown("---")
    
    # هەڵبژاردنی مۆدێل
    st.subheader("🧠 مۆدێل")
    model = st.selectbox(
        "مۆدێل هەڵبژێرە:",
        ["llama-3.1-8b-instant", "mixtral-8x7b-32768", "gemma2-9b-it"],
        help="Llama: خێرا | Mixtral: زیرەک | Gemma: هاوسەنگ"
    )
    
    # زمانی وەڵام
    st.subheader("🌐 زمان")
    language = st.radio(
        "زمانی وەڵام:",
        ["کوردی", "عەرەبی", "ئینگلیزی"],
        horizontal=True
    )
    
    st.markdown("---")
    
    # ڕێکخستنی وەڵام
    st.subheader("🎯 ڕێکخستنی وەڵام")
    temperature = st.slider("🔧 ڕادەی داهێنان:", 0.0, 1.0, 0.7, 0.1)
    max_tokens = st.slider("📏 درێژی وەڵام:", 50, 2000, 500, 50)
    top_p = st.slider("🎲 فراوانی بژاردەکان:", 0.0, 1.0, 0.9, 0.1)
    
    st.markdown("---")
    
    # ئامار
    if "messages" in st.session_state:
        msg_count = len(st.session_state.messages) // 2
        st.metric("💬 ژمارەی گفتوگۆ", msg_count)
    
    st.markdown("---")
    
    # دوگمەکانی بەڕێوەبردن
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ پاککردنەوە", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    with col2:
        if st.button("↩️ سڕینەوە", use_container_width=True):
            if len(st.session_state.messages) >= 2:
                st.session_state.messages = st.session_state.messages[:-2]
                st.rerun()
    
    # هەناردەکردن
    if "messages" in st.session_state and st.session_state.messages:
        chat_text = "\n\n".join([
            f"{'👤 بەکارهێنەر' if m['role']=='user' else '🤖 یاریدەدەر'}: {m['content']}" 
            for m in st.session_state.messages
        ])
        st.download_button(
            "📥 هەناردەی گفتوگۆ",
            chat_text,
            "گفتوگۆکەم.txt",
            "text/plain",
            use_container_width=True
        )

# ═══════════ بەشی سەرەکی ═══════════

# ئەگەر کلیلی API نەنووسراوە
if not api_key:
    st.warning("👈 تکایە لە لای چەپ کلیلی Groq -ەکەت بنووسە بۆ دەستپێکردن")
    st.info("""
    **چۆن کلیلی خۆرایی بەدەست بهێنیت:**
    1. بڕۆ بۆ [console.groq.com](https://console.groq.com)
    2. هەژمارێک دروست بکە
    3. بڕۆ بەشی API Keys
    4. Create API Key بکە و کۆپی بکە
    """)
    st.stop()

# دروستکردنی client
try:
    client = Groq(api_key=api_key)
except Exception as e:
    st.error(f"کلیلەکە هەڵەیە: {e}")
    st.stop()

# system message بەپێی زمان
system_messages = {
    "کوردی": "تۆ یاریدەدەرێکی زیرەکی، هەمیشە بە زمانی کوردی وەڵام بدەوە.",
    "عەرەبی": "أنت مساعد ذكي، أجب دائماً باللغة العربية.",
    "ئینگلیزی": "You are a helpful assistant, always respond in English."
}

# مێژووی گفتوگۆ
if "messages" not in st.session_state:
    st.session_state.messages = []

# ═══════════ بارکردنی فایل ═══════════
uploaded_file = st.file_uploader("📄 فایلێکی دەقی باربکە (تەنها TXT):", type="txt")
if uploaded_file:
    file_text = uploaded_file.read().decode("utf-8")
    with st.expander("📋 ناوەڕۆکی فایلەکە"):
        st.text(file_text)
    if st.button("🔍 شیکاری ئەم دەقە بکە"):
        prompt = f"تکایە شیکاری ئەم دەقە بکە و کورتەیەکی لێ بڵێ: {file_text}"
        st.session_state.messages.append({"role": "user", "content": prompt})

# ═══════════ نمایشی مێژوو ═══════════
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ═══════════ وەرگرتنی پرسیار ═══════════
prompt = st.chat_input("💬 پرسیارەکەت لێرە بنووسە...")

if prompt:
    # زیادکردنی پرسیاری بەکارهێنەر
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # وەرگرتنی وەڵام
    with st.chat_message("assistant"):
        with st.spinner("🤔 بیردەکەمەوە..."):
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_messages[language]},
                        *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=top_p
                )
                
                reply = response.choices[0].message.content
                st.write(reply)
                
                # دوگمەی کۆپیکردن
                col1, col2, col3 = st.columns([1, 1, 4])
                with col1:
                    if st.button("📋", key=f"copy_{len(st.session_state.messages)}", help="کۆپی بکە"):
                        st.toast("✅ وەڵامەکە کۆپی کرا!")
                
                st.session_state.messages.append({"role": "assistant", "content": reply})
                
            except Exception as e:
                st.error(f"❌ هەڵەیەک ڕوویدا: {e}")

# پەراوێز
st.markdown("---")
st.caption("🚀 دروستکراوە بە Streamlit و Groq | مۆدێل: " + model)
