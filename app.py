import streamlit as st
import requests
import tempfile
from datetime import datetime
import pandas as pd
import plotly.express as px
from deep_translator import GoogleTranslator
from gtts import gTTS
import random
from io import BytesIO
import fitz
import qrcode
import json

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
    model = st.selectbox("", [
        "google/flan-t5-large",
        "facebook/blenderbot-400M-distill",
        "microsoft/DialoGPT-medium"
    ])
    
    st.divider()
    
    temp = st.slider("🌡️ ڕادەی داهێنان:", 0.0, 2.0, 0.7)
    max_len = st.slider("📏 درێژی وەڵام:", 50, 500, 200)
    lang = st.radio("🌐 زمان:", ["کوردی", "عەرەبی", "English"], horizontal=True)
    
    st.divider()
    
    if st.button("🗑️ پاککردنەوەی چات", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ═══════════════════════════════════════════
# بەشی سەرەکی
# ═══════════════════════════════════════════
col1, col2 = st.columns([2, 1])

# ═══════════════════════════════════════════
# چات
# ═══════════════════════════════════════════
with col1:
    st.markdown("## 💬 چات - Hugging Face")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if not hf_token:
        st.warning("👈 تکایە کلیلی Hugging Face بنووسە")
        st.info("🔗 [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)")
    else:
        # نیشاندانی مێژوو
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
        
        # پرسیار
        prompt = st.chat_input("💬 پرسیارەکەت بنووسە...")
        
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.write(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("🤔 بیردەکەمەوە..."):
                    try:
                        # API URL
                        API_URL = f"https://api-inference.huggingface.co/models/{model}"
                        headers = {"Authorization": f"Bearer {hf_token}"}
                        
                        # ئامادەکردنی پرسیار
                        if lang == "کوردی":
                            full_prompt = f"Answer in Kurdish (Sorani, Arabic script): {prompt}"
                        elif lang == "عەرەبی":
                            full_prompt = f"Answer in Arabic: {prompt}"
                        else:
                            full_prompt = prompt
                        
                        payload = {
                            "inputs": full_prompt,
                            "parameters": {
                                "max_new_tokens": max_len,
                                "temperature": temp,
                                "return_full_text": False
                            }
                        }
                        
                        response = requests.post(API_URL, headers=headers, json=payload)
                        
                        if response.status_code == 200:
                            result = response.json()
                            if isinstance(result, list) and len(result) > 0:
                                reply = result[0].get("generated_text", "نەتوانرا وەڵام بدرێتەوە")
                            else:
                                reply = str(result)
                        else:
                            reply = f"هەڵە: {response.status_code}"
                        
                        st.write(reply)
                        
                        # دوگمەی خوێندنەوە
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
st.caption(f"🤖 Hugging Face API | خۆرایی | {datetime.now().strftime('%Y-%m-%d')}")
