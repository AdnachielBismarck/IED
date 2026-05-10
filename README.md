# IED Intelligence Platform · México

Plataforma de inteligencia económica territorial para el análisis estructural
de la Inversión Extranjera Directa (IED) en México. Período: Q1 2006 — Q2 2025.

**Fuente de datos:** Secretaría de Economía — DGIE

---

## Estructura del proyecto

```
IED/
├── data/
│   ├── raw/                         ← Excel originales de la SE (3 archivos)
│   └── processed/
│       ├── proc_1/                  ← 10 CSVs limpios (generados por paso 0)
│       └── proc_2/                  ← 20+ Parquets y JSONs para la app
│
├── pipeline/                        ← Scripts de procesamiento (correr una vez)
│   ├── run_pipeline.py              ← Ejecutor maestro
│   ├── 00_cleaning_data.py          ← Excel → CSV
│   ├── 01_data_preparation.py      ← CSV → Parquet
│   ├── 02_graph_analytics.py       ← Análisis de red bipartita
│   ├── 03_economic_scoring.py      ← Índices estructurales por estado
│   └── 04_clustering.py            ← Tipología de estados (KMeans k=4)
│
├── app/                             ← Aplicación Streamlit
│   ├── main.py                      ← Executive Overview (página principal)
│   └── pages/
│       ├── 1_Network_Graph.py       ← Red País ↔ Estado interactiva
│       ├── 2_Regional_Profiles.py   ← Perfil individual por estado
│       ├── 3_Risk_Analysis.py       ← Vulnerabilidades y dependencia
│       └── 4_Temporal_Dynamics.py  ← Evolución temporal y nearshoring
│
├── reports/
│   ├── generate_pdf.py              ← Reporte PDF ejecutivo (10 páginas)
│   └── img/                         ← Imágenes generadas por el PDF
│
├── .streamlit/
│   └── config.toml                  ← Tema dark y configuración
│
└── requirements.txt
```

---

## Instalación y uso

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

> **Python 3.13:** si algún paquete falla, instalar individualmente:
> `pip install pandas numpy pyarrow networkx python-louvain scikit-learn plotly streamlit reportlab matplotlib openpyxl`

### 2. Colocar los datos originales

Los 3 archivos Excel de la SE deben estar en `data/raw/`:
- `2025_3T_Flujosportipodeinversion_actu__3_.xlsx`
- `2025_3T_Flujosporentidadfederativa_actu__5__.xlsx`
- `2025_3T_Flujospororigen_actu__4_.xlsx`

### 3. Ejecutar el pipeline

```bash
# Desde la raíz del proyecto (carpeta IED/)
python pipeline/run_pipeline.py
```

Tiempo estimado: 5-8 minutos. Genera todos los archivos en `data/processed/proc_2/`.

### 4. Lanzar la aplicación

```bash
streamlit run app/main.py
```

Abre automáticamente en `http://localhost:8501`

### 5. Generar el reporte PDF (opcional)

```bash
python reports/generate_pdf.py
```

Genera `reports/IED_Intelligence_Report_Mexico.pdf` (~10 páginas).

---

## Descripción de los análisis

### Pipeline de procesamiento

| Paso | Script | Descripción |
|------|--------|-------------|
| 0 | `00_cleaning_data.py` | Limpia los 3 Excel y genera 10 CSVs estructurados |
| 1 | `01_data_preparation.py` | Convierte CSVs a Parquet, filtra totales, parsea fechas |
| 2 | `02_graph_analytics.py` | Red bipartita País↔Estado, centralidad, Louvain |
| 3 | `03_economic_scoring.py` | 5 índices estructurales + Score Estratégico |
| 4 | `04_clustering.py` | KMeans k=4, PCA 2D, tipología de estados |

### Índices estructurales (Paso 3)

| Índice | Fórmula base | Interpretación |
|--------|-------------|----------------|
| Dependency Score | HHI_norm × 100 | Mayor = más concentrado en un país |
| Diversification Score | (1 - HHI_norm) × 100 | Mayor = más diversificado por tipo |
| Observability Risk | % registros "C" | Mayor = más datos confidenciales |
| Stability Index | 100 / (1 + CV) | Mayor = flujos más estables |
| Nearshoring Score | Compuesto 4 señales | Mayor = más señal nearshoring |
| Strategic Score | Ponderado 5 índices | Mayor = posición más favorable |

### Análisis de red (Paso 2)

- **72 nodos:** 40 países + 32 estados
- **~990 aristas:** ponderadas por IED acumulada
- **Hub Score:** 35% grado + 25% betweenness + 25% eigenvector + 15% closeness
- **Comunidades:** algoritmo Louvain, modularidad ≈ 0.17

---

## Consideraciones técnicas importantes

1. **Valores "C" (confidenciales):** No son datos faltantes aleatorios. Se tratan
   como MNAR y se marcan con `is_confidential = True`. Los índices de concentración
   pueden estar subestimados en estados con alta confidencialidad.

2. **Naturaleza acumulativa con revisiones:** Los datos pueden mostrar decrementos
   entre trimestres por revisiones institucionales. No interpretar Qt - Qt-1
   como flujo económico real directo.

3. **Nombre oficial de EE.UU. en el dataset:** `"Estados Unidos de América"`
   (con tilde, nombre completo). Usar este string exacto en filtros.

4. **KMeans vs HDBSCAN:** Con 32 estados, HDBSCAN clasifica casi todo como ruido.
   Se usa KMeans con k=4 forzado por interpretabilidad económica.

5. **Eigenvector centrality:** Los estados tienen eigenvector ≈ 0 porque no están
   directamente conectados entre sí en la red bipartita. Esto es correcto.

---

## Archivos pendientes de integración

Los siguientes dos archivos CSV (generados por el pipeline) están listos para
un análisis sectorial completo que aún no está implementado en la app:

- `Investment_by_Sector_from_the_States.csv` (~60 MB)
- `Investment_by_Sector_from_the_Countries.csv` (~170 MB)

El paso 05 del pipeline y la página 5 de la app están en la hoja de ruta.
