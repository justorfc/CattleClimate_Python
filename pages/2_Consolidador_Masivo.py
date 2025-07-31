# pages/2_Consolidador_Masivo.py

import streamlit as st
import pandas as pd
from pathlib import Path
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

st.header("📊 Consolidador Masivo de Archivos .data")

# --- Rutas base (multiplataforma) ---
BASE_DIR = Path(__file__).parent.parent  # Raíz del proyecto
DATA_DIR = BASE_DIR / "datos"
DATA_HIDRO = DATA_DIR / "hidrometeorologicos"
GLOSARIO_PATH = DATA_DIR / "Glosario Variables.xlsx"
CNE_PATH = DATA_DIR / "CNE_IDEAM.xlsx"

# --- Cargar auxiliares ---
try:
    glosario = pd.read_excel(GLOSARIO_PATH, sheet_name="Básicas")
    cne = pd.read_excel(CNE_PATH, sheet_name="CNE")
except Exception as e:
    st.error(f"Error cargando archivos auxiliares: {e}")
    st.stop()

# --- Buscar archivos con pathlib ---
data_files = [f.name for f in DATA_HIDRO.glob("*.data")]  # Lista multiplataforma

@st.cache_data(show_spinner=True)
def cargar_datos_masivos():
    todos = []
    for archivo in data_files:
        try:
            etiqueta, codigo = archivo.replace(".data", "").split("@")
            ruta = DATA_HIDRO / archivo  # Ruta compatible con ambos OS
            
            df = pd.read_csv(ruta, sep="|", names=["Fecha", "Valor"], engine="python")
            df["Archivo"] = archivo
            df["Etiqueta"] = etiqueta
            df["Codigo"] = codigo

            # Metadatos (variables)
            meta_var = glosario[glosario["Etiqueta"] == etiqueta]
            if not meta_var.empty:
                df = df.assign(**meta_var.iloc[0].to_dict())

            # Metadatos (estaciones)
            meta_est = cne[cne["CODIGO"] == int(codigo)]
            if not meta_est.empty:
                df = df.assign(**meta_est.iloc[0].to_dict())

            todos.append(df)
        except Exception as e:
            st.warning(f"No se pudo procesar {archivo}: {str(e)}")
    return pd.concat(todos, ignore_index=True) if todos else pd.DataFrame()

# --- Interfaz ---
st.info("Procesando archivos .data...")
df_total = cargar_datos_masivos()

if not df_total.empty:
    st.success(f"✅ {len(df_total)} registros de {df_total['Archivo'].nunique()} archivos procesados")

    # --- Filtros ---
    col1, col2 = st.columns(2)
    etiquetas = df_total["Etiqueta"].unique()
    departamentos = df_total["DEPARTAMENTO"].dropna().unique()

    with col1:
        filtro_etiqueta = st.selectbox("📌 Filtrar por variable", ["Todas"] + sorted(etiquetas))
    with col2:
        filtro_departamento = st.selectbox("📍 Filtrar por departamento", ["Todos"] + sorted(departamentos))

    # Aplicar filtros
    df_filtrado = df_total.copy()
    if filtro_etiqueta != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Etiqueta"] == filtro_etiqueta]
    if filtro_departamento != "Todos":
        df_filtrado = df_filtrado[df_filtrado["DEPARTAMENTO"] == filtro_departamento]

    # Mostrar resultados
    st.dataframe(df_filtrado.head(1000), use_container_width=True)

    # Botón de descarga
    st.download_button(
        "⬇️ Descargar CSV filtrado",
        data=df_filtrado.to_csv(index=False, encoding="utf-8-sig"),
        file_name="datos_consolidados.csv",
        mime="text/csv"
    )
else:
    st.error("❌ No se encontraron archivos .data válidos")