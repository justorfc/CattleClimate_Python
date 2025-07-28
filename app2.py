import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px

# Configuración inicial de la página
st.set_page_config(page_title="CattleClimate", layout="wide")
st.title("📡 CattleClimate - Visualizador de Datos Meteorológicos")

# Ruta al directorio de datos
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "datos", "hidrometeorologicos")

# Listar archivos .data
archivos = [f for f in os.listdir(DATA_DIR) if f.endswith(".data")]

if not archivos:
    st.warning("⚠️ No se encontraron archivos .data en la carpeta 'datos/hidrometeorologicos'.")
    st.stop()

# Selección del archivo
archivo_seleccionado = st.selectbox("Selecciona un archivo .data", archivos)

# Leer contenido
ruta_archivo = os.path.join(DATA_DIR, archivo_seleccionado)
with open(ruta_archivo, "r", encoding="utf-8") as f:
    lineas = f.readlines()

# Mostrar primera línea como encabezado
etiqueta_info = lineas[0].strip()
st.markdown(f"**Etiqueta y código de estación:** `{etiqueta_info}`")

# Mostrar primeras líneas del archivo
datos_crudos = [line.strip() for line in lineas[1:]]
st.markdown("### 🛠 Primeras líneas del archivo:")
st.code("\n".join(datos_crudos[:5]), language="text")

# Procesar los datos
fechas = []
valores = []

for linea in datos_crudos:
    try:
        parte_fecha, parte_valor = linea.split("|")
        fecha = datetime.strptime(parte_fecha.strip(), "%Y-%m-%d %H:%M:%S")
        valor = float(parte_valor.strip())
        fechas.append(fecha)
        valores.append(valor)
    except Exception:
        continue

# Validar si se pudo construir el DataFrame
if fechas:
    df = pd.DataFrame({"FechaHora": fechas, "Valor": valores})

    st.subheader("📊 Datos leídos del archivo")
    st.dataframe(df.head(10))

    # ✅ Nuevo: Filtro por rango de fechas
    st.subheader("📆 Filtro de rango de fechas")

    min_fecha = df["FechaHora"].min().date()
    max_fecha = df["FechaHora"].max().date()

    rango = st.date_input(
        "Selecciona el rango de fechas:",
        value=(min_fecha, max_fecha),
        min_value=min_fecha,
        max_value=max_fecha
    )

    if isinstance(rango, tuple) and len(rango) == 2:
        df_filtrado = df[(df["FechaHora"].dt.date >= rango[0]) & (df["FechaHora"].dt.date <= rango[1])]
    else:
        df_filtrado = df.copy()

    # Gráfico con Plotly
    st.subheader("📈 Gráfico de serie temporal")

    if not df_filtrado.empty:
        fig = px.line(df_filtrado, x="FechaHora", y="Valor",
                      title="Serie temporal del archivo seleccionado",
                      labels={"FechaHora": "Fecha", "Valor": "Valor registrado"})

        fig.update_layout(xaxis_title="Fecha", yaxis_title="Valor",
                          xaxis=dict(rangeslider_visible=True))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ No hay datos disponibles en el rango seleccionado.")

else:
    st.error("No se pudieron interpretar los datos del archivo seleccionado. Verifica el formato.")
