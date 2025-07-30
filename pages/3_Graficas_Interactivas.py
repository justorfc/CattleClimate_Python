# pages/3_Graficas_Interactivas.py

import streamlit as st
import pandas as pd
import os
import plotly.express as px
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

st.header("📈 Gráficas Interactivas por Estación o Variable")

# --- Rutas base ---
base_path = r"C:\Proyectos\CattleClimate_Python"
data_path = os.path.join(base_path, "datos", "hidrometeorologicos")
glosario_path = os.path.join(base_path, "datos", "Glosario Variables.xlsx")
cne_path = os.path.join(base_path, "datos", "CNE_IDEAM.xlsx")

# --- Cargar auxiliares ---
glosario = pd.read_excel(glosario_path, sheet_name="Básicas")
cne = pd.read_excel(cne_path, sheet_name="CNE")

# --- Buscar archivos ---
data_files = [f for f in os.listdir(data_path) if f.endswith(".data")]

@st.cache_data(show_spinner=True)
def cargar_todo():
    total = []
    for file in data_files:
        try:
            etiqueta, codigo = file.replace(".data", "").split("@")
            ruta = os.path.join(data_path, file)
            df = pd.read_csv(ruta, sep="|", names=["Fecha", "Valor"], engine="python")
            df["Archivo"] = file
            df["Etiqueta"] = etiqueta
            df["Codigo"] = codigo

            meta_est = cne[cne["CODIGO"] == int(codigo)]
            if not meta_est.empty:
                for col in ["nombre", "DEPARTAMENTO", "MUNICIPIO"]:
                    df[col] = meta_est.iloc[0][col]

            total.append(df)
        except:
            continue
    return pd.concat(total, ignore_index=True) if total else pd.DataFrame()

# --- Carga de datos ---
df = cargar_todo()

if not df.empty:
    # df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df["Fecha"] = pd.to_datetime(df["Fecha"], format="%Y-%m-%d %H:%M:%S", errors="coerce")
    df = df.dropna(subset=["Fecha"])

    col1, col2 = st.columns(2)

    with col1:
        estacion = st.selectbox("📍 Seleccione una estación", options=sorted(df["nombre"].dropna().unique()))
    with col2:
        variable = st.selectbox("📌 Seleccione una variable (Etiqueta)", options=sorted(df["Etiqueta"].unique()))

    df_filtrado = df[(df["nombre"] == estacion) & (df["Etiqueta"] == variable)]

    st.markdown(f"#### Serie temporal: {variable} en {estacion}")
    fig = px.line(df_filtrado, x="Fecha", y="Valor", title=f"{variable} - {estacion}", markers=True)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("No se encontraron datos para graficar.")
