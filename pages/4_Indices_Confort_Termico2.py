# pages/4_Indices_Confort_Termico.py

import streamlit as st
import pandas as pd
import os
import numpy as np
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

st.header("🧮 Cálculo de Índices de Confort Térmico (ITH, ITGH, CTR)")

# --- Rutas base ---
base_path = r"C:\Proyectos\CattleClimate_Python"
data_path = os.path.join(base_path, "datos", "hidrometeorologicos")
glosario_path = os.path.join(base_path, "datos", "Glosario Variables.xlsx")

# --- Cargar glosario ---
glosario = pd.read_excel(glosario_path, sheet_name="Básicas")

# --- Buscar archivos ---
data_files = [f for f in os.listdir(data_path) if f.endswith(".data")]

# --- Identificar archivos por parámetro ---
def encontrar_archivo_por_parametro(parametro):
    fila = glosario[glosario["Parámetro"].str.contains(parametro, case=False, na=False)]
    if not fila.empty:
        etiqueta = fila.iloc[0]["Etiqueta"]
        for f in data_files:
            if f.startswith(etiqueta):
                return f
    return None

archivo_tbs = encontrar_archivo_por_parametro("bulbo seco")
archivo_tbh = encontrar_archivo_por_parametro("bulbo húmedo")
archivo_tr = encontrar_archivo_por_parametro("rocío")
archivo_vv = encontrar_archivo_por_parametro("viento")

st.markdown("### 1. Archivos detectados automáticamente")

col1, col2, col3, col4 = st.columns(4)
col1.write(f"🌡️ Tbs: {archivo_tbs if archivo_tbs else 'No encontrado'}")
col2.write(f"💧 Tbh: {archivo_tbh if archivo_tbh else 'No encontrado'}")
col3.write(f"🌫️ Tr: {archivo_tr if archivo_tr else 'No encontrado'}")
col4.write(f"💨 Vv: {archivo_vv if archivo_vv else 'No encontrado'}")

# --- Cargar variable ---
def cargar_variable(nombre_archivo):
    ruta = os.path.join(data_path, nombre_archivo)
    df = pd.read_csv(ruta, sep="|", names=["Fecha", "Valor"], engine="python")
    df["Fecha"] = pd.to_datetime(df["Fecha"], format="%Y-%m-%d %H:%M:%S", errors="coerce")
    df = df.dropna(subset=["Fecha"])
    return df.set_index("Fecha")["Valor"]

if st.button("🧮 Calcular Índices"):
    try:
        if not all([archivo_tbs, archivo_tbh, archivo_tr, archivo_vv]):
            st.error("Faltan archivos necesarios para calcular los índices.")
        else:
            tbs = cargar_variable(archivo_tbs)
            tbh = cargar_variable(archivo_tbh)
            tr = cargar_variable(archivo_tr)
            vv = cargar_variable(archivo_vv)

            df = pd.concat([tbs, tbh, tr, vv], axis=1)
            df.columns = ["Tbs", "Tbh", "Tr", "Vv"]

            # --- ITH ---
            df["ITH"] = 0.72 * (df["Tbs"] + df["Tbh"]) + 40.6

            # --- ITGH (ambiente externo) ---
            df["Tgn"] = 0.0162 * df["Tbs"]**2 + 0.8562 * df["Tbs"] - 0.9387
            df["ITGH"] = df["Tgn"] + 0.36 * df["Tr"] + 41.5

            # --- CTR ---
            Tbs_K = df["Tbs"] + 273.15
            Tgn_K = df["Tgn"] + 273.15
            TRM = 100 * np.sqrt(2.51 * df["Vv"]**0.5 * (df["Tgn"] - df["Tbs"])) + (df["Tgn"] / 100)**44
            sigma = 5.67e-8
            df["CTR"] = sigma * TRM**4

            st.success("Índices calculados correctamente.")
            st.dataframe(df[["Tbs", "Tbh", "Tr", "Vv", "ITH", "ITGH", "CTR"].copy()].head(100))

            st.download_button("⬇️ Descargar como CSV", data=df.to_csv(), file_name="indices_confort_termico.csv", mime="text/csv")

    except Exception as e:
        st.error(f"Error en cálculo: {e}")
