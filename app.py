import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import time

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="Medical Health Analyzer",
    page_icon=":hospital:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for better styling ---
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #0066cc;
    }
    .css-18e3th9 {
        padding-top: 0rem;
    }
    .stButton > button {
        background-color: #0066cc;
        color: white;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- Load and Train Model (Cached) ---
@st.cache_resource
def train_model():
    try:
        url = "https://raw.githubusercontent.com/jbrownlee/Datasets/master/pima-indians-diabetes.data.csv"
        columns = ['pregnancies', 'glucose', 'blood_pressure', 'skin_thickness', 'insulin', 'bmi', 'dpf', 'age', 'outcome']
        df = pd.read_csv(url, names=columns)
    except:
        st.error("Could not fetch dataset. Please check your internet connection.")
        return None, None, None

    # Prepare data
    X = df.drop('outcome', axis=1)
    y = df['outcome']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=150, random_state=42, max_depth=5)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    return model, accuracy, df

model, accuracy, df = train_model()

# --- Sidebar Navigation ---
st.sidebar.title("🏥 HealthGuard AI")
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2966/2966327.png", width=100)
page = st.sidebar.radio(
    "Menu",
    ["Home", "Diabetes Predictor", "Dataset Info", "About"]
)

# --- Home Page ---
if page == "Home":
    st.title("🧠 Welcome to HealthGuard AI")
    st.markdown("""
    This application utilizes **Machine Learning** to help assess the risk of diabetes based on diagnostic measurements.

    **What you can do here:**
    - ✅ Predict your risk of diabetes using our trained AI model.
    - 📊 Visualize important health metrics.
    - 🔬 Understand which factors contribute most to diabetes.

    ---
    **⚠️ Medical Disclaimer:**
    The content provided here is for informational purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or another qualified health provider with any questions you may have regarding a medical condition.
    """)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Model Accuracy", f"{accuracy:.2%}" if accuracy else "N/A")
    with col2:
        st.metric("Dataset Size", len(df) if df is not None else "N/A")
    with col3:
        st.metric("Features", "8")

# --- Diabetes Predictor Page ---
elif page == "Diabetes Predictor":
    st.title("🩺 Diabetes Risk Assessment")
    st.markdown("Please fill in the following health parameters:")

    with st.form(key="health_form"):
        col1, col2 = st.columns(2)

        with col1:
            pregnancies = st.number_input("Pregnancies", min_value=0, max_value=20, value=1, help="Number of times pregnant")
            glucose = st.number_input("Glucose (mg/dL)", min_value=0, max_value=300, value=100, help="Plasma glucose concentration")
            blood_pressure = st.number_input("Blood Pressure (mm Hg)", min_value=0, max_value=200, value=70, help="Diastolic blood pressure")
            skin_thickness = st.number_input("Skin Thickness (mm)", min_value=0, max_value=100, value=20, help="Triceps skin fold thickness")

        with col2:
            insulin = st.number_input("Insulin (μU/mL)", min_value=0, max_value=900, value=30, help="2-Hour serum insulin")
            bmi = st.number_input("BMI (kg/m²)", min_value=0.0, max_value=70.0, value=25.0, step=0.1, help="Body mass index")
            dpf = st.number_input("Diabetes Pedigree Function", min_value=0.0, max_value=3.0, value=0.5, step=0.01, help="Diabetes pedigree function")
            age = st.number_input("Age (years)", min_value=1, max_value=120, value=30, help="Age in years")

        submit_button = st.form_submit_button(label="🔬 Predict Diabetes Risk")

    if submit_button:
        if model is None:
            st.error("Model not loaded. Please check the Home page.")
        else:
            input_data = np.array([[pregnancies, glucose, blood_pressure, skin_thickness, insulin, bmi, dpf, age]])

            with st.spinner('Analyzing your health data...'):
                time.sleep(1)
                prediction = model.predict(input_data)
                prediction_proba = model.predict_proba(input_data)[0]

                st.subheader("Prediction Result")

                col1, col2 = st.columns(2)

                if prediction[0] == 0:
                    col1.success("✅ Non-Diabetic")
                    col1.metric("Confidence", f"{prediction_proba[0]:.2%}")
                    col2.info("Your current metrics suggest a low risk of diabetes. Keep maintaining a healthy lifestyle!")
                else:
                    col1.error("⚠️ Diabetic (High Risk)")
                    col1.metric("Confidence", f"{prediction_proba[1]:.2%}")
                    col2.warning("Your metrics suggest a high risk of diabetes. Please consult a healthcare professional for proper diagnosis.")

                # Show feature importance
                st.subheader("📊 Feature Importance in Prediction")
                feature_names = ['Pregnancies', 'Glucose', 'Blood Pressure', 'Skin Thickness', 'Insulin', 'BMI', 'DPF', 'Age']
                importance_data = model.feature_importances_

                importance_df = pd.DataFrame({
                    'Feature': feature_names,
                    'Importance': importance_data
                }).sort_values(by='Importance', ascending=False)

                st.bar_chart(importance_df.set_index('Feature'))

# --- Dataset Info Page ---
elif page == "Dataset Info":
    st.title("📋 Pima Indians Diabetes Database")
    if df is not None:
        st.markdown("This dataset was hosted by the National Institute of Diabetes and Digestive and Kidney Diseases.")
        st.dataframe(df.head(20))
        st.subheader("Statistical Summary")
        st.write(df.describe())
    else:
        st.warning("Dataset not available.")

# --- About Page ---
elif page == "About":
    st.title("ℹ️ About This Application")
    st.markdown("""
    **Technology Stack:**
    - **Frontend:** Streamlit 🎈
    - **Model:** Random Forest Classifier 🌲
    - **Dataset:** Pima Indians Diabetes Database

    **Developer:** Created for medical data science education.
    """)
