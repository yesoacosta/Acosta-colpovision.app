🔬 ColpoVision - Sistema de Análisis Inteligente para Colposcopía

Sistema web de análisis de imágenes de colposcopía utilizando inteligencia artificial para apoyo diagnóstico.

## 🚀 Características

- **Análisis Individual**: Procesamiento y análisis de imágenes individuales
- **Análisis por Lotes**: Procesamiento múltiple de imágenes
- **Comparación de Técnicas**: Evaluación de diferentes métodos de procesamiento
- **Interfaz Intuitiva**: Diseño moderno y fácil de usar
- **Resultados Detallados**: Probabilidades, gráficos y recomendaciones clínicas

## 📋 Requisitos

- Python 3.8+
- Dependencias listadas en `requirements.txt`

## 🛠️ Instalación Local

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/colpovision-app.git
cd colpovision-app

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
streamlit run app.py
```

## ☁️ Despliegue en Streamlit Cloud

### Paso 1: Preparar Repositorio
1. Sube estos archivos a tu repositorio GitHub privado:
   - `app.py` (aplicación principal)
   - `requirements.txt` (dependencias)
   - `README.md` (este archivo)

### Paso 2: Desplegar
1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Inicia sesión con GitHub
3. Selecciona "New app"
4. Configura:
   - **Repository**: tu-usuario/colpovision-app
   - **Branch**: main
   - **Main file path**: app.py
5. Haz clic en "Deploy"

### Paso 3: Acceder
- Tu aplicación estará disponible en: `https://tu-usuario-colpovision-app-main-xxx.streamlit.app`
- Accesible desde cualquier dispositivo con internet

## 📱 Uso

### Análisis Individual
1. Carga una imagen de colposcopía
2. Selecciona opciones de procesamiento
3. Haz clic en "Realizar Análisis"
4. Revisa resultados y recomendaciones

### Análisis por Lotes
1. Selecciona "Análisis por Lotes"
2. Carga múltiples imágenes
3. Ejecuta análisis en lote
4. Revisa estadísticas y resultados

### Comparación de Técnicas
1. Selecciona "Comparación de Técnicas"
2. Carga una imagen
3. Compara resultados entre técnicas

## ⚠️ Consideraciones Importantes

- **Uso Médico**: Esta herramienta es de apoyo diagnóstico únicamente
- **Supervisión Profesional**: Siempre requiere interpretación médica
- **Privacidad**: Maneja datos médicos de forma segura
- **Limitaciones**: El modelo es demostrativo y requiere entrenamiento específico

## 🔧 Configuración Avanzada

### Variables de Entorno (Streamlit Cloud)
Si necesitas configurar variables especiales:

1. En Streamlit Cloud, ve a tu app
2. Click en "Settings" → "Secrets"
3. Agrega configuraciones en formato TOML:

```toml
[general]
model_path = "ruta/al/modelo"
api_key = "tu_api_key"
```

### Personalización
- Modifica colores en la sección CSS del archivo `app.py`
- Ajusta parámetros del modelo en la función `load_model()`
- Personaliza clases de diagnóstico según necesidades

## 📞 Soporte

Para problemas o preguntas:
1. Revisa la documentación de Streamlit
2. Verifica logs en Streamlit Cloud
3. Consulta la sección de issues del repositorio

## 📄 Licencia

Proyecto educativo y de investigación. Uso responsable requerido para aplicaciones médicas.

---

**⚠️ Descargo de Responsabilidad**: Esta aplicación es una herramienta de apoyo diagnóstico y no reemplaza el criterio médico profesional. Siempre consulta con un especialista calificado para diagnósticos definitivos.
