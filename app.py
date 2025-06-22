import streamlit as st
import pandas as pd
from datetime import datetime, date
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
        # Simulación de análisis - aquí iría tu modelo de IA real
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
        
        # Normalizar probabilidades
        total = sum(results['predictions'].values())
        results['predictions'] = {k: v/total for k, v in results['predictions'].items()}
        
        # Generar recomendaciones basadas en el resultado principal
        max_class = max(results['predictions'], key=results['predictions'].get)
        max_prob = results['predictions'][max_class]
        
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
        
        # Estilo personalizado para el título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1,  # Centrado
            textColor=colors.darkblue
        )
        
        # Título del reporte
        story.append(Paragraph("REPORTE DE ANÁLISIS COLPOSCÓPICO", title_style))
        story.append(Spacer(1, 20))
        
        # Información del paciente
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
        
        # Resultados del análisis
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
        
        # Recomendaciones
        story.append(Paragraph("RECOMENDACIONES CLÍNICAS", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        for i, rec in enumerate(analysis_results['recommendations'], 1):
            story.append(Paragraph(f"{i}. {rec}", styles['Normal']))
            story.append(Spacer(1, 5))
        
        story.append(Spacer(1, 20))
        
        # Información adicional
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
            
            # Adjuntar PDF
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(pdf_buffer.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename="Reporte_Colposcopia_{patient_name.replace(" ", "_")}.pdf"'
            )
            msg.attach(part)
            
            # Enviar email
            server = smtplib.SMTP(smtp_config['smtp_server'], smtp_config['port'])
            server.starttls()
            server.login(smtp_config['email'], smtp_config['password'])
            text = msg.as_string()
            server.sendmail(smtp_config['email'], recipient_email, text)
            server.quit()
            
            return True, "Email enviado exitosamente"
        except Exception as e:
            return False, f"Error al enviar email: {str(e)}"

def main():
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>🔬 ColpoVision</h1>
        <p>Sistema de Análisis de Colposcopía con Inteligencia Artificial</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar para navegación
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
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>👤 Pacientes</h3>
            <h2>{}</h2>
        </div>
        """.format(len(st.session_state.patients_db)), unsafe_allow_html=True)
    
    with col2:
        total_analyses = len(st.session_state.analysis_results)
        st.markdown("""
        <div class="metric-card">
            <h3>🔍 Análisis</h3>
            <h2>{}</h2>
        </div>
        """.format(total_analyses), unsafe_allow_html=True)
    
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
    
    # Gráficos de ejemplo
    if st.session_state.analysis_results:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Distribución de Diagnósticos")
            # Crear gráfico de ejemplo
            diagnoses = ['Normal', 'CIN I', 'CIN II', 'CIN III', 'Carcinoma']
            values = [45, 25, 15, 10, 5]  # Valores de ejemplo
            
            fig = px.pie(values=values, names=diagnoses, 
                        title="Distribución de Diagnósticos")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📈 Análisis por Mes")
            # Gráfico de tendencia temporal
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
            
            # Información médica adicional
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
                if nombre and apellido and identificacion:
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
                    
                    patient_id = PatientManager.add_patient(patient_data)
                    st.success(f"✅ Paciente agregado exitosamente con ID: {patient_id}")
                    st.balloons()
                else:
                    st.error("⚠️ Por favor complete los campos obligatorios marcados con *")
    
    with tab2:
        st.subheader("Lista de Pacientes Registrados")
        
        if st.session_state.patients_db:
            # Crear DataFrame para mostrar
            df_patients = pd.DataFrame(st.session_state.patients_db)
            
            # Filtros
            col1, col2 = st.columns(2)
            with col1:
                search_term = st.text_input("🔍 Buscar paciente", placeholder="Nombre, apellido o identificación")
            with col2:
                sort_by = st.selectbox("Ordenar por:", ["nombre", "apellido", "fecha_nacimiento", "created_at"])
            
            # Aplicar filtros
            if search_term:
                mask = (
                    df_patients['nombre'].str.contains(search_term, case=False, na=False) |
                    df_patients['apellido'].str.contains(search_term, case=False, na=False) |
                    df_patients['identificacion'].str.contains(search_term, case=False, na=False)
                )
                df_patients = df_patients[mask]
            
            # Mostrar tabla
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
    
    # Selección de paciente
    if st.session_state.patients_db:
        patient_options = {f"{p['nombre']} {p['apellido']} - {p['identificacion']}": p['id'] 
                         for p in st.session_state.patients_db}
        
        selected_patient_key = st.selectbox("👤 Seleccionar Paciente:", 
                                          ["Seleccione un paciente..."] + list(patient_options.keys()))
        
        if selected_patient_key != "Seleccione un paciente...":
            patient_id = patient_options[selected_patient_key]
            patient = PatientManager.get_patient(patient_id)
            
            st.success(f"📋 Paciente seleccionado: {patient['nombre']} {patient['apellido']}")
            
            # Tipo de análisis
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
        # Mostrar imagen
        image = Image.open(uploaded_file)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.image(image, caption="Imagen Original", use_column_width=True)
            
            # Opciones de procesamiento
            st.subheader("⚙️ Opciones de Procesamiento")
            enhance_contrast = st.checkbox("Mejorar Contraste", value=True)
            reduce_noise = st.checkbox("Reducir Ruido", value=True)
            edge_detection = st.checkbox("Detección de Bordes", value=False)
        
        with col2:
            if st.button("🚀 Realizar Análisis", type="primary", use_container_width=True):
                with st.spinner("Analizando imagen... Por favor espere"):
                    # Simular tiempo de procesamiento
                    import time
                    time.sleep(2)
                    
                    # Realizar análisis
                    results = ImageAnalyzer.analyze_image(image, "individual")
                    
                    # Guardar resultados
                    analysis_record = {
                        'patient_id': patient['id'],
                        'results': results,
                        'image_name': uploaded_file.name,
                        'analysis_date': datetime.now()
                    }
                    st.session_state.analysis_results.append(analysis_record)
                    
                    # Mostrar resultados
                    show_analysis_results(results)
                    
                    # Botón para generar reporte
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
    print(uploaded_file)  # 4 espacios aquí
