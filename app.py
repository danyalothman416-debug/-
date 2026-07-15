import streamlit as st
import base64

# ========== ڕێکخستنی پەڕە ==========
st.set_page_config(
    page_title="ئەپەکەم | My App",
    page_icon="🏠",
    layout="wide"
)

# ========== PWA - بۆ گۆگڵ و داخڵ بوون ==========
def make_pwa():
    """ئەم فەنکشەنە وا دەکات ئەپەکەت وەک ماڵپەڕ لە گۆگڵ دابنرێت"""
    
    pwa_code = """
    <head>
        <!-- ئایکۆنی ئەپ بۆ مۆبایل -->
        <link rel="apple-touch-icon" href="🏠">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-title" content="ئەپەکەم">
        
        <!-- ڕەنگی theme -->
        <meta name="theme-color" content="#4CAF50">
        
        <!-- manifest بۆ PWA -->
        <link rel="manifest" href="data:application/json;base64,eyJuYW1lIjoiMjAyNjAxMDgifQ==">
        
        <script>
            // تۆمارکردنی Service Worker
            if ('serviceWorker' in navigator) {
                window.addEventListener('load', () => {
                    navigator.serviceWorker.register('/sw.js')
                        .then(() => console.log('✅ Service Worker تۆمارکرا'))
                        .catch(() => console.log('❌ هەڵە'));
                });
            }
        </script>
    </head>
    """
    
    st.markdown(pwa_code, unsafe_allow_html=True)

# ========== CSS بۆ بەکگراوند ==========
def set_style():
    st.markdown("""
    <style>
    /* بەکگراوندی سەرەکی */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* ناونیشانەکان */
    h1 {
        color: white !important;
        text-align: center;
        font-size: 3rem !important;
    }
    
    /* دوگمەکان */
    .stButton > button {
        background: #4CAF50 !important;
        color: white !important;
        font-size: 1.2rem !important;
        border-radius: 10px !important;
        padding: 10px 30px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ========== ئەپی سەرەکی ==========
def main():
    # داگرتنی PWA
    make_pwa()
    
    # ستایلی بەکگراوند
    set_style()
    
    # ===== ناوەڕۆک =====
    st.title("🏠 بەخێربێیت بۆ ئەپەکەم!")
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("👥 بەکارهێنەران", "1,234", "+15%")
    with col2:
        st.metric("💰 فرۆشتن", "$5,678", "+8%")
    with col3:
        st.metric("⭐ ڕێژەی ڕەزامەندی", "98%", "+2%")
    
    st.markdown("---")
    
    # فۆرمی سادە
    with st.form("my_form"):
        name = st.text_input("👤 ناوت بنووسە:")
        email = st.text_input("📧 ئیمەیڵت بنووسە:")
        submitted = st.form_submit_button("📩 ناردن")
        
        if submitted:
            st.success(f"✅ سڵاو {name}! بە سەرکەوتوویی نێردرا")

# ========== Service Worker فایل ==========
def create_sw_file():
    """دروستکردنی فایلی service worker بە شێوازی سادە"""
    sw_code = """
self.addEventListener('install', (e) => {
    console.log('PWA App: installed');
});

self.addEventListener('fetch', (e) => {
    e.respondWith(fetch(e.request));
});
"""
    # ئەمە تەنها ئاماژەیە - بۆ Streamlit Cloud پێویست بە sw.js نییە

# ========== ڕاکردن ==========
if __name__ == "__main__":
    main()
