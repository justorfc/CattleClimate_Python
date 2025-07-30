# pages/5_Exportar_Resultados.py

import streamlit as st
import pandas as pd
import os
from io import BytesIO
import warnings
from fpdf import FPDF

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

st.header("📤 Exportar Resultados a Excel o PDF")

# --- Rutas base ---
base_path = r"C:\Proyectos\CattleClimate_Python"
data_path = os.path.join(base_path, "datos", "hidrometeorologicos")

# --- Buscar archivos generados ---
csv_files = [f for f in os.listdir(base_path) if f.endswith(".csv")]
archivo = st.selectbox("Seleccione archivo .csv generado para exportar:", csv_files)

if archivo:
    df = pd.read_csv(os.path.join(base_path, archivo))
    st.dataframe(df.head(100))

    # --- Descargar como Excel ---
    output_excel = BytesIO()
    with pd.ExcelWriter(output_excel, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Resultados')
        writer.close()
    st.download_button(
        label="⬇️ Descargar como Excel",
        data=output_excel.getvalue(),
        file_name=archivo.replace(".csv", ".xlsx"),
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # --- Descargar como PDF (simplificado) ---
    def generar_pdf(df):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)
        pdf.cell(200, 10, txt="Resumen de Resultados", ln=True, align='C')
        pdf.ln(10)

        # Solo las primeras filas como resumen
        for i, row in df.head(20).iterrows():
            linea = ', '.join([f"{col}: {val}" for col, val in row.items()])
            pdf.multi_cell(0, 6, txt=linea)
        return pdf.output(dest='S').encode('latin1')

    pdf_bytes = generar_pdf(df)
    st.download_button(
        label="⬇️ Descargar como PDF",
        data=pdf_bytes,
        file_name=archivo.replace(".csv", ".pdf"),
        mime="application/pdf"
    )
