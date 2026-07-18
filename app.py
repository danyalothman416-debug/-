import streamlit as st
import sys
import io
import tempfile
from datetime import datetime
from PIL import Image
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
st.set_page_config(page_title="یاریدەدەری AI", page_icon="🤖", layout="centered")

# CSS ی سادە و جوان
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
    
    .stButton button:hover {
        background: #4338ca !important;
        transform: scale(1.02) !important;
    }
    
    .stChatMessage {
        border-radius: 12px !important;
        padding: 15px !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-weight: bold !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: #4f46e5 !important;
        color: white !important;
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════
# سایدبار
# ═══════════════════════════════════════════
with st.sidebar:
    st.image("https://huggingface.co/front/assets/huggingface_logo-noborder.svg", width=50)
    st.title("ڕێکخستنەکان")
    
    # API Key
    hf_token = st.text_input("🔑 کلیلی Hugging Face:", type="password", 
                             help="لە huggingface.co/settings/tokens وەربگرە")
    st.markdown("[🔗 وەرگرتنی کلیلی خۆرایی](https://huggingface.co/settings/tokens)")
    
    st.divider()
    
    # مۆدێل
    model = st.selectbox("🤖 مۆدێل:", [
        "cognitivecomputations/dolphin-2.5-mixtral-8x7b",
        "NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO",
        "teknium/OpenHermes-2.5-Mistral-7B",
        "mistralai/Mixtral-8x7B-Instruct-v0.1"
    ])
    
    temp = st.slider("🌡️ ڕادەی داهێنان:", 0.0, 2.0, 0.7)
    max_len = st.slider("📏 درێژی وەڵام:", 50, 2000, 800)
    
    st.divider()
    
    if st.button("🗑️ پاککردنەوەی چات", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ═══════════════════════════════════════════
# سەرپەڕە
# ═══════════════════════════════════════════
st.title("🤖 یاریدەدەری زیرەکی دەستکرد")
st.caption("بە Hugging Face - خۆرایی و بێ سانسۆر")

# ═══════════════════════════════════════════
# چات
# ═══════════════════════════════════════════
if "messages" not in st.session_state:
    st.session_state.messages = []

if not hf_token:
    st.info("👈 تکایە کلیلی Hugging Face بنووسە بۆ دەستپێکردن")
    st.markdown("""
    **چۆن کلیلی خۆرایی وەربگریت:**
    1. بڕۆ بۆ [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
    2. هەژمار دروست بکە
    3. New token بکە و ناوی بنووسە
    4. کلیلەکە کۆپی بکە
    """)
else:
    try:
        client = InferenceClient(token=hf_token)
        
        # نمایشی چات
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
        
        # پرسیار
        prompt = st.chat_input("💬 پرسیارەکەت بنووسە...")
        
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("assistant"):
                with st.spinner("🤔 بیردەکەمەوە..."):
                    try:
                        response = client.chat_completion(
                            model=model,
                            messages=[{"role": m["role"], "content": m["content"]} 
                                     for m in st.session_state.messages],
                            max_tokens=max_len,
                            temperature=temp
                        )
                        reply = response.choices[0].message.content
                        st.write(reply)
                        
                        # دوگمەی خوێندنەوە
                        if st.button("🔊 بیخوێنەوە", key=f"tts_{len(st.session_state.messages)}"):
                            try:
                                tts = gTTS(text=reply[:500], lang='ar')
                                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                                    tts.save(fp.name)
                                    st.audio(fp.name)
                            except:
                                st.warning("نەتوانرا")
                        
                        st.session_state.messages.append({"role": "assistant", "content": reply})
                        
                    except Exception as e:
                        st.error(f"هەڵە: {e}")
                        
    except Exception as e:
        st.error(f"هەڵە لە پەیوەندی: {e}")

# ═══════════════════════════════════════════
# تایبەتمەندییەکانی تر
# ═══════════════════════════════════════════
st.divider()
st.subheader("🛠️ ئامرازەکان")

tool_tabs = st.tabs(["📄 PDF", "🌐 وەرگێڕان", "📊 چارت", "🎨 QR", "🎮 یاری"])

# PDF
with tool_tabs[0]:
    pdf_file = st.file_uploader("فایلی PDF باربکە:", type="pdf")
    if pdf_file:
        try:
            doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            st.text_area("ناوەڕۆک:", text, height=200)
        except Exception as e:
            st.error(f"هەڵە: {e}")

# وەرگێڕان
with tool_tabs[1]:
    col1, col2 = st.columns(2)
    with col1:
        text = st.text_area("دەق:", height=150)
    with col2:
        lang = st.selectbox("وەربگێڕە بۆ:", ["کوردی (عەرەبی)", "عەرەبی", "English", "فارسی", "تورکی"])
        if st.button("وەربگێڕە", use_container_width=True) and text:
            try:
                lang_map = {"کوردی (عەرەبی)": "ar", "عەرەبی": "ar", "English": "en", "فارسی": "fa", "تورکی": "tr"}
                translated = GoogleTranslator(source='auto', target=lang_map[lang]).translate(text)
                st.text_area("وەرگێڕدراو:", translated, height=150)
            except:
                st.error("هەڵە")

# چارت
with tool_tabs[2]:
    data = pd.DataFrame({'X': [1,2,3,4,5], 'Y': [10,20,15,25,30]})
    edited = st.data_editor(data, num_rows="dynamic")
    if st.button("📊 چارت دروست بکە"):
        fig = px.line(edited, x='X', y='Y')
        st.plotly_chart(fig, use_container_width=True)

# QR
with tool_tabs[3]:
    qr_text = st.text_input("دەق بۆ QR:", "سڵاو!")
    if qr_text:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = BytesIO()
        img.save(buf, format="PNG")
        st.image(buf, width=200)

# یاری
with tool_tabs[4]:
    game = st.selectbox("یاری:", ["🎲 زار", "🔢 ژمارە"])
    
    if game == "🎲 زار":
        if st.button("بڕژێنە"):
            st.markdown(f"<h1 style='text-align:center;'>{random.randint(1,6)}</h1>", unsafe_allow_html=True)
    
    elif game == "🔢 ژمارە":
        if "secret" not in st.session_state:
            st.session_state.secret = random.randint(1, 100)
            st.session_state.attempts = 0
        
        guess = st.number_input("ژمارە:", 1, 100)
        if st.button("تاقی بکەرەوە"):
            st.session_state.attempts += 1
            if guess == st.session_state.secret:
                st.balloons()
                st.success(f"🎉 دۆزیتەوە! {st.session_state.attempts} هەوڵ")
                st.session_state.secret = random.randint(1, 100)
                st.session_state.attempts = 0
            elif guess < st.session_state.secret:
                st.info("⬆️ گەورەترە")
            else:
                st.info("⬇️ بچووکترە")

# ═══════════════════════════════════════════
# پەڕاوێز
# ═══════════════════════════════════════════
st.divider()
st.caption(f"🤖 یاریدەدەری AI | بە Hugging Face | {datetime.now().strftime('%Y-%m-%d')}")
