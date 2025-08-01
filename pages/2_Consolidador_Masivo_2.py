import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import dask.dataframe as dd
from dask.diagnostics import ProgressBar
import warnings

warnings.filterwarnings("ignore")

# --- Configuración de rutas ---
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "datos"
DATA_HIDRO = DATA_DIR / "hidrometeorologicos"
GLOSARIO_PATH = DATA_DIR / "Glosario Variables.xlsx"
CNE_PATH = DATA_DIR / "CNE_IDEAM.xlsx"

# --- Cargar CNE y extraer lista de estaciones y etiquetas disponibles ---
@st.cache_data
def obtener_opciones_disponibles():
    archivos = sorted(DATA_HIDRO.glob("*.data"))
    etiquetas = []
    codigos = []

    for archivo in archivos:
        try:
            etiqueta, codigo = archivo.stem.split("@")
            etiquetas.append(etiqueta)
            codigos.append(codigo)
        except:
            continue

    cne = pd.read_excel(CNE_PATH, sheet_name="CNE")
    estaciones = cne[cne["CODIGO"].astype(str).isin(codigos)]["nombre"].unique().tolist()

    return sorted(set(etiquetas)), sorted(estaciones), cne

# --- Cargar solo los datos necesarios según filtros ---
def cargar_datos_filtrados(etiqueta_seleccionada, estacion_seleccionada, cne):
    # Obtener código de estación desde el nombre
    codigo_estacion = cne[cne["nombre"] == estacion_seleccionada]["CODIGO"].astype(str).values[0]

    # Buscar archivo que coincida con la etiqueta y el código
    archivo = DATA_HIDRO / f"{etiqueta_seleccionada}@{codigo_estacion}.data"
    if not archivo.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {archivo.name}")

    # Leer solo ese archivo con Dask
    ddf = dd.read_csv(
        archivo,
        sep="|",
        skiprows=1,
        names=["Fecha", "Valor"],
        dtype={"Valor": "float32"},
        blocksize="8MB",
        assume_missing=True
    )

    # Procesamiento mínimo
    ddf["Fecha"] = dd.to_datetime(ddf["Fecha"], errors="coerce")
    ddf = ddf[~ddf["Fecha"].isna()]
    ddf["Etiqueta"] = etiqueta_seleccionada
    ddf["Codigo"] = codigo_estacion
    ddf["ITH"] = 0.72 * (ddf["Valor"] + ddf["Valor"].shift(1)) + 40.6

    # Unir con nombre de estación
    ddf = ddf.merge(cne[["CODIGO", "nombre"]].astype({"CODIGO": "str"}), left_on="Codigo", right_on="CODIGO", how="left")

    # Retornar datos materializados
    with ProgressBar():
        return ddf.compute()

# --- Aplicación Streamlit ---
def main():
    st.set_page_config(page_title="CattleClimate", layout="wide")
    st.title("📊 Consolidador Liviano de Datos Hidrometeorológicos")

    etiquetas, estaciones, cne = obtener_opciones_disponibles()

    col1, col2 = st.columns(2)
    with col1:
        estacion = st.selectbox("Estación", estaciones)
    with col2:
        variable = st.selectbox("Variable", etiquetas)

    # --- Botón para cargar datos ---
    if st.button("📥 Cargar datos filtrados"):
        with st.spinner("Procesando archivo seleccionado..."):
            try:
                df = cargar_datos_filtrados(variable, estacion, cne)
                st.session_state.df_filtrado = df  # Guardar en sesión
                st.success(f"✅ {len(df)} registros cargados.")
            except Exception as e:
                st.error(f"⚠️ Error: {str(e)}")
                st.session_state.pop("df_filtrado", None)  # ← Limpia datos anteriores si hay error

    # --- Mostrar tabla si ya fue cargada antes ---
    if "df_filtrado" in st.session_state:
        st.subheader("Vista previa de los datos")
        st.dataframe(st.session_state.df_filtrado.head(100))

        # Nombre editable del archivo
        nombre_archivo = st.text_input("📝 Nombre del archivo de salida (sin extensión):", "resultado_filtrado")

        # Botón de exportar
        if st.button("💾 Exportar a Parquet"):
            try:
                output_file = f"{nombre_archivo}.parquet"
                st.session_state.df_filtrado.to_parquet(output_file, index=False)
                st.success(f"📁 Archivo exportado como '{output_file}'.")

                # Botón para descargar
                with open(output_file, "rb") as f:
                    st.download_button("⬇️ Descargar Parquet", f, file_name=output_file)
            except Exception as e:
                st.error(f"❌ Error al exportar: {str(e)}")

if __name__ == "__main__":
    main()
