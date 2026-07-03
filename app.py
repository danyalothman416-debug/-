import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import random
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# ڕێکخستنی ڕووکاری پەڕە
st.set_page_config(
    page_title="ڕاهێنەری پزیشکی - Medical Training Simulator",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        text-align: center;
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
    }
    .case-card {
        background: linear-gradient(145deg, #f0f4ff, #e8edff);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #667eea;
        margin: 1rem 0;
    }
    .success-box {
        background: #d4edda;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #28a745;
    }
    .error-box {
        background: #f8d7da;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #dc3545;
    }
    .quiz-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    .progress-bar {
        height: 10px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# داتابەیسی نەخۆشییەکان بۆ فێربوون
DISEASE_DATABASE = {
    "شەکرەی جۆری 2": {
        "نیشانەکان": ["تینوویەتی زۆر", "میزی زۆر", "ماندوویی", "کێش کەمبوونەوە", "بینی تەڵخ"],
        "پشکنینەکان": {
            "FBS": ">126 mg/dL",
            "HbA1c": ">6.5%",
            "OGTT": ">200 mg/dL"
        },
        "چارەسەر": ["مێتفۆرمین 500mg", "گۆڕینی شێوازی ژیان", "وەرزشی ڕۆژانە"],
        "ئاستی مەترسی": "مەترسیدار",
        "تایبەتمەندییە جیاکەرەوەکان": "FBS بەرز + HbA1c بەرز"
    },
    "پەستانی خوێنی سەرەتایی": {
        "نیشانەکان": ["سەرئێشە", "سەرگێژخواردن", "فشاری پشت چاو", "خێرالێدانی دڵ"],
        "پشکنینەکان": {
            "BP": ">140/90 mmHg",
            "ECG": "Left ventricular hypertrophy",
            "Creatinine": "نۆرماڵ"
        },
        "چارەسەر": ["کاپتۆپریل 25mg", "کەمکردنەوەی نمەک", "وەرزش"],
        "ئاستی مەترسی": "مامناوەند",
        "تایبەتمەندییە جیاکەرەوەکان": "BP بەرز بەبێ هۆکاری دیکە"
    },
    "نەخۆشی دڵی ئیسکیمیک": {
        "نیشانەکان": ["ئازاری سنگ", "کورتی هەناسە", "ئارەقەکردن", "سکچوون و ڕشانەوە"],
        "پشکنینەکان": {
            "ECG": "ST depression",
            "Troponin": "بەرز",
            "CK-MB": "بەرز"
        },
        "چارەسەر": ["ئەسپیرین 300mg", "نایترۆگلیسیرین", "ئۆکسجین"],
        "ئاستی مەترسی": "زۆر مەترسیدار",
        "تایبەتمەندییە جیاکەرەوەکان": "ST changes + Troponin elevated"
    },
    "هەوکردنی سییەکان": {
        "نیشانەکان": ["تا", "کۆخە", "هەناسەدان بە زەحمەت", "ئازاری سنگ"],
        "پشکنینەکان": {
            "Chest X-ray": "Consolidation",
            "CRP": "بەرز",
            "WBC": "بەرز"
        },
        "چارەسەر": ["ئەنتیبایۆتیک", "ئۆکسجین", "شلەمەنی"],
        "ئاستی مەترسی": "مامناوەند",
        "تایبەتمەندییە جیاکەرەوەکان": "Consolidation لە X-ray + CRP بەرز"
    },
    "ئەنیمیا": {
        "نیشانەکان": ["ماندوویی", "ڕەنگی پێست زەرد", "سەرگێژخواردن", "لێدانی دڵ خێرا"],
        "پشکنینەکان": {
            "Hb": "<12 g/dL",
            "MCV": "<80 fL (microcytic)",
            "Ferritin": "نزم"
        },
        "چارەسەر": ["سوپلیمێنتی ئاسن", "گۆڕینی خواردن", "دۆزینەوەی هۆکاری سەرەکی"],
        "ئاستی مەترسی": "مامناوەند",
        "تایبەتمەندییە جیاکەرەوەکان": "Hb نزم + MCV نزم + Ferritin نزم"
    }
}

# کویزەکانی پزیشکی
MEDICAL_QUIZZES = [
    {
        "پرسیار": "نەخۆشێکی 45 ساڵان، سەرئێشە و سەرگێژخواردنی هەیە، BP=160/95. باشترین هەنگاوی داهاتوو چییە؟",
        "هەڵبژاردەکان": [
            "دەستبەجێ دەرمانی دژە پەستانی خوێن",
            "پێوانەکردنی BP دوای 2 هەفتە و گۆڕینی شێوازی ژیان",
            "CT سەر",
            "پشکنینی خوێنی تەواو"
        ],
        "وەڵامی ڕاست": 1,
        "ڕوونکردنەوە": "بەپێی ڕێنماییەکان، بۆ پەستانی خوێنی قۆناغی 1، دەبێت دووبارە BP پێوانە بکرێت و گۆڕانی شێوازی ژیان پێشنیار بکرێت"
    },
    {
        "پرسیار": "نەخۆشێک FBS=150, HbA1c=7.2%. دەستنیشانکردن چییە؟",
        "هەڵبژاردەکان": [
            "پێش شەکرە (Prediabetes)",
            "شەکرەی جۆری 2",
            "شەکرەی جۆری 1",
            "نەخۆشی مێتابۆلیک"
        ],
        "وەڵامی ڕاست": 1,
        "ڕوونکردنەوە": "FBS>126 و HbA1c>6.5% دوو پێوەری سەرەکی بۆ دەستنیشانکردنی شەکرەن"
    },
    {
        "پرسیار": "لە نەخۆشێکی ئەنیمیادا، MCV=72 fL. جۆری ئەنیمیا چییە؟",
        "هەڵبژاردەکان": [
            "ماکرۆسایتیک",
            "مایکرۆسایتیک",
            "نۆرمۆسایتیک",
            "هیمۆلایتیک"
        ],
        "وەڵامی ڕاست": 1,
        "ڕوونکردنەوە": "MCV<80 fL ئاماژەیە بۆ ئەنیمیای مایکرۆسایتیک (Microcytic Anemia)"
    }
]

# دروستکردنی داتای ڕاهێنان
@st.cache_data
def generate_training_cases():
    cases = []
    for disease, info in DISEASE_DATABASE.items():
        for i in range(5):
            age = random.randint(25, 75)
            case = {
                'case_id': f"CASE-{len(cases)+1:03d}",
                'تەمەن': age,
                'ڕەگەز': random.choice(['نێر', 'مێ']),
                'نیشانە سەرەکییەکان': random.sample(info['نیشانەکان'], 3),
                'پشکنینە پێویستەکان': random.choice(list(info['پشکنینەکان'].keys())),
                'دەستنیشانکردن': disease,
                'ئاستی مەترسی': info['ئاستی مەترسی']
            }
            cases.append(case)
    return pd.DataFrame(cases)

training_data = generate_training_cases()

# سایدبار
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/medical-doctor.png", width=80)
    st.markdown("## 🎓 ڕاهێنەری پزیشکی")
    
    # ئاستی خوێندکار
    student_level = st.selectbox(
        "📚 ئاستی خوێندنت:",
        ["ساڵی یەکەم", "ساڵی دووەم", "ساڵی سێیەم", "ساڵی چوارەم", "ساڵی پێنجەم", "ساڵی شەشەم"]
    )
    
    st.markdown("---")
    
    page = st.radio(
        "📋 بەشەکان:",
        [
            "🏠 داشبۆردی فێربوون",
            "📚 کتێبخانەی نەخۆشییەکان",
            "🩺 شیکاری کەیس",
            "📝 کویزی پزیشکی",
            "🔬 تاقیگەی ڤێرچواڵ",
            "📊 پێشکەوتنی فێربوون",
            "💊 فارماکۆلۆجی"
        ]
    )
    
    st.markdown("---")
    st.markdown(f"### 👨‍🎓 خوێندکاری ساڵی {student_level}")
    st.progress(0.65, text="پێشکەوتنی گشتی: 65%")

# پەڕەی سەرەکی - داشبۆرد
if page == "🏠 داشبۆردی فێربوون":
    st.markdown('<h1 class="main-header">🎓 ڕاهێنەری پزیشکی - ببە پزیشکێکی لێهاتوو</h1>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="case-card">', unsafe_allow_html=True)
        st.metric("📚 کەیسی فێربوون", len(training_data), f"{len(training_data)} کەیس")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="case-card">', unsafe_allow_html=True)
        st.metric("🩺 نەخۆشی جیاواز", len(DISEASE_DATABASE), "نەخۆشی")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="case-card">', unsafe_allow_html=True)
        st.metric("📝 کویزی ئەنجامدراو", "12/20", "60%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ڕێنمایی ڕۆژانە
    st.markdown("### 📖 وانەی ڕۆژانە")
    
    daily_topic = random.choice(list(DISEASE_DATABASE.keys()))
    daily_info = DISEASE_DATABASE[daily_topic]
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"""
        <div class="case-card">
            <h3>🎯 وانەی ئەمڕۆ: {daily_topic}</h3>
            <p><strong>نیشانە سەرەکییەکان:</strong> {', '.join(daily_info['نیشانەکان'][:3])}</p>
            <p><strong>تایبەتمەندی جیاکەرەوە:</strong> {daily_info['تایبەتمەندییە جیاکەرەوەکان']}</p>
            <p><strong>ئاستی مەترسی:</strong> <span style='color: red;'>{daily_info['ئاستی مەترسی']}</span></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 🎯 ئامانجەکانی فێربوون")
        st.checkbox("ناسینەوەی نیشانەکان", True)
        st.checkbox("دەستنیشانکردنی جیاکار", False)
        st.checkbox("پلانی چارەسەر", False)
        st.checkbox("پشکنینە پێویستەکان", True)
    
    # گرافی پێشکەوتن
    st.markdown("---")
    st.markdown("### 📈 پێشکەوتنی فێربوون بەپێی بوار")
    
    progress_data = pd.DataFrame({
        'بوار': ['نیشانەناسی', 'دەستنیشانکردن', 'چارەسەر', 'فارماکۆلۆجی', 'پشکنینەکان'],
        'پێشکەوتن': [75, 60, 55, 70, 80]
    })
    
    fig = px.bar(progress_data, x='بوار', y='پێشکەوتن',
                 title='ڕێژەی لێهاتوویی بەپێی بوار (%)',
                 color='پێشکەوتن',
                 color_continuous_scale='Viridis')
    st.plotly_chart(fig, use_container_width=True)

# پەڕەی کتێبخانە
elif page == "📚 کتێبخانەی نەخۆشییەکان":
    st.markdown("## 📚 کتێبخانەی نەخۆشییەکان")
    
    search = st.text_input("🔍 گەڕان بەدوای نەخۆشیدا:", placeholder="ناوی نەخۆشی بنووسە...")
    
    if search:
        filtered = {k: v for k, v in DISEASE_DATABASE.items() if search in k}
        diseases_to_show = filtered if filtered else DISEASE_DATABASE
    else:
        diseases_to_show = DISEASE_DATABASE
    
    cols = st.columns(2)
    col_idx = 0
    
    for disease, info in diseases_to_show.items():
        with cols[col_idx % 2]:
            with st.expander(f"🩺 {disease}", expanded=False):
                st.markdown("#### 🔍 نیشانەکان")
                for symptom in info['نیشانەکان']:
                    st.markdown(f"- {symptom}")
                
                st.markdown("#### 🧪 پشکنینە دەستنیشانکردنەکان")
                for test, value in info['پشکنینەکان'].items():
                    st.markdown(f"- **{test}**: {value}")
                
                st.markdown("#### 💊 چارەسەر")
                for treatment in info['چارەسەر']:
                    st.markdown(f"- {treatment}")
                
                st.markdown(f"#### ⚠️ ئاستی مەترسی: {info['ئاستی مەترسی']}")
                
                st.info(f"**تایبەتمەندی جیاکەرەوە:** {info['تایبەتمەندییە جیاکەرەوەکان']}")
        col_idx += 1

# پەڕەی شیکاری کەیس
elif page == "🩺 شیکاری کەیس":
    st.markdown("## 🩺 شیکاری کەیسی پزیشکی")
    
    st.markdown("### 📋 کەیسێکی نوێ بخوێنەرەوە و دەستنیشانی بکە")
    
    if 'current_case' not in st.session_state or st.button("🔄 کەیسی نوێ"):
        random_case = training_data.sample(1).iloc[0]
        st.session_state.current_case = random_case
        st.session_state.diagnosis_submitted = False
    
    case = st.session_state.current_case
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"""
        <div class="case-card">
            <h3>📋 کەیسی ژمارە: {case['case_id']}</h3>
            <table style="width:100%">
                <tr><td><strong>تەمەن:</strong></td><td>{case['تەمەن']} ساڵ</td></tr>
                <tr><td><strong>ڕەگەز:</strong></td><td>{case['ڕەگەز']}</td></tr>
                <tr><td><strong>نیشانەکان:</strong></td><td>{', '.join(case['نیشانە سەرەکییەکان'])}</td></tr>
                <tr><td><strong>پشکنینی پێشنیارکراو:</strong></td><td>{case['پشکنینە پێویستەکان']}</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 🔬 پشکنینە پێویستەکان")
        st.multiselect(
            "کام پشکنینانە دەکەیت؟",
            ["FBS", "HbA1c", "BP", "ECG", "Chest X-ray", "CBC", "Troponin", "CRP"],
            key="selected_tests"
        )
    
    st.markdown("### 🎯 دەستنیشانکردنەکەت چییە؟")
    
    diagnosis_options = list(DISEASE_DATABASE.keys()) + ["نەخۆشی تر", "پێویستی بە پشکنینی زیاترە"]
    
    user_diagnosis = st.selectbox("دەستنیشانکردن هەڵبژێرە:", diagnosis_options)
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("✅ پشتڕاستکردنەوە", type="primary", use_container_width=True):
            correct_diagnosis = case['دەستنیشانکردن']
            
            if user_diagnosis == correct_diagnosis:
                st.markdown(f"""
                <div class="success-box">
                    <h3>🎉 زۆر باشە! دەستنیشانکردنەکەت ڕاستە!</h3>
                    <p>دەستنیشانکردنی ڕاست: <strong>{correct_diagnosis}</strong></p>
                    <p>تۆ نیشانەکانت بە باشی خوێندەوە و گەیشتیتە دەستنیشانکردنی ڕاست!</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.balloons()
            else:
                st.markdown(f"""
                <div class="error-box">
                    <h3>❌ ببورە، دەستنیشانکردنەکەت هەڵەیە</h3>
                    <p>دەستنیشانکردنی ڕاست: <strong>{correct_diagnosis}</strong></p>
                    <p>دەستنیشانکردنی تۆ: {user_diagnosis}</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("### 💡 ڕێنمایی فێربوون:")
                disease_info = DISEASE_DATABASE[correct_diagnosis]
                st.info(f"**خاڵی جیاکەرەوە:** {disease_info['تایبەتمەندییە جیاکەرەوەکان']}")
    
    # نمرەی فێربوون
    st.markdown("---")
    st.markdown("### 📊 ئاماری شیکاری کەیسەکان")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("کەیسە شی کراوەکان", "15")
    with col2:
        st.metric("دەستنیشانکردنی ڕاست", "11", "73%")
    with col3:
        st.metric("تێکڕای کاتی شیکاری", "4.2 خولەک")

# پەڕەی کویز
elif page == "📝 کویزی پزیشکی":
    st.markdown("## 📝 تاقیکردنەوەی پزیشکی")
    
    if 'quiz_index' not in st.session_state:
        st.session_state.quiz_index = 0
        st.session_state.score = 0
        st.session_state.quiz_completed = False
    
    if not st.session_state.quiz_completed:
        quiz = MEDICAL_QUIZZES[st.session_state.quiz_index]
        
        st.markdown(f"### ❓ پرسیاری {st.session_state.quiz_index + 1} لە {len(MEDICAL_QUIZZES)}")
        st.markdown(f"""
        <div class="quiz-card">
            <h3>{quiz['پرسیار']}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        answer = st.radio("وەڵام هەڵبژێرە:", quiz['هەڵبژاردەکان'], key=f"q_{st.session_state.quiz_index}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ پشتڕاستکردنەوە", use_container_width=True):
                selected_index = quiz['هەڵبژاردەکان'].index(answer)
                
                if selected_index == quiz['وەڵامی ڕاست']:
                    st.session_state.score += 1
                    st.success("🎉 وەڵامەکەت ڕاستە!")
                else:
                    st.error(f"❌ وەڵامەکەت هەڵەیە. وەڵامی ڕاست: {quiz['هەڵبژاردەکان'][quiz['وەڵامی ڕاست']]}")
                
                st.info(f"📚 ڕوونکردنەوە: {quiz['ڕوونکردنەوە']}")
        
        with col2:
            if st.button("➡️ پرسیاری داهاتوو", use_container_width=True):
                if st.session_state.quiz_index < len(MEDICAL_QUIZZES) - 1:
                    st.session_state.quiz_index += 1
                else:
                    st.session_state.quiz_completed = True
                st.rerun()
    
    else:
        st.markdown(f"""
        <div class="success-box">
            <h2>🎊 تاقیکردنەوە تەواو بوو!</h2>
            <h3>نمرەی تۆ: {st.session_state.score}/{len(MEDICAL_QUIZZES)}</h3>
            <h4>ڕێژە: {(st.session_state.score/len(MEDICAL_QUIZZES))*100:.1f}%</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 تاقیکردنەوەی نوێ"):
            st.session_state.quiz_index = 0
            st.session_state.score = 0
            st.session_state.quiz_completed = False
            st.rerun()

# پەڕەی تاقیگە
elif page == "🔬 تاقیگەی ڤێرچواڵ":
    st.markdown("## 🔬 تاقیگەی پزیشکی ڤێرچواڵ")
    
    st.markdown("### 🧪 شیکاری پشکنینە تاقیگەییەکان")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 پشکنینی خوێن - CBC")
        
        wbc = st.slider("WBC (x10³/µL):", 1.0, 30.0, 8.0, 0.1)
        hb = st.slider("Hemoglobin (g/dL):", 5.0, 20.0, 14.0, 0.1)
        platelets = st.slider("Platelets (x10³/µL):", 50, 500, 250, 10)
        
        if st.button("🔍 شیکاری CBC بکە", use_container_width=True):
            st.markdown("---")
            st.markdown("#### 📈 ئەنجامی شیکاری:")
            
            abnormalities = []
            
            if wbc > 11:
                abnormalities.append("⚠️ WBC بەرزە - ئەگەری هەوکردن یان لیکۆسایتۆسیس")
            elif wbc < 4:
                abnormalities.append("⚠️ WBC نزمە - لیکۆپینیا")
            else:
                abnormalities.append("✅ WBC نۆرماڵە")
            
            if hb < 12:
                abnormalities.append(f"⚠️ Hb={hb} نزمە - ئەگەری ئەنیمیا")
            elif hb > 16:
                abnormalities.append("⚠️ Hb بەرزە - پۆلیسایتیمیا")
            else:
                abnormalities.append("✅ Hb نۆرماڵە")
            
            if platelets < 150:
                abnormalities.append("⚠️ Platelets نزمە - ترۆمبۆسایتۆپینیا")
            elif platelets > 450:
                abnormalities.append("⚠️ Platelets بەرزە - ترۆمبۆسایتۆسیس")
            else:
                abnormalities.append("✅ Platelets نۆرماڵە")
            
            for ab in abnormalities:
                st.markdown(ab)
    
    with col2:
        st.markdown("#### 🩸 پشکنینی بایۆکیمیایی")
        
        glucose = st.number_input("Glucose (mg/dL):", 50, 400, 100)
        creatinine = st.number_input("Creatinine (mg/dL):", 0.1, 10.0, 1.0, 0.1)
        alt = st.number_input("ALT (U/L):", 10, 200, 30)
        
        if st.button("🔍 شیکاری بایۆکیمیایی بکە", use_container_width=True):
            st.markdown("---")
            st.markdown("#### 📈 ئەنجامی شیکاری:")
            
            if glucose > 126:
                st.error(f"⚠️ Glucose={glucose} بەرزە - پێویستە پشکنینی شەکرە بکرێت")
            elif glucose < 70:
                st.warning(f"⚠️ Glucose={glucose} نزمە - هایپۆگلایسیمیا")
            else:
                st.success("✅ Glucose نۆرماڵە")
            
            if creatinine > 1.3:
                st.error(f"⚠️ Creatinine={creatinine} بەرزە - ئەگەری کێشەی گورچیلە")
            else:
                st.success("✅ Creatinine نۆرماڵە")
            
            if alt > 40:
                st.warning(f"⚠️ ALT={alt} بەرزە - ئەگەری کێشەی جگەر")
            else:
                st.success("✅ ALT نۆرماڵە")

# پەڕەی پێشکەوتن
elif page == "📊 پێشکەوتنی فێربوون":
    st.markdown("## 📊 دۆشیەی فێربوون")
    
    st.markdown("### 🎯 خاڵەکانی لێهاتوویی")
    
    skills_data = pd.DataFrame({
        'توانا': ['نیشانەناسی', 'دەستنیشانکردن', 'پشکنینەکان', 'چارەسەر', 'ڕاوێژکاری'],
        'خاڵ': [85, 70, 90, 65, 75]
    })
    
    fig = px.line_polar(skills_data, r='خاڵ', theta='توانا',
                        line_close=True, title='ڕاداری لێهاتوویی',
                        range_r=[0, 100])
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏆 دەستکەوتەکان")
        st.markdown("""
        - ⭐ دەستنیشانکردنی 50 کەیسی سەرکەوتوو
        - 🎓 تەواوکردنی کۆرسی نیشانەناسی
        - 💯 100% لە تاقیکردنەوەی فارماکۆلۆجی
        - 🔬 تەواوکردنی تاقیگەی ڤێرچواڵ
        """)
    
    with col2:
        st.markdown("### 📅 پێشکەوتنی مانگانە")
        months = ['مانگی 1', 'مانگی 2', 'مانگی 3', 'مانگی 4', 'مانگی 5']
        scores = [45, 55, 65, 72, 80]
        
        fig = px.line(x=months, y=scores, title='پێشکەوتنی فێربوون',
                     labels={'x': 'مانگ', 'y': 'نمرە'})
        st.plotly_chart(fig, use_container_width=True)

# پەڕەی فارماکۆلۆجی
elif page == "💊 فارماکۆلۆجی":
    st.markdown("## 💊 فارماکۆلۆجی و دەرمانناسی")
    
    drug_categories = {
        "دژە پەستانی خوێن": {
            "دەرمانەکان": {
                "کاپتۆپریل": {"ڕێژە": "25-50mg", "میکانیزم": "ACE inhibitor", "کاریگەری لاوەکی": "کۆخە"},
                "ئەملۆدیپین": {"ڕێژە": "5-10mg", "میکانیزم": "Calcium channel blocker", "کاریگەری لاوەکی": "ئاوسانی قاچ"}
            }
        },
        "دژە شەکرە": {
            "دەرمانەکان": {
                "مێتفۆرمین": {"ڕێژە": "500-2000mg", "میکانیزم": "Biguanide", "کاریگەری لاوەکی": "سکچوون"},
                "گلیپیزاید": {"ڕێژە": "5-20mg", "میکانیزم": "Sulfonylurea", "کاریگەری لاوەکی": "هایپۆگلایسیمیا"}
            }
        }
    }
    
    selected_category = st.selectbox("پۆلێنی دەرمان:", list(drug_categories.keys()))
    
    if selected_category:
        for drug, info in drug_categories[selected_category]["دەرمانەکان"].items():
            with st.expander(f"💊 {drug}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**ڕێژە:** {info['ڕێژە']}")
                    st.markdown(f"**میکانیزم:** {info['میکانیزم']}")
                with col2:
                    st.markdown(f"**کاریگەری لاوەکی:** {info['کاریگەری لاوەکی']}")

# فووەتەر
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea, #764ba2); color: white; border-radius: 15px;">
    <h3>🎓 ڕاهێنەری پزیشکی - Medical Training Simulator</h3>
    <p>بۆ خوێندکارانی پزیشکی - ببە پزیشکێکی لێهاتوو</p>
    <p style="font-size: 0.8rem;">© 2024 | وەشانی 1.0.0</p>
</div>
""", unsafe_allow_html=True)
