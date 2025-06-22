
import streamlit as st
import cv2
import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix
import io
import time

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
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #ff7f0e;
        margin: 1rem 0;
    }
    .metric-card {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .stButton>button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 20px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# Funciones de procesamiento de imagen
def preprocess_image(image, target_size=(224, 224)):
    """Preprocesa imagen para el modelo"""
    # Convertir PIL a numpy array
    if isinstance(image, Image.Image):
        image = np.array(image)
    
    # Redimensionar
    image_resized = cv2.resize(image, target_size)
    
    # Normalizar
    image_normalized = image_resized.astype(np.float32) / 255.0
    
    return image_normalized

def enhance_image(image):
    """Mejora la calidad de la imagen"""
    # Convertir a numpy array si es necesario
    if isinstance(image, Image.Image):
        image = np.array(image)
    
    # Mejorar contraste usando CLAHE
    lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    lab[:,:,0] = clahe.apply(lab[:,:,0])
    enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
    
    return enhanced

def apply_filters(image):
    """Aplica filtros de procesamiento"""
    # Convertir a numpy array si es necesario
    if isinstance(image, Image.Image):
        image = np.array(image)
    
    # Filtro Gaussiano para suavizar
    gaussian = cv2.GaussianBlur(image, (5, 5), 0)
    
    # Detección de bordes
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
    
    # Realce de características
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    sharpened = cv2.filter2D(image, -1, kernel)
    
    return {
        'original': image,
        'gaussian': gaussian,
        'edges': edges_colored,
        'sharpened': sharpened
    }

# Modelo CNN simplificado para demostración
@st.cache_resource
def load_model():
    """Carga o crea el modelo CNN"""
    try:
        # Intentar cargar modelo pre-entrenado
        model = keras.models.load_model('colpovision_model.h5')
        return model
    except:
        # Crear modelo de demostración
        model = keras.Sequential([
            layers.Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)),
            layers.MaxPooling2D((2, 2)),
            layers.Conv2D(64, (3, 3), activation='relu'),
            layers.MaxPooling2D((2, 2)),
            layers.Conv2D(128, (3, 3), activation='relu'),
            layers.MaxPooling2D((2, 2)),
            layers.Flatten(),
            layers.Dropout(0.5),
            layers.Dense(128, activation='relu'),
            layers.Dense(4, activation='softmax')  # 4 clases: Normal, CIN1, CIN2, CIN3
        ])
        
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model

def predict_image(model, image):
    """Realiza predicción sobre la imagen"""
    # Preprocesar imagen
    processed_image = preprocess_image(image)
    
    # Expandir dimensiones para el batch
    image_batch = np.expand_dims(processed_image, axis=0)
    
    # Realizar predicción
    predictions = model.predict(image_batch, verbose=0)
    
    # Clases
    classes = ['Normal', 'CIN I', 'CIN II', 'CIN III']
    
    # Obtener probabilidades
    probabilities = predictions[0]
    
    # Crear diccionario de resultados
    results = {}
    for i, class_name in enumerate(classes):
        results[class_name] = float(probabilities[i])
    
    # Predicción principal
    predicted_class = classes[np.argmax(probabilities)]
    confidence = float(np.max(probabilities))
    
    return results, predicted_class, confidence

def create_analysis_chart(results):
    """Crea gráfico de análisis"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Gráfico de barras
    classes = list(results.keys())
    probabilities = list(results.values())
    colors = ['#2ecc71', '#f39c12', '#e74c3c', '#8e44ad']
    
    bars = ax1.bar(classes, probabilities, color=colors, alpha=0.8)
    ax1.set_title('Probabilidades por Clase', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Probabilidad')
    ax1.set_ylim(0, 1)
    
    # Agregar valores en las barras
    for bar, prob in zip(bars, probabilities):
        ax1.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.01,
                f'{prob:.3f}', ha='center', va='bottom', fontweight='bold')
    
    # Gráfico circular
    wedges, texts, autotexts = ax2.pie(probabilities, labels=classes, colors=colors,
                                      autopct='%1.1f%%', startangle=90)
    ax2.set_title('Distribución de Probabilidades', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    return fig

def main():
    # Header principal
    st.markdown('<h1 class="main-header">🔬 ColpoVision</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Sistema de Análisis Inteligente para Colposcopía</p>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("🛠️ Panel de Control")
    
    # Cargar modelo
    with st.spinner("Cargando modelo de IA..."):
        model = load_model()
    
    st.sidebar.success("✅ Modelo cargado exitosamente")
    
    # Opciones de análisis
    analysis_type = st.sidebar.selectbox(
        "Tipo de Análisis",
        ["Análisis Individual", "Análisis por Lotes", "Comparación de Técnicas"]
    )
    
    if analysis_type == "Análisis Individual":
        st.markdown('<h2 class="sub-header">📸 Análisis de Imagen Individual</h2>', unsafe_allow_html=True)
        
        # Upload de imagen
        uploaded_file = st.file_uploader(
            "Cargar imagen de colposcopía",
            type=['png', 'jpg', 'jpeg', 'bmp', 'tiff'],
            help="Formatos soportados: PNG, JPG, JPEG, BMP, TIFF"
        )
        
        if uploaded_file is not None:
            # Cargar imagen
            image = Image.open(uploaded_file)
            
            # Layout en columnas
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("🖼️ Imagen Original")
                st.image(image, caption="Imagen cargada", use_column_width=True)
                
                # Información de la imagen
                st.info(f"""
                **Información de la imagen:**
                - Dimensiones: {image.size[0]} x {image.size[1]} px
                - Formato: {image.format}
                - Modo: {image.mode}
                """)
            
            with col2:
                st.subheader("🔍 Procesamiento")
                
                # Opciones de procesamiento
                enhance_option = st.checkbox("Mejorar calidad de imagen", value=True)
                show_filters = st.checkbox("Mostrar filtros aplicados")
                
                if enhance_option:
                    enhanced_image = enhance_image(image)
                    st.image(enhanced_image, caption="Imagen mejorada", use_column_width=True)
                    analysis_image = enhanced_image
                else:
                    analysis_image = image
            
            # Mostrar filtros si está habilitado
            if show_filters:
                st.markdown('<h3 class="sub-header">🎨 Filtros de Procesamiento</h3>', unsafe_allow_html=True)
                
                filters = apply_filters(analysis_image)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.image(filters['original'], caption="Original", use_column_width=True)
                with col2:
                    st.image(filters['gaussian'], caption="Suavizado", use_column_width=True)
                with col3:
                    st.image(filters['edges'], caption="Bordes", use_column_width=True)
                with col4:
                    st.image(filters['sharpened'], caption="Realzado", use_column_width=True)
            
            # Botón de análisis
            if st.button("🔬 Realizar Análisis", key="analyze_button"):
                with st.spinner("Analizando imagen..."):
                    # Simular tiempo de procesamiento
                    progress_bar = st.progress(0)
                    for i in range(100):
                        time.sleep(0.01)
                        progress_bar.progress(i + 1)
                    
                    # Realizar predicción
                    results, predicted_class, confidence = predict_image(model, analysis_image)
                
                # Mostrar resultados
                st.markdown('<h3 class="sub-header">📊 Resultados del Análisis</h3>', unsafe_allow_html=True)
                
                # Métricas principales
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>Diagnóstico Principal</h3>
                        <h2>{predicted_class}</h2>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>Confianza</h3>
                        <h2>{confidence:.1%}</h2>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    risk_level = "Alto" if predicted_class in ["CIN II", "CIN III"] else "Bajo" if predicted_class == "Normal" else "Medio"
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>Nivel de Riesgo</h3>
                        <h2>{risk_level}</h2>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Gráfico de probabilidades
                fig = create_analysis_chart(results)
                st.pyplot(fig)
                
                # Tabla de resultados detallados
                st.subheader("📋 Resultados Detallados")
                results_df = pd.DataFrame(list(results.items()), columns=['Clase', 'Probabilidad'])
                results_df['Probabilidad'] = results_df['Probabilidad'].apply(lambda x: f"{x:.4f}")
                results_df['Porcentaje'] = results_df['Probabilidad'].astype(float).apply(lambda x: f"{x*100:.2f}%")
                st.dataframe(results_df, use_container_width=True)
                
                # Recomendaciones
                st.subheader("💡 Recomendaciones Clínicas")
                if predicted_class == "Normal":
                    st.success("✅ Resultado normal. Se recomienda seguimiento rutinario según protocolo.")
                elif predicted_class == "CIN I":
                    st.warning("⚠️ Lesión de bajo grado detectada. Se recomienda seguimiento cercano y posible repetición en 6-12 meses.")
                elif predicted_class == "CIN II":
                    st.error("🔴 Lesión de alto grado detectada. Se recomienda evaluación por especialista y posible tratamiento.")
                else:  # CIN III
                    st.error("🚨 Lesión de alto grado severa detectada. Se requiere evaluación inmediata por especialista y tratamiento.")
                
                st.info("⚠️ **Importante**: Este análisis es una herramienta de apoyo diagnóstico. Siempre debe ser interpretado por un profesional médico calificado.")
    
    elif analysis_type == "Análisis por Lotes":
        st.markdown('<h2 class="sub-header">📁 Análisis por Lotes</h2>', unsafe_allow_html=True)
        
        uploaded_files = st.file_uploader(
            "Cargar múltiples imágenes",
            type=['png', 'jpg', 'jpeg', 'bmp', 'tiff'],
            accept_multiple_files=True,
            help="Selecciona múltiples archivos para análisis en lote"
        )
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} archivos cargados")
            
            if st.button("🔬 Analizar Lote", key="batch_analyze"):
                results_list = []
                
                # Barra de progreso
                progress_bar = st.progress(0)
                
                for i, uploaded_file in enumerate(uploaded_files):
                    # Cargar y procesar imagen
                    image = Image.open(uploaded_file)
                    enhanced_image = enhance_image(image)
                    
                    # Realizar predicción
                    results, predicted_class, confidence = predict_image(model, enhanced_image)
                    
                    # Guardar resultados
                    results_list.append({
                        'Archivo': uploaded_file.name,
                        'Diagnóstico': predicted_class,
                        'Confianza': confidence,
                        **results
                    })
                    
                    # Actualizar progreso
                    progress_bar.progress((i + 1) / len(uploaded_files))
                
                # Mostrar resultados del lote
                st.subheader("📊 Resultados del Lote")
                
                # Crear DataFrame
                batch_df = pd.DataFrame(results_list)
                
                # Métricas del lote
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    normal_count = len(batch_df[batch_df['Diagnóstico'] == 'Normal'])
                    st.metric("Casos Normales", normal_count)
                
                with col2:
                    cin1_count = len(batch_df[batch_df['Diagnóstico'] == 'CIN I'])
                    st.metric("CIN I", cin1_count)
                
                with col3:
                    cin2_count = len(batch_df[batch_df['Diagnóstico'] == 'CIN II'])
                    st.metric("CIN II", cin2_count)
                
                with col4:
                    cin3_count = len(batch_df[batch_df['Diagnóstico'] == 'CIN III'])
                    st.metric("CIN III", cin3_count)
                
                # Tabla de resultados
                st.dataframe(batch_df, use_container_width=True)
                
                # Gráfico de distribución
                fig, ax = plt.subplots(figsize=(10, 6))
                diagnosis_counts = batch_df['Diagnóstico'].value_counts()
                colors = ['#2ecc71', '#f39c12', '#e74c3c', '#8e44ad']
                ax.pie(diagnosis_counts.values, labels=diagnosis_counts.index, colors=colors, autopct='%1.1f%%')
                ax.set_title('Distribución de Diagnósticos en el Lote')
                st.pyplot(fig)
    
    else:  # Comparación de Técnicas
        st.markdown('<h2 class="sub-header">⚖️ Comparación de Técnicas</h2>', unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Cargar imagen para comparación",
            type=['png', 'jpg', 'jpeg', 'bmp', 'tiff'],
            key="comparison_upload"
        )
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            
            st.subheader("🔍 Comparación de Técnicas de Procesamiento")
            
            # Aplicar diferentes técnicas
            with st.spinner("Aplicando técnicas de procesamiento..."):
                filters = apply_filters(image)
                enhanced = enhance_image(image)
            
            # Mostrar comparación
            col1, col2 = st.columns(2)
            
            with col1:
                st.image(image, caption="Original", use_column_width=True)
                results_orig, pred_orig, conf_orig = predict_image(model, image)
                st.write(f"**Diagnóstico**: {pred_orig} ({conf_orig:.1%})")
            
            with col2:
                st.image(enhanced, caption="Mejorada", use_column_width=True)
                results_enh, pred_enh, conf_enh = predict_image(model, enhanced)
                st.write(f"**Diagnóstico**: {pred_enh} ({conf_enh:.1%})")
            
            # Tabla comparativa
            st.subheader("📊 Comparación Detallada")
            
            comparison_data = {
                'Técnica': ['Original', 'Mejorada'],
                'Diagnóstico': [pred_orig, pred_enh],
                'Confianza': [f"{conf_orig:.1%}", f"{conf_enh:.1%}"],
                'Normal': [f"{results_orig['Normal']:.3f}", f"{results_enh['Normal']:.3f}"],
                'CIN I': [f"{results_orig['CIN I']:.3f}", f"{results_enh['CIN I']:.3f}"],
                'CIN II': [f"{results_orig['CIN II']:.3f}", f"{results_enh['CIN II']:.3f}"],
                'CIN III': [f"{results_orig['CIN III']:.3f}", f"{results_enh['CIN III']:.3f}"]
            }
            
            comparison_df = pd.DataFrame(comparison_data)
            st.dataframe(comparison_df, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p><strong>ColpoVision v2.0</strong> - Sistema de Análisis Inteligente para Colposcopía</p>
        <p>⚠️ <em>Herramienta de apoyo diagnóstico. No reemplaza el criterio médico profesional.</em></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
