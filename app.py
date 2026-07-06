import streamlit as st
import pandas as pd
from datetime import datetime, date
import sqlite3
import plotly.express as px
import plotly.graph_objects as go

# Set page config with Kurdish title
st.set_page_config(
    page_title="Dr. Danyal - سیستەمی بەڕێوەبردنی نەخۆش",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for RTL support and styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@400;700&display=swap');
    
    * {
        font-family: 'Noto Sans Arabic', sans-serif;
    }
    
    .main-title {
        text-align: center;
        color: #1f77b4;
        font-size: 2.5em;
        margin-bottom: 30px;
        direction: rtl;
    }
    
    .card {
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        background-color: white;
        margin: 10px 0;
        direction: rtl;
    }
    
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        border-radius: 5px;
        padding: 10px;
        font-size: 16px;
    }
    
    .stButton>button:hover {
        background-color: #145a8c;
    }
    
    .delete-button>button {
        background-color: #dc3545;
    }
    
    .delete-button>button:hover {
        background-color: #c82333;
    }
    
    .rtl {
        direction: rtl;
        text-align: right;
    }
</style>
""", unsafe_allow_html=True)

# Initialize database
def init_database():
    conn = sqlite3.connect('dr_danyal.db')
    c = conn.cursor()
    
    # Patients table
    c.execute('''CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER,
        gender TEXT,
        phone TEXT,
        address TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Tests/Checkups table
    c.execute('''CREATE TABLE IF NOT EXISTS tests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        test_name TEXT NOT NULL,
        test_date DATE NOT NULL,
        result TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES patients (id)
    )''')
    
    # Medications table
    c.execute('''CREATE TABLE IF NOT EXISTS medications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        medication_name TEXT NOT NULL,
        dosage TEXT,
        frequency TEXT,
        start_date DATE,
        end_date DATE,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES patients (id)
    )''')
    
    conn.commit()
    return conn

# Database functions
def add_patient(conn, name, age, gender, phone, address):
    c = conn.cursor()
    c.execute("INSERT INTO patients (name, age, gender, phone, address) VALUES (?, ?, ?, ?, ?)",
              (name, age, gender, phone, address))
    conn.commit()
    return c.lastrowid

def get_all_patients(conn):
    return pd.read_sql_query("SELECT * FROM patients ORDER BY created_at DESC", conn)

def update_patient(conn, patient_id, name, age, gender, phone, address):
    c = conn.cursor()
    c.execute("""UPDATE patients 
                 SET name=?, age=?, gender=?, phone=?, address=? 
                 WHERE id=?""",
              (name, age, gender, phone, address, patient_id))
    conn.commit()

def delete_patient(conn, patient_id):
    c = conn.cursor()
    c.execute("DELETE FROM tests WHERE patient_id=?", (patient_id,))
    c.execute("DELETE FROM medications WHERE patient_id=?", (patient_id,))
    c.execute("DELETE FROM patients WHERE id=?", (patient_id,))
    conn.commit()

def add_test(conn, patient_id, test_name, test_date, result, notes):
    c = conn.cursor()
    c.execute("""INSERT INTO tests (patient_id, test_name, test_date, result, notes) 
                 VALUES (?, ?, ?, ?, ?)""",
              (patient_id, test_name, test_date, result, notes))
    conn.commit()

def get_patient_tests(conn, patient_id):
    return pd.read_sql_query(
        "SELECT * FROM tests WHERE patient_id=? ORDER BY test_date DESC", 
        conn, params=(patient_id,)
    )

def update_test(conn, test_id, test_name, test_date, result, notes):
    c = conn.cursor()
    c.execute("""UPDATE tests 
                 SET test_name=?, test_date=?, result=?, notes=? 
                 WHERE id=?""",
              (test_name, test_date, result, notes, test_id))
    conn.commit()

def delete_test(conn, test_id):
    c = conn.cursor()
    c.execute("DELETE FROM tests WHERE id=?", (test_id,))
    conn.commit()

def add_medication(conn, patient_id, medication_name, dosage, frequency, start_date, end_date, notes):
    c = conn.cursor()
    c.execute("""INSERT INTO medications (patient_id, medication_name, dosage, frequency, start_date, end_date, notes) 
                 VALUES (?, ?, ?, ?, ?, ?, ?)""",
              (patient_id, medication_name, dosage, frequency, start_date, end_date, notes))
    conn.commit()

def get_patient_medications(conn, patient_id):
    return pd.read_sql_query(
        "SELECT * FROM medications WHERE patient_id=? ORDER BY start_date DESC", 
        conn, params=(patient_id,)
    )

def update_medication(conn, med_id, medication_name, dosage, frequency, start_date, end_date, notes):
    c = conn.cursor()
    c.execute("""UPDATE medications 
                 SET medication_name=?, dosage=?, frequency=?, start_date=?, end_date=?, notes=? 
                 WHERE id=?""",
              (medication_name, dosage, frequency, start_date, end_date, notes, med_id))
    conn.commit()

def delete_medication(conn, med_id):
    c = conn.cursor()
    c.execute("DELETE FROM medications WHERE id=?", (med_id,))
    conn.commit()

# Main App
def main():
    # Initialize database
    conn = init_database()
    
    # Header
    st.markdown('<h1 class="main-title">🏥 Dr. Danyal - سیستەمی بەڕێوەبردنی نەخۆش</h1>', unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("📋 ناوەڕۆک")
    page = st.sidebar.radio(
        "لاپەڕەکان",
        ["👥 نەخۆشەکان", "🔬 پشکنینەکان", "💊 دەرمانەکان", "📊 داشبۆرد"]
    )
    
    # Patients Page
    if page == "👥 نەخۆشەکان":
        st.markdown("## 👥 بەڕێوەبردنی نەخۆشەکان")
        
        tab1, tab2 = st.tabs(["📝 زیادکردنی نەخۆش", "📋 لیستی نەخۆشەکان"])
        
        with tab1:
            with st.form("add_patient_form"):
                st.markdown("### نەخۆشێکی نوێ زیاد بکە")
                col1, col2 = st.columns(2)
                
                with col1:
                    name = st.text_input("ناوی نەخۆش *")
                    age = st.number_input("تەمەن", min_value=0, max_value=150, value=30)
                    gender = st.selectbox("ڕەگەز", ["نێر", "مێ"])
                
                with col2:
                    phone = st.text_input("ژمارەی تەلەفۆن")
                    address = st.text_area("ناونیشان")
                
                submitted = st.form_submit_button("➕ زیادکردنی نەخۆش")
                
                if submitted and name:
                    patient_id = add_patient(conn, name, age, gender, phone, address)
                    st.success(f"✅ نەخۆش بە سەرکەوتووی زیادکرا! (ID: {patient_id})")
                elif submitted and not name:
                    st.error("❌ تکایە ناوی نەخۆش بنووسە")
        
        with tab2:
            patients_df = get_all_patients(conn)
            
            if not patients_df.empty:
                st.markdown(f"### {len(patients_df)} نەخۆش تۆمارکراوە")
                
                for idx, patient in patients_df.iterrows():
                    with st.expander(f"{patient['name']} - {patient['age']} ساڵ"):
                        col1, col2, col3 = st.columns([3, 1, 1])
                        
                        with col1:
                            st.write(f"**تەمەن:** {patient['age']} | **ڕەگەز:** {patient['gender']}")
                            st.write(f"**تەلەفۆن:** {patient['phone']} | **ناونیشان:** {patient['address']}")
                        
                        with col2:
                            if st.button("✏️ دەستکاری", key=f"edit_{patient['id']}"):
                                st.session_state[f"editing_patient_{patient['id']}"] = True
                        
                        with col3:
                            if st.button("🗑️ سڕینەوە", key=f"delete_{patient['id']}"):
                                if st.warning("دڵنیایت دەتەوێت ئەم نەخۆشە بسڕیتەوە؟"):
                                    delete_patient(conn, patient['id'])
                                    st.success("نەخۆش سڕدرایەوە")
                                    st.rerun()
                        
                        # Edit form
                        if st.session_state.get(f"editing_patient_{patient['id']}", False):
                            st.markdown("---")
                            st.markdown("### ✏️ دەستکاری نەخۆش")
                            
                            with st.form(key=f"edit_form_{patient['id']}"):
                                e_col1, e_col2 = st.columns(2)
