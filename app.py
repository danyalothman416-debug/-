import streamlit as st
import json

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
    }
    
    .header-card * {
        color: white !important;
    }
    
    .test-card {
        background: white;
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 25px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.08);
        border-right: 6px solid #3949ab;
        transition: all 0.3s ease;
    }
    
    .test-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    }
    
    .test-name {
        font-size: 1.6rem;
        font-weight: bold;
        color: #1a237e;
        margin-bottom: 15px;
        border-bottom: 2px solid #e8eaf6;
        padding-bottom: 10px;
    }
    
    .test-description {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 12px;
        margin: 15px 0;
        border-right: 4px solid #5c6bc0;
        line-height: 1.9;
        font-size: 1.05rem;
    }
    
    .test-ranges {
        background: linear-gradient(135deg, #e8eaf6, #c5cae9);
        padding: 18px;
        border-radius: 12px;
        margin: 15px 0;
        font-weight: bold;
        color: #1a237e;
        line-height: 2;
        font-size: 1.05rem;
        word-wrap: break-word;
    }
    
    .category-title {
        font-size: 1.5rem;
        font-weight: bold;
        color: #1a237e;
        margin: 30px 0 15px 0;
        padding: 10px 20px;
        background: linear-gradient(135deg, #e8eaf6, #c5cae9);
        border-radius: 15px;
        display: inline-block;
    }
    
    .search-box {
        background: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.08);
        margin-bottom: 25px;
    }
    
    .warning-box {
        background: #ffebee;
        border-right: 5px solid #f44336;
        border-radius: 15px;
        padding: 20px;
        margin: 25px 0;
        text-align: center;
    }
    
    .stTextInput input {
        border: 2px solid #e0e0e0 !important;
        border-radius: 15px !important;
        padding: 15px 20px !important;
        font-size: 1.1rem !important;
    }
    
    .stTextInput input:focus {
        border-color: #3949ab !important;
        box-shadow: 0 0 0 3px rgba(57,73,171,0.1) !important;
    }
    
    .interpretation-section {
        background: linear-gradient(135deg, #f3e5f5, #e1bee7);
        border-radius: 15px;
        padding: 20px;
        margin-top: 20px;
        border: 2px dashed #7b1fa2;
    }
    
    .result-normal {
        background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
        border-right: 5px solid #4caf50;
        border-radius: 12px;
        padding: 18px;
        margin: 10px 0;
    }
    
    .result-abnormal {
        background: linear-gradient(135deg, #fff3e0, #ffe0b2);
        border-right: 5px solid #ff9800;
        border-radius: 12px;
        padding: 18px;
        margin: 10px 0;
    }
    
    .result-critical {
        background: linear-gradient(135deg, #ffebee, #ffcdd2);
        border-right: 5px solid #f44336;
        border-radius: 12px;
        padding: 18px;
        margin: 10px 0;
    }
    
    .stButton button {
        background: linear-gradient(135deg, #7b1fa2, #9c27b0) !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
        border-radius: 15px !important;
        padding: 12px 30px !important;
        font-size: 16px !important;
    }
    
    .stButton button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(123,31,162,0.5) !important;
    }
    
    .result-summary {
        background: white;
        border-radius: 15px;
        padding: 20px;
        margin-top: 15px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    [dir="rtl"] {
        text-align: right !important;
        direction: rtl !important;
    }
</style>
""", unsafe_allow_html=True)

# --- هەموو پشکنینەکان لە یەک DICTIONARY (JSON Format) ---
ALL_TESTS = {
    "پشکنینی تەواوی خوێن (CBC)": {
        "Name": "پشکنینی تەواوی خوێن (CBC - Complete Blood Count)",
        "Description": "یەکێکە لە باوترین پشکنینەکان کە پێوانەی پێکهاتەکانی خوێن دەکات، وەک خڕۆکە سوورەکان، خڕۆکە سپییەکان و پەڕەکانی خوێن. یارمەتیدەرە بۆ دەستنیشانکردنی کەمخوێنی (ئەنیمیا)، هەوکردن، و کێشەکانی مەینبوونی خوێن.",
        "Ranges": "هیمۆگڵۆبین (پیاوان): 13.5-17.5 g/dL | هیمۆگڵۆبین (ژنان): 12.0-15.5 g/dL | خڕۆکە سپییەکان (WBC): 4,500-11,000 /µL | پەڕەکانی خوێن (Platelets): 150,000-450,000 /µL",
        "Category": "پشکنینە بنەڕەتییەکان"
    },
    "شەکری ناو خوێن (FBS)": {
        "Name": "شەکری ناو خوێن لە کاتی برسێتیدا (FBS - Fasting Blood Sugar)",
        "Description": "ئەم پشکنینە بڕی گلوکۆز (شەکر) لە خوێندا دەپێوێت. دەبێت کەسەکە ٨ بۆ ١٢ کاتژمێر پێش پشکنینەکە هیچ شتێکی نەخواردبێت. بەکاردێت بۆ دەستنیشانکردنی نەخۆشی شەکرە یان قۆناغی پێش شەکرە. ١٠٠-١٢٥ = پێش شەکرە | ١٢٦+ = شەکرە.",
        "Ranges": "ڕێژەی ئاسایی: 70-99 mg/dL",
        "Category": "پشکنینە بنەڕەتییەکان"
    },
    "شەکری کەڵەکەبوو (HbA1c)": {
        "Name": "شەکری کەڵەکەبوو (HbA1c)",
        "Description": "ئەم پشکنینە تێکڕای ڕێژەی شەکری خوێنت نیشان دەدات لە ماوەی ٢ بۆ ٣ مانگی ڕابردوو. باشترین ڕێگەیە بۆ کۆنترۆڵکردنی شەکرە. 5.7%-6.4% = پێش شەکرە | 6.5%+ = شەکرە.",
        "Ranges": "ڕێژەی ئاسایی: کەمتر لە 5.7%",
        "Category": "پشکنینە بنەڕەتییەکان"
    },
    "چەورییەکانی خوێن (Lipid Profile)": {
        "Name": "چەورییەکانی خوێن (Lipid Profile)",
        "Description": "کۆمەڵە پشکنینێکە بۆ پێوانەکردنی جۆرە جیاوازەکانی چەوری لە خوێندا. گرنگە بۆ هەڵسەنگاندنی مەترسییەکانی تووشبوون بە نەخۆشییەکانی دڵ و جەڵتە.",
        "Ranges": "کۆلیسترۆڵی گشتی: کەمتر لە 200 mg/dL | چەوری سیانی (Triglycerides): کەمتر لە 150 mg/dL | HDL (چەوری سوودبەخش): زیاتر لە 40 mg/dL | LDL (چەوری زیانبەخش): کەمتر لە 100 mg/dL",
        "Category": "پشکنینە بنەڕەتییەکان"
    },
    "فەرمانی گورچیلە (KFT)": {
        "Name": "پشکنینی فەرمانی گورچیلە (KFT - Kidney Function Tests)",
        "Description": "پێوانەی توانای گورچیلەکان دەکات بۆ فلتەرکردن و پاککردنەوەی خوێن لە پاشماوەکان. سەرەکیترین دوو پشکنین بریتین لە کریاتینین و یوریا.",
        "Ranges": "کریاتینین (پیاوان): 0.7-1.3 mg/dL | کریاتینین (ژنان): 0.6-1.1 mg/dL | یوریا (Blood Urea): 15-40 mg/dL",
        "Category": "پشکنینە بنەڕەتییەکان"
    },
    "ئەلیکترۆلیتەکان (Electrolytes)": {
        "Name": "پشکنینی ئەلیکترۆلیتەکان (Electrolytes)",
        "Description": "ئەم پشکنینانە بۆ زانینی هاوسەنگی خوێ و کانزاکانە لە لەشدا کە بۆ کارکردنی ماسولکە و دەمارەکان گرنگن.",
        "Ranges": "سۆدیۆم (Sodium): 135-145 mEq/L | پۆتاسیۆم (Potassium): 3.6-5.2 mEq/L | کالیسیۆم (Calcium): 8.5-10.2 mg/dL",
        "Category": "پشکنینە بنەڕەتییەکان"
    },
    "فەرمانی جگەر (LFT)": {
        "Name": "پشکنینی فەرمانی جگەر (LFT - Liver Function Tests)",
        "Description": "ئەم پشکنینانە بڕی ئەو ئەنزیم و پرۆتینانە دەپێون کە جگەر دەریاندەدات. بەرزبوونەوەی ڕێژەکانیان نیشانەیە بۆ هەوکردن یان تێکچوونی خانەکانی جگەر.",
        "Ranges": "ALT (SGPT): 7-56 U/L | AST (SGOT): 10-40 U/L",
        "Category": "پشکنینە بنەڕەتییەکان"
    },
    "پرۆتینەکانی جگەر و گورچیلە": {
        "Name": "پشکنینی پرۆتینەکانی جگەر و گورچیلە (Albumin & Total Protein)",
        "Description": "ئەم پشکنینانە بۆ زانینی ڕێژەی پڕۆتین لە خوێندان. ئەگەر ئەلبومین کەم بێت نیشانەی کێشەی جگەر یان گورچیلەیە. پرۆتینی گشتی کۆی هەموو پڕۆتینەکانی خوێن دەپێوێت.",
        "Ranges": "ئەلبومین (Albumin): 3.4-5.4 g/dL | پرۆتینی گشتی (Total Protein): 6.0-8.3 g/dL",
        "Category": "پشکنینە بنەڕەتییەکان"
    },
    "هۆرمۆنی دەرەقی (TSH)": {
        "Name": "هۆرمۆنی ڕژێنی دەرەقی (TSH - Thyroid Stimulating Hormone)",
        "Description": "هۆرمۆنێکە لە مێشکەوە دەردەدرێت بۆ کۆنترۆڵکردنی ڕژێنی دەرەقی (غودەی دەرەقی). ئەم پشکنینە دیاری دەکات ئایا غودەکە تەمەڵە (گەر TSH بەرز بێت) یان زۆر چالاکە (گەر TSH نزم بێت).",
        "Ranges": "ڕێژەی ئاسایی TSH: 0.4-4.0 mIU/L",
        "Category": "پشکنینە بنەڕەتییەکان"
    },
    "پشکنینی پەنکریاس": {
        "Name": "پشکنینی پەنکریاس (Amylase & Lipase)",
        "Description": "ئەم ئەنزیمانە بۆ هەرسکردنی نیشاستە و چەوری بەکاردێن. بەرزبوونەوەیان نیشانەی هەوکردنی پەنکریاسە (Pancreatitis). لیپەیز وردترە لە ئامیلاز بۆ دەستنیشانکردنی کێشەکانی پەنکریاس.",
        "Ranges": "ئامیلاز (Amylase): 40-140 U/L | لیپەیز (Lipase): 0-160 U/L",
        "Category": "پشکنینە تایبەتەکان"
    },
    "پشکنینی ماسولکە و دڵ": {
        "Name": "پشکنینی ماسولکە و دڵ (LDH & CPK)",
        "Description": "ئەم ئەنزیمانە لە زۆربەی شانەکانی لەشدا هەیە. بەرزبوونەوەیان ئاماژەیە بۆ زیانگەیشتن بە شانەکانی دڵ، جگەر، گورچیلە یان ماسولکەکان. CPK بەتایبەت بۆ زانینی زیانی ماسولکە دوای وەرزشی قورس یان جەڵتەی دڵ بەکاردێت.",
        "Ranges": "LDH: 140-280 U/L | CPK: 10-120 U/L",
        "Category": "پشکنینە تایبەتەکان"
    },
    "ترۆپۆنین (Troponin)": {
        "Name": "پشکنینی ترۆپۆنین (Troponin)",
        "Description": "پشکنینێکی زۆر گرنگ و فریاگوزارییە بۆ زانینی بوونی جەڵتەی دڵ. کاتێک ماسولکەی دڵ زیانی پێدەگات، ئەم ماددەیە دەچێتە ناو خوێنەوە. دەبێت زۆر نزم بێت (نزیک بە سفر)، بەرزبوونەوەی کەمێکیش نیشانەی مەترسییە.",
        "Ranges": "ڕێژەی ئاسایی: نزیک بە سفر (کەمتر لە 0.04 ng/mL)",
        "Category": "پشکنینی فریاگوزاری"
    },
    "هەوکردن (CRP)": {
        "Name": "پشکنینی هەوکردن (CRP - C-Reactive Protein)",
        "Description": "ئەگەر ڕێژەکەی بەرزبێت، نیشانەیە بۆ بوونی هەوکردنێکی چالاک لە لەشدا (وەک هەوکردنی بەکتریا یان ڤایرۆس).",
        "Ranges": "ڕێژەی ئاسایی: کەمتر لە 10 mg/L",
        "Category": "پشکنینی هەوکردن"
    },
    "نیشتنەوەی خڕۆکە سوورەکان (ESR)": {
        "Name": "ڕێژەی نیشتنەوەی خڕۆکە سوورەکان (ESR)",
        "Description": "ڕێژەی نیشتنەوەی خڕۆکە سوورەکانە، بەکاردێت بۆ دەستنیشانکردنی هەوکردنی درێژخایەن یان جومگەکان. بەپێی تەمەن و ڕەگەز دەگۆڕێت.",
        "Ranges": "پیاوان: 0-22 mm/hr | ژنان: 0-29 mm/hr",
        "Category": "پشکنینی هەوکردن"
    },
    "ترشی یۆریک (Uric Acid)": {
        "Name": "پشکنینی ترشی یۆریک (Uric Acid)",
        "Description": "ماددەی یۆریک ئەسید پاشماوەی تێکشانی ماددە خۆراکییەکانە (پۆرین). بەرزبوونەوەی دەبێتە هۆی نەخۆشی ڕۆماتیزمی دەردە پاشا (Gout) و دروستبوونی بەردی گورچیلە.",
        "Ranges": "پیاوان: 3.4-7.0 mg/dL | ژنان: 2.4-6.0 mg/dL",
        "Category": "پشکنینە تایبەتەکان"
    },
    "کۆگای ئاسن (Ferritin)": {
        "Name": "کۆگای ئاسن (Ferritin)",
        "Description": "فێریتین پڕۆتینێکە کە ئاسن لە خانەکاندا هەڵدەگرێت. ئەم پشکنینە بڕی ئەو ئاسنە خەزنکراوەی لەش دەپێوێت کە هۆکاری سەرەکییە بۆ دروستبوونی خڕۆکە سوورەکان و قژ و نینۆکێکی تەندروست. لەکاتی سووڕی مانگانەدا ڕەنگە ڕێژەکە بەرەو کەمتر دابەزێت.",
        "Ranges": "پیاوان: 24-336 ng/mL | ژنان: 11-307 ng/mL",
        "Category": "پشکنینە تایبەتەکان"
    },
    "ئاسنی خوێن (Serum Iron)": {
        "Name": "پشکنینی ئاسنی خوێن (Serum Iron)",
        "Description": "ئاستی ڕاستەوخۆی ئاسن لە خوێندا دەپێوێت. ئاسن بۆ دروستبوونی خڕۆکە سوورەکان و گواستنەوەی ئۆکسجین لە لەشدا پێویستە.",
        "Ranges": "ڕێژەی ئاسایی: 60-170 mcg/dL",
        "Category": "پشکنینە تایبەتەکان"
    },
    "مەگنیسیۆم (Magnesium)": {
        "Name": "پشکنینی مەگنیسیۆم (Magnesium)",
        "Description": "مەگنیسیۆم بۆ کارکردنی دەمار و ماسولکەکان، تەندروستی دڵ، و بەهێزبوونی ئێسکەکان زۆر گرنگە. کەمی یان زیادبوونی دەبێتە هۆی کێشەی تەندروستی.",
        "Ranges": "ڕێژەی ئاسایی: 1.7-2.2 mg/dL",
        "Category": "پشکنینی ڤیتامین و کانزاکان"
    },
    "ڤیتامین دی (Vitamin D3)": {
        "Name": "ڤیتامین دی (Vitamin D3)",
        "Description": "پێوانەی بڕی ڤیتامین دی دەکات کە زۆر گرنگە بۆ تەندروستی ئێسک، هەڵمژینی کالیسیۆم، و بەهێزکردنی کۆئەندامی بەرگری. ئەگەر لە ٢٠ ng/mL کەمتر بێت، ئەوا کەسی تووشبوو کەمی ڤیتامین دی هەیە.",
        "Ranges": "ڕێژەی ئاسایی: 30-100 ng/mL",
        "Category": "پشکنینی ڤیتامین و کانزاکان"
    },
    "ڤیتامین B12": {
        "Name": "ڤیتامین B12",
        "Description": "زۆر گرنگە بۆ تەندروستی دەمارەکان و دروستکردنی خڕۆکە سوورەکان. کەمی ئەم ڤیتامینە دەبێتە هۆی لاوازی، بێهێزی، و کێشەی بیرەوەری.",
        "Ranges": "ڕێژەی ئاسایی: 200-900 pg/mL",
        "Category": "پشکنینی ڤیتامین و کانزاکان"
    },
    "هۆرمۆنەکانی زاوزێ": {
        "Name": "پشکنینی هۆرمۆنەکانی زاوزێ (Testosterone & Prolactin)",
        "Description": "ئەم هۆرمۆنانە بۆ تێگەیشتن لە نەزۆکی یان تێکچوونی هۆرمۆنی بەکاردێن. تێستۆستیرۆن هۆرمۆنی پیاوەیەتییە و پرۆلاکتین هۆرمۆنی شیرە کە بەرزبوونەوەی دەبێتە هۆی تێکچوونی سووڕی مانگانە یان کێشەی سێکسی.",
        "Ranges": "تێستۆستیرۆن (پیاوان): 300-1,000 ng/dL | پرۆلاکتین (پیاوان): 2-18 ng/mL | پرۆلاکتین (ژنان): 2-29 ng/mL",
        "Category": "پشکنینی هۆرمۆنەکان"
    }
}

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

# --- SEARCH ---
st.markdown('<div class="search-box">', unsafe_allow_html=True)
search_query = st.text_input(
    "🔍 گەڕان بەناو پشکنینەکاندا...",
    placeholder="ناوی پشکنین بنووسە بۆ گەڕان...",
    key="search_input"
)
st.markdown('</div>', unsafe_allow_html=True)

# --- FILTER & DISPLAY ---
if search_query:
    filtered_tests = {}
    for key, test in ALL_TESTS.items():
        search_text = f"{test['Name']} {test['Description']} {test['Ranges']} {test['Category']}"
        if search_query.lower() in search_text.lower():
            filtered_tests[key] = test
    
    if filtered_tests:
        st.success(f"🔍 {len(filtered_tests)} پشکنین دۆزرایەوە بۆ: '{search_query}'")
        tests_to_display = filtered_tests
    else:
        st.warning(f"😔 هیچ پشکنینێک نەدۆزرایەوە بۆ: '{search_query}'")
        tests_to_display = {}
else:
    tests_to_display = ALL_TESTS

# --- DISPLAY BY CATEGORY ---
if tests_to_display:
    categories = {}
    for key, test in tests_to_display.items():
        cat = test['Category']
        if cat not in categories:
            categories[cat] = {}
        categories[cat][key] = test
    
    for category, tests in categories.items():
        st.markdown(f"<div class='category-title'>📂 {category} ({len(tests)} پشکنین)</div>", unsafe_allow_html=True)
        
        for test_key, test in tests.items():
            st.markdown(f"""
            <div class="test-card">
                <div class="test-name">🔬 {test['Name']}</div>
                <div class="test-description">
                    📝 <b>وەسف:</b> {test['Description']}
                </div>
                <div class="test-ranges">
                    📊 <b>ڕێژە ئاساییەکان:</b> {test['Ranges']}
                </div>
            </div>
            """, unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(f"""
<div style="background:white;padding:25px;border-radius:15px;text-align:center;
            box-shadow:0 -5px 20px rgba(0,0,0,0.05);margin-top:30px;">
    <div class="warning-box" style="margin-bottom:15px;">
        <h3 style="color:#c62828;">⚠️ تێبینییەکی گرنگ</h3>
        <p style="color:#333;">
            ئەم سیستەمە تەنها بۆ ڕێنمایی سەرەتاییە و نابێت جێگەی سەردانی پزیشک بگرێتەوە.
        </p>
    </div>
    <p style="color:#666;">© ٢٠٢٤ ڕێبەری پشکنینە تاقیگەییەکان</p>
    <p style="color:#999; font-size:0.85rem;">کۆی گشتی: {len(ALL_TESTS)} پشکنین</p>
</div>
""", unsafe_allow_html=True)
