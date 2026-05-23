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
        "specialty": "پزیشکی گشتی"
    },
    "ئەنفلۆنزا": {
        "symptoms": ["تا بەرز", "لەرزین", "ئێشی ماسولکەکان", "سەرئێشە", "کۆکەی وشک", "ماندوێتی زۆر", "قورگ ئێشە"],
        "severity": "مامناوەند",
        "advice": "پشووی تەواو، شلەی زۆر، دەرمانی دژە تا. لە ماوەی ٤٨ کاتژمێری یەکەمدا سەردانی پزیشک بکە.",
        "when_to_see_doctor": "هەرچەند زووە پەیوەندی بە پزیشکەوە بکە، بەتایبەت ئەگەر تەمەنت لە ٦٥ ساڵ زیاترە یان نەخۆشی درێژخایەنت هەیە",
        "specialty": "پزیشکی گشتی"
    },
    "کۆڤید-١٩": {
        "symptoms": ["تا", "کۆکەی وشک", "ماندوێتی", "لەدەستدانی بۆن", "لەدەستدانی تام", "هەناسە تەنگی", "ئێشی ماسولکەکان", "قورگ ئێشە"],
        "severity": "مامناوەند تا مەترسیدار",
        "advice": "خۆت جیا بکەرەوە، پشوو بدە، شلە زۆر بخۆرەوە. ئەگەر هەناسە تەنگی هەبوو یەکسەر پەیوەندی بە پزیشکەوە بکە.",
        "when_to_see_doctor": "هەناسە تەنگی، ئازاری سنگ، لەدەستدانی هۆش، ڕەنگی پێستی شین بوو",
        "specialty": "پزیشکی هەناوی"
    },
    "شەکرەی جۆری ٢": {
        "symptoms": ["تینوێتی زۆر", "میزکردنی زۆر", "برسێتی زۆر", "ماندوێتی", "بینینی تەمومژاوی", "برینی درەنگ چاکبوو", "دابەزینی کێش"],
        "severity": "درێژخایەن",
        "advice": "پشکنینی شەکری خوێن ئەنجام بدە. ڕێجیم و وەرزش ڕێک بخە. سەردانی پزیشکی شەکرە بکە.",
        "when_to_see_doctor": "ئاستی شەکری خوێن لە ٢٠٠ mg/dL زیاتر، یان نیشانەکانی ketoacidosis",
        "specialty": "پزیشکی شەکرە"
    },
    "پەستانی خوێنی بەرز": {
        "symptoms": ["سەرئێشە", "سەرگێژخواردن", "بینینی تەمومژاوی", "ئازاری سنگ", "هەناسە تەنگی", "خوێن لە لوت"],
        "severity": "درێژخایەن",
        "advice": "پێوانەکردنی پەستانی خوێن. کەمکردنەوەی خوێ. ڕێجیمی تەندروست. وەرزشی ڕێک.",
        "when_to_see_doctor": "پەستانی خوێن لە ١٨٠/١٢٠ زیاتر، ئازاری سنگی توند، هەناسە تەنگی لەناکاو",
        "specialty": "پزیشکی دڵ"
    },
    "هەوکردنی گەدە (Gastritis)": {
        "symptoms": ["ئازاری سک", "دڵ تێکەڵهاتن", "ڕشانەوە", "هەستکردن بە پڕی", "نەمانی ئارەزووی خواردن", "هەڵئاوسان"],
        "severity": "مامناوەند",
        "advice": "خواردنی سوک و بەش بەش. دوورکەوتنەوە لە خواردنی تیژ و چەور. دەرمانی دژە ترش.",
        "when_to_see_doctor": "ڕشانەوەی خوێناوی، پیسایی ڕەش، ئازاری توندی سک",
        "specialty": "پزیشکی هەرس"
    },
    "هەوکردنی سینوسەکان (Sinusitis)": {
        "symptoms": ["سەرئێشە", "ئازاری ڕوخسار", "گیرانی لوت", "پژمین", "کۆکە", "تا", "دەردراوی لوت"],
        "severity": "سوک تا مامناوەند",
        "advice": "هەڵم لە دەموچاو بدە. شلەی زۆر بخۆرەوە. دەرمانی دژە کۆکە و هەستیاری.",
        "when_to_see_doctor": "تا بەرز، ئازاری توندی ڕوخسار، درێژەکێشانی زیاتر لە ١٠ ڕۆژ",
        "specialty": "پزیشکی گوێ و لوت و قورگ"
    },
    "هەوکردنی میزەڕۆ (UTI)": {
        "symptoms": ["میزکردنی زۆر", "ئازار لە کاتی میزکردن", "ئازاری خوارەوەی سک", "میزی تەمومژاوی", "تا"],
        "severity": "مامناوەند",
        "advice": "زۆر ئاو بخۆرەوە. پشکنینی میز ئەنجام بدە. ئەنتی بایۆتیک بە ڕێنمایی پزیشک.",
        "when_to_see_doctor": "تا بەرز، ئازاری توند، خوێن لە میزدا",
        "specialty": "پزیشکی گورچیلە و میزەڕۆ"
    },
    "هەستیاری وەرزی (Allergy)": {
        "symptoms": ["پژمین", "کۆکە", "چاوی هەستیار", "گیرانی لوت", "خورانی چاو", "خورانی پێست"],
        "severity": "سوک",
        "advice": "دەرمانی دژە هەستیاری. دوورکەوتنەوە لە هۆکارەکانی هەستیاری.",
        "when_to_see_doctor": "هەناسە تەنگی، ئاوسانی ڕوخسار یان زمان",
        "specialty": "پزیشکی هەستیاری"
    },
    "بێخەوی (Insomnia)": {
        "symptoms": ["نەتوانینی خەوتن", "هەڵسانەوەی زوو", "ماندوێتی ڕۆژ", "بێزاری", "کەمی تەرکیز"],
        "severity": "سوک تا مامناوەند",
        "advice": "کاتەکانی خەوتن ڕێک بخە. لە شەواندا کافایین مەخۆرەوە. وەرزش بکە بەڵام نە لە کاتی شەودا.",
        "when_to_see_doctor": "ئەگەر زیاتر لە ٣ مانگ درێژەی کێشا و کاریگەری لەسەر ژیانی ڕۆژانەت هەبوو",
        "specialty": "پزیشکی دەروونی"
    },
    "سکچوون (Diarrhea)": {
        "symptoms": ["سکچوونی زۆر", "ئازاری سک", "تینوێتی", "تا", "ڕشانەوە"],
        "severity": "سوک تا مامناوەند",
        "advice": "شلەی زۆر بخۆرەوە بۆ جێگرتنەوەی ئاو. خواردنی سوک بخۆ. ORS بەکاربهێنە.",
        "when_to_see_doctor": "سکچوونی خوێناوی، زیاتر لە ٣ ڕۆژ، نیشانەکانی وشکبوونەوە",
        "specialty": "پزیشکی هەرس"
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
        "add_symptom": "زیادکردنی نیشانە"
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

# --- 6. DIAGNOSIS ENGINE (شیکەرەوەی نەخۆشی) ---
def analyze_symptoms(selected_symptoms, age, gender, duration):
    """
    شیکاری نیشانەکان بۆ دۆزینەوەی نەخۆشییە ئەگەرییەکان
    """
    results = []
    
    for disease, data in DISEASE_DATABASE.items():
        disease_symptoms = data['symptoms']
        
        # هەژمارکردنی نیشانە هاوبەشەکان
        matching_symptoms = set(selected_symptoms) & set(disease_symptoms)
        total_disease_symptoms = len(disease_symptoms)
        
        if matching_symptoms:
            # هەژمارکردنی ڕێژەی ئەگەر بەپێی نیشانە هاوبەشەکان
            base_probability = (len(matching_symptoms) / total_disease_symptoms) * 100
            
            # زیادکردنی ئەگەر بەپێی تەمەن
            if age > 60 and disease in ["پەستانی خوێنی بەرز", "شەکرەی جۆری ٢"]:
                base_probability += 15
            elif age < 12 and disease in ["هەڵامەت (سەرماخواردن)", "ئەنفلۆنزا"]:
                base_probability += 10
                
            # زیادکردنی ئەگەر بەپێی ماوە
            if duration in ["more_than_2_weeks", "weeks_1_2"] and data['severity'] == "درێژخایەن":
                base_probability += 10
            elif duration == "days_1_3" and data['severity'] == "سوک":
                base_probability += 5
                
            # سنووردارکردنی ئەگەر لە ٩٥٪
            probability = min(base_probability, 95)
            
            if probability > 20:  # تەنها ئەوانەی ئەگەریان لە ٢٠٪ زیاترە
                results.append({
                    "disease": disease,
                    "probability": round(probability, 1),
                    "matching_symptoms": len(matching_symptoms),
                    "total_symptoms": total_disease_symptoms,
                    "severity": data['severity'],
                    "advice": data['advice'],
                    "when_to_see_doctor": data['when_to_see_doctor'],
                    "specialty": data['specialty']
                })
    
    # ڕێکخستن بەپێی ئەگەر (زۆرترین یەکەم)
    results.sort(key=lambda x: x['probability'], reverse=True)
    
    return results[:5]  # تەنها ٥ ئەنجامی سەرەوە

# --- 7. EMERGENCY CHECKER ---
EMERGENCY_SYMPTOMS = [
    "ئازاری توندی سنگ", "هەناسە تەنگی لەناکاو", "لەدەستدانی هۆش", 
    "ڕشانەوەی خوێناوی", "خوێنبەربوونی توند", "ئیفلیجی", 
    "قسەکردنی ناڕوون", "ئازاری توندی سەر", "بینینی دووانە"
]

def check_emergency(selected_symptoms):
    """پشکنینی حاڵەتی فریاکەوتن"""
    emergency_found = set(selected_symptoms) & set(EMERGENCY_SYMPTOMS)
    return list(emergency_found)

# --- 8. HELPER FUNCTIONS ---
def get_severity_color(severity):
    colors = {
        "سوک": "#00C851",
        "مامناوەند": "#FFA500",
        "مامناوەند تا مەترسیدار": "#FF8800",
        "درێژخایەن": "#0077B6",
        "مەترسیدار": "#FF4444"
    }
    return colors.get(severity, "#0077B6")

def get_severity_emoji(severity):
    emojis = {
        "سوک": "🟢",
        "مامناوەند": "🟡",
        "مامناوەند تا مەترسیدار": "🟠",
        "درێژخایەن": "🔵",
        "مەترسیدار": "🔴"
    }
    return emojis.get(severity, "⚪")

# --- 9. LAYOUT ---
L = languages[st.session_state.lang_choice]

# CSS
accent = "#0077B6"
accent_light = "#00B4D8"
main_bg = "#F0F8FF"
card_bg = "#FFFFFF"

st.markdown(f"""
<style>
    [data-testid="stSidebar"] {{ display: none; }}
    html, body, [data-testid="stAppViewContainer"] {{ background-color: {main_bg} !important; }}
    .medical-card {{ background: linear-gradient(135deg, {accent} 0%, {accent_light} 100%); 
                    border-radius: 20px; padding: 25px; color: white !important; margin-bottom: 20px; }}
    .medical-card * {{ color: white !important; }}
    .glass-card {{ background-color: {card_bg}; border-radius: 20px; padding: 25px; 
                  border: 1px solid {accent}30; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
    .stButton button {{ background-color: {accent} !important; color: white !important; 
                        border: none !important; font-weight: bold !important; border-radius: 10px !important; 
                        padding: 12px 24px !important; font-size: 16px !important; }}
    .stButton button:hover {{ background-color: {accent_light} !important; transform: translateY(-2px) !important; }}
    .emergency-btn {{ background-color: #FF4444 !important; animation: pulse 2s infinite; }}
    @keyframes pulse {{ 0% {{ box-shadow: 0 0 0 0 rgba(255,68,68,0.4); }} 
                        70% {{ box-shadow: 0 0 0 15px rgba(255,68,68,0); }} 
                        100% {{ box-shadow: 0 0 0 0 rgba(255,68,68,0); }} }}
    .symptom-tag {{ display: inline-block; background-color: {accent}20; color: {accent}; 
                   padding: 8px 15px; border-radius: 20px; margin: 5px; cursor: pointer; 
                   border: 1px solid {accent}40; transition: all 0.3s; }}
    .symptom-tag:hover {{ background-color: {accent}; color: white !important; }}
    .symptom-selected {{ background-color: {accent} !important; color: white !important; }}
    .probability-bar {{ height: 10px; border-radius: 5px; margin: 10px 0; }}
    [dir="{L['dir']}"] {{ text-align: {L['align']} !important; }}
    h2 {{ color: {accent} !important; }}
    h3 {{ color: {accent} !important; }}
</style>
""", unsafe_allow_html=True)

# --- 10. NAVIGATION ---
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
        "container": {"padding": "0!important", "background-color": "transparent"},
        "nav-link": {"font-size": "14px", "text-align": "center", "padding": "10px 15px", 
                     "border-radius": "30px", "margin": "0px 3px"},
        "nav-link-selected": {"background-color": accent, "color": "white", "font-weight": "bold"},
    }
)

# Map navigation
page_mapping = {
    L['nav_home']: "home", L['nav_diagnosis']: "diagnosis",
    L['nav_history']: "history", L['nav_info']: "info",
    L['nav_emergency']: "emergency", L['nav_about']: "about"
}
st.session_state.page = page_mapping.get(selected, "home")

# --- 11. HOME PAGE ---
if st.session_state.page == "home":
    st.markdown(f"""
    <div class="medical-card" style="text-align:center;">
        <h1>🏥 {L['title']}</h1>
        <p style="font-size:1.2rem;">{L['desc']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="glass-card" style="text-align:center;">
            <h2>🔍</h2>
            <h3>شیکاری خێرا</h3>
            <p>نیشانەکانت داخڵ بکە و لە چەند چرکەیەکدا ئەنجامی شیکاری وەربگرە</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="glass-card" style="text-align:center;">
            <h2>🤖</h2>
            <h3>هۆشمەندی دەستکرد</h3>
            <p>بەکارهێنانی سیستەمی زیرەک بۆ شیکاری نیشانەکان و پێشبینی نەخۆشی</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="glass-card" style="text-align:center;">
            <h2>📚</h2>
            <h3>بنکەی زانیاری پزیشکی</h3>
            <p>زانیاری ورد لەسەر نەخۆشییە جیاوازەکان و ڕێنمایی چارەسەر</p>
        </div>
        """, unsafe_allow_html=True)
    
    # دوایین شیکارییەکان
    history_df = load_diagnosis_history()
    if not history_df.empty:
        st.markdown(f"<h3>📋 {L['history_title']}</h3>", unsafe_allow_html=True)
        st.dataframe(history_df.tail(5)[['date', 'symptoms', 'diagnosis', 'probability']], 
                    use_container_width=True)
    
    st.markdown(f'<div class="glass-card" style="text-align:center; margin-top:30px;">{L["disclaimer"]}</div>', unsafe_allow_html=True)
    
    if st.button(f"🔍 {L['start_diagnosis']}", use_container_width=True):
        st.session_state.page = "diagnosis"
        st.rerun()

# --- 12. DIAGNOSIS PAGE (شیکاری سەرەکی) ---
elif st.session_state.page == "diagnosis":
    st.markdown(f"<h2>🔍 {L['nav_diagnosis']}</h2>", unsafe_allow_html=True)
    
    # کۆکردنەوەی هەموو نیشانەکان لە بنکەدراوە
    all_symptoms = []
    for disease_data in DISEASE_DATABASE.values():
        all_symptoms.extend(disease_data['symptoms'])
    all_symptoms = sorted(list(set(all_symptoms)))
    
    # زانیاری کەسی
    col1, col2, col3 = st.columns(3)
    with col1:
        age = st.number_input(L['age'], min_value=1, max_value=120, value=30)
    with col2:
        gender = st.selectbox(L['gender'], [L['male'], L['female']])
    with col3:
        duration = st.selectbox(L['duration'], 
                               [L['days_1_3'], L['days_4_7'], 
                                L['weeks_1_2'], L['more_than_2_weeks']])
    
    # هەڵبژاردنی نیشانەکان
    st.markdown(f"<h4>{L['select_symptoms']}</h4>", unsafe_allow_html=True)
    
    # ڕێکخستنی نیشانەکان بە ستوون
    cols = st.columns(3)
    selected_symptoms = []
    
    for i, symptom in enumerate(all_symptoms):
        col = cols[i % 3]
        with col:
            if st.checkbox(f"• {symptom}", key=f"symptom_{i}"):
                selected_symptoms.append(symptom)
    
    # پیشاندانی نیشانە هەڵبژێردراوەکان
    if selected_symptoms:
        st.markdown(f"**{L['selected_symptoms']}:** {len(selected_symptoms)}")
        st.markdown(" ".join([f"<span class='symptom-tag symptom-selected'>{s}</span>" 
                             for s in selected_symptoms]), unsafe_allow_html=True)
    
    # پشکنینی حاڵەتی فریاکەوتن
    emergency_symptoms = check_emergency(selected_symptoms)
    if emergency_symptoms:
        st.markdown(f"""
        <div class="glass-card" style="border: 2px solid #FF4444; background-color: #FF444410;">
            <h2 style="color:#FF4444;">🚨 {L['emergency_title']}</h2>
            <p style="color:#FF4444; font-size:1.2rem;">{L['emergency_warning']}</p>
            <p><b>نیشانە مەترسیدارەکانت:</b> {', '.join(emergency_symptoms)}</p>
            <button onclick="window.location.href='tel:122'" style="background-color:#FF4444; color:white; 
                    padding:15px 30px; border:none; border-radius:10px; font-size:1.2rem; cursor:pointer;">
                📞 پەیوەندی بە ١٢٢ بکە
            </button>
        </div>
        """, unsafe_allow_html=True)
    
    # دوگمەی شیکاری
    if st.button(f"🔍 {L['start_diagnosis']}", use_container_width=True, type="primary"):
        if len(selected_symptoms) < 1:
            st.warning("تکایە لانیکەم یەک نیشانە هەڵبژێرە")
        else:
            with st.spinner("🔍 شیکاری نیشانەکانت دەکرێت..."):
                time.sleep(1.5)  # سیمولەیشنی شیکاری
                results = analyze_symptoms(selected_symptoms, age, gender, duration)
                
                if results:
                    st.session_state.current_diagnosis = {
                        "symptoms": selected_symptoms,
                        "results": results,
                        "age": age,
                        "gender": gender,
                        "duration": duration
                    }
                    
                    # هەڵگرتنی لە مێژوو
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
                    st.rerun()
                else:
                    st.warning("نەتوانرا نەخۆشی دیاری بکرێت. تکایە نیشانەی زیاتر زیاد بکە یان سەردانی پزیشک بکە.")
    
    # پیشاندانی ئەنجامی شیکاری
    if st.session_state.current_diagnosis:
        results = st.session_state.current_diagnosis['results']
        symptoms = st.session_state.current_diagnosis['symptoms']
        
        st.markdown(f"<h2 style='margin-top:30px;'>📊 {L['diagnosis_result']}</h2>", unsafe_allow_html=True)
        st.markdown(f"**{L['selected_symptoms']}:** {', '.join(symptoms)}")
        
        for i, result in enumerate(results):
            severity_color = get_severity_color(result['severity'])
            severity_emoji = get_severity_emoji(result['severity'])
            
            with st.container():
                st.markdown(f"""
                <div class="glass-card" style="border-left: 5px solid {severity_color};">
                    <h3>{'🥇' if i==0 else '🥈' if i==1 else '🥉' if i==2 else '📋'} 
                        {result['disease']} {severity_emoji}</h3>
                    
                    <div style="background-color:#e0e0e0; border-radius:10px; margin:10px 0;">
                        <div style="background-color:{severity_color}; width:{result['probability']}%; 
                             height:10px; border-radius:10px;"></div>
                    </div>
                    <p><b>{L['probability']}:</b> {result['probability']}% 
                    ({result['matching_symptoms']}/{result['total_symptoms']} نیشانە)</p>
                    
                    <p><b>{L['severity']}:</b> <span style="color:{severity_color};">{result['severity']}</span></p>
                    <p><b>💊 {L['advice']}:</b> {result['advice']}</p>
                    <p><b>⚕️ {L['specialty']}:</b> {result['specialty']}</p>
                    <p><b>🚨 {L['when_to_see_doctor']}:</b> {result['when_to_see_doctor']}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # دوگمەی شیکاری نوێ
        if st.button("🔄 شیکاری نوێ", use_container_width=True):
            st.session_state.current_diagnosis = None
            st.rerun()

# --- 13. HISTORY PAGE ---
elif st.session_state.page == "history":
    st.markdown(f"<h2>📋 {L['history_title']}</h2>", unsafe_allow_html=True)
    
    history_df = load_diagnosis_history()
    
    if history_df.empty:
        st.info(L['no_history'])
        if st.button(f"🔍 {L['start_diagnosis']}"):
            st.session_state.page = "diagnosis"
            st.rerun()
    else:
        st.dataframe(history_df, use_container_width=True)
        
        # چارت
        if len(history_df) > 0:
            diagnosis_counts = history_df['diagnosis'].value_counts()
            fig = px.pie(values=diagnosis_counts.values, names=diagnosis_counts.index, 
                        title='نەخۆشییە شیکاریکراوەکانت')
            st.plotly_chart(fig, use_container_width=True)

# --- 14. INFO PAGE (زانیاری نەخۆشییەکان) ---
elif st.session_state.page == "info":
    st.markdown(f"<h2>📚 {L['nav_info']}</h2>", unsafe_allow_html=True)
    
    disease_list = list(DISEASE_DATABASE.keys())
    selected_disease = st.selectbox("نەخۆشی هەڵبژێرە بۆ زانیاری زیاتر", disease_list)
    
    if selected_disease:
        disease = DISEASE_DATABASE[selected_disease]
        severity_color = get_severity_color(disease['severity'])
        
        st.markdown(f"""
        <div class="glass-card" style="border-left: 5px solid {severity_color};">
            <h2>{selected_disease}</h2>
            <p><b>{L['severity']}:</b> <span style="color:{severity_color};">{disease['severity']}</span></p>
            <hr>
            <h4>🔍 نیشانەکان:</h4>
            <p>{', '.join(disease['symptoms'])}</p>
            <hr>
            <h4>💊 ڕێنمایی:</h4>
            <p>{disease['advice']}</p>
            <hr>
            <h4>⚕️ پزیشکی پسپۆڕ:</h4>
            <p>{disease['specialty']}</p>
            <hr>
            <h4>🚨 کەی سەردانی پزیشک بکەیت:</h4>
            <p>{disease['when_to_see_doctor']}</p>
        </div>
        """, unsafe_allow_html=True)

# --- 15. EMERGENCY PAGE ---
elif st.session_state.page == "emergency":
    st.markdown(f"<h2 style='color:#FF4444;'>🚨 {L['emergency_title']}</h2>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="glass-card" style="border: 2px solid #FF4444; background-color: #FF444410;">
        <h3 style="color:#FF4444;">⚠️ {L['emergency_warning']}</h3>
        <p style="font-size:1.2rem;">{L['emergency_symptoms']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <a href="tel:104" style="text-decoration:none;">
            <div class="glass-card" style="text-align:center; cursor:pointer;">
                <h1>🚓</h1>
                <h3>پۆلیس</h3>
                <h2 style="color:#FF4444;">104</h2>
            </div>
        </a>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <a href="tel:122" style="text-decoration:none;">
            <div class="glass-card" style="text-align:center; cursor:pointer;">
                <h1>🚑</h1>
                <h3>فریاکەوتن</h3>
                <h2 style="color:#FF4444;">122</h2>
            </div>
        </a>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <a href="tel:07801352003" style="text-decoration:none;">
            <div class="glass-card" style="text-align:center; cursor:pointer;">
                <h1>🏥</h1>
                <h3>نەخۆشخانە</h3>
                <h2 style="color:#FF4444;">0780...</h2>
            </div>
        </a>
        """, unsafe_allow_html=True)

# --- 16. ABOUT PAGE ---
elif st.session_state.page == "about":
    st.markdown(f"<h2>ℹ️ {L['nav_about']}</h2>", unsafe_allow_html=True)
    
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
        <p><b>وەشانی:</b> 1.0.0</p>
        <p><b>زمان:</b> کوردی</p>
        <p><b>بنکەدراوەی نەخۆشییەکان:</b> {len(DISEASE_DATABASE)} نەخۆشی</p>
        <br>
        {L['disclaimer']}
    </div>
    """, unsafe_allow_html=True)

# --- 17. FOOTER ---
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(f"""
<div style="background-color:{card_bg}; padding:15px; border-radius:10px; text-align:center; 
            border: 1px solid {accent}20; margin-top:30px;">
    <p style="color:#FF4444;">⚠️ ئەم سیستەمە تەنها بۆ ڕێنمایی سەرەتاییە و نابێت جێگەی سەردانی پزیشک بگرێتەوە</p>
    <p>© ٢٠٢٤ سیستەمی شیکاری نەخۆشییەکان - بە هۆشمەندی دەستکرد</p>
</div>
""", unsafe_allow_html=True)
