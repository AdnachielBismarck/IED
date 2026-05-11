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
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
from pathlib import Path
from numpy.polynomial import polynomial as P

st.set_page_config(
    page_title="IED Intelligence Platform · México",
    page_icon="🇲🇽",
    layout="wide",
    initial_sidebar_state="auto",
)

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

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
    --amber:         #d29922;
    --red:           #f85149;
    --green:         #3fb950;
    --purple:        #bc8cff;
    --gray:          #8b949e;
  }

  /* Fuente solo a contenido — NO a html/body/* para no romper iconos de Streamlit */
  h1, h2, h3, h4, p, label,
  [data-testid="stMarkdownContainer"] {
    font-family: 'IBM Plex Sans', sans-serif !important;
    color: var(--text-primary);
  }

  [data-testid="stSidebar"] {
    background: var(--bg-surface) !important;
    border-right: 1px solid var(--border) !important;
  }

  footer { visibility: hidden; }

  /* KPI cards */
  .kpi-card {
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1rem 1.2rem;
    border-top: 2px solid var(--blue);
    text-align: center;
  }
  .kpi-card .kpi-val {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.6rem;
    font-weight: 500;
    color: var(--blue);
    margin: 0;
    line-height: 1.2;
  }
  .kpi-card .kpi-label {
    font-size: 0.72rem;
    color: var(--text-secondary);
    margin: 0.2rem 0 0;
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }
  .kpi-card .kpi-sub {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.76rem;
    color: var(--text-muted);
    margin: 0.1rem 0 0;
  }

  /* Insight cards */
  .insight-card {
    background: var(--bg-elevated);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.7rem;
  }
  .insight-card .ic-tag {
    font-size: 0.68rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin: 0 0 0.35rem;
  }
  .insight-card .ic-title {
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0 0 0.4rem;
    line-height: 1.3;
  }
  .insight-card .ic-text {
    font-size: 0.84rem;
    color: var(--text-secondary);
    margin: 0 0 0.5rem;
    line-height: 1.6;
  }
  .insight-card .ic-impl {
    font-size: 0.80rem;
    font-weight: 500;
    margin: 0;
  }

  /* Cluster cards */
  .cluster-card {
    background: var(--bg-elevated);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1rem 1.1rem;
    min-height: 210px;
  }
  .cluster-card .cl-id {
    font-size: 0.68rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin: 0 0 0.2rem;
  }
  .cluster-card .cl-name {
    font-size: 0.88rem;
    font-weight: 600;
    margin: 0 0 0.4rem;
    line-height: 1.3;
  }
  .cluster-card .cl-states {
    font-size: 0.74rem;
    color: var(--text-secondary);
    margin: 0 0 0.4rem;
    line-height: 1.5;
  }
  .cluster-card .cl-metrics {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.70rem;
    color: var(--text-muted);
    margin: 0;
    border-top: 1px solid var(--border-subtle);
    padding-top: 0.4rem;
  }

  /* Intro / filter box */
  .filter-box {
    background: var(--bg-elevated);
    border: 1px solid var(--border-subtle);
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin-bottom: 1rem;
  }

  /* Nota metodológica */
  .method-note {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    color: var(--text-muted);
    border-top: 1px solid var(--border-subtle);
    padding-top: 0.4rem;
    margin-top: 0.6rem;
  }
</style>
""", unsafe_allow_html=True)

# ── Rutas ─────────────────────────────────────────────────────────────────────
BASE = Path(__file__).resolve().parent.parent
PROC = BASE / "data" / "processed" / "proc_2"

def _load(name):
    p = PROC / name
    if p.exists():
        return pd.read_parquet(p)
    c = PROC / (name + ".csv")
    if c.exists():
        return pd.read_csv(c, low_memory=False)
    raise FileNotFoundError(f"{name} no encontrado en {PROC}")

@st.cache_data
def load_all():
    data = {}
    data["states"]      = _load("investment_by_state.parquet")
    data["countries"]   = _load("investment_by_country.parquet")
    data["types"]       = _load("investment_types.parquet")
    data["scores"]      = _load("state_scores.parquet")
    data["nodes"]       = _load("network_nodes.parquet")
    data["clusters"]    = _load("state_clusters.parquet")
    data["annual"]      = _load("annual_by_state.parquet")
    data["ctry_prof"]   = _load("country_profiles.parquet")
    data["top_inv"]     = _load("top_investors_per_state.parquet")
    data["types_state"] = _load("types_by_state.parquet")
    data["cs_raw"]      = _load("country_by_state.parquet")
    with open(PROC / "graph_stats.json", encoding="utf-8") as f:
        data["graph_stats"] = json.load(f)
    with open(PROC / "community_profiles.json", encoding="utf-8") as f:
        data["communities"] = json.load(f)
    with open(PROC / "cluster_summary.json", encoding="utf-8") as f:
        data["cluster_summary"] = json.load(f)
    return data

D            = load_all()
states_df    = D["states"]
scores_df    = D["scores"]
countries_df = D["countries"]

# ── Métricas de cabecera ───────────────────────────────────────────────────────
total_recent     = states_df[states_df["Fecha"] == states_df["Fecha"].max()]["IED"].sum()
active_countries = int((countries_df[countries_df["IED"].notna()].groupby("Origen")["IED"].sum() > 0).sum())
high_risk_states = int((scores_df["dependency_score"] > 60).sum())
gs               = D["graph_stats"]

# ── Helpers de layout ─────────────────────────────────────────────────────────
# PLOT_LAYOUT sin xaxis/yaxis · LEGEND sin font · para evitar colisiones
PLOT_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="#161b22",
    plot_bgcolor="#161b22",
    font=dict(family="IBM Plex Sans, sans-serif", color="#8b949e", size=11),
    title_font=dict(family="IBM Plex Sans, sans-serif", color="#e6edf3", size=13),
)
XAXIS_BASE = dict(gridcolor="#21262d", linecolor="#30363d")
YAXIS_BASE = dict(gridcolor="#21262d", linecolor="#30363d")
LEGEND_H   = dict(bgcolor="rgba(0,0,0,0)", bordercolor="#30363d", orientation="h", y=-0.22)
LEGEND_V   = dict(bgcolor="rgba(0,0,0,0)", bordercolor="#30363d")
MARGIN_STD = dict(t=45, b=45, l=10, r=10)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## IED Intelligence")
    st.markdown("**Mexico · 2006–2025**")
    st.markdown("---")
    st.markdown(
        "<p style='font-size:0.78rem;color:#8b949e;'>Fuente: Secretaría de Economía · DGIE<br>"
        "Datos en USD Millones corrientes</p>",
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown(
        "<p style='font-size:0.90rem;color:#484f58;'>Diseñado por Adnachiel Avendaño</p>",
        unsafe_allow_html=True,
    )

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    "<h1 style='font-size:1.6rem;margin-bottom:0.2rem;'>"
    "¿Dónde fluye la inversión extranjera en México, quién la mueve "
    "y qué tan resiliente es cada estado ante cambios en ese flujo?</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='font-size:0.9rem;color:#8b949e;margin-top:0;margin-bottom:0.3rem;'>"
    "Executive Overview — Período Q1 2006 — Q2 2025 · Secretaría de Economía · DGIE</p>",
    unsafe_allow_html=True,
)

st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.markdown(f"""<div class="kpi-card">
      <p class="kpi-val">${total_recent:,.0f} M</p>
      <p class="kpi-label">IED último trimestre</p>
      <p class="kpi-sub">USD Millones</p>
    </div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""<div class="kpi-card">
      <p class="kpi-val">{active_countries}</p>
      <p class="kpi-label">Países inversionistas</p>
      <p class="kpi-sub">Con flujos activos</p>
    </div>""", unsafe_allow_html=True)
with k3:
    st.markdown(f"""<div class="kpi-card">
      <p class="kpi-val">32</p>
      <p class="kpi-label">Estados cubiertos</p>
      <p class="kpi-sub">Cobertura nacional</p>
    </div>""", unsafe_allow_html=True)
with k4:
    st.markdown(f"""<div class="kpi-card">
      <p class="kpi-val">{gs['n_communities']}</p>
      <p class="kpi-label">Comunidades económicas</p>
      <p class="kpi-sub">Algoritmo Louvain</p>
    </div>""", unsafe_allow_html=True)
with k5:
    st.markdown(f"""<div class="kpi-card" style="border-top-color:#f85149;">
      <p class="kpi-val" style="color:#f85149;">{high_risk_states}</p>
      <p class="kpi-label">Estados alto riesgo</p>
      <p class="kpi-sub">Dependency score &gt; 60</p>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='margin-top:1.4rem;'></div>", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["Evolución Temporal", "Distribución Territorial", "Hallazgos Clave"])

# =============================================================================
# TAB 1 — EVOLUCIÓN TEMPORAL
# =============================================================================
with tab1:
    annual_total = (
        D["states"].groupby("Year")["IED"].sum()
        .reset_index()
        .rename(columns={"IED": "IED_total"})
    )

    fig_time = go.Figure()
    fig_time.add_trace(go.Bar(
        x=annual_total["Year"], y=annual_total["IED_total"],
        name="IED Total (USD M)",
        marker_color="#58a6ff", marker_line_width=0, opacity=0.8,
    ))

    # Línea de tendencia lineal
    xn   = annual_total["Year"].values
    yn   = annual_total["IED_total"].fillna(0).values
    coef = P.polyfit(xn, yn, 1)
    fig_time.add_trace(go.Scatter(
        x=xn, y=P.polyval(xn, coef),
        name="Tendencia lineal",
        line=dict(color="#d29922", width=2, dash="dot"),
    ))

    fig_time.add_vrect(
        x0=2020.5, x1=annual_total["Year"].max() + 0.5,
        fillcolor="rgba(88,166,255,0.04)", line_width=0,
        annotation_text="Período nearshoring",
        annotation_position="top left",
        annotation_font=dict(color="#58a6ff", size=9),
    )
    fig_time.update_layout(
        **PLOT_LAYOUT,
        title="La tendencia de largo plazo es positiva, con aceleración visible post-2021",
        height=400,
        xaxis=dict(**XAXIS_BASE, title="Año", tickfont=dict(size=10), dtick=2),
        yaxis=dict(**YAXIS_BASE, title="IED (USD Millones)", tickfont=dict(size=10)),
        legend=LEGEND_H,
        margin=MARGIN_STD,
    )
    st.plotly_chart(fig_time, use_container_width=True)
    st.markdown(
        "<p class='method-note'>Agregado anual (suma de 4 trimestres) · "
        "Tendencia: regresión lineal OLS sobre el período completo · "
        "Fuente: Secretaría de Economía · DGIE</p>",
        unsafe_allow_html=True,
    )

# =============================================================================
# TAB 2 — DISTRIBUCIÓN TERRITORIAL
# =============================================================================
with tab2:
    # ── Selector de año dentro de la página ───────────────────────────────────
    st.markdown("<div class='filter-box'>", unsafe_allow_html=True)
    years_avail = sorted(D["states"]["Year"].dropna().unique().astype(int), reverse=True)
    selected_year = st.selectbox(
        "Año para el ranking de estados",
        years_avail,
        index=0,
        key="year_selector",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # Top 15 estados — año seleccionado
    recent_states = (
        D["states"][D["states"]["Year"] == selected_year]
        .groupby("Entidad federativa")["IED"].sum()
        .reset_index()
        .sort_values("IED", ascending=True)
        .tail(15)
    )

    fig_states = go.Figure(go.Bar(
        x=recent_states["IED"],
        y=recent_states["Entidad federativa"],
        orientation="h",
        marker=dict(color=recent_states["IED"], colorscale="Blues", showscale=False),
        marker_line_width=0,
        text=[f"${v:,.0f}" for v in recent_states["IED"]],
        textposition="outside",
        textfont=dict(size=8, color="#8b949e"),
    ))
    fig_states.update_layout(
        **PLOT_LAYOUT,
        title=f"Ciudad de México y los estados fronterizos dominan la captación en {selected_year}",
        height=480,
        xaxis=dict(**XAXIS_BASE, title="IED (USD Millones)", tickfont=dict(size=10)),
        yaxis=dict(**YAXIS_BASE, title="", tickfont=dict(size=10)),
        margin=dict(t=45, b=30, l=10, r=60),
    )
    st.plotly_chart(fig_states, use_container_width=True)
    st.markdown(
        f"<p class='method-note'>Top 15 estados por IED acumulada en {selected_year} · "
        "Suma anual de los 4 trimestres · Fuente: Secretaría de Economía · DGIE</p>",
        unsafe_allow_html=True,
    )

    st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)

    # Dona de países con "Otros" como categoría residual
    all_ctry = (
        D["countries"][D["countries"]["IED"].notna()]
        .groupby("Origen")["IED"].sum()
        .reset_index()
        .sort_values("IED", ascending=False)
    )
    top_n    = 11
    top_ctry = all_ctry.head(top_n).copy()
    otros    = all_ctry.iloc[top_n:]["IED"].sum()
    if otros > 0:
        otros_row = pd.DataFrame([{"Origen": "Otros", "IED": otros}])
        top_ctry  = pd.concat([top_ctry, otros_row], ignore_index=True)
    top_ctry = top_ctry.rename(columns={"Origen": "País"})

    fig_pie = px.pie(
        top_ctry, values="IED", names="País",
        template="plotly_dark", hole=0.4, height=400,
        color_discrete_sequence=[
            "#58a6ff","#3fb950","#d29922","#bc8cff","#f85149",
            "#58d4d4","#ff8c69","#a8d8a8","#c9b1ff","#ffcc80",
            "#90caf9","#8b949e",
        ],
    )
    fig_pie.update_layout(
        **PLOT_LAYOUT,
        title="EE.UU. lidera la composición acumulada; Europa y Asia complementan el flujo",
        legend=dict(**LEGEND_V, font=dict(size=9)),
        margin=dict(t=45, b=20, l=10, r=10),
    )
    fig_pie.update_traces(textfont_size=9)
    st.plotly_chart(fig_pie, use_container_width=True)
    st.markdown(
        "<p class='method-note'>Acumulado histórico 2006–Q2 2025 · "
        "Top 11 países de origen + categoría residual 'Otros' · "
        "Fuente: Secretaría de Economía · DGIE</p>",
        unsafe_allow_html=True,
    )

# =============================================================================
# TAB 3 — HALLAZGOS CLAVE
# =============================================================================
with tab3:
    # Datos dinámicos para los hallazgos
    top_hub      = gs["top_state_hubs"][0]["node"]
    top_ns       = scores_df.nlargest(1, "nearshoring_score")["estado"].values[0]
    top_dep      = scores_df.nlargest(1, "dependency_score")["estado"].values[0]
    top_dep_ctry = scores_df.nlargest(1, "dependency_score")["top_country"].values[0]
    top_dep_sh   = float(scores_df.nlargest(1, "dependency_score")["top_country_share"].values[0])

    insights = [
        {
            "color": "#3fb950",
            "tag":   "Hub Estratégico",
            "title": f"{top_hub} concentra la mayor centralidad estructural de la red",
            "text":  f"Con el mayor Hub Score del sistema, {top_hub} actúa como nodo articulador "
                     f"entre múltiples fuentes de inversión extranjera, combinando volumen, "
                     f"diversificación y posición de puente en la red.",
            "impl":  "Alta resiliencia estructural. Punto de entrada preferente para IED diversificada.",
            "impl_color": "#3fb950",
        },
        {
            "color": "#d29922",
            "tag":   "Señal Nearshoring",
            "title": f"{top_ns} lidera la aceleración de inversión post-pandemia",
            "text":  f"{top_ns} presenta la mayor señal de nearshoring del sistema, con aceleración "
                     f"de IED en el período 2021–2024 consistente con la reconfiguración de cadenas "
                     f"de suministro hacia el continente americano.",
            "impl":  "Oportunidad de expansión industrial y desarrollo de infraestructura logística.",
            "impl_color": "#d29922",
        },
        {
            "color": "#f85149",
            "tag":   "Dependencia Estructural",
            "title": f"{top_dep} presenta concentración crítica en un solo origen",
            "text":  f"El {top_dep_sh:.0f}% de la IED de {top_dep} proviene de {top_dep_ctry}, "
                     f"generando una vulnerabilidad estructural ante shocks en ese país de origen "
                     f"(fluctuaciones cambiarias, tensiones comerciales, cambios regulatorios).",
            "impl":  "Riesgo sistémico ante shocks externos. Diversificación de origen es prioritaria.",
            "impl_color": "#f85149",
        },
        {
            "color": "#58a6ff",
            "tag":   "Red de Inversión",
            "title": f"La red de IED se organiza en {gs['n_communities']} ecosistemas económicos diferenciados",
            "text":  f"El algoritmo Louvain detectó {gs['n_communities']} comunidades con densidad "
                     f"{gs['density']:.2f} y modularidad {gs['modularity']:.2f}. Cada ecosistema tiene "
                     f"lógica territorial y sectorial propia: automotriz japonés, bloque norteamericano, "
                     f"corredor industrial del noreste, entre otros.",
            "impl":  "Estrategias de atracción de inversión deben segmentarse por ecosistema, no por estado.",
            "impl_color": "#58a6ff",
        },
        {
            "color": "#8b949e",
            "tag":   "Observabilidad Parcial",
            "title": "Alta confidencialidad en datos sectoriales limita la visibilidad real del sistema",
            "text":  "Una fracción relevante de los registros de la Secretaría de Economía presenta "
                     "valores confidenciales ('C'). Esto genera observabilidad parcial estructural "
                     "en varios estados, que pueden estar subestimados o sobreestimados en los rankings.",
            "impl":  "Los indicadores deben interpretarse con cautela en estados de alta opacidad.",
            "impl_color": "#8b949e",
        },
    ]

    # Dos columnas para los hallazgos
    col_ins1, col_ins2 = st.columns(2)
    for i, ins in enumerate(insights):
        col = col_ins1 if i % 2 == 0 else col_ins2
        with col:
            st.markdown(f"""
            <div class="insight-card" style="border-left:3px solid {ins['color']};">
              <p class="ic-tag" style="color:{ins['color']};">{ins['tag']}</p>
              <p class="ic-title">{ins['title']}</p>
              <p class="ic-text">{ins['text']}</p>
              <p class="ic-impl" style="color:{ins['impl_color']};">Implicación: {ins['impl']}</p>
            </div>""", unsafe_allow_html=True)

st.markdown("<div style='margin-top:1.6rem;'></div>", unsafe_allow_html=True)

# =============================================================================
# TIPOLOGÍA ESTRUCTURAL DE ESTADOS
# =============================================================================
st.markdown(
    "<h2 style='font-size:1.2rem;color:#e6edf3;margin-bottom:0.3rem;'>"
    "Tipología estructural de estados</h2>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='font-size:0.85rem;color:#8b949e;margin-bottom:1rem;'>"
    "Clasificación de los 32 estados en grupos homogéneos según sus patrones estructurales "
    "de IED, obtenida mediante KMeans sobre indicadores de dependencia, diversificación, "
    "estabilidad y nearshoring.</p>",
    unsafe_allow_html=True,
)

clusters       = D["cluster_summary"]
cluster_colors = ["#58a6ff", "#3fb950", "#d29922", "#bc8cff", "#f85149"]
cl_cols        = st.columns(len(clusters))

for i, (col, cluster) in enumerate(zip(cl_cols, clusters)):
    color       = cluster_colors[i % len(cluster_colors)]
    states_list = ", ".join(cluster["states"][:4])
    if len(cluster["states"]) > 4:
        states_list += f" +{len(cluster['states']) - 4} más"
    with col:
        st.markdown(f"""
        <div class="cluster-card" style="border-left:3px solid {color};">
          <p class="cl-id" style="color:{color};">Cluster {cluster['cluster_id']}</p>
          <p class="cl-name" style="color:{color};">{cluster['cluster_name']}</p>
          <p style="font-size:0.72rem;color:#8b949e;margin:0 0 0.3rem;">
            <strong style="color:#e6edf3;">{cluster['n_states']}</strong> estados
          </p>
          <p class="cl-states">{states_list}</p>
          <p class="cl-metrics">
            Dep: {cluster['mean_dependency']} · Div: {cluster['mean_diversification']}<br>
            Near: {cluster['mean_nearshoring']} · Hub: {cluster['mean_hub_score']}
          </p>
        </div>""", unsafe_allow_html=True)

st.markdown(
    "<p class='method-note' style='margin-top:1rem;'>IED Intelligence Platform · "
    "Secretaría de Economía · Análisis Estructural 2006–2025 · "
    "Datos en USD Millones corrientes · Cálculo propio</p>",
    unsafe_allow_html=True,
)