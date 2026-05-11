# =============================================================================
# PÁGINA 4 — TEMPORAL DYNAMICS · IED Intelligence Platform
# RUTAS: IED/app/pages/ → .parent.parent.parent = IED/
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Temporal Dynamics · IED Mexico",
    layout="wide",
    page_icon="📈",
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
    border-top: 2px solid var(--blue);
  }
  .kpi-card .kpi-val {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.6rem;
    font-weight: 500;
    color: var(--blue);
    margin: 0;
    line-height: 1.2;
  }
  .kpi-card .kpi-val.amber { color: var(--amber); }
  .kpi-card .kpi-val.green { color: var(--green); }
  .kpi-card .kpi-val.red   { color: var(--red);   }
  .kpi-card .kpi-label {
    font-size: 0.72rem;
    color: var(--text-secondary);
    margin: 0.2rem 0 0;
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }
  .kpi-card .kpi-sub {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
    color: var(--text-muted);
    margin: 0;
  }

  .insight-box {
    background: var(--bg-elevated);
    border: 1px solid var(--border);
    border-left: 3px solid var(--amber);
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin-top: 0.8rem;
  }
  .insight-box .insight-title {
    font-size: 0.78rem;
    font-weight: 600;
    color: var(--amber);
    margin: 0 0 0.4rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
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

  .filter-box {
    background: var(--bg-elevated);
    border: 1px solid var(--border-subtle);
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin-bottom: 1rem;
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
        _load("investment_by_state.parquet"),
        _load("investment_by_country.parquet"),
        _load("investment_types.parquet"),
        _load("annual_by_state.parquet"),
        _load("state_scores.parquet"),
        _load("country_by_state.parquet"),
    )

states, countries, types, annual, scores, cs_raw = load_data()

# ── Helpers de layout ─────────────────────────────────────────────────────────
# PLOT_LAYOUT no incluye xaxis ni yaxis para evitar el error:
# "got multiple values for keyword argument 'xaxis'"
# Se pasan siempre de forma explícita en cada update_layout.
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


# ── Preparar serie trimestral ─────────────────────────────────────────────────
@st.cache_data
def preparar_series(df_states):
    nq = df_states.groupby("Fecha")["IED"].sum().reset_index()
    nq["Fecha"] = pd.to_datetime(nq["Fecha"])
    nq["Year"]  = nq["Fecha"].dt.year
    nq["Mes"]   = nq["Fecha"].dt.month
    nq["Q"]     = nq["Mes"].map({
        1:"Q1",2:"Q1",3:"Q1",
        4:"Q2",5:"Q2",6:"Q2",
        7:"Q3",8:"Q3",9:"Q3",
        10:"Q4",11:"Q4",12:"Q4",
    })
    nq["IED_4Q"] = nq["IED"].rolling(4).mean()
    return nq

nq = preparar_series(states)

# ── Métricas de cabecera ───────────────────────────────────────────────────────
annual_total = states.groupby("Year")["IED"].sum()
peak_year  = int(annual_total.idxmax())
peak_val   = float(annual_total.max())
recent_avg = float(annual_total[annual_total.index >= 2021].mean())
pre_avg    = float(annual_total[(annual_total.index >= 2015) & (annual_total.index <= 2019)].mean())
growth_pct = ((recent_avg - pre_avg) / abs(pre_avg) * 100) if pre_avg else 0

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
    "¿Qué cambió estructuralmente en los flujos de IED después de 2020?</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='font-size:0.9rem;color:#8b949e;margin-top:0;margin-bottom:1rem;'>"
    "Temporal Dynamics — Patrones de nearshoring · Composición por tipo · Flujos por país y estado</p>",
    unsafe_allow_html=True,
)

# ── KPIs ──────────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"""<div class="kpi-card">
      <p class="kpi-val">{peak_year}</p>
      <p class="kpi-label">Año de inversión máxima</p>
      <p class="kpi-sub">${peak_val:,.0f} M USD</p>
    </div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""<div class="kpi-card">
      <p class="kpi-val amber">${recent_avg:,.0f} M</p>
      <p class="kpi-label">Promedio anual 2021–2024</p>
      <p class="kpi-sub">Período post-COVID</p>
    </div>""", unsafe_allow_html=True)
with k3:
    st.markdown(f"""<div class="kpi-card">
      <p class="kpi-val" style="color:#8b949e;">${pre_avg:,.0f} M</p>
      <p class="kpi-label">Promedio anual 2015–2019</p>
      <p class="kpi-sub">Período pre-pandemia</p>
    </div>""", unsafe_allow_html=True)
with k4:
    color_cls = "green" if growth_pct > 0 else "red"
    st.markdown(f"""<div class="kpi-card">
      <p class="kpi-val {color_cls}">{growth_pct:+.1f}%</p>
      <p class="kpi-label">Variación estructural</p>
      <p class="kpi-sub">2021–2024 vs 2015–2019</p>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='margin-top:1.2rem;'></div>", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["Evolución Temporal", "Señal Nearshoring", "Dinámica por País"])

# =============================================================================
# TAB 1 — EVOLUCIÓN TEMPORAL
# =============================================================================
with tab1:
    st.markdown("""<div class="intro-box"><p>
      El año <strong>2020</strong> marca un punto de inflexión en la IED de México.
      La contracción por la pandemia fue seguida de una reactivación acelerada impulsada
      por la reconfiguración global de cadenas de suministro.
      <br><br>
      <strong>Nota sobre la serie trimestral:</strong> los datos de IED reportan flujos
      del período — no son acumulativos. Sumar o promediar trimestres distintos
      (Q1 con Q2, Q3, Q4) introduce sesgos estacionales propios del reporte.
      Por eso se ofrece un modo de <strong>comparación homogénea</strong>
      que muestra el mismo trimestre a través de los años (Q1 vs Q1, Q2 vs Q2, etc.).
    </p></div>""", unsafe_allow_html=True)

    # ── Filtro dentro de la página ─────────────────────────────────────────────
    st.markdown("<div class='filter-box'>", unsafe_allow_html=True)
    fcol1, fcol2 = st.columns([1, 3])
    with fcol1:
        modo_serie = st.radio(
            "Modo de visualización",
            ["Serie completa", "Comparar por trimestre"],
            index=0,
            key="modo_serie",
        )
    with fcol2:
        if modo_serie == "Comparar por trimestre":
            q_sel = st.selectbox(
                "Trimestre a comparar entre años",
                ["Q1 (Ene–Mar)", "Q2 (Abr–Jun)", "Q3 (Jul–Sep)", "Q4 (Oct–Dic)"],
                index=0,
                key="q_sel",
            )
            q_map = {
                "Q1 (Ene–Mar)": "Q1",
                "Q2 (Abr–Jun)": "Q2",
                "Q3 (Jul–Sep)": "Q3",
                "Q4 (Oct–Dic)": "Q4",
            }
            q_filtro = q_map[q_sel]
        else:
            q_filtro  = None
            st.caption("Muestra todos los trimestres como serie continua con media móvil de 4 períodos.")
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Gráfica según modo ─────────────────────────────────────────────────────
    if modo_serie == "Serie completa":
        fig_n = go.Figure()
        fig_n.add_trace(go.Bar(
            x=nq["Fecha"], y=nq["IED"],
            name="IED Trimestral (USD M)",
            marker_color="#58a6ff", marker_line_width=0, opacity=0.75,
        ))
        fig_n.add_trace(go.Scatter(
            x=nq["Fecha"], y=nq["IED_4Q"],
            name="Media móvil 4 trimestres",
            line=dict(color="#d29922", width=2.5),
        ))
        y_max = nq["IED"].max()
        for date, label, color in [
            ("2008-09-01", "Crisis Financiera", "#f85149"),
            ("2018-10-01", "T-MEC Firma",       "#58a6ff"),
            ("2020-04-01", "COVID-19",           "#f85149"),
            ("2022-01-01", "Aceleración NS",     "#3fb950"),
        ]:
            fig_n.add_vline(x=date, line_dash="dot", opacity=0.35, line_color=color)
            fig_n.add_annotation(
                x=date, y=y_max * 0.88, text=label,
                showarrow=False, font=dict(size=8, color=color),
                textangle=-90, xanchor="left",
            )
        fig_n.update_layout(
            **PLOT_LAYOUT,
            title="IED trimestral 2006–2025: la media móvil revela la tendencia estructural",
            height=400,
            xaxis=dict(**XAXIS_BASE, title="Trimestre", tickfont=dict(size=10)),
            yaxis=dict(**YAXIS_BASE, title="IED (USD Millones)", tickfont=dict(size=10)),
            legend=LEGEND_H,
            margin=MARGIN_STD,
        )
        st.plotly_chart(fig_n, use_container_width=True)
        st.markdown(
            "<p class='method-note'>Serie completa 2006–Q2 2025 · Cada barra = un trimestre · "
            "La media móvil de 4 trimestres suaviza la estacionalidad del reporte · "
            "Fuente: Secretaría de Economía · DGIE</p>",
            unsafe_allow_html=True,
        )

    else:
        # Comparación homogénea: mismo trimestre, todos los años
        nq_q = nq[nq["Q"] == q_filtro].copy().sort_values("Year")
        delta = nq_q["IED"].pct_change() * 100
        colors_bar = [
            "#3fb950" if (pd.isna(v) or v >= 0) else "#f85149"
            for v in delta
        ]
        avg_pre  = nq_q[nq_q["Year"].between(2015, 2019)]["IED"].mean()
        avg_post = nq_q[nq_q["Year"] >= 2021]["IED"].mean()

        fig_q = go.Figure()
        fig_q.add_trace(go.Bar(
            x=nq_q["Year"], y=nq_q["IED"],
            name=f"IED {q_filtro}",
            marker_color=colors_bar, marker_line_width=0,
            text=[f"${v:,.0f}" for v in nq_q["IED"]],
            textposition="outside",
            textfont=dict(size=8, color="#8b949e"),
        ))
        if pd.notna(avg_pre):
            fig_q.add_hline(
                y=avg_pre, line_dash="dot", line_color="#484f58",
                annotation_text=f"Prom 2015–19: ${avg_pre:,.0f}M",
                annotation_position="top left",
                annotation_font=dict(size=8, color="#484f58"),
            )
        if pd.notna(avg_post):
            fig_q.add_hline(
                y=avg_post, line_dash="dot", line_color="#d29922",
                annotation_text=f"Prom 2021–24: ${avg_post:,.0f}M",
                annotation_position="top right",
                annotation_font=dict(size=8, color="#d29922"),
            )
        fig_q.update_layout(
            **PLOT_LAYOUT,
            title=f"Comparación inter-anual homogénea — {q_filtro} de cada año",
            height=400,
            xaxis=dict(**XAXIS_BASE, title="Año", dtick=1, tickfont=dict(size=10)),
            yaxis=dict(**YAXIS_BASE, title="IED (USD Millones)", tickfont=dict(size=10)),
            legend=LEGEND_H,
            margin=MARGIN_STD,
        )
        st.plotly_chart(fig_q, use_container_width=True)

        if pd.notna(avg_pre) and pd.notna(avg_post):
            delta_pct = (avg_post - avg_pre) / abs(avg_pre) * 100
            dir_str   = "superior" if delta_pct > 0 else "inferior"
            st.markdown(f"""<div class="insight-box">
              <p class="insight-title">Comparación {q_filtro} — Pre vs Post COVID</p>
              <p>El promedio de <strong>{q_filtro}</strong> en 2021–2024 es
              <strong>{abs(delta_pct):.1f}% {dir_str}</strong> al de 2015–2019
              (${avg_post:,.0f} M vs ${avg_pre:,.0f} M).
              Comparar el mismo trimestre entre años elimina los sesgos de
              estacionalidad del reporte de la Secretaría de Economía.</p>
            </div>""", unsafe_allow_html=True)

        st.markdown(
            f"<p class='method-note'>Comparación inter-anual de {q_filtro} · "
            "Verde = crecimiento respecto al año anterior · Rojo = caída · "
            "Fuente: Secretaría de Economía · DGIE</p>",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-top:1.2rem;'></div>", unsafe_allow_html=True)

    # ── Composición por tipo de inversión (anual) ──────────────────────────────
    ta = types.groupby(["Year", "Tipo de Inversión"])["IED"].sum().reset_index()
    fig_ta = px.bar(
        ta, x="Year", y="IED", color="Tipo de Inversión",
        template="plotly_dark", height=320, barmode="stack",
        color_discrete_sequence=["#58a6ff", "#3fb950", "#d29922"],
        labels={"IED": "IED (USD Millones)", "Year": "Año"},
    )
    fig_ta.update_layout(
        **PLOT_LAYOUT,
        title="La reinversión de utilidades gana peso relativo en el período reciente",
        xaxis=dict(**XAXIS_BASE, title="Año", tickfont=dict(size=10)),
        yaxis=dict(**YAXIS_BASE, title="IED (USD Millones)", tickfont=dict(size=10)),
        legend=dict(**LEGEND_H),
        margin=MARGIN_STD,
    )
    st.plotly_chart(fig_ta, use_container_width=True)
    st.markdown(
        "<p class='method-note'>Fuente: Secretaría de Economía · DGIE · "
        "Clasificación: Nuevas inversiones, Reinversión de utilidades, "
        "Cuentas entre compañías · Agregado anual.</p>",
        unsafe_allow_html=True,
    )

# =============================================================================
# TAB 2 — SEÑAL NEARSHORING
# =============================================================================
with tab2:
    # Sankey al inicio — visualización más impactante
    st.markdown(
        "<h3 style='font-size:1.05rem;color:#e6edf3;margin-bottom:0.3rem;'>"
        "¿Hacia dónde fluye la inversión de cada país? (2022–2024)</h3>",
        unsafe_allow_html=True,
    )
    st.markdown("""<div class="intro-box"><p>
      El diagrama muestra los flujos acumulados entre los
      <strong>8 países de origen con mayor volumen</strong> y los
      <strong>12 estados receptores más activos</strong> en el período 2022–2024.
      El grosor de cada banda es proporcional al monto en USD Millones.
    </p></div>""", unsafe_allow_html=True)

    sd = (
        cs_raw[(cs_raw["Year"] >= 2022) & (cs_raw["IED"].notna()) & (cs_raw["IED"] > 50)]
        .groupby(["País_origen", "Estado"])["IED"].sum()
        .reset_index()
    )
    tc = sd.groupby("País_origen")["IED"].sum().nlargest(8).index.tolist()
    ts = sd.groupby("Estado")["IED"].sum().nlargest(12).index.tolist()
    sf = sd[sd["País_origen"].isin(tc) & sd["Estado"].isin(ts)]

    if len(sf) > 0:
        paises  = list(sf["País_origen"].unique())
        estados = list(sf["Estado"].unique())
        all_n   = paises + estados
        nidx    = {n: i for i, n in enumerate(all_n)}
        fig_sk  = go.Figure(go.Sankey(
            node=dict(
                pad=18, thickness=18,
                line=dict(color="#30363d", width=0.5),
                label=all_n,
                color=["#58a6ff"] * len(paises) + ["#3fb950"] * len(estados),
                hovertemplate="<b>%{label}</b><br>IED: $%{value:,.0f} M<extra></extra>",
            ),
            link=dict(
                source=[nidx[r["País_origen"]] for _, r in sf.iterrows()],
                target=[nidx[r["Estado"]]      for _, r in sf.iterrows()],
                value=sf["IED"].tolist(),
                color="rgba(88,166,255,0.18)",
                hovertemplate="<b>%{source.label} → %{target.label}</b><br>$%{value:,.0f} M<extra></extra>",
            ),
        ))
        fig_sk.update_layout(
            title="Flujos IED acumulados: Países de origen → Estados receptores (2022–2024)",
            template="plotly_dark",
            height=520,
            paper_bgcolor="#161b22",
            font=dict(family="IBM Plex Sans, sans-serif", size=11, color="#e6edf3"),
            margin=dict(t=50, b=20, l=20, r=20),
        )
        st.plotly_chart(fig_sk, use_container_width=True)
        st.markdown(
            "<p class='method-note'>Azul: países de origen · Verde: estados receptores · "
            "Grosor = volumen IED en USD Millones · Solo flujos &gt; $50 M · "
            "Período: acumulado 2022–2024 · Fuente: Secretaría de Economía</p>",
            unsafe_allow_html=True,
        )
    else:
        st.info("No hay flujos suficientes para construir el diagrama con los datos disponibles.")

    st.markdown("<div style='margin-top:1.6rem;'></div>", unsafe_allow_html=True)

    # Ranking nearshoring
    st.markdown(
        "<h3 style='font-size:1.05rem;color:#e6edf3;margin-bottom:0.3rem;'>"
        "Ranking de estados por señal de nearshoring</h3>",
        unsafe_allow_html=True,
    )
    ns_st = scores.sort_values("nearshoring_score", ascending=False)
    n1, n2 = st.columns(2)

    with n1:
        fig_ns = px.bar(
            ns_st.head(15),
            x="nearshoring_score", y="estado", orientation="h",
            color="zone", template="plotly_dark", height=420,
            color_discrete_map={
                "frontera":   "#d29922",
                "bajio":      "#58a6ff",
                "centro/sur": "#484f58",
            },
            labels={"nearshoring_score": "Nearshoring Score", "estado": "", "zone": "Zona"},
        )
        fig_ns.update_layout(
            **PLOT_LAYOUT,
            title="Frontera norte y Bajío concentran la señal",
            xaxis=dict(**XAXIS_BASE, title="Nearshoring Score", tickfont=dict(size=10)),
            yaxis=dict(**YAXIS_BASE, title="", tickfont=dict(size=10)),
            legend=LEGEND_V,
            margin=dict(t=45, b=20, l=10, r=10),
        )
        st.plotly_chart(fig_ns, use_container_width=True)

    with n2:
        fig_gr = px.scatter(
            ns_st.dropna(subset=["growth_ratio_2021_24", "nearshoring_score"]),
            x="growth_ratio_2021_24", y="nearshoring_score",
            color="zone", text="estado", template="plotly_dark", height=420,
            color_discrete_map={
                "frontera":   "#d29922",
                "bajio":      "#58a6ff",
                "centro/sur": "#484f58",
            },
            labels={
                "growth_ratio_2021_24": "Crecimiento IED 2021–2024 (%)",
                "nearshoring_score":    "Nearshoring Score",
                "zone":                 "Zona",
            },
        )
        fig_gr.update_traces(textposition="top center", textfont_size=7)
        fig_gr.update_layout(
            **PLOT_LAYOUT,
            title="Mayor crecimiento post-COVID coincide con señal nearshoring",
            xaxis=dict(**XAXIS_BASE, title="Crecimiento IED 2021–2024 (%)", tickfont=dict(size=10)),
            yaxis=dict(**YAXIS_BASE, title="Nearshoring Score", tickfont=dict(size=10)),
            legend=LEGEND_V,
            margin=dict(t=45, b=20, l=10, r=10),
        )
        st.plotly_chart(fig_gr, use_container_width=True)

    # Pre vs Post reconfiguración
    st.markdown(
        "<h3 style='font-size:1.05rem;color:#e6edf3;margin-top:0.8rem;margin-bottom:0.3rem;'>"
        "Inversión promedio anual antes y después de la reconfiguración</h3>",
        unsafe_allow_html=True,
    )
    pp = []
    for state in annual["Entidad federativa"].unique():
        sub  = annual[annual["Entidad federativa"] == state]
        pre  = sub[sub["Year"].between(2016, 2020)]["IED"].mean()
        post = sub[sub["Year"].between(2021, 2024)]["IED"].mean()
        if pd.notna(pre) and pd.notna(post) and pre > 0:
            pp.append({
                "Estado": state,
                "Pre":    pre,
                "Post":   post,
                "Cambio": (post - pre) / abs(pre) * 100,
            })
    df_pp = pd.DataFrame(pp).sort_values("Cambio", ascending=False)

    fig_pp = go.Figure()
    fig_pp.add_trace(go.Bar(
        name="Promedio 2016–2020", x=df_pp["Estado"], y=df_pp["Pre"],
        marker_color="#484f58", marker_line_width=0,
    ))
    fig_pp.add_trace(go.Bar(
        name="Promedio 2021–2024", x=df_pp["Estado"], y=df_pp["Post"],
        marker_color="#58a6ff", marker_line_width=0,
    ))
    fig_pp.update_layout(
        **PLOT_LAYOUT,
        title="La mayoría de estados muestra incremento en el período post-reconfiguración",
        barmode="group",
        height=400,
        xaxis=dict(**XAXIS_BASE, title="", tickangle=45, tickfont=dict(size=7)),
        yaxis=dict(**YAXIS_BASE, title="IED Promedio Anual (USD Millones)", tickfont=dict(size=10)),
        legend=dict(**LEGEND_H),
        margin=dict(t=45, b=90, l=10, r=10),
    )
    st.plotly_chart(fig_pp, use_container_width=True)

    top3 = df_pp.nlargest(3, "Cambio")["Estado"].tolist()
    st.markdown(f"""<div class="insight-box">
      <p class="insight-title">Hallazgo — Nearshoring en México</p>
      <p><strong>{", ".join(top3)}</strong> registran las mayores aceleraciones de IED
      en el período 2021–2024, consistentes con efectos de nearshoring manufacturero.
      La zona fronteriza norte y el Bajío concentran la mayor parte de esta señal,
      con el T-MEC como ancla institucional.</p>
    </div>
    <p class='method-note' style='margin-top:0.5rem;'>
      Nota: la comparación por período promedio anual (2016–2020 vs 2021–2024) es válida
      porque cada año incluye los mismos 4 trimestres. El "Nearshoring Score" es un índice
      compuesto que incorpora participación de IED de EE.UU., crecimiento relativo 2021–2024
      y proximidad a la frontera norte · Fuente: Secretaría de Economía · DGIE
    </p>""", unsafe_allow_html=True)

# =============================================================================
# TAB 3 — DINÁMICA POR PAÍS
# =============================================================================
with tab3:
    st.markdown("""<div class="intro-box"><p>
      La concentración en <strong>Estados Unidos</strong> como país de origen
      es el rasgo más persistente de la IED en México. La evolución anual permite
      identificar qué países han ganado o perdido participación estructural a lo largo del período.
      La comparación anual es metodológicamente robusta: cada punto suma los 4 trimestres del año,
      lo que hace los valores comparables entre sí.
    </p></div>""", unsafe_allow_html=True)

    top12 = (
        countries[countries["IED"].notna()]
        .groupby("Origen")["IED"].sum()
        .nlargest(12).index.tolist()
    )
    sel_c = st.multiselect(
        "Selecciona países para visualizar",
        top12, default=top12[:6], key="pais_selector",
    )

    if sel_c:
        ca = (
            countries[countries["Origen"].isin(sel_c) & countries["IED"].notna()]
            .groupby(["Year", "Origen"])["IED"].sum()
            .reset_index()
        )
        fig_ce = px.line(
            ca, x="Year", y="IED", color="Origen",
            template="plotly_dark", height=420,
            labels={"IED": "IED (USD Millones)", "Year": "Año", "Origen": "País"},
        )
        fig_ce.update_traces(line=dict(width=2))
        fig_ce.update_layout(
            **PLOT_LAYOUT,
            title="EE.UU. mantiene liderazgo; Europa y Asia ganan presencia post-2018",
            xaxis=dict(**XAXIS_BASE, title="Año", tickfont=dict(size=10)),
            yaxis=dict(**YAXIS_BASE, title="IED (USD Millones)", tickfont=dict(size=10)),
            legend=dict(**LEGEND_H),
            margin=MARGIN_STD,
        )
        st.plotly_chart(fig_ce, use_container_width=True)
        st.markdown(
            "<p class='method-note'>Fuente: Secretaría de Economía · DGIE · "
            "Agregado anual (suma de 4 trimestres) · Solo valores positivos reportados.</p>",
            unsafe_allow_html=True,
        )
    else:
        st.info("Selecciona al menos un país en el selector.")