import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px

# Configuración inicial
st.set_page_config(page_title="CattleClimate", layout="wide")

st.title("📡 CattleClimate - Visualizador de Datos Meteorológicos")

# Ruta a los datos
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "datos", "hidrometeorologicos")

# Listar archivos .data disponibles
archivos = [f for f in os.listdir(DATA_DIR) if f.endswith(".data")]

if not archivos:
    st.warning("No se encontraron archivos .data en la carpeta 'datos/hidrometeorologicos'.")
    st.stop()

# Selección de archivo
archivo_seleccionado = st.selectbox("Selecciona un archivo .data", archivos)

# Leer archivo
ruta_archivo = os.path.join(DATA_DIR, archivo_seleccionado)

with open(ruta_archivo, "r", encoding="utf-8") as f:
    lineas = f.readlines()

# Mostrar etiqueta y código
etiqueta_info = lineas[0].strip()
st.markdown(f"**Etiqueta y código de estación:** `{etiqueta_info}`")

# Leer los datos (líneas desde la segunda)
datos_crudos = [line.strip() for line in lineas[1:]]

# Mostrar las primeras 5 líneas crudas para inspección
st.markdown("### 🛠 Primeras líneas del archivo:")
st.code("\n".join(datos_crudos[:5]), language="text")

# Nueva lógica de separación por '|'
fechas = []
valores = []

for linea in datos_crudos:
    try:
        parte_fecha, parte_valor = linea.split("|")
        fecha = datetime.strptime(parte_fecha.strip(), "%Y-%m-%d %H:%M:%S")
        valor = float(parte_valor.strip())

        fechas.append(fecha)
        valores.append(valor)

    except Exception as e:
        continue  # O puedes usar st.warning(str(e)) si quieres mostrar el error


# Mostrar tabla
if fechas:
    df = pd.DataFrame({"FechaHora": fechas, "Valor": valores})
    st.subheader("📊 Datos leídos del archivo")
    st.dataframe(df.head(10))

    st.subheader("📈 Gráfico de serie temporal")

    fig = px.line(df, x="FechaHora", y="Valor",
              title="Serie temporal del archivo seleccionado",
              labels={"FechaHora": "Fecha y Hora", "Valor": "Valor registrado"})

    fig.update_layout(xaxis_title="Fecha", yaxis_title="Valor",
                  xaxis=dict(rangeslider_visible=True))

    st.plotly_chart(fig, use_container_width=True)

else:
    st.error("No se pudieron interpretar los datos del archivo seleccionado. Verifica el formato.")

