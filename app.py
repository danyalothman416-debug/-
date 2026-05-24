# ============================================
# MOBILE SHOP APP UI - STREAMLIT
# ============================================

import streamlit as st

# ============================================
# PAGE CONFIG
# ============================================

st.set_page_config(
    page_title="دووکانی مۆبایل",
    page_icon="📱",
    layout="wide"
)

# ============================================
# CSS DESIGN
# ============================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Cairo', sans-serif;
    direction: rtl;
}

.main {
    background-color: #f5f7fb;
}

.title {
    font-size: 38px;
    font-weight: bold;
    color: #222;
    margin-bottom: 20px;
}

.search-box input {
    border-radius: 15px;
}

.banner {
    background: linear-gradient(135deg,#5B4BFF,#8A7DFF);
    padding: 40px;
    border-radius: 25px;
    color: white;
    margin-bottom: 30px;
}

.banner h1 {
    font-size: 42px;
}

.banner p {
    font-size: 20px;
}

.product-card {
    background: white;
    padding: 20px;
    border-radius: 20px;
    box-shadow: 0px 5px 20px rgba(0,0,0,0.08);
    text-align: center;
    transition: 0.3s;
    margin-bottom: 20px;
}

.product-card:hover {
    transform: translateY(-8px);
}

.product-image {
    width: 100%;
    border-radius: 15px;
}

.product-name {
    font-size: 22px;
    font-weight: bold;
    margin-top: 15px;
    color: #222;
}

.product-price {
    color: #5B4BFF;
    font-size: 24px;
    font-weight: bold;
    margin-top: 10px;
}

.buy-btn {
    background: #5B4BFF;
    color: white;
    border: none;
    padding: 12px 25px;
    border-radius: 12px;
    font-size: 18px;
    margin-top: 15px;
    cursor: pointer;
}

.section-title {
    font-size: 30px;
    font-weight: bold;
    margin-bottom: 20px;
    color: #222;
}

.sidebar .sidebar-content {
    background: white;
}

</style>
""", unsafe_allow_html=True)

# ============================================
# SIDEBAR
# ============================================

st.sidebar.title("📱 مێنیو")

page = st.sidebar.radio(
    "هەڵبژاردن",
    [
        "🏠 سەرەکی",
        "📱 مۆبایلەکان",
        "🎧 ئامێرەکان",
        "🛒 سەبەتە",
        "👤 هەژمار"
    ]
)

# ============================================
# HOME PAGE
# ============================================

if page == "🏠 سەرەکی":

    st.markdown('<div class="title">📱 دووکانی مۆبایل</div>', unsafe_allow_html=True)

    st.text_input("🔍 گەڕان بە ناوی مۆبایل")

    st.markdown("""
    <div class="banner">
        <h1>iPhone 15 Pro</h1>
        <p>باشترین ئۆفەر بۆ ئەم هەفتەیە 🔥</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">🔥 باشترین فرۆشراوەکان</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="product-card">
            <img class="product-image" src="https://images.unsplash.com/photo-1592750475338-74b7b21085ab">
            <div class="product-name">iPhone 15 Pro Max</div>
            <div class="product-price">$1199</div>
            <button class="buy-btn">🛒 کڕین</button>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="product-card">
            <img class="product-image" src="https://images.unsplash.com/photo-1610945265064-0e34e5519bbf">
            <div class="product-name">Samsung S24 Ultra</div>
            <div class="product-price">$1299</div>
            <button class="buy-btn">🛒 کڕین</button>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="product-card">
            <img class="product-image" src="https://images.unsplash.com/photo-1606229365485-93a3b8ee0385">
            <div class="product-name">AirPods Pro</div>
            <div class="product-price">$249</div>
            <button class="buy-btn">🛒 کڕین</button>
        </div>
        """, unsafe_allow_html=True)

# ============================================
# MOBILE PAGE
# ============================================

elif page == "📱 مۆبایلەکان":

    st.markdown('<div class="section-title">📱 مۆبایلەکان</div>', unsafe_allow_html=True)

    phones = [
        ("iPhone 15 Pro Max", "$1199"),
        ("Samsung S24 Ultra", "$1299"),
        ("Xiaomi 14", "$899"),
        ("Google Pixel 8", "$999")
    ]

    for phone, price in phones:
        st.markdown(f"""
        <div class="product-card">
            <div class="product-name">{phone}</div>
            <div class="product-price">{price}</div>
            <button class="buy-btn">🛒 زیادکردن</button>
        </div>
        """, unsafe_allow_html=True)

# ============================================
# ACCESSORIES PAGE
# ============================================

elif page == "🎧 ئامێرەکان":

    st.markdown('<div class="section-title">🎧 ئامێرەکان</div>', unsafe_allow_html=True)

    accessories = [
        ("AirPods Pro", "$249"),
        ("Apple Watch", "$399"),
        ("Anker Charger", "$49"),
        ("Gaming Headset", "$99")
    ]

    for item, price in accessories:
        st.markdown(f"""
        <div class="product-card">
            <div class="product-name">{item}</div>
            <div class="product-price">{price}</div>
            <button class="buy-btn">🛒 کڕین</button>
        </div>
        """, unsafe_allow_html=True)

# ============================================
# CART PAGE
# ============================================

elif page == "🛒 سەبەتە":

    st.markdown('<div class="section-title">🛒 سەبەتەی کڕین</div>', unsafe_allow_html=True)

    st.success("iPhone 15 Pro Max زیادکرا")

    st.markdown("""
    <div class="product-card">
        <div class="product-name">کۆی گشتی</div>
        <div class="product-price">$1199</div>
    </div>
    """, unsafe_allow_html=True)

    st.button("💳 تەواوکردنی کڕین")

# ============================================
# PROFILE PAGE
# ============================================

elif page == "👤 هەژمار":

    st.markdown('<div class="section-title">👤 هەژمار</div>', unsafe_allow_html=True)

    st.text_input("ناو")
    st.text_input("ئیمەیڵ")
    st.text_input("ژمارەی مۆبایل")

    st.button("💾 پاشەکەوتکردن")
