import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Golden Delivery", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# Initialize Session States
if 'page' not in st.session_state:
    st.session_state.page = "home"
if 'user_email' not in st.session_state:
    st.session_state.user_email = None

# --- 2. MULTI-LANGUAGE & UI STRINGS ---
languages = {
    "English 🇬🇧": {
        "dir": "ltr", "align": "left", "theme_label": "Theme", "light": "Light ☀️", "dark": "Dark 🌙",
        "title": "GOLDEN DELIVERY",
        "desc": "Experience the gold standard of logistics in Kirkuk. Fast, secure, and always on time.",
        "customer_name": "Customer Name", "shop_name": "Shop Name", 
        "shop_addr": "Shop Address", "phone": "Phone Number", 
        "area": "Neighborhood", "full_addr": "Address Details (Near what?)",
        "price": "Price (IQD)", "submit": "Confirm Order", 
        "nav_home": "Home", "nav_order": "Order", "nav_profile": "Account",
        "free_info": "🎁 Special: 1 out of every 3 deliveries is FREE!",
        "free_success": "🎊 Loyalty Reward: This delivery is 0 IQD!",
        "google_btn": "Sign in with Google", "logout": "Logout",
        "settings": "Settings & Language",
        "terms_title": "📜 Terms and Rules",
        "terms_text": """
        1. Golden Delivery is not responsible for illegal or prohibited items.
        2. Delivery prices are fixed at 3,000 IQD unless a loyalty discount applies.
        3. Fragile items must be packed properly by the shop; we are not liable for poor packaging.
        4. Cancellations must be made within 10 minutes of ordering.
        5. Every 3rd successful delivery to the same phone number is free of charge.
        """,
        "mgmt_links": "🔗 Management Links"
    },
    "کوردی 🇭🇺": {
        "dir": "rtl", "align": "right", "theme_label": "ڕووکار", "light": "ڕوون ☀️", "dark": "تاریک 🌙",
        "title": "گۆڵدن دلیڤەری",
        "desc": "بەرزترین کوالێتی گەیاندن لە کەرکوک. خێرا، پارێزراو، و هەمیشە لە کاتی خۆیدا.",
        "customer_name": "ناوی کڕیار", "shop_name": "ناوی دوکان", 
        "shop_addr": "ناونیشانی دوکان", "phone": "ژمارەی مۆبایل", 
        "area": "گەڕەک", "full_addr": "وردەکاری ناونیشان (نزیک کوێیە؟)",
        "price": "نرخ (د.ع)", "submit": "تۆمارکردن", 
        "nav_home": "سەرەکی", "nav_order": "داواکردن", "nav_profile": "هەژمار",
        "free_info": "🎁 دیاری: یەکێک لە هەر ٣ گەیاندنێک بە خۆڕاییە!",
        "free_success": "🎊 پیرۆزە! ئەم گەیاندنەت بە ٠ دینارە!",
        "google_btn": "چوونەژوورەوە بە Google", "logout": "چوونەدەرەوە",
        "settings": "ڕێکخستن و زمان",
        "terms_title": "📜 مەرج و ڕێساکان",
        "terms_text": """
        ١. گۆڵدن دلیڤەری بەرپرسیار نییە لە گواستنەوەی کاڵای قەدەغەکراو.
        ٢. نرخی گەیاندن ٣،٠٠٠ دینارە مەگەر ئۆفەری سێیەم بێت.
        ٣. کاڵای شکاوه دەبێت لەلایەن دوکانەوە بە باشی داپۆشرێت.
        ٤. هەڵوەشاندنەوەی داواکاری تەنها لە ١٠ خولەکی یەکەمدا دەبێت.
        ٥. هەموو گەیاندنی سێیەم بۆ هەمان ژمارە بە خۆڕاییە.
        """,
        "mgmt_links": "🔗 لینکەکانی بەڕێوەبردن"
    },
    "العربية 🇮🇶": {
        "dir": "rtl", "align": "right", "theme_label": "المظهر", "light": "فاتح ☀️", "dark": "داكن 🌙",
        "title": "گولدن دليفري",
        "desc": "المعيار الذهبي للخدمات اللوجستية في كركوك. سرعة، أمان، ودقة في المواعيد.",
        "customer_name": "اسم الزبون", "shop_name": "اسم المحل", 
        "shop_addr": "عنوان المحل", "phone": "رقم الهاتف", 
        "area": "المنطقة", "full_addr": "تفاصيل العنوان (قرب ماذا؟)",
        "price": "السعر (د.ع)", "submit": "تأكيد الطلب", 
        "nav_home": "الرئيسية", "nav_order": "طلب", "nav_profile": "الحساب",
        "free_info": "🎁 عرض: واحدة من كل ٣ توصيلات مجانية!",
        "free_success": "🎊 مبروك! هذه الطلبية بـ ٠ دينار!",
        "google_btn": "الدخول بواسطة Google", "logout": "خروج",
        "settings": "الإعدادات واللغة",
        "terms_title": "📜 الشروط والقواعد",
        "terms_text": """
        ١. جولدن دليفري غير مسؤولة عن نقل المواد المحظورة قانونياً.
        ٢. سعر التوصيل ثابت ٣,٠٠٠ دينار إلا في حالة العرض المجاني.
        ٣. المواد القابلة للكسر يجب تغليفها جيداً من قبل المحل.
        ٤. يمكن إلغاء الطلب خلال ١٠ دقائق فقط من تسجيله.
        ٥. كل توصيل ثالث لنفس رقم الهاتف يكون مجانياً بالكامل.
        """,
        "mgmt_links": "🔗 روابط الإدارة"
    }
}

# --- 3. NEIGHBORHOODS ---
KIRKUK_AREAS = sorted([
    "Arfa / عرفة", "Tis'in / تسعين", "Binja Ali / بنجة علي", "Shoraw / شوراو",
    "Rahim Awa / رحيماوة", "Laylawa / ليلان", "Wasit / واسطي", "Al-Musalla / مصلى",
    "Quraya / قورية", "Dumiz / دوميز", "Al-Khadra / الخضراء", "Al-Wasiti / الواسطي",
    "Al-Askari / الحي العسكري", "Al-Qadisiyya / القادسية", "Al-Nasr / النصر", 
    "Azadi / ازادي", "Shura / شورى", "Al-Nabi Yunus / النبي يونس", "Al-Shorja / الشورجة",
    "Wahid Huzairan / واحد حزيران", "Ronaki / رونكي", "Biriti / بريتي", "Sarhad / سرحد",
    "Shahidan / شهيدان", "Tarkalan / تركلان", "Haidar Khana / حيدر خانة", "Sayyada / صيادة",
    "Al-Mu'allimin / المعلمين", "Al-Muhandisin / المهندسين", "Al-Atibba / الاطباء",
    "Al-Adala / العدالة", "Al-Salam / السلام", "Taza Khurmato / تازة خورماتو", 
    "Yaychi / يايجي", "Daquq / داقوق", "Laylan / ليلان", "Malha / ملحة", 
    "Bashir / بشير", "Tarjala / ترجلة"
])

# --- 4. THEME & CSS ---
# Consolidate Settings into Top Nav
with st.container():
    c_logo, c_set = st.columns([2, 1])
    with c_set:
        with st.expander("⚙️ Settings"):
            lang_choice = st.selectbox("🌐 Language", list(languages.keys()))
            L = languages[lang_choice]
            theme_choice = st.radio(L['theme_label'], [L['light'], L['dark']], horizontal=True)
    with c_logo:
        L = languages[lang_choice]
        st.markdown(f"<h2 style='color:#D4AF37; margin:0;'>{L['title']}</h2>", unsafe_allow_html=True)

is_dark = theme_choice == L['dark']
main_bg = "#0f1116" if is_dark else "#fdfdfd"
card_bg = "rgba(30, 34, 45, 0.85)" if is_dark else "rgba(255, 255, 255, 0.98)"
text_color = "#ffffff" if is_dark else "#1a1a1a"
accent = "#D4AF37"

st.markdown(f"""
    <style>
    [data-testid="stSidebar"] {{ display: none; }}
    html, body, [data-testid="stAppViewContainer"] {{
        background: {main_bg};
        color: {text_color} !important;
        direction: {L['dir']};
    }}
    label, p, span, h1, h2, h3, div {{ color: {text_color} !important; }}
    .stForm {{
        background: {card_bg} !important;
        border: 1px solid {accent}55 !important;
        border-radius: 20px !important;
        padding: 25px !important;
    }}
    .brand-header {{
        background: linear-gradient(135deg, #D4AF37 0%, #8A6D3B 100%);
        padding: 40px; border-radius: 0 0 40px 40px; text-align: center;
    }}
    .terms-box {{
        background: {card_bg};
        border-top: 2px solid {accent};
        padding: 20px; margin-top: 50px; border-radius: 15px;
        font-size: 0.9rem; opacity: 0.9;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. DATA LOGIC ---
DB_FILE = "deliveries.csv"
def load_data():
    if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE, dtype={"phone": str})
    return pd.DataFrame(columns=["date", "customer", "shop", "phone", "area", "address", "shop_addr", "price", "status", "user_email"])

# --- 6. PAGE CONTENT ---

if st.session_state.page == "home":
    st.markdown(f'<div class="brand-header"><h1 style="color:white; margin:0;">{L["title"]}</h1></div>', unsafe_allow_html=True)
    st.markdown(f"<div style='text-align:center; padding:40px;'><h3>Kirkuk's Premiere Logistics</h3><p>{L['desc']}</p></div>", unsafe_allow_html=True)

elif st.session_state.page == "order":
    st.markdown(f"<h2 style='text-align:center; color:{accent};'>{L['nav_order']}</h2>", unsafe_allow_html=True)
    st.info(L["free_info"])
    
    df = load_data()
    phone_input = st.text_input(L['phone'], placeholder="07xx xxx xxxx")
    
    is_free = False
    if phone_input:
        count = len(df[df['phone'] == phone_input])
        is_free = (count + 1) % 3 == 0
        if is_free: st.success(L["free_success"])

    with st.form("order_form"):
        c1, c2 = st.columns(2)
        with c1:
            customer = st.text_input(L['customer_name'])
            shop = st.text_input(L['shop_name'])
            area = st.selectbox(L['area'], ["-- Select --"] + KIRKUK_AREAS)
        with c2:
            shop_addr = st.text_input(L['shop_addr'])
            full_addr = st.text_area(L['full_addr'])
            price = st.number_input(L['price'], value=0 if is_free else 3000)
        
        if st.form_submit_button(L['submit'], use_container_width=True):
            if customer and phone_input and "--" not in area:
                new_row = pd.DataFrame([{"date": datetime.now().strftime("%Y-%m-%d"), "customer": customer, "shop": shop, "phone": phone_input, "area": area, "address": full_addr, "shop_addr": shop_addr, "price": price, "status": "Pending", "user_email": st.session_state.user_email}])
                pd.concat([df, new_row]).to_csv(DB_FILE, index=False)
                st.success("✅ Registered!")

elif st.session_state.page == "profile":
    st.markdown(f"<h2 style='text-align:center; color:{accent};'>{L['nav_profile']}</h2>", unsafe_allow_html=True)
    
    if st.session_state.user_email is None:
        if st.button(L["google_btn"], use_container_width=True):
            st.session_state.user_email = "admin@goldendelivery.com"
            st.rerun()
    else:
        st.write(f"Logged in as: {st.session_state.user_email}")
        
        # Admin / Management Links Section
        st.subheader(L["mgmt_links"])
        st.write("Click the links below to manage your private website and databases:")
        st.markdown("- [Admin Dashboard](https://your-private-link.com/admin)")
        st.markdown("- [Database View](https://your-private-link.com/database)")
        
        if st.button(L["logout"]):
            st.session_state.user_email = None
            st.rerun()
        
        st.divider()
        st.dataframe(load_data(), use_container_width=True)

# --- 7. FOOTER: TERMS & RULES ---
st.markdown(f"""
    <div class="terms-box">
        <h4>{L['terms_title']}</h4>
        <p style="white-space: pre-wrap;">{L['terms_text']}</p>
    </div>
    """, unsafe_allow_html=True)

# --- 8. BOTTOM NAVIGATION ---
st.markdown("<br><br><br>", unsafe_allow_html=True)
n1, n2, n3 = st.columns(3)
with n1:
    if st.button(L["nav_home"], use_container_width=True): st.session_state.page="home"; st.rerun()
with n2:
    if st.button(L["nav_order"], use_container_width=True): st.session_state.page="order"; st.rerun()
with n3:
    if st.button(L["nav_profile"], use_container_width=True): st.session_state.page="profile"; st.rerun()
