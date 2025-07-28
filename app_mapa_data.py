import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from pathlib import Path

st.set_page_config(layout="wide")

st.title("📍 Mapa + Datos de Estaciones Meteorológicas")

# Rutas
ruta_estaciones = Path("datos/estaciones_mapa.csv")
ruta_datos = Path("datos/hidrometeorologicos")

# Cargar estaciones
@st.cache_data
def cargar_estaciones():
    df = pd.read_csv(ruta_estaciones)
    return df.dropna(subset=["latitud", "longitud"])

estaciones = cargar_estaciones()

# Mapa con selección
st.subheader("Selecciona una estación desde el mapa")
muestra = estaciones.rename(columns={"latitud": "lat", "longitud": "lon"})

estacion_sel = st.selectbox("O selecciona por nombre:", muestra["nombre"].unique())
detalle = muestra[muestra["nombre"] == estacion_sel].iloc[0]
st.map(pd.DataFrame([detalle]))

# Mostrar detalles
st.markdown(f"**Código:** `{detalle.CODIGO}`")
st.markdown(f"**Departamento:** {detalle.DEPARTAMENTO} — **Municipio:** {detalle.MUNICIPIO}")

# Buscar archivo .data por código
codigo = str(detalle.CODIGO)
archivo_data = next(ruta_datos.glob(f"{codigo}*.data"), None)

if archivo_data:
    st.success(f"Archivo encontrado: {archivo_data.name}")
    
    # Leer archivo
    with open(archivo_data, "r", encoding="utf-8", errors="ignore") as f:
        lineas = f.readlines()

    if len(lineas) > 1:
        datos = lineas[1:]  # saltar encabezado
        fechas, valores = [], []
        for linea in datos:
            try:
                fecha = linea[:16].strip()
                valor = float(linea[16:].strip())
                fechas.append(pd.to_datetime(fecha))
                valores.append(valor)
            except:
                continue

        df_datos = pd.DataFrame({"Fecha": fechas, "Valor": valores})

        st.subheader("📈 Serie de tiempo")
        fig = px.line(df_datos, x="Fecha", y="Valor", title="Variable registrada")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📊 Resumen estadístico")
        st.dataframe(df_datos.describe())
    else:
        st.warning("El archivo está vacío o mal formado.")
else:
    st.error(f"No se encontró archivo .data para el código {codigo}")
