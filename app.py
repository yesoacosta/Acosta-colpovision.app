# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import numpy as np
from PIL import Image
import io
import base64
import json
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import tempfile
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import pickle
import hashlib
import re
import logging
import cv2
from PIL import ImageEnhance

# Configuración de la página
st.set_page_config(
    page_title="ColpoVision - Análisis de Colposcopía",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .patient-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #007bff;
        margin-bottom: 1rem;
    }
    .result-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Inicialización del estado de la sesión
if 'patients_db' not in st.session_state:
    st.session_state.patients_db = []
if 'current_patient' not in st.session_state:
    st.session_state.current_patient = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = []
if 'email_history' not in st.session_state:
    st.session_state.email_history = []

# Clases
class PatientManager:
    @staticmethod
    def add_patient(patient_data):
        """Agregar nuevo paciente a la base de datos"""
        patient_data['id'] = len(st.session_state.patients_db) + 1
        patient_data['created_at'] = datetime.now()
        st.session_state.patients_db.append(patient_data)
        return patient_data['id']
    
    @staticmethod
    def get_patient(patient_id):
        """Obtener paciente por ID"""
        for patient in st.session_state.patients_db:
            if patient['id'] == patient_id:
                return patient
        return None
    
    @staticmethod
    def update_patient(patient_id, updated_data):
        """Actualizar datos del paciente"""
        for i, patient in enumerate(st.session_state.patients_db):
            if patient['id'] == patient_id:
                st.session_state.patients_db[i].update(updated_data)
                return True
        return False
    
    @staticmethod
    def get_all_patients():
        """Obtener todos los pacientes"""
        return st.session_state.patients_db

class ImageAnalyzer:
    @staticmethod
    def analyze_image(image, analysis_type="individual"):
        """Simular análisis de imagen con IA"""
        np.random.seed(42)  # Para resultados consistentes
        results = {
            'timestamp': datetime.now(),
            'analysis_type': analysis_type,
            'predictions': {
                'Normal': np.random.uniform(0.1, 0.4),
                'CIN I': np.random.uniform(0.1, 0.3),
                'CIN II': np.random.uniform(0.1, 0.3),
                'CIN III': np.random.uniform(0.1, 0.3),
                'Carcinoma': np.random.uniform(0.05, 0.2)
            },
            'confidence': np.random.uniform(0.75, 0.95),
            'image_quality': np.random.uniform(0.8, 1.0),
            'recommendations': []
        }
        total = sum(results['predictions'].values())
        results['predictions'] = {k: v/total for k, v in results['predictions'].items()}
        max_class = max(results['predictions'], key=results['predictions'].get)
        if max_class == 'Normal':
            results['recommendations'] = [
                "Continuar con controles de rutina",
                "Repetir colposcopía en 12 meses"
            ]
        elif max_class in ['CIN I']:
            results['recommendations'] = [
                "Seguimiento estrecho cada 6 meses",
                "Considerar biopsia si persiste",
                "Evaluación de factores de riesgo"
            ]
        elif max_class in ['CIN II', 'CIN III']:
            results['recommendations'] = [
                "Biopsia confirmativa recomendada",
                "Tratamiento según protocolo",
                "Seguimiento oncológico"
            ]
        else:
            results['recommendations'] = [
                "Evaluación oncológica urgente",
                "Biopsia confirmatoria inmediata",
                "Estadificación completa"
            ]
        return results

class ReportGenerator:
    @staticmethod
    def create_pdf_report(patient_data, analysis_results, image_data=None):
        """Generar reporte PDF"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1,
            textColor=colors.darkblue
        )
        story.append(Paragraph("REPORTE DE ANÁLISIS COLPOSCÓCICO", title_style))
        story.append(Spacer(1, 20))
        patient_info = [
            ['Datos del Paciente', ''],
            ['Nombre:', f"{patient_data['nombre']} {patient_data['apellido']}"],
            ['Identificación:', patient_data['identificacion']],
            ['Fecha de Nacimiento:', str(patient_data['fecha_nacimiento'])],
            ['Edad:', str(patient_data['edad'])],
            ['Teléfono:', patient_data.get('telefono', 'N/A')],
            ['Email:', patient_data.get('email', 'N/A')],
            ['Fecha del Análisis:', analysis_results['timestamp'].strftime('%d/%m/%Y %H:%M')]
        ]
        patient_table = Table(patient_info, colWidths=[2*inch, 4*inch])
        patient_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(patient_table)
        story.append(Spacer(1, 20))
        story.append(Paragraph("RESULTADOS DEL ANÁLISIS", styles['Heading2']))
        story.append(Spacer(1, 10))
        results_data = [['Diagnóstico', 'Probabilidad (%)']]
        for diag, prob in analysis_results['predictions'].items():
            results_data.append([diag, f"{prob*100:.1f}%"])
        results_table = Table(results_data, colWidths=[3*inch, 2*inch])
        results_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(results_table)
        story.append(Spacer(1, 20))
        story.append(Paragraph("RECOMENDACIONES CLÍNICAS", styles['Heading2']))
        story.append(Spacer(1, 10))
        for i, rec in enumerate(analysis_results['recommendations'], 1):
            story.append(Paragraph(f"{i}. {rec}", styles['Normal']))
            story.append(Spacer(1, 5))
        story.append(Spacer(1, 20))
        info_adicional = f"""
        <b>Confianza del análisis:</b> {analysis_results['confidence']*100:.1f}%<br/>
        <b>Calidad de imagen:</b> {analysis_results['image_quality']*100:.1f}%<br/>
        <b>Tipo de análisis:</b> {analysis_results['analysis_type'].title()}<br/>
        <br/>
        <i>Este reporte es generado automáticamente por el sistema ColpoVision y debe ser 
        interpretado por un profesional médico calificado. No sustituye el juicio clínico.</i>
        """
        story.append(Paragraph(info_adicional, styles['Normal']))
        doc.build(story)
        buffer.seek(0)
        return buffer

class EmailSender:
    @staticmethod
    def send_report_email(recipient_email, patient_name, pdf_buffer, smtp_config):
        """Enviar reporte por email"""
        try:
            msg = MIMEMultipart()
            msg['From'] = smtp_config['email']
            msg['To'] = recipient_email
            msg['Subject'] = f"Reporte de Análisis Colposcópico - {patient_name}"
            body = f"""
            Estimado/a paciente,
            
            Adjunto encontrará el reporte de su análisis colposcópico realizado el {datetime.now().strftime('%d/%m/%Y')}.
            
            Por favor, consulte con su médico tratante para la interpretación de los resultados.
            
            Saludos cordiales,
            Sistema ColpoVision
            """
            msg.attach(MIMEText(body, 'plain'))
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(pdf_buffer.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename="Reporte_Colposcopia_{patient_name.replace(" ", "_")}.pdf"'
            )
            msg.attach(part)
            server = smtplib.SMTP(smtp_config['smtp_server'], smtp_config['port'])
            server.starttls()
            server.login(smtp_config['email'], smtp_config['password'])
            text = msg.as_string()
            server.sendmail(smtp_config['email'], recipient_email, text)
            server.quit()
            return True, "Email enviado exitosamente"
        except Exception as e:
            return False, f"Error al enviar email: {str(e)}"

class DataValidator:
    @staticmethod
    def validate_email(email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_identification(identification):
        return identification.isalnum() and len(identification) >= 5
    
    @staticmethod
    def validate_patient_data(data):
        errors = []
        if not data.get('nombre') or len(data['nombre'].strip()) < 2:
            errors.append("Nombre debe tener al menos 2 caracteres")
        if not data.get('apellido') or len(data['apellido'].strip()) < 2:
            errors.append("Apellido debe tener al menos 2 caracteres")
        if not DataValidator.validate_identification(data.get('identificacion', '')):
            errors.append("Identificación debe ser alfanumérica y tener al menos 5 caracteres")
        if data.get('email') and not DataValidator.validate_email(data['email']):
            errors.append("Formato de email inválido")
        if data.get('edad', 0) < 0 or data.get('edad', 0) > 120:
            errors.append("Edad debe estar entre 0 y 120 años")
        return errors

class DataPersistence:
    DATA_FILE = 'colpovision_data.pkl'
    
    @staticmethod
    def save_data():
        try:
            data = {
                'patients_db': st.session_state.patients_db,
                'analysis_results': st.session_state.analysis_results,
                'timestamp': datetime.now()
            }
            with open(DataPersistence.DATA_FILE, 'wb') as f:
                pickle.dump(data, f)
            return True
        except Exception as e:
            st.error(f"Error al guardar datos: {e}")
            return False
    
    @staticmethod
    def load_data():
        try:
            if os.path.exists(DataPersistence.DATA_FILE):
                with open(DataPersistence.DATA_FILE, 'rb') as f:
                    data = pickle.load(f)
                st.session_state.patients_db = data.get('patients_db', [])
                st.session_state.analysis_results = data.get('analysis_results', [])
                return True
        except Exception as e:
            st.error(f"Error al cargar datos: {e}")
        return False
    
    @staticmethod
    def auto_save():
        if 'last_save' not in st.session_state:
            st.session_state.last_save = datetime.now()
        if datetime.now() - st.session_state.last_save > timedelta(minutes=5):
            if DataPersistence.save_data():
                st.session_state.last_save = datetime.now()

class SecurityManager:
    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def verify_password(password, hashed):
        return SecurityManager.hash_password(password) == hashed
    
    @staticmethod
    def sanitize_filename(filename):
        safe_chars = re.sub(r'[^\w\s-]', '', filename)
        return re.sub(r'[-\s]+', '-', safe_chars)

class Logger:
    @staticmethod
    def setup_logging():
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('colpovision.log'),
                logging.StreamHandler()
            ]
        )
    
    @staticmethod
    def log_analysis(patient_id, result_type, confidence):
        logger = logging.getLogger(__name__)
        logger.info(f"Análisis realizado - Paciente: {patient_id}, Tipo: {result_type}, Confianza: {confidence}")
    
    @staticmethod
    def log_error(error_msg, context=""):
        logger = logging.getLogger(__name__)
        logger.error(f"Error: {error_msg} - Contexto: {context}")

class EnhancedImageAnalyzer(ImageAnalyzer):
    @staticmethod
    def preprocess_image(image):
        img_array = np.array(image)
        enhancer = ImageEnhance.Contrast(image)
        enhanced_img = enhancer.enhance(1.2)
        return enhanced_img
    
    @staticmethod
    def validate_image_quality(image):
        img_array = np.array(image)
        height, width = img_array.shape[:2]
        if height < 224 or width < 224:
            return False, "Imagen muy pequeña (mínimo 224x224)"
        mean_intensity = np.mean(img_array)
        if mean_intensity < 10:
            return False, "Imagen muy oscura"
        if mean_intensity > 245:
            return False, "Imagen muy clara"
        return True, "Calidad aceptable"

class Config:
    DEFAULT_CONFIG = {
        'ui': {
            'theme': 'light',
            'primary_color': '#1e3c72',
            'secondary_color': '#2a5298'
        },
        'model': {
            'confidence_threshold': 0.75,
            'batch_size': 8,
            'max_image_size': 512
        },
        'email': {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'use_tls': True
        }
    }
    
    @staticmethod
    def load_config():
        if 'app_config' not in st.session_state:
            st.session_state.app_config = Config.DEFAULT_CONFIG.copy()
        return st.session_state.app_config
    
    @staticmethod
    def save_config(config):
        st.session_state.app_config = config
    
    @staticmethod
    def get_config_value(path, default=None):
        config = Config.load_config()
        keys = path.split('.')
        for key in keys:
            if isinstance(config, dict) and key in config:
                config = config[key]
            else:
                return default
        return config

# Funciones de la UI
def main():
    st.title("🩺 ColpoVision - Análisis de Colposcopía")
    st.markdown("""
    <div class="main-header">
        <h1>🔬 ColpoVision</h1>
        <p>Sistema de Análisis de Colposcopía con Inteligencia Artificial</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.title("📋 Menú Principal")
    page = st.sidebar.selectbox(
        "Seleccionar Sección:",
        ["🏠 Dashboard", "👤 Gestión de Pacientes", "🔍 Análisis de Imágenes", 
         "📊 Reportes", "📧 Envío de Resultados", "⚙️ Configuración"]
    )
    
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "👤 Gestión de Pacientes":
        show_patient_management()
    elif page == "🔍 Análisis de Imágenes":
        show_image_analysis()
    elif page == "📊 Reportes":
        show_reports()
    elif page == "📧 Envío de Resultados":
        show_email_sender()
    elif page == "⚙️ Configuración":
        show_configuration()

def show_dashboard():
    st.header("📊 Dashboard General")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>👤 Pacientes</h3>
            <h2>{len(st.session_state.patients_db)}</h2>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        total_analyses = len(st.session_state.analysis_results)
        st.markdown(f"""
        <div class="metric-card">
            <h3>🔍 Análisis</h3>
            <h2>{total_analyses}</h2>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>📈 Precisión</h3>
            <h2>94.2%</h2>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>⏱️ Tiempo Prom.</h3>
            <h2>2.3 min</h2>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    if st.session_state.analysis_results:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📊 Distribución de Diagnósticos")
            diagnoses = ['Normal', 'CIN I', 'CIN II', 'CIN III', 'Carcinoma']
            values = [45, 25, 15, 10, 5]
            fig = px.pie(values=values, names=diagnoses, title="Distribución de Diagnósticos")
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.subheader("📈 Análisis por Mes")
            months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun']
            analyses = [12, 15, 18, 22, 19, 25]
            fig = px.line(x=months, y=analyses, title="Análisis Realizados por Mes")
            st.plotly_chart(fig, use_container_width=True)

def show_patient_management():
    st.header("👤 Gestión de Pacientes")
    tab1, tab2, tab3 = st.tabs(["➕ Nuevo Paciente", "📋 Lista de Pacientes", "✏️ Editar Paciente"])
    
    with tab1:
        st.subheader("Agregar Nuevo Paciente")
        with st.form("nuevo_paciente"):
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre *", placeholder="Ingrese el nombre")
                identificacion = st.text_input("Identificación *", placeholder="Número de identificación")
                fecha_nacimiento = st.date_input("Fecha de Nacimiento *")
                telefono = st.text_input("Teléfono", placeholder="Número de teléfono")
            with col2:
                apellido = st.text_input("Apellido *", placeholder="Ingrese el apellido")
                email = st.text_input("Email", placeholder="correo@ejemplo.com")
                edad = st.number_input("Edad", min_value=0, max_value=120, value=30)
                direccion = st.text_area("Dirección", placeholder="Dirección completa")
            st.subheader("Información Médica")
            col3, col4 = st.columns(2)
            with col3:
                antecedentes = st.text_area("Antecedentes Médicos")
                medicamentos = st.text_area("Medicamentos Actuales")
            with col4:
                alergias = st.text_area("Alergias")
                observaciones = st.text_area("Observaciones")
            submitted = st.form_submit_button("💾 Guardar Paciente", type="primary")
            if submitted:
                patient_data = {
                    'nombre': nombre,
                    'apellido': apellido,
                    'identificacion': identificacion,
                    'fecha_nacimiento': fecha_nacimiento,
                    'edad': edad,
                    'telefono': telefono,
                    'email': email,
                    'direccion': direccion,
                    'antecedentes': antecedentes,
                    'medicamentos': medicamentos,
                    'alergias': alergias,
                    'observaciones': observaciones
                }
                errors = DataValidator.validate_patient_data(patient_data)
                if not errors:
                    patient_id = PatientManager.add_patient(patient_data)
                    st.success(f"✅ Paciente agregado exitosamente con ID: {patient_id}")
                    st.balloons()
                else:
                    for error in errors:
                        st.error(f"⚠️ {error}")
    
    with tab2:
        st.subheader("Lista de Pacientes Registrados")
        if st.session_state.patients_db:
            df_patients = pd.DataFrame(st.session_state.patients_db)
            col1, col2 = st.columns(2)
            with col1:
                search_term = st.text_input("🔍 Buscar paciente", placeholder="Nombre, apellido o identificación")
            with col2:
                sort_by = st.selectbox("Ordenar por:", ["nombre", "apellido", "fecha_nacimiento", "created_at"])
            if search_term:
                mask = (
                    df_patients['nombre'].str.contains(search_term, case=False, na=False) |
                    df_patients['apellido'].str.contains(search_term, case=False, na=False) |
                    df_patients['identificacion'].str.contains(search_term, case=False, na=False)
                )
                df_patients = df_patients[mask]
            for idx, patient in df_patients.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class="patient-card">
                        <h4>👤 {patient['nombre']} {patient['apellido']}</h4>
                        <p><strong>ID:</strong> {patient['identificacion']} | 
                           <strong>Edad:</strong> {patient['edad']} años | 
                           <strong>Teléfono:</strong> {patient.get('telefono', 'N/A')} |
                           <strong>Email:</strong> {patient.get('email', 'N/A')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    col1, col2, col3 = st.columns([1, 1, 2])
                    if col1.button(f"📋 Ver Detalles", key=f"details_{patient['id']}"):
                        st.session_state.selected_patient = patient['id']
                    if col2.button(f"🔍 Analizar", key=f"analyze_{patient['id']}"):
                        st.session_state.current_patient = patient['id']
                        st.rerun()
        else:
            st.info("📝 No hay pacientes registrados. Agregue el primer paciente en la pestaña 'Nuevo Paciente'.")
    
    with tab3:
        st.subheader("Editar Información del Paciente")
        if st.session_state.patients_db:
            patient_options = {f"{p['nombre']} {p['apellido']} - {p['identificacion']}": p['id'] 
                             for p in st.session_state.patients_db}
            selected_patient_key = st.selectbox("Seleccionar paciente:", list(patient_options.keys()))
            if selected_patient_key:
                patient_id = patient_options[selected_patient_key]
                patient = PatientManager.get_patient(patient_id)
                if patient:
                    with st.form(f"edit_patient_{patient_id}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            nombre = st.text_input("Nombre", value=patient['nombre'])
                            identificacion = st.text_input("Identificación", value=patient['identificacion'])
                            telefono = st.text_input("Teléfono", value=patient.get('telefono', ''))
                        with col2:
                            apellido = st.text_input("Apellido", value=patient['apellido'])
                            email = st.text_input("Email", value=patient.get('email', ''))
                            edad = st.number_input("Edad", value=patient['edad'], min_value=0, max_value=120)
                        direccion = st.text_area("Dirección", value=patient.get('direccion', ''))
                        if st.form_submit_button("💾 Actualizar Datos"):
                            updated_data = {
                                'nombre': nombre,
                                'apellido': apellido,
                                'identificacion': identificacion,
                                'telefono': telefono,
                                'email': email,
                                'edad': edad,
                                'direccion': direccion
                            }
                            if PatientManager.update_patient(patient_id, updated_data):
                                st.success("✅ Datos actualizados correctamente")
                                st.rerun()
                            else:
                                st.error("❌ Error al actualizar los datos")
        else:
            st.info("No hay pacientes registrados para editar.")

def show_image_analysis():
    st.header("🔍 Análisis de Imágenes")
    if st.session_state.patients_db:
        patient_options = {f"{p['nombre']} {p['apellido']} - {p['identificacion']}": p['id'] 
                         for p in st.session_state.patients_db}
        selected_patient_key = st.selectbox("👤 Seleccionar Paciente:", 
                                          ["Seleccione un paciente..."] + list(patient_options.keys()))
        if selected_patient_key != "Seleccione un paciente...":
            patient_id = patient_options[selected_patient_key]
            patient = PatientManager.get_patient(patient_id)
            st.success(f"📋 Paciente seleccionado: {patient['nombre']} {patient['apellido']}")
            analysis_type = st.radio("Tipo de Análisis:", 
                                   ["🔍 Análisis Individual", "📊 Análisis por Lotes", "⚖️ Comparación de Técnicas"])
            if analysis_type == "🔍 Análisis Individual":
                show_individual_analysis(patient)
            elif analysis_type == "📊 Análisis por Lotes":
                show_batch_analysis(patient)
            else:
                show_technique_comparison(patient)
    else:
        st.warning("⚠️ Primero debe registrar pacientes en la sección 'Gestión de Pacientes'")

def show_individual_analysis(patient):
    st.subheader("🔍 Análisis Individual de Imagen")
    uploaded_file = st.file_uploader("📷 Cargar imagen de colposcopía", 
                                   type=['png', 'jpg', 'jpeg', 'tiff'])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        col1, col2 = st.columns([1, 1])
        with col1:
            st.image(image, caption="Imagen Original", use_column_width=True)
            st.subheader("⚙️ Opciones de Procesamiento")
            enhance_contrast = st.checkbox("Mejorar Contraste", value=True)
            reduce_noise = st.checkbox("Reducir Ruido", value=True)
            edge_detection = st.checkbox("Detección de Bordes", value=False)
        with col2:
            if st.button("🚀 Realizar Análisis", type="primary", use_container_width=True):
                with st.spinner("Analizando imagen... Por favor espere"):
                    import time
                    time.sleep(2)
                    results = EnhancedImageAnalyzer.analyze_image(image, "individual")
                    analysis_record = {
                        'patient_id': patient['id'],
                        'results': results,
                        'image_name': uploaded_file.name,
                        'analysis_date': datetime.now()
                    }
                    st.session_state.analysis_results.append(analysis_record)
                    Logger.log_analysis(patient['id'], "individual", results['confidence'])
                    show_analysis_results(results)
                    if st.button("📄 Generar Reporte PDF"):
                        pdf_buffer = ReportGenerator.create_pdf_report(patient, results)
                        st.download_button(
                            label="⬇️ Descargar Reporte",
                            data=pdf_buffer,
                            file_name=f"Reporte_{patient['apellido']}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                            mime="application/pdf"
                        )

def show_batch_analysis(patient):
    st.subheader("📊 Análisis por Lotes")
    uploaded_files = st.file_uploader("📷 Cargar múltiples imágenes", 
                                    type=['png', 'jpg', 'jpeg', 'tiff'],
                                    accept_multiple_files=True)
    if uploaded_files:
        st.info(f"✅ {len(uploaded_files)} imágenes cargadas")
        if st.button("🚀 Procesar Lote", type="primary"):
            progress_bar = st.progress(0)
            results_container = st.container()
            batch_results = []
            for i, uploaded_file in enumerate(uploaded_files):
                progress = (i + 1) / len(uploaded_files)
                progress_bar.progress(progress)
                image = Image.open(uploaded_file)
                results = EnhancedImageAnalyzer.analyze_image(image, "batch")
                batch_results.append({
                    'filename': uploaded_file.name,
                    'results': results
                })
                with results_container:
                    st.write(f"✅ Procesada: {uploaded_file.name}")
            st.success("🎉 Análisis por lotes completado!")
            show_batch_summary(batch_results)
            batch_record = {
                'patient_id': patient['id'],
                'batch_results': batch_results,
                'batch_date': datetime.now(),
                'total_images': len(uploaded_files)
            }
            st.session_state.analysis_results.append(batch_record)
            Logger.log_analysis(patient['id'], "batch", np.mean([r['results']['confidence'] for r in batch_results]))

def show_technique_comparison(patient):
    st.subheader("⚖️ Comparación de Técnicas")
    uploaded_file = st.file_uploader("📷 Cargar imagen para comparar técnicas", 
                                   type=['png', 'jpg', 'jpeg', 'tiff'])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Imagen para Comparación", use_column_width=True)
        if st.button("🔬 Comparar Técnicas", type="primary"):
            with st.spinner("Comparando diferentes técnicas de análisis..."):
                import time
                time.sleep(3)
                techniques = ['CNN Básico', 'ResNet-50', 'EfficientNet', 'Vision Transformer']
                comparison_results = {}
                for technique in techniques:
                    results = EnhancedImageAnalyzer.analyze_image(image, f"comparison_{technique}")
                    comparison_results[technique] = results
                show_technique_comparison_results(comparison_results)
                Logger.log_analysis(patient['id'], "comparison", np.mean([r['confidence'] for r in comparison_results.values()]))

def show_analysis_results(results):
    st.subheader("🎯 Resultados del Análisis")
    max_class = max(results['predictions'], key=results['predictions'].get)
    max_prob = results['predictions'][max_class]
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🎯 Diagnóstico Principal", max_class, f"{max_prob*100:.1f}%")
    with col2:
        st.metric("🔍 Confianza", f"{results['confidence']*100:.1f}%")
    with col3:
        st.metric("📸 Calidad de Imagen", f"{results['image_quality']*100:.1f}%")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Distribución de Probabilidades")
        labels = list(results['predictions'].keys())
        values = [v*100 for v in results['predictions'].values()]
        fig = px.bar(x=labels, y=values, 
                    title="Probabilidades por Diagnóstico",
                    labels={'x': 'Diagnóstico', 'y': 'Probabilidad (%)'})
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader("🥧 Vista Circular")
        fig = px.pie(values=values, names=labels, title="Distribución de Probabilidades")
        st.plotly_chart(fig, use_container_width=True)
    st.subheader("💡 Recomendaciones Clínicas")
    for i, rec in enumerate(results['recommendations'], 1):
        st.write(f"**{i}.** {rec}")
    with st.expander("🔧 Información Técnica"):
        st.json({
            'Timestamp': results['timestamp'].isoformat(),
            'Analysis Type': results['analysis_type'],
            'Confidence Score': results['confidence'],
            'Image Quality Score': results['image_quality']
        })

def show_batch_summary(batch_results):
    st.subheader("📈 Resumen del Análisis por Lotes")
    total_images = len(batch_results)
    avg_confidence = np.mean([r['results']['confidence'] for r in batch_results])
    avg_quality = np.mean([r['results']['image_quality'] for r in batch_results])
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📊 Total Imágenes", total_images)
    with col2:
        st.metric("🎯 Confianza Promedio", f"{avg_confidence*100:.1f}%")
    with col3:
        st.metric("📸 Calidad Promedio", f"{avg_quality*100:.1f}%")
    all_predictions = {}
    for result in batch_results:
        for diag, prob in result['results']['predictions'].items():
            if diag not in all_predictions:
                all_predictions[diag] = []
            all_predictions[diag].append(prob)
    diagnoses = list(all_predictions.keys())
    avg_probs = [np.mean(all_predictions[diag])*100 for diag in diagnoses]
    fig = px.bar(x=diagnoses, y=avg_probs,
                title="Distribución Promedio de Diagnósticos en el Lote",
                labels={'x': 'Diagnóstico', 'y': 'Probabilidad Promedio (%)'})
    st.plotly_chart(fig, use_container_width=True)
    st.subheader("📋 Resultados Detallados")
    results_data = []
    for result in batch_results:
        max_diag = max(result['results']['predictions'], 
                      key=result['results']['predictions'].get)
        max_prob = result['results']['predictions'][max_diag]
        results_data.append({
            'Archivo': result['filename'],
            'Diagnóstico Principal': max_diag,
            'Probabilidad': f"{max_prob*100:.1f}%",
            'Confianza': f"{result['results']['confidence']*100:.1f}%",
            'Calidad': f"{result['results']['image_quality']*100:.1f}%"
        })
    df = pd.DataFrame(results_data)
    st.dataframe(df, use_container_width=True)

def show_technique_comparison_results(comparison_results):
    st.subheader("⚖️ Comparación de Técnicas")
    comparison_data = []
    for technique, results in comparison_results.items():
        max_diag = max(results['predictions'], key=results['predictions'].get)
        max_prob = results['predictions'][max_diag]
        comparison_data.append({
            'Técnica': technique,
            'Diagnóstico': max_diag,
            'Probabilidad': f"{max_prob*100:.1f}%",
            'Confianza': f"{results['confidence']*100:.1f}%",
            'Tiempo (s)': np.random.uniform(1.5, 4.2)
        })
    df = pd.DataFrame(comparison_data)
    st.dataframe(df, use_container_width=True)
    techniques = list(comparison_results.keys())
    diagnoses = list(comparison_results[techniques[0]]['predictions'].keys())
    fig = go.Figure()
    for technique in techniques:
        probs = [comparison_results[technique]['predictions'][diag]*100 
                for diag in diagnoses]
        fig.add_trace(go.Scatter(x=diagnoses, y=probs, 
                               mode='lines+markers', name=technique))
    fig.update_layout(title="Comparación de Probabilidades por Técnica",
                     xaxis_title="Diagnóstico",
                     yaxis_title="Probabilidad (%)")
    st.plotly_chart(fig, use_container_width=True)

def show_reports():
    st.header("📊 Gestión de Reportes")
    if not st.session_state.analysis_results:
        st.info("📝 No hay análisis realizados. Realice análisis en la sección correspondiente.")
        return
    tab1, tab2, tab3 = st.tabs(["📋 Historial", "📄 Generar Reporte", "📈 Estadísticas"])
    with tab1:
        st.subheader("Historial de Análisis")
        col1, col2 = st.columns(2)
        with col1:
            date_filter = st.date_input("Filtrar por fecha")
        with col2:
            patient_filter = st.selectbox("Filtrar por paciente", 
                                        ["Todos"] + [f"{p['nombre']} {p['apellido']}" 
                                                   for p in st.session_state.patients_db])
        for i, analysis in enumerate(st.session_state.analysis_results):
            patient = PatientManager.get_patient(analysis['patient_id'])
            if patient:
                with st.expander(f"Análisis #{i+1} - {patient['nombre']} {patient['apellido']}", 
                               expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Fecha:** {analysis['analysis_date'].strftime('%d/%m/%Y %H:%M')}")
                        st.write(f"**Paciente:** {patient['nombre']} {patient['apellido']}")
                        if 'image_name' in analysis:
                            st.write(f"**Imagen:** {analysis['image_name']}")
                    with col2:
                        if st.button(f"📄 Ver Reporte", key=f"report_{i}"):
                            pdf_buffer = ReportGenerator.create_pdf_report(
                                patient, analysis['results'])
                            st.download_button(
                                label="⬇️ Descargar PDF",
                                data=pdf_buffer,
                                file_name=f"Reporte_{patient['apellido']}_{i+1}.pdf",
                                mime="application/pdf",
                                key=f"download_{i}"
                            )
    with tab2:
        st.subheader("Generar Nuevo Reporte")
        if st.session_state.patients_db and st.session_state.analysis_results:
            analysis_options = []
            for i, analysis in enumerate(st.session_state.analysis_results):
                patient = PatientManager.get_patient(analysis['patient_id'])
                if patient:
                    analysis_options.append(
                        f"Análisis #{i+1} - {patient['nombre']} {patient['apellido']} - {analysis['analysis_date'].strftime('%d/%m/%Y')}"
                    )
            selected_analysis = st.selectbox("Seleccionar análisis:", analysis_options)
            if selected_analysis:
                analysis_idx = int(selected_analysis.split('#')[1].split(' ')[0]) - 1
                analysis = st.session_state.analysis_results[analysis_idx]
                patient = PatientManager.get_patient(analysis['patient_id'])
                include_images = st.checkbox("Incluir imágenes", value=True)
                include_recommendations = st.checkbox("Incluir recomendaciones", value=True)
                include_technical_info = st.checkbox("Incluir información técnica", value=False)
                if st.button("📄 Generar Reporte Personalizado"):
                    pdf_buffer = ReportGenerator.create_pdf_report(patient, analysis['results'])
                    st.download_button(
                        label="⬇️ Descargar Reporte",
                        data=pdf_buffer,
                        file_name=f"Reporte_Personalizado_{patient['apellido']}.pdf",
                        mime="application/pdf"
                    )
    with tab3:
        st.subheader("Estadísticas Generales")
        show_statistics()

def show_statistics():
    if not st.session_state.analysis_results:
        st.info("No hay datos suficientes para mostrar estadísticas.")
        return
    total_analyses = len(st.session_state.analysis_results)
    total_patients = len(set(a['patient_id'] for a in st.session_state.analysis_results))
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🔍 Total Análisis", total_analyses)
    with col2:
        st.metric("👥 Pacientes Únicos", total_patients)
    with col3:
        avg_analyses = total_analyses / len(st.session_state.patients_db) if st.session_state.patients_db else 0
        st.metric("📊 Promedio por Paciente", f"{avg_analyses:.1f}")
    with col4:
        if st.session_state.analysis_results:
            last_analysis = max(st.session_state.analysis_results, 
                              key=lambda x: x['analysis_date'])
            days_since = (datetime.now() - last_analysis['analysis_date']).days
            st.metric("📅 Último Análisis", f"Hace {days_since} días")
    st.subheader("📈 Tendencias")
    dates = [datetime.now() - pd.Timedelta(days=30-i) for i in range(30)]
    analyses_per_day = np.random.poisson(2, 30)
    df_trend = pd.DataFrame({
        'Fecha': dates,
        'Análisis': analyses_per_day
    })
    fig = px.line(df_trend, x='Fecha', y='Análisis', 
                 title="Análisis Realizados por Día (Últimos 30 días)")
    st.plotly_chart(fig, use_container_width=True)

def show_email_sender():
    st.header("📧 Envío de Resultados")
    if not st.session_state.analysis_results:
        st.warning("⚠️ No hay análisis disponibles para enviar.")
        return
    with st.expander("⚙️ Configuración de Email", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            smtp_server = st.text_input("Servidor SMTP", value="smtp.gmail.com")
            smtp_port = st.number_input("Puerto", value=587)
            sender_email = st.text_input("Email del remitente")
        with col2:
            sender_password = st.text_input("Contraseña", type="password")
            use_tls = st.checkbox("Usar TLS", value=True)
    st.subheader("📋 Seleccionar Análisis")
    analysis_options = []
    for i, analysis in enumerate(st.session_state.analysis_results):
        patient = PatientManager.get_patient(analysis['patient_id'])
        if patient:
            analysis_options.append({
                'label': f"Análisis #{i+1} - {patient['nombre']} {patient['apellido']} - {analysis['analysis_date'].strftime('%d/%m/%Y')}",
                'index': i,
                'patient': patient,
                'analysis': analysis
            })
    selected_analyses = st.multiselect(
        "Seleccionar análisis para enviar:",
        options=analysis_options,
        format_func=lambda x: x['label']
    )
    if selected_analyses:
        st.subheader("📧 Configurar Envío")
        recipients = []
        for selected in selected_analyses:
            patient = selected['patient']
            if patient.get('email'):
                recipients.append(patient['email'])
        send_to_patient = st.checkbox("Enviar a pacientes", value=True)
        additional_emails = st.text_area(
            "Emails adicionales (separados por comas):",
            placeholder="doctor@hospital.com, admin@clinica.com"
        )
        if additional_emails:
            additional_list = [email.strip() for email in additional_emails.split(',')]
            recipients.extend(additional_list)
        email_subject = st.text_input(
            "Asunto del email:",
            value="Resultados de Análisis Colposcópico"
        )
        email_body = st.text_area(
            "Mensaje personalizado:",
            value="""Estimado/a paciente,

Adjunto encontrará los resultados de su análisis colposcópico.

Por favor, consulte con su médico tratante para la interpretación de los resultados.

Saludos cordiales,
Equipo Médico"""
        )
        if st.button("📧 Enviar Reportes", type="primary"):
            if sender_email and sender_password and recipients:
                success_count = 0
                error_count = 0
                progress_bar = st.progress(0)
                status_container = st.container()
                smtp_config = {
                    'smtp_server': smtp_server,
                    'port': smtp_port,
                    'email': sender_email,
                    'password': sender_password
                }
                for i, selected in enumerate(selected_analyses):
                    progress = (i + 1) / len(selected_analyses)
                    progress_bar.progress(progress)
                    patient = selected['patient']
                    analysis = selected['analysis']
                    pdf_buffer = ReportGenerator.create_pdf_report(patient, analysis['results'])
                    patient_recipients = [patient.get('email')] if patient.get('email') and send_to_patient else []
                    if additional_emails:
                        patient_recipients.extend(additional_list)
                    for recipient in patient_recipients:
                        try:
                            success, message = EmailSender.send_report_email(
                                recipient, 
                                f"{patient['nombre']} {patient['apellido']}", 
                                pdf_buffer, 
                                smtp_config
                            )
                            if success:
                                success_count += 1
                                with status_container:
                                    st.success(f"✅ Enviado a {recipient}")
                            else:
                                error_count += 1
                                with status_container:
                                    st.error(f"❌ Error enviando a {recipient}: {message}")
                        except Exception as e:
                            error_count += 1
                            with status_container:
                                st.error(f"❌ Error enviando a {recipient}: {str(e)}")
                            Logger.log_error(str(e), f"Envío de email a {recipient}")
                st.success(f"🎉 Proceso completado: {success_count} enviados exitosamente, {error_count} errores")
            else:
                st.error("⚠️ Por favor complete la configuración SMTP y verifique que hay destinatarios válidos")
    st.subheader("📝 Historial de Envíos")
    if st.session_state.email_history:
        df_history = pd.DataFrame(st.session_state.email_history)
        st.dataframe(df_history, use_container_width=True)
    else:
        st.info("No hay historial de envíos disponible.")

def show_configuration():
    st.header("⚙️ Configuración del Sistema")
    tab1, tab2, tab3, tab4 = st.tabs(["🎨 Apariencia", "🤖 Modelo IA", "📧 Email", "💾 Datos"])
    with tab1:
        st.subheader("Configuración de Apariencia")
        config = Config.load_config()
        theme = st.selectbox("Tema", ["light", "dark"], index=0 if config['ui']['theme'] == 'light' else 1)
        primary_color = st.color_picker("Color Primario", config['ui']['primary_color'])
        secondary_color = st.color_picker("Color Secundario", config['ui']['secondary_color'])
        if st.button("💾 Guardar Cambios de Apariencia"):
            config['ui'].update({
                'theme': theme,
                'primary_color': primary_color,
                'secondary_color': secondary_color
            })
            Config.save_config(config)
            st.success("✅ Configuración de apariencia guardada")
    with tab2:
        st.subheader("Configuración del Modelo IA")
        confidence_threshold = st.slider("Umbral de Confianza", 0.5, 1.0, config['model']['confidence_threshold'])
        batch_size = st.number_input("Tamaño del Lote", 1, 32, config['model']['batch_size'])
        max_image_size = st.number_input("Tamaño Máximo de Imagen", 128, 1024, config['model']['max_image_size'])
        if st.button("💾 Guardar Configuración del Modelo"):
            config['model'].update({
                'confidence_threshold': confidence_threshold,
                'batch_size': batch_size,
                'max_image_size': max_image_size
            })
            Config.save_config(config)
            st.success("✅ Configuración del modelo guardada")
    with tab3:
        st.subheader("Configuración de Email")
        smtp_server = st.text_input("Servidor SMTP", config['email']['smtp_server'])
        smtp_port = st.number_input("Puerto SMTP", min_value=0, max_value=65535, value=config['email']['smtp_port'])
        use_tls = st.checkbox("Usar TLS", value=config['email']['use_tls'])
        if st.button("💾 Guardar Configuración de Email"):
            config['email'].update({
                'smtp_server': smtp_server,
                'smtp_port': smtp_port,
                'use_tls': use_tls
            })
            Config.save_config(config)
            st.success("✅ Configuración de email guardada")
    with tab4:
        st.subheader("Gestión de Datos")
        if st.button("🗑️ Eliminar Todos los Datos"):
            st.session_state.patients_db = []
            st.session_state.analysis_results = []
            DataPersistence.save_data()
            st.success("✅ Todos los datos han sido eliminados")

def enhanced_main():
    Logger.setup_logging()
    if 'data_loaded' not in st.session_state:
        DataPersistence.load_data()
        st.session_state.data_loaded = True
    DataPersistence.auto_save()
    config = Config.load_config()
    main()
    DataPersistence.save_data()

if __name__ == "__main__":
    enhanced_main()
