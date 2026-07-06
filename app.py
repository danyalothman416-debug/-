import streamlit as st
import pandas as pd
import json
import os
from datetime import date, datetime
import plotly.express as px

# --- کۆنفیگریشن ---
st.set_page_config(
    page_title="سیستەمی بەڕێوەبردنی نەخۆشی - دکتۆر دانیال",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ناوی فایلی داتا ---
DATA_FILE = "patient_data.json"

# --- فەنکشنە سەرەکییەکان بۆ خەزن و خوێندنەوە ---
def load_data():
    """داتای نەخۆشەکان لە JSON دەخاتەوە"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # کۆنتڕۆڵی تایپ بۆ بەکارهێنەرانی کۆن
                if isinstance(data, dict):
                    return data
                else:
                    return {}
        except:
            return {}
    return {}

def save_data(data):
    """داتا دابین کەین بۆ JSON"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def init_session_state():
    """داتای سەشن دابین کەین"""
    if 'patients' not in st.session_state:
        st.session_state.patients = load_data()
    if 'current_patient' not in st.session_state:
        st.session_state.current_patient = None
    if 'view_mode' not in st.session_state:
        st.session_state.view_mode = 'dashboard' # dashboard, add_record, history

# --- فەنکشنە یارمەتییەکان ---
def add_patient(name, age, gender, phone, notes):
    patient_id = str(len(st.session_state.patients) + 1) + "_" + datetime.now().strftime("%Y%m%d%H%M%S")
    st.session_state.patients[patient_id] = {
        "info": {
            "name": name, "age": age, "gender": gender, "phone": phone, "notes": notes,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        },
        "records": [] # لیستی پشکنین/دەرمان
    }
    save_data(st.session_state.patients)
    return patient_id

def add_record(patient_id, record_type, date_val, title, details, medication="", dosage="", med_notes=""):
    record = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
        "type": record_type, # 'checkup' أو 'medication'
        "date": str(date_val),
        "title": title,
        "details": details,
        "medication": medication,
        "dosage": dosage,
        "med_notes": med_notes,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    st.session_state.patients[patient_id]["records"].append(record)
    # داڕێژە بەپێی بەروار
    st.session_state.patients[patient_id]["records"].sort(key=lambda x: x['date'], reverse=True)
    save_data(st.session_state.patients)

def update_record(patient_id, record_id, updated_fields):
    for i, rec in enumerate(st.session_state.patients[patient_id]["records"]):
        if rec["id"] == record_id:
            st.session_state.patients[patient_id]["records"][i].update(updated_fields)
            save_data(st.session_state.patients)
            return True
    return False

def delete_record(patient_id, record_id):
    st.session_state.patients[patient_id]["records"] = [
        r for r in st.session_state.patients[patient_id]["records"] if r["id"] != record_id
    ]
    save_data(st.session_state.patients)

# --- جیاکەرە ڕووەکە (UI Components) ---

def sidebar_ui():
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3774/3774299.png", width=100)
        st.title("🩺 دکتۆر دانیال")
        st.caption("سیستەمی بەڕێوەبردنی نەخۆشی")
        st.divider()
        
        # هەڵبژاردنی نەخۆش
        patient_names = {pid: p['info']['name'] for pid, p in st.session_state.patients.items()}
        
        if not patient_names:
            st.info("هەڵە بۆ زیادکردنی نەخۆشی نوێ کلیک بکە")
        else:
            selected_name = st.selectbox(
                "🔍 هەڵبژاردنەوەی نەخۆش", 
                options=list(patient_names.values()),
                index=list(patient_names.values()).index(st.session_state.current_patient['info']['name']) if st.session_state.current_patient and st.session_state.current_patient['info']['name'] in patient_names.values() else 0
            )
            # دۆزینەوەی ID
            selected_id = [pid for pid, name in patient_names.items() if name == selected_name][0]
            st.session_state.current_patient = {"id": selected_id, **st.session_state.patients[selected_id]}
            
            st.divider()
            st.subheader(f"👤 {selected_name}")
            info = st.session_state.current_patient['info']
            st.write(f"🎂 تەمەن: {info['age']}")
            st.write(f"⚧️ جینس: {info['gender']}")
            st.write(f"📞 تەلەفۆن: {info['phone']}")
            
            if st.button("➕ نەخۆشی نوێ", use_container_width=True, type="primary"):
                st.session_state.current_patient = None
                st.rerun()

        st.divider()
        st.markdown("---")
        st.caption("© 2024 Dr. Danyal System")

def dashboard_ui():
    if not st.session_state.current_patient:
        st.warning("تکایە نەخۆشێک هەڵبژێرە یان نوێ زیاد بکە لە پاکەڵەوە.")
        return

    p = st.session_state.current_patient
    records = p['records']
    
    # ----- هێدەر -----
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.header(f"📋 داشبۆردی: {p['info']['name']}")
    with col2:
        if st.button("➕ پشکنین/دەرمان نوێ", use_container_width=True, type="primary"):
            st.session_state.view_mode = 'add_record'
            st.rerun()
    with col3:
        if st.button("📜 مێژووی تەواو", use_container_width=True):
            st.session_state.view_mode = 'history'
            st.rerun()

    st.divider()

    # ----- کارتەстатистиک -----
    total_records = len(records)
    checkups = len([r for r in records if r['type'] == 'checkup'])
    meds = len([r for r in records if r['type'] == 'medication'])
    
    m1, m2, m3 = st.columns(3)
    m1.metric("کۆی گشتی", total_records)
    m2.metric("🩺 پشکنینەکان", checkups)
    m3.metric("💊 دەرمانەکان", meds)

    # ----- چارت (بەکارهێنانی Plotly) -----
    if records:
        df = pd.DataFrame(records)
        df['date'] = pd.to_datetime(df['date'])
        # گرووپکردن بەپێی بەروار و جۆر
        chart_data = df.groupby([df['date'].dt.date, 'type']).size().reset_index(name='count')
        fig = px.bar(chart_data, x='date', y='count', color='type', 
                     labels={'date': 'بەروار', 'count': 'ژمارە', 'type': 'جۆر'},
                     title="📊 بەراوردی پشکنین و دەرمان بەپێی بەروار",
                     color_discrete_map={'checkup': '#007bff', 'medication': '#28a745'})
        fig.update_layout(xaxis_title="", yaxis_title="ژمارە", legend_title_text='')
        st.plotly_chart(fig, use_container_width=True)

    # ----- دوایی تۆمارەکان (Last 5) -----
    st.subheader("🕒 دوایی تۆمارەکان")
    if not records:
        st.info("هێچ تۆمارێک نییە، تکایە یەکەم تۆمار زیاد بکە.")
    else:
        for rec in records[:5]:
            render_record_card(p['id'], rec, compact=True)

def add_record_ui():
    if not st.session_state.current_patient:
        st.warning("تکایە نەخۆشێک هەڵبژێرە")
        return

    p = st.session_state.current_patient
    st.header(f"➕ زیادکردنی تۆماری نوێ بۆ: {p['info']['name']}")
    
    if st.button("⬅️ بگەڕێوە بۆ داشبۆرد"):
        st.session_state.view_mode = 'dashboard'
        st.rerun()

    st.divider()
    
    tab1, tab2 = st.tabs(["🩺 پشکنینی ڕۆژانە (Check-up)", "💊 دەرمان (Medication)"])

    with tab1:
        with st.form("checkup_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                rec_date = st.date_input("📅 بەروار", value=date.today())
                title = st.text_input("📝 سەرناوی پشکنین", placeholder="مەبەست: پشکنینی ڕۆژانە، سەیرکردنی خۆون،...")
            with col2:
                pass # بۆ ڕێکخستن
            
            details = st.text_area("📋 وردی‌کاری و تێبینی پشکنین", height=150, placeholder="هەرچی دۆیت بنووسە: هەستەکان، دەرەنجامەکان، پێشنیار...")
            
            submitted = st.form_submit_button("💾 پاشەکەوتکردن", use_container_width=True, type="primary")
            if submitted:
                if title:
                    add_record(p['id'], 'checkup', rec_date, title, details)
                    st.success("پشکنین بە سەرکەوتوویی تۆمار کرا!")
                    st.session_state.view_mode = 'dashboard'
                    st.rerun()
                else:
                    st.error("تکایە سەرناو بنووسە")

    with tab2:
        with st.form("med_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                rec_date = st.date_input("📅 بەرواری دەستپێک", value=date.today(), key="med_date")
                med_name = st.text_input("💊 ناوی دەرمان", placeholder="مەبەست: Amoxicillin, Paracetamol...")
            with col2:
                dosage = st.text_input("📏 دۆز (Dosage)", placeholder="مەبەست: 500mg - 1x3 بۆ ٧ ڕۆژ")
                # duration = st.text_input("⏳ ماوە", placeholder="مەبەست: ٧ ڕۆژ")
            
            med_notes = st.text_area("📝 تێبینی دەرمان", height=100, placeholder="مەبەست: دوایەکە بەخۆش سەیر دەبێت، هەڵەبەندەکان...")
            details = st.text_area("🩺 ھۆکاری دابینکردن (Diagnosis/Reason)", height=100, 
