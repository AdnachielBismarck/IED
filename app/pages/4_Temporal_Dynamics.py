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

st.set_page_config(page_title="Temporal Dynamics · IED Mexico", layout="wide", page_icon="📈")
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
    return (_load("investment_by_state.parquet"), _load("investment_by_country.parquet"),
            _load("investment_types.parquet"), _load("annual_by_state.parquet"),
            _load("state_scores.parquet"), _load("country_by_state.parquet"))

states, countries, types, annual, scores, cs_raw = load_data()

annual_total = states.groupby("Year")["IED"].sum()
peak_year  = int(annual_total.idxmax())
peak_val   = float(annual_total.max())
recent_avg = float(annual_total[annual_total.index >= 2021].mean())
# annual_total.index es un pd.Index (integers), no una pd.Series.
# .between() no existe en pd.Index — se usa comparación directa en su lugar.
pre_avg    = float(annual_total[(annual_total.index >= 2015) & (annual_total.index <= 2019)].mean())
growth_pct = ((recent_avg - pre_avg) / abs(pre_avg) * 100) if pre_avg else 0

st.markdown("# 📈 Temporal Dynamics & Nearshoring")
st.markdown("##### Evolución estructural de la IED · Patrones de nearshoring · Cambios de composición")

c1,c2,c3,c4 = st.columns(4)
c1.metric("📅 Año Pico", f"{peak_year}", f"${peak_val:,.0f}M")
c2.metric("📊 Prom. 2021-2024", f"${recent_avg:,.0f}M")
c3.metric("📊 Prom. 2015-2019", f"${pre_avg:,.0f}M")
c4.metric("📈 Crecimiento Post-COVID", f"{growth_pct:+.1f}%")
st.markdown("---")

tab1,tab2,tab3 = st.tabs(["📈 Evolución Temporal","🏭 Señal Nearshoring","🌍 Dinámica por País"])

with tab1:
    nq = states.groupby("Fecha")["IED"].sum().reset_index()
    nq["IED_4Q"] = nq["IED"].rolling(4).mean()
    fig_n = go.Figure()
    fig_n.add_trace(go.Scatter(x=nq["Fecha"], y=nq["IED"], name="IED Trimestral",
                                line=dict(color="#4a9eff",width=1.5), fill="tozeroy", fillcolor="rgba(74,158,255,0.08)"))
    fig_n.add_trace(go.Scatter(x=nq["Fecha"], y=nq["IED_4Q"], name="Media Móvil 4Q", line=dict(color="#ff9f40",width=2)))
    for date,label,color in [("2008-09-01","Crisis\nFinanciera","#ff4b4b"),("2020-04-01","COVID-19","#ff4b4b"),("2022-01-01","Nearshoring\nAceleración","#00c878"),("2018-10-01","T-MEC\nFirma","#4a9eff")]:
        fig_n.add_vline(x=date, line_dash="dot", opacity=0.4, line_color=color)
        fig_n.add_annotation(x=date, y=nq["IED"].max()*0.9, text=label, showarrow=False, font=dict(size=8,color=color), textangle=-90, xanchor="left")
    fig_n.update_layout(title="IED Total México — Serie Trimestral 2006–2025", template="plotly_dark", height=380,
                         xaxis_title="Trimestre", yaxis_title="IED (USD M)", paper_bgcolor="#0f1117", plot_bgcolor="#0f1117",
                         legend=dict(orientation="h",y=-0.15))
    st.plotly_chart(fig_n, use_container_width=True)

    ta = types.groupby(["Year","Tipo de Inversión"])["IED"].sum().reset_index()
    fig_ta = px.bar(ta, x="Year", y="IED", color="Tipo de Inversión", title="Composición por Tipo de Inversión",
                     template="plotly_dark", height=320, barmode="stack", color_discrete_sequence=["#4a9eff","#00c878","#ff9f40"])
    fig_ta.update_layout(paper_bgcolor="#0f1117", plot_bgcolor="#0f1117")
    st.plotly_chart(fig_ta, use_container_width=True)

    top_st = annual.groupby("Entidad federativa")["IED"].sum().nlargest(10).index.tolist()
    fig_se = px.line(annual[annual["Entidad federativa"].isin(top_st)], x="Year", y="IED", color="Entidad federativa",
                      title="Evolución IED — Top 10 Estados (Anual)", template="plotly_dark", height=400)
    fig_se.update_layout(paper_bgcolor="#0f1117", plot_bgcolor="#0f1117", legend=dict(orientation="h",y=-0.2,font=dict(size=9)))
    st.plotly_chart(fig_se, use_container_width=True)

with tab2:
    st.markdown("### 🏭 Análisis de Señal Nearshoring")
    ns_st = scores.sort_values("nearshoring_score",ascending=False)
    n1,n2 = st.columns(2)
    with n1:
        fig_ns = px.bar(ns_st.head(15), x="nearshoring_score", y="estado", orientation="h",
                         color="zone", title="Top 15 Estados por Señal Nearshoring", template="plotly_dark", height=400,
                         color_discrete_map={"frontera":"#ff9f40","bajio":"#4a9eff","centro/sur":"#888"})
        fig_ns.update_layout(paper_bgcolor="#0f1117", plot_bgcolor="#0f1117")
        st.plotly_chart(fig_ns, use_container_width=True)
    with n2:
        fig_gr = px.scatter(ns_st, x="growth_ratio_2021_24", y="nearshoring_score", color="zone", text="estado",
                             title="Crecimiento Post-COVID vs Señal Nearshoring", template="plotly_dark", height=400,
                             color_discrete_map={"frontera":"#ff9f40","bajio":"#4a9eff","centro/sur":"#888"},
                             labels={"growth_ratio_2021_24":"Crecimiento 2021-24 (%)","nearshoring_score":"Nearshoring Score"})
        fig_gr.update_traces(textposition="top center", textfont_size=7)
        fig_gr.update_layout(paper_bgcolor="#0f1117", plot_bgcolor="#0f1117")
        st.plotly_chart(fig_gr, use_container_width=True)

    st.markdown("### 📊 IED Pre vs Post Reconfiguración (2016-2020 vs 2021-2024)")
    pp = []
    for state in annual["Entidad federativa"].unique():
        sub = annual[annual["Entidad federativa"]==state]
        pre  = sub[sub["Year"].between(2016,2020)]["IED"].mean()
        post = sub[sub["Year"].between(2021,2024)]["IED"].mean()
        if pd.notna(pre) and pd.notna(post) and pre > 0:
            pp.append({"Estado":state,"Pre (2016-20)":pre,"Post (2021-24)":post,"Cambio %":(post-pre)/abs(pre)*100})
    df_pp = pd.DataFrame(pp).sort_values("Cambio %",ascending=False)
    fig_pp = go.Figure()
    fig_pp.add_trace(go.Bar(name="Pre (2016-2020)", x=df_pp["Estado"], y=df_pp["Pre (2016-20)"], marker_color="#888"))
    fig_pp.add_trace(go.Bar(name="Post (2021-2024)",x=df_pp["Estado"], y=df_pp["Post (2021-24)"],marker_color="#4a9eff"))
    fig_pp.update_layout(title="IED Promedio Anual — Pre vs Post Reconfiguración", template="plotly_dark", barmode="group", height=400,
                          xaxis_tickangle=45, xaxis_tickfont=dict(size=7), paper_bgcolor="#0f1117", plot_bgcolor="#0f1117", legend=dict(orientation="h",y=-0.2))
    st.plotly_chart(fig_pp, use_container_width=True)
    top3 = df_pp.nlargest(3,"Cambio %")["Estado"].tolist()
    st.markdown(f"""<div style="background:#1a2744;border-radius:10px;padding:1rem;border:1px solid #2a3a5c;">
      <h4 style="color:#4a9eff;margin:0 0 0.5rem;">📍 Insight Ejecutivo: Nearshoring en México</h4>
      <p style="color:#ccc;font-size:0.9rem;line-height:1.6;">Los estados de <strong>{", ".join(top3)}</strong> registran las mayores aceleraciones de IED post-pandemia (2021–2024), consistentes con efectos de nearshoring manufacturero. La zona fronteriza norte y el Bajío concentran la mayor parte de esta señal, con el T-MEC como ancla institucional.</p>
    </div>""", unsafe_allow_html=True)

with tab3:
    st.markdown("### 🌍 Evolución por País de Origen")
    top10 = countries[countries["IED"].notna()].groupby("Origen")["IED"].sum().nlargest(12).index.tolist()
    sel_c = st.multiselect("Países a visualizar", top10, default=top10[:6])
    if sel_c:
        ca = countries[countries["Origen"].isin(sel_c) & countries["IED"].notna()].groupby(["Year","Origen"])["IED"].sum().reset_index()
        fig_ce = px.line(ca, x="Year", y="IED", color="Origen", title="Evolución IED por País (Anual)", template="plotly_dark", height=400)
        fig_ce.update_layout(paper_bgcolor="#0f1117", plot_bgcolor="#0f1117", legend=dict(orientation="h",y=-0.2,font=dict(size=9)))
        st.plotly_chart(fig_ce, use_container_width=True)
        total_y = countries[countries["IED"].notna()].groupby("Year")["IED"].sum()
        cs2 = ca.copy()
        cs2["share"] = cs2.apply(lambda r: r["IED"]/total_y.get(r["Year"],1)*100, axis=1)
        fig_sh = px.area(cs2, x="Year", y="share", color="Origen", title="Participación de Mercado por País (%)", template="plotly_dark", height=350)
        fig_sh.update_layout(paper_bgcolor="#0f1117", plot_bgcolor="#0f1117")
        st.plotly_chart(fig_sh, use_container_width=True)

    st.markdown("### 🔀 Flujos de Inversión — Sankey (2022–2024)")
    sd = cs_raw[(cs_raw["Year"]>=2022) & (cs_raw["IED"].notna()) & (cs_raw["IED"]>50)].groupby(["País_origen","Estado"])["IED"].sum().reset_index()
    tc = sd.groupby("País_origen")["IED"].sum().nlargest(8).index.tolist()
    ts = sd.groupby("Estado")["IED"].sum().nlargest(12).index.tolist()
    sf = sd[sd["País_origen"].isin(tc) & sd["Estado"].isin(ts)]
    if len(sf) > 0:
        all_n = list(sf["País_origen"].unique()) + list(sf["Estado"].unique())
        nidx  = {n: i for i,n in enumerate(all_n)}
        fig_sk = go.Figure(go.Sankey(
            node=dict(pad=15, thickness=15, line=dict(color="black",width=0.5), label=all_n,
                      color=["#4a9eff"]*len(sf["País_origen"].unique())+["#00c878"]*len(sf["Estado"].unique())),
            link=dict(source=[nidx[r["País_origen"]] for _,r in sf.iterrows()],
                      target=[nidx[r["Estado"]]      for _,r in sf.iterrows()],
                      value=sf["IED"].tolist(), color="rgba(74,158,255,0.2)")))
        fig_sk.update_layout(title="Flujos IED: Top Países → Top Estados (2022-2024)", template="plotly_dark", height=500, paper_bgcolor="#0f1117", font=dict(size=10,color="#ddd"))
        st.plotly_chart(fig_sk, use_container_width=True)
