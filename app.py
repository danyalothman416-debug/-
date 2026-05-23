import streamlit as st
from streamlit_option_menu import option_menu
import re

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
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
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
        flex-wrap: wrap;
    }
    
    .range-item:hover {
        background: #e8eaf6;
        transform: translateX(-5px);
    }
    
    .range-label {
        font-weight: bold;
        color: #333;
        flex: 1;
        min-width: 200px;
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
    
    /* شیکردنەوەی ئەنجام */
    .interpretation-section {
        background: linear-gradient(135deg, #f3e5f5, #e1bee7);
        border-radius: 15px;
        padding: 20px;
        margin-top: 20px;
        border: 2px dashed #7b1fa2;
    }
    
    .interpretation-title {
        font-size: 1.2rem;
        font-weight: bold;
        color: #4a148c;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .result-normal {
        background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
        border-right: 5px solid #4caf50;
        border-radius: 12px;
        padding: 18px;
        margin: 10px 0;
        animation: slideIn 0.5s ease-out;
    }
    
    .result-abnormal {
        background: linear-gradient(135deg, #fff3e0, #ffe0b2);
        border-right: 5px solid #ff9800;
        border-radius: 12px;
        padding: 18px;
        margin: 10px 0;
        animation: slideIn 0.5s ease-out;
    }
    
    .result-critical {
        background: linear-gradient(135deg, #ffebee, #ffcdd2);
        border-right: 5px solid #f44336;
        border-radius: 12px;
        padding: 18px;
        margin: 10px 0;
        animation: slideIn 0.5s ease-out;
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    .result-icon {
        font-size: 2rem;
        margin-left: 10px;
    }
    
    .result-text {
        font-size: 1.1rem;
        line-height: 1.8;
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
    
    .interpret-btn {
        background: linear-gradient(135deg, #7b1fa2, #9c27b0) !important;
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
    
    .result-summary {
        background: white;
        border-radius: 15px;
        padding: 20px;
        margin-top: 15px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .result-summary-normal {
        border: 3px solid #4caf50;
    }
    
    .result-summary-abnormal {
        border: 3px solid #ff9800;
    }
    
    .result-summary-critical {
        border: 3px solid #f44336;
    }
    
    [dir="rtl"] {
        text-align: right !important;
        direction: rtl !important;
    }
    
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 10px; }
    ::-webkit-scrollbar-thumb { background: #3949ab; border-radius: 10px; }
    ::-webkit-scrollbar-thumb:hover { background: #1a237e; }
    
    .stTextInput input, .stNumberInput input {
        border: 2px solid #e0e0e0 !important;
        border-radius: 15px !important;
        padding: 12px 20px !important;
        font-size: 1.1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #7b1fa2 !important;
        box-shadow: 0 0 0 3px rgba(123,31,162,0.1) !important;
    }
    
    .interpret-input-label {
        font-weight: bold;
        color: #4a148c;
        margin-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
<div class="header-card">
    <h1 style="font-size:2.5rem; margin-bottom:15px;">🔬 ڕێبەری پشکنینە تاقیگەییەکان</h1>
    <p style="font-size:1.3rem; opacity:0.95;">گرنگترین و باوترین پشکنینە تاقیگەییەکان | شیکردنەوەی ئەنجامەکانت</p>
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

# --- INTERPRETATION ENGINE (شیکەرەوەی ئەنجام) ---
def interpret_result(test_id, test_name, user_value, range_item_label):
    """
    شیکردنەوەی ئەنجامی بەکارهێنەر
    دەگەڕێتەوە: (status, message, color_class)
    """
    
    # هەموو مەودا ئاساییەکان بەپێی پشکنین
    normal_ranges = {
        "cbc": {
            "هیمۆگڵۆبین": {"male": (13.5, 17.5), "female": (12.0, 15.5), "unit": "g/dL"},
            "WBC": {"all": (4500, 11000), "unit": "/µL"},
            "Platelets": {"all": (150000, 450000), "unit": "/µL"}
        },
        "fbs": {
            "FBS": {"all": (70, 99), "unit": "mg/dL", "pre_diabetes": (100, 125), "diabetes": 126}
        },
        "hba1c": {
            "HbA1c": {"all": (0, 5.7), "unit": "%", "pre_diabetes": (5.7, 6.4), "diabetes": 6.5}
        },
        "lipid": {
            "Total Cholesterol": {"all": (0, 200), "unit": "mg/dL"},
            "Triglycerides": {"all": (0, 150), "unit": "mg/dL"},
            "HDL": {"all": (40, 999), "unit": "mg/dL"},
            "LDL": {"all": (0, 100), "unit": "mg/dL"}
        },
        "kft": {
            "Creatinine male": {"male": (0.7, 1.3), "unit": "mg/dL"},
            "Creatinine female": {"female": (0.6, 1.1), "unit": "mg/dL"},
            "Urea": {"all": (15, 40), "unit": "mg/dL"}
        },
        "electrolytes": {
            "Sodium": {"all": (135, 145), "unit": "mEq/L"},
            "Potassium": {"all": (3.6, 5.2), "unit": "mEq/L"},
            "Calcium": {"all": (8.5, 10.2), "unit": "mg/dL"}
        },
        "lft": {
            "ALT": {"all": (7, 56), "unit": "U/L"},
            "AST": {"all": (10, 40), "unit": "U/L"}
        },
        "tsh": {
            "TSH": {"all": (0.4, 4.0), "unit": "mIU/L"}
        },
        "vitd": {
            "Vitamin D": {"all": (30, 100), "unit": "ng/mL", "deficiency": 20}
        },
        "b12": {
            "B12": {"all": (200, 900), "unit": "pg/mL"}
        },
        "ferritin": {
            "Ferritin male": {"male": (24, 336), "unit": "ng/mL"},
            "Ferritin female": {"female": (11, 307), "unit": "ng/mL"}
        },
        "uric_acid": {
            "Uric Acid male": {"male": (3.4, 7.0), "unit": "mg/dL"},
            "Uric Acid female": {"female": (2.4, 6.0), "unit": "mg/dL"}
        },
        "crp": {
            "CRP": {"all": (0, 10), "unit": "mg/L"}
        },
        "esr": {
            "ESR male": {"male": (0, 22), "unit": "mm/hr"},
            "ESR female": {"female": (0, 29), "unit": "mm/hr"}
        },
        "troponin": {
            "Troponin": {"all": (0, 0.04), "unit": "ng/mL", "critical": 0.04}
        }
    }
    
    if test_id not in normal_ranges:
        return None, None, None
    
    # دۆزینەوەی مەودای ئاسایی
    range_data = None
    for key, value in normal_ranges[test_id].items():
        if range_item_label and key in range_item_label:
            range_data = value
            break
        elif not range_item_label:
            range_data = value
            break
    
    if not range_data:
        return None, None, None
    
    # دیاریکردنی مەودا
    if "male" in range_data and "female" not in range_data:
        min_val, max_val = range_data["male"]
    elif "female" in range_data and "male" not in range_data:
        min_val, max_val = range_data["female"]
    elif "all" in range_data:
        min_val, max_val = range_data["all"]
    else:
        return None, None, None
    
    # شیکردنەوەی ئەنجام
    if user_value >= min_val and user_value <= max_val:
        status = "normal"
        message = f"""
        ✅ ئەنجامەکەت لە ئاستی ئاساییدایە!
        <br><br>
        <b>ئەنجامی تۆ:</b> {user_value} {range_data.get('unit', '')}<br>
        <b>مەودای ئاسایی:</b> {min_val} - {max_val} {range_data.get('unit', '')}<br>
        <br>
        ئەنجامەکەت لە سنووری ئاساییدایە و پێویست بە نیگەرانی نییە. 
        بەڵام ئەگەر نیشانەکانت بەردەوام بوون، سەردانی پزیشک بکە.
        """
        color_class = "result-normal"
        
        # پشکنینی تایبەت بۆ HbA1c و FBS
        if test_id == "fbs" and "pre_diabetes" in range_data:
            if user_value >= range_data["pre_diabetes"][0] and user_value <= range_data["pre_diabetes"][1]:
                status = "abnormal"
                message = f"""
                ⚠️ ئەنجامەکەت لە قۆناغی پێش شەکرەدایە!
                <br><br>
                <b>ئەنجامی تۆ:</b> {user_value} mg/dL<br>
                <b>مەودای پێش شەکرە:</b> {range_data['pre_diabetes'][0]} - {range_data['pre_diabetes'][1]} mg/dL<br>
                <br>
                ڕێنمایی: پێویستە ڕێجیم و وەرزش ڕێک بخەیت و سەردانی پزیشکی شەکرە بکەیت.
                """
                color_class = "result-abnormal"
            elif user_value >= range_data.get("diabetes", 999):
                status = "critical"
                message = f"""
                🚨 ئەنجامەکەت نیشانەی نەخۆشی شەکرەیە!
                <br><br>
                <b>ئەنجامی تۆ:</b> {user_value} mg/dL<br>
                <b>ئاستی شەکرە:</b> 126 mg/dL یان زیاتر<br>
                <br>
                پێویستە بە زووترین کات سەردانی پزیشکی شەکرە بکەیت!
                """
                color_class = "result-critical"
        
        elif test_id == "hba1c" and "pre_diabetes" in range_data:
            if user_value >= range_data["pre_diabetes"][0] and user_value <= range_data["pre_diabetes"][1]:
                status = "abnormal"
                message = f"""
                ⚠️ ئەنجامەکەت لە قۆناغی پێش شەکرەدایە!
                <br><br>
                <b>ئەنجامی تۆ:</b> {user_value}%<br>
                <b>مەودای پێش شەکرە:</b> {range_data['pre_diabetes'][0]}% - {range_data['pre_diabetes'][1]}%<br>
                """
                color_class = "result-abnormal"
        
        return status, message, color_class
    
    elif user_value < min_val:
        status = "abnormal"
        message = f"""
        ⚠️ ئەنجامەکەت لە ئاستی ئاسایی کەمترە!
        <br><br>
        <b>ئەنجامی تۆ:</b> {user_value} {range_data.get('unit', '')}<br>
        <b>مەودای ئاسایی:</b> {min_val} - {max_val} {range_data.get('unit', '')}<br>
        <br>
        ئەنجامەکەت کەمترە لە سنووری ئاسایی. پێویستە سەردانی پزیشک بکەیت 
        بۆ دیاریکردنی هۆکار و چارەسەری گونجاو.
        """
        color_class = "result-abnormal"
        
        # پشکنینی تایبەت بۆ ڤیتامین دی
        if test_id == "vitd" and user_value < range_data.get("deficiency", 20):
            status = "critical"
            message = f"""
            🚨 کەمی ڤیتامین دی!
            <br><br>
            <b>ئەنجامی تۆ:</b> {user_value} ng/mL<br>
            <b>مەودای ئاسایی:</b> {min_val} - {max_val} ng/mL<br>
            <br>
            ئەنجامەکەت نیشانەی کەمی ڤیتامین دییە. پێویستە سەردانی پزیشک بکەیت 
            بۆ وەرگرتنی دەرمانی گونجاو.
            """
            color_class = "result-critical"
        
        return status, message, color_class
    
    else:  # user_value > max_val
        status = "abnormal"
        message = f"""
        ⚠️ ئەنجامەکەت لە ئاستی ئاسایی زیاترە!
        <br><br>
        <b>ئەنجامی تۆ:</b> {user_value} {range_data.get('unit', '')}<br>
        <b>مەودای ئاسایی:</b> {min_val} - {max_val} {range_data.get('unit', '')}<br>
        <br>
        ئەنجامەکەت زیاترە لە سنووری ئاسایی. پێویستە سەردانی پزیشک بکەیت 
        بۆ دیاریکردنی هۆکار و چارەسەری گونجاو.
        """
        color_class = "result-abnormal"
        
        # پشکنینی تایبەت بۆ ترۆپۆنین
        if test_id == "troponin" and user_value > range_data.get("critical", 0.04):
            status = "critical"
            message = f"""
            🚨 ئەنجامی مەترسیدار! (فریاکەوتن)
            <br><br>
            <b>ئەنجامی تۆ:</b> {user_value} ng/mL<br>
            <b>ئاستی ئاسایی:</b> نزیک بە سفر<br>
            <br>
            ئەم ئەنجامە نیشانەی زیانگەیشتن بە ماسولکەی دڵە!
            <b>یەکسەر پەیوەندی بە فریاکەوتن بکە (١٢٢)!</b>
            """
            color_class = "result-critical"
        
        return status, message, color_class

# --- ALL TESTS DATA (بە زیادکردنی ئایدی بۆ شیکردنەوە) ---
all_tests = [
    # === پشکنینە بنەڕەتییەکان ===
    {
        "id": "cbc",
        "name": "پشکنینی تەواوی خوێن (CBC - Complete Blood Count)",
        "icon": "🩸",
        "category": "پشکنینە بنەڕەتییەکان",
        "description": "یەکێکە لە باوترین پشکنینەکان کە پێوانەی پێکهاتەکانی خوێن دەکات، وەک خڕۆکە سوورەکان، خڕۆکە سپییەکان و پەڕەکانی خوێن. یارمەتیدەرە بۆ دەستنیشانکردنی کەمخوێنی (ئەنیمیا)، هەوکردن، و کێشەکانی مەینبوونی خوێن.",
        "ranges": [
            {"label": "هیمۆگڵۆبین (Hemoglobin) - پیاوان", "value": "13.5 - 17.5 g/dL", "type": "male", "range_id": "هیمۆگڵۆبین"},
            {"label": "هیمۆگڵۆبین (Hemoglobin) - ژنان", "value": "12.0 - 15.5 g/dL", "type": "female", "range_id": "هیمۆگڵۆبین"},
            {"label": "خڕۆکە سپییەکان (WBC)", "value": "4,500 - 11,000 /µL", "type": "normal", "range_id": "WBC"},
            {"label": "پەڕەکانی خوێن (Platelets)", "value": "150,000 - 450,000 /µL", "type": "normal", "range_id": "Platelets"},
        ]
    },
    {
        "id": "fbs",
        "name": "شەکری ناو خوێن لە کاتی برسێتیدا (FBS)",
        "icon": "🍬",
        "category": "پشکنینە بنەڕەتییەکان",
        "description": "ئەم پشکنینە بڕی گلوکۆز (شەکر) لە خوێندا دەپێوێت. دەبێت کەسەکە ٨ بۆ ١٢ کاتژمێر پێش پشکنینەکە هیچ شتێکی نەخواردبێت.",
        "ranges": [
            {"label": "ڕێژەی ئاسایی", "value": "70 - 99 mg/dL", "type": "normal", "range_id": "FBS"},
        ],
        "note": "١٠٠-١٢٥ = پێش شەکرە | ١٢٦+ = شەکرە"
    },
    {
        "id": "hba1c",
        "name": "شەکری کەڵەکەبوو (HbA1c)",
        "icon": "📊",
        "category": "پشکنینە بنەڕەتییەکان",
        "description": "ئەم پشکنینە تێکڕای ڕێژەی شەکری خوێنت نیشان دەدات لە ماوەی ٢ بۆ ٣ مانگی ڕابردوو.",
        "ranges": [
            {"label": "ڕێژەی ئاسایی", "value": "کەمتر لە 5.7%", "type": "normal", "range_id": "HbA1c"},
        ],
        "note": "5.7%-6.4% = پێش شەکرە | 6.5%+ = شەکرە"
    },
    {
        "id": "lipid",
        "name": "چەورییەکانی خوێن (Lipid Profile)",
        "icon": "❤️",
        "category": "پشکنینە بنەڕەتییەکان",
        "description": "کۆمەڵە پشکنینێکە بۆ پێوانەکردنی جۆرە جیاوازەکانی چەوری لە خوێندا. گرنگە بۆ هەڵسەنگاندنی مەترسییەکانی نەخۆشییەکانی دڵ.",
        "ranges": [
            {"label": "کۆلیسترۆڵی گشتی", "value": "کەمتر لە 200 mg/dL", "type": "normal", "range_id": "Total Cholesterol"},
            {"label": "چەوری سیانی (Triglycerides)", "value": "کەمتر لە 150 mg/dL", "type": "normal", "range_id": "Triglycerides"},
            {"label": "HDL (چەوری سوودبەخش)", "value": "زیاتر لە 40 mg/dL", "type": "normal", "range_id": "HDL"},
            {"label": "LDL (چەوری زیانبەخش)", "value": "کەمتر لە 100 mg/dL", "type": "normal", "range_id": "LDL"},
        ]
    },
    {
        "id": "kft",
        "name": "پشکنینی فەرمانی گورچیلە (KFT)",
        "icon": "🫘",
        "category": "پشکنینە بنەڕەتییەکان",
        "description": "پێوانەی توانای گورچیلەکان دەکات بۆ فلتەرکردنی خوێن. سەرەکیترین پشکنینەکان: کریاتینین و یوریا.",
        "ranges": [
            {"label": "کریاتینین - پیاوان", "value": "0.7 - 1.3 mg/dL", "type": "male", "range_id": "Creatinine male"},
            {"label": "کریاتینین - ژنان", "value": "0.6 - 1.1 mg/dL", "type": "female", "range_id": "Creatinine female"},
            {"label": "یوریا (Blood Urea)", "value": "15 - 40 mg/dL", "type": "normal", "range_id": "Urea"},
        ]
    },
    {
        "id": "electrolytes",
        "name": "پشکنینی ئەلیکترۆلیتەکان (Electrolytes)",
        "icon": "⚡",
        "category": "پشکنینە بنەڕەتییەکان",
        "description": "پێوانەی خوێ و کانزاکانی لەش: سۆدیۆم، پۆتاسیۆم، و کالیسیۆم کە بۆ کاری ماسولکە و دەمار گرنگن.",
        "ranges": [
            {"label": "سۆدیۆم (Sodium)", "value": "135 - 145 mEq/L", "type": "normal", "range_id": "Sodium"},
            {"label": "پۆتاسیۆم (Potassium)", "value": "3.6 - 5.2 mEq/L", "type": "normal", "range_id": "Potassium"},
            {"label": "کالیسیۆم (Calcium)", "value": "8.5 - 10.2 mg/dL", "type": "normal", "range_id": "Calcium"},
        ]
    },
    {
        "id": "lft",
        "name": "پشکنینی فەرمانی جگەر (LFT)",
        "icon": "🫁",
        "category": "پشکنینە بنەڕەتییەکان",
        "description": "پێوانەی ئەنزیمەکانی جگەر (ALT و AST) کە بەرزبوونەوەیان نیشانەی هەوکردن یان تێکچوونی جگەرە.",
        "ranges": [
            {"label": "ALT (SGPT)", "value": "7 - 56 U/L", "type": "normal", "range_id": "ALT"},
            {"label": "AST (SGOT)", "value": "10 - 40 U/L", "type": "normal", "range_id": "AST"},
        ]
    },
    {
        "id": "tsh",
        "name": "هۆرمۆنی ڕژێنی دەرەقی (TSH)",
        "icon": "🦋",
        "category": "پشکنینە بنەڕەتییەکان",
        "description": "پشکنینی کارکردنی غودەی دەرەقی. بەرزبوونەوە = تەمەڵی، نزمبوونەوە = زۆر چالاکی.",
        "ranges": [
            {"label": "ڕێژەی ئاسایی TSH", "value": "0.4 - 4.0 mIU/L", "type": "normal", "range_id": "TSH"},
        ]
    },
    {
        "id": "vitd",
        "name": "ڤیتامین دی (Vitamin D3)",
        "icon": "☀️",
        "category": "پشکنینی ڤیتامینەکان",
        "description": "پێوانەی ڤیتامین دی کە بۆ تەندروستی ئێسک و بەرگری لەش گرنگە.",
        "ranges": [
            {"label": "ڕێژەی ئاسایی", "value": "30 - 100 ng/mL", "type": "normal", "range_id": "Vitamin D"},
        ],
        "note": "کەمتر لە ٢٠ ng/mL = کەمی ڤیتامین دی"
    },
    {
        "id": "b12",
        "name": "ڤیتامین B12",
        "icon": "💊",
        "category": "پشکنینی ڤیتامینەکان",
        "description": "گرنگە بۆ تەندروستی دەمارەکان و دروستکردنی خڕۆکە سوورەکان.",
        "ranges": [
            {"label": "ڕێژەی ئاسایی", "value": "200 - 900 pg/mL", "type": "normal", "range_id": "B12"},
        ]
    },
    {
        "id": "ferritin",
        "name": "کۆگای ئاسن (Ferritin)",
        "icon": "🧲",
        "category": "پشکنینە تایبەتەکان",
        "description": "پێوانەی ئاسنی خەزنکراوی لەش کە بۆ دروستبوونی خڕۆکە سوورەکان پێویستە.",
        "ranges": [
            {"label": "پیاوان", "value": "24 - 336 ng/mL", "type": "male", "range_id": "Ferritin male"},
            {"label": "ژنان", "value": "11 - 307 ng/mL", "type": "female", "range_id": "Ferritin female"},
        ]
    },
    {
        "id": "uric_acid",
        "name": "پشکنینی ترشی یۆریک (Uric Acid)",
        "icon": "🦴",
        "category": "پشکنینە تایبەتەکان",
        "description": "بەرزبوونەوەی دەبێتە هۆی نەخۆشی ڕۆماتیزمی دەردە پاشا (Gout) و بەردی گورچیلە.",
        "ranges": [
            {"label": "پیاوان", "value": "3.4 - 7.0 mg/dL", "type": "male", "range_id": "Uric Acid male"},
            {"label": "ژنان", "value": "2.4 - 6.0 mg/dL", "type": "female", "range_id": "Uric Acid female"},
        ]
    },
    {
        "id": "crp",
        "name": "پشکنینی هەوکردن (CRP)",
        "icon": "🔥",
        "category": "پشکنینی هەوکردن",
        "description": "بەرزبوونەوەی نیشانەی هەوکردنی چالاکە (بەکتریا یان ڤایرۆس).",
        "ranges": [
            {"label": "ڕێژەی ئاسایی", "value": "کەمتر لە 10 mg/L", "type": "normal", "range_id": "CRP"},
        ]
    },
    {
        "id": "esr",
        "name": "ڕێژەی نیشتنەوەی خڕۆکە سوورەکان (ESR)",
        "icon": "⏳",
        "category": "پشکنینی هەوکردن",
        "description": "بۆ دەستنیشانکردنی هەوکردنی درێژخایەن یان نەخۆشی جومگەکان.",
        "ranges": [
            {"label": "پیاوان", "value": "0 - 22 mm/hr", "type": "male", "range_id": "ESR male"},
            {"label": "ژنان", "value": "0 - 29 mm/hr", "type": "female", "range_id": "ESR female"},
        ]
    },
    {
        "id": "troponin",
        "name": "پشکنینی ترۆپۆنین (Troponin)",
        "icon": "💔",
        "category": "پشکنینی فریاگوزاری",
        "description": "پشکنینی فریاگوزاری بۆ دەستنیشانکردنی جەڵتەی دڵ.",
        "ranges": [
            {"label": "ڕێژەی ئاسایی", "value": "نزیک بە سفر", "type": "warning", "range_id": "Troponin"},
        ],
        "note": "🚨 بەرزبوونەوەی کەمێکیش نیشانەی مەترسییە!"
    },
]

# --- SEARCH ---
st.markdown('<div class="search-box">', unsafe_allow_html=True)
search_query = st.text_input(
    "🔍 گەڕان بەناو پشکنینەکاندا...",
    placeholder="ناوی پشکنین بنووسە...",
    key="search_input"
)
st.markdown('</div>', unsafe_allow_html=True)

# --- FILTER TESTS ---
if search_query:
    filtered_tests = []
    for test in all_tests:
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
        st.warning(f"😔 هیچ پشکنینێک نەدۆزرایەوە")
        tests_to_display = []
else:
    tests_to_display = all_tests

# --- DISPLAY TESTS ---
if tests_to_display:
    categories = {}
    for test in tests_to_display:
        cat = test['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(test)
    
    for category, tests in categories.items():
        st.markdown(f"<div class='category-title'>📂 {category}</div>", unsafe_allow_html=True)
        
        for i, test in enumerate(tests):
            st.markdown(f"""
            <div class="test-card" style="animation-delay:{i*0.1}s;">
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
            
            if 'note' in test:
                st.markdown(f"""
                <div class="note-box">
                    💡 <b>تێبینی:</b> {test['note']}
                </div>
                """, unsafe_allow_html=True)
            
            # --- بەشی شیکردنەوەی ئەنجام ---
            st.markdown(f"""
            <div class="interpretation-section">
                <div class="interpretation-title">🧪 شیکردنەوەی ئەنجامی تۆ</div>
                <p style="color:#666; margin-bottom:15px;">
                    ئەنجامی پشکنینەکەت بنووسە بۆ ئەوەی بزانیت لە چ ئاستێکدایە
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # هەڵبژاردنی پێوەر
            range_options = [f"{r['label']} ({r['value']})" for r in test['ranges']]
            selected_range = st.selectbox(
                "پێوەر هەڵبژێرە:",
                range_options,
                key=f"range_select_{test['id']}_{i}"
            )
            
            # داخڵکردنی ئەنجام
            col1, col2 = st.columns([3, 1])
            with col1:
                user_value = st.number_input(
                    "ئەنجامی پشکنینەکەت:",
                    value=0.0,
                    step=0.1,
                    format="%.1f",
                    key=f"value_input_{test['id']}_{i}"
                )
            with col2:
                interpret_btn = st.button(
                    "🔍 شیکاری بکە",
                    key=f"interpret_btn_{test['id']}_{i}",
                    use_container_width=True
                )
            
            # شیکردنەوە
            if interpret_btn and user_value > 0:
                selected_label = selected_range.split(" (")[0] if " (" in selected_range else selected_range
                
                status, message, color_class = interpret_result(
                    test['id'], test['name'], user_value, selected_label
                )
                
                if message:
                    status_icons = {
                        "normal": "✅",
                        "abnormal": "⚠️",
                        "critical": "🚨"
                    }
                    status_titles = {
                        "normal": "ئەنجامی ئاسایی",
                        "abnormal": "ئەنجامی نائاسایی",
                        "critical": "ئەنجامی مەترسیدار"
                    }
                    
                    st.markdown(f"""
                    <div class="{color_class}">
                        <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">
                            <span style="font-size:2rem;">{status_icons.get(status, '📋')}</span>
                            <h4 style="margin:0;color:#333;">{status_titles.get(status, '')}</h4>
                        </div>
                        <div class="result-text">{message}</div>
                    </div>
                    
                    <div class="result-summary result-summary-{status}">
                        <p style="font-size:1.1rem;font-weight:bold;">
                            {status_icons.get(status, '')} 
                            {'ئەنجامەکەت لە ئاستی ئاساییدایە' if status == 'normal' else 'پێویستە سەردانی پزیشک بکەیت'}
                        </p>
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
            ئەم سیستەمە تەنها بۆ ڕێنمایی سەرەتاییە و نابێت جێگەی سەردانی پزیشک بگرێتەوە.
        </p>
    </div>
    <p style="color:#666;">© ٢٠٢٤ ڕێبەری پشکنینە تاقیگەییەکان | شیکردنەوەی ئەنجامەکان</p>
    <p style="color:#999; font-size:0.85rem;">وەشانی 3.0 | {len(all_tests)} پشکنین | بە توانای شیکردنەوە</p>
</div>
""", unsafe_allow_html=True)
