# =============================================================================
# PÁGINA 1 — ANÁLISIS DE RED · IED Intelligence Platform
# RUTAS: IED/app/pages/ → .parent.parent.parent = IED/
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import json
import pickle
import networkx as nx
from pathlib import Path           # ← CRÍTICO

st.set_page_config(page_title="Network Graph · IED Mexico", layout="wide", page_icon="🕸️")
st.markdown("""<style>
  [data-testid="stSidebar"] { background: #0f1117; }
  [data-testid="stSidebar"] * { color: #e8e8e8 !important; }
  .metric-card { background:#1a1d27; border-radius:10px; padding:1rem 1.2rem; border-left:3px solid #4a9eff; margin-bottom:0.5rem; }
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
    nodes = _load("network_nodes.parquet")
    edges = _load("network_edges.parquet")
    with open(PROC / "community_profiles.json", encoding="utf-8") as f: communities = json.load(f)
    with open(PROC / "graph_stats.json", encoding="utf-8") as f: stats = json.load(f)
    return nodes, edges, communities, stats

@st.cache_data
def get_layout():
    """Calcula posiciones x,y de cada nodo usando spring_layout.
    Se cachea para no recalcular en cada interacción."""
    with open(PROC / "main_graph.pkl", "rb") as f: G = pickle.load(f)
    pos = nx.spring_layout(G, weight="weight", seed=42, k=2.5)
    return {n: (x, y) for n, (x, y) in pos.items()}

nodes, edges, communities, stats = load_data()
pos = get_layout()

st.markdown("# 🕸️ Network Analysis")
st.markdown("##### Análisis de Red Económica · País ↔ Estado · Detección de Comunidades")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Nodos en Red", stats["n_nodes"])
c2.metric("Vínculos Económicos", stats["n_edges"])
c3.metric("Comunidades Detectadas", stats["n_communities"])
c4.metric("Modularidad (Louvain)", f"{stats['modularity']:.3f}")
st.markdown("---")

with st.sidebar:
    st.markdown("## 🔧 Filtros de Red")
    node_type_filter = st.selectbox("Mostrar nodos", ["Todos","Solo países","Solo estados"])
    min_weight = st.slider("IED mínima por arista (USD M)", 0, 5000, 50, step=50)
    color_by   = st.selectbox("Colorear por", ["Comunidad","Tipo de nodo","Hub Score"])
    st.markdown("---")
    st.caption(f"Densidad: {stats['density']:.3f}")

edges_filt = edges[edges["weight"] >= min_weight].copy()
nodes_filt = nodes.copy()
if node_type_filter == "Solo países": nodes_filt = nodes_filt[nodes_filt["node_type"] == "country"]
elif node_type_filter == "Solo estados": nodes_filt = nodes_filt[nodes_filt["node_type"] == "state"]

community_colors = ["#4a9eff","#00c878","#ff9f40","#bf5af2","#ff4b4b","#00d4d4","#ffcc00"]

edge_traces = []
for _, row in edges_filt.iterrows():
    if row["source"] not in pos or row["target"] not in pos: continue
    x0, y0 = pos[row["source"]]; x1, y1 = pos[row["target"]]
    opacity = min(0.6, max(0.05, np.log1p(row["weight"]) / 15))
    width   = max(0.3, np.log1p(row["weight"]) / 8)
    edge_traces.append(go.Scatter(x=[x0,x1,None], y=[y0,y1,None], mode="lines",
                                   line=dict(width=width, color=f"rgba(150,150,200,{opacity:.2f})"),
                                   hoverinfo="none", showlegend=False))

node_x, node_y, node_text, node_color, node_size, hover_texts = [], [], [], [], [], []
for _, row in nodes_filt.iterrows():
    if row["node"] not in pos: continue
    x, y = pos[row["node"]]
    node_x.append(x); node_y.append(y); node_text.append(row["node"])
    if color_by == "Comunidad":
        comm = int(row["community"]) if pd.notna(row["community"]) else 0
        node_color.append(community_colors[comm % len(community_colors)])
    elif color_by == "Hub Score": node_color.append(row["hub_score"])
    else: node_color.append("#4a9eff" if row["node_type"]=="country" else "#00c878")
    node_size.append(max(6, min(30, row["hub_score"] * 0.5 + 6)))
    hover_texts.append(f"<b>{row['node']}</b><br>Tipo: {'País' if row['node_type']=='country' else 'Estado'}<br>Hub Score: {row['hub_score']:.1f}<br>IED Total: ${row['total_ied']:,.0f}M<br>Betweenness: {row['betweenness']:.3f}<br>Comunidad: {int(row['community']) if pd.notna(row['community']) else 'N/A'}")

marker_cfg = dict(size=node_size, color=node_color, colorscale="Blues", showscale=True, colorbar=dict(title="Hub Score")) if color_by=="Hub Score" else dict(size=node_size, color=node_color, line=dict(width=0.5, color="#333"))
node_trace = go.Scatter(x=node_x, y=node_y, mode="markers+text", text=node_text, textposition="top center",
                         textfont=dict(size=7, color="#ddd"), marker=marker_cfg, hovertext=hover_texts, hoverinfo="text")

fig_net = go.Figure(data=edge_traces + [node_trace])
fig_net.update_layout(title=f"Red IED: País↔Estado — {len(nodes_filt)} nodos, {len(edges_filt)} vínculos (IED≥${min_weight}M)",
                       template="plotly_dark", height=600, showlegend=False,
                       xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       paper_bgcolor="#0f1117", plot_bgcolor="#0f1117", margin=dict(l=0,r=0,t=40,b=0))
st.plotly_chart(fig_net, use_container_width=True)
st.markdown("> 💎 **Diamantes** = países · ⚫ **Círculos** = estados · Tamaño = Hub Score · Grosor arista = volumen IED")

st.markdown("---")
st.markdown("## 🏘️ Comunidades Económicas Detectadas")
comm_cols = st.columns(min(4, len(communities)))
for i, (comm_id, profile) in enumerate(communities.items()):
    col = comm_cols[i % len(comm_cols)]
    with col:
        color = community_colors[int(comm_id) % len(community_colors)]
        countries_str = ", ".join(profile["top_country"][:3]) if profile["top_country"] else "N/A"
        states_str    = ", ".join(profile["top_state"][:3])   if profile["top_state"]   else "N/A"
        st.markdown(f"""<div class="metric-card" style="border-left:3px solid {color};min-height:180px;">
          <span style="font-size:0.7rem;color:{color};font-weight:700;">COMUNIDAD {int(comm_id)+1}</span>
          <p style="font-size:0.75rem;margin:0.3rem 0;color:#ccc;"><strong>{profile['n_members']}</strong> miembros ({len(profile['countries'])} países · {len(profile['states'])} estados)</p>
          <p style="font-size:0.72rem;color:#aaa;margin:0.2rem 0;">🌐 <strong>Países:</strong> {countries_str}</p>
          <p style="font-size:0.72rem;color:#aaa;margin:0.2rem 0;">🗺️ <strong>Estados:</strong> {states_str}</p>
          <p style="font-size:0.72rem;color:{color};margin-top:0.4rem;">IED Interna: ${profile['total_ied_internal']:,.0f}M</p>
        </div>""", unsafe_allow_html=True)

st.markdown("---")
col_h1, col_h2 = st.columns(2)
with col_h1:
    st.markdown("### 🏆 Top Hubs — Estados")
    st.dataframe(nodes[nodes["node_type"]=="state"].nlargest(10,"hub_score")[["node","hub_score","betweenness","eigenvector","community"]].rename(columns={"node":"Estado","hub_score":"Hub Score","betweenness":"Betweenness","eigenvector":"Eigenvector","community":"Comunidad"}).round(3), use_container_width=True, hide_index=True)
with col_h2:
    st.markdown("### 🌍 Top Hubs — Países")
    st.dataframe(nodes[nodes["node_type"]=="country"].nlargest(10,"hub_score")[["node","hub_score","betweenness","eigenvector","total_ied"]].rename(columns={"node":"País","hub_score":"Hub Score","betweenness":"Betweenness","eigenvector":"Eigenvector","total_ied":"IED Total (M)"}).round(3), use_container_width=True, hide_index=True)
