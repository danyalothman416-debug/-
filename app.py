import streamlit as st

# ١. ڕێکخستنی سەرەتایی پەڕەکە (دەبێت یەکەم کۆد بێت)
st.set_page_config(page_title="دوکانی مۆبایل", page_icon="📱", layout="centered")

# ٢. جوانکاری (CSS) بۆ ڕاستکردنەوەی فۆنت و دروستکردنی دوگمەی وەتساپ
st.markdown("""
<style>
    /* ئاراستەی نووسین بۆ لای ڕاست */
    body, .stApp {
        direction: rtl;
        text-align: right;
    }
    /* جوانکردنی تابەکان */
    .stTabs [data-baseweb="tab-list"] {
        display: flex;
        justify-content: center;
    }
    /* دیزاینی دوگمەی وەتساپ */
    .whatsapp-btn {
        background-color: #25D366;
        color: white !important;
        padding: 10px 15px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        border-radius: 8px;
        font-weight: bold;
        width: 100%;
        margin-top: 10px;
    }
    .whatsapp-btn:hover {
        background-color: #128C7E;
    }
</style>
""", unsafe_allow_html=True)

# --- لێرە ژمارەی مۆبایلەکەت بنووسە (بە کۆدی عێراقەوە 964 بێ پلەس) ---
MY_NUMBER = "9647700000000"

# ٣. سەرەدێڕی دوکانەکە
st.title("📱 فرۆشگای دیجیتاڵیی مۆبایل")
st.write("بەخێربێیت! لێرە باشترین کاڵا و خزمەتگوزارییەکان بەدەست بهێنە.")
st.markdown("---")

# ٤. دروستکردنی تابەکان (بەشەکان)
tab1, tab2, tab3, tab4 = st.tabs(["📱 مۆبایل", "🎮 یوسی", "💳 باڵانس", "🌟 VIP ژمارە"])

# ==========================================
# بەشی یەکەم: مۆبایلەکان
# ==========================================
with tab1:
    st.subheader("نوێترین مۆبایلەکان")
    # دابەشکردنی شاشەکە بۆ دوو بەش
    col1, col2 = st.columns(2)
    
    with col1:
        st.image("https://fdn2.gsmarena.com/vv/bigpic/apple-iphone-15-pro-max.jpg") 
        st.markdown("**iPhone 15 Pro Max**")
        st.write("بیرگە: 256GB | ڕەنگ: تیتانیۆم")
        st.error("نرخ: $1200")
        msg1 = "سڵاو، دەمەوێت پرسیار لەسەر iPhone 15 Pro Max بکەم."
        st.markdown(f'<a href="https://wa.me/{MY_NUMBER}?text={msg1}" class="whatsapp-btn" target="_blank">کڕین لە وەتساپ 🟢</a>', unsafe_allow_html=True)

    with col2:
        st.image("https://fdn2.gsmarena.com/vv/bigpic/samsung-galaxy-s24-ultra-5g-sm-s928-stylus.jpg")
        st.markdown("**Galaxy S24 Ultra**")
        st.write("بیرگە: 512GB | ڕەنگ: ڕەش")
        st.error("نرخ: $1150")
        msg2 = "سڵاو، دەمەوێت پرسیار لەسەر Galaxy S24 Ultra بکەم."
        st.markdown(f'<a href="https://wa.me/{MY_NUMBER}?text={msg2}" class="whatsapp-btn" target="_blank">کڕین لە وەتساپ 🟢</a>', unsafe_allow_html=True)

# ==========================================
# بەشی دووەم: یوسی و سپۆنسەر
# ==========================================
with tab2:
    st.subheader("یوسی پۆبجی و سپۆنسەری یوتیوب")
    
    st.markdown("#### 🎮 یوسی پۆبجی")
    uc1, uc2, uc3 = st.columns(3)
    with uc1:
        st.info("325 UC\n\n **5,000 IQD**")
        st.markdown(f'<a href="https://wa.me/{MY_NUMBER}?text=سڵاو، دەمەوێت 325 یوسی بکڕم" class="whatsapp-btn" target="_blank">کڕین 🟢</a>', unsafe_allow_html=True)
    with uc2:
        st.info("660 UC\n\n **10,000 IQD**")
        st.markdown(f'<a href="https://wa.me/{MY_NUMBER}?text=سڵاو، دەمەوێت 660 یوسی بکڕم" class="whatsapp-btn" target="_blank">کڕین 🟢</a>', unsafe_allow_html=True)
    with uc3:
        st.info("1800 UC\n\n **25,000 IQD**")
        st.markdown(f'<a href="https://wa.me/{MY_NUMBER}?text=سڵاو، دەمەوێت 1800 یوسی بکڕم" class="whatsapp-btn" target="_blank">کڕین 🟢</a>', unsafe_allow_html=True)
        
    st.markdown("---")
    st.markdown("#### 📺 سپۆنسەری یوتیوب")
    st.success("پاکێجی زیادکردنی بینەر (Views) - 10,000 بینەر بە $10")
    st.markdown(f'<a href="https://wa.me/{MY_NUMBER}?text=سڵاو، دەمەوێت پاکێجی ڤیوی یوتیوب بکڕم" class="whatsapp-btn" target="_blank">داواکردن 🟢</a>', unsafe_allow_html=True)

# ==========================================
# بەشی سێیەم: کارتی باڵانس
# ==========================================
with tab3:
    st.subheader("کارتەکانی باڵانس")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### 🔴 کۆڕەک")
    with c2:
        st.markdown("### 🟣 ئاسیاسێڵ")
    with c3:
        st.markdown("### 🔵 زەین")
        
    st.markdown(f'<a href="https://wa.me/{MY_NUMBER}?text=سڵاو، دەمەوێت کارتی باڵانس بکڕم" class="whatsapp-btn" target="_blank">داواکردنی کارت لە وەتساپ 🟢</a>', unsafe_allow_html=True)

# ==========================================
# بەشی چوارەم: ژمارەی VIP
# ==========================================
with tab4:
    st.subheader("🌟 ژمارە ناوازەکان (VIP)")
    st.write("پەلە بکە پێش ئەوەی بفرۆشرێن!")
    
    # بەکارهێنانی ڕەنگی جیاواز بۆ سەرنجڕاکێشان
    st.warning("🟣 ئاسیاسێڵ: 0770 000 1234 - نرخ: $500")
    st.markdown(f'<a href="https://wa.me/{MY_NUMBER}?text=سڵاو، دەمەوێت ژمارەی 07700001234 بکڕم" class="whatsapp-btn" target="_blank">کڕینی ئەم ژمارەیە 🟢</a>', unsafe_allow_html=True)
    
    st.info("🔵 زەین: 0780 999 999X - نرخ: $800")
    st.markdown(f'<a href="https://wa.me/{MY_NUMBER}?text=سڵاو، دەمەوێت ژمارەی زەین 0780999999X بکڕم" class="whatsapp-btn" target="_blank">کڕینی ئەم ژمارەیە 🟢</a>', unsafe_allow_html=True)

