# =============================================================================
# APLICACIÓN STREAMLIT — EXECUTIVE OVERVIEW
# IED Intelligence Platform · México
# =============================================================================
# Punto de entrada de la app. Ejecutar desde IED/:
#   streamlit run app/main.py
#
# RUTAS: este archivo está en IED/app/
#   .parent.parent sube dos niveles → IED/
# =============================================================================

import streamlit as st

st.set_page_config(
    page_title="IED Intelligence Platform · México",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# SISTEMA DE DISEÑO
# =============================================================================
# Paleta: fondo oscuro neutro, azul primario para datos positivos/clave,
# ámbar para tendencias/nearshoring, rojo para riesgo, verde para positivo.
# Sin emojis en el chrome (navegación, headers, labels). Solo en tooltips
# o contextos donde añaden significado sin restar profesionalismo.
# Tipografía: IBM Plex Sans (legibilidad en dashboards analíticos).
# =============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

/* ── Variables de diseño ─────────────────────────────────────────────── */
:root {
  --bg-base:       #0d1117;
  --bg-surface:    #161b22;
  --bg-elevated:   #1c2333;
  --border:        #30363d;
  --border-subtle: #21262d;
  --text-primary:  #e6edf3;
  --text-secondary:#8b949e;
  --text-muted:    #484f58;
  --blue:          #58a6ff;
  --blue-dim:      rgba(88,166,255,0.10);
  --amber:         #d29922;
  --amber-dim:     rgba(210,153,34,0.10);
  --red:           #f85149;
  --red-dim:       rgba(248,81,73,0.10);
  --green:         #3fb950;
  --green-dim:     rgba(63,185,80,0.10);
}

/* ── Base ────────────────────────────────────────────────────────────── */
html, body, [data-testid="stAppViewContainer"] {
  background: var(--bg-base) !important;
  font-family: 'IBM Plex Sans', sans-serif !important;
}

/* ── Sidebar ─────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
  background: var(--bg-surface) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text-secondary) !important; }
[data-testid="stSidebar"] a { color: var(--blue) !important; }

/* ── Ocultar elementos por defecto de Streamlit ─────────────────────── */
#MainMenu, footer, [data-testid="stToolbar"] { visibility: hidden; }
[data-testid="stHeader"] { background: transparent !important; }

/* ── Tipografía global ───────────────────────────────────────────────── */
h1, h2, h3, h4 {
  font-family: 'IBM Plex Sans', sans-serif !important;
  font-weight: 600 !important;
  color: var(--text-primary) !important;
  letter-spacing: -0.02em;
}
p, li, span, label {
  font-family: 'IBM Plex Sans', sans-serif !important;
  color: var(--text-secondary);
}

/* ── Header de página ────────────────────────────────────────────────── */
.page-header {
  padding: 2rem 0 1.5rem 0;
  border-bottom: 1px solid var(--border);
  margin-bottom: 1.5rem;
}
.page-header .platform-label {
  font-size: 0.7rem;
  font-weight: 500;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--blue);
  margin-bottom: 0.4rem;
}
.page-header h1 {
  font-size: 1.8rem !important;
  font-weight: 600 !important;
  color: var(--text-primary) !important;
  margin: 0 0 0.3rem 0 !important;
  line-height: 1.2;
}
.page-header .page-subtitle {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin: 0;
  font-weight: 300;
}
.page-header .meta {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: 0.6rem;
  font-family: 'IBM Plex Mono', monospace;
}

/* ── Tarjetas de métricas ────────────────────────────────────────────── */
.kpi-card {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 1rem 1.2rem;
  margin-bottom: 0.5rem;
}
.kpi-card .kpi-value {
  font-size: 1.6rem;
  font-weight: 600;
  color: var(--text-primary);
  font-family: 'IBM Plex Mono', monospace;
  line-height: 1;
  margin-bottom: 0.25rem;
}
.kpi-card .kpi-label {
  font-size: 0.72rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: 500;
}
.kpi-card .kpi-sub {
  font-size: 0.7rem;
  color: var(--text-muted);
  margin-top: 0.2rem;
  font-family: 'IBM Plex Mono', monospace;
}

/* ── Tarjetas de insights ────────────────────────────────────────────── */
.insight-card {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 1rem 1.2rem;
  margin-bottom: 0.6rem;
  border-left-width: 3px;
  border-left-style: solid;
}
.insight-card .insight-label {
  font-size: 0.65rem;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  margin-bottom: 0.35rem;
}
.insight-card .insight-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.3rem;
  line-height: 1.4;
}
.insight-card .insight-text {
  font-size: 0.8rem;
  color: var(--text-secondary);
  line-height: 1.5;
  margin: 0;
}

/* ── Tarjetas de clusters ────────────────────────────────────────────── */
.cluster-card {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 1rem;
  height: 100%;
  border-top-width: 2px;
  border-top-style: solid;
}
.cluster-card .cluster-type {
  font-size: 0.62rem;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  margin-bottom: 0.3rem;
}
.cluster-card .cluster-name {
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.4rem;
  line-height: 1.3;
}
.cluster-card .cluster-states {
  font-size: 0.72rem;
  color: var(--text-secondary);
  line-height: 1.5;
}
.cluster-card .cluster-metrics {
  font-size: 0.68rem;
  color: var(--text-muted);
  margin-top: 0.5rem;
  font-family: 'IBM Plex Mono', monospace;
  border-top: 1px solid var(--border-subtle);
  padding-top: 0.4rem;
}

/* ── Separadores y secciones ─────────────────────────────────────────── */
.section-label {
  font-size: 0.65rem;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--text-muted);
  margin-bottom: 0.8rem;
  padding-bottom: 0.4rem;
  border-bottom: 1px solid var(--border-subtle);
}
.chart-caption {
  font-size: 0.72rem;
  color: var(--text-muted);
  font-style: italic;
  margin-top: -0.5rem;
  margin-bottom: 1rem;
  font-family: 'IBM Plex Mono', monospace;
}

/* ── Tabs ────────────────────────────────────────────────────────────── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
  background: transparent !important;
  border-bottom: 1px solid var(--border) !important;
  gap: 0 !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
  font-family: 'IBM Plex Sans', sans-serif !important;
  font-size: 0.82rem !important;
  font-weight: 500 !important;
  color: var(--text-muted) !important;
  padding: 0.6rem 1.2rem !important;
  border-radius: 0 !important;
  background: transparent !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
  color: var(--text-primary) !important;
  border-bottom: 2px solid var(--blue) !important;
}

/* ── Selectbox y widgets ─────────────────────────────────────────────── */
[data-testid="stSelectbox"] label,
[data-testid="stSlider"] label {
  font-size: 0.75rem !important;
  color: var(--text-muted) !important;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: 500;
}

/* ── Métricas nativas de Streamlit ───────────────────────────────────── */
[data-testid="stMetric"] {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 0.8rem 1rem;
}
[data-testid="stMetricLabel"] {
  font-size: 0.7rem !important;
  color: var(--text-muted) !important;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
[data-testid="stMetricValue"] {
  font-family: 'IBM Plex Mono', monospace !important;
  font-size: 1.4rem !important;
  color: var(--text-primary) !important;
}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# SIDEBAR — NAVEGACIÓN
# =============================================================================
with st.sidebar:
    st.markdown("""
    <div style="padding: 0.5rem 0 1rem 0; border-bottom: 1px solid #30363d; margin-bottom: 1rem;">
      <div style="font-size:0.62rem; font-weight:600; letter-spacing:0.12em;
                  text-transform:uppercase; color:#58a6ff; margin-bottom:0.3rem;">
        IED Intelligence
      </div>
      <div style="font-size:0.85rem; font-weight:600; color:#e6edf3;">
        México · 2006–2025
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size:0.65rem; font-weight:600; letter-spacing:0.1em;
                text-transform:uppercase; color:#484f58; margin-bottom:0.6rem;">
      Módulos
    </div>
    """, unsafe_allow_html=True)

    nav_items = [
        ("Executive Overview", True),
        ("Network Graph", False),
        ("Regional Profiles", False),
        ("Risk & Dependency", False),
        ("Temporal Dynamics", False),
    ]
    for label, active in nav_items:
        style = (
            "color:#58a6ff; font-weight:500; background:rgba(88,166,255,0.08); "
            "border-left:2px solid #58a6ff;"
        ) if active else "color:#8b949e;"
        st.markdown(
            f"<div style='font-size:0.82rem; padding:0.35rem 0.6rem; "
            f"border-radius:4px; margin-bottom:0.15rem; {style}'>{label}</div>",
            unsafe_allow_html=True
        )

    st.markdown("""
    <div style="position:absolute; bottom:1.5rem; left:1rem; right:1rem;">
      <div style="font-size:0.65rem; color:#484f58; border-top:1px solid #21262d; padding-top:0.8rem;">
        Secretaría de Economía · DGIE<br>
        Datos en USD Millones corrientes
      </div>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# IMPORTS Y RUTAS
# =============================================================================
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
from pathlib import Path
from numpy.polynomial import polynomial as P

BASE = Path(__file__).resolve().parent.parent
PROC = BASE / "data" / "processed" / "proc_2"

def _load(name):
    """Carga parquet o csv como fallback."""
    p = PROC / name
    if p.exists():
        return pd.read_parquet(p)
    c = PROC / (name + ".csv")
    if c.exists():
        return pd.read_csv(c, low_memory=False)
    raise FileNotFoundError(f"{name} no encontrado en {PROC}")

# =============================================================================
# CARGA DE DATOS
# =============================================================================
@st.cache_data
def load_all():
    data = {}
    data["states"]        = _load("investment_by_state.parquet")
    data["countries"]     = _load("investment_by_country.parquet")
    data["types"]         = _load("investment_types.parquet")
    data["scores"]        = _load("state_scores.parquet")
    data["nodes"]         = _load("network_nodes.parquet")
    data["clusters"]      = _load("state_clusters.parquet")
    data["annual"]        = _load("annual_by_state.parquet")
    data["cs_raw"]        = _load("country_by_state.parquet")
    with open(PROC / "graph_stats.json", encoding="utf-8") as f:
        data["graph_stats"] = json.load(f)
    with open(PROC / "cluster_summary.json", encoding="utf-8") as f:
        data["cluster_summary"] = json.load(f)
    return data

D          = load_all()
states_df  = D["states"]
scores_df  = D["scores"]
countries_df = D["countries"]

# =============================================================================
# CÁLCULOS GLOBALES
# =============================================================================
# IED del último trimestre disponible
latest_q        = states_df["Fecha"].max()
latest_q_label  = f"Q{latest_q.quarter} {latest_q.year}"
total_recent    = states_df[states_df["Fecha"] == latest_q]["IED"].sum()

# Países con IED positiva acumulada
active_countries = int(
    (countries_df[countries_df["IED"].notna()]
     .groupby("Origen")["IED"].sum() > 0).sum()
)

# Crecimiento post-COVID
annual_total = states_df.groupby("Year")["IED"].sum()
recent_avg   = float(annual_total[annual_total.index >= 2021].mean())
pre_avg      = float(annual_total[(annual_total.index >= 2015) & (annual_total.index <= 2019)].mean())
growth_pct   = ((recent_avg - pre_avg) / abs(pre_avg) * 100) if pre_avg else 0

# Estados de alto riesgo
high_risk_states = int((scores_df["dependency_score"] > 60).sum())

# Top hallazgos desde los datos
top_hub       = D["graph_stats"]["top_state_hubs"][0]["node"]
top_ns        = scores_df.nlargest(1, "nearshoring_score")["estado"].values[0]
top_dep       = scores_df.nlargest(1, "dependency_score")["estado"].values[0]
top_dep_ctry  = scores_df.nlargest(1, "dependency_score")["top_country"].values[0]
top_dep_share = float(scores_df.nlargest(1, "dependency_score")["top_country_share"].values[0])
n_communities = D["graph_stats"]["n_communities"]

# Años disponibles para filtro
available_years = sorted(states_df["Year"].unique(), reverse=True)

# =============================================================================
# CONFIGURACIÓN DE GRÁFICAS
# =============================================================================
# Tema oscuro consistente con el sistema de diseño
PLOT_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="#161b22",
    plot_bgcolor="#161b22",
    font=dict(family="IBM Plex Sans, sans-serif", color="#8b949e", size=11),
    title_font=dict(family="IBM Plex Sans, sans-serif", color="#e6edf3", size=13),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        bordercolor="#30363d",
        font=dict(size=10)
    ),
    margin=dict(t=40, b=40, l=10, r=10),
    xaxis=dict(gridcolor="#21262d", linecolor="#30363d", tickfont=dict(size=10)),
    yaxis=dict(gridcolor="#21262d", linecolor="#30363d", tickfont=dict(size=10)),
)

# Paleta de colores para gráficas (ordenada por frecuencia de uso)
C_BLUE   = "#58a6ff"
C_AMBER  = "#d29922"
C_GREEN  = "#3fb950"
C_RED    = "#f85149"
C_PURPLE = "#bc8cff"
C_TEAL   = "#39d353"
C_GRAY   = "#8b949e"

# =============================================================================
# HEADER DE PÁGINA
# =============================================================================
st.markdown("""
<div class="page-header">
  <div class="platform-label">IED Intelligence Platform</div>
  <h1>¿Dónde fluye la inversión extranjera en México,<br>quién la mueve y qué tan resiliente es?</h1>
  <p class="page-subtitle">
    Análisis estructural de la Inversión Extranjera Directa · 32 estados · 152 países · Q1 2006 — Q2 2025
  </p>
  <div class="meta">Secretaría de Economía · DGIE · USD Millones corrientes</div>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# KPIs SUPERIORES
# =============================================================================
k1, k2, k3, k4, k5 = st.columns(5)

kpis = [
    (f"${total_recent:,.0f} M", f"IED · {latest_q_label}", "USD Millones · último trimestre"),
    (f"{active_countries}", "Países inversionistas", "Con IED positiva acumulada"),
    (f"{growth_pct:+.1f}%", "Crecimiento post-2020", "vs promedio 2015–2019"),
    (f"{n_communities}", "Comunidades económicas", "Detectadas por algoritmo Louvain"),
    (f"{high_risk_states}", "Estados alto riesgo", "Dependencia >60% en un solo país"),
]

for col, (value, label, sub) in zip([k1, k2, k3, k4, k5], kpis):
    with col:
        st.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-value">{value}</div>
          <div class="kpi-label">{label}</div>
          <div class="kpi-sub">{sub}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='margin-bottom:1.5rem'></div>", unsafe_allow_html=True)

# =============================================================================
# TABS PRINCIPALES
# =============================================================================
tab1, tab2, tab3 = st.tabs([
    "Evolución histórica",
    "Distribución territorial",
    "Hallazgos clave"
])

# ─── Tab 1: Evolución histórica ───────────────────────────────────────────────
with tab1:
    st.markdown("<div class='section-label'>IED total anual · México</div>",
                unsafe_allow_html=True)

    # Datos anuales nacionales
    annual_nat = (states_df.groupby("Year")["IED"]
                  .sum().reset_index()
                  .rename(columns={"IED": "IED_total"}))

    fig_time = go.Figure()

    # Barras anuales
    fig_time.add_trace(go.Bar(
        x=annual_nat["Year"],
        y=annual_nat["IED_total"],
        name="IED anual",
        marker_color=C_BLUE,
        marker_opacity=0.75,
        hovertemplate="<b>%{x}</b><br>IED: $%{y:,.0f} M USD<extra></extra>",
    ))

    # Línea de tendencia lineal
    xn   = annual_nat["Year"].values
    yn   = annual_nat["IED_total"].fillna(0).values
    coef = P.polyfit(xn, yn, 1)
    fig_time.add_trace(go.Scatter(
        x=xn, y=P.polyval(xn, coef),
        name="Tendencia",
        line=dict(color=C_AMBER, width=1.5, dash="dot"),
        hoverinfo="skip",
    ))

    # Sombreado período nearshoring
    fig_time.add_vrect(
        x0=2020.5, x1=annual_nat["Year"].max() + 0.5,
        fillcolor=f"rgba(88,166,255,0.04)", line_width=0,
    )
    fig_time.add_annotation(
        x=2022, y=annual_nat["IED_total"].max() * 0.95,
        text="Período nearshoring", showarrow=False,
        font=dict(size=9, color=C_BLUE), xanchor="center",
    )

    fig_time.update_layout(
        **PLOT_LAYOUT,
        height=360,
        title="IED total México — USD Millones anuales",
        xaxis_title=None,
        yaxis_title="USD Millones",
        yaxis_tickformat="$,.0f",
        showlegend=True,
        legend=dict(orientation="h", y=-0.12, x=0),
        bargap=0.25,
    )
    st.plotly_chart(fig_time, use_container_width=True)
    st.markdown(
        "<div class='chart-caption'>Fuente: SE–DGIE · Totales anuales · "
        "Datos sujetos a revisión institucional</div>",
        unsafe_allow_html=True
    )

# ─── Tab 2: Distribución territorial ─────────────────────────────────────────
with tab2:
    col_ctrl, _ = st.columns([1, 3])
    with col_ctrl:
        selected_year = st.selectbox(
            "Año",
            options=available_years,
            index=0,
            key="year_filter_main"
        )

    st.markdown("<div style='margin-bottom:0.5rem'></div>", unsafe_allow_html=True)

    col_l, col_r = st.columns([3, 2])

    with col_l:
        st.markdown(
            f"<div class='section-label'>Top estados por IED · {selected_year}</div>",
            unsafe_allow_html=True
        )

        # Filtrar por año seleccionado
        states_year = (
            states_df[states_df["Year"] == selected_year]
            .groupby("Entidad federativa")["IED"]
            .sum().reset_index()
            .sort_values("IED", ascending=True)
            .tail(15)
        )

        fig_states = go.Figure(go.Bar(
            x=states_year["IED"],
            y=states_year["Entidad federativa"],
            orientation="h",
            marker=dict(
                color=states_year["IED"],
                colorscale=[[0, "#1c2333"], [1, C_BLUE]],
                showscale=False,
            ),
            hovertemplate="<b>%{y}</b><br>IED: $%{x:,.0f} M USD<extra></extra>",
        ))
        fig_states.update_layout(
            **PLOT_LAYOUT,
            height=430,
            title=f"Top 15 estados por IED recibida · {selected_year}",
            xaxis_title="USD Millones",
            xaxis_tickformat="$,.0f",
            yaxis_title=None,
        )
        st.plotly_chart(fig_states, use_container_width=True)

    with col_r:
        st.markdown(
            "<div class='section-label'>Origen del capital · acumulado histórico</div>",
            unsafe_allow_html=True
        )

        top_countries = (
            countries_df[countries_df["IED"].notna()]
            .groupby("Origen")["IED"].sum()
            .nlargest(10).reset_index()
            .rename(columns={"Origen": "País"})
        )
        # Agrupar el resto como "Otros"
        total_ied    = countries_df[countries_df["IED"].notna()]["IED"].sum()
        top_10_total = top_countries["IED"].sum()
        otros        = pd.DataFrame([{"País": "Otros", "IED": total_ied - top_10_total}])
        pie_data     = pd.concat([top_countries, otros], ignore_index=True)

        fig_pie = go.Figure(go.Pie(
            labels=pie_data["País"],
            values=pie_data["IED"],
            hole=0.5,
            textinfo="percent",
            textfont=dict(size=10, family="IBM Plex Mono"),
            hovertemplate="<b>%{label}</b><br>$%{value:,.0f} M USD<br>%{percent}<extra></extra>",
            marker=dict(
                colors=[
                    C_BLUE, C_AMBER, C_GREEN, C_RED, C_PURPLE,
                    C_TEAL, "#79c0ff", "#e3b341", "#56d364", "#ff7b72", C_GRAY
                ],
                line=dict(color="#0d1117", width=1.5),
            ),
        ))
        fig_pie.update_layout(
            **PLOT_LAYOUT,
            height=430,
            title="Países de origen · participación acumulada",
            showlegend=True,
            legend=dict(
                orientation="v", x=1.0, y=0.5,
                font=dict(size=9), itemsizing="constant",
            ),
            margin=dict(t=40, b=20, l=0, r=120),
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown(
        "<div class='chart-caption'>IED acumulada 2006–2025 · Solo top 10 países mostrados en detalle</div>",
        unsafe_allow_html=True
    )

# ─── Tab 3: Hallazgos clave ───────────────────────────────────────────────────
with tab3:
    st.markdown(
        "<div class='section-label'>Hallazgos estructurales · generados desde los datos</div>",
        unsafe_allow_html=True
    )

    # Definición de insights: título = conclusión, texto = evidencia mínima
    insights = [
        {
            "color":  C_BLUE,
            "label":  "Red de inversión",
            "title":  f"{top_hub} es el nodo más estratégico de la red nacional",
            "text":   (f"Concentra la mayor centralidad estructural entre los 32 estados, "
                       f"actuando como punto de conexión entre múltiples países inversores. "
                       f"Ver Network Graph para el análisis completo de la red."),
        },
        {
            "color":  C_AMBER,
            "label":  "Nearshoring",
            "title":  f"{top_ns} lidera la aceleración de IED post-2020",
            "text":   (f"Registra la mayor señal de nearshoring del análisis, con crecimiento "
                       f"consistente en el período 2021–2024. "
                       f"Ver Temporal Dynamics para el análisis pre/post reconfiguración."),
        },
        {
            "color":  C_RED,
            "label":  "Riesgo de concentración",
            "title":  f"{top_dep_share:.0f}% de la IED de {top_dep} proviene de un solo país",
            "text":   (f"{top_dep_ctry} domina la estructura de inversión de {top_dep}, "
                       f"creando dependencia estructural ante variaciones en la relación bilateral. "
                       f"Ver Risk & Dependency para el mapa completo de vulnerabilidades."),
        },
        {
            "color":  C_GREEN,
            "label":  "Ecosistemas económicos",
            "title":  f"La red de IED se organiza en {n_communities} comunidades con lógica territorial",
            "text":   (f"El análisis de redes revela que países y estados no se conectan aleatoriamente, "
                       f"sino en grupos con patrones geográficos y sectoriales definidos. "
                       f"Ver Network Graph para los perfiles de cada comunidad."),
        },
        {
            "color":  C_GRAY,
            "label":  "Nota metodológica",
            "title":  "Parte de los datos presenta confidencialidad estadística",
            "text":   (f"La SE clasifica como confidenciales los registros que identificarían "
                       f"a un inversionista específico. Los índices de concentración pueden estar "
                       f"subestimados en los estados con mayor proporción de datos reservados."),
        },
    ]

    col_ins1, col_ins2 = st.columns(2)
    for i, ins in enumerate(insights):
        col = col_ins1 if i % 2 == 0 else col_ins2
        with col:
            st.markdown(f"""
            <div class="insight-card" style="border-left-color:{ins['color']};">
              <div class="insight-label" style="color:{ins['color']};">{ins['label']}</div>
              <div class="insight-title">{ins['title']}</div>
              <p class="insight-text">{ins['text']}</p>
            </div>
            """, unsafe_allow_html=True)

# =============================================================================
# TIPOLOGÍA DE ESTADOS
# =============================================================================
st.markdown("<div style='margin-top:2rem'></div>", unsafe_allow_html=True)
st.markdown(
    "<div class='section-label'>Tipología estructural de estados · 4 grupos identificados por clustering</div>",
    unsafe_allow_html=True
)

clusters       = D["cluster_summary"]
cluster_colors = [C_BLUE, C_AMBER, C_GREEN, C_PURPLE]
cluster_cols   = st.columns(len(clusters))

for i, (col, cluster) in enumerate(zip(cluster_cols, clusters)):
    with col:
        color = cluster_colors[i % len(cluster_colors)]
        # Mostrar hasta 5 estados, resto como contador
        states_shown = cluster["states"][:5]
        states_str   = " · ".join(states_shown)
        if len(cluster["states"]) > 5:
            states_str += f" · +{len(cluster['states']) - 5} más"

        st.markdown(f"""
        <div class="cluster-card" style="border-top-color:{color};">
          <div class="cluster-type" style="color:{color};">
            Grupo {cluster['cluster_id'] + 1} · {cluster['n_states']} estados
          </div>
          <div class="cluster-name">{cluster['cluster_name']}</div>
          <div class="cluster-states">{states_str}</div>
          <div class="cluster-metrics">
            Dep {cluster['mean_dependency']:.0f} ·
            Div {cluster['mean_diversification']:.0f} ·
            NS {cluster['mean_nearshoring']:.0f} ·
            Hub {cluster['mean_hub_score']:.0f}
          </div>
        </div>
        """, unsafe_allow_html=True)

# =============================================================================
# FOOTER
# =============================================================================
st.markdown("<div style='margin-top:3rem'></div>", unsafe_allow_html=True)
st.markdown("""
<div style="border-top:1px solid #21262d; padding-top:1rem; margin-top:1rem;">
  <span style="font-size:0.7rem; color:#484f58; font-family:'IBM Plex Mono',monospace;">
    IED Intelligence Platform · Secretaría de Economía · DGIE ·
    Q1 2006 — Q2 2025 · USD Millones corrientes ·
    Análisis estructural con fines académicos y de portafolio
  </span>
</div>
""", unsafe_allow_html=True)