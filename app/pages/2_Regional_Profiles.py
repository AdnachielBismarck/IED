# =============================================================================
# PÁGINA 2 — PERFILES REGIONALES · IED Intelligence Platform
# RUTAS: IED/app/pages/ → .parent.parent.parent = IED/
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Regional Profiles · IED Mexico",
    layout="wide",
    page_icon="🗺️",
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
    font-size: 1.7rem;
    font-weight: 500;
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

  /* Síntesis ejecutiva — destacada */
  .synthesis-box {
    background: var(--bg-elevated);
    border: 1px solid var(--border);
    border-left: 4px solid var(--blue);
    border-radius: 8px;
    padding: 1.1rem 1.4rem;
    margin-bottom: 1.2rem;
  }
  .synthesis-box .synth-title {
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--blue);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin: 0 0 0.5rem;
  }
  .synthesis-box p {
    font-size: 0.92rem;
    color: var(--text-secondary);
    margin: 0;
    line-height: 1.7;
  }
  .synthesis-box strong { color: var(--text-primary); }

  /* Intro box */
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

  /* Filter box */
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
    scores   = _load("state_scores.parquet")
    clusters = _load("state_clusters.parquet")
    annual   = _load("annual_by_state.parquet")
    top_inv  = _load("top_investors_per_state.parquet")
    nodes    = _load("network_nodes.parquet")
    types_st = _load("types_by_state.parquet")
    return scores, clusters, annual, top_inv, nodes, types_st

scores_raw, clusters, annual, top_inv, nodes, types_st = load_data()

# Enriquecer scores con cluster y hub_score
scores = scores_raw.merge(
    clusters[["estado", "cluster_id", "cluster_name", "pca_x", "pca_y"]],
    on="estado", how="left",
)
state_nodes = (
    nodes[nodes["node_type"] == "state"]
    [["node", "hub_score", "community"]]
    .rename(columns={"node": "estado"})
)
scores = scores.merge(state_nodes, on="estado", how="left")

# ── Helpers de layout ─────────────────────────────────────────────────────────
# PLOT_LAYOUT sin xaxis/yaxis para evitar colisión de parámetros.
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

# ── Función de color semántico ─────────────────────────────────────────────────
def sem_color(val, invert=False):
    """Verde = bueno, rojo = malo. invert=True para métricas donde menor es mejor."""
    if pd.isna(val):
        return "#8b949e"
    v = (100 - val) if invert else val
    if v >= 70:
        return "#3fb950"
    elif v >= 40:
        return "#d29922"
    else:
        return "#f85149"

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
    "¿Cuál es la posición estratégica de cada estado y qué tan resiliente es su estructura de inversión?</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='font-size:0.9rem;color:#8b949e;margin-top:0;margin-bottom:1rem;'>"
    "Regional Profiles — Matriz estratégica · Perfil individual · Comparativa entre estados</p>",
    unsafe_allow_html=True,
)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_matrix, tab_profile, tab_compare = st.tabs([
    "Matriz Estratégica",
    "Perfil de Estado",
    "Comparativa",
])

# =============================================================================
# TAB 1 — MATRIZ ESTRATÉGICA
# =============================================================================
with tab_matrix:
    st.markdown("""<div class="intro-box"><p>
      Cada estado se posiciona según dos dimensiones estructurales:
      <strong>Diversificación</strong> (cuántos países distintos invierten en él) y
      <strong>Dependencia</strong> (qué fracción del flujo proviene de un solo origen).
      El tamaño del nodo refleja el <strong>Hub Score</strong> de red y el color indica
      la señal de <strong>nearshoring</strong>. Los cuadrantes delimitan cuatro perfiles
      de riesgo estratégico.
    </p></div>""", unsafe_allow_html=True)

    fig_m = px.scatter(
        scores.dropna(subset=["diversification_score", "dependency_score"]),
        x="dependency_score",
        y="diversification_score",
        size="hub_score",
        color="nearshoring_score",
        text="estado",
        template="plotly_dark",
        height=560,
        color_continuous_scale="Blues",
        labels={
            "dependency_score":    "Dependencia",
            "diversification_score": "Diversificación",
            "nearshoring_score":   "Nearshoring Score",
            "hub_score":           "Hub Score",
        },
    )

    med_dep = scores["dependency_score"].median()
    med_div = scores["diversification_score"].median()
    fig_m.add_hline(y=med_div, line_dash="dot", line_color="rgba(255,255,255,0.15)")
    fig_m.add_vline(x=med_dep, line_dash="dot", line_color="rgba(255,255,255,0.15)")

    # Cuadrantes sin emojis
    for txt, x, y in [
        ("Diversificado\nBaja dependencia",  8,  92),
        ("Diversificado\nAlta dependencia",  72, 92),
        ("Concentrado\nAlta dependencia",    72, 8),
        ("Concentrado\nBaja dependencia",    8,  8),
    ]:
        fig_m.add_annotation(
            x=x, y=y, text=txt, showarrow=False,
            font=dict(size=8, color="rgba(180,180,180,0.4)"),
            align="center",
        )

    fig_m.update_traces(textposition="top center", textfont_size=7)
    fig_m.update_layout(
        **PLOT_LAYOUT,
        title="Estados con alta diversificación y baja dependencia presentan mayor resiliencia estructural",
        xaxis=dict(**XAXIS_BASE, title="Dependencia (score)", tickfont=dict(size=10)),
        yaxis=dict(**YAXIS_BASE, title="Diversificación (score)", tickfont=dict(size=10)),
        coloraxis_colorbar=dict(title="Nearshoring", thickness=12, len=0.5),
        margin=dict(t=45, b=45, l=10, r=10),
    )
    st.plotly_chart(fig_m, use_container_width=True)
    st.markdown(
        "<p class='method-note'>Tamaño del nodo = Hub Score de red · Color = Nearshoring Score · "
        "Líneas punteadas = medianas del conjunto · "
        "Fuente: Secretaría de Economía · DGIE · Cálculo propio</p>",
        unsafe_allow_html=True,
    )

# =============================================================================
# TAB 2 — PERFIL DE ESTADO
# =============================================================================
with tab_profile:

    # ── Selector dentro de la página ──────────────────────────────────────────
    st.markdown("<div class='filter-box'>", unsafe_allow_html=True)
    all_states = sorted(scores["estado"].unique())
    default    = "Ciudad de México" if "Ciudad de México" in all_states else all_states[0]
    selected   = st.selectbox(
        "Selecciona un estado",
        all_states,
        index=all_states.index(default),
        key="state_selector",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    sd = scores[scores["estado"] == selected].iloc[0]

    dep    = float(sd.get("dependency_score",    0) or 0)
    div    = float(sd.get("diversification_score", 0) or 0)
    ns     = float(sd.get("nearshoring_score",   0) or 0)
    stab   = float(sd.get("stability_index",     0) or 0)
    hub    = float(sd.get("hub_score",           0) or 0)
    strat  = float(sd.get("strategic_score",     0) or 0)
    obs    = float(sd.get("observability_risk",  0) or 0)
    top_c  = sd.get("top_country", None)
    top_sh = float(sd.get("top_country_share",   0) or 0)

    dep_label = "ALTO"     if dep > 60 else ("MODERADO" if dep > 35 else "BAJO")
    dep_color = "#f85149"  if dep > 60 else ("#d29922"  if dep > 35 else "#3fb950")
    ns_texto  = (
        f"Señal de nearshoring <strong>significativa</strong> ({ns:.0f}/100), con aceleración post-2021."
        if ns > 25
        else f"Señal de nearshoring moderada ({ns:.0f}/100)."
    )
    top_c_texto = (
        f"País inversor principal: <strong>{top_c}</strong> con el {top_sh:.0f}% del flujo total."
        if top_c else ""
    )

    # ── SÍNTESIS EJECUTIVA — posición prominente ───────────────────────────────
    st.markdown(f"""
    <div class="synthesis-box">
      <p class="synth-title">Síntesis ejecutiva — {selected}</p>
      <p>
        <strong>{selected}</strong> presenta una diversificación de
        <strong>{div:.0f}/100</strong> y un nivel de dependencia
        <span style="color:{dep_color};font-weight:600;">{dep_label}</span>
        ({dep:.0f}/100). {top_c_texto} {ns_texto}
        Score estratégico global: <strong>{strat:.0f}/100</strong>.
      </p>
    </div>""", unsafe_allow_html=True)

    # ── KPIs del estado ────────────────────────────────────────────────────────
    k1, k2, k3, k4, k5 = st.columns(5)
    kpi_items = [
        (k1, strat, "Score Estratégico",  False),
        (k2, div,   "Diversificación",    False),
        (k3, dep,   "Dependencia",        True),
        (k4, ns,    "Nearshoring",        False),
        (k5, hub,   "Hub Score",          False),
    ]
    for col_k, val, label, inv in kpi_items:
        c = sem_color(val, invert=inv)
        with col_k:
            st.markdown(f"""<div class="kpi-card" style="border-top-color:{c};">
              <p class="kpi-val" style="color:{c};">{val:.0f}</p>
              <p class="kpi-label">{label}</p>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)

    # ── Gráficas del perfil ────────────────────────────────────────────────────
    col_l, col_r = st.columns(2)

    with col_l:
        # Evolución anual — barras (regla de granularidad)
        state_ann = annual[annual["Entidad federativa"] == selected].sort_values("Year")
        fig_ev = go.Figure()
        fig_ev.add_trace(go.Bar(
            x=state_ann["Year"], y=state_ann["IED"],
            marker_color="#58a6ff", marker_line_width=0, opacity=0.85,
            name="IED Anual",
        ))
        if len(state_ann) > 1:
            fig_ev.add_vrect(
                x0=2020.5, x1=state_ann["Year"].max() + 0.5,
                fillcolor="rgba(63,185,80,0.04)", line_width=0,
                annotation_text="Post-COVID",
                annotation_position="top left",
                annotation_font=dict(color="#3fb950", size=8),
            )
        fig_ev.update_layout(
            **PLOT_LAYOUT,
            title=f"IED anual — {selected}",
            height=280,
            xaxis=dict(**XAXIS_BASE, title="Año", tickfont=dict(size=9), dtick=2),
            yaxis=dict(**YAXIS_BASE, title="IED (USD M)", tickfont=dict(size=9)),
            margin=dict(t=40, b=40, l=10, r=10),
            showlegend=False,
        )
        st.plotly_chart(fig_ev, use_container_width=True)

        # Top países inversores
        top_inv_state = top_inv[top_inv["Estado"] == selected].nlargest(10, "IED")
        if len(top_inv_state) > 0:
            fig_inv = px.bar(
                top_inv_state,
                x="IED", y="País_origen", orientation="h",
                template="plotly_dark", height=280,
                color="IED", color_continuous_scale="Blues",
                labels={"IED": "IED (USD M)", "País_origen": ""},
            )
            fig_inv.update_layout(
                **PLOT_LAYOUT,
                title=f"Países de origen — {selected} (2023–2024)",
                xaxis=dict(**XAXIS_BASE, title="IED (USD M)", tickfont=dict(size=9)),
                yaxis=dict(**YAXIS_BASE, title="", tickfont=dict(size=9)),
                margin=dict(t=40, b=20, l=10, r=10),
                showlegend=False,
                coloraxis_showscale=False,
            )
            st.plotly_chart(fig_inv, use_container_width=True)
        else:
            st.markdown(
                "<p style='font-size:0.82rem;color:#484f58;margin-top:0.5rem;'>"
                "Sin datos de países inversores disponibles para este estado en 2023–2024.</p>",
                unsafe_allow_html=True,
            )

    with col_r:
        # Radar de perfil
        cat_labels = [
            "Diversificación", "Estabilidad", "Nearshoring",
            "Hub Score", "Anti-Dependencia", "Observabilidad",
        ]
        raw_vals = [
            div,
            stab,
            min(100, ns * 2),
            min(100, hub * 2),
            100 - dep,
            100 - obs,
        ]
        fig_r = go.Figure()
        fig_r.add_trace(go.Scatterpolar(
            r=raw_vals + [raw_vals[0]],
            theta=cat_labels + [cat_labels[0]],
            fill="toself",
            fillcolor="rgba(88,166,255,0.15)",
            line=dict(color="#58a6ff", width=2),
            name=selected,
        ))
        fig_r.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], gridcolor="#21262d", tickfont=dict(size=8)),
                angularaxis=dict(gridcolor="#21262d"),
                bgcolor="#161b22",
            ),
            showlegend=False,
            template="plotly_dark",
            paper_bgcolor="#161b22",
            font=dict(family="IBM Plex Sans, sans-serif", color="#8b949e", size=10),
            title=f"Perfil estructural — {selected}",
            title_font=dict(family="IBM Plex Sans, sans-serif", color="#e6edf3", size=13),
            height=320,
            margin=dict(t=45, b=20, l=30, r=30),
        )
        st.plotly_chart(fig_r, use_container_width=True)

        # Composición por tipo de inversión
        excl = ["Total general", "Total general por estado"]
        tss  = types_st[
            (types_st["Estado"] == selected) &
            (~types_st["Tipo de Inversión"].isin(excl)) &
            (types_st["IED"].notna())
        ]
        if len(tss) > 0:
            tr = tss[tss["Year"] >= 2020].groupby("Tipo de Inversión")["IED"].mean().reset_index()
            if len(tr) > 0:
                fig_tp = px.pie(
                    tr, values="IED", names="Tipo de Inversión",
                    template="plotly_dark", hole=0.4, height=280,
                    color_discrete_sequence=["#58a6ff", "#3fb950", "#d29922"],
                )
                fig_tp.update_layout(
                    **PLOT_LAYOUT,
                    title=f"Composición por tipo — {selected} (prom. 2020–2024)",
                    legend=dict(**LEGEND_V, font=dict(size=9)),
                    margin=dict(t=40, b=20, l=10, r=10),
                )
                st.plotly_chart(fig_tp, use_container_width=True)

    st.markdown(
        "<p class='method-note'>IED anual = suma de los 4 trimestres del año · "
        "Top inversores: acumulado 2023–2024 · "
        "Radar: Anti-Dependencia = 100 − Dependencia · Observabilidad = 100 − Riesgo de opacidad · "
        "Fuente: Secretaría de Economía · DGIE</p>",
        unsafe_allow_html=True,
    )

# =============================================================================
# TAB 3 — COMPARATIVA
# =============================================================================
with tab_compare:
    st.markdown("""<div class="intro-box"><p>
      Selecciona un estado base y hasta cuatro estados adicionales para comparar
      sus indicadores estructurales. La comparación permite identificar brechas
      en diversificación, dependencia y señal de nearshoring entre entidades.
    </p></div>""", unsafe_allow_html=True)

    # ── Selectores dentro de la página ────────────────────────────────────────
    st.markdown("<div class='filter-box'>", unsafe_allow_html=True)
    cmp1, cmp2 = st.columns([1, 2])
    with cmp1:
        all_states_cmp = sorted(scores["estado"].unique())
        default_cmp    = "Ciudad de México" if "Ciudad de México" in all_states_cmp else all_states_cmp[0]
        selected_cmp   = st.selectbox(
            "Estado base",
            all_states_cmp,
            index=all_states_cmp.index(default_cmp),
            key="cmp_base",
        )
    with cmp2:
        compare_states = st.multiselect(
            "Comparar con (hasta 4 estados)",
            [s for s in all_states_cmp if s != selected_cmp],
            max_selections=4,
            key="cmp_others",
        )
    st.markdown("</div>", unsafe_allow_html=True)

    states_cmp = [selected_cmp] + compare_states
    comp       = scores[scores["estado"].isin(states_cmp)]

    if len(comp) < 2:
        st.info("Selecciona al menos un estado adicional para activar la comparativa.")
    else:
        sc_cols = [
            "diversification_score", "dependency_score", "stability_index",
            "nearshoring_score", "hub_score", "strategic_score",
        ]
        lb_cols = [
            "Diversificación", "Dependencia", "Estabilidad",
            "Nearshoring", "Hub Score", "Score Estratégico",
        ]
        palette = ["#58a6ff", "#3fb950", "#d29922", "#bc8cff", "#f85149"]

        fig_cmp = go.Figure()
        for i, (_, row) in enumerate(comp.iterrows()):
            fig_cmp.add_trace(go.Bar(
                name=row["estado"],
                x=lb_cols,
                y=[float(row.get(c, 0) or 0) for c in sc_cols],
                marker_color=palette[i % len(palette)],
                marker_line_width=0,
            ))
        fig_cmp.update_layout(
            **PLOT_LAYOUT,
            title="Comparativa de indicadores estructurales entre estados seleccionados",
            barmode="group",
            height=420,
            xaxis=dict(**XAXIS_BASE, title="", tickfont=dict(size=10)),
            yaxis=dict(**YAXIS_BASE, title="Score (0–100)", tickfont=dict(size=10)),
            legend=dict(**LEGEND_H),
            margin=dict(t=45, b=60, l=10, r=10),
        )
        st.plotly_chart(fig_cmp, use_container_width=True)

        # Tabla resumen
        tabla = (
            comp[["estado"] + sc_cols]
            .rename(columns={"estado": "Estado", **dict(zip(sc_cols, lb_cols))})
            .round(1)
            .reset_index(drop=True)
        )
        st.dataframe(tabla, use_container_width=True, hide_index=True)

        st.markdown(
            "<p class='method-note'>Todos los indicadores en escala 0–100 · "
            "Dependencia: mayor valor = mayor concentración en un solo origen · "
            "Fuente: Secretaría de Economía · DGIE · Cálculo propio</p>",
            unsafe_allow_html=True,
        )