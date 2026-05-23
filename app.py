import streamlit as st
from streamlit_option_menu import option_menu

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="ڕێبەری پشکنینە تاقیگەییەکان", 
    layout="wide", 
    initial_sidebar_state="collapsed",
    page_icon="🔬"
)

# --- CSS STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Naskh+Arabic:wght@400;700&display=swap');
    
    * {
        font-family: 'Noto Naskh Arabic', 'Segoe UI', sans-serif;
    }
    
    [data-testid="stSidebar"] {
        display: none;
    }
    
    html, body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #F5F7FA 0%, #E8EDF2 100%) !important;
    }
    
    .header-card {
        background: linear-gradient(135deg, #1a237e 0%, #283593 50%, #3949ab 100%);
        border-radius: 25px;
        padding: 35px;
        color: white !important;
        margin-bottom: 30px;
        text-align: center;
        box-shadow: 0 15px 40px rgba(26,35,126,0.3);
        position: relative;
        overflow: hidden;
    }
    
    .header-card::before {
        content: '🔬';
        position: absolute;
        left: -30px;
        top: -30px;
        font-size: 150px;
        opacity: 0.1;
        transform: rotate(-20deg);
    }
    
    .header-card::after {
        content: '🧬';
        position: absolute;
        right: -30px;
        bottom: -30px;
        font-size: 150px;
        opacity: 0.1;
        transform: rotate(20deg);
    }
    
    .header-card * {
        color: white !important;
        position: relative;
        z-index: 1;
    }
    
    .test-card {
        background: white;
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 25px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.08);
        border-right: 6px solid #3949ab;
        transition: all 0.3s ease;
        animation: fadeInUp 0.5s ease-out;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .test-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    }
    
    .test-name {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1a237e;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .test-description {
        background: #f5f5f5;
        padding: 18px;
        border-radius: 15px;
        margin: 15px 0;
        border-right: 4px solid #5c6bc0;
        line-height: 1.8;
        font-size: 1.05rem;
    }
    
    .normal-range-container {
        background: linear-gradient(135deg, #e8eaf6, #c5cae9);
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
    }
    
    .normal-range-title {
        font-weight: bold;
        color: #1a237e;
        font-size: 1.2rem;
        margin-bottom: 12px;
    }
    
    .range-item {
        background: white;
        padding: 12px 18px;
        border-radius: 10px;
        margin: 8px 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        transition: all 0.2s ease;
    }
    
    .range-item:hover {
        background: #e8eaf6;
        transform: translateX(-5px);
    }
    
    .range-label {
        font-weight: bold;
        color: #333;
    }
    
    .range-value {
        background: #1a237e;
        color: white !important;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.95rem;
    }
    
    .range-value-female {
        background: #e91e63;
        color: white !important;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.95rem;
    }
    
    .note-box {
        background: #fff3e0;
        border-right: 5px solid #ff9800;
        border-radius: 12px;
        padding: 15px;
        margin-top: 15px;
        font-size: 0.95rem;
        line-height: 1.8;
    }
    
    .warning-box {
        background: #ffebee;
        border-right: 5px solid #f44336;
        border-radius: 15px;
        padding: 20px;
        margin: 25px 0;
        text-align: center;
    }
    
    .icon-circle {
        width: 50px;
        height: 50px;
        background: linear-gradient(135deg, #3949ab, #5c6bc0);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        color: white;
    }
    
    .stButton button {
        background: linear-gradient(135deg, #1a237e, #3949ab) !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
        border-radius: 15px !important;
        padding: 12px 30px !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 5px 15px rgba(26,35,126,0.3) !important;
    }
    
    .stButton button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(26,35,126,0.5) !important;
    }
    
    .summary-card {
        background: white;
        border-radius: 20px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .summary-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 35px rgba(0,0,0,0.15);
    }
    
    .test-icon {
        font-size: 3rem;
        margin-bottom: 10px;
    }
    
    [dir="rtl"] {
        text-align: right !important;
        direction: rtl !important;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #3949ab;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #1a237e;
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
<div class="header-card">
    <h1 style="font-size:2.5rem; margin-bottom:15px;">🔬 ڕێبەری پشکنینە تاقیگەییەکان</h1>
    <p style="font-size:1.3rem; opacity:0.95;">گرنگترین و باوترین پشکنینە تاقیگەییەکان لەگەڵ ڕێژە ئاساییەکانیان</p>
</div>
""", unsafe_allow_html=True)

# --- WARNING ---
st.markdown("""
<div class="warning-box">
    <h3 style="color:#c62828; margin-bottom:10px;">⚠️ تێبینییەکی گرنگ</h3>
    <p style="color:#333; font-size:1.05rem;">
        ئەم ڕێژە ئاساییانە (Normal Ranges) لەوانەیە بەپێی ئەو ئامێر و تاقیگەیەی پشکنینەکەی تێدا دەکرێت 
        کەمێک گۆڕانکارییان تێدا هەبێت. هەمیشە باشترین کار ئەوەیە <b>پزیشکی تایبەت</b> ئەنجامەکانت بۆ بخوێنێتەوە.
    </p>
</div>
""", unsafe_allow_html=True)

# --- NAVIGATION ---
selected = option_menu(
    menu_title=None,
    options=[
        "هەموو پشکنینەکان",
        "پشکنینی خوێن (CBC)",
        "شەکری خوێن (FBS)",
        "چەورییەکانی خوێن (Lipid)",
        "فەرمانی گورچیلە (KFT)",
        "فەرمانی جگەر (LFT)",
        "هۆرمۆنی دەرەقی (TSH)",
        "ڤیتامین دی (D3)",
        "کۆگای ئاسن (Ferritin)"
    ],
    icons=['list', 'droplet', 'sugar', 'heart', 'kidney', 'liver', 'thyroid', 'sun', 'iron'],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "10px!important", "background-color": "transparent", "max-width": "1200px", "margin": "0 auto"},
        "icon": {"color": "#3949ab", "font-size": "16px"},
        "nav-link": {
            "font-size": "13px", "text-align": "center", "padding": "10px 15px",
            "border-radius": "30px", "margin": "0px 3px", "font-weight": "500",
            "background-color": "white", "box-shadow": "0 2px 8px rgba(0,0,0,0.05)"
        },
        "nav-link:hover": {"background-color": "#e8eaf6", "transform": "translateY(-2px)"},
        "nav-link-selected": {
            "background-color": "#1a237e", "color": "white", "font-weight": "bold",
            "box-shadow": "0 5px 15px rgba(26,35,126,0.3)"
        },
    }
)

# --- ALL TESTS DATA ---
all_tests = [
    {
        "id": "cbc",
        "name": "١. پشکنینی تەواوی خوێن (CBC - Complete Blood Count)",
        "icon": "🩸",
        "description": "یەکێکە لە باوترین پشکنینەکان کە پێوانەی پێکهاتەکانی خوێن دەکات، وەک خڕۆکە سوورەکان، خڕۆکە سپییەکان و پەڕەکانی خوێن. یارمەتیدەرە بۆ دەستنیشانکردنی کەمخوێنی (ئەنیمیا)، هەوکردن، و کێشەکانی مەینبوونی خوێن.",
        "ranges": [
            {"label": "هیمۆگڵۆبین (Hemoglobin) - پیاوان", "value": "13.5 - 17.5 g/dL", "type": "male"},
            {"label": "هیمۆگڵۆبین (Hemoglobin) - ژنان", "value": "12.0 - 15.5 g/dL", "type": "female"},
            {"label": "خڕۆکە سپییەکان (WBC)", "value": "4,500 - 11,000 /µL", "type": "normal"},
            {"label": "پەڕەکانی خوێن (Platelets)", "value": "150,000 - 450,000 /µL", "type": "normal"},
        ]
    },
    {
        "id": "fbs",
        "name": "٢. شەکری ناو خوێن لە کاتی برسێتیدا (FBS - Fasting Blood Sugar)",
        "icon": "🍬",
        "description": "ئەم پشکنینە بڕی گلوکۆز (شەکر) لە خوێندا دەپێوێت. دەبێت کەسەکە ٨ بۆ ١٢ کاتژمێر پێش پشکنینەکە هیچ شتێکی نەخواردبێت. بەکاردێت بۆ دەستنیشانکردنی نەخۆشی شەکرە یان قۆناغی پێش شەکرە.",
        "ranges": [
            {"label": "ڕێژەی ئاسایی", "value": "70 - 99 mg/dL", "type": "normal"},
        ],
        "note": "ئەگەر لە ١٠٠ تا ١٢٥ بێت، ئەوا قۆناغی پێش شەکرەیە، وە ئەگەر ١٢٦ یان زیاتر بێت، نیشانەی نەخۆشی شەکرەیە."
    },
    {
        "id": "lipid",
        "name": "٣. چەورییەکانی خوێن (Lipid Profile)",
        "icon": "❤️",
        "description": "کۆمەڵە پشکنینێکە بۆ پێوانەکردنی جۆرە جیاوازەکانی چەوری لە خوێندا. گرنگە بۆ هەڵسەنگاندنی مەترسییەکانی تووشبوون بە نەخۆشییەکانی دڵ و جەڵتە.",
        "ranges": [
            {"label": "کۆلیسترۆڵی گشتی (Total Cholesterol)", "value": "کەمتر لە 200 mg/dL", "type": "normal"},
            {"label": "چەوری سیانی (Triglycerides)", "value": "کەمتر لە 150 mg/dL", "type": "normal"},
            {"label": "چەورییە سوودبەخشەکان (HDL)", "value": "زیاتر لە 40 mg/dL", "type": "normal"},
            {"label": "چەورییە زیانبەخشەکان (LDL)", "value": "کەمتر لە 100 mg/dL", "type": "normal"},
        ]
    },
    {
        "id": "kft",
        "name": "٤. پشکنینی فەرمانی گورچیلە (KFT - Kidney Function Tests)",
        "icon": "🫘",
        "description": "پێوانەی توانای گورچیلەکان دەکات بۆ فلتەرکردن و پاککردنەوەی خوێن لە پاشماوەکان. سەرەکیترین دوو پشکنین بریتین لە یوریا و کریاتینین.",
        "ranges": [
            {"label": "کریاتینین (Creatinine) - پیاوان", "value": "0.7 - 1.3 mg/dL", "type": "male"},
            {"label": "کریاتینین (Creatinine) - ژنان", "value": "0.6 - 1.1 mg/dL", "type": "female"},
            {"label": "یوریا (Blood Urea)", "value": "15 - 40 mg/dL", "type": "normal"},
        ]
    },
    {
        "id": "lft",
        "name": "٥. پشکنینی فەرمانی جگەر (LFT - Liver Function Tests)",
        "icon": "🫁",
        "description": "ئەم پشکنینانە بڕی ئەو ئەنزیم و پرۆتینانە دەپێون کە جگەر دەریاندەدات. بەرزبوونەوەی ڕێژەکانیان نیشانەیە بۆ هەوکردن یان تێکچوونی خانەکانی جگەر.",
        "ranges": [
            {"label": "ALT (SGPT)", "value": "7 - 56 U/L", "type": "normal"},
            {"label": "AST (SGOT)", "value": "10 - 40 U/L", "type": "normal"},
        ]
    },
    {
        "id": "tsh",
        "name": "٦. هۆرمۆنی ڕژێنی دەرەقی (TSH - Thyroid Stimulating Hormone)",
        "icon": "🦋",
        "description": "هۆرمۆنێکە لە مێشکەوە دەردەدرێت بۆ کۆنترۆڵکردنی ڕژێنی دەرەقی (غودەی دەرەقی). ئەم پشکنینە دیاری دەکات ئایا غودەکە تەمەڵە (گەر TSH بەرز بێت) یان زۆر چالاکە (گەر TSH نزم بێت).",
        "ranges": [
            {"label": "ڕێژەی ئاسایی TSH", "value": "0.4 - 4.0 mIU/L", "type": "normal"},
        ]
    },
    {
        "id": "vitd",
        "name": "٧. ڤیتامین دی (Vitamin D3)",
        "icon": "☀️",
        "description": "پێوانەی بڕی ڤیتامین دی دەکات کە زۆر گرنگە بۆ تەندروستی ئێسک، هەڵمژینی کالیسیۆم، و بەهێزکردنی کۆئەندامی بەرگری.",
        "ranges": [
            {"label": "ڕێژەی ئاسایی", "value": "30 - 100 ng/mL", "type": "normal"},
        ],
        "note": "ئەگەر لە ٢٠ ng/mL کەمتر بێت، ئەوا کەسی تووشبوو کەمی ڤیتامین دی هەیە."
    },
    {
        "id": "ferritin",
        "name": "٨. کۆگای ئاسن (Ferritin)",
        "icon": "🧲",
        "description": "فێریتین پڕۆتینێکە کە ئاسن لە خانەکاندا هەڵدەگرێت. ئەم پشکنینە بڕی ئەو ئاسنە خەزنکراوەی لەش دەپێوێت کە هۆکاری سەرەکییە بۆ دروستبوونی خڕۆکە سوورەکان و قژ و نینۆکێکی تەندروست.",
        "ranges": [
            {"label": "پیاوان", "value": "24 - 336 ng/mL", "type": "male"},
            {"label": "ژنان", "value": "11 - 307 ng/mL", "type": "female"},
        ],
        "note": "لەکاتی سووڕی مانگانەدا ڕەنگە ڕێژەکە بەرەو کەمتر دابەزێت."
    }
]

# --- DISPLAY TESTS ---
if selected == "هەموو پشکنینەکان":
    # Summary cards
    st.markdown("<h2 style='text-align:center; color:#1a237e; margin:30px 0;'>📋 هەموو پشکنینە تاقیگەییەکان</h2>", unsafe_allow_html=True)
    
    cols = st.columns(4)
    for i, test in enumerate(all_tests):
        with cols[i % 4]:
            st.markdown(f"""
            <div class="summary-card" style="animation-delay:{i*0.1}s;">
                <div class="test-icon">{test['icon']}</div>
                <h4 style="color:#1a237e;">{test['name'][:50]}...</h4>
                <p style="color:#666; font-size:0.9rem;">{len(test['ranges'])} ڕێژەی ئاسایی</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<hr style='margin:30px 0;'>", unsafe_allow_html=True)
    
    # All tests detailed
    for i, test in enumerate(all_tests):
        st.markdown(f"""
        <div class="test-card" style="animation-delay:{i*0.15}s;">
            <div class="test-name">
                <div class="icon-circle">{test['icon']}</div>
                {test['name']}
            </div>
            <div class="test-description">
                📝 <b>وەسف:</b> {test['description']}
            </div>
            <div class="normal-range-container">
                <div class="normal-range-title">📊 ڕێژە ئاساییەکان:</div>
        """, unsafe_allow_html=True)
        
        for range_item in test['ranges']:
            value_class = "range-value-female" if range_item['type'] == "female" else "range-value"
            st.markdown(f"""
                <div class="range-item">
                    <span class="range-label">{range_item['label']}</span>
                    <span class="{value_class}">{range_item['value']}</span>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        if 'note' in test:
            st.markdown(f"""
            <div class="note-box">
                💡 <b>تێبینی:</b> {test['note']}
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

else:
    # Display single test
    test_map = {
        "پشکنینی خوێن (CBC)": "cbc",
        "شەکری خوێن (FBS)": "fbs",
        "چەورییەکانی خوێن (Lipid)": "lipid",
        "فەرمانی گورچیلە (KFT)": "kft",
        "فەرمانی جگەر (LFT)": "lft",
        "هۆرمۆنی دەرەقی (TSH)": "tsh",
        "ڤیتامین دی (D3)": "vitd",
        "کۆگای ئاسن (Ferritin)": "ferritin"
    }
    
    test_id = test_map.get(selected)
    if test_id:
        test = next((t for t in all_tests if t['id'] == test_id), None)
        if test:
            st.markdown(f"""
            <div class="test-card">
                <div class="test-name">
                    <div class="icon-circle">{test['icon']}</div>
                    {test['name']}
                </div>
                <div class="test-description">
                    📝 <b>وەسف:</b> {test['description']}
                </div>
                <div class="normal-range-container">
                    <div class="normal-range-title">📊 ڕێژە ئاساییەکان:</div>
            """, unsafe_allow_html=True)
            
            for range_item in test['ranges']:
                value_class = "range-value-female" if range_item['type'] == "female" else "range-value"
                st.markdown(f"""
                    <div class="range-item">
                        <span class="range-label">{range_item['label']}</span>
                        <span class="{value_class}">{range_item['value']}</span>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            if 'note' in test:
                st.markdown(f"""
                <div class="note-box">
                    💡 <b>تێبینی:</b> {test['note']}
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style="background:white;padding:25px;border-radius:15px;text-align:center;
            box-shadow:0 -5px 20px rgba(0,0,0,0.05);margin-top:30px;">
    <div class="warning-box" style="margin-bottom:15px;">
        <h3 style="color:#c62828;">⚠️ تێبینییەکی گرنگ</h3>
        <p style="color:#333;">
            ئەم ڕێژە ئاساییانە (Normal Ranges) لەوانەیە بەپێی ئەو ئامێر و تاقیگەیەی پشکنینەکەی تێدا دەکرێت 
            کەمێک گۆڕانکارییان تێدا هەبێت. هەمیشە باشترین کار ئەوەیە <b>پزیشکی تایبەت</b> ئەنجامەکانت بۆ بخوێنێتەوە.
        </p>
    </div>
    <p style="color:#666;">© ٢٠٢٤ ڕێبەری پشکنینە تاقیگەییەکان | هەموو زانیارییەکان تەنها بۆ مەبەستی ڕێنمایین</p>
    <p style="color:#999; font-size:0.85rem;">وەشانی 1.0</p>
</div>
""", unsafe_allow_html=True)
