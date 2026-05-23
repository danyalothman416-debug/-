import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import uuid
import json
import plotly.express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
import random
import time

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="سیستەمی شیکاری نەخۆشییەکان - AI Diagnosis", 
    layout="wide", 
    initial_sidebar_state="collapsed",
    page_icon="🏥"
)

# --- 2. INITIALIZE SESSION STATES ---
def init_session_states():
    defaults = {
        'page': "home",
        'user_email': None,
        'user_role': "patient",
        'user_name': None,
        'user_phone': None,
        'user_id': None,
        'lang_choice': "کوردی 🇭🇺",
        'diagnosis_history': [],
        'current_diagnosis': None,
        'symptom_checker_data': {}
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_states()

# --- 3. DISEASE DATABASE (Knowledge Base) ---
DISEASE_DATABASE = {
    "هەڵامەت (سەرماخواردن)": {
        "symptoms": ["قورگ ئێشە", "کۆکە", "پژمین", "سەرئێشە", "ماندوێتی", "تا", "گیرانی لوت"],
        "severity": "سوک",
        "advice": "پشوو بدە، زۆر شلە بخۆرەوە، دەرمانی سەرماخواردن بەکاربهێنە. ئەگەر زیاتر لە ٧ ڕۆژ خایاند پەیوەندی بە پزیشک بکە.",
        "when_to_see_doctor": "تا بەرز لە ٣٨.٥ پلە زیاتر، کۆکەی خوێناوی، یان هەناسە تەنگی",
        "specialty": "پزیشکی گشتی",
        "color": "#00C851"
    },
    "ئەنفلۆنزا": {
        "symptoms": ["تا بەرز", "لەرزین", "ئێشی ماسولکەکان", "سەرئێشە", "کۆکەی وشک", "ماندوێتی زۆر", "قورگ ئێشە"],
        "severity": "مامناوەند",
        "advice": "پشووی تەواو، شلەی زۆر، دەرمانی دژە تا. لە ماوەی ٤٨ کاتژمێری یەکەمدا سەردانی پزیشک بکە.",
        "when_to_see_doctor": "هەرچەند زووە پەیوەندی بە پزیشکەوە بکە، بەتایبەت ئەگەر تەمەنت لە ٦٥ ساڵ زیاترە یان نەخۆشی درێژخایەنت هەیە",
        "specialty": "پزیشکی گشتی",
        "color": "#FFA500"
    },
    "کۆڤید-١٩": {
        "symptoms": ["تا", "کۆکەی وشک", "ماندوێتی", "لەدەستدانی بۆن", "لەدەستدانی تام", "هەناسە تەنگی", "ئێشی ماسولکەکان", "قورگ ئێشە"],
        "severity": "مامناوەند تا مەترسیدار",
        "advice": "خۆت جیا بکەرەوە، پشوو بدە، شلە زۆر بخۆرەوە. ئەگەر هەناسە تەنگی هەبوو یەکسەر پەیوەندی بە پزیشکەوە بکە.",
        "when_to_see_doctor": "هەناسە تەنگی، ئازاری سنگ، لەدەستدانی هۆش، ڕەنگی پێستی شین بوو",
        "specialty": "پزیشکی هەناوی",
        "color": "#FF8800"
    },
    "شەکرەی جۆری ٢": {
        "symptoms": ["تینوێتی زۆر", "میزکردنی زۆر", "برسێتی زۆر", "ماندوێتی", "بینینی تەمومژاوی", "برینی درەنگ چاکبوو", "دابەزینی کێش"],
        "severity": "درێژخایەن",
        "advice": "پشکنینی شەکری خوێن ئەنجام بدە. ڕێجیم و وەرزش ڕێک بخە. سەردانی پزیشکی شەکرە بکە.",
        "when_to_see_doctor": "ئاستی شەکری خوێن لە ٢٠٠ mg/dL زیاتر، یان نیشانەکانی ketoacidosis",
        "specialty": "پزیشکی شەکرە",
        "color": "#0077B6"
    },
    "پەستانی خوێنی بەرز": {
        "symptoms": ["سەرئێشە", "سەرگێژخواردن", "بینینی تەمومژاوی", "ئازاری سنگ", "هەناسە تەنگی", "خوێن لە لوت"],
        "severity": "درێژخایەن",
        "advice": "پێوانەکردنی پەستانی خوێن. کەمکردنەوەی خوێ. ڕێجیمی تەندروست. وەرزشی ڕێک.",
        "when_to_see_doctor": "پەستانی خوێن لە ١٨٠/١٢٠ زیاتر، ئازاری سنگی توند، هەناسە تەنگی لەناکاو",
        "specialty": "پزیشکی دڵ",
        "color": "#E91E63"
    },
    "هەوکردنی گەدە (Gastritis)": {
        "symptoms": ["ئازاری سک", "دڵ تێکەڵهاتن", "ڕشانەوە", "هەستکردن بە پڕی", "نەمانی ئارەزووی خواردن", "هەڵئاوسان"],
        "severity": "مامناوەند",
        "advice": "خواردنی سوک و بەش بەش. دوورکەوتنەوە لە خواردنی تیژ و چەور. دەرمانی دژە ترش.",
        "when_to_see_doctor": "ڕشانەوەی خوێناوی، پیسایی ڕەش، ئازاری توندی سک",
        "specialty": "پزیشکی هەرس",
        "color": "#9C27B0"
    },
    "هەوکردنی سینوسەکان (Sinusitis)": {
        "symptoms": ["سەرئێشە", "ئازاری ڕوخسار", "گیرانی لوت", "پژمین", "کۆکە", "تا", "دەردراوی لوت"],
        "severity": "سوک تا مامناوەند",
        "advice": "هەڵم لە دەموچاو بدە. شلەی زۆر بخۆرەوە. دەرمانی دژە کۆکە و هەستیاری.",
        "when_to_see_doctor": "تا بەرز، ئازاری توندی ڕوخسار، درێژەکێشانی زیاتر لە ١٠ ڕۆژ",
        "specialty": "پزیشکی گوێ و لوت و قورگ",
        "color": "#00BCD4"
    },
    "هەوکردنی میزەڕۆ (UTI)": {
        "symptoms": ["میزکردنی زۆر", "ئازار لە کاتی میزکردن", "ئازاری خوارەوەی سک", "میزی تەمومژاوی", "تا"],
        "severity": "مامناوەند",
        "advice": "زۆر ئاو بخۆرەوە. پشکنینی میز ئەنجام بدە. ئەنتی بایۆتیک بە ڕێنمایی پزیشک.",
        "when_to_see_doctor": "تا بەرز، ئازاری توند، خوێن لە میزدا",
        "specialty": "پزیشکی گورچیلە و میزەڕۆ",
        "color": "#FF5722"
    },
    "هەستیاری وەرزی (Allergy)": {
        "symptoms": ["پژمین", "کۆکە", "چاوی هەستیار", "گیرانی لوت", "خورانی چاو", "خورانی پێست"],
        "severity": "سوک",
        "advice": "دەرمانی دژە هەستیاری. دوورکەوتنەوە لە هۆکارەکانی هەستیاری.",
        "when_to_see_doctor": "هەناسە تەنگی، ئاوسانی ڕوخسار یان زمان",
        "specialty": "پزیشکی هەستیاری",
        "color": "#4CAF50"
    },
    "بێخەوی (Insomnia)": {
        "symptoms": ["نەتوانینی خەوتن", "هەڵسانەوەی زوو", "ماندوێتی ڕۆژ", "بێزاری", "کەمی تەرکیز"],
        "severity": "سوک تا مامناوەند",
        "advice": "کاتەکانی خەوتن ڕێک بخە. لە شەواندا کافایین مەخۆرەوە. وەرزش بکە بەڵام نە لە کاتی شەودا.",
        "when_to_see_doctor": "ئەگەر زیاتر لە ٣ مانگ درێژەی کێشا و کاریگەری لەسەر ژیانی ڕۆژانەت هەبوو",
        "specialty": "پزیشکی دەروونی",
        "color": "#607D8B"
    },
    "سکچوون (Diarrhea)": {
        "symptoms": ["سکچوونی زۆر", "ئازاری سک", "تینوێتی", "تا", "ڕشانەوە"],
        "severity": "سوک تا مامناوەند",
        "advice": "شلەی زۆر بخۆرەوە بۆ جێگرتنەوەی ئاو. خواردنی سوک بخۆ. ORS بەکاربهێنە.",
        "when_to_see_doctor": "سکچوونی خوێناوی، زیاتر لە ٣ ڕۆژ، نیشانەکانی وشکبوونەوە",
        "specialty": "پزیشکی هەرس",
        "color": "#795548"
    }
}

# --- 4. MULTI-LANGUAGE UI STRINGS ---
languages = {
    "کوردی 🇭🇺": {
        "dir": "rtl", "align": "right",
        "title": "سیستەمی شیکاری نەخۆشییەکان 🏥",
        "desc": "نیشانەکانت داخڵ بکە و پێشبینی نەخۆشییەکەت وەربگرە بە هۆشمەندی دەستکرد",
        "nav_home": "سەرەکی", "nav_diagnosis": "شیکاری نوێ", 
        "nav_history": "مێژووی شیکاری", "nav_info": "زانیاری پزیشکی",
        "nav_emergency": "فریاکەوتن", "nav_about": "دەربارە",
        
        "select_symptoms": "نیشانەکانت هەڵبژێرە",
        "start_diagnosis": "دەستپێکردنی شیکاری",
        "diagnosis_result": "ئەنجامی شیکاری",
        "possible_diseases": "نەخۆشییە ئەگەرییەکان",
        "probability": "ڕێژەی ئەگەر",
        "advice": "ڕێنمایی",
        "when_to_see_doctor": "کەی سەردانی پزیشک بکەیت",
        "specialty": "پزیشکی پسپۆڕ",
        "severity": "ئاستی مەترسی",
        
        "age": "تەمەن",
        "gender": "ڕەگەز",
        "male": "نێر",
        "female": "مێ",
        "duration": "ماوەی نیشانەکان",
        "days_1_3": "١-٣ ڕۆژ",
        "days_4_7": "٤-٧ ڕۆژ",
        "weeks_1_2": "١-٢ هەفتە",
        "more_than_2_weeks": "زیاتر لە ٢ هەفتە",
        
        "emergency_title": "🚨 حاڵەتی فریاکەوتن",
        "emergency_warning": "ئەگەر ئەم نیشانانەت هەیە یەکسەر پەیوەندی بە فریاکەوتن بکە:",
        "emergency_symptoms": "ئازاری توندی سنگ, هەناسە تەنگی لەناکاو, لەدەستدانی هۆش, ڕشانەوەی خوێناوی, خوێنبەربوونی توند, ئیفلیجی",
        
        "disclaimer": "⚠️ ئاگاداری: ئەم سیستەمە تەنها بۆ ڕێنماییە و جێگەی سەردانی پزیشک ناگرێتەوە",
        "history_title": "مێژووی شیکارییەکانت",
        "no_history": "هێشتا هیچ شیکارییەکت ئەنجام نەداوە",
        
        "all_symptoms": "هەموو نیشانە بەردەستەکان",
        "selected_symptoms": "نیشانە هەڵبژێردراوەکان",
        "clear_all": "سڕینەوەی هەموو",
        "add_symptom": "زیادکردنی نیشانە",
        
        "how_it_works": "چۆن کاردەکات؟",
        "step1": "نیشانەکانت هەڵبژێرە",
        "step2": "زانیاری کەسی داخڵ بکە",
        "step3": "ئەنجامی شیکاری وەربگرە",
        "step4": "ڕێنمایی پزیشکی ببینە"
    }
}

# --- 5. DATA FILES ---
DIAGNOSIS_HISTORY_FILE = "diagnosis_history.csv"

def load_diagnosis_history():
    if os.path.exists(DIAGNOSIS_HISTORY_FILE):
        return pd.read_csv(DIAGNOSIS_HISTORY_FILE)
    return pd.DataFrame(columns=["diagnosis_id", "date", "age", "gender", "duration", 
                                  "symptoms", "diagnosis", "probability", "severity"])

def save_diagnosis_history(df):
    df.to_csv(DIAGNOSIS_HISTORY_FILE, index=False)

# --- 6. DIAGNOSIS ENGINE ---
def analyze_symptoms(selected_symptoms, age, gender, duration):
    results = []
    
    for disease, data in DISEASE_DATABASE.items():
        disease_symptoms = data['symptoms']
        matching_symptoms = set(selected_symptoms) & set(disease_symptoms)
        total_disease_symptoms = len(disease_symptoms)
        
        if matching_symptoms:
            base_probability = (len(matching_symptoms) / total_disease_symptoms) * 100
            
            if age > 60 and disease in ["پەستانی خوێنی بەرز", "شەکرەی جۆری ٢"]:
                base_probability += 15
            elif age < 12 and disease in ["هەڵامەت (سەرماخواردن)", "ئەنفلۆنزا"]:
                base_probability += 10
                
            if duration in ["more_than_2_weeks", "weeks_1_2"] and data['severity'] == "درێژخایەن":
                base_probability += 10
            elif duration == "days_1_3" and data['severity'] == "سوک":
                base_probability += 5
                
            probability = min(base_probability, 95)
            
            if probability > 20:
                results.append({
                    "disease": disease,
                    "probability": round(probability, 1),
                    "matching_symptoms": len(matching_symptoms),
                    "total_symptoms": total_disease_symptoms,
                    "severity": data['severity'],
                    "advice": data['advice'],
                    "when_to_see_doctor": data['when_to_see_doctor'],
                    "specialty": data['specialty'],
                    "color": data['color']
                })
    
    results.sort(key=lambda x: x['probability'], reverse=True)
    return results[:5]

# --- 7. EMERGENCY CHECKER ---
EMERGENCY_SYMPTOMS = [
    "ئازاری توندی سنگ", "هەناسە تەنگی لەناکاو", "لەدەستدانی هۆش", 
    "ڕشانەوەی خوێناوی", "خوێنبەربوونی توند", "ئیفلیجی", 
    "قسەکردنی ناڕوون", "ئازاری توندی سەر", "بینینی دووانە"
]

def check_emergency(selected_symptoms):
    emergency_found = set(selected_symptoms) & set(EMERGENCY_SYMPTOMS)
    return list(emergency_found)

# --- 8. CSS STYLING ---
L = languages[st.session_state.lang_choice]

accent = "#0077B6"
accent_light = "#00B4D8"
main_bg = "#F0F8FF"
card_bg = "#FFFFFF"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Naskh+Arabic:wght@400;700&display=swap');
    
    * {{
        font-family: 'Noto Naskh Arabic', 'Segoe UI', sans-serif;
    }}
    
    [data-testid="stSidebar"] {{ display: none; }}
    
    html, body, [data-testid="stAppViewContainer"] {{ 
        background: linear-gradient(135deg, #F0F8FF 0%, #E8F4F8 50%, #F0F8FF 100%) !important; 
    }}
    
    .medical-card {{ 
        background: linear-gradient(135deg, #0077B6 0%, #00B4D8 100%); 
        border-radius: 25px; 
        padding: 35px; 
        color: white !important; 
        margin-bottom: 25px; 
        box-shadow: 0 10px 30px rgba(0,119,182,0.3);
        position: relative;
        overflow: hidden;
    }}
    
    .medical-card::before {{
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 60%);
        animation: rotate 20s linear infinite;
    }}
    
    @keyframes rotate {{
        from {{ transform: rotate(0deg); }}
        to {{ transform: rotate(360deg); }}
    }}
    
    .medical-card * {{ color: white !important; position: relative; z-index: 1; }}
    
    .glass-card {{ 
        background: rgba(255, 255, 255, 0.9); 
        backdrop-filter: blur(10px);
        border-radius: 20px; 
        padding: 25px; 
        border: 1px solid rgba(0,119,182,0.2); 
        margin-bottom: 20px; 
        box-shadow: 0 8px 25px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }}
    
    .glass-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 12px 35px rgba(0,0,0,0.12);
    }}
    
    .diagnosis-card {{
        background: white;
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.08);
        border-right: 6px solid #0077B6;
        animation: slideIn 0.5s ease-out;
        transition: all 0.3s ease;
    }}
    
    .diagnosis-card:hover {{
        transform: translateX(-5px);
        box-shadow: 0 12px 35px rgba(0,0,0,0.15);
    }}
    
    @keyframes slideIn {{
        from {{
            opacity: 0;
            transform: translateX(30px);
        }}
        to {{
            opacity: 1;
            transform: translateX(0);
        }}
    }}
    
    .stButton button {{ 
        background: linear-gradient(135deg, #0077B6 0%, #00B4D8 100%) !important; 
        color: white !important; 
        border: none !important; 
        font-weight: bold !important; 
        border-radius: 15px !important; 
        padding: 15px 30px !important; 
        font-size: 18px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 5px 15px rgba(0,119,182,0.3) !important;
    }}
    
    .stButton button:hover {{ 
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(0,119,182,0.4) !important;
    }}
    
    .emergency-btn {{ 
        background: linear-gradient(135deg, #FF4444 0%, #FF6B6B 100%) !important;
        animation: pulse 2s infinite !important;
    }}
    
    @keyframes pulse {{ 
        0% {{ box-shadow: 0 0 0 0 rgba(255,68,68,0.4); }} 
        50% {{ box-shadow: 0 0 0 20px rgba(255,68,68,0); }} 
        100% {{ box-shadow: 0 0 0 0 rgba(255,68,68,0); }} 
    }}
    
    .symptom-checkbox {{
        background: white;
        padding: 10px 15px;
        border-radius: 12px;
        margin: 5px 0;
        border: 2px solid #e0e0e0;
        transition: all 0.3s ease;
        cursor: pointer;
    }}
    
    .symptom-checkbox:hover {{
        border-color: #0077B6;
        background: #F0F8FF;
    }}
    
    .probability-bar-container {{
        background: linear-gradient(90deg, #f0f0f0, #e8e8e8);
        border-radius: 20px;
        padding: 4px;
        margin: 15px 0;
        box-shadow: inset 0 3px 6px rgba(0,0,0,0.1);
    }}
    
    .probability-bar {{
        height: 18px;
        border-radius: 16px;
        background: linear-gradient(90deg, #0077B6, #00B4D8);
        box-shadow: 0 3px 10px rgba(0,119,182,0.4);
        position: relative;
        transition: width 1.5s cubic-bezier(0.4, 0, 0.2, 1);
        display: flex;
        align-items: center;
        justify-content: flex-end;
        padding-right: 10px;
    }}
    
    .probability-text {{
        color: white;
        font-weight: bold;
        font-size: 0.85rem;
        text-shadow: 0 1px 3px rgba(0,0,0,0.3);
    }}
    
    .info-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 15px;
        margin-top: 15px;
    }}
    
    .info-item {{
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        padding: 15px;
        border-radius: 12px;
        border-right: 4px solid #0077B6;
    }}
    
    .metric-card {{
        background: white;
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }}
    
    .metric-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 12px 35px rgba(0,0,0,0.15);
    }}
    
    .metric-value {{
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(135deg, #0077B6, #00B4D8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    
    h2 {{ color: #0077B6 !important; font-weight: bold !important; }}
    h3 {{ color: #0077B6 !important; }}
    
    [dir="rtl"] {{ text-align: right !important; direction: rtl !important; }}
</style>
""", unsafe_allow_html=True)

# --- 9. NAVIGATION ---
selected = option_menu(
    menu_title=None,
    options=[L['nav_home'], L['nav_diagnosis'], L['nav_history'], 
             L['nav_info'], L['nav_emergency'], L['nav_about']],
    icons=['house-door', 'clipboard2-pulse', 'clock-history', 
           'info-circle', 'exclamation-triangle', 'people'],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "10px!important", "background-color": "transparent", "max-width": "1200px", "margin": "0 auto"},
        "icon": {"color": "#0077B6", "font-size": "18px"},
        "nav-link": {"font-size": "15px", "text-align": "center", "padding": "12px 20px", 
                     "border-radius": "30px", "margin": "0px 5px", "font-weight": "500",
                     "background-color": "white", "box-shadow": "0 2px 10px rgba(0,0,0,0.05)"},
        "nav-link:hover": {"background-color": "#0077B620", "transform": "translateY(-2px)"},
        "nav-link-selected": {"background-color": "#0077B6", "color": "white", "font-weight": "bold",
                              "box-shadow": "0 5px 15px rgba(0,119,182,0.3)"},
    }
)

# Map navigation
page_mapping = {
    L['nav_home']: "home", L['nav_diagnosis']: "diagnosis",
    L['nav_history']: "history", L['nav_info']: "info",
    L['nav_emergency']: "emergency", L['nav_about']: "about"
}
st.session_state.page = page_mapping.get(selected, "home")

# --- 10. HOME PAGE ---
if st.session_state.page == "home":
    st.markdown(f"""
    <div class="medical-card" style="text-align:center;">
        <h1 style="font-size:2.5rem; margin-bottom:15px;">🏥 {L['title']}</h1>
        <p style="font-size:1.3rem; opacity:0.95;">{L['desc']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Steps
    st.markdown(f"<h2 style='text-align:center; margin:30px 0;'>📋 {L['how_it_works']}</h2>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size:3rem;">🔍</div>
            <h4>{L['step1']}</h4>
            <p style="color:#666;">لە لیستی نیشانەکان ئەوانەی هەتە هەڵبژێرە</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size:3rem;">📝</div>
            <h4>{L['step2']}</h4>
            <p style="color:#666;">تەمەن و ڕەگەز و ماوەی نیشانەکان دیاری بکە</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size:3rem;">🤖</div>
            <h4>{L['step3']}</h4>
            <p style="color:#666;">سیستەمەکە نیشانەکانت شیدەکاتەوە و ئەنجام دەدات</p>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size:3rem;">💊</div>
            <h4>{L['step4']}</h4>
            <p style="color:#666;">ڕێنمایی و ڕێژەی ئەگەری نەخۆشییەکان وەربگرە</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Statistics
    history_df = load_diagnosis_history()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(history_df)}</div>
            <div class="metric-label">کۆی شیکارییەکان</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(DISEASE_DATABASE)}</div>
            <div class="metric-label">نەخۆشی لە بنکەدراوە</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">95%</div>
            <div class="metric-label">ڕێژەی دروستی</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Start button
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button(f"🔍 {L['start_diagnosis']} - دەستپێبکە", use_container_width=True):
        st.session_state.page = "diagnosis"
        st.rerun()
    
    st.markdown(f'<div class="glass-card" style="text-align:center; margin-top:20px;">{L["disclaimer"]}</div>', unsafe_allow_html=True)

# --- 11. DIAGNOSIS PAGE ---
elif st.session_state.page == "diagnosis":
    st.markdown(f"<h2 style='text-align:center;'>🔍 {L['nav_diagnosis']}</h2>", unsafe_allow_html=True)
    
    # جمع كل الأعراض
    all_symptoms = []
    for disease_data in DISEASE_DATABASE.values():
        all_symptoms.extend(disease_data['symptoms'])
    all_symptoms = sorted(list(set(all_symptoms)))
    
    # معلومات شخصية
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        age = st.number_input(L['age'], min_value=1, max_value=120, value=30)
    with col2:
        gender = st.selectbox(L['gender'], [L['male'], L['female']])
    with col3:
        duration = st.selectbox(L['duration'], 
                               [L['days_1_3'], L['days_4_7'], 
                                L['weeks_1_2'], L['more_than_2_weeks']])
    st.markdown('</div>', unsafe_allow_html=True)
    
    # اختيار الأعراض
    st.markdown(f"<h4>{L['select_symptoms']}</h4>", unsafe_allow_html=True)
    
    cols = st.columns(3)
    selected_symptoms = []
    
    for i, symptom in enumerate(all_symptoms):
        col = cols[i % 3]
        with col:
            if st.checkbox(f"• {symptom}", key=f"symptom_{i}"):
                selected_symptoms.append(symptom)
    
    # عرض الأعراض المختارة
    if selected_symptoms:
        st.markdown(f"**{L['selected_symptoms']}:** {len(selected_symptoms)}")
        symptoms_html = " ".join([
            f"<span style='display:inline-block;background:linear-gradient(135deg,#0077B6,#00B4D8);color:white;padding:8px 16px;border-radius:25px;margin:5px;font-size:0.9rem;box-shadow:0 3px 10px rgba(0,119,182,0.3);'>{s}</span>" 
            for s in selected_symptoms
        ])
        st.markdown(symptoms_html, unsafe_allow_html=True)
    
    # فحص الطوارئ
    emergency_symptoms = check_emergency(selected_symptoms)
    if emergency_symptoms:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#FF444410,#FF6B6B10);border:3px solid #FF4444;
                    border-radius:20px;padding:25px;margin:20px 0;animation:pulse 2s infinite;">
            <h2 style="color:#FF4444;text-align:center;">🚨 {L['emergency_title']}</h2>
            <p style="color:#FF4444;font-size:1.3rem;text-align:center;font-weight:bold;">{L['emergency_warning']}</p>
            <p style="text-align:center;font-size:1.1rem;"><b>نیشانە مەترسیدارەکانت:</b> {', '.join(emergency_symptoms)}</p>
            <div style="text-align:center;margin-top:15px;">
                <a href="tel:122" style="text-decoration:none;">
                    <button style="background:linear-gradient(135deg,#FF4444,#FF6B6B);color:white;
                                   padding:15px 40px;border:none;border-radius:15px;font-size:1.3rem;
                                   cursor:pointer;box-shadow:0 5px 20px rgba(255,68,68,0.4);">
                        📞 پەیوەندی بە ١٢٢ بکە
                    </button>
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # زر التشخيص
    if st.button(f"🔍 {L['start_diagnosis']}", use_container_width=True):
        if len(selected_symptoms) < 1:
            st.warning("تکایە لانیکەم یەک نیشانە هەڵبژێرە")
        else:
            with st.spinner("🔍 شیکاری نیشانەکانت دەکرێت... تکایە چاوەڕێ بکە"):
                time.sleep(1.5)
                results = analyze_symptoms(selected_symptoms, age, gender, duration)
                
                if results:
                    st.session_state.current_diagnosis = {
                        "symptoms": selected_symptoms,
                        "results": results,
                        "age": age,
                        "gender": gender,
                        "duration": duration
                    }
                    
                    # حفظ في التاريخ
                    history_df = load_diagnosis_history()
                    top_diagnosis = results[0]['disease']
                    top_probability = results[0]['probability']
                    
                    new_record = pd.DataFrame([{
                        "diagnosis_id": str(uuid.uuid4())[:8],
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "age": age,
                        "gender": gender,
                        "duration": duration,
                        "symptoms": ", ".join(selected_symptoms),
                        "diagnosis": top_diagnosis,
                        "probability": f"{top_probability}%",
                        "severity": results[0]['severity']
                    }])
                    history_df = pd.concat([history_df, new_record], ignore_index=True)
                    save_diagnosis_history(history_df)
                    
                    st.success("✅ شیکاری تەواو بوو!")
                    st.balloons()
                    st.rerun()
                else:
                    st.warning("نەتوانرا نەخۆشی دیاری بکرێت. تکایە نیشانەی زیاتر زیاد بکە یان سەردانی پزیشک بکە.")
    
    # عرض النتائج
    if st.session_state.current_diagnosis:
        results = st.session_state.current_diagnosis['results']
        symptoms = st.session_state.current_diagnosis['symptoms']
        
        st.markdown(f"<h2 style='margin-top:40px;text-align:center;'>📊 {L['diagnosis_result']}</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center;color:#666;'><b>{L['selected_symptoms']}:</b> {', '.join(symptoms)}</p>", unsafe_allow_html=True)
        
        for i, result in enumerate(results):
            medals = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣']
            
            st.markdown(f"""
            <div class="diagnosis-card" style="border-right:6px solid {result['color']};animation-delay:{i*0.1}s;">
                <div style="display:flex;align-items:center;gap:15px;margin-bottom:20px;">
                    <span style="font-size:2.5rem;">{medals[i]}</span>
                    <div style="flex:1;">
                        <h3 style="margin:0;color:{result['color']};">{result['disease']}</h3>
                        <span style="background:{result['color']}20;color:{result['color']};
                                     padding:5px 15px;border-radius:20px;font-size:0.9rem;font-weight:bold;">
                            {result['severity']}
                        </span>
                    </div>
                    <div style="text-align:center;">
                        <div style="font-size:2rem;font-weight:bold;color:{result['color']};">{result['probability']}%</div>
                        <div style="font-size:0.8rem;color:#666;">{L['probability']}</div>
                    </div>
                </div>
                
                <div class="probability-bar-container">
                    <div class="probability-bar" style="width:{result['probability']}%;background:linear-gradient(90deg,{result['color']},{result['color']}cc);">
                        <span class="probability-text">{result['matching_symptoms']}/{result['total_symptoms']} نیشانە</span>
                    </div>
                </div>
                
                <div class="info-grid">
                    <div class="info-item" style="border-right-color:{result['color']};">
                        <strong>💊 {L['advice']}:</strong><br>
                        <span style="color:#555;">{result['advice']}</span>
                    </div>
                    <div class="info-item" style="border-right-color:{result['color']};">
                        <strong>⚕️ {L['specialty']}:</strong><br>
                        <span style="color:#555;">{result['specialty']}</span>
                    </div>
                    <div class="info-item" style="border-right-color:{result['color']};">
                        <strong>🚨 {L['when_to_see_doctor']}:</strong><br>
                        <span style="color:#555;">{result['when_to_see_doctor']}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # زر تشخيص جديد
        if st.button("🔄 شیکاری نوێ", use_container_width=True):
            st.session_state.current_diagnosis = None
            st.rerun()

# --- 12. HISTORY PAGE ---
elif st.session_state.page == "history":
    st.markdown(f"<h2 style='text-align:center;'>📋 {L['history_title']}</h2>", unsafe_allow_html=True)
    
    history_df = load_diagnosis_history()
    
    if history_df.empty:
        st.info(L['no_history'])
        if st.button(f"🔍 {L['start_diagnosis']}"):
            st.session_state.page = "diagnosis"
            st.rerun()
    else:
        st.dataframe(history_df, use_container_width=True)
        
        if len(history_df) > 0:
            diagnosis_counts = history_df['diagnosis'].value_counts()
            fig = px.pie(values=diagnosis_counts.values, names=diagnosis_counts.index, 
                        title='نەخۆشییە شیکاریکراوەکانت')
            fig.update_traces(marker=dict(colors=['#0077B6', '#00B4D8', '#00C851', '#FFA500', '#FF4444']))
            st.plotly_chart(fig, use_container_width=True)

# --- 13. INFO PAGE ---
elif st.session_state.page == "info":
    st.markdown(f"<h2 style='text-align:center;'>📚 {L['nav_info']}</h2>", unsafe_allow_html=True)
    
    disease_list = list(DISEASE_DATABASE.keys())
    selected_disease = st.selectbox("نەخۆشی هەڵبژێرە بۆ زانیاری زیاتر", disease_list)
    
    if selected_disease:
        disease = DISEASE_DATABASE[selected_disease]
        
        st.markdown(f"""
        <div class="diagnosis-card" style="border-right:6px solid {disease['color']};">
            <h2 style="color:{disease['color']};">{selected_disease}</h2>
            <span style="background:{disease['color']}20;color:{disease['color']};
                         padding:5px 15px;border-radius:20px;font-weight:bold;">
                {disease['severity']}
            </span>
            <hr style="margin:20px 0;">
            
            <div class="info-grid">
                <div class="info-item">
                    <h4>🔍 نیشانەکان:</h4>
                    <p>{', '.join(disease['symptoms'])}</p>
                </div>
                <div class="info-item">
                    <h4>💊 ڕێنمایی:</h4>
                    <p>{disease['advice']}</p>
                </div>
                <div class="info-item">
                    <h4>⚕️ پزیشکی پسپۆڕ:</h4>
                    <p>{disease['specialty']}</p>
                </div>
                <div class="info-item">
                    <h4>🚨 کەی سەردانی پزیشک بکەیت:</h4>
                    <p>{disease['when_to_see_doctor']}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# --- 14. EMERGENCY PAGE ---
elif st.session_state.page == "emergency":
    st.markdown(f"<h2 style='color:#FF4444;text-align:center;'>🚨 {L['emergency_title']}</h2>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#FF444410,#FF6B6B10);border:3px solid #FF4444;
                border-radius:20px;padding:25px;margin:20px 0;">
        <h3 style="color:#FF4444;">⚠️ {L['emergency_warning']}</h3>
        <p style="font-size:1.2rem;">{L['emergency_symptoms']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <a href="tel:104" style="text-decoration:none;">
            <div class="metric-card" style="cursor:pointer;">
                <h1>🚓</h1>
                <h3>پۆلیس</h3>
                <h2 style="color:#FF4444;">104</h2>
            </div>
        </a>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <a href="tel:122" style="text-decoration:none;">
            <div class="metric-card" style="cursor:pointer;">
                <h1>🚑</h1>
                <h3>فریاکەوتن</h3>
                <h2 style="color:#FF4444;">122</h2>
            </div>
        </a>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <a href="tel:07801352003" style="text-decoration:none;">
            <div class="metric-card" style="cursor:pointer;">
                <h1>🏥</h1>
                <h3>نەخۆشخانە</h3>
                <h2 style="color:#FF4444;">0780...</h2>
            </div>
        </a>
        """, unsafe_allow_html=True)

# --- 15. ABOUT PAGE ---
elif st.session_state.page == "about":
    st.markdown(f"<h2 style='text-align:center;'>ℹ️ {L['nav_about']}</h2>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="glass-card">
        <h3>🏥 سیستەمی شیکاری نەخۆشییەکان</h3>
        <p>ئەم سیستەمە بەکاردێت بۆ:</p>
        <ul>
            <li>🔍 شیکاری سەرەتایی نیشانەکان</li>
            <li>🤖 پێشبینی نەخۆشییە ئەگەرییەکان بە هۆشمەندی دەستکرد</li>
            <li>📚 پێشکەشکردنی زانیاری پزیشکی و ڕێنمایی</li>
            <li>🚨 دیاریکردنی حاڵەتی فریاکەوتن</li>
        </ul>
        <br>
        <p><b>وەشانی:</b> 2.0.0</p>
        <p><b>زمان:</b> کوردی</p>
        <p><b>بنکەدراوەی نەخۆشییەکان:</b> {len(DISEASE_DATABASE)} نەخۆشی</p>
        <p><b>ژمارەی نیشانەکان:</b> {sum(len(d['symptoms']) for d in DISEASE_DATABASE.values())} نیشانە</p>
        <br>
        {L['disclaimer']}
    </div>
    """, unsafe_allow_html=True)

# --- 16. FOOTER ---
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(f"""
<div style="background:white;padding:20px;border-radius:15px;text-align:center;
            box-shadow:0 -5px 20px rgba(0,0,0,0.05);margin-top:30px;">
    <p style="color:#FF4444;font-weight:bold;">⚠️ ئەم سیستەمە تەنها بۆ ڕێنمایی سەرەتاییە و نابێت جێگەی سەردانی پزیشک بگرێتەوە</p>
    <p style="color:#666;">© ٢٠٢٤ سیستەمی شیکاری نەخۆشییەکان - بە هۆشمەندی دەستکرد | وەشانی 2.0</p>
</div>
""", unsafe_allow_html=True)
