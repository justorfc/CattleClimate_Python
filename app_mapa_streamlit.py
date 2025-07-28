import streamlit as st
import pandas as pd

# Título
st.title("Mapa de Estaciones Meteorológicas - IDEAM")

# Cargar los datos
@st.cache_data
def cargar_estaciones():
    df = pd.read_csv("datos/estaciones_mapa.csv")
    return df.dropna(subset=["latitud", "longitud"])

estaciones = cargar_estaciones()

# Filtros
departamentos = sorted(estaciones["DEPARTAMENTO"].dropna().unique())
departamento_sel = st.selectbox("Filtrar por departamento:", ["Todos"] + departamentos)

if departamento_sel != "Todos":
    estaciones = estaciones[estaciones["DEPARTAMENTO"] == departamento_sel]

# Mapa
st.subheader("Ubicación de estaciones")
muestra = estaciones.rename(columns={"latitud": "lat", "longitud": "lon"})
st.map(muestra)

# Tabla opcional
with st.expander("Ver tabla de estaciones"):
    st.dataframe(estaciones)

# Pie de página
st.caption("Proyecto AGRISOS BIOCLIMÁTICA - Visualización geoespacial con Streamlit")
