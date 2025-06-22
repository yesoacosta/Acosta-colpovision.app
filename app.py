import streamlit as st

# Prueba básica para verificar que Streamlit funciona
st.title("🔍 Prueba de Funcionamiento")
st.write("Si ves este mensaje, Streamlit está funcionando correctamente.")

try:
    import pandas as pd
    st.success("✅ Pandas importado correctamente")
except ImportError as e:
    st.error(f"❌ Error importando pandas: {e}")

try:
    import numpy as np
    st.success("✅ Numpy importado correctamente")
except ImportError as e:
    st.error(f"❌ Error importando numpy: {e}")

try:
    import plotly.express as px
    st.success("✅ Plotly importado correctamente")
except ImportError as e:
    st.error(f"❌ Error importando plotly: {e}")

try:
    from reportlab.lib.pagesizes import letter
    st.success("✅ Reportlab importado correctamente")
except ImportError as e:
    st.error(f"❌ Error importando reportlab: {e}")

try:
    import cv2
    st.success("✅ OpenCV importado correctamente")
except ImportError as e:
    st.error(f"❌ Error importando opencv: {e}")

st.write("---")
st.write("Si todas las importaciones están en verde, tu app debería funcionar.")
st.write("Si hay errores en rojo, necesitamos arreglar esas dependencias.")
