# pages/1_Explorador_Data.py

import streamlit as st
import pandas as pd
import os

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

st.header("📂 Explorador de Archivos .data")

# --- Rutas base ---
base_path = r"C:\Proyectos\CattleClimate_Python"
data_path = os.path.join(base_path, "datos", "hidrometeorologicos")
glosario_path = os.path.join(base_path, "datos", "Glosario Variables.xlsx")
cne_path = os.path.join(base_path, "datos", "CNE_IDEAM.xlsx")

# --- Cargar auxiliares ---
glosario = pd.read_excel(glosario_path, sheet_name="Básicas")
cne = pd.read_excel(cne_path, sheet_name="CNE")

# --- Listar archivos .data ---
data_files = [f for f in os.listdir(data_path) if f.endswith(".data")]
archivo = st.selectbox("Seleccione un archivo .data", options=data_files)

if archivo:
    etiqueta, codigo = archivo.replace(".data", "").split("@")
    ruta_archivo = os.path.join(data_path, archivo)

    # Cargar datos
    try:
        df = pd.read_csv(ruta_archivo, sep="|", names=["Fecha", "Valor"], engine="python")
        df["Etiqueta"] = etiqueta
        df["Codigo"] = codigo

        st.success(f"Archivo: {archivo} cargado correctamente")

        info_var = glosario[glosario["Etiqueta"] == etiqueta]
        info_est = cne[cne["CODIGO"] == int(codigo)]

        if not info_var.empty:
            st.subheader("🔎 Información de la variable")
            st.dataframe(info_var)

        if not info_est.empty:
            st.subheader("📍 Información de la estación")
            st.dataframe(info_est)

        st.subheader("📄 Vista previa de datos")
        st.dataframe(df.head(100))

    except Exception as e:
        st.error(f"Error al cargar archivo: {e}")
