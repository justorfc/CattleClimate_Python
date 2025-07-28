import streamlit as st
import pandas as pd
import os
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

# --- Configuración inicial ---
st.set_page_config(page_title="Lectura archivos .data", layout="wide")
st.title("Visor de Archivos .data con Información de Etiqueta y Estación")

# --- Rutas base ---
base_path = r"C:\Proyectos\CattleClimate_Python"
data_path = os.path.join(base_path, "datos", "hidrometeorologicos")
glosario_path = os.path.join(base_path, "datos", "Glosario Variables.xlsx")
cne_path = os.path.join(base_path, "datos", "CNE_IDEAM.xlsx")

# --- Cargar archivos auxiliares ---
glosario = pd.read_excel(glosario_path, sheet_name="Básicas")
cne = pd.read_excel(cne_path, sheet_name="CNE")

# --- Buscar archivos .data ---
data_files = [f for f in os.listdir(data_path) if f.endswith(".data")]
st.sidebar.header("Archivos disponibles")
archivo_seleccionado = st.sidebar.selectbox("Seleccione un archivo .data", data_files)

# --- Procesar archivo seleccionado ---
if archivo_seleccionado:
    st.success(f"Archivo seleccionado: {archivo_seleccionado}")  # <- agregado

    try:
        etiqueta, codigo = archivo_seleccionado.replace(".data", "").split("@")
        st.info(f"Etiqueta: {etiqueta}, Código: {codigo}")  # <- agregado

        # Información desde el glosario
        info_glosario = glosario[glosario["Etiqueta"] == etiqueta]
        info_cne = cne[cne["CODIGO"] == int(codigo)]

        # Mostrar información
        st.subheader("🧾 Información general del archivo")
        st.markdown(f"- **Archivo**: `{archivo_seleccionado}`")
        st.markdown(f"- **Etiqueta**: `{etiqueta}`")
        st.markdown(f"- **Código estación**: `{codigo}`")

        if not info_glosario.empty:
            st.markdown("#### 📌 Información desde Glosario Variables:")
            st.dataframe(info_glosario)
        else:
            st.warning("No se encontró la etiqueta en el Glosario.")

        if not info_cne.empty:
            st.markdown("#### 🌍 Información de la estación (CNE_IDEAM):")
            st.dataframe(info_cne)
        else:
            st.warning("No se encontró el código en CNE_IDEAM.")

        # Leer contenido del archivo .data
        file_path = os.path.join(data_path, archivo_seleccionado)
        df_data = pd.read_csv(file_path, sep="|", engine="python", names=["Fecha", "Valor"])
        df_data["Etiqueta"] = etiqueta
        df_data["Código"] = codigo
        st.markdown("#### 📊 Contenido del archivo .data:")
        st.dataframe(df_data.head(20))

    except Exception as e:
        st.error(f"❌ Error en procesamiento: {e}")
