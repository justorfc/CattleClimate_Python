# pages/5_Exportar_Resultados.py
import streamlit as st
import pandas as pd
from pathlib import Path
from io import BytesIO
import warnings
from fpdf import FPDF
import time
import os

warnings.filterwarnings("ignore")
st.set_page_config(page_title="Exportador de Resultados", layout="wide")

# --- Configuración de rutas ---
BASE_DIR = Path(__file__).parent.parent
RESULTS_DIR = BASE_DIR / "resultados"
RESULTS_DIR.mkdir(exist_ok=True)

# --- Función para generar PDF (Versión Simplificada y Corregida) ---
def generar_pdf(df, filename):
    """Genera un PDF profesional con los resultados"""
    pdf = FPDF()
    pdf.add_page()
    
    # Encabezado
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Reporte de Datos Climáticos", 0, 1, 'C')
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Archivo: {filename}", 0, 1)
    pdf.cell(0, 10, f"Generado el: {time.strftime('%Y-%m-%d %H:%M')}", 0, 1)
    pdf.ln(10)
    
    # Estadísticas
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Resumen Estadístico", 0, 1)
    pdf.set_font("Arial", '', 10)
    
    if df.select_dtypes(include='number').columns.any():
        stats = df.describe().round(2)
        for col in stats.columns:
            pdf.cell(0, 6, f"{col}:", 0, 1)
            pdf.cell(10)
            pdf.multi_cell(0, 6, f"Media={stats[col]['mean']} | Min={stats[col]['min']} | Max={stats[col]['max']}")
            pdf.ln(2)
    
    # Muestra de datos (versión simplificada)
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Muestra de Datos", 0, 1)
    pdf.set_font("Arial", '', 8)
    
    # Configuración de anchos de columna FIJOS para evitar el error
    col_widths = [30, 60]  # Anchos fijos para la primera y demás columnas
    
    # Encabezados
    cols = df.columns
    for i, col in enumerate(cols):
        pdf.cell(col_widths[0] if i == 0 else col_widths[1], 8, str(col), border=1)
    pdf.ln()
    
    # Datos (limitado a 30 filas)
    for _, row in df.head(30).iterrows():
        for i, col in enumerate(cols):
            pdf.cell(col_widths[0] if i == 0 else col_widths[1], 6, str(row[col]), border=1)
        pdf.ln()
    
    return pdf.output(dest='S').encode('latin1')

# --- Interfaz principal ---
def main():
    st.title("📊 Exportador de Resultados")
    
    # Listar archivos CSV
    try:
        archivos = sorted([f for f in RESULTS_DIR.glob("*.csv") if f.is_file()], 
                         key=lambda x: x.stat().st_mtime, reverse=True)
        
        if not archivos:
            st.warning("No hay archivos CSV en la carpeta 'resultados'")
            return
            
        archivo = st.selectbox("Seleccione archivo:", archivos, format_func=lambda x: x.name)
        
        # Cargar datos
        df = pd.read_csv(archivo)
        st.dataframe(df.head(10))
        
        # Opciones de exportación
        st.subheader("Formatos de Exportación")
        
        # Excel
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
            writer.close()
        
        st.download_button(
            "Descargar Excel",
            data=excel_buffer.getvalue(),
            file_name=archivo.name.replace(".csv", ".xlsx"),
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        # PDF
        pdf_bytes = generar_pdf(df, archivo.name)
        st.download_button(
            "Descargar PDF",
            data=pdf_bytes,
            file_name=archivo.name.replace(".csv", ".pdf"),
            mime="application/pdf"
        )
        
        # JSON
        st.download_button(
            "Descargar JSON",
            data=df.to_json(orient='records', indent=2),
            file_name=archivo.name.replace(".csv", ".json"),
            mime="application/json"
        )
        
    except Exception as e:
        st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()