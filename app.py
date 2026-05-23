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
    
    .test-header {
        display: flex;
        align-items: center;
        gap: 15px;
        margin-bottom: 20px;
        padding-bottom: 15px;
        border-bottom: 2px solid #e8eaf6;
    }
    
    .test-icon-large {
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, #3949ab, #5c6bc0);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        color: white;
        flex-shrink: 0;
    }
    
    .test-title {
        font-size: 1.5rem;
        font-weight: bold;
        color: #1a237e;
        line-height: 1.4;
    }
    
    .test-description {
        background: #f8f9fa;
        padding: 18px;
        border-radius: 15px;
        margin: 15px 0;
        border-right: 4px solid #5c6bc0;
        line-height: 1.9;
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
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .range-item {
        background: white;
        padding: 14px 18px;
        border-radius: 12px;
        margin: 8px 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        transition: all 0.2s ease;
        gap: 15px;
    }
    
    .range-item:hover {
        background: #e8eaf6;
        transform: translateX(-5px);
    }
    
    .range-label {
        font-weight: bold;
        color: #333;
        flex: 1;
    }
    
    .range-value {
        background: #1a237e;
        color: white !important;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.95rem;
        white-space: nowrap;
    }
    
    .range-value-female {
        background: #e91e63;
        color: white !important;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.95rem;
        white-space: nowrap;
    }
    
    .range-value-warning {
        background: #ff6f00;
        color: white !important;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.95rem;
        white-space: nowrap;
    }
    
    .note-box {
        background: #fff3e0;
        border-right: 5px solid #ff9800;
        border-radius: 12px;
        padding: 15px 18px;
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
    
    .search-box {
        background: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.08);
        margin-bottom: 25px;
    }
    
    .category-title {
        font-size: 1.3rem;
        font-weight: bold;
        color: #1a237e;
        margin: 25px 0 15px 0;
        padding-bottom: 10px;
        border-bottom: 3px solid #3949ab;
        display: inline-block;
    }
    
    [dir="rtl"] {
        text-align: right !important;
        direction: rtl !important;
    }
    
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
    
    /* Search input styling */
    .stTextInput input {
        border: 2px solid #e0e0e0 !important;
        border-radius: 15px !important;
        padding: 15px 20px !important;
        font-size: 1.1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput input:focus {
        border-color: #3949ab !important;
        box-shadow: 0 0 0 3px rgba(57,73,171,0.1) !important;
    }
    
    .highlight {
        background-color: #ffeb3b;
        padding: 2px 5px;
        border-radius: 3px;
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

# --- ALL TESTS DATA ---
all_tests = [
    # === پشکنینە بنەڕەتییەکان ===
    {
        "id": "cbc",
        "name": "پشکنینی تەواوی خوێن (CBC - Complete Blood Count)",
        "icon": "🩸",
        "category": "پشکنینە بنەڕەتییەکان",
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
        "name": "شەکری ناو خوێن لە کاتی برسێتیدا (FBS - Fasting Blood Sugar)",
        "icon": "🍬",
        "category": "پشکنینە بنەڕەتییەکان",
        "description": "ئەم پشکنینە بڕی گلوکۆز (شەکر) لە خوێندا دەپێوێت. دەبێت کەسەکە ٨ بۆ ١٢ کاتژمێر پێش پشکنینەکە هیچ شتێکی نەخواردبێت. بەکاردێت بۆ دەستنیشانکردنی نەخۆشی شەکرە یان قۆناغی پێش شەکرە.",
        "ranges": [
            {"label": "ڕێژەی ئاسایی", "value": "70 - 99 mg/dL", "type": "normal"},
        ],
        "note": "ئەگەر لە ١٠٠ تا ١٢٥ بێت، ئەوا قۆناغی پێش شەکرەیە، وە ئەگەر ١٢٦ یان زیاتر بێت، نیشانەی نەخۆشی شەکرەیە."
    },
    {
        "id": "hba1c",
        "name": "شەکری کەڵەکەبوو (HbA1c)",
        "icon": "📊",
        "category": "پشکنینە بنەڕەتییەکان",
        "description": "ئەم پشکنینە تێکڕای ڕێژەی شەکری خوێنت نیشان دەدات لە ماوەی ٢ بۆ ٣ مانگی ڕابردوو. باشترین ڕێگەیە بۆ کۆنتڕۆڵکردنی شەکرە.",
        "ranges": [
            {"label": "ڕێژەی ئاسایی", "value": "کەمتر لە 5.7%", "type": "normal"},
        ],
        "note": "نێوان 5.7% بۆ 6.4% وەک پێش شەکرە دادەنرێت، 6.5% یان زیاتر بە نەخۆشی شەکرە دادەنرێت."
    },
    {
        "id": "lipid",
        "name": "چەورییەکانی خوێن (Lipid Profile)",
        "icon": "❤️",
        "category": "پشکنینە بنەڕەتییەکان",
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
        "name": "پشکنینی فەرمانی گورچیلە (KFT - Kidney Function Tests)",
        "icon": "🫘",
        "category": "پشکنینە بنەڕەتییەکان",
        "description": "پێوانەی توانای گورچیلەکان دەکات بۆ فلتەرکردن و پاککردنەوەی خوێن لە پاشماوەکان. سەرەکیترین دوو پشکنین بریتین لە یوریا و کریاتینین.",
        "ranges": [
            {"label": "کریاتینین (Creatinine) - پیاوان", "value": "0.7 - 1.3 mg/dL", "type": "male"},
            {"label": "کریاتینین (Creatinine) - ژنان", "value": "0.6 - 1.1 mg/dL", "type": "female"},
            {"label": "یوریا (Blood Urea)", "value": "15 - 40 mg/dL", "type": "normal"},
        ]
    },
    {
        "id": "electrolytes",
        "name": "پشکنینی ئەلیکترۆلیتەکان (Electrolytes)",
        "icon": "⚡",
        "category": "پشکنینە بنەڕەتییەکان",
        "description": "ئەم پشکنینانە بۆ زانینی هاوسەنگی خوێ و کانزاکانە لە لەشدا کە بۆ کارکردنی ماسولکە و دەمارەکان گرنگن.",
        "ranges": [
            {"label": "سۆدیۆم (Sodium)", "value": "135 - 145 mEq/L", "type": "normal"},
            {"label": "پۆتاسیۆم (Potassium)", "value": "3.6 - 5.2 mEq/L", "type": "normal"},
            {"label": "کالیسیۆم (Calcium)", "value": "8.5 - 10.2 mg/dL", "type": "normal"},
        ]
    },
    {
        "id": "lft",
        "name": "پشکنینی فەرمانی جگەر (LFT - Liver Function Tests)",
        "icon": "🫁",
        "category": "پشکنینە بنەڕەتییەکان",
        "description": "ئەم پشکنینانە بڕی ئەو ئەنزیم و پرۆتینانە دەپێون کە جگەر دەریاندەدات. بەرزبوونەوەی ڕێژەکانیان نیشانەیە بۆ هەوکردن یان تێکچوونی خانەکانی جگەر.",
        "ranges": [
            {"label": "ALT (SGPT)", "value": "7 - 56 U/L", "type": "normal"},
            {"label": "AST (SGOT)", "value": "10 - 40 U/L", "type": "normal"},
        ]
    },
    {
        "id": "tsh",
        "name": "هۆرمۆنی ڕژێنی دەرەقی (TSH)",
        "icon": "🦋",
        "category": "پشکنینە بنەڕەتییەکان",
        "description": "هۆرمۆنێکە لە مێشکەوە دەردەدرێت بۆ کۆنترۆڵکردنی ڕژێنی دەرەقی (غودەی دەرەقی). ئەم پشکنینە دیاری دەکات ئایا غودەکە تەمەڵە (گەر TSH بەرز بێت) یان زۆر چالاکە (گەر TSH نزم بێت).",
        "ranges": [
            {"label": "ڕێژەی ئاسایی TSH", "value": "0.4 - 4.0 mIU/L", "type": "normal"},
        ]
    },
    {
        "id": "vitd",
        "name": "ڤیتامین دی (Vitamin D3)",
        "icon": "☀️",
        "category": "پشکنینی ڤیتامینەکان",
        "description": "پێوانەی بڕی ڤیتامین دی دەکات کە زۆر گرنگە بۆ تەندروستی ئێسک، هەڵمژینی کالیسیۆم، و بەهێزکردنی کۆئەندامی بەرگری.",
        "ranges": [
            {"label": "ڕێژەی ئاسایی", "value": "30 - 100 ng/mL", "type": "normal"},
        ],
        "note": "ئەگەر لە ٢٠ ng/mL کەمتر بێت، ئەوا کەسی تووشبوو کەمی ڤیتامین دی هەیە."
    },
    {
        "id": "b12",
        "name": "ڤیتامین B12",
        "icon": "💊",
        "category": "پشکنینی ڤیتامینەکان",
        "description": "زۆر گرنگە بۆ تەندروستی دەمارەکان و دروستکردنی خڕۆکە سوورەکان. کەمی ئەم ڤیتامینە دەبێتە هۆی لاوازی، بێهێزی، و کێشەی بیرەوەری.",
        "ranges": [
            {"label": "ڕێژەی ئاسایی", "value": "200 - 900 pg/mL", "type": "normal"},
        ]
    },
    {
        "id": "ferritin",
        "name": "کۆگای ئاسن (Ferritin)",
        "icon": "🧲",
        "category": "پشکنینە تایبەتەکان",
        "description": "فێریتین پڕۆتینێکە کە ئاسن لە خانەکاندا هەڵدەگرێت. ئەم پشکنینە بڕی ئەو ئاسنە خەزنکراوەی لەش دەپێوێت کە هۆکاری سەرەکییە بۆ دروستبوونی خڕۆکە سوورەکان و قژ و نینۆکێکی تەندروست.",
        "ranges": [
            {"label": "پیاوان", "value": "24 - 336 ng/mL", "type": "male"},
            {"label": "ژنان", "value": "11 - 307 ng/mL", "type": "female"},
        ],
        "note": "لەکاتی سووڕی مانگانەدا ڕەنگە ڕێژەکە بەرەو کەمتر دابەزێت."
    },
    {
        "id": "uric_acid",
        "name": "پشکنینی ترشی یۆریک (Uric Acid)",
        "icon": "🦴",
        "category": "پشکنینە تایبەتەکان",
        "description": "ماددەی یۆریک ئەسید پاشماوەی تێکشانی ماددە خۆراکییەکانە (پۆرین). بەرزبوونەوەی دەبێتە هۆی نەخۆشی ڕۆماتیزمی دەردە پاشا (Gout) و دروستبوونی بەردی گورچیلە.",
        "ranges": [
            {"label": "پیاوان", "value": "3.4 - 7.0 mg/dL", "type": "male"},
            {"label": "ژنان", "value": "2.4 - 6.0 mg/dL", "type": "female"},
        ]
    },
    {
        "id": "crp",
        "name": "پشکنینی هەوکردن (CRP - C-Reactive Protein)",
        "icon": "🔥",
        "category": "پشکنینی هەوکردن",
        "description": "ئەگەر ڕێژەکەی بەرزبێت، نیشانەیە بۆ بوونی هەوکردنێکی چالاک لە لەشدا (وەک هەوکردنی بەکتریا یان ڤایرۆس).",
        "ranges": [
            {"label": "ڕێژەی ئاسایی", "value": "کەمتر لە 10 mg/L", "type": "normal"},
        ]
    },
    {
        "id": "esr",
        "name": "ڕێژەی نیشتنەوەی خڕۆکە سوورەکان (ESR)",
        "icon": "⏳",
        "category": "پشکنینی هەوکردن",
        "description": "ڕێژەی نیشتنەوەی خڕۆکە سوورەکانە، بەکاردێت بۆ دەستنیشانکردنی هەوکردنی درێژخایەن یان جومگەکان.",
        "ranges": [
            {"label": "پیاوان", "value": "0 - 22 mm/hr", "type": "male"},
            {"label": "ژنان", "value": "0 - 29 mm/hr", "type": "female"},
        ],
        "note": "بەپێی تەمەن و ڕەگەز دەگۆڕێت."
    },
    {
        "id": "troponin",
        "name": "پشکنینی ترۆپۆنین (Troponin)",
        "icon": "💔",
        "category": "پشکنینی فریاگوزاری",
        "description": "پشکنینێکی زۆر گرنگ و فریاگوزارییە بۆ زانینی بوونی جەڵتەی دڵ. کاتێک ماسولکەی دڵ زیانی پێدەگات، ئەم ماددەیە دەچێتە ناو خوێنەوە.",
        "ranges": [
            {"label": "ڕێژەی ئاسایی", "value": "نزیک بە سفر", "type": "warning"},
        ],
        "note": "دەبێت زۆر نزم بێت (نزیک بە سفر)، بەرزبوونەوەی کەمێکیش نیشانەی مەترسییە."
    },
]

# --- SEARCH FUNCTIONALITY ---
st.markdown('<div class="search-box">', unsafe_allow_html=True)
search_query = st.text_input(
    "🔍 گەڕان بەناو پشکنینەکاندا...",
    placeholder="ناوی پشکنین یان نیشانەکەت بنووسە...",
    key="search_input"
)
st.markdown('</div>', unsafe_allow_html=True)

# --- FILTER TESTS BASED ON SEARCH ---
if search_query:
    filtered_tests = []
    for test in all_tests:
        # گەڕان لە ناو، وەسف، و نیشانەکاندا
        search_text = f"{test['name']} {test['description']} {test['category']}"
        for range_item in test['ranges']:
            search_text += f" {range_item['label']}"
        if 'note' in test:
            search_text += f" {test['note']}"
        
        if search_query.lower() in search_text.lower():
            filtered_tests.append(test)
    
    if filtered_tests:
        st.success(f"🔍 {len(filtered_tests)} پشکنین دۆزرایەوە بۆ: '{search_query}'")
        tests_to_display = filtered_tests
    else:
        st.warning(f"😔 هیچ پشکنینێک نەدۆزرایەوە بۆ: '{search_query}'")
        st.info("💡 پێشنیار: وشەیەکی تر تاقی بکەرەوە یان ڕێنووسەکە بپشکنە")
        tests_to_display = []
else:
    tests_to_display = all_tests

# --- DISPLAY TESTS BY CATEGORY ---
if tests_to_display:
    # گروپکردنی پشکنینەکان بەپێی کاتێگۆری
    categories = {}
    for test in tests_to_display:
        cat = test['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(test)
    
    # پیشاندانی هەر کاتێگۆرییەک
    for category, tests in categories.items():
        st.markdown(f"<div class='category-title'>📂 {category}</div>", unsafe_allow_html=True)
        
        for i, test in enumerate(tests):
            # دیاریکردنی کلیل بۆ ئەنیمەیشن
            animation_delay = i * 0.1
            
            st.markdown(f"""
            <div class="test-card" style="animation-delay:{animation_delay}s;">
                <div class="test-header">
                    <div class="test-icon-large">{test['icon']}</div>
                    <div class="test-title">{test['name']}</div>
                </div>
                <div class="test-description">
                    📝 <b>وەسف:</b> {test['description']}
                </div>
                <div class="normal-range-container">
                    <div class="normal-range-title">📊 ڕێژە ئاساییەکان:</div>
            """, unsafe_allow_html=True)
            
            # پیشاندانی ڕێژە ئاساییەکان
            for range_item in test['ranges']:
                if range_item['type'] == "female":
                    value_class = "range-value-female"
                elif range_item['type'] == "warning":
                    value_class = "range-value-warning"
                else:
                    value_class = "range-value"
                
                st.markdown(f"""
                    <div class="range-item">
                        <span class="range-label">{range_item['label']}</span>
                        <span class="{value_class}">{range_item['value']}</span>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # پیشاندانی تێبینی ئەگەر هەبێت
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
    <p style="color:#999; font-size:0.85rem;">وەشانی 2.0 | {len(all_tests)} پشکنین</p>
</div>
""", unsafe_allow_html=True)
