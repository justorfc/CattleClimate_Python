
### 📘 `README.md` sugerido para tu proyecto `CattleClimate_Python`

```markdown
# 🐄🌦️ CattleClimate_Python

**Aplicación interactiva para la lectura, análisis y visualización de archivos `.data` meteorológicos del IDEAM, con fines de investigación en confort térmico del ganado en Sucre, Colombia.**  
Desarrollado con Python y Streamlit.

---

## 📌 Objetivo

Este proyecto permite:
- Leer automáticamente los archivos `.data` provenientes de estaciones meteorológicas del IDEAM.
- Asociar cada archivo con su **etiqueta de variable** y su **código de estación**.
- Consultar las **unidades y descripción** desde el archivo `Glosario Variables.xlsx`.
- Consultar la **información de la estación** (nombre, ubicación, tecnología, etc.) desde `CNE_IDEAM.xlsx`.
- Visualizar de forma amigable los datos crudos y exportarlos para análisis posterior.

---

## 📁 Estructura de Carpetas

```

CattleClimate\_Python/
│
├── app.py                       ← Aplicación Streamlit principal
├── requirements.txt             ← Lista de dependencias
├── .gitignore                   ← Exclusión de archivos sensibles
│
├── datos/
│   ├── hidrometeorologicos/    ← Archivos .data con mediciones meteorológicas
│   └── radiacion/              ← Archivos de apoyo en Excel:
│        ├── Glosario Variables.xlsx
│        └── CNE\_IDEAM.xlsx

````

---

## 🚀 Cómo ejecutar la aplicación

1. **Clonar el repositorio:**

```bash
git clone https://github.com/justorfc/CattleClimate_Python.git
cd CattleClimate_Python
````

2. **Crear entorno virtual (opcional pero recomendado):**

```bash
python -m venv .venv
.venv\Scripts\activate  # En Windows
```

3. **Instalar dependencias:**

```bash
pip install -r requirements.txt
```

4. **Ejecutar la aplicación:**

```bash
streamlit run app.py
```

5. Abre en tu navegador:
   [http://localhost:8501](http://localhost:8501)

---

## 📊 Funcionalidades actuales

* 📂 Lectura automatizada de archivos `.data` con formato `ETIQUETA@CÓDIGO.data`.
* 🔎 Consulta cruzada con glosario de variables y catálogo de estaciones IDEAM.
* 🧾 Visualización de metadatos completos (unidad, descripción, ubicación, etc.)
* 📑 Visualización previa de los datos de cada archivo.
* 💾 Exportación de los datos procesados.

---

## 🧠 Aplicación en investigación

Este proyecto se enmarca dentro del proyecto **CattleClimate**, orientado al análisis del confort térmico en bovinos, dirigido por el Dr. Quelbis Quintero (grupo Bioindustrias, Universidad de Sucre).

Los datos meteorológicos alimentan modelos de predicción de índices como:

* Índice de Temperatura y Humedad (ITH)
* Índice de Temperatura de Globo Negro y Humedad (ITGH)
* Índice de Carga Térmica Radiante (CTR)

---

## 📦 Tecnologías usadas

* [Python 3.13](https://www.python.org/)
* [Streamlit](https://streamlit.io/)
* [Pandas](https://pandas.pydata.org/)
* [OpenPyXL](https://openpyxl.readthedocs.io/) (para archivos `.xlsx`)

---

## 📌 Pendientes y mejoras futuras

* [ ] Agregar filtros por fecha, estación y variable.
* [ ] Implementar cálculos automáticos de índices bio-climáticos.
* [ ] Visualizaciones interactivas de series de tiempo.
* [ ] Exportación de reportes en PDF/Excel.

---

## 👨‍💻 Autor

**Ing. Justo Fuentes**
Docente Investigador – Universidad de Sucre
[GitHub](https://github.com/justorfc)

---

## 📄 Licencia

Este proyecto está licenciado bajo los términos de uso académico y de investigación abierta.
Si deseas contribuir o reutilizar el código, por favor contacta al autor.

```

---

### ✅ ¿Cómo agregarlo?

1. Crea el archivo en VSCode:
```

CattleClimate\_Python/README.md

````

2. Pega el contenido anterior.

3. Guarda y haz commit + push:

```bash
git add README.md
git commit -m "Agregar README detallado del proyecto"
git push
````