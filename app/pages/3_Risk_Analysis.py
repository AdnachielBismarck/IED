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

st.set_page_config(page_title="Risk Analysis · IED Mexico", layout="wide", page_icon="⚠️")
st.markdown("""<style>
  [data-testid="stSidebar"] { background: #0f1117; }
  [data-testid="stSidebar"] * { color: #e8e8e8 !important; }
</style>""", unsafe_allow_html=True)

BASE = Path(__file__).resolve().parent.parent.parent
PROC = BASE / "data" / "processed" / "proc_2"

def _load(name):
    p = PROC / name
    if p.exists(): return pd.read_parquet(p)
    c = PROC / (name + ".csv")
    if c.exists(): return pd.read_csv(c, low_memory=False)
    raise FileNotFoundError(name)

@st.cache_data
def load_data():
    return _load("state_scores.parquet"), _load("country_profiles.parquet"), _load("country_by_state.parquet"), _load("investment_by_state.parquet")

scores, ctry_p, cs_raw, states = load_data()

st.markdown("# ⚠️ Risk & Dependency Analysis")
st.markdown("##### Análisis de vulnerabilidades estructurales, concentración y riesgo económico")

c1,c2,c3,c4 = st.columns(4)
c1.metric("🔴 Alta Dependencia (>60)", int((scores["dependency_score"]>60).sum()))
c2.metric("🔒 Alta Opacidad (>50%)",   int((scores["observability_risk"]>50).sum()))
c3.metric("📉 Baja Estabilidad (<30)", int((scores["stability_index"]<30).sum()))
c4.metric("🏭 Señal Nearshoring (>30)",int((scores["nearshoring_score"]>30).sum()))
st.markdown("---")

tab1,tab2,tab3,tab4 = st.tabs(["🎯 Mapa de Riesgo","🌍 Dependencia por País","📊 Concentración","🔍 Rankings"])

with tab1:
    col_a,col_b = st.columns([2,1])
    with col_a:
        fig_r = px.scatter(scores.dropna(subset=["dependency_score","observability_risk"]),
                            x="dependency_score", y="observability_risk", size="stability_index",
                            color="strategic_score", text="estado",
                            title="Mapa de Riesgo: Dependencia × Opacidad (tamaño=Estabilidad)",
                            template="plotly_dark", height=480, color_continuous_scale="RdYlGn",
                            labels={"dependency_score":"Dependencia","observability_risk":"Opacidad (%)","strategic_score":"Score Estratégico"})
        fig_r.add_hrect(y0=50, y1=100, fillcolor="rgba(255,75,75,0.04)", line_width=0)
        fig_r.add_vrect(x0=60, x1=100, fillcolor="rgba(255,75,75,0.04)", line_width=0)
        fig_r.add_annotation(x=75, y=75, text="⚠️ ZONA RIESGO ALTO", showarrow=False, font=dict(size=10, color="rgba(255,75,75,0.6)"))
        fig_r.add_annotation(x=20, y=20, text="✅ ZONA SEGURA",      showarrow=False, font=dict(size=10, color="rgba(0,200,120,0.6)"))
        fig_r.update_traces(textposition="top center", textfont_size=7)
        fig_r.update_layout(paper_bgcolor="#0f1117", plot_bgcolor="#0f1117")
        st.plotly_chart(fig_r, use_container_width=True)
    with col_b:
        rt = scores[["estado","dependency_score","observability_risk","strategic_score"]].copy()
        rt["Riesgo"] = rt.apply(lambda r: "🔴 Alto" if (r["dependency_score"]>60 or r["observability_risk"]>50) else ("🟡 Medio" if (r["dependency_score"]>35 or r["observability_risk"]>30) else "🟢 Bajo"), axis=1)
        st.markdown("### 🏷️ Clasificación de Riesgo")
        st.dataframe(rt.sort_values("dependency_score",ascending=False)[["estado","Riesgo","dependency_score","observability_risk"]].rename(columns={"estado":"Estado","dependency_score":"Dependencia","observability_risk":"Opacidad %"}).round(1), use_container_width=True, hide_index=True, height=420)

with tab2:
    top_inv = ctry_p.nlargest(20,"total_ied")
    cc1,cc2 = st.columns(2)
    with cc1:
        fig_c = px.bar(top_inv.sort_values("total_ied"), x="total_ied", y="country", orientation="h",
                        title="Top 20 Países — IED Acumulada", template="plotly_dark", height=480,
                        color="concentration_hhi", color_continuous_scale="RdYlGn_r",
                        labels={"total_ied":"IED Total (USD M)","country":"País","concentration_hhi":"Conc. HHI"})
        fig_c.update_layout(paper_bgcolor="#0f1117", plot_bgcolor="#0f1117")
        st.plotly_chart(fig_c, use_container_width=True)
    with cc2:
        fig_h = px.scatter(top_inv, x="n_states_active", y="concentration_hhi", size="total_ied", text="country",
                            title="Concentración vs Alcance Territorial", template="plotly_dark", height=480,
                            color="total_ied", color_continuous_scale="Blues",
                            labels={"n_states_active":"Estados Activos","concentration_hhi":"Concentración HHI"})
        fig_h.update_traces(textposition="top center", textfont_size=7)
        fig_h.update_layout(paper_bgcolor="#0f1117", plot_bgcolor="#0f1117")
        st.plotly_chart(fig_h, use_container_width=True)
    st.markdown("### 🌡️ Matriz País × Estado (2020-2024)")
    cs20 = cs_raw[(cs_raw["IED"].notna()) & (cs_raw["Year"]>=2020)].copy()
    top_c = ctry_p.nlargest(15,"total_ied")["country"].tolist()
    top_s = cs_raw[cs_raw["IED"].notna()].groupby("Estado")["IED"].sum().nlargest(20).index.tolist()
    matrix= cs20[cs20["País_origen"].isin(top_c) & cs20["Estado"].isin(top_s)].groupby(["País_origen","Estado"])["IED"].sum().unstack(fill_value=0)
    fig_m = go.Figure(go.Heatmap(z=matrix.values, x=matrix.columns.tolist(), y=matrix.index.tolist(),
                                   colorscale="Blues", text=np.round(matrix.values,0).astype(int), texttemplate="%{text}", textfont=dict(size=6)))
    fig_m.update_layout(title="Flujos IED País×Estado 2020-2024", template="plotly_dark", height=450, paper_bgcolor="#0f1117", plot_bgcolor="#0f1117", margin=dict(l=150,b=120))
    st.plotly_chart(fig_m, use_container_width=True)

with tab3:
    dep_s = scores.sort_values("dependency_score",ascending=False)
    cols_dep = ["#ff4b4b" if v>60 else ("#ffa500" if v>35 else "#00c878") for v in dep_s["dependency_score"].fillna(0)]
    fig_dep = go.Figure()
    fig_dep.add_trace(go.Bar(x=dep_s["estado"], y=dep_s["dependency_score"].fillna(0), marker_color=cols_dep,
                              text=[f"{v:.0f}" for v in dep_s["dependency_score"].fillna(0)], textposition="outside", textfont=dict(size=7)))
    fig_dep.add_hline(y=60, line_dash="dot", line_color="rgba(255,75,75,0.6)", annotation_text="Umbral alto", annotation_position="right")
    fig_dep.add_hline(y=35, line_dash="dot", line_color="rgba(255,165,0,0.6)",  annotation_text="Umbral medio",annotation_position="right")
    fig_dep.update_layout(title="Dependency Score por Estado", template="plotly_dark", height=400, xaxis_tickangle=45, xaxis_tickfont=dict(size=8), paper_bgcolor="#0f1117", plot_bgcolor="#0f1117")
    st.plotly_chart(fig_dep, use_container_width=True)
    d1,d2 = st.columns(2)
    with d1:
        fig_stab = px.bar(scores.sort_values("stability_index"), x="stability_index", y="estado", orientation="h",
                           title="Stability Index por Estado", template="plotly_dark", height=450, color="stability_index", color_continuous_scale="RdYlGn")
        fig_stab.update_layout(paper_bgcolor="#0f1117", plot_bgcolor="#0f1117")
        st.plotly_chart(fig_stab, use_container_width=True)
    with d2:
        fig_obs = px.bar(scores.sort_values("observability_risk",ascending=False), x="estado", y="observability_risk",
                          title="Observability Risk por Estado", template="plotly_dark", height=450, color="observability_risk", color_continuous_scale="Reds")
        fig_obs.update_layout(paper_bgcolor="#0f1117", plot_bgcolor="#0f1117", xaxis_tickangle=45, xaxis_tickfont=dict(size=7))
        st.plotly_chart(fig_obs, use_container_width=True)

with tab4:
    st.markdown("### 🏆 Rankings Inteligentes")
    rk1,rk2 = st.columns(2)
    with rk1:
        st.markdown("**✅ Top 10: Mayor Score Estratégico**")
        st.dataframe(scores.nlargest(10,"strategic_score")[["estado","strategic_score","diversification_score","nearshoring_score"]].rename(columns={"estado":"Estado","strategic_score":"Score","diversification_score":"Diversif.","nearshoring_score":"Nearshoring"}).round(1), use_container_width=True, hide_index=True)
        st.markdown("**🏭 Top 10: Señal Nearshoring**")
        st.dataframe(scores.nlargest(10,"nearshoring_score")[["estado","nearshoring_score","zone","us_share_pct","growth_ratio_2021_24"]].rename(columns={"estado":"Estado","nearshoring_score":"Score NS","zone":"Zona","us_share_pct":"% EE.UU.","growth_ratio_2021_24":"Crec 21-24%"}).round(1), use_container_width=True, hide_index=True)
    with rk2:
        st.markdown("**🔴 Top 10: Mayor Dependencia**")
        st.dataframe(scores.nlargest(10,"dependency_score")[["estado","dependency_score","top_country","top_country_share"]].rename(columns={"estado":"Estado","dependency_score":"Dependencia","top_country":"País Dom.","top_country_share":"% Dom."}).round(1), use_container_width=True, hide_index=True)
        st.markdown("**🔒 Top 10: Observability Risk**")
        st.dataframe(scores.nlargest(10,"observability_risk")[["estado","observability_risk","n_confidential_records","n_total_records"]].rename(columns={"estado":"Estado","observability_risk":"Riesgo %","n_confidential_records":"Regist. C","n_total_records":"Total"}).round(1), use_container_width=True, hide_index=True)
