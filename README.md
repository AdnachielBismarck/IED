# IED Intelligence Platform

[![Quality checks](https://github.com/AdnachielBismarck/IED/actions/workflows/quality.yml/badge.svg)](https://github.com/AdnachielBismarck/IED/actions/workflows/quality.yml)
![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B)

Plataforma de inteligencia económica territorial para analizar la Inversión Extranjera Directa (IED) en México. Convierte datos públicos de la Secretaría de Economía en indicadores comparables, análisis de redes y perfiles estatales orientados a decisiones.

El proyecto fue diseñado para responder tres preguntas:

- ¿Qué estados concentran, diversifican o dependen de determinados orígenes de capital?
- ¿Cómo cambió la estructura territorial de la IED con la reorganización de cadenas de suministro?
- ¿Qué entidades combinan escala, estabilidad y conectividad dentro de la red de inversión?

## Producto

La aplicación Streamlit contiene seis vistas:

| Vista | Propósito |
|---|---|
| Panorama nacional | Síntesis de tendencias, distribución territorial y principales señales |
| Red de inversión | Relaciones país-estado, centralidad y comunidades económicas |
| Perfiles estatales | Diagnóstico y comparación de las 32 entidades federativas |
| Riesgo y dependencia | Concentración, observabilidad y estabilidad |
| Dinámica temporal | Evolución trimestral, composición y señales asociadas con nearshoring |
| Metodología | Definiciones, supuestos, validación del clustering y límites de interpretación |

La interfaz utiliza navegación controlada, sistema visual compartido, fecha de corte dinámica y exportaciones CSV para los principales resultados. La documentación metodológica forma parte del producto y no depende del README.

La cobertura exacta se obtiene de `data/processed/proc_2/metadata.json`. Esto evita inconsistencias entre el pipeline, la aplicación y la documentación.

## Stack técnico

- Procesamiento: pandas, NumPy, PyArrow y OpenPyXL.
- Modelado: scikit-learn.
- Redes: NetworkX y python-louvain.
- Producto analítico: Streamlit y Plotly.
- Reportería: Matplotlib y ReportLab.
- Calidad: pytest y GitHub Actions.

La descripción de componentes y decisiones se encuentra en [Arquitectura técnica](docs/ARCHITECTURE.md). La procedencia y granularidad de los artefactos se documentan en [Datos y artefactos](docs/DATA.md).

## Metodología

El pipeline produce cuatro capas analíticas:

1. Preparación: normalización de fechas, entidades, países, tipos de inversión y sectores.
2. Red bipartita: vínculos entre países de origen y estados receptores, ponderados por IED acumulada. Los caminos mínimos usan `1 / IED` como distancia económica.
3. Indicadores estatales: dependencia, diversificación, observabilidad, estabilidad y señal empírica de nearshoring.
4. Tipología territorial: KMeans evaluado entre `k=2` y `k=6`; se prioriza la mayor silhouette entre soluciones sin grupos menores de tres estados.

El Nearshoring Score mostrado se basa en crecimiento, participación estadounidense y peso del período reciente. Los resultados también incluyen una variante estratégica con componente geográfico, identificada de forma separada.

### Limitaciones

- Los valores confidenciales publicados como `C` no son faltantes aleatorios. Los indicadores desagregados pueden subestimar concentraciones reales.
- Los flujos pueden ser negativos por desinversiones y revisiones. Para cuotas de concentración se consideran relaciones con IED positiva; las series temporales conservan los valores reportados.
- Los scores son instrumentos comparativos, no estimaciones causales ni recomendaciones de inversión.
- La asociación temporal posterior a 2021 no demuestra por sí sola un efecto causal de nearshoring.

## Arquitectura

```text
IED/
|-- app/
|   |-- main.py
|   |-- shared.py
|   `-- pages/
|-- data/
|   |-- raw/
|   `-- processed/
|       |-- proc_1/
|       `-- proc_2/
|-- pipeline/
|   |-- 00_cleaning_data.py
|   |-- 01_data_preparation.py
|   |-- 02_graph_analytics.py
|   |-- 03_economic_scoring.py
|   |-- 04_clustering.py
|   `-- run_pipeline.py
|-- reports/
|   `-- generate_pdf.py
|-- docs/
|-- tests/
|-- requirements.txt
`-- requirements-dev.txt
```

Los artefactos de `proc_2` permanecen versionados porque Streamlit Community Cloud los necesita para iniciar sin procesar los archivos originales.

## Ejecución local

Requiere Python 3.11.

```bash
python -m venv .venv
python -m pip install -r requirements.txt
streamlit run app/main.py
```

Para reconstruir los datos procesados:

```bash
python pipeline/run_pipeline.py
```

Los tres libros de origen deben estar en `data/raw/`. Los nombres esperados están definidos en `pipeline/00_cleaning_data.py`.

## Calidad y reproducibilidad

```bash
python -m pip install -r requirements-dev.txt
python -m pytest
python -m compileall -q app pipeline reports tests
```

Las pruebas verifican cobertura estatal, fechas, rangos de indicadores, consistencia de artefactos y metadatos. El flujo de integración continua ejecuta estas validaciones en Python 3.11.

Las convenciones para desarrollo y revisión están descritas en [CONTRIBUTING.md](CONTRIBUTING.md).

## Fuente

Secretaría de Economía, Dirección General de Inversión Extranjera. Cifras expresadas en millones de dólares corrientes. Procesamiento y análisis: Adnachiel Avendaño.
