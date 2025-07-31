# pages/1_Explorador_Data.py
import streamlit as st
import pandas as pd
from pathlib import Path
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

st.header("📂 Explorador de Archivos .data")

# --- Configuración de rutas ---
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "datos"
DATA_HIDRO = DATA_DIR / "hidrometeorologicos"
RESULTS_DIR = BASE_DIR / "resultados"
GLOSARIO_PATH = DATA_DIR / "Glosario Variables.xlsx"
CNE_PATH = DATA_DIR / "CNE_IDEAM.xlsx"

# Crear directorio de resultados si no existe
RESULTS_DIR.mkdir(exist_ok=True)

# --- Cargar auxiliares ---
try:
    glosario = pd.read_excel(GLOSARIO_PATH, sheet_name="Básicas")
    cne = pd.read_excel(CNE_PATH, sheet_name="CNE")
except Exception as e:
    st.error(f"Error cargando archivos auxiliares: {e}")
    st.stop()

# --- Listar archivos .data ---
try:
    data_files = [f.name for f in DATA_HIDRO.glob("*.data")]  # Usamos pathlib para listar archivos
    archivo = st.selectbox("Seleccione un archivo .data", options=data_files)

    if archivo:
        etiqueta, codigo = archivo.replace(".data", "").split("@")
        ruta_archivo = DATA_HIDRO / archivo  # pathlib maneja la ruta correctamente

        # Cargar datos
        try:
            df = pd.read_csv(ruta_archivo, sep="|", names=["Fecha", "Valor"], engine="python")
            df["Etiqueta"] = etiqueta
            df["Codigo"] = codigo

            st.success(f"Archivo: {archivo} cargado correctamente")

            # Mostrar información
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

            # --- Nueva sección para guardar resultados ---
            st.markdown("---")
            st.subheader("💾 Guardar Resultados")
            
            nombre_archivo = st.text_input(
                "Nombre para el archivo de resultados (sin extensión)",
                value=f"resultados_{etiqueta}_{codigo}"
            )
            
            if st.button("Guardar como CSV"):
                nombre_completo = f"{nombre_archivo}.csv"
                ruta_guardado = RESULTS_DIR / nombre_completo
                df.to_csv(ruta_guardado, index=False)
                st.success(f"Archivo guardado en: {ruta_guardado}")
                
                # Mostrar enlace al exportador
                st.markdown(f"""
                ### 📤 Puede exportar este archivo a otros formatos en:
                [Exportar Resultados](/5_Exportar_Resultados)
                """)

        except Exception as e:
            st.error(f"Error al procesar archivo: {e}")

except Exception as e:
    st.error(f"No se encontraron archivos .data en: {DATA_HIDRO}")