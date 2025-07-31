# pages/4_Indices_Confort_Termico.py
import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

st.header("🧮 Cálculo de Índices de Confort Térmico (ITH, ITGH, CTR)")

# --- Rutas base multiplataforma ---
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "datos"
DATA_HIDRO = DATA_DIR / "hidrometeorologicos"
GLOSARIO_PATH = DATA_DIR / "Glosario Variables.xlsx"
CNE_PATH = DATA_DIR / "CNE_IDEAM.xlsx"

# --- Buscar archivos con pathlib ---
data_files = [f.name for f in DATA_HIDRO.glob("*.data") if f.is_file()]

# --- Selección de archivos requeridos ---
st.markdown("### 1. Seleccione las variables requeridas")

col1, col2, col3, col4 = st.columns(4)
with col1:
    archivo_tbs = st.selectbox(
        "🌡️ Tbs (bulbo seco)", 
        [f for f in data_files if "TBS" in f.upper()],
        index=0 if any("TBS" in f.upper() for f in data_files) else None
    )
with col2:
    archivo_tbh = st.selectbox(
        "💧 Tbh (bulbo húmedo)", 
        [f for f in data_files if "TBH" in f.upper()],
        index=0 if any("TBH" in f.upper() for f in data_files) else None
    )
with col3:
    archivo_tr = st.selectbox(
        "🌫️ Tr (rocío)", 
        [f for f in data_files if "TR" in f.upper()],
        index=0 if any("TR" in f.upper() for f in data_files) else None
    )
with col4:
    archivo_vv = st.selectbox(
        "💨 Vv (viento)", 
        [f for f in data_files if "VV" in f.upper()],
        index=0 if any("VV" in f.upper() for f in data_files) else None
    )

# --- Función mejorada para cargar variables ---
def cargar_variable_segura(nombre_archivo):
    """Carga los datos con manejo robusto de errores"""
    try:
        ruta = DATA_HIDRO / nombre_archivo
        df = pd.read_csv(
            ruta,
            sep="|",
            names=["Fecha", "Valor"],
            engine="python",
            dtype={"Valor": "object"},
            na_values=["?", "-", "NaN", "NA", "", "null"],
            on_bad_lines="warn"
        )
        
        # Conversión segura de tipos
        df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")
        df["Fecha"] = pd.to_datetime(df["Fecha"], format="%Y-%m-%d %H:%M:%S", errors="coerce")
        
        # Eliminar filas con problemas
        df = df.dropna(subset=["Fecha", "Valor"])
        
        if df.empty:
            st.warning(f"Archivo {nombre_archivo} no contiene datos válidos")
            return None
            
        return df.set_index("Fecha")["Valor"]
        
    except Exception as e:
        st.error(f"Error al cargar {nombre_archivo}: {str(e)}")
        return None

# --- Cálculo de índices ---
if st.button("🧮 Calcular Índices", type="primary"):
    with st.spinner("Calculando índices..."):
        try:
            # Cargar variables con verificación
            tbs = cargar_variable_segura(archivo_tbs)
            tbh = cargar_variable_segura(archivo_tbh)
            tr = cargar_variable_segura(archivo_tr)
            vv = cargar_variable_segura(archivo_vv)
            
            if None in [tbs, tbh, tr, vv]:
                st.error("No se pudieron cargar todos los archivos necesarios")
                st.stop()
            
            # Unificar datos
            df = pd.concat([tbs, tbh, tr, vv], axis=1, join="inner")
            df.columns = ["Tbs", "Tbh", "Tr", "Vv"]
            
            if df.empty:
                st.error("No hay datos coincidentes en el rango temporal")
                st.stop()
            
            # --- Cálculo de índices con manejo de NaN ---
            # ITH (Índice de Temperatura y Humedad)
            df["ITH"] = 0.72 * (df["Tbs"] + df["Tbh"]) + 40.6
            
            # ITGH (Índice de Temperatura de Globo y Humedad)
            df["Tgn"] = 0.0162 * df["Tbs"]**2 + 0.8562 * df["Tbs"] - 0.9387
            df["ITGH"] = df["Tgn"] + 0.36 * df["Tr"] + 41.5
            
            # CTR (Carga Térmica Radiante)
            Tbs_K = df["Tbs"] + 273.15
            Tgn_K = df["Tgn"] + 273.15
            df["CTR"] = 5.67e-8 * (100 * np.sqrt(2.51 * df["Vv"]**0.5 * (df["Tgn"] - df["Tbs"])) + (df["Tgn"] / 100)**44)**4
            
            # Mostrar resultados
            st.success("✅ Índices calculados correctamente")
            
            # Resumen estadístico
            with st.expander("📊 Resumen Estadístico", expanded=True):
                st.dataframe(df.describe().T)
            
            # Gráfico interactivo
            st.markdown("### 📈 Evolución Temporal de los Índices")
            fig = px.line(
                df[["ITH", "ITGH", "CTR"]],
                labels={"value": "Valor del Índice", "variable": "Índice"},
                title="Variación de Índices de Confort Térmico"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Datos completos (mostrar solo 100 filas)
            st.markdown("### 📝 Datos Detallados (muestra)")
            st.dataframe(df.head(100))
            
            # Botón de descarga
            csv = df.to_csv().encode('utf-8')
            st.download_button(
                "⬇️ Descargar CSV Completo",
                data=csv,
                file_name="indices_confort_termico.csv",
                mime="text/csv",
                help="Descargue todos los datos calculados en formato CSV"
            )
            
        except Exception as e:
            st.error(f"❌ Error en los cálculos: {str(e)}")
            st.error("Verifique que los archivos tengan el formato correcto y datos válidos")