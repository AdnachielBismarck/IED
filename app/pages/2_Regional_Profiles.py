# =============================================================================
# PÁGINA 2 — PERFILES REGIONALES · IED Intelligence Platform
# RUTAS: IED/app/pages/ → .parent.parent.parent = IED/
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path           # ← CRÍTICO

st.set_page_config(page_title="Regional Profiles · IED Mexico", layout="wide", page_icon="🗺️")
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
    scores   = _load("state_scores.parquet")
    clusters = _load("state_clusters.parquet")
    annual   = _load("annual_by_state.parquet")
    top_inv  = _load("top_investors_per_state.parquet")
    nodes    = _load("network_nodes.parquet")
    types_st = _load("types_by_state.parquet")
    return scores, clusters, annual, top_inv, nodes, types_st

scores, clusters, annual, top_inv, nodes, types_st = load_data()
scores = scores.merge(clusters[["estado","cluster_id","cluster_name","pca_x","pca_y"]], on="estado", how="left")
state_nodes = nodes[nodes["node_type"]=="state"][["node","hub_score","community"]].rename(columns={"node":"estado"})
scores = scores.merge(state_nodes, on="estado", how="left")

st.markdown("# 🗺️ Regional Profiles & Economic Scoring")
st.markdown("##### Perfiles ejecutivos por estado · Indicadores estructurales de IED")

with st.sidebar:
    st.markdown("## 🗺️ Selección")
    all_states    = sorted(scores["estado"].unique())
    default       = "Ciudad de México" if "Ciudad de México" in all_states else all_states[0]
    selected      = st.selectbox("Estado principal", all_states, index=all_states.index(default))
    st.markdown("---")
    compare_states= st.multiselect("Comparar con:", [s for s in all_states if s != selected], max_selections=4)

tab_matrix, tab_profile, tab_compare = st.tabs(["🎯 Matriz Estratégica","📋 Perfil de Estado","⚖️ Comparativa"])

with tab_matrix:
    fig_m = px.scatter(scores.dropna(subset=["diversification_score","dependency_score"]),
                        x="dependency_score", y="diversification_score", size="hub_score",
                        color="nearshoring_score", text="estado",
                        title="Matriz Estratégica: Diversificación vs Dependencia",
                        template="plotly_dark", height=550, color_continuous_scale="Blues",
                        labels={"dependency_score":"Dependencia","diversification_score":"Diversificación","nearshoring_score":"Nearshoring","hub_score":"Hub Score"})
    med_dep = scores["dependency_score"].median(); med_div = scores["diversification_score"].median()
    fig_m.add_hline(y=med_div, line_dash="dot", line_color="rgba(255,255,255,0.2)")
    fig_m.add_vline(x=med_dep, line_dash="dot", line_color="rgba(255,255,255,0.2)")
    for txt,x,y in [("✅ Diversificado\nBaja dep.",10,90),("⚠️ Diversificado\nAlta dep.",70,90),("🔴 Concentrado\nAlta dep.",70,20),("🟡 Concentrado\nBaja dep.",10,20)]:
        fig_m.add_annotation(x=x, y=y, text=txt, showarrow=False, font=dict(size=9, color="rgba(200,200,200,0.5)"), align="center")
    fig_m.update_traces(textposition="top center", textfont_size=8)
    fig_m.update_layout(paper_bgcolor="#0f1117", plot_bgcolor="#0f1117")
    st.plotly_chart(fig_m, use_container_width=True)

    st.markdown("### 🌡️ Heatmap de Indicadores por Estado")
    score_cols = ["dependency_score","diversification_score","observability_risk","stability_index","nearshoring_score","hub_score","strategic_score"]
    hm = scores.set_index("estado")[score_cols].sort_values("strategic_score", ascending=False)
    fig_hm = go.Figure(go.Heatmap(z=hm.values,
                                   x=["Dependencia","Diversificación","Riesgo Obs.","Estabilidad","Nearshoring","Hub Score","Score Estratégico"],
                                   y=hm.index.tolist(), colorscale="RdYlBu",
                                   text=np.round(hm.values,1), texttemplate="%{text}", textfont=dict(size=7)))
    fig_hm.update_layout(height=700, template="plotly_dark", title="Indicadores Estructurales — Todos los Estados",
                          paper_bgcolor="#0f1117", plot_bgcolor="#0f1117", xaxis=dict(side="top"), margin=dict(l=200))
    st.plotly_chart(fig_hm, use_container_width=True)

with tab_profile:
    st.markdown(f"## 🏛️ Perfil Ejecutivo: {selected}")
    sd = scores[scores["estado"] == selected].iloc[0]
    def sc(val, inv=False):
        if pd.isna(val): return "#888"
        v = 100 - val if inv else val
        return "#00c878" if v >= 70 else ("#ffa500" if v >= 40 else "#ff4b4b")
    r1,r2,r3,r4,r5 = st.columns(5)
    for col_st, key, label, inv in [(r1,"strategic_score","Score Estratégico",False),(r2,"diversification_score","Diversificación",False),(r3,"dependency_score","Dependencia",True),(r4,"nearshoring_score","Nearshoring",False),(r5,"hub_score","Hub Score",False)]:
        val = float(sd.get(key,0) or 0); c = sc(val, inv)
        with col_st:
            st.markdown(f"<div style='text-align:center;background:#1a1d27;border-radius:10px;padding:1rem;border-top:3px solid {c};'><h2 style='color:{c};margin:0'>{val:.0f}</h2><p style='font-size:0.75rem;color:#aaa;margin:0'>{label}</p></div>", unsafe_allow_html=True)
    st.markdown("")
    col_l, col_r = st.columns(2)
    with col_l:
        state_ann = annual[annual["Entidad federativa"]==selected].sort_values("Year")
        fig_ev = go.Figure()
        fig_ev.add_trace(go.Scatter(x=state_ann["Year"], y=state_ann["IED"], mode="lines+markers",
                                     line=dict(color="#4a9eff",width=2), fill="tozeroy", fillcolor="rgba(74,158,255,0.1)"))
        fig_ev.add_vrect(x0=2020.5, x1=2024.5, fillcolor="rgba(0,200,120,0.05)", line_width=0,
                          annotation_text="Post-COVID", annotation_position="top left", annotation=dict(font_color="#00c878",font_size=9))
        fig_ev.update_layout(title=f"Evolución Anual — {selected}", template="plotly_dark", height=280,
                              paper_bgcolor="#0f1117", plot_bgcolor="#0f1117", margin=dict(t=40,b=40))
        st.plotly_chart(fig_ev, use_container_width=True)
        top_inv_state = top_inv[top_inv["Estado"]==selected].nlargest(10,"IED")
        if len(top_inv_state) > 0:
            fig_inv = px.bar(top_inv_state, x="IED", y="País_origen", orientation="h",
                              title=f"Top Países Inversores — {selected} (2023-2024)",
                              template="plotly_dark", height=280, color="IED", color_continuous_scale="Blues")
            fig_inv.update_layout(paper_bgcolor="#0f1117", plot_bgcolor="#0f1117", margin=dict(t=40,b=20), showlegend=False)
            st.plotly_chart(fig_inv, use_container_width=True)
    with col_r:
        categories = ["Diversificación","Estabilidad","Nearshoring","Hub Score","Anti-Dependencia","Observabilidad OK"]
        values = [float(sd.get("diversification_score",0) or 0), float(sd.get("stability_index",0) or 0),
                  float(sd.get("nearshoring_score",0) or 0)*2, float(sd.get("hub_score",0) or 0)*2,
                  100-float(sd.get("dependency_score",50) or 50), 100-float(sd.get("observability_risk",50) or 50)]
        vn = [min(100,v) for v in values]
        fig_r = go.Figure()
        fig_r.add_trace(go.Scatterpolar(r=vn+[vn[0]], theta=categories+[categories[0]], fill="toself",
                                         fillcolor="rgba(74,158,255,0.2)", line=dict(color="#4a9eff",width=2)))
        fig_r.update_layout(polar=dict(radialaxis=dict(visible=True,range=[0,100],gridcolor="#333"),
                                        angularaxis=dict(gridcolor="#333"),bgcolor="#0f1117"),
                              showlegend=False, template="plotly_dark", title=f"Perfil — {selected}", height=320, paper_bgcolor="#0f1117")
        st.plotly_chart(fig_r, use_container_width=True)
        excl = ["Total general","Total general por estado"]
        tss = types_st[(types_st["Estado"]==selected) & (~types_st["Tipo de Inversión"].isin(excl)) & (types_st["IED"].notna())]
        if len(tss) > 0:
            tr = tss[tss["Year"]>=2020].groupby("Tipo de Inversión")["IED"].mean().reset_index()
            fig_tp = px.pie(tr, values="IED", names="Tipo de Inversión", title="Composición por Tipo (Prom 2020-2024)",
                             template="plotly_dark", hole=0.4, height=280, color_discrete_sequence=["#4a9eff","#00c878","#ff9f40"])
            fig_tp.update_layout(paper_bgcolor="#0f1117")
            st.plotly_chart(fig_tp, use_container_width=True)
        dep  = float(sd.get("dependency_score",0) or 0)
        div  = float(sd.get("diversification_score",0) or 0)
        ns   = float(sd.get("nearshoring_score",0) or 0)
        top_c= sd.get("top_country","N/D")
        top_sh=float(sd.get("top_country_share",0) or 0)
        rl   = "ALTO" if dep>60 else ("MODERADO" if dep>35 else "BAJO")
        rc   = "#ff4b4b" if dep>60 else ("#ffa500" if dep>35 else "#00c878")
        ns_t = f"Señal nearshoring <strong>significativa</strong> ({ns:.0f}/100), aceleración post-2021." if ns>25 else "Señal nearshoring moderada."
        st.markdown(f"""<div style="background:#1a1d27;border-radius:10px;padding:1rem;border:1px solid #2a3a5c;margin-top:0.5rem;">
          <h4 style="color:#e8eaf6;margin:0 0 0.5rem;">📝 Síntesis Ejecutiva</h4>
          <p style="font-size:0.85rem;color:#ccc;line-height:1.6;">
          <strong>{selected}</strong> presenta diversificación <strong>{div:.0f}/100</strong> y dependencia <span style="color:{rc};font-weight:600;">{rl}</span> ({dep:.0f}/100).
          {f"País inversor principal: <strong>{top_c}</strong> con {top_sh:.0f}% del flujo." if top_c else ""} {ns_t}</p></div>""", unsafe_allow_html=True)

with tab_compare:
    states_cmp = [selected] + compare_states
    comp = scores[scores["estado"].isin(states_cmp)]
    if len(comp) < 2:
        st.info("Selecciona al menos un estado adicional en el panel izquierdo.")
    else:
        sc_cols = ["diversification_score","dependency_score","stability_index","nearshoring_score","hub_score","strategic_score"]
        lb_cols = ["Diversificación","Dependencia","Estabilidad","Nearshoring","Hub Score","Score Estratégico"]
        colors_c= ["#4a9eff","#00c878","#ff9f40","#bf5af2","#ff4b4b"]
        fig_cmp = go.Figure()
        for i,(_, row) in enumerate(comp.iterrows()):
            fig_cmp.add_trace(go.Bar(name=row["estado"], x=lb_cols, y=[float(row.get(c,0) or 0) for c in sc_cols], marker_color=colors_c[i%len(colors_c)]))
        fig_cmp.update_layout(title="Comparativa de Indicadores Estructurales", template="plotly_dark", barmode="group", height=420, paper_bgcolor="#0f1117", plot_bgcolor="#0f1117", legend=dict(orientation="h",y=-0.15))
        st.plotly_chart(fig_cmp, use_container_width=True)
        st.dataframe(comp[["estado"]+sc_cols].rename(columns=dict(zip(sc_cols,lb_cols))).round(1).reset_index(drop=True), use_container_width=True, hide_index=True)
