# pages/3_Graficas_Interactivas.py
import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px
import base64
from datetime import datetime, timedelta
import warnings

# Configuración inicial
warnings.filterwarnings("ignore")
st.set_page_config(layout="wide", page_title="Análisis Climático Ganadero")

# ======================================
# 1. FUNCIÓN DE CARGA OPTIMIZADA
# ======================================

@st.cache_data(show_spinner="Cargando datos climáticos...", max_entries=1, ttl=3600)
def cargar_datos():
    """Carga los datos con manejo robusto de tipos"""
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "datos"
    
    try:
        # Cargar metadatos (solo columnas necesarias)
        glosario = pd.read_excel(
            DATA_DIR / "Glosario Variables.xlsx",
            sheet_name="Básicas",
            usecols=["Etiqueta", "Unidad"]
        )
        cne = pd.read_excel(
            DATA_DIR / "CNE_IDEAM.xlsx",
            sheet_name="CNE",
            usecols=["CODIGO", "nombre", "DEPARTAMENTO", "MUNICIPIO"]
        )
        
        # Procesar archivos .data
        data_files = list((DATA_DIR / "hidrometeorologicos").glob("*.data"))
        if not data_files:
            st.error("❌ No se encontraron archivos .data")
            return None, None, None
            
        chunks = []
        for file in data_files:
            try:
                etiqueta, codigo = file.stem.split("@")
                
                # Leer archivo con manejo seguro de tipos
                df = pd.read_csv(
                    file,
                    sep="|",
                    names=["Fecha", "Valor"],
                    engine="python",
                    dtype={"Valor": "object"},  # Primero como texto
                    na_values=["?", "-", "NaN", "NA", "", "null"],
                    on_bad_lines="skip"
                )
                
                # Conversión segura a numérico
                df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")
                df = df.dropna(subset=["Valor"])
                
                if df.empty:
                    continue
                
                # Optimizar tipos de datos
                df["Valor"] = df["Valor"].astype("float32")
                df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
                df = df.dropna(subset=["Fecha"])
                
                # Filtrar por fecha (últimos 5 años)
                fecha_limite = datetime.now() - timedelta(days=5*365)
                df = df[df["Fecha"] >= fecha_limite]
                
                if not df.empty:
                    # Añadir metadatos básicos
                    df["Archivo"] = file.name
                    df["Etiqueta"] = etiqueta
                    df["Codigo"] = codigo
                    
                    # Fusionar con metadatos de estación
                    meta_est = cne[cne["CODIGO"] == int(codigo)]
                    if not meta_est.empty:
                        df = df.assign(**meta_est.iloc[0].to_dict())
                    
                    chunks.append(df)
                    
            except Exception as e:
                st.warning(f"⚠️ Archivo {file.name} omitido: {str(e)}")
                continue
                
        return pd.concat(chunks, ignore_index=True), glosario, cne
        
    except Exception as e:
        st.error(f"❌ Error crítico al cargar datos: {str(e)}")
        return None, None, None

# ======================================
# 2. FUNCIONALIDAD DE EXPORTACIÓN
# ======================================

def get_image_download_link(fig, filename, text):
    """Genera enlace de descarga para la imagen"""
    img_bytes = fig.to_image(format="png", scale=1)
    b64 = base64.b64encode(img_bytes).decode()
    return f'<a href="data:image/png;base64,{b64}" download="{filename}">{text}</a>'

def get_html_download_link(fig, filename, text):
    """Genera enlace de descarga para HTML"""
    html = fig.to_html()
    b64 = base64.b64encode(html.encode()).decode()
    return f'<a href="data:text/html;base64,{b64}" download="{filename}">{text}</a>'

# ======================================
# 3. INTERFAZ PRINCIPAL
# ======================================

def main():
    st.title("📈 Gráficas Climáticas Interactivas")
    
    # Cargar datos
    df, glosario, cne = cargar_datos()
    
    if df is None:
        st.error("No se pudieron cargar los datos. Verifique los archivos fuente.")
        return
    
    # ======================
    # CONTROLES DE FILTRO
    # ======================
    col1, col2 = st.columns(2)
    
    with col1:
        estacion = st.selectbox(
            "📍 Seleccione Estación",
            options=sorted(df["nombre"].dropna().unique()),
            index=0
        )
    
    with col2:
        variable = st.selectbox(
            "📌 Seleccione Variable",
            options=sorted(df["Etiqueta"].unique()),
            index=0
        )
    
    # Filtrado de datos
    df_filtrado = df[(df["nombre"] == estacion) & (df["Etiqueta"] == variable)]
    
    if not df_filtrado.empty:
        # ======================
        # CREACIÓN DEL GRÁFICO
        # ======================
        st.markdown(f"### {variable} en {estacion}")
        
        # Muestreo para mejor rendimiento
        if len(df_filtrado) > 15_000:
            df_filtrado = df_filtrado.sample(15_000, random_state=42)
            st.info("Mostrando muestra aleatoria de 15,000 puntos para mejor rendimiento")
        
        # Crear gráfico interactivo
        fig = px.line(
            df_filtrado,
            x="Fecha",
            y="Valor",
            labels={"Valor": "Valor", "Fecha": "Fecha"},
            render_mode="webgl",
            line_shape="linear"
        )
        
        # Configuración del layout
        fig.update_layout(
            height=500,
            hovermode="x unified",
            margin=dict(t=30, b=30),
            xaxis=dict(showgrid=True, gridcolor="LightGrey"),
            yaxis=dict(showgrid=True, gridcolor="LightGrey")
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # ======================
        # SECCIÓN DE EXPORTACIÓN
        # ======================
        st.markdown("---")
        st.markdown("### 📤 Exportar Gráfico")
        
        exp_col1, exp_col2, exp_col3 = st.columns(3)
        
        with exp_col1:
            st.markdown(get_image_download_link(
                fig, 
                f"{variable}_{estacion}.png", 
                "⬇️ Descargar como PNG"
            ), unsafe_allow_html=True)
        
        with exp_col2:
            st.markdown(get_html_download_link(
                fig,
                f"{variable}_{estacion}.html",
                "⬇️ Descargar como HTML"
            ), unsafe_allow_html=True)
        
        with exp_col3:
            csv = df_filtrado.to_csv(index=False)
            st.download_button(
                "⬇️ Descargar Datos (CSV)",
                data=csv,
                file_name=f"datos_{variable}_{estacion}.csv",
                mime="text/csv"
            )
        
        # ======================
        # ESTADÍSTICAS
        # ======================
        with st.expander("📊 Ver Estadísticas Descriptivas", expanded=False):
            st.dataframe(df_filtrado["Valor"].describe().to_frame("Estadísticas"))
            
    else:
        st.warning("No se encontraron datos para los filtros seleccionados")

if __name__ == "__main__":
    main()