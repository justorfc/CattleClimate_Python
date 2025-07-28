import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px
import io

st.set_page_config(page_title="CattleClimate", layout="wide")
st.title("📡 CattleClimate - Visualizador de Datos Meteorológicos")

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "datos", "hidrometeorologicos")

# Buscar archivos .data
try:
    archivos = [f for f in os.listdir(DATA_DIR) if f.endswith(".data")]
except Exception as e:
    st.error(f"❌ No se pudo acceder a la carpeta de datos: {e}")
    st.stop()

if not archivos:
    st.warning("⚠️ No hay archivos .data en la carpeta 'datos/hidrometeorologicos'.")
    st.stop()

archivo_seleccionado = st.selectbox("Selecciona un archivo .data", archivos)
ruta_archivo = os.path.join(DATA_DIR, archivo_seleccionado)

try:
    with open(ruta_archivo, "r", encoding="utf-8") as f:
        lineas = f.readlines()
except Exception as e:
    st.error(f"❌ Error al leer el archivo seleccionado: {e}")
    st.stop()

# Validación básica
if len(lineas) < 2:
    st.error("⚠️ El archivo no tiene suficientes líneas para procesar.")
    st.stop()

# Mostrar etiqueta (primera línea)
etiqueta_info = lineas[0].strip()
st.markdown(f"**Etiqueta y código de estación:** `{etiqueta_info}`")

# Mostrar primeras líneas de datos
datos_crudos = [line.strip() for line in lineas[1:]]
st.markdown("### 🛠 Primeras líneas del archivo:")
st.code("\n".join(datos_crudos[:5]), language="text")

# Parseo de líneas
fechas = []
valores = []
errores = 0

for idx, linea in enumerate(datos_crudos):
    try:
        parte_fecha, parte_valor = linea.split("|")
        fecha = datetime.strptime(parte_fecha.strip(), "%Y-%m-%d %H:%M:%S")
        valor = float(parte_valor.strip())
        fechas.append(fecha)
        valores.append(valor)
    except Exception:
        errores += 1
        continue

# Mostrar resumen de validación
total = len(datos_crudos)
validos = len(fechas)
st.info(f"✅ Líneas válidas: {validos} / {total} ({(validos/total)*100:.1f}%)")
if errores > 0:
    st.warning(f"⚠️ {errores} líneas no pudieron ser procesadas y fueron descartadas.")

if validos == 0:
    st.error("❌ No se pudo leer ningún dato válido.")
    st.stop()

# Crear DataFrame
df = pd.DataFrame({"FechaHora": fechas, "Valor": valores})

# Mostrar resumen estadístico
st.subheader("📋 Resumen del archivo")
st.markdown(f"- Registros válidos: **{len(df)}**")
st.markdown(f"- Fecha mínima: **{df['FechaHora'].min()}**")
st.markdown(f"- Fecha máxima: **{df['FechaHora'].max()}**")
st.markdown(f"- Valor mínimo: **{df['Valor'].min()}**")
st.markdown(f"- Valor máximo: **{df['Valor'].max()}**")
st.markdown(f"- Promedio: **{df['Valor'].mean():.2f}**")

# Filtro por rango de fechas
st.subheader("📆 Filtro de rango de fechas")
min_fecha = df["FechaHora"].min().date()
max_fecha = df["FechaHora"].max().date()

rango = st.date_input("Selecciona el rango de fechas:", (min_fecha, max_fecha),
                      min_value=min_fecha, max_value=max_fecha)

if isinstance(rango, tuple) and len(rango) == 2:
    df_filtrado = df[(df["FechaHora"].dt.date >= rango[0]) & (df["FechaHora"].dt.date <= rango[1])]
else:
    df_filtrado = df.copy()

# Mostrar tabla
st.subheader("📊 Datos filtrados")
st.dataframe(df_filtrado.head(10))

# Descarga CSV
csv = df_filtrado.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Descargar datos filtrados (.csv)",
    data=csv,
    file_name=f"{archivo_seleccionado.replace('.data','')}_filtrado.csv",
    mime="text/csv"
)

# Gráfico
st.subheader("📈 Gráfico de serie temporal")
if not df_filtrado.empty:
    fig = px.line(df_filtrado, x="FechaHora", y="Valor",
                  title="Serie temporal del archivo seleccionado",
                  labels={"FechaHora": "Fecha", "Valor": "Valor registrado"})
    fig.update_layout(xaxis_title="Fecha", yaxis_title="Valor",
                      xaxis=dict(rangeslider_visible=True))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("⚠️ No hay datos disponibles en el rango seleccionado.")

# === RESUMEN MENSUAL ===
st.subheader("📊 Promedio mensual (todas las fechas combinadas)")

orden_meses = ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"]

df_filtrado["Mes"] = df_filtrado["FechaHora"].dt.month_name()
resumen_mensual = df_filtrado.groupby("Mes")["Valor"].mean().reindex(orden_meses)


fig_mes = px.bar(resumen_mensual, x=resumen_mensual.index, y="Valor",
                 labels={"Valor": "Promedio", "Mes": "Mes"},
                 title="Promedio mensual de valores registrados")
st.plotly_chart(fig_mes, use_container_width=True)

# === RESUMEN ANUAL ===
st.subheader("📊 Promedio anual")

df_filtrado["Año"] = df_filtrado["FechaHora"].dt.year
resumen_anual = df_filtrado.groupby("Año")["Valor"].mean()

fig_anio = px.bar(resumen_anual, x=resumen_anual.index, y="Valor",
                  labels={"Valor": "Promedio", "Año": "Año"},
                  title="Promedio anual de valores registrados")
st.plotly_chart(fig_anio, use_container_width=True)
