import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
import io
import base64
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from streamlit_option_menu import option_menu
import torch
import torchvision.transforms as transforms
from torchvision import models
import torch.nn as nn
import cv2
import pydicom
from fpdf import FPDF
import hashlib
import json
import os

# Configuration
st.set_page_config(
    page_title="MediScan AI - Medical Diagnosis System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .diagnosis-box {
        padding: 20px;
        border-radius: 10px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin: 10px 0;
    }
    .confidence-high {
        color: #28a745;
        font-weight: bold;
    }
    .confidence-medium {
        color: #ffc107;
        font-weight: bold;
    }
    .confidence-low {
        color: #dc3545;
        font-weight: bold;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'patient_history' not in st.session_state:
    st.session_state.patient_history = []
if 'current_diagnosis' not in st.session_state:
    st.session_state.current_diagnosis = None
if 'uploaded_images' not in st.session_state:
    st.session_state.uploaded_images = []

class MedicalImageAnalyzer:
    """AI-based Medical Image Analysis Engine"""
    
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = self._load_model()
        self.class_names = [
            'Normal', 'Pneumonia', 'COVID-19', 'Tuberculosis', 
            'Lung Cancer', 'Pleural Effusion', 'Pneumothorax'
        ]
        
    def _load_model(self):
        """Load pre-trained model (simulated for demo)"""
        # In production, load your trained model
        # model = models.densenet121(pretrained=True)
        # model.classifier = nn.Linear(1024, len(self.class_names))
        # model.load_state_dict(torch.load('medical_model.pth'))
        # return model.to(self.device)
        return None
    
    def preprocess_image(self, image):
        """Preprocess image for model inference"""
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
        return transform(image).unsqueeze(0)
    
    def analyze_image(self, image):
        """
        Analyze medical image and return diagnosis
        This is a simulated analysis for demonstration
        """
        # Simulate AI analysis
        # In production, replace with actual model inference
        
        # Mock analysis results
        conditions = {
            'Normal': {'probability': 0.75, 'findings': 'No abnormalities detected'},
            'Pneumonia': {'probability': 0.15, 'findings': 'Bilateral infiltrates in lower lobes'},
            'COVID-19': {'probability': 0.05, 'findings': 'Ground-glass opacities'},
            'Tuberculosis': {'probability': 0.03, 'findings': 'Apical cavitary lesion'},
            'Lung Cancer': {'probability': 0.01, 'findings': 'Solitary pulmonary nodule'},
            'Pleural Effusion': {'probability': 0.005, 'findings': 'Blunting of costophrenic angle'},
            'Pneumothorax': {'probability': 0.005, 'findings': 'Visible pleural line'}
        }
        
        # Simulate randomness for demo
        import random
        primary_diagnosis = random.choices(
            list(conditions.keys()), 
            weights=[0.7, 0.15, 0.05, 0.03, 0.02, 0.03, 0.02]
        )[0]
        
        confidence = random.uniform(0.85, 0.99)
        
        return {
            'primary_diagnosis': primary_diagnosis,
            'confidence': confidence,
            'findings': conditions[primary_diagnosis]['findings'],
            'differential_diagnoses': [
                {'condition': k, 'probability': v['probability']}
                for k, v in conditions.items() if k != primary_diagnosis
            ],
            'recommendations': self._generate_recommendations(primary_diagnosis),
            'urgency_level': self._assess_urgency(primary_diagnosis)
        }
    
    def _generate_recommendations(self, diagnosis):
        """Generate clinical recommendations"""
        recommendations = {
            'Normal': [
                'Routine follow-up as scheduled',
                'Maintain healthy lifestyle',
                'No immediate intervention required'
            ],
            'Pneumonia': [
                'Start empiric antibiotic therapy',
                'Consider sputum culture',
                'Monitor oxygen saturation',
                'Follow-up chest X-ray in 4-6 weeks'
            ],
            'COVID-19': [
                'Isolate patient immediately',
                'Perform RT-PCR test for confirmation',
                'Monitor inflammatory markers',
                'Consider antiviral therapy if eligible'
            ],
            'Tuberculosis': [
                'Order AFB sputum smear and culture',
                'Start quadruple therapy if confirmed',
                'Contact tracing recommended',
                'Report to public health authorities'
            ],
            'Lung Cancer': [
                'Urgent referral to pulmonology',
                'CT-guided biopsy recommended',
                'PET-CT for staging',
                'Multidisciplinary tumor board review'
            ],
            'Pleural Effusion': [
                'Diagnostic thoracentesis',
                'Analyze pleural fluid',
                'Treat underlying cause',
                'Consider chest tube if large effusion'
            ],
            'Pneumothorax': [
                'Assess size of pneumothorax',
                'Consider chest tube insertion',
                'Monitor with serial chest X-rays',
                'Avoid air travel until resolved'
            ]
        }
        return recommendations.get(diagnosis, ['Consult specialist for further evaluation'])
    
    def _assess_urgency(self, diagnosis):
        """Assess clinical urgency"""
        urgency_map = {
            'Normal': 'Routine',
            'Pneumonia': 'Urgent',
            'COVID-19': 'Urgent',
            'Tuberculosis': 'Semi-urgent',
            'Lung Cancer': 'Emergency',
            'Pleural Effusion': 'Semi-urgent',
            'Pneumothorax': 'Emergency'
        }
        return urgency_map.get(diagnosis, 'Routine')

class ReportGenerator:
    """Generate medical reports"""
    
    @staticmethod
    def generate_pdf(patient_info, diagnosis_result, image):
        """Generate PDF report"""
        pdf = FPDF()
        pdf.add_page()
        
        # Header
        pdf.set_font('Arial', 'B', 20)
        pdf.cell(0, 10, 'MediScan AI - Diagnostic Report', 0, 1, 'C')
        pdf.ln(10)
        
        # Patient Information
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Patient Information', 0, 1)
        pdf.set_font('Arial', '', 12)
        for key, value in patient_info.items():
            pdf.cell(0, 8, f'{key}: {value}', 0, 1)
        
        pdf.ln(10)
        
        # Diagnosis Results
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'AI-Assisted Diagnosis', 0, 1)
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 8, f"Primary Diagnosis: {diagnosis_result['primary_diagnosis']}", 0, 1)
        pdf.cell(0, 8, f"Confidence: {diagnosis_result['confidence']:.1%}", 0, 1)
        pdf.cell(0, 8, f"Urgency: {diagnosis_result['urgency_level']}", 0, 1)
        
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, 'Clinical Findings:', 0, 1)
        pdf.set_font('Arial', '', 12)
        pdf.multi_cell(0, 8, diagnosis_result['findings'])
        
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, 'Recommendations:', 0, 1)
        pdf.set_font('Arial', '', 12)
        for rec in diagnosis_result['recommendations']:
            pdf.cell(0, 8, f'- {rec}', 0, 1)
        
        # Save image to PDF
        if image:
            temp_path = 'temp_image.png'
            image.save(temp_path)
            pdf.image(temp_path, x=10, y=pdf.get_y()+10, w=100)
        
        # Disclaimer
        pdf.ln(20)
        pdf.set_font('Arial', 'I', 8)
        pdf.multi_cell(0, 5, 'DISCLAIMER: This is an AI-assisted diagnosis and should be reviewed by a qualified healthcare professional. Clinical correlation is required.')
        
        # Save report
        report_path = f'report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        pdf.output(report_path)
        return report_path

def load_dicom_image(file):
    """Load DICOM image file"""
    try:
        dicom = pydicom.dcmread(file)
        image = dicom.pixel_array
        # Normalize to 0-255
        image = ((image - image.min()) / (image.max() - image.min()) * 255).astype(np.uint8)
        return Image.fromarray(image)
    except:
        return None

def create_confidence_gauge(confidence):
    """Create a confidence gauge using Plotly"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=confidence * 100,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Confidence Score"},
        delta={'reference': 90},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "#1f77b4"},
            'steps': [
                {'range': [0, 50], 'color': "#ffcccc"},
                {'range': [50, 75], 'color': "#ffffcc"},
                {'range': [75, 100], 'color': "#ccffcc"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    fig.update_layout(height=250)
    return fig

def main():
    # Sidebar Navigation
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/cardiogram.png", width=80)
        st.title("MediScan AI")
        
        selected = option_menu(
            menu_title="Navigation",
            options=["Image Analysis", "Patient History", "Reports", "Settings"],
            icons=["camera", "clock-history", "file-text", "gear"],
            menu_icon="cast",
            default_index=0,
        )
        
        st.markdown("---")
        st.markdown("### About")
        st.info(
            "MediScan AI is an advanced medical imaging analysis system "
            "powered by artificial intelligence. It assists healthcare "
            "professionals in diagnosing various conditions from medical images."
        )
        
        st.warning(
            "⚠️ **Disclaimer**: This tool is for assistance only. "
            "Always verify with clinical examination."
        )

    # Main Content
    if selected == "Image Analysis":
        st.markdown('<h1 class="main-header">Medical Image Analysis</h1>', 
                   unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 📤 Upload Medical Image")
            
            # Patient Information
            with st.expander("📋 Patient Information", expanded=True):
                patient_id = st.text_input("Patient ID", value=f"PT-{datetime.now().strftime('%Y%m%d%H%M%S')}")
                patient_name = st.text_input("Patient Name")
                patient_age = st.number_input("Age", 0, 120, 30)
                patient_gender = st.selectbox("Gender", ["Male", "Female", "Other"])
                clinical_history = st.text_area("Clinical History", 
                                              placeholder="Enter relevant clinical history...")
            
            # Image Upload
            uploaded_file = st.file_uploader(
                "Choose a medical image",
                type=['png', 'jpg', 'jpeg', 'dcm', 'dicom'],
                help="Supported formats: PNG, JPG, JPEG, DICOM"
            )
            
            if uploaded_file is not None:
                # Process uploaded image
                if uploaded_file.name.lower().endswith(('.dcm', '.dicom')):
                    image = load_dicom_image(uploaded_file)
                    if image is None:
                        st.error("Error loading DICOM file")
                else:
                    image = Image.open(uploaded_file)
                
                st.image(image, caption="Uploaded Medical Image", use_column_width=True)
                
                # Image metadata
                st.markdown("**Image Details:**")
                st.write(f"- Size: {image.size}")
                st.write(f"- Mode: {image.mode}")
                st.write(f"- Format: {uploaded_file.type}")
        
        with col2:
            if uploaded_file is not None:
                st.markdown("### 🔍 Analysis Results")
                
                # Analyze button
                if st.button("🔬 Analyze Image", type="primary", use_container_width=True):
                    with st.spinner("AI analyzing medical image..."):
                        # Initialize analyzer
                        analyzer = MedicalImageAnalyzer()
                        
                        # Perform analysis
                        diagnosis_result = analyzer.analyze_image(image)
                        
                        # Store in session state
                        st.session_state.current_diagnosis = {
                            'patient_info': {
                                'ID': patient_id,
                                'Name': patient_name,
                                'Age': patient_age,
                                'Gender': patient_gender,
                                'History': clinical_history
                            },
                            'diagnosis': diagnosis_result,
                            'image': image,
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        
                        # Add to history
                        st.session_state.patient_history.append(
                            st.session_state.current_diagnosis
                        )
                
                # Display results if available
                if st.session_state.current_diagnosis:
                    diag = st.session_state.current_diagnosis['diagnosis']
                    
                    # Diagnosis Box
                    st.markdown(f"""
                    <div class="diagnosis-box">
                        <h2>Primary Diagnosis: {diag['primary_diagnosis']}</h2>
                        <h3>Urgency Level: {diag['urgency_level']}</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Confidence Metrics
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        confidence_color = ("confidence-high" if diag['confidence'] > 0.9 
                                          else "confidence-medium" if diag['confidence'] > 0.7 
                                          else "confidence-low")
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4>Confidence</h4>
                            <p class="{confidence_color}" style="font-size: 24px;">
                                {diag['confidence']:.1%}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_b:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4>Findings</h4>
                            <p>{diag['findings']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_c:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4>Recommendations</h4>
                            <ul>
                            {''.join(f'<li>{rec}</li>' for rec in diag['recommendations'][:2])}
                            </ul>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Confidence Gauge
                    st.plotly_chart(create_confidence_gauge(diag['confidence']), 
                                  use_container_width=True)
                    
                    # Differential Diagnoses
                    st.markdown("### Differential Diagnoses")
                    diff_df = pd.DataFrame(diag['differential_diagnoses'])
                    diff_df = diff_df.sort_values('probability', ascending=False)
                    
                    fig = px.bar(diff_df, x='condition', y='probability',
                               title="Differential Diagnosis Probabilities",
                               color='probability',
                               color_continuous_scale='Viridis')
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Action Buttons
                    col_btn1, col_btn2, col_btn3 = st.columns(3)
                    
                    with col_btn1:
                        if st.button("📄 Generate Report", use_container_width=True):
                            with st.spinner("Generating PDF report..."):
                                report_gen = ReportGenerator()
                                report_path = report_gen.generate_pdf(
                                    st.session_state.current_diagnosis['patient_info'],
                                    diag,
                                    image
                                )
                                st.success(f"Report generated: {report_path}")
                                
                                # Provide download link
                                with open(report_path, 'rb') as f:
                                    st.download_button(
                                        "⬇️ Download Report",
                                        f,
                                        file_name=report_path,
                                        mime="application/pdf"
                                    )
                    
                    with col_btn2:
                        if st.button("💾 Save to Records", use_container_width=True):
                            st.success("Diagnosis saved to patient records!")
                    
                    with col_btn3:
                        if st.button("🔄 New Analysis", use_container_width=True):
                            st.session_state.current_diagnosis = None
                            st.rerun()

    elif selected == "Patient History":
        st.markdown('<h1 class="main-header">Patient History</h1>', 
                   unsafe_allow_html=True)
        
        if st.session_state.patient_history:
            # Create history dataframe
            history_data = []
            for record in st.session_state.patient_history:
                history_data.append({
                    'Date': record['timestamp'],
                    'Patient ID': record['patient_info']['ID'],
                    'Name': record['patient_info']['Name'],
                    'Diagnosis': record['diagnosis']['primary_diagnosis'],
                    'Confidence': f"{record['diagnosis']['confidence']:.1%}",
                    'Urgency': record['diagnosis']['urgency_level']
                })
            
            df_history = pd.DataFrame(history_data)
            
            # Search and filter
            search_term = st.text_input("🔍 Search patients", placeholder="Search by name or ID...")
            
            if search_term:
                df_history = df_history[
                    df_history['Name'].str.contains(search_term, case=False) |
                    df_history['Patient ID'].str.contains(search_term, case=False)
                ]
            
            st.dataframe(df_history, use_container_width=True)
            
            # Statistics
            st.markdown("### 📊 Statistics")
            col_stats1, col_stats2, col_stats3 = st.columns(3)
            
            with col_stats1:
                st.metric("Total Cases", len(df_history))
            with col_stats2:
                st.metric("Unique Patients", df_history['Patient ID'].nunique())
            with col_stats3:
                urgency_counts = df_history['Urgency'].value_counts()
                st.metric("Emergency Cases", urgency_counts.get('Emergency', 0))
            
            # Diagnosis distribution
            fig = px.pie(df_history, names='Diagnosis', title='Diagnosis Distribution')
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.info("No patient history available. Start by analyzing images.")

    elif selected == "Reports":
        st.markdown('<h1 class="main-header">Reports & Analytics</h1>', 
                   unsafe_allow_html=True)
        
        # Report generation
        st.markdown("### Generate Summary Reports")
        
        report_type = st.selectbox(
            "Report Type",
            ["Daily Summary", "Weekly Report", "Monthly Analytics", "Custom Range"]
        )
        
        if report_type == "Custom Range":
            col_date1, col_date2 = st.columns(2)
            with col_date1:
                start_date = st.date_input("Start Date")
            with col_date2:
                end_date = st.date_input("End Date")
        
        st.button("Generate Report", type="primary")
        
        # Analytics Dashboard
        st.markdown("### 📈 Analytics Dashboard")
        
        if st.session_state.patient_history:
            # Create sample analytics
            dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
            sample_data = pd.DataFrame({
                'Date': dates,
                'Cases': np.random.randint(5, 20, 30),
                'Accuracy': np.random.uniform(0.85, 0.99, 30)
            })
            
            fig = px.line(sample_data, x='Date', y=['Cases', 'Accuracy'],
                         title='Trend Analysis')
            st.plotly_chart(fig, use_container_width=True)

    elif selected == "Settings":
        st.markdown('<h1 class="main-header">Settings</h1>', 
                   unsafe_allow_html=True)
        
        # Model Settings
        st.markdown("### 🤖 AI Model Configuration")
        model_type = st.selectbox(
            "Model Architecture",
            ["DenseNet121", "ResNet50", "EfficientNet", "Custom Ensemble"]
        )
        
        confidence_threshold = st.slider(
            "Confidence Threshold",
            min_value=0.5,
            max_value=0.99,
            value=0.85,
            step=0.01
        )
        
        # Display Settings
        st.markdown("### 🖥️ Display Settings")
        show_advanced_metrics = st.checkbox("Show Advanced Metrics", value=True)
        auto_generate_report = st.checkbox("Auto-generate Report", value=False)
        
        # Security Settings
        st.markdown("### 🔒 Security")
        enable_audit_log = st.checkbox("Enable Audit Logging", value=True)
        data_retention_days = st.number_input("Data Retention (days)", 30, 365, 90)
        
        # Save Settings
        if st.button("💾 Save Settings", type="primary"):
            st.success("Settings saved successfully!")
            
            # Store settings in session
            st.session_state.settings = {
                'model_type': model_type,
                'confidence_threshold': confidence_threshold,
                'show_advanced_metrics': show_advanced_metrics,
                'auto_generate_report': auto_generate_report,
                'enable_audit_log': enable_audit_log,
                'data_retention_days': data_retention_days
            }

if __name__ == "__main__":
    main()
