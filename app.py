import streamlit as st
from groq import Groq
import sys
import base64
import fitz
from PIL import Image
import io
import pandas as pd
import plotly.express as px
from deep_translator import GoogleTranslator
from gtts import gTTS
import tempfile
import os
from datetime import datetime
import sqlite3
import hashlib

# ═══════════════════════════════════════
# ڕێکخستنی سەرەتایی
# ═══════════════════════════════════════
sys.stdout.reconfigure(encoding='utf-8')

st.set_page_config(
    page_title="سوپەر ئەپی AI",
    page_icon="🚀",
    layout="wide"
)

# CSS
st.markdown("""
<style>
    .stChatMessage { border-radius: 15px !important; }
    .stButton button { 
        background: linear-gradient(45deg, #4CAF50, #45a049) !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 10px !important;
    }
    .stDownloadButton button {
        background: linear-gradient(45deg, #2196F3, #1976D2) !important;
        color: white !important;
    }
    .feature-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        margin: 10px 0;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #1e1e2f 0%, #2d2d44 100%);
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════
# داتابەیس بۆ هەڵگرتنی مێژوو
# ═══════════════════════════════════════
def init_db():
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS chats
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  session_id TEXT,
                  role TEXT,
                  content TEXT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    return conn

def save_message(conn, session_id, role, content):
    c = conn.cursor()
    c.execute("INSERT INTO chats (session_id, role, content) VALUES (?, ?, ?)",
              (session_id, role, content))
    conn.commit()

def load_history(conn, session_id):
    c = conn.cursor()
    c.execute("SELECT role, content FROM chats WHERE session_id=? ORDER BY timestamp", (session_id,))
    return [{"role": row[0], "content": row[1]} for row in c.fetchall()]

# ═══════════════════════════════════════
# سایدبار
# ═══════════════════════════════════════
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=80)
    st.title("🚀 سوپەر ئەپ")
    
    # کلیلی API
    with st.expander("🔑 کلیلی API", expanded=True):
        api_key = st.text_input("کلیلی Groq:", type="password")
        st.markdown("[کلیلی خۆرایی بەدەست بهێنە](https://console.groq.com)")
    
    st.markdown("---")
    
    # هەڵبژاردنی مۆدێل
    with st.expander("🧠 ڕێکخستنی AI", expanded=True):
        model = st.selectbox("مۆدێل:", ["llama-3.1-8b-instant", "mixtral-8x7b-32768", "gemma2-9b-it"])
        language = st.radio("زمان:", ["کوردی", "عەرەبی", "ئینگلیزی"], horizontal=True)
        
        st.markdown("---")
        temperature = st.slider("🎲 ڕادەی داهێنان:", 0.0, 1.0, 0.7)
        max_tokens = st.slider("📏 درێژی وەڵام:", 50, 2000, 500)
    
    st.markdown("---")
    
    # کەسایەتی
    with st.expander("🎭 کەسایەتی AI"):
        personality = st.selectbox("شێوازی وەڵام:", [
            "یاریدەدەری ئاسایی",
            "مامۆستای شارەزا",
            "دۆستی میهرەبان",
            "پرۆگرامەری پیشەگەر",
            "شاعیری خەیاڵی",
            "ڕەخنەگری وردبین"
        ])
    
    st.markdown("---")
    
    # ئامار
    if "messages" in st.session_state:
        msg_count = len(st.session_state.messages) // 2
        col1, col2 = st.columns(2)
        with col1:
            st.metric("💬 گفتوگۆ", msg_count)
        with col2:
            st.metric("🟢", "ئۆنلاین")
    
    st.markdown("---")
    
    # دوگمەکان
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🗑️", help="پاککردنەوە", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    with col2:
        if st.button("↩️", help="سڕینەوە", use_container_width=True):
            if len(st.session_state.messages) >= 2:
                st.session_state.messages = st.session_state.messages[:-2]
                st.rerun()
    with col3:
        if st.button("💾", help="هەڵگرتن", use_container_width=True):
            st.success("هەڵگیرا!")
    
    # هەناردە
    if "messages" in st.session_state and st.session_state.messages:
        chat_text = "\n\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
        st.download_button("📥 هەناردە", chat_text, "گفتوگۆ.txt", use_container_width=True)

# ═══════════════════════════════════════
# بەشی سەرەکی
# ═══════════════════════════════════════

# Tab -ەکان
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "💬 گفتوگۆ", "📄 فایل", "🌐 وەرگێڕان", "📊 داتا", "🔍 گەڕان", "📝 کورتکردنەوە"
])

# ═══════════════════════════════════════
# TAB 1: گفتوگۆ
# ═══════════════════════════════════════
with tab1:
    st.header("💬 گفتوگۆی زیرەک")
    
    if not api_key:
        st.warning("تکایە کلیلی API بنووسە")
        st.stop()
    
    client = Groq(api_key=api_key)
    
    # system message
    personality_prompts = {
        "یاریدەدەری ئاسایی": "You are a helpful assistant.",
        "مامۆستای شارەزا": "You are an expert teacher. Explain things clearly and thoroughly.",
        "دۆستی میهرەبان": "You are a friendly and supportive friend. Be warm and encouraging.",
        "پرۆگرامەری پیشەگەر": "You are a professional programmer. Provide code examples and technical explanations.",
        "شاعیری خەیاڵی": "You are a creative poet. Respond in a poetic and artistic style.",
        "ڕەخنەگری وردبین": "You are a critical reviewer. Analyze carefully and provide constructive feedback."
    }
    
    system_messages = {
        "کوردی": personality_prompts[personality] + " IMPORTANT: Respond in Kurdish (Sorani, Arabic script).",
        "عەرەبی": personality_prompts[personality] + " IMPORTANT: Respond in Arabic.",
        "ئینگلیزی": personality_prompts[personality] + " Respond in English."
    }
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # نمایشی مێژوو
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    # پرسیاری دەنگی (سادە)
    col1, col2 = st.columns([5, 1])
    with col2:
        if st.button("🎙️", help="تۆمارکردنی دەنگ", use_container_width=True):
            st.info("تایبەتمەندی دەنگ لە Cloud پشتگیری ناکرێت. لە کۆمپیوتەری خۆت کاردەکات.")
    
    # چاتی سەرەکی
    prompt = st.chat_input("پرسیارەکەت بنووسە...")
    
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("assistant"):
            with st.spinner("🤔"):
                try:
                    response = client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": system_messages[language]},
                            *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                        ],
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                    reply = response.choices[0].message.content
                    st.write(reply)
                    
                    # دوگمەی دەنگ
                    col1, col2, col3 = st.columns([1, 1, 4])
                    with col1:
                        if st.button("🔊", key=f"tts_{len(st.session_state.messages)}", help="بیخوێنەوە"):
                            try:
                                tts = gTTS(text=reply, lang='ar' if language in ['کوردی', 'عەرەبی'] else 'en')
                                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                                    tts.save(fp.name)
                                    st.audio(fp.name, format='audio/mp3')
                            except:
                                st.warning("نەتوانرا دەنگ دروست بکرێت")
                    
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                    
                except Exception as e:
                    st.error(f"هەڵە: {e}")

# ═══════════════════════════════════════
# TAB 2: فایل
# ═══════════════════════════════════════
with tab2:
    st.header("📄 شیکاری فایل")
    
    sub_tab1, sub_tab2 = st.tabs(["📝 PDF/TXT", "🖼️ وێنە"])
    
    with sub_tab1:
        uploaded_file = st.file_uploader("فایل باربکە:", type=["pdf", "txt"], key="file_tab")
        
        if uploaded_file:
            try:
                if uploaded_file.type == "application/pdf":
                    pdf_bytes = uploaded_file.read()
                    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                    file_text = ""
                    for page in doc:
                        file_text += page.get_text()
                    doc.close()
                else:
                    file_text = uploaded_file.read().decode("utf-8")
                
                with st.expander("📋 ناوەڕۆک", expanded=True):
                    st.text_area("", file_text, height=200)
                
                if st.button("🔍 شیکاری بکە", type="primary"):
                    st.info("بەشی شیکاری فایل - ئەنجامەکە لە Tab ی گفتوگۆ دەردەکەوێت")
                    
            except Exception as e:
                st.error(f"هەڵە: {e}")
    
    with sub_tab2:
        uploaded_image = st.file_uploader("وێنە باربکە:", type=["png", "jpg", "jpeg"], key="img_tab")
        
        if uploaded_image:
            image = Image.open(uploaded_image)
            st.image(image, caption="وێنەکەت", use_column_width=True)
            
            # OCR سادە
            if st.button("🔍 خوێندنەوەی دەقی وێنە (OCR)"):
                try:
                    import pytesseract
                    text = pytesseract.image_to_string(image, lang='ara+eng')
                    st.text_area("دەقی دۆزراوە:", text, height=150)
                except:
                    st.warning("OCR لە Cloud کارناکات. پێویستت بە Tesseract هەیە.")

# ═══════════════════════════════════════
# TAB 3: وەرگێڕان
# ═══════════════════════════════════════
with tab3:
    st.header("🌐 وەرگێڕانی دەق")
    
    col1, col2 = st.columns(2)
    
    with col1:
        source_lang = st.selectbox("زمانی سەرچاوە:", ["auto", "ku", "ar", "en", "fa", "tr"])
        text_to_translate = st.text_area("دەق بنووسە:", height=150)
    
    with col2:
        target_lang = st.selectbox("زمانی مەبەست:", ["ku", "ar", "en", "fa", "tr"])
        
        if st.button("🔄 وەربگێڕە", type="primary", use_container_width=True) and text_to_translate:
            try:
                translated = GoogleTranslator(source=source_lang if source_lang != "auto" else 'auto',
                                            target=target_lang).translate(text_to_translate)
                st.text_area("وەرگێڕدراو:", translated, height=150)
                
                # دوگمەی بیخوێنەوە
                if st.button("🔊 بیخوێنەوە"):
                    tts = gTTS(text=translated, lang=target_lang if target_lang != 'ku' else 'ar')
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                        tts.save(fp.name)
                        st.audio(fp.name, format='audio/mp3')
            except Exception as e:
                st.error(f"هەڵە: {e}")

# ═══════════════════════════════════════
# TAB 4: داتا و چارت
# ═══════════════════════════════════════
with tab4:
    st.header("📊 شیکاری داتا و چارت")
    
    # نموونە داتا
    st.subheader("داتای نموونە")
    sample_data = pd.DataFrame({
        'مانگ': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
        'فرۆش': [100, 150, 200, 180, 220],
        'قازانج': [20, 45, 60, 50, 80]
    })
    
    edited_data = st.data_editor(sample_data, num_rows="dynamic", use_container_width=True)
    
    if st.button("📊 دروستکردنی چارت", type="primary"):
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = px.line(edited_data, x='مانگ', y=['فرۆش', 'قازانج'], title='فرۆش و قازانج')
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            fig2 = px.bar(edited_data, x='مانگ', y='فرۆش', title='ڕێژەی فرۆش')
            st.plotly_chart(fig2, use_container_width=True)
    
    # بارکردنی CSV
    st.markdown("---")
    csv_file = st.file_uploader("فایلی CSV باربکە:", type="csv")
    if csv_file:
        df = pd.read_csv(csv_file)
        st.dataframe(df, use_container_width=True)
        
        if st.button("📈 چارتی CSV"):
            numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
            if numeric_cols:
                fig = px.bar(df, x=df.columns[0], y=numeric_cols[0] if len(numeric_cols) > 0 else df.columns[1])
                st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════
# TAB 5: گەڕان
# ═══════════════════════════════════════
with tab5:
    st.header("🔍 گەڕان لە ئینتەرنێت")
    
    search_query = st.text_input("گەڕان:", placeholder="شتێک بگەڕێ...")
    
    if search_query and st.button("🔍 بگەڕێ", type="primary"):
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                results = list(ddgs.text(search_query, max_results=5))
                
                for i, result in enumerate(results, 1):
                    with st.container():
                        st.markdown(f"### {i}. [{result['title']}]({result['href']})")
                        st.write(result['body'])
                        st.markdown("---")
        except Exception as e:
            st.error("گەڕان لە Cloud کارناکات. پێویستت بە ڕێکخستنی تایبەت هەیە.")

# ═══════════════════════════════════════
# TAB 6: کورتکردنەوە
# ═══════════════════════════════════════
with tab6:
    st.header("📝 کورتکردنەوەی دەق")
    
    text_to_summarize = st.text_area("دەقی درێژ لێرە بنووسە:", height=200)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        max_length = st.slider("درێژی کورتە:", 50, 300, 150)
    with col2:
        min_length = st.slider("کەمترین درێژی:", 20, 100, 40)
    
    if st.button("📝 کورت بکەوە", type="primary") and text_to_summarize:
        if api_key:
            try:
                client = Groq(api_key=api_key)
                response = client.chat.completions.create(
                    model=model,
                    messages=[{
                        "role": "user",
                        "content": f"Please summarize the following text in {language}:\n\n{text_to_summarize}\n\nSummary should be between {min_length} and {max_length} characters."
                    }],
                    temperature=0.3,
                    max_tokens=max_length
                )
                summary = response.choices[0].message.content
                st.text_area("کورتە:", summary, height=150)
            except Exception as e:
                st.error(f"هەڵە: {e}")
        else:
            st.warning("کلیلی API پێویستە")

# ═══════════════════════════════════════
# پەراوێز
# ═══════════════════════════════════════
st.markdown("---")
st.caption(f"🚀 سوپەر ئەپی AI | دروستکراوە بە Streamlit | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
