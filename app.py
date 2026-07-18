# ═══════════════════════════════════════════
# 🚀 سوپەر ئەپی AI - هەموو شتێک لە یەک شوێن
# ═══════════════════════════════════════════
import streamlit as st
import sys
import base64
import io
import os
import tempfile
from datetime import datetime
from PIL import Image
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from deep_translator import GoogleTranslator
from gtts import gTTS
import hashlib
import random
import json
import requests
from io import BytesIO

# Check for optional imports
try:
    import fitz  # PyMuPDF
    PDF_SUPPORT = True
except:
    PDF_SUPPORT = False

try:
    from groq import Groq
    GROQ_SUPPORT = True
except:
    GROQ_SUPPORT = False

try:
    import yfinance as yf
    FINANCE_SUPPORT = True
except:
    FINANCE_SUPPORT = False

try:
    import folium
    from streamlit_folium import folium_static
    MAP_SUPPORT = True
except:
    MAP_SUPPORT = False

try:
    from duckduckgo_search import DDGS
    SEARCH_SUPPORT = True
except:
    SEARCH_SUPPORT = False

try:
    import pytesseract
    OCR_SUPPORT = True
except:
    OCR_SUPPORT = False

try:
    import qrcode
    QR_SUPPORT = True
except:
    QR_SUPPORT = False

# ═══════════════════════════════════════════
# پەڕەی سەرەکی
# ═══════════════════════════════════════════
sys.stdout.reconfigure(encoding='utf-8')

st.set_page_config(
    page_title="🚀 سوپەر ئەپی AI",
    page_icon="🧞‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════
# CSS - ڕووکاری سەرسوڕهێنەر
# ═══════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Kufi+Arabic:wght@400;700&display=swap');
    
    * {
        font-family: 'Noto Kufi Arabic', sans-serif !important;
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        animation: gradient 5s ease infinite;
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .feature-card {
        background: linear-gradient(135deg, #2d2d44 0%, #1e1e2f 100%);
        padding: 25px;
        border-radius: 20px;
        color: white;
        margin: 15px 0;
        border: 1px solid rgba(255,255,255,0.1);
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4);
        border-color: #667eea;
    }
    
    .stButton button {
        background: linear-gradient(45deg, #667eea, #764ba2) !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 15px !important;
        border: none !important;
        padding: 12px 25px !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.5) !important;
    }
    
    .stChatMessage {
        border-radius: 20px !important;
        padding: 15px !important;
    }
    
    .stChatMessage[data-testid="user-message"] {
        background: linear-gradient(135deg, #667eea20, #764ba220) !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px !important;
        background: #1e1e2f !important;
        border-radius: 15px !important;
        padding: 8px !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px !important;
        padding: 12px 20px !important;
        color: white !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(45deg, #667eea, #764ba2) !important;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4) !important;
    }
    
    .magic-text {
        background: linear-gradient(45deg, #ff6b6b, #ffd93d, #6bcb77, #4d96ff, #ff6b6b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-size: 400% 400%;
        animation: rainbow 5s ease infinite;
        font-size: 3em;
        font-weight: bold;
        text-align: center;
    }
    
    @keyframes rainbow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .pulse {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .glass {
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 20px !important;
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════
# Session State
# ═══════════════════════════════════════════
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_data" not in st.session_state:
    st.session_state.user_data = {}
if "favorites" not in st.session_state:
    st.session_state.favorites = []
if "theme" not in st.session_state:
    st.session_state.theme = "dark"
if "username" not in st.session_state:
    st.session_state.username = "بەکارهێنەر"

# ═══════════════════════════════════════════
# سایدبار - ناوەندی کۆنتڕۆڵ
# ═══════════════════════════════════════════
with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>🧞‍♂️ سوپەر ئەپ</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    # پرۆفایلی بەکارهێنەر
    with st.expander("👤 پڕۆفایل", expanded=True):
        st.session_state.username = st.text_input("ناوی بەکارهێنەر:", value=st.session_state.username)
        st.write(f"🌟 بەخێربێیت، {st.session_state.username}!")
    
    # API Keys
    with st.expander("🔑 کلیلی API", expanded=True):
        groq_api = st.text_input("Groq API:", type="password", key="groq_key")
        st.markdown("[کلیلی خۆرایی Groq](https://console.groq.com)")
        
        openai_api = st.text_input("OpenAI API (ئارەزوومەندانە):", type="password", key="openai_key")
    
    st.markdown("---")
    
    # ڕێکخستنی AI
    with st.expander("🤖 ڕێکخستنی AI"):
        ai_model = st.selectbox("مۆدێل:", [
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768", 
            "gemma2-9b-it"
        ])
        
        ai_temp = st.slider("🎲 ڕادەی داهێنان:", 0.0, 1.0, 0.7)
        ai_tokens = st.slider("📏 درێژی:", 50, 2000, 500)
        ai_lang = st.selectbox("🌐 زمان:", ["کوردی", "عەرەبی", "English"])
    
    st.markdown("---")
    
    # ئامار
    col1, col2 = st.columns(2)
    with col1:
        st.metric("💬", len(st.session_state.messages)//2)
    with col2:
        st.metric("⭐", len(st.session_state.favorites))
    
    st.markdown("---")
    
    # دوگمەی خێرا
    if st.button("🗑️ پاککردنەوەی هەموو", use_container_width=True):
        st.session_state.messages = []
        st.session_state.favorites = []
        st.rerun()
    
    if st.button("📥 هەناردەی داتا", use_container_width=True):
        export_data = {
            "messages": st.session_state.messages,
            "favorites": st.session_state.favorites,
            "username": st.session_state.username,
            "timestamp": str(datetime.now())
        }
        st.download_button(
            "📥 دابەزاندن",
            json.dumps(export_data, ensure_ascii=False, indent=2),
            "super_app_data.json",
            use_container_width=True
        )

# ═══════════════════════════════════════════
# سەرپەڕەی سەرەکی
# ═══════════════════════════════════════════
st.markdown("""
<div class="main-header pulse">
    <h1>🧞‍♂️ سوپەر ئەپی AI</h1>
    <p style="font-size: 1.3em;">هەموو شتێک لە یەک شوێن - جادوو بکە!</p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════
# TAB -ەکان
# ═══════════════════════════════════════════
tabs = st.tabs([
    "💬 چات", "📄 فایل", "🌐 وەرگێڕ", "📊 چارت", 
    "🔍 گەڕان", "📝 کورتە", "💰 کریپتۆ", "🗺️ نەخشە",
    "🎮 یاری", "🎨 QR", "🧮 هەژمار", "⏰ کاتژمێر"
])

# ═══════════════════════════════════════════
# TAB 1: چاتی زیرەک
# ═══════════════════════════════════════════
with tabs[0]:
    col1, col2 = st.columns([3, 1])
    
    with col2:
        st.markdown("<div class='feature-card'>", unsafe_allow_html=True)
        st.subheader("🎭 کەسایەتی")
        personality = st.selectbox("", [
            "یاریدەدەر", "مامۆستا", "دۆست", "پرۆگرامەر",
            "شاعیر", "ڕەخنەگر", "کتێبخوێن", "چێشتلێنەر"
        ])
        
        st.markdown("---")
        st.subheader("🎯 کردارەکان")
        if st.button("🔊 وەڵام بخوێنەرەوە", use_container_width=True):
            st.info("لە وەڵامەکاندا دوگمەی 🔊 هەیە")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col1:
        if not groq_api:
            st.warning("👈 کلیلی Groq بنووسە")
        else:
            client = Groq(api_key=groq_api)
            
            # System message
            personalities = {
                "یاریدەدەر": "You are a helpful assistant.",
                "مامۆستا": "You are an expert teacher. Explain clearly.",
                "دۆست": "You are a friendly, supportive friend.",
                "پرۆگرامەر": "You are a professional programmer. Show code.",
                "شاعیر": "You are a creative poet. Be artistic.",
                "ڕەخنەگر": "You are a critical analyst. Be detailed.",
                "کتێبخوێن": "You are a book expert. Recommend books.",
                "چێشتلێنەر": "You are a master chef. Share recipes."
            }
            
            sys_msg = personalities[personality]
            if ai_lang == "کوردی":
                sys_msg += " Answer in Kurdish (Sorani, Arabic script)."
            elif ai_lang == "عەرەبی":
                sys_msg += " Answer in Arabic."
            
            # نمایشی چات
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])
                    if msg["role"] == "assistant":
                        if st.button("⭐", key=f"fav_{hash(msg['content'])}"):
                            st.session_state.favorites.append(msg["content"])
                            st.toast("⭐ زیاد کرا بۆ دڵخوازەکان!")
            
            # پرسیار
            prompt = st.chat_input("💭 پرسیارەکەت...")
            
            if prompt:
                st.session_state.messages.append({"role": "user", "content": prompt})
                
                with st.chat_message("assistant"):
                    with st.spinner("🤔"):
                        try:
                            response = client.chat.completions.create(
                                model=ai_model,
                                messages=[
                                    {"role": "system", "content": sys_msg},
                                    *[{"role": m["role"], "content": m["content"]} 
                                      for m in st.session_state.messages]
                                ],
                                temperature=ai_temp,
                                max_tokens=ai_tokens
                            )
                            reply = response.choices[0].message.content
                            st.write(reply)
                            
                            # TTS
                            if st.button("🔊 بیخوێنەوە", key=f"tts_{len(st.session_state.messages)}"):
                                try:
                                    lang_code = 'ar' if ai_lang in ['کوردی', 'عەرەبی'] else 'en'
                                    tts = gTTS(text=reply, lang=lang_code)
                                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                                        tts.save(fp.name)
                                        st.audio(fp.name)
                                except:
                                    st.warning("نەتوانرا")
                            
                            st.session_state.messages.append({"role": "assistant", "content": reply})
                            
                        except Exception as e:
                            st.error(f"هەڵە: {e}")

# ═══════════════════════════════════════════
# TAB 2: شیکاری فایل
# ═══════════════════════════════════════════
with tabs[1]:
    st.header("📄 شیکاری فایل و وێنە")
    
    ft1, ft2, ft3 = st.tabs(["📝 PDF/TXT", "🖼️ وێنە", "🔍 OCR"])
    
    with ft1:
        file = st.file_uploader("فایل:", type=["pdf", "txt"])
        if file and PDF_SUPPORT:
            try:
                if file.type == "application/pdf":
                    doc = fitz.open(stream=file.read(), filetype="pdf")
                    text = ""
                    for page in doc:
                        text += page.get_text()
                    doc.close()
                else:
                    text = file.read().decode("utf-8")
                
                st.text_area("ناوەڕۆک:", text, height=200)
                
                if st.button("🤖 بشیکەرەوە", type="primary"):
                    if groq_api:
                        client = Groq(api_key=groq_api)
                        response = client.chat.completions.create(
                            model=ai_model,
                            messages=[{"role": "user", "content": f"Summarize this:\n{text}"}],
                            max_tokens=300
                        )
                        st.write(response.choices[0].message.content)
            except Exception as e:
                st.error(f"هەڵە: {e}")
    
    with ft2:
        img_file = st.file_uploader("وێنە:", type=["png", "jpg", "jpeg"], key="img2")
        if img_file:
            img = Image.open(img_file)
            st.image(img, use_column_width=True)
            
            # QR Scanner
            if QR_SUPPORT:
                import qrcode as qr
                try:
                    from qrcode import QRCode
                    # Simple - just detect if QR
                    st.info("بۆ سکانکردنی QR، کامێرا پێویستە")
                except:
                    pass
    
    with ft3:
        if OCR_SUPPORT:
            ocr_img = st.file_uploader("وێنە بۆ OCR:", type=["png", "jpg"], key="ocr")
            if ocr_img:
                img = Image.open(ocr_img)
                st.image(img, width=300)
                if st.button("🔍 دەق بدۆزەرەوە"):
                    text = pytesseract.image_to_string(img, lang='ara+eng')
                    st.text_area("دەق:", text, height=150)
        else:
            st.info("OCR پێویستی بە Tesseract هەیە")

# ═══════════════════════════════════════════
# TAB 3: وەرگێڕان
# ═══════════════════════════════════════════
with tabs[2]:
    st.header("🌐 وەرگێڕانی دەق")
    
    col1, col2 = st.columns(2)
    with col1:
        src_lang = st.selectbox("لە:", ["auto", "ku", "ar", "en", "fa", "tr"])
        text = st.text_area("دەق:", height=200)
    
    with col2:
        tgt_lang = st.selectbox("بۆ:", ["ku", "ar", "en", "fa", "tr"])
        if st.button("🔄 وەربگێڕە", type="primary", use_container_width=True) and text:
            try:
                translated = GoogleTranslator(
                    source=src_lang if src_lang != "auto" else 'auto',
                    target=tgt_lang
                ).translate(text)
                st.text_area("وەرگێڕدراو:", translated, height=200)
                
                if st.button("🔊 بیخوێنەوە"):
                    tts = gTTS(text=translated, lang=tgt_lang if tgt_lang != 'ku' else 'ar')
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                        tts.save(fp.name)
                        st.audio(fp.name)
            except Exception as e:
                st.error(f"هەڵە: {e}")

# ═══════════════════════════════════════════
# TAB 4: چارت و داتا
# ═══════════════════════════════════════════
with tabs[3]:
    st.header("📊 شیکاری داتا")
    
    data = pd.DataFrame({
        'مانگ': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'فرۆش': [120, 180, 150, 200, 170, 220],
        'قازانج': [30, 50, 40, 60, 45, 70]
    })
    
    edited = st.data_editor(data, num_rows="dynamic")
    
    col1, col2 = st.columns(2)
    with col1:
        chart_type = st.selectbox("جۆری چارت:", ["Line", "Bar", "Area", "Scatter"])
    with col2:
        if st.button("📊 دروست بکە", type="primary", use_container_width=True):
            if chart_type == "Line":
                fig = px.line(edited, x='مانگ', y=['فرۆش', 'قازانج'])
            elif chart_type == "Bar":
                fig = px.bar(edited, x='مانگ', y='فرۆش')
            elif chart_type == "Area":
                fig = px.area(edited, x='مانگ', y='فرۆش')
            else:
                fig = px.scatter(edited, x='فرۆش', y='قازانج')
            
            st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════
# TAB 5: گەڕان
# ═══════════════════════════════════════════
with tabs[4]:
    st.header("🔍 گەڕانی ئینتەرنێت")
    
    query = st.text_input("بگەڕێ:")
    if query and st.button("🔍 بگەڕێ", type="primary"):
        if SEARCH_SUPPORT:
            try:
                with DDGS() as ddgs:
                    results = list(ddgs.text(query, max_results=5))
                    for i, r in enumerate(results, 1):
                        st.markdown(f"### {i}. [{r['title']}]({r['href']})")
                        st.write(r['body'])
                        st.markdown("---")
            except:
                st.error("گەڕان شکستی هێنا")
        else:
            st.info("گەڕان پێویستی بە duckduckgo-search هەیە")

# ═══════════════════════════════════════════
# TAB 6: کورتکردنەوە
# ═══════════════════════════════════════════
with tabs[5]:
    st.header("📝 کورتکردنەوە")
    
    long_text = st.text_area("دەق بنووسە:", height=200)
    
    if st.button("📝 کورت بکەوە", type="primary") and long_text and groq_api:
        client = Groq(api_key=groq_api)
        response = client.chat.completions.create(
            model=ai_model,
            messages=[{"role": "user", "content": f"Summarize in 3-5 sentences:\n{long_text}"}],
            max_tokens=200
        )
        st.write(response.choices[0].message.content)

# ═══════════════════════════════════════════
# TAB 7: کریپتۆ و دارایی
# ═══════════════════════════════════════════
with tabs[6]:
    st.header("💰 نرخی کریپتۆ و بۆرسە")
    
    if FINANCE_SUPPORT:
        symbol = st.text_input("سیمبۆڵ (وەک BTC-USD, AAPL):", "BTC-USD")
        if symbol and st.button("📈 نرخ ببینە"):
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1mo")
                
                fig = go.Figure(data=[
                    go.Candlestick(
                        x=hist.index,
                        open=hist['Open'],
                        high=hist['High'],
                        low=hist['Low'],
                        close=hist['Close']
                    )
                ])
                fig.update_layout(title=f"نرخی {symbol}")
                st.plotly_chart(fig, use_container_width=True)
                
                # Current price
                current = hist['Close'].iloc[-1]
                st.metric("نرخی ئێستا", f"${current:.2f}")
            except:
                st.error("سیمبۆڵ نەدۆزرایەوە")
    else:
        st.info("yfinance پێویستە")

# ═══════════════════════════════════════════
# TAB 8: نەخشە
# ═══════════════════════════════════════════
with tabs[7]:
    st.header("🗺️ نەخشە")
    
    if MAP_SUPPORT:
        lat = st.number_input("Latitude:", value=35.5)
        lon = st.number_input("Longitude:", value=44.5)
        
        m = folium.Map(location=[lat, lon], zoom_start=6)
        folium.Marker([lat, lon], popup="📍 شوێن").add_to(m)
        
        folium_static(m, width=800, height=400)
    else:
        st.info("folium پێویستە")

# ═══════════════════════════════════════════
# TAB 9: یاری
# ═══════════════════════════════════════════
with tabs[8]:
    st.header("🎮 یاری")
    
    game = st.selectbox("یاری هەڵبژێرە:", [
        "🎲 زار", "🔢 ژمارە بدۆزەرەوە", "📝 وشە دروستکە"
    ])
    
    if game == "🎲 زار":
        if st.button("🎲 بڕژێنە"):
            dice = random.randint(1, 6)
            st.markdown(f"<h1 style='text-align: center; font-size: 5em;'>{dice}</h1>", unsafe_allow_html=True)
    
    elif game == "🔢 ژمارە بدۆزەرەوە":
        if "secret" not in st.session_state:
            st.session_state.secret = random.randint(1, 100)
            st.session_state.attempts = 0
        
        guess = st.number_input("ژمارەکە:", 1, 100)
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
    
    elif game == "📝 وشە دروستکە":
        words = ["پاراستن", "سەربەخۆیی", "کۆمپیوتەر", "زیرەکی", "جوانی"]
        if "word" not in st.session_state:
            st.session_state.word = random.choice(words)
            st.session_state.guessed = set()
            st.session_state.wrong = 0
        
        word = st.session_state.word
        display = " ".join([c if c in st.session_state.guessed else "_" for c in word])
        
        st.markdown(f"<h2 style='text-align: center;'>{display}</h2>", unsafe_allow_html=True)
        st.write(f"هەڵەکان: {st.session_state.wrong}/6")
        
        letter = st.text_input("پیتێک:", max_chars=1)
        if st.button("تاقی بکەرەوە") and letter:
            if letter in word:
                st.session_state.guessed.add(letter)
            else:
                st.session_state.wrong += 1
            
            if all(c in st.session_state.guessed for c in word):
                st.balloons()
                st.success("🎉 سەرکەوتیت!")
                st.session_state.word = random.choice(words)
                st.session_state.guessed = set()
                st.session_state.wrong = 0
            elif st.session_state.wrong >= 6:
                st.error(f"💀 شکست! وشەکە: {word}")
                st.session_state.word = random.choice(words)
                st.session_state.guessed = set()
                st.session_state.wrong = 0

# ═══════════════════════════════════════════
# TAB 10: QR Code
# ═══════════════════════════════════════════
with tabs[9]:
    st.header("🎨 دروستکردنی QR Code")
    
    if QR_SUPPORT:
        qr_text = st.text_input("دەق بۆ QR:", "سڵاو! ئەمە QR ی منە")
        if qr_text:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qr_text)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            
            buf = BytesIO()
            img.save(buf, format="PNG")
            st.image(buf, caption="QR Code", width=300)
    else:
        st.info("qrcode پێویستە")

# ═══════════════════════════════════════════
# TAB 11: هەژماری زیرەک
# ═══════════════════════════════════════════
with tabs[10]:
    st.header("🧮 هەژماری زیرەک")
    
    col1, col2, col3, col4 = st.columns(4)
    
    if "calc" not in st.session_state:
        st.session_state.calc = ""
    
    with col1:
        if st.button("7", use_container_width=True): st.session_state.calc += "7"
        if st.button("4", use_container_width=True): st.session_state.calc += "4"
        if st.button("1", use_container_width=True): st.session_state.calc += "1"
        if st.button("0", use_container_width=True): st.session_state.calc += "0"
    
    with col2:
        if st.button("8", use_container_width=True): st.session_state.calc += "8"
        if st.button("5", use_container_width=True): st.session_state.calc += "5"
        if st.button("2", use_container_width=True): st.session_state.calc += "2"
        if st.button(".", use_container_width=True): st.session_state.calc += "."
    
    with col3:
        if st.button("9", use_container_width=True): st.session_state.calc += "9"
        if st.button("6", use_container_width=True): st.session_state.calc += "6"
        if st.button("3", use_container_width=True): st.session_state.calc += "3"
        if st.button("+", use_container_width=True): st.session_state.calc += "+"
    
    with col4:
        if st.button("÷", use_container_width=True): st.session_state.calc += "/"
        if st.button("×", use_container_width=True): st.session_state.calc += "*"
        if st.button("-", use_container_width=True): st.session_state.calc += "-"
        if st.button("=", use_container_width=True):
            try:
                st.session_state.calc = str(eval(st.session_state.calc))
            except:
                st.session_state.calc = ""
    
    st.text_input("", value=st.session_state.calc, key="calc_display")
    
    if st.button("🗑️ پاک بکەرەوە", use_container_width=True):
        st.session_state.calc = ""

# ═══════════════════════════════════════════
# TAB 12: کاتژمێر و بیرهێنانەوە
# ═══════════════════════════════════════════
with tabs[11]:
    st.header("⏰ کاتژمێر و بیرهێنانەوە")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🕐 کاتی ئێستا")
        now = datetime.now()
        st.markdown(f"<h2 style='text-align: center;'>{now.strftime('%H:%M:%S')}</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center;'>{now.strftime('%Y-%m-%d')}</p>", unsafe_allow_html=True)
        
        # Kurdish date
        kurdish_months = {
            1: "ڕێبەندان", 2: "ڕەشەمێ", 3: "نەورۆز",
            4: "گوڵان", 5: "جۆزەردان", 6: "پوشپەڕ",
            7: "گەلاوێژ", 8: "خەرمانان", 9: "ڕەزبەر",
            10: "گەڵاڕێزان", 11: "سەرماوەز", 12: "بەفرانبار"
        }
        kurdish_month = kurdish_months.get(now.month, "")
        st.write(f"📅 ڕێکەوتی کوردی: {now.day}ی {kurdish_month}ی {now.year}")
    
    with col2:
        st.subheader("⏰ بیرهێنانەوە")
        reminder_time = st.time_input("کات:")
        reminder_text = st.text_input("بیرهێنانەوە:")
        if st.button("⏰ تۆمار بکە", type="primary"):
            st.success(f"✅ بیرهێنانەوە تۆمارکرا بۆ {reminder_time}")
            st.balloons()

# ═══════════════════════════════════════════
# پەڕاوێز
# ═══════════════════════════════════════════
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #888;'>
    <p>🚀 سوپەر ئەپی AI v3.0 | دروستکراوە بە ❤️ | {now.strftime('%Y-%m-%d %H:%M')}</p>
    <p>🐙 <a href='https://github.com'>GitHub</a> | ⭐ فۆڕک بکە</p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════
# دوگمەی جادوویی
# ═══════════════════════════════════════════
with st.sidebar:
    st.markdown("---")
    if st.button("✨ جادوو بکە!", use_container_width=True, type="primary"):
        st.balloons()
        st.toast("🧞‍♂️ سوپەر ئەپ ئامادەیە!")
