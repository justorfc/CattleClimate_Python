import streamlit as st
import pandas as pd
import os
import warnings

# --- Configuración general ---
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")
st.set_page_config(page_title="Lectura masiva de archivos .data", layout="wide")
st.title("📦 Lectura masiva de archivos .data con metadatos")

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
st.sidebar.write(f"🗃️ Archivos encontrados: {len(data_files)}")

# --- Función principal para leer todos los archivos ---
@st.cache_data(show_spinner=True)
def cargar_archivos():
    todos = []

    for file in data_files:
        try:
            etiqueta, codigo = file.replace(".data", "").split("@")
            codigo_int = int(codigo)
            ruta = os.path.join(data_path, file)

            df = pd.read_csv(ruta, sep="|", engine="python", names=["Fecha", "Valor"])

            # Añadir etiqueta y código
            df["Archivo"] = file
            df["Etiqueta"] = etiqueta
            df["Código"] = codigo

            # Datos del glosario
            fila_glosario = glosario[glosario["Etiqueta"] == etiqueta]
            if not fila_glosario.empty:
                for col in fila_glosario.columns:
                    df[col] = fila_glosario.iloc[0][col]

            # Datos de la estación
            fila_cne = cne[cne["CODIGO"] == codigo_int]
            if not fila_cne.empty:
                for col in fila_cne.columns:
                    df[col] = fila_cne.iloc[0][col]

            todos.append(df)

        except Exception as e:
            st.warning(f"Error procesando {file}: {e}")

    if todos:
        return pd.concat(todos, ignore_index=True)
    else:
        return pd.DataFrame()

# --- Ejecutar lectura y mostrar resultado ---
st.info("Cargando todos los archivos .data y generando tabla combinada...")
df_total = cargar_archivos()

if not df_total.empty:
    st.success(f"✅ {len(df_total)} registros procesados desde {df_total['Archivo'].nunique()} archivos.")

    # Filtro opcional
    filtro = st.selectbox("🔎 Filtrar por archivo", options=["Todos"] + sorted(df_total["Archivo"].unique()))
    if filtro != "Todos":
        df_filtrado = df_total[df_total["Archivo"] == filtro]
    else:
        df_filtrado = df_total

    st.dataframe(df_filtrado.head(1000), use_container_width=True)

    # Descargar CSV
    st.download_button(
        "⬇️ Descargar como CSV",
        data=df_filtrado.to_csv(index=False),
        file_name="datos_consolidados.csv",
        mime="text/csv"
    )
else:
    st.error("❌ No se pudo construir el DataFrame. Verifica los archivos.")
