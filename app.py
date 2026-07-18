import streamlit as st
from groq import Groq
import sys
import base64
import fitz  # PyMuPDF بۆ PDF
from PIL import Image
import io

# چارەسەری encoding
sys.stdout.reconfigure(encoding='utf-8')

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
st.write("پرسیار بکە، فایل باربکە، یان وێنە بنێرە!")

# ═══════════ سایدبار ═══════════
with st.sidebar:
    st.header("⚙️ ڕێکخستنەکان")
    
    # کلیلی API
    api_key = st.text_input("کلیلی Groq بنووسە:", type="password")
    st.markdown("[کلیلی خۆرایی بەدەست بهێنە](https://console.groq.com)")
    
    st.markdown("---")
    
    # هەڵبژاردنی مۆدێل
    st.subheader("مۆدێل")
    model = st.selectbox(
        "مۆدێل هەڵبژێرە:",
        ["llama-3.1-8b-instant", "mixtral-8x7b-32768", "gemma2-9b-it"],
        help="Llama: خێرا | Mixtral: زیرەک | Gemma: هاوسەنگ"
    )
    
    # زمانی وەڵام
    st.subheader("زمان")
    language = st.radio(
        "زمانی وەڵام:",
        ["کوردی", "عەرەبی", "ئینگلیزی"],
        horizontal=True
    )
    
    st.markdown("---")
    
    # ڕێکخستنی وەڵام
    st.subheader("ڕێکخستنی وەڵام")
    temperature = st.slider("ڕادەی داهێنان:", 0.0, 1.0, 0.7, 0.1)
    max_tokens = st.slider("درێژی وەڵام:", 50, 2000, 500, 50)
    top_p = st.slider("فراوانی بژاردەکان:", 0.0, 1.0, 0.9, 0.1)
    
    st.markdown("---")
    
    # ئامار
    if "messages" in st.session_state:
        msg_count = len(st.session_state.messages) // 2
        st.metric("ژمارەی گفتوگۆ", msg_count)
    
    st.markdown("---")
    
    # دوگمەکانی بەڕێوەبردن
    col1, col2 = st.columns(2)
    with col1:
        if st.button("پاککردنەوە", use_container_width=True):
            st.session_state.messages = []
            st.session_state.uploaded_file_content = None
            st.session_state.uploaded_image = None
            st.rerun()
    with col2:
        if st.button("سڕینەوە", use_container_width=True):
            if len(st.session_state.messages) >= 2:
                st.session_state.messages = st.session_state.messages[:-2]
                st.rerun()
    
    # هەناردەکردن
    if "messages" in st.session_state and st.session_state.messages:
        chat_text = "\n\n".join([
            f"{'به‌كارهێنه‌ر' if m['role']=='user' else 'یاریده‌ده‌ر'}: {m['content']}" 
            for m in st.session_state.messages
        ])
        st.download_button(
            "هەناردەی گفتوگۆ",
            chat_text,
            "گفتوگۆکەم.txt",
            "text/plain",
            use_container_width=True
        )

# ═══════════ بەشی سەرەکی ═══════════

# ئەگەر کلیلی API نەنووسراوە
if not api_key:
    st.warning("تکایە لە لای چەپ کلیلی Groq -ەکەت بنووسە بۆ دەستپێکردن")
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
    "کوردی": "You are a helpful assistant. IMPORTANT: Always respond in Kurdish (Sorani, using Arabic script). Never use Latin script for Kurdish.",
    "عەرەبی": "You are a helpful assistant. IMPORTANT: Always respond in Arabic language only.",
    "ئینگلیزی": "You are a helpful assistant. Always respond in English language only."
}

# مێژووی گفتوگۆ
if "messages" not in st.session_state:
    st.session_state.messages = []

if "uploaded_file_content" not in st.session_state:
    st.session_state.uploaded_file_content = None

if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None

# ═══════════ بارکردنی فایل (PDF و TXT) ═══════════
st.subheader("📄 بارکردنی فایل")
tab1, tab2 = st.tabs(["📝 فایلی PDF/TXT", "🖼️ وێنە"])

with tab1:
    uploaded_file = st.file_uploader(
        "فایلێک باربکە (PDF یان TXT):",
        type=["pdf", "txt"],
        key="file_uploader"
    )
    
    if uploaded_file:
        try:
            if uploaded_file.type == "application/pdf":
                # خوێندنەوەی PDF
                pdf_bytes = uploaded_file.read()
                doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                file_text = ""
                for page in doc:
                    file_text += page.get_text()
                doc.close()
                st.success("✅ فایلی PDF بە سەرکەوتوویی خوێندراەوە")
            else:
                # خوێندنەوەی TXT
                file_text = uploaded_file.read().decode("utf-8")
                st.success("✅ فایلی دەقی خوێندراەوە")
            
            st.session_state.uploaded_file_content = file_text
            
            with st.expander("📋 ناوەڕۆکی فایلەکە"):
                st.text_area("ناوەڕۆک:", file_text, height=200)
            
            if st.button("🔍 شیکاری ئەم فایلە بکە", type="primary"):
                prompt = f"Please analyze this document and provide a comprehensive summary in the appropriate language:\n\n{file_text}"
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.rerun()
                
        except Exception as e:
            st.error(f"هەڵە لە خوێندنەوەی فایل: {e}")

with tab2:
    uploaded_image = st.file_uploader(
        "وێنەیەک باربکە:",
        type=["png", "jpg", "jpeg"],
        key="image_uploader"
    )
    
    if uploaded_image:
        try:
            # نمایشی وێنە
            image = Image.open(uploaded_image)
            st.image(image, caption="وێنەکەت", use_column_width=True)
            
            # گۆڕینی وێنە بۆ base64
            buffered = io.BytesIO()
            image.save(buffered, format=image.format or "PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            st.session_state.uploaded_image = img_str
            
            # پرسیار لەسەر وێنە
            image_question = st.text_input("💬 پرسیارت لەسەر ئەم وێنەیە چییە؟",
                                          placeholder="بۆ نموونە: ئەم وێنەیە چی پیشان دەدات؟")
            
            if st.button("🔍 پرسیار لەسەر وێنە بکە", type="primary") and image_question:
                # دروستکردنی payload بۆ مۆدێلی بینایی
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": image_question},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{img_str}"
                                }
                            }
                        ]
                    }
                ]
                
                st.session_state.messages.append({
                    "role": "user",
                    "content": f"[وێنەیەک نێردرا] پرسیار: {image_question}"
                })
                st.rerun()
                
        except Exception as e:
            st.error(f"هەڵە لە پرۆسێسکردنی وێنە: {e}")

st.markdown("---")

# ═══════════ نمایشی مێژوو ═══════════
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ═══════════ وەرگرتنی پرسیار ═══════════
prompt = st.chat_input("💬 پرسیارەکەت لێرە بنووسە...")

if prompt:
    # زیادکردنی پرسیاری بەکارهێنەر
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # ئامادەکردنی messages
    api_messages = []
    
    # زیادکردنی system message
    api_messages.append({"role": "system", "content": system_messages[language]})
    
    # زیادکردنی مێژوو
    for m in st.session_state.messages:
        if m["role"] == "user" and m["content"].startswith("[وێنەیەک نێردرا]"):
            # ئەگەر وێنە بوو، ناتوانین بنێرین بۆ Groq (Groq بینایی نییە)
            api_messages.append({
                "role": "user",
                "content": m["content"] + "\n\nتکایە وەڵام بدەرەوە وەک ئەوەی وێنەکەت بینیبێت، یان ڕێنمایی بکە کە ناتوانیت وێنە ببینی."
            })
        else:
            api_messages.append({"role": m["role"], "content": m["content"]})
    
    # وەرگرتنی وەڵام
    with st.chat_message("assistant"):
        with st.spinner("🤔 بیردەکەمەوە..."):
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=api_messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=top_p
                )
                
                reply = response.choices[0].message.content
                st.write(reply)
                
                st.session_state.messages.append({"role": "assistant", "content": reply})
                
            except Exception as e:
                st.error(f"❌ هەڵەیەک ڕوویدا: {e}")

# پەراوێز
st.markdown("---")
st.caption(f"🚀 دروستکراوە بە Streamlit و Groq | مۆدێل: {model}")
