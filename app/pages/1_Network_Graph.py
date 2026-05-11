# =============================================================================
# PÁGINA 1 — ANÁLISIS DE RED · IED Intelligence Platform
# RUTAS: IED/app/pages/ → .parent.parent.parent = IED/
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import json
import pickle
import networkx as nx
from pathlib import Path

st.set_page_config(
    page_title="Network Graph · IED Mexico",
    layout="wide",
    page_icon="🕸️",
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

  .legend-box {
    background: var(--bg-elevated);
    border: 1px solid var(--border-subtle);
    border-radius: 8px;
    padding: 0.7rem 1rem;
    margin-bottom: 0.8rem;
    display: flex;
    gap: 1.5rem;
    flex-wrap: wrap;
    align-items: center;
  }
  .legend-item {
    font-size: 0.78rem;
    color: var(--text-secondary);
    display: flex;
    align-items: center;
    gap: 0.4rem;
  }
  .legend-dot {
    width: 10px; height: 10px;
    border-radius: 50%;
    display: inline-block;
    flex-shrink: 0;
  }
  .legend-line {
    width: 24px; height: 2px;
    display: inline-block;
    flex-shrink: 0;
    border-radius: 1px;
  }

  .filter-box {
    background: var(--bg-elevated);
    border: 1px solid var(--border-subtle);
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin-bottom: 1rem;
  }

  .comm-card {
    background: var(--bg-elevated);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1rem 1.1rem;
    margin-bottom: 0.6rem;
    min-height: 220px;
  }
  .comm-card .comm-tag {
    font-size: 0.68rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin: 0 0 0.3rem;
  }
  .comm-card .comm-name {
    font-size: 0.92rem;
    font-weight: 600;
    margin: 0 0 0.4rem;
    line-height: 1.3;
  }
  .comm-card .comm-meta {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    color: var(--text-muted);
    margin: 0 0 0.4rem;
  }
  .comm-card .comm-members {
    font-size: 0.76rem;
    color: var(--text-secondary);
    margin: 0.2rem 0;
    line-height: 1.5;
  }
  .comm-card .comm-desc {
    font-size: 0.78rem;
    color: var(--text-secondary);
    margin: 0.5rem 0 0;
    line-height: 1.5;
    border-top: 1px solid var(--border-subtle);
    padding-top: 0.4rem;
  }
  .comm-card .comm-ied {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
    margin: 0.3rem 0 0;
  }

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
    nodes = _load("network_nodes.parquet")
    edges = _load("network_edges.parquet")
    with open(PROC / "community_profiles.json", encoding="utf-8") as f:
        communities = json.load(f)
    with open(PROC / "graph_stats.json", encoding="utf-8") as f:
        stats = json.load(f)
    return nodes, edges, communities, stats

@st.cache_data
def get_layout():
    """Calcula posiciones x,y con spring_layout. Cacheado para no recalcular."""
    with open(PROC / "main_graph.pkl", "rb") as f:
        G = pickle.load(f)
    pos = nx.spring_layout(G, weight="weight", seed=42, k=2.5)
    return {n: (float(x), float(y)) for n, (x, y) in pos.items()}

nodes, edges, communities, stats = load_data()
pos = get_layout()

# ── Nombres y descripciones de comunidades ────────────────────────────────────
COMM_NAMES = {
    "0": ("Bloque Norteamericano y Tecnológico",
          "Agrupa a EE.UU., Suiza e Irlanda junto con los estados de mayor diversificación "
          "tecnológica y manufacturera. Domina en volumen absoluto y centralidad de red."),
    "1": ("Capital Financiero Especializado",
          "Flujos de capital provenientes de centros financieros internacionales "
          "(Luxemburgo, Hong Kong) hacia estados con perfil de inversión concentrada y no industrial."),
    "2": ("Bloque Europeo-Latino y Turismo",
          "España, Canadá e Italia articulan inversión hacia estados con vocación industrial "
          "y turística. Coahuila, Querétaro y Quintana Roo son los receptores principales."),
    "3": ("Corredor Industrial del Noreste",
          "Países Bajos, Corea del Sur y Argentina invierten principalmente en Nuevo León y Veracruz, "
          "estados con infraestructura industrial y logística consolidada."),
    "4": ("Ecosistema Automotriz Japonés",
          "Japón concentra su inversión en el clúster automotriz del Bajío: "
          "Guanajuato, Aguascalientes y Morelos. Alta especialización sectorial."),
    "5": ("Bloque Europeo Diversificado",
          "Alemania, Reino Unido y Francia diversifican flujos hacia el Estado de México, "
          "Jalisco y San Luis Potosí. Sectores manufacturero, retail y servicios."),
    "6": ("Origen Difuso / Minería",
          "Origen no clasificado o diverso, con presencia predominante en Sonora y Zacatecas. "
          "Patrón consistente con inversión en sectores extractivos y mineros."),
}

COMM_COLORS = [
    "#58a6ff",  # 0 — azul
    "#bc8cff",  # 1 — púrpura
    "#d29922",  # 2 — ámbar
    "#3fb950",  # 3 — verde
    "#f85149",  # 4 — rojo
    "#58d4d4",  # 5 — cian
    "#8b949e",  # 6 — gris
]

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
    "¿Cómo se organizan los países inversores y los estados en ecosistemas económicos?</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='font-size:0.9rem;color:#8b949e;margin-top:0;margin-bottom:1rem;'>"
    "Network Analysis — Estructura de vínculos País ↔ Estado · Comunidades · Nodos estratégicos</p>",
    unsafe_allow_html=True,
)

# ── KPIs ──────────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"""<div class="kpi-card">
      <p class="kpi-val">{stats['n_nodes']}</p>
      <p class="kpi-label">Nodos en la red</p>
      <p class="kpi-sub">Países + estados</p>
    </div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""<div class="kpi-card">
      <p class="kpi-val">{stats['n_edges']}</p>
      <p class="kpi-label">Vínculos económicos</p>
      <p class="kpi-sub">Flujos IED activos</p>
    </div>""", unsafe_allow_html=True)
with k3:
    st.markdown(f"""<div class="kpi-card">
      <p class="kpi-val">{stats['n_communities']}</p>
      <p class="kpi-label">Comunidades detectadas</p>
      <p class="kpi-sub">Algoritmo Louvain</p>
    </div>""", unsafe_allow_html=True)
with k4:
    st.markdown(f"""<div class="kpi-card">
      <p class="kpi-val">{stats['modularity']:.3f}</p>
      <p class="kpi-label">Modularidad de red</p>
      <p class="kpi-sub">Densidad: {stats['density']:.3f}</p>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='margin-top:1.2rem;'></div>", unsafe_allow_html=True)

# ── Introducción ──────────────────────────────────────────────────────────────
st.markdown("""<div class="intro-box"><p>
  Una <strong>red de inversión</strong> representa a países y estados como nodos, y los flujos
  de IED como aristas que los conectan. Este enfoque revela patrones que una tabla no puede mostrar:
  qué nodos actúan como <strong>puentes estratégicos</strong> entre múltiples fuentes de capital,
  qué países invierten juntos en los mismos estados, y cómo se agrupan en
  <strong>ecosistemas económicos</strong> con lógica territorial y sectorial.
  El tamaño de cada nodo refleja su <strong>Hub Score</strong> —
  una medida de centralidad que combina volumen, diversificación y posición estructural en la red.
</p></div>""", unsafe_allow_html=True)

# ── Filtros dentro de la página ───────────────────────────────────────────────
st.markdown("<div class='filter-box'>", unsafe_allow_html=True)
fc1, fc2, fc3 = st.columns(3)
with fc1:
    node_type_filter = st.selectbox(
        "Nodos a mostrar",
        ["Todos", "Solo países", "Solo estados"],
        key="node_type",
    )
with fc2:
    min_weight = st.slider(
        "IED mínima por vínculo (USD M)",
        0, 5000, 50, step=50,
        key="min_weight",
    )
with fc3:
    color_by = st.selectbox(
        "Colorear nodos por",
        ["Comunidad", "Tipo de nodo", "Hub Score"],
        key="color_by",
        help="Comunidad: agrupa por ecosistema detectado · Tipo: azul=país, verde=estado · Hub Score: gradiente de centralidad",
    )
st.markdown("</div>", unsafe_allow_html=True)

# ── Construir red ─────────────────────────────────────────────────────────────
edges_filt = edges[edges["weight"] >= min_weight].copy()
nodes_filt = nodes.copy()
if node_type_filter == "Solo países":
    nodes_filt = nodes_filt[nodes_filt["node_type"] == "country"]
elif node_type_filter == "Solo estados":
    nodes_filt = nodes_filt[nodes_filt["node_type"] == "state"]

# Aristas
edge_traces = []
for _, row in edges_filt.iterrows():
    if row["source"] not in pos or row["target"] not in pos:
        continue
    x0, y0 = pos[row["source"]]
    x1, y1 = pos[row["target"]]
    opacity = min(0.55, max(0.04, np.log1p(row["weight"]) / 15))
    width   = max(0.3,  np.log1p(row["weight"]) / 8)
    edge_traces.append(go.Scatter(
        x=[x0, x1, None], y=[y0, y1, None],
        mode="lines",
        line=dict(width=width, color=f"rgba(140,140,190,{opacity:.2f})"),
        hoverinfo="none",
        showlegend=False,
    ))

# Nodos
node_x, node_y, node_text, node_color, node_size, hover_texts = [], [], [], [], [], []
for _, row in nodes_filt.iterrows():
    if row["node"] not in pos:
        continue
    x, y = pos[row["node"]]
    node_x.append(x)
    node_y.append(y)
    node_text.append(row["node"])

    if color_by == "Comunidad":
        comm = int(row["community"]) if pd.notna(row["community"]) else 0
        node_color.append(COMM_COLORS[comm % len(COMM_COLORS)])
    elif color_by == "Hub Score":
        node_color.append(float(row["hub_score"]))
    else:
        node_color.append("#58a6ff" if row["node_type"] == "country" else "#3fb950")

    node_size.append(max(7, min(32, float(row["hub_score"]) * 0.5 + 7)))

    comm_id  = str(int(row["community"])) if pd.notna(row["community"]) else "N/A"
    comm_name= COMM_NAMES.get(comm_id, ("Sin clasificar", ""))[0] if comm_id != "N/A" else "N/A"
    tipo     = "País" if row["node_type"] == "country" else "Estado"
    hover_texts.append(
        f"<b>{row['node']}</b><br>"
        f"Tipo: {tipo}<br>"
        f"Hub Score: {row['hub_score']:.1f}<br>"
        f"IED Total: ${row['total_ied']:,.0f} M<br>"
        f"Betweenness: {row['betweenness']:.3f}<br>"
        f"Comunidad: {comm_name}"
    )

if color_by == "Hub Score":
    marker_cfg = dict(
        size=node_size,
        color=node_color,
        colorscale="Blues",
        showscale=True,
        colorbar=dict(title="Hub Score", thickness=12, len=0.6),
        line=dict(width=0.5, color="#161b22"),
    )
else:
    marker_cfg = dict(
        size=node_size,
        color=node_color,
        line=dict(width=0.5, color="#161b22"),
    )

node_trace = go.Scatter(
    x=node_x, y=node_y,
    mode="markers+text",
    text=node_text,
    textposition="top center",
    textfont=dict(size=7, color="#8b949e"),
    marker=marker_cfg,
    hovertext=hover_texts,
    hoverinfo="text",
)

fig_net = go.Figure(data=edge_traces + [node_trace])
fig_net.update_layout(
    title=f"Red IED País ↔ Estado — {len(nodes_filt)} nodos · {len(edges_filt)} vínculos · IED ≥ ${min_weight} M",
    template="plotly_dark",
    height=620,
    showlegend=False,
    paper_bgcolor="#161b22",
    plot_bgcolor="#161b22",
    font=dict(family="IBM Plex Sans, sans-serif", color="#8b949e", size=11),
    title_font=dict(family="IBM Plex Sans, sans-serif", color="#e6edf3", size=13),
    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, linecolor="#30363d"),
    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, linecolor="#30363d"),
    margin=dict(l=0, r=0, t=45, b=0),
)
st.plotly_chart(fig_net, use_container_width=True)

# ── Leyenda interpretativa ────────────────────────────────────────────────────
st.markdown("""
<div class="legend-box">
  <span style="font-size:0.75rem;color:#8b949e;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;">Cómo leer esta red:</span>
  <span class="legend-item">
    <span class="legend-dot" style="background:#58a6ff;width:14px;height:14px;border-radius:50%;"></span>
    Nodo grande = mayor Hub Score (centralidad + volumen)
  </span>
  <span class="legend-item">
    <span class="legend-line" style="background:rgba(140,140,190,0.5);height:3px;"></span>
    Línea gruesa = mayor volumen de IED en el vínculo
  </span>
  <span class="legend-item">
    <span class="legend-dot" style="background:#58a6ff;"></span>
    Azul = país de origen
  </span>
  <span class="legend-item">
    <span class="legend-dot" style="background:#3fb950;"></span>
    Verde = estado receptor
  </span>
  <span class="legend-item" style="color:#484f58;">
    Pasa el cursor sobre un nodo para ver su detalle
  </span>
</div>
<p class="method-note">
  Posiciones calculadas con algoritmo spring_layout (NetworkX · seed=42) ·
  Comunidades detectadas con algoritmo Louvain · Modularidad {modularity:.3f} indica estructura comunitaria {mod_desc}.
</p>
""".format(
    modularity=stats["modularity"],
    mod_desc="bien definida" if stats["modularity"] > 0.4 else "moderada",
), unsafe_allow_html=True)

st.markdown("<div style='margin-top:1.6rem;'></div>", unsafe_allow_html=True)

# ── Comunidades económicas ────────────────────────────────────────────────────
st.markdown(
    "<h2 style='font-size:1.2rem;color:#e6edf3;margin-bottom:0.3rem;'>"
    "Ecosistemas económicos detectados</h2>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='font-size:0.85rem;color:#8b949e;margin-bottom:1rem;'>"
    "El algoritmo Louvain identifica grupos de países y estados que invierten y reciben "
    "inversión de forma preferente entre sí, formando ecosistemas con lógica territorial y sectorial.</p>",
    unsafe_allow_html=True,
)

# Mostrar en dos filas de columnas para mejor legibilidad
comm_items = list(communities.items())
n_cols = min(4, len(comm_items))

for row_start in range(0, len(comm_items), n_cols):
    row_items = comm_items[row_start:row_start + n_cols]
    cols = st.columns(len(row_items))
    for col, (comm_id, profile) in zip(cols, row_items):
        cid   = str(int(comm_id)) if str(comm_id).isdigit() else comm_id
        color = COMM_COLORS[int(cid) % len(COMM_COLORS)]
        name, desc = COMM_NAMES.get(cid, (f"Comunidad {cid}", "Sin descripción disponible."))
        countries_str = ", ".join(profile["top_country"][:3]) if profile["top_country"] else "N/A"
        states_str    = ", ".join(profile["top_state"][:3])   if profile["top_state"]   else "N/A"
        n_paises      = len(profile.get("countries", []))
        n_estados     = len(profile.get("states", []))
        ied_int       = profile.get("total_ied_internal", 0)

        with col:
            st.markdown(f"""
            <div class="comm-card" style="border-left: 3px solid {color};">
              <p class="comm-tag" style="color:{color};">Ecosistema {int(cid)+1}</p>
              <p class="comm-name" style="color:{color};">{name}</p>
              <p class="comm-meta">{n_paises} países · {n_estados} estados · {profile['n_members']} miembros</p>
              <p class="comm-members"><strong style="color:#e6edf3;">Países:</strong> {countries_str}</p>
              <p class="comm-members"><strong style="color:#e6edf3;">Estados:</strong> {states_str}</p>
              <p class="comm-ied" style="color:{color};">IED interna: ${ied_int:,.0f} M</p>
              <p class="comm-desc">{desc}</p>
            </div>""", unsafe_allow_html=True)

st.markdown("<div style='margin-top:1.6rem;'></div>", unsafe_allow_html=True)

# ── Top Hubs ──────────────────────────────────────────────────────────────────
st.markdown(
    "<h2 style='font-size:1.2rem;color:#e6edf3;margin-bottom:0.3rem;'>"
    "Nodos más estratégicos de la red</h2>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='font-size:0.85rem;color:#8b949e;margin-bottom:1rem;'>"
    "El <strong>Hub Score</strong> combina volumen de IED, betweenness centrality (rol de puente) "
    "y eigenvector centrality (conexión con nodos influyentes). "
    "Un Hub Score alto indica un nodo estratégico que conecta múltiples fuentes o destinos de inversión.</p>",
    unsafe_allow_html=True,
)

h1, h2 = st.columns(2)

with h1:
    st.markdown(
        "<p style='font-size:0.85rem;font-weight:600;color:#e6edf3;margin-bottom:0.4rem;'>"
        "Top 10 — Estados por Hub Score</p>",
        unsafe_allow_html=True,
    )
    top_states = (
        nodes[nodes["node_type"] == "state"]
        .nlargest(10, "hub_score")
        [["node", "hub_score", "betweenness", "eigenvector", "community"]]
        .copy()
    )
    # Agregar nombre de comunidad
    top_states["Ecosistema"] = top_states["community"].apply(
        lambda c: COMM_NAMES.get(str(int(c)), ("—", ""))[0] if pd.notna(c) else "—"
    )
    top_states = top_states.rename(columns={
        "node":        "Estado",
        "hub_score":   "Hub Score",
        "betweenness": "Betweenness",
        "eigenvector": "Eigenvector",
    }).drop(columns=["community"]).round(3)
    st.dataframe(top_states, use_container_width=True, hide_index=True)

with h2:
    st.markdown(
        "<p style='font-size:0.85rem;font-weight:600;color:#e6edf3;margin-bottom:0.4rem;'>"
        "Top 10 — Países por Hub Score</p>",
        unsafe_allow_html=True,
    )
    top_countries = (
        nodes[nodes["node_type"] == "country"]
        .nlargest(10, "hub_score")
        [["node", "hub_score", "betweenness", "eigenvector", "total_ied"]]
        .rename(columns={
            "node":        "País",
            "hub_score":   "Hub Score",
            "betweenness": "Betweenness",
            "eigenvector": "Eigenvector",
            "total_ied":   "IED Total (M)",
        })
        .round(3)
    )
    st.dataframe(top_countries, use_container_width=True, hide_index=True)

st.markdown(
    "<p class='method-note'>Hub Score: índice compuesto de centralidad estructural (volumen IED + betweenness + eigenvector) · "
    "Betweenness: proporción de caminos más cortos que pasan por el nodo · "
    "Eigenvector: centralidad ponderada por la importancia de los vecinos · "
    "Fuente: Secretaría de Economía · DGIE · Cálculo: NetworkX</p>",
    unsafe_allow_html=True,
)