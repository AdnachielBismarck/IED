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
    page_icon="🇲🇽",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  [data-testid="stSidebar"] { background: #0f1117; }
  [data-testid="stSidebar"] * { color: #e8e8e8 !important; }
  .metric-card { background:#1a1d27; border-radius:10px; padding:1rem 1.2rem; border-left:3px solid #4a9eff; margin-bottom:0.5rem; }
  .metric-card h3 { font-size:1.6rem; margin:0; color:#4a9eff; }
  .metric-card p  { margin:0; font-size:0.8rem; color:#aaa; }
  .insight-box { background:linear-gradient(135deg,#1a2744,#0f1117); border-radius:10px; padding:1.2rem; border:1px solid #2a3a5c; margin-bottom:0.8rem; }
  .insight-box .tag { font-size:0.7rem; background:#2a4a8c; color:#8ab4ff; padding:2px 8px; border-radius:12px; display:inline-block; margin-bottom:0.4rem; }
  h1, h2, h3 { color:#e8eaf6; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🌐 IED Intelligence")
    st.markdown("**Mexico · 2006–2025**")
    st.markdown("---")
    st.markdown("**Módulos**\n- 🏠 Executive Overview ← *aquí*\n- 🕸️ Network Graph\n- 🗺️ Regional Profiles\n- ⚠️ Risk & Dependency\n- 📈 Temporal Dynamics")
    st.markdown("---")
    st.caption("Fuente: Secretaría de Economía · DGIE")

# IMPORTANTE: Path debe importarse aquí. Streamlit re-ejecuta el script
# completo en cada interacción, por lo que los imports deben estar disponibles.
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
from pathlib import Path          # ← CRÍTICO: sin esto Path() falla en Streamlit
from numpy.polynomial import polynomial as P

BASE = Path(__file__).resolve().parent.parent
PROC = BASE / "data" / "processed" / "proc_2"

def _load(name):
    """Carga parquet o csv como fallback (si pyarrow no disponible)."""
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
    data["edges"]       = _load("network_edges.parquet")
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

D          = load_all()
states_df  = D["states"]
scores_df  = D["scores"]
countries_df = D["countries"]

total_recent     = states_df[states_df["Fecha"] == states_df["Fecha"].max()]["IED"].sum()
active_countries = int((countries_df[countries_df["IED"].notna()].groupby("Origen")["IED"].sum() > 0).sum())
high_risk_states = int((scores_df["dependency_score"] > 60).sum())

col_title, col_period = st.columns([3, 1])
with col_title:
    st.markdown("# 🌐 IED Intelligence Platform")
    st.markdown("##### Plataforma de Inteligencia Económica · Inversión Extranjera Directa en México")
with col_period:
    st.markdown("")
    st.info("📅 **Período:** Q1 2006 — Q2 2025\n\n📊 **Datos:** Secretaría de Economía")

st.markdown("---")

c1, c2, c3, c4, c5 = st.columns(5)
with c1: st.metric("💰 IED Último Trimestre", f"${total_recent:,.0f}M")
with c2: st.metric("🌍 Países Inversionistas", f"{active_countries}")
with c3: st.metric("🗺️ Estados Cubiertos", "32")
with c4: st.metric("🕸️ Comunidades Económicas", f"{D['graph_stats']['n_communities']}")
with c5: st.metric("⚠️ Estados Alto Riesgo", f"{high_risk_states}")

st.markdown("---")
st.markdown("## 🎯 Executive Overview")

tab1, tab2, tab3 = st.tabs(["📈 Evolución Temporal", "🗺️ Distribución Territorial", "🔍 Key Insights"])

with tab1:
    annual_total = D["states"].groupby("Year")["IED"].sum().reset_index().rename(columns={"IED":"IED_total"})
    fig_time = go.Figure()
    fig_time.add_trace(go.Bar(x=annual_total["Year"], y=annual_total["IED_total"], name="IED Total", marker_color="#4a9eff", opacity=0.8))
    xn = annual_total["Year"].values
    yn = annual_total["IED_total"].fillna(0).values
    coef = P.polyfit(xn, yn, 1)
    fig_time.add_trace(go.Scatter(x=xn, y=P.polyval(xn, coef), name="Tendencia", line=dict(color="#ff9f40", width=2, dash="dot")))
    fig_time.add_vrect(x0=2020.5, x1=2024.5, fillcolor="rgba(74,158,255,0.05)", line_width=0,
                       annotation_text="Nearshoring", annotation_position="top left",
                       annotation=dict(font_color="#4a9eff", font_size=10))
    fig_time.update_layout(title="IED Total México — Anual (USD Millones)", template="plotly_dark", height=380,
                            xaxis_title="Año", yaxis_title="IED (USD M)", plot_bgcolor="#0f1117", paper_bgcolor="#0f1117")
    st.plotly_chart(fig_time, use_container_width=True)

    types_annual = D["types"].groupby(["Year","Tipo de Inversión"])["IED"].sum().reset_index()
    fig_types = px.area(types_annual, x="Year", y="IED", color="Tipo de Inversión",
                         title="Composición por Tipo de Inversión", template="plotly_dark", height=300,
                         color_discrete_sequence=["#4a9eff","#00c878","#ff9f40"])
    fig_types.update_layout(paper_bgcolor="#0f1117", plot_bgcolor="#0f1117")
    st.plotly_chart(fig_types, use_container_width=True)

with tab2:
    recent_states = (D["states"][D["states"]["Year"] >= 2024].groupby("Entidad federativa")["IED"].sum()
                     .reset_index().sort_values("IED", ascending=True).tail(20))
    fig_states = go.Figure(go.Bar(x=recent_states["IED"], y=recent_states["Entidad federativa"],
                                   orientation="h", marker=dict(color=recent_states["IED"], colorscale="Blues")))
    fig_states.update_layout(title="Top 20 Estados por IED (2024)", template="plotly_dark", height=500,
                              xaxis_title="IED (USD M)", plot_bgcolor="#0f1117", paper_bgcolor="#0f1117")
    st.plotly_chart(fig_states, use_container_width=True)

    top_countries = (D["countries"][D["countries"]["IED"].notna()].groupby("Origen")["IED"].sum()
                     .nlargest(12).reset_index().rename(columns={"Origen":"País"}))
    fig_pie = px.pie(top_countries, values="IED", names="País", title="Composición por País de Origen (Acumulado)",
                      template="plotly_dark", hole=0.4, height=380)
    fig_pie.update_layout(paper_bgcolor="#0f1117")
    st.plotly_chart(fig_pie, use_container_width=True)

with tab3:
    st.markdown("### 💡 Hallazgos Estructurales Clave")
    top_hub       = D["graph_stats"]["top_state_hubs"][0]["node"]
    top_ns        = scores_df.nlargest(1,"nearshoring_score")["estado"].values[0]
    top_dep       = scores_df.nlargest(1,"dependency_score")["estado"].values[0]
    top_dep_ctry  = scores_df.nlargest(1,"dependency_score")["top_country"].values[0]
    top_dep_share = scores_df.nlargest(1,"dependency_score")["top_country_share"].values[0]
    gs            = D["graph_stats"]

    insights = [
        {"tag":"🏆 Hub Estratégico", "risk":"low",
         "title": f"{top_hub} concentra la mayor centralidad estructural",
         "text": f"Con el mayor Hub Score de la red, {top_hub} actúa como nodo articulador entre múltiples fuentes de inversión extranjera.",
         "impl": "Alta resiliencia estructural. Punto de entrada preferente para inversión extranjera."},
        {"tag":"🏭 Señal Nearshoring", "risk":"low",
         "title": f"{top_ns} lidera el índice de nearshoring",
         "text": f"{top_ns} presenta la mayor aceleración de inversión en el período post-pandemia (2021–2024), compatible con efectos de nearshoring manufacturero.",
         "impl": "Oportunidad de expansión industrial y desarrollo de infraestructura logística."},
        {"tag":"⚠️ Dependencia Estructural", "risk":"high",
         "title": f"{top_dep} presenta alta concentración en un solo origen",
         "text": f"Aproximadamente el {top_dep_share:.0f}% de la IED de {top_dep} proviene de {top_dep_ctry}, generando vulnerabilidad estructural.",
         "impl": "Riesgo sistémico ante shocks externos. Diversificación de origen es prioritaria."},
        {"tag":"🌐 Red de Inversión", "risk":"med",
         "title": f"La red de IED presenta {gs['n_communities']} comunidades económicas",
         "text": f"Se detectaron {gs['n_communities']} comunidades con densidad {gs['density']:.2f} y modularidad {gs['modularity']:.2f}, con lógica territorial y sectorial.",
         "impl": "Ecosistemas económicos diferenciados requieren estrategias de atracción segmentadas."},
        {"tag":"🔒 Observabilidad Parcial", "risk":"med",
         "title": "Alta confidencialidad en datos sectoriales y regionales",
         "text": "Una fracción relevante de los registros presenta valores confidenciales ('C'), generando observabilidad parcial estructural.",
         "impl": "Los rankings deben interpretarse con cautela. Estados con alta confidencialidad pueden estar subestimados."},
    ]
    risk_colors = {"high":"#ff4b4b","med":"#ffa500","low":"#00c878"}
    for ins in insights:
        c = risk_colors[ins["risk"]]
        st.markdown(f"""
        <div class="insight-box" style="border-left:4px solid {c};">
          <span class="tag">{ins['tag']}</span>
          <h4 style="margin:0.3rem 0;color:#e8eaf6;">{ins['title']}</h4>
          <p style="color:#ccc;font-size:0.9rem;margin-bottom:0.5rem;">{ins['text']}</p>
          <p style="color:{c};font-size:0.82rem;"><strong>→ Implicación:</strong> {ins['impl']}</p>
        </div>""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("## 🔬 Tipología Estructural de Estados")
clusters       = D["cluster_summary"]
cluster_colors = ["#4a9eff","#00c878","#ff9f40","#bf5af2","#ff4b4b"]
cols           = st.columns(len(clusters))
for i, (col, cluster) in enumerate(zip(cols, clusters)):
    with col:
        color = cluster_colors[i % len(cluster_colors)]
        states_list = ", ".join(cluster["states"][:4])
        if len(cluster["states"]) > 4: states_list += f" +{len(cluster['states'])-4}"
        st.markdown(f"""
        <div class="metric-card" style="border-left:3px solid {color};min-height:200px;">
          <span style="font-size:0.7rem;color:{color};text-transform:uppercase;font-weight:600;">Cluster {cluster['cluster_id']}</span>
          <h3 style="font-size:1rem;color:{color};margin:0.3rem 0;">{cluster['cluster_name']}</h3>
          <p style="font-size:0.75rem;color:#aaa;margin-bottom:0.5rem;"><strong>{cluster['n_states']}</strong> estados</p>
          <p style="font-size:0.72rem;color:#ccc;">{states_list}</p>
          <hr style="border-color:#333;margin:0.5rem 0;">
          <p style="font-size:0.7rem;color:#999;margin:0;">Dep:<b>{cluster['mean_dependency']}</b> · Div:<b>{cluster['mean_diversification']}</b><br>Near:<b>{cluster['mean_nearshoring']}</b> · Hub:<b>{cluster['mean_hub_score']}</b></p>
        </div>""", unsafe_allow_html=True)

st.markdown("---")
st.caption("IED Intelligence Platform · Secretaría de Economía · Análisis Estructural 2006–2025 · Datos en USD Millones corrientes")
