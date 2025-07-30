# pages/2_Consolidador_Masivo.py

import streamlit as st
import pandas as pd
import os
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

st.header("📊 Consolidador Masivo de Archivos .data")

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
def cargar_datos_masivos():
    todos = []
    for archivo in data_files:
        try:
            etiqueta, codigo = archivo.replace(".data", "").split("@")
            ruta = os.path.join(data_path, archivo)
            df = pd.read_csv(ruta, sep="|", names=["Fecha", "Valor"], engine="python")
            df["Archivo"] = archivo
            df["Etiqueta"] = etiqueta
            df["Codigo"] = codigo

            # Metadatos
            meta_var = glosario[glosario["Etiqueta"] == etiqueta]
            if not meta_var.empty:
                for col in meta_var.columns:
                    df[col] = meta_var.iloc[0][col]

            meta_est = cne[cne["CODIGO"] == int(codigo)]
            if not meta_est.empty:
                for col in meta_est.columns:
                    df[col] = meta_est.iloc[0][col]

            todos.append(df)
        except Exception as e:
            st.warning(f"No se pudo procesar {archivo}: {e}")
    return pd.concat(todos, ignore_index=True) if todos else pd.DataFrame()

# --- Ejecutar carga ---
st.info("Procesando archivos .data...")
df_total = cargar_datos_masivos()

if not df_total.empty:
    st.success(f"{len(df_total)} registros procesados de {df_total['Archivo'].nunique()} archivos.")

    # --- Filtros ---
    col1, col2 = st.columns(2)
    etiquetas = df_total["Etiqueta"].unique()
    departamentos = df_total["DEPARTAMENTO"].dropna().unique()

    with col1:
        filtro_etiqueta = st.selectbox("📌 Filtrar por variable (Etiqueta)", options=["Todas"] + sorted(etiquetas))
    with col2:
        filtro_departamento = st.selectbox("📍 Filtrar por departamento", options=["Todos"] + sorted(departamentos))

    df_filtrado = df_total.copy()
    if filtro_etiqueta != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Etiqueta"] == filtro_etiqueta]
    if filtro_departamento != "Todos":
        df_filtrado = df_filtrado[df_filtrado["DEPARTAMENTO"] == filtro_departamento]

    st.dataframe(df_filtrado.head(1000), use_container_width=True)

    st.download_button(
        "⬇️ Descargar como CSV",
        data=df_filtrado.to_csv(index=False),
        file_name="datos_filtrados.csv",
        mime="text/csv"
    )
else:
    st.error("No se pudieron consolidar los datos.")
