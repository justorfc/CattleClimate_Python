# streamlit_app.py
# Archivo principal que lanza la app multipágina

import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="CattleClimate: Análisis BioClimático Ganadero",
    layout="wide"
)

st.title("🐄🌦️ CattleClimate")
st.markdown("""
Bienvenido a la plataforma interactiva para el análisis de confort térmico en ganado vacuno.

Use la barra lateral para navegar por las diferentes herramientas disponibles:
- Exploración individual de archivos `.data`
- Consolidación masiva
- Gráficas interactivas
- Cálculo de índices ITH, ITGH, CTR
- Exportación de resultados
""")
