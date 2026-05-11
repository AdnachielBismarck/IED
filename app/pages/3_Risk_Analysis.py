# =============================================================================
# PÁGINA 3 — RISK & DEPENDENCY · IED Intelligence Platform
# RUTAS: IED/app/pages/ → .parent.parent.parent = IED/
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Risk Analysis · IED Mexico",
    layout="wide",
    page_icon="⚠️",
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

  .kpi-card {
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1rem 1.2rem;
    border-top: 2px solid var(--red);
    text-align: center;
  }
  .kpi-card.amber { border-top-color: var(--amber); }
  .kpi-card.green { border-top-color: var(--green); }
  .kpi-card.blue  { border-top-color: var(--blue);  }
  .kpi-card .kpi-val {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.7rem;
    font-weight: 500;
    color: var(--red);
    margin: 0;
    line-height: 1.2;
  }
  .kpi-card.amber .kpi-val { color: var(--amber); }
  .kpi-card.green .kpi-val { color: var(--green); }
  .kpi-card.blue  .kpi-val { color: var(--blue);  }
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

  .intro-box {
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: 8px;
    padding: 0.9rem 1.2rem;
    margin-bottom: 1rem;
  }
  .intro-box p {
    font-size: 0.88rem;
    color: var(--text-secondary);
    margin: 0;
    line-height: 1.6;
  }
  .intro-box strong { color: var(--text-primary); }

  .risk-types {
    display: flex;
    gap: 0.8rem;
    margin-bottom: 1rem;
    flex-wrap: wrap;
  }
  .risk-type-item {
    background: var(--bg-elevated);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.7rem 1rem;
    flex: 1;
    min-width: 180px;
  }
  .risk-type-item .rt-title {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin: 0 0 0.3rem;
  }
  .risk-type-item p {
    font-size: 0.80rem;
    color: var(--text-secondary);
    margin: 0;
    line-height: 1.5;
  }

  .insight-box {
    background: var(--bg-elevated);
    border: 1px solid var(--border);
    border-left: 3px solid var(--red);
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin-top: 0.8rem;
  }
  .insight-box.amber { border-left-color: var(--amber); }
  .insight-box .insight-title {
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--red);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin: 0 0 0.4rem;
  }
  .insight-box.amber .insight-title { color: var(--amber); }
  .insight-box p {
    font-size: 0.88rem;
    color: var(--text-secondary);
    margin: 0;
    line-height: 1.6;
  }
  .insight-box strong { color: var(--text-primary); }

  .method-note {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    color: var(--text-muted);
    border-top: 1px solid var(--border-subtle);
    padding-top: 0.4rem;
    margin-top: 0.6rem;
  }

  .ranking-label {
    font-size: 0.82rem;
    font-weight: 600;
    color: var(--text-primary);
    margin: 1rem 0 0.4rem;
    padding-bottom: 0.3rem;
    border-bottom: 1px solid var(--border-subtle);
  }
</style>
""", unsafe_allow_html=True)

# ── Rutas ─────────────────────────────────────────────────────────────────────
BASE = Path(__file__).resolve().parent.parent.parent
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
def load_data():
    return (
        _load("state_scores.parquet"),
        _load("country_profiles.parquet"),
        _load("country_by_state.parquet"),
        _load("investment_by_state.parquet"),
    )

scores, ctry_p, cs_raw, states = load_data()

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
    "¿Qué estados y relaciones representan vulnerabilidades estructurales ante shocks externos?</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='font-size:0.9rem;color:#8b949e;margin-top:0;margin-bottom:1rem;'>"
    "Risk & Dependency — Concentración de origen · Opacidad de datos · Estabilidad histórica</p>",
    unsafe_allow_html=True,
)

# ── Introducción: tres tipos de riesgo ────────────────────────────────────────
st.markdown("""
<div class="risk-types">
  <div class="risk-type-item" style="border-top:2px solid #f85149;">
    <p class="rt-title" style="color:#f85149;">Riesgo de Dependencia</p>
    <p>Un solo país de origen concentra una fracción dominante del flujo.
    Un shock en ese país (político, económico, cambiario) puede contraer
    la IED del estado receptor de forma abrupta.</p>
  </div>
  <div class="risk-type-item" style="border-top:2px solid #d29922;">
    <p class="rt-title" style="color:#d29922;">Riesgo de Observabilidad</p>
    <p>Alta proporción de registros con valor confidencial ("C") en los datos de la SE.
    Limita la capacidad de análisis y puede ocultar concentraciones reales.
    No implica necesariamente mayor vulnerabilidad económica.</p>
  </div>
  <div class="risk-type-item" style="border-top:2px solid #8b949e;">
    <p class="rt-title" style="color:#8b949e;">Riesgo de Estabilidad</p>
    <p>Alta volatilidad histórica en los flujos trimestrales del estado.
    Estados con baja estabilidad presentan ciclos irregulares que dificultan
    la planificación de infraestructura y política de atracción.</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
with k1:
    n = int((scores["dependency_score"] > 60).sum())
    st.markdown(f"""<div class="kpi-card">
      <p class="kpi-val">{n}</p>
      <p class="kpi-label">Alta dependencia</p>
      <p class="kpi-sub">Dependency score &gt; 60</p>
    </div>""", unsafe_allow_html=True)
with k2:
    n = int((scores["observability_risk"] > 50).sum())
    st.markdown(f"""<div class="kpi-card amber">
      <p class="kpi-val">{n}</p>
      <p class="kpi-label">Alta opacidad</p>
      <p class="kpi-sub">Observability risk &gt; 50%</p>
    </div>""", unsafe_allow_html=True)
with k3:
    n = int((scores["stability_index"] < 30).sum())
    st.markdown(f"""<div class="kpi-card amber">
      <p class="kpi-val">{n}</p>
      <p class="kpi-label">Baja estabilidad</p>
      <p class="kpi-sub">Stability index &lt; 30</p>
    </div>""", unsafe_allow_html=True)
with k4:
    n = int((scores["nearshoring_score"] > 30).sum())
    st.markdown(f"""<div class="kpi-card blue">
      <p class="kpi-val">{n}</p>
      <p class="kpi-label">Señal nearshoring</p>
      <p class="kpi-sub">Nearshoring score &gt; 30</p>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='margin-top:1.2rem;'></div>", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["Mapa de Riesgo", "Dependencia por País", "Rankings"])

# =============================================================================
# TAB 1 — MAPA DE RIESGO
# =============================================================================
with tab1:
    st.markdown("""<div class="intro-box"><p>
      Cada estado se posiciona según su <strong>Dependencia</strong> (concentración en un origen)
      y su <strong>Opacidad</strong> (proporción de registros confidenciales).
      El tamaño del nodo refleja el <strong>Stability Index</strong> — estados más grandes
      tienen flujos más predecibles. El color indica el Score Estratégico global.
      Los estados en el cuadrante superior derecho concentran los tres tipos de riesgo simultáneamente.
    </p></div>""", unsafe_allow_html=True)

    col_a, col_b = st.columns([2, 1])

    with col_a:
        fig_r = px.scatter(
            scores.dropna(subset=["dependency_score", "observability_risk"]),
            x="dependency_score",
            y="observability_risk",
            size="stability_index",
            color="strategic_score",
            text="estado",
            template="plotly_dark",
            height=500,
            color_continuous_scale="RdYlGn",
            labels={
                "dependency_score":    "Dependencia",
                "observability_risk":  "Opacidad (%)",
                "strategic_score":     "Score Estratégico",
                "stability_index":     "Estabilidad",
            },
        )
        fig_r.add_hrect(y0=50, y1=100, fillcolor="rgba(248,81,73,0.04)", line_width=0)
        fig_r.add_vrect(x0=60, x1=100, fillcolor="rgba(248,81,73,0.04)", line_width=0)
        fig_r.add_annotation(
            x=78, y=78, text="Zona de riesgo alto",
            showarrow=False, font=dict(size=9, color="rgba(248,81,73,0.55)"),
        )
        fig_r.add_annotation(
            x=15, y=15, text="Zona de menor riesgo",
            showarrow=False, font=dict(size=9, color="rgba(63,185,80,0.55)"),
        )
        fig_r.update_traces(textposition="top center", textfont_size=7)
        fig_r.update_layout(
            **PLOT_LAYOUT,
            title="Estados en el cuadrante superior derecho acumulan dependencia y opacidad simultáneamente",
            height=500,
            xaxis=dict(**XAXIS_BASE, title="Dependencia (score)", tickfont=dict(size=10)),
            yaxis=dict(**YAXIS_BASE, title="Opacidad — % registros confidenciales", tickfont=dict(size=10)),
            coloraxis_colorbar=dict(title="Score\nEstratégico", thickness=12, len=0.5),
            margin=MARGIN_STD,
        )
        st.plotly_chart(fig_r, use_container_width=True)

        # Identificar el patrón más preocupante
        alto_riesgo = scores[
            (scores["dependency_score"] > 60) & (scores["observability_risk"] > 50)
        ]["estado"].tolist()
        if alto_riesgo:
            st.markdown(f"""<div class="insight-box">
              <p class="insight-title">Patrón de mayor preocupación</p>
              <p><strong>{", ".join(alto_riesgo)}</strong> presentan simultáneamente
              alta dependencia de un solo origen <em>y</em> alta opacidad de datos,
              lo que combina vulnerabilidad estructural con limitada capacidad de monitoreo.
              Son los estados que requieren atención prioritaria en política de diversificación.</p>
            </div>""", unsafe_allow_html=True)

        st.markdown(
            "<p class='method-note'>Tamaño = Stability Index (mayor = más predecible) · "
            "Color = Score Estratégico (verde = mayor score) · "
            "Líneas punteadas = umbrales de riesgo alto (Dependencia &gt; 60, Opacidad &gt; 50%) · "
            "Fuente: Secretaría de Economía · DGIE</p>",
            unsafe_allow_html=True,
        )

    with col_b:
        # Clasificación de riesgo
        st.markdown(
            "<p style='font-size:0.85rem;font-weight:600;color:#e6edf3;margin-bottom:0.5rem;'>"
            "Clasificación por nivel de riesgo</p>",
            unsafe_allow_html=True,
        )
        rt = scores[["estado", "dependency_score", "observability_risk", "strategic_score"]].copy()
        rt["Riesgo"] = rt.apply(
            lambda r: "Alto" if (r["dependency_score"] > 60 or r["observability_risk"] > 50)
            else ("Medio" if (r["dependency_score"] > 35 or r["observability_risk"] > 30)
            else "Bajo"),
            axis=1,
        )
        tabla_r = (
            rt.sort_values("dependency_score", ascending=False)
            [["estado", "Riesgo", "dependency_score", "observability_risk"]]
            .rename(columns={
                "estado":             "Estado",
                "dependency_score":   "Dependencia",
                "observability_risk": "Opacidad %",
            })
            .round(1)
        )
        st.dataframe(tabla_r, use_container_width=True, hide_index=True, height=440)

# =============================================================================
# TAB 2 — DEPENDENCIA POR PAÍS
# =============================================================================
with tab2:
    st.markdown("""<div class="intro-box"><p>
      Analiza la concentración territorial de cada país inversor: cuántos estados activa,
      qué volumen total acumula y cómo se distribuye geográficamente su inversión.
      Un país con alto HHI concentra su inversión en pocos estados, creando dependencia bilateral.
    </p></div>""", unsafe_allow_html=True)

    top_inv_c = ctry_p.nlargest(20, "total_ied")

    # Barras horizontales — Top 20 países por IED acumulada
    fig_c = px.bar(
        top_inv_c.sort_values("total_ied"),
        x="total_ied", y="country", orientation="h",
        template="plotly_dark", height=520,
        color="concentration_hhi",
        color_continuous_scale="RdYlGn_r",
        labels={
            "total_ied":          "IED Total (USD M)",
            "country":            "",
            "concentration_hhi":  "Concentración HHI",
        },
    )
    fig_c.update_layout(
        **PLOT_LAYOUT,
        title="Los países con mayor volumen no siempre tienen la mayor concentración territorial",
        xaxis=dict(**XAXIS_BASE, title="IED Acumulada (USD Millones)", tickfont=dict(size=10)),
        yaxis=dict(**YAXIS_BASE, title="", tickfont=dict(size=10)),
        coloraxis_colorbar=dict(title="HHI", thickness=12, len=0.5),
        margin=dict(t=45, b=30, l=10, r=10),
    )
    st.plotly_chart(fig_c, use_container_width=True)
    st.markdown(
        "<p class='method-note'>HHI (Herfindahl-Hirschman Index): mide concentración geográfica · "
        "HHI cercano a 1 = inversión concentrada en pocos estados · "
        "HHI cercano a 0 = inversión distribuida ampliamente · "
        "Fuente: Secretaría de Economía · DGIE · Cálculo propio</p>",
        unsafe_allow_html=True,
    )

    st.markdown("<div style='margin-top:1.2rem;'></div>", unsafe_allow_html=True)

    # Barras de Dependency Score por estado
    st.markdown(
        "<h3 style='font-size:1.05rem;color:#e6edf3;margin-bottom:0.3rem;'>"
        "Dependencia estructural por estado</h3>",
        unsafe_allow_html=True,
    )
    dep_s    = scores.sort_values("dependency_score", ascending=False)
    cols_dep = [
        "#f85149" if v > 60 else ("#d29922" if v > 35 else "#3fb950")
        for v in dep_s["dependency_score"].fillna(0)
    ]

    fig_dep = go.Figure()
    fig_dep.add_trace(go.Bar(
        x=dep_s["estado"],
        y=dep_s["dependency_score"].fillna(0),
        marker_color=cols_dep,
        marker_line_width=0,
        text=[f"{v:.0f}" for v in dep_s["dependency_score"].fillna(0)],
        textposition="outside",
        textfont=dict(size=7, color="#8b949e"),
    ))
    fig_dep.add_hline(
        y=60, line_dash="dot", line_color="rgba(248,81,73,0.5)",
        annotation_text="Umbral alto (60)",
        annotation_position="top right",
        annotation_font=dict(size=8, color="rgba(248,81,73,0.7)"),
    )
    fig_dep.add_hline(
        y=35, line_dash="dot", line_color="rgba(210,153,34,0.5)",
        annotation_text="Umbral medio (35)",
        annotation_position="top right",
        annotation_font=dict(size=8, color="rgba(210,153,34,0.7)"),
    )
    fig_dep.update_layout(
        **PLOT_LAYOUT,
        title="Rojo: dependencia alta (>60) · Ámbar: moderada (35–60) · Verde: baja (<35)",
        height=420,
        xaxis=dict(**XAXIS_BASE, title="", tickangle=45, tickfont=dict(size=7)),
        yaxis=dict(**YAXIS_BASE, title="Dependency Score", tickfont=dict(size=10)),
        margin=dict(t=45, b=100, l=10, r=80),
        showlegend=False,
    )
    st.plotly_chart(fig_dep, use_container_width=True)

    d1, d2 = st.columns(2)
    with d1:
        fig_stab = px.bar(
            scores.sort_values("stability_index"),
            x="stability_index", y="estado", orientation="h",
            template="plotly_dark", height=480,
            color="stability_index",
            color_continuous_scale="RdYlGn",
            labels={"stability_index": "Stability Index", "estado": ""},
        )
        fig_stab.update_layout(
            **PLOT_LAYOUT,
            title="Estados con mayor estabilidad histórica de flujos",
            xaxis=dict(**XAXIS_BASE, title="Stability Index", tickfont=dict(size=10)),
            yaxis=dict(**YAXIS_BASE, title="", tickfont=dict(size=9)),
            coloraxis_showscale=False,
            margin=dict(t=45, b=20, l=10, r=10),
        )
        st.plotly_chart(fig_stab, use_container_width=True)

    with d2:
        fig_obs = px.bar(
            scores.sort_values("observability_risk", ascending=False),
            x="estado", y="observability_risk",
            template="plotly_dark", height=480,
            color="observability_risk",
            color_continuous_scale="YlOrRd",
            labels={"observability_risk": "Observability Risk (%)", "estado": ""},
        )
        fig_obs.update_layout(
            **PLOT_LAYOUT,
            title="Alta opacidad no implica mayor riesgo — puede reflejar sectores estratégicos",
            xaxis=dict(**XAXIS_BASE, title="", tickangle=45, tickfont=dict(size=7)),
            yaxis=dict(**YAXIS_BASE, title="Registros confidenciales (%)", tickfont=dict(size=10)),
            coloraxis_showscale=False,
            margin=dict(t=45, b=110, l=10, r=10),
        )
        st.plotly_chart(fig_obs, use_container_width=True)

    st.markdown("""<div class="insight-box amber">
      <p class="insight-title">Nota metodológica — Observability Risk</p>
      <p>Una alta proporción de registros confidenciales no implica necesariamente mayor
      vulnerabilidad económica. En muchos casos refleja la presencia de
      <strong>inversiones de gran escala en sectores estratégicos</strong>
      (energía, defensa, tecnología) que la Secretaría de Economía clasifica como reservados.
      Los estados con alto Observability Risk deben interpretarse con cautela:
      su posición real podría ser mejor o peor que lo que los datos visibles sugieren.</p>
    </div>""", unsafe_allow_html=True)

    st.markdown(
        "<p class='method-note'>Observability Risk = proporción de registros con valor 'C' "
        "(confidencial) sobre el total de registros del estado · "
        "Stability Index = inverso del coeficiente de variación de la serie trimestral · "
        "Fuente: Secretaría de Economía · DGIE</p>",
        unsafe_allow_html=True,
    )

# =============================================================================
# TAB 3 — RANKINGS
# =============================================================================
with tab3:
    st.markdown("""<div class="intro-box"><p>
      Los rankings permiten identificar de forma rápida los extremos del sistema:
      los estados con mayor fortaleza estratégica, los que más se benefician del nearshoring
      y los que presentan las vulnerabilidades más pronunciadas.
    </p></div>""", unsafe_allow_html=True)

    rk1, rk2 = st.columns(2)

    with rk1:
        st.markdown(
            "<p class='ranking-label'>Top 10 — Mayor Score Estratégico</p>",
            unsafe_allow_html=True,
        )
        st.dataframe(
            scores.nlargest(10, "strategic_score")
            [["estado", "strategic_score", "diversification_score", "nearshoring_score"]]
            .rename(columns={
                "estado":                "Estado",
                "strategic_score":       "Score Estratégico",
                "diversification_score": "Diversificación",
                "nearshoring_score":     "Nearshoring",
            })
            .round(1),
            use_container_width=True, hide_index=True,
        )

        st.markdown(
            "<p class='ranking-label'>Top 10 — Señal de Nearshoring</p>",
            unsafe_allow_html=True,
        )
        ns_cols = ["estado", "nearshoring_score", "zone", "us_share_pct", "growth_ratio_2021_24"]
        ns_cols_exist = [c for c in ns_cols if c in scores.columns]
        st.dataframe(
            scores.nlargest(10, "nearshoring_score")
            [ns_cols_exist]
            .rename(columns={
                "estado":              "Estado",
                "nearshoring_score":   "Score NS",
                "zone":                "Zona",
                "us_share_pct":        "% EE.UU.",
                "growth_ratio_2021_24":"Crec. 21–24%",
            })
            .round(1),
            use_container_width=True, hide_index=True,
        )

    with rk2:
        st.markdown(
            "<p class='ranking-label'>Top 10 — Mayor Dependencia estructural</p>",
            unsafe_allow_html=True,
        )
        st.dataframe(
            scores.nlargest(10, "dependency_score")
            [["estado", "dependency_score", "top_country", "top_country_share"]]
            .rename(columns={
                "estado":             "Estado",
                "dependency_score":   "Dependencia",
                "top_country":        "País dominante",
                "top_country_share":  "% dominante",
            })
            .round(1),
            use_container_width=True, hide_index=True,
        )

        st.markdown(
            "<p class='ranking-label'>Top 10 — Mayor Opacidad de datos</p>",
            unsafe_allow_html=True,
        )
        obs_cols = ["estado", "observability_risk", "n_confidential_records", "n_total_records"]
        obs_cols_exist = [c for c in obs_cols if c in scores.columns]
        st.dataframe(
            scores.nlargest(10, "observability_risk")
            [obs_cols_exist]
            .rename(columns={
                "estado":                  "Estado",
                "observability_risk":      "Opacidad %",
                "n_confidential_records":  "Registros C",
                "n_total_records":         "Total",
            })
            .round(1),
            use_container_width=True, hide_index=True,
        )

    st.markdown(
        "<p class='method-note'>Todos los scores en escala 0–100 · "
        "Score Estratégico: índice compuesto de diversificación, estabilidad, nearshoring y hub score · "
        "Registros C: valor 'C' (confidencial) en datos originales de la SE · "
        "Fuente: Secretaría de Economía · DGIE · Cálculo propio</p>",
        unsafe_allow_html=True,
    )