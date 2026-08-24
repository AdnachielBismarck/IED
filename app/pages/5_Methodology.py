import json
from pathlib import Path

import pandas as pd
import streamlit as st

from app.shared import (
    apply_product_styles,
    load_metadata,
    render_header,
    render_provenance,
    render_sidebar,
)


st.set_page_config(
    page_title="Metodología · IED México",
    layout="wide",
    initial_sidebar_state="auto",
)
apply_product_styles()
render_sidebar()

ROOT = Path(__file__).resolve().parent.parent.parent
PROC = ROOT / "data" / "processed" / "proc_2"


@st.cache_data
def load_methodology_data():
    with open(PROC / "graph_stats.json", encoding="utf-8") as file:
        graph = json.load(file)
    with open(PROC / "clustering_diagnostics.json", encoding="utf-8") as file:
        clustering = json.load(file)
    scores = pd.read_parquet(PROC / "state_scores.parquet")
    return graph, clustering, scores


metadata = load_metadata()
graph, clustering, scores = load_methodology_data()

render_header(
    "Metodología",
    "Definiciones, supuestos y límites del análisis",
    "Documentación técnica para interpretar los indicadores, reproducir resultados y distinguir evidencia descriptiva de inferencia causal.",
)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Fecha de corte", metadata["period_label"].split(" - ")[-1])
m2.metric("Entidades", metadata["states"])
m3.metric("Relaciones de red", f"{graph['n_edges']:,}")
m4.metric("Tipologías seleccionadas", clustering["selected_k"])

tab_method, tab_dictionary, tab_quality = st.tabs(
    ["Diseño analítico", "Diccionario de indicadores", "Calidad y límites"]
)

with tab_method:
    st.subheader("Flujo de procesamiento")
    st.markdown(
        """
        1. **Ingesta y normalización.** Los libros de la Secretaría de Economía se transforman a formato largo, se normalizan fechas y se eliminan agregados identificados como totales.
        2. **Preparación analítica.** Se generan tablas por estado, país, tipo de inversión y sector; los artefactos finales se almacenan en Parquet.
        3. **Red bipartita.** Cada arista conecta un país de origen con un estado receptor. Su peso es la IED positiva acumulada y su distancia para caminos mínimos es `1 / IED`.
        4. **Indicadores estatales.** Las métricas se calculan de forma comparable en escala de 0 a 100.
        5. **Tipología.** KMeans evalúa soluciones entre `k=2` y `k=6`. Se selecciona la mayor silhouette entre soluciones con al menos tres estados por grupo.
        """
    )

    st.subheader("Selección del número de grupos")
    candidates = pd.DataFrame(clustering["candidates"]).rename(
        columns={
            "k": "Grupos",
            "silhouette": "Silhouette",
            "calinski_harabasz": "Calinski-Harabasz",
            "min_cluster_size": "Grupo mínimo",
        }
    )
    st.dataframe(
        candidates.style.format(
            {"Silhouette": "{:.3f}", "Calinski-Harabasz": "{:.2f}"}
        ),
        width="stretch",
        hide_index=True,
    )
    st.caption(
        f"Solución seleccionada: k={clustering['selected_k']}. "
        f"Los dos primeros componentes principales explican "
        f"{sum(clustering['pca_explained_variance']):.1%} de la varianza."
    )

with tab_dictionary:
    definitions = pd.DataFrame(
        [
            {
                "Indicador": "Dependency Score",
                "Qué mide": "Concentración de la IED positiva por país de origen mediante HHI normalizado.",
                "Lectura": "Mayor valor implica mayor concentración.",
                "Precaución": "Puede subestimarse cuando existen valores confidenciales.",
            },
            {
                "Indicador": "Diversification Score",
                "Qué mide": "Distribución reciente entre tipos de inversión.",
                "Lectura": "Mayor valor implica una mezcla más equilibrada.",
                "Precaución": "No mide productividad ni calidad de la inversión.",
            },
            {
                "Indicador": "Observability Risk",
                "Qué mide": "Porcentaje de registros publicados como confidenciales.",
                "Lectura": "Mayor valor implica menor visibilidad estadística.",
                "Precaución": "No equivale directamente a riesgo económico.",
            },
            {
                "Indicador": "Stability Index",
                "Qué mide": "Inverso del coeficiente de variación de los flujos históricos.",
                "Lectura": "Mayor valor implica menor variabilidad relativa.",
                "Precaución": "Es sensible a desinversiones y revisiones de cifras.",
            },
            {
                "Indicador": "Nearshoring Score",
                "Qué mide": "Crecimiento 2021–2024, participación estadounidense y peso del período reciente.",
                "Lectura": "Mayor valor implica una señal descriptiva más intensa.",
                "Precaución": "No identifica causalidad ni sustituye evidencia sectorial.",
            },
            {
                "Indicador": "Hub Score",
                "Qué mide": "Volumen, intermediación, centralidad espectral y cercanía dentro de la red.",
                "Lectura": "Mayor valor implica una posición más conectada.",
                "Precaución": "Centralidad no equivale automáticamente a resiliencia.",
            },
            {
                "Indicador": "Strategic Score",
                "Qué mide": "Síntesis ponderada de diversificación, dependencia, estabilidad, nearshoring y observabilidad.",
                "Lectura": "Permite comparación relativa entre estados.",
                "Precaución": "Depende de ponderaciones explícitas y no es una recomendación de inversión.",
            },
        ]
    )
    st.dataframe(definitions, width="stretch", hide_index=True)
    st.download_button(
        "Descargar diccionario en CSV",
        data=definitions.to_csv(index=False).encode("utf-8-sig"),
        file_name="diccionario_indicadores_ied.csv",
        mime="text/csv",
    )

with tab_quality:
    st.subheader("Controles implementados")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            """
            - Cobertura de las 32 entidades federativas.
            - Fechas válidas y fecha de corte centralizada.
            - Indicadores restringidos al rango de 0 a 100.
            - Estados únicos en tablas de scoring y clustering.
            - Distancia de red verificada contra la inversa del peso.
            - Tamaño mínimo de grupo en la tipología seleccionada.
            """
        )
    with c2:
        st.markdown(
            """
            - Pruebas automáticas de todos los artefactos críticos.
            - Pruebas de ejecución de cada página Streamlit.
            - Integración continua en Python 3.11.
            - Artefactos versionados para despliegue reproducible.
            - Metadatos consumidos por aplicación y reporte.
            - Semilla fija para algoritmos estocásticos.
            """
        )

    st.subheader("Limitaciones de interpretación")
    st.warning(
        "Los valores confidenciales son datos faltantes no aleatorios. Los rankings deben "
        "interpretarse junto con Observability Risk, especialmente en análisis desagregados."
    )
    st.info(
        "Las señales posteriores a 2021 son descriptivas. Establecer un efecto causal de "
        "nearshoring requeriría un diseño econométrico y variables externas adicionales."
    )
    st.markdown(
        "Los flujos negativos se conservan en las series temporales porque pueden representar "
        "desinversión o revisiones. Para calcular cuotas y concentración se utilizan relaciones "
        "con IED positiva."
    )

    export = scores[
        [
            "estado",
            "dependency_score",
            "diversification_score",
            "observability_risk",
            "stability_index",
            "nearshoring_score",
            "strategic_score",
        ]
    ].sort_values("strategic_score", ascending=False)
    st.download_button(
        "Descargar indicadores estatales",
        data=export.to_csv(index=False).encode("utf-8-sig"),
        file_name="indicadores_estatales_ied.csv",
        mime="text/csv",
    )

render_provenance()
