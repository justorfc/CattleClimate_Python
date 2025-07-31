# pages/4_Indices_Confort_Termico.py
import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

st.header("🧮 Cálculo de Índices de Confort Térmico (ITH, ITGH, CTR)")

# --- Configuración inicial ---
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "datos"
DATA_HIDRO = DATA_DIR / "hidrometeorologicos"
GLOSARIO_PATH = DATA_DIR / "Glosario Variables.xlsx"

# --- Cargar glosario ---
@st.cache_data
def cargar_glosario():
    try:
        return pd.read_excel(GLOSARIO_PATH, sheet_name="Básicas")
    except Exception as e:
        st.error(f"Error al cargar el glosario: {str(e)}")
        return pd.DataFrame()

glosario = cargar_glosario()

# --- Buscar archivos ---
data_files = [f.name for f in DATA_HIDRO.glob("*.data") if f.is_file()]

# --- Función mejorada para encontrar archivos ---
def encontrar_archivo_por_parametro(parametro):
    """Busca archivos usando coincidencias flexibles"""
    try:
        if glosario.empty:
            return None
            
        # Buscar en parámetros y etiquetas
        mask = (glosario["Parámetro"].str.contains(parametro, case=False, na=False) | 
                glosario["Etiqueta"].str.contains(parametro.split()[0], case=False, na=False))
        
        fila = glosario[mask]
        if not fila.empty:
            etiqueta = fila.iloc[0]["Etiqueta"]
            # Buscar archivo que comience con la etiqueta
            for f in data_files:
                if f.startswith(etiqueta):
                    return f
            # Si no se encuentra por etiqueta exacta, buscar coincidencia parcial
            for f in data_files:
                if etiqueta in f:
                    return f
        return None
    except Exception as e:
        st.warning(f"Error buscando {parametro}: {str(e)}")
        return None

# --- Detección automática de archivos ---
archivo_tbs = encontrar_archivo_por_parametro("bulbo seco")
archivo_tbh = encontrar_archivo_por_parametro("bulbo húmedo")
archivo_tr = encontrar_archivo_por_parametro("punto de rocío")
archivo_vv = encontrar_archivo_por_parametro("velocidad del viento")

# --- Interfaz de usuario ---
st.markdown("### 1. Archivos detectados automáticamente")

cols = st.columns(4)
params = [
    ("🌡️ Temperatura de bulbo seco (Tbs)", archivo_tbs),
    ("💧 Temperatura de bulbo húmedo (Tbh)", archivo_tbh),
    ("🌫️ Temperatura de rocío (Tr)", archivo_tr),
    ("💨 Velocidad del viento (Vv)", archivo_vv)
]

for col, (label, archivo) in zip(cols, params):
    with col:
        st.metric(label, archivo if archivo else "No encontrado")

# --- Función mejorada para cargar variables ---
def cargar_variable_segura(nombre_archivo):
    """Carga datos con manejo robusto de errores"""
    if not nombre_archivo:
        return None
        
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
        df = df.dropna(subset=["Fecha", "Valor"])
        
        return df.set_index("Fecha")["Valor"] if not df.empty else None
        
    except Exception as e:
        st.error(f"Error al cargar {nombre_archivo}: {str(e)}")
        return None

# --- Cálculo de índices ---
if st.button("🧮 Calcular Índices", type="primary"):
    with st.spinner("Calculando índices..."):
        try:
            # Verificar archivos
            if not all([archivo_tbs, archivo_tbh, archivo_tr, archivo_vv]):
                missing = []
                if not archivo_tbs: missing.append("Tbs")
                if not archivo_tbh: missing.append("Tbh")
                if not archivo_tr: missing.append("Tr")
                if not archivo_vv: missing.append("Vv")
                st.error(f"Faltan archivos necesarios: {', '.join(missing)}")
                st.stop()
            
            # Cargar datos
            tbs = cargar_variable_segura(archivo_tbs)
            tbh = cargar_variable_segura(archivo_tbh)
            tr = cargar_variable_segura(archivo_tr)
            vv = cargar_variable_segura(archivo_vv)
            
            # Verificar datos cargados
            if None in [tbs, tbh, tr, vv]:
                st.error("Algunos archivos no contenían datos válidos")
                st.stop()
            
            # Unificar datos
            df = pd.concat([tbs, tbh, tr, vv], axis=1, join="inner")
            df.columns = ["Tbs", "Tbh", "Tr", "Vv"]
            
            if df.empty:
                st.error("No hay datos coincidentes en el rango temporal")
                st.stop()
            
            # --- Cálculo de índices ---
            # ITH (Índice de Temperatura y Humedad)
            df["ITH"] = 0.72 * (df["Tbs"] + df["Tbh"]) + 40.6
            
            # ITGH (Índice de Temperatura de Globo y Humedad)
            df["Tgn"] = 0.0162 * df["Tbs"]**2 + 0.8562 * df["Tbs"] - 0.9387
            df["ITGH"] = df["Tgn"] + 0.36 * df["Tr"] + 41.5
            
            # CTR (Carga Térmica Radiante)
            df["CTR"] = 5.67e-8 * (100 * np.sqrt(2.51 * df["Vv"]**0.5 * (df["Tgn"] - df["Tbs"])) + (df["Tgn"] / 100)**44)**4
            
            # --- Mostrar resultados ---
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
            fig.update_layout(height=500, hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)
            
            # Datos completos (muestra)
            st.markdown("### 📝 Datos Detallados (muestra)")
            st.dataframe(df.head(100))
            
            # Botón de descarga
            csv = df.to_csv().encode('utf-8')
            st.download_button(
                "⬇️ Descargar CSV Completo",
                data=csv,
                file_name="indices_confort_termico.csv",
                mime="text/csv"
            )
            
        except Exception as e:
            st.error(f"❌ Error en los cálculos: {str(e)}")
            st.error("Verifique que los archivos tengan el formato correcto")