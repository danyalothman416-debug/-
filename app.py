import streamlit as st
import tempfile
from datetime import datetime
import pandas as pd
import plotly.express as px
from deep_translator import GoogleTranslator
from gtts import gTTS
import random
from io import BytesIO
from huggingface_hub import InferenceClient
import fitz
import qrcode

# ═══════════════════════════════════════════
# ڕێکخستن
# ═══════════════════════════════════════════
st.set_page_config(page_title="🤖 یاریدەدەری AI", page_icon="🤖", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Naskh+Arabic:wght@400;700&display=swap');
    * { font-family: 'Noto Naskh Arabic', sans-serif; }
    .stButton button {
        background: #4f46e5 !important;
        color: white !important;
        border-radius: 10px !important;
        border: none !important;
        padding: 10px 20px !important;
        font-weight: bold !important;
    }
    .stButton button:hover { background: #4338ca !important; }
    .stChatMessage { border-radius: 15px !important; padding: 15px !important; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════
# سایدبار
# ═══════════════════════════════════════════
with st.sidebar:
    st.image("https://huggingface.co/front/assets/huggingface_logo-noborder.svg", width=60)
    st.markdown("## ⚙️ ڕێکخستنەکان")
    
    hf_token = st.text_input("🔑 کلیلی Hugging Face:", type="password")
    st.markdown("[🔗 وەرگرتنی کلیلی خۆرایی](https://huggingface.co/settings/tokens)")
    
    st.divider()
    
    st.markdown("### 🤖 مۆدێل")
    st.info("**Mistral 7B** - خۆرایی و بێ کێشە")
    
    st.divider()
    
    temp = st.slider("🌡️ ڕادەی داهێنان:", 0.0, 2.0, 0.7)
    max_len = st.slider("📏 درێژی وەڵام:", 50, 2000, 800)
    lang = st.radio("🌐 زمان:", ["کوردی", "عەرەبی", "English"], horizontal=True)
    
    st.divider()
    
    if st.button("🗑️ پاککردنەوەی چات", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    if "messages" in st.session_state and st.session_state.messages:
        chat_text = "\n\n".join([f"{'👤' if m['role']=='user' else '🤖'}: {m['content']}" 
                                for m in st.session_state.messages])
        st.download_button("📥 هەناردە", chat_text, "chat.txt", use_container_width=True)

# ═══════════════════════════════════════════
# بەشی سەرەکی
# ═══════════════════════════════════════════
col1, col2 = st.columns([2, 1])

# ═══════════════════════════════════════════
# چات
# ═══════════════════════════════════════════
with col1:
    st.markdown("## 💬 چات - Mistral AI")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if not hf_token:
        st.warning("👈 تکایە کلیلی Hugging Face بنووسە")
        st.info("🔗 [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)")
    else:
        try:
            client = InferenceClient(token=hf_token)
            
            lang_prompts = {
                "کوردی": "ALWAYS respond in Kurdish (Sorani, Arabic script).",
                "عەرەبی": "ALWAYS respond in Arabic.",
                "English": "Respond in English."
            }
            sys_msg = f"You are a helpful assistant. {lang_prompts[lang]}"
            
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])
            
            prompt = st.chat_input("💬 پرسیارەکەت بنووسە...")
            
            if prompt:
                st.session_state.messages.append({"role": "user", "content": prompt})
                
                with st.chat_message("user"):
                    st.write(prompt)
                
                with st.chat_message("assistant"):
                    with st.spinner("🤔 بیردەکەمەوە..."):
                        try:
                            response = client.chat_completion(
                                model="mistralai/Mistral-7B-Instruct-v0.2",
                                messages=[
                                    {"role": "system", "content": sys_msg},
                                    *[{"role": m["role"], "content": m["content"]} 
                                      for m in st.session_state.messages]
                                ],
                                max_tokens=max_len,
                                temperature=temp
                            )
                            reply = response.choices[0].message.content
                            st.write(reply)
                            
                            if st.button("🔊 بیخوێنەرەوە", key=f"t{len(st.session_state.messages)}"):
                                try:
                                    tts = gTTS(text=reply[:500], lang='ar' if lang != 'English' else 'en')
                                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
                                        tts.save(f.name)
                                        st.audio(f.name)
                                except:
                                    pass
                            
                            st.session_state.messages.append({"role": "assistant", "content": reply})
                        except Exception as e:
                            st.error(f"❌ هەڵە: {e}")
        except Exception as e:
            st.error(f"❌ هەڵە لە پەیوەندی: {e}")

# ═══════════════════════════════════════════
# ئامرازەکان
# ═══════════════════════════════════════════
with col2:
    st.markdown("## 🛠️ ئامرازەکان")
    
    with st.expander("📄 PDF"):
        f = st.file_uploader("فایل:", type="pdf")
        if f:
            try:
                doc = fitz.open(stream=f.read(), filetype="pdf")
                t = ""
                for p in doc: t += p.get_text()
                doc.close()
                st.text_area("ناوەڕۆک:", t, height=150)
            except:
                st.error("هەڵە")
    
    with st.expander("🌐 وەرگێڕان"):
        txt = st.text_area("دەق:", height=100)
        lng = st.selectbox("بۆ:", ["عەرەبی", "English", "فارسی", "تورکی"])
        if st.button("وەربگێڕە", use_container_width=True) and txt:
            try:
                m = {"عەرەبی":"ar","English":"en","فارسی":"fa","تورکی":"tr"}
                r = GoogleTranslator(source='auto', target=m[lng]).translate(txt)
                st.success(r)
            except:
                st.error("هەڵە")
    
    with st.expander("📊 چارت"):
        d = pd.DataFrame({'X':[1,2,3,4,5], 'Y':[10,20,15,25,30]})
        d = st.data_editor(d, num_rows="dynamic")
        if st.button("دروست بکە", use_container_width=True):
            st.plotly_chart(px.line(d, x='X', y='Y'), use_container_width=True)
    
    with st.expander("🎨 QR"):
        q = st.text_input("دەق:", "سڵاو!")
        if q:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(q)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            b = BytesIO()
            img.save(b, format="PNG")
            st.image(b, width=200)
    
    with st.expander("🎮 یاری"):
        g = st.selectbox("", ["🎲 زار", "🔢 ژمارە"])
        if g == "🎲 زار":
            if st.button("بڕژێنە", use_container_width=True):
                st.markdown(f"<h1 style='text-align:center;'>{random.randint(1,6)}</h1>", unsafe_allow_html=True)
        else:
            if "s" not in st.session_state:
                st.session_state.s = random.randint(1,100)
                st.session_state.a = 0
            n = st.number_input("ژمارە:", 1, 100)
            if st.button("تاقی", use_container_width=True):
                st.session_state.a += 1
                if n == st.session_state.s:
                    st.balloons()
                    st.success(f"🎉 {st.session_state.a} هەوڵ")
                    st.session_state.s = random.randint(1,100)
                    st.session_state.a = 0
                elif n < st.session_state.s:
                    st.info("⬆️ گەورەترە")
                else:
                    st.info("⬇️ بچووکترە")

st.divider()
st.caption(f"🤖 Mistral 7B | Hugging Face | خۆرایی | {datetime.now().strftime('%Y-%m-%d')}")
