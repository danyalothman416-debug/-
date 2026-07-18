import streamlit as st
import sys
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
# ڕێکخستنی سەرەتایی
# ═══════════════════════════════════════════
st.set_page_config(page_title="🤖 یاریدەدەری AI", page_icon="🤖", layout="wide")

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
        transition: all 0.2s !important;
    }
    
    .stButton button:hover {
        background: #4338ca !important;
        transform: scale(1.02) !important;
    }
    
    .stChatMessage {
        border-radius: 15px !important;
        padding: 15px !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: #4f46e5 !important;
        color: white !important;
        border-radius: 8px !important;
    }
    
    .sidebar .stTextInput input {
        border-radius: 10px !important;
    }
    
    .feature-box {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        border: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════
# سایدبار
# ═══════════════════════════════════════════
with st.sidebar:
    st.markdown("## ⚙️ ڕێکخستنەکان")
    
    # API Key
    hf_token = st.text_input("🔑 کلیلی Hugging Face:", type="password",
                             help="لە huggingface.co/settings/tokens وەربگرە")
    st.markdown("[🔗 وەرگرتنی کلیلی خۆرایی](https://huggingface.co/settings/tokens)")
    
    st.divider()
    
    # هەڵبژاردنی مۆدێل
    st.markdown("### 🤖 هەڵبژاردنی مۆدێل")
    
    model_choice = st.selectbox("مۆدێل:", [
        "🐬 Dolphin (بێ سانسۆر)",
        "🧠 Nous Hermes (بێ سانسۆر)",
        "📚 OpenHermes (بێ سانسۆر)",
        "🌐 Mixtral (گشتی)"
    ])
    
    model_map = {
        "🐬 Dolphin (بێ سانسۆر)": "cognitivecomputations/dolphin-2.5-mixtral-8x7b",
        "🧠 Nous Hermes (بێ سانسۆر)": "NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO",
        "📚 OpenHermes (بێ سانسۆر)": "teknium/OpenHermes-2.5-Mistral-7B",
        "🌐 Mixtral (گشتی)": "mistralai/Mixtral-8x7B-Instruct-v0.1"
    }
    
    model = model_map[model_choice]
    
    st.divider()
    
    # ڕێکخستنی وەڵام
    st.markdown("### 🎯 ڕێکخستنی وەڵام")
    temp = st.slider("🌡️ ڕادەی داهێنان:", 0.0, 2.0, 0.7)
    max_len = st.slider("📏 درێژی وەڵام:", 50, 2000, 800)
    
    # زمانی وەڵام
    lang = st.radio("🌐 زمان:", ["کوردی", "عەرەبی", "English"], horizontal=True)
    
    st.divider()
    
    # دوگمەی پاککردنەوە
    if st.button("🗑️ پاککردنەوەی چات", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    # هەناردە
    if "messages" in st.session_state and st.session_state.messages:
        chat_text = "\n\n".join([f"{'👤' if m['role']=='user' else '🤖'}: {m['content']}" 
                                for m in st.session_state.messages])
        st.download_button("📥 هەناردەی چات", chat_text, "chat.txt", use_container_width=True)
    
    st.divider()
    st.caption("🤖 بە Hugging Face - خۆرایی")

# ═══════════════════════════════════════════
# بەشی سەرەکی
# ═══════════════════════════════════════════

# دوو ستوون: چات + ئامرازەکان
col1, col2 = st.columns([2, 1])

# ═══════════════════════════════════════════
# ستوونی ١: چات
# ═══════════════════════════════════════════
with col1:
    st.markdown("## 💬 چات")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if not hf_token:
        st.warning("👈 تکایە کلیلی Hugging Face بنووسە بۆ دەستپێکردنی چات")
        st.markdown("""
        **ڕێنمایی وەرگرتنی کلیلی خۆرایی:**
        1. بڕۆ بۆ [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
        2. هەژمار دروست بکە (Sign Up)
        3. کلیک لەسەر **New token** بکە
        4. ناویەک بنووسە و **Generate** بکە
        5. کلیلەکە **کۆپی** بکە
        """)
    else:
        try:
            client = InferenceClient(token=hf_token)
            
            # System message
            if lang == "کوردی":
                sys_msg = "You are a helpful AI assistant. ALWAYS respond in Kurdish (Sorani, Arabic script)."
            elif lang == "عەرەبی":
                sys_msg = "You are a helpful AI assistant. ALWAYS respond in Arabic."
            else:
                sys_msg = "You are a helpful AI assistant. Respond in English."
            
            # نمایشی مێژووی چات
            chat_container = st.container(height=500)
            with chat_container:
                for msg in st.session_state.messages:
                    with st.chat_message(msg["role"]):
                        st.write(msg["content"])
            
            # پرسیار
            prompt = st.chat_input("💬 پرسیارەکەت بنووسە...")
            
            if prompt:
                st.session_state.messages.append({"role": "user", "content": prompt})
                
                # نیشاندانی پرسیار
                with chat_container:
                    with st.chat_message("user"):
                        st.write(prompt)
                
                # وەڵام
                with st.chat_message("assistant"):
                    with st.spinner("🤔 بیردەکەمەوە..."):
                        try:
                            response = client.chat_completion(
                                model=model,
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
                            
                            # دوگمەی خوێندنەوە
                            col_a, col_b = st.columns([1, 10])
                            with col_a:
                                if st.button("🔊", key=f"tts_{len(st.session_state.messages)}", help="بیخوێنەرەوە"):
                                    try:
                                        tts = gTTS(text=reply[:500], lang='ar' if lang != 'English' else 'en')
                                        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                                            tts.save(fp.name)
                                            st.audio(fp.name)
                                    except:
                                        st.warning("نەتوانرا")
                            
                            st.session_state.messages.append({"role": "assistant", "content": reply})
                            
                        except Exception as e:
                            st.error(f"❌ هەڵە: {e}")
                            
        except Exception as e:
            st.error(f"❌ هەڵە لە پەیوەندی: {e}")

# ═══════════════════════════════════════════
# ستوونی ٢: ئامرازەکان
# ═══════════════════════════════════════════
with col2:
    st.markdown("## 🛠️ ئامرازەکان")
    
    # PDF
    with st.expander("📄 شیکاری PDF", expanded=False):
        pdf_file = st.file_uploader("فایلی PDF:", type="pdf", key="pdf")
        if pdf_file:
            try:
                doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
                text = ""
                for page in doc:
                    text += page.get_text()
                doc.close()
                st.text_area("ناوەڕۆک:", text, height=150)
            except:
                st.error("هەڵە لە خوێندنەوە")
    
    # وەرگێڕان
    with st.expander("🌐 وەرگێڕان", expanded=False):
        trans_text = st.text_area("دەق:", height=100, key="trans")
        trans_lang = st.selectbox("بۆ:", ["عەرەبی", "English", "فارسی", "تورکی"], key="trans_lang")
        if st.button("وەربگێڕە", use_container_width=True, key="trans_btn") and trans_text:
            try:
                lang_map = {"عەرەبی": "ar", "English": "en", "فارسی": "fa", "تورکی": "tr"}
                result = GoogleTranslator(source='auto', target=lang_map[trans_lang]).translate(trans_text)
                st.success(result)
            except:
                st.error("هەڵە")
    
    # چارت
    with st.expander("📊 چارت", expanded=False):
        data = pd.DataFrame({
            'X': [1, 2, 3, 4, 5],
            'Y': [10, 20, 15, 25, 30]
        })
        edited = st.data_editor(data, num_rows="dynamic", key="chart_data")
        chart_type = st.selectbox("جۆر:", ["Line", "Bar"], key="chart_type")
        if st.button("دروست بکە", use_container_width=True, key="chart_btn"):
            if chart_type == "Line":
                fig = px.line(edited, x='X', y='Y')
            else:
                fig = px.bar(edited, x='X', y='Y')
            st.plotly_chart(fig, use_container_width=True)
    
    # QR Code
    with st.expander("🎨 QR Code", expanded=False):
        qr_text = st.text_input("دەق:", "سڵاو!", key="qr_text")
        if qr_text:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qr_text)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buf = BytesIO()
            img.save(buf, format="PNG")
            st.image(buf, width=200)
    
    # یاری
    with st.expander("🎮 یاری", expanded=False):
        game = st.selectbox("یاری:", ["🎲 زار", "🔢 ژمارە"], key="game")
        
        if game == "🎲 زار":
            if st.button("بڕژێنە", use_container_width=True, key="dice"):
                st.markdown(f"<h1 style='text-align:center;'>{random.randint(1,6)}</h1>", unsafe_allow_html=True)
        
        elif game == "🔢 ژمارە":
            if "secret" not in st.session_state:
                st.session_state.secret = random.randint(1, 100)
                st.session_state.attempts = 0
            
            guess = st.number_input("ژمارە (١-١٠٠):", 1, 100, key="guess")
            if st.button("تاقی بکەرەوە", use_container_width=True, key="guess_btn"):
                st.session_state.attempts += 1
                if guess == st.session_state.secret:
                    st.balloons()
                    st.success(f"🎉 دۆزیتەوە! ({st.session_state.attempts} هەوڵ)")
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
st.caption(f"🤖 یاریدەدەری AI | بە Hugging Face | خۆرایی و بێ سانسۆر | {datetime.now().strftime('%Y-%m-%d')}")
