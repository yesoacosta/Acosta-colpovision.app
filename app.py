
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

# ConfiguraciÃ³n de la pÃ¡gina
st.set_page_config(
st.title("ðŸ©º ColpoVision - AnÃ¡lisis de ColposcopÃ­a")
    page_title="ColpoVision - AnÃ¡lisis de ColposcopÃ­a",
    page_icon="ðŸ”¬",
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

# InicializaciÃ³n del estado de la sesiÃ³n
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
        """Simular anÃ¡lisis de imagen con IA"""
        # SimulaciÃ³n de anÃ¡lisis - aquÃ­ irÃ­a tu modelo de IA real
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
                "Repetir colposcopÃ­a en 12 meses"
            ]
        elif max_class in ['CIN I']:
            results['recommendations'] = [
                "Seguimiento estrecho cada 6 meses",
                "Considerar biopsia si persiste",
                "EvaluaciÃ³n de factores de riesgo"
            ]
        elif max_class in ['CIN II', 'CIN III']:
            results['recommendations'] = [
                "Biopsia confirmativa recomendada",
                "Tratamiento segÃºn protocolo",
                "Seguimiento oncolÃ³gico"
            ]
        else:
            results['recommendations'] = [
                "EvaluaciÃ³n oncolÃ³gica urgente",
                "Biopsia confirmatoria inmediata",
                "EstadificaciÃ³n completa"
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
        
        # Estilo personalizado para el tÃ­tulo
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1,  # Centrado
            textColor=colors.darkblue
        )
        
        # TÃ­tulo del reporte
        story.append(Paragraph("REPORTE DE ANÃLISIS COLPOSCÃ“PICO", title_style))
        story.append(Spacer(1, 20))
        
        # InformaciÃ³n del paciente
        patient_info = [
            ['Datos del Paciente', ''],
            ['Nombre:', f"{patient_data['nombre']} {patient_data['apellido']}"],
            ['IdentificaciÃ³n:', patient_data['identificacion']],
            ['Fecha de Nacimiento:', str(patient_data['fecha_nacimiento'])],
            ['Edad:', str(patient_data['edad'])],
            ['TelÃ©fono:', patient_data.get('telefono', 'N/A')],
            ['Email:', patient_data.get('email', 'N/A')],
            ['Fecha del AnÃ¡lisis:', analysis_results['timestamp'].strftime('%d/%m/%Y %H:%M')]
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
        
        # Resultados del anÃ¡lisis
        story.append(Paragraph("RESULTADOS DEL ANÃLISIS", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        results_data = [['DiagnÃ³stico', 'Probabilidad (%)']]
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
        story.append(Paragraph("RECOMENDACIONES CLÃNICAS", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        for i, rec in enumerate(analysis_results['recommendations'], 1):
            story.append(Paragraph(f"{i}. {rec}", styles['Normal']))
            story.append(Spacer(1, 5))
        
        story.append(Spacer(1, 20))
        
        # InformaciÃ³n adicional
        info_adicional = f"""
        <b>Confianza del anÃ¡lisis:</b> {analysis_results['confidence']*100:.1f}%<br/>
        <b>Calidad de imagen:</b> {analysis_results['image_quality']*100:.1f}%<br/>
        <b>Tipo de anÃ¡lisis:</b> {analysis_results['analysis_type'].title()}<br/>
        <br/>
        <i>Este reporte es generado automÃ¡ticamente por el sistema ColpoVision y debe ser 
        interpretado por un profesional mÃ©dico calificado. No sustituye el juicio clÃ­nico.</i>
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
            msg['Subject'] = f"Reporte de AnÃ¡lisis ColposcÃ³pico - {patient_name}"
            
            body = f"""
            Estimado/a paciente,
            
            Adjunto encontrarÃ¡ el reporte de su anÃ¡lisis colposcÃ³pico realizado el {datetime.now().strftime('%d/%m/%Y')}.
            
            Por favor, consulte con su mÃ©dico tratante para la interpretaciÃ³n de los resultados.
            
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
        <h1>ðŸ”¬ ColpoVision</h1>
        <p>Sistema de AnÃ¡lisis de ColposcopÃ­a con Inteligencia Artificial</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar para navegaciÃ³n
    st.sidebar.title("ðŸ“‹ MenÃº Principal")
    page = st.sidebar.selectbox(
        "Seleccionar SecciÃ³n:",
        ["ðŸ  Dashboard", "ðŸ‘¤ GestiÃ³n de Pacientes", "ðŸ” AnÃ¡lisis de ImÃ¡genes", 
         "ðŸ“Š Reportes", "ðŸ“§ EnvÃ­o de Resultados", "âš™ï¸ ConfiguraciÃ³n"]
    )
    
    if page == "ðŸ  Dashboard":
        show_dashboard()
    elif page == "ðŸ‘¤ GestiÃ³n de Pacientes":
        show_patient_management()
    elif page == "ðŸ” AnÃ¡lisis de ImÃ¡genes":
        show_image_analysis()
    elif page == "ðŸ“Š Reportes":
        show_reports()
    elif page == "ðŸ“§ EnvÃ­o de Resultados":
        show_email_sender()
    elif page == "âš™ï¸ ConfiguraciÃ³n":
        show_configuration()

def show_dashboard():
    st.header("ðŸ“Š Dashboard General")
    
    # MÃ©tricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>ðŸ‘¤ Pacientes</h3>
            <h2>{}</h2>
        </div>
        """.format(len(st.session_state.patients_db)), unsafe_allow_html=True)
    
    with col2:
        total_analyses = len(st.session_state.analysis_results)
        st.markdown("""
        <div class="metric-card">
            <h3>ðŸ” AnÃ¡lisis</h3>
            <h2>{}</h2>
        </div>
        """.format(total_analyses), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>ðŸ“ˆ PrecisiÃ³n</h3>
            <h2>94.2%</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>â±ï¸ Tiempo Prom.</h3>
            <h2>2.3 min</h2>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # GrÃ¡ficos de ejemplo
    if st.session_state.analysis_results:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("ðŸ“Š DistribuciÃ³n de DiagnÃ³sticos")
            # Crear grÃ¡fico de ejemplo
            diagnoses = ['Normal', 'CIN I', 'CIN II', 'CIN III', 'Carcinoma']
            values = [45, 25, 15, 10, 5]  # Valores de ejemplo
            
            fig = px.pie(values=values, names=diagnoses, 
                        title="DistribuciÃ³n de DiagnÃ³sticos")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("ðŸ“ˆ AnÃ¡lisis por Mes")
            # GrÃ¡fico de tendencia temporal
            months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun']
            analyses = [12, 15, 18, 22, 19, 25]
            
            fig = px.line(x=months, y=analyses, title="AnÃ¡lisis Realizados por Mes")
            st.plotly_chart(fig, use_container_width=True)

def show_patient_management():
    st.header("ðŸ‘¤ GestiÃ³n de Pacientes")
    
    tab1, tab2, tab3 = st.tabs(["âž• Nuevo Paciente", "ðŸ“‹ Lista de Pacientes", "âœï¸ Editar Paciente"])
    
    with tab1:
        st.subheader("Agregar Nuevo Paciente")
        
        with st.form("nuevo_paciente"):
            col1, col2 = st.columns(2)
            
            with col1:
                nombre = st.text_input("Nombre *", placeholder="Ingrese el nombre")
                identificacion = st.text_input("IdentificaciÃ³n *", placeholder="NÃºmero de identificaciÃ³n")
                fecha_nacimiento = st.date_input("Fecha de Nacimiento *")
                telefono = st.text_input("TelÃ©fono", placeholder="NÃºmero de telÃ©fono")
                
            with col2:
                apellido = st.text_input("Apellido *", placeholder="Ingrese el apellido")
                email = st.text_input("Email", placeholder="correo@ejemplo.com")
                edad = st.number_input("Edad", min_value=0, max_value=120, value=30)
                direccion = st.text_area("DirecciÃ³n", placeholder="DirecciÃ³n completa")
            
            # InformaciÃ³n mÃ©dica adicional
            st.subheader("InformaciÃ³n MÃ©dica")
            col3, col4 = st.columns(2)
            
            with col3:
                antecedentes = st.text_area("Antecedentes MÃ©dicos")
                medicamentos = st.text_area("Medicamentos Actuales")
                
            with col4:
                alergias = st.text_area("Alergias")
                observaciones = st.text_area("Observaciones")
            
            submitted = st.form_submit_button("ðŸ’¾ Guardar Paciente", type="primary")
            
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
                    st.success(f"âœ… Paciente agregado exitosamente con ID: {patient_id}")
                    st.balloons()
                else:
                    st.error("âš ï¸ Por favor complete los campos obligatorios marcados con *")
    
    with tab2:
        st.subheader("Lista de Pacientes Registrados")
        
        if st.session_state.patients_db:
            # Crear DataFrame para mostrar
            df_patients = pd.DataFrame(st.session_state.patients_db)
            
            # Filtros
            col1, col2 = st.columns(2)
            with col1:
                search_term = st.text_input("ðŸ” Buscar paciente", placeholder="Nombre, apellido o identificaciÃ³n")
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
                        <h4>ðŸ‘¤ {patient['nombre']} {patient['apellido']}</h4>
                        <p><strong>ID:</strong> {patient['identificacion']} | 
                           <strong>Edad:</strong> {patient['edad']} aÃ±os | 
                           <strong>TelÃ©fono:</strong> {patient.get('telefono', 'N/A')} |
                           <strong>Email:</strong> {patient.get('email', 'N/A')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns([1, 1, 2])
                    if col1.button(f"ðŸ“‹ Ver Detalles", key=f"details_{patient['id']}"):
                        st.session_state.selected_patient = patient['id']
                    if col2.button(f"ðŸ” Analizar", key=f"analyze_{patient['id']}"):
                        st.session_state.current_patient = patient['id']
                        st.rerun()
        else:
            st.info("ðŸ“ No hay pacientes registrados. Agregue el primer paciente en la pestaÃ±a 'Nuevo Paciente'.")
    
    with tab3:
        st.subheader("Editar InformaciÃ³n del Paciente")
        
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
                            identificacion = st.text_input("IdentificaciÃ³n", value=patient['identificacion'])
                            telefono = st.text_input("TelÃ©fono", value=patient.get('telefono', ''))
                            
                        with col2:
                            apellido = st.text_input("Apellido", value=patient['apellido'])
                            email = st.text_input("Email", value=patient.get('email', ''))
                            edad = st.number_input("Edad", value=patient['edad'], min_value=0, max_value=120)
                        
                        direccion = st.text_area("DirecciÃ³n", value=patient.get('direccion', ''))
                        
                        if st.form_submit_button("ðŸ’¾ Actualizar Datos"):
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
                                st.success("âœ… Datos actualizados correctamente")
                                st.rerun()
                            else:
                                st.error("âŒ Error al actualizar los datos")
        else:
            st.info("No hay pacientes registrados para editar.")

def show_image_analysis():
    st.header("ðŸ” AnÃ¡lisis de ImÃ¡genes")
    
    # SelecciÃ³n de paciente
    if st.session_state.patients_db:
        patient_options = {f"{p['nombre']} {p['apellido']} - {p['identificacion']}": p['id'] 
                         for p in st.session_state.patients_db}
        
        selected_patient_key = st.selectbox("ðŸ‘¤ Seleccionar Paciente:", 
                                          ["Seleccione un paciente..."] + list(patient_options.keys()))
        
        if selected_patient_key != "Seleccione un paciente...":
            patient_id = patient_options[selected_patient_key]
            patient = PatientManager.get_patient(patient_id)
            
            st.success(f"ðŸ“‹ Paciente seleccionado: {patient['nombre']} {patient['apellido']}")
            
            # Tipo de anÃ¡lisis
            analysis_type = st.radio("Tipo de AnÃ¡lisis:", 
                                   ["ðŸ” AnÃ¡lisis Individual", "ðŸ“Š AnÃ¡lisis por Lotes", "âš–ï¸ ComparaciÃ³n de TÃ©cnicas"])
            
            if analysis_type == "ðŸ” AnÃ¡lisis Individual":
                show_individual_analysis(patient)
            elif analysis_type == "ðŸ“Š AnÃ¡lisis por Lotes":
                show_batch_analysis(patient)
            else:
                show_technique_comparison(patient)
    else:
        st.warning("âš ï¸ Primero debe registrar pacientes en la secciÃ³n 'GestiÃ³n de Pacientes'")

def show_individual_analysis(patient):
    st.subheader("ðŸ” AnÃ¡lisis Individual de Imagen")
    
    uploaded_file = st.file_uploader("ðŸ“· Cargar imagen de colposcopÃ­a", 
                                   type=['png', 'jpg', 'jpeg', 'tiff'])
    
    if uploaded_file is not None:
        # Mostrar imagen
        image = Image.open(uploaded_file)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.image(image, caption="Imagen Original", use_column_width=True)
            
            # Opciones de procesamiento
            st.subheader("âš™ï¸ Opciones de Procesamiento")
            enhance_contrast = st.checkbox("Mejorar Contraste", value=True)
            reduce_noise = st.checkbox("Reducir Ruido", value=True)
            edge_detection = st.checkbox("DetecciÃ³n de Bordes", value=False)
        
        with col2:
            if st.button("ðŸš€ Realizar AnÃ¡lisis", type="primary", use_container_width=True):
                with st.spinner("Analizando imagen... Por favor espere"):
                    # Simular tiempo de procesamiento
                    import time
                    time.sleep(2)
                    
                    # Realizar anÃ¡lisis
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
                    
                    # BotÃ³n para generar reporte
                    if st.button("ðŸ“„ Generar Reporte PDF"):
                        pdf_buffer = ReportGenerator.create_pdf_report(patient, results)
                        st.download_button(
                            label="â¬‡ï¸ Descargar Reporte",
                            data=pdf_buffer,
                            file_name=f"Reporte_{patient['apellido']}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                            mime="application/pdf"
                        )

def show_batch_analysis(patient):
    st.subheader("ðŸ“Š AnÃ¡lisis por Lotes")
    
    uploaded_files = st.file_uploader("ðŸ“· Cargar mÃºltiples imÃ¡genes", 
                                    type=['png', 'jpg', 'jpeg', 'tiff'],
                                    accept_multiple_files=True)
    
    if uploaded_files:
        st.info(f"âœ… {len(uploaded_files)} imÃ¡genes cargadas")
        
        if st.button("ðŸš€ Procesar Lote", type="primary"):
            progress_bar = st.progress(0)
            results_container = st.container()
            
            batch_results = []
            
            for i, uploaded_file in enumerate(uploaded_files):
                # Actualizar barra de progreso
                progress = (i + 1) / len(uploaded_files)
                progress_bar.progress(progress)
                
                # Procesar imagen
                image = Image.open(uploaded_file)
                results = ImageAnalyzer.analyze_image(image, "batch")
                
                batch_results.append({
                    'filename': uploaded_file.name,
                    'results': results
                })
                
                # Mostrar progreso
                with results_container:
                    st.write(f"âœ… Procesada: {uploaded_file.name}")
            
            # Mostrar resumen del lote
            st.success("ðŸŽ‰ AnÃ¡lisis por lotes completado!")
            show_batch_summary(batch_results)
            
            # Guardar resultados del lote
            batch_record = {
                'patient_id': patient['id'],
                'batch_results': batch_results,
                'batch_date': datetime.now(),
                'total_images': len(uploaded_files)
            }
            st.session_state.analysis_results.append(batch_record)

def show_technique_comparison(patient):
    st.subheader("âš–ï¸ ComparaciÃ³n de TÃ©cnicas")
    
    uploaded_file = st.file_uploader("ðŸ“· Cargar imagen para comparar tÃ©cnicas", 
                                   type=['png', 'jpg', 'jpeg', 'tiff'])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Imagen para ComparaciÃ³n", use_column_width=True)
        
        if st.button("ðŸ”¬ Comparar TÃ©cnicas", type="primary"):
            with st.spinner("Comparando diferentes tÃ©cnicas de anÃ¡lisis..."):
                import time
                time.sleep(3)  # Simular procesamiento
                
                # Simular diferentes tÃ©cnicas
                techniques = ['CNN BÃ¡sico', 'ResNet-50', 'EfficientNet', 'Vision Transformer']
                comparison_results = {}
                
                for technique in techniques:
                    results = ImageAnalyzer.analyze_image(image, f"comparison_{technique}")
                    comparison_results[technique] = results
                
                show_technique_comparison_results(comparison_results)

def show_analysis_results(results):
    st.subheader("ðŸŽ¯ Resultados del AnÃ¡lisis")
    
    # Resultado principal
    max_class = max(results['predictions'], key=results['predictions'].get)
    max_prob = results['predictions'][max_class]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("ðŸŽ¯ DiagnÃ³stico Principal", max_class, f"{max_prob*100:.1f}%")
    
    with col2:
        st.metric("ðŸ” Confianza", f"{results['confidence']*100:.1f}%")
    
    with col3:
        st.metric("ðŸ“¸ Calidad de Imagen", f"{results['image_quality']*100:.1f}%")
    
    # GrÃ¡fico de probabilidades
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("ðŸ“Š DistribuciÃ³n de Probabilidades")
        labels = list(results['predictions'].keys())
        values = [v*100 for v in results['predictions'].values()]
        
        fig = px.bar(x=labels, y=values, 
                    title="Probabilidades por DiagnÃ³stico",
                    labels={'x': 'DiagnÃ³stico', 'y': 'Probabilidad (%)'})
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("ðŸ¥§ Vista Circular")
        fig = px.pie(values=values, names=labels, 
                    title="DistribuciÃ³n de Probabilidades")
        st.plotly_chart(fig, use_container_width=True)
    
    # Recomendaciones
    st.subheader("ðŸ’¡ Recomendaciones ClÃ­nicas")
    for i, rec in enumerate(results['recommendations'], 1):
        st.write(f"**{i}.** {rec}")
    
    # InformaciÃ³n tÃ©cnica
    with st.expander("ðŸ”§ InformaciÃ³n TÃ©cnica"):
        st.json({
            'Timestamp': results['timestamp'].isoformat(),
            'Analysis Type': results['analysis_type'],
            'Confidence Score': results['confidence'],
            'Image Quality Score': results['image_quality']
        })

def show_batch_summary(batch_results):
    st.subheader("ðŸ“ˆ Resumen del AnÃ¡lisis por Lotes")
    
    # EstadÃ­sticas generales
    total_images = len(batch_results)
    avg_confidence = np.mean([r['results']['confidence'] for r in batch_results])
    avg_quality = np.mean([r['results']['image_quality'] for r in batch_results])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("ðŸ“Š Total ImÃ¡genes", total_images)
    with col2:
        st.metric("ðŸŽ¯ Confianza Promedio", f"{avg_confidence*100:.1f}%")
    with col3:
        st.metric("ðŸ“¸ Calidad Promedio", f"{avg_quality*100:.1f}%")
    
    # DistribuciÃ³n de diagnÃ³sticos
    all_predictions = {}
    for result in batch_results:
        for diag, prob in result['results']['predictions'].items():
            if diag not in all_predictions:
                all_predictions[diag] = []
            all_predictions[diag].append(prob)
    
    # GrÃ¡fico de distribuciÃ³n
    diagnoses = list(all_predictions.keys())
    avg_probs = [np.mean(all_predictions[diag])*100 for diag in diagnoses]
    
    fig = px.bar(x=diagnoses, y=avg_probs,
                title="DistribuciÃ³n Promedio de DiagnÃ³sticos en el Lote",
                labels={'x': 'DiagnÃ³stico', 'y': 'Probabilidad Promedio (%)'})
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabla detallada
    st.subheader("ðŸ“‹ Resultados Detallados")
    results_data = []
    for result in batch_results:
        max_diag = max(result['results']['predictions'], 
                      key=result['results']['predictions'].get)
        max_prob = result['results']['predictions'][max_diag]
        
        results_data.append({
            'Archivo': result['filename'],
            'DiagnÃ³stico Principal': max_diag,
            'Probabilidad': f"{max_prob*100:.1f}%",
            'Confianza': f"{result['results']['confidence']*100:.1f}%",
            'Calidad': f"{result['results']['image_quality']*100:.1f}%"
        })
    
    df = pd.DataFrame(results_data)
    st.dataframe(df, use_container_width=True)

def show_technique_comparison_results(comparison_results):
    st.subheader("âš–ï¸ ComparaciÃ³n de TÃ©cnicas")
    
    # Tabla comparativa
    comparison_data = []
    for technique, results in comparison_results.items():
        max_diag = max(results['predictions'], key=results['predictions'].get)
        max_prob = results['predictions'][max_diag]
        
        comparison_data.append({
            'TÃ©cnica': technique,
            'DiagnÃ³stico': max_diag,
            'Probabilidad': f"{max_prob*100:.1f}%",
            'Confianza': f"{results['confidence']*100:.1f}%",
            'Tiempo (s)': np.random.uniform(1.5, 4.2)  # Tiempo simulado
        })
    
    df = pd.DataFrame(comparison_data)
    st.dataframe(df, use_container_width=True)
    
    # GrÃ¡fico comparativo
    techniques = list(comparison_results.keys())
    diagnoses = list(comparison_results[techniques[0]]['predictions'].keys())
    
    fig = go.Figure()
    
    for technique in techniques:
        probs = [comparison_results[technique]['predictions'][diag]*100 
                for diag in diagnoses]
        fig.add_trace(go.Scatter(x=diagnoses, y=probs, 
                               mode='lines+markers', name=technique))
    
    fig.update_layout(title="ComparaciÃ³n de Probabilidades por TÃ©cnica",
                     xaxis_title="DiagnÃ³stico",
                     yaxis_title="Probabilidad (%)")
    
    st.plotly_chart(fig, use_container_width=True)

def show_reports():
    st.header("ðŸ“Š GestiÃ³n de Reportes")
    
    if not st.session_state.analysis_results:
        st.info("ðŸ“ No hay anÃ¡lisis realizados. Realice anÃ¡lisis en la secciÃ³n correspondiente.")
        return
    
    tab1, tab2, tab3 = st.tabs(["ðŸ“‹ Historial", "ðŸ“„ Generar Reporte", "ðŸ“ˆ EstadÃ­sticas"])
    
    with tab1:
        st.subheader("Historial de AnÃ¡lisis")
        
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            date_filter = st.date_input("Filtrar por fecha")
        with col2:
            patient_filter = st.selectbox("Filtrar por paciente", 
                                        ["Todos"] + [f"{p['nombre']} {p['apellido']}" 
                                                   for p in st.session_state.patients_db])
        
        # Mostrar historial
        for i, analysis in enumerate(st.session_state.analysis_results):
            patient = PatientManager.get_patient(analysis['patient_id'])
            if patient:
                with st.expander(f"AnÃ¡lisis #{i+1} - {patient['nombre']} {patient['apellido']}", 
                               expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Fecha:** {analysis['analysis_date'].strftime('%d/%m/%Y %H:%M')}")
                        st.write(f"**Paciente:** {patient['nombre']} {patient['apellido']}")
                        if 'image_name' in analysis:
                            st.write(f"**Imagen:** {analysis['image_name']}")
                    
                    with col2:
                        if st.button(f"ðŸ“„ Ver Reporte", key=f"report_{i}"):
                            pdf_buffer = ReportGenerator.create_pdf_report(
                                patient, analysis['results'])
                            st.download_button(
                                label="â¬‡ï¸ Descargar PDF",
                                data=pdf_buffer,
                                file_name=f"Reporte_{patient['apellido']}_{i+1}.pdf",
                                mime="application/pdf",
                                key=f"download_{i}"
                            )
    
    with tab2:
        st.subheader("Generar Nuevo Reporte")
        
        if st.session_state.patients_db and st.session_state.analysis_results:
            # SelecciÃ³n de anÃ¡lisis
            analysis_options = []
            for i, analysis in enumerate(st.session_state.analysis_results):
                patient = PatientManager.get_patient(analysis['patient_id'])
                if patient:
                    analysis_options.append(
                        f"AnÃ¡lisis #{i+1} - {patient['nombre']} {patient['apellido']} - {analysis['analysis_date'].strftime('%d/%m/%Y')}"
                    )
            
            selected_analysis = st.selectbox("Seleccionar anÃ¡lisis:", analysis_options)
            
            if selected_analysis:
                analysis_idx = int(selected_analysis.split('#')[1].split(' ')[0]) - 1
                analysis = st.session_state.analysis_results[analysis_idx]
                patient = PatientManager.get_patient(analysis['patient_id'])
                
                # Opciones del reporte
                include_images = st.checkbox("Incluir imÃ¡genes", value=True)
                include_recommendations = st.checkbox("Incluir recomendaciones", value=True)
                include_technical_info = st.checkbox("Incluir informaciÃ³n tÃ©cnica", value=False)
                
                if st.button("ðŸ“„ Generar Reporte Personalizado"):
                    pdf_buffer = ReportGenerator.create_pdf_report(patient, analysis['results'])
                    st.download_button(
                        label="â¬‡ï¸ Descargar Reporte",
                        data=pdf_buffer,
                        file_name=f"Reporte_Personalizado_{patient['apellido']}.pdf",
                        mime="application/pdf"
                    )
    
    with tab3:
        st.subheader("EstadÃ­sticas Generales")
        show_statistics()

def show_statistics():
    if not st.session_state.analysis_results:
        st.info("No hay datos suficientes para mostrar estadÃ­sticas.")
        return
    
    # MÃ©tricas generales
    total_analyses = len(st.session_state.analysis_results)
    total_patients = len(set(a['patient_id'] for a in st.session_state.analysis_results))
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("ðŸ” Total AnÃ¡lisis", total_analyses)
    with col2:
        st.metric("ðŸ‘¥ Pacientes Ãšnicos", total_patients)
    with col3:
        avg_analyses = total_analyses / len(st.session_state.patients_db) if st.session_state.patients_db else 0
        st.metric("ðŸ“Š Promedio por Paciente", f"{avg_analyses:.1f}")
    with col4:
        # Ãšltimo anÃ¡lisis
        if st.session_state.analysis_results:
            last_analysis = max(st.session_state.analysis_results, 
                              key=lambda x: x['analysis_date'])
            days_since = (datetime.now() - last_analysis['analysis_date']).days
            st.metric("ðŸ“… Ãšltimo AnÃ¡lisis", f"Hace {days_since} dÃ­as")
    
    # GrÃ¡ficos de tendencias
    st.subheader("ðŸ“ˆ Tendencias")
    
    # Crear datos de ejemplo para grÃ¡ficos
    dates = [datetime.now() - pd.Timedelta(days=30-i) for i in range(30)]
    analyses_per_day = np.random.poisson(2, 30)  # SimulaciÃ³n
    
    df_trend = pd.DataFrame({
        'Fecha': dates,
        'AnÃ¡lisis': analyses_per_day
    })
    
    fig = px.line(df_trend, x='Fecha', y='AnÃ¡lisis', 
                 title="AnÃ¡lisis Realizados por DÃ­a (Ãšltimos 30 dÃ­as)")
    st.plotly_chart(fig, use_container_width=True)

def show_email_sender():
    st.header("ðŸ“§ EnvÃ­o de Resultados")
    
    if not st.session_state.analysis_results:
        st.warning("âš ï¸ No hay anÃ¡lisis disponibles para enviar.")
        return
    
    # ConfiguraciÃ³n SMTP
    with st.expander("âš™ï¸ ConfiguraciÃ³n de Email", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            smtp_server = st.text_input("Servidor SMTP", value="smtp.gmail.com")
            smtp_port = st.number_input("Puerto", value=587)
            sender_email = st.text_input("Email del remitente")
            
        with col2:
            sender_password = st.text_input("ContraseÃ±a", type="password")
            use_tls = st.checkbox("Usar TLS", value=True)
    
    # SelecciÃ³n de anÃ¡lisis para enviar
    st.subheader("ðŸ“‹ Seleccionar AnÃ¡lisis")
    
    analysis_options = []
    for i, analysis in enumerate(st.session_state.analysis_results):
        patient = PatientManager.get_patient(analysis['patient_id'])
        if patient:
            analysis_options.append({
                'label': f"AnÃ¡lisis #{i+1} - {patient['nombre']} {patient['apellido']} - {analysis['analysis_date'].strftime('%d/%m/%Y')}",
                'index': i,
                'patient': patient,
                'analysis': analysis
            })
    
    selected_analyses = st.multiselect(
        "Seleccionar anÃ¡lisis para enviar:",
        options=analysis_options,
        format_func=lambda x: x['label']
    )
    
    if selected_analyses:
        st.subheader("ðŸ“§ Configurar EnvÃ­o")
        
        # Destinatarios
        recipients = []
        for selected in selected_analyses:
            patient = selected['patient']
            if patient.get('email'):
                recipients.append(patient['email'])
        
        # Opciones de envÃ­o
        send_to_patient = st.checkbox("Enviar a pacientes", value=True)
        
        additional_emails = st.text_area(
            "Emails adicionales (separados por comas):",
            placeholder="doctor@hospital.com, admin@clinica.com"
        )
        
        if additional_emails:
            additional_list = [email.strip() for email in additional_emails.split(',')]
            recipients.extend(additional_list)
        
        # Personalizar email
        email_subject = st.text_input(
            "Asunto del email:",
            value="Resultados de AnÃ¡lisis ColposcÃ³pico"
        )
        
        email_body = st.text_area(
            "Mensaje personalizado:",
            value="""Estimado/a paciente,

Adjunto encontrarÃ¡ los resultados de su anÃ¡lisis colposcÃ³pico.

Por favor, consulte con su mÃ©dico tratante para la interpretaciÃ³n de los resultados.

Saludos cordiales,
Equipo MÃ©dico"""
        )
        
        # BotÃ³n de envÃ­o
        if st.button("ðŸ“§ Enviar Reportes", type="primary"):
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
                    
                    # Generar PDF
                    pdf_buffer = ReportGenerator.create_pdf_report(patient, analysis['results'])
                    
                    # Enviar a cada destinatario
                    patient_recipients = [patient.get('email')] if patient.get('email') else []
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
                                    st.success(f"âœ… Enviado a {recipient}")
                            else:
                                error_count += 1
                                with status_container:
                                    st.error(f"âŒ Error enviando a {recipient}: {message}")
                                    
                        except Exception as e:
                            error_count += 1
                            with status_container:
                                st.error(f"âŒ Error enviando a {recipient}: {str(e)}")
                
                # Resumen final
                st.success(f"ðŸŽ‰ Proceso completado: {success_count} enviados exitosamente, {error_count} errores")
                
            else:
                st.error("âš ï¸ Por favor complete la configuraciÃ³n SMTP y verifique que hay destinatarios vÃ¡lidos")
    
    # Historial de envÃ­os
    st.subheader("ðŸ“ Historial de EnvÃ­os")
    
    if 'email_history' not in st.session_state:
        st.session_state.email_history = []
    
    if st.session_state.email_history:
        df_history = pd.DataFrame(st.session_state.email_history)
        st.dataframe(df_history, use_container_width=True)
    else:
        st.info("No hay historial de envÃ­os disponible.")

def show_configuration():
    st.header("âš™ï¸ ConfiguraciÃ³n del Sistema")
    
    tab1, tab2, tab3, tab4 = st.tabs(["ðŸŽ¨ Apariencia", "ðŸ¤– Modelo IA", "ðŸ“§ Email", "ðŸ’¾ Datos"])
    
    with tab1:
        st.subheader("ConfiguraciÃ³n de Apariencia")
        
        # Tema
        theme = st.se
# Agregar estas mejoras al archivo app.py

import hashlib
import re
from datetime import timedelta

# 1. ValidaciÃ³n de datos mejorada
class DataValidator:
    @staticmethod
    def validate_email(email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_identification(identification):
        # Validar que solo contenga nÃºmeros y letras
        return identification.isalnum() and len(identification) >= 5
    
    @staticmethod
    def validate_patient_data(data):
        errors = []
        
        if not data.get('nombre') or len(data['nombre'].strip()) < 2:
            errors.append("Nombre debe tener al menos 2 caracteres")
        
        if not data.get('apellido') or len(data['apellido'].strip()) < 2:
            errors.append("Apellido debe tener al menos 2 caracteres")
        
        if not DataValidator.validate_identification(data.get('identificacion', '')):
            errors.append("IdentificaciÃ³n debe ser alfanumÃ©rica y tener al menos 5 caracteres")
        
        if data.get('email') and not DataValidator.validate_email(data['email']):
            errors.append("Formato de email invÃ¡lido")
        
        if data.get('edad', 0) < 0 or data.get('edad', 0) > 120:
            errors.append("Edad debe estar entre 0 y 120 aÃ±os")
        
        return errors

# 2. Persistencia mejorada
class DataPersistence:
    DATA_FILE = 'colpovision_data.pkl'
    
    @staticmethod
    def save_data():
        """Guardar datos en archivo"""
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
        """Cargar datos desde archivo"""
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
        """Guardado automÃ¡tico cada 5 minutos"""
        if 'last_save' not in st.session_state:
            st.session_state.last_save = datetime.now()
        
        if datetime.now() - st.session_state.last_save > timedelta(minutes=5):
            if DataPersistence.save_data():
                st.session_state.last_save = datetime.now()

# 3. Seguridad bÃ¡sica
class SecurityManager:
    @staticmethod
    def hash_password(password):
        """Hash de contraseÃ±a"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def verify_password(password, hashed):
        """Verificar contraseÃ±a"""
        return SecurityManager.hash_password(password) == hashed
    
    @staticmethod
    def sanitize_filename(filename):
        """Sanitizar nombre de archivo"""
        # Remover caracteres peligrosos
        safe_chars = re.sub(r'[^\w\s-]', '', filename)
        return re.sub(r'[-\s]+', '-', safe_chars)

# 4. Logging mejorado
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
        """Log de anÃ¡lisis realizado"""
        logger = logging.getLogger(__name__)
        logger.info(f"AnÃ¡lisis realizado - Paciente: {patient_id}, Tipo: {result_type}, Confianza: {confidence}")
    
    @staticmethod
    def log_error(error_msg, context=""):
        """Log de errores"""
        logger = logging.getLogger(__name__)
        logger.error(f"Error: {error_msg} - Contexto: {context}")

# 5. Mejoras en ImageAnalyzer
class EnhancedImageAnalyzer(ImageAnalyzer):
    @staticmethod
    def preprocess_image(image):
        """Preprocesamiento mejorado de imÃ¡genes"""
        import cv2
        import numpy as np
        from PIL import ImageEnhance
        
        # Convertir a array numpy
        img_array = np.array(image)
        
        # Mejorar contraste
        enhancer = ImageEnhance.Contrast(image)
        enhanced_img = enhancer.enhance(1.2)
        
        # Reducir ruido (simulado)
        # En producciÃ³n usar cv2.bilateralFilter o similar
        
        return enhanced_img
    
    @staticmethod
    def validate_image_quality(image):
        """Validar calidad de imagen"""
        # Convertir a array
        img_array = np.array(image)
        
        # Verificar dimensiones mÃ­nimas
        height, width = img_array.shape[:2]
        if height < 224 or width < 224:
            return False, "Imagen muy pequeÃ±a (mÃ­nimo 224x224)"
        
        # Verificar que no estÃ© completamente negra o blanca
        mean_intensity = np.mean(img_array)
        if mean_intensity < 10:
            return False, "Imagen muy oscura"
        if mean_intensity > 245:
            return False, "Imagen muy clara"
        
        return True, "Calidad aceptable"

# 6. ConfiguraciÃ³n centralizada
class Config:
    # ConfiguraciÃ³n por defecto
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
        """Cargar configuraciÃ³n"""
        if 'app_config' not in st.session_state:
            st.session_state.app_config = Config.DEFAULT_CONFIG.copy()
        return st.session_state.app_config
    
    @staticmethod
    def save_config(config):
        """Guardar configuraciÃ³n"""
        st.session_state.app_config = config
        # AquÃ­ se podrÃ­a guardar en archivo tambiÃ©n
        
    @staticmethod
    def get_config_value(path, default=None):
        """Obtener valor de configuraciÃ³n por ruta (ej: 'ui.theme')"""
        config = Config.load_config()
        keys = path.split('.')
        
        for key in keys:
            if isinstance(config, dict) and key in config:
                config = config[key]
            else:
                return default
        
        return config

# Modificar la funciÃ³n main para incluir mejoras
def enhanced_main():
    # Configurar logging
    Logger.setup_logging()
    
    # Cargar datos al inicio
    if 'data_loaded' not in st.session_state:
        DataPersistence.load_data()
        st.session_state.data_loaded = True
    
    # Guardado automÃ¡tico
    DataPersistence.auto_save()
    
    # Cargar configuraciÃ³n
    config = Config.load_config()
    
    # Resto del cÃ³digo main original...
    main()
    
    # Guardar datos al final
    DataPersistence.save_data()

# Para usar las mejoras, reemplazar la lÃ­nea final:
# if __name__ == "__main__":
#     enhanced_main()
